"""Render a ``starterfile.pseudo`` as coloured HTML for human review.

Pure and Streamlit-free: :func:`classify` labels each line by its role (status
marker, section header, entry header, field label, function-model line, tag) and
:func:`colorize` wraps the file in a ``<pre>`` block of coloured spans. The
Starter page's Review tab composes :data:`CSS` + :func:`colorize` through
``st.markdown(..., unsafe_allow_html=True)``.

Content is HTML-escaped, so arbitrary starterfile text is safe to embed.
"""

from __future__ import annotations

import html
import re

#: Stylesheet for the coloured view (dark, monospace).
CSS = """<style>
.sf-view { background:#0d1117; color:#c9d1d9; padding:14px 16px; border-radius:10px;
  border:1px solid #30363d; font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  font-size:0.82rem; line-height:1.5; overflow-x:auto; white-space:pre; }
.sf-status-ok { color:#3fb950; font-weight:700; }
.sf-status-bad { color:#f85149; font-weight:700; }
.sf-tag-error { color:#f85149; font-weight:600; }
.sf-tag-warning { color:#d29922; font-weight:600; }
.sf-tag-info { color:#8b949e; }
.sf-section { color:#58a6ff; font-weight:700; }
.sf-entry { color:#d2a8ff; font-weight:600; }
.sf-label { color:#ffa657; font-weight:700; }
.sf-fn { color:#7ee787; }
.sf-key { color:#79c0ff; }
.sf-text { color:#c9d1d9; }
</style>"""

_STATUS_RE = re.compile(r"^#\s*STATUS\s*:\s*([A-Za-z0-9_]+)\s*$")
_TAG_RE = re.compile(r"^#\s*TAG\s*:\s*([A-Za-z]+)")
_ENTRY_RE = re.compile(r"^##\s+")
_SECTION_RE = re.compile(r"^#\s+([A-Za-z_][A-Za-z0-9_ ]*?)\s*$")
_FIELD_RE = re.compile(r"^([A-Z][A-Z ]*):")
_FN_ITEM_RE = re.compile(r"^\s*[-*]\s*name\s*:", re.IGNORECASE)
_FN_KEY_RE = re.compile(r"^\s*(?:kind|inputs|returns|formula|criteria)\s*:", re.IGNORECASE)

_ROLE_CLASS = {
    "status-ok": "sf-status-ok",
    "status-bad": "sf-status-bad",
    "tag-error": "sf-tag-error",
    "tag-warning": "sf-tag-warning",
    "tag-info": "sf-tag-info",
    "section": "sf-section",
    "entry": "sf-entry",
    "fn": "sf-fn",
    "key": "sf-key",
    "text": "sf-text",
}


def classify(line: str) -> str:
    """Return the role of one starterfile line (a key of :data:`_ROLE_CLASS`,
    plus ``"blank"`` and ``"field"``)."""
    if not line.strip():
        return "blank"
    match = _STATUS_RE.match(line)
    if match:
        return "status-ok" if match.group(1).upper() == "APPROVED" else "status-bad"
    match = _TAG_RE.match(line)
    if match:
        severity = match.group(1).upper()
        if severity == "ERROR":
            return "tag-error"
        if severity == "WARNING":
            return "tag-warning"
        return "tag-info"
    if _ENTRY_RE.match(line):
        return "entry"
    if _SECTION_RE.match(line):
        return "section"
    if _FIELD_RE.match(line):
        return "field"
    if _FN_ITEM_RE.match(line):
        return "fn"
    if _FN_KEY_RE.match(line):
        return "key"
    return "text"


def _line_html(line: str) -> str:
    role = classify(line)
    if role == "blank":
        return ""
    if role == "field":
        match = _FIELD_RE.match(line)
        label = match.group(1)
        return '<span class="sf-label">{}</span>{}'.format(
            html.escape(label), html.escape(line[len(label):])
        )
    return '<span class="{}">{}</span>'.format(_ROLE_CLASS[role], html.escape(line))


def colorize(text: str) -> str:
    """Wrap ``text`` in a ``<pre>`` block with one coloured span per line."""
    if not text.strip():
        return '<pre class="sf-view"></pre>'
    body = "\n".join(_line_html(line) for line in text.rstrip("\n").split("\n"))
    return '<pre class="sf-view">{}</pre>'.format(body)


def role_counts(text: str) -> dict:
    """Count lines per role (handy for summaries and tests)."""
    counts: dict = {}
    for line in text.splitlines():
        role = classify(line)
        counts[role] = counts.get(role, 0) + 1
    return counts
