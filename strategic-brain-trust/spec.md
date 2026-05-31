# Architecture Specification: Leadership & Mechanisms Brain Trust

**Version:** 4.0 (Final Stack & Feature Parity)
**Target User:** Staff/Principal (L6/L7) Engineering Leadership
**Environment:** Node.js (Express) + React (Vite) + Bash CLI + SQLite3 + `gemini` CLI
**Topology:** Dynamic Iterative Multi-Agent System (MAS)

---

## 1. System Overview & Execution Loop

The system operates as an iterative state machine powered by bash scripts that act as the orchestration layer, driven by a Node.js Express backend and a React frontend. The process runs up to a maximum of 3 iterations, looping dynamically based on the Orchestrator's assessment.

* **Iteration Phase (Diagnosis):** The leader inputs a proposed behavioral mechanism via the UI. The Orchestrator routes the payload to four sub-agents in parallel/sequence. Sub-agents (Skeptic, Architect, Empath, Innovator) diagnose flaws. If it is Iteration > 1, the sub-agents are additionally fed their own previous critique to ensure continuity.
* **Synthesis Phase:** The Orchestrator evaluates the multi-agent diagnostics. It outputs a `<STATUS>` flag (`Revision Required` or `Proposal Approved`). If revision is required, the loop increments and re-runs the diagnosis. 
* **Final Summary Phase:** Once approved (or if the 3-iteration hard limit is reached), the Orchestrator generates a simple, highly actionable final summary in plain language outlining the core problem, what was analyzed, and a clear recommendation.

---

## 2. Infrastructure & Data Models

The system relies on a **Push (Payload) Strategy**. Agents do not have direct database access; the Bash execution plane injects exact context diffs (via database queries and `jq`) into prompt templates to maintain strict psychological sandboxing.

### 2.1 Backend Architecture
* **API Gateway:** A Node.js Express server (`server.js`) handles REST API endpoints for the frontend (`GET /api/sessions`, `POST /api/sessions`, `DELETE /api/sessions/:id`, `POST /api/sessions/:id/chat`, etc.).
* **Subprocess Spawning:** When a new session is started, Node.js uses `child_process.exec` to fire off the `execution_loop.sh` bash script in the background.
* **Token Extraction:** The application uses `--output-format json` with the `gemini` CLI. Bash scripts parse the output via `jq` to extract both the generated text and the API token usage, persisting both to the database.

### 2.2 State Persistence (SQLite Schema)

```sql
-- Tracks the overall session state
CREATE TABLE brain_trust_sessions (
    session_id TEXT PRIMARY KEY,
    title TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    current_iteration INTEGER DEFAULT 1,
    original_proposal TEXT,
    final_execution_artifact TEXT
);

-- Tracks the orchestrator's synthesis per iteration
CREATE TABLE session_iterations (
    session_id TEXT,
    iteration INTEGER,
    orchestrator_synthesis TEXT,
    PRIMARY KEY(session_id, iteration),
    FOREIGN KEY(session_id) REFERENCES brain_trust_sessions(session_id)
);

-- Tracks the isolated outputs of the sub-agents and token costs
CREATE TABLE agent_critiques (
    critique_id TEXT PRIMARY KEY,
    session_id TEXT,
    iteration INTEGER,
    agent_role TEXT,
    raw_response TEXT,
    token_usage INTEGER DEFAULT 0,
    FOREIGN KEY(session_id) REFERENCES brain_trust_sessions(session_id)
);

-- Tracks the Deep Dive chat messages and token costs
CREATE TABLE deep_dive_chats (
    message_id TEXT PRIMARY KEY,
    session_id TEXT,
    role TEXT,
    content TEXT,
    token_usage INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(session_id) REFERENCES brain_trust_sessions(session_id)
);
```

---

## 3. Persona Configurations & Model Routing

Compute is optimized by utilizing the `gemini-3.1-pro-preview` model via the CLI. 

* **The Orchestrator:** Routes state, summarizes agent critiques, controls the `while` loop logic via `<STATUS>` tags, and synthesizes the Final Summary and Recommendation.
* **The Skeptic:** Analyzes proposals via Game Theory, Malicious Compliance, and Metric Manipulation.
* **The Architect:** Identifies systemic bottlenecks, cognitive load issues, and cascading failures.
* **The Empath:** Evaluates psychological safety, tone, and cultural health impacts.
* **The Innovator:** Generates unconventional lateral solutions within immutable limits.

---

## 4. User Interface Architecture (React / Vite)

The frontend is built as a Single Page Application (SPA) providing real-time visibility into the multi-agent simulation.

### 4.1 Layout & Navigation (Sidebar)
* **Sidebar Container:** Displays a paginated list of past sessions (10 per page), sorted chronologically with precise timestamps.
* **Features:** Includes a real-time text search filter (searching titles and original proposals), session deletion capabilities, and a "Hide/Show" toggle to collapse the sidebar for full-screen focus.
* **Dynamic Renaming:** Sessions are auto-titled by an LLM upon creation, but users can edit the title inline via a pencil icon.

### 4.2 Main Workspace & Real-time Transparency
* **Live State Tracking:** Status badges (`✅ Completed` or a dynamic, animated CSS pulsing dot indicating active processing) poll the backend dynamically to reflect the Bash script's progress.
* **Iteration Blocks:** The UI renders each iteration sequentially. The Orchestrator's Synthesis is contained within a collapsible card to save vertical space.
* **Agent Transparency Dashboard:** Inside each iteration block, a sub-dashboard displays the 4 agent critiques. These are collapsed by default. The UI explicitly renders the exact API Token cost (🪙 X Tokens) utilized by each agent per iteration.
* **Universal Clipboard Integration:** A reusable `CopyButton` component (`📋 Copy`) is integrated across the UI, allowing one-click Markdown extraction of the original proposal, orchestrator syntheses, individual agent critiques, and final recommendations.

### 4.3 Deep Dive Chat Interface
* **Location:** Rendered at the bottom of the session view, with a toggle to hide/show the chat pane.
* **Context Injection:** When the user asks a question, the Node.js backend fetches the *entire session state* from SQLite (Original Proposal, all Iterations, all Agent Critiques, and the Final Summary). This massive context block is injected into the Deep Dive LLM system prompt, allowing hyper-accurate cross-iteration analysis.
* **Formatting & Telemetry:** Chat output is beautifully formatted using `react-markdown`. Every assistant response explicitly displays its API Token cost, and an aggregated "Total Tokens" counter is pinned to the top of the Deep Dive pane. Chat bubbles also include the one-click copy to clipboard integration.
