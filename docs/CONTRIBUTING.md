# Contributing to Code Assistant

Thank you for your interest in contributing to Code Assistant! This document provides guidelines and instructions for contributing.

## Code of Conduct

- Be respectful and inclusive
- No harassment, discrimination, or abusive behavior
- Report violations to olga.moreira@gmail.com

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- Basic understanding of Python development
- Familiarity with pytest for testing

### Setup Development Environment

1. Fork the repository on GitHub
2. Clone your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/code_assistant.git
   cd code_assistant
   ```

3. Create virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

5. Setup pre-commit hooks:
   ```bash
   make setup-hooks  # (When available)
   ```

## Development Workflow

### 1. Create Feature Branch

```bash
git checkout -b feature/your-feature-name
# or for bug fixes:
git checkout -b bugfix/issue-description
```

Branch naming convention:
- `feature/` - New features
- `bugfix/` - Bug fixes
- `docs/` - Documentation updates
- `test/` - Test additions
- `refactor/` - Code refactoring

### 2. Make Your Changes

- Write clear, self-documenting code
- Follow PEP 8 style guide
- Add docstrings to functions and classes
- Include type hints where practical

### 3. Write Tests

- Add unit tests for new functions
- Add integration tests for new features
- Aim for >80% code coverage
- Tests go in `tests/` directory

```python
# Example test
import pytest
from code_starter import StarterFileCreator

def test_starterfile_creator_init():
    creator = StarterFileCreator()
    assert creator is not None

def test_create_project_spec():
    creator = StarterFileCreator()
    spec = creator.create_project_spec(
        name="test_project",
        description="Test",
        modules=["test"],
        dependencies=[]
    )
    assert spec["name"] == "test_project"
```

### 4. Run Code Quality Checks

```bash
# Run all checks
make lint
make format
make test

# Or individually:
# Format code
black code_starter code_debugger code_patcher shared tests

# Run linting
flake8 code_starter code_debugger code_patcher shared tests
pylint code_starter code_debugger code_patcher shared

# Type checking
mypy shared code_starter

# Tests with coverage
pytest tests/ --cov=code_starter --cov=code_debugger --cov=code_patcher --cov=shared
```

### 5. Write Commit Messages

Follow conventional commits format:

```
type(scope): subject

body (optional)

footer (optional)
```

Examples:
- `feat(code_starter): add new template support`
- `fix(llm): handle connection timeout`
- `docs(readme): update installation steps`
- `test(code_debugger): add unit tests for analyzer`
- `refactor(shared): improve config loading`

Types: `feat`, `fix`, `docs`, `test`, `refactor`, `perf`, `chore`, `ci`

### 6. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub with:
- Clear description of changes
- Reference to related issues (e.g., "Closes #123")
- Before/after for UI changes
- Any breaking changes clearly marked

## Code Style Guidelines

### Python Style

- Follow PEP 8 (enforced by black and flake8)
- Line length: 88 characters
- Use double quotes for strings (per black default)
- Sort imports alphabetically

### Docstrings

Use Google-style docstrings:

```python
def my_function(param1: str, param2: int) -> dict:
    """Short description of function.
    
    Longer description if needed, explaining the function's purpose,
    behavior, and any important details.
    
    Args:
        param1: Description of param1
        param2: Description of param2
    
    Returns:
        Description of return value
    
    Raises:
        ValueError: When something is invalid
        FileNotFoundError: When file not found
    
    Examples:
        >>> result = my_function("test", 42)
        >>> result["key"]
        "value"
    """
    pass
```

### Type Hints

Always add type hints to function signatures:

```python
from typing import Dict, List, Optional

def process_data(
    items: List[str],
    config: Optional[Dict[str, any]] = None
) -> Dict[str, int]:
    """Process data with optional configuration."""
    pass
```

## Testing Requirements

### Unit Tests

- Test individual functions/methods
- Use pytest fixtures for setup
- Mock external dependencies (LLM, files, etc.)
- Test both happy path and error cases

```python
@pytest.fixture
def sample_spec():
    return {
        "name": "test_project",
        "modules": ["test"]
    }

def test_with_fixture(sample_spec):
    # Use fixture
    assert sample_spec["name"] == "test_project"
```

### Integration Tests

- Test complete workflows
- Use real files/directories (in temp directories)
- Test interaction between modules
- Clean up after tests

```python
def test_full_project_creation(tmp_path):
    creator = StarterFileCreator(output_dir=str(tmp_path))
    spec = creator.create_project_spec(...)
    creator.save_spec(spec, str(tmp_path / "test.pseudo"))
    
    # Verify file was created
    assert (tmp_path / "test.pseudo").exists()
```

### Coverage Requirements

- Aim for >80% code coverage
- 100% coverage for critical paths
- Run `make test-cov` to generate coverage report

## Documentation

### Update Documentation When:

- Adding new features - document in API.md and module README
- Changing existing behavior - update relevant documentation
- Adding new modules - create docs/MODULE_NAME/ directory

### Documentation Format:

- Use Markdown for all documentation
- Include code examples
- Keep explanations clear and concise
- Link to related documentation

## Reporting Issues

### Found a Bug?

1. Check existing issues - don't create duplicates
2. Create detailed bug report with:
   - Clear title
   - Steps to reproduce
   - Expected vs actual behavior
   - Python version and OS
   - Error traceback (if applicable)

### Feature Request?

1. Check existing issues
2. Create feature request with:
   - Clear description
   - Use case and motivation
   - Proposed API (if applicable)
   - Any alternatives considered

## Review Process

### What to Expect

- Code review within 1-2 weeks (volunteer-driven)
- Feedback on code style, tests, documentation
- Requests for changes are not criticism
- Approval is needed before merge

### Making Changes Based on Review

```bash
# Make requested changes
git add .
git commit -m "Address review feedback"
git push origin feature/your-feature-name
```

No need to force-push; we'll squash on merge if needed.

## Merging

Once approved:
- Maintainers will merge to main
- PR will be squashed into single commit
- Commit message will be conventional commit format

## Release Process

Releases follow semantic versioning:
- MAJOR: Breaking changes
- MINOR: New features (backward compatible)
- PATCH: Bug fixes

Maintainers handle:
- Version bumps in setup.py, __init__.py
- CHANGELOG.md updates
- Git tags and releases

## Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Credited in commit messages and release notes
- Thanked in README

## Need Help?

- Ask questions in GitHub issues (use "question" label)
- Check existing documentation
- Contact: olga.moreira@gmail.com

## Additional Resources

- [Python PEP 8 Style Guide](https://www.python.org/dev/peps/pep-0008/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- [pytest Documentation](https://docs.pytest.org/)
- [Conventional Commits](https://www.conventionalcommits.org/)

---

Thank you for contributing to Code Assistant! 🎉
