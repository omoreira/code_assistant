"""Tests for the pure ``# DATABASES`` model (parse/render/mutate).

These also assert round-trip fidelity against the *real* generator parser in
:mod:`code_starter.sql_schema_creator` so the builder can never emit a body the
pipeline would reject.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
for _p in (REPO_ROOT / "ui", REPO_ROOT / "src"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from core import database_model as dm  # noqa: E402
from core.verify import verify_databases  # noqa: E402
from code_starter.sql_schema_creator import (  # noqa: E402
    DatabaseSpecError,
    parse_database_specs,
    render_schema,
)


def test_parse_none_and_blank_are_empty():
    for value in ("", "   ", "NONE", "none", "EMPTY"):
        assert dm.parse(value) == []
    assert dm.render([]) == ""


def test_roundtrip_through_model():
    model = [
        {
            "file": "app.db",
            "tables": [
                {
                    "name": "users",
                    "columns": [
                        {"name": "identifier", "desc": "primary key"},
                        {"name": "name", "desc": "display name"},
                        {"name": "email", "desc": ""},
                    ],
                }
            ],
        }
    ]
    assert dm.parse(dm.render(model)) == model


def test_render_matches_real_parser():
    model = dm.parse(
        "app.db\n"
        "table 1 name: users\n"
        "table 1 columns:\n"
        "- identifier: primary key\n"
        "- name: display name\n"
    )
    assert model == [
        {
            "file": "app.db",
            "tables": [
                {
                    "name": "users",
                    "columns": [
                        {"name": "identifier", "desc": "primary key"},
                        {"name": "name", "desc": "display name"},
                    ],
                }
            ],
        }
    ]
    specs = parse_database_specs(dm.render(model))
    assert specs == [("app.db", [("users", ["identifier", "name"])])]
    render_schema(*specs[0])  # must not raise


def test_table_numbering_resets_per_database():
    model = [
        {
            "file": "a.db",
            "tables": [
                {"name": "t1", "columns": [{"name": "identifier", "desc": ""}]},
                {"name": "t2", "columns": [{"name": "identifier", "desc": ""}]},
            ],
        },
        {"file": "b.db", "tables": [{"name": "u1", "columns": [{"name": "identifier", "desc": ""}]}]},
    ]
    text = dm.render(model)
    assert "table 1 name: t1" in text
    assert "table 2 name: t2" in text
    assert text.count("table 1 name:") == 2  # reset for b.db
    # Blank line between databases still parses as two databases.
    assert [name for name, _ in parse_database_specs(text)] == ["a.db", "b.db"]


def test_other_keys_placeholder_ignored():
    model = dm.parse(
        "app.db\n"
        "table 1 name: users\n"
        "table 1 columns:\n"
        "- identifier: primary key\n"
        "- other keys: instructional placeholder\n"
    )
    assert [c["name"] for c in model[0]["tables"][0]["columns"]] == ["identifier"]


def test_add_and_remove_helpers():
    databases = []
    db = dm.add_database(databases, "app.db")
    table = dm.add_table(db, "users")
    dm.add_column(table, "identifier", "primary key")
    assert dm.count(databases) == 1
    assert dm.count_tables(databases) == 1
    assert dm.render(databases) == (
        "app.db\ntable 1 name: users\ntable 1 columns:\n- identifier: primary key"
    )
    dm.remove_column(table, 0)
    dm.remove_table(db, 0)
    dm.remove_database(databases, 0)
    assert databases == []


def test_verify_databases_accepts_valid_and_rejects_missing_identifier():
    good = [{"file": "app.db", "tables": [{"name": "users", "columns": [{"name": "identifier", "desc": "pk"}]}]}]
    ok, _ = verify_databases(dm.render(good))
    assert ok

    bad = [{"file": "app.db", "tables": [{"name": "users", "columns": [{"name": "name", "desc": ""}]}]}]
    ok, _ = verify_databases(dm.render(bad))
    assert not ok


def test_missing_identifier_fails_render_schema():
    specs = parse_database_specs(
        "app.db\ntable 1 name: users\ntable 1 columns:\n- name: display\n"
    )
    with pytest.raises(DatabaseSpecError):
        render_schema(*specs[0])
