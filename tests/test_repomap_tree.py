"""Round-trip tests for the REPOMAP tree<->text helpers."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "ui"))

from core import repomap_tree as rt  # noqa: E402


def test_roundtrip_simple():
    text = "src/\n    code_starter/\n    code_converter/\nui/\n    views/"
    tree = rt.parse_text(text)
    assert rt.count(tree) == 5
    assert rt.to_text(tree) == text


def test_ascii_connectors_comments_and_nesting():
    # Nesting comes from leading spaces (4/level); leading ASCII connectors and
    # trailing "(comments)" are stripped -- mirroring parse_repomap exactly.
    text = "- src/\n    `- code_starter/   (starter pkg)\n+ ui/"
    tree = rt.parse_text(text)
    assert [n["name"] for n in tree] == ["src", "ui"]
    assert tree[0]["children"][0]["name"] == "code_starter"


def test_none_and_blank_are_empty():
    for value in ("", "   ", "NONE", "none", "EMPTY"):
        assert rt.parse_text(value) == []
    assert rt.to_text([]) == ""


def test_file_entries_are_ignored():
    tree = rt.parse_text("src/\n    main.py\n    pkg/\n")
    assert [n["name"] for n in tree[0]["children"]] == ["pkg"]


def test_dotted_directory_name_survives_roundtrip():
    tree = [{"name": "my.tools", "children": []}]
    text = rt.to_text(tree)
    assert text == "my.tools/"  # trailing slash keeps it a directory
    assert rt.parse_text(text) == [{"name": "my.tools", "children": []}]


def test_find_by_path():
    tree = rt.parse_text("a/\n    b/\n        c/\n")
    assert rt.find(tree, [0, 0, 0])["name"] == "c"
    assert rt.find(tree, [0, 5]) is None
