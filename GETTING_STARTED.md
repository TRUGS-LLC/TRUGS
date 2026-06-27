# Getting Started with TRUGS

TRUG/L (TRL) is a constrained subset of English: every valid sentence compiles
to a graph, and every graph decompiles back to the sentence — losslessly. You
write TRL when *communicating* (specs, instructions, acceptance criteria); you
store and validate TRUGS (the JSON graph) when *executing*. The sentence is the
graph.

This guide takes you from `pip install` to your first `VALID` verdict in about
five minutes. No prior TRUGS knowledge is assumed.

## 1. Install

```bash
pip install trugs-tools trugs-folder
```

This gives you two commands:

- `trug` — the language CLI: validate TRUG graphs, compile and decompile TRL.
- `trug-a-folder` — the cartography tool: keep a directory and its graph in sync.

## 2. Your first sentence

Write a TRL sentence to a file:

```bash
cat > hello.trl <<'EOF'
PARTY api SHALL FILTER ALL ACTIVE RECORD THEN WRITE RESULT TO ENDPOINT output.
EOF
```

That's an actor (`PARTY api`), an obligation (`SHALL`), two chained operations
(`FILTER … THEN WRITE`), and a target (`TO ENDPOINT output`). Compile it:

```bash
trug trl compile hello.trl > hello.trug.json
```

Open `hello.trug.json`: the sentence became nodes (the party, the operations,
the record, the endpoint) and edges (who does what, where results flow). Now
decompile the graph:

```bash
trug trl decompile hello.trug.json
```

You get your sentence back. That round trip — sentence → graph → sentence,
nothing lost — is the core of TRUGS.

## 3. Your first VALID verdict

A compiled fragment is just a graph body. A full TRUG document wraps it in an
envelope (`name`, `version`, `type`, declared `dimensions`) and gives every
node seven core fields. Write a minimal complete one:

```bash
cat > first.trug.json <<'EOF'
{
  "name": "first-graph",
  "version": "1.0.0",
  "type": "PROJECT",
  "dimension": "system",
  "dimensions": { "system": { "description": "My first TRUG graph" } },
  "nodes": [
    {
      "id": "api",
      "type": "PARTY",
      "properties": { "modal": "SHALL" },
      "parent_id": null,
      "contains": [],
      "metric_level": "BASE_PARTY",
      "dimension": "system"
    }
  ],
  "edges": []
}
EOF
trug validate first.trug.json
```

```
VALID  first.trug.json
```

`VALID` means all sixteen CORE rules pass. Break something — change the
node's `"dimension": "system"` to a dimension the envelope never declared —
and `trug validate` tells you exactly which rule failed and why:

```
INVALID  first.trug.json
  ERROR UNDECLARED_DIMENSION: Node 'api' uses undeclared dimension '...'
```

Validation is how TRUGS keeps graphs trustworthy enough to act on.

## 4. Map a real folder

The cartography tool applies the same idea to a directory tree: the folder
*is* a graph. Point it at any project:

```bash
mkdir -p myproject/docs
echo '# My Project'   > myproject/README.md
echo 'notes'          > myproject/docs/notes.md
echo 'print("hi")'    > myproject/app.py

trug-a-folder init myproject --scan -d "My first mapped folder"
trug-a-folder check myproject
trug-a-folder render architecture myproject
```

`init --scan` writes `myproject/folder.trug.json` — one node per file, typed
by the folder governance vocabulary (code is `COMPONENT`, prose is
`DOCUMENT`). `check` validates the graph against that vocabulary and the
filesystem. `render architecture` turns the graph into a human-readable
`ARCHITECTURE.md`. When files change, `trug-a-folder sync` reconciles the
graph instead of you editing JSON by hand.

## 5. Where to go next

- **The cheatsheet:** [TRUGS_LANGUAGE/CHEATSHEET.md](TRUGS_LANGUAGE/CHEATSHEET.md) — the whole language on one page.
- **The vocabulary:** [TRUGS_LANGUAGE/SPEC_vocabulary.md](TRUGS_LANGUAGE/SPEC_vocabulary.md) — all 233 executable words across 9 parts of speech.
- **The grammar:** [TRUGS_LANGUAGE/SPEC_grammar.md](TRUGS_LANGUAGE/SPEC_grammar.md) — sentence forms and compilation rules.
- **Worked examples:** [TRUGS_LANGUAGE/SPEC_examples.md](TRUGS_LANGUAGE/SPEC_examples.md) and [EXAMPLES/](EXAMPLES/).

Questions or rough edges? Open an issue — this guide is meant to be the
shortest honest path in, and we treat gaps in it as bugs.
