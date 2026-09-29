"""
blueprint_renderer.py

Scans the starterfile.pseudo and creates empty directories defined in REPOMAP.

INPUT: starterfile.pseudo
OUTPUT: "success" or "fail"

TASK:
    1. Parse starterfile.pseudo to extract REPOMAP
    2. Create directories as defined in REPOMAP
    3. Ignore file entries and tree glyphs
    4. Return status message
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
        'files': []  # retained for backwards compatibility
    }
    """
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        
        # Extract REPOMAP section (between # REPOMAP and # PSEUDOCODE)
        repomap_match = re.search(r'# REPOMAP\n(.*?)(?=\n# PSEUDOCODE|\Z)', content, re.DOTALL)
        if not repomap_match:
            return {'directories': [], 'files': []}
        
        repomap_content = repomap_match.group(1)
        
        directories = []
        current_dir_stack = []  # Track directory nesting level
        
        for line in repomap_content.split('\n'):
            if not line.strip() or line.startswith('#'):
                continue
            
            # Calculate indentation level (groups of 4+ spaces or tabs)
            indent_level = (len(line) - len(line.lstrip())) // 4
            clean_line = line.strip()
            
            if not clean_line:
                continue
            
            # Ignore the tree connector glyphs. Only the entry text and its
            # indentation determine the directory hierarchy.
            clean_line = re.sub(r'^[|\-+`_\s]+', '', clean_line).strip()
            
            # Extract directory or file name (remove trailing comments)
            item_name = re.split(r'\s*\(', clean_line)[0].strip()
            
            if not item_name:
                continue
            
            # Adjust directory stack based on indentation
            while len(current_dir_stack) > indent_level:
                current_dir_stack.pop()
            
            # REPOMAP seeds directories only. Entries with file extensions are
            # ignored; names and connector glyphs never create files.
            if not item_name.endswith('/') and Path(item_name).suffix:
                continue

            dir_name = item_name.rstrip('/')
            full_path = (
                '/'.join(current_dir_stack) + '/' + dir_name
                if current_dir_stack else dir_name
            )
            if full_path not in directories:
                directories.append(full_path)
            current_dir_stack.append(dir_name)
        
        return {
            'directories': sorted(set(directories)),  # Remove duplicates and sort
            'files': []
        }
    
    except Exception as e:
        print(f"Error parsing REPOMAP: {e}")
        return None


def create_blueprint(repomap: Dict[str, List[str]]) -> Tuple[bool, str]:
    """
    Create directories from REPOMAP. REPOMAP file entries are ignored.
    
    Returns (success: bool, message: str)
    """
    if not repomap or 'directories' not in repomap:
        return False, "Invalid REPOMAP structure"
    
    created_dirs = []
    skipped_dirs = []
    project_root = Path.cwd().resolve()
    
    # Create directories
    for dir_path in repomap['directories']:
        try:
            full_path = (project_root / dir_path).resolve()
            full_path.relative_to(project_root)
            if not full_path.exists():
                full_path.mkdir(parents=True, exist_ok=True)
                created_dirs.append(dir_path)
            else:
                skipped_dirs.append(dir_path)
        except Exception as e:
            return False, f"Failed to create directory {dir_path}: {e}"
    
    # Generate success message
    message = f"""
Blueprint creation completed successfully!

Created Directories ({len(created_dirs)}):
{chr(10).join(f'  ✓ {d}' for d in created_dirs) if created_dirs else '  (none)'}

Skipped Directories ({len(skipped_dirs)}):
{chr(10).join(f'  - {d}' for d in skipped_dirs) if skipped_dirs else '  (none)'}

REPOMAP file entries: ignored (PSEUDOCODE headers define files)
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
    
    print(f"Found {len(repomap['directories'])} directories to create")
    
    # Create blueprint
    success, message = create_blueprint(repomap)
    print(message)
    
    return "success" if success else "fail"


if __name__ == '__main__':
    result = main()
    print(f"\n[Result]: {result}")
