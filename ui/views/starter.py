"""Starter page: build a ``starterfile.pseudo`` section by section, then run.

Four tabs:
  1. Roadmap & Paths  -> ``# PATHS`` (root, data_dir) and ``# REPOMAP``
  2. Databases        -> ``# DATABASES``
  3. Pseudocode       -> ``# PSEUDOCODE``
  4. Review & Run     -> revise the assembled file and run the pipeline

Tabs 1-3 each show a **Verify** button; when the section passes, a **Save**
button appears and the section is merged into the starterfile on disk.
"""

from __future__ import annotations

import re
import time
from pathlib import Path

import streamlit as st

from core import paths as ui_paths
from core.pipeline_runner import collect_artifacts, start_pipeline
from core.verify import (
    verify_databases,
    verify_paths,
    verify_pseudocode,
    verify_repomap,
    verify_starterfile,
)
from code_starter.starterfile_builder import StarterfileBuilder

_STAGE_RE = re.compile(r"\[(OK|FAIL)\]\s+(\S+):\s*(.*)")


def _init_state() -> None:
    ss = st.session_state
    ss.setdefault("starter_project_root", str(ui_paths.WORKSPACE_DIR))
    ss.setdefault("starter_file_name", "starterfile.pseudo")
    ss.setdefault("sf_paths_root", ".")
    ss.setdefault("sf_paths_data_dir", "data")
    ss.setdefault("sf_repomap", "")
    ss.setdefault("sf_databases", "NONE")
    ss.setdefault("sf_pseudocode", "")
    ss.setdefault("sf_verified", {})
    ss.setdefault("starter_run", None)


def _starterfile_path() -> Path:
    return (
        Path(st.session_state.starter_project_root).expanduser()
        / st.session_state.starter_file_name
    )


def _assemble() -> StarterfileBuilder:
    """Build a builder from the current editor state (no disk read)."""
    builder = StarterfileBuilder(_starterfile_path())
    builder.set_paths(st.session_state.sf_paths_root, st.session_state.sf_paths_data_dir)
    builder.repomap = st.session_state.sf_repomap
    builder.databases = st.session_state.sf_databases
    builder.pseudocode = st.session_state.sf_pseudocode
    return builder


def _merge_into_file(sections) -> Path:
    """Merge the named sections from editor state into the on-disk starterfile."""
    path = _starterfile_path()
    builder = StarterfileBuilder.from_file(path) if path.is_file() else StarterfileBuilder(path)
    for section in sections:
        if section == "PATHS":
            builder.set_paths(
                st.session_state.sf_paths_root, st.session_state.sf_paths_data_dir
            )
        else:
            builder.set_section(section, st.session_state["sf_" + section.lower()])
    return builder.write()


def _verify_save_row(label, state_key, signature, verify_fn, sections) -> None:
    """Render the Verify button and, once passed, the Save button."""
    verified = st.session_state.sf_verified
    if st.button("Verify", key="verify_" + state_key):
        ok, message = verify_fn()
        if ok:
            verified[state_key] = signature
            st.success("{}: passed verification — {}".format(label, message))
        else:
            verified.pop(state_key, None)
            st.error("{}: verification failed\n\n{}".format(label, message))
    if verified.get(state_key) == signature:
        if st.button("Save section", key="save_" + state_key, type="primary"):
            path = _merge_into_file(sections)
            st.success("Saved {} to {}".format(label, path))


def _verify_roads() -> tuple:
    ok1, msg1 = verify_paths(
        st.session_state.sf_paths_root, st.session_state.sf_paths_data_dir
    )
    ok2, msg2 = verify_repomap(st.session_state.sf_repomap)
    if ok1 and ok2:
        return True, "{}\n{}".format(msg1, msg2)
    return False, "\n".join(m for ok, m in ((ok1, msg1), (ok2, msg2)) if not ok)


def render() -> None:
    _init_state()
    st.header("Starter")
    st.caption(
        "Build a starterfile.pseudo one section at a time, then run the pipeline."
    )

    ss = st.session_state
    ss.starter_project_root = st.text_input(
        "Project root", value=ss.starter_project_root, key="w_starter_project_root"
    )
    ss.starter_file_name = st.text_input(
        "Starterfile name", value=ss.starter_file_name, key="w_starter_file_name"
    )

    col_load, _ = st.columns([1, 3])
    if col_load.button("Load existing starterfile"):
        path = _starterfile_path()
        if path.is_file():
            builder = StarterfileBuilder.from_file(path)
            ss.sf_paths_root = builder.root
            ss.sf_paths_data_dir = builder.data_dir
            ss.sf_repomap = builder.repomap
            ss.sf_databases = builder.databases
            ss.sf_pseudocode = builder.pseudocode
            ss.sf_verified = {}
            st.success("Loaded {}".format(path))
        else:
            st.warning("No file at {}".format(path))

    tab_paths, tab_db, tab_pseudo, tab_review = st.tabs(
        ["Roadmap & Paths", "Databases", "Pseudocode", "Review & Run"]
    )

    # -- Tab 1: PATHS + REPOMAP -----------------------------------------
    with tab_paths:
        st.text_input(
            "PATHS root (relative to the starterfile)", key="sf_paths_root"
        )
        st.text_input("PATHS data_dir", key="sf_paths_data_dir")
        st.text_area(
            "REPOMAP directory tree (indentation matters; use NONE for none)",
            key="sf_repomap",
            height=240,
        )
        _verify_save_row(
            "Roadmap & Paths",
            "roads",
            (ss.sf_paths_root, ss.sf_paths_data_dir, ss.sf_repomap),
            _verify_roads,
            ["PATHS", "REPOMAP"],
        )

    # -- Tab 2: DATABASES -----------------------------------------------
    with tab_db:
        st.text_area(
            "DATABASES specification (use NONE for none)",
            key="sf_databases",
            height=300,
        )
        with st.expander("DATABASES format"):
            st.code(
                "example.db\n"
                "table 1 name: users\n"
                "table 1 columns:\n"
                "- identifier: primary key\n"
                "- name: display name\n",
                language="text",
            )
        _verify_save_row(
            "Databases",
            "databases",
            ss.sf_databases,
            lambda: verify_databases(ss.sf_databases),
            ["DATABASES"],
        )

    # -- Tab 3: PSEUDOCODE ----------------------------------------------
    with tab_pseudo:
        st.text_area(
            "PSEUDOCODE entries (use NONE for none)",
            key="sf_pseudocode",
            height=360,
        )
        with st.expander("PSEUDOCODE format"):
            st.code(
                "## src/pkg/module.py\n"
                "INPUT: what the module reads\n"
                "OUTPUT: what it produces\n"
                "TASK: responsibilities and steps\n"
                "CONDITIONS: constraints and error cases\n",
                language="text",
            )
        _verify_save_row(
            "Pseudocode",
            "pseudocode",
            ss.sf_pseudocode,
            lambda: verify_pseudocode(ss.sf_pseudocode),
            ["PSEUDOCODE"],
        )

    # -- Tab 4: Review & Run --------------------------------------------
    with tab_review:
        path = _starterfile_path()
        if "sf_review" not in ss:
            ss.sf_review = path.read_text(encoding="utf-8") if path.is_file() else _assemble().render()
        st.text_area("Assembled starterfile.pseudo (editable)", key="sf_review", height=380)

        col_a, col_b = st.columns(2)
        if col_a.button("Reassemble from sections"):
            ss.sf_review = _assemble().render()
        if col_b.button("Write reviewed file"):
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(ss.sf_review, encoding="utf-8")
            st.success("Wrote {}".format(path))

        if st.button("Verify whole file"):
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(ss.sf_review, encoding="utf-8")
            ok, message = verify_starterfile(path)
            (st.success if ok else st.error)("{}".format(message))

        st.divider()
        st.subheader("Run pipeline")
        st.caption("Requires `# STATUS: APPROVED`. Runs in a background process.")
        col_run, col_clear = st.columns(2)
        if col_run.button("Run pipeline", type="primary"):
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(ss.sf_review, encoding="utf-8")
            ss.starter_run = start_pipeline(
                ui_paths.REPO_ROOT,
                Path(ss.starter_project_root).expanduser(),
                ss.starter_file_name,
                data_dir=ss.sf_paths_data_dir,
                use_llm=True,
            )
        if col_clear.button("Clear run"):
            ss.starter_run = None

        _render_run(ss)


def _render_run(ss) -> None:
    run = ss.get("starter_run")
    if run is None:
        return
    log_box = st.empty()
    while run.running():
        log_box.code(run.text() or "starting…", language="text")
        time.sleep(1)
    log_box.code(run.text() or "(no output)", language="text")

    if run.returncode == 0:
        st.success("Pipeline finished successfully.")
    else:
        st.error("Pipeline exited with code {}.".format(run.returncode))

    stages = _STAGE_RE.findall(run.text())
    if stages:
        st.subheader("Stages")
        st.table(
            [
                {"Stage": name, "Result": result, "Detail": detail}
                for result, name, detail in stages
            ]
        )

    artifacts = collect_artifacts(Path(ss.starter_project_root).expanduser())
    if artifacts:
        st.subheader("Report artifacts")
        for artifact in artifacts:
            st.markdown("- `{}`".format(artifact))
            if artifact.suffix == ".txt" or artifact.name.endswith(".md"):
                with st.expander(artifact.name):
                    st.code(
                        artifact.read_text(encoding="utf-8", errors="replace"),
                        language="text",
                    )
