"""
Code Refractor Module

Intelligent code refactoring with automatic verification of path consistency.
Ensures that when code is refactored, all imports, references, and paths 
remain valid and consistent throughout the project.

Main Classes:
    - RefactoringVerifier: Verify paths/names after refactoring
    - CodeRefactorer: Core refactoring engine
    - PathResolver: Resolve and update all path references
    - DependencyMapper: Map code dependencies across refactored modules

Usage:
    from code_refractor import RefactoringVerifier, CodeRefactorer
    
    # Verify refactoring won't break things
    verifier = RefactoringVerifier()
    issues = verifier.check_refactoring_safety(old_path, new_path)
    
    # Perform refactoring with automatic path updates
    refactorer = CodeRefactorer()
    refactorer.refactor_with_verification(file_path, changes, project_root)
"""

from code_refractor.refactoring_verifier import RefactoringVerifier
from code_refractor.code_refactorer import CodeRefactorer
from code_refractor.path_resolver import PathResolver
from code_refractor.dependency_mapper import DependencyMapper

__version__ = "0.1.0"
__author__ = "Olga Moreira"

__all__ = [
    "RefactoringVerifier",
    "CodeRefactorer",
    "PathResolver",
    "DependencyMapper",
]
