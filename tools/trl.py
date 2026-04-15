"""TRL compiler v0.1 — deterministic TRL ↔ TRUG round-trip.

TRL (TRUGS Language) is a closed 190-word subset of English. Every valid
sentence round-trips through a TRUG graph with no information loss beyond
sugar tokens. This module implements that round-trip.

## What's implemented in v0.1

Minimum valid sentence form only, per SPEC_grammar.md §1.2:

    SUBJECT_NOUN identifier VERB .

Example: `PARTY system VALIDATE.`

Tokenizer, word classifier (backed by language.trug.json), and round-trip
for this form are complete. Subsequent PRs expand coverage per
SPEC_grammar.md §1 BNF and the 30 canonical examples in SPEC_examples.md.

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


@dataclass
class VerbPhrase:
    verb: str                      # e.g. "VALIDATE"
    modal: Optional[str] = None    # "SHALL" | "MAY" | "SHALL_NOT" — v0.2+


@dataclass
class Sentence:
    subject: NounPhrase
    verb_phrase: VerbPhrase


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


def _parse_sentence(tokens: list[Token], pos: int, lang: dict) -> tuple[Sentence, int]:
    # Subject: WORD (noun) + IDENTIFIER
    if tokens[pos].kind != "WORD":
        raise TRLSyntaxError(f"expected noun at position {pos}, got {tokens[pos]!r}")
    noun = tokens[pos].value
    entry = classify(noun, lang)
    if entry["speech"] != "noun":
        raise TRLGrammarError(f"{noun!r} is a {entry['speech']}, not a noun — expected subject")
    pos += 1

    identifier: Optional[str] = None
    if tokens[pos].kind == "IDENTIFIER":
        identifier = tokens[pos].value
        pos += 1

    # Verb
    if tokens[pos].kind != "WORD":
        raise TRLSyntaxError(f"expected verb at position {pos}, got {tokens[pos]!r}")
    verb = tokens[pos].value
    verb_entry = classify(verb, lang)
    if verb_entry["speech"] != "verb":
        raise TRLGrammarError(f"{verb!r} is a {verb_entry['speech']}, not a verb")
    pos += 1

    # Terminator
    if tokens[pos].kind != "PUNCT" or tokens[pos].value != ".":
        raise TRLSyntaxError(
            f"expected '.' at position {pos}, got {tokens[pos]!r}. "
            "v0.1 supports only SUBJECT VERB. form — complex sentences land in later PRs."
        )
    pos += 1

    return Sentence(
        subject=NounPhrase(noun=noun, identifier=identifier),
        verb_phrase=VerbPhrase(verb=verb),
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

    for sentence in sentences:
        subj_id = sentence.subject.identifier
        if subj_id is None:
            raise TRLGrammarError(
                "v0.1 requires an identifier on the subject noun (e.g. 'PARTY system' not 'PARTY')"
            )
        # §3: NOUN + identifier -> node
        if not any(n["id"] == subj_id for n in nodes):
            nodes.append({"id": subj_id, "type": sentence.subject.noun})

        # §3: VERB -> operation node (type="TRANSFORM" per spec literal)
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

        # Subject -> operation edge. v0.1: unmodaled uses "EXECUTES"
        relation = sentence.verb_phrase.modal if sentence.verb_phrase.modal else "EXECUTES"
        edges.append({"from_id": subj_id, "to_id": op_id, "relation": relation})

    return {"nodes": nodes, "edges": edges}


# ─── Decompile (TRUG → TRL) ───────────────────────────────────────────

def decompile(graph: dict, lang: Optional[dict] = None) -> str:
    """Turn a TRUG graph fragment back into canonical TRL source.

    For v0.1 minimum-form graphs only. Round-trip guarantee per
    SPEC_grammar.md §3: `compile(decompile(g)) == g`.
    """
    if lang is None:
        lang = load_language()

    # Find operation nodes (type TRANSFORM with properties.operation)
    op_nodes = [n for n in graph["nodes"] if n.get("type") == "TRANSFORM"
                and n.get("properties", {}).get("operation")]
    # Map each op to its incoming subject edge
    op_by_id = {n["id"]: n for n in op_nodes}
    subj_nodes = {n["id"]: n for n in graph["nodes"] if n.get("type") != "TRANSFORM"}

    sentences_out: list[str] = []
    # Stable order: by op index (op-1, op-2, ...) then fallback to node order
    for edge in graph["edges"]:
        op = op_by_id.get(edge["to_id"])
        subj = subj_nodes.get(edge["from_id"])
        if op is None or subj is None:
            continue
        subj_noun = subj["type"]
        subj_id = subj["id"]
        verb = op["properties"]["operation"]
        modal = edge.get("relation")
        if modal == "EXECUTES":
            # Unmodaled
            sentences_out.append(f"{subj_noun} {subj_id} {verb}.")
        elif modal in ("SHALL", "MAY", "SHALL_NOT"):
            sentences_out.append(f"{subj_noun} {subj_id} {modal} {verb}.")
        else:
            raise TRLGrammarError(f"unknown subject→operation relation {modal!r} — v0.1 only handles EXECUTES/SHALL/MAY/SHALL_NOT")

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
    v01_relations = prepositions | {"SHALL", "MAY", "SHALL_NOT", "EXECUTES", "TRANSFORM"}

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
