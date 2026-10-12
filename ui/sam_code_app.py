"""Streamlit UI for the code-assistant toolkit.

Run from the repository root:

    streamlit run ui/sam_code_app.py

Or from inside `ui/`:

    streamlit run sam_code_app.py

The app wraps the packages under ``src/`` (code_starter, code_converter,
code_analyzer) and keeps only presentation logic here. Application logic lives
in ``src/`` per ui/README.md.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Make the repo's `src/` packages and this UI's own modules importable.
REPO_ROOT = Path(__file__).resolve().parents[1]
UI_DIR = REPO_ROOT / "ui"
for _path in (str(REPO_ROOT / "src"), str(UI_DIR)):
    if _path not in sys.path:
        sys.path.insert(0, _path)

import streamlit as st

from core.llm import require_ollama
from views import converter, editor, patcher, starter

st.set_page_config(
    page_title="Code Assistant UI",
    page_icon="🛠️",
    layout="wide",
)

# Hard-block when Ollama is unavailable (all LLM-backed pages depend on it).
require_ollama()

# Every page callable is named `render`, and st.Page infers a page's URL
# pathname from the callable's __name__ (not from the title), so we must give
# each page an explicit, unique url_path — otherwise Streamlit raises
# "Multiple Pages specified with URL pathname render".
navigation = st.navigation(
    [
        st.Page(starter.render, title="Starter", icon="🧭", url_path="starter", default=True),
        st.Page(editor.render, title="Editor", icon="📝", url_path="editor"),
        st.Page(converter.render, title="Converter", icon="🔄", url_path="converter"),
        st.Page(patcher.render, title="Patcher", icon="🩹", url_path="patcher"),
    ]
)
navigation.run()
