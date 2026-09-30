#!/bin/bash

################################################################################
# Code Assistant - Environment Setup Script
# Purpose: Initialize virtual environment and install dependencies
# Usage: ./setup.sh
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
print_header() {
    echo ""
    echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║${NC}     Code Assistant - Environment Setup Script            ${BLUE}║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

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
    print_info "Checking Python installation..."
    
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 not found. Please install Python 3.8 or higher."
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    print_success "Python $PYTHON_VERSION found"
}

check_pip() {
    print_info "Checking pip installation..."
    
    if ! python3 -m pip --version > /dev/null 2>&1; then
        print_error "pip not found. Please install pip."
        exit 1
    fi
    
    print_success "pip is installed"
}

create_venv() {
    print_info "Setting up virtual environment..."
    
    if [ -d "$VENV_DIR" ]; then
        echo -n "Virtual environment already exists. Remove and recreate? (y/n) "
        read -r response
        if [ "$response" = "y" ] || [ "$response" = "Y" ]; then
            rm -rf "$VENV_DIR"
            print_info "Removed existing virtual environment"
        else
            print_info "Using existing virtual environment"
            return 0
        fi
    fi
    
    python3 -m venv "$VENV_DIR"
    print_success "Virtual environment created at $VENV_DIR"
}

activate_venv() {
    if [ -f "$VENV_DIR/bin/activate" ]; then
        source "$VENV_DIR/bin/activate"
        print_success "Virtual environment activated"
    else
        print_error "Failed to activate virtual environment"
        exit 1
    fi
}

upgrade_pip() {
    print_info "Upgrading pip..."
    pip install --upgrade pip setuptools wheel -q
    print_success "pip upgraded"
}

install_requirements() {
    if [ ! -f "$PROJECT_DIR/requirements.txt" ]; then
        print_error "requirements.txt not found"
        exit 1
    fi
    
    print_info "Installing dependencies..."
    pip install -r "$PROJECT_DIR/requirements.txt" -q
    print_success "Dependencies installed"
}

install_dev_requirements() {
    if [ ! -f "$PROJECT_DIR/requirements-dev.txt" ]; then
        print_error "requirements-dev.txt not found"
        exit 1
    fi
    
    echo -n "Install development dependencies? (y/n) "
    read -r response
    if [ "$response" = "y" ] || [ "$response" = "Y" ]; then
        print_info "Installing development dependencies..."
        pip install -r "$PROJECT_DIR/requirements-dev.txt" -q
        print_success "Development dependencies installed"
    else
        print_info "Skipping development dependencies"
    fi
}

install_package() {
    print_info "Installing code-assistant package..."
    pip install -e "$PROJECT_DIR" -q
    print_success "code-assistant installed in development mode"
}

verify_installation() {
    print_info "Verifying installation..."
    
    local errors=0
    
    # Check for required modules
    if ! python3 -c "import yaml" 2>/dev/null; then
        print_error "yaml module not found"
        errors=$((errors + 1))
    else
        echo -e "  ${GREEN}✓${NC} yaml module available"
    fi
    
    if ! python3 -c "import code_starter" 2>/dev/null; then
        print_error "code_starter module not found"
        errors=$((errors + 1))
    else
        echo -e "  ${GREEN}✓${NC} code_starter module available"
    fi
    
    if ! python3 -c "import shared" 2>/dev/null; then
        print_error "shared module not found"
        errors=$((errors + 1))
    else
        echo -e "  ${GREEN}✓${NC} shared module available"
    fi
    
    if [ $errors -gt 0 ]; then
        print_error "Installation verification failed with $errors error(s)"
        return 1
    else
        print_success "Installation verified successfully"
        return 0
    fi
}

show_next_steps() {
    echo ""
    echo -e "${BLUE}Next Steps:${NC}"
    echo ""
    echo "1. Run the main menu:"
    echo "   ${GREEN}./run_code_assistant.sh${NC}"
    echo ""
    echo "2. Or run specific modules:"
    echo "   ${GREEN}./run_starter.sh${NC}"
    echo "   ${GREEN}./run_debugger.sh${NC}"
    echo "   ${GREEN}./run_patcher.sh${NC}"
    echo ""
    echo "3. Or activate the virtual environment manually:"
    echo "   ${GREEN}source venv/bin/activate${NC}"
    echo ""
    echo "4. View documentation:"
    echo "   ${GREEN}cat README.md${NC}"
    echo ""
}

main() {
    print_header
    
    check_python
    check_pip
    create_venv
    activate_venv
    upgrade_pip
    install_requirements
    install_dev_requirements
    install_package
    
    echo ""
    if verify_installation; then
        echo ""
        print_success "Environment setup completed successfully!"
        show_next_steps
    else
        echo ""
        print_error "Environment setup completed with warnings"
        exit 1
    fi
}

# Run main function
main "$@"
