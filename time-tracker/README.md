# Private Air-Gapped Time-Tracking System

This repository contains the design specifications, architecture, and code templates for a 100% private, air-gapped time-tracking system on macOS. 

To maintain security and allow local customizations, the actual executable scripts are excluded from git.

## 📂 Repository Structure
*   **[time_tracker_spec.md](time_tracker_spec.md)**: The full technical design, including system architecture, security considerations, and the inline code templates for the logger, parser, and LLM prompt.

## 🚀 How to Set Up on a New Laptop

To replicate this time-tracking system on another machine:

1.  Clone this repository.
2.  Open **[time_tracker_spec.md](time_tracker_spec.md)**.
3.  Copy the code block under **1. Passive macOS Window Capture** and save it locally as `local_tracker.sh` in the root of the project folder.
4.  Copy the code block under **2. Deterministic Aggregator** and save it locally as `parser.py` in the root of the project folder.
5.  Set execution permissions for the tracker:
    ```bash
    chmod +x local_tracker.sh
    ```
6.  Start tracking and aggregate your metrics as outlined in the setup guide.
