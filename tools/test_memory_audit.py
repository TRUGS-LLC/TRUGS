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


# AGENT claude SHALL DEFINE RECORD empty_graph AS A RECORD fixture.
@pytest.fixture
def empty_graph():
    with tempfile.TemporaryDirectory() as d:
        path = Path(d) / "memory.trug.json"
        yield init_memory_graph(path)


# AGENT claude SHALL DEFINE RECORD fixed_now AS A RECORD fixture.
@pytest.fixture
def fixed_now():
    return datetime(2026, 4, 10, 12, 0, 0, tzinfo=timezone.utc)


# AGENT claude SHALL DEFINE RECORD graph_with_old_feedback AS A RECORD fixture.
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


# AGENT SHALL VALIDATE DATA memory_audit.
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


# AGENT SHALL VALIDATE DATA memory_audit.
def test_bump_hit_returns_false_on_unknown(empty_graph, fixed_now):
    g = deepcopy(empty_graph)
    assert bump_hit(g, "nonexistent", now=fixed_now) is False


# AGENT SHALL VALIDATE DATA memory_audit.
def test_bump_hit_refuses_memory_root(empty_graph, fixed_now):
    g = deepcopy(empty_graph)
    assert bump_hit(g, "memory-root", now=fixed_now) is False


# AGENT SHALL VALIDATE DATA memory_audit.
def test_bump_hit_on_memory_with_existing_count(empty_graph, fixed_now):
    g = deepcopy(empty_graph)
    mid = remember(g, "Rule")
    _find_node(g, mid)["properties"]["hit_count"] = 5
    bump_hit(g, mid, now=fixed_now)
    assert _find_node(g, mid)["properties"]["hit_count"] == 6


# ─── dead_rules ────────────────────────────────────────────────────────────────


# AGENT SHALL VALIDATE DATA memory_audit.
def test_dead_rules_finds_old_unconsulted_feedback(graph_with_old_feedback, fixed_now):
    g, old_id, new_id = graph_with_old_feedback
    dead = dead_rules(g, older_than_days=30, now=fixed_now)
    assert len(dead) == 1
    assert dead[0].memory_id == old_id


# AGENT SHALL VALIDATE DATA memory_audit.
def test_dead_rules_skips_recent_memories(empty_graph, fixed_now):
    """Audit #15 — use controlled created timestamps instead of relying on
    wall-clock `datetime.now()`. Before the fix, this test only passed by
    accident of the system clock being past `fixed_now`.
    """
    g = deepcopy(empty_graph)
    mid = remember(g, "Just-written rule", memory_type="feedback")
    # Force created = fixed_now - 3 days. Clearly within the 30d threshold,
    # independent of the wall clock.
    _find_node(g, mid)["properties"]["created"] = (fixed_now - timedelta(days=3)).isoformat()
    dead = dead_rules(g, older_than_days=30, now=fixed_now)
    assert mid not in [d.memory_id for d in dead]


# AGENT SHALL VALIDATE DATA memory_audit.
def test_dead_rules_skips_consulted_memories(graph_with_old_feedback, fixed_now):
    g, old_id, _ = graph_with_old_feedback
    bump_hit(g, old_id, now=fixed_now)
    dead = dead_rules(g, older_than_days=30, now=fixed_now)
    # Once consulted, no longer dead.
    assert old_id not in [d.memory_id for d in dead]


# AGENT SHALL VALIDATE DATA memory_audit.
def test_dead_rules_skips_non_feedback_types(empty_graph, fixed_now):
    g = deepcopy(empty_graph)
    for mt in ("user", "project", "reference", "fact"):
        mid = remember(g, f"Old {mt} memory", memory_type=mt)
        _find_node(g, mid)["properties"]["created"] = (fixed_now - timedelta(days=60)).isoformat()
    dead = dead_rules(g, older_than_days=30, now=fixed_now)
    assert dead == []


# AGENT SHALL VALIDATE DATA memory_audit.
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


# AGENT SHALL VALIDATE DATA memory_audit.
def test_dead_rules_handles_missing_created(empty_graph, fixed_now):
    g = deepcopy(empty_graph)
    mid = remember(g, "Rule", memory_type="feedback")
    del _find_node(g, mid)["properties"]["created"]
    # Should not crash, should not mark as dead (unparseable = skip).
    dead = dead_rules(g, older_than_days=1, now=fixed_now)
    assert mid not in [d.memory_id for d in dead]


# ─── reconcile_candidates ─────────────────────────────────────────────────────


# AGENT SHALL VALIDATE DATA memory_audit.
def test_reconcile_finds_exact_duplicates(empty_graph):
    g = deepcopy(empty_graph)
    remember(g, "Always fix every audit finding", memory_type="feedback")
    remember(g, "Always fix every audit finding", memory_type="feedback")
    candidates = reconcile_candidates(g, threshold=0.9)
    assert len(candidates) == 1
    assert candidates[0].similarity == 1.0


# AGENT SHALL VALIDATE DATA memory_audit.
def test_reconcile_finds_near_duplicates(empty_graph):
    g = deepcopy(empty_graph)
    remember(g, "Always fix every audit finding regardless of severity", memory_type="feedback")
    remember(g, "Fix every finding in the audit regardless of severity level", memory_type="feedback")
    candidates = reconcile_candidates(g, threshold=0.5)
    assert len(candidates) >= 1


# AGENT SHALL VALIDATE DATA memory_audit.
def test_reconcile_respects_threshold(empty_graph):
    g = deepcopy(empty_graph)
    remember(g, "apple banana cherry", memory_type="feedback")
    remember(g, "apple banana cherry date", memory_type="feedback")
    # 3/4 = 0.75 Jaccard.
    strict = reconcile_candidates(g, threshold=0.9)
    loose = reconcile_candidates(g, threshold=0.7)
    assert len(strict) == 0
    assert len(loose) == 1


# AGENT SHALL VALIDATE DATA memory_audit.
def test_reconcile_dedupes_symmetric_pairs(empty_graph):
    g = deepcopy(empty_graph)
    remember(g, "identical text here please", memory_type="feedback")
    remember(g, "identical text here please", memory_type="feedback")
    candidates = reconcile_candidates(g, threshold=0.9)
    assert len(candidates) == 1  # Not 2.


# AGENT SHALL VALIDATE DATA memory_audit.
def test_reconcile_sorted_by_similarity_descending(empty_graph):
    g = deepcopy(empty_graph)
    remember(g, "alpha beta gamma delta", memory_type="feedback")
    remember(g, "alpha beta gamma zeta", memory_type="feedback")  # 3/5 = 0.6
    remember(g, "alpha beta gamma delta", memory_type="feedback")  # 4/4 = 1.0 vs first
    candidates = reconcile_candidates(g, threshold=0.5)
    assert len(candidates) >= 2
    sims = [c.similarity for c in candidates]
    assert sims == sorted(sims, reverse=True)


# AGENT SHALL VALIDATE DATA memory_audit.
def test_reconcile_filters_by_type(empty_graph):
    g = deepcopy(empty_graph)
    remember(g, "same text here", memory_type="feedback")
    remember(g, "same text here", memory_type="user")
    # Cross-type pair should NOT surface when --type filter is set.
    all_candidates = reconcile_candidates(g, threshold=0.9)
    feedback_only = reconcile_candidates(g, threshold=0.9, memory_type="feedback")
    assert len(all_candidates) == 1
    assert len(feedback_only) == 0


# AGENT SHALL VALIDATE DATA memory_audit.
def test_reconcile_empty_graph_returns_empty(empty_graph):
    assert reconcile_candidates(empty_graph) == []


# AGENT SHALL VALIDATE DATA memory_audit.
def test_reconcile_prefers_rule_over_text_for_comparison(empty_graph):
    g = deepcopy(empty_graph)
    # Two memories with very different text but identical rules.
    a = remember(g, "Long verbose prose paragraph one", memory_type="feedback", rule="Do X always")
    b = remember(g, "Entirely different verbose text", memory_type="feedback", rule="Do X always")
    candidates = reconcile_candidates(g, threshold=0.9)
    assert len(candidates) == 1
    assert candidates[0].similarity == 1.0


# AGENT SHALL VALIDATE DATA memory_audit.
def test_reconcile_skips_memories_with_empty_text(empty_graph):
    g = deepcopy(empty_graph)
    remember(g, "", memory_type="feedback")  # Empty text.
    remember(g, "nonzero content here", memory_type="feedback")
    candidates = reconcile_candidates(g, threshold=0.0)
    # No pair surfaced because one side has no tokens.
    assert candidates == []


# ─── Helpers ──────────────────────────────────────────────────────────────────


# AGENT SHALL VALIDATE DATA memory_audit.
def test_tokenize_lowercases_and_alphanumeric_only():
    assert _tokenize("Hello, WORLD! 123") == {"hello", "world", "123"}
    assert _tokenize("") == set()
    assert _tokenize("punctuation!!! only???") == {"punctuation", "only"}


# AGENT SHALL VALIDATE DATA memory_audit.
def test_jaccard_basic():
    assert _jaccard(set(), set()) == 0.0
    assert _jaccard({"a"}, {"a"}) == 1.0
    assert _jaccard({"a", "b"}, {"a", "c"}) == 1 / 3
    assert _jaccard({"a", "b", "c"}, {"d", "e", "f"}) == 0.0


# AGENT SHALL VALIDATE DATA memory_audit.
def test_parse_duration_days_shortforms():
    assert _parse_duration_days("30d") == 30
    assert _parse_duration_days("2w") == 14
    assert _parse_duration_days("1mo") == 30  # Round 3 R3-8: 'mo' for months
    assert _parse_duration_days("1y") == 365
    assert _parse_duration_days("60") == 60


# AGENT SHALL VALIDATE DATA memory_audit.
def test_parse_duration_days_rejects_bare_m():
    """Audit round 3 R3-8 — bare `1m` is ambiguous (minutes vs months) and rejected."""
    with pytest.raises(ValueError) as exc:
        _parse_duration_days("1m")
    assert "ambiguous" in str(exc.value).lower()


# AGENT SHALL VALIDATE DATA memory_audit.
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


# AGENT SHALL VALIDATE DATA memory_audit.
def test_cli_help():
    rc, out, _ = _run_cli("--help")
    assert rc == 0
    assert "TRUGS Memory Audit" in out


# AGENT SHALL VALIDATE DATA memory_audit.
def test_cli_audit_missing_file():
    rc, _, err = _run_cli("audit", "/nonexistent/path.json")
    assert rc == 1
    assert "not found" in err


# AGENT SHALL VALIDATE DATA memory_audit.
def test_cli_audit_reports_dead_rules(tmp_path, fixed_now):
    path = tmp_path / "mem.trug.json"
    g = init_memory_graph(path)
    mid = remember(g, "Old rule", memory_type="feedback")
    _find_node(g, mid)["properties"]["created"] = "2026-01-01T00:00:00+00:00"
    save_graph(path, g)

    rc, out, _ = _run_cli("audit", str(path), "--dead-rules", "30d")
    assert rc == 0
    assert "1 dead feedback rule" in out


# AGENT SHALL VALIDATE DATA memory_audit.
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


# AGENT SHALL VALIDATE DATA memory_audit.
def test_cli_audit_bump_unknown_id(tmp_path):
    path = tmp_path / "mem.trug.json"
    init_memory_graph(path)
    rc, _, err = _run_cli("audit", str(path), "--bump", "nonexistent")
    assert rc == 1
    assert "not found" in err


# AGENT SHALL VALIDATE DATA memory_audit.
def test_cli_reconcile(tmp_path):
    path = tmp_path / "mem.trug.json"
    g = init_memory_graph(path)
    remember(g, "duplicate content please", memory_type="feedback")
    remember(g, "duplicate content please", memory_type="feedback")
    save_graph(path, g)

    rc, out, _ = _run_cli("reconcile", str(path), "--threshold", "0.9")
    assert rc == 0
    assert "candidate pair" in out


# AGENT SHALL VALIDATE DATA memory_audit.
def test_cli_reconcile_no_candidates(tmp_path):
    path = tmp_path / "mem.trug.json"
    g = init_memory_graph(path)
    remember(g, "unique alpha", memory_type="feedback")
    remember(g, "distinct beta", memory_type="feedback")
    save_graph(path, g)

    rc, out, _ = _run_cli("reconcile", str(path), "--threshold", "0.9")
    assert rc == 0
    assert "No duplicate candidates" in out


# AGENT SHALL VALIDATE DATA memory_audit.
def test_cli_unknown_subcommand():
    rc, _, err = _run_cli("garble")
    assert rc == 2
    assert "Unknown command" in err


# ─── Audit round 2 regression tests ──────────────────────────────────────────


# AGENT SHALL VALIDATE DATA memory_audit.
def test_parse_duration_rejects_negative():
    """Audit #4 (HIGH) — `-30d` must raise, not produce a future threshold."""
    with pytest.raises(ValueError):
        _parse_duration_days("-30d")
    with pytest.raises(ValueError):
        _parse_duration_days("-1")
    with pytest.raises(ValueError):
        _parse_duration_days("0d")
    with pytest.raises(ValueError):
        _parse_duration_days("0")


# AGENT SHALL VALIDATE DATA memory_audit.
def test_parse_duration_positive_still_works():
    """Audit #4 — positive durations continue to parse."""
    assert _parse_duration_days("30d") == 30
    assert _parse_duration_days("1") == 1


# AGENT SHALL VALIDATE DATA memory_audit.
def test_cli_audit_rejects_negative_duration(tmp_path):
    """Audit #4 — CLI fails loud on a negative duration."""
    path = tmp_path / "mem.trug.json"
    init_memory_graph(path)
    rc, _, err = _run_cli("audit", str(path), "--dead-rules", "-30d")
    assert rc == 2
    assert "invalid duration" in err.lower() or "must be positive" in err.lower()


# AGENT SHALL VALIDATE DATA memory_audit.
def test_reconcile_length_blocking_skips_mismatched_sizes(empty_graph):
    """Audit #6 (MED) — length-ratio pre-check avoids Jaccard when impossible.

    Two token sets of size 1 and size 100 have Jaccard upper bound 1/100 = 0.01;
    at threshold 0.7 we should skip without computing the full intersection.
    The test verifies correctness (no candidate surfaced at 0.7), and a
    companion test at threshold 0.005 verifies that the optimization doesn't
    hide a legitimate low-similarity match.
    """
    g = deepcopy(empty_graph)
    remember(g, "one", memory_type="feedback")  # 1 token
    remember(g, " ".join(f"word{i}" for i in range(100)), memory_type="feedback")  # 100 tokens
    remember(g, " ".join(f"word{i}" for i in range(100)), memory_type="feedback")  # another 100
    # At threshold 0.7, the 1-vs-100 pair is pruned; the 100-vs-100 pair matches.
    candidates = reconcile_candidates(g, threshold=0.7)
    assert len(candidates) == 1
    # At threshold 0.005, the length-ratio filter admits the mismatched pair
    # for real Jaccard computation, which returns 0 (disjoint) → still no match.
    candidates_loose = reconcile_candidates(g, threshold=0.005)
    # Mismatched pair passes the length ratio (0.01 ≥ 0.005) but actual Jaccard is 0.
    # So we only see the 100-vs-100 match again.
    assert len(candidates_loose) == 1


# AGENT SHALL VALIDATE DATA memory_audit.
def test_dead_rules_strips_whitespace_from_memory_type(empty_graph, fixed_now):
    """Audit #17 (LOW) — ' feedback ' should still match the feedback filter."""
    g = deepcopy(empty_graph)
    mid = remember(g, "Old rule", memory_type="feedback")
    # Inject whitespace directly (simulating data that drifted).
    _find_node(g, mid)["properties"]["memory_type"] = "  feedback  "
    _find_node(g, mid)["properties"]["created"] = "2026-01-01T00:00:00+00:00"
    dead = dead_rules(g, older_than_days=10, now=fixed_now)
    assert len(dead) == 1
    assert dead[0].memory_id == mid


# AGENT SHALL VALIDATE DATA memory_audit.
def test_dead_rules_uses_shared_iso_parser(empty_graph, fixed_now):
    """Audit #14 — _parse_iso in this module should route through the shared
    memory._parse_iso_utc helper, same as memory._is_expired.
    """
    from memory_audit import _parse_iso
    from memory import _parse_iso_utc
    # Same inputs → same outputs.
    for sample in (None, "", "not a date", "2026-04-10T00:00:00+00:00", "2026-04-10T00:00:00"):
        assert _parse_iso(sample) == _parse_iso_utc(sample)


# AGENT SHALL VALIDATE DATA memory_audit.
def test_parse_duration_days_overflow_capped():
    """M2 — 99999999y must raise ValueError, not OverflowError."""
    from memory_audit import _parse_duration_days
    with pytest.raises(ValueError, match="too large"):
        _parse_duration_days("99999999y")
    # 999y is just under the cap and should still work
    assert _parse_duration_days("999y") == 999 * 365


# AGENT SHALL VALIDATE DATA memory_audit.
def test_parse_duration_days_rejects_none():
    """L2 — None must raise ValueError, not AttributeError."""
    from memory_audit import _parse_duration_days
    with pytest.raises(ValueError, match="string"):
        _parse_duration_days(None)


# AGENT SHALL VALIDATE DATA memory_audit.
def test_parse_duration_days_rejects_int():
    """L2 — integer input must raise ValueError."""
    from memory_audit import _parse_duration_days
    with pytest.raises(ValueError, match="string"):
        _parse_duration_days(123)


# AGENT SHALL VALIDATE DATA memory_audit.
def test_parse_duration_days_rejects_internal_whitespace():
    """L2 — '30 d' with internal whitespace must raise ValueError."""
    from memory_audit import _parse_duration_days
    with pytest.raises(ValueError, match="whitespace"):
        _parse_duration_days("30 d")
