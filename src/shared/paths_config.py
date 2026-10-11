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

#: Provenance labels returned by :func:`data_dir_source`.
SOURCE_BUILTIN = "builtin"
SOURCE_CONFIG = "config"
SOURCE_STARTERFILE = "starterfile"
SOURCE_ENV = "env"
SOURCE_OVERRIDE = "override"

#: Sources that count as an *explicit* request. The implicit ``config`` and
#: ``builtin`` defaults never authorise creating a data directory; an explicit
#: starterfile ``# PATHS`` entry, an env var, or a CLI override does.
EXPLICIT_SOURCES = (SOURCE_STARTERFILE, SOURCE_ENV, SOURCE_OVERRIDE)


def _ordered_sources(override, project_value, config_file, env):
    env = os.environ if env is None else env
    config = load_raw_config(config_file)
    return (
        (SOURCE_OVERRIDE, override),
        (SOURCE_ENV, _env_value(env, *ENV_VARS)),
        (SOURCE_STARTERFILE, project_value),
        (SOURCE_CONFIG, _cfg_get(config, "paths", "data_dir")),
    )


def data_dir_source(
    override: Optional[str] = None,
    project_value: Optional[str] = None,
    config_file: str = "config/defaults.yaml",
    env: Optional[Mapping[str, str]] = None,
) -> str:
    """Return which precedence level supplied the data directory.

    Precedence (highest first): override > environment > starterfile
    ``# PATHS`` > ``config/defaults.yaml`` > built-in. Returns one of the
    ``SOURCE_*`` labels, or ``SOURCE_BUILTIN`` when nothing was set.
    """
    for label, value in _ordered_sources(override, project_value, config_file, env):
        if value not in (None, ""):
            return label
    return SOURCE_BUILTIN


def data_dir_is_explicit(source: str) -> bool:
    """True when ``source`` is an explicit request (and may create the dir)."""
    return source in EXPLICIT_SOURCES


def resolve_data_dir(
    override: Optional[str] = None,
    project_value: Optional[str] = None,
    config_file: str = "config/defaults.yaml",
    env: Optional[Mapping[str, str]] = None,
) -> str:
    """Resolve the SQLite data directory for a target project.

    Args:
        override: Highest-precedence value (e.g. from ``--data-dir``). Ignored
            when ``None`` or empty.
        project_value: Value declared in the starterfile's ``# PATHS`` section
            (below the environment, above ``config/defaults.yaml``).
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
        project_value,
        _cfg_get(config, "paths", "data_dir"),
        DEFAULT_DATA_DIR,
    )
    return str(resolved)


if __name__ == "__main__":  # pragma: no cover - manual/tooling entry point
    print(resolve_data_dir())
