"""UI smoke + flow tests for the Starter page's Create-vs-Load modes.

The page is run through Streamlit's ``AppTest`` (no Ollama needed: ``views.starter``
never imports the LLM gate). These cover: rendering in each mode, and the
create flow scanning the project root then writing a starterfile to disk.
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


def test_starter_page_renders_in_create_mode(tmp_path):
    at = _app(tmp_path).run()
    assert not at.exception, [str(e.value) for e in at.exception]
    assert at.radio(key="starter_mode").value == "Create new"
    assert at.button(key="starter_scan").label
    assert at.button(key="starter_create").label


def test_starter_page_renders_in_load_mode(tmp_path):
    at = _app(tmp_path).run()
    at.radio(key="starter_mode").set_value("Load existing").run()
    assert not at.exception, [str(e.value) for e in at.exception]
    assert at.button(key="starter_load").label


def test_create_scans_root_and_writes_starterfile(tmp_path):
    project = tmp_path / "proj"
    (project / "pkg").mkdir(parents=True)
    (project / "ui" / "views").mkdir(parents=True)

    at = _app(tmp_path).run()
    at.text_input(key="w_starter_project_root").set_value(str(project)).run()
    assert not at.exception, [str(e.value) for e in at.exception]

    at.button(key="starter_scan").click().run()
    assert not at.exception, [str(e.value) for e in at.exception]
    assert "pkg/" in at.session_state["sf_repomap"]

    at.button(key="starter_create").click().run()
    assert not at.exception, [str(e.value) for e in at.exception]

    written = project / "starterfile.pseudo"
    assert written.is_file()
    text = written.read_text(encoding="utf-8")
    assert "# STATUS: APPROVED" in text
    assert "# REPOMAP" in text
    assert "pkg/" in text
