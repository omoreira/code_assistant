"""Unit tests for shared.config module."""

import pytest
import yaml
from pathlib import Path
from shared import config


@pytest.mark.unit
class TestConfigModule:
    """Tests for configuration management."""
    
    def test_load_env_config(self, monkeypatch):
        """Test loading configuration from environment variables."""
        monkeypatch.setenv("LLM_MODEL", "test-model")
        monkeypatch.setenv("LOG_LEVEL", "DEBUG")
        
        env_config = config.load_env_config()
        
        assert "llm" in env_config
        assert env_config["llm"]["model"] == "test-model"
        assert "logging" in env_config
        assert env_config["logging"]["level"] == "DEBUG"
    
    def test_merge_configs(self):
        """Test configuration merging."""
        config1 = {"a": 1, "b": {"c": 2}}
        config2 = {"b": {"d": 3}, "e": 4}
        
        merged = config.merge_configs(config1, config2)
        
        assert merged["a"] == 1
        assert merged["b"]["c"] == 2
        assert merged["b"]["d"] == 3
        assert merged["e"] == 4
    
    def test_get_config(self, sample_config):
        """Test getting configuration values."""
        value = config.get_config("project.name", config=sample_config)
        assert value == "test_project"
        
        value = config.get_config("llm.model", config=sample_config)
        assert value == "deepseek-coder:6.7b"
        
        value = config.get_config("nonexistent", default="default", config=sample_config)
        assert value == "default"
    
    def test_save_config(self, temp_dir, sample_config):
        """Test saving configuration to file."""
        output_file = str(temp_dir / "test_config.yaml")
        result = config.save_config(sample_config, output_file)
        
        assert Path(result).exists()
        
        # Verify saved content
        with open(result) as f:
            saved = yaml.safe_load(f)
        
        assert saved["project"]["name"] == "test_project"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
