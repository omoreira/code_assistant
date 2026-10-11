"""Section-level and whole-file verification, using the repository's parsers.

Per-section verification (recommendation from the plan): the whole-file
:class:`~code_analyzer.pseudocode_analyzer.PseudocodeAnalyzer` needs every
required section plus ``# STATUS: APPROVED``. To verify one section in
isolation we assemble a minimal, otherwise-valid starterfile (placeholder
sections marked ``NONE``) and run the real analyzer, then surface its findings.
Sections with a dedicated parser (REPOMAP, DATABASES) are checked with those
parsers directly.
"""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Tuple

from code_analyzer.pseudocode_analyzer import PseudocodeAnalyzer
from code_starter.blueprint_renderer import parse_repomap
from code_starter.sql_schema_creator import (
    DatabaseSpecError,
    parse_database_specs,
    render_schema,
)
from code_starter.starterfile_builder import StarterfileBuilder

_NONE_TOKENS = {"", "NONE", "EMPTY"}


def _is_none(body: str) -> bool:
    return body.strip().upper() in _NONE_TOKENS


def verify_paths(root: str, data_dir: str) -> Tuple[bool, str]:
    """Validate the ``# PATHS`` entries."""
    problems = []
    if not (root or "").strip():
        problems.append("root is empty")
    if not (data_dir or "").strip():
        problems.append("data_dir is empty")
    if problems:
        return False, "; ".join(problems)
    return True, "PATHS looks valid (root={!r}, data_dir={!r})".format(root, data_dir)


def verify_repomap(text: str) -> Tuple[bool, str]:
    """Validate a ``# REPOMAP`` body by parsing it for directories."""
    body = text.strip("\n")
    if _is_none(body):
        return True, "REPOMAP is NONE (directories will be inferred from PSEUDOCODE)"
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "starterfile.pseudo"
        path.write_text(
            "# REPOMAP\n" + body + "\n\n# PSEUDOCODE\nNONE\n", encoding="utf-8"
        )
        parsed = parse_repomap(str(path)) or {"directories": []}
    directories = parsed.get("directories", [])
    if not directories:
        return False, "REPOMAP produced no directories; check indentation and names."
    return True, "REPOMAP defines {} directory(ies)".format(len(directories))


def verify_databases(text: str) -> Tuple[bool, str]:
    """Validate a ``# DATABASES`` body via parse + render (catches key rules)."""
    body = text.strip("\n")
    if _is_none(body):
        return True, "DATABASES is NONE (no databases will be created)"
    try:
        specs = parse_database_specs(body)
        for filename, tables in specs:
            render_schema(filename, tables)
    except DatabaseSpecError as exc:
        return False, str(exc)
    return True, "DATABASES defines {} database(s)".format(len(specs))


def verify_pseudocode(text: str) -> Tuple[bool, str]:
    """Validate a ``# PSEUDOCODE`` body using the full analyzer."""
    body = text.strip("\n")
    if _is_none(body):
        return True, "PSEUDOCODE is NONE (no files will be generated)"
    builder = StarterfileBuilder("starterfile.pseudo")
    builder.repomap = "NONE"
    builder.databases = "NONE"
    builder.pseudocode = body
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "starterfile.pseudo"
        path.write_text(builder.render(), encoding="utf-8")
        report = PseudocodeAnalyzer(str(path), project_root=tmp).analyze()
    if report.errors:
        return False, _render_tags(report.errors, report.warnings)
    message = "PSEUDOCODE passed verification"
    if report.warnings:
        message += " ({} warning(s) — see below)".format(len(report.warnings))
    if report.warnings:
        message += "\n" + _render_tags([], report.warnings)
    return True, message


def verify_starterfile(path) -> Tuple[bool, str]:
    """Run the full analyzer against a starterfile on disk."""
    target = Path(path)
    if not target.is_file():
        return False, "starterfile not found: {}".format(target)
    report = PseudocodeAnalyzer(str(target)).analyze()
    summary = (
        "starterfile passed verification"
        if report.ok
        else "starterfile has {} error(s)".format(len(report.errors))
    )
    detail = _render_tags(report.errors, report.warnings)
    return report.ok, summary + ("\n\n" + detail if detail else "")


def _render_tags(errors, warnings) -> str:
    lines = []
    for tag in errors:
        lines.append("ERROR   line {}: `{}` — {}".format(tag.line, tag.code, tag.message))
    for tag in warnings:
        lines.append("WARNING line {}: `{}` — {}".format(tag.line, tag.code, tag.message))
    return "\n".join(lines)
