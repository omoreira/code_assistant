"""Turn long research notes into a structured pseudocode document.

Notes are read from text or Markdown files, summarized in bounded chunks, and
combined into a project-relative ``patch.pseudo`` compatible specification.
An LLM is injected by the caller so this module does not choose a provider.
"""

from pathlib import Path
from typing import Iterable, List, Optional


class LongContextReader:
    """Read research notes and use an LLM interface to draft pseudocode."""

    def __init__(self, llm_interface, chunk_chars: int = 12000):
        if chunk_chars < 1000:
            raise ValueError("chunk_chars must be at least 1000")
        self.llm = llm_interface
        self.chunk_chars = chunk_chars

    def read_notes(self, paths: Iterable[str]) -> str:
        """Read and combine UTF-8 note files, preserving their filenames."""
        documents = []
        for filename in paths:
            path = Path(filename)
            documents.append("# Research note: {}\n\n{}".format(
                path.name, path.read_text(encoding="utf-8")
            ))
        if not documents:
            raise ValueError("At least one research note is required")
        return "\n\n".join(documents)

    def _chunks(self, text: str) -> List[str]:
        """Split notes at paragraph boundaries where possible."""
        chunks: List[str] = []
        current = ""
        for paragraph in text.split("\n\n"):
            while len(paragraph) > self.chunk_chars:
                if current:
                    chunks.append(current)
                    current = ""
                chunks.append(paragraph[:self.chunk_chars])
                paragraph = paragraph[self.chunk_chars:]
            candidate = (current + "\n\n" + paragraph).strip()
            if len(candidate) > self.chunk_chars and current:
                chunks.append(current)
                current = paragraph
            else:
                current = candidate
        if current:
            chunks.append(current)
        return chunks

    def create_pseudocode(
        self,
        notes: str,
        output_path: Optional[str] = None,
        docker_support: Optional[bool] = None,
    ) -> str:
        """Generate a patch.pseudo document from notes and optionally save it.

        The output follows ``#PATCHES`` / ``#NEW SCRIPTS``. Existing-script
        changes must be unified diffs under ``## relative/path`` entries;
        new files contain their full source under the same headers.
        """
        chunks = self._chunks(notes)
        summaries = []
        for number, chunk in enumerate(chunks, start=1):
            summaries.append(self.llm.call(
                "Extract implementation requirements, constraints, relevant "
                "file names, and unresolved questions from research notes. "
                "Do not invent details. This is chunk {}/{}:\n\n{}".format(
                    number, len(chunks), chunk
                ),
                temperature=0.2,
            ))
        if docker_support is True:
            docker_instruction = (
                "Docker support was selected: include Dockerfile and .dockerignore. "
            )
        elif docker_support is False:
            docker_instruction = "Docker support was declined: do not include Docker files. "
        else:
            docker_instruction = (
                "Include Dockerfile and .dockerignore only if the notes request or "
                "select Docker support. "
            )
        prompt = (
            "Convert these research summaries into a patch.pseudo specification. "
            "Return exactly two sections: #PATCHES and #NEW SCRIPTS. Under each, "
            "use ## project/relative/path headers. For existing files, produce "
            "valid unified diff hunks with context. For new files, provide the "
            "complete file contents. Do not include markdown fences. If no "
            "existing-file edits are required, leave #PATCHES empty.\n\n"
            "When the research describes creating a new repository, use this "
            "architecture principle: separate user-designed tasks into their own "
            "packages under src/, and keep cross-cutting shared utilities and "
            "tools in shared packages. Include common top-level docs/, scripts/, "
            "config/, and src/ structure, plus src/shared/ and src/tools/ as "
            "appropriate. Derive package names only from modules described by "
            "the user; do not copy this assistant's module names or invent a "
            "fixed module list. Include setup.py and pyproject.toml as default "
            "new repository files. " + docker_instruction + "If the notes do "
            "not identify the user-designed modules, record that as an open "
            "question instead of guessing. For packages that need to exist in "
            "the scaffold, include __init__.py so their directories are created.\n\n"
            + "\n\n--- Summary ---\n\n".join(summaries)
        )
        pseudocode = self.llm.call(prompt, temperature=0.2)
        if output_path:
            Path(output_path).write_text(pseudocode.rstrip() + "\n", encoding="utf-8")
        return pseudocode

    def create_from_files(
        self,
        paths: Iterable[str],
        output_path: str = "patch.pseudo",
        docker_support: Optional[bool] = None,
    ) -> str:
        """Read note files and save their generated patch pseudocode."""
        return self.create_pseudocode(
            self.read_notes(paths), output_path, docker_support=docker_support
        )


def main(argv=None) -> int:
    """CLI entry point used by ``scripts/longtext2pseudo``."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Convert long research notes into patch.pseudo"
    )
    parser.add_argument("input", help="Research note file (UTF-8 text or Markdown)")
    parser.add_argument("-o", "--output", default="patch.pseudo", help="Output file")
    parser.add_argument("--model", default="deepseek-coder:6.7b", help="Ollama model")
    parser.add_argument(
        "--endpoint", default="http://localhost:11434", help="Ollama API endpoint"
    )
    docker_group = parser.add_mutually_exclusive_group()
    docker_group.add_argument(
        "--docker", dest="docker_support", action="store_true",
        help="Include Dockerfile and .dockerignore for a new repository",
    )
    docker_group.add_argument(
        "--no-docker", dest="docker_support", action="store_false",
        help="Exclude Docker files from a new repository",
    )
    parser.set_defaults(docker_support=None)
    args = parser.parse_args(argv)
    from shared.llm import LLMInterface

    llm = LLMInterface(model=args.model, api_endpoint=args.endpoint)
    LongContextReader(llm).create_from_files(
        [args.input], args.output, docker_support=args.docker_support
    )
    print("Wrote pseudocode patch to {}".format(args.output))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
