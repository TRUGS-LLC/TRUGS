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
6. **v0.1f** (this slice) — adverbs + value literals:
   - Adverbs between verb and object: `VERB (ADVERB [value])* [object] ...`
   - All 18 TRL adverbs recognised
   - INTEGER literals (`\d+`) and DURATION literals (`\d+[smhd]`) parsed
     as Token.kind=="INTEGER" / "DURATION"
   - Each adverb compiles to an entry on `op.properties.adverbs`:
     `[{"adverb": "WITHIN", "value": "30s"}, ...]` preserving source order
   - Decompile walks the list in order, emitting `ADVERB [value]`
   - STRING and DATE literals deferred; they appear rarely in examples
     and land with DEFINE / WHEREAS in v0.1g.

Still not implemented: WHEREAS preamble semantics, DEFINE definitions,
multi-sentence cross-sentence references (SAID / THE-noun across
sentences), AND-chained prep phrases.

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
IDENTIFIER_RE = re.compile(r"[a-z_][a-z0-9_]*")
WORD_RE = re.compile(r"[A-Z_]+")
DURATION_RE = re.compile(r"\d+[smhd]")
INTEGER_RE = re.compile(r"\d+")


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
    verb: str                      # e.g. "VALIDATE"
    modal: Optional[str] = None    # "SHALL" | "MAY" | "SHALL_NOT"
    adverbs: list[AdverbPhrase] = field(default_factory=list)


@dataclass
class PrepPhrase:
    preposition: str               # e.g. "TO"
    target: NounPhrase


@dataclass
class Clause:
    subject: Optional[NounPhrase]      # None means inherit from prior clause
    verb_phrase: VerbPhrase
    object: Optional[NounPhrase] = None
    prep_phrases: list["PrepPhrase"] = field(default_factory=list)


@dataclass
class Sentence:
    clauses: list["Clause"]            # >=1 clause
    conjunctions: list[str] = field(default_factory=list)  # length = len(clauses)-1


MODALS = {"SHALL", "MAY", "SHALL_NOT"}
CONJUNCTIONS = {
    "THEN", "AND", "OR", "ELSE", "IF", "WHEN", "WHILE", "FINALLY",
    "UNLESS", "EXCEPT", "NOTWITHSTANDING", "PROVIDED_THAT", "WHEREAS",
}
# Pronouns supported in v0.1e (object / prep-target positions).
# SAID and cross-sentence "THE <noun>" back-references land later.
PRONOUNS_OP_ANTECEDENT = {"RESULT", "OUTPUT", "INPUT", "SOURCE", "TARGET"}
PRONOUNS_SUBJECT_ANTECEDENT = {"SELF"}
PRONOUNS = PRONOUNS_OP_ANTECEDENT | PRONOUNS_SUBJECT_ANTECEDENT


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
                        require_identifier: bool = False) -> tuple[NounPhrase, int]:
    """Parse [article] [adjective]* NOUN [identifier], OR a bare pronoun."""
    # Pronoun shortcut (object / prep-target position)
    if tokens[pos].kind == "WORD" and tokens[pos].value in PRONOUNS:
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


def _parse_clause(tokens: list[Token], pos: int, lang: dict,
                   require_subject: bool) -> tuple[Clause, int]:
    """Parse one clause: [subject] [modal] VERB [object].

    Clause terminates when the next token is '.', EOF, or a CONJUNCTION.
    """
    subject: Optional[NounPhrase] = None
    if require_subject:
        subject, pos = _parse_noun_phrase(tokens, pos, lang, require_identifier=True)
    else:
        # Speculative parse: try noun_phrase, check that modal/verb follows.
        # If it doesn't, back up and inherit subject from prior clause.
        saved_pos = pos
        cur = tokens[pos]
        if cur.kind == "WORD" and lang.get(cur.value, {}).get("speech") in ("noun", "article", "adjective"):
            try:
                trial_subject, trial_pos = _parse_noun_phrase(tokens, pos, lang, require_identifier=False)
                # After a real subject, the next token must be a modal or a verb.
                nxt = tokens[trial_pos]
                if nxt.kind == "WORD" and (
                    nxt.value in MODALS
                    or lang.get(nxt.value, {}).get("speech") == "verb"
                ):
                    subject = trial_subject
                    pos = trial_pos
            except TRLError:
                pos = saved_pos

    # Optional modal
    modal: Optional[str] = None
    if tokens[pos].kind == "WORD" and tokens[pos].value in MODALS:
        modal = tokens[pos].value
        pos += 1

    # Verb
    if tokens[pos].kind != "WORD":
        raise TRLSyntaxError(f"expected verb at position {pos}, got {tokens[pos]!r}")
    verb = tokens[pos].value
    verb_entry = classify(verb, lang)
    if verb_entry["speech"] != "verb":
        raise TRLGrammarError(f"{verb!r} is a {verb_entry['speech']}, not a verb")
    if verb in MODALS:
        raise TRLGrammarError(f"{verb!r} is a modal and cannot appear as the primary verb")
    pos += 1

    # Zero or more adverb phrases: ADVERB [value]
    adverbs: list[AdverbPhrase] = []
    while tokens[pos].kind == "WORD":
        entry = lang.get(tokens[pos].value)
        if not (entry and entry["speech"] == "adverb"):
            break
        adv_word = tokens[pos].value
        pos += 1
        adv_value: Optional[str] = None
        if tokens[pos].kind in ("DURATION", "INTEGER"):
            adv_value = tokens[pos].value
            pos += 1
        adverbs.append(AdverbPhrase(adverb=adv_word, value=adv_value))

    # Optional direct-object noun_phrase (a regular noun_phrase or a pronoun)
    obj: Optional[NounPhrase] = None
    if tokens[pos].kind == "WORD" and tokens[pos].value not in CONJUNCTIONS:
        first_entry = lang.get(tokens[pos].value)
        if first_entry and first_entry["speech"] in ("noun", "article", "adjective", "pronoun"):
            obj, pos = _parse_noun_phrase(tokens, pos, lang, require_identifier=False)

    # Zero or more prepositional phrases: PREPOSITION noun_phrase
    prep_phrases: list[PrepPhrase] = []
    while tokens[pos].kind == "WORD" and tokens[pos].value not in CONJUNCTIONS:
        entry = lang.get(tokens[pos].value)
        if not (entry and entry["speech"] == "preposition"):
            break
        prep_word = tokens[pos].value
        pos += 1
        target, pos = _parse_noun_phrase(tokens, pos, lang, require_identifier=False)
        prep_phrases.append(PrepPhrase(preposition=prep_word, target=target))

    return Clause(
        subject=subject,
        verb_phrase=VerbPhrase(verb=verb, modal=modal, adverbs=adverbs),
        object=obj,
        prep_phrases=prep_phrases,
    ), pos


def _parse_sentence(tokens: list[Token], pos: int, lang: dict) -> tuple[Sentence, int]:
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
            "Remaining v0.1 grammar (prepositions / pronouns / literals) lands in later PRs."
        )
    pos += 1

    return Sentence(clauses=clauses, conjunctions=conjunctions), pos


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

    for sentence in sentences:
        inherited_subject: Optional[NounPhrase] = None
        clause_op_ids: list[str] = []
        prev_op_id: Optional[str] = None

        def _resolve_pronoun(np: NounPhrase, current_subj_id: str) -> str:
            """Return the antecedent node id for a pronoun noun_phrase."""
            word = np.pronoun
            if word in PRONOUNS_SUBJECT_ANTECEDENT:
                return current_subj_id
            if word in PRONOUNS_OP_ANTECEDENT:
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

            op_counter += 1
            op_id = f"op-{op_counter}"
            op_props: dict = {
                "operation": clause.verb_phrase.verb,
                "verb_subcategory": classify(clause.verb_phrase.verb, lang)["subcategory"],
            }
            if clause.verb_phrase.adverbs:
                op_props["adverbs"] = [
                    ({"adverb": a.adverb, "value": a.value}
                     if a.value is not None else {"adverb": a.adverb})
                    for a in clause.verb_phrase.adverbs
                ]
            nodes.append({"id": op_id, "type": "TRANSFORM", "properties": op_props})

            relation = clause.verb_phrase.modal if clause.verb_phrase.modal else "EXECUTES"
            edges.append({"from_id": subj_id, "to_id": op_id, "relation": relation})

            if clause.object is not None:
                if clause.object.pronoun:
                    target_id = _resolve_pronoun(clause.object, subj_id)
                    edges.append({
                        "from_id": op_id, "to_id": target_id, "relation": "ACTS_ON",
                        "properties": {"pronoun": clause.object.pronoun},
                    })
                else:
                    obj_id = _ensure_noun_node(clause.object)
                    edges.append({"from_id": op_id, "to_id": obj_id, "relation": "ACTS_ON"})

            for pp in clause.prep_phrases:
                if pp.target.pronoun:
                    target_id = _resolve_pronoun(pp.target, subj_id)
                    edges.append({
                        "from_id": op_id, "to_id": target_id, "relation": pp.preposition,
                        "properties": {"pronoun": pp.target.pronoun},
                    })
                else:
                    target_id = _ensure_noun_node(pp.target)
                    edges.append({"from_id": op_id, "to_id": target_id, "relation": pp.preposition})

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
    if modal in MODALS:
        parts.append(modal)
    elif modal != "EXECUTES":
        raise TRLGrammarError(f"unknown subject→operation relation {modal!r}")
    parts.append(op["properties"]["operation"])

    # Adverbs — stored on op.properties.adverbs as ordered list
    for adv in op["properties"].get("adverbs", []):
        parts.append(adv["adverb"])
        if "value" in adv and adv["value"] is not None:
            parts.append(adv["value"])

    # Preposition set from the language TRUG (what relations count as prep edges)
    preposition_words = {w for w, e in lang.items() if e["speech"] == "preposition"}

    # Outgoing edges from this op, in list order. ACTS_ON renders as a bare
    # direct object; preposition edges render as "PREP target_noun_phrase".
    # Pronoun edges carry `properties.pronoun` and render that word instead.
    for e in edges:
        if e["from_id"] != op_id:
            continue
        rel = e.get("relation")
        pronoun = (e.get("properties") or {}).get("pronoun")
        if rel == "ACTS_ON":
            if pronoun:
                parts.append(pronoun)
            else:
                obj_node = nodes_by_id.get(e["to_id"])
                if obj_node is not None:
                    parts.append(_render_noun_phrase(obj_node, lang=lang))
        elif rel in preposition_words:
            parts.append(rel)
            if pronoun:
                parts.append(pronoun)
            else:
                target_node = nodes_by_id.get(e["to_id"])
                if target_node is not None:
                    parts.append(_render_noun_phrase(target_node, lang=lang))

    return " ".join(parts)


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

    # Roots of sentences = ops with no incoming conjunction edge.
    # Iterate in op-1, op-2, ... order for determinism.
    def op_order_key(op_id: str) -> int:
        try:
            return int(op_id.split("-", 1)[1])
        except (IndexError, ValueError):
            return 10**9

    sentences_out: list[str] = []
    visited: set[str] = set()
    for op_id in sorted(op_nodes.keys(), key=op_order_key):
        if op_id in conj_targets or op_id in visited:
            continue
        # Walk the conjunction chain from this root
        parts: list[str] = [_render_clause(op_id, op_nodes, edges, nodes_by_id, lang,
                                            include_subject=True)]
        visited.add(op_id)
        cur = op_id
        # Track last-clause's subject to decide whether to reprint it
        prev_subject_id = next(e["from_id"] for e in edges
                                if e["to_id"] == cur and e.get("relation") in MODALS | {"EXECUTES"})
        while cur in conj_next:
            conj, nxt = conj_next[cur]
            nxt_subject_id = next(e["from_id"] for e in edges
                                   if e["to_id"] == nxt and e.get("relation") in MODALS | {"EXECUTES"})
            include_subject = nxt_subject_id != prev_subject_id
            parts.append(conj)
            parts.append(_render_clause(nxt, op_nodes, edges, nodes_by_id, lang,
                                          include_subject=include_subject))
            visited.add(nxt)
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
