# TRUGS Paper

**Title:** TRUGS: A Formalized English Specification for Executable Graph Communication Between Humans and Large Language Models

**Target:** arXiv preprint (cs.CL / cs.AI)

## Files

- `trugs.tex` — Main paper (LaTeX, NeurIPS style + natbib)
- `trugs.bib` — BibTeX bibliography (25 references)
- `neurips_2024.sty` — NeurIPS 2024 style file

## Build

Upload to [Overleaf](https://overleaf.com) or compile locally:

```bash
pdflatex trugs.tex
bibtex trugs
pdflatex trugs.tex
pdflatex trugs.tex
```

## Submit to arXiv

1. Compile to PDF and verify
2. Create archive: `tar czf trugs.tar.gz trugs.tex trugs.bib trugs.bbl neurips_2024.sty`
3. Submit at https://arxiv.org/submit
4. Categories: cs.CL (primary), cs.AI (secondary)

## References (25)

Spanning: controlled natural languages (Kuhn 2014, Attempto, CPL, PENG), formal semantics (Montague 1973), deontic logic (von Wright 1951, Hohfeld 1919), RFC standards (2119, 8259), SQL (Chamberlin 1974), knowledge graphs (Bian 2025, Pan 2024), graph specs (RDF, OWL, JSON-LD, Neo4j), LLM protocols (MCP 2025), structured output (Willard 2023, SLOT 2025), ontology (Gruber 1993), formal grammars (Backus 1959).
