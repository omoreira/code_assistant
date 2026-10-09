"""Convert a single pseudocode-bearing file into real code for its language.

A "code-devoided" file keeps the shape of a module - its name, docstrings, and
structural notes - but replaces runnable statements with pseudocode. This module
hands that text to an injected LLM and writes back the real code for the file's
extension (for example a ``.py`` file becomes Python).

The LLM is injected by the caller so this module does not choose a provider; see
``LongContextReader`` for the sibling pattern.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Optional

# Extensions we know how to name in a prompt. Keys are lower-case suffixes.
EXTENSION_LANGUAGES = {
    ".py": "Python",
    ".pyi": "Python stub",
    ".js": "JavaScript",
    ".mjs": "JavaScript",
    ".cjs": "JavaScript",
    ".jsx": "JavaScript (React)",
    ".ts": "TypeScript",
    ".tsx": "TypeScript (React)",
    ".java": "Java",
    ".kt": "Kotlin",
    ".go": "Go",
    ".rs": "Rust",
    ".rb": "Ruby",
    ".php": "PHP",
    ".cs": "C#",
    ".c": "C",
    ".h": "C header",
    ".cpp": "C++",
    ".hpp": "C++ header",
    ".sh": "POSIX shell",
    ".sql": "SQL",
}


def language_for_path(path) -> str:
    """Return a prompt-friendly language name for ``path``'s extension.

    Raises:
        ValueError: if the file has no extension or the extension is unsupported.
    """
    suffix = Path(path).suffix.lower()
    if not suffix:
        raise ValueError("File has no extension: {}".format(path))
    try:
        return EXTENSION_LANGUAGES[suffix]
    except KeyError:
        raise ValueError(
            "Unsupported extension '{}'. Known extensions: {}".format(
                suffix, ", ".join(sorted(EXTENSION_LANGUAGES))
            )
        )


def strip_code_fences(text: str) -> str:
    """Remove a surrounding Markdown code fence if the model added one."""
    stripped = text.strip()
    if not stripped.startswith("```"):
        return stripped
    lines = stripped.splitlines()
    if lines[0].startswith("```"):
        lines = lines[1:]
    if lines and lines[-1].strip() == "```":
        lines = lines[:-1]
    return "\n".join(lines).strip("\n")


class PseudofileConverter:
    """Convert one pseudocode file into real code using an injected LLM."""

    def __init__(self, llm_interface):
        self.llm = llm_interface

    def read_pseudocode(self, path: str) -> str:
        """Read a UTF-8 pseudocode file, rejecting empty input."""
        text = Path(path).read_text(encoding="utf-8")
        if not text.strip():
            raise ValueError("Pseudocode file is empty: {}".format(path))
        return text

    def convert(self, pseudocode: str, language: str) -> str:
        """Turn pseudocode into runnable ``language`` source code."""
        if not pseudocode.strip():
            raise ValueError("No pseudocode supplied to convert")
        prompt = (
            "Convert the following pseudocode into a single runnable {language} "
            "file. Preserve any docstrings and the intended structure, fill in "
            "real implementations, and follow {language} best practices. Return "
            "only the source code, without Markdown fences or commentary.\n\n"
            "{pseudocode}"
        ).format(language=language, pseudocode=pseudocode)
        code = self.llm.call(prompt, temperature=0.2)
        return strip_code_fences(code).rstrip() + "\n"

    def convert_file(self, input_path: str, output_path: Optional[str] = None) -> str:
        """Convert one file and return the path that was written.

        When ``output_path`` is omitted the input file is overwritten in place.
        """
        source = Path(input_path)
        language = language_for_path(source)
        code = self.convert(self.read_pseudocode(str(source)), language)
        destination = Path(output_path) if output_path else source
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(code, encoding="utf-8")
        return str(destination)


def main(argv=None) -> int:
    """CLI entry point: convert one pseudocode file to real code."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", help="Pseudocode-bearing source file")
    parser.add_argument(
        "-o", "--output", help="Output path (default: overwrite the input file)"
    )
    parser.add_argument("--model", default="qwen3:14b", help="Ollama model to use")
    parser.add_argument(
        "--endpoint", default="http://localhost:11434", help="Ollama API endpoint"
    )
    args = parser.parse_args(argv)
    from shared.llm import LLMInterface

    llm = LLMInterface(model=args.model, api_endpoint=args.endpoint)
    written = PseudofileConverter(llm).convert_file(args.input, args.output)
    print("Wrote converted code to {}".format(written))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
