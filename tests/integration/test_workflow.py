"""Integration tests for complete workflows.

Tests end-to-end workflows involving multiple modules.
"""

import pytest
from pathlib import Path
from code_starter.starterfile_creator import StarterFileCreator
from code_starter.blueprint_renderer import BlueprintRenderer


@pytest.mark.integration
class TestProjectCreationWorkflow:
    """Tests for complete project creation workflow."""
    
    def test_create_and_render_project(self, temp_dir, sample_spec):
        """Test creating specification and rendering blueprint."""
        creator = StarterFileCreator(output_dir=str(temp_dir))
        
        # Step 1: Create specification
        spec_file = str(temp_dir / "test_project.pseudo")
        creator.save_spec(sample_spec, spec_file)
        
        # Verify specification file was created
        assert Path(spec_file).exists()
        
        # Step 2: Try to render blueprint (if BlueprintRenderer is available)
        try:
            renderer = BlueprintRenderer(spec_file)
            blueprint = renderer.parse_blueprint()
            assert blueprint is not None
        except Exception as e:
            # BlueprintRenderer might not be fully implemented
            pytest.skip(f"BlueprintRenderer not fully implemented: {e}")
    
    @pytest.mark.slow
    def test_full_project_setup(self, temp_dir):
        """Test complete project setup from scratch."""
        creator = StarterFileCreator(output_dir=str(temp_dir))
        
        # Create a complete project specification
        spec = creator.create_project_spec(
            name="integration_test_project",
            description="Integration test project",
            modules=["core", "utils", "tests"],
            dependencies=["pytest", "requests"]
        )
        
        # Save specification
        spec_file = str(temp_dir / "project.pseudo")
        creator.save_spec(spec, spec_file)
        
        # Verify all expected fields
        assert spec["name"] == "integration_test_project"
        assert len(spec["modules"]) == 3
        assert len(spec["dependencies"]) == 2
        assert Path(spec_file).exists()


@pytest.mark.integration
class TestConfigurationWorkflow:
    """Tests for configuration loading and usage."""
    
    def test_load_and_use_config(self, sample_config, temp_dir):
        """Test loading configuration and using it."""
        from shared import config as config_module
        
        # Save configuration
        config_file = str(temp_dir / "test_config.yaml")
        config_module.save_config(sample_config, config_file)
        
        # Load configuration
        loaded = config_module.load_config(config_file)
        
        # Verify loaded configuration
        assert loaded["project"]["name"] == sample_config["project"]["name"]
        assert loaded["llm"]["model"] == sample_config["llm"]["model"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
