"""Tests for shared.continue_config rendering."""

import textwrap

import pytest
import yaml

from shared.continue_config import collect_models, render_continue_config

CONFIG = textwrap.dedent(
    """
    llm:
      provider: "ollama"
      models:
        analysis: "qwen3:14b"
        reasoning: "deepseek-r1:14b"
        generation: "deepseek-coder:6.7b"
      api_endpoint: "http://localhost:11434"
      providers:
        ollama:
          base_url: "http://localhost:11434"
        openai:
          base_url: "https://api.openai.com/v1"
          api_key_env: "OPENAI_API_KEY"
    """
)


@pytest.fixture
def config_file(tmp_path):
    path = tmp_path / "defaults.yaml"
    path.write_text(CONFIG, encoding="utf-8")
    return str(path)


def test_renders_valid_v1_schema(config_file):
    text = render_continue_config(config_file=config_file)
    data = yaml.safe_load(text)
    assert data["schema"] == "v1"
    assert data["version"] == "1.0.0"
    assert len(data["models"]) == 3
    names = {m["model"] for m in data["models"]}
    assert names == {"qwen3:14b", "deepseek-r1:14b", "deepseek-coder:6.7b"}


def test_ollama_models_have_no_api_key(config_file):
    text = render_continue_config(config_file=config_file)
    assert 'provider: "ollama"' in text
    assert "apiKey" not in text


def test_api_key_referenced_by_name_not_value(config_file):
    env = {"LLM_PROVIDER": "openai", "OPENAI_API_KEY": "sk-SUPER-SECRET"}
    text = render_continue_config(config_file=config_file, env=env)
    assert 'provider: "openai"' in text
    assert "${{ secrets.OPENAI_API_KEY }}" in text
    assert "sk-SUPER-SECRET" not in text


def test_duplicate_models_are_deduped(tmp_path):
    cfg = textwrap.dedent(
        """
        llm:
          models:
            analysis: "same-model"
            reasoning: "same-model"
            generation: "same-model"
        """
    )
    path = tmp_path / "d.yaml"
    path.write_text(cfg, encoding="utf-8")
    text = render_continue_config(config_file=str(path))
    data = yaml.safe_load(text)
    assert len(data["models"]) == 1
    assert data["models"][0]["model"] == "same-model"
    # generation is first in DEFAULT_ROLES, so it keeps the broader role set
    assert set(data["models"][0]["roles"]) == {"chat", "edit", "apply"}


def test_collect_models_order_and_dedup(config_file):
    models = collect_models(config_file=config_file)
    assert [m.model for m in models] == [
        "deepseek-coder:6.7b",
        "qwen3:14b",
        "deepseek-r1:14b",
    ]
