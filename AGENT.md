# AGENT.md — TRUGS Specification Repository

<trl>
DEFINE "trugs_spec" AS NAMESPACE.
NAMESPACE trugs_spec CONTAINS MODULE trugs_language AND MODULE trugs_protocol.
MODULE trugs_language GOVERNS INTERFACE trl.
MODULE trugs_protocol GOVERNS DATA graph.
</trl>

## What This Repository Is

This is the canonical TRUGS specification. It defines:

- **TRUGS CORE** — 7 required node fields, 3 required edge fields. The universal foundation.
- **TRUGS Language (TRL)** — 233 executable words across 9 parts of speech. Every sentence compiles to a directed graph.
- **BRANCHES** — Domain-specific vocabularies layered on CORE.
- **Validation** — 16 rules (9 structural, 7 compositional).

<trl>
INTERFACE trl SHALL DEFINE 233 RECORD word.
INTERFACE trl SHALL DEFINE 9 RECORD part_of_speech.
</trl>

## Repository Structure

| Path | Content |
|------|---------|
| `TRUGS_LANGUAGE/` | TRL vocabulary, grammar, examples |
| `TRUGS_PROTOCOL/` | CORE, BRANCHES, fundamentals, validation |
| `REFERENCE/` | Dark Code paper, standard, how-to guide |
| `EXAMPLES/` | Example TRUG JSON files |
| `PAPER/` | Academic paper source (LaTeX) |
| `tools/` | `build_language_trug.py` only — regenerates `language.trug.json` from `SPEC_vocabulary.md`. All other tooling moved to `trugs-tools` at the 2.0.0 release. |
| `folder.trug.json` | Structural truth for this repo |

## Companion package: `trugs-tools`

As of `trugs` 2.0.0 (breaking), this repository contains the spec only — no CLIs. All tooling lives at [TRUGS-LLC/TRUGS-TOOLS](https://github.com/TRUGS-LLC/TRUGS-TOOLS) and is installed separately:

```bash
pip install trugs-tools    # provides the `trug` binary
trug --help                # 8 language verbs: validate, trl, get, update, delete, unlink, compliance, audit
```

This repo describes data. The companion repo implements tools. See `principle_spec_is_data` in the portfolio EPIC.

## Rules for This Repository

<trl>
AGENT SHALL_NOT WRITE ANY FILE SUBJECT_TO RECORD trl_violation.
AGENT SHALL VALIDATE EACH RECORD change SUBJECT_TO RECORD rule.
AGENT MAY READ FILE folder_trug.
AGENT MAY READ FILE vocabulary.
</trl>

### Sugar — 'words

Sugar is a pattern (`'[a-z_]+`), not a fixed word list. Any tick-prefixed lowercase token is sugar. Sugar compiles to nothing — it exists for human readability.

<trl>
PROCESS validator SHALL FILTER ALL RECORD sugar.
</trl>

## License

Apache 2.0. See LICENSE and NOTICE files.

<trl>
NAMESPACE trugs_spec SUBJECT_TO FILE license.
FILE notice GOVERNS RECORD patent_boundary.
</trl>

## Related Repositories

- [TRUGS-AGENT](https://github.com/TRUGS-LLC/TRUGS-AGENT) — LLM development framework using TRL + AAA + EPIC + Memory
- [TRUGS-SDK](https://github.com/TRUGS-LLC/TRUGS-SDK) — Installable Python toolchain
