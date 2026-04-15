# PLAN: TRL compiler v0.3 PR-B — formatting (Categories A, B, G + refinements)

**Issue:** TRUGS-DEVELOPMENT#1544
**Status:** PLANNING (Phases 1–5 of AAA Protocol — awaiting human VALIDATION before coding)
**Target repo:** `TRUGS-LLC/TRUGS`
**Predecessor:** PR-A (#43, merged) — semantic fixes brought 11/28 → 15/28 byte-identical
**Goal of this PR:** 15/28 → 28/28 byte-identical
**Author:** Claude Opus 4.6 (1M context)

---

## Phase 1 — VISION

PR-A closed all the semantic gaps the audit raised. The remaining 13 differences between `decompile(compile(src))` and the published SPEC source are **purely formatting** — same graph, different line-breaks and indentation.

This PR closes the gap so every published example round-trips byte-identical. After merge, `KNOWN_DEFERRED` in `tools/test_trl.py` becomes empty, the coverage assertion becomes `passed == len(examples)`, and `SPEC_examples.md` becomes the de-facto test suite (any future spec change immediately becomes a compiler test).

---

## Phase 2 — FEASIBILITY

GO. Each remaining diff has a categorisable, mechanical fix. The largest model change is **clause depth** (Category A); the rest are decompile heuristics that don't touch the AST.

Estimated effort: one focused session, ~6 hours.

Risk: the line-break heuristics (Categories B, G) require choosing a deterministic rule that the SPEC authors followed implicitly. Mitigation: anchor each rule to a concrete published example, document the rule in code, and re-run the SPEC sweep after each rule lands.

---

## Phase 3 — SPECIFICATIONS

### Inventory of the 13 remaining diffs

After PR-A, the precise diffs are:

#### Cat A — Tree-shaped depth (3 examples)

**#9** — `PROVIDED_THAT` nested under `EXCEPT` should be 4-space indented, not 2:
```
NO PARTY SHALL WRITE CONFIDENTIAL RESOURCE
  EXCEPT PARTY owner MAY WRITE CONFIDENTIAL RESOURCE
    PROVIDED_THAT PARTY owner AUTHENTICATE TO SERVICE auth.    ← 4-space
```

**#16** — `UNLESS` → `PROVIDED_THAT` → `EXCEPT` chain, depths 2, 4, 6:
```
PARTY api SHALL FILTER ALL RECORD
  UNLESS PARTY admin OVERRIDE                          ← 2
    PROVIDED_THAT PARTY admin AUTHENTICATE TO SERVICE auth   ← 4
      EXCEPT PARTY admin ADMINISTER SERVICE auth.    ← 6
```

**#25** — sub-prep `SUBJECT_TO` and sub-OR continuations indented 4:
```
PARTY loader SHALL READ ALL RECORD FROM ENDPOINT source
  THEN BATCH RESULT 100
  THEN MAP EACH RESULT TO VALID DATA
    SUBJECT_TO INTERFACE schema                        ← 4 (sub-prep)
  THEN WRITE RESULT TO ENDPOINT destination
    OR RETRY BOUNDED 3 WITHIN 60s.                     ← 4 (sub-OR)
```

#### Cat B — Tail prep phrases on new line (8 examples)

When a clause has `direct_object + tail prep`, the tail prep goes on a new line indented to match the clause's continuation depth. Affected examples and their tail preps:

- **#5** — `CONTAINS NAMESPACE production` (after `ALL PRIVATE RESOURCE`)
- **#7** — `SUBJECT_TO INSTRUMENT deadline` (final tail) AND `ONCE WITHIN 24h` adverbs on own line
- **#12** — `SUBJECT_TO INTERFACE schema` (final tail)
- **#20** — `AND THE RECORD FROM PARTY worker-b` (continuation of object AND-list breaks)
- **#23** — `TO NAMESPACE api-system` (after long object AND-list)
- **#24** — `SUBJECT_TO PRECEDENT RECORD history` (final tail)
- **#26** — `SUBJECT_TO DATA rate-limit` (final tail)
- **#28** — `SUBJECT_TO INTERFACE event-schema` (mid-clause), `WITHIN 100ms` (adverb on own line after FROM)

#### Cat G — Paragraph breaks between blocks (2 examples)

**#27** — blank line between DEFINE block and operative block:
```
DEFINE "word" AS DATA.
DEFINE "grammar-rule" AS DATA.
DEFINE "constraint" AS DATA.
                                ← BLANK
EACH DATA word NEST STRING DATA name
  AND STRING DATA speech
  AND STRING DATA definition.
                                ← BLANK
PARTY language SHALL ADMINISTER ...
```

**#28** — blank lines between DEFINE block, WHEREAS block, each operative sentence, and final ADMINISTER.

#### Cat E refinement — modal-bearing clauses repeat subject (3 examples)

After PR-A, three remaining diffs are subject-elision bugs. The unified rule:

**A coordinated clause whose own modal is present (SHALL / MAY / SHALL_NOT) repeats its subject regardless of inheritance.**

Affected examples:
- **#8** — `OR PARTY processor SHALL SEND MESSAGE` (current: `OR SHALL SEND`; spec: explicit because SHALL present)
- **#26** — `THEN PARTY api SHALL SEND ERROR TO PARTY client` (current: `THEN SHALL SEND`; spec: explicit because SHALL)
- **#28** — `OR PARTY ingester SHALL RETRY BOUNDED 5 WITHIN 30s` (similar)

This refines PR-A's elision rule.

#### Cat F refinement — adverb on own line when no other content follows (2 examples)

When an adverb is the LAST element of a clause and the clause has prep phrases or a multi-line context, the adverb goes on its own continuation line:

- **#7** — `ONCE WITHIN 24h` is a clause's only tail content; spec puts it on own line
- **#28** — `WITHIN 100ms` follows `FROM STREAM raw-events`; spec breaks the line before WITHIN

This is a corollary of Cat B (tail prep heuristic) extended to adverbs.

### Per-category specifications

#### A — Clause depth model

Add `Clause.depth: int = 0`. During parse, when a SUBORDINATING conjunction introduces a clause, that clause's depth is `parent_depth + 1`. The full set of subordinating conjunctions:

```python
SUBORDINATING_CONJUNCTIONS = {
    "UNLESS", "EXCEPT", "NOTWITHSTANDING", "PROVIDED_THAT",
    "IF", "WHEN", "WHILE", "ELSE",
}
```

`THEN`, `AND`, `OR`, `FINALLY` are coordinating — same depth as parent.

`WHEREAS` is preamble-only (sentence-level, not clause-level conjunction).

Track depth in the parser using a stack: each clause's depth = current_depth; when a subordinating conjunction is consumed, push depth+1 for the next clause; when control returns to the parent (next coordinating conjunction at the parent depth), pop. v0.3 keeps the parse FLAT (clauses + conjunctions list) — depth is decoration on each Clause, not a tree.

**Decompile:** instead of `"\n  " + conj + " " + clause_text`, use `"\n" + "  " * (clause.depth) + conj + " " + clause_text`.

Where `clause.depth` is stored: on the op node as `properties.depth`. Subject_edge's clause inherits its op's depth.

#### B — Tail prep phrase line breaks

Decompile-only change. After computing the rendered clause string, if the clause has BOTH a direct object AND a tail prep phrase whose preposition is in `STRUCTURAL_PREPOSITIONS`, insert a line-break before the prep.

```python
STRUCTURAL_PREPOSITIONS = {
    "SUBJECT_TO", "CONTAINS", "GOVERNS", "REFERENCES", "BINDS",
    "DEPENDS_ON", "IMPLEMENTS", "EXTENDS", "PURSUANT_TO", "ON_BEHALF_OF",
}
```

Inline (always): `TO`, `FROM`, `ROUTES`, `FEEDS`, `RETURNS_TO`, `AS`, `BY`. These are "directional" prepositions tied to the verb's complement.

Edge case: `FROM` in #25's `READ ALL RECORD FROM ENDPOINT source` is inline (no break before). But `FROM` is "directional" — consistent with the rule.

Verify the rule against the 8 affected examples:
- #5 CONTAINS — break ✓
- #7 SUBJECT_TO — break ✓ (also Cat F adverb break)
- #12 SUBJECT_TO — break ✓
- #20 — AND-chained object continuation, not a tail prep — handled by **Cat B sub-rule**: AND-chained objects/preps with multi-clause-style content break to new lines
- #23 TO NAMESPACE after long object AND-list — `TO` is normally inline; **exception**: when the preceding object list is itself an AND-chain ≥ 2 items, break before TO (object-list-too-long heuristic)
- #24 SUBJECT_TO — break ✓
- #26 SUBJECT_TO — break ✓
- #28 SUBJECT_TO — break ✓

#### Cat F refinement — adverb-on-own-line

Same heuristic as Cat B, applied to adverbs at the end of a clause when the clause has prep phrases:

When clause has prep phrases AND adverbs, break to new line before each adverb. This affects #7 (`ONCE WITHIN 24h`) and #28 (`WITHIN 100ms`).

Detail: the adverbs come AFTER preps in the canonical order (PR-A change). For multi-clause sentences, breaking before tail adverbs matches SPEC.

#### Cat E refinement — modal-bearing clauses repeat subject

In `_render_clause`'s context, when called from the decompile loop, check the clause's subject-edge relation. If it's a modal (SHALL/MAY/SHALL_NOT), the canonical form REPEATS the subject regardless of inheritance.

```python
include_subject = (
    not inherit
    or nxt_modal in MODALS  # modal-bearing clause repeats subject
)
```

Where `nxt_modal` is the next clause's subject→op edge relation.

#### Cat G — Paragraph breaks

Add `Sentence.preceded_by_blank_line: bool = False` to the AST. The PARSER detects 2+ consecutive newlines between sentences and sets the flag on the next sentence.

In compile: when the sentence's first node is emitted, set `properties.preceded_by_blank_line = True` on it. In decompile: when assembling the output, if a sentence's first op has this flag, emit a blank line before it.

For DEFINE sentences (which are nodes, not ops), the flag goes on the DEFINED_TERM node.

---

## Phase 4 — ARCHITECTURE

### File-level changes

`tools/trl.py`:
1. **Constants** — add `SUBORDINATING_CONJUNCTIONS`, `COORDINATING_CONJUNCTIONS`, `STRUCTURAL_PREPOSITIONS`, `INLINE_PREPOSITIONS`.
2. **AST** — `Clause.depth: int = 0`, `Sentence.preceded_by_blank_line: bool = False`.
3. **Parser** — track `current_depth` through clause loop; bump for SUBORDINATING conjunctions; reset on next coordinating-at-parent-depth.
4. **Parser** — track source blank-lines between sentences via the position-tracked tokenizer (count `\n` runs in the source between previous sentence's terminator and current sentence's first token).
5. **Compile** — emit `op.properties.depth = clause.depth` for every operation node; emit `properties.preceded_by_blank_line` on first node of sentence.
6. **Decompile `_render_clause`** — break before tail prep phrases in `STRUCTURAL_PREPOSITIONS`; break before tail adverbs when prep phrases exist; break before TO when preceded by AND-chained object list of length ≥ 2.
7. **Decompile sentence-loop** — use op's depth for indentation; emit blank line before sentences flagged with `preceded_by_blank_line`.
8. **Decompile elision rule** — when the next coordinated clause has a modal subject-edge, force `include_subject = True`.

`tools/test_trl.py`:
- New tests per category (4 new):
  - `test_clause_depth_increases_under_subordinating_conjunction`
  - `test_tail_structural_prep_breaks_to_new_line`
  - `test_paragraph_break_preserved_through_round_trip`
  - `test_modal_bearing_clause_repeats_subject_after_inherit`
- Update `KNOWN_DEFERRED` to empty set
- Update coverage assertion to `passed == len(examples)`

### Risks

1. **Subordinating-vs-coordinating partition** — the spec doesn't classify conjunctions this way explicitly. My partition is derived from §2.8 semantics. Risk: some examples may use a "subordinating" conjunction in a coordinating context. Mitigation: if any example breaks, tighten the rule and re-run; document the partition clearly.

2. **Depth tracking determinism** — when does a chain "exit" a subordinate scope? My approach: depth is per-clause, set at parse based on the conjunction that introduced the clause. No "exit" — depth doesn't decrease in v0.3. This means `EXCEPT` after `UNLESS` always nests under UNLESS (depth 4); the next coordinating conjunction (e.g. THEN at sentence level) would be at depth 0 again only if the parser correctly resets. Mitigation: be explicit about the depth-reset rule (next THEN/AND/OR at a coordinating context returns to current outermost depth).

3. **Tail-prep heuristic over-fires** — could break previously-passing examples. Mitigation: re-run the full 28-example sweep after each rule lands; if any previously-passing example regresses, refine.

4. **Cat G blank-lines** — the parser must distinguish "1 newline between sentences" from "2+ newlines". My existing tokenizer tracks line/col but discards whitespace. Need to capture multi-newline runs and attach them to the next sentence's first-token metadata.

### Sequencing within PR-B

Land the changes in this order, running tests after each:
1. **Cat E refinement** (modal-bearing clauses repeat subject) — small, immediate win for #8, #26, #28
2. **Cat A** (depth tracking) — affects #9, #16, #25 and may reveal previously-hidden depth issues
3. **Cat B** (tail prep breaks) — affects #5, #7, #12, #20, #24, #26, #28
4. **Cat F refinement** (adverb-on-own-line) — affects #7, #28
5. **Cat G** (paragraph breaks) — affects #27, #28

After each step, run SPEC sweep and check the count moves in the right direction.

---

## Phase 5 — VALIDATION (HITM gate)

Items the human reviewer should evaluate before approving Phase 6 (CODING):

### Alignment
- [ ] PR-B targets exactly the 13 remaining diffs identified, no scope creep
- [ ] Sequencing within PR-B is acceptable (5 incremental steps)

### Completeness
- [ ] All 13 diffs categorised (Cat A: 3, B: 8, G: 2, plus E and F refinements)
- [ ] Subject elision unified rule (modal → include) covers #8, #26, #28
- [ ] Cat C bug 2 (inherit through subordinate scope) folded into depth-tracking work

### Feasibility
- [ ] `Clause.depth` as a flat decoration (not full tree AST) is acceptable
- [ ] `Sentence.preceded_by_blank_line` data field added — acceptable schema growth
- [ ] `STRUCTURAL_PREPOSITIONS` set as listed:
  - `SUBJECT_TO`, `CONTAINS`, `GOVERNS`, `REFERENCES`, `BINDS`, `DEPENDS_ON`, `IMPLEMENTS`, `EXTENDS`, `PURSUANT_TO`, `ON_BEHALF_OF`
  - Inline always: `TO`, `FROM`, `ROUTES`, `FEEDS`, `RETURNS_TO`, `AS`, `BY`
- [ ] `SUBORDINATING_CONJUNCTIONS` set as listed:
  - `UNLESS`, `EXCEPT`, `NOTWITHSTANDING`, `PROVIDED_THAT`, `IF`, `WHEN`, `WHILE`, `ELSE`
  - Coordinating: `THEN`, `AND`, `OR`, `FINALLY`

### Risk
- [ ] Tail-prep heuristic might disagree with future SPEC additions — accept the documented rule
- [ ] Object-list-too-long heuristic for #23 (break before TO when prior object list is AND-chained ≥ 2) — acceptable?
- [ ] `preceded_by_blank_line` is the only way to round-trip user-written paragraph breaks — acceptable single-bool addition?

### Scope
- [ ] PR-B fits in a single PR (not split further)
- [ ] No grammar / vocabulary changes — confirmed
- [ ] AST gains 2 fields (`depth`, `preceded_by_blank_line`) — acceptable

### Coding plan
- [ ] File-level changes detailed enough
- [ ] Test plan: 4 new unit tests + sweep assertion bump

### Execution order
1. Approve this plan (Phase 5)
2. PR-B coding (Phase 6) — sequential within a single PR
3. Audit (Phase 8) — independent agent, verify 28/28 byte-identical
4. Merge (Phase 9) — close TRUGS-DEVELOPMENT#1544

---

## Phases 6–9 (deferred until Phase 5 approval)

- **Phase 6 — CODING:** implement per architecture; sequence inside the PR.
- **Phase 7 — TESTING:** new unit tests + SPEC sweep at byte-equal level.
- **Phase 8 — AUDIT:** independent agent runs cyclic audit; cycle until P0/P1 = 0.
- **Phase 9 — DEPLOYMENT:** human merges, version bump to v0.3.0, CHANGELOG entry, close TRUGS-DEVELOPMENT#1544.

---

## Reference

- TRUGS-DEVELOPMENT#1544 — umbrella
- TRUGS-LLC/TRUGS#42 — PR-A + PR-B umbrella plan (merged)
- TRUGS-LLC/TRUGS#43 — PR-A semantic fixes (merged) — 11/28 → 15/28
- `TRUGS_LANGUAGE/SPEC_examples.md` — the 28 published examples
- `TRUGS_LANGUAGE/SPEC_grammar.md` §2.8 — conjunction scoping (the source of the subordinating/coordinating partition)
- `.claude/rules/aaa-protocol.md` — process this plan follows
