#!/bin/bash

################################################################################
# Code Assistant - Install Dependencies Script
# Purpose: Install dependencies only (assumes venv already exists)
# Usage: ./install_deps.sh [--dev]
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
PROJECT_DIR="$SCRIPT_DIR"
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

check_venv() {
    if [ ! -f "$VENV_DIR/bin/activate" ]; then
        print_error "Virtual environment not found at $VENV_DIR"
        echo ""
        echo "Please run setup.sh first to create the environment:"
        echo "  ./setup.sh"
        exit 1
    fi
}

activate_venv() {
    source "$VENV_DIR/bin/activate"
    print_success "Virtual environment activated"
}

install_requirements() {
    if [ ! -f "$PROJECT_DIR/requirements.txt" ]; then
        print_error "requirements.txt not found"
        exit 1
    fi
    
    print_info "Installing dependencies..."
    pip install -r "$PROJECT_DIR/requirements.txt"
    print_success "Dependencies installed"
}

install_dev_requirements() {
    if [ ! -f "$PROJECT_DIR/requirements-dev.txt" ]; then
        print_error "requirements-dev.txt not found"
        exit 1
    fi
    
    print_info "Installing development dependencies..."
    pip install -r "$PROJECT_DIR/requirements-dev.txt"
    print_success "Development dependencies installed"
}

show_help() {
    echo ""
    echo -e "${BLUE}Install Dependencies Script${NC}"
    echo ""
    echo "Usage: ./install_deps.sh [options]"
    echo ""
    echo "Options:"
    echo "  (no options)  Install only runtime dependencies"
    echo "  --dev         Install both runtime and development dependencies"
    echo "  -h, --help    Show this help message"
    echo ""
}

main() {
    echo ""
    echo -e "${BLUE}Code Assistant - Install Dependencies${NC}"
    echo ""
    
    check_venv
    activate_venv
    
    case "${1:-}" in
        -h|--help)
            show_help
            exit 0
            ;;
        --dev)
            install_requirements
            install_dev_requirements
            echo ""
            print_success "All dependencies installed successfully"
            exit 0
            ;;
        "")
            install_requirements
            echo ""
            print_success "Runtime dependencies installed successfully"
            echo ""
            print_info "To install development dependencies, run:"
            echo "  ./install_deps.sh --dev"
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
