"""UI tests for the interactive Databases builder in the Starter page.

Drives the real page through Streamlit's ``AppTest``: add database -> table ->
identifier column, then Verify + Append to disk. Popovers are transparent to
AppTest, so the widgets inside them are addressed by their (stable) keys; form
submit buttons surface as ``FormSubmitter:<form-key>-<label>``.
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
    """Click the submit button of the form whose key starts with ``form_prefix``."""
    for button in at.button:
        if (button.key or "").startswith("FormSubmitter:" + form_prefix):
            button.click()
            return at
    raise AssertionError("form submit not found: " + form_prefix)


def _add_database(at, filename):
    at.text_input(key="dbb-add-db-name").set_value(filename)
    return _submit_form(at, "dbb-add-db").run()


def _add_table(at, filename_index, name):
    at.text_input(key="dbb-add-table-name-{}".format(filename_index)).set_value(name)
    return _submit_form(at, "dbb-add-table-{}".format(filename_index)).run()


def _add_column(at, db_index, table_index, name, desc=""):
    at.text_input(key="dbb-add-col-name-{}-{}".format(db_index, table_index)).set_value(name)
    at.text_input(key="dbb-add-col-desc-{}-{}".format(db_index, table_index)).set_value(desc)
    return _submit_form(at, "dbb-add-col-{}-{}".format(db_index, table_index)).run()


def test_add_database_updates_section_text(tmp_path):
    at = _app(tmp_path).run()
    _add_database(at, "app.db")
    assert not at.exception, [str(e.value) for e in at.exception]
    assert at.session_state["sf_databases"] == "app.db"
    assert at.session_state["sf_databases_model"] == [{"file": "app.db", "tables": []}]


def test_build_full_database(tmp_path):
    at = _app(tmp_path).run()
    _add_database(at, "app.db")
    _add_table(at, 0, "users")
    _add_column(at, 0, 0, "identifier", "primary key")
    _add_column(at, 0, 0, "name", "display name")

    assert not at.exception, [str(e.value) for e in at.exception]
    text = at.session_state["sf_databases"]
    assert "app.db" in text
    assert "table 1 name: users" in text
    assert "- identifier: primary key" in text
    assert "- name: display name" in text


def test_append_writes_databases_section_to_disk(tmp_path):
    project = tmp_path / "proj"
    project.mkdir()

    at = _app(tmp_path).run()
    at.text_input(key="w_starter_project_root").set_value(str(project)).run()
    at.button(key="starter_create").click().run()

    _add_database(at, "app.db")
    _add_table(at, 0, "users")
    _add_column(at, 0, 0, "identifier", "primary key")

    at.button(key="verify_databases").click().run()
    assert not at.exception, [str(e.value) for e in at.exception]
    at.button(key="save_databases").click().run()
    assert not at.exception, [str(e.value) for e in at.exception]

    written = (project / "starterfile.pseudo").read_text(encoding="utf-8")
    assert "app.db" in written
    assert "table 1 name: users" in written
    assert "- identifier: primary key" in written
    assert at.session_state["sf_appended"].get("databases") is True


def test_removal_rewrites_section_on_disk(tmp_path):
    project = tmp_path / "proj"
    project.mkdir()

    at = _app(tmp_path).run()
    at.text_input(key="w_starter_project_root").set_value(str(project)).run()
    at.button(key="starter_create").click().run()

    _add_database(at, "app.db")
    _add_table(at, 0, "users")
    _add_column(at, 0, 0, "identifier")

    at.button(key="verify_databases").click().run()
    at.button(key="save_databases").click().run()
    assert "table 1 name: users" in (project / "starterfile.pseudo").read_text(encoding="utf-8")

    # Removing the database must rewrite the already-appended section on disk.
    at.button(key="dbb-del-db-0").click().run()
    assert not at.exception, [str(e.value) for e in at.exception]
    written = (project / "starterfile.pseudo").read_text(encoding="utf-8")
    assert "app.db" not in written
