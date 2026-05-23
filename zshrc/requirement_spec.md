# Zshrc Capabilities Specification

> [!WARNING]
> **Implementation Note**
> When implementing this specification on a new machine, **DO NOT replace the existing `~/.zshrc` file**. Instead, append these configurations and scripts as **additional capabilities** to the existing file. This ensures you do not break standard Zsh configurations or Oh-My-Zsh setups.

## 1. Overview
This specification details custom extensions for the Zsh environment tailored for users running inside a Tmux multiplexer. It provides four command-line capabilities: opening a new tmux tab in the current directory, retroactively capturing the previous command's output to the clipboard, converting natural-language requests into shell commands, and a short alias for clearing the screen.

## 2. Core Requirements

### 2.1 New Tmux Tab (`create`)
1. Provide a shell function named `create`.
2. When a user runs `create` (no arguments), the environment must:
   - Verify that the current shell is running inside a tmux session (i.e., the `TMUX` environment variable is set). If not, print an error to stderr and return non-zero — do not attempt to spawn a window outside of tmux.
   - Open a new tmux tab (window) whose working directory is the **active pane's current working directory** (e.g., via `tmux new-window -c "$PWD"`).
3. The new tab should inherit the user's standard shell so it is immediately ready for input.

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
3. **Backend agent.** The function must drive a **basic kiro-cli agent** named `zshrc-ask` rather than calling a model SDK directly. The agent is intentionally minimal: no MCP servers, no tool access (apart from `fs_read` for token discovery), and a single system prompt that defines the delimited output contract. The agent's JSON config lives at `~/.kiro/agents/zshrc-ask.json`. A reference copy is shipped at `ask-agent.json.example` (see §3).
4. The function must:
   - Concatenate all arguments passed to it as the user message.
   - Invoke `kiro-cli chat --no-interactive --trust-all-tools --agent zshrc-ask "$*"`.
   - Strip ANSI escape sequences from kiro-cli's stdout (kiro-cli decorates output with color codes that would otherwise confuse delimiter matching).
   - Use `awk` to extract the command and explanation between `===CMD===`/`===/CMD===` and `===EXP===`/`===/EXP===` markers respectively. The closing delimiters MUST include a leading slash so the close tag is textually distinct from the open tag — without that, the model paraphrases (e.g., emitting `<<<ENDCMD>>>` instead of `<<<END_CMD>>>`) cause silent extraction failures. Underscored markers like `___CMD_START___` are also forbidden because some kiro-cli display paths render them as Markdown horizontal rules.
5. The generated command and the brief explanation must be printed cleanly to the terminal for the user to visually review and understand.
6. Only the generated command must be simultaneously piped to the system clipboard (via `pbcopy`) so it is instantly ready to paste and execute without dragging the explanation along.
7. On extraction failure (e.g., the model deviates from the delimiter contract), the function must print an error and dump the first 400 characters of the raw kiro-cli stdout for debugging — never silently fail.

### 2.4 Clear-Screen Alias (`cl`)
1. Provide a shell alias named `cl` that runs `clear`.
2. The alias serves as a two-character shortcut for clearing the terminal screen — strictly cosmetic, no other behavior.
3. If the existing `~/.zshrc` already defines `cl` for another purpose, the implementation must overwrite or remove the prior definition so `cl` unambiguously means "clear screen."

## 3. Reference Files
- `zshrc_snippet.sh.example`: Contains the exact shell functions and aliases to append to the end of `~/.zshrc`.
- `tmux-copy-last.py.example`: The Python script required to fulfill the Tmux buffer scraping capability. This should be placed in `~/.local/bin/tmux-copy-last` and made executable.
- `ask-agent.json.example`: The kiro-cli agent definition powering §2.3 (`ask`). Install by copying to `~/.kiro/agents/zshrc-ask.json`, then verify with `kiro-cli agent list | grep zshrc-ask`.
