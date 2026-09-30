#!/bin/bash

################################################################################
# Code Refractor - Quick Launch Script
# Purpose: Run code_refractor module for safe code refactoring
# Usage: ./run_refractor.sh [options]
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
    echo -e "${BLUE}Code Refractor - Quick Launch${NC}"
    echo ""
    echo "Usage: ./run_refractor.sh [options]"
    echo ""
    echo "Safe code refactoring with automatic path and import verification"
    echo ""
    echo "Options:"
    echo "  -h, --help         Show this help message"
    echo "  --info             Show module information and features"
    echo "  --docs             Show documentation links"
    echo "  --status           Show environment status"
    echo "  -i, --interactive  Run interactive refactoring mode"
    echo ""
}

show_info() {
    echo ""
    echo -e "${BLUE}Code Refractor Module${NC}"
    echo ""
    echo -e "${GREEN}Status: Fully Implemented & Ready to Use${NC}"
    echo ""
    echo "Purpose:"
    echo "  Verify and change paths/names after refactoring"
    echo "  Ensures refactoring doesn't break code"
    echo ""
    echo "Key Features:"
    echo "  • RefactoringVerifier - Verify refactoring safety before execution"
    echo "  • CodeRefactorer - Execute refactoring with automatic updates"
    echo "  • PathResolver - Resolve and validate all paths"
    echo "  • DependencyMapper - Map dependencies and analyze impact"
    echo ""
    echo "What It Does:"
    echo "  ✓ Checks if refactoring is safe"
    echo "  ✓ Automatically updates all imports"
    echo "  ✓ Updates configuration files"
    echo "  ✓ Updates documentation"
    echo "  ✓ Detects circular dependencies"
    echo "  ✓ Analyzes refactoring impact"
    echo "  ✓ Suggests safe refactoring order"
    echo "  ✓ Dry-run mode for previewing"
    echo ""
    echo "Available Classes:"
    echo "  from code_refractor import RefactoringVerifier"
    echo "  from code_refractor import CodeRefactorer"
    echo "  from code_refractor import PathResolver"
    echo "  from code_refractor import DependencyMapper"
    echo ""
}

show_docs() {
    echo ""
    echo -e "${BLUE}Code Refractor Documentation${NC}"
    echo ""
    echo "Main Documentation:"
    echo "  • docs/code_refractor/README.md       - Complete user guide"
    echo "  • code_refractor/QUICK_START.md       - Quick reference guide"
    echo "  • code_refractor/REFACTORING_MODULE_SUMMARY.md - Module overview"
    echo "  • docs/ARCHITECTURE.md                - System architecture"
    echo ""
    echo "Quick Example:"
    echo "  from code_refractor import RefactoringVerifier, CodeRefactorer"
    echo ""
    echo "  # Check if refactoring is safe"
    echo "  verifier = RefactoringVerifier('.')"
    echo "  issues = verifier.check_refactoring_safety('old.py', 'new.py')"
    echo "  print(verifier.generate_refactoring_report())"
    echo ""
    echo "  # Do the refactoring"
    echo "  refactorer = CodeRefactorer('.')"
    echo "  result = refactorer.refactor_with_verification('old.py', 'new.py')"
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
    
    if python3 -c "import code_refractor" 2>/dev/null; then
        echo -e "  code_refractor:      ${GREEN}✓ Available${NC}"
    else
        echo -e "  code_refractor:      ${RED}✗ Not found${NC}"
    fi
    
    echo ""
}

run_interactive() {
    echo ""
    echo -e "${BLUE}Code Refractor - Interactive Mode${NC}"
    echo ""
    
    check_python
    setup_venv
    activate_venv
    install_deps
    
    echo ""
    python3 << 'PYTHON_CODE'
from code_refractor import RefactoringVerifier, CodeRefactorer, DependencyMapper

print("\n" + "="*70)
print("CODE REFRACTOR - INTERACTIVE MODE")
print("="*70)

menu = """
What would you like to do?

1) Verify if refactoring is safe
2) Perform refactoring with automatic updates
3) Analyze project dependencies
4) Find circular dependencies
5) Get refactoring suggestions
6) Exit

Choice (1-6): """

while True:
    choice = input(menu).strip()
    
    if choice == '1':
        old_path = input("Old path (e.g., module.py): ").strip()
        new_path = input("New path (e.g., utils/module.py): ").strip()
        
        verifier = RefactoringVerifier(".")
        issues = verifier.check_refactoring_safety(old_path, new_path)
        print("\n" + verifier.generate_refactoring_report())
    
    elif choice == '2':
        old_path = input("Old path: ").strip()
        new_path = input("New path: ").strip()
        dry_run = input("Dry-run mode? (y/n, default: y): ").strip().lower() != 'n'
        
        refactorer = CodeRefactorer(".", dry_run=dry_run)
        result = refactorer.refactor_with_verification(old_path, new_path)
        
        print("\n" + "="*70)
        if result.success:
            print("✓ Refactoring completed successfully!")
            print(f"  Files modified: {result.files_modified}")
            print(f"  Changes made:")
            for change in result.changes_made:
                print(f"    - {change}")
        else:
            print("✗ Refactoring failed!")
            for error in result.errors:
                print(f"  {error.message}")
        print("="*70)
    
    elif choice == '3':
        mapper = DependencyMapper(".")
        graph = mapper.build_dependency_graph()
        print(f"\n✓ Dependency graph built ({len(graph)} modules)")
        print("\nExport as:")
        print("  1) Text format (human-readable)")
        print("  2) DOT format (for Graphviz)")
        print("  3) JSON format (programmatic)")
        
        export_choice = input("Choice (1-3): ").strip()
        format_map = {'1': 'text', '2': 'dot', '3': 'json'}
        if export_choice in format_map:
            output = mapper.export_dependency_graph(format_map[export_choice])
            print("\n" + output)
    
    elif choice == '4':
        mapper = DependencyMapper(".")
        mapper.build_dependency_graph()
        circles = mapper.find_circular_dependencies()
        
        if circles:
            print(f"\n⚠ Found {len(circles)} circular dependencies:")
            for cycle in circles:
                print(f"  {' → '.join(cycle)}")
        else:
            print("\n✓ No circular dependencies found!")
    
    elif choice == '5':
        mapper = DependencyMapper(".")
        mapper.build_dependency_graph()
        order = mapper.suggest_refactoring_order()
        
        print("\n" + "="*70)
        print("Suggested Refactoring Order (modules with fewer dependents first)")
        print("="*70)
        for i, module in enumerate(order, 1):
            impact = mapper.get_impact(module)
            print(f"{i:2d}. {module:30s} (affects {impact['total_affected']} modules)")
    
    elif choice == '6':
        print("\nGoodbye!")
        break
    
    else:
        print("Invalid choice. Try again.")

print("\n")
PYTHON_CODE
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
        -i|--interactive)
            run_interactive
            exit 0
            ;;
        "")
            check_python
            setup_venv
            activate_venv
            install_deps
            
            echo ""
            print_success "code_refractor is ready to use!"
            echo ""
            echo "Available commands:"
            echo "  ./run_refractor.sh --info        - Show module information"
            echo "  ./run_refractor.sh --docs        - Show documentation links"
            echo "  ./run_refractor.sh --status      - Check environment status"
            echo "  ./run_refractor.sh -i            - Interactive refactoring mode"
            echo "  ./run_refractor.sh -h            - Show help"
            echo ""
            echo "Or use directly in Python:"
            echo "  from code_refractor import RefactoringVerifier, CodeRefactorer"
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
