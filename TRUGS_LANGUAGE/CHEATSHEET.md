# TRL Cheat Sheet — 190 Words

## Nouns (26) — become graph nodes

| Word | Sub | Word | Sub | Word | Sub |
|------|-----|------|-----|------|-----|
| PROCESS | Actor | DATA | Artifact | PIPELINE | Container |
| SERVICE | Actor | FILE | Artifact | STAGE | Container |
| FUNCTION | Actor | RECORD | Artifact | MODULE | Container |
| TRANSFORM | Actor | MESSAGE | Artifact | NAMESPACE | Container |
| PARTY | Actor | STREAM | Artifact | ENTRY | Boundary |
| AGENT | Actor | RESOURCE | Artifact | EXIT | Boundary |
| PRINCIPAL | Actor | INSTRUMENT | Artifact | INTERFACE | Boundary |
| ERROR | Outcome | EXCEPTION | Outcome | ENDPOINT | Boundary |
| REMEDY | Outcome | | | JURISDICTION | Boundary |

## Verbs (61) — become operations

| Category | Words |
|----------|-------|
| Transform (14) | FILTER EXCLUDE MAP SORT MERGE SPLIT FLATTEN AGGREGATE GROUP RENAME BATCH DISTINCT TAKE SKIP |
| Move (10) | READ WRITE SEND RECEIVE RETURN REQUEST RESPOND AUTHENTICATE DELIVER ASSIGN |
| Obligate (4) | VALIDATE ASSERT REQUIRE SHALL |
| Permit (5) | ALLOW APPROVE GRANT OVERRIDE MAY |
| Prohibit (4) | DENY REJECT SHALL_NOT REVOKE |
| Control (10) | BRANCH MATCH RETRY TIMEOUT THROW EXISTS EXPIRE EQUALS EXCEEDS PRECEDES |
| Bind (9) | DEFINE DECLARE IMPLEMENT NEST AUGMENT REPLACE CITE ADMINISTER STIPULATE |
| Resolve (5) | CATCH HANDLE RECOVER CURE INDEMNIFY |

## Modals (3) — obligation on Actor subjects

| Modal | Meaning |
|-------|---------|
| SHALL | MUST do |
| MAY | ALLOWED to do |
| SHALL_NOT | MUST NOT do |

## Adjectives (36) — become node properties

| Category | Words |
|----------|-------|
| Type (5) | STRING INTEGER BOOLEAN ARRAY OBJECT |
| Access (5) | PUBLIC PRIVATE PROTECTED READONLY CONFIDENTIAL |
| State (14) | VALID INVALID NULL EMPTY PENDING ACTIVE FAILED MUTABLE IMMUTABLE BINDING VOID ENFORCEABLE EXPIRED PRECEDENT |
| Quantity (6) | REQUIRED OPTIONAL UNIQUE MULTIPLE SOLE JOINT |
| Priority (6) | DEFAULT CRITICAL HIGH LOW MATERIAL SUBORDINATE |

## Adverbs (19) — become operation properties

| Category | Words |
|----------|-------|
| Timing (9) | ASYNC SYNC SEQUENTIAL PARALLEL IMMEDIATE LAZY PROMPTLY FORTHWITH WITHIN |
| Repetition (4) | ONCE ALWAYS NEVER BOUNDED |
| Degree (4) | STRICTLY PARTIALLY SUBSTANTIALLY REASONABLY |
| Condition (2) | UNCONDITIONALLY CONDITIONALLY |

## Prepositions (18) — become graph edges

| Category | Words |
|----------|-------|
| Flow (5) | FEEDS ROUTES TO FROM RETURNS_TO |
| Dependency (5) | BINDS DEPENDS_ON IMPLEMENTS EXTENDS SUBJECT_TO |
| Structure (3) | CONTAINS REFERENCES SUPERSEDES |
| Authority (3) | GOVERNS PURSUANT_TO ON_BEHALF_OF |
| Binding (2) | AS BY |

## Conjunctions (13) — connect clauses

| Category | Words |
|----------|-------|
| Sequence | THEN FINALLY |
| Parallel | AND |
| Alternative | OR ELSE |
| Cause | IF WHEN WHILE |
| Exception | UNLESS EXCEPT NOTWITHSTANDING PROVIDED_THAT WHEREAS |

## Articles (10) — scope selectors

| Specific | Universal | Existential | Negative |
|----------|-----------|-------------|----------|
| THE THIS | ALL EACH EVERY | ANY SOME A | NO NONE |

## Pronouns (7) — back-references

SELF | RESULT OUTPUT | INPUT SOURCE | TARGET | SAID

## Sugar — compiles to nothing

Pattern: `'[a-z_]+` — e.g. `'of`, `'is`, `'the`, `'please`. Human readability only.

---

## Common Patterns

```
PARTY x SHALL FILTER ALL ACTIVE RECORD THEN WRITE RESULT TO ENDPOINT out.
  Actor + obligation + transform + scope + object + sequence + move + target

AGENT a SHALL_NOT MERGE ANY RESOURCE TO ENDPOINT main.
  Actor + prohibition + action + scope + object + destination

EACH FUNCTION skill SHALL PRODUCE RECORD output THEN RESPOND TO PARTY human.
  Quantifier + actor + obligation + artifact + sequence + move + target

IF DATA input EXISTS THEN PARTY system SHALL VALIDATE RESULT SUBJECT_TO RECORD rule.
  Condition + check + sequence + obligation + validate + constraint

STAGE audit CONTAINS DATA code_quality AND DATA plan_compliance.
  Container + containment + parallel artifacts
```
