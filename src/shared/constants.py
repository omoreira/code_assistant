"""Project constants.

Defines constants used throughout the code-assistant project.
"""

# Project Information
PROJECT_NAME = "code-assistant"
PROJECT_VERSION = "0.1.0"
PROJECT_AUTHOR = "Olga Moreira"
PROJECT_EMAIL = "olga.moreira@gmail.com"
PROJECT_REPOSITORY = "https://github.com/omoreira/code_assistant"
PROJECT_LICENSE = "MIT"

# Modules
MODULES = [
    "code_starter",
    "code_debugger",
    "code_patcher"
]

SHARED_PATHS = [
    "config",
    "shared",
    "docs",
    "tests"
]

# LLM Configuration
DEFAULT_LLM_PROVIDER = "ollama"
DEFAULT_LLM_MODEL = "deepseek-coder:6.7b"
DEFAULT_LLM_ENDPOINT = "http://localhost:11434"
DEFAULT_LLM_TIMEOUT = 300
DEFAULT_LLM_TEMPERATURE = 0.7
DEFAULT_LLM_MAX_TOKENS = 2048

# Supported Languages
SUPPORTED_LANGUAGES = [
    "python",
    "javascript",
    "typescript",
    "java",
    "cpp",
    "c",
    "csharp",
    "go",
    "rust",
    "php",
]

# Supported LLM Providers
SUPPORTED_LLM_PROVIDERS = [
    "ollama",
    "openai",
    "claude",
    "huggingface",
]

# File Patterns
FILE_PATTERNS = {
    "python": "*.py",
    "javascript": "*.js",
    "typescript": "*.ts",
    "java": "*.java",
    "cpp": "*.cpp",
    "config": "*.yaml",
    "markdown": "*.md",
    "pseudocode": "*.pseudo",
    "json": "*.json",
}

# Default Paths
DEFAULT_OUTPUT_DIR = "./generated_projects"
DEFAULT_CONFIG_DIR = "./config"
DEFAULT_DOCS_DIR = "./docs"
DEFAULT_TESTS_DIR = "./tests"

# Logging Configuration
DEFAULT_LOG_LEVEL = "INFO"
DEFAULT_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DEFAULT_LOG_FILE = "code_assistant.log"

# Code Generation Settings
DEFAULT_INDENT = 4
DEFAULT_LINE_LENGTH = 88
DEFAULT_CODE_STYLE = "black"

# Testing
DEFAULT_TEST_FRAMEWORK = "pytest"
DEFAULT_TEST_TIMEOUT = 300

# Error Messages
ERROR_MESSAGES = {
    "llm_unavailable": "LLM API not available. Ensure ollama is running.",
    "config_not_found": "Configuration file not found.",
    "file_not_found": "File not found: {filepath}",
    "invalid_input": "Invalid input provided.",
    "invalid_config": "Invalid configuration.",
}

# Success Messages
SUCCESS_MESSAGES = {
    "project_created": "Project created successfully.",
    "files_generated": "Files generated successfully.",
    "config_loaded": "Configuration loaded successfully.",
    "tests_passed": "All tests passed.",
}

# Feature Flags
FEATURES = {
    "syntax_highlighting": True,
    "color_output": True,
    "interactive_mode": True,
    "progress_bars": True,
    "ai_code_generation": True,
    "automatic_testing": False,
    "continuous_integration": False,
}

# API Endpoints
API_ENDPOINTS = {
    "ollama_generate": "/api/generate",
    "ollama_tags": "/api/tags",
    "ollama_pull": "/api/pull",
}

# Timeouts (in seconds)
TIMEOUTS = {
    "default": 30,
    "long": 300,
    "short": 5,
    "llm": 300,
    "api": 30,
}

# Retry Configuration
RETRY_CONFIG = {
    "max_retries": 3,
    "backoff_factor": 1,
    "status_forcelist": [429, 500, 502, 503, 504],
}
