# Hardened Ollama wrapper contract

Reusable contract for shell wrappers that call a local Ollama server from an
IDE coding agent. Delivers deterministic exit codes, a machine-checkable JSON
envelope, an explicit health check, and metadata-only logging, so a caller
(R1/R2 rules) can rely on success/failure without trusting free text.

Canonical location: `code_assistant/scripts/ollama/` (this repo). The copies in
`~/bin/ollama/` are symlinks to these files.

## Files
- `ollama_common.sh`      - shared library (sourced, not executed)
- `ask_local_analyzer.sh` - R1 code-analysis wrapper (default model qwen3:14b)
- `ask_local_reasoner.sh` - R2 deep-reasoning wrapper (default model deepseek-r1:14b)
- `ollama_stats.sh`       - summaries of the metadata log
- `setup_hybrid_continue.sh` - interactive Continue rule/configurator (see repo scripts/)

## Exit codes
| Code | Meaning            | Trigger                                              |
|-----:|--------------------|------------------------------------------------------|
| 0    | success            | response generated and validated non-empty           |
| 2    | usage error        | bad/unknown option, or empty question                |
| 3    | environment error  | curl/jq missing, or Ollama not reachable             |
| 4    | upstream error     | curl failed, non-2xx, or timeout                     |
| 5    | invalid response   | model returned empty/whitespace or non-JSON body     |

## Health check
Before generating, the wrapper probes `$OLLAMA_HOST/api/tags` with
`curl --max-time 5` and requires HTTP 200. On failure it exits 3 (emitting an
error envelope first when `--json` is set).

## JSON envelope
Printed to stdout when `--json` is passed (safe escaping via `jq --arg`):

```json
{
  "tool":       "ask_local_analyzer",
  "model":      "qwen3:14b",
  "question":   "<the focused question>",
  "answer":     "<model response, or empty on error>",
  "ok":         true,
  "exit":       0,
  "latency_ms": 1234,
  "ts":         "2026-01-01T00:00:00Z"
}
```

With no `--json`, only the plain answer text is printed. On error the process
exits with the matching code and writes a human-readable message to stderr.

## Config (env)
- `OLLAMA_HOST`     - server base URL (default `http://localhost:11434`)
- `MODEL`           - per-script default model; override with `--model`
- `OLLAMA_DATA_DIR` - dir for the default log (default `${XDG_STATE_HOME:-$HOME/.local/state}/ollama_wrappers`)
- `OLLAMA_LOG`      - metadata log path (default `$OLLAMA_DATA_DIR/calls.jsonl`)

## Usage
```bash
ask_local_analyzer.sh [--json] [--model M] "<question>"
some_command | ask_local_analyzer.sh [--json] [--model M]
ask_local_analyzer.sh --stats [ollama_stats.sh args]   # delegates to the viewer
```

## Verifiability / logging
Each wrapper calls `log_meta` from `ollama_common.sh`, which appends one
metadata-only JSON line to `$OLLAMA_LOG`:

```json
{"tool":"ask_local_analyzer","model":"qwen3:14b","ok":true,"exit":0,"latency_ms":1234,"ts":"..."}
```

It records metadata only -- never the question/answer body and never secrets --
and is best-effort (it never fails the call, and creates `OLLAMA_DATA_DIR` as
needed). Callers rely on the exit code and (with `--json`) the `ok` field.

## Stats viewer
`ollama_stats.sh` summarizes the metadata log (jq-only, no network; it never
reads question/answer bodies):

```bash
ollama_stats.sh [--log FILE] [--json] [--tool NAME] [--model NAME] [--since ISO]
                [--failures [N]] [--tail [N]]
```

- default: totals, ok/failed + success rate, latency min/mean/p50/p90/max (ms),
  counts by tool/model/exit, and the `ts` window.
- `--failures [N]`: list the last N failed calls, newest first (default 10).
- `--tail [N]`: list the last N calls, newest first (default 10).
- `--tool/--model` filter by exact match; `--since ISO` keeps `ts >= ISO`
  (lexical, ISO-8601 UTC). `--log` defaults to `$OLLAMA_LOG`.
- A missing/empty log prints `no data` and exits 0. `--json` emits the summary
  as a JSON object (with the resolved `log` path added) in summary mode.

Any wrapper can reach it via `--stats`, e.g. `ask_local_analyzer.sh --stats --failures`.

## Install
These wrappers live in `code_assistant/scripts/ollama/`. Either call them by
full path, or symlink them into a directory on `PATH` (e.g. `~/bin/ollama/`).
`setup_hybrid_continue.sh` writes Continue rule files into `~/.continue/rules/`.

## Model version pinning
For reproducibility, each call records the digest (exact build) of the model that
served it. After the health check the wrapper resolves the digest via
`GET /api/tags` (`ollama_model_digest`) and includes it as `model_digest` in both
the JSON envelope and the metadata log line (omitted when unknown). The stats
viewer prints a 12-char prefix in `--tail`/`--failures`. Map a digest back with
`ollama list` or `GET /api/tags`.
