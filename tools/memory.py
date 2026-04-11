"""TRUGS Memory — LLM-native persistent memory as a TRUG graph.

Memories are nodes. Associations are edges. The graph validates against CORE.

Usage:
    trugs-memory init <file>
    trugs-memory remember <file> "memory text" [flags]
    trugs-memory recall <file> [flags]
    trugs-memory forget <file> <memory_id>
    trugs-memory associate <file> <from_id> <to_id> [--relation RELATION]
    trugs-memory render <in.trug.json> <out.md> [flags]

Run `trugs-memory <command> --help` for per-command help.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


# ─── Graph Operations ──────────────────────────────────────────────────────────

def load_graph(path: Path) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_graph(path: Path, graph: Dict[str, Any]) -> None:
    """Atomically write `graph` to `path`.

    Writes to a sibling temp file, fsyncs, then `os.replace`s. On most
    POSIX filesystems this is atomic — the target file either contains
    the old content or the new content, never a truncated mix. Protects
    against Ctrl-C / kill -9 / power loss mid-write, which the naive
    truncate-then-stream pattern does NOT.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    # tempfile in the same directory so os.replace is atomic on the same FS.
    fd, tmp_path = tempfile.mkstemp(
        prefix=f".{path.name}.",
        suffix=".tmp",
        dir=str(path.parent),
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(graph, f, indent=2)
            f.write("\n")
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_path, path)
    except BaseException:
        # On any failure, clean up the temp file so we don't leave junk.
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise


def init_memory_graph(path: Path) -> Dict[str, Any]:
    """Create a new empty memory TRUG."""
    graph = {
        "name": "LLM Memory",
        "version": "1.0.0",
        "type": "MEMORY",
        "description": "Persistent memory graph for LLM sessions. Memories are nodes, associations are edges.",
        "dimensions": {
            "memory": {
                "description": "Memory hierarchy: store > topic > memory",
                "base_level": "BASE"
            }
        },
        "capabilities": {
            "extensions": [],
            "vocabularies": ["core_v1.0.0"],
            "profiles": []
        },
        "nodes": [
            {
                "id": "memory-root",
                "type": "MODULE",
                "properties": {
                    "name": "Memory Store",
                    "created": datetime.now(timezone.utc).isoformat()
                },
                "parent_id": None,
                "contains": [],
                "metric_level": "KILO_STORE",
                "dimension": "memory"
            }
        ],
        "edges": []
    }
    save_graph(path, graph)
    return graph


# ─── Remember ──────────────────────────────────────────────────────────────────

def remember(
    graph: Dict[str, Any],
    text: str,
    memory_type: str = "FACT",
    tags: Optional[List[str]] = None,
    source: Optional[str] = None,
    *,
    rule: Optional[str] = None,
    rationale: Optional[str] = None,
    valid_to: Optional[str] = None,
    session_id: Optional[str] = None,
    supersede: Optional[str] = None,
) -> str:
    """Add a memory node to the graph. Returns the new memory ID.

    Args:
        graph: the memory TRUG (mutated in place).
        text: full-prose memory content. Always stored.
        memory_type: canonical type. Common values: `user`, `feedback`,
            `project`, `reference`. Unknown values are accepted.
        tags: list of free-form tags for retrieval.
        source: optional URL or path citation.

    Keyword-only args (added in trugs 1.1.0):
        rule: terse executable form of the memory. If set, renderers
            prefer this over `text`. Keep under ~140 chars.
        rationale: explanatory prose — the "why" behind a rule. Not
            rendered to MEMORY.md by default (agents don't need it in
            their session context).
        valid_to: ISO-8601 timestamp at which this memory stops being
            active. Renderers filter out expired memories. `None` means
            still active.
        session_id: identifier of the session that wrote this memory.
            Enables session-scoped recall and temporal reasoning.
        supersede: id of an older memory that this one replaces. When
            set, the old memory gets `valid_to = now()` and
            `superseded_by = <new id>`, AND a `SUPERSEDES` edge is
            added from the new memory to the old one. This is the
            Graphiti-style bi-temporal pattern: nothing is deleted,
            stale facts are closed.
    """
    memory_id = f"mem-{uuid.uuid4().hex[:8]}"
    now = datetime.now(timezone.utc).isoformat()

    # Validate supersede BEFORE mutating the graph, so a raise leaves the
    # store clean. If the chain has a cycle or the old node is missing we
    # fail fast without creating an orphan new memory.
    supersede_tail: Optional[Dict[str, Any]] = None
    if supersede is not None:
        if supersede == memory_id:  # defensive; new_id is freshly generated
            raise SupersedeError(f"cannot supersede a memory with itself: {supersede}")
        old = _find_node(graph, supersede)
        if old is not None:
            supersede_tail = _resolve_supersede_tail(graph, supersede)
            if supersede_tail is None:
                raise SupersedeError(
                    f"supersede chain starting at {supersede} contains a cycle"
                )
            if supersede_tail["id"] == memory_id:
                # Impossible in practice (new_id is fresh) but cheap to assert.
                raise SupersedeError(
                    f"supersede chain starting at {supersede} already terminates at {memory_id}"
                )

    props: Dict[str, Any] = {
        "text": text,
        "memory_type": memory_type,
        "created": now,
        "tags": tags or [],
    }
    if source is not None:
        props["source"] = source
    if rule is not None:
        props["rule"] = rule
    if rationale is not None:
        props["rationale"] = rationale
    if valid_to is not None:
        props["valid_to"] = valid_to
    if session_id is not None:
        props["session_id"] = session_id

    node = {
        "id": memory_id,
        "type": "DATA",
        "properties": props,
        "parent_id": "memory-root",
        "contains": [],
        "metric_level": "BASE_MEMORY",
        "dimension": "memory",
    }

    graph["nodes"].append(node)

    # Update root contains[]
    root = _find_node(graph, "memory-root")
    if root and memory_id not in root.get("contains", []):
        root["contains"].append(memory_id)

    # Handle supersession — close the TAIL of the chain (not necessarily the
    # node the caller named) and link the new memory. Validation already ran.
    if supersede is not None and supersede_tail is not None:
        tail_props = supersede_tail.setdefault("properties", {})
        if "valid_to" not in tail_props or tail_props["valid_to"] is None:
            tail_props["valid_to"] = now
        tail_props["superseded_by"] = memory_id
        associate(graph, memory_id, supersede_tail["id"], relation="SUPERSEDES")

    return memory_id


class SupersedeError(ValueError):
    """Raised when a supersede call violates the bi-temporal invariant."""


def _resolve_supersede_tail(graph: Dict[str, Any], start_id: str) -> Optional[Dict[str, Any]]:
    """Walk `superseded_by` links from `start_id` until we hit a node that
    is not yet superseded, a cycle, or a missing link.

    Returns the tail node (the one currently active in the chain), or None
    if the start doesn't exist. Cycles return None rather than looping.
    """
    visited = set()
    current = _find_node(graph, start_id)
    while current is not None:
        cid = current.get("id")
        if cid in visited:
            return None  # cycle guard
        visited.add(cid)
        props = current.get("properties", {})
        successor_id = props.get("superseded_by")
        if not successor_id:
            return current
        successor = _find_node(graph, successor_id)
        if successor is None:
            return current  # dangling successor pointer — treat as tail
        current = successor
    return None


def _apply_supersede(
    graph: Dict[str, Any],
    *,
    new_id: str,
    old_id: str,
    now: str,
) -> bool:
    """Close an old memory and link the new one. Returns True on success.

    Sets `valid_to=now` (if not already set) and `superseded_by=new_id`
    on the old node, and adds a `SUPERSEDES` edge from `new_id` → `old_id`.

    Raises `SupersedeError` when:
      - `new_id == old_id` (self-supersede)
      - the chain from `old_id` already terminates at `new_id` (cycle)

    When `old_id` is ALREADY superseded by some other node (chain exists),
    the new memory is linked to the TAIL of the chain — i.e. supersede
    `old_id` behaves as supersede the currently-active-replacement of
    `old_id`. This preserves chain-of-custody instead of silently
    orphaning middle nodes.

    Returns False if the old node doesn't exist (no raise, for CLI
    convenience).
    """
    if new_id == old_id:
        raise SupersedeError(f"cannot supersede a memory with itself: {old_id}")

    old = _find_node(graph, old_id)
    if old is None:
        return False

    # Walk the chain to the current tail. If the chain is already terminal
    # (old_id has no superseded_by), tail == old, and we close old directly.
    # If a chain exists, we close the TAIL instead, preserving the chain.
    tail = _resolve_supersede_tail(graph, old_id)
    if tail is None:
        # Cycle in the existing chain — refuse rather than make it worse.
        raise SupersedeError(f"supersede chain starting at {old_id} contains a cycle")

    tail_id = tail["id"]
    if tail_id == new_id:
        raise SupersedeError(
            f"supersede chain starting at {old_id} already terminates at {new_id}"
        )

    props = tail.setdefault("properties", {})
    # Don't overwrite an explicitly-set valid_to.
    if "valid_to" not in props or props["valid_to"] is None:
        props["valid_to"] = now
    props["superseded_by"] = new_id

    # Add the SUPERSEDES edge from new → TAIL (the node actually being closed).
    associate(graph, new_id, tail_id, relation="SUPERSEDES")
    return True


# ─── Recall ────────────────────────────────────────────────────────────────────

def recall(
    graph: Dict[str, Any],
    query: Optional[str] = None,
    memory_type: Optional[str] = None,
    recent: Optional[int] = None,
    all_memories: bool = False,
    *,
    active_only: bool = False,
    now: Optional[datetime] = None,
) -> List[Dict[str, Any]]:
    """Query memories. Returns matching memory nodes.

    Args:
        graph: the memory TRUG.
        query: case-insensitive substring match against text, tags, or type.
        memory_type: exact match on `memory_type` (case-insensitive).
        recent: limit to N most recent results.
        all_memories: if True, skip the query/type filters but still respect
            `active_only` and `recent`.

    Keyword-only args (added in trugs 1.1.0):
        active_only: if True, exclude memories whose `valid_to` is in the past.
        now: reference timestamp for `active_only` filtering. Defaults to UTC now.
    """
    memories = [
        n for n in graph.get("nodes", [])
        if n.get("id") != "memory-root" and n.get("parent_id") == "memory-root"
    ]

    if active_only:
        ref = now or datetime.now(timezone.utc)
        memories = [m for m in memories if not _is_expired(m, ref)]

    if not all_memories:
        if query:
            q = query.lower()
            memories = [
                m for m in memories
                if q in m.get("properties", {}).get("text", "").lower()
                or q in m.get("properties", {}).get("rule", "").lower()
                or q in str(m.get("properties", {}).get("tags", [])).lower()
                or q in m.get("properties", {}).get("memory_type", "").lower()
            ]

        if memory_type:
            memories = [
                m for m in memories
                if m.get("properties", {}).get("memory_type", "").upper() == memory_type.upper()
            ]

    # Sort by created date, newest first
    memories.sort(
        key=lambda m: m.get("properties", {}).get("created", ""),
        reverse=True
    )

    if recent:
        memories = memories[:recent]

    return memories


def _parse_iso_utc(value: Any) -> Optional[datetime]:
    """Parse an ISO-8601 timestamp with fail-open semantics.

    - None, empty string, or non-string → None
    - Malformed string → None
    - Naive (tz-less) timestamps → assumed UTC

    Shared between `_is_expired` here and `_is_past` in memory_render.py
    to prevent the two from drifting.
    """
    if not value or not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value)
    except (TypeError, ValueError):
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


def _is_expired(memory: Dict[str, Any], now: datetime) -> bool:
    """Return True if the memory's `valid_to` is strictly before `now`."""
    parsed = _parse_iso_utc(memory.get("properties", {}).get("valid_to"))
    if parsed is None:
        return False  # Fail-open: malformed timestamps are treated as active.
    return parsed < now


# ─── Forget ────────────────────────────────────────────────────────────────────

def forget(graph: Dict[str, Any], memory_id: str) -> bool:
    """Remove a memory node and all its edges. Returns True if found."""
    node = _find_node(graph, memory_id)
    if not node:
        return False

    # Remove from parent's contains[]
    parent_id = node.get("parent_id")
    if parent_id:
        parent = _find_node(graph, parent_id)
        if parent:
            contains = parent.get("contains", [])
            if memory_id in contains:
                contains.remove(memory_id)

    # Remove all connected edges
    graph["edges"] = [
        e for e in graph.get("edges", [])
        if e.get("from_id") != memory_id and e.get("to_id") != memory_id
    ]

    # Remove the node
    graph["nodes"] = [n for n in graph["nodes"] if n.get("id") != memory_id]

    return True


# ─── Associate ─────────────────────────────────────────────────────────────────

def associate(
    graph: Dict[str, Any],
    from_id: str,
    to_id: str,
    relation: str = "REFERENCES",
) -> bool:
    """Create an edge between two memories. Returns True if both nodes exist."""
    if not _find_node(graph, from_id) or not _find_node(graph, to_id):
        return False

    # Check for duplicate
    for e in graph.get("edges", []):
        if e.get("from_id") == from_id and e.get("to_id") == to_id and e.get("relation") == relation:
            return True  # Already exists

    graph["edges"].append({
        "from_id": from_id,
        "to_id": to_id,
        "relation": relation,
    })
    return True


# ─── Helpers ───────────────────────────────────────────────────────────────────

def _find_node(graph: Dict[str, Any], node_id: str) -> Optional[Dict[str, Any]]:
    for n in graph.get("nodes", []):
        if n.get("id") == node_id:
            return n
    return None


def _format_memory(mem: Dict[str, Any], edges: List[Dict[str, Any]]) -> str:
    """Format a memory for CLI display. Prefers `rule` over `text` if present."""
    props = mem.get("properties", {})
    body = props.get("rule") or props.get("text") or ""
    lines = [
        f"  [{mem['id']}] {props.get('memory_type', '?')}",
        f"    {body}",
    ]
    if props.get("tags"):
        lines.append(f"    tags: {', '.join(props['tags'])}")
    if props.get("source"):
        lines.append(f"    source: {props['source']}")
    lines.append(f"    created: {props.get('created', '?')}")
    if props.get("valid_to"):
        lines.append(f"    valid_to: {props['valid_to']}")
    if props.get("superseded_by"):
        lines.append(f"    superseded_by: {props['superseded_by']}")

    # Show associations
    related = [e for e in edges if e.get("from_id") == mem["id"] or e.get("to_id") == mem["id"]]
    if related:
        for e in related:
            other = e["to_id"] if e["from_id"] == mem["id"] else e["from_id"]
            direction = "→" if e["from_id"] == mem["id"] else "←"
            lines.append(f"    {direction} {e['relation']} {other}")

    return "\n".join(lines)


# ─── CLI (argparse) ────────────────────────────────────────────────────────────

def _build_parser() -> argparse.ArgumentParser:
    """Construct the argparse parser with all subcommands."""
    parser = argparse.ArgumentParser(
        prog="trugs-memory",
        description=(
            "TRUGS Memory — LLM-native persistent memory as a TRUG graph. "
            "Memories are nodes, associations are edges, the graph validates against CORE."
        ),
    )
    sub = parser.add_subparsers(dest="command", metavar="command")
    sub.required = False  # Printed in main() if missing, so we can show the helpful message.

    # init
    p_init = sub.add_parser("init", help="Create an empty memory graph.")
    p_init.add_argument("file", help="Path to the new memory graph file.")

    # remember
    p_rem = sub.add_parser(
        "remember",
        help="Add a memory to the graph.",
        epilog=(
            "If the memory text begins with `-`, pass `--` first: "
            "`trugs-memory remember mem.json -- '--foo is a rule'`."
        ),
    )
    p_rem.add_argument("file", help="Path to an existing memory graph.")
    p_rem.add_argument("text", help="The memory content as prose.")
    p_rem.add_argument("--type", dest="memory_type", default="FACT",
                       help="Memory type (e.g. user, feedback, project, reference). Default: FACT")
    p_rem.add_argument("--tag", dest="tag_list", action="append", default=[],
                       help="Tag to attach to this memory. May be given multiple times. "
                            "Tags can contain commas when set via --tag (preferred).")
    p_rem.add_argument("--tags", default="",
                       help="Comma-separated tags (legacy form; use --tag for commas inside a tag).")
    p_rem.add_argument("--source", default=None, help="Optional source URL or citation.")
    p_rem.add_argument("--rule", default=None,
                       help="Terse executable form of the memory. Renderers prefer this over `text`.")
    p_rem.add_argument("--rationale", default=None,
                       help="Explanatory prose. Not rendered to MEMORY.md by default.")
    p_rem.add_argument("--valid-to", default=None,
                       help="ISO-8601 timestamp when this memory stops being active. "
                            "Must parse via datetime.fromisoformat — garbage is rejected.")
    p_rem.add_argument("--session-id", default=None,
                       help="Identifier of the session that wrote this memory.")
    p_rem.add_argument("--supersede", default=None,
                       help="ID of an older memory this one replaces. Closes the old memory "
                            "(valid_to=now, superseded_by=<new>) and adds a SUPERSEDES edge. "
                            "If the old memory is already superseded, the new memory is linked "
                            "to the tail of the existing chain, not the original.")

    # recall
    p_rec = sub.add_parser("recall", help="Query memories.")
    p_rec.add_argument("file", help="Path to the memory graph.")
    p_rec.add_argument("--query", default=None,
                       help="Case-insensitive substring match across text, rule, tags, type.")
    p_rec.add_argument("--type", dest="memory_type", default=None,
                       help="Filter by memory type (exact match, case-insensitive).")
    p_rec.add_argument("--recent", type=int, default=None,
                       help="Limit to N most recent results.")
    p_rec.add_argument("--all", dest="all_memories", action="store_true",
                       help="Skip query/type filters; still respects --active-only and --recent.")
    p_rec.add_argument("--active-only", action="store_true",
                       help="Exclude memories whose valid_to is in the past.")

    # forget
    p_for = sub.add_parser("forget", help="Remove a memory and all its edges.")
    p_for.add_argument("file", help="Path to the memory graph.")
    p_for.add_argument("memory_id", help="ID of the memory to remove.")

    # associate
    p_asc = sub.add_parser("associate", help="Create an edge between two memories.")
    p_asc.add_argument("file", help="Path to the memory graph.")
    p_asc.add_argument("from_id", help="Source memory ID.")
    p_asc.add_argument("to_id", help="Target memory ID.")
    p_asc.add_argument("--relation", default="REFERENCES",
                       help="TRL preposition (e.g. REFERENCES, SUPERSEDES, GOVERNS, "
                            "DEPENDS_ON, CONTAINS). Default: REFERENCES")

    # render (delegates to memory_render)
    p_ren = sub.add_parser("render", help="Render the memory graph to a markdown file.")
    p_ren.add_argument("in_file", metavar="in.trug.json", help="Path to the memory graph.")
    p_ren.add_argument("out_file", metavar="out.md", help="Path to the rendered markdown output.")
    p_ren.add_argument("--budget", type=int, default=8000,
                       help="Soft token budget for the rendered output. Default: 8000")
    p_ren.add_argument("--include-rationale", action="store_true",
                       help="Include rationale text in the rendered output.")

    return parser


def _cmd_init(args: argparse.Namespace) -> int:
    path = Path(args.file)
    if path.exists():
        print(f"Error: {path} already exists", file=sys.stderr)
        return 1
    init_memory_graph(path)
    print(f"Created memory graph: {path}")
    return 0


def _cmd_remember(args: argparse.Namespace) -> int:
    path = Path(args.file)

    # Merge --tag (repeatable) and --tags (legacy comma form).
    tags: List[str] = list(getattr(args, "tag_list", []))
    if args.tags:
        tags.extend(t.strip() for t in args.tags.split(",") if t.strip())

    # Validate --valid-to as ISO-8601 before writing. Fail-loud at the CLI
    # boundary so a fat-finger doesn't silently store a garbage timestamp
    # that fail-open filtering will later treat as active.
    if args.valid_to is not None:
        if _parse_iso_utc(args.valid_to) is None:
            print(
                f"Error: --valid-to must be ISO-8601 (got {args.valid_to!r}). "
                f"Example: 2026-12-31T00:00:00+00:00",
                file=sys.stderr,
            )
            return 2

    graph = load_graph(path)
    try:
        mid = remember(
            graph,
            args.text,
            memory_type=args.memory_type,
            tags=tags,
            source=args.source,
            rule=args.rule,
            rationale=args.rationale,
            valid_to=args.valid_to,
            session_id=args.session_id,
            supersede=args.supersede,
        )
    except SupersedeError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2

    save_graph(path, graph)
    print(f"Remembered: {mid}")
    if args.supersede:
        print(f"Superseded: {args.supersede}")
    return 0


def _cmd_recall(args: argparse.Namespace) -> int:
    path = Path(args.file)
    graph = load_graph(path)
    results = recall(
        graph,
        query=args.query,
        memory_type=args.memory_type,
        recent=args.recent,
        all_memories=args.all_memories,
        active_only=args.active_only,
    )
    edges = graph.get("edges", [])
    if not results:
        print("No memories found.")
    else:
        print(f"{len(results)} memories:")
        for m in results:
            print(_format_memory(m, edges))
    return 0


def _cmd_forget(args: argparse.Namespace) -> int:
    path = Path(args.file)
    graph = load_graph(path)
    if forget(graph, args.memory_id):
        save_graph(path, graph)
        print(f"Forgot: {args.memory_id}")
        return 0
    print(f"Error: memory '{args.memory_id}' not found", file=sys.stderr)
    return 1


def _cmd_associate(args: argparse.Namespace) -> int:
    path = Path(args.file)
    graph = load_graph(path)
    if associate(graph, args.from_id, args.to_id, args.relation):
        save_graph(path, graph)
        print(f"Associated: {args.from_id} --[{args.relation}]--> {args.to_id}")
        return 0
    print("Error: one or both nodes not found", file=sys.stderr)
    return 1


def _cmd_render(args: argparse.Namespace) -> int:
    try:
        from memory_render import render_to_file  # test/dev cwd=tools/
    except ImportError:
        from tools.memory_render import render_to_file  # installed package
    with open(args.in_file, "r", encoding="utf-8") as f:
        graph = json.load(f)
    n = render_to_file(
        graph,
        Path(args.out_file),
        token_budget=args.budget,
        include_rationale=args.include_rationale,
    )
    print(f"Rendered {n} bytes to {args.out_file}")
    return 0


_COMMANDS = {
    "init": _cmd_init,
    "remember": _cmd_remember,
    "recall": _cmd_recall,
    "forget": _cmd_forget,
    "associate": _cmd_associate,
    "render": _cmd_render,
}


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)
    handler = _COMMANDS.get(args.command)
    if handler is None:
        parser.error(f"Unknown command: {args.command}")
    sys.exit(handler(args))


if __name__ == "__main__":
    main()
