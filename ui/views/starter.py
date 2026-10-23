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

from core import database_model as db_model
from core import paths as ui_paths
from core import pseudocode_model as pm
from core import repomap_tree as rt
from core import starterfile_view as sfview
from core.pipeline_runner import collect_artifacts, start_pipeline
from core.project_scanner import scan_project_root
from core.local_path_picker import render_path_picker
from core.verify import (
    verify_databases,
    verify_paths,
    verify_pseudocode,
    verify_repomap,
    verify_starterfile,
)
from code_starter.starterfile_builder import StarterfileBuilder
from views.database_builder import render_database_builder
from views.pseudocode_builder import render_pseudocode_builder
from views.repomap_editor import render_repomap_editor

_STAGE_RE = re.compile(r"\[(OK|FAIL)\]\s+(\S+):\s*(.*)")


def _init_state() -> None:
    ss = st.session_state
    ss.setdefault("starter_mode", "Create new")
    ss.setdefault("starter_project_root", str(ui_paths.WORKSPACE_DIR))
    ss.setdefault("starter_file_name", "starterfile.pseudo")
    ss.setdefault("sf_paths_root", ".")
    ss.setdefault("sf_paths_data_dir", "data")
    ss.setdefault("sf_repomap", "")
    ss.setdefault("sf_repomap_tree", None)
    ss.setdefault("sf_databases", "NONE")
    ss.setdefault("sf_databases_model", None)
    ss.setdefault("sf_databases_src", None)
    ss.setdefault("sf_pseudocode", "")
    ss.setdefault("sf_pseudocode_model", None)
    ss.setdefault("sf_pseudocode_src", None)
    ss.setdefault("sf_verified", {})
    ss.setdefault("sf_appended", {})
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


def _verify_save_row(label, state_key, signature, verify_fn, sections, save_label="Save section") -> None:
    """Render the Verify button and, once passed, the write-to-disk button."""
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
        if st.button(save_label, key="save_" + state_key, type="primary"):
            path = _merge_into_file(sections)
            st.session_state.setdefault("sf_appended", {})[state_key] = True
            st.success("Saved {} to {}".format(label, path))


def _verify_roads() -> tuple:
    ok1, msg1 = verify_paths(
        st.session_state.sf_paths_root, st.session_state.sf_paths_data_dir
    )
    ok2, msg2 = verify_repomap(st.session_state.sf_repomap)
    if ok1 and ok2:
        return True, "{}\n{}".format(msg1, msg2)
    return False, "\n".join(m for ok, m in ((ok1, msg1), (ok2, msg2)) if not ok)


def _reset_editor_state(ss) -> None:
    """Clear the per-section editor fields to their blank defaults."""
    ss.sf_paths_root = "."
    ss.sf_paths_data_dir = "data"
    ss.sf_repomap = ""
    ss.sf_repomap_tree = None
    ss.sf_databases = "NONE"
    ss.sf_databases_model = None
    ss.sf_pseudocode = ""
    ss.sf_pseudocode_model = None
    ss.sf_verified = {}
    ss.sf_appended = {}


def _apply_builder(ss, builder) -> None:
    """Copy a loaded builder's sections into the editor session state."""
    ss.sf_paths_root = builder.root
    ss.sf_paths_data_dir = builder.data_dir
    ss.sf_repomap = builder.repomap
    ss.sf_repomap_tree = None  # force the tree editor to reparse
    ss.sf_databases = builder.databases
    ss.sf_databases_model = None  # force the databases builder to reparse
    ss.sf_pseudocode = builder.pseudocode
    ss.sf_pseudocode_model = None  # force the pseudocode builder to reparse
    ss.sf_verified = {}
    ss.sf_appended = {}


def _persist_databases() -> None:
    """Rewrite the on-disk DATABASES section after an edit, once it was appended."""
    ss = st.session_state
    if ss.get("sf_appended", {}).get("databases") and _starterfile_path().is_file():
        _merge_into_file(["DATABASES"])


def _persist_pseudocode() -> None:
    """Rewrite the on-disk PSEUDOCODE section after an edit, once it was appended."""
    ss = st.session_state
    if ss.get("sf_appended", {}).get("pseudocode") and _starterfile_path().is_file():
        _merge_into_file(["PSEUDOCODE"])


def _verify_pseudocode_all() -> tuple:
    """Verify PSEUDOCODE with the analyzer, plus a REPOMAP folder cross-check."""
    ss = st.session_state
    ok, message = verify_pseudocode(ss.sf_pseudocode)
    folders = pm.folders_from_repomap(ss.sf_repomap)
    orphans = pm.orphan_paths(pm.parse(ss.sf_pseudocode), folders)
    if orphans:
        message += "\n" + "\n".join(
            "WARNING: `structure-orphan-file` — {} is not under any REPOMAP directory".format(
                path
            )
            for path in orphans
        )
    return ok, message


def _render_create(path: Path, ss) -> None:
    """Create-new controls: scan the project root, then write a fresh file."""
    root = Path(ss.starter_project_root).expanduser()
    st.caption("Create a new starterfile in the project root entered above.")
    exists = path.is_file()
    overwrite = False
    if exists:
        st.warning("A starterfile already exists at `{}`.".format(path))
        overwrite = st.checkbox("Overwrite the existing file", key="starter_overwrite")

    col_scan, col_create = st.columns(2)
    scan_clicked = col_scan.button(
        "🔍 Scan root → REPOMAP",
        key="starter_scan",
        disabled=not root.is_dir(),
        help="Auto-fill REPOMAP from the folder tree under the project root.",
    )
    create_clicked = col_create.button(
        "➕ Create starterfile",
        key="starter_create",
        type="primary",
        disabled=exists and not overwrite,
    )

    if scan_clicked:
        tree = scan_project_root(root)
        ss.sf_repomap = rt.to_text(tree)
        ss.sf_repomap_tree = None
        ss.sf_verified = {}
        found = rt.count(tree)
        if found:
            st.success("Found {} director(ies) under {}".format(found, root))
        else:
            st.info("No sub-directories found under {}.".format(root))

    if create_clicked and not (exists and not overwrite):
        if not root.is_dir():
            st.error("Project root does not exist: {}".format(root))
        else:
            _reset_editor_state(ss)
            if not ss.sf_repomap.strip():
                ss.sf_repomap = rt.to_text(scan_project_root(root))
            ss.sf_repomap_tree = None
            path.parent.mkdir(parents=True, exist_ok=True)
            _assemble().write()
            st.success(
                "Created {} ({} director(ies) in REPOMAP).".format(
                    path, rt.count(rt.parse_text(ss.sf_repomap))
                )
            )


def _render_load(path: Path, ss) -> None:
    """Load-existing controls: read an on-disk starterfile into the editor."""
    st.caption("Load an existing starterfile into the editor.")
    if st.button("Load existing starterfile", key="starter_load"):
        if path.is_file():
            _apply_builder(ss, StarterfileBuilder.from_file(path))
            st.success("Loaded {}".format(path))
        else:
            st.warning("No file at {}".format(path))


def render() -> None:
    _init_state()
    st.header("Starter")
    st.caption(
        "Build a starterfile.pseudo one section at a time, then run the pipeline."
    )

    ss = st.session_state
    mode = st.radio(
        "Start from",
        ["Create new", "Load existing"],
        horizontal=True,
        key="starter_mode",
    )
    render_path_picker(
        "Project root",
        "starter_project_root",
        "directory",
        default_directory=str(ui_paths.WORKSPACE_DIR),
    )
    render_path_picker(
        "Starterfile path or name",
        "starter_file_name",
        "file",
        default_directory=ss.starter_project_root,
    )

    path = _starterfile_path()
    if mode == "Create new":
        _render_create(path, ss)
    else:
        _render_load(path, ss)

    st.divider()
    tab_paths, tab_db, tab_pseudo, tab_review = st.tabs(
        ["Roadmap & Paths", "Databases", "Pseudocode", "Review & Run"]
    )

    # -- Tab 1: PATHS + REPOMAP -----------------------------------------
    with tab_paths:
        st.text_input(
            "PATHS root (relative to the starterfile)", key="sf_paths_root"
        )
        st.text_input("PATHS data_dir", key="sf_paths_data_dir")
        st.markdown("**REPOMAP**")
        render_repomap_editor()
        _verify_save_row(
            "Roadmap & Paths",
            "roads",
            (ss.sf_paths_root, ss.sf_paths_data_dir, ss.sf_repomap),
            _verify_roads,
            ["PATHS", "REPOMAP"],
        )

    # -- Tab 2: DATABASES -----------------------------------------------
    with tab_db:
        render_database_builder(on_change=_persist_databases)
        _verify_save_row(
            "Databases",
            "databases",
            ss.sf_databases,
            lambda: verify_databases(ss.sf_databases),
            ["DATABASES"],
            save_label="Append DATABASES to starterfile",
        )
        with st.expander("DATABASES format (reference)"):
            st.code(
                "example.db\n"
                "table 1 name: users\n"
                "table 1 columns:\n"
                "- identifier: primary key\n"
                "- name: display name\n",
                language="text",
            )

    # -- Tab 3: PSEUDOCODE ----------------------------------------------
    with tab_pseudo:
        render_pseudocode_builder(on_change=_persist_pseudocode)
        _verify_save_row(
            "Pseudocode",
            "pseudocode",
            ss.sf_pseudocode,
            _verify_pseudocode_all,
            ["PSEUDOCODE"],
            save_label="Append PSEUDOCODE to starterfile",
        )
        with st.expander("PSEUDOCODE format (reference)"):
            st.code(
                "## src/pkg/module.py\n"
                "INPUT: what the module reads\n"
                "OUTPUT: what it produces\n"
                "TASK: responsibilities and steps\n"
                "CONDITIONS: constraints and error cases\n"
                "PREFERENCES: style or library preferences\n"
                "FUNCTION MODEL:\n"
                "  - name: score\n"
                "    kind: math\n"
                "    formula: sum(values) / len(values)\n",
                language="text",
            )

    # -- Tab 4: Review & Run --------------------------------------------
    with tab_review:
        path = _starterfile_path()
        assembled = _assemble().render()

        _render_review_summary(ss)
        st.markdown(
            "**Assembled `{}`** — auto-assembled from the sections above.".format(path.name)
        )
        _render_starterfile(assembled)

        col_a, col_b = st.columns(2)
        if col_a.button("Write assembled file"):
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(assembled, encoding="utf-8")
            st.success("Wrote {}".format(path))
        if col_b.button("Verify whole file"):
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(assembled, encoding="utf-8")
            ok, message = verify_starterfile(path)
            (st.success if ok else st.error)("{}".format(message))

        st.divider()
        st.subheader("Run pipeline")
        st.caption("Requires `# STATUS: APPROVED`. Runs in a background process.")
        col_run, col_clear = st.columns(2)
        if col_run.button("Run pipeline", type="primary"):
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(assembled, encoding="utf-8")
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


def _render_starterfile(text: str) -> None:
    """Show a starterfile as coloured, read-only HTML for human review."""
    st.markdown(sfview.CSS + sfview.colorize(text), unsafe_allow_html=True)


def _render_review_summary(ss) -> None:
    """Colourful counters summarising the assembled file at a glance."""
    databases = db_model.parse(ss.sf_databases)
    modules = pm.parse(ss.sf_pseudocode)
    counters = [
        ("Directories", rt.count(rt.parse_text(ss.sf_repomap))),
        ("Databases", db_model.count(databases)),
        ("Tables", db_model.count_tables(databases)),
        ("Modules", pm.count(modules)),
        ("Functions", pm.count_functions(modules)),
    ]
    for column, (label, value) in zip(st.columns(len(counters)), counters):
        column.metric(label, value)


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
