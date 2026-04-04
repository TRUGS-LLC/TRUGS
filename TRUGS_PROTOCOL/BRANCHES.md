]633;E;{   sed -n '1,168p' TRUGS_PROTOCOL/BRANCHES.md\x0ased -n '326,447p' TRUGS_PROTOCOL/BRANCHES.md\x3b   sed -n '863,1175p' TRUGS_PROTOCOL/BRANCHES.md\x3b   sed -n '1288,1543p' TRUGS_PROTOCOL/BRANCHES.md\x0ased -n '1571,1662p' TRUGS_PROTOCOL/BRANCHES.md\x3b } > /tmp/branches_new.md;f6115331-d0a5-417b-983d-f8667381b403]633;C# TRUGS Protocol Branches

**Version:** 1.0.0 (AAA_AARDVARK)  
**Status:** ✅ Stable  
**Purpose:** Domain-specific properties and vocabularies

---

## What is a Branch?

A **Branch** defines what makes a domain unique - the properties and vocabularies that exist in that domain but not in others.

**Branch = Domain-specific properties + domain-specific vocabularies**

**What a Branch is:**
- ✅ Properties unique to this domain
- ✅ Node type vocabulary (TRANSFORM, PAGE, CHAPTER)
- ✅ Edge relation vocabulary (FEEDS, LINKS_TO, REFERENCES)
- ✅ Extension requirements (compute)
- ✅ Property conventions (operation, url, title)

**What a Branch is NOT:**
- ❌ Hierarchy (that's CORE: parent_id, contains, metric_level)
- ❌ Graph structure (that's CORE: 7 boundaries)
- ❌ Validation rules (CORE validates structure)
- ❌ Required by CORE (branches are domain-specific)

---

## CORE + BRANCH = Complete TRUG

```
CORE provides:
- 7 node fields (structure)
- 3 edge fields (relationships)
- Hierarchy rules (parent/child, metric ordering)
- Validation rules (9 mechanical checks)
- Universal boundaries (apply to all TRUGs)

BRANCH provides:
- Node types (what things are called)
- Edge relations (what relationships are called)
- Properties (what data is stored)
- Extensions (what capabilities are needed)
- Conventions (how properties are used)
```

**Example:**

**CORE fields (universal - same for all domains):**
```json
{
  "id": "transform_filter",
  "parent_id": "pipeline_etl",
  "contains": [],
  "metric_level": "BASE_TRANSFORM",
  "dimension": "data_flow"
}
```

**BRANCH fields (domain-specific - Computation conventions):**
```json
{
  "type": "TRANSFORM",
  "properties": {
    "operation": "filter",
    "parameters": {"predicate": {"field": "status", "op": "eq", "value": "active"}},
    "description": "Keep only active records"
  }
}
```

---

## How Branches Relate to CORE

### CORE is Universal

**CORE defines boundaries that ALL TRUGs must satisfy:**
- 7 required node fields
- 3 required edge fields
- Bidirectional hierarchy
- Metric level ordering
- Dimension declaration
- JSON structure
- 9 validation rules

**Every TRUG passes CORE validation, regardless of branch.**

---

### Branches are Domain-Specific

**Branches define vocabularies and conventions for specific domains:**
- What node types exist (FUNCTION vs PAGE vs CHAPTER)
- What edge relations exist (CALLS vs LINKS_TO vs REFERENCES)
- What properties to use (function_name vs url vs chapter_number)
- What extensions to declare (typed vs none)

**Branches do NOT affect CORE validation.**

---

### CORE Validates Structure, Branches Validate Semantics

**CORE validation (universal):**
```python
# All TRUGs, regardless of branch
assert node has 7 required fields
assert parent.contains includes child.id
assert parent.metric_level >= child.metric_level
assert dimension is declared
```

**Branch validation (domain-specific):**
```python
# Computation branch only
assert node.type in ['PIPELINE', 'STAGE', 'TRANSFORM', 'DATA', 'FLOW_ENTRY', 'FLOW_EXIT']
assert 'operation' in transform_node.properties
assert 'compute' in capabilities.extensions if 'operation_spec' used
```

---

### Multiple Branches Can Coexist

**A single TRUG can use multiple branches:**

```json
{
  "dimensions": {
    "data_flow": {
      "description": "Computational pipeline"
    },
    "development": {
      "description": "Development lifecycle"
    }
  },
  "capabilities": {
    "extensions": [],
    "vocabularies": ["compute_v1", "aaa_v1"]
  },
  "nodes": [
    {
      "id": "transform_filter",
      "type": "TRANSFORM",
      "dimension": "data_flow",
      "properties": {
        "operation": "filter",
        "description": "Filter active records"
      }
    },
    {
      "id": "task_implement_filter",
      "type": "TASK",
      "dimension": "development",
      "properties": {
        "name": "Implement filter operation",
        "status": "NOT_STARTED",
        "operation": "filter"
      }
    }
  ]
}
```

**Both nodes satisfy CORE. Both use branch-specific properties.**

---
## Understanding Through Content Examples

### Writer Branch - Documents

**What's unique to written documents:**

```json
{
  "id": "chapter_1",
  "type": "CHAPTER",
  "properties": {
    "title": "Introduction to TRUGS",
    "content": "This chapter introduces...",
    "chapter_number": 1,
    "page_start": 15,
    "page_end": 42,
    "word_count": 3500,
    "reading_time_minutes": 14,
    "footnotes": [
      {"marker": "1", "text": "See appendix A"}
    ],
    "index_terms": ["TRUGS", "graphs"],
    "in_table_of_contents": true,
    "bibliography_entries": ["Smith2024"]
  },
  "parent_id": "book_guide",
  "contains": ["section_1", "section_2"],
  "metric_level": "BASE_CHAPTER",
  "dimension": "document_structure"
}
```

**Writer-specific elements:**
- Properties: `chapter_number`, `page_start`, `footnotes`, `index_terms`, `bibliography_entries`
- Node types: BOOK, CHAPTER, SECTION, PARAGRAPH, CITATION, REFERENCE
- Edge relations: REFERENCES, CONTINUES, CITES, SUPPORTS, CONTRADICTS
- Extensions: None (CORE only)

**Why these are Writer-specific:**
- Chapter numbers for sequential reading
- Page numbers for physical pagination
- Footnotes for print-specific annotations
- Index terms for back-of-book index
- Bibliography for citations

---

### Web Branch - Websites

**What's unique to web pages:**

```json
{
  "id": "page_intro",
  "type": "PAGE",
  "properties": {
    "title": "Introduction to TRUGS",
    "content": "This page introduces...",
    "url": "/docs/introduction",
    "canonical_url": "https://trugs.dev/docs/introduction",
    "meta_description": "Learn TRUGS protocol",
    "meta_keywords": ["TRUGS", "graphs"],
    "open_graph": {
      "og:title": "Introduction to TRUGS",
      "og:image": "/images/preview.png"
    },
    "css_classes": ["documentation-page"],
    "http_status": 200,
    "last_modified": "2026-02-08T10:30:00Z",
    "cache_control": "public, max-age=3600"
  },
  "parent_id": "site_root",
  "contains": ["section_hero"],
  "metric_level": "BASE_PAGE",
  "dimension": "web_structure"
}
```

**Web-specific elements:**
- Properties: `url`, `meta_description`, `open_graph`, `css_classes`, `http_status`, `cache_control`
- Node types: SITE, PAGE, SECTION, ELEMENT
- Edge relations: LINKS_TO, NAVIGATES_TO, CITES
- Extensions: None (CORE only)

**Why these are Web-specific:**
- URLs for web addressing
- Meta tags for SEO
- Open Graph for social media
- CSS classes for styling
- HTTP headers for protocol

---

## What's Universal (CORE)

**All examples above share:**

```json
{
  "id": "unique_identifier",
  "type": "DOMAIN_SPECIFIC",
  "properties": {},
  "parent_id": "parent_or_null",
  "contains": ["children"],
  "metric_level": "PREFIX_NAME",
  "dimension": "dimension_name"
}
```

**Universal CORE concepts:**
- All have 7 required node fields
- All use parent_id/contains for hierarchy
- All use metric_level for positioning
- All reference declared dimensions
- All pass CORE validation

**The structure is universal. The vocabulary is domain-specific.**

---

## Complete Branch Definitions

### Web Branch

**Domain:** Web pages and sites

**Node Type Vocabulary:**
- SITE (KILO level)
- PAGE (BASE level)
- SECTION (CENTI level)
- ELEMENT (MILLI level)

**Edge Relation Vocabulary:**
- LINKS_TO (page → page)
- NAVIGATES_TO (element → page)
- CITES (page → external)

**Property Conventions:**
```json
{
  "url": "string",
  "canonical_url": "string",
  "title": "string",
  "meta_description": "string",
  "meta_keywords": ["string"],
  "open_graph": {},
  "html_tag": "string",
  "css_classes": ["string"],
  "http_status": "integer",
  "last_modified": "ISO8601",
  "cache_control": "string"
}
```

**Extension Requirements:**
- None (CORE only)

**Example:**
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
        "url": "https://trugs.dev"
      },
      "parent_id": null,
      "contains": ["page_home", "page_docs"],
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
      "contains": ["section_hero"],
      "metric_level": "BASE_PAGE",
      "dimension": "web_structure"
    },
    {
      "id": "page_docs",
      "type": "PAGE",
      "properties": {
        "title": "Documentation",
        "url": "/docs",
        "meta_description": "Complete TRUGS documentation",
        "http_status": 200
      },
      "parent_id": "site_root",
      "contains": [],
      "metric_level": "BASE_PAGE",
      "dimension": "web_structure"
    },
    {
      "id": "section_hero",
      "type": "SECTION",
      "properties": {
        "html_tag": "section",
        "css_classes": ["hero", "primary"]
      },
      "parent_id": "page_home",
      "contains": ["elem_heading", "elem_cta"],
      "metric_level": "CENTI_SECTION",
      "dimension": "web_structure"
    },
    {
      "id": "elem_heading",
      "type": "ELEMENT",
      "properties": {
        "html_tag": "h1",
        "content": "Welcome to TRUGS"
      },
      "parent_id": "section_hero",
      "contains": [],
      "metric_level": "MILLI_ELEMENT",
      "dimension": "web_structure"
    }
  ],
  "edges": [
    {
      "from_id": "page_home",
      "to_id": "page_docs",
      "relation": "LINKS_TO",
      "properties": {
        "link_text": "Documentation"
      }
    }
  ]
}
```

---

### Writer Branch

**Domain:** Written documents (books, manuals, papers)

**Node Type Vocabulary:**
- BOOK (MEGA level) — `MEGA_BOOK`
- CHAPTER (BASE level) — `BASE_CHAPTER`
- SECTION (CENTI level) — `CENTI_SECTION`
- PARAGRAPH (MILLI level) — `MILLI_PARAGRAPH`
- CITATION (MILLI level) — `MILLI_CITATION`
- REFERENCE (MILLI level) — `MILLI_REFERENCE`

**Edge Relation Vocabulary:**
- REFERENCES (section → section)
- CONTINUES (paragraph → paragraph)
- CITES (paragraph → bibliography)
- SUPPORTS (source → claim)
- CONTRADICTS (source → claim)

**Property Conventions:**
```json
{
  "title": "string",
  "content": "string",
  "chapter_number": "integer",
  "section_number": "string",
  "page_start": "integer",
  "page_end": "integer",
  "word_count": "integer",
  "footnotes": [],
  "index_terms": ["string"],
  "bibliography_entries": ["string"]
}
```

**Extension Requirements:**
- None (CORE only)

**Example:**
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
      "contains": ["chapter_1", "chapter_2"],
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
      "contains": ["section_1_1", "section_1_2"],
      "metric_level": "BASE_CHAPTER",
      "dimension": "document_structure"
    },
    {
      "id": "chapter_2",
      "type": "CHAPTER",
      "properties": {
        "title": "Core Concepts",
        "chapter_number": 2,
        "page_start": 25,
        "page_end": 48,
        "word_count": 4800
      },
      "parent_id": "book_guide",
      "contains": ["section_2_1"],
      "metric_level": "BASE_CHAPTER",
      "dimension": "document_structure"
    },
    {
      "id": "section_1_1",
      "type": "SECTION",
      "properties": {
        "title": "What is TRUGS?",
        "section_number": "1.1",
        "in_table_of_contents": true
      },
      "parent_id": "chapter_1",
      "contains": ["para_1_1_1"],
      "metric_level": "CENTI_SECTION",
      "dimension": "document_structure"
    },
    {
      "id": "para_1_1_1",
      "type": "PARAGRAPH",
      "properties": {
        "content": "TRUGS is a universal graph representation system...",
        "word_count": 87
      },
      "parent_id": "section_1_1",
      "contains": [],
      "metric_level": "MILLI_PARAGRAPH",
      "dimension": "document_structure"
    },
    {
      "id": "section_1_2",
      "type": "SECTION",
      "properties": {
        "title": "Why TRUGS?",
        "section_number": "1.2",
        "in_table_of_contents": true
      },
      "parent_id": "chapter_1",
      "contains": [],
      "metric_level": "CENTI_SECTION",
      "dimension": "document_structure"
    },
    {
      "id": "chapter_3",
      "type": "CHAPTER",
      "properties": {
        "title": "Advanced Topics",
        "chapter_number": 3,
        "page_start": 49,
        "page_end": 72,
        "word_count": 5500
      },
      "parent_id": "book_guide",
      "contains": ["section_3_1"],
      "metric_level": "BASE_CHAPTER",
      "dimension": "document_structure"
    },
    {
      "id": "section_3_1",
      "type": "SECTION",
      "properties": {
        "title": "Multi-dimensional Graphs",
        "section_number": "3.1",
        "in_table_of_contents": true
      },
      "parent_id": "chapter_3",
      "contains": [],
      "metric_level": "CENTI_SECTION",
      "dimension": "document_structure"
    }
  ],
  "edges": [
    {
      "from_id": "section_1_2",
      "to_id": "section_3_1",
      "relation": "REFERENCES",
      "properties": {
        "reference_text": "See section 3.1 for details"
      }
    }
  ]
}
```

---

## Filesystem Branch (Folder Structure)

**Domain:** Project folder structure and documentation graphs

**Note:** Filesystem Branch is vocabulary like any other branch — it defines node types and edge relations for folder graphs. It is not a structural primitive. Edges in filesystem TRUGs support the optional `weight` field for curator endorsement (0.0–1.0).

**Purpose:** Represents a folder in a software project as a graph — its files, their roles, and relationships between them. Used by TRUGS_GATEWAY to maintain the three-file pattern (AAA.md, README.md, ARCHITECTURE.md) as deterministic compiled views of a single source of truth.

**Graph Root Type:** `PROJECT`

**When to Use:**
- Representing a project folder's structure as a TRUG
- Generating deterministic documentation from a single source
- Cross-folder dependency tracking
- Folder-level validation (does the TRUG match the filesystem?)

**Node Type Vocabulary:**

| Node Type | Metric Level | Description |
|-----------|-------------|-------------|
| FOLDER | KILO level | Root node representing the folder itself |
| DOCUMENT | BASE level | A human-authored file (markdown, config, etc.) |
| SPECIFICATION | BASE level | A formal specification or protocol document |
| STANDARD | BASE level | A standards/guidelines document |
| TEMPLATE | BASE level | A template file used to generate other files |
| GENERATED | BASE level | A file compiled from the TRUG (AAA.md, README.md, ARCHITECTURE.md) |
| SOURCE | BASE level | A source code file |
| CONFIG | BASE level | A configuration file (pyproject.toml, etc.) |
| TEST | CENTI level | A test file or test suite |

**Edge Relation Vocabulary:**

| Relation | Description | Example |
|----------|-------------|---------|
| REFERENCES | General reference between files | vision → tech stack |
| EXTENDS | Adds capabilities to another component | branches → core |
| IMPLEMENTS | Realizes a specification | code → spec |
| DEFINED_BY | Formally defined by another document | rules → schema |
| ENFORCED_BY | Mechanically enforced by validation | boundaries → validator |
| GOVERNS | Sets standards/rules for another file | standards → readme |
| TEMPLATES | Provides structural template for another | template → generated |
| COMPLEMENTS | Covers same topic for different audience | human ref ↔ LLM ref |
| SUPERSEDES | Replaces or extends a previous version | v2 → v1 |
| REPRESENTED_BY | Has equivalent representation in another format | .md → .trug.json |
| DEPENDS_ON | Runtime or build dependency | module → library |
| TESTS | Validates correctness of another component | test → source |

**Property Conventions:**
```json
{
  "name": "string (filename or component name)",
  "purpose": "string (what this file/component does)",
  "format": "string (markdown, trug_json, python, toml, etc.)",
  "audience": "string (developers, LLMs, everyone, architects, stakeholders)",
  "phase": "string (VISION, FEASIBILITY, SPECIFICATIONS, ARCHITECTURE, VALIDATION, CODING, TESTING, AUDIT, DEPLOYMENT, MAINTENANCE)",
  "status": "string (ACTIVE, STABLE, DRAFT, DEPRECATED)",
  "layer": "string (optional: core, branch, extension, pattern, meta)",
  "version": "string (optional: semantic version)",
  "generated_header": "string (present on GENERATED nodes: header comment for compiled files)"
}
```

**Extension Requirements:**
- None (CORE only)

**Naming Convention:** `folder.trug.json` (one per folder, always this filename)

**Example:**
```json
{
  "name": "TRUGS_PROTOCOL Folder",
  "version": "1.0.0",
  "type": "PROJECT",
  "description": "Complete TRUGS protocol specification documentation",
  "dimensions": {
    "folder_structure": {
      "description": "Protocol documentation structure and relationships",
      "base_level": "BASE"
    }
  },
  "capabilities": {
    "extensions": [],
    "vocabularies": ["project_v1"],
    "profiles": []
  },
  "nodes": [
    {
      "id": "protocol_folder",
      "type": "FOLDER",
      "properties": {
        "name": "TRUGS_PROTOCOL",
        "purpose": "Complete TRUGS protocol specification documentation",
        "phase": "MAINTENANCE",
        "status": "STABLE"
      },
      "parent_id": null,
      "contains": ["spec_core", "spec_branches", "doc_aaa"],
      "metric_level": "KILO_FOLDER",
      "dimension": "folder_structure"
    },
    {
      "id": "spec_core",
      "type": "SPECIFICATION",
      "properties": {
        "name": "CORE.md",
        "purpose": "Universal graph structure and validation rules",
        "format": "markdown",
        "layer": "core"
      },
      "parent_id": "protocol_folder",
      "contains": [],
      "metric_level": "BASE_SPECIFICATION",
      "dimension": "folder_structure"
    },
    {
      "id": "spec_branches",
      "type": "SPECIFICATION",
      "properties": {
        "name": "BRANCHES.md",
        "purpose": "Domain-specific vocabularies",
        "format": "markdown",
        "layer": "branch"
      },
      "parent_id": "protocol_folder",
      "contains": [],
      "metric_level": "BASE_SPECIFICATION",
      "dimension": "folder_structure"
    },
    {
      "id": "doc_aaa",
      "type": "GENERATED",
      "properties": {
        "name": "AAA.md",
        "purpose": "Development tracking",
        "format": "markdown",
        "generated_header": "GENERATED BY TRUGS — DO NOT EDIT"
      },
      "parent_id": "protocol_folder",
      "contains": [],
      "metric_level": "BASE_GENERATED",
      "dimension": "folder_structure"
    }
  ],
  "edges": [
    {
      "from_id": "spec_branches",
      "to_id": "spec_core",
      "relation": "EXTENDS",
      "properties": {
        "description": "Branches add domain vocabulary to universal core"
      }
    }
  ]
}
```

**Key Design Decisions:**
1. **One TRUG per folder** — always named `folder.trug.json`
2. **GENERATED nodes** — mark files compiled from the TRUG, not hand-authored
3. **FOLDER is the root** — every folder TRUG has exactly one FOLDER node at KILO level
4. **Dimension is `folder_structure`** — consistent across all folder TRUGs
5. **Flat hierarchy** — folder contains files directly (no deep nesting within a single folder)

---

## Advanced Branches

The following advanced branches define specialized vocabularies for **Agentic Systems** — Orchestration, Memory, World Modeling, and Graph-as-Computation — rather than just representing static content. These branches are critical for enabling capabilities like Agent Coordination and Living Memory.

> **Note:** Previously documented in SPEC_advanced_branches.md, now merged here as the single source of truth for all branch specifications.

---

### ORCHESTRATION Branch

**Domain:** Multi-Agent Coordination
**Purpose:** Enables multi-agent systems to be *coordinated via* graph structure rather than a hard-coded loop.
**Key Concept:** Exclusive Communication (Agents communicate only via graph edits).

#### Node Vocabulary

| Node Type | Level | Description |
|-----------|-------|-------------|
| `AGENT` | BASE | An autonomous actor (e.g. "Worker", "Reviewer"). |
| `PRINCIPAL` | BASE | An identity or role (e.g. "Agent Alpha", "System Admin"). |
| `RESOURCE` | KILO | An asset to be accessed (e.g. "Database", "File"). |
| `PERMISSION` | MILLI | An access grant (e.g. "Read Access"). |
| `TASK` | BASE | A unit of work to be delegated. |
| `ESCALATION` | BASE | A request for human intervention. |

#### Edge Vocabulary

| Edge Type | From | To | Description |
|-----------|------|----|-------------|
| `DELEGATES_TO` | AGENT | TASK | Assigns work to a sub-agent or task. |
| `REPORTS_TO` | AGENT | PRINCIPAL | Submits results back to the requestor. |
| `AUTHORIZES` | PRINCIPAL | PERMISSION | Grants specific rights to a role. |
| `ESCALATES_TO` | TASK | AGENT (Human) | Routes failure for manual review. |
| `ACCESSES` | AGENT | RESOURCE | Represents a read/write operation. |

---

### CODE Branch

**Domain:** Language-agnostic source code structure
**Vocabulary identifier:** `code_v1`
**Purpose:** Represents code structure — modules, packages, classes, structs, functions, and their relationships — independent of programming language. Language is a property on nodes, not a branch identifier.
**Key Concepts:** Containment (packages contain modules contain definitions), Reference (functions call functions, modules import modules), Typing (entities have types, functions return types).

> **History:** Replaces the former Python, Rust, and LLVM branches (extracted in #607) with a single language-agnostic vocabulary. See issue #621.

#### Node Vocabulary

| Node Type | Metric Level | Description |
|-----------|-------------|-------------|
| `CODE_GRAPH` | KILO | Root node for a code graph. |
| `PACKAGE` | HECTO | A package or top-level namespace (e.g. Go package, Java package, Python top-level package). |
| `MODULE` | HECTO | A single source file or module (e.g. Python module, TypeScript file, Go file). |
| `CLASS` | DEKA | A class definition (Python, Java, TypeScript, Ruby). |
| `STRUCT` | DEKA | A struct or record type (Go, Rust, C, Kotlin data class). |
| `INTERFACE` | DEKA | An interface, trait, or protocol (Go interface, Rust trait, Python Protocol, Java interface, TypeScript interface). |
| `ENUM` | DEKA | An enumeration type (Python Enum, Rust enum, TypeScript enum, Java enum, Go iota constants). |
| `FUNCTION` | BASE | A standalone function (not bound to a class/struct). |
| `METHOD` | BASE | A function bound to a class, struct, or interface. |
| `PARAMETER` | CENTI | A function/method parameter. |
| `VARIABLE` | CENTI | A variable or field declaration. |
| `IMPORT` | CENTI | An import or dependency statement. |
| `DECORATOR` | CENTI | A decorator, annotation, or attribute (Python @decorator, Java @Annotation, Rust #[attribute]). |
| `CONSTANT` | CENTI | A constant or immutable value declaration. |
| `TYPE_ANNOTATION` | MILLI | A type hint, generic parameter, or type constraint. |

#### Edge Vocabulary

| Edge Type | From → To | Description |
|-----------|-----------|-------------|
| `CALLS` | FUNCTION/METHOD → FUNCTION/METHOD | Invocation relationship. |
| `IMPORTS` | MODULE → MODULE/PACKAGE | Module imports another module or package. |
| `INHERITS` | CLASS → CLASS | Class inheritance (extends/subclasses). |
| `IMPLEMENTS` | CLASS/STRUCT → INTERFACE | Type implements an interface/trait/protocol. |
| `CONTAINS_DEFINITION` | MODULE/CLASS/STRUCT → any | Parent contains a definition (function, method, variable, etc.). |
| `RETURNS_TYPE` | FUNCTION/METHOD → TYPE_ANNOTATION | Function returns this type. |
| `HAS_PARAMETER` | FUNCTION/METHOD → PARAMETER | Function has this parameter. |
| `DECORATES` | DECORATOR → FUNCTION/METHOD/CLASS | Decorator applied to a definition. |
| `REFERENCES` | any → any | General reference (e.g. variable references a type, function references a constant). |
| `DEPENDS_ON` | PACKAGE → PACKAGE | Package-level dependency. |
| `OVERRIDES` | METHOD → METHOD | Method overrides a parent class/interface method. |

#### Property Conventions

```json
{
  "name": "string (required — identifier name)",
  "description": "string (required — what this element does)",
  "language": "string (python|go|rust|typescript|java|c|ruby|...)",
  "visibility": "string (public|private|protected|internal|package)",
  "is_async": "boolean (async function/method)",
  "is_static": "boolean (static/class method)",
  "is_abstract": "boolean (abstract method/class)",
  "return_type": "string (return type name)",
  "signature": "string (full function/method signature)",
  "docstring": "string (documentation string or comment)",
  "parameters_count": "integer (number of parameters)",
  "file_path": "string (relative path to source file)",
  "line_start": "integer (starting line number)",
  "line_end": "integer (ending line number)"
}
```

**Extension Requirements:** None (CORE only)

---

### KNOWLEDGE Branch

**Domain:** Knowledge management — persistent memory, ontology, and research
**Vocabulary identifier:** `knowledge_v1`
**Purpose:** Unified vocabulary for "what I know" — covers session persistence (Living), world modeling (Ontology), and bibliographic indexing (Research).
**Key Concepts:** Accumulation (knowledge is added, never lost), Taxonomy (entities have types and relationships), Evidence (claims cite sources).

> **History:** Merges the former Living, Knowledge, and Research branches into a single vocabulary. See issue #622. Also incorporates the DECISION node and rejection/invalidation edges from #620.

#### Node Vocabulary

| Node Type | Metric Level | Description |
|-----------|-------------|-------------|
| `KNOWLEDGE_GRAPH` | KILO | Root node for a knowledge graph. |
| `CONCEPT` | BASE | An abstract idea (e.g. "Disease", "Recursion"). |
| `ENTITY` | BASE | A specific instance or discovered fact (e.g. "Type 2 Diabetes", "PostgreSQL supports JSONB"). |
| `CLASS` | KILO | A taxonomic category (e.g. "Metabolic Disorder"). |
| `INSTANCE` | MILLI | An individual occurrence (e.g. "Patient #123"). |
| `QUERY` | BASE | A user's input question or intent. |
| `ANSWER` | BASE | A synthesized system response. |
| `SYNTHESIS` | BASE | A summary or insight derived from multiple facts. |
| `DECISION` | BASE | A conclusion or chosen course of action — forward-looking and operational, distinct from SYNTHESIS (which is backward-looking and informational). |
| `TOOL_EXECUTION` | MILLI | A record of an action taken (e.g. "Search", "API call"). |
| `WEB_SOURCE` | BASE | A web page or online resource used as evidence. |
| `PAPER` | BASE | An academic paper or formal publication. |
| `PROJECT` | BASE | A software project, library, or framework under evaluation. |
| `AUTHOR` | BASE | A person or organization that authored a source. |
| `CLAIM` | CENTI | A specific assertion extracted from a source, with confidence. |
| `VERSION` | CENTI | A specific release version of a project or library. |

#### Edge Vocabulary

| Edge Type | From → To | Description |
|-----------|-----------|-------------|
| `IS_A` | ENTITY → CLASS | Taxonomy / subclass relationship. |
| `HAS_PROPERTY` | ENTITY → CONCEPT | Attribute definition. |
| `PART_OF` | ENTITY → ENTITY | Compositional relationship. |
| `CAUSES` | ENTITY → ENTITY | Causal link. |
| `RELATED_TO` | ENTITY → ENTITY | General association. |
| `TRIGGERS` | QUERY → TOOL_EXECUTION | The query caused this action. |
| `PRODUCES` | TOOL_EXECUTION → ENTITY | The action discovered this fact. |
| `SYNTHESIZES_TO` | ENTITY → ANSWER | This fact contributed to the answer. |
| `BUILDS_ON` | QUERY → QUERY | This query refines a previous one. |
| `CITES` | any → WEB_SOURCE/PAPER/ENTITY | References a source or fact. |
| `DEFINES` | WEB_SOURCE/PAPER → CONCEPT | Source defines or introduces a concept. |
| `SUPPORTS` | WEB_SOURCE/PAPER → CLAIM | Source provides evidence for a claim. |
| `CONTRADICTS` | WEB_SOURCE/PAPER → CLAIM | Source provides counter-evidence. |
| `ALTERNATIVE_TO` | PROJECT → PROJECT | Competing or substitute project. |
| `DEPRECATED_BY` | PROJECT → PROJECT | Superseded by a newer project. |
| `DEPENDS_ON` | PROJECT → PROJECT | Runtime or build dependency. |
| `AUTHORED_BY` | any → AUTHOR | Attribution to creator. |
| `REJECTS` | DECISION → any | Evaluated and discarded a proposal or option. |
| `INVALIDATES` | any → any | New information renders old position incorrect. |
| `SUPERSEDES` | any → any | New version replaces old version. |

#### Property Conventions

```json
{
  "name": "string (required)",
  "description": "string (required)",
  "url": "string (for WEB_SOURCE, PAPER, PROJECT)",
  "title": "string (for WEB_SOURCE, PAPER)",
  "accessed_date": "YYYY-MM-DD (when source was accessed)",
  "published_date": "YYYY-MM-DD (when source was published)",
  "claim_text": "string (for CLAIM — the assertion in plain language)",
  "confidence": "float 0.0-1.0 (for CLAIM — evidence strength)",
  "source_id": "string (node ID of the source backing a CLAIM)",
  "version_string": "string semver (for VERSION)",
  "release_date": "YYYY-MM-DD (for VERSION)",
  "status": "string active|deprecated|archived (for PROJECT, VERSION)",
  "organization": "string (for AUTHOR, PROJECT)",
  "language": "string (for PROJECT — programming language)",
  "license": "string (for PROJECT)",
  "decision": "string (for DECISION — the conclusion in plain language)",
  "decision_type": "string architectural|sequencing|scoping|evaluation (for DECISION)",
  "rationale": "string (for DECISION — why this conclusion was reached)",
  "constraints": ["string (for DECISION — what this rules out)"],
  "reversible_by": "string (for DECISION — what would cause revisit, optional)"
}
```

**Extension Requirements:** None (CORE only)

---

## Computation Branch (Data-Flow Pipelines)

**Domain:** Data-flow computation expressed as typed operations over named data flows

**Vocabulary identifier:** `compute_v1`

**Purpose:** Represents computational pipelines as graphs where nodes are operations and edges are data flows. Enables LLMs to describe, validate, and execute data transformations without generating imperative code. Every computational TRUG is a valid TRUG — tools that do not understand `compute_v1` can still read and traverse the graph structurally.

**Graph Root Type:** `PIPELINE`

**When to Use:**
- Describing ETL pipelines, data transformations, or validation flows
- LLM-to-LLM handoff of computational intent (what to compute, not how)
- Code generation from declarative operation graphs
- Validating pipeline structure (type compatibility, acyclicity) before execution

**Node Type Vocabulary:**

| Node Type | Metric Level | Description |
|-----------|-------------|-------------|
| PIPELINE | KILO_PIPELINE | Container for a group of related transforms (organizational) |
| STAGE | DEKA_STAGE | Container for a phase within a pipeline (organizational) |
| FLOW_ENTRY | DEKA_ENTRY | Entry point of a computational flow — no incoming FEEDS edges |
| FLOW_EXIT | DEKA_EXIT | Exit point of a computational flow — no outgoing FEEDS edges |
| TRANSFORM | BASE_TRANSFORM | A computational operation with typed input and output |
| DATA | BASE_DATA | A named, typed data source or sink |

**Edge Relation Vocabulary:**

| Relation | From | To | Description |
|----------|------|----|-------------|
| FEEDS | TRANSFORM, DATA, FLOW_ENTRY | TRANSFORM, DATA, FLOW_EXIT | Data flows from source output to target input |
| ROUTES | TRANSFORM | TRANSFORM, FLOW_EXIT | Conditional flow — edge followed when condition matches output |
| BINDS | DATA | TRANSFORM | Schema binding — DATA node declares the shape of transform input/output |

**Operation Vocabulary (23 operations):**

| # | Operation | Category | Input | Output | Deterministic |
|---|-----------|----------|-------|--------|---------------|
| 1 | `filter` | Filter | `array<T>` | `array<T>` | Yes |
| 2 | `exclude` | Filter | `array<T>` | `array<T>` | Yes |
| 3 | `take` | Filter | `array<T>` | `array<T>` | Yes |
| 4 | `skip` | Filter | `array<T>` | `array<T>` | Yes |
| 5 | `distinct` | Filter | `array<T>` | `array<T>` | Yes |
| 6 | `map` | Transform | `array<T>` | `array<U>` | Yes |
| 7 | `flatten` | Transform | `array<array<T>>` | `array<T>` | Yes |
| 8 | `merge` | Transform | `T, U` (multi-port) | `T ∪ U` | Yes |
| 9 | `split` | Transform | `array<T>` | `array<T>` (multi-port) | Yes |
| 10 | `sort` | Transform | `array<T>` | `array<T>` | Yes |
| 11 | `rename` | Transform | `object` / `array<object>` | Same structure | Yes |
| 12 | `batch` | Transform | `array<T>` | `array<array<T>>` | Yes |
| 13 | `aggregate` | Aggregate | `array<T>` | Scalar / `T` | Yes |
| 14 | `group` | Aggregate | `array<T>` | `array<GroupResult>` | Yes |
| 15 | `branch` | Control | `T` | `T` (routed) | Yes |
| 16 | `match` | Control | `T` | `T` (routed) | Yes |
| 17 | `retry` | Control | `T` | `T` | No |
| 18 | `timeout` | Control | `T` | `T` | No |
| 19 | `read` | I/O | `void` | `T` | No |
| 20 | `write` | I/O | `T` | `void` / metadata | No |
| 21 | `request` | I/O | `T` / `void` | Response | No |
| 22 | `respond` | I/O | `T` | `void` | Yes |
| 23 | `validate` | Assertion | `T` | `T` | Yes |

**Property Conventions:**

TRANSFORM node:
```json
{
  "operation": "string — operation name from vocabulary (required)",
  "parameters": {},
  "description": "string — human-readable description",
  "input_schema": {},
  "output_schema": {}
}
```

DATA node:
```json
{
  "name": "string — human-readable data name",
  "schema": {
    "type": "object | array | string | number | boolean",
    "fields": [],
    "description": "string — what this data represents"
  },
  "source": "string — origin (file, api, literal, parameter)",
  "cardinality": "one | many | optional"
}
```

FLOW_ENTRY node:
```json
{
  "name": "string — entry point name",
  "input_schema": {},
  "description": "string — what this flow accepts"
}
```

FLOW_EXIT node:
```json
{
  "name": "string — exit point name",
  "output_schema": {},
  "description": "string — what this flow produces"
}
```

PIPELINE / STAGE node:
```json
{
  "name": "string — pipeline or stage name",
  "description": "string — purpose",
  "version": "string (optional)"
}
```

**Extension Requirements:**
- `compute` extension required — declares `operation_spec` and `constraint_spec` property structures
- When `compute` extension is declared, TRANSFORM nodes gain optional `operation_spec` (full operation specification) and `constraint_spec` (pre/post conditions, invariants)

**Type System:** Structural type system with 8 primitives (`string`, `number`, `integer`, `decimal`, `boolean`, `null`, `any`, `void`) and 3 compound types (`object`, `array`, `union`). Compatibility determined by shape, not name.

**Validation Rules:** 6 additional rules (10–15) appended to CORE rules 1–9. All 9 CORE rules still apply.

**Full specification:** `TRUGS_COMPUTATION/SPEC_computation.md`

**Example:**
```json
{
  "name": "Customer Order Summary",
  "version": "1.0.0",
  "type": "COMPUTE",
  "dimensions": {
    "data_flow": {
      "description": "Order processing pipeline",
      "base_level": "BASE"
    }
  },
  "capabilities": {
    "extensions": ["compute"],
    "vocabularies": ["compute_v1"],
    "profiles": []
  },
  "nodes": [
    {
      "id": "read_orders",
      "type": "TRANSFORM",
      "properties": {
        "operation": "read",
        "parameters": {"source": "orders.csv", "format": "csv"}
      },
      "parent_id": null,
      "contains": [],
      "metric_level": "BASE_TRANSFORM",
      "dimension": "data_flow"
    },
    {
      "id": "completed_only",
      "type": "TRANSFORM",
      "properties": {
        "operation": "filter",
        "parameters": {
          "predicate": {"field": "status", "op": "eq", "value": "completed"}
        }
      },
      "parent_id": null,
      "contains": [],
      "metric_level": "BASE_TRANSFORM",
      "dimension": "data_flow"
    },
    {
      "id": "by_customer",
      "type": "TRANSFORM",
      "properties": {
        "operation": "group",
        "parameters": {
          "key": "customer_id",
          "aggregates": [
            {"field": "amount", "function": "sum", "alias": "total_spent"},
            {"field": "order_id", "function": "count", "alias": "order_count"}
          ]
        }
      },
      "parent_id": null,
      "contains": [],
      "metric_level": "BASE_TRANSFORM",
      "dimension": "data_flow"
    },
    {
      "id": "write_report",
      "type": "TRANSFORM",
      "properties": {
        "operation": "write",
        "parameters": {"target": "customer_summary.json", "format": "json"}
      },
      "parent_id": null,
      "contains": [],
      "metric_level": "BASE_TRANSFORM",
      "dimension": "data_flow"
    }
  ],
  "edges": [
    {"from_id": "read_orders", "to_id": "completed_only", "relation": "FEEDS"},
    {"from_id": "completed_only", "to_id": "by_customer", "relation": "FEEDS"},
    {"from_id": "by_customer", "to_id": "write_report", "relation": "FEEDS"}
  ]
}
```

---

## AAA Branch (Development Governance)

**Domain:** Development governance — 9-phase issue-sourced development lifecycle for autonomous LLM execution

**Vocabulary identifier:** `aaa_v1`

**Purpose:** Represents a GitHub Issue's 9-phase development specification (VISION → FEASIBILITY → SPECIFICATIONS → ARCHITECTURE → VALIDATION → CODING → TESTING → AUDIT → DEPLOYMENT) as a typed graph. Enables agent-to-agent handoff of development work, rendering deterministic human-readable AAA.md from structured source, and validating development specifications before execution.

**Graph Root Type:** `AAA`

**When to Use:**
- Expressing a GitHub Issue's 9-phase development specification as a typed graph
- Agent-to-agent handoff of development work (PERAGO_CHAT → PORT_PERAGO)
- Rendering human-readable AAA.md from structured source of truth
- Validating development specifications before execution

**Node Type Vocabulary:**

| Node Type | Metric Level | Description |
|-----------|-------------|-------------|
| AAA | KILO_AAA | Root node — the overall development specification |
| PHASE | BASE_PHASE | One of the 7 development phases |
| TASK | CENTI_TASK | A unit of work within a phase |
| RISK | CENTI_RISK | A risk entry from FEASIBILITY — severity, mitigation, source |
| ADR | CENTI_ADR | An architecture decision record — decision, rationale, status |
| DEPENDENCY | CENTI_DEPENDENCY | An external or internal dependency — technology, version, status |
| RESEARCH_SOURCE | MILLI_RESEARCH_SOURCE | A bibliography entry from FEASIBILITY — URL, access date, relevance |
| QUALITY_GATE | CENTI_QUALITY_GATE | A quality gate between phases — condition, status |
| SUB_ISSUE | CENTI_SUB_ISSUE | A tracked sub-issue — number, title, type (A or B), status |
| AUDIT | CENTI_AUDIT | Paired validation for a TASK in the CODING phase — gated checklist (Gate 1: Tests, Gate 2: Coverage, Gate 3: Logic, Gate 4: Integration) |

**Edge Relation Vocabulary:**

| Relation | Description | Example |
|----------|-------------|---------|
| `precedes` | Phase ordering | `phase_vision → phase_feasibility` |
| `depends_on` | Task dependency | `task_api → task_db_schema` |
| `blocked_by` | Phase or task blocked by another | `phase_coding → phase_specifications` |
| `mitigates` | Risk mitigation relationship | `task_retry → risk_timeout` |
| `validates` | Quality gate validates a phase | `gate_tests → phase_coding` |
| `tracks` | Sub-issue tracks a task or phase | `sub_issue_42 → task_widget` |
| `cites` | Research source cited by risk or decision | `risk_deprecation → source_npm` |
| `decides` | ADR decides architectural question | `adr_001 → task_choose_db` |
| `implements` | Task implements a specification | `task_widget → phase_specifications` |
| `audits` | AUDIT node validates a TASK | `audit_renderer → task_renderer` |

Edge direction for `audits`: `from_id` = AUDIT node, `to_id` = TASK node. Example edge: `{"from_id": "audit_renderer", "to_id": "task_renderer", "relation": "audits"}`

**Property Conventions:**

AAA (root node):
```json
{
  "name": "string — issue title",
  "description": "string — one-sentence summary",
  "issue_number": "integer — GitHub issue number",
  "folder": "string — target folder (from folder:* label)",
  "status": "NOT_STARTED | IN_PROGRESS | COMPLETE | BLOCKED",
  "created": "YYYY-MM-DD",
  "labels": ["string"]
}
```

PHASE:
```json
{
  "name": "VISION | FEASIBILITY | SPECIFICATIONS | ARCHITECTURE | VALIDATION | CODING | TESTING | AUDIT | DEPLOYMENT",
  "status": "NOT_STARTED | IN_PROGRESS | COMPLETE | BLOCKED | NOT_APPLICABLE",
  "quality_gate": "✅ | ⏳ | 🔴",
  "blocked_reason": "string (optional)",
  "output": "string — what this phase produces"
}
```

TASK:
```json
{
  "name": "string — task description",
  "status": "NOT_STARTED | IN_PROGRESS | COMPLETE | BLOCKED",
  "priority": "HIGH | MEDIUM | LOW",
  "operation": "string (optional — a compute_v1 operation when this task describes code)",
  "predicate": "string (optional — for FILTER/EXCLUDE operations)",
  "fields": ["string"],
  "parameters": {}
}
```

RISK:
```json
{
  "name": "string — risk description",
  "severity": "LOW | MEDIUM | HIGH | CRITICAL",
  "mitigation": "string",
  "source": "string (optional)"
}
```

ADR:
```json
{
  "name": "string — decision title",
  "decision": "string — what was decided",
  "rationale": "string — why",
  "status": "PROPOSED | ACCEPTED | DEPRECATED | SUPERSEDED",
  "adr_id": "string — e.g., ADR-001"
}
```

DEPENDENCY:
```json
{
  "name": "string — dependency name",
  "type": "INTERNAL | EXTERNAL",
  "version": "string (optional)",
  "status": "ACTIVE | DEPRECATED | UNKNOWN",
  "url": "string (optional)"
}
```

RESEARCH_SOURCE:
```json
{
  "name": "string — short title",
  "url": "string",
  "accessed": "YYYY-MM-DD",
  "relevance": "string — why this source matters"
}
```

QUALITY_GATE:
```json
{
  "name": "string — gate description",
  "condition": "string — what must be true to pass",
  "status": "✅ | ⏳ | 🔴",
  "phase": "string — which phase this gate guards"
}
```

SUB_ISSUE:
```json
{
  "name": "string — sub-issue title",
  "issue_number": "integer (optional — null if not yet created)",
  "type": "A | B",
  "status": "NOT_STARTED | IN_PROGRESS | COMPLETE",
  "pr_number": "integer (optional)"
}
```

AUDIT:
```json
{
  "name": "string — audit description",
  "status": "NOT_STARTED | IN_PROGRESS | PASS | FAIL",
  "gate_1_tests": "string — test pass condition",
  "gate_2_coverage": "string — coverage condition",
  "gate_3_logic": "string — logic review condition",
  "gate_4_integration": "string — integration condition",
  "fix_cycles": "integer — count of fix+retest cycles (max 3)",
  "failure_gate": "string (optional — which gate failed)"
}
```

**CODE+AUDIT Pairing Rule:**

Every TASK node under a CODING phase must have a corresponding AUDIT node linked via an `audits` edge. This requirement is intentionally scoped to CODING because AUDIT nodes are the implementation-quality gate before work proceeds to TESTING. The audit follows a gated sequence:

```
CODE → AUDIT:
  Gate 1: Tests pass?       → NO → FAIL → fix → retest
  Gate 2: Coverage adequate? → NO → FAIL → fix → retest
  Gate 3: Logic correct?     → NO → FAIL → fix → retest
  Gate 4: Integration sound? → NO → FAIL → fix → retest
  ALL PASS → proceed to next phase
```

- Gate 1 (Tests) is the precondition — if tests fail, remaining gates are not evaluated
- Scope: applies to all TASK nodes in CODING phase (implementation and non-implementation) to enforce a uniform quality gate
- Max 3 fix+retest cycles before escalation
- Validation rule: any AAA TRUG where a CODING-phase TASK lacks a corresponding AUDIT node is invalid

**Extension Requirements:**
- None required (CORE only)
- `compute` extension OPTIONAL — when present, TASK nodes with `operation` property are validated against `compute_v1` parameter schemas

**Vocabulary Interaction with `compute_v1`:**
- When both `aaa_v1` and `compute_v1` are declared: TASK nodes with `operation` are validated against `compute_v1` schemas
- When only `aaa_v1` is declared: TASK nodes with `operation` are accepted but not validated against `compute_v1`

**Full specification:** `TRUGS_AAA/VISION_native_trug_aaa.md`

**Example:**
```json
{
  "name": "Calculator",
  "version": "0.1.0",
  "type": "AAA",
  "description": "Simple arithmetic module providing basic operations",
  "dimensions": {
    "development": {
      "description": "9-phase development lifecycle",
      "base_level": "BASE"
    }
  },
  "capabilities": {
    "extensions": [],
    "vocabularies": ["aaa_v1"],
    "profiles": []
  },
  "nodes": [
    {
      "id": "aaa_root",
      "type": "AAA",
      "properties": {
        "name": "Calculator",
        "description": "Simple arithmetic module providing basic operations",
        "folder": "PORT_PERAGO/docs/EXAMPLES/simple_function",
        "status": "IN_PROGRESS",
        "created": "2026-02-12",
        "labels": ["example"]
      },
      "parent_id": null,
      "contains": ["phase_vision", "phase_coding", "phase_testing"],
      "metric_level": "KILO_AAA",
      "dimension": "development"
    },
    {
      "id": "phase_vision",
      "type": "PHASE",
      "properties": {
        "name": "VISION",
        "status": "COMPLETE",
        "quality_gate": "✅",
        "output": "Clear vision: simple calculator module with basic arithmetic"
      },
      "parent_id": "aaa_root",
      "contains": [],
      "metric_level": "BASE_PHASE",
      "dimension": "development"
    },
    {
      "id": "phase_coding",
      "type": "PHASE",
      "properties": {
        "name": "CODING",
        "status": "NOT_STARTED",
        "quality_gate": "⏳",
        "output": "calculator.py with add() function"
      },
      "parent_id": "aaa_root",
      "contains": ["task_create_calculator", "audit_task_create_calculator"],
      "metric_level": "BASE_PHASE",
      "dimension": "development"
    },
    {
      "id": "task_create_calculator",
      "type": "TASK",
      "properties": {
        "name": "Create calculator.py with add(a, b) -> float",
        "status": "NOT_STARTED",
        "priority": "HIGH"
      },
      "parent_id": "phase_coding",
      "contains": [],
      "metric_level": "CENTI_TASK",
      "dimension": "development"
    },
    {
      "id": "audit_task_create_calculator",
      "type": "AUDIT",
      "properties": {
        "name": "Audit calculator add() task",
        "status": "NOT_STARTED",
        "gate_1_tests": "pytest passes for calculator tests",
        "gate_2_coverage": "Coverage >= 90%",
        "gate_3_logic": "Review confirms add() behavior is correct",
        "gate_4_integration": "Module integrates with CLI usage path",
        "fix_cycles": 0
      },
      "parent_id": "phase_coding",
      "contains": [],
      "metric_level": "CENTI_AUDIT",
      "dimension": "development"
    },
    {
      "id": "phase_testing",
      "type": "PHASE",
      "properties": {
        "name": "TESTING",
        "status": "NOT_STARTED",
        "quality_gate": "⏳",
        "output": "All tests pass"
      },
      "parent_id": "aaa_root",
      "contains": ["gate_tests_passing"],
      "metric_level": "BASE_PHASE",
      "dimension": "development"
    },
    {
      "id": "gate_tests_passing",
      "type": "QUALITY_GATE",
      "properties": {
        "name": "All tests passing",
        "condition": "pytest passes with 0 failures",
        "status": "⏳",
        "phase": "TESTING"
      },
      "parent_id": "phase_testing",
      "contains": [],
      "metric_level": "CENTI_QUALITY_GATE",
      "dimension": "development"
    }
  ],
  "edges": [
    {"from_id": "phase_vision", "to_id": "phase_coding", "relation": "precedes"},
    {"from_id": "phase_coding", "to_id": "phase_testing", "relation": "precedes"},
    {"from_id": "audit_task_create_calculator", "to_id": "task_create_calculator", "relation": "audits"},
    {"from_id": "gate_tests_passing", "to_id": "phase_coding", "relation": "validates"}
  ]
}
```

---

---

## Project Tracking Branch

**Domain:** Project planning, epic management, task delegation, and foundational motivation  
**Vocabulary identifier:** `project_tracking`  
**Used in:** `project.trug.json` files (any folder)

---

### Node Vocabulary

| Node Type | Metric Level | Description |
|---|---|---|
| `TRACKER` | `HECTO_TRACKER` | Root node. One per project. Owns all EPICs. |
| `EPIC` | `HECTO_EPIC` | A major initiative grouping related tasks. Maps to a GitHub issue. |
| `TASK` | `BASE_TASK` | A unit of delegable work. Maps to a GitHub sub-issue. |
| `SUBTASK` | `DECI_SUBTASK` | A step within a task. Atomic, not separately issued. |
| `MILESTONE` | `KILO_MILESTONE` | A named checkpoint. Optionally gates task execution. |
| `MOTIVATION` | `HECTO_EPIC` | A foundational principle or insight that grounds the project. Not a task — a reason. Authorized by the author; persisted as graph truth. |
| `PRINCIPLE` | `DECI_PRINCIPLE` | A sub-concept within a MOTIVATION. One named, self-contained idea that can be read and applied independently. Child of MOTIVATION. |

**`MOTIVATION` node — usage rules:**
- Captures a named principle, architectural insight, or design philosophy with system-wide implications
- `properties.statement` — full prose statement of the motivation (required)
- `properties.key_principles` — array of single-sentence distillations (required)
- `properties.origin` — source reference: conversation date, document, or session (required)
- `properties.status` — one of `ESTABLISHED`, `PROPOSED`, `DEPRECATED`
- `parent_id` — must be an `EPIC` (typically the foundations epic) or `TRACKER`
- `contains` — list of `PRINCIPLE` node IDs, or `[]` if the motivation is not yet decomposed
- A MOTIVATION node is **not a task** — it has no `github_issue`, no `effort`, no `priority`
- MOTIVATION nodes are never erased by cleanup tools — they are the permanent record of intent

**`PRINCIPLE` node — usage rules:**
- `parent_id` — must be a `MOTIVATION` node
- `properties.statement` — full prose statement of the principle (required)
- `properties.status` — one of `ESTABLISHED`, `PROPOSED`, `DEPRECATED`
- `contains` — always `[]`; PRINCIPLE nodes are atomic
- A PRINCIPLE node is **not a task** — it has no `github_issue`, no `effort`, no `priority`
- PRINCIPLE nodes inherit the protection of their parent MOTIVATION: never erased by cleanup tools

---

### Edge Vocabulary

| Relation | From | To | Description |
|---|---|---|---|
| `CONTAINS` | TRACKER / EPIC | EPIC / TASK / SUBTASK / MOTIVATION | Hierarchy ownership |
| `DEPENDS_ON` | TASK | TASK / EPIC | Execution prerequisite |
| `BLOCKS` | TASK / EPIC | TASK / EPIC | Hard blocker — downstream cannot start |
| `INFORMS` | EPIC / MOTIVATION | EPIC / TASK | Provides context or theoretical basis for downstream work |
| `GROUNDS` | MOTIVATION | TRACKER / EPIC | The motivation is the foundational reason the target exists. Stronger than INFORMS — this is the "why" at the root of the project. |
| `EXTENDS` | MOTIVATION | MOTIVATION | One motivation builds on and deepens another. Directional: the newer theory extends the older. |
| `COMPLETES` | TASK | EPIC | Task completion satisfies the epic's acceptance criteria |
| `TRACKS` | EPIC / TASK | EPIC / TASK | Cross-reference between related items |

**`GROUNDS` edge — usage rules:**
- Directionality: `from_id` = MOTIVATION node, `to_id` = TRACKER or top-level EPIC
- One MOTIVATION node may GROUNDS multiple targets
- A TRACKER may have multiple incoming GROUNDS edges (multiple foundational motivations)
- `GROUNDS` is not a dependency — it does not gate execution; it anchors meaning

---

### Property Conventions

**EPIC node required properties:** `name`, `status`, `github_issue`, `github_url`, `created_date`  
**TASK node required properties:** `name`, `status`, `github_issue`, `github_url`, `priority`, `folder`  
**MOTIVATION node required properties:** `name`, `statement`, `key_principles`, `origin`, `status`, `captured_date`  
**PRINCIPLE node required properties:** `name`, `statement`, `status`

**Status values:** `BACKLOG`, `IN_PROGRESS`, `DONE`, `BLOCKED` (for EPIC/TASK); `ESTABLISHED`, `PROPOSED`, `DEPRECATED` (for MOTIVATION/PRINCIPLE)

---

## Summary

**CORE provides:**
- Universal structure (7 node fields, 3 edge fields)
- Hierarchy rules (parent/child, metric ordering)
- Validation (9 mechanical checks)
- Boundaries (7 constraints all TRUGs satisfy)

**BRANCH provides:**
- Node type vocabulary (domain-specific)
- Edge relation vocabulary (domain-specific)
- Property conventions (domain-specific)
- Extension requirements (domain-specific)

**Together:**
```
CORE = Structure (how graphs work)
BRANCH = Vocabulary (what graphs contain)
TRUG = CORE + BRANCH
```

**Key insight:**
- CORE is universal (applies to all domains)
- Branches are domain-specific (apply to one domain)
- CORE validates structure
- Branches define vocabulary
- Both are necessary for complete TRUGs

---

**Next steps:**
- Read ARCHITECTURE.md to understand how CORE creates patterns
- Read SPEC_patterns.md to see the three fundamental patterns
- See EXAMPLES/ for complete working TRUGs
- See individual branch documentation for detailed specifications

---
