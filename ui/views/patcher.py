"""Assistant (patcher) page: a context-aware chat that reads project files and proposes patches.

The chat is fed a bounded snapshot of user-selected project files. When the
model proposes edits it must emit a ``patch.pseudo`` block (``#PATCHES`` /
``#NEW SCRIPTS``). We validate that block with a **dry run** of
:func:`code_analyzer.patch_file.apply_patch_file` and only apply it after the
user confirms.
"""

from __future__ import annotations

import re
import tempfile
from pathlib import Path
from typing import List, Optional, Tuple

import streamlit as st

from core import paths as ui_paths
from core.llm import get_llm
from core.local_path_picker import render_path_picker

_TEXT_SUFFIXES = {
    ".py", ".pyi", ".md", ".txt", ".toml", ".yaml", ".yml", ".json",
    ".pseudo", ".cfg", ".ini", ".sh", ".js", ".ts", ".tsx", ".jsx",
    ".css", ".html", ".sql",
}
_SKIP_DIRS = {
    ".git", "venv", ".venv", "__pycache__", "node_modules", "build",
    "dist", ".mypy_cache", ".pytest_cache", ".streamlit",
}
_MAX_FILE_CHARS = 4000
_MAX_CONTEXT_CHARS = 24000


def _init_state() -> None:
    ss = st.session_state
    ss.setdefault("patcher_root", str(ui_paths.REPO_ROOT))
    ss.setdefault("patcher_files", [])
    ss.setdefault("patcher_messages", [])
    ss.setdefault("patcher_patch", None)


def _list_files(root: Path, limit: int = 500) -> List[str]:
    files: List[str] = []
    root = root.resolve()
    for path in sorted(root.rglob("*")):
        if any(part in _SKIP_DIRS for part in path.parts):
            continue
        if path.is_file() and path.suffix.lower() in _TEXT_SUFFIXES:
            files.append(str(path.relative_to(root)))
        if len(files) >= limit:
            break
    return files


def _build_context(root: Path, relatives: List[str]) -> str:
    parts: List[str] = []
    used = 0
    for relative in relatives:
        target = (root / relative).resolve()
        try:
            text = target.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if len(text) > _MAX_FILE_CHARS:
            text = text[:_MAX_FILE_CHARS] + "\n…[truncated]"
        block = "### {}\n```\n{}\n```".format(relative, text)
        if used + len(block) > _MAX_CONTEXT_CHARS:
            break
        parts.append(block)
        used += len(block)
    return "\n\n".join(parts)


def _system_prompt(root: Path) -> str:
    return (
        "You are a precise coding assistant working inside the repository at "
        "`{}`.\n"
        "Answer questions about the code. When you propose changes, emit a "
        "patch.pseudo block with two sections, `#PATCHES` and `#NEW SCRIPTS`. "
        "Under each, use `## project/relative/path` headers. For existing files "
        "provide valid unified diff hunks with context; for new files provide "
        "the complete contents. Do not use Markdown fences around the block. If "
        "no change is needed, do not emit a patch block.".format(root)
    )


_PATCH_RE = re.compile(r"(#PATCHES.*?)(?=\n#\s|\Z)", re.DOTALL | re.IGNORECASE)


def _extract_patch_block(text: str) -> Optional[str]:
    if not re.search(r"#PATCHES", text, re.IGNORECASE):
        return None
    start = re.search(r"^#PATCHES", text, re.MULTILINE | re.IGNORECASE)
    if not start:
        return None
    block = text[start.start():]
    # Trim a trailing prose paragraph that clearly is not part of the file.
    return block.strip()


def _prepare_patch(patch_text: str, root: str):
    """Dry-run a patch block; return (patch_text, error, changes, tmp_path)."""
    tmp = Path(tempfile.mkdtemp()) / "patch.pseudo"
    tmp.write_text(patch_text, encoding="utf-8")
    try:
        from code_analyzer.patch_file import apply_patch_file

        changes = apply_patch_file(str(tmp), root, dry_run=True)
        return patch_text, None, changes, str(tmp)
    except Exception as exc:  # noqa: BLE001 - any parse/apply error is reported
        return patch_text, str(exc), None, str(tmp)


def render() -> None:
    _init_state()
    st.header("Project Assistant")
    st.caption("A context-aware chat that reads project files and proposes patches.")

    ss = st.session_state
    render_path_picker(
        "Project root", "patcher_root", "directory", str(ui_paths.REPO_ROOT)
    )
    root = Path(ss.patcher_root).expanduser()

    with st.expander("Context files", expanded=not ss.patcher_messages):
        if st.button("Scan project for files"):
            ss.patcher_files = _list_files(root)
            st.success("Found {} candidate files.".format(len(ss.patcher_files)))
        ss.patcher_files = st.multiselect(
            "Files included as context",
            options=ss.patcher_files,
            default=ss.patcher_files,
        )

    for message in ss.patcher_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if patch := ss.get("patcher_patch"):
        _render_patch(patch, ss)

    user_text = st.chat_input("Ask about the code or request a patch")
    if not user_text:
        return

    ss.patcher_messages.append({"role": "user", "content": user_text})
    with st.chat_message("user"):
        st.markdown(user_text)

    context = _build_context(root, ss.patcher_files)
    history = "\n\n".join(
        "{role}: {content}".format(**m) for m in ss.patcher_messages
    )
    prompt = "{system}\n\nProject files:\n{context}\n\nConversation:\n{history}".format(
        system=_system_prompt(root), context=context or "(none selected)", history=history
    )

    with st.chat_message("assistant"):
        with st.spinner("Thinking…"):
            try:
                reply = get_llm("reasoning").call(prompt, temperature=0.2)
            except Exception as exc:  # noqa: BLE001
                reply = "⚠️ Request failed: {}".format(exc)
        st.markdown(reply)

    ss.patcher_messages.append({"role": "assistant", "content": reply})
    patch_text = _extract_patch_block(reply)
    if patch_text:
        ss.patcher_patch = _prepare_patch(patch_text, str(root))
    st.rerun()


def _render_patch(patch, ss) -> None:
    patch_text, error, changes, tmp_path = patch
    st.divider()
    st.subheader("Proposed patch")
    st.code(patch_text, language="text")
    if error:
        st.error("This patch cannot be applied: {}".format(error))
        if st.button("Discard patch"):
            ss.patcher_patch = None
            st.rerun()
        return
    st.write("Would change:")
    for change in changes or []:
        st.markdown("- `{}`".format(change))
    col_apply, col_discard = st.columns(2)
    if col_apply.button("Apply patch", type="primary"):
        try:
            from code_analyzer.patch_file import apply_patch_file

            written = apply_patch_file(tmp_path, str(ss.patcher_root), dry_run=False)
            st.success("Applied: {}".format(", ".join(written)))
            ss.patcher_patch = None
        except Exception as exc:  # noqa: BLE001
            st.error("Apply failed: {}".format(exc))
    if col_discard.button("Discard patch"):
        ss.patcher_patch = None
        st.rerun()
