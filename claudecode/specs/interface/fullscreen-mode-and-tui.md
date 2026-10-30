# Fullscreen mode and /tui

**Status:** preview (research preview; default for many users)
**Provenance:** both (internal in snapshot; public since v2.1.89, 2026-03-31)
**Sources:** docs `fullscreen`, `interactive-mode`, `settings-reference`, `errors`, `accessibility`, `agent-view`; snapshot `utils/fullscreen.ts`, `components/FullscreenLayout.tsx`, `components/VirtualMessageList.tsx`, `ink/components/AlternateScreen.tsx`, `ink/components/ScrollBox.tsx`, `ink/selection.ts`; changelog 2.1.89 through 2.1.314

## Purpose

An alternate-screen renderer that stops flicker, keeps memory flat in long sessions by rendering only visible messages, and adds in-app scrolling, selection and mouse control. "Fullscreen" means owning the drawing surface like `vim`. It has nothing to do with window size.

## Behaviour

### Choosing the renderer

1. Attached background sessions MUST always render fullscreen, whatever `tui` or `CLAUDE_CODE_DISABLE_ALTERNATE_SCREEN` say.
2. Other sessions in screen reader mode MUST use classic.
3. Otherwise the first matching row wins:

| Situation | Renderer |
|---|---|
| `CLAUDE_CODE_DISABLE_ALTERNATE_SCREEN=1` or `CLAUDE_CODE_NO_FLICKER=0` | Classic |
| `CLAUDE_CODE_NO_FLICKER=1` | Fullscreen |
| Fullscreen was turned off after a failed start on this machine | Classic |
| iTerm2 `tmux -CC`, or SSH to Claude Code running on Windows | Classic |
| `tui` is saved | The named renderer |
| No feature-flag fetch, and startup dialog no longer offered here | Classic |
| No feature-flag fetch, and first launch on this machine was v2.1.239+ | Fullscreen |
| Flags fetched, and first used on or after 2026-05-06 | Fullscreen |
| Anything else | Classic |

4. When both `CLAUDE_CODE_NO_FLICKER` and the disable variable are set to conflicting values, fullscreen MUST be off.
5. If a user in classic has no `tui` saved, a startup dialog MAY offer the switch. Accepting relaunches like `/tui fullscreen` and saves the setting only once the relaunched session starts successfully. **Not now** stops offers on this machine. Offers stop after three launches shown, answered or not.

### /tui

6. `/tui` with no argument prints the active renderer. If a failed start is why classic is active, the `Current renderer` line MUST say so.
7. `/tui fullscreen` and `/tui default` save `tui` and relaunch with the conversation intact. `CLAUDE_CODE_NO_FLICKER` is cleared from the relaunched process so the saved value applies.
8. The relaunch MUST carry: the conversation as shown (so a `/rewind` point, or an empty conversation if rewound past the start), permission mode, effort, the model last picked with `/model`, `--allowed-tools`/`--disallowed-tools` rules, `--agent`, `--agents`, `--append-system-prompt`, `--system-prompt-snapshot`, and `--chrome`/`--no-chrome`.
9. The switch MUST be refused, printing `Cannot switch renderers in this session` with reasons and saving nothing, when a restriction cannot be carried: for example `--system-prompt`, a `--tools` allowlist, `--setting-sources`, or session-only deny or ask rules added by a hook or SDK permission update. A separate `Cannot switch renderers while work is running in the background` refusal exists.
10. In screen reader mode, `/tui fullscreen` prints an explanation and saves nothing (except in attached background sessions, which are already fullscreen).
11. `/tui default` keeps the choice without relaunching when recovering from a failed start. Otherwise it MAY show an optional feedback prompt (Enter sends, Esc skips), then relaunches either way.
12. A usage-limit wait ends on `/tui`; it does not carry across.

### Failed-start protection

13. A session counts as started once it has drawn its first frame and then stayed up 10 seconds or ended via `/exit`, Ctrl+C or Ctrl+D.
14. After one failed start: next session is classic, prints `Claude Code's fullscreen renderer didn't finish starting last time on this machine`, and fullscreen is tried again in the session after.
15. After two: classic continues, prints `Claude Code's fullscreen renderer has repeatedly failed to start on this machine`, and stays classic silently until an update or `/tui fullscreen`.
16. Counting rules: only sessions fullscreen by setting, accepted dialog or default count. `CLAUDE_CODE_NO_FLICKER=1` renders fullscreen regardless and does not count. Counts are per version, and a success resets them. An accepted dialog followed by a crash prints neither line and suppresses the dialog for that version.

### Layout

17. The prompt box MUST stay fixed at the bottom. Only visible messages stay in the render tree.
18. `CLAUDE_CODE_DISABLE_VIRTUAL_SCROLL=1` renders every message, as a workaround for blank regions.
19. While scrolled up, a dim sticky header row shows the most recent prompt above the view. Clicking it jumps to that prompt.
20. The diff panel, mod panes and bands sit beside or above the transcript. See `/diff` in [slash-commands-catalogue.md](slash-commands-catalogue.md).
21. Remote Control status shows in the header in fullscreen (2.1.268).
22. Resuming a compacted session stops scroll-up at the `Conversation compacted` row. In a live session, repeated compactions keep the full pre-compaction history in scrollback (2.1.224).

### Scrolling

23. Defaults: `PgUp`/`PgDn` half a screen; `Ctrl+Home` start; `Ctrl+End` latest, resuming auto-follow; wheel a few lines.
24. Scrolling up MUST pause auto-follow. A `Jump to bottom` button shows while scrolled up, with a count such as `3 new messages`. Clicking it, `Ctrl+End`, or reaching the bottom resumes following. Typing in the prompt MUST NOT jump the view (2.1.121).
25. The button's hint MUST match what the keyboard can send: on macOS it suggests clicking or `Fn+↓`, and a rebound `scroll:bottom` shows on every platform. It MUST shorten rather than wrap on narrow terminals.
26. `autoScrollEnabled: false` disables following entirely. Permission prompts and other dialogs needing a response MUST still come into view.
27. `CLAUDE_CODE_SCROLL_SPEED` multiplies wheel distance: any positive value up to 20, including below 1.
28. `/scroll-speed` adjusts it live: `←`/`→` step, `r` resets to auto-detected default, `Enter` saves to `~/.claude/settings.json`. Whole steps up to 10, and quarter steps down to 0.25 where the terminal supports finer control. A higher env value shows and saves as 10.
29. `wheelScrollAccelerationEnabled` (default true) speeds up fast spins.
30. JetBrains IDE terminal: scroll handling is built in, `CLAUDE_CODE_SCROLL_SPEED` is ignored, `/scroll-speed` is unavailable. The 2025.2 wheel bugs are mitigated at runtime, with a one-time hint.

### Mouse

31. Click positions the cursor in the prompt; click accepts `/` and `@` suggestions (hover highlights); click chooses or toggles menu options and focuses free-text rows; click on a `/config` value changes it.
32. Wheel scrolls menus and lists under the pointer. Scrollbars appear beside overflowing lists while hovered: click the track, drag the thumb, click or hold arrows. Clicks on arrows and bars act on release (2.1.311). `↑ N more` and `↓ N more` rows jump to that end.
33. Clicking a collapsed tool result toggles it, along with `!` output and dim `Message from @<sender>` lines. Only rows with more to show are clickable.
34. Clicking the `to send now` hint under a queued message sends it (2.1.312).
35. URLs and file paths open with `Cmd`+click (macOS) or `Ctrl`+click, not a plain click (2.1.181). The link under the pointer is underlined (2.1.296). File paths open in the file manager; on Linux and WSL this needs `org.freedesktop.FileManager1`. UNC paths stay plain text. Ghostty and Warp on macOS allow a plain click, because `Cmd` cannot be encoded. xterm.js terminals defer to their own link handler.
36. Right-click paste (Windows, Linux) and middle-click paste (Linux) fire on release; moving away cancels (2.1.287).

### Selection and copying

37. Click-drag selects in-app; double-click selects a word (paths and whole URLs as one unit); triple-click a line.
38. With `copyOnSelect` (global config, default true) release copies. Otherwise `Ctrl+Shift+C`, or `Cmd+C` under kitty-protocol terminals. With a selection active, `Ctrl+C` copies rather than cancels.
39. `Shift`+arrows extend; `Shift+↑/↓` scroll at the edge; `Shift+Home/End` extend to line ends.
40. `Esc` performs its usual action and keeps the selection (2.1.234). Paging keys and modified navigation keep it. Other keys clear it. A key bound to `selection:clear` always clears.
41. Clipboard path: macOS `pbcopy`; Linux `wl-copy`, then `xclip` or `xsel`, writing clipboard and PRIMARY; Windows and WSL PowerShell `Set-Clipboard`; tmux also writes the paste buffer; SSH falls back to OSC 52. A toast MUST state the path used.
42. A one-off native selection uses a terminal-specific modifier: `Fn` in Terminal.app, `Option` in iTerm2, otherwise `Shift`. The on-screen hint MUST show the right key, or the candidates when detection is impossible over SSH or tmux.

### Transcript mode

43. `Ctrl+O` toggles transcript mode, with `less`-style keys: `/` search, `n`/`N`, `j`/`k`, `g`/`G`, `{`/`}`, half and full paging, `?` help.
44. `[` writes the whole conversation, expanded, to native scrollback until exit. `v` opens it in `$VISUAL` or `$EDITOR` through a temp file. `Ctrl+O`, `Esc` or `q` exit.
45. `/focus` toggles a view with the last prompt, a one-line tool summary and the final response. It persists across sessions, and `viewMode` overrides it.

## Configuration & interfaces

| Key or variable | Effect |
|---|---|
| `tui` | Saved renderer |
| `viewMode` | `default`, `verbose`, `focus` |
| `autoScrollEnabled` | Follow output |
| `wheelScrollAccelerationEnabled` | Wheel acceleration |
| `copyOnSelect` | Global config only |
| `CLAUDE_CODE_NO_FLICKER` | `1` on, `0` off |
| `CLAUDE_CODE_DISABLE_ALTERNATE_SCREEN` | Force classic |
| `CLAUDE_CODE_DISABLE_MOUSE` | No mouse capture; wins over clicks variable |
| `CLAUDE_CODE_DISABLE_MOUSE_CLICKS` | Wheel only |
| `CLAUDE_CODE_ALT_SCREEN_FULL_REPAINT` | Repaint every cell each frame |
| `CLAUDE_CODE_DISABLE_VIRTUAL_SCROLL` | Render all messages |
| `CLAUDE_CODE_SCROLL_SPEED` | Wheel multiplier |

## Failure modes & edge cases

- `tmux -CC`: alternate screen and mouse tracking fail, so the renderer MUST stay classic unless forced. In the snapshot this used an environment heuristic plus a `tmux display-message` probe.
- Plain tmux needs `set -g mouse on` for the wheel. A one-time startup hint appears when mouse mode is off.
- ConPTY hosts can leave stale fragments. Set `CLAUDE_CODE_ALT_SCREEN_FULL_REPAINT=1`. Windows background sessions and agent view already do this.
- iTerm2 needs per-profile mouse reporting for wheel, click and selection.
- `Cmd+F` and tmux search cannot see the alternate screen. Use transcript `/` or `[`.
- iTerm2 and Terminal.app handle `Cmd+K` themselves. The app detects the cleared screen and repaints.
- Terminal.app does not support OSC 52, and iTerm2 blocks it until enabled. `/terminal-setup` enables it in iTerm2.

## Changes since the snapshot

- 2.1.89: public opt-in. 2.1.97: focus view (on `Ctrl+O`); 2.1.110: moved to `/focus`, plus `/tui`, `tui` and `autoScrollEnabled`.
- 2.1.132: disable variable. 2.1.139: `/scroll-speed`. 2.1.174: acceleration setting. 2.1.195: click-disable variable.
- 2.1.181: modifier required to open URLs. 2.1.234: Esc keeps selection. 2.1.239: offer extended to providers without flag fetch.
- `Ctrl+L`: 2.1.238 repaint only; 2.1.260 cleared the view; docs say repaint again from 2.1.280.
- 2.1.236 (per docs): failed-start protection.
- 2.1.260: diff panel. 2.1.271, 2.1.286, 2.1.311, 2.1.312: `/config` mouse, list and scrollbar, click-to-send.

## Open questions

- When the research-preview label ends.
- Whether snapshot scroll drain and sticky mechanics still apply.
- Exact conditions for the optional feedback prompt on `/tui default`.
