"""Analyzer integration: FUNCTION MODEL findings surface as tags."""

from __future__ import annotations

from pathlib import Path

from code_analyzer.pseudocode_analyzer import PseudocodeAnalyzer

BASE = """# STATUS: APPROVED

# REPOMAP

smoke-project
    |______ src/

# DATABASES

NONE

# PSEUDOCODE

## smoke-project/src/app.py
INPUT: values
TASK: run: score() -> decide()
FUNCTION MODEL:
  - name: score
    kind: math
  - name: score
    criteria: x >= -> ok
"""

VALID_MODEL = (
    "  - name: score\n"
    "    kind: math\n"
    "    formula: sum(v)\n"
    "  - name: decide\n"
    "    kind: criteria\n"
    "    criteria: score >= 0.5 -> accept\n"
)
BAD_MODEL = "  - name: score\n    kind: math\n  - name: score\n    criteria: x >= -> ok\n"


def _report(tmp_path: Path, body: str):
    path = tmp_path / "starterfile.pseudo"
    path.write_text(body, encoding="utf-8")
    return PseudocodeAnalyzer(str(path), project_root=str(tmp_path)).analyze()


def test_function_model_findings_become_tags(tmp_path):
    report = _report(tmp_path, BASE)
    error_codes = {tag.code for tag in report.errors}
    assert "math-function-missing-formula" in error_codes
    assert "duplicate-function" in error_codes
    assert "task-references-unknown-function" in error_codes
    assert "criteria-unparseable" in {tag.code for tag in report.warnings}


def test_valid_function_model_is_clean(tmp_path):
    report = _report(tmp_path, BASE.replace(BAD_MODEL, VALID_MODEL))
    assert report.ok
    assert report.warnings == []
