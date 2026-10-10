---
description: R2 — deep reasoning. Use for design tradeoffs, architecture, strategy, plan critique, and ambiguous requirements — questions NOT grounded in a specific file.
---

rule R2 (deep reasoning): when a task needs deep reasoning not grounded in specific code, run `{{OLLAMA_BIN}}/ask_local_reasoner.sh --json --model {{REASONER_MODEL}} "<focused question>"` in the terminal and use its output in your answer.

Trigger: the question is not localized to a file — design tradeoffs, architecture, strategy, plan or approach critique, ambiguous requirements, or complex logic that spans the system.
Does NOT fire for: a task grounded in a specific file (use R1), or a single, unambiguous edit that needs no understanding. Say so explicitly when it does not apply.

Action (MUST): run the reasoner with `--json` and a focused, single-purpose question. Read the JSON envelope on stdout — success is `ok:true` with `exit:0`; use the `answer` field.
Order: if R1 also applies (reasoning grounded in code), run R1 first and feed its output into R2.

Output (MUST): state that R2 ran, the exact focused question, and use the envelope's `answer` in your answer (cite `model` / `latency_ms` when useful).
Fallback (MUST): if the script is missing, exits non-zero (2/3/4/5), or returns `ok:false`, say so and continue; never silently skip. Require a non-empty `answer` with `ok:true` before using its output.

Safety: the R0 global invariants apply — never transmit secrets.
