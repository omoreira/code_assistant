"""
CodeRefactorer: Execute refactoring operations with automatic path/import updates.

This module performs actual refactoring while automatically updating:
1. All import statements
2. All file path references
3. All module names in configuration files
4. All related documentation
"""

import shutil
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass

from code_refractor.refactoring_verifier import RefactoringVerifier, RefactoringIssue
from code_refractor.path_resolver import PathResolver
from code_refractor.dependency_mapper import DependencyMapper


@dataclass
class RefactoringResult:
    """Result of a refactoring operation."""
    
    success: bool
    old_path: str
    new_path: str
    files_modified: int
    files_moved: int
    changes_made: List[str]
    errors: List[RefactoringIssue]


class CodeRefactorer:
    """
    Executes refactoring operations with automatic verification and path updates.
    """
    
    def __init__(self, project_root: Optional[str] = None, dry_run: bool = False):
        """
        Initialize the CodeRefactorer.
        
        Args:
            project_root: Root directory of the project
            dry_run: If True, show what would be done without making changes
        """
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.dry_run = dry_run
        self.verifier = RefactoringVerifier(str(self.project_root))
        self.path_resolver = PathResolver(str(self.project_root))
        self.dependency_mapper = DependencyMapper(str(self.project_root))
        self.changes_made: List[str] = []
        
    def refactor_with_verification(
        self,
        old_path: str,
        new_path: str,
        element_type: str = "module"
    ) -> RefactoringResult:
        """
        Perform refactoring with automatic verification.
        
        Args:
            old_path: Current path/name
            new_path: Desired path/name
            element_type: Type of element (module, class, function, etc.)
            
        Returns:
            RefactoringResult with details of changes made
        """
        self.changes_made = []
        
        # Verify safety first
        issues = self.verifier.check_refactoring_safety(
            old_path, new_path, element_type
        )
        
        # Check for blocking errors
        errors = [i for i in issues if i.severity == "error"]
        if errors:
            return RefactoringResult(
                success=False,
                old_path=old_path,
                new_path=new_path,
                files_modified=0,
                files_moved=0,
                changes_made=self.changes_made,
                errors=errors
            )
        
        # Proceed with refactoring
        try:
            if not self.dry_run:
                # Step 1: Move/copy the file
                self._move_file(old_path, new_path)
                
                # Step 2: Update all imports in other files
                self._update_imports(old_path, new_path)
                
                # Step 3: Update references in config files
                self._update_config_references(old_path, new_path)
                
                # Step 4: Update documentation
                self._update_documentation(old_path, new_path)
                
                # Step 5: Cleanup old location if applicable
                self._cleanup_old_location(old_path)
            else:
                self._simulate_changes(old_path, new_path)
            
            # Get statistics
            affected = self.verifier.get_affected_files()
            
            return RefactoringResult(
                success=True,
                old_path=old_path,
                new_path=new_path,
                files_modified=len(affected),
                files_moved=1,
                changes_made=self.changes_made,
                errors=[]
            )
        except Exception as e:
            return RefactoringResult(
                success=False,
                old_path=old_path,
                new_path=new_path,
                files_modified=0,
                files_moved=0,
                changes_made=self.changes_made,
                errors=[RefactoringIssue(
                    severity="error",
                    file_path=old_path,
                    issue_type="refactoring_failed",
                    message=f"Refactoring failed: {str(e)}"
                )]
            )
    
    def _move_file(self, old_path: str, new_path: str) -> None:
        """Move or copy the file to its new location."""
        old_full = self.project_root / old_path
        new_full = self.project_root / new_path
        
        # Create parent directories if needed
        new_full.parent.mkdir(parents=True, exist_ok=True)
        
        # Copy file to new location
        shutil.copy2(old_full, new_full)
        self.changes_made.append(f"Moved file: {old_path} → {new_path}")
    
    def _update_imports(self, old_path: str, new_path: str) -> None:
        """Update all import statements that reference the moved file."""
        old_module = self._path_to_module(old_path)
        new_module = self._path_to_module(new_path)
        
        # Find all files that import the old module
        for python_file in self.project_root.rglob("*.py"):
            if python_file == self.project_root / old_path:
                continue
            
            try:
                content = python_file.read_text(encoding="utf-8")
                original = content
                
                # Update various import patterns
                patterns = [
                    (
                        rf"from\s+{re.escape(old_module)}\s+import",
                        f"from {new_module} import"
                    ),
                    (
                        rf"import\s+{re.escape(old_module)}(?:\s|$|\.)",
                        f"import {new_module}"
                    ),
                ]
                
                for pattern, replacement in patterns:
                    content = re.sub(pattern, replacement, content)
                
                if content != original:
                    if not self.dry_run:
                        python_file.write_text(content, encoding="utf-8")
                    self.changes_made.append(
                        f"Updated imports in: {python_file.relative_to(self.project_root)}"
                    )
            except Exception:
                pass
    
    def _update_config_references(self, old_path: str, new_path: str) -> None:
        """Update references in configuration files (YAML, JSON, etc.)."""
        old_name = Path(old_path).stem
        new_name = Path(new_path).stem
        
        config_patterns = ["*.yaml", "*.yml", "*.json", "*.toml", "*.ini"]
        
        for config_file in self.project_root.rglob("*"):
            if not config_file.is_file():
                continue
            
            # Check if matches config pattern
            if not any(config_file.match(pattern) for pattern in config_patterns):
                continue
            
            try:
                content = config_file.read_text(encoding="utf-8")
                original = content
                
                # Simple replacement (can be enhanced for specific formats)
                content = content.replace(old_name, new_name)
                content = content.replace(old_path, new_path)
                
                if content != original:
                    if not self.dry_run:
                        config_file.write_text(content, encoding="utf-8")
                    self.changes_made.append(
                        f"Updated config: {config_file.relative_to(self.project_root)}"
                    )
            except Exception:
                pass
    
    def _update_documentation(self, old_path: str, new_path: str) -> None:
        """Update references in documentation files."""
        old_name = Path(old_path).stem
        new_name = Path(new_path).stem
        
        doc_patterns = ["*.md", "*.rst", "*.txt"]
        
        for doc_file in self.project_root.rglob("*"):
            if not doc_file.is_file():
                continue
            
            if not any(doc_file.match(pattern) for pattern in doc_patterns):
                continue
            
            try:
                content = doc_file.read_text(encoding="utf-8")
                original = content
                
                # Update references
                content = re.sub(
                    rf"\b{re.escape(old_name)}\b",
                    new_name,
                    content
                )
                
                if content != original:
                    if not self.dry_run:
                        doc_file.write_text(content, encoding="utf-8")
                    self.changes_made.append(
                        f"Updated docs: {doc_file.relative_to(self.project_root)}"
                    )
            except Exception:
                pass
    
    def _cleanup_old_location(self, old_path: str) -> None:
        """Remove the old file after successful refactoring."""
        old_full = self.project_root / old_path
        if old_full.exists():
            old_full.unlink()
            self.changes_made.append(f"Removed old file: {old_path}")
    
    def _simulate_changes(self, old_path: str, new_path: str) -> None:
        """In dry-run mode, simulate what would be changed."""
        old_module = self._path_to_module(old_path)
        new_module = self._path_to_module(new_path)
        
        self.changes_made.append(f"[DRY RUN] Would move: {old_path} → {new_path}")
        
        # Find affected files
        for python_file in self.project_root.rglob("*.py"):
            if python_file == self.project_root / old_path:
                continue
            
            try:
                content = python_file.read_text(encoding="utf-8")
                if old_module in content:
                    self.changes_made.append(
                        f"[DRY RUN] Would update imports: {python_file.relative_to(self.project_root)}"
                    )
            except Exception:
                pass
    
    @staticmethod
    def _path_to_module(path: str) -> str:
        """Convert file path to module name."""
        # Remove .py extension if present
        if path.endswith(".py"):
            path = path[:-3]
        
        # Convert path separators to dots
        return path.replace("/", ".").replace("\\", ".")
    
    def set_dry_run(self, dry_run: bool) -> None:
        """Set dry-run mode."""
        self.dry_run = dry_run
    
    def get_verification_report(self) -> str:
        """Get the verification report from the last operation."""
        return self.verifier.generate_refactoring_report()
