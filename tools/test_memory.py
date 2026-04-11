"""Tests for tools/memory.py — extended properties + argparse CLI (U2)."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from memory import (
    _apply_supersede,
    _build_parser,
    _find_node,
    _format_memory,
    _is_expired,
    associate,
    forget,
    init_memory_graph,
    load_graph,
    recall,
    remember,
    save_graph,
)
from validate import validate


# ─── Fixtures ──────────────────────────────────────────────────────────────────


@pytest.fixture
def empty_graph():
    with tempfile.TemporaryDirectory() as d:
        path = Path(d) / "memory.trug.json"
        yield init_memory_graph(path)


@pytest.fixture
def graph_path():
    with tempfile.TemporaryDirectory() as d:
        path = Path(d) / "memory.trug.json"
        init_memory_graph(path)
        yield path


# ─── Backwards compatibility ───────────────────────────────────────────────────


def test_remember_without_new_kwargs_produces_1_0_0_shape(empty_graph):
    g = deepcopy(empty_graph)
    mid = remember(g, "Legacy memory", memory_type="feedback", tags=["a", "b"])
    node = _find_node(g, mid)
    assert node is not None
    props = node["properties"]
    assert props["text"] == "Legacy memory"
    assert props["memory_type"] == "feedback"
    assert props["tags"] == ["a", "b"]
    # None of the new optional keys should be present by default.
    for k in ("rule", "rationale", "valid_to", "superseded_by", "session_id"):
        assert k not in props, f"Unexpected key {k!r} in 1.0.0-compat write"


def test_graph_written_by_new_remember_still_validates(empty_graph):
    g = deepcopy(empty_graph)
    remember(
        g,
        "Test memory",
        memory_type="feedback",
        rule="Do the thing.",
        rationale="Because we said so.",
        valid_to="2027-01-01T00:00:00+00:00",
        session_id="2026-04-10",
    )
    result = validate(g)
    assert result.valid, f"Validation failed: {[e.message for e in result.errors]}"


def test_load_graph_written_by_1_0_0_then_remember_with_new_props(tmp_path):
    """Round-trip: a graph the old format wrote can accept new-format writes."""
    path = tmp_path / "legacy.trug.json"
    # Simulate what trugs==1.0.0 would produce: no new keys anywhere.
    legacy = {
        "name": "LLM Memory",
        "version": "1.0.0",
        "type": "MEMORY",
        "description": "Legacy",
        "dimensions": {"memory": {"description": "m", "base_level": "BASE"}},
        "capabilities": {"extensions": [], "vocabularies": ["core_v1.0.0"], "profiles": []},
        "nodes": [
            {
                "id": "memory-root",
                "type": "MODULE",
                "properties": {"name": "Memory Store", "created": "2026-04-01T00:00:00+00:00"},
                "parent_id": None,
                "contains": ["mem-legacy1"],
                "metric_level": "KILO_STORE",
                "dimension": "memory",
            },
            {
                "id": "mem-legacy1",
                "type": "DATA",
                "properties": {
                    "text": "Legacy rule from 1.0.0",
                    "memory_type": "feedback",
                    "created": "2026-04-01T00:00:00+00:00",
                    "tags": ["legacy"],
                },
                "parent_id": "memory-root",
                "contains": [],
                "metric_level": "BASE_MEMORY",
                "dimension": "memory",
            },
        ],
        "edges": [],
    }
    save_graph(path, legacy)

    g = load_graph(path)
    # Existing validate passes.
    assert validate(g).valid
    # Add a new-format memory alongside the legacy one.
    new_id = remember(g, "New-format memory", memory_type="feedback", rule="Do X.", session_id="now")
    save_graph(path, g)

    # Re-load and check both coexist.
    g2 = load_graph(path)
    assert validate(g2).valid
    legacy_node = _find_node(g2, "mem-legacy1")
    new_node = _find_node(g2, new_id)
    assert legacy_node is not None
    assert new_node is not None
    assert "rule" not in legacy_node["properties"]
    assert new_node["properties"]["rule"] == "Do X."


# ─── Extended properties ──────────────────────────────────────────────────────


def test_remember_with_rule_sets_rule_property(empty_graph):
    g = deepcopy(empty_graph)
    mid = remember(g, "Long prose", rule="Short rule")
    node = _find_node(g, mid)
    assert node["properties"]["rule"] == "Short rule"
    assert node["properties"]["text"] == "Long prose"


def test_remember_with_all_new_props(empty_graph):
    g = deepcopy(empty_graph)
    mid = remember(
        g,
        "Full memory",
        memory_type="feedback",
        rule="Rule",
        rationale="Why",
        valid_to="2028-01-01T00:00:00+00:00",
        session_id="sess-1",
    )
    props = _find_node(g, mid)["properties"]
    assert props["rule"] == "Rule"
    assert props["rationale"] == "Why"
    assert props["valid_to"] == "2028-01-01T00:00:00+00:00"
    assert props["session_id"] == "sess-1"


def test_remember_optional_kwargs_none_means_not_set(empty_graph):
    g = deepcopy(empty_graph)
    mid = remember(g, "Memory", rule=None, rationale=None, valid_to=None, session_id=None)
    props = _find_node(g, mid)["properties"]
    assert "rule" not in props
    assert "rationale" not in props
    assert "valid_to" not in props
    assert "session_id" not in props


# ─── Supersede workflow ───────────────────────────────────────────────────────


def test_supersede_closes_old_and_links_new(empty_graph):
    g = deepcopy(empty_graph)
    old_id = remember(g, "Old rule", memory_type="feedback", rule="Do X.")
    new_id = remember(g, "New rule", memory_type="feedback", rule="Do X then Y.", supersede=old_id)

    old_node = _find_node(g, old_id)
    new_node = _find_node(g, new_id)

    # Old memory is now marked expired and points forward to the new one.
    assert old_node["properties"]["valid_to"] is not None
    assert old_node["properties"]["superseded_by"] == new_id

    # New memory is clean — no back-reference from its own properties.
    assert "superseded_by" not in new_node["properties"]
    assert "valid_to" not in new_node["properties"]

    # SUPERSEDES edge exists from new to old.
    edges = [
        e for e in g["edges"]
        if e["from_id"] == new_id and e["to_id"] == old_id and e["relation"] == "SUPERSEDES"
    ]
    assert len(edges) == 1


def test_supersede_unknown_id_returns_false():
    g = {"nodes": [{"id": "memory-root", "type": "MODULE", "properties": {}, "parent_id": None,
                    "contains": [], "metric_level": "KILO_STORE", "dimension": "memory"}],
         "edges": []}
    remember(g, "New")  # creates mem-xxxx, but no "nonexistent" to link to.
    result = _apply_supersede(g, new_id="mem-new", old_id="nonexistent", now="2026-04-10T00:00:00+00:00")
    assert result is False


def test_supersede_preserves_explicit_valid_to(empty_graph):
    g = deepcopy(empty_graph)
    old_id = remember(g, "Old", valid_to="2025-12-31T00:00:00+00:00")
    _ = remember(g, "New", supersede=old_id)
    old_node = _find_node(g, old_id)
    # Explicit valid_to should NOT be overwritten by supersede's `now`.
    assert old_node["properties"]["valid_to"] == "2025-12-31T00:00:00+00:00"


def test_superseded_memory_excluded_by_active_only_recall(empty_graph):
    g = deepcopy(empty_graph)
    old_id = remember(g, "Old rule")
    new_id = remember(g, "New rule", supersede=old_id)

    all_results = recall(g, all_memories=True)
    assert len(all_results) == 2

    active = recall(g, all_memories=True, active_only=True)
    active_ids = {m["id"] for m in active}
    assert new_id in active_ids
    assert old_id not in active_ids


# ─── active-only recall ───────────────────────────────────────────────────────


def test_recall_active_only_filters_expired(empty_graph):
    g = deepcopy(empty_graph)
    remember(g, "Still valid", memory_type="feedback")
    remember(g, "Expired", memory_type="feedback", valid_to="2024-01-01T00:00:00+00:00")

    fixed = datetime(2026, 4, 10, tzinfo=timezone.utc)
    results = recall(g, all_memories=True, active_only=True, now=fixed)
    texts = {m["properties"]["text"] for m in results}
    assert "Still valid" in texts
    assert "Expired" not in texts


def test_recall_active_only_keeps_future_valid_to(empty_graph):
    g = deepcopy(empty_graph)
    remember(g, "Scheduled retire", valid_to="2027-01-01T00:00:00+00:00")
    fixed = datetime(2026, 4, 10, tzinfo=timezone.utc)
    results = recall(g, all_memories=True, active_only=True, now=fixed)
    assert len(results) == 1


def test_recall_without_active_only_returns_everything(empty_graph):
    g = deepcopy(empty_graph)
    remember(g, "Active")
    remember(g, "Expired", valid_to="2024-01-01T00:00:00+00:00")
    results = recall(g, all_memories=True)
    assert len(results) == 2


def test_recall_query_matches_rule_field(empty_graph):
    g = deepcopy(empty_graph)
    remember(g, "Some long prose about auditing", rule="Always fix findings")
    results = recall(g, query="fix findings")
    assert len(results) == 1


def test_is_expired_handles_malformed_date(empty_graph):
    g = deepcopy(empty_graph)
    remember(g, "Garbage date", valid_to="not-a-date")
    node = _find_node(g, g["nodes"][-1]["id"])
    assert _is_expired(node, datetime.now(timezone.utc)) is False


# ─── _format_memory ───────────────────────────────────────────────────────────


def test_format_memory_prefers_rule_over_text(empty_graph):
    g = deepcopy(empty_graph)
    mid = remember(g, "Verbose prose", rule="Do thing.")
    node = _find_node(g, mid)
    formatted = _format_memory(node, g["edges"])
    assert "Do thing." in formatted
    assert "Verbose prose" not in formatted


def test_format_memory_shows_valid_to(empty_graph):
    g = deepcopy(empty_graph)
    mid = remember(g, "Memory", valid_to="2027-01-01T00:00:00+00:00")
    node = _find_node(g, mid)
    formatted = _format_memory(node, g["edges"])
    assert "valid_to: 2027-01-01T00:00:00+00:00" in formatted


# ─── CLI (argparse) ────────────────────────────────────────────────────────────


def _run_cli(*args):
    """Invoke tools/memory.py as a subprocess and return (returncode, stdout, stderr)."""
    script = Path(__file__).parent / "memory.py"
    result = subprocess.run(
        [sys.executable, str(script), *args],
        capture_output=True,
        text=True,
        cwd=str(script.parent),
    )
    return result.returncode, result.stdout, result.stderr


def test_cli_help_exits_zero():
    rc, out, _ = _run_cli("--help")
    assert rc == 0
    assert "TRUGS Memory" in out
    assert "init" in out
    assert "remember" in out


def test_cli_remember_help_lists_new_flags():
    rc, out, _ = _run_cli("remember", "--help")
    assert rc == 0
    assert "--rule" in out
    assert "--rationale" in out
    assert "--valid-to" in out
    assert "--session-id" in out
    assert "--supersede" in out


def test_cli_init_then_remember_then_recall(tmp_path):
    path = tmp_path / "mem.trug.json"
    rc, _, _ = _run_cli("init", str(path))
    assert rc == 0

    rc, out, _ = _run_cli(
        "remember", str(path), "Test rule",
        "--type", "feedback",
        "--rule", "Do X.",
        "--rationale", "Because Y.",
        "--tags", "a,b",
    )
    assert rc == 0
    assert "Remembered:" in out

    rc, out, _ = _run_cli("recall", str(path), "--all")
    assert rc == 0
    assert "Do X." in out  # rule preferred over text
    assert "tags: a, b" in out


def test_cli_recall_active_only(tmp_path):
    path = tmp_path / "mem.trug.json"
    _run_cli("init", str(path))
    _run_cli("remember", str(path), "Active one")
    _run_cli("remember", str(path), "Expired one", "--valid-to", "2024-01-01T00:00:00+00:00")

    rc, out, _ = _run_cli("recall", str(path), "--all", "--active-only")
    assert rc == 0
    assert "Active one" in out
    assert "Expired one" not in out


def test_cli_supersede_closes_old(tmp_path):
    path = tmp_path / "mem.trug.json"
    _run_cli("init", str(path))
    rc, out, _ = _run_cli("remember", str(path), "Old rule")
    assert rc == 0
    old_id = out.split("Remembered: ")[1].strip()

    rc, out, _ = _run_cli("remember", str(path), "New rule", "--supersede", old_id)
    assert rc == 0
    assert f"Superseded: {old_id}" in out

    # Inspect the graph.
    g = load_graph(path)
    old = _find_node(g, old_id)
    assert old["properties"]["valid_to"] is not None


def test_cli_unknown_command_exits_nonzero():
    rc, _, err = _run_cli("garble")
    assert rc != 0


def test_cli_no_command_prints_help(tmp_path):
    rc, out, _ = _run_cli()
    assert rc != 0
    # argparse prints help on stderr when parser.print_help() is called with no args;
    # but we call parser.print_help() which goes to stdout.
    combined = out
    assert "trugs-memory" in combined or "usage:" in combined


# ─── Parser structure sanity ──────────────────────────────────────────────────


def test_parser_includes_render_subcommand():
    parser = _build_parser()
    # parse_args will raise SystemExit if the subcommand isn't recognized.
    args = parser.parse_args(["render", "in.json", "out.md"])
    assert args.command == "render"
    assert args.in_file == "in.json"
    assert args.out_file == "out.md"
    assert args.budget == 8000
    assert args.include_rationale is False


def test_parser_render_with_flags():
    parser = _build_parser()
    args = parser.parse_args(["render", "in.json", "out.md", "--budget", "12000", "--include-rationale"])
    assert args.budget == 12000
    assert args.include_rationale is True


def test_parser_remember_minimal():
    parser = _build_parser()
    args = parser.parse_args(["remember", "file.json", "some text"])
    assert args.command == "remember"
    assert args.text == "some text"
    assert args.memory_type == "FACT"
    assert args.rule is None
