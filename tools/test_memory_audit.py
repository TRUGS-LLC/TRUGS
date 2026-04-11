"""Tests for trugs-memory audit / reconcile — instrumentation + duplicate detection."""

from __future__ import annotations

import subprocess
import sys
import tempfile
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from memory import _find_node, init_memory_graph, load_graph, remember, save_graph
from memory_audit import (
    DEFAULT_SIMILARITY_THRESHOLD,
    DeadRule,
    ReconcileCandidate,
    _jaccard,
    _parse_duration_days,
    _tokenize,
    bump_hit,
    dead_rules,
    reconcile_candidates,
)


# ─── Fixtures ──────────────────────────────────────────────────────────────────


@pytest.fixture
def empty_graph():
    with tempfile.TemporaryDirectory() as d:
        path = Path(d) / "memory.trug.json"
        yield init_memory_graph(path)


@pytest.fixture
def fixed_now():
    return datetime(2026, 4, 10, 12, 0, 0, tzinfo=timezone.utc)


@pytest.fixture
def graph_with_old_feedback(empty_graph, fixed_now):
    """Graph with one recent + one old unconsulted feedback memory."""
    g = deepcopy(empty_graph)
    old_id = remember(g, "Old unconsulted rule", memory_type="feedback", rule="Old rule")
    new_id = remember(g, "Recent rule", memory_type="feedback", rule="New rule")

    # Force timestamps so the test is deterministic.
    _find_node(g, old_id)["properties"]["created"] = (fixed_now - timedelta(days=60)).isoformat()
    _find_node(g, new_id)["properties"]["created"] = (fixed_now - timedelta(days=3)).isoformat()
    return g, old_id, new_id


# ─── bump_hit ──────────────────────────────────────────────────────────────────


def test_bump_hit_increments_count(empty_graph, fixed_now):
    g = deepcopy(empty_graph)
    mid = remember(g, "Rule", memory_type="feedback")
    assert "hit_count" not in _find_node(g, mid)["properties"]

    assert bump_hit(g, mid, now=fixed_now) is True
    props = _find_node(g, mid)["properties"]
    assert props["hit_count"] == 1
    assert props["last_hit"] == fixed_now.isoformat()

    bump_hit(g, mid, now=fixed_now + timedelta(hours=1))
    assert _find_node(g, mid)["properties"]["hit_count"] == 2


def test_bump_hit_returns_false_on_unknown(empty_graph, fixed_now):
    g = deepcopy(empty_graph)
    assert bump_hit(g, "nonexistent", now=fixed_now) is False


def test_bump_hit_refuses_memory_root(empty_graph, fixed_now):
    g = deepcopy(empty_graph)
    assert bump_hit(g, "memory-root", now=fixed_now) is False


def test_bump_hit_on_memory_with_existing_count(empty_graph, fixed_now):
    g = deepcopy(empty_graph)
    mid = remember(g, "Rule")
    _find_node(g, mid)["properties"]["hit_count"] = 5
    bump_hit(g, mid, now=fixed_now)
    assert _find_node(g, mid)["properties"]["hit_count"] == 6


# ─── dead_rules ────────────────────────────────────────────────────────────────


def test_dead_rules_finds_old_unconsulted_feedback(graph_with_old_feedback, fixed_now):
    g, old_id, new_id = graph_with_old_feedback
    dead = dead_rules(g, older_than_days=30, now=fixed_now)
    assert len(dead) == 1
    assert dead[0].memory_id == old_id


def test_dead_rules_skips_recent_memories(empty_graph, fixed_now):
    g = deepcopy(empty_graph)
    mid = remember(g, "Just-written rule", memory_type="feedback")
    # created is ~now by default — not dead yet.
    dead = dead_rules(g, older_than_days=30, now=fixed_now)
    assert mid not in [d.memory_id for d in dead]


def test_dead_rules_skips_consulted_memories(graph_with_old_feedback, fixed_now):
    g, old_id, _ = graph_with_old_feedback
    bump_hit(g, old_id, now=fixed_now)
    dead = dead_rules(g, older_than_days=30, now=fixed_now)
    # Once consulted, no longer dead.
    assert old_id not in [d.memory_id for d in dead]


def test_dead_rules_skips_non_feedback_types(empty_graph, fixed_now):
    g = deepcopy(empty_graph)
    for mt in ("user", "project", "reference", "fact"):
        mid = remember(g, f"Old {mt} memory", memory_type=mt)
        _find_node(g, mid)["properties"]["created"] = (fixed_now - timedelta(days=60)).isoformat()
    dead = dead_rules(g, older_than_days=30, now=fixed_now)
    assert dead == []


def test_dead_rules_sorted_oldest_first(empty_graph, fixed_now):
    g = deepcopy(empty_graph)
    a = remember(g, "A", memory_type="feedback")
    b = remember(g, "B", memory_type="feedback")
    c = remember(g, "C", memory_type="feedback")
    _find_node(g, a)["properties"]["created"] = "2026-01-01T00:00:00+00:00"
    _find_node(g, b)["properties"]["created"] = "2026-02-01T00:00:00+00:00"
    _find_node(g, c)["properties"]["created"] = "2026-03-01T00:00:00+00:00"
    dead = dead_rules(g, older_than_days=10, now=fixed_now)
    assert [d.memory_id for d in dead] == [a, b, c]


def test_dead_rules_handles_missing_created(empty_graph, fixed_now):
    g = deepcopy(empty_graph)
    mid = remember(g, "Rule", memory_type="feedback")
    del _find_node(g, mid)["properties"]["created"]
    # Should not crash, should not mark as dead (unparseable = skip).
    dead = dead_rules(g, older_than_days=1, now=fixed_now)
    assert mid not in [d.memory_id for d in dead]


# ─── reconcile_candidates ─────────────────────────────────────────────────────


def test_reconcile_finds_exact_duplicates(empty_graph):
    g = deepcopy(empty_graph)
    remember(g, "Always fix every audit finding", memory_type="feedback")
    remember(g, "Always fix every audit finding", memory_type="feedback")
    candidates = reconcile_candidates(g, threshold=0.9)
    assert len(candidates) == 1
    assert candidates[0].similarity == 1.0


def test_reconcile_finds_near_duplicates(empty_graph):
    g = deepcopy(empty_graph)
    remember(g, "Always fix every audit finding regardless of severity", memory_type="feedback")
    remember(g, "Fix every finding in the audit regardless of severity level", memory_type="feedback")
    candidates = reconcile_candidates(g, threshold=0.5)
    assert len(candidates) >= 1


def test_reconcile_respects_threshold(empty_graph):
    g = deepcopy(empty_graph)
    remember(g, "apple banana cherry", memory_type="feedback")
    remember(g, "apple banana cherry date", memory_type="feedback")
    # 3/4 = 0.75 Jaccard.
    strict = reconcile_candidates(g, threshold=0.9)
    loose = reconcile_candidates(g, threshold=0.7)
    assert len(strict) == 0
    assert len(loose) == 1


def test_reconcile_dedupes_symmetric_pairs(empty_graph):
    g = deepcopy(empty_graph)
    remember(g, "identical text here please", memory_type="feedback")
    remember(g, "identical text here please", memory_type="feedback")
    candidates = reconcile_candidates(g, threshold=0.9)
    assert len(candidates) == 1  # Not 2.


def test_reconcile_sorted_by_similarity_descending(empty_graph):
    g = deepcopy(empty_graph)
    remember(g, "alpha beta gamma delta", memory_type="feedback")
    remember(g, "alpha beta gamma zeta", memory_type="feedback")  # 3/5 = 0.6
    remember(g, "alpha beta gamma delta", memory_type="feedback")  # 4/4 = 1.0 vs first
    candidates = reconcile_candidates(g, threshold=0.5)
    assert len(candidates) >= 2
    sims = [c.similarity for c in candidates]
    assert sims == sorted(sims, reverse=True)


def test_reconcile_filters_by_type(empty_graph):
    g = deepcopy(empty_graph)
    remember(g, "same text here", memory_type="feedback")
    remember(g, "same text here", memory_type="user")
    # Cross-type pair should NOT surface when --type filter is set.
    all_candidates = reconcile_candidates(g, threshold=0.9)
    feedback_only = reconcile_candidates(g, threshold=0.9, memory_type="feedback")
    assert len(all_candidates) == 1
    assert len(feedback_only) == 0


def test_reconcile_empty_graph_returns_empty(empty_graph):
    assert reconcile_candidates(empty_graph) == []


def test_reconcile_prefers_rule_over_text_for_comparison(empty_graph):
    g = deepcopy(empty_graph)
    # Two memories with very different text but identical rules.
    a = remember(g, "Long verbose prose paragraph one", memory_type="feedback", rule="Do X always")
    b = remember(g, "Entirely different verbose text", memory_type="feedback", rule="Do X always")
    candidates = reconcile_candidates(g, threshold=0.9)
    assert len(candidates) == 1
    assert candidates[0].similarity == 1.0


def test_reconcile_skips_memories_with_empty_text(empty_graph):
    g = deepcopy(empty_graph)
    remember(g, "", memory_type="feedback")  # Empty text.
    remember(g, "nonzero content here", memory_type="feedback")
    candidates = reconcile_candidates(g, threshold=0.0)
    # No pair surfaced because one side has no tokens.
    assert candidates == []


# ─── Helpers ──────────────────────────────────────────────────────────────────


def test_tokenize_lowercases_and_alphanumeric_only():
    assert _tokenize("Hello, WORLD! 123") == {"hello", "world", "123"}
    assert _tokenize("") == set()
    assert _tokenize("punctuation!!! only???") == {"punctuation", "only"}


def test_jaccard_basic():
    assert _jaccard(set(), set()) == 0.0
    assert _jaccard({"a"}, {"a"}) == 1.0
    assert _jaccard({"a", "b"}, {"a", "c"}) == 1 / 3
    assert _jaccard({"a", "b", "c"}, {"d", "e", "f"}) == 0.0


def test_parse_duration_days_shortforms():
    assert _parse_duration_days("30d") == 30
    assert _parse_duration_days("2w") == 14
    assert _parse_duration_days("1m") == 30
    assert _parse_duration_days("1y") == 365
    assert _parse_duration_days("60") == 60


def test_parse_duration_days_rejects_empty():
    with pytest.raises(ValueError):
        _parse_duration_days("")


# ─── CLI ───────────────────────────────────────────────────────────────────────


def _run_cli(*args):
    script = Path(__file__).parent / "memory_audit.py"
    result = subprocess.run(
        [sys.executable, str(script), *args],
        capture_output=True,
        text=True,
        cwd=str(script.parent),
    )
    return result.returncode, result.stdout, result.stderr


def test_cli_help():
    rc, out, _ = _run_cli("--help")
    assert rc == 0
    assert "TRUGS Memory Audit" in out


def test_cli_audit_missing_file():
    rc, _, err = _run_cli("audit", "/nonexistent/path.json")
    assert rc == 1
    assert "not found" in err


def test_cli_audit_reports_dead_rules(tmp_path, fixed_now):
    path = tmp_path / "mem.trug.json"
    g = init_memory_graph(path)
    mid = remember(g, "Old rule", memory_type="feedback")
    _find_node(g, mid)["properties"]["created"] = "2026-01-01T00:00:00+00:00"
    save_graph(path, g)

    rc, out, _ = _run_cli("audit", str(path), "--dead-rules", "30d")
    assert rc == 0
    assert "1 dead feedback rule" in out


def test_cli_audit_bump(tmp_path):
    path = tmp_path / "mem.trug.json"
    g = init_memory_graph(path)
    mid = remember(g, "Rule", memory_type="feedback")
    save_graph(path, g)

    rc, out, _ = _run_cli("audit", str(path), "--bump", mid)
    assert rc == 0
    assert "Bumped" in out

    g2 = load_graph(path)
    assert _find_node(g2, mid)["properties"]["hit_count"] == 1


def test_cli_audit_bump_unknown_id(tmp_path):
    path = tmp_path / "mem.trug.json"
    init_memory_graph(path)
    rc, _, err = _run_cli("audit", str(path), "--bump", "nonexistent")
    assert rc == 1
    assert "not found" in err


def test_cli_reconcile(tmp_path):
    path = tmp_path / "mem.trug.json"
    g = init_memory_graph(path)
    remember(g, "duplicate content please", memory_type="feedback")
    remember(g, "duplicate content please", memory_type="feedback")
    save_graph(path, g)

    rc, out, _ = _run_cli("reconcile", str(path), "--threshold", "0.9")
    assert rc == 0
    assert "candidate pair" in out


def test_cli_reconcile_no_candidates(tmp_path):
    path = tmp_path / "mem.trug.json"
    g = init_memory_graph(path)
    remember(g, "unique alpha", memory_type="feedback")
    remember(g, "distinct beta", memory_type="feedback")
    save_graph(path, g)

    rc, out, _ = _run_cli("reconcile", str(path), "--threshold", "0.9")
    assert rc == 0
    assert "No duplicate candidates" in out


def test_cli_unknown_subcommand():
    rc, _, err = _run_cli("garble")
    assert rc == 2
    assert "Unknown command" in err
