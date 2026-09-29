"""
starterfile_creator.py

Interactive tool to create starterfile.pseudo with REPOMAP and PSEUDOCODE sections.

Features:
- Build directory tree interactively
- Create pseudocode definitions for each file
- Validate structure
- Preview formatted output
- Save to starterfile.pseudo
"""

import os
import json
import re
from typing import Dict, List, Optional, Tuple
from collections import OrderedDict

try:
    from .blueprint_renderer import parse_repomap
except ImportError:  # Support direct-script execution.
    from blueprint_renderer import parse_repomap


class StarterfileCreator:
    """Interactive builder for starterfile.pseudo"""
    
    def __init__(self):
        self.root_dir = None
        self.tree_structure = OrderedDict()  # {path: {'type': 'dir'|'file', 'children': [], ...}}
        self.pseudocodes = {}  # {filepath: {'input': '', 'output': '', 'task': '', ...}}
        self.current_path = []  # Track current position in tree
    
    def main_menu(self):
        """Display main menu."""
        while True:
            print("\n" + "="*60)
            print("STARTERFILE CREATOR - Main Menu")
            print("="*60)
            print("1. Create new project structure")
            print("2. View current structure")
            print("3. Add/Edit pseudocode for files")
            print("4. Preview starterfile.pseudo")
            print("5. Save to starterfile.pseudo")
            print("6. Load existing starterfile.pseudo")
            print("7. Clear all")
            print("8. Exit")
            print("-"*60)
            
            choice = input("Select option (1-8): ").strip()
            
            if choice == '1':
                self.create_project_structure()
            elif choice == '2':
                self.view_structure()
            elif choice == '3':
                self.manage_pseudocodes()
            elif choice == '4':
                self.preview_output()
            elif choice == '5':
                self.save_to_file()
            elif choice == '6':
                self.load_from_file()
            elif choice == '7':
                self.clear_all()
            elif choice == '8':
                print("\nGoodbye!")
                break
            else:
                print("Invalid option. Try again.")
    
    # ==================== PROJECT STRUCTURE ====================
    
    def create_project_structure(self):
        """Interactively build project directory structure."""
        print("\n" + "="*60)
        print("CREATE PROJECT STRUCTURE")
        print("="*60)
        
        # Get root directory
        while True:
            root = input("\nEnter root directory (e.g., ./my_project): ").strip()
            if root:
                self.root_dir = root
                self.tree_structure = {root: {'type': 'dir', 'children': []}}
                print(f"Root directory set: {root}")
                break
        
        # Build tree
        self.build_tree_interactive(root)
    
    def build_tree_interactive(self, parent_path: str, level: int = 0):
        """Interactively add items to tree."""
        while True:
            print(f"\n[{parent_path}]")
            print("1. Add directory")
            print("2. Add file")
            print("3. Go to parent")
            print("4. Done")
            
            choice = input("Select (1-4): ").strip()
            
            if choice == '1':
                dir_name = input("Directory name: ").strip()
                if dir_name:
                    self.add_directory(parent_path, dir_name)
                    new_path = f"{parent_path}/{dir_name}"
                    # Ask if user wants to add items inside
                    if input(f"Add items to {new_path}? (y/n): ").strip().lower() == 'y':
                        self.build_tree_interactive(new_path, level + 1)
            
            elif choice == '2':
                filename = input("Filename (with extension): ").strip()
                if filename:
                    self.add_file(parent_path, filename)
            
            elif choice == '3':
                if level > 0:
                    break
                else:
                    print("Cannot go above root")
            
            elif choice == '4':
                break
            
            else:
                print("Invalid option")
    
    def add_directory(self, parent: str, dir_name: str):
        """Add directory to tree."""
        if parent not in self.tree_structure:
            self.tree_structure[parent] = {'type': 'dir', 'children': []}
        
        new_path = f"{parent}/{dir_name}"
        self.tree_structure[parent]['children'].append(new_path)
        self.tree_structure[new_path] = {'type': 'dir', 'children': []}
        print(f"✓ Added directory: {new_path}")
    
    def add_file(self, parent: str, filename: str):
        """Add file to tree."""
        if parent not in self.tree_structure:
            self.tree_structure[parent] = {'type': 'dir', 'children': []}
        
        new_path = f"{parent}/{filename}"
        self.tree_structure[parent]['children'].append(new_path)
        self.tree_structure[new_path] = {'type': 'file'}
        print(f"✓ Added file: {new_path}")
    
    def view_structure(self):
        """Display the current tree structure."""
        print("\n" + "="*60)
        print("CURRENT STRUCTURE")
        print("="*60)
        
        if not self.root_dir:
            print("No structure created yet")
            return
        
        self._print_tree(self.root_dir, "", is_last=True)
    
    def _print_tree(self, node: str, prefix: str = "", is_last: bool = True):
        """Recursively print tree structure."""
        if node not in self.tree_structure:
            return
        
        # Print current node
        connector = "└── " if is_last else "├── "
        node_name = node.split('/')[-1]
        node_type = self.tree_structure[node].get('type', 'unknown')
        
        if node == self.root_dir:
            print(node)
        else:
            print(prefix + connector + node_name + ("/" if node_type == 'dir' else ""))
        
        # Print children
        children = self.tree_structure[node].get('children', [])
        for i, child in enumerate(children):
            is_last_child = (i == len(children) - 1)
            extension = "    " if is_last else "│   "
            self._print_tree(child, prefix + extension, is_last_child)
    
    # ==================== PSEUDOCODE MANAGEMENT ====================
    
    def manage_pseudocodes(self):
        """Manage pseudocode definitions for files."""
        print("\n" + "="*60)
        print("MANAGE PSEUDOCODE")
        print("="*60)
        
        # Get list of files
        files = self.get_all_files()
        
        if not files:
            print("No files in project structure")
            return
        
        print("\nFiles in project:")
        for i, filepath in enumerate(files, 1):
            status = "✓" if filepath in self.pseudocodes else " "
            print(f"  {i}. [{status}] {filepath}")
        
        while True:
            choice = input("\nSelect file number (or 'done' to return): ").strip()
            
            if choice.lower() == 'done':
                break
            
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(files):
                    filepath = files[idx]
                    self.edit_pseudocode(filepath)
                else:
                    print("Invalid selection")
            except ValueError:
                print("Invalid input")
    
    def edit_pseudocode(self, filepath: str):
        """Edit pseudocode for a specific file."""
        print(f"\n{'='*60}")
        print(f"EDIT PSEUDOCODE: {filepath}")
        print(f"{'='*60}")
        
        # Load existing pseudocode if any
        existing = self.pseudocodes.get(filepath, {})
        
        fields = ['input', 'output', 'task', 'conditions', 'preferences']
        
        for field in fields:
            print(f"\n[{field.upper()}]")
            if existing.get(field):
                print(f"Current: {existing[field][:50]}...")
                keep = input("Keep current? (y/n): ").strip().lower()
                if keep == 'y':
                    continue
            
            print(f"Enter {field} (multi-line, type 'END' on new line to finish):")
            lines = []
            while True:
                line = input()
                if line.strip() == 'END':
                    break
                lines.append(line)
            
            value = '\n'.join(lines).strip()
            
            if not self.pseudocodes.get(filepath):
                self.pseudocodes[filepath] = {}
            
            self.pseudocodes[filepath][field] = value
        
        print(f"\n✓ Pseudocode saved for {filepath}")
    
    def get_all_files(self) -> List[str]:
        """Get list of all files in the tree."""
        files = []
        
        for path, node in self.tree_structure.items():
            if node.get('type') == 'file':
                files.append(path)
        
        return sorted(files)
    
    # ==================== OUTPUT & PREVIEW ====================
    
    def preview_output(self):
        """Preview the formatted starterfile.pseudo."""
        print("\n" + "="*60)
        print("PREVIEW STARTERFILE.PSEUDO")
        print("="*60)
        
        content = self.generate_content()
        print("\n" + content)
        
        input("\nPress Enter to continue...")
    
    def generate_content(self) -> str:
        """Generate the complete starterfile.pseudo content."""
        lines = []
        
        # REPOMAP section
        lines.append("# REPOMAP\n")
        if self.root_dir:
            lines.append(self.root_dir)
            self._generate_repomap(self.root_dir, "", lines, is_last=True)
        
        lines.append("\n\n")
        
        # PSEUDOCODE section
        lines.append("# PSEUDOCODE\n")
        files = self.get_all_files()
        
        for filepath in files:
            lines.append(f"\n## {filepath}\n")
            
            pseudo = self.pseudocodes.get(filepath, {})
            
            for field in ['input', 'output', 'task', 'conditions', 'preferences']:
                if pseudo.get(field):
                    lines.append(f"{field.upper()}: {pseudo[field]}")
                    lines.append("")
        
        return '\n'.join(lines)
    
    def _generate_repomap(self, node: str, prefix: str, lines: List[str], is_last: bool):
        """Recursively generate REPOMAP tree."""
        children = self.tree_structure.get(node, {}).get('children', [])
        
        for i, child in enumerate(children):
            is_last_child = (i == len(children) - 1)
            node_type = self.tree_structure[child].get('type', 'unknown')
            child_name = child.split('/')[-1]
            
            # Build tree characters
            if is_last_child:
                tree_chars = "        |______ "
                extension = "                        "
            else:
                tree_chars = "        |______ "
                extension = "        |               "
            
            # Add node type indicator
            if node_type == 'dir':
                child_name += "/"
            
            lines.append(f"{tree_chars}{child_name}")
            
            # Recursively add children
            sub_children = self.tree_structure.get(child, {}).get('children', [])
            if sub_children:
                # Adjust prefix for tree visualization
                new_prefix = extension if not is_last_child else "                        "
                self._generate_repomap(child, new_prefix, lines, is_last_child)
    
    # ==================== FILE I/O ====================
    
    def save_to_file(self):
        """Save to starterfile.pseudo."""
        if not self.root_dir:
            print("Cannot save: No project structure created")
            return
        
        filename = input("\nFilename (default: starterfile.pseudo): ").strip()
        if not filename:
            filename = "starterfile.pseudo"
        
        content = self.generate_content()
        
        try:
            with open(filename, 'w') as f:
                f.write(content)
            print(f"✓ Saved to {filename}")
        except Exception as e:
            print(f"✗ Error saving: {e}")
    
    def load_from_file(self):
        """Load a starterfile and rebuild the editable tree and pseudocode."""
        filename = input("\nFilename to load: ").strip()
        
        if not os.path.exists(filename):
            print(f"File not found: {filename}")
            return
        
        try:
            with open(filename, 'r', encoding='utf-8') as starter:
                content = starter.read()

            pseudo_match = re.search(
                r'^# PSEUDOCODE\s*$', content, flags=re.MULTILINE
            )
            if not pseudo_match:
                print("Invalid starterfile: # PSEUDOCODE section is missing")
                return

            repomap_match = re.search(
                r'^# REPOMAP\s*$(.*?)(?=^# PSEUDOCODE\s*$|\Z)',
                content, flags=re.MULTILINE | re.DOTALL
            )
            repomap_lines = repomap_match.group(1).splitlines() if repomap_match else []
            root = None
            for line in repomap_lines:
                clean = re.sub(r'^[|\-+`_\s]+', '', line).strip()
                clean = re.split(r'\s*\(', clean, maxsplit=1)[0].strip().rstrip('/')
                if clean:
                    root = clean
                    break

            sections = {}
            current_path = None
            body = []
            for line in content[pseudo_match.end():].splitlines():
                header = re.match(r'^##\s+(.+?)\s*$', line)
                if header:
                    if current_path is not None:
                        sections[current_path] = '\n'.join(body).strip()
                    current_path = header.group(1).strip()
                    body = []
                elif current_path is not None:
                    body.append(line)
            if current_path is not None:
                sections[current_path] = '\n'.join(body).strip()

            if not sections:
                print("Invalid starterfile: no PSEUDOCODE file headers found")
                return

            # Infer a usable root if the REPOMAP has no root entry.
            if not root:
                parents = [os.path.dirname(os.path.normpath(path)) for path in sections]
                root = os.path.commonpath(parents) or "."
            root = os.path.normpath(root)

            tree = OrderedDict([(root, {'type': 'dir', 'children': []})])

            def add_directory(directory_path):
                normalized_dir = os.path.normpath(directory_path)
                relative_dir = os.path.relpath(normalized_dir, root)
                if relative_dir == os.pardir or relative_dir.startswith(os.pardir + os.sep):
                    raise ValueError(
                        f"Directory path is outside the declared root: {directory_path}"
                    )
                parent = root
                if relative_dir == ".":
                    return
                for part in relative_dir.split(os.sep):
                    child = os.path.join(parent, part)
                    tree.setdefault(child, {'type': 'dir', 'children': []})
                    if child not in tree[parent]['children']:
                        tree[parent]['children'].append(child)
                    parent = child

            parsed_repomap = parse_repomap(filename) or {'directories': []}
            for directory in parsed_repomap.get('directories', []):
                add_directory(directory)

            pseudocodes = {}
            field_labels = {
                'INPUT': 'input', 'OUTPUT': 'output', 'TASK': 'task',
                'TASKS GOAL': 'task', 'CONDITIONS': 'conditions',
                'PREFERENCES': 'preferences',
            }
            for file_path, body_text in sections.items():
                normalized = os.path.normpath(file_path)
                try:
                    relative = os.path.relpath(normalized, root)
                    if relative == os.pardir or relative.startswith(os.pardir + os.sep):
                        raise ValueError(f"File path is outside the declared root: {file_path}")
                except ValueError:
                    raise ValueError(f"Could not place {file_path} under {root}")

                parts = relative.split(os.sep)
                directory = os.path.join(root, *parts[:-1]) if len(parts) > 1 else root
                add_directory(directory)
                full_file = os.path.join(directory, parts[-1])
                if full_file not in tree[directory]['children']:
                    tree[directory]['children'].append(full_file)
                tree[full_file] = {'type': 'file'}

                fields = {}
                active_field = 'task'
                field_lines = {active_field: []}
                for body_line in body_text.splitlines():
                    label = re.match(r'^([A-Z][A-Z ]*):\s*(.*)$', body_line)
                    normalized_label = ' '.join(label.group(1).split()) if label else None
                    if label and normalized_label in field_labels:
                        active_field = field_labels[normalized_label]
                        field_lines.setdefault(active_field, [])
                        if label.group(2):
                            field_lines[active_field].append(label.group(2))
                    else:
                        field_lines.setdefault(active_field, []).append(body_line)
                for name, lines in field_lines.items():
                    fields[name] = '\n'.join(lines).strip()
                pseudocodes[full_file] = fields

            self.root_dir = root
            self.tree_structure = tree
            self.pseudocodes = pseudocodes
            print(f"✓ Loaded {len(pseudocodes)} file specifications from {filename}")
        except (OSError, ValueError) as e:
            print(f"✗ Error loading {filename}: {e}")
    
    def clear_all(self):
        """Clear all data."""
        if input("Clear all data? (y/n): ").strip().lower() == 'y':
            self.root_dir = None
            self.tree_structure = OrderedDict()
            self.pseudocodes = {}
            print("✓ All data cleared")


# Preserve the public spelling used by code_starter.__init__ and the docs.
StarterFileCreator = StarterfileCreator


def main():
    """Entry point."""
    print("\n" + "="*60)
    print("STARTERFILE CREATOR")
    print("Create starterfile.pseudo for code_starter projects")
    print("="*60)
    
    creator = StarterfileCreator()
    creator.main_menu()


if __name__ == '__main__':
    main()
