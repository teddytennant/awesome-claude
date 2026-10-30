# Scheduling Tools: Cron*, ScheduleWakeup, RemoteTrigger

**Status:** shipped
**Provenance:** both (`ScheduleWakeup`: post-leak; docs give v2.1.202 for its `stop` field; first changelog mention 2.1.248)
**Sources:** docs `scheduled-tasks`, `routines`, `tools-reference`, `agent-sdk/typescript`, `headless`, `env-vars`, `hooks`; snapshot `tools/ScheduleCronTool`, `tools/RemoteTriggerTool`, `tools.ts`; changelog 2.1.101 to 2.1.314

## Purpose

Run prompts later or repeatedly. Three tiers exist: session-scoped tasks in a running session, Desktop tasks on the user's machine, and cloud scheduled tasks (formerly routines) hosted by Anthropic. This spec covers the tools; Desktop tasks and the routines web UI are specified elsewhere.

| | Cloud | Desktop | `/loop` and Cron* |
| :- | :- | :- | :- |
| Needs machine on | No | Yes | Yes |
| Needs open session | No | No | Yes |
| Survives restart | Yes | Yes | Restored on `--resume`, with exceptions |
| Local files | No, fresh clone | Yes | Yes |
| Permissions | Auto mode by default | Per task | Inherits session |
| Minimum interval | 1 hour | 1 minute by Claude, 1 hour in forms | 1 minute |

## Behaviour

### CronCreate, CronList, CronDelete

1. `CronCreate` input: `cron`, `prompt`, optional `recurring`, `durable`. `recurring: false` fires once at the next match. Output: `id`, `humanSchedule`, `recurring`, optional `durable`, `nextFireAt` (epoch ms, jitter applied; v2.1.299+).
2. `CronList` returns `jobs` with `id`, `cron`, `humanSchedule`, `prompt`, optional `recurring`, `durable`, `nextFireAt`. `nextFireAt` is never earlier than the call. Session-only jobs carry `durable: false`; jobs read from disk omit it.
3. `CronDelete` takes `id` and returns it.
4. Each task has an 8-character ID, and a session MUST hold at most 50.
5. Cron is the 5-field form in local time, supporting `*`, values, steps, ranges and comma lists. Day-of-week takes `0` or `7` for Sunday. `L`, `W`, `?` and name aliases are not supported. When both day-of-month and day-of-week are constrained, either matching counts.
6. Tasks fire only while Claude Code runs and is idle. The scheduler checks each second and enqueues at low priority, firing between turns. A task due mid-turn waits. Missed fires do not catch up: one fire on idle.
7. Fired prompts are delivered as the session's assigned task (2.1.214) and classified as task notifications, not keyboard input, so they cannot approve a pending action (2.1.183).

### Jitter and expiry

8. Recurring tasks start late by up to half the gap to the next run, at most 30 minutes. Even gaps get a stable delay; uneven gaps can vary.

| Schedule | Start |
| :- | :- |
| `*/5 * * * *` | 4 min 45 s after the previous run (kept inside a 5-minute cache window) |
| Every 10 min | 0 to 5 min late |
| Every 30 min | 0 to 15 min late |
| Hourly or rarer | 0 to 30 min late |

9. One-shot tasks on `:00` or `:30` run up to 90 seconds early; other minutes are unshifted.
10. Recurring tasks MUST expire seven days after creation: they fire a final time and delete themselves. One-shot tasks delete after firing.

### Persistence

11. Tasks are session-scoped by default. `--resume` and `--continue` restore them, except expired recurring tasks and one-shots whose time passed.
12. A restored recurring task does not make up missed runs; its next run is the first due after resume, with jitter.
13. `durable: true` requests persistence to `.claude/scheduled_tasks.json`. Durable scheduling is not available in every session; where it is not, the call succeeds as session-only and the `durable` output field reports the truth.
14. With feature-flag fetching off, a task kept across sessions goes in that file. A symlinked `.claude` or file MUST return an error. A copied file lists tasks but they do not run in the other folder (2.1.273).
15. Backgrounding a session carries `/loop` tasks over.

### /loop

16. A bundled skill. Argument forms:

| Input | Behaviour |
| :- | :- |
| Interval and prompt | Fixed schedule through cron |
| Prompt only | Self-paced |
| Interval only, or nothing | Built-in maintenance prompt or `loop.md` |

17. Intervals lead as a token (`30m`) or trail as a clause (`every 2 hours`), in `s`, `m`, `h`, `d`. Seconds round up to a minute. Intervals with no clean cron step round to the nearest one, and Claude says so.
18. A prompt may be a skill, but a scheduled fire runs only skills Claude may invoke itself. Built-in commands, `disable-model-invocation` skills, skills withheld by `skillOverrides` or a deny rule, and MCP prompts arrive as plain text.
19. The maintenance prompt, in order: continue unfinished work; tend the branch's PR (comments, failed CI, conflicts); run cleanups when idle. It does not start new initiatives, and irreversible actions proceed only if the transcript authorised them.
20. `.claude/loop.md` beats `~/.claude/loop.md`; content over 25,000 bytes is cut; edits apply at the next iteration; it is ignored when a prompt is given.
21. Monitor MAY replace polling when a dynamic schedule is requested.
22. Stopping: a self-paced loop stops with `Esc`, or `Ctrl+C` while idle except in an attached background session, showing `Pending wakeup cancelled`. Fixed loops and directly scheduled tasks need Claude to cancel them.
23. `Ctrl+C` twice on an empty prompt detaches from a background session and leaves a self-paced loop running (v2.1.295+).

### ScheduleWakeup

24. Input: `delaySeconds`, `reason`, `prompt`, `noop`, `stop`. The first four are required unless `stop` is true. `noop: true` reports a wake-up where nothing changed.
25. Delay MUST be clamped to 60 to 3600 seconds. Output: `scheduledFor`, `clampedDelaySeconds`, `wasClamped`, optional `stopped`, `cancelledWakeups`.
26. Claude calls it at the end of each self-paced iteration. `stop: true` cancels pending wakeups and ends the loop, but does not cancel a recurring `/loop` cron; `cancelledWakeups` of `0` means nothing was pending.
27. If an iteration neither reschedules nor stops, one fallback wakeup MUST fire about 20 minutes later, and the loop ends if that iteration also does neither.
28. The pending wakeup appears as a one-shot in the task list, in `session_crons` in Stop hook input, and is subject to early-run and seven-day rules.
29. A self-paced loop is not restored on resume. In a background session, a wakeup due while the process is down stops the loop, and the transcript shows a notice (2.1.295).
30. Subagents never get the tool. In a text-prompt `-p` run, the run waits for each wakeup, past the idle cap.
31. Claude writes each status update and the stop outcome as visible text (2.1.284).

### RemoteTrigger

32. Backs `/schedule` (alias `/routines`). Input: `action`, optional `trigger_id`, `session_id`, `cursor`, `body`. Output: `status`, `json`, optional `summary`.

| Action | Needs | Since |
| :- | :- | :- |
| `list` | | |
| `get` | `trigger_id` | |
| `create` | `body` | |
| `update` | `trigger_id`, `body` | |
| `run` | `trigger_id`; `body` optional | |
| `create_webhook_trigger` | `body` naming source, events and task | v2.1.225 |
| `list_runs` | `trigger_id`; paged by `cursor` | v2.1.227 |
| `get_run_log` | `session_id` from `list_runs`; paged by `cursor` | v2.1.227 |

33. Available only with a claude.ai login on a plan with scheduled tasks. Absent when org policy disables cloud sessions, or (v2.1.227+) when an Owner turned off scheduled tasks. Not reachable on Bedrock, Claude Platform on AWS, Agent Platform or Foundry.
34. Authentication is handled in-process; the API surface is not specified here.
35. Cloud tasks: cron more often than hourly is rejected. A run starts in auto mode unless unavailable, and can pause for a person on ask rules or repeated blocks. Triggers are schedule, API and GitHub events. MCP servers configured in Claude Code cannot attach to cloud tasks; connectors are per task (2.1.251).

## Configuration & interfaces

| Key | Effect |
| :- | :- |
| `CLAUDE_CODE_DISABLE_CRON=1` | Disables scheduler, cron tools and `/loop`; pending tasks stop firing |
| `.claude/loop.md`, `~/.claude/loop.md` | Default loop prompt |
| `.claude/scheduled_tasks.json` | Durable store |

Self-paced loops and the maintenance prompt work on every provider, and with feature-flag fetching off, from v2.1.248. `/proactive` is an alias of `/loop` (2.1.105). `/usage` has a Loops breakdown (2.1.243).

## Failure modes & edge cases

- DST fall-back previously re-fired tasks after every turn (fixed 2.1.299).
- Delivery failure previously re-fired every second (fixed 2.1.281).
- Cloud sessions: a lost wakeup after container restart leaves the session asleep with no notice, after 2.1.293 reverted a 2.1.290 fix.
- Pending loops do not keep a remote container alive, so `/loop` is not promoted there (2.1.172).
- `/schedule` shows `Unknown command` or a specific message by auth state; API keys disable it even with a claude.ai login present (2.1.139).
- Scheduled turns ask before the first publish of an artifact in the session case; see [post-leak-artifact](post-leak-artifact.md).

## Changes since the snapshot

- 2.1.101: RemoteTrigger `run` sends a proper body.
- 2.1.105, 2.1.113: `/proactive` alias; Esc cancels wakeups.
- 2.1.183, 2.1.214: fired prompts treated as task notifications and assigned tasks.
- v2.1.202, v2.1.206: `stop`, `cancelledWakeups`.
- v2.1.225, v2.1.227: `create_webhook_trigger`, `list_runs`, `get_run_log`.
- 2.1.243: wake-ups with nothing to do fold into one line.
- 2.1.248: self-paced mode on all providers.
- 2.1.290, 2.1.292, 2.1.295: resume, compaction and background reliability.
- v2.1.299: `nextFireAt`; next run shown in tool rows.
- 2.1.304: wakeups at the 1-hour maximum no longer fall just past the cache TTL.

## Open questions

- Exact `recurring` default; the snapshot and SDK text imply true.
- Which sessions support `durable`; the snapshot used a remote gate.
- How `prompt` on `ScheduleWakeup` interacts with `loop.md` edits.
- Trigger `body` schema.
