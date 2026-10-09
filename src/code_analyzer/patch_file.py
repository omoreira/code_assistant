"""Read and apply the ``patch.pseudo`` file format.

The file has ``#PATCHES`` and ``#NEW SCRIPTS`` sections. Each entry starts
with ``## path/to/file``. Patch entries contain a unified diff; new script
entries contain the complete file contents.
"""

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Dict, List, Optional, Tuple


@dataclass
class PatchEntry:
    path: str
    content: str


@dataclass
class PatchFile:
    patches: List[PatchEntry]
    new_scripts: List[PatchEntry]


def parse_patch_file(filename: str) -> PatchFile:
    """Parse sections and ``## relative/path`` entries from a patch file."""
    text = Path(filename).read_text(encoding="utf-8")
    section: Optional[str] = None
    path: Optional[str] = None
    lines: List[str] = []
    groups: Dict[str, List[PatchEntry]] = {"patches": [], "new_scripts": []}

    def save() -> None:
        if path is not None and section in groups:
            groups[section].append(PatchEntry(path, "\n".join(lines).rstrip("\n")))

    for line in text.splitlines():
        marker = line.strip().upper()
        if marker == "#PATCHES":
            save()
            section, path, lines = "patches", None, []
        elif marker in ("#NEW SCRIPTS", "#NEW_SCRIPTS"):
            save()
            section, path, lines = "new_scripts", None, []
        elif section and re.match(r"^##\s+\S", line):
            save()
            path = line[2:].strip()
            lines = []
        elif section and path is not None:
            lines.append(line)
    save()
    return PatchFile(groups["patches"], groups["new_scripts"])


def _safe_target(root: Path, relative: str) -> Path:
    candidate = Path(relative)
    if candidate.is_absolute():
        raise ValueError("Patch paths must be relative to project_root")
    target = (root / candidate).resolve()
    try:
        target.relative_to(root)
    except ValueError as exc:
        raise ValueError("Patch path escapes project_root: {}".format(relative)) from exc
    return target


def _apply_unified_diff(original: str, diff: str) -> str:
    """Apply unified diff hunks with strict context matching."""
    source = original.splitlines(keepends=True)
    diff_lines = diff.splitlines(keepends=True)
    result: List[str] = []
    cursor = 0
    index = 0
    while index < len(diff_lines):
        if not diff_lines[index].startswith("@@"):
            index += 1
            continue
        match = re.match(r"@@ -(\d+)(?:,\d+)? \+(\d+)(?:,\d+)? @@", diff_lines[index])
        if not match:
            raise ValueError("Malformed unified diff hunk header")
        old_start = max(0, int(match.group(1)) - 1)
        if old_start < cursor:
            raise ValueError("Overlapping or out-of-order diff hunks")
        result.extend(source[cursor:old_start])
        cursor = old_start
        index += 1
        while index < len(diff_lines) and not diff_lines[index].startswith("@@"):
            line = diff_lines[index]
            if line.startswith("\\ No newline"):
                index += 1
                continue
            if not line or line[0] not in " +-":
                raise ValueError("Malformed unified diff line: {}".format(line.rstrip()))
            body = line[1:]
            if line[0] in " -":
                if cursor >= len(source) or source[cursor].rstrip("\r\n") != body.rstrip("\r\n"):
                    raise ValueError("Patch context does not match target near line {}".format(cursor + 1))
                if line[0] == " ":
                    result.append(source[cursor])
                cursor += 1
            elif line[0] == "+":
                result.append(body)
            index += 1
    result.extend(source[cursor:])
    return "".join(result)


def apply_patch_file(filename: str, project_root: str = ".", dry_run: bool = False) -> List[str]:
    """Apply every patch and create every new script; return changed paths.

    All entries are validated and rendered before any files are written.
    Existing files are never overwritten by ``#NEW SCRIPTS`` entries.
    """
    root = Path(project_root).resolve()
    parsed = parse_patch_file(filename)
    rendered: List[Tuple[Path, str, bool]] = []
    for entry in parsed.patches:
        target = _safe_target(root, entry.path)
        if not target.is_file():
            raise FileNotFoundError("Patch target does not exist: {}".format(entry.path))
        original = target.read_text(encoding="utf-8")
        rendered.append((target, _apply_unified_diff(original, entry.content), False))
    for entry in parsed.new_scripts:
        target = _safe_target(root, entry.path)
        if target.exists():
            raise FileExistsError("New script already exists: {}".format(entry.path))
        rendered.append((target, entry.content + ("\n" if entry.content else ""), True))
    if not dry_run:
        for target, content, _ in rendered:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
    return [str(target.relative_to(root)) for target, _, _ in rendered]
