"""Interactive ``# REPOMAP`` tree editor for the Starter page.

Renders the repo map as an indented tree where every directory has an
add-child (➕), rename (✏) and delete (🗑) control, so users no longer hand-type
the indented text. The widget keeps ``st.session_state["sf_repomap"]`` in sync
with the tree, so ``verify_repomap`` / saving / the pipeline are unchanged.
"""

from __future__ import annotations

import streamlit as st

from core import repomap_tree as rt

TREE_KEY = "sf_repomap_tree"
SRC_KEY = "sf_repomap_src"


def _commit() -> None:
    """Write the tree back into the canonical ``sf_repomap`` text."""
    text = rt.to_text(st.session_state.get(TREE_KEY) or [])
    st.session_state.sf_repomap = text
    st.session_state[SRC_KEY] = text


def _sync_from_text() -> None:
    """(Re)build the tree from ``sf_repomap`` when that text changed externally
    (e.g. the user loaded an existing starterfile)."""
    current = st.session_state.get("sf_repomap", "")
    tree = st.session_state.get(TREE_KEY)
    if tree is None or st.session_state.get(SRC_KEY) != current:
        st.session_state[TREE_KEY] = rt.parse_text(current)
        st.session_state[SRC_KEY] = current


def _clean_name(raw: str) -> str | None:
    name = (raw or "").strip().strip("/").strip()
    if not name or "/" in name:
        return None
    return name


def _add_popover(container, target: list, uid: str, label: str = "➕") -> None:
    """Popover with a small form that appends a child directory to ``target``."""
    with container.popover(label):
        with st.form(key="add-form-" + uid, clear_on_submit=True):
            name = st.text_input("New subdirectory", key="add-name-" + uid)
            if st.form_submit_button("Add directory"):
                clean = _clean_name(name)
                if clean is None:
                    st.error("Enter a name without slashes.")
                else:
                    target.append({"name": clean, "children": []})
                    _commit()
                    st.rerun()


def _render_node(node: dict, siblings: list, index: int, path: str, level: int) -> None:
    cols = st.columns([6, 1, 1, 1])
    cols[0].markdown(
        "{}📁 {}".format("&nbsp;" * (4 * level), node["name"]),
        unsafe_allow_html=True,
    )

    _add_popover(cols[1], node.setdefault("children", []), uid=path)

    with cols[2].popover("✏"):
        with st.form(key="ren-form-" + path):
            new = st.text_input("Rename to", value=node["name"], key="ren-name-" + path)
            if st.form_submit_button("Rename"):
                clean = _clean_name(new)
                if clean is None:
                    st.error("Enter a name without slashes.")
                else:
                    node["name"] = clean
                    _commit()
                    st.rerun()

    if cols[3].button("🗑", key="del-" + path):
        siblings.pop(index)
        _commit()
        st.rerun()

    for i, child in enumerate(list(node.get("children", []))):
        _render_node(child, node["children"], i, "{}-{}".format(path, i), level + 1)


def render_repomap_editor() -> None:
    """Render the whole REPOMAP editor and keep ``sf_repomap`` up to date."""
    _sync_from_text()
    roots = st.session_state[TREE_KEY]

    st.caption(
        "Build the repo map as a tree. **➕** adds a subdirectory, **✏** renames, "
        "**🗑** deletes. Only directories are mapped."
    )

    head, add_col = st.columns([6, 1])
    head.markdown(
        "**Top-level directories**" if roots else "*No directories yet — add one with **➕**.*"
    )
    _add_popover(add_col, roots, uid="root", label="➕ Add")

    for i, node in enumerate(list(roots)):
        _render_node(node, roots, i, str(i), 0)

    _commit()

    with st.expander("Generated # REPOMAP text"):
        st.code(rt.to_text(roots) or "NONE", language="text")
