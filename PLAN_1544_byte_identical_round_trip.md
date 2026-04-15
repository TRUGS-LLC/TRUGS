# PLAN: TRL compiler v0.3 — byte-identical SPEC round-trip

**Issue:** TRUGS-DEVELOPMENT#1544
**Status:** PLANNING (Phases 1–5 of AAA Protocol — awaiting human VALIDATION before coding)
**Target repo:** `TRUGS-LLC/TRUGS`
**Target version:** v0.3.0
**Author:** Claude Opus 4.6 (1M context)

---

## Phase 1 — VISION

Every published example in `TRUGS_LANGUAGE/SPEC_examples.md` must round-trip through `compile()` → `decompile()` → `compile()` and produce **byte-identical** output, not just graph-equal or canonical-equal.

Today (v0.2.5+audit-fixes):
- 28/28 graph-equal
- 17/28 canonical-equal (collapsing `\n  ` continuations)
- **11/28 byte-identical** with the SPEC source

The compiler's "round-trip" claim is the spec's load-bearing correctness criterion (`SPEC_grammar.md` §3: *"If a sentence cannot round-trip, it is not valid"*). Honouring it at the byte level on the published examples turns the SPEC into the test suite — every spec change automatically becomes a compiler test.

This work is **not** about adding new grammar features. The grammar is complete (every example already parses). It is about ensuring the **canonical decompile form chosen by the compiler matches the canonical form chosen by the spec authors**.

---

## Phase 2 — FEASIBILITY

GO. Each of the 17 failing examples has a categorisable, mechanical fix. Two categories require a small model change (clause hierarchy + per-edge noun type); the rest are heuristics or canonical-form rules. No new grammar, no vocabulary changes, no parser restructuring.

Estimated effort: 2 sessions, split as PR-A (semantic) + PR-B (formatting). Risk: medium — the line-break heuristic for tail prep phrases (Category B) requires a deterministic rule the SPEC authors followed implicitly. Mitigation: pick a defensible rule (break before any prep that *follows* the direct object) and document it as the canonical form. If the rule disagrees with one or two SPEC examples, propose the SPEC change in a separate PR (precedent: #1542 for DEADLINE→INSTRUMENT).

---

## Phase 3 — SPECIFICATIONS

### Coverage of the 17 failing examples by category

| # | Title | Categories |
|---|---|---|
| 5 | Scope and authority | B |
| 6 | Authentication flow | D |
| 7 | Scheduled operation with deadline | B, E (partial) |
| 8 | Error recovery with escalation | E |
| 9 | Prohibition with exception and remedy | A |
| 11 | Loop with termination | C |
| 12 | Chained transforms with schema binding | B |
| 13 | Agent delegation chain | C |
| 16 | Nested conditions (three-deep) | A |
| 17 | Event-driven reactive pattern | C |
| 20 | Concurrent actors with synchronization | B (AND-list breaks) |
| 23 | Multi-level containment | B (TO after long object list) |
| 24 | PRECEDENT usage | B |
| 25 | Batch processing with bounded retry | A, B, E |
| 26 | API rate limiting | B, E |
| 27 | Self-describing language | B (AND-list), G (paragraph breaks) |
| 28 | Complete ETL pipeline | C, E, F, G |

### Per-category specifications

#### Category A — Tree-shaped clause hierarchy (3 examples)

**Spec evidence:** `SPEC_examples.md` examples #9 and #16 use progressive indentation to convey clause subordination:

```
PARTY api SHALL FILTER ALL RECORD
  UNLESS PARTY admin OVERRIDE
    PROVIDED_THAT PARTY admin AUTHENTICATE TO SERVICE auth
      EXCEPT PARTY admin ADMINISTER SERVICE auth.
```

Each conjunction nested inside the previous one is indented by 2 more spaces. This implies a TREE of clauses, not a flat chain.

**Subordinating conjunctions** (introduce a nested scope):
- UNLESS, EXCEPT, NOTWITHSTANDING, PROVIDED_THAT — exception/condition modifiers on the preceding clause
- IF, WHEN, WHILE — condition gate
- ELSE — alternate branch on a conditional

**Coordinating conjunctions** (stay at same depth):
- THEN, AND, OR, FINALLY

**Compile model change:** `Sentence.clauses` becomes a TREE, not a flat list. New AST:

```python
@dataclass
class ClauseNode:
    clause: Clause
    children: list[tuple[str, "ClauseNode"]]  # (subordinating_conjunction, child)
    next_in_chain: Optional[tuple[str, "ClauseNode"]]  # (coordinating_conjunction, sibling)
```

Or simpler — keep flat AST + track depth per clause:

```python
@dataclass
class Clause:
    ...existing fields...
    depth: int = 0  # 0 = top-level, 1 = first nesting, 2 = nested under nested, etc.
```

Recommended: **flat with depth field**. Less invasive; preserves existing parse logic; depth computed during parse based on subordinating-conjunction history.

**Decompile rule:** prefix each clause continuation with `"\n" + "  " * (depth + 1)` instead of always `"\n  "`.

#### Category B — Tail prep phrases on new line (7 examples)

**Spec evidence:** prep phrases that come after the verb's direct object, especially the *last* one in a clause, are placed on a new line with the clause-continuation indent (2 spaces):

```
PARTY administrator SHALL ADMINISTER ALL PRIVATE RESOURCE
  CONTAINS NAMESPACE production.
```

Inline prep phrases (Example 4: `MAP EACH PENDING RECORD TO VALID DATA`) stay inline. Tail prep phrases on a separate "logical unit" line.

**Decompile rule:**
- If a clause has BOTH a direct object AND a prep phrase, AND the prep phrase is one of `{SUBJECT_TO, CONTAINS, GOVERNS, REFERENCES, BINDS, DEPENDS_ON, IMPLEMENTS, EXTENDS, PURSUANT_TO, ON_BEHALF_OF, FROM (when not paired with TO)}` — break to a new line before that prep phrase with the clause's depth+1 indent.
- TO/ROUTES/FEEDS/RETURNS_TO/AS/BY remain inline (they are "directional" prep phrases tied to the verb).

This is a heuristic. SPEC authors used it implicitly; we make it explicit. Document in code comments.

#### Category C — Subject identity through inheritance (4 examples)

**Bug 1 — anonymous subjects re-counter:** when a clause inherits subject from a previous clause whose subject was anonymous (e.g. `EACH AGENT`), the inherited NounPhrase, when passed to `_ensure_noun_node`, generates a NEW anon id (`agent-2`) instead of reusing the prior op's subject (`agent-1`).

**Fix:** track `last_emitted_subject_id: dict[id(NounPhrase), str]` keyed by Python id() of the NounPhrase object. When inheriting, look up the prior emitted id and reuse the node directly.

**Bug 2 — inherited subject from wrong scope:** in Example 11:

```
PARTY worker SHALL READ RECORD FROM STREAM input
  WHILE ACTIVE RECORD EXISTS
  THEN WRITE RESULT TO ENDPOINT output
```

`THEN WRITE` should inherit `PARTY worker` (the WHILE's PARENT clause), not `ACTIVE RECORD` (the WHILE's INTERNAL subject). My current chain inherits from immediate predecessor.

**Fix:** when the previous clause is in a SUBORDINATE scope (Category A) and the current clause is back at the parent depth, inherit subject from the parent clause, not the subordinate.

This integrates Category A — once depth tracking exists, "inherit from parent" follows naturally.

#### Category D — Same-id different-noun-type (1 example)

**Bug:** Example 6 has:

```
PARTY user SHALL AUTHENTICATE TO SERVICE gateway.
PARTY gateway MAY GRANT ...
PARTY gateway SHALL ADMINISTER ...
```

The first sentence creates a node `id=gateway, type=SERVICE`. The next sentences reference `PARTY gateway` — same identifier, different type. My `_ensure_noun_node` reuses the existing node by id, so the type stays `SERVICE`, and decompile emits `SERVICE gateway` instead of `PARTY gateway`.

**Fix:** noun type, like article/adjectives, is per-MENTION not per-NODE. Move `type` from the node to the edge's `np_shape` (or a sibling `np_type` field on the edge).

The shared node represents the entity (`gateway`). Each mention's type lives on its referencing edge.

**Caveat:** this changes the fundamental graph schema. The audit's earlier model change (per-mention article/adjectives on edges) sets the precedent. Worth doing — once done, the graph correctly distinguishes "the gateway as a SERVICE" from "the gateway as a PARTY" while keeping the entity identity.

**Alternative:** treat differently-typed mentions of the same id as a SPEC error. Reject at compile. Less work but invalidates Example 6.

**Recommended:** Per-mention type. Aligns with the existing per-mention attribute model.

#### Category E — Subject elision after leading conjunction (4 examples)

**Spec evidence:** Example 8 source:

```
PARTY processor SHALL VALIDATE EACH REQUIRED RECORD.
IF PARTY processor THROW EXCEPTION
  THEN PARTY processor SHALL CATCH THE EXCEPTION
  THEN HANDLE THE ERROR
```

Inside the IF sentence, the first THEN clause **repeats** the subject (`PARTY processor SHALL CATCH`), but the second THEN clause **inherits** (`HANDLE THE ERROR` — no subject).

**Pattern:** the FIRST coordinating conjunction after a leading conditional (IF/WHEN) repeats the subject. SUBSEQUENT same-subject coordinating conjunctions inherit per the existing INHERITING_CONJUNCTIONS rule.

**Canonical-form rule:**
- A clause's subject is elided when: same as prior emitted subject AND the conjunction is in INHERITING_CONJUNCTIONS AND the clause is NOT the first clause after a leading-conjunction parent.
- Otherwise: subject is repeated.

#### Category F — Adverb position (1 example, #28)

**Spec evidence:** Example 28 has `READ EACH DATA raw-event FROM STREAM raw-events WITHIN 100ms` — adverb (`WITHIN 100ms`) AFTER the prep phrase (`FROM STREAM raw-events`).

My current decompile order: `verb → object → adverbs → preps`. SPEC's order here: `verb → object → preps → adverbs` (adverbs at the very end).

**Fix:** Move adverb emission to AFTER preposition phrases. Re-verify the existing examples that pass (#3 `RESPOND PROMPTLY WITHIN 30s` has no preps; #18 `VALIDATE EACH RECORD ONCE` has only direct object — both still produce `verb → object → adverbs`).

#### Category G — Paragraph breaks within multi-block sentences (2 examples)

**Spec evidence:** Examples 27 and 28 have *blank lines* between groups of related sentences (DEFINEs as a block, WHEREAS preambles as a block, operative sentences as a block):

```
DEFINE "raw-event" AS STRING DATA.
DEFINE "clean-event" AS VALID OBJECT DATA.
DEFINE "event-store" AS IMMUTABLE ENDPOINT.

WHEREAS SERVICE kafka FEEDS STREAM raw-events.
WHEREAS ENDPOINT event-store REQUIRE MODULE postgres.

PARTY ingester SHALL READ EACH DATA raw-event FROM STREAM raw-events
...
```

**Decompile rule:** insert a blank line between consecutive sentences when they belong to different "blocks":
- Block 1: all DEFINEs in source order
- Block 2: all WHEREAS preambles
- Block 3+: groups of operative sentences (per source-blank-line cues — but those aren't in the graph)

This is the trickiest because the graph has no information about source blank lines. Two options:

a) Heuristic: blank line between consecutive DEFINEs and the next non-DEFINE; blank line between consecutive WHEREAS preambles and the next non-WHEREAS-preamble; otherwise no blank line.

b) Preserve source blank lines as graph property (e.g. on the next sentence's first op: `properties.preceded_by_blank_line: true`).

**Recommended (b)** — explicit, deterministic, and the only way to round-trip user-written formatting. Add to the parser: when scanning between sentences, if the source contains 2+ consecutive newlines, set the flag on the next sentence's first node.

---

## Phase 4 — ARCHITECTURE

### Two-PR sequence (recommended)

**PR-A: Semantic fixes (Categories C, D, E, F)**
Targets ~7 of the 17 examples. Pure compiler logic, no formatting. Reviewable in one sitting.

**PR-B: Formatting (Categories A, B, G)**
Targets the remaining ~10 examples. Introduces depth tracking, line-break heuristics, paragraph-break tracking. Larger surface, but only formatting — can't break graph correctness.

### File-level changes (PR-A)

`tools/trl.py`:
- `Clause` — add `depth: int = 0` (used by PR-B; introduced now to avoid two model changes)
- `_emit_target_edge` and subject-edge emission — store noun TYPE on edge, not on node (Category D)
- `_ensure_noun_node` — node carries id only, type comes from edge
- `_render_noun_phrase` — read type from supplied shape, not from node
- `_render_clause` — move adverb emission AFTER prep phrases (Category F)
- `compile` — track `inherited_subject_id` map keyed by NounPhrase identity; reuse on inheritance (Category C bug 1)
- `compile` — when inheriting subject across conjunction, look up the parent-depth subject not the immediate predecessor (Category C bug 2 — needs depth, deferred to PR-B but stub the API)
- `decompile` — enforce Category E rule for subject elision after leading-conjunction parent

`tools/test_trl.py`:
- New test per category (4 new tests for PR-A)
- Update `KNOWN_DEFERRED` and coverage assertion as examples cross to byte-identical
- Update existing tests that read node `type` via the new edge-type model

### File-level changes (PR-B)

`tools/trl.py`:
- Parser — track conjunction subordination, set `Clause.depth`
- Parser — track source blank lines (Category G), set `Sentence.preceded_by_blank_line` on first node
- Decompile — use `clause.depth` for indentation (`"\n" + "  " * (depth + 1)`)
- Decompile — break before tail prep phrases when their preposition is in the structural set (Category B)
- Decompile — emit blank line before sentences with the new flag (Category G)

### Edge-cases / risks

- **Per-edge noun type model change** is invasive — every test that reads `node["type"]` to assert noun classification must move to reading the referencing edge's `np_type` (or `np_shape.type`). The audit already did this dance for article/adjectives; same migration shape.
- **Depth tracking from grammar** — the BNF says `clause (CONJUNCTION clause)*` flat. Subordinating conjunctions introducing depth is a SPEC-level convention. Risk: if SPEC authors want a flat parse, the tree interpretation is over-engineered.
   Mitigation: keep flat parse output; depth is a decoration, not a structural change.
- **Tail-prep heuristic** — choosing the right set of "structural" prepositions. Start from {SUBJECT_TO, CONTAINS, GOVERNS, REFERENCES, BINDS, DEPENDS_ON, IMPLEMENTS, EXTENDS, PURSUANT_TO, ON_BEHALF_OF}, refine by running the SPEC sweep.
- **Preserved blank lines** — only round-trippable if encoded in the graph. Adding `preceded_by_blank_line` to the data model is a small, justifiable addition.

---

## Phase 5 — VALIDATION (HITM gate)

Items the human reviewer should evaluate before approving Phase 6 (CODING):

### Alignment
- [ ] Vision (28/28 byte-identical) is the right outcome for v0.3
- [ ] Two-PR sequence is acceptable (vs one big PR)

### Completeness
- [ ] All 17 failing examples are accounted for in the category table
- [ ] Each category has a concrete fix specification
- [ ] Risks are surfaced

### Feasibility
- [ ] Per-mention noun type is acceptable as a graph schema change
- [ ] Depth-as-decoration (vs tree AST) is acceptable
- [ ] Heuristic preposition set for tail-line-breaks is acceptable

### Risk
- [ ] Category B heuristic might disagree with future SPEC examples — accept that risk and document the rule, OR pre-commit to updating SPEC examples that disagree
- [ ] `preceded_by_blank_line` data field added to graphs — acceptable schema growth?

### Scope
- [ ] PR-A scope (~7 examples crossed to byte-identical) is appropriate for one PR
- [ ] PR-B scope (~10 examples crossed) is appropriate for one PR
- [ ] No grammar changes (closed 190-word vocabulary) — confirmed

### Coding plan
- [ ] File-level changes for PR-A are detailed enough
- [ ] Test plan per PR is detailed enough (one new test per category in PR-A; test per fixed example in PR-B)

### Execution order
1. PR-A (semantic) — merge first
2. Re-run audit
3. PR-B (formatting) — merge second
4. Re-run audit
5. Close TRUGS-DEVELOPMENT#1544

---

## Phases 6–9 (deferred until Phase 5 approval)

- **Phase 6 — CODING:** implement per architecture above, two PRs sequentially.
- **Phase 7 — TESTING:** unit tests per category; SPEC sweep at byte-equal level.
- **Phase 8 — AUDIT:** independent agent re-runs cyclic audit; cycle until P0/P1 = 0.
- **Phase 9 — DEPLOYMENT:** human merges, version bump to v0.3.0, CHANGELOG entry.

---

## Reference

- TRUGS-DEVELOPMENT#1544 — umbrella issue
- TRUGS-LLC/TRUGS — target repo
- `TRUGS_LANGUAGE/SPEC_examples.md` — the 28 published examples
- `TRUGS_LANGUAGE/SPEC_grammar.md` — round-trip guarantee (§3) and validation rules (§4)
- TRUGS-LLC/TRUGS#41 — the audit-fixes PR that surfaced this gap (v0.2.5)
- `.claude/rules/aaa-protocol.md` — process this plan follows
