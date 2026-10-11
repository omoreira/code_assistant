"""Contract tests for shared.llm_config precedence and resolution."""

import textwrap

import pytest

from shared.llm_config import resolve_llm, resolve_ollama

CONFIG = textwrap.dedent(
    """
    llm:
      provider: "ollama"
      model: "global-model"
      models:
        analysis: "file-analysis"
        reasoning: "file-reasoning"
      api_endpoint: "http://file-endpoint:11434"
      providers:
        ollama:
          base_url: "http://file-endpoint:11434"
          api_key_env: ""
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


def test_defaults_from_file(config_file):
    assert resolve_llm("analysis", config_file=config_file).model == "file-analysis"
    assert resolve_llm("reasoning", config_file=config_file).model == "file-reasoning"
    # A role absent from the file falls back to the global file model.
    assert resolve_llm("generation", config_file=config_file).model == "global-model"
    assert resolve_llm("analysis", config_file=config_file).provider == "ollama"


def test_builtin_role_defaults_without_file(tmp_path):
    missing = str(tmp_path / "nope.yaml")
    assert resolve_llm("analysis", config_file=missing).model == "qwen3:14b"
    assert resolve_llm("reasoning", config_file=missing).model == "deepseek-r1:14b"
    assert resolve_llm("generation", config_file=missing).model == "deepseek-coder:6.7b"
    assert (
        resolve_llm("analysis", config_file=missing).base_url
        == "http://localhost:11434"
    )


def test_env_overrides_file(config_file):
    assert (
        resolve_llm(
            "analysis", config_file=config_file, env={"LLM_MODEL": "env-global"}
        ).model
        == "env-global"
    )
    assert (
        resolve_llm(
            "analysis",
            config_file=config_file,
            env={"LLM_MODEL": "env-global", "LLM_ANALYSIS_MODEL": "env-analysis"},
        ).model
        == "env-analysis"
    )


def test_overrides_beat_env(config_file):
    resolved = resolve_llm(
        "analysis",
        config_file=config_file,
        overrides={"model": "override"},
        env={"LLM_ANALYSIS_MODEL": "env"},
    )
    assert resolved.model == "override"


def test_provider_switch_uses_registry(config_file):
    resolved = resolve_llm(
        "reasoning",
        config_file=config_file,
        overrides={"provider": "openai", "model": "gpt-4o"},
        env={"OPENAI_API_KEY": "sk-secret"},
    )
    assert resolved.provider == "openai"
    assert resolved.base_url == "https://api.openai.com/v1"
    assert resolved.api_key == "sk-secret"
    assert resolved.api_key_env == "OPENAI_API_KEY"


def test_api_key_never_in_describe(config_file):
    resolved = resolve_llm(
        "reasoning",
        config_file=config_file,
        overrides={"provider": "openai"},
        env={"OPENAI_API_KEY": "sk-secret"},
    )
    assert "sk-secret" not in resolved.describe()


def test_resolve_ollama_pins_provider(config_file):
    resolved = resolve_ollama(
        "analysis", config_file=config_file, env={"LLM_PROVIDER": "openai"}
    )
    assert resolved.provider == "ollama"
    assert resolved.base_url == "http://file-endpoint:11434"
    assert resolved.model == "file-analysis"
