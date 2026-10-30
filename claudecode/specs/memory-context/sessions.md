# Sessions: transcripts, resume, continue, branch, fork, rename, recap

**Status:** shipped
**Provenance:** both (running-session resume, `/fork` copy, recap post-leak)
**Sources:** docs `sessions`, `claude-directory`, `interactive-mode`, `commands`, `cli-reference`, `checkpointing`, `agent-view`; snapshot `utils/sessionStorage.ts`, `types/logs.ts`, `commands/resume/`, `commands/rename/`, `commands/branch/`, `services/awaySummary.ts`; changelog versions cited below

## Purpose

Persist each conversation locally as it happens, so it can be reopened, branched, named and searched.

## Behaviour

### Transcripts

1. Transcripts MUST be written continuously as JSONL at `~/.claude/projects/<project>/<session-id>.jsonl`, where `<project>` is the working directory path with non-alphanumerics replaced by `-`. Names over 200 characters MUST be truncated and suffixed with a hash of the full path.
2. Each line is a message, tool use or result, a record of a request sent to the model, or a metadata entry. The format is internal and MAY change in any release; scripts SHOULD use `/export`, `-p` JSON, the `transcript_path` hook field, or the Agent SDK.
3. Snapshot metadata entries include title, AI title, last prompt, tag, agent name/colour/setting, PR link, mode, worktree state, content replacement and file-history snapshots. Since v2.1.300 local transcripts also record each request's system prompt, tools and parameters.
4. Subagent transcripts live in `<session>/subagents/`; large tool outputs in `<session>/tool-results/`.
5. A displaced transcript MUST be set aside as `.orphaned-…jsonl` or `.jsonl.superseded-…`, not overwritten, and hidden from the picker.
6. Failing writes MUST produce a warning, as must session saving being disabled by an inherited variable.
7. `CLAUDE_CODE_SKIP_PROMPT_HISTORY` suppresses writes in all modes, and `--no-session-persistence` for one `-p` run. `CLAUDE_CODE_TRANSCRIPT_LOCAL_GC=1` trims `-p`/SDK transcripts after compaction once over 5 MB, unless that frees under 10%.
8. `CLAUDE_CODE_FORCE_SESSION_PERSISTENCE` restores persistence for a top-level session misclassified as a child.

### Entry points

9. `claude --continue` MUST open the most recent eligible session in the current directory. `--resume` alone opens the picker. `--resume <id|name|absolute-transcript-path>` targets directly. `--from-pr` opens the picker filtered by pull request (number or GitHub, GitHub Enterprise, GitLab or Bitbucket URL). `/resume [session]` (alias `/continue`) switches inside a session. `--session-id <uuid>` sets the ID of a new session.
10. Sessions from `claude -p`, the Agent SDK, or whose first prompt was `/loop` MUST be excluded from the picker and `--continue`, but `claude -p --continue` includes them. Any can be resumed by ID.
11. `--continue` opens a finished background session but not a running one; if the most recent is running in the background, it MUST exit naming that session's ID.

### Resolution

12. ID lookup order: current project and its worktrees, then every other project. Cross-project resolution MUST succeed only when exactly one other project holds a transcript with messages for it; otherwise report `No conversation found with session ID: <id>`.
13. Name lookup covers the current repository and worktrees. An exact match resumes directly. An ambiguous name opens the picker pre-filled for `--resume`, and is an error for `/resume`.
14. Generated titles resolve like names. Default display names (`my-app-3f`) do not.

### Picker

15. The default list is the current worktree, including background sessions marked `bg`, plus sessions that added the directory with `/add-dir`. `Ctrl+W` widens to all worktrees, `Ctrl+A` to all projects, `Ctrl+B` filters to the current branch.
16. Keys: arrows or `j`/`k` navigate, `→`/`←` expand or collapse groups, `Enter` or `1`–`9` resume, `Space` previews, `Ctrl+R` renames. Other printable characters enter search. A pasted PR or MR URL finds the session that created it.
17. Rows show name or title or summary or first prompt, age, branch and size. The list MUST load more as you scroll.
18. A selected session in another worktree resumes in place, or in the current directory if that worktree is gone. A session from an unrelated project copies a `cd` and resume command, unless the directory is gone, in which case it resumes here.
19. `/cd` moves a session's storage to the new project.

### Restoration

20. Resume MUST restore history; if compacted, opening at a `Conversation compacted` row with the last summary, kept messages and everything since. Summarised messages are not reloaded.
21. Interrupted tool calls MUST NOT re-run. Model, agent (searched in the original directory if trusted, then the resuming directory), active goal (counters reset), and unexpired scheduled tasks are restored. Background Bash and monitors are not; ended background work appears as a note and does not start a turn.
22. Flags are not restored: `--mcp-config`, `--settings`, `--plugin-dir`, `--fallback-model`, `--add-dir`, and `/add-dir` directories. Settings files are re-read.
23. Permission mode depends on route:

| Session ended in | Route | Result |
|---|---|---|
| `bypassPermissions` | Terminal | New-session mode; must be re-enabled at launch or by user, `--settings` or managed `defaultMode` |
| `plan` | Terminal | Plan; with `--fork-session`, or a deny rule removing `ExitPlanMode`, new-session mode |
| `auto` | Terminal | `auto` if the account still qualifies |
| Manual | Terminal | Manual when new sessions would be auto by built-in default; a settings `defaultMode` wins |
| `plan` | `-p`, all conditions below | Plan |
| Any | `-p`, otherwise | Mode of a new `-p` run |
| `plan` | VS Code | Plan, with listed exceptions |

24. `-p` restores plan only with `--permission-prompt-tool`, without `--permission-prompts none`, `--permission-mode`, `--dangerously-skip-permissions` or `--fork-session`, not through channels, and with no deny on `ExitPlanMode`.
25. The picker at launch starts in new-session mode except that plan is restored, unless `--permission-mode`, `--dangerously-skip-permissions` or `--fork-session` is passed. `/resume` keeps the current mode except that plan is restored; a conversation already open earlier in this process keeps the current mode.

### Running background sessions

26. `claude --resume <session>` on a running background session MUST attach instead of loading the transcript; a command-line prompt is sent as its next turn, printing a message first. This also applies to `-p` at a terminal.
27. It MUST NOT attach, MUST send nothing, and MUST exit 1 with instructions when input or output is piped, or when flags configure the session, read output, or limit the run, or agent view is off. `--fork-session` resumes a copy.
28. Prompts beginning `/` or `!`, or any prompt while the session waits on a question, are not sent.
29. `/resume` on a running session backgrounds the current conversation and attaches, or prints the `claude attach` command if it cannot.
30. `claude --resume <id> --bg` continues under the same ID when nothing runs it; a copy is announced.

### Stale resume dialog

31. On Pro and Max, resuming a long conversation after a long break or on a different model MAY show "Resume this conversation?", estimating the share of the 5-hour limit the saved conversation alone would use. Options are **Resume** and **Start a new conversation**. The estimated use happens on the first message.

### Branch and fork

32. `/branch [name]` MUST copy the transcript to this point and switch this process into the copy, leaving the original unchanged. Default name comes from the first prompt. It prints both IDs. Grants, background work and Remote Control carry into the branch.
33. `--fork-session` with `--continue` or `--resume` creates a new ID in a new process; "allow for this session" grants do not carry.
34. `/fork [prompt]` copies the conversation into a new background session and keeps working here. Unless it edits in place, the copy is told to create its own worktree. The copy is named from the prompt if the session has no title. `/subtask` is the in-session subagent replacement.
35. Branches appear as separate rows, grouped when entries match.
36. The same session resumed in two terminals without forking interleaves into one transcript.

### Names

37. Names are set by `-n`, `/rename`, `Ctrl+R` in the picker, plan accept (generated), claude.ai or the app, or desktop.
38. Names MUST be sanitised on every surface: control and invisible characters become spaces, 200 character cap, and an effectively empty name is rejected with a usage message. `/rename` without an argument generates from history.
39. Unnamed interactive sessions get a default display name, and a generated title from a background small-model request on the first prompt, in the configured `language`. Direct `claude -p` runs get none. Accepting a plan replaces the generated title.
40. Live interactive sessions on a machine MUST have unique names; a collision yields a `name-word-word` variant, with notice.
41. The exit-time resume command MUST name the session by ID, so nothing in a name can run when pasted.

### Clear and export

42. `/clear [name]` (aliases `/reset`, `/new`) starts a new session and saves the old one. With no argument the new session keeps a user-set name, not a generated title. With a name, that labels the old session, and the new one starts unnamed.
43. `/export [filename]` writes plain text, or opens a clipboard/file menu.

### Recap

44. After the user has been away, the client MUST show a one-line recap. It generates in the background once at least 3 minutes have passed since the last completed turn with the terminal unfocused, needs at least 3 turns, and never fires twice in a row. Output is capped at 400 characters at a word boundary.
45. `/recap` generates on demand and appends output without replacing history, keeping the cache. Relayed from a chat thread, or from a routine or webhook, it MUST decline with a notice.
46. Automatic recaps never appear in non-interactive mode. `awaySummaryEnabled` or `/config` **Session recap** turns them off; `CLAUDE_CODE_ENABLE_AWAY_SUMMARY` overrides in either direction.

### Retention and deletion

47. See [claude-directory.md](claude-directory.md) for the sweep. `claude purge` deletes project state. `claude rm` leaves the transcript resumable.

## Configuration & interfaces

| Interface | Effect |
|---|---|
| `--continue/-c`, `--resume/-r`, `--from-pr`, `--fork-session`, `--session-id`, `--name/-n`, `--no-session-persistence` | Session selection |
| `cleanupPeriodDays`, `desktopSessionCleanupPeriodDays` | Retention |
| `awaySummaryEnabled`, `terminalTitleFromRename` | Recap; tab title |
| `CLAUDE_CONFIG_DIR`, `CLAUDE_CODE_PROJECT_DIR_NAME` | Storage location |
| `CLAUDE_CODE_RESUME_INTERRUPTED_TURN`, `CLAUDE_CODE_RESUME_INTERRUPTED_TURN_MAX_AGE_MS`, `CLAUDE_CODE_RESUME_PROMPT`, `CLAUDE_CODE_RESUME_SHOWS_CUT_OFF_CALLS` | Automatic continuation |
| `CLAUDE_CODE_SESSION_ID` | Exposed to subprocesses; updates on `/clear` |
| `SessionStart` sources | `startup`, `resume`, `clear`, `compact`, `fork` |
| `CLAUDE_CODE_DISABLE_TERMINAL_TITLE` | Also skips title generation |

## Failure modes & edge cases

- An unloadable picker selection at launch prints `Failed to resume the conversation` with a retry command and exits 1; inside a session it reports the failure and keeps running.
- Damaged transcripts: malformed entries MUST NOT crash resume, and `tool_use_id` corruption self-heals where possible.
- A batch of parallel tool calls at a crash MUST NOT lose subsequent turns.
- Paths differing only by `_`, `-` or `.` MUST NOT cross-resolve.
- `CLAUDE_CODE_PROJECT_DIR_NAME` needs `CLAUDE_CONFIG_DIR`, 1–64 safe characters, and the launch environment; otherwise it is ignored.

## Changes since the snapshot

- v2.1.101: `-p --resume` accepts titles.
- v2.1.108: recap; picker defaults to the current directory.
- v2.1.110: resume restores scheduled tasks.
- v2.1.117: `/resume` offers to summarise stale sessions.
- v2.1.118: `/add-dir` sessions found.
- v2.1.122: PR URL search.
- v2.1.196: default names.
- v2.1.212: `/fork` becomes a background copy; `/subtask` replaces the old behaviour.
- v2.1.217: transcript-write warnings.
- v2.1.221: name sanitisation; `/fork` worktrees.
- v2.1.232: unique names.
- v2.1.234: `CLAUDE_CODE_PROJECT_DIR_NAME`; shorter titles.
- v2.1.236: recap 400-character cap.
- v2.1.239: goals restored from the picker.
- v2.1.243: picker pagination.
- v2.1.246: `/cd` applies project settings at once.
- v2.1.257: `--continue` opens finished background sessions; `--bg` keeps the ID.
- v2.1.285: resume opens running background sessions.
- v2.1.290, v2.1.292: plan mode restoration fixes.
- v2.1.299: exit command uses the ID.
- v2.1.300: transcripts record request parameters.
- v2.1.304: "Resume this conversation?" dialog.
- v2.1.311: agent teams task list restored.
- v2.1.314: damaged-transcript performance.

## Open questions

- Thresholds for the stale-resume dialog.
- Whether the snapshot's metadata entry set is still complete.
- Which model produces recaps now; the snapshot used the small/fast model over the last 30 messages.
