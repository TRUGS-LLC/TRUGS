"""Tests for trugs-memory-import — bulk import flat markdown into a memory TRUG."""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from memory import load_graph
from memory_import import (
    FILENAME_TYPE_PREFIXES,
    ImportReport,
    ParsedFile,
    derive_memory_type,
    import_flat_directory,
    parse_markdown_with_frontmatter,
)
from validate import validate


# ─── Frontmatter parser ────────────────────────────────────────────────────────


def test_parse_with_full_frontmatter():
    content = "---\nname: Test name\ndescription: Short desc\ntype: feedback\n---\nBody paragraph."
    parsed = parse_markdown_with_frontmatter(content)
    assert parsed.name == "Test name"
    assert parsed.description == "Short desc"
    assert parsed.type == "feedback"
    assert parsed.body == "Body paragraph."


def test_parse_without_frontmatter():
    content = "Just a body with no frontmatter."
    parsed = parse_markdown_with_frontmatter(content)
    assert parsed.frontmatter == {}
    assert parsed.body == "Just a body with no frontmatter."


def test_parse_empty_content():
    parsed = parse_markdown_with_frontmatter("")
    assert parsed.frontmatter == {}
    assert parsed.body == ""


def test_parse_unclosed_frontmatter_treated_as_body():
    content = "---\nname: Unclosed\nno trailing delimiter"
    parsed = parse_markdown_with_frontmatter(content)
    assert parsed.frontmatter == {}
    # Body preserves original content (stripped).
    assert "Unclosed" in parsed.body


def test_parse_value_with_colon():
    content = "---\nname: Format: subtitle\ndescription: A: B: C\ntype: user\n---\nBody"
    parsed = parse_markdown_with_frontmatter(content)
    assert parsed.name == "Format: subtitle"
    assert parsed.description == "A: B: C"


def test_parse_ignores_lines_without_colon():
    content = "---\nname: Foo\nthis line has no colon\ntype: feedback\n---\nBody"
    parsed = parse_markdown_with_frontmatter(content)
    assert parsed.name == "Foo"
    assert parsed.type == "feedback"
    assert "no_colon" not in parsed.frontmatter


def test_parse_multiline_body():
    content = "---\nname: X\n---\nLine 1\n\nLine 2\n\nLine 3"
    parsed = parse_markdown_with_frontmatter(content)
    assert "Line 1" in parsed.body
    assert "Line 2" in parsed.body
    assert "Line 3" in parsed.body


# ─── Type derivation ──────────────────────────────────────────────────────────


def test_derive_type_from_frontmatter_wins():
    parsed = ParsedFile(frontmatter={"type": "feedback"}, body="")
    assert derive_memory_type(parsed, "user_xepayac.md", type_from_filename=True) == "feedback"


def test_derive_type_from_filename_when_no_frontmatter():
    parsed = ParsedFile(frontmatter={}, body="body")
    assert derive_memory_type(parsed, "user_xepayac.md", type_from_filename=True) == "user"
    assert derive_memory_type(parsed, "feedback_test.md", type_from_filename=True) == "feedback"
    assert derive_memory_type(parsed, "project_wp.md", type_from_filename=True) == "project"
    assert derive_memory_type(parsed, "reference_foo.md", type_from_filename=True) == "reference"


def test_derive_type_default_fact():
    parsed = ParsedFile(frontmatter={}, body="")
    assert derive_memory_type(parsed, "random_name.md", type_from_filename=True) == "fact"


def test_derive_type_filename_disabled():
    parsed = ParsedFile(frontmatter={}, body="")
    assert derive_memory_type(parsed, "user_xepayac.md", type_from_filename=False) == "fact"


def test_derive_type_lowercases_frontmatter():
    parsed = ParsedFile(frontmatter={"type": "FEEDBACK"}, body="")
    assert derive_memory_type(parsed, "x.md", type_from_filename=False) == "feedback"


def test_filename_prefixes_cover_all_canonical_types():
    prefixes = {p[1] for p in FILENAME_TYPE_PREFIXES}
    assert {"user", "feedback", "project", "reference"} <= prefixes


# ─── Directory walk & import ─────────────────────────────────────────────────


@pytest.fixture
def sample_dir():
    """Create a temp directory with a handful of realistic memory files."""
    with tempfile.TemporaryDirectory() as d:
        base = Path(d)

        (base / "user_xepayac.md").write_text(
            "---\nname: Xepayac is the HITM\ndescription: The human in the loop\ntype: user\n---\n"
            "Role: HITM on all merges. Claude writes code; Xepayac approves.",
            encoding="utf-8",
        )

        (base / "feedback_audit_rule.md").write_text(
            "---\nname: Fix every finding\ndescription: All severities get fixed in the same round\ntype: feedback\n---\n"
            "In an audit, always fix every finding regardless of severity.\n\n"
            "**Why:** Deferred findings accumulate.",
            encoding="utf-8",
        )

        (base / "project_wp03.md").write_text(
            "---\nname: WP-03 shipped\ndescription: Inner loop landed in PR #1459\ntype: project\n---\n"
            "TRUGS_OS WP-03 inner loop shipped 2026-04-09.",
            encoding="utf-8",
        )

        (base / "reference_trl.md").write_text(
            "---\nname: TRL vocabulary\ndescription: 190-word formalized English\ntype: reference\n---\n"
            "See TRUGS_PROTOCOL/TRUGS_LANGUAGE/SPEC_vocabulary.md",
            encoding="utf-8",
        )

        (base / "plain_no_frontmatter.md").write_text(
            "Just a raw note with no frontmatter at all.",
            encoding="utf-8",
        )

        yield base


def test_import_scans_all_md_files(sample_dir):
    with tempfile.TemporaryDirectory() as out_dir:
        out = Path(out_dir) / "memory.trug.json"
        report = import_flat_directory(sample_dir, out)
        assert report.files_scanned == 5
        assert report.imported == 5
        assert report.skipped_duplicate == 0
        assert report.skipped_malformed == 0


def test_import_produces_valid_graph(sample_dir):
    with tempfile.TemporaryDirectory() as out_dir:
        out = Path(out_dir) / "memory.trug.json"
        import_flat_directory(sample_dir, out)
        graph = load_graph(out)
        result = validate(graph)
        assert result.valid, f"Imported graph invalid: {[e.message for e in result.errors]}"


def test_import_maps_frontmatter_to_rule_and_rationale(sample_dir):
    with tempfile.TemporaryDirectory() as out_dir:
        out = Path(out_dir) / "memory.trug.json"
        import_flat_directory(sample_dir, out)
        graph = load_graph(out)
        # Find the user memory.
        user_nodes = [
            n for n in graph["nodes"]
            if n.get("properties", {}).get("memory_type") == "user"
        ]
        assert len(user_nodes) == 1
        props = user_nodes[0]["properties"]
        assert props["rule"] == "Xepayac is the HITM"
        assert props["rationale"] == "The human in the loop"
        assert "HITM on all merges" in props["text"]


def test_import_preserves_source_path(sample_dir):
    with tempfile.TemporaryDirectory() as out_dir:
        out = Path(out_dir) / "memory.trug.json"
        import_flat_directory(sample_dir, out)
        graph = load_graph(out)
        sources = {
            n.get("properties", {}).get("source")
            for n in graph["nodes"]
            if n.get("id") != "memory-root"
        }
        assert "user_xepayac.md" in sources
        assert "feedback_audit_rule.md" in sources


def test_import_source_prefix(sample_dir):
    with tempfile.TemporaryDirectory() as out_dir:
        out = Path(out_dir) / "memory.trug.json"
        import_flat_directory(sample_dir, out, source_prefix="legacy:")
        graph = load_graph(out)
        sources = [
            n.get("properties", {}).get("source")
            for n in graph["nodes"]
            if n.get("id") != "memory-root"
        ]
        assert any(s and s.startswith("legacy:") for s in sources)


def test_import_assigns_tags(sample_dir):
    with tempfile.TemporaryDirectory() as out_dir:
        out = Path(out_dir) / "memory.trug.json"
        import_flat_directory(sample_dir, out, tags=["migrated-2026-04"])
        graph = load_graph(out)
        for n in graph["nodes"]:
            if n.get("id") == "memory-root":
                continue
            assert "migrated-2026-04" in n["properties"]["tags"]


def test_import_plain_file_without_frontmatter_uses_filename_type(sample_dir):
    with tempfile.TemporaryDirectory() as out_dir:
        out = Path(out_dir) / "memory.trug.json"
        import_flat_directory(sample_dir, out, type_from_filename=True)
        graph = load_graph(out)
        plain = [
            n for n in graph["nodes"]
            if n.get("properties", {}).get("source") == "plain_no_frontmatter.md"
        ]
        assert len(plain) == 1
        # No filename prefix match → "fact".
        assert plain[0]["properties"]["memory_type"] == "fact"
        assert "rule" not in plain[0]["properties"]
        assert "rationale" not in plain[0]["properties"]


# ─── Idempotency ──────────────────────────────────────────────────────────────


def test_import_is_idempotent_on_rerun(sample_dir):
    with tempfile.TemporaryDirectory() as out_dir:
        out = Path(out_dir) / "memory.trug.json"
        first = import_flat_directory(sample_dir, out)
        assert first.imported == 5

        second = import_flat_directory(sample_dir, out)
        assert second.imported == 0
        assert second.skipped_duplicate == 5
        assert second.files_scanned == 5


def test_import_picks_up_new_files_on_rerun(sample_dir):
    with tempfile.TemporaryDirectory() as out_dir:
        out = Path(out_dir) / "memory.trug.json"
        first = import_flat_directory(sample_dir, out)
        assert first.imported == 5

        # Add a new file and re-run.
        (sample_dir / "user_new.md").write_text(
            "---\nname: New user fact\ndescription: Added after initial import\ntype: user\n---\nBody",
            encoding="utf-8",
        )
        second = import_flat_directory(sample_dir, out)
        assert second.imported == 1
        assert second.skipped_duplicate == 5
        assert second.files_scanned == 6


# ─── Dry run ──────────────────────────────────────────────────────────────────


def test_dry_run_does_not_write_file(sample_dir):
    with tempfile.TemporaryDirectory() as out_dir:
        out = Path(out_dir) / "memory.trug.json"
        report = import_flat_directory(sample_dir, out, dry_run=True)
        assert report.imported == 5
        assert not out.exists()


def test_dry_run_against_existing_graph_does_not_mutate(sample_dir):
    with tempfile.TemporaryDirectory() as out_dir:
        out = Path(out_dir) / "memory.trug.json"
        import_flat_directory(sample_dir, out)
        before = out.read_bytes()

        # Add a file, dry run.
        (sample_dir / "feedback_new.md").write_text(
            "---\nname: New rule\ndescription: x\ntype: feedback\n---\nBody",
            encoding="utf-8",
        )
        report = import_flat_directory(sample_dir, out, dry_run=True)
        assert report.imported == 1
        assert report.skipped_duplicate == 5

        after = out.read_bytes()
        assert before == after


# ─── Error handling ───────────────────────────────────────────────────────────


def test_import_raises_on_missing_src_dir():
    with pytest.raises(FileNotFoundError):
        import_flat_directory(Path("/nonexistent/totally/fake"), Path("/tmp/x.trug.json"))


def test_import_recursive_subdirs(tmp_path):
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "nested.md").write_text(
        "---\nname: Nested\ndescription: d\ntype: feedback\n---\nNested body content",
        encoding="utf-8",
    )
    (tmp_path / "top.md").write_text(
        "---\nname: Top\ndescription: d\ntype: user\n---\nTop-level body content",
        encoding="utf-8",
    )
    with tempfile.TemporaryDirectory() as out_dir:
        out = Path(out_dir) / "memory.trug.json"
        report = import_flat_directory(tmp_path, out)
        assert report.imported == 2


def test_import_skips_empty_files(tmp_path):
    (tmp_path / "empty.md").write_text("", encoding="utf-8")
    (tmp_path / "real.md").write_text("Content", encoding="utf-8")
    with tempfile.TemporaryDirectory() as out_dir:
        out = Path(out_dir) / "memory.trug.json"
        report = import_flat_directory(tmp_path, out)
        assert report.imported == 1
        assert report.skipped_malformed == 1


# ─── Report ───────────────────────────────────────────────────────────────────


def test_import_report_new_ids_match_count(sample_dir):
    with tempfile.TemporaryDirectory() as out_dir:
        out = Path(out_dir) / "memory.trug.json"
        report = import_flat_directory(sample_dir, out)
        assert len(report.new_ids) == report.imported
        # All IDs start with mem- (actual remember() format).
        for mid in report.new_ids:
            assert mid.startswith("mem-")
