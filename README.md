# Code Assistant

A comprehensive local coding assistant system with modular tools for
scaffolding repositories, generating code, applying patches, and producing
documentation.

- **Author/Maintainer/Developer:** Olga Moreira
- **License:** MIT
- **Repository:** https://github.com/omoreira/code_assistant
- **Objective:** This app aims to provide a local, low-resource coding assistant. Users should create a starter file with a repomap and pseudocode for each script file.
- **Assistive Tools and LLMs:** This code was developed from author's pseudocode. VS Code Continue (LLM: Claude 3 Haiku) was used to auto-convert developer's pseudocode into Python-based modules in a similar process that this app will offer. For further information, see AI Assistance Disclosure below.
- **Status:** Manual-auditing of the generated base code (i.e., the human behind the machine is manually auditing each piece of code and documentation generated). Assistant testing phase. This base code is still in the initial phase of development; use with caution!
- **Last Updated by the Human behind the Machine:** 2026-10-10
- **Warning:** This code is still in the initial phase of development. Use with caution! The human behind the machine is manually auditing each piece of code and documentation generated. The assistant is still in the testing phase. Some scrips may not work as expected. 

## Overview

Code Assistant is a modular Python project for creating repository scaffolds,
turning research notes into patch plans, applying patches, and generating UI,
benchmark, and documentation artifacts. Development is ongoing; treat generated
code as a draft and review it before use.

### Project context and roadmap

Code Assistant is designed as an external module within the larger **Sam AI**
project. Sam AI is currently in private development; its **first open-source
release is planned before the end of the year**. A planned integration is Sam's
**DPO (Direct Preference Optimization)** strategy, which will let local models
learn individual users' patterns and retrieve a coding best-practices database
to ground their suggestions. These capabilities are on the roadmap and are not
part of the current release.

### Modules

- **`code_starter`** builds a target repository from an approved
  `starterfile.pseudo`. The creator defines a `# PATHS` section (project root
  and data directory), a REPOMAP, optional `# DATABASES`, and source
  pseudocode. The `pipeline` runs a preflight check, then creates
  directories and spec files, builds SQLite databases, converts source
  pseudocode with Ollama, analyzes the result, and documents the repository.
- **`code_converter`** reads UTF-8 research notes and asks an LLM to produce
  `patch.pseudo` with `#PATCHES` and `#NEW SCRIPTS` sections, and converts a
  single code-devoided file into real code for its extension. It can also
  produce a JSON assistant contract from a text/Markdown requirements file and
  output examples in a directory.
- **`code_analyzer`** parses and applies those patch entries, and provides the
  pre-generation `pseudocode_analyzer` that checks a starterfile's sections,
  approval marker, and path structure before any code is written. Conversion
  and patch application are separate operations.
- **`code_refractor`** provides APIs for checking and carrying out structural
  changes such as moving modules and updating references. This area is still
  evolving.
- **`ui_builder`** creates `ui/uidesign.pseudo` and generates Streamlit or
  React + TypeScript UI files under the target repository's `ui/` folder.
- **`benchmarker`** creates `benchmark/benchmark.pseudo` and generates a
  Python benchmark harness under the target repository's `benchmark/` folder.
- **`repo_documenter`** scans Python packages under a target's `src/` and
  creates or updates documentation in its root `docs/` folder.
- **`data_handler`** creates SQLite database files from the `.sql` schemas
  generated under `src/data_handler/sqlite_schema/`.
- **`shared`** contains cross-cutting services such as LLM access,
  configuration, logging, and utilities.

`tools/` and `assistant_contracts/` are reserved support packages with little
or no implementation currently. 

The root-level `ui/` and `benchmark/` folders described above are defaults for
generated repositories; the assistant itself keeps those tools under `src/`.
The assistant's own Streamlit interface also lives in the top-level [`ui/`](ui/)
folder and is launched with `scripts/codeassistant_ui.sh`.

## Hybrid VS Code + Continue

This repo also ships a **hybrid** Continue (VS Code) setup: the agent plans and
edits, while local Ollama wrappers under `scripts/ollama/` handle code analysis
(R1) and deep reasoning (R2) behind a small, hardened contract (deterministic
exit codes, a JSON envelope, and metadata-only logging). Rule templates live in
`templates/continue_rules/`; `scripts/setup_hybrid_continue.sh` writes them into
`~/.continue/rules/`.

See [Building a hybrid VS Code with Continue](docs/building_hybrid_vscode_continue.md)
and [`scripts/ollama/CONTRACT.md`](scripts/ollama/CONTRACT.md).

## Configure your LLM (local or API)

The provider and model are resolved centrally by `shared.llm_config`, with a
three-level precedence (lowest to highest):

1. `config/defaults.yaml` — the committed defaults.
2. Environment variables — copy [`config/.env.example`](config/.env.example) to
   `.env` (git-ignored) or export them in your shell.
3. CLI flags / explicit overrides (for example `--model`).

Three roles are resolved: `analysis` (R1 code analysis, default `qwen3:14b`),
`reasoning` (R2 deep reasoning, default `deepseek-r1:14b`), and `generation`
(code generation, default `deepseek-coder:6.7b`).

Use a different **local Ollama** model by setting `LLM_ANALYSIS_MODEL`,
`LLM_REASONING_MODEL`, or `LLM_GENERATION_MODEL`, or by editing
`config/defaults.yaml`.

Use an **API provider** by setting a provider and its key, for example:

```bash
export LLM_PROVIDER=openai
export LLM_MODEL=gpt-4o
export OPENAI_API_KEY=sk-...   # read from the environment only; never stored
```

Supported providers: `ollama`, `openai`, `anthropic`, `huggingface`. Secrets are
read from the environment **only** — never from `defaults.yaml`, never written to
disk, never shown in logs. Mix providers per role with e.g.
`LLM_REASONING_PROVIDER=openai` while leaving `LLM_GENERATION_PROVIDER=ollama`.

The Continue wrappers under `scripts/ollama/` speak the **Ollama API only**; an
API provider applies to the Python pipeline and to the Continue agent model,
which `scripts/setup_hybrid_continue.sh --write-config` renders from the same
resolved roles.

## Quick Start

### Requirements

- Python 3.8 or newer.
- pip and Python virtual environments.
- The `sqlite3` command-line tool, used to build databases from `# DATABASES`.
- Ollama and the `deepseek-coder:6.7b` model for commands that use local LLM
  generation. UI and benchmark scaffolds can also be generated without an LLM.

### Install

```bash
git clone https://github.com/omoreira/code_assistant.git
cd code_assistant
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
python -m pip install -e ".[dev]"
```

For Ollama-backed features, start the local service and pull the configured
model:

```bash
ollama pull deepseek-coder:6.7b
ollama serve
```

### Create a repository

Launch the interactive starter:

```bash
code-assistant
```

Choose a target project root, enter the user-designed module names for its
`src/` tree, and add source-file pseudocode. Save to create
`<project-root>/starterfile.pseudo`. New starterfiles include a `# PATHS`
section (`root: .` and `data_dir`), a root `benchmark/` directory, and a
`# SPECIFICATIONS` section for `benchmark/benchmark.pseudo` and
`ui/uidesign.pseudo`. The `# PATHS` `data_dir` (like `--data-dir` or
`CODE_ASSISTANT_DATA_DIR`) is created during generation; the implicit default
`data/` is not created automatically. Per-file `ENV_VARS` declarations produce a
`.env.example` at the project root (never overwriting an existing file).

Generation only runs for an approved starterfile (one carrying a
`# STATUS: APPROVED` marker). Run the full pipeline from the repository root:

```bash
bash scripts/run_pipeline.sh /path/to/new_assistant --data-dir data
```

The pipeline runs a static preflight (required sections, approval marker,
`sqlite3` and Ollama availability, and a `code_analyzer` starterfile review),
then runs `code_starter` (skeleton, databases, source generation),
`code_analyzer`, and `repo_documenter`, and writes a smoke test to `tmp/`.
The project root comes from the positional argument; when omitted (direct
`python -m code_starter.pipeline`), the starterfile's `# PATHS` root is used,
falling back to the current directory.
Source generation uses the configured Ollama model. On success the starterfile
is moved to `tmp/` with a timestamp; on failure it is left in place. See
[user_manual.md](user_manual.md) for the detailed workflow.

The renderer can also be run on its own:

```bash
python -m code_starter.pseudocode_renderer \
  /path/to/new_assistant/starterfile.pseudo
```

### Other common workflows

Convert research notes into a patch plan:

```bash
python -m code_converter.longtext_pseudo_converter research.md \
  --output patch.pseudo
```

Convert a single code-devoided file into real code for its file extension:

```bash
python -m code_converter.pseudofile_converter path/to/module.py
```

Create a JSON assistant contract from requirements and output examples:

```bash
python -m code_converter.assistant_contract_builder requirements.md examples/ \
  --output assistant_contract.json
```

The equivalent repository launcher is `scripts/build_assistant_contract.sh`.
Contract generation defaults to Ollama `deepseek-r1:14b`; `--model` also accepts
`qwen3:14b` and `mistral:7b`.

The contract captures rules, obligations, output requirements inferred from
the examples, and unresolved questions. Requirements can be `.txt`, `.md`, or
`.markdown`; example files are read recursively as UTF-8 text.

Apply a patch plan through the API after reviewing it:

```python
from code_analyzer import apply_patch_file

apply_patch_file("patch.pseudo", project_root="/path/to/repository", dry_run=True)
```

Create a UI design spec, then generate a Streamlit interface:

```bash
assistant-ui-builder /path/to/repository --create-pseudo
assistant-ui-builder /path/to/repository --from-pseudo --framework streamlit
```

Create a benchmark spec and generate a harness:

```bash
assistant-benchmarker /path/to/repository --create-spec
assistant-benchmarker /path/to/repository --generate
```

Generate target-repository documentation:

```bash
assistant-repo-documenter /path/to/repository
```

For the full command reference, formats, and current limitations, see the
[user manual](user_manual.md). For architecture and contribution guidance, see
[developer guidelines](developer_guidelines.md).

### Launch the assistant web UI

The assistant ships a Streamlit UI for the Starter, Editor, Converter, and
Patcher workflows. Start it from the repository root:

```bash
bash scripts/codeassistant_ui.sh
```

The launcher creates/activates the project virtual environment, installs
dependencies, and runs `streamlit run ui/sam_code_app.py` (the port is assigned
by the local hub when it launches this app; standalone runs use 8501). Override
the port with `--port PORT`, or forward options to `streamlit run` after `--`.
The UI hard-blocks with a message unless a local Ollama server is reachable. See
[`ui/README.md`](ui/README.md) for the page-by-page breakdown.

## Repository Layout

```text
code_assistant/
├── docs/                    # Unified project documentation
├── scripts/                 # Shell helpers and module launchers
│   └── ollama/              # Hardened Ollama wrappers (hybrid Continue)
├── templates/               # Continue hybrid rule templates
├── ui/                      # Assistant Streamlit web UI (codeassistant_ui.sh)
├── src/
│   ├── code_starter/        # Project scaffolding and source generation
│   ├── code_converter/      # Research notes to patch pseudocode
│   ├── code_analyzer/       # Patch parsing and application
│   ├── code_refractor/      # Structural refactoring tools
│   ├── ui_builder/          # Target-repository UI generation
│   ├── benchmarker/         # Target-repository benchmark generation
│   ├── repo_documenter/     # Target-repository documentation
│   ├── shared/              # Shared infrastructure
│   ├── tools/               # Reserved support package
│   ├── data_handler/        # SQLite schema and database creation
│   └── assistant_contracts/ # Reserved support package
├── tests/                   # Automated tests
├── user_manual.md
├── developer_guidelines.md
├── setup.py
└── pyproject.toml
```

## Development

Run the test suite with:

```bash
python -m pytest
```

The Makefile also provides convenience targets (`make help` lists them).
Install the development extra to use formatting, linting, typing, and test
tools. Contribution practices and module boundaries are in
[developer_guidelines.md](developer_guidelines.md).

## License and Support

This project is licensed under the MIT License; see [LICENSE](LICENSE).
For issues and feature requests, use the
[GitHub issue tracker](https://github.com/omoreira/code_assistant/issues).

---

## AI Disclosure Assistance

The development of this project involved the use of AI tools, including VS Code Continue (Claude 3 Haiku) and GitHub Copilot in the same spirit as any modern development environment might use IDE code completion, search engines, or documentation assistants.

These tools were used for:

- Generating boilerplate code and debugging suggestions
- Refining documentation and organizing materials

Main reason being to accelerate development and reduce repetitive tasks, allowing the human developer to focus on higher-level design, architecture, and problem-solving. AI Copilots can generated code and documentation faster that I can type, but they do not replace the human developer's expertise, judgment, or creativity. The human developer (Olga Moreira) was responsible for reviewing, editing, and integrating all AI-generated content to ensure it met the project's standards and objectives.

In summary, all architectural decisions, design logic, modular framework, and core vision were conceived and guided by the human creator (Olga Moreira). This project reflects years of research into low-resource coding assistance, modular and decentralized design principles.

**This disclosure is offered in the interest of transparency and to acknowledge that while AI can support structured thinking and development, it does not replace human intent, authorship, or ethical responsibility.**


