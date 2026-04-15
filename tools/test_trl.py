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
    assert len(s.clauses) == 1
    c = s.clauses[0]
    assert c.subject.noun == "PARTY"
    assert c.subject.identifier == "system"
    assert c.verb_phrase.verb == "VALIDATE"


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


def test_anonymous_subject_now_allowed() -> None:
    """v0.1g allows anonymous subjects so WHEREAS preambles and NO PARTY clauses work."""
    g = trl.compile("PARTY VALIDATE.")
    party_nodes = [n for n in g["nodes"] if n["type"] == "PARTY"]
    assert len(party_nodes) == 1
    assert party_nodes[0]["id"] == "party-1"  # auto-generated


def test_compile_modal_on_edge() -> None:
    g = trl.compile("PARTY system SHALL VALIDATE.")
    assert g["edges"][0]["relation"] == "SHALL"


def test_compile_shall_not_on_edge() -> None:
    g = trl.compile("PARTY system SHALL_NOT WRITE.")
    assert g["edges"][0]["relation"] == "SHALL_NOT"


def test_compile_anonymous_object_gets_auto_id() -> None:
    g = trl.compile("PARTY system SHALL VALIDATE ALL PENDING RECORD.")
    record = next(n for n in g["nodes"] if n["type"] == "RECORD")
    assert record["id"] == "record-1"  # auto-generated for anonymous noun
    # Per-mention attributes live on the ACTS_ON edge, not on the node
    obj_edge = next(e for e in g["edges"]
                    if e["to_id"] == "record-1" and e.get("relation") == "ACTS_ON")
    shape = (obj_edge.get("properties") or {}).get("np_shape", {})
    assert shape.get("article") == "ALL"
    assert shape.get("state") == "PENDING"


def test_compile_spec_example_1_verbatim() -> None:
    """The very first example in SPEC_examples.md round-trips exactly."""
    g = trl.compile(SPEC_EXAMPLE_1)
    back = trl.decompile(g)
    assert back == SPEC_EXAMPLE_1
    g2 = trl.compile(back)
    assert g == g2


def test_compile_reuses_existing_identified_object() -> None:
    # PARTY server (identified) should reuse a pre-existing node
    g = trl.compile("PARTY a SHALL REQUEST PARTY server. PARTY b SHALL REQUEST PARTY server.")
    servers = [n for n in g["nodes"] if n["id"] == "server"]
    assert len(servers) == 1


# ─── v0.1c — Conjunctions ─────────────────────────────────────────────

def test_parse_conjunction_creates_two_clauses() -> None:
    s = trl.parse("PARTY a SHALL FILTER DATA THEN SORT DATA.")[0]
    assert len(s.clauses) == 2
    assert s.conjunctions == ["THEN"]
    # Second clause inherits subject (no explicit subject in AST)
    assert s.clauses[1].subject is None


def test_parse_conjunction_preserves_explicit_subject() -> None:
    s = trl.parse("PARTY server SHALL RESPOND OR PARTY client MAY RETRY.")[0]
    assert s.conjunctions == ["OR"]
    assert s.clauses[0].subject.identifier == "server"
    assert s.clauses[1].subject is not None
    assert s.clauses[1].subject.identifier == "client"


def test_compile_conjunction_edge() -> None:
    g = trl.compile("PARTY a SHALL FILTER DATA THEN SORT DATA.")
    conj_edges = [e for e in g["edges"] if e.get("relation") == "THEN"]
    assert len(conj_edges) == 1
    assert conj_edges[0]["from_id"] == "op-1"
    assert conj_edges[0]["to_id"] == "op-2"


def test_compile_three_way_then_chain() -> None:
    g = trl.compile("PARTY a SHALL FILTER DATA THEN SORT DATA THEN WRITE DATA.")
    then_edges = [e for e in g["edges"] if e.get("relation") == "THEN"]
    assert len(then_edges) == 2


def test_unless_with_anonymous_subject() -> None:
    src = "PARTY api SHALL FILTER RECORD UNLESS NO RECORD EXISTS."
    g = trl.compile(src)
    # The UNLESS clause's subject (record-2) is an anonymous NO RECORD.
    # The NO article lives on the subject edge from record-2 → its op.
    record_nodes = [n for n in g["nodes"] if n["type"] == "RECORD"]
    assert any(n["id"] == "record-2" for n in record_nodes)
    no_subj_edge = next(
        e for e in g["edges"]
        if e["from_id"] == "record-2" and e.get("relation") in {"EXECUTES"} | trl.MODALS
    )
    shape = (no_subj_edge.get("properties") or {}).get("np_shape", {})
    assert shape.get("article") == "NO"


def test_decompile_omits_inherited_subject() -> None:
    """Canonical form drops subject when it matches the prior clause."""
    src = "PARTY a SHALL FILTER DATA THEN SORT DATA."
    back = trl.decompile(trl.compile(src))
    # Second clause should NOT include "PARTY a"
    assert back == src
    assert " PARTY a SORT " not in back  # sanity: subject is omitted after THEN


# ─── v0.1d — Prepositions ─────────────────────────────────────────────

def test_parse_single_preposition() -> None:
    s = trl.parse("PARTY user SHALL AUTHENTICATE TO SERVICE gateway.")[0]
    c = s.clauses[0]
    assert c.object is None
    assert len(c.prep_phrases) == 1
    assert c.prep_phrases[0].preposition == "TO"
    assert c.prep_phrases[0].target.noun == "SERVICE"
    assert c.prep_phrases[0].target.identifier == "gateway"


def test_parse_object_then_preposition() -> None:
    s = trl.parse("PARTY system SHALL WRITE DATA TO ENDPOINT output.")[0]
    c = s.clauses[0]
    assert c.object.noun == "DATA"
    assert [pp.preposition for pp in c.prep_phrases] == ["TO"]


def test_parse_multiple_prepositions() -> None:
    s = trl.parse("PARTY system SHALL FILTER DATA FROM ENDPOINT input TO ENDPOINT output.")[0]
    c = s.clauses[0]
    assert [pp.preposition for pp in c.prep_phrases] == ["FROM", "TO"]


def test_compile_emits_preposition_edges() -> None:
    g = trl.compile("PARTY user SHALL AUTHENTICATE TO SERVICE gateway.")
    to_edges = [e for e in g["edges"] if e.get("relation") == "TO"]
    assert len(to_edges) == 1
    assert to_edges[0]["to_id"] == "gateway"


def test_compile_preserves_preposition_order() -> None:
    g = trl.compile("PARTY system SHALL FILTER DATA FROM ENDPOINT a TO ENDPOINT b.")
    prep_rels = [e["relation"] for e in g["edges"]
                 if e["from_id"].startswith("op-") and e.get("relation") in ("FROM", "TO")]
    assert prep_rels == ["FROM", "TO"]


def test_contains_preposition_roundtrip() -> None:
    src = "PARTY admin SHALL ADMINISTER RESOURCE CONTAINS NAMESPACE production."
    g = trl.compile(src)
    assert trl.decompile(g) == src


def test_preposition_with_conjunction_combination() -> None:
    src = "PARTY system SHALL FILTER DATA TO ENDPOINT output THEN VALIDATE RECORD."
    g = trl.compile(src)
    back = trl.decompile(g)
    assert back == src
    # Verify the TO edge is attached to op-1 (the FILTER op), not op-2
    to_edges = [e for e in g["edges"] if e.get("relation") == "TO"]
    assert len(to_edges) == 1
    assert to_edges[0]["from_id"] == "op-1"


# ─── v0.1e — Pronouns ─────────────────────────────────────────────────

def test_parse_pronoun_object() -> None:
    s = trl.parse("PARTY api SHALL FILTER RECORD THEN SORT RESULT.")[0]
    c2 = s.clauses[1]
    assert c2.object is not None
    assert c2.object.pronoun == "RESULT"
    assert c2.object.noun == ""


def test_compile_result_points_to_previous_op() -> None:
    g = trl.compile("PARTY api SHALL FILTER RECORD THEN SORT RESULT.")
    # op-2 (SORT) should ACTS_ON op-1 (FILTER), with pronoun=RESULT
    result_edges = [e for e in g["edges"]
                    if e.get("relation") == "ACTS_ON" and e["from_id"] == "op-2"]
    assert len(result_edges) == 1
    assert result_edges[0]["to_id"] == "op-1"
    assert result_edges[0]["properties"]["pronoun"] == "RESULT"


def test_compile_self_points_to_subject() -> None:
    g = trl.compile("PARTY admin SHALL ADMINISTER RESOURCE REFERENCES SELF.")
    refs = [e for e in g["edges"] if e.get("relation") == "REFERENCES"]
    assert len(refs) == 1
    assert refs[0]["to_id"] == "admin"
    assert refs[0]["properties"]["pronoun"] == "SELF"


def test_result_in_prep_target() -> None:
    src = "PARTY system SHALL FILTER DATA THEN WRITE RESULT TO ENDPOINT destination."
    g = trl.compile(src)
    assert trl.decompile(g) == src


def test_pronoun_without_antecedent_errors() -> None:
    # RESULT in the first clause has no prior op to reference
    try:
        trl.compile("PARTY system SHALL FILTER RESULT.")
    except trl.TRLGrammarError:
        return
    assert False, "expected TRLGrammarError — RESULT has no antecedent"


def test_pronoun_cannot_be_subject_in_v01e() -> None:
    # Subjects require identifiers; pronoun-as-subject is deferred.
    try:
        trl.compile("SELF SHALL VALIDATE.")
    except trl.TRLError:
        return
    assert False, "expected TRLError — subject pronoun not in v0.1e scope"


def test_spec_example_2_verbatim() -> None:
    """SPEC_examples.md §1 Example 2 round-trips."""
    g = trl.compile(SPEC_EXAMPLE_2)
    back = trl.decompile(g)
    assert back == SPEC_EXAMPLE_2
    assert trl.compile(back) == g


# ─── v0.1f — Adverbs + value literals ─────────────────────────────────

def test_tokenize_duration_literal() -> None:
    tokens = trl.tokenize("WITHIN 30s.")
    kinds = [t.kind for t in tokens if t.kind != "EOF"]
    assert kinds == ["WORD", "DURATION", "PUNCT"]
    assert tokens[1].value == "30s"


def test_tokenize_integer_literal() -> None:
    tokens = trl.tokenize("BOUNDED 3.")
    kinds = [t.kind for t in tokens if t.kind != "EOF"]
    assert kinds == ["WORD", "INTEGER", "PUNCT"]
    assert tokens[1].value == "3"


def test_parse_adverb_no_value() -> None:
    s = trl.parse("PARTY server SHALL RESPOND PROMPTLY.")[0]
    advs = s.clauses[0].verb_phrase.adverbs
    assert len(advs) == 1
    assert advs[0].adverb == "PROMPTLY"
    assert advs[0].value is None


def test_parse_adverb_with_duration() -> None:
    s = trl.parse("PARTY server SHALL RESPOND WITHIN 30s.")[0]
    advs = s.clauses[0].verb_phrase.adverbs
    assert advs[0].adverb == "WITHIN"
    assert advs[0].value == "30s"


def test_parse_adverb_with_integer() -> None:
    s = trl.parse("PARTY client MAY RETRY BOUNDED 3.")[0]
    advs = s.clauses[0].verb_phrase.adverbs
    assert advs[0].adverb == "BOUNDED"
    assert advs[0].value == "3"


def test_parse_multiple_adverbs() -> None:
    s = trl.parse("PARTY server SHALL RESPOND PROMPTLY WITHIN 30s.")[0]
    advs = s.clauses[0].verb_phrase.adverbs
    assert [(a.adverb, a.value) for a in advs] == [
        ("PROMPTLY", None),
        ("WITHIN", "30s"),
    ]


def test_compile_stores_adverbs_on_op() -> None:
    g = trl.compile("PARTY server SHALL RESPOND PROMPTLY WITHIN 30s.")
    op = next(n for n in g["nodes"] if n.get("type") == "TRANSFORM")
    assert op["properties"]["adverbs"] == [
        {"adverb": "PROMPTLY"},
        {"adverb": "WITHIN", "value": "30s"},
    ]


def test_spec_example_3_verbatim() -> None:
    """SPEC_examples.md §1 Example 3 round-trips — multi-sentence with
    adverbs, value literals, OR, THEN, and THE <noun> back-reference."""
    g = trl.compile(SPEC_EXAMPLE_3)
    back = trl.decompile(g)
    assert back == SPEC_EXAMPLE_3
    assert trl.compile(back) == g


# ─── v0.1g — DEFINE / WHEREAS / STRING literals ──────────────────────

def test_tokenize_string_literal() -> None:
    tokens = trl.tokenize('DEFINE "curator" AS PARTY.')
    kinds = [t.kind for t in tokens if t.kind != "EOF"]
    assert kinds == ["WORD", "STRING", "WORD", "WORD", "PUNCT"]
    assert tokens[1].value == "curator"


def test_tokenize_string_with_spaces() -> None:
    tokens = trl.tokenize('DEFINE "policy name" AS PARTY.')
    assert tokens[1].value == "policy name"


def test_parse_define() -> None:
    s = trl.parse('DEFINE "curator" AS PARTY.')[0]
    assert s.definition is not None
    assert s.definition.name == "curator"
    assert s.definition.noun_phrase.noun == "PARTY"


def test_parse_define_with_adjective() -> None:
    s = trl.parse('DEFINE "ledger" AS IMMUTABLE RECORD.')[0]
    d = s.definition
    assert d.name == "ledger"
    assert d.noun_phrase.noun == "RECORD"
    assert d.noun_phrase.adjectives == ["IMMUTABLE"]


def test_compile_define_emits_defined_term() -> None:
    g = trl.compile('DEFINE "curator" AS PARTY.')
    curator = next(n for n in g["nodes"] if n["id"] == "curator")
    assert curator["type"] == "PARTY"
    assert curator["properties"]["defined"] is True
    assert curator["properties"]["name"] == "curator"


def test_parse_whereas_preamble() -> None:
    s = trl.parse("WHEREAS PARTY system ADMINISTER ALL RESOURCE.")[0]
    assert s.preamble is True


def test_compile_whereas_marks_preamble_on_op() -> None:
    g = trl.compile("WHEREAS PARTY system ADMINISTER ALL RESOURCE.")
    op = next(n for n in g["nodes"] if n.get("type") == "TRANSFORM")
    assert op["properties"]["preamble"] is True


def test_spec_example_10_verbatim() -> None:
    """SPEC_examples.md §3 Example 10 — DEFINE + AND parallel."""
    g = trl.compile(SPEC_EXAMPLE_10)
    back = trl.decompile(g)
    assert back == SPEC_EXAMPLE_10
    assert trl.compile(back) == g


def test_spec_example_18_verbatim() -> None:
    """SPEC_examples.md §4 Example 18 — WHEREAS preambles + operative."""
    g = trl.compile(SPEC_EXAMPLE_18)
    back = trl.decompile(g)
    assert back == SPEC_EXAMPLE_18
    assert trl.compile(back) == g


# ─── v0.2 — AND-chained noun lists ────────────────────────────────────

def test_object_and_chain_two_items() -> None:
    g = trl.compile("PARTY analyst SHALL READ DATA AND RECORD.")
    acts_on = [e for e in g["edges"] if e.get("relation") == "ACTS_ON"]
    assert len(acts_on) == 2
    # Both should share the same chain_id
    cid = (acts_on[0].get("properties") or {}).get("chain_id")
    assert cid is not None
    assert (acts_on[1].get("properties") or {}).get("chain_id") == cid


def test_object_and_chain_three_items_with_prep() -> None:
    src = "PARTY system SHALL NEST MODULE auth AND MODULE data AND MODULE search TO NAMESPACE api-system."
    g = trl.compile(src)
    back = trl.decompile(g)
    assert back == src
    assert trl.compile(back) == g


def test_prep_noun_list_and_chain() -> None:
    src = "PARTY a SHALL SPLIT THE MESSAGE TO AGENT worker-a AND AGENT worker-b."
    g = trl.compile(src)
    back = trl.decompile(g)
    assert back == src
    to_edges = [e for e in g["edges"] if e.get("relation") == "TO"]
    assert len(to_edges) == 2


def test_clause_level_and_still_works() -> None:
    """Smarter peek must not break clause-level AND."""
    src = "PARTY system SHALL FILTER DATA AND PARTY system SHALL VALIDATE RECORD."
    g = trl.compile(src)
    back = trl.decompile(g)
    assert back == src


# ─── v0.2.1 — Verb elision and current-op pronouns ───────────────────

def test_verb_elision_in_except_clause() -> None:
    src = "NO PARTY MAY WRITE RECORD ledger EXCEPT PARTY system."
    g = trl.compile(src)
    back = trl.decompile(g)
    assert back == src
    # The EXCEPT clause's op should carry verb_elided so canonical form drops verb+modal
    op2 = next(n for n in g["nodes"] if n["id"] == "op-2")
    assert op2["properties"]["verb_elided"] is True
    # Compiler still records the inherited verb for graph use
    assert op2["properties"]["operation"] == "WRITE"


def test_input_pronoun_resolves_to_current_op() -> None:
    src = "EACH AGENT SHALL HANDLE INPUT PARALLEL."
    g = trl.compile(src)
    back = trl.decompile(g)
    assert back == src
    # The INPUT pronoun creates an ACTS_ON edge from op back to itself
    op = next(n for n in g["nodes"] if n.get("type") == "TRANSFORM")
    self_edge = next(e for e in g["edges"]
                     if e["from_id"] == op["id"]
                     and e.get("relation") == "ACTS_ON"
                     and (e.get("properties") or {}).get("pronoun") == "INPUT")
    assert self_edge["to_id"] == op["id"]


# ─── v0.2.2 — Stative clauses ─────────────────────────────────────────

def test_stative_clause_emits_direct_edge() -> None:
    g = trl.compile("THE REMEDY DEPENDS_ON PARTY owner.")
    # No op nodes — only the subject, target, and the direct edge between them
    op_count = sum(1 for n in g["nodes"] if n.get("type") == "TRANSFORM")
    assert op_count == 0
    edge = next(e for e in g["edges"] if e.get("relation") == "DEPENDS_ON")
    assert edge["from_id"] == "remedy-1"
    assert edge["to_id"] == "owner"


def test_stative_clause_round_trip_verbatim() -> None:
    src = "THE REMEDY DEPENDS_ON PARTY owner."
    assert trl.decompile(trl.compile(src)) == src


def test_stative_in_whereas_preamble() -> None:
    src = "WHEREAS SERVICE kafka FEEDS STREAM raw-events."
    g = trl.compile(src)
    back = trl.decompile(g)
    assert back == src
    edge = next(e for e in g["edges"] if e.get("relation") == "FEEDS")
    assert (edge.get("properties") or {}).get("preamble") is True


def test_stative_after_then_in_compound_sentence() -> None:
    """Example 9 pattern: IF ... THEN <stative-clause>."""
    src = "IF ANY PARTY WRITE CONFIDENTIAL RESOURCE THEN THE REMEDY DEPENDS_ON PARTY owner."
    g = trl.compile(src)
    back = trl.decompile(g)
    assert back == src


# ─── v0.2.3 — SAID pronoun + per-mention noun_phrase attributes ──────

def test_said_as_quasi_article() -> None:
    """SAID NOUN parses as `article=SAID + noun`."""
    s = trl.parse("PARTY a SHALL READ SAID DATA.")[0]
    obj = s.clauses[0].object
    assert obj is not None
    assert obj.article == "SAID"
    assert obj.noun == "DATA"


def test_per_mention_attributes_dont_leak_between_references() -> None:
    """A node referenced as `RECORD ledger` then `THE RECORD ledger` keeps
    each mention's article on its own edge — neither leaks into the other."""
    src = (
        'DEFINE "ledger" AS IMMUTABLE RECORD.\n'
        'PARTY system SHALL WRITE EACH VALID DATA TO RECORD ledger.\n'
        'PARTY system SHALL REPLACE THE RECORD ledger FROM SAID RECORD.'
    )
    g = trl.compile(src)
    back = trl.decompile(g)
    assert back == src
    # The ledger node itself should carry only DEFINE attributes
    ledger = next(n for n in g["nodes"] if n["id"] == "ledger")
    assert ledger.get("properties", {}).get("defined") is True
    # Reference shapes are on edges, not on the node
    assert "scope" not in ledger.get("properties", {})


def test_duration_with_two_letter_unit() -> None:
    """v0.2.4 — 100ms tokenizes as one DURATION, not 100m + s."""
    tokens = trl.tokenize("WITHIN 100ms.")
    durations = [t for t in tokens if t.kind == "DURATION"]
    assert len(durations) == 1
    assert durations[0].value == "100ms"


def test_cross_sentence_pronoun_antecedent() -> None:
    """v0.2.4 — RESULT in a later sentence references the prior sentence's op."""
    src = "PARTY a SHALL FILTER DATA.\nPARTY loader SHALL WRITE EACH RESULT TO ENDPOINT store."
    g = trl.compile(src)
    back = trl.decompile(g)
    assert back == src
    # Verify the EACH article on the RESULT pronoun survived
    result_edge = next(e for e in g["edges"]
                       if (e.get("properties") or {}).get("pronoun") == "RESULT")
    assert result_edge["properties"]["pronoun_article"] == "EACH"


def test_subject_only_with_following_conjunction() -> None:
    """v0.2.4 — `EXCEPT PARTY loader PROVIDED_THAT ...` — subject-only EXCEPT
    clause followed by another conjunction-led clause."""
    src = (
        "NO PARTY SHALL WRITE ENDPOINT event-store "
        "EXCEPT PARTY loader "
        "PROVIDED_THAT PARTY loader AUTHENTICATE TO SERVICE auth."
    )
    assert trl.decompile(trl.compile(src)) == src


def test_spec_example_14_verbatim() -> None:
    """SPEC Example 14 — DEFINE + reuse of `ledger` with different mentions
    + SAID pronoun. Round-trips when per-mention shapes are isolated."""
    src = (
        'DEFINE "ledger" AS IMMUTABLE RECORD.\n'
        'PARTY system SHALL WRITE EACH VALID DATA TO RECORD ledger.\n'
        'NO PARTY MAY WRITE RECORD ledger EXCEPT PARTY system.\n'
        'PARTY system SHALL REPLACE THE RECORD ledger FROM SAID RECORD.'
    )
    g = trl.compile(src)
    back = trl.decompile(g)
    assert back == src
    assert trl.compile(back) == g


# ─── v0.1h — Sweep all SPEC_examples.md examples ─────────────────────

import re
from pathlib import Path

SPEC_EXAMPLES_PATH = Path(__file__).resolve().parent.parent / "TRUGS_LANGUAGE" / "SPEC_examples.md"

# Examples this compiler version cannot round-trip yet — each tracked for follow-on:
#   7   — DEADLINE not in 190-word vocabulary (TRUGS-DEV#1542)
#   14  — SAID pronoun used as article-like ("SAID RECORD")
#   28  — Complete ETL — multi-line stative WHEREAS interleaved with operative
# All 28 SPEC_examples now round-trip. (TRUGS-DEVELOPMENT#1542 resolved by
# updating Example 7 to use INSTRUMENT instead of DEADLINE, keeping the
# closed 190-word vocabulary intact.)
KNOWN_DEFERRED: set[int] = set()


def _extract_examples():
    text = SPEC_EXAMPLES_PATH.read_text()
    pat = re.compile(r"### (\d+)\.\s+([^\n]+)\n```\n(.+?)\n```", re.DOTALL)
    return [(int(m.group(1)), m.group(2), m.group(3).strip()) for m in pat.finditer(text)]


def _normalize_whitespace(src: str) -> str:
    return re.sub(r"\s+", " ", src).strip()


def test_spec_examples_in_scope_round_trip() -> None:
    """Every SPEC_examples.md example not in KNOWN_DEFERRED must round-trip
    at the graph level (compile(decompile(g)) == g)."""
    examples = _extract_examples()
    assert examples, "failed to extract examples from SPEC_examples.md"
    failures: list[str] = []
    for n, title, body in examples:
        if n in KNOWN_DEFERRED:
            continue
        norm = _normalize_whitespace(body)
        try:
            g = trl.compile(norm)
            back = trl.decompile(g)
            g2 = trl.compile(back)
            if g != g2:
                failures.append(f"#{n} {title}: graph diverged on round-trip")
        except trl.TRLError as e:
            failures.append(f"#{n} {title}: {type(e).__name__}: {e}")
    assert not failures, "in-scope examples failed:\n" + "\n".join(failures)


def test_spec_examples_coverage_summary() -> None:
    """Sanity assertion: at least 23 of the 28 examples round-trip post-v0.2.1."""
    examples = _extract_examples()
    passed = 0
    for n, _, body in examples:
        norm = _normalize_whitespace(body)
        try:
            g = trl.compile(norm)
            if trl.compile(trl.decompile(g)) == g:
                passed += 1
        except trl.TRLError:
            pass
    assert passed == len(examples), f"only {passed}/{len(examples)} examples round-trip; expected all"


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
    # v0.1a — minimum form
    "PARTY system VALIDATE.",
    "PARTY api FILTER.",
    "PARTY user AUTHENTICATE.",
    "AGENT worker FILTER.",
    "SERVICE gateway VALIDATE.",
    # v0.1b — modals
    "PARTY system SHALL VALIDATE.",
    "AGENT worker MAY FILTER.",
    "PARTY system SHALL_NOT WRITE.",
    # v0.1b — single object
    "PARTY client SHALL REQUEST PARTY server.",
    "PARTY system SHALL VALIDATE DATA.",
    # v0.1b — articles + adjectives on anonymous objects
    "PARTY system SHALL VALIDATE ALL PENDING RECORD.",  # Example 1 verbatim
    "PARTY api SHALL FILTER ALL ACTIVE DATA.",
    "AGENT worker MAY READ ANY CRITICAL FILE.",
    "PARTY system SHALL_NOT WRITE ANY READONLY RESOURCE.",
    # v0.1c — conjunctions, subject carryover
    "PARTY a SHALL FILTER DATA THEN SORT DATA.",
    "PARTY system SHALL FILTER RECORD THEN VALIDATE RECORD.",
    "PARTY api SHALL FILTER ALL ACTIVE RECORD THEN SORT ALL RECORD.",
    # v0.1c — AND parallel (canonical form repeats subject after AND)
    "PARTY system SHALL FILTER DATA AND PARTY system SHALL VALIDATE RECORD.",
    # v0.1c — OR alternative, new subject
    "PARTY server SHALL RESPOND OR PARTY client MAY RETRY.",
    # v0.1c — UNLESS with anonymous subject
    "PARTY api SHALL FILTER RECORD UNLESS NO RECORD EXISTS.",
    "PARTY api SHALL FILTER ALL ACTIVE RECORD UNLESS NO VALID RECORD EXISTS.",
    # v0.1c — IF/PROVIDED_THAT/FINALLY (IF repeats subject; FINALLY inherits)
    "PARTY admin MAY APPROVE RECORD IF PARTY admin AUTHENTICATE.",
    "PARTY system SHALL VALIDATE RECORD PROVIDED_THAT PARTY admin APPROVE.",
    "PARTY system SHALL FILTER RECORD THEN VALIDATE RECORD FINALLY WRITE RECORD.",
    # v0.1d — prepositions
    "PARTY user SHALL AUTHENTICATE TO SERVICE gateway.",
    "PARTY system SHALL WRITE DATA TO ENDPOINT output.",
    "PARTY agent SHALL RESPOND ON_BEHALF_OF PARTY user.",
    "PARTY system SHALL FILTER DATA FROM ENDPOINT input TO ENDPOINT output.",
    "PARTY admin SHALL ADMINISTER RESOURCE CONTAINS NAMESPACE production.",
    "PARTY a SHALL READ DATA REFERENCES RESOURCE store.",
    "PARTY system SHALL VALIDATE RECORD SUBJECT_TO INTERFACE schema.",
    # v0.1d — preposition + conjunction combined
    "PARTY system SHALL FILTER DATA TO ENDPOINT output THEN VALIDATE RECORD.",
    # v0.1e — pronouns
    "PARTY api SHALL FILTER ALL ACTIVE RECORD THEN SORT RESULT.",
    "PARTY system SHALL MAP RECORD TO DATA THEN MERGE RESULT TO STREAM output.",
    "PARTY admin SHALL ADMINISTER RESOURCE REFERENCES SELF.",
    "PARTY a SHALL FILTER DATA THEN VALIDATE OUTPUT.",
    "PARTY system SHALL FILTER DATA THEN WRITE RESULT TO ENDPOINT destination.",
    # v0.1f — adverbs and value literals
    "PARTY server SHALL RESPOND PROMPTLY.",
    "PARTY server SHALL RESPOND WITHIN 30s.",
    "PARTY client MAY RETRY BOUNDED 3.",
    "PARTY server SHALL RESPOND PROMPTLY WITHIN 30s.",
    "PARTY server SHALL RESPOND PROMPTLY WITHIN 30s OR PARTY client MAY RETRY BOUNDED 3.",
    # v0.1g — DEFINE / WHEREAS / STRING literals
    'DEFINE "curator" AS PARTY.',
    'DEFINE "ledger" AS IMMUTABLE RECORD.',
    "WHEREAS PARTY system ADMINISTER ALL RESOURCE.",
    "WHEREAS ALL RECORD REQUIRE MODULE storage.",
]

SPEC_EXAMPLE_1 = "PARTY system SHALL VALIDATE ALL PENDING RECORD."
SPEC_EXAMPLE_2 = "PARTY api SHALL FILTER ALL ACTIVE RECORD THEN SORT RESULT UNLESS NO VALID RECORD REQUIRE SELF."
SPEC_EXAMPLE_3 = (
    "PARTY client SHALL REQUEST PARTY server.\n"
    "PARTY server SHALL RESPOND PROMPTLY WITHIN 30s "
    "OR PARTY client MAY RETRY BOUNDED 3 "
    "THEN HANDLE THE ERROR."
)
SPEC_EXAMPLE_10 = (
    'DEFINE "curator" AS PARTY.\n'
    "PARTY curator SHALL VALIDATE ALL RECORD "
    "AND PARTY curator SHALL_NOT WRITE INVALID RECORD."
)
SPEC_EXAMPLE_18 = (
    "WHEREAS PARTY system ADMINISTER ALL RESOURCE.\n"
    "WHEREAS ALL RECORD REQUIRE MODULE storage.\n"
    "PARTY system SHALL VALIDATE EACH RECORD ONCE "
    "THEN WRITE RESULT TO ENDPOINT output."
)


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
