"""Extraction, CLI failures and round-trip accounting on synthetic inputs."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from tools import check_paper_trl as checker


@pytest.fixture
def fake_trug(tmp_path: Path) -> str:
    """A real subprocess fixture, independent of any installed language tool."""
    tool = tmp_path / "trug"
    tool.write_text(
        f"#!{sys.executable}\n"
        "import json, sys\n"
        "from pathlib import Path\n"
        "args = sys.argv[1:]\n"
        "if args[:2] == ['trl', 'compile']:\n"
        "    text = Path(args[2]).read_text()\n"
        "    if text.startswith('REJECT'):\n"
        "        print('synthetic rejection', file=sys.stderr)\n"
        "        sys.exit(2)\n"
        "    print(json.dumps({'text': text}))\n"
        "elif args[0] == 'validate':\n"
        "    try:\n"
        "        text = json.loads(Path(args[1]).read_text())['text']\n"
        "    except (ValueError, KeyError):\n"
        "        print('INVALID: malformed graph')\n"
        "        sys.exit(1)\n"
        "    bad = text.startswith('INVALID')\n"
        "    print('INVALID' if bad else 'VALID')\n"
        "    sys.exit(int(bad))\n"
        "elif args[:2] == ['trl', 'decompile']:\n"
        "    text = json.loads(Path(args[2]).read_text())['text']\n"
        "    if text.startswith('DECOMPILE_ERROR'):\n"
        "        sys.exit(2)\n"
        "    if text.startswith('DIFFERENT'):\n"
        "        text = text.replace('  ', ' ')\n"
        "    sys.stdout.write(text)\n"
    )
    tool.chmod(0o700)
    return str(tool)


def test_extract_only_measured_styles_preserving_bytes() -> None:
    text = (
        b"\\begin{lstlisting}[style=grammar]\nBNF\n\\end{lstlisting}\n"
        b"\\begin{lstlisting}[style=trugsillustration]\nSKETCH\n\\end{lstlisting}\n"
        b"\\begin{lstlisting}[style=trugs]\n  A\n\nB\n\\end{lstlisting}\n"
        b"\\begin{lstlisting}[style=pseudocode]\nCODE\n\\end{lstlisting}\n"
        b"\\begin{lstlisting}[style=trugs]\nC\n\\end{lstlisting}\n"
    )
    assert checker.extract_listings(text) == [
        checker.Case("1", b"  A\n\nB\n"),
        checker.Case("2", b"C\n"),
    ]


def test_numbered_examples_ignore_other_fences_and_keep_numbers() -> None:
    text = (
        b"## Notes\n```\nignored\n```\n"
        b"### 2. Example\n```trl\n A\n```\nnotes\n"
        b"### 17. Reserved\n```\nB\n```\n"
        b"## Other section\n```\nignored\n```\n"
    )
    assert checker.extract_examples(text) == [
        checker.Case("2", b" A\n"),
        checker.Case("17", b"B\n"),
    ]
    with pytest.raises(ValueError, match="exactly one fence"):
        checker.extract_examples(b"### 1. Missing\nprose\n")
    with pytest.raises(ValueError, match="duplicate"):
        checker.extract_examples(b"### 1. A\n```\nA\n```\n" * 2)


def test_extract_annotations_from_all_listing_languages() -> None:
    paper = (
        b"Prose <tr>ignored</tr>\n"
        b"\\begin{lstlisting}[language=Python]\n"
        b"x = 1 # <tr>PARTY system SHALL READ DATA x.</tr>\n"
        b"# <tr>PARTY system SHALL FILTER ALL ACTIVE RECORD\n"
        b"#   THEN SORT RESULT.</tr>\n\\end{lstlisting}\n"
        b"\\begin{lstlisting}[caption={Example}, language={Go}]\n"
        b"// <tr>PARTY system SHALL READ DATA x\n"
        b"//   FROM STREAM db.</tr>\n\\end{lstlisting}\n"
        b"\\begin{lstlisting}[language=Rust]\n"
        b"// <tr>PARTY system SHALL WRITE DATA x.</tr>\n\\end{lstlisting}\n"
        b"\\begin{lstlisting}[language=Java]\n"
        b"/* <tr>PARTY system SHALL READ DATA x\n"
        b" *   FROM STREAM db.</tr> */\n\\end{lstlisting}\n"
        b"\\begin{lstlisting}[style=other]\n"
        b"<tr>KEEP # // INTERNAL  SPACES</tr>\n\\end{lstlisting}\n"
        b"\\begin{lstlisting}\n<tr>UNTYPED</tr>\n\\end{lstlisting}\n"
    )
    annotations = checker.extract_annotations(paper)
    assert [case.text for case in annotations] == [
        b"PARTY system SHALL READ DATA x.\n",
        b"PARTY system SHALL FILTER ALL ACTIVE RECORD\n  THEN SORT RESULT.\n",
        b"PARTY system SHALL READ DATA x\n  FROM STREAM db.\n",
        b"PARTY system SHALL WRITE DATA x.\n",
        b"PARTY system SHALL READ DATA x\n  FROM STREAM db.\n",
        b"KEEP # // INTERNAL  SPACES\n",
        b"UNTYPED\n",
    ]
    assert [case.exact_round_trip for case in annotations] == [
        True,
        False,
        False,
        False,
        False,
        False,
        False,
    ]
    for tags in (b"<tr>missing", b"missing</tr>", b"<tr><tr>nested</tr></tr>"):
        with pytest.raises(ValueError, match="annotation tags"):
            checker.extract_annotations(
                b"\\begin{lstlisting}[language=Python]\n"
                + tags
                + b"\n\\end{lstlisting}\n"
            )


def test_compile_validate_and_byte_comparison(tmp_path: Path, fake_trug: str) -> None:
    for source, expected in [
        (b"OK\n  same\n", checker.Result(True, True, True)),
        (b"REJECT\n", checker.Result(False, False, False)),
        (b"INVALID\n", checker.Result(True, False, True)),
        (b"DIFFERENT  layout\n", checker.Result(True, True, False)),
    ]:
        assert (
            checker.check_case(checker.Case("1", source), tmp_path, fake_trug)
            == expected
        )
    with pytest.raises(ValueError, match="decompile exit 2"):
        checker.check_case(checker.Case("1", b"DECOMPILE_ERROR\n"), tmp_path, fake_trug)


def test_version_uses_selected_console_script_interpreter(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    tool = tmp_path / "trug"
    tool.write_text("#!/fixture/python\n")
    calls: list[list[str]] = []

    def run(args: list[str]) -> subprocess.CompletedProcess[bytes]:
        calls.append(args)
        return subprocess.CompletedProcess(args, 0, b"fixture-version\n", b"")

    monkeypatch.setattr(checker, "run_command", run)
    assert checker.tool_version(str(tool)) == "fixture-version"
    assert calls[0][:2] == ["/fixture/python", "-c"]


@pytest.mark.parametrize("listing", [b"OK\n", b"INVALID\n", b"DIFFERENT  layout\n"])
def test_main_counts_examples_and_fails_bad_listings(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, fake_trug: str, listing: bytes
) -> None:
    paper = tmp_path / "PAPER/trugs.tex"
    paper.parent.mkdir()
    paper.write_bytes(
        b"\\begin{lstlisting}[style=trugs]\n" + listing + b"\\end{lstlisting}\n"
        b'\\begin{lstlisting}[style=json]\n{"text": "OK"}\n\\end{lstlisting}\n'
    )
    examples = tmp_path / "TRUGS_LANGUAGE/SPEC_examples.md"
    examples.parent.mkdir()
    examples.write_bytes(
        b"### 1. Accepted\n```\nOK\n```\n### 9. Reserved\n```\nREJECT\n```\n"
    )
    monkeypatch.setattr(checker, "ROOT", tmp_path)
    monkeypatch.setattr(checker.shutil, "which", lambda name: fake_trug)
    monkeypatch.setattr(checker, "tool_version", lambda executable: "fixture-version")
    assert checker.main() == (0 if listing == b"OK\n" else 1)
    macros = (tmp_path / "PAPER/generated/trl_counts.tex").read_text()
    assert "\\newcommand{\\ExamplesTotal}{2}" in macros
    assert "\\newcommand{\\ExamplesAccepted}{1}" in macros
    assert "\\newcommand{\\ExamplesRoundTrip}{1}" in macros
    assert "\\newcommand{\\ExamplesRejectedList}{9}" in macros
    assert "\\newcommand{\\ListingsAccepted}{1}" in macros
    expected = "0" if listing.startswith(b"DIFFERENT") else "1"
    assert f"\\newcommand{{\\ListingsRoundTrip}}{{{expected}}}" in macros
    assert "\\newcommand{\\GraphsTotal}{1}" in macros
    assert "\\newcommand{\\GraphsValid}{1}" in macros


@pytest.mark.parametrize(
    "graph", [b'{"text": "OK"}\n', b'{"text": "INVALID"}\n', b"{...}\n"]
)
def test_main_validates_whole_graphs_and_excludes_fragments(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, fake_trug: str, graph: bytes
) -> None:
    paper = tmp_path / "PAPER/trugs.tex"
    paper.parent.mkdir()
    paper.write_bytes(
        b"\\begin{lstlisting}[style=trugs]\nOK\n\\end{lstlisting}\n"
        b"\\begin{lstlisting}[style=jsonfragment]\nSCHEMA\n\\end{lstlisting}\n"
        b"\\begin{lstlisting}[style=json]\n" + graph + b"\\end{lstlisting}\n"
        b'\\begin{lstlisting}[style=json]\n{"text": "OK"}\n\\end{lstlisting}\n'
    )
    assert checker.extract_graphs(paper.read_bytes()) == [
        checker.Case("1", graph),
        checker.Case("2", b'{"text": "OK"}\n'),
    ]
    examples = tmp_path / "TRUGS_LANGUAGE/SPEC_examples.md"
    examples.parent.mkdir()
    examples.write_bytes(b"### 1. Accepted\n```\nOK\n```\n")
    monkeypatch.setattr(checker, "ROOT", tmp_path)
    monkeypatch.setattr(checker.shutil, "which", lambda name: fake_trug)
    monkeypatch.setattr(checker, "tool_version", lambda executable: "fixture-version")
    valid = graph == b'{"text": "OK"}\n'
    assert checker.main() == (0 if valid else 1)
    macros = (tmp_path / "PAPER/generated/trl_counts.tex").read_text()
    assert "\\newcommand{\\GraphsTotal}{2}" in macros
    assert f"\\newcommand{{\\GraphsValid}}{{{2 if valid else 1}}}" in macros


def test_no_rejections_is_reported_as_none() -> None:
    macros = checker.count_macros(
        [checker.Case("2", b"A\n")], [checker.Result(True, True, True)], [], [], []
    )
    assert macros["ExamplesRejectedList"] == "none"


@pytest.mark.parametrize(
    "annotation", [b"OK", b"REJECT", b"INVALID", b"DIFFERENT  layout"]
)
@pytest.mark.parametrize("inline", [True, False])
def test_main_measures_annotations_and_propagates_failures(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    fake_trug: str,
    annotation: bytes,
    inline: bool,
) -> None:
    paper = tmp_path / "PAPER/trugs.tex"
    paper.parent.mkdir()
    paper.write_bytes(
        b"\\begin{lstlisting}[style=trugs]\nOK\n\\end{lstlisting}\n"
        b'\\begin{lstlisting}[style=json]\n{"text": "OK"}\n\\end{lstlisting}\n'
        b"\\begin{lstlisting}[language=Python]\n"
        + (b"x = 1 # <tr>" if inline else b"# <tr>")
        + annotation
        + b"</tr>\n\\end{lstlisting}\n"
        b"\\begin{lstlisting}[language=Go]\n// <tr>OK</tr>\n\\end{lstlisting}\n"
        b"\\begin{lstlisting}[language=Rust]\n// <tr>OK</tr>\n\\end{lstlisting}\n"
    )
    examples = tmp_path / "TRUGS_LANGUAGE/SPEC_examples.md"
    examples.parent.mkdir()
    examples.write_bytes(b"### 1. Accepted\n```\nOK\n```\n")
    monkeypatch.setattr(checker, "ROOT", tmp_path)
    monkeypatch.setattr(checker.shutil, "which", lambda name: fake_trug)
    monkeypatch.setattr(checker, "tool_version", lambda executable: "fixture-version")
    succeeds = annotation == b"OK" or (
        not inline and annotation == b"DIFFERENT  layout"
    )
    assert checker.main() == (0 if succeeds else 1)
    if annotation == b"DIFFERENT  layout":
        assert "annotation-1: compile exit 0, validate VALID, round trip different" in (
            capsys.readouterr().out
        )
    macros = (tmp_path / "PAPER/generated/trl_counts.tex").read_text()
    expected = {
        "AnnotationsTotal": 3,
        "AnnotationsAccepted": 2 if annotation == b"REJECT" else 3,
        "AnnotationsValid": 2 if annotation in (b"REJECT", b"INVALID") else 3,
        "AnnotationsRoundTrip": (
            2 if annotation in (b"REJECT", b"DIFFERENT  layout") else 3
        ),
    }
    for key, value in expected.items():
        assert f"\\newcommand{{\\{key}}}{{{value}}}" in macros


def test_numbered_examples_strip_trl_tag_lines() -> None:
    tagged = b"### 1. A\n```\n<trl>\nPARTY a VALIDATE.\n</trl>\n```\n"
    plain = b"### 1. A\n```\nPARTY a VALIDATE.\n```\n"
    assert checker.extract_examples(tagged) == checker.extract_examples(plain)
    assert checker.extract_examples(tagged)[0].text == b"PARTY a VALIDATE.\n"
    assert checker.strip_trl_tags(b"A\n") == b"A\n"
    assert checker.strip_trl_tags(b"<trl>\n</trl>\n") == b""
