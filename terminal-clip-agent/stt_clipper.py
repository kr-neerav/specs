#!/usr/bin/env python3
import os
import sys
import re
import time
import argparse
import subprocess
import shutil

# Color and formatting constants
COLOR_DIM = "\033[90m"
COLOR_GREEN = "\033[92m"
COLOR_CYAN = "\033[96m"
COLOR_YELLOW = "\033[93m"
COLOR_RESET = "\033[0m"
COLOR_BOLD = "\033[1m"

def get_terminal_width():
    """Returns the width of the terminal, defaulting to 80."""
    return shutil.get_terminal_size((80, 20)).columns

def print_banner(text, width=64):
    """Prints a beautiful, centered box with the copied text."""
    lines = []
    # Simple word wrap for the box content
    max_line_len = width - 4
    words = text.split()
    current_line = []
    current_len = 0
    
    for word in words:
        # Check if adding the word exceeds the line length
        if current_len + len(word) + (1 if current_line else 0) > max_line_len:
            lines.append(" ".join(current_line))
            current_line = [word]
            current_len = len(word)
        else:
            current_line.append(word)
            current_len += len(word) + (1 if current_line else 0)
    if current_line:
        lines.append(" ".join(current_line))

    # Top border
    print(f"\n{COLOR_GREEN}┌{'─' * (width - 2)}┐", flush=True)
    print(f"│ {COLOR_BOLD}📋 COPIED TO CLIPBOARD{COLOR_RESET}{COLOR_GREEN}{' ' * (width - 24)}│", flush=True)
    print(f"├{'─' * (width - 2)}┤", flush=True)
    
    # Content lines
    for line in lines:
        padding = width - 4 - len(line)
        print(f"│ {COLOR_RESET}{COLOR_BOLD}{line}{COLOR_RESET}{' ' * padding} │", flush=True)
        
    # Bottom border
    print(f"{COLOR_GREEN}└{'─' * (width - 2)}┘{COLOR_RESET}\n", flush=True)


def copy_to_clipboard(text):
    """Copies text to the clipboard using macOS pbcopy."""
    try:
        process = subprocess.Popen(['pbcopy'], stdin=subprocess.PIPE)
        process.communicate(input=text.encode('utf-8'))
    except Exception as e:
        print(f"{COLOR_YELLOW}⚠️ Clipboard copy failed: {e}{COLOR_RESET}", file=sys.stderr)

def notify(text):
    """Native macOS notification with banner and glass sound."""
    title = "📋 Clip Agent"
    preview = (text[:60] + ("..." if len(text) > 60 else "")).replace('"', '\\"')
    script = f'display notification "{preview}" with title "{title}" sound name "Glass"'
    try:
        subprocess.run(["osascript", "-e", script], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass # Ignore failure if notifications fail or terminal is non-interactive

def run_external_formatter(script_path, raw_text):
    """Pipes text into the external formatter script and returns the formatted text."""
    if not os.path.exists(script_path):
        print(f"{COLOR_YELLOW}⚠️ Formatter script not found at {script_path}. Using raw text.{COLOR_RESET}", file=sys.stderr)
        return raw_text
    
    try:
        # Run script, piping raw_text to stdin
        process = subprocess.Popen(
            [script_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = process.communicate(input=raw_text)
        if process.returncode == 0:
            return stdout.strip()
        else:
            print(f"{COLOR_YELLOW}⚠️ Formatter script failed with exit code {process.returncode}: {stderr.strip()}{COLOR_RESET}", file=sys.stderr)
            return raw_text
    except Exception as e:
        print(f"{COLOR_YELLOW}⚠️ Error running formatter script: {e}{COLOR_RESET}", file=sys.stderr)
        return raw_text

def build_regex(start_marker, end_marker):
    """Builds regex for matching words between the start and end markers."""
    # Split the markers into tokens and escape them
    start_tokens = [re.escape(t) for t in start_marker.split()]
    end_tokens = [re.escape(t) for t in end_marker.split()]
    
    # We want to match markers even with potential speech gaps (e.g. non-word characters)
    start_regex = r"[^\w]+".join(start_tokens)
    end_regex = r"[^\w]+".join(end_tokens)
    
    # Match pattern: start_regex ... end_regex
    pattern = rf'{start_regex}[^\w]*(.*?){end_regex}'
    return re.compile(pattern, re.IGNORECASE | re.DOTALL)

def process_transcript(content, clip_re, seen_keys, formatter_script):
    """Scans content for matches, formats them, and copies them to clipboard."""
    new_match_found = False
    for m in clip_re.finditer(content):
        raw_match = m.group(1).strip()
        if not raw_match:
            continue
            
        # Normalization to check for duplicates
        key = re.sub(r'[^\w]', '', raw_match.lower())
        if key and key not in seen_keys:
            seen_keys.add(key)
            
            # Clean up leading/trailing punctuation and extra spacing
            cleaned = re.sub(r'^[^\w]+', '', raw_match)
            cleaned = re.sub(r'\s+', ' ', cleaned).strip()
            
            if not cleaned:
                continue
                
            # Formatting (if external script provided)
            if formatter_script:
                formatted = run_external_formatter(formatter_script, cleaned)
            else:
                formatted = cleaned
                
            # Copy to clipboard & trigger UI output
            copy_to_clipboard(formatted)
            notify(formatted)
            print_banner(formatted)
            new_match_found = True
            
    return new_match_found

def stream_stdin(clip_re, seen_keys, formatter_script):
    """Streams live text line-by-line from stdin."""
    print(f"\n{COLOR_CYAN}>>> Ready: Streaming from stdin. Listening for markers...{COLOR_RESET}\n", flush=True)
    
    # Keep track of everything heard in the current session
    full_transcript = ""
    
    try:
        for line in sys.stdin:
            if not line:
                break
            
            # Print the live text as it is heard in dimmed colors
            sys.stdout.write(f"{COLOR_DIM}{line}{COLOR_RESET}")
            sys.stdout.flush()
            
            full_transcript += " " + line
            
            # Check for matches
            process_transcript(full_transcript, clip_re, seen_keys, formatter_script)
            
    except KeyboardInterrupt:
        print(f"\n{COLOR_CYAN}>>> Stopping CLI agent.{COLOR_RESET}", flush=True)

def tail_file(file_path, clip_re, seen_keys, formatter_script):
    """Tails a log or transcript file, reading new lines as they are appended."""
    print(f"\n{COLOR_CYAN}>>> Ready: Tailing file '{file_path}'. Listening for markers...{COLOR_RESET}\n", flush=True)
    
    # Read initial content to pre-populate seen keys (avoid copying old transcripts on restart)
    full_transcript = ""
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            full_transcript = f.read()
            # Scan existing content to register them as already seen
            for m in clip_re.finditer(full_transcript):
                raw_match = m.group(1).strip()
                key = re.sub(r'[^\w]', '', raw_match.lower())
                if key:
                    seen_keys.add(key)
        
        # Print existing content as dimmed if requested or desired, or just print start message
        print(f"{COLOR_DIM}Loaded existing history from file. Continuing to tail...{COLOR_RESET}\n", flush=True)

    # Start tailing
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            # Go to the end of the file
            f.seek(0, os.SEEK_END)
            last_mtime = os.stat(file_path).st_mtime
            
            while True:
                time.sleep(0.2)
                # Check if file has been modified
                try:
                    stat = os.stat(file_path)
                    if stat.st_mtime != last_mtime:
                        last_mtime = stat.st_mtime
                        
                        # Read newly appended lines
                        new_data = f.read()
                        if new_data:
                            # Print live transcript in dimmed text
                            sys.stdout.write(f"{COLOR_DIM}{new_data}{COLOR_RESET}")
                            sys.stdout.flush()
                            
                            # Append to running transcript and process
                            full_transcript += new_data
                            process_transcript(full_transcript, clip_re, seen_keys, formatter_script)
                except FileNotFoundError:
                    # Handle file rotation or deletion
                    pass
    except KeyboardInterrupt:
        print(f"\n{COLOR_CYAN}>>> Stopping CLI agent.{COLOR_RESET}", flush=True)


def main():
    parser = argparse.ArgumentParser(
        description="A lightweight, portable clipboard extractor that streams/tails speech-to-text outputs, parses marker words, formats matches, and copies to clipboard."
    )
    parser.add_argument(
        "-f", "--file",
        help="Path to the speech-to-text log/transcript file to tail. If omitted, streams from stdin."
    )
    parser.add_argument(
        "--start-marker",
        default="charlie charlie",
        help="Starting marker words (default: 'charlie charlie')"
    )
    parser.add_argument(
        "--end-marker",
        default="delta delta",
        help="Ending marker words (default: 'delta delta')"
    )
    parser.add_argument(
        "--formatter",
        help="Path to an external formatter executable/script. The extracted text is piped into it via stdin."
    )
    
    args = parser.parse_args()
    
    # Build regex and tracking sets
    clip_re = build_regex(args.start_marker, args.end_marker)
    seen_keys = set()
    
    if args.file:
        tail_file(args.file, clip_re, seen_keys, args.formatter)
    else:
        stream_stdin(clip_re, seen_keys, args.formatter)

if __name__ == "__main__":
    main()
