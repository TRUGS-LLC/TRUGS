# TRUGS Validation

**Version:** 1.0.0 (AAA_AARDVARK)
**Status:** ✅ Stable
**Purpose:** Complete validation rules with executable implementations

---

## Overview

**What gets validated:** CORE structure only (7 node fields, 3 edge fields, hierarchy rules)

**What doesn't get validated:**
- Node `type` vocabularies (branch-specific)
- Property schemas (properties are open)
- Domain-specific rules (branch validation)

**When to validate:**
- Before loading graph into memory
- After modifications
- In CI/CD pipelines
- Before graph operations

**How to validate:** Mechanical checks - no semantic interpretation required

---

## The 9 Core Validation Rules

All TRUGs must pass these checks to be considered valid.

---

### Rule 1: Node ID Uniqueness

**What it checks:** All node IDs must be unique within the graph

**Why it matters:** Node IDs are references - duplicates cause ambiguity

**Python code:**
```python
def validate_unique_ids(nodes: list) -> list[str]:
    """Check that all node IDs are unique.

    Returns:
        List of error messages (empty if valid)
    """
    errors = []
    node_ids = []

    for node in nodes:
        node_id = node.get('id')
        if node_id in node_ids:
            errors.append(f"Duplicate node ID: '{node_id}'")
        node_ids.append(node_id)

    return errors
```

**Error code:** `DUPLICATE_NODE_ID`

**Example invalid TRUG:**
```json
{
  "nodes": [
    {"id": "func_1", "type": "FUNCTION"},
    {"id": "func_1", "type": "FUNCTION"}
  ]
}
```
❌ **Error:** `Duplicate node ID: 'func_1'`

**Example valid TRUG:**
```json
{
  "nodes": [
    {"id": "func_1", "type": "FUNCTION"},
    {"id": "func_2", "type": "FUNCTION"}
  ]
}
```
✅ **Valid:** All IDs unique

---

### Rule 2: Edge ID Validity

**What it checks:** Edge `from_id` and `to_id` must reference existing nodes

**Why it matters:** Dangling references cause runtime errors

**Python code:**
```python
def validate_edge_references(nodes: list, edges: list) -> list[str]:
    """Check that all edges reference existing nodes.

    Returns:
        List of error messages (empty if valid)
    """
    errors = []
    node_ids = {node['id'] for node in nodes}

    for i, edge in enumerate(edges):
        from_id = edge.get('from_id')
        to_id = edge.get('to_id')

        if from_id not in node_ids:
            errors.append(
                f"Edge {i}: from_id '{from_id}' references non-existent node"
            )
        if to_id not in node_ids:
            errors.append(
                f"Edge {i}: to_id '{to_id}' references non-existent node"
            )

    return errors
```

**Error code:** `INVALID_EDGE_REFERENCE`

**Example invalid TRUG:**
```json
{
  "nodes": [
    {"id": "func_1", "type": "FUNCTION"}
  ],
  "edges": [
    {"from_id": "func_1", "to_id": "func_MISSING", "relation": "CALLS"}
  ]
}
```
❌ **Error:** `Edge 0: to_id 'func_MISSING' references non-existent node`

**Example valid TRUG:**
```json
{
  "nodes": [
    {"id": "func_1", "type": "FUNCTION"},
    {"id": "func_2", "type": "FUNCTION"}
  ],
  "edges": [
    {"from_id": "func_1", "to_id": "func_2", "relation": "CALLS"}
  ]
}
```
✅ **Valid:** All edge references exist

---

### Rule 3: Hierarchy Consistency

**What it checks:** Parent's `contains` must match children's `parent_id` (bidirectional)

**Why it matters:** Ensures O(1) tree navigation in both directions

**Python code:**
```python
def validate_hierarchy_consistency(nodes: list) -> list[str]:
    """Check bidirectional parent-child consistency.

    Returns:
        List of error messages (empty if valid)
    """
    errors = []
    nodes_by_id = {n['id']: n for n in nodes}

    for node in nodes:
        node_id = node.get('id')
        parent_id = node.get('parent_id')
        contains = node.get('contains', [])

        # Rule 3a: If node has parent, parent must list it in contains[]
        if parent_id is not None:
            if parent_id not in nodes_by_id:
                errors.append(
                    f"Node '{node_id}': parent_id '{parent_id}' references non-existent node"
                )
            else:
                parent = nodes_by_id[parent_id]
                parent_contains = parent.get('contains', [])
                if node_id not in parent_contains:
                    errors.append(
                        f"Node '{node_id}': parent '{parent_id}' doesn't list it in contains[]"
                    )

        # Rule 3b: Every child in contains[] must have this node as parent
        for child_id in contains:
            if child_id not in nodes_by_id:
                errors.append(
                    f"Node '{node_id}': contains[] references non-existent node '{child_id}'"
                )
            else:
                child = nodes_by_id[child_id]
                child_parent_id = child.get('parent_id')
                if child_parent_id != node_id:
                    errors.append(
                        f"Node '{node_id}': child '{child_id}' has wrong parent_id "
                        f"(expected '{node_id}', got '{child_parent_id}')"
                    )

    return errors
```

**Error code:** `INCONSISTENT_HIERARCHY`

**Example invalid TRUG:**
```json
{
  "nodes": [
    {
      "id": "module_1",
      "parent_id": null,
      "contains": ["func_1"]
    },
    {
      "id": "func_1",
      "parent_id": "module_1",
      "contains": []
    },
    {
      "id": "func_2",
      "parent_id": "module_1",
      "contains": []
    }
  ]
}
```
❌ **Error:** `Node 'func_2': parent 'module_1' doesn't list it in contains[]`

**Example valid TRUG:**
```json
{
  "nodes": [
    {
      "id": "module_1",
      "parent_id": null,
      "contains": ["func_1", "func_2"]
    },
    {
      "id": "func_1",
      "parent_id": "module_1",
      "contains": []
    },
    {
      "id": "func_2",
      "parent_id": "module_1",
      "contains": []
    }
  ]
}
```
✅ **Valid:** All parent-child references are bidirectional

---

### Rule 4: Metric Level Ordering

**What it checks:** Parent metric level ≥ child metric level (within same dimension)

**Why it matters:** Enforces hierarchical ordering using numeric comparison

**Python code:**
```python
METRIC_VALUES = {
    "YOTTA": 1e24, "ZETTA": 1e21, "EXA": 1e18, "PETA": 1e15,
    "TERA": 1e12, "GIGA": 1e9, "MEGA": 1e6, "KILO": 1e3,
    "HECTO": 1e2, "DEKA": 1e1, "BASE": 1e0, "DECI": 1e-1,
    "CENTI": 1e-2, "MILLI": 1e-3, "MICRO": 1e-6, "NANO": 1e-9,
    "PICO": 1e-12, "FEMTO": 1e-15, "ATTO": 1e-18,
    "ZEPTO": 1e-21, "YOCTO": 1e-24
}

def parse_metric_level(level_name: str) -> float:
    """Parse metric level to numeric value.

    Args:
        level_name: Format {PREFIX}_{SEMANTIC} (e.g., "BASE_FUNCTION")

    Returns:
        Numeric value of prefix

    Raises:
        ValueError: If prefix is invalid
    """
    parts = level_name.split('_', 1)
    if len(parts) < 2:
        raise ValueError(f"Invalid format: '{level_name}' (expected PREFIX_NAME)")

    prefix = parts[0]
    if prefix not in METRIC_VALUES:
        raise ValueError(f"Invalid metric prefix: '{prefix}'")

    return METRIC_VALUES[prefix]

def validate_metric_ordering(nodes: list) -> list[str]:
    """Check parent metric ≥ child metric within same dimension.

    Returns:
        List of error messages (empty if valid)
    """
    errors = []
    nodes_by_id = {n['id']: n for n in nodes}

    for node in nodes:
        node_id = node.get('id')
        parent_id = node.get('parent_id')

        if parent_id and parent_id in nodes_by_id:
            parent = nodes_by_id[parent_id]

            # Only check if same dimension
            if parent.get('dimension') == node.get('dimension'):
                try:
                    parent_val = parse_metric_level(parent['metric_level'])
                    child_val = parse_metric_level(node['metric_level'])

                    if parent_val < child_val:
                        errors.append(
                            f"Node '{node_id}': child metric_level "
                            f"({node['metric_level']} = {child_val}) "
                            f"exceeds parent metric_level "
                            f"({parent['metric_level']} = {parent_val})"
                        )
                except ValueError as e:
                    # Will be caught by Rule 9
                    pass

    return errors
```

**Error code:** `INVALID_METRIC_ORDERING`

**Example invalid TRUG:**
```json
{
  "nodes": [
    {
      "id": "stmt_1",
      "parent_id": null,
      "metric_level": "CENTI_STATEMENT",
      "dimension": "code_structure"
    },
    {
      "id": "func_1",
      "parent_id": "stmt_1",
      "metric_level": "BASE_FUNCTION",
      "dimension": "code_structure"
    }
  ]
}
```
❌ **Error:** `Node 'func_1': child metric_level (BASE_FUNCTION = 1.0) exceeds parent metric_level (CENTI_STATEMENT = 0.01)`

**Example valid TRUG:**
```json
{
  "nodes": [
    {
      "id": "func_1",
      "parent_id": null,
      "metric_level": "BASE_FUNCTION",
      "dimension": "code_structure"
    },
    {
      "id": "stmt_1",
      "parent_id": "func_1",
      "metric_level": "CENTI_STATEMENT",
      "dimension": "code_structure"
    }
  ]
}
```
✅ **Valid:** BASE (1.0) ≥ CENTI (0.01)

---

### Rule 5: Dimension Declaration

**What it checks:** All node dimensions must be declared in root `dimensions` object

**Why it matters:** Explicit declaration prevents typos and enables validation

**Python code:**
```python
def validate_dimension_declarations(graph: dict) -> list[str]:
    """Check all node dimensions are declared.

    Returns:
        List of error messages (empty if valid)
    """
    errors = []
    declared_dims = set(graph.get('dimensions', {}).keys())

    for node in graph.get('nodes', []):
        node_id = node.get('id')
        dimension = node.get('dimension')

        if dimension and dimension not in declared_dims:
            errors.append(
                f"Node '{node_id}': dimension '{dimension}' not declared in root dimensions"
            )

    return errors
```

**Error code:** `UNDECLARED_DIMENSION`

**Example invalid TRUG:**
```json
{
  "dimensions": {
    "code_structure": {"description": "Code hierarchy"}
  },
  "nodes": [
    {
      "id": "page_1",
      "dimension": "web_structure"
    }
  ]
}
```
❌ **Error:** `Node 'page_1': dimension 'web_structure' not declared in root dimensions`

**Example valid TRUG:**
```json
{
  "dimensions": {
    "code_structure": {"description": "Code hierarchy"},
    "web_structure": {"description": "Web hierarchy"}
  },
  "nodes": [
    {
      "id": "page_1",
      "dimension": "web_structure"
    }
  ]
}
```
✅ **Valid:** All dimensions declared

---

### Rule 6: Required Fields Present

**What it checks:** All required fields must be present in nodes, edges, and graph root

**Why it matters:** Missing fields cause runtime errors

**Python code:**
```python
def validate_required_fields(graph: dict) -> list[str]:
    """Check all required fields are present.

    Returns:
        List of error messages (empty if valid)
    """
    errors = []

    # Required graph root fields
    root_fields = ['name', 'version', 'type', 'dimensions', 'capabilities', 'nodes', 'edges']
    for field in root_fields:
        if field not in graph:
            errors.append(f"Graph root: missing required field '{field}'")

    # Required node fields
    node_fields = ['id', 'type', 'properties', 'parent_id', 'contains', 'metric_level', 'dimension']
    for i, node in enumerate(graph.get('nodes', [])):
        for field in node_fields:
            if field not in node:
                node_id = node.get('id', f'<node {i}>')
                errors.append(f"Node '{node_id}': missing required field '{field}'")

    # Required edge fields
    edge_fields = ['from_id', 'to_id', 'relation']
    for i, edge in enumerate(graph.get('edges', [])):
        for field in edge_fields:
            if field not in edge:
                errors.append(f"Edge {i}: missing required field '{field}'")

    return errors
```

**Error code:** `MISSING_REQUIRED_FIELD`

**Example invalid TRUG:**
```json
{
  "nodes": [
    {
      "id": "func_1",
      "type": "FUNCTION"
    }
  ]
}
```
❌ **Error:** `Node 'func_1': missing required field 'properties'`
❌ **Error:** `Node 'func_1': missing required field 'parent_id'`
❌ **Error:** `Node 'func_1': missing required field 'contains'`
(etc.)

**Example valid TRUG:**
```json
{
  "name": "Example",
  "version": "1.0.0",
  "type": "CODE",
  "dimensions": {},
  "capabilities": {},
  "nodes": [
    {
      "id": "func_1",
      "type": "FUNCTION",
      "properties": {},
      "parent_id": null,
      "contains": [],
      "metric_level": "BASE_FUNCTION",
      "dimension": "code_structure"
    }
  ],
  "edges": []
}
```
✅ **Valid:** All required fields present

---

### Rule 7: Field Type Correctness

**What it checks:** Fields must have correct JSON types

**Why it matters:** Type mismatches cause parse errors

**Python code:**
```python
def validate_field_types(graph: dict) -> list[str]:
    """Check all fields have correct types.

    Returns:
        List of error messages (empty if valid)
    """
    errors = []

    # Check root types
    if 'name' in graph and not isinstance(graph['name'], str):
        errors.append(f"Graph 'name' must be string (got {type(graph['name']).__name__})")
    if 'version' in graph and not isinstance(graph['version'], str):
        errors.append(f"Graph 'version' must be string (got {type(graph['version']).__name__})")
    if 'type' in graph and not isinstance(graph['type'], str):
        errors.append(f"Graph 'type' must be string (got {type(graph['type']).__name__})")
    if 'dimensions' in graph and not isinstance(graph['dimensions'], dict):
        errors.append(f"Graph 'dimensions' must be object (got {type(graph['dimensions']).__name__})")
    if 'nodes' in graph and not isinstance(graph['nodes'], list):
        errors.append(f"Graph 'nodes' must be array (got {type(graph['nodes']).__name__})")
    if 'edges' in graph and not isinstance(graph['edges'], list):
        errors.append(f"Graph 'edges' must be array (got {type(graph['edges']).__name__})")

    # Check node types
    for node in graph.get('nodes', []):
        node_id = node.get('id', '<unknown>')

        if 'id' in node and not isinstance(node['id'], str):
            errors.append(f"Node '{node_id}': 'id' must be string")
        if 'type' in node and not isinstance(node['type'], str):
            errors.append(f"Node '{node_id}': 'type' must be string")
        if 'properties' in node and not isinstance(node['properties'], dict):
            errors.append(f"Node '{node_id}': 'properties' must be object")
        if 'parent_id' in node and node['parent_id'] is not None and not isinstance(node['parent_id'], str):
            errors.append(f"Node '{node_id}': 'parent_id' must be string or null")
        if 'contains' in node and not isinstance(node['contains'], list):
            errors.append(f"Node '{node_id}': 'contains' must be array")
        if 'metric_level' in node and not isinstance(node['metric_level'], str):
            errors.append(f"Node '{node_id}': 'metric_level' must be string")
        if 'dimension' in node and not isinstance(node['dimension'], str):
            errors.append(f"Node '{node_id}': 'dimension' must be string")

    # Check edge types
    for i, edge in enumerate(graph.get('edges', [])):
        if 'from_id' in edge and not isinstance(edge['from_id'], str):
            errors.append(f"Edge {i}: 'from_id' must be string")
        if 'to_id' in edge and not isinstance(edge['to_id'], str):
            errors.append(f"Edge {i}: 'to_id' must be string")
        if 'relation' in edge and not isinstance(edge['relation'], str):
            errors.append(f"Edge {i}: 'relation' must be string")

    return errors
```

**Error code:** `INVALID_FIELD_TYPE`

**Example invalid TRUG:**
```json
{
  "nodes": [
    {
      "id": "func_1",
      "type": "FUNCTION",
      "properties": [],
      "parent_id": null,
      "contains": [],
      "metric_level": "BASE_FUNCTION",
      "dimension": "code_structure"
    }
  ]
}
```
❌ **Error:** `Node 'func_1': 'properties' must be object`

**Example valid TRUG:**
```json
{
  "nodes": [
    {
      "id": "func_1",
      "type": "FUNCTION",
      "properties": {},
      "parent_id": null,
      "contains": [],
      "metric_level": "BASE_FUNCTION",
      "dimension": "code_structure"
    }
  ]
}
```
✅ **Valid:** All fields have correct types

---

### Rule 8: Extension Declaration

**What it checks:** Extensions used in node properties must be declared in `capabilities.extensions`

**Why it matters:** Explicit declaration enables validation and compatibility checking

**Python code:**
```python
# Known extension-specific property keys
EXTENSION_PROPERTIES = {
    'typed': ['type_info'],
    'scoped': ['scope_id']
}

def validate_extension_declarations(graph: dict) -> list[str]:
    """Check extensions are declared before use.

    Returns:
        List of error messages (empty if valid)
    """
    errors = []
    declared_extensions = set(graph.get('capabilities', {}).get('extensions', []))

    for node in graph.get('nodes', []):
        node_id = node.get('id', '<unknown>')
        properties = node.get('properties', {})

        # Check for known extension properties
        for ext_name, prop_keys in EXTENSION_PROPERTIES.items():
            for prop_key in prop_keys:
                if prop_key in properties:
                    if ext_name not in declared_extensions:
                        errors.append(
                            f"Node '{node_id}': uses extension property '{prop_key}' "
                            f"but extension '{ext_name}' not declared in capabilities.extensions"
                        )

    return errors
```

**Error code:** `UNDECLARED_EXTENSION`

**Example invalid TRUG:**
```json
{
  "capabilities": {
    "extensions": []
  },
  "nodes": [
    {
      "id": "func_1",
      "properties": {
        "type_info": {"category": "function"}
      }
    }
  ]
}
```
❌ **Error:** `Node 'func_1': uses extension property 'type_info' but extension 'typed' not declared`

**Example valid TRUG:**
```json
{
  "capabilities": {
    "extensions": ["typed"]
  },
  "nodes": [
    {
      "id": "func_1",
      "properties": {
        "type_info": {"category": "function"}
      }
    }
  ]
}
```
✅ **Valid:** Extension declared before use

---

### Rule 9: Metric Level Format

**What it checks:** `metric_level` must be format `{PREFIX}_{NAME}` where PREFIX is valid SI prefix

**Why it matters:** Standardized format enables parsing and comparison

**Python code:**
```python
def validate_metric_format(nodes: list) -> list[str]:
    """Check metric_level format is PREFIX_NAME.

    Returns:
        List of error messages (empty if valid)
    """
    errors = []
    valid_prefixes = set(METRIC_VALUES.keys())

    for node in nodes:
        node_id = node.get('id', '<unknown>')
        metric_level = node.get('metric_level')

        if not metric_level:
            continue

        # Check format
        parts = metric_level.split('_', 1)
        if len(parts) < 2:
            errors.append(
                f"Node '{node_id}': metric_level '{metric_level}' "
                f"must be format PREFIX_NAME (missing underscore)"
            )
            continue

        prefix = parts[0]
        semantic = parts[1]

        # Check prefix validity
        if prefix not in valid_prefixes:
            errors.append(
                f"Node '{node_id}': invalid metric prefix '{prefix}' "
                f"(must be one of {sorted(valid_prefixes)})"
            )

        # Check semantic name not empty
        if not semantic:
            errors.append(
                f"Node '{node_id}': metric_level '{metric_level}' "
                f"has empty semantic name"
            )

    return errors
```

**Error code:** `INVALID_METRIC_FORMAT`

**Example invalid TRUG:**
```json
{
  "nodes": [
    {
      "id": "func_1",
      "metric_level": "INVALID_FUNCTION"
    }
  ]
}
```
❌ **Error:** `Node 'func_1': invalid metric prefix 'INVALID'`

**Example valid TRUG:**
```json
{
  "nodes": [
    {
      "id": "func_1",
      "metric_level": "BASE_FUNCTION"
    }
  ]
}
```
✅ **Valid:** BASE is valid SI prefix

---

## Complete Validator Implementation

**Full Python validator class with all 9 rules:**

```python
"""TRUGS v1.0.0 Validator - Complete Reference Implementation"""

from typing import Dict, List, Set


# Metric prefix values (Rule 4 and Rule 9)
METRIC_VALUES = {
    "YOTTA": 1e24, "ZETTA": 1e21, "EXA": 1e18, "PETA": 1e15,
    "TERA": 1e12, "GIGA": 1e9, "MEGA": 1e6, "KILO": 1e3,
    "HECTO": 1e2, "DEKA": 1e1, "BASE": 1e0, "DECI": 1e-1,
    "CENTI": 1e-2, "MILLI": 1e-3, "MICRO": 1e-6, "NANO": 1e-9,
    "PICO": 1e-12, "FEMTO": 1e-15, "ATTO": 1e-18,
    "ZEPTO": 1e-21, "YOCTO": 1e-24
}

# Extension property mappings (Rule 8)
EXTENSION_PROPERTIES = {
    'typed': ['type_info'],
    'scoped': ['scope_id']
}


class ValidationError(Exception):
    """TRUG validation error"""
    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message
        super().__init__(f"[{code}] {message}")


class TrugValidator:
    """Complete TRUGS v1.0.0 validator"""

    def __init__(self, graph: dict):
        self.graph = graph
        self.errors: List[Dict[str, str]] = []

    def validate(self) -> bool:
        """Run all 9 validation rules.

        Returns:
            True if valid, False if errors found
        """
        self.errors = []

        # Rule 1: Node ID Uniqueness
        self._validate_unique_ids()

        # Rule 2: Edge ID Validity
        self._validate_edge_references()

        # Rule 3: Hierarchy Consistency
        self._validate_hierarchy_consistency()

        # Rule 4: Metric Level Ordering
        self._validate_metric_ordering()

        # Rule 5: Dimension Declaration
        self._validate_dimension_declarations()

        # Rule 6: Required Fields Present
        self._validate_required_fields()

        # Rule 7: Field Type Correctness
        self._validate_field_types()

        # Rule 8: Extension Declaration
        self._validate_extension_declarations()

        # Rule 9: Metric Level Format
        self._validate_metric_format()

        return len(self.errors) == 0

    def _add_error(self, code: str, message: str):
        """Add validation error"""
        self.errors.append({"code": code, "message": message})

    def _validate_unique_ids(self):
        """Rule 1: Node ID Uniqueness"""
        node_ids = []
        for node in self.graph.get('nodes', []):
            node_id = node.get('id')
            if node_id in node_ids:
                self._add_error('DUPLICATE_NODE_ID', f"Duplicate node ID: '{node_id}'")
            node_ids.append(node_id)

    def _validate_edge_references(self):
        """Rule 2: Edge ID Validity"""
        node_ids = {node['id'] for node in self.graph.get('nodes', [])}

        for i, edge in enumerate(self.graph.get('edges', [])):
            from_id = edge.get('from_id')
            to_id = edge.get('to_id')

            if from_id not in node_ids:
                self._add_error('INVALID_EDGE_REFERENCE',
                    f"Edge {i}: from_id '{from_id}' references non-existent node")
            if to_id not in node_ids:
                self._add_error('INVALID_EDGE_REFERENCE',
                    f"Edge {i}: to_id '{to_id}' references non-existent node")

    def _validate_hierarchy_consistency(self):
        """Rule 3: Hierarchy Consistency"""
        nodes_by_id = {n['id']: n for n in self.graph.get('nodes', [])}

        for node in self.graph.get('nodes', []):
            node_id = node.get('id')
            parent_id = node.get('parent_id')
            contains = node.get('contains', [])

            # Check parent reference
            if parent_id is not None:
                if parent_id not in nodes_by_id:
                    self._add_error('INCONSISTENT_HIERARCHY',
                        f"Node '{node_id}': parent_id '{parent_id}' references non-existent node")
                else:
                    parent = nodes_by_id[parent_id]
                    if node_id not in parent.get('contains', []):
                        self._add_error('INCONSISTENT_HIERARCHY',
                            f"Node '{node_id}': parent '{parent_id}' doesn't list it in contains[]")

            # Check child references
            for child_id in contains:
                if child_id not in nodes_by_id:
                    self._add_error('INCONSISTENT_HIERARCHY',
                        f"Node '{node_id}': contains[] references non-existent node '{child_id}'")
                else:
                    child = nodes_by_id[child_id]
                    if child.get('parent_id') != node_id:
                        self._add_error('INCONSISTENT_HIERARCHY',
                            f"Node '{node_id}': child '{child_id}' has wrong parent_id")

    def _validate_metric_ordering(self):
        """Rule 4: Metric Level Ordering"""
        nodes_by_id = {n['id']: n for n in self.graph.get('nodes', [])}

        for node in self.graph.get('nodes', []):
            node_id = node.get('id')
            parent_id = node.get('parent_id')

            if parent_id and parent_id in nodes_by_id:
                parent = nodes_by_id[parent_id]

                if parent.get('dimension') == node.get('dimension'):
                    try:
                        parent_val = self._parse_metric_level(parent['metric_level'])
                        child_val = self._parse_metric_level(node['metric_level'])

                        if parent_val < child_val:
                            self._add_error('INVALID_METRIC_ORDERING',
                                f"Node '{node_id}': child metric exceeds parent metric")
                    except ValueError:
                        pass  # Caught by Rule 9

    def _validate_dimension_declarations(self):
        """Rule 5: Dimension Declaration"""
        declared_dims = set(self.graph.get('dimensions', {}).keys())

        for node in self.graph.get('nodes', []):
            node_id = node.get('id')
            dimension = node.get('dimension')

            if dimension and dimension not in declared_dims:
                self._add_error('UNDECLARED_DIMENSION',
                    f"Node '{node_id}': dimension '{dimension}' not declared")

    def _validate_required_fields(self):
        """Rule 6: Required Fields Present"""
        # Root fields
        root_fields = ['name', 'version', 'type', 'dimensions', 'capabilities', 'nodes', 'edges']
        for field in root_fields:
            if field not in self.graph:
                self._add_error('MISSING_REQUIRED_FIELD',
                    f"Graph root: missing required field '{field}'")

        # Node fields
        node_fields = ['id', 'type', 'properties', 'parent_id', 'contains', 'metric_level', 'dimension']
        for node in self.graph.get('nodes', []):
            node_id = node.get('id', '<unknown>')
            for field in node_fields:
                if field not in node:
                    self._add_error('MISSING_REQUIRED_FIELD',
                        f"Node '{node_id}': missing required field '{field}'")

        # Edge fields
        edge_fields = ['from_id', 'to_id', 'relation']
        for i, edge in enumerate(self.graph.get('edges', [])):
            for field in edge_fields:
                if field not in edge:
                    self._add_error('MISSING_REQUIRED_FIELD',
                        f"Edge {i}: missing required field '{field}'")

    def _validate_field_types(self):
        """Rule 7: Field Type Correctness"""
        # Check root types
        if 'name' in self.graph and not isinstance(self.graph['name'], str):
            self._add_error('INVALID_FIELD_TYPE', "Graph 'name' must be string")
        if 'version' in self.graph and not isinstance(self.graph['version'], str):
            self._add_error('INVALID_FIELD_TYPE', "Graph 'version' must be string")

        # Check node types
        for node in self.graph.get('nodes', []):
            node_id = node.get('id', '<unknown>')

            if 'id' in node and not isinstance(node['id'], str):
                self._add_error('INVALID_FIELD_TYPE', f"Node '{node_id}': 'id' must be string")
            if 'properties' in node and not isinstance(node['properties'], dict):
                self._add_error('INVALID_FIELD_TYPE', f"Node '{node_id}': 'properties' must be object")
            if 'contains' in node and not isinstance(node['contains'], list):
                self._add_error('INVALID_FIELD_TYPE', f"Node '{node_id}': 'contains' must be array")

    def _validate_extension_declarations(self):
        """Rule 8: Extension Declaration"""
        declared = set(self.graph.get('capabilities', {}).get('extensions', []))

        for node in self.graph.get('nodes', []):
            node_id = node.get('id', '<unknown>')
            props = node.get('properties', {})

            for ext_name, prop_keys in EXTENSION_PROPERTIES.items():
                for prop_key in prop_keys:
                    if prop_key in props and ext_name not in declared:
                        self._add_error('UNDECLARED_EXTENSION',
                            f"Node '{node_id}': extension '{ext_name}' not declared")

    def _validate_metric_format(self):
        """Rule 9: Metric Level Format"""
        for node in self.graph.get('nodes', []):
            node_id = node.get('id', '<unknown>')
            metric_level = node.get('metric_level')

            if not metric_level:
                continue

            parts = metric_level.split('_', 1)
            if len(parts) < 2:
                self._add_error('INVALID_METRIC_FORMAT',
                    f"Node '{node_id}': metric_level must be PREFIX_NAME")
                continue

            prefix = parts[0]
            if prefix not in METRIC_VALUES:
                self._add_error('INVALID_METRIC_FORMAT',
                    f"Node '{node_id}': invalid metric prefix '{prefix}'")

    def _parse_metric_level(self, level_name: str) -> float:
        """Parse metric level to numeric value"""
        prefix = level_name.split('_')[0]
        if prefix not in METRIC_VALUES:
            raise ValueError(f"Invalid prefix: {prefix}")
        return METRIC_VALUES[prefix]

    def get_errors(self) -> List[Dict[str, str]]:
        """Get all validation errors"""
        return self.errors

    def print_errors(self):
        """Print all validation errors"""
        if not self.errors:
            print("✅ Valid TRUG - all 9 rules passed")
            return

        print(f"❌ Invalid TRUG - {len(self.errors)} error(s) found:")
        for error in self.errors:
            print(f"  [{error['code']}] {error['message']}")


# Usage example
if __name__ == "__main__":
    import json

    # Example: Validate a TRUG file
    with open('graph.json', 'r') as f:
        graph = json.load(f)

    validator = TrugValidator(graph)
    if validator.validate():
        print("✅ Valid TRUG")
    else:
        validator.print_errors()
```

---

## Error Code Reference

| Code | Rule | Description |
|------|------|-------------|
| `DUPLICATE_NODE_ID` | 1 | Node ID appears multiple times |
| `INVALID_EDGE_REFERENCE` | 2 | Edge references non-existent node |
| `INCONSISTENT_HIERARCHY` | 3 | parent_id and contains[] don't match |
| `INVALID_METRIC_ORDERING` | 4 | Child metric > parent metric |
| `UNDECLARED_DIMENSION` | 5 | Node uses undeclared dimension |
| `MISSING_REQUIRED_FIELD` | 6 | Required field absent |
| `INVALID_FIELD_TYPE` | 7 | Field has wrong JSON type |
| `UNDECLARED_EXTENSION` | 8 | Extension used but not declared |
| `INVALID_METRIC_FORMAT` | 9 | metric_level format wrong or invalid prefix |

---

## Complete Valid Example

**Minimal TRUG passing all 9 rules:**

```json
{
  "name": "Valid Example",
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
      "id": "module_main",
      "type": "MODULE",
      "properties": {"module_name": "main"},
      "parent_id": null,
      "contains": ["func_init"],
      "metric_level": "DEKA_MODULE",
      "dimension": "code_structure"
    },
    {
      "id": "func_init",
      "type": "FUNCTION",
      "properties": {"function_name": "init"},
      "parent_id": "module_main",
      "contains": [],
      "metric_level": "BASE_FUNCTION",
      "dimension": "code_structure"
    }
  ],
  "edges": []
}
```

**Why this is valid:**
- ✅ Rule 1: All IDs unique (`module_main`, `func_init`)
- ✅ Rule 2: No edges (empty array valid)
- ✅ Rule 3: `func_init` parent is `module_main`, which contains `func_init`
- ✅ Rule 4: DEKA (10) ≥ BASE (1) in same dimension
- ✅ Rule 5: `code_structure` declared in root
- ✅ Rule 6: All required fields present
- ✅ Rule 7: All fields have correct types
- ✅ Rule 8: No extensions used
- ✅ Rule 9: `DEKA_MODULE` and `BASE_FUNCTION` have valid format

---

## Command Line Usage

**Install validator:**
```bash
pip install trugs-tools
```

**Validate a TRUG file:**
```bash
trugs-validate graph.json
```

**Verbose output (show all checks):**
```bash
trugs-validate -v graph.json
```

**Quiet mode (CI/CD):**
```bash
trugs-validate -q graph.json
```

**Exit codes:**
- `0`: Valid TRUG
- `1`: Invalid TRUG

---

## Integration with Other Tools

### Python

```python
from trugs_tools.validator import TrugValidator

validator = TrugValidator(graph)
if validator.validate():
    # Process graph
    pass
else:
    for error in validator.get_errors():
        print(f"{error['code']}: {error['message']}")
```

### CI/CD (GitHub Actions)

```yaml
- name: Validate TRUG
  run: |
    pip install trugs-tools
    trugs-validate graph.json
```

### Pre-commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit

for file in $(git diff --cached --name-only --diff-filter=ACM | grep '\.json$'); do
    trugs-validate "$file" || exit 1
done
```

---

## See Also

- [CORE.md](CORE.md) - The 7 boundaries and field definitions
- [BRANCHES.md](BRANCHES.md) - Domain-specific vocabularies
- [SPEC_patterns.md](SPEC_patterns.md) - System patterns using validated TRUGs
- [REFERENCE_communication.md](REFERENCE_communication.md) - JSON/JSONL/Pydantic standards

---

**TRUGS Validation v1.0.0 (AAA_AARDVARK)**
