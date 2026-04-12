# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.1] - 2026-04-10

### Fixed
- M1: `save_graph` resolves symlinks before atomic write (no longer orphans target)
- M2: `_parse_duration_days` caps at 365,000 days (OverflowError -> ValueError)
- L1: `init_memory_graph` version bumped to 1.2.0 (was stuck at 1.0.0)
- L2: `_parse_duration_days` rejects None/int/whitespace inputs
- L3: `_idempotency_key` uses SHA-256 hash instead of raw join
- I1: `_render_memory` collapses multi-line body to single line
- I2: `memory_import` reads from resolved path (closes TOCTOU window)

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
