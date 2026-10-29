# TRUGS Paper

**Title:** TRUGS: A Formalized Language Specification for Executable Graph Communication Between Humans and Large Language Models

**Target:** arXiv preprint (cs.CL / cs.AI)

## Files

- `trugs.tex` — Main paper (LaTeX, NeurIPS style + natbib)
- `trugs.bib` — BibTeX bibliography
- `neurips_2023.sty` — NeurIPS 2023 style file (`\ProvidesPackage{neurips_2023}`, revision 2023/03/31)
- `generated/vocab_counts.tex` — the vocabulary counts and percentages the paper states, written by `tools/paper_vocab_counts.py` from `TRUGS_LANGUAGE/language.trug.json`; committed, and input by `trugs.tex`
- `generated/trl_counts.tex` — the example and listing counts the paper states, written by `tools/check_paper_trl.py` with the released `trugs-tools`; committed, and input by `trugs.tex`

## Build

The generated files are committed, so the paper builds from this directory alone. Upload the directory (including `generated/`) to [Overleaf](https://overleaf.com) or compile locally:

```bash
pdflatex trugs.tex
bibtex trugs
pdflatex trugs.tex
pdflatex trugs.tex
```

To regenerate the counts first, run from the repository root `python3 tools/paper_vocab_counts.py` and, with `trugs-tools` 2.4.0 installed so that `trug` is on the PATH, `python3 tools/check_paper_trl.py`; the second also checks every TRL listing of the paper with the released tool.

## Submit to arXiv

1. Compile to PDF and verify
2. Create archive: `tar czf trugs.tar.gz trugs.tex trugs.bib trugs.bbl neurips_2023.sty generated/vocab_counts.tex generated/trl_counts.tex`
3. Submit at https://arxiv.org/submit
4. Categories: cs.CL (primary), cs.AI (secondary)

## References

Spanning: controlled natural languages (Kuhn 2014, Attempto, CPL, PENG, Sydney OWL Syntax, Schwitter 2018), the earlier systems closest to TRUGS (OWL-S, Object-Process Methodology and OPCAT, Attempto, Schwitter 2018, Executable Knowledge Graphs), formal semantics (Montague 1973), deontic logic (von Wright 1951, Hohfeld 1919), RFC 2119, SQL (Chamberlin 1974, 2012), knowledge graphs (Bian 2025, Pan 2024), graph specs (RDF, OWL, JSON-LD, Neo4j), the executable-graph lineage (Petri 1962, Karp and Miller 1966, Dennis 1975, Hewitt 1973, Harel 1987, TensorFlow, Spark), semantic-network roots (Quillian 1968, Berners-Lee 2001), LLM protocols and agent frameworks (MCP, LangGraph, AutoGen, CrewAI, DSPy), structured output (Willard 2023, SLOT 2025), ontology (Gruber 1993), adjective ordering (Sproat and Shih 1991), functional programming (Hutton 2016), comparative law (Nyazee 2022), formal grammars (Backus 1959). The reference list is whatever `bibtex` writes to `trugs.bbl` from the citations in `trugs.tex`.
