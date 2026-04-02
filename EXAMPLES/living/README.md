# Living Branch Example

`complex.json` — 9 nodes, 21 edges. Multi-query research with synthesis across multiple data sources.

## Node Types

- **QUERY** — User question or information request
- **TOOL_EXECUTION** — Invocation of an external tool or API
- **ENTITY** — Extracted data or fact from a tool execution
- **SYNTHESIS** — Aggregation or comparison of multiple entities
- **ANSWER** — Final response to a query

## Edge Types

- **triggers** — Query triggers a tool execution
- **produces** — Tool execution produces an entity
- **synthesizes_to** — Entity feeds into a synthesis node
- **builds_on** — A node builds on prior results
- **cites** — Answer cites a source entity
