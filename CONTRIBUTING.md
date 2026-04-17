# Contributing to TRUGS

Thanks for your interest in contributing to TRUGS — the Traceable Recursive Universal Graph Specification. This document describes how to propose changes, what quality gates apply, and how the project works.

## Quick links

- **License:** [Apache 2.0](LICENSE) — all contributions are licensed under the same terms
- **Compliance standard:** [`REFERENCE/STANDARD_dark_code_compliance.md`](REFERENCE/STANDARD_dark_code_compliance.md) — what every TRUGS-LLC repo is audited against
- **How-to guide:** [`REFERENCE/PAPER_how_to_code_with_trugs.md`](REFERENCE/PAPER_how_to_code_with_trugs.md) — practitioner reference
- **Issue tracker:** [github.com/TRUGS-LLC/TRUGS/issues](https://github.com/TRUGS-LLC/TRUGS/issues)

## Types of contribution

| Change | Path |
|---|---|
| **Typo, doc clarity, single-line fix** | Branch → PR. No issue required. |
| **Spec / vocabulary / branch addition** | Issue first. The AAA protocol applies — see [`PAPER_how_to_code_with_trugs.md`](REFERENCE/PAPER_how_to_code_with_trugs.md) §5. |
| **New tool or feature** | Issue first. Requires human validation at the planning gate before coding. |
| **Bug fix with non-obvious cause** | Issue first. Tests required. |

If you're unsure, open an issue and ask. That is always cheaper than writing code that we can't merge.

## Workflow

1. **Fork + branch.** Create a feature branch off `main`. Branch naming:
   - `fix/<short-desc>` for bug fixes
   - `feat/<short-desc>` for features
   - `chore/<short-desc>` for maintenance
   - `docs/<short-desc>` for docs-only changes
2. **Write a TRUG/L-commented test.** Every behavior change needs a test. Every test needs an `AGENT SHALL VALIDATE ...` comment naming what it verifies. See [`PAPER_how_to_code_with_trugs.md`](REFERENCE/PAPER_how_to_code_with_trugs.md) §2 Step 4.
3. **Run compliance locally.**
   ```bash
   pip install -e .
   trugs-compliance-check .
   trugs-folder-check .
   pytest tools/
   ```
   All three must pass.
4. **Commit.** Use Conventional Commits format:
   ```
   <type>(<scope>): <imperative summary>

   <body — what changed and why>
   ```
5. **Open a PR.** Link the issue (if any), describe the change, include a test plan. A human will review and merge.

## Quality gates (what CI enforces)

Every PR runs three gates:

- **Build** — package installs cleanly, pytest passes
- **Compliance** — `trugs-compliance-check` may not decrease. Baseline is ratcheted only upward.
- **Graph** — `trugs-folder-check` reports zero errors on `folder.trug.json`

A PR that fails any gate cannot merge. The gate output names the specific failing check.

## Human-in-the-middle

Automated agents (Claude Code, etc.) can open PRs, but **only humans merge** into `main`. This is non-negotiable — it's how we keep the repo's intent accountable to a person. If you're an agent: open the PR, link the issue, stop.

## Reporting vulnerabilities

Security issues do not go in the public issue tracker. See [`SECURITY.md`](SECURITY.md) for private disclosure.

## Code of conduct

Be decent. Assume good faith. Criticize ideas, not people. We reserve the right to remove contributions and contributors that make the project less welcoming.

## Questions

Open a discussion or an issue. Either works.
