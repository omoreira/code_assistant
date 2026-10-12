"""Interactive ``# PSEUDOCODE`` builder for the Starter page.

Renders the PSEUDOCODE section as one editable card per script module: a path
chosen from the REPOMAP folders, the five preset fields, and an optional
``FUNCTION MODEL``. Adds (➕) and removes (🗑) keep
``st.session_state["sf_pseudocode"]`` in sync so Verify/Append and the pipeline
are unchanged.

The grammar lives in :mod:`core.pseudocode_model`; this module is presentation.
"""

from __future__ import annotations

import streamlit as st

from core import pseudocode_model as pm
from code_starter import function_model as fm

MODEL_KEY = "sf_pseudocode_model"
SRC_KEY = "sf_pseudocode_src"


# -- state sync ----------------------------------------------------------

def _commit() -> None:
    text = pm.render(st.session_state.get(MODEL_KEY) or [])
    st.session_state.sf_pseudocode = text
    st.session_state[SRC_KEY] = text


def _sync_from_text() -> None:
    current = st.session_state.get("sf_pseudocode", "")
    model = st.session_state.get(MODEL_KEY)
    if model is None or st.session_state.get(SRC_KEY) != current:
        st.session_state[MODEL_KEY] = pm.parse(current)
        st.session_state[SRC_KEY] = current


def _change(on_change) -> None:
    _commit()
    if on_change is not None:
        on_change()
    st.rerun()


# -- add controls --------------------------------------------------------

def _add_entry(on_change, folders) -> None:
    model = st.session_state[MODEL_KEY]
    options = ["(root)"] + list(folders)
    with st.popover("➕ Add script module"):
        with st.form(key="pb-add-entry", clear_on_submit=True):
            folder = st.selectbox("REPOMAP folder", options, key="pb-add-folder")
            filename = st.text_input(
                "Script filename (e.g. module.py)", key="pb-add-filename"
            )
            if st.form_submit_button("Add module"):
                if not (filename or "").strip():
                    st.error("Enter a filename.")
                else:
                    path = pm.join_path("" if folder == "(root)" else folder, filename)
                    if any(entry["path"] == path for entry in model):
                        st.error("An entry for {} already exists.".format(path))
                    else:
                        pm.add_entry(model, path)
                        _change(on_change)


def _add_function_form(entry, e_index: int, on_change) -> None:
    base = str(e_index)
    with st.popover("➕ Add function"):
        with st.form(key="pb-add-fn-" + base, clear_on_submit=True):
            name = st.text_input("Name", key="pb-add-fn-name-" + base)
            kind = st.selectbox("Kind", list(fm.KNOWN_KINDS), key="pb-add-fn-kind-" + base)
            inputs = st.text_input("Inputs", key="pb-add-fn-inputs-" + base)
            returns = st.text_input("Returns", key="pb-add-fn-returns-" + base)
            formula = st.text_input("Formula", key="pb-add-fn-formula-" + base)
            criteria = st.text_input("Criteria", key="pb-add-fn-criteria-" + base)
            if st.form_submit_button("Add function"):
                clean = (name or "").strip()
                if not clean:
                    st.error("Enter a function name.")
                elif any(f["name"] == clean for f in entry.get("functions", [])):
                    st.error("That function already exists in this module.")
                else:
                    entry.setdefault("functions", []).append(
                        {
                            "name": clean,
                            "kind": kind,
                            "inputs": inputs.strip(),
                            "returns": returns.strip(),
                            "formula": formula.strip(),
                            "criteria": criteria.strip(),
                        }
                    )
                    _change(on_change)


# -- per-item rendering --------------------------------------------------

def _render_function(entry, e_index: int, f_index: int, function, on_change) -> None:
    base = "{}-{}".format(e_index, f_index)
    with st.container(border=True):
        col_name, col_kind, col_del = st.columns([4, 3, 1])
        new_name = col_name.text_input("name", value=function["name"], key="pb-fname-" + base)
        kinds = list(fm.KNOWN_KINDS)
        current_kind = function.get("kind") or "step"
        kind_index = kinds.index(current_kind) if current_kind in kinds else 0
        new_kind = col_kind.selectbox("kind", kinds, index=kind_index, key="pb-fkind-" + base)
        remove = col_del.button("🗑", key="pb-del-fn-" + base, help="Remove function")
        if remove:
            pm.remove_function(entry, f_index)
            _change(on_change)

        row1, row2 = st.columns(2)
        new_inputs = row1.text_input("inputs", value=function.get("inputs", ""), key="pb-fin-" + base)
        new_returns = row2.text_input("returns", value=function.get("returns", ""), key="pb-fret-" + base)
        new_formula = st.text_input("formula", value=function.get("formula", ""), key="pb-fform-" + base)
        new_criteria = st.text_input("criteria", value=function.get("criteria", ""), key="pb-fcrit-" + base)

        updated = {
            "name": new_name.strip(),
            "kind": new_kind,
            "inputs": new_inputs.strip(),
            "returns": new_returns.strip(),
            "formula": new_formula.strip(),
            "criteria": new_criteria.strip(),
        }
        if any(function.get(k, "") != v for k, v in updated.items()):
            function.update(updated)
            _change(on_change)


def _render_function_model(entry, e_index: int, on_change) -> None:
    functions = entry.get("functions", [])
    with st.expander("FUNCTION MODEL ({} function(s))".format(len(functions))):
        if not functions:
            st.caption("No functions yet — optional, but recommended for math and criteria.")
        for f_index, function in enumerate(list(functions)):
            _render_function(entry, e_index, f_index, function, on_change)

        _add_function_form(entry, e_index, on_change)

        for finding in pm.function_findings(entry):
            text = "{}: {}".format(finding.code, finding.message)
            (st.error if finding.severity == "ERROR" else st.warning)(text)


def _render_entry_card(entry, e_index: int, folders, on_change) -> None:
    problems = pm.entry_problems(entry, folders)
    with st.container(border=True):
        col_path, col_del = st.columns([6, 1])
        new_path = col_path.text_input(
            "Module path", value=entry["path"], key="pb-path-{}".format(e_index)
        )
        if new_path != entry["path"]:
            entry["path"] = new_path.strip()
            _change(on_change)
        if col_del.button("🗑", key="pb-del-entry-{}".format(e_index), help="Remove module"):
            pm.remove_entry(st.session_state[MODEL_KEY], e_index)
            _change(on_change)

        if problems:
            st.caption("⚠️ " + "; ".join(problems))

        for key in pm.FIELD_ORDER:
            label = key + (" *" if key in pm.REQUIRED_FIELDS else "")
            new_value = st.text_area(
                label,
                value=entry["fields"].get(key, ""),
                key="pb-field-{}-{}".format(e_index, key),
                height=68,
            )
            if new_value != entry["fields"].get(key, ""):
                entry["fields"][key] = new_value.rstrip("\n")
                _change(on_change)

        _render_function_model(entry, e_index, on_change)


def render_pseudocode_builder(on_change=None) -> None:
    """Render the whole PSEUDOCODE builder and keep ``sf_pseudocode`` up to date."""
    _sync_from_text()
    model = st.session_state[MODEL_KEY]
    folders = pm.folders_from_repomap(st.session_state.get("sf_repomap", ""))

    st.caption(
        "One entry per script module, under a folder from the REPOMAP. "
        "**TASK** is required; **➕** adds, **🗑** removes."
    )

    add_col, _ = st.columns([2, 5])
    with add_col:
        _add_entry(on_change, folders)

    if not model:
        st.info("No script modules yet — add one, or leave empty for NONE.")

    for e_index, entry in enumerate(list(model)):
        _render_entry_card(entry, e_index, folders, on_change)

    _commit()

    with st.expander("Generated # PSEUDOCODE text"):
        st.code(pm.render(model) or "NONE", language="text")
