# Requirements Specification: Modal Terminal Experience

## 1. Overview
This project defines a comprehensive configuration for **Tmux** that transforms it from a traditional prefix-based terminal multiplexer into a **Vim-like Modal Editor**. It provides a "browser-style" vertical tabs experience that pops up when needed, keeping the interface clean and entirely keyboard-driven.

## 2. Core Requirements

### 2.1 Modal Architecture
1. The multiplexer must operate in two distinct modes: **Insert Mode** (default) and **Normal Mode** (command mode).
2. There should be no traditional "prefix" key required for normal operation.
3. `Escape` transitions the environment from Insert Mode to Normal Mode.
4. `i` transitions the environment from Normal Mode back to Insert Mode.

### 2.2 Visual Feedback
1. The status bar must clearly indicate the current mode on the bottom-left of the screen (e.g., a green `INSERT` block, a red `NORMAL` block, or a yellow `COPY` block).
2. The status bar must highlight the active tab in green, using a clean ` #I:#W ` format.
3. The status bar must highlight any background tabs with active processing (stdout output) in yellow.

### 2.3 Browser-Style Vertical Tabs
1. The environment must support a vertical list of tabs/windows.
2. The vertical list should be accessible via `Space` (in Normal mode).
3. Navigation within this list must use Vim keys (`j` for down, `k` for up).
4. The environment must provide quick text-based filtering/searching of these tabs via `/`.

### 2.4 Tab Management & Navigation
1. `c` creates a new tab.
2. New tabs must seamlessly spawn in the current working directory of the active pane.
3. `r` renames the active tab.
4. `Tab` and `Shift+Tab` must quickly cycle forward/backward through open tabs.
5. Keys `1` through `9` in Normal Mode must jump directly to tabs 1 through 9.
6. `X` (Shift+x) closes the current tab and all of its split panes.
7. `Q` (Shift+q) closes all tabs and terminates the entire session.

### 2.5 Pane Management (Splits)
1. `|` splits the active pane vertically (side-by-side).
2. `-` splits the active pane horizontally (top-and-bottom).
3. `h`, `j`, `k`, `l` navigates focus between split panes.
4. `x` closes the current pane.

### 2.6 Visual Copy & Scroll Mode
1. `v` in Normal Mode transitions the environment to Copy/Scroll Mode.
2. While in Copy Mode, `v` starts visual selection (begins highlighting text).
3. `Ctrl-v` toggles between normal visual selection and block/rectangle selection.
4. `y` copies the current selection to the macOS clipboard (using `pbcopy`) and exits Copy Mode.
5. `Escape` exits Copy Mode and returns to Normal Mode.

### 2.7 Environment Defaults
1. The scrollback buffer history limit must be increased to 50,000 lines.
