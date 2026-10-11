"""Create SQLite database files from generated ``.sql`` schema files.

The schema files are the ones written by
``code_starter.sql_schema_creator.create_schema_files`` into
``src/data_handler/sqlite_schema/``. Each ``<name>.db.sql`` file becomes a
``<name>.db`` database in the configured data directory.

Creation overwrites any existing database at the target path (the schema uses
``CREATE TABLE IF NOT EXISTS`` and each run starts from a clean file). The
``sqlite3`` command-line tool is required.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import Callable, List, Optional

from shared.paths_config import resolve_data_dir

#: Where ``sql_schema_creator`` writes generated schema files.
SCHEMA_DIR = Path("src") / "data_handler" / "sqlite_schema"

#: Runner signature: (command, input_text) -> None. Injected for testing.
Runner = Callable[[List[str], str], None]


class Sqlite3UnavailableError(RuntimeError):
    """Raised when the ``sqlite3`` executable cannot be found."""


def sqlite3_path() -> Optional[str]:
    """Return the path to the ``sqlite3`` executable, or ``None`` if missing."""
    return shutil.which("sqlite3")


def _default_runner(command: List[str], input_text: str) -> None:
    """Run ``sqlite3`` feeding the schema through standard input."""
    result = subprocess.run(
        command,
        input=input_text,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(
            "sqlite3 failed ({}): {}".format(
                result.returncode, result.stderr.strip() or "unknown error"
            )
        )


def schema_files(project_root: Path) -> List[Path]:
    """Return the generated ``.sql`` schema files for a project, sorted."""
    directory = Path(project_root) / SCHEMA_DIR
    if not directory.is_dir():
        return []
    return sorted(directory.glob("*.sql"))


def database_name(schema_file: Path) -> str:
    """Derive the database filename from a schema filename.

    ``users.db.sql`` -> ``users.db``; ``report.sql`` -> ``report``.
    """
    name = schema_file.name
    if name.endswith(".sql"):
        name = name[: -len(".sql")]
    return name


class DatabaseCreator:
    """Create SQLite databases from a project's generated schema files."""

    def __init__(
        self,
        project_root: str,
        data_dir: Optional[str] = None,
        interactive: bool = False,
        runner: Optional[Runner] = None,
    ) -> None:
        self.project_root = Path(project_root).expanduser().resolve()
        if not self.project_root.is_dir():
            raise NotADirectoryError(
                "Target project root must be an existing directory: {}".format(
                    self.project_root
                )
            )
        # Fall back to the resolved default (config/defaults.yaml -> env vars
        # -> built-in) when the caller passes no explicit directory.
        self.default_data_dir = data_dir or resolve_data_dir()
        self.interactive = interactive
        self._runner = runner or _default_runner

    # -- path handling ---------------------------------------------------
    def _absolute_data_dir(self, data_dir: Optional[str] = None) -> Path:
        # An explicit argument always wins. Otherwise, prompt only when
        # interactive; automated callers never prompt.
        chosen = data_dir
        if chosen is None and self.interactive:
            answer = input(
                "Data storage path [{}]: ".format(self.default_data_dir)
            ).strip()
            chosen = answer or self.default_data_dir
        if chosen is None:
            chosen = self.default_data_dir
        path = Path(chosen).expanduser()
        if not path.is_absolute():
            path = self.project_root / path
        return path.resolve()

    def resolve_data_dir(self, data_dir: Optional[str] = None) -> Path:
        """Return the absolute data directory that ``create_all`` will use."""
        return self._absolute_data_dir(data_dir)

    # -- creation --------------------------------------------------------
    def create_all(self, data_dir: Optional[str] = None) -> List[Path]:
        """Create (or overwrite) one database per schema file.

        Returns the list of database paths that were created.
        """
        target_dir = self._absolute_data_dir(data_dir)
        schemas = schema_files(self.project_root)
        if not schemas:
            return []

        executable = sqlite3_path()
        if executable is None:
            raise Sqlite3UnavailableError(
                "sqlite3 is required but was not found on PATH"
            )

        created: List[Path] = []
        target_dir.mkdir(parents=True, exist_ok=True)
        for schema in schemas:
            target = target_dir / database_name(schema)
            if target.exists():
                target.unlink()
            self._runner([executable, str(target)], schema.read_text(encoding="utf-8"))
            created.append(target)
        return created


def create_databases(
    project_root: str,
    data_dir: Optional[str] = None,
    interactive: bool = False,
    runner: Optional[Runner] = None,
) -> List[Path]:
    """Convenience wrapper around :class:`DatabaseCreator`."""
    return DatabaseCreator(
        project_root, data_dir=data_dir, interactive=interactive, runner=runner
    ).create_all()
