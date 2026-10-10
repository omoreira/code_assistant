#local_analysis.py
import requests
import json

from shared.llm_config import resolve_ollama

_ANALYSIS = resolve_ollama("analysis")


def analyze_code(code: str, focus: str = "bugs"):
    payload = {
        "model": _ANALYSIS.model,
        "prompt": f"Analyze this code for {focus}:\n{code}",
        "stream": False
    }
    resp = requests.post(f"{_ANALYSIS.base_url}/api/generate", json=payload)
    return resp.json()["response"]
