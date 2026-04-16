# How to Code with TRUGS

**Authors:** Xepayac
**Date:** April 2026
**Venue:** Companion to `PAPER_dark_code.md` (TRUGS-LLC/TRUGS/REFERENCE/)
**Audience:** practitioners about to write or refactor code under TRUGS-LLC

---

## Abstract

`PAPER_dark_code.md` established the problem — LLM-generated code accumulates as Dark Code: correct, tested, opaque — and proposed TRUGS (Traceable Recursive Universal Graph Specification) as the structural fix. That paper argues the theory. This paper teaches the practice. It covers how to start a project TRUG-first, how to refactor existing dark code into compliance, how compliance composes across files and modules, how the AAA development protocol wraps the day-to-day work, how memory captures intent over time, how CI enforces the gates, and what patterns and anti-patterns practitioners encounter. It then specifies the Python dialect conventions that the `trugs-compliance-check` tool audits against.

Readers who have not read `PAPER_dark_code.md` will miss the *why*. Readers who have read it and now want to write TRUGS code start here.

---

## 1. Overview

TRUGS-compliant development has one simple principle: **intent precedes implementation, at every scale.** The architectural intent (which functions exist, how they relate) is captured in a TRUG graph. The function-level intent (what each function must do) is captured in a formal TRUG/L comment derived from the graph. The line-level intent (why this specific line exists) is captured in inline TRUG/L comments. The verification intent (which invariant does this test check) is captured in a TRUG/L comment on every test function.

Code is written to satisfy intent that has already been recorded. This reverses the usual direction — where code exists first and documentation (if it comes at all) describes what happened — and is the essential move that keeps TRUGS code legible.

The rest of this paper is the how-to: greenfield first, then refactoring, then the composition rules that let the approach scale, then the operational wrapper (AAA + memory + CI), then the patterns and anti-patterns we've found along the way, and finally the Python dialect conventions.

---

## 2. The four-step greenfield process

This is the canonical walkthrough from `PAPER_dark_code.md` §5, reproduced here as reference material. Readers already familiar with the casino shoe example can skim to §3.

### Step 1 — Write the TRUG (the macro flow)

Before any code, capture the macro flow as a TRUG. What are the stages? How does data move? Four or five nodes, three or four edges, two minutes.

For a shuffle_shoe pipeline:

```
stage_build → stage_shuffle → stage_cut → stage_burn
```

### Step 2 — Clarify the dependent flows (attach TRUG/L)

Each stage node gets a `trl` property — a TRUG/L sentence stating what the stage does. Invariants become properties.

```json
{
  "id": "stage_build",
  "type": "STAGE",
  "properties": {
    "trl": "PROCESS build SHALL DEFINE DATA shoe AS 8 MULTIPLE DATA deck.",
    "invariant_card_count": 416,
    "invariant_per_rank": 32,
    "invariant_per_suit": 104
  }
}
```

At this point a reviewer can read the TRUG and understand the complete system specification, without any code.

### Step 3 — Write the code as you write the TRUG/L

Each TRUG node becomes a function. The function-level TRUG/L comment (above the `def`) is copied from the node's `trl` property. Inline TRUG/L comments annotate every significant line.

```python
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
```

### Step 4 — Write TRUG/L-commented tests

Every test function has a TRUG/L comment naming what it verifies. Every invariant from step 2 gets a dedicated test.

```python
# AGENT SHALL VALIDATE STAGE build SUBJECT_TO RECORD invariant_card_count.
# ASSERT DATA shoe CONTAINS 416 DATA card.
def test_build_shoe_card_count():
    shoe = build_shoe(8)
    assert len(shoe) == 416
```

Coverage gaps are visible at a glance: a node with invariants but no tests is flagged immediately.

---

## 3. Refactoring dark code

Most real-world code already exists. It is dark. Compliance by greenfield rewrite is impractical — you need a refactoring path.

The refactoring path is the four-step process applied in reverse: start from the existing code, reconstruct intent, attach it formally.

### Step A — Read and document what the code actually does

Resist the urge to fix anything. Read a function top to bottom. Write a one-sentence summary of what it does in plain English.

For a hypothetical function:

```python
def parse_input(raw):
    raw = raw.strip()
    if not raw:
        return None
    parts = raw.split(',')
    parts = [p.strip() for p in parts]
    parts = [p for p in parts if p]
    return parts
```

Plain English: *"Takes a raw string, splits it on commas, returns the trimmed non-empty parts, or None if the input is empty after stripping."*

### Step B — Translate the summary into TRUG/L

Replace plain English with TRUG/L vocabulary. Every English concept maps to a TRUG/L word. No invention; only translation.

TRUG/L: *`PROCESS parse SHALL FILTER THE STRING input BY COMMA THEN REJECT EACH EMPTY RECORD OR RETURN NULL.`*

If the English summary contains a concept with no clear TRUG/L word, either:
- Rephrase the summary using concepts that are in the vocabulary
- The function is doing something the language doesn't cover — split it into smaller functions that each fit

### Step C — Add the TRUG node

Before touching the code, add a FUNCTION node in the folder's `.trug.json`:

```json
{
  "id": "fn_parse_input",
  "type": "FUNCTION",
  "properties": {
    "name": "parse_input",
    "trl": "PROCESS parse SHALL FILTER THE STRING input BY COMMA THEN REJECT EACH EMPTY RECORD OR RETURN NULL.",
    "file": "src/parse.py"
  }
}
```

### Step D — Attach the function-level TRUG/L comment

Copy the `trl` property as a comment above the `def`:

```python
# PROCESS parse SHALL FILTER THE STRING input BY COMMA THEN REJECT EACH EMPTY RECORD OR RETURN NULL.
def parse_input(raw):
    ...
```

### Step E — Annotate significant lines

Work through the function, attaching inline TRUG/L to every non-trivial line:

```python
# PROCESS parse SHALL FILTER THE STRING input BY COMMA THEN REJECT EACH EMPTY RECORD OR RETURN NULL.
def parse_input(raw):
    raw = raw.strip()            # TRIM STRING input
    if not raw:                  # IF NULL input
        return None              # RETURN NULL
    parts = raw.split(',')       # SPLIT BY COMMA
    parts = [p.strip() for p in parts]  # MAP EACH RECORD part THEN TRIM
    parts = [p for p in parts if p]     # FILTER EACH RECORD part THEN REJECT EMPTY
    return parts                 # RETURN RESULT
```

Trivial lines (literal returns, constants) can be skipped.

### Step F — Write the missing tests

Identify what the function promises (the `trl`), enumerate the properties it implies, write a test for each.

```python
# AGENT SHALL VALIDATE PROCESS parse — EACH EMPTY STRING RETURNS NULL.
def test_parse_empty_returns_null():
    assert parse_input("") is None
    assert parse_input("   ") is None

# AGENT SHALL VALIDATE PROCESS parse — MULTIPLE RECORD parts SEPARATED BY COMMA.
def test_parse_multiple_parts():
    assert parse_input("a,b,c") == ["a", "b", "c"]

# AGENT SHALL VALIDATE PROCESS parse — EACH EMPTY RECORD IS REJECTED.
def test_parse_drops_empty_parts():
    assert parse_input("a,,b") == ["a", "b"]
    assert parse_input(",a,") == ["a"]

# AGENT SHALL VALIDATE PROCESS parse — TRIM EACH RECORD.
def test_parse_trims_whitespace():
    assert parse_input(" a , b , c ") == ["a", "b", "c"]
```

### Step G — Run `trugs-compliance-check` and iterate

The tool reports what's missing. Fix one finding at a time. Each fix is a micro-commit. Compliance % monotonically rises.

**Key refactoring rule: never change behavior during a compliance pass.** If you discover a bug while annotating, file a separate issue. Compliance PRs are about visibility, not correctness. Mixing them is how legitimate compliance work gets blocked on scope arguments.

---

## 4. Multi-file projects

The greenfield and refactoring sections showed single-function compliance. Real projects have many files, many functions, and — critically — cross-file relationships. Compliance must compose.

### 4.1 One `.trug.json` per folder

Every folder with code gets a `folder.trug.json`. It captures all the public functions, classes, and their relationships within that folder. The file is the TRUG graph for that folder.

Standard layout:

```
my_project/
├── folder.trug.json
├── core/
│   ├── folder.trug.json          ← graph for core/
│   ├── parser.py
│   └── emitter.py
├── io/
│   ├── folder.trug.json          ← graph for io/
│   ├── reader.py
│   └── writer.py
└── cli/
    ├── folder.trug.json
    └── main.py
```

Each folder.trug.json owns nodes for its own files. Cross-folder references use the `FOLDER_NAME:node_id` prefix convention (e.g. `core:fn_parse`).

### 4.2 Inter-module edges

When `cli/main.py` calls `core.parser.parse_input`, the relationship must be a `DEPENDS_ON` edge in the CLI folder's TRUG:

```json
{
  "from_id": "fn_main",
  "to_id": "core:fn_parse_input",
  "relation": "DEPENDS_ON"
}
```

These cross-graph edges let someone understand the system from any starting point — traverse the edges and you find every dependency, every downstream caller, every test that validates this function.

### 4.3 Compliance checks compose

`trugs-compliance-check` runs across the whole repo. It walks folder-by-folder, checks each source file against its folder's TRUG, checks that cross-graph edges point at nodes that actually exist in the referenced graphs, and reports a single overall percentage.

A repo is compliant if every folder is compliant. A folder is compliant if every check (C1–C7 in the Standard) passes for every file.

### 4.4 Boundaries where compliance does not apply

Certain folders/files are out of scope by design:

- `zzz_*` archives — marked archive, not audited
- Auto-generated files (`ARCHITECTURE.md`, `AAA.md`, `CLAUDE.md`) — produced by `trugs-folder-render`, compliance is the responsibility of the source TRUG
- Third-party vendored code — requires a waiver (Standard §8)

The boundary must be explicit. Silent exclusion is a hole.

---

## 5. AAA protocol integration

TRUGS development isn't just a coding style — it's a full lifecycle. The AAA (Author-Audit-Action) protocol is the process wrapper: nine phases, two HITM gates, deterministic.

### 5.1 The nine phases

| # | Phase | Type |
|---|---|---|
| 1 | VISION | Human states what they want |
| 2 | FEASIBILITY | Quick GO/NO-GO |
| 3 | SPECIFICATIONS | Detailed enough to build |
| 4 | ARCHITECTURE | System design + ADRs |
| 5 | VALIDATION | **HITM Gate 1** — human approves the plan |
| 6 | CODING | Build — this is where TRUGS code gets written |
| 7 | TESTING | Tests pass |
| 8 | AUDIT | **HITM Gate 2** — independent audit, cyclic until clean |
| 9 | DEPLOYMENT | PR → human merges |

Phases 1–5 are the PLANNING cycle. Phases 6–9 are the EXECUTION cycle.

### 5.2 TRUGS work in each phase

- **Phase 1 (VISION)** — prose from the human. No TRUGS formality yet.
- **Phase 2 (FEASIBILITY)** — no artifact; just a judgment.
- **Phase 3 (SPECIFICATIONS)** — the macro TRUG appears here. Stages, data types, invariants. Step 1 + Step 2 of §2.
- **Phase 4 (ARCHITECTURE)** — the detailed TRUG. File layout, node breakdown, cross-module edges. This is the outline before the code.
- **Phase 5 (VALIDATION, HITM)** — human reads the Spec + Architecture TRUGs. Must be able to understand the system without code. If they can't, the TRUG is incomplete.
- **Phase 6 (CODING)** — Step 3 of §2. Code written top-down from the TRUG. Every `def` has a TRUG/L comment from day one; no "add docs later."
- **Phase 7 (TESTING)** — Step 4 of §2. Tests with TRUG/L comments. `trugs-compliance-check` passes locally.
- **Phase 8 (AUDIT, HITM)** — independent reviewer (human or a different agent) runs the compliance check, reads the TRUG, reads the code, checks alignment.
- **Phase 9 (DEPLOYMENT)** — PR with the changes. The PR body links the TRUG. The human merges.

### 5.3 Why this matters

Without AAA, TRUGS-compliance becomes a post-hoc annotation exercise — dangerous because it creates pressure to rationalize what already exists rather than design what should. With AAA, the TRUG is a **required input** to coding; there's no way to skip the outline.

### 5.4 CHORE exception

Not every change deserves the full AAA. Trivial fixes (typos, formatting, one-line bug fixes) follow the CHORE path: branch → PR → merge, no issue, no formal AAA. The rule of thumb: if it would need an issue, it needs an AAA. If not, it's a chore.

---

## 6. Memory system usage

TRUGS code captures intent in the graph. TRUGS **decisions** — the reasoning behind the graph, the tradeoffs considered, the alternatives rejected — get captured separately, in the memory system.

### 6.1 Memory as a TRUG

Agent memory is itself a TRUG graph. Each memory is a node; each association is an edge. Types are constrained: `user`, `feedback`, `project`, `reference`.

During development, decisions that shape the code are captured as memories:

```
trugs-memory remember ~/.../memory.trug.json \
  "We chose Fisher-Yates because uniform randomness matters for a casino shoe — other in-place shuffles have bias." \
  --type project \
  --rule "Use Fisher-Yates for any card shuffle; other shuffles have subtle bias" \
  --rationale "uniform random is a correctness requirement, not an optimization" \
  --tags "shuffle,fisher-yates"
```

### 6.2 What belongs in memory

- **Why decisions were made** (not what was decided — that's in the TRUG and the code)
- **Context a future agent needs** to judge whether the decision still applies
- **Feedback the agent received** about how to approach work
- **Facts about the user** that shape how help is given

### 6.3 What does NOT belong in memory

- Code patterns — readable from the code
- Architecture — readable from the TRUG
- Recent git history — readable from `git log`
- Ephemeral task state — use plan/todo instead

### 6.4 Memory in the compliance picture

Memory is not part of `trugs-compliance-check` (yet). But it's part of the broader TRUGS story: the code is legible, and the **decisions that shaped the code** are captured elsewhere in a similarly structured form. Future work may extend compliance to include memory hygiene (e.g., every architectural decision has a memory node).

---

## 7. CI enforcement

Compliance that isn't gated is aspirational. CI is where the standard stops being a suggestion.

### 7.1 The three gates

Every TRUGS-LLC public repo enforces three CI gates (adopted in `Xepayac/TRUGS-DEVELOPMENT#1548`):

1. **PR gate** — `trugs-compliance-check --strict` must pass. Compliance % may not decrease.
2. **Release gate** — compliance % must equal 100.0 before a version tag is cut or a package is published (PyPI, npm, crates.io, etc.).
3. **Promotion gate** — a private `Xepayac/*` repo cannot be transferred to `TRUGS-LLC/*` until it meets 100% compliance.

### 7.2 Workflow skeleton

`.github/workflows/compliance.yml`:

```yaml
name: Dark Code compliance
on: [pull_request, push]
jobs:
  compliance:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install
        run: pip install -e . -e 'git+https://github.com/TRUGS-LLC/TRUGS.git'
      - name: Run compliance check
        run: trugs-compliance-check --strict
```

On PR, CI runs the check against the PR branch and compares to the baseline on the target branch. On push to `main`, it updates the baseline.

### 7.3 Failure modes

When the gate fails, CI output tells the PR author exactly what's missing — file, line, rule number (C1–C7). The author fixes the specific finding, re-runs locally, and iterates.

Common failure modes:

- **New public function with no TRUG/L comment.** Add one. Usually a 1-line fix.
- **New test with no `AGENT SHALL VALIDATE` comment.** Same.
- **New TRUG/L comment that doesn't parse.** The `trl.py` parser is strict. Fix the vocabulary or syntax.
- **TRUG file has a dangling reference.** Either add the missing node or remove the edge.
- **Baseline decreased.** Means the PR introduced dark code. Either fix it in the PR or roll back.

### 7.4 Baselines and ratchets

The compliance baseline is a ratchet. Once set, it only goes up. This is intentional — it prevents the gradual erosion that happens when "we'll fix it later" becomes "we never fix it."

A PR that fixes 10 violations raises the baseline. A PR that introduces 5 new violations while fixing 10 existing ones raises the baseline by 5 — acceptable. A PR that breaks even on count but increases the total file count (new files, all dark) fails the ratio check. CI catches this.

---

## 8. Patterns & anti-patterns

### Pattern: one TRUG node per public surface

Every function a caller can reach gets a TRUG node. Every private helper does not. The graph is an outside-in view; internal plumbing is the responsibility of the function implementing the node.

### Pattern: invariants as properties-and-assertions-and-tests

An invariant that lives in only one of the three places (property, assertion, test) is fragile. Declare it in all three and the system enforces it at all three moments (graph review, runtime, test run).

### Pattern: short TRUG/L sentences

TRUG/L is English. It is readable. A 6-word sentence beats a 20-word sentence. If a node's `trl` property is a paragraph, the node is doing too much — split it.

### Pattern: test TRUG/L names the invariant, not the behavior

Bad: `# AGENT SHALL VALIDATE shuffle works.` — vague.
Good: `# AGENT SHALL VALIDATE STAGE shuffle SUBJECT_TO RECORD invariant_card_count.` — specific.

The good form names *which* invariant — reviewers see gaps instantly.

### Anti-pattern: retrofitting TRUG/L to existing code without reading it

The temptation during refactoring is to generate TRUG/L comments with an LLM from the code itself. Don't. The TRUG/L comment must be derived from the *specification* the function satisfies — which may not be what the code actually does. LLM-generated comments from code produce tautological annotations: "the comment is true because the code is the comment." That's dark code wearing a TRUG/L hat.

Instead: read the code, understand what it is *supposed* to do, write the TRUG/L from intent. If you can't, the function has no discoverable intent — which is itself a finding.

### Anti-pattern: over-decomposing

Not every 3-line helper needs a TRUG node. Nodes are for public surface. A `def _normalize(x)` that's only called from one other function in the same module doesn't need its own node; roll its intent into the caller's inline TRUG/L.

### Anti-pattern: inline TRUG/L on every line

Trivial lines don't need comments. Variable declarations, obvious arithmetic, single-line getters — leave them alone. TRUG/L on every line is noise; TRUG/L on *significant* lines is signal.

### Anti-pattern: invariant with no test

An `invariant_*` property in the TRUG that has no matching test is a checkbox without a check. Compliance requires all three corners — property + assertion + test — or the invariant isn't really claimed.

### Anti-pattern: mixing compliance and behavior changes

A compliance PR annotates; it doesn't refactor. A refactor PR changes code; its annotations are a side effect of the new shape. Mixing them produces PRs that are neither reviewable as compliance work nor as refactors. Keep them separate.

---

## 9. Python conventions

This section specifies the Python dialect of TRUGS compliance — the concrete rules that `trugs-compliance-check` enforces. It is the Python appendix of `STANDARD_dark_code_compliance.md`; readers seeking the normative text should refer to the Standard directly.

### 9.1 Function-level comment placement

Immediately above every public `def` or `class`, with nothing but blank lines between the comment block and the declaration. Multiple lines of `#`-prefixed comment; combined text must parse via `tools/trl.py`.

### 9.2 Inline comment placement

On the same line after the code, or on the line immediately above (for long annotations). `# TRUG/L SENTENCE.` form. Trivial lines are exempt.

### 9.3 Test function intent

Test functions are `def test_*` at module scope or methods of `class Test*`. Every test function's comment block begins with `AGENT SHALL VALIDATE`.

### 9.4 Invariant assertions

Invariants in the TRUG surface as `assert` statements in code at the point the invariant must hold. The assertion message (if provided) should reference the invariant name: `assert len(shoe) == 416, "invariant_card_count"`.

### 9.5 Public vs private

Public: not prefixed with `_`, not a dunder. Private: prefixed with `_` or dunder. Only public members require TRUG nodes + function-level TRUG/L.

### 9.6 What the CLI actually checks

Refer to `STANDARD_dark_code_compliance.md` §3 and §6 for the C1–C7 check specifications. The `--help` output of `trugs-compliance-check` is the runtime reference.

---

## 10. Closing

TRUGS-compliance is not a documentation exercise. It is a development discipline. The graph, the TRUG/L comments, the invariants, the tests, and the CI gates together make code legible — so the human reviewer can understand what an LLM produced without reading every line, and so a future agent modifying the code has formal specifications to satisfy rather than rediscover.

When practitioners internalize the discipline, the Dark Code problem doesn't arise. When organizations adopt the CI gates, Dark Code can't enter the codebase silently. When the portfolio enforces the hard rules (no decrease, no release without 100%, no promotion without 100%), the compliance state only improves over time.

"We TRUG" is not a slogan. It's a set of checks the CI runs on every PR.

---

## Version history

| Version | Date | Change |
|---|---|---|
| 0.1 | 2026-04-16 | Initial draft — `TRUGS-LLC/TRUGS#48` |
