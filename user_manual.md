# Code Assistant User Manual

Code Assistant is a modular Python toolkit for scaffolding repositories,
turning research notes into patch plans, applying those plans, generating UI
and benchmark code, and documenting or refactoring projects. Some modules are
still in development. Review generated output before using it in a real
project.

>**Project context.** Code Assistant is an external module of the larger
> **Sam AI** project. Sam AI is in private development, with its first
> open-source release planned before the end of the year. A future Sam AI
> integration adds a **DPO (Direct Preference Optimization)** strategy so local
> models can learn individual users' patterns and retrieve a coding
> best-practices database. This is roadmap material, not current functionality.

## 1. Install and configure

Requirements are Python 3.8 or newer and pip. From the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
python -m pip install -e .
```

Install the optional development tools with `python -m pip install -e ".[dev]"`.
LLM-backed commands use Ollama by default with model `deepseek-coder:6.7b` at
`http://localhost:11434`. Install and start Ollama and pull that model if you
want those features:

```bash
ollama pull deepseek-coder:6.7b
ollama serve
```

Commands that use Ollama generally accept `--model` and `--endpoint` options.
Several Python APIs also accept an LLM interface object, allowing another
compatible provider to be supplied by the caller.

### Configuring the LLM (local or API)

The provider and model for each role are resolved by `shared.llm_config` from
`config/defaults.yaml`, overridden by environment variables, then by CLI flags.
Copy `config/.env.example` to `.env` and set the variables you need (the example
lists variable *names* only and holds no secrets):

| Variable | Role | Default |
|---|---|---|
| `LLM_MODEL` | global default model | `deepseek-coder:6.7b` |
| `LLM_ANALYSIS_MODEL` | R1 code analysis | `qwen3:14b` |
| `LLM_REASONING_MODEL` | R2 deep reasoning | `deepseek-r1:14b` |
| `LLM_GENERATION_MODEL` | generation | `deepseek-coder:6.7b` |
| `LLM_PROVIDER`, `LLM_ANALYSIS_PROVIDER`, ... | provider | `ollama` |
| `LLM_API_ENDPOINT` | base URL | `http://localhost:11434` |
| `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `HUGGINGFACE_API_KEY` | API credentials | (none) |

Supported providers: `ollama`, `openai`, `anthropic`, `huggingface`. API keys are
read from the environment only and are never stored in the repository.

## 2. Create a repository from a starterfile

Run the interactive creator from the repository root:

```bash
python -m code_starter.starterfile_creator
```

In the menu:

1. Choose **Create standard project structure** and enter the target folder,
   such as `./new_assistant`.
2. Enter the user-designed Python modules to place under `src/`.
3. Add source-file pseudocode through the script and pseudocode menu options.
4. Preview and save. By default, `starterfile.pseudo` is saved directly in the
   selected project root.

The standard layout includes `docs/`, `scripts/`, `config/`, `ui/`,
`benchmark/`, `src/`, and shared support package folders. The starterfile uses
a `# PATHS` section with `root: .` and relative paths, so it can be rendered
from any working directory.

New starterfiles have these sections:

- `# PATHS` declares generation-time locations: `root` (relative to the
  starterfile, like the legacy `# PROJECT_ROOT: .` marker) and `data_dir` (the
  SQLite storage folder). The data directory is created only when it is
  declared here (or requested via `--data-dir`, the
  `CODE_ASSISTANT_DATA_DIR`/`DATA_DIR` environment variable, or
  `--interactive`).
- `# REPOMAP` describes the directory tree to seed. `NONE` infers the structure
  from the `# PSEUDOCODE` headers.
- `# DATABASES` describes SQLite databases and tables. `NONE` means the
  repository has no databases.
- `# PSEUDOCODE` describes source files to generate as code. `NONE` means the
  source code was already generated and generation is skipped. Each `## <path>`
  block may carry `INPUT`, `OUTPUT`, `TASK`, `CONDITIONS`, `PREFERENCES`, and
  `ENV_VARS` fields; `ENV_VARS` lists the environment variables (names and
  defaults only -- never secrets) that the generated code expects to read. When
  any `ENV_VARS` are declared, generation writes a `.env.example` at the project
  root (existing files are never overwritten).
- `# SPECIFICATIONS` describes editable pseudo files to place into the target
  repository, currently `benchmark/benchmark.pseudo` and `ui/uidesign.pseudo`.
- `# STATUS: APPROVED` must be present before the pipeline generates code.

Run the full pipeline (recommended) for an approved starterfile:

```bash
bash scripts/run_pipeline.sh /path/to/new_assistant --data-dir data
```

The pipeline runs four stages:

1. **Preflight** (static, no generation): checks for the approval marker, the
   required sections, `sqlite3` and Ollama availability, and runs
   `code_analyzer`'s `pseudocode_analyzer`. It writes
   `docs/pseudocode_report.md` and a tagged copy of the starterfile under
   `tmp/`. Blocking errors stop before any code is written.
2. **code_starter**: seeds REPOMAP directories, creates specification files,
   builds the SQLite schema files, creates `.db` files under the data directory,
   and converts `# PSEUDOCODE` entries with Ollama. The data directory itself is
   created only when its location was requested explicitly (see the `# PATHS`
   note above); otherwise `.db` creation reports a clear error and stops.
3. **code_analyzer**: analyzes the generated code.
4. **repo_documenter**: writes project documentation under `docs/`.

A smoke test (compile generated modules, verify each database) is written to
`<project-root>/tmp/`. The database folder is chosen by precedence: the
`--data-dir` option (highest) overrides the `CODE_ASSISTANT_DATA_DIR` (or
`DATA_DIR`) environment variable, which overrides the `# PATHS` `data_dir`
value, which overrides `paths.data_dir` in `config/defaults.yaml`; the built-in
fallback is `data`. The directory is created only when the location came from
one of the explicit sources (`--data-dir`, an environment variable, `# PATHS`,
or `--interactive`); the `config/defaults.yaml`/built-in default is never
created automatically. On overall success the starterfile is moved to `tmp/`
with a timestamp; on failure it is left in place.

The renderer alone can also be run:

```bash
python -m code_starter.pseudocode_renderer /path/to/new_assistant/starterfile.pseudo
```

An optional `--project-root /path/to/new_assistant` overrides its declared
root. The project root is chosen by precedence: an explicit `project_root`
argument (the pipeline's first positional argument or `--project-root`) wins,
otherwise the starterfile's `# PATHS` `root` is used (relative to the
starterfile), otherwise the current working directory. `python -m
code_starter.pipeline` therefore treats `project_root` as optional. Existing
specification files are preserved, and existing source files must be empty to
pass the renderer’s initial check.

New starterfiles declare their root in `# PATHS` (`root: .`). Legacy starterfiles
that use the older `# PROJECT_ROOT:` marker are still recognised, and files with
neither marker retain current-working-directory semantics. The standalone
`blueprint_renderer` only creates directories; it does not generate source code
or specification file contents.

### Optional generated-repository helpers

- `ScriptsWriter` generates setup and run shell helpers.
- `CodeDocumenter` writes starter documentation templates.
- `GitHubRepoPlanner` interactively creates repository packaging files,
  including `setup.py` and `pyproject.toml`; Docker files are optional.
- `sql_schema_creator` reads a `# DATABASES` section and creates SQL schema
  files under `src/data_handler/sqlite_schema/`; `data_handler` then builds the
  `.db` files from those schemas.

These helpers can be imported from `code_starter`; their interactive workflows
and generated files should be reviewed before use.

## 3. Turn research notes into a patch plan

The `code_converter` module reads UTF-8 text or Markdown notes, summarizes
large inputs in chunks, and asks an LLM to write `patch.pseudo`:

```bash
python -m code_converter.longtext_pseudo_converter research.md \
  --output patch.pseudo
```

Use `--docker` or `--no-docker` to express the Docker preference when the
notes describe creating a new repository. The format has two sections:

```text
#PATCHES
## src/package/existing.py
--- a/src/package/existing.py
+++ b/src/package/existing.py
@@ -1,2 +1,2 @@
-old line
+new line

#NEW SCRIPTS
## src/package/new_file.py
complete contents of the new file
```

Patch entries contain unified diff hunks. New-script entries contain complete
file contents. Paths are relative to the target repository root.

## 4. Apply a patch plan

Patch application belongs to `code_analyzer`. The public API validates paths,
applies strict unified-diff context matching, and refuses to overwrite a file
listed under `#NEW SCRIPTS`:

```python
from code_analyzer import apply_patch_file

changed = apply_patch_file(
    "patch.pseudo",
    project_root="/path/to/repository",
    dry_run=True,  # validate and report without writing
)
print(changed)

# After reviewing the dry-run result:
changed = apply_patch_file(
    "patch.pseudo",
    project_root="/path/to/repository",
)
```

All entries are prepared and validated before any are written. Keep a version
control checkpoint and inspect the patch first; successful application writes
the changed files.

`code_analyzer` currently provides the patch parser and applier. Broader code
analysis and debugging assistance described as future functionality is not
implemented as a complete user workflow yet.

## 5. Build a UI from its design pseudocode

`ui_builder` writes into the target repository’s root `ui/` folder. Create the
default design brief:

```bash
assistant-ui-builder /path/to/repository --create-pseudo
```

Edit `ui/uidesign.pseudo`, then generate a Streamlit app:

```bash
assistant-ui-builder /path/to/repository \
  --from-pseudo --framework streamlit
```

For React + TypeScript, use `--framework react-typescript`. Add `--use-llm` to
ask the local LLM for the main app component. Without it, the builder creates
a usable starter template based on the design text. Existing generated files
are skipped unless `--overwrite` is provided.

You can also provide a description directly with `--description "..."`, or
use the `UIBuilder` Python API (`create_pseudocode`, `build_from_pseudocode`,
and `build`).

## 6. Generate a benchmark harness

Create or preserve the default `benchmark/benchmark.pseudo`:

```bash
assistant-benchmarker /path/to/repository --create-spec
```

Edit the specification, then generate `benchmark/benchmark.py`:

```bash
assistant-benchmarker /path/to/repository --generate
```

Without `--use-llm`, the generator produces a generic command-timing harness.
Run a command through that harness like this:

```bash
python /path/to/repository/benchmark/benchmark.py \
  --warmups 1 --iterations 5 -- python -m your_application
```

With `--use-llm`, the benchmark code is generated from the specification. The
result is code; inspect it and choose benchmark commands and input data
carefully before execution.

## 7. Generate repository documentation

`repo_documenter` scans Python packages beneath the target’s `src/` and writes
an index, architecture overview, API inventory, and package pages into
`docs/`:

```bash
assistant-repo-documenter /path/to/repository
```

Existing documentation is preserved by default. Pass `--update` to refresh
existing generated pages. `--use-llm` allows the LLM to update existing pages
using current source inventory facts; new pages are generated from static
inspection.

## 8. Refactor a project

`code_refractor` exposes `RefactoringVerifier`, `CodeRefactorer`,
`PathResolver`, and `DependencyMapper` as Python APIs. A typical operation
starts with a dry run:

```python
from code_refractor import CodeRefactorer

refactorer = CodeRefactorer("/path/to/repository", dry_run=True)
preview = refactorer.refactor_with_verification(
    "src/old_package", "src/new_package", element_type="module"
)
print(preview)
```

Review verification issues and the preview before repeating with
`dry_run=False`. Refactoring behavior is still being developed; it should be
reviewed carefully and backed by version control.

## 9. Module boundaries and support packages

The project keeps separate tasks in separate `src/` packages:

- `code_starter`: repository scaffolding, database and source generation, and
  the end-to-end `pipeline`.
- `code_converter`: research notes to patch pseudocode.
- `code_analyzer`: patch parsing and application, plus pre-generation
  starterfile analysis (`pseudocode_analyzer`).
- `code_refractor`: structural moves and reference updates.
- `ui_builder`: UI specifications and UI generation.
- `benchmarker`: benchmark specifications and benchmark code.
- `repo_documenter`: target-repository documentation.
- `data_handler`: SQLite schema and database creation.
- `shared`: cross-cutting services such as configuration, logging, and LLM
  access.

`tools/` and `assistant_contracts/` are reserved support packages and
currently have no substantial implementation.

## 10. Hybrid VS Code + Continue

Beyond the Python toolkit, this repo provides a hybrid Continue (VS Code) setup:
local Ollama wrappers for code analysis (R1) and deep reasoning (R2), driven by
Continue rules (R0-R3). The wrappers live in `scripts/ollama/`
(see `scripts/ollama/CONTRACT.md`), rule templates in `templates/continue_rules/`,
and `scripts/setup_hybrid_continue.sh` installs the rules into `~/.continue/rules/`.

Full guide: [Building a hybrid VS Code with Continue](docs/building_hybrid_vscode_continue.md).

## Troubleshooting

- **Ollama connection or model errors:** ensure `ollama serve` is running, the
  requested model is pulled, and the endpoint is correct.
- **Module import errors from a source checkout:** install the project with
  `pip install -e .`, or set `PYTHONPATH=src` for the current command.
- **Patch context mismatch:** re-check the target file and regenerate the diff
  against the exact version you intend to modify.
- **New-file conflict:** `#NEW SCRIPTS` entries never overwrite an existing
  path. Choose another path or resolve the conflict manually.
- **Starterfile path issues:** new-format paths are relative to the folder
  containing the starterfile; legacy files use the current working directory.
- **`sqlite3` not found:** install the `sqlite3` command-line tool. The
  pipeline preflight requires it to build databases from `# DATABASES`.
- **Data directory not created / `.db` creation fails:** the data directory is
  created only when requested explicitly. Declare `data_dir` in the `# PATHS`
  section, pass `--data-dir DIR`, set `CODE_ASSISTANT_DATA_DIR`/`DATA_DIR`, or
  run with `--interactive`; the implicit `config/defaults.yaml`/`data` default
  is not created automatically.
- **Generation blocked by preflight:** set `# STATUS: APPROVED`, then review
  and resolve the errors in `docs/pseudocode_report.md`; the tagged copy under
  `tmp/` marks the offending lines.
