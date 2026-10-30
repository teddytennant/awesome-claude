# Agent View

**Status:** preview (research preview)
**Provenance:** post-leak (since v2.1.139, 2026-05-11)
**Sources:** docs `agent-view`, `keybindings`, `hooks`, `settings-reference`; `subhelp.txt`; changelog 2.1.139 to 2.1.299

## Purpose

`claude agents` opens one full-terminal screen listing background sessions with their state, and lets the user dispatch, peek, reply, attach and delete. Hosting and deletion rules are in [background-sessions.md](background-sessions.md). Note that `/agents` inside a session is a different thing.

## Behaviour

### Opening

1. In an untrusted directory, the workspace trust dialog MUST appear first. Declining exits without opening (2.1.225).
2. `defaultToAgentsView: true` makes a bare `claude` open the view. `claude "<prompt>"` still starts a regular session.
3. If agent view is unavailable, `claude agents` prints a count and the configured subagents, then exits.
4. By default the list MUST show all background sessions across projects. `--cwd <path>` limits it to sessions started under that path, including ones in worktrees under its `.claude/worktrees/`.
5. Open interactive sessions MUST NOT appear until backgrounded. Subagents and teammates MUST NOT appear as rows.
6. `Esc` exits to the shell, or to the originating conversation if the view was opened by `←`.

### The `←` gesture

7. On an empty prompt in a foreground session, `←` MUST background the session and open the view with that row selected, showing `Your conversation moved to the background`. In an attached session it detaches. `leftArrowOpensAgents` disables the foreground shortcut.
8. `←` after emptying the prompt or moving through history MUST ask for a second press (`Press ← again to open agents`), accepted at the first press at least a second later.
9. A `←` inside pasted or scripted input MUST NOT trigger the switch.
10. With a tool running, the switch waits for it, then Claude continues in the background. A second press backgrounds at once.
11. After about ten seconds it backgrounds regardless, except when: foreground subagents run (a second press restarts them from the beginning); a question or permission prompt awaits; the user types (cancels with a message); the turn is stopped (cancels); or a queued message cannot move (stays foreground with a notice).
12. When it does background, a foreground shell command MUST stop, with no dialog. The model has no record that it started. `Ctrl+B` during the wait keeps it.
13. `Enter` reopens, `Esc` undoes (or reports `Still starting — try again in a moment`), double `Ctrl+C` exits. If the conversation cannot reopen, Claude Code exits and prints a `claude --resume` command.
14. Text sent as the session moves is stopped or left unsent and MUST stay in prompt history (2.1.296).
15. `←` creates a row even for a session with no messages.
16. On Windows a press within about half a second of attaching MUST show `Ambiguous ←, press again to detach`.

### Footer hint

17. A regular session footer shows `← for agents` for ten seconds, then `← N agents` while sessions wait on the user (`99+` above 99), refreshing about every ten seconds while focused. `← N done` shows briefly when sessions finish and none wait.
18. Counts briefly change colour. `prefersReducedMotion` removes the colour change and `done` count. Screen reader mode hides all of it.

### States and groups

19. Row states: Working (animated), Needs input (yellow), Idle (dimmed), Completed (green), Failed (red), Stopped (grey).
20. Row shapes: `✻` or animated `✽` for a live process or a session needing input; `∙` for an exited process that restarts on reply or attach; `✢` for a sleeping `/loop`, with run count and countdown.
21. Default groups: Pinned, `Ready for review`, `Needs input`, `Working`, `Completed`. `Ready for review` means an open PR needing review or failing checks. `Completed` includes finished, failed and stopped. `Ctrl+S` toggles grouping by directory and persists.
22. Row age counts from creation and freezes at run duration when finished.
23. Name colour MUST follow `/color`.
24. Overflow in `Completed` folds to `… N more`. On a short terminal the header compacts to one line.
25. A tab title shows `N awaiting input · claude agents` or `claude agents`.

### Summaries

26. While working, row text updates at most every 15 seconds from the session's own output with no model request.
27. A Haiku-class request writes the summary at each turn end and every few minutes during a long turn, on the same provider and billing as the session. Without a Haiku-class model on a third-party provider, the main model is used.
28. When directory-grouped, the summary opens with a coloured state word.

### Pull request labels

29. Rows show `#N` or `!N` (GitLab) as a link, even without detected hyperlink support, unless `FORCE_HYPERLINK=0`.
30. Linking: a `gh` edit, comment, close or ready links the PR the output names; `gh pr checkout` or a push looks up the branch with `gh pr view`, retrying after up to five later `git`, `gh`, `glab` or `curl` commands in that directory. `gh pr merge` usually gives no link, since it prints only to a terminal.
31. Several linked PRs show `N PRs`, coloured by the open one most needing attention.
32. Colours: yellow waiting or failed, green passing with no blocking review, purple merged, grey draft or closed.

### Peek and reply

33. `Space` opens a peek panel with the exact question, the result, or the full status, followed by linked PRs, and `waiting 3m` or `safe mode · customizations are off` where applicable.
34. Typing and `Enter` sends a reply. `!` sends a Bash command.
35. To a working session, `/model`, `/effort`, `/rename` and `/usage` MUST run at once. Other replies queue. Other commands wait for the turn to end.
36. A reply of exactly `/stop` MUST stop the session at once. On a shell job, all input goes to the terminal, `/stop` included.
37. A question with choices lists them by number; a digit fills the input. `Tab` fills a suggested reply.
38. A reply MUST NOT answer a permission prompt or dialog; it waits in the queue, and the user attaches with `→`.
39. An invalid `PermissionRequest` or `PreToolUse` hook output MUST show the event and `hook output invalid:` with the validation error on the row.
40. An undeliverable reply's error MUST state whether it was saved.

### Attach and detach

41. `Enter` or `→` attaches, posting a recap of what happened while away.
42. Attached sessions MUST always render fullscreen, whatever the `tui` setting, and do not report status to the terminal.
43. Commands needing a human, `/install-github-app` and the `/mcp` list, work while attached. Unattached they park the session under `Needs input` with a row saying so. `/mcp reconnect`, `enable` and `disable` work regardless.
44. Detach with `←` on an empty prompt or `/exit`, returning to the view; `Ctrl+Z` returns to where the user started; double `Ctrl+C` on an empty prompt detaches. `Ctrl+C` otherwise interrupts.
45. Detaching MUST NOT stop a session. `/stop` does. `←` also detaches with `/btw` open, and the overlay reopens later (2.1.257).
46. A cold attach MUST show a formatted transcript tail with a `Session is starting` note until live.

### Dispatch input

47. Each submitted prompt starts a new session and never sends a follow-up. Names are short Haiku-class labels, and a later generated title also appears.
48. Prompts under four characters MUST be rejected with `Too short`.
49. Images may be pasted. Paste longer than 800 characters or three lines collapses to `[Pasted text #N]`; pasting the same text again expands it.
50. Prefix rules:

| Input | Effect |
| --- | --- |
| `<agent> <prompt>` | First word matching a custom agent runs it as main agent |
| `@<agent>` | Same, anywhere in the prompt; beats a same-named repository |
| `@<repo>` | Runs there: child repositories, in-tree registered worktrees, directories with sessions. Names with spaces are not listed |
| `/<command>` | Skills and commands sent as the first prompt |
| `! <command>` | Shell job |
| `#N` or PR/MR URL | Selects an existing session on it |

51. Handled locally: `/exit`, `/quit`, `/logout`, `/login`, `/model`, `/effort`, `/fast`, bare `/resume` or `/continue`. Unavailable built-ins show `isn't available in agent view` and keep the text.
52. `/model`, `/effort` and `/fast` apply to later dispatches in that window and are not saved. `default` undoes. No value opens a picker. `/effort ultracode` is not accepted here.
53. A `/model` choice or `claude agents --model` MUST override a dispatched agent's frontmatter `model`.
54. Bare `/resume` opens a picker of the repository's past sessions, newest first, including deleted ones, excluding existing rows. It fails with an id or term, `--cwd`, `--safe-mode`, or flags such as `--permission-mode` or `--settings`.
55. When directory-grouped, dispatch goes to the selected row's directory. Hover MUST NOT change the target (2.1.225).

### Filters

56. Filters in the dispatch input: `a:<name>`, `s:<state>` (also group names, and `s:blocked`), `n:<text>`, `o:<text>`, a PR or MR number or URL, any other URL (first prompt match). Combine with spaces. Collapsed groups expand while filtering, and a match is selected.

### Notifications

57. While the view is open, sessions needing input, finishing or failing MUST notify through `preferredNotifChannel` and fire `Notification` with `agent_needs_input` or `agent_completed`. Scheduled sessions notify only when needing input.

## Configuration & interfaces

### Keys

| Key | Action |
| --- | --- |
| `↑` `↓`, `PgUp` `PgDn`, `Home` `End` | Move |
| `Enter`, `→` | Attach; `Enter` submits non-filter input |
| `Space` | Peek |
| `Shift+Enter`, `Ctrl+J` | Newline |
| `Ctrl+Enter` | Dispatch and attach, where supported |
| `Alt+1..9` | Attach by index in the focused directory |
| `Tab` | Browse subagents on empty input |
| `Ctrl+S`, `Ctrl+T`, `Ctrl+R` | Group, pin, rename |
| `Ctrl+F`, `Alt+↑/↓` | Find by name, jump groups |
| `Ctrl+G` | External editor |
| `Ctrl+X` | Stop, then delete within two seconds; on a group header deletes all after confirmation |
| `Shift+↑/↓` | Reorder |
| `Esc`, `Ctrl+C` | Close, clear, exit |
| `?` | Help |

Keys with `Agents` context actions follow `keybindings.json`, such as `agents:switchView` and `agents:togglePin`. `Ctrl+G` follows `chat:externalEditor`.

### `claude agents` flags

`--add-dir`, `--agent`, `--all`, `--allow-dangerously-skip-permissions`, `--cwd`, `--dangerously-skip-permissions`, `--effort`, `--json`, `--mcp-config`, `--model`, `--permission-mode`, `--plugin-dir`, `--restricted`, `--safe-mode`, `--setting-sources`, `--settings`, `--strict-mcp-config`.

`--settings`, `--setting-sources` and `--plugin-dir` apply to the view and dispatches, and may go before or after `agents`. `--add-dir` and `--mcp-config` MUST go after it and are repeated per value. Active defaults appear in the footer. An auto-update relaunch keeps them (2.1.274). `--agent` defaults to the `agent` setting, then `claude`. `--restricted` needs 2.1.248.

## Failure modes & edge cases

- A prompt whose first word matches an agent name dispatches that agent.
- `/fast` on a model without fast mode starts sessions with it off; the hint, not the header, confirms.
- `Ctrl+X` delete proceeds even if the stop fails, ending the process itself.
- The `Completed` group mixes outcomes, so state requires the icon.

## Changes since the snapshot

- 2.1.139: introduced. 2.1.141: `--cwd`. 2.1.145: `--json`, voice in peek.
- 2.1.196: single `←`. 2.1.198: notifications. 2.1.205: `← N agents`, PR linking.
- 2.1.233: GitLab labels. 2.1.248: `Ctrl+Enter`, 48-hour stopped state.
- 2.1.287: `n:` filter, queued replies, `/stop`. 2.1.288: find and group jump.
- 2.1.290: `/model`, `/effort`, `/rename` run at once. 2.1.299: `/effort`, `/fast`, safe mode line.

## Open questions

- The complete `Agents` keybinding context; see the keybindings spec if one exists.
- Exact conditions for `Ctrl+Enter` terminal support.
- Whether `Idle` is distinct in any group, since groups omit it.
