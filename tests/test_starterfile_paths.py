"""Tests for the optional # PATHS starterfile section parser."""

from code_starter.starterfile_paths import parse_paths, parse_text_paths


def test_parses_paths_section():
    text = "# PATHS\nroot: .\ndata_dir: mydb\n\n# REPOMAP\nsmoke\n"
    assert parse_text_paths(text) == {"root": ".", "data_dir": "mydb"}


def test_missing_section_is_empty():
    assert parse_text_paths("# REPOMAP\nsmoke\n") == {}


def test_section_stops_at_next_heading():
    text = "# PATHS\nroot: .\ndata_dir: d\n# DATABASES\nNONE\n"
    assert parse_text_paths(text) == {"root": ".", "data_dir": "d"}


def test_legacy_project_root_marker_is_honoured():
    assert parse_text_paths("# PROJECT_ROOT: .\n\n# REPOMAP\n") == {"root": "."}


def test_paths_section_overrides_legacy_marker():
    text = "# PATHS\nroot: sub\n\n# PROJECT_ROOT: ignored\n"
    assert parse_text_paths(text)["root"] == "sub"


def test_parse_paths_reads_file_and_missing(tmp_path):
    starterfile = tmp_path / "starterfile.pseudo"
    starterfile.write_text("# PATHS\nroot: sub\ndata_dir: db\n", encoding="utf-8")
    assert parse_paths(starterfile) == {"root": "sub", "data_dir": "db"}
    assert parse_paths(tmp_path / "nope.pseudo") == {}
