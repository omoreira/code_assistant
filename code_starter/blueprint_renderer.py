"""
blueprint_renderer.py

Scans the starterfile.pseudo and creates the directory tree and placeholder files
defined in the REPOMAP section.

INPUT: starterfile.pseudo
OUTPUT: "success" or "fail"

TASK:
    1. Parse starterfile.pseudo to extract REPOMAP
    2. Create directories as defined in REPOMAP
    3. Create empty placeholder files
    4. Skip creation if directories/files already exist (do not overwrite)
    5. Return status message
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Tuple


def parse_repomap(filepath: str) -> Dict[str, List[str]]:
    """
    Parse starterfile.pseudo to extract REPOMAP section.
    Handles tree-style directory structure.
    
    Returns dict with structure:
    {
        'directories': ['./code_assistant', './code_assistant/code_starter', ...],
        'files': ['./code_assistant/blueprint_renderer.py', ...]
    }
    """
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        
        # Extract REPOMAP section (between # REPOMAP and # PSEUDOCODE)
        repomap_match = re.search(r'# REPOMAP\n(.*?)(?=\n# PSEUDOCODE|\Z)', content, re.DOTALL)
        if not repomap_match:
            return None
        
        repomap_content = repomap_match.group(1)
        
        directories = []
        files = []
        current_dir_stack = []  # Track directory nesting level
        
        for line in repomap_content.split('\n'):
            if not line.strip() or line.startswith('#'):
                continue
            
            # Calculate indentation level (groups of 4+ spaces or tabs)
            indent_level = (len(line) - len(line.lstrip())) // 4
            clean_line = line.strip()
            
            if not clean_line:
                continue
            
            # Remove tree characters (|, _, -)
            clean_line = re.sub(r'^[|\-_\s]+', '', clean_line).strip()
            
            # Extract directory or file name (remove trailing comments)
            item_name = re.split(r'\s*\(', clean_line)[0].strip()
            
            if not item_name:
                continue
            
            # Adjust directory stack based on indentation
            while len(current_dir_stack) > indent_level:
                current_dir_stack.pop()
            
            # Determine if it's a directory or file
            if item_name.endswith('/'):
                # It's a directory
                dir_name = item_name[:-1]  # Remove trailing /
                
                # Build full path
                if current_dir_stack:
                    full_path = '/'.join(current_dir_stack) + '/' + dir_name
                else:
                    full_path = dir_name
                
                # Add to directories if not already there
                if full_path not in directories:
                    directories.append(full_path)
                
                # Update stack for next items
                current_dir_stack.append(dir_name)
            
            elif item_name.endswith('.py'):
                # It's a file
                # Build full path
                if current_dir_stack:
                    full_path = '/'.join(current_dir_stack) + '/' + item_name
                else:
                    full_path = item_name
                
                files.append(full_path)
        
        return {
            'directories': sorted(set(directories)),  # Remove duplicates and sort
            'files': sorted(set(files))
        }
    
    except Exception as e:
        print(f"Error parsing REPOMAP: {e}")
        return None


def create_blueprint(repomap: Dict[str, List[str]]) -> Tuple[bool, str]:
    """
    Create directories and placeholder files from REPOMAP.
    
    Returns (success: bool, message: str)
    """
    if not repomap or 'directories' not in repomap:
        return False, "Invalid REPOMAP structure"
    
    created_dirs = []
    skipped_dirs = []
    created_files = []
    skipped_files = []
    
    # Create directories
    for dir_path in repomap['directories']:
        try:
            if not os.path.exists(dir_path):
                os.makedirs(dir_path, exist_ok=True)
                created_dirs.append(dir_path)
            else:
                skipped_dirs.append(dir_path)
        except Exception as e:
            return False, f"Failed to create directory {dir_path}: {e}"
    
    # Create empty placeholder files
    for file_path in repomap['files']:
        try:
            if not os.path.exists(file_path):
                # Ensure parent directory exists
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                # Create empty file
                Path(file_path).touch()
                created_files.append(file_path)
            else:
                skipped_files.append(file_path)
        except Exception as e:
            return False, f"Failed to create file {file_path}: {e}"
    
    # Generate success message
    message = f"""
Blueprint creation completed successfully!

Created Directories ({len(created_dirs)}):
{chr(10).join(f'  ✓ {d}' for d in created_dirs) if created_dirs else '  (none)'}

Skipped Directories ({len(skipped_dirs)}):
{chr(10).join(f'  - {d}' for d in skipped_dirs) if skipped_dirs else '  (none)'}

Created Files ({len(created_files)}):
{chr(10).join(f'  ✓ {f}' for f in created_files) if created_files else '  (none)'}

Skipped Files ({len(skipped_files)}):
{chr(10).join(f'  - {f}' for f in skipped_files) if skipped_files else '  (none)'}
"""
    
    return True, message


def main():
    """
    Main entry point for blueprint renderer.
    """
    starterfile = 'starterfile.pseudo'
    
    print(f"[blueprint_renderer] Reading {starterfile}...")
    
    if not os.path.exists(starterfile):
        print(f"FAIL: {starterfile} not found")
        return "fail"
    
    # Parse REPOMAP
    repomap = parse_repomap(starterfile)
    if not repomap:
        print("FAIL: Could not parse REPOMAP")
        return "fail"
    
    print(f"Found {len(repomap['directories'])} directories and {len(repomap['files'])} files to create")
    
    # Create blueprint
    success, message = create_blueprint(repomap)
    print(message)
    
    return "success" if success else "fail"


if __name__ == '__main__':
    result = main()
    print(f"\n[Result]: {result}")
