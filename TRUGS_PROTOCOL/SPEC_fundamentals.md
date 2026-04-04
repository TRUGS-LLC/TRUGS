# **TRUGS Fundamentals**

**Version:** 1.0.0 (AAA\_AARDVARK)  
 **Purpose:** Core concepts for LLM understanding of TRUGS  
 **Read time:** 8 minutes

---

## **What is a TRUG?**

A TRUG is a JSON file representing structured information as a graph.

**Three components:**

1. **Nodes** \- Things (functions, pages, chapters)  
2. **Edges** \- Relationships (calls, links, references)  
3. **Hierarchy** \- Organization using metric levels

---

## **Minimal Valid TRUG**

{  
  "name": "Hello TRUGS",  
  "version": "1.0.0",  
  "type": "CODE",  
  "dimensions": {  
    "code\_structure": {  
      "description": "Code hierarchy",  
      "base\_level": "BASE"  
    }  
  },  
  "capabilities": {  
    "extensions": \[\],  
    "vocabularies": \[\],  
    "profiles": \[\]  
  },  
  "nodes": \[  
    {  
      "id": "root",  
      "type": "MODULE",  
      "properties": {},  
      "parent\_id": null,  
      "contains": \[\],  
      "metric\_level": "DEKA\_MODULE",  
      "dimension": "code\_structure"  
    }  
  \],  
  "edges": \[\]  
}

---

## **Required Node Fields (7 Fields)**

Every node must have:

{  
  "id": "unique\_string",  
  "type": "FUNCTION",  
  "properties": {},  
  "parent\_id": "parent\_id\_or\_null",  
  "contains": \["child\_ids"\],  
  "metric\_level": "BASE\_FUNCTION",  
  "dimension": "dimension\_name"  
}

| Field | Type | Rules |
| ----- | ----- | ----- |
| `id` | string | Unique within graph |
| `type` | string | From vocabulary |
| `properties` | object | Never null, use `{}` for empty |
| `parent_id` | string|null | `null` for roots |
| `contains` | array | `[]` for leaves |
| `metric_level` | string | Format: `{PREFIX}_{NAME}`, parent ≥ child (same dimension) |
| `dimension` | string | Declared in root dimensions |

---

## **Required Edge Fields (3 Fields)**

Every edge must have:

{  
  "from\_id": "source\_node\_id",  
  "to\_id": "target\_node\_id",  
  "relation": "CALLS"  
}

| Field | Type | Rules |
| ----- | ----- | ----- |
| `from_id` | string | Must reference existing node |
| `to_id` | string | Must reference existing node |
| `relation` | string | From vocabulary |

**Optional:** `weight` (0.0-1.0), `properties` (object)

---

## **Required Graph Fields**

Every TRUG file must have:

{  
  "name": "string",  
  "version": "1.0.0",  
  "type": "CODE|WEB|WRITER|KNOWLEDGE",  
  "dimensions": {  
    "dimension\_name": {  
      "description": "string",  
      "base\_level": "BASE"  
    }  
  },  
  "capabilities": {  
    "extensions": \[\],  
    "vocabularies": \[\],  
    "profiles": \[\]  
  },  
  "nodes": \[\],  
  "edges": \[\]  
}

---

## **Metric Hierarchy System**

### **Concept**

Nodes use metric prefixes for hierarchy positioning:

DEKA\_MODULE     (higher)  
  BASE\_FUNCTION   (middle)  
    CENTI\_STATEMENT (lower)

**Rule:** Parent metric ≥ child metric (same dimension)

### **The Metric System**

TRUGS uses standard SI metric prefixes:

| Prefix | Value | Power | Typical Use |
| ----- | ----- | ----- | ----- |
| **YOTTA** | 10²⁴ | 1e24 | Universal systems |
| **ZETTA** | 10²¹ | 1e21 | Galactic scale |
| **EXA** | 10¹⁸ | 1e18 | Planetary systems |
| **PETA** | 10¹⁵ | 1e15 | Global networks |
| **TERA** | 10¹² | 1e12 | Continental systems |
| **GIGA** | 10⁹ | 1e9 | National infrastructure |
| **MEGA** | 10⁶ | 1e6 | City-scale systems |
| **KILO** | 10³ | 1e3 | Large programs |
| **HECTO** | 10² | 1e2 | Program collections |
| **DEKA** | 10¹ | 1e1 | Packages, modules |
| **BASE** | **10⁰** | **1e0** | **Functions, classes (standard)** |
| **DECI** | 10⁻¹ | 1e-1 | Blocks, scopes |
| **CENTI** | 10⁻² | 1e-2 | Statements |
| **MILLI** | 10⁻³ | 1e-3 | Expressions |
| **MICRO** | 10⁻⁶ | 1e-6 | Operations, operands |
| **NANO** | 10⁻⁹ | 1e-9 | Registers, atoms |
| **PICO** | 10⁻¹² | 1e-12 | Bits, quantum states |
| **FEMTO** | 10⁻¹⁵ | 1e-15 | Sub-quantum |
| **ATTO** | 10⁻¹⁸ | 1e-18 | Theoretical |
| **ZEPTO** | 10⁻²¹ | 1e-21 | Mathematical |
| **YOCTO** | 10⁻²⁴ | 1e-24 | Abstraction |

**Most common (99% of use):**

* MEGA through DEKA (large scale)  
* **BASE** (standard connection point)  
* DECI through MICRO (fine granularity)

### **Format**

Metric levels use format: `{PREFIX}_{SEMANTIC_NAME}`

**Examples:**

"metric\_level": "DEKA\_MODULE"  
"metric\_level": "BASE\_FUNCTION"  
"metric\_level": "CENTI\_STATEMENT"  
"metric\_level": "MILLI\_EXPRESSION"  
"metric\_level": "MICRO\_OPERAND"

**Why this works:**

* Error prevention: Can't typo `CENTI_STATEMENT` like you can typo `0.01` vs `0.001`  
* Self-documenting: `MEGA_SYSTEM` clearly bigger than `KILO_SUBSYSTEM`  
* Universal standard: Metric system already known globally  
* Searchable: Easy to find all CENTI-level nodes

### **Dimensions**

Dimensions are named hierarchies declared at root:

{  
  "dimensions": {  
    "data\_flow": {  
      "description": "Code hierarchy",  
      "base\_level": "BASE"  
    },  
    "network\_topology": {  
      "description": "Infrastructure hierarchy",  
      "base\_level": "BASE"  
    }  
  }  
}

**Multiple dimensions in one graph enable modeling different aspects of same system.**

---

## **Hierarchy Rules**

### **Rule 1: Bidirectional Consistency**

If `node.parent_id = "parent"`, then `parent.contains` must include `node.id`.

{  
  "nodes": \[  
    {"id": "parent", "contains": \["child"\]},  
    {"id": "child", "parent\_id": "parent"}  
  \]  
}

### **Rule 2: Metric Level Ordering**

Parent metric ≥ child metric (within same dimension).

{  
  "nodes": \[  
    {"id": "parent", "metric\_level": "DEKA\_MODULE", "dimension": "code"},  
    {"id": "child", "metric\_level": "BASE\_FUNCTION", "dimension": "code", "parent\_id": "parent"}  
  \]  
}

Valid: DEKA (10) ≥ BASE (1) ✅

### **Rule 3: Same Dimension**

Parent and child must share dimension.

// Valid  
{"id": "parent", "dimension": "code\_structure"},  
{"id": "child", "dimension": "code\_structure", "parent\_id": "parent"}

// Invalid  
{"id": "parent", "dimension": "code\_structure"},  
{"id": "child", "dimension": "network", "parent\_id": "parent"}

### **Rule 4: Root Nodes**

Root nodes: `parent_id: null`, not in any `contains` array.

### **Rule 5: Leaf Nodes**

Leaf nodes: `contains: []`, no children reference them.

---

## **Properties Object**

`properties` contains all node data:

{  
  "id": "func\_add",  
  "type": "FUNCTION",  
  "properties": {  
    "function\_name": "add",  
    "parameters": \["a", "b"\],  
    "type\_info": {  
      "category": "function",  
      "return\_type": {"category": "integer"}  
    }  
  }  
}

**Two categories:**

1. Domain data (function\_name, url, title)  
2. Extensions (type\_info, scope\_info)

**Rules:**

* Always an object (never null)  
* Empty properties use `{}`  
* Property names are domain-specific  
* Values can be any JSON type

---

## **Extension System**

Extensions add optional fields to `properties`.

### **Common Extensions**

| Extension | Field | Use Case |
| ----- | ----- | ----- |
| `typed` | `type_info` | Type systems |
| `scoped` | `scope_info` | Variable scoping |

### **Using Extensions**

**Declare in capabilities:**

{  
  "capabilities": {  
    "extensions": \["typed", "scoped"\]  
  }  
}

**Add to properties:**

{  
  "properties": {  
    "variable\_name": "x",  
    "type\_info": {"category": "integer", "width": 32},  
    "scope\_info": {"location": "local", "mutable": true}  
  }  
}

---

## **Validation Rules**

### **1\. Unique IDs**

All node IDs unique within graph.

### **2\. Valid References**

Edge `from_id` and `to_id` reference existing nodes.

### **3\. Hierarchy Consistency**

Parent's `contains` matches child's `parent_id`.

### **4\. Metric Level Ordering**

Parent metric ≥ child metric (same dimension).

Parse metric prefix to compare:

DEKA (10) ≥ BASE (1) ✅  
BASE (1) ≥ CENTI (0.01) ✅

### **5\. Dimension Declaration**

All node dimensions declared in root `dimensions` object.

### **6\. Required Fields Present**

All 7 node fields, 3 edge fields, 7 graph fields present.

### **7\. Correct Types**

Fields have correct types (string, object, array).

### **8\. Extension Declaration**

Extensions used in nodes declared in `capabilities.extensions`.

### **9\. Metric Level Format**

`metric_level` must be format: `{PREFIX}_{NAME}` where PREFIX is valid metric prefix.

---

## **Complete Example**

{  
  "name": "Simple Function",  
  "version": "1.0.0",  
  "type": "CODE",  
  "dimensions": {  
    "code\_structure": {  
      "description": "Code hierarchy",  
      "base\_level": "BASE"  
    }  
  },  
  "capabilities": {  
    "extensions": \[\],  
    "vocabularies": \["code\_v1"\],  
    "profiles": \[\]  
  },  
  "nodes": \[  
    {  
      "id": "func\_add",  
      "type": "FUNCTION",  
      "properties": {"function\_name": "add"},  
      "parent\_id": null,  
      "contains": \["stmt\_return"\],  
      "metric\_level": "BASE\_FUNCTION",  
      "dimension": "code\_structure"  
    },  
    {  
      "id": "stmt\_return",  
      "type": "STATEMENT",  
      "properties": {"statement\_type": "return"},  
      "parent\_id": "func\_add",  
      "contains": \["expr\_add"\],  
      "metric\_level": "CENTI\_STATEMENT",  
      "dimension": "code\_structure"  
    },  
    {  
      "id": "expr\_add",  
      "type": "EXPRESSION",  
      "properties": {"operation": "add"},  
      "parent\_id": "stmt\_return",  
      "contains": \[\],  
      "metric\_level": "MILLI\_EXPRESSION",  
      "dimension": "code\_structure"  
    }  
  \],  
  "edges": \[  
    {  
      "from\_id": "stmt\_return",  
      "to\_id": "expr\_add",  
      "relation": "CONTAINS"  
    }  
  \]  
}

**Hierarchy:**

func\_add (BASE)  
  └─ stmt\_return (CENTI)  
       └─ expr\_add (MILLI)

**Validation:** ✅ All rules pass  
 **Metric ordering:** BASE (1) ≥ CENTI (0.01) ≥ MILLI (0.001) ✅

---

## **CORE vs BRANCH**

### **What is CORE?**

CORE provides universal structure for all TRUGs:

* 7 required node fields  
* 3 required edge fields  
* Metric hierarchy system  
* Dimensions  
* Properties object  
* Extension system  
* Validation rules

**CORE is domain-agnostic.** It works for code, web, documents, orchestration.

### **What is a BRANCH?**

A BRANCH provides domain-specific vocabulary:

* Node types (FUNCTION, PAGE, CHAPTER)  
* Edge relations (CALLS, LINKS\_TO, REFERENCES)  
* Extension schemas (type\_info, scope\_info)  
* Property conventions (function\_name, url, title)

**BRANCH is domain-specific.** Each domain has its own vocabulary.

### **CORE \+ BRANCH \= Complete TRUG**

TRUG \= CORE (structure) \+ BRANCH (vocabulary)

---

## **Branch Examples**

### **Python CODE Branch**

{  
  "type": "CODE",  
  "dimensions": {  
    "data\_flow": {  
      "description": "Code hierarchy",  
      "base\_level": "BASE"  
    }  
  },  
  "capabilities": {  
    "extensions": \["typed", "scoped"\],  
    "vocabularies": \["compute\_v1"\]  
  },  
  "nodes": \[  
    {  
      "id": "module\_main",  
      "type": "MODULE",  
      "metric\_level": "DEKA\_MODULE",  
      "dimension": "data\_flow"  
    },  
    {  
      "id": "func\_calculate",  
      "type": "FUNCTION",  
      "metric\_level": "BASE\_FUNCTION",  
      "dimension": "data\_flow",  
      "parent\_id": "module\_main"  
    },  
    {  
      "id": "stmt\_return",  
      "type": "STATEMENT",  
      "metric\_level": "CENTI\_STATEMENT",  
      "dimension": "data\_flow",  
      "parent\_id": "func\_calculate"  
    }  
  \]  
}

**CORE elements (universal):**

* Structure: `dimensions`, `capabilities`, `nodes`  
* Node fields: `id`, `type`, `properties`, `parent_id`, `contains`, `metric_level`, `dimension`

**BRANCH elements (Python-specific):**

* Node types: `MODULE`, `FUNCTION`, `STATEMENT`  
* Extensions: `type_info`, `scope_info`  
* Properties: `function_name`, `parameters`

### **WEB Branch**

{  
  "type": "WEB",  
  "dimensions": {  
    "web\_structure": {  
      "description": "Website hierarchy",  
      "base\_level": "BASE"  
    }  
  },  
  "capabilities": {  
    "extensions": \[\],  
    "vocabularies": \["web\_site\_v1"\]  
  },  
  "nodes": \[  
    {  
      "id": "site\_root",  
      "type": "SITE",  
      "metric\_level": "KILO\_SITE",  
      "dimension": "web\_structure"  
    },  
    {  
      "id": "page\_home",  
      "type": "PAGE",  
      "metric\_level": "BASE\_PAGE",  
      "dimension": "web\_structure",  
      "parent\_id": "site\_root",  
      "properties": {"url": "/index.html"}  
    },  
    {  
      "id": "section\_hero",  
      "type": "SECTION",  
      "metric\_level": "CENTI\_SECTION",  
      "dimension": "web\_structure",  
      "parent\_id": "page\_home"  
    }  
  \]  
}

**BRANCH elements (WEB-specific):**

* Node types: `SITE`, `PAGE`, `SECTION`, `ELEMENT`  
* Relations: `LINKS_TO`, `CITES`  
* Properties: `url`, `title`, `html_tag`  
* Extensions: None (uses CORE only)

### **WRITER Branch**

{  
  "type": "WRITER",  
  "dimensions": {  
    "document\_structure": {  
      "description": "Document hierarchy",  
      "base\_level": "BASE"  
    }  
  },  
  "capabilities": {  
    "extensions": \[\],  
    "vocabularies": \["document\_v1"\]  
  },  
  "nodes": \[  
    {  
      "id": "book\_guide",  
      "type": "BOOK",  
      "metric\_level": "MEGA\_BOOK",  
      "dimension": "document\_structure"  
    },  
    {  
      "id": "chapter\_intro",  
      "type": "CHAPTER",  
      "metric\_level": "BASE\_CHAPTER",  
      "dimension": "document\_structure",  
      "parent\_id": "book\_guide",  
      "properties": {"chapter\_number": 1}  
    },  
    {  
      "id": "section\_overview",  
      "type": "SECTION",  
      "metric\_level": "CENTI\_SECTION",  
      "dimension": "document\_structure",  
      "parent\_id": "chapter\_intro"  
    }  
  \]  
}

**BRANCH elements (WRITER-specific):**

* Node types: `BOOK`, `CHAPTER`, `SECTION`, `PARAGRAPH`  
* Relations: `REFERENCES`, `CONTINUES`  
* Properties: `title`, `chapter_number`, `content`  
* Extensions: None (uses CORE only)

---

## **Real-World Example: Rust Program**

{  
  "name": "Rust Web Server",  
  "version": "1.0.0",  
  "type": "CODE",  
  "dimensions": {  
    "data\_flow": {  
      "description": "Code hierarchy",  
      "base\_level": "BASE"  
    }  
  },  
  "capabilities": {  
    "extensions": \["typed", "scoped"\],  
    "vocabularies": \["compute\_v1"\],  
    "profiles": \[\]  
  },  
  "nodes": \[  
    {  
      "id": "crate\_server",  
      "type": "CRATE",  
      "properties": {"crate\_name": "web\_server"},  
      "parent\_id": null,  
      "contains": \["mod\_handlers"\],  
      "metric\_level": "HECTO\_CRATE",  
      "dimension": "data\_flow"  
    },  
    {  
      "id": "mod\_handlers",  
      "type": "MODULE",  
      "properties": {"module\_name": "handlers"},  
      "parent\_id": "crate\_server",  
      "contains": \["func\_handle\_request"\],  
      "metric\_level": "DEKA\_MODULE",  
      "dimension": "data\_flow"  
    },  
    {  
      "id": "func\_handle\_request",  
      "type": "FUNCTION",  
      "properties": {  
        "function\_name": "handle\_request",  
        "type\_info": {  
          "category": "function",  
          "params": \[{"category": "struct", "name": "Request"}\],  
          "return\_type": {"category": "struct", "name": "Response"}  
        }  
      },  
      "parent\_id": "mod\_handlers",  
      "contains": \["stmt\_parse", "stmt\_respond"\],  
      "metric\_level": "BASE\_FUNCTION",  
      "dimension": "data\_flow"  
    },  
    {  
      "id": "stmt\_parse",  
      "type": "STATEMENT",  
      "properties": {"statement\_type": "let"},  
      "parent\_id": "func\_handle\_request",  
      "contains": \[\],  
      "metric\_level": "CENTI\_STATEMENT",  
      "dimension": "data\_flow"  
    },  
    {  
      "id": "stmt\_respond",  
      "type": "STATEMENT",  
      "properties": {"statement\_type": "return"},  
      "parent\_id": "func\_handle\_request",  
      "contains": \[\],  
      "metric\_level": "CENTI\_STATEMENT",  
      "dimension": "data\_flow"  
    }  
  \],  
  "edges": \[  
    {  
      "from\_id": "func\_handle\_request",  
      "to\_id": "stmt\_parse",  
      "relation": "CONTAINS"  
    },  
    {  
      "from\_id": "func\_handle\_request",  
      "to\_id": "stmt\_respond",  
      "relation": "CONTAINS"  
    }  
  \]  
}

**Hierarchy:**

crate\_server (HECTO \= 100\)  
  └─ mod\_handlers (DEKA \= 10\)  
       └─ func\_handle\_request (BASE \= 1\)  
            ├─ stmt\_parse (CENTI \= 0.01)  
            └─ stmt\_respond (CENTI \= 0.01)

---

## **Type System Extension**

The `typed` extension adds type information to nodes.

**Used by:** CODE branches (Python, Rust)

**Declared in capabilities:**

{  
  "capabilities": {  
    "extensions": \["typed"\]  
  }  
}

**Added to properties:**

{  
  "properties": {  
    "type\_info": {  
      "category": "function",  
      "params": \[  
        {"category": "integer", "width": 32},  
        {"category": "integer", "width": 32}  
      \],  
      "return\_type": {"category": "integer", "width": 32}  
    }  
  }  
}

**Type categories:**

* `integer`, `float`, `string`, `boolean`  
* `pointer`, `struct`, `array`, `function`  
* `void`, `dynamic`

**Not used by:** WEB, WRITER branches (no type systems)

---

## **Multi-Dimensional Example**

Multiple hierarchies in one TRUG:

{  
  "name": "Distributed System",  
  "version": "1.0.0",  
  "type": "CODE",  
  "dimensions": {  
    "data\_flow": {  
      "description": "Data flow hierarchy",  
      "base\_level": "BASE"  
    },  
    "network\_topology": {  
      "description": "Infrastructure hierarchy",  
      "base\_level": "BASE"  
    }  
  },  
  "capabilities": {  
    "extensions": \[\],  
    "vocabularies": \["compute\_v1", "infrastructure\_v1"\],  
    "profiles": \[\]  
  },  
  "nodes": \[  
    {  
      "id": "service\_api",  
      "type": "SERVICE",  
      "properties": {"service\_name": "api\_gateway"},  
      "parent\_id": null,  
      "contains": \[\],  
      "metric\_level": "BASE\_SERVICE",  
      "dimension": "data\_flow"  
    },  
    {  
      "id": "server\_prod\_01",  
      "type": "SERVER",  
      "properties": {"hostname": "prod-api-01"},  
      "parent\_id": null,  
      "contains": \[\],  
      "metric\_level": "BASE\_SERVER",  
      "dimension": "network\_topology"  
    }  
  \],  
  "edges": \[  
    {  
      "from\_id": "service\_api",  
      "to\_id": "server\_prod\_01",  
      "relation": "DEPLOYED\_ON",  
      "properties": {"crosses\_dimensions": true}  
    }  
  \]  
}

**Cross-dimensional edges connect different hierarchies.**

---

## **Key Takeaways**

### **CORE (Universal)**

1. 7 required node fields  
2. 3 required edge fields  
3. Metric hierarchy system (21 standard prefixes)  
4. Dimensions (named hierarchies)  
5. Properties object (domain data \+ extensions)  
6. Extension system (optional capabilities)  
7. Validation rules (9 core rules)

### **BRANCH (Domain-Specific)**

1. Node type vocabulary  
2. Edge relation vocabulary  
3. Extension schemas  
4. Property conventions

### **Metric System**

* Format: `{PREFIX}_{SEMANTIC_NAME}`  
* 21 standard SI prefixes (YOTTA through YOCTO)  
* BASE \= 1.0 (standard connection point)  
* Self-documenting, error-proof, universal

### **Together**

CORE \= Structure (how graphs work)  
BRANCH \= Vocabulary (what graphs contain)  
METRIC \= Hierarchy (how nodes organize)  
TRUG \= CORE \+ BRANCH \+ METRIC

---

## **Beyond the Fundamentals**

This document covers CORE concepts \- the universal foundation all TRUGs share.

**There's more:**

**Domain Species:** Specialized TRUGs adapted for specific use cases (SITE, HUB, CODE, ORCHESTRATION, KNOWLEDGE, LIVING, NESTED). Each inherits CORE but adds domain-specific capabilities. Note: HUB is a usage pattern — a root node with a `qualifying_interest` property and weighted edges — not a structural addition to the graph model. TRUGS has two primitives: node and edge. Everything else, including HUB, is built from those two primitives.

**Architectural Patterns:** Three fundamental patterns that underlie all TRUGs (STRUCTURAL, PEER\_GROUPING, CROSS\_CUTTING). Understanding these reveals how TRUGs organize information at the deepest level.

**Branch Extensions:** Domain-specific vocabularies that extend CORE with specialized node types, edge relations, and extension schemas.

You now understand the foundation. The rest builds on what you've learned here.

---

**End of TRUGS Fundamentals v1.0.0 (AAA\_AARDVARK)**

---

**This is the complete version with the metric system that we created together. It's ready to use\!**

