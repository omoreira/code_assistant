"""Run the ``code_starter`` pipeline in the background.

The pipeline is launched as a **separate process** (``python -m
code_starter.pipeline``) so a crash or a long model call cannot take the UI
down. Its combined stdout/stderr is streamed into a list by a reader thread and
the page polls :meth:`PipelineRun.running`. After completion the page reads the
artifacts the pipeline wrote under ``<project_root>/tmp`` and ``docs``.
"""

from __future__ import annotations

import os
import subprocess
import sys
import threading
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


@dataclass
class PipelineRun:
    """A running (or finished) pipeline subprocess with its captured log."""

    process: subprocess.Popen
    log: List[str] = field(default_factory=list)
    _thread: Optional[threading.Thread] = None

    @property
    def returncode(self) -> Optional[int]:
        return self.process.poll()

    def running(self) -> bool:
        return self.process.poll() is None

    def text(self) -> str:
        return "".join(self.log)


def start_pipeline(
    repo_root: Path,
    project_root: Path,
    starterfile: str = "starterfile.pseudo",
    data_dir: Optional[str] = None,
    use_llm: bool = False,
    extra_args: Optional[List[str]] = None,
) -> PipelineRun:
    """Start the pipeline subprocess and begin capturing its output."""
    env = dict(os.environ)
    src = str(Path(repo_root) / "src")
    env["PYTHONPATH"] = src + os.pathsep + env.get("PYTHONPATH", "")

    command = [
        sys.executable,
        "-m",
        "code_starter.pipeline",
        str(project_root),
        "--starterfile",
        starterfile,
    ]
    if data_dir:
        command += ["--data-dir", data_dir]
    if use_llm:
        command += ["--use-llm"]
    if extra_args:
        command += list(extra_args)

    process = subprocess.Popen(
        command,
        cwd=str(repo_root),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )
    run = PipelineRun(process=process)

    def _pump() -> None:
        assert process.stdout is not None
        for line in process.stdout:
            run.log.append(line)

    run._thread = threading.Thread(target=_pump, daemon=True)
    run._thread.start()
    return run


def collect_artifacts(project_root: Path) -> List[Path]:
    """Return report-style files the pipeline may have produced."""
    root = Path(project_root)
    artifacts: List[Path] = []
    tmp = root / "tmp"
    if tmp.is_dir():
        artifacts.extend(sorted(p for p in tmp.glob("*") if p.is_file()))
    report = root / "docs" / "pseudocode_report.md"
    if report.is_file():
        artifacts.append(report)
    return artifacts
