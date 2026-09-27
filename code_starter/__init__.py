"""code_starter - Project Creation and Code Generation Module

Interactive tools for starting new projects with intelligent code generation.

Key components:
- StarterFileCreator: Interactive project specification builder
- BlueprintRenderer: Directory structure generator
- PseudocodeRenderer: Convert pseudocode to Python code
- GitHubRepoPlanner: Automate GitHub repository setup

Example usage:
    from code_starter import StarterFileCreator
    
    creator = StarterFileCreator()
    creator.run_interactive()

See docs/code_starter/README.md for detailed documentation.
"""

from .starterfile_creator import StarterFileCreator
from .blueprint_renderer import BlueprintRenderer
from .pseudocode_renderer import PseudocodeRenderer
from .github_repo_planner import GitHubRepoPlanner

__version__ = "0.1.0"
__author__ = "Olga Moreira"

__all__ = [
    "StarterFileCreator",
    "BlueprintRenderer",
    "PseudocodeRenderer",
    "GitHubRepoPlanner",
]
