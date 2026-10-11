"""data_handler - SQLite database creation and data-storage helpers.

This package turns the ``.sql`` schemas produced by
``code_starter.sql_schema_creator`` (under
``src/data_handler/sqlite_schema/``) into real SQLite database files.

The database files are written to a data-storage directory that defaults to
``data/`` relative to the target project root. In interactive use the caller
may prompt the operator for that path; automated callers (the pipeline) pass an
explicit directory and never prompt.

Example:
    from data_handler import DatabaseCreator

    creator = DatabaseCreator("/path/to/project", data_dir="data")
    created = creator.create_all()
"""

from shared.constants import DEFAULT_DATA_DIR

from data_handler.db_creator import (
    SCHEMA_DIR,
    DatabaseCreator,
    DataDirectoryMissingError,
    Sqlite3UnavailableError,
    create_databases,
    sqlite3_path,
)

__version__ = "0.1.0"

__all__ = [
    "DEFAULT_DATA_DIR",
    "SCHEMA_DIR",
    "DatabaseCreator",
    "DataDirectoryMissingError",
    "Sqlite3UnavailableError",
    "create_databases",
    "sqlite3_path",
]
