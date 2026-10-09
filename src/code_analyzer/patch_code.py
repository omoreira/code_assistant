#!/usr/bin/env python3
# patch_code.py
"""
Intelligent code patching tool.
Combines diff analysis, AST-based impact assessment, and LLM reasoning.

Usage:
    python patch_code.py apply <file> "<patch_description>"
    python patch_code.py suggest <file> "<issue>"
    python patch_code.py validate <original> <patched>
    python patch_code.py rollback <file> [backup_path]
"""

import sys
import json
import ast
import subprocess
import difflib
import argparse
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
from dataclasses import dataclass, asdict, field
import hashlib
import shutil
from datetime import datetime
import requests

# ============================================================================
# Configuration
# ============================================================================

OLLAMA_BASE = "http://localhost:11434"
OLLAMA_TIMEOUT = 600
QWEN_MODEL = "qwen3:14b"
DEEPSEEK_MODEL = "deepseek-r1:14b"
PATCH_BACKUP_DIR = Path.home() / ".continue" / "patch_backups"
PATCH_BACKUP_DIR.mkdir(parents=True, exist_ok=True)

@dataclass
class PatchResult:
    """Result of a patch operation."""
    success: bool
    operation: str
    original_file: Optional[str] = None
    backup_path: Optional[str] = None
    patch_description: str = ""
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    info: Dict[str, Any] = field(default_factory=dict)
    duration_ms: Optional[int] = None
    
    def to_dict(self) -> Dict:
        """Convert to JSON-serializable dict."""
        return {
            "success": self.success,
            "operation": self.operation,
            "original_file": self.original_file,
            "backup_path": self.backup_path,
            "patch_description": self.patch_description,
            "errors": self.errors,
            "warnings": self.warnings,
            "info": self.info,
            "duration_ms": self.duration_ms,
        }

@dataclass
class CodeChange:
    """Represents a single code change."""
    line_start: int
    line_end: int
    original_code: str
    new_code: str
    reason: str
    dependencies: List[str] = field(default_factory=list)
    impact_level: str = "low"  # low, medium, high

# ============================================================================
# Backup & Rollback
# ============================================================================

def create_backup(file_path: str) -> str:
    """Create timestamped backup before patching."""
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_hash = hashlib.md5(file_path.read_bytes()).hexdigest()[:8]
    
    backup_name = f"{file_path.stem}_{timestamp}_{file_hash}{file_path.suffix}"
    backup_path = PATCH_BACKUP_DIR / backup_name
    
    shutil.copy2(file_path, backup_path)
    return str(backup_path)

def rollback_patch(file_path: str, backup_path: Optional[str] = None) -> PatchResult:
    """Restore file from backup."""
    result = PatchResult(
        success=False,
        operation="rollback",
        original_file=file_path,
    )
    
    file_path = Path(file_path)
    
    # Find latest backup if not specified
    if not backup_path:
        backups = sorted(
            PATCH_BACKUP_DIR.glob(f"{file_path.stem}_*{file_path.suffix}"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )
        if not backups:
            result.errors.append(f"No backups found for {file_path.name}")
            return result
        backup_path = str(backups[0])
    
    backup_path = Path(backup_path)
    if not backup_path.exists():
        result.errors.append(f"Backup not found: {backup_path}")
        return result
    
    try:
        shutil.copy2(backup_path, file_path)
        result.success = True
        result.backup_path = str(backup_path)
        result.info["restored_from"] = str(backup_path)
        return result
    except Exception as e:
        result.errors.append(f"Rollback failed: {str(e)}")
        return result

# ============================================================================
# Impact Analysis (AST-based)
# ============================================================================

def analyze_change_impact(
    original_code: str,
    patched_code: str,
    language: str = "python"
) -> Dict[str, Any]:
    """Analyze how changes impact the codebase."""
    if language != "python":
        return {"language": language, "warning": "Detailed impact analysis only for Python"}
    
    try:
        orig_tree = ast.parse(original_code)
        patch_tree = ast.parse(patched_code)
    except SyntaxError as e:
        return {"error": f"Syntax error: {str(e)}"}
    
    # Extract definitions
    def get_definitions(tree):
        defs = {"functions": set(), "classes": set(), "imports": set()}
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                defs["functions"].add(node.name)
            elif isinstance(node, ast.ClassDef):
                defs["classes"].add(node.name)
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                defs["imports"].add(str(node))
        return defs
    
    orig_defs = get_definitions(orig_tree)
    patch_defs = get_definitions(patch_tree)
    
    # Calculate changes
    removed_functions = orig_defs["functions"] - patch_defs["functions"]
    added_functions = patch_defs["functions"] - orig_defs["functions"]
    modified_functions = orig_defs["functions"] & patch_defs["functions"]
    
    impact = {
        "functions_removed": list(removed_functions),
        "functions_added": list(added_functions),
        "functions_modified": list(modified_functions),
        "breaking_changes": len(removed_functions) > 0,
        "impact_level": _assess_impact_level(
            len(removed_functions),
            len(added_functions),
            len(modified_functions)
        ),
    }
    
    return impact

def _assess_impact_level(removed: int, added: int, modified: int) -> str:
    """Assess overall impact level."""
    if removed > 0:
        return "high"  # Breaking change
    if modified > 3 or added > 5:
        return "high"
    if modified > 1 or added > 2:
        return "medium"
    return "low"

# ============================================================================
# Diff Analysis
# ============================================================================

def generate_unified_diff(original: str, patched: str, file_path: str = "code") -> str:
    """Generate unified diff between original and patched code."""
    orig_lines = original.splitlines(keepends=True)
    patch_lines = patched.splitlines(keepends=True)
    
    diff = difflib.unified_diff(
        orig_lines,
        patch_lines,
        fromfile=f"{file_path} (original)",
        tofile=f"{file_path} (patched)",
        lineterm=""
    )
    
    return "".join(diff)

def parse_diff(diff_text: str) -> List[Dict[str, Any]]:
    """Parse unified diff into structured changes."""
    changes = []
    current_change = None
    
    for line in diff_text.split("\n"):
        if line.startswith("@@"):
            if current_change:
                changes.append(current_change)
            # Extract line numbers: @@ -start,count +start,count @@
            match = re.search(r"@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@", line)
            if match:
                current_change = {
                    "original_start": int(match.group(1)),
                    "original_count": int(match.group(2) or 1),
                    "patched_start": int(match.group(3)),
                    "patched_count": int(match.group(4) or 1),
                    "removed_lines": [],
                    "added_lines": [],
                }
        elif current_change:
            if line.startswith("-"):
                current_change["removed_lines"].append(line[1:])
            elif line.startswith("+"):
                current_change["added_lines"].append(line[1:])
    
    if current_change:
        changes.append(current_change)
    
    return changes

# ============================================================================
# Patch Suggestion (LLM-based)
# ============================================================================

def suggest_patch(file_path: str, issue: str) -> PatchResult:
    """
    Analyze code and suggest a patch using Qwen (analysis) + DeepSeek (reasoning).
    """
    result = PatchResult(
        success=False,
        operation="suggest_patch",
        original_file=file_path,
        patch_description=issue,
        info={
            "analysis": None,
            "reasoning": None,
            "suggested_patch": None,
            "confidence": None,
        }
    )
    
    file_path = Path(file_path)
    if not file_path.exists():
        result.errors.append(f"File not found: {file_path}")
        return result
    
    code = file_path.read_text()
    language = _detect_language(file_path)
    
    # Step 1: Qwen analyzes the issue in context
    analysis_prompt = f"""Analyze this {language} code for the issue: {issue}

Code:
{code}

Identify:
1. Root cause of the issue
2. Lines affected
3. What needs to change
4. Potential side effects"""
    
    analysis = call_local_model(QWEN_MODEL, analysis_prompt, temperature=0.3)
    result.info["analysis"] = analysis
    
    # Step 2: DeepSeek reasons about the fix
    reasoning_prompt = f"""Given this issue and analysis, reason through the fix:

Issue: {issue}
Analysis: {analysis}

Code to fix:
{code[:2000]}...

Step through the fix:
1. What's the root cause?
2. What's the safest way to fix it?
3. What edge cases exist?
4. Provide the patched code section"""
    
    reasoning = call_local_model(DEEPSEEK_MODEL, reasoning_prompt, temperature=0.5)
    result.info["reasoning"] = reasoning
    
    # Step 3: Extract suggested code from reasoning
    suggested = _extract_code_from_reasoning(reasoning, language)
    if suggested:
        result.info["suggested_patch"] = suggested
        result.info["confidence"] = _estimate_confidence(reasoning)
        result.success = True
    else:
        result.warnings.append("Could not extract code suggestion from reasoning")
    
    return result

def call_local_model(
    model: str,
    prompt: str,
    temperature: float = 0.7,
) -> str:
    """Call Ollama model."""
    try:
        response = requests.post(
            f"{OLLAMA_BASE}/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "temperature": temperature,
            },
            timeout=OLLAMA_TIMEOUT
        )
        response.raise_for_status()
        return response.json().get("response", "").strip()
    except Exception as e:
        return f"[LLM Error: {str(e)}]"

def _extract_code_from_reasoning(text: str, language: str) -> Optional[str]:
    """Extract code block from LLM reasoning."""
    import re
    
    patterns = [
        rf"```{language}\n(.*?)\n```",
        r"```\n(.*?)\n```",
        r"<code>(.*?)</code>",
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.DOTALL)
        if match:
            return match.group(1).strip()
    
    return None

def _estimate_confidence(reasoning: str) -> float:
    """Estimate confidence in the suggested patch."""
    confidence_indicators = [
        ("confident", 0.9),
        ("certain", 0.9),
        ("definitely", 0.85),
        ("should", 0.7),
        ("likely", 0.65),
        ("maybe", 0.5),
        ("uncertain", 0.4),
    ]
    
    reasoning_lower = reasoning.lower()
    confidence = 0.5  # Default
    
    for indicator, score in confidence_indicators:
        if indicator in reasoning_lower:
            confidence = max(confidence, score)
    
    return round(confidence, 2)

# ============================================================================
# Apply Patch (with Validation)
# ============================================================================

def apply_patch(
    file_path: str,
    patch_description: str,
    patch_code: str,
    validate: bool = True,
    auto_backup: bool = True,
) -> PatchResult:
    """
    Apply a patch to a file with validation and backup.
    
    Args:
        file_path: File to patch
        patch_description: What the patch does
        patch_code: The patched code (full file or section)
        validate: Run validation before applying
        auto_backup: Create backup before patching
    """
    result = PatchResult(
        success=False,
        operation="apply_patch",
        original_file=file_path,
        patch_description=patch_description,
        info={
            "validation": {},
            "diff": None,
            "impact": {},
        }
    )
    
    file_path = Path(file_path)
    if not file_path.exists():
        result.errors.append(f"File not found: {file_path}")
        return result
    
    original_code = file_path.read_text()
    language = _detect_language(file_path)
    
    # Step 1: Backup
    if auto_backup:
        try:
            backup_path = create_backup(str(file_path))
            result.backup_path = backup_path
        except Exception as e:
            result.errors.append(f"Backup failed: {str(e)}")
            return result
    
    # Step 2: Analyze impact
    impact = analyze_change_impact(original_code, patch_code, language)
    result.info["impact"] = impact
    
    if impact.get("breaking_changes"):
        result.warnings.append("⚠️  This patch contains breaking changes (functions removed)")
    
    if impact.get("impact_level") == "high":
        result.warnings.append("⚠️  High-impact patch; recommend thorough testing")
    
    # Step 3: Validation
    if validate:
        validation = _validate_patch(patch_code, language)
        result.info["validation"] = validation
        
        if not validation.get("syntax_valid"):
            result.errors.append(f"Syntax error in patched code: {validation.get('error')}")
            return result
        
        if validation.get("warnings"):
            result.warnings.extend(validation["warnings"])
    
    # Step 4: Generate diff
    diff = generate_unified_diff(original_code, patch_code, str(file_path))
    result.info["diff"] = diff
    
    # Step 5: Apply patch
    try:
        file_path.write_text(patch_code)
        result.success = True
    except Exception as e:
        result.errors.append(f"Failed to write patched code: {str(e)}")
        # Attempt rollback
        if auto_backup and result.backup_path:
            rollback_patch(str(file_path), result.backup_path)
            result.warnings.append("Automatic rollback performed")
        return result
    
    result.info["patch_applied"] = True
    return result

def _validate_patch(code: str, language: str) -> Dict[str, Any]:
    """Validate patched code before applying."""
    validation = {
        "syntax_valid": False,
        "warnings": [],
        "error": None,
    }
    
    if language == "python":
        try:
            ast.parse(code)
            validation["syntax_valid"] = True
        except SyntaxError as e:
            validation["error"] = f"Line {e.lineno}: {e.msg}"
            return validation
        
        # Additional checks
        if "import *" in code:
            validation["warnings"].append("Wildcard imports detected")
        if code.count("except:
