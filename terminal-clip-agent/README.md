# Terminal Clip Agent Specs & Tool

This project specifies and implements a decoupled **Terminal Clipboard Extractor** (`stt_clipper.py`) for speech-to-text workflows. It replicates the custom UX from the home `whisper_stt` setup but is completely decoupled from any specific model, making it easy to migrate to an office laptop running any internal approved speech-to-text software.

## Project Structure

- **[`requirement_spec.md`](requirement_spec.md)**: The technical requirements and specifications for the tool.
- **[`stt_clipper.py`](stt_clipper.py)**: The fully portable, dependency-free reference implementation written in standard Python 3.

---

## Features

- **Live Gray Log**: Displays raw incoming speech in dark gray so you can see "everything heard" without clutter.
- **Visual Highlight**: Automatically formats and renders copied text in a distinct bold green box.
- **Native Clipboard & Chime**: Copies to clipboard via `pbcopy` and alerts you with a native macOS sound and notification via `osascript`.
- **Double-Tap Markers**: Scans for standard starting/ending marker words (defaults to `charlie charlie` ... `delta delta`).
- **External Script Pipeline**: Supports feeding the matched segments through an external script (e.g. for post-formatting, spell checking, or custom shortcuts) before it lands in the clipboard.

---

## Usage Examples

### 1. Log Tailing Mode (Recommended)
If your office speech-to-text software writes text to a local log or transcript file, run the clipper in tailing mode:
```bash
./stt_clipper.py --file /path/to/office_stt_output.log
```

### 2. Standard Input Pipe Mode
If your office speech-to-text tool outputs directly to standard output, you can pipe it directly into `stt_clipper.py`:
```bash
/path/to/office_stt_command | ./stt_clipper.py
```

### 3. Custom Markers & Formatter Integration
To specify different marker words and run the extracted text through a custom script (e.g., `office_formatter.py` or a shell script):
```bash
./stt_clipper.py \
  --file /path/to/office_stt.log \
  --start-marker "copy copy" \
  --end-marker "paste paste" \
  --formatter "/path/to/office_formatter.sh"
```

*Note: The script passed to `--formatter` must read the raw text from standard input (`stdin`) and write the final formatted text to standard output (`stdout`).*
