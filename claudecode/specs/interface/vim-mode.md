# Vim mode

**Status:** shipped
**Provenance:** both
**Sources:** docs `interactive-mode`, `keybindings`, `terminal-config`, `settings-reference`, `statusline`; snapshot `vim/`, `hooks/useVimInput.ts`, `components/VimTextInput.tsx`; changelog 2.1.92 through 2.1.301

## Purpose

Optional vim-style editing in the prompt. It works at the text-input layer, separate from the keybinding system, and supports NORMAL, INSERT and VISUAL modes.

## Behaviour

### Enabling

1. Enabled by `editorMode: "vim"` or `/config` → Editor mode. `/vim` was removed in 2.1.92.
2. The mode is visible as `-- INSERT --` style text below the prompt, unless a status line sets `hideVimModeIndicator`.
3. `Enter` submits in INSERT mode, unlike real vim. `o`, `O` or `Ctrl+J` insert newlines.
4. Mode, cursor and the yank register MUST survive `Ctrl+O`, panels, dialogs and history search (2.1.221, 2.1.235).
5. Agent view prompts, and the `Other` row of questions, also support vim editing. `Esc` in agent view switches mode and keeps text (2.1.239).

### State machine

6. Snapshot model: `VimState` is INSERT (tracking inserted text for dot-repeat) or NORMAL (a `CommandState` parser moving through idle, count, operator, operator count, find, text object, `g`, replace and indent states). VISUAL was added after the snapshot. Counts cap at 10,000 in the snapshot.

### Mode changes

7. `Esc` or `Ctrl+[` to NORMAL from INSERT or VISUAL. `i`, `I`, `a`, `A`, `o`, `O` to INSERT. `v` and `V` to VISUAL.
8. `vimInsertModeRemaps` maps a two-printable-character INSERT sequence to `"<Esc>"`, the only target. The first character inserts normally. If the second arrives within one second, the pending character is removed and the mode changes, leaving neither in the buffer. Otherwise both stay. Other lengths or targets are ignored.
9. That setting MUST be ignored in project and local settings files, so a repository cannot remap keystrokes.

### NORMAL motions

10. `h j k l`, `Space`; `w e b`; `0 $ ^`; `gg`; `G`; `f F t T {char}`; `;` `,`; `%`.
11. `%` jumps to the matching `()`, `[]` or `{}`, starting from the next bracket on the line if not on one (2.1.301). `gj`/`gk` exist (changelog evidence).
12. `/` opens reverse history search, like `Ctrl+R` (2.1.152). The empty prompt hints how to reach the command menu: `Esc`, `i`, `/`.
13. `?` shows help.
14. At the start or end of input, `j`/`k` and arrows go to history, and can select the footer pill (2.1.98). `←` on an empty prompt opens agent view from NORMAL as well as INSERT.

### NORMAL editing

15. `x`, `r{char}`, `s`, `S`, `dd`, `D`, `cc`, `C`, `yy`, `Y`, `p`, `P`, `>>`, `<<`, `J`, `u`, `.`, `~`.
16. Operators `d c y` with `w e b`, `0`, `%`, `f`/`t`, `j`/`k`, `gg`/`G`, and text objects.
17. Text objects: `iw aw iW aW`, `i" a"`, `i' a'`, `i( a(`, `i[ a[`, `i{ a{`.
18. `u` steps one command at a time (2.1.178). `.` honours a typed count.
19. Vim deletes through `f`/`t` remove a collapsed paste placeholder whole, and `p` restores it.

### VISUAL

20. `v` is character-wise and `V` is line-wise. Motions extend. `Ctrl+V` block mode is not supported.
21. Actions: `d x y c s p`, `r{char}`, `~ u U`, `> <`, `J`, `o` (swap ends), text objects. `v`/`V` toggle kinds or exit.
22. `p` replaces the selection with the register, respecting whether the yank was whole lines.

### Interaction with keybindings

23. `Esc` in vim INSERT switches mode; it does not fire `chat:cancel`. Since 2.1.119 it also does not pull a queued message back.
24. Most Ctrl shortcuts pass through. Vim keys cannot be remapped through `keybindings.json`.
25. `Space` starts dictation only where it would type, so not outside INSERT. A modifier-key binding works in any mode.
26. In a question's `Other` row, the field starts in INSERT, except in screen reader mode. `Esc` changes mode or drops a partial command. A further `Esc` from NORMAL cancels. Binding `select:cancel` to a Ctrl or Alt key gives one-press cancel for single-select questions; it does not work in screen reader mode or multi-select.

## Configuration & interfaces

| Key | Notes |
|---|---|
| `editorMode` | `normal` or `vim`; any settings file; `/config` writes user settings |
| `vimInsertModeRemaps` | User or managed only; requires `editorMode: "vim"` |
| `statusLine.hideVimModeIndicator` | Hide built-in indicator |
| status-line `vim.mode` | `NORMAL`, `INSERT`, `VISUAL`, `VISUAL LINE`; absent when off |

## Failure modes & edge cases

- `Ctrl+[` MUST leave INSERT in terminals that encode modified keys, including under the kitty protocol (2.1.243).
- Cursor MUST NOT rest past the end of a line, on an image placeholder's bracket, or inside an accented letter. Several fix releases address these.
- `w` stops on empty lines, and `dw`/`yw` stop at line end (2.1.314).
- Fast or unbracketed paste into INSERT must stay repeatable with `.`.
- A count larger than remaining lines on `gj`/`gk` with an operator moves only.

## Changes since the snapshot

- 2.1.92: `/vim` removed.
- 2.1.98: boundary `j`/`k` reach history and footer.
- 2.1.118: VISUAL and VISUAL LINE.
- 2.1.119: Esc no longer recalls queued messages.
- 2.1.152: `/` history search.
- 2.1.208: `vimInsertModeRemaps`.
- 2.1.211: `s` and `S` in NORMAL.
- 2.1.235: mode and cursor preserved over panels.
- 2.1.281 (per docs): `d0`, `c0`, `y0`.
- 2.1.301: `%`, `d%`, `c%`, `y%`.

## Open questions

- The current count cap, and whether the snapshot's state names survive.
- `gj`/`gk`, `W`, `B`, `E`, `~` in NORMAL appear in changelog or snapshot evidence but not in the doc table.
- First release of agent-view vim support; 2.1.239 only fixed its Esc handling.
