"""LLM / Ollama access for the UI.

Builds :class:`shared.llm.LLMInterface` instances from the repository's own
provider configuration (:mod:`shared.llm_config`) and provides the hard Ollama
availability gate used at app start-up.
"""

from __future__ import annotations

from typing import Tuple

import streamlit as st

from shared.llm import LLMInterface
from shared.llm_config import resolve_llm


def get_llm(role: str = "generation") -> LLMInterface:
    """Return an ``LLMInterface`` for ``role`` using repo configuration."""
    return LLMInterface(resolved=resolve_llm(role))


def _probe(endpoint: str) -> bool:
    try:
        return LLMInterface(api_endpoint=endpoint).is_available()
    except Exception:  # noqa: BLE001 - a failed probe simply means "down"
        return False


@st.cache_data(ttl=15, show_spinner=False)
def _cached_probe(endpoint: str) -> bool:
    return _probe(endpoint)


def ollama_status() -> Tuple[bool, str]:
    """Return ``(available, endpoint)`` for the configured analysis provider."""
    resolved = resolve_llm("analysis")
    return _cached_probe(resolved.base_url), resolved.base_url


def require_ollama() -> None:
    """Hard-block the app when the LLM endpoint is unreachable (user choice)."""
    available, endpoint = ollama_status()
    if not available:
        st.error(
            "Ollama is not reachable at `{}`.\n\n"
            "Start it (for example `ollama serve`) and reload this page. "
            "The Converter, Editor-convert and Patcher pages, and the Starter "
            "pipeline run, all require a local model.".format(endpoint)
        )
        st.stop()
