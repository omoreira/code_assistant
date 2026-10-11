"""Non-interactive assembly of a ``starterfile.pseudo``.

The interactive
:class:`~code_starter.starterfile_creator.StarterfileCreator` drives its menu
with ``input()``. This module exposes the same on-disk format as a small, pure
programmatic API so a caller (for example the Streamlit UI under ``ui/``) can
set one section at a time and render the file without prompts.

Canonical rendered output::

    # STATUS: APPROVED

    # PATHS
    root: .
    data_dir: data

    # REPOMAP
    <directory tree>

    # DATABASES
    <database specifications>

    # PSEUDOCODE
    ## relative/path.py
    INPUT: ...
    OUTPUT: ...
    TASK: ...

The ``# STATUS: APPROVED`` marker is written first so it can never leak into a
section body. ``REPOMAP``, ``DATABASES`` and ``PSEUDOCODE`` are always emitted
(``NONE`` when empty) because
:class:`code_analyzer.pseudocode_analyzer.PseudocodeAnalyzer` requires all three
sections to be present.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, Optional

from .starterfile_paths import parse_text_paths

#: Sections the analyzer requires to be present (bodies may be ``NONE``).
REQUIRED_SECTIONS = ("REPOMAP", "DATABASES", "PSEUDOCODE")

#: The approval marker that gates ``code_starter.pipeline``.
STATUS_LINE = "# STATUS: APPROVED"

_SECTION_HEADER = re.compile(r"^#\s+([A-Za-z_][A-Za-z0-9_ ]*?)\s*$")
_STATUS_MARKER = re.compile(r"^#\s*STATUS\s*:\s*([A-Za-z0-9_]+)\s*$", re.IGNORECASE)


def split_sections(text: str) -> Dict[str, str]:
    """Split starterfile text into ``{SECTION: body}`` with bodies stripped.

    Only top-level ``# NAME`` headers are recognised; the ``# STATUS:`` marker
    (which contains a colon) is not treated as a section.
    """
    sections: Dict[str, str] = {}
    current: Optional[str] = None
    body: list = []
    for line in text.splitlines():
        match = _SECTION_HEADER.match(line)
        if match:
            if current is not None:
                sections[current] = "\n".join(body).strip("\n")
            current = " ".join(match.group(1).split()).upper()
            body = []
        elif current is not None:
            body.append(line)
    if current is not None:
        sections[current] = "\n".join(body).strip("\n")
    return sections


class StarterfileBuilder:
    """Build and render a ``starterfile.pseudo`` without interactive prompts."""

    def __init__(
        self,
        path="starterfile.pseudo",
        *,
        root: str = ".",
        data_dir: str = "data",
    ) -> None:
        self.path = Path(path)
        self.root = root or "."
        self.data_dir = data_dir or "data"
        self.repomap = ""
        self.databases = ""
        self.pseudocode = ""
        self.approved = True

    # -- loading ---------------------------------------------------------
    @classmethod
    def from_file(cls, path, **kwargs) -> "StarterfileBuilder":
        """Create a builder and load sections from ``path`` when it exists."""
        builder = cls(path, **kwargs)
        builder.load()
        return builder

    def load(self) -> "StarterfileBuilder":
        """Populate this builder from ``self.path`` (no-op when missing)."""
        if not self.path.is_file():
            return self
        text = self.path.read_text(encoding="utf-8")
        paths = parse_text_paths(text)
        if paths.get("root"):
            self.root = paths["root"]
        if paths.get("data_dir"):
            self.data_dir = paths["data_dir"]
        sections = split_sections(text)
        self.repomap = sections.get("REPOMAP", self.repomap)
        self.databases = sections.get("DATABASES", self.databases)
        self.pseudocode = sections.get("PSEUDOCODE", self.pseudocode)
        self.approved = any(
            (_STATUS_MARKER.match(line) is not None
             and _STATUS_MARKER.match(line).group(1).upper() == "APPROVED")
            for line in text.splitlines()
        )
        return self

    # -- section access --------------------------------------------------
    def get_section(self, name: str) -> str:
        return {
            "REPOMAP": self.repomap,
            "DATABASES": self.databases,
            "PSEUDOCODE": self.pseudocode,
        }.get(name.upper(), "")

    def set_section(self, name: str, body: str) -> None:
        key = name.upper()
        if key == "REPOMAP":
            self.repomap = body
        elif key == "DATABASES":
            self.databases = body
        elif key == "PSEUDOCODE":
            self.pseudocode = body
        elif key == "PATHS":
            raise ValueError("Use set_paths() to update the PATHS section")
        else:
            raise ValueError("Unknown section: {}".format(name))

    def set_paths(self, root: str, data_dir: str) -> None:
        self.root = root or "."
        self.data_dir = data_dir or "data"

    # -- rendering -------------------------------------------------------
    def render(self) -> str:
        """Return the full starterfile text."""
        parts = [STATUS_LINE, "", "# PATHS"]
        parts.append("root: {}".format(self.root))
        parts.append("data_dir: {}".format(self.data_dir))
        for name, body in (
            ("REPOMAP", self.repomap),
            ("DATABASES", self.databases),
            ("PSEUDOCODE", self.pseudocode),
        ):
            parts.extend(["", "# {}".format(name)])
            parts.append(body.strip("\n") if body.strip() else "NONE")
        return "\n".join(parts).rstrip() + "\n"

    def write(self) -> Path:
        """Render and write the starterfile, returning its path."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(self.render(), encoding="utf-8")
        return self.path
