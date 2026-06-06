# Architecture Specification: Strategic Brain Trust

**Version:** 5.0 (Multi-Persona Architecture)
**Target User:** Staff/Principal (L6/L7) Engineering Leadership
**Environment:** Node.js (Express) + Bash CLI + SQLite3 + `antigravitycli`
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
* **Subprocess Spawning:** When a new session is started, Node.js uses `child_process` to trigger the orchestrator.
* **Token Extraction:** The application uses `--output-format json` with `antigravitycli`. Bash scripts parse the output via `jq` to extract both the generated text and the API token usage, persisting both to the database.

### 2.2 State Persistence (SQLite Schema)

```sql
-- Tracks the overall session state
CREATE TABLE brain_trust_sessions (
    session_id TEXT PRIMARY KEY,
    title TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    current_iteration INTEGER DEFAULT 1,
    original_proposal TEXT,
    persona TEXT DEFAULT 'leadership',
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

Compute is optimized by utilizing the `gemini-3.1-pro-preview` model via `antigravitycli`. 

### 3.1 Prompt Sub-Domains (Personas)
The system now supports dynamic "Personas" that drastically alter the behavior of the agents without changing the orchestrator mechanics:
* **Leadership & Culture (`backend/prompts/leadership/`)**: Evaluates behavior, game theory, corporate incentives, and organizational management.
* **Technical & Architecture (`backend/prompts/technical/`)**: Evaluates CAP theorem, data races, Developer Experience (DevEx), and system scalability (Staff+ level).

### 3.2 Orchestration Loop (`backend/core/execution_loop.sh`)
* **Execution:** Sequential, avoiding Antigravity API rate limits. Each agent script receives a `$PERSONA` argument to determine which prompt directory to read from. Output is strictly formatted as JSON.

---

## 4. User Interface Architecture

The Strategic Brain Trust integrates with the centralized [Common Review Platform](../common_ui/README.md) for its UI layer. 

The specific UI capabilities—including Iteration Blocks, the Agent Transparency Dashboard, and the Deep Dive Chat Interface—are defined in the dedicated [SBT UI Specification](../common_ui/sbt.md). The backend exposes the SQLite payload and state boundaries via REST API for the common UI to consume.
