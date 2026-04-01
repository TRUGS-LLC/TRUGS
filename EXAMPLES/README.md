# TRUGS Examples Gallery

Examples for **7 domains** demonstrating the TRUGS v1.0.0 specification. All examples pass validation (16 rules, 0 errors).

**Total:** 20 validated JSON files across 7 domains.

## Domains

| Domain | Files | Node Types |
|--------|-------|------------|
| [knowledge/](knowledge/) | 3 (simple, medium, complex) | CONCEPT, ENTITY, CLASS, INSTANCE |
| [living/](living/) | 3 (simple, medium, complex) | QUERY, ANSWER, ENTITY, TOOL_EXECUTION, SYNTHESIS |
| [memory/](memory/) | 1 (session) | MODULE, DATA — LLM persistent memory |
| [nested/](nested/) | 3 (simple, medium, complex) | TASK, SUBGRAPH, RESULT |
| [research/](research/) | 2 (minimal, complete) | CONCEPT, CLAIM, SOURCE, PROJECT |
| [web/](web/) | 4 (minimal, medium, complex, complete) | SITE, PAGE, SECTION |
| [writer/](writer/) | 4 (minimal, medium, complex, complete) | DOCUMENT, SECTION, PARAGRAPH, CITATION, REFERENCE |

## Tiers

| Tier | Description | Typical Nodes |
|------|-------------|---------------|
| `minimal.json` / `simple.json` | Minimal structure | 3 |
| `medium.json` | Medium complexity with relationships | 5-9 |
| `complex.json` / `complete.json` | Full feature demonstration | 8-15 |

## Validate

```bash
python tools/validate.py --all EXAMPLES/
python tools/validate.py EXAMPLES/memory/session.trug.json
```
