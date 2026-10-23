"""Streamlit controls for browsing the local filesystem for files and folders."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import streamlit as st


def _open_selected(browse_key: str, selection_key: str) -> None:
    selected = st.session_state.get(selection_key, "")
    if selected:
        st.session_state[browse_key] = str(
            Path(st.session_state[browse_key]).expanduser() / selected
        )


def _open_parent(browse_key: str) -> None:
    location = Path(st.session_state[browse_key]).expanduser()
    parent = location.parent
    if parent != location:
        st.session_state[browse_key] = str(parent)


def _use_current_folder(target_key: str, browse_key: str) -> None:
    st.session_state[target_key] = st.session_state[browse_key]


def _use_selected_file(target_key: str, browse_key: str, file_key: str) -> None:
    selected = st.session_state.get(file_key, "")
    if selected:
        st.session_state[target_key] = str(
            Path(st.session_state[browse_key]).expanduser() / selected
        )


def _use_new_file(target_key: str, browse_key: str, name_key: str) -> None:
    name = st.session_state.get(name_key, "").strip()
    if name and Path(name).name == name and name not in {".", ".."}:
        st.session_state[target_key] = str(
            Path(st.session_state[browse_key]).expanduser() / name
        )


def _start_from_target(
    target_key: str,
    browse_key: str,
    kind: str,
    default_directory: Optional[str],
) -> None:
    st.session_state[browse_key] = _initial_location(
        st.session_state.get(target_key, ""), kind, default_directory
    )


def _initial_location(target_value: str, kind: str, default_directory: Optional[str]) -> str:
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
        _initial_location(current_value, kind, default_directory),
    )
    st.text_input(label, key=key, help=help_text)

    browse_key = key + "__browse_location"
    folder_key = key + "__browse_folder"
    file_key = key + "__browse_file"
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
            args=(key, browse_key, kind, default_directory),
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

        if folders:
            st.selectbox("Subfolder", [""] + folders, key=folder_key)
            st.button(
                "Open selected folder",
                key=key + "__browse_open",
                disabled=not st.session_state.get(folder_key),
                on_click=_open_selected,
                args=(browse_key, folder_key),
            )
        else:
            st.caption("No subfolders here.")

        if kind == "directory":
            st.button(
                "Use this folder",
                key=key + "__browse_use_folder",
                on_click=_use_current_folder,
                args=(key, browse_key),
            )
        elif files:
            st.selectbox("File", [""] + files, key=file_key)
            st.button(
                "Use selected file",
                key=key + "__browse_use_file",
                disabled=not st.session_state.get(file_key),
                on_click=_use_selected_file,
                args=(key, browse_key, file_key),
            )
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
        else:
            st.caption("No files here.")
            st.text_input(
                "Filename in this folder",
                key=key + "__browse_new_name",
            )
            st.button(
                "Use new filename",
                key=key + "__browse_use_new_file",
                disabled=not st.session_state.get(key + "__browse_new_name", "").strip(),
                on_click=_use_new_file,
                args=(key, browse_key, key + "__browse_new_name"),
            )
