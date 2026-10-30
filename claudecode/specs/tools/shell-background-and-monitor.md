# Background Execution, Monitor and TaskStop

**Status:** shipped
**Provenance:** both (Monitor: post-leak since v2.1.98, 2026-04-09; gated reference in snapshot)
**Sources:** docs `tools-reference` (Background commands, Monitor tool), `interactive-mode`, `headless`, `agent-sdk/typescript`, `plugins/components`, `plugins/manifest-reference`, `worktrees`, `sub-agents`; snapshot `tools/BashTool`, `tools/TaskStopTool`, `tools/TaskOutputTool`, `tools.ts`; changelog 2.1.98 to 2.1.314

## Purpose

Let long-running work continue without blocking the conversation. Background shell commands run as tracked tasks. `Monitor` turns a running source into a stream of events the model reacts to. `TaskStop` ends tasks.

## Behaviour

### Starting background work

1. Claude starts a command in the background with `run_in_background: true`. The call MUST return a task ID at once.
2. The user can press `Ctrl+B` to move a running command to the background (twice under tmux).
3. A foreground command reaching its timeout MUST move to the background rather than stop, unless it starts with `sleep`. See requirements 17 and 18.
4. `CLAUDE_CODE_DISABLE_BACKGROUND_TASKS=1` or bare mode MUST remove `run_in_background` from Bash, PowerShell and subagents, turn off `Ctrl+B`, and make a command stop at its timeout.

### Output access

5. Output MUST be written to a file. Claude reads it with `Read`; `TaskOutput` was removed in v2.1.277.
6. Background tasks are killed if output exceeds 5 GB, with a note saying why.

### When a background command stops

7. A command started by a foreground subagent MUST stop when that subagent's run ends for any reason. `backgroundEndsWithFinalResponse: true` marks such a command (v2.1.227+).
8. A command started by the main conversation or a background subagent keeps running after a final response until it exits, is stopped, or reaches its time limit.
9. On exit, tasks are cleaned up. On macOS and Linux, stopping a task from `/tasks` or at exit also stops detached processes, such as those under `setsid` or `timeout`.
10. Backgrounding the session itself keeps tasks running in the background session.
11. On macOS and Linux, tasks MUST be stopped under critical memory pressure when the session has been idle at least 30 minutes with no turn or subagent running, unless `CLAUDE_CODE_DISABLE_BG_SHELL_PRESSURE_REAP=1`.
12. After the user stops a task from `/tasks` or a connected client, Claude (or the owning subagent) moves on instead of waiting.

### Time limit

13. Unattended sessions (`-p`, Agent SDK, CI, cloud) MUST apply a time limit to background Bash and PowerShell commands. Terminal, desktop and VS Code sessions have none (since 2.1.288; 2.1.285 applied it everywhere).
14. The limit counts from entering the background:

| Case | Default | Maximum |
| :- | :- | :- |
| Started in background | 30 minutes, or Claude's `timeout` | 2 hours |
| Moved from foreground | 30 minutes from the move | n/a |
| `-p` with prompt as text (not `--input-format stream-json`) | 10 minutes for both | 2 hours |

15. At the limit Claude Code MUST stop the command and tell Claude, with `Background command "<description>" was stopped after reaching its background time limit`. Claude may restart it with a longer `timeout`.
16. Environment variables can only raise limits:
    - `BASH_DEFAULT_TIMEOUT_MS` above 1,800,000 replaces the 30-minute default (above 600,000 for the text-prompt `-p` default).
    - `BASH_MAX_TIMEOUT_MS` above 7,200,000 raises the maximum, as does `BASH_DEFAULT_TIMEOUT_MS` above it.
    - Lower values leave defaults in place.

### Moved-command results

17. The result MUST state `Command did not complete within its 120s timeout and was moved to the background`, with the actual seconds, the task ID and the output file path.
18. A `cd`, `pushd`, `popd` or `chdir` in a moved command never carries over. The result states `Session cwd remains <dir>; directory changes made by the backgrounded command do not apply to subsequent commands.` (`backgroundCwdHint`).

### Non-interactive runs

19. After the final result, a `-p` run MUST stay open for background work the main conversation started until it exits or reaches its time limit, then take one more turn. A command a background subagent started is stopped when the run exits.
20. Monitor watches hold the run until they time out or the idle cap ends the wait. Pending `/loop` wakeups in a text-prompt run are waited for even past the cap.
21. The cap is 10 minutes of idle waiting (`CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS`, `0` for none). `--max-budget-usd` stops remaining work.

### Monitor

22. Input is `description`, `timeout_ms`, and exactly one of `command` or `ws`. Output is `taskId`, `timeoutMs`, optional `persistent`.
23. A `command` source runs in the background and each stdout line MUST become an event delivered to Claude mid-conversation, without pausing it. The user keeps working and Claude interjects.
24. **Deadlines.** Every watch MUST have one (2.1.271, replacing the no-timeout `persistent` option): default 300,000 ms; values up to 3,600,000 validate but the effective maximum is 30 minutes, and 10 minutes in a single-prompt `-p` run. At the deadline the watch ends and Claude gets one notice so it can re-arm.
25. A watch that exits with no output MUST say so (2.1.221). Final output and exit arrive as one notification (2.1.274). Event rows show what was printed (2.1.284).
26. Monitors stop on request through `TaskStop`, on session end, or with a stopped parent subagent. On `--resume`, background commands and monitors are not restarted.

### Monitor WebSocket source

27. `ws` takes `url` (required; `ws://` or `wss://`, ASCII, no embedded credentials or whitespace) and `protocols` (optional valid unique subprotocol tokens). Requires v2.1.195+.
28. Event mapping:

| Socket activity | Result |
| :- | :- |
| Text message | One event, even if multi-line |
| Binary message | Placeholder such as `[binary frame, 512 bytes]` |
| Message over 1 MiB | Watch ends |
| Close | Watch ends; Claude gets the close code |

29. Opening a socket MUST prompt, or be decided by the classifier in auto mode, and the prompt MUST NOT offer a skip-for-this-host option.
30. Claude Code MUST deny private, link-local and cloud-metadata addresses, including hostnames resolving to one; hosts in `sandbox.network.deniedDomains`; and, with managed `allowManagedDomainsOnly`, hosts outside the managed allowlist.

### Monitor permissions

31. Commands use Bash rules (`Bash(...)`). In auto mode allow rules naming `Monitor` are set aside, so the classifier reviews commands as for Bash (2.1.236).
32. Hooks matching Bash run on Monitor commands and can block or ask, but not approve or rewrite (2.1.314). Hook `if` conditions such as `Monitor(tail *)` match the commands as `Bash(tail *)` does (2.1.314).
33. Sandboxed Monitor commands follow permission rules under auto-allow (fixed 2.1.290). Worktree isolation applies the same working-directory and command-shape checks as Bash.
34. Availability: on Bedrock, Claude Platform on AWS, Agent Platform and Foundry, or with `DISABLE_TELEMETRY` or `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC`, it needs v2.1.310+. On Windows it needs Git Bash.

### Plugin monitors

35. Plugins declare monitors in `monitors/monitors.json` or under `experimental.monitors`, each with `name`, `command`, `description`, and `when` of `"always"` (default) or `"on-skill-invoke:<skill>"`.
36. They run in a shell in the session's working directory, with full user permissions and outside the sandbox, and do not start in `-p` mode. `${user_config.*}` in `command` is rejected, and `CLAUDE_PLUGIN_OPTION_<KEY>` is not provided. Disabling a plugin mid-session leaves running monitors until session end.

### TaskStop

37. Input is `task_id`, with deprecated `shell_id`. Output is `message`, `task_id`, `task_type`, optional `command`.
38. `task_id` also accepts a teammate or named background agent by ID or name (v2.1.198). If nothing matches, the error MUST list running background agents by ID and description, including agents another agent spawned.
39. Legacy names `KillShell` and `KillBash` resolve to `TaskStop`.

### UI

40. `/tasks` lists and stops tasks and shows watches under **Monitors**; watches the system started sit under a **System tasks** row. Tool results and events also reach Agent SDK clients as task messages.

## Configuration & interfaces

| Key | Effect |
| :- | :- |
| `CLAUDE_CODE_DISABLE_BACKGROUND_TASKS` | Remove backgrounding |
| `CLAUDE_CODE_DISABLE_BG_SHELL_PRESSURE_REAP` | Keep tasks under memory pressure |
| `CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS` | `-p` idle wait cap |
| `CLAUDE_CODE_TOOL_MEMORY_LIMIT` | Shared memory cap, including Monitor (v2.1.246+) |

Stop hook input carries `background_tasks` and `session_crons`, so a hook can tell "done" from "waiting".

## Failure modes & edge cases

- The 2.1.285 limit applied in every session; the 2.1.288 change narrowed it, so behaviour depends on version.
- A session resumed after exit has no running monitors.
- A stopped subagent takes its monitors with it.
- SDK `MonitorOutput` still lists `persistent` after its removal as an input option.
- `sleep`-prefixed foreground commands stop at timeout instead of moving.

## Changes since the snapshot

- 2.1.98: Monitor added. 2.1.105: plugin monitors. 2.1.129: declare them under `experimental`.
- v2.1.195 (SDK docs): `ws` source.
- 2.1.207: `${user_config.*}` rejected in monitor shell commands.
- 2.1.236: Monitor allow rules set aside in auto mode.
- 2.1.257: `-p` waits for armed Monitors.
- 2.1.271: mandatory deadlines; `allowed_domains` on Monitor.
- 2.1.277: `TaskOutput` removed.
- 2.1.285, 2.1.288: background time limit, then narrowed to unattended sessions.
- 2.1.310: Monitor on third-party providers and with telemetry off.
- 2.1.314: Monitor hook matching.

## Open questions

- Whether `persistent` in `MonitorOutput` can ever be set.
- Precisely how the 3,600,000 accepted maximum is shortened in `-p` runs.
- The file location and retention of background output files beyond "session directory".
