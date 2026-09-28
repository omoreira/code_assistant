# Shell Scripts Guide

Complete guide to using the Linux shell scripts for code-assistant modules.

---

## 📋 Overview

Six automated shell scripts are provided to make running and managing code-assistant easy:

| Script | Purpose | When to Use |
|--------|---------|------------|
| `setup.sh` | Setup environment & install dependencies | First time setup |
| `install_deps.sh` | Install/reinstall dependencies | Update packages |
| `run_code_assistant.sh` | Main interactive menu | Choose which module to run |
| `run_starter.sh` | Run code_starter directly | Quick project creation |
| `run_debugger.sh` | Run code_debugger | Debug code (in development) |
| `run_patcher.sh` | Run code_patcher | Patch code (in development) |

---

## ✅ Script Status

All scripts have been:
- ✅ Created successfully
- ✅ Checked for syntax errors
- ✅ Made executable (`chmod +x`)
- ✅ Include error handling
- ✅ Support multiple options

---

## 🚀 Quick Start

### First Time Setup

```bash
# 1. Make setup script executable (if needed)
chmod +x scripts/setup.sh

# 2. Run setup (creates venv, installs dependencies)
./scripts/setup.sh

# That's it! You're ready to use code-assistant
```

### Using the Scripts

```bash
# Run main menu (choose any module)
./scripts/run_code_assistant.sh

# Or run specific module
./scripts/run_starter.sh
./scripts/run_debugger.sh
./scripts/run_patcher.sh
```

---

## 📖 Detailed Script Documentation

### 1. `setup.sh` - Initial Setup

**Purpose:** Set up complete environment from scratch

**Usage:**
```bash
./scripts/setup.sh
```

**What it does:**
1. ✅ Checks Python 3 is installed
2. ✅ Checks pip is available
3. ✅ Creates virtual environment (`venv/`)
4. ✅ Upgrades pip, setuptools, wheel
5. ✅ Installs runtime dependencies
6. ✅ Optionally installs dev dependencies
7. ✅ Installs code-assistant package
8. ✅ Verifies all modules are accessible

**Interactive prompts:**
- Ask if venv exists: "Remove and recreate? (y/n)"
- Ask about dev dependencies: "Install development dependencies? (y/n)"

**Output:**
```
╔════════════════════════════════════════════════════════════╗
║     Code Assistant - Environment Setup Script            ║
╚════════════════════════════════════════════════════════════╝

ℹ Checking Python installation...
✓ Python 3.9 found
ℹ Checking pip installation...
✓ pip is installed
ℹ Setting up virtual environment...
✓ Virtual environment created at ./venv
✓ Virtual environment activated
...
✓ Environment setup completed successfully!

Next Steps:
1. Run the main menu: ./run_code_assistant.sh
...
```

---

### 2. `install_deps.sh` - Dependency Installation

**Purpose:** Install or reinstall dependencies

**Usage:**
```bash
./scripts/install_deps.sh              # Install runtime only
./scripts/install_deps.sh --dev        # Install runtime + dev
./scripts/install_deps.sh --help       # Show help
```

**Options:**
- No argument: Install only runtime dependencies
- `--dev`: Install both runtime and development
- `-h, --help`: Show help message

**What it does:**
1. ✅ Checks if venv exists
2. ✅ Activates virtual environment
3. ✅ Installs dependencies from requirements files

**Example:**
```bash
$ ./install_deps.sh --dev

Code Assistant - Install Dependencies

✓ Virtual environment activated
ℹ Installing dependencies...
✓ Dependencies installed
ℹ Installing development dependencies...
✓ Development dependencies installed

✓ All dependencies installed successfully
```

---

### 3. `run_code_assistant.sh` - Main Menu

**Purpose:** Interactive menu to choose and run any module

**Usage:**
```bash
./scripts/run_code_assistant.sh
```

**Features:**
- ✅ Automatic venv setup if needed
- ✅ Interactive menu to choose module
- ✅ Shows system status
- ✅ Handles dependency installation
- ✅ Color-coded output

**Menu Options:**
```
╔════════════════════════════════════════════════════════════╗
║           Code Assistant - Main Menu                      ║
╚════════════════════════════════════════════════════════════╝

Available Modules:

  1) code_starter     - Project creation and code generation
  2) code_debugger    - Code analysis and debugging (in development)
  3) code_patcher     - Code refactoring and patching (in development)
  4) Setup/Status     - Setup environment or check status
  5) Exit             - Exit program

Choose an option (1-5):
```

**Status Display (Option 4):**
```
System Status:

  Virtual Environment: ✓ Installed
  Requirements File:   ✓ Found
  Dependencies:        ✓ Installed
```

**Example workflow:**
```bash
$ ./run_code_assistant.sh
# Shows menu
# User enters: 1
# Launches code_starter module
```

---

### 4. `run_starter.sh` - Code Starter Quick Launch

**Purpose:** Quick way to run code_starter module

**Usage:**
```bash
./scripts/run_starter.sh                    # Interactive mode (default)
./scripts/run_starter.sh -i                 # Same as above
./scripts/run_starter.sh --interactive      # Same as above
./scripts/run_starter.sh -c                 # Create new project
./scripts/run_starter.sh --create           # Same as above
./scripts/run_starter.sh --status           # Show status
./scripts/run_starter.sh --setup            # Setup environment
./scripts/run_starter.sh -h                 # Show help
```

**Options:**
- `-h, --help`: Show help message
- `-i, --interactive`: Run interactive mode (default)
- `-c, --create`: Create new project with prompts
- `--status`: Show environment status
- `--setup`: Setup/install dependencies

**Examples:**

**Interactive mode:**
```bash
$ ./scripts/run_starter.sh
✓ Virtual environment activated
✓ Dependencies installed

Launching code_starter in interactive mode...
# Interactive menu appears
```

**Create project:**
```bash
$ ./scripts/run_starter.sh --create

Enter project name: my_project
Enter project description: My awesome project
Enter modules (comma-separated): models,views,utils
Enter dependencies (comma-separated): flask,sqlalchemy

✓ Project specification saved to: my_project.pseudo
```

**Check status:**
```bash
$ ./scripts/run_starter.sh --status

Environment Status:

  Virtual Environment: ✓ Ready
  Dependencies:        ✓ Installed
  Code Starter:        ✓ Found
```

---

### 5. `run_debugger.sh` - Code Debugger Launch

**Purpose:** Run code_debugger module (currently in development)

**Usage:**
```bash
./scripts/run_debugger.sh                   # Show status (module in dev)
./scripts/run_debugger.sh --info            # Show detailed info
./scripts/run_debugger.sh --docs            # Show documentation links
./scripts/run_debugger.sh --status          # Show environment status
./scripts/run_debugger.sh -h                # Show help
```

**Options:**
- `-h, --help`: Show help
- `--info`: Show module info and roadmap
- `--docs`: Show documentation links
- `--status`: Show environment status

**Features:**
- ✅ Shows development status
- ✅ Lists planned features
- ✅ Shows implementation roadmap
- ✅ Points to documentation

**Example output:**
```bash
$ ./scripts/run_debugger.sh --info

Code Debugger Module

Current Status: IN DEVELOPMENT

Purpose:
  Intelligent code analysis and debugging for Python code

Planned Features:
  • Code quality analysis and metrics
  • Bug detection and diagnosis
  • Performance profiling and bottleneck detection
  • Automated test generation
  • Code improvement suggestions

Implementation Roadmap:
  Phase 1: Basic code analyzer
  Phase 2: Error diagnosis engine
  Phase 3: Performance profiler
  Phase 4: Suggestions engine
  Phase 5: Test generation

For more details, see: docs/code_debugger/README.md
```

---

### 6. `run_patcher.sh` - Code Patcher Launch

**Purpose:** Run code_patcher module (currently in development)

**Usage:**
```bash
./scripts/run_patcher.sh                    # Show status (module in dev)
./scripts/run_patcher.sh --info             # Show detailed info
./scripts/run_patcher.sh --docs             # Show documentation links
./scripts/run_patcher.sh --status           # Show environment status
./scripts/run_patcher.sh -h                 # Show help
```

**Options:**
- `-h, --help`: Show help
- `--info`: Show module info and roadmap
- `--docs`: Show documentation links
- `--status`: Show environment status

**Similar to `run_debugger.sh` but for patcher module**

---

## 🔧 Common Tasks

### Task 1: Fresh Installation

```bash
# 1. Make scripts executable
chmod +x scripts/*.sh

# 2. Run setup
./scripts/setup.sh

# Answer the prompts
# - Virtual environment creation: auto (creates if not exists)
# - Dev dependencies: choose y or n

# 3. Done! Ready to use
```

### Task 2: Update Dependencies

```bash
# Update runtime dependencies
./scripts/install_deps.sh

# Update runtime + development
./scripts/install_deps.sh --dev
```

### Task 3: Run code_starter Interactively

```bash
# Option A: Use main menu
./scripts/run_code_assistant.sh
# Then choose option 1

# Option B: Direct
./scripts/run_starter.sh
```

### Task 4: Create New Project from Command Line

```bash
./scripts/run_starter.sh --create
# Follow prompts to create project specification
```

### Task 5: Check Environment Status

```bash
# Option A: Main menu
./scripts/run_code_assistant.sh
# Then choose option 4

# Option B: Direct
./scripts/run_starter.sh --status
```

### Task 6: Reinstall Everything

```bash
# Remove venv
rm -rf venv

# Reinstall from scratch
./scripts/setup.sh
```

### Task 7: Use Virtual Environment Manually

```bash
# Activate venv
source venv/bin/activate

# Now use python, pip, etc. directly
python3 -c "from code_refractor import RefactoringVerifier; ..."

# Deactivate when done
deactivate
```

---

## 📊 Script Features Summary

### Color Output
All scripts use color-coded output:
- 🔴 **Red** (`${RED}`): Errors
- 🟢 **Green** (`${GREEN}`): Success
- 🟡 **Yellow** (`${YELLOW}`): Information
- 🔵 **Blue** (`${BLUE}`): Headers/Sections

### Error Handling
- ✅ Checks Python 3 exists
- ✅ Checks pip available
- ✅ Validates venv exists
- ✅ Verifies dependencies
- ✅ Reports missing files
- ✅ Exits gracefully on errors

### Interactive Prompts
- User-friendly yes/no questions
- Clear option selection menus
- Input validation where needed
- Cancel with Ctrl+C anytime

### Automation
- Auto-creates venv if needed
- Auto-installs dependencies
- Auto-activates environment
- Auto-verifies installation

---

## 🐛 Troubleshooting

### Issue: "Permission denied" when running scripts

**Solution:**
```bash
chmod +x scripts/*.sh
```

### Issue: "Python 3 not found"

**Solution:**
```bash
# Check Python is installed
python3 --version

# If not, install Python 3.8+
# Ubuntu/Debian:
sudo apt-get install python3 python3-venv python3-pip

# macOS:
brew install python3
```

### Issue: "Virtual environment not found"

**Solution:**
```bash
# Run setup first
./scripts/setup.sh
```

### Issue: Module import errors

**Solution:**
```bash
# Reinstall dependencies
./scripts/install_deps.sh --dev

# Or full setup
./scripts/setup.sh
```

### Issue: Scripts not executable

**Solution:**
```bash
# Make all scripts executable
chmod +x scripts/*.sh

# Verify
ls -l scripts/
# Should show 'x' in permissions
```

### Issue: "yaml module not found"

**Solution:**
```bash
# Install dependencies
./scripts/install_deps.sh

# Or if venv not activated:
./scripts/setup.sh
```

---

## 📝 Script Structure

All scripts follow this pattern:

```bash
#!/bin/bash                          # Shebang

# Constants
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$SCRIPT_DIR"

# Color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'

# Helper functions
print_error()    { echo -e "${RED}✗ Error: $1${NC}" >&2; }
print_success()  { echo -e "${GREEN}✓ $1${NC}"; }
print_info()     { echo -e "${YELLOW}ℹ $1${NC}"; }

# Main logic
check_python()
check_venv()
activate_venv()
install_deps()

# Main function
main() {
    # ... orchestrate functions ...
}

main "$@"
```

---

## 🎯 Script Usage Flowchart

```
START
  │
  ├─→ ./scripts/setup.sh                      (First time only)
  │   ├─ Creates venv
  │   ├─ Installs deps
  │   └─ Verifies install
  │
  └─→ ./scripts/run_code_assistant.sh        (Daily use)
      ├─ Option 1: run_starter.sh
      ├─ Option 2: run_debugger.sh
      ├─ Option 3: run_patcher.sh
      ├─ Option 4: Show status
      └─ Option 5: Exit

Or use specific scripts directly:
  ├─ ./scripts/run_starter.sh
  ├─ ./scripts/run_debugger.sh
  └─ ./scripts/run_patcher.sh
```

---

## 📚 Related Documentation

- **README.md** - Project overview
- **POST_GENERATION_GUIDE.md** - Setup steps
- **docs/code_starter/README.md** - Starter module guide
- **docs/CONTRIBUTING.md** - Development workflow

---

## ✨ Key Features

✅ **User-Friendly**
- Automatic environment setup
- Interactive menus
- Clear prompts and messages
- Color-coded output

✅ **Robust**
- Error checking
- Validation
- Graceful failure
- Helpful error messages

✅ **Flexible**
- Multiple options
- Can run individual modules
- Can run main menu
- Manual environment control

✅ **Documented**
- Inline comments
- Help options (-h)
- Usage examples
- Clear output

---

## 🎉 You're All Set!

All 6 scripts are ready to use:

1. **First time:** Run `./scripts/setup.sh`
2. **Then:** Use `./scripts/run_code_assistant.sh` or specific scripts
3. **Manage:** Use `./scripts/install_deps.sh` for updates

**That's it! Enjoy using code-assistant!** 🚀

---

*Scripts created and tested on: 2024-01-01*  
*All scripts: Bash 4.0+, Linux/macOS compatible*
