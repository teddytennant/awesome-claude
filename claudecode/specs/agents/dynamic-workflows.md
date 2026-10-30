# Dynamic Workflows

**Status:** shipped
**Provenance:** post-leak (since v2.1.154, 2026-05-28); a `WORKFLOW_SCRIPTS` build gate and worktree slug pattern existed in the snapshot with the implementation absent
**Sources:** docs `workflows`, `agent-sdk/typescript`, `settings-reference`, `env-vars`, `agent-view`; snapshot `tools.ts`, `tasks/types.ts`, `utils/worktree.ts`; changelog 2.1.154 to 2.1.300

## Purpose

A workflow is a JavaScript script, usually written by the model, that orchestrates many subagents. A runtime executes it in the background. The script holds the plan, loops and intermediate results, so the conversation receives only the final answer. Runs can be watched, paused, resumed, saved and rerun.

## Behaviour

### Availability

1. Workflows MUST be available in the CLI, Desktop, IDE extensions, `-p` and the SDK, on paid plans, API access, Bedrock, Google Cloud's Agent Platform and Foundry.
2. Default: on, except off on Pro, where `enableWorkflows` or the `/config` Dynamic workflows row turns them on.
3. `disableWorkflows: true` or `CLAUDE_CODE_DISABLE_WORKFLOWS=1` MUST disable `/workflows`, workflow commands, `/workflow-authoring`, the keyword, and the Ultracode toggle. A run in progress MUST keep going. `enableWorkflows: true` MUST NOT override the variable.
4. `disableBundledSkills` hides bundled workflows from the model.
5. Code Review and `/ultrareview` still run with `disableWorkflows` on, unless the machine's own administrator set it (2.1.285).

### Starting a run

6. Triggers: the keyword `ultracode` in a typed prompt; a direct request in plain words ("use a workflow"); a saved or bundled workflow command; ultracode mode.
7. The keyword MUST count only for human-typed input: interactive prompt, IDE panel, Remote Control client, or an SDK message with `origin: { kind: "human" }`. It MUST NOT count for `-p` prompts, unstamped SDK prompts, scheduled prompts, or relayed webhooks and PR comments.
8. The keyword is highlighted. `Option+W` or `Alt+W`, or backspace right after it, dismisses it for that prompt. `workflowKeywordTriggerEnabled: false` disables it.
9. The keyword MUST only choose structure. Agents' tool calls get the same permission checks and sandboxing as any other.
10. `/deep-research <question>` is bundled, runs only when invoked (2.1.218), requires WebSearch, cross-checks and votes on claims, and lists claims unverifiable because of errors as unverified rather than refuted.
11. The `Workflow` tool MUST NOT be available to subagents.

### Ultracode mode

12. `/effort ultracode` makes the model plan a workflow for each substantive task, at any effort level (2.1.284). `/effort ultracode off` turns it off. The `/effort` slider has a toggle on `Tab`.
13. `/effort ultracode` lasts for the session; the `ultracode` setting applies to all. `claude --effort ultracode` also sets `xhigh`.
14. While on: no `Large workflow` warning, no concurrent subagent limit for Agent spawns, and no first-launch prompt in auto mode.
15. No managed setting rules out ultracode alone. Disabling workflows does. An effort cap lowers effort but does not disable it.

### Approval

16. The CLI prompt MUST show phases and offer: Yes; Yes and don't ask again for `<name>` in `<path>` (for bundled, saved or plugin workflows only); View raw script; No. `Ctrl+G` opens the script. `Tab` adds a comment.

| Mode | Prompted |
| --- | --- |
| Auto | First launch only; any Yes records consent in user settings |
| Manual, acceptEdits | Every run unless remembered |
| Bypass | Never |
| `-p`, SDK | Never shown; normal permission evaluation |

17. In `-p` and SDK the launch needs a `Workflow` or `Workflow(<name>)` allow rule, auto mode classifier approval, bypass mode, a `PreToolUse` hook returning allow, or the host's permission tool or `canUseTool`. In plan mode a hook's approval alone MUST NOT start the run.
18. Desktop shows an approval card with name, phases and a usage caution, with Once, Always and Deny.
19. Agents use the session's permission rules and the subagent mode inheritance rules.
20. A script file MUST be readable by the session to run from its path.

### Script format

21. The file begins with `export const meta = {...}`, the first statement and a plain object literal with `name` and `description`, and optional `phases`. Non-literal content MUST drop `/<name>` from autocomplete.
22. Body: plain JavaScript with top-level `await`.

| API | Behaviour |
| --- | --- |
| `agent(prompt, opts)` | Spawn one agent. Options seen in public docs: `schema`, `label`, `stallMs`; a model per stage may be named |
| `pipeline(items, fn)` | One per item |
| `parallel(tasks)` | Concurrent, waits for all |
| `phase(title)` | Groups later agents in the view |
| `log(msg)` | Message above phases |
| `args` | Global input, `undefined` if omitted |

23. `agent()` MUST resolve to `null` if stopped mid-run or on an unrecoverable API error. `pipeline()` keeps `null` entries.
24. `Date.now()`, `Math.random()` and no-argument `new Date()` MUST throw, so relaunch is deterministic.
25. `import()` MUST fail before the run starts. Scripts have no filesystem or shell access. A script's hand-back nesting past 28,000 levels MUST be refused (2.1.299).
26. A `schema` MUST be checked first. A provably contradictory schema fails with an error naming the contradiction, and the agent never starts (2.1.260). Output failing validation MUST retry up to `MAX_STRUCTURED_OUTPUT_RETRIES`, default five, then fail with the last validation failure.
27. In auto mode a computed `agent()` prompt MUST NOT count as a user request; it is marked as script-computed text (2.1.277).

### Runtime

28. The script executes in an isolated environment. The run's script is written under the session's directory in `~/.claude/projects/` unless started from a path, and the model receives the path.
29. Each agent's result MUST be tracked for resumption.
30. The only pauses: agent permission prompts and usage-limit waits. No mid-run user input.

| Limit | Value |
| --- | --- |
| Concurrent agents | 16 by default, fewer with fewer CPUs, including in CPU-limited containers; `CLAUDE_CODE_WORKFLOW_MAX_CONCURRENT_AGENTS` 1 to 256 |
| Items per `parallel()` or `pipeline()` | 4,096; longer MUST reject with an error |
| Agents per run | 1,000 |

### Cache staggering

31. Agents with the same model, effort, type, tools, schema and working directory share a prefix. In a fan-out, all but the first MUST be held until the first response begins, capped by `CLAUDE_CODE_WORKFLOW_PREFIX_STAGGER_MS` (5000; `0` disables).
32. Workflow agent cache defaults to five minutes, including on subscription; `subagentPromptCacheTtl: "1h"` extends it.

### Model selection

33. Order is as for subagents. A script-named model counts as the per-invocation value. `CLAUDE_CODE_WORKFLOW_SUBAGENT_MODEL` runs all workflow agents on one model (2.1.296). `CLAUDE_CODE_SUBAGENT_MODEL_FORCE` also applies. Blocked models warn (2.1.223).
34. Mod `agent.spawn` hooks can refuse workflow agents (2.1.292), or rewrite `prompt` and `model` (2.1.300).

### Observing and control

35. `/workflows` lists runs; a single run opens directly. A task-panel line shows name, progress bar, agent count on wide terminals, elapsed time, tokens and warnings (2.1.281).
36. Keys: `↑`/`↓` select; `Enter` or `→` drill in; `Esc` or `←` back; `j`/`k` scroll; `f` filter by status; `p` pause or resume; `x` stop agent or run; `r` restart a running agent; `s` save. In the list, `x` stops the run under the pointer.
37. Agent detail shows the prompt, recent tool calls with state, task list if any, and result. `Enter` expands.
38. A stopped run stays in the panel while agent processes live. Stopping again re-signals them.
39. `/workflows` MUST open immediately during a turn (2.1.169).

### Resume

40. `p` resumes paused runs. A stopped run needs a relaunch with `resumeFromRunId`, refused until prior agents have exited.
41. Replay runs in agent start order. Completed agents return saved results. The first agent whose prompt differs runs again, and so does every agent after it. Agents running at stop start over. A failed agent runs again, with all agents after it, even completed ones. Stopping one agent counts as a failure; stopping the run does not.
42. Resume is same-session only. Leaving a session stops progress. On backgrounding the run needs relaunching, through the Workflow tool's approval (2.1.300), and may show `could not be resumed`. After `Exit and stop tasks`, resume the session with `--resume`, then relaunch.
43. Cloud sessions save results with history, surviving VM reclaim.
44. Missing saved results MUST fail with `nothing to resume`, not silently restart. A path-started run outside `~/.claude/projects/` cannot be relaunched in a background session.

### Usage limits and stalls

45. On a claude.ai usage limit, affected agents wait, no new ones start, and the run continues shortly after reset (2.1.271). This requires an interactive subscription session (not `-p`, SDK, background, Remote Control or teammate), `autoContinueAtUsageLimit` on, reset within 24 hours, and fewer than two earlier waits. Otherwise the agent fails.
46. An agent silent past its stall window MUST restart from the same prompt, shown as `(retry 1)` and `attempt 2 (stalled)`, without the prior transcript. Changed files and spent tokens remain. Tool and usage-limit waits do not count.
47. At most five restarts, including `r`. Failures read `agent stalled on all 6 attempts`, `agent lost its reply on all 6 attempts`, or `agent abandoned after 6 attempts`.
48. Inside `parallel()` or `pipeline()` the run continues with `null`. A directly awaited failure ends the run.
49. `stallMs` sets one agent's window. `CLAUDE_ASYNC_AGENT_STALL_TIMEOUT_MS` sets all, for workflows since 2.1.286.

### Saving and distribution

50. `s` saves to `.claude/workflows/` or `~/.claude/workflows/`, chosen with `Tab`. The file runs as `/<name>`.
51. Saves MUST refuse symlinks: for the project, `.claude`, `.claude/workflows` or the target; for personal, only the target.
52. Project saves go to the closest existing `.claude/workflows/`, or the repository root. All along the path load, and the closest wins. Project beats personal.
53. Plugins ship scripts in `workflows/` or via the `workflows` manifest field, as `/<plugin>:<meta.name>`.
54. `/reload-skills` re-reads workflow directories. `/workflow-authoring` loads the writing reference (2.1.248).
55. Names in the `anthropic-skills` namespace MUST NOT load (2.1.282).

### Cost signals

56. A run over 25 agents or a projected 1.5 million tokens shows a `Large workflow` warning. It is advisory. A chosen size guideline's agent count replaces 25.
57. Size guideline is advice to the model: `unrestricted`, `small` (under 5), `medium` (under 10), `large` (under 50). Default is `medium`, `small` on Pro (2.1.271). Set through `/config` or `workflowSizeGuideline`, where a settings file hides the row.

## Configuration & interfaces

### `Workflow` tool input

| Field | Notes |
| --- | --- |
| `script` | Inline script |
| `name` | Built-in or saved |
| `scriptPath` | Takes precedence; rejected when `Read` is absent |
| `args` | JSON value exposed as `args` |
| `resumeFromRunId` | Same session only |
| `title`, `description` | Ignored |

At least one of `script`, `name` or `scriptPath` is required.

### Settings and variables

`enableWorkflows`, `disableWorkflows`, `workflowKeywordTriggerEnabled`, `workflowSizeGuideline`, `ultracode`, `subagentPromptCacheTtl`, `autoContinueAtUsageLimit`. `CLAUDE_CODE_DISABLE_WORKFLOWS`, `CLAUDE_CODE_WORKFLOW_MAX_CONCURRENT_AGENTS`, `CLAUDE_CODE_WORKFLOW_PREFIX_STAGGER_MS`, `CLAUDE_CODE_WORKFLOW_SUBAGENT_MODEL`, `CLAUDE_ASYNC_AGENT_STALL_TIMEOUT_MS`, `MAX_STRUCTURED_OUTPUT_RETRIES`.

### Telemetry and hooks

Spawned agents carry OpenTelemetry attributes `workflow.run_id` and `workflow.name` (2.1.202). Workflow agents in their own worktree trigger `WorktreeCreate`.

## Failure modes & edge cases

- Editing or reordering a script reruns everything from the first changed start.
- Rerun of a middle failure repeats completed later agents.
- A syntax error in the body reports at run time.
- `pipeline()` multi-agent items could rerun completed work before 2.1.305.
- Disabled tools: `scriptPath` refusal says to pass `script` inline (2.1.295).

## Changes since the snapshot

- 2.1.154: introduced, with `/workflows`.
- 2.1.157: keyword setting. 2.1.160: keyword renamed to `ultracode`. 2.1.178: explicit phrases only and closest-wins directories.
- 2.1.202: size setting, OTel attributes. 2.1.219: `workflowSizeGuideline`. 2.1.229: staggering.
- 2.1.248: tool description shrunk; script reference moved to `workflow-authoring`.
- 2.1.260: schema checks. 2.1.269: concurrency variable.
- 2.1.271: usage-limit pause, Pro small default, medium lowered to 10.
- 2.1.277: script-authored prompt framing. 2.1.284: ultracode a toggle independent of effort.
- 2.1.296: dedicated model variable. 2.1.300: mod rewrites.

## Open questions

- Complete `agent()` options beyond those in public docs, including isolation and agent type.
- Run ID and on-disk layout of saved results.
- Whether the 2.1.296 `CLAUDE_CODE_WORKFLOW_SUBAGENT_MODEL` remains current; it is absent from the env-vars reference.
- The stall restart's interaction with worktree-isolated agents.
