"""Editor page: create or edit a pseudocode file and convert it to real code."""

from __future__ import annotations

from pathlib import Path

import streamlit as st

from core import paths as ui_paths
from core.llm import get_llm
from core.local_path_picker import render_path_picker


def _init_state() -> None:
    ss = st.session_state
    ss.setdefault("editor_project_root", str(ui_paths.REPO_ROOT))
    ss.setdefault("editor_input", "")
    ss.setdefault("editor_output", "")
    ss.setdefault("editor_text", "")


def _target(relative: str) -> Path:
    return Path(st.session_state.editor_project_root).expanduser() / relative


def render() -> None:
    _init_state()
    st.header("Editor")
    st.caption("Create or edit a pseudocode file, then convert it to real code.")

    ss = st.session_state
    render_path_picker(
        "Project root", "editor_project_root", "directory", str(ui_paths.REPO_ROOT)
    )
    render_path_picker(
        "Pseudocode file (project-relative or absolute)",
        "editor_input",
        "file",
        default_directory=ss.editor_project_root,
    )
    render_path_picker(
        "Output file (optional; blank overwrites the input file)",
        "editor_output",
        "file",
        default_directory=ss.editor_project_root,
    )

    col_load, col_save = st.columns(2)
    if col_load.button("Load file"):
        target = _target(ss.editor_input)
        if target.is_file():
            ss.editor_text = target.read_text(encoding="utf-8", errors="replace")
            st.success("Loaded {}".format(target))
        else:
            st.warning("File not found: {}".format(target))
    if col_save.button("Save file"):
        if not ss.editor_input.strip():
            st.error("Enter a file path first.")
        else:
            target = _target(ss.editor_input)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(ss.editor_text, encoding="utf-8")
            st.success("Saved {}".format(target))

    st.text_area("Pseudocode", key="editor_text", height=420)

    if st.button("Convert to code", type="primary"):
        if not ss.editor_input.strip():
            st.error("Enter a file path first.")
            return
        target = _target(ss.editor_input)
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.is_file():
            target.write_text(ss.editor_text, encoding="utf-8")
        output = ss.editor_output.strip()
        output_path = str(_target(output)) if output else None
        try:
            from code_converter.pseudofile_converter import PseudofileConverter

            written = PseudofileConverter(get_llm("analysis")).convert_file(
                str(target), output_path
            )
            st.success("Wrote code to {}".format(written))
            st.code(
                Path(written).read_text(encoding="utf-8", errors="replace"),
                language="python",
            )
        except Exception as exc:  # noqa: BLE001 - surface any conversion error
            st.error("Conversion failed: {}".format(exc))
