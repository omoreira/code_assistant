"""Parse and validate the optional ``FUNCTION MODEL`` of a PSEUDOCODE entry.

A FUNCTION MODEL declares the callable units a module provides and that its
``TASK`` may invoke -- named **steps**, **math** formulas, and **criteria**
(predicates/thresholds). It is written inside a PSEUDOCODE entry body as::

    FUNCTION MODEL:
      - name: score
        kind: math
        inputs: values: list[float], weights: list[float]
        returns: float
        formula: sum(w * v for w, v in zip(weights, values))
        criteria: 0 <= score <= 1
      - name: decide
        kind: criteria
        inputs: score: float
        returns: str
        criteria: score >= 0.5 -> "accept" else "reject"

Input/return **types are free text** (only their ``name: type`` shape is
checked). The **mechanics** (structure) and the **math** (that ``formula`` /
``criteria`` are parseable expressions) are validated.

Findings use the analyzer's ``# TAG:`` shape so the UI can render them
uniformly alongside :mod:`code_analyzer.pseudocode_analyzer` tags.
"""

from __future__ import annotations

import ast
import re
from dataclasses import dataclass
from typing import List, Optional, Set, Tuple

#: The field label. NOTE: must contain no hyphen -- the analyzer's field regex
#: is ``^([A-Z][A-Z ]*):`` which allows uppercase letters and spaces only.
FIELD_LABEL = "FUNCTION MODEL"

_FIELD_LABEL_RE = re.compile(r"^([A-Z][A-Z ]*):\s*(.*)$")
_ITEM_RE = re.compile(r"^\s*[-*]\s*name\s*:\s*(?P<name>.+?)\s*$", re.IGNORECASE)
_KEY_RE = re.compile(r"^\s*(?P<key>[A-Za-z][A-Za-z ]*?)\s*:\s*(?P<value>.*)$")
_IDENT_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
_CALL_RE = re.compile(r"\b([A-Za-z_][A-Za-z0-9_]*)\s*\(")

KNOWN_KEYS = ("name", "kind", "inputs", "returns", "formula", "criteria")
KNOWN_KINDS = ("step", "math", "criteria", "predicate", "function")


@dataclass
class Finding:
    """A single validation finding (mirrors the analyzer's tag style)."""

    severity: str  # "ERROR" | "WARNING"
    code: str
    message: str
    name: Optional[str] = None

    def render(self) -> str:
        where = " [{}]".format(self.name) if self.name else ""
        return "# TAG: {}: {}{}: {}".format(self.severity, self.code, where, self.message)


@dataclass
class Function:
    """One declared function/step/math/criterion."""

    name: str
    kind: str = "step"
    inputs: str = ""
    returns: str = ""
    formula: str = ""
    criteria: str = ""


# -- parsing ----------------------------------------------------------------

def extract_block(body: str) -> Optional[str]:
    """Return the FUNCTION MODEL block text, or None if the field is absent.

    The block runs from the ``FUNCTION MODEL:`` line to the next top-level
    field label (e.g. ``CONDITIONS:``) or the end of the entry body.
    """
    collected: List[str] = []
    collecting = False
    for line in body.splitlines():
        label = _FIELD_LABEL_RE.match(line)
        if label:
            if " ".join(label.group(1).split()) == FIELD_LABEL:
                collecting = True
                inline = label.group(2).strip()
                if inline:
                    collected.append(inline)
                continue
            if collecting:
                break  # a later field (TASK/CONDITIONS/...) ends the block
        if collecting:
            collected.append(line)
    if not collecting:
        return None
    return "\n".join(collected)


def parse_block(block: str) -> Tuple[List[Function], List[Finding]]:
    """Parse a FUNCTION MODEL block into functions plus structural findings."""
    functions: List[Function] = []
    findings: List[Finding] = []
    current: Optional[Function] = None

    for raw in block.splitlines():
        if not raw.strip():
            continue
        item = _ITEM_RE.match(raw)
        if item:
            current = Function(name=item.group("name").strip())
            functions.append(current)
            continue
        key = _KEY_RE.match(raw)
        if key:
            if current is None:
                findings.append(
                    Finding("ERROR", "function-model-malformed",
                            "field {!r} appears before any '- name:' entry".format(key.group("key").strip()))
                )
                continue
            name = key.group("key").strip().lower()
            value = key.group("value").strip()
            if name == "name":
                continue
            if name in KNOWN_KEYS:
                setattr(current, name, value)
            else:
                findings.append(
                    Finding("WARNING", "unknown-function-key",
                            "unknown key {!r} in function {!r}".format(name, current.name), current.name)
                )
            continue
        findings.append(
            Finding("ERROR", "function-model-malformed", "unrecognized line: {!r}".format(raw.strip()))
        )
    if not functions:
        findings.append(
            Finding("ERROR", "function-model-empty", "FUNCTION MODEL has no '- name:' entries")
        )
    return functions, findings


def parse(body: str) -> Tuple[List[Function], List[Finding]]:
    """Parse the FUNCTION MODEL from a full PSEUDOCODE entry body."""
    block = extract_block(body)
    if block is None:
        return [], []
    return parse_block(block)


# -- validation -------------------------------------------------------------

def _is_expression(text: str) -> bool:
    text = (text or "").strip()
    if not text:
        return False
    try:
        ast.parse(text, mode="eval")
        return True
    except SyntaxError:
        return False


def _criteria_parses(text: str) -> bool:
    """A criterion may use 'COND -> outcome'; only the COND part is checked."""
    left = text.split("->", 1)[0].strip()
    return _is_expression(left)


def _task_referenced_names(task: str) -> Set[str]:
    """Names TASK appears to invoke: call form ``f(`` or arrow chains ``a -> b``."""
    names: Set[str] = set()
    if not task:
        return names
    names.update(_CALL_RE.findall(task))
    if "->" in task:
        for part in task.split("->"):
            tokens = part.strip().split()
            token = tokens[-1] if tokens else ""
            if _IDENT_RE.match(token):
                names.add(token)
    return names


def validate(functions: List[Function], task: str = "") -> List[Finding]:
    """Mechanics + math checks over parsed functions (TASK cross-check included)."""
    findings: List[Finding] = []
    seen: Set[str] = set()

    for fn in functions:
        name = (fn.name or "").strip()
        if not name:
            findings.append(Finding("ERROR", "function-model-malformed", "an entry is missing 'name'"))
            continue
        if not _IDENT_RE.match(name):
            findings.append(Finding("WARNING", "function-name-not-identifier",
                                    "name {!r} is not a valid identifier".format(name), name))
        if name in seen:
            findings.append(Finding("ERROR", "duplicate-function",
                                    "function {!r} declared more than once".format(name), name))
        seen.add(name)

        kind = (fn.kind or "step").strip().lower() or "step"
        if kind not in KNOWN_KINDS:
            findings.append(Finding("WARNING", "unknown-function-kind",
                                    "unknown kind {!r}".format(kind), name))
        if fn.formula and not _is_expression(fn.formula):
            findings.append(Finding("WARNING", "formula-unparseable",
                                    "formula is not a valid expression: {}".format(fn.formula), name))
        if fn.criteria and not _criteria_parses(fn.criteria):
            findings.append(Finding("WARNING", "criteria-unparseable",
                                    "criteria is not a valid condition: {}".format(fn.criteria), name))
        if kind in ("math", "function") and not fn.formula:
            findings.append(Finding("ERROR", "math-function-missing-formula",
                                    "{!r} is a math function but declares no formula".format(name), name))
        if kind in ("criteria", "predicate") and not fn.criteria:
            findings.append(Finding("ERROR", "criteria-function-missing-criteria",
                                    "{!r} is a criterion but declares no criteria".format(name), name))

    declared = {fn.name.strip() for fn in functions if fn.name.strip()}
    for name in sorted(_task_referenced_names(task)):
        if name not in declared:
            findings.append(Finding("ERROR", "task-references-unknown-function",
                                    "TASK references {!r}, not declared in FUNCTION MODEL".format(name), name))
    return findings


def analyze(body: str, task: Optional[str] = None, *, required: bool = False) -> Tuple[List[Function], List[Finding]]:
    """Parse + validate the FUNCTION MODEL of one entry body.

    ``task`` defaults to the entry's own ``TASK:`` field; pass it explicitly to
    override. ``required=True`` adds a WARNING when the field is absent entirely.
    """
    if task is None:
        task = split_task(body)
    block = extract_block(body)
    if block is None:
        findings: List[Finding] = []
        if required:
            findings.append(Finding("WARNING", "function-model-missing",
                                    "entry has no FUNCTION MODEL"))
        return [], findings
    functions, structural = parse_block(block)
    return functions, structural + validate(functions, task)


def split_task(body: str) -> str:
    """Return the text of the entry's ``TASK:`` field (first line + continuations)."""
    lines = body.splitlines()
    task_lines: List[str] = []
    capturing = False
    for line in lines:
        label = _FIELD_LABEL_RE.match(line)
        if label and " ".join(label.group(1).split()) == "TASK":
            capturing = True
            task_lines.append(label.group(2))
            continue
        if capturing and label:
            break
        if capturing:
            task_lines.append(line)
    return " ".join(part.strip() for part in task_lines).strip()


# -- rendering --------------------------------------------------------------

def render(functions: List[Function], *, include_label: bool = True) -> str:
    """Render functions back to FUNCTION MODEL text (the editor/append format)."""
    lines: List[str] = [FIELD_LABEL + ":"] if include_label else []
    for fn in functions:
        lines.append("  - name: {}".format(fn.name))
        if fn.kind and fn.kind != "step":
            lines.append("    kind: {}".format(fn.kind))
        for key in ("inputs", "returns", "formula", "criteria"):
            value = getattr(fn, key)
            if value:
                lines.append("    {}: {}".format(key, value))
    return "\n".join(lines)


def count(functions: List[Function]) -> int:
    return len(functions)
