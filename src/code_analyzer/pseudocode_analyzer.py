"""Statically analyze a ``starterfile.pseudo`` before any code is generated.

The analyzer reviews *static signals* first (required sections, the approval
marker, per-section syntax) and then the *overall structure* (how the
PSEUDOCODE file paths relate to the REPOMAP directories and the DATABASES
spec).

It never calls an LLM by default. It returns a structured
:class:`AnalysisReport` with ``errors`` and ``warnings``, can write a Markdown
report, and can emit a *tagged copy* of the starterfile where every finding is
inserted as a ``# TAG:`` comment. Hard ``errors`` are meant to block code
generation; warnings are advisory.

Example:
    from code_analyzer.pseudocode_analyzer import PseudocodeAnalyzer

    analyzer = PseudocodeAnalyzer("starterfile.pseudo", project_root=".")
    report = analyzer.analyze()
    analyzer.write_report()
    analyzer.write_tagged_copy()
    if not report.ok:
        ...
"""

from __future__ import annotations

import posixpath
import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

#: Sections every starterfile must define, even when their body is ``NONE``.
REQUIRED_SECTIONS: Tuple[str, ...] = ("REPOMAP", "DATABASES", "PSEUDOCODE")

#: Bodies that mean "no items in this section".
_NONE_TOKENS = {"", "NONE", "EMPTY"}

#: Known source-file extensions the generator can produce.
KNOWN_EXTENSIONS = {
    ".py", ".pyi", ".js", ".mjs", ".cjs", ".jsx", ".ts", ".tsx", ".java",
    ".kt", ".go", ".rs", ".rb", ".php", ".cs", ".c", ".h", ".cpp", ".hpp",
    ".sh", ".sql",
}

_SECTION_HEADER = re.compile(r"^#\s+([A-Za-z_][A-Za-z0-9_ ]*?)\s*$")
_STATUS_MARKER = re.compile(r"^#\s*STATUS\s*:\s*([A-Za-z0-9_]+)\s*$", re.IGNORECASE)
_PSEUDO_HEADER = re.compile(r"^##\s+(.+?)\s*$")
_FIELD_LABEL = re.compile(r"^([A-Z][A-Z ]*):\s*(.*)$")


@dataclass
class Tag:
    """A single finding anchored to a 1-based line in the starterfile."""

    line: int
    severity: str  # "ERROR" | "WARNING"
    code: str
    message: str

    def render(self) -> str:
        return "# TAG: {}: {}: {}".format(self.severity, self.code, self.message)


@dataclass
class AnalysisReport:
    """Structured result of a starterfile analysis."""

    path: str
    errors: List[Tag] = field(default_factory=list)
    warnings: List[Tag] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        """True when there are no blocking errors."""
        return not self.errors

    @property
    def tags(self) -> List[Tag]:
        return list(self.errors) + list(self.warnings)

    def to_markdown(self) -> str:
        lines = [
            "# Pseudocode analysis report",
            "",
            "Source: `{}`".format(self.path),
            "",
        ]
        status = "PASS" if self.ok else "FAIL"
        lines.append("- Status: **{}**".format(status))
        lines.append("- Errors: {}".format(len(self.errors)))
        lines.append("- Warnings: {}".format(len(self.warnings)))
        lines.append("")
        for title, entries in (("Errors", self.errors), ("Warnings", self.warnings)):
            lines.append("## {}".format(title))
            if not entries:
                lines.append("")
                lines.append("_None_")
            else:
                for tag in entries:
                    lines.append(
                        "- line {}: `{}` — {}".format(
                            tag.line, tag.code, tag.message
                        )
                    )
            lines.append("")
        return "\n".join(lines).rstrip() + "\n"


def _is_none_body(text: str) -> bool:
    return text.strip().upper() in _NONE_TOKENS


def _split_sections(lines: List[str]) -> Dict[str, Tuple[int, List[Tuple[int, str]]]]:
    """Split top-level ``# SECTION`` blocks.

    Returns ``{NAME: (header_index0, [(line_index0, text), ...])}``. Lines with
    a colon (e.g. ``# STATUS: APPROVED``) are not treated as section headers.
    """
    sections: Dict[str, Tuple[int, List[Tuple[int, str]]]] = {}
    current: Optional[str] = None
    header_index = 0
    body: List[Tuple[int, str]] = []
    for index, line in enumerate(lines):
        match = _SECTION_HEADER.match(line)
        if match:
            if current is not None:
                sections[current] = (header_index, body)
            current = " ".join(match.group(1).split()).upper()
            header_index = index
            body = []
        elif current is not None:
            body.append((index, line))
    if current is not None:
        sections[current] = (header_index, body)
    return sections


class PseudocodeAnalyzer:
    """Analyze a starterfile for structural consistency before generation."""

    def __init__(
        self,
        starterfile: str,
        project_root: Optional[str] = None,
        llm_interface=None,
        use_llm: bool = False,
    ) -> None:
        self.starterfile = Path(starterfile).expanduser()
        self.project_root = (
            Path(project_root).expanduser().resolve()
            if project_root
            else self.starterfile.resolve().parent
        )
        self.llm_interface = llm_interface
        self.use_llm = use_llm
        self._lines: List[str] = []
        self._report: Optional[AnalysisReport] = None

    # -- analysis --------------------------------------------------------
    def analyze(self) -> AnalysisReport:
        report = AnalysisReport(path=str(self.starterfile))
        try:
            text = self.starterfile.read_text(encoding="utf-8")
        except OSError as exc:
            report.errors.append(Tag(1, "ERROR", "missing-file", str(exc)))
            self._report = report
            return report

        self._lines = text.splitlines()
        sections = _split_sections(self._lines)

        self._check_status(report)
        self._check_required_sections(report, sections)
        pseudocode_paths = self._check_pseudocode(report, sections)
        self._check_databases(report, sections)
        repomap_dirs = self._check_repomap(report, sections)
        self._check_overall_structure(report, repomap_dirs, pseudocode_paths)

        self._report = report
        return report

    def _add(
        self,
        report: AnalysisReport,
        severity: str,
        line: int,
        code: str,
        message: str,
    ) -> None:
        tag = Tag(max(1, line), severity, code, message)
        (report.errors if severity == "ERROR" else report.warnings).append(tag)

    def _check_status(self, report: AnalysisReport) -> None:
        for index, line in enumerate(self._lines):
            match = _STATUS_MARKER.match(line)
            if match:
                if match.group(1).upper() != "APPROVED":
                    self._add(
                        report, "ERROR", index + 1, "status-not-approved",
                        "STATUS is {!r}; expected APPROVED".format(match.group(1)),
                    )
                return
        self._add(
            report, "ERROR", 1, "status-missing",
            "Missing '# STATUS: APPROVED' approval marker",
        )

    def _check_required_sections(self, report, sections) -> None:
        for name in REQUIRED_SECTIONS:
            if name not in sections:
                self._add(
                    report, "ERROR", 1, "section-missing",
                    "Required section '# {}' is missing".format(name),
                )

    def _check_pseudocode(self, report, sections) -> List[str]:
        entry = sections.get("PSEUDOCODE")
        if entry is None:
            return []
        header_index, body = entry
        if _is_none_body("\n".join(text for _, text in body)):
            return []

        paths: List[str] = []
        seen: Dict[str, int] = {}
        current_path: Optional[str] = None
        current_line = header_index + 1
        body_buffer: List[str] = []
        header_fields: Dict[str, List[Tuple[str, str, int]]] = {}

        def flush() -> None:
            if current_path is None:
                return
            has_task = any(
                label == "TASK" for label, _, _ in header_fields.get(current_path, [])
            )
            if not has_task and not body_buffer:
                self._add(
                    report, "WARNING", current_line, "pseudocode-empty",
                    "PSEUDOCODE entry {!r} has no body or TASK".format(current_path),
                )
            elif not has_task:
                self._add(
                    report, "WARNING", current_line, "task-missing",
                    "PSEUDOCODE entry {!r} has no TASK field".format(current_path),
                )
            self._check_function_model(report, current_path, current_line, body_buffer)

        for index, text in body:
            match = _PSEUDO_HEADER.match(text)
            if match:
                flush()
                current_path = match.group(1).strip()
                current_line = index + 1
                body_buffer = []
                paths.append(current_path)
                if current_path in seen:
                    self._add(
                        report, "ERROR", index + 1, "duplicate-header",
                        "Duplicate PSEUDOCODE header {!r} (first at line {})".format(
                            current_path, seen[current_path]
                        ),
                    )
                else:
                    seen[current_path] = index + 1
                # Validate the path itself.
                if Path(current_path).is_absolute():
                    self._add(
                        report, "ERROR", index + 1, "absolute-path",
                        "PSEUDOCODE path must be project-relative: {}".format(
                            current_path
                        ),
                    )
                normalized = posixpath.normpath(current_path)
                if normalized == ".." or normalized.startswith("../"):
                    self._add(
                        report, "ERROR", index + 1, "path-escape",
                        "PSEUDOCODE path escapes the project root: {}".format(
                            current_path
                        ),
                    )
                suffix = Path(current_path).suffix.lower()
                if not suffix:
                    self._add(
                        report, "WARNING", index + 1, "no-extension",
                        "PSEUDOCODE path has no file extension: {}".format(
                            current_path
                        ),
                    )
                elif suffix not in KNOWN_EXTENSIONS:
                    self._add(
                        report, "WARNING", index + 1, "unknown-extension",
                        "Unrecognized extension {!r} for {}".format(
                            suffix, current_path
                        ),
                    )
            else:
                if current_path is not None:
                    body_buffer.append(text)
                    field = _FIELD_LABEL.match(text)
                    if field:
                        header_fields.setdefault(current_path, []).append(
                            (
                                " ".join(field.group(1).split()),
                                field.group(2),
                                index + 1,
                            )
                        )
        flush()
        return paths

    def _check_function_model(self, report, path, line, body_lines) -> None:
        """Validate an entry's optional FUNCTION MODEL.

        Delegates to :mod:`code_starter.function_model`. Absence is allowed here
        (the UI can require it); malformed models, duplicate functions, missing
        formulas/criteria and unparseable math are reported as tags.
        """
        from code_starter import function_model as fm

        _, findings = fm.analyze("\n".join(body_lines))
        for finding in findings:
            self._add(report, finding.severity, line, finding.code, finding.message)

    def _check_databases(self, report, sections) -> List[str]:
        entry = sections.get("DATABASES")
        if entry is None:
            return []
        _, body = entry
        text = "\n".join(line for _, line in body)
        if _is_none_body(text):
            return []
        try:
            from code_starter.sql_schema_creator import (
                DatabaseSpecError,
                parse_database_specs,
            )
        except Exception:  # pragma: no cover - import guard
            return []
        try:
            specs = parse_database_specs(text)
        except DatabaseSpecError as exc:
            self._add(report, "ERROR", entry[0] + 1, "database-spec", str(exc))
            return []
        return [filename for filename, _ in specs]

    def _check_repomap(self, report, sections) -> List[str]:
        entry = sections.get("REPOMAP")
        if entry is None:
            return []
        _, body = entry
        if _is_none_body("\n".join(line for _, line in body)):
            self._add(
                report, "WARNING", entry[0] + 1, "repomap-none",
                "REPOMAP is NONE; directories will be inferred from PSEUDOCODE",
            )
            return []
        return self._repomap_directories()

    def _repomap_directories(self) -> List[str]:
        try:
            from code_starter.blueprint_renderer import parse_repomap
        except Exception:  # pragma: no cover - import guard
            return []
        parsed = parse_repomap(str(self.starterfile)) or {"directories": []}
        return list(parsed.get("directories", []))

    def _check_overall_structure(self, report, repomap_dirs, pseudocode_paths) -> None:
        if not repomap_dirs or not pseudocode_paths:
            return
        normalized_dirs = [posixpath.normpath(d) for d in repomap_dirs]

        for path in pseudocode_paths:
            normalized = posixpath.normpath(path)
            if not any(
                normalized == d or normalized.startswith(d + "/")
                for d in normalized_dirs
            ):
                line = self._line_of_header(path)
                self._add(
                    report, "WARNING", line, "structure-orphan-file",
                    "PSEUDOCODE file {!r} is not under any REPOMAP directory".format(
                        path
                    ),
                )

        for directory in normalized_dirs:
            if not any(
                posixpath.normpath(p) == directory
                or posixpath.normpath(p).startswith(directory + "/")
                for p in pseudocode_paths
            ):
                self._add(
                    report, "WARNING", self._line_of_section("REPOMAP"),
                    "structure-empty-dir",
                    "REPOMAP directory {!r} has no PSEUDOCODE file".format(directory),
                )

    def _line_of_header(self, path: str) -> int:
        for index, line in enumerate(self._lines):
            match = _PSEUDO_HEADER.match(line)
            if match and match.group(1).strip() == path:
                return index + 1
        return 1

    def _line_of_section(self, name: str) -> int:
        for index, line in enumerate(self._lines):
            match = _SECTION_HEADER.match(line)
            if match and " ".join(match.group(1).split()).upper() == name:
                return index + 1
        return 1

    # -- outputs ---------------------------------------------------------
    def write_report(self, report_path: Optional[str] = None) -> Path:
        report = self._report or self.analyze()
        if report_path is None:
            target = self.project_root / "docs" / "pseudocode_report.md"
        else:
            target = Path(report_path).expanduser()
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(report.to_markdown(), encoding="utf-8")
        return target

    def write_tagged_copy(self, output_path: Optional[str] = None) -> Optional[Path]:
        """Write a tagged copy of the starterfile (original left untouched)."""
        report = self._report or self.analyze()
        if not self._lines:
            return None
        if output_path is None:
            stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            target = (
                self.project_root
                / "tmp"
                / "{}.{}.tagged".format(self.starterfile.name, stamp)
            )
        else:
            target = Path(output_path).expanduser()
        target.parent.mkdir(parents=True, exist_ok=True)

        insertions: Dict[int, List[Tag]] = {}
        for tag in report.tags:
            insertions.setdefault(tag.line, []).append(tag)

        out: List[str] = ["# === pseudocode_analyzer tags ==="]
        for tag in report.tags:
            out.append(tag.render())
        if not report.tags:
            out.append("# TAG: INFO: clean: no issues found")
        out.append("# === end tags ===")
        out.append("")
        for index, line in enumerate(self._lines, start=1):
            out.append(line)
            for tag in insertions.get(index, []):
                out.append(tag.render())
        target.write_text("\n".join(out) + "\n", encoding="utf-8")
        return target


def analyze_starterfile(
    starterfile: str,
    project_root: Optional[str] = None,
    use_llm: bool = False,
    llm_interface=None,
) -> AnalysisReport:
    """Analyze ``starterfile`` and return the report."""
    return PseudocodeAnalyzer(
        starterfile,
        project_root=project_root,
        use_llm=use_llm,
        llm_interface=llm_interface,
    ).analyze()
