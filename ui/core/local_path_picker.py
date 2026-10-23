"""Streamlit controls for browsing the local filesystem for files and folders."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Optional

import streamlit as st


def _navigate_to(browse_key: str, location: str, filter_key: str) -> None:
    st.session_state[browse_key] = location
    st.session_state[filter_key] = ""


def _open_parent(browse_key: str) -> None:
    location = Path(st.session_state[browse_key]).expanduser()
    parent = location.parent
    if parent != location:
        st.session_state[browse_key] = str(parent)


def _use_current_folder(target_key: str, browse_key: str) -> None:
    st.session_state[target_key] = st.session_state[browse_key]


def _use_path(target_key: str, path: str) -> None:
    st.session_state[target_key] = path


def _use_new_file(target_key: str, browse_key: str, name_key: str) -> None:
    name = st.session_state.get(name_key, "").strip()
    if name and Path(name).name == name and name not in {".", ".."}:
        st.session_state[target_key] = str(
            Path(st.session_state[browse_key]).expanduser() / name
        )


def _start_from_target(
    target_key: str,
    browse_key: str,
    default_directory: Optional[str],
) -> None:
    st.session_state[browse_key] = _initial_location(
        st.session_state.get(target_key, ""), default_directory
    )


def _initial_location(
    target_value: str, default_directory: Optional[str]
) -> str:
    candidate = Path(target_value).expanduser() if target_value else None
    if candidate and candidate.is_dir():
        return str(candidate)
    if candidate and candidate.is_file():
        return str(candidate.parent)
    if default_directory and Path(default_directory).expanduser().is_dir():
        return str(Path(default_directory).expanduser())
    if candidate and candidate.parent.is_dir():
        return str(candidate.parent)
    return str(Path.cwd())


def render_path_picker(
    label: str,
    key: str,
    kind: str,
    default_directory: Optional[str] = None,
    help_text: Optional[str] = None,
) -> None:
    """Render a normal path input plus an expandable local filesystem browser.

    ``kind`` is ``"file"`` or ``"directory"``. Users can still type a path;
    the browser selects existing local paths and writes the selection there.
    """
    if kind not in ("file", "directory"):
        raise ValueError("kind must be 'file' or 'directory'")

    current_value = st.session_state.get(key, "")
    st.session_state.setdefault(
        key + "__browse_location",
        _initial_location(current_value, default_directory),
    )
    st.text_input(label, key=key, help=help_text)

    browse_key = key + "__browse_location"
    filter_key = key + "__browse_filter"
    with st.expander("Browse local files and folders", expanded=False):
        location_col, parent_col, start_col = st.columns([5, 1, 2])
        location_col.text_input("Browse location", key=browse_key)
        parent_col.button(
            "↑",
            key=key + "__browse_parent",
            help="Go to the parent folder",
            on_click=_open_parent,
            args=(browse_key,),
        )
        start_col.button(
            "Start from path above",
            key=key + "__browse_start",
            on_click=_start_from_target,
            args=(key, browse_key, default_directory),
        )

        directory = Path(st.session_state[browse_key]).expanduser()
        if not directory.is_dir():
            st.warning("This folder does not exist or cannot be opened.")
            return
        try:
            entries = sorted(directory.iterdir(), key=lambda item: item.name.casefold())
            folders = [item.name for item in entries if item.is_dir() and not item.is_symlink()]
            files = [item.name for item in entries if item.is_file()]
        except OSError as exc:
            st.warning("Cannot read this folder: {}".format(exc))
            return

        # Clickable breadcrumb buttons make it easy to move back several levels.
        crumbs = []
        current = Path(directory.anchor) if directory.is_absolute() else Path()
        for part in directory.parts if directory.is_absolute() else (".",) + directory.parts:
            if part in (directory.anchor, "."):
                current = Path(part)
            else:
                current = current / part
            crumbs.append((part, str(current)))
        crumb_cols = st.columns(min(len(crumbs), 6)) if crumbs else []
        for index, (part, path) in enumerate(crumbs):
            column = crumb_cols[index] if index < len(crumb_cols) else st
            column.button(
                part or "/",
                key=key + "__crumb_" + hashlib.sha1(path.encode("utf-8")).hexdigest()[:10],
                on_click=_navigate_to,
                args=(browse_key, path, filter_key),
                help=path,
            )

        st.text_input("Filter this folder", key=filter_key, placeholder="Type to narrow the list")
        query = st.session_state.get(filter_key, "").casefold().strip()
        visible_folders = [name for name in folders if query in name.casefold()]
        visible_files = [name for name in files if query in name.casefold()]
        st.caption(
            "{} folder(s), {} file(s){}".format(
                len(visible_folders), len(visible_files),
                " matching the filter" if query else "",
            )
        )
        if kind == "directory":
            st.button(
                "Use this folder",
                key=key + "__browse_use_folder",
                on_click=_use_current_folder,
                args=(key, browse_key),
            )
        if visible_folders:
            st.markdown("**Folders**")
            for name in visible_folders[:80]:
                path = str(directory / name)
                st.button(
                    "📁  " + name,
                    key=key + "__folder_" + hashlib.sha1(path.encode("utf-8")).hexdigest()[:12],
                    on_click=_navigate_to,
                    args=(browse_key, path, filter_key),
                    use_container_width=True,
                )
            if len(visible_folders) > 80:
                st.caption("Showing the first 80 folders. Use the filter to narrow the list.")
        if kind == "file" and visible_files:
            st.markdown("**Files**")
            for name in visible_files[:80]:
                path = str(directory / name)
                st.button(
                    "📄  " + name,
                    key=key + "__file_" + hashlib.sha1(path.encode("utf-8")).hexdigest()[:12],
                    on_click=_use_path,
                    args=(key, path),
                    use_container_width=True,
                )
            if len(visible_files) > 80:
                st.caption("Showing the first 80 files. Use the filter to narrow the list.")
        if not visible_folders and (kind == "directory" or not visible_files):
            st.caption("No matching entries in this folder.")
        if kind == "file":
            st.text_input(
                "Or choose a new filename in this folder",
                key=key + "__browse_new_name",
            )
            st.button(
                "Use new filename",
                key=key + "__browse_use_new_file",
                disabled=not st.session_state.get(key + "__browse_new_name", "").strip(),
                on_click=_use_new_file,
                args=(key, browse_key, key + "__browse_new_name"),
            )
