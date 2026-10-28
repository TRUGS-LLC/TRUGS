# Version and compatibility

Specification: 2.0.0

Python 3.10 is the minimum for the specification package trugs. Python 3.11 is the minimum for trugs-tools, trugs-store, trugs-web and trugs-agent. The browser viewer, calculator and static site have no Python minimum.

Each package file is relative to its repository root. Requirements list dependencies on the packages in this table; all other dependencies remain in the package files. A live repository version is its package-file version, without implying an index release.

| Repository | Package | Status | Version | Python minimum | Requirements | Package file | Public addresses |
|---|---|---|---|---|---|---|---|
| TRUGS | trugs | released | 2.0.0 | 3.10 | none | pyproject.toml | https://github.com/TRUGS-LLC/TRUGS |
| TRUGS-TOOLS | trugs-tools | released | 2.4.0 | 3.11 | trugs-store>=2.0.0 | pyproject.toml | https://github.com/TRUGS-LLC/TRUGS-TOOLS |
| TRUGS-STORE | trugs-store | released | 2.2.0 | 3.11 | none | trugs-store/pyproject.toml | https://github.com/TRUGS-LLC/TRUGS-STORE |
| TRUGS-WEB | trugs-web | released | 2.1.0 | 3.11 | trugs-tools>=2.4.0,<3.0.0; trugs-store>=2.0.0,<3.0.0 | pyproject.toml | https://github.com/TRUGS-LLC/TRUGS-WEB |
| TRUGS-AGENT | trugs-agent | released | 2.0.0 | 3.11 | trugs-tools>=2.4.0,<3 | installer/pyproject.toml | https://github.com/TRUGS-LLC/TRUGS-AGENT |
| TRUGS-VIEWER | trugs-viewer | live | 0.1.0 | none | none | package.json | https://github.com/TRUGS-LLC/TRUGS-VIEWER https://trugs-llc.github.io/TRUGS-VIEWER/ |
| TRUGS-ACCOUNTING-CALCULATOR | trugs-accounting-calculator | live | 0.2.0 | none | none | Cargo.toml | https://github.com/TRUGS-LLC/TRUGS-ACCOUNTING-CALCULATOR |
| TRUGS-SITE | none | live | none | none | none | none | https://github.com/TRUGS-LLC/TRUGS-SITE https://trugs.ai/ |
| TRUGS-TRL | none | coming | none | none | none | none | none |
| TRUGS-LAW | none | coming | none | none | none | none | none |
| Govern runner | none | coming | none | none | none | none | none |
| trugs-folder | none | withdrawn | none | none | none | none | none |

The coming and withdrawn rows state only a name and status. The released and live values come from the named package files and, for Python releases, the package index JSON. TRUGS-SITE has no package file.

## Check local inputs

Use Python 3.11 or later. Supply all eight repository roots, the five index JSON files named PACKAGE.json, and a complete local HTML tree. The checker reads every README.md and package file under those roots, excluding .git and vendor/, and every HTML page. It makes no network connections.

```sh
python tools/check_compatibility.py --repositories ./repositories --index ./index-json --site ./site
```

Use repeated `--repo NAME=PATH` options for repositories stored elsewhere. `--table PATH` selects another table. Exit 0 means no disagreements; exit 1 prints each disagreement with its file, line, rule, claim and expected value; exit 2 means usage or incomplete inputs. A site snapshot check does not establish when that site was published.

## Comparison

C1 compares component versions (shorter dot versions agree with their longer prefix). C2 compares specification versions. C3 checks package requirements: prose ranges must admit the current version, and metadata clauses must also equal the owning row’s requirements, independent of clause order. C4 compares Python minima for named packages or the source’s own component. C5 compares current and coming status words, excluding quoted words and code. E1 exempts version and specification history marked in a clause or under a change, history or release heading.
