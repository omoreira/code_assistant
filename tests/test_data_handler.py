"""Offline tests for data_handler SQLite database creation."""

import shutil
import sqlite3
from pathlib import Path

import pytest

from data_handler import (
    DatabaseCreator,
    DataDirectoryMissingError,
    create_databases,
    sqlite3_path,
)

SCHEMA_DIR = Path("src") / "data_handler" / "sqlite_schema"


def _write_schema(project_root: Path, name: str, sql: str) -> Path:
    directory = project_root / SCHEMA_DIR
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / name
    path.write_text(sql, encoding="utf-8")
    return path


def test_no_schemas_returns_empty(tmp_path):
    assert create_databases(str(tmp_path), data_dir="data") == []


def test_create_all_overwrites_via_injected_runner(tmp_path, monkeypatch):
    _write_schema(tmp_path, "users.db.sql", "CREATE TABLE people (identifier TEXT);")
    monkeypatch.setattr("data_handler.db_creator.sqlite3_path", lambda: "/usr/bin/sqlite3")

    calls = []

    def runner(command, input_text):
        calls.append((command, input_text))
        Path(command[1]).write_text(input_text, encoding="utf-8")

    created = create_databases(str(tmp_path), data_dir="data", runner=runner)

    assert created == [(tmp_path / "data" / "users.db").resolve()]
    assert (tmp_path / "data" / "users.db").read_text(encoding="utf-8").startswith(
        "CREATE TABLE"
    )
    assert calls and calls[0][0][1].endswith("users.db")


def test_create_all_without_create_dir_requires_existing(tmp_path):
    _write_schema(tmp_path, "users.db.sql", "CREATE TABLE t (identifier TEXT);")

    with pytest.raises(DataDirectoryMissingError):
        create_databases(
            str(tmp_path), data_dir="data", create_dir=False, runner=lambda *_: None
        )

    # The directory is never created implicitly.
    assert not (tmp_path / "data").exists()


def test_create_all_with_create_dir_makes_directory(tmp_path):
    _write_schema(tmp_path, "users.db.sql", "CREATE TABLE t (identifier TEXT);")

    created = create_databases(
        str(tmp_path), data_dir="data", create_dir=True, runner=lambda *_: None
    )

    assert created == [(tmp_path / "data" / "users.db").resolve()]
    assert (tmp_path / "data").is_dir()


def test_prompt_is_skipped_when_not_interactive(tmp_path, monkeypatch):
    _write_schema(tmp_path, "users.db.sql", "CREATE TABLE t (identifier TEXT);")
    monkeypatch.setattr("data_handler.db_creator.sqlite3_path", lambda: "/usr/bin/sqlite3")

    def boom(_prompt):
        raise AssertionError("pipeline must never prompt")

    monkeypatch.setattr("builtins.input", boom)
    creator = DatabaseCreator(str(tmp_path), data_dir="data", interactive=False, runner=lambda *_: None)

    assert creator.resolve_data_dir() == (tmp_path / "data").resolve()


@pytest.mark.skipif(sqlite3_path() is None, reason="sqlite3 CLI not installed")
def test_integration_creates_real_database(tmp_path):
    _write_schema(
        tmp_path,
        "users.db.sql",
        'CREATE TABLE IF NOT EXISTS "people" ("identifier" TEXT PRIMARY KEY NOT NULL, "name" TEXT);',
    )

    created = create_databases(str(tmp_path), data_dir="data")

    assert created and created[0].is_file()
    connection = sqlite3.connect(str(created[0]))
    try:
        tables = {
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type='table';"
            )
        }
    finally:
        connection.close()
    assert "people" in tables
