# Dark Code: How TRUGS Resolves the LLM-Generated Code Legibility Crisis

**Authors:** Xepayac
**Date:** April 2026
**Venue:** arXiv (cs.SE primary, cs.AI secondary)
**Issue:** Xepayac/TRUGS-DEVELOPMENT#1509

---

## Abstract

As LLM code generation becomes mainstream, organizations accumulate *Dark Code* — code that humans did not write and cannot follow the logic of or understand what the code is accomplishing. We define the Dark Code problem, show why existing mitigations (code review, documentation, testing, static analysis, AI auditing) fail structurally, and present TRUGS (Traceable Recursive Universal Graph Specification) as a resolution. TRUGS introduces a four-corner verification square: a validated JSON graph (TRUG), formal English comments (TRUG/L), implementation code, and a TRUG/L-annotated test matrix. Each corner validates against the others mechanically. We demonstrate the approach on a production system and argue that formal intermediate representations between intent and code are necessary for safe autonomous code generation.

---

## 1. Introduction

Code generation by large language models is no longer experimental. GitHub Copilot, Claude Code, Cursor, and Windsurf are used by millions of developers daily. These tools generate code faster than any human can write — and faster than any human can read.

This speed creates a new category of technical debt. We call it **Dark Code**: code that humans did not write and cannot follow the logic of or understand what the code is accomplishing.

Dark Code is not buggy code. It compiles. It passes tests. It ships to production. The problem is not correctness — it is legibility. When a human cannot follow the logic, they cannot:

- Audit it for security vulnerabilities
- Maintain it when requirements change
- Explain it when something goes wrong
- Take responsibility for its behavior

This paper makes one claim: **developing with TRUGS significantly resolves the Dark Code problem.** The TRUG graph creates the logical framework. TRUG/L inline comments make every line readable by both humans and machines. A mechanical validator enforces consistency. A TRUG/L-annotated test matrix closes the verification loop.

Together, these four components form a **verification square** where each corner validates against the others. Dark Code is code where any edge of this square is broken. TRUGS keeps all four edges mechanically verifiable.

---

## 2. The Dark Code Problem

### 2.1 Definition

Dark Code exists on a spectrum:

| Level | Description | Example |
|---|---|---|
| **Transparent** | Human dictated the logic, LLM typed it | "Write a function that sorts by date" |
| **Guided** | Human specified the architecture, LLM filled in details | Detailed spec → generated implementation |
| **Supervised** | Human reviewed and understood the output | PR review where human reads every line |
| **Opaque** | Human approved but didn't fully follow the logic | "Tests pass, audit clean, merge" |
| **Dark** | Human cannot follow the logic even if they tried | Complex generated code with emergent patterns |

Most LLM-assisted code lands in the Opaque-to-Dark range. The human provides a prompt, the LLM generates hundreds of lines, the human skims for obvious errors, and merges. The gap between what was generated and what was understood widens with every interaction.

### 2.2 Why It Is Inevitable

Dark Code accumulation is structural, not incidental. Three forces drive it:

**Speed asymmetry.** LLMs generate code at thousands of tokens per minute. Humans read code at tens of lines per minute. The generation-to-comprehension ratio is at least 10:1 and growing with each model generation. No amount of discipline closes this gap — it is a property of the medium.

**Review fatigue.** Studies of code review at scale (Bacchelli & Bird, 2013; Sadowski et al., 2018) show that review effectiveness drops with PR size and reviewer cognitive load. LLM-generated PRs are often larger (more files, more lines) and more frequent (faster generation cycles) than human-written PRs. The human reviewer's natural response is to trust the tests and approve.

**Trust transfer.** As LLMs prove reliable on small tasks, humans extend trust to larger tasks. "It got the sort function right, so the pipeline orchestration is probably fine too." This trust is rational locally but dangerous systemically — the human's mental model of the code diverges from the actual code, and the divergence is invisible.

### 2.3 Accumulation

Dark Code is monotonically increasing in any LLM-assisted codebase without structural intervention. Each session adds more generated code. Each session reduces the percentage of code the human has personally read and understood. Over months, the human's mental model covers an ever-shrinking fraction of the system.

This is not a problem that resolves itself. Dark Code does not become understood through time — it becomes normalized. The team stops expecting to understand every line. "The AI wrote it" becomes an acceptable answer to "why does this work this way?"

---

## 3. Why Existing Solutions Fail

### 3.1 Code Review

Code review is the primary defense against code quality issues. But code review assumes the reviewer can read and understand the code. When the code is LLM-generated:

- The reviewer did not write it and has no mental model of its design decisions
- The volume exceeds what careful review can handle
- The reviewer's incentive is to merge (blocked PRs slow the team) not to understand
- "Tests pass" becomes a proxy for "code is correct," which becomes a proxy for "I understand the code"

Code review catches surface issues (naming, style, obvious bugs) but cannot catch Dark Code — because Dark Code is correct code that nobody understands.

### 3.2 Documentation

Natural language documentation fails against Dark Code for three reasons:

1. **Ambiguity.** Natural language has multiple interpretations. "Shuffles the deck" does not specify the algorithm, the invariants, or the edge cases. Two readers extract different mental models from the same doc.

2. **No validation.** Documentation can say anything. There is no mechanical check that the docs match the code. The docs say "Fisher-Yates" while the code implements something subtly different, and nobody catches it.

3. **Decay.** Documentation diverges from code over time. The code changes; the docs don't. Within months, the docs describe a system that no longer exists.

4. **Recursive darkness.** When LLMs generate documentation alongside code, you get LLM-generated docs explaining LLM-generated code. The documentation is as dark as the code it describes.

### 3.3 Testing

Testing verifies behavior, not understanding. A test suite with 100% code coverage proves that every branch executes — it does not prove that a human understands why any branch exists.

Worse, tests themselves can be Dark Code. An LLM generates a test that asserts `result == expected_value`. The test passes. But:

- Why is `expected_value` the correct value?
- What requirement does this test verify?
- What does the test NOT cover?
- Is the test testing the right thing, or testing the LLM's assumptions?

Green checkmarks create false confidence. The human sees "47 tests pass" and infers "the code works." The inference is valid for correctness. It is not valid for understanding.

### 3.4 Static Analysis

Static analysis tools (linters, type checkers, security scanners) catch patterns. They detect unused variables, type mismatches, known vulnerability patterns, and style violations. What they cannot detect is intent.

A linter does not know why the code exists. It does not know that the shuffle must be Fisher-Yates (not a naive shuffle) because uniform randomness matters. It does not know that the cut card must be placed 60-80 cards from the end. It does not know that the burn card is a casino convention, not a mathematical requirement.

Static analysis catches Dark Bugs in Dark Code. It does not make Dark Code legible.

### 3.5 AI Auditing AI

The most tempting solution is to use one LLM to audit another LLM's code. The code generator writes the implementation; an auditor model reviews it. This is the pattern used by autonomous development systems with cyclic audit phases.

The problem: the human sees "audit passed" but cannot verify the audit. The auditor model may have the same blind spots as the generator model. The audit report is itself generated text — it can be wrong, misleading, or simply parroting the code.

AI auditing AI is machines validating machines. It may catch errors (and empirically, it does). But it does not make the code less dark. It adds a layer of dark validation on top of dark code.

---

## 4. The TRUGS Solution: Four-Corner Verification Square

TRUGS (Traceable Recursive Universal Graph Specification) introduces a formal intermediate representation between intent and code. The representation has three components, which combined with code form a four-corner verification square.

### 4.1 Corner 1: The TRUG Graph

A TRUG is a JSON document with three components: **nodes** (typed things), **edges** (named relationships), and **hierarchy** (parent/child containment with metric levels).

Every node has 7 required fields:

```json
{
  "id": "stage_shuffle",
  "type": "STAGE",
  "properties": {
    "name": "Fisher-Yates Shuffle",
    "algorithm": "Fisher-Yates (Knuth)",
    "trl": "PROCESS shuffle SHALL SORT DATA shoe BY RANDOM ONCE."
  },
  "parent_id": "shoe",
  "contains": [],
  "metric_level": "BASE_STAGE",
  "dimension": "shuffle"
}
```

Every edge has 3 required fields:

```json
{
  "from_id": "stage_build",
  "to_id": "stage_shuffle",
  "relation": "FEEDS"
}
```

16 validation rules enforce structural integrity mechanically. The TRUG is the architecture document — machine-readable, validated, and always current. Any agent or human can traverse the graph to understand the system's structure without reading a single line of implementation code.

### 4.2 Corner 2: TRUG/L Inline Comments

TRUGS Language (TRUG/L) is a formalized subset of English with 190 executable words. Every valid sentence compiles to a directed graph. Every word has exactly one meaning. The vocabulary is drawn from computation and law:

- **Nouns** (26): PROCESS, SERVICE, DATA, RECORD, ENDPOINT, ...
- **Verbs** (61): FILTER, SORT, WRITE, VALIDATE, ASSERT, ...
- **Modals** (3): SHALL (must), MAY (allowed), SHALL_NOT (prohibited)
- **Adjectives** (36): ACTIVE, VALID, UNIQUE, REQUIRED, ...
- **Prepositions** (18): FEEDS, DEPENDS_ON, IMPLEMENTS, CONTAINS, ...

A TRUG/L comment is placed above every code block:

```python
# PROCESS shuffle SHALL SORT DATA shoe BY RANDOM ONCE.
# EACH DATA card SHALL EXIST 'at EXACTLY A UNIQUE RECORD position.
# RESULT SHALL CONTAIN 416 DATA card.
def shuffle_shoe(shoe: list[Card], rng: random.Random | None = None) -> list[Card]:
    ...
```

The comment is not a description — it is a **compilable specification**. It has exactly one interpretation. It can be validated against the TRUG graph (does the comment match the node?) and against the code (does the implementation satisfy the specification?).

TRUG/L comments replace natural language documentation with formal English that both humans and machines can parse unambiguously.

### 4.3 Corner 3: Implementation Code

The code implements the TRUG through the TRUG/L comments. Each function corresponds to a TRUG node. Each function's behavior satisfies its TRUG/L specification. The code is still code — it can still be complex, optimized, or algorithmically sophisticated. The difference is that every function has an explicit, formal statement of what it is supposed to do.

The code between TRUG/L comments can still be opaque. A complex algorithm is still complex. But the *intent* of every code block is explicit, validated, and traceable to the TRUG graph. This is the distinction between Dark Code (no legible intent) and complex code (legible intent, complex implementation).

### 4.4 Corner 4: TRUG/L-Annotated Test Matrix

Every test function gets a TRUG/L comment stating what it verifies:

```python
# AGENT SHALL VALIDATE STAGE shuffle — RESULT SHALL CONTAIN ALL DATA card.
# NO DATA card SHALL 'be ADDED OR REMOVED.
def test_shuffle_preserves_cards():
    ...
```

The test matrix as a TRUG graph has three node types and two edge types:

- **TEST** nodes with TRUG/L intent comments
- **FUNCTION** nodes (code under test)
- **SPEC** nodes (requirements)
- TEST `VALIDATES` FUNCTION — this test exercises this function
- TEST `IMPLEMENTS` SPEC — this test verifies this requirement

This structure enables:

- **Coverage gap detection** — SPEC nodes with no inbound TEST edges are untested requirements. Visible without reading any code.
- **Dark test detection** — TEST nodes without TRUG/L comments are dark tests. Flagged automatically.
- **Test-to-requirement traceability** — "Are all requirements tested?" is a graph query, not a manual audit.
- **Impact analysis** — When code changes, follow VALIDATES edges backward to find all affected tests.

### 4.5 The Verification Square

The four corners form a square where each edge is a mechanical validation:

```
      TRUG (structure)
     /       \
    TRUG/L       Code
  (intent)  (implementation)
     \       /
      Tests
   (verification)
```

| Edge | Validation |
|---|---|
| TRUG ↔ Code | Does the code implement the graph? (function-to-node mapping) |
| TRUG ↔ TRUG/L | Do the comments match the graph? (TRUG/L compiles to TRUG subgraph) |
| TRUG ↔ Tests | Does the test matrix cover the graph? (SPEC node coverage) |
| TRUG/L ↔ Tests | Does each test's TRUG/L match the code's TRUG/L it verifies? (intent alignment) |
| Code ↔ Tests | Do the tests pass? (behavioral verification) |
| TRUG/L ↔ Code | Does the implementation satisfy the TRUG/L specification? (specification compliance) |

**Dark Code is code where any edge of this square is broken or missing.** TRUGS keeps all edges mechanically verifiable. The human does not need to read the code — they read the TRUG, verify the TRUG/L makes sense, and confirm the validator reports all edges intact.

---

## 5. How to Code with TRUGS: Outline First, Then Write

Writing code with TRUGS is like writing a paper. You don't start with the first sentence — you start with the outline. The outline captures the structure: what the major sections are, how they relate, what each one accomplishes. Once the outline is solid, writing the prose is straightforward — you're filling in a skeleton that already makes sense.

TRUG-first development follows the same principle. The TRUG is the outline. The code is the prose.

We demonstrate this with a concrete example: shuffling an 8-deck casino shoe. We chose this problem because it is universally understood (everyone knows what shuffling a deck of cards means), short enough to fit in a paper, yet complicated enough to reveal the Dark Code problem. A casino shoe has domain conventions (cut cards, burn cards, specific deck counts) that are invisible in naive implementations and critical for correctness.

### 5.1 What Dark Code Looks Like

Before showing the TRUG approach, consider what an LLM produces when asked to shuffle a casino shoe:

```python
import random

def shuffle_shoe(n_decks=8):
    suits = ['H', 'D', 'C', 'S']
    ranks = ['A'] + [str(i) for i in range(2, 11)] + ['J', 'Q', 'K']
    shoe = [(r, s) for _ in range(n_decks) for s in suits for r in ranks]
    for i in range(len(shoe) - 1, 0, -1):
        j = random.randint(0, i)
        shoe[i], shoe[j] = shoe[j], shoe[i]
    return shoe
```

This is 8 lines. It compiles. It probably works. A human reads it and thinks: "Looks like Fisher-Yates, tests pass, merge."

But what is missing?

- The algorithm is unnamed. You recognize Fisher-Yates or you don't.
- No invariant assertions. Is the shoe 416 cards? Are there 32 of each rank?
- No cut card. In a real casino shoe, a cut card is placed 60-80 cards from the end to determine when to reshuffle.
- No burn card. The first card is dealt face-down and discarded.
- The RNG is unseeded. Tests are not reproducible.
- The function does everything in one block. Build, shuffle, cut, and burn are conflated into a single function with no separation of concerns.

A different LLM editing this later has no idea what invariants matter, what domain conventions apply, or where the boundaries between stages are. This is Dark Code — correct code that nobody can maintain, audit, or extend with confidence.

### 5.2 Step 1: Write the TRUG — The Macro Flow

Before writing any code, write the TRUG. The first pass captures the top-level structure: what are the major components, and how does data flow between them?

This is the equivalent of a paper's section headings. You are not thinking about implementation. You are thinking about architecture — the shape of the system.

For the shoe shuffle, the first pass is:

```
stage_build → stage_shuffle → stage_cut → stage_burn
```

Four nodes. Three FEEDS edges. This is the entire pipeline at the macro scale. A human reading this knows what the system does without any code, any detail, any implementation. Build a shoe, shuffle it, place the cut card, burn the first card.

Write this as a TRUG:

```json
{
  "nodes": [
    {"id": "stage_build",   "type": "STAGE", "properties": {"order": 1}},
    {"id": "stage_shuffle", "type": "STAGE", "properties": {"order": 2}},
    {"id": "stage_cut",     "type": "STAGE", "properties": {"order": 3}},
    {"id": "stage_burn",    "type": "STAGE", "properties": {"order": 4}}
  ],
  "edges": [
    {"from_id": "stage_build",   "to_id": "stage_shuffle", "relation": "FEEDS"},
    {"from_id": "stage_shuffle", "to_id": "stage_cut",     "relation": "FEEDS"},
    {"from_id": "stage_cut",     "to_id": "stage_burn",    "relation": "FEEDS"}
  ]
}
```

This takes two minutes. It forces you to think about the flow before you think about the implementation. Most design mistakes are structural — wrong decomposition, missing stages, tangled dependencies. The TRUG catches these at the outline level, when they are cheap to fix.

Notice what the outline already reveals that the Dark Code version hides: there are four stages, not one. The cut card and burn card are explicit stages, not afterthoughts. The data flows in one direction. A human reviewing this outline can immediately ask: "Where does the cut card go? What are the invariants?" — questions that are invisible in the 8-line Dark Code version.

### 5.3 Step 2: Clarify the Dependent Flows

The second pass adds detail to each node. What does `stage_build` actually produce? What invariants does `stage_shuffle` maintain? What are the parameters of `stage_cut`?

This is the equivalent of writing topic sentences for each section of a paper. You are still not writing code. You are specifying what each component does, in TRUG/L:

```json
{
  "id": "stage_build",
  "type": "STAGE",
  "properties": {
    "trl": "PROCESS build SHALL DEFINE DATA shoe AS 8 MULTIPLE DATA deck. EACH DATA deck CONTAINS 52 UNIQUE DATA card.",
    "invariant_card_count": 416,
    "invariant_per_rank": 32,
    "invariant_per_suit": 104
  }
}
```

```json
{
  "id": "stage_shuffle",
  "type": "STAGE",
  "properties": {
    "trl": "PROCESS shuffle SHALL SORT DATA shoe BY RANDOM ONCE. EACH DATA card SHALL EXIST 'at EXACTLY A UNIQUE RECORD position.",
    "algorithm": "Fisher-Yates (Knuth)"
  }
}
```

```json
{
  "id": "stage_cut",
  "type": "STAGE",
  "properties": {
    "trl": "PROCESS cut SHALL SPLIT DATA shoe 'at RECORD position BETWEEN 336 AND 356.",
    "cut_range_from_end": [60, 80]
  }
}
```

```json
{
  "id": "stage_burn",
  "type": "STAGE",
  "properties": {
    "trl": "PROCESS burn SHALL TAKE 1 DATA card FROM ENTRY shoe THEN WRITE RESULT TO DATA discard."
  }
}
```

Now each node has a TRUG/L specification — a formal English sentence that says exactly what the stage does. The invariants are explicit. The algorithm is named. The cut card range is specified. A human reading the TRUG at this level understands the complete system specification without any code.

If there are dependencies within a stage — sub-steps, helper functions, internal data transformations — add child nodes and edges within the stage. The TRUG hierarchy (parent_id, contains) supports arbitrary nesting. Clarify the dependent flows until every decision point has a TRUG/L specification.

### 5.4 Step 3: Write the Code as You Write the TRUG/L

Once the TRUG maps the code, writing the implementation is the final step — not the first. Each TRUG node becomes a function. Each node's TRUG/L specification becomes the function's inline comment. The code implements the comment.

The process is simultaneous: write the TRUG/L comment, then write the code that satisfies it. TRUG/L comments appear at two levels — **function-level comments** state what the function does (from the TRUG node's TRUG/L property), and **inline comments** annotate the logic within the function so that every significant line is readable:

```python
import random
from dataclasses import dataclass

# DEFINE DATA suit AS 4 UNIQUE STRING.
SUITS = ('H', 'D', 'C', 'S')
# DEFINE DATA rank AS 13 UNIQUE STRING.
RANKS = ('A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K')

# DEFINE DATA card AS RECORD CONTAINS RECORD rank AND RECORD suit.
@dataclass(frozen=True)
class Card:
    rank: str
    suit: str

# PROCESS build SHALL DEFINE DATA shoe AS 8 MULTIPLE DATA deck.
# EACH DATA deck CONTAINS 52 UNIQUE DATA card.
def build_shoe(n_decks: int = 8) -> list[Card]:
    # MAP EACH DATA deck TO ALL DATA card — 8 decks × 4 suits × 13 ranks
    shoe = [Card(r, s) for _ in range(n_decks) for s in SUITS for r in RANKS]
    # ASSERT RECORD invariant_card_count — shoe SHALL CONTAIN n_decks × 52 DATA card
    assert len(shoe) == n_decks * 52
    return shoe

# PROCESS shuffle SHALL SORT DATA shoe BY RANDOM ONCE.
# EACH DATA card SHALL EXIST 'at EXACTLY A UNIQUE RECORD position.
# RESULT SHALL CONTAIN 416 DATA card.
def shuffle_shoe(shoe: list[Card], rng: random.Random | None = None) -> list[Card]:
    rng = rng or random.Random()
    # PROCESS copy — SHALL_NOT MODIFY SOURCE DATA shoe
    shuffled = shoe.copy()
    # Fisher-Yates: EACH RECORD position RECEIVES A RANDOM DATA card FROM REMAINING
    for i in range(len(shuffled) - 1, 0, -1):
        j = rng.randint(0, i)  # RANDOM INTEGER BETWEEN 0 AND i INCLUSIVE
        shuffled[i], shuffled[j] = shuffled[j], shuffled[i]  # SWAP positions i AND j
    # ASSERT RECORD invariant — NO DATA card ADDED OR REMOVED
    assert len(shuffled) == len(shoe)
    return shuffled

# PROCESS cut SHALL SPLIT DATA shoe 'at RECORD position BETWEEN 336 AND 356.
# DATA cut_card DEFINES ENDPOINT shoe_end.
def place_cut_card(shoe: list[Card], rng: random.Random | None = None,
                   cut_range: tuple[int, int] = (60, 80)) -> int:
    rng = rng or random.Random()
    # RANDOM INTEGER cards FROM ENTRY end — dealer places cut card 60-80 from back
    cards_from_end = rng.randint(cut_range[0], cut_range[1])
    # RESULT 'is RECORD position — cards AFTER THIS POSITION SHALL_NOT 'be DEALT
    return len(shoe) - cards_from_end

# PROCESS burn SHALL TAKE 1 DATA card FROM ENTRY shoe
# THEN WRITE RESULT TO DATA discard.
def burn_card(shoe: list[Card]) -> tuple[list[Card], Card]:
    # TAKE ENTRY card — first card dealt face-down, not played
    return shoe[1:], shoe[0]
```

Notice the two levels of TRUG/L commenting:

1. **Function-level** (above the `def`): States the function's purpose, directly from the TRUG node's TRUG/L property. This is the specification — what the function SHALL do.

2. **Inline** (within the function): Annotates the implementation logic so that every significant line has a formal explanation. `# Fisher-Yates: EACH RECORD position RECEIVES A RANDOM DATA card FROM REMAINING` tells the reader both the algorithm name and what the line accomplishes in TRUG/L vocabulary.

A human reading this code can follow the logic at two speeds: skim the function-level TRUG/L to understand the pipeline, or read the inline TRUG/L to understand every step. An LLM modifying this code has formal specifications at both levels — it knows what the function must do and why each line exists.

The TRUG/L comment came from the TRUG. The code implements the comment. The assertions enforce the invariants from the TRUG properties. The three artifacts — TRUG node, TRUG/L comment, code — are written in that order and are mechanically traceable.

### 5.5 Step 4: Write TRUG/L-Commented Tests

The same principle applies to tests. Each test gets a TRUG/L comment stating what it verifies — not in natural language ("test shuffle works") but in formal English that names the specific invariant or property being validated:

```python
# AGENT SHALL VALIDATE STAGE build SUBJECT_TO RECORD invariant_card_count.
# ASSERT DATA shoe CONTAINS 416 DATA card.
def test_build_shoe_card_count():
    shoe = build_shoe(8)
    assert len(shoe) == 416

# AGENT SHALL VALIDATE STAGE build SUBJECT_TO RECORD invariant_per_rank.
# EACH RECORD rank SHALL EXIST 32 MULTIPLE 'in DATA shoe.
def test_build_shoe_rank_distribution():
    shoe = build_shoe(8)
    from collections import Counter
    rank_counts = Counter(c.rank for c in shoe)
    # ASSERT EACH RECORD rank — 8 decks × 4 suits = 32 of each rank
    assert all(count == 32 for count in rank_counts.values())

# AGENT SHALL VALIDATE STAGE build SUBJECT_TO RECORD invariant_per_suit.
# EACH RECORD suit SHALL EXIST 104 MULTIPLE 'in DATA shoe.
def test_build_shoe_suit_distribution():
    shoe = build_shoe(8)
    from collections import Counter
    suit_counts = Counter(c.suit for c in shoe)
    # ASSERT EACH RECORD suit — 8 decks × 13 ranks = 104 of each suit
    assert all(count == 104 for count in suit_counts.values())

# AGENT SHALL VALIDATE STAGE shuffle — RESULT SHALL CONTAIN ALL DATA card.
# NO DATA card SHALL 'be ADDED OR REMOVED.
def test_shuffle_preserves_cards():
    rng = random.Random(42)
    shoe = build_shoe(8)
    shuffled = shuffle_shoe(shoe, rng)
    # SORT both BY suit AND rank — ASSERT identical multisets
    assert sorted(shuffled, key=lambda c: (c.suit, c.rank)) == \
           sorted(shoe, key=lambda c: (c.suit, c.rank))

# AGENT SHALL VALIDATE STAGE shuffle — RESULT SHALL_NOT EQUAL DATA shoe.
# PROCESS shuffle SHALL SORT DATA shoe BY RANDOM (not identity).
def test_shuffle_changes_order():
    rng = random.Random(42)
    shoe = build_shoe(8)
    shuffled = shuffle_shoe(shoe, rng)
    # ASSERT shuffled order DIFFERS — probability of identity is ~1/416!
    assert shuffled != shoe

# AGENT SHALL VALIDATE STAGE shuffle — PROCESS shuffle SHALL 'be UNIFORM.
# EACH RECORD position SHALL RECEIVE EACH DATA card 'with EQUAL RECORD probability.
def test_shuffle_uniformity():
    """Statistical test: 10,000 shuffles, verify first-position distribution."""
    rng = random.Random(42)
    shoe = build_shoe(1)  # single deck for tractability
    first_card_counts = {}
    for _ in range(10_000):
        shuffled = shuffle_shoe(shoe, rng)
        first_card_counts[shuffled[0]] = first_card_counts.get(shuffled[0], 0) + 1
    expected = 10_000 / 52
    # ASSERT NO DATA card EXCEEDS 2.5× expected frequency — chi-squared proxy
    assert all(count < expected * 2.5 for count in first_card_counts.values())

# AGENT SHALL VALIDATE STAGE cut — RECORD cut_position BETWEEN 336 AND 356.
def test_cut_card_range():
    rng = random.Random(42)
    shoe = build_shoe(8)
    for _ in range(100):
        pos = place_cut_card(shoe, rng)
        # ASSERT position — 416 - 80 = 336 to 416 - 60 = 356
        assert 336 <= pos <= 356, f"Cut at {pos}, expected 336-356"

# AGENT SHALL VALIDATE STAGE burn — RESULT SHALL CONTAIN 415 DATA card.
# DATA burned SHALL EQUAL ENTRY card 'of DATA shoe.
def test_burn_card():
    shoe = build_shoe(8)
    shuffled = shuffle_shoe(shoe, random.Random(42))
    remaining, burned = burn_card(shuffled)
    # ASSERT card count — 416 minus 1 burned = 415
    assert len(remaining) == 415
    # ASSERT burned card identity — SHALL EQUAL first card of shuffled shoe
    assert burned == shuffled[0]
```

A human reading only the TRUG/L comments sees the complete test matrix: build (3 invariants: card count, rank distribution, suit distribution), shuffle (3 properties: card preservation, order change, uniformity), cut (position range), burn (count + identity). Coverage gaps are visible by comparing test TRUG/L to TRUG stages — every stage has at least one test, every invariant has an assertion.

### 5.6 Why This Order Matters

Writing code first and adding documentation later is how Dark Code is born. The code exists without a specification. The documentation (if it comes at all) describes what the code does — not what it was supposed to do. The gap between intent and implementation is invisible because intent was never recorded.

Writing the TRUG first inverts this:

1. **TRUG** captures intent at the architectural level (what are the pieces, how do they connect)
2. **TRUG/L** captures intent at the function level (what does each piece do, formally)
3. **TRUG/L inline** captures intent at the line level (why does each line exist)
4. **Code** implements the intent (how does it do it)
5. **Tests with TRUG/L** verify the intent (does it actually do it, and which invariant does each test check)

At every step, intent precedes implementation. The human reads the intent chain (TRUG → TRUG/L → inline TRUG/L) and trusts the implementation chain (Code → Tests) because both are mechanically validated against the same specification.

### 5.7 The Complete Comparison

| Aspect | Dark Version (8 lines) | TRUG Version |
|---|---|---|
| Card count invariant | Implicit (count the loop) | Explicit in TRUG properties, asserted in code, tested |
| Algorithm identity | Unnamed | Named: "Fisher-Yates (Knuth)" in TRUG, comment, and inline |
| Cut card | Not implemented | TRUG stage, function, range specified, tested |
| Burn card | Not implemented | TRUG stage, function, tested |
| Reproducibility | Unseeded `random.randint` | Injectable `rng` parameter |
| Function-level intent | None | TRUG/L comment on every function |
| Line-level intent | None | TRUG/L inline comment on every significant line |
| Test intent | "test_shuffle works" | Each test names the specific invariant it verifies |
| Test coverage visibility | Unknown | TRUG stages map to tests; gaps are visible |
| Next developer | Reads code, guesses intent | Reads TRUG, understands pipeline; reads TRUG/L, understands every line |

The Dark version is 8 lines and a liability — every future interaction with it requires re-understanding. The TRUG version is more code and an asset — the understanding is embedded in the structure at three levels (architecture, function, line) and never decays.

This is why TRUG-first development produces legible code where code-first development produces Dark Code. The outline exists before the prose. The specification exists before the implementation. The structure is legible because it was designed to be legible — not reverse-engineered from code that was designed to run.

---

## 6. The Test Matrix: From Dark Tests to Verified Coverage

### 6.1 The Dark Test Problem

Tests are the last line of defense — but they are also the most dangerous vector for false confidence. When an LLM generates tests alongside code:

- The tests verify the LLM's interpretation, not the human's requirements
- The tests may encode the LLM's assumptions as assertions
- "All tests pass" creates confidence that the code is correct — but nobody verified that the tests are correct
- The tests themselves are Dark Code

A test suite with 100% coverage and all green is not evidence of understanding. It is evidence that the LLM's code is consistent with the LLM's tests. This is tautological, not informative.

### 6.2 TRUG/L-Commented Tests

Adding a TRUG/L comment to every test function breaks the tautology:

```python
# AGENT SHALL VALIDATE STAGE shuffle — PROCESS shuffle SHALL 'be UNIFORM.
# EACH RECORD position SHALL RECEIVE EACH DATA card 'with EQUAL RECORD probability.
def test_shuffle_uniformity():
    ...
```

The TRUG/L comment is a claim about what the test verifies. A human reading the comment can evaluate whether that claim matches the requirement. If the requirement says "uniform shuffle" and the TRUG/L says `SHALL 'be UNIFORM`, the intent is aligned. If the test implementation actually verifies uniformity (via statistical test), the triangle closes.

A test without a TRUG/L comment is a dark test. A test with a TRUG/L comment that doesn't match the implementation is a broken test. Both are mechanically detectable.

### 6.3 The Test Matrix as TRUG

When the test matrix is itself a TRUG graph, verification becomes structural:

- **SPEC** nodes with no inbound TEST `IMPLEMENTS` edges → untested requirements
- **TEST** nodes without TRUG/L comments → dark tests
- **FUNCTION** nodes with no inbound TEST `VALIDATES` edges → untested code
- Multiple TEST nodes with similar TRUG/L against the same FUNCTION → redundancy candidates

"Are all requirements tested?" is a graph query: `FILTER ALL SPEC WHERE NO TEST IMPLEMENTS SELF`. The answer is a list of node IDs, not a judgment call.

---

## 7. The Self-Referential Problem

In an autogenous system — a system that builds itself — Dark Code compounds across layers. The system generates code that generates code. Each layer is potentially darker than the last.

Consider: an LLM agent writes a code generator. The generator writes application code. The application code processes user input. Three layers of code, each written by a different process, each potentially dark to the humans responsible for the system.

TRUGS addresses this through **TRUG chains**: each layer has its own TRUG graph. The human audits the chain of TRUGs, not the chain of code. Each TRUG decompiles to formal English via TRUG/L. The chain of English is human-readable even when the chain of code is not.

```
Layer 0 TRUG → Layer 0 Code → produces → Layer 1 TRUG → Layer 1 Code → produces → Layer 2 TRUG → ...
```

The human reads: Layer 0 TRUG, Layer 1 TRUG, Layer 2 TRUG. If each TRUG makes sense and the validator confirms each TRUG matches its code, the system is legible — even though no human has read the implementation at any layer.

This is the structural argument for TRUG-first development in autonomous systems. The TRUG is not documentation added after the fact. It is the specification written before the code, validated during development, and maintained as the code evolves.

---

## 8. The Economics of Dark Code

### 8.1 Maintenance Cost

Dark Code maintenance costs more than understood code because the fix cycle is: regenerate, not repair. When code breaks and nobody understands it, the response is to ask the LLM to rewrite it. The rewrite produces new Dark Code. The system accumulates layers of regenerated Dark Code, each overwriting the last, with no human understanding at any point.

TRUGS breaks this cycle. When code breaks, the human reads the TRUG to understand what the code was supposed to do. The fix targets the divergence between the TRUG specification and the implementation — a specific, bounded repair rather than a wholesale regeneration.

### 8.2 Security Cost

Security vulnerabilities in Dark Code are invisible. You cannot audit what you cannot read. An LLM may generate code with subtle vulnerabilities — race conditions, injection vectors, cryptographic weaknesses — that pass all tests and all automated scanners.

The TRUG does not eliminate security vulnerabilities. But it makes the attack surface legible. Each node in the TRUG is a component with explicit inputs, outputs, and relationships. Security review becomes: "for each ENDPOINT node, what validates its inputs?" — a graph traversal, not a line-by-line code audit.

### 8.3 Liability Cost

Legal liability for Dark Code is an unresolved question. When autonomously generated code causes harm, the liability chain is unclear. The human approved the PR — but they didn't understand the code. The LLM generated it — but LLM providers disclaim liability for outputs. The company ships it — but no employee wrote it.

TRUGS provides an audit trail: the TRUG specification (what was intended), the TRUG/L comments (what was specified), the validator results (whether specification matched implementation), and the HITM approval records (who approved what, when). This does not resolve the legal question, but it provides the evidence that any resolution would require.

---

## 9. Limitations

**TRUGS reduces Dark Code; it does not eliminate it.** The implementation between TRUG/L comments can still be opaque. A complex algorithm is still complex. The four-corner square verifies structure and intent, not every line of logic. The claim is legibility of intent, not legibility of implementation.

**TRUG/L has 190 words.** Some domains may need branch extensions. The vocabulary is a closed set; extending it requires formal specification. Counter: 190 words cover computation, data flow, obligations, permissions, and prohibitions — sufficient for most software systems.

**Adoption has a cost.** Developers must learn TRUG/L (190 words) and TRUG structure (7 node fields, 3 edge fields). This is learnable in a day but is a nonzero cost. Counter: the alternative is unbounded Dark Code accumulation with escalating maintenance, security, and liability costs.

**The validator enforces structure, not semantics.** The validator can confirm that a TRUG/L comment compiles to a valid TRUG subgraph. It cannot confirm that the TRUG/L comment accurately describes the code's behavior. Semantic verification remains a human (or AI auditor) responsibility — but the TRUG/L comment gives them something formal to verify against, rather than nothing.

---

## 10. Related Work

**Literate Programming** (Knuth, 1984). Knuth proposed interweaving code and documentation in a single document. TRUGS shares the goal of co-locating intent with implementation but differs in three ways: TRUG/L is formal (not prose), TRUG/L is validated (not advisory), and TRUG/L compiles to a machine-readable graph (not a typeset document).

**Design by Contract** (Meyer, 1986). Preconditions, postconditions, and invariants specify function behavior formally. TRUGS extends this from the function level to the system level: the TRUG graph is a contract for the entire architecture, not just individual functions.

**Controlled Natural Languages** (Kuhn, 2014). CNLs restrict natural language to enable formal interpretation. TRUG/L is a CNL optimized for graph compilation: its 190 words map to nodes, edges, and operations in a TRUG graph. Unlike Attempto or PENG, TRUG/L targets directed graphs rather than first-order logic.

**Model-Driven Development** (UML, SysML, Eclipse Modeling Framework). MDD uses visual models as the primary artifact. TRUGS replaces heavyweight visual modeling with lightweight JSON and formal English. No special tools are required — any text editor works. The TRUG is a text file, not a diagram.

**AI Interpretability** (Christiano et al., 2017; Anthropic interpretability team). The Dark Code problem is an interpretability problem at the code level: understanding what a system does and why. TRUGS provides structural interpretability through the four-corner verification square — the system's intent is explicit, formal, and mechanically verifiable.

---

## 11. Conclusion

Dark Code is the inevitable consequence of LLM-assisted development. Code is generated faster than it can be understood. Existing mitigations — review, documentation, testing, analysis, AI auditing — address symptoms without resolving the structural cause.

The structural cause is the absence of a formal intermediate representation between human intent and machine-generated code. Without such a representation, intent lives in the human's head (or in ambiguous natural language) and code lives in the repository. The gap between them is Dark Code.

TRUGS provides the intermediate representation: a validated JSON graph (TRUG) with formal English annotations (TRUG/L), mechanical consistency validation, and a TRUG/L-annotated test matrix. Together, these form a four-corner verification square where each corner validates against the others. The human reads the TRUG and TRUG/L — not the code. If the formal English makes sense and the validator confirms consistency, the code is understood in intent even if the implementation is complex.

### 11.1 TRUGS as a Development Framework for LLMs

The value of TRUGS extends beyond reducing Dark Code for human readers. The TRUG and TRUG/L also serve as a **supporting framework for the LLM itself** — both when generating code initially and when returning to modify it later.

When an LLM generates code without a TRUG, it works from a natural language prompt and its training distribution. The output is statistically likely to be correct but carries no structural guarantee that the code matches the user's intent, maintains domain invariants, or preserves the design decisions of the existing codebase. Each generation is independent — the LLM has no memory of why the code was written this way.

When an LLM generates code with a TRUG, the situation is fundamentally different:

**During initial development**, the TRUG constrains the LLM's output. The LLM is not generating code from a vague prompt — it is implementing a validated graph with formal TRUG/L specifications at every node. Each function has a stated purpose. Each invariant is explicit. The LLM's task shifts from "write code that probably does what the user means" to "implement this specific TRUG/L specification." The specification is unambiguous (190 words, each with one meaning), so the LLM's output is verifiable against a formal target rather than a fuzzy intent.

**During future modifications**, the TRUG serves as the context that the LLM otherwise lacks. When a different LLM (or the same LLM in a new session) returns to modify the code, it reads:

1. **The TRUG graph** — the architecture of the system, all components and their relationships. The LLM immediately knows what exists, what depends on what, and where the boundaries are.
2. **The function-level TRUG/L comments** — what each function is supposed to do, formally. The LLM knows the specification before it reads the implementation.
3. **The inline TRUG/L comments** — why each line exists. The LLM can distinguish between lines that are load-bearing (they satisfy a TRUG/L specification) and lines that are incidental (implementation details that could change).
4. **The test TRUG/L comments** — what each test verifies. The LLM knows which invariants are enforced and can ensure modifications don't break them.

This means the LLM can make targeted changes rather than wholesale regeneration. Consider our shoe shuffle example: if the requirement changes from an 8-deck shoe to a 6-deck shoe, the LLM reads the TRUG node (`invariant_card_count: 416`) and the TRUG/L (`PROCESS build SHALL DEFINE DATA shoe AS 8 MULTIPLE DATA deck`), updates both to 6 decks and 312 cards, modifies the code to match, and updates the test assertions. Every change is traceable to a TRUG node. No other code is touched. No invariants are silently broken.

Without the TRUG, the same modification is dangerous. The LLM changes `n_decks=8` to `n_decks=6` in the function signature. But does it find the cut card range (which was calculated for 416 cards)? Does it update the test that asserts 416? Does it know that 32-per-rank changes to 24-per-rank? These are implicit dependencies in Dark Code. They are explicit edges in the TRUG.

**The TRUG is not just documentation for humans — it is a development scaffold for LLMs.** It gives the LLM the same structural understanding that a senior developer carries in their head: what the components are, how they relate, what invariants matter, and where the boundaries are. The difference is that the TRUG is explicit, validated, and permanent — it does not degrade across sessions, models, or context windows.

### 11.2 Two Audiences, One Structure

This dual audience — humans and LLMs — is the core insight. Traditional documentation serves humans. Traditional code serves machines. TRUGS serves both simultaneously:

- **Humans** read the TRUG to understand architecture, read TRUG/L to understand intent, and trust the validator to confirm consistency. They never need to read the implementation to understand what the system does.
- **LLMs** read the TRUG to understand scope, read TRUG/L to understand specifications, and use both as constraints during generation. They produce code that is structurally aligned with the existing system rather than statistically plausible.

The four-corner verification square works because all four corners are readable by both audiences. The TRUG is JSON (machine-native, human-readable). TRUG/L is formal English (human-native, machine-parseable). Code is code. Tests are code with TRUG/L annotations. Every artifact serves both readers.

### 11.3 The Choice

The cost of the TRUG approach is nonzero: a 190-word vocabulary, a 10-field node structure, and the discipline to write specifications before code. The cost of the alternative — unbounded Dark Code accumulation in every LLM-assisted codebase — is structural illegibility, unauditable security, unmaintainable systems, and unresolvable liability.

The four-corner verification square is the minimum viable framework for safe autonomous code generation. As LLMs write more of our code, we must choose: slow down generation, or make generation legible. TRUGS chooses the second path — and in doing so, it gives both the human and the LLM the structure they need to build, understand, and maintain software together.

---

## References

- Bacchelli, A., & Bird, C. (2013). Expectations, outcomes, and challenges of modern code review. *ICSE*.
- Christiano, P., et al. (2017). Deep reinforcement learning from human feedback. *NeurIPS*.
- Knuth, D. (1984). Literate programming. *The Computer Journal*, 27(2).
- Kuhn, T. (2014). A survey and classification of controlled natural languages. *Computational Linguistics*, 40(1).
- Meyer, B. (1986). Design by contract. *Technical Report TR-EI-12/CO, ISE*.
- Sadowski, C., et al. (2018). Modern code review: A case study at Google. *ICSE-SEIP*.
