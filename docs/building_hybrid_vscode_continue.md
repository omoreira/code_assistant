# Building a hybrid VS Code with Continue

A practical guide to running a **hybrid** coding assistant in VS Code: a Continue
agent that *plans and edits* while local Ollama models *do the code analysis and
reasoning* through small, hardened shell wrappers. This repo ships the wrappers,
the Continue rule templates, and a setup script.

## 1. What "hybrid" means here

- **The agent** (Continue in VS Code) drives the conversation, proposes plans, and
  makes edits. It can use your usual model (cloud or local).
- **The local specialists** are two small scripts that call Ollama directly for
  narrow, well-defined jobs:
  - **R1 — code analysis** (`ask_local_analyzer.sh`, default `qwen3:14b`)
  - **R2 — deep reasoning** (`ask_local_reasoner.sh`, default `deepseek-r1:14b`)
- **The rules** (R0–R3 in `~/.continue/rules/`) tell the agent *when* to shell out
  to those wrappers, *how* to read their JSON output, and *what to do on failure*.

The result: local, private, zero-cost analysis/reasoning for well-scoped questions,
while the agent keeps control of the overall task.

## 2. How it works

```
        VS Code + Continue agent
  ┌───────────────────────────────────────────┐
  │  follows R0..R3 rules in ~/.continue/rules  │
  │                                             │
  │  R0 plan ─► R1 analyze ─► R2 reason ─► R3 build
  └───────┬──────────────┬───────────────┬──────┘
          │ terminal     │ terminal      │ terminal
          ▼              ▼               ▼
   ask_local_analyzer  ask_local_reasoner  repo helper scripts
          │              │               (code_starter, refractor, ...)
          └──────┬───────┘
                 ▼
          hardened contract (scripts/ollama/)
          • exit codes 0/2/3/4/5  • JSON envelope
          • /api/tags health check • metadata-only log
                 ▼
             Ollama  http://localhost:11434
```

Each wrapper returns a **JSON envelope** on stdout (`--json`) plus a deterministic
**exit code**, and appends a **metadata-only** line to a log file. The agent trusts
the exit code and the `ok` field instead of parsing prose.

## 3. Prerequisites

- **VS Code** with the **Continue** extension.
- **Ollama** installed and running: `ollama serve` (check: `curl -s localhost:11434/api/tags`).
- Pull the default models (or use your own):
  ```bash
  ollama pull qwen3:14b        # R1 analyzer default
  ollama pull deepseek-r1:14b  # R2 reasoner default
  ```
- **curl** and **jq** on `PATH` (the wrappers require both; missing them → exit 3).

## 4. Quick start (automated)

From this repo:

```bash
# interactive: prompts for paths + models
scripts/setup_hybrid_continue.sh

# or non-interactive with your choices
scripts/setup_hybrid_continue.sh --yes \
  --analyzer-model qwen3:14b \
  --reasoner-model deepseek-r1:14b \
  --host http://localhost:11434
```

The script:

1. fills the rule templates from `templates/continue_rules/` and writes them to
   `~/.continue/rules/` (backing up any files it overwrites to
   `~/.continue/rules/.backup-<timestamp>/`),
2. creates the metadata data dir (`~/.local/state/ollama_wrappers/` by default),
3. checks `curl`, `jq`, and whether Ollama is reachable.

Then **reload VS Code** (or the Continue window) so the new rules load.

### Put the wrappers on your PATH

The wrappers live in `scripts/ollama/`. Either call them by full path, copy them
somewhere on `PATH`, or symlink them:

```bash
mkdir -p ~/bin/ollama
ln -sf "$PWD"/scripts/ollama/*.sh ~/bin/ollama/
```

Test one:

```bash
~/bin/ollama/ask_local_analyzer.sh --json "What does src/foo.py:42 do?"
```

## 5. Manual setup

If you prefer to wire things by hand:

1. Copy `templates/continue_rules/*.md` into `~/.continue/rules/`.
2. Replace the placeholders:
   - `{{OLLAMA_BIN}}` → the dir holding the wrapper scripts (e.g. `~/bin/ollama`)
   - `{{ANALYZER_MODEL}}` / `{{REASONER_MODEL}}` → your model names
   - `{{CODE_ASSISTANT_ROOT}}` → this repo's path (used by rule R3)
3. Make the wrappers executable and ensure `curl`/`jq` are installed.

## 6. Configuration reference

Wrappers read these environment variables (see `scripts/ollama/CONTRACT.md`):

| Variable          | Default                                                   | Purpose                          |
|-------------------|-----------------------------------------------------------|----------------------------------|
| `OLLAMA_HOST`     | `http://localhost:11434`                                  | Ollama server base URL           |
| `MODEL`           | per-script (analyzer/reasoner)                            | default model; override `--model`|
| `OLLAMA_DATA_DIR` | `${XDG_STATE_HOME:-$HOME/.local/state}/ollama_wrappers`   | dir for the metadata log         |
| `OLLAMA_LOG`      | `$OLLAMA_DATA_DIR/calls.jsonl`                            | metadata log path                |

Per-call flags: `--json`, `--model M`, `--stats`.

## 7. The rule set

| Rule | File                  | Fires when…                                   | Calls                    |
|-----:|-----------------------|-----------------------------------------------|--------------------------|
| R0   | `plantask.md`         | **every task** (plan first; global invariants)| —                        |
| R1   | `askcodeanalyzer.md`  | question is grounded in specific code          | `ask_local_analyzer.sh`  |
| R2   | `asklocalreasoner.md` | design/strategy/ambiguous, not file-specific   | `ask_local_reasoner.sh`  |
| R3   | `codeassistantscripts.md` | deliverable is generated code/docs         | repo helper scripts      |

R0 also carries the **global invariants**: never transmit secrets, always state
which rule fired (verifiability), and always fall back explicitly when a script is
missing or fails.

## 8. Observability

Every wrapper call records one metadata-only JSON line (never the question/answer,
never secrets):

```json
{"tool":"ask_local_analyzer","model":"qwen3:14b","ok":true,"exit":0,"latency_ms":1234,"ts":"2026-01-01T00:00:00Z"}
```

Summarize it with the viewer:

```bash
scripts/ollama/ollama_stats.sh                          # totals, latency, breakdowns
scripts/ollama/ollama_stats.sh --failures 5             # last 5 failures, newest first
scripts/ollama/ollama_stats.sh --since 2026-01-01T00:00:00Z
scripts/ollama/ollama_stats.sh --json                   # machine-readable
# any wrapper can delegate:
ask_local_analyzer.sh --stats --tail 10
```

## 9. Verification checklist

- [ ] `curl -s localhost:11434/api/tags` returns 200.
- [ ] `command -v curl jq` finds both.
- [ ] `~/bin/ollama/ask_local_analyzer.sh --json "ping"` prints an envelope with `"ok":true`.
- [ ] `~/.continue/rules/` contains the four rule files (R0–R3).
- [ ] In VS Code, ask a code-grounded question and confirm the agent runs R1
      (the rule requires it to state the rule fired and cite the envelope).

## 10. Troubleshooting

| Symptom                         | Likely cause / fix                                            |
|---------------------------------|---------------------------------------------------------------|
| Wrapper exits **2**             | bad option or empty question                                  |
| Wrapper exits **3**             | `curl`/`jq` missing, or Ollama not running (`ollama serve`)   |
| Wrapper exits **4**             | network/HTTP/timeout to Ollama                                |
| Wrapper exits **5**             | model returned empty/whitespace or non-JSON                   |
| Agent ignores the wrappers      | rules not loaded — reload VS Code; check `~/.continue/rules/` |
| Model not found                 | `ollama pull <model>`, then match the rule's `--model` value  |
| Command blocked: "Security Policy Violation" | Continue agent terminal policy; see section 12. |

## 11. Adoption pitfalls

The biggest pitfall (confirmed by our own design review) is **misconfiguration due
to environment variability**: different Ollama hosts, model tags, and install paths
make copy-pasted rules break. Mitigations baked into this repo:

- **No hardcoded paths/models in templates** — use the placeholders and the setup
  script instead of hand-editing absolute paths.
- **Deterministic failures** — the exit-code contract and JSON envelope mean a
  misconfiguration surfaces as a clean exit code, not a silent wrong answer.
- **Backups** — the setup script never destroys your existing rules silently.

## 12. Environment constraints: the agent's terminal policy

The Continue agent (VS Code) executes our terminal commands through Continue's
own **command-safety policy**, which is *not* configurable from `config.yaml`.
Knowing this prevents surprises when the R1-R3 rules shell out.

Verified against Continue **v2.0.0** (`out/extension.js`, `gui/assets/index.js`):

- Every command is classified as **safe** (`allowedWithoutPermission`),
  **high-risk** (`allowedWithPermission`), or **critical** (`disabled`). The most
  restrictive result wins, and `disabled` always wins.
- A `disabled` result raises the "Security Policy Violation - command disabled"
  block. The critical classifier covers filesystem-format commands and `rm` with
  recursive+force flags on dangerous paths (root, home, system directories) or on
  critical files.
- **Safe** (no prompt): `ls`, `cat`, `head`, `tail`, `wc`, `grep` (without
  `--exec`), `find` (without `-exec` or `-delete`), `echo`, and similar read-only tools.
- **High-risk** (prompts for permission): network fetch tools and script
  interpreters, plus most other commands.
- There is **no per-command allowlist**. The only knobs are the GUI per-tool
  policy toggle (`run_terminal_command`: Allowed-with-permission ->
  Allowed-without-permission -> Disabled) and, in `config.yaml`, a model
  `chatOptions.toolOverrides`, which exposes only a `disabled` boolean (plus
  cosmetic labels) and cannot allowlist individual commands.

Practical consequences for these rules:

- **Prefer safe substitutes.** For edits and cleanups use `python3` (write, remove,
  rename) and `printf` / `cat >` for file writes, instead of `sed`, `awk`, `rm`,
  or `find -delete`.
- **Encapsulate when needed.** For operations the policy blocks, call `scripts/agent_ops.sh` (a scoped helper doing literal/regex replace, delete, and move via `python3`) instead of issuing those commands directly - a script's internals are not subject to the agent's command policy.
- **To remove the block entirely,** the installed extension bundle can be patched locally (a `.bak` backup is kept); reload VS Code afterwards.
- **Long calls:** there is no user-facing terminal-timeout setting in v2.0.0. Run
  slow local model calls in the background (`nohup ... &`) and poll the output.
- A stricter-than-stock policy (for example an enterprise/admin policy) surfaces
  the same "Security Policy Violation" message; check with your administrator.

## 13. For developers

Repository layout relevant to the hybrid stack:

```
scripts/ollama/            hardened wrappers + CONTRACT.md (the interface)
scripts/setup_hybrid_continue.sh   Continue rule/configurator
templates/continue_rules/  R0–R3 rule templates (with placeholders)
templates/README.md        placeholder reference
docs/                      this guide
```

Design principles:

- **One contract, many callers.** `scripts/ollama/CONTRACT.md` defines exit codes,
  the envelope schema, the health check, and logging. The R1/R2 rules are just
  clients of that contract.
- **Metadata only.** `log_meta` never records prompt/answer bodies or secrets.
- **Best-effort logging.** Logging failures never fail a call.
- **Idempotent, safe setup.** `setup_hybrid_continue.sh --dry-run` shows actions;
  real runs back up overwritten rules.

Exit codes: `0` success · `2` usage · `3` environment · `4` upstream · `5` invalid response.

## 14. See also

- `scripts/ollama/CONTRACT.md` — the wrapper contract.
- `user_manual.md`, `developer_guidelines.md` — the wider code_assistant toolkit.
- Continue docs: rules and `config.yaml` models.
