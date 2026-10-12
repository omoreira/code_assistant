"""Tests for the FUNCTION MODEL parser + validator."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from code_starter import function_model as fm  # noqa: E402

BODY = """INPUT: values
OUTPUT: score
TASK: orchestrate: load -> score -> decide
FUNCTION MODEL:
  - name: load
  - name: score
    kind: math
    inputs: values: list[float], weights: list[float]
    returns: float
    formula: sum(w * v for w, v in zip(weights, values))
    criteria: 0 <= score <= 1
  - name: decide
    kind: criteria
    inputs: score: float
    returns: str
    criteria: score >= 0.5 -> "accept" else "reject"
CONDITIONS: none
PREFERENCES: none
"""


def _codes(findings):
    return [f.code for f in findings]


def test_parse_fields():
    functions, findings = fm.analyze(BODY)
    assert [f.name for f in functions] == ["load", "score", "decide"]
    assert functions[1].kind == "math"
    assert functions[1].formula.startswith("sum(")
    assert functions[2].criteria == 'score >= 0.5 -> "accept" else "reject"'
    assert findings == []  # the model above is clean


def test_absent_field_is_ignored():
    assert fm.analyze("INPUT: x\nTASK: do it\n") == ([], [])
    assert fm.analyze("INPUT: x\nTASK: do it\n", required=True)[1][0].code == "function-model-missing"


def test_empty_field_is_error():
    _, findings = fm.analyze("FUNCTION MODEL:\nCONDITIONS: x\n")
    assert "function-model-empty" in _codes(findings)


def test_duplicate_function():
    body = "FUNCTION MODEL:\n  - name: a\n  - name: a\n"
    _, findings = fm.analyze(body)
    assert "duplicate-function" in _codes(findings)


def test_math_without_formula_and_criteria_without_criteria():
    body = "FUNCTION MODEL:\n  - name: m\n    kind: math\n  - name: c\n    kind: criteria\n"
    _, findings = fm.analyze(body)
    assert "math-function-missing-formula" in _codes(findings)
    assert "criteria-function-missing-criteria" in _codes(findings)


def test_unparseable_formula_and_criteria():
    body = (
        "FUNCTION MODEL:\n"
        "  - name: f\n    formula: sum(w *\n"
        "  - name: g\n    criteria: score >= -> accept\n"
    )
    _, findings = fm.analyze(body)
    assert "formula-unparseable" in _codes(findings)
    assert "criteria-unparseable" in _codes(findings)


def test_criteria_arrow_left_side_is_checked():
    body = "FUNCTION MODEL:\n  - name: ok\n    criteria: x > 0 -> accept\n"
    assert _codes(fm.analyze(body)[1]) == []


def test_task_reference_cross_check():
    declared = "FUNCTION MODEL:\n  - name: load\n"
    assert _codes(fm.analyze(declared + "TASK: run: load()\n")[1]) == []
    assert "task-references-unknown-function" in _codes(
        fm.analyze(declared + "TASK: run: missing()\n")[1]
    )
    # arrow chains are treated as step references; declared ones are fine
    chain = "FUNCTION MODEL:\n  - name: a\n  - name: b\n"
    assert _codes(fm.analyze(chain + "TASK: a -> b\n")[1]) == []


def test_render_roundtrip_is_stable():
    functions, _ = fm.analyze(BODY)
    once = fm.render(functions)
    twice = fm.render(fm.parse(once)[0])
    assert once == twice
    assert once.startswith("FUNCTION MODEL:")


def test_split_task():
    assert fm.split_task(BODY) == "orchestrate: load -> score -> decide"
