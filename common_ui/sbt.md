# Strategic Brain Trust (SBT) - Review UI Specification

This document defines how the Strategic Brain Trust integrates with the [Common Review Platform](./README.md) running on the shared UI port.

## 1. Canvas Rendering (Main Workspace)
When an SBT session is initiated or viewed, the Common UI will render a specific Dynamic Review Canvas.
*   **Persona Selection:** A dropdown allows users to target their proposal either towards "Leadership" or "Technical" agents.
*   **File Uploads:** Users can natively load `.txt`, `.md`, `.csv`, and `.json` documents directly into the proposal text box via an HTML5 `FileReader`.
*   **Live State Tracking:** Status badges (`✅ Completed` or a dynamic, animated CSS pulsing dot indicating active processing) poll the backend dynamically to reflect the Bash script's progress.
*   **Iteration Blocks:** The UI renders each execution loop under a distinct, explicitly marked header (e.g., "Iteration 1"). Inside this block, the Orchestrator's Synthesis (Synthesizer output) is contained within a full-width collapsible card (accordion) that expands when clicked. Both the synthesis and critiques MUST be rendered using `react-markdown`.
*   **Agent Transparency Dashboard:** Inside each explicitly marked iteration block, the display of agent outputs is NOT tile-based. Instead, each agent's output takes up the full width of the screen in a collapsible accordion format. When clicked, it expands to show the critique. The UI explicitly renders the exact API Token cost (`🪙 X Tokens`) utilized by each agent per iteration.

## 2. Navigation & Sidebar
*   **Sidebar Container:** Displays a paginated list of historical sessions (10 per page), sorted by the 10 most recent sessions. This pane must include the ability to start new SBT sessions (e.g., a "New Session" button).
*   **Features:** Includes the ability to delete any existing sessions directly from the left pane, a real-time text search filter (searching titles and original proposals), and a dedicated minimize button to collapse the left pane (sidebar) for full-screen focus.
*   **Dynamic Renaming:** Sessions are auto-titled by an LLM upon creation, but users can edit the title inline via a pencil icon.
*   **Token Telemetry:** Each historic session card natively calculates and renders a dynamic `🪙 X` badge, summing the API token consumption across the original execution loop and any subsequent deep dive chats.

## 3. Deep Dive Chat Interface
*   **Location:** Rendered at the bottom of the session view, with a toggle to hide/show the chat pane.
*   **Context Injection:** When the user asks a question, the backend fetches the *entire session state* from SQLite and routes it to the chat engine. The historical chat log must be explicitly scoped to the active `session_id`, instantly loading older conversations whenever a past session is selected.
*   **Formatting & Telemetry:** Chat output is natively formatted using `react-markdown`. Every assistant response explicitly displays its API Token cost (`🪙 X`), and an aggregated "Total Tokens" counter is pinned to the top of the Deep Dive pane summarizing the entire conversation history.

## 4. Universal Clipboard Integration
A reusable `CopyButton` component (`📋 Copy`) is integrated across the UI, allowing one-click Markdown extraction of the original proposal, orchestrator syntheses, individual agent critiques, and final recommendations.
