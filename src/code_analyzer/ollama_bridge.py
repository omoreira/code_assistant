# ollama_bridge.py

import requests
import json
from typing import Optional

OLLAMA_BASE = "http://localhost:11434"
OLLAMA_TIMEOUT = 600

def call_local_model(
    model: str,
    prompt: str,
    temperature: float = 0.7,
    top_p: float = 0.9,
) -> str:
    """Send request to Ollama, return formatted response."""
    
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "temperature": temperature,
        "top_p": top_p,
    }
    
    try:
        response = requests.post(
            f"{OLLAMA_BASE}/api/generate",
            json=payload,
            timeout=OLLAMA_TIMEOUT
        )
        response.raise_for_status()
        result = response.json()
        return result.get("response", "").strip()
    except requests.exceptions.RequestException as e:
        return f"Error calling model {model}: {str(e)}"

def analyze_code(code: str) -> str:
    """Use Qwen for code analysis."""
    prompt = f"""Analyze this code for bugs, structure, and improvements:

{code}

Provide:
1. Purpose and functionality
2. Issues or edge cases
3. Improvement suggestions"""
    
    return call_local_model("qwen3:14b", prompt, temperature=0.3)

def debug_code(code: str, issue: str) -> str:
    """Use DeepSeek-R1 for debugging with reasoning."""
    prompt = f"""Debug this code. The issue is: {issue}

Code:
{code}

Trace the execution step-by-step to find the root cause and propose a fix."""
    
    return call_local_model("deepseek-r1:14b", prompt, temperature=0.5)

def generate_code(requirement: str, language: str = "python") -> str:
    """Use Claude via API (or fallback to Qwen locally)."""
    prompt = f"""Generate {language} code for:
{requirement}

Include error handling and be production-ready."""
    
    return call_local_model("qwen3:14b", prompt, temperature=0.7)
