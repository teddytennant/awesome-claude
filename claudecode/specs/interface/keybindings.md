# Keybindings

**Status:** shipped
**Provenance:** both
**Sources:** docs `keybindings`, `interactive-mode`, `fullscreen`, `agent-view`; snapshot `keybindings/` (all files), `skills/bundled/keybindings.ts`; changelog 2.1.122 through 2.1.305

## Purpose

Let users rebind component-level actions through a JSON file, with chords, per-context resolution and hot reload. Fixed readline editing keys and vim keys are out of scope for this system.

## Behaviour

### File

1. Bindings live in `~/.claude/keybindings.json`. `/keybindings` creates or opens it. Edits apply without restart.
2. Shape: optional `$schema` and `$docs`, and a `bindings` array of `{ context, bindings: { "<keystroke>": "<action>" | null } }` blocks. `--safe-mode` skips custom keybindings.
3. `null` unbinds a default. Unbinding every chord on a prefix frees the prefix for a single-key binding. A chord in any active context keeps its prefix reserved.

### Syntax

4. Modifiers joined with `+`: `ctrl`/`control`; `shift`; `alt`/`opt`/`option`/`meta`; `cmd`/`command`/`super`/`win`. `cmd` is detected only where the terminal reports Super. `meta` and `cmd` are different groups.
5. Key names are case-insensitive, so `K` equals `k`. `shift+k` means Shift and K.
6. Space separates chord steps. Each step MUST arrive within 3 seconds of the last, or the chord cancels with a brief notice. (The snapshot used 1 second.)
7. Special keys: `escape`/`esc`, `enter`/`return`, `tab`, `space`, arrows, `pageup`, `pagedown`, `home`, `end`, `backspace`, `delete`, `wheelup`, `wheeldown`.
8. Ctrl shortcuts are written in Latin. On non-Latin layouts they match by US-layout position where the kitty protocol reports it, otherwise whatever the terminal sends. Layouts rearranging Latin letters match the typed letter.

### Resolution

9. Snapshot resolver model: all bindings in the active contexts are scanned and the last match wins, so user overrides beat defaults. Results are match, none, unbound, chord started or chord cancelled.
10. An unknown action MUST be skipped and the default binding for that key kept (2.1.246).
11. While a text field in a dialog has focus, a printable key without Ctrl, Alt or Cmd goes to the field. Keys that type nothing, modified keys, and second chord steps still reach bindings. At the main prompt, every key is matched first and typed only if nothing takes it (2.1.280).
12. While agent view is open, an `Agents` binding beats `Chat` or `Global` on the same key, and bindings fire on single keystrokes, so chords do not work there.
13. With a footer item selected, `Enter` opens it even if `Chat` rebinds `Enter`. `Chat` bindings on keys `Footer` does not bind still work.
14. Vim and keybindings are independent; see [vim-mode.md](vim-mode.md).
15. `Ctrl+C` or `Ctrl+D` twice closes most dialogs, not the app, and the first-press hint says which (2.1.281).
16. Shortcut hints MUST reflect rebinding, and show opt/cmd when connected from a Mac over SSH (2.1.198).

### Reserved keys

17. Not rebindable: `Ctrl+C`, `Ctrl+D`, `Ctrl+M` (Enter), `Ctrl+[` (Escape), `Ctrl+I` (Tab), `Ctrl+H` (backspace byte), Caps Lock.
18. Terminal conflicts to warn about: `Ctrl+B` (tmux), `Ctrl+A` (screen), `Ctrl+Z` (SIGTSTP).

## Configuration & interfaces

### Contexts

`Global`, `Chat`, `Autocomplete`, `Settings`, `Confirmation`, `Tabs`, `Help`, `Transcript`, `HistorySearch`, `Task`, `ThemePicker`, `Attachments`, `Footer`, `MessageSelector`, `DiffDialog`, `DiffPanel`, `ModelPicker`, `EffortSlider`, `Select`, `Plugin`, `AbovePrompt`, `AbovePromptInput`, `AbovePromptSelect`, `Pane`, `PaneField`, `Agents`, `Scroll`.

New since the snapshot: `DiffPanel`, `EffortSlider`, `AbovePrompt`, `AbovePromptInput`, `AbovePromptSelect`, `Pane`, `PaneField`, `Agents`, `Scroll`. A `Doctor` context existed before 2.1.205.

### Actions and defaults

| Group | Action = default |
|---|---|
| app | `interrupt`=Ctrl+C, `exit`=Ctrl+D, `redraw`=unbound, `toggleTodos`=Ctrl+T, `toggleTranscript`=Ctrl+O |
| history | `search`=Ctrl+R, `previous`=Up, `next`=Down |
| chat | `cancel`=Esc, `clearInput`=Ctrl+L, `clearScreen`=Cmd+K, `killAgents`=Ctrl+X Ctrl+K, `cycleMode`=Shift+Tab (Meta+M on Windows without VT), `modelPicker`=Meta+P, `fastMode`=Meta+O, `thinkingToggle`=Meta+T, `submit`=Enter, `queueSubmit`=Ctrl+X Enter, `sendNow`=Ctrl+Enter and Ctrl+X Ctrl+S, `newline`=Ctrl+J, `undo`=Ctrl+_ and Ctrl+Shift+-, `externalEditor`=Ctrl+G and Ctrl+X Ctrl+E, `stash`=Ctrl+S, `imagePaste`=Ctrl+V (Alt+V on Windows and WSL) |
| command | `command:<name>`=unbound; runs `/<name>` |
| autocomplete | `accept`=Tab, `dismiss`=Esc, `previous`=Up, `next`=Down |
| confirm | `yes`=Enter, `no`=Esc, `previous`=Up, `next`=Down, `nextField`=Tab (`/fast` only), `previousField`=inert, `toggle`=Space, `cycleMode`=Shift+Tab |
| permission | `toggleDebug`=inert |
| transcript | `toggleShowAll`=Ctrl+E (classic only), `exit`=q, Ctrl+C, Esc |
| historySearch | `next`=Ctrl+R, `accept`=Esc and Tab, `cancel`=Ctrl+C, `execute`=Enter, `cycleScope`=Ctrl+S (fullscreen) |
| task | `background`=Ctrl+B and Ctrl+X Ctrl+B |
| theme | `toggleSyntaxHighlighting`=Ctrl+T |
| help | `dismiss`=Esc |
| tabs | `next`=Tab and Right, `previous`=Shift+Tab and Left |
| attachments | `next`=Right, `previous`=Left, `remove`=Backspace and Delete, `exit`=Down and Esc |
| footer | `next`=Right, `previous`=Left, `up`=Up and Ctrl+P, `down`=Down and Ctrl+N, `openSelected`=Enter, `clearSelection`=Esc, `close`=x, `dismiss`=inert |
| diff (legacy viewer) | `dismiss`=Esc, `previousSource`=Left, `nextSource`=Right, `previousFile`=Up and K, `nextFile`=Down and J, `back`=unbound |
| diff panel | `app:toggleReplTab`=unbound, `app:cycleDiffBase`=Ctrl+X B, `app:diffFileListUp`=Ctrl+Up and Meta+Up, `app:diffFileListDown`=Ctrl+Down and Meta+Down, `app:toggleDiffNoiseFilter`=unbound, `app:toggleDiffPreSession`=unbound |
| modelPicker | `decreaseEffort`=Left, `increaseEffort`=Right, `thisSessionOnly`=s |
| effortSlider | `decreaseEffort`=Left, `increaseEffort`=Right, `toggleUltracode`=Tab, `thisSessionOnly`=s |
| select | `next`=Down, J, Ctrl+N; `previous`=Up, K, Ctrl+P; `pageUp`, `pageDown`, `first`=Home, `last`=End, `accept`=Enter, `cancel`=Esc |
| plugin | `toggle`=Space, `install`=I, `favorite`=F |
| abovePrompt | `toggle`=Ctrl+X Ctrl+A, `focus`=Ctrl+X Tab, `next`=Tab, `previous`=Shift+Tab, `press`=Enter, `leave`=Esc, `highlightNext`=Down, `highlightPrevious`=Up |
| pane | `scrollUp`, `scrollDown`, `pageUp`, `pageDown`, `top`, `bottom`, `grow`=Ctrl+X Left and Up, `shrink`=Ctrl+X Right and Down, `close`=Ctrl+X X, `next`, `previous`=unbound |
| settings | `search`=/, `retry`=R, `fixUsage`=F; reuses `select:accept` (Enter, Space) and `confirm:no` (Esc) |
| agents | `switchView`=Ctrl+S, `togglePin`=Ctrl+T, `find`=Ctrl+F, `rename`=Ctrl+R, `previousGroup`=Ctrl+Up and Meta+Up, `nextGroup`=Ctrl+Down and Meta+Down |
| voice | `pushToTalk`=Space |
| scroll | `lineUp`=wheelup, `lineDown`=wheeldown, `pageUp`, `pageDown`, `top`=Ctrl+Home, `bottom`=Ctrl+End, `halfPageUp`, `halfPageDown`, `fullPageUp`, `fullPageDown`=unbound |
| selection | `copy`=Ctrl+Shift+C and Cmd+C, `clear`=unbound, `extendLeft`, `extendRight`, `extendUp`, `extendDown`, `extendLineStart`, `extendLineEnd` |

Notes:

- `chat:clearInput` and `chat:clearScreen` both redraw despite their names. Both keep input and conversation.
- In `DiffDialog`'s detail view, pager keys bind standard scroll actions.
- `MessageSelector` has no actions of its own since 2.1.283. It takes `select:*`, and old `messageSelector:*` names still work.
- `diff:viewDetails` keeps working as `select:accept` in the file list.
- `cc-plugin-diff` handles the panel's cycle and scroll actions. Noise-filter and pre-session actions reach only the older panel used when that mod is off.
- In panels such as `/skills`, `/mcp`, `/tasks`, page and end bindings apply. In other lists PageUp and PageDown are fixed.

### Default `ctrl+x` chords by context

`Chat`: `ctrl+k`, `ctrl+e`, `enter`, `ctrl+a`, `ctrl+s`, `tab`. `Task`: `ctrl+b`. `DiffPanel`: `b`. `Pane`: `left`, `right`, `up`, `down`, `x`. `PaneField`: `x`.

### Validation

Warnings go to the debug log for parse errors, misspelled modifiers (the unknown part is dropped, with a suggestion, 2.1.283), a space next to `+` (it reads as a chord and never fires, 2.1.293), invalid contexts, non-string actions, unknown actions, reserved conflicts and duplicates. A file naming retired actions stays valid.

## Failure modes & edge cases

- A bare letter on `confirm:yes` also acts on dialogs that never show that letter.
- Files generated by `/keybindings` before 2.1.280 list `y` and `n` confirm bindings that stay until deleted.
- `Ctrl+Enter` needs extended keys.
- `Ctrl+Home` and `Ctrl+End` do not reach the app from a Mac keyboard by default. Rebind `scroll:bottom`.
- The `/effort` slider's Enter and Escape cannot be rebound.

## Changes since the snapshot

- Chord timeout now 3 seconds (documented; a guide fix in 2.1.283).
- `y`/`n` defaults removed from Confirmation (2.1.280). `Ctrl+E` explanation action removed (2.1.257). `doctor:fix` removed (2.1.205). `footer:dismiss` inert (2.1.281).
- `modelPicker:setAsDefault` replaced by `thisSessionOnly`, key `s` (2.1.153).
- Added: `selection:clear` (2.1.234), `chat:queueSubmit` (2.1.247), `chat:sendNow` (2.1.275), Agents actions (2.1.257, 2.1.288), `settings:fixUsage` (2.1.305), `effortSlider:*` (2.1.257, 2.1.284), above-prompt and pane actions, and chords (2.1.260).
- Not documented now, present in snapshot: `app:globalSearch`, `app:quickOpen`, `app:toggleBrief`, `app:toggleTeammatePreview`, `app:toggleTerminal`, `chat:messageActions`, `settings:close`.

## Open questions

- Whether the last-match-wins scan is still how overlapping contexts resolve. Current docs describe only special cases.
- Whether `app:toggleTeammatePreview` and `settings:close` still resolve.
- `Cmd+C` default for `selection:copy` depends on the kitty protocol; the full list of qualifying terminals is unknown.
