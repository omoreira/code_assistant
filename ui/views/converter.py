"""Converter page for pseudocode, research notes, and assistant contracts."""

from __future__ import annotations

import json
from pathlib import Path

import streamlit as st

from core import paths as ui_paths
from core.llm import get_llm
from core.local_path_picker import render_path_picker

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
    ss.setdefault("contract_requirements", "")
    ss.setdefault("contract_examples", "")
    ss.setdefault("contract_output", "assistant_contract.json")
    ss.setdefault("contract_model", "deepseek-r1:14b")


def _target(relative: str) -> Path:
    return Path(st.session_state.conv_project_root).expanduser() / relative


def _pseudo2code() -> None:
    ss = st.session_state
    st.caption("Convert one pseudocode-bearing file into real code for its language.")
    render_path_picker(
        "Pseudocode file (project-relative or absolute)",
        "p2c_input",
        "file",
        st.session_state.conv_project_root,
    )
    render_path_picker(
        "Output file (optional; blank overwrites the input)",
        "p2c_output",
        "file",
        st.session_state.conv_project_root,
    )
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
    render_path_picker(
        "…or path to a notes file (project-relative or absolute)",
        "lt_notes_file",
        "file",
        ss.conv_project_root,
    )
    render_path_picker(
        "Output file",
        "lt_output",
        "file",
        ss.conv_project_root,
    )
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


def _assistant_contract() -> None:
    ss = st.session_state
    st.caption(
        "Extract assistant rules and obligations, then infer output requirements "
        "from example files. The result is a JSON contract."
    )
    render_path_picker(
        "Requirements file (.txt or .md; project-relative or absolute)",
        "contract_requirements",
        "file",
        ss.conv_project_root,
    )
    render_path_picker(
        "Output examples directory (project-relative or absolute)",
        "contract_examples",
        "directory",
        ss.conv_project_root,
    )
    render_path_picker(
        "Contract JSON output path",
        "contract_output",
        "file",
        ss.conv_project_root,
    )
    st.selectbox(
        "Local Ollama model",
        ["deepseek-r1:14b", "qwen3:14b", "mistral:7b"],
        key="contract_model",
    )
    if st.button("Build assistant contract", type="primary", key="contract_run"):
        requirements = ss.contract_requirements.strip()
        examples = ss.contract_examples.strip()
        output = ss.contract_output.strip() or "assistant_contract.json"
        if not requirements or not examples:
            st.error("Provide a requirements file and an examples directory.")
            return
        requirements_path = _target(requirements)
        if not requirements_path.is_file():
            requirements_path = Path(requirements).expanduser()
        examples_path = _target(examples)
        if not examples_path.is_dir():
            examples_path = Path(examples).expanduser()
        if not requirements_path.is_file():
            st.error("Requirements file not found: {}".format(requirements_path))
            return
        if not examples_path.is_dir():
            st.error("Examples directory not found: {}".format(examples_path))
            return
        output_path = _target(output)
        try:
            from code_converter.assistant_contract_builder import AssistantContractBuilder
            from shared.llm import LLMInterface
            from shared.llm_config import resolve_llm

            with st.spinner("Summarizing samples and generating the contract…"):
                contract_llm = LLMInterface(
                    resolved=resolve_llm(
                        "reasoning",
                        overrides={"provider": "ollama", "model": ss.contract_model},
                    )
                )
                written = AssistantContractBuilder(contract_llm).create_from_files(
                    str(requirements_path), str(examples_path), str(output_path)
                )
            contract_text = Path(written).read_text(encoding="utf-8")
            st.success("Wrote assistant contract to {}".format(written))
            st.json(json.loads(contract_text))
        except Exception as exc:  # noqa: BLE001
            st.error("Contract generation failed: {}".format(exc))


def render() -> None:
    _init_state()
    st.header("Converter")
    render_path_picker(
        "Project root", "conv_project_root", "directory", str(ui_paths.REPO_ROOT)
    )
    tab_p2c, tab_lt, tab_contract = st.tabs(
        ["pseudo2code", "longtext2pseudo", "assistant contract"]
    )
    with tab_p2c:
        _pseudo2code()
    with tab_lt:
        _longtext2pseudo()
    with tab_contract:
        _assistant_contract()
