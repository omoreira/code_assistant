"""
PathResolver: Resolve and validate all paths after refactoring.

Ensures that all file paths, import paths, and relative references remain valid.
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple


class PathResolver:
    """
    Resolves and validates paths after refactoring operations.
    """
    
    def __init__(self, project_root: Optional[str] = None):
        """Initialize PathResolver."""
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.path_mappings: Dict[str, str] = {}  # old_path -> new_path
        self.broken_imports: List[Tuple[str, str, int]] = []  # (file, import, line)
        self.undefined_references: List[Tuple[str, str, int]] = []  # (file, ref, line)
        
    def register_path_change(self, old_path: str, new_path: str) -> None:
        """Register a path change for tracking."""
        self.path_mappings[old_path] = new_path
    
    def resolve_all_imports(self) -> List[Tuple[str, str, int]]:
        """
        Resolve all imports in the project.
        
        Returns:
            List of broken imports (file, import_statement, line_number)
        """
        self.broken_imports = []
        
        for python_file in self.project_root.rglob("*.py"):
            try:
                content = python_file.read_text(encoding="utf-8")
                self._check_file_imports(python_file, content)
            except Exception:
                pass
        
        return self.broken_imports
    
    def _check_file_imports(self, file_path: Path, content: str) -> None:
        """Check imports in a single file."""
        lines = content.split("\n")
        
        for line_num, line in enumerate(lines, 1):
            # Extract import statements
            import_match = re.match(
                r"^\s*(?:from\s+([\w\.]+)\s+)?import\s+(.*)",
                line
            )
            
            if not import_match:
                continue
            
            module_path = import_match.group(1) or import_match.group(2).split()[0]
            
            # Check if module exists
            if not self._module_exists(module_path):
                self.broken_imports.append(
                    (str(file_path), line.strip(), line_num)
                )
    
    def _module_exists(self, module_path: str) -> bool:
        """Check if a module path exists in the project."""
        # Convert module path to file path
        file_path = module_path.replace(".", os.sep) + ".py"
        
        # Check in project root
        if (self.project_root / file_path).exists():
            return True
        
        # Check if it's a standard library or third-party module
        try:
            __import__(module_path)
            return True
        except ImportError:
            return False
    
    def resolve_relative_paths(self, file_path: str) -> Dict[str, str]:
        """
        Resolve all relative paths in a file to absolute paths.
        
        Returns:
            Dictionary mapping relative paths to absolute paths
        """
        result = {}
        file_path = Path(file_path)
        
        if not file_path.exists():
            return result
        
        try:
            content = file_path.read_text(encoding="utf-8")
            
            # Pattern for relative path references
            patterns = [
                r"open\(['\"]([^'\"]+)['\"]",
                r"load\(['\"]([^'\"]+)['\"]",
                r"open_file\(['\"]([^'\"]+)['\"]",
                r"Path\(['\"]([^'\"]+)['\"]",
            ]
            
            for pattern in patterns:
                for match in re.finditer(pattern, content):
                    rel_path = match.group(1)
                    abs_path = (file_path.parent / rel_path).resolve()
                    result[rel_path] = str(abs_path)
        except Exception:
            pass
        
        return result
    
    def update_path_references(
        self,
        file_path: str,
        old_path: str,
        new_path: str
    ) -> int:
        """
        Update all references to old_path with new_path in a file.
        
        Returns:
            Number of replacements made
        """
        try:
            file_path = Path(file_path)
            content = file_path.read_text(encoding="utf-8")
            original = content
            
            # Replace various path formats
            replacements = [
                (re.escape(old_path), new_path),
                (re.escape(old_path.replace("/", "\\\\")), new_path.replace("/", "\\\\")),
                (re.escape(old_path.replace("\\", "/")), new_path.replace("\\", "/")),
            ]
            
            count = 0
            for old_pattern, new_pattern in replacements:
                content, n = re.subn(old_pattern, new_pattern, content)
                count += n
            
            if content != original:
                file_path.write_text(content, encoding="utf-8")
            
            return count
        except Exception:
            return 0
    
    def find_path_references(self, path: str) -> List[Tuple[str, int]]:
        """
        Find all references to a path in the project.
        
        Returns:
            List of (file_path, line_number) tuples
        """
        references = []
        escaped_path = re.escape(path)
        
        for file_path in self.project_root.rglob("*"):
            if not file_path.is_file():
                continue
            
            try:
                # Skip binary files
                if file_path.suffix in [".png", ".jpg", ".bin", ".pyc"]:
                    continue
                
                content = file_path.read_text(encoding="utf-8", errors="ignore")
                
                for line_num, line in enumerate(content.split("\n"), 1):
                    if re.search(escaped_path, line):
                        references.append((str(file_path), line_num))
            except Exception:
                pass
        
        return references
    
    def validate_all_paths(self) -> Tuple[bool, List[str]]:
        """
        Validate all paths in the project.
        
        Returns:
            (is_valid, list_of_issues)
        """
        issues = []
        
        for file_path in self.project_root.rglob("*.py"):
            try:
                content = file_path.read_text(encoding="utf-8")
                
                # Check for hardcoded paths that might be broken
                path_pattern = r"['\"]([./\\][^'\"]*)['\"]"
                for match in re.finditer(path_pattern, content):
                    potential_path = match.group(1)
                    full_path = (file_path.parent / potential_path).resolve()
                    
                    if not full_path.exists() and not potential_path.startswith("http"):
                        issues.append(
                            f"Broken path in {file_path}: {potential_path}"
                        )
            except Exception:
                pass
        
        return len(issues) == 0, issues
    
    def get_import_map(self) -> Dict[str, Set[str]]:
        """
        Get a map of all imports in the project.
        
        Returns:
            Dictionary mapping file paths to imported modules
        """
        import_map = {}
        
        for python_file in self.project_root.rglob("*.py"):
            try:
                content = python_file.read_text(encoding="utf-8")
                imports = set()
                
                # Extract all imports
                import_pattern = r"(?:from\s+([\w\.]+)|import\s+([\w\.]+))"
                for match in re.finditer(import_pattern, content):
                    module = match.group(1) or match.group(2)
                    imports.add(module)
                
                import_map[str(python_file)] = imports
            except Exception:
                pass
        
        return import_map
    
    def clear_cache(self) -> None:
        """Clear internal caches."""
        self.path_mappings.clear()
        self.broken_imports.clear()
        self.undefined_references.clear()
