# TRUGS Language

> Formalized English as an LLM-native executable language.

**Issue:** #1211 | **Status:** DRAFT | **Version:** 1.0.1

## What This Is

TRUGS Language is a constrained subset of English where every valid sentence compiles to a TRUG graph and every graph decompiles back to a sentence. Lossless round-trip.

It is not a new language. It is English with a constraint: **only the precise words are allowed.** The vocabulary draws from two domains that spent centuries eliminating ambiguity: computation and law.

## How It Works

1. Every LLM conversation begins by loading an **opening TRUG** — a graph that defines the valid words, grammar rules, and constraints for that session
2. The human writes sentences using only the words in the opening TRUG
3. The LLM compiles each sentence into a TRUG graph and executes it
4. The graph can be decompiled back to the exact same sentence

The language definition IS a TRUG. TRUGs all the way down.

## Quick Example

```
PARTY api SHALL FILTER ALL ACTIVE RECORD
  THEN SORT RESULT
  THEN TAKE RESULT 10
  THEN WRITE RESULT TO ENDPOINT output
  OR RETRY BOUNDED 3 WITHIN 60s.
```

Every word is from the 190-word vocabulary. The sentence compiles to a graph with 6 nodes and 5 edges. The graph decompiles back to the same sentence.

## The Numbers

- **190 executable words** + `'word` sugar pattern (human readability only)
- **8 parts of speech** — sugar is a pattern (`'[a-z_]+`), not a word list
- **67% computation**, 27% law, 5% shared (executable words)
- **12 validation rules** for compiled graphs
- **No ambiguity** — verbs and prepositions are always distinct words
- **30 examples** tested token-by-token against the grammar

## Files

| File | Purpose |
|------|---------|
| [SPEC_vocabulary.md](SPEC_vocabulary.md) | Complete word list: 190 words, 8 parts of speech, definitions |
| [SPEC_grammar.md](SPEC_grammar.md) | BNF grammar, composition rules, validation rules |
| [SPEC_examples.md](SPEC_examples.md) | 30 parsed examples with token-by-token analysis |
| [language.trug.json](language.trug.json) | The opening TRUG — the language defining itself |

## Relationship to TRUGS

- **TRUGS CORE** defines the 46 semantic primitives (graph vocabulary)
- **TRUGS Language** uses CORE as its seed and adds 144 words to fill the gaps CORE doesn't cover (adjectives, adverbs, conjunctions, articles, pronouns)
- The language tests CORE; CORE tests the language. They educate each other.
- CORE is the grammar invariant. Branches add domain vocabulary. Same architecture.
