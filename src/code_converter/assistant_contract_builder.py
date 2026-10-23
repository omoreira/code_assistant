"""Build a JSON assistant contract from requirements and output examples."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable, List, Optional


class AssistantContractBuilder:
    """Extract obligations and output conventions with an injected LLM."""

    def __init__(self, llm_interface):
        self.llm = llm_interface

    @staticmethod
    def read_requirements(path: str) -> str:
        """Read a UTF-8 plain-text or Markdown requirements file."""
        source = Path(path)
        if source.suffix.lower() not in (".txt", ".md", ".markdown"):
            raise ValueError("Requirements file must be .txt, .md, or .markdown")
        text = source.read_text(encoding="utf-8")
        if not text.strip():
            raise ValueError("Requirements file is empty: {}".format(source))
        return text

    @staticmethod
    def read_examples(directory: str) -> List[str]:
        """Read non-empty UTF-8 example files recursively in stable order."""
        root = Path(directory)
        if not root.is_dir():
            raise ValueError("Examples directory does not exist: {}".format(root))
        examples = []
        for path in sorted(p for p in root.rglob("*") if p.is_file()):
            try:
                content = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            if content.strip():
                examples.append(
                    "### Example: {}\n{}".format(path.relative_to(root), content)
                )
        if not examples:
            raise ValueError("No non-empty UTF-8 examples found in {}".format(root))
        return examples

    @staticmethod
    def _parse_json(response: str) -> dict:
        """Parse a JSON object, tolerating fences and surrounding commentary."""
        text = response.strip()
        if not text:
            raise ValueError("LLM returned an empty response")
        if text.startswith("```"):
            lines = text.splitlines()
            if lines and lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            text = "\n".join(lines).strip()
        decoder = json.JSONDecoder()
        value = None
        last_error = None
        for start in [0] + [index for index, char in enumerate(text) if char == "{"]:
            try:
                candidate, _ = decoder.raw_decode(text, start)
            except json.JSONDecodeError as exc:
                last_error = exc
                continue
            if isinstance(candidate, dict):
                value = candidate
                break
        if value is None:
            detail = str(last_error) if last_error else "no JSON object found"
            preview = text[:160].replace("\n", " ")
            raise ValueError(
                "LLM response did not contain valid JSON ({}). Response starts: {!r}".format(
                    detail, preview
                )
            )
        required = ("rules", "obligations", "output_contract", "open_questions")
        missing = [key for key in required if key not in value]
        if missing:
            raise ValueError("Contract JSON is missing keys: {}".format(", ".join(missing)))
        if not isinstance(value["rules"], list) or not isinstance(value["obligations"], list):
            raise ValueError("Contract 'rules' and 'obligations' must be arrays")
        if not isinstance(value["output_contract"], dict):
            raise ValueError("Contract 'output_contract' must be an object")
        if not isinstance(value["open_questions"], list):
            raise ValueError("Contract 'open_questions' must be an array")
        return value

    def create_contract(self, requirements: str, examples: Iterable[str]) -> dict:
        """Create a JSON-serializable contract from requirements and examples."""
        if not requirements.strip():
            raise ValueError("Requirements text is empty")
        examples = list(examples)
        if not examples:
            raise ValueError("At least one output example is required")
        prompt = (
            "Create a reusable assistant contract from the requirements and "
            "output examples below. Treat requirements as authoritative. Use "
            "examples only to infer output structure, tone, formatting, and "
            "level of detail. Do not infer new obligations from an example if "
            "it conflicts with the requirements. Mark uncertainty in "
            "open_questions rather than inventing facts. Return only valid JSON, "
            "without Markdown fences, with exactly this top-level structure:\n"
            '{{"rules": [string], "obligations": [string], '
            '"output_contract": {{"format": string, "required_sections": '
            '[string], "style": [string], "validation": [string]}}, '
            '"open_questions": [string]}}\n\n'
            "REQUIREMENTS\n{}\n\nOUTPUT EXAMPLES\n{}"
        ).format(requirements, "\n\n".join(examples))
        response = self.llm.call(prompt, temperature=0.2)
        try:
            return self._parse_json(response)
        except ValueError as first_error:
            if not response.strip():
                raise
            repair_prompt = (
                "Rewrite the following response as valid JSON only. Preserve its "
                "intended information, and ensure the top-level keys are rules, "
                "obligations, output_contract, and open_questions. Do not add "
                "Markdown fences or commentary.\n\nRESPONSE TO REPAIR:\n{}"
            ).format(response)
            try:
                return self._parse_json(self.llm.call(repair_prompt, temperature=0.0))
            except ValueError as repair_error:
                raise ValueError(
                    "LLM did not produce a valid assistant contract after one repair "
                    "attempt: {}".format(repair_error)
                ) from first_error

    def create_from_files(
        self, requirements_path: str, examples_dir: str, output_path: str
    ) -> str:
        """Create and save a formatted JSON contract; return its destination."""
        contract = self.create_contract(
            self.read_requirements(requirements_path), self.read_examples(examples_dir)
        )
        destination = Path(output_path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(
            json.dumps(contract, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        return str(destination)


def main(argv: Optional[List[str]] = None) -> int:
    """CLI entry point for generating an assistant contract."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("requirements", help="UTF-8 .txt or Markdown requirements file")
    parser.add_argument("examples", help="Directory containing output examples")
    parser.add_argument("-o", "--output", default="assistant_contract.json")
    from shared.llm_config import resolve_llm

    defaults = resolve_llm("generation")
    parser.add_argument("--model", default=defaults.model)
    parser.add_argument("--endpoint", default=defaults.base_url)
    args = parser.parse_args(argv)

    from shared.llm import LLMInterface

    llm = LLMInterface(model=args.model, api_endpoint=args.endpoint)
    output = AssistantContractBuilder(llm).create_from_files(
        args.requirements, args.examples, args.output
    )
    print("Wrote assistant contract to {}".format(output))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
