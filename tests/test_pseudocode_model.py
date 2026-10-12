"""Tests for the pure ``# PSEUDOCODE`` model (parse/render/folders/validate)."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
for _p in (REPO_ROOT / "ui", REPO_ROOT / "src"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from core import pseudocode_model as pm  # noqa: E402
from core.verify import verify_pseudocode  # noqa: E402


def _entry(path, task="compute the total", **fields):
    values = {
        "INPUT": "a",
        "OUTPUT": "b",
        "TASK": task,
        "CONDITIONS": "none",
        "PREFERENCES": "stdlib",
    }
    values.update(fields)
    return {"path": path, "fields": values, "functions": []}


def test_parse_none_and_blank():
    for value in ("", "   ", "NONE", "none", "EMPTY"):
        assert pm.parse(value) == []
    assert pm.render([]) == ""


def test_roundtrip_multiline_fields_and_functions():
    model = [
        {
            "path": "src/pkg/module.py",
            "fields": {
                "INPUT": "reads lines",
                "OUTPUT": "writes rows",
                "TASK": "parse input\nthen load rows",
                "CONDITIONS": "none",
                "PREFERENCES": "stdlib",
            },
            "functions": [
                {
                    "name": "score",
                    "kind": "math",
                    "inputs": "values: list[float]",
                    "returns": "float",
                    "formula": "sum(values) / len(values)",
                    "criteria": "",
                }
            ],
        }
    ]
    assert pm.parse(pm.render(model)) == model


def test_verify_pseudocode_accepts_rendered_model():
    entry = _entry("src/pkg/module.py", task="call score(values)")
    entry["functions"] = [
        {
            "name": "score",
            "kind": "math",
            "inputs": "values: list[float]",
            "returns": "float",
            "formula": "sum(values) / len(values)",
            "criteria": "",
        }
    ]
    ok, message = verify_pseudocode(pm.render([entry]))
    assert ok, message


def test_folders_from_repomap():
    text = "src/\n    code_starter/\n        nested/\nui/\n    views/"
    assert pm.folders_from_repomap(text) == [
        "src",
        "src/code_starter",
        "src/code_starter/nested",
        "ui",
        "ui/views",
    ]
    assert pm.folders_from_repomap("NONE") == []


def test_join_path():
    assert pm.join_path("src/pkg", "module") == "src/pkg/module.py"
    assert pm.join_path("src/pkg", "module.py") == "src/pkg/module.py"
    assert pm.join_path("(root)", "main.py") == "main.py"
    assert pm.join_path("", "main.py") == "main.py"


def test_orphan_paths():
    entries = [_entry("src/a.py"), _entry("other/b.py")]
    assert pm.orphan_paths(entries, ["src"]) == ["other/b.py"]
    assert pm.orphan_paths(entries, []) == []


def test_entry_problems():
    entry = _entry("other/b.py", task="")
    problems = pm.entry_problems(entry, ["src"])
    assert any("TASK" in p for p in problems)
    assert any("REPOMAP" in p for p in problems)


def test_function_findings_report_missing_formula():
    entry = _entry("src/a.py", task="compute")
    entry["functions"] = [
        {"name": "score", "kind": "math", "inputs": "", "returns": "", "formula": "", "criteria": ""}
    ]
    codes = {finding.code for finding in pm.function_findings(entry)}
    assert "math-function-missing-formula" in codes


def test_add_and_remove_helpers():
    entries = []
    entry = pm.add_entry(entries, "src/a.py")
    pm.add_function(entry, "score")
    assert pm.count(entries) == 1
    assert pm.count_functions(entries) == 1
    pm.remove_function(entry, 0)
    pm.remove_entry(entries, 0)
    assert entries == []
