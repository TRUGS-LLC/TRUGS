r"""TRL compiler v0.1 — deterministic TRL ↔ TRUG round-trip.

TRL (TRUGS Language) is a closed 190-word subset of English. Every valid
sentence round-trips through a TRUG graph with no information loss beyond
sugar tokens. This module implements that round-trip.

## What's implemented

Incrementally, toward #1539 full v0.1 (round-trip all 30 canonical
examples in SPEC_examples.md):

1. **v0.1a** — minimum valid sentence: `SUBJ_NOUN id VERB .`
2. **v0.1b** — modals + single object phrase:
   `[SUBJ_NOUN id] [modal] VERB [article] [adj]* NOUN [id] .`
3. **v0.1c** — conjunctions, multi-clause sentences:
   `clause (CONJUNCTION clause)* .`
4. **v0.1d** — prepositional phrases after the verb:
   `clause := subject verb_phrase [direct_object] (PREPOSITION noun_phrase)*`
5. **v0.1e** — pronouns in object / prep-target position.
6. **v0.1f** — adverbs + value literals (INTEGER, DURATION).
7. **v0.1g** (this slice) — DEFINE / WHEREAS / STRING literals:
   - STRING literal tokens: `"quoted text"` → Token.kind="STRING"
   - `DEFINE "name" AS noun_phrase .` — emits a `DEFINED_TERM` node
     tagged with the quoted name. Per §3: `{id: name, type: NOUN,
     properties: {defined: true}}`.
   - `WHEREAS clause .` — a sentence-starting WHEREAS becomes a
     preamble. Compiles identically to a regular clause, with
     `op.properties.preamble = true` so execution semantics are
     declared as context-only.
   - Decompile restores the DEFINE / WHEREAS form verbatim.

Still not implemented: DATE literals, AND-chained prep phrases,
cross-sentence back-references (SAID), noun conjunction in
object/prep lists (e.g. `AGENT a AND AGENT b`).

## Not yet implemented (tracked in TRUGS-DEVELOPMENT#1539 / #1540)

- Modals (SHALL / MAY / SHALL_NOT)
- Articles, adjectives, adverbs
- Object phrases and prepositions
- Conjunctions (THEN / AND / OR / UNLESS / etc.)
- Pronouns (RESULT / SELF / etc.)
- Literal values (INTEGER_LITERAL / STRING_LITERAL / DURATION_LITERAL / DATE_LITERAL)
- WHEREAS preambles, DEFINE definitions

## Spec decisions for v0.1

The following are choices not fully pinned down by SPEC_grammar.md §3;
v0.1 makes them explicit so round-trip is deterministic. Will be raised
as spec-clarification issues against SPEC_grammar.md.

1. **Operation node type** — SPEC_grammar.md §3 says every VERB compiles
   to `{type: "TRANSFORM", ...}`. v0.1 follows this literally. The verb's
   actual subcategory (Obligate / Move / etc.) is preserved in
   `properties.verb_subcategory`.

2. **Unmodaled subject → operation edge** — spec §3 specifies an edge
   only when a modal is present. For unmodaled sentences, v0.1 emits
   an edge with `relation: "EXECUTES"` to keep the graph connected.
   This is a v0.1 convention, to be proposed for spec inclusion.

3. **Node IDs for identified subjects/objects** — the identifier is the
   node id (e.g. `PARTY system` → id "system"). For anonymous nouns
   (bare `RECORD` with no identifier), no node is emitted in v0.1 —
   those appear with articles/adjectives in later grammar subsets.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Optional

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_LANGUAGE_TRUG = REPO_ROOT / "TRUGS_LANGUAGE" / "language.trug.json"

SUGAR_RE = re.compile(r"'[a-z_]+")
IDENTIFIER_RE = re.compile(r"[a-z_][a-z0-9_-]*")
WORD_RE = re.compile(r"[A-Z_]+")
DURATION_RE = re.compile(r"\d+[smhd]")
INTEGER_RE = re.compile(r"\d+")
STRING_RE = re.compile(r'"([^"\\]*(?:\\.[^"\\]*)*)"')


# ─── Tokenizer ────────────────────────────────────────────────────────

@dataclass(frozen=True)
class Token:
    kind: str   # 'WORD' | 'IDENTIFIER' | 'PUNCT' | 'EOF'
    value: str


def tokenize(src: str) -> list[Token]:
    """Strip sugar, split into tokens. Spec §1.1 (sugar) + §1 BNF tokens.

    Produces WORD (uppercase TRL word), IDENTIFIER (lowercase_name),
    and PUNCT ('.'). Whitespace is discarded.
    """
    stripped = SUGAR_RE.sub("", src)
    tokens: list[Token] = []
    i = 0
    while i < len(stripped):
        ch = stripped[i]
        if ch.isspace():
            i += 1
            continue
        if ch == ".":
            tokens.append(Token("PUNCT", "."))
            i += 1
            continue
        # String literal: "..."
        if ch == '"':
            m = STRING_RE.match(stripped, i)
            if not m:
                raise TRLSyntaxError(f"unterminated string literal at position {i}")
            tokens.append(Token("STRING", m.group(1)))
            i = m.end()
            continue
        m = WORD_RE.match(stripped, i)
        if m and (m.end() == len(stripped) or not stripped[m.end()].isalnum() and stripped[m.end()] != "_"):
            tokens.append(Token("WORD", m.group()))
            i = m.end()
            continue
        # Duration literal first (more specific than bare integer)
        m = DURATION_RE.match(stripped, i)
        if m:
            tokens.append(Token("DURATION", m.group()))
            i = m.end()
            continue
        m = INTEGER_RE.match(stripped, i)
        if m:
            tokens.append(Token("INTEGER", m.group()))
            i = m.end()
            continue
        m = IDENTIFIER_RE.match(stripped, i)
        if m:
            tokens.append(Token("IDENTIFIER", m.group()))
            i = m.end()
            continue
        raise TRLSyntaxError(f"unexpected character {ch!r} at position {i}")
    tokens.append(Token("EOF", ""))
    return tokens


# ─── Language lookup ─────────────────────────────────────────────────

@lru_cache(maxsize=4)
def load_language(path: Optional[str] = None) -> dict:
    """Load language.trug.json, return dict of {WORD: {speech, subcategory, ...}}."""
    p = Path(path) if path else DEFAULT_LANGUAGE_TRUG
    trug = json.loads(p.read_text())
    lookup: dict[str, dict] = {}
    for node in trug["nodes"]:
        props = node.get("properties", {})
        word = props.get("word")
        if word:
            lookup[word] = {
                "speech": props.get("speech"),
                "subcategory": props.get("subcategory"),
                "definition": props.get("definition", ""),
                "core": props.get("core", False),
            }
    return lookup


def classify(word: str, lang: dict) -> dict:
    """Return {speech, subcategory, ...} for a TRL word. Raises on unknown."""
    entry = lang.get(word)
    if not entry:
        raise TRLVocabularyError(f"{word!r} is not in the TRL vocabulary")
    return entry


# ─── AST ──────────────────────────────────────────────────────────────

@dataclass
class NounPhrase:
    noun: str = ""                  # e.g. "PARTY". Empty if pronoun is set.
    identifier: Optional[str] = None  # e.g. "system"
    article: Optional[str] = None     # "ALL" | "EACH" | "NO" | ...
    adjectives: list[str] = field(default_factory=list)  # ["PENDING", "CRITICAL"]
    pronoun: Optional[str] = None     # "RESULT" | "SELF" | "OUTPUT" | ...


@dataclass
class AdverbPhrase:
    adverb: str                    # e.g. "WITHIN"
    value: Optional[str] = None    # raw literal text, e.g. "30s" or "3"


@dataclass
class VerbPhrase:
    verb: Optional[str] = None     # e.g. "VALIDATE"; None means inherit from prior clause
    modal: Optional[str] = None    # "SHALL" | "MAY" | "SHALL_NOT"
    adverbs: list[AdverbPhrase] = field(default_factory=list)


@dataclass
class PrepPhrase:
    preposition: str               # e.g. "TO"
    target: NounPhrase
    extra_targets: list[NounPhrase] = field(default_factory=list)  # AND-chained: TO a AND b AND c


@dataclass
class Clause:
    subject: Optional[NounPhrase]      # None means inherit from prior clause
    verb_phrase: VerbPhrase
    object: Optional[NounPhrase] = None
    extra_objects: list[NounPhrase] = field(default_factory=list)  # AND-chained: A AND B AND C
    prep_phrases: list["PrepPhrase"] = field(default_factory=list)
    value_arg: Optional[str] = None    # trailing INTEGER argument (e.g. "10" in TAKE RESULT 10)


@dataclass
class Definition:
    name: str          # quoted string, e.g. "curator"
    noun_phrase: NounPhrase  # e.g. IMMUTABLE RECORD


@dataclass
class Sentence:
    clauses: list["Clause"] = field(default_factory=list)  # >=1 clause for normal/preamble
    conjunctions: list[str] = field(default_factory=list)  # length = len(clauses)-1
    preamble: bool = False          # True for WHEREAS preambles
    leading_conjunction: Optional[str] = None  # "IF" | "WHEN" — sentence-starting conditional
    definition: Optional[Definition] = None   # set iff this sentence is a DEFINE


MODALS = {"SHALL", "MAY", "SHALL_NOT"}
CONJUNCTIONS = {
    "THEN", "AND", "OR", "ELSE", "IF", "WHEN", "WHILE", "FINALLY",
    "UNLESS", "EXCEPT", "NOTWITHSTANDING", "PROVIDED_THAT", "WHEREAS",
}
# Conjunctions where canonical form omits the subject when it matches
# the prior clause. Others (AND/OR/UNLESS/IF/WHEN/WHILE/etc.) always
# repeat the subject for clarity — they introduce scope or parallelism.
INHERITING_CONJUNCTIONS = {"THEN", "FINALLY", "ELSE"}
# Pronouns supported in v0.1e+ (object / prep-target positions).
# SAID and cross-sentence "THE <noun>" back-references land later.
#
# Antecedent semantics:
#   PRIOR_OP   — refers to the previous clause's op (RESULT, OUTPUT)
#   CURRENT_OP — refers to the current clause's op-self (INPUT, SOURCE, TARGET)
#   SUBJECT    — refers to the current clause's subject (SELF)
PRONOUNS_PRIOR_OP = {"RESULT", "OUTPUT"}
PRONOUNS_CURRENT_OP = {"INPUT", "SOURCE", "TARGET"}
PRONOUNS_SUBJECT_ANTECEDENT = {"SELF"}
PRONOUNS = PRONOUNS_PRIOR_OP | PRONOUNS_CURRENT_OP | PRONOUNS_SUBJECT_ANTECEDENT


# ─── Errors ───────────────────────────────────────────────────────────

class TRLError(Exception):
    """Base for TRL compiler errors."""


class TRLSyntaxError(TRLError):
    """Malformed TRL — tokens do not match the grammar."""


class TRLVocabularyError(TRLError):
    """Word is not in the 190-word TRL vocabulary."""


class TRLGrammarError(TRLError):
    """Valid tokens, wrong composition (e.g. modal on non-Actor subject)."""


# ─── Parser ───────────────────────────────────────────────────────────

def parse(src: str, lang: Optional[dict] = None) -> list[Sentence]:
    """Parse TRL source into a list of Sentences.

    v0.1: supports only SUBJECT_NOUN identifier VERB . form.
    """
    if lang is None:
        lang = load_language()
    tokens = tokenize(src)
    sentences: list[Sentence] = []
    pos = 0

    while pos < len(tokens) and tokens[pos].kind != "EOF":
        sentence, pos = _parse_sentence(tokens, pos, lang)
        sentences.append(sentence)

    return sentences


def _parse_noun_phrase(tokens: list[Token], pos: int, lang: dict,
                        require_identifier: bool = False,
                        allow_pronoun: bool = True) -> tuple[NounPhrase, int]:
    """Parse [article] [adjective]* NOUN [identifier], OR a bare pronoun."""
    # Pronoun shortcut (object / prep-target position). Subjects set
    # allow_pronoun=False — cross-sentence / back-reference pronouns as
    # subjects are deferred past v0.1.
    if tokens[pos].kind == "WORD" and tokens[pos].value in PRONOUNS:
        if not allow_pronoun:
            raise TRLGrammarError(
                f"{tokens[pos].value!r} is a pronoun and cannot appear here — subjects require a noun phrase"
            )
        if require_identifier:
            raise TRLGrammarError(
                f"{tokens[pos].value!r} is a pronoun and cannot be a required-identifier subject"
            )
        pronoun_word = tokens[pos].value
        return NounPhrase(pronoun=pronoun_word), pos + 1

    article: Optional[str] = None
    adjectives: list[str] = []

    # Optional article
    if tokens[pos].kind == "WORD":
        entry = lang.get(tokens[pos].value)
        if entry and entry["speech"] == "article":
            article = tokens[pos].value
            pos += 1

    # Article + pronoun shortcut (e.g. EACH RESULT)
    if article is not None and tokens[pos].kind == "WORD" and tokens[pos].value in PRONOUNS:
        if not allow_pronoun:
            raise TRLGrammarError(f"{tokens[pos].value!r} pronoun not allowed here")
        np = NounPhrase(article=article, pronoun=tokens[pos].value)
        return np, pos + 1

    # Zero or more adjectives
    while tokens[pos].kind == "WORD":
        entry = lang.get(tokens[pos].value)
        if entry and entry["speech"] == "adjective":
            adjectives.append(tokens[pos].value)
            pos += 1
        else:
            break

    # Required noun
    if tokens[pos].kind != "WORD":
        raise TRLSyntaxError(f"expected noun at position {pos}, got {tokens[pos]!r}")
    noun = tokens[pos].value
    entry = classify(noun, lang)
    if entry["speech"] != "noun":
        raise TRLGrammarError(f"{noun!r} is a {entry['speech']}, not a noun")
    pos += 1

    # Optional identifier
    identifier: Optional[str] = None
    if tokens[pos].kind == "IDENTIFIER":
        identifier = tokens[pos].value
        pos += 1
    elif require_identifier:
        raise TRLGrammarError(f"{noun!r} requires an identifier as a subject")

    return NounPhrase(noun=noun, identifier=identifier, article=article, adjectives=adjectives), pos


def _peek_and_noun_phrase(tokens: list[Token], pos: int, lang: dict) -> bool:
    """True if the current token is AND introducing a noun_list extension.

    Disambiguates noun_list AND (binds within prep_phrase / object list) from
    clause-level AND (joins clauses with verbs). Algorithm: speculatively parse
    a noun_phrase after the AND; if what follows that noun_phrase is a modal
    or verb, the AND is clause-level (the noun_phrase is the next clause's
    subject). Otherwise it's noun_list AND.
    """
    if pos >= len(tokens) or tokens[pos].kind != "WORD" or tokens[pos].value != "AND":
        return False
    nxt = tokens[pos + 1] if pos + 1 < len(tokens) else None
    if nxt is None or nxt.kind != "WORD":
        return False
    if nxt.value in MODALS or nxt.value in CONJUNCTIONS:
        return False
    e = lang.get(nxt.value)
    if not e or e["speech"] not in ("noun", "article", "adjective", "pronoun"):
        return False
    # Speculatively parse the noun_phrase starting at pos+1; check the
    # follow-on token. If modal/verb, it's clause-level AND.
    try:
        _, after = _parse_noun_phrase(tokens, pos + 1, lang, require_identifier=False)
    except TRLError:
        return False
    follow = tokens[after] if after < len(tokens) else None
    if follow is not None and follow.kind == "WORD":
        if follow.value in MODALS:
            return False
        f_entry = lang.get(follow.value)
        if f_entry and f_entry["speech"] == "verb":
            return False
    return True


def _parse_clause(tokens: list[Token], pos: int, lang: dict,
                   require_subject: bool) -> tuple[Clause, int]:
    """Parse one clause: [subject] [modal] VERB [object].

    Clause terminates when the next token is '.', EOF, or a CONJUNCTION.
    """
    subject: Optional[NounPhrase] = None
    if require_subject:
        # First clause — subject required but identifier optional.
        # Anonymous subjects like "ALL RECORD" or "NO PARTY" are valid
        # per SPEC_grammar.md §1 BNF (noun_phrase := [ARTICLE] [ADJ]* NOUN [id]).
        # Pronouns as subjects are deferred past v0.1.
        subject, pos = _parse_noun_phrase(tokens, pos, lang, require_identifier=False, allow_pronoun=False)
    else:
        # Speculative parse: try noun_phrase, check that modal/verb follows.
        # If it doesn't, back up and inherit subject from prior clause.
        saved_pos = pos
        cur = tokens[pos]
        if cur.kind == "WORD" and lang.get(cur.value, {}).get("speech") in ("noun", "article", "adjective"):
            try:
                trial_subject, trial_pos = _parse_noun_phrase(tokens, pos, lang, require_identifier=False)
                # Commit subject if the next token is:
                #   - a modal or verb (regular clause)
                #   - PUNCT '.' (subject-only carve-out, verb elided)
                nxt = tokens[trial_pos]
                if (nxt.kind == "PUNCT" and nxt.value == ".") or (nxt.kind == "WORD" and (
                    nxt.value in MODALS
                    or lang.get(nxt.value, {}).get("speech") == "verb"
                )):
                    subject = trial_subject
                    pos = trial_pos
            except TRLError:
                pos = saved_pos

    # Optional modal
    modal: Optional[str] = None
    if tokens[pos].kind == "WORD" and tokens[pos].value in MODALS:
        modal = tokens[pos].value
        pos += 1

    # Verb. May be elided when the clause is a subject-only carve-out (e.g.
    # `EXCEPT PARTY system` after a clause that established the verb).
    # Returns verb=None to signal verb-inheritance to the caller.
    verb: Optional[str] = None
    if tokens[pos].kind == "WORD":
        v = tokens[pos].value
        v_entry = lang.get(v)
        if v_entry and v_entry["speech"] == "verb" and v not in MODALS:
            verb = v
            pos += 1
        elif tokens[pos].kind == "PUNCT" or v in CONJUNCTIONS:
            pass  # subject-only clause, verb inherited
    # If we still don't have a verb and the next token isn't a sentence
    # terminator or another conjunction, fall through — caller may treat
    # as stative or error.
    if verb is None and tokens[pos].kind != "PUNCT" and not (
        tokens[pos].kind == "WORD" and tokens[pos].value in CONJUNCTIONS
    ):
        # Allow stative form: subject + PREPOSITION + noun_phrase
        # (handled below — verb stays None and we fall through to the
        # post-verb loop, which will pick up the preposition).
        pass

    # After the verb: a mix of adverbs, one optional direct object, and zero or
    # more prep phrases, in any source order. Accept until punctuation/conjunction.
    adverbs: list[AdverbPhrase] = []
    obj: Optional[NounPhrase] = None
    extra_objects: list[NounPhrase] = []
    prep_phrases: list[PrepPhrase] = []
    value_arg: Optional[str] = None

    while tokens[pos].kind != "PUNCT" and tokens[pos].kind != "EOF":
        # Trailing INTEGER as a verb-argument (e.g. TAKE RESULT 10, BATCH RESULT 100)
        if tokens[pos].kind == "INTEGER":
            if value_arg is not None:
                break  # only one trailing int per verb
            value_arg = tokens[pos].value
            pos += 1
            continue
        if tokens[pos].kind != "WORD":
            break
        if tokens[pos].value in CONJUNCTIONS:
            break
        tok = tokens[pos]
        entry = lang.get(tok.value)
        if not entry:
            break
        sp = entry["speech"]
        if sp == "adverb":
            adv_word = tok.value
            pos += 1
            adv_value: Optional[str] = None
            if tokens[pos].kind in ("DURATION", "INTEGER"):
                adv_value = tokens[pos].value
                pos += 1
            adverbs.append(AdverbPhrase(adverb=adv_word, value=adv_value))
        elif sp == "preposition":
            prep_word = tok.value
            pos += 1
            target, pos = _parse_noun_phrase(tokens, pos, lang, require_identifier=False)
            extras: list[NounPhrase] = []
            # AND-chained noun_list within a prep_phrase: TO a AND b AND c
            while _peek_and_noun_phrase(tokens, pos, lang):
                pos += 1  # consume AND
                extra, pos = _parse_noun_phrase(tokens, pos, lang, require_identifier=False)
                extras.append(extra)
            prep_phrases.append(PrepPhrase(preposition=prep_word, target=target, extra_targets=extras))
        elif sp in ("noun", "article", "adjective", "pronoun") and obj is None:
            obj, pos = _parse_noun_phrase(tokens, pos, lang, require_identifier=False)
            # AND-chained object list: MERGE A AND B AND C
            while _peek_and_noun_phrase(tokens, pos, lang):
                pos += 1  # consume AND
                extra, pos = _parse_noun_phrase(tokens, pos, lang, require_identifier=False)
                extra_objects.append(extra)
        else:
            break

    return Clause(
        subject=subject,
        verb_phrase=VerbPhrase(verb=verb, modal=modal, adverbs=adverbs),
        object=obj,
        extra_objects=extra_objects,
        prep_phrases=prep_phrases,
        value_arg=value_arg,
    ), pos


def _parse_definition(tokens: list[Token], pos: int, lang: dict) -> tuple[Sentence, int]:
    """Parse `DEFINE "name" AS noun_phrase .`. Caller has NOT consumed DEFINE yet."""
    assert tokens[pos].kind == "WORD" and tokens[pos].value == "DEFINE"
    pos += 1
    if tokens[pos].kind != "STRING":
        raise TRLSyntaxError(f"DEFINE requires a quoted string name, got {tokens[pos]!r}")
    name = tokens[pos].value
    pos += 1
    if tokens[pos].kind != "WORD" or tokens[pos].value != "AS":
        raise TRLSyntaxError(f"expected 'AS' after DEFINE name, got {tokens[pos]!r}")
    pos += 1
    np, pos = _parse_noun_phrase(tokens, pos, lang, require_identifier=False)
    if tokens[pos].kind != "PUNCT" or tokens[pos].value != ".":
        raise TRLSyntaxError(f"expected '.' after DEFINE clause, got {tokens[pos]!r}")
    pos += 1
    return Sentence(definition=Definition(name=name, noun_phrase=np)), pos


def _parse_sentence(tokens: list[Token], pos: int, lang: dict) -> tuple[Sentence, int]:
    # DEFINE definition — sentence-level
    if tokens[pos].kind == "WORD" and tokens[pos].value == "DEFINE":
        return _parse_definition(tokens, pos, lang)

    # Sentence-starting prefixes: WHEREAS preamble or IF/WHEN conditional.
    # Each tags the first clause's op with a property so decompile reproduces it.
    preamble = False
    leading_conjunction: Optional[str] = None
    if tokens[pos].kind == "WORD":
        if tokens[pos].value == "WHEREAS":
            preamble = True
            pos += 1
        elif tokens[pos].value in ("IF", "WHEN"):
            leading_conjunction = tokens[pos].value
            pos += 1

    clauses: list[Clause] = []
    conjunctions: list[str] = []

    # First clause — subject required
    clause, pos = _parse_clause(tokens, pos, lang, require_subject=True)
    clauses.append(clause)

    # Subsequent clauses joined by conjunctions
    while tokens[pos].kind == "WORD" and tokens[pos].value in CONJUNCTIONS:
        conj = tokens[pos].value
        pos += 1
        clause, pos = _parse_clause(tokens, pos, lang, require_subject=False)
        clauses.append(clause)
        conjunctions.append(conj)

    # Terminator
    if tokens[pos].kind != "PUNCT" or tokens[pos].value != ".":
        raise TRLSyntaxError(
            f"expected '.' at position {pos}, got {tokens[pos]!r}. "
            "Remaining v0.1 grammar (noun conjunctions, DATE literals) lands in later PRs."
        )
    pos += 1

    return Sentence(
        clauses=clauses, conjunctions=conjunctions, preamble=preamble,
        leading_conjunction=leading_conjunction,
    ), pos


# ─── Compile (TRL → TRUG) ────────────────────────────────────────────

def compile(src_or_sentences, lang: Optional[dict] = None) -> dict:
    """Compile TRL into a TRUG graph fragment (nodes + edges).

    Accepts a string or a pre-parsed list[Sentence]. Returns a graph
    dict with keys {nodes, edges}. Deterministic — the same input
    always produces the same graph.
    """
    if lang is None:
        lang = load_language()
    sentences = parse(src_or_sentences, lang) if isinstance(src_or_sentences, str) else src_or_sentences

    nodes: list[dict] = []
    edges: list[dict] = []
    op_counter = 0
    anon_counters: dict[str, int] = {}

    def _ensure_noun_node(np: NounPhrase) -> str:
        """Emit a node for a noun_phrase, return its id. Idempotent by id."""
        if np.identifier:
            node_id = np.identifier
        else:
            anon_counters[np.noun] = anon_counters.get(np.noun, 0) + 1
            node_id = f"{np.noun.lower()}-{anon_counters[np.noun]}"

        # Build properties from article + adjectives
        props: dict = {}
        if np.article:
            props["scope"] = {"quantifier": np.article}
        if np.adjectives:
            # Group adjectives by their subcategory (state/type/priority/...) per §3
            adj_groups: dict[str, list[str]] = {}
            for adj in np.adjectives:
                sub = classify(adj, lang)["subcategory"]
                adj_groups.setdefault(sub, []).append(adj)
            for sub, vals in adj_groups.items():
                props[sub] = vals[0] if len(vals) == 1 else vals

        # Find existing node; if present and identified, merge compatibly
        existing = next((n for n in nodes if n["id"] == node_id), None)
        if existing is None:
            node: dict = {"id": node_id, "type": np.noun}
            if props:
                node["properties"] = props
            nodes.append(node)
        elif props:
            # Only merge properties if node is identified (re-used subject)
            existing.setdefault("properties", {}).update(props)
        return node_id

    inherited_verb_phrase: Optional[VerbPhrase] = None
    for sentence in sentences:
        # DEFINE sentence: emit a DEFINED_TERM node, no ops/edges
        if sentence.definition is not None:
            d = sentence.definition
            # Build property dict from the noun_phrase (adjectives, article)
            def_props: dict = {"defined": True, "name": d.name}
            if d.noun_phrase.article:
                def_props["scope"] = {"quantifier": d.noun_phrase.article}
            for adj in d.noun_phrase.adjectives:
                sub = classify(adj, lang)["subcategory"]
                def_props.setdefault(sub, adj)
            nodes.append({
                "id": d.name,
                "type": d.noun_phrase.noun,
                "properties": def_props,
            })
            continue

        inherited_subject: Optional[NounPhrase] = None
        clause_op_ids: list[str] = []
        prev_op_id: Optional[str] = None

        def _resolve_pronoun(np: NounPhrase, current_subj_id: str, current_op_id: str) -> str:
            """Return the antecedent node id for a pronoun noun_phrase."""
            word = np.pronoun
            if word in PRONOUNS_SUBJECT_ANTECEDENT:
                return current_subj_id
            if word in PRONOUNS_CURRENT_OP:
                return current_op_id
            if word in PRONOUNS_PRIOR_OP:
                if prev_op_id is None:
                    raise TRLGrammarError(
                        f"pronoun {word!r} has no prior clause to reference"
                    )
                return prev_op_id
            raise TRLGrammarError(f"unhandled pronoun {word!r}")

        for clause in sentence.clauses:
            subject_np = clause.subject or inherited_subject
            if subject_np is None:
                raise TRLGrammarError(
                    "clause has no subject and no prior clause to inherit from"
                )
            subj_id = _ensure_noun_node(subject_np)
            inherited_subject = subject_np

            # Verb may be elided in carve-out clauses (e.g. EXCEPT PARTY system).
            # Inherit verb_phrase from prior clause if so.
            effective_vp = clause.verb_phrase
            if effective_vp.verb is None:
                if inherited_verb_phrase is None:
                    raise TRLGrammarError(
                        "clause has no verb and no prior clause to inherit from"
                    )
                # Keep clause's own modal if present, otherwise inherit prior modal too
                effective_vp = VerbPhrase(
                    verb=inherited_verb_phrase.verb,
                    modal=clause.verb_phrase.modal or inherited_verb_phrase.modal,
                    adverbs=clause.verb_phrase.adverbs,
                )
            inherited_verb_phrase = effective_vp

            op_counter += 1
            op_id = f"op-{op_counter}"
            op_props: dict = {
                "operation": effective_vp.verb,
                "verb_subcategory": classify(effective_vp.verb, lang)["subcategory"],
            }
            if effective_vp.adverbs:
                op_props["adverbs"] = [
                    ({"adverb": a.adverb, "value": a.value}
                     if a.value is not None else {"adverb": a.adverb})
                    for a in effective_vp.adverbs
                ]
            if sentence.preamble and not clause_op_ids:
                op_props["preamble"] = True
            if sentence.leading_conjunction and not clause_op_ids:
                op_props["leading_conjunction"] = sentence.leading_conjunction
            if clause.value_arg is not None:
                op_props["value_arg"] = clause.value_arg
            if clause.verb_phrase.verb is None:
                # Original source had no verb — mark for elision on decompile
                op_props["verb_elided"] = True
            nodes.append({"id": op_id, "type": "TRANSFORM", "properties": op_props})

            relation = effective_vp.modal if effective_vp.modal else "EXECUTES"
            edges.append({"from_id": subj_id, "to_id": op_id, "relation": relation})

            chain_counter = 0

            def _emit_target_edge(np: NounPhrase, relation: str, chain_id: Optional[int]) -> None:
                edge_props: dict = {}
                if np.pronoun:
                    target_id = _resolve_pronoun(np, subj_id, op_id)
                    edge_props["pronoun"] = np.pronoun
                else:
                    target_id = _ensure_noun_node(np)
                if chain_id is not None:
                    edge_props["chain_id"] = chain_id
                edge: dict = {"from_id": op_id, "to_id": target_id, "relation": relation}
                if edge_props:
                    edge["properties"] = edge_props
                edges.append(edge)

            if clause.object is not None:
                cid: Optional[int] = None
                if clause.extra_objects:
                    chain_counter += 1
                    cid = chain_counter
                _emit_target_edge(clause.object, "ACTS_ON", cid)
                for extra in clause.extra_objects:
                    _emit_target_edge(extra, "ACTS_ON", cid)

            for pp in clause.prep_phrases:
                cid = None
                if pp.extra_targets:
                    chain_counter += 1
                    cid = chain_counter
                _emit_target_edge(pp.target, pp.preposition, cid)
                for extra in pp.extra_targets:
                    _emit_target_edge(extra, pp.preposition, cid)

            clause_op_ids.append(op_id)
            prev_op_id = op_id

        # Conjunction edges between consecutive ops in the same sentence
        for i, conj in enumerate(sentence.conjunctions):
            edges.append({
                "from_id": clause_op_ids[i],
                "to_id": clause_op_ids[i + 1],
                "relation": conj,
            })

    return {"nodes": nodes, "edges": edges}


# ─── Decompile (TRUG → TRL) ───────────────────────────────────────────

def _is_anonymous_id(node: dict) -> bool:
    """Auto-generated IDs follow `{type_lower}-N`. Skip them on render."""
    return re.fullmatch(rf"{re.escape(node['type'].lower())}-\d+", node["id"]) is not None


def _render_noun_phrase(node: dict, lang: dict) -> str:
    """Render a noun node back to its TRL form: [article] [adj]* NOUN [id]."""
    parts: list[str] = []
    props = node.get("properties") or {}
    scope = props.get("scope") or {}
    article = scope.get("quantifier")
    if article:
        parts.append(article)

    # Adjectives: reconstruct in §2.5 fixed order
    adj_order = ["quantity", "priority", "state", "access", "type"]
    for sub in adj_order:
        vals = props.get(sub)
        if vals is None:
            continue
        if sub == "type" and isinstance(vals, str) and vals.isupper() and not lang.get(vals, {}).get("speech") == "adjective":
            continue
        if isinstance(vals, str):
            parts.append(vals)
        elif isinstance(vals, list):
            parts.extend(vals)

    parts.append(node["type"])
    if not _is_anonymous_id(node):
        parts.append(node["id"])
    return " ".join(parts)


def _render_clause(op_id: str, op_nodes: dict, edges: list[dict], nodes_by_id: dict,
                    lang: dict, include_subject: bool) -> str:
    """Render a single clause (subject + modal + verb + object)."""
    op = op_nodes[op_id]
    # Find subject edge (modal or EXECUTES incoming)
    subj_edge = next((e for e in edges if e["to_id"] == op_id
                      and e.get("relation") in MODALS | {"EXECUTES"}), None)
    if subj_edge is None:
        raise TRLGrammarError(f"op {op_id} has no subject edge")
    subj_node = nodes_by_id[subj_edge["from_id"]]
    modal = subj_edge.get("relation")

    parts: list[str] = []
    if include_subject:
        parts.append(_render_noun_phrase(subj_node, lang=lang))
    elided = op["properties"].get("verb_elided")
    if modal in MODALS and not elided:
        parts.append(modal)
    elif modal != "EXECUTES" and modal not in MODALS:
        raise TRLGrammarError(f"unknown subject→operation relation {modal!r}")
    if not elided:
        parts.append(op["properties"]["operation"])

    preposition_words = {w for w, e in lang.items() if e["speech"] == "preposition"}

    # Canonical post-verb order:
    #   1. direct object (ACTS_ON edge, if any)
    #   2. adverbs (op.properties.adverbs, in stored order)
    #   3. preposition phrases (outgoing preposition edges, in edge-list order)
    # This matches SPEC_examples.md: adverbs after the object when one is present
    # (Examples 7, 15, 18); after the verb directly when there is none (Example 3).

    def _render_target(e: dict) -> str:
        pronoun = (e.get("properties") or {}).get("pronoun")
        if pronoun:
            return pronoun
        node = nodes_by_id.get(e["to_id"])
        return _render_noun_phrase(node, lang=lang) if node else ""

    # 1. Direct object(s) — possibly AND-chained via chain_id
    obj_edges = [e for e in edges
                 if e["from_id"] == op_id and e.get("relation") == "ACTS_ON"]
    if obj_edges:
        first = obj_edges[0]
        parts.append(_render_target(first))
        cid = (first.get("properties") or {}).get("chain_id")
        if cid is not None:
            for e in obj_edges[1:]:
                if (e.get("properties") or {}).get("chain_id") == cid:
                    parts.append("AND")
                    parts.append(_render_target(e))

    # 2. Adverbs
    for adv in op["properties"].get("adverbs", []):
        parts.append(adv["adverb"])
        if "value" in adv and adv["value"] is not None:
            parts.append(adv["value"])

    # 3. Preposition phrases — group AND-chained noun_lists by chain_id
    rendered_chain_ids: set[int] = set()
    for e in edges:
        if e["from_id"] != op_id:
            continue
        rel = e.get("relation")
        if rel not in preposition_words:
            continue
        cid = (e.get("properties") or {}).get("chain_id")
        if cid is not None and cid in rendered_chain_ids:
            continue
        parts.append(rel)
        parts.append(_render_target(e))
        if cid is not None:
            rendered_chain_ids.add(cid)
            for e2 in edges:
                if (e2["from_id"] == op_id
                        and e2.get("relation") == rel
                        and (e2.get("properties") or {}).get("chain_id") == cid
                        and e2 is not e):
                    parts.append("AND")
                    parts.append(_render_target(e2))

    # 4. Trailing integer argument (TAKE RESULT 10, BATCH RESULT 100)
    if op["properties"].get("value_arg") is not None:
        parts.append(op["properties"]["value_arg"])

    return " ".join(parts)


def _render_define(node: dict, lang: dict) -> str:
    """Render a DEFINED_TERM node back to its `DEFINE "name" AS np .` form."""
    props = node.get("properties") or {}
    name = props.get("name", node["id"])
    parts = [f'DEFINE "{name}" AS']
    scope = (props.get("scope") or {}).get("quantifier")
    if scope:
        parts.append(scope)
    for sub in ["quantity", "priority", "state", "access", "type"]:
        val = props.get(sub)
        if val is None:
            continue
        if sub == "type" and isinstance(val, str) and val.isupper() \
                and not lang.get(val, {}).get("speech") == "adjective":
            continue
        if isinstance(val, str):
            parts.append(val)
    parts.append(node["type"])
    return " ".join(parts) + "."


def decompile(graph: dict, lang: Optional[dict] = None) -> str:
    """Turn a TRUG graph fragment back into canonical TRL source."""
    if lang is None:
        lang = load_language()

    nodes_by_id = {n["id"]: n for n in graph["nodes"]}
    op_nodes = {n["id"]: n for n in graph["nodes"]
                if n.get("type") == "TRANSFORM"
                and n.get("properties", {}).get("operation")}
    edges = graph["edges"]

    # Index conjunction edges: op_from -> (conjunction_word, op_to)
    conj_next: dict[str, tuple[str, str]] = {}
    conj_targets: set[str] = set()
    for e in edges:
        rel = e.get("relation")
        if rel in CONJUNCTIONS and e["from_id"] in op_nodes and e["to_id"] in op_nodes:
            conj_next[e["from_id"]] = (rel, e["to_id"])
            conj_targets.add(e["to_id"])

    sentences_out: list[str] = []
    visited_ops: set[str] = set()

    # Walk nodes in graph order. DEFINED_TERM nodes emit as DEFINE sentences.
    # Operation nodes that are not conjunction-targets start a sentence chain.
    for node in graph["nodes"]:
        if node.get("properties", {}).get("defined") is True:
            sentences_out.append(_render_define(node, lang))
            continue
        if node.get("type") != "TRANSFORM":
            continue
        if node.get("properties", {}).get("operation") is None:
            continue
        op_id = node["id"]
        if op_id in visited_ops or op_id in conj_targets:
            continue

        preamble = bool(node["properties"].get("preamble"))
        leading = node["properties"].get("leading_conjunction")
        parts: list[str] = []
        if preamble:
            parts.append("WHEREAS")
        elif leading:
            parts.append(leading)
        parts.append(_render_clause(op_id, op_nodes, edges, nodes_by_id, lang,
                                     include_subject=True))
        visited_ops.add(op_id)
        cur = op_id
        prev_subject_id = next(e["from_id"] for e in edges
                                if e["to_id"] == cur and e.get("relation") in MODALS | {"EXECUTES"})
        while cur in conj_next:
            conj, nxt = conj_next[cur]
            nxt_subject_id = next(e["from_id"] for e in edges
                                   if e["to_id"] == nxt and e.get("relation") in MODALS | {"EXECUTES"})
            # Canonical form: omit the subject only for INHERITING_CONJUNCTIONS
            # (THEN/FINALLY/ELSE — sequential/continuation). AND/OR/UNLESS/etc.
            # always repeat the subject, matching SPEC_examples.md conventions.
            same_subject = nxt_subject_id == prev_subject_id
            inherit = conj in INHERITING_CONJUNCTIONS and same_subject
            include_subject = not inherit
            parts.append(conj)
            parts.append(_render_clause(nxt, op_nodes, edges, nodes_by_id, lang,
                                          include_subject=include_subject))
            visited_ops.add(nxt)
            prev_subject_id = nxt_subject_id
            cur = nxt
        sentences_out.append(" ".join(parts) + ".")

    return "\n".join(sentences_out)


# ─── Validate ─────────────────────────────────────────────────────────

def validate(graph: dict, lang: Optional[dict] = None) -> list[str]:
    """Return a list of validation errors. Empty list = valid.

    v0.1 implements a subset of SPEC_grammar.md §4 rules:
      - Rule 1: every node has a type from the noun vocabulary (or TRANSFORM for ops)
      - Rule 2: every edge has a relation (TRL preposition or v0.1 convention)
    Full 12-rule validator is v0.2+ work.
    """
    if lang is None:
        lang = load_language()
    errors: list[str] = []

    nouns = {w for w, e in lang.items() if e["speech"] == "noun"}
    prepositions = {w for w, e in lang.items() if e["speech"] == "preposition"}
    v01_relations = prepositions | MODALS | CONJUNCTIONS | {"EXECUTES", "ACTS_ON"}

    for n in graph.get("nodes", []):
        if "type" not in n:
            errors.append(f"node {n.get('id', '?')}: missing type")
        elif n["type"] == "TRANSFORM":
            pass  # Operation nodes are fine
        elif n["type"] not in nouns:
            errors.append(f"node {n.get('id', '?')}: type {n['type']!r} is not a TRL noun")

    for e in graph.get("edges", []):
        rel = e.get("relation")
        if not rel:
            errors.append(f"edge {e.get('from_id')} → {e.get('to_id')}: missing relation")
        elif rel not in v01_relations:
            errors.append(f"edge {e.get('from_id')} → {e.get('to_id')}: unknown relation {rel!r}")

    return errors


# ─── CLI ──────────────────────────────────────────────────────────────

def main(argv: Optional[list] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="trugs-trl",
        description="TRL compiler — compile/decompile/validate TRL ↔ TRUG.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    for cmd, help_text in [("compile", "Compile TRL to TRUG JSON"),
                            ("decompile", "Decompile TRUG JSON to TRL"),
                            ("validate", "Validate a TRUG JSON")]:
        sp = sub.add_parser(cmd, help=help_text)
        sp.add_argument("file", help="input file, or - for stdin")

    ns = parser.parse_args(argv)
    src = sys.stdin.read() if ns.file == "-" else Path(ns.file).read_text()

    try:
        if ns.command == "compile":
            print(json.dumps(compile(src), indent=2))
        elif ns.command == "decompile":
            print(decompile(json.loads(src)))
        elif ns.command == "validate":
            errors = validate(json.loads(src))
            for err in errors:
                print(f"  {err}", file=sys.stderr)
            if errors:
                print(f"{len(errors)} validation error(s)", file=sys.stderr)
                return 1
            print("valid")
    except TRLError as e:
        print(f"{type(e).__name__}: {e}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
