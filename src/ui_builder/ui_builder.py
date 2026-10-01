"""Generate a basic Streamlit or React + TypeScript UI in a target repo."""

import argparse
import html
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class UIBuildResult:
    """Files created or skipped by a UI build operation."""

    framework: str
    output_dir: str
    created: List[str] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)


class UIBuilder:
    """Create a starter UI inside ``<project_root>/ui``.

    Existing files are preserved by default. Set ``overwrite=True`` to replace
    files owned by the selected template. An optional LLM interface can create
    the main application component from the user's description.
    """

    FRAMEWORKS = {"streamlit", "react-typescript"}

    def __init__(self, project_root: str, llm_interface=None):
        self.project_root = Path(project_root).resolve()
        if not self.project_root.is_dir():
            raise NotADirectoryError("Target project root must be an existing directory")
        self.llm = llm_interface

    def build(
        self,
        description: str,
        framework: str = "streamlit",
        overwrite: bool = False,
    ) -> UIBuildResult:
        """Generate the selected UI starter and return per-file results."""
        framework = framework.strip().lower()
        if framework in ("react", "react+typescript", "react_typescript", "react-ts"):
            framework = "react-typescript"
        if framework not in self.FRAMEWORKS:
            raise ValueError("framework must be 'streamlit' or 'react-typescript'")
        if not description.strip():
            raise ValueError("A short description of the application is required")

        files = (
            self._streamlit_files(description)
            if framework == "streamlit"
            else self._react_files(description)
        )
        output_candidate = self.project_root / "ui"
        if output_candidate.is_symlink():
            raise ValueError("Target ui directory must not be a symlink")
        output_dir = output_candidate.resolve()
        self._ensure_within_project(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        result = UIBuildResult(framework=framework, output_dir=str(output_dir))
        for relative_path, content in files.items():
            target = (output_dir / relative_path).resolve()
            self._ensure_within_project(target)
            try:
                target.relative_to(output_dir)
            except ValueError as exc:
                raise ValueError("Generated UI file escapes the target ui directory") from exc
            if target.exists() and not overwrite:
                result.skipped.append(str(target.relative_to(self.project_root)))
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
            result.created.append(str(target.relative_to(self.project_root)))
        return result

    def _ensure_within_project(self, path: Path) -> None:
        try:
            path.relative_to(self.project_root)
        except ValueError as exc:
            raise ValueError("Generated UI path escapes the target project") from exc

    def _generate_component(
        self, description: str, language: str, framework: str
    ) -> Optional[str]:
        if self.llm is None:
            return None
        prompt = (
            "Create a small, runnable first version of this application's main UI. "
            "Use {} source compatible with {}. Use only the framework and its "
            "standard dependencies; do not add third-party imports.\n"
            "Application requirements:\n{}\n\n"
            "Return only source code, without Markdown fences or explanations."
        ).format(language, framework, description.strip())
        response = self.llm.call(prompt, temperature=0.2, max_tokens=4096)
        response = re.sub(r"^```[A-Za-z0-9_+-]*\s*\n", "", response.strip())
        response = re.sub(r"\n```\s*$", "", response)
        return response.strip() + "\n"

    def _streamlit_files(self, description: str) -> Dict[str, str]:
        app = self._generate_component(description, "Python", "Streamlit")
        if not app:
            title = json.dumps(self.project_root.name.replace("_", " ").title())
            summary = json.dumps(description.strip())
            app = '''"""Generated Streamlit application starter."""

import streamlit as st

st.set_page_config(page_title={title}, layout="wide")
st.title({title})
st.write({summary})

# TODO: Add the application workflow described above.
'''.format(title=title, summary=summary)
        return {
            "app.py": app,
            "requirements.txt": "streamlit>=1.30\n",
            "README.md": (
                "# Streamlit UI\n\n"
                "Generated UI for `{}`. From this directory, run:\n\n"
                "```bash\npython -m pip install -r requirements.txt\n"
                "streamlit run app.py\n```\n"
            ).format(self.project_root.name),
        }

    def _react_files(self, description: str) -> Dict[str, str]:
        component = self._generate_component(
            description, "TSX / React + TypeScript", "Vite"
        )
        if not component:
            label = json.dumps(description.strip())
            component = '''export default function App() {
  return (
    <main className="app-shell">
      <h1>{%s}</h1>
      <p>Application interface starter. Replace this content with the planned workflow.</p>
    </main>
  );
}
''' % label
        package_name = re.sub(r"[^a-z0-9-]+", "-", self.project_root.name.lower()).strip("-") or "project-ui"
        return {
            "package.json": json.dumps({
                "name": package_name + "-ui",
                "private": True,
                "version": "0.1.0",
                "type": "module",
                "scripts": {
                    "dev": "vite",
                    "build": "tsc --noEmit && vite build",
                    "preview": "vite preview",
                },
                "dependencies": {"react": "^18.3.0", "react-dom": "^18.3.0"},
                "devDependencies": {
                    "@types/react": "^18.3.0",
                    "@types/react-dom": "^18.3.0",
                    "@vitejs/plugin-react": "^4.3.0",
                    "typescript": "^5.5.0",
                    "vite": "^5.4.0",
                },
            }, indent=2) + "\n",
            "index.html": '''<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{}</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
'''.format(html.escape(self.project_root.name)),
            "tsconfig.json": json.dumps({
                "compilerOptions": {
                    "target": "ES2020", "useDefineForClassFields": True,
                    "lib": ["ES2020", "DOM", "DOM.Iterable"],
                    "module": "ESNext", "skipLibCheck": True,
                    "moduleResolution": "Bundler", "allowImportingTsExtensions": True,
                    "resolveJsonModule": True, "isolatedModules": True,
                    "noEmit": True, "jsx": "react-jsx", "strict": True,
                },
                "include": ["src"],
            }, indent=2) + "\n",
            "vite.config.ts": '''import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({ plugins: [react()] });
''',
            "src/main.tsx": '''import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import App from "./App";
import "./index.css";

createRoot(document.getElementById("root")!).render(
  <StrictMode><App /></StrictMode>,
);
''',
            "src/App.tsx": component,
            "src/index.css": '''* { box-sizing: border-box; }
body { margin: 0; font-family: system-ui, sans-serif; color: #172033; background: #f5f7fb; }
.app-shell { max-width: 960px; margin: 0 auto; padding: 3rem 1.5rem; }
''',
            "README.md": (
                "# React + TypeScript UI\n\nGenerated interface for: {}\n\n"
                "```bash\nnpm install\nnpm run dev\n```\n"
            ).format(description.strip()),
        }


def main(argv=None) -> int:
    """CLI entry point for building a target project's UI."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_root", nargs="?", default=".")
    parser.add_argument(
        "--framework", choices=sorted(UIBuilder.FRAMEWORKS), default="streamlit"
    )
    parser.add_argument("--description", required=True, help="Describe the app to create")
    parser.add_argument(
        "--overwrite", action="store_true", help="Replace generated UI files"
    )
    parser.add_argument(
        "--use-llm", action="store_true",
        help="Generate the main component with local Ollama",
    )
    parser.add_argument("--model", default="deepseek-coder:6.7b")
    parser.add_argument("--endpoint", default="http://localhost:11434")
    args = parser.parse_args(argv)
    llm = None
    if args.use_llm:
        from shared.llm import LLMInterface
        llm = LLMInterface(model=args.model, api_endpoint=args.endpoint)
    result = UIBuilder(args.project_root, llm_interface=llm).build(
        args.description, framework=args.framework, overwrite=args.overwrite
    )
    print("Created: {}".format(", ".join(result.created) or "none"))
    print("Skipped existing: {}".format(", ".join(result.skipped) or "none"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
