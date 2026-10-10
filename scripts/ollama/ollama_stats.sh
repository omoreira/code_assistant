#!/usr/bin/env bash
set -euo pipefail
# ollama_stats.sh - summarize the wrapper metadata log. See CONTRACT.md.
# Usage: ollama_stats.sh [--log FILE] [--json] [--tool NAME] [--model NAME]
#                        [--since ISO] [--failures [N]] [--tail [N]]

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=ollama_common.sh
source "$SCRIPT_DIR/ollama_common.sh"

LOG="$OLLAMA_LOG"
EMIT_JSON=0
F_TOOL=""
F_MODEL=""
F_SINCE=""
MODE="summary"
MODE_N=0

while (($#)); do
  case "$1" in
    --log)   LOG="${2:?--log requires an argument}"; shift 2 ;;
    --json)  EMIT_JSON=1; shift ;;
    --tool)  F_TOOL="${2:?--tool requires an argument}"; shift 2 ;;
    --model) F_MODEL="${2:?--model requires an argument}"; shift 2 ;;
    --since) F_SINCE="${2:?--since requires an argument}"; shift 2 ;;
    --failures) shift; MODE=failures; if [[ "${1:-}" =~ ^[0-9]+$ ]]; then MODE_N="$1"; shift; else MODE_N=10; fi ;;
    --tail)     shift; MODE=tail;     if [[ "${1:-}" =~ ^[0-9]+$ ]]; then MODE_N="$1"; shift; else MODE_N=10; fi ;;
    -h|--help)
      cat <<'USAGE'
Usage: ollama_stats.sh [--log FILE] [--json] [--tool NAME] [--model NAME]
                       [--since ISO] [--failures [N]] [--tail [N]]
  --log FILE      metadata log (default: $OLLAMA_LOG, i.e. $OLLAMA_DATA_DIR/calls.jsonl)
  --json          emit the summary as JSON (summary mode only)
  --tool NAME     only count entries for this tool
  --model NAME    only count entries for this model
  --since ISO     only count entries with ts >= ISO (lexical, ISO-8601 UTC)
  --failures [N]  list the last N failed calls, newest first (default 10)
  --tail [N]      list the last N calls, newest first (default 10)
USAGE
      exit "$EX_OK" ;;
    -*) echo "Error: unknown option: $1" >&2; exit "$EX_USAGE" ;;
    *)  echo "Error: unexpected argument: $1" >&2; exit "$EX_USAGE" ;;
  esac
done

command -v jq >/dev/null 2>&1 || { echo "Error: jq missing" >&2; exit "$EX_ENV"; }

if [[ ! -e "$LOG" ]]; then
  if (( EMIT_JSON )) && [[ "$MODE" == summary ]]; then
    jq -n --arg log "$LOG" '{log:$log,total:0,note:"no data (log not found)"}'
  else
    printf 'no data (log not found: %s)\n' "$LOG"
  fi
  exit "$EX_OK"
fi

if [[ "$MODE" == failures ]]; then
  out="$(jq -rs --arg tool "$F_TOOL" --arg model "$F_MODEL" --arg since "$F_SINCE" --argjson n "$MODE_N" '
    def passes: (.tool == $tool or $tool == "") and (.model == $model or $model == "") and ($since == "" or (.ts >= $since));
    [ .[] | select(passes) | select(.ok | not) ] | sort_by(.ts)
    | if length > $n then .[length-$n:] else . end | reverse
    | .[] | "\(.ts)  \(.tool)  \(.model)  exit=\(.exit)  latency_ms=\(.latency_ms)\(if .model_digest then "  digest=\(.model_digest[0:12])" else "" end)"
    ' "$LOG")"
  if [[ -z "$out" ]]; then echo "no failures in range"; else printf 'Recent failures (newest first):\n%s\n' "$out"; fi
  exit "$EX_OK"
fi

if [[ "$MODE" == tail ]]; then
  out="$(jq -rs --arg tool "$F_TOOL" --arg model "$F_MODEL" --arg since "$F_SINCE" --argjson n "$MODE_N" '
    def passes: (.tool == $tool or $tool == "") and (.model == $model or $model == "") and ($since == "" or (.ts >= $since));
    [ .[] | select(passes) ] | sort_by(.ts)
    | if length > $n then .[length-$n:] else . end | reverse
    | .[] | "\(.ts)  \(.tool)  \(.model)  ok=\(.ok)  exit=\(.exit)  latency_ms=\(.latency_ms)\(if .model_digest then "  digest=\(.model_digest[0:12])" else "" end)"
    ' "$LOG")"
  if [[ -z "$out" ]]; then echo "no calls in range"; else printf 'Recent calls (newest first):\n%s\n' "$out"; fi
  exit "$EX_OK"
fi

summary="$(
  jq -s --arg tool "$F_TOOL" --arg model "$F_MODEL" --arg since "$F_SINCE" '
    def passes: (.tool == $tool or $tool == "") and (.model == $model or $model == "") and ($since == "" or (.ts >= $since));
    def pick($a; $n; $p): if $n == 0 then 0 else $a[ ((($n - 1) * $p) | floor) ] end;
    [ .[] | select(passes) ] as $r
    | ($r | map(.latency_ms) | sort) as $lat
    | ($lat | length) as $n
    | ($r | map(select(.ok)) | length) as $ok
    | {
        total: $n,
        ok: $ok,
        failed: ($n - $ok),
        success_rate: (if $n == 0 then 0 else ($ok / $n) end),
        latency_ms: {
          min:  (if $n == 0 then 0 else $lat[0]  end),
          max:  (if $n == 0 then 0 else $lat[-1] end),
          mean: (if $n == 0 then 0 else (($lat | add) / $n) end),
          p50:  pick($lat; $n; 0.5),
          p90:  pick($lat; $n; 0.9)
        },
        by_tool:  ($r | group_by(.tool)  | map({key: (.[0].tool  // "?"), value: length}) | from_entries),
        by_model: ($r | group_by(.model) | map({key: (.[0].model // "?"), value: length}) | from_entries),
        by_exit:  ($r | group_by(.exit)  | map({key: (.[0].exit | tostring), value: length}) | from_entries),
        first_ts: (if $n == 0 then null else ($r | map(.ts) | min) end),
        last_ts:  (if $n == 0 then null else ($r | map(.ts) | max) end)
      }
    ' "$LOG"
)"

if (( EMIT_JSON )); then
  printf '%s\n' "$summary" | jq --arg log "$LOG" '. + {log:$log}'
  exit "$EX_OK"
fi

total=$(jq -r '.total' <<<"$summary")
ok=$(jq -r '.ok' <<<"$summary")
failed=$(jq -r '.failed' <<<"$summary")
rate=$(jq -r '.success_rate' <<<"$summary")
lmin=$(jq -r '.latency_ms.min' <<<"$summary")
lmean=$(jq -r '.latency_ms.mean' <<<"$summary")
lp50=$(jq -r '.latency_ms.p50' <<<"$summary")
lp90=$(jq -r '.latency_ms.p90' <<<"$summary")
lmax=$(jq -r '.latency_ms.max' <<<"$summary")
by_tool=$(jq -r '.by_tool  | to_entries | map("\(.key)=\(.value)") | join("  ")' <<<"$summary")
by_model=$(jq -r '.by_model | to_entries | map("\(.key)=\(.value)") | join("  ")' <<<"$summary")
by_exit=$(jq -r '.by_exit  | to_entries | map("\(.key)=\(.value)") | join("  ")' <<<"$summary")
first_ts=$(jq -r '.first_ts // "-"' <<<"$summary")
last_ts=$(jq -r '.last_ts  // "-"' <<<"$summary")
pct=$(awk -v r="$rate" 'BEGIN{printf "%.1f%%", r*100}')

printf 'Ollama wrapper stats\n'
printf '  log:        %s\n' "$LOG"
if [[ -n "$F_TOOL$F_MODEL$F_SINCE" ]]; then
  printf '  filter:     tool=%s model=%s since=%s\n' "${F_TOOL:-*}" "${F_MODEL:-*}" "${F_SINCE:-*}"
fi
printf '  calls:      %s\n' "$total"
printf '  ok:         %s (%s)\n' "$ok" "$pct"
printf '  failed:     %s\n' "$failed"
printf '  latency_ms: min=%s  mean=%s  p50=%s  p90=%s  max=%s\n' \
  "$lmin" "$lmean" "$lp50" "$lp90" "$lmax"
printf '  by tool:    %s\n' "${by_tool:--}"
printf '  by model:   %s\n' "${by_model:--}"
printf '  by exit:    %s\n' "${by_exit:--}"
printf '  window:     %s .. %s\n' "$first_ts" "$last_ts"
