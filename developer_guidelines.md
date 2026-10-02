# Developer Guidelines

This document describes the current architecture and conventions for
maintaining Code Assistant. The project is in an early development and
auditing phase; confirm behavior in source before relying on old notes or
examples.

## 1. Architectural principles

### Keep task responsibilities in modules

Each substantial task belongs in its own package under `src/`. The current
functional areas are:

| Package | Responsibility |
| --- | --- |
| `code_starter` | Define a starterfile, create a repository structure, and generate source files |
| `code_converter` | Convert long research notes into `patch.pseudo` |
| `code_debugger` | Parse/apply `#PATCHES` and create `#NEW SCRIPTS` entries |
| `code_refractor` | Verify and perform structural path/module changes |
| `ui_builder` | Create `ui/uidesign.pseudo` and generate a UI in a target repository |
| `benchmarker` | Create `benchmark/benchmark.pseudo` and generate a benchmark harness |
| `repo_documenter` | Inspect a target repository and write/update docs in its root `docs/` |
| `shared` | Cross-cutting configuration, logging, LLM, and utility services |

Avoid combining the converter and applier: conversion proposes a structured
plan, while the debugger applies it. Similarly, generated-repository modules
belong to the future project and should be derived from user-designed tasks;
do not copy this assistant’s own module names into every generated `src/`.

### Keep project context explicit

Operations on another repository should accept an explicit `project_root` or
`project_root`-like constructor argument. Resolve it once, anchor output paths
to it, and reject absolute or traversal paths when entries are expected to be
relative. The starterfile’s `# PROJECT_ROOT: .` means its own directory is the
root for new-format starterfiles. Legacy starterfiles retain their prior
working-directory behavior.

### Treat pseudo files according to their purpose

- `starterfile.pseudo` contains a REPOMAP, source-code `# PSEUDOCODE` entries,
  and optionally `# SPECIFICATIONS` artifacts.
- `patch.pseudo` contains `#PATCHES` unified diffs and `#NEW SCRIPTS` complete
  file contents.
- `ui/uidesign.pseudo` describes a UI to be generated inside the target
  repository’s `ui/` folder.
- `benchmark/benchmark.pseudo` describes a benchmark to be generated inside
  the target repository’s `benchmark/` folder.

Do not route user-authored specification artifacts through source-code
generation. Keep their parsing and output destinations explicit.

## 2. Source tree

```text
src/
├── code_starter/
├── code_converter/
├── code_debugger/
├── code_refractor/
├── ui_builder/
├── benchmarker/
├── repo_documenter/
├── shared/
├── tools/                 # Reserved support package
├── db_master_handler/     # Reserved support package
└── assistant_contracts/   # Reserved support package
```

The three support packages are intentionally sparse. Add code to them only
when the responsibility and shared interface are clear; do not use them as
miscellaneous catch-all folders.

## 3. Environment and package layout

The project supports Python 3.8 and newer. Packages live in `src/`; setuptools
package discovery is configured in `setup.py` and `pyproject.toml`.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

When adding a package, update `pyproject.toml` package discovery if it uses an
explicit include list. If it needs a user-facing command, add the entry point
to both `setup.py` and `pyproject.toml` so the two installation paths agree.
Keep runtime dependencies minimal and list them consistently in both package
metadata files.

## 4. Module implementation conventions

- Give each package a concise `__init__.py` that exports stable public symbols.
- Keep interactive CLI parsing in a `main(argv=None)` function where
  practical; keep reusable behavior in independently callable classes and
  functions.
- Accept explicit paths and resolve them with `pathlib.Path`.
- Validate input before writing. For project generators, ensure the resolved
  output remains inside the selected project root.
- Preserve user files by default. Make overwriting an explicit option.
- Return structured results for multi-file operations so callers can inspect
  created, updated, skipped, or failed paths.
- Report actionable errors and avoid silently treating partial work as
  success.
- Keep network/LLM setup at the integration boundary. Prefer injecting the
  project’s `shared.llm.LLMInterface` into reusable APIs rather than making
  module logic depend on an implicit global service.
- Keep module documentation aligned with the implementation. Check command
  arguments and public methods in source before documenting them.

### LLM output handling

Treat model output as untrusted input. Give prompts a precise output format,
remove only expected Markdown fences, parse or compile generated material
before writing when possible, and include enough source context for the user
to understand the result. Do not claim that model output is correct merely
because generation completed.

## 5. Current data flows

### Repository creation

`StarterfileCreator` creates a portable starter specification. The
`PseudocodeRenderer` reads REPOMAP directories, creates specification
artifacts, creates source paths from PSEUDOCODE headers, converts source
pseudocode, and removes the starterfile only after successful conversion.
The renderer preserves existing specification files and expects source files
to be empty before conversion.

### Research to patch

`LongContextReader` reads UTF-8 note files, chunks long text, summarizes the
chunks through an injected LLM interface, and asks for `#PATCHES` plus
`#NEW SCRIPTS`. `code_debugger.patch_file` validates paths and diffs before it
writes any entry. Patch application rejects path traversal and refuses to
overwrite files designated as new scripts.

### UI, benchmark, and documentation

- `UIBuilder` works only under `<project_root>/ui`; it preserves existing
  files by default. `build_from_pseudocode` reads `ui/uidesign.pseudo`.
- `BenchmarkGenerator` reads `benchmark/benchmark.pseudo`. Without an LLM it
  generates a generic command timing harness; with an LLM it requests a
  tailored Python program.
- `RepoDocumenter` scans Python packages below `src/` and writes to `docs/`.
  Existing pages are preserved unless update mode is selected.

### Structural refactoring

`CodeRefactorer` coordinates `RefactoringVerifier`, `PathResolver`, and
`DependencyMapper`. The `dry_run` option should be used to inspect proposed
changes before applying them. Structural refactoring is still under active
development and needs review against real projects.

## 6. Adding a module

1. Identify one task with a clear input, output, and ownership boundary.
2. Create `src/<module_name>/` and an `__init__.py` with the supported public
   API.
3. Implement reusable functions/classes separately from CLI interaction.
4. Add focused tests under `tests/` that cover ordinary, invalid, and path
   boundary cases.
5. Update packaging metadata if the package or its dependencies require it.
6. Document user-facing workflows in `user_manual.md`; document internal
   interfaces or architectural changes here.
7. Update generated-repository defaults only when the change belongs in every
   future repository. Keep this assistant’s internal module layout separate
   from the generated user-designed module list.

## 7. Testing and review

Run focused tests during development, then run the full suite before merging:

```bash
python -m pytest
```

Use `python -m py_compile` for a quick syntax check and `git diff --check` for
whitespace errors. For changes that write files, cover both dry-run behavior
and actual output in a temporary project root. Do not run generated benchmark
or application code as part of a documentation-only review.

Before accepting a change, review the diff for:

- Path writes outside the intended project root.
- Accidental overwrites or cleanup of user files.
- Mismatch between package entry points in `setup.py` and `pyproject.toml`.
- Documentation describing unavailable methods or CLI options.
- Coupling that crosses the established module boundaries.

## 8. Current implementation limits

- `code_debugger` currently implements patch parsing and application; it is
  not a complete automated debugging-analysis suite.
- `code_converter` proposes pseudocode and does not itself apply edits.
- `code_refractor` has verification and refactoring APIs, but should be treated
  as an evolving implementation and carefully reviewed.
- `tools/`, `db_master_handler/`, and `assistant_contracts/` are reserved,
  mostly empty support packages.
- LLM-backed generation depends on a working local Ollama service unless a
  caller injects another compatible interface.
