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

import base64
import sys
from datetime import date
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

# --- Branding -------------------------------------------------------------
ASSETS_DIR = UI_DIR / "assets"
LOGO_PATH = ASSETS_DIR / "omsys_logo.png"  # real logo, used when USE_REAL_LOGO is True

BRAND_NAME = "Sam Local Code Assistant"  # shown under the logo in the sidebar header
WEBSITE_URL = "https://github.com/omoreira/code_assistant"

COMPANY_NAME = "OM Synaptic Systems Inc."  # legal entity, used in the footer
AUTHOR = "Olga Moreira"
COPYRIGHT_YEAR = date.today().year

LOGO_WIDTH = 160  # px, rendered width of the sidebar logo / placeholder
USE_REAL_LOGO = False  # False -> show a placeholder logo until the real one is ready


def _brandmark_html() -> str:
    """A centered, clickable brand mark with the brand name directly below it.

    ``st.image`` can hyperlink (``link=``) but cannot center itself, so the
    sidebar brand mark is rendered as HTML. When ``USE_REAL_LOGO`` is set and
    the asset exists, the logo is embedded as a base64 data URI (self-contained,
    no static-file server needed); otherwise a neutral placeholder box is shown.
    """
    if USE_REAL_LOGO and LOGO_PATH.is_file():
        encoded = base64.b64encode(LOGO_PATH.read_bytes()).decode("ascii")
        mark = (
            f'<img src="data:image/png;base64,{encoded}" width="{LOGO_WIDTH}" '
            f'alt="{BRAND_NAME}" style="display:block;margin:0 auto;"/>'
        )
    else:
        mark = (
            f'<div style="width:{LOGO_WIDTH}px;height:{LOGO_WIDTH}px;'
            "margin:0 auto;border:2px dashed #9aa0a6;border-radius:10px;"
            "display:flex;align-items:center;justify-content:center;"
            'color:#9aa0a6;font-size:0.8rem;letter-spacing:0.08em;">LOGO</div>'
        )
    return (
        '<div style="text-align:center;">'
        f'<a href="{WEBSITE_URL}" target="_blank" rel="noopener noreferrer">'
        f"{mark}</a>"
        '<div style="margin-top:0.4rem;font-weight:600;line-height:1.25;">'
        f"{BRAND_NAME}</div></div>"
    )


st.set_page_config(
    page_title="Code Assistant UI",
    page_icon="🛠️",
    layout="wide",
)

# Hard-block when Ollama is unavailable (all LLM-backed pages depend on it).
require_ollama()

# --- Sidebar: custom header + custom navigation + footer ------------------
# Streamlit pins its built-in `st.navigation` menu to the very top of the
# sidebar and offers no supported way to place other content above it (only
# `st.logo` can sit there). To group the logo with the company name *above*
# the navigation items, we hide the built-in menu (position="hidden") and
# compose the whole sidebar ourselves: header, navigation links, then footer.
#
# Every page callable is named `render`, and st.Page infers a page's URL
# pathname from the callable's __name__ (not from the title) when no url_path
# is given, so each page needs an explicit, unique url_path — otherwise
# Streamlit raises "Multiple Pages specified with URL pathname render".
PAGES = [
    st.Page(starter.render, title="Starter", icon="🧭", url_path="starter", default=True),
    st.Page(editor.render, title="Editor", icon="📝", url_path="editor"),
    st.Page(converter.render, title="Converter", icon="🔄", url_path="converter"),
    st.Page(patcher.render, title="Assistant", icon="🔍", url_path="patcher"),
]

# `st.navigation` must run before any `st.page_link` so the pages are registered.
navigation = st.navigation(PAGES, position="hidden")

with st.sidebar:
    # Header: centered, clickable logo placeholder with the brand name below it.
    st.markdown(_brandmark_html(), unsafe_allow_html=True)

    st.divider()

    # Navigation: one link per page (label and icon are taken from the Page).
    for page in PAGES:
        st.page_link(page)

    # Footer: proof-of-concept note and copyright at the bottom.
    st.divider()
    st.caption(
        "Proof of concept for a local code assistant, developed by "
        "{} (Founder of {}). Part of a bigger project: Sam AI.".format(
            AUTHOR, COMPANY_NAME
        )
    )
    st.caption(
        "© {} {} — All rights reserved.".format(COPYRIGHT_YEAR, COMPANY_NAME)
    )

navigation.run()
