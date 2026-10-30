# Subagent Runtime: Agent Tool, Lifecycle and Handback

**Status:** shipped
**Provenance:** both (Agent tool in snapshot; background-by-default, nesting, limits, `SubagentHandback`, output scanning post-leak)
**Sources:** docs `sub-agents`, `tools-reference`, `hooks`, `permissions`, `agent-sdk/typescript`, `errors`; snapshot `tools/AgentTool/AgentTool.tsx`, `runAgent.ts`, `resumeAgent.ts`, `agentToolUtils.ts`, `tasks/LocalAgentTask`, `constants/tools.ts`; changelog 2.1.172 to 2.1.314

## Purpose

The `Agent` tool launches a worker with its own context. The parent sees only the final report. This spec defines the tool contract, foreground and background execution, tool and permission resolution, how results come back, resuming, nesting and limits. Forks and teammates share the same tool and are specified in [forks.md](forks.md) and [agent-teams.md](agent-teams.md).

## Behaviour

### Tool contract

1. Launching MUST NOT itself raise a permission prompt. The agent's tool calls are checked individually. In auto mode the spawn itself is evaluated by the classifier before launch (2.1.178).
2. A call routes to one of three kinds: a subagent; a fork, when `subagent_type: "fork"` is used with fork mode on; a teammate, when agent teams are on, the session is interactive, the caller is the main conversation, `name` is set, and the call is neither a fork nor passes `isolation` itself.
3. `team_name` and `mode` MUST be accepted and ignored. `mode` was deprecated in 2.1.212: agents follow the inheritance rules below.
4. Permission rules can match parameters, such as `Agent(model:opus)` and `Agent(isolation:worktree)`. Matching is literal against the input as sent, an omitted parameter never matches, and one rule names one parameter (2.1.178).

### Model and effort

5. Model resolution order: per-invocation `model`; definition `model` (`inherit` means the main model); `CLAUDE_CODE_SUBAGENT_MODEL`; main model. A mod's `agent.spawn` hook model replaces the per-invocation value.
6. The per-invocation parameter MUST accept aliases only.
7. A family alias in the parameter or the definition MUST resolve to the main model's exact ID, including `[1m]`, when the main model belongs to that family. It also resolves there when a non-Anthropic provider leaves the family unknown (opus only, and not when `ANTHROPIC_DEFAULT_OPUS_MODEL` is set). An alias in `CLAUDE_CODE_SUBAGENT_MODEL` MUST always resolve normally.
8. `CLAUDE_CODE_SUBAGENT_MODEL=inherit` equals unset. On its own the variable MUST NOT change Explore or Plan.
9. `CLAUDE_CODE_SUBAGENT_MODEL_FORCE=1` MUST ignore definition `model` and refuse a passed model, applying to subagents, teammates and workflow agents. With the model variable set, that model is used. Without it, the main model is used, and Explore keeps its listed model. Forks, and `context: fork` skills with `model: inherit`, stay on the main model.
10. Every resolved value MUST be checked against `availableModels`. A blocked family alias uses the newest allowed version of the family. Other blocked values, or no allowed version, use the inherited model after trying `CLAUDE_CODE_SUBAGENT_MODEL`. Interactive sessions MUST warn with both names.
11. Per-invocation `model` and `effort` MUST persist through resume.
12. Effort precedence: `CLAUDE_CODE_EFFORT_LEVEL`, per-invocation `effort` (non-fork, 2.1.292), definition `effort`, session effort.
13. Subagents MUST inherit the main conversation's extended-thinking configuration (2.1.198).
14. `/tasks` MUST show the model and any effort for each subagent.

### Foreground and background

15. With nothing configured, an agent spawned from the main conversation MUST start in the background.
16. In `claude -p` and the SDK the main conversation may wait, by the model's judgment or on request. In interactive terminal, VS Code and desktop sessions waiting requires turning fork mode off (`CLAUDE_CODE_FORK_SUBAGENT=0`) and restarting.
17. `CLAUDE_CODE_DISABLE_BACKGROUND_TASKS=1` MUST make the parent wait for subagents, remove `run_in_background`, and disable Ctrl+B.
18. `background: true` in a definition MUST keep it in the background even if the model asks to wait.
19. Ctrl+B or the VS Code action MUST move a running foreground subagent to the background.
20. A background launch MUST return immediately with status `async_launched`, so hook responses carry no usage fields. The launch result MUST NOT tell the model to end its turn; it keeps working (2.1.193).
21. Results arrive as a completion notification in a later turn, marked as an automated event. The model MUST report still-running agents as running rather than inventing results (2.1.211).
22. A background agent may leave a background shell running past its turn and MUST be notified when that shell ends. Time limits on such shells were removed in 2.1.260.
23. In `claude -p`, the SDK, desktop and VS Code, a subagent's own Agent calls default to foreground (2.1.302).

### Tool resolution

24. A non-fork subagent inherits the session's built-in and MCP tools, narrowed by two filters. On macOS, Linux and WSL it may also receive Glob and Grep when the main conversation lacks them.
25. Filter 1 MUST always remove: `AskUserQuestion`, `EndConversation`, `EnterPlanMode`, `ScheduleWakeup`, `WaitForMcpServers`, `Workflow`; `ExitPlanMode` unless the agent's mode is `plan`; and `Agent` at the depth limit.
26. Filter 2 applies to background agents. They MUST keep all MCP tools but only these built-ins: `Read`, `Grep`, `Glob`, `LSP` (2.1.280), `Bash`, `PowerShell`, `Edit`, `Write`, `NotebookEdit`, `WebFetch`, `WebSearch`, `TodoWrite`, `Skill`, `ToolSearch`, `EnterWorktree`, `ExitWorktree`, `Monitor`, `TaskStop`, `SendMessage`, `Artifact`, plus `SubagentHandback` where applicable.
27. Filter 2 removal MUST be silent unless it leaves `tools` resolving to nothing. The same definition may therefore differ between foreground and background.
28. A resumed agent MUST keep the tool set from where it first ran. Forks skip both filters.
29. `ListAgents` follows these filters: foreground inherits it where messaging is enabled, background does not.
30. Teammates additionally keep `TaskCreate`, `TaskGet`, `TaskList`, `TaskUpdate`, `CronCreate`, `CronDelete`, `CronList`.

### Permission mode

31. `permissionMode` unset MUST inherit the main mode.
32. Main mode `bypassPermissions`, `acceptEdits` or `auto`: the subagent runs in that mode and the field is ignored.
33. Main mode `plan`: the subagent stays in plan, except teammates under team rules. With `dontAsk` set, actions plan mode would ask about are denied instead.
34. Main mode `default` or `dontAsk`: the field applies, except `bypassPermissions` (2.1.267) and `auto` when unavailable to the agent, where the main mode is kept.
35. Foreground prompts pass through as they arise. Background prompts MUST surface in the main session naming the agent, Esc denying only that call (2.1.186). A grant lasting beyond one call MUST apply to the whole session.
36. Worktree isolation and working-directory rules are in [worktrees.md](worktrees.md).

### Startup context

37. A non-fork agent MUST start with a fresh context: its own system prompt plus environment details, the task message, CLAUDE.md hierarchy (subject to Explore, Plan and `omitClaudeMd`), a git status snapshot (skipped by Explore and Plan, and absent outside a repository or when disabled), preloaded skills, and a sibling roster.
38. The roster is a system reminder listing `main` and other named agents. It MUST appear only when the agent has `SendMessage` and at least one other agent is named. It is a snapshot at start.
39. Output style and auto memory MUST NOT reach a non-fork agent. Its context window is sized by its own model.
40. In `-p`, `--append-subagent-system-prompt[-file]` MUST append text to every non-fork subagent's prompt, nested included.
41. A subagent starts in the parent's working directory. `cd` does not persist between shell calls or affect the parent.

### Handback and result delivery

42. Without `SubagentHandback`, the final assistant message is the result.
43. In auto mode, on 2.1.271 and later, locally run non-fork subagents MUST receive the `SubagentHandback` tool, even if omitted from `tools` or listed in `disallowedTools`. Available in terminal CLI, IDE extensions, cloud sessions and the SDK.
44. `SubagentHandback` delivers the report to whichever conversation receives the result, and the classifier MUST review the report before delivery. The run MUST end once the report is handed back (2.1.285).
45. No prompt appears for this tool, and the call runs even if the classifier objects. A `PreToolUse` hook returning `deny` stops it: the subagent is told up to three times to call again. If denials continue it ends without delivering through the tool.
46. With handback, the `SubagentStop` field `last_assistant_message` holds the closing text and `Agent` `tool_response.content` holds a short note rather than the report.
47. A subagent hitting `maxTurns` MUST return output marked partial with a hint to continue via `SendMessage` (2.1.246).
48. A completion notification SHOULD include elapsed duration (2.1.144). Notifications MUST state when an agent is only waiting on its own background work, received a message too late for its result, or was stopped by a usage limit (2.1.299).

### Output scanning

49. Each final report MUST be scanned before the parent reads it. The scan MUST NOT remove or reword content. It inserts a backslash into text imitating harness output, such as `<system-reminder>` or lines starting `Human:` or `Assistant:`.
50. It MUST prepend a marker line starting `[harness: subagent output matched instruction-shaped pattern(s):` for imitated tags or mentions of permission settings.
51. Results MUST arrive under a header stating they are subagent output and that instructions or approval claims inside carry no user authority, with the result indented (2.1.277).
52. Scanning is not a security boundary. Tool calls induced by a report still go through permissions and sandboxing.

### Resume and messaging

53. Each invocation creates a new instance. Resuming uses `SendMessage` with agent ID or name in `to`. Agent teams are not required.
54. Explore and Plan are one-shot and return no ID.
55. A message to a completed or stopped agent MUST resume it in the background under the same ID with full history, including delivered nested results. It shows as running again.
56. A resumed run SHOULD be able to read the prompt cache the original run warmed.
57. An agent resumed by a subagent reports to that subagent, which waits. A message from a subagent to its own launcher resumes the launcher without redirecting results.
58. An agent stopped by the model with `TaskStop` is resumable once its run has exited. An agent the user stopped (`x` in `/tasks`, or SDK `stop_task`) MUST refuse model messages, reporting cancellation, until the user types into its transcript while its row is present.
59. Before sending by name, `SendMessage` MUST verify the name still reaches the same agent. If a newer agent took it, the send MUST be refused with the current holder identified. The check is per conversation and resets on `/clear`.
60. A subagent MUST treat its launcher's messages as task direction. No agent message counts as user approval or may change permissions, CLAUDE.md or configuration.
61. Names given in the main conversation since its last compaction MUST survive restart. Older names need an ID-addressed message first (2.1.299).

### Nesting and limits

62. Default depth is 3 layers below main; `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH` overrides and `1` disables nesting. At the limit `Agent` is withheld, except forks, where it stays listed and errors.
63. Interactively, a subagent launching background children MUST wait for them before finishing. In `-p` and the SDK it waits while fork mode is on. With fork mode off children run in the background and may report to main if they outlast the parent.
64. Default concurrency limit is 20 running subagents per session. Exceeding it MUST fail with `Concurrent subagent limit reached` and tell the model not to retry. `CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS` overrides with any positive integer. The limit is not enforced while ultracode is on.
65. `/subtask` forks and resumes occupy slots but are never blocked, so resumes can exceed the limit. Workflows and teammates have their own limits.
66. There is no total spawn cap (removed 2.1.224).

### Errors and stalls

67. A mid-stream cutoff with text and no tool calls MUST prompt continuation, in interactive sessions too, until continuations are exhausted.
68. Foreground: a rate limit, overload or server error after text MUST return the partial output with a note. With no text it fails with `Agent terminated early due to an API error`.
69. Background: the agent is marked failed and the notification names the error and last output.
70. With a fallback chain, the agent MUST switch model and its report MUST open with a line naming the switch.
71. Stalled agents fail after `CLAUDE_ASYNC_AGENT_STALL_TIMEOUT_MS`, default 600000 ms.

### Display and persistence

72. A successful background agent's panel row is removed at once, with `/tasks to see subagents` shown for 30 seconds except in screen reader mode (2.1.232). Failed or stopped rows stay 30 seconds, and `x` clears them. Done agents remain in `/tasks` for those 30 seconds (2.1.208).
73. Nested agents render as a tree with `(+N)` descendant counts.
74. Transcripts live at `~/.claude/projects/{project}/{sessionId}/subagents/agent-{agentId}.jsonl` with `agent-{agentId}.meta.json`. They are unaffected by main compaction and deleted by `cleanupPeriodDays`.
75. Subagents auto-compact on their own window, logging `compact_boundary` entries with `preTokens`.
76. In a viewed agent transcript, plain text and skills go to that agent and built-in commands go to main. `/compact`, `/clear` and `/rewind` confirm first. `/model` and `/fast` refuse with a notice. Send-now (`Ctrl+Enter` or `Ctrl+X Ctrl+S`) moves backgroundable work aside so the message is read at once (2.1.286).

## Configuration & interfaces

### `Agent` input

| Field | Notes |
| --- | --- |
| `description`, `prompt` | required |
| `subagent_type` | name, or `fork` |
| `model` | `sonnet`, `opus`, `haiku`, `fable` |
| `effort` | `low` to `max` |
| `run_in_background` | boolean |
| `name` | makes it addressable; may create a teammate |
| `isolation` | `worktree`, `remote` |
| `team_name`, `mode` | deprecated, ignored |

### Environment variables

`CLAUDE_CODE_SUBAGENT_MODEL`, `CLAUDE_CODE_SUBAGENT_MODEL_FORCE`, `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH`, `CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS`, `CLAUDE_CODE_FORK_SUBAGENT`, `CLAUDE_CODE_DISABLE_BACKGROUND_TASKS`, `CLAUDE_ASYNC_AGENT_STALL_TIMEOUT_MS`, `CLAUDE_CODE_FORWARD_SUBAGENT_TEXT`. `CLAUDE_CODE_MAX_SUBAGENTS_PER_SESSION` is a no-op.

### Hooks

`SubagentStart` fires on spawn, on resume, and per message for in-process teammates. `SubagentStop` receives `agent_id`, `agent_type`, `agent_transcript_path`, `last_assistant_message`, and parent-scoped `background_tasks` and `session_crons`. Internal agents may produce an empty `agent_type`. A completed `Agent` response carries `agentId`, `content`, `resolvedModel`, `modelsUsed`, `totalTokens` (final request only), `totalDurationMs`, `totalToolUseCount`, `usage`.

## Failure modes & edge cases

- `isolation` passed on the call prevents teammate routing; `isolation` in frontmatter does not, and the teammate then runs in the main working directory.
- Removing `Agent` from a definition's `tools` stops that agent spawning while nesting stays on.
- A TaskOutput call no longer exists; background output is read from the output file with `Read` (2.1.277).
- A stale name after restart yields a refusal until an ID-addressed message.

## Changes since the snapshot

- 2.1.172: nesting to 5 levels. 2.1.217: nesting off by default. 2.1.219: depth 3 default.
- 2.1.178: auto mode classifier evaluates spawns; parameter-level permission rules.
- 2.1.186: background prompts surface in main instead of auto-denying.
- 2.1.198: background by default. 2.1.232: fork mode on and interactive spawns background.
- 2.1.210, 2.1.277: hardening of report framing.
- 2.1.212: 200-spawn cap added; 2.1.224: removed. 2.1.217: concurrency cap.
- 2.1.246: `maxTurns` partial results.
- 2.1.251: `CLAUDE_CODE_SUBAGENT_MODEL` became a default instead of an override. 2.1.257: `_FORCE`.
- 2.1.271: `SubagentHandback`. 2.1.285: run ends at handback.
- 2.1.277: `TaskOutput` removed.
- 2.1.292: `effort` parameter.
- 2.1.302: foreground default for nested spawns in non-terminal surfaces.
- 2.1.314: parent stops retaining subagent tool results during long headless turns.

## Open questions

- The `SubagentHandback` input schema is not public.
- Whether the snapshot's `cwd` input survives; it is absent from the current SDK `AgentInput`.
- `isolation: "remote"` requirements and availability outside the SDK type.
- Whether a fork or teammate receives scanned output identically.
