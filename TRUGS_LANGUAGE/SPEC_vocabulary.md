# TRUGS Language Vocabulary

> 233 words across 9 parts of speech. Computation primary, law fills gaps. SI prefixes mark hierarchy transitions.

**Issue:** #1211, [TRUGS-DEVELOPMENT#1719](https://github.com/Xepayac/TRUGS-DEVELOPMENT/issues/1719) | **Version:** 2.0.0

---

## 1. Nouns — Things That Exist (26)

A noun is anything that can be a node in the TRUG graph. It occupies subject or object position.

### Actors (7) — Who performs actions

| # | Word | Source | Definition | CORE |
|---|---|---|---|---|
| 1 | PROCESS | computation | An executing unit of work with its own state | |
| 2 | SERVICE | computation | A long-lived process that accepts requests | |
| 3 | FUNCTION | computation | A callable unit that accepts input and returns output | |
| 4 | TRANSFORM | computation | A node that performs exactly one operation | yes |
| 5 | PARTY | law | A bound entity capable of obligations and permissions | yes |
| 6 | AGENT | law | An entity authorized to act on behalf of another | |
| 7 | PRINCIPAL | law | The entity on whose behalf an agent acts | |

### Artifacts (7) — What is acted upon

| # | Word | Source | Definition | CORE |
|---|---|---|---|---|
| 8 | DATA | computation | A typed value: input, output, or intermediate state | yes |
| 9 | FILE | computation | A named, persistent byte sequence | |
| 10 | RECORD | computation | A single structured data item with named fields | |
| 11 | MESSAGE | computation | A discrete unit of communication between actors | |
| 12 | STREAM | computation | An ordered, potentially unbounded sequence of data items | |
| 13 | RESOURCE | computation | A managed asset: file, service, endpoint, or data store | |
| 14 | INSTRUMENT | law | A formal document that creates or records rights | |

### Containers (4) — What holds other things

| # | Word | Source | Definition | CORE |
|---|---|---|---|---|
| 15 | PIPELINE | computation | A container of ordered operations data flows through | yes |
| 16 | STAGE | computation | A logical grouping of transforms within a pipeline | yes |
| 17 | MODULE | computation | A self-contained unit of related functionality | |
| 18 | NAMESPACE | computation | A named scope that prevents identifier collision | |

### Boundaries (5) — Where/when things apply

| # | Word | Source | Definition | CORE |
|---|---|---|---|---|
| 19 | ENTRY | computation | The point where data enters a scope | yes |
| 20 | EXIT | computation | The point where data leaves a scope | yes |
| 21 | INTERFACE | computation | A contract defining what operations a thing exposes | |
| 22 | ENDPOINT | computation | A named, addressable point of interaction | |
| 23 | JURISDICTION | law | The scope within which authority is valid | |

### Outcomes (3) — What comes out

| # | Word | Source | Definition | CORE |
|---|---|---|---|---|
| 24 | ERROR | computation | A named failure condition with a cause | |
| 25 | EXCEPTION | computation | An error that interrupts normal flow | |
| 26 | REMEDY | law | The consequence when an obligation is breached | yes |

---

## 2. Verbs — Actions That Execute (80)

A verb transforms state or establishes obligation. Every sentence has exactly one primary verb. Verbs chain with conjunctions.

### Transform (17) — Change data shape

| # | Word | Source | Definition | CORE |
|---|---|---|---|---|
| 27 | FILTER | computation | Select items satisfying a predicate | yes |
| 28 | EXCLUDE | computation | Remove items satisfying a predicate | yes |
| 29 | MAP | computation | Transform each item independently | yes |
| 30 | SORT | computation | Order items by comparison function | yes |
| 31 | MERGE | computation | Combine multiple collections into one | yes |
| 32 | SPLIT | computation | Divide one collection into multiple | yes |
| 33 | FLATTEN | computation | Collapse one level of nesting | yes |
| 34 | AGGREGATE | computation | Reduce collection to single value | yes |
| 35 | GROUP | computation | Partition collection by key | yes |
| 36 | RENAME | computation | Change field names without changing values | yes |
| 37 | BATCH | computation | Group items into fixed-size chunks | yes |
| 38 | DISTINCT | computation | Remove duplicates | yes |
| 39 | TAKE | computation | Return first N items | yes |
| 40 | SKIP | computation | Bypass first N items | yes |
| 41 | APPLY | computation | Apply a rule, transform, or patch to a target | |
| 42 | DERIVE | computation | Produce a derived artifact from a source | |
| 43 | UPDATE | computation | Mutate existing state in place; distinct from WRITE | |

### Move (16) — Move data between actors

| # | Word | Source | Definition | CORE |
|---|---|---|---|---|
| 44 | READ | computation | Input data from external source | yes |
| 45 | WRITE | computation | Output data to external destination | yes |
| 46 | SEND | computation | Transmit data to another actor | |
| 47 | RECEIVE | computation | Accept data from another actor | |
| 48 | RETURN | computation | Emit final output and terminate | |
| 49 | REQUEST | computation | Send message expecting a response | yes |
| 50 | RESPOND | computation | Reply to a prior request | yes |
| 51 | AUTHENTICATE | computation | Prove identity to another actor | |
| 52 | DELIVER | law | Transfer possession of an artifact to another party | |
| 53 | ASSIGN | law | Transfer rights or obligations to another party | |
| 54 | LOAD | computation | Read data into working context; distinct from READ | |
| 55 | POST | computation | Publish to a channel or issue thread; distinct from SEND | |
| 56 | EMIT | computation | Produce an artifact or event to an outward channel | |
| 57 | PRODUCE | computation | Generate output from an operation | |
| 58 | APPEND | computation | Add an item to the end of an ordered log or list | |
| 59 | DELEGATE | computation | Hand off a stage to another agent to perform | |

### Obligate (6) — Mandate behavior

| # | Word | Source | Definition | CORE |
|---|---|---|---|---|
| 60 | VALIDATE | computation | Assert data satisfies condition; halt if not | yes |
| 61 | ASSERT | computation | Declare a condition that must be true | |
| 62 | REQUIRE | computation | Declare a hard prerequisite | |
| 63 | SHALL | law | Mandatory: party MUST perform action | yes |
| 64 | ASSERT_NOT | computation | Declare a condition that must never be true; negative dual of ASSERT | |
| 65 | INVARIANT | computation | Declare a condition that must hold across all time, not just at one point | |

### Permit (7) — Allow behavior

| # | Word | Source | Definition | CORE |
|---|---|---|---|---|
| 66 | ALLOW | computation | Permit an action without mandating it | |
| 67 | APPROVE | computation | Accept as satisfying criteria; opposite of REJECT | |
| 68 | GRANT | law | Confer a right or permission to another party | |
| 69 | OVERRIDE | law | Supersede a constraint or prohibition for this action | |
| 70 | MAY | law | Permitted: party is allowed but not required | yes |
| 71 | ACCEPT | computation | Accept a result or proposal at a decision gate | |
| 72 | SUGGEST | computation | Recommend a non-binding course of action | |

### Prohibit (4) — Forbid behavior

| # | Word | Source | Definition | CORE |
|---|---|---|---|---|
| 73 | DENY | computation | Refuse a requested action | |
| 74 | REJECT | computation | Refuse input that does not meet criteria | |
| 75 | SHALL_NOT | law | Prohibited: party MUST NOT perform action | yes |
| 76 | REVOKE | law | Withdraw a previously granted right or permission | |

### Control (15) — Direct execution flow

| # | Word | Source | Definition | CORE |
|---|---|---|---|---|
| 77 | BRANCH | computation | Route to one of two paths on boolean condition | yes |
| 78 | MATCH | computation | Route to one of N paths on pattern | yes |
| 79 | RETRY | computation | Re-attempt failed operation up to bounded count | yes |
| 80 | TIMEOUT | computation | Bound wall-clock time for an operation | yes |
| 81 | THROW | computation | Generate an error condition; directs flow to error handler | |
| 82 | EXISTS | computation | Evaluates true if the noun is present and non-null | |
| 83 | EXPIRE | computation | Transition to EXPIRED state; deadline passed | |
| 84 | EQUALS | computation | Evaluates true if left and right values are identical | |
| 85 | EXCEEDS | computation | Evaluates true if left value is greater than right | |
| 86 | PRECEDES | computation | Evaluates true if left value is less than right | |
| 87 | EXECUTE | computation | Run a unit of work | |
| 88 | INVOKE | computation | Call an interface, function, or process | |
| 89 | HALT | computation | Stop a process immediately | |
| 90 | COMPLETE | computation | Bring an operation to its finished state | |
| 91 | PASS | computation | Satisfy a check or gate | |

### Bind (10) — Establish meaning or structural relationships

| # | Word | Source | Definition | CORE |
|---|---|---|---|---|
| 92 | DEFINE | computation | Establish the meaning of a term | |
| 93 | DECLARE | computation | State a fact or create a named thing | |
| 94 | IMPLEMENT | computation | Fulfill the contract of an interface | |
| 95 | NEST | computation | Place one thing structurally inside another | |
| 96 | AUGMENT | computation | Add capability to an existing thing | |
| 97 | REPLACE | computation | Entirely substitute one thing for another | |
| 98 | CITE | law | Formally refer to another entity | |
| 99 | ADMINISTER | law | Establish and exercise authority over | |
| 100 | STIPULATE | law | Establish a binding agreed-upon condition | |
| 101 | HAVE | computation | Possess a property or attribute (SHALL HAVE) | |

### Resolve (5) — Respond to failure

| # | Word | Source | Definition | CORE |
|---|---|---|---|---|
| 102 | CATCH | computation | Intercept an error and enter recovery | |
| 103 | HANDLE | computation | Process an error condition | |
| 104 | RECOVER | computation | Restore normal operation after failure | |
| 105 | CURE | law | Correct a breach within allowed time | |
| 106 | INDEMNIFY | law | Compensate for loss caused by breach | |

---

## 3. Adjectives — Constraints on Nouns (39)

An adjective constrains what a noun is or can do. Precedes the noun. Stacking order: Quantity > Priority > State > Access > Type > Noun.

### Type (5) — What kind of thing

| # | Word | Source | Definition |
|---|---|---|---|
| 107 | STRING | computation | Text data type |
| 108 | INTEGER | computation | Whole number data type |
| 109 | BOOLEAN | computation | True/false data type |
| 110 | ARRAY | computation | Ordered collection data type |
| 111 | OBJECT | computation | Key-value structure data type |

### Access (5) — Who can see/touch it

| # | Word | Source | Definition |
|---|---|---|---|
| 112 | PUBLIC | computation | Accessible to any actor |
| 113 | PRIVATE | computation | Accessible only to the owning actor |
| 114 | PROTECTED | computation | Accessible to the owning actor and its children |
| 115 | READONLY | computation | Can be read but not written |
| 116 | CONFIDENTIAL | law | Restricted to authorized parties only |

### State (14) — Current condition

| # | Word | Source | Definition |
|---|---|---|---|
| 117 | VALID | computation | Satisfies all declared constraints |
| 118 | INVALID | computation | Fails one or more declared constraints |
| 119 | NULL | computation | Absent; no value |
| 120 | EMPTY | computation | Present but containing nothing |
| 121 | PENDING | computation | Created but not yet processed |
| 122 | ACTIVE | computation | Currently in use or executing |
| 123 | FAILED | computation | Terminated with error |
| 124 | MUTABLE | computation | Can be changed after creation |
| 125 | IMMUTABLE | computation | Cannot be changed after creation |
| 126 | BINDING | law | Creates enforceable obligation |
| 127 | VOID | law | Without legal effect; as if it never existed |
| 128 | ENFORCEABLE | law | Can be compelled by remedy |
| 129 | EXPIRED | law | Past its deadline; no longer in effect |
| 130 | PRECEDENT | law | Informing but not binding; advisory based on prior decision |

### Quantity (9) — How many / whether required

| # | Word | Source | Definition |
|---|---|---|---|
| 131 | REQUIRED | computation | Must be present; absence is an error |
| 132 | OPTIONAL | computation | May be absent; absence is acceptable |
| 133 | UNIQUE | computation | Exactly one instance may exist |
| 134 | MULTIPLE | computation | More than one instance may exist |
| 135 | SOLE | law | One and only one; no others permitted |
| 136 | JOINT | law | Shared equally among multiple parties |
| 137 | ONLY | computation | Exclusively; no other instance or case is permitted |
| 138 | AT_LEAST | computation | Lower-bound cardinality; the count is N or more |
| 139 | EXACTLY | computation | Exact cardinality; the count is precisely N |

### Priority (6) — Relative importance

| # | Word | Source | Definition |
|---|---|---|---|
| 140 | DEFAULT | computation | The value used when none is specified |
| 141 | CRITICAL | computation | Failure is unrecoverable |
| 142 | HIGH | computation | Elevated importance |
| 143 | LOW | computation | Reduced importance |
| 144 | MATERIAL | law | Significant enough to affect decisions |
| 145 | SUBORDINATE | law | Lower in authority hierarchy |

---

## 4. Adverbs — Constraints on Verbs (19)

An adverb constrains how a verb executes. Follows the verb. Each adverb optionally carries a value.

### Timing (9) — When/how fast

| # | Word | Source | Definition |
|---|---|---|---|
| 146 | ASYNC | computation | Execute without blocking the caller |
| 147 | SYNC | computation | Execute and block until complete |
| 148 | SEQUENTIAL | computation | Execute steps one after another in order |
| 149 | PARALLEL | computation | Execute steps simultaneously |
| 150 | IMMEDIATE | computation | Execute with no delay |
| 151 | LAZY | computation | Defer execution until the result is needed |
| 152 | PROMPTLY | law | Within a reasonable time, without unnecessary delay |
| 153 | FORTHWITH | law | Immediately and without any delay |
| 154 | WITHIN | law | Before the specified duration elapses (requires duration) |

### Repetition (4) — How often

| # | Word | Source | Definition |
|---|---|---|---|
| 155 | ONCE | computation | Execute exactly one time |
| 156 | ALWAYS | computation | Execute every time the condition is met |
| 157 | NEVER | computation | Do not execute under any condition |
| 158 | BOUNDED | computation | Execute up to N times (requires integer) |

### Degree (4) — How precisely

| # | Word | Source | Definition |
|---|---|---|---|
| 159 | STRICTLY | computation | With zero tolerance for deviation |
| 160 | PARTIALLY | computation | Affecting some but not all items |
| 161 | SUBSTANTIALLY | law | In all material respects; minor deviations tolerated |
| 162 | REASONABLY | law | As a competent party would under the circumstances |

### Condition (2) — Whether qualified

| # | Word | Source | Definition |
|---|---|---|---|
| 163 | UNCONDITIONALLY | law | Without any prerequisite or qualification |
| 164 | CONDITIONALLY | law | Only if a stated prerequisite is met |

---

## 5. Prepositions — Relationships Between Nouns (18)

A preposition becomes an edge in the TRUG graph connecting two nouns.

### Flow (5) — Data movement direction

| # | Word | Source | Definition | CORE |
|---|---|---|---|---|
| 165 | FEEDS | computation | Data flows unconditionally from source to destination | yes |
| 166 | ROUTES | computation | Data flows conditionally based on predicate | yes |
| 167 | TO | computation | Directional: data moves toward destination | |
| 168 | FROM | computation | Directional: data originates at source | |
| 169 | RETURNS_TO | computation | Output flows back to a previous node | |

### Dependency (5) — What constrains what

| # | Word | Source | Definition | CORE |
|---|---|---|---|---|
| 170 | BINDS | computation | Schema constrains what a node accepts or produces | yes |
| 171 | DEPENDS_ON | computation | Source requires target to function | yes |
| 172 | IMPLEMENTS | computation | Source fulfills the contract of target | |
| 173 | EXTENDS | computation | Source adds capability to target | |
| 174 | SUBJECT_TO | law | Source is constrained by target | yes |

### Containment (1)

| # | Word | Source | Definition | CORE |
|---|---|---|---|---|
| 175 | CONTAINS | computation | Parent structurally holds child | yes |

### Reference (1)

| # | Word | Source | Definition | CORE |
|---|---|---|---|---|
| 176 | REFERENCES | computation | Non-hierarchical cross-reference | yes |

### Replacement (1)

| # | Word | Source | Definition | CORE |
|---|---|---|---|---|
| 177 | SUPERSEDES | computation | Source completely replaces target | yes |

### Authority (3)

| # | Word | Source | Definition | CORE |
|---|---|---|---|---|
| 178 | GOVERNS | law | Source has authority over target | yes |
| 179 | PURSUANT_TO | law | In accordance with; as directed by | |
| 180 | ON_BEHALF_OF | law | Acting with delegated authority for another | |

### Binding (2) — Establish identity or criterion

| # | Word | Source | Definition |
|---|---|---|---|
| 181 | AS | computation | Binds an identifier to a type or role |
| 182 | BY | computation | Specifies the key, criterion, or basis for an operation |

---

## 6. Conjunctions — Sentence Combinators (13)

A conjunction connects complete clauses. Each clause must independently be a valid sentence.

### Sequence (2)

| # | Word | Source | Definition |
|---|---|---|---|
| 183 | THEN | computation | Execute next step after current completes |
| 184 | FINALLY | computation | Execute regardless of success or failure |

### Parallel (1)

| # | Word | Source | Definition |
|---|---|---|---|
| 185 | AND | computation | Execute both; both must succeed |

### Alternative (2)

| # | Word | Source | Definition |
|---|---|---|---|
| 186 | OR | computation | Execute alternative if first fails or is false |
| 187 | ELSE | computation | Execute only when preceding condition is false |

### Cause (3)

| # | Word | Source | Definition |
|---|---|---|---|
| 188 | IF | computation | Execute following clause only when condition is true |
| 189 | WHEN | computation | Execute following clause upon event occurrence |
| 190 | WHILE | computation | Continue executing as long as condition holds |

### Exception (5)

| # | Word | Source | Definition |
|---|---|---|---|
| 191 | UNLESS | law | Clause does not apply if exception condition is met |
| 192 | EXCEPT | law | Everything applies other than the stated carve-out |
| 193 | NOTWITHSTANDING | law | Overrides any conflicting clause |
| 194 | PROVIDED_THAT | law | Clause applies only if the stated condition is met |
| 195 | WHEREAS | law | Establishes factual context for what follows (preamble only) |

---

## 7. Articles — Quantifiers and Determiners (10)

An article specifies which or how many of a noun. Precedes adjectives and nouns. Shared vocabulary — same words, same meaning in both computation and law.

### Specific (2)

| # | Word | Definition |
|---|---|---|
| 196 | THE | One specific, previously identified instance |
| 197 | THIS | The instance in current scope |

### Universal (3)

| # | Word | Definition |
|---|---|---|
| 198 | ALL | Every instance without exception |
| 199 | EACH | Every instance, considered individually |
| 200 | EVERY | Every instance (synonym of ALL, emphasizes completeness) |

### Existential (3)

| # | Word | Definition |
|---|---|---|
| 201 | ANY | At least one; whichever satisfies |
| 202 | SOME | One or more, unspecified which |
| 203 | A | Exactly one, unspecified which |

### Negative (2)

| # | Word | Definition |
|---|---|---|
| 204 | NO | Zero instances |
| 205 | NONE | Zero instances (used without following noun) |

---

## 8. Pronouns — Back-References (7)

A pronoun refers to a previously named noun. Must have an unambiguous antecedent in the same sentence. Cross-sentence references use THE + NOUN or SAID + NOUN.

### Self (1)

| # | Word | Source | Definition |
|---|---|---|---|
| 206 | SELF | computation | The current actor or scope |

### Result (2)

| # | Word | Source | Definition |
|---|---|---|---|
| 207 | RESULT | computation | The output of the most recent verb |
| 208 | OUTPUT | computation | The data produced by a transform |

### Source (2)

| # | Word | Source | Definition |
|---|---|---|---|
| 209 | INPUT | computation | The data received by the current operation |
| 210 | SOURCE | computation | The originating node of the current data |

### Target (1)

| # | Word | Source | Definition |
|---|---|---|---|
| 211 | TARGET | computation | The destination node of the current action |

### Legal reference (1)

| # | Word | Source | Definition |
|---|---|---|---|
| 212 | SAID | law | The previously named noun (legal "the") |

---

## 9. Level Prefixes — Hierarchy Transition Markers (21)

A level prefix names a metric level in the TRUG hierarchy. The 21 SI prefixes (plus `BASE` for the default level) form a closed scale from macro (10²⁴) to micro (10⁻²⁴). Combined with a semantic name they form a `metric_level` identifier, e.g. `KILO_REPOSITORY`, `BASE_FUNCTION`, `DECI_LINE`.

In TRL, a level prefix joined with an UPPERCASE semantic name appears as a bare token on its own line — a **level directive** — to mark a transition between hierarchy levels for an LLM consumer reading the source. Level directives are an LLM-comprehension affordance: they compile to nothing, produce no node or edge, and the validator does not enforce them. See `SPEC_grammar.md §level_directive`.

`BASE` (10⁰, no scaling factor) names the default consumption level — the "ground zero" plane of every TRUG, the most information-dense and the level a fresh consumer should reach first.

### Macro (10) — Zoom out — scaling factors above 10⁰

| # | Word | Factor | Definition |
|---|---|---|---|
| 213 | YOTTA | 10²⁴ | Largest macro scale |
| 214 | ZETTA | 10²¹ | |
| 215 | EXA | 10¹⁸ | |
| 216 | PETA | 10¹⁵ | |
| 217 | TERA | 10¹² | |
| 218 | GIGA | 10⁹ | |
| 219 | MEGA | 10⁶ | |
| 220 | KILO | 10³ | |
| 221 | HECTO | 10² | |
| 222 | DEKA | 10¹ | Smallest macro scale |

### Default (1) — Ground zero — the generally accessible plane

| # | Word | Factor | Definition |
|---|---|---|---|
| 223 | BASE | 10⁰ | Default consumption level — no prefix scaling, the generally accessible plane |

### Micro (10) — Zoom in — scaling factors below 10⁰

| # | Word | Factor | Definition |
|---|---|---|---|
| 224 | DECI | 10⁻¹ | Largest micro scale |
| 225 | CENTI | 10⁻² | |
| 226 | MILLI | 10⁻³ | |
| 227 | MICRO | 10⁻⁶ | |
| 228 | NANO | 10⁻⁹ | |
| 229 | PICO | 10⁻¹² | |
| 230 | FEMTO | 10⁻¹⁵ | |
| 231 | ATTO | 10⁻¹⁸ | |
| 232 | ZEPTO | 10⁻²¹ | |
| 233 | YOCTO | 10⁻²⁴ | Smallest micro scale |

### Composition

A `metric_level` identifier is formed as `<LEVEL_PREFIX>_<UPPERCASE_SEMANTIC_NAME>`. The semantic name is domain-defined (REPOSITORY, FOLDER, FILE, FUNCTION, LINE, STATEMENT, etc.) and follows the rules in `TRUGS_PROTOCOL/SCHEMA.md §Metric Level Prefixes`. Examples:

```
KILO_REPOSITORY      MEGA_PORTFOLIO       BASE_FUNCTION
DECI_STATEMENT       CENTI_TOKEN          MICRO_BIT
```

### Level directive in TRL

When a TRL source crosses from one metric level to another, the new level's name appears alone on a line. Example:

```
PARTY system SHALL FILTER ALL ACTIVE RECORD
  THEN SORT RESULT.

DECI_STATEMENT

PARTY system SHALL VALIDATE EACH FIELD 'of RESULT.

CENTI_TOKEN

PARTY system SHALL ASSERT TYPE EQUALS STRING.
```

Each directive marks the start of work at that level. Directives are sugar-equivalent: they compile to nothing, but unlike `'sugar` they retain their executable-vocabulary identity and can be referenced inside a sentence as a `metric_level` value (e.g. `... AT BASE_FUNCTION`). See `SPEC_grammar.md` for the BNF rule.

---

## 10. Sugar — Human Readability Pattern

Sugar is any token matching the pattern `'[a-z_]+` — an apostrophe followed by one or more lowercase letters or underscores. Sugar compiles to nothing. No node, no edge, no property. The validator ignores it. The compiler strips it. Sugar exists only to make sentences readable by humans.

Without sugar: `PARTY system SHALL FILTER ALL ACTIVE RECORD`
With sugar: `PARTY system SHALL 'please FILTER ALL 'of 'the ACTIVE RECORD`

Both compile to the identical graph.

### Pattern

```
sugar := "'" [a-z_]+
```

Any token beginning with `'` followed by lowercase characters is sugar. Position-independent — sugar may appear anywhere in a sentence. The apostrophe prefix is the visual signal: lowercase after `'` means "this compiles to nothing."

### Common Sugar Words

These are the most frequently used sugar words. They correspond to English function words that improve readability.

| Word | Category | Usage |
|---|---|---|
| `'of` | Connective | `ALL 'of 'the RECORD` |
| `'is` | Connective | `PARTY admin 'is 'the PRINCIPAL` |
| `'are` | Connective | `ALL RECORD 'are VALID` |
| `'be` | Connective | `SHALL 'be WRITTEN` |
| `'been` | Connective | `'has 'been VALIDATED` |
| `'has` | Connective | `PARTY system 'has COMPLETED` |
| `'have` | Connective | `ALL PARTY 'have AUTHENTICATED` |
| `'will` | Connective | `PARTY system 'will FILTER` |
| `'that` | Relative | `'the RECORD 'that 'is VALID` |
| `'which` | Relative | `'the RECORD 'which 'is ACTIVE` |
| `'where` | Relative | `'the ENDPOINT 'where RESULT FEEDS` |
| `'who` | Relative | `'the PARTY 'who SHALL VALIDATE` |
| `'into` | Filler | `MERGE RESULT 'into STREAM` |
| `'upon` | Filler | `'upon COMPLETION` |
| `'with` | Filler | `FILTER RECORD 'with VALID STATE` |
| `'for` | Filler | `VALIDATE 'for COMPLIANCE` |
| `'at` | Filler | `WRITE 'at ENDPOINT output` |
| `'on` | Filler | `RETRY 'on FAILURE` |
| `'please` | Politeness | `'please VALIDATE ALL RECORD` |
| `'also` | Politeness | `'also SORT RESULT` |
| `'then_also` | Politeness | `THEN 'also WRITE RESULT` |
| `'these` | Determiner | `VALIDATE 'these RECORD` |
| `'those` | Determiner | `FILTER 'those ACTIVE RECORD` |
| `'such` | Determiner | `'such RECORD SHALL 'be VALIDATED` |

### Custom Sugar

Any `'word` works. Custom sugar lets authors annotate sentences with domain context that the compiler ignores:

```
PARTY system SHALL WRITE DATA 'to 'the 'postgres ENDPOINT store.
PARTY admin 'trugs_llc SHALL ADMINISTER ALL RESOURCE.
```

`'postgres` and `'trugs_llc` are sugar — they compile to nothing but tell the human reader what system or entity is involved.

**Rule:** Sugar tokens may appear anywhere in a sentence without changing its meaning, graph compilation, or validation result. A sentence with sugar and the same sentence without sugar are semantically identical — they produce the same graph.

---

## 11. Summary

| Part of Speech | Computation | Law | Shared | Total | Compiles To |
|---|---|---|---|---|---|
| Nouns | 20 | 6 | — | 26 | Nodes |
| Verbs | 61 | 19 | — | 80 | Operations |
| Adjectives | 29 | 10 | — | 39 | Properties |
| Adverbs | 12 | 7 | — | 19 | Op properties |
| Prepositions | 14 | 4 | — | 18 | Edges |
| Conjunctions | 8 | 5 | — | 13 | Structure |
| Articles | — | — | 10 | 10 | Scope |
| Pronouns | 6 | 1 | — | 7 | References |
| Level prefixes | — | — | 21 | 21 | Hierarchy markers (no-op in graph) |
| Sugar | — | — | ∞ (pattern) | `'[a-z_]+` | **Nothing** |
| **Total** | **150** | **52** | **31** | **233** | |

233 executable words + `'word` sugar pattern. Sugar is not counted as vocabulary — it is a syntactic pattern (`'[a-z_]+`) that compiles to nothing. Level prefixes are counted but produce no graph artifacts when used as bare-line directives; they DO contribute when used as the prefix of a `metric_level` value. The executable vocabulary is 233 words.

### Modals (subset of verbs)

Three verbs serve as modals — they modify other verbs to establish obligation, permission, or prohibition:

| Modal | Meaning | From |
|---|---|---|
| SHALL | Mandatory; failure is breach | Law |
| SHALL_NOT | Prohibited; performance is breach | Law |
| MAY | Permitted but not required | Law |

Modals require Actor subjects. A modal + verb creates an obligation/permission on the actor.

---

## 12. Vocabulary-closure design notes

The 233-word vocabulary is **closed by design**. When a domain concept seems to call for a new word, the first move is to express it with existing vocabulary before extending the language. Two worked examples:

### Temporal constraints without `DEADLINE`

A scheduled operation with a time limit uses existing vocabulary:

```
DEFINE "deadline" AS INSTRUMENT.
PARTY scheduler SHALL AGGREGATE ALL ACTIVE RECORD ONCE WITHIN 24h
  THEN WRITE RESULT TO ENDPOINT report
  SUBJECT_TO INSTRUMENT deadline.
```

The temporal constraint is modelled as an `INSTRUMENT` (#14, a formal document) defined upfront with `DEFINE ... AS`. Adverb-value pairs (`ONCE`, `WITHIN 24h`) carry the timing. `DEADLINE` is not a keyword — it's an identifier inside quotes. The closed 233-word vocabulary suffices. See SPEC_examples.md example 7.

### Precedent / advisory constraints with `PRECEDENT`

`PRECEDENT` (#130, an adjective / state) is already in the vocabulary under Adjectives → Legal state. `REFERENCES` (#176) is the edge. Combined:

```
WHEREAS THE RECORD history REFERENCES RECORD current.
PARTY system SHALL VALIDATE THE RECORD current
  SUBJECT_TO PRECEDENT RECORD history.
```

No new keyword needed. See SPEC_examples.md example 24.

### Rule of thumb for would-be new words

1. **Is it already in the vocabulary in a different part of speech?** (PRECEDENT as adjective is different from PRECEDENT as noun — but the adjective form often covers the need.)
2. **Can it be expressed as `DEFINE "name" AS CATEGORY`?** (INSTRUMENT, RECORD, RESOURCE — generic categories absorb domain-specific instances.)
3. **Is it a BRANCH concern?** Domain-specific vocabularies layer onto CORE. Legal-domain words like FILING, WITNESS, TESTIMONY belong in a LEGAL branch vocabulary, not in core TRL.
4. **Only after 1-3 fail:** consider extending the vocabulary (as AAA #2048 did — 22 corpus-evidenced additions, 211 → 233).

Resolved in [Xepayac/TRUGS-DEVELOPMENT#1542](https://github.com/Xepayac/TRUGS-DEVELOPMENT/issues/1542) (2026-04-18).
