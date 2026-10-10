#!/usr/bin/env bash
set -euo pipefail
# setup_hybrid_continue.sh - install the Continue hybrid-agent rule files (and,
# optionally, a Continue config.yaml) generated from the shared LLM resolver.
#
# Model names default to what resolve_llm(...) returns for the analysis and
# reasoning roles (config/defaults.yaml < environment), so a fork can point the
# rules at its own models via config/defaults.yaml or LLM_ANALYSIS_MODEL /
# LLM_REASONING_MODEL. Explicit flags still win.
#
# See scripts/ollama/CONTRACT.md and docs/building_hybrid_vscode_continue.md.

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd -- "$SCRIPT_DIR/.." && pwd)"
TEMPLATES_DIR="$ROOT_DIR/templates/continue_rules"
OLLAMA_BIN_DEFAULT="$ROOT_DIR/scripts/ollama"

OLLAMA_BIN="$OLLAMA_BIN_DEFAULT"
RULES_DIR="${HOME}/.continue/rules"
OLLAMA_DATA_DIR="${XDG_STATE_HOME:-$HOME/.local/state}/ollama_wrappers"
CONTINUE_CONFIG="${HOME}/.continue/config.yaml"
CONFIG_FILE="$ROOT_DIR/config/defaults.yaml"

# Model/host start empty: an explicit flag wins, else the shared resolver, else
# the literal fallbacks below (kept in sync with config/defaults.yaml).
ANALYZER_MODEL=""
REASONER_MODEL=""
OLLAMA_HOST=""
ANALYZER_FALLBACK="qwen3:14b"
REASONER_FALLBACK="deepseek-r1:14b"
HOST_FALLBACK="http://localhost:11434"

ASSUME_YES=0
DRY_RUN=0
NO_RESOLVE=0
WRITE_CONFIG=0
PRINT_CONFIG=0

usage() {
  cat <<'USAGE'
Usage: setup_hybrid_continue.sh [options]
  --ollama-bin DIR     dir with the wrapper scripts (default: <repo>/scripts/ollama)
  --rules-dir DIR      Continue rules dir (default: ~/.continue/rules)
  --analyzer-model M   R1 analyzer model (default: from shared.llm_config)
  --reasoner-model M   R2 reasoner model (default: from shared.llm_config)
  --host URL           Ollama host URL (default: from shared.llm_config)
  --data-dir DIR       metadata log dir (default: ${XDG_STATE_HOME:-$HOME/.local/state}/ollama_wrappers)
  --config-file FILE   shared config to resolve from (default: <repo>/config/defaults.yaml)
  --continue-config F  Continue config path (default: ~/.continue/config.yaml)
  --print-config       print the generated Continue config.yaml to stdout
  --write-config       write the Continue config.yaml (backing up any existing)
  --no-resolve         skip shared.llm_config; use flags/literal defaults only
  -y, --yes            non-interactive (use defaults/flags, no prompts)
  -n, --dry-run        show what would be written, change nothing
  -h, --help           show this help
USAGE
}

while (($#)); do
  case "$1" in
    --ollama-bin)     OLLAMA_BIN="${2:?--ollama-bin needs a value}"; shift 2 ;;
    --rules-dir)      RULES_DIR="${2:?--rules-dir needs a value}"; shift 2 ;;
    --analyzer-model) ANALYZER_MODEL="${2:?}"; shift 2 ;;
    --reasoner-model) REASONER_MODEL="${2:?}"; shift 2 ;;
    --host)           OLLAMA_HOST="${2:?}"; shift 2 ;;
    --data-dir)       OLLAMA_DATA_DIR="${2:?}"; shift 2 ;;
    --config-file)    CONFIG_FILE="${2:?}"; shift 2 ;;
    --continue-config) CONTINUE_CONFIG="${2:?}"; shift 2 ;;
    --print-config)   PRINT_CONFIG=1; shift ;;
    --write-config)   WRITE_CONFIG=1; shift ;;
    --no-resolve)     NO_RESOLVE=1; shift ;;
    -y|--yes)         ASSUME_YES=1; shift ;;
    -n|--dry-run)     DRY_RUN=1; shift ;;
    -h|--help)        usage; exit 0 ;;
    *) echo "Error: unknown option: $1" >&2; usage >&2; exit 2 ;;
  esac
done

find_python() {
  local c
  for c in "$ROOT_DIR/venv/bin/python" "$ROOT_DIR/.venv/bin/python" python3 python; do
    if [[ "$c" == */* ]]; then [[ -x "$c" ]] && { printf '%s' "$c"; return 0; }
    else command -v "$c" >/dev/null 2>&1 && { printf '%s' "$c"; return 0; }; fi
  done
  return 1
}

py_resolve() {  # py_resolve ROLE FIELD [extra args...]
  local py
  py="$(find_python)" || return 1
  PYTHONPATH="$ROOT_DIR/src${PYTHONPATH:+:$PYTHONPATH}" "$py" \
    -m shared.llm_config --config-file "$CONFIG_FILE" \
    --role "$1" --field "$2" "${@:3}" 2>/dev/null
}

if (( ! NO_RESOLVE )); then
  [[ -n "$ANALYZER_MODEL" ]] || ANALYZER_MODEL="$(py_resolve analysis model || true)"
  [[ -n "$REASONER_MODEL" ]] || REASONER_MODEL="$(py_resolve reasoning model || true)"
  [[ -n "$OLLAMA_HOST"    ]] || OLLAMA_HOST="$(py_resolve analysis base_url --provider ollama || true)"
fi
ANALYZER_MODEL="${ANALYZER_MODEL:-$ANALYZER_FALLBACK}"
REASONER_MODEL="${REASONER_MODEL:-$REASONER_FALLBACK}"
OLLAMA_HOST="${OLLAMA_HOST:-$HOST_FALLBACK}"

if (( ! NO_RESOLVE )); then
  _ap="$(py_resolve analysis provider || true)"
  if [[ -n "$_ap" && "$_ap" != "ollama" ]]; then
    echo "Warning: analysis role resolves to provider '$_ap', but the R1/R2 wrappers speak the Ollama API only." >&2
  fi
fi

prompt() {  # prompt VARNAME "label" DEFAULT
  local __var="$1" __label="$2" __default="$3" __reply
  if (( ASSUME_YES )) || [[ ! -t 0 ]]; then printf -v "$__var" '%s' "$__default"; return; fi
  read -r -p "$__label [$__default]: " __reply || true
  printf -v "$__var" '%s' "${__reply:-$__default}"
}

if (( ! ASSUME_YES )); then
  prompt OLLAMA_BIN      "Ollama wrapper dir"   "$OLLAMA_BIN"
  prompt RULES_DIR       "Continue rules dir"   "$RULES_DIR"
  prompt ANALYZER_MODEL  "R1 analyzer model"    "$ANALYZER_MODEL"
  prompt REASONER_MODEL  "R2 reasoner model"    "$REASONER_MODEL"
  prompt OLLAMA_HOST     "Ollama host URL"      "$OLLAMA_HOST"
  prompt OLLAMA_DATA_DIR "Metadata data dir"    "$OLLAMA_DATA_DIR"
fi

[[ -d "$TEMPLATES_DIR" ]] || { echo "Error: templates dir not found: $TEMPLATES_DIR" >&2; exit 3; }
for w in ask_local_analyzer.sh ask_local_reasoner.sh ollama_common.sh ollama_stats.sh; do
  [[ -e "$OLLAMA_BIN/$w" ]] || echo "Warning: wrapper not found: $OLLAMA_BIN/$w" >&2
done

render() {  # render TEMPLATE DEST
  local src="$1" dest="$2" content
  content="$(cat -- "$src")"
  content="${content//'{{OLLAMA_BIN}}'/$OLLAMA_BIN}"
  content="${content//'{{ANALYZER_MODEL}}'/$ANALYZER_MODEL}"
  content="${content//'{{REASONER_MODEL}}'/$REASONER_MODEL}"
  content="${content//'{{CODE_ASSISTANT_ROOT}}'/$ROOT_DIR}"
  if (( DRY_RUN )); then
    printf '[dry-run] would write %s (%d bytes)\n' "$dest" "${#content}"
  else
    printf '%s\n' "$content" > "$dest"
    printf 'wrote %s\n' "$dest"
  fi
}

if (( DRY_RUN )); then
  for t in "$TEMPLATES_DIR"/*.md; do [[ -e "$t" ]] || continue; render "$t" "$RULES_DIR/$(basename -- "$t")"; done
else
  mkdir -p -- "$RULES_DIR" "$OLLAMA_DATA_DIR"
  # back up any rule files we are about to overwrite
  need_backup=0
  for t in "$TEMPLATES_DIR"/*.md; do [[ -e "$t" ]] || continue; [[ -e "$RULES_DIR/$(basename -- "$t")" ]] && need_backup=1; done
  if (( need_backup )); then
    BACKUP_DIR="$RULES_DIR/.backup-$(date -u +%Y%m%dT%H%M%SZ)"
    mkdir -p -- "$BACKUP_DIR"
    for t in "$TEMPLATES_DIR"/*.md; do
      b="$(basename -- "$t")"; [[ -e "$RULES_DIR/$b" ]] && cp -a -- "$RULES_DIR/$b" "$BACKUP_DIR/"
    done
    echo "backed up existing rules to $BACKUP_DIR"
  fi
  for t in "$TEMPLATES_DIR"/*.md; do [[ -e "$t" ]] || continue; render "$t" "$RULES_DIR/$(basename -- "$t")"; done
fi

# --- optional: Continue config.yaml (models), from the shared resolver --------
snippet=""
if (( WRITE_CONFIG || PRINT_CONFIG )); then
  if py="$(find_python)"; then
    snippet="$(PYTHONPATH="$ROOT_DIR/src${PYTHONPATH:+:$PYTHONPATH}" "$py" \
      -m shared.continue_config --config-file "$CONFIG_FILE" 2>/dev/null || true)"
  fi
  [[ -n "$snippet" ]] || echo "Warning: could not render Continue config (python + PyYAML required)." >&2
fi

if (( PRINT_CONFIG )) && [[ -n "$snippet" ]]; then
  echo
  echo "# ---- Continue config.yaml (models) ----"
  printf '%s\n' "$snippet"
fi

if (( WRITE_CONFIG )) && [[ -n "$snippet" ]]; then
  if (( DRY_RUN )); then
    printf '[dry-run] would write %s (%d bytes)\n' "$CONTINUE_CONFIG" "${#snippet}"
  else
    mkdir -p -- "$(dirname -- "$CONTINUE_CONFIG")"
    if [[ -e "$CONTINUE_CONFIG" ]]; then
      _bak="${CONTINUE_CONFIG}.bak-$(date -u +%Y%m%dT%H%M%SZ)"
      cp -a -- "$CONTINUE_CONFIG" "$_bak"
      echo "backed up existing Continue config to $_bak"
    fi
    printf '%s\n' "$snippet" > "$CONTINUE_CONFIG"
    echo "wrote $CONTINUE_CONFIG"
  fi
fi

echo
echo "Summary:"
echo "  wrappers : $OLLAMA_BIN"
echo "  rules    : $RULES_DIR"
echo "  models   : R1=$ANALYZER_MODEL  R2=$REASONER_MODEL  (host $OLLAMA_HOST)"
echo "  data dir : $OLLAMA_DATA_DIR"
if (( WRITE_CONFIG )); then echo "  config   : $CONTINUE_CONFIG (written)"
elif (( PRINT_CONFIG )); then echo "  config   : printed above"
else echo "  config   : not written (use --write-config)"; fi
echo
echo "Checks:"
command -v curl >/dev/null 2>&1 && echo "  curl     : ok" || echo "  curl     : MISSING (wrappers exit 3)"
command -v jq   >/dev/null 2>&1 && echo "  jq       : ok" || echo "  jq       : MISSING (wrappers exit 3)"
if command -v curl >/dev/null 2>&1; then
  code="$(curl -s -o /dev/null -w '%{http_code}' --max-time 5 "$OLLAMA_HOST/api/tags" 2>/dev/null || echo 000)"
  if [[ "$code" == "200" ]]; then echo "  ollama   : reachable ($OLLAMA_HOST)"; else echo "  ollama   : NOT reachable at $OLLAMA_HOST (run 'ollama serve')"; fi
fi
