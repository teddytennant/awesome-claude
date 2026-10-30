# /goal

**Status:** shipped
**Provenance:** post-leak (since v2.1.139, 2026-05-11)
**Sources:** docs `goal`, `hooks-guide`, `env-vars`; changelog 2.1.139, 2.1.172, 2.1.234, 2.1.236, 2.1.239, 2.1.246, 2.1.269

## Purpose

`/goal <condition>` keeps a session working across turns until a separate small model judges a completion condition met or impossible, or an error requires the user. It removes per-turn prompting in the same way auto mode removes per-tool prompting. It is session-scoped, built on a prompt-based Stop hook, and independent of the permission mode.

## Behaviour

### Commands

1. `/goal <condition>` MUST set the goal and start a turn immediately, with the condition as directive. One goal per session; a new one replaces the old.
2. The condition has a 4,000-character limit.
3. `/goal` with no argument MUST show the condition, elapsed time, evaluated turns, token spend and latest reason. Turn count and reason appear after the first evaluation. If no goal is active but one was achieved, it shows that condition with duration, turns and spend.
4. `/goal clear`, or `stop`, `off`, `reset`, `none`, `cancel`, MUST clear it, printing `Goal cleared:` and the condition, or `No goal set`.
5. `/clear` MUST also remove an active goal.
6. While active, a `◎ /goal active` indicator shows duration. Each verdict appears in the transcript, with the reason at Ctrl+O.

### Evaluation

7. After each turn the condition and the conversation so far go to the configured small fast model, on the session's provider.
8. The evaluator MUST NOT call tools. It judges only what the conversation shows.
9. Verdicts, each with a reason:
   - Not yet met: continue, using the reason as guidance.
   - Met: clear, recording an achieved entry.
   - Impossible: clear, recording a failed entry with the reason.
10. If the model keeps replying without progress (no tool use for several consecutive turns), the loop MUST stop with a warning and return control, goal still set. Evaluation resumes after the next prompt.
11. Turn or time bounds are not built in. A clause such as `or stop after 20 turns` is judged from the conversation, with the model reporting progress against it.
12. `ANTHROPIC_DEFAULT_HAIKU_MODEL` selects the evaluator model and affects every other small-fast-model use.

### Failures

13. A goal MUST clear, with a warning starting `Goal cleared after an unrecoverable error` and ending `Run /goal again to continue`, on: an authentication failure where Claude Code manages credentials; an exhausted credit balance; a context overflow auto-compaction could not clear; an unavailable model.
14. Where a host manages credentials (desktop, cloud), an authentication failure MUST leave the goal active.
15. After other errors the goal stays. In interactive sessions on 2.1.269 or later:
    - Transient failures (overload, dropped connection): a notice starting `Goal still active` shows the wait, and after three automatic retries the goal pauses.
    - Failures a retry would repeat (API rate limit, usage limit, hook-ended turn): a notice starting `Goal paused` names the cause. If the session is waiting on a usage-limit reset, work resumes then.
16. A user message MUST start the next turn at any time.

### Background work

17. If a subagent or background shell is running when a turn ends, that turn's evaluation MUST be skipped until a turn ends with none running. Results arrive as a new turn with no user prompt needed.
18. After background work has held the goal for the check-in interval (30 minutes), a check-in is due: Claude Code lists running tasks and asks the model to read output, keep waiting if progressing, and fix or stop stuck ones.
19. Intervals back off: first at N, then 2N, then 4N repeating. By default 30 minutes, 1 hour, then every 2 hours.
20. Delivery: at the next turn end with work still running; and, in interactive sessions only, by starting an idle turn. If the work stopped with no result, the model is told to continue.
21. At most three idle check-ins per goal between user prompts. The third MUST say they are paused until the next prompt.

### Resume and non-interactive

22. Every resume route MUST restore a goal still active at session end: `--continue`, `--resume` by ID, name or path, and the picker (picker since 2.1.239). The condition carries; turn count, timer and token baseline reset.
23. Achieved or cleared goals MUST NOT be restored.
24. `claude -p "/goal ..."` MUST run the loop to completion in one invocation, printing only the final response in text mode. `--output-format stream-json --verbose` emits messages as they happen. Ctrl+C stops it.
25. `/goal` MUST work in desktop and Remote Control.

### Availability

26. `/goal` follows the workspace trust rule for settings hooks, and is unavailable under `disableAllHooks` (after precedence) or managed `allowManagedHooksOnly`. The command MUST say why.

## Configuration & interfaces

| Item | Detail |
| --- | --- |
| `CLAUDE_CODE_GOAL_CHECKIN_MINUTES` | First interval, default 30. Whole minutes up to 10080. Other values mean default. `0` disables check-ins and automatic retries |
| `ANTHROPIC_DEFAULT_HAIKU_MODEL` | Evaluator model |

Comparison with neighbours: `/loop` starts turns on time; a Stop hook is persistent, can be deterministic, and applies across sessions; `/goal` is session-scoped and model-evaluated.

## Failure modes & edge cases

- A condition Claude's output cannot demonstrate can never verify.
- Default `-p` text output looks stalled during long loops.
- In Manual mode, tool prompts still stop a goal turn.
- Evaluation tokens bill on the small fast model.

## Changes since the snapshot

- 2.1.139: introduced, in interactive, `-p` and Remote Control.
- 2.1.172: status chip stopped re-rendering at 5 Hz.
- 2.1.234: unrecoverable errors clear the goal; turn-end check-ins.
- 2.1.236: idle check-ins. 2.1.239: backoff at turn ends; picker resume. 2.1.246: idle cap of three.
- 2.1.269: automatic retry and pause notices.

## Open questions

- The exact count of no-progress turns before the loop stops. The hooks guide has a block cap; see that spec.
- Retry wait durations.
- Whether `/goal` runs within a subagent or teammate.
