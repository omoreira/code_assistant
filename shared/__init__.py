"""Shared utilities module for code-assistant.

Provides common functionality for all modules including:
- Configuration management
- Logging setup
- LLM interface
- General utilities
- Project constants
"""

from . import config, logging as app_logging, llm, utils, constants

__version__ = "0.1.0"
__author__ = "Olga Moreira"
__all__ = ["config", "app_logging", "llm", "utils", "constants"]
