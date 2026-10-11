"""Offline tests for the preflight + pipeline orchestrator."""

from pathlib import Path

from code_starter.pipeline import Pipeline

APPROVED = """# STATUS: APPROVED

# REPOMAP

smoke-project
    |______ src/

# DATABASES
NONE

# PSEUDOCODE

## smoke-project/src/app.py
INPUT: a name
OUTPUT: a greeting
TASK: return a greeting
"""

VALID_PY = "def greet(name):\n    return 'hi ' + name\n"


class FakeLLM:
    api_endpoint = "http://fake:11434"

    def __init__(self, available=True):
        self._available = available

    def is_available(self):
        return self._available


class _DocResult:
    def __init__(self):
        self.created = ["README.md"]
        self.updated = []
        self.skipped = []


class FakeDocumenter:
    def __init__(self):
        self.kwargs = None

    def generate_docs(self, **kwargs):
        self.kwargs = kwargs
        return _DocResult()


class FakeRenderer:
    def __init__(self, converted, ok=True, databases=None):
        self.converted_files = list(converted)
        self.created_databases = list(databases or [])
        self._ok = ok

    def run_mode_a(self):
        return self._ok


def _setup(tmp_path: Path) -> Path:
    (tmp_path / "starterfile.pseudo").write_text(APPROVED, encoding="utf-8")
    generated = tmp_path / "smoke-project" / "src" / "app.py"
    generated.parent.mkdir(parents=True, exist_ok=True)
    generated.write_text(VALID_PY, encoding="utf-8")
    return generated


def _pipeline(tmp_path, renderer, llm=None):
    return Pipeline(
        str(tmp_path),
        data_dir="data",
        llm_interface=llm or FakeLLM(True),
        renderer=renderer,
        documenter=FakeDocumenter(),
        sqlite_available=lambda: True,
    )


def test_pipeline_success_archives_starterfile(tmp_path):
    _setup(tmp_path)
    renderer = FakeRenderer(["smoke-project/src/app.py"])

    result = _pipeline(tmp_path, renderer).run()

    assert result.ok
    assert [stage.name for stage in result.stages] == [
        "preflight",
        "code_starter",
        "code_analyzer",
        "repo_documenter",
    ]
    assert all(stage.ok for stage in result.stages)
    assert result.smoke_report is not None and Path(result.smoke_report).is_file()
    # Starterfile moved into tmp on success.
    assert not (tmp_path / "starterfile.pseudo").exists()
    archived = list((tmp_path / "tmp").glob("starterfile.pseudo.*"))
    assert archived


def test_pipeline_aborts_when_ollama_unavailable(tmp_path):
    _setup(tmp_path)
    renderer = FakeRenderer(["smoke-project/src/app.py"])

    result = _pipeline(tmp_path, renderer, llm=FakeLLM(False)).run()

    assert not result.ok
    assert result.stages[0].name == "preflight"
    assert not result.stages[0].ok
    # Preflight failure leaves the starterfile in place.
    assert (tmp_path / "starterfile.pseudo").exists()


def test_pipeline_aborts_without_approval_marker(tmp_path):
    _setup(tmp_path)
    (tmp_path / "starterfile.pseudo").write_text(
        APPROVED.replace("# STATUS: APPROVED\n", ""), encoding="utf-8"
    )
    renderer = FakeRenderer(["smoke-project/src/app.py"])

    result = _pipeline(tmp_path, renderer).run()

    assert not result.ok
    assert "status-missing" in result.stages[0].detail
    assert (tmp_path / "starterfile.pseudo").exists()


def test_pipeline_leaves_starterfile_when_generation_fails(tmp_path):
    _setup(tmp_path)
    renderer = FakeRenderer(["smoke-project/src/app.py"], ok=False)

    result = _pipeline(tmp_path, renderer).run()

    assert not result.ok
    code_starter_stage = next(s for s in result.stages if s.name == "code_starter")
    assert not code_starter_stage.ok
    assert (tmp_path / "starterfile.pseudo").exists()


DECLARED_ROOT = """# PATHS
root: sub

# REPOMAP

sub

# PSEUDOCODE

## sub/src/app.py
TASK: noop
"""


def test_declared_paths_root_used_when_project_root_omitted(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "starterfile.pseudo").write_text(DECLARED_ROOT, encoding="utf-8")

    pipeline = Pipeline(starterfile="starterfile.pseudo")

    assert pipeline.project_root == (tmp_path / "sub").resolve()


def test_explicit_project_root_wins_over_declared(tmp_path, monkeypatch):
    (tmp_path / "starterfile.pseudo").write_text(DECLARED_ROOT, encoding="utf-8")

    pipeline = Pipeline(str(tmp_path), "starterfile.pseudo")

    assert pipeline.project_root == tmp_path.resolve()
