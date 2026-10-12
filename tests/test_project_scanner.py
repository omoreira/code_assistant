"""Tests for scanning a project root into a REPOMAP directory tree."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "ui"))

from core import project_scanner as ps  # noqa: E402
from core import repomap_tree as rt  # noqa: E402


def _make_project(tmp_path: Path) -> Path:
    """Build a small project tree mixing real dirs, files and junk."""
    for rel in (
        "src",
        "src/code_starter",
        "src/code_starter/nested",
        "ui",
        "ui/views",
        "docs",
        ".git/hooks",
        "venv/lib",
        "__pycache__",
        "node_modules/pkg",
        "build",
        ".hidden_dir",
    ):
        (tmp_path / rel).mkdir(parents=True, exist_ok=True)
    for rel in ("README.md", "src/main.py", "ui/views/starter.py"):
        (tmp_path / rel).write_text("x", encoding="utf-8")
    return tmp_path


def test_dirs_only_and_sorted(tmp_path):
    root = _make_project(tmp_path)
    tree = ps.scan_project_root(root)
    assert [n["name"] for n in tree] == ["docs", "src", "ui"]
    # Files (README.md) are never included.
    assert "README.md" not in [n["name"] for n in tree]


def test_nesting_is_preserved(tmp_path):
    root = _make_project(tmp_path)
    tree = ps.scan_project_root(root)
    src = next(n for n in tree if n["name"] == "src")
    assert [c["name"] for c in src["children"]] == ["code_starter"]
    assert [c["name"] for c in src["children"][0]["children"]] == ["nested"]


def test_junk_and_hidden_dirs_ignored(tmp_path):
    root = _make_project(tmp_path)
    tree = ps.scan_project_root(root)
    names = {n["name"] for n in tree}
    assert names.isdisjoint({"venv", "__pycache__", "node_modules", "build", ".hidden_dir"})
    # .git is skipped because hidden (and in the ignore set).
    assert ".git" not in names


def test_max_depth_limits_descent(tmp_path):
    root = _make_project(tmp_path)
    shallow = ps.scan_project_root(root, max_depth=1)
    src = next(n for n in shallow if n["name"] == "src")
    assert src["children"] == []  # children listed but not descended into
    assert [n["name"] for n in shallow] == ["docs", "src", "ui"]


def test_include_hidden_option(tmp_path):
    root = _make_project(tmp_path)
    tree = ps.scan_project_root(root, include_hidden=True)
    assert ".hidden_dir" in {n["name"] for n in tree}
    assert ".git" not in {n["name"] for n in tree}  # explicit ignore wins


def test_missing_or_file_root_returns_empty(tmp_path):
    assert ps.scan_project_root(tmp_path / "nope") == []
    afile = tmp_path / "a.txt"
    afile.write_text("x", encoding="utf-8")
    assert ps.scan_project_root(afile) == []


def test_scan_text_roundtrips(tmp_path):
    root = _make_project(tmp_path)
    text = ps.scan_project_root_text(root)
    assert rt.parse_text(text) == ps.scan_project_root(root)
    # Real REPOMAP the project parser understands (4-space indent, sorted).
    assert text.splitlines()[0] == "docs/"
    assert "src/\n    code_starter/" in text


def test_symlink_not_followed(tmp_path):
    root = _make_project(tmp_path)
    link = root / "linked"
    try:
        link.symlink_to(root / "src", target_is_directory=True)
    except (OSError, NotImplementedError):
        return  # platform without symlink support
    names = {n["name"] for n in ps.scan_project_root(root)}
    assert "linked" not in names
