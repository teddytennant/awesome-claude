# Accessibility

**Status:** shipped
**Provenance:** post-leak (since v2.1.200, 2026-07-03; announced v2.1.208, 2026-07-13)
**Sources:** docs `accessibility`, `settings-reference`, `env-vars`, `cli-reference`, `terminal-config`, `keybindings`, `vs-code`; changelog 2.1.200 through 2.1.311; snapshot has only `CLAUDE_CODE_ACCESSIBILITY`, reduced motion and daltonized themes

## Purpose

Make the CLI usable with screen readers, magnifiers, reduced motion and colour vision differences. The central feature is a screen reader mode that replaces the visual UI with linear labelled text.

## Behaviour

### Enabling screen reader mode

1. Opt-in. It is never auto-detected.
2. Sources, strongest first: `--ax-screen-reader`, `CLAUDE_AX_SCREEN_READER` (`0` forces off, even with the setting on), `axScreenReader`.
3. Project and local settings MUST NOT turn the mode on or off, including through an `env` block. If only a project asks, startup prints `Screen reader mode is off: project settings can't turn it on`. `axScreenReader: false` in user settings silences it.
4. Valid setting scope: user, managed, or a `--settings` file.
5. The first line MUST confirm the source: `[Screen Reader Mode: on via flag]`, `...via env]`, `...via settings]`.
6. After that line, the prompt waits 3 seconds, so the reader finishes. Any key ends the wait. `CLAUDE_AX_STARTUP_QUIET_MS` changes it (2.1.217).
7. Over SSH, set it on the machine running Claude Code.

### Rendering

8. No box-drawing chrome, no colour-only cues, no redraw of unchanged content, spinners as static text, decorative glyphs hidden (2.1.200).
9. Forces the classic renderer, and ignores `tui`. `/tui fullscreen` prints an explanation. Attached background sessions still render fullscreen, in the alternate screen, with no scrollback.
10. Tables read as `Header: value` sentences. Diffs read line by line with `+` and `-`.
11. Everything stays in native scrollback.
12. Each transcript item starts with a searchable label:

| Label | Meaning |
|---|---|
| `you:` | User |
| `claude:` | Reply |
| `thinking:` | Thinking |
| `tool:` | Tool activity |
| `tool error:` | Failed tool |
| `error:` | Conversation error |
| `warning:` | Warning |
| `Permission Required:` | Prompt |
| `Cost:` | Exit summary, if costs show |

13. Search boxes say `Search:`. Questions list as `Questions: Color (answered), Pages` (2.1.311). Answered questions say "answered" (2.1.288). `/mcp` reads disabled as "off" (2.1.281).
14. OSC 133 markers at turn boundaries let terminals jump between turns. They are not emitted in WezTerm; macOS Terminal ignores them. Search `you:` there.

### Cursor and echo

15. The terminal cursor stays on the input caret, so read-current-line reads the prompt.
16. Typing or backspacing at end of line writes only changed characters, so the echo is exact.
17. New text moves the cursor back to the prompt. Users should stop their reader following the cursor to read earlier output.
18. `CLAUDE_AX_PREPARK_MS` delays writes with the cursor at line start. Default 0 since 2.1.287; earlier 50.

### Announcements

19. Word and line deletions announce the removed text: `Ctrl+W`, `Alt+D`, `Option+Delete`, `Ctrl+Backspace`, `Ctrl+U`, `Cmd+Backspace`, `Ctrl+K` (2.1.218).
20. `Shift+Tab` announces the mode once, such as `[plan mode on]`. Approving a plan announces too (2.1.288). Rule deletion in `/permissions` says so (2.1.311).
21. Short announcements stay until the next key or until something above changes (2.1.288).

### Menus and prompts

22. Arrow menus become numbered lists followed by a `Select with numbers` prompt naming the range. Typing a number and `Enter` chooses. Out-of-range input reports the range and retries.
23. `Escape` cancels when the prompt ends `or Escape to cancel`.
24. `/effort` becomes a numbered list (2.1.233).
25. Yes-or-no prompts take typed `y`, `n`, `yes` or `no`.
26. Vim's `Other` row does not start in INSERT.

### Bell

27. Rings BEL at reply end, when a prompt needs an answer, and when a tool over 5 seconds finishes.
28. `/terminal-setup` leaves the bell setting alone in this mode.

### Other options

29. `CLAUDE_CODE_ACCESSIBILITY=1` keeps a visible terminal cursor that tracks the caret and, since 2.1.218, highlighted rows, for magnifiers. It disables the inverted-text cursor.
30. `prefersReducedMotion` reduces animation, including the voice level cursor.
31. `theme`: `dark-daltonized` and `light-daltonized`.
32. `preferredNotifChannel: "terminal_bell"` gives a similar bell outside the mode.
33. Selected `/` and `@` rows carry `❯`, so selection is not colour-only (2.1.290).
34. Spell check is off in the mode.

### VS Code

35. The chat panel announces activity to screen readers without a setting (2.1.236). The mode applies to the terminal interface only.

## Configuration & interfaces

| Option | Type |
|---|---|
| `--ax-screen-reader` | Flag |
| `CLAUDE_AX_SCREEN_READER` | Env; `1` on, `0` off |
| `axScreenReader` | Setting |
| `CLAUDE_AX_STARTUP_QUIET_MS` | Env |
| `CLAUDE_AX_PREPARK_MS` | Env |
| `CLAUDE_CODE_ACCESSIBILITY` | Env |
| `prefersReducedMotion`, `theme`, `preferredNotifChannel` | Settings |
| `syntaxHighlightingDisabled` | Setting; can help readers |

## Failure modes & edge cases

- A `/plan` command mode change is not announced.
- Costs are announced only at exit.
- `claude attach` enters the alternate screen. Leave with Left Arrow on an empty prompt, or `Ctrl+Z` with a dialog focused.
- `-p` output is unchanged and already plain.
- VoiceOver once read typed spaces as "new line"; echo MUST stay exact.

## Changes since the snapshot

- 2.1.200: output cleaned. 2.1.208: announced.
- 2.1.217, 2.1.218, 2.1.233: startup quiet, deletions, numbered effort.
- 2.1.287: prepark default 0. 2.1.288, 2.1.311: announcements and question lists.

## Open questions

- Docs give `--ax-screen-reader` a 2.1.181 floor, and the changelog announces it at 2.1.208.
- Whether the mode works in all dialogs, such as `/plugin` and `/config`.
- Whether numbered menus exist in agent view.
