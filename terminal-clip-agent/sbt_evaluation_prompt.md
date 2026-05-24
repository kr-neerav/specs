# SBT Evaluation Input: Terminal Clip Agent Design

## Problem Context
We have designed a portable, decoupled terminal-based clipboard extraction tool (`stt_clipper.py`) to mimic the speech-to-text clipboard copying experience from a personal setup on a locked-down office laptop. 

The personal setup uses PyAudio + Faster-Whisper to transcribe microphone audio in real time and monitor a markdown transcript. When it hears marker keywords (like `charlie charlie ... delta delta`), it extracts the text, runs a local LLM format (via Ollama/Gemma), and copies it to the clipboard.

For the office setup:
1. The speech-to-text translation engine is a different, internal approved tool.
2. There is a specific proprietary formatting script that we must integrate with, which does custom formatting (e.g. spelling corrections or business shortcuts).
3. The office machine is a locked-down macOS device with constraints: zero third-party Python dependencies (no `pyperclip`, no `openai` SDK, etc.) can be installed.

## Proposed Architecture
The decoupled clipper utility (`stt_clipper.py`) is implemented in pure Python 3 using standard libraries. It operates by:
1. **Input Interface**: Supports two inputs:
   - *Tailing Mode*: Tailing a local log file written to by the office STT tool.
   - *Piping Mode*: Reading line-by-line from `sys.stdin` (e.g., `office_stt | stt_clipper.py`).
2. **Terminal UI**: Displays raw text in dimmed color (`\033[90m`) to show a running transcript of "everything heard" without screen clutter.
3. **Regex Extraction**: Scans the running session transcript for configurable marker keywords (defaulting to double-taps: `charlie charlie (.*?) delta delta`).
4. **Formatter Pipeline**: Pipes the extracted match to the external office formatting script's standard input and captures its standard output.
5. **System Integration**: Copies the formatted text to the macOS clipboard using a native `pbcopy` subprocess and sends desktop banner notifications with an auditory cue using `osascript`.
6. **Double-Copy Guard**: Normalizes matches and tracks seen keys in memory to prevent duplicate copies.
7. **Highlight Box**: Renders successfully copied text in a bold green box (`\033[92m`) directly in the terminal stream.

---

## Evaluation Request for the Strategic Brain Trust (SBT)
Deliberate on the robustness, edge-case behavior, and operational risks of this design. Specifically, evaluate:

1. **Piping & Buffering Risks**: Under pipe mode (`office_stt | stt_clipper.py`), how does standard output buffering in Python or the upstream STT command affect live terminal feedback? Are there risks of delayed output or deadlock?
2. **Memory Growth & Deduplication**: Since `seen_keys` and the `full_transcript` buffer grow continuously in memory during a session, are there risks of memory exhaustion or performance degradation for long-running tailing/piping sessions?
3. **Log Rotation & File Locks**: In file tailing mode, how will the tool handle log rotation, file truncation, or permission lockups from the office STT writer process?
4. **Subprocess Failures**: If the external formatting script fails, hangs, or exits with non-zero codes, how does the utility prevent UI lockups or empty clipboard overrides?
5. **Multi-loop or Overlapping Markers**: What happens when markers are spoken across chunk boundaries or if a user speaks multiple marker sequences in quick succession?
6. **Dependency-Free System Calls**: Is wrapping `pbcopy` and `osascript` in subprocess calls robust enough across macOS version updates, especially concerning notification center permissions or sandboxing?
