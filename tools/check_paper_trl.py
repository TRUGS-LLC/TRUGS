"""Measure paper TRL, whole graphs and numbered examples with the trug CLI."""

# <trl>
# PROCESS paper_measurement SHALL READ FILE paper AND FILE examples THEN PRODUCE DATA counts.
# </trl>
from __future__ import annotations

import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LISTING = re.compile(
    rb"^\\begin\{lstlisting\}\[style=trugs\]\r?\n(.*?)^\\end\{lstlisting\}",
    re.MULTILINE | re.DOTALL,
)
GRAPH_LISTING = re.compile(
    rb"^\\begin\{lstlisting\}\[style=json\]\r?\n(.*?)^\\end\{lstlisting\}",
    re.MULTILINE | re.DOTALL,
)
CODE_LISTING = re.compile(
    rb"^\\begin\{lstlisting\}(?:\[([^\]]*)\])?\r?\n(.*?)^\\end\{lstlisting\}",
    re.MULTILINE | re.DOTALL,
)
ANNOTATION = re.compile(rb"<tr>(.*?)</tr>", re.DOTALL)
LANGUAGE = re.compile(rb"(?:^|,)\s*language\s*=\s*\{?([\w+]+)\}?")
COMMENT_LEADERS = {
    b"python": rb"#",
    b"go": rb"//|/\*|\*(?!/)",
    b"rust": rb"//|/\*|\*(?!/)",
    b"c": rb"//|/\*|\*(?!/)",
    b"c++": rb"//|/\*|\*(?!/)",
    b"java": rb"//|/\*|\*(?!/)",
    b"javascript": rb"//|/\*|\*(?!/)",
    b"bash": rb"#",
    b"sql": rb"--|/\*|\*(?!/)",
}
HEADING = re.compile(rb"^#{2,3} .*$", re.MULTILINE)
NUMBERED = re.compile(rb"^### (\d+)\. ")
FENCE = re.compile(rb"^```(?:trl)?\r?\n(.*?)^```[ \t]*\r?$", re.MULTILINE | re.DOTALL)


# <trl>
# RECORD case CONTAINS DATA label AND DATA text AND DATA exact_round_trip.
# </trl>
# ---
@dataclass(frozen=True)
# RECORD case CONTAINS DATA label AND DATA text AND DATA exact_round_trip.
class Case:
    label: str
    text: bytes
    exact_round_trip: bool = True


# <trl>
# RECORD result CONTAINS DATA accepted AND DATA valid AND DATA round_trip.
# </trl>
# ---
@dataclass(frozen=True)
# RECORD result CONTAINS DATA accepted AND DATA valid AND DATA round_trip.
class Result:
    accepted: bool
    valid: bool
    round_trip: bool


# <trl>
# FUNCTION extract_listings SHALL FILTER DATA text THEN RETURN ALL RECORD listing.
# </trl>
# ---
# FUNCTION extract_listings SHALL FILTER DATA text THEN RETURN ALL RECORD listing.
def extract_listings(text: bytes) -> list[Case]:
    """Keep all body bytes, including indentation and the final newline."""
    return [Case(str(i), m[1]) for i, m in enumerate(LISTING.finditer(text), 1)]


# <trl>
# FUNCTION extract_graphs SHALL FILTER DATA text THEN RETURN ALL RECORD graph.
# </trl>
# ---
# FUNCTION extract_graphs SHALL FILTER DATA text THEN RETURN ALL RECORD graph.
def extract_graphs(text: bytes) -> list[Case]:
    """Every json-style listing is a whole graph; fragments have their own style."""
    return [Case(str(i), m[1]) for i, m in enumerate(GRAPH_LISTING.finditer(text), 1)]


# <trl>
# FUNCTION extract_annotations SHALL FILTER DATA text THEN RETURN ALL RECORD annotation.
# </trl>
# ---
# FUNCTION extract_annotations SHALL FILTER DATA text THEN RETURN ALL RECORD annotation.
def extract_annotations(text: bytes) -> list[Case]:
    """Preserve every tag payload; require exact round trips for inline code tags."""
    cases: list[Case] = []
    for listing in CODE_LISTING.finditer(text):
        body = listing[2]
        blocks = list(ANNOTATION.finditer(body))
        if body.count(b"<tr>") != len(blocks) or body.count(b"</tr>") != len(blocks):
            raise ValueError("unpaired or nested annotation tags")
        language = LANGUAGE.search(listing[1] or b"")
        leader = COMMENT_LEADERS.get(language[1].lower()) if language else None
        for block in blocks:
            source = block[1]
            line_start = body.rfind(b"\n", 0, block.start()) + 1
            prefix = body[line_start : block.start()].lstrip()
            inline = bool(prefix) and not (
                leader and re.match(rb"(?:" + leader + rb")", prefix)
            )
            if leader:
                source = re.sub(rb"(?m)^[ \t]*(?:" + leader + rb")(?: ?)", b"", source)
            source = source.strip() + b"\n"
            cases.append(Case(f"annotation-{len(cases) + 1}", source, bool(inline)))
    return cases


# <trl>
# FUNCTION strip_trl_tags SHALL FILTER DATA payload THEN RETURN DATA text.
# </trl>
# ---
# FUNCTION strip_trl_tags SHALL FILTER DATA payload THEN RETURN DATA text.
def strip_trl_tags(payload: bytes) -> bytes:
    """Drop a fence's <trl> and </trl> lines; keep every other byte."""
    lines = payload.split(b"\n")
    if lines and lines[0].strip() == b"<trl>":
        lines = lines[1:]
    if len(lines) >= 2 and lines[-1] == b"" and lines[-2].strip() == b"</trl>":
        lines = lines[:-2] + [b""]
    return b"\n".join(lines)


# <trl>
# FUNCTION extract_examples SHALL FILTER DATA text THEN RETURN ALL RECORD example.
# </trl>
# ---
# FUNCTION extract_examples SHALL FILTER DATA text THEN RETURN ALL RECORD example.
def extract_examples(text: bytes) -> list[Case]:
    """Require exactly one example fence per numbered heading.

    The fence may hold its sentences between <trl> and </trl> lines, the form
    `trug audit markdown` reads; those two lines are not part of the example.
    """
    headings = list(HEADING.finditer(text))
    cases = []
    for i, heading in enumerate(headings):
        number = NUMBERED.match(heading[0])
        if number is None:
            continue
        end = headings[i + 1].start() if i + 1 < len(headings) else len(text)
        fences = list(FENCE.finditer(text, heading.end(), end))
        if len(fences) != 1:
            raise ValueError("each numbered example must have exactly one fence")
        cases.append(Case(number[1].decode("ascii"), strip_trl_tags(fences[0][1])))
    if len({case.label for case in cases}) != len(cases):
        raise ValueError("duplicate example number")
    return cases


# <trl>
# FUNCTION run_command SHALL EXECUTE PROCESS command THEN RETURN RECORD result.
# </trl>
# ---
# FUNCTION run_command SHALL EXECUTE PROCESS command THEN RETURN RECORD result.
def run_command(args: list[str]) -> subprocess.CompletedProcess[bytes]:
    """Keep child Python invocations from writing bytecode."""
    return subprocess.run(
        args,
        capture_output=True,
        check=False,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
    )


# <trl>
# FUNCTION tool_version SHALL READ FILE executable THEN RETURN DATA version.
# </trl>
# ---
# FUNCTION tool_version SHALL READ FILE executable THEN RETURN DATA version.
def tool_version(executable: str) -> str:
    """Ask the Python console script's interpreter for its package metadata.

    The CLI has no version verb. Using its shebang queries the installation
    actually selected on PATH, even when this script uses another interpreter.
    """
    with Path(executable).open("rb") as stream:
        first_line = stream.readline().decode("utf-8").strip()
    if not first_line.startswith("#!"):
        raise ValueError("trug must be the Python package's console script")
    interpreter = shlex.split(first_line[2:])
    result = run_command(
        interpreter
        + [
            "-c",
            "from importlib.metadata import version; print(version('trugs-tools'))",
        ]
    )
    if result.returncode:
        raise ValueError("cannot read trugs-tools version from trug's interpreter")
    return result.stdout.decode("utf-8").strip()


# <trl>
# FUNCTION check_case SHALL EXECUTE PROCESS compilation THEN VALIDATE RECORD graph AND RETURN RECORD result.
# </trl>
# ---
# FUNCTION check_case SHALL EXECUTE PROCESS compilation THEN VALIDATE RECORD graph AND RETURN RECORD result.
def check_case(case: Case, directory: Path, executable: str) -> Result:
    source = directory / f"case-{case.label}.trl"
    graph = source.with_suffix(".json")
    source.write_bytes(case.text)
    compiled = run_command([executable, "trl", "compile", str(source)])
    if compiled.returncode:
        print(f"  {case.label}: compile exit {compiled.returncode}")
        print(compiled.stderr.decode("utf-8", errors="replace").strip())
        return Result(False, False, False)
    graph.write_bytes(compiled.stdout)
    validation = run_command([executable, "validate", str(graph)])
    valid = validation.returncode == 0 and bool(
        re.search(rb"\bVALID\b", validation.stdout)
    )
    decompiled = run_command([executable, "trl", "decompile", str(graph)])
    if decompiled.returncode:
        raise ValueError(f"{case.label}: decompile exit {decompiled.returncode}")
    equal = decompiled.stdout == case.text
    print(
        f"  {case.label}: compile exit 0, "
        f"validate {'VALID' if valid else 'FAILED'}, "
        f"round trip {'identical' if equal else 'different'}"
    )
    return Result(True, valid, equal)


# <trl>
# FUNCTION check_graph SHALL VALIDATE RECORD graph THEN RETURN DATA valid.
# </trl>
# ---
# FUNCTION check_graph SHALL VALIDATE RECORD graph THEN RETURN DATA valid.
def check_graph(case: Case, directory: Path, executable: str) -> bool:
    """Validate the exact listing bytes, including any malformed JSON."""
    graph = directory / f"graph-{case.label}.json"
    graph.write_bytes(case.text)
    validation = run_command([executable, "validate", str(graph)])
    valid = validation.returncode == 0 and bool(
        re.search(rb"\bVALID\b", validation.stdout)
    )
    print(f"  {case.label}: validate {'VALID' if valid else 'FAILED'}")
    if not valid:
        print((validation.stdout + validation.stderr).decode("utf-8", errors="replace"))
    return valid


# <trl>
# FUNCTION count_macros SHALL MAP ALL RECORD result TO DATA macros THEN RETURN DATA macros.
# </trl>
# ---
# FUNCTION count_macros SHALL MAP ALL RECORD result TO DATA macros THEN RETURN DATA macros.
def count_macros(
    examples: list[Case],
    example_results: list[Result],
    listing_results: list[Result],
    graph_results: list[bool],
    annotation_results: list[Result],
) -> dict[str, str]:
    if len(examples) != len(example_results):
        raise ValueError("example results must match the extracted examples")
    rejected = [
        case.label
        for case, result in zip(examples, example_results)
        if not result.accepted
    ]
    return {
        "ExamplesTotal": str(len(examples)),
        "ExamplesAccepted": str(sum(r.accepted for r in example_results)),
        "ExamplesRoundTrip": str(sum(r.round_trip for r in example_results)),
        "ExamplesRejectedList": ", ".join(rejected) or "none",
        "ListingsTotal": str(len(listing_results)),
        "ListingsAccepted": str(sum(r.accepted for r in listing_results)),
        "ListingsRoundTrip": str(sum(r.round_trip for r in listing_results)),
        "GraphsTotal": str(len(graph_results)),
        "GraphsValid": str(sum(graph_results)),
        "AnnotationsTotal": str(len(annotation_results)),
        "AnnotationsAccepted": str(sum(r.accepted for r in annotation_results)),
        "AnnotationsValid": str(sum(r.valid for r in annotation_results)),
        "AnnotationsRoundTrip": str(sum(r.round_trip for r in annotation_results)),
    }


# <trl>
# FUNCTION main SHALL READ FILE paper AND FILE examples THEN WRITE FILE counts AND RETURN DATA exit_code.
# </trl>
# ---
# FUNCTION main SHALL READ FILE paper AND FILE examples THEN WRITE FILE counts AND RETURN DATA exit_code.
def main() -> int:
    executable = shutil.which("trug")
    if executable is None:
        raise ValueError("install trugs-tools and put trug on PATH")
    print(f"trugs-tools {tool_version(executable)}")
    paper = (ROOT / "PAPER/trugs.tex").read_bytes()
    listings = extract_listings(paper)
    graphs = extract_graphs(paper)
    annotations = extract_annotations(paper)
    examples = extract_examples((ROOT / "TRUGS_LANGUAGE/SPEC_examples.md").read_bytes())
    if not listings or not examples or not graphs:
        raise ValueError(
            "paper TRL listings, whole graphs and numbered examples required"
        )
    with tempfile.TemporaryDirectory(prefix="paper-trl-") as temporary:
        directory = Path(temporary)
        print("Paper listings:")
        listing_results = [check_case(case, directory, executable) for case in listings]
        print("Numbered examples:")
        example_results = [check_case(case, directory, executable) for case in examples]
        print("Paper graphs:")
        graph_results = [check_graph(case, directory, executable) for case in graphs]
        print("Paper tagged annotations:")
        annotation_results = [
            check_case(case, directory, executable) for case in annotations
        ]
    macros = count_macros(
        examples, example_results, listing_results, graph_results, annotation_results
    )
    output = ROOT / "PAPER/generated/trl_counts.tex"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        "% Generated by tools/check_paper_trl.py; do not edit.\n"
        + "".join(
            f"\\newcommand{{\\{key}}}{{{value}}}\n" for key, value in macros.items()
        ),
        encoding="utf-8",
    )
    for key, value in macros.items():
        print(f"{key}: {value}")
    print(f"Wrote {output.relative_to(ROOT)}")
    return int(
        any(not (r.accepted and r.valid and r.round_trip) for r in listing_results)
        or any(r.accepted and not r.valid for r in example_results)
        or not all(graph_results)
        or any(
            not (r.accepted and r.valid and (r.round_trip or not case.exact_round_trip))
            for case, r in zip(annotations, annotation_results)
        )
    )


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        sys.exit(1)
