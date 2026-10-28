"""Rule fixtures and complete-tree checks for the offline compatibility reader."""

from __future__ import annotations

import ast
import json
import re
import socket
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pytest

from tools import check_compatibility as checker

FIXTURES = Path(__file__).parent / "fixtures" / "compatibility"
TABLE = Path(__file__).resolve().parents[1] / "COMPATIBILITY.md"
TEXT_CASES = json.loads((FIXTURES / "text.json").read_text())
METADATA_CASES = json.loads((FIXTURES / "metadata.json").read_text())


@pytest.fixture(autouse=True)
def block_sockets(monkeypatch: pytest.MonkeyPatch) -> None:
    def blocked(*args: Any, **kwargs: Any) -> None:
        raise AssertionError("network connection attempted")

    monkeypatch.setattr(socket, "socket", blocked)
    monkeypatch.setattr(socket, "create_connection", blocked)


@pytest.mark.parametrize("case", TEXT_CASES, ids=lambda c: c["case"])
def test_text_rules(case: dict[str, Any]) -> None:
    table = checker.read_table(TABLE)
    own = table.row(case["own"]) if case["own"] else None
    result = checker.inspect_text(checker.markdown(case["text"]), own, table)
    assert sorted({r[1] for r in result}) == case["rules"]


def metadata(row: checker.Row) -> dict[str, Any]:
    data: dict[str, Any] = {"name": row.package, "version": row.version}
    if row.python != "none":
        data["requires-python"] = ">=" + row.python
    data["dependencies"] = [name + spec for name, spec in row.requirements.items()]
    return data


@pytest.mark.parametrize("case", METADATA_CASES, ids=lambda c: c["case"])
def test_metadata_rules(case: dict[str, Any]) -> None:
    table = checker.read_table(TABLE)
    own = table.row(case["own"])
    data = metadata(own)
    data[case["field"]] = case["value"]
    result = checker.metadata_findings(data, own, table)
    assert sorted({r[0] for r in result}) == case["rules"]


def write_metadata(path: Path, row: checker.Row, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.suffix == ".json":
        path.write_text(json.dumps(data))
    else:
        section = "package" if path.name == "Cargo.toml" else "project"
        path.write_text(
            "["
            + section
            + "]\n"
            + "\n".join(k + " = " + json.dumps(v) for k, v in data.items())
            + "\n"
        )


@dataclass
class Tree:
    table: checker.Table
    roots: dict[str, Path]
    index: Path
    site: Path

    def args(self) -> list[str]:
        return [
            "--table",
            str(TABLE),
            "--index",
            str(self.index),
            "--site",
            str(self.site),
        ] + [
            part
            for name, path in self.roots.items()
            for part in ("--repo", f"{name}={path}")
        ]


@pytest.fixture
def tree(tmp_path: Path) -> Tree:
    table = checker.read_table(TABLE)
    roots = {}
    index = tmp_path / "index"
    index.mkdir()
    site = tmp_path / "site"
    site.mkdir()
    (site / "index.html").write_text(
        '<p>TRUGS-WEB is available.</p><a href="/onboard/">Start</a>'
    )
    (site / "onboard").mkdir()
    (site / "onboard/index.html").write_text('<a href="../">Home</a>')
    for row in table.rows:
        if not row.present:
            continue
        root = tmp_path / row.repository
        root.mkdir()
        roots[row.repository] = root
        (root / "README.md").write_text("# " + row.repository + "\n")
        data = metadata(row)
        if row.package_file != "none":
            write_metadata(root / row.package_file, row, data)
        if row.status == "released":
            info = {
                "name": row.package,
                "version": row.version,
                "requires_python": ">=" + row.python,
                "requires_dist": data["dependencies"],
                "description": "# " + row.package,
            }
            (index / (row.package + ".json")).write_text(json.dumps({"info": info}))
    return Tree(table, roots, index, site)


def test_complete_and_unpackaged_inputs(tree: Tree) -> None:
    assert not list(tree.roots["TRUGS-SITE"].glob("*.toml"))
    assert checker.main(tree.args()) == 0


@pytest.mark.parametrize(
    "missing", ["root", "readme", "package", "index", "site", "linked"]
)
def test_incomplete_input(
    tree: Tree, missing: str, capsys: pytest.CaptureFixture[str]
) -> None:
    path = {
        "readme": tree.roots["TRUGS"] / "README.md",
        "package": tree.roots["TRUGS-AGENT"] / "installer/pyproject.toml",
        "index": tree.index / "trugs.json",
        "site": tree.site / "index.html",
        "linked": tree.site / "onboard/index.html",
    }
    if missing == "root":
        del tree.roots["TRUGS"]
    else:
        path[missing].unlink()
    assert checker.main(tree.args()) == 2
    assert "incomplete input" in capsys.readouterr().err


@pytest.mark.parametrize(
    "surface",
    [
        "nested-readme",
        "metadata",
        "extra-metadata",
        "index-readme",
        "index-metadata",
        "page",
        "unlinked-page",
    ],
)
def test_every_surface_is_read(
    tree: Tree, surface: str, capsys: pytest.CaptureFixture[str]
) -> None:
    root = tree.roots["TRUGS-TOOLS"]
    if surface == "nested-readme":
        path = root / "nested/README.md"
        path.parent.mkdir()
        path.write_text("trugs-tools 1.0\n")
    elif surface in {"metadata", "extra-metadata"}:
        row = tree.table.row("TRUGS-TOOLS")
        data = metadata(row)
        data["dependencies"] = ["trugs-store>=2.1.0"]
        path = root / (
            "extra/pyproject.toml" if surface.startswith("extra") else "pyproject.toml"
        )
        write_metadata(path, row, data)
    elif surface.startswith("index"):
        path = tree.index / "trugs-tools.json"
        data = json.loads(path.read_text())
        data["info"]["description" if surface.endswith("readme") else "version"] = (
            "trugs-tools 1.0" if surface.endswith("readme") else "1.0.0"
        )
        path.write_text(json.dumps(data))
    else:
        path = tree.site / (
            "extra.html" if surface == "unlinked-page" else "index.html"
        )
        path.write_text("<p>TRUGS-WEB 1.0</p>")
    assert checker.main(tree.args()) == 1
    output = capsys.readouterr().out
    assert str(path) in output
    for line in output.splitlines():
        assert all(field in line for field in [": C", "claimed=", "expected="])
        assert re.search(r":\d+: C[1-5]:", line)


def test_excluded_directories(tree: Tree) -> None:
    for name in [".git", "vendor"]:
        path = tree.roots["TRUGS"] / name
        path.mkdir()
        (path / "README.md").write_text("trugs-tools 1.0")
    assert checker.main(tree.args()) == 0


@pytest.mark.parametrize(
    "requirement", ["trugs-store<3,>=2.0.0", "trugs-store>=2.0.0,<3"]
)
def test_clause_order(requirement: str) -> None:
    assert checker.clause_set(
        requirement.removeprefix("trugs-store")
    ) == checker.clause_set(">=2.0.0,<3")


def test_exact_metadata_precedes_range_exemption(tree: Tree) -> None:
    row = tree.table.row("TRUGS-TOOLS")
    assert checker.admits(">=2.1.0", "2.2.0")
    data = metadata(row)
    data["dependencies"] = ["trugs-store>=2.1.0"]
    assert checker.metadata_findings(data, row, tree.table)[0][0] == "C3"
    assert not checker.inspect_text(
        checker.markdown("trugs-store>=2.1.0"), row, tree.table
    )


@pytest.mark.parametrize(
    "href,expected",
    [
        ("/onboard/", "onboard/index.html"),
        ("../", "index.html"),
        ("https://trugs.ai/onboard/", "onboard/index.html"),
        ("//trugs.ai/", "index.html"),
        ("/extra.html#section", "extra.html"),
        ("https://elsewhere.example/missing/", None),
        ("image.svg", None),
    ],
)
def test_page_links(href: str, expected: str | None) -> None:
    assert checker.linked_page(href, "onboard/index.html") == expected


@pytest.mark.parametrize(
    "html,expected",
    [
        ("<p>TRUGS-WEB <b>1.0</b></p>", ["C1"]),
        ("<p>TRUGS-WEB&#32;2.1.0</p>", []),
        ("<p>TRUGS-WEB</p><p>coming</p>", []),
        ("<p>TRUGS-WEB <code>coming</code></p>", []),
        ("<h2>History</h2><p>TRUGS-WEB 1.0</p>", []),
        (
            "<h2>History</h2><p>TRUGS-WEB 1.0</p><h2>Today</h2><p>TRUGS-WEB 1.0</p>",
            ["C1"],
        ),
    ],
)
def test_html(html: str, expected: list[str]) -> None:
    page = checker.Page()
    page.feed(html)
    table = checker.read_table(TABLE)
    assert (
        sorted(
            {
                r[1]
                for r in checker.inspect_text(page.text, table.row("TRUGS-SITE"), table)
            }
        )
        == expected
    )


@pytest.mark.parametrize(
    "separator", [". ", "? ", "! ", "; ", " | ", "\n\n", "\n- ", "\n## "]
)
def test_clause_boundaries(separator: str) -> None:
    table = checker.read_table(TABLE)
    assert not checker.inspect_text(
        checker.markdown("TRUGS-VIEWER" + separator + "coming"),
        table.row("TRUGS"),
        table,
    )


def test_wrapped_clause_and_source_line() -> None:
    table = checker.read_table(TABLE)
    text = checker.markdown("# Today\n\nTRUGS-VIEWER\nis coming.\n")
    assert checker.inspect_text(text, table.row("TRUGS"), table)[0][:2] == (4, "C5")


def test_no_network_imports() -> None:
    source = ast.parse(Path(checker.__file__).read_text())
    imports: set[str] = set()
    for node in ast.walk(source):
        if isinstance(node, ast.Import):
            imports.update(n.name.split(".")[0] for n in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module.split(".")[0])
    assert not imports & {"socket", "urllib", "http", "requests", "httpx", "subprocess"}


@pytest.mark.parametrize("case", TEXT_CASES, ids=lambda c: c["case"])
def test_text_fixture_exit(
    tree: Tree, case: dict[str, Any], capsys: pytest.CaptureFixture[str]
) -> None:
    if case["own"]:
        path = tree.roots[case["own"]] / "README.md"
        path.write_text(case["text"])
    else:
        path = tree.site / "extra.html"
        path.write_text(case["text"])
    assert checker.main(tree.args()) == int(bool(case["rules"]))
    for line in capsys.readouterr().out.splitlines():
        assert str(path) in line
        assert re.search(r":\d+: C[1-5]: claimed=.+; expected=.+", line)


@pytest.mark.parametrize("case", METADATA_CASES, ids=lambda c: c["case"])
def test_metadata_fixture_exit(tree: Tree, case: dict[str, Any]) -> None:
    row = tree.table.row(case["own"])
    data = metadata(row)
    data[case["field"]] = case["value"]
    write_metadata(tree.roots[row.repository] / row.package_file, row, data)
    assert checker.main(tree.args()) == int(bool(case["rules"]))


@pytest.mark.parametrize(
    "surface,phrase,rule",
    [
        ("readme", "package version", "C1"),
        ("readme", "spec revision", "C2"),
        ("page", "spec revision", "C2"),
    ],
)
@pytest.mark.parametrize("space", [" ", "\t", "\n", " \t\n "])
@pytest.mark.parametrize("number", ["9.0", "2.0.0"])
def test_phrase_whitespace_and_locations(
    tree: Tree,
    phrase: str,
    rule: str,
    space: str,
    number: str,
    surface: str,
    capsys: pytest.CaptureFixture[str],
) -> None:
    words = phrase.split()
    claim = space.join(words) + " " + number
    path = tree.roots["TRUGS"] / "README.md"
    if surface == "page":
        path = tree.site / "extra.html"
        path.write_text("<p>\n\n" + claim + ".</p>\n")
    else:
        path.write_text("# Today\n\n" + claim + ".\n")
    assert checker.main(tree.args()) == int(number == "9.0")
    output = capsys.readouterr().out
    if number == "9.0":
        assert output.startswith(f"{path}:3: {rule}: claimed=")
        assert "; expected='2.0.0'" in output
    else:
        assert not output


@pytest.mark.parametrize("space", ["\t", "\n", " \t\n "])
def test_reverse_spec_phrase_whitespace(space: str) -> None:
    table = checker.read_table(TABLE)
    for number in ["9.0", "2.0.0"]:
        text = checker.markdown("# Today\n\n" + number + " spec" + space + "revision")
        result = checker.inspect_text(text, table.row("TRUGS"), table)
        assert [r[:2] for r in result] == ([(3, "C2")] if number == "9.0" else [])


@pytest.mark.parametrize("phrase", ["package version", "spec revision"])
@pytest.mark.parametrize(
    "separator", ["\n\n", ";", " | ", ". ", "? ", "! ", "\n- ", "\n## "]
)
def test_phrase_respects_clause_boundaries(phrase: str, separator: str) -> None:
    table = checker.read_table(TABLE)
    first, second = phrase.split()
    text = checker.markdown(first + separator + second + " 9.0")
    assert not checker.inspect_text(text, table.row("TRUGS"), table)


def test_wrapped_spec_html_block_boundary_and_history() -> None:
    table = checker.read_table(TABLE)
    for html in [
        "<p>spec</p><p>revision 9.0</p>",
        "<p>Previously spec\nrevision 9.0</p>",
        "<h2>History</h2><p>spec\nrevision 9.0</p>",
    ]:
        page = checker.Page()
        page.feed(html)
        assert not checker.inspect_text(page.text, table.row("TRUGS-SITE"), table)
