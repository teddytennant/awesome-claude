# Built-in Tool Catalogue

**Status:** shipped
**Provenance:** both
**Sources:** docs `tools-reference`, `agent-sdk/typescript` (Tool Input/Output Types), `permissions`, `sub-agents`; snapshot `tools.ts`, `tools/`, `constants/tools.ts`; `comparison/tools.md`; changelog 2.1.98 to 2.1.277

## Purpose

Single index of every tool named in the `tools-reference` table as of 2.1.314, with its permission requirement and its standing in the 2026-03-31 snapshot. Tool names are the exact strings used in permission rules, subagent tool lists, hook matchers and `--allowedTools`/`--disallowedTools`. Per-tool behaviour lives in the family specs linked below.

## Behaviour

### Reading the table

1. "Permission" is the documented `Permission required` value: whether the tool prompts in Manual mode for paths inside the working directory. It MUST NOT be read as a complete policy:
   - File-access tools marked No (`Read`, `Grep`, `Glob`) still prompt for paths outside the working directories.
   - `Bash` is Yes but a built-in read-only command set runs without a prompt.
   - In auto mode a classifier decides most prompts instead of the user.
2. A tool in the table is not necessarily in a given session. The tool set depends on provider, platform, model, plan, settings and surface. The SDK's `BUILTIN_TOOL_NAMES` list has the same caveat; the session's real list is the `tools` array of the init system message, which reports `Agent` as `Task` for compatibility.
3. "Snapshot" column values:
   - **source**: a `tools/<Name>Tool/` directory exists in the snapshot.
   - **gated ref**: the snapshot registry references the module behind a build gate, but no source directory is present. The feature was planned or internal at that date.
   - **no**: no trace of the name in the snapshot.

### Catalogue (46 rows)

| Tool | Permission | Snapshot | Spec | Availability notes |
| :- | :- | :- | :- | :- |
| `Agent` | No | source (alias `Task`) | agents area | Launch itself never prompts; a subagent's own calls are checked. A call with `name` can start a teammate; fork mode can start a fork |
| `Artifact` | Yes | no | [post-leak-artifact](post-leak-artifact.md) | claude.ai sign-in, paid plan, Anthropic API; off in SDK and `-p` |
| `AskUserQuestion` | No | source | [interaction-and-planning](interaction-and-planning.md) | Never in subagents |
| `Bash` | Yes | source | [shell-bash-powershell](shell-bash-powershell.md) | Removing it restores Glob/Grep |
| `CronCreate` | No | source (gated `AGENT_TRIGGERS`) | [scheduling-tools](scheduling-tools.md) | Off with `CLAUDE_CODE_DISABLE_CRON=1` |
| `CronDelete` | No | source (same gate) | [scheduling-tools](scheduling-tools.md) | As above |
| `CronList` | No | source (same gate) | [scheduling-tools](scheduling-tools.md) | As above |
| `Edit` | Yes | source | [file-tools](file-tools.md) | |
| `EndConversation` | No | no | [end-conversation-and-send-feedback](end-conversation-and-send-feedback.md) | Interactive terminal, recent models, first-party provider only |
| `EnterPlanMode` | No | source | [interaction-and-planning](interaction-and-planning.md) | Never in subagents |
| `EnterWorktree` | Yes | source | [worktree-tools](worktree-tools.md) | In practice prompts only for a `path` outside `.claude/worktrees/` |
| `ExitPlanMode` | Yes | source | [interaction-and-planning](interaction-and-planning.md) | Subagents only with `permissionMode: plan` |
| `ExitWorktree` | No | source | [worktree-tools](worktree-tools.md) | Not for subagents pinned to their own directory |
| `Glob` | No | source | [search-tools](search-tools.md) | Default on Windows only; conditional elsewhere |
| `Grep` | No | source | [search-tools](search-tools.md) | Default on Windows only; conditional elsewhere |
| `ListAgents` | No | no (see note a) | [agent-coordination-tools](agent-coordination-tools.md) | v2.1.224+, where cross-session messaging is enabled |
| `ListMcpResourcesTool` | No | source | MCP area | Omits MCP Apps UI resources |
| `LSP` | No | source (env-gated `ENABLE_LSP_TOOL`) | [lsp-code-intelligence](lsp-code-intelligence.md) | Inactive until a code intelligence plugin is installed; inactive in cloud |
| `Monitor` | Yes | gated ref (`MONITOR_TOOL`) | [shell-background-and-monitor](shell-background-and-monitor.md) | Windows needs Git Bash; third-party providers and telemetry-off need v2.1.310+ |
| `NotebookEdit` | Yes | source | [file-tools](file-tools.md) | |
| `PowerShell` | Yes | source (conditional registry entry) | [shell-bash-powershell](shell-bash-powershell.md) | Opt-in on Linux, macOS, WSL; defaults vary on Windows |
| `PushNotification` | No | gated ref (`KAIROS`, `KAIROS_PUSH_NOTIFICATION`) | [delivery-and-reporting-tools](delivery-and-reporting-tools.md) | Not on Bedrock, Claude Platform on AWS, Agent Platform, Foundry |
| `Read` | No | source | [file-tools](file-tools.md) | |
| `ReadMcpResourceTool` | No | source | MCP area | |
| `RemoteTrigger` | No | source (gated `AGENT_TRIGGERS_REMOTE`) | [scheduling-tools](scheduling-tools.md) | Needs claude.ai plan with scheduled tasks; org policy can remove it |
| `ReportFindings` | No | no | [delivery-and-reporting-tools](delivery-and-reporting-tools.md) | v2.1.196+; called when active code-review instructions say so |
| `ScheduleWakeup` | No | no (see note b) | [scheduling-tools](scheduling-tools.md) | Self-paced `/loop` only; never in subagents |
| `SendFeedback` | No | no | [end-conversation-and-send-feedback](end-conversation-and-send-feedback.md) | Interactive, first-party, local only |
| `SendMessage` | No | source | agents area | Cross-session targets v2.1.224+ |
| `SendUserFile` | No | gated ref (`KAIROS`) | [delivery-and-reporting-tools](delivery-and-reporting-tools.md) | Remote Control client connected, or cloud session |
| `ShareOnboardingGuide` | Yes | no | [delivery-and-reporting-tools](delivery-and-reporting-tools.md) | Team/Enterprise claude.ai subscribers; called from `/team-onboarding` |
| `Skill` | Yes | source | skills area | |
| `SubagentHandback` | No | no | [agent-coordination-tools](agent-coordination-tools.md) | Auto mode, local non-fork subagents, v2.1.271+ |
| `TaskCreate` | No | source | [interaction-and-planning](interaction-and-planning.md) | Default only on older models |
| `TaskGet` | No | source | [interaction-and-planning](interaction-and-planning.md) | As above |
| `TaskList` | No | source | [interaction-and-planning](interaction-and-planning.md) | As above |
| `TaskOutput` | No | source | [snapshot-tool-fates](snapshot-tool-fates.md) | **Removed in v2.1.277**; row kept in docs |
| `TaskStop` | No | source | [shell-background-and-monitor](shell-background-and-monitor.md) | |
| `TaskUpdate` | No | source | [interaction-and-planning](interaction-and-planning.md) | Default only on older models |
| `TodoWrite` | No | source | [interaction-and-planning](interaction-and-planning.md) | Only with `CLAUDE_CODE_ENABLE_TASKS=0` in sessions that have task tools |
| `ToolSearch` | No | source | [search-tools](search-tools.md) | Requires tool search enabled |
| `WaitForMcpServers` | No | no | [agent-coordination-tools](agent-coordination-tools.md) | Only when tool search is disabled; never in subagents |
| `WebFetch` | Yes | source | [web-tools](web-tools.md) | Org policy can withhold it; `CLAUDE_CODE_DISABLE_WEB_FETCH` |
| `WebSearch` | Yes | source | [web-tools](web-tools.md) | Not on Bedrock |
| `Workflow` | Yes | gated ref (`WORKFLOW_SCRIPTS`) | agents area | Never in subagents |
| `Write` | Yes | source | [file-tools](file-tools.md) | |

Notes:
- (a) The snapshot has a gated `ListPeersTool` reference (`UDS_INBOX`), a plausible ancestor of `ListAgents`. No public source confirms the link.
- (b) The snapshot has a gated `Sleep` tool with a related purpose. No public source says `ScheduleWakeup` derives from it.

Counts: `comparison/tools.md` reports 33 in both, 13 new, 10 snapshot-only. That diff is by name against source directories and registered names, so it counts four tools as new that the snapshot already referenced behind gates (`Monitor`, `PushNotification`, `SendUserFile`, `Workflow`). It also counts `TaskOutput` as "in both" though docs now list it as removed.

## Configuration & interfaces

### Rule formats

| Format | Tools | Match |
| :- | :- | :- |
| `Bash(npm run *)` | Bash, Monitor | Command pattern |
| `PowerShell(Get-ChildItem *)` | PowerShell | Command pattern |
| `Read(~/secrets/**)` | Read, Grep, Glob, LSP | Path pattern |
| `Edit(/src/**)` | Edit, Write, NotebookEdit | Path pattern |
| `Skill(deploy *)` | Skill | Skill name |
| `Agent(Explore)` | Agent | Subagent type |
| `WebFetch(domain:example.com)` | WebFetch | Domain |
| `WebSearch` | WebSearch | Bare name only |

- Every other tool accepts only the bare name.
- Rules are accepted in `permissions.allow/deny`, `/permissions`, `--allowedTools`/`--disallowedTools`, SDK `allowedTools`/`disallowedTools`, skill `allowed-tools`, and hook `if` conditions. Hook `matcher` fields use bare names, not this format.
- An `Edit(...)` allow also grants read on that path. A `Read(...)` deny also blocks Edit and Write there, including creation (Write since v2.1.228).

### Tools outside the 46-row table

| Name | Where documented | Status |
| :- | :- | :- |
| `StructuredOutput` | SDK structured outputs | Added by the host when `outputFormat`/`--json-schema` is set; schema comes from the caller |
| `Projects` | SDK types | Reads and writes the claude.ai Project attached to the session |
| `ReadMcpResourceDirTool` | SDK types | Lists a directory resource's direct children; not enabled in every session |
| `RefreshMcpTools` | SDK types | Registered only with `CLAUDE_CODE_ENABLE_REFRESH_MCP_TOOLS=1` and at least one MCP server; v2.1.211+ |
| `ShowOnboardingRolePicker` | SDK types | Cowork onboarding role picker |
| `mcp__<server>__<tool>` | MCP docs | Dynamic; open argument object |
| advisor | `tools-reference` note | API server tool, not nameable in rules or matchers |

### Legacy aliases

`LEGACY_TOOL_NAME_ALIASES` maps earlier names to current ones and is honoured by permission rules, hook matchers and the `tools`/`disallowedTools` options. Documented examples: `Task` to `Agent`, `KillShell` and `KillBash` to `TaskStop`. Path rules for `Write`, `NotebookEdit`, `Glob` and legacy `MultiEdit` are accepted but never match.

## Failure modes & edge cases

- A `TaskOutput` entry in `disallowedTools` or a deny rule is silently ignored.
- `BUILTIN_TOOL_NAMES` omits some built-ins, so a deny list built from it is incomplete; `"*"` is the documented way to deny everything.
- `EndConversation` is not removed by deny rules while any other tool remains.
- `TodoWrite` is in `BUILTIN_TOOL_NAMES` though absent by default.

## Changes since the snapshot

- 2.1.178: `TeamCreate`, `TeamDelete` removed.
- 2.1.277: `TaskOutput` removed.
- Tools added: see each family spec. Dated introductions: `Monitor` 2.1.98, `PushNotification` 2.1.110, `EndConversation` 2.1.214, `ListAgents` 2.1.224, `SendFeedback` 2.1.247 (docs say v2.1.238).
- Docs give minimum versions, not changelog entries, for `ReportFindings` (v2.1.196) and `SubagentHandback` (v2.1.271).

## Open questions

- Full membership of `LEGACY_TOOL_NAME_ALIASES`. Docs give examples only.
- Whether `ArtifactInput`'s two documented actions are the tool's complete interface; see [post-leak-artifact](post-leak-artifact.md).
