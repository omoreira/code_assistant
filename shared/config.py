"""Configuration management module.

Handles loading and managing configuration from YAML files
and environment variables.
"""

import os
import yaml
from pathlib import Path
from typing import Any, Dict, Optional


def load_config(config_file: str = "config/defaults.yaml") -> Dict[str, Any]:
    """Load configuration from YAML file.
    
    Args:
        config_file: Path to YAML configuration file
    
    Returns:
        Dictionary containing configuration
    
    Raises:
        FileNotFoundError: If config file not found
        yaml.YAMLError: If YAML parsing fails
    """
    config_path = Path(config_file)
    
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_file}")
    
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
            if config is None:
                config = {}
            return config
    except yaml.YAMLError as e:
        raise yaml.YAMLError(f"Failed to parse {config_file}: {e}")


def load_env_config() -> Dict[str, Any]:
    """Load configuration from environment variables.
    
    Looks for environment variables starting with 'APP_' or module-specific
    prefixes like 'CODE_ASSISTANT_', 'LLM_', 'LOG_' etc.
    
    Returns:
        Dictionary containing environment variable settings
    """
    env_config = {}
    
    # Map environment variable names to config paths
    env_mappings = {
        "LLM_PROVIDER": "llm.provider",
        "LLM_MODEL": "llm.model",
        "LLM_API_ENDPOINT": "llm.api_endpoint",
        "LLM_TIMEOUT": "llm.timeout",
        "LLM_TEMPERATURE": "llm.temperature",
        "LLM_MAX_TOKENS": "llm.max_tokens",
        "LOG_LEVEL": "logging.level",
        "LOG_FILE": "logging.file",
        "OUTPUT_DIR": "paths.output_dir",
        "CONFIG_DIR": "paths.config_dir",
        "DEBUG": "development.debug",
        "VERBOSE": "development.verbose",
        "TEST_MODE": "development.test_mode",
    }
    
    for env_var, config_path in env_mappings.items():
        if env_var in os.environ:
            value = os.environ[env_var]
            # Convert string booleans
            if value.lower() in ("true", "false"):
                value = value.lower() == "true"
            # Convert string numbers
            elif value.isdigit():
                value = int(value)
            _set_nested_dict(env_config, config_path, value)
    
    return env_config


def merge_configs(*configs: Dict[str, Any]) -> Dict[str, Any]:
    """Merge multiple configuration dictionaries.
    
    Later configurations override earlier ones.
    
    Args:
        *configs: Variable number of configuration dictionaries
    
    Returns:
        Merged configuration dictionary
    """
    merged = {}
    
    for config in configs:
        if config:
            _deep_merge(merged, config)
    
    return merged


def get_config(
    key: str,
    default: Any = None,
    config: Optional[Dict[str, Any]] = None
) -> Any:
    """Get configuration value by key.
    
    Supports dot notation for nested keys (e.g., 'llm.model').
    
    Args:
        key: Configuration key (supports dot notation)
        default: Default value if key not found
        config: Configuration dictionary to search (uses default if None)
    
    Returns:
        Configuration value or default
    """
    if config is None:
        try:
            config = load_config()
        except FileNotFoundError:
            return default
    
    keys = key.split(".")
    value = config
    
    for k in keys:
        if isinstance(value, dict) and k in value:
            value = value[k]
        else:
            return default
    
    return value


def save_config(config: Dict[str, Any], output_file: str) -> str:
    """Save configuration to YAML file.
    
    Args:
        config: Configuration dictionary to save
        output_file: Path to output YAML file
    
    Returns:
        Path to saved file
    """
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False)
        return str(output_path)
    except Exception as e:
        raise IOError(f"Failed to save configuration: {e}")


def _set_nested_dict(d: Dict[str, Any], key_path: str, value: Any) -> None:
    """Set value in nested dictionary using dot notation.
    
    Args:
        d: Dictionary to modify
        key_path: Dot-separated key path
        value: Value to set
    """
    keys = key_path.split(".")
    current = d
    
    for key in keys[:-1]:
        if key not in current:
            current[key] = {}
        current = current[key]
    
    current[keys[-1]] = value


def _deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> None:
    """Deep merge override dictionary into base dictionary.
    
    Args:
        base: Base dictionary (modified in-place)
        override: Dictionary with values to override
    """
    for key, value in override.items():
        if key in base and isinstance(base[key], dict) and isinstance(value, dict):
            _deep_merge(base[key], value)
        else:
            base[key] = value


if __name__ == "__main__":
    # Example usage
    cfg = load_config()
    print("Loaded configuration:")
    print(yaml.dump(cfg, default_flow_style=False))
    
    print("\nProject name:", get_config("project.name", cfg))
    print("LLM model:", get_config("llm.model", cfg))
