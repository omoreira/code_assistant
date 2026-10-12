"""Pure model for the ``# DATABASES`` starterfile section.

The Starter page's Databases tab builds the ``# DATABASES`` body interactively
(add a database, then tables, then columns). This module is the pure,
Streamlit-free core: it parses the section text into a structured model, lets
callers add/remove items, and renders the model back to the exact
``table N ...`` text that :mod:`code_starter.sql_schema_creator` and the
analyzer expect.

Grammar (mirrors
:func:`code_starter.sql_schema_creator.parse_database_specs`)::

    example.db
    table 1 name: users
    table 1 columns:
    - identifier: primary key
    - name: display name

A model is a list of databases::

    [{"file": "example.db",
      "tables": [{"name": "users",
                  "columns": [{"name": "identifier", "desc": "primary key"}]}]}]
"""

from __future__ import annotations

import re
from typing import List, Optional

_NONE_TOKENS = {"", "NONE", "EMPTY"}

TABLE_NAME_RE = re.compile(r"^table\s+\d+\s+name\s*:\s*(.+?)\s*$", re.IGNORECASE)
TABLE_COLUMNS_RE = re.compile(r"^table\s+\d+\s+columns\s*:\s*$", re.IGNORECASE)
COLUMN_RE = re.compile(r"^[-*]\s*([A-Za-z_][A-Za-z0-9_]*)\s*(?::\s*(.*))?$")

# Plain dicts so the model is trivially serializable in session state.
Column = dict    # {"name": str, "desc": str}
Table = dict     # {"name": str, "columns": list[Column]}
Database = dict  # {"file": str, "tables": list[Table]}


def is_none(text: str) -> bool:
    """True when ``text`` means "no databases" (blank / ``NONE`` / ``EMPTY``)."""
    return (text or "").strip().upper() in _NONE_TOKENS


def parse(text: str) -> List[Database]:
    """Parse DATABASES text into a tolerant, editable model.

    Unlike the strict generator parser this never raises: items may be
    incomplete (an empty table or database) so the UI can build them up. Lines
    that don't fit the grammar are ignored.
    """
    if is_none(text):
        return []

    databases: List[Database] = []
    current: Optional[Database] = None
    table: Optional[Table] = None
    reading_columns = False

    def flush_table() -> None:
        nonlocal table, reading_columns
        if table is not None and current is not None:
            current["tables"].append(table)
        table, reading_columns = None, False

    def flush_db() -> None:
        nonlocal current
        if current is not None:
            databases.append(current)
        current = None

    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue

        match = TABLE_NAME_RE.match(line)
        if match:
            flush_table()
            if current is not None:
                table = {"name": match.group(1).strip(), "columns": []}
            continue

        if TABLE_COLUMNS_RE.match(line):
            reading_columns = table is not None
            continue

        if line.casefold().endswith(".db") and "/" not in line and "\\" not in line:
            flush_table()
            flush_db()
            current = {"file": line, "tables": []}
            continue

        match = COLUMN_RE.match(line)
        if match and reading_columns and table is not None:
            name = match.group(1)
            desc = (match.group(2) or "").strip()
            # 'other keys:' is an instructional placeholder, not a column.
            if name.casefold() == "other" and desc.casefold() == "keys":
                continue
            table["columns"].append({"name": name, "desc": desc})
            continue

    flush_table()
    flush_db()
    return databases


def render(databases: List[Database]) -> str:
    """Render the model to canonical DATABASES text (``""`` when empty)."""
    blocks: List[str] = []
    for database in databases:
        lines = [database["file"]]
        for index, table in enumerate(database.get("tables", []), start=1):
            lines.append("table {} name: {}".format(index, table["name"]))
            lines.append("table {} columns:".format(index))
            for column in table.get("columns", []):
                if column.get("desc"):
                    lines.append("- {}: {}".format(column["name"], column["desc"]))
                else:
                    lines.append("- {}".format(column["name"]))
        blocks.append("\n".join(lines))
    return "\n\n".join(blocks)


# -- mutation helpers ----------------------------------------------------

def add_database(databases: List[Database], filename: str) -> Database:
    database: Database = {"file": filename, "tables": []}
    databases.append(database)
    return database


def remove_database(databases: List[Database], index: int) -> None:
    del databases[index]


def add_table(database: Database, name: str) -> Table:
    table: Table = {"name": name, "columns": []}
    database["tables"].append(table)
    return table


def remove_table(database: Database, index: int) -> None:
    del database["tables"][index]


def add_column(table: Table, name: str, desc: str = "") -> Column:
    column: Column = {"name": name, "desc": desc}
    table["columns"].append(column)
    return column


def remove_column(table: Table, index: int) -> None:
    del table["columns"][index]


def count(databases: List[Database]) -> int:
    """Number of databases in the model."""
    return len(databases)


def count_tables(databases: List[Database]) -> int:
    """Total number of tables across all databases."""
    return sum(len(database.get("tables", [])) for database in databases)
