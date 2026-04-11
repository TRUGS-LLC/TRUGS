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
    SupersedeError,
    _apply_supersede,
    _build_parser,
    _find_node,
    _format_memory,
    _is_expired,
    _parse_iso_utc,
    _resolve_supersede_tail,
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


# ─── Audit round 2 regression tests ──────────────────────────────────────────


def test_save_graph_is_atomic_on_crash_simulation(tmp_path):
    """Audit #1 (HIGH) — a crash mid-save must leave the old file intact.

    We simulate a crash by patching json.dump to raise. With the atomic
    write (tempfile + os.replace), the target file must still contain
    the PREVIOUS content, not a half-written garbage mix.
    """
    path = tmp_path / "mem.trug.json"
    init_memory_graph(path)
    original_bytes = path.read_bytes()

    # Add a memory to the loaded graph.
    g = load_graph(path)
    remember(g, "new memory", memory_type="feedback")

    # Sabotage json.dump to simulate a crash mid-write.
    import memory as memory_module
    real_dump = memory_module.json.dump

    class Boom(RuntimeError):
        pass

    def broken(*args, **kwargs):
        # Write a partial byte then raise — worst case for non-atomic writers.
        args[1].write("{not-valid-json")
        raise Boom("simulated crash")

    memory_module.json.dump = broken
    try:
        with pytest.raises(Boom):
            save_graph(path, g)
    finally:
        memory_module.json.dump = real_dump

    # Target file must be untouched.
    assert path.read_bytes() == original_bytes
    # No .tmp file left behind.
    leftover = list(tmp_path.glob(".*.tmp"))
    assert leftover == [], f"Leftover tmp files: {leftover}"


def test_save_graph_creates_parent_dirs(tmp_path):
    """Audit #1 — atomic save should create parent dirs (matches old behavior)."""
    nested = tmp_path / "a" / "b" / "c" / "mem.trug.json"
    g = init_memory_graph(tmp_path / "seed.trug.json")
    save_graph(nested, g)
    assert nested.exists()


def test_supersede_rejects_self(empty_graph):
    """Audit #2 — cannot supersede own ID."""
    g = deepcopy(empty_graph)
    mid = remember(g, "rule")
    with pytest.raises(SupersedeError):
        _apply_supersede(g, new_id=mid, old_id=mid, now="2026-04-10T00:00:00+00:00")


def test_supersede_chain_closes_tail_not_original(empty_graph):
    """Audit #2 (HIGH) — supersede on an already-superseded memory links to the chain tail.

    Before the fix, supersede(A) twice would silently overwrite A's
    superseded_by pointer, orphaning the middle memory (B). Now the
    second supersede(A) closes the TAIL of A's chain instead, so the
    chain stays linear.
    """
    g = deepcopy(empty_graph)
    a = remember(g, "A", memory_type="feedback", rule="A")
    b = remember(g, "B", memory_type="feedback", rule="B", supersede=a)
    # Second supersede of A — should actually close B (the tail).
    c = remember(g, "C", memory_type="feedback", rule="C", supersede=a)

    node_a = _find_node(g, a)
    node_b = _find_node(g, b)
    node_c = _find_node(g, c)

    # A is still superseded by B (unchanged from the first supersede).
    assert node_a["properties"]["superseded_by"] == b
    # B is now superseded by C (the second supersede closed the tail).
    assert node_b["properties"]["superseded_by"] == c
    # C is still active.
    assert "superseded_by" not in node_c["properties"]
    assert "valid_to" not in node_c["properties"]

    # SUPERSEDES edges: A←B and B←C.
    sup_edges = [(e["from_id"], e["to_id"]) for e in g["edges"] if e["relation"] == "SUPERSEDES"]
    assert (b, a) in sup_edges
    assert (c, b) in sup_edges


def test_supersede_rejects_cycle_in_chain(empty_graph):
    """Audit #2 — a pre-existing cycle in the chain is refused, not made worse."""
    g = deepcopy(empty_graph)
    a = remember(g, "A")
    b = remember(g, "B")
    # Forge a cycle: A → B and B → A.
    _find_node(g, a)["properties"]["superseded_by"] = b
    _find_node(g, b)["properties"]["superseded_by"] = a
    with pytest.raises(SupersedeError):
        remember(g, "C", supersede=a)


def test_supersede_on_missing_old_id_raises(empty_graph):
    """Audit round 3 R3-1 — `remember(supersede=missing)` must RAISE, not
    silently add an orphan memory. Round-2 behavior was to return cleanly
    with no supersede side-effects, which let the CLI print
    `Superseded: <id>` for a non-existent target (lying contract).
    """
    g = deepcopy(empty_graph)
    before_nodes = len(g["nodes"])
    with pytest.raises(SupersedeError):
        remember(g, "new rule", supersede="nonexistent")
    # Graph unchanged — new memory never appended.
    assert len(g["nodes"]) == before_nodes
    sup = [e for e in g["edges"] if e["relation"] == "SUPERSEDES"]
    assert sup == []


def test_apply_supersede_helper_still_returns_false_on_missing(empty_graph):
    """Audit round 3 R3-4 — `_apply_supersede` (the lower-level helper)
    preserves its legacy False-return contract even though `remember()`
    now layers a raise on top. Direct test callers and library consumers
    that don't want to catch exceptions can still use it.
    """
    g = deepcopy(empty_graph)
    assert _apply_supersede(
        g, new_id="mem-fake", old_id="nonexistent",
        now="2026-04-10T00:00:00+00:00",
    ) is False


def test_parse_iso_utc_none_and_garbage():
    """Audit #14 (DRY) — shared helper handles every fail-open case."""
    assert _parse_iso_utc(None) is None
    assert _parse_iso_utc("") is None
    assert _parse_iso_utc("not a date") is None
    assert _parse_iso_utc(123) is None  # non-string
    # Valid ISO with timezone round-trips.
    dt = _parse_iso_utc("2026-04-10T00:00:00+00:00")
    assert dt is not None
    assert dt.tzinfo is not None
    # Naive string assumed UTC.
    dt_naive = _parse_iso_utc("2026-04-10T00:00:00")
    assert dt_naive is not None
    assert dt_naive.tzinfo == timezone.utc


def test_is_expired_uses_shared_parser(empty_graph):
    """Audit #14 — _is_expired is wired through _parse_iso_utc."""
    g = deepcopy(empty_graph)
    mid = remember(g, "memory", valid_to="banana")  # garbage
    node = _find_node(g, mid)
    # Fail-open: garbage timestamp → not expired.
    assert _is_expired(node, datetime(2099, 1, 1, tzinfo=timezone.utc)) is False


def _run_cli_u2(*args):
    """Invoke tools/memory.py as a subprocess."""
    script = Path(__file__).parent / "memory.py"
    result = subprocess.run(
        [sys.executable, str(script), *args],
        capture_output=True,
        text=True,
        cwd=str(script.parent),
    )
    return result.returncode, result.stdout, result.stderr


def test_cli_remember_rejects_garbage_valid_to(tmp_path):
    """Audit #8 (MED) — --valid-to must parse; garbage fails loud."""
    path = tmp_path / "mem.trug.json"
    _run_cli_u2("init", str(path))
    rc, _, err = _run_cli_u2(
        "remember", str(path), "rule", "--valid-to", "banana"
    )
    assert rc == 2
    assert "ISO-8601" in err


def test_cli_remember_accepts_valid_iso_valid_to(tmp_path):
    """Audit #8 — valid ISO-8601 is accepted."""
    path = tmp_path / "mem.trug.json"
    _run_cli_u2("init", str(path))
    rc, out, _ = _run_cli_u2(
        "remember", str(path), "rule", "--valid-to", "2027-01-01T00:00:00+00:00"
    )
    assert rc == 0
    assert "Remembered:" in out


def test_cli_remember_tag_can_contain_comma(tmp_path):
    """Audit #10 (MED) — --tag (repeatable) accepts commas inside a single tag."""
    path = tmp_path / "mem.trug.json"
    _run_cli_u2("init", str(path))
    rc, _, _ = _run_cli_u2(
        "remember", str(path), "rule",
        "--tag", "2026, reviewed",
        "--tag", "session-2026-04-10",
    )
    assert rc == 0
    g = load_graph(path)
    memories = [n for n in g["nodes"] if n.get("id") != "memory-root"]
    assert len(memories) == 1
    tags = memories[0]["properties"]["tags"]
    assert "2026, reviewed" in tags
    assert "session-2026-04-10" in tags


def test_cli_remember_tags_legacy_comma_form_still_works(tmp_path):
    """Audit #10 — backwards compatibility: --tags "a,b,c" still splits."""
    path = tmp_path / "mem.trug.json"
    _run_cli_u2("init", str(path))
    _run_cli_u2("remember", str(path), "rule", "--tags", "a,b,c")
    g = load_graph(path)
    tags = [n for n in g["nodes"] if n.get("id") != "memory-root"][0]["properties"]["tags"]
    assert set(tags) == {"a", "b", "c"}


def test_cli_remember_text_starting_with_dash(tmp_path):
    """Audit #11 (MED) — text beginning with `--` works when `--` separator used."""
    path = tmp_path / "mem.trug.json"
    _run_cli_u2("init", str(path))
    rc, out, err = _run_cli_u2(
        "remember", str(path), "--type", "feedback",
        "--", "--foo is a rule beginning with a flag",
    )
    assert rc == 0, f"stderr={err}"
    g = load_graph(path)
    memories = [n for n in g["nodes"] if n.get("id") != "memory-root"]
    assert len(memories) == 1
    assert memories[0]["properties"]["text"].startswith("--foo")


def test_remember_supersede_validation_leaves_graph_clean_on_error(empty_graph):
    """Audit #2 — a SupersedeError during remember() must not leave an orphan."""
    g = deepcopy(empty_graph)
    a = remember(g, "A")
    # Poison the chain with a cycle.
    _find_node(g, a)["properties"]["superseded_by"] = a  # self-loop
    before_count = len([n for n in g["nodes"] if n.get("id") != "memory-root"])
    with pytest.raises(SupersedeError):
        remember(g, "B", supersede=a)
    after_count = len([n for n in g["nodes"] if n.get("id") != "memory-root"])
    # B was never added.
    assert after_count == before_count


# ─── Audit round 3 regression tests ───────────────────────────────────────────


def test_supersede_error_is_not_a_value_error():
    """Audit round 3 R3-12 — SupersedeError subclasses Exception, not ValueError.

    This prevents a caller that catches ValueError for unrelated input
    validation from accidentally swallowing a supersede-contract violation.
    """
    assert issubclass(SupersedeError, Exception)
    assert not issubclass(SupersedeError, ValueError)


def test_save_graph_preserves_existing_mode(tmp_path):
    """Audit round 3 R3-3 — save_graph must not tighten 0o644 → 0o600."""
    import os
    path = tmp_path / "mem.trug.json"
    init_memory_graph(path)
    # Set mode to 0o644 (group/other readable) so we can verify preservation.
    os.chmod(path, 0o644)
    g = load_graph(path)
    remember(g, "rule", memory_type="feedback")
    save_graph(path, g)
    mode = path.stat().st_mode & 0o777
    assert mode == 0o644, f"save_graph clobbered mode: expected 0o644, got 0o{mode:o}"


def test_save_graph_fsyncs_parent_directory(tmp_path, monkeypatch):
    """Audit round 3 R3-2 — save_graph must fsync the parent dir after replace.

    We can't easily test that the POSIX semantics produce durable rename
    metadata, but we CAN verify that `os.fsync` is called on a directory
    fd after `os.replace`. Monkeypatch `os.fsync` to record calls.
    """
    import os
    import memory as memory_module
    path = tmp_path / "mem.trug.json"
    init_memory_graph(path)

    fsync_fds: list = []
    real_fsync = os.fsync

    def tracking_fsync(fd):
        fsync_fds.append(fd)
        return real_fsync(fd)

    monkeypatch.setattr(memory_module.os, "fsync", tracking_fsync)
    g = load_graph(path)
    remember(g, "new memory")
    save_graph(path, g)

    # At least 2 fsyncs: the tempfile content, and the parent directory.
    assert len(fsync_fds) >= 2, f"Expected ≥2 fsyncs (file + dir), got {len(fsync_fds)}"


def test_cmd_render_uses_load_graph(tmp_path, monkeypatch):
    """Audit round 3 R3-10 — _cmd_render routes through load_graph."""
    import memory as memory_module
    path = tmp_path / "mem.trug.json"
    init_memory_graph(path)
    g = load_graph(path)
    remember(g, "rule", memory_type="feedback")
    save_graph(path, g)

    call_count = [0]
    real_load = memory_module.load_graph

    def tracking_load(p):
        call_count[0] += 1
        return real_load(p)

    monkeypatch.setattr(memory_module, "load_graph", tracking_load)

    from argparse import Namespace
    args = Namespace(
        in_file=str(path),
        out_file=str(tmp_path / "MEMORY.md"),
        budget=8000,
        include_rationale=False,
    )
    rc = memory_module._cmd_render(args)
    assert rc == 0
    assert call_count[0] == 1, "Expected _cmd_render to call load_graph exactly once"


def test_cli_remember_supersede_reports_chain_tail(tmp_path):
    """Audit round 3 R3-1 corollary — the CLI must report the memory that
    actually got closed, not necessarily the one the user named (which may
    be mid-chain).
    """
    path = tmp_path / "mem.trug.json"
    _run_cli_u2("init", str(path))

    rc, out_a, _ = _run_cli_u2("remember", str(path), "A", "--rule", "A")
    a_id = out_a.split("Remembered: ")[1].strip()

    rc, out_b, _ = _run_cli_u2("remember", str(path), "B", "--rule", "B", "--supersede", a_id)
    assert "Superseded:" in out_b
    b_id = out_b.split("Remembered: ")[1].split()[0]

    # Supersede A again (chain is A→B, so tail is B now).
    rc, out_c, err = _run_cli_u2("remember", str(path), "C", "--rule", "C", "--supersede", a_id)
    assert rc == 0, err
    assert "tail of" in out_c, f"Expected chain-tail annotation in: {out_c}"
    # The annotation says "tail of <a_id>" and the closed id is b_id.
    assert b_id in out_c
    assert a_id in out_c


def test_cli_remember_supersede_missing_target_fails_loud(tmp_path):
    """Audit round 3 R3-1 — unknown supersede target must return non-zero.

    Before the fix, `trugs-memory remember mem.json x --supersede nonexistent`
    returned 0 and even printed "Superseded: nonexistent" for a memory
    that did not exist.
    """
    path = tmp_path / "mem.trug.json"
    _run_cli_u2("init", str(path))
    rc, _, err = _run_cli_u2(
        "remember", str(path), "rule", "--supersede", "nonexistent"
    )
    assert rc == 2
    assert "not found" in err.lower()
