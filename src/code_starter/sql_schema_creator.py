"""Create SQLite schema files from a ``# DATABASES`` starterfile section.

The deliberately small input format uses ``table N name: ...`` and
``table N columns:`` records. Column bullets are ``- name: description``;
columns default to SQLite TEXT, and a column named ``identifier`` becomes the
table's TEXT primary key. Output is written to
``<project-root>/src/db_master_handler/sqlite_schema/<database>.sql``.

Usage::

    python -m code_starter.sql_schema_creator starterfile.pseudo
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import List, Optional, Tuple


DATABASES_HEADER = re.compile(r"^#\s*DATABASES\s*$", re.IGNORECASE)
SECTION_HEADER = re.compile(r"^#\s+\w")
TABLE_NAME = re.compile(r"^table\s+\d+\s+name\s*:\s*(.+?)\s*$", re.IGNORECASE)
TABLE_COLUMNS = re.compile(r"^table\s+\d+\s+columns\s*:\s*$", re.IGNORECASE)
COLUMN = re.compile(r"^[-*]\s*([A-Za-z_][A-Za-z0-9_]*)\s*(?::\s*(.*))?$")


class DatabaseSpecError(ValueError):
    """Raised when the DATABASES section is malformed or unsafe."""


def extract_databases_section(content: str) -> str:
    """Return the DATABASES section body, wherever it appears in a starterfile."""
    lines = content.splitlines()
    for index, line in enumerate(lines):
        if DATABASES_HEADER.match(line.strip()):
            body = []
            for candidate in lines[index + 1 :]:
                if SECTION_HEADER.match(candidate.strip()):
                    break
                body.append(candidate)
            return "\n".join(body)
    raise DatabaseSpecError("No #DATABASES section found in starterfile")


def _quote_identifier(value: str) -> str:
    """Quote a SQLite identifier safely."""
    return '"' + value.replace('"', '""') + '"'


def parse_database_specs(section: str) -> List[Tuple[str, List[Tuple[str, List[str]]]]]:
    """Parse a DATABASES body into (filename, [(table, columns), ...]) specs."""
    databases = []
    filename: Optional[str] = None
    tables: List[Tuple[str, List[str]]] = []
    table_name: Optional[str] = None
    columns: List[str] = []
    reading_columns = False

    def finish_table() -> None:
        nonlocal table_name, columns, reading_columns
        if table_name is not None:
            if not columns:
                raise DatabaseSpecError(f"Table {table_name!r} has no column bullets")
            folded = [column.casefold() for column in columns]
            if len(folded) != len(set(folded)):
                raise DatabaseSpecError(f"Table {table_name!r} has duplicate columns")
            tables.append((table_name, columns))
        table_name, columns, reading_columns = None, [], False

    def finish_database() -> None:
        nonlocal filename, tables
        if filename is not None:
            if not tables:
                raise DatabaseSpecError(f"Database {filename!r} has no tables")
            databases.append((filename, tables))
        filename, tables = None, []

    for raw_line in section.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue

        table_match = TABLE_NAME.match(line)
        if table_match:
            finish_table()
            if filename is None:
                raise DatabaseSpecError("A database filename must precede its tables")
            table_name = table_match.group(1).strip()
            if not table_name:
                raise DatabaseSpecError("Table name cannot be empty")
            continue

        if TABLE_COLUMNS.match(line):
            if table_name is None:
                raise DatabaseSpecError("A table name must precede 'table N columns:'")
            reading_columns = True
            continue

        column_match = COLUMN.match(line)
        if column_match and reading_columns and table_name is not None:
            column_name = column_match.group(1)
            # 'other keys:' is an instructional placeholder from the example,
            # not an actual column definition.
            if column_name.casefold() != "other" or (column_match.group(2) or "").strip().casefold() != "keys":
                columns.append(column_name)
            continue

        if line.startswith("-") or line.startswith("*"):
            if reading_columns:
                raise DatabaseSpecError(f"Invalid column entry: {line}")
            continue

        # A non-indented line ending in .db begins a database declaration.
        if line.casefold().endswith(".db"):
            finish_table()
            finish_database()
            if Path(line).name != line or line in {".", ".."}:
                raise DatabaseSpecError("Database entries must be simple filenames ending in .db")
            filename = line
            continue

        if reading_columns:
            # Permit a human-readable continuation/description line while
            # requiring every actual column to have a bullet.
            continue

    finish_table()
    finish_database()
    if not databases:
        raise DatabaseSpecError("DATABASES section contains no database definitions")
    names = [name.casefold() for name, _ in databases]
    if len(names) != len(set(names)):
        raise DatabaseSpecError("Database filenames must be unique")
    return databases


def render_schema(filename: str, tables: List[Tuple[str, List[str]]]) -> str:
    """Render a single database specification as idempotent SQLite DDL."""
    statements = [f"-- Schema for {filename}", "PRAGMA foreign_keys = ON;", ""]
    for table, columns in tables:
        definitions = []
        has_identifier = any(column.casefold() == "identifier" for column in columns)
        for column in columns:
            quoted = _quote_identifier(column)
            if column.casefold() == "identifier":
                definitions.append(f"    {quoted} TEXT PRIMARY KEY NOT NULL")
            else:
                definitions.append(f"    {quoted} TEXT")
        if not has_identifier:
            raise DatabaseSpecError(
                f"Table {table!r} must include an 'identifier' column for its primary key"
            )
        statement = ",\n".join(definitions)
        statements.append(
            f"CREATE TABLE IF NOT EXISTS {_quote_identifier(table)} (\n{statement}\n);"
        )
        statements.append("")
    return "\n".join(statements).rstrip() + "\n"


def create_schema_files(starterfile: Path, project_root: Path) -> List[Path]:
    """Generate schema SQL files and return their paths."""
    content = starterfile.read_text(encoding="utf-8")
    specs = parse_database_specs(extract_databases_section(content))
    output_dir = project_root / "src" / "db_master_handler" / "sqlite_schema"
    output_dir.mkdir(parents=True, exist_ok=True)
    outputs = []
    for filename, tables in specs:
        output = output_dir / f"{filename}.sql"
        output.write_text(render_schema(filename, tables), encoding="utf-8")
        outputs.append(output)
    return outputs


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("starterfile", nargs="?", default="starterfile.pseudo")
    parser.add_argument(
        "--project-root",
        default=".",
        help="Project root where src/db_master_handler/sqlite_schema will be created",
    )
    args = parser.parse_args(argv)
    try:
        outputs = create_schema_files(Path(args.starterfile), Path(args.project_root))
    except (OSError, DatabaseSpecError) as exc:
        parser.error(str(exc))
    for output in outputs:
        print(f"Created {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
