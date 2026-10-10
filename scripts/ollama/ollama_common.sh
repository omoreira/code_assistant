#!/usr/bin/env bash
# ollama_common.sh - shared helpers for hardened Ollama wrapper scripts.
# Source this file; do not execute it directly. See CONTRACT.md.
#
# Exit-code contract:
#   0 = success | 2 = usage | 3 = environment | 4 = upstream | 5 = invalid response
#
# Config via env:
#   OLLAMA_HOST     (default: http://localhost:11434)
#   MODEL           (per-script default; override per call)
#   OLLAMA_DATA_DIR (default: ${XDG_STATE_HOME:-$HOME/.local/state}/ollama_wrappers)
#   OLLAMA_LOG      (default: $OLLAMA_DATA_DIR/calls.jsonl)

readonly EX_OK=0
readonly EX_USAGE=2
readonly EX_ENV=3
readonly EX_UPSTREAM=4
readonly EX_INVALID=5

OLLAMA_HOST="${OLLAMA_HOST:-http://localhost:11434}"
OLLAMA_DATA_DIR="${OLLAMA_DATA_DIR:-${XDG_STATE_HOME:-$HOME/.local/state}/ollama_wrappers}"
OLLAMA_LOG="${OLLAMA_LOG:-$OLLAMA_DATA_DIR/calls.jsonl}"

# now_epoch_ms -> print current epoch time in milliseconds
now_epoch_ms() {
  if date +%s%3N >/dev/null 2>&1; then
    date +%s%3N
  else
    echo $(( $(date +%s) * 1000 ))
  fi
}

# require_deps -> 0 if curl+jq present, else EX_ENV
require_deps() {
  local missing=()
  command -v curl >/dev/null 2>&1 || missing+=("curl")
  command -v jq   >/dev/null 2>&1 || missing+=("jq")
  if (( ${#missing[@]} )); then
    echo "Error: missing required command(s): ${missing[*]}" >&2
    return "$EX_ENV"
  fi
  return 0
}

# ollama_health -> 0 if server answers HTTP 200 on /api/tags, else 1
ollama_health() {
  local code
  code="$(curl -s -o /dev/null -w '%{http_code}' --max-time 5 \
    "${OLLAMA_HOST}/api/tags" 2>/dev/null)" || return 1
  [[ "$code" == "200" ]]
}

# ollama_model_digest MODEL -> print the model's content digest (version pin), or ""
#   The digest is the reproducible identity of the exact model build served.
ollama_model_digest() {
  local model="$1"
  curl -s --max-time 5 "${OLLAMA_HOST}/api/tags" 2>/dev/null \
    | jq -r --arg m "$model" '
        (.models // [])
        | map(select(.name == $m or .model == $m))
        | (.[0].digest // "")' 2>/dev/null || true
}

# ollama_generate MODEL PROMPT -> prints response to stdout
#   returns EX_UPSTREAM on transport/HTTP error, EX_INVALID on empty/invalid body
ollama_generate() {
  local model="$1" prompt="$2" raw response
  raw="$(
    jq -n --arg model "$model" --arg prompt "$prompt" \
      '{model: $model, prompt: $prompt, stream: false}' |
    curl --fail-with-body --silent --show-error \
      --connect-timeout 5 --max-time 600 \
      "${OLLAMA_HOST}/api/generate" \
      -H 'Content-Type: application/json' \
      --data-binary @-
  )" || return "$EX_UPSTREAM"

  response="$(printf '%s' "$raw" | jq -r '.response // empty' 2>/dev/null)" \
    || return "$EX_INVALID"
  [[ -n "${response//[[:space:]]/}" ]] || return "$EX_INVALID"
  printf '%s' "$response"
}

# emit_envelope TOOL MODEL QUESTION ANSWER OK EXIT_CODE LATENCY_MS [MODEL_DIGEST]
#   prints the JSON envelope; ts generated here; safe escaping via jq --arg
emit_envelope() {
  local tool="$1" model="$2" question="$3" answer="$4" ok="$5" ec="$6" lat="$7" digest="${8:-}"
  local ts
  ts="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  jq -n \
    --arg tool "$tool" \
    --arg model "$model" \
    --arg question "$question" \
    --arg answer "$answer" \
    --argjson ok "$ok" \
    --argjson exit_code "$ec" \
    --argjson latency_ms "$lat" \
    --arg ts "$ts" \
    --arg digest "$digest" \
    '{tool:$tool, model:$model, question:$question, answer:$answer,
      ok:$ok, exit:$exit_code, latency_ms:$latency_ms, ts:$ts}
     + (if $digest == "" then {} else {model_digest:$digest} end)'
}

# log_meta TOOL MODEL OK EXIT_CODE LATENCY_MS [MODEL_DIGEST]
#   appends one metadata-only JSON line (NO question/answer; never secrets).
#   best effort: never fails the calling script (creates OLLAMA_DATA_DIR as needed).
log_meta() {
  local tool="$1" model="$2" ok="$3" ec="$4" lat="$5" digest="${6:-}"
  mkdir -p -- "$(dirname -- "$OLLAMA_LOG")" 2>/dev/null || return 0
  jq -c -n \
    --arg tool "$tool" --arg model "$model" \
    --argjson ok "$ok" --argjson exit_code "$ec" --argjson latency_ms "$lat" \
    --arg ts "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
    --arg digest "$digest" \
    '{tool:$tool,model:$model,ok:$ok,exit:$exit_code,latency_ms:$latency_ms,ts:$ts}
     + (if $digest == "" then {} else {model_digest:$digest} end)' \
    >> "$OLLAMA_LOG" 2>/dev/null || return 0
  return 0
}
