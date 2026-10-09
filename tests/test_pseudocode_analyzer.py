"""Offline tests for the pre-generation starterfile analyzer."""

from pathlib import Path

from code_analyzer.pseudocode_analyzer import PseudocodeAnalyzer

APPROVED = """# STATUS: APPROVED

# REPOMAP

smoke-project
    |______ src/

# DATABASES

users.db
table 1 name: people
table 1 columns:
- identifier
- name

# PSEUDOCODE

## smoke-project/src/app.py
INPUT: a name
OUTPUT: a greeting
TASK: return a greeting
"""


def _write(tmp_path: Path, content: str, name: str = "starterfile.pseudo") -> Path:
    path = tmp_path / name
    path.write_text(content, encoding="utf-8")
    return path


def test_clean_approved_starterfile_passes(tmp_path):
    path = _write(tmp_path, APPROVED)
    report = PseudocodeAnalyzer(str(path), project_root=str(tmp_path)).analyze()

    assert report.ok
    assert report.errors == []
    assert report.warnings == []


def test_missing_status_marker_is_error(tmp_path):
    path = _write(tmp_path, APPROVED.replace("# STATUS: APPROVED\n", ""))
    report = PseudocodeAnalyzer(str(path), project_root=str(tmp_path)).analyze()

    assert not report.ok
    assert any(tag.code == "status-missing" for tag in report.errors)


def test_missing_required_section_is_error(tmp_path):
    path = _write(tmp_path, APPROVED.replace("# DATABASES", "# NOTES"))
    report = PseudocodeAnalyzer(str(path), project_root=str(tmp_path)).analyze()

    assert not report.ok
    assert any(tag.code == "section-missing" for tag in report.errors)


def test_none_sections_are_accepted(tmp_path):
    content = """# STATUS: APPROVED

# REPOMAP
NONE

# DATABASES
NONE

# PSEUDOCODE
NONE
"""
    path = _write(tmp_path, content)
    report = PseudocodeAnalyzer(str(path), project_root=str(tmp_path)).analyze()

    assert report.ok


def test_duplicate_header_is_error(tmp_path):
    content = APPROVED + "\n## smoke-project/src/app.py\nTASK: duplicate\n"
    path = _write(tmp_path, content)
    report = PseudocodeAnalyzer(str(path), project_root=str(tmp_path)).analyze()

    assert any(tag.code == "duplicate-header" for tag in report.errors)


def test_path_outside_repomap_is_warning(tmp_path):
    content = APPROVED.replace(
        "## smoke-project/src/app.py",
        "## another-project/main.py",
    )
    path = _write(tmp_path, content)
    report = PseudocodeAnalyzer(str(path), project_root=str(tmp_path)).analyze()

    assert report.ok  # warnings do not block
    assert any(tag.code == "structure-orphan-file" for tag in report.warnings)


def test_report_and_tagged_copy_are_written(tmp_path):
    path = _write(tmp_path, APPROVED.replace("# STATUS: APPROVED\n", ""))
    analyzer = PseudocodeAnalyzer(str(path), project_root=str(tmp_path))
    analyzer.analyze()

    report_path = analyzer.write_report()
    tagged_path = analyzer.write_tagged_copy()

    assert report_path == tmp_path / "docs" / "pseudocode_report.md"
    assert report_path.is_file()
    assert "FAIL" in report_path.read_text(encoding="utf-8")
    assert tagged_path is not None and tagged_path.is_file()
    assert "# TAG: ERROR: status-missing" in tagged_path.read_text(encoding="utf-8")
    # The approved original must not be mutated.
    assert "# TAG:" not in path.read_text(encoding="utf-8")
