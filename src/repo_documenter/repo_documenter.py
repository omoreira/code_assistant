"""Generate or refresh Markdown documentation for a target repository."""

import argparse
import ast
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


SKIP_DIRECTORIES = {
    ".git", ".venv", "venv", "node_modules", "__pycache__", "build",
    "dist", ".pytest_cache", ".mypy_cache", ".tox",
}


@dataclass
class DocumentationResult:
    """Files written, refreshed, or preserved by a documentation run."""

    output_dir: str
    created: List[str] = field(default_factory=list)
    updated: List[str] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)


class RepoDocumenter:
    """Document a target repo's Python packages into its root ``docs/`` folder.

    Generates a docs index, architecture overview, API inventory, and one
    overview per package under ``src/``. Existing documents are preserved
    unless ``update_existing=True`` is explicitly requested.
    """

    def __init__(self, project_root: str, llm_interface=None):
        self.project_root = Path(project_root).resolve()
        if not self.project_root.is_dir():
            raise NotADirectoryError("Target project root must be an existing directory")
        self.llm = llm_interface

    def scan_project(self) -> Dict[str, object]:
        """Collect package names and public top-level Python symbols via AST."""
        src_root = self.project_root / "src"
        packages: Dict[str, Dict[str, object]] = {}
        python_files: List[str] = []
        if src_root.is_symlink() and not self._is_within_project(src_root.resolve()):
            raise ValueError("Target src directory must stay within project_root")
        if src_root.is_dir():
            for package_dir in sorted(src_root.iterdir()):
                if not package_dir.is_dir() or package_dir.name.startswith("."):
                    continue
                if not self._is_within_project(package_dir.resolve()):
                    continue
                if package_dir.name in SKIP_DIRECTORIES:
                    continue
                init_file = package_dir / "__init__.py"
                if not init_file.is_file():
                    continue
                if not self._is_within_project(init_file.resolve()):
                    continue
                package_info: Dict[str, object] = {
                    "description": ast.get_docstring(
                        self._parse_python(init_file)
                    ) or "",
                    "files": [],
                    "symbols": [],
                    "parse_errors": [],
                }
                for source in sorted(package_dir.rglob("*.py")):
                    if any(part in SKIP_DIRECTORIES for part in source.parts):
                        continue
                    if not self._is_within_project(source.resolve()):
                        continue
                    relative = source.relative_to(self.project_root).as_posix()
                    python_files.append(relative)
                    package_info["files"].append(relative)
                    try:
                        tree = ast.parse(source.read_text(encoding="utf-8"))
                    except (OSError, UnicodeError, SyntaxError) as exc:
                        package_info["parse_errors"].append("{}: {}".format(relative, exc))
                        continue
                    for node in tree.body:
                        if isinstance(
                            node,
                            (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef),
                        ):
                            if not node.name.startswith("_"):
                                package_info["symbols"].append({
                                    "name": node.name,
                                    "kind": (
                                        "class" if isinstance(node, ast.ClassDef)
                                        else "function"
                                    ),
                                    "file": relative,
                                    "description": ast.get_docstring(node) or "",
                                })
                packages[package_dir.name] = package_info
        return {
            "project_name": self.project_root.name,
            "packages": packages,
            "python_files": sorted(set(python_files)),
        }

    @staticmethod
    def _parse_python(path: Path) -> ast.Module:
        try:
            return ast.parse(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, SyntaxError):
            return ast.Module(body=[], type_ignores=[])

    def _is_within_project(self, path: Path) -> bool:
        try:
            path.relative_to(self.project_root)
            return True
        except ValueError:
            return False

    def _docs_root(self) -> Path:
        docs_candidate = self.project_root / "docs"
        if docs_candidate.is_symlink():
            raise ValueError("Target docs directory must not be a symlink")
        docs_root = docs_candidate.resolve()
        if not self._is_within_project(docs_root):
            raise ValueError("Target docs directory must stay within project_root")
        return docs_root

    def _render_documents(self, facts: Dict[str, object]) -> Dict[str, str]:
        project_name = str(facts["project_name"])
        packages = facts["packages"]
        assert isinstance(packages, dict)
        package_names = sorted(packages)

        docs_index = "# {} Documentation\n\n".format(project_name)
        docs_index += (
            str(facts.get("description") or "Generated documentation for this repository.")
            + "\n\n"
        )
        docs_index += "- [Architecture](ARCHITECTURE.md)\n- [API inventory](API.md)\n"
        docs_index += "\n## Packages\n\n"
        for name in package_names:
            docs_index += "- [{}](./{}/README.md)\n".format(name, name)

        architecture = "# {} Architecture\n\n".format(project_name)
        architecture += (
            "This overview is based on the repository's current Python package "
            "layout under `src/`.\n\n## Package responsibilities\n\n"
        )
        for name in package_names:
            info = packages[name]
            description = (
                str(info["description"]).strip()
                or "Responsibility not documented yet."
            )
            architecture += "### `{}`\n\n{}\n\n".format(name, description)
        architecture += "## Source inventory\n\n"
        for path in facts["python_files"]:
            architecture += "- `{}`\n".format(path)

        api = "# {} API Inventory\n\n".format(project_name)
        api += (
            "Public top-level Python classes and functions found by static AST "
            "inspection.\n"
        )
        symbol_count = 0
        for name in package_names:
            symbols = packages[name]["symbols"]
            if not symbols:
                continue
            api += "\n## `{}`\n".format(name)
            for symbol in symbols:
                symbol_count += 1
                api += "\n### `{}` ({})\n\n".format(symbol["name"], symbol["kind"])
                api += "Defined in `{}`.\n".format(symbol["file"])
                if symbol["description"]:
                    api += "\n{}\n".format(symbol["description"])
        if not symbol_count:
            api += "\nNo public top-level classes or functions were found.\n"

        output = {
            "README.md": docs_index,
            "ARCHITECTURE.md": architecture,
            "API.md": api,
        }
        for name in package_names:
            info = packages[name]
            content = "# `{}`\n\n".format(name)
            content += str(info["description"]).strip() or "Package overview not documented yet."
            content += "\n\n## Python files\n\n"
            for path in info["files"]:
                content += "- `{}`\n".format(path)
            output["{}/README.md".format(name)] = content
        return output

    def _llm_update(
        self, relative_path: str, previous: str, facts: Dict[str, object]
    ) -> str:
        prompt = (
            "Update this Markdown document using the current repository facts. "
            "Keep accurate and useful existing content, correct stale statements, "
            "and do not invent APIs or behavior. Return only Markdown.\n\n"
            "Document path: {}\n\nPrevious document:\n{}\n\n"
            "Current source inventory and AST facts:\n{}"
        ).format(relative_path, previous, repr(facts))
        response = self.llm.call(
            prompt, temperature=0.2, max_tokens=6000
        ).strip()
        response = re.sub(r"^```(?:markdown|md)?\s*\n|\n```\s*$", "", response)
        return response.rstrip() + "\n"

    def generate_docs(
        self,
        project_name: Optional[str] = None,
        description: str = "",
        update_existing: bool = False,
    ) -> DocumentationResult:
        """Generate docs, or refresh existing generated docs when requested."""
        facts = self.scan_project()
        if project_name:
            facts["project_name"] = project_name
        if description:
            facts["description"] = description
        documents = self._render_documents(facts)
        docs_root = self._docs_root()
        docs_root.mkdir(parents=True, exist_ok=True)
        result = DocumentationResult(output_dir=str(docs_root))

        for relative_path, generated in documents.items():
            target = (docs_root / relative_path).resolve()
            try:
                target.relative_to(docs_root)
            except ValueError as exc:
                raise ValueError(
                    "Documentation output path escapes target docs directory"
                ) from exc
            if not self._is_within_project(target):
                raise ValueError("Documentation output path escapes target project")
            existed = target.exists()
            if existed and not update_existing:
                result.skipped.append(str(target.relative_to(self.project_root)))
                continue
            if existed and self.llm is not None:
                previous = target.read_text(encoding="utf-8")
                generated = self._llm_update(relative_path, previous, facts)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(generated, encoding="utf-8")
            path = str(target.relative_to(self.project_root))
            (result.updated if existed else result.created).append(path)
        return result


def main(argv=None) -> int:
    """CLI entry point for generating target-project documentation."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_root", nargs="?", default=".")
    parser.add_argument("--name", help="Override the project name in generated docs")
    parser.add_argument("--description", default="")
    parser.add_argument(
        "--update", action="store_true", help="Refresh existing docs"
    )
    parser.add_argument(
        "--use-llm", action="store_true",
        help="Use local Ollama to refresh existing docs",
    )
    parser.add_argument("--model", default="deepseek-coder:6.7b")
    parser.add_argument("--endpoint", default="http://localhost:11434")
    args = parser.parse_args(argv)
    llm = None
    if args.use_llm:
        from shared.llm import LLMInterface
        llm = LLMInterface(model=args.model, api_endpoint=args.endpoint)
    result = RepoDocumenter(args.project_root, llm_interface=llm).generate_docs(
        project_name=args.name,
        description=args.description,
        update_existing=args.update,
    )
    print("Created: {}".format(", ".join(result.created) or "none"))
    print("Updated: {}".format(", ".join(result.updated) or "none"))
    print("Preserved: {}".format(", ".join(result.skipped) or "none"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
