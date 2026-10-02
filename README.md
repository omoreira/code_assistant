# Code Assistant

A comprehensive local coding assistant system with three integrated modules for code generation, debugging, and patching.

- **Author/Maintainer/Developer:** Olga Moreira
- **License:** MIT
- **Repository:** https://github.com/omoreira/code_assistant
- **Objective:** This app aims to provide a local, low-resource coding assistant. Users should create a starter file with a repomap and pseudocode for each script file.
- **Assistive Tools and LLMs:** This code was developed from author's pseudocode. VS Code Continue (LLM: Claude 3 Haiku) was used to auto-convert developer's pseudocode into Python-based modules in a similar process that this app will offer. For further information, see AI Assistance Disclosure below.
- **Status:** Manual-auditing of the generated base code (i.e., the human behind the machine is manually auditing each piece of code and documentation generated). Assistant testing phase. This base code is still in the initial phase of development; use with caution!
- **Last Updated by the Human behind the Machine:** 2026-10-01

## Overview

Code Assistant is a modular Python project for creating repository scaffolds,
turning research notes into patch plans, applying patches, and generating UI,
benchmark, and documentation artifacts. Development is ongoing; treat generated
code as a draft and review it before use.

### Modules

- **`code_starter`** builds a target repository from `starterfile.pseudo`.
  The creator defines a REPOMAP and source pseudocode. The renderer creates
  directories and spec files, then converts source pseudocode with Ollama.
- **`code_converter`** reads UTF-8 research notes and asks an LLM to produce
  `patch.pseudo` with `#PATCHES` and `#NEW SCRIPTS` sections.
- **`code_debugger`** parses and applies those patch entries. Conversion and
  patch application are separate operations.
- **`code_patcher`** is a retained development placeholder; patch application
  currently lives in `code_debugger`.
- **`code_refractor`** provides APIs for checking and carrying out structural
  changes such as moving modules and updating references. This area is still
  evolving.
- **`ui_builder`** creates `ui/uidesign.pseudo` and generates Streamlit or
  React + TypeScript UI files under the target repository's `ui/` folder.
- **`benchmarker`** creates `benchmark/benchmark.pseudo` and generates a
  Python benchmark harness under the target repository's `benchmark/` folder.
- **`repo_documenter`** scans Python packages under a target's `src/` and
  creates or updates documentation in its root `docs/` folder.
- **`shared`** contains cross-cutting services such as LLM access,
  configuration, logging, and utilities.

`tools/`, `db_master_handler/`, and `assistant_contracts/` are reserved support
packages with little or no implementation currently.

The root-level `ui/` and `benchmark/` folders described above are defaults for
generated repositories; the assistant itself keeps those tools under `src/`.

## Quick Start

### Requirements

- Python 3.8 or newer.
- pip and Python virtual environments.
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
`<project-root>/starterfile.pseudo`. New starterfiles include a
`# PROJECT_ROOT: .` marker, a root `benchmark/` directory, and a
`# SPECIFICATIONS` section for `benchmark/benchmark.pseudo` and
`ui/uidesign.pseudo`.

Render the starterfile from any working directory:

```bash
python -m code_starter.pseudocode_renderer \
  /path/to/new_assistant/starterfile.pseudo
```

Source generation uses the configured Ollama model. On successful completion,
the renderer removes the starterfile; keep a copy if you want to preserve the
specification. See [user_manual.md](user_manual.md) for the detailed workflow.

### Other common workflows

Convert research notes into a patch plan:

```bash
python -m code_converter.longtext_pseudo_converter research.md \
  --output patch.pseudo
```

Apply a patch plan through the API after reviewing it:

```python
from code_debugger import apply_patch_file

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

## Repository Layout

```text
code_assistant/
├── docs/                    # Unified project documentation
├── scripts/                 # Shell helpers and module launchers
├── src/
│   ├── code_starter/        # Project scaffolding and source generation
│   ├── code_converter/      # Research notes to patch pseudocode
│   ├── code_debugger/       # Patch parsing and application
│   ├── code_patcher/        # Development placeholder
│   ├── code_refractor/      # Structural refactoring tools
│   ├── ui_builder/          # Target-repository UI generation
│   ├── benchmarker/         # Target-repository benchmark generation
│   ├── repo_documenter/     # Target-repository documentation
│   ├── shared/              # Shared infrastructure
│   ├── tools/               # Reserved support package
│   ├── db_master_handler/   # Reserved support package
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
