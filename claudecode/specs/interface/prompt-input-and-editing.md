# Prompt input and editing

**Status:** shipped
**Provenance:** both
**Sources:** docs `interactive-mode`, `terminal-config`, `commands`, `keybindings`; snapshot `components/PromptInput/`, `components/TextInput.tsx`, `hooks/useTextInput.ts`, `hooks/useTypeahead.tsx`, `hooks/usePasteHandler.ts`, `hooks/useArrowKeyHistory.tsx`, `hooks/useHistorySearch.ts`, `history.ts`; changelog 2.1.89 through 2.1.314

## Purpose

The prompt box is where the user writes messages, runs commands and shell lines, attaches files and images, and steers a running turn. It behaves like a readline editor with autocompletion, multiline input, history and a queue.

## Behaviour

### Input routing

1. A leading `/` is a command or skill, recognised only at the start of the message; following text is its arguments. Up to six skills may be chained at the start of a message at the terminal.
2. A leading `!` enters shell mode. Pasting text starting with `!` into an empty prompt also enters it (2.1.89).
3. `@` triggers file path completion. With cross-session messaging available, at least one letter after `@` also suggests other live sessions (2.1.232).
4. `:` starts an emoji shortcode. `?` on an empty prompt toggles the shortcut panel; otherwise it types `?`.
5. `Enter` submits. Multiline methods: `\` then `Enter`, `Ctrl+J`, `Shift+Enter` where supported, `Option+Enter` with Option as Meta, or a paste.

### Editing keys

6. Fixed readline keys, not rebindable: `Ctrl+A/E` line start and end (of the logical line in multiline, 2.1.113); `Ctrl+K`, `Ctrl+U`, `Ctrl+W` kill; `Ctrl+Y` yank; `Alt+Y` yank-pop; `Alt+B/F` word motion; `Alt+D` word kill.
7. Word keys MUST treat a word as a run of letters and digits, so punctuation separates words. `Ctrl+W` MUST delete back to the previous whitespace (behaviour fixed in 2.1.261). In unspaced scripts such as Chinese and Japanese, word keys still move one word at a time.
8. `Alt+F` and `Alt+D` stop at the end of the current or next word.
9. `Ctrl+U` deletes to the line start, and repeats across lines. This is the doc's current behaviour; 2.1.111 notes said it cleared the whole buffer.
10. `Ctrl+_` or `Ctrl+Shift+-` undoes the last input edit.
11. `Ctrl+D` deletes forward when there is text. On an empty prompt, it exits on a second press within 800 ms.
12. `Ctrl+C` interrupts when running. Idle, the first press clears the prompt and the second exits.
13. `Esc Esc` clears a non-empty draft, saving it to history. On an empty prompt it opens the rewind menu.
14. `Ctrl+L` redraws. `Ctrl+G` or `Ctrl+X Ctrl+E` opens the external editor, on the cursor's line where the editor accepts a line number (2.1.286). With `externalEditorContext`, the buffer starts with the last 50 lines of Claude's previous reply as `#` comments, stripped on save.
15. `Ctrl+S` stashes the draft, or on an empty prompt restores text, cursor, paste content and input mode.
16. Up and Down first move inside a prompt of several visual rows. On the first or last row they navigate history. With a queue, `Up` on the first row takes queued items back.

### Autocomplete

17. The `/` menu filters as typed. See [slash-commands-system.md](slash-commands-system.md).
18. Mid-prompt completion: `/` after a space plus leading letters offers commands whose names start with those letters, so a path such as `/tmp/x` does not keep a list open. Only commands at the start of a message run.
    - Fullscreen: a list opens with no row highlighted, so `Enter` still sends; `Tab` inserts the top match.
    - Classic: ghost text shows the top match with a count such as `+2`; `Tab` inserts the only match or opens the list.
    - `Tab` on a bare mid-prompt `/` lists all commands. Plugin skills match on bare names and insert the qualified form.
19. `@` ranks a file whose name contains the query above one matching only across folders (2.1.280). `fileSuggestion` overrides suggestions with a command. `CLAUDE_CODE_DISABLE_FILE_MENTIONS` gives Claude paths rather than contents (2.1.299).
20. `/add-dir` and `/cd` (2.1.206) suggest directories.
21. Shell mode autocompletes from earlier `!` commands in the project and, from 2.1.193, live paths for tokens containing `/` (forward slash only, on Windows too).
22. `autocomplete:accept` is `Tab`. `Enter` in the `/` menu runs a highlighted suggestion; `chat:queueSubmit` submits the draft even with one highlighted.

### Emoji shortcodes

23. A complete `:name:` is replaced on the closing colon. `:` plus two or more characters opens suggestions; `Tab` or `Enter` inserts.
24. The shortcode MUST start the input or follow a space. Common alternate spellings and GitHub and Slack aliases are accepted (2.1.221, 2.1.257). `emojiCompletionEnabled: false` disables both behaviours.

### Spell check

25. Off by default (2.1.235). Underlines words shortly after typing pauses, never changing text. It checks only the input box, and never during shell mode, `Ctrl+R` search, dictation or screen reader mode.
26. It runs the first of `aspell`, `hunspell`, `ispell` on `PATH`, or the configured `checker` with no fallback.
27. It MUST skip commands, mentions, URLs, paths, flags, words with digits, underscores or inner capitals, backticked text, the word being typed, and Chinese, Japanese, Korean, Thai, Lao, Khmer and Myanmar text.
28. Two failures in a row, or three answers slower than 15 seconds, stop checking until restart. Details go to `[spellcheck]` debug lines.
29. `spellcheck` is read from managed, then `--settings`, then user settings, using only the first found, never project settings.

### Pasting

30. Text over 800 characters or more than three lines MUST collapse to `[Pasted text #N +L lines]`, with the full content sent. The `+N lines` marker in a truncated long paste is a full-width rule (2.1.111).
31. Paste contents are cached in `~/.claude/paste-cache/`, subject to `cleanupPeriodDays`.
32. Word, line and vim `f`/`t` deletes reaching inside a placeholder remove it whole. `Ctrl+Y` or vim `p` restores it.
33. A recalled prompt resends the full paste. If the cache is gone, the literal placeholder MUST NOT be sent: plain prompts drop it and notify; `!` and `/` commands, or prompts left empty, cancel submission and keep the text (with a cancel-and-confirm step since 2.1.224). Recalled paste numbers renumber on accept (2.1.224).
34. In sessions that fetch feature flags, Claude is told pasted content came from elsewhere and that instructions inside it count only where the typed message asks. Without flag fetch, pastes are not marked.
35. In agent view, pasting the same text again expands the placeholder (2.1.207).

### Images

36. `Ctrl+V` (also `Cmd+V` in iTerm2, `Alt+V` on Windows and WSL) inserts `[Image #N]` at the cursor. No trailing space (2.1.89). A `Pasting…` footer hint shows during clipboard reads (2.1.132). Reads MUST NOT block the event loop (2.1.232).

### Invisible characters

37. On `Enter`, tag characters, bidirectional controls and zero-width spaces are removed from the prompt and from collapsed paste content. Joiners used by Persian and Indic scripts and selectors inside emoji sequences stay.
38. If anything was removed, that `Enter` sends nothing. The cleaned text returns with a notice such as `Removed 3 invisible characters · review and press Enter to send` (2.1.277).
39. A prompt passed on the command line is cleaned and sent with a notice. If the result begins with `/`, it goes to the input box for review.

### History

40. History is per working directory, and `Up` reaches earlier sessions of the project. After `/clear`, the new session's prompts come first. Consecutive duplicates are recorded once (2.1.147).
41. A cleared draft returns on `Up`: right away on an empty prompt (2.1.288), or after sending (2.1.292). Ten cleared drafts are kept per session, with paste content, and discarded on exit.
42. `Ctrl+R` differs by renderer:
    - Classic: inline search over all projects, newest first, deduplicated. `Ctrl+R` cycles older; `Tab` or `Esc` accept; `Enter` runs; `Ctrl+C` or `Backspace` on an empty query cancel.
    - Fullscreen: a dialog with `Up`/`Down`, `Ctrl+S` scope cycling (session, project, all), `Enter` or `Tab` to place, `Esc` to cancel. Recent prompts appear at once and older ones fill in.
43. Search matches inside collapsed paste pills (2.1.314).
44. `CLAUDE_CODE_SKIP_PROMPT_HISTORY=1` stops writing history and transcripts.

### Queueing

45. `Enter` during a turn queues the message. Plain messages are delivered after running tool calls finish, within the same turn. Remaining messages go out in order when the turn ends. Commands and shell lines run one at a time after the turn.
46. `chat:sendNow` (`Ctrl+Enter`, `Ctrl+X Ctrl+S`, 2.1.275) sends queued messages and the draft now. Work that can move to the background does, and Claude reads the messages in the same turn; otherwise the turn is interrupted (2.1.281). A queued `!` ahead of messages interrupts. In shell mode the key only queues.
47. `Esc` interrupts without submitting the draft, and the queue is sent next.
48. `Up` on the first row returns queued text to the box, one per line ahead of the draft. Shell entries return only with an empty box and nothing else queued, switching to shell mode.
49. Pressing `←` moves queued messages with a backgrounded session. Commands, `!` lines and messages with an IDE selection block it, showing `Cannot open agents`.
50. An IDE selection attached to a queued message MUST be the one present at `Enter`.

### Prompt suggestions

51. A gray example from git history shows on a new session. After a response, a predicted next prompt may show. `Tab` or `Right` places it; typing dismisses it.
52. Suggestions are skipped with a cold cache, after an error, in plan mode, near a usage limit (unless forced by env), and in teammates. They show less often after 20 unused in a row (2.1.283), with a notice. Each costs a small background request.
53. Interactive sessions with no flag fetch default them off.

### Shell mode

54. `Escape`, `Backspace` or `Ctrl+U` on an empty prompt exit. Output enters context and Claude responds unless `respondToBashCommands` is false. Commands run outside the sandbox except in strict sandbox sessions.

## Configuration & interfaces

| Key | Effect |
|---|---|
| `editorMode` | `normal` or `vim` |
| `emojiCompletionEnabled` | Shortcodes |
| `spellcheck` | `{enabled, checker, language, color}` |
| `promptSuggestionEnabled`, `CLAUDE_CODE_ENABLE_PROMPT_SUGGESTION` | Suggestions; env wins |
| `externalEditorContext` | Global config only |
| `fileSuggestion` | Custom `@` command |
| `respondToBashCommands` | Auto-response to `!` output |
| `cleanupPeriodDays` | Paste cache expiry |

## Failure modes & edge cases

- The VS Code terminal can drop characters from very large pastes.
- gnome-terminal and JetBrains IDEs have no `Shift+Enter`; use `Ctrl+J` or `\`.
- Inside tmux, `Shift+Enter` needs extended keys.
- `Ctrl+Enter` arrives as `Enter` without extended key reporting, so it queues. `Ctrl+X Ctrl+S` always works.

## Changes since the snapshot

- New: emoji (2.1.217), spell check (2.1.235), invisible-character review (2.1.277), draft recovery (2.1.288, 2.1.292), `chat:sendNow` (2.1.275), `chat:queueSubmit` (2.1.247), bash path completion (2.1.193), mid-prompt lists (2.1.265).
- Changed: word keys match Bash (2.1.261); `Ctrl+A/E` logical lines (2.1.113); queued display (2.1.281).

## Open questions

- Current history retention and whether the snapshot `~/.claude/history.jsonl` path and 100-item window still apply.
- The `memoryBackgroundColor` token mentions `#` memory entries, but no current doc lists a `#` prefix. Whether that input survives is unknown.
- Docs and the 2.1.111 note disagree on `Ctrl+U`; the doc wording is used here.
