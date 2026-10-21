"""Vocabulary counting rules on small graphs independent of the live vocabulary."""

# <trl>
# AGENT SHALL VALIDATE MODULE paper_vocab_counts.
# </trl>
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from tools import paper_vocab_counts as counts


# <trl>
# FUNCTION fixture_language SHALL PRODUCE RECORD language THEN RETURN RECORD language.
# </trl>
# ---
# FUNCTION fixture_language SHALL PRODUCE RECORD language THEN RETURN RECORD language.
def fixture_language() -> dict[str, Any]:
    categories = ["verb", "noun", "article", "level_prefix"]
    nodes: list[dict[str, Any]] = [
        {
            "id": "root",
            "parent_id": None,
            "contains": categories,
            "properties": {"word_count": 999},
        }
    ]
    nodes += [
        {
            "id": part,
            "parent_id": "root",
            "properties": {"speech": part, "count": 999},
        }
        for part in categories
    ]
    for i, (speech, source, group) in enumerate(
        [
            ("noun", "computation", ""),
            ("noun", "law", ""),
            ("noun", "law", ""),
            ("noun", "law", ""),
            ("verb", "computation", "transform"),
            ("verb", "law", "move"),
            ("article", "", ""),
            ("level_prefix", "shared", ""),
        ]
    ):
        nodes.append(
            {
                "id": f"word-{i}",
                "parent_id": speech,
                "properties": {
                    # Even an empty word value counts: membership is by key.
                    "word": str(i) if i else "",
                    "speech": speech,
                    "source": source,
                    "subcategory": group,
                },
            }
        )
    return {"version": "fixture-version", "nodes": nodes}


# <trl>
# AGENT SHALL VALIDATE DATA word_counts_and_category_order.
# </trl>
# ---
# AGENT SHALL VALIDATE DATA word_counts_and_category_order.
def test_counts_use_word_properties_and_root_order() -> None:
    macros = counts.vocabulary_macros(fixture_language())
    assert macros["VocabTotal"] == "8"
    assert macros["VocabParts"] == "4"
    assert macros["VocabVersion"] == "fixture-version"
    assert macros["VocabNouns"] == "4"
    assert macros["VocabVerbs"] == "2"
    assert macros["VocabVerbsTransform"] == "1"
    assert macros["VocabVerbsMove"] == "1"
    assert macros["VocabVerbsResolve"] == "0"
    keys = list(macros)
    assert keys.index("VocabVerbs") < keys.index("VocabNouns")
    assert keys.index("VocabNouns") < keys.index("VocabArticles")


# <trl>
# AGENT SHALL VALIDATE DATA shared_sources_empty_cells_and_rounding.
# </trl>
# ---
# AGENT SHALL VALIDATE DATA shared_sources_empty_cells_and_rounding.
def test_shared_empty_source_zero_cells_and_half_up_rounding() -> None:
    graph = fixture_language()
    macros = counts.vocabulary_macros(graph)
    assert macros["VocabShared"] == "2"
    assert macros["VocabArticlesShared"] == "1"
    assert macros["VocabNounsShared"] == "---"
    assert macros["VocabLevelPrefixesComputation"] == "---"
    assert macros["VocabLawPct"] == "50"
    # One of eight is exactly 12.5%, which must round up, not to even.
    graph["nodes"][6]["properties"]["source"] = "shared"
    graph["nodes"][9]["properties"]["source"] = "law"
    assert counts.vocabulary_macros(graph)["VocabComputationPct"] == "13"


# <trl>
# AGENT SHALL VALIDATE DATA empty_vocabulary_error.
# </trl>
# ---
# AGENT SHALL VALIDATE DATA empty_vocabulary_error.
def test_empty_vocabulary_is_rejected() -> None:
    graph = fixture_language()
    graph["nodes"] = graph["nodes"][:5]
    with pytest.raises(ValueError, match="no words"):
        counts.vocabulary_macros(graph)


# <trl>
# AGENT SHALL VALIDATE DATA repeated_generation_bytes_and_messages.
# </trl>
# ---
# AGENT SHALL VALIDATE DATA repeated_generation_bytes_and_messages.
def test_generation_is_deterministic_on_fixture(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    source = tmp_path / "TRUGS_LANGUAGE/language.trug.json"
    source.parent.mkdir()
    source.write_text(json.dumps(fixture_language()))
    monkeypatch.setattr(counts, "ROOT", tmp_path)
    counts.main()
    output = tmp_path / "PAPER/generated/vocab_counts.tex"
    first = output.read_bytes()
    counts.main()
    assert output.read_bytes() == first
    assert b"\\newcommand{\\VocabTotal}{8}" in first
    assert b"\\newcommand{\\VocabNounsShared}{---}" in first
    assert capsys.readouterr().out.count("Wrote PAPER/generated/vocab_counts.tex") == 2
