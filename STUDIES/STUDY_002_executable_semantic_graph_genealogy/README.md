# STUDY 002: Intellectual Genealogy of Executable Semantic Graphs

A comprehensive research compilation tracing the two intellectual lineages — semantic graphs and executable graphs — from their origins to the present, identifying the gap that TRUGS fills.

## What This Proves

The exact term "Executable Semantic Graph" does not appear as an established concept in academic literature. Two lineages developed independently for 60+ years:

**Semantic lineage:** Quillian (1968) → Berners-Lee Semantic Web (1998) → RDF (1999) → OWL (2004) → Knowledge Graphs (2012)
- Carries meaning. Cannot execute.

**Executable lineage:** Petri (1962) → Dennis dataflow (1975) → TensorFlow (2015) → LangGraph (2024)
- Can execute. Carries no meaning.

No system in the literature fully combines all three properties:
1. **Semantic** — typed nodes/edges with formal domain meaning
2. **Executable** — the graph IS the program
3. **Self-modifying** — execution can alter the graph's own structure

The closest prior attempts (OWL-S 2001-2004, ExeKG 2022, graph rewriting 1973) each achieved one or two of these properties but never all three.

## Files

| File | Description |
|------|-------------|
| `PAPER_genealogy.md` | Full research: 7 sections covering semantic web, computational graphs, the combination attempts, modern LLM frameworks, self-modifying graphs, and the synthesis |

## Key Sources Identified

| System | Year | What It Does | What It Lacks |
|--------|------|-------------|---------------|
| Petri Nets | 1962 | Executable graph computation | No semantics, no self-modification |
| OWL + Reasoners | 2004 | Semantic inference on graphs | Not arbitrary execution, read-only |
| OWL-S / DAML-S | 2001-2004 | Semantic + service orchestration | Graph doesn't execute itself |
| Graph Rewriting (DPO) | 1973 | Formal self-modification | No domain semantics, no execution engine |
| Genetic Programming | 1988 | Programs-as-trees that evolve | External modification, no semantics, trees not graphs |
| TensorFlow | 2015 | Executable dataflow graph | No semantic meaning |
| ExeKG (Bosch) | 2022 | KG translated to executable scripts | KG itself doesn't execute |
| LangGraph | 2024 | LLM workflow orchestration graph | Not semantic, external engine drives execution |
