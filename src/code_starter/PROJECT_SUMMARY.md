# Local Coding Assistant - Project Summary

## Overview
You're building a **local coding assistant** that converts pseudo code into real code using a local LLM (like deepseek-coder:6.7b). This project has three main components:

---

## 🎯 Core Components

### 1. **blueprint_renderer.py** ✅ (In Progress)
**Purpose**: Scaffolds the project structure from a REPOMAP definition

**Current Status**:
- Parses `starterfile.pseudo` REPOMAP section
- Creates directory tree structure
- Creates empty placeholder files
- Skips files/directories that already exist
- Returns success/fail status

**What It Does**:
```bash
python blueprint_renderer.py
# Reads: starterfile.pseudo
# Creates: Project directory structure
# Output: success/fail message
```

**Known Issues**:
- Tree parsing needs refinement for complex nested structures
- Need to handle intermediate directories that don't have trailing `/`

**Next Steps**:
- Fix REPOMAP parser to correctly handle all nesting levels
- Add validation of created structure
- Consider adding a `--verify` flag to check structure without creating files

---

### 2. **pseudocode_renderer.py** ✅ (Implemented - Needs LLM Integration)
**Purpose**: Converts pseudo code comments into real, functional code

**Features**:
- **Dual-mode operation**:
  - **Mode A** (Fresh Project): When `starterfile.pseudo` exists
    - Extracts pseudocode from starterfile.pseudo
    - Verifies all files/directories created
    - Verifies files are empty
    - Converts pseudocode → real code
    - Deletes starterfile.pseudo (cleanup)
  - **Mode B** (Existing Project): When `starterfile.pseudo` doesn't exist
    - Scans for `"""Pseudo Code"""` comments in existing files
    - Extracts and converts pseudocode
    - No cleanup needed

**What It Does**:
```bash
python pseudocode_renderer.py
# Mode A: Scaffolds from starterfile.pseudo
# Mode B: Enhances existing project files
# Uses: Local LLM (ollama + deepseek-coder:6.7b)
```

**Current Status**:
- Structure implemented
- LLM integration is a placeholder (needs ollama setup)
- Handles both modes correctly
- Has proper error handling and reporting

**Next Steps**:
- Test with actual LLM once ollama is set up
- Refine code generation prompts
- Add unit tests for conversion logic

---

### 3. **starterfile_creator.py** ✅ (Complete - Feature Ready)
**Purpose**: Interactive wizard to create `starterfile.pseudo` files

**Features**:
- **Interactive Menu System**
  - Create project structure step-by-step
  - View current structure
  - Add/edit pseudocode for each file
  - Preview formatted output
  - Save to file

- **Pseudocode Management**
  - Collect INPUT, OUTPUT, TASK, CONDITIONS, PREFERENCES for each file
  - Multi-line input support
  - Edit existing pseudocode

- **Validation & Preview**
  - View structure before saving
  - Check file/directory status
  - Generate properly formatted output

**What It Does**:
```bash
python starterfile_creator.py
# Interactive menu to build starterfile.pseudo
# Creates REPOMAP section (directory tree)
# Creates PSEUDOCODE section (file specifications)
# Saves to starterfile.pseudo
```

**Current Status**: ✅ Fully functional
- All menu options implemented
- Generates valid starterfile.pseudo format
- Interactive tree building works
- Pseudocode collection works

**Enhancements Possible**:
- Template system (save/load project templates)
- Batch file creation
- Edit mode (modify existing structure)
- Load existing starterfile.pseudo
- Project templates (FastAPI, Django, etc.)
- Validation rules
- GUI version

---

## 📁 File Structure Overview

```
./
├── blueprint_renderer.py          # Creates project structure (needs fix)
├── pseudocode_renderer.py         # Converts pseudo code to real code
├── starterfile_creator.py         # Interactive tool to create starterfile.pseudo
├── starterfile.pseudo             # Example project definition
├── STARTERFILE_CREATOR_GUIDE.md   # Usage guide for creator tool
├── PROJECT_SUMMARY.md             # This file
└── code_assistant/                # Example output from blueprint_renderer
    ├── blueprint_renderer.py       # (placeholder)
    └── pseudocode_renderer.py      # (placeholder)
```

---

## 🔄 Workflow / Pipeline

### Stage 1: Create Project Definition
```
User → starterfile_creator.py → starterfile.pseudo
```
- User runs interactive tool
- Builds directory structure
- Adds pseudocode for each file
- Saves to `starterfile.pseudo`

### Stage 2: Create Project Skeleton
```
starterfile.pseudo → blueprint_renderer.py → File System
```
- Reads `starterfile.pseudo` REPOMAP
- Creates all directories
- Creates empty placeholder files
- Returns success/fail

### Stage 3: Generate Real Code
```
starterfile.pseudo → pseudocode_renderer.py → Real Code
                        ↓
                    Local LLM
                 (deepseek-coder)
```
- Detects `starterfile.pseudo` exists (Mode A)
- Extracts pseudocode definitions
- Calls local LLM for each file
- Writes generated code to files
- Deletes `starterfile.pseudo` (cleanup)

### Stage 4+: Iterate
```
Existing Project → pseudocode_renderer.py (Mode B) → Enhanced Code
```
- Add `"""Pseudo Code"""` comments to existing files
- Run `pseudocode_renderer.py`
- Generates code from comments
- Keeps project growing

---

## 🛠️ Technical Details

### starterfile.pseudo Format

```
# REPOMAP

./project_root
        |___________src/
        |               |______main.py
        |               |______utils.py
        |___________tests/
                        |______ test_main.py

# PSEUDOCODE

## ./project_root/src/main.py

INPUT: Configuration object
OUTPUT: Application instance
TASK: Initialize the main application
CONDITIONS: Config must be valid
PREFERENCES: Use type hints

## ./project_root/src/utils.py

INPUT: Raw data
OUTPUT: Processed data
TASK: Utility functions for data processing
CONDITIONS: None
PREFERENCES: Use vectorization (numpy) for math operations
```

### Key Design Principles
1. **Tree-based Structure**: Uses ASCII art tree format for readability
2. **Pseudocode-First**: Code is generated from clear specifications
3. **Non-Destructive**: Existing files are never overwritten
4. **Local-First**: Uses local LLM, not cloud APIs
5. **Modular**: Each stage can run independently

---

## 🐛 Known Issues & TODO

### blueprint_renderer.py
- [ ] Tree parser doesn't handle intermediate directories without `/` suffix
- [ ] Need better indentation detection for nested levels
- [ ] Should validate that all listed files/dirs were successfully created

### pseudocode_renderer.py
- [ ] LLM integration needs ollama setup
- [ ] Code generation prompts need refinement
- [ ] Missing unit tests
- [ ] Should handle file encoding issues

### starterfile_creator.py
- [ ] REPOMAP generation could be improved for complex trees
- [ ] No load from existing file functionality
- [ ] No template system yet
- [ ] Could benefit from a non-interactive mode

### General
- [ ] No logging/debugging mode
- [ ] No dry-run capability
- [ ] No rollback functionality
- [ ] No progress indicators for large projects

---

## 🚀 Quick Start

### 1. Create a New Project
```bash
python starterfile_creator.py
# Follow interactive prompts to build project structure
# Save as starterfile.pseudo
```

### 2. Create Project Skeleton
```bash
python blueprint_renderer.py
# Creates directories and empty files from starterfile.pseudo
```

### 3. Generate Code
```bash
python pseudocode_renderer.py
# Converts pseudocode to real code using local LLM
```

---

## 📋 Example Usage

### Create a FastAPI project:

1. **Run Creator Tool**:
   ```bash
   python starterfile_creator.py
   # Menu 1: Create structure
   # → ./my_api (root)
   # → app/ (directory)
   #    → main.py (file)
   #    → models.py (file)
   #    → config.py (file)
   # → tests/ (directory)
   #    → test_main.py (file)
   # Menu 3: Add pseudocode for each file
   # Menu 5: Save to starterfile.pseudo
   ```

2. **Create Skeleton**:
   ```bash
   python blueprint_renderer.py
   # Output:
   # ✓ Created ./my_api
   # ✓ Created ./my_api/app
   # ✓ Created ./my_api/tests
   # ✓ Created ./my_api/app/main.py
   # ...
   ```

3. **Generate Code**:
   ```bash
   python pseudocode_renderer.py
   # ✓ Converted ./my_api/app/main.py
   # ✓ Converted ./my_api/app/models.py
   # ✓ Deleted starterfile.pseudo
   ```

4. **Result**: Fully functional FastAPI project ready to run!

---

## 💡 Future Enhancements

### Short-term (Easy)
- [ ] Add template system
- [ ] Batch file operations
- [ ] Edit/delete from tree
- [ ] Better error messages

### Medium-term (Moderate)
- [ ] Load existing starterfile.pseudo
- [ ] Pre-built templates (FastAPI, Django, etc.)
- [ ] Validation rules
- [ ] JSON export

### Long-term (Complex)
- [ ] GUI version (web-based)
- [ ] Filesystem scanner (auto-detect structure)
- [ ] Dependency tracking
- [ ] Code quality checks
- [ ] Integration with git

---

## 🔗 Dependencies

### Required
- Python 3.8+
- (No external Python packages for blueprint_renderer or starterfile_creator)

### Optional (For pseudocode_renderer)
- ollama (local LLM server)
- deepseek-coder:6.7b (or compatible LLM model)

### Recommended
- pytest (for testing)
- black (code formatting)
- mypy (type checking)

---

## 📝 Notes

- All tools are designed to be **non-destructive** (won't overwrite existing files)
- The system uses **pure Python** (no external dependencies for core tools)
- **Local-first** approach means complete privacy and offline capability
- **Modular design** allows each tool to be used independently

---

## 🎓 Learning Resources

- Pseudocode syntax: See examples in `starterfile.pseudo`
- Blueprint format: Check REPOMAP section examples
- Tool usage: See `STARTERFILE_CREATOR_GUIDE.md`

---

Created: 2024
Status: In Active Development
