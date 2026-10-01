# Repository Documenter

`repo_documenter` scans Python packages under a target project's `src/` and
writes documentation under its root `docs/` directory. It creates a docs
index, architecture overview, API inventory, and one package overview per
package containing `__init__.py`.

## Python API

```python
from repo_documenter import RepoDocumenter

result = RepoDocumenter("/path/to/new_assistant").generate_docs(
    project_name="Research Assistant",
    description="Tools for organizing research projects.",
)
print(result.created)
print(result.skipped)
```

Existing documents are preserved by default. Set `update_existing=True` to
refresh generated documentation. Provide `shared.llm.LLMInterface` to use the
LLM to update existing prose; without an LLM, updates use the deterministic
static source inventory.

## CLI

```bash
assistant-repo-documenter /path/to/new_assistant \
  --name "Research Assistant" \
  --description "Tools for organizing research projects."
```

Pass `--update` to refresh existing docs. Add `--use-llm` to ask local Ollama
to retain and update existing prose using the current source inventory.
