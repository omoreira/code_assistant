"""Scan a project directory into a REPOMAP tree (directories only).

The Starter page lets a user *create* a starterfile for an existing project. To
avoid hand-typing the ``# REPOMAP`` tree, this module walks the project root and
returns the same ``{"name", "children"}`` node shape used by
:mod:`core.repomap_tree`, so the result feeds straight into
``repomap_tree.to_text`` / the tree editor.

REPOMAP seeds **directories only** (file entries are ignored by
``code_starter.blueprint_renderer.parse_repomap``), so this scanner collects
directories and skips files entirely. Hidden directories and common
build/cache/virtualenv folders are skipped by default to keep the map clean.
"""

from __future__ import annotations

from pathlib import Path
from typing import FrozenSet, Iterable

from core.repomap_tree import Node, to_text

#: Directory names that never belong in a REPOMAP.
DEFAULT_IGNORE: FrozenSet[str] = frozenset(
    {
        ".git",
        ".hg",
        ".svn",
        ".venv",
        "venv",
        "env",
        "node_modules",
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        ".tox",
        ".eggs",
        "build",
        "dist",
        ".idea",
        ".vscode",
    }
)

#: How many directory levels below the root to descend.
DEFAULT_MAX_DEPTH = 4


def scan_project_root(
    root,
    *,
    max_depth: int = DEFAULT_MAX_DEPTH,
    ignore: Iterable[str] = DEFAULT_IGNORE,
    include_hidden: bool = False,
) -> list[Node]:
    """Return the directory tree under ``root`` as REPOMAP nodes.

    Only directories are included (files are ignored, matching REPOMAP
    semantics). ``max_depth`` counts directory levels below ``root`` (``1`` =
    the root's immediate children). Hidden directories (leading ``.``) and names
    in ``ignore`` are skipped unless ``include_hidden`` is set. Symlinks are not
    followed, so the walk cannot loop.
    """
    base = Path(root).expanduser()
    if not base.is_dir():
        return []

    ignore_set = set(ignore)

    def walk(directory: Path, depth: int) -> list[Node]:
        nodes: list[Node] = []
        try:
            entries = sorted(directory.iterdir(), key=lambda p: p.name.lower())
        except OSError:
            return nodes
        for entry in entries:
            if entry.is_symlink() or not entry.is_dir():
                continue
            name = entry.name
            if name in ignore_set:
                continue
            if not include_hidden and name.startswith("."):
                continue
            node: Node = {"name": name, "children": []}
            if depth < max_depth:
                node["children"] = walk(entry, depth + 1)
            nodes.append(node)
        return nodes

    return walk(base, 1)


def scan_project_root_text(root, **kwargs) -> str:
    """Convenience wrapper: scan ``root`` and render it as REPOMAP text."""
    return to_text(scan_project_root(root, **kwargs))
