"""Converter page: ``pseudo2code`` and ``longtext2pseudo`` tasks."""

from __future__ import annotations

from pathlib import Path

import streamlit as st

from core import paths as ui_paths
from core.llm import get_llm

_DOCKER_CHOICES = {"Auto": None, "Include Docker files": True, "Exclude Docker files": False}


def _init_state() -> None:
    ss = st.session_state
    ss.setdefault("conv_project_root", str(ui_paths.REPO_ROOT))
    ss.setdefault("p2c_input", "")
    ss.setdefault("p2c_output", "")
    ss.setdefault("lt_notes", "")
    ss.setdefault("lt_notes_file", "")
    ss.setdefault("lt_output", "patch.pseudo")
    ss.setdefault("lt_docker", "Auto")


def _target(relative: str) -> Path:
    return Path(st.session_state.conv_project_root).expanduser() / relative


def _pseudo2code() -> None:
    ss = st.session_state
    st.caption("Convert one pseudocode-bearing file into real code for its language.")
    st.text_input("Pseudocode file (project-relative)", key="p2c_input")
    st.text_input("Output file (optional; blank overwrites the input)", key="p2c_output")
    if st.button("Convert", type="primary", key="p2c_run"):
        if not ss.p2c_input.strip():
            st.error("Enter a file path first.")
            return
        target = _target(ss.p2c_input)
        if not target.is_file():
            st.error("File not found: {}".format(target))
            return
        output = ss.p2c_output.strip()
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
        except Exception as exc:  # noqa: BLE001
            st.error("Conversion failed: {}".format(exc))


def _longtext2pseudo() -> None:
    ss = st.session_state
    st.caption("Turn long research notes into a structured ``patch.pseudo`` document.")
    st.text_area("Paste research notes (optional)", key="lt_notes", height=220)
    st.text_input(
        "…or path to a notes file (project-relative or absolute)", key="lt_notes_file"
    )
    st.text_input("Output file", key="lt_output")
    st.radio("Docker files", list(_DOCKER_CHOICES), key="lt_docker", horizontal=True)

    if st.button("Generate pseudocode", type="primary", key="lt_run"):
        notes_file = ss.lt_notes_file.strip()
        output = ss.lt_output.strip() or "patch.pseudo"
        docker_support = _DOCKER_CHOICES[ss.lt_docker]
        try:
            from code_converter.longtext_pseudo_converter import LongContextReader

            reader = LongContextReader(get_llm("generation"))
            if notes_file:
                candidate = _target(notes_file)
                if not candidate.is_file():
                    candidate = Path(notes_file).expanduser()
                reader.create_from_files(
                    [str(candidate)], output, docker_support=docker_support
                )
            elif ss.lt_notes.strip():
                reader.create_pseudocode(
                    ss.lt_notes, output, docker_support=docker_support
                )
            else:
                st.error("Provide notes text or a notes file path.")
                return
            st.success("Wrote {}".format(output))
            st.code(Path(output).read_text(encoding="utf-8", errors="replace"), language="text")
        except Exception as exc:  # noqa: BLE001
            st.error("Generation failed: {}".format(exc))


def render() -> None:
    _init_state()
    st.header("Converter")
    st.text_input("Project root", key="conv_project_root")
    tab_p2c, tab_lt = st.tabs(["pseudo2code", "longtext2pseudo"])
    with tab_p2c:
        _pseudo2code()
    with tab_lt:
        _longtext2pseudo()
