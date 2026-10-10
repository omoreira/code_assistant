# Continue hybrid-agent rule templates

Templates for the Continue (VS Code) hybrid coding-assistant rules (R0–R3).
Placeholders are filled in by `scripts/setup_hybrid_continue.sh`:

- `{{OLLAMA_BIN}}`          - dir containing the wrapper scripts
- `{{ANALYZER_MODEL}}`      - R1 analyzer model
- `{{REASONER_MODEL}}`      - R2 reasoner model
- `{{CODE_ASSISTANT_ROOT}}` - this repo's root (for R3 helper-script paths)

The model placeholders default to the shared LLM resolver
(`config/defaults.yaml` overridden by the environment): the `analysis` role →
`{{ANALYZER_MODEL}}`, the `reasoning` role → `{{REASONER_MODEL}}`. Override with
`--analyzer-model` / `--reasoner-model`, the `LLM_ANALYSIS_MODEL` /
`LLM_REASONING_MODEL` env vars, or the config file. `--write-config` also renders
a Continue `config.yaml` (models); API keys are referenced by environment-variable
name only and never written.

Install automatically:

    scripts/setup_hybrid_continue.sh                       # interactive
    scripts/setup_hybrid_continue.sh --yes                 # non-interactive defaults
    scripts/setup_hybrid_continue.sh --yes --write-config  # also write Continue config.yaml

or copy these files into `~/.continue/rules/` and edit the placeholders by hand.
Existing rules are backed up to `~/.continue/rules/.backup-<timestamp>/`.
