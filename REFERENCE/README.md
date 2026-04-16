# REFERENCE Library

**Canonical home for TRUGS papers, standards, and cross-cutting material.**

This folder is the umbrella library for reference documents that apply across the TRUGS ecosystem — not specific to the TRUG/L language (`TRUGS_LANGUAGE/`) or the TRUG CORE protocol (`TRUGS_PROTOCOL/`). Papers and standards live here; normative specifications for the language and protocol live in their dedicated folders next door.

## Layout

```
REFERENCE/
├── README.md                              ← you are here
├── PAPER_dark_code.md                     ← the WHY — Dark Code problem and TRUGS as resolution
├── PAPER_how_to_code_with_trugs.md        ← the HOW — practitioner guide
├── STANDARD_dark_code_compliance.md       ← the CHECK — auditable compliance checklist
└── examples/                              ← reserved for cross-language examples
```

## What lives where

| Topic | Home |
|---|---|
| Papers (Dark Code, How To, future research) | `REFERENCE/` |
| Compliance standards | `REFERENCE/STANDARD_*.md` |
| TRUG CORE protocol spec (7 node fields, 3 edge fields, 16 validation rules) | `TRUGS_PROTOCOL/` |
| TRUG/L language spec (190 words, BNF, grammar) | `TRUGS_LANGUAGE/` |
| Original foundational TRUGS paper (LaTeX) | `PAPER/` |
| Python reference implementation | `tools/` |

## The document trinity

The three documents in `REFERENCE/` form a trinity:

- **`PAPER_dark_code.md`** — the WHY. Defines the Dark Code problem and TRUGS as the resolution. Starts every reader who has never seen TRUGS.
- **`PAPER_how_to_code_with_trugs.md`** — the HOW. Practitioner guide derived from §5 of the Dark Code paper, expanded with refactoring, multi-file, AAA, CI, and patterns material.
- **`STANDARD_dark_code_compliance.md`** — the CHECK. Auditable, mechanical compliance checklist + `trugs-compliance-check` CLI specification. Every TRUGS-LLC public repo is graded against this.

The trinity flows: WHY you do it → HOW you do it → how you PROVE you did it.

## Related

- Upstream EPIC: [Xepayac/TRUGS-DEVELOPMENT#1548](https://github.com/Xepayac/TRUGS-DEVELOPMENT/issues/1548) — Bring TRUGS-LLC public portfolio to Dark Code compliance
- Foundation issue: [TRUGS-LLC/TRUGS#48](https://github.com/TRUGS-LLC/TRUGS/issues/48) — REFERENCE/ foundation: Dark Code trinity + trugs-compliance-check CLI
