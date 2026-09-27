"""Unit tests for shared.utils module."""

import pytest
import json
from pathlib import Path
from shared import utils


@pytest.mark.unit
class TestUtilsModule:
    """Tests for utility functions."""
    
    def test_read_write_file(self, temp_dir):
        """Test reading and writing files."""
        test_file = temp_dir / "test.txt"
        content = "Test content"
        
        utils.write_file(test_file, content)
        read_content = utils.read_file(test_file)
        
        assert read_content == content
    
    def test_ensure_directory(self, temp_dir):
        """Test directory creation."""
        test_dir = temp_dir / "nested" / "dir" / "structure"
        result = utils.ensure_directory(test_dir)
        
        assert Path(result).exists()
        assert Path(result).is_dir()
    
    def test_read_json(self, temp_dir):
        """Test reading JSON files."""
        data = {"key": "value", "number": 42}
        json_file = temp_dir / "test.json"
        
        utils.write_json(json_file, data)
        read_data = utils.read_json(json_file)
        
        assert read_data == data
    
    def test_write_json(self, temp_dir):
        """Test writing JSON files."""
        data = {"test": "data"}
        json_file = temp_dir / "output.json"
        
        result = utils.write_json(json_file, data)
        
        assert Path(result).exists()
    
    def test_validate_input(self):
        """Test input validation."""
        data = {"name": "test", "value": 42}
        
        assert utils.validate_input(data, required_fields=["name", "value"])
        assert not utils.validate_input(data, required_fields=["missing"])
    
    def test_list_files(self, temp_dir):
        """Test listing files."""
        # Create test files
        (temp_dir / "test1.py").write_text("# Python file")
        (temp_dir / "test2.py").write_text("# Another Python file")
        (temp_dir / "test.txt").write_text("Text file")
        
        py_files = utils.list_files(temp_dir, "*.py")
        
        assert len(py_files) == 2
        assert all(f.endswith(".py") for f in py_files)
    
    def test_file_exists(self, temp_dir):
        """Test file existence check."""
        test_file = temp_dir / "test.txt"
        
        assert not utils.file_exists(test_file)
        
        utils.write_file(test_file, "content")
        assert utils.file_exists(test_file)
    
    def test_format_output(self, sample_code):
        """Test output formatting."""
        # Test text format (default)
        formatted = utils.format_output(sample_code, format_type="text")
        assert formatted == sample_code
        
        # Test JSON format
        json_str = '{"key": "value"}'
        formatted = utils.format_output(json_str, format_type="json")
        assert '"key"' in formatted


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
