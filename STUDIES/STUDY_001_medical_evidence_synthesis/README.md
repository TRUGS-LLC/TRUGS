# STUDY 001: Medical Evidence Synthesis — Heart Health

A demonstration of TRUGS-based evidence synthesis applied to six papers on heart health, statins, dietary alternatives, side effects, and metabolic syndrome.

## What This Proves

Six papers (41,000 words) were decomposed into 403 paragraph-level nodes and connected by 210 typed cross-paper edges. The resulting directed graph was used to compose a seventh combined paper that resolved 30 contradictions between sources, eliminated redundancy, and produced a narrative structure that emerged from the graph topology rather than being imposed by the author.

## Files

| File | Description |
|------|-------------|
| `heart_health_series.trug.json` | The TRUG — 90 nodes, 190 edges. The artifact. |
| `PAPER_methodology.md` | How the TRUG was built and what it revealed. |

## How to Read the TRUG

The TRUG contains three types of nodes:
- **DOCUMENT** — the six source papers and the combined paper
- **SECTION** — 73 sections across all papers with one-sentence summaries
- **REFERENCE** — 16 high-connectivity studies (CTT, JUPITER, PREDIMED, etc.)

And four types of edges:
- **FEEDS** — A's conclusion raises B's question (narrative flow)
- **DEPENDS_ON** — understanding A requires understanding B first (prerequisites)
- **REFERENCES** — same study cited in both (shared evidence)
- **SUPERSEDES** — A provides newer/deeper data replacing B (contradiction resolution)

## Source Papers

Published on Medium by Dr. William E. Leigh III DAOM under 8Vitality:

- [The Evidence-Based Medicine Pyramid](https://medium.com/@DrLeigh3/the-evidence-pyramid-for-modern-medicine-753318962172)
- [The History of Statin Drugs](https://medium.com/@DrLeigh3/the-history-of-statin-drugs-tracking-cholesterol-treatment-through-the-evidence-pyramid-d2438fd9df32)
- Should I Take a Statin? — *URL pending*
- The Gundry Diet: Evidence Review — *URL pending*
- Managing Statin Side Effects — *URL pending*
- The Statin-Metabolic Paradox — *URL pending*
