#!/bin/bash

################################################################################
# Code Assistant - Full Pipeline Launcher
# Purpose: Run the preflight + code_starter + code_analyzer + repo_documenter
#          pipeline against an approved starterfile.pseudo.
# Usage: ./run_pipeline.sh <project_root> [--data-dir DIR] [--use-llm] [--interactive]
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
VENV_DIR="$PROJECT_DIR/venv"

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
    if ! python3 -c "import yaml" 2>/dev/null; then
        print_info "Installing dependencies..."
        pip install -q -r "$PROJECT_DIR/requirements.txt"
        print_success "Dependencies installed"
    fi
}

show_help() {
    echo ""
    echo -e "${BLUE}Code Assistant - Full Pipeline${NC}"
    echo ""
    echo "Usage: ./run_pipeline.sh <project_root> [options]"
    echo ""
    echo "Runs, in order: preflight (static analysis + approval check),"
    echo "code_starter (skeleton + databases + code generation),"
    echo "code_analyzer, and repo_documenter."
    echo ""
    echo "Arguments:"
    echo "  <project_root>     Project containing starterfile.pseudo (default: .)"
    echo ""
    echo "Options:"
    echo "  -h, --help         Show this help message"
    echo "  --starterfile F    Starterfile name (default: starterfile.pseudo)"
    echo "  --data-dir DIR     Database storage path (highest precedence)."
    echo "                     The data directory is created only when its"
    echo "                     location is requested explicitly -- via this flag,"
    echo "                     CODE_ASSISTANT_DATA_DIR/DATA_DIR, a '# PATHS'"
    echo "                     data_dir entry in the starterfile, or --interactive."
    echo "                     Otherwise it is resolved from config/defaults.yaml"
    echo "                     (paths.data_dir) / built-in 'data' and is NOT"
    echo "                     created automatically."
    echo "  --use-llm          Use Ollama for analysis/documentation refresh"
    echo "  --interactive      Prompt for the database storage path (and create it)"
    echo ""
}

main() {
    case "${1:-}" in
        -h|--help)
            show_help
            exit 0
            ;;
        "")
            print_error "A project root is required."
            show_help
            exit 2
            ;;
    esac

    check_python
    setup_venv
    activate_venv
    install_deps

    echo ""
    echo -e "${GREEN}Running pipeline for project: ${1}${NC}"
    echo ""

    python3 -m code_starter.pipeline "$@"
}

main "$@"
