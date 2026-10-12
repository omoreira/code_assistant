"""Tests for the pure starterfile colouriser (``ui/core/starterfile_view.py``)."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
for _p in (REPO_ROOT / "ui", REPO_ROOT / "src"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from core import starterfile_view as sv  # noqa: E402


def test_classify_roles():
    assert sv.classify("# STATUS: APPROVED") == "status-ok"
    assert sv.classify("# STATUS: DRAFT") == "status-bad"
    assert sv.classify("# TAG: ERROR: boom") == "tag-error"
    assert sv.classify("# TAG: WARNING: hmm") == "tag-warning"
    assert sv.classify("# TAG: INFO: note") == "tag-info"
    assert sv.classify("# REPOMAP") == "section"
    assert sv.classify("## src/pkg/module.py") == "entry"
    assert sv.classify("TASK: do the thing") == "field"
    assert sv.classify("FUNCTION MODEL:") == "field"
    assert sv.classify("- name: score") == "fn"
    assert sv.classify("    kind: math") == "key"
    assert sv.classify("") == "blank"
    assert sv.classify("   ") == "blank"
    assert sv.classify("root: .") == "text"


def test_colorize_escapes_html():
    out = sv.colorize("## <script>alert(1)</script>")
    assert "<script>" not in out
    assert "&lt;script&gt;" in out


def test_colorize_marks_roles():
    out = sv.colorize("# STATUS: APPROVED\n# TAG: ERROR: x\nTASK: go")
    assert out.startswith('<pre class="sf-view">')
    assert 'class="sf-status-ok"' in out
    assert 'class="sf-tag-error"' in out
    assert 'class="sf-label"' in out


def test_colorize_empty():
    assert sv.colorize("") == '<pre class="sf-view"></pre>'
    assert sv.colorize("   \n  ") == '<pre class="sf-view"></pre>'


def test_role_counts():
    counts = sv.role_counts("# STATUS: APPROVED\n# REPOMAP\n## a.py\n")
    assert counts["status-ok"] == 1
    assert counts["section"] == 1
    assert counts["entry"] == 1
