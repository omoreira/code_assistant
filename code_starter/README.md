# Local Coding Assistant

A complete system for creating and generating project code from pseudocode specifications using local LLMs.

## 🎯 What This Does

Convert your project ideas into working code in **three simple steps**:

1. **Define** your project structure interactively
2. **Create** the directory skeleton
3. **Generate** real code from pseudocode specifications

All locally, using your own LLM. No cloud APIs. No dependencies beyond Python.

## 📦 Components

### 1. `starterfile_creator.py`
Interactive wizard to create project specifications.
- Define directory structure
- Add pseudocode for each file
- Generates `starterfile.pseudo`

**Usage**: `python starterfile_creator.py`

### 2. `blueprint_renderer.py`
Scaffolds the project structure from specifications.
- Reads `starterfile.pseudo`
- Creates directories and empty files
- Non-destructive (won't overwrite existing files)

**Usage**: `python blueprint_renderer.py`

### 3. `pseudocode_renderer.py`
Converts pseudocode into real, working code using your local LLM.
- **Mode A**: Fresh projects (from starterfile.pseudo)
- **Mode B**: Existing projects (from inline pseudocode comments)

**Usage**: `python pseudocode_renderer.py`

## 🚀 Quick Start

### Step 1: Create Your Project Definition
```bash
python starterfile_creator.py
# Follow prompts to build structure and add pseudocode
# Saves to: starterfile.pseudo
```

### Step 2: Create Project Skeleton
```bash
python blueprint_renderer.py
# Creates all directories and empty files
```

### Step 3: Generate Code
```bash
python pseudocode_renderer.py
# Uses local LLM to convert pseudocode to real code
# Requires: ollama + deepseek-coder:6.7b
```

## 📋 File Format

### starterfile.pseudo
```
# REPOMAP

./project_name
        |___________src/
        |               |______main.py
        |               |______utils.py
        |___________tests/
                        |______ test_main.py

# PSEUDOCODE

## ./project_name/src/main.py

INPUT: Configuration object
OUTPUT: Application instance
TASK: Initialize the main application
CONDITIONS: Config must exist
PREFERENCES: Use type hints
```

## 🔄 Workflow

```
starterfile_creator.py
        ↓
   starterfile.pseudo
        ↓
   blueprint_renderer.py
        ↓
   Directory Structure
        ↓
   pseudocode_renderer.py (Mode A)
        ↓
   Real Code Files
        ↓
   [Iterate with Mode B for new features]
```

## 💡 Features

✅ **Interactive Project Builder** - No manual YAML/JSON needed
✅ **Dual-Mode Code Generation** - Fresh projects & existing project enhancement
✅ **Local-First** - All processing happens on your machine
✅ **Non-Destructive** - Never overwrites existing files
✅ **Modular** - Each tool can be used independently
✅ **Zero Dependencies** - Only Python 3.8+ needed (for core tools)

## 📚 Documentation

- **PROJECT_SUMMARY.md** - Complete overview of all components
- **STARTERFILE_CREATOR_GUIDE.md** - Detailed guide for the creator tool
- **DEMO_WORKFLOW.md** - Full example walkthrough with generated code

## 🛠️ Requirements

### Core
- Python 3.8+
- No external dependencies for blueprint_renderer or starterfile_creator

### For Code Generation (pseudocode_renderer)
- ollama (local LLM server)
- deepseek-coder:6.7b model (or compatible LLM)

### Optional
- pytest (testing)
- black (code formatting)
- mypy (type checking)

## 🐛 Known Issues

- blueprint_renderer tree parsing needs refinement for complex structures
- pseudocode_renderer LLM integration requires ollama setup
- No GUI version yet (planned)

## 🔮 Future Enhancements

- [ ] Template system (save/load project templates)
- [ ] Pre-built project templates (FastAPI, Django, etc.)
- [ ] Load existing starterfile.pseudo for editing
- [ ] GUI version (web or Tkinter)
- [ ] Filesystem scanner (auto-detect structure)
- [ ] Better validation and error handling
- [ ] Integration with git

## 📝 Example Projects

See `DEMO_WORKFLOW.md` for a complete example of creating a data processing pipeline.

## 🎓 Learning Resources

1. Read `PROJECT_SUMMARY.md` for architecture overview
2. Run `python starterfile_creator.py` to explore
3. Follow `DEMO_WORKFLOW.md` for a complete example
4. Check `STARTERFILE_CREATOR_GUIDE.md` for creator tool features

## ⚖️ License

MIT

## 🤝 Contributing

Suggestions and improvements welcome!

Current priorities:
1. Fix blueprint_renderer tree parsing
2. Test pseudocode_renderer with ollama
3. Add more template examples
4. Improve error messages

---

**Status**: In Active Development

Last Updated: 2024
