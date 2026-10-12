"""Pure model for the ``# PSEUDOCODE`` starterfile section.

The Starter page's Pseudocode tab builds the ``# PSEUDOCODE`` body one
*script-module* at a time. Per the design, each module is one entry under a
folder declared in the REPOMAP, and each entry carries the preset fields
(INPUT / OUTPUT / TASK / CONDITIONS / PREFERENCES) plus an optional
``FUNCTION MODEL``.

This module is the pure, Streamlit-free core: it parses the section text into a
structured model, lets callers add/remove entries, derives the folder choices
from the REPOMAP, and renders the model back to text the analyzer accepts.

Model::

    [{"path": "src/pkg/module.py",
      "fields": {"INPUT": ..., "OUTPUT": ..., "TASK": ...,
                 "CONDITIONS": ..., "PREFERENCES": ...},
      "functions": [{"name": ..., "kind": ..., "inputs": ..., "returns": ...,
                     "formula": ..., "criteria": ...}]}]

Grammar (mirrors :mod:`code_analyzer.pseudocode_analyzer`)::

    ## src/pkg/module.py
    INPUT: what the module reads
    OUTPUT: what it produces
    TASK: responsibilities and steps
    CONDITIONS: constraints and error cases
    PREFERENCES: style or library preferences
    FUNCTION MODEL:
      - name: score
        kind: math
        formula: sum(values) / len(values)
"""

from __future__ import annotations

import posixpath
import re
from pathlib import Path
from typing import Dict, List, Optional

from core import repomap_tree as rt
from code_starter import function_model as fm

FIELD_ORDER = ("INPUT", "OUTPUT", "TASK", "CONDITIONS", "PREFERENCES")
REQUIRED_FIELDS = ("TASK",)

_NONE_TOKENS = {"", "NONE", "EMPTY"}
_HEADER_RE = re.compile(r"^##\s+(.+?)\s*$")
_FIELD_LABEL_RE = re.compile(r"^([A-Z][A-Z ]*):\s*(.*)$")

Entry = dict    # {"path": str, "fields": dict, "functions": list}
Function = dict  # {"name","kind","inputs","returns","formula","criteria"}


def is_none(text: str) -> bool:
    """True when ``text`` means "no pseudocode entries"."""
    return (text or "").strip().upper() in _NONE_TOKENS


# -- function dict <-> dataclass ----------------------------------------

def _to_functions(dicts: List[Function]) -> List[fm.Function]:
    functions = []
    for item in dicts:
        functions.append(
            fm.Function(
                name=item.get("name", ""),
                kind=item.get("kind", "step") or "step",
                inputs=item.get("inputs", ""),
                returns=item.get("returns", ""),
                formula=item.get("formula", ""),
                criteria=item.get("criteria", ""),
            )
        )
    return functions


def _from_functions(functions: List[fm.Function]) -> List[Function]:
    return [
        {
            "name": f.name,
            "kind": f.kind or "step",
            "inputs": f.inputs,
            "returns": f.returns,
            "formula": f.formula,
            "criteria": f.criteria,
        }
        for f in functions
    ]


# -- parsing -------------------------------------------------------------

def _parse_body(body: str):
    """Return ``(fields, functions)`` for one entry body."""
    collected: Dict[str, List[str]] = {key: [] for key in FIELD_ORDER}
    current: Optional[str] = None
    skipping_function_model = False

    for line in body.splitlines():
        match = _FIELD_LABEL_RE.match(line)
        if match:
            key = " ".join(match.group(1).split())
            if key == fm.FIELD_LABEL:
                skipping_function_model = True
                current = None
                continue
            skipping_function_model = False
            if key in FIELD_ORDER:
                current = key
                if match.group(2):
                    collected[key].append(match.group(2))
                continue
            current = None
            continue
        if skipping_function_model:
            continue
        if current is not None:
            collected[current].append(line.lstrip())

    fields = {
        key: "\n".join(part.rstrip() for part in collected[key]).strip("\n")
        for key in FIELD_ORDER
    }
    functions, _ = fm.parse(body)
    return fields, _from_functions(functions)


def parse(text: str) -> List[Entry]:
    """Parse PSEUDOCODE text into a tolerant, editable model (never raises)."""
    if is_none(text):
        return []

    entries: List[Entry] = []
    current: Optional[Entry] = None
    body_lines: List[str] = []

    def flush() -> None:
        nonlocal current, body_lines
        if current is not None:
            fields, functions = _parse_body("\n".join(body_lines))
            current["fields"] = fields
            current["functions"] = functions
            entries.append(current)
        current, body_lines = None, []

    for raw in text.splitlines():
        match = _HEADER_RE.match(raw)
        if match:
            flush()
            current = {"path": match.group(1).strip(), "fields": {}, "functions": []}
            continue
        if current is not None:
            body_lines.append(raw)
    flush()
    return entries


# -- rendering -----------------------------------------------------------

def render(entries: List[Entry]) -> str:
    """Render the model to canonical PSEUDOCODE text (``""`` when empty)."""
    return "\n\n".join(_render_entry(entry) for entry in entries)


def _render_entry(entry: Entry) -> str:
    lines = ["## " + entry.get("path", "")]
    fields = entry.get("fields", {})
    for key in FIELD_ORDER:
        value = (fields.get(key) or "").strip("\n")
        if not value:
            lines.append(key + ":")
        elif "\n" in value:
            lines.append(key + ":")
            lines.extend("    " + part for part in value.splitlines())
        else:
            lines.append(key + ": " + value)
    functions = _to_functions(entry.get("functions", []))
    if functions:
        lines.append(fm.render(functions))
    return "\n".join(lines)


# -- folders from the REPOMAP -------------------------------------------

def folders_from_repomap(repomap_text: str) -> List[str]:
    """Return every folder path declared in a REPOMAP body (depth-first)."""
    if is_none(repomap_text):
        return []
    paths: List[str] = []

    def walk(nodes, prefix: str) -> None:
        for node in nodes:
            path = prefix + "/" + node["name"] if prefix else node["name"]
            paths.append(path)
            walk(node.get("children", []), path)

    walk(rt.parse_text(repomap_text), "")
    return paths


def join_path(folder: str, filename: str) -> str:
    """Combine a REPOMAP folder with a script filename (defaults to ``.py``)."""
    name = (filename or "").strip()
    if name and not Path(name).suffix:
        name += ".py"
    folder = (folder or "").strip().strip("/")
    if folder in {"", ".", "(root)"}:
        return name
    return folder + "/" + name


# -- mutation helpers ----------------------------------------------------

def add_entry(entries: List[Entry], path: str) -> Entry:
    entry: Entry = {
        "path": path,
        "fields": {key: "" for key in FIELD_ORDER},
        "functions": [],
    }
    entries.append(entry)
    return entry


def remove_entry(entries: List[Entry], index: int) -> None:
    del entries[index]


def add_function(entry: Entry, name: str = "new_function") -> Function:
    function: Function = {
        "name": name,
        "kind": "step",
        "inputs": "",
        "returns": "",
        "formula": "",
        "criteria": "",
    }
    entry.setdefault("functions", []).append(function)
    return function


def remove_function(entry: Entry, index: int) -> None:
    del entry["functions"][index]


def count(entries: List[Entry]) -> int:
    return len(entries)


def count_functions(entries: List[Entry]) -> int:
    return sum(len(entry.get("functions", [])) for entry in entries)


def function_findings(entry: Entry) -> List[fm.Finding]:
    """Validate one entry's FUNCTION MODEL against its TASK."""
    return fm.validate(
        _to_functions(entry.get("functions", [])),
        entry.get("fields", {}).get("TASK", "") or "",
    )


def orphan_paths(entries: List[Entry], folders: List[str]) -> List[str]:
    """Entry paths not under any REPOMAP folder (the ``structure-orphan-file`` rule)."""
    if not folders:
        return []
    orphans: List[str] = []
    for entry in entries:
        path = (entry.get("path") or "").strip()
        normalized = posixpath.normpath(path)
        if path and not any(
            normalized == folder or normalized.startswith(folder + "/")
            for folder in folders
        ):
            orphans.append(path)
    return orphans


# -- light validation (for inline badges; Verify uses the real analyzer) --

def entry_problems(entry: Entry, folders: Optional[List[str]] = None) -> List[str]:
    """Return short human-readable problems with one entry (for inline display)."""
    problems: List[str] = []
    path = (entry.get("path") or "").strip()
    if not path:
        problems.append("no file path")
    else:
        if Path(path).is_absolute():
            problems.append("absolute path")
        normalized = posixpath.normpath(path)
        if normalized == ".." or normalized.startswith("../"):
            problems.append("path escapes the project root")
        if not Path(path).suffix:
            problems.append("no file extension")
        if folders and not any(
            normalized == folder or normalized.startswith(folder + "/")
            for folder in folders
        ):
            problems.append("not under any REPOMAP folder")
    for key in REQUIRED_FIELDS:
        if not (entry.get("fields", {}).get(key) or "").strip():
            problems.append("no {} field".format(key))
    return problems
