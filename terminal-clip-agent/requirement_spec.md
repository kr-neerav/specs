# Terminal Clip Agent Specification

> [!NOTE]
> **Implementation Note**
> When setting up this utility on an office machine, use the provided portable script `stt_clipper.py`. It does not require any external Python dependencies (e.g., no `pyperclip` required) as it interacts directly with native macOS commands (`pbcopy` and `osascript`).

## 1. Overview
This specification details a standalone terminal utility that extracts speech-to-text transcription segments marked by start/end keywords (e.g., `charlie charlie` ... `delta delta`), runs them through an optional external formatting script, and copies the formatted result to the system clipboard. 

Crucially, it provides a unified terminal User Experience:
- Streams the running raw transcription in a dimmed gray color ("everything the model heard").
- Renders any successfully copied matches inside a highly visible, styled terminal box.
- Triggers a native desktop notification with an auditory chime.

By decoupling the input feed (using standard input streams or file tailing) from the speech-to-text engine itself, this utility can run on any laptop using whatever internal, approved speech-to-text software is installed.

---

## 2. Core Requirements

### 2.1 Input Methods
The tool must support two consumption models to interface with different speech-to-text engines:
1. **Stdin Streaming (Pipe Mode)**:
   - Read incoming transcriptions directly from standard input (`sys.stdin`) line-by-line.
   - Example: `office_stt | python3 stt_clipper.py`
2. **Log File Tailing (Tail Mode)**:
   - Monitor a specified log file (e.g. via `--file <path>`).
   - Dynamically tail the end of the file, reading and processing newly appended text as it is written.
   - Ignore/pre-register any existing marker matches from previous runs to prevent duplicate copies on startup.

### 2.2 Live Transcription UI
1. **Dimmed Raw Log**:
   - Any raw text read from the stream must be immediately printed to the terminal stdout.
   - The text must be colored using standard ANSI escape codes (`\033[90m` / Dark Gray) to signify that it is background text.
2. **Visual Clipboard Highlight**:
   - When a target segment is captured and copied, the tool must print a distinct, styled box containing the copied text.
   - The box must have borders (using ASCII box-drawing characters: `┌`, `─`, `┐`, `│`, `└`, `┘`) and use a bold green color (`\033[92m`) to draw the user's eye.
   - Text inside the box must wrap correctly to match the terminal size.

### 2.3 Marker Detection & Extraction
1. **Regex Extraction**:
   - Search the running session transcript for segments enclosed by starting and ending marker keywords.
   - The default markers are:
     - **Start**: `charlie charlie`
     - **End**: `delta delta`
   - These markers must be configurable via CLI flags (e.g., `--start-marker` and `--end-marker`).
   - The regex must handle gaps/non-word characters (e.g. speaker pause punctuation: `charlie, charlie`) and match case-insensitively.
2. **Deduplication**:
   - Maintain a set of previously copied text keys (normalized to lowercase alphanumeric characters) to ensure that repeated matches are not copied multiple times.

### 2.4 External Formatter Integration
1. If an external formatting script is provided (via `--formatter <path>`):
   - The extracted text must be piped into the script's stdin.
   - The tool must capture the script's stdout and use it as the final text.
   - If the formatting script fails or is not found, the tool must fallback to copying the raw, cleaned text.
2. If no formatter script is specified, the tool copies the raw cleaned text directly.

### 2.5 macOS Notifications & Clipboard Copy
1. **System Copy**:
   - Pipe the final text directly into `/usr/bin/pbcopy` to put it in the system clipboard.
2. **Banner Notification**:
   - Use `osascript` to trigger a system banner displaying a truncated preview of the copied text.
   - Use the native `Glass` sound effect as an auditory cue of a successful copy.

---

## 3. Reference Files
- `stt_clipper.py`: The complete, dependency-free reference Python implementation that satisfies all the above requirements.
