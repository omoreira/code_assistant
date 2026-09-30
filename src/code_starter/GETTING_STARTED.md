# Getting Started with Local Coding Assistant

Welcome! This guide will help you understand and use the local coding assistant system.

## 🎯 What You Have

Three powerful tools that work together to turn ideas into working code:

1. **starterfile_creator.py** - Create project specifications interactively
2. **blueprint_renderer.py** - Build project skeleton from specifications  
3. **pseudocode_renderer.py** - Generate real code from pseudocode

## 📖 Documentation Structure

### For Beginners: Start Here
1. **README.md** - High-level overview and quick start
2. **GETTING_STARTED.md** - This file! Step-by-step guide
3. **DEMO_WORKFLOW.md** - Complete example with real code output

### For In-Depth Understanding
1. **PROJECT_SUMMARY.md** - Architecture and design details
2. **STARTERFILE_CREATOR_GUIDE.md** - Complete guide to the creator tool

### For Reference
1. **starterfile.pseudo** - Example starterfile format
2. Source files (*.py) - The actual tools

## 🚀 5-Minute Quickstart

### 1. Create a Simple Project (2 minutes)

```bash
python starterfile_creator.py
```

When prompted:
- **Root directory**: `./hello_world`
- **Add directory**: `src` 
  - Add file: `main.py`
  - Add file: `config.py`
- **Add directory**: `tests`
  - Add file: `test_main.py`
- **Done with structure**

Then for each file, add simple pseudocode:
```
INPUT: User input
OUTPUT: Greeting message  
TASK: Print a greeting
CONDITIONS: None
PREFERENCES: Use f-strings
```

Save as `starterfile.pseudo`.

### 2. Create Project Skeleton (1 minute)

```bash
python blueprint_renderer.py
```

You'll see:
```
Created Directories (3):
  ✓ ./hello_world
  ✓ ./hello_world/src
  ✓ ./hello_world/tests

Created Files (3):
  ✓ ./hello_world/src/main.py
  ✓ ./hello_world/src/config.py
  ✓ ./hello_world/tests/test_main.py
```

### 3. Generate Code (2 minutes)

```bash
python pseudocode_renderer.py
```

**Note**: This requires ollama with deepseek-coder model installed:
```bash
ollama run deepseek-coder:6.7b
```

## 📚 Understanding the System

### The Three-Stage Pipeline

```
Stage 1: CREATE SPECIFICATION
┌─────────────────────────────────────┐
│  starterfile_creator.py             │
│  ↓                                  │
│  Define project structure           │
│  Define pseudocode for each file    │
│  ↓                                  │
│  Output: starterfile.pseudo         │
└─────────────────────────────────────┘

Stage 2: CREATE SKELETON
┌─────────────────────────────────────┐
│  blueprint_renderer.py              │
│  ↓                                  │
│  Read: starterfile.pseudo           │
│  ↓                                  │
│  Create directories                 │
│  Create empty files                 │
│  ↓                                  │
│  Output: File system structure      │
└─────────────────────────────────────┘

Stage 3: GENERATE CODE
┌─────────────────────────────────────┐
│  pseudocode_renderer.py             │
│  ↓                                  │
│  Mode A: Read starterfile.pseudo    │
│  (Fresh project initialization)     │
│  ↓                                  │
│  Call local LLM                     │
│  Generate real code                 │
│  ↓                                  │
│  Output: Working code files         │
└─────────────────────────────────────┘
```

### File Formats

#### starterfile.pseudo
Contains two sections:

**REPOMAP**: Directory tree structure
```
# REPOMAP

./my_project
        |___________src/
        |               |______main.py
        |               |______utils.py
```

**PSEUDOCODE**: File specifications
```
# PSEUDOCODE

## ./my_project/src/main.py

INPUT: Command line arguments
OUTPUT: Processed result
TASK: Main entry point
CONDITIONS: Config file required
PREFERENCES: Use type hints
```

## 💻 Detailed Workflows

### Workflow 1: Fresh Project

**Goal**: Create a new project from scratch

1. Run `starterfile_creator.py`
   - Build directory structure interactively
   - Add pseudocode for each file
   - Save to `starterfile.pseudo`

2. Run `blueprint_renderer.py`
   - Creates all directories and files
   - Verifies everything was created

3. Run `pseudocode_renderer.py` (Mode A)
   - Reads `starterfile.pseudo`
   - Verifies files are empty
   - Generates code from pseudocode
   - Deletes `starterfile.pseudo` (cleanup)

**Time**: ~10-30 minutes (depending on project size)
**Result**: Fully working project ready to use

### Workflow 2: Add Features to Existing Project

**Goal**: Add new features to an existing project

1. Add pseudocode to an existing file:
   ```python
   """
   Pseudo Code
   INPUT: User data
   OUTPUT: Processed result
   TASK: Process user input
   CONDITIONS: None
   PREFERENCES: Use async/await
   """
   ```

2. Run `pseudocode_renderer.py` (Mode B)
   - Scans for `"""Pseudo Code"""` markers
   - Generates code from inline pseudocode
   - No cleanup step

**Time**: ~5 minutes per feature
**Result**: New working feature code

## 🎓 Learning By Example

### Example 1: Simple Script

**Scenario**: Create a simple greeting script

```bash
python starterfile_creator.py
# Root: ./greeter
# Add file: main.py
# Pseudocode:
#   INPUT: Name as argument
#   OUTPUT: Greeting message
#   TASK: Print personalized greeting
#   CONDITIONS: None
#   PREFERENCES: Use argparse

python blueprint_renderer.py
# Creates: ./greeter/main.py (empty)

python pseudocode_renderer.py
# Generates complete greeting script
```

### Example 2: Web API Project

See `DEMO_WORKFLOW.md` for a complete data processing project example.

## 🔧 Configuration & Setup

### Requirements
- Python 3.8 or higher
- No external dependencies for basic tools

### Optional: Code Generation Setup

To actually generate code, install ollama:

**macOS/Linux**:
```bash
curl -fsSL https://ollama.ai/install.sh | sh
ollama run deepseek-coder:6.7b
```

**Windows**: Download from https://ollama.ai

Once running:
```bash
ollama run deepseek-coder:6.7b
# Leave this running in the background
# In another terminal:
python pseudocode_renderer.py
```

## ⚡ Tips & Tricks

### Tip 1: Preview Before Saving
In `starterfile_creator.py`, use option 4 (Preview) to check your structure before saving.

### Tip 2: Start Small
Begin with simple 2-3 file projects to understand the workflow, then scale up.

### Tip 3: Good Pseudocode
The better your pseudocode specification, the better the generated code:

**Bad**:
```
TASK: Do something
```

**Good**:
```
TASK: Load CSV data and return as Pandas DataFrame
      Handle missing values by filling with 0
      Log warnings for malformed rows
CONDITIONS: File must be valid CSV with headers
PREFERENCES: Use pandas read_csv with error handling
```

### Tip 4: Iterate
Don't try to generate everything at once. Build incrementally:
- Generate core functionality
- Test it
- Add more features in Mode B
- Iterate

### Tip 5: Use Git
Track your changes:
```bash
git init
git add .
git commit -m "Initial skeleton from starterfile_creator"
# ... run pseudocode_renderer
git add .
git commit -m "Generated initial code from pseudocode"
```

## 🐛 Troubleshooting

### Problem: blueprint_renderer says "Could not parse REPOMAP"
**Solution**: Make sure `starterfile.pseudo` was properly saved by starterfile_creator.py

### Problem: pseudocode_renderer doesn't find LLM
**Solution**: Ensure ollama is installed and running:
```bash
ollama run deepseek-coder:6.7b
```

### Problem: Generated code looks wrong
**Solution**: 
1. Check your pseudocode - is it clear enough?
2. Try more specific instructions in "PREFERENCES"
3. Split complex tasks into multiple smaller files

## ❓ FAQ

**Q: Can I edit starterfile.pseudo manually?**
A: Yes! You can edit it as a text file or use `starterfile_creator.py` again.

**Q: What if I want to use a different LLM?**
A: Modify `pseudocode_renderer.py` to call your preferred LLM instead of ollama.

**Q: Can I use this without ollama?**
A: Yes! blueprint_renderer.py doesn't need LLM. starterfile_creator.py doesn't need LLM. Only pseudocode_renderer.py needs LLM for code generation.

**Q: Will existing files be overwritten?**
A: No! All three tools check if files exist and skip them.

**Q: Can I mix pseudocode and real code?**
A: Yes! You can have some real code and some pseudocode. Only the pseudocode sections will be regenerated in Mode B.

## 🎬 Next Steps

1. **Read**: Start with README.md
2. **Explore**: Run `python starterfile_creator.py` and explore the menu
3. **Example**: Follow the data processing example in DEMO_WORKFLOW.md
4. **Create**: Build your first real project
5. **Iterate**: Use Mode B to keep adding features

## 📞 Getting Help

1. Check PROJECT_SUMMARY.md for architecture questions
2. Check STARTERFILE_CREATOR_GUIDE.md for creator tool help
3. Check DEMO_WORKFLOW.md for examples
4. Review the source files (they're well-commented)

## ✨ You're Ready!

You now have a powerful system for rapidly prototyping and building projects. Start with simple projects and scale up as you get comfortable.

Happy coding! 🚀

---

**Questions?** Review the documentation files or check the source code - it's designed to be readable and understandable.
