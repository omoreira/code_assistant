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
import shutil
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import json
import argparse

try:  # Support both package and direct-script execution.
    from .blueprint_renderer import create_blueprint, parse_repomap
except ImportError:  # pragma: no cover - used by `python code_starter/pseudocode_renderer.py`
    from blueprint_renderer import create_blueprint, parse_repomap

try:
    from shared.llm_config import resolve_llm
except ImportError:  # pragma: no cover - direct execution without PYTHONPATH=src

    def resolve_llm(role: str = "generation", **kwargs):  # type: ignore
        """Minimal fallback mirroring shared.llm_config built-in defaults."""
        from types import SimpleNamespace

        return SimpleNamespace(
            model="deepseek-coder:6.7b",
            base_url="http://localhost:11434",
            timeout=600,
        )


try:
    from shared.paths_config import (
        data_dir_is_explicit,
        data_dir_source,
        resolve_data_dir,
    )
except ImportError:  # pragma: no cover - direct execution without PYTHONPATH=src

    def resolve_data_dir(override: Optional[str] = None, **kwargs) -> str:  # type: ignore
        """Minimal fallback mirroring shared.constants.DEFAULT_DATA_DIR."""
        return override or "data"

    def data_dir_source(override: Optional[str] = None, **kwargs) -> str:  # type: ignore
        return "override" if override else "builtin"

    def data_dir_is_explicit(source: str) -> bool:  # type: ignore
        return source in ("override", "env", "starterfile")


try:
    from .starterfile_paths import parse_paths
except ImportError:  # pragma: no cover - direct script execution
    from starterfile_paths import parse_paths


# Bodies that mean "no items in this section".
_NONE_TOKENS = {"", "NONE", "EMPTY"}


def _extract_section_body(content: str, name: str) -> Optional[str]:
    """Return the body of a top-level ``# NAME`` section, or ``None``."""
    match = re.search(
        r'^#\s*' + re.escape(name) + r'\s*$(.*?)(?=^#\s+\w|\Z)',
        content, flags=re.MULTILINE | re.DOTALL | re.IGNORECASE,
    )
    return match.group(1).strip() if match else None


def is_none_section(body: Optional[str]) -> bool:
    """True when a section body means "no items" (blank/``NONE``/``empty``)."""
    return body is not None and body.strip().upper() in _NONE_TOKENS


def archive_starterfile(
    starterfile: str,
    project_root: Optional[str] = None,
    tmp_dir: Optional[str] = None,
) -> Optional[Path]:
    """Move a starterfile into ``tmp/`` with a timestamp; return the new path."""
    source = Path(starterfile)
    if not source.exists():
        return None
    if tmp_dir is not None:
        destination_dir = Path(tmp_dir).expanduser()
    else:
        if project_root:
            base = Path(project_root).expanduser()
        else:
            base = source.resolve().parent
        destination_dir = base / "tmp"
    destination_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    destination = destination_dir / "{}.{}".format(source.name, stamp)
    shutil.move(str(source), str(destination))
    return destination


class PseudocodeRenderer:
    """Main controller for pseudocode to code conversion."""
    
    def __init__(
        self,
        starterfile: str = 'starterfile.pseudo',
        project_root: Optional[str] = None,
        data_dir: Optional[str] = None,
        interactive: bool = False,
        archive: bool = True,
    ):
        self.starterfile = str(Path(starterfile).expanduser())
        self.project_root = Path(project_root).expanduser().resolve() if project_root else None
        self._project_root_explicit = project_root is not None
        # Parse the optional # PATHS section for the project-level data dir.
        self.paths = parse_paths(self.starterfile) or {}
        self._explicit_data_dir = data_dir
        # Resolve the data-storage folder (CLI override -> env -> # PATHS ->
        # config -> built-in) so a user-set default flows through.
        self.data_dir = resolve_data_dir(
            override=data_dir, project_value=self.paths.get("data_dir")
        )
        self.interactive = interactive
        self.archive = archive
        self.mode = None
        self.converted_files: List[str] = []
        self.created_databases: List[Path] = []
        self.warnings: List[str] = []
        self.errors: List[str] = []
    
    def detect_mode(self) -> str:
        """
        Detect which mode to run based on starterfile.pseudo existence.
        
        Returns: 'mode_a' or 'mode_b'
        """
        if Path(self.starterfile).is_file():
            if not self._project_root_explicit:
                self.project_root = self._root_from_starterfile()
            self.mode = 'mode_a'
            print("[pseudocode_renderer] Detected starterfile.pseudo → Running MODE A (Fresh Project)")
            return 'mode_a'
        else:
            if self.project_root is None:
                self.project_root = Path.cwd().resolve()
            self.mode = 'mode_b'
            print("[pseudocode_renderer] starterfile.pseudo not found → Running MODE B (Existing Project)")
            return 'mode_b'

    def _root_from_starterfile(self) -> Path:
        """Resolve root metadata from ``# PATHS`` (or legacy ``# PROJECT_ROOT:``).

        Retains current-working-directory semantics for legacy files that
        declare no root.
        """
        starter_path = Path(self.starterfile).resolve()
        root_value = (self.paths or {}).get("root")
        if not root_value:
            return Path.cwd().resolve()
        return (starter_path.parent / root_value).resolve()
    
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
            pseudo_content = re.split(
                r'^# SPECIFICATIONS\s*$', pseudo_content,
                maxsplit=1, flags=re.MULTILINE
            )[0]

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

    def parse_specifications(self) -> Dict[str, str]:
        """Read optional user-authored .pseudo artifacts from the starterfile."""
        try:
            content = Path(self.starterfile).read_text(encoding="utf-8")
        except OSError as exc:
            self.errors.append("Could not read specifications: {}".format(exc))
            return {}
        section = re.search(
            r'^# SPECIFICATIONS\s*$(.*)\Z', content,
            flags=re.MULTILINE | re.DOTALL
        )
        if not section:
            return {}
        specs: Dict[str, str] = {}
        active = None
        body: List[str] = []
        for line in section.group(1).splitlines():
            header = re.match(r'^##\s+(.+?)\s*$', line)
            if header:
                if active is not None:
                    specs[active] = "\n".join(body).strip() + "\n"
                active, body = header.group(1).strip(), []
            elif active is not None:
                body.append(line)
        if active is not None:
            specs[active] = "\n".join(body).strip() + "\n"
        return specs
    
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

    def _resolve_project_path(self, filepath: str) -> Path:
        """Resolve a header path and ensure it stays within the working tree."""
        path = Path(filepath)
        if path.is_absolute():
            raise ValueError(f"PSEUDOCODE path must be project-relative: {filepath}")
        root = (self.project_root or Path.cwd()).resolve()
        resolved = (root / path).resolve()
        try:
            resolved.relative_to(root)
        except ValueError as exc:
            raise ValueError(f"PSEUDOCODE path escapes project root: {filepath}") from exc
        return resolved

    def prepare_mode_a_files(self, file_pseudocodes: Dict[str, str], repomap_none: bool = False) -> Tuple[bool, List[str]]:
        """Seed REPOMAP directories, then create missing header-defined files."""
        report = []
        if repomap_none:
            report.append("  - REPOMAP is NONE: skipping directory seeding")
        else:
            repomap = parse_repomap(self.starterfile)
            # Blueprint creation only seeds directories; REPOMAP file entries
            # have no effect on which files are created.
            success, message = create_blueprint(repomap, project_root=str(self.project_root or Path.cwd()))
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
        for filepath, content in self.parse_specifications().items():
            try:
                target = self._resolve_project_path(filepath)
                if target.suffix != ".pseudo":
                    raise ValueError("Specification artifacts must use the .pseudo extension")
                target.parent.mkdir(parents=True, exist_ok=True)
                if target.exists():
                    report.append("  - Existing specification preserved: {}".format(filepath))
                else:
                    target.write_text(content, encoding="utf-8")
                    report.append("  ✓ Created specification: {}".format(filepath))
            except (OSError, ValueError) as exc:
                self.errors.append("Could not prepare specification {}: {}".format(filepath, exc))
                report.append("  ✗ Could not prepare specification {}: {}".format(filepath, exc))
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
        
        # Read the section bodies so NONE/empty can skip work deliberately.
        content = Path(self.starterfile).read_text(encoding="utf-8")
        pseudocode_body = _extract_section_body(content, "PSEUDOCODE")
        repomap_body = _extract_section_body(content, "REPOMAP")
        databases_body = _extract_section_body(content, "DATABASES")
        pseudocode_none = is_none_section(pseudocode_body)
        repomap_none = repomap_body is None or is_none_section(repomap_body)
        databases_none = databases_body is None or is_none_section(databases_body)

        # Step 1: Parse starterfile.pseudo
        print("\n[Step 1] Extracting pseudocode from starterfile.pseudo...")
        file_pseudocodes = {} if pseudocode_none else self.parse_starterfile()
        specifications = self.parse_specifications()

        if pseudocode_none:
            print(
                "  PSEUDOCODE is NONE: assuming code was already generated; "
                "skipping generation."
            )
        elif not file_pseudocodes and not specifications:
            self.errors.append("No source pseudocode or project specifications found in starterfile")
            return False
        
        print("  Found {} source files and {} project specifications".format(
            len(file_pseudocodes), len(specifications)
        ))

        if not pseudocode_none:
            # Step 2: Seed directories and create files using header paths.
            print("\n[Step 2] Preparing project structure from REPOMAP and PSEUDOCODE...")
            prepared, preparation_report = self.prepare_mode_a_files(
                file_pseudocodes, repomap_none=repomap_none
            )
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

        # Step 3b: Create SQLite databases from the DATABASES section.
        if not self.create_databases(skip=databases_none):
            return False
        
        # Step 4: Convert pseudocode to real code
        if not pseudocode_none:
            print("\n[Step 4] Converting pseudocode to real code...")
            if not self.convert_pseudocodes(file_pseudocodes):
                self.warnings.append(
                    "starterfile.pseudo was kept because one or more files were not generated"
                )
                print("\nGeneration incomplete; starterfile.pseudo has been preserved.")
                return False

        # Step 5: Archive starterfile.pseudo (timestamped) into the tmp folder.
        if self.archive:
            self._archive_starterfile()

        return True

    def create_databases(self, skip: bool = False) -> bool:
        """Create SQLite databases (and their ``.sql`` schemas) from DATABASES."""
        if skip:
            print("\n[Step 3b] DATABASES is NONE: skipping database creation.")
            return True

        print("\n[Step 3b] Creating SQLite schemas and databases...")
        try:
            from .sql_schema_creator import DatabaseSpecError, create_schema_files
        except ImportError:  # pragma: no cover - direct-script execution
            from sql_schema_creator import DatabaseSpecError, create_schema_files

        project_root = self.project_root or Path.cwd()
        try:
            schemas = create_schema_files(Path(self.starterfile), project_root)
        except (OSError, DatabaseSpecError) as exc:
            self.errors.append("Failed to create SQL schemas: {}".format(exc))
            print("  ✗ {}".format(exc))
            return False

        if not schemas:
            print("  (no database definitions found)")
            return True

        try:
            from data_handler import create_databases as _create_databases
        except ImportError:  # pragma: no cover - data_handler is always packaged
            self.warnings.append("data_handler unavailable; .db files were not created")
            print("  ⚠ data_handler unavailable; databases not created")
            return True

        # The data directory is created only when its location was requested
        # explicitly (--data-dir / env var / # PATHS / interactive prompt); the
        # implicit default is never created as a side effect.
        source = data_dir_source(
            override=self._explicit_data_dir, project_value=self.paths.get("data_dir")
        )
        create_dir = data_dir_is_explicit(source) or self.interactive
        try:
            created = _create_databases(
                str(project_root),
                data_dir=self.data_dir,
                interactive=self.interactive,
                create_dir=create_dir,
            )
        except Exception as exc:
            self.errors.append("Database creation failed: {}".format(exc))
            print("  ✗ {}".format(exc))
            return False

        self.created_databases = list(created)
        for path in created:
            print("  ✓ Created database {}".format(path))
        return True

    def _archive_starterfile(self) -> None:
        """Move the starterfile into ``tmp/`` with a timestamp, on success."""
        if not Path(self.starterfile).exists():
            return
        print("\n[Step 5] Archiving starterfile.pseudo...")
        try:
            destination = archive_starterfile(
                self.starterfile,
                project_root=str(self.project_root) if self.project_root else None,
            )
            if destination is not None:
                print("  ✓ Moved {} -> {}".format(self.starterfile, destination))
        except OSError as exc:
            self.warnings.append("Failed to archive starterfile.pseudo: {}".format(exc))
            print("  ⚠ Could not archive starterfile: {}".format(exc))
    
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
        Call the configured local LLM to convert pseudocode to real code.
        
        Args:
            pseudocode: The pseudocode to convert
            filepath: The target file path (for context)
        
        Returns: Generated code or None if failed
        """
        try:
            import subprocess
            
            # Build prompt for LLM
            prompt = self._build_conversion_prompt(pseudocode, filepath)
            
            # Call local LLM via ollama (model resolved from shared.llm_config)
            model = resolve_llm("generation").model
            result = subprocess.run(
                ['ollama', 'run', model],
                input=prompt,
                capture_output=True,
                text=True,
                timeout=600
            )
            
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                self.errors.append(f"LLM error: {result.stderr}")
                return None
        
        except FileNotFoundError:
            # Ollama not installed/not in PATH
            print("    ⚠ Warning: ollama not available, skipping LLM conversion")
            print("    Please ensure the configured model is available via ollama")
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
    parser = argparse.ArgumentParser(description="Render a starterfile.pseudo project")
    parser.add_argument("starterfile", nargs="?", default="starterfile.pseudo")
    parser.add_argument("--project-root", help="Override the project root declared by the starterfile")
    args = parser.parse_args()
    renderer = PseudocodeRenderer(args.starterfile, project_root=args.project_root)
    success = renderer.run()
    return "success" if success else "fail"


if __name__ == '__main__':
    result = main()
    print(f"\n[Result]: {result}")
