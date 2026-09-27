"""Unit tests for code_starter module."""

import pytest
from pathlib import Path
from code_starter.starterfile_creator import StarterFileCreator


@pytest.mark.unit
class TestStarterFileCreator:
    """Tests for StarterFileCreator class."""
    
    def test_init(self, temp_dir):
        """Test StarterFileCreator initialization."""
        creator = StarterFileCreator(output_dir=str(temp_dir))
        assert creator is not None
        assert Path(creator.output_dir).exists()
    
    def test_create_project_spec(self, temp_dir):
        """Test project specification creation."""
        creator = StarterFileCreator(output_dir=str(temp_dir))
        
        spec = creator.create_project_spec(
            name="test_project",
            description="Test project",
            modules=["test_module"],
            dependencies=["pytest"]
        )
        
        assert spec["name"] == "test_project"
        assert spec["description"] == "Test project"
        assert "test_module" in spec["modules"]
        assert "pytest" in spec["dependencies"]
    
    def test_save_spec(self, temp_dir, sample_spec):
        """Test specification saving."""
        creator = StarterFileCreator(output_dir=str(temp_dir))
        
        output_file = str(temp_dir / "test.pseudo")
        result = creator.save_spec(sample_spec, output_file)
        
        assert Path(result).exists()
        assert Path(result).suffix == ".pseudo"
    
    @pytest.mark.skip(reason="Requires user interaction")
    def test_run_interactive(self, monkeypatch):
        """Test interactive mode (skipped for automation)."""
        # This would require mocking user input
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
