"""Integration: data-dir creation is gated on an explicit # PATHS declaration."""

from pathlib import Path

from code_starter.pseudocode_renderer import PseudocodeRenderer


def _starterfile(tmp_path: Path, *, with_paths: bool) -> Path:
    paths = "# PATHS\nroot: .\ndata_dir: store\n\n" if with_paths else ""
    text = (
        "# STATUS: APPROVED\n\n"
        + paths
        + "# REPOMAP\n\nsmoke-project\n    |______ src/\n\n"
        + "# DATABASES\nusers.db\ntable 1 name: people\ntable 1 columns:\n"
        + "- identifier: primary key\n- name: text\n\n"
        + "# PSEUDOCODE\n\n## smoke-project/src/app.py\n"
        + "INPUT: a name\nOUTPUT: a greeting\nTASK: return a greeting\n"
    )
    starterfile = tmp_path / "starterfile.pseudo"
    starterfile.write_text(text, encoding="utf-8")
    return starterfile


def _clean_env(monkeypatch):
    monkeypatch.delenv("CODE_ASSISTANT_DATA_DIR", raising=False)
    monkeypatch.delenv("DATA_DIR", raising=False)


def test_declared_paths_authorise_dir_creation(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    _clean_env(monkeypatch)
    _starterfile(tmp_path, with_paths=True)
    captured = {}

    def fake_create_databases(project_root, data_dir=None, interactive=False, create_dir=True):
        captured["data_dir"] = data_dir
        captured["create_dir"] = create_dir
        return []

    monkeypatch.setattr("data_handler.create_databases", fake_create_databases)
    renderer = PseudocodeRenderer()
    renderer.call_llm_for_conversion = lambda *_args: "def greet(name):\n    return name\n"

    assert renderer.run_mode_a()
    assert renderer.data_dir == "store"
    assert captured["data_dir"] == "store"
    assert captured["create_dir"] is True


def test_implicit_paths_do_not_authorise_dir_creation(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    _clean_env(monkeypatch)
    _starterfile(tmp_path, with_paths=False)
    captured = {}

    def fake_create_databases(project_root, data_dir=None, interactive=False, create_dir=True):
        captured["create_dir"] = create_dir
        return []

    monkeypatch.setattr("data_handler.create_databases", fake_create_databases)
    renderer = PseudocodeRenderer()
    renderer.call_llm_for_conversion = lambda *_args: "def greet(name):\n    return name\n"

    assert renderer.run_mode_a()
    assert renderer.paths == {}
    assert captured["create_dir"] is False
