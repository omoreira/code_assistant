"""LLM Interface module.

A thin facade over the provider adapters in :mod:`shared.providers`. It keeps
the historical Ollama defaults so existing callers are unaffected, while
allowing any provider to be selected via ``provider=`` or ``resolved=``.
"""

from typing import Any, Dict, List, Optional

from .llm_config import PROVIDER_OLLAMA, ResolvedLLM
from .providers import LLMResponseError, LLMTransportError, provider_for


class LLMInterface:
    """Facade over a provider adapter.

    Defaults preserve the historical Ollama behaviour. Pass ``resolved=`` (a
    :class:`shared.llm_config.ResolvedLLM`) to use any configured provider, or
    ``provider=`` with an explicit ``api_endpoint``.
    """

    def __init__(
        self,
        model: str = "deepseek-r1:14b",
        api_endpoint: str = "http://localhost:11434",
        timeout: int = 600,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        provider: Optional[str] = None,
        resolved: Optional[ResolvedLLM] = None,
    ):
        """Initialize the LLM interface.

        Args:
            model: Model name (default: deepseek-r1:14b) when ``resolved`` is
                not supplied.
            api_endpoint: Base URL (default: localhost Ollama).
            timeout: Request timeout in seconds.
            temperature: Default model temperature (0.0-1.0).
            max_tokens: Default maximum tokens in response.
            provider: Provider kind (ollama/openai/anthropic/huggingface);
                defaults to ``ollama``.
            resolved: A fully-resolved selection to use verbatim (highest
                priority; ignores the other arguments).
        """
        if resolved is None:
            kind = (provider or PROVIDER_OLLAMA).strip().lower()
            resolved = ResolvedLLM(
                role="default",
                provider=kind,
                kind=kind,
                model=model,
                base_url=api_endpoint.rstrip("/"),
                timeout=timeout,
                temperature=temperature,
                max_tokens=max_tokens,
            )
    
        self._resolved = resolved
        self._provider = provider_for(resolved)

        # Preserve the historical public attributes.
        self.model = resolved.model
        self.api_endpoint = resolved.base_url
        self.timeout = resolved.timeout
        self.temperature = resolved.temperature
        self.max_tokens = resolved.max_tokens

    def is_available(self) -> bool:
        """Return True if the underlying provider looks reachable."""
        return self._provider.is_available()

    def call(
        self,
        prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs: Any
    ) -> str:
        """Call the configured LLM with ``prompt``.

        Args:
            prompt: Prompt text.
            temperature: Override the default temperature.
            max_tokens: Override the default max tokens.
            **kwargs: Extra provider parameters.

        Returns:
            The model response text.

        Raises:
            ConnectionError: If the provider is unreachable or times out.
            ValueError: If the provider returns an invalid response.
        """
        try:
            return self._provider.generate(
                prompt,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs,
            )
        except LLMTransportError as e:
            raise ConnectionError(f"LLM API error: {e}") from e
        except LLMResponseError as e:
            raise ValueError(f"Invalid API response: {e}") from e
    
    def generate_code(
        self,
        description: str,
        language: str = "python",
        **kwargs: Any
    ) -> str:
        """Generate code from description.
        
        Args:
            description: Code description
            language: Target language (default: python)
            **kwargs: Additional parameters
        
        Returns:
            Generated code
        """
        prompt = f"""Generate {language} code for the following:

{description}

Provide only the code without explanations or markdown formatting."""
        
        return self.call(prompt, **kwargs)
    
    def analyze_code(
        self,
        code: str,
        analysis_type: str = "general",
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Analyze code with LLM.
        
        Args:
            code: Code to analyze
            analysis_type: Type of analysis (general, performance, security, etc.)
            **kwargs: Additional parameters
        
        Returns:
            Dictionary with analysis results
        """
        prompts = {
            "general": f"""Analyze this {len(code)} character code snippet and provide:
1. Code quality assessment
2. Potential issues or improvements
3. Complexity analysis

Code:
```
{code}
```""",
            "performance": f"""Analyze this code for performance issues:
```
{code}
```
Identify bottlenecks and suggest optimizations.""",
            "security": f"""Analyze this code for security vulnerabilities:
```
{code}
```
Identify any security issues and suggest fixes.""",
        }
        
        prompt = prompts.get(analysis_type, prompts["general"])
        response = self.call(prompt, **kwargs)
        
        return {
            "analysis_type": analysis_type,
            "code_length": len(code),
            "analysis": response
        }
    
    def fix_code(
        self,
        code: str,
        issue: str = "general",
        **kwargs: Any
    ) -> str:
        """Generate fixed version of code.
        
        Args:
            code: Code to fix
            issue: Type of issue to fix (style, bugs, security, etc.)
            **kwargs: Additional parameters
        
        Returns:
            Fixed code
        """
        prompt = f"""Fix the following {issue} issues in this code:

```python
{code}
```

Provide only the corrected code without explanations."""
        
        return self.call(prompt, **kwargs)
    
    def explain_code(
        self,
        code: str,
        **kwargs: Any
    ) -> str:
        """Generate explanation of code.
        
        Args:
            code: Code to explain
            **kwargs: Additional parameters
        
        Returns:
            Code explanation
        """
        prompt = f"""Explain what this code does in simple terms:

```python
{code}
```"""
        
        return self.call(prompt, **kwargs)
    
    def suggest_refactoring(
        self,
        code: str,
        **kwargs: Any
    ) -> str:
        """Suggest refactoring improvements.
        
        Args:
            code: Code to refactor
            **kwargs: Additional parameters
        
        Returns:
            Refactoring suggestions
        """
        prompt = f"""Suggest refactoring improvements for this code:

```python
{code}
```

Provide specific, actionable suggestions."""
        
        return self.call(prompt, **kwargs)


if __name__ == "__main__":
    # Example usage
    llm = LLMInterface()
    
    if llm.is_available():
        print("LLM API is available")
        
        # Generate code
        code = llm.generate_code("A function to calculate fibonacci number")
        print("Generated code:")
        print(code)
    else:
        print("LLM API is not available. Ensure ollama is running.")
