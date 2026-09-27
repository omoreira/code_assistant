# API Reference - Code Assistant

Complete API reference for all modules in the code-assistant package.

## Table of Contents

1. [code_starter](#code_starter)
2. [code_debugger](#code_debugger)
3. [code_patcher](#code_patcher)
4. [shared](#shared-utilities)

---

## code_starter

### StarterFileCreator

Main class for interactive project specification creation.

#### Methods

**`__init__(output_dir="./output")`**
- Initialize the creator with optional output directory
- Parameters:
  - `output_dir` (str): Directory for output files

**`run_interactive()`**
- Start interactive menu for project specification
- Returns: None
- Side effects: Creates starterfile.pseudo file

**`create_project_spec(name, description, modules, dependencies)`**
- Programmatically create project specification
- Parameters:
  - `name` (str): Project name
  - `description` (str): Project description
  - `modules` (list): List of module names
  - `dependencies` (list): List of dependencies
- Returns: dict with project specification

**`save_spec(spec, filename)`**
- Save specification to file
- Parameters:
  - `spec` (dict): Project specification
  - `filename` (str): Output filename
- Returns: str (path to saved file)

### BlueprintRenderer

Generate directory structures from starterfile specifications.

#### Methods

**`__init__(source_file="starterfile.pseudo")`**
- Initialize blueprint renderer
- Parameters:
  - `source_file` (str): Path to starterfile.pseudo

**`parse_blueprint()`**
- Parse the starterfile.pseudo specification
- Returns: dict representing project structure

**`render_blueprint(output_dir="./blueprint")`**
- Create actual directory structure
- Parameters:
  - `output_dir` (str): Base directory to create structure in
- Returns: str (path to created structure)

**`get_directory_tree()`**
- Get the parsed directory structure as a tree
- Returns: dict with tree representation

### PseudocodeRenderer

Convert pseudocode specifications to Python code.

#### Methods

**`__init__(llm_interface=None)`**
- Initialize pseudocode renderer
- Parameters:
  - `llm_interface` (optional): LLM interface for code generation

**`render_from_file(filename)`**
- Render pseudocode from file to Python code
- Parameters:
  - `filename` (str): Path to pseudocode file
- Returns: str (generated Python code)

**`render_from_string(pseudocode_text)`**
- Render pseudocode from string to Python code
- Parameters:
  - `pseudocode_text` (str): Pseudocode content
- Returns: str (generated Python code)

**`save_code(code, output_file)`**
- Save generated code to file
- Parameters:
  - `code` (str): Generated code
  - `output_file` (str): Output file path
- Returns: str (path to saved file)

### GitHubRepoPlanner

Automate GitHub repository structure generation.

#### Methods

**`__init__()`**
- Initialize GitHub repo planner
- No parameters

**`answer_questions()`**
- Guide through 10-question implementation questionnaire
- Returns: dict with all answers

**`quick_setup()`**
- Use recommended defaults for quick setup
- Returns: dict with preset configuration

**`manual_config()`**
- Manually edit individual settings
- Returns: dict with edited configuration

**`generate_structure(config)`**
- Create all repository files based on configuration
- Parameters:
  - `config` (dict): Configuration from answer_questions()
- Returns: dict with created files summary

**`save_config(config, filename)`**
- Save configuration to JSON for later use
- Parameters:
  - `config` (dict): Configuration to save
  - `filename` (str): Output JSON filename
- Returns: str (path to saved file)

**`load_config(filename)`**
- Load previously saved configuration
- Parameters:
  - `filename` (str): Path to JSON config file
- Returns: dict with loaded configuration

**`print_summary(config)`**
- Print summary of configuration
- Parameters:
  - `config` (dict): Configuration to summarize
- Returns: None (prints to stdout)

---

## code_debugger

*Currently under development. API will be added as features are implemented.*

---

## code_patcher

*Currently under development. API will be added as features are implemented.*

---

## shared (Utilities)

### config

Configuration management utilities.

**`load_config(config_file='config/defaults.yaml')`**
- Load configuration from YAML file
- Parameters:
  - `config_file` (str): Path to YAML config file
- Returns: dict with configuration
- Raises: FileNotFoundError if config file not found

**`load_env_config()`**
- Load configuration from environment variables
- Returns: dict with environment variable settings
- Note: Looks for variables prefixed with APP_

**`merge_configs(*configs)`**
- Merge multiple configuration dictionaries
- Parameters:
  - `*configs`: Variable number of config dicts
- Returns: Merged dict (later configs override earlier ones)

**`get_config(key, default=None)`**
- Get single configuration value
- Parameters:
  - `key` (str): Configuration key (supports dot notation: "section.key")
  - `default`: Default value if key not found
- Returns: Configuration value or default

### logging

Logging utilities for all modules.

**`setup_logging(config_file='config/logging_config.yaml')`**
- Configure Python logging from YAML file
- Parameters:
  - `config_file` (str): Path to logging config YAML
- Returns: None
- Side effects: Configures root logger and all module loggers

**`get_logger(name)`**
- Get configured logger for a module
- Parameters:
  - `name` (str): Logger name (typically __name__)
- Returns: logging.Logger instance

**`set_log_level(name, level)`**
- Change log level for specific logger
- Parameters:
  - `name` (str): Logger name
  - `level` (str): Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Returns: None

### llm

LLM interface for all modules.

**`class LLMInterface`**

**`__init__(model="deepseek-coder:6.7b", api_endpoint="http://localhost:11434")`**
- Initialize LLM interface
- Parameters:
  - `model` (str): Model name
  - `api_endpoint` (str): API endpoint URL

**`call(prompt, **kwargs)`**
- Call LLM with prompt
- Parameters:
  - `prompt` (str): Prompt text
  - `**kwargs`: Additional parameters (temperature, max_tokens, etc.)
- Returns: str (LLM response)
- Raises: ConnectionError if API unreachable

**`generate_code(description, language="python")`**
- Generate code from description
- Parameters:
  - `description` (str): Code description
  - `language` (str): Target language
- Returns: str (generated code)

**`analyze_code(code, analysis_type="general")`**
- Analyze code with LLM
- Parameters:
  - `code` (str): Code to analyze
  - `analysis_type` (str): Type of analysis
- Returns: dict with analysis results

**`is_available()`**
- Check if LLM API is available
- Returns: bool

### utils

General utility functions.

**`format_output(content, format_type="text")`**
- Format content for output
- Parameters:
  - `content` (str): Content to format
  - `format_type` (str): Output format (text, json, html)
- Returns: str (formatted content)

**`validate_input(data, schema=None)`**
- Validate input data against schema
- Parameters:
  - `data`: Data to validate
  - `schema` (dict, optional): Validation schema
- Returns: bool

**`read_file(filepath, encoding='utf-8')`**
- Read file content
- Parameters:
  - `filepath` (str): Path to file
  - `encoding` (str): File encoding
- Returns: str (file content)

**`write_file(filepath, content, encoding='utf-8')`**
- Write content to file
- Parameters:
  - `filepath` (str): Path to file
  - `content` (str): Content to write
  - `encoding` (str): File encoding
- Returns: str (path to written file)

**`ensure_directory(dirpath)`**
- Ensure directory exists, create if needed
- Parameters:
  - `dirpath` (str): Path to directory
- Returns: str (path to directory)

### constants

Project constants.

**Attributes:**

```python
PROJECT_NAME = "code-assistant"
PROJECT_VERSION = "0.1.0"
PROJECT_AUTHOR = "Olga Moreira"
PROJECT_REPOSITORY = "https://github.com/omoreira/code_assistant"

MODULES = ["code_starter", "code_debugger", "code_patcher"]
SHARED_PATHS = ["config", "shared", "docs", "tests"]

SUPPORTED_LANGUAGES = ["python", "javascript", "typescript", "java", "cpp"]
SUPPORTED_LLM_PROVIDERS = ["ollama", "openai", "claude"]

DEFAULT_LLM_MODEL = "deepseek-coder:6.7b"
DEFAULT_LLM_ENDPOINT = "http://localhost:11434"
DEFAULT_OUTPUT_DIR = "./generated_projects"

FILE_PATTERNS = {
    "python": "*.py",
    "config": "*.yaml",
    "markdown": "*.md",
    "pseudocode": "*.pseudo"
}
```

---

## Usage Examples

### Example 1: Create a New Project

```python
from code_starter import StarterFileCreator

creator = StarterFileCreator()
spec = creator.create_project_spec(
    name="my_app",
    description="My awesome application",
    modules=["models", "views", "controllers"],
    dependencies=["flask", "sqlalchemy"]
)
creator.save_spec(spec, "my_app.pseudo")
```

### Example 2: Generate Project Structure

```python
from code_starter import BlueprintRenderer

renderer = BlueprintRenderer("my_app.pseudo")
blueprint = renderer.parse_blueprint()
output_path = renderer.render_blueprint("./projects/my_app")
```

### Example 3: Convert Pseudocode to Python

```python
from code_starter import PseudocodeRenderer
from shared.llm import LLMInterface

llm = LLMInterface()
renderer = PseudocodeRenderer(llm)
code = renderer.render_from_file("pseudocode.txt")
renderer.save_code(code, "generated_code.py")
```

### Example 4: Use Shared Configuration

```python
from shared import config, logging as app_logging

# Load configuration
cfg = config.load_config()
debug = config.get_config("development.debug", default=False)

# Setup logging
app_logging.setup_logging()
logger = app_logging.get_logger(__name__)
logger.info("Application started")
```

### Example 5: Use LLM Interface

```python
from shared.llm import LLMInterface

llm = LLMInterface()

# Check availability
if llm.is_available():
    # Generate code
    code = llm.generate_code("A function to calculate factorial")
    
    # Analyze code
    analysis = llm.analyze_code(code, "complexity")
    print(analysis)
```

---

## Error Handling

All functions follow consistent error handling:

- **FileNotFoundError**: When required files don't exist
- **ValueError**: When invalid parameters provided
- **ConnectionError**: When cannot reach LLM API
- **ConfigurationError**: When configuration is invalid

Example:

```python
from code_starter import BlueprintRenderer

try:
    renderer = BlueprintRenderer("nonexistent.pseudo")
    renderer.render_blueprint()
except FileNotFoundError:
    print("Specification file not found")
except ValueError as e:
    print(f"Invalid specification: {e}")
```

---

## Deprecation Policy

- Functions marked with `@deprecated` should not be used in new code
- Deprecated functions will be removed in the next major version
- Check CHANGELOG.md for migration guides

---

For more information, see [ARCHITECTURE.md](ARCHITECTURE.md) and module-specific documentation.
