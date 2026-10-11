"""Filesystem locations used by the UI.

The UI never hard-codes paths: it derives the repository root from this file's
location and offers a dedicated ``ui/workspace`` folder as the default place to
write generated ``starterfile.pseudo`` files (so the repo's own
``src/code_starter/starterfile.pseudo`` is never clobbered by accident).
"""

from pathlib import Path

# ui/core/paths.py -> [0]=core [1]=ui [2]=<repo root>
REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = REPO_ROOT / "src"
UI_DIR = REPO_ROOT / "ui"
WORKSPACE_DIR = UI_DIR / "workspace"
