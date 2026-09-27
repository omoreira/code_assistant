# Implementation Questions - GitHub Structure

Before I reorganize the project for GitHub, please answer these questions:

## 1. Module Structure

**Q: For the 3 modules, do you want:**

- [ ] Option A: Separate repos (code-starter, code-analyzer, code-executor)?
- [ ] Option B: Single mono-repo with 3 subdirectories?
- [x] Option C: Main repo + submodules?

**Current Plan**: Option C (main repo with submodules) - Is this correct?

---

## 2. Configuration

**Q: Do you want configuration files?**

- [x] Yes, create `config/` with YAML/JSON configs
  - [x] `config/defaults.yaml` - Default settings
  - [x] `config/logging_config.yaml` - Logging setup
  - [x] `.env.example` - Environment variables template
  
- [ ] No, just simple Python configs

**Note**: For LLM integration, you'll want to configure:
- LLM model name
- Ollama API endpoint
- Default output directory
- etc.

---

## 3. Virtual Environment

**Q: How should venv be handled?**

- [x] Document setup: `python -m venv venv`
- [ ] Create venv setup script: `scripts/setup_env.py`
- [ ] Both of the above

**Current Plan**: Document in README + Makefile target - OK? Yes

---

## 4. Module Placeholders

**Q: Should I create placeholder files for the other 2 modules?**

- [x] Yes: code_analyzer/ and code_executor/ with basic structure
- [ ] No: Just focus on code_starter for now
- [ ] Yes, but with more detail

**Current Plan**: Create minimal placeholders - OK?

---

## 5. Testing Structure

**Q: What's your testing strategy?**

- [ ] Unit tests only (test individual functions)
- [ ] Integration tests only (test full workflows)
- [x] Both unit + integration tests
- [ ] No tests initially (add later)

**Current Plan**: Create test structure, write basic tests - OK?

---

## 6. Documentation Structure

**Q: Where should module docs live?**

- [ ] In each module: `code_starter/docs/`, `code_analyzer/docs/`, etc.
- [x] All in root: `docs/code_starter/`, `docs/code_analyzer/`, etc.
- [ ] Move existing docs to `code_starter/docs/`?

**Current Plan**: Each module has its own `docs/` folder - OK?

---

## 7. Git Workflow

**Q: Do you want:**

- [ ] CI/CD workflows (.github/workflows) for automated testing?
- [ ] Pre-commit hooks for code quality?
- [ ] GitHub issue templates?
- [ ] Pull request templates?

**Current Plan**: Just core files initially, add CI/CD later - OK? Yes

---

## 8. Python Package Installation

**Q: How should users install this?**

Option A (Most Common):
```bash
pip install -e .
# Then: from code_starter import starterfile_creator
```

Option B (Scripts):
```bash
python code_starter/starterfile_creator.py
```

Option C (Command Line):
```bash
code-assistant-start  # After pip install
```

**Current Plan**: Option A or B - Which do you prefer? A

---

## 9. Shared Code

**Q: Should there be shared utilities?**

- [x] Yes: `shared/` directory for common functions
  - Config management
  - Logging utilities
  - File operations
  - LLM interface
  
- [ ] No: Each module self-contained
- [ ] Minimal: Just what's needed

**Current Plan**: Create `shared/` with common utilities - OK? YES

---

## 10. GitHub Repo Details

**Q: GitHub metadata:**

- Your GitHub username: omoreira
- Repository name: code_assistant ( not setup yet)
- Your name: Olga Moreira
- Email: olga.moreira@gmail.com

**Used in**: LICENSE, setup.py, README

---

## Quick Answers Template

Copy and paste these answers:

```
1. Module Structure: [ ] A [ ] B [ x] C
2. Configuration Files: [ ] Yes [ ] No
3. Virtual Environment: [ ] Script [ ] Docs [ ] Both
4. Module Placeholders: [ ] Yes [ ] No [ ] With detail
5. Testing: [ ] Unit [ ] Integration [ ] Both [ ] None
6. Documentation: [ ] Per-module [ ] Root [ ] Move existing
7. CI/CD: [ ] Yes [ ] No [ ] Later
8. Installation: [ ] A [ ] B [ ] C
9. Shared Code: [ ] Yes [ ] No [ ] Minimal
10. GitHub: 
    - Username: ___________
    - Repo name: ___________
    - Your name: ___________
    - Email: ___________
```

---

## My Recommendations

If you want to **get on GitHub ASAP**:
1. Answer questions 1, 8, 10
2. I'll create minimal GitHub-ready structure
3. You can iterate later

If you want **production-ready**:
1. Answer all questions
2. I'll create complete structure with all files
3. Ready to use immediately

---

**Which approach do you prefer?**
