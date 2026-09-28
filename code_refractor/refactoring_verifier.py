"""
RefactoringVerifier: Verify code safety after refactoring operations.

This module ensures that refactoring operations don't break code by:
1. Tracking all path and name changes
2. Finding all references to changed elements
3. Validating that all imports remain valid
4. Checking for circular dependencies
5. Ensuring all external references are updated
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass, field


@dataclass
class RefactoringIssue:
    """Represents a potential issue found during refactoring verification."""
    
    severity: str  # "error", "warning", "info"
    file_path: str
    issue_type: str  # "broken_import", "undefined_reference", "circular_dep", etc.
    message: str
    line_number: Optional[int] = None
    suggested_fix: Optional[str] = None


@dataclass
class RefactoringMap:
    """Maps old names/paths to new ones."""
    
    old_name: str
    new_name: str
    old_path: str
    new_path: str
    element_type: str  # "function", "class", "module", "variable"
    references: Dict[str, List[int]] = field(default_factory=dict)  # file -> line numbers


class RefactoringVerifier:
    """
    Verifies code integrity after refactoring operations.
    
    Ensures all paths, imports, and references remain consistent.
    """
    
    def __init__(self, project_root: Optional[str] = None):
        """
        Initialize the RefactoringVerifier.
        
        Args:
            project_root: Root directory of the project (default: current dir)
        """
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.issues: List[RefactoringIssue] = []
        self.refactoring_maps: List[RefactoringMap] = []
        self.import_cache: Dict[str, Set[str]] = {}
        self.defined_symbols: Dict[str, Set[str]] = {}
        
    def check_refactoring_safety(
        self,
        old_path: str,
        new_path: str,
        element_type: str = "module"
    ) -> List[RefactoringIssue]:
        """
        Check if a refactoring operation is safe before executing.
        
        Args:
            old_path: Original file/function path
            new_path: New file/function path
            element_type: Type of element being refactored
            
        Returns:
            List of issues found (empty if safe)
        """
        self.issues = []
        
        # Create refactoring map
        refmap = RefactoringMap(
            old_name=Path(old_path).stem,
            new_name=Path(new_path).stem,
            old_path=old_path,
            new_path=new_path,
            element_type=element_type
        )
        
        # Run verification checks
        self._check_file_existence(old_path)
        self._check_path_conflicts(new_path)
        self._find_all_references(old_path, refmap)
        self._check_import_chain(old_path, new_path)
        self._check_circular_dependencies(new_path)
        self._validate_new_location(new_path)
        
        return self.issues
    
    def _check_file_existence(self, old_path: str) -> None:
        """Check if the file to be refactored exists."""
        full_path = self.project_root / old_path
        if not full_path.exists():
            self.issues.append(RefactoringIssue(
                severity="error",
                file_path=old_path,
                issue_type="file_not_found",
                message=f"File to refactor does not exist: {old_path}"
            ))
    
    def _check_path_conflicts(self, new_path: str) -> None:
        """Check if the new path would overwrite existing files."""
        full_path = self.project_root / new_path
        if full_path.exists():
            self.issues.append(RefactoringIssue(
                severity="error",
                file_path=new_path,
                issue_type="path_conflict",
                message=f"New path already exists: {new_path}",
                suggested_fix=f"Choose a different path or remove {new_path} first"
            ))
    
    def _find_all_references(self, old_path: str, refmap: RefactoringMap) -> None:
        """Find all files that reference the element being refactored."""
        old_module = Path(old_path).stem
        search_patterns = [
            rf"from\s+.*{re.escape(old_module)}\s+import",
            rf"import\s+.*{re.escape(old_module)}",
            rf"require\(['\"].*{re.escape(old_module)}",
        ]
        
        for python_file in self.project_root.rglob("*.py"):
            if python_file.samefile(self.project_root / old_path):
                continue
            
            try:
                content = python_file.read_text(encoding="utf-8", errors="ignore")
                for pattern in search_patterns:
                    for match in re.finditer(pattern, content):
                        line_num = content[:match.start()].count("\n") + 1
                        if str(python_file) not in refmap.references:
                            refmap.references[str(python_file)] = []
                        refmap.references[str(python_file)].append(line_num)
            except Exception:
                pass
        
        self.refactoring_maps.append(refmap)
    
    def _check_import_chain(self, old_path: str, new_path: str) -> None:
        """Verify that the import chain remains valid after refactoring."""
        try:
            old_full = self.project_root / old_path
            new_full = self.project_root / new_path
            
            # Check if __init__.py files exist in parent directories
            old_parents = [p for p in old_full.parents if p >= self.project_root]
            new_parents = [p for p in new_full.parents if p >= self.project_root]
            
            for parent in old_parents:
                if (parent / "__init__.py").exists():
                    continue
                    
            for parent in new_parents:
                if parent == self.project_root:
                    break
                if not (parent / "__init__.py").exists():
                    self.issues.append(RefactoringIssue(
                        severity="warning",
                        file_path=str(new_path),
                        issue_type="missing_init",
                        message=f"Missing __init__.py in: {parent}",
                        suggested_fix=f"Create {parent}/__init__.py"
                    ))
        except Exception as e:
            self.issues.append(RefactoringIssue(
                severity="warning",
                file_path=new_path,
                issue_type="import_chain_check_failed",
                message=f"Could not verify import chain: {str(e)}"
            ))
    
    def _check_circular_dependencies(self, new_path: str) -> None:
        """Check for circular dependencies after refactoring."""
        try:
            new_full = self.project_root / new_path
            if not new_full.exists():
                return
            
            content = new_full.read_text(encoding="utf-8", errors="ignore")
            
            # Extract imports
            import_pattern = r"(?:from|import)\s+[\w\.]+"
            imports = re.findall(import_pattern, content)
            
            # Simple circular dependency check
            new_module = new_path.replace("/", ".").replace(".py", "")
            for imp in imports:
                if new_module in imp:
                    self.issues.append(RefactoringIssue(
                        severity="warning",
                        file_path=new_path,
                        issue_type="potential_circular_dep",
                        message=f"Potential circular import detected: {imp}",
                        suggested_fix="Review the import structure"
                    ))
        except Exception:
            pass
    
    def _validate_new_location(self, new_path: str) -> None:
        """Validate that the new location is appropriate."""
        new_full = self.project_root / new_path
        
        # Check parent directory exists
        if not new_full.parent.exists():
            self.issues.append(RefactoringIssue(
                severity="error",
                file_path=new_path,
                issue_type="parent_dir_missing",
                message=f"Parent directory does not exist: {new_full.parent}",
                suggested_fix=f"Create directory: {new_full.parent}"
            ))
    
    def get_affected_files(self) -> Dict[str, List[int]]:
        """
        Get all files affected by the refactoring.
        
        Returns:
            Dictionary mapping file paths to line numbers
        """
        affected = {}
        for refmap in self.refactoring_maps:
            for file_path, lines in refmap.references.items():
                affected[file_path] = lines
        return affected
    
    def generate_refactoring_report(self) -> str:
        """Generate a detailed report of refactoring verification results."""
        lines = [
            "=" * 70,
            "REFACTORING VERIFICATION REPORT",
            "=" * 70,
            "",
        ]
        
        # Summary
        errors = [i for i in self.issues if i.severity == "error"]
        warnings = [i for i in self.issues if i.severity == "warning"]
        
        lines.append(f"Issues Found: {len(self.issues)}")
        lines.append(f"  - Errors: {len(errors)}")
        lines.append(f"  - Warnings: {len(warnings)}")
        lines.append("")
        
        # Details
        if errors:
            lines.append("ERRORS (must fix before refactoring):")
            for issue in errors:
                lines.append(f"  [{issue.file_path}] {issue.message}")
                if issue.suggested_fix:
                    lines.append(f"    💡 Fix: {issue.suggested_fix}")
            lines.append("")
        
        if warnings:
            lines.append("WARNINGS (review before refactoring):")
            for issue in warnings:
                lines.append(f"  [{issue.file_path}] {issue.message}")
                if issue.suggested_fix:
                    lines.append(f"    💡 Fix: {issue.suggested_fix}")
            lines.append("")
        
        # Affected files
        affected = self.get_affected_files()
        if affected:
            lines.append("AFFECTED FILES (will need path updates):")
            for file_path, line_nums in affected.items():
                lines.append(f"  {file_path}: lines {line_nums}")
            lines.append("")
        
        # Safety verdict
        if errors:
            lines.append("VERDICT: ❌ UNSAFE - Fix errors before proceeding")
        elif warnings:
            lines.append("VERDICT: ⚠️  PROCEED WITH CAUTION - Review warnings first")
        else:
            lines.append("VERDICT: ✅ SAFE - No issues found")
        
        lines.append("=" * 70)
        
        return "\n".join(lines)
    
    def clear_issues(self) -> None:
        """Clear the issues list."""
        self.issues = []
        self.refactoring_maps = []
