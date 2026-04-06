# Graph-Driven Evidence Synthesis: How a Directed Graph Methodology Produced a More Comprehensive Understanding of Heart Health Than Traditional Literature Review

**Author:** Dr. William E. Leigh III DAOM
**Date:** 2026-04-05

---

## Abstract

This paper documents a novel methodology for medical evidence synthesis that combines three established approaches — scoping review, evidence mapping, and narrative synthesis — with a graph-based composition framework called TRUGS (Traceable Recursive Universal Graph Specification). Over the course of a single working session, six individual papers totaling approximately 41,000 words were authored on topics spanning evidence-based medicine, statin pharmacology, dietary alternatives, side effect management, and metabolic syndrome. These papers were then decomposed into 403 paragraph-level nodes, connected by 210 typed cross-paper edges (REFERENCES, DEPENDS_ON, SUPERSEDES, FEEDS), and the resulting directed graph was used to compose a seventh combined paper that resolved contradictions, eliminated redundancy, and produced a narrative structure that no linear review process could have identified.

The key finding: the SUPERSEDES edges — connections where newer or deeper evidence in one paper replaces a simpler treatment of the same topic in another — revealed 30 instances where the combined paper needed to choose between competing framings of the same data. Without the graph, these contradictions would have remained invisible, producing a combined document that contained internally inconsistent claims. With the graph, every contradiction was surfaced and resolved before composition began.

This paper describes the methodology, the specific decisions the graph forced, and the implications for evidence synthesis in any domain where multiple bodies of knowledge must be integrated.

---

## 1. The Problem: Why Traditional Review Fails at Scale

Medical evidence synthesis faces a structural problem. A single clinical question — "should I take a statin?" — touches pharmacology, epidemiology, genetics, nutrition, exercise physiology, behavioral psychology (the nocebo effect), metabolic endocrinology (insulin resistance), and health policy (clinical guidelines). No single paper can cover all of these domains with adequate depth. But a series of papers, each covering one domain, creates a different problem: redundancy, inconsistency, and the absence of cross-domain connections.

Consider a concrete example. The JUPITER trial (rosuvastatin in 17,802 healthy participants with elevated CRP) appears in our series four times:

1. **In the statin history paper (P2):** JUPITER is the tenth entry in a chronological table of eleven landmark trials, cited for its 44% composite event reduction and its demonstration that inflammation-based prescribing works.

2. **In the counter-arguments paper (P3):** JUPITER reappears as a case study in statistical framing — the 44% relative risk reduction becomes a 0.35% absolute risk reduction, an NNT of approximately 285.

3. **In the side effects paper (P5):** JUPITER reappears again for its diabetes signal — 270 new cases on rosuvastatin versus 216 on placebo, a 25% relative increase.

4. **In the metabolic paradox paper (P6):** JUPITER reappears a fourth time, now reframed by the 2024 CTT meta-analysis showing that high-intensity statins increase diabetes risk by 36%, with measurable retinal complications.

Each citation is accurate. Each serves its paper's argument. But they present four different framings of the same trial, and a reader encountering them in sequence would see the same study interpreted as a triumph (P2), a statistical illusion (P3), a side-effect signal (P5), and a metabolic warning (P6). Without explicit resolution, these framings coexist in tension.

A traditional literature review would not catch this. The reviewer would read each paper, extract key findings, and organize them thematically. The four JUPITER framings would likely all survive into the combined document, creating subtle internal contradictions that undermine the reader's ability to form a coherent understanding.

The graph catches it immediately. JUPITER is a node. The four citations are edges. The SUPERSEDES relationship between S6.2 (P6's CTT 2024 framing) and S5.9 (P5's simpler JUPITER framing) explicitly states: "CTT 2024 with 123,000 participants and dose-response data supersedes JUPITER's isolated observation." The combined paper knows which version to use and where.

---

## 2. The Methodology: Three Passes

The synthesis followed a three-pass approach, each pass increasing in granularity and each producing a durable artifact.

### Pass 1: Section-Level Outline (73 Nodes)

Each of the six papers was decomposed into its major sections and subsections. This produced 73 section-level nodes with one-sentence summaries capturing the key claim, study, or finding in each section. For example:

- **S2.5:** "P2 Randomized Controlled Trials — 11 landmark trials: 4S, WOSCOPS, CARE, LIPID, AFCAPS, HPS, ASCOT-LLA, PROVE IT, TNT, JUPITER, HOPE-3"
- **S5.5:** "P5 Vitamin D — 89% statin tolerance after supplementation in deficient patients"
- **S6.2:** "P6 What Statins Do to Metabolism — CTT 2024 (36% diabetes increase), METSIM (24% insulin sensitivity decrease), 5 mechanisms including She 2024 GLP-1 pathway"

At this level, the structure of each paper is visible but the cross-paper connections are not yet explicit. The section-level outline serves the same function as a table of contents — it tells you what exists and where to find it.

**Artifact produced:** A TRUG with 73 section nodes, 7 document nodes, and 15 reference-study nodes, connected by 7 document-level FEEDS edges.

### Pass 2: Paragraph-Level Outline (403 Nodes)

Each section was then decomposed into its individual paragraphs, each tagged with its specific claim, study name, and key numbers. This produced 403 paragraph-level nodes across the six papers:

| Paper | Paragraphs |
|-------|-----------|
| P1: Evidence-Based Medicine Pyramid | 79 |
| P2: History of Statin Drugs | 70 |
| P3: Should I Take a Statin? | 89 |
| P4: The Gundry Diet | 61 |
| P5: Managing Statin Side Effects | 64 |
| P6: The Statin-Metabolic Paradox | 40 |
| **Total** | **403** |

At this level, the specific claims are visible. "JUPITER showed 44% composite reduction" is a different node from "JUPITER showed 25% diabetes increase" — even though they describe the same trial. This granularity is where cross-paper connections become identifiable.

**Why paragraph-level matters:** Section-level nodes are too coarse to detect contradictions. "P2 discusses JUPITER" and "P5 discusses JUPITER" are both true at the section level, but they don't reveal that the two discussions present the same trial in incompatible frames. At the paragraph level, the specific framing is captured, and the SUPERSEDES relationship becomes explicit.

### Pass 3: Cross-Paper Edges (210 Edges)

Two parallel analysis processes identified every cross-paper connection at the paragraph level. Each edge was typed:

| Edge Type | Count | Purpose |
|-----------|-------|---------|
| REFERENCES | 78 | Same study, organization, or dataset cited in both paragraphs |
| DEPENDS_ON | 52 | Understanding paragraph A requires understanding paragraph B first |
| SUPERSEDES | 30 | Paragraph A provides newer, deeper, or more accurate data that replaces B's treatment |
| FEEDS | 50 | A's conclusion naturally raises the question B addresses |
| **Total** | **210** | |

**Artifact produced:** The complete TRUG — 90 nodes (sections + documents + reference studies), 190 edges (after deduplication from paragraph-level to section-level). This graph is the complete blueprint for composition.

---

## 3. What the Graph Revealed

### 3.1 The Hub Nodes: Studies That Connect Everything

The highest-connectivity nodes — the studies that appeared across the most papers — emerged naturally from the REFERENCES edges:

| Study | Papers | Angles |
|-------|--------|--------|
| CTT Collaboration | P2, P3, P5, P6 | Efficacy, transparency, side effects, diabetes 2024 |
| JUPITER Trial | P2, P3, P5, P6 | Trial results, ARR critique, diabetes signal, metabolic mechanism |
| PREDIMED Trial | P3, P4, P6 | Dietary alternative, lectin contradiction, insulin-neutral intervention |
| Framingham Heart Study | P1, P2, P3 | Cohort exemplar, epidemiological foundation, discordance data |

These hub nodes are the load-bearing studies of the entire series. The combined paper must handle each one with particular care — they are the studies the reader will encounter most often, and inconsistency in their treatment will be most noticeable.

A traditional review would not identify these hubs until the writing stage, when the reviewer discovers they keep citing the same studies and must improvise a way to avoid repetition. The graph identifies them before writing begins.

### 3.2 The SUPERSEDES Chains: Resolving Contradictions

The 30 SUPERSEDES edges were the most valuable output of the analysis. Each one represents a place where the combined paper must choose between two treatments of the same topic. Selected examples:

**Diabetes risk framing:**
- P5 (Side Effects paper) presents statin diabetes as: "JUPITER showed 25% relative increase; Sattar meta-analysis showed 9% increase; concentrated in pre-diabetic patients; 5 cardiovascular events prevented per 1 diabetes case."
- P6 (Metabolic Paradox paper) presents the same topic as: "CTT 2024 showed 36% increase with high-intensity statins; METSIM showed 24% insulin sensitivity decrease and 12% secretion decrease; She 2024 discovered microbiome-mediated GLP-1 suppression; the 5:1 trade-off framing understates the problem because it ignores the feedback loop."
- **Resolution:** P6's framing supersedes P5's. The combined paper uses CTT 2024 numbers (36%), not JUPITER alone (25%), and presents the 5 mechanisms rather than the simple trade-off. P5's 5:1 framing is noted as the clinical consensus but challenged by the feedback loop analysis.

**Nocebo effect:**
- P2 (History paper) mentions the nocebo effect in one paragraph within the "Controversies" section — a brief note that most reported side effects may be expectation-driven.
- P5 (Side Effects paper) dedicates three full paragraphs to the SAMSON trial (90% nocebo ratio), StatinWISE (no difference in muscle scores), and the CTT meta-analysis (>90% not caused by statin).
- **Resolution:** P5's treatment supersedes P2's. The combined paper places the full nocebo evidence in Part V and removes the brief mention from Part II entirely, replacing it with a forward reference.

**Beyond-statins alternatives:**
- P3 (Counter-Arguments paper) evaluates dietary supplements and lifestyle: Mediterranean diet, berberine, fiber, exercise, CoQ10.
- P6 (Metabolic Paradox paper) evaluates pharmaceutical root-cause alternatives: GLP-1 receptor agonists (SELECT trial), SGLT2 inhibitors (EMPA-REG, DAPA-HF, CREDENCE), and metformin (UKPDS).
- **Resolution:** P6's pharmacological alternatives supersede P3's supplement-level comparison for the metabolic syndrome population. The combined paper places supplements in Part IV and pharmaceuticals in Part VI, with an explicit narrative bridge: "Part IV examined what you can do without a prescription. Part VI examines what happens when the root cause requires pharmaceutical intervention."

Without the SUPERSEDES edges, these contradictions would have survived into the combined paper as subtle inconsistencies — the same topic framed differently in different sections, leaving the reader to reconcile them alone. The graph forces reconciliation before composition.

### 3.3 The FEEDS Chains: The Narrative Arc

The 50 FEEDS edges, when traced end-to-end, revealed the natural narrative arc of the combined paper:

```
P1 (pyramid)
  → "not all evidence is equal"
    → P2 (how strong is the statin evidence?)
      → "eleven RCTs and 170,000 participants"
        → P3 (what are the counter-arguments?)
          → "RRR vs ARR, NNT 250, data transparency"
            → P3 alternatives (Mediterranean diet, supplements)
              → P4 (Gundry — deep dive on one popular alternative)
            → P5 (side effects — what's real?)
              → "JUPITER diabetes signal"
                → P6 (the metabolic paradox)
                  → "are we treating the right thing?"
```

This arc was not designed. It emerged from the edges. The FEEDS relationships between paragraphs, when aggregated to the document level, produced a reading order that moves from framework (P1) through evidence (P2) through criticism (P3) through alternatives (P3+P4) through side effects (P5) to the systemic question (P6). Each paper's conclusion raises the question the next paper addresses.

A traditional reviewer would design this arc consciously, imposing a structure based on their understanding of the material. The graph-driven approach lets the structure emerge from the connections between the content itself. The distinction matters when the material is complex enough that the optimal structure is not obvious in advance.

### 3.4 The DEPENDS_ON Chains: Reader Prerequisites

The 52 DEPENDS_ON edges identified which concepts must be understood before which arguments can be followed. The longest chains revealed the deepest prerequisite structures:

**The metabolic paradox chain:**
```
S1.7 (what is an RCT?)
  → S2.5 (statin RCTs, including JUPITER)
    → S5.9 (JUPITER diabetes signal)
      → S6.2 (CTT 2024 mechanistic data)
        → S6.3 (7-step feedback loop)
```

Five links. A reader encountering the feedback loop in Part VI without having absorbed Parts I, II, and V would lack the context to evaluate the claim. The combined paper must either present these prerequisites in order or include sufficient recap at each stage.

**The Gundry evaluation chain:**
```
S1.3 (what is animal/in-vitro evidence?)
  → S1.4 (what is a case report?)
    → S4.1 (Gundry's poster abstracts are case-level evidence)
      → S4.11 (conclusion: Level 6 hypothesis contradicted by Level 3 population data)
```

This chain shows that the Gundry evaluation is structurally dependent on Part I's evidence hierarchy. A reader who skips Part I will not understand why Gundry's lectin hypothesis is classified at Level 6 or why Blue Zones population data (Level 3) outranks it.

---

## 4. The Composition Process

With the graph complete, the combined paper was composed using three rules derived from the edge types:

**Rule 1 (from FEEDS):** Follow the narrative arc. The document-level FEEDS chain (P1→P2→P3→P4→P5→P6) becomes the six-part structure.

**Rule 2 (from SUPERSEDES):** Use the newest, deepest version. When the same topic appears in multiple papers, the SUPERSEDES edges identify which treatment is authoritative. The other versions are either removed entirely or replaced with forward/backward references.

**Rule 3 (from REFERENCES):** Each study appears once in its primary context. The hub studies (CTT, JUPITER, PREDIMED, Framingham) are placed at the point in the narrative where they carry the most argumentative weight, and all other citations become cross-references: "As JUPITER demonstrated in Part II..."

**Rule 4 (from DEPENDS_ON):** Respect prerequisite order. No concept is introduced before its dependencies have been established. The DEPENDS_ON chains are checked against the proposed section order to ensure no forward references to unexplained concepts.

These four rules are deterministic. Given the same graph, any writer following them would produce the same structural decisions — the same section order, the same study placements, the same contradiction resolutions. The prose would differ but the architecture would be identical.

---

## 5. What the Graph Would Have Caught That Traditional Review Would Not

### 5.1 The Statin Diabetes Escalation

Across the six papers, the statin diabetes story escalated:
- P2 mentions it in one paragraph as a "~10% relative increase"
- P5 dedicates a full section, citing JUPITER (25%) and Sattar (9%)
- P6 reframes it entirely with CTT 2024 (36%), METSIM mechanisms, and the feedback loop

A traditional combined review, written linearly, would likely present the P2 framing first (10%), then the P5 framing (25%), then the P6 framing (36%) — giving the reader three different numbers for the same phenomenon without explaining why they differ. The graph's SUPERSEDES edges make the escalation explicit: 10% was the early estimate, 25% was trial-specific, 36% is the current best estimate from the largest analysis. The combined paper uses 36% as the authoritative number and explains the escalation in a footnote.

### 5.2 The PREDIMED Triple Role

PREDIMED appears in three papers with three different argumentative functions:
- P3: as the strongest dietary alternative to statins (~30% CV reduction)
- P4: as evidence contradicting Gundry's lectin avoidance (legumes were encouraged and outcomes improved)
- P6: as an insulin-neutral intervention that provides comparable CV protection without worsening metabolic health

A traditional review might cite PREDIMED three times with three different emphases, or might place it in one section and lose the other two arguments. The graph shows all three roles, and the combined paper places PREDIMED primarily in Part IV (alternatives) with explicit cross-references in Part IV's Gundry section and Part VI's root-cause alternatives.

### 5.3 The CoQ10 Thread

CoQ10 appears in three papers:
- P3: briefly, as a potential adjunct for statin side effects
- P5: in detail, with contradictory meta-analyses and dose considerations
- P6: as a diabetes mechanism — CoQ10 depletion damages pancreatic beta cells

A traditional review would likely place CoQ10 in the side effects section and miss the diabetes mechanism connection entirely. The graph's FEEDS edge from S5.4 (CoQ10 for muscles) to S6.2 (CoQ10 for beta cells) makes the cross-tissue connection explicit: "The same CoQ10 depletion that may cause muscle symptoms also damages the cells that produce insulin." This is a novel insight that emerged from the graph topology, not from any individual paper.

---

## 6. The TRUGS Methodology

### What Is a TRUG?

TRUG stands for Traceable Recursive Universal Graph Specification. A TRUG is a JSON file with three components: nodes (things), edges (relationships between things), and hierarchy (organization via parent/child containment). Every node has a unique identifier, a type, a label, and a summary. Every edge has a source, a target, and a typed relation.

The specification defines a 190-word formal vocabulary (TRUGS Language, or TRL) with exact definitions for every word. Edge relations use prepositions from this vocabulary: FEEDS, DEPENDS_ON, REFERENCES, SUPERSEDES, CONTAINS, IMPLEMENTS, EXTENDS. Node types use nouns: DOCUMENT, SECTION, REFERENCE, RECORD. The vocabulary is a closed set — no invented terms.

### Why Graphs for Evidence Synthesis?

Evidence synthesis is inherently a graph problem. Studies reference other studies. Findings depend on prior findings. Newer data supersedes older data. Clinical questions feed into other clinical questions. These relationships are typed and directional — they are edges in a directed graph, not items in a list.

Traditional review methods represent evidence as lists (reference lists), tables (comparison tables), or hierarchies (outline structures). All three are projections of a graph into a lower-dimensional structure that loses information:

- A reference list loses the relationships between references
- A comparison table loses the narrative flow between interventions
- An outline loses the cross-section dependencies

The TRUG preserves all three: which studies relate to which (REFERENCES), what order they must be presented (DEPENDS_ON and FEEDS), and where newer data replaces older (SUPERSEDES). The composition process reads the graph, not a list.

### The Three-Pass Protocol

The protocol used in this synthesis is generalizable to any multi-document evidence review:

**Pass 1 — Section-level decomposition.** Read each document. Produce one node per section with a one-sentence summary capturing the key claim or finding. Connect documents with FEEDS edges. This takes approximately 15 minutes per document and produces the structural skeleton.

**Pass 2 — Paragraph-level decomposition.** Expand each section into individual claim nodes. Each node must contain the specific study name, finding, and number — not a generic summary. This takes approximately 30 minutes per document and produces the content inventory.

**Pass 3 — Cross-document edges.** For each paragraph node, identify connections to paragraph nodes in other documents. Type each connection: does A reference the same study as B? Does understanding A require understanding B first? Does A provide newer data that replaces B? Does A's conclusion raise the question B addresses? This takes approximately 20 minutes per pair of documents and produces the synthesis blueprint.

**Composition** follows deterministically from the graph using four rules: follow FEEDS for narrative order, use SUPERSEDES for contradiction resolution, place each study at its REFERENCES hub with the most argumentative weight, and check DEPENDS_ON chains against section order.

---

## 7. Quantitative Results

### The Evidence Inventory

| Metric | Value |
|--------|-------|
| Source papers | 6 |
| Total source words | ~41,000 |
| Section-level nodes (Pass 1) | 73 |
| Paragraph-level nodes (Pass 2) | 403 |
| Cross-paper edges (Pass 3) | 210 |
| REFERENCES edges | 78 |
| DEPENDS_ON edges | 52 |
| SUPERSEDES edges | 30 |
| FEEDS edges | 50 |
| Hub studies (≥3 papers) | 4 (CTT, JUPITER, PREDIMED, Framingham) |
| Combined paper words | ~8,000 |
| Combined paper sections | 39 |
| Unified references | 70 |
| Contradictions resolved by SUPERSEDES | 30 |

### Compression Ratio

The combined paper (8,000 words) is 19.5% the length of the source material (41,000 words) while preserving all key findings, resolving all contradictions, and maintaining the complete argumentative structure. This compression is possible because the graph identifies and eliminates redundancy: the same study cited four times becomes one authoritative citation with three cross-references.

### Edge Density

The graph has 210 edges across 403 paragraph nodes, giving an edge density of 0.52 edges per node. This means approximately every other paragraph in the source material has a meaningful cross-paper connection. This is remarkably high and reflects the interconnected nature of the subject matter — statin pharmacology, metabolic endocrinology, nutritional epidemiology, and clinical guidelines are deeply entangled domains.

---

## 8. Limitations

**The methodology requires domain expertise at every stage.** The paragraph-level summaries, the edge typing, and the composition decisions all require understanding of the source material. The graph does not replace expertise — it organizes it.

**Edge identification is subjective.** Two analysts might identify different SUPERSEDES relationships or disagree on whether a connection is FEEDS versus DEPENDS_ON. The typed vocabulary constrains this subjectivity but does not eliminate it. Inter-rater reliability testing was not performed.

**The paragraph-level decomposition is labor-intensive.** 403 nodes across 6 papers required approximately 2 hours of agent computation time. Scaling to 20 or 50 papers would require automation of the decomposition step — feasible but not yet implemented.

**The combined paper favors brevity over depth.** At 8,000 words versus 41,000 words of source material, significant detail is necessarily lost. The combined paper is an evidence map, not a comprehensive review. Readers requiring full depth on any topic must consult the individual papers.

**The SUPERSEDES relationship assumes temporal ordering maps to quality.** "Newer supersedes older" is usually but not always correct. A 2024 meta-analysis may supersede a 2010 meta-analysis, but a well-designed 2010 trial may be more relevant to a specific population than a poorly designed 2024 observational study. The methodology does not currently weight study quality independent of recency.

---

## 9. Implications

### For Medical Evidence Synthesis

The traditional methods for combining evidence — systematic review, meta-analysis, clinical practice guideline development — are designed for single clinical questions. "Does drug X reduce outcome Y?" can be answered by pooling RCTs. But the question "What should I do about my heart health?" spans pharmacology, nutrition, genetics, metabolism, and health policy. No single systematic review can answer it.

The graph-based approach is designed for exactly this kind of cross-domain synthesis. It does not replace systematic review for narrowly defined questions — it complements it for broadly defined ones. The TRUG is not an alternative to Cochrane methodology; it is a tool for integrating Cochrane reviews with dietary trials, genetic studies, mechanistic research, and guideline analyses into a coherent whole.

### For Any Domain Requiring Multi-Source Integration

The methodology is not specific to medicine. Any domain where multiple bodies of knowledge must be integrated — law (statutes, case law, regulations, commentary), engineering (specifications, test data, failure analyses, standards), policy (research, stakeholder input, economic modeling, precedent) — faces the same structural problem: redundancy, inconsistency, and missing cross-connections.

The three-pass protocol (decompose into nodes, identify edges, compose from graph) is domain-agnostic. The edge types (REFERENCES, DEPENDS_ON, SUPERSEDES, FEEDS) are universal. The composition rules (follow FEEDS, resolve SUPERSEDES, place at strongest REFERENCES, check DEPENDS_ON) apply everywhere.

### For the Reader

If you have read this far, you now understand why the combined paper on heart health reads differently from a traditional review article. It reads as a single coherent argument because it was composed from a graph that made every cross-section connection explicit before a word of prose was written. The contradictions were resolved in the graph, not in the writing. The structure emerged from the edges, not from an outline imposed by the author.

The six individual papers remain available for depth. The combined paper provides the map. And this paper documents how the map was made.

---

## References

1. Arksey H, O'Malley L. Scoping studies: towards a methodological framework. *International Journal of Social Research Methodology*. 2005;8(1):19-32.
2. Miake-Lye IM, Hempel S, Shanman R, Shekelle PG. What is an evidence map? A systematic review of published evidence maps and their definitions, methods, and products. *Systematic Reviews*. 2016;5:28.
3. Popay J, Roberts H, Sowden A, et al. Guidance on the conduct of narrative synthesis in systematic reviews. *ESRC Methods Programme*. 2006.
4. Global Evidence Synthesis Initiative (GESI). Evidence and gap maps. https://www.gesi-ev.org
5. Ioannidis JPA. The mass production of redundant, misleading, and conflicted systematic reviews and meta-analyses. *Milbank Quarterly*. 2016;94(3):485-514.
6. Murad MH, Asi N, Alsawas M, Alahdab F. New evidence pyramid. *BMJ Evidence-Based Medicine*. 2016;21(4):125-127.
7. GRADE Working Group. Grading quality of evidence and strength of recommendations. *BMJ*. 2004;328:1490.
8. Reith C, et al. Effect of statin therapy on muscle symptoms: an individual participant data meta-analysis. *The Lancet*. 2022;400:1075-1084.
9. Reith C, et al. Statin therapy, diabetes, and glycaemia: individual participant data meta-analysis. *The Lancet Diabetes & Endocrinology*. 2024.
10. Ridker PM, et al. Rosuvastatin to prevent vascular events in men and women with elevated C-reactive protein (JUPITER). *New England Journal of Medicine*. 2008;359(21):2195-2207.
11. Estruch R, et al. Primary prevention of cardiovascular disease with a Mediterranean diet (PREDIMED). *New England Journal of Medicine*. 2018;378(25):e34.
12. She J, et al. Atorvastatin decreases Clostridium abundance, alters bile acid profiles, and reduces GLP-1 levels. *Cell Metabolism*. 2024.
13. Cederberg H, et al. Increased risk of diabetes with statin treatment in the METSIM cohort. *Diabetologia*. 2015;58:1109-1117.
14. Howard JP, et al. Side effect patterns in a crossover trial of statin, placebo, and no treatment (SAMSON). *Journal of the American College of Cardiology*. 2021;78(12):1210-1222.
15. Lincoff AM, et al. Semaglutide and cardiovascular outcomes in obesity without diabetes (SELECT). *New England Journal of Medicine*. 2023;389(24):2221-2232.

---

## Appendix: Source Papers

The six source papers and combined review were authored by Dr. William E. Leigh III DAOM and published on Medium under 8Vitality. The TRUG artifact (`heart_health_series.trug.json`) in this study folder is the graph that connected them.

| # | Paper | Medium URL |
|---|-------|-----------|
| P1 | The Evidence-Based Medicine Pyramid | [Published](https://medium.com/@DrLeigh3/the-evidence-pyramid-for-modern-medicine-753318962172) |
| P2 | The History of Statin Drugs | [Published](https://medium.com/@DrLeigh3/the-history-of-statin-drugs-tracking-cholesterol-treatment-through-the-evidence-pyramid-d2438fd9df32) |
| P3 | Should I Take a Statin? | *URL pending* |
| P4 | The Gundry Diet: Evidence Review | *URL pending* |
| P5 | Managing Statin Side Effects | *URL pending* |
| P6 | The Statin-Metabolic Paradox | *URL pending* |
| Combined | Heart Health: Complete Evidence Review | *URL pending* |
| Methodology | This paper | *URL pending* |
