# TRUGS spec repo — single-command specification checks.
# `make check` runs the following checks:
#   Industry baseline: secrets / format / lint / types / tests
#   Self-description: shipped TRUGs validate against TRUGS's
#                     own 16-rule CORE via `trug validate`
#
#   make check    # run the full gate (each step prints PASS/FAIL)
#   make dev      # install the dev tooling (ruff, mypy, pytest)
#   make trugs    # Layer-4 only: validate the shipped TRUGs
#
# gitleaks is optional locally (not pip-installable; CI installs the free gitleaks
# CLI binary and runs `make check` end-to-end). `trug` (trugs-tools) is optional locally
# too — `make check` skips each with a notice if not on PATH, so the lint/type/test
# core always runs.

.PHONY: check dev gitleaks fmt-check lint types test trugs

check: gitleaks fmt-check lint types test trugs
	@echo "=== GREEN: all checks passed ==="

dev:
	pip install -e '.[dev]'

gitleaks:
	@if command -v gitleaks >/dev/null 2>&1; then \
		echo "==> gitleaks"; gitleaks detect --source=. --no-git --redact && echo "PASS: gitleaks"; \
	else \
		echo "SKIP: gitleaks not installed locally (CI installs the free CLI and runs it)"; \
	fi

fmt-check:
	@echo "==> ruff format --check"; ruff format --check . && echo "PASS: format zero-diff"

lint:
	@echo "==> ruff check"; ruff check . && echo "PASS: lint zero-warning"

types:
	@echo "==> mypy"; mypy tools/ && echo "PASS: types zero-error"

test:
	@echo "==> pytest"; pytest -q && echo "PASS: tests"

# Self-description: the spec proves itself — every TRUG the spec ships validates
# against TRUGS's own 16-rule CORE validator. language.trug.json must also be a
# deterministic rebuild of SPEC_vocabulary.md, and every <trl> block in the
# repository's Markdown must compile with trugs-tools.
trugs:
	@if command -v trug >/dev/null 2>&1; then \
		echo "==> trug validate (shipped TRUGs)"; \
		for t in folder.trug.json tools/folder.trug.json TRUGS_LANGUAGE/language.trug.json $$(find EXAMPLES STUDIES -name '*.json'); do \
			trug validate "$$t" && echo "  VALID  $$t" || { echo "  FAIL   $$t"; exit 1; }; \
		done; \
		echo "==> deterministic rebuild check"; \
		tmp=$$(mktemp); python3 tools/build_language_trug.py TRUGS_LANGUAGE/SPEC_vocabulary.md "$$tmp" >/dev/null; \
		diff "$$tmp" TRUGS_LANGUAGE/language.trug.json >/dev/null && echo "  PASS: language.trug.json is a deterministic rebuild" || { echo "  FAIL: rebuild differs"; rm -f "$$tmp"; exit 1; }; \
		rm -f "$$tmp"; \
		echo "==> trug audit markdown (every <trl> block compiles)"; \
		trug audit markdown . && echo "  PASS: every <trl> block compiles" || { echo "  FAIL: a <trl> block does not compile"; exit 1; }; \
		echo "PASS: Layer-4 spec-proves-itself"; \
	else \
		echo "SKIP: trug (trugs-tools) not installed — Layer-4 shipped-TRUG validation skipped (run: pip install trugs-tools)"; \
	fi
