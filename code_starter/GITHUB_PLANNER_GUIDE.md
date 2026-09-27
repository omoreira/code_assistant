# GitHub Repo Planner - Usage Guide

## What is This?

`github_repo_planner.py` is an interactive tool that automates the setup of the code-assistant project for GitHub distribution. It:

1. Asks you 10 implementation questions
2. Validates your answers
3. Generates all necessary files (.gitignore, LICENSE, setup.py, etc.)
4. Creates the proper directory structure
5. Provides a summary report

## Quick Start (5 minutes)

```bash
# Run the planner
python code_starter/github_repo_planner.py

# Select option 1: Answer Implementation Questions
# Fill out the 10 questions
# Select option 3: Generate Repository Structure
# Done!
```

## The 10 Implementation Questions

### Q1: Module Structure
- **Option A**: Separate repositories
- **Option B**: Single mono-repo (RECOMMENDED)
- **Option C**: Main repo + submodules

### Q2: Configuration Files
Do you want `config/` directory with YAML/JSON files?
- Recommended: **Yes** (better for production)

### Q3: Virtual Environment
How to handle venv?
- **Option 1**: Document in README
- **Option 2**: Create setup script
- **Option 3**: Both (RECOMMENDED)

### Q4: Module Placeholders
Create empty code_analyzer/ and code_executor/ directories?
- Recommended: **Yes** (shows full structure)

### Q5: Testing Strategy
What tests to create?
- **Option 1**: Unit tests only
- **Option 2**: Integration tests only
- **Option 3**: Both (RECOMMENDED)
- **Option 4**: None

### Q6: Documentation Location
Where should module docs go?
- **Option 1**: Each module: `code_starter/docs/` (RECOMMENDED)
- **Option 2**: Root: `docs/code_starter/`
- **Option 3**: Move existing docs

### Q7: CI/CD
Add GitHub Actions workflows?
- Recommended: **No** (can add later)

### Q8: Installation Method
How should users install?
- **Option A**: `pip install -e .` (RECOMMENDED)
- **Option B**: Direct script execution
- **Option C**: Command-line tools

### Q9: Shared Code
Create `shared/` directory for utilities?
- **Option 1**: Yes (full utilities)
- **Option 2**: No (self-contained)
- **Option 3**: Minimal (RECOMMENDED)

### Q10: GitHub Details
- Your GitHub username
- Repository name (default: code-assistant)
- Your name
- Your email

## Menu Options

```
1. Answer Implementation Questions
   → Interactive Q&A through all 10 questions
   
2. View Current Configuration
   → See what's been configured so far
   
3. Generate Repository Structure
   → Create all files based on answers
   → THIS IS THE KEY STEP!
   
4. Quick Setup (Use Defaults)
   → Recommended defaults + your GitHub info
   → Fastest option
   
5. Manual Configuration
   → Edit individual settings manually
   
6. Save Configuration
   → Save answers to JSON for later
   
7. Load Configuration
   → Load from saved JSON
   
8. Generate Summary Report
   → See everything before generating
   
9. Exit
   → Quit the program
```

## Recommended Workflow

### Option 1: Quick Start (Recommended)
```bash
python code_starter/github_repo_planner.py

> Select: 4 (Quick Setup)
> Enter GitHub username: myusername
> Enter your name: Jane Doe
> Enter your email: jane@example.com

> Select: 3 (Generate Repository Structure)
> Select: 8 (View Summary)
```

**Time: 2 minutes**

### Option 2: Detailed Setup
```bash
python code_starter/github_repo_planner.py

> Select: 1 (Answer Questions)
> Answer all 10 questions...
> Select: 8 (View Summary)
> Select: 3 (Generate Repository Structure)
```

**Time: 5 minutes**

### Option 3: Save & Review
```bash
python code_starter/github_repo_planner.py

> Select: 1 (Answer Questions)
> Answer all 10 questions...
> Select: 6 (Save Configuration)
> Filename: my_repo_config.json
> Exit

# Review the file
cat my_repo_config.json

# Run again to generate
python code_starter/github_repo_planner.py

> Select: 7 (Load Configuration)
> Filename: my_repo_config.json
> Select: 3 (Generate Repository Structure)
```

**Time: 10 minutes**

## Files Generated

### Critical Files
- `.gitignore` - Git ignore rules
- `LICENSE` - MIT License
- `setup.py` - Python package setup
- `requirements.txt` - Dependencies
- `requirements-dev.txt` - Dev dependencies
- `README.md` (root) - Project overview
- `__init__.py` files in packages

### Optional Files (Based on Answers)
- `config/` - Configuration directory
- `code_analyzer/` - Placeholder module 2
- `code_executor/` - Placeholder module 3
- `tests/` - Test structure
- `shared/` - Shared utilities
- `.github/workflows/` - CI/CD pipelines

## Example Run

```
╔════════════════════════════════════════════════════════════════╗
║ GITHUB REPOSITORY PLANNER - SUMMARY REPORT                    ║
╚════════════════════════════════════════════════════════════════╝

Project: code-assistant
Repository: https://github.com/myusername/code-assistant
Author: Jane Doe <jane@example.com>

────────────────────────────────────────────────────────────────
CONFIGURATION SUMMARY
────────────────────────────────────────────────────────────────
Module Structure .................. B
Configuration Files .............. Yes
venv Setup ........................ both
Module Placeholders ............... Yes
Testing Strategy .................. both
Documentation Location ............ per-module
CI/CD Workflows ................... No
Installation Method ............... A
Shared Code ....................... minimal

FILES CREATED:
✓ .gitignore
✓ LICENSE
✓ setup.py
✓ requirements.txt
✓ requirements-dev.txt
✓ README.md (root)
✓ config/ directory
✓ Module placeholders
✓ tests/ directory
✓ shared/ directory

✓ Repository structure generated successfully!
```

## After Generation

Once files are generated:

1. **Review files**
   ```bash
   cat README.md
   cat setup.py
   cat requirements.txt
   ```

2. **Initialize git**
   ```bash
   git init
   git add .
   git commit -m "Initial repository structure"
   ```

3. **Create GitHub repo**
   - Go to github.com
   - Create new repository
   - Name it "code-assistant"

4. **Push to GitHub**
   ```bash
   git remote add origin https://github.com/yourusername/code-assistant.git
   git branch -M main
   git push -u origin main
   ```

5. **Set up development environment**
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements-dev.txt
   ```

## Troubleshooting

**Q: Where are the files created?**
A: Current directory (where you run the script from)

**Q: Can I edit the generated files?**
A: Yes! They're just starting points. Edit them as needed.

**Q: Can I run this multiple times?**
A: Yes, but files will be overwritten. Save your answers first with option 6.

**Q: What if I mess up?**
A: Delete the generated files and run again.

**Q: Can I add this to an existing project?**
A: Yes! Files will be created/overwritten. Backup first if needed.

## Next Steps

1. **Fill out the questions** (Option 1 or 4)
2. **Generate the structure** (Option 3)
3. **Review the files** (Option 8)
4. **Push to GitHub** (git commands above)
5. **Set up development** (venv + pip)

## Tips

- Use **Quick Setup (Option 4)** for fastest setup
- Use **Save Configuration (Option 6)** to save your choices
- Use **View Summary (Option 8)** before generating
- The tool won't overwrite existing `code_starter/` files
- Keep your `repo_config.json` file for future reference

---

That's it! You'll have a GitHub-ready project structure in minutes! 🚀
