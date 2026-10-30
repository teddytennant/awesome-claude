# VS Code Extension
**Status:** shipped
**Provenance:** both (IDE bridge in the snapshot; graphical panel feature set largely post-leak)
**Sources:** docs `vs-code.md`, `settings-reference.md`, `env-vars.md`; snapshot `utils/ide.ts`, `utils/idePathConversion.ts`, `hooks/useIde*.ts`; changelog 2.1.94 to 2.1.314

## Purpose
A graphical chat panel for Claude Code inside VS Code (and VS Code forks such as Cursor and Windsurf), plus a local bridge that lets a `claude` CLI running in a terminal use the editor for diffs, selections and diagnostics. The extension source is not in the snapshot; the panel is specified from public behaviour.

## Behaviour

### Installation and process model
1. The extension MUST require VS Code 1.94.0 or later and work with a paid Claude subscription, a Console account, or a third-party provider.
2. The extension MUST bundle a private CLI copy for its panel and MUST NOT add `claude` to the shell `PATH`. Terminal use needs the standalone install.
3. `claudeProcessWrapper` MUST be able to replace the launch executable, receiving the bundled binary path as an argument when one exists. This also covers platforms for which no binary is bundled.
4. The process MUST activate the workspace Python environment when `usePythonEnvironment` is on. Since 2.1.299 startup MUST NOT wait for the Python extension in workspaces with no Python environment.
5. With VS Code's own telemetry setting off, the extension MUST start sessions with `DISABLE_TELEMETRY` set, so they send no usage metrics or error reports and fetch no feature flags (2.1.311).
6. `CLAUDE_CONFIG_DIR` in `environmentVariables` MUST apply only when absolute. `~` is not expanded and relative values are ignored. It also passes to terminals that continue the chat.
7. The extension's own HTTP requests and voice dictation MUST filter trusted certificates the way the CLI does, and MUST trust the `NODE_EXTRA_CA_CERTS` file named in the environment or user settings (2.1.307). Certificate verification failures MUST produce an actionable log warning (2.1.309).

### Prompt box
8. A mode indicator MUST offer Auto, Manual, Plan, Edit automatically, and Bypass permissions only when `allowDangerouslySkipPermissions` is on. Since 2.1.283 Auto is the built-in starting mode on all plans; earlier it was Pro, Max and Team only.
9. `initialPermissionMode` MUST be read from user settings only; workspace values are ignored (since 2.1.225). `manual` is an alias of `default`.
10. Plan mode MUST open the plan as a full Markdown document supporting inline comments. `/plan` switches mode, `/plan <task>` also starts planning, `/plan open` opens the file (2.1.280).
11. The footer model pill MUST show the current model and open a flat picker (2.1.257, 2.1.261). An Effort row MUST appear for models with effort levels; a non-`max` pick is saved under `modelSettings` in user settings, `max` applies to the session only.
12. An Ultracode switch MUST appear under Effort when dynamic workflows are enabled and the model supports it. While on, the pill shows `· Ultracode` (2.1.284).
13. The model picker SHOULD show model names rather than raw Bedrock, Vertex or gateway IDs when the ID is recognised (2.1.261).
14. Pasted text over 800 characters or over 2 line breaks MUST be marked as pasted. Invisible Unicode format and tag characters MUST be removed, with a notice for pastes (2.1.280).
15. Images MUST be sendable with no accompanying text (2.1.275).
16. A message sent while Claude is working MUST wait at the bottom of the conversation until Claude starts on it (2.1.275), and a screen reader MUST hear "Message queued." (2.1.290).
17. Prompt cache clock: a countdown MUST show estimated minutes until cache expiry and turn red without minutes on expiry and just after compaction. Only compaction, of the cache-invalidating actions, resets it.
18. Idle compaction: a 200K+ token conversation left idle MUST be summarised, and the summary used on the next message if the prompt cache has expired (2.1.314).

### Command menu
19. Typing or clicking `/` MUST open a menu with Context, Model, Customize and Settings sections. Commands MUST be a subset of the CLI's; CLI-only items SHOULD open in the integrated terminal.
20. Native dialogs MUST exist for the following, with typed equivalents where shown:

| Surface | Typed | Since |
|---|---|---|
| Account & usage | `/usage` | 2.1.120 |
| Context usage | `/context` | 2.1.121 |
| Hooks (edit user, project, local; others read-only) | | 2.1.269 |
| Permissions (Allow, Ask, Deny; other sources read-only) | | 2.1.269 |
| Memory (toggles, browse, edit, delete) | | 2.1.274, 2.1.275 |
| Instructions (edit CLAUDE.md, creating if absent) | | 2.1.274 |
| Output styles, "Build a custom style" | | 2.1.257, 2.1.261 |
| Slash command browser; skill visibility | `/skills` | 2.1.257, 2.1.280 |
| Status | `/status` | 2.1.280 |
| Sandbox | `/sandbox` | 2.1.280 |
| Claude in Chrome (needs claude.ai sign-in) | `/chrome` | 2.1.280 |
| Export conversation | `/export [file]` | 2.1.280 |
| Bookmarks | `/bookmarks` | 2.1.286 |
| Tasks / agent map | `/tasks` | 2.1.277 |

21. A failed hook save caused by the settings file itself MUST open a popup with an "Open settings file" button and the reason behind "Copy error" (2.1.271).
22. `/bug` and `/feedback` MUST open a feedback dialog. On a first-party sign-in the report is sent to Anthropic. On third-party providers or without Anthropic credentials nothing is sent, the dialog says so, and submission saves a redacted archive under `~/.claude/feedback-bundles/` with a Show folder button (2.1.284). Policy, `DISABLE_FEEDBACK_COMMAND` or `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` MUST turn this off and show a notice.
23. `/btw` MUST open a resizable side panel. The thread survives reloads, keeps the newest 20 exchanges, and expires on the `cleanupPeriodDays` schedule when retention can be safely determined.

### Editor context
24. The open file and selection MUST attach automatically unless `attachOpenFile` or `attachSelection` is off. With `attachOpenFile` off, the path is sent only with a selection. With `attachSelection` off, a selection can still be added as an @-mention.
25. A queued message MUST keep the selection captured when Enter was pressed.
26. A `Read` deny rule for a path MUST suppress both selected text and the open-file notice for that path.
27. `Option+K` / `Alt+K` MUST insert an @-mention with path and lines, for example `@app.ts#5-10`.
28. Custom skills and slash commands sent from the panel MUST include the same open-file and selection context as ordinary messages.

### Conversation view
29. Focus view (`focusView`, `Ctrl+Option+F` / `Ctrl+Alt+F`) MUST hide tools, results and thinking behind per-turn rows, while keeping the latest to-do list, pending question text, live subagent rows and sent-file rows visible. It applies to all open sessions and persists.
30. The agent map MUST draw subagents as a tree with status, elapsed time and tokens, list background shells and monitors below them, show their output (2.1.287), and allow stopping each. The pill MUST count running agents and turn red on failure (2.1.275). Stop or Esc ends the turn but background agents continue (2.1.286).
31. Each proposed change in a diff tab MUST have accept and reject buttons (2.1.275).
32. `AskUserQuestion` cards SHOULD show option previews, and answers MUST be recorded as a Questions row (2.1.286).
33. Claude responses MUST render LaTeX (`$$`, `\[ \]`, `$ $`, `\( \)`) (2.1.301) and syntax-coloured code blocks (2.1.311).
34. Rows under a message MUST reveal attached terminal output, browser tab, browser instructions and selected code (2.1.286).
35. Files sent with `SendUserFile` during Remote Control MUST appear as a clickable row. A path naming a network host MUST NOT be linked, because opening it could send Windows credentials to that host.
36. `showMessageTimestamps` defaults on since 2.1.290 (off in 2.1.284).
37. Long sessions SHOULD trim older tool-activity rows first (2.1.243).

### Session management
38. A sessions list in the Activity Bar MUST be always visible and separate from the panel. It carries ACCOUNT & USAGE and SESSION MANAGER headers, with session cost and tokens where plan limits don't apply (2.1.277).
39. Sessions MUST be groupable into named, collapsible groups saved per workspace folder. One session belongs to at most one group. Deleting a group only ungroups its members.
40. Filters: Active, and status (Needs input, Working, Completed, Open, Closed). A session is open if it has a tab here or runs in another process on this machine. Archived sessions are hidden while a filter is on. Filters persist.
41. A hollow ring MUST mark sessions open in a terminal, another window or Claude Desktop (2.1.261).
42. Delete was replaced by Archive (2.1.257). `archiveInactiveSessions` auto-archives (1, 2, 7, 14; 0 off; default 14), with a one-time notice and an "Unarchive all" action (2.1.277).
43. On reload, editor tabs MUST return. Sidebar conversations return only if active in the last 10 minutes. `continueAfterReload` MUST continue an interrupted step, labelled in chat, including after an extension restart (2.1.274, 2.1.290). A note MUST appear when no reply will follow (2.1.285).
44. "Still open somewhere else" MUST cover a leftover process from an extension restart, which usually ends within about 10 minutes (2.1.307).
45. A resumed conversation in a Claude-created worktree under `.claude/worktrees/` MUST reopen there, with a banner and an **Open worktree** action.
46. Session history MUST have Local and Web tabs. Web requires claude.ai sign-in, loads when first opened (2.1.311), and filters to the current GitHub repo. Resuming downloads a copy and does not sync back. Remote Control sessions from the same folder MUST open locally unless another process may hold them. A partial download MUST save nothing.

### Terminal bridge
47. While active, the extension MUST run a local MCP server named `ide`, hidden from `/mcp`, bound to `127.0.0.1` on a random port in 10000-65535 over unencrypted `ws://`.
48. Each activation MUST generate a fresh token, written to `~/.claude/ide/<port>.lock` (or `$CLAUDE_CONFIG_DIR/ide/`) with mode `0600` in a `0700` directory. The CLI presents it as `X-Claude-Code-Ide-Authorization`.
49. Snapshot lockfile shape, not re-verified for current releases: `workspaceFolders`, `pid`, `ideName`, `transport` (`ws` or `sse`), `runningInWindows`, `authToken`.
50. About a dozen tools MUST exist, with only `mcp__ide__getDiagnostics` and `mcp__ide__executeCode` model-visible; the others are internal RPC for diffs, selections and saves.
51. `executeCode` MUST insert a cell at the end of the active notebook, scroll to it, and ask via a Quick Pick. Cancel or Esc returns an error and nothing runs.
52. In the panel, diagnostics MUST come from a separate built-in server, `claude-vscode`, as `mcp__claude-vscode__getDiagnostics` (2.1.285). A `Read` deny covers neither tool; deny both by name.
53. The panel's post-edit wait for new problems is about 0.75 seconds in most cases (2.1.309).
54. The transcript MUST show a `⧉ Selected N lines from <file>` line. The CLI prompt shows a `[⧉ …]` pill, deletable with Backspace (2.1.271).

### Third-party providers and plugins
55. On third-party providers, claude.ai-only features (plan bars, dictation, Web tab, sign-out) MUST be absent. A leftover claude.ai sign-in MUST NOT be sent with any request.
56. Plugins containing mods MAY draw panes, toasts, status lines and custom message or tool rendering (2.1.299; 2.1.304 for sessions that fetch no feature flags). A label MUST name the plugin for each contribution.
57. Install links `vscode://anthropic.claude-code/install-plugin` open the plugin dialog on one plugin.

## Configuration & interfaces

### Extension settings (`claudeCode.*`)
| Key | Default | Note |
|---|---|---|
| `useTerminal` | false | Terminal mode |
| `initialPermissionMode` | unset | User scope only |
| `preferredLocation` | `panel` | `sidebar` or `panel` |
| `lockEditorGroups` | true | 2.1.274 |
| `autosave` | true | Before Claude reads or writes |
| `attachOpenFile`, `attachSelection` | true | 2.1.271, 2.1.300 |
| `useCtrlEnterToSend` | false | |
| `scrollToBottomOnSend` | true | 2.1.275 |
| `showMessageTimestamps` | true | |
| `spinnerVerbs` | append, empty | Same shape as CLI |
| `enableNewConversationShortcut` | false | Cmd/Ctrl+N |
| `enableReopenClosedSessionShortcut` | true | Cmd/Ctrl+Shift+T; falls through to VS Code if the last tab was not Claude's |
| `archiveInactiveSessions` | 14 | |
| `continueAfterReload` | true | |
| `hideOnboarding`, `focusView` | false | |
| `respectGitIgnore`, `usePythonEnvironment` | true | |
| `environmentVariables` | `[]` | |
| `disableLoginPrompt` | false | Third-party setups |
| `allowDangerouslySkipPermissions` | false | |
| `claudeProcessWrapper` | unset | |

### URI handler
`vscode://anthropic.claude-code/open` with optional URL-encoded `prompt` (prefilled, never auto-submitted) and `session` (resume; matches main checkout or worktrees since 2.1.300; unknown ID starts fresh; an open tab is focused).

### CLI side settings and variables
| Name | Effect |
|---|---|
| `diffTool` | `auto` or `terminal`; shown in `/config` only while connected |
| `autoConnectIde`, `CLAUDE_CODE_AUTO_CONNECT_IDE` | Connect from external terminal; the variable wins |
| `autoInstallIdeExtension`, `CLAUDE_CODE_IDE_SKIP_AUTO_INSTALL` | Extension auto-install from a VS Code terminal |
| `CLAUDE_CODE_IDE_HOST_OVERRIDE` | Host used to reach the extension, including WSL routing |
| `CLAUDE_CODE_IDE_SKIP_VALID_CHECK` | Skip lockfile validation |
| `CLAUDE_CODE_DISABLE_CFC_PROMPT` | Stop adding Claude in Chrome instructions; tools remain (2.1.314) |

Commands include Focus Input, Focus last message, Open in Side Bar, Open in Terminal, Open in New Tab, Open in New Window, New Conversation, Reopen Closed Session, Insert @-Mention Reference, Accept and Reject Change at Cursor, Toggle Focus view, Rename Session Tab, Add Session Tab to Group, Mark Session as Unread, Show Logs, Logout.

## Failure modes & edge cases
- On macOS Tahoe and later, the Game Overlay shortcut takes `Cmd+Esc` before VS Code sees it; clear it or rebind `Claude Code: Focus input`.
- Dictation or the Web tab can fail behind a TLS-inspecting proxy unless the proxy CA is trusted.
- `Ctrl+Alt+F` on Windows and Linux opens Find while focus is in the Debug Console or a searchable list.
- A window reload can open with blank messages at first until the transcript loads.
- A session ID in the URI handler from another folder starts a fresh conversation.
- `!` Bash shortcut and tab completion are CLI-only.
- The Fix button in the usage dialog is hidden during Remote Control.

## Changes since the snapshot
- 2.1.120, 2.1.121: native `/usage` and `/context`.
- 2.1.139: reopen-closed-session shortcut.
- 2.1.203 to 2.1.251: Remote Control toggle, banner, then footer pill.
- 2.1.221: Focus view. 2.1.229: session groups, built-in feedback dialog.
- 2.1.257 to 2.1.261: section headers, model pill, Archive replaces Delete, filters, flat model list.
- 2.1.265: auto-archive. 2.1.271: attach open file setting. 2.1.274: continue after reload, Memory and Instructions.
- 2.1.275: per-change accept and reject. 2.1.277 and 2.1.280: Copy, Status, Export, `/plan`.
- 2.1.284: Ultracode switch. 2.1.285: on-demand diagnostics via `claude-vscode`.
- 2.1.286: bookmarks, question previews. 2.1.295: sent-file rows.
- 2.1.296: Chrome actions always ask, including with `@browser`.
- 2.1.300: `attachSelection`. 2.1.301: LaTeX. 2.1.304: mod drawing in flagless sessions. 2.1.311: telemetry follows VS Code setting.
- 2.1.314: idle compaction; `CLAUDE_CODE_DISABLE_CFC_PROMPT` scope widened.

## Open questions
- Exact number and names of internal `ide` MCP RPC tools in the current build.
- Whether the lockfile schema has changed since the snapshot.
- Which forks are officially supported at 2.1.314; docs name only VS Code in this page, though the snapshot and changelog cover Cursor and Windsurf.
