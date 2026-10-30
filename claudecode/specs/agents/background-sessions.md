# Background Sessions and Supervisor

**Status:** preview (research preview)
**Provenance:** post-leak (since v2.1.139, 2026-05-11); a gated `ps`/`logs`/`attach`/`kill`/`--bg` and `daemon` skeleton existed in the snapshot
**Sources:** docs `agent-view`, `env-vars`, `settings-reference`, `errors`, `permission-modes`; `help.txt`, `subhelp.txt`; snapshot `entrypoints/cli.tsx`; changelog 2.1.139 to 2.1.311

## Purpose

A background session is a full Claude Code conversation that runs without a terminal, hosted by a local supervisor. It can be dispatched, detached, attached, stopped, restarted and deleted from the shell or from [agent view](agent-view.md). This spec covers hosting, dispatch, lifecycle, isolation and deletion.

## Behaviour

### Hosting

1. A supervisor MUST start on demand the first time a session is backgrounded or agent view opens. Each session is its own process under it, and its terminal runs in a separate host process.
2. Process rules by state:
   - Working (including a running subagent, workflow, monitor or pending `/loop` wakeup), paused on a dialog, or attached: keep running.
   - Finished or awaiting the next message, unattached for about an hour: stop the process and keep the conversation. Pinned sessions MUST stay alive. Sessions waiting on a scheduled wakeup MUST NOT be restarted or shut down by updates or low memory (2.1.290).
   - Unexpected exit with the supervisor alive: restart, except a session backgrounded with `←` or `/background` that was killed externally, which MUST be marked stopped.
   - After an auto-update: the supervisor restarts into the new version and moves idle sessions over in the background. Working, waiting or attached sessions MUST NOT be interrupted. Pinned sessions restart in place.
   - Memory pressure: idle sessions are shed first; pinned ones only if that freed nothing.
3. If the supervisor stops on macOS or Linux, sessions MUST stop unless a new supervisor connects within about a minute. `claude agents` exiting with no supervisor MUST NOT start one (2.1.295), and it may print a notice.
4. Empty idle sessions left by `←` MUST retire after five minutes (2.1.141). A session whose scheduled task is gone moves to Completed about 20 seconds later (2.1.290).
5. Sessions MUST survive machine sleep; the supervisor reconnects rather than treating the gap as idle. Shutdown stops them.
6. A session unresponsive after sleep MUST be restarted when opened, continuing the interrupted response.
7. A running session's background shells and background subagents MUST carry to its next process. Workflows continue only when relaunched. Monitors and shell commands started by a subagent stop. `CLAUDE_CODE_DISABLE_BG_EXIT_HANDOFF=1` stops all of it with the process.
8. Workers killed by a daemon restart MUST auto-resume the next time the agents view opens (2.1.196).
9. A saved reply is sent as the next prompt on restart. Replies prefixed with `!` or `/` are never saved.
10. Teardown MUST send SIGTERM to shell subprocesses before SIGKILL (2.1.160).
11. A session MUST be told it was restarted after a crash, and a restarted `←` or `/background` session MUST NOT resume an interrupted response older than about an hour.
12. Exit messages MUST NOT promise a restart that will not come, and SHOULD say how to resume (2.1.311).

### Dispatch

13. `claude --bg "<prompt>"` starts a session in the background and prints its short ID, optional name, and commands for attach, logs and stop. It may first print `Starting background service…`.
14. `--bg` with `-p` or `--print` MUST be rejected before any session is created.
15. The prompt is positional. `--bg` MUST be read as a flag only where a flag can stand: before a bare `--` and not as another flag's value. Ambiguous positions MUST start nothing and exit with `Couldn't tell whether --bg is a flag or text here` (2.1.299).
16. Untrusted directories MUST show the trust dialog in a terminal. Where no dialog can appear, the command MUST exit with `Workspace not trusted`.
17. `--agent <name>` runs that agent as the main agent. An unknown name still prints as backgrounded, with a `no agent named` warning, and the session exits with `--agent '<name>' not found`.
18. `--resume <full-id> --bg` MUST continue in place under the same ID, or start a copy under a new ID with a `note:` line (2.1.257). `--continue`, a bare `--resume`, or a name or path always copy. `--fork-session` copies without the note.
19. `--name` sets the display name.
20. `--exec '<cmd>'` runs a PTY-backed job with no model. Output stays in memory, not on disk, and the row cleans up about five minutes after exit. A shell row MUST never be restarted automatically.
21. `/background` or `/bg [prompt]` moves the current session. A running response continues there (2.1.153). With no messages, `/bg` asks for one, while `←` works anyway.
22. Exiting with background work running MUST show a `Background work is running` dialog with `Move to background and exit`, unless agent view is off.
23. A name collision MUST number the new row, such as `my-session (2)`, and leave the existing row alone.
24. Sessions forked with `/fork` are specified in [forks.md](forks.md).

### What carries over when backgrounding

25. Carries: background shells, backgrounded subagents (only if everything they started can move), `/loop` tasks, automatic artifact-comment replies.
26. Relaunch only: dynamic workflows. Running workflow agents start over and re-spend tokens.
27. Stops: monitors and other immovable work. When any exists, a `Background this session?` dialog MUST confirm first, naming what stops and counting what carries.
28. Launch flags `--mcp-config`, `--strict-mcp-config`, `--settings`, `--setting-sources`, `--add-dir`, `--plugin-dir`, `--fallback-model` and `--allow-dangerously-skip-permissions` MUST carry, as do `/add-dir` additions. `--ide`, `--chrome`, `--bare` and `--remote-control` also persist across retire and wake (2.1.169).
29. The task list moves with the conversation (2.1.210).

### Settings, provider, environment

30. Settings MUST be read from the session's directory as a new `claude` there would, including project `env`.
31. The session MUST run with the dispatching shell's `PATH`, cloud provider selection, `ANTHROPIC_DEFAULT_*_MODEL` aliases and `CLAUDE_CODE_EXTRA_BODY`.
32. A shell-exported gateway `ANTHROPIC_BASE_URL` reaches a session only when the supervisor started from a shell exporting the same gateway, and only when backgrounding, dispatching into the current directory, waking from the current directory, or respawning there. The same applies to a cloud-provider gateway's endpoint-and-flag pair. Forwarded values MUST apply to the process only and MUST NOT be written to disk. Otherwise a session shows `No LLM gateway`.
33. Authentication comes from stored credentials through the supervisor.
34. `CLAUDE_CONFIG_DIR` MUST give a separate supervisor instance with its own sessions.

### Permission mode, model, effort

35. `/bg` or `←` keeps the current mode.
36. `claude agents` from a shell, and `--bg`, start as a new `claude` would, unless dispatch defaults apply.
37. Dispatching from an agent view opened by `←` takes the target's `permissions.defaultMode` if allowed, else the mode of the originating session. `auto` and `bypassPermissions` as `defaultMode` count only from managed settings, a `--settings` file or user settings. A project or local `defaultMode` more permissive than the originating session MUST be refused.
38. Permissiveness order: plan, then Manual and `dontAsk`, then `acceptEdits` and auto (each more permissive than the other), then `bypassPermissions`.
39. Starting in `bypassPermissions` requires the disclaimer acceptance on record. Without it a dispatch may start in Manual mode with `Bypass permissions was requested at launch and ignored`.
40. Permission mode, model, effort, carried flags and names MUST persist across restarts. Effort taken from settings MUST re-read on each process start.

### File isolation

41. A dispatched or `--bg` session starts in the working directory, reads the shared checkout, and MUST move into a worktree under `.claude/worktrees/` before editing. `Edit`, `Write` and `NotebookEdit` on the shared checkout MUST be blocked until then, and the session MUST be told so in advance (2.1.169).
42. Worktree move is skipped for: sessions moved with `←` or `/background`; sessions already in a linked worktree; targets inside a linked worktree; non-git directories with no `WorktreeCreate` hook; writes outside the working directory.
43. `worktree.bgIsolation: "none"` MUST let sessions edit the checkout directly.
44. If the hook fails outside a repository, edits proceed in place.
45. Once in a worktree, [isolation enforcement](worktrees.md) covers the session and its subagents.
46. After code changes in a worktree it entered, a session MUST commit without asking, push the branch if a remote exists, open a draft PR only when the task calls for one, and never push to `main` or `master`, force-push or merge. Git instructions in the task, CLAUDE.md or memory take precedence.
47. A session editing a checkout it did not isolate MUST ask before committing or switching branches.
48. Every job MUST end with a report of what it did and where the work lives.

### Deleting

49. Delete means `Ctrl+X` twice or `claude rm`. The session leaves the list, survives supervisor restarts as removed, and the transcript stays available through `claude --resume`.
50. Agent view removes a Claude-created worktree, including uncommitted changes. `claude rm` keeps it, and the row, when uncommitted changes exist.
51. Both MUST refuse a worktree in use or locked by another session, naming the directory and reason. Agent view shows `not deleted`.
52. Commits not confirmed saved elsewhere MUST keep the worktree and session, naming the branch and count. Commits on a remote do not block, nor do commits on the local copy of `origin`'s default branch when that branch is checked out in the main checkout.
53. Deleting again discards only what the refusal showed (`--discard-unpushed <commit>@<worktree-id>`). New commits keep it again. Another finished session's record naming the worktree also keeps it.
54. If git or `WorktreeRemove` fails, the worktree and session are kept with the cause named. `--force-remove-worktree <worktree-id>` is offered only for a linked worktree under `.claude/worktrees/`, with clean tracked files in it and in submodules, and no other session's record naming it. The branch stays.
55. A worktree git no longer recognises MUST NOT block; the directory is left on disk.
56. User-created worktrees are left in place.
57. A directory belonging to no repository: agent view double-press removes it, or runs `WorktreeRemove` for a hook-created one, refusing if there is no hook. `claude rm` keeps it while files remain.

## Configuration & interfaces

### Commands

| Command | Purpose |
| --- | --- |
| `claude agents [--cwd] [--json [--all]]` | View or list |
| `claude attach <id\|name>` | Attach; by name only while running |
| `claude logs <id\|name>` | Recent output |
| `claude stop\|kill <id>` | Stop, keep conversation |
| `claude respawn <id>` / `--all` | Restart, resuming a saved conversation |
| `claude rm <id>` | Delete |
| `claude daemon status` | State, version, socket directory, worker count; warns on version skew |
| `claude daemon logs` | Follow `~/.claude/daemon.log` |
| `claude daemon stop --any [--keep-workers]` | Stop supervisor |

### State

| Path | Content |
| --- | --- |
| `~/.claude/daemon.log` | Log; multi-line messages written as one JSON-quoted line |
| `~/.claude/daemon/roster.json` | Running sessions |
| `~/.claude/daemon.lock` | Lock |
| `~/.claude/jobs/<id>/state.json` | Session state; not a stable interface |
| `~/.claude/jobs/<id>/tmp/` | Scratch; `Write` and `Edit` do not prompt there; removed on delete |

Older versions rewriting `state.json` or `roster.json` MUST preserve unknown fields. `CLAUDE_JOB_DIR` is set for each session.

### `claude agents --json`

Fields: `cwd`, `kind` (`interactive`, `background`), `startedAt`; `id`, `state` (`working`, `blocked`, `done`, `failed`, `stopped`) for background; `pid`, `status` (`busy`, `waiting`, `idle`) while alive; `waitingFor` (`permission prompt`, `input needed`, `sandbox request`, `worker request`, `dialog open`); `sessionId`, `name`. It is the supported state interface. `blocked` always means needing the user. A session awaiting its next instruction reads `done`.

### Settings and variables

`disableAgentView`, `CLAUDE_CODE_DISABLE_AGENT_VIEW`, `worktree.bgIsolation`, `defaultToAgentsView`, `leftArrowOpensAgents`, `CLAUDE_CODE_DISABLE_BG_EXIT_HANDOFF`. `/status` shows `Session kind`: `background job · attached`, `background job · unattended`, or `interactive`.

## Failure modes & edge cases

- Machine off under 48 hours: running sessions show failed. Over 48 hours: stopped with `ended while the background service was off`, and a first `Enter` asks before resuming. A session waiting on input stays under `Needs input`.
- Transcript cleaned up: nothing to resume; `claude respawn` reruns the original prompt.
- Conversation open elsewhere: refused, with `Open in a terminal` or an already-open message.
- No saved transcript: `claude attach` reports it; agent view offers a fresh restart.
- Host process death fails within seconds on Linux and WSL.
- Silent early exit on low memory adds a `possibly low memory` note, a hypothesis only.
- `background service did not respond`: stop with `--keep-workers`, then reopen within a minute.
- macOS: protected folders and Local Network need separate grants for the Claude Code entry.
- Monitor-owning subagents stop with the monitor.

## Changes since the snapshot

- 2.1.139: agent view and hosted sessions. 2.1.142, 2.1.143: dispatch flags, `worktree.bgIsolation`.
- 2.1.147: pinned sessions. 2.1.154: `--exec`.
- 2.1.169: pre-move edit warning. 2.1.196: restart resume; single `←`.
- 2.1.198: notifications; commit, push and draft PR. 2.1.221: narrowed to preserving work, draft PR only when called for.
- 2.1.208: `Ctrl+X` protects unpushed commits. 2.1.212: `/resume` in view. 2.1.257: in-place `--resume --bg`.
- 2.1.260, 2.1.268: delete refusals and overrides. 2.1.295: exiting view no longer starts a supervisor.
- 2.1.299: `--bg` position rule. 2.1.300: carried workflows resume through the Workflow tool's approval.

## Open questions

- Snapshot subcommand `ps` is not in `--help`; whether it remains as an alias.
- Whether the supervisor is installable as a service. Changelog 2.1.295 mentions "Linux without the service installed", without details.
- Windows behaviour when the supervisor dies; docs specify macOS and Linux only.
