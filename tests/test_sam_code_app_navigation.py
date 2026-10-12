"""Regression test: sam_code_app's ``st.navigation`` pages need unique URL paths.

Every page callable in ``ui/sam_code_app.py`` is a function named ``render``,
and ``st.Page`` infers a page's URL pathname from the callable's ``__name__``
(not from the title) when no ``url_path`` is given. If the explicit ``url_path``
arguments are ever dropped, Streamlit raises::

    StreamlitAPIException: Multiple Pages specified with URL pathname render.
    URL pathnames must be unique.

This test runs the real script through Streamlit's ``AppTest`` so that
``st.navigation`` actually executes, and asserts the app starts without error.
"""

from __future__ import annotations

import sys
from pathlib import Path

from streamlit.testing.v1 import AppTest

REPO_ROOT = Path(__file__).resolve().parents[1]
ENTRY = REPO_ROOT / "ui" / "sam_code_app.py"


def test_sam_code_app_pages_have_unique_url_paths(monkeypatch):
    # ``ui/sam_code_app.py`` (and ``ui/core/llm.py``) import from both ``src/``
    # and ``ui/``; make both resolvable however pytest was invoked.
    for path in (REPO_ROOT / "src", REPO_ROOT / "ui"):
        if str(path) not in sys.path:
            sys.path.insert(0, str(path))

    # Bypass the Ollama hard-gate so the script always reaches st.navigation,
    # keeping this test independent of a running local model server.
    import core.llm as llm

    monkeypatch.setattr(llm, "require_ollama", lambda: None, raising=False)

    at = AppTest.from_file(str(ENTRY), default_timeout=60).run()

    assert not at.exception, [str(e.value) for e in at.exception]
