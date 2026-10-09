#!/usr/bin/env python3

"""
Code analysis and debugging.
Combines fast static analysis tools with LLM reasoning for explanation.

Usage:
    python hybrid_analyzer.py analyze <file_or_code>
    python hybrid_analyzer.pydebug <file_or_code> "<issue_description>"
    python hybrid_analyzer.py generate "<requirement>" [language]
    python hybrid_analyzer.py check <file_or_code>
"""

import sys
import json
import ast
import subprocess
import argparse
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
import requests
from dataclasses import dataclass, asdict
import traceback


# Configuration


OLLAMA_BASE = "http://localhost:11434"
OLLAMA_TIMEOUT = 600
QWEN_MODEL = "qwen3:14b"
DEEPSEEK_MODEL = "deepseek-r1:14b"

@dataclass
class AnalysisResult:
    """Structured result from analysis."""
    success: bool
    tool: str
    duration_ms: Optional[int] = None
    errors: List[str] = None
    warnings: List[str] = None
    info: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []
        if self.info is None:
            self.info = {}


# Ollama Bridge (LLM Fallback)


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
    except requests.exceptions.Timeout:
        return f"[LLM Timeout] Model {model} took too long to respond"
    except requests.exceptions.RequestException as e:
        return f"[LLM Error] Could not reach {model}: {str(e)}"

# Static Analysis Tools (Fast, Deterministic)

def run_pylint(code: str) -> Tuple[List[Dict], bool]:
    """Run pylint on code, return structured issues."""
    try:
        result = subprocess.run(
            ["pylint", "--output-format=json", "--disable=all", 
             "--enable=E,W,R,C", "-"],
            input=code,
            capture_output=True,
            text=True,
            timeout=15
        )
        if result.stdout:
            issues = json.loads(result.stdout)
            return issues, len(issues) == 0
        return [], True
    except FileNotFoundError:
        return [{"message": "pylint not installed"}], False
    except Exception as e:
        return [{"message": f"pylint error: {str(e)}"}], False

def run_flake8(code: str) -> Tuple[List[Dict], bool]:
    """Run flake8 on code, return style/format issues."""
    try:
        result = subprocess.run(
            ["flake8", "--format=json", "-"],
            input=code,
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.stdout:
            issues = json.loads(result.stdout)
            return issues, len(issues) == 0
        return [], True
    except FileNotFoundError:
        return [], True  # Optional tool
    except Exception as e:
        return [{"message": f"flake8 error: {str(e)}"}], False

def run_bandit(code: str) -> Tuple[List[Dict], bool]:
    """Run bandit security scanner."""
    try:
        result = subprocess.run(
            ["bandit", "-f", "json", "-"],
            input=code,
            capture_output=True,
            text=True,
            timeout=15
        )
        if result.stdout:
            data = json.loads(result.stdout)
            return data.get("results", []), len(data.get("results", [])) == 0
        return [], True
    except FileNotFoundError:
        return [], True  # Optional tool
    except Exception as e:
        return [{"message": f"bandit error: {str(e)}"}], False

def get_code_complexity(code: str) -> Dict[str, Any]:
    """Use radon to get cyclomatic complexity."""
    try:
        result = subprocess.run(
            ["radon", "cc", "-j", "-"],
            input=code,
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.stdout:
            return json.loads(result.stdout)
        return {}
    except FileNotFoundError:
        return {}
    except Exception:
        return {}

def analyze_ast(code: str) -> Dict[str, Any]:
    """Parse and analyze AST structure."""
    try:
        tree = ast.parse(code)
        
        functions = []
        classes = []
        imports = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                functions.append({
                    "name": node.name,
                    "lineno": node.lineno,
                    "args": [arg.arg for arg in node.args.args],
                })
            elif isinstance(node, ast.ClassDef):
                classes.append({
                    "name": node.name,
                    "lineno": node.lineno,
                })
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                imports.append(f"from {node.module} import ...")
        
        return {
            "valid": True,
            "functions": functions,
            "classes": classes,
            "imports": list(set(imports)),
            "total_lines": len(code.split('\n')),
        }
    except SyntaxError as e:
        return {
            "valid": False,
            "syntax_error": {
                "line": e.lineno,
                "offset": e.offset,
                "message": e.msg,
                "text": e.text,
            }
        }
    except Exception as e:
        return {"valid": False, "error": str(e)}

def find_undefined_vars(code: str) -> Dict[str, List[str]]:
    """Detect potentially undefined variables."""
    try:
        tree = ast.parse(code)
        
        defined = set()
        used = set()
        undefined = []
        
        for node in ast.walk(tree):
            # Track definitions
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                defined.add(node.name)
            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        defined.add(target.id)
            elif isinstance(node, ast.For):
                if isinstance(node.target, ast.Name):
                    defined.add(node.target.id)
            elif isinstance(node, ast.With):
                if isinstance(node.items[0].optional_vars, ast.Name):
                    defined.add(node.items[0].optional_vars.id)
            
            # Track usage
            elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                used.add(node.id)
        
        # Built-ins that are always available
        builtins = {
            'len', 'range', 'str', 'int', 'float', 'list', 'dict', 'set',
            'print', 'input', 'open', 'type', 'isinstance', 'enumerate',
            'zip', 'map', 'filter', 'sorted', 'sum', 'min', 'max', 'abs',
            'any', 'all', 'reversed', 'round', 'pow', 'divmod', 'hex',
            'bin', 'oct', 'ord', 'chr', 'repr', 'format', 'hash', 'id',
            'callable', 'iter', 'next', 'object', 'super', 'property',
            'staticmethod', 'classmethod', 'Exception', 'BaseException',
            'True', 'False', 'None', 'self', 'cls', '__name__', '__main__',
            'NotImplemented', 'Ellipsis', '__doc__', '__file__',
        }
        
        undefined = list(used - defined - builtins)
        
        return {
            "potentially_undefined": sorted(undefined),
            "count": len(undefined),
        }
    except Exception as e:
        return {"error": str(e)}

# ============================================================================
# Code Analysis (Fast Path + LLM Explanation)
# ============================================================================

def analyze_code(code: str, use_llm: bool = True) -> AnalysisResult:
    """
    Comprehensive code analysis combining static tools + optional LLM.
    """
    result = AnalysisResult(
        success=True,
        tool="analyze_code",
        info={
            "static_issues": {},
            "complexity": {},
            "structure": {},
            "undefined_vars": {},
            "llm_explanation": None,
        }
    )
    
    # 1. AST Structure Analysis
    ast_result = analyze_ast(code)
    result.info["structure"] = ast_result
    
    if not ast_result.get("valid"):
        result.errors.append(f"Syntax Error: {ast_result.get('syntax_error', {}).get('message', 'Unknown')}")
        result.success = False
        return result
    
    # 2. Static Analysis with pylint
    pylint_issues, pylint_ok = run_pylint(code)
    result.info["static_issues"]["pylint"] = {
        "ok": pylint_ok,
        "count": len(pylint_issues),
        "issues": pylint_issues[:10],  # Limit to top 10
    }
    if pylint_issues:
        result.warnings.extend([issue.get("message", str(issue)) for issue in pylint_issues[:5]])
    
    # 3. Style Analysis with flake8
    flake8_issues, flake8_ok = run_flake8(code)
    result.info["static_issues"]["flake8"] = {
        "ok": flake8_ok,
        "count": len(flake8_issues),
        "sample": flake8_issues[:5],
    }
    
    # 4. Security Analysis with bandit
    bandit_issues, bandit_ok = run_bandit(code)
    result.info["static_issues"]["bandit"] = {
        "ok": bandit_ok,
        "count": len(bandit_issues),
        "issues": bandit_issues,
    }
    if bandit_issues:
        result.errors.extend([issue.get("issue_text", str(issue)) for issue in bandit_issues[:3]])
    
    # 5. Complexity Analysis
    complexity = get_code_complexity(code)
    result.info["complexity"] = complexity
    
    # 6. Undefined Variables
    undef = find_undefined_vars(code)
    result.info["undefined_vars"] = undef
    if undef.get("count", 0) > 0:
        result.warnings.append(f"Potentially undefined variables: {', '.join(undef.get('potentially_undefined', [])[:5])}")
    
    # 7. LLM Explanation (only if issues found)
    if use_llm and (pylint_issues or bandit_issues or undef.get("count", 0) > 0):
        summary = f"""
Issues found:
- Pylint: {len(pylint_issues)} issues
- Bandit: {len(bandit_issues)} security issues
- Undefined vars: {undef.get('count', 0)}

Provide a brief explanation of the most critical issues and how to fix them.
"""
        llm_response = call_local_model(
            QWEN_MODEL,
            summary + f"\n\nCode:\n{code[:1500]}...",
            temperature=0.3
        )
        result.info["llm_explanation"] = llm_response
    
    return result

# ============================================================================
# Code Debugging (AST + DeepSeek Reasoning)
# ============================================================================

def debug_code(code: str, issue_description: str, use_llm: bool = True) -> AnalysisResult:
    """
    Debug code by analyzing for syntax errors, then using reasoning.
    """
    result = AnalysisResult(
        success=True,
        tool="debug_code",
        info={
            "syntax_check": {},
            "ast_analysis": {},
            "llm_reasoning": None,
        }
    )
    
    # 1. Syntax Check
    ast_result = analyze_ast(code)
    if not ast_result.get("valid"):
        error = ast_result.get("syntax_error", {})
        result.errors.append(
            f"Syntax Error at line {error.get('line')}: {error.get('message')}"
        )
        result.info["syntax_check"] = error
        result.success = False
        return result
    
    result.info["syntax_check"] = {"status": "valid"}
    result.info["ast_analysis"] = ast_result
    
    # 2. Undefined Variables Detection
    undef = find_undefined_vars(code)
    if undef.get("potentially_undefined"):
        result.warnings.append(
            f"Potentially undefined: {', '.join(undef['potentially_undefined'][:5])}"
        )
    
    # 3. DeepSeek Reasoning for debugging
    if use_llm:
        prompt = f"""Debug this code. The issue reported is: {issue_description}

Code:
{code}

Analyze step-by-step:
1. Trace the execution path
2. Identify where logic diverges from expected behavior
3. Suggest the root cause
4. Provide a fix with explanation"""
        
        llm_response = call_local_model(
            DEEPSEEK_MODEL,
            prompt,
            temperature=0.5
        )
        result.info["llm_reasoning"] = llm_response
    
    return result


# Code Generation (LLM-based)


def generate_code(requirement: str, language: str = "python") -> AnalysisResult:
    """
    Generate code using local model (delegates to Claude for production).
    """
    result = AnalysisResult(
        success=True,
        tool="generate_code",
        info={
            "generated_code": None,
            "explanation": None,
        }
    )
    
    prompt = f"""Generate production-ready {language} code for:
{requirement}

Requirements:
- Include proper error handling
- Add type hints (if applicable)
- Include docstrings
- Follow best practices

Provide the code and brief explanation."""
    
    response = call_local_model(
        QWEN_MODEL,
        prompt,
        temperature=0.7
    )
    
    result.info["generated_code"] = response
    return result


# Quick Check (Lightweight, Fast)


def quick_check(code: str) -> AnalysisResult:
    """
    Fast health check: syntax + critical issues only.
    """
    result = AnalysisResult(
        success=True,
        tool="quick_check",
        info={}
    )
    
    # Syntax check
    ast_result = analyze_ast(code)
    if not ast_result.get("valid"):
        result.errors.append(f"Syntax Error: {ast_result['syntax_error']}")
        result.success = False
        return result
    
    # Pylint critical issues only
    try:
        proc = subprocess.run(
            ["pylint", "--output-format=json", "--disable=all", 
             "--enable=E", "-"],  # Errors only
            input=code,
            capture_output=True,
            text=True,
            timeout=10
        )
        if proc.stdout:
            issues = json.loads(proc.stdout)
            result.errors.extend([i.get("message", str(i)) for i in issues[:5]])
    except:
        pass
    
    # Security check
    try:
        proc = subprocess.run(
            ["bandit", "-f", "json", "-"],
            input=code,
            capture_output=True,
            text=True,
            timeout=10
        )
        if proc.stdout:
            data = json.loads(proc.stdout)
            issues = data.get("results", [])
            result.errors.extend([i.get("issue_text", str(i)) for i in issues[:5]])
    except (OSError, subprocess.SubprocessError, json.JSONDecodeError):
                pass
        
    return result
