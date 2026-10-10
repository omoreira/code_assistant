#!/usr/bin/env bash
set -euo pipefail
# ask_local_analyzer.sh - hardened Ollama wrapper. See CONTRACT.md.
# Usage: ask_local_analyzer.sh [--json] [--model M] "<question>"
#        ... | ask_local_analyzer.sh [--json] [--model M]
#        ask_local_analyzer.sh --stats [ollama_stats.sh args]

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=ollama_common.sh
source "$SCRIPT_DIR/ollama_common.sh"

TOOL="ask_local_analyzer"
MODEL="${MODEL:-qwen3:14b}"
EMIT_JSON=0

args=()
while (($#)); do
  case "$1" in
    --stats)  shift; exec "$SCRIPT_DIR/ollama_stats.sh" "$@" ;;
    --json)   EMIT_JSON=1; shift ;;
    --model)  MODEL="${2:?--model requires an argument}"; shift 2 ;;
    -h|--help) echo "Usage: $TOOL [--json] [--model M] \"<question>\" (or pipe input); $TOOL --stats [args]"; exit "$EX_OK" ;;
    --)       shift; args+=("$@"); break ;;
    -*)       echo "Error: unknown option: $1" >&2; exit "$EX_USAGE" ;;
    *)        args+=("$1"); shift ;;
  esac
done

question="${args[*]:-}"
if [[ ! -t 0 ]]; then
  piped="$(cat)"
  [[ -n "$piped" ]] && question+="${question:+$'\n\n'}$piped"
fi

if [[ -z "${question//[[:space:]]/}" ]]; then
  echo "Error: empty question. Usage: $TOOL [--json] \"<question>\" or pipe input." >&2
  exit "$EX_USAGE"
fi

require_deps || exit "$EX_ENV"

if ! ollama_health; then
  log_meta "$TOOL" "$MODEL" false "$EX_ENV" 0
  (( EMIT_JSON )) && emit_envelope "$TOOL" "$MODEL" "$question" "" false "$EX_ENV" 0
  echo "Error: Ollama not reachable at ${OLLAMA_HOST}" >&2
  exit "$EX_ENV"
fi

digest="$(ollama_model_digest "$MODEL")"
start="$(now_epoch_ms)"
answer="" ; rc=0
answer="$(ollama_generate "$MODEL" "$question")" || rc=$?
lat="$(( $(now_epoch_ms) - start ))"

if (( rc != 0 )); then
  log_meta "$TOOL" "$MODEL" false "$rc" "$lat" "$digest"
  (( EMIT_JSON )) && emit_envelope "$TOOL" "$MODEL" "$question" "$answer" false "$rc" "$lat" "$digest"
  echo "Error: generation failed (exit $rc)" >&2
  exit "$rc"
fi

log_meta "$TOOL" "$MODEL" true "$EX_OK" "$lat" "$digest"
if (( EMIT_JSON )); then
  emit_envelope "$TOOL" "$MODEL" "$question" "$answer" true "$EX_OK" "$lat" "$digest"
else
  printf '%s\n' "$answer"
fi
