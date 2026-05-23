# Zshrc Capabilities Specification

> [!WARNING]
> **Implementation Note**
> When implementing this specification on a new machine, **DO NOT replace the existing `~/.zshrc` file**. Instead, append these configurations and scripts as **additional capabilities** to the existing file. This ensures you do not break standard Zsh configurations or Oh-My-Zsh setups.

## 1. Overview
This specification details custom extensions for the Zsh environment that provide advanced command output capture capabilities, specifically tailored for users running inside a Tmux multiplexer.

## 2. Core Requirements

### 2.1 Live Output Capture (`c`)
1. Provide a wrapper command named `c`.
2. When a user runs `c <command>`, the environment must:
   - Execute the target `<command>`.
   - Display the output (both stdout and stderr) to the terminal normally so the user can read it in real-time.
   - Simultaneously pipe the exact same output directly to the system clipboard (e.g., via `pbcopy`).
   - Print a success message (e.g., "[Copied to clipboard!]") after completion.

### 2.2 Retroactive Output Capture (`clast`)
1. Provide an alias named `clast`.
2. When a user runs `clast`, the environment must capture the output of the *immediately preceding* command without re-executing that command.
3. **Tmux Buffer Scraping**: To achieve this without re-execution, `clast` must invoke a script that:
   - Connects to the active Tmux session's screen buffer (`tmux capture-pane -pS -2000`).
   - Searches backwards through the text to find the last two instances of the user's shell prompt indicator (e.g., `➜`).
   - Extracts all printed text between the second-to-last prompt (the original command) and the last prompt (the `clast` invocation itself).
4. The extracted text must be piped directly to the system clipboard.
5. A success message must be printed to the terminal.

### 2.3 Natural Language Command Generator (`ask`)
1. Provide a shell function named `ask`.
2. The user can type `ask <any natural language request>` (no quotes required) to describe a shell command they want to run.
3. The function must:
   - Concatenate all arguments passed to it.
   - Invoke a local LLM CLI tool (specifically `gemini`) in headless mode (`-p`).
   - Use a strict system prompt to ensure the LLM outputs exactly two things: the raw executable shell command, and a brief explanation of how it works.
   - Use text delimiters and tools like `awk` to extract the command and the explanation separately, ignoring any warning messages or extraneous output.
4. The generated command and the brief explanation must be printed cleanly to the terminal for the user to visually review and understand.
5. Only the generated command must be simultaneously piped to the system clipboard (via `pbcopy`) so it is instantly ready to paste and execute without dragging the explanation along.

## 3. Reference Files
- `zshrc_snippet.sh.example`: Contains the exact shell functions and aliases to append to the end of `~/.zshrc`.
- `tmux-copy-last.py.example`: The Python script required to fulfill the Tmux buffer scraping capability. This should be placed in `~/.local/bin/tmux-copy-last` and made executable.
