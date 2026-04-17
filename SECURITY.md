# Security Policy

## Reporting a vulnerability

**Do not open a public issue for security problems.** Instead, report privately via GitHub's security advisory workflow:

1. Go to [github.com/TRUGS-LLC/TRUGS/security/advisories/new](https://github.com/TRUGS-LLC/TRUGS/security/advisories/new)
2. Fill in the details: the bug, its impact, how to reproduce it
3. We'll respond within 5 business days

If you cannot use GitHub Security Advisories, email `xepayac@gmail.com` with `[TRUGS SECURITY]` in the subject line.

## What counts as a security issue

- Code injection, path traversal, or arbitrary file read/write in the reference tools (`tools/*.py`)
- A crafted TRUG or TRUG/L sentence that causes resource exhaustion, infinite loops, or memory blowup in the validator, parser, or compiler
- A validation rule that can be bypassed in a way that silently produces an invalid graph
- Dependency vulnerabilities with a plausible exploitation path against the reference tools

Bugs that are not security issues (just file a normal issue):
- A validation rule that rejects a technically-valid TRUG
- A parser error on valid TRUG/L input
- Performance problems without an exploitation path

## Supported versions

Only the latest published version on PyPI (`pip install trugs`) receives security fixes. TRUGS is pre-1.0 semantically; breaking changes can happen at any minor version.

| Version | Supported |
|---------|-----------|
| Latest on PyPI | Yes |
| Prior versions | No — upgrade |

## Our commitment

- Acknowledge receipt within 5 business days
- Keep you informed during investigation
- Credit you in the advisory and CHANGELOG (unless you prefer anonymity)
- Publish a fix within 30 days for high/critical findings, or explain why more time is needed

## Scope

This policy covers `TRUGS-LLC/TRUGS` — the specification, reference tools, and documentation in this repository. For other TRUGS-LLC repositories, see their individual `SECURITY.md` files.
