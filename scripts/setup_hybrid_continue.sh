#!/usr/bin/env bash
set -euo pipefail
# setup_hybrid_continue.sh - write Continue hybrid-agent rule files from templates
# and prepare the local Ollama wrapper environment.
# See scripts/ollama/CONTRACT.md and docs/building_hybrid_vscode_continue.md.

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd -- "$SCRIPT_DIR/.." && pwd)"
TEMPLATES_DIR="$ROOT_DIR/templates/continue_rules"
OLLAMA_BIN_DEFAULT="$ROOT_DIR/scripts/ollama"

OLLAMA_BIN="$OLLAMA_BIN_DEFAULT"
RULES_DIR="${HOME}/.continue/rules"
ANALYZER_MODEL="qwen3:14b"
REASONER_MODEL="deepseek-r1:14b"
OLLAMA_HOST="http://localhost:11434"
OLLAMA_DATA_DIR="${XDG_STATE_HOME:-$HOME/.local/state}/ollama_wrappers"
ASSUME_YES=0
DRY_RUN=0

usage() {
  cat <<'USAGE'
Usage: setup_hybrid_continue.sh [options]
  --ollama-bin DIR     dir with the wrapper scripts (default: <repo>/scripts/ollama)
  --rules-dir DIR      Continue rules dir (default: ~/.continue/rules)
  --analyzer-model M   R1 analyzer model (default: qwen3:14b)
  --reasoner-model M   R2 reasoner model (default: deepseek-r1:14b)
  --host URL           Ollama host URL (default: http://localhost:11434)
  --data-dir DIR       metadata log dir (default: ${XDG_STATE_HOME:-$HOME/.local/state}/ollama_wrappers)
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
    -y|--yes)         ASSUME_YES=1; shift ;;
    -n|--dry-run)     DRY_RUN=1; shift ;;
    -h|--help)        usage; exit 0 ;;
    *) echo "Error: unknown option: $1" >&2; usage >&2; exit 2 ;;
  esac
done

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

echo
echo "Summary:"
echo "  wrappers : $OLLAMA_BIN"
echo "  rules    : $RULES_DIR"
echo "  models   : R1=$ANALYZER_MODEL  R2=$REASONER_MODEL"
echo "  host     : $OLLAMA_HOST"
echo "  data dir : $OLLAMA_DATA_DIR"
echo
echo "Checks:"
command -v curl >/dev/null 2>&1 && echo "  curl     : ok" || echo "  curl     : MISSING (wrappers exit 3)"
command -v jq   >/dev/null 2>&1 && echo "  jq       : ok" || echo "  jq       : MISSING (wrappers exit 3)"
if command -v curl >/dev/null 2>&1; then
  code="$(curl -s -o /dev/null -w '%{http_code}' --max-time 5 "$OLLAMA_HOST/api/tags" 2>/dev/null || echo 000)"
  if [[ "$code" == "200" ]]; then echo "  ollama   : reachable ($OLLAMA_HOST)"; else echo "  ollama   : NOT reachable at $OLLAMA_HOST (run 'ollama serve')"; fi
fi
