# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2024-01-01

### Added
- Initial release of code-assistant
- **code_starter module**: Interactive project creation tool with starterfile.pseudo support
  - `starterfile_creator.py`: Interactive project specification builder
  - `blueprint_renderer.py`: Generate skeleton directory structure from specifications
  - `pseudocode_renderer.py`: Generate Python code from pseudocode syntax
  - `github_repo_planner.py`: Automate GitHub repository structure generation
- **code_debugger module**: Placeholder for debugging utilities (in development)
- **code_patcher module**: Placeholder for code patching utilities (in development)
- **shared utilities module**: Centralized utilities for all modules
  - Configuration management with YAML support
  - Logging utilities
  - LLM interface for ollama integration
  - General utility functions
- Comprehensive documentation in `docs/` directory
- Testing structure with unit and integration tests
- Configuration files (defaults.yaml, logging_config.yaml)
- GitHub repository structure with LICENSE, setup.py, requirements files

### Notes
- Uses local LLM (ollama with deepseek-coder:6.7b model)
- Python 3.8+ support
- MIT License

[0.1.0]: https://github.com/omoreira/code_assistant/releases/tag/v0.1.0
