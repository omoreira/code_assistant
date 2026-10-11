# User interface

Place the Streamlit application and UI-specific assets in this directory. Keep
application logic in the packages under `src/` and call those packages from the
UI.

## Running

From the repository root, the launcher sets up the venv, installs
dependencies, and starts the app on port 8503:

```bash
bash scripts/codeassistant_ui.sh          # override the port with --port PORT
```

Or run Streamlit directly:

```bash
python -m pip install -r requirements.txt      # adds streamlit>=1.36
streamlit run ui/app.py
```

The app listens on **port 8503** (see `ui/.streamlit/config.toml`) so it does
not collide with an app already using the default 8501. Change it either in the
config file or on the command line:

```bash
streamlit run ui/app.py --server.port 8504
```

## Pages

- **Starter** -- build a `starterfile.pseudo` one section at a time
  (`# PATHS`/`# REPOMAP`, `# DATABASES`, `# PSEUDOCODE`). Each section has a
  **Verify** button; once it passes, a **Save** button merges it into the file.
  The **Review & Run** tab runs the `code_starter` pipeline as a background
  process and shows a per-stage report.
- **Editor** -- create/edit a pseudocode file and convert it to real code.
- **Converter** -- `pseudo2code` and `longtext2pseudo` tasks.
- **Patcher** -- a context-aware chat that reads project files and proposes
  `patch.pseudo` changes, validated with a dry run before you apply them.

## Layout

```text
ui/
  app.py               # entrypoint: page config, Ollama gate, sidebar nav
  core/                # UI helpers (paths, LLM access, verification, pipeline)
  views/               # one module per page (starter, editor, converter, patcher)
  workspace/           # default output for generated starterfiles (created on use)
  .streamlit/config.toml
  uidesign.pseudo      # design brief used to scaffold this app
  requirements.txt
```

All LLM-backed features require a reachable local Ollama server; the app
hard-blocks with a message when it is unavailable.
