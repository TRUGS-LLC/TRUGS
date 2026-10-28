"""Compare local package, README and HTML inputs with COMPATIBILITY.md.

Python 3.11+; standard library only. No files are fetched or written. See
--help for input layout and exit codes. Clause labels C1-C5 and E1 identify
version, specification, requirement, Python, status and history rules.
"""

from __future__ import annotations

import argparse
import json
import os
import posixpath
import re
import sys
from collections.abc import Iterator
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

import tomllib

VERSION = r"\d+(?:\.\d+)+"
BOUND = r"[\w-]"
SPEC_VERSION = r"\d+(?:\.\d+)*"
SPECIFIER = rf"(?:===|==|!=|~=|>=|<=|>|<)\s*{SPEC_VERSION}(?:\.\*)?"
RANGE = rf"{SPECIFIER}(?:\s*,\s*{SPECIFIER})*"
HISTORY = re.compile(
    r"\b(?:as\s+of|since|before|until|legacy|earlier|previously|prior|was|were|had)\b",
    re.IGNORECASE,
)
STATUS = re.compile(
    r"\b(?:under\s+reconstruction|coming|unpublished|unreleased|released|available|live|served|published)\b",
    re.IGNORECASE,
)
CURRENT = {"released", "available", "live", "served", "published"}
SKIP = {".git", "vendor", "private"}
BLOCKS = {
    "h3",
    "h5",
    "fieldset",
    "footer",
    "aside",
    "nav",
    "blockquote",
    "h1",
    "td",
    "details",
    "article",
    "div",
    "figure",
    "dialog",
    "th",
    "hr",
    "h6",
    "p",
    "tr",
    "ul",
    "dt",
    "dd",
    "header",
    "tbody",
    "form",
    "br",
    "pre",
    "ol",
    "section",
    "address",
    "tfoot",
    "dl",
    "figcaption",
    "li",
    "table",
    "h4",
    "h2",
    "main",
    "thead",
}


class InputError(ValueError):
    """An input is absent, malformed or ambiguous."""


@dataclass
class Row:
    repository: str
    package: str
    status: str
    version: str
    python: str
    requirements: dict[str, str]
    package_file: str
    addresses: list[str]

    @property
    def names(self) -> list[str]:
        return sorted({self.repository, self.package} - {"none"}, key=len, reverse=True)

    @property
    def present(self) -> bool:
        return self.status in {"released", "live"}


@dataclass
class Table:
    specification: str
    rows: list[Row]

    def row(self, name: str) -> Row:
        for row in self.rows:
            if name.lower() in [n.lower() for n in row.names]:
                return row
        raise InputError(f"unknown component: {name}")


def version(value: str) -> tuple[int, ...]:
    return tuple(int(n) for n in value.split("."))


def agrees(left: str, right: str) -> bool:
    a, b = version(left), version(right)
    return a[: min(len(a), len(b))] == b[: min(len(a), len(b))]


def clause_set(value: str) -> set[tuple[str, str]]:
    parts = value.strip().strip("()").split(",")
    result = set()
    for part in parts:
        match = re.fullmatch(
            rf"\s*(===|==|!=|~=|>=|<=|>|<)\s*({SPEC_VERSION}(?:\.\*)?)\s*", part
        )
        if not match:
            raise InputError(f"unsupported requirement: {value}")
        result.add((match[1], match[2]))
    return result


def admits(spec: str, current: str) -> bool:
    def padded(v: str) -> tuple[int, ...]:
        return version(v) + (0,) * (8 - len(version(v)))

    actual = padded(current)
    for op, wanted in clause_set(spec):
        if wanted.endswith(".*"):
            equal = version(current)[: len(version(wanted[:-2]))] == version(
                wanted[:-2]
            )
            if op not in {"==", "!="}:
                raise InputError(f"unsupported wildcard: {spec}")
            if equal != (op == "=="):
                return False
            continue
        expected = padded(wanted)
        if op in {"==", "==="} and actual != expected:
            return False
        if op == "!=" and actual == expected:
            return False
        if op == ">=" and actual < expected:
            return False
        if op == ">" and actual <= expected:
            return False
        if op == "<=" and actual > expected:
            return False
        if op == "<" and actual >= expected:
            return False
        if op == "~=":
            prefix = list(version(wanted)[:-1])
            prefix[-1] += 1
            upper = tuple(prefix) + (0,) * (8 - len(prefix))
            if not expected <= actual < upper:
                return False
    return True


def requirement(value: str) -> tuple[str, str] | None:
    match = re.match(rf"\s*([\w-]+)(?:\[[^]]+\])?\s*(\(?{RANGE}\)?)", value)
    return (match[1].lower(), match[2].strip("()")) if match else None


def read_table(path: Path) -> Table:
    text = path.read_text(encoding="utf-8")
    header = re.search(rf"^Specification:\s*({VERSION})\s*$", text, re.MULTILINE)
    if not header:
        raise InputError("table lacks Specification header")
    rows = []
    for line in text.splitlines():
        if not line.startswith("| "):
            continue
        cells = [c.strip().strip("`") for c in line.strip("|").split("|")]
        if len(cells) != 8 or cells[2] not in {
            "released",
            "live",
            "coming",
            "withdrawn",
        }:
            continue
        repo, package, status, ver, minimum, requires, package_file, addresses = cells
        reqs = {}
        if requires != "none":
            for item in requires.split(";"):
                pair = requirement(item)
                if not pair:
                    raise InputError(f"invalid table requirement: {item}")
                clause_set(pair[1])
                reqs[pair[0]] = pair[1]
        if status in {"released", "live"}:
            if ver != "none" and not re.fullmatch(VERSION, ver):
                raise InputError(f"invalid table version: {repo}")
            if minimum != "none" and not re.fullmatch(VERSION, minimum):
                raise InputError(f"invalid table minimum: {repo}")
            if package_file != "none" and (
                Path(package_file).is_absolute() or ".." in Path(package_file).parts
            ):
                raise InputError(f"invalid package file: {repo}")
        rows.append(
            Row(
                repo,
                package,
                status,
                ver,
                minimum,
                reqs,
                package_file,
                addresses.split(),
            )
        )
    if not rows or len({r.repository.lower() for r in rows}) != len(rows):
        raise InputError("table is empty or has duplicate rows")
    table = Table(header[1], rows)
    if not agrees(table.specification, table.row("trugs").version):
        raise InputError("table specification and trugs row differ")
    return table


@dataclass
class Text:
    value: str = ""
    lines: list[int] = field(default_factory=list)
    coded: list[bool] = field(default_factory=list)
    historical: list[bool] = field(default_factory=list)

    def append(
        self, text: str, line: int, code: bool = False, history: bool = False
    ) -> None:
        self.value += text
        self.lines.extend(line + text[:i].count("\n") for i in range(len(text)))
        self.coded.extend([code] * len(text))
        self.historical.extend([history] * len(text))


def markdown(source: str) -> Text:
    """Keep source line locations while expanding links and removing markup."""
    result = Text()
    references = {}
    definition_lines = set()
    definition_fence = ""
    for number, raw in enumerate(source.splitlines(), 1):
        marker = re.match(r"\s*(`{3,}|~{3,})", raw)
        if marker:
            definition_fence = (
                ""
                if definition_fence and marker[1][0] == definition_fence
                else marker[1][0]
            )
        if not definition_fence:
            definition = re.match(r"^\s{0,3}\[([^]]+)\]:\s*(?:<([^>]+)>|(\S+))", raw)
            if definition:
                references[" ".join(definition[1].lower().split())] = (
                    definition[2] or definition[3]
                )
                definition_lines.add(number)
    headings: list[tuple[int, bool]] = []
    fence = ""
    inline_tick = ""
    skip_underline = False
    raw_lines = source.splitlines(keepends=True)
    for number, raw in enumerate(raw_lines, 1):
        if number in definition_lines:
            result.append("\n\n", number)
            continue
        if skip_underline:
            skip_underline = False
            continue
        if not fence and number < len(raw_lines) and raw.strip():
            underline = re.fullmatch(r"\s{0,3}(=+|-+)\s*", raw_lines[number])
            if underline:
                raw = ("# " if underline[1][0] == "=" else "## ") + raw
                skip_underline = True
        marker = re.match(r"\s*(`{3,}|~{3,})", raw)
        if marker:
            fence = "" if fence and marker[1][0] == fence else marker[1][0]
            result.append("\n\n", number)
            continue
        heading = re.match(r"^\s{0,3}(#{1,6})\s+(.+)", raw) if not fence else None
        if heading:
            level = len(heading[1])
            while headings and headings[-1][0] >= level:
                headings.pop()
            headings.append(
                (
                    level,
                    bool(
                        re.search("change|history|release", heading[2], re.IGNORECASE)
                    ),
                )
            )
            result.append("\n\n", number)
            raw = heading[2] + "\n\n"
        elif re.match(r"^\s*(?:[-+*]|\d+[.)])\s", raw) and not fence:
            result.append("\n\n", number)
        history = any(h[1] for h in headings)
        raw = re.sub(r"!?\[([^]]+)\]\(([^)]+)\)", r"\1 \2", raw)

        def expand_reference(match: re.Match[str]) -> str:
            label = match[2] or match[1] if match.lastindex == 2 else match[1]
            target = references.get(" ".join(label.lower().split()))
            return match[1] + " " + target if target else match[0]

        raw = re.sub(r"!?\[([^]]+)\]\[([^]]*)\]", expand_reference, raw)
        raw = re.sub(r"(?<!!)\[([^]]+)\](?!\[|\()", expand_reference, raw)
        raw = re.sub(r"(\*{1,3})(?=\S)(.+?)(?<=\S)\1", r"\2", raw)
        raw = re.sub(r"(?<!\w)(_{1,3})(?=\S)(.+?)(?<=\S)\1(?!\w)", r"\2", raw)
        pieces = re.split(r"(`+)", raw)
        for i, piece in enumerate(pieces):
            if not fence and re.fullmatch(r"`+", piece):
                if inline_tick == piece:
                    inline_tick = ""
                    continue
                if not inline_tick:
                    remainder = "".join(pieces[i + 1 :]) + "".join(raw_lines[number:])
                    if re.search(r"(?<!`)" + re.escape(piece) + r"(?!`)", remainder):
                        inline_tick = piece
                        continue
            result.append(piece, number, bool(fence or inline_tick), history)
    return result


class Page(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.text = Text()
        self.links: list[tuple[int, str]] = []
        self.hidden = 0
        self.code = 0
        self.headings: list[tuple[int, bool]] = []
        self.heading: tuple[int, str] | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"script", "style"}:
            self.hidden += 1
        if self.hidden:
            return
        line = self.getpos()[0]
        if tag in BLOCKS:
            self.text.append("\n\n", line)
        if re.fullmatch("h[1-6]", tag):
            level = int(tag[1])
            while self.headings and self.headings[-1][0] >= level:
                self.headings.pop()
            self.heading = (level, "")
        if tag in {"code", "pre"}:
            self.code += 1
        href = dict(attrs).get("href")
        if href:
            self.links.append((line, href))

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style"}:
            self.hidden = max(0, self.hidden - 1)
            return
        if self.hidden:
            return
        if re.fullmatch("h[1-6]", tag) and self.heading:
            level, value = self.heading
            self.headings.append(
                (level, bool(re.search("change|history|release", value, re.IGNORECASE)))
            )
            self.heading = None
        if tag in {"code", "pre"}:
            self.code = max(0, self.code - 1)
        if tag in BLOCKS:
            self.text.append("\n\n", self.getpos()[0])

    def handle_data(self, data: str) -> None:
        if self.hidden:
            return
        if self.heading:
            self.heading = (self.heading[0], self.heading[1] + data)
        self.text.append(
            data, self.getpos()[0], bool(self.code), any(h[1] for h in self.headings)
        )


def names(row: Row) -> str:
    return rf"(?<!{BOUND})(?:{'|'.join(re.escape(n) for n in row.names)})(?!{BOUND})"


def address(value: str) -> str:
    return re.sub(r"^(?:[a-z][a-z0-9+.-]*:)?//", "", value.lower()).rstrip("/")


def clauses(text: Text) -> Iterator[tuple[int, str, str, bool]]:
    # A single wrapped line remains in its clause. Dots within versions/URLs do too.
    visible_source = "".join(
        " " if code else char for char, code in zip(text.value, text.coded)
    )
    visible_source = re.sub(
        r'"[^"]*"|“[^”]*”|‘[^’]*’|(?<!\w)\x27[^\x27]*\x27(?!\w)',
        lambda m: " " * len(m[0]),
        visible_source,
    )
    start = 0
    for end in re.finditer(r"[.?!](?=\s|$)|;|\||\n\s*\n|$", text.value):
        stop = end.start()
        value = text.value[start:stop]
        visible = visible_source[start:stop]
        if value.strip():
            yield start, value, visible, any(text.historical[start:stop])
        start = end.end()


def inspect_text(
    text: Text, own: Row | None, table: Table
) -> list[tuple[int, str, str, str]]:
    findings: list[tuple[int, str, str, str]] = []

    def report(start: int, offset: int, rule: str, claimed: str, expected: str) -> None:
        findings.append((text.lines[start + offset], rule, claimed, expected))

    for start, value, visible, historical in clauses(text):
        exempt = historical or bool(HISTORY.search(value))
        # Read complete addresses so a foreign host's path cannot name this site.
        addresses = [
            address(match[0])
            for match in re.finditer(
                r"(?:[a-z][a-z0-9+.-]*://|//)?[\w.-]+(?:[/:?#@%][^\s<>\"'`|]*)?",
                value,
                re.IGNORECASE,
            )
        ]
        for row in table.rows:
            pattern = names(row)
            if row.version != "none" and not exempt:
                for match in re.finditer(
                    rf"{pattern}\s+(?:v\s*)?({VERSION})(?![\w.])", value, re.IGNORECASE
                ):
                    if not agrees(match[1], row.version):
                        report(
                            start,
                            match.start(),
                            "C1",
                            match[0],
                            f"{row.repository} {row.version}",
                        )
                if row.package != "none":
                    for match in re.finditer(
                        rf"/project/{re.escape(row.package)}/({VERSION})/",
                        value,
                        re.IGNORECASE,
                    ):
                        if not agrees(match[1], row.version):
                            report(start, match.start(), "C1", match[0], row.version)
            if row.package != "none" and row.version != "none":
                for match in re.finditer(
                    rf"{pattern}\s*(\(?{RANGE}\)?)", value, re.IGNORECASE
                ):
                    if not admits(match[1].strip("()"), row.version):
                        report(
                            start,
                            match.start(),
                            "C3",
                            match[0],
                            f"admits {row.version}",
                        )
            # Bare TRUGS has no status meaning; its public address still does.
            mentioned = (
                bool(re.search(pattern, value, re.IGNORECASE))
                if row.repository.lower() != "trugs"
                else False
            )
            mentioned = mentioned or any(
                found == address(a) or found.startswith(address(a) + "/")
                for a in row.addresses
                if a != "none"
                for found in addresses
            )
            if mentioned:
                for match in STATUS.finditer(visible):
                    word = match[0].lower()
                    is_current = word in CURRENT and not re.search(
                        r"\bnot\b", visible[: match.start()], re.IGNORECASE
                    )
                    if row.present != is_current:
                        report(
                            start,
                            match.start(),
                            "C5",
                            f"{row.repository} {match[0]}",
                            row.status,
                        )
        if not exempt:
            spec_word = r"(?:specification|spec\s+revision)"
            patterns = [
                rf"{spec_word}\s*(?:version\s*)?:?\s*v?({VERSION})",
                rf"({VERSION})\s+{spec_word}",
            ]
            for pattern in patterns:
                for match in re.finditer(pattern, value, re.IGNORECASE):
                    if not agrees(match[1], table.specification):
                        report(
                            start, match.start(), "C2", match[0], table.specification
                        )
            if own and own.version != "none":
                for match in re.finditer(
                    rf"\b(?:Version:|package\s+version)\s*v?({VERSION})",
                    value,
                    re.IGNORECASE,
                ):
                    if not agrees(match[1], own.version):
                        report(start, match.start(), "C1", match[0], own.version)
        for match in re.finditer(
            rf"\bPython\s+(?:>=\s*)?({VERSION})", value, re.IGNORECASE
        ):
            targets = [
                r
                for r in table.rows
                if r.package != "none" and re.search(names(r), value, re.IGNORECASE)
            ]
            targets = targets or ([own] if own else [])
            minima = [(r.repository, r.python) for r in targets if r.python != "none"]
            if not minima:
                minima = [
                    (
                        "released packages",
                        max(
                            (
                                r.python
                                for r in table.rows
                                if r.status == "released" and r.python != "none"
                            ),
                            key=version,
                        ),
                    )
                ]
            for label, minimum in minima:
                if version(match[1]) != version(minimum):
                    report(
                        start,
                        match.start(),
                        "C4",
                        match[0],
                        f"{label} Python {minimum}",
                    )
    return list(dict.fromkeys(findings))


def files(root: Path) -> Iterator[Path]:
    if "private" in root.parts:
        raise InputError("excluded input directory")
    for directory, subdirs, filenames in os.walk(root, followlinks=False):
        subdirs[:] = sorted(
            d
            for d in subdirs
            if d not in SKIP and not (Path(directory) / d).is_symlink()
        )
        for name in sorted(filenames):
            path = Path(directory) / name
            if not path.is_symlink():
                yield path


def package_data(path: Path) -> dict[str, Any]:
    if path.name == "package.json":
        data = json.loads(path.read_text(encoding="utf-8"))
        return {
            "name": data.get("name"),
            "version": data.get("version"),
            "dependencies": list(data.get("dependencies", {})),
        }
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    return dict(data.get("project", data.get("package", {})))


def metadata_findings(
    data: dict[str, Any], row: Row, table: Table
) -> list[tuple[str, str, str]]:
    result = []
    if data.get("name", row.package).lower() != row.package.lower():
        raise InputError(f"metadata package name differs from table: {row.repository}")
    ver = data.get("version")
    if row.version != "none" and (
        not isinstance(ver, str) or not re.fullmatch(VERSION, ver)
    ):
        raise InputError(f"missing or invalid metadata version: {row.repository}")
    if ver and row.version != "none" and not agrees(ver, row.version):
        result.append(("C1", str(ver), row.version))
    minimum = data.get("requires-python")
    if row.python != "none":
        if not isinstance(minimum, str):
            raise InputError(f"missing Python minimum: {row.repository}")
        match = re.search(rf"(?:>=|>|==|~=)\s*({VERSION})", minimum)
        if not match:
            raise InputError(f"unsupported Python minimum: {minimum}")
        if version(match[1]) != version(row.python):
            result.append(("C4", minimum, row.python))
    dependencies = list(data.get("dependencies", []))
    for values in data.get("optional-dependencies", {}).values():
        dependencies.extend(values)
    observed: dict[str, str] = {}
    for dependency in dependencies:
        pair = requirement(dependency)
        if pair and any(pair[0].lower() == r.package.lower() for r in table.rows):
            name, spec = pair
            observed[name] = spec
            target = table.row(name)
            expected = row.requirements.get(name)
            if (
                not admits(spec, target.version)
                or expected is None
                or clause_set(spec) != clause_set(expected)
            ):
                result.append(
                    ("C3", dependency, f"{name}{expected or ' (no requirement)'}")
                )
        elif any(
            re.match(rf"{re.escape(r.package)}(?:\W|$)", dependency, re.IGNORECASE)
            for r in table.rows
            if r.package != "none"
        ):
            result.append(("C3", dependency, "bounded table requirement"))
    for name, spec in row.requirements.items():
        if name not in observed:
            result.append(("C3", f"missing {name}", f"{name}{spec}"))
    return result


def metadata_line(source: str, rule: str, claimed: str) -> int:
    needle = (
        "version" if rule == "C1" else "requires-python" if rule == "C4" else claimed
    )
    return next(
        (i for i, line in enumerate(source.splitlines(), 1) if needle in line), 1
    )


def linked_page(href: str, relative: str) -> str | None:
    href = href.split("#", 1)[0].split("?", 1)[0]
    if href.startswith("//"):
        href = "https:" + href
    match = re.match(r"^https?://([^/]+)(/.*)?$", href, re.IGNORECASE)
    if match:
        if match[1].lower() != "trugs.ai":
            return None
        href = match[2] or "/"
    elif re.match(r"^[\w+.-]+:", href):
        return None
    if not href or not href.endswith(("/", ".html")):
        return None
    joined = posixpath.normpath(
        href.lstrip("/")
        if href.startswith("/")
        else posixpath.join(posixpath.dirname(relative), href)
    )
    if joined.startswith("../") or joined == ".." or "private" in Path(joined).parts:
        raise InputError("page link leaves the input tree")
    return (
        posixpath.normpath(posixpath.join(joined, "index.html"))
        if href.endswith("/")
        else joined
    )


def check(
    table: Table, repositories: dict[str, Path], index: Path, site: Path
) -> list[str]:
    errors = []

    def scan(path: str, text: Text, own: Row) -> None:
        for line, rule, claimed, expected in inspect_text(text, own, table):
            errors.append(
                f"{path}:{line}: {rule}: claimed={claimed!r}; expected={expected!r}"
            )

    for row in table.rows:
        if not row.present:
            continue
        if row.repository not in repositories:
            raise InputError(f"missing repository root: {row.repository}")
        root = repositories[row.repository]
        entries = list(files(root))
        if root / "README.md" not in entries:
            raise InputError(f"missing {root / 'README.md'}")
        if row.package_file != "none" and root / row.package_file not in entries:
            raise InputError(f"missing {root / row.package_file}")
        for path in entries:
            if path.name == "README.md":
                scan(str(path), markdown(path.read_text(encoding="utf-8")), row)
            if path.name in {"pyproject.toml", "package.json", "Cargo.toml"}:
                source = path.read_text(encoding="utf-8")
                scan(str(path), markdown(source), row)
                for rule, claimed, expected in metadata_findings(
                    package_data(path), row, table
                ):
                    errors.append(
                        f"{path}:{metadata_line(source, rule, claimed)}: {rule}: claimed={claimed!r}; expected={expected!r}"
                    )
        if row.status == "released":
            path = index / f"{row.package}.json"
            if not path.is_file():
                raise InputError(f"missing {path}")
            source = path.read_text(encoding="utf-8")
            data = json.loads(source)["info"]
            if data.get("name", "").lower() != row.package.lower() or not isinstance(
                data.get("description"), str
            ):
                raise InputError(f"invalid index info: {path}")
            values = {
                "version": data.get("version"),
                "requires-python": data.get("requires_python"),
                "dependencies": data.get("requires_dist") or [],
            }
            for rule, claimed, expected in metadata_findings(values, row, table):
                errors.append(
                    f"{path}:1: {rule}: claimed={claimed!r}; expected={expected!r}"
                )
            scan(f"{path} info.description", markdown(data["description"]), row)
    pages = {str(p.relative_to(site)): p for p in files(site) if p.suffix == ".html"}
    if "index.html" not in pages:
        raise InputError(f"missing {site / 'index.html'}")
    for relative, path in sorted(pages.items()):
        parser = Page()
        parser.feed(path.read_text(encoding="utf-8"))
        scan(str(path), parser.text, table.row("TRUGS-SITE"))
        for line, href in parser.links:
            needed = linked_page(href, relative)
            if needed and needed not in pages:
                raise InputError(f"{path}:{line}: missing linked page {needed}")
    return sorted(set(errors))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__,
        epilog="Exit 0: no disagreements; 1: disagreements; 2: usage or incomplete input. All inputs must be local. A run says nothing about publication order or completion.",
    )
    parser.add_argument(
        "--table",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "COMPATIBILITY.md",
    )
    parser.add_argument(
        "--repositories",
        type=Path,
        help="parent of repository directories named by the table",
    )
    parser.add_argument(
        "--repo",
        action="append",
        default=[],
        metavar="NAME=PATH",
        help="explicit repository root; overrides --repositories",
    )
    parser.add_argument(
        "--index",
        type=Path,
        required=True,
        help="directory of PACKAGE.json index snapshots",
    )
    parser.add_argument(
        "--site",
        type=Path,
        required=True,
        help="local site tree, including index.html and all same-site linked pages",
    )
    args = parser.parse_args(argv)
    try:
        table = read_table(args.table)
        repositories = (
            {
                r.repository: args.repositories / r.repository
                for r in table.rows
                if r.present
            }
            if args.repositories
            else {}
        )
        for item in args.repo:
            name, separator, value = item.partition("=")
            if not separator or not value:
                raise InputError("--repo requires NAME=PATH")
            repositories[table.row(name).repository] = Path(value)
        errors = check(table, repositories, args.index, args.site)
    except (OSError, ValueError, KeyError, TypeError) as problem:
        print(f"incomplete input: {problem}", file=sys.stderr)
        return 2
    for error in errors:
        print(error)
    return int(bool(errors))


if __name__ == "__main__":
    sys.exit(main())
