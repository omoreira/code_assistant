# UI Builder

`ui_builder` creates a starter application under the target repository's root
`ui/` directory. It supports Streamlit and React + TypeScript.

## Python API

```python
from ui_builder import UIBuilder

result = UIBuilder("/path/to/new_assistant").build(
    "A dashboard for tracking research projects",
    framework="streamlit",
)
print(result.created)
print(result.skipped)
```

Pass `framework="react-typescript"` for the React + TypeScript/Vite template.
Generated files that already exist are skipped unless `overwrite=True` is
passed. An optional `shared.llm.LLMInterface` can generate the primary
application component from the description.

## CLI

```bash
assistant-ui-builder /path/to/new_assistant \
  --framework react-typescript \
  --description "A dashboard for tracking research projects"
```

Add `--use-llm` to generate the main component with the configured local
Ollama service. Use `--overwrite` only when you intend to replace generated UI
files.
