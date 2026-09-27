"""Logging utilities module.

Provides logging setup and management for all modules.
"""

import logging
import logging.config
import yaml
from pathlib import Path
from typing import Optional


# Global logger cache
_loggers = {}


def setup_logging(config_file: str = "config/logging_config.yaml") -> None:
    """Setup logging configuration from YAML file.
    
    Args:
        config_file: Path to logging configuration YAML file
    
    Raises:
        FileNotFoundError: If config file not found
        yaml.YAMLError: If YAML parsing fails
    """
    config_path = Path(config_file)
    
    if not config_path.exists():
        # Fallback to basic configuration
        _setup_basic_logging()
        return
    
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
            
            if config:
                logging.config.dictConfig(config)
            else:
                _setup_basic_logging()
    except (yaml.YAMLError, Exception) as e:
        print(f"Failed to load logging config: {e}. Using basic logging.")
        _setup_basic_logging()


def get_logger(name: str) -> logging.Logger:
    """Get logger for a module.
    
    Args:
        name: Logger name (typically __name__)
    
    Returns:
        Configured Logger instance
    """
    if name not in _loggers:
        _loggers[name] = logging.getLogger(name)
    return _loggers[name]


def set_log_level(name: str, level: str) -> None:
    """Set log level for specific logger.
    
    Args:
        name: Logger name
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    logger = get_logger(name)
    log_level = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(log_level)


def add_file_handler(
    logger_name: str,
    file_path: str,
    level: str = "DEBUG",
    format_string: Optional[str] = None
) -> None:
    """Add file handler to logger.
    
    Args:
        logger_name: Logger name
        file_path: Path to log file
        level: Log level
        format_string: Log message format
    """
    logger = get_logger(logger_name)
    
    # Create file handler
    handler = logging.FileHandler(file_path)
    log_level = getattr(logging, level.upper(), logging.DEBUG)
    handler.setLevel(log_level)
    
    # Create formatter
    if format_string is None:
        format_string = (
            "%(asctime)s - %(name)s - %(levelname)s - "
            "[%(filename)s:%(lineno)d] - %(message)s"
        )
    formatter = logging.Formatter(format_string)
    handler.setFormatter(formatter)
    
    logger.addHandler(handler)


def add_console_handler(
    logger_name: str,
    level: str = "INFO",
    format_string: Optional[str] = None
) -> None:
    """Add console handler to logger.
    
    Args:
        logger_name: Logger name
        level: Log level
        format_string: Log message format
    """
    logger = get_logger(logger_name)
    
    # Create console handler
    handler = logging.StreamHandler()
    log_level = getattr(logging, level.upper(), logging.INFO)
    handler.setLevel(log_level)
    
    # Create formatter
    if format_string is None:
        format_string = "%(levelname)s - %(message)s"
    formatter = logging.Formatter(format_string)
    handler.setFormatter(formatter)
    
    logger.addHandler(handler)


def _setup_basic_logging() -> None:
    """Setup basic logging configuration as fallback."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )


if __name__ == "__main__":
    # Example usage
    setup_logging()
    logger = get_logger(__name__)
    logger.info("Logging initialized")
    logger.debug("Debug message")
    logger.warning("Warning message")
