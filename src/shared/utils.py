"""General utility functions.

Common utilities for all modules.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union


def read_file(filepath: Union[str, Path], encoding: str = "utf-8") -> str:
    """Read file content.
    
    Args:
        filepath: Path to file
        encoding: File encoding
    
    Returns:
        File content as string
    
    Raises:
        FileNotFoundError: If file doesn't exist
        IOError: If read operation fails
    """
    filepath = Path(filepath)
    
    if not filepath.exists():
        raise FileNotFoundError(f"File not found: {filepath}")
    
    try:
        with open(filepath, "r", encoding=encoding) as f:
            return f.read()
    except Exception as e:
        raise IOError(f"Failed to read {filepath}: {e}")


def write_file(
    filepath: Union[str, Path],
    content: str,
    encoding: str = "utf-8",
    create_dirs: bool = True
) -> str:
    """Write content to file.
    
    Args:
        filepath: Path to file
        content: Content to write
        encoding: File encoding
        create_dirs: Create parent directories if needed
    
    Returns:
        Path to written file (as string)
    """
    filepath = Path(filepath)
    
    if create_dirs:
        filepath.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        with open(filepath, "w", encoding=encoding) as f:
            f.write(content)
        return str(filepath)
    except Exception as e:
        raise IOError(f"Failed to write {filepath}: {e}")


def ensure_directory(dirpath: Union[str, Path]) -> str:
    """Ensure directory exists, create if needed.
    
    Args:
        dirpath: Path to directory
    
    Returns:
        Path to directory (as string)
    """
    dirpath = Path(dirpath)
    dirpath.mkdir(parents=True, exist_ok=True)
    return str(dirpath)


def read_json(filepath: Union[str, Path]) -> Dict[str, Any]:
    """Read JSON file.
    
    Args:
        filepath: Path to JSON file
    
    Returns:
        Parsed JSON content
    
    Raises:
        FileNotFoundError: If file doesn't exist
        json.JSONDecodeError: If JSON is invalid
    """
    content = read_file(filepath)
    try:
        return json.loads(content)
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(f"Invalid JSON in {filepath}: {e}", "", 0)


def write_json(
    filepath: Union[str, Path],
    data: Dict[str, Any],
    indent: int = 2,
    create_dirs: bool = True
) -> str:
    """Write JSON file.
    
    Args:
        filepath: Path to JSON file
        data: Data to write
        indent: JSON indentation
        create_dirs: Create parent directories if needed
    
    Returns:
        Path to written file (as string)
    """
    content = json.dumps(data, indent=indent)
    return write_file(filepath, content, create_dirs=create_dirs)


def validate_input(
    data: Any,
    schema: Optional[Dict[str, Any]] = None,
    required_fields: Optional[List[str]] = None
) -> bool:
    """Validate input data.
    
    Args:
        data: Data to validate
        schema: Optional validation schema
        required_fields: List of required field names
    
    Returns:
        True if valid, False otherwise
    """
    if required_fields and isinstance(data, dict):
        for field in required_fields:
            if field not in data or not data[field]:
                return False
    
    if schema and isinstance(data, dict):
        for key, value_type in schema.items():
            if key in data and not isinstance(data[key], value_type):
                return False
    
    return True


def format_output(
    content: str,
    format_type: str = "text",
    indent: int = 2
) -> str:
    """Format content for output.
    
    Args:
        content: Content to format
        format_type: Output format (text, json, markdown)
        indent: Indentation level
    
    Returns:
        Formatted content
    """
    if format_type == "json":
        try:
            data = json.loads(content)
            return json.dumps(data, indent=indent)
        except json.JSONDecodeError:
            return content
    
    elif format_type == "markdown":
        # Add markdown formatting
        lines = content.split("\n")
        formatted = []
        for line in lines:
            if line.strip().startswith("#"):
                formatted.append(f"\n{line}\n")
            else:
                formatted.append(line)
        return "\n".join(formatted)
    
    else:
        return content


def list_files(
    dirpath: Union[str, Path],
    pattern: str = "*",
    recursive: bool = False
) -> List[str]:
    """List files in directory matching pattern.
    
    Args:
        dirpath: Directory path
        pattern: File pattern (e.g., "*.py")
        recursive: Search recursively
    
    Returns:
        List of file paths
    """
    dirpath = Path(dirpath)
    
    if not dirpath.exists():
        return []
    
    if recursive:
        files = dirpath.glob(f"**/{pattern}")
    else:
        files = dirpath.glob(pattern)
    
    return [str(f) for f in files if f.is_file()]


def get_file_size(filepath: Union[str, Path]) -> int:
    """Get file size in bytes.
    
    Args:
        filepath: Path to file
    
    Returns:
        File size in bytes
    """
    filepath = Path(filepath)
    return filepath.stat().st_size if filepath.exists() else 0


def file_exists(filepath: Union[str, Path]) -> bool:
    """Check if file exists.
    
    Args:
        filepath: Path to file
    
    Returns:
        True if file exists, False otherwise
    """
    return Path(filepath).exists()


def directory_exists(dirpath: Union[str, Path]) -> bool:
    """Check if directory exists.
    
    Args:
        dirpath: Path to directory
    
    Returns:
        True if directory exists, False otherwise
    """
    return Path(dirpath).is_dir()


def clean_path(filepath: Union[str, Path]) -> str:
    """Clean and normalize file path.
    
    Args:
        filepath: Path to clean
    
    Returns:
        Normalized path
    """
    return str(Path(filepath).resolve())


def get_relative_path(
    filepath: Union[str, Path],
    start: Union[str, Path] = "."
) -> str:
    """Get relative path from start point.
    
    Args:
        filepath: File path
        start: Starting point (default: current directory)
    
    Returns:
        Relative path
    """
    filepath = Path(filepath)
    start = Path(start)
    
    try:
        return str(filepath.relative_to(start))
    except ValueError:
        # Path is not relative to start
        return str(filepath)


if __name__ == "__main__":
    # Example usage
    print("Testing utility functions...")
    
    # Test directory creation
    test_dir = ensure_directory("./test_output")
    print(f"Created directory: {test_dir}")
    
    # Test file writing
    test_file = write_file(f"{test_dir}/test.txt", "Hello, World!")
    print(f"Written file: {test_file}")
    
    # Test file reading
    content = read_file(test_file)
    print(f"Read content: {content}")
