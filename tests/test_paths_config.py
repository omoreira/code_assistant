"""Offline tests for shared.paths_config data-dir resolution precedence."""

from pathlib import Path

from shared.constants import DEFAULT_DATA_DIR
from shared.paths_config import (
    data_dir_is_explicit,
    data_dir_source,
    resolve_data_dir,
)

REPO_CONFIG = Path(__file__).resolve().parents[1] / "config" / "defaults.yaml"


def _write_config(tmp_path: Path, data_dir: str) -> str:
    config = tmp_path / "defaults.yaml"
    config.write_text('paths:\n  data_dir: "{0}"\n'.format(data_dir), encoding="utf-8")
    return str(config)


def test_builtin_fallback_when_nothing_set(tmp_path):
    missing = str(tmp_path / "missing.yaml")
    assert resolve_data_dir(config_file=missing, env={}) == DEFAULT_DATA_DIR


def test_config_file_beats_builtin(tmp_path):
    cfg = _write_config(tmp_path, "from_config")
    assert resolve_data_dir(config_file=cfg, env={}) == "from_config"


def test_env_beats_config(tmp_path):
    cfg = _write_config(tmp_path, "from_config")
    assert resolve_data_dir(config_file=cfg, env={"DATA_DIR": "from_env"}) == "from_env"


def test_specific_env_var_beats_generic(tmp_path):
    cfg = _write_config(tmp_path, "from_config")
    env = {"CODE_ASSISTANT_DATA_DIR": "specific", "DATA_DIR": "generic"}
    assert resolve_data_dir(config_file=cfg, env=env) == "specific"


def test_override_beats_everything(tmp_path):
    cfg = _write_config(tmp_path, "from_config")
    env = {"CODE_ASSISTANT_DATA_DIR": "from_env"}
    assert resolve_data_dir("explicit", config_file=cfg, env=env) == "explicit"


def test_empty_override_falls_through(tmp_path):
    cfg = _write_config(tmp_path, "from_config")
    assert resolve_data_dir("", config_file=cfg, env={}) == "from_config"


def test_repo_default_config_resolves_to_data():
    assert resolve_data_dir(config_file=str(REPO_CONFIG), env={}) == "data"


def test_project_value_beats_config_but_loses_to_env(tmp_path):
    cfg = _write_config(tmp_path, "from_config")
    assert (
        resolve_data_dir(project_value="from_starterfile", config_file=cfg, env={})
        == "from_starterfile"
    )
    assert (
        resolve_data_dir(
            project_value="from_starterfile",
            config_file=cfg,
            env={"DATA_DIR": "from_env"},
        )
        == "from_env"
    )


def test_data_dir_source_labels(tmp_path):
    cfg = _write_config(tmp_path, "from_config")
    missing = str(tmp_path / "missing.yaml")
    assert data_dir_source(config_file=cfg, env={}) == "config"
    assert data_dir_source(project_value="p", config_file=cfg, env={}) == "starterfile"
    assert data_dir_source(config_file=cfg, env={"DATA_DIR": "e"}) == "env"
    assert (
        data_dir_source(
            override="o", project_value="p", config_file=cfg, env={"DATA_DIR": "e"}
        )
        == "override"
    )
    assert data_dir_source(config_file=missing, env={}) == "builtin"


def test_explicit_sources_only():
    for source in ("override", "env", "starterfile"):
        assert data_dir_is_explicit(source) is True
    for source in ("config", "builtin"):
        assert data_dir_is_explicit(source) is False
