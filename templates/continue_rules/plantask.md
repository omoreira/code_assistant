---
description: R0 — always-first meta rule. Plan and confirm any task before executing, then work one task at a time and evaluate each step. Also carries the global safety and verifiability invariants.
---

rule R0 (highest precedence — applies to every task, before R1–R3): before executing any task, you MUST produce and confirm a plan.

Trigger: every task, without exception. This rule runs before R1, R2, and R3.

Action (MUST):
  1. State the plan: goal, task breakdown, dependencies, resources, and risks.
  2. Prioritize tasks by urgency and importance; execute one task at a time (no multitasking).
  3. Confirm the plan when the task is non-trivial or ambiguous.
  4. After each task, stop and evaluate; gather feedback and adjust the plan.

Output (MUST): show the plan (goal -> tasks -> dependencies -> risks) before acting.
Fallback: for a single, unambiguous edit that needs no understanding, a one-line plan is sufficient — but still state it.

Re-planning (MUST): if scope changes or an unexpected obstacle appears, revise and restate the plan.

Global invariants (apply to all rules R0–R3):
- Secrets (MUST NOT transmit): API keys, access tokens, passwords, .env contents, credentials, private keys, and personal data. Send only the minimum source code and context a task requires.
- Verifiability (MUST): when a rule fires, state which rule fired and the artifact it produced; when a rule's trigger does NOT apply, say so explicitly rather than staying silent.
- Fallbacks (MUST): if a required script is missing or fails, say so and proceed; never silently skip a rule.
