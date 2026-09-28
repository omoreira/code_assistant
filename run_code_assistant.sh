#!/bin/bash

################################################################################
# Code Assistant - Main Entry Point Script
# Purpose: Interactive menu to choose and run any module
# Usage: ./run_code_assistant.sh
################################################################################

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$SCRIPT_DIR"
VENV_DIR="$PROJECT_DIR/venv"

# Functions
print_header() {
    echo ""
    echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║${NC}           Code Assistant - Main Menu                      ${BLUE}║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

print_error() {
    echo -e "${RED}✗ Error: $1${NC}"
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
    
    PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    print_info "Using Python $PYTHON_VERSION"
}

setup_venv() {
    if [ ! -d "$VENV_DIR" ]; then
        print_info "Virtual environment not found. Creating..."
        python3 -m venv "$VENV_DIR"
        print_success "Virtual environment created"
    fi
}

activate_venv() {
    if [ -f "$VENV_DIR/bin/activate" ]; then
        source "$VENV_DIR/bin/activate"
        print_success "Virtual environment activated"
    else
        print_error "Virtual environment not found"
        exit 1
    fi
}

check_dependencies() {
    if ! python3 -c "import yaml" 2>/dev/null; then
        print_info "Installing dependencies..."
        pip install -q -r "$PROJECT_DIR/requirements.txt"
        print_success "Dependencies installed"
    fi
}

show_menu() {
    echo -e "${GREEN}Available Modules:${NC}"
    echo ""
    echo "  1) code_starter     - Project creation and code generation"
    echo "  2) code_debugger    - Code analysis and debugging (in development)"
    echo "  3) code_patcher     - Code refactoring and patching (in development)"
    echo "  4) Setup/Status     - Setup environment or check status"
    echo "  5) Exit             - Exit program"
    echo ""
}

show_status() {
    echo ""
    echo -e "${BLUE}System Status:${NC}"
    echo ""
    if [ -d "$VENV_DIR" ]; then
        echo -e "  Virtual Environment: ${GREEN}✓ Installed${NC}"
    else
        echo -e "  Virtual Environment: ${RED}✗ Not installed${NC}"
    fi
    
    if [ -f "$PROJECT_DIR/requirements.txt" ]; then
        echo -e "  Requirements File:   ${GREEN}✓ Found${NC}"
    else
        echo -e "  Requirements File:   ${RED}✗ Not found${NC}"
    fi
    
    if python3 -c "import yaml" 2>/dev/null; then
        echo -e "  Dependencies:        ${GREEN}✓ Installed${NC}"
    else
        echo -e "  Dependencies:        ${RED}✗ Not installed${NC}"
    fi
    
    echo ""
}

run_starter() {
    echo ""
    echo -e "${GREEN}Starting code_starter module...${NC}"
    echo ""
    python3 -c "
from code_starter import StarterFileCreator
creator = StarterFileCreator()
creator.run_interactive()
"
}

run_debugger() {
    echo ""
    echo -e "${YELLOW}code_debugger is currently under development.${NC}"
    echo ""
    echo "Planned features:"
    echo "  • Code quality analysis"
    echo "  • Bug detection and diagnosis"
    echo "  • Performance profiling"
    echo ""
    echo "See docs/code_debugger/README.md for more information."
    echo ""
}

run_patcher() {
    echo ""
    echo -e "${YELLOW}code_patcher is currently under development.${NC}"
    echo ""
    echo "Planned features:"
    echo "  • Code refactoring"
    echo "  • Patch generation and application"
    echo "  • Automated code quality fixes"
    echo ""
    echo "See docs/code_patcher/README.md for more information."
    echo ""
}

main() {
    # Check Python
    check_python
    
    # Setup and activate venv
    setup_venv
    activate_venv
    
    # Check dependencies
    check_dependencies
    
    # Main loop
    while true; do
        print_header
        show_menu
        
        read -p "Choose an option (1-5): " choice
        
        case $choice in
            1)
                run_starter
                ;;
            2)
                run_debugger
                ;;
            3)
                run_patcher
                ;;
            4)
                show_status
                ;;
            5)
                print_info "Exiting..."
                exit 0
                ;;
            *)
                print_error "Invalid option. Please try again."
                sleep 1
                clear
                ;;
        esac
    done
}

# Run main function
main "$@"
