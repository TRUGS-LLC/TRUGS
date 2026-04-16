# STANDARD: Dark Code Compliance

**Status:** Draft v0.1 — adopted by `TRUGS-LLC/TRUGS#48`
**Applies to:** every TRUGS-LLC public repo
**Enforced by:** `trugs-compliance-check` CLI + CI gates (this repo, `tools/compliance_check.py`)
**See also:** [`PAPER_dark_code.md`](PAPER_dark_code.md) (the WHY), [`PAPER_how_to_code_with_trugs.md`](PAPER_how_to_code_with_trugs.md) (the HOW)

---

## 1. Purpose & scope

This standard operationalizes the four-corner verification square from `PAPER_dark_code.md` into a concrete, auditable checklist that every TRUGS-LLC public repository must pass. It is the answer to the question "how do we know a repo actually dogfoods TRUGS?"

**Applies to:** every public repo under the `TRUGS-LLC` GitHub organization.

**Covers:** source code, tests, TRUG graph files (`.trug.json`), and prose documents (`.md`).

**Does not cover:** third-party vendored code (call it out with a waiver — see §8), auto-generated files (`ARCHITECTURE.md`, `AAA.md`, `CLAUDE.md` — produced by `trugs-folder-render`), build artifacts.

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

| Edge | What it means | How it is checked |
|---|---|---|
| **TRUG ↔ code** | Every public function has a TRUG node | `trugs-compliance-check` C1 |
| **TRUG ↔ TRUG/L** | Every TRUG node with a `trl` property parses via `trl.py` | C2 |
| **TRUG ↔ tests** | Every SPEC/FUNCTION node has ≥ 1 inbound `VALIDATES` edge from a TEST node | C3 |
| **TRUG/L ↔ code** | Every public function has a function-level TRUG/L comment that parses | C4 |
| **TRUG/L ↔ tests** | Every test function has an `AGENT SHALL VALIDATE ...` comment that parses | C5 |
| **invariants** | Every `invariant_*` property has an assertion in code + a test | C6 |
| **TRUG validity** | Every `.trug.json` file passes `trugs-folder-check` | C7 |
| **code ↔ tests** | The test suite passes | existing `pytest` / language-native test runner |

**Dark Code is code where any edge of this square is broken.** Compliance means every edge is intact and mechanically verified.

## 3. Python conventions

The Python dialect of TRUG/L compliance. (v1 supports Python only; other languages queue as future appendices — see §9.)

### 3.1 Function-level TRUG/L comments

Every public `def` and `class` declaration must have a **function-level TRUG/L comment block** immediately above the declaration, separated by nothing but blank lines.

A comment is "function-level TRUG/L" if:
- Every line is a Python comment (`#` prefix)
- The concatenated text (with `#` and leading whitespace stripped) parses successfully via `tools/trl.py`
- The TRUG/L sentence begins with a Verb (`FILTER`, `VALIDATE`, `SHALL`, etc.) — describes what the function **does**, not what it **is**

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

- Parses via `tools/trl.py`
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

Every public function / class / method in the implementation must have a corresponding node in the folder's `.trug.json`. Node type is one of:

- `FUNCTION` — a public function
- `PROCESS` — a long-running or multi-step process (preferred for pipeline stages)
- `CLASS` — a public class
- `STAGE` — a pipeline stage (subset of PROCESS with ordered position)
- `METHOD` — a public method of a class (optional — can roll up to the CLASS node)

### 4.2 The `trl` property is canonical

When a node has a `trl` property, that string is the **canonical TRUG/L specification** of what the node represents. The function-level TRUG/L comment above the corresponding `def` in code must be identical to (or an exact extension of) the `trl` property. This ensures TRUG ↔ TRUG/L ↔ code is mechanically traceable.

### 4.3 Cross-node edges

The graph must encode these relations as edges:

| Edge | Relation | From | To |
|---|---|---|---|
| A FUNCTION validates another | `VALIDATES` | TEST | FUNCTION / SPEC |
| A FUNCTION implements a spec | `IMPLEMENTS` | FUNCTION | SPEC |
| A FUNCTION depends on another | `DEPENDS_ON` | FUNCTION | FUNCTION / MODULE |
| Containment | `contains` | parent | child |
| Flow | `FEEDS` | upstream stage | downstream stage |

Edge relations must come from the TRUG/L preposition set (see `TRUGS_LANGUAGE/SPEC_vocabulary.md`). Inventing new relations is a violation.

## 5. TRUG file conventions

Every `.trug.json` file in the repo (excluding `zzz_*` archives) must:

- Pass `trugs-folder-check` (existing CORE validation — 16 rules)
- Contain no dangling references (edges to nonexistent nodes, `contains` to missing children)
- Match the filesystem: nodes with `properties.path` or `properties.file` must reference existing files (or be marked `stale: true` with a reason)
- Use edge relations from the TRUG/L preposition set

These rules already exist via `trugs-folder-check`; the compliance standard incorporates them rather than re-specifying.

## 6. CI gate

### 6.1 Every PR runs `trugs-compliance-check`

A GitHub Actions workflow at `.github/workflows/compliance.yml` must run on every PR and every push to main:

```yaml
- name: Dark Code compliance
  run: trugs-compliance-check --strict
```

Exit codes:
- `0` — compliance % is ≥ the baseline on the target branch
- `1` — compliance % decreased, or a hard violation was introduced

### 6.2 Baseline tracking

Each repo stores its current compliance baseline in `.github/compliance-baseline.json`:

```json
{
  "compliance_percent": 85.3,
  "files_checked": 42,
  "violations_by_rule": {"C1": 5, "C2": 1, "C3": 0}
}
```

PRs that raise compliance update the baseline (committed in the PR). PRs that merely maintain compliance do not need to touch it. PRs that decrease compliance fail CI.

### 6.3 Hard violations

Certain violations fail CI regardless of overall percentage:

- A TRUG node with an invalid `trl` property that does not parse
- A `.trug.json` file that fails `trugs-folder-check`
- A test function with no TRUG/L comment at all (total darkness)

## 7. Hard rules

Three hard gates apply to every TRUGS-LLC public repo (adopted in `Xepayac/TRUGS-DEVELOPMENT#1548`):

1. **No PR may decrease compliance %.** CI enforces.
2. **No version bump without 100% compliance.** Tag/release workflows must check `compliance_percent == 100.0` before building wheels, publishing to PyPI, etc.
3. **No `Xepayac → TRUGS-LLC` promotion without 100% compliance.** A private-to-public repo transfer must pass the standard first.

These are hard. They are not aspirational.

## 8. Exceptions & waivers

Reality bites: vendored code, generated code, or narrowly-scoped legacy material may be unreasonably expensive to bring to compliance. Waivers exist, but are limited and tracked.

### 8.1 Waiver mechanism

> **Implementation status:** [DEFERRED] — The waiver mechanism is specified here for completeness. `trugs-compliance-check` v1.x does not yet read `.github/compliance-waivers.json` or support `--no-waivers`. Track implementation in a future issue.

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
- `trugs-compliance-check --no-waivers` flag produces the unwaived percentage. The baseline can track either the waived or the raw percentage, configured in `.github/compliance-baseline.json`.

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
- Human approval (HITM)
- A version bump of the standard (semantic: major for breaking changes to what counts as compliant; minor for new required checks; patch for clarifications)

When the standard changes, downstream repos may see their compliance % shift without any code change. CI at those repos will correctly flag the new state.

## Version history

| Version | Date | Change |
|---|---|---|
| 0.1 | 2026-04-16 | Initial draft — `TRUGS-LLC/TRUGS#48` |
