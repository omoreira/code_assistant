# code_starter - Project Creation Module

The `code_starter` module is your gateway to quickly creating new projects with intelligent code generation. It provides interactive tools for defining project specifications, generating directory structures, and writing initial code.

## Overview

**code_starter** handles the initial project setup phase:
1. Define project specifications interactively
2. Generate directory structures from specifications
3. Convert pseudocode to working Python code
4. Setup GitHub-ready repository structure

## Features

- ✅ **Interactive Project Builder** - Menu-driven specification creation
- ✅ **Smart Directory Generator** - Creates project structures from specs
- ✅ **Code Generation** - Converts pseudocode to Python
- ✅ **GitHub Setup** - Automate repository initialization
- ✅ **Template Support** - Use existing projects as templates
- ✅ **AI-Assisted** - Uses local LLM for code generation

## Quick Start

### Basic Usage

```python
from code_starter import StarterFileCreator

# Create project creator
creator = StarterFileCreator()

# Run interactive mode
creator.run_interactive()
```

This starts an interactive menu where you define:
- Project name
- Description
- Modules/packages
- Dependencies
- File structure

### Programmatic Usage

```python
from code_starter import StarterFileCreator

creator = StarterFileCreator(output_dir="./my_projects")

# Create specification
spec = creator.create_project_spec(
    name="data_processor",
    description="Process and analyze data files",
    modules=["parsers", "analyzers", "utils"],
    dependencies=["pandas", "numpy"]
)

# Save specification
creator.save_spec(spec, "data_processor.pseudo")
```

## Tools

### 1. StarterFileCreator

Create project specifications in interactive or programmatic mode.

**Key Methods:**
- `run_interactive()` - Start interactive menu
- `create_project_spec()` - Programmatic specification
- `save_spec()` - Save specification to file
- `load_spec()` - Load existing specification

**Output:** `starterfile.pseudo` (project specification)

### 2. BlueprintRenderer

Generate directory structures from project specifications.

**Key Methods:**
- `parse_blueprint()` - Parse specification file
- `render_blueprint()` - Create actual directories
- `get_directory_tree()` - View structure before creating

**Input:** `starterfile.pseudo`  
**Output:** Directory structure on disk

### 3. PseudocodeRenderer

Convert pseudocode to Python code.

**Key Methods:**
- `render_from_file()` - Convert file
- `render_from_string()` - Convert string
- `save_code()` - Save generated code

**Input:** Pseudocode file or string  
**Output:** Python code files

### 4. GitHubRepoPlanner

Automate GitHub repository setup.

**Key Methods:**
- `answer_questions()` - Interactive questionnaire
- `quick_setup()` - Use presets
- `generate_structure()` - Create all files
- `save_config()` / `load_config()` - Persist configuration

**Output:** Complete repository structure

The repository planner creates both `setup.py` and `pyproject.toml` by default.
Its interactive setup also offers optional Docker support; enabling it writes a
`Dockerfile` and `.dockerignore`. Quick Setup leaves Docker support disabled.

## Workflow Examples

### Example 1: Create a Flask Web Project

```bash
python -m code_starter.starterfile_creator

# Follow prompts:
# Project name: my_flask_app
# Description: A simple Flask web application
# Modules: app, routes, models, utils
# Dependencies: flask, sqlalchemy
```

### Example 2: Generate Structure from Specification

```python
from code_starter import BlueprintRenderer

renderer = BlueprintRenderer("my_project.pseudo")
renderer.render_blueprint("./projects/my_project")
print("Project structure created!")
```

### Example 3: Full Project Setup

```python
from code_starter import (
    StarterFileCreator,
    BlueprintRenderer,
    PseudocodeRenderer,
    GitHubRepoPlanner
)
from shared.llm import LLMInterface

# Step 1: Create specification
creator = StarterFileCreator()
spec = creator.create_project_spec(
    name="web_scraper",
    description="Web scraping tool",
    modules=["scrapers", "parsers", "storage"],
    dependencies=["requests", "beautifulsoup4"]
)
creator.save_spec(spec, "web_scraper.pseudo")

# Step 2: Generate directory structure
renderer = BlueprintRenderer("web_scraper.pseudo")
renderer.render_blueprint("./projects/web_scraper")

# Step 3: Generate initial code
llm = LLMInterface()
pseudocode = """
module: scrapers
  class: WebScraper
    method: __init__(url)
      set self.url = url
    method: fetch()
      fetch from url
      return html
"""

code_renderer = PseudocodeRenderer(llm)
code = code_renderer.render_from_string(pseudocode)

# Step 4: Setup GitHub repo
planner = GitHubRepoPlanner()
config = planner.quick_setup()
planner.generate_structure(config)
```

## Project Specification Format (.pseudo)

Project specifications use a hierarchical tree format:

```
PROJECT: MyProject
  DESCRIPTION: A sample project
  VERSION: 1.0.0
  
  DEPENDENCIES:
    - numpy>=1.20
    - pandas>=1.3
    - requests>=2.25
  
  REPOMAP:
    my_project/
      __init__.py
      main.py
      config/
        __init__.py
        settings.py
      models/
        __init__.py
        user.py
        product.py
      utils/
        __init__.py
        helpers.py
      tests/
        test_models.py
        test_utils.py
```

## Pseudocode Format

Convert pseudocode to Python:

```
module: myapp
  
  function: process_data(items)
    description: Process a list of items
    param: items - list of items to process
    return: processed list
    
    for item in items
      validate item
      transform item
      add to results
    
    return results
  
  class: DataProcessor
    attributes:
      - data: list
      - config: dict
    
    method: __init__(config)
      set self.config = config
      set self.data = []
    
    method: add_item(item)
      validate item
      append to self.data
    
    method: process()
      results = []
      for item in self.data
        result = process_item(item)
        append to results
      return results
```

The renderer converts this to:

```python
# Generated from pseudocode

def process_data(items):
    """Process a list of items.
    
    Args:
        items: list of items to process
    
    Returns:
        processed list
    """
    results = []
    for item in items:
        # validate item
        # transform item
        results.append(item)
    
    return results


class DataProcessor:
    """Data processor class."""
    
    def __init__(self, config):
        self.config = config
        self.data = []
    
    def add_item(self, item):
        """Add item to data."""
        # validate item
        self.data.append(item)
    
    def process(self):
        """Process all items."""
        results = []
        for item in self.data:
            result = process_item(item)
            results.append(result)
        return results
```

## Configuration

The module uses `config/defaults.yaml` for settings:

```yaml
code_starter:
  output_dir: ./generated_projects
  template_dir: ./templates
  enable_ai_generation: true
  default_language: python
```

## Advanced Topics

### Using Templates

Create reusable project templates:

```python
creator = StarterFileCreator()

# Save as template
creator.save_spec(spec, "templates/flask_api.pseudo")

# Later, load and customize template
template_spec = creator.load_spec("templates/flask_api.pseudo")
template_spec["name"] = "my_api"
creator.save_spec(template_spec, "my_api.pseudo")
```

### Custom Code Generation

Use custom prompts with LLM:

```python
from code_starter import PseudocodeRenderer
from shared.llm import LLMInterface

llm = LLMInterface()
renderer = PseudocodeRenderer(llm)

# Custom pseudocode with LLM generation
code = renderer.render_from_string("""
  function: calculate_fibonacci(n)
    description: Calculate nth Fibonacci number with memoization
    optimize_for: performance
""")
```

### Batch Project Creation

Create multiple projects:

```python
projects = [
    ("api_service", "REST API service"),
    ("worker", "Background job worker"),
    ("client", "Client library"),
]

creator = StarterFileCreator()
for name, desc in projects:
    spec = creator.create_project_spec(
        name=name,
        description=desc,
        modules=["core", "utils"],
        dependencies=[]
    )
    creator.save_spec(spec, f"{name}.pseudo")
    print(f"Created {name}")
```

## Troubleshooting

### Issue: "Cannot find starterfile.pseudo"

**Solution:** Make sure you've run the creator and saved the specification file.

```python
creator = StarterFileCreator()
creator.run_interactive()  # This creates starterfile.pseudo
```

### Issue: "LLM API unreachable"

**Solution:** Ensure ollama is running:

```bash
ollama serve  # Start in another terminal
```

Then try again.

### Issue: "Invalid pseudocode syntax"

**Solution:** Check pseudocode format:
- Proper indentation
- Valid keywords (module, class, method, function)
- Correct parameter syntax

### Issue: Slow code generation

**Solution:** This is normal for LLM operations. Generated code is cached, so subsequent calls for same pseudocode are faster.

## API Reference

See [API.md](../API.md) for complete API documentation.

## Related Documentation

- [Architecture](../ARCHITECTURE.md) - System design
- [Contributing](../CONTRIBUTING.md) - How to contribute
- [Main README](../../README.md) - Project overview

## Examples

See `code_starter/` directory for example files:
- `starterfile.pseudo` - Example project specification
- `starterfile_test.pseudo` - Test specification

## Next Steps

1. **Create Your First Project** - Use interactive creator
2. **Explore Tools** - Try each tool individually
3. **Read Examples** - Check example specifications
4. **Integrate** - Use in your own workflows
5. **Extend** - Customize templates and pseudocode

---

**Questions?** Check [troubleshooting](#troubleshooting) or open an issue on GitHub.
