"""
DependencyMapper: Map code dependencies across the project.

Tracks which modules depend on which other modules, helping to understand
the impact of refactoring operations.
"""

import re
from pathlib import Path
from typing import Dict, Set, List, Optional, Tuple
from collections import defaultdict, deque


class DependencyMapper:
    """
    Maps and analyzes code dependencies across the project.
    """
    
    def __init__(self, project_root: Optional[str] = None):
        """Initialize DependencyMapper."""
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.dependencies: Dict[str, Set[str]] = defaultdict(set)
        self.reverse_dependencies: Dict[str, Set[str]] = defaultdict(set)
        self.circular_deps: List[List[str]] = []
        
    def build_dependency_graph(self) -> Dict[str, Set[str]]:
        """
        Build a complete dependency graph for the project.
        
        Returns:
            Dictionary mapping each module to its dependencies
        """
        self.dependencies.clear()
        self.reverse_dependencies.clear()
        
        # Scan all Python files
        for python_file in self.project_root.rglob("*.py"):
            try:
                content = python_file.read_text(encoding="utf-8")
                module_name = self._file_to_module(python_file)
                
                # Extract imports
                dependencies = self._extract_imports(content)
                self.dependencies[module_name] = dependencies
                
                # Build reverse mapping
                for dep in dependencies:
                    self.reverse_dependencies[dep].add(module_name)
            except Exception:
                pass
        
        return dict(self.dependencies)
    
    def find_circular_dependencies(self) -> List[List[str]]:
        """
        Find all circular dependencies in the project.
        
        Returns:
            List of circular dependency cycles
        """
        self.circular_deps = []
        visited = set()
        rec_stack = set()
        
        for module in self.dependencies:
            if module not in visited:
                self._find_cycles_dfs(module, visited, rec_stack, [])
        
        return self.circular_deps
    
    def _find_cycles_dfs(
        self,
        node: str,
        visited: Set[str],
        rec_stack: Set[str],
        path: List[str]
    ) -> None:
        """DFS to find circular dependencies."""
        visited.add(node)
        rec_stack.add(node)
        path.append(node)
        
        for neighbor in self.dependencies.get(node, set()):
            if neighbor not in visited:
                self._find_cycles_dfs(neighbor, visited, rec_stack, path)
            elif neighbor in rec_stack:
                # Found a cycle
                cycle_start = path.index(neighbor)
                cycle = path[cycle_start:] + [neighbor]
                if cycle not in self.circular_deps:
                    self.circular_deps.append(cycle)
        
        path.pop()
        rec_stack.remove(node)
    
    def get_dependents(self, module: str) -> Set[str]:
        """
        Get all modules that depend on the given module.
        
        Args:
            module: Module name to check
            
        Returns:
            Set of dependent module names
        """
        return self.reverse_dependencies.get(module, set())
    
    def get_dependencies(self, module: str) -> Set[str]:
        """
        Get all modules that the given module depends on.
        
        Args:
            module: Module name to check
            
        Returns:
            Set of dependency module names
        """
        return self.dependencies.get(module, set())
    
    def get_impact(self, module: str) -> Dict[str, Set[str]]:
        """
        Analyze the impact of refactoring a module.
        
        Returns:
            Dictionary with direct and transitive dependents
        """
        direct = self.get_dependents(module)
        transitive = self._get_transitive_dependents(module)
        
        return {
            "direct_dependents": direct,
            "transitive_dependents": transitive - direct,
            "all_dependents": transitive,
            "total_affected": len(transitive)
        }
    
    def _get_transitive_dependents(self, module: str) -> Set[str]:
        """Get all transitive dependents of a module (BFS)."""
        transitive = set()
        queue = deque([module])
        visited = {module}
        
        while queue:
            current = queue.popleft()
            dependents = self.get_dependents(current)
            
            for dependent in dependents:
                if dependent not in visited:
                    transitive.add(dependent)
                    visited.add(dependent)
                    queue.append(dependent)
        
        return transitive
    
    def suggest_refactoring_order(self) -> List[str]:
        """
        Suggest an order to refactor modules to minimize cascading changes.
        
        Modules with fewer dependents should be refactored first.
        
        Returns:
            List of modules ordered by refactoring priority
        """
        modules_with_dependents = [
            (module, len(self.get_dependents(module)))
            for module in self.dependencies.keys()
        ]
        
        # Sort by number of dependents (ascending)
        modules_with_dependents.sort(key=lambda x: x[1])
        
        return [module for module, _ in modules_with_dependents]
    
    def _extract_imports(self, content: str) -> Set[str]:
        """Extract all imported modules from Python code."""
        imports = set()
        
        # Patterns for different import styles
        patterns = [
            r"from\s+([\w\.]+)\s+import",
            r"import\s+([\w\.]+)",
        ]
        
        for pattern in patterns:
            for match in re.finditer(pattern, content):
                module = match.group(1)
                imports.add(module)
        
        return imports
    
    def _file_to_module(self, file_path: Path) -> str:
        """Convert file path to module name."""
        # Get path relative to project root
        try:
            rel_path = file_path.relative_to(self.project_root)
        except ValueError:
            rel_path = file_path
        
        # Remove .py extension
        module_path = str(rel_path).replace(".py", "")
        
        # Convert path separators to dots
        module_name = module_path.replace("/", ".").replace("\\", ".")
        
        return module_name
    
    def export_dependency_graph(self, output_format: str = "text") -> str:
        """
        Export the dependency graph in various formats.
        
        Args:
            output_format: "text", "dot", or "json"
            
        Returns:
            Formatted dependency graph
        """
        if output_format == "text":
            return self._export_as_text()
        elif output_format == "dot":
            return self._export_as_dot()
        elif output_format == "json":
            return self._export_as_json()
        else:
            raise ValueError(f"Unknown format: {output_format}")
    
    def _export_as_text(self) -> str:
        """Export as text format."""
        lines = ["DEPENDENCY GRAPH", "=" * 50, ""]
        
        for module in sorted(self.dependencies.keys()):
            deps = self.dependencies[module]
            if deps:
                lines.append(f"{module}:")
                for dep in sorted(deps):
                    lines.append(f"  → {dep}")
            else:
                lines.append(f"{module}: (no dependencies)")
        
        return "\n".join(lines)
    
    def _export_as_dot(self) -> str:
        """Export as Graphviz DOT format."""
        lines = ["digraph DependencyGraph {", "  rankdir=LR;", ""]
        
        for module in self.dependencies:
            lines.append(f"  \"{module}\";")
        
        lines.append("")
        
        for module, deps in self.dependencies.items():
            for dep in deps:
                lines.append(f"  \"{module}\" -> \"{dep}\";")
        
        lines.append("}")
        return "\n".join(lines)
    
    def _export_as_json(self) -> str:
        """Export as JSON format."""
        import json
        
        # Convert sets to lists for JSON serialization
        graph_dict = {
            module: list(deps)
            for module, deps in self.dependencies.items()
        }
        
        return json.dumps(graph_dict, indent=2, sort_keys=True)
    
    def get_statistics(self) -> Dict[str, any]:
        """Get statistics about the dependency graph."""
        all_modules = set(self.dependencies.keys())
        
        # Modules with no dependencies
        independent = {m for m in all_modules if not self.dependencies[m]}
        
        # Modules with no dependents
        leaves = {m for m in all_modules if m not in self.reverse_dependencies}
        
        # Average dependencies
        total_deps = sum(len(deps) for deps in self.dependencies.values())
        avg_deps = total_deps / len(all_modules) if all_modules else 0
        
        return {
            "total_modules": len(all_modules),
            "total_dependencies": total_deps,
            "average_dependencies_per_module": round(avg_deps, 2),
            "independent_modules": len(independent),
            "leaf_modules": len(leaves),
            "circular_dependencies": len(self.circular_deps),
            "circular_dependency_cycles": self.circular_deps,
        }
    
    def clear_cache(self) -> None:
        """Clear internal caches."""
        self.dependencies.clear()
        self.reverse_dependencies.clear()
        self.circular_deps.clear()
