# Requirements Specification: Strategic Brain Trust

## 1. Overview

The Strategic Brain Trust is a **multi-persona LLM orchestration** for strategic deliberation. The user supplies a complex, ambiguous problem (the kind that does not reduce to a spreadsheet); the system runs five specialized "thinking-mode" personas in a fixed order, with a conditional re-loop driven by red-team severity triage, and produces an actionable Markdown synthesis the user can defend in a senior review. After deliberation, the user can continue the conversation through a separate deep-dive chat.

The system is intentionally simple: a linear graph with one back-edge, five personas, and a categorical re-loop signal. It is **CLI-agnostic** — the same prompts can be driven by Claude, Gemini, or Amazon's internal `kiro-cli`.

## 2. Goals (the system serves these)

1. Surface the user's hidden assumptions.
2. Push past first-order thinking to second-order effects.
3. Force a pre-mortem before commitment.
4. Catch motivated reasoning through structured critique.
5. End with an actionable strategy that explicitly states the limits of the reasoning.

## 3. Personas

The system runs five personas in this order (see `prompts/` for verbatim prompts):

| # | Persona | Output type | Key fields |
|---|---|---|---|
| 1 | **First-Principles Thinker** | Strict JSON | `thought_log`, `core_assumptions[]` (with `confidence_level`), `first_order_effects[]` (with `confidence_level`), `addressed_critiques[]` |
| 2 | **Systems Thinker** | Strict JSON | `thought_log`, `second_order_effects[]`, `unintended_consequences[]` |
| 3 | **Pre-Mortem Risk Strategist** | Strict JSON | `insufficient_context`, `insufficient_context_details`, `thought_log`, `risk_clusters[]` |
| 4 | **Red Teamer (Devil's Advocate)** | Strict JSON | `critical[]`, `important[]`, `minor[]`, `has_unresolved_criticals` |
| 5 | **Executive Synthesizer** | Strict JSON | `no_go_triggered`, `formatted_report` (with H2 sections: Executive Summary / Blocking Conflicts (Conditional) / Mental Model / Recommended Strategy / Key Tradeoffs / Watch List / Confidence & Caveats) |

### 3.1 Output Contract

1. Personas 1–5 MUST emit a single JSON object and nothing else (no prose, no markdown fences, no preamble). The First-Principles Thinker includes a `thought_log` scratchpad at the root of the JSON for cognitive scaffolding, tags each assumption/effect with a `confidence_level` (`HIGH`, `MEDIUM`, or `LOW`), and logs resolutions of prior critiques in `addressed_critiques` (list of strings). The orchestrator validates with Pydantic (or equivalent) and treats validation failures as empty payloads. To prevent parser crashes during external tool invocation (e.g., `builder-mcp`), prompts must instruct the agent to run in Schema-Only Mode, strictly suppressing thoughts, preambles, conversational tool narration, or markdown fences outside the JSON object.
2. Persona 5's JSON object contains `no_go_triggered` (boolean) and `formatted_report` (string). It triggers `no_go_triggered: true` if the latest Red Team pass has `"has_unresolved_criticals": true` or if a fatal flaw is discovered.
3. List items in personas 1 and 2 are bounded (3–7 per list) but have no word count constraints. Persona 3 is bounded up to 7 risk clusters with no minimum floor.
4. Persona 4's lists may each be empty. To prevent token-pressure collision and observation eviction, there is no hard limit on the total number of items, but focus should be on high-signal findings. Persona 4 MUST prioritize carrying over all unaddressed critical issues from prior iterations over introducing new minor/important observations. Persona 4 MUST output `"has_unresolved_criticals": true` if there are any critical issues. On the final iteration (turn 3), unresolved critical issues must be documented, prefixed with `[UNRESOLVED CONFLICT]`, and `"has_unresolved_criticals"` set to `true` to signal persistent deadlock to the Synthesizer. Items must point to a SPECIFIC upstream artifact, not generic critique.
5. Persona 5's `formatted_report` contains exact H2 sections in order: Executive Summary, Blocking Conflicts (mandatory only if `no_go_triggered` is true), Mental Model, Recommended Strategy, Key Tradeoffs, Watch List, and Confidence & Caveats. Bullet count constraints in the report are relaxed (e.g., 1-3 bullets for Mental Model based on available signal) to prevent forced hallucinations. If `no_go_triggered` is true, the Synthesizer invokes **Degraded Execution Mode** and designs conditional, risk-containment actions rather than standard forward progress, allowing safe evidence gathering.
6. The First-Principles Thinker prompt abstracts tool implementations, specifying functional capabilities (e.g. "internal search and documentation tools") rather than hardcoding names, and enforces at least one non-technical constraint (economics, psychology, etc.) to prevent perspective homogenization. Bedrock is defined to include socio-technical primitives like human incentives and institutional inertia.
7. **Context Optimization**: To minimize token consumption and maximize efficiency across all LLM systems, the orchestrator MUST strip the `thought_log` reasoning scratchpad field from the upstream JSON payloads before feeding them as context to downstream personas. The `thought_log` is strictly reserved for human review/UI rendering and is not required for downstream agent context.
8. **Memory Vacuum Safeguard**: Because the orchestrator strips upstream `thought_log` reasoning logs, downstream personas (Systems Thinker, Pre-Mortem, Red Teamer) only receive the clean analysis statements and their rationales/mechanisms. Persona 3 (Pre-Mortem) must base failure modes strictly on these visible fields, treating any vague or missing upstream rationale as a distinct risk to be mitigated. Persona 5 (Synthesizer) must compose the final strategy by explicitly linking the documented rationales and flagging any gaps in *Confidence & Caveats*.


### 3.2 Persona Prompts (CLI-agnostic)

The verbatim system prompts live in `prompts/01-…` through `prompts/05-…`. These prompts are written to be portable across LLM CLIs. The orchestrator wraps each invocation with a runtime user message containing:

- The original problem (`PROBLEM:\n…`).
- The upstream personas' validated JSON outputs as context blocks.
- For persona 4 on a re-loop pass: the prior `red_team_critique` history, with explicit instructions not to downgrade still-unaddressed Critical issues.
- For persona 1 on a re-loop pass: an `UNADDRESSED CRITIQUES` block listing every Critical (and Importants flagged optional) from the prior Red Team pass.

## 4. Workflow

```
first_principles → systems_thinker → pre_mortem → red_team
                                                       │
                              critical[] non-empty AND iters < 3?
                                  │                       │
                                 yes                      no
                                  │                       │
                              loop back              synthesizer → END
                              (with prior
                               criticals
                               injected)
```

### 4.1 Severity-Driven Re-Loop

1. The Red Teamer triages every issue into one of three severities:
   - 🔴 **Critical** — Blocking. Without this fix, the synthesis would mislead a senior reviewer. Triggers a re-loop.
   - 🟠 **Important** — A senior engineer would address this; deferral requires a stated tradeoff. Surfaced in the synthesis. Does NOT trigger a re-loop on its own.
   - 🟢 **Minor** — Nice-to-have. Acknowledged in synthesis only if relevant.
2. The orchestrator re-loops to First-Principles iff `critical` is non-empty AND `iterations < MAX_ITERATIONS` (default 3).
3. On re-loop, the next First-Principles prompt MUST include an `UNADDRESSED CRITIQUES` block listing every Critical, with an instruction that the re-analysis must directly address each one.
4. The Red Teamer's prompt MUST forbid quietly downgrading a still-unaddressed Critical to a softer severity on later passes. If a prior Critical wasn't addressed in the upstream analysis, it must be re-listed as Critical.
5. If the iteration cap is hit with Criticals still open, the Synthesizer MUST name each unresolved Critical in Confidence & Caveats and recommend a probe before any irreversible commitment.

### 4.2 Synthesizer's Severity Handling

1. Critical: empty by synthesis time in normal operation. If non-empty (cap hit), each must be named explicitly with a recommended probe.
2. Important: each must be either reflected in Recommended Strategy as a tradeoff OR explained in Confidence & Caveats as a deferred-with-reason.
3. Minor: acknowledge only if relevant; otherwise omit.

## 5. Sessions and UI

### 5.1 Persistence

1. Every session is a single JSON file under `sessions/` named `<timestamp>_<slug>_<id8>.json`.
2. Each session file holds: `id`, `created_at`, `updated_at`, `title`, `problem`, `state` (the deliberation outputs), `chat` (the deep-dive history), `chat_summary` (running summary of older chat turns), `chat_summary_through` (cursor into `chat`), and `credits_log` (per-call telemetry).
3. Writes MUST be atomic (write to `*.tmp`, then rename) so a crash mid-run cannot corrupt a session.
4. The session loader MUST tolerate unknown keys for forward/backward compatibility.

### 5.2 Streamlit UI

1. The UI runs in three modes:
   - `new`: blank slate; user enters a problem, optional file attachments (text/code files only), and clicks Run. Uploaded files are parsed and appended to the problem under a `### Supporting Documents` section.
   - `running`: the graph streams node-by-node; each persona's output renders in a beautified (non-JSON) format as soon as it's parsed; the session is persisted incrementally. The metrics strip updates dynamically in real-time to show intermediate credits and compute time as each step completes.
   - `view`: a completed (or partial) session is displayed; the user can read the deliberation and start a deep-dive chat.
2. The sidebar MUST list every saved session as a clickable card showing title, timestamp, ID, severity-count badges (🔴N 🟠N 🟢N), credits total, and chat-message count. Clicking a card loads it into `view` mode.
3. Below the title in `view` mode, the original problem statement and any attached files are rendered in a collapsible expander: `📝 Original Problem Statement & Context`.
4. The metrics strip across the top of `view` and `running` modes shows: kiro/LLM credits, compute time, iterations, and chat message count. During deliberation execution, these metrics MUST update incrementally and in real-time as each individual agent finishes running.
5. The deliberation history tab displays agent outputs formatted cleanly (no raw JSON):
   - First Principles displays the `thought_log` scratchpad in an expander, followed by assumptions/effects tagged with color-coded confidence pills (🟢, 🟡, 🔴).
   - Systems Thinker displays the `thought_log` in an expander, followed by second-order effects and unintended consequences grouped by temporal horizon (Immediate, Delayed, Generational), displaying their causal mechanisms and highlighting any primitive failures.
   - Pre-Mortem displays a warning if context is insufficient, a `thought_log` expander, and failure modes paired with their lists of mitigations.
   - Red Teamer displays critique items categorized under red, orange, and green severity boxes.
6. The completed session layout is vertical: the Synthesis and Deliberation History tabs appear at the top, and a divider separates the Deep-Dive Chat section situated directly below them. The chat history is displayed inside a scrollable, height-bounded container (`height=500`) with the input bar pinned at the bottom.
7. After deliberation completes, a Deep-Dive Chat panel appears with a model selector. Default model: `claude-opus-4.7` if using kiro; the equivalent Opus 4.x or Sonnet 4.x for `claude`; the latest Gemini Pro thinking model for `gemini`.
8. If `no_go_triggered` is true, the UI MUST render a prominent alert banner at the top of the final strategy view indicating a "NO-GO / NOT RECOMMENDED" status.

### 5.3 Resume

1. Any saved session can be reopened from the sidebar. Resuming loads the full deliberation state and the chat history; the user can continue chatting where they left off.
2. The deep-dive chat retains a hybrid memory: the most recent N turns (default 8) verbatim, plus a running summary of older turns produced by a small "summarizer" agent.

## 6. Telemetry

1. Every LLM CLI invocation MUST capture credit/cost and duration metadata where the CLI provides it (e.g., `kiro-cli` emits `Credits: X.XX • Time: Ns` in stdout; `claude` may emit token counts; `gemini` similarly).
2. Each call appends an entry to `Session.credits_log`: `{agent, model, credits, duration_seconds, ts, phase}` where `phase` ∈ `{deliberation, deep_dive, summarizer}`.
3. Helpers MUST aggregate: total credits, total duration, per-agent breakdown.
4. The sidebar shows a "lifetime credits" metric across all sessions.
5. Telemetry aggregations MUST update the UI incrementally as steps finish, allowing immediate visibility of resource usage before the final strategy is fully synthesized.

## 7. LLM CLI Choice

The system MUST allow the user to choose which LLM CLI provider to use. Three providers are first-class:

| Provider | CLI binary | Auth | Notable models |
|---|---|---|---|
| **Claude** | `claude` (Anthropic Claude Code) | Anthropic API key | claude-opus-4.x, claude-sonnet-4.x, claude-haiku-4.x |
| **Gemini** | `gemini` | Google API key / OAuth | gemini-2.5-pro, gemini-2.5-flash |
| **Kiro** | `kiro-cli` | Amazon Midway / IDC | claude-opus-4.7, claude-sonnet-4.6, claude-haiku-4.5, deepseek-3.2, etc. |

### 7.1 Configuration

1. The provider choice MUST be configurable in at least three places, with the following precedence (highest first):
   1. A per-call argument in the orchestrator (e.g., explicit `provider="gemini"`).
   2. A `Session.provider` field, set when the session is created and persisted with the session.
   3. A workspace-level config: `.sbt/config.toml` or environment variables `SBT_PROVIDER`, `SBT_MODEL`.
   4. A built-in default (recommended: `kiro` if available; otherwise `claude`).
2. Within a single session, all deliberation personas MUST use the same provider for consistency. The deep-dive chat MAY use a different provider/model (e.g., a stronger reasoning model than the deliberation default).

### 7.2 Adapter Layer

1. The orchestrator MUST shell out through a small adapter that takes `(provider, agent_name, prompt, model, expect_json)` and returns a uniform `Result(extracted_json | extracted_markdown, credits, duration_seconds)`.
2. Each adapter implementation handles:
   - The provider's specific CLI invocation (`claude --print`, `gemini -p`, `kiro-cli chat --no-interactive --agent <name>`).
   - ANSI escape stripping in stdout.
   - JSON extraction:
     * For CLI command wrappers, extract the first/outermost balanced `{...}` object to isolate the CLI payload.
     * For the LLM response within the payload, extract the last balanced `{...}` object (while skipping scanning inside successfully parsed JSON blocks to prevent matching inner nested properties) to handle preceding conversational narration or tool output.
     * Fall back to an empty payload on failure.
   - Telemetry parsing (regex match on the provider's footer format).
   - Workspace cwd for any provider that resolves agents from a workspace directory.

### 7.3 Persona Configuration per Provider

1. **Kiro**: each persona is a workspace agent at `.kiro/agents/sbt-*.json`. The agent JSON references the verbatim prompts from `prompts/` and grants the persona access to relevant `builder-mcp` tools (e.g., `InternalSearch`, `InternalCodeSearch`, `ReadInternalWebsites`).
2. **Claude**: each persona is invoked by passing the prompt as the system prompt (`claude --system-prompt-file prompts/01-…md` or equivalent). Tool use (e.g., web search) configured via Anthropic's tool-use API if needed.
3. **Gemini**: each persona is invoked with the prompt as the system instruction. Tool use configured via Gemini's tool/function-calling API.
4. The prompts MUST NOT depend on any provider-specific feature beyond strict-JSON or structured-output guidance.
5. **Model Tiering**: To optimize cost and latency, the orchestration architecture supports provider-agnostic model tiering. Instead of running all personas on a single expensive reasoning model, the orchestrator can route simpler structured tasks (First-Principles, Pre-Mortem, Executive Synthesis) to faster, cheaper 'Flash-tier' models (e.g. Gemini Flash, Claude Haiku, Kiro Haiku), while reserving the highly capable 'Pro-tier' models (e.g. Gemini Pro, Claude Sonnet/Opus, Kiro Sonnet/Opus) for complex reasoning tasks (Systems Thinker, Red Teamer).


### 7.4 Tool Access (Internal Grounding)

1. When the chosen provider supports them, personas SHOULD have access to internal-search tools so they can ground claims in real internal data instead of hallucinating service names.
2. For `kiro-cli`, this is `builder-mcp` (Amazon-internal). For `claude` / `gemini`, the equivalent is provider-native web search or a local MCP server bridging to internal systems.
3. Tool access is a non-blocking enhancement: a persona without tool access still produces structured output, just less grounded.

## 8. State Machine and Schema

1. The orchestrator MUST be implemented as a state machine with the following nodes: `first_principles`, `systems_thinker`, `pre_mortem`, `red_team`, `synthesizer`.
2. Edges: linear from `first_principles` → `synthesizer`, with one conditional edge after `red_team` that returns to `first_principles` per the re-loop rule in §4.1.
3. The state schema (Pydantic / TypedDict / equivalent) must include:
   - `input_data: str` — original problem.
   - `first_principles_analysis`, `systems_analysis`, `risk_analysis`: each persona's validated output dict.
   - `red_team_critique: List[dict]` (append-only across iterations).
   - `final_strategy: str` (Markdown).
   - `iterations: int`.
4. Each persona node MUST persist its result to the session file before returning, so a crash mid-run leaves a partial-but-valid session that the UI can still display.
5. The orchestrator MUST act as a generator (yielding events like `(persona_name, output_data)`) to allow the UI to consume and render the outputs incrementally as the state machine progresses.

## 9. Deep-Dive Chat

1. After deliberation completes, the user may continue the conversation through a chat panel.
2. The chat panel is a separate persona (see `prompts/06-sbt-deep-dive.md`) that receives the full deliberation state, the decoupled Project Dictionary, and the chat history on every turn. The agent operates under a strict **Hierarchy of Truth** (Tool Outputs > User Corrections > Static JSON) and an **Axiom Override** protocol allowing it to branch the strategy and propose amendments if valid, verified evidence is provided.
3. Chat memory is hybrid:
   - The most recent N turns (default 8) are sent verbatim.
   - Older turns are folded into a running summary by a small summarizer persona (`prompts/07-sbt-chat-summarizer.md`) once the chat exceeds N turns. The summarizer has a relaxed word cap of 300 words, supports branching/hypothetical sandboxed reasoning, and uses semantic anchors referring back to the Deliberation JSON. Any technical terms or services explicitly referenced in the summary are cross-pinned by the Project Dictionary Extractor.
   - Alongside summarization, a dedicated, low-latency Project Dictionary Extractor agent (`prompts/08-sbt-project-dictionary.md`) runs to maintain a durable "Project Dictionary" (Technical Ledger) in `Session.project_dictionary`. It merges new observations into the dictionary using a "pinned variable" logic: core architectural entities are marked as `pinned: true` (e.g. initial concepts from the problem statement and deliberation state) and are immune to eviction. In addition, **Cross-Pinning** is enforced: any technical entity actively referenced in the chat summary is also treated as `pinned: true` to prevent FIFO eviction. Transient entities (`pinned: false`) are capped at 15 entries and are managed using a FIFO eviction policy.
   - The summary is persisted to `Session.chat_summary` and the project dictionary to `Session.project_dictionary`, and neither is re-derived from scratch.
4. Each chat message is appended to `Session.chat` and persisted before the next turn so a failed deep-dive call cannot lose user input.
5. The chat panel allows model override per call (e.g., default Opus 4.7 for thinking; switch to Haiku for cheap iteration).
6. **Deterministic Tool Triggers**: The agent MUST run under deterministic tool-invocation rules, automatically executing search/retrieval tools when alphanumeric service names, technical file extensions, or internal acronyms are present in the active conversation buffer.

## 10. Constraints and Anti-Goals

1. **Anti-goal: a confidence score on a 1–10 scale.** Severity triage replaces it. The re-loop is driven by a categorical signal (`critical[]` non-empty), not a tunable threshold.
2. **Anti-goal: implicit consensus signaling.** The system MUST NOT present persona convergence as evidence of correctness — multiple personas using the same underlying LLM share a calibration source.
3. **Anti-goal: feature creep without empirical justification.** Mechanisms that "could be useful" but have no signal from real usage MUST be deferred until there is data.
4. **Anti-goal: provider lock-in.** The prompts in `prompts/` are the contract. The orchestrator and adapter are implementation details and may be rewritten without changing what the system means.

## 11. Recommended Defaults

| Setting | Default |
|---|---|
| Provider | `kiro` if available, else `claude` |
| Deliberation model | `auto` (provider-decides) per persona |
| Deep-dive model | `claude-opus-4.7` (or provider equivalent) |
| Summarizer model | `claude-haiku-4.5` (or cheapest capable provider model) |
| `MAX_ITERATIONS` | 3 |
| Verbatim chat tail | 8 turns |
| Subprocess timeout | 300 seconds |
