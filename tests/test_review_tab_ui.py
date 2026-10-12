"""UI tests for the reworked Review & Run tab.

Per the plan the tab must show the *auto-assembled* starterfile (no manual
"Reassemble from sections" button) as coloured, read-only HTML.
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


def test_reassemble_button_removed(tmp_path):
    at = _app(tmp_path).run()
    labels = [button.label for button in at.button]
    assert "Reassemble from sections" not in labels
    assert "Write assembled file" in labels
    assert "Verify whole file" in labels


def test_review_tab_renders_colored_assembled_file(tmp_path):
    project = tmp_path / "proj"
    project.mkdir()

    at = _app(tmp_path).run()
    at.text_input(key="w_starter_project_root").set_value(str(project)).run()
    at.button(key="starter_create").click().run()

    assert not at.exception, [str(e.value) for e in at.exception]
    joined = "\n".join(markdown.value for markdown in at.markdown)
    assert 'class="sf-view"' in joined
    assert "# STATUS: APPROVED" in joined
    assert "# REPOMAP" in joined
    assert "# PSEUDOCODE" in joined
