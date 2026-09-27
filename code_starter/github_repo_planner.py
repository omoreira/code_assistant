"""
github_repo_planner.py

Interactive tool to plan and generate GitHub repository structure for the code assistant project.
Based on the implementation planning session, guides users through setup decisions and generates
necessary files (.gitignore, LICENSE, setup.py, requirements.txt, etc.).

Features:
- Interactive Q&A for GitHub structure decisions
- Validates user inputs
- Generates configuration files
- Creates package structure
- Provides implementation summary
"""

import os
import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime


class GitHubRepoPlanner:
    """Interactive GitHub repository structure planner."""
    
    def __init__(self):
        self.config = {
            'module_structure': None,  # A, B, or C
            'config_files': False,
            'venv_setup': None,  # script, docs, both
            'module_placeholders': False,
            'testing_strategy': None,  # unit, integration, both, none
            'documentation_location': None,  # per-module, root, move-existing
            'ci_cd': False,
            'installation_method': None,  # A, B, C
            'shared_code': None,  # yes, no, minimal
            'github_username': None,
            'github_repo_name': 'code-assistant',
            'author_name': None,
            'author_email': None,
        }
        self.decisions = []  # Track all decisions made
    
    def main_menu(self):
        """Main menu for the planner."""
        while True:
            print("\n" + "="*70)
            print("GITHUB REPOSITORY PLANNER")
            print("="*70)
            print("Setup the code-assistant for GitHub")
            print("-"*70)
            print("1. Answer Implementation Questions")
            print("2. View Current Configuration")
            print("3. Generate Repository Structure")
            print("4. Quick Setup (Use Defaults)")
            print("5. Manual Configuration")
            print("6. Save Configuration")
            print("7. Load Configuration")
            print("8. Generate Summary Report")
            print("9. Exit")
            print("-"*70)
            
            choice = input("Select option (1-9): ").strip()
            
            if choice == '1':
                self.answer_questions()
            elif choice == '2':
                self.view_config()
            elif choice == '3':
                self.generate_structure()
            elif choice == '4':
                self.quick_setup()
            elif choice == '5':
                self.manual_config()
            elif choice == '6':
                self.save_config()
            elif choice == '7':
                self.load_config()
            elif choice == '8':
                self.print_summary()
            elif choice == '9':
                print("\nGoodbye!")
                break
            else:
                print("Invalid option. Try again.")
    
    # ==================== QUESTION & ANSWER ====================
    
    def answer_questions(self):
        """Guide user through all 10 implementation questions."""
        print("\n" + "="*70)
        print("IMPLEMENTATION QUESTIONS")
        print("="*70)
        
        # Q1: Module Structure
        print("\n[Q1] Module Structure")
        print("How should the 3 modules be organized?")
        print("  A) Separate repositories (code-starter, code-analyzer, code-executor)")
        print("  B) Single mono-repo with 3 subdirectories (RECOMMENDED)")
        print("  C) Main repo + submodules")
        self.config['module_structure'] = self._get_choice("A/B/C", ["A", "B", "C"], "B")
        self.decisions.append(f"Module Structure: Option {self.config['module_structure']}")
        
        # Q2: Configuration Files
        print("\n[Q2] Configuration Files")
        print("Do you want configuration files (YAML/JSON)?")
        self.config['config_files'] = self._get_yes_no("Yes/No", True)
        self.decisions.append(f"Config Files: {'Yes' if self.config['config_files'] else 'No'}")
        
        # Q3: Virtual Environment
        print("\n[Q3] Virtual Environment Setup")
        print("How should venv be handled?")
        print("  1) Document setup in README")
        print("  2) Create venv setup script")
        print("  3) Both (RECOMMENDED)")
        choice = self._get_choice("1/2/3", ["1", "2", "3"], "3")
        venv_map = {"1": "docs", "2": "script", "3": "both"}
        self.config['venv_setup'] = venv_map[choice]
        self.decisions.append(f"venv Setup: {self.config['venv_setup']}")
        
        # Q4: Module Placeholders
        print("\n[Q4] Module Placeholders")
        print("Create placeholder files for code_analyzer and code_executor?")
        self.config['module_placeholders'] = self._get_yes_no("Yes/No", True)
        self.decisions.append(f"Module Placeholders: {'Yes' if self.config['module_placeholders'] else 'No'}")
        
        # Q5: Testing Strategy
        print("\n[Q5] Testing Strategy")
        print("What testing approach?")
        print("  1) Unit tests only")
        print("  2) Integration tests only")
        print("  3) Both unit + integration (RECOMMENDED)")
        print("  4) No tests initially")
        choice = self._get_choice("1/2/3/4", ["1", "2", "3", "4"], "3")
        test_map = {"1": "unit", "2": "integration", "3": "both", "4": "none"}
        self.config['testing_strategy'] = test_map[choice]
        self.decisions.append(f"Testing: {self.config['testing_strategy']}")
        
        # Q6: Documentation Location
        print("\n[Q6] Documentation Structure")
        print("Where should module documentation live?")
        print("  1) Each module: code_starter/docs/, code_analyzer/docs/ (RECOMMENDED)")
        print("  2) Root: docs/code_starter/, docs/code_analyzer/")
        print("  3) Move existing docs to code_starter/docs/")
        choice = self._get_choice("1/2/3", ["1", "2", "3"], "1")
        doc_map = {"1": "per-module", "2": "root", "3": "move-existing"}
        self.config['documentation_location'] = doc_map[choice]
        self.decisions.append(f"Documentation: {self.config['documentation_location']}")
        
        # Q7: CI/CD
        print("\n[Q7] Continuous Integration/Deployment")
        print("Add GitHub Actions workflows for automated testing?")
        self.config['ci_cd'] = self._get_yes_no("Yes/No", False)
        self.decisions.append(f"CI/CD: {'Yes' if self.config['ci_cd'] else 'No'}")
        
        # Q8: Installation Method
        print("\n[Q8] Installation Method")
        print("How should users install the package?")
        print("  A) pip install -e . (Python package, RECOMMENDED)")
        print("  B) python code_starter/starterfile_creator.py (Direct scripts)")
        print("  C) Command line tools after pip install (Advanced)")
        self.config['installation_method'] = self._get_choice("A/B/C", ["A", "B", "C"], "A")
        self.decisions.append(f"Installation: Option {self.config['installation_method']}")
        
        # Q9: Shared Code
        print("\n[Q9] Shared Code/Utilities")
        print("Should there be a shared/ directory for common utilities?")
        print("  1) Yes: For config, logging, LLM interface")
        print("  2) No: Each module self-contained")
        print("  3) Minimal: Just what's needed (RECOMMENDED)")
        choice = self._get_choice("1/2/3", ["1", "2", "3"], "3")
        shared_map = {"1": "yes", "2": "no", "3": "minimal"}
        self.config['shared_code'] = shared_map[choice]
        self.decisions.append(f"Shared Code: {self.config['shared_code']}")
        
        # Q10: GitHub Details
        print("\n[Q10] GitHub Repository Details")
        self.config['github_username'] = input("GitHub username: ").strip()
        self.config['github_repo_name'] = input("Repository name (default: code-assistant): ").strip() or "code-assistant"
        self.config['author_name'] = input("Your name: ").strip()
        self.config['author_email'] = input("Your email: ").strip()
        
        self.decisions.append(f"GitHub: {self.config['github_username']}/{self.config['github_repo_name']}")
        self.decisions.append(f"Author: {self.config['author_name']} <{self.config['author_email']}>")
        
        print("\n✓ All questions answered!")
    
    def _get_choice(self, prompt: str, valid_options: List[str], default: str) -> str:
        """Get single character choice from user."""
        while True:
            choice = input(f"{prompt} (default: {default}): ").strip().upper() or default
            if choice.upper() in [o.upper() for o in valid_options]:
                return choice.upper()
            print(f"Invalid. Choose from: {', '.join(valid_options)}")
    
    def _get_yes_no(self, prompt: str, default: bool) -> bool:
        """Get yes/no response from user."""
        default_str = "Yes" if default else "No"
        response = input(f"{prompt} (default: {default_str}): ").strip().lower()
        
        if response in ['y', 'yes']:
            return True
        elif response in ['n', 'no']:
            return False
        else:
            return default
    
    # ==================== VIEW & MANAGE ====================
    
    def view_config(self):
        """Display current configuration."""
        print("\n" + "="*70)
        print("CURRENT CONFIGURATION")
        print("="*70)
        
        for key, value in self.config.items():
            print(f"{key:.<40} {value}")
        
        print("\n" + "="*70)
        print("DECISIONS MADE:")
        for decision in self.decisions:
            print(f"  ✓ {decision}")
    
    def manual_config(self):
        """Manually configure individual settings."""
        print("\n" + "="*70)
        print("MANUAL CONFIGURATION")
        print("="*70)
        
        while True:
            print("\nSettings:")
            for i, (key, value) in enumerate(self.config.items(), 1):
                print(f"{i:2d}. {key:.<40} {value}")
            
            choice = input("\nEdit setting (number) or 'done': ").strip().lower()
            
            if choice == 'done':
                break
            
            try:
                idx = int(choice) - 1
                keys = list(self.config.keys())
                if 0 <= idx < len(keys):
                    key = keys[idx]
                    new_value = input(f"New value for {key}: ").strip()
                    self.config[key] = new_value
                    print(f"✓ Updated {key}")
                else:
                    print("Invalid number")
            except ValueError:
                print("Invalid input")
    
    # ==================== SETUP MODES ====================
    
    def quick_setup(self):
        """Quick setup with default values."""
        print("\n" + "="*70)
        print("QUICK SETUP - Using Recommended Defaults")
        print("="*70)
        
        defaults = {
            'module_structure': 'B',
            'config_files': True,
            'venv_setup': 'both',
            'module_placeholders': True,
            'testing_strategy': 'both',
            'documentation_location': 'per-module',
            'ci_cd': False,
            'installation_method': 'A',
            'shared_code': 'minimal',
            'github_username': input("GitHub username: ").strip() or "yourusername",
            'github_repo_name': 'code-assistant',
            'author_name': input("Your name: ").strip() or "Your Name",
            'author_email': input("Your email: ").strip() or "your.email@example.com",
        }
        
        self.config.update(defaults)
        
        print("\n✓ Quick setup complete with defaults!")
        print("\nDefaults applied:")
        for key, value in defaults.items():
            print(f"  • {key}: {value}")
    
    # ==================== GENERATION ====================
    
    def generate_structure(self):
        """Generate the repository structure based on configuration."""
        print("\n" + "="*70)
        print("GENERATING REPOSITORY STRUCTURE")
        print("="*70)
        
        if not self.config['github_username']:
            print("✗ Error: Configuration incomplete. Answer questions first.")
            return
        
        print("\nGenerating files and structure...")
        
        # Generate files based on configuration
        files_created = []
        
        # Critical files
        try:
            self._create_gitignore()
            files_created.append("✓ .gitignore")
            
            self._create_license()
            files_created.append("✓ LICENSE")
            
            self._create_setup_py()
            files_created.append("✓ setup.py")
            
            self._create_requirements()
            files_created.append("✓ requirements.txt")
            files_created.append("✓ requirements-dev.txt")
            
            self._create_root_readme()
            files_created.append("✓ README.md (root)")
            
            # Optional files
            if self.config['config_files']:
                self._create_config_structure()
                files_created.append("✓ config/ directory")
            
            if self.config['module_placeholders']:
                self._create_module_placeholders()
                files_created.append("✓ Module placeholders")
            
            if self.config['testing_strategy'] != 'none':
                self._create_test_structure()
                files_created.append("✓ tests/ directory")
            
            if self.config['shared_code'] in ['yes', 'minimal']:
                self._create_shared_utilities()
                files_created.append("✓ shared/ directory")
            
            if self.config['ci_cd']:
                self._create_github_workflows()
                files_created.append("✓ .github/workflows/")
            
            print("\n" + "="*70)
            print("FILES CREATED:")
            for file_info in files_created:
                print(f"  {file_info}")
            
            print("\n✓ Repository structure generated successfully!")
            
        except Exception as e:
            print(f"\n✗ Error generating structure: {e}")
    
    def _create_gitignore(self):
        """Create .gitignore file."""
        content = '''# Virtual environments
venv/
env/
ENV/
.venv
__pycache__/
*.py[cod]
*$py.class

# Python
*.egg-info/
dist/
build/
.eggs/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~
.DS_Store

# Testing
.pytest_cache/
.coverage
htmlcov/
.tox/

# Environment
.env
.env.local
*.log
'''
        with open('.gitignore', 'w') as f:
            f.write(content)
    
    def _create_license(self):
        """Create MIT LICENSE file."""
        content = f'''MIT License

Copyright (c) {datetime.now().year} {self.config['author_name']}

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''
        with open('LICENSE', 'w') as f:
            f.write(content)
    
    def _create_setup_py(self):
        """Create setup.py file."""
        content = f'''from setuptools import setup, find_packages

setup(
    name="{self.config['github_repo_name']}",
    version="0.1.0",
    description="Local AI-powered coding assistant with 3 modules",
    author="{self.config['author_name']}",
    author_email="{self.config['author_email']}",
    url="https://github.com/{self.config['github_username']}/{self.config['github_repo_name']}",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        # Add dependencies here as needed
    ],
    extras_require={{
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=3.0",
            "black>=22.0",
            "flake8>=4.0",
            "mypy>=0.950",
            "pylint>=2.0",
        ]
    }},
    entry_points={{
        "console_scripts": [
            # Add CLI commands here if using installation method C
        ],
    }},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
'''
        with open('setup.py', 'w') as f:
            f.write(content)
    
    def _create_requirements(self):
        """Create requirements files."""
        requirements_txt = '''# Core dependencies
# (Add external dependencies here as needed)

# Optional for LLM integration:
# ollama>=0.1.0
'''
        
        requirements_dev = '''# Include core requirements
-r requirements.txt

# Testing
pytest>=7.0
pytest-cov>=3.0

# Code quality
black>=22.0
flake8>=4.0
mypy>=0.950
pylint>=2.0

# Development
ipython>=7.0
'''
        
        with open('requirements.txt', 'w') as f:
            f.write(requirements_txt)
        
        with open('requirements-dev.txt', 'w') as f:
            f.write(requirements_dev)
    
    def _create_root_readme(self):
        """Create root README.md."""
        content = f'''# Code Assistant

A local, AI-powered coding assistant with 3 integrated modules for specification, analysis, and execution.

## Modules

- **code_starter** - Create project specifications and generate project skeletons from pseudocode
- **code_analyzer** - Analyze code and provide insights (coming soon)
- **code_executor** - Execute and test generated code (coming soon)

## Quick Start

### 1. Clone & Setup

```bash
git clone https://github.com/{self.config['github_username']}/{self.config['github_repo_name']}.git
cd {self.config['github_repo_name']}

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate

# Install
pip install -e ".[dev]"
```

### 2. Use code_starter

```bash
python -m code_starter.starterfile_creator
```

This will guide you through:
1. Creating a project specification
2. Generating project skeleton
3. Converting pseudocode to real code

## Documentation

- [Architecture](docs/ARCHITECTURE.md)
- **Module Docs:**
  - [code_starter](code_starter/docs/README.md)
  - [code_analyzer](code_analyzer/docs/README.md) (coming soon)
  - [code_executor](code_executor/docs/README.md) (coming soon)

## Installation Options

### Option A: Python Package (Recommended)
```bash
pip install -e .
python -m code_starter.starterfile_creator
```

### Option B: Direct Scripts
```bash
python code_starter/starterfile_creator.py
```

### Option C: CLI Commands (After full setup)
```bash
code-assistant-start
```

## Development

### Running Tests

```bash
pytest
pytest --cov  # With coverage
```

### Code Quality

```bash
black .           # Format
flake8 .          # Lint
mypy .            # Type check
```

### Build & Install

```bash
make install-dev
make test
make lint
```

## Requirements

- Python 3.8+
- Optional: ollama + deepseek-coder:6.7b (for code generation)

## License

MIT License - See [LICENSE](LICENSE) file

## Author

{self.config['author_name']} ({self.config['author_email']})

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md)
'''
        with open('README.md', 'w') as f:
            f.write(content)
    
    def _create_config_structure(self):
        """Create config directory structure."""
        os.makedirs('config', exist_ok=True)
        
        # __init__.py
        with open('config/__init__.py', 'w') as f:
            f.write('"""Configuration module."""\n')
        
        # settings.py
        with open('config/settings.py', 'w') as f:
            f.write('''"""Project settings and configuration."""

# Project name
PROJECT_NAME = "code-assistant"

# Modules
MODULES = ["code_starter", "code_analyzer", "code_executor"]

# LLM Configuration
LLM_MODEL = "deepseek-coder:6.7b"
LLM_API_ENDPOINT = "http://localhost:11434"

# Default directories
DEFAULT_OUTPUT_DIR = "./generated_projects"

# Logging
LOG_LEVEL = "INFO"
''')
    
    def _create_module_placeholders(self):
        """Create placeholder modules."""
        for module_name in ['code_analyzer', 'code_executor']:
            os.makedirs(f'{module_name}/docs', exist_ok=True)
            
            # __init__.py
            with open(f'{module_name}/__init__.py', 'w') as f:
                f.write(f'"""The {module_name} module."""\n')
            
            # Main module file
            with open(f'{module_name}/{module_name.split("_")[1]}.py', 'w') as f:
                f.write(f'"""{module_name} module.\n\nComing soon...\n"""')
            
            # docs/README.md
            with open(f'{module_name}/docs/README.md', 'w') as f:
                f.write(f'# {module_name.replace("_", " ").title()}\n\nComing soon...\n')
    
    def _create_test_structure(self):
        """Create tests directory."""
        os.makedirs('tests', exist_ok=True)
        
        with open('tests/__init__.py', 'w') as f:
            f.write('"""Tests for code-assistant."""\n')
        
        with open('tests/conftest.py', 'w') as f:
            f.write('"""Pytest configuration and fixtures."""\n')
    
    def _create_shared_utilities(self):
        """Create shared utilities directory."""
        os.makedirs('shared', exist_ok=True)
        
        with open('shared/__init__.py', 'w') as f:
            f.write('"""Shared utilities across modules."""\n')
        
        with open('shared/config.py', 'w') as f:
            f.write('''"""Shared configuration utilities."""

def load_config(config_file):
    """Load configuration from file."""
    pass
''')
        
        with open('shared/utils.py', 'w') as f:
            f.write('''"""Shared utility functions."""

def format_output(content):
    """Format output content."""
    pass
''')
    
    def _create_github_workflows(self):
        """Create GitHub Actions workflows."""
        os.makedirs('.github/workflows', exist_ok=True)
        
        with open('.github/workflows/tests.yml', 'w') as f:
            f.write('''name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, 3.10, 3.11]
    
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v2
      with:
        python-version: ${{ matrix.python-version }}
    - name: Install dependencies
      run: |
        pip install -e ".[dev]"
    - name: Run tests
      run: pytest --cov
''')
    
    # ==================== PERSISTENCE ====================
    
    def save_config(self):
        """Save configuration to JSON file."""
        filename = input("Save configuration as (default: repo_config.json): ").strip() or "repo_config.json"
        
        try:
            with open(filename, 'w') as f:
                json.dump(self.config, f, indent=2)
            print(f"✓ Configuration saved to {filename}")
        except Exception as e:
            print(f"✗ Error saving: {e}")
    
    def load_config(self):
        """Load configuration from JSON file."""
        filename = input("Load configuration from (default: repo_config.json): ").strip() or "repo_config.json"
        
        try:
            with open(filename, 'r') as f:
                loaded = json.load(f)
                self.config.update(loaded)
            print(f"✓ Configuration loaded from {filename}")
        except Exception as e:
            print(f"✗ Error loading: {e}")
    
    # ==================== REPORTING ====================
    
    def print_summary(self):
        """Print comprehensive summary report."""
        print("\n" + "="*70)
        print("GITHUB REPOSITORY PLANNER - SUMMARY REPORT")
        print("="*70)
        
        print(f"\nProject: {self.config['github_repo_name']}")
        print(f"Repository: https://github.com/{self.config['github_username']}/{self.config['github_repo_name']}")
        print(f"Author: {self.config['author_name']} <{self.config['author_email']}>")
        
        print("\n" + "-"*70)
        print("CONFIGURATION SUMMARY")
        print("-"*70)
        
        settings = [
            ("Module Structure", self.config['module_structure']),
            ("Configuration Files", "Yes" if self.config['config_files'] else "No"),
            ("venv Setup", self.config['venv_setup']),
            ("Module Placeholders", "Yes" if self.config['module_placeholders'] else "No"),
            ("Testing Strategy", self.config['testing_strategy']),
            ("Documentation Location", self.config['documentation_location']),
            ("CI/CD Workflows", "Yes" if self.config['ci_cd'] else "No"),
            ("Installation Method", self.config['installation_method']),
            ("Shared Code", self.config['shared_code']),
        ]
        
        for setting, value in settings:
            print(f"  {setting:.<40} {value}")
        
        print("\n" + "-"*70)
        print("DECISIONS MADE")
        print("-"*70)
        for decision in self.decisions:
            print(f"  ✓ {decision}")
        
        print("\n" + "-"*70)
        print("NEXT STEPS")
        print("-"*70)
        print("""
  1. Review configuration above
  2. Select option 3: "Generate Repository Structure"
  3. Files will be created in current directory
  4. Review generated files
  5. Commit to git and push to GitHub
  
  Recommended next commands:
  
    git init
    git add .
    git commit -m "Initial repository structure"
    git remote add origin https://github.com/{}/{}.git
    git push -u origin main
""".format(self.config['github_username'], self.config['github_repo_name']))


def main():
    """Entry point."""
    print("\n" + "="*70)
    print("GITHUB REPOSITORY PLANNER")
    print("="*70)
    print("Setup code-assistant for GitHub distribution")
    print("="*70)
    
    planner = GitHubRepoPlanner()
    planner.main_menu()


if __name__ == '__main__':
    main()
