# User interface

Place the Streamlit application and UI-specific assets in this directory. Keep
application logic in the packages under `src/` and call those packages from the
UI.

## Running

From the repository root, the launcher sets up the venv, installs
dependencies, and starts the app:

```bash
bash scripts/codeassistant_ui.sh          # override the port with --port PORT
```

Or run Streamlit directly:

```bash
python -m pip install -r requirements.txt      # adds streamlit>=1.36
streamlit run ui/sam_code_app.py
```

The port is not pinned in the repo: when launched by the **local hub**
(`local_hub/hub_launcher.py`) the hub passes an explicit free
`--server.port`. Standalone runs fall back to Streamlit's default 8501, which
you can override on the command line:

```bash
streamlit run ui/sam_code_app.py --server.port 8504
```

## Pages

- **Starter** -- build a `starterfile.pseudo` one section at a time
  (`# PATHS`/`# REPOMAP`, `# DATABASES`, `# PSEUDOCODE`). Each section has a
  **Verify** button; once it passes, a **Save** button merges it into the file.
  The **Review & Run** tab runs the `code_starter` pipeline as a background
  process and shows a per-stage report.
- **Editor** -- create/edit a pseudocode file and convert it to real code.
- **Converter** -- `pseudo2code`, `longtext2pseudo`, and JSON assistant
  contract generation from a text/Markdown requirements file and output samples.
- **Patcher** -- a context-aware chat that reads project files and proposes
  `patch.pseudo` changes, validated with a dry run before you apply them.

Path fields across these pages include an expandable local filesystem browser
with clickable breadcrumbs, folder navigation, and an in-folder filter. Click
an existing file to select it, select the current folder where appropriate, or
choose a new filename in the current folder. Paths can still be typed directly.

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
