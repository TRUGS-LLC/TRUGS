# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed
- Remove internal provenance labels and references from specification text while retaining technical content and released-version facts.
- Remove the medical evidence synthesis study; update the studies description to name the remaining genealogy study.
- Remove the retired development protocol from current documents and contribution templates; update the branch examples and renumber the how-to guide.
- Replace the missing CLI specification link with `trug --help` and the trugs-tools repository.
- Clean the generated vocabulary description and its builder text, preserving byte-for-byte regeneration.
- Give the vocabulary obligations in `AGENT.md` to the actor `PARTY trugs_llc` so all its TRL blocks validate.
- Clarify that compliance rule C2 accepts `STAGE` only from code to graph and excludes it from graph to code.
- `LICENSE` is the official Apache License 2.0 text; `NOTICE` carries the attribution only, its patent
  paragraph removed; the README gains a Scope section.
- `TRUGS_PROTOCOL/CORE.md` names the current ruleset `core_v2.0.0` where it said `core_v1.0.0`, which the
  validator rejects as retired.
- The TRL examples of the language pages, the README and the cheat sheet sit inside `<trl>` tags, and
  `make check` compiles every `<trl>` block in the repository with `trug audit markdown`; five examples are
  rewritten, in eight sentences, to what trugs-tools 2.4.0 accepts.
- `SPEC_grammar.md` states what trugs-tools 2.4.0 enforces from TRL (§2, §4), describes the compiled graph as
  the compiler writes it (§3, level directives), marks the `metric_level` value form reserved, and gives the
  adjective order as canonical rather than required; `SPEC_vocabulary.md`, `SPEC_examples.md` and the cheat
  sheet follow.
- `TRUGS_LANGUAGE/README.md` counts the 16 CORE validation rules.
- Paper: the novelty claim qualified and the five earlier systems cited and distinguished (TRUGS-LLC/TRUGS#81); every TRL listing checked with the released trugs-tools; vocabulary counts generated from the language file.
- The README is organised around the four types of TRUGS (describe, say, compute, govern), naming what is
  released for each and what is coming.
- The folder tool withdrawn from the toolchain is no longer mentioned: the getting-started guide's folder
  section is removed, and the README, the contributing guide, the templates, the standard, the how-to paper
  and the paper name `trugs-tools` alone.

## [2.0.0] — 2026-06-12

### Added — Release polish

Adds the specification repository's release checks.

Correction, 2026-10-16: The release-polish standard referenced during release preparation is not shipped in this repository; the implemented checks are defined in `Makefile` and `.github/workflows/check.yml`.

- **Layer 1 (industry baseline):** `ruff` + `mypy` + `pytest` declared in `pyproject.toml [project.optional-dependencies] dev` with `[tool.*]` config; `Makefile` adds a single-command `make check` gate; `.github/workflows/check.yml` runs it in CI (coexists with `compliance.yml`); `.gitignore` covers `.mypy_cache/`/`.ruff_cache/`. Baseline was already lint/type/test-green; formatting applied.
- **Layer 3 (TRL contracts):** `tools/build_language_trug.py` (the one production module) carries a module-level `<trl>` header, function-level `<trl>` contracts on its 3 public functions, and inline `<trl>` annotations on significant lines.
- **Layer 2 (structural):** this changelog finalized from `CHANGELOG_TRUGS_2.0_pending.md` → `CHANGELOG.md` (resolving the `folder.trug.json` `doc_changelog` mispoint); `folder.trug.json` brought to a clean filesystem consistency check (added nodes for `Makefile`, `PROPOSAL/`, and the archive directory).
- **Layer 4 (self-description):** "the spec proves itself" — the spec's shipped TRUGs (`TRUGS_LANGUAGE/language.trug.json` + the `EXAMPLES/` + `STUDIES/` exemplars) validate against TRUGS's own 16-rule CORE via `trug validate`, and `language.trug.json` is a deterministic rebuild of `SPEC_vocabulary.md`. Verify in one command:
  ```sh
  make trugs    # validate every shipped TRUG + confirm the deterministic language.trug.json rebuild
  ```
  (or, all four layers at once: `make check`). Branch protection (PR-required, no force-push) is applied to the public `TRUGS-LLC/TRUGS` at the 2.0 release; the development mirror could not carry it (GitHub plan limit).

> **Reconciliation note:** the "Added — Dark Code (under TRUGS 1.x line)" entry below references `tools/compliance_check.py` + a `trugs-compliance-check` entrypoint that are **not present in this 2.0 spec-only repo** (the tooling moved to `trugs-tools`); and it records the *initial* baseline **26.72%**, whereas `.github/compliance-baseline.json` currently reads **99.83%**. The historical entry is preserved as-is; this note flags the drift. The baseline number is not advanced here (out of scope).

### Added — TRUGS 2.0 (corpus-driven vocabulary expansion)

Vocabulary grows **211 → 233 words**. The 22 additions are corpus-evidenced: derived from the de-masked per-class TRL drift re-measurement (which overturned an earlier null result), accepted through human review, with swap-safety confirmed by the swap-capacity regression check.

- **22 vocabulary additions** in `TRUGS_LANGUAGE/SPEC_vocabulary.md` (per-POS counts + §11 Summary table reconciled):
  - **Verbs +19** (61 → 80): `EXECUTE`, `INVOKE`, `HALT`, `COMPLETE`, `PASS` (control); `EMIT`, `POST`, `LOAD`, `APPEND`, `PRODUCE`, `DELEGATE` (move); `APPLY`, `DERIVE`, `UPDATE` (transform); `ACCEPT`, `SUGGEST` (permit); `HAVE` (bind); `ASSERT_NOT`, `INVARIANT` (obligate keywords).
  - **Adjectives +3** (36 → 39): `ONLY`, `AT_LEAST`, `EXACTLY` (quantity — the cardinality/exclusivity family; `AT_LEAST` fills the `>=` gap where only strict-`>` `EXCEEDS` existed).
- **`leading_keyword_directive` grammar** in `TRUGS_LANGUAGE/SPEC_grammar.md` — `ASSERT` / `ASSERT_NOT` / `INVARIANT` may head a sentence (keyword before subject). `INVARIANT` is the first-class temporal-universality keyword subsuming the legacy `ASSERT … ACROSS ALL TIME` idiom.
- **10 capacity-preserving swaps** (no vocabulary added — these drift forms are retired in favor of an existing word, confirmed by the swap-capacity regression check): `CONTAIN`→`CONTAINS`, `EXIST`→`EXISTS`, `EQUAL`→`EQUALS`, `BEFORE`→`PRECEDES`, `ASK`→`REQUEST`, `UNRESOLVED`→`PENDING`, `SUPERSEDED`→`SUPERSEDES`, `ONE`→`1` (integer literal), `FOR`→`'for` (sugar), `AT`→`'at` (sugar).
- `TRUGS_LANGUAGE/language.trug.json` — regenerated from the spec by `tools/build_language_trug.py` (22 new `BASE_WORD` nodes; total nodes 267 → 289; `meta.word_count` 211 → 233). `tools/test_build_language_trug.py` constants updated; all 7 generator tests pass.

#### Deferred to the parser update
- At release, the `leading_keyword_directive` production was **spec-only** here; the v1 reference parser did not yet implement it. Parser support + the corpus migration retiring the `ACROSS ALL TIME` idiom were deferred to the parser update.
- 2 of the 12 proposed swaps — `ACROSS`→`INVARIANT` and `TIME`→`INVARIANT` — were **deferred**: their capacity was not confirmed because dropping the `ACROSS ALL TIME` idiom required the parser to parse `INVARIANT` as a leading directive first. Until that parser update, the idiom remained supported.

### Added — TRUGS 2.0 (selective loading foundation)

- **`LEVEL_PREFIX` part of speech** — 21 SI prefixes added to TRL vocabulary (vocabulary grows 190 → 211 words across 9 parts of speech). New section in `TRUGS_LANGUAGE/SPEC_vocabulary.md §9 Level Prefixes`. Prefixes: YOTTA, ZETTA, EXA, PETA, TERA, GIGA, MEGA, KILO, HECTO, DEKA (macro · zoom out); BASE (default · ground zero); DECI, CENTI, MILLI, MICRO, NANO, PICO, FEMTO, ATTO, ZEPTO, YOCTO (micro · zoom in).
- **`level_directive` BNF rule** — bare `metric_level` token (e.g. `DECI_STATEMENT`) on its own line marks a hierarchy transition for an LLM consumer reading TRL source. Compiles to nothing; no node, no edge. Validator does not enforce directives — they are an LLM-comprehension affordance, not a correctness gate. See `TRUGS_LANGUAGE/SPEC_grammar.md §level_directive`.
- **`metric_level` value position** — `<LEVEL_PREFIX>_<UPPERCASE_NAME>` may appear in the value position of an `object_phrase`, e.g. `... AT BASE_FUNCTION`. Compiles to a `metric_level` property on the affected node (existing `metric_level` property semantics from CORE Rule 9 — no change).
- `TRUGS_LANGUAGE/SPEC_examples.md` — examples 29–30 demonstrate the directive form and the value form.
- `TRUGS_LANGUAGE/language.trug.json` — 21 new word nodes (`w-yotta` … `w-yocto`), 1 new top-level category (`level_prefixes`), 3 sub-category nodes (macro · default · micro). Total nodes: 246 → 267.

### Added — Dark Code (under TRUGS 1.x line)
- `REFERENCE/` folder — canonical library for TRUGS papers, standards, and cross-cutting material
  - `REFERENCE/README.md` — index
  - `REFERENCE/PAPER_dark_code.md` — WHY paper, moved from `TRUGS-LLC/TRUGS-AGENT`; TRL→TRUG/L rename applied
  - `REFERENCE/PAPER_how_to_code_with_trugs.md` — HOW paper, practitioner guide (new)
  - `REFERENCE/STANDARD_dark_code_compliance.md` — CHECK, the auditable compliance standard (new)
- `tools/compliance_check.py` — `trugs-compliance-check` CLI — mechanical C1–C7 verifier per STANDARD
- `tools/test_compliance_check.py` — 23 unit tests covering C1, C3, C4, C5 + metrics + CLI
- `pyproject.toml` entrypoint: `trugs-compliance-check`
- `.github/compliance-baseline.json` — initial baseline (26.72%) recorded

### Changed
- `folder.trug.json` — new nodes for REFERENCE/ children and `tools_compliance_check`, plus 4 edges
- `TRUGS_LANGUAGE/SPEC_vocabulary.md`, `SPEC_grammar.md`, `SPEC_examples.md`, `language.trug.json` — version bumped 1.0.1 → 2.0.0 to reflect LEVEL_PREFIX vocabulary extension.

### Context
- Implements the selective-loading foundation. Macro-to-micro hierarchy markers in TRL allow an LLM to consume a large TRUG selectively (top-down by level) without loading the whole graph upfront. The TRUG itself remains the source of truth; the directives are LLM affordance.
- Implements `TRUGS-LLC/TRUGS#48` (foundation) — bring the TRUGS-LLC public portfolio to Dark Code compliance.
- Convention: TRUG/L (not "TRL") in all prose going forward.

### Migration
- This is the first release on the **TRUGS 2.0 line**. At release, `trugs` 1.2.x and 1.0.x remained on PyPI, with **yanking** scheduled for the end of a 6-week migration window. Any consumer outside the TRUGS-LLC portfolio should pin to `trugs>=2.0.0`. There are no breaking changes to existing CORE rules — only additive vocabulary and grammar.

## [1.2.1] - 2026-04-10

### Fixed
- `save_graph` resolves symlinks before atomic write (no longer orphans target)
- `_parse_duration_days` caps at 365,000 days (OverflowError -> ValueError)
- `init_memory_graph` version bumped to 1.2.0 (was stuck at 1.0.0)
- `_parse_duration_days` rejects None/int/whitespace inputs
- `_idempotency_key` uses SHA-256 hash instead of raw join
- `_render_memory` collapses multi-line body to single line
- `memory_import` reads from resolved path (closes TOCTOU window)

### Added
- CHANGELOG.md (this file)
- Module-level `MEMORY_GRAPH_VERSION` constant in `tools/memory.py`

## [1.2.0] - 2026-04-09

### Added
- Memory audit subsystem: `trugs-memory audit` with dead-rules detection and hit tracking
- Memory reconcile: duplicate-candidate detection via token-set Jaccard similarity
- Memory import: bulk import flat markdown files with YAML frontmatter
- Memory render: deterministic markdown render with budget enforcement
- 5 new optional node properties: `rule`, `rationale`, `valid_to`, `session_id`, `superseded_by`
- Supersede chains for memory lifecycle management

Note: version 1.1.0 was skipped. The schema extension shipped directly as 1.2.0.

## [1.0.1] - 2026-04-07

### Fixed
- Minor validation and CLI fixes

## [1.0.0] - 2026-04-06

### Added
- Initial release: TRUGS core validator (`trugs-validate`)
- Memory graph: `trugs-memory init`, `remember`, `recall`, `forget`, `associate`
- Graph query tools: `trugs-tget`, `trugs-tupdate`, `trugs-tdelete`, `trugs-tunlink`
