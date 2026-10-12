"""Pure helpers to convert between REPOMAP text and an editable tree.

``# REPOMAP`` is an indented directory listing parsed by
``code_starter.blueprint_renderer.parse_repomap``: four spaces per nesting
level, tree-connector glyphs ignored, and entries that look like *files*
(a suffix and no trailing ``/``) are skipped. This module turns that text into a
nested list of nodes for the UI tree editor and back again, so the editor can
keep ``st.session_state["sf_repomap"]`` as the single canonical value used by
verification and saving.

A node is a plain dict: ``{"name": str, "children": list[Node]}``.
"""

from __future__ import annotations

import re
from pathlib import Path

Node = dict  # {"name": str, "children": list[Node]}

INDENT = 4  # spaces per nesting level (matches parse_repomap)

# Leading tree-connector glyphs used by hand-drawn repo maps: │ ├ └ ─ + ` _ and
# whitespace. Stripped before the entry name is read.
_CONNECTOR_RE = re.compile(r"^[|\-+`_\s]+")
# Trailing "(comment)" annotations, e.g. "src/ (source packages)".
_COMMENT_RE = re.compile(r"\s*\(")

_NONE_TOKENS = {"", "NONE", "EMPTY"}


def _clean_name(raw: str) -> str | None:
    """Return the directory name from a raw REPOMAP line, or None if it's a file."""
    name = _CONNECTOR_RE.sub("", raw.strip()).strip()
    name = _COMMENT_RE.split(name)[0].strip()
    if not name:
        return None
    # REPOMAP seeds directories only: entries with a file extension are ignored
    # unless they end with "/" (which protects dotted directory names).
    if not name.endswith("/") and Path(name).suffix:
        return None
    return name.rstrip("/").strip()


def parse_text(text: str) -> list[Node]:
    """Parse REPOMAP text into a list of ``{"name", "children"}`` nodes."""
    if text is None or text.strip().upper() in _NONE_TOKENS:
        return []

    roots: list[Node] = []
    stack: list[Node] = []  # stack[level] == node owning children at that level
    for raw in text.splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        level = (len(raw) - len(raw.lstrip())) // INDENT
        name = _clean_name(raw)
        if name is None:
            continue
        node: Node = {"name": name, "children": []}
        stack = stack[:level]  # drop deeper levels, keep the parent chain
        if stack:
            stack[-1]["children"].append(node)
        else:
            roots.append(node)
        stack.append(node)
    return roots


def to_text(nodes: list[Node]) -> str:
    """Serialize a tree back to REPOMAP text (DFS pre-order, 4-space indent)."""
    lines: list[str] = []

    def walk(items: list[Node], level: int) -> None:
        for node in items:
            lines.append(" " * (INDENT * level) + node["name"] + "/")
            walk(node.get("children", []), level + 1)

    walk(nodes, 0)
    return "\n".join(lines)


def count(nodes: list[Node]) -> int:
    """Total number of nodes (directories) in the tree."""
    return sum(1 + count(node.get("children", [])) for node in nodes)


def find(nodes: list[Node], path: list[int]) -> Node | None:
    """Return the node at ``path`` (list of child indices), or None."""
    current = None
    items = nodes
    for index in path:
        if index < 0 or index >= len(items):
            return None
        current = items[index]
        items = current.get("children", [])
    return current
