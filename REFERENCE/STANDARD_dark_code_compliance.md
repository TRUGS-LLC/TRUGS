# STANDARD: Dark Code Compliance

**Status:** Draft v0.1.1 — adopted by `TRUGS-LLC/TRUGS#48`
**Applies to:** every TRUGS-LLC public repo
**Enforced by:** `trug compliance` CLI from the companion [TRUGS-TOOLS](https://github.com/TRUGS-LLC/TRUGS-TOOLS) repository + CI gates
**See also:** [`PAPER_dark_code.md`](PAPER_dark_code.md) (the WHY), [`PAPER_how_to_code_with_trugs.md`](PAPER_how_to_code_with_trugs.md) (the HOW)

---

## 1. Purpose & scope

This standard operationalizes the four-corner verification square from `PAPER_dark_code.md` into a concrete, auditable checklist that every TRUGS-LLC public repository must pass. It is the answer to the question "how do we know a repo actually dogfoods TRUGS?"

**Applies to:** every public repo under the `TRUGS-LLC` GitHub organization.

**Covers:** source code, tests, TRUG graph files (`.trug.json`), and prose documents (`.md`).

**Does not cover:** third-party vendored code (call it out with a waiver — see §8), auto-generated files (such as `ARCHITECTURE.md`), build artifacts.

## 2. The four-corner square

The compliance standard has exactly four corners, each a mechanical validation:

```
         TRUG (.trug.json)
        /               \
       /                 \
   TRUG/L             implementation
   (comments)            code
       \                 /
        \               /
         TRUG/L tests
```

| Edge | What it means | Enforced by |
|---|---|---|
| **TRUG/L ↔ code** | Every public function has a function-level TRUG/L comment that parses | check rule C1 |
| **TRUG ↔ code** | Every public function has a TRUG node | check rule C2 |
| **TRUG ↔ TRUG/L** | Every TRUG node with a `trl` property parses via `trl.py` | check rule C3 |
| **TRUG/L ↔ tests** | Every test function has an `AGENT SHALL VALIDATE ...` comment that parses | check rule C4 |
| **TRUG ↔ tests** | Code implementation graphs use inbound `VALIDATES` edges from TEST to SPEC/FUNCTION nodes; this repository's folder graph uses suite-to-file `tests` edges | C5 convention; individual folder-function test edges are not verified |
| **invariants** | Every `invariant_*` property has an assertion in code + a test | check rule C6 |
| **TRUG validity** | Every `.trug.json` file passes validation | check rule C7 |
| **code ↔ tests** | The test suite passes | existing `pytest` / language-native test runner |

The check rules C1–C7 are defined below in §3–§6. Read `trug compliance` results with their reported check coverage: a passing report does not establish individual-function test traceability in this repository's folder graph.

**Dark Code is code where any edge of this square is broken.** The square is the verification goal; the shipped folder graph records file-level test relationships, without inbound test edges to its individual build-function nodes.

## 3. Python conventions

The Python dialect of TRUG/L compliance. (v1 supports Python only; other languages queue as future appendices — see §9.)

### 3.1 Function-level TRUG/L comments

Every public `def` and `class` declaration must have a **function-level TRUG/L comment block** immediately above the declaration, separated by nothing but blank lines.

A comment is "function-level TRUG/L" if:
- Every line is a Python comment (`#` prefix)
- The concatenated text (with `#` and leading whitespace stripped), saved as `comments.trl`, compiles successfully via `trug trl compile comments.trl > comments.json`; `trug trl validate comments.json` checks the compiled JSON graph
- The TRUG/L sentence describes what the function **does** using subject-first clauses: a noun phrase or pronoun, followed by a verb phrase (optional modal, then verb)

"Public" means:
- Not prefixed with `_` (single-underscore conventions are module-private)
- Not dunder (`__init__`, `__repr__`, etc. — exempt; they're language scaffolding)
- Top-level in a module or a public method of a public class

**Example:**

```python
# PROCESS shuffle SHALL SORT DATA shoe BY RANDOM ONCE.
# EACH DATA card SHALL EXIST 'at EXACTLY A UNIQUE RECORD position.
# RESULT SHALL CONTAIN 416 DATA card.
def shuffle_shoe(shoe: list[Card], rng: random.Random | None = None) -> list[Card]:
    ...
```

### 3.2 Inline TRUG/L comments

Every **non-trivial line** inside a public function must carry an inline TRUG/L comment. "Non-trivial" means:

- Branching (`if`, `for`, `while`, `try`, `with`)
- Assignment with a call (`x = foo(...)`, `x = bar.method(...)`)
- Return statements that aren't plain passthrough (`return x` is trivial; `return transform(x)` is not)
- Assertions
- Raises

Trivial lines — variable declaration, obvious arithmetic, boilerplate, one-line getters — are exempt.

The inline comment is either:
- On the same line after the code (`x = foo()  # MAP RECORD input TO DATA output`)
- On the line immediately above (for long comments or multi-line logic)

These are policy requirements. The builder `tools/build_language_trug.py` currently has only partial inline annotations in `parse_spec`, `build_trug` and `main`: loops, branches and assignments with calls lack the required same-line or immediately preceding TRUG/L comments. The builder therefore falls short of this policy. The current passing `trug compliance .` report checks no functions in this repository and does not verify these inline annotations.

**Example:**

```python
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

### 3.3 Test TRUG/L comments

Every test function — i.e. every `def test_*` at module top-level, and every method of a `class Test*` — must have a function-level TRUG/L comment that:

- Compiles from stripped comment text via `trug trl compile comments.trl > comments.json`; `trug trl validate comments.json` checks the compiled JSON graph
- Begins with `AGENT SHALL VALIDATE` (the canonical test-intent opener)
- Names a specific invariant, property, or node being verified

**Example:**

```python
# AGENT SHALL VALIDATE STAGE build SUBJECT_TO RECORD invariant_card_count.
# ASSERT DATA shoe CONTAINS 416 DATA card.
def test_build_shoe_card_count():
    shoe = build_shoe(8)
    assert len(shoe) == 416
```

### 3.4 Invariants

An **invariant** is a property that must hold at a specific point in the execution. Invariants are declared three ways and the three must match:

1. **In the TRUG:** as a property on a FUNCTION / PROCESS / STAGE node, with a key matching `invariant_*`.
   ```json
   "properties": {
     "invariant_card_count": 416,
     "invariant_per_rank": 32
   }
   ```
2. **In code:** as an `assert` statement at the point the invariant must hold.
   ```python
   assert len(shoe) == n_decks * 52  # ASSERT RECORD invariant_card_count
   ```
3. **In tests:** as a dedicated test function whose TRUG/L comment names the invariant.
   ```python
   # AGENT SHALL VALIDATE STAGE build SUBJECT_TO RECORD invariant_card_count.
   def test_build_shoe_card_count():
       assert len(build_shoe(8)) == 416
   ```

Compliance requires all three. An invariant in the TRUG with no assertion or no test is a gap.

## 4. TRUG node conventions

### 4.1 Node for every public code artifact

Every public function / class / method in the implementation must have a corresponding node in the folder's `.trug.json`. In this specification repository's `project_v1` folder graph, repo-side build functions use individual `SPECIFICATION` nodes: `parse_spec`, `build_trug` and `main` are indexed beneath the file-level builder node. In a code implementation graph, node type is one of:

- `FUNCTION` — a public function
- `PROCESS` — a long-running or multi-step process (preferred for pipeline stages)
- `CLASS` — a public class
- `STAGE` — a pipeline stage (subset of PROCESS with ordered position); C2 accepts it only in the code-to-graph direction and excludes it from the graph-to-code direction.
- `METHOD` — a public method of a class (optional — can roll up to the CLASS node)

### 4.2 The `trl` property is canonical

When a node has a `trl` property, that string is the **canonical TRUG/L specification** of what the node represents. The function-level TRUG/L comment above the corresponding `def` in code must be identical to (or an exact extension of) the `trl` property. This ensures TRUG ↔ TRUG/L ↔ code is mechanically traceable.

### 4.3 Cross-node edges

Code implementation graphs use the relations below. In this repository's `project_v1` folder graph, `TEST_SUITE` links to the builder file and tools component through lowercase `tests` edges. The individual `SPECIFICATION` function nodes have no inbound test edges; containment alone does not establish test coverage. The table is a code-graph convention, not an additional mandatory `VALIDATES` relation for those folder nodes:

| Edge | Relation | From | To |
|---|---|---|---|
| A test validates a function or spec | `VALIDATES` | TEST | FUNCTION / SPEC |
| A FUNCTION implements a spec | `IMPLEMENTS` | FUNCTION | SPEC |
| A FUNCTION depends on another | `DEPENDS_ON` | FUNCTION | FUNCTION / MODULE |
| Containment | `contains` | parent | child |
| Flow | `FEEDS` | upstream stage | downstream stage |

These are descriptive compliance-graph relation labels. They need not be TRUG/L prepositions: `VALIDATES`, for example, is a compliance relation rather than a TRUG/L preposition. See `TRUGS_LANGUAGE/SPEC_vocabulary.md` for the preposition vocabulary.

## 5. TRUG file conventions

Every `.trug.json` file in the repo (excluding `zzz_*` archives) must:

- Pass `trug validate` (general CORE graph validation)
- Contain no dangling references (edges to nonexistent nodes, `contains` to missing children)
- Match the filesystem for repository filesystem-index references: nodes with `properties.path` or `properties.file` must reference existing files (or be marked `stale: true` with a reason). External research-source references need not resolve to files in this repository.
- Use descriptive relation labels for compliance graphs, including those in §4.3; a graph label does not add a TRUG/L preposition

General CORE validation uses `trug validate`; `make trugs` validates the root `folder.trug.json` with the other shipped graphs. These commands do not establish enforcement of every convention listed above.

## 6. CI gate

### 6.1 Every PR targeting main runs `trug compliance`

The shipped `.github/workflows/compliance.yml` runs on every PR targeting main and every push to main. Its compliance step runs the command below; it passes neither `--strict` nor `--baseline-update` and has no separate target-branch baseline comparison or update step. The baseline ratchet described in §6.2 is a proposed workflow design, not an implemented gate here:

```yaml
- name: Dark Code compliance
  run: trug compliance .
```

The workflow fails when the compliance command exits unsuccessfully. On failure it attempts a JSON report with `trug compliance --json .`; that reporting step is allowed to fail. A successful command is not evidence of a comparison with the target branch.

### 6.2 Baseline tracking

Each repo stores its current compliance baseline in `.github/compliance-baseline.json`:

```json
{
  "compliance_percent": 85.3,
  "files_checked": 42,
  "violations_by_rule": {"C1": 5, "C2": 1, "C3": 0}
}
```

Under the proposed ratchet, PRs that raise compliance would update the baseline and decreases would fail CI. A `.github/compliance-baseline.json` snapshot is present, but the shipped workflow does not fetch a target-branch snapshot or update the stored baseline. The JSON above illustrates the design rather than the current snapshot.

### 6.3 Hard violations

The list below states hard-violation policy. The shipped CI runs the commands in §6.1 and `make check`; it does not establish enforcement of every policy item:

- A TRUG node with an invalid `trl` property that does not parse
- A shipped graph that fails `trug validate` (enforced by `make trugs`, within `make check`)
- A test function with no TRUG/L comment at all (total darkness)

## 7. Hard rules

Three hard gates apply to every TRUGS-LLC public repo:

1. **No PR may decrease compliance %.** This is a policy requirement; the shipped workflow runs `trug compliance .` without an explicit target-branch baseline comparison, so it does not establish enforcement of this ratchet.
2. **No version bump without 100% compliance.** Tag/release workflows must check `compliance_percent == 100.0` before building wheels, publishing to PyPI, etc.
3. **No `Xepayac → TRUGS-LLC` promotion without 100% compliance.** A private-to-public repo transfer must pass the standard first.

These are hard. They are not aspirational.

## 8. Exceptions & waivers

Reality bites: vendored code, generated code, or narrowly-scoped legacy material may be unreasonably expensive to bring to compliance. Waivers exist, but are limited and tracked.

### 8.1 Waiver mechanism

> **Implementation status:** [DEFERRED] — The waiver mechanism is specified here for completeness. `trug compliance` v1.x does not yet read `.github/compliance-waivers.json` or support `--no-waivers`. Track implementation in a future issue.

A file can be excluded from compliance checks by listing it in `.github/compliance-waivers.json`:

```json
{
  "waivers": [
    {
      "path": "vendor/third_party_lib.py",
      "reason": "Vendored from upstream; compliance applies to our code only.",
      "expires": "2027-01-01",
      "approved_by": "Xepayac"
    }
  ]
}
```

### 8.2 Rules for waivers

- Every waiver must have a `reason`, an `expires` date, and an `approved_by` field.
- Waivers expire. Reapply or remove before the expiry date.
- Waiver files count toward the total file count but not toward the violation count. Compliance % is reported both with and without waivers.
- No waiver may cover a file that TRUGS-LLC authors own. Waivers are for code we don't control.
- `trug compliance --no-waivers` flag produces the unwaived percentage. The baseline can track either the waived or the raw percentage, configured in `.github/compliance-baseline.json`.

## 9. Future language appendices

This standard specifies **Python conventions** only. Other languages queue as future appendices:

| Language | Status | Appendix |
|---|---|---|
| Python | **live** | §3 above |
| Go | future | `appendix_go_trug_l.md` (not yet written — needed when a Go repo enters the TRUGS-LLC portfolio) |
| Rust | future | as needed |
| TypeScript / JavaScript | future | as needed |

Each language appendix specifies the dialect-specific form of:
- Function-level comment placement
- Inline comment placement
- Test-function intent comment
- Invariant assertion idiom

A TRUGS-LLC repo written in a language without a published appendix is not compliance-ready. The appendix must be written (and adopted via PR to this standard) **before** the first repo in that language can be audited.

## 10. Change control

This standard is a normative document. Changes require:

- A PR to `TRUGS-LLC/TRUGS` against `REFERENCE/STANDARD_dark_code_compliance.md`
- Discussion in an issue linked from the PR
- Human approval
- A version bump of the standard (semantic: major for breaking changes to what counts as compliant; minor for new required checks; patch for clarifications)

When the standard changes, downstream repos may see their compliance % shift without any code change. CI at those repos will correctly flag the new state.

## Version history

| Version | Date | Change |
|---|---|---|
| 0.1 | 2026-04-16 | Initial draft — `TRUGS-LLC/TRUGS#48` |

Correction, 2026-10-16: Draft v0.1.1 clarifies the folder graph's test-edge convention, distinguishes graph relations from TRUG/L prepositions, and corrects the compliance workflow and baseline claims to the shipped configuration. The initial draft entry above is retained.
