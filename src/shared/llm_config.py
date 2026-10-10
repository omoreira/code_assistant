"""Central LLM provider/model configuration resolver.

Single source of truth for choosing an LLM provider and model, per role, so a
fork can plug in *any* local Ollama model or *any* API provider (OpenAI,
Anthropic, HuggingFace) without editing code.

Precedence (lowest to highest)::

    config/defaults.yaml   <   environment variables   <   explicit overrides

API keys are read from the environment **only**. They are never loaded from the
YAML file, never written to disk, and never included in ``describe()`` output.

This module depends only on the standard library plus PyYAML and performs no
network calls.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Mapping, Optional

from .constants import (
    CODE_ANALYSIS_MODEL,
    DEFAULT_LLM_ENDPOINT,
    DEFAULT_LLM_MAX_TOKENS,
    DEFAULT_LLM_MODEL,
    DEFAULT_LLM_PROVIDER,
    DEFAULT_LLM_TEMPERATURE,
    DEFAULT_LLM_TIMEOUT,
    REASONING_MODEL,
)

try:  # PyYAML is a declared runtime dependency, but degrade gracefully.
    import yaml
except ImportError:  # pragma: no cover
    yaml = None  # type: ignore

# --- provider constants ----------------------------------------------------

PROVIDER_OLLAMA = "ollama"
PROVIDER_OPENAI = "openai"
PROVIDER_ANTHROPIC = "anthropic"
PROVIDER_HUGGINGFACE = "huggingface"

SUPPORTED_PROVIDERS = (
    PROVIDER_OLLAMA,
    PROVIDER_OPENAI,
    PROVIDER_ANTHROPIC,
    PROVIDER_HUGGINGFACE,
)

# --- role constants --------------------------------------------------------

ROLE_DEFAULT = "default"
ROLE_ANALYSIS = "analysis"
ROLE_REASONING = "reasoning"
ROLE_GENERATION = "generation"
KNOWN_ROLES = (ROLE_DEFAULT, ROLE_ANALYSIS, ROLE_REASONING, ROLE_GENERATION)

# --- defaults --------------------------------------------------------------

DEFAULT_CONFIG_FILE = "config/defaults.yaml"

# Built-in fallbacks, used only when config, env, and overrides are all silent.
# The literal values live in :mod:`shared.constants` to keep a single source.
_DEFAULTS: Dict[str, Any] = {
    "provider": DEFAULT_LLM_PROVIDER,
    "model": DEFAULT_LLM_MODEL,
    "endpoint": DEFAULT_LLM_ENDPOINT,
    "timeout": DEFAULT_LLM_TIMEOUT,
    "temperature": DEFAULT_LLM_TEMPERATURE,
    "max_tokens": DEFAULT_LLM_MAX_TOKENS,
}

# Per-role built-in models, applied when neither config nor env name one.
_DEFAULT_ROLE_MODELS: Dict[str, str] = {
    ROLE_DEFAULT: DEFAULT_LLM_MODEL,
    ROLE_ANALYSIS: CODE_ANALYSIS_MODEL,
    ROLE_REASONING: REASONING_MODEL,
    ROLE_GENERATION: DEFAULT_LLM_MODEL,
}

# Canonical base URLs per provider (used when config/env do not specify one).
_PROVIDER_BASE_URLS: Dict[str, str] = {
    PROVIDER_OLLAMA: "http://localhost:11434",
    PROVIDER_OPENAI: "https://api.openai.com/v1",
    PROVIDER_ANTHROPIC: "https://api.anthropic.com",
    PROVIDER_HUGGINGFACE: "https://api-inference.huggingface.co",
}

# Environment variables that may hold a provider's API key (first set wins).
_PROVIDER_API_KEY_ENVS: Dict[str, tuple] = {
    PROVIDER_OLLAMA: ("OLLAMA_API_KEY",),
    PROVIDER_OPENAI: ("OPENAI_API_KEY",),
    PROVIDER_ANTHROPIC: ("ANTHROPIC_API_KEY",),
    PROVIDER_HUGGINGFACE: ("HUGGINGFACE_API_KEY", "HF_TOKEN"),
}

_GENERIC_API_KEY_ENV = "LLM_API_KEY"


# --- small helpers ---------------------------------------------------------


def _first_set(*values: Any) -> Any:
    """Return the first value that is neither ``None`` nor an empty string."""
    for value in values:
        if value is not None and value != "":
            return value
    return None


def _env_value(env: Mapping[str, str], *names: str) -> Optional[str]:
    """Return the first non-empty environment value among ``names``."""
    for name in names:
        if not name:
            continue
        value = env.get(name)
        if value:
            return value
    return None


def _coerce_int(value: Any) -> Optional[int]:
    if value is None or value == "":
        return None
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


def _coerce_float(value: Any) -> Optional[float]:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _cfg_get(config: Mapping[str, Any], *keys: str, default: Any = None) -> Any:
    """Read a nested key, returning ``default`` if any level is missing."""
    node: Any = config
    for key in keys:
        if isinstance(node, Mapping) and key in node:
            node = node[key]
        else:
            return default
    return node


def load_raw_config(config_file: str = DEFAULT_CONFIG_FILE) -> Dict[str, Any]:
    """Load the YAML config file; return ``{}`` if missing or unreadable."""
    path = Path(config_file)
    if yaml is None or not path.is_file():
        return {}
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, Exception):  # noqa: BLE001 - never fail on bad config
        return {}
    return data if isinstance(data, dict) else {}


# --- public result type ----------------------------------------------------


@dataclass(frozen=True)
class ResolvedLLM:
    """A fully resolved provider + model selection for one role."""

    role: str
    provider: str
    kind: str
    model: str
    base_url: str
    api_key: str = ""
    api_key_env: str = ""
    timeout: int = 600
    temperature: float = 0.7
    max_tokens: int = 2048

    def describe(self) -> str:
        """One-line summary that never exposes the API key value."""
        key_state = "set" if self.api_key else "unset"
        return (
            f"role={self.role} provider={self.provider} kind={self.kind} "
            f"model={self.model} base_url={self.base_url} "
            f"api_key_env={self.api_key_env or '-'} ({key_state}) "
            f"timeout={self.timeout} temperature={self.temperature} "
            f"max_tokens={self.max_tokens}"
        )


# --- resolver --------------------------------------------------------------


def resolve_llm(
    role: str = ROLE_DEFAULT,
    overrides: Optional[Mapping[str, Any]] = None,
    config_file: str = DEFAULT_CONFIG_FILE,
    env: Optional[Mapping[str, str]] = None,
) -> ResolvedLLM:
    """Resolve the LLM selection for ``role``.

    Args:
        role: One of :data:`KNOWN_ROLES` (unknown roles are allowed and simply
            fall back to the global/default settings).
        overrides: Highest-precedence values; recognised keys are ``provider``,
            ``model``, ``base_url``, ``timeout``, ``temperature`` and
            ``max_tokens``.
        config_file: Path to the YAML config (relative to CWD by default).
        env: Environment mapping to read from (defaults to ``os.environ``).

    Returns:
        A :class:`ResolvedLLM`.
    """
    env = os.environ if env is None else env
    overrides = dict(overrides or {})

    config = load_raw_config(config_file)
    llm = _cfg_get(config, "llm", default={}) or {}
    providers_cfg = _cfg_get(llm, "providers", default={}) or {}
    roles_cfg = _cfg_get(llm, "roles", default={}) or {}
    role_cfg = roles_cfg.get(role, {}) or {}
    models_cfg = _cfg_get(llm, "models", default={}) or {}

    role_env = role.upper()

    # --- provider ----------------------------------------------------------
    provider = _first_set(
        overrides.get("provider"),
        _env_value(env, f"LLM_{role_env}_PROVIDER", "LLM_PROVIDER"),
        role_cfg.get("provider"),
        llm.get("provider"),
        _DEFAULTS["provider"],
    )
    provider = str(provider).strip().lower()

    provider_cfg = providers_cfg.get(provider, {}) or {}

    # --- model -------------------------------------------------------------
    model = _first_set(
        overrides.get("model"),
        _env_value(env, f"LLM_{role_env}_MODEL", "LLM_MODEL"),
        role_cfg.get("model"),
        models_cfg.get(role),
        llm.get("model"),
        _DEFAULT_ROLE_MODELS.get(role),
        _DEFAULTS["model"],
    )

    # --- base_url ----------------------------------------------------------
    # ``llm.api_endpoint`` is treated as the Ollama base URL (backward compat);
    # named API providers use their own ``providers.<provider>.base_url``.
    base_url = _first_set(
        overrides.get("base_url"),
        _env_value(env, "LLM_API_ENDPOINT"),
        provider_cfg.get("base_url"),
        llm.get("api_endpoint") if provider == PROVIDER_OLLAMA else None,
        _PROVIDER_BASE_URLS.get(provider),
        _DEFAULTS["endpoint"],
    )

    # --- numeric scalars ---------------------------------------------------
    timeout = _first_set(
        _coerce_int(overrides.get("timeout")),
        _coerce_int(_env_value(env, "LLM_TIMEOUT")),
        _coerce_int(llm.get("timeout")),
        _DEFAULTS["timeout"],
    )
    temperature = _first_set(
        _coerce_float(overrides.get("temperature")),
        _coerce_float(_env_value(env, "LLM_TEMPERATURE")),
        _coerce_float(llm.get("temperature")),
        _DEFAULTS["temperature"],
    )
    max_tokens = _first_set(
        _coerce_int(overrides.get("max_tokens")),
        _coerce_int(_env_value(env, "LLM_MAX_TOKENS")),
        _coerce_int(llm.get("max_tokens")),
        _DEFAULTS["max_tokens"],
    )

    # --- API key (environment ONLY) ---------------------------------------
    api_key_env = str(provider_cfg.get("api_key_env", "") or "")
    candidates = []
    if api_key_env:
        candidates.append(api_key_env)
    candidates.extend(_PROVIDER_API_KEY_ENVS.get(provider, ()))
    if _GENERIC_API_KEY_ENV not in candidates:
        candidates.append(_GENERIC_API_KEY_ENV)

    api_key = ""
    for name in candidates:
        if name and env.get(name):
            api_key = env[name]
            break

    primary_key_env = api_key_env or (_PROVIDER_API_KEY_ENVS.get(provider, ("",))[0])

    return ResolvedLLM(
        role=role,
        provider=provider,
        kind=provider,
        model=str(model),
        base_url=str(base_url),
        api_key=api_key,
        api_key_env=primary_key_env,
        timeout=int(timeout),
        temperature=float(temperature),
        max_tokens=int(max_tokens),
    )


def resolve_ollama(
    role: str = ROLE_DEFAULT,
    overrides: Optional[Mapping[str, Any]] = None,
    config_file: str = DEFAULT_CONFIG_FILE,
    env: Optional[Mapping[str, str]] = None,
) -> ResolvedLLM:
    """Resolve with the provider pinned to Ollama.

    Used by the Ollama-only bridges that speak the native ``/api/generate``
    protocol; they still honour the role's model and the Ollama base URL.
    """
    merged: Dict[str, Any] = {"provider": PROVIDER_OLLAMA}
    merged.update(overrides or {})
    return resolve_llm(role, overrides=merged, config_file=config_file, env=env)


def describe(resolved: ResolvedLLM) -> str:
    """Backward-friendly module-level wrapper for :meth:`ResolvedLLM.describe`."""
    return resolved.describe()


if __name__ == "__main__":  # pragma: no cover - manual/tooling entry point
    import argparse

    _parser = argparse.ArgumentParser(description="Resolve LLM settings.")
    _parser.add_argument("--config-file", default=DEFAULT_CONFIG_FILE)
    _parser.add_argument("--role", help="print a single role's value")
    _parser.add_argument("--field", help="field for --role (e.g. model, base_url)")
    _parser.add_argument(
        "--provider",
        choices=SUPPORTED_PROVIDERS,
        help="pin the provider (default: as resolved)",
    )
    _args = _parser.parse_args()
    if _args.role and _args.field:
        _overrides = {"provider": _args.provider} if _args.provider else None
        _resolved = resolve_llm(
            _args.role, overrides=_overrides, config_file=_args.config_file
        )
        print(getattr(_resolved, _args.field, ""))
    else:
        for _role in KNOWN_ROLES:
            print(describe(resolve_llm(_role, config_file=_args.config_file)))
