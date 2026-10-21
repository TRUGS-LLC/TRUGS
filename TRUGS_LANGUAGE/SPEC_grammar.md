# TRUGS Language Grammar

> Formal composition rules: what can combine with what, and what it compiles to.

**Version:** 2.0.0

---

## 1. BNF Grammar

Every valid TRUGS Language program is one or more sentences. Every valid sentence matches this grammar. If it doesn't parse, it's not valid.

```
program         := preamble* (sentence | level_directive)+

preamble        := WHEREAS clause "."

sentence        := clause (CONJUNCTION clause)* "."
                 | definition "."
                 | leading_keyword_directive "."

clause          := subject verb_phrase (object_phrase)*

definition      := DEFINE value AS noun_phrase

leading_keyword_directive := ASSERTION_KEYWORD clause (CONJUNCTION clause)*
ASSERTION_KEYWORD         := ASSERT | ASSERT_NOT | INVARIANT

subject         := noun_phrase
                 | PRONOUN

noun_phrase     := [ARTICLE] [ADJECTIVE]* NOUN [identifier]

noun_list       := noun_phrase (AND noun_phrase)*

verb_phrase     := [modal] VERB adverb_phrase*

adverb_phrase   := ADVERB [value]

object_phrase   := prep_phrase (AND prep_phrase)*
                 | noun_phrase
                 | PRONOUN

prep_phrase     := PREPOSITION noun_list

modal           := SHALL | SHALL_NOT | MAY

identifier      := lowercase_name

value           := INTEGER_LITERAL | STRING_LITERAL | DURATION_LITERAL | DATE_LITERAL
                 | metric_level          (reserved: not yet accepted by the reference parser)

level_directive := metric_level

metric_level    := LEVEL_PREFIX "_" UPPERCASE_NAME

LEVEL_PREFIX    := YOTTA | ZETTA | EXA  | PETA  | TERA  | GIGA | MEGA
                 | KILO  | HECTO | DEKA | BASE  | DECI  | CENTI | MILLI
                 | MICRO | NANO  | PICO | FEMTO | ATTO  | ZEPTO | YOCTO

UPPERCASE_NAME  := [A-Z][A-Z0-9_]*

sugar           := "'" lowercase_name

lowercase_name  := [a-z_]+
```

### `level_directive` — hierarchy transition marker

A `level_directive` is a bare `metric_level` token appearing alone on its own line in TRL. It marks the transition into a new hierarchy level for an LLM consumer reading the source. Lexically, the parser recognises a directive when a line contains exactly one `metric_level` token followed by end-of-line and no other grammar production. Examples:

```
<trl>
PARTY system SHALL FILTER ALL ACTIVE RECORD.

DECI_STATEMENT

PARTY system SHALL VALIDATE EACH DATA field.
</trl>
```

`DECI_STATEMENT` here is a directive: it announces "what follows is at the DECI_STATEMENT level."

#### Compilation

A `level_directive` compiles to no node and no edge. The reference compiler (trugs-tools 2.4.0) records the level as the `metric_level` property of the next sentence's operation node; the directive itself is not stored. Decompilation may emit directives at every level transition for LLM-comprehension.

#### Distinction from `metric_level` as a value (reserved)

The grammar reserves a second position for a `metric_level` token, as the value of a hierarchy-aware property inside a sentence, distinguished from a directive by position (a directive stands alone; a value sits in the value position of an `object_phrase`):

```
PARTY system SHALL VALIDATE INPUT AT BASE_FUNCTION.
```

This form is reserved and not yet accepted: the reference parser (trugs-tools 2.4.0) accepts a `metric_level` token only as a directive line, and `AT` is not a word of the vocabulary. The example is kept as the reference case for the extension and is not checked TRL. See `SPEC_examples.md` example 30.

#### Validation

The validator does NOT enforce level directives. A TRL source with no directives is valid. A TRL source with directives that do not match the hierarchy on the underlying graph is also valid. Directives are an LLM-comprehension affordance, not a correctness gate.

### `leading_keyword_directive` — leading-keyword directives (`ASSERT` / `ASSERT_NOT` / `INVARIANT`)

A `leading_keyword_directive` is a sentence whose head is one of three **assertion keywords** — `ASSERT`, `ASSERT_NOT`, or `INVARIANT` — placed *before* the subject, followed by an ordinary clause. The keyword names the proposition's modality; the clause states the proposition:

```
<trl>
ASSERT       RESOURCE tracker CONTAINS EACH RECORD release_candidate.
ASSERT_NOT   FUNCTION instance_open EXISTS.
INVARIANT    RESOURCE tracker EXISTS.
</trl>
```

The three keywords differ only in modality:

| Keyword | Proposition modality |
|---|---|
| `ASSERT` | The clause must be **true** — a point-in-time condition checked at the assertion site. |
| `ASSERT_NOT` | The clause must be **false** — the negative dual of `ASSERT` (used for OUT-OF-SCOPE / prohibition statements). |
| `INVARIANT` | The clause must hold **across all time** — an always-true structural condition, not merely at one point. `INVARIANT` is the first-class temporal-universality keyword; it subsumes the older idiomatic phrasing `ASSERT … ACROSS ALL TIME`. |

Grammatically, a `leading_keyword_directive` differs from an ordinary `clause` only in the leading keyword: everything after the keyword is a normal clause (subject + verb_phrase + objects) and may chain with conjunctions. The keyword position — *before* the subject — is what distinguishes a directive from a clause whose verb happens to be `ASSERT` (verb #61, which sits in the verb position after a subject).

#### Compilation

A `leading_keyword_directive` compiles as its clause does, with the keyword recorded as `properties.modality` on the sentence's first operation node when the clause has a verb (the second and third examples above). A clause with no verb — a subject, a preposition and an object, as in the first example — compiles to its edge alone, and trugs-tools 2.4.0 keeps no record of the keyword: the decompiler writes the clause without it.

#### Parser support

> **Implemented.** The reference parser in `trugs-tools` 2.4.0 accepts `ASSERT`, `ASSERT_NOT`, and `INVARIANT` before a subject-first clause. It records the leading keyword as the modality of the first operation in that sentence. The v1 reference parser did not implement this production; the parser update and the corpus migration retiring the legacy `ACROSS ALL TIME` idiom were deferred at the specification release.

### Sugar preprocessing

Before parsing, the compiler strips all sugar tokens from the input. A sugar token is any token matching `'[a-z_]+`. Sugar tokens may appear anywhere in a sentence. They do not affect the parse, the compiled graph, or validation. The decompiler may optionally reinsert sugar tokens for human-readable output.

```
<trl>
PARTY system SHALL 'please FILTER ALL 'of 'the ACTIVE RECORD.
PARTY system SHALL FILTER ALL ACTIVE RECORD.
</trl>
```

The first sentence strips to the second; both parse by the normal BNF rules and compile to the same graph.

Custom sugar works the same way:

```
<trl>
PARTY admin 'trugs_llc SHALL ADMINISTER ALL RESOURCE.
PARTY admin SHALL ADMINISTER ALL RESOURCE.
</trl>
```

### Minimum valid sentence

```
<trl>
PARTY system VALIDATE.
</trl>
```
Subject (PARTY system) + verb (VALIDATE). No modal, no object, no adverbs.

### Maximum structure

```
<trl>
WHEREAS PARTY admin GOVERNS ALL RESOURCE.
EACH ACTIVE PARTY SHALL FILTER PROMPTLY ALL PENDING RECORD
  SUBJECT_TO REQUIRED VALID INTERFACE schema
  THEN DELIVER RESULT TO THE ENDPOINT output AND THE ENDPOINT backup
  UNLESS PARTY admin OVERRIDE
    PROVIDED_THAT PARTY admin AUTHENTICATE TO SERVICE auth.
</trl>
```
Preamble + subject with article/adjective + modal + verb with adverb + multiple object phrases + conjunction chain 3 deep.

---

## 2. Composition Rules

**What the reference tools enforce.** trugs-tools 2.4.0 rejects, from TRL, a modal on a non-Actor subject (§2.3, CORE validation rule 14) and a pronoun with no prior clause to reference. It compiles and validates sentences that break the other tables of this section (§2.1, §2.2, §2.4, §2.6 and §2.7): its compiled graph carries verbs as operation nodes, adjectives and articles as the `np_shape` of an edge, and adverbs as a list, which validation rules 10–13 do not read. Those tables state the language's composition rules; until the tools enforce them, a sentence that breaks one compiles. This is a known gap in the tools, not a licence to break the rules.

### 2.1 Subject-Verb Compatibility

Which noun subcategories can be the subject of which verb subcategories:

| Subject (noun) | Transform | Move | Obligate | Permit | Prohibit | Control | Bind | Resolve |
|---|---|---|---|---|---|---|---|---|
| **Actor** | yes | yes | yes | yes | yes | yes | yes | yes |
| **Artifact** | — | — | — | — | — | yes* | — | — |
| **Container** | yes | — | — | — | — | yes | yes | — |
| **Boundary** | — | — | — | — | — | — | yes | — |
| **Outcome** | — | — | — | — | — | — | — | — |

*Artifacts can be subjects of comparison/existence Control verbs only: EXISTS, EQUALS, EXCEEDS, PRECEDES, EXPIRE.

**Rule:** Only Actors can be subjects of most verbs. Containers can Transform (a PIPELINE filters) and Control (a STAGE branches). Artifacts can only be subjects of boolean-evaluation verbs.

### 2.2 Verb-Object Compatibility

| Object (noun) | Transform | Move | Obligate | Permit | Prohibit | Control | Bind | Resolve |
|---|---|---|---|---|---|---|---|---|
| **Actor** | — | — | — | yes | yes | — | — | — |
| **Artifact** | yes | yes | yes | — | — | yes | yes | — |
| **Container** | — | yes | — | — | — | — | yes | — |
| **Boundary** | — | — | — | — | — | — | yes | — |
| **Outcome** | — | — | — | — | — | — | — | yes |

**Rule:** Transforms act on Artifacts. Move verbs move Artifacts and Containers. Permit/Prohibit target Actors. Resolve verbs target Outcomes.

### 2.3 Modal Rules

Modals (SHALL, SHALL_NOT, MAY) require Actor subjects. Always.

```
PARTY client SHALL FILTER ...        valid   Actor + modal
PIPELINE main SHALL FILTER ...       INVALID Container cannot bear obligation
DATA records SHALL SORT ...          INVALID Artifact cannot bear obligation
```

### 2.4 Adjective-Noun Compatibility

| Adjective | Actor | Artifact | Container | Boundary | Outcome |
|---|---|---|---|---|---|
| **Type** | — | yes | — | — | yes |
| **Access** | — | yes | yes | yes | — |
| **State** | yes | yes | yes | yes | yes |
| **Quantity** | yes | yes | yes | — | yes |
| **Priority** | yes | yes | yes | yes | yes |

**Rule:** Type adjectives (STRING, INTEGER) only modify Artifacts and Outcomes. State and Priority are universal.

### 2.5 Adjective Ordering

When multiple adjectives stack, the canonical order is:

```
[QUANTITY] [PRIORITY] [STATE] [ACCESS] [TYPE] NOUN
```

```
REQUIRED CRITICAL VALID PUBLIC STRING data     canonical
VALID REQUIRED STRING data                     accepted; the decompiler writes REQUIRED VALID STRING data
```

The parser accepts adjectives in any order and compiles them to the same graph; the decompiler writes the canonical order. One exception: two adjectives of one category keep the order written, so `ACTIVE VALID RECORD x` and `VALID ACTIVE RECORD x` compile to different graphs, and the decompiler keeps each as written.

### 2.6 Adverb-Verb Compatibility

| Adverb | Transform | Move | Obligate | Permit | Prohibit | Control | Bind | Resolve |
|---|---|---|---|---|---|---|---|---|
| **Timing** | yes | yes | yes | yes | yes | yes | — | yes |
| **Repetition** | yes | yes | yes | yes | yes | yes | — | yes |
| **Degree** | — | — | yes | yes | yes | — | yes | — |
| **Condition** | yes | yes | yes | yes | yes | yes | yes | yes |

**Rule:** Timing and Repetition modify any verb except Bind. Degree modifies authority verbs. Condition modifies everything.

### 2.7 Preposition Compatibility

| Preposition | From (subject) | To (object) |
|---|---|---|
| FEEDS | Actor, Container | Actor, Container, Artifact |
| ROUTES | Actor, Container | Actor, Container |
| BINDS | Artifact (schema) | Actor, Container |
| CONTAINS | Container | Any |
| DEPENDS_ON | Any | Any |
| REFERENCES | Any | Any |
| SUPERSEDES | Any | Same type as source |
| GOVERNS | Actor | Actor, Container, Boundary |
| SUBJECT_TO | Any | Artifact (constraint), Boundary |
| IMPLEMENTS | Actor, Container | Boundary (interface) |
| EXTENDS | Any | Same type as source |
| RETURNS_TO | Actor | Actor |
| PURSUANT_TO | Actor | Artifact (rule), Boundary |
| ON_BEHALF_OF | Actor (agent) | Actor (principal) |
| TO | Any | Any |
| FROM | Any | Any |
| AS | value (in DEFINE) | noun_phrase |
| BY | Any | Artifact (key) |

**Rule:** SUPERSEDES and EXTENDS require same noun subcategory. GOVERNS flows from Actors downward. BINDS flows from schemas to actors.

### 2.8 Conjunction Scoping

| Conjunction | Left clause | Right clause | Execution semantics |
|---|---|---|---|
| THEN | Must complete | Starts after left | Sequential |
| AND | Independent | Independent | Parallel |
| OR | May fail | Fallback | Alternative |
| ELSE | Conditional (IF/WHEN) | Opposite condition | Branch |
| IF | — | Conditional clause | Gate |
| WHEN | — | Event-triggered clause | Reactive |
| WHILE | — | Loop body | Repeat |
| FINALLY | Any | Cleanup clause | Guaranteed |
| UNLESS | Normal clause | Exception condition | Override |
| EXCEPT | Broad clause | Narrow carve-out | Scope reduction |
| NOTWITHSTANDING | Overriding clause | Any prior clause | Override |
| PROVIDED_THAT | Conditional clause | Prerequisite | Gate |
| WHEREAS | — | Context/fact | Preamble (no execution) |

**Rule:** THEN, AND, OR, ELSE chain equal-weight clauses. UNLESS, EXCEPT, NOTWITHSTANDING, PROVIDED_THAT create subordinate clauses. WHEREAS is preamble-only. WHILE is the only loop.

### 2.9 Verb-Preposition Separation

Every word belongs to exactly one part of speech. Where a concept has both an action form (verb) and a relationship form (preposition), they are distinct words:

| Action (verb) | Relationship (preposition) |
|---|---|
| ADMINISTER | GOVERNS |
| NEST | CONTAINS |
| CITE | REFERENCES |
| REQUIRE | DEPENDS_ON |
| REPLACE | SUPERSEDES |
| AUGMENT | EXTENDS |

**Rule:** No word is both a verb and a preposition. Verbs appear in verb_phrase position. Prepositions appear in prep_phrase position. There is no ambiguity.

---

## 3. Sentence-to-Graph Compilation

Each sentence element compiles to the graph element or property below (as trugs-tools 2.4.0 writes it):

| Sentence Element | Compiles To | Graph Element |
|---|---|---|
| NOUN + identifier | Node | `{ id: identifier, type: NOUN }`; a noun without an identifier gets a generated id such as `record-1` |
| ADJECTIVE on a noun | Edge property | `properties.np_shape.{ subcategory: ADJECTIVE }` on the edge that reaches the node, for example `type: "STRING"`; a list when a category has more than one adjective, such as `state: ["ACTIVE", "VALID"]` |
| ARTICLE on a noun | Edge property | `properties.np_shape.article: ARTICLE` on that edge |
| VERB | Operation node | `{ type: "TRANSFORM", properties: { operation: VERB, verb_subcategory: … } }` |
| Modal on a verb | Edge from the subject to the operation | `relation: modal`; a clause with no modal uses `relation: "EXECUTES"` |
| ADVERB on a verb | Operation property | an entry `{ adverb: ADVERB }` in `properties.adverbs` |
| ADVERB value | Operation property | `{ adverb: ADVERB, value: literal }` in that list |
| Bare value after the object | Operation property | `properties.value_arg: literal` |
| Object noun phrase | Edge from the operation to the object | `relation: "ACTS_ON"` |
| PREPOSITION | Edge | `{ from_id, to_id, relation: PREPOSITION }`: from the operation after a verb, from the subject in a clause with no verb |
| CONJUNCTION | Edge between clauses | `relation: CONJUNCTION` (THEN, AND, UNLESS, …) from the first clause's operation node to the next clause's, or from a clause's subject when it has no verb; a conjunction that opens a sentence (IF, WHEN) is `properties.leading_conjunction` on the first operation |
| PRONOUN | Edge to the antecedent | `properties.pronoun: PRONOUN` on an edge from the operation to the antecedent: `relation: "ACTS_ON"` for a bare object, the preposition's name after a preposition; the antecedent is the prior clause's operation for RESULT and the subject for SELF |
| WHEREAS clause | Nodes and edges | as a clause, with `preamble: true` on its operation node, or on its edge when it has no verb |
| DEFINE definition | Node | `{ id: term, type: noun, properties: { defined: true, name: term } }` |
| ASSERT / ASSERT_NOT / INVARIANT | Operation property | `properties.modality: KEYWORD` on the clause's first operation node; a clause with no verb keeps no record of the keyword |
| `level_directive` | Operation property | no node and no edge; `properties.metric_level: "<PREFIX>_<NAME>"` on the next sentence's operation node |
| `metric_level` value | Reserved | not yet accepted by the reference parser (§1) |

### Round-Trip Guarantee

- **Sentence to Graph:** Parse by grammar, emit nodes and edges. Every executable word maps to exactly one graph element or property. Sugar tokens compile to nothing; `level_directive` markers set a property and emit no element.
- **Graph to Sentence:** Walk in topological order, emit words by reversing the table. Every element maps to exactly one word. The canonical decompiler may insert `level_directive` lines at every metric-level transition encountered during the walk.

If a sentence cannot round-trip (after stripping sugar and directives), it is not valid. Directives and sugar are dropped on TRL→TRUG and may be re-emitted on TRUG→TRL by the canonical decompiler — graphs are equal across the round-trip; sources may not be byte-identical without canonicalisation.

---

## 4. Validation Rules

A compiled graph is valid when it passes the 16 CORE rules of `TRUGS_PROTOCOL/CORE.md` (ruleset `core_v2.0.0`: 9 structural, 7 compositional), which `trug trl compile` applies to every graph it emits. Before that, the parser rejects a sentence that uses a word outside the vocabulary, one its grammar does not parse, and a pronoun with no prior clause to reference. The parser's grammar is wider than the BNF of §1 in one respect: it accepts a clause of a subject, a preposition and an object with no verb (`RESOURCE tracker CONTAINS RECORD x.`), which compiles to that edge alone.

The composition tables of §2.1, §2.2, §2.4, §2.6 and §2.7 and the rule against double negation (a negative article with SHALL_NOT) are CORE rules 10 to 13 and 15, which `trug validate` applies to the operation words on a graph's edges and to the modifiers in its node properties. The compiler of trugs-tools 2.4.0 writes verbs, adjectives, articles and adverbs where those rules do not read, so a sentence that breaks them compiles and validates (the note at §2). Pronoun scope within one sentence is not a CORE rule, and the compiler resolves a pronoun across sentences.

---

## 5. The Opening TRUG

Every LLM conversation begins by loading a language TRUG. This TRUG is the complete, self-contained definition of the language for that session.

### What the opening TRUG contains

| Node Type | Purpose |
|---|---|
| **WORD** | Every valid word, its part of speech, subcategory, and exact definition |
| **GRAMMAR_RULE** | Composition rules — which parts of speech combine with which |
| **CONSTRAINT** | Structural limits on the language itself |
| **DOMAIN** | Domain-specific vocabulary extensions loaded for this session |

### What this means

- **Vocabulary size** — count the WORD nodes. That's the vocabulary.
- **Domain extensions** — add DOMAIN nodes with WORD children.
- **Ambiguity** — impossible. Each WORD has exactly one definition.
- **Configuration** — every question about "how should the language work" is answered by: read the graph you were given.

### The language IS the program loader

`#!/usr/bin/python` tells the OS which interpreter to use. The opening TRUG tells the LLM which language to speak. Different TRUGs = different languages. Same grammar, same parts of speech, same compilation rules. Only the words differ.

This is not configuration. This is the language runtime.
