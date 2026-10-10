"""Code generation (hybrid strategy).

Routes complex requirements to Claude (via Continue) and simpler work to a
local Qwen 3 model, then validates and polishes the result.
"""

import ast
from typing import Dict, List, Optional

import requests

from code_analyzer.hybrid_code_analyzer import (
    OLLAMA_BASE,
    OLLAMA_TIMEOUT,
    QWEN_MODEL,
    AnalysisResult,
)


def generate_code(
    requirement: str,
    language: str = "python",
    context_code: Optional[str] = None,
    use_claude: bool = True,
) -> AnalysisResult:
    """
    Generate code using hybrid strategy:
    - Claude  (API) for production, architecture, edge cases
    - Qwen 3 (Local) for boilerplate, simple functions, rapid iteration
    
    Args:
        requirement: What code to generate
        language: python, javascript, typescript, etc.
        context_code: Existing code for context/consistency
        use_claude: Route to Claude (True) or local model (False)
    """
    result = AnalysisResult(
        success=True,
        tool="generate_code",
        info={
            "model_used": None,
            "generated_code": None,
            "explanation": None,
            "quality_score": None,
            "suggestions": [],
        }
    )
    
    # Determine routing
    is_complex = _estimate_complexity(requirement)
    needs_claude = use_claude and is_complex
    
    # Build context-aware prompt
    system_prompt = f"""You are a code generation expert specializing in {language}.
Generate production-ready code that:
- Follows language best practices and conventions
- Includes comprehensive error handling
- Has type hints/annotations (where applicable)
- Includes docstrings/JSDoc comments
- Is maintainable and testable
- Handles edge cases"""
    
    if context_code:
        system_prompt += f"\n\nMatch the style and patterns of this existing codebase:\n{context_code[:1000]}"
    
    user_prompt = f"""Requirement:
{requirement}

Language: {language}
Generate the code and provide a brief explanation of key design decisions."""
    
    if needs_claude:
        # Route to Claude via Ollama (requires Claude API integration via Continue)
        # For now, we call local model with instruction to pass to Claude
        result.info["model_used"] = "claude-3-5-sonnet (via Continue API)"
        
        # In practice, this would call your Continue API configuration
        # For demonstration, we show the prompt structure
        response = _call_claude_via_continue(user_prompt, system_prompt)
        if response:
            result.info["generated_code"] = response.get("code", "")
            result.info["explanation"] = response.get("explanation", "")
            result.info["quality_score"] = 0.95
        else:
            # Fallback to local
            result.info["model_used"] = f"{QWEN_MODEL} (fallback)"
            response = _generate_with_qwen(user_prompt, system_prompt, language)
            result.info["generated_code"] = response
            result.info["quality_score"] = 0.75
    else:
        # Route to Qwen for fast boilerplate/simple functions
        result.info["model_used"] = f"{QWEN_MODEL}"
        response = _generate_with_qwen(user_prompt, system_prompt, language)
        result.info["generated_code"] = response
        result.info["quality_score"] = 0.75
    
    # Post-processing: syntax check + suggestions
    if result.info["generated_code"]:
        code = result.info["generated_code"]
        
        # Extract code block if wrapped in markdown
        code = _extract_code_block(code, language)
        result.info["generated_code"] = code
        
        # Syntax check
        if language == "python":
            syntax_ok = _check_syntax(code, "python")
            if not syntax_ok:
                result.warnings.append("Generated code has syntax errors; review before use")
        
        # Quality suggestions
        result.info["suggestions"] = _suggest_improvements(code, language)
    
    result.success = bool(result.info["generated_code"])
    return result


def _estimate_complexity(requirement: str) -> bool:
    """Estimate if requirement needs Claude (complex) vs Qwen (simple)."""
    complex_keywords = [
        "architecture", "design pattern", "refactor", "optimize",
        "concurrent", "distributed", "transaction", "security",
        "integration", "microservice", "api", "framework",
        "algorithm", "data structure", "edge case"
    ]
    
    req_lower = requirement.lower()
    return any(kw in req_lower for kw in complex_keywords)


def _generate_with_qwen(
    user_prompt: str,
    system_prompt: str,
    language: str,
) -> str:
    """Generate code using Qwen 2.5 locally."""
    full_prompt = f"{system_prompt}\n\n{user_prompt}"
    
    try:
        response = requests.post(
            f"{OLLAMA_BASE}/api/generate",
            json={
                "model": QWEN_MODEL,
                "prompt": full_prompt,
                "stream": False,
                "temperature": 0.7,
                "top_p": 0.9,
            },
            timeout=OLLAMA_TIMEOUT
        )
        response.raise_for_status()
        return response.json().get("response", "").strip()
    except Exception as e:
        return f"[Error generating code: {str(e)}]"


def _call_claude_via_continue(
    user_prompt: str,
    system_prompt: str,
) -> Optional[Dict[str, str]]:
    """
    Call Claude via Continue's API integration.
    
    In your Continue config, you would have:
    ```yaml
    customCommands:
      - name: "bridge_generate"
        prompt: "Generate production code"
        description: "Uses Claude for architecture decisions"
    ```
    
    This is a placeholder; actual integration depends on your Continue setup.
    """
    # Placeholder: In real implementation, call your Continue API endpoint
    # For now, fallback to local model
    return None


def _extract_code_block(text: str, language: str) -> str:
    """Extract code from markdown code blocks if present."""
    import re
    
    # Try markdown code block first
    pattern = rf"```{language}\n(.*?)\n```"
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return match.group(1).strip()
    
    # Try generic code block
    match = re.search(r"```\n(.*?)\n```", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    
    # Return as-is if no block found
    return text


def _check_syntax(code: str, language: str) -> bool:
    """Quick syntax validation."""
    if language == "python":
        try:
            ast.parse(code)
            return True
        except SyntaxError:
            return False
    return True


def _suggest_improvements(code: str, language: str) -> List[str]:
    """Generate improvement suggestions."""
    suggestions = []
    
    if language == "python":
        # Check for missing docstring
        if not code.startswith('"""') and not code.startswith("'''"):
            if "def " in code or "class " in code:
                suggestions.append("Consider adding module-level docstring")
        
        # Check for error handling
        if "open(" in code and "try:" not in code:
            suggestions.append("Consider wrapping file operations in try/except")
        
        # Check for type hints
        if "def " in code and "->" not in code:
            suggestions.append("Consider adding type hints to function signatures")
    
    elif language in ["javascript", "typescript"]:
        # Check for async/await
        if "fetch(" in code and "async" not in code:
            suggestions.append("Consider using async/await for cleaner async code")
        
        # Check for error handling
        if "Promise" in code and ".catch" not in code:
            suggestions.append("Add .catch() or try/catch for Promise error handling")
    
    return suggestions[:3]  # Limit to top 3 suggestions
