"""Code Documenter Module

Generates documentation files for code-assistant projects.
Creates markdown documentation in the docs/ directory.

Classes:
    CodeDocumenter: Main class for generating documentation
"""

from pathlib import Path
from typing import Dict, List, Optional
import os


class CodeDocumenter:
    """Generate documentation files for projects."""

    def __init__(self, output_dir: str = "./docs"):
        """Initialize CodeDocumenter.

        Args:
            output_dir: Directory where docs will be created (default: ./docs)
        """
        self.output_dir = Path(output_dir)
        self.docs = {}

    def create_docs_directory(self) -> str:
        """Create docs directory if it doesn't exist.

        Returns:
            Path to docs directory
        """
        self.output_dir.mkdir(parents=True, exist_ok=True)
        return str(self.output_dir)

    def write_readme(self, project_name: str, description: str, modules: List[str]) -> str:
        """Write README.md file.

        Args:
            project_name: Name of the project
            description: Project description
            modules: List of module names

        Returns:
            Path to created file
        """
        modules_text = "\n".join([f"- **{mod}**: " for mod in modules])
        module_commands = "\n".join(
            f"./scripts/run_{mod[5:] if mod.startswith('code_') else mod}.sh"
            for mod in modules
        )
        module_tree = "\n".join(f"│   ├── {mod}/" for mod in modules)

        readme_content = f'''# {project_name}

{description}

## Features

- Clean, modular structure
- Comprehensive documentation
- Testing infrastructure included
- Easy setup with shell scripts

## Quick Start

### Prerequisites

- Python 3.8+
- pip and venv

### Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd {project_name.lower().replace(' ', '_')}
   ```

2. Run the setup script:
   ```bash
   ./scripts/setup.sh
   ```

3. Activate the virtual environment:
   ```bash
   source venv/bin/activate
   ```

## Modules

{modules_text}

## Documentation

See the `docs/` directory for detailed documentation:
- `ARCHITECTURE.md` - System design and architecture
- `API.md` - API reference
- `GETTING_STARTED.md` - Getting started guide
- Module-specific guides in subdirectories

## Running the Application

### Using Interactive Menu
```bash
./scripts/run_starter.sh
```

### Running Specific Module
```bash
{module_commands}
```

## Development

### Running Tests
```bash
pytest tests/ -v
```

### Code Quality
```bash
# Format code
black .

# Lint
flake8 .

# Type checking
mypy .
```

### Installing Development Dependencies
```bash
./scripts/setup.sh  # Select yes for dev dependencies
# Or:
pip install -r requirements-dev.txt
```

## Project Structure

```
{project_name.lower().replace(' ', '_')}/
├── docs/                    # Documentation
├── scripts/                 # User-facing shell helpers
├── config/                  # Configuration files
├── ui/                      # User interface
├── src/
{module_tree}
│   ├── tools/
│   ├── shared/
│   ├── db_master_handler/
│   └── assistant_contracts/
├── tests/                   # Test suite
├── setup.py                 # Package setup
├── requirements.txt         # Dependencies
└── README.md                # This file
```

## Configuration

Configuration files are located in the `config/` directory:
- `defaults.yaml` - Default settings
- `logging_config.yaml` - Logging configuration

Create a `.env` file in the root directory for environment-specific settings (not committed to git).

## Contributing

See `docs/CONTRIBUTING.md` for guidelines on contributing to this project.

## License

This project is licensed under the MIT License - see `LICENSE` file for details.

## Support

For issues, questions, or feature requests, please open an issue on GitHub.

## Authors

- Your Name

## Changelog

See `CHANGELOG.md` for version history and release notes.
'''
        doc_path = self.output_dir / "README.md"
        doc_path.write_text(readme_content)
        return str(doc_path)

    def write_architecture_docs(self, modules: List[str]) -> str:
        """Write ARCHITECTURE.md file.

        Args:
            modules: List of module names

        Returns:
            Path to created file
        """
        modules_section = "\n".join(
            [f"- **{mod}**: {mod.capitalize()} module" for mod in modules]
        )
        module_tree = "\n".join(f"    ├── {mod}/" for mod in modules)

        architecture_content = f'''# Architecture

## System Overview

This project follows a modular architecture with shared utilities.

## Modules

{modules_section}

## Architecture Diagram

```
┌─────────────────────────────────┐
│     User Interface              │
│   (CLI / Shell Scripts)         │
└────────────┬────────────────────┘
             │
    ┌────────┼────────┐
    │        │        │
    ▼        ▼        ▼
{chr(10).join([f'┌──────────────┐' for _ in modules[:3]])}
{chr(10).join([f'│  {m.ljust(10)}  │' for m in modules])}
{chr(10).join([f'└──────────────┘' for _ in modules[:3]])}
    │        │        │
    └────────┼────────┘
             │
        ┌────▼────┐
        │ Shared  │
        │Utilities│
        └─────────┘
```

## Directory Structure

```
project/
├── docs/                    # Documentation
├── scripts/                 # User-facing shell helpers
├── config/                  # Configuration files
├── ui/                      # User interface
├── src/
{module_tree}
│   ├── tools/
│   ├── shared/
│   ├── db_master_handler/
│   └── assistant_contracts/
└── tests/                   # Test suite
```

## Data Flow

```
User Input
    ↓
Module Processing
    ↓
Shared Utilities
  ├─ Config Management
  ├─ Logging
  ├─ LLM Interface
  └─ Utilities
    ↓
Output/Results
```

## Design Patterns

- **Modular Design**: Each module operates independently
- **Shared Core**: Common functionality in shared/ directory
- **Configuration Management**: YAML-based settings
- **Error Handling**: Comprehensive error handling throughout

## Development Workflow

1. Create specification
2. Generate project structure
3. Implement features
4. Test thoroughly
5. Document changes
6. Deploy

## Performance Considerations

- Lazy loading of modules
- Efficient file operations
- Minimal dependencies
- Local processing (no cloud dependencies)

## Security

- No hardcoded credentials
- Environment variable support
- Input validation
- Error safe operations

## Future Enhancements

- Web UI
- Additional module support
- Enhanced reporting
- Integration with external tools
'''
        doc_path = self.output_dir / "ARCHITECTURE.md"
        doc_path.write_text(architecture_content)
        return str(doc_path)

    def write_api_docs(self, modules: List[str]) -> str:
        """Write API.md file.

        Args:
            modules: List of module names

        Returns:
            Path to created file
        """
        api_content = f'''# API Reference

## Overview

Complete API reference for all modules.

## Modules

{chr(10).join([f'### {m.capitalize()}' + chr(10) + f'See `docs/{m}/README.md` for detailed API documentation.' for m in modules])}

## Shared Utilities

### Configuration (src/shared/config.py)

```python
from shared.config import load_config, get_config

# Load configuration
config = load_config('config/defaults.yaml')

# Get specific value
value = get_config('key.subkey', default='default_value')
```

### Logging (src/shared/logging.py)

```python
from shared.logging import get_logger, setup_logging

# Setup logging
setup_logging('config/logging_config.yaml')

# Get logger
logger = get_logger(__name__)
logger.info("Message")
```

### Utilities (src/shared/utils.py)

```python
from shared.utils import read_file, write_file, ensure_directory

# File operations
content = read_file('path/to/file.txt')
write_file('path/to/output.txt', content)
ensure_directory('path/to/directory')
```

## Common Patterns

### Error Handling

All modules follow consistent error handling:

```python
try:
    result = do_something()
except FileNotFoundError:
    # Handle missing file
except ValueError as e:
    # Handle invalid value
```

### Configuration

Access configuration consistently:

```python
from shared.config import get_config

timeout = get_config('llm.timeout', default=300)
model = get_config('llm.model', default='default-model')
```

### Logging

Use logging throughout:

```python
from shared.logging import get_logger

logger = get_logger(__name__)
logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
```

## Best Practices

1. **Always use shared utilities** for common operations
2. **Validate inputs** before processing
3. **Use proper logging** for debugging
4. **Handle errors gracefully** with informative messages
5. **Document public APIs** with docstrings
6. **Follow PEP 8** style guide

## Testing

All modules should include unit tests:

```bash
pytest tests/ -v
pytest tests/ --cov=module_name
```

## Examples

See the `docs/` subdirectories for module-specific examples.
'''
        doc_path = self.output_dir / "API.md"
        doc_path.write_text(api_content)
        return str(doc_path)

    def write_getting_started(self, project_name: str, modules: List[str]) -> str:
        """Write GETTING_STARTED.md file.

        Args:
            project_name: Name of the project
            modules: List of module names

        Returns:
            Path to created file
        """
        getting_started_content = f'''# Getting Started

## Prerequisites

- Python 3.8 or higher
- pip and venv
- Basic knowledge of command line

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd {project_name.lower().replace(' ', '_')}
```

### 2. Run Setup Script

```bash
chmod +x scripts/*.sh          # Make scripts executable
./scripts/setup.sh             # Run setup
```

The setup script will:
- Check Python 3 installation
- Create virtual environment
- Install dependencies
- Verify installation

### 3. Activate Virtual Environment (Optional)

If not using the shell scripts:

```bash
source venv/bin/activate
```

## First Steps

### Using the Interactive Menu

```bash
./scripts/run_starter.sh
```

This opens an interactive menu where you can:
1. Create new projects
2. Generate code structures
3. View project specifications

### Viewing Project Structure

```bash
./scripts/run_starter.sh --status
```

Shows the current environment status.

### Creating a New Project

```bash
./scripts/run_starter.sh --create
```

Follow the prompts to create a new project:
1. Enter project name
2. Enter description
3. Specify modules
4. Add dependencies

### Exploring Documentation

```bash
# View main documentation
cat docs/README.md

# View architecture
cat docs/ARCHITECTURE.md

# View API reference
cat docs/API.md
```

## Common Tasks

### Update Dependencies

```bash
./scripts/setup.sh
# Or if venv already exists:
pip install -r requirements.txt
```

### Run Tests

```bash
pytest tests/ -v
```

### Format Code

```bash
black .
```

### Check Code Quality

```bash
flake8 .
mypy .
```

### Create a Project

```bash
./scripts/run_starter.sh
# Or from CLI:
./scripts/run_starter.sh --create
```

## Troubleshooting

### Python not found

```bash
# Check Python installation
python3 --version

# If not installed, install Python 3.8+
# Ubuntu/Debian:
sudo apt-get install python3 python3-venv

# macOS:
brew install python3
```

### Permission denied

```bash
# Make scripts executable
chmod +x scripts/*.sh
```

### Module not found

```bash
# Reinstall dependencies
./scripts/setup.sh
# Or:
pip install -r requirements.txt
```

### Virtual environment issues

```bash
# Remove and recreate venv
rm -rf venv
./scripts/setup.sh
```

## Next Steps

1. **Read the documentation** in `docs/`
2. **Explore the code** in the module directories
3. **Run examples** to get familiar with functionality
4. **Check the API** reference for detailed information
5. **Join development** by contributing improvements

## Learning Path

1. Start: Read `README.md`
2. Setup: Run `./scripts/setup.sh`
3. Explore: Run `./scripts/run_starter.sh`
4. Understand: Read `docs/ARCHITECTURE.md`
5. Learn: Check `docs/API.md`
6. Contribute: See `docs/CONTRIBUTING.md`

## Additional Resources

- [Python Documentation](https://docs.python.org/3/)
- [Bash Scripting Guide](https://www.gnu.org/software/bash/manual/)
- [Git Documentation](https://git-scm.com/doc)

## Support

For help:
1. Check this guide
2. Read module documentation
3. Look at examples
4. Open an issue on GitHub

Happy coding! 🚀
'''
        doc_path = self.output_dir / "GETTING_STARTED.md"
        doc_path.write_text(getting_started_content)
        return str(doc_path)

    def write_contributing_guide(self) -> str:
        """Write CONTRIBUTING.md file.

        Returns:
            Path to created file
        """
        contributing_content = '''# Contributing

Thank you for your interest in contributing!

## Getting Started

1. Fork the repository
2. Clone your fork
3. Create a feature branch: `git checkout -b feature/your-feature`
4. Make your changes
5. Write tests for new functionality
6. Ensure all tests pass
7. Submit a pull request

## Code Style

- Follow PEP 8
- Use descriptive variable names
- Add docstrings to functions and classes
- Include type hints where practical
- Use black for formatting

## Testing

- Write unit tests for new functions
- Ensure all tests pass: `pytest tests/ -v`
- Aim for >80% code coverage
- Test both happy path and error cases

## Documentation

- Update README.md if adding features
- Add docstrings to new functions
- Update ARCHITECTURE.md for structural changes
- Include usage examples

## Commit Messages

- Use clear, descriptive messages
- Reference issues when applicable
- Follow conventional commits format:
  - `feat:` for new features
  - `fix:` for bug fixes
  - `docs:` for documentation
  - `test:` for tests
  - `refactor:` for refactoring

## Pull Request Process

1. Update documentation
2. Add tests for new functionality
3. Ensure all tests pass
4. Update CHANGELOG.md
5. Submit PR with clear description
6. Address review feedback
7. Maintain clean commit history

## Code Review

- Be respectful and constructive
- Suggest improvements kindly
- Ask clarifying questions
- Approve when satisfied

## Questions?

- Open an issue for discussion
- Contact maintainers
- Check existing documentation

Thank you for contributing! 🙏
'''
        doc_path = self.output_dir / "CONTRIBUTING.md"
        doc_path.write_text(contributing_content)
        return str(doc_path)

    def create_module_docs(self, module_name: str) -> str:
        """Create documentation directory for a module.

        Args:
            module_name: Name of the module

        Returns:
            Path to module docs directory
        """
        module_docs_dir = self.output_dir / module_name
        module_docs_dir.mkdir(parents=True, exist_ok=True)

        # Create module README
        module_readme = f'''# {module_name.capitalize()} Module

Documentation for the {module_name} module.

## Overview

This module provides [description of functionality].

## Usage

```python
from {module_name} import SomeClass

obj = SomeClass()
result = obj.do_something()
```

## API Reference

See `../API.md` for complete API reference.

## Examples

[Add usage examples here]

## Contributing

See `../CONTRIBUTING.md` for contribution guidelines.
'''
        readme_path = module_docs_dir / "README.md"
        readme_path.write_text(module_readme)
        return str(module_docs_dir)

    def generate_all_docs(
        self,
        project_name: str,
        description: str,
        modules: Optional[List[str]] = None,
    ) -> Dict[str, str]:
        """Generate all documentation files.

        Args:
            project_name: Project name
            description: Project description
            modules: List of module names

        Returns:
            Dictionary mapping doc names to their paths
        """
        if modules is None:
            modules = ["starter", "debugger", "patcher"]

        # Create docs directory
        self.create_docs_directory()

        # Write main documentation files
        self.docs["README.md"] = self.write_readme(project_name, description, modules)
        self.docs["ARCHITECTURE.md"] = self.write_architecture_docs(modules)
        self.docs["API.md"] = self.write_api_docs(modules)
        self.docs["GETTING_STARTED.md"] = self.write_getting_started(
            project_name, modules
        )
        self.docs["CONTRIBUTING.md"] = self.write_contributing_guide()

        # Create module documentation directories
        for module in modules:
            self.create_module_docs(module)

        return self.docs

    def generate_to_project(
        self,
        project_dir: str,
        project_name: str,
        description: str,
        modules: Optional[List[str]] = None,
    ) -> Dict[str, str]:
        """Generate docs for a project.

        Args:
            project_dir: Project directory path
            project_name: Project name
            description: Project description
            modules: List of module names

        Returns:
            Dictionary mapping doc names to their paths
        """
        project_path = Path(project_dir)
        docs_dir = project_path / "docs"
        self.output_dir = docs_dir

        return self.generate_all_docs(project_name, description, modules)

    def get_doc_count(self) -> int:
        """Get number of generated documentation files.

        Returns:
            Number of docs
        """
        return len(self.docs)

    def list_generated_docs(self) -> List[str]:
        """List all generated documentation file names.

        Returns:
            List of doc names
        """
        return list(self.docs.keys())

    def get_doc_info(self) -> Dict[str, Dict[str, str]]:
        """Get information about generated documentation.

        Returns:
            Dictionary with doc metadata
        """
        info = {}
        for name, path in self.docs.items():
            doc_path = Path(path)
            if doc_path.exists():
                size = doc_path.stat().st_size
                info[name] = {
                    "path": path,
                    "size": f"{size / 1024:.1f} KB",
                }
        return info


if __name__ == "__main__":
    # Example usage
    documenter = CodeDocumenter("./test_docs")
    docs = documenter.generate_all_docs(
        "Test Project",
        "A test project for documentation generation",
        ["starter", "debugger", "patcher"],
    )

    print("Generated Documentation:")
    for name, path in docs.items():
        print(f"  ✓ {name} → {path}")

    print(f"\nTotal docs: {documenter.get_doc_count()}")
    print("\nDocumentation Info:")
    for name, info in documenter.get_doc_info().items():
        print(f"  {name}: {info['size']}")
