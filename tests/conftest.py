"""Pytest configuration and fixtures.

Provides common fixtures for all tests.
"""

import pytest
import tempfile
from pathlib import Path
from typing import Generator


@pytest.fixture
def project_root() -> Path:
    """Return project root path."""
    return Path(__file__).parent.parent


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create temporary directory for test files.
    
    Yields:
        Temporary directory path
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_spec() -> dict:
    """Create sample project specification."""
    return {
        "name": "test_project",
        "description": "Test project for unit tests",
        "modules": ["core", "utils", "tests"],
        "dependencies": ["pytest", "numpy"],
    }


@pytest.fixture
def sample_code() -> str:
    """Create sample Python code."""
    return '''def hello_world():
    """Print hello world."""
    print("Hello, World!")


def add(a, b):
    """Add two numbers."""
    return a + b


class Calculator:
    """Simple calculator class."""
    
    def __init__(self):
        self.result = 0
    
    def add(self, a, b):
        """Add two numbers."""
        self.result = a + b
        return self.result
    
    def multiply(self, a, b):
        """Multiply two numbers."""
        self.result = a * b
        return self.result
'''


@pytest.fixture
def sample_pseudocode() -> str:
    """Create sample pseudocode."""
    return """
module: calculator

function: add(a, b)
  description: Add two numbers
  param: a - first number
  param: b - second number
  return: sum of a and b
  
  result = a + b
  return result

class: Calculator
  attributes:
    - value: int (default 0)
  
  method: __init__()
    set self.value = 0
  
  method: add(num)
    add num to self.value
    return self.value
  
  method: multiply(num)
    multiply self.value by num
    return self.value
"""


@pytest.fixture
def sample_config() -> dict:
    """Create sample configuration."""
    return {
        "project": {
            "name": "test_project",
            "version": "0.1.0",
        },
        "llm": {
            "model": "deepseek-coder:6.7b",
            "api_endpoint": "http://localhost:11434",
        },
        "paths": {
            "output_dir": "./test_output",
            "config_dir": "./config",
        },
    }
