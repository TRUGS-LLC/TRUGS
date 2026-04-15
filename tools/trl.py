"""TRL compiler v0.1 — deterministic TRL ↔ TRUG round-trip.

TRL (TRUGS Language) is a closed 190-word subset of English. Every valid
sentence round-trips through a TRUG graph with no information loss beyond
sugar tokens. This module implements that round-trip.

## What's implemented

Incrementally, toward #1539 full v0.1 (round-trip all 30 canonical
examples in SPEC_examples.md):

1. **v0.1a** (initial) — minimum valid sentence: `SUBJ_NOUN id VERB .`
2. **v0.1b** (this slice) — modals + single object phrase:
   `[SUBJ_NOUN id] [modal] VERB [article] [adj]* NOUN [id] .`
   - Modals: SHALL, MAY, SHALL_NOT
   - Articles on objects: ALL, EACH, EVERY, ANY, SOME, A, NO, NONE, THE, THIS
   - Stacked adjectives preceding the object noun
   - Anonymous (bare) object nouns get auto-generated IDs: `{noun}-N`
   - Identified object nouns work (e.g. `PARTY server`)
   - Covers SPEC_examples.md Example 1 (`Simple obligation`)

Still not implemented (future PRs on this branch or subsequent):
conjunctions (THEN/AND/OR/UNLESS/etc.), prepositions (TO/FROM/CONTAINS),
pronouns (RESULT/SELF), adverbs + value literals, WHEREAS preambles,
DEFINE definitions, multi-sentence programs with cross-references.

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
    noun: str                      # e.g. "PARTY"
    identifier: Optional[str] = None  # e.g. "system"
    article: Optional[str] = None     # "ALL" | "EACH" | "NO" | ...
    adjectives: list[str] = field(default_factory=list)  # ["PENDING", "CRITICAL"]


@dataclass
class VerbPhrase:
    verb: str                      # e.g. "VALIDATE"
    modal: Optional[str] = None    # "SHALL" | "MAY" | "SHALL_NOT"


@dataclass
class Sentence:
    subject: NounPhrase
    verb_phrase: VerbPhrase
    object: Optional[NounPhrase] = None


MODALS = {"SHALL", "MAY", "SHALL_NOT"}


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
    """Parse [article] [adjective]* NOUN [identifier]."""
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


def _parse_sentence(tokens: list[Token], pos: int, lang: dict) -> tuple[Sentence, int]:
    # Subject noun_phrase (identifier required)
    subject, pos = _parse_noun_phrase(tokens, pos, lang, require_identifier=True)

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

    # Optional object noun_phrase
    obj: Optional[NounPhrase] = None
    if tokens[pos].kind == "WORD" and tokens[pos].value != "." and tokens[pos].kind != "EOF":
        # Peek: if next WORD is a noun/article/adjective, parse as object
        first_w = tokens[pos].value
        first_entry = lang.get(first_w)
        if first_entry and first_entry["speech"] in ("noun", "article", "adjective"):
            obj, pos = _parse_noun_phrase(tokens, pos, lang, require_identifier=False)

    # Terminator
    if tokens[pos].kind != "PUNCT" or tokens[pos].value != ".":
        raise TRLSyntaxError(
            f"expected '.' at position {pos}, got {tokens[pos]!r}. "
            "This slice supports SUBJECT [modal] VERB [object] . — "
            "conjunctions/prepositions/pronouns land in later PRs."
        )
    pos += 1

    return Sentence(subject=subject, verb_phrase=VerbPhrase(verb=verb, modal=modal), object=obj), pos


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
        subj_id = _ensure_noun_node(sentence.subject)

        op_counter += 1
        op_id = f"op-{op_counter}"
        nodes.append({
            "id": op_id,
            "type": "TRANSFORM",
            "properties": {
                "operation": sentence.verb_phrase.verb,
                "verb_subcategory": classify(sentence.verb_phrase.verb, lang)["subcategory"],
            },
        })

        relation = sentence.verb_phrase.modal if sentence.verb_phrase.modal else "EXECUTES"
        edges.append({"from_id": subj_id, "to_id": op_id, "relation": relation})

        if sentence.object is not None:
            obj_id = _ensure_noun_node(sentence.object)
            # Operation → object edge. §3: verb-object relation.
            # v0.1 convention: unnamed edge uses relation "ACTS_ON" until a
            # preposition appears between verb and object.
            edges.append({"from_id": op_id, "to_id": obj_id, "relation": "ACTS_ON"})

    return {"nodes": nodes, "edges": edges}


# ─── Decompile (TRUG → TRL) ───────────────────────────────────────────

def _render_noun_phrase(node: dict, anonymous: bool, lang: dict) -> str:
    """Render a noun node back to its TRL form: [article] [adj]* NOUN [id]."""
    parts: list[str] = []
    props = node.get("properties") or {}
    scope = props.get("scope") or {}
    article = scope.get("quantifier")
    if article:
        parts.append(article)

    # Adjectives: reconstruct in §2.5 fixed order
    # [QUANTITY] [PRIORITY] [STATE] [ACCESS] [TYPE]
    adj_order = ["quantity", "priority", "state", "access", "type"]
    for sub in adj_order:
        vals = props.get(sub)
        if vals is None:
            continue
        # Skip reserved keys that aren't adjectives (e.g. 'type' vs adj subcategory 'type')
        if sub == "type" and isinstance(vals, str) and vals.isupper() and not lang.get(vals, {}).get("speech") == "adjective":
            continue
        if isinstance(vals, str):
            parts.append(vals)
        elif isinstance(vals, list):
            parts.extend(vals)

    parts.append(node["type"])
    if not anonymous:
        parts.append(node["id"])
    return " ".join(parts)


def decompile(graph: dict, lang: Optional[dict] = None) -> str:
    """Turn a TRUG graph fragment back into canonical TRL source.

    Round-trip guarantee: `compile(decompile(g)) == g` for graphs produced
    by this compiler.
    """
    if lang is None:
        lang = load_language()

    nodes_by_id = {n["id"]: n for n in graph["nodes"]}
    op_nodes = [n for n in graph["nodes"] if n.get("type") == "TRANSFORM"
                and n.get("properties", {}).get("operation")]
    op_by_id = {n["id"]: n for n in op_nodes}

    # Build subject and object edges per op
    subj_edge_by_op: dict[str, dict] = {}
    obj_edge_by_op: dict[str, dict] = {}
    for e in graph["edges"]:
        if e["to_id"] in op_by_id:
            subj_edge_by_op[e["to_id"]] = e
        elif e["from_id"] in op_by_id and e.get("relation") == "ACTS_ON":
            obj_edge_by_op[e["from_id"]] = e

    sentences_out: list[str] = []
    for op_id, op in op_by_id.items():
        subj_edge = subj_edge_by_op.get(op_id)
        if subj_edge is None:
            continue
        subj_node = nodes_by_id.get(subj_edge["from_id"])
        if subj_node is None:
            continue

        subj_str = _render_noun_phrase(subj_node, anonymous=False, lang=lang)
        verb = op["properties"]["operation"]
        modal = subj_edge.get("relation")

        parts = [subj_str]
        if modal in MODALS:
            parts.append(modal)
        elif modal != "EXECUTES":
            raise TRLGrammarError(f"unknown subject→operation relation {modal!r}")
        parts.append(verb)

        obj_edge = obj_edge_by_op.get(op_id)
        if obj_edge is not None:
            obj_node = nodes_by_id.get(obj_edge["to_id"])
            if obj_node is not None:
                # Anonymous if id matches the auto-pattern `<type_lower>-N`
                anon = re.fullmatch(rf"{re.escape(obj_node['type'].lower())}-\d+", obj_node["id"]) is not None
                parts.append(_render_noun_phrase(obj_node, anonymous=anon, lang=lang))

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
    v01_relations = prepositions | {"SHALL", "MAY", "SHALL_NOT", "EXECUTES", "ACTS_ON"}

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
