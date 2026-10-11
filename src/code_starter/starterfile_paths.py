"""Parse the optional ``# PATHS`` section of a ``starterfile.pseudo``.

The section declares *generation-time* locations for the target project::

    # PATHS
    root: .
    data_dir: data

Only ``root`` and ``data_dir`` are consumed today. ``root`` is a path relative
to the starterfile (portable, like the legacy ``# PROJECT_ROOT:`` marker, which
is still recognised for backward compatibility). ``data_dir`` is forwarded to
:func:`shared.paths_config.resolve_data_dir` as the project-level value and, when
present, authorises creating that directory during generation.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, Union

PATHS_HEADER = re.compile(r"^#\s*PATHS\s*$", re.IGNORECASE)
SECTION_HEADER = re.compile(r"^#\s+\w")
LEGACY_ROOT = re.compile(r"^#\s*PROJECT_ROOT:\s*(.*?)\s*$", re.MULTILINE)
ENTRY = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)\s*:\s*(.+?)\s*$")


def parse_text_paths(content: str) -> Dict[str, str]:
    """Parse ``# PATHS`` key/value entries out of starterfile text."""
    paths: Dict[str, str] = {}
    in_paths = False
    for line in content.splitlines():
        stripped = line.strip()
        if PATHS_HEADER.match(stripped):
            in_paths = True
            continue
        if in_paths and SECTION_HEADER.match(stripped):
            break
        if not in_paths or not stripped or stripped.startswith("#"):
            continue
        match = ENTRY.match(stripped)
        if match:
            paths[match.group(1).lower()] = match.group(2)

    # Backward compatibility: honour the legacy ``# PROJECT_ROOT:`` marker when
    # no explicit ``root`` was declared.
    if "root" not in paths:
        legacy = LEGACY_ROOT.search(content)
        if legacy:
            paths["root"] = legacy.group(1) or "."
    return paths


def parse_paths(source: Union[str, Path]) -> Dict[str, str]:
    """Return the ``# PATHS`` mapping for a starterfile, or ``{}``.

    Missing or unreadable files yield an empty mapping so callers can treat
    "no ``# PATHS`` section" and "no file" identically.
    """
    path = Path(source)
    if not path.is_file():
        return {}
    try:
        content = path.read_text(encoding="utf-8")
    except OSError:
        return {}
    return parse_text_paths(content)
