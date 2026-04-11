# Intellectual Genealogy of Executable Semantic Graphs

**Type:** Knowledge Base / Research Compilation
**Date:** 2026-04-05
**Purpose:** Trace the intellectual lineage of the Executable Semantic Graph concept that TRUGS builds upon

---



I now have comprehensive research material. Here is the full report.

---

# Intellectual Genealogy of Executable Semantic Graphs

## 1. SEMANTIC WEB / KNOWLEDGE GRAPHS LINEAGE

### Prehistoric Roots: Semantic Networks (1956-1975)

The concept of representing knowledge as a graph predates computers. The lineage traces to:

- **Richard H. Richens (1956)** — First proposed "semantic nets" for machine translation at the Cambridge Language Research Unit.
- **M. Ross Quillian (1962-1968)** — Built the first computational semantic network as part of the SYNTHEX project at System Development Corporation. His 1968 PhD thesis "Semantic Memory" at Carnegie Mellon formally defined semantic networks as a knowledge representation: nodes are concepts, links are typed relationships. This is the paper most modern derivatives cite.
- **Allan Collins and M. Ross Quillian (1969)** — "Retrieval Time from Semantic Memory" — the hierarchical network model, first to capture differences between superordinate and basic-level concepts. Introduced spreading activation.
- **Allan Collins and Elizabeth Loftus (1975)** — "A Spreading-Activation Theory of Semantic Processing" — revised Quillian's model, replaced strict hierarchy with weighted associative links. This is the direct intellectual ancestor of modern graph-based knowledge representations.

### Tim Berners-Lee and the Semantic Web (1989-2001)

- **1989** — Berners-Lee writes "Information Management: A Proposal" at CERN — the original web proposal.
- **1994** — First International World Wide Web Conference in Geneva. Berners-Lee describes the Web as "a flat, boring world devoid of meaning" for computers and discusses the need for semantics.
- **1998** — Berners-Lee publishes "Semantic Web Road Map", outlining the architecture for a web of machine-processable data. This is the foundational design document.
- **2001, May** — The seminal paper: Tim Berners-Lee, James Hendler, and Ora Lassila, "The Semantic Web: A New Form of Web Content That is Meaningful to Computers Will Unleash a Revolution of New Possibilities" in Scientific American. This is the paper that launched the field.

### RDF — Resource Description Framework (1997-2004)

- **1997** — First RDF specification drafted by Ora Lassila (Nokia) and Ralph Swick (W3C).
- **1999, February 24** — W3C publishes the first recommended RDF specification: "RDF Model and Syntax Specification" (RDF M&S), coauthored by Lassila and Swick. RDF defines the triple model: subject-predicate-object.
- **2000** — RDF Schema Specification candidate recommendation, coedited by Dan Brickley and R.V. Guha.
- **2004** — RDF revised specifications published as W3C Recommendations. RDF becomes the backbone data model for the Semantic Web.

### OWL — Web Ontology Language (2001-2012)

- **2001, March** — DAML+OIL specification published, the precursor to OWL. The DARPA Agent Markup Language (DAML) combined with the Ontology Inference Layer (OIL).
- **2001, November** — W3C Web Ontology Working Group chartered, operating until May 2004.
- **2004, February 10** — OWL 1.0 published as W3C Recommendation. Three sublanguages: OWL Lite, OWL DL, OWL Full. OWL is a computational logic-based language — knowledge expressed in OWL can be reasoned with by computer programs to verify consistency or make implicit knowledge explicit. This is a critical milestone: OWL reasoning is a form of execution on a semantic graph.
- **2009** — OWL 2 published as W3C Recommendation.
- **2012** — OWL 2 Second Edition.

### SPARQL (2004-2013)

- Developed by Eric Prud'hommeaux (W3C) and Andy Seaborne.
- **2008, January 15** — SPARQL 1.0 acknowledged by W3C as official recommendation. The graph query language for RDF.
- **2013, March** — SPARQL 1.1 published. Added Update (write operations), Federated Query (cross-server queries), and entailment regimes (reasoning during query).

### The Term "Knowledge Graph" — Who Coined It?

- **1972** — The term "knowledge graph" was coined by Austrian linguist **Edgar W. Schneider**, in a discussion of how to build modular instructional systems for courses. This is decades before Google.
- **Late 1980s** — University of Groningen and University of Twente jointly began work on knowledge graphs in education.
- **2012, May 16** — **Google announces the Google Knowledge Graph** — an engineering SVP published "Introducing the Knowledge Graph: things, not strings." Google popularized the term but did not coin it. The announcement caused academia to adopt "knowledge graph" loosely to refer to systems integrating data with graph structure — essentially a rebranding of Semantic Web / linked data concepts.
- Emil Eifrem (Neo4j) has been quoted confirming Google "embraced semantic technology and coined the term Knowledge Graph in 2012" — but this is inaccurate regarding coinage; Google popularized it in the tech industry.

### DBpedia and Wikidata

- **2007** — DBpedia initiated by Soren Auer, Christian Bizer, Georgi Kobilarov, Jens Lehmann, Richard Cyganiak, and Zachary Ives. Extracts structured content from Wikipedia into RDF. Became the nucleus for the Web of Open Data.
- **2012, October 29** — Wikidata launched by Wikimedia Foundation. First new Wikimedia project since 2006. A collaboratively edited knowledge base, providing structured data to Wikipedia and beyond.

### Property Graphs vs. RDF: The Neo4j/Cypher Approach vs. W3C

- **2000** — Emil Eifrem sketches the idea for a graph database "on the back of a napkin during his flight to Mumbai."
- **2007** — Neo4j incorporated as Neo Technology in Malmo, Sweden. Founders: Emil Eifrem (CEO), Johan Svensson, Peter Neubauer. Eifrem is credited with coining the term "graph database" and developing the **property graph model** — nodes and edges can have internal structure (key-value attributes).
- The core distinction: **RDF** uses triples (subject-predicate-object) — everything is broken into atomic statements. The RDF model was designed for data exchange and the open/linked data web. **Property graphs** use a higher level of abstraction — nodes and relationships are first-class with embedded attributes. Property graphs assume a closed-world model (only stored data is true); RDF operates under open-world assumption.
- RDF has SPARQL + OWL reasoning. Property graphs have Cypher (Neo4j) and Gremlin (TinkerPop) — traversal-optimized query languages.
- The two worlds are converging: Neo4j now maintains neosemantics (n10s) for RDF integration including SHACL validation and RDF* edge properties.

### "Semantic Graph" vs. "Knowledge Graph" — Terminology

The terms were never cleanly separated in academic literature. "Semantic graph" refers to any graph where the meaning of relationships is embedded in the graph itself and exposed in a standard format — essentially any RDF graph. "Knowledge graph" became the industry marketing term after Google's 2012 announcement. In practice: a "semantic graph" emphasizes the formal semantics (RDF/OWL reasoning capability), while "knowledge graph" emphasizes the practical integration of heterogeneous data sources. Most practitioners use them interchangeably, with "knowledge graph" dominant since 2012.

---

## 2. EXECUTABLE GRAPHS / COMPUTATIONAL GRAPHS LINEAGE

### Karp-Miller Computation Graphs (1966)

- **Richard M. Karp and Raymond E. Miller (1966-1969)** — "Parallel Program Schemata" introduced a mathematical model for parallel computation. One of the earliest theories treating computation explicitly as a graph structure. Published in the Journal of Computer and Systems Sciences, with earlier IBM reports from 1964.

### Petri Nets (1962)

- **Carl Adam Petri (1962)** — Doctoral dissertation "Kommunikation mit Automaten" (Communication with Automata), submitted to the Science Faculty of Darmstadt Technical University in July 1961, published 1962. English translation published 1966.
- Petri nets are bipartite graphs: places (conditions) and transitions (events), with tokens representing state. They formalized the basis for a theory of communication between asynchronous components.
- Key insight: Petri's construction is computationally universal. He proposed asynchronous computing architectures that challenged conventional synchronous systems.
- Petri nets are arguably the first "executable graph" — the graph itself defines the computation, and execution proceeds by firing transitions when tokens are available.

### Dataflow Programming — Jack Dennis, MIT (1960s-1970s)

- **Jack Dennis, late 1960s** — At MIT, began exploring alternatives to the von Neumann model, proposing static dataflow architectures to enable fine-grained parallelism without centralized control.
- **1975** — Jack Dennis and David Misunas at MIT wrote "A Preliminary Architecture for a Basic Data-Flow Processor" — a landmark paper laying out a novel concept for organizing computation where individual instructions (codelets) execute as soon as data becomes available.
- Dataflow graphs are explicitly executable: edges carry data tokens, nodes fire when all inputs are available. The graph IS the program. This is the most direct ancestor of the "executable graph" concept.

### Actor Model — Carl Hewitt (1973)

- **1973** — Carl Hewitt, Peter Bishop, and Richard Steiger publish "A Universal Modular ACTOR Formalism for Artificial Intelligence" at IJCAI. Proposed a modular architecture based on a single kind of object: actors.
- Actors communicate via asynchronous message passing. Each actor is a graph node with a mailbox. The system is a graph of communicating actors.
- The Actor model influenced Erlang, Akka, and modern distributed systems. It models computation as a graph of autonomous entities passing messages — executable graph nodes.
- Hewitt's work spanned 30+ years (1973-2006), with the lambda calculus viewed as the earliest message-passing programming language.

### Harel Statecharts (1987)

- **David Harel, 1987** — "Statecharts: A Visual Formalism for Complex Systems" published in Science of Computer Programming (received December 1984, revised July 1986).
- Extended conventional state machines with hierarchy, concurrency, and communication. Statecharts are executable specifications — the visual graph can be directly interpreted as a running system.
- Enormously influential: the basis for UML state diagrams, and the direct ancestor of XState (modern JavaScript state machine library). Statecharts are used in embedded systems, protocol design, and reactive system specification.
- Key contribution: a graph formalism that is both human-readable AND directly executable.

### Graph Reduction in Functional Programming (1970s-1980s)

- **Peter Henderson and James H. Morris Jr., 1976** — "A Lazy Evaluator" introduced lazy evaluation via graph reduction.
- **David Turner, 1976** — Incorporated lazy evaluation into SASL using combinators. Turner's work (1972 onwards) pioneered the implementation of functional languages via combinator graph reduction.
- Programs are compiled to lambda calculus expressions, then to graph data structures. Execution is graph reduction — rewriting the graph until it reaches normal form. The program literally IS a graph, and execution IS graph transformation.

### Graph Rewriting / Graph Transformation (1973-)

- **Hartmut Ehrig, Manfred Pfender, Hans-Jurgen Schneider (1973)** — "Graph-grammars: An algebraic approach" at the 14th Annual Symposium on Switching and Automata Theory. Introduced pushout constructions as a categorical framework for graph transformation.
- Double Pushout (DPO) rewriting: a rigorous formalism where computation is defined as rule-based transformation of graph structures. This is self-modifying graph computation — the graph changes its own structure according to rules.
- The algebraic approach to graph transformation laid the foundation for an entire field, with the Handbook of Graph Grammars (multi-volume) as the canonical reference.

### BPMN — Business Process Graphs (2004-)

- **2004** — Business Process Modeling Notation developed by the Business Process Management Initiative.
- **2005** — Object Management Group (OMG) took over management.
- **2011, January** — BPMN 2.0 released — renamed to Business Process Model and Notation. Critically, BPMN 2.0 introduced **execution semantics** alongside the existing notational elements. This made BPMN graphs directly executable by process engines (Camunda, etc.).
- BPMN is an executable graph for business processes — the diagram IS the program.

### TensorFlow and ML Computational Graphs (2010-2015)

- **Theano (2007/2010)** — Developed by MILA (Montreal Institute for Learning Algorithms) at University of Montreal, under Yoshua Bengio's group. First public release 2010 (SciPy presentation). Theano defined computational graphs with symbolic variables — the graph is compiled and optimized before execution. Theano was the precursor that proved the computational graph paradigm for deep learning. Development ceased 2017.
- **TensorFlow (2015, November)** — Released by Google as open-source. The paper explicitly states: "TensorFlow computations are expressed as stateful dataflow graphs." Nodes represent operations, edges represent tensors (multidimensional arrays). The name derives from the operations neural networks perform on tensors.
- TensorFlow's computational graph is a direct descendant of Dennis's dataflow programming — Google's 2015 whitepaper describes "a single, optimized dataflow graph to represent the entire computation."
- **PyTorch (2016)** — Facebook's dynamic graph approach (define-by-run vs TensorFlow's original define-and-run). The graph is built on-the-fly during execution.

The connection: ML computational graphs are dataflow graphs where nodes are mathematical operations and edges carry tensor data. They are executable but NOT semantic — they encode computation without meaning.

### Apache Spark DAGs (2009-2014)

- **Matei Zaharia, 2009** — Created Apache Spark at UC Berkeley's AMPLab as a faster alternative to MapReduce.
- **2012** — RDD (Resilient Distributed Datasets) paper published. Spark represents computations as DAGs (Directed Acyclic Graphs) of transformations. The DAG scheduler breaks the computation graph into stages and tasks.
- Spark won the 2014 ACM Doctoral Dissertation Award for Zaharia's PhD research.

### Dask Task Graphs (2015)

- **Matthew Rocklin, 2015** — "Dask: Parallel Computation with Blocked algorithms and Task Scheduling" at SciPy 2015. Dask represents computations as task graphs — Python dictionaries where keys are variable names and values are computation specifications. The graph IS the program.

---

## 3. THE SPECIFIC COMBINATION: "EXECUTABLE" + "SEMANTIC"

### SWRL — Semantic Web Rule Language (2004)

- **2004, May** — SWRL submitted to W3C. Combines OWL DL/Lite with a subset of the Rule Markup Language (itself a subset of Datalog).
- SWRL adds Horn-clause rules to OWL ontologies, enabling inference. This is execution on a semantic graph — the rules derive new triples from existing ones.
- Critical limitation: key inference problems for SWRL are undecidable. SWRL never progressed beyond W3C Member Submission to full Recommendation.

### OWL-S / DAML-S — Semantic Web Services (2001-2004)

- **DAML-S (2001)** / **OWL-S (2004)** — An ontology for describing Web services semantically. Developed under DARPA Agent Markup Language program. Key contributors: Sheila McIlraith, Mark Burstein, Ora Lassila, Massimo Paolucci, Katia Sycara.
- OWL-S provided semantic descriptions of web services allowing agents to automatically discover, invoke, and **compose** services based on semantic properties. The process model even had a Petri Net-based operational semantics.
- This is arguably the earliest explicit attempt to combine semantic meaning with execution: semantically described services that could be automatically orchestrated into executable workflows. The graph of service descriptions IS both meaningful AND executable.

### SHACL — Shapes Constraint Language (2017)

- **2017, July 20** — Published as W3C Recommendation. Developed by the W3C RDF Data Shapes Working Group.
- SHACL defines constraints that can be validated against RDF graphs. This is "validation as execution" — SHACL processors traverse the graph, evaluate constraints, and produce validation reports.
- SHACL-SPARQL extends this with SPARQL-based rules, enabling inference alongside validation.
- SHACL is execution on a semantic graph, though limited to validation and simple inference.

### OWL Reasoning Engines — Inference as Execution

OWL reasoning is a form of graph execution:
- **Pellet** (Clark & Parsia, now Stardog) — OWL DL reasoner
- **HermiT** — first reasoner to use hypertableau calculus
- **FaCT++** — University of Manchester
- **Jena** — Apache's RDF/OWL framework with built-in reasoner

These engines traverse semantic graphs, apply logical rules, derive new facts, and check consistency. They execute on the graph to expand it. This is computation driven by meaning.

### Datalog on Graphs

- **1977** — Herve Gallaire and Jack Minker organized the foundational workshop on logic and databases in Toulouse, France, with assistance from Jean-Marie Nicolas. This established deductive databases as a field.
- Datalog is a subset of Prolog designed for database queries — recursive queries on graph-structured data. It combines the semantics of logic programming with graph traversal.
- Modern revival: Datalog is used in program analysis (Soufle), security policy (SecPAL), and knowledge graph reasoning. Datomic (Rich Hickey, 2012) uses Datalog for querying.

### GraphBLAS — Linear Algebra on Graphs (2011-2013)

- **2011** — "Graph Algorithms in the Language of Linear Algebra" book by Jeremy Kepner and John Gilbert — the foundational text.
- **2013** — GraphBLAS manifesto published. Tim Mattson, David Bader, Jonathan Berry, Aydin Buluc, Jack Dongarra, Christos Faloutsos, John Feo, John Gilbert, Joseph Gonzalez, Bruce Hendrickson, Jeremy Kepner, Charles Leiserson, Andrew Lumsdaine, David Padua, Stephen Poole, Steve Reinhardt, Mike Stonebraker, Steve Wallach, and Andrew Yoo — "Standards for Graph Algorithm Primitives" at IEEE HPEC 2013.
- GraphBLAS mathematically defines matrix-based graph operations. Graph algorithms are expressed as sparse linear algebra — adjacency matrices multiplied and transformed. This is executable computation on graph structure, though the semantics are mathematical rather than ontological.

### Apache TinkerPop / Gremlin — Traversal as Computation (2009-)

- **2009, October 30** — TinkerPop project born. Founded by **Marko A. Rodriguez**.
- **2015** — Rodriguez publishes "The Gremlin Graph Traversal Machine and Language" (arXiv 1508.03843).
- Gremlin is a graph traversal machine — it defines computation as paths through a graph. TinkerPop is to graph databases what JDBC/SQL is to relational databases. The Gremlin traversal machine is to graph computing what the JVM is to general purpose computing.
- Gremlin traversals ARE programs — they express arbitrary computation as graph traversal. This is executable graph computation, with the semantics embedded in the graph structure.

---

## 4. MODERN GRAPH-NATIVE COMPUTATION (LLM ERA)

### LangGraph — LangChain (January 2024)

- Built by **Harrison Chase** and the LangChain team. LangChain itself started in late 2022.
- LangGraph launched in **early January 2024** as a separate library on top of LangChain. Provides a graph-based state machine for building stateful, multi-actor agent workflows.
- Nodes are functions/agents, edges define control flow. State is carried through the graph. Supports cycles (unlike pure DAGs).
- **Assessment:** LangGraph is a workflow DAG/state machine, not an executable semantic graph. The graph structure defines execution order, but the nodes are opaque functions — the graph doesn't carry semantic meaning about what the computation means, only how it flows.

### CrewAI (October 2023)

- Founded by **Joao Moura** (with Rob Bailey). Built in October 2023, open-sourced November 2023.
- Role-based multi-agent framework: agents have defined responsibilities and collaborate on structured tasks.
- **Assessment:** CrewAI uses a role hierarchy, not a graph. Agents are nodes with roles, but the structure is more like a team org chart than an executable graph. It abstracts above the graph level.

### AutoGen — Microsoft Research (August 2023)

- Paper: "AutoGen: Enabling Next-Gen LLM Applications via Multi-Agent Conversation" by **Qingyun Wu, Gagan Bansal, Chi Wang** and others at Microsoft Research. ArXiv August 2023.
- Multi-agent conversation framework: agents converse to accomplish tasks. Customizable, conversable agents operating in various modes.
- **Assessment:** AutoGen is a conversation graph — agents are nodes, conversations are edges. But the graph is implicit (conversation topology), not a first-class data structure. Not truly an executable semantic graph.

### DSPy — Stanford (October 2023)

- **Omar Khattab** and collaborators at Stanford NLP. Paper: "DSPy: Compiling Declarative Language Model Calls into Self-Improving Pipelines" (arXiv October 2023, published ICLR 2024).
- DSPy abstracts LM pipelines as "imperative computation graphs where LMs are invoked through declarative modules." A compiler optimizes the pipeline.
- **Assessment:** DSPy is the closest to an executable semantic graph in the LLM space. The pipeline IS a graph, the modules carry semantic meaning (their signatures declare what they do), and the compiler transforms/optimizes the graph. However, DSPy's semantics are at the module level (input/output type signatures), not at the fine-grained node/edge level of a true semantic graph.

### MCP — Model Context Protocol (November 2024)

- Announced by **Anthropic** in November 2024 as an open standard. Originated from developer David Soria Parra's frustration with copying code between AI tools.
- MCP connects AI assistants to data systems (repositories, business tools, development environments). Inspired by the Language Server Protocol.
- By mid-2025: adopted by OpenAI, Google, Microsoft. 97M+ monthly SDK downloads. 1,000+ open-source connectors.
- **Assessment:** MCP defines a tool graph — servers expose tools, resources, and prompts that clients can discover and invoke. This is a graph of capabilities with semantic descriptions, but it is not self-contained execution — the LLM orchestrates calls externally.

### Are Any of These Truly "Executable Semantic Graphs"?

None of the modern LLM frameworks are truly executable semantic graphs. They are:
- **LangGraph/CrewAI/AutoGen:** Workflow orchestration graphs — control flow, not semantic meaning
- **DSPy:** Closest — declarative computation graph with module-level semantics
- **MCP:** Capability discovery graph — semantic but not self-executing

The gap: all of these use graphs to ORCHESTRATE computation, but the graph itself doesn't carry enough semantic meaning to be self-describing, and the graph doesn't execute itself — an external engine (the LLM, the Python runtime) drives execution.

---

## 5. THE TERM "EXECUTABLE SEMANTIC GRAPH" SPECIFICALLY

### Exact Phrase Search Results

The exact phrase "Executable Semantic Graph" does not appear as an established term in academic literature. No paper, patent, or standard uses this precise three-word combination as a named concept.

### "Executable Knowledge Graph" (ExeKG) — The Closest Match

The most relevant prior work uses "Executable Knowledge Graph":

1. **ExeKG — Bosch / ISWC 2022:** Zhuoxun Zheng, Baifan Zhou, Dongzhuoran Zhou et al. "Executable Knowledge Graphs for Machine Learning: A Bosch Case of Welding Monitoring" at ISWC 2022 (International Semantic Web Conference). Uses semantic technologies (OWL ontologies) to formally encode ML pipelines in knowledge graphs, which are then translated to executable Python scripts. Published by Springer LNCS vol. 13489, pp. 791-809.

2. **ExeKG System — CIKM 2022:** Same team. "ExeKG: Executable Knowledge Graph System for User-friendly Data Analytics" at CIKM 2022 (ACM International Conference on Information & Knowledge Management). A GUI-based system where users create/modify knowledge graphs that are translated into data analysis pipelines.

3. **xKG — Zhejiang University, 2025:** Yujie Luo, Zhuoyun Yu, Xuehai Wang et al. "What Makes AI Research Replicable? Executable Knowledge Graphs as Scientific Knowledge Representations" (arXiv:2510.17795, 2025). Models scientific literature as hierarchical graphs that ground academic concepts in executable code snippets. Unlike conventional KGs, xKG captures both conceptual relations AND runnable components. Shows 10.9% performance gains with o3-mini on PaperBench.

### Related Terms and Their Usage

- **"Computational Ontology"** — Used in philosophy of AI and knowledge representation, refers to ontologies designed to support computation/reasoning. Not a single well-defined system.
- **"Active Graph"** — Scattered usage in distributed systems literature, no standard definition.
- **"Live Graph" / "Dynamic Knowledge Graph"** — Used for graphs that update in real-time (streaming data), not for graphs that execute.
- **"Executable Ontology"** — OWL-S / DAML-S used this concept implicitly (ontologies that describe executable services).
- **"Self-modifying graph"** — No standard term. The concept exists in genetic programming, graph rewriting, and neural architecture search.

---

## 6. GRAPH DATABASES AS COMPUTATION PLATFORMS

### Neo4j (2007-)
- **Founded 2007, Malmo, Sweden** by Emil Eifrem, Johan Svensson, Peter Neubauer. First released as open-source Java graph database in 2007.
- Cypher query language. Property graph model. ACID-compliant.
- Neo4j is primarily a storage/query system — computation happens via queries, algorithms library (PageRank, community detection, etc.), and APOC procedures. Not a general computation platform.
- Valued at over $2B.

### Amazon Neptune (2017-)
- **Announced November 29, 2017** at AWS re:Invent. Fully managed graph database.
- Supports both property graphs (Gremlin) AND RDF (SPARQL). Unique in straddling both worlds.

### TigerGraph (2012-)
- **Founded 2012 by Yu Xu.** "Graph-native analytics" — GSQL query language.
- Claims fastest graph analytics at scale.
- Positioned for real-time analytics over massive graphs.

### Dgraph (2015-2016)
- **Founded July 2015 / incorporated January 2016 by Manish Rai Jain**, ex-Google (led Google's knowledge graph serving system).
- Native, distributed graph database. Open source. GraphQL-native.
- Jain ran Dgraph Labs from Jan 2016 to Jan 2022, growing to 50+ people and $1M ARR. Raised $23.5M total.

### Graph Storage vs. Graph Computation — The Critical Distinction

- **Storage:** Neo4j, Neptune, TigerGraph, Dgraph — store and query graphs
- **Computation frameworks:** Pregel, GraphX, Giraph — compute over graphs
- **Google Pregel (2010):** Malewicz, Austern, Bik, Dehnert, Horn, Leiser, Czajkowski. "Pregel: A System for Large-Scale Graph Processing" at ACM SIGMOD 2010. Vertex-centric programming with Bulk Synchronous Parallel (BSP) synchronization. Each vertex receives messages, updates its state, sends messages to neighbors. The graph structure IS the program topology.
- **Apache Giraph:** Open-source Pregel implementation. Facebook used it to process their social graph (trillions of edges).
- **Apache Spark GraphX (2014):** Brought graph processing into the Spark ecosystem. Unifies ETL, exploratory analysis, and iterative graph computation. Exposes the Pregel API.

None of these are "semantic" in the OWL/RDF sense — they compute over graph structure (topology, weights) but don't carry ontological meaning.

---

## 7. SELF-MODIFYING GRAPHS

### The Von Neumann Foundation

The stored-program concept (von Neumann architecture) is the ultimate ancestor: instructions and data reside in the same memory, enabling the CPU to treat instructions as data. Self-modifying code has existed since the earliest computers.

### Reflective Programming

- **Reflective programming** — the ability of a process to examine, introspect, and modify its own structure and behavior. Present in Lisp (1958, McCarthy), Smalltalk (1972, Kay/Ingalls), and the metacircular evaluator (Abelson & Sussman, SICP).
- A metacircular evaluator is a program that interprets itself — the structure of the evaluator IS the program, and it can modify itself.

### Genetic Programming — John Koza (1988-1992)

- **1988** — John Koza patents his invention of a genetic algorithm for program evolution. (David Goldberg, also a PhD student of John Holland, coined the term "genetic programming.")
- **1992** — Koza publishes "Genetic Programming: On the Programming of Computers by Means of Natural Selection." Programs are represented as trees (a restricted form of graph). The population of programs evolves through crossover (swapping subtrees) and mutation.
- Programs-as-trees that modify themselves through evolutionary operators. This is self-modifying graph computation — the graph structure IS the program, and evolution modifies the graph.

### Graph Rewriting — Algebraic Approach (1973-)

- **Ehrig, Pfender, Schneider (1973)** — Algebraic graph transformation. Rules specify how to match subgraphs and replace them with new subgraphs. The graph modifies itself according to rules.
- **Pfaltz and Rosenfeld (1969)** — Earlier web grammars, predecessor to graph grammars.
- The DPO (Double Pushout) approach uses category theory to give rigorous semantics to graph self-modification. This is the most mathematically mature framework for self-modifying graphs.

### Neural Architecture Search (2016-2017)

- **Barret Zoph and Quoc V. Le (Google Brain), November 2016** — "Neural Architecture Search with Reinforcement Learning" (arXiv:1611.01578). A recurrent network generates neural network architecture descriptions, trained with RL to maximize accuracy.
- Networks that design networks — the computation graph generates new computation graphs. This is meta-level self-modification.
- Enormously expensive initially (800 GPUs for 3-4 weeks) but spawned an entire subfield of AutoML.

### Is Self-Modification the Key Differentiator?

Self-modification separates:
- **Static executable graphs** (TensorFlow computational graph, Spark DAG, BPMN workflow) — the graph structure is fixed at compile time
- **Dynamic executable graphs** (PyTorch define-by-run, LangGraph with cycles) — the graph structure changes during execution
- **Self-modifying graphs** (genetic programming, graph rewriting, NAS) — the graph modifies its OWN structure as part of computation

For an "Executable Semantic Graph" that is truly novel, the combination that has NOT been done is: a graph that is (1) semantically meaningful (typed nodes/edges with ontological meaning), (2) directly executable (the graph IS the program), AND (3) self-modifying (execution can change the graph's own structure).

---

## SYNTHESIS: THE GENEALOGY MAP

### Two Lineages That Never Fully Merged

**Lineage 1: Semantic (meaning-carrying) graphs**
```
Quillian semantic networks (1968)
  -> Collins & Loftus spreading activation (1975)
    -> Berners-Lee Semantic Web Road Map (1998)
      -> RDF (1999) -> OWL (2004) -> SPARQL (2008)
        -> Google Knowledge Graph (2012)
        -> Wikidata (2012), DBpedia (2007)
        -> SHACL (2017)
```

**Lineage 2: Executable (computation-carrying) graphs**
```
Petri nets (1962)
  -> Karp-Miller computation graphs (1966)
    -> Dennis dataflow programming (1969-1975)
      -> Theano (2010) -> TensorFlow (2015)
      -> Spark DAGs (2012)
    -> Harel statecharts (1987)
      -> BPMN 2.0 (2011)
      -> XState
Hewitt Actor model (1973) -> Erlang -> Akka
Graph reduction (Turner 1976) -> functional programming
Pregel (2010) -> Giraph -> GraphX
```

**Partial Bridges (attempts to combine)**
```
SWRL (2004) — rules on semantic graphs (limited)
OWL-S / DAML-S (2001-2004) — executable service composition with semantic descriptions (closest early attempt)
OWL reasoning engines — inference as execution on semantic graphs
ExeKG (Bosch, 2022) — KGs translated to executable scripts
xKG (Zhejiang, 2025) — KGs with embedded code snippets
Gremlin/TinkerPop (2009) — traversal as computation on property graphs
GraphBLAS (2013) — linear algebra as graph computation
```

### The Gap

No system in the literature fully combines all three properties:
1. **Semantic:** Nodes and edges carry ontological meaning (typed, formally defined)
2. **Executable:** The graph itself is the program (not just data that a separate program reads)
3. **Self-modifying:** Execution can alter the graph's own structure

OWL-S came closest in 2001-2004 but was limited to service composition. ExeKG (2022) translates KGs to scripts but the KG itself doesn't execute. Modern LLM frameworks (LangGraph, etc.) are executable but not semantic. The exact phrase "Executable Semantic Graph" appears to be unclaimed territory.