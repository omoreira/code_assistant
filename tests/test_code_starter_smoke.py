"""Offline smoke tests for the code_starter user workflow."""

from pathlib import Path

import code_starter
from code_starter.blueprint_renderer import BlueprintRenderer
from code_starter.pseudocode_renderer import PseudocodeRenderer
from code_starter.starterfile_creator import StarterfileCreator


STARTERFILE = """# REPOMAP

smoke-project
    |______ seeded/
        |______ ignored.py

# PSEUDOCODE

## smoke-project/pkg-one/hello world.py
INPUT: a name
OUTPUT: greeting
TASK: return a greeting
"""


def _write_starterfile(tmp_path: Path) -> Path:
    starterfile = tmp_path / "starterfile.pseudo"
    starterfile.write_text(STARTERFILE, encoding="utf-8")
    return starterfile


def test_blueprint_renderer_creates_directories_only(tmp_path):
    starterfile = _write_starterfile(tmp_path)
    output_dir = tmp_path / "blueprint-output"
    blueprint = BlueprintRenderer(str(starterfile))

    parsed = blueprint.parse_blueprint()
    result = blueprint.render_blueprint(str(output_dir))

    assert result == str(output_dir.resolve())
    assert parsed["files"] == []
    assert (output_dir / "smoke-project/seeded").is_dir()
    assert not (output_dir / "smoke-project/ignored.py").exists()


def test_package_import_and_header_paths_create_files(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    _write_starterfile(tmp_path)
    renderer = PseudocodeRenderer()
    renderer.call_llm_for_conversion = lambda *_args: "def greet(name):\n    return f'hi {name}'\n"

    assert code_starter.__version__
    assert renderer.run_mode_a()
    assert (tmp_path / "smoke-project/seeded").is_dir()
    assert (tmp_path / "smoke-project/pkg-one/hello world.py").read_text(
        encoding="utf-8"
    ).startswith("def greet")
    assert not (tmp_path / "smoke-project/ignored.py").exists()
    assert not (tmp_path / "starterfile.pseudo").exists()


def test_failed_generation_preserves_starterfile(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    starterfile = _write_starterfile(tmp_path)
    renderer = PseudocodeRenderer()
    renderer.call_llm_for_conversion = lambda *_args: None

    assert not renderer.run_mode_a()
    assert starterfile.exists()
    assert (tmp_path / "smoke-project/pkg-one/hello world.py").read_text(
        encoding="utf-8"
    ) == ""


def test_invalid_generated_python_is_not_written(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    starterfile = _write_starterfile(tmp_path)
    renderer = PseudocodeRenderer()
    renderer.call_llm_for_conversion = lambda *_args: "def broken(:\n    pass\n"

    assert not renderer.run_mode_a()
    assert starterfile.exists()
    assert (tmp_path / "smoke-project/pkg-one/hello world.py").read_text(
        encoding="utf-8"
    ) == ""
    assert renderer.errors


def test_creator_loads_structure_and_pseudocode(tmp_path, monkeypatch, capsys):
    starterfile = _write_starterfile(tmp_path)
    monkeypatch.setattr("builtins.input", lambda _prompt: str(starterfile))
    creator = StarterfileCreator()

    creator.load_from_file()

    assert creator.root_dir == "smoke-project"
    assert "smoke-project/seeded" in creator.tree_structure
    assert "smoke-project/pkg-one/hello world.py" in creator.pseudocodes
    assert creator.pseudocodes["smoke-project/pkg-one/hello world.py"]["task"] == (
        "return a greeting"
    )
    assert "Loaded 1 file specifications" in capsys.readouterr().out
