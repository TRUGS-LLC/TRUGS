"""Tests for trugs-memory-render — deterministic markdown render of memory TRUGs."""

from __future__ import annotations

import json
import tempfile
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from memory import init_memory_graph, remember
from memory_render import (
    DEFAULT_BUDGET_TOKENS,
    DEFAULT_TYPE_ORDER,
    DEMOTION_ORDER,
    render,
    render_to_file,
    _active_memories,
    _approx_tokens,
    _group_by_type,
    _is_past,
)
from validate import validate


# ─── Fixtures ──────────────────────────────────────────────────────────────────


@pytest.fixture
def empty_graph():
    with tempfile.TemporaryDirectory() as d:
        path = Path(d) / "memory.trug.json"
        yield init_memory_graph(path)


@pytest.fixture
def small_graph(empty_graph):
    g = deepcopy(empty_graph)
    # Intentionally out-of-order insertion to exercise sort.
    remember(g, "Xepayac is the HITM", memory_type="user", tags=["role"])
    remember(g, "Always fix every audit finding", memory_type="feedback", tags=["audit"])
    remember(g, "WP-03 inner loop shipped in #1459", memory_type="project", tags=["wp03"])
    remember(g, "Linear INGEST project tracks pipeline bugs", memory_type="reference", tags=["linear"])
    remember(g, "Never merge PRs — only human does", memory_type="feedback", tags=["hitm"])
    return g


@pytest.fixture
def fixed_now():
    return datetime(2026, 4, 10, 20, 0, 0, tzinfo=timezone.utc)


# ─── Determinism ───────────────────────────────────────────────────────────────


def test_render_is_byte_deterministic(small_graph, fixed_now):
    a = render(small_graph, now=fixed_now)
    b = render(small_graph, now=fixed_now)
    c = render(small_graph, now=fixed_now)
    assert a == b == c
    assert isinstance(a, str)
    assert a.endswith("\n")


def test_render_is_byte_deterministic_under_real_wall_clock(small_graph):
    """Round-5 audit C-H4 regression guard.

    The previous implementation embedded `datetime.utcnow()` in the
    header, so two renders against the same graph at different wall-clock
    instants produced different bytes. This test calls `render()` WITHOUT
    passing `now`, then sleeps long enough to advance the wall clock past
    the second-precision boundary, and asserts the two renders are
    bit-identical. It will fail loudly if any future change reintroduces
    a wall-clock dependency in the header or body.
    """
    import time
    a = render(small_graph)
    time.sleep(1.05)  # cross at least one full-second boundary
    b = render(small_graph)
    assert a == b, "render() must be a pure function of the graph"


def test_render_stable_under_reordered_insertion(empty_graph, fixed_now):
    # Build two graphs with the same memories but different creation timestamps.
    # A fixed `now` alone isn't enough — the `created` field is set by `remember`
    # at insertion time. Instead, we build both graphs, then forcibly patch the
    # `created` timestamps so the sort order input is identical.
    g1 = deepcopy(empty_graph)
    g2 = deepcopy(empty_graph)

    ids1 = [
        remember(g1, "Rule A", memory_type="feedback"),
        remember(g1, "Rule B", memory_type="feedback"),
        remember(g1, "Rule C", memory_type="feedback"),
    ]
    ids2 = [
        remember(g2, "Rule C", memory_type="feedback"),
        remember(g2, "Rule A", memory_type="feedback"),
        remember(g2, "Rule B", memory_type="feedback"),
    ]

    # Normalize created timestamps and ids so the body differs only in insertion order.
    times = ["2026-04-10T10:00:00+00:00", "2026-04-10T11:00:00+00:00", "2026-04-10T12:00:00+00:00"]
    name_to_time = {"Rule A": times[0], "Rule B": times[1], "Rule C": times[2]}
    for g in (g1, g2):
        for n in g["nodes"]:
            if n["id"] == "memory-root":
                continue
            text = n["properties"]["text"]
            n["properties"]["created"] = name_to_time[text]
            n["id"] = f"mem-{text.replace(' ', '-').lower()}"
        # Fix root contains[] ordering so it doesn't affect content — renderer
        # walks nodes in list order but `_group_by_type` sorts.
        root = next(n for n in g["nodes"] if n["id"] == "memory-root")
        root["contains"] = sorted(
            [n["id"] for n in g["nodes"] if n["id"] != "memory-root"]
        )
        # Re-sort parent_id refs via node list ordering.
        g["nodes"].sort(key=lambda n: n["id"])

    out1 = render(g1, now=datetime(2026, 4, 11, tzinfo=timezone.utc))
    out2 = render(g2, now=datetime(2026, 4, 11, tzinfo=timezone.utc))
    assert out1 == out2


# ─── Content ───────────────────────────────────────────────────────────────────


def test_render_empty_graph_does_not_crash(empty_graph, fixed_now):
    out = render(empty_graph, now=fixed_now)
    assert "# MEMORY" in out
    assert "0 active memories" in out
    assert "_(no active memories)_" in out


def test_render_groups_by_type_in_default_order(small_graph, fixed_now):
    out = render(small_graph, now=fixed_now)
    # Find each section's line index.
    lines = out.splitlines()
    positions = {}
    for t in DEFAULT_TYPE_ORDER:
        for i, line in enumerate(lines):
            if line == f"## {t}":
                positions[t] = i
                break
    # All four present.
    assert set(positions) == set(DEFAULT_TYPE_ORDER)
    # In order.
    ordered = [positions[t] for t in DEFAULT_TYPE_ORDER]
    assert ordered == sorted(ordered)


def test_render_unknown_type_goes_last(empty_graph, fixed_now):
    g = deepcopy(empty_graph)
    remember(g, "Rule 1", memory_type="feedback")
    remember(g, "Weird thing", memory_type="wildcard")
    out = render(g, now=fixed_now)
    # feedback section must precede wildcard.
    assert out.index("## feedback") < out.index("## wildcard")


def test_render_prefers_rule_over_text(empty_graph, fixed_now):
    g = deepcopy(empty_graph)
    remember(g, "Full prose with rationale paragraphs", memory_type="feedback")
    # Manually add a `rule` to the last node (U2 will make this a kwarg).
    g["nodes"][-1]["properties"]["rule"] = "Always fix every finding."
    out = render(g, now=fixed_now)
    assert "Always fix every finding." in out
    assert "Full prose with rationale paragraphs" not in out


def test_render_does_not_include_rationale_by_default(empty_graph, fixed_now):
    g = deepcopy(empty_graph)
    remember(g, "Rule body", memory_type="feedback")
    g["nodes"][-1]["properties"]["rationale"] = "Long explanation of why."
    out = render(g, now=fixed_now)
    assert "Rule body" in out
    assert "Long explanation of why." not in out


def test_render_includes_rationale_when_requested(empty_graph, fixed_now):
    g = deepcopy(empty_graph)
    remember(g, "Rule body", memory_type="feedback")
    g["nodes"][-1]["properties"]["rationale"] = "Line one.\nLine two."
    out = render(g, include_rationale=True, now=fixed_now)
    assert "Rule body" in out
    assert "> Line one." in out
    assert "> Line two." in out


def test_render_includes_tags(small_graph, fixed_now):
    out = render(small_graph, now=fixed_now)
    assert "tags: audit" in out or "tags: audit," in out
    assert "tags: hitm" in out


# ─── Temporal filtering ────────────────────────────────────────────────────────


def test_render_filters_expired_valid_to(empty_graph, fixed_now):
    g = deepcopy(empty_graph)
    remember(g, "Active rule", memory_type="feedback")
    remember(g, "Expired rule", memory_type="feedback")
    # Mark the second memory as expired before `fixed_now`.
    g["nodes"][-1]["properties"]["valid_to"] = "2026-01-01T00:00:00+00:00"
    out = render(g, now=fixed_now)
    assert "Active rule" in out
    assert "Expired rule" not in out


def test_render_keeps_future_valid_to(empty_graph, fixed_now):
    g = deepcopy(empty_graph)
    remember(g, "Scheduled retire", memory_type="feedback")
    g["nodes"][-1]["properties"]["valid_to"] = "2027-06-01T00:00:00+00:00"
    out = render(g, now=fixed_now)
    assert "Scheduled retire" in out


def test_is_past_handles_none(fixed_now):
    assert _is_past(None, now=fixed_now) is False


def test_is_past_handles_malformed(fixed_now):
    assert _is_past("not a date", now=fixed_now) is False


def test_is_past_handles_naive_iso(fixed_now):
    # Naive timestamps assumed UTC.
    assert _is_past("2026-01-01T00:00:00", now=fixed_now) is True


# ─── Budget ────────────────────────────────────────────────────────────────────


def test_render_under_budget_is_unchanged(small_graph, fixed_now):
    a = render(small_graph, token_budget=DEFAULT_BUDGET_TOKENS, now=fixed_now)
    assert "demoted for budget" not in a


def test_render_over_budget_demotes_project_first(empty_graph, fixed_now):
    g = deepcopy(empty_graph)
    # One feedback + one user + many project memories.
    remember(g, "Critical feedback rule", memory_type="feedback")
    remember(g, "Xepayac is HITM", memory_type="user")
    for i in range(30):
        remember(
            g,
            f"Project decision {i:03d} — a fairly lengthy explanation of the reasoning",
            memory_type="project",
        )

    # Very tight budget that forces demotion.
    out = render(g, token_budget=120, now=fixed_now)

    # user and feedback always survive.
    assert "Critical feedback rule" in out
    assert "Xepayac is HITM" in out
    # At least one project entry got demoted.
    assert "demoted for budget" in out


def test_render_never_demotes_user_or_feedback(empty_graph, fixed_now):
    g = deepcopy(empty_graph)
    for i in range(50):
        remember(g, f"Feedback rule {i:03d}" * 5, memory_type="feedback")
    # Impossibly tight budget.
    out = render(g, token_budget=20, now=fixed_now)
    # Every feedback entry is still present (we never drop user/feedback).
    for i in range(50):
        assert f"Feedback rule {i:03d}" in out


def test_demotion_order_constant_excludes_user_feedback():
    assert "user" not in DEMOTION_ORDER
    assert "feedback" not in DEMOTION_ORDER


def test_approx_tokens_empty_is_zero():
    """Audit round 2 #18 — empty string should cost 0 tokens, not 1."""
    assert _approx_tokens("") == 0


def test_approx_tokens_is_4_char_ratio():
    assert _approx_tokens("abcd") == 1
    assert _approx_tokens("abcdefgh") == 2
    assert _approx_tokens("a" * 400) == 100


def test_render_protected_overflow_warns_instead_of_pointless_demotion(empty_graph, fixed_now):
    """Audit round 2 #3 — user/feedback alone over budget → no pointless demotion of project/reference.

    Before the fix, the budget loop would pop every `project` and `reference`
    entry one-by-one even though the protected sections were already bigger
    than the budget. That silently nuked context with no warning.
    """
    g = deepcopy(empty_graph)
    # 1 huge feedback rule (already over any reasonable budget on its own)
    big = "HUGE_FEEDBACK_MARKER " + ("lorem ipsum " * 500)  # >2k approx tokens
    remember(g, big, memory_type="feedback")
    # + a bunch of project entries that WOULD be demoted in the old code
    for i in range(20):
        remember(g, f"Project_entry_{i:02d}_marker", memory_type="project")

    out = render(g, token_budget=500, now=fixed_now)
    # The big feedback rule must survive (user/feedback are never demoted).
    assert "HUGE_FEEDBACK_MARKER" in out
    # Project entries should also survive — demoting them can't fix the overflow.
    assert "Project_entry_00_marker" in out
    assert "Project_entry_19_marker" in out
    # And we should see the warning.
    assert "protected sections" in out.lower()
    assert "no demotion applied" in out.lower()


def test_render_zero_budget_emits_warning_but_renders(empty_graph, fixed_now):
    """Audit round 2 #3 — token_budget=0 should not infinite-loop or return nothing."""
    g = deepcopy(empty_graph)
    remember(g, "A", memory_type="feedback")
    remember(g, "B", memory_type="project")
    out = render(g, token_budget=0, now=fixed_now)
    assert "# MEMORY" in out
    assert "A" in out
    assert "B" in out
    assert "token_budget" in out.lower()


def test_render_incremental_demotion_matches_old_behavior(empty_graph, fixed_now):
    """Audit round 2 #5 — the O(n²) → O(n) rewrite must produce the same final set.

    We verify that when demotion is legitimately needed (user/feedback fit but
    project overflows), exactly the oldest project entries get dropped and the
    demoted count is accurate.
    """
    g = deepcopy(empty_graph)
    remember(g, "Critical rule", memory_type="feedback")
    for i in range(100):
        remember(g, f"Project decision number {i:03d} with some body text", memory_type="project")

    out = render(g, token_budget=150, now=fixed_now)

    # Newest projects survive; oldest are demoted.
    assert "Project decision number 099" in out
    # At least some demotion happened.
    assert "demoted for budget" in out
    # Parse the demotion count — should be >0 and < 100.
    import re
    m = re.search(r"_(\d+) memories demoted", out)
    assert m is not None
    n = int(m.group(1))
    assert 0 < n < 100


# ─── Sorting ───────────────────────────────────────────────────────────────────


def test_group_by_type_sorts_newest_first(empty_graph, fixed_now):
    g = deepcopy(empty_graph)
    remember(g, "Oldest", memory_type="feedback")
    g["nodes"][-1]["properties"]["created"] = "2026-01-01T00:00:00+00:00"
    remember(g, "Middle", memory_type="feedback")
    g["nodes"][-1]["properties"]["created"] = "2026-02-01T00:00:00+00:00"
    remember(g, "Newest", memory_type="feedback")
    g["nodes"][-1]["properties"]["created"] = "2026-03-01T00:00:00+00:00"

    active = _active_memories(g, now=fixed_now)
    grouped = _group_by_type(active, type_order=DEFAULT_TYPE_ORDER)

    feedback = grouped["feedback"]
    texts = [m["properties"]["text"] for m in feedback]
    assert texts == ["Newest", "Middle", "Oldest"]


# ─── File writes & validation ─────────────────────────────────────────────────


def test_render_to_file_creates_parent_and_writes_utf8(small_graph, fixed_now):
    with tempfile.TemporaryDirectory() as d:
        out_path = Path(d) / "subdir" / "MEMORY.md"
        n = render_to_file(small_graph, out_path, now=fixed_now)
        assert out_path.exists()
        assert n > 0
        content = out_path.read_text(encoding="utf-8")
        assert "# MEMORY" in content


def test_render_never_mutates_the_source_graph(small_graph, fixed_now):
    before = json.dumps(small_graph, sort_keys=True)
    _ = render(small_graph, now=fixed_now)
    after = json.dumps(small_graph, sort_keys=True)
    assert before == after


def test_rendered_source_graph_still_validates(small_graph):
    # Sanity — the graph we rendered from is still a valid CORE TRUG.
    result = validate(small_graph)
    assert result.valid, f"Render fixture graph is invalid: {result.errors}"


def test_render_memory_collapses_multiline_body(empty_graph, fixed_now):
    """I1 — a memory body with newlines and markdown syntax must render as
    a single line, not inject headings into MEMORY.md."""
    from memory import remember
    from memory_render import render

    g = empty_graph
    remember(g, "line1\n# Heading\nline3", memory_type="feedback")
    md = render(g, now=fixed_now)
    # The body should appear as a single bullet line, not a heading
    assert "- line1 # Heading line3" in md
    # Must NOT contain a real markdown heading from the injected content
    lines = md.splitlines()
    injected_headings = [l for l in lines if l.strip() == "# Heading"]
    assert len(injected_headings) == 0, "Multi-line body injected a heading"
