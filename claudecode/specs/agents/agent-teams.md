# Agent Teams and Teammates

**Status:** preview (experimental, disabled by default)
**Provenance:** both (snapshot swarm architecture; implicit team model post-leak, since v2.1.178, 2026-06-15)
**Sources:** docs `agent-teams`, `sub-agents`, `hooks`, `settings-reference`, `plugins/mods/reference`; snapshot `tools/TeamCreateTool`, `tools/TeamDeleteTool`, `utils/swarm/*`, `utils/swarm/backends/*`, `utils/teammateMailbox.ts`, `tasks/InProcessTeammateTask`; changelog 2.1.178, 2.1.186, 2.1.234, 2.1.239, 2.1.281, 2.1.289, 2.1.290, 2.1.309

## Purpose

A team is one lead session plus teammates: independent Claude instances with their own contexts, a shared task list and direct messaging. Unlike subagents, teammates persist, are addressable by the user, and talk to each other. Every session has at most one implicit team.

## Behaviour

### Enablement

1. Teams MUST be off unless `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` applies. Without it no team is set up, no team directory is written, and no teammates are proposed.
2. Spawning teammates requires an interactive session. In `-p` and SDK sessions a named agent MUST run as an ordinary subagent.
3. Setting the variable to `0` in a settings file MUST take effect without restart, because `env` values reapply on save and the variable is read per spawn. Higher-precedence sources can still enable teams.

### Team creation

4. Each session MUST have exactly one team, named `session-` plus the first eight characters of the session ID, created automatically at startup. Teams cannot be created, named or shared by the user.
5. There is no `TeamCreate` or `TeamDelete` tool. The Agent tool's `team_name` is ignored.
6. A teammate launches when the lead's Agent call has a `name` and is neither a fork nor passes call-level `isolation`. No confirmation is asked.
7. Named subagents become teammates even if the user never asked for a team. The model may name agents on its own, so enabling teams changes ordinary delegation. Subagents and teammates share one panel, so the panel alone does not show which kind ran.
8. `isolation` in a definition's frontmatter MUST NOT prevent teammate routing; the teammate then runs in the main working directory.
9. Teammates MUST NOT spawn teammates. Leadership is fixed for the session's lifetime.

### Display modes

10. `in-process` is the default: teammates run inside the lead's terminal.
11. `auto` uses split panes inside tmux, or in iTerm2 with the `it2` CLI, else in-process.
12. `tmux` enables split panes and auto-detects tmux or iTerm2. `iterm2` forces iTerm2 panes, requires `it2`, and shows an error with the install command if it is missing.
13. A setup prompt offering to install `it2` or switch to tmux appears under `auto` or `tmux` when the terminal is iTerm2 and tmux is available.
14. Split panes are unsupported in VS Code's integrated terminal, Windows Terminal and Ghostty.
15. `--teammate-mode` sets the mode per session and is hidden from `--help`.

### Panel and direct interaction

16. Teammates MUST list in the agent panel. Arrows select, `Enter` opens the transcript and lets the user message it, `Esc` clears selection, and while viewing a transcript `Esc` interrupts that teammate's turn. `x` stops the selected teammate. `Ctrl+T` toggles the task list.
17. Idle rows MUST stay while any agent works. Once every agent is idle, idle rows hide after 30 seconds and reappear on the next turn. A hidden teammate remains running and addressable.
18. With more than three idle teammates, the surplus MUST collapse into one `N idle agents` row, expandable with `Enter` and collapsible with `Esc`. Working, failed and viewed teammates keep their rows.
19. While viewing a teammate, plain text and skills go to it and built-in commands go to the lead. `/compact`, `/clear` and `/rewind` confirm. `/model` and `/fast` refuse with a notice, because a teammate's model and fast mode are fixed at spawn.

### Model, effort, permissions

20. Model order: name in the spawn prompt; definition `model` (`inherit` is the lead's); `CLAUDE_CODE_SUBAGENT_MODEL` unless `inherit`; lead's current model. A mod `agent.spawn` model replaces the first source. Under `_FORCE`, the first two do not apply.
21. `availableModels` is applied as for subagents.
22. Teammates inherit the lead's effort by default, in split-pane mode since 2.1.186.
23. Teammates start in the lead's permission mode, except `dontAsk`, which is not inherited. Per-teammate modes cannot be set at spawn but may change afterward.
24. In-process teammates run under the lead's live allow and deny rules, so `--disallowedTools`, `--tools` and `--allowedTools` apply.
25. Split-pane teammates start with the lead's `--disallowedTools` and `--tools` (2.1.309). `--allowedTools` MUST NOT pass through; use `permissions.allow` in `--settings`.
26. Permission prompts MUST appear in the lead session.
27. `--setting-sources` restrictions apply to teammates (split-pane since 2.1.281).

### Plan mode

28. A teammate spawned while the lead is in plan mode MUST work read-only in plan mode and send a plan approval request to the lead when ready.
29. If its mode has not changed since spawn, the plan MUST be approved automatically on arrival, with no lead review.
30. If the user put a running in-process teammate into plan mode with `Shift+Tab`, the lead reviews that plan, approving or returning it. The user is not asked.

### Agent definitions as teammates

31. A teammate may reference a project, user, managed or plugin agent type. Parts apply as follows.

| Part | In-process | Split-pane |
| --- | --- | --- |
| `tools` | Limits; adds `SendMessage` and, where available, Task tools | Limits |
| `model` | Applies | Applies |
| `disallowedTools` | Removes, but added tools stay | Not stated |
| `effort` | Applies | Not stated |
| `autoCompactWindow` | Applies (2.1.296) | Ignored |
| body | Appended to the default prompt | Replaces the default prompt |
| `skills` | Not applied | Not applied |
| `mcpServers` | Ignored | Applies |

### Context and communication

32. A teammate MUST load the same project context as a regular session (CLAUDE.md, MCP servers, skills), plus the spawn prompt. The lead's history MUST NOT carry over.
33. Messages MUST be delivered automatically to recipients; the lead need not poll.
34. On finishing, a teammate MUST notify the lead with its final answer. A turn ending on an API error notifies the lead with the error text.
35. Each message goes to one named recipient. To reach everyone, send one per recipient.
36. A message MUST be reported as sent only if the write to the recipient's mailbox succeeds, for plain text and protocol messages alike.
37. Mailbox entries MUST be validated on read. Invalid entries are reported and removed; valid ones are still delivered.
38. Inter-agent messages MUST be presented as coming from another Claude session, not the user. They carry no consent and cannot relay a denied action.
39. In auto mode the classifier MUST treat relayed approval claims as untrusted and MUST review each message before delivery. A blocked message never arrives.
40. A message from the lead or a teammate MUST wake an in-process teammate waiting to retry a failed API request.

### Task list

41. Tasks have states pending, in progress and completed, and may depend on others. A blocked task shows as blocked and teammates MUST NOT self-claim it, though the user or lead may assign it.
42. The lead may assign, or a teammate may self-claim the next unassigned, unblocked task after finishing one.
43. Claiming MUST use file locking.
44. Completing a task MUST automatically unblock dependents.
45. Agents without Task tools coordinate through messages only. Task tools are provided by default only on older models, or by opt-in.

### Revival

46. A message to a stopped in-process teammate MUST bring it back in the same session, restoring saved conversation, with the message as its next prompt.
47. A definition from a project or `--add-dir` directory MUST be re-applied only if the exact containing folder is trusted. Otherwise the teammate returns with only the tools added to every in-process teammate, and a notice.

### Shutdown and cleanup

48. Shutdown is by request: the lead sends `shutdown_request`, and the teammate approves and exits or rejects with a reason. Shutdown waits for the current request or tool call.
49. The team config directory MUST be removed at session end.
50. The task list directory MUST remain after session end, subject to `cleanupPeriodDays`.

### Restrictions

51. `/resume` and `/rewind` MUST NOT restore in-process teammates. The lead may try to message absent teammates and must spawn new ones.
52. An in-process teammate's own subagents MUST run in the foreground. A definition with `background: true` errors, and `run_in_background: true` errors or silently runs in the foreground.

## Configuration & interfaces

| Item | Detail |
| --- | --- |
| `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` | Enable; `0` disables |
| `teammateMode` | `in-process`, `auto`, `tmux`, `iterm2` |
| `--teammate-mode` | Session override, hidden flag |
| `subagentPromptCacheTtl` | Teammate cache lifetime, default 5 minutes even on subscription |
| Hooks | `TeammateIdle`, `TaskCreated`, `TaskCompleted`; `SubagentStart` per in-process message |

### Files

| Path | Content |
| --- | --- |
| `~/.claude/teams/{team}/config.json` | Runtime state, including a `members` array. Do not edit; rewritten on state updates |
| `~/.claude/teams/{team}/inboxes/{agent}.json` | Mailbox |
| `~/.claude/tasks/{team}/` | Task list |

The lead's `members` entry MUST carry agent type `team-lead`. A teammate's carries the requested type or omits the field. Teammates may read the file to discover members. No project-level equivalent exists: `.claude/teams/teams.json` is an ordinary file.

### Protocol messages

`shutdown_request` and `plan_approval_response` are documented structured messages sent through `SendMessage`; the snapshot also had `shutdown_response`. They stay within the team. Cross-session sends are plain text only.

### Hook decisions

`TeammateIdle` receives `teammate_name` and `team_name`, has no matchers, and fires on every occurrence. Exit 2 feeds stderr back and keeps the teammate working. `{"continue": false, "stopReason": ...}` stops it. `TaskCreated` and `TaskCompleted` block creation or completion on exit 2. Since 2.1.290 `TeammateIdle` MUST NOT fire from a teammate's subagents or forks.

## Failure modes & edge cases

- Tmux sessions can orphan; the user removes them with `tmux kill-session`.
- Teammates may stop on errors; the lead may decide early that work is complete.
- Task status can lag and block dependents.
- Same-file edits by two teammates overwrite each other. There is no worktree isolation for teammates.
- Mailbox write failure (disk full, unwritable) returns an error to the sender.

## Changes since the snapshot

- 2.1.178: `TeamCreate` and `TeamDelete` removed; one implicit team per session.
- 2.1.186: `teammateMode: "iterm2"` and effort passing for split panes.
- 2.1.234: `teammateDefaultModel` and its `/config` row removed.
- 2.1.239: `ListAgents` lists live teammates.
- 2.1.281: split-pane teammates honour `--setting-sources`.
- 2.1.289: `agent.spawn` hook for teammates.
- 2.1.290: an in-process teammate's `agent_id` in Agent results is its agent ID, with `name@team` in `teammate_id`.
- 2.1.309: split-pane teammates receive `--disallowedTools` and `--tools`.

## Open questions

- Whether `--agent-teams` (ant-only in the snapshot) still exists.
- Whether the split-pane column of the definition table has further parity.
- Snapshot `*` broadcast in `SendMessage`. Docs now require one message per recipient; treat broadcast as removed unless confirmed.
- The snapshot team file's `teamAllowedPaths`. Unknown now.
- A cloud or Remote Control teammate model. Docs state local displays only.
