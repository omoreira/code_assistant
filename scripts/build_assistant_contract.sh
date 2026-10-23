#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd -- "$SCRIPT_DIR/.." && pwd)"
export PYTHONPATH="$PROJECT_DIR/src${PYTHONPATH:+:$PYTHONPATH}"

if [[ $# -lt 2 ]]; then
    echo "Usage: build_assistant_contract.sh <requirements.txt|requirements.md> <examples-dir> [-o contract.json]" >&2
    exit 2
fi

exec python3 -m code_converter.assistant_contract_builder "$@"
