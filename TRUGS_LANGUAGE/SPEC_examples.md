# TRUGS Language Examples

> 30 examples parsed token-by-token against the grammar. Each example was written, parsed, and if it failed, the failure was diagnosed, the vocabulary/grammar was patched, and the sentence was rewritten.

**Issue:** #1211 | **Version:** 0.1.0

For full token-by-token parse tables, see the development workspace at `TRUGS_PROTOCOL/SPEC_language.md` Section 4.

---

## Simple Patterns

### 1. Simple obligation
```
PARTY system SHALL VALIDATE ALL PENDING RECORD.
```
Actor + modal + verb + article + adjective + artifact.

### 2. Conditional pipeline
```
PARTY api SHALL FILTER ALL ACTIVE RECORD
  THEN SORT RESULT
  UNLESS NO VALID RECORD REQUIRE SELF.
```
Sequential chain (THEN) with exception (UNLESS). Pronoun RESULT back-references FILTER output. REQUIRE replaces DEPENDS_ON as verb. SELF references the subject.

### 3. Multi-party request-response
```
PARTY client SHALL REQUEST PARTY server.
PARTY server SHALL RESPOND PROMPTLY WITHIN 30s
  OR PARTY client MAY RETRY BOUNDED 3
  THEN HANDLE THE ERROR.
```
Two sentences, two actors. Adverb-value pair (WITHIN 30s). Alternative (OR). Pronoun (THE ERROR).

### 4. Data transformation pipeline
```
PARTY system SHALL MAP EACH PENDING RECORD TO VALID DATA
  THEN MERGE RESULT TO STREAM output
  THEN WRITE RESULT TO ENDPOINT destination.
```
Three-step pipeline. TO preposition for direction. RESULT chains between steps.

### 5. Scope and authority
```
PARTY administrator SHALL ADMINISTER ALL PRIVATE RESOURCE
  CONTAINS NAMESPACE production.
NO PARTY SHALL WRITE READONLY RESOURCE
  NOTWITHSTANDING PARTY administrator MAY OVERRIDE.
```
ADMINISTER as verb (establishes authority). NOTWITHSTANDING exception overrides prohibition.

---

## Authentication and Delegation

### 6. Authentication flow
```
PARTY user SHALL AUTHENTICATE TO SERVICE gateway.
PARTY gateway MAY GRANT AGENT worker ON_BEHALF_OF PARTY user.
PARTY gateway SHALL ADMINISTER AGENT worker.
AGENT worker SHALL READ ALL PRIVATE RESOURCE.
```
Four sentences. ON_BEHALF_OF delegation. ADMINISTER establishes authority chain.

### 7. Scheduled operation with deadline
```
PARTY scheduler SHALL AGGREGATE ALL ACTIVE RECORD
  ONCE WITHIN 24h
  THEN WRITE RESULT TO ENDPOINT report
  SUBJECT_TO DEADLINE "2026-04-01".
```
Multiple adverb-value pairs (ONCE, WITHIN 24h). DEADLINE as temporal constraint.

---

## Error Handling

### 8. Error recovery with escalation
```
PARTY processor SHALL VALIDATE EACH REQUIRED RECORD.
IF PARTY processor THROW EXCEPTION
  THEN PARTY processor SHALL CATCH THE EXCEPTION
  THEN HANDLE THE ERROR
  OR PARTY processor SHALL SEND MESSAGE TO PARTY admin.
```
IF conditional. THROW (Control verb). CATCH + HANDLE resolve chain. OR escalation.

### 9. Prohibition with exception and remedy
```
NO PARTY SHALL WRITE CONFIDENTIAL RESOURCE
  EXCEPT PARTY owner MAY WRITE CONFIDENTIAL RESOURCE
    PROVIDED_THAT PARTY owner AUTHENTICATE TO SERVICE auth.
IF ANY PARTY WRITE CONFIDENTIAL RESOURCE
  THEN THE REMEDY DEPENDS_ON PARTY owner.
```
Three-level nesting: EXCEPT → PROVIDED_THAT. REMEDY as outcome node. DEPENDS_ON as preposition (edge).

---

## Definitions and Structure

### 10. Definition of terms
```
DEFINE "curator" AS PARTY.
PARTY curator SHALL VALIDATE ALL RECORD
  AND PARTY curator SHALL_NOT WRITE INVALID RECORD.
```
Subjectless DEFINE sentence. AND parallel conjunction.

### 11. Loop with termination
```
PARTY worker SHALL READ RECORD FROM STREAM input
  WHILE ACTIVE RECORD EXISTS
  THEN WRITE RESULT TO ENDPOINT output
  FINALLY PARTY worker SHALL SEND MESSAGE TO PARTY supervisor.
```
WHILE loop with EXISTS control verb. FINALLY guaranteed cleanup.

### 12. Chained transforms with schema binding
```
PARTY pipeline SHALL FILTER ALL ACTIVE RECORD
  THEN SORT RESULT
  THEN TAKE RESULT 10
  THEN MAP RESULT TO VALID DATA
  SUBJECT_TO INTERFACE schema.
```
Four-step chain. TAKE with integer value. SUBJECT_TO constraint at end.

---

## Advanced Patterns

### 13. Agent delegation chain
```
PARTY user SHALL REQUEST PARTY orchestrator.
PARTY orchestrator MAY SPLIT THE MESSAGE TO AGENT worker-a AND AGENT worker-b.
EACH AGENT SHALL HANDLE INPUT PARALLEL
  THEN MERGE RESULT TO PARTY orchestrator.
PARTY orchestrator SHALL RESPOND TO PARTY user.
```
Noun conjunction (AND between noun_phrases). PARALLEL adverb. Fan-out/fan-in.

### 14. Immutable record with versioning
```
DEFINE "ledger" AS IMMUTABLE RECORD.
PARTY system SHALL WRITE EACH VALID DATA TO RECORD ledger.
NO PARTY MAY WRITE RECORD ledger
  EXCEPT PARTY system.
PARTY system SHALL REPLACE THE RECORD ledger FROM SAID RECORD.
```
IMMUTABLE adjective in definition. REPLACE as verb (action of superseding). SAID pronoun.

### 15. Conditional permission with time constraint
```
PARTY reviewer MAY APPROVE THE PENDING RECORD WITHIN 48h
  PROVIDED_THAT PARTY reviewer VALIDATE THE RECORD.
IF NO PARTY APPROVE THE RECORD WITHIN 48h
  THEN PARTY system SHALL EXPIRE THE RECORD.
```
Time-bounded permission. APPROVE and EXPIRE verbs. Forced active voice ("system expires record" not "record expires").

---

## Stress Tests

### 16. Nested conditions (three-deep)
```
PARTY api SHALL FILTER ALL RECORD
  UNLESS PARTY admin OVERRIDE
    PROVIDED_THAT PARTY admin AUTHENTICATE TO SERVICE auth
      EXCEPT PARTY admin ADMINISTER SERVICE auth.
```
UNLESS → PROVIDED_THAT → EXCEPT (depth 3). ADMINISTER as verb.

### 17. Event-driven reactive pattern
```
WHEN PARTY client SEND MESSAGE TO SERVICE queue
  THEN SERVICE queue SHALL VALIDATE THE MESSAGE
  THEN SEND RESULT TO PARTY handler
  OR REJECT THE MESSAGE.
```
WHEN event trigger. Subject inheritance across THEN chain.

### 18. WHEREAS preamble
```
WHEREAS PARTY system ADMINISTER ALL RESOURCE.
WHEREAS ALL RECORD REQUIRE MODULE storage.
PARTY system SHALL VALIDATE EACH RECORD ONCE
  THEN WRITE RESULT TO ENDPOINT output.
```
Preambles establish context. ADMINISTER and REQUIRE as verbs. Operative sentence follows.

### 19. Cross-sentence reference
```
PARTY ingester SHALL READ ALL RECORD FROM STREAM raw-input.
PARTY transformer SHALL FILTER THE RECORD
  THEN MAP RESULT TO VALID DATA.
PARTY loader SHALL WRITE THE DATA TO ENDPOINT warehouse.
```
THE + NOUN for cross-sentence reference (not pronouns). Multi-actor pipeline across three sentences.

### 20. Concurrent actors with synchronization
```
PARTY worker-a SHALL FILTER ALL RECORD PARALLEL.
PARTY worker-b SHALL SORT ALL RECORD PARALLEL.
PARTY coordinator SHALL MERGE THE RECORD FROM PARTY worker-a
  AND THE RECORD FROM PARTY worker-b
  THEN WRITE RESULT TO ENDPOINT output.
```
Prepositional phrase conjunction (FROM X AND FROM Y). PARALLEL on separate actors. MERGE synchronization.

### 21. GROUP BY + AGGREGATE
```
PARTY analyst SHALL GROUP ALL RECORD BY FILE type
  THEN AGGREGATE EACH RESULT TO INTEGER DATA count
  THEN SORT RESULT
  THEN TAKE RESULT 10.
```
BY binding preposition. EACH RESULT iterates groups. Type adjective on output.

### 22. FLATTEN + MAP (flatMap)
```
PARTY processor SHALL MAP EACH RECORD TO ARRAY DATA
  THEN FLATTEN RESULT
  THEN DISTINCT RESULT
  THEN WRITE RESULT TO ENDPOINT output.
```
Four-step functional pipeline. Clean first-attempt parse.

### 23. Multi-level containment
```
DEFINE "api-system" AS NAMESPACE.
PARTY system SHALL NEST MODULE auth AND MODULE data AND MODULE search
  TO NAMESPACE api-system.
PARTY system SHALL NEST FUNCTION login AND FUNCTION logout
  TO MODULE auth.
PARTY system SHALL NEST FUNCTION read-record AND FUNCTION write-record
  TO MODULE data.
FUNCTION read-record REQUIRE MODULE auth.
FUNCTION write-record REQUIRE MODULE auth.
```
NEST as verb (action of containment). REQUIRE as verb (action of dependency). Explicit actor for structural actions.

### 24. PRECEDENT usage
```
WHEREAS THE RECORD history REFERENCES RECORD current.
PARTY system SHALL VALIDATE THE RECORD current
  SUBJECT_TO PRECEDENT RECORD history.
```
PRECEDENT as adjective (State). REFERENCES as preposition (edge). Advisory but not binding.

### 25. Batch processing with bounded retry
```
PARTY loader SHALL READ ALL RECORD FROM ENDPOINT source
  THEN BATCH RESULT 100
  THEN MAP EACH RESULT TO VALID DATA
    SUBJECT_TO INTERFACE schema
  THEN WRITE RESULT TO ENDPOINT destination
    OR RETRY BOUNDED 3 WITHIN 60s.
```
Multiple adverb_phrases on RETRY (BOUNDED 3 + WITHIN 60s). OR for retry fallback.

### 26. API rate limiting
```
DEFINE "rate-limit" AS REQUIRED INTEGER DATA.
PARTY client SHALL REQUEST PARTY api WITHIN 1s
  SUBJECT_TO DATA rate-limit.
IF PARTY client REQUEST PARTY api
  AND DATA rate-limit EXCEEDS 100
  THEN PARTY api SHALL REJECT THE MESSAGE
  THEN PARTY api SHALL SEND ERROR TO PARTY client.
```
Comparison verb EXCEEDS. Artifact as subject of Control verb. Compound IF condition (AND).

### 27. Self-describing language
```
DEFINE "word" AS DATA.
DEFINE "grammar-rule" AS DATA.
DEFINE "constraint" AS DATA.

EACH DATA word NEST STRING DATA name
  AND STRING DATA speech
  AND STRING DATA definition.

PARTY language SHALL ADMINISTER ALL DATA word
  AND ALL DATA grammar-rule
  AND ALL DATA constraint.

PARTY language SHALL VALIDATE EACH DATA word
  SUBJECT_TO INTERFACE language-schema.

NO PARTY SHALL AUGMENT PARTY language
  UNLESS PARTY language MAY APPROVE.
```
The language describes its own structure — words, grammar, constraints, authority. NEST, ADMINISTER, AUGMENT as verbs. Self-referential and valid.

### 28. Complete ETL pipeline (real-world)
```
DEFINE "raw-event" AS STRING DATA.
DEFINE "clean-event" AS VALID OBJECT DATA.
DEFINE "event-store" AS IMMUTABLE ENDPOINT.

WHEREAS SERVICE kafka FEEDS STREAM raw-events.
WHEREAS ENDPOINT event-store REQUIRE MODULE postgres.

PARTY ingester SHALL READ EACH DATA raw-event FROM STREAM raw-events
  WITHIN 100ms
  OR PARTY ingester SHALL RETRY BOUNDED 5 WITHIN 30s
  OR THROW EXCEPTION.

PARTY transformer SHALL VALIDATE THE DATA raw-event
  SUBJECT_TO INTERFACE event-schema
  THEN MAP RESULT TO DATA clean-event
  THEN BATCH RESULT 500.

PARTY loader SHALL WRITE EACH RESULT TO ENDPOINT event-store
  OR RETRY BOUNDED 3 WITHIN 60s.

IF PARTY loader THROW EXCEPTION
  THEN PARTY loader SHALL SEND ERROR TO PARTY monitor
  THEN PARTY monitor SHALL SEND MESSAGE TO PARTY oncall.

NO PARTY SHALL WRITE ENDPOINT event-store
  EXCEPT PARTY loader
  PROVIDED_THAT PARTY loader AUTHENTICATE TO SERVICE auth.

PARTY monitor SHALL ADMINISTER PARTY ingester
  AND PARTY transformer
  AND PARTY loader.
```
11 sentences. 3 definitions. 2 preambles. 4 actors. Retry, timeout, error handling, authentication, authority. ADMINISTER and REQUIRE as verbs. Complete real-world ETL in the language.

---

## Sugar Comparison

The same sentences with and without sugar words. Both compile to identical graphs.

### Obligation (Example 1)

Without sugar:
```
PARTY system SHALL VALIDATE ALL PENDING RECORD.
```

With sugar:
```
THE PARTY system SHALL PLEASE VALIDATE ALL OF THE PENDING RECORD.
```

### Multi-party (Example 3)

Without sugar:
```
PARTY client SHALL REQUEST PARTY server.
PARTY server SHALL RESPOND PROMPTLY WITHIN 30s
  OR PARTY client MAY RETRY BOUNDED 3
  THEN HANDLE THE ERROR.
```

With sugar:
```
THE PARTY client SHALL REQUEST THE PARTY server.
THE PARTY server SHALL RESPOND PROMPTLY WITHIN 30s
  OR THE PARTY client MAY ALSO RETRY BOUNDED 3
  THEN ALSO HANDLE THE ERROR THAT HAS BEEN RECEIVED.
```

### Prohibition (Example 9)

Without sugar:
```
NO PARTY SHALL WRITE CONFIDENTIAL RESOURCE
  EXCEPT PARTY owner MAY WRITE CONFIDENTIAL RESOURCE
    PROVIDED_THAT PARTY owner AUTHENTICATE TO SERVICE auth.
```

With sugar:
```
NO PARTY SHALL WRITE CONFIDENTIAL RESOURCE
  EXCEPT THE PARTY owner, WHO MAY WRITE SUCH CONFIDENTIAL RESOURCE
    PROVIDED_THAT THE PARTY owner HAS BEEN AUTHENTICATED AT SERVICE auth.
```

### ETL Pipeline (Example 28, excerpt)

Without sugar:
```
PARTY monitor SHALL ADMINISTER PARTY ingester
  AND PARTY transformer AND PARTY loader.
```

With sugar:
```
THE PARTY monitor SHALL ADMINISTER THE PARTY ingester
  AND ALSO THE PARTY transformer AND ALSO THE PARTY loader.
```

Sugar makes the language read like natural English. The compiler ignores it. The graph is identical. Humans get readability. Machines get precision.

---

## Gaps Discovered

Testing these 30 examples produced:

| Finding | Count | Details |
|---|---|---|
| New words | 19 | TO, FROM, RESOURCE, OVERRIDE, AUTHENTICATE, AS, EXISTS, APPROVE, EXPIRE, BY, PRECEDENT, EQUALS, EXCEEDS, PRECEDES, ADMINISTER, NEST, CITE, REPLACE, AUGMENT |
| Reclassifications | 1 | THROW: Prohibit → Control |
| Grammar additions | 5 | definitions, noun lists, prep phrase conjunction, preambles, adverb-value pairs |
| Validation rules added | 2 | no double negation, pronoun scope |
| Rule revisions | 2 | Timing on all verbs, Artifacts as Control subjects |
| Verb-preposition separation | 6 | ADMINISTER/GOVERNS, NEST/CONTAINS, CITE/REFERENCES, REQUIRE/DEPENDS_ON, REPLACE/SUPERSEDES, AUGMENT/EXTENDS |
