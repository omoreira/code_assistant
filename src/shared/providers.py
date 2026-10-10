"""Concrete LLM provider adapters.

Each provider turns a :class:`shared.llm_config.ResolvedLLM` into a working
``generate()`` call. Providers are selected with :func:`provider_for`.

Design notes:
- ``OllamaProvider`` reproduces the historical ``LLMInterface`` request shape
  exactly (``POST {base}/api/generate`` with ``num_predict`` and a ``response``
  field), so existing behaviour is unchanged.
- API providers use plain ``requests`` (no SDK dependencies) so the runtime
  footprint stays at ``pyyaml`` + ``requests``.
- Credentials are only ever taken from ``ResolvedLLM.api_key`` (which the
  resolver reads from the environment); this module never reads files.

Errors raise :class:`LLMTransportError` (network/HTTP) or
:class:`LLMResponseError` (unexpected body); callers can map these to their own
exception types.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .llm_config import (
    PROVIDER_ANTHROPIC,
    PROVIDER_HUGGINGFACE,
    PROVIDER_OLLAMA,
    PROVIDER_OPENAI,
    ResolvedLLM,
)

__all__ = [
    "LLMProviderError",
    "LLMTransportError",
    "LLMResponseError",
    "LLMProvider",
    "OllamaProvider",
    "OpenAICompatibleProvider",
    "AnthropicProvider",
    "HuggingFaceProvider",
    "provider_for",
]


# --- errors ----------------------------------------------------------------


class LLMProviderError(RuntimeError):
    """Base class for provider failures."""


class LLMTransportError(LLMProviderError):
    """Network/HTTP failure (unreachable, timeout, non-2xx)."""


class LLMResponseError(LLMProviderError):
    """The provider answered but the body was empty or malformed."""


# --- base ------------------------------------------------------------------


def _make_session() -> requests.Session:
    session = requests.Session()
    retry = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


class LLMProvider(ABC):
    """Abstract provider bound to one resolved selection."""

    kind = "base"

    def __init__(self, resolved: ResolvedLLM):
        self.resolved = resolved
        self._session = _make_session()

    @property
    def model(self) -> str:
        return self.resolved.model

    @property
    def base_url(self) -> str:
        return self.resolved.base_url.rstrip("/")

    def _temperature(self, temperature: Optional[float]) -> float:
        return self.resolved.temperature if temperature is None else float(temperature)

    def _max_tokens(self, max_tokens: Optional[int]) -> int:
        return self.resolved.max_tokens if max_tokens is None else int(max_tokens)

    def _post_json(
        self,
        url: str,
        payload: Dict[str, Any],
        headers: Optional[Dict[str, str]] = None,
    ) -> Any:
        """POST ``payload`` as JSON and return the decoded body."""
        try:
            response = self._session.post(
                url,
                json=payload,
                headers=headers or {},
                timeout=self.resolved.timeout,
            )
            response.raise_for_status()
        except requests.Timeout as exc:
            raise LLMTransportError(f"{self.kind} request timed out: {exc}") from exc
        except requests.RequestException as exc:
            raise LLMTransportError(f"{self.kind} request failed: {exc}") from exc

        try:
            return response.json()
        except ValueError as exc:
            raise LLMResponseError(f"{self.kind} returned invalid JSON: {exc}") from exc

    def is_available(self) -> bool:
        """Best-effort reachability check. API providers return True."""
        return True

    @abstractmethod
    def generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs: Any,
    ) -> str:
        """Return the model's text response for ``prompt``."""
        raise NotImplementedError


# --- providers -------------------------------------------------------------


class OllamaProvider(LLMProvider):
    """Local Ollama server (``/api/generate``)."""

    kind = PROVIDER_OLLAMA

    def is_available(self) -> bool:
        try:
            response = self._session.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except requests.RequestException:
            return False

    def generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs: Any,
    ) -> str:
        payload: Dict[str, Any] = {
            "model": self.model,
            "prompt": prompt,
            "temperature": self._temperature(temperature),
            "num_predict": self._max_tokens(max_tokens),
            "stream": False,
        }
        if system:
            payload["system"] = system
        payload.update(kwargs)

        data = self._post_json(f"{self.base_url}/api/generate", payload)
        if not isinstance(data, dict) or "response" not in data:
            raise LLMResponseError("missing 'response' field")
        return str(data["response"]).strip()


class OpenAICompatibleProvider(LLMProvider):
    """Any OpenAI-style ``POST {base}/chat/completions`` endpoint.

    Covers OpenAI plus compatible vendors (Azure, OpenRouter, vLLM, LM Studio,
    Ollama's OpenAI shim, ...).
    """

    kind = PROVIDER_OPENAI

    def generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs: Any,
    ) -> str:
        headers = {"Content-Type": "application/json"}
        if self.resolved.api_key:
            headers["Authorization"] = f"Bearer {self.resolved.api_key}"

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": self._temperature(temperature),
            "max_tokens": self._max_tokens(max_tokens),
        }
        payload.update(kwargs)

        data = self._post_json(f"{self.base_url}/chat/completions", payload, headers)
        try:
            return str(data["choices"][0]["message"]["content"]).strip()
        except (KeyError, IndexError, TypeError) as exc:
            raise LLMResponseError("unexpected OpenAI-compatible response body") from exc


class AnthropicProvider(LLMProvider):
    """Anthropic Claude Messages API (``POST {base}/v1/messages``)."""

    kind = PROVIDER_ANTHROPIC

    def generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs: Any,
    ) -> str:
        headers = {
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01",
        }
        if self.resolved.api_key:
            headers["x-api-key"] = self.resolved.api_key

        payload: Dict[str, Any] = {
            "model": self.model,
            "max_tokens": self._max_tokens(max_tokens),
            "messages": [{"role": "user", "content": prompt}],
        }
        if system:
            payload["system"] = system
        if temperature is not None:
            payload["temperature"] = float(temperature)
        payload.update(kwargs)

        data = self._post_json(f"{self.base_url}/v1/messages", payload, headers)
        parts = data.get("content") if isinstance(data, dict) else None
        text = ""
        if isinstance(parts, list):
            text = "".join(
                str(part.get("text", ""))
                for part in parts
                if isinstance(part, dict)
            )
        text = text.strip()
        if not text:
            raise LLMResponseError("unexpected Anthropic response body")
        return text


class HuggingFaceProvider(LLMProvider):
    """HuggingFace Inference API (``POST {base}/models/{model}``)."""

    kind = PROVIDER_HUGGINGFACE

    def generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs: Any,
    ) -> str:
        headers = {"Content-Type": "application/json"}
        if self.resolved.api_key:
            headers["Authorization"] = f"Bearer {self.resolved.api_key}"

        full_prompt = prompt if not system else f"{system}\n\n{prompt}"
        payload: Dict[str, Any] = {
            "inputs": full_prompt,
            "parameters": {
                "max_new_tokens": self._max_tokens(max_tokens),
                "temperature": self._temperature(temperature),
                "return_full_text": False,
            },
        }
        payload.update(kwargs)

        data = self._post_json(f"{self.base_url}/models/{self.model}", payload, headers)

        if isinstance(data, list) and data:
            first = data[0]
            if isinstance(first, dict):
                return str(
                    first.get("generated_text") or first.get("summary_text") or ""
                ).strip()
            return str(first).strip()
        if isinstance(data, dict):
            text = data.get("generated_text") or data.get("error") or ""
            text = str(text).strip()
            if text:
                return text
        raise LLMResponseError("unexpected HuggingFace response body")


# --- factory ---------------------------------------------------------------

_PROVIDER_CLASSES = {
    PROVIDER_OLLAMA: OllamaProvider,
    PROVIDER_OPENAI: OpenAICompatibleProvider,
    PROVIDER_ANTHROPIC: AnthropicProvider,
    PROVIDER_HUGGINGFACE: HuggingFaceProvider,
}


def provider_for(resolved: ResolvedLLM) -> LLMProvider:
    """Return the provider adapter for ``resolved``.

    Raises:
        ValueError: If ``resolved.provider`` is not a known provider.
    """
    provider = (resolved.provider or "").strip().lower()
    cls = _PROVIDER_CLASSES.get(provider)
    if cls is None:
        raise ValueError(
            f"Unsupported provider: {resolved.provider!r}. "
            f"Known: {sorted(_PROVIDER_CLASSES)}"
        )
    return cls(resolved)
