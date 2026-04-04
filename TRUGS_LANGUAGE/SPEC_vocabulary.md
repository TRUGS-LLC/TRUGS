# TRUGS Language Vocabulary

> 190 words across 8 parts of speech. Computation primary, law fills gaps.

**Issue:** #1211 | **Version:** 1.0.1

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

## 2. Verbs — Actions That Execute (61)

A verb transforms state or establishes obligation. Every sentence has exactly one primary verb. Verbs chain with conjunctions.

### Transform (14) — Change data shape

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

### Move (10) — Move data between actors

| # | Word | Source | Definition | CORE |
|---|---|---|---|---|
| 41 | READ | computation | Input data from external source | yes |
| 42 | WRITE | computation | Output data to external destination | yes |
| 43 | SEND | computation | Transmit data to another actor | |
| 44 | RECEIVE | computation | Accept data from another actor | |
| 45 | RETURN | computation | Emit final output and terminate | |
| 46 | REQUEST | computation | Send message expecting a response | yes |
| 47 | RESPOND | computation | Reply to a prior request | yes |
| 48 | AUTHENTICATE | computation | Prove identity to another actor | |
| 49 | DELIVER | law | Transfer possession of an artifact to another party | |
| 50 | ASSIGN | law | Transfer rights or obligations to another party | |

### Obligate (4) — Mandate behavior

| # | Word | Source | Definition | CORE |
|---|---|---|---|---|
| 51 | VALIDATE | computation | Assert data satisfies condition; halt if not | yes |
| 52 | ASSERT | computation | Declare a condition that must be true | |
| 53 | REQUIRE | computation | Declare a hard prerequisite | |
| 54 | SHALL | law | Mandatory: party MUST perform action | yes |

### Permit (5) — Allow behavior

| # | Word | Source | Definition | CORE |
|---|---|---|---|---|
| 55 | ALLOW | computation | Permit an action without mandating it | |
| 56 | APPROVE | computation | Accept as satisfying criteria; opposite of REJECT | |
| 57 | GRANT | law | Confer a right or permission to another party | |
| 58 | OVERRIDE | law | Supersede a constraint or prohibition for this action | |
| 59 | MAY | law | Permitted: party is allowed but not required | yes |

### Prohibit (4) — Forbid behavior

| # | Word | Source | Definition | CORE |
|---|---|---|---|---|
| 60 | DENY | computation | Refuse a requested action | |
| 61 | REJECT | computation | Refuse input that does not meet criteria | |
| 62 | SHALL_NOT | law | Prohibited: party MUST NOT perform action | yes |
| 63 | REVOKE | law | Withdraw a previously granted right or permission | |

### Control (10) — Direct execution flow

| # | Word | Source | Definition | CORE |
|---|---|---|---|---|
| 64 | BRANCH | computation | Route to one of two paths on boolean condition | yes |
| 65 | MATCH | computation | Route to one of N paths on pattern | yes |
| 66 | RETRY | computation | Re-attempt failed operation up to bounded count | yes |
| 67 | TIMEOUT | computation | Bound wall-clock time for an operation | yes |
| 68 | THROW | computation | Generate an error condition; directs flow to error handler | |
| 69 | EXISTS | computation | Evaluates true if the noun is present and non-null | |
| 70 | EXPIRE | computation | Transition to EXPIRED state; deadline passed | |
| 71 | EQUALS | computation | Evaluates true if left and right values are identical | |
| 72 | EXCEEDS | computation | Evaluates true if left value is greater than right | |
| 73 | PRECEDES | computation | Evaluates true if left value is less than right | |

### Bind (9) — Establish meaning or structural relationships

| # | Word | Source | Definition | CORE |
|---|---|---|---|---|
| 74 | DEFINE | computation | Establish the meaning of a term | |
| 75 | DECLARE | computation | State a fact or create a named thing | |
| 76 | IMPLEMENT | computation | Fulfill the contract of an interface | |
| 77 | NEST | computation | Place one thing structurally inside another | |
| 78 | AUGMENT | computation | Add capability to an existing thing | |
| 79 | REPLACE | computation | Entirely substitute one thing for another | |
| 80 | CITE | law | Formally refer to another entity | |
| 81 | ADMINISTER | law | Establish and exercise authority over | |
| 82 | STIPULATE | law | Establish a binding agreed-upon condition | |

### Resolve (5) — Respond to failure

| # | Word | Source | Definition | CORE |
|---|---|---|---|---|
| 83 | CATCH | computation | Intercept an error and enter recovery | |
| 84 | HANDLE | computation | Process an error condition | |
| 85 | RECOVER | computation | Restore normal operation after failure | |
| 86 | CURE | law | Correct a breach within allowed time | |
| 87 | INDEMNIFY | law | Compensate for loss caused by breach | |

---

## 3. Adjectives — Constraints on Nouns (36)

An adjective constrains what a noun is or can do. Precedes the noun. Stacking order: Quantity > Priority > State > Access > Type > Noun.

### Type (5) — What kind of thing

| # | Word | Source | Definition |
|---|---|---|---|
| 88 | STRING | computation | Text data type |
| 89 | INTEGER | computation | Whole number data type |
| 90 | BOOLEAN | computation | True/false data type |
| 91 | ARRAY | computation | Ordered collection data type |
| 92 | OBJECT | computation | Key-value structure data type |

### Access (5) — Who can see/touch it

| # | Word | Source | Definition |
|---|---|---|---|
| 93 | PUBLIC | computation | Accessible to any actor |
| 94 | PRIVATE | computation | Accessible only to the owning actor |
| 95 | PROTECTED | computation | Accessible to the owning actor and its children |
| 96 | READONLY | computation | Can be read but not written |
| 97 | CONFIDENTIAL | law | Restricted to authorized parties only |

### State (14) — Current condition

| # | Word | Source | Definition |
|---|---|---|---|
| 98 | VALID | computation | Satisfies all declared constraints |
| 99 | INVALID | computation | Fails one or more declared constraints |
| 100 | NULL | computation | Absent; no value |
| 101 | EMPTY | computation | Present but containing nothing |
| 102 | PENDING | computation | Created but not yet processed |
| 103 | ACTIVE | computation | Currently in use or executing |
| 104 | FAILED | computation | Terminated with error |
| 105 | MUTABLE | computation | Can be changed after creation |
| 106 | IMMUTABLE | computation | Cannot be changed after creation |
| 107 | BINDING | law | Creates enforceable obligation |
| 108 | VOID | law | Without legal effect; as if it never existed |
| 109 | ENFORCEABLE | law | Can be compelled by remedy |
| 110 | EXPIRED | law | Past its deadline; no longer in effect |
| 111 | PRECEDENT | law | Informing but not binding; advisory based on prior decision |

### Quantity (6) — How many / whether required

| # | Word | Source | Definition |
|---|---|---|---|
| 112 | REQUIRED | computation | Must be present; absence is an error |
| 113 | OPTIONAL | computation | May be absent; absence is acceptable |
| 114 | UNIQUE | computation | Exactly one instance may exist |
| 115 | MULTIPLE | computation | More than one instance may exist |
| 116 | SOLE | law | One and only one; no others permitted |
| 117 | JOINT | law | Shared equally among multiple parties |

### Priority (6) — Relative importance

| # | Word | Source | Definition |
|---|---|---|---|
| 118 | DEFAULT | computation | The value used when none is specified |
| 119 | CRITICAL | computation | Failure is unrecoverable |
| 120 | HIGH | computation | Elevated importance |
| 121 | LOW | computation | Reduced importance |
| 122 | MATERIAL | law | Significant enough to affect decisions |
| 123 | SUBORDINATE | law | Lower in authority hierarchy |

---

## 4. Adverbs — Constraints on Verbs (19)

An adverb constrains how a verb executes. Follows the verb. Each adverb optionally carries a value.

### Timing (9) — When/how fast

| # | Word | Source | Definition |
|---|---|---|---|
| 124 | ASYNC | computation | Execute without blocking the caller |
| 125 | SYNC | computation | Execute and block until complete |
| 126 | SEQUENTIAL | computation | Execute steps one after another in order |
| 127 | PARALLEL | computation | Execute steps simultaneously |
| 128 | IMMEDIATE | computation | Execute with no delay |
| 129 | LAZY | computation | Defer execution until the result is needed |
| 130 | PROMPTLY | law | Within a reasonable time, without unnecessary delay |
| 131 | FORTHWITH | law | Immediately and without any delay |
| 132 | WITHIN | law | Before the specified duration elapses (requires duration) |

### Repetition (4) — How often

| # | Word | Source | Definition |
|---|---|---|---|
| 133 | ONCE | computation | Execute exactly one time |
| 134 | ALWAYS | computation | Execute every time the condition is met |
| 135 | NEVER | computation | Do not execute under any condition |
| 136 | BOUNDED | computation | Execute up to N times (requires integer) |

### Degree (4) — How precisely

| # | Word | Source | Definition |
|---|---|---|---|
| 137 | STRICTLY | computation | With zero tolerance for deviation |
| 138 | PARTIALLY | computation | Affecting some but not all items |
| 139 | SUBSTANTIALLY | law | In all material respects; minor deviations tolerated |
| 140 | REASONABLY | law | As a competent party would under the circumstances |

### Condition (2) — Whether qualified

| # | Word | Source | Definition |
|---|---|---|---|
| 141 | UNCONDITIONALLY | law | Without any prerequisite or qualification |
| 142 | CONDITIONALLY | law | Only if a stated prerequisite is met |

---

## 5. Prepositions — Relationships Between Nouns (18)

A preposition becomes an edge in the TRUG graph connecting two nouns.

### Flow (5) — Data movement direction

| # | Word | Source | Definition | CORE |
|---|---|---|---|---|
| 143 | FEEDS | computation | Data flows unconditionally from source to destination | yes |
| 144 | ROUTES | computation | Data flows conditionally based on predicate | yes |
| 145 | TO | computation | Directional: data moves toward destination | |
| 146 | FROM | computation | Directional: data originates at source | |
| 147 | RETURNS_TO | computation | Output flows back to a previous node | |

### Dependency (5) — What constrains what

| # | Word | Source | Definition | CORE |
|---|---|---|---|---|
| 148 | BINDS | computation | Schema constrains what a node accepts or produces | yes |
| 149 | DEPENDS_ON | computation | Source requires target to function | yes |
| 150 | IMPLEMENTS | computation | Source fulfills the contract of target | |
| 151 | EXTENDS | computation | Source adds capability to target | |
| 152 | SUBJECT_TO | law | Source is constrained by target | yes |

### Containment (1)

| # | Word | Source | Definition | CORE |
|---|---|---|---|---|
| 153 | CONTAINS | computation | Parent structurally holds child | yes |

### Reference (1)

| # | Word | Source | Definition | CORE |
|---|---|---|---|---|
| 154 | REFERENCES | computation | Non-hierarchical cross-reference | yes |

### Replacement (1)

| # | Word | Source | Definition | CORE |
|---|---|---|---|---|
| 155 | SUPERSEDES | computation | Source completely replaces target | yes |

### Authority (3)

| # | Word | Source | Definition | CORE |
|---|---|---|---|---|
| 156 | GOVERNS | law | Source has authority over target | yes |
| 157 | PURSUANT_TO | law | In accordance with; as directed by | |
| 158 | ON_BEHALF_OF | law | Acting with delegated authority for another | |

### Binding (2) — Establish identity or criterion

| # | Word | Source | Definition |
|---|---|---|---|
| 159 | AS | computation | Binds an identifier to a type or role |
| 160 | BY | computation | Specifies the key, criterion, or basis for an operation |

---

## 6. Conjunctions — Sentence Combinators (13)

A conjunction connects complete clauses. Each clause must independently be a valid sentence.

### Sequence (2)

| # | Word | Source | Definition |
|---|---|---|---|
| 161 | THEN | computation | Execute next step after current completes |
| 162 | FINALLY | computation | Execute regardless of success or failure |

### Parallel (1)

| # | Word | Source | Definition |
|---|---|---|---|
| 163 | AND | computation | Execute both; both must succeed |

### Alternative (2)

| # | Word | Source | Definition |
|---|---|---|---|
| 164 | OR | computation | Execute alternative if first fails or is false |
| 165 | ELSE | computation | Execute only when preceding condition is false |

### Cause (3)

| # | Word | Source | Definition |
|---|---|---|---|
| 166 | IF | computation | Execute following clause only when condition is true |
| 167 | WHEN | computation | Execute following clause upon event occurrence |
| 168 | WHILE | computation | Continue executing as long as condition holds |

### Exception (5)

| # | Word | Source | Definition |
|---|---|---|---|
| 169 | UNLESS | law | Clause does not apply if exception condition is met |
| 170 | EXCEPT | law | Everything applies other than the stated carve-out |
| 171 | NOTWITHSTANDING | law | Overrides any conflicting clause |
| 172 | PROVIDED_THAT | law | Clause applies only if the stated condition is met |
| 173 | WHEREAS | law | Establishes factual context for what follows (preamble only) |

---

## 7. Articles — Quantifiers and Determiners (10)

An article specifies which or how many of a noun. Precedes adjectives and nouns. Shared vocabulary — same words, same meaning in both computation and law.

### Specific (2)

| # | Word | Definition |
|---|---|---|
| 174 | THE | One specific, previously identified instance |
| 175 | THIS | The instance in current scope |

### Universal (3)

| # | Word | Definition |
|---|---|---|
| 176 | ALL | Every instance without exception |
| 177 | EACH | Every instance, considered individually |
| 178 | EVERY | Every instance (synonym of ALL, emphasizes completeness) |

### Existential (3)

| # | Word | Definition |
|---|---|---|
| 179 | ANY | At least one; whichever satisfies |
| 180 | SOME | One or more, unspecified which |
| 181 | A | Exactly one, unspecified which |

### Negative (2)

| # | Word | Definition |
|---|---|---|
| 182 | NO | Zero instances |
| 183 | NONE | Zero instances (used without following noun) |

---

## 8. Pronouns — Back-References (7)

A pronoun refers to a previously named noun. Must have an unambiguous antecedent in the same sentence. Cross-sentence references use THE + NOUN or SAID + NOUN.

### Self (1)

| # | Word | Source | Definition |
|---|---|---|---|
| 184 | SELF | computation | The current actor or scope |

### Result (2)

| # | Word | Source | Definition |
|---|---|---|---|
| 185 | RESULT | computation | The output of the most recent verb |
| 186 | OUTPUT | computation | The data produced by a transform |

### Source (2)

| # | Word | Source | Definition |
|---|---|---|---|
| 187 | INPUT | computation | The data received by the current operation |
| 188 | SOURCE | computation | The originating node of the current data |

### Target (1)

| # | Word | Source | Definition |
|---|---|---|---|
| 189 | TARGET | computation | The destination node of the current action |

### Legal reference (1)

| # | Word | Source | Definition |
|---|---|---|---|
| 190 | SAID | law | The previously named noun (legal "the") |

---

## 9. Sugar — Human Readability Pattern

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

## 10. Summary

| Part of Speech | Computation | Law | Shared | Total | Compiles To |
|---|---|---|---|---|---|
| Nouns | 20 | 6 | — | 26 | Nodes |
| Verbs | 42 | 19 | — | 61 | Operations |
| Adjectives | 26 | 10 | — | 36 | Properties |
| Adverbs | 12 | 7 | — | 19 | Op properties |
| Prepositions | 14 | 4 | — | 18 | Edges |
| Conjunctions | 8 | 5 | — | 13 | Structure |
| Articles | — | — | 10 | 10 | Scope |
| Pronouns | 6 | 1 | — | 7 | References |
| Sugar | — | — | ∞ (pattern) | `'[a-z_]+` | **Nothing** |
| **Total** | **128** | **52** | **10** | **190** | |

190 executable words + `'word` sugar pattern. Sugar is not counted as vocabulary — it is a syntactic pattern (`'[a-z_]+`) that compiles to nothing. The executable vocabulary is 190 words: 71% computation, 24% law, 5% shared.

### Modals (subset of verbs)

Three verbs serve as modals — they modify other verbs to establish obligation, permission, or prohibition:

| Modal | Meaning | From |
|---|---|---|
| SHALL | Mandatory; failure is breach | Law |
| SHALL_NOT | Prohibited; performance is breach | Law |
| MAY | Permitted but not required | Law |

Modals require Actor subjects. A modal + verb creates an obligation/permission on the actor.
