# Agent TDD (Test-Driven Development) - UI Specification

This document defines how the Agent TDD capability integrates with the [Common Review Platform](./README.md) running on the shared UI port.

## 1. Canvas Rendering (Main Workspace)
When the Agent TDD session is initiated or viewed, the Common UI renders a dynamic canvas:
*   **Control Panel:** A top-level input where the user specifies the `scope` of the agentic generation process. It features a "Generate Specification" button that triggers the backend orchestrator.
*   **Status Bar:** Displays the current real-time session status (e.g., "Awaiting Input", "Orchestrating Agents...", or "Completed"), alongside dynamic calculation of completion percentages based on Verified vs Total DAG nodes.
*   **DAG Visualizer (Collapsible):** Renders the tree structure of the generated specification contracts (Epics, Components, Units). Nodes are visually distinct based on their validation status (`VERIFIED_AND_LOCKED`, `DRAFT`, `REJECTED`).
*   **Live Feed (Collapsible):** A streaming log output displaying real-time agent interactions, warnings, successes, and errors as the MAS orchestrator works through the spec.

## 2. Navigation & Sidebar
*   **Session History Sidebar:** Displays a collapsible left sidebar listing all historical Agent TDD sessions.
*   **Direct API Integration:** The session list natively fetches `GET /api/sessions` rather than relying on local browser caches (localStorage).
*   **Session Cards:** Display the `root_scope` (title), `session_name` (ID), execution status (`current_node_id`), and steps (`interaction_count`).
*   **Deletion:** Clicking the trash icon issues a `DELETE /api/sessions/{session_name}` call to the backend, wiping the session from the backend database and immediately updating the UI.

## 3. Gateway Connectivity
The Agent TDD local backend exposes the following endpoints for the Common UI to consume:
*   `POST /api/rsew` (Payload: `{ "scope": "string" }`) - Kicks off a new spec generation run.
*   `GET /api/sessions` - Returns the comprehensive history list from the SQLite backend.
*   `DELETE /api/sessions/{session_name}` - Wipes the historical session.
