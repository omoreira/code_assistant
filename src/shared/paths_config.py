"""Resolver for the SQLite data-storage directory.

Mirrors :mod:`shared.llm_config` so the data directory is chosen the same way
LLM settings are: a single source of truth with an explicit precedence.

Precedence (lowest to highest)::

    config/defaults.yaml (paths.data_dir)   <
        environment variables (CODE_ASSISTANT_DATA_DIR, DATA_DIR)   <
            explicit overrides (e.g. the --data-dir CLI flag)

The built-in fallback is :data:`shared.constants.DEFAULT_DATA_DIR`; it is used
only when config, environment, and overrides are all silent. This module
depends only on the standard library plus PyYAML and performs no network calls.
"""

from __future__ import annotations

import os
from typing import Mapping, Optional

from .constants import DEFAULT_DATA_DIR
from .llm_config import _cfg_get, _env_value, _first_set, load_raw_config

#: Environment variables that may carry a data-dir override (first set wins).
ENV_VARS = ("CODE_ASSISTANT_DATA_DIR", "DATA_DIR")


def resolve_data_dir(
    override: Optional[str] = None,
    config_file: str = "config/defaults.yaml",
    env: Optional[Mapping[str, str]] = None,
) -> str:
    """Resolve the SQLite data directory for a target project.

    Args:
        override: Highest-precedence value (e.g. from ``--data-dir``). Ignored
            when ``None`` or empty.
        config_file: Path to the YAML config (relative to CWD by default).
        env: Environment mapping to read from (defaults to ``os.environ``).

    Returns:
        The resolved data-directory string (never empty).
    """
    env = os.environ if env is None else env
    config = load_raw_config(config_file)
    resolved = _first_set(
        override,
        _env_value(env, *ENV_VARS),
        _cfg_get(config, "paths", "data_dir"),
        DEFAULT_DATA_DIR,
    )
    return str(resolved)


if __name__ == "__main__":  # pragma: no cover - manual/tooling entry point
    print(resolve_data_dir())
