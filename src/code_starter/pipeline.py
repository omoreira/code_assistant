"""End-to-end pipeline for an approved ``starterfile.pseudo``.

Stages, in order:

0. **Preflight** (static, no generation): confirm the starterfile exists and
   carries the ``# STATUS: APPROVED`` marker, that every required section
   (REPOMAP, DATABASES, PSEUDOCODE) is present, that the ``sqlite3`` tool and
   Ollama are available, and run ``code_analyzer.pseudocode_analyzer`` to tag
   inconsistencies. Blocking errors abort before any code is written.
1. **code_starter** builds the repository skeleton, creates SQLite schemas and
   databases, then generates code from the PSEUDOCODE section.
2. **code_analyzer** analyzes the generated code.
3. **repo_documenter** writes project documentation.

A smoke test (compile generated modules, verify each database) is written to
``<project_root>/tmp/``. On overall success the starterfile is moved to
``tmp/`` with a timestamp; on any failure it is left untouched.

Usage:
    python -m code_starter.pipeline <project_root> [--data-dir data]
"""

from __future__ import annotations

import argparse
import ast
import sqlite3
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from code_analyzer.pseudocode_analyzer import PseudocodeAnalyzer
from code_starter.pseudocode_renderer import PseudocodeRenderer, archive_starterfile
from code_starter.starterfile_paths import parse_paths
from shared.constants import DEFAULT_DATA_DIR
from shared.paths_config import resolve_data_dir


@dataclass
class StageResult:
    name: str
    ok: bool
    detail: str = ""


@dataclass
class PipelineResult:
    ok: bool
    stages: List[StageResult] = field(default_factory=list)
    smoke_report: Optional[str] = None
    data_dir: Optional[str] = None


class Pipeline:
    """Drive preflight and the code_starter/analyzer/documenter stages."""

    def __init__(
        self,
        project_root: str = ".",
        starterfile: str = "starterfile.pseudo",
        *,
        data_dir: Optional[str] = None,
        use_llm: bool = False,
        llm_interface=None,
        interactive: bool = False,
        tmp_dir: Optional[str] = None,
        renderer=None,
        documenter=None,
        sqlite_available=None,
    ) -> None:
        self.project_root = Path(project_root).expanduser().resolve()
        candidate = Path(starterfile)
        self.starterfile = (
            candidate if candidate.is_absolute() else self.project_root / candidate
        )
        # The starterfile may declare a # PATHS section (root + data_dir).
        self.paths = parse_paths(self.starterfile) or {}
        # Resolve the data-storage folder when the caller passes none:
        # CLI override -> CODE_ASSISTANT_DATA_DIR/DATA_DIR -> # PATHS -> config.
        self.data_dir = resolve_data_dir(
            override=data_dir, project_value=self.paths.get("data_dir")
        )
        self.use_llm = use_llm
        self._llm = llm_interface
        self.interactive = interactive
        self.tmp_dir = (
            Path(tmp_dir).expanduser() if tmp_dir else self.project_root / "tmp"
        )
        self._renderer = renderer
        self._documenter = documenter
        self._sqlite_available = sqlite_available

    # -- helpers ---------------------------------------------------------
    def llm_interface(self):
        if self._llm is None:
            from shared.llm import LLMInterface

            self._llm = LLMInterface()
        return self._llm

    def _sqlite_ok(self) -> bool:
        if self._sqlite_available is not None:
            return bool(self._sqlite_available())
        from data_handler import sqlite3_path

        return sqlite3_path() is not None

    def _write_tmp(self, name: str, content: str) -> Path:
        self.tmp_dir.mkdir(parents=True, exist_ok=True)
        target = self.tmp_dir / name
        target.write_text(content, encoding="utf-8")
        return target

    # -- preflight -------------------------------------------------------
    def preflight(self) -> List[str]:
        errors: List[str] = []
        if not self.starterfile.is_file():
            return ["starterfile not found: {}".format(self.starterfile)]

        analyzer = PseudocodeAnalyzer(
            str(self.starterfile),
            project_root=str(self.project_root),
            use_llm=self.use_llm,
            llm_interface=self._llm,
        )
        report = analyzer.analyze()
        analyzer.write_report()
        analyzer.write_tagged_copy()
        errors.extend(
            "starterfile: {}: {}".format(tag.code, tag.message) for tag in report.errors
        )

        if not self._sqlite_ok():
            errors.append("sqlite3 is required but was not found on PATH")

        llm = self.llm_interface()
        available = getattr(llm, "is_available", lambda: True)()
        if not available:
            endpoint = getattr(llm, "api_endpoint", "unknown endpoint")
            errors.append("Ollama is unavailable at {}; aborting".format(endpoint))
        return errors

    # -- stages ----------------------------------------------------------
    def _analyze_generated(self, generated: List[Path]) -> StageResult:
        from code_analyzer.hybrid_code_analyzer import quick_check

        scanned = 0
        issues: List[str] = []
        for path in generated:
            if path.suffix.lower() not in {".py", ".pyi"} or not path.is_file():
                continue
            scanned += 1
            result = quick_check(path.read_text(encoding="utf-8"))
            if not result.success:
                issues.extend(result.errors)
        detail = "analyzed {} file(s)".format(scanned)
        if issues:
            detail += "; {} issue(s)".format(len(issues))
        self._write_tmp(
            "code_analysis_{}.txt".format(datetime.now().strftime("%Y%m%d-%H%M%S")),
            "\n".join(issues) if issues else "no issues",
        )
        return StageResult("code_analyzer", not issues, detail)

    def _document(self) -> StageResult:
        if self._documenter is not None:
            documenter = self._documenter
        else:
            from repo_documenter.repo_documenter import RepoDocumenter

            llm = self.llm_interface() if self.use_llm else None
            documenter = RepoDocumenter(str(self.project_root), llm_interface=llm)
        result = documenter.generate_docs(
            project_name=self._project_name(), description="", update_existing=False
        )
        detail = "created {}, preserved {}".format(
            len(result.created), len(result.skipped)
        )
        return StageResult("repo_documenter", True, detail)

    def _project_name(self) -> Optional[str]:
        try:
            from code_starter.blueprint_renderer import parse_repomap

            parsed = parse_repomap(str(self.starterfile)) or {"directories": []}
            dirs = parsed.get("directories", [])
            if dirs:
                return dirs[0].split("/")[0]
        except Exception:  # pragma: no cover - best effort
            pass
        return self.project_root.name

    # -- smoke test ------------------------------------------------------
    def _smoke_test(self, generated: List[Path], databases: List[Path]) -> Path:
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        lines: List[str] = ["# Smoke test @ {}".format(stamp), "", "## Compile"]
        for path in generated:
            rel = self._relative(path)
            try:
                ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
                lines.append("OK    {}".format(rel))
            except SyntaxError as exc:
                lines.append("ERROR {}: {}".format(rel, exc))
        lines.append("")
        lines.append("## Databases")
        for db in databases:
            rel = self._relative(db)
            try:
                connection = sqlite3.connect(str(db))
                try:
                    integrity = connection.execute("PRAGMA integrity_check;").fetchone()
                    lines.append("OK    {} integrity={}".format(rel, integrity[0]))
                finally:
                    connection.close()
            except sqlite3.Error as exc:
                lines.append("ERROR {}: {}".format(rel, exc))
        return self._write_tmp("smoke_{}.txt".format(stamp), "\n".join(lines) + "\n")

    def _relative(self, path: Path) -> str:
        try:
            return str(path.resolve().relative_to(self.project_root))
        except ValueError:
            return str(path)

    # -- driver ----------------------------------------------------------
    def run(self) -> PipelineResult:
        result = PipelineResult(ok=False, data_dir=str(self.data_dir))

        errors = self.preflight()
        if errors:
            result.stages.append(StageResult("preflight", False, "; ".join(errors)))
            print("\n\u2717 Preflight failed:")
            for error in errors:
                print("  - {}".format(error))
            return result
        result.stages.append(
            StageResult("preflight", True, "starterfile approved and consistent")
        )

        renderer = self._renderer or PseudocodeRenderer(
            str(self.starterfile),
            project_root=str(self.project_root),
            data_dir=self.data_dir,
            interactive=self.interactive,
            archive=False,
        )
        try:
            generated_ok = renderer.run_mode_a()
            detail = "generated {} file(s)".format(
                len(getattr(renderer, "converted_files", []))
            )
        except Exception as exc:  # pragma: no cover - defensive
            generated_ok, detail = False, "code_starter raised: {}".format(exc)
        result.stages.append(StageResult("code_starter", generated_ok, detail))
        if not generated_ok:
            print("\n\u2717 code_starter failed; starterfile left in place.")
            return result

        generated = [
            self.project_root / item
            for item in getattr(renderer, "converted_files", [])
        ]
        databases = list(getattr(renderer, "created_databases", []))
        result.smoke_report = str(self._smoke_test(generated, databases))

        analyze_stage = self._analyze_generated(generated)
        result.stages.append(analyze_stage)

        try:
            result.stages.append(self._document())
        except Exception as exc:  # pragma: no cover - defensive
            result.stages.append(StageResult("repo_documenter", False, str(exc)))

        if all(stage.ok for stage in result.stages):
            try:
                destination = archive_starterfile(
                    str(self.starterfile), project_root=str(self.project_root)
                )
                if destination is not None:
                    print("\n\u2713 Starterfile archived to {}".format(destination))
            except OSError as exc:
                print("\n\u26a0 Could not archive starterfile: {}".format(exc))
            result.ok = True
        return result


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_root", nargs="?", default=".")
    parser.add_argument("--starterfile", default="starterfile.pseudo")
    parser.add_argument(
        "--data-dir",
        default=None,
        help=(
            "Database storage path. Overrides CODE_ASSISTANT_DATA_DIR/DATA_DIR "
            "and paths.data_dir (built-in default: {})".format(DEFAULT_DATA_DIR)
        ),
    )
    parser.add_argument("--use-llm", action="store_true")
    parser.add_argument("--interactive", action="store_true")
    from shared.llm_config import resolve_llm

    _llm_defaults = resolve_llm("generation")
    parser.add_argument("--model", default=_llm_defaults.model)
    parser.add_argument("--endpoint", default=_llm_defaults.base_url)
    args = parser.parse_args(argv)

    llm = None
    if args.use_llm:
        from shared.llm import LLMInterface

        llm = LLMInterface(model=args.model, api_endpoint=args.endpoint)

    result = Pipeline(
        args.project_root,
        args.starterfile,
        data_dir=args.data_dir,
        use_llm=args.use_llm,
        llm_interface=llm,
        interactive=args.interactive,
    ).run()

    print("\n=== Pipeline summary ===")
    for stage in result.stages:
        mark = "OK " if stage.ok else "FAIL"
        print("  [{}] {}: {}".format(mark, stage.name, stage.detail))
    if result.smoke_report:
        print("  smoke report: {}".format(result.smoke_report))
    return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
