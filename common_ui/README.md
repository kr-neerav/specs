# Architecture Design Document: Common Review Platform

**Version:** 1.0.0  
**Status:** DRAFT  
**Domain:** Multi-Agent Systems (MAS) & Human-In-The-Loop (HITL)  

## 1. Executive Summary

The **Common Review Platform** is a unified, framework-agnostic dashboard designed to serve as the Human-In-The-Loop (HITL) gate across multiple agentic capabilities (e.g., the Blueprint Engine, Strategic Brain Trust, Agent TDD). By decoupling the UI from individual execution engines, this platform ensures a consistent, premium user experience while allowing different capabilities to plug in their specific state schemas.

## 2. Architecture & Technology Stack

The platform is designed for scalability and separation of concerns.

*   **Frontend Framework:** Next.js (React)
*   **Styling:** Vanilla CSS. The design prioritizes a rich, dynamic, and premium aesthetic (incorporating smooth gradients, micro-animations, and modern typography like Inter) rather than a generic boilerplate look.
*   **Backend Gateway:** FastAPI (Python) serving as an API gateway that routes between the React frontend and the respective local SQLite3 states or LangGraph engines of the underlying capabilities.
*   **Networking:** The UI is hosted on a single, shared port (e.g., `localhost:3000`). All capabilities render their specific views through this centralized application rather than spinning up individual UI servers.

## 3. Core Capabilities

1.  **Unified Dashboard / Execution Hub:** A centralized live view of all processing runs across different capabilities. Displays statuses (`PROCESSING`, `AWAITING_HITL`, `APPROVED`, `FAILED`), capability type, and timestamps.
2.  **Dynamic Review Canvas:** A pluggable interactive interface that adapts to the specific capability being reviewed. When a run hits an `AWAITING_HITL` state, it displays the relevant context (e.g., drafted business rules for the Blueprint Engine, or translation outputs for a different tool).
3.  **Universal Feedback Injector:** A unified text input and feedback mechanism where human operators can provide guidance. The gateway routes this feedback to deserialize the specific capability's state and resume execution.
4.  **Approval Gate:** A final confirmation mechanism to mark outputs as `VERIFIED` and signal the underlying agentic graph to proceed to synthesis or finalization.

## 4. Integration Protocol

To plug a new capability (like the Blueprint Engine) into the Common Review Platform, the capability must:
1. Provide a SQLite3 database or equivalent state representation accessible by the FastAPI gateway.
2. Implement standard state enums (`AWAITING_HITL`, `PROCESSING`, etc.).
3. Define a UI schema that dictates how its specific payload should be rendered on the Dynamic Review Canvas.
