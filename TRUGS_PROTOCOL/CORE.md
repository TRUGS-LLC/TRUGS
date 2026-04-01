# TRUGS CORE

**Version:** 0.9.1
**Status:** DRAFT — pre-release
**Purpose:** The universal foundation for all TRUGs

---

## What is TRUGS?

**TRUGS** — Traversable, Recursive, Universal, Graph, Specification — is a structured graph format for **data storage** and **inter-agent communication**.

A TRUG is a JSON document with a distinct structure that separates it from other computational languages. Agents read and write TRUGs to store structured information and to communicate it to other agents.

Examples:
- A project tracker where tasks, dependencies, and status persist across sessions and agents
- A protocol specification that multiple LLMs can read and validate
- A knowledge graph that one agent builds and another agent queries
- A shared plan that coordinates work between concurrent agents

---

## What is TRUGS_CORE (Core)?

Core is the specification that defines the boundaries every TRUG must satisfy, regardless of domain, purpose, or detail level, to give a standard of practice for all systems using TRUGS.

**Core is:**
- 7 boundaries that constrain structure
- 10 semantic primitive classes (~140 primitives)
- Composition rules (which primitives combine with which)
- 16 universal validation rules
- Domain-agnostic foundation

**CORE is NOT:**
- Domain-specific node type vocabularies (that's BRANCHES)
- Domain-specific property schemas (properties are open)
- Domain-specific transformation rules (transformations are free)
- A complete specification (CORE + BRANCH = complete)

---

## The Seven Boundaries

Every TRUG must satisfy these seven constraints:

### Boundary 1: Core Structure is Invariant

**Every node must have exactly 7 fields:**
```json
{
  "id": "string",
  "type": "string",
  "properties": {},
  "parent_id": "string | null",
  "contains": ["string"],
  "metric_level": "PREFIX_NAME",
  "dimension": "string"
}
```

**Every edge must have exactly 3 fields:**
```json
{
  "from_id": "string",
  "to_id": "string",
  "relation": "string"
}
```

**Why this matters:** Universal tooling. Any tool can read any TRUG.

---

### Boundary 2: Properties Are Open

**The `properties` object can contain anything:**
```json
{
  "properties": {
    "intent": "calculates factorial",
    "custom_field": "whatever you want",
    "experimental_data": [1, 2, 3],
    "ai_metadata": {"confidence": 0.95}
  }
}
```

**Rules:**
- Always an object (never null)
- Use `{}` for empty
- No predefined schema
- Any JSON-valid content

**Why this matters:** Experimentation is free. No Core updates needed for new ideas.

---

### Boundary 3: Dimensions Are Declared

**All dimensions must be declared at graph root:**
```json
{
  "dimensions": {
    "code_structure": {
      "description": "Code hierarchy",
      "base_level": "BASE"
    },
    "network_topology": {
      "description": "Infrastructure hierarchy",
      "base_level": "BASE"
    }
  }
}
```

**Rules:**
- Declare before use
- Nodes must reference declared dimensions
- Multiple dimensions allowed
- `description` required, `base_level` optional

**Why this matters:** Explicit hierarchies. Validation can check dimension references.

---

### Boundary 4: Hierarchy Is Explicit

**Parent-child relationships must be bidirectional:**

```json
{
  "nodes": [
    {
      "id": "parent",
      "contains": ["child"],
      "metric_level": "DEKA_MODULE"
    },
    {
      "id": "child",
      "parent_id": "parent",
      "metric_level": "BASE_FUNCTION"
    }
  ]
}
```

**Rules:**
- If `node.parent_id = "X"`, then `X.contains` must include `node.id`
- Parent `metric_level` ≥ child `metric_level` (same dimension)
- Parent and child must share dimension
- Roots have `parent_id: null`
- Leaves have `contains: []`

**Why this matters:** O(1) tree navigation. No hidden structure.

---

### Boundary 5: Edges Are Simple

**Edges connect nodes with named relations:**

```json
{
  "edges": [
    {
      "from_id": "func_a",
      "to_id": "func_b",
      "relation": "CALLS"
    }
  ]
}
```

**Rules:**
- `from_id` and `to_id` must reference existing nodes
- `relation` is any string (no predefined vocabulary)
- Edges can have optional `weight` (0.0-1.0) and `properties` object
- Edges don't affect hierarchy (separate from parent_id/contains)

**Why this matters:** Graph relationships across hierarchy. Extensible relation names.

---

### Boundary 6: Metric Prefixes Are Standard

**Metric levels use SI prefix format:**

```json
{
  "metric_level": "DEKA_MODULE"
}
```

**Format:** `{PREFIX}_{SEMANTIC_NAME}`

**21 Standard SI Prefixes:**

| Prefix | Value | Power | Common Use |
|--------|-------|-------|------------|
| YOTTA | 10²⁴ | 1e24 | Universal systems |
| ZETTA | 10²¹ | 1e21 | Galactic scale |
| EXA | 10¹⁸ | 1e18 | Planetary systems |
| PETA | 10¹⁵ | 1e15 | Global networks |
| TERA | 10¹² | 1e12 | Continental systems |
| GIGA | 10⁹ | 1e9 | National infrastructure |
| MEGA | 10⁶ | 1e6 | City-scale systems |
| KILO | 10³ | 1e3 | Large programs |
| HECTO | 10² | 1e2 | Program collections |
| DEKA | 10¹ | 1e1 | Packages, modules |
| **BASE** | **10⁰** | **1e0** | **Functions, classes (standard)** |
| DECI | 10⁻¹ | 1e-1 | Blocks, scopes |
| CENTI | 10⁻² | 1e-2 | Statements |
| MILLI | 10⁻³ | 1e-3 | Expressions |
| MICRO | 10⁻⁶ | 1e-6 | Operations, operands |
| NANO | 10⁻⁹ | 1e-9 | Registers, atoms |
| PICO | 10⁻¹² | 1e-12 | Bits, quantum states |
| FEMTO | 10⁻¹⁵ | 1e-15 | Sub-quantum |
| ATTO | 10⁻¹⁸ | 1e-18 | Theoretical |
| ZEPTO | 10⁻²¹ | 1e-21 | Mathematical |
| YOCTO | 10⁻²⁴ | 1e-24 | Abstraction |

**Rules:**
- PREFIX must be one of 21 standard SI prefixes
- SEMANTIC_NAME is free-form (domain-specific)
- Underscore required between prefix and name
- Comparison uses prefix numeric value

**Why this matters:** Error prevention. Can't typo `CENTI` like you can typo `0.01` vs `0.001`.

---

### Boundary 7: JSON Structure

**TRUGs are valid JSON:**

```json
{
  "name": "Valid TRUG",
  "version": "1.0.0",
  "type": "CODE",
  "dimensions": {},
  "capabilities": {},
  "nodes": [],
  "edges": []
}
```

**Rules:**
- Valid JSON syntax
- UTF-8 encoding
- Standard JSON types (string, number, boolean, null, array, object)
- File extension: `.json`

**Why this matters:** Universal tooling. Language agnostic. Diff-able in git.

---

## Required Node Fields

### 1. id (string)

**Purpose:** Unique identifier within graph

**Rules:**
- Must be unique across all nodes
- Any string format
- Stable across parses recommended

**Examples:**
```json
{"id": "func_add"}
{"id": "node_42"}
{"id": "chapter_1"}
```

---

### 2. type (string)

**Purpose:** Node classification from domain vocabulary

**Rules:**
- Any string value
- Domain-specific (CODE: FUNCTION, WEB: PAGE, WRITER: CHAPTER)
- Not validated by Core (Branch-specific)

**Examples:**
```json
{"type": "FUNCTION"}
{"type": "PAGE"}
{"type": "INTENT"}
{"type": "CUSTOM_NODE_TYPE"}
```

---

### 3. properties (object)

**Purpose:** Container for all node data

**Rules:**
- Always an object (never null)
- Use `{}` for empty
- No predefined schema
- Any JSON-valid content

**Examples:**
```json
{"properties": {}}

{"properties": {
  "function_name": "add",
  "parameters": ["a", "b"]
}}

{"properties": {
  "intent": "calculates factorial",
  "type_info": {"category": "function"},
  "custom_metadata": {"ai_generated": true}
}}
```

---

### 4. parent_id (string | null)

**Purpose:** Reference to parent node in hierarchy

**Rules:**
- `null` for root nodes
- String referencing existing node ID for children
- Must be consistent with parent's `contains` (bidirectional)

**Examples:**
```json
{"parent_id": null}
{"parent_id": "func_main"}
```

---

### 5. contains (array)

**Purpose:** List of child node IDs

**Rules:**
- Always an array
- `[]` for leaf nodes
- Contains strings referencing existing node IDs
- Must be consistent with children's `parent_id` (bidirectional)

**Examples:**
```json
{"contains": []}
{"contains": ["stmt_1", "stmt_2", "stmt_3"]}
```

---

### 6. metric_level (string)

**Purpose:** Position in hierarchy using metric prefix

**Format:** `{PREFIX}_{SEMANTIC_NAME}`

**Rules:**
- PREFIX must be one of 21 SI prefixes
- SEMANTIC_NAME is free-form
- Parent metric ≥ child metric (same dimension)

**Examples:**
```json
{"metric_level": "DEKA_MODULE"}
{"metric_level": "BASE_FUNCTION"}
{"metric_level": "CENTI_STATEMENT"}
{"metric_level": "MILLI_EXPRESSION"}
```

**Comparison:**
```python
METRIC_VALUES = {
    "DEKA": 1e1,   # 10
    "BASE": 1e0,   # 1
    "CENTI": 1e-2, # 0.01
    "MILLI": 1e-3  # 0.001
}

# Valid: parent ≥ child
DEKA (10) ≥ BASE (1) ✅
BASE (1) ≥ CENTI (0.01) ✅
CENTI (0.01) ≥ MILLI (0.001) ✅
```

---

### 7. dimension (string)

**Purpose:** Reference to declared dimension

**Rules:**
- Must reference dimension declared in graph root
- Parent and child must share dimension
- String identifier

**Examples:**
```json
{"dimension": "code_structure"}
{"dimension": "web_structure"}
{"dimension": "semantic_structure"}
```

---

## Required Edge Fields

### 1. from_id (string)

**Purpose:** Source node of relationship

**Rules:**
- Must reference existing node ID
- String identifier

---

### 2. to_id (string)

**Purpose:** Target node of relationship

**Rules:**
- Must reference existing node ID
- String identifier

---

### 3. relation (string)

**Purpose:** Type of relationship

**Rules:**
- Any string value
- Domain-specific (CODE: CALLS, WEB: LINKS_TO, WRITER: REFERENCES)
- Not validated by Core (Branch-specific)

**Examples:**
```json
{"relation": "CALLS"}
{"relation": "LINKS_TO"}
{"relation": "REFERENCES"}
{"relation": "CUSTOM_RELATION"}
```

---

## Optional Edge Fields

### weight (number, 0.0-1.0)

**Purpose:** Curator endorsement strength — how strongly the curator endorses this relationship (0.0 = not endorsed, 1.0 = fully endorsed). One field, one meaning, everywhere.

**Default:** If omitted, no weight (unendorsed — not the same as 0.0)

**Example:**
```json
{
  "from_id": "func_a",
  "to_id": "func_b",
  "relation": "CALLS",
  "weight": 0.85
}
```

---

### properties (object)

**Purpose:** Edge metadata

**Example:**
```json
{
  "from_id": "page_1",
  "to_id": "page_2",
  "relation": "LINKS_TO",
  "properties": {
    "link_text": "Next Page",
    "anchor": "#section-2"
  }
}
```

---

## Required Graph Fields

Every TRUG file must have this root structure:

```json
{
  "name": "string",
  "version": "1.0.0",
  "type": "string",
  "dimensions": {},
  "capabilities": {},
  "nodes": [],
  "edges": []
}
```

### name (string)

**Purpose:** Human-readable graph name

**Example:** `"Python Calculator Module"`

---

### version (string)

**Purpose:** TRUGS format version

**Value:** `"1.0.0"` for this specification

---

### type (string)

**Purpose:** Primary graph domain

**Common values:** `CODE`, `WEB`, `WRITER`, `KNOWLEDGE`, `ORCHESTRATION`

**Note:** Not validated by Core (informational)

---

### dimensions (object)

**Purpose:** Declare all dimensions used in graph

**Structure:**
```json
{
  "dimensions": {
    "dimension_name": {
      "description": "string",
      "base_level": "BASE"
    }
  }
}
```

**Rules:**
- At least one dimension required
- Each dimension needs `description`
- `base_level` optional (default: "BASE")

---

### capabilities (object)

**Purpose:** Declare extensions, vocabularies, profiles used

**Structure:**
```json
{
  "capabilities": {
    "extensions": ["typed"],
    "vocabularies": ["compute_v1"],
    "profiles": []
  }
}
```

**Rules:**
- All three fields required (can be empty arrays)
- Extensions referenced in node properties must be declared
- Vocabularies are informational
- Profiles are shorthand for common capability combinations

---

### nodes (array)

**Purpose:** Array of node objects

**Rules:**
- Each node must have all 7 required fields
- All node IDs must be unique

---

### edges (array)

**Purpose:** Array of edge objects

**Rules:**
- Each edge must have all 3 required fields
- All edge IDs must reference existing nodes

---

## Optional Graph Fields

### description (string)

Brief description of graph contents

### url (string)

Canonical URL if graph represents web content

### maintainer (string)

Contact information for graph maintainer

### updated (string)

ISO 8601 timestamp of last update

### meta (object)

Tool-specific metadata

---

## Validation Rules

Every TRUG must pass these 16 checks (rules 1-9 are structural; rules 10-16 are compositional and only enforced when `capabilities.vocabularies` includes `"core_v0.9.1"`):

### Rule 1: Node ID Uniqueness

All node IDs must be unique within graph.

```python
all_ids = [node['id'] for node in nodes]
assert len(all_ids) == len(set(all_ids))
```

**Error code:** `DUPLICATE_NODE_ID`

---

### Rule 2: Edge ID Validity

Edge `from_id` and `to_id` must reference existing nodes.

```python
node_ids = {node['id'] for node in nodes}
for edge in edges:
    assert edge['from_id'] in node_ids
    assert edge['to_id'] in node_ids
```

**Error code:** `INVALID_EDGE_REFERENCE`

---

### Rule 3: Hierarchy Consistency

Parent's `contains` must match children's `parent_id` (bidirectional).

```python
for node in nodes:
    if node['parent_id']:
        parent = find_node(node['parent_id'])
        assert node['id'] in parent['contains']
    
    for child_id in node['contains']:
        child = find_node(child_id)
        assert child['parent_id'] == node['id']
```

**Error code:** `INCONSISTENT_HIERARCHY`

---

### Rule 4: Metric Level Ordering

Parent metric level ≥ child metric level (same dimension).

```python
METRIC_VALUES = {
    "YOTTA": 1e24, "ZETTA": 1e21, "EXA": 1e18, "PETA": 1e15,
    "TERA": 1e12, "GIGA": 1e9, "MEGA": 1e6, "KILO": 1e3,
    "HECTO": 1e2, "DEKA": 1e1, "BASE": 1e0, "DECI": 1e-1,
    "CENTI": 1e-2, "MILLI": 1e-3, "MICRO": 1e-6, "NANO": 1e-9,
    "PICO": 1e-12, "FEMTO": 1e-15, "ATTO": 1e-18,
    "ZEPTO": 1e-21, "YOCTO": 1e-24
}

def parse_metric_level(level_name):
    prefix = level_name.split('_')[0]
    if prefix not in METRIC_VALUES:
        raise ValueError(f"Invalid metric prefix: {prefix}")
    return METRIC_VALUES[prefix]

for node in nodes:
    if node['parent_id']:
        parent = find_node(node['parent_id'])
        parent_val = parse_metric_level(parent['metric_level'])
        child_val = parse_metric_level(node['metric_level'])
        assert parent_val >= child_val
        assert parent['dimension'] == node['dimension']
```

**Error code:** `INVALID_METRIC_ORDERING`

---

### Rule 5: Dimension Declaration

All node dimensions must be declared in root `dimensions` object.

```python
declared_dims = set(dimensions.keys())
for node in nodes:
    assert node['dimension'] in declared_dims
```

**Error code:** `UNDECLARED_DIMENSION`

---

### Rule 6: Required Fields Present

All required fields must be present.

```python
# Nodes
for node in nodes:
    assert all(field in node for field in 
               ['id', 'type', 'properties', 'parent_id', 
                'contains', 'metric_level', 'dimension'])

# Edges
for edge in edges:
    assert all(field in edge for field in 
               ['from_id', 'to_id', 'relation'])

# Graph
assert all(field in graph for field in 
           ['name', 'version', 'type', 'dimensions', 
            'capabilities', 'nodes', 'edges'])
```

**Error code:** `MISSING_REQUIRED_FIELD`

---

### Rule 7: Field Type Correctness

Fields must have correct types.

```python
# Node types
assert isinstance(node['id'], str)
assert isinstance(node['type'], str)
assert isinstance(node['properties'], dict)
assert node['parent_id'] is None or isinstance(node['parent_id'], str)
assert isinstance(node['contains'], list)
assert isinstance(node['metric_level'], str)
assert isinstance(node['dimension'], str)

# Edge types
assert isinstance(edge['from_id'], str)
assert isinstance(edge['to_id'], str)
assert isinstance(edge['relation'], str)
```

**Error code:** `INVALID_FIELD_TYPE`

---

### Rule 8: Extension Declaration

Extensions used in node properties must be declared in `capabilities.extensions`.

```python
# Example: If any node has type_info
if any('type_info' in node['properties'] for node in nodes):
    assert 'typed' in graph['capabilities']['extensions']
```

**Error code:** `UNDECLARED_EXTENSION`

---

### Rule 9: Metric Level Format

`metric_level` must be format `{PREFIX}_{NAME}` where PREFIX is valid SI prefix.

```python
def validate_metric_level(level_name):
    parts = level_name.split('_')
    if len(parts) < 2:
        raise ValueError("Format must be {PREFIX}_{NAME}")
    prefix = parts[0]
    if prefix not in METRIC_VALUES:
        raise ValueError(f"Invalid metric prefix: {prefix}")
```

**Error code:** `INVALID_METRIC_FORMAT`

---

### Rule 10: Subject-Operation Compatibility

When a TRUG uses semantic primitives (core_v0.9.1), the subject entity of an operation must be compatible with the operation class.

| Subject Entity | Transform | Move | Obligate | Permit | Prohibit | Control | Bind | Resolve |
|---|---|---|---|---|---|---|---|---|
| Actor | yes | yes | yes | yes | yes | yes | yes | yes |
| Artifact | — | — | — | — | — | yes* | — | — |
| Container | yes | — | — | — | — | yes | yes | — |
| Boundary | — | — | — | — | — | — | yes | — |
| Outcome | — | — | — | — | — | — | — | — |

*Artifacts can only be subjects of comparison/existence Control operations: EXISTS, EQUALS, EXCEEDS, PRECEDES, EXPIRE.

**Error code:** `INCOMPATIBLE_SUBJECT_OPERATION`

---

### Rule 11: Operation-Object Compatibility

The target entity of an operation must be compatible with the operation class.

| Object Entity | Transform | Move | Obligate | Permit | Prohibit | Control | Bind | Resolve |
|---|---|---|---|---|---|---|---|---|
| Actor | — | — | — | yes | yes | — | — | — |
| Artifact | yes | yes | yes | — | — | yes | yes | — |
| Container | — | yes | — | — | — | — | yes | — |
| Boundary | — | — | — | — | — | — | yes | — |
| Outcome | — | — | — | — | — | — | — | yes |

**Error code:** `INCOMPATIBLE_OPERATION_OBJECT`

---

### Rule 12: Modifier-Entity Compatibility

Modifier primitives used as node properties must be compatible with the entity class.

| Modifier | Actor | Artifact | Container | Boundary | Outcome |
|---|---|---|---|---|---|
| Type | — | yes | — | — | yes |
| Access | — | yes | yes | yes | — |
| State | yes | yes | yes | yes | yes |
| Quantity | yes | yes | yes | — | yes |
| Priority | yes | yes | yes | yes | yes |

**Error code:** `INCOMPATIBLE_MODIFIER_ENTITY`

---

### Rule 13: Qualifier-Operation Compatibility

Qualifier primitives used as operation properties must be compatible with the operation class.

| Qualifier | Transform | Move | Obligate | Permit | Prohibit | Control | Bind | Resolve |
|---|---|---|---|---|---|---|---|---|
| Timing | yes | yes | yes | yes | yes | yes | — | yes |
| Repetition | yes | yes | yes | yes | yes | yes | — | yes |
| Degree | — | — | yes | yes | yes | — | yes | — |
| Condition | yes | yes | yes | yes | yes | yes | yes | yes |

**Error code:** `INCOMPATIBLE_QUALIFIER_OPERATION`

---

### Rule 14: Constraint-Subject Rule

Constraint primitives (SHALL, SHALL_NOT, MAY) require Actor entity subjects.

```python
if operation.constraint in ['SHALL', 'SHALL_NOT', 'MAY']:
    assert subject.entity_class == 'Actor'
```

**Error code:** `CONSTRAINT_REQUIRES_ACTOR`

---

### Rule 15: No Double Negation

A Negative selector (NO, NONE) and a Prohibit constraint (SHALL_NOT) cannot modify the same operation.

**Error code:** `DOUBLE_NEGATION`

---

### Rule 16: Reference Scope

Reference primitives (SELF, RESULT, OUTPUT, INPUT, SOURCE, TARGET) resolve within the same subgraph scope. Cross-scope references use Specific selectors (THE, THIS) with an entity type.

**Error code:** `UNRESOLVED_REFERENCE`

---

## Minimal Valid TRUG

The simplest TRUG that passes all validation rules:

```json
{
  "name": "Minimal Example",
  "version": "1.0.0",
  "type": "CODE",
  "dimensions": {
    "code_structure": {
      "description": "Code hierarchy",
      "base_level": "BASE"
    }
  },
  "capabilities": {
    "extensions": [],
    "vocabularies": [],
    "profiles": []
  },
  "nodes": [
    {
      "id": "root",
      "type": "MODULE",
      "properties": {},
      "parent_id": null,
      "contains": [],
      "metric_level": "DEKA_MODULE",
      "dimension": "code_structure"
    }
  ],
  "edges": []
}
```

**Why this is valid:**
- ✅ Has all required graph fields
- ✅ Declares dimension before use
- ✅ Single node has all 7 required fields
- ✅ Root node has `parent_id: null`
- ✅ Leaf node has `contains: []`
- ✅ No edges (empty array valid)
- ✅ Passes all 9 validation rules

---

## Complete Example

A function with proper hierarchy:

```json
{
  "name": "Add Function",
  "version": "1.0.0",
  "type": "CODE",
  "dimensions": {
    "code_structure": {
      "description": "Code hierarchy",
      "base_level": "BASE"
    }
  },
  "capabilities": {
    "extensions": [],
    "vocabularies": ["code_v1"],
    "profiles": []
  },
  "nodes": [
    {
      "id": "func_add",
      "type": "FUNCTION",
      "properties": {
        "function_name": "add",
        "parameters": ["a", "b"]
      },
      "parent_id": null,
      "contains": ["stmt_return"],
      "metric_level": "BASE_FUNCTION",
      "dimension": "code_structure"
    },
    {
      "id": "stmt_return",
      "type": "STATEMENT",
      "properties": {
        "statement_type": "return"
      },
      "parent_id": "func_add",
      "contains": ["expr_add"],
      "metric_level": "CENTI_STATEMENT",
      "dimension": "code_structure"
    },
    {
      "id": "expr_add",
      "type": "EXPRESSION",
      "properties": {
        "operation": "add"
      },
      "parent_id": "stmt_return",
      "contains": [],
      "metric_level": "MILLI_EXPRESSION",
      "dimension": "code_structure"
    }
  ],
  "edges": [
    {
      "from_id": "stmt_return",
      "to_id": "expr_add",
      "relation": "CONTAINS"
    }
  ]
}
```

**Hierarchy:**
```
func_add (BASE = 1)
  └─ stmt_return (CENTI = 0.01)
       └─ expr_add (MILLI = 0.001)
```

**Validation:**
- ✅ All IDs unique
- ✅ Edge references valid nodes
- ✅ Hierarchy consistent (bidirectional)
- ✅ Metric levels ordered (BASE ≥ CENTI ≥ MILLI)
- ✅ All nodes same dimension
- ✅ All 9 rules pass

---

## Multi-Dimensional Example

A system with code + infrastructure:

```json
{
  "name": "Distributed System",
  "version": "1.0.0",
  "type": "CODE",
  "dimensions": {
    "data_flow": {
      "description": "Data flow hierarchy",
      "base_level": "BASE"
    },
    "network_topology": {
      "description": "Infrastructure hierarchy",
      "base_level": "BASE"
    }
  },
  "capabilities": {
    "extensions": [],
    "vocabularies": ["compute_v1", "infrastructure_v1"],
    "profiles": []
  },
  "nodes": [
    {
      "id": "service_api",
      "type": "SERVICE",
      "properties": {"service_name": "api_gateway"},
      "parent_id": null,
      "contains": [],
      "metric_level": "BASE_SERVICE",
      "dimension": "data_flow"
    },
    {
      "id": "server_prod_01",
      "type": "SERVER",
      "properties": {"hostname": "prod-api-01"},
      "parent_id": null,
      "contains": [],
      "metric_level": "BASE_SERVER",
      "dimension": "network_topology"
    }
  ],
  "edges": [
    {
      "from_id": "service_api",
      "to_id": "server_prod_01",
      "relation": "DEPLOYED_ON",
      "properties": {"crosses_dimensions": true}
    }
  ]
}
```

**Key features:**
- Two dimensions (code + infrastructure)
- Two root nodes (different dimensions)
- Cross-dimensional edge (DEPLOYED_ON)
- Both nodes at BASE level in their dimensions

---

---

# Part 2: Semantic Primitives

CORE defines semantic primitives organized into 10 classes. These are the atoms of meaning. Every TRUG — regardless of domain — MAY use these primitives and MUST interpret them identically.

Every word belongs to exactly one class. There are no dual-class words.

| Class | Count | Purpose | Graph Element |
|---|---|---|---|
| Operation | 23 | Data transformations | TRANSFORM node `properties.operation` |
| Relation | 6 | Named connections between nodes | Edge `relation` |
| Entity | 8 | Typed things that exist | Node `type` |
| Constraint | 6 | Conditions that limit or obligate | Edge from PARTY to operation |
| Boundary | 3 | Structural containment and reference | Hierarchy and cross-reference edges |
| Modifier | 36 | Constraints on entities | Node `properties` |
| Qualifier | 19 | Constraints on operations | Operation node `properties` |
| Combinator | 13 | Graph structure control | Structural edges between subgraphs |
| Selector | 10 | Scope which entities an operation targets | Node query scope |
| Reference | 7 | Back-reference to established entities | Reference edges |

**Total: ~131 primitives** (precise count may shift as the language evolves).

For complete definitions of every primitive with source domain, subcategory, and formal definition, see **TRUGS_LANGUAGE/SPEC_vocabulary.md**.

---

## Class 1: Operation (23)

Operations describe data transformations. Each operation has exactly one meaning.

### Transform (14) — Change data shape

FILTER, EXCLUDE, MAP, SORT, MERGE, SPLIT, FLATTEN, AGGREGATE, GROUP, RENAME, BATCH, DISTINCT, TAKE, SKIP

### Move (10) — Move data between actors

READ, WRITE, SEND, RECEIVE, RETURN, REQUEST, RESPOND, AUTHENTICATE, DELIVER*, ASSIGN*

### Obligate (4) — Mandate behavior

VALIDATE, ASSERT, REQUIRE, SHALL*

### Permit (5) — Allow behavior

ALLOW, APPROVE, GRANT*, OVERRIDE*, MAY*

### Prohibit (3) — Forbid behavior

DENY, REJECT, SHALL_NOT*, REVOKE*

### Control (10) — Direct execution flow

BRANCH, MATCH, RETRY, TIMEOUT, THROW, EXISTS, EXPIRE, EQUALS, EXCEEDS, PRECEDES

### Bind (9) — Establish meaning or structural relationships

DEFINE, DECLARE, IMPLEMENT, NEST, AUGMENT, REPLACE, CITE*, ADMINISTER*, STIPULATE*

### Resolve (5) — Respond to failure

CATCH, HANDLE, RECOVER, CURE*, INDEMNIFY*

*Words marked with \* originate from law. All others from computation.*

---

## Class 2: Relation (6)

Relations are named connections between nodes. They appear as edge `relation` values.

| Relation | Intent | Scope |
|---|---|---|
| FEEDS | Data flows unconditionally from source to destination | Communication, Execution |
| ROUTES | Data flows conditionally based on predicate | Communication, Execution |
| BINDS | Schema constrains what a node accepts or produces | Storage, Communication, Execution |
| GOVERNS | One entity has authority over another | Communication |
| SUBJECT_TO | One thing is constrained by another | Communication |
| SUPERSEDES | One thing entirely replaces another | Storage, Communication |

---

## Class 3: Entity (8)

Entities are typed things that exist in the graph. They appear as node `type` values.

### Actor — Who performs actions

TRANSFORM, PARTY*, AGENT*, PRINCIPAL*

### Artifact — What is acted upon

DATA, RESOURCE, FILE, RECORD, MESSAGE, STREAM, INSTRUMENT*

### Container — What holds other things

PIPELINE, STAGE, MODULE, NAMESPACE

### Boundary — Where/when things apply

ENTRY (FLOW_ENTRY), EXIT (FLOW_EXIT), INTERFACE, ENDPOINT, JURISDICTION*

### Outcome — What comes out

RESULT, ERROR, EXCEPTION, REMEDY*

---

## Class 4: Constraint (6)

Constraints express normative statements about what parties must, must not, or may do.

| Constraint | Intent |
|---|---|
| SHALL | Obligation: party MUST perform action |
| SHALL_NOT | Prohibition: party MUST NOT perform action |
| MAY | Permission: party is allowed but not required |
| PRECEDENT | Prior decision that informs but doesn't bind |
| DEADLINE | Temporal bound by which obligation must be fulfilled |
| DEFINED_TERM | Word with specific formal meaning within context |

---

## Class 5: Boundary (3)

Boundaries affect hierarchy and structural reference.

| Boundary | Intent |
|---|---|
| CONTAINS | Hierarchical parent-child containment |
| REFERENCES | Non-hierarchical cross-reference |
| DEPENDS_ON | Functional requirement |

---

## Class 6: Modifier (36)

Modifiers constrain what an entity is or can do. They appear as node properties. When multiple modifiers stack, they follow fixed order: **Quantity > Priority > State > Access > Type**.

### Type (5) — What kind of thing

STRING, INTEGER, BOOLEAN, ARRAY, OBJECT

### Access (5) — Who can see/touch it

PUBLIC, PRIVATE, PROTECTED, READONLY, CONFIDENTIAL*

### State (14) — Current condition

VALID, INVALID, NULL, EMPTY, PENDING, ACTIVE, FAILED, MUTABLE, IMMUTABLE, BINDING*, VOID*, ENFORCEABLE*, EXPIRED*, PRECEDENT*

### Quantity (6) — How many / whether required

REQUIRED, OPTIONAL, UNIQUE, MULTIPLE, SOLE*, JOINT*

### Priority (6) — Relative importance

DEFAULT, CRITICAL, HIGH, LOW, MATERIAL*, SUBORDINATE*

---

## Class 7: Qualifier (19)

Qualifiers constrain how an operation executes. They appear as operation node properties. Each qualifier optionally carries a value (e.g., WITHIN 30s, BOUNDED 3).

### Timing (9) — When/how fast

ASYNC, SYNC, SEQUENTIAL, PARALLEL, IMMEDIATE, LAZY, PROMPTLY*, FORTHWITH*, WITHIN*

### Repetition (4) — How often

ONCE, ALWAYS, NEVER, BOUNDED

### Degree (4) — How precisely

STRICTLY, PARTIALLY, SUBSTANTIALLY*, REASONABLY*

### Condition (2) — Whether qualified

UNCONDITIONALLY*, CONDITIONALLY*

---

## Class 8: Combinator (13)

Combinators control graph structure — how subgraphs connect. They appear as structural edges between operation subgraphs.

### Sequence (2) — Ordered execution

THEN, FINALLY

### Parallel (1) — Simultaneous execution

AND

### Alternative (2) — Branching

OR, ELSE

### Cause (3) — Trigger or condition

IF, WHEN, WHILE

### Exception (5) — Override or carve-out

UNLESS*, EXCEPT*, NOTWITHSTANDING*, PROVIDED_THAT*, WHEREAS*

---

## Class 9: Selector (10)

Selectors scope which entities an operation targets. They appear as query scope on node references.

### Specific (2) — One identified instance

THE, THIS

### Universal (3) — Every instance

ALL, EACH, EVERY

### Existential (3) — At least one

ANY, SOME, A

### Negative (2) — Zero instances

NO, NONE

---

## Class 10: Reference (7)

References back-refer to previously established entities. They resolve within the same subgraph scope (see Rule 16).

| Reference | Intent |
|---|---|
| SELF | The current actor or scope |
| RESULT | The output of the most recent operation |
| OUTPUT | The data produced by a transform |
| INPUT | The data received by the current operation |
| SOURCE | The originating node of the current data |
| TARGET | The destination node of the current action |
| SAID* | The previously named entity (legal "the") |

---

## Verb-Preposition Separation

Where a concept has both an action form (operation) and a relationship form (relation/boundary), they are distinct words:

| Action (Operation) | Relationship (Relation/Boundary) |
|---|---|
| ADMINISTER | GOVERNS |
| NEST | CONTAINS |
| CITE | REFERENCES |
| REQUIRE | DEPENDS_ON |
| REPLACE | SUPERSEDES |
| AUGMENT | EXTENDS |

Every primitive belongs to exactly one class. No ambiguity.

---

# Part 3: Composition Rules

Composition rules define which primitives can combine with which. These are the type system for the graph. When `capabilities.vocabularies` includes `"core_v0.9.1"`, these rules are enforced as validation rules 10-16 (defined above in the Validation Rules section).

For the complete compatibility matrices, see:
- **Validation Rule 10:** Subject-Operation compatibility
- **Validation Rule 11:** Operation-Object compatibility
- **Validation Rule 12:** Modifier-Entity compatibility
- **Validation Rule 13:** Qualifier-Operation compatibility
- **Validation Rule 14:** Constraint-Subject rule (modals require Actor subjects)
- **Validation Rule 15:** No double negation
- **Validation Rule 16:** Reference scope

For full composition grammar (BNF) and detailed compatibility tables with subcategory breakdowns, see **TRUGS_LANGUAGE/SPEC_grammar.md**.

---

# Part 4: Opening TRUG

An **opening TRUG** is a TRUG that defines the vocabulary for a session or domain. It is the protocol-level mechanism for loading language definitions.

## Definition

An opening TRUG is a TRUG whose `type` is `"LANGUAGE"` or `"VOCABULARY"`. It contains:

| Node Type | Purpose |
|---|---|
| WORD | Every valid word, its class, subcategory, and exact definition |
| GRAMMAR_RULE | Composition rules — which classes combine with which |
| CONSTRAINT | Structural limits on the language |
| DOMAIN | Domain-specific vocabulary extensions |

## Loading Semantics

- CORE primitives are always available
- The opening TRUG adds domain-specific extensions
- The opening TRUG itself must validate against CORE
- Different opening TRUGs = different vocabularies, same grammar

## Self-Description

The opening TRUG pattern is recursive: the TRUGS Language definition is itself a TRUG (`TRUGS_LANGUAGE/language.trug.json`). The language that describes TRUGs is a TRUG.

---

## What CORE Does NOT Define

**CORE does not specify:**

### Node Type Vocabularies

- `FUNCTION`, `PAGE`, `CHAPTER` are branch-specific
- Any string value valid at Core level
- See BRANCHES.md for domain vocabularies

### Edge Relation Vocabularies

- `CALLS`, `LINKS_TO`, `REFERENCES` are Branch-specific
- Any string value valid at Core level
- See BRANCHES.md for domain vocabularies

### Property Schemas

- Property names are domain-specific
- Property structures are open-ended
- Extensions are opt-in
- See BRANCHES.md for conventions

### Semantic Meanings

- What `FUNCTION` means (that's Python branch)
- What `BASE_FUNCTION` means semantically (that's domain)
- What transformations do (that's tools)

---

## Example: Constraints File

The following is an example of how TRUGS can be used for storage and communication. A **Constraints file** is a TRUG that declares the constraints governing a repository, project, or system.

```json
{
  "name": "Repository Constraints",
  "version": "1.0.0",
  "type": "CONSTRAINTS",
  "dimensions": {
    "constraint_structure": {
      "description": "Constraint hierarchy",
      "base_level": "BASE"
    }
  },
  "capabilities": {
    "extensions": [],
    "vocabularies": [],
    "profiles": []
  },
  "nodes": [
    {
      "id": "root",
      "type": "CONSTRAINT_SET",
      "properties": {
        "name": "Project Constraints",
        "scope": "repository"
      },
      "parent_id": null,
      "contains": ["constraint_branching"],
      "metric_level": "DEKA_SET",
      "dimension": "constraint_structure"
    },
    {
      "id": "constraint_branching",
      "type": "CONSTRAINT",
      "properties": {
        "name": "All changes use branches",
        "description": "No commits directly to the default branch"
      },
      "parent_id": "root",
      "contains": [],
      "metric_level": "BASE_CONSTRAINT",
      "dimension": "constraint_structure"
    }
  ],
  "edges": []
}
```

---

## Reference Implementation

The canonical Core validator is in `trugs_tools`:

```bash
# Validate CORE compliance
python -m trugs_tools.validate my_graph.json

# Check specific rules
python -m trugs_tools.validate --core-only my_graph.json
```

**Source:** `packages/trugs/src/trugs/core/`  
**Test coverage:** 193 tests, 80% coverage

---

## Summary

**The 7 Boundaries:**
1. Core structure invariant (7 node fields, 3 edge fields)
2. Properties open (any content)
3. Dimensions declared (explicit)
4. Hierarchy explicit (bidirectional)
5. Edges simple (node to node)
6. Metric prefixes standard (21 SI prefixes)
7. JSON structure (valid JSON)

**The 10 Primitive Classes:**
1. Operation (23) — data transformations
2. Relation (6) — named connections
3. Entity (8+) — typed things
4. Constraint (6) — obligations and permissions
5. Boundary (3) — hierarchy and reference
6. Modifier (36) — constraints on entities
7. Qualifier (19) — constraints on operations
8. Combinator (13) — graph structure control
9. Selector (10) — query scope
10. Reference (7) — back-references

**The 16 Validation Rules:**
- Rules 1-9: structural (always enforced)
- Rules 10-16: compositional (enforced when core_v0.9.1 declared)

**What this enables:**
- Universal validation (16 mechanical rules)
- Domain flexibility (open properties)
- Multi-aspect modeling (multiple dimensions)
- Composition type system (which primitives combine with which)
- Opening TRUG pattern (loadable language definitions)
- Tool composability (any tool respects boundaries)

**What's NOT in CORE:**
- Domain-specific node type vocabularies (BRANCHES)
- Domain-specific edge relation vocabularies (BRANCHES)
- Domain-specific property schemas (open-ended)
- Domain-specific transformation rules (free within boundaries)

**Next steps:**
- Read TRUGS_LANGUAGE/ to understand the formal language built on these primitives
- Read BRANCHES.md to learn domain vocabularies
- See EXAMPLES/ for working TRUGs

---

**TRUGS Core v0.9.1 — The universal foundation**

---

## Appendix A: Definitions

| Term | Definition |
|------|------------|
| **TRUGS** | Traversable, Recursive, Universal, Graph, Specification. The specification and standard. When all letters are capitalized, TRUGS refers to the specification itself. |
| **TRUG** | A single JSON document conforming to the TRUGS specification. |
| **TRUGs** | Multiple TRUG documents. In this document, distinguished from TRUGS (the specification) by the lowercase 's'. In common usage, TRUGS may refer to either the specification or multiple documents — context determines meaning. |
| **CORE** | Short for TRUGS CORE. This specification — the structural boundaries, semantic primitives, composition rules, and validation rules that every TRUG must satisfy. |
| **Branch** | A domain-specific vocabulary layered on top of CORE. CORE + Branch = complete TRUG. |
| **Node** | A graph element representing a thing. Has 7 required fields. |
| **Edge** | A graph element representing a relationship between two nodes. Has 3 required fields. |
| **Dimension** | A declared axis of hierarchy within a TRUG. Nodes belong to exactly one dimension. |
| **Metric level** | A node's position in its dimension's hierarchy, expressed as an SI prefix and a semantic name. |
| **Hierarchy** | The parent-child containment tree within a dimension. Expressed via `parent_id` and `contains`. Separate from edges. |
| **Properties** | An open JSON object on nodes and edges. No predefined schema — any JSON-valid content allowed. |
| **Capabilities** | A graph-level declaration of extensions, vocabularies, and profiles in use. |
| **Extension** | An opt-in feature declared in capabilities. Must be declared before use in node properties. |
| **Vocabulary** | An informational declaration of the domain-specific type and relation names a TRUG uses. |
| **Profile** | A shorthand for a common combination of capabilities. |
| **Weight** | An optional edge field (0.0–1.0) expressing curator endorsement strength for a relationship. |
| **Curator** | The human or agent responsible for authoring and maintaining a TRUG. |
| **SI prefix** | One of 21 standard metric prefixes (YOTTA through YOCTO) used in metric levels to express hierarchical position. |
| **Graph** | The root-level JSON structure of a TRUG, containing name, version, type, dimensions, capabilities, nodes, and edges. |
| **Opening TRUG** | A TRUG that defines the vocabulary for a session or domain. Type is LANGUAGE or VOCABULARY. |
| **Semantic primitive** | An atom of meaning defined by CORE. Organized into 10 classes. |
| **Composition rule** | A type rule defining which primitives can combine with which. Validation rules 10-16. |
| **Boundary** | A structural constraint that CORE enforces. There are 7 boundaries. |
| **Validation rule** | A mechanical check that a TRUG must pass. There are 16 rules (9 structural, 7 compositional). |
