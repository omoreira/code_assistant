# Code Assistant

A comprehensive local coding assistant system with three integrated modules for code generation, debugging, and patching.

- **Author:** Olga Moreira
- **License:** MIT
- **Repository:** https://github.com/omoreira/code_assistant
- **Objective:** This app aims to provide a local, low-resource coding assistant. Users should create a starter file with a repomap and pseudocode for each script file.
- **Assistive Tools and LLMs:** This code was developed from author's pseudocode. VS Code Continue (LLM: Claude 3 Haiku) was used to auto-convert pseudocode into Python-based modules in a similar process that this app will offer. For further information, see AI Assistance Disclosure below.
- **Status:** Manual-auditing of the generated base code (i.e., the human behind the machine is manually auditing each piece of code and documentation generated). Assistant testing phase. This base code is still in the initial phase of development; use with caution!
- **Last Updated by Human:** 2026-09-28

## Overview

Code Assistant is a modular Python package that leverages local LLM (ollama) to provide intelligent coding assistance without cloud dependencies. It consists of four main components:

### **code_starter**
Interactive tool for starting new projects. Creates complete project structures from simple specifications.

- **starterfile_creator.py**: Interactive project specification builder
- **blueprint_renderer.py**: Generate directory skeletons from specifications
- **pseudocode_renderer.py**: Convert pseudocode to working Python code
- **github_repo_planner.py**: Automate GitHub repository setup
- **scripts_writer.py**: Automated shell script generation
- **code_documenter.py**: Automated documentation generation

### **code_debugger** (In Development)
Tools for analyzing and debugging existing code with AI assistance.

### **code_patcher** (In Development)
Automated code patching and patching utilities.

### **code_refractor** (New)
Intelligent code refactoring with automatic path and name verification.
Ensures that refactoring operations don't break imports, paths, or dependencies.

- **refactoring_verifier.py**: Verify refactoring safety before execution
- **code_refactorer.py**: Execute refactoring with automatic updates
- **path_resolver.py**: Resolve and validate all paths after refactoring
- **dependency_mapper.py**: Map code dependencies to analyze impact

## Quick Start

### Prerequisites

- Python 3.8 or higher
- ollama with `deepseek-coder:6.7b` model (for LLM features)
- pip and venv

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/omoreira/code_assistant.git
   cd code_assistant
   ```

2. **Create and activate virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install in development mode:**
   ```bash
   pip install -e ".[dev]"
   ```

### First Steps

Start with the `code_starter` module:

```bash
# View available tools
   python -c "from code_starter import starterfile_creator; help(starterfile_creator)"

# Run the interactive project creator
   python src/code_starter/starterfile_creator.py
```

For detailed documentation, see [docs/code_starter/README.md](docs/code_starter/README.md).

The starter creates the common `docs/`, `scripts/`, `config/`, `ui/`, and
`src/` layout automatically. Users enter module names under `src/` in the
REPOMAP; script paths and their pseudocode are defined separately in the
PSEUDOCODE section.

## Project Structure

```
code_assistant/
├── docs/                   # Project and module documentation
├── scripts/                # User-facing shell helpers
├── config/                 # Runtime and logging configuration
├── ui/                     # Streamlit or other user interface
├── src/
│   ├── code_starter/       # Project creation and code generation
│   ├── code_debugger/      # Code debugging module
│   ├── code_patcher/       # Code patching module
│   ├── code_refractor/     # Refactoring verification module
│   ├── tools/              # Reusable technical tools
│   ├── shared/             # Shared Python utilities
│   ├── db_master_handler/  # Shared database infrastructure
│   └── assistant_contracts/ # LLM contracts and schemas
├── tests/                  # Automated tests
├── setup.py                # Package configuration
└── pyproject.toml
```

## Documentation

- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** - System design and module interaction
- **[API.md](docs/API.md)** - Complete API reference
- **[CONTRIBUTING.md](docs/CONTRIBUTING.md)** - Contribution guidelines
- **[code_starter Documentation](docs/code_starter/README.md)** - Starter module guide
- **[code_debugger Documentation](docs/code_debugger/README.md)** - Debugger module guide
- **[code_patcher Documentation](docs/code_patcher/README.md)** - Patcher module guide
- **[code_refractor Documentation](docs/code_refractor/README.md)** - Refactoring verification guide
- **[SCRIPTS_GUIDE.md](docs/SCRIPTS_GUIDE.md)** - Shell scripts reference

## Configuration

### Default Configuration

Edit `config/defaults.yaml` to customize:
- Project name and version
- LLM model and endpoint
- Output directories
- Module settings

### Environment Variables

Copy `.env.example` to `.env` and customize:
```bash
cp .env.example .env
```

## Development

### Running Tests

```bash
# Run all tests
make test

# Run with coverage report
make test-cov

# Run specific test file
pytest tests/unit/test_code_starter.py -v
```

### Code Quality

```bash
# Format code
make format

# Run linting
make lint

# Type checking
mypy shared code_starter
```

### Common Commands

```bash
# Create virtual environment
make venv

# Install dependencies
make install
make install-dev

# Clean cache and build files
make clean
```

See `make help` for all available commands.

## LLM Setup

This project uses ollama with the `deepseek-coder:6.7b` model. 

### Setup ollama:

```bash
# Install ollama (https://ollama.ai)
# Pull the deepseek-coder model
ollama pull deepseek-coder:6.7b

# Start ollama service
ollama serve
```

The default API endpoint is `http://localhost:11434`. You can change this in `config/defaults.yaml` or `.env`.

## Usage Examples

### Example 1: Create a New Project

```python
from code_starter.starterfile_creator import StarterFileCreator

creator = StarterFileCreator()
creator.run_interactive()
```

### Example 2: Generate Project Blueprint

```python
from code_starter.blueprint_renderer import BlueprintRenderer

renderer = BlueprintRenderer()
renderer.render_blueprint("starterfile.pseudo", "output_dir")
```

### Example 3: Convert Pseudocode to Python

```python
from code_starter.pseudocode_renderer import PseudocodeRenderer

renderer = PseudocodeRenderer()
code = renderer.render_from_file("pseudocode.txt")
print(code)
```

## Troubleshooting

### Issue: Cannot import modules

**Solution:** Ensure you've installed the package in development mode:
```bash
pip install -e .
```

### Issue: ollama connection error

**Solution:** Ensure ollama is running:
```bash
ollama serve
```

Check that the endpoint in `config/defaults.yaml` matches your setup.

### Issue: YAML parsing error

**Solution:** Ensure `pyyaml` is installed:
```bash
pip install pyyaml
```

## Contributing

See [CONTRIBUTING.md](docs/CONTRIBUTING.md) for guidelines on:
- Setting up your development environment
- Code style requirements
- Testing and submitting changes
- Adding new features

## License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

## Support

For issues, questions, or feature requests:
- Open an issue: https://github.com/omoreira/code_assistant/issues
- Check documentation: https://github.com/omoreira/code_assistant/tree/main/docs
- Contact: olga.moreira@gmail.com


## Changelog

See [CHANGELOG.md](docs/CHANGELOG.md) for version history and release notes.

---

## AI Disclosure Assistance

The development of this project involved the use of AI tools, including VS Code Continue (Claude 3 Haiku) and GitHub Copilot in the same spirit as any modern development environment might use IDE code completion, search engines, or documentation assistants.

These tools were used for:

- Generating boilerplate code and debugging suggestions
- Refining documentation and organizing materials

However, all architectural decisions, design logic, modular framework, and core vision were conceived and guided by the human creator (Olga Moreira). This project reflects years of research into low-resource coding assistance, modular and decentralized design principles.

**This disclosure is offered in the interest of transparency and to acknowledge that while AI can support structured thinking and development, it does not replace human intent, authorship, or ethical responsibility.**
