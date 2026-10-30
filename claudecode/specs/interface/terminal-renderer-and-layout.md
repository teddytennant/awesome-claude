# Terminal renderer and layout

**Status:** shipped
**Provenance:** both
**Sources:** docs `fullscreen`, `terminal-config`, `troubleshooting`, `interactive-mode`, `settings-reference`, `env-vars`; snapshot `ink/`, `components/`, `utils/fullscreen.ts`; changelog 2.1.97 through 2.1.314

## Purpose

Draw the whole interactive session in a terminal: transcript, prompt, footer, dialogs and status elements. It updates as a stream arrives without flicker, reads keyboard, mouse and focus input, and adapts to what each terminal emulator can do. Two presentation modes share this engine: the classic main-screen renderer and the alternate-screen fullscreen renderer. Fullscreen-only behaviour is in [fullscreen-mode-and-tui.md](fullscreen-mode-and-tui.md); plain-text output is in [accessibility.md](accessibility.md).

## Behaviour

### Renderer modes

1. The product MUST offer two renderers. Classic writes the conversation to the terminal's main screen, so it lands in native scrollback. Fullscreen uses the alternate screen buffer and scrolls inside the app.
2. Only one renderer MUST be active in a process. Switching relaunches the process (see the fullscreen spec).
3. `-p` and other headless paths MUST NOT load or use the interactive UI (since 2.1.283 they do not even load it).

### Rendering pipeline

The stages below are snapshot evidence of the implementation. The public record confirms a layout engine (2.1.161, 2.1.211) and incremental cell updates in fullscreen. Treat the rest as a design that MAY have moved.

4. UI is a React tree rendered by a custom reconciler onto a DOM-like node tree (`ink/reconciler.ts`, `ink/dom.ts`).
5. Layout uses flexbox through a Yoga binding (`ink/layout/`). Text nodes are measured by display width.
6. Each frame is painted into a cell-grid screen buffer, with styles, characters and hyperlinks interned in pools (`ink/screen.ts`).
7. The new frame is diffed against the previous one to produce patches (`ink/log-update.ts`). An optimizer drops no-ops and merges cursor moves and style transitions (`ink/optimizer.ts`).
8. Frames are throttled to about 60 per second (16 ms interval in the snapshot).
9. Where supported, each write MUST be wrapped in synchronized-output markers (DEC 2026) so old content stays until the new frame swaps in.
10. In the alternate screen, a scroll change MAY use a terminal scroll region (DECSTBM) rather than repainting. If a row has already entered scrollback in the main screen and needs to change, a full reset is required, because cursor moves cannot reach scrollback.
11. Content scrolled out of view MAY be frozen so it does not re-render (`components/OffscreenFreeze.tsx`).

### Terminal input

12. Input is read in raw mode and parsed into key, mouse, paste and focus events (`ink/parse-keypress.ts`, `ink/termio/`).
13. The renderer MUST enable bracketed paste (DEC 2004) and focus reporting (DEC 1004) where available.
14. Extended keys MUST be requested through the kitty keyboard protocol or xterm `modifyOtherKeys`. Since 2.1.269, any terminal that answers the kitty keyboard query gets them, which covers SSH and unrecognised terminals such as foot and Alacritty 0.16+.
15. Mouse capture uses SGR tracking (DEC 1000, 1002, 1003, 1006) and is enabled only in fullscreen.
16. Capabilities MAY be probed at startup. Synchronized output MUST be probed rather than assumed (see Failure modes for tmux).
17. All modes the app sets MUST be restored on exit and on suspend (`Ctrl+Z`, Unix only). While a GUI editor is open (`/memory`, `/plan`, `/keybindings`, `Ctrl+G`), mouse and focus reporting MUST be off so no escape garbage appears.

### Text and Markdown

18. Width calculation MUST handle wide CJK and emoji cells, bidirectional text and tab stops. Since 2.1.295 tab stops count from where the text starts, not the screen's left edge.
19. Assistant Markdown renders with headings, lists, blockquotes (a continuous left bar across wrapped lines, 2.1.97), GFM task checkboxes (2.1.149) and tables.
20. Tables MUST display at most 200 rows, followed by a `… N more rows not shown` line. The cap is display-only: the conversation and `/copy` keep every row.
21. Code blocks and diffs use a built-in syntax highlighter (highlight.js 11 since 2.1.198). Six rarely used languages were removed in 2.1.251. A block with no language is coloured like inline code (2.1.280).
22. `maxProseWidth` (whole number, minimum 40) MUST cap paragraphs, headings, lists and blockquotes. Tables and code blocks keep the full width.
23. Hyperlinks use OSC 8 when supported or forced. A wrapped URL MUST stay one link (2.1.113). A link target that is a network or automounter path, contains a control character or leads with an invisible character MUST render as plain text (2.1.247).
24. `owner/repo#N` references become links for the host from the git remote. They stay plain for a bare `#N`, nested GitLab paths, code spans and blocks, replies over about 1,000 lines or 100,000 characters, and bitbucket.org, codeberg.org and gitea.com remotes.
25. Long file paths on tool rows truncate in the middle (2.1.239). Long single-line writes truncate instead of paginating (2.1.105).

### Screen regions

26. Top to bottom in a normal session: startup logo and notices, transcript, live status area, queued messages, prompt box, footer.
27. Queued messages MUST render in the conversation above the spinner (since 2.1.281). Sent and queued messages stay gray until Claude starts on them. A prompt sent with nothing running or queued shows in normal colour at once (2.1.286).
28. The spinner shows a rotating verb, an optional tip and live counters. Collapsed tool rows show a ticking elapsed time (2.1.210, dimmed in 2.1.234). The end-of-turn line shows duration and finish time, such as `✻ Sautéed for 23s · done 6:05 PM` (2.1.246), subject to `showTurnDuration`, `timeFormat` and `timeZone`.
29. `prefersReducedMotion` MUST reduce or remove spinner, shimmer and flash effects.
30. The footer MUST keep its indicators on the mode-indicator row at narrow widths (2.1.98). It holds the mode badge, PR or MR badge, `footerLinksRegexes` badges (at most 5), agent panel, artifact pill (`⧉ name` or `⧉ N`, 2.1.281) and hints. A custom status line sits in its own row above the badges.
31. Dialogs open as framed blocks. A dialog that overflows the terminal MUST scroll with arrows, PgUp/PgDn, Home/End and the wheel, in both renderers (2.1.121). In screens of list rows, overflow rows read `↑ N more` and `↓ N more` (2.1.286), and each row's details line up in one column (2.1.286).
32. The `/` and `@` suggestion lists show a `❯` pointer on the selected row, so the selection does not depend on colour (2.1.290).
33. Mods can draw a band above the prompt, docked panes and toasts. A docked pane MUST stay within 45% of terminal width (2.1.305). A mod's `Image` draws in kitty, Ghostty and iTerm2 3.5+ under fullscreen rendering, and inside tmux with passthrough and focus events on (2.1.305, 2.1.310). A failed mod draw MUST name the mod and say nothing was drawn (2.1.289).

### Terminal integration

34. The terminal title reflects the session name or an AI-generated title, with a busy glyph. A terminal that reports OSC 7501 support gets no glyph. `CLAUDE_CODE_DISABLE_TERMINAL_TITLE=1` disables title updates, the title-generation request and OSC 7501 reporting.
35. OSC 7501 (Program Status Protocol, 2.1.295) reports working, waiting or done for interactive sessions. It is skipped inside tmux and in background sessions.
36. `terminalProgressBarEnabled` controls the progress indicator, sent only to ConEmu, Ghostty 1.2.0+ and iTerm2 3.6.6+. It stays on while background subagents or workflows run after the turn ends.
37. `Ctrl+L` MUST force a full redraw, keeping input and conversation.
38. When the terminal is slow or paused, output MUST NOT fall further behind while it catches up (2.1.275).
39. The renderer MUST skip sequences that VTE older than 0.53 prints as stray text such as `>0q` and `>4m` (2.1.301).
40. `CLAUDE_CODE_FORCE_SYNC_OUTPUT=1` forces synchronized output where detection misses it, such as Emacs `eat` (2.1.129).

## Configuration & interfaces

| Key or variable | Effect |
|---|---|
| `tui` | `"default"` or `"fullscreen"` |
| `maxProseWidth` | Prose wrap cap in columns |
| `prefersReducedMotion` | Reduce animation |
| `syntaxHighlightingDisabled` | Plain code in diffs, blocks, previews |
| `CLAUDE_CODE_SYNTAX_HIGHLIGHT=false` | Plain diff output only |
| `terminalProgressBarEnabled` | Tab or taskbar progress |
| `spinnerVerbs` | `{verbs, mode: "append"\|"replace"}`; empty replace keeps built-ins |
| `spinnerTipsEnabled`, `spinnerTipsOverride` | See [onboarding-tips-and-powerup.md](onboarding-tips-and-powerup.md) |
| `showTurnDuration`, `timeFormat`, `timeZone` | End-of-turn line |
| `footerLinksRegexes` | Footer badges (user or managed scope only) |
| `prUrlTemplate` | Rewrites rendered PR links |
| `FORCE_HYPERLINK` | `1` on, `0` off; `false`, `no`, `off` mean off since 2.1.314 |
| `CLAUDE_CODE_FORCE_SYNC_OUTPUT` | Force DEC 2026 |
| `CLAUDE_CODE_TMUX_TRUECOLOR` | Any non-empty value allows 24-bit colour in tmux, including `0` |
| `CLAUDE_CODE_DISABLE_TERMINAL_TITLE` | No title or OSC 7501 |
| `CLAUDE_CODE_HIDE_CWD` | Hide cwd in the logo |

`footerLinksRegexes` badge rules: captures are URL-encoded and the link must keep the template's origin; URLs over 2048 characters are dropped; the scheme must be `https`, `http` or a listed editor or workspace scheme; labels truncate to 28 columns; `/clear` removes badges. Patterns run on the main thread at turn end, so a catastrophic regex freezes the UI.

## Failure modes & edge cases

- tmux through the 3.6 series has no synchronized output. Newer tmux is detected automatically (corrected note in 2.1.212). Without it, expect more flicker.
- Editor integrated terminals (VS Code, Cursor, Devin Desktop) can garble text through the GPU renderer. `/terminal-setup` sets `terminal.integrated.gpuAcceleration` to `"off"`.
- Without detected hyperlink support, links stay plain unless forced. The footer PR badge is a link regardless (2.1.217).
- A very large table in a resumed session no longer stalls, because of the row cap (2.1.208).
- Issue-link reference cut-offs are sizes, so a very long reply loses its links.

## Changes since the snapshot

- 2.1.89: `CLAUDE_CODE_NO_FLICKER` shipped publicly. 2.1.110: `/tui` and `tui`. 2.1.132: `CLAUDE_CODE_DISABLE_ALTERNATE_SCREEN`.
- 2.1.129: forced synchronized output. 2.1.212: tmux note corrected. 2.1.269: kitty query for unknown terminals.
- 2.1.149, 2.1.208, 2.1.280: task checkboxes, 200-row table cap, unnamed-language colouring.
- 2.1.247: link target sanitising. 2.1.282: `maxProseWidth`. 2.1.295: OSC 7501 and tab-stop origin. 2.1.301: VTE sequence skip. 2.1.314: `FORCE_HYPERLINK` word values.
- Performance: 2.1.147, 2.1.161, 2.1.169, 2.1.196, 2.1.203, 2.1.208, 2.1.211, 2.1.257, 2.1.259, 2.1.261, 2.1.267, 2.1.275 reduce per-frame, streaming, resize and keystroke work.

## Open questions

- Whether the snapshot pipeline (frame interval, cell pools, DECSTBM optimisation) is still accurate.
- Whether OSC 133 turn markers are emitted outside screen reader mode. Docs mention them only there.
- Whether `/config` exposes every animation and footer key shown here.
