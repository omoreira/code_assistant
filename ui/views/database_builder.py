"""Interactive ``# DATABASES`` builder for the Starter page.

Renders the DATABASES section as an editable set of databases -> tables ->
columns with add (➕) and remove (🗑) controls, so users no longer hand-type the
``table N ...`` records. The builder keeps
``st.session_state["sf_databases"]`` in sync with the model, so verification,
saving and the pipeline are unchanged.

Only the pure model in :mod:`core.database_model` knows the grammar; this module
is presentation only.
"""

from __future__ import annotations

import re

import streamlit as st

from core import database_model as dm

MODEL_KEY = "sf_databases_model"
SRC_KEY = "sf_databases_src"

_IDENT_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")


# -- state sync ----------------------------------------------------------

def _commit() -> None:
    """Write the model back into the canonical ``sf_databases`` text."""
    text = dm.render(st.session_state.get(MODEL_KEY) or [])
    st.session_state.sf_databases = text
    st.session_state[SRC_KEY] = text


def _sync_from_text() -> None:
    """(Re)build the model from ``sf_databases`` when that text changed
    externally (e.g. the user loaded or created a starterfile)."""
    current = st.session_state.get("sf_databases", "")
    model = st.session_state.get(MODEL_KEY)
    if model is None or st.session_state.get(SRC_KEY) != current:
        st.session_state[MODEL_KEY] = dm.parse(current)
        st.session_state[SRC_KEY] = current


def _change(on_change) -> None:
    """Persist an edit to ``sf_databases`` (and to disk via ``on_change``)."""
    _commit()
    if on_change is not None:
        on_change()
    st.rerun()


# -- input cleaning ------------------------------------------------------

def _clean_db_name(raw: str):
    name = (raw or "").strip()
    if not name or "/" in name or "\\" in name or name in {".", ".."}:
        return None
    if not name.casefold().endswith(".db"):
        name += ".db"
    return name


def _clean_ident(raw: str):
    name = (raw or "").strip()
    return name if _IDENT_RE.fullmatch(name) else None


# -- add controls --------------------------------------------------------

def _add_database(on_change) -> None:
    model = st.session_state[MODEL_KEY]
    with st.popover("➕ Add database"):
        with st.form(key="dbb-add-db", clear_on_submit=True):
            name = st.text_input("Database filename (e.g. app.db)", key="dbb-add-db-name")
            if st.form_submit_button("Add database"):
                clean = _clean_db_name(name)
                if clean is None:
                    st.error("Enter a simple filename (no path separators).")
                elif any(db["file"].casefold() == clean.casefold() for db in model):
                    st.error("That database is already listed.")
                else:
                    dm.add_database(model, clean)
                    _change(on_change)


def _add_table(db, db_index: int, on_change) -> None:
    with st.popover("➕ Add table"):
        with st.form(key="dbb-add-table-{}".format(db_index), clear_on_submit=True):
            name = st.text_input("Table name", key="dbb-add-table-name-{}".format(db_index))
            if st.form_submit_button("Add table"):
                clean = (name or "").strip()
                if not clean:
                    st.error("Enter a table name.")
                elif any(t["name"].casefold() == clean.casefold() for t in db["tables"]):
                    st.error("That table already exists in this database.")
                else:
                    dm.add_table(db, clean)
                    _change(on_change)


def _add_column(table, db_index: int, t_index: int, on_change) -> None:
    base = "{}-{}".format(db_index, t_index)
    with st.popover("➕ Add column"):
        with st.form(key="dbb-add-col-" + base, clear_on_submit=True):
            name = st.text_input("Column name", key="dbb-add-col-name-" + base)
            desc = st.text_input("Description (optional)", key="dbb-add-col-desc-" + base)
            if st.form_submit_button("Add column"):
                clean = _clean_ident(name)
                if clean is None:
                    st.error("Column names must be identifiers (letters, digits, _).")
                elif any(c["name"].casefold() == clean.casefold() for c in table["columns"]):
                    st.error("That column already exists in this table.")
                else:
                    dm.add_column(table, clean, (desc or "").strip())
                    _change(on_change)


# -- per-item rendering --------------------------------------------------

def _render_column(table, db_index: int, t_index: int, c_index: int, column, on_change) -> None:
    base = "{}-{}-{}".format(db_index, t_index, c_index)
    name_col, desc_col, del_col = st.columns([3, 5, 1])
    new_name = name_col.text_input(
        "column", value=column["name"], key="dbb-cname-" + base,
        placeholder="column name", label_visibility="collapsed",
    )
    new_desc = desc_col.text_input(
        "description", value=column.get("desc", ""), key="dbb-cdesc-" + base,
        placeholder="description", label_visibility="collapsed",
    )
    if new_name != column["name"] or new_desc != column.get("desc", ""):
        column["name"] = new_name.strip()
        column["desc"] = new_desc.strip()
        _change(on_change)
    if del_col.button("🗑", key="dbb-del-col-" + base, help="Remove column"):
        dm.remove_column(table, c_index)
        _change(on_change)


def _render_table(db, db_index: int, t_index: int, table, on_change) -> None:
    with st.container(border=True):
        head, remove_col = st.columns([6, 1])
        new_name = head.text_input(
            "table {} name".format(t_index + 1),
            value=table["name"],
            key="dbb-tname-{}-{}".format(db_index, t_index),
        )
        if new_name != table["name"]:
            table["name"] = new_name.strip()
            _change(on_change)
        if remove_col.button(
            "🗑", key="dbb-del-table-{}-{}".format(db_index, t_index), help="Remove table"
        ):
            dm.remove_table(db, t_index)
            _change(on_change)

        if not any(c["name"].casefold() == "identifier" for c in table["columns"]):
            st.caption(
                "⚠️ No `identifier` column yet — one is required (it becomes the primary key)."
            )

        for c_index, column in enumerate(list(table["columns"])):
            _render_column(table, db_index, t_index, c_index, column, on_change)

        _add_column(table, db_index, t_index, on_change)


def _render_database(db, db_index: int, on_change) -> None:
    with st.expander("📁 {}".format(db["file"] or "(unnamed)"), expanded=True):
        head, remove_col = st.columns([6, 1])
        new_file = head.text_input(
            "Database filename", value=db["file"], key="dbb-file-{}".format(db_index)
        )
        if new_file != db["file"]:
            db["file"] = new_file.strip()
            _change(on_change)
        if remove_col.button(
            "🗑", key="dbb-del-db-{}".format(db_index), help="Remove database"
        ):
            dm.remove_database(st.session_state[MODEL_KEY], db_index)
            _change(on_change)

        _add_table(db, db_index, on_change)

        for t_index, table in enumerate(list(db["tables"])):
            _render_table(db, db_index, t_index, table, on_change)


def render_database_builder(on_change=None) -> None:
    """Render the whole DATABASES builder and keep ``sf_databases`` up to date.

    ``on_change`` is called after every structural edit (add/remove/rename) so
    the caller can persist the section to disk once it has been appended.
    """
    _sync_from_text()
    model = st.session_state[MODEL_KEY]

    st.caption(
        "Add databases, then tables and columns. **➕** adds, **🗑** removes. "
        "Every table needs an `identifier` column (it becomes the primary key)."
    )

    add_col, _ = st.columns([2, 5])
    with add_col:
        _add_database(on_change)

    if not model:
        st.info("No databases yet — add one, or leave empty for NONE.")

    for db_index, db in enumerate(list(model)):
        _render_database(db, db_index, on_change)

    _commit()

    with st.expander("Generated # DATABASES text"):
        st.code(dm.render(model) or "NONE", language="text")
