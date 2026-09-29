"""
pseudocode_renderer.py

Converts pseudo code into real code. Supports two modes:
  - MODE A: Fresh Project (when starterfile.pseudo exists)
  - MODE B: Existing Project (when starterfile.pseudo does not exist)

INPUT: List of script files and their paths
OUTPUT: Converted pseudocode into real code

MODE A (Fresh Project Initialization):
    1. Detect starterfile.pseudo exists
    2. Read PSEUDOCODE headers as authoritative file paths
    3. Seed optional REPOMAP directories and create missing header files
    4. Convert and validate each generated file
    5. Delete starterfile.pseudo only after every conversion succeeds

MODE B (Existing Project Development):
    1. Detect starterfile.pseudo does NOT exist
    2. Scan each file for `pseudocode` inline comments
    3. Call local LLM to convert pseudocode → real code
    4. Print summary
"""

import os
import re
import ast
import stat
import tempfile
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import json

try:  # Support both package and direct-script execution.
    from .blueprint_renderer import create_blueprint, parse_repomap
except ImportError:  # pragma: no cover - used by `python code_starter/pseudocode_renderer.py`
    from blueprint_renderer import create_blueprint, parse_repomap


class PseudocodeRenderer:
    """Main controller for pseudocode to code conversion."""
    
    def __init__(self):
        self.starterfile = 'starterfile.pseudo'
        self.mode = None
        self.converted_files: List[str] = []
        self.warnings: List[str] = []
        self.errors: List[str] = []
    
    def detect_mode(self) -> str:
        """
        Detect which mode to run based on starterfile.pseudo existence.
        
        Returns: 'mode_a' or 'mode_b'
        """
        if os.path.exists(self.starterfile):
            self.mode = 'mode_a'
            print("[pseudocode_renderer] Detected starterfile.pseudo → Running MODE A (Fresh Project)")
            return 'mode_a'
        else:
            self.mode = 'mode_b'
            print("[pseudocode_renderer] starterfile.pseudo not found → Running MODE B (Existing Project)")
            return 'mode_b'
    
    # ==================== MODE A: Fresh Project ====================
    
    def parse_starterfile(self) -> Dict[str, str]:
        """
        Extract file paths and their pseudocode from starterfile.pseudo.
        
        Returns dict: {file_path: pseudocode_content}
        """
        file_pseudocodes = {}
        
        try:
            with open(self.starterfile, 'r') as f:
                content = f.read()
            
            # Extract pseudocode section (after "# PSEUDOCODE").
            pseudo_match = re.search(r'^# PSEUDOCODE\s*$', content, re.MULTILINE)
            if not pseudo_match:
                self.warnings.append("No PSEUDOCODE section found in starterfile.pseudo")
                return file_pseudocodes
            
            pseudo_content = content[pseudo_match.end():]

            # Headers are complete project-relative paths. Capture everything
            # after "## " so names may include hyphens, spaces, and dots.
            current_path = None
            body_lines = []
            for line in pseudo_content.splitlines():
                header = re.match(r'^##\s+(.+?)\s*$', line)
                if header:
                    if current_path is not None:
                        file_pseudocodes[current_path] = '\n'.join(body_lines).strip()
                    current_path = header.group(1).strip()
                    body_lines = []
                elif current_path is not None:
                    body_lines.append(line)
            if current_path is not None:
                file_pseudocodes[current_path] = '\n'.join(body_lines).strip()
            
            return file_pseudocodes
        
        except Exception as e:
            self.errors.append(f"Error parsing starterfile.pseudo: {e}")
            return file_pseudocodes
    
    def verify_mode_a_setup(self, file_pseudocodes: Dict[str, str]) -> Tuple[bool, List[str]]:
        """
        Verify that every PSEUDOCODE header path exists and is empty.
        
        Returns (all_verified: bool, verification_report: List[str])
        """
        report = []
        all_ok = True
        
        for filepath in file_pseudocodes.keys():
            try:
                full_path = self._resolve_project_path(filepath)
            except ValueError as e:
                report.append(f"  ✗ Invalid file path: {filepath} ({e})")
                self.errors.append(str(e))
                all_ok = False
                continue
            
            # Check if file exists
            if not full_path.exists():
                report.append(f"  ✗ File missing: {full_path}")
                self.errors.append(f"File not created: {full_path}")
                all_ok = False
                continue
            
            # Check if file is empty
            try:
                file_size = full_path.stat().st_size
                if file_size > 0:
                    report.append(f"  ✗ File not empty: {full_path} (size: {file_size} bytes)")
                    self.warnings.append(f"File not empty: {full_path} - may already contain code")
                    all_ok = False
                else:
                    report.append(f"  ✓ File verified: {full_path} (empty, ready for conversion)")
            except Exception as e:
                report.append(f"  ✗ Error verifying: {full_path} - {e}")
                self.errors.append(f"Verification error for {full_path}: {e}")
                all_ok = False
        
        return all_ok, report

    @staticmethod
    def _resolve_project_path(filepath: str) -> Path:
        """Resolve a header path and ensure it stays within the working tree."""
        path = Path(filepath)
        if path.is_absolute():
            raise ValueError(f"PSEUDOCODE path must be project-relative: {filepath}")
        root = Path.cwd().resolve()
        resolved = (root / path).resolve()
        try:
            resolved.relative_to(root)
        except ValueError as exc:
            raise ValueError(f"PSEUDOCODE path escapes project root: {filepath}") from exc
        return resolved

    def prepare_mode_a_files(self, file_pseudocodes: Dict[str, str]) -> Tuple[bool, List[str]]:
        """Seed REPOMAP directories, then create missing header-defined files."""
        report = []
        repomap = parse_repomap(self.starterfile)
        # Blueprint creation only seeds directories; REPOMAP file entries have
        # no effect on which files are created.
        success, message = create_blueprint(repomap)
        if not success:
            self.errors.append(message)
            return False, [f"  ✗ {message}"]

        for filepath in file_pseudocodes:
            try:
                full_path = self._resolve_project_path(filepath)
                full_path.parent.mkdir(parents=True, exist_ok=True)
                if full_path.exists():
                    if not full_path.is_file():
                        raise ValueError(f"Header path is not a file: {filepath}")
                    report.append(f"  - Existing file preserved: {filepath}")
                else:
                    full_path.touch()
                    report.append(f"  ✓ Created from PSEUDOCODE header: {filepath}")
            except (OSError, ValueError) as exc:
                self.errors.append(f"Could not prepare {filepath}: {exc}")
                report.append(f"  ✗ Could not prepare {filepath}: {exc}")
                return False, report
        return True, report
    
    def run_mode_a(self) -> bool:
        """
        Execute MODE A: Fresh Project Initialization.
        
        Returns: True if successful, False otherwise
        """
        print("\n" + "="*60)
        print("MODE A: Fresh Project Initialization")
        print("="*60)
        
        # Step 1: Parse starterfile.pseudo
        print("\n[Step 1] Extracting pseudocode from starterfile.pseudo...")
        file_pseudocodes = self.parse_starterfile()
        
        if not file_pseudocodes:
            self.errors.append("No pseudocode definitions found in starterfile.pseudo")
            return False
        
        print(f"  Found {len(file_pseudocodes)} files with pseudocode")
        
        # Step 2: Seed directories and create files using header paths.
        print("\n[Step 2] Preparing project structure from REPOMAP and PSEUDOCODE...")
        prepared, preparation_report = self.prepare_mode_a_files(file_pseudocodes)
        for line in preparation_report:
            print(line)
        if not prepared:
            return False

        # Step 3: Verify header-defined files.
        print("\n[Step 3] Verifying PSEUDOCODE files...")
        verified, report = self.verify_mode_a_setup(file_pseudocodes)
        for line in report:
            print(line)
        
        if not verified:
            print(f"\n✗ Verification failed. Cannot proceed with code generation.")
            return False
        
        # Step 4: Convert pseudocode to real code
        print("\n[Step 4] Converting pseudocode to real code...")
        if not self.convert_pseudocodes(file_pseudocodes):
            self.warnings.append(
                "starterfile.pseudo was kept because one or more files were not generated"
            )
            print("\nGeneration incomplete; starterfile.pseudo has been preserved.")
            return False
        
        # Step 5: Cleanup - Delete starterfile.pseudo
        print("\n[Step 5] Cleanup: Removing starterfile.pseudo...")
        try:
            os.remove(self.starterfile)
            print(f"  ✓ Deleted {self.starterfile}")
        except Exception as e:
            self.warnings.append(f"Failed to delete starterfile.pseudo: {e}")
        
        return True
    
    # ==================== MODE B: Existing Project ====================
    
    def scan_project_files(self) -> List[str]:
        """
        Recursively scan project for Python files containing pseudocode.
        
        Returns: List of file paths with pseudocode
        """
        files_with_pseudo = []
        
        for root, dirs, files in os.walk('.'):
            # Skip common directories
            dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', '.venv', 'venv', '.env']]
            
            for file in files:
                if file.endswith('.py'):
                    filepath = os.path.join(root, file)
                    if self.has_pseudocode(filepath):
                        files_with_pseudo.append(filepath)
        
        return files_with_pseudo
    
    def has_pseudocode(self, filepath: str) -> bool:
        """
        Check if a file contains pseudocode markers (`pseudocode`).
        """
        try:
            with open(filepath, 'r') as f:
                content = f.read()
            return '"""Pseudo Code"""' in content or "'''Pseudo Code'''" in content
        except (OSError, UnicodeError):
            return False
    
    def extract_pseudocode_from_file(self, filepath: str) -> Optional[str]:
        """
        Extract pseudocode from a file's comments.
        
        Looks for patterns like:
        \"\"\"Pseudo Code\"\"\"
        ... pseudocode content ...
        \"\"\"End Pseudo Code\"\"\"
        """
        try:
            with open(filepath, 'r') as f:
                content = f.read()
            
            # Try to extract between markers
            match = re.search(
                r'"""Pseudo Code"""\n(.*?)\n"""End Pseudo Code"""',
                content,
                re.DOTALL
            )
            
            if match:
                return match.group(1).strip()
            
            # Fallback: extract everything after the marker until a blank line or next section
            match = re.search(r'"""Pseudo Code"""\n(.*?)(?:\n\n|$)', content, re.DOTALL)
            if match:
                return match.group(1).strip()
            
            return None
        
        except Exception as e:
            self.errors.append(f"Error extracting pseudocode from {filepath}: {e}")
            return None
    
    def run_mode_b(self) -> bool:
        """
        Execute MODE B: Existing Project Development.
        
        Returns: True if successful, False otherwise
        """
        print("\n" + "="*60)
        print("MODE B: Existing Project Development")
        print("="*60)
        
        # Step 1: Scan for files with pseudocode
        print("\n[Step 1] Scanning project for pseudocode comments...")
        files_with_pseudo = self.scan_project_files()
        
        if not files_with_pseudo:
            print("  No files with pseudocode found")
            self.warnings.append("No Python files with pseudocode markers found in project")
            return True  # Not an error, just nothing to do
        
        print(f"  Found {len(files_with_pseudo)} files with pseudocode")
        for fp in files_with_pseudo:
            print(f"    - {fp}")
        
        # Step 2: Extract and convert pseudocode
        print("\n[Step 2] Extracting and converting pseudocode...")
        pseudo_dict = {}
        for filepath in files_with_pseudo:
            pseudo = self.extract_pseudocode_from_file(filepath)
            if pseudo:
                pseudo_dict[filepath] = pseudo
            else:
                self.warnings.append(f"Could not extract pseudocode from {filepath}")
        
        if pseudo_dict:
            return self.convert_pseudocodes(pseudo_dict)
        return True
    
    # ==================== Shared: Code Conversion ====================
    
    def convert_pseudocodes(self, pseudocodes: Dict[str, str]) -> bool:
        """
        Convert pseudocode to real code using local LLM.
        
        Args:
            pseudocodes: Dict mapping file_path -> pseudocode_content
        """
        successful = True
        for filepath, pseudocode in pseudocodes.items():
            print(f"\n  Converting: {filepath}")
            
            if not pseudocode.strip():
                self.warnings.append(f"Empty pseudocode for {filepath}")
                successful = False
                continue
            
            # Call LLM to convert pseudocode
            real_code = self.call_llm_for_conversion(pseudocode, filepath)
            
            if real_code:
                try:
                    target = self._resolve_project_path(filepath)
                    clean_code = self._validate_generated_code(real_code, target)
                    self._atomic_write(target, clean_code)
                    self.converted_files.append(filepath)
                    print(f"    ✓ Converted and saved")
                except (OSError, SyntaxError, ValueError) as e:
                    self.errors.append(f"Failed to write converted code to {filepath}: {e}")
                    print(f"    ✗ Failed to save: {e}")
                    successful = False
            else:
                self.errors.append(f"LLM conversion failed for {filepath}")
                print(f"    ✗ LLM conversion failed")
                successful = False
        return successful

    @staticmethod
    def _validate_generated_code(code: str, target: Path) -> str:
        """Strip common Markdown fences and validate Python before writing."""
        code = code.strip()
        fenced = re.fullmatch(r"```(?:[\w+-]+)?\s*\n(.*?)\n```", code, re.DOTALL)
        if fenced:
            code = fenced.group(1).rstrip() + "\n"
        if target.suffix.lower() in {".py", ".pyi"}:
            ast.parse(code, filename=str(target))
        if not code.strip():
            raise ValueError("generated output is empty")
        return code if code.endswith("\n") else code + "\n"

    @staticmethod
    def _atomic_write(target: Path, content: str) -> None:
        """Replace a generated file atomically, preserving existing permissions."""
        target.parent.mkdir(parents=True, exist_ok=True)
        existing_mode = stat.S_IMODE(target.stat().st_mode) if target.exists() else 0o644
        temporary_path = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w", encoding="utf-8", dir=str(target.parent),
                prefix=f".{target.name}.", suffix=".tmp", delete=False
            ) as temporary:
                temporary_path = Path(temporary.name)
                temporary.write(content)
                temporary.flush()
                os.fsync(temporary.fileno())
            temporary_path.chmod(existing_mode)
            os.replace(str(temporary_path), str(target))
        finally:
            if temporary_path is not None and temporary_path.exists():
                temporary_path.unlink()
    
    def call_llm_for_conversion(self, pseudocode: str, filepath: str) -> Optional[str]:
        """
        Call local LLM (deepseek-coder:6.7b) to convert pseudocode to real code.
        
        Args:
            pseudocode: The pseudocode to convert
            filepath: The target file path (for context)
        
        Returns: Generated code or None if failed
        """
        try:
            import subprocess
            
            # Build prompt for LLM
            prompt = self._build_conversion_prompt(pseudocode, filepath)
            
            # Call local LLM via ollama or similar
            # Note: This is a placeholder - adjust based on your LLM setup
            result = subprocess.run(
                ['ollama', 'run', 'deepseek-coder:6.7b'],
                input=prompt,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                self.errors.append(f"LLM error: {result.stderr}")
                return None
        
        except FileNotFoundError:
            # Ollama not installed/not in PATH
            print("    ⚠ Warning: ollama not available, skipping LLM conversion")
            print("    Please ensure 'deepseek-coder:6.7b' is available via ollama")
            return None
        except Exception as e:
            self.errors.append(f"Exception calling LLM: {e}")
            return None
    
    def _build_conversion_prompt(self, pseudocode: str, filepath: str) -> str:
        """
        Build a prompt for the LLM to convert pseudocode to real code.
        """
        file_ext = os.path.splitext(filepath)[1]
        lang = self._detect_language(file_ext)
        
        prompt = f"""Convert the following pseudocode into production-ready {lang} code.
File: {filepath}
Language: {lang}

Pseudocode:
{pseudocode}

Requirements:
- Write clean, idiomatic {lang} code
- Include proper error handling
- Add docstrings/comments where appropriate
- Follow {lang} best practices
- Do not include pseudocode markers in the output
- Return only the complete, runnable code

Generated Code:"""
        
        return prompt
    
    def _detect_language(self, file_ext: str) -> str:
        """Detect programming language from file extension."""
        lang_map = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.ts': 'TypeScript',
            '.java': 'Java',
            '.cpp': 'C++',
            '.c': 'C',
            '.cs': 'C#',
            '.go': 'Go',
            '.rs': 'Rust',
        }
        return lang_map.get(file_ext, 'Python')
    
    # ==================== Reporting ====================
    
    def print_summary(self) -> None:
        """Print conversion summary and any warnings/errors."""
        print("\n" + "="*60)
        print("CONVERSION SUMMARY")
        print("="*60)
        
        if self.converted_files:
            print(f"\n✓ Successfully converted {len(self.converted_files)} file(s):")
            for f in self.converted_files:
                print(f"  - {f}")
        else:
            print("\nNo files were converted")
        
        if self.warnings:
            print(f"\n⚠ Warnings ({len(self.warnings)}):")
            for w in self.warnings:
                print(f"  - {w}")
        
        if self.errors:
            print(f"\n✗ Errors ({len(self.errors)}):")
            for e in self.errors:
                print(f"  - {e}")
        
        print("\n" + "="*60)
    
    # ==================== Main Entry Point ====================
    
    def run(self) -> bool:
        """Main execution method."""
        mode = self.detect_mode()
        
        if mode == 'mode_a':
            success = self.run_mode_a()
        else:
            success = self.run_mode_b()
        
        self.print_summary()
        return success


def main():
    """Entry point for pseudocode renderer."""
    renderer = PseudocodeRenderer()
    success = renderer.run()
    return "success" if success else "fail"


if __name__ == '__main__':
    result = main()
    print(f"\n[Result]: {result}")
