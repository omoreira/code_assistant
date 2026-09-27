"""LLM Interface module.

Provides abstraction for local LLM (ollama) integration.
"""

import requests
import json
from typing import Any, Dict, List, Optional
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class LLMInterface:
    """Interface to local LLM via ollama API."""
    
    def __init__(
        self,
        model: str = "deepseek-coder:6.7b",
        api_endpoint: str = "http://localhost:11434",
        timeout: int = 300,
        temperature: float = 0.7,
        max_tokens: int = 2048
    ):
        """Initialize LLM interface.
        
        Args:
            model: Model name (default: deepseek-coder:6.7b)
            api_endpoint: API endpoint URL (default: localhost ollama)
            timeout: Request timeout in seconds
            temperature: Model temperature (0.0-1.0)
            max_tokens: Maximum tokens in response
        """
        self.model = model
        self.api_endpoint = api_endpoint.rstrip("/")
        self.timeout = timeout
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        # Setup session with retries
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
    
    def is_available(self) -> bool:
        """Check if LLM API is available.
        
        Returns:
            True if API is reachable, False otherwise
        """
        try:
            response = self.session.get(
                f"{self.api_endpoint}/api/tags",
                timeout=5
            )
            return response.status_code == 200
        except (requests.RequestException, Exception):
            return False
    
    def call(
        self,
        prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs: Any
    ) -> str:
        """Call LLM with prompt.
        
        Args:
            prompt: Prompt text
            temperature: Override default temperature
            max_tokens: Override default max_tokens
            **kwargs: Additional parameters
        
        Returns:
            LLM response text
        
        Raises:
            ConnectionError: If API unreachable
            ValueError: If response is invalid
        """
        if not self.is_available():
            raise ConnectionError(
                f"LLM API not available at {self.api_endpoint}. "
                "Ensure ollama is running."
            )
        
        url = f"{self.api_endpoint}/api/generate"
        
        # Use provided values or defaults
        temp = temperature if temperature is not None else self.temperature
        tokens = max_tokens if max_tokens is not None else self.max_tokens
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "temperature": temp,
            "num_predict": tokens,
            "stream": False,
            **kwargs
        }
        
        try:
            response = self.session.post(
                url,
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            data = response.json()
            if "response" not in data:
                raise ValueError("Invalid API response: missing 'response' field")
            
            return data["response"].strip()
            
        except requests.Timeout:
            raise ConnectionError("LLM API request timed out")
        except requests.RequestException as e:
            raise ConnectionError(f"LLM API error: {e}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON response from LLM API: {e}")
    
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
