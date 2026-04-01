# TRUGS Glossary

> Alphabetical reference of all terminology in the TRUGS v0.9.1 specification: protocol concepts, semantic primitives, language grammar, node/edge fields, branch vocabularies, and tools.

---

**ACTIVE** — Modifier (State). Currently in use or executing.

**ADMINISTER** — Operation (Bind). Establish and exercise authority over. Verb form of the GOVERNS relation.

**AGENT** — Entity (Actor). An entity authorized to act on behalf of another. From law.

**AGGREGATE** — Operation (Transform). Reduce a collection to a single value using an accumulator function. CORE primitive.

**ALL** — Selector (Universal). Every instance without exception.

**ALLOW** — Operation (Permit). Permit an action without mandating it.

**AND** — Combinator (Parallel). Execute both clauses; both must succeed.

**ANY** — Selector (Existential). At least one; whichever satisfies.

**APPROVE** — Operation (Permit). Accept as satisfying criteria; opposite of REJECT.

**ARRAY** — Modifier (Type). Ordered collection data type.

**AS** — Preposition (Binding). Binds an identifier to a type or role.

**ASSERT** — Operation (Obligate). Declare a condition that must be true.

**ASSIGN** — Operation (Move). Transfer rights or obligations to another party. From law.

**ASYNC** — Qualifier (Timing). Execute without blocking the caller.

**AUGMENT** — Operation (Bind). Add capability to an existing thing. Verb form of the EXTENDS relation.

**AUTHENTICATE** — Operation (Move). Prove identity to another actor.

**BATCH** — Operation (Transform). Group items into fixed-size chunks. CORE primitive.

**BINDS** — Relation. Schema constrains what a node accepts or produces. CORE primitive.

**BOOLEAN** — Modifier (Type). True/false data type.

**BOUNDED** — Qualifier (Repetition). Execute up to N times (requires integer).

**Boundary** — One of the 7 structural constraints CORE enforces on every TRUG.

**Branch** — A domain-specific vocabulary layered on top of CORE. CORE + Branch = complete TRUG.

**BRANCH** — Operation (Control). Route to one of two paths on boolean condition. CORE primitive.

**BY** — Preposition (Binding). Specifies the key, criterion, or basis for an operation.

**CATCH** — Operation (Resolve). Intercept an error and enter recovery.

**CITE** — Operation (Bind). Formally refer to another entity. Verb form of the REFERENCES relation.

**Combinator** — Semantic primitive class (Class 8). Controls graph structure — how subgraphs connect. 13 primitives.

**Composition rules** — Type rules defining which primitives can combine with which. Validation rules 10-16.

**CONDITIONALLY** — Qualifier (Condition). Only if a stated prerequisite is met. From law.

**CONFIDENTIAL** — Modifier (Access). Restricted to authorized parties only. From law.

**Constraint** — Semantic primitive class (Class 4). Conditions that limit or obligate. 6 primitives.

**CONTAINS** — Boundary. Hierarchical parent-child containment. CORE primitive.

**CORE** — The universal foundation for all TRUGs. Defines 7 boundaries, 10 semantic primitive classes, 16 validation rules, and composition rules.

**CRITICAL** — Modifier (Priority). Failure is unrecoverable.

**CURE** — Operation (Resolve). Correct a breach within allowed time. From law.

**DATA** — Entity (Artifact). A typed value: input, output, or intermediate state. CORE primitive.

**DEADLINE** — Constraint. Temporal bound by which obligation must be fulfilled. CORE primitive.

**DECLARE** — Operation (Bind). State a fact or create a named thing.

**DEFAULT** — Modifier (Priority). The value used when none is specified.

**DEFINED_TERM** — Constraint. Word with specific formal meaning within context. CORE primitive.

**DEFINE** — Operation (Bind). Establish the meaning of a term.

**DELIVER** — Operation (Move). Transfer possession of an artifact to another party. From law.

**DENY** — Operation (Prohibit). Refuse a requested action.

**DEPENDS_ON** — Boundary. Functional requirement — one thing requires another. CORE primitive.

**Dimension** — A declared axis of hierarchy within a TRUG. Nodes belong to exactly one dimension.

**DISTINCT** — Operation (Transform). Remove duplicates. CORE primitive.

**EACH** — Selector (Universal). Every instance, considered individually.

**Edge** — A graph element representing a relationship between two nodes. Has 3 required fields: from_id, to_id, relation.

**ELSE** — Combinator (Alternative). Execute only when preceding condition is false.

**EMPTY** — Modifier (State). Present but containing nothing.

**ENDPOINT** — Entity (Boundary). A named, addressable point of interaction.

**ENFORCEABLE** — Modifier (State). Can be compelled by remedy. From law.

**Entity** — Semantic primitive class (Class 3). Typed things that exist in the graph. 5 subcategories: Actor, Artifact, Container, Boundary, Outcome.

**ENTRY** — Entity (Boundary). The point where data enters a scope. CORE primitive (FLOW_ENTRY).

**EQUALS** — Operation (Control). Evaluates true if left and right values are identical.

**ERROR** — Entity (Outcome). A named failure condition with a cause.

**EVERY** — Selector (Universal). Every instance (synonym of ALL).

**EXCEPT** — Combinator (Exception). Everything applies other than the stated carve-out. From law.

**EXCEPTION** — Entity (Outcome). An error that interrupts normal flow.

**EXCEEDS** — Operation (Control). Evaluates true if left value is greater than right.

**EXCLUDE** — Operation (Transform). Remove items satisfying a predicate. CORE primitive.

**EXISTS** — Operation (Control). Evaluates true if the noun is present and non-null.

**EXIT** — Entity (Boundary). The point where data leaves a scope. CORE primitive (FLOW_EXIT).

**EXPIRE** — Operation (Control). Transition to EXPIRED state; deadline passed.

**EXPIRED** — Modifier (State). Past its deadline; no longer in effect. From law.

**EXTENDS** — Relation (Dependency). Source adds capability to target.

**FAILED** — Modifier (State). Terminated with error.

**FEEDS** — Relation. Data flows unconditionally from source to destination. CORE primitive.

**FILE** — Entity (Artifact). A named, persistent byte sequence.

**FILTER** — Operation (Transform). Select items satisfying a predicate. CORE primitive.

**FINALLY** — Combinator (Sequence). Execute regardless of success or failure.

**FLATTEN** — Operation (Transform). Collapse one level of nesting. CORE primitive.

**FORTHWITH** — Qualifier (Timing). Immediately and without any delay. From law.

**FROM** — Preposition (Flow). Directional: data originates at source.

**FUNCTION** — Entity (Actor). A callable unit that accepts input and returns output.

**GOVERNS** — Relation (Authority). One entity has authority over another. CORE primitive.

**GRANT** — Operation (Permit). Confer a right or permission to another party. From law.

**Graph** — The root-level JSON structure of a TRUG, containing name, version, type, dimensions, capabilities, nodes, and edges.

**GROUP** — Operation (Transform). Partition collection by key. CORE primitive.

**HANDLE** — Operation (Resolve). Process an error condition.

**HIGH** — Modifier (Priority). Elevated importance.

**Hierarchy** — The parent-child containment tree within a dimension. Expressed via parent_id and contains[].

**IF** — Combinator (Cause). Execute following clause only when condition is true.

**IMMEDIATE** — Qualifier (Timing). Execute with no delay.

**IMMUTABLE** — Modifier (State). Cannot be changed after creation.

**IMPLEMENT** — Operation (Bind). Fulfill the contract of an interface.

**INDEMNIFY** — Operation (Resolve). Compensate for loss caused by breach. From law.

**INPUT** — Reference (Source). The data received by the current operation.

**INSTRUMENT** — Entity (Artifact). A formal document that creates or records rights. From law.

**INTEGER** — Modifier (Type). Whole number data type.

**INTERFACE** — Entity (Boundary). A contract defining what operations a thing exposes.

**INVALID** — Modifier (State). Fails one or more declared constraints.

**JOINT** — Modifier (Quantity). Shared equally among multiple parties. From law.

**JURISDICTION** — Entity (Boundary). The scope within which authority is valid. From law.

**LAZY** — Qualifier (Timing). Defer execution until the result is needed.

**LOW** — Modifier (Priority). Reduced importance.

**MAP** — Operation (Transform). Transform each item independently. CORE primitive.

**MATCH** — Operation (Control). Route to one of N paths on pattern. CORE primitive.

**MATERIAL** — Modifier (Priority). Significant enough to affect decisions. From law.

**MAY** — Constraint / Modal. Permission: party is allowed but not required. CORE primitive.

**MERGE** — Operation (Transform). Combine multiple collections into one. CORE primitive.

**MESSAGE** — Entity (Artifact). A discrete unit of communication between actors.

**Metric level** — A node's position in its dimension's hierarchy, expressed as PREFIX_NAME using SI prefixes.

**Modal** — A verb (SHALL, SHALL_NOT, MAY) that modifies another verb to establish obligation, permission, or prohibition. Requires Actor subject.

**Modifier** — Semantic primitive class (Class 6). Constrains what an entity is or can do. 36 primitives in 5 subcategories: Type, Access, State, Quantity, Priority.

**MODULE** — Entity (Container). A self-contained unit of related functionality.

**MULTIPLE** — Modifier (Quantity). More than one instance may exist.

**MUTABLE** — Modifier (State). Can be changed after creation.

**NAMESPACE** — Entity (Container). A named scope that prevents identifier collision.

**NEST** — Operation (Bind). Place one thing structurally inside another. Verb form of the CONTAINS relation.

**NEVER** — Qualifier (Repetition). Do not execute under any condition.

**NO** — Selector (Negative). Zero instances.

**Node** — A graph element representing a thing. Has 7 required fields: id, type, properties, parent_id, contains, metric_level, dimension.

**NONE** — Selector (Negative). Zero instances (used without following noun).

**NOTWITHSTANDING** — Combinator (Exception). Overrides any conflicting clause. From law.

**NULL** — Modifier (State). Absent; no value.

**OBJECT** — Modifier (Type). Key-value structure data type.

**ON_BEHALF_OF** — Preposition (Authority). Acting with delegated authority for another. From law.

**ONCE** — Qualifier (Repetition). Execute exactly one time.

**Opening TRUG** — A TRUG that defines the vocabulary for a session or domain. Type is LANGUAGE or VOCABULARY. Loaded at the start of an LLM conversation.

**Operation** — Semantic primitive class (Class 1). Data transformations. 23 CORE primitives in 8 subcategories: Transform, Move, Obligate, Permit, Prohibit, Control, Bind, Resolve.

**OPTIONAL** — Modifier (Quantity). May be absent; absence is acceptable.

**OR** — Combinator (Alternative). Execute alternative if first fails or is false.

**OUTPUT** — Reference (Result). The data produced by a transform.

**OVERRIDE** — Operation (Permit). Supersede a constraint or prohibition for this action. From law.

**PARALLEL** — Qualifier (Timing). Execute steps simultaneously.

**PARTIALLY** — Qualifier (Degree). Affecting some but not all items.

**PARTY** — Entity (Actor). A bound entity capable of obligations and permissions. CORE primitive. From law.

**PENDING** — Modifier (State). Created but not yet processed.

**PIPELINE** — Entity (Container). A container of ordered operations data flows through. CORE primitive.

**PRECEDES** — Operation (Control). Evaluates true if left value is less than right.

**PRECEDENT** — Modifier (State) / Constraint. Informing but not binding; advisory based on prior decision. CORE primitive.

**PRINCIPAL** — Entity (Actor). The entity on whose behalf an agent acts. From law.

**PRIVATE** — Modifier (Access). Accessible only to the owning actor.

**PROCESS** — Entity (Actor). An executing unit of work with its own state.

**PROMPTLY** — Qualifier (Timing). Within a reasonable time, without unnecessary delay. From law.

**PROTECTED** — Modifier (Access). Accessible to the owning actor and its children.

**PROVIDED_THAT** — Combinator (Exception). Clause applies only if the stated condition is met. From law.

**PUBLIC** — Modifier (Access). Accessible to any actor.

**PURSUANT_TO** — Preposition (Authority). In accordance with; as directed by. From law.

**Qualifier** — Semantic primitive class (Class 7). Constrains how an operation executes. 19 primitives in 4 subcategories: Timing, Repetition, Degree, Condition.

**READ** — Operation (Move). Input data from external source. CORE primitive.

**READONLY** — Modifier (Access). Can be read but not written.

**REASONABLY** — Qualifier (Degree). As a competent party would under the circumstances. From law.

**RECEIVE** — Operation (Move). Accept data from another actor.

**RECORD** — Entity (Artifact). A single structured data item with named fields.

**RECOVER** — Operation (Resolve). Restore normal operation after failure.

**Reference** — Semantic primitive class (Class 10). Back-reference to established entities. 7 primitives.

**REFERENCES** — Boundary. Non-hierarchical cross-reference. CORE primitive.

**REJECT** — Operation (Prohibit). Refuse input that does not meet criteria.

**Relation** — Semantic primitive class (Class 2). Named connections between nodes. 6 CORE primitives.

**REMEDY** — Entity (Outcome). The consequence when an obligation is breached. CORE primitive. From law.

**RENAME** — Operation (Transform). Change field names without changing values. CORE primitive.

**REPLACE** — Operation (Bind). Entirely substitute one thing for another. Verb form of the SUPERSEDES relation.

**REQUEST** — Operation (Move). Send message expecting a response. CORE primitive.

**REQUIRE** — Operation (Obligate). Declare a hard prerequisite. Verb form of the DEPENDS_ON relation.

**REQUIRED** — Modifier (Quantity). Must be present; absence is an error.

**RESOURCE** — Entity (Artifact). A managed asset: file, service, endpoint, or data store.

**RESPOND** — Operation (Move). Reply to a prior request. CORE primitive.

**RESULT** — Reference (Result). The output of the most recent operation.

**RETRY** — Operation (Control). Re-attempt failed operation up to bounded count. CORE primitive.

**RETURN** — Operation (Move). Emit final output and terminate.

**RETURNS_TO** — Preposition (Flow). Output flows back to a previous node.

**REVOKE** — Operation (Prohibit). Withdraw a previously granted right or permission. From law.

**ROUTES** — Relation. Data flows conditionally based on predicate. CORE primitive.

**SAID** — Reference (Legal). The previously named entity. From law.

**Selector** — Semantic primitive class (Class 9). Scopes which entities an operation targets. 10 primitives in 4 subcategories: Specific, Universal, Existential, Negative.

**SELF** — Reference (Self). The current actor or scope.

**SEND** — Operation (Move). Transmit data to another actor.

**SEQUENTIAL** — Qualifier (Timing). Execute steps one after another in order.

**SERVICE** — Entity (Actor). A long-lived process that accepts requests.

**SHALL** — Constraint / Modal. Obligation: party MUST perform action. CORE primitive. From law.

**SHALL_NOT** — Constraint / Modal. Prohibition: party MUST NOT perform action. CORE primitive. From law.

**SI prefix** — One of 21 standard metric prefixes (YOTTA through YOCTO) used in metric levels.

**SKIP** — Operation (Transform). Bypass first N items. CORE primitive.

**SOLE** — Modifier (Quantity). One and only one; no others permitted. From law.

**SOME** — Selector (Existential). One or more, unspecified which.

**SORT** — Operation (Transform). Order items by comparison function. CORE primitive.

**SOURCE** — Reference (Source). The originating node of the current data.

**SPLIT** — Operation (Transform). Divide one collection into multiple. CORE primitive.

**STAGE** — Entity (Container). A logical grouping of transforms within a pipeline. CORE primitive.

**STIPULATE** — Operation (Bind). Establish a binding agreed-upon condition. From law.

**STREAM** — Entity (Artifact). An ordered, potentially unbounded sequence of data items.

**STRICTLY** — Qualifier (Degree). With zero tolerance for deviation.

**STRING** — Modifier (Type). Text data type.

**SUBJECT_TO** — Relation (Dependency). One thing is constrained by another. CORE primitive. From law.

**SUBORDINATE** — Modifier (Priority). Lower in authority hierarchy. From law.

**SUBSTANTIALLY** — Qualifier (Degree). In all material respects; minor deviations tolerated. From law.

**SUPERSEDES** — Relation (Replacement). One thing entirely replaces another. CORE primitive.

**SYNC** — Qualifier (Timing). Execute and block until complete.

**TAKE** — Operation (Transform). Return first N items. CORE primitive.

**TARGET** — Reference (Target). The destination node of the current action.

**THE** — Selector (Specific). One specific, previously identified instance.

**THEN** — Combinator (Sequence). Execute next step after current completes.

**THIS** — Selector (Specific). The instance in current scope.

**THROW** — Operation (Control). Generate an error condition; directs flow to error handler.

**TIMEOUT** — Operation (Control). Bound wall-clock time for an operation. CORE primitive.

**TO** — Preposition (Flow). Directional: data moves toward destination.

**TRANSFORM** — Entity (Actor). A node that performs exactly one operation. CORE primitive.

**TRUG** — A single JSON document conforming to the TRUGS specification.

**TRUGS** — Traceable Recursive Universal Graph Specification. The protocol and format for representing structured information as directed graphs.

**TRUGS Language** — A formalized subset of English (190 executable words + 24 sugar words from computation and law) where every valid sentence compiles to a TRUG graph and every graph decompiles back to a sentence.

**UNCONDITIONALLY** — Qualifier (Condition). Without any prerequisite or qualification. From law.

**UNIQUE** — Modifier (Quantity). Exactly one instance may exist.

**UNLESS** — Combinator (Exception). Clause does not apply if exception condition is met. From law.

**VALID** — Modifier (State). Satisfies all declared constraints.

**Validation rule** — A mechanical check that a TRUG must pass. 16 rules: 9 structural (always enforced), 7 compositional (enforced when core_v0.9.1 declared).

**VALIDATE** — Operation (Obligate). Assert data satisfies condition; halt if not. CORE primitive.

**VOID** — Modifier (State). Without legal effect; as if it never existed. From law.

**WHEN** — Combinator (Cause). Execute following clause upon event occurrence.

**WHEREAS** — Combinator (Exception). Establishes factual context for what follows; preamble only. From law.

**WHILE** — Combinator (Cause). Continue executing as long as condition holds.

**WITHIN** — Qualifier (Timing). Before the specified duration elapses (requires duration). From law.

**WRITE** — Operation (Move). Output data to external destination. CORE primitive.

---

*214 glossary entries covering the complete TRUGS v0.9.1 specification: semantic primitives, protocol concepts, language grammar, and tools.*
