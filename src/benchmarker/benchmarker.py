"""Create benchmark.pseudo files and turn them into runnable Python harnesses."""

import argparse
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


DEFAULT_SPEC = """# Benchmark specification

GOAL: Describe what system behavior or performance should be measured.
TARGET: Provide a command to run, or describe the operation to benchmark.
INPUTS: List representative input data and required setup.
ITERATIONS: Specify warm-up and measured iteration counts.
METRICS: List duration, throughput, memory, or other metrics to report.
ACCEPTANCE: Define expected limits or comparison criteria.
"""


@dataclass
class BenchmarkResult:
    """Paths created by a benchmark specification or generation operation."""

    specification: str
    generated_files: List[str] = field(default_factory=list)


class BenchmarkGenerator:
    """Manage benchmark specifications and generate scripts in a project."""

    def __init__(self, project_root: str, llm_interface=None):
        self.project_root = Path(project_root).expanduser().resolve()
        if not self.project_root.is_dir():
            raise NotADirectoryError("Target project root must be an existing directory")
        self.llm = llm_interface

    @property
    def specification_path(self) -> Path:
        return self.project_root / "benchmark" / "benchmark.pseudo"

    def create_specification(self, content: str = DEFAULT_SPEC, overwrite: bool = False) -> BenchmarkResult:
        """Create the default benchmark folder and editable specification."""
        target = self.specification_path
        if target.exists() and not overwrite:
            return BenchmarkResult(str(target))
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content.rstrip() + "\n", encoding="utf-8")
        return BenchmarkResult(str(target), [str(target.relative_to(self.project_root))])

    def generate(self, overwrite: bool = False) -> BenchmarkResult:
        """Generate benchmark.py from the project's benchmark.pseudo."""
        specification = self.specification_path
        if not specification.is_file():
            raise FileNotFoundError("Create benchmark/benchmark.pseudo first")
        target = self.project_root / "benchmark" / "benchmark.py"
        if target.exists() and not overwrite:
            return BenchmarkResult(str(specification))
        spec_text = specification.read_text(encoding="utf-8").strip()
        generated = self._convert(spec_text) if self.llm is not None else self._default_harness(spec_text)
        target.write_text(generated, encoding="utf-8")
        return BenchmarkResult(str(specification), [str(target.relative_to(self.project_root))])

    def _convert(self, specification: str) -> str:
        prompt = (
            "Generate one runnable Python benchmark program from this specification. "
            "Use argparse, report each measured run and summary statistics, and "
            "return only Python source code. Do not execute destructive commands.\n\n"
            + specification
        )
        code = re.sub(r"^```(?:python)?\s*\n|\n```\s*$", "", self.llm.call(prompt).strip())
        compile(code, "benchmark.py", "exec")
        return code.rstrip() + "\n"

    @staticmethod
    def _default_harness(specification: str) -> str:
        """Provide a useful command timing harness when no LLM is configured."""
        return '''#!/usr/bin/env python3
"""Command timing harness; replace the command with the one in benchmark.pseudo."""
import argparse
import statistics
import sys
import subprocess
import time

def main():
    parser = argparse.ArgumentParser(description="Run repeated command benchmarks")
    parser.add_argument("--command", help="Command to benchmark (alternative to `-- ...`)")
    parser.add_argument("--warmups", type=int, default=1)
    parser.add_argument("--iterations", type=int, default=5)
    if "--" in sys.argv:
        separator = sys.argv.index("--")
        args = parser.parse_args(sys.argv[1:separator])
        command = sys.argv[separator + 1:]
    else:
        args = parser.parse_args()
        command = args.command.split() if args.command else []
    if not command:
        parser.error("provide the command after `--`, or use --command")
    if args.warmups < 0 or args.iterations < 1:
        parser.error("warmups must be >= 0 and iterations must be >= 1")
    for _ in range(args.warmups):
        subprocess.run(command, check=True)
    durations = []
    for index in range(args.iterations):
        start = time.perf_counter()
        subprocess.run(command, check=True)
        elapsed = time.perf_counter() - start
        durations.append(elapsed)
        print("run {}: {:.6f}s".format(index + 1, elapsed))
    print("mean: {:.6f}s".format(statistics.mean(durations)))
    print("median: {:.6f}s".format(statistics.median(durations)))

if __name__ == "__main__":
    main()
'''


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_root", nargs="?", default=".")
    parser.add_argument("--create-spec", action="store_true")
    parser.add_argument("--generate", action="store_true")
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--use-llm", action="store_true")
    parser.add_argument("--model", default="deepseek-coder:6.7b")
    parser.add_argument("--endpoint", default="http://localhost:11434")
    args = parser.parse_args(argv)
    llm = None
    if args.use_llm:
        from shared.llm import LLMInterface
        llm = LLMInterface(model=args.model, api_endpoint=args.endpoint)
    generator = BenchmarkGenerator(args.project_root, llm)
    if args.create_spec or not args.generate:
        print("Created/preserved: {}".format(generator.create_specification(overwrite=args.overwrite).specification))
    if args.generate:
        result = generator.generate(overwrite=args.overwrite)
        print("Generated: {}".format(", ".join(result.generated_files) or "none"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
