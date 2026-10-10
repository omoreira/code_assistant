# Upstream request: configurable command policy for the agent terminal tool

**Status / where to send:** none. The `continuedev/continue` repository is
read-only ("no longer actively maintained"), Discussions are removed, the
community/Discord links are gone from the README, and Continue was acquired by
Cursor. There is no active recipient, so this is kept as a local record and as
input to any fork. See `docs/building_hybrid_vscode_continue.md` (section 12).

---

Title: Expose a configurable command allow/deny policy for the agent's terminal tool

### Environment
- Continue VS Code extension v2.0.0 (linux-x64)
- OS: Linux Mint 22.3 "Zena" (XFCE, x86_64); based on Ubuntu 24.04 LTS
- Models: mixed (Anthropic + local Ollama)

### Summary
The agent's `run_terminal_command` tool applies a hardcoded command-safety
classifier. Commands classified `critical` are hard-blocked with
"Security Policy Violation / command disabled", and there is no config to
allowlist specific commands. This blocks legitimate, safe automation and cannot
be tuned without editing the shipped bundle.

### Evidence (from the installed v2.0.0 bundle)
- Core classifier in `out/extension.js`:
  - `evaluateSingleCommand()` returns, in order:
    `isCriticalCommand` -> "disabled", else a `$`-prefixed command -> high-risk,
    `isHighRiskCommand` -> "allowedWithPermission",
    `isSafeCommand` -> "allowedWithoutPermission", else "allowedWithPermission".
  - `getMostRestrictive()` composes the results; "disabled" always wins.
  - `isCriticalCommand()` returns true for filesystem-format commands, and for a
    recursive forced delete aimed at a system/root/home path or at sensitive
    system files.
  - `isSafeCommand()` is a fixed read-only list (`ls`, `cat`, `head`, `tail`,
    `wc`, `grep` without `--exec`, `find` without `-exec`/`-delete`, `echo`, ...).
- GUI surfaces the block in `gui/assets/index.js` (a "Security Policy Violation"
  context item, description "Command Disabled").
- The only config surface is `chatOptions.toolOverrides` keyed by tool name
  (e.g. `run_terminal_command`), whose schema (`toolOverrideSchema`) exposes just
  a `disabled` boolean plus cosmetic strings - it cannot allowlist commands.

### Expected behavior
A documented, supported way to tune the command policy, for example:

```yaml
# config.yaml
tools:
  run_terminal_command:
    commandPolicy:
      allowWithoutPermission: ["sed", "awk", "make", "docker compose"]
      requirePermission: ["git push"]
      deny: ["format", "power"]
```

or an external file (e.g. `.continue/command-policy.yaml`) merged over the
defaults, with a per-command `allow | ask | deny` policy.

### Actual behavior
No such config exists. Teams must either avoid common tools (`sed`, `awk`, and
similar) or patch the extension bundle (lost on update, and a security risk).

### Steps to reproduce
1. Ask the agent to run a command the classifier marks critical (for example a
   recursive forced delete, or a filesystem-format command).
2. Observe "Security Policy Violation / command disabled" with no way to permit it.

### Desired additional change
Expose the terminal command timeout as a setting (long local model calls can
exceed the hardcoded cap; currently the only workaround is running in the
background).

### Alternatives considered
- Per-tool policy in the GUI: per tool, not per command; a `disabled` command
  classification still wins.
- `chatOptions.toolOverrides`: only toggles the tool on/off.

### Additional context
Some installs appear to enforce a stricter-than-stock policy (same message),
suggesting an enterprise/admin layer. A first-class, documented policy config
would cover both cases.
