# code_converter

`code_converter` turns research notes into a `patch.pseudo` proposal. The
proposal uses `#PATCHES` for unified diffs against existing files and
`#NEW SCRIPTS` for complete new files.

## Research notes to pseudocode

```bash
./scripts/longtext2pseudo path/to/research-notes.md
```

The command writes `patch.pseudo` in the current directory. Use `-o` to choose
another output path. The local Ollama model and endpoint can be changed with
`--model` and `--endpoint`. For new repository plans, pass `--docker` to
request Docker files or `--no-docker` to explicitly omit them. Without either
flag, the converter follows the notes' Docker requirements.

## New repository architecture

When notes describe a new repository, the converter asks for a modular
`src/` layout following this project's design principles:

- Put each user-designed task in its own package under `src/`.
- Keep shared utilities and reusable tools in shared packages.
- Use common top-level `docs/`, `scripts/`, `config/`, and `src/` directories.
- Derive module names from the user's notes. Do not copy this assistant's
  module names or choose a fixed list.
- Include `setup.py` and `pyproject.toml` by default.
- Include `Dockerfile` and `.dockerignore` only when Docker support is requested.

The converter records unclear module names as open questions rather than
inventing project modules. Package `__init__.py` files in `#NEW SCRIPTS` ensure
the corresponding directories are created when the pseudocode is applied.

## Python API

```python
from code_converter import LongContextReader
from shared.llm import LLMInterface

reader = LongContextReader(LLMInterface())
reader.create_from_files(["notes.md"], "patch.pseudo")
```
