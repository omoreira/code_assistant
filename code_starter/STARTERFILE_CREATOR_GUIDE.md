# Starterfile Creator Tool Guide

## Overview
`starterfile_creator.py` is an interactive wizard that helps you build `starterfile.pseudo` files without manual formatting.

## Features

### 1. **Interactive Menu System**
```
Main Menu:
  1. Create new project structure
  2. View current structure
  3. Add/Edit pseudocode for files
  4. Preview starterfile.pseudo
  5. Save to starterfile.pseudo
  6. Load existing starterfile.pseudo
  7. Clear all
  8. Exit
```

### 2. **Directory Tree Builder**
- Interactively add directories and files
- Navigate through the tree structure
- Visual representation of the complete structure
- Supports nested directories

### 3. **Pseudocode Management**
For each file, collect:
- **INPUT**: What the code expects as input
- **OUTPUT**: What the code produces
- **TASK**: What the code does (main purpose)
- **CONDITIONS**: Special conditions or prerequisites
- **PREFERENCES**: Optional preferences/recommendations

### 4. **Preview & Validation**
- Preview the formatted output before saving
- Ensure structure is valid
- Shows file/directory status

### 5. **Save/Load**
- Save to `starterfile.pseudo` or custom filename
- Load existing files (for future enhancement)

---

## Usage Example

### Step 1: Start the Tool
```bash
python starterfile_creator.py
```

### Step 2: Create Project Structure
```
Select option: 1
Enter root directory: ./my_coding_assistant
[./my_coding_assistant]
Select (1-4): 1  # Add directory
Directory name: core
Add items to ./my_coding_assistant/core? (y/n): y
```

### Step 3: Build Your Tree
Continue adding directories and files interactively.

### Step 4: Add Pseudocode
```
Select option: 3  # Manage pseudocode
Files in project:
  1. [ ] ./my_coding_assistant/core/main.py
  2. [ ] ./my_coding_assistant/core/config.py
Select file number: 1
```

### Step 5: Preview
```
Select option: 4  # Preview
```

### Step 6: Save
```
Select option: 5  # Save
Filename (default: starterfile.pseudo): starterfile.pseudo
✓ Saved to starterfile.pseudo
```

---

## My Suggestions for Enhancement

### Short-term (Easy to Add)
1. **Template System**
   - Save frequently-used structures as templates
   - Load templates to speed up creation
   ```python
   def save_template(self, name):
       templates[name] = {
           'tree': self.tree_structure,
           'pseudocodes': self.pseudocodes
       }
   ```

2. **Batch File Creation**
   - Add multiple files at once with pattern matching
   ```
   Add files: *.py (would create placeholder for all Python files)
   ```

3. **Edit Mode**
   - Modify existing structure items
   - Delete items from tree

### Medium-term (More Complex)
4. **Load Existing Structure**
   - Parse starterfile.pseudo back into the editor
   - Allow modification and re-saving

5. **Project Templates**
   - Pre-built templates for common project types:
     - `FastAPI Server`
     - `Django App`
     - `CLI Tool`
     - `ML Pipeline`
     - `Data Pipeline`

6. **Validation Rules**
   - Warn about duplicate file paths
   - Check for circular dependencies
   - Validate file extensions
   - Suggest best practices

### Advanced Features (Long-term)
7. **Configuration File**
   - `starterfile_config.json` for project metadata
   - Store project name, version, author, etc.

8. **Multi-Format Export**
   - Export as JSON for programmatic use
   - Export as Markdown documentation
   - Generate README automatically

9. **Integration with blueprint_renderer**
   - Auto-validate tree structure matches what blueprint_renderer expects
   - Quick-generate from existing project (scan filesystem)

10. **GUI Version**
    - Web-based or Tkinter GUI
    - Drag-and-drop tree builder
    - Live preview

---

## File Structure Generated

```
# REPOMAP

./my_project
        |___________src/
        |               |______main.py
        |               |______config.py
        |___________tests/
                        |______ test_main.py

# PSEUDOCODE

## ./my_project/src/main.py

INPUT: Configuration file path
OUTPUT: Application instance
TASK: Initialize and configure the main application
CONDITIONS: Configuration file must exist
PREFERENCES: Use async/await for I/O operations

## ./my_project/src/config.py

INPUT: YAML configuration file
OUTPUT: Parsed configuration dictionary
TASK: Parse and validate application configuration
CONDITIONS: File must be valid YAML
PREFERENCES: Use dataclasses for type safety
```

---

## Suggested Workflow

1. **Day 1**: Create project structure
2. **Day 2**: Add pseudocode for key files
3. **Day 3**: Run `blueprint_renderer.py` to create skeleton
4. **Day 4**: Run `pseudocode_renderer.py` to convert to real code
5. **Iterate**: Edit pseudocode, regenerate code as needed

---

## Next Steps

1. Test the current `starterfile_creator.py`
2. Decide which enhancement features to implement
3. Consider adding a `--quick` mode for automation
4. Create example templates

Would you like me to:
- Add any of the suggested features?
- Fix the `blueprint_renderer.py` tree parsing issue?
- Create example templates?
- Build an interactive tree visualizer?
