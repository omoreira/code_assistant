# Code Refractor - Quick Start Guide

## Installation

Already included in code-assistant! Just import:

```python
from code_refractor import (
    RefactoringVerifier,
    CodeRefactorer,
    PathResolver,
    DependencyMapper
)
```

## The Problem It Solves

When you refactor code, you have to:
- ❌ Manually update 50+ import statements
- ❌ Manually update config files
- ❌ Manually update documentation
- ❌ Hope you didn't break anything
- ❌ Run tests to find what broke

**code_refractor** does all this automatically! ✅

## Quick Examples

### Example 1: Check If Refactoring is Safe (30 seconds)

```python
from code_refractor import RefactoringVerifier

# Initialize
verifier = RefactoringVerifier(".")

# Check if refactoring is safe
issues = verifier.check_refactoring_safety(
    old_path="old_module.py",
    new_path="new_location/renamed_module.py"
)

# See what would happen
print(verifier.generate_refactoring_report())
```

**Output:**
```
======================================================================
REFACTORING VERIFICATION REPORT
======================================================================

Issues Found: 1
  - Errors: 0
  - Warnings: 1

WARNINGS (review before refactoring):
  [new_location/renamed_module.py] Missing __init__.py
    💡 Fix: Create new_location/__init__.py

AFFECTED FILES (will need path updates):
  module1.py: lines [5, 12, 28]
  module2.py: lines [3, 9]
  test_module.py: lines [1]

VERDICT: ⚠️  PROCEED WITH CAUTION - Review warnings first
======================================================================
```

### Example 2: Do the Refactoring (1 minute)

```python
from code_refractor import CodeRefactorer

# Initialize
refactorer = CodeRefactorer(".")

# Refactor (automatically updates all imports/paths/docs)
result = refactorer.refactor_with_verification(
    old_path="old_module.py",
    new_path="new_location/renamed_module.py"
)

# Check results
if result.success:
    print("✅ Refactoring successful!")
    print(f"📝 Modified {result.files_modified} files")
    print("Changes made:")
    for change in result.changes_made:
        print(f"  ✓ {change}")
else:
    print("❌ Refactoring failed!")
    for error in result.errors:
        print(f"  ✗ {error.message}")
```

**Output:**
```
✅ Refactoring successful!
📝 Modified 3 files
Changes made:
  ✓ Moved file: old_module.py → new_location/renamed_module.py
  ✓ Updated imports in: module1.py
  ✓ Updated imports in: module2.py
  ✓ Updated config: config.yaml
  ✓ Updated docs: README.md
  ✓ Removed old file: old_module.py
```

### Example 3: Preview First (Dry-Run)

```python
# See what would happen WITHOUT making changes
refactorer = CodeRefactorer(".", dry_run=True)
result = refactorer.refactor_with_verification(
    "old_module.py",
    "new_location/renamed_module.py"
)

print("Preview (not executed):")
for change in result.changes_made:
    print(f"  {change}")

# If looks good, actually do it
refactorer.set_dry_run(False)
result = refactorer.refactor_with_verification(
    "old_module.py",
    "new_location/renamed_module.py"
)
```

### Example 4: Analyze Impact (2 minutes)

```python
from code_refractor import DependencyMapper

mapper = DependencyMapper(".")
mapper.build_dependency_graph()

# What will be affected?
impact = mapper.get_impact("my_module")
print(f"This module affects {impact['total_affected']} other modules:")
print(f"  - Direct dependents: {impact['direct_dependents']}")
print(f"  - Transitive dependents: {impact['transitive_dependents']}")

# Are there circular dependencies?
circles = mapper.find_circular_dependencies()
if circles:
    print("⚠️  Circular dependencies found:")
    for cycle in circles:
        print(f"  {' → '.join(cycle)}")
else:
    print("✅ No circular dependencies")

# What's the safe order to refactor?
order = mapper.suggest_refactoring_order()
print(f"\nSafe refactoring order:\n  {' → '.join(order)}")
```

## The Four Classes

| Class | Purpose | Main Method |
|-------|---------|------------|
| **RefactoringVerifier** | Check before refactoring | `check_refactoring_safety()` |
| **CodeRefactorer** | Do the refactoring | `refactor_with_verification()` |
| **PathResolver** | Resolve paths after | `resolve_all_imports()` |
| **DependencyMapper** | Analyze dependencies | `build_dependency_graph()` |

## Common Tasks

### Rename a File

```python
result = refactorer.refactor_with_verification(
    old_path="utils.py",
    new_path="utilities.py"
)
```

### Move to Subdirectory

```python
result = refactorer.refactor_with_verification(
    old_path="handler.py",
    new_path="handlers/event_handler.py"
)
```

### Refactor Multiple Files

```python
files = [
    ("old_util.py", "utils/helpers.py"),
    ("old_config.py", "config/loader.py"),
]

for old, new in files:
    result = refactorer.refactor_with_verification(old, new)
    if not result.success:
        print(f"Stopped at {old}: {result.errors[0].message}")
        break
```

## What Gets Updated Automatically

✅ **Python Imports**
- `from old_module import something`
- `import old_module`
- Nested imports

✅ **Config Files**
- YAML files (defaults.yaml, config.yaml)
- JSON files
- TOML files  
- INI files

✅ **Documentation**
- Markdown files (*.md)
- ReStructuredText (*.rst)
- Text files (*.txt)

✅ **Paths and References**
- Relative paths in code
- Path references in config
- Documentation references

## Best Practices

### 1️⃣ Always Check First
```python
# Always verify before doing
issues = verifier.check_refactoring_safety(old, new)
print(verifier.generate_refactoring_report())
```

### 2️⃣ Use Dry-Run to Preview
```python
# Preview first
refactorer.set_dry_run(True)
# Then do it for real
refactorer.set_dry_run(False)
```

### 3️⃣ Commit Before Refactoring
```bash
git commit -m "Before refactoring: renaming old_module.py"
```

### 4️⃣ Analyze Impact First
```python
impact = mapper.get_impact(module)
if impact['total_affected'] > 50:
    print("Warning: affects many modules")
```

### 5️⃣ Test After Refactoring
```bash
pytest tests/ -v
```

## Troubleshooting

### "File to refactor does not exist"
✅ **Solution:** Check the path is relative to project root
```python
# ❌ Wrong
check_refactoring_safety("/absolute/path/file.py", ...)

# ✅ Right
check_refactoring_safety("relative/path/file.py", ...)
```

### "New path already exists"
✅ **Solution:** Remove or rename the destination file first
```python
import os
os.remove("existing_file.py")
# Then refactor
```

### Refactoring incomplete
✅ **Solution:** Check the affected files list
```python
affected = verifier.get_affected_files()
print(f"These files need updates: {affected.keys()}")
```

## API Cheat Sheet

**RefactoringVerifier:**
```python
verifier = RefactoringVerifier(".")
issues = verifier.check_refactoring_safety(old, new)
report = verifier.generate_refactoring_report()
affected = verifier.get_affected_files()
```

**CodeRefactorer:**
```python
refactorer = CodeRefactorer(".", dry_run=False)
result = refactorer.refactor_with_verification(old, new)
refactorer.set_dry_run(True)
report = refactorer.get_verification_report()
```

**PathResolver:**
```python
resolver = PathResolver(".")
resolver.register_path_change(old, new)
broken = resolver.resolve_all_imports()
valid, issues = resolver.validate_all_paths()
count = resolver.update_path_references(file, old, new)
refs = resolver.find_path_references(path)
```

**DependencyMapper:**
```python
mapper = DependencyMapper(".")
graph = mapper.build_dependency_graph()
circles = mapper.find_circular_dependencies()
impact = mapper.get_impact(module)
order = mapper.suggest_refactoring_order()
stats = mapper.get_statistics()
text = mapper.export_dependency_graph("text|dot|json")
```

## More Information

- 📖 **Full Guide:** [README.md](README.md)
- 📊 **Module Summary:** [REFACTORING_MODULE_SUMMARY.md](REFACTORING_MODULE_SUMMARY.md)
- 🔗 **API Docs:** [../API.md](../API.md)

## Real-World Example

```python
from code_refractor import (
    RefactoringVerifier,
    CodeRefactorer,
    DependencyMapper
)

# Step 1: Analyze impact
print("📊 Analyzing dependencies...")
mapper = DependencyMapper(".")
mapper.build_dependency_graph()
impact = mapper.get_impact("old_logging")
print(f"   Affects {impact['total_affected']} modules")

# Step 2: Verify safety
print("\n🔍 Checking safety...")
verifier = RefactoringVerifier(".")
issues = verifier.check_refactoring_safety(
    "logging/old_logging.py",
    "logging/unified_logger.py"
)
print(verifier.generate_refactoring_report())

# Step 3: Preview
print("\n👁️  Previewing changes...")
refactorer = CodeRefactorer(".", dry_run=True)
result = refactorer.refactor_with_verification(
    "logging/old_logging.py",
    "logging/unified_logger.py"
)
print("Would make these changes:")
for change in result.changes_made:
    print(f"  {change}")

# Step 4: Do it!
print("\n🚀 Performing refactoring...")
refactorer.set_dry_run(False)
result = refactorer.refactor_with_verification(
    "logging/old_logging.py",
    "logging/unified_logger.py"
)

if result.success:
    print("✅ SUCCESS!")
    print(f"   Updated {result.files_modified} files")
else:
    print("❌ FAILED!")
    for error in result.errors:
        print(f"   {error.message}")
```

**Output:**
```
📊 Analyzing dependencies...
   Affects 7 modules

🔍 Checking safety...
======================================================================
REFACTORING VERIFICATION REPORT
======================================================================
Issues Found: 0
VERDICT: ✅ SAFE - No issues found
======================================================================

👁️  Previewing changes...
Would make these changes:
  [DRY RUN] Moved file: logging/old_logging.py → logging/unified_logger.py
  [DRY RUN] Would update imports: module1.py
  [DRY RUN] Would update imports: module2.py
  [DRY RUN] Would update config: config.yaml

🚀 Performing refactoring...
✅ SUCCESS!
   Updated 3 files
```

## That's It!

You're ready to refactor safely. Just follow the pattern:

1. **Analyze** with DependencyMapper
2. **Verify** with RefactoringVerifier
3. **Preview** with dry-run
4. **Execute** with CodeRefactorer
5. **Test** with pytest

Happy refactoring! 🎉
