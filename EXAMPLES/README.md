# TRUGS Examples

One strong example per domain demonstrating the TRUGS v1.0.0 specification. All examples pass validation (16 rules, 0 errors).

**Total:** 7 validated JSON files across 7 domains.

## Domains

| Domain | File | Nodes | Edges | Node Types |
|--------|------|-------|-------|------------|
| [knowledge/](knowledge/) | complex.json | 8 | 17 | CONCEPT, ENTITY, CLASS, INSTANCE |
| [living/](living/) | complex.json | 9 | 21 | QUERY, ANSWER, ENTITY, TOOL_EXECUTION, SYNTHESIS |
| [memory/](memory/) | session.trug.json | 3 | 1 | MODULE, DATA — LLM persistent memory |
| [nested/](nested/) | complex.json | 12 | 20 | TASK, SUBGRAPH, RESULT |
| [research/](research/) | complete.json | 8 | 10 | CONCEPT, CLAIM, SOURCE, PROJECT |
| [web/](web/) | complex.json | 9 | 13 | SITE, PAGE, SECTION |
| [writer/](writer/) | complex.json | 14 | 20 | DOCUMENT, SECTION, PARAGRAPH, CITATION, REFERENCE |

## Validate

```bash
python tools/validate.py --all EXAMPLES/
python tools/validate.py EXAMPLES/knowledge/complex.json
```

## More Examples

See [TRUGS-AGENT](https://github.com/TRUGS-LLC/TRUGS-AGENT) for applied examples: NDA agreements, project trackers, web research hubs, and memory systems — all built with TRUGs.
