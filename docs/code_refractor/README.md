# Code Refractor Module

Intelligent code refactoring with automatic verification and path safety.

**Status:** ✅ Fully Implemented  
**Version:** 0.1.0  
**Author:** Olga Moreira  

## Overview

The `code_refractor` module ensures that code refactoring operations don't break anything. It provides:

1. **RefactoringVerifier** - Verify refactoring safety before executing
2. **CodeRefactorer** - Execute refactoring with automatic path/import updates  
3. **PathResolver** - Resolve and validate all paths after refactoring
4. **DependencyMapper** - Map code dependencies to analyze refactoring impact

### Problem It Solves

When you refactor code (rename files, move modules, rename classes), you need to:
- Update all `import` statements in other files
- Update all path references in code
- Update configuration files
- Update documentation
- Verify nothing breaks

**code_refractor** automates this entire process safely.

## Installation

The module is already included in the code-assistant package:

```bash
# Install code-assistant
pip install -e ".[dev]"

# Or just the dependencies
pip install -e .
```

## Quick Start

### Example 1: Verify Refactoring is Safe

```python
from code_refractor import RefactoringVerifier

# Initialize verifier
verifier = RefactoringVerifier(project_root="/path/to/project")

# Check if refactoring is safe
issues = verifier.check_refactoring_safety(
    old_path="code_starter/old_module.py",
    new_path="code_starter/modules/new_module.py",
    element_type="module"
)

# See what would break
print(verifier.generate_refactoring_report())

# Results:
# - Errors (must fix)
# - Warnings (review)  
# - Affected files (will need updates)
# - Safety verdict
```

### Example 2: Refactor with Automatic Updates

```python
from code_refractor import CodeRefactorer

# Initialize refactorer
refactorer = CodeRefactorer(project_root="/path/to/project")

# Perform refactoring
result = refactorer.refactor_with_verification(
    old_path="code_starter/old_module.py",
    new_path="code_starter/modules/new_module.py",
    element_type="module"
)

# Check results
if result.success:
    print(f"✓ Refactored successfully!")
    print(f"✓ Files modified: {result.files_modified}")
    print(f"✓ Changes: {result.changes_made}")
else:
    print(f"✗ Refactoring failed")
    for error in result.errors:
        print(f"  - {error.message}")
```

### Example 3: Analyze Refactoring Impact

```python
from code_refractor import DependencyMapper

# Initialize mapper
mapper = DependencyMapper(project_root="/path/to/project")

# Build dependency graph
dependencies = mapper.build_dependency_graph()

# Analyze impact of refactoring a module
impact = mapper.get_impact("code_starter.old_module")
print(f"Files that depend on this module: {len(impact['all_dependents'])}")
print(f"Direct dependents: {impact['direct_dependents']}")
print(f"Transitive dependents: {impact['transitive_dependents']}")

# Find circular dependencies
circles = mapper.find_circular_dependencies()
if circles:
    print(f"⚠️  Found circular dependencies: {circles}")

# Get refactoring suggestions
order = mapper.suggest_refactoring_order()
print(f"Suggested refactoring order: {order}")
```

### Example 4: Dry-Run Mode (Preview Changes)

```python
from code_refractor import CodeRefactorer

refactorer = CodeRefactorer(project_root="/path/to/project", dry_run=True)

# Simulate what would happen
result = refactorer.refactor_with_verification(
    old_path="code_starter/old_module.py",
    new_path="code_starter/modules/new_module.py"
)

# See what would be changed (without actually making changes)
print("Changes that would be made:")
for change in result.changes_made:
    print(f"  {change}")
```

## Core Classes

### RefactoringVerifier

Verifies refactoring operations before execution.

**Methods:**
```python
# Check if refactoring is safe
issues = verifier.check_refactoring_safety(
    old_path: str,
    new_path: str,
    element_type: str = "module"
) -> List[RefactoringIssue]

# Get affected files
affected = verifier.get_affected_files() -> Dict[str, List[int]]

# Generate detailed report
report = verifier.generate_refactoring_report() -> str
```

**Verification Checks:**
- ✅ Source file exists
- ✅ No path conflicts (overwriting)
- ✅ All references found
- ✅ Import chain validity
- ✅ No circular dependencies
- ✅ Parent directories exist

### CodeRefactorer

Executes refactoring with automatic updates.

**Methods:**
```python
# Perform refactoring with verification
result = refactorer.refactor_with_verification(
    old_path: str,
    new_path: str,
    element_type: str = "module"
) -> RefactoringResult

# Get verification report
report = refactorer.get_verification_report() -> str

# Set dry-run mode
refactorer.set_dry_run(True)
```

**What It Does:**
1. Verifies safety
2. Moves file
3. Updates imports
4. Updates config files
5. Updates documentation
6. Cleans up old location

### PathResolver

Resolves and validates paths after refactoring.

**Methods:**
```python
# Register a path change
resolver.register_path_change(old_path, new_path)

# Find all broken imports
broken = resolver.resolve_all_imports() -> List[Tuple[str, str, int]]

# Update path references in a file
count = resolver.update_path_references(
    file_path: str,
    old_path: str,
    new_path: str
) -> int

# Find all references to a path
refs = resolver.find_path_references(path: str) -> List[Tuple[str, int]]

# Validate all paths in project
is_valid, issues = resolver.validate_all_paths() -> Tuple[bool, List[str]]

# Get import map
imports = resolver.get_import_map() -> Dict[str, Set[str]]
```

### DependencyMapper

Maps code dependencies and analyzes impact.

**Methods:**
```python
# Build dependency graph
graph = mapper.build_dependency_graph() -> Dict[str, Set[str]]

# Find circular dependencies
circles = mapper.find_circular_dependencies() -> List[List[str]]

# Get modules that depend on this one
dependents = mapper.get_dependents(module: str) -> Set[str]

# Get modules this one depends on
dependencies = mapper.get_dependencies(module: str) -> Set[str]

# Analyze refactoring impact
impact = mapper.get_impact(module: str) -> Dict[str, Set[str]]

# Suggest refactoring order
order = mapper.suggest_refactoring_order() -> List[str]

# Export dependency graph
graph_text = mapper.export_dependency_graph(format="text|dot|json") -> str

# Get statistics
stats = mapper.get_statistics() -> Dict[str, any]
```

## Usage Patterns

### Pattern 1: Safe Refactoring Workflow

```python
from code_refractor import (
    RefactoringVerifier,
    CodeRefactorer,
    DependencyMapper
)

# Step 1: Analyze impact
mapper = DependencyMapper(".")
mapper.build_dependency_graph()
impact = mapper.get_impact("my_old_module")
print(f"This will affect {impact['total_affected']} modules")

# Step 2: Verify safety
verifier = RefactoringVerifier(".")
issues = verifier.check_refactoring_safety(
    "my_old_module.py",
    "new_path/my_new_module.py"
)

if any(i.severity == "error" for i in issues):
    print("Cannot refactor - errors found")
    sys.exit(1)

# Step 3: Preview changes (dry-run)
refactorer = CodeRefactorer(".", dry_run=True)
result = refactorer.refactor_with_verification(
    "my_old_module.py",
    "new_path/my_new_module.py"
)
print("Preview:", result.changes_made)

# Step 4: Execute refactoring
refactorer.set_dry_run(False)
result = refactorer.refactor_with_verification(
    "my_old_module.py",
    "new_path/my_new_module.py"
)

if result.success:
    print("✓ Refactoring complete!")
```

### Pattern 2: Batch Refactoring

```python
from code_refractor import CodeRefactorer, DependencyMapper

mapper = DependencyMapper(".")
mapper.build_dependency_graph()

# Get modules in refactoring order
order = mapper.suggest_refactoring_order()

refactorer = CodeRefactorer(".")

# Refactor in safe order
for module in modules_to_refactor:
    if module in order:
        result = refactorer.refactor_with_verification(
            old_path=f"{module}.py",
            new_path=f"refactored/{module}.py"
        )
        
        if result.success:
            print(f"✓ {module} refactored")
        else:
            print(f"✗ {module} failed - stopping")
            break
```

### Pattern 3: Analyze Dependencies Before Refactoring

```python
from code_refractor import DependencyMapper

mapper = DependencyMapper(".")
graph = mapper.build_dependency_graph()

# Show dependency tree
print(mapper.export_dependency_graph(format="text"))

# Check for circular dependencies
circles = mapper.find_circular_dependencies()
if circles:
    print("⚠️  Circular dependencies found:")
    for cycle in circles:
        print(f"  {' → '.join(cycle)}")

# Get statistics
stats = mapper.get_statistics()
print(f"Total modules: {stats['total_modules']}")
print(f"Independent modules: {stats['independent_modules']}")
print(f"Circular deps: {stats['circular_dependencies']}")
```

## Data Structures

### RefactoringIssue

Represents a potential problem during refactoring:

```python
@dataclass
class RefactoringIssue:
    severity: str              # "error", "warning", "info"
    file_path: str            # File involved
    issue_type: str           # "broken_import", "path_conflict", etc.
    message: str              # Human-readable message
    line_number: Optional[int] # Line where issue occurs
    suggested_fix: Optional[str] # How to fix it
```

### RefactoringResult

Result of a refactoring operation:

```python
@dataclass
class RefactoringResult:
    success: bool              # Was refactoring successful?
    old_path: str             # Original path
    new_path: str             # New path
    files_modified: int       # Number of files updated
    files_moved: int          # Number of files moved
    changes_made: List[str]   # List of changes
    errors: List[RefactoringIssue]  # Errors encountered
```

## Common Tasks

### Rename a Module

```python
from code_refractor import CodeRefactorer

refactorer = CodeRefactorer(".")
result = refactorer.refactor_with_verification(
    old_path="old_name.py",
    new_path="new_name.py",
    element_type="module"
)
```

### Move a Module to a Subdirectory

```python
result = refactorer.refactor_with_verification(
    old_path="module.py",
    new_path="subdir/module.py",
    element_type="module"
)
```

### Refactor Multiple Related Files

```python
files_to_refactor = [
    ("old_utils.py", "utils/helpers.py"),
    ("old_config.py", "config/loader.py"),
]

for old_path, new_path in files_to_refactor:
    result = refactorer.refactor_with_verification(old_path, new_path)
    if not result.success:
        print(f"Failed to refactor {old_path}")
        break
```

## Configuration

The module works out of the box with no configuration needed. Optional settings:

```python
# Custom project root
verifier = RefactoringVerifier(project_root="/path/to/project")

# Dry-run mode (preview only)
refactorer = CodeRefactorer(project_root=".", dry_run=True)
```

## Troubleshooting

### Issue: "File to refactor does not exist"

**Solution:** Check the file path is correct relative to project root:
```python
# Wrong
verifier.check_refactoring_safety("/absolute/path/file.py", ...)

# Right
verifier.check_refactoring_safety("relative/path/file.py", ...)
```

### Issue: "New path already exists"

**Solution:** Choose a different name or remove the existing file:
```python
# Remove the file first
import os
os.remove("new_path.py")

# Then refactor
result = refactorer.refactor_with_verification(old_path, new_path)
```

### Issue: Refactoring seems incomplete

**Solution:** Check the detailed report:
```python
print(refactorer.get_verification_report())

# Or check individual affected files
print(verifier.get_affected_files())
```

## Performance Considerations

- **Large projects:** Module scanning scales linearly with project size
- **Many dependencies:** Circular dependency detection is O(V + E)
- **Dry-run mode:** Same performance as normal mode (doesn't save)

## Advanced Usage

### Custom Verification Rules

```python
from code_refractor import RefactoringVerifier

class CustomVerifier(RefactoringVerifier):
    def _check_additional_rules(self, old_path, new_path):
        """Add custom verification rules"""
        # Your custom checks here
        pass
```

### Extend PathResolver

```python
from code_refractor import PathResolver

class CustomPathResolver(PathResolver):
    def update_custom_formats(self, old_path, new_path):
        """Update paths in custom file formats"""
        # Your custom path updates here
        pass
```

## Integration with Other Modules

Works seamlessly with other code-assistant modules:

```python
# Use with code_starter to refactor generated code
from code_starter import ScriptsWriter
from code_refractor import CodeRefactorer

# Generate scripts, then refactor them
writer = ScriptsWriter()
refactorer = CodeRefactorer()

# Can now safely refactor generated code
```

## API Reference

See [../API.md](../API.md) for complete API documentation.

## Best Practices

1. **Always use dry-run first:**
   ```python
   refactorer = CodeRefactorer(dry_run=True)
   ```

2. **Review the report before refactoring:**
   ```python
   print(verifier.generate_refactoring_report())
   ```

3. **Analyze impact on dependencies:**
   ```python
   mapper.get_impact(module)
   ```

4. **Commit changes before refactoring:**
   ```bash
   git commit -m "Pre-refactoring commit"
   ```

5. **Refactor in safe order:**
   ```python
   order = mapper.suggest_refactoring_order()
   ```

## Testing

Test the module with the included test suite:

```bash
# Run tests
pytest tests/unit/test_code_refractor.py -v

# Run with coverage
pytest tests/ --cov=code_refractor
```

## Contributing

See [../CONTRIBUTING.md](../CONTRIBUTING.md) for how to contribute.

## License

This module is part of code-assistant and is licensed under the MIT License.

## Support

For issues, questions, or suggestions:
- Open an issue: https://github.com/omoreira/code_assistant/issues
- Contact: olga.moreira@gmail.com

---

**Version:** 0.1.0  
**Last Updated:** 2024  
**Status:** Stable
