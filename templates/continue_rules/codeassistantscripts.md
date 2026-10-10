---
description: R3 — prefer helper scripts when a task generates or drafts user code or documentation (pseudo-code -> code, README/user/developer guides, or research notes -> code). Routing table below.
---

rule R3 (produce code/docs via helper scripts): when a task generates or drafts (a) code from pseudo-code, (b) README/user/developer guides, or (c) code from research notes, prefer running the helper scripts in `{{CODE_ASSISTANT_ROOT}}/scripts` from the terminal over hand-writing the output.

Trigger: the task's deliverable is generated code or documentation (cases a, b, c above), as opposed to understanding existing code (R1) or reasoning about it (R2).
Order: understanding (R1/R2) happens before production (R3).

Action (SHOULD): run the helper script that fits the task; use the routing table below.
Fallback (MUST): if no script fits, or the chosen script is missing/fails or returns unusable output, say so and proceed normally (hand-write); never silently skip.

Script routing:
- Pseudo-code (starterfile) → code: `run_pipeline.sh <project_root> --data-dir data` (requires `# STATUS: APPROVED`), or `run_starter.sh` for interactive generation.
- Research notes → patch plan → applied code: `longtext2pseudo <notes> -o patch.pseudo` to convert, then apply via the Python API `code_analyzer.apply_patch_file(...)` (dry_run first). `run_analyzer.sh` is currently a placeholder launcher (info/docs/status only).
- README / user & developer guides: use `longtext2pseudo` plus the repo documentation flow (`assistant-repo-documenter`, see `user_manual.md`); note there is no dedicated docs launcher under `scripts/`.
- Structural review / refactoring: `run_refractor.sh` (dry-run supported); the `code_refractor` Python API for programmatic use.
- Environment & dependencies: `setup.sh`, `install_deps.sh`. Database creation: `create_sqlite_db.sh`.
- Interactive entry point / environment bootstrap: `run_code_assistant.sh` — menu-driven launcher that creates/activates the venv, checks dependencies, and dispatches to code_starter, code_analyzer (in development), or code_refractor. Prefer the specific scripts above for automated or non-interactive use.

Safety: the R0 global invariants apply — never transmit secrets; send only the minimum source code and context a task requires.
