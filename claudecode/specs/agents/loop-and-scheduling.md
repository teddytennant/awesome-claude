# /loop, Self-Pacing and Session Cron

**Status:** shipped
**Provenance:** both (fixed-interval `/loop` and cron tools in snapshot; self-pacing, `ScheduleWakeup` and maintenance prompt post-leak)
**Sources:** docs `scheduled-tasks`, `tools-reference`, `agent-sdk/typescript`, `agent-view`, `hooks`; snapshot `skills/bundled/loop.ts`, `tools/ScheduleCronTool`, `utils/cronTasks.ts`, `utils/cronScheduler.ts`, `utils/cronJitterConfig.ts`, `tools/SleepTool`; changelog 2.1.105 to 2.1.295

## Purpose

Session-scoped scheduling reruns prompts while a session lives. `/loop` is the user entry point, either on a fixed cron interval or self-paced, where the model picks the delay after each iteration. Cloud routines and Desktop tasks are separate durable systems, specified elsewhere. For turn-after-turn work toward a condition, see [goal.md](goal.md).

## Behaviour

### `/loop` parsing

1. `/loop` is a bundled skill. `/proactive` is an alias (2.1.105).

| Input | Mode |
| --- | --- |
| Interval and prompt | Fixed |
| Prompt only | Self-paced |
| Interval only | Fixed, default prompt |
| Nothing | Self-paced, default prompt |

2. The interval may lead as a token (`30m`) or trail as a clause (`every 2 hours`). Units: `s`, `m`, `h`, `d`.
3. Seconds MUST round up to a minute. Intervals with no clean cron step, such as `7m` or `90m`, MUST round to the nearest that has one, and the model MUST report the choice.
4. A skill as the prompt reruns that skill. A scheduled fire MUST run only model-invocable skills. Built-in commands, `disable-model-invocation` skills, skills hidden by `skillOverrides` or a `Skill` deny rule, and MCP prompts MUST reach the model as plain text.

### Self-pacing

5. After each iteration the model MUST choose a delay from one minute to one hour, based on what it observed, and print the delay and reason.
6. Scheduling goes through `ScheduleWakeup`. The runtime MUST clamp `delaySeconds` to 60 to 3600.
7. `stop: true` MUST cancel the pending wakeup and end the loop. Other fields are required unless `stop` is true.
8. If an iteration neither reschedules nor stops, one fallback wakeup MUST be scheduled about 20 minutes later, and the loop MUST end if that iteration does not reschedule either.
9. The pending wakeup MUST appear in the task list as a one-shot task and in `session_crons` in Stop hook input. It is subject to one-shot early firing and the seven-day expiry.
10. Where the Monitor tool is available, the model may use it instead of polling for a dynamic `/loop`.
11. `ScheduleWakeup` MUST NOT be available to subagents.
12. Self-pacing and the default prompt work on every provider and with flag fetching off (2.1.248 for those cases).
13. Consecutive wake-ups with nothing to do SHOULD fold into one line (2.1.243). Wakeups display as `Claude resuming /loop wakeup`.

### Default prompt

14. With no prompt, the built-in maintenance prompt runs. Each iteration, in order: continue unfinished work from the conversation; tend the current branch's PR (comments, failed CI, conflicts); run cleanup passes when nothing else is pending.
15. It MUST NOT start new initiatives, and irreversible actions proceed only when they continue something the transcript authorised.
16. `loop.md` replaces it: `.claude/loop.md`, then `~/.claude/loop.md`, first found. It is ignored when a prompt is given. Edits apply at the next iteration. Content beyond 25,000 bytes is truncated.

### Stopping

17. Self-paced: `Esc` while waiting MUST stop the loop with `Pending wakeup cancelled`. `Ctrl+C` while idle does too, except in an attached background session.
18. In an attached background session, double `Ctrl+C` on an empty prompt MUST detach and leave the wakeup pending (2.1.295).
19. Fixed-interval tasks and directly scheduled tasks stop only by cancelling through the model (`CronDelete`) or by expiry. `Esc` and `Ctrl+C` MUST NOT stop them.

### Cron tools

20. `CronCreate` takes a 5-field expression, prompt and recurrence. `CronList` shows IDs, schedules, next run times and prompts. `CronDelete` cancels by ID.
21. IDs have 8 characters. A session holds up to 50 tasks.
22. Expressions are `minute hour day-of-month month day-of-week`, in local time, with `*`, values, steps, ranges and lists. `0` or `7` is Sunday. `L`, `W`, `?` and name aliases are unsupported. With both day fields constrained, either matching suffices.
23. One-time reminders from natural language use a single-fire task that deletes itself. The model pins minute and hour.

### Firing

24. The scheduler MUST check every second and enqueue due tasks at low priority, firing between turns, never mid-response.
25. There is no catch-up. A task missed while busy fires once when idle.
26. Jitter for recurring tasks: each run late by up to half the gap to the next, capped at 30 minutes. Evenly spaced tasks have a constant offset. Unevenly spaced ones can vary.
27. `*/5 * * * *`, which `/loop 5m` creates, is exempt: each run starts 15 seconds sooner, at 4 minutes 45 seconds after the last, so it lands inside the five-minute prompt cache.
28. One-shot tasks at `:00` or `:30` run up to 90 seconds early. Other minutes MUST NOT shift.
29. The `CronCreate` row shows `next run <time>`, and `CronList` too (2.1.299).
30. Recurring tasks expire seven days after creation: one final fire, then deletion.

### Persistence

31. Tasks fire only while the process runs and is idle. Backgrounding carries `/loop` tasks.
32. `--resume` and `--continue` MUST restore `CronCreate` tasks, except expired recurring tasks and past one-shots. A restored recurring task fires first at its next due run after resume, with jitter.
33. Self-paced loops MUST NOT be restored on resume. Background Bash commands and monitors are not restarted.
34. In a background session, a self-paced loop stops if its wakeup comes due while the process is down. The transcript shows a notice on restart. Sessions waiting on a wakeup are protected from updates and low-memory shutdown (2.1.290).
35. With feature-flag fetching off, tasks kept across sessions live in the project's `.claude/scheduled_tasks.json`. A symlinked `.claude` or file MUST error. A copied file lists but does not run tasks in another folder.

### Observability

36. `/usage` MUST include a Loops breakdown: per-loop run count, total tokens, tokens per run, last run (2.1.243).
37. Agent view shows `✢` rows with run count and countdown. Scheduled sessions notify only when needing input.
38. Teammates retain cron tools.

## Configuration & interfaces

### `ScheduleWakeup` input

| Field | Notes |
| --- | --- |
| `delaySeconds` | Clamped 60 to 3600 |
| `reason` | Printed |
| `prompt` | Fired |
| `noop` | Reports a wake-up where nothing changed |
| `stop` | Cancels the pending wakeup and ends the loop (2.1.202) |

### Variables and settings

`CLAUDE_CODE_DISABLE_CRON=1` MUST remove the cron tools and `/loop` and stop any scheduled tasks, including mid-session.

### Comparison

| | Cloud | Desktop | `/loop` |
| --- | --- | --- | --- |
| Needs machine on | No | Yes | Yes |
| Needs open session | No | No | Yes |
| Minimum interval | 1 hour | 1 minute by Claude, 1 hour in forms | 1 minute |
| Local files | No | Yes | Yes |

## Failure modes & edge cases

- A busy turn delays a fire indefinitely until idle.
- Cloud sessions: pending loops do not keep the container alive, and `/loop` is not promoted there (2.1.172). The fix for a lost wakeup was reverted in 2.1.293, so the session stays asleep with no notice.
- Editing `loop.md` to a large file truncates silently beyond the limit.

## Changes since the snapshot

- 2.1.105: `/proactive` alias.
- 2.1.113: `Esc` cancels wakeups; display label.
- 2.1.243: Loops in `/usage`; folded idle wake-ups.
- 2.1.248: self-pacing and default prompt on all providers.
- 2.1.290: wakeup-waiting background sessions left running through updates and low memory.
- 2.1.293: cloud lost-wakeup notice reverted.
- 2.1.295: `Ctrl+C` leaves attached wakeups alone.
- 2.1.299: next-run display.
- Compared with the snapshot: `/loop` defaulted to 10 minutes with cron only; bare prompts now self-pace. Recurring jitter was a fraction capped at 15 minutes; docs now state half the gap capped at 30.

## Open questions

- The version that introduced `ScheduleWakeup`; the changelog does not name it directly. Pending wakeups already existed by 2.1.113.
- The `Sleep` tool in the snapshot is not documented now. Status unknown.
- The durable flag on `CronCreate`, seen in behaviour under rule 35, is not in public schemas.
- The `/proactive` alias's status beyond 2.1.105.
