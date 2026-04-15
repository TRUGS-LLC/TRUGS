"""Tests for the TRL compiler v0.1.

v0.1 scope: minimum valid sentence (SUBJECT + VERB).
Covers tokenizer, classifier, parser, compile, decompile,
round-trip guarantee, and validator. Grammar expansion to
articles / adjectives / modals / objects / conjunctions is
tracked in subsequent PRs per TRUGS-DEVELOPMENT#1539.
"""

from __future__ import annotations

import json
from pathlib import Path

from tools import trl


# ─── Tokenizer ───────────────────────────────────────────────────────

def test_tokenize_simple_sentence() -> None:
    tokens = trl.tokenize("PARTY system VALIDATE.")
    kinds = [t.kind for t in tokens]
    values = [t.value for t in tokens]
    assert kinds == ["WORD", "IDENTIFIER", "WORD", "PUNCT", "EOF"]
    assert values == ["PARTY", "system", "VALIDATE", ".", ""]


def test_tokenize_strips_sugar() -> None:
    # Sugar tokens start with apostrophe and are discarded before parsing
    tokens = trl.tokenize("PARTY system 'please VALIDATE 'of 'the.")
    values = [t.value for t in tokens if t.kind != "EOF"]
    assert values == ["PARTY", "system", "VALIDATE", "."]


def test_tokenize_multiple_sentences() -> None:
    tokens = trl.tokenize("PARTY a VALIDATE. PARTY b VALIDATE.")
    words = [t.value for t in tokens if t.kind == "WORD"]
    assert words == ["PARTY", "VALIDATE", "PARTY", "VALIDATE"]


def test_tokenize_rejects_unexpected_char() -> None:
    try:
        trl.tokenize("PARTY @system VALIDATE.")
    except trl.TRLSyntaxError:
        return
    assert False, "expected TRLSyntaxError"


# ─── Classifier ──────────────────────────────────────────────────────

def test_classify_known_noun() -> None:
    lang = trl.load_language()
    entry = trl.classify("PARTY", lang)
    assert entry["speech"] == "noun"
    assert entry["subcategory"] == "actors"  # spec section header preserves plural


def test_classify_known_verb() -> None:
    lang = trl.load_language()
    entry = trl.classify("VALIDATE", lang)
    assert entry["speech"] == "verb"


def test_classify_modals_are_in_modal_subcategories() -> None:
    # Per SPEC_vocabulary.md, modals are in the Verbs section under
    # obligate / permit / prohibit subcategories (not a separate "modal"
    # speech). SPEC_grammar.md §1 BNF treats them syntactically as modals.
    lang = trl.load_language()
    expected = {"SHALL": "obligate", "MAY": "permit", "SHALL_NOT": "prohibit"}
    for word, sub in expected.items():
        entry = trl.classify(word, lang)
        assert entry["speech"] == "verb"
        assert entry["subcategory"] == sub


def test_classify_unknown_word_raises() -> None:
    lang = trl.load_language()
    try:
        trl.classify("FAKEWORD", lang)
    except trl.TRLVocabularyError:
        return
    assert False, "expected TRLVocabularyError"


# ─── Parser ──────────────────────────────────────────────────────────

def test_parse_minimum_sentence() -> None:
    sentences = trl.parse("PARTY system VALIDATE.")
    assert len(sentences) == 1
    s = sentences[0]
    assert s.subject.noun == "PARTY"
    assert s.subject.identifier == "system"
    assert s.verb_phrase.verb == "VALIDATE"


def test_parse_rejects_verb_as_subject() -> None:
    try:
        trl.parse("FILTER system VALIDATE.")
    except trl.TRLGrammarError:
        return
    assert False, "FILTER is a verb, should not parse as subject"


def test_parse_rejects_missing_period() -> None:
    try:
        trl.parse("PARTY system VALIDATE")
    except trl.TRLSyntaxError:
        return
    assert False, "expected TRLSyntaxError for missing period"


# ─── Compile ─────────────────────────────────────────────────────────

def test_compile_emits_subject_and_op_nodes() -> None:
    g = trl.compile("PARTY system VALIDATE.")
    assert len(g["nodes"]) == 2
    assert g["nodes"][0] == {"id": "system", "type": "PARTY"}
    op = g["nodes"][1]
    assert op["type"] == "TRANSFORM"
    assert op["properties"]["operation"] == "VALIDATE"
    assert op["properties"]["verb_subcategory"] == "obligate"


def test_compile_emits_executes_edge_for_unmodaled() -> None:
    g = trl.compile("PARTY system VALIDATE.")
    assert len(g["edges"]) == 1
    e = g["edges"][0]
    assert e["from_id"] == "system"
    assert e["to_id"] == "op-1"
    assert e["relation"] == "EXECUTES"


def test_compile_reuses_existing_subject_node() -> None:
    # Two sentences, same subject. The subject node appears once, two ops, two edges.
    g = trl.compile("PARTY system VALIDATE. PARTY system FILTER.")
    party_nodes = [n for n in g["nodes"] if n["type"] == "PARTY"]
    assert len(party_nodes) == 1
    op_nodes = [n for n in g["nodes"] if n["type"] == "TRANSFORM"]
    assert len(op_nodes) == 2
    assert len(g["edges"]) == 2


def test_compile_requires_identifier() -> None:
    try:
        trl.compile("PARTY VALIDATE.")  # no identifier
    except trl.TRLGrammarError:
        return
    assert False, "expected TRLGrammarError for bare noun subject"


# ─── Decompile ───────────────────────────────────────────────────────

def test_decompile_minimum_graph() -> None:
    g = {
        "nodes": [
            {"id": "system", "type": "PARTY"},
            {"id": "op-1", "type": "TRANSFORM",
             "properties": {"operation": "VALIDATE", "verb_subcategory": "obligate"}},
        ],
        "edges": [{"from_id": "system", "to_id": "op-1", "relation": "EXECUTES"}],
    }
    assert trl.decompile(g) == "PARTY system VALIDATE."


# ─── Round-trip (the primary acceptance criterion) ──────────────────

ROUND_TRIP_FIXTURES = [
    "PARTY system VALIDATE.",
    "PARTY api FILTER.",
    "PARTY user AUTHENTICATE.",
    "AGENT worker FILTER.",
    "SERVICE gateway VALIDATE.",
]


def test_round_trip_trl_to_trug_to_trl() -> None:
    for sentence in ROUND_TRIP_FIXTURES:
        g1 = trl.compile(sentence)
        sentence_out = trl.decompile(g1)
        g2 = trl.compile(sentence_out)
        assert g1 == g2, f"round-trip diverged for {sentence!r}: {g1} != {g2}"
        assert sentence_out == sentence, f"decompile diverged for {sentence!r}: {sentence_out!r}"


def test_round_trip_trug_to_trl_to_trug() -> None:
    for sentence in ROUND_TRIP_FIXTURES:
        g1 = trl.compile(sentence)
        s = trl.decompile(g1)
        g2 = trl.compile(s)
        assert g1 == g2


def test_round_trip_sugar_is_stripped() -> None:
    # Sugar doesn't survive the round-trip — canonical form is sugar-free
    original = "PARTY system 'please VALIDATE 'of 'all."
    g = trl.compile(original)
    decompiled = trl.decompile(g)
    assert decompiled == "PARTY system VALIDATE."  # sugar gone


# ─── Validate ────────────────────────────────────────────────────────

def test_validate_clean_graph() -> None:
    g = trl.compile("PARTY system VALIDATE.")
    assert trl.validate(g) == []


def test_validate_detects_bad_noun_type() -> None:
    g = {
        "nodes": [{"id": "x", "type": "NOT_A_NOUN"}],
        "edges": [],
    }
    errors = trl.validate(g)
    assert any("not a TRL noun" in e for e in errors)


def test_validate_detects_missing_relation() -> None:
    g = {
        "nodes": [
            {"id": "x", "type": "PARTY"},
            {"id": "op-1", "type": "TRANSFORM", "properties": {"operation": "VALIDATE"}},
        ],
        "edges": [{"from_id": "x", "to_id": "op-1"}],  # missing relation
    }
    errors = trl.validate(g)
    assert any("missing relation" in e for e in errors)
