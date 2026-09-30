"""Scripts Writer Module

Generates shell scripts for running code-assistant modules.
Creates executable bash scripts in the scripts/ directory.

Classes:
    ScriptsWriter: Main class for generating shell scripts
"""

from pathlib import Path
from typing import Dict, List, Optional
import os


class ScriptsWriter:
    """Generate shell scripts for running code-assistant modules."""

    def __init__(self, output_dir: str = "./scripts"):
        """Initialize ScriptsWriter.

        Args:
            output_dir: Directory where scripts will be created (default: ./scripts)
        """
        self.output_dir = Path(output_dir)
        self.scripts = {}

    def create_scripts_directory(self) -> str:
        """Create scripts directory if it doesn't exist.

        Returns:
            Path to scripts directory
        """
        self.output_dir.mkdir(parents=True, exist_ok=True)
        return str(self.output_dir)

    def write_setup_script(self) -> str:
        """Write setup.sh script.

        Returns:
            Path to created script
        """
        setup_content = '''#!/bin/bash

################################################################################
# Code Assistant - Environment Setup Script
# Purpose: Initialize virtual environment and install dependencies
# Usage: ./setup.sh
################################################################################

set -e

# Colors
RED='\\033[0;31m'
GREEN='\\033[0;32m'
YELLOW='\\033[1;33m'
BLUE='\\033[0;34m'
NC='\\033[0m'

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
    
    if ! python3 -c "import yaml" 2>/dev/null; then
        print_error "yaml module not found"
        errors=$((errors + 1))
    else
        echo -e "  ${GREEN}✓${NC} yaml module available"
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
    echo ""
    echo "3. View documentation:"
    echo "   ${GREEN}cat ../README.md${NC}"
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

main "$@"
'''
        script_path = self.output_dir / "setup.sh"
        script_path.write_text(setup_content)
        os.chmod(script_path, 0o755)
        return str(script_path)

    def write_run_script(self, module_name: str) -> str:
        """Write run script for a specific module.

        Args:
            module_name: Name of the module (starter, debugger, patcher)

        Returns:
            Path to created script
        """
        run_content = f'''#!/bin/bash

################################################################################
# Code {module_name.title()} - Quick Launch Script
# Purpose: Run code_{module_name} module directly
# Usage: ./run_{module_name}.sh [options]
################################################################################

set -e

# Colors
RED='\\033[0;31m'
GREEN='\\033[0;32m'
YELLOW='\\033[1;33m'
BLUE='\\033[0;34m'
NC='\\033[0m'

# Project directory
SCRIPT_DIR="$(cd "$(dirname "${{BASH_SOURCE[0]}}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
export PYTHONPATH="$PROJECT_DIR/src${{PYTHONPATH:+:$PYTHONPATH}}"
cd -- "$PROJECT_DIR"
VENV_DIR="$PROJECT_DIR/venv"

# Functions
print_error() {{
    echo -e "${{RED}}✗ Error: $1${{NC}}" >&2
}}

print_success() {{
    echo -e "${{GREEN}}✓ $1${{NC}}"
}}

print_info() {{
    echo -e "${{YELLOW}}ℹ $1${{NC}}"
}}

check_python() {{
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 not found. Please install Python 3.8 or higher."
        exit 1
    fi
}}

setup_venv() {{
    if [ ! -d "$VENV_DIR" ]; then
        print_info "Creating virtual environment..."
        python3 -m venv "$VENV_DIR"
        print_success "Virtual environment created"
    fi
}}

activate_venv() {{
    if [ -f "$VENV_DIR/bin/activate" ]; then
        source "$VENV_DIR/bin/activate"
    else
        print_error "Virtual environment not found"
        exit 1
    fi
}}

install_deps() {{
    if ! python3 -c "import yaml" 2>/dev/null; then
        print_info "Installing dependencies..."
        pip install -q -r "$PROJECT_DIR/requirements.txt"
        print_success "Dependencies installed"
    fi
}}

show_help() {{
    echo ""
    echo -e "${{BLUE}}Code {module_name.title()} - Quick Launch${{NC}}"
    echo ""
    echo "Usage: ./run_{module_name}.sh [options]"
    echo ""
    echo "Options:"
    echo "  -h, --help      Show this help message"
    echo "  --status        Show environment status"
    echo ""
}}

show_status() {{
    echo ""
    echo -e "${{BLUE}}Environment Status:${{NC}}"
    echo ""
    
    if [ -d "$VENV_DIR" ]; then
        echo -e "  Virtual Environment: ${{GREEN}}✓ Ready${{NC}}"
    else
        echo -e "  Virtual Environment: ${{YELLOW}}⚠ Not set up${{NC}}"
    fi
    
    if python3 -c "import yaml" 2>/dev/null; then
        echo -e "  Dependencies:        ${{GREEN}}✓ Installed${{NC}}"
    else
        echo -e "  Dependencies:        ${{YELLOW}}⚠ Not installed${{NC}}"
    fi
    
    echo ""
}}

main() {{
    case "${{1:-}}" in
        -h|--help)
            show_help
            exit 0
            ;;
        --status)
            show_status
            exit 0
            ;;
        *)
            check_python
            setup_venv
            activate_venv
            install_deps
            
            echo ""
            print_success "Running code_{module_name}..."
            echo ""
            python3 -c "from code_{module_name} import *; print('Module loaded successfully')"
            exit 0
            ;;
    esac
}}

main "$@"
'''
        script_path = self.output_dir / f"run_{module_name}.sh"
        script_path.write_text(run_content)
        os.chmod(script_path, 0o755)
        return str(script_path)

    def generate_all_scripts(self, modules: Optional[List[str]] = None) -> Dict[str, str]:
        """Generate all standard scripts.

        Args:
            modules: List of module names (default: starter, debugger, patcher, refractor)

        Returns:
            Dictionary mapping script names to their paths
        """
        if modules is None:
            modules = ["starter", "debugger", "patcher", "refractor"]

        # Create scripts directory
        self.create_scripts_directory()

        # Write setup script
        self.scripts["setup.sh"] = self.write_setup_script()

        # Write run scripts for each module
        for module in modules:
            script_name = f"run_{module}.sh"
            self.scripts[script_name] = self.write_run_script(module)

        return self.scripts

    def generate_to_project(
        self, project_dir: str, modules: Optional[List[str]] = None
    ) -> Dict[str, str]:
        """Generate scripts for a project.

        Args:
            project_dir: Project directory path
            modules: List of module names

        Returns:
            Dictionary mapping script names to their paths
        """
        project_path = Path(project_dir)
        scripts_dir = project_path / "scripts"
        self.output_dir = scripts_dir

        return self.generate_all_scripts(modules)

    def get_script_count(self) -> int:
        """Get number of generated scripts.

        Returns:
            Number of scripts
        """
        return len(self.scripts)

    def list_generated_scripts(self) -> List[str]:
        """List all generated script names.

        Returns:
            List of script names
        """
        return list(self.scripts.keys())

    def get_script_info(self) -> Dict[str, Dict[str, str]]:
        """Get information about generated scripts.

        Returns:
            Dictionary with script metadata
        """
        info = {}
        for name, path in self.scripts.items():
            script_path = Path(path)
            if script_path.exists():
                size = script_path.stat().st_size
                info[name] = {
                    "path": path,
                    "size": f"{size / 1024:.1f} KB",
                    "executable": os.access(path, os.X_OK),
                }
        return info


if __name__ == "__main__":
    # Example usage
    writer = ScriptsWriter("./test_scripts")
    scripts = writer.generate_all_scripts()

    print("Generated Scripts:")
    for name, path in scripts.items():
        print(f"  ✓ {name} → {path}")

    print(f"\nTotal scripts: {writer.get_script_count()}")
    print("\nScript Info:")
    for name, info in writer.get_script_info().items():
        print(f"  {name}: {info['size']} (executable: {info['executable']})")
