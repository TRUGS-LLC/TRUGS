# TRUGS Language Grammar

> Formal composition rules: what can combine with what, and what it compiles to.

**Issue:** #1211 | **Version:** 1.0.1

---

## 1. BNF Grammar

Every valid TRUGS Language program is one or more sentences. Every valid sentence matches this grammar. If it doesn't parse, it's not valid.

```
program         := preamble* sentence+

preamble        := WHEREAS clause "."

sentence        := clause (CONJUNCTION clause)* "."
                 | definition "."

clause          := subject verb_phrase (object_phrase)*

definition      := DEFINE value AS noun_phrase

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

sugar           := "'" lowercase_name

lowercase_name  := [a-z_]+
```

### Sugar preprocessing

Before parsing, the compiler strips all sugar tokens from the input. A sugar token is any token matching `'[a-z_]+`. Sugar tokens may appear anywhere in a sentence. They do not affect the parse, the compiled graph, or validation. The decompiler may optionally reinsert sugar tokens for human-readable output.

```
Input:   "PARTY system SHALL 'please FILTER ALL 'of 'the ACTIVE RECORD."
Strip:   "PARTY system SHALL FILTER ALL ACTIVE RECORD."
Parse:   (normal BNF rules apply)
Compile: (identical graph regardless of sugar)
```

Custom sugar works the same way:

```
Input:   "PARTY admin 'trugs_llc SHALL ADMINISTER ALL RESOURCE."
Strip:   "PARTY admin SHALL ADMINISTER ALL RESOURCE."
```

### Minimum valid sentence

```
PARTY system VALIDATE.
```
Subject (PARTY system) + verb (VALIDATE). No modal, no object, no adverbs.

### Maximum structure

```
WHEREAS PARTY admin GOVERNS ALL RESOURCE.
EACH ACTIVE PARTY SHALL PROMPTLY FILTER ALL PENDING RECORD
  SUBJECT_TO REQUIRED VALID INTERFACE schema
  THEN DELIVER RESULT TO THE ENDPOINT output AND THE ENDPOINT backup
  UNLESS PARTY admin OVERRIDE
    PROVIDED_THAT PARTY admin AUTHENTICATE TO SERVICE auth.
```
Preamble + subject with article/adjective + modal + verb with adverb + multiple object phrases + conjunction chain 3 deep.

---

## 2. Composition Rules

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

When multiple adjectives stack, fixed order:

```
[QUANTITY] [PRIORITY] [STATE] [ACCESS] [TYPE] NOUN
```

```
REQUIRED CRITICAL VALID PUBLIC STRING data     valid
VALID REQUIRED STRING data                     INVALID (STATE before QUANTITY)
```

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

Every sentence element compiles to exactly one TRUG graph element:

| Sentence Element | Compiles To | Graph Element |
|---|---|---|
| NOUN + identifier | Node | `{ id: identifier, type: NOUN }` |
| ADJECTIVE on noun | Node property | `properties.{ adjective_subcategory: ADJECTIVE }` |
| ARTICLE on noun | Node query scope | `scope: { quantifier: ARTICLE }` |
| VERB | Operation node | `{ type: "TRANSFORM", properties: { operation: VERB } }` |
| Modal on verb | Constraint edge | Edge from PARTY to operation: `relation: modal` |
| ADVERB on verb | Operation property | `properties.{ adverb_subcategory: ADVERB }` |
| ADVERB value | Property value | `properties.{ adverb: value }` |
| PREPOSITION | Edge | `{ from_id: left, to_id: right, relation: PREPOSITION }` |
| CONJUNCTION | Graph structure | THEN: sequential edge. AND: parallel edges. UNLESS: conditional edge |
| PRONOUN | Back-reference edge | `{ from_id: current, to_id: antecedent, relation: "REFERENCES" }` |
| Value literal | Property value | `properties.value: literal` |
| WHEREAS clause | Nodes + edges | Same as regular clause, but no obligation semantics |
| DEFINE definition | DEFINED_TERM node | `{ id: term, type: noun, properties: { defined: true } }` |

### Round-Trip Guarantee

- **Sentence to Graph:** Parse by grammar, emit nodes and edges. Every word maps to exactly one graph element.
- **Graph to Sentence:** Walk in topological order, emit words by reversing the table. Every element maps to exactly one word.

If a sentence cannot round-trip, it is not valid.

---

## 4. Validation Rules

A compiled graph is valid if and only if all 12 rules pass:

1. **Every node has a type** from the noun vocabulary
2. **Every edge has a relation** from the preposition vocabulary
3. **Subject-verb compatibility** holds for every operation
4. **Verb-object compatibility** holds for every operation-to-target edge
5. **Adjective-noun compatibility** holds for every property on every node
6. **Adverb-verb compatibility** holds for every property on every operation
7. **Modal-subject rule** holds: modals only on Actor subjects
8. **Pronoun resolution** succeeds: every pronoun has exactly one antecedent in scope
9. **SUPERSEDES/EXTENDS type match** holds: source and target are the same noun subcategory
10. **No orphan nodes** — every node is reachable from an entry point or subject
11. **No double negation** — a Negative article (NO, NONE) and a Prohibit modal (SHALL_NOT) cannot modify the same clause
12. **Pronoun scope** — pronouns resolve within the current sentence only; cross-sentence references use THE + NOUN or SAID + NOUN

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
