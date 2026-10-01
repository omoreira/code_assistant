# Architecture - Code Assistant

## System Overview

Code Assistant is a modular Python package. Each module owns one stage of the
workflow, while `shared/` provides cross-cutting services such as LLM access.

The main flow is: `code_starter` creates projects; `code_converter` turns long
research notes into `patch.pseudo`; `code_debugger` analyzes code and applies
patches; `code_refractor` handles structural changes such as moving or renaming
modules and updating imports. The `scripts/longtext2pseudo` command invokes the
notes converter. Patch application and structural refactoring are separate
responsibilities.

For generated repositories, `code_starter.github_repo_planner` creates
`setup.py` and `pyproject.toml` by default. Its interactive setup can also
generate a `Dockerfile` and `.dockerignore` when Docker support is selected.
`code_converter` uses the same modular design principle in generated
specifications: its `src/` packages come from user-designed tasks, while
shared utilities remain in shared packages; it does not copy this assistant's
own module names into a future project.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│              CLI, Scripts, or Python API                     │
└────────────────────┬────────────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
        ▼            ▼            ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│code_starter  │ │code_converter│ │code_debugger │ │code_refractor│
│Project/code  │ │Notes → pseudo│ │Analysis and  │ │Structural    │
│generation    │ │conversion    │ │patch apply   │ │refactoring   │
└──────┬───────┘ └──────┬───────┘ └──────┬───────┘ └──────┬───────┘
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

### 2. **code_converter** - Long Text to Pseudocode

**Purpose**: Turn UTF-8 research notes into a `patch.pseudo` proposal. The
`LongContextReader` summarizes bounded chunks through the shared LLM interface
and asks for `#PATCHES` and `#NEW SCRIPTS` sections. `scripts/longtext2pseudo`
is its command-line entry point.

### 3. **code_debugger** - Code Analysis, Debugging & Patch Application

**Purpose**: Provide debugging and analysis capabilities for existing code.

**Components**:
- Code analysis tools
- Error detection and suggestion
- Performance profiling
- Testing utilities
- `patch_file.py` parses and applies unified diff entries and creates new files

**Planned Workflow**:
1. Load existing project code
2. Analyze code structure and patterns
3. Identify potential issues
4. Generate debugging suggestions
5. Propose fixes and optimizations

### 4. **code_refractor** - Structural Refactoring

**Purpose**: Safely move or rename code elements and update dependent imports,
paths, configuration, and documentation.

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

### 5. **ui_builder** - Target Repository UI Generation

**Purpose**: Help users create a Streamlit or React + TypeScript application
inside the generated project's root `ui/` directory. The package lives under
this assistant's `src/ui_builder/`; generated UI files belong to the target
repository.

### 6. **repo_documenter** - Target Repository Documentation

**Purpose**: Generate or update project documentation inside the generated
project's root `docs/` directory. The package lives under this assistant's
`src/repo_documenter/`; documentation output belongs to the target repository.

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
├── docs/                    # Project and module documentation
├── scripts/                 # User-facing shell helpers
├── config/                  # Runtime and logging configuration
├── ui/                      # Streamlit or other user interface
├── src/
│   ├── code_starter/        # Project creation and code generation
│   ├── code_converter/      # Long research text to pseudocode
│   ├── code_debugger/       # Debugging module
│   ├── code_refractor/      # Refactoring module
│   ├── ui_builder/          # Generate apps in a target repo's root ui/
│   ├── repo_documenter/     # Generate docs in a target repo's root docs/
│   ├── tools/               # Reusable technical tools
│   ├── shared/              # Shared Python utilities
│   ├── db_master_handler/   # Shared database infrastructure
│   └── assistant_contracts/ # LLM contracts and schemas
├── tests/
├── setup.py
├── pyproject.toml
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
