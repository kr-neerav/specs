# Strategic Brain Trust — Persona Prompts

Each file in this folder is the verbatim system prompt for one persona. The reference implementation is hosted as **kiro-cli agent configs** (`.kiro/agents/sbt-*.json`), but the prompts are CLI-agnostic — they work as system prompts for `claude` (Anthropic), `gemini` (Google), `kiro-cli` (Amazon internal), or any LLM that supports JSON-mode / structured-output guidance.

## Files

| Order | File | Stage |
|---|---|---|
| 1 | `01-sbt-first-principles.md` | Decompose the problem into core assumptions and first-order effects |
| 2 | `02-sbt-systems-thinker.md` | Surface second-order effects and unintended consequences |
| 3 | `03-sbt-pre-mortem.md` | Imagine 12-month-out failure; pair failures with mitigations |
| 4 | `04-sbt-red-teamer.md` | Triage critique into Critical / Important / Minor |
| 5 | `05-sbt-synthesizer.md` | Compose the final Markdown strategy |
| — | `06-sbt-deep-dive.md` | Conversational follow-up after deliberation completes |
| — | `07-sbt-chat-summarizer.md` | Compresses older deep-dive turns into a running summary |

## Output contract reminder

Personas 1–4 must emit **strict JSON only** (no prose, no markdown fences, no preamble). Persona 5 emits **Markdown only**. Personas 6–7 are conversational (Markdown / plain text).

The orchestrator parses persona 1–4 outputs with Pydantic and treats validation failures as empty payloads — the deliberation continues but downstream personas get less to work with. Test prompts against the chosen LLM CLI before adopting; some models need additional "respond with JSON only" framing to honor the contract reliably.

## Schema summary

| Persona | Fields |
|---|---|
| First-Principles | `core_assumptions[]`, `first_order_effects[]` |
| Systems | `second_order_effects[]`, `unintended_consequences[]` |
| Pre-Mortem | `failure_modes[]`, `mitigation_strategies[]` (index-aligned) |
| Red Team | `critical[]`, `important[]`, `minor[]` |
| Synthesizer | Markdown with required H2 sections (see file 05) |
