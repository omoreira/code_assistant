"""UI tests for the interactive Pseudocode builder in the Starter page.

Drives the real page through ``AppTest``: add a script module, edit a field,
add a FUNCTION MODEL function, then Verify + Append to disk. Form submits
surface as ``FormSubmitter:<form-key>-<label>`` buttons.
"""

from __future__ import annotations

import sys
from pathlib import Path

from streamlit.testing.v1 import AppTest

REPO_ROOT = Path(__file__).resolve().parents[1]
UI_DIR = REPO_ROOT / "ui"
SRC_DIR = REPO_ROOT / "src"

for _p in (SRC_DIR, UI_DIR):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

_SCRIPT = (
    "import sys\n"
    "sys.path.insert(0, {src!r})\n"
    "sys.path.insert(0, {ui!r})\n"
    "from views import starter\n"
    "starter.render()\n"
)


def _app(tmp_path: Path) -> AppTest:
    script = tmp_path / "_starter_page.py"
    script.write_text(_SCRIPT.format(src=str(SRC_DIR), ui=str(UI_DIR)), encoding="utf-8")
    return AppTest.from_file(str(script), default_timeout=60)


def _submit_form(at: AppTest, form_prefix: str):
    for button in at.button:
        if (button.key or "").startswith("FormSubmitter:" + form_prefix):
            button.click()
            return at
    raise AssertionError("form submit not found: " + form_prefix)


def _add_module(at, filename):
    at.text_input(key="pb-add-filename").set_value(filename)
    return _submit_form(at, "pb-add-entry").run()


def test_add_module_updates_section_text(tmp_path):
    at = _app(tmp_path).run()
    _add_module(at, "main.py")
    assert not at.exception, [str(e.value) for e in at.exception]
    assert "## main.py" in at.session_state["sf_pseudocode"]
    assert at.session_state["sf_pseudocode_model"][0]["path"] == "main.py"


def test_edit_task_field(tmp_path):
    at = _app(tmp_path).run()
    _add_module(at, "main.py")
    at.text_area(key="pb-field-0-TASK").set_value("compute the totals").run()
    assert not at.exception, [str(e.value) for e in at.exception]
    assert "TASK: compute the totals" in at.session_state["sf_pseudocode"]


def test_add_function_model_entry(tmp_path):
    at = _app(tmp_path).run()
    _add_module(at, "main.py")
    at.text_input(key="pb-add-fn-name-0").set_value("score")
    at.text_input(key="pb-add-fn-formula-0").set_value("sum(values) / len(values)")
    _submit_form(at, "pb-add-fn-0").run()

    assert not at.exception, [str(e.value) for e in at.exception]
    text = at.session_state["sf_pseudocode"]
    assert "- name: score" in text
    assert "formula: sum(values) / len(values)" in text


def test_append_pseudocode_to_disk(tmp_path):
    project = tmp_path / "proj"
    project.mkdir()

    at = _app(tmp_path).run()
    at.text_input(key="w_starter_project_root").set_value(str(project)).run()
    at.button(key="starter_create").click().run()

    _add_module(at, "main.py")
    at.text_area(key="pb-field-0-TASK").set_value("compute the totals").run()

    at.button(key="verify_pseudocode").click().run()
    assert not at.exception, [str(e.value) for e in at.exception]
    at.button(key="save_pseudocode").click().run()
    assert not at.exception, [str(e.value) for e in at.exception]

    written = (project / "starterfile.pseudo").read_text(encoding="utf-8")
    assert "## main.py" in written
    assert "TASK: compute the totals" in written
    assert at.session_state["sf_appended"].get("pseudocode") is True


def test_module_removal_rewrites_disk(tmp_path):
    project = tmp_path / "proj"
    project.mkdir()

    at = _app(tmp_path).run()
    at.text_input(key="w_starter_project_root").set_value(str(project)).run()
    at.button(key="starter_create").click().run()

    _add_module(at, "main.py")
    at.text_area(key="pb-field-0-TASK").set_value("compute the totals").run()
    at.button(key="verify_pseudocode").click().run()
    at.button(key="save_pseudocode").click().run()
    assert "## main.py" in (project / "starterfile.pseudo").read_text(encoding="utf-8")

    at.button(key="pb-del-entry-0").click().run()
    assert not at.exception, [str(e.value) for e in at.exception]
    written = (project / "starterfile.pseudo").read_text(encoding="utf-8")
    assert "## main.py" not in written
