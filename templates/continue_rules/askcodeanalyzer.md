---
description: R1 — code analysis. Use for debugging, explaining behavior, reviewing diffs, or tracing data flow — any question grounded in specific files.
---

rule R1 (code analysis): when a task involves analyzing code, run `{{OLLAMA_BIN}}/ask_local_analyzer.sh --json --model {{ANALYZER_MODEL}} "<focused question>"` in the terminal and use its output in your answer.

Trigger: the question is grounded in code — debugging, explaining runtime or design behavior, reviewing a diff, tracing data flow or call chains, answering "why does X happen", or assessing structure and patterns in specific files.
Does NOT fire for: a single, unambiguous edit that needs no understanding, or reasoning with no file basis (use R2). Say so explicitly when it does not apply.

Action (MUST): run the analyzer with `--json` and a focused, single-purpose question. Read the JSON envelope on stdout — success is `ok:true` with `exit:0`; use the `answer` field. (Optional: `{{OLLAMA_BIN}}/ask_local_analyzer.sh --stats` shows recent run stats.)
Order: run R1 before R2 when both apply; feed R1's output into R2.

Output (MUST): state that R1 ran, the exact focused question, and quote or summarize the envelope's `answer` (cite `model` / `latency_ms` when useful).
Fallback (MUST): if the script is missing, exits non-zero (2 usage / 3 environment / 4 upstream / 5 invalid), or returns `ok:false`, say so and continue with a clearly labeled manual analysis; never silently skip. Require a non-empty `answer` with `ok:true` before using its output.
Safety: the R0 global invariants apply — never transmit secrets; send only the minimum source code and context.
