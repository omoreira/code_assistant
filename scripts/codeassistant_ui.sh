#!/bin/bash

################################################################################
# Code Assistant - Streamlit UI Launcher
# Purpose: Create/activate the project virtual environment and launch the
#          Streamlit web UI (Starter, Editor, Converter, Patcher) on port 8503.
# Usage: ./codeassistant_ui.sh [--port PORT] [-- <extra streamlit args>]
################################################################################

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Project directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
export PYTHONPATH="$PROJECT_DIR/src${PYTHONPATH:+:$PYTHONPATH}"
cd -- "$PROJECT_DIR"
VENV_DIR="$PROJECT_DIR/venv"

# UI settings
UI_APP="$PROJECT_DIR/ui/app.py"
UI_PORT="8503"

print_error() {
    echo -e "${RED}✗ Error: $1${NC}" >&2
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ $1${NC}"
}

check_python() {
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 not found. Please install Python 3.8 or higher."
        exit 1
    fi
}

setup_venv() {
    if [ ! -d "$VENV_DIR" ]; then
        print_info "Creating virtual environment..."
        python3 -m venv "$VENV_DIR"
        print_success "Virtual environment created"
    fi
}

activate_venv() {
    if [ -f "$VENV_DIR/bin/activate" ]; then
        # shellcheck disable=SC1091
        source "$VENV_DIR/bin/activate"
    else
        print_error "Virtual environment not found"
        exit 1
    fi
}

install_deps() {
    if ! python3 -c "import streamlit" 2>/dev/null; then
        print_info "Installing dependencies..."
        pip install -q -r "$PROJECT_DIR/requirements.txt"
        print_success "Dependencies installed"
    fi
}

check_app() {
    if [ ! -f "$UI_APP" ]; then
        print_error "UI entrypoint not found: $UI_APP"
        exit 1
    fi
}

show_help() {
    echo ""
    echo -e "${BLUE}Code Assistant - Streamlit UI${NC}"
    echo ""
    echo "Usage: ./codeassistant_ui.sh [options]"
    echo ""
    echo "Creates/activates the project virtual environment and launches the"
    echo "Streamlit web UI."
    echo ""
    echo "Options:"
    echo "  -h, --help         Show this help message"
    echo "  --port PORT        Port to listen on (default: 8503)"
    echo "  --                 Pass all remaining arguments to 'streamlit run'"
    echo ""
    echo "All LLM-backed features require a reachable local Ollama server; the"
    echo "app hard-blocks with a message when Ollama is unavailable."
    echo ""
}

run_ui() {
    echo ""
    echo -e "${GREEN}Launching Streamlit UI on http://localhost:${UI_PORT}${NC}"
    echo ""
    streamlit run "$UI_APP" --server.port "$UI_PORT" "$@"
}

main() {
    # Handle help before doing any work.
    case "${1:-}" in
        -h|--help)
            show_help
            exit 0
            ;;
    esac

    # Pull out --port; forward everything else to 'streamlit run'.
    local extra=()
    while [ "$#" -gt 0 ]; do
        case "$1" in
            --port)
                if [ -z "${2:-}" ]; then
                    print_error "--port requires a value"
                    exit 2
                fi
                UI_PORT="$2"
                shift 2
                ;;
            --port=*)
                UI_PORT="${1#--port=}"
                shift
                ;;
            --)
                shift
                extra+=("$@")
                break
                ;;
            *)
                extra+=("$1")
                shift
                ;;
        esac
    done

    check_python
    setup_venv
    activate_venv
    install_deps
    check_app

    run_ui ${extra[@]+"${extra[@]}"}
}

main "$@"
