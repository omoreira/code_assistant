# Continue hybrid-agent rule templates

Templates for the Continue (VS Code) hybrid coding-assistant rules (R0–R3).
Placeholders are filled in by `scripts/setup_hybrid_continue.sh`:

- `{{OLLAMA_BIN}}`          - dir containing the wrapper scripts
- `{{ANALYZER_MODEL}}`      - R1 analyzer model
- `{{REASONER_MODEL}}`      - R2 reasoner model
- `{{CODE_ASSISTANT_ROOT}}` - this repo's root (for R3 helper-script paths)

Install automatically:

    scripts/setup_hybrid_continue.sh           # interactive
    scripts/setup_hybrid_continue.sh --yes     # non-interactive defaults

or copy these files into `~/.continue/rules/` and edit the placeholders by hand.
Existing rules are backed up to `~/.continue/rules/.backup-<timestamp>/`.
