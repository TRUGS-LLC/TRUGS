# AGENT.md — TRUGS Specification Repository

<trl>
DEFINE "trugs_spec" AS NAMESPACE.
NAMESPACE trugs_spec CONTAINS MODULE trugs_language AND MODULE trugs_protocol.
MODULE trugs_language GOVERNS INTERFACE TRL.
MODULE trugs_protocol GOVERNS DATA graph.
</trl>

## What This Repository Is

This is the canonical TRUGS specification. It defines:

- **TRUGS CORE** — 7 required node fields, 3 required edge fields. The universal foundation.
- **TRUGS Language (TRL)** — 190 executable words. Every sentence compiles to a directed graph.
- **BRANCHES** — Domain-specific vocabularies layered on CORE.
- **Validation** — 16 rules (9 structural, 7 compositional).

<trl>
NAMESPACE trugs_spec REFERENCES ENDPOINT "https://github.com/TRUGS-LLC/TRUGS".
INTERFACE TRL CONTAINS 190 UNIQUE RECORD word.
EACH RECORD word BELONGS_TO EXACTLY A RECORD part_of_speech.
</trl>

## Repository Structure

| Path | Content |
|------|---------|
| `TRUGS_LANGUAGE/` | TRL vocabulary, grammar, examples |
| `TRUGS_PROTOCOL/` | CORE, BRANCHES, fundamentals, validation |
| `REFERENCE/` | Dark Code paper, standard, how-to guide |
| `EXAMPLES/` | Example TRUG JSON files |
| `PAPER/` | Academic paper source (LaTeX) |
| `tools/` | Validation tooling (will migrate to `trugs-tools` in `trugs` 2.0.0 release) |
| `folder.trug.json` | Structural truth for this repo |

## Companion package: `trugs-tools`

As of `trugs` 2.0.0 (breaking, shipping post-soak on 2026-05-02), this repository will contain the spec only — no CLIs. All tooling lives at [TRUGS-LLC/TRUGS-TOOLS](https://github.com/TRUGS-LLC/TRUGS-TOOLS) and is installed separately:

```bash
pip install trugs-tools    # provides the `tg` binary
tg --help                  # 36 operations under 21 top-level verbs + 3 sub-namespaces
```

This repo describes data. The companion repo implements tools. See `principle_spec_is_data` in the portfolio EPIC.

## Rules for This Repository

<trl>
AGENT SHALL_NOT WRITE ANY FILE 'that CONTRADICTS INTERFACE TRL.
AGENT SHALL VALIDATE EACH RECORD change SUBJECT_TO 16 REQUIRED RECORD rule.
AGENT MAY READ FILE folder.trug.json 'for RECORD structure.
AGENT MAY READ FILE "TRUGS_LANGUAGE/SPEC_vocabulary.md" 'for DATA vocabulary.
</trl>

### Sugar — 'words

Sugar is a pattern (`'[a-z_]+`), not a fixed word list. Any tick-prefixed lowercase token is sugar. Sugar compiles to nothing — it exists for human readability.

<trl>
EACH RECORD sugar MATCHES RECORD pattern "'[a-z_]+".
PROCESS validator SHALL STRIP ALL RECORD sugar 'before VALIDATE.
</trl>

## License

Apache 2.0. See LICENSE and NOTICE files.

<trl>
NAMESPACE trugs_spec SUBJECT_TO FILE LICENSE.
FILE NOTICE GOVERNS RECORD patent_boundary.
</trl>

## Related Repositories

- [TRUGS-AGENT](https://github.com/TRUGS-LLC/TRUGS-AGENT) — LLM development framework using TRL + AAA + EPIC + Memory
- [TRUGS-SDK](https://github.com/TRUGS-LLC/TRUGS-SDK) — Installable Python toolchain
