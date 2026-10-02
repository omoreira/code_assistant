# ScriptsWriter Guide

Generate shell scripts for running code-assistant projects.

## Overview

The `ScriptsWriter` class generates ready-to-use shell scripts that automate:
- Environment setup
- Dependency management
- Module execution
- Status checking

## Quick Start

```python
from code_starter import ScriptsWriter

# Create scripts in ./scripts directory
writer = ScriptsWriter()
scripts = writer.generate_all_scripts()

# List generated scripts
for name, path in scripts.items():
    print(f"{name} → {path}")
```

## Basic Usage

### Generate Scripts in Default Location

```python
from code_starter import ScriptsWriter

writer = ScriptsWriter()
scripts = writer.generate_all_scripts()

# All scripts created in ./scripts/
```

### Generate Scripts in Custom Location

```python
writer = ScriptsWriter("./my_scripts")
scripts = writer.generate_all_scripts()

# All scripts created in ./my_scripts/
```

### Generate Scripts with Custom Modules

```python
writer = ScriptsWriter()
modules = ["starter", "analyzer", "generator"]
scripts = writer.generate_all_scripts(modules=modules)

# Creates: setup.sh, run_starter.sh, run_analyzer.sh, run_generator.sh
```

### Generate Scripts for a Project

```python
writer = ScriptsWriter()
project_path = "/path/to/project"
scripts = writer.generate_to_project(project_path)

# Scripts created in /path/to/project/scripts/
```

## API Reference

### ScriptsWriter Class

**Constructor:**
```python
ScriptsWriter(output_dir: str = "./scripts")
```

**Methods:**

```python
# Create scripts directory
create_scripts_directory() -> str

# Write specific scripts
write_setup_script() -> str
write_run_script(module_name: str) -> str

# Generate all scripts
generate_all_scripts(modules: Optional[List[str]] = None) -> Dict[str, str]

# Generate scripts for a project
generate_to_project(project_dir: str, modules: Optional[List[str]] = None) -> Dict[str, str]

# Get information about scripts
get_script_count() -> int
list_generated_scripts() -> List[str]
get_script_info() -> Dict[str, Dict[str, str]]
```

## Generated Scripts

### setup.sh
Purpose: One-time environment setup

Features:
- Checks Python 3 installation
- Creates virtual environment
- Installs dependencies
- Verifies installation
- Color-coded output

Usage:
```bash
./scripts/setup.sh
```

### run_<module>.sh
Purpose: Run specific module

Features:
- Auto venv creation/activation
- Dependency checking
- Module execution
- Status reporting
- Help options

Usage:
```bash
./scripts/run_starter.sh          # Run module
./scripts/run_starter.sh --help   # Show help
./scripts/run_starter.sh --status # Show status
```

## Usage Examples

### Example 1: Generate Scripts for New Project

```python
from code_starter import ScriptsWriter
from pathlib import Path

# Create project directory
project_dir = Path("./my_project")
project_dir.mkdir(exist_ok=True)

# Generate scripts
writer = ScriptsWriter()
scripts = writer.generate_to_project(str(project_dir))

print(f"Generated {writer.get_script_count()} scripts")
for script_name in writer.list_generated_scripts():
    print(f"  ✓ {script_name}")
```

### Example 2: Generate Scripts with Custom Modules

```python
from code_starter import ScriptsWriter

writer = ScriptsWriter("./generated_scripts")

# Custom modules
modules = ["processor", "analyzer", "reporter"]
scripts = writer.generate_all_scripts(modules=modules)

# Shows scripts for each module
for name, path in scripts.items():
    size = Path(path).stat().st_size
    print(f"{name:20} {size:,} bytes")
```

### Example 3: Check Generated Scripts

```python
from code_starter import ScriptsWriter

writer = ScriptsWriter()
writer.generate_all_scripts()

# Get detailed information
info = writer.get_script_info()
for name, details in info.items():
    print(f"\n{name}:")
    print(f"  Path: {details['path']}")
    print(f"  Size: {details['size']}")
    print(f"  Executable: {details['executable']}")
```

### Example 4: Integrate with StarterFileCreator

```python
from code_starter import StarterFileCreator, ScriptsWriter
from pathlib import Path

# Create project specification
creator = StarterFileCreator()
spec = creator.create_project_spec(
    name="my_app",
    description="My awesome application",
    modules=["models", "views", "controllers"],
    dependencies=["flask", "sqlalchemy"]
)

# Create project directory
project_dir = Path("./projects/my_app")
project_dir.mkdir(parents=True, exist_ok=True)

# Generate project blueprint
from code_starter import BlueprintRenderer
renderer = BlueprintRenderer()
# ... render blueprint ...

# Generate scripts
writer = ScriptsWriter()
scripts = writer.generate_to_project(str(project_dir))

print(f"Project created with {writer.get_script_count()} scripts")
```

## Script Features

All generated scripts include:

**Validation:**
- Check Python 3 exists
- Check pip available
- Verify virtual environment

**Management:**
- Create venv if needed
- Activate venv automatically
- Install/update dependencies

**Output:**
- Color-coded messages
- Progress indicators
- Error messages
- Status displays

**Options:**
- Help (-h, --help)
- Status (--status)
- Setup (--setup)
- Create (--create)

## Customization

### Modify Generated Scripts

Edit scripts after generation:
```bash
# Edit setup script
nano ./scripts/setup.sh

# Edit module script
nano ./scripts/run_starter.sh
```

### Add Custom Functionality

Add custom sections to generated scripts:
```bash
# Add to setup.sh after installation
echo "Custom setup step"
```

### Extend Script Features

Add new functions to scripts:
```bash
# Add to run_<module>.sh
my_custom_function() {
    echo "Custom function"
}
```

## Best Practices

1. **Run setup first**: `./scripts/setup.sh`
2. **Make executable**: `chmod +x ./scripts/*.sh`
3. **Test scripts**: Run each script to verify
4. **Keep backups**: Backup before modifying
5. **Document changes**: Comment any modifications
6. **Use error checking**: Let scripts validate
7. **Follow conventions**: Keep naming consistent

## Troubleshooting

### Scripts Not Executable

```bash
# Make all scripts executable
chmod +x ./scripts/*.sh

# Verify
ls -l ./scripts/*.sh
```

### Python Not Found

```bash
# Check Python installation
python3 --version

# Scripts will show error if Python missing
./scripts/setup.sh  # Will fail with clear message
```

### Virtual Environment Issues

```bash
# Let setup.sh handle venv
./scripts/setup.sh

# Or recreate manually
rm -rf venv
./scripts/setup.sh
```

### Dependencies Not Installing

```bash
# Check requirements.txt exists
ls -l requirements.txt
ls -l requirements-dev.txt

# Run install_deps.sh
./scripts/install_deps.sh --dev
```

## Advanced Usage

### Generate Scripts Programmatically

```python
from code_starter import ScriptsWriter
import os

class CustomScriptsWriter(ScriptsWriter):
    """Extended scripts writer with custom functionality."""
    
    def write_custom_script(self, name: str, content: str) -> str:
        """Write custom script."""
        script_path = self.output_dir / name
        script_path.write_text(content)
        os.chmod(script_path, 0o755)
        return str(script_path)

writer = CustomScriptsWriter()
writer.generate_all_scripts()
```

### Generate Scripts in Pipeline

```python
from code_starter import (
    StarterFileCreator,
    BlueprintRenderer,
    ScriptsWriter,
    CodeDocumenter
)

# Create spec
creator = StarterFileCreator()
spec = creator.create_project_spec(...)

# Generate structure
renderer = BlueprintRenderer()
renderer.render_blueprint(...)

# Generate scripts
writer = ScriptsWriter()
writer.generate_to_project("./project")

# Generate docs
documenter = CodeDocumenter()
documenter.generate_to_project("./project", ...)

print("Project fully generated!")
```

## Integration with Other Tools

### With BlueprintRenderer

```python
from code_starter import BlueprintRenderer, ScriptsWriter

# Generate structure
renderer = BlueprintRenderer("spec.pseudo")
renderer.render_blueprint("./project")

# Generate scripts for the project
writer = ScriptsWriter()
writer.generate_to_project("./project")
```

### With CodeDocumenter

```python
from code_starter import ScriptsWriter, CodeDocumenter

# Generate scripts
writer = ScriptsWriter()
writer.generate_to_project("./project")

# Generate documentation
documenter = CodeDocumenter()
documenter.generate_to_project(
    "./project",
    "My Project",
    "Project description"
)
```

## See Also

- `code_documenter.py` - Documentation generation
- `blueprint_renderer.py` - Structure generation
- `starterfile_creator.py` - Specification creation
