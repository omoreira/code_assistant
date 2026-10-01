"""Code analysis, debugging, and applying user-authored code patches."""

from code_debugger.patch_file import (
    PatchEntry,
    PatchFile,
    apply_patch_file,
    parse_patch_file,
)

__version__ = "0.1.0"
__author__ = "Olga Moreira"

__all__ = ["PatchEntry", "PatchFile", "parse_patch_file", "apply_patch_file"]
