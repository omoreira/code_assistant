#!/bin/bash

################################################################################
# Code Starter - Quick Launch Script
# Purpose: Run code_starter module directly
# Usage: ./run_starter.sh [options]
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
    echo -e "${BLUE}Code Starter - Quick Launch${NC}"
    echo ""
    echo "Usage: ./run_starter.sh [options]"
    echo ""
    echo "Options:"
    echo "  -h, --help         Show this help message"
    echo "  -i, --interactive  Run in interactive mode (default)"
    echo "  -c, --create       Create a new project specification"
    echo "  --status           Show environment status"
    echo "  --setup            Setup/reinstall dependencies"
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
    
    if [ -d "$PROJECT_DIR/src/code_starter" ]; then
        echo -e "  Code Starter:        ${GREEN}✓ Found${NC}"
    else
        echo -e "  Code Starter:        ${RED}✗ Not found${NC}"
    fi
    
    echo ""
}

run_interactive() {
    echo ""
    echo -e "${GREEN}Launching code_starter in interactive mode...${NC}"
    echo ""
    python3 << 'EOF'
from code_starter import StarterFileCreator
import sys

try:
    creator = StarterFileCreator()
    creator.run_interactive()
except KeyboardInterrupt:
    print("\n\nInterrupted by user.")
    sys.exit(0)
except Exception as e:
    print(f"\nError: {e}")
    sys.exit(1)
EOF
}

run_create() {
    echo ""
    echo -e "${GREEN}Creating a new project...${NC}"
    echo ""
    
    read -p "Enter project name: " project_name
    read -p "Enter project description: " description
    read -p "Enter modules (comma-separated): " modules
    read -p "Enter dependencies (comma-separated): " dependencies
    
    python3 << EOF
from code_starter import StarterFileCreator

try:
    creator = StarterFileCreator()
    modules_list = [m.strip() for m in "$modules".split(',')]
    deps_list = [d.strip() for d in "$dependencies".split(',')]
    
    spec = creator.create_project_spec(
        name="$project_name",
        description="$description",
        modules=modules_list,
        dependencies=deps_list
    )
    
    filename = "${project_name}.pseudo"
    creator.save_spec(spec, filename)
    print(f"\n✓ Project specification saved to: {filename}")
except Exception as e:
    print(f"\nError: {e}")
EOF
}

main() {
    # Parse arguments
    case "${1:-}" in
        -h|--help)
            show_help
            exit 0
            ;;
        --status)
            show_status
            exit 0
            ;;
        --setup)
            check_python
            setup_venv
            activate_venv
            install_deps
            print_success "Environment setup complete"
            exit 0
            ;;
        -c|--create)
            check_python
            setup_venv
            activate_venv
            install_deps
            run_create
            exit 0
            ;;
        -i|--interactive|"")
            check_python
            setup_venv
            activate_venv
            install_deps
            run_interactive
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
