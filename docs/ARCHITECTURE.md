# Architecture - Code Assistant

## System Overview

Code Assistant is a modular Python package designed to provide intelligent coding assistance through local LLM integration. The system is built around three main modules that work together with shared utilities and centralized configuration.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    User Interface                            │
│         (CLI, Scripts, or Python API)                        │
└────────────────────┬────────────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
        ▼            ▼            ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│code_starter  │ │code_debugger │ │ code_patcher │
│              │ │              │ │              │
│• Project     │ │• Analysis    │ │• Refactoring │
│  Creation    │ │• Debugging   │ │• Patching    │
│• Scaffolding │ │• Profiling   │ │• Testing     │
│• Code Gen    │ │• Suggestions │ │• Validation  │
└──────┬───────┘ └──────┬───────┘ └──────┬───────┘
       │                │                │
       └────────────────┼────────────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
        ▼               ▼               ▼
    ┌────────────┐ ┌────────────┐ ┌────────────┐
    │  Config    │ │  Logging   │ │    LLM     │
    │ (defaults. │ │  (logging_ │ │ Interface  │
    │   yaml)    │ │ config.yml)│ │ (ollama)   │
    └────────────┘ └────────────┘ └────────────┘
              ▲             ▲             ▲
              └─────────────┼─────────────┘
                            │
                    ┌───────▼────────┐
                    │  shared/       │
                    │  utilities     │
                    │  (config.py,   │
                    │   logging.py,  │
                    │   llm.py,      │
                    │   utils.py)    │
                    └────────────────┘
```

## Module Breakdown

### 1. **code_starter** - Project Creation & Code Generation

**Purpose**: Interactive tool for starting new projects and generating code.

**Components**:
- `starterfile_creator.py` - Interactive specification builder
- `blueprint_renderer.py` - Directory structure generator
- `pseudocode_renderer.py` - Pseudocode to Python converter
- `github_repo_planner.py` - GitHub repository setup automation

**Workflow**:
1. User defines project specification (interactive)
2. Create starterfile.pseudo with project details
3. Generate directory blueprint from starterfile
4. Generate skeleton code from pseudocode templates
5. Create GitHub-ready repository structure

**Key Features**:
- Interactive menu-driven interface
- Tree-based specification format (.pseudo files)
- Automatic directory structure generation
- AI-assisted code generation (via ollama)
- GitHub repository scaffolding

### 2. **code_debugger** - Code Analysis & Debugging

**Purpose**: Provide debugging and analysis capabilities for existing code.

**Planned Components**:
- Code analysis tools
- Error detection and suggestion
- Performance profiling
- Testing utilities

**Planned Workflow**:
1. Load existing project code
2. Analyze code structure and patterns
3. Identify potential issues
4. Generate debugging suggestions
5. Propose fixes and optimizations

### 3. **code_patcher** - Code Refactoring & Patching

**Purpose**: Automated code patching, refactoring, and improvements.

**Planned Components**:
- Code transformation tools
- Refactoring suggestions
- Automated patch generation
- Version compatibility handling

**Planned Workflow**:
1. Analyze code for improvement opportunities
2. Generate patch suggestions
3. Apply patches with user approval
4. Validate changes with tests
5. Generate change documentation

## Shared Utilities

The `shared/` directory provides common functionality for all modules:

### `config.py` - Configuration Management
- Load YAML configuration files
- Override with environment variables
- Provide consistent config interface across modules

### `logging.py` - Logging Utilities
- Configure Python logging from YAML
- Set up rotating file handlers
- Provide module-specific loggers

### `llm.py` - LLM Interface
- Abstract LLM provider interface
- Manage ollama connections
- Handle prompts and responses
- Implement retry logic

### `utils.py` - General Utilities
- Text formatting and validation
- File operations
- Common helper functions

### `constants.py` - Project Constants
- Project metadata
- Default paths and settings
- Supported file types and patterns

## Data Flow

### Code Starter - Project Creation Flow

```
User Input
    ↓
StarterFileCreator (interactive)
    ↓
starterfile.pseudo (specification)
    ↓
BlueprintRenderer (parse specification)
    ↓
Directory Structure Created
    ↓
PseudocodeRenderer (convert pseudocode)
    ↓
Python Code Generated
    ↓
GitHubRepoPlanner (setup repo)
    ↓
GitHub-Ready Project
```

### LLM Integration Flow

```
Module Needs LLM Response
    ↓
Call shared/llm.py:LLMInterface
    ↓
Format Prompt
    ↓
Query ollama API (localhost:11434)
    ↓
Parse Response
    ↓
Return Result to Module
    ↓
Module Processes and Uses Result
```

### Configuration Flow

```
Application Start
    ↓
shared/config.py:load_config()
    ↓
Load defaults.yaml
    ↓
Load .env environment variables
    ↓
Override with CLI arguments
    ↓
Provide merged config to modules
    ↓
Each module accesses via shared interface
```

## Design Patterns

### 1. **Module Independence with Shared Core**
- Each module can work independently
- All modules access shared utilities through common interface
- Reduces code duplication
- Enables easy testing of individual modules

### 2. **Configuration Inheritance**
- Base configuration in `defaults.yaml`
- Environment-specific overrides via `.env`
- Module-specific settings via module config files
- CLI arguments override all

### 3. **Plugin Architecture (Future)**
- Modules can register handlers for specific file types
- Easy to add new modules without modifying core
- Extensible without breaking compatibility

### 4. **LLM Abstraction**
- Single interface for all LLM interactions
- Easy to swap providers (ollama, OpenAI, etc.)
- Centralized prompt management
- Consistent error handling

## Technology Stack

- **Language**: Python 3.8+
- **Configuration**: YAML (PyYAML)
- **LLM**: ollama with deepseek-coder:6.7b
- **Testing**: pytest
- **Code Quality**: black, flake8, mypy, pylint
- **Packaging**: setuptools, pip

## Directory Structure

```
code_assistant/
├── code_starter/           # Project startup module
│   ├── __init__.py
│   ├── starterfile_creator.py
│   ├── blueprint_renderer.py
│   ├── pseudocode_renderer.py
│   └── github_repo_planner.py
├── code_debugger/          # Debugging module
│   └── __init__.py
├── code_patcher/           # Patching module
│   └── __init__.py
├── shared/                 # Shared utilities
│   ├── __init__.py
│   ├── config.py
│   ├── logging.py
│   ├── llm.py
│   ├── utils.py
│   └── constants.py
├── config/                 # Configuration files
│   ├── defaults.yaml
│   └── logging_config.yaml
├── docs/                   # Documentation
│   ├── ARCHITECTURE.md     # This file
│   ├── API.md
│   ├── CONTRIBUTING.md
│   ├── code_starter/
│   ├── code_debugger/
│   └── code_patcher/
├── tests/                  # Test suite
│   ├── unit/
│   ├── integration/
│   └── conftest.py
├── .gitignore
├── LICENSE
├── setup.py
├── pyproject.toml
├── requirements.txt
├── requirements-dev.txt
└── README.md
```

## External Dependencies

### Runtime
- `pyyaml` - YAML configuration parsing
- `requests` - HTTP requests (for LLM API)

### Development
- `pytest` - Testing framework
- `pytest-cov` - Coverage reporting
- `black` - Code formatting
- `flake8` - Linting
- `mypy` - Type checking
- `pylint` - Additional linting

## Deployment Models

### Model 1: Local Development
- Install with `pip install -e ".[dev]"`
- Run tools locally
- Use local ollama instance

### Model 2: Distribution
- Package as pip-installable module
- Users install with `pip install code-assistant`
- Can use remote LLM or local ollama

### Model 3: Container (Future)
- Docker image with ollama included
- Single command to start
- Pre-configured environment

## Extension Points

1. **Add New Module**: Create `code_xyz/` directory with proper structure
2. **Add New Handler**: Register in module's config
3. **Add New LLM Provider**: Implement in `shared/llm.py`
4. **Add Utilities**: Add to `shared/utils.py`
5. **Custom Configuration**: Extend `defaults.yaml`

## Security Considerations

1. **No Cloud Dependencies**: All processing local
2. **Configuration Isolation**: `.env` files not version controlled
3. **Input Validation**: All user inputs validated
4. **Logging**: Sensitive data excluded from logs
5. **Dependency Scanning**: Regular dependency updates

## Performance Considerations

1. **Lazy Loading**: Modules loaded on demand
2. **LLM Caching**: Cache LLM responses when appropriate
3. **Parallel Processing**: Use multiprocessing for I/O-bound tasks
4. **Memory Management**: Stream large files instead of loading fully

## Future Roadmap

1. **Web Interface**: Flask/FastAPI-based UI
2. **More LLM Providers**: Support for GPT, Claude, etc.
3. **Plugin System**: Enable third-party extensions
4. **Cloud Deployment**: AWS/Azure/GCP templates
5. **Monitoring**: Integration with monitoring services
6. **Batch Processing**: Process multiple projects at once
7. **Version Control**: Git integration for version management

---

**For more information:**
- See [README.md](../README.md) for overview
- See [API.md](API.md) for API documentation
- See module-specific docs in module directories
