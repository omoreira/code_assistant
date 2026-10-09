#!/bin/bash

################################################################################
# Code Debugger - Quick Launch Script
# Purpose: Run code_debugger module (currently in development)
# Usage: ./run_debugger.sh [options]
################################################################################

set -e

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

# Functions
print_error() {
    echo -e "${RED}✗ Error: $1${NC}" >&2
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
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
    echo -e "${BLUE}Code Debugger - Quick Launch${NC}"
    echo ""
    echo "Usage: ./run_debugger.sh [options]"
    echo ""
    echo "⚠️  Note: code_debugger is currently under development"
    echo ""
    echo "Options:"
    echo "  -h, --help         Show this help message"
    echo "  --info             Show module information and roadmap"
    echo "  --docs             Show documentation links"
    echo "  --status           Show environment status"
    echo ""
}

show_info() {
    echo ""
    echo -e "${BLUE}Code Debugger Module${NC}"
    echo ""
    echo -e "${YELLOW}Current Status: IN DEVELOPMENT${NC}"
    echo ""
    echo "Purpose:"
    echo "  Intelligent code analysis and debugging for Python code"
    echo ""
    echo "Planned Features:"
    echo "  • Code quality analysis and metrics"
    echo "  • Bug detection and diagnosis"
    echo "  • Performance profiling and bottleneck detection"
    echo "  • Automated test generation"
    echo "  • Code improvement suggestions"
    echo ""
    echo "Implementation Roadmap:"
    echo "  Phase 1: Basic code analyzer"
    echo "  Phase 2: Error diagnosis engine"
    echo "  Phase 3: Performance profiler"
    echo "  Phase 4: Suggestions engine"
    echo "  Phase 5: Test generation"
    echo ""
    echo "For more details, see: docs/code_debugger/README.md"
    echo ""
}

show_docs() {
    echo ""
    echo -e "${BLUE}Code Debugger Documentation${NC}"
    echo ""
    echo "Main Documentation:"
    echo "  • docs/code_debugger/README.md      - Module overview"
    echo "  • docs/ARCHITECTURE.md              - System architecture"
    echo "  • docs/CONTRIBUTING.md              - How to contribute"
    echo ""
    echo "Want to help develop this module?"
    echo "  1. Read docs/CONTRIBUTING.md"
    echo "  2. Choose a feature to implement"
    echo "  3. Create a branch: git checkout -b feature/your-feature"
    echo "  4. Submit a pull request"
    echo ""
}

show_status() {
    echo ""
    echo -e "${BLUE}Environment Status:${NC}"
    echo ""
    
    if [ -d "$VENV_DIR" ]; then
        echo -e "  Virtual Environment: ${GREEN}✓ Ready${NC}"
    else
        echo -e "  Virtual Environment: ${YELLOW}⚠ Not set up${NC}"
    fi
    
    if python3 -c "import yaml" 2>/dev/null; then
        echo -e "  Dependencies:        ${GREEN}✓ Installed${NC}"
    else
        echo -e "  Dependencies:        ${YELLOW}⚠ Not installed${NC}"
    fi
    
    if python3 -c "import code_debugger" 2>/dev/null; then
        echo -e "  code_debugger:       ${GREEN}✓ Available${NC}"
    else
        echo -e "  code_debugger:       ${RED}✗ Not found${NC}"
    fi
    
    echo ""
}

main() {
    # Parse arguments
    case "${1:-}" in
        -h|--help)
            show_help
            exit 0
            ;;
        --info)
            show_info
            exit 0
            ;;
        --docs)
            show_docs
            exit 0
            ;;
        --status)
            show_status
            exit 0
            ;;
        "")
            check_python
            setup_venv
            activate_venv
            install_deps
            
            echo ""
            print_warning "code_debugger is currently under development"
            echo ""
            echo "Available commands:"
            echo "  ./run_debugger.sh --info     - Show module information"
            echo "  ./run_debugger.sh --docs     - Show documentation"
            echo "  ./run_debugger.sh --status   - Check environment"
            echo ""
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
}

main "$@"
