# CodeDocumenter Guide

Generate professional documentation for code-assistant projects.

## Overview

The `CodeDocumenter` class generates comprehensive markdown documentation:
- Project README
- Architecture documentation
- API reference
- Getting started guide
- Contributing guidelines
- Module-specific documentation

## Quick Start

```python
from code_starter import CodeDocumenter

# Create documentation in ./docs directory
documenter = CodeDocumenter()
docs = documenter.generate_all_docs(
    project_name="My Project",
    description="A brief project description",
    modules=["starter", "debugger", "patcher"]
)

# List generated documentation
for name, path in docs.items():
    print(f"{name} → {path}")
```

## Basic Usage

### Generate Documentation in Default Location

```python
from code_starter import CodeDocumenter

documenter = CodeDocumenter()
docs = documenter.generate_all_docs(
    project_name="MyApp",
    description="MyApp - A great application"
)

# All docs created in ./docs/
```

### Generate Documentation in Custom Location

```python
documenter = CodeDocumenter("./documentation")
docs = documenter.generate_all_docs(
    project_name="MyApp",
    description="MyApp - A great application"
)

# All docs created in ./documentation/
```

### Generate Documentation with Custom Modules

```python
documenter = CodeDocumenter()
modules = ["processor", "analyzer", "formatter"]
docs = documenter.generate_all_docs(
    project_name="DataApp",
    description="Data processing application",
    modules=modules
)

# Creates docs for each module
```

### Generate Documentation for a Project

```python
documenter = CodeDocumenter()
project_path = "/path/to/project"
docs = documenter.generate_to_project(
    project_path,
    project_name="My Project",
    description="Project description"
)

# Docs created in /path/to/project/docs/
```

## API Reference

### CodeDocumenter Class

**Constructor:**
```python
CodeDocumenter(output_dir: str = "./docs")
```

**Methods:**

```python
# Create docs directory
create_docs_directory() -> str

# Write specific documentation
write_readme(project_name: str, description: str, modules: List[str]) -> str
write_architecture_docs(modules: List[str]) -> str
write_api_docs(modules: List[str]) -> str
write_getting_started(project_name: str, modules: List[str]) -> str
write_contributing_guide() -> str
create_module_docs(module_name: str) -> str

# Generate all documentation
generate_all_docs(
    project_name: str,
    description: str,
    modules: Optional[List[str]] = None
) -> Dict[str, str]

# Generate docs for a project
generate_to_project(
    project_dir: str,
    project_name: str,
    description: str,
    modules: Optional[List[str]] = None
) -> Dict[str, str]

# Get information about docs
get_doc_count() -> int
list_generated_docs() -> List[str]
get_doc_info() -> Dict[str, Dict[str, str]]
```

## Generated Documentation

### README.md
Main project documentation with:
- Project description
- Quick start guide
- Installation instructions
- Module overview
- Project structure
- Configuration info
- License info

### ARCHITECTURE.md
Technical documentation with:
- System overview
- Architecture diagram
- Module descriptions
- Directory structure
- Data flow diagrams
- Design patterns
- Future enhancements

### API.md
API reference with:
- Module APIs
- Function signatures
- Parameter descriptions
- Return values
- Usage examples
- Common patterns
- Best practices

### GETTING_STARTED.md
User-friendly guide with:
- Prerequisites
- Installation steps
- First steps
- Common tasks
- Troubleshooting
- Learning path

### CONTRIBUTING.md
Developer guide with:
- Fork/clone instructions
- Code style requirements
- Testing guidelines
- Documentation standards
- Commit message format
- PR process

### Module Documentation
Per-module docs with:
- Module overview
- Usage examples
- API reference
- Contributing info

## Usage Examples

### Example 1: Generate Complete Documentation

```python
from code_starter import CodeDocumenter
from pathlib import Path

# Create project directory
project_dir = Path("./my_project")
project_dir.mkdir(exist_ok=True)

# Generate documentation
documenter = CodeDocumenter()
docs = documenter.generate_to_project(
    str(project_dir),
    project_name="My Project",
    description="A comprehensive project documentation example",
    modules=["starter", "debugger", "patcher"]
)

print(f"Generated {documenter.get_doc_count()} documentation files")
```

### Example 2: Generate Documentation with Custom Modules

```python
from code_starter import CodeDocumenter

documenter = CodeDocumenter()

modules = ["parser", "analyzer", "reporter"]
docs = documenter.generate_all_docs(
    project_name="DataAnalyzer",
    description="Analyze and report on data",
    modules=modules
)

# Shows generated docs
for doc_name in documenter.list_generated_docs():
    print(f"  ✓ {doc_name}")
```

### Example 3: Check Generated Documentation

```python
from code_starter import CodeDocumenter
from pathlib import Path

documenter = CodeDocumenter()
documenter.generate_all_docs(
    "TestProject",
    "Test project documentation"
)

# Get detailed information
info = documenter.get_doc_info()
for name, details in info.items():
    print(f"\n{name}:")
    print(f"  Path: {details['path']}")
    print(f"  Size: {details['size']}")
```

### Example 4: Integrate with ScriptsWriter

```python
from code_starter import ScriptsWriter, CodeDocumenter
from pathlib import Path

project_dir = Path("./my_project")
project_dir.mkdir(exist_ok=True, parents=True)

# Generate scripts
writer = ScriptsWriter()
writer.generate_to_project(str(project_dir))

# Generate documentation
documenter = CodeDocumenter()
documenter.generate_to_project(
    str(project_dir),
    project_name="My Project",
    description="My awesome project"
)

print("Project fully documented!")
```

### Example 5: Full Project Generation

```python
from code_starter import (
    StarterFileCreator,
    BlueprintRenderer,
    ScriptsWriter,
    CodeDocumenter
)
from pathlib import Path

# Create specification
creator = StarterFileCreator()
spec = creator.create_project_spec(
    name="analytics",
    description="Data analytics platform",
    modules=["parser", "analyzer"],
    dependencies=["pandas", "numpy"]
)

# Create project directories
project_dir = Path("./projects/analytics")
project_dir.mkdir(parents=True, exist_ok=True)

# Save specification
creator.save_spec(spec, str(project_dir / "spec.pseudo"))

# Generate structure
renderer = BlueprintRenderer(str(project_dir / "spec.pseudo"))
renderer.render_blueprint(str(project_dir))

# Generate scripts
writer = ScriptsWriter()
writer.generate_to_project(str(project_dir), modules=["parser", "analyzer"])

# Generate documentation
documenter = CodeDocumenter()
documenter.generate_to_project(
    str(project_dir),
    project_name="Analytics Platform",
    description="Data analytics platform for analysis and reporting",
    modules=["parser", "analyzer"]
)

print("✓ Project fully generated with structure, scripts, and documentation!")
```

## Documentation Structure

Generated docs follow this structure:

```
docs/
├── README.md              # Main documentation
├── ARCHITECTURE.md        # Technical design
├── API.md                 # API reference
├── GETTING_STARTED.md     # User guide
├── CONTRIBUTING.md        # Developer guide
└── modules/
    ├── starter/
    │   └── README.md
    ├── debugger/
    │   └── README.md
    └── patcher/
        └── README.md
```

## Customization

### Modify Generated Documentation

Edit docs after generation:
```bash
# Edit README
nano ./docs/README.md

# Edit architecture docs
nano ./docs/ARCHITECTURE.md
```

### Add Custom Sections

Add to generated documentation:
```markdown
## Custom Section

Your custom content here...
```

### Extend Module Documentation

Add to module-specific README:
```bash
echo "## Additional Info" >> ./docs/starter/README.md
```

## Best Practices

1. **Be descriptive**: Clear, helpful documentation
2. **Include examples**: Show how to use features
3. **Keep updated**: Update docs with code changes
4. **Use Markdown**: Format consistently
5. **Structure clearly**: Logical organization
6. **Add links**: Cross-reference related docs
7. **Review regularly**: Keep docs accurate

## Content Guidelines

### README.md
- What is the project?
- How to install?
- How to get started?
- What are the main features?
- Where to find help?

### ARCHITECTURE.md
- System design overview
- Components and modules
- Data flow
- Design decisions
- Technical considerations

### API.md
- How to use the API?
- Function signatures
- Parameters and returns
- Usage examples
- Error handling

### GETTING_STARTED.md
- Installation steps
- First steps
- Common tasks
- Troubleshooting
- Next steps

### CONTRIBUTING.md
- How to contribute?
- Development setup
- Code standards
- Testing requirements
- PR process

## Advanced Usage

### Custom Documentation Generation

```python
from code_starter import CodeDocumenter
from pathlib import Path

class CustomDocumenter(CodeDocumenter):
    """Extended documenter with custom docs."""
    
    def write_custom_doc(self, name: str, content: str) -> str:
        """Write custom documentation file."""
        doc_path = self.output_dir / f"{name}.md"
        doc_path.write_text(content)
        return str(doc_path)

documenter = CustomDocumenter()
documenter.generate_all_docs(
    "MyProject",
    "My project"
)
documenter.write_custom_doc("CHANGELOG", "# Changelog\n...")
```

### Programmatic Documentation

```python
from code_starter import CodeDocumenter

def generate_project_docs(project_info: dict) -> dict:
    """Generate docs from project info dictionary."""
    documenter = CodeDocumenter()
    
    return documenter.generate_all_docs(
        project_name=project_info.get("name"),
        description=project_info.get("description"),
        modules=project_info.get("modules", [])
    )

# Use with project data
project_data = {
    "name": "MyApp",
    "description": "My application",
    "modules": ["core", "utils"]
}

docs = generate_project_docs(project_data)
```

## Integration Examples

### With GitHub
```markdown
# Repository

Documentation is automatically generated and placed in the `docs/` folder.

See:
- [README](docs/README.md)
- [Getting Started](docs/GETTING_STARTED.md)
- [API Reference](docs/API.md)
```

### With CI/CD
```bash
# Generate docs as part of build
python -c "
from code_starter import CodeDocumenter
documenter = CodeDocumenter()
documenter.generate_all_docs('MyProject', 'Description')
"
```

## Troubleshooting

### Documentation Not Generated

```python
# Check directory was created
from pathlib import Path
print(Path("./docs").exists())

# Check docs were written
documenter = CodeDocumenter()
docs = documenter.generate_all_docs("Test", "Test project")
print(documenter.get_doc_count())
```

### Module Documentation Missing

```python
# Ensure modules list is provided
documenter = CodeDocumenter()
modules = ["starter", "debugger", "patcher"]
docs = documenter.generate_all_docs(
    "Project",
    "Description",
    modules=modules  # Must provide modules
)
```

## See Also

- `scripts_writer.py` - Script generation
- `blueprint_renderer.py` - Structure generation
- `starterfile_creator.py` - Specification creation
- README.md - Project overview
