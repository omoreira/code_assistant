#local_analysis.py
import requests
import json

def analyze_code(code: str, focus: str = "bugs"):
    payload = {
        "model": "qwen3:14b",
        "prompt": f"Analyze this code for {focus}:\n{code}",
        "stream": False
    }
    resp = requests.post("http://localhost:11434/api/generate", json=payload)
    return resp.json()["response"]
