# TRUGS Schema Reference

**Version:** 1.0.0 (AAA_AARDVARK)
**Status:** ✅ Stable
**Purpose:** Complete schema definitions for all TRUG components

---

## Overview

This document provides the complete schema reference for TRUGS v1.0, including:

1. **Core Schema** - Universal structure all TRUGs must follow
2. **Branch Schemas** - Domain-specific property conventions
3. **Extension Schemas** - Optional capability property structures
4. **Complete Examples** - Working TRUGs for each domain

**Key Principle:** CORE defines structure, BRANCHES define vocabulary, EXTENSIONS add capabilities.

---

## Table of Contents

1. [Core Schema](#core-schema)
2. [Branch Schemas](#branch-schemas)
   - [Web Branch](#web-branch-schema)
   - [Writer Branch](#writer-branch-schema)
3. [Extension Schemas](#extension-schemas)
   - [typed Extension](#typed-extension-schema)
   - [scoped Extension](#scoped-extension-schema)
   - [ownership Extension](#ownership-extension-schema)
4. [Complete Examples](#complete-examples)
5. [Schema Validation](#schema-validation)

---

# Core Schema

The universal schema that ALL TRUGs must satisfy, regardless of domain.

## Graph Root Schema

```typescript
interface TrugGraph {
  // Required fields
  name: string;                    // Human-readable graph name
  version: "1.0.0";                // TRUGS format version
  type: string;                    // Primary domain (CODE, WEB, WRITER, etc.)

  dimensions: {
    [dimension_name: string]: {
      description: string;         // Human-readable description
      base_level?: string;         // Default: "BASE"
    }
  };

  capabilities: {
    extensions: string[];          // Extension names (e.g., ["typed", "scoped"])
    vocabularies: string[];        // Vocabulary identifiers
    profiles: string[];            // Profile names
  };

  nodes: Node[];                   // Array of nodes
  edges: Edge[];                   // Array of edges

  // Optional fields
  description?: string;            // Brief description
  url?: string;                    // Canonical URL
  maintainer?: string;             // Contact information
  updated?: string;                // ISO 8601 timestamp
  meta?: object;                   // Tool-specific metadata
}
```

---

## Node Schema

```typescript
interface Node {
  // Required fields (7 total)
  id: string;                      // Unique identifier
  type: string;                    // Node type from vocabulary
  properties: object;              // Open object (never null)
  parent_id: string | null;        // Parent node ID or null for root
  contains: string[];              // Array of child node IDs
  metric_level: string;            // Format: PREFIX_NAME
  dimension: string;               // Declared dimension reference
}
```

### Field Details

**id** (string, required)
- Must be unique across all nodes in graph
- Any string format valid
- Recommended: stable identifiers

**type** (string, required)
- Node type from branch vocabulary
- Examples: `FUNCTION`, `PAGE`, `CHAPTER`
- Not validated by CORE (branch-specific)

**properties** (object, required)
- Always an object, never null
- Use `{}` for empty
- No predefined schema (open)
- Contains branch-specific and extension properties

**parent_id** (string | null, required)
- `null` for root nodes
- String ID of parent node for children
- Must be consistent with parent's `contains[]`

**contains** (array, required)
- Always an array, never null
- `[]` for leaf nodes
- Array of child node IDs
- Must be consistent with children's `parent_id`

**metric_level** (string, required)
- Format: `{PREFIX}_{SEMANTIC_NAME}`
- PREFIX must be valid SI prefix (YOTTA to YOCTO)
- Example: `BASE_FUNCTION`, `CENTI_STATEMENT`

**dimension** (string, required)
- Must reference dimension declared in root `dimensions`
- Parent and child must share dimension
- Example: `code_structure`, `web_structure`

---

## Edge Schema

```typescript
interface Edge {
  // Required fields (3 total)
  from_id: string;                 // Source node ID
  to_id: string;                   // Target node ID
  relation: string;                // Relationship type

  // Optional fields
  weight?: number;                 // 0.0 to 1.0
  properties?: object;             // Edge metadata
}
```

### Field Details

**from_id** (string, required)
- Must reference existing node ID
- Source of directed edge

**to_id** (string, required)
- Must reference existing node ID
- Target of directed edge

**relation** (string, required)
- Relationship type from branch vocabulary
- Examples: `CALLS`, `LINKS_TO`, `REFERENCES`
- Not validated by CORE (branch-specific)

**weight** (number, optional)
- Range: 0.0 to 1.0
- Relationship strength or confidence

**properties** (object, optional)
- Edge-specific metadata
- Open schema

---

## Metric Level Prefixes

Valid SI prefixes for `metric_level` field:

```typescript
const METRIC_VALUES = {
  "YOTTA": 1e24,   // 10^24
  "ZETTA": 1e21,   // 10^21
  "EXA":   1e18,   // 10^18
  "PETA":  1e15,   // 10^15
  "TERA":  1e12,   // 10^12
  "GIGA":  1e9,    // 10^9
  "MEGA":  1e6,    // 10^6
  "KILO":  1e3,    // 10^3
  "HECTO": 1e2,    // 10^2
  "DEKA":  1e1,    // 10^1
  "BASE":  1e0,    // 10^0 (standard)
  "DECI":  1e-1,   // 10^-1
  "CENTI": 1e-2,   // 10^-2
  "MILLI": 1e-3,   // 10^-3
  "MICRO": 1e-6,   // 10^-6
  "NANO":  1e-9,   // 10^-9
  "PICO":  1e-12,  // 10^-12
  "FEMTO": 1e-15,  // 10^-15
  "ATTO":  1e-18,  // 10^-18
  "ZEPTO": 1e-21,  // 10^-21
  "YOCTO": 1e-24   // 10^-24
};
```

**Usage:**
- Parent metric level ≥ child metric level (same dimension)
- Comparison uses numeric value of prefix
- Semantic name is free-form

---

## Complete Core Example

Minimal valid TRUG passing all 9 validation rules:

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

---

# Branch Schemas

Domain-specific property conventions and vocabularies.

## Web Branch Schema

**Domain:** Web pages and sites

### Node Types

```typescript
type WebNodeType =
  | "SITE"         // KILO level
  | "PAGE"         // BASE level
  | "SECTION"      // CENTI level
  | "ELEMENT";     // MILLI level
```

### Edge Relations

```typescript
type WebEdgeRelation =
  | "LINKS_TO"     // page → page
  | "NAVIGATES_TO" // element → page
  | "CITES";       // page → external
```

### Property Schema

```typescript
interface WebProperties {
  // Site properties
  domain?: string;
  title?: string;

  // Page properties
  url?: string;
  canonical_url?: string;
  title?: string;
  meta_description?: string;
  meta_keywords?: string[];
  open_graph?: {
    [key: string]: string;
  };
  http_status?: number;
  last_modified?: string;  // ISO 8601
  cache_control?: string;

  // Section properties
  html_tag?: string;
  css_classes?: string[];
  css_id?: string;

  // Element properties
  html_tag?: string;
  content?: string;
  attributes?: { [key: string]: string };
}
```

### Extension Requirements

```typescript
interface WebCapabilities {
  extensions: [];  // No extensions required
  vocabularies: ["web_site_v1"];
  profiles: [];
}
```

### Complete Example

```json
{
  "name": "Documentation Site",
  "version": "1.0.0",
  "type": "WEB",
  "dimensions": {
    "web_structure": {
      "description": "Website hierarchy",
      "base_level": "BASE"
    }
  },
  "capabilities": {
    "extensions": [],
    "vocabularies": ["web_site_v1"],
    "profiles": []
  },
  "nodes": [
    {
      "id": "site_root",
      "type": "SITE",
      "properties": {
        "title": "TRUGS Documentation",
        "domain": "trugs.dev"
      },
      "parent_id": null,
      "contains": ["page_home"],
      "metric_level": "KILO_SITE",
      "dimension": "web_structure"
    },
    {
      "id": "page_home",
      "type": "PAGE",
      "properties": {
        "title": "Home",
        "url": "/",
        "meta_description": "TRUGS Protocol Documentation",
        "http_status": 200
      },
      "parent_id": "site_root",
      "contains": [],
      "metric_level": "BASE_PAGE",
      "dimension": "web_structure"
    }
  ],
  "edges": []
}
```

---

## Writer Branch Schema

**Domain:** Written documents (books, manuals, papers)

### Node Types

```typescript
type WriterNodeType =
  | "BOOK"         // MEGA level
  | "CHAPTER"      // BASE level
  | "SECTION"      // CENTI level
  | "PARAGRAPH"    // MILLI level
  | "SENTENCE";    // MICRO level
```

### Edge Relations

```typescript
type WriterEdgeRelation =
  | "REFERENCES"   // section → section
  | "CONTINUES"    // paragraph → paragraph
  | "CITES";       // paragraph → bibliography
```

### Property Schema

```typescript
interface WriterProperties {
  // Book properties
  title?: string;
  author?: string;
  isbn?: string;
  publisher?: string;

  // Chapter properties
  title?: string;
  chapter_number?: number;
  page_start?: number;
  page_end?: number;
  word_count?: number;

  // Section properties
  title?: string;
  section_number?: string;
  in_table_of_contents?: boolean;

  // Paragraph properties
  content?: string;
  word_count?: number;

  // Cross-cutting properties
  footnotes?: Array<{
    marker: string;
    text: string;
  }>;
  index_terms?: string[];
  bibliography_entries?: string[];
}
```

### Extension Requirements

```typescript
interface WriterCapabilities {
  extensions: [];  // No extensions required
  vocabularies: ["document_v1"];
  profiles: [];
}
```

### Complete Example

```json
{
  "name": "TRUGS Guide",
  "version": "1.0.0",
  "type": "WRITER",
  "dimensions": {
    "document_structure": {
      "description": "Document hierarchy",
      "base_level": "BASE"
    }
  },
  "capabilities": {
    "extensions": [],
    "vocabularies": ["document_v1"],
    "profiles": []
  },
  "nodes": [
    {
      "id": "book_guide",
      "type": "BOOK",
      "properties": {
        "title": "The Complete TRUGS Guide",
        "author": "TRUGS Team"
      },
      "parent_id": null,
      "contains": ["chapter_1"],
      "metric_level": "MEGA_BOOK",
      "dimension": "document_structure"
    },
    {
      "id": "chapter_1",
      "type": "CHAPTER",
      "properties": {
        "title": "Introduction",
        "chapter_number": 1,
        "page_start": 1,
        "page_end": 24,
        "word_count": 5200
      },
      "parent_id": "book_guide",
      "contains": [],
      "metric_level": "BASE_CHAPTER",
      "dimension": "document_structure"
    }
  ],
  "edges": []
}
```

---

## typed Extension Schema

**Purpose:** Type system information

### type_info Property Schema

```typescript
interface TypeInfo {
  category: TypeCategory;

  // For integer
  width?: 8 | 16 | 32 | 64 | 128;
  signed?: boolean;

  // For float
  width?: 32 | 64;

  // For pointer
  pointee_type?: TypeInfo;

  // For array
  element_type?: TypeInfo;
  size?: number;

  // For struct
  name?: string;
  fields?: Array<{
    name: string;
    type: TypeInfo;
  }>;

  // For function
  params?: TypeInfo[];
  return_type?: TypeInfo;
}

type TypeCategory =
  | "integer"
  | "float"
  | "pointer"
  | "array"
  | "struct"
  | "function"
  | "string"
  | "boolean"
  | "void"
  | "dynamic";
```

### Usage Example

```json
{
  "properties": {
    "function_name": "add",
    "type_info": {
      "category": "function",
      "params": [
        {"category": "integer", "width": 32, "signed": true},
        {"category": "integer", "width": 32, "signed": true}
      ],
      "return_type": {
        "category": "integer",
        "width": 32,
        "signed": true
      }
    }
  }
}
```

---

## scoped Extension Schema

**Purpose:** Variable scoping information

### scope_id Property Schema

```typescript
type ScopeID = string;  // Format: global | local_{id} | closure_{id} | block_{id}
```

### Usage Example

```json
{
  "properties": {
    "variable_name": "x",
    "scope_id": "local_outer"
  }
}
```

---

## ownership Extension Schema

**Purpose:** Resource ownership and lifetime system

### ownership Property Schema

```typescript
interface Ownership {
  self_param: "owned" | "borrowed" | "mut_borrowed" | "none";
  param_ownership: {
    [param_name: string]: "owned" | "borrowed" | "mut_borrowed";
  };
}
```

### lifetimes Property Schema

```typescript
interface Lifetimes {
  function_lifetime?: string;  // Format: 'a
  param_lifetimes: {
    [param_name: string]: string;
  };
  return_lifetime?: string;
}
```

### Usage Example

```json
{
  "properties": {
    "function_name": "distance",
    "ownership": {
      "self_param": "borrowed",
      "param_ownership": {
        "other": "borrowed"
      }
    },
    "lifetimes": {
      "function_lifetime": "'a",
      "param_lifetimes": {
        "self": "'a",
        "other": "'a"
      }
    }
  }
}
```

---

# Complete Examples

## Validation Rules

All TRUGs must pass the 9 CORE validation rules:

1. **Node ID Uniqueness** - All node IDs unique
2. **Edge ID Validity** - Edges reference existing nodes
3. **Hierarchy Consistency** - parent_id ↔ contains bidirectional
4. **Metric Level Ordering** - Parent ≥ child (same dimension)
5. **Dimension Declaration** - All dimensions declared
6. **Required Fields Present** - All 7 node fields, 3 edge fields present
7. **Field Type Correctness** - Correct JSON types
8. **Extension Declaration** - Extensions declared before use
9. **Metric Level Format** - PREFIX_NAME format valid

See [SPEC_validation.md](SPEC_validation.md) for complete validation specification.

---

## Extension Property Mapping

```python
EXTENSION_PROPERTIES = {
    'typed': ['type_info'],
    'scoped': ['scope_id'],
    'ownership': ['ownership', 'lifetimes']
}
```

**Validation:** If property present, extension must be declared.

---

## TypeScript Schema Definitions

Complete TypeScript definitions for type-safe TRUG handling:

```typescript
// Graph root
interface TrugGraph {
  name: string;
  version: "1.0.0";
  type: string;
  dimensions: Record<string, Dimension>;
  capabilities: Capabilities;
  nodes: Node[];
  edges: Edge[];
  description?: string;
  url?: string;
  maintainer?: string;
  updated?: string;
  meta?: Record<string, unknown>;
}

// Dimension
interface Dimension {
  description: string;
  base_level?: string;
}

// Capabilities
interface Capabilities {
  extensions: string[];
  vocabularies: string[];
  profiles: string[];
}

// Node
interface Node {
  id: string;
  type: string;
  properties: Record<string, unknown>;
  parent_id: string | null;
  contains: string[];
  metric_level: string;
  dimension: string;
}

// Edge
interface Edge {
  from_id: string;
  to_id: string;
  relation: string;
  weight?: number;
  properties?: Record<string, unknown>;
}
```

---

## JSON Schema

For JSON Schema validation tools:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["name", "version", "type", "dimensions", "capabilities", "nodes", "edges"],
  "properties": {
    "name": {"type": "string"},
    "version": {"type": "string", "const": "1.0.0"},
    "type": {"type": "string"},
    "dimensions": {
      "type": "object",
      "additionalProperties": {
        "type": "object",
        "required": ["description"],
        "properties": {
          "description": {"type": "string"},
          "base_level": {"type": "string"}
        }
      }
    },
    "capabilities": {
      "type": "object",
      "required": ["extensions", "vocabularies", "profiles"],
      "properties": {
        "extensions": {"type": "array", "items": {"type": "string"}},
        "vocabularies": {"type": "array", "items": {"type": "string"}},
        "profiles": {"type": "array", "items": {"type": "string"}}
      }
    },
    "nodes": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["id", "type", "properties", "parent_id", "contains", "metric_level", "dimension"],
        "properties": {
          "id": {"type": "string"},
          "type": {"type": "string"},
          "properties": {"type": "object"},
          "parent_id": {"type": ["string", "null"]},
          "contains": {"type": "array", "items": {"type": "string"}},
          "metric_level": {"type": "string"},
          "dimension": {"type": "string"}
        }
      }
    },
    "edges": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["from_id", "to_id", "relation"],
        "properties": {
          "from_id": {"type": "string"},
          "to_id": {"type": "string"},
          "relation": {"type": "string"},
          "weight": {"type": "number", "minimum": 0.0, "maximum": 1.0},
          "properties": {"type": "object"}
        }
      }
    }
  }
}
```

---

## Summary

**Core Schema:**
- 7 required node fields
- 3 required edge fields
- Open properties object
- 21 SI metric prefixes

**Branch Schemas:**
- Web: Site and page structure
- Writer: Document hierarchy

**Extension Schemas:**
- typed: Type system information
- scoped: Variable and context scoping
- ownership: Resource ownership and lifetimes

**Key Principle:** CORE = structure, BRANCH = vocabulary, EXTENSION = capabilities

---

## See Also

- [CORE.md](CORE.md) - The 7 boundaries
- [BRANCHES.md](BRANCHES.md) - Complete branch specifications
- [SPEC_extensions.md](SPEC_extensions.md) - Complete extension specifications
- [SPEC_validation.md](SPEC_validation.md) - The 9 validation rules
- [SPEC_patterns.md](SPEC_patterns.md) - System patterns

---

**TRUGS Schema v1.0.0 (AAA_AARDVARK)**
