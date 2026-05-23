# Strategic Brain Trust Specs

This folder contains the requirement specification and reference prompts for the **Strategic Brain Trust** — a multi-persona LLM orchestration that helps the user think through complex, ambiguous strategic problems through staged deliberation (first principles → systems → pre-mortem → red team → synthesis).

## Contents

- `requirement_spec.md` — Full functional and architectural requirements.
- `prompts/` — One Markdown file per persona, containing the verbatim system prompt. CLI-agnostic; works with `claude`, `gemini`, or `kiro-cli`.

## Deployment Sketch

1. Choose your LLM CLI provider (see [LLM CLI Choice](requirement_spec.md#7-llm-cli-choice) in the spec). Pick one of:
   - `claude` — Anthropic Claude Code CLI.
   - `gemini` — Google Gemini CLI.
   - `kiro-cli` — Amazon-internal kiro CLI (requires Midway / IDC auth).
2. Create one agent / config per persona using the prompts in `prompts/`. The exact mechanism varies by CLI — see the spec.
3. Build an orchestrator that runs the personas in the linear order, parses persona 1–4 outputs as JSON via Pydantic (or equivalent), and re-loops on `critical[]` non-empty up to a 3-iteration cap.
4. Persist sessions to local JSON. Provide a UI (Streamlit or similar) that lists prior sessions and allows resuming any one of them, with a deep-dive chat after deliberation completes.
