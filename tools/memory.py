"""TRUGS Memory — LLM-native persistent memory as a TRUG graph.

Memories are nodes. Associations are edges. The graph validates against CORE.

Usage:
    python tools/memory.py remember <file> "memory text" [--type TYPE] [--tags tag1,tag2]
    python tools/memory.py recall <file> [--query KEYWORD] [--type TYPE] [--recent N] [--all]
    python tools/memory.py forget <file> <memory_id>
    python tools/memory.py associate <file> <from_id> <to_id> [--relation RELATION]
    python tools/memory.py render <in.trug.json> <out.md> [--budget N] [--include-rationale]
    python tools/memory.py init <file>
"""

import json
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


# ─── Graph Operations ──────────────────────────────────────────────────────────

def load_graph(path: Path) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_graph(path: Path, graph: Dict[str, Any]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(graph, f, indent=2)
        f.write("\n")


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
) -> str:
    """Add a memory node to the graph. Returns the new memory ID."""
    memory_id = f"mem-{uuid.uuid4().hex[:8]}"
    now = datetime.now(timezone.utc).isoformat()

    node = {
        "id": memory_id,
        "type": "DATA",
        "properties": {
            "text": text,
            "memory_type": memory_type,
            "created": now,
            "tags": tags or [],
        },
        "parent_id": "memory-root",
        "contains": [],
        "metric_level": "BASE_MEMORY",
        "dimension": "memory",
    }

    if source:
        node["properties"]["source"] = source

    graph["nodes"].append(node)

    # Update root contains[]
    root = _find_node(graph, "memory-root")
    if root and memory_id not in root.get("contains", []):
        root["contains"].append(memory_id)

    return memory_id


# ─── Recall ────────────────────────────────────────────────────────────────────

def recall(
    graph: Dict[str, Any],
    query: Optional[str] = None,
    memory_type: Optional[str] = None,
    recent: Optional[int] = None,
    all_memories: bool = False,
) -> List[Dict[str, Any]]:
    """Query memories. Returns matching memory nodes."""
    memories = [
        n for n in graph.get("nodes", [])
        if n.get("id") != "memory-root" and n.get("parent_id") == "memory-root"
    ]

    if not all_memories:
        if query:
            q = query.lower()
            memories = [
                m for m in memories
                if q in m.get("properties", {}).get("text", "").lower()
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
    props = mem.get("properties", {})
    lines = [
        f"  [{mem['id']}] {props.get('memory_type', '?')}",
        f"    {props.get('text', '')}",
    ]
    if props.get("tags"):
        lines.append(f"    tags: {', '.join(props['tags'])}")
    if props.get("source"):
        lines.append(f"    source: {props['source']}")
    lines.append(f"    created: {props.get('created', '?')}")

    # Show associations
    related = [e for e in edges if e.get("from_id") == mem["id"] or e.get("to_id") == mem["id"]]
    if related:
        for e in related:
            other = e["to_id"] if e["from_id"] == mem["id"] else e["from_id"]
            direction = "→" if e["from_id"] == mem["id"] else "←"
            lines.append(f"    {direction} {e['relation']} {other}")

    return "\n".join(lines)


# ─── CLI ───────────────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    command = sys.argv[1]

    if command == "init":
        if len(sys.argv) < 3:
            print("Usage: memory.py init <file>")
            sys.exit(1)
        path = Path(sys.argv[2])
        if path.exists():
            print(f"Error: {path} already exists", file=sys.stderr)
            sys.exit(1)
        init_memory_graph(path)
        print(f"Created memory graph: {path}")
        sys.exit(0)

    if command == "remember":
        if len(sys.argv) < 4:
            print("Usage: memory.py remember <file> \"memory text\" [--type TYPE] [--tags t1,t2] [--source SRC]")
            sys.exit(1)
        path = Path(sys.argv[2])
        text = sys.argv[3]
        mem_type = "FACT"
        tags = []
        source = None
        i = 4
        while i < len(sys.argv):
            if sys.argv[i] == "--type" and i + 1 < len(sys.argv):
                mem_type = sys.argv[i + 1]
                i += 2
            elif sys.argv[i] == "--tags" and i + 1 < len(sys.argv):
                tags = [t.strip() for t in sys.argv[i + 1].split(",")]
                i += 2
            elif sys.argv[i] == "--source" and i + 1 < len(sys.argv):
                source = sys.argv[i + 1]
                i += 2
            else:
                i += 1

        graph = load_graph(path)
        mid = remember(graph, text, mem_type, tags, source)
        save_graph(path, graph)
        print(f"Remembered: {mid}")
        sys.exit(0)

    if command == "recall":
        if len(sys.argv) < 3:
            print("Usage: memory.py recall <file> [--query KW] [--type TYPE] [--recent N] [--all]")
            sys.exit(1)
        path = Path(sys.argv[2])
        query = None
        mem_type = None
        recent = None
        all_mem = False
        i = 3
        while i < len(sys.argv):
            if sys.argv[i] == "--query" and i + 1 < len(sys.argv):
                query = sys.argv[i + 1]
                i += 2
            elif sys.argv[i] == "--type" and i + 1 < len(sys.argv):
                mem_type = sys.argv[i + 1]
                i += 2
            elif sys.argv[i] == "--recent" and i + 1 < len(sys.argv):
                recent = int(sys.argv[i + 1])
                i += 2
            elif sys.argv[i] == "--all":
                all_mem = True
                i += 1
            else:
                i += 1

        graph = load_graph(path)
        results = recall(graph, query, mem_type, recent, all_mem)
        edges = graph.get("edges", [])

        if not results:
            print("No memories found.")
        else:
            print(f"{len(results)} memories:")
            for m in results:
                print(_format_memory(m, edges))
        sys.exit(0)

    if command == "forget":
        if len(sys.argv) < 4:
            print("Usage: memory.py forget <file> <memory_id>")
            sys.exit(1)
        path = Path(sys.argv[2])
        memory_id = sys.argv[3]
        graph = load_graph(path)
        if forget(graph, memory_id):
            save_graph(path, graph)
            print(f"Forgot: {memory_id}")
        else:
            print(f"Error: memory '{memory_id}' not found", file=sys.stderr)
            sys.exit(1)
        sys.exit(0)

    if command == "render":
        # Delegate to memory_render.main() — pass the remaining argv through.
        try:
            from memory_render import main as render_main  # test/dev cwd=tools/
        except ImportError:
            from tools.memory_render import main as render_main  # installed package
        sys.argv = [sys.argv[0]] + sys.argv[2:]
        render_main()
        return

    if command == "associate":
        if len(sys.argv) < 5:
            print("Usage: memory.py associate <file> <from_id> <to_id> [--relation REL]")
            sys.exit(1)
        path = Path(sys.argv[2])
        from_id = sys.argv[3]
        to_id = sys.argv[4]
        relation = "REFERENCES"
        if len(sys.argv) > 5 and sys.argv[5] == "--relation" and len(sys.argv) > 6:
            relation = sys.argv[6]

        graph = load_graph(path)
        if associate(graph, from_id, to_id, relation):
            save_graph(path, graph)
            print(f"Associated: {from_id} --[{relation}]--> {to_id}")
        else:
            print("Error: one or both nodes not found", file=sys.stderr)
            sys.exit(1)
        sys.exit(0)

    print(f"Unknown command: {command}")
    print(__doc__)
    sys.exit(1)


if __name__ == "__main__":
    main()
