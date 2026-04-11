"""TRUGS Memory Render — deterministic markdown render of a memory TRUG.

Reads a memory graph produced by `trugs-memory` and emits a single
integrated `MEMORY.md` file that an LLM agent can load at session start.

The renderer is:
  - Deterministic: same graph in → same bytes out.
  - Temporal-aware: filters nodes whose `valid_to` is in the past.
  - Grouped by `memory_type` with a stable default order.
  - Budget-aware: if the rendered output exceeds the token budget, the
    oldest `project` entries are demoted first, then `reference`.
    `user` and `feedback` entries are never demoted (they are the
    behavioral rules Claude needs every session).

Usage:
    python tools/memory_render.py <in.trug.json> <out.md> [--budget N] [--include-rationale]
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


# ─── Public API ────────────────────────────────────────────────────────────────

#: Default order for `memory_type` sections in the rendered output.
DEFAULT_TYPE_ORDER: Tuple[str, ...] = ("user", "feedback", "project", "reference")

#: Default render budget (approximate tokens). 1 token ≈ 4 characters is a
#: standard rule of thumb for English; we use that here as a conservative
#: bound. Callers can override with any integer.
DEFAULT_BUDGET_TOKENS: int = 8000

#: Order in which sections get demoted when over budget. `user` and
#: `feedback` are never demoted — they are behavioral load-bearing.
DEMOTION_ORDER: Tuple[str, ...] = ("project", "reference")


def render(
    graph: Dict[str, Any],
    *,
    token_budget: int = DEFAULT_BUDGET_TOKENS,
    include_rationale: bool = False,
    now: Optional[datetime] = None,
    type_order: Tuple[str, ...] = DEFAULT_TYPE_ORDER,
) -> str:
    """Render a memory graph to a single markdown string.

    Args:
        graph: a memory TRUG dict (as produced by `tools.memory.init_memory_graph`).
        token_budget: soft upper bound on rendered output, in approximate tokens
            (4 chars ≈ 1 token). Sections are demoted when over budget.
        include_rationale: if True, each memory's `rationale` property is
            emitted as a quoted sub-block. Default False (Claude only needs rules).
        now: reference timestamp for `valid_to` filtering. Defaults to UTC now.
        type_order: tuple of `memory_type` section names in the order they
            should appear. Unknown types are appended at the end, sorted.

    Returns:
        The rendered markdown, terminating with a single trailing newline.
    """
    if now is None:
        now = datetime.now(timezone.utc)

    active = _active_memories(graph, now=now)
    grouped = _group_by_type(active, type_order=type_order)

    header_lines = _render_header(graph, grouped, now=now)
    body = _render_body(grouped, include_rationale=include_rationale)

    # Budget enforcement — demote oldest entries in DEMOTION_ORDER types.
    final_body = _apply_budget(
        header_lines,
        body,
        grouped,
        token_budget=token_budget,
        include_rationale=include_rationale,
    )

    out = "\n".join(header_lines) + "\n\n" + final_body
    if not out.endswith("\n"):
        out += "\n"
    return out


def render_to_file(
    graph: Dict[str, Any],
    path: Path,
    **kwargs: Any,
) -> int:
    """Render `graph` to `path`. Returns the number of bytes written.

    Keyword arguments are forwarded to `render()`.
    """
    text = render(graph, **kwargs)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    return len(text.encode("utf-8"))


# ─── Internals ─────────────────────────────────────────────────────────────────


def _active_memories(
    graph: Dict[str, Any],
    *,
    now: datetime,
) -> List[Dict[str, Any]]:
    """Return memory nodes under `memory-root` whose `valid_to` is null or future."""
    memories: List[Dict[str, Any]] = []
    for n in graph.get("nodes", []):
        if n.get("id") == "memory-root":
            continue
        if n.get("parent_id") != "memory-root":
            continue
        props = n.get("properties", {})
        valid_to = props.get("valid_to")
        if valid_to and _is_past(valid_to, now=now):
            continue
        memories.append(n)
    return memories


def _is_past(iso_timestamp: str, *, now: datetime) -> bool:
    """Return True if the given ISO-8601 timestamp is strictly before `now`."""
    try:
        parsed = datetime.fromisoformat(iso_timestamp)
    except (TypeError, ValueError):
        return False
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed < now


def _group_by_type(
    memories: List[Dict[str, Any]],
    *,
    type_order: Tuple[str, ...],
) -> Dict[str, List[Dict[str, Any]]]:
    """Group memories by `properties.memory_type`, ordered by type_order.

    Within each group, memories are sorted by `properties.created` descending
    (newest first). Unknown memory_types are appended at the end in sorted
    order for determinism.
    """
    buckets: Dict[str, List[Dict[str, Any]]] = {}
    for m in memories:
        t = (m.get("properties", {}).get("memory_type") or "other").lower()
        buckets.setdefault(t, []).append(m)

    # Sort each bucket: newest first, stable on id for determinism.
    for t, lst in buckets.items():
        lst.sort(
            key=lambda m: (
                -_created_epoch(m),
                m.get("id", ""),
            )
        )

    # Rebuild in deterministic order: known types first in given order,
    # then unknown types sorted alphabetically.
    ordered: Dict[str, List[Dict[str, Any]]] = {}
    for t in type_order:
        if t in buckets:
            ordered[t] = buckets.pop(t)
    for t in sorted(buckets):
        ordered[t] = buckets[t]
    return ordered


def _created_epoch(memory: Dict[str, Any]) -> float:
    """Return `created` as a float epoch for sort ordering. Missing → 0."""
    created = memory.get("properties", {}).get("created", "")
    try:
        dt = datetime.fromisoformat(created)
    except (TypeError, ValueError):
        return 0.0
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.timestamp()


def _render_header(
    graph: Dict[str, Any],
    grouped: Dict[str, List[Dict[str, Any]]],
    *,
    now: datetime,
) -> List[str]:
    """Render the top-of-file metadata block as a list of lines."""
    total = sum(len(v) for v in grouped.values())
    counts = ", ".join(f"{t}={len(v)}" for t, v in grouped.items() if v)
    return [
        f"# MEMORY",
        "",
        f"> Rendered from `{graph.get('name', 'memory graph')}` "
        f"at {now.replace(microsecond=0).isoformat()}.",
        f"> {total} active memories — {counts if counts else '(none)'}.",
        f"> **Do not edit.** This file is produced by `trugs-memory render`.",
    ]


def _render_body(
    grouped: Dict[str, List[Dict[str, Any]]],
    *,
    include_rationale: bool,
) -> str:
    """Render grouped memories as markdown body (type sections + entries)."""
    chunks: List[str] = []
    for t, memories in grouped.items():
        if not memories:
            continue
        chunks.append(f"## {t}")
        chunks.append("")
        for m in memories:
            chunks.append(_render_memory(m, include_rationale=include_rationale))
            chunks.append("")
    if not chunks:
        return "_(no active memories)_\n"
    return "\n".join(chunks).rstrip() + "\n"


def _render_memory(
    memory: Dict[str, Any],
    *,
    include_rationale: bool,
) -> str:
    """Render a single memory as a markdown bullet + optional rationale block."""
    props = memory.get("properties", {})
    body = props.get("rule") or props.get("text") or ""
    body = body.strip()

    lines = [f"- {body}" if body else "- _(empty memory)_"]

    tags = props.get("tags") or []
    if tags:
        lines.append(f"  tags: {', '.join(tags)}")

    if include_rationale:
        rationale = (props.get("rationale") or "").strip()
        if rationale:
            for rl in rationale.splitlines():
                lines.append(f"  > {rl}")

    return "\n".join(lines)


def _approx_tokens(text: str) -> int:
    """Approximate token count. 1 token ≈ 4 chars (English rule of thumb)."""
    return max(1, (len(text) + 3) // 4)


def _apply_budget(
    header_lines: List[str],
    body: str,
    grouped: Dict[str, List[Dict[str, Any]]],
    *,
    token_budget: int,
    include_rationale: bool,
) -> str:
    """Demote oldest entries in DEMOTION_ORDER types until body fits budget.

    `user` and `feedback` are never demoted. Demoted entries are dropped from
    the output; they remain on disk in the source TRUG.
    """
    header = "\n".join(header_lines)

    def over_budget(b: str) -> bool:
        return _approx_tokens(header + "\n\n" + b) > token_budget

    if not over_budget(body):
        return body

    # Build a mutable working copy we can trim from.
    working: Dict[str, List[Dict[str, Any]]] = {
        t: list(lst) for t, lst in grouped.items()
    }

    demoted_count = 0
    for t in DEMOTION_ORDER:
        bucket = working.get(t)
        if not bucket:
            continue
        # Drop oldest entries first; bucket is newest-first, so pop from end.
        while bucket and over_budget(_render_body(working, include_rationale=include_rationale)):
            bucket.pop()
            demoted_count += 1
        if bucket:
            working[t] = bucket
        else:
            # Remove empty bucket entirely to avoid orphan section header.
            del working[t]

    new_body = _render_body(working, include_rationale=include_rationale)

    if demoted_count > 0:
        note = f"\n_{demoted_count} memories demoted for budget; still on disk in the graph._\n"
        new_body = new_body.rstrip() + "\n" + note
    return new_body


# ─── CLI ───────────────────────────────────────────────────────────────────────


def main() -> None:
    """CLI entry: `trugs-memory-render <in.trug.json> <out.md> [flags]`."""
    argv = sys.argv[1:]
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        sys.exit(0)

    if len(argv) < 2:
        print("Usage: memory_render.py <in.trug.json> <out.md> [--budget N] [--include-rationale]", file=sys.stderr)
        sys.exit(2)

    in_path = Path(argv[0])
    out_path = Path(argv[1])
    token_budget = DEFAULT_BUDGET_TOKENS
    include_rationale = False

    i = 2
    while i < len(argv):
        if argv[i] == "--budget" and i + 1 < len(argv):
            try:
                token_budget = int(argv[i + 1])
            except ValueError:
                print(f"Error: --budget requires an integer, got '{argv[i + 1]}'", file=sys.stderr)
                sys.exit(2)
            i += 2
        elif argv[i] == "--include-rationale":
            include_rationale = True
            i += 1
        else:
            print(f"Error: unknown argument '{argv[i]}'", file=sys.stderr)
            sys.exit(2)

    if not in_path.exists():
        print(f"Error: input file not found: {in_path}", file=sys.stderr)
        sys.exit(1)

    with open(in_path, "r", encoding="utf-8") as f:
        graph = json.load(f)

    bytes_written = render_to_file(
        graph,
        out_path,
        token_budget=token_budget,
        include_rationale=include_rationale,
    )
    print(f"Rendered {bytes_written} bytes to {out_path}")
    sys.exit(0)


if __name__ == "__main__":
    main()
