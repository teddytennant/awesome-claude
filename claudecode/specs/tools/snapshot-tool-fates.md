# Fate of Snapshot Tools No Longer Documented

**Status:** removed
**Provenance:** snapshot
**Sources:** `comparison/tools.md`; snapshot `tools/BriefTool`, `tools/ConfigTool`, `tools/REPLTool`, `tools/SleepTool`, `tools/SyntheticOutputTool`, `tools/TaskOutputTool`, `tools/TeamCreateTool`, `tools/TeamDeleteTool`, `tools/AgentTool/constants.ts`, `cli/structuredIO.ts`; docs `agent-sdk/typescript`, `agent-sdk/structured-outputs`, `sub-agents`, `permissions`, `settings-reference`; changelog 2.1.178, 2.1.277

## Purpose

`comparison/tools.md` lists ten snapshot names absent from the current `tools-reference` table. This spec records what each was and what happened to it. The ten are not one class: some were really removed, some were renamed, some were never public tools, and one is still live but documented elsewhere. A snapshot-only name MUST NOT be read as removed without the evidence below.

## Behaviour

### Disposition summary

| Name | Class | Disposition | Evidence |
| :- | :- | :- | :- |
| `Task` | Renamed | Now `Agent`; alias still accepted | Docs |
| `TeamCreate` | Removed | Removed in 2.1.178 | Changelog |
| `TeamDelete` | Removed | Removed in 2.1.178 | Changelog |
| `REPL` | Removed | Removed in v2.1.275 | SDK docs |
| `StructuredOutput` | Live, undocumented in that table | Still exists; host-added | SDK docs |
| `SandboxNetworkAccess` | Never a model tool | Internal permission-request name | Snapshot; no current mention |
| `Brief` | Legacy name | Legacy alias of `SendUserMessage`; same fate | Snapshot only |
| `SendUserMessage` | Gated, unreleased at snapshot | No public trace | Snapshot only |
| `Sleep` | Gated, unreleased at snapshot | No public trace | Snapshot only |
| `Config` | Internal-only at snapshot | No public trace; `/config` is a separate command | Snapshot only |

`TaskOutput` is not in the comparison's snapshot-only list because `tools-reference` still has a row for it, but that row says it was removed. It belongs in this spec.

### Renamed

1. **`Task` to `Agent`.** Renamed in version 2.1.63 per `sub-agents`, before the snapshot. In the snapshot `Task` is `LEGACY_AGENT_TOOL_NAME`, an alias on the Agent tool, and permission setup normalises it. Current requirements:
   - Permission rules, hook matchers, `tools` and `disallowedTools` MUST continue to accept `Task` and resolve it to `Agent`, including `Task(...)` rule forms.
   - The `tools` array of the SDK init message MUST continue to report the tool as `Task` for compatibility, so consumers map names through `LEGACY_TOOL_NAME_ALIASES`.

### Removed

2. **`TeamCreate`, `TeamDelete`.** Snapshot behaviour: gated by `isAgentSwarmsEnabled()`; `TeamCreate` took `team_name` and optional `description`, and `TeamDelete` tore a team down. Since 2.1.178, with `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` every session has one implicit team and teammates are spawned directly with the Agent tool's `name`. The Agent `team_name` parameter MUST still be accepted and ignored.
3. **`TaskOutput`.** Snapshot behaviour: retrieved output from a running or finished background task. Removed in v2.1.277. Current replacement: Claude reads the background task's output file with `Read`. Requirements:
   - The `taskOutputMaxChars` setting and `TASK_MAX_OUTPUT_LENGTH` MUST have no effect.
   - A `disallowedTools` entry or deny rule naming `TaskOutput` MUST be ignored without a warning.
   - The `TaskOutputInput` type is gone from the SDK.
4. **`REPL`.** Snapshot behaviour: a batch-execution tool that, when on, hid the primitive tools (`Read`, `Write`, `Edit`, `Glob`, `Grep`, `Bash`, `NotebookEdit`, `Agent`) from direct model use and exposed them inside a VM context. Internal default-on for the interactive CLI only; opt in via `CLAUDE_CODE_REPL`. Docs state the experimental tool could be turned on through v2.1.274 with `CLAUDE_CODE_REPL=1` and was removed in v2.1.275. No changelog entry names the removal.

### Still live

5. **`StructuredOutput`.** Snapshot source `SyntheticOutputTool`. Current: the host adds it when the caller sets `outputFormat`, `output_format` or `--json-schema`; its input schema is built from the caller's schema, so there is no fixed exported type. Requirements:
   - A schema mismatch MUST produce a `tool_result` with `is_error: true`, and the model calls again, so one query can hold several calls.
   - The validated value surfaces as `ResultMessage.structured_output`.
   - Applications SHOULD filter calls by this name from any display of agent steps.

### Never public

6. **`SandboxNetworkAccess`.** A constant in `cli/structuredIO.ts`, not a tool directory. It names network-access permission requests sent through the structured IO channel. It was never a model-callable tool. No current doc uses the name; the comparison picked it up as a name match.
7. **`SendUserMessage` (legacy `Brief`).** Snapshot feature gated by `KAIROS`/`KAIROS_BRIEF`: a tool that made user-visible replies explicit, with `message`, optional `attachments` and a `status` of normal or proactive. Text outside it was treated as background detail. Gated and unreleased at the snapshot. Current docs and changelog do not mention it. Parts of its surface now appear in separately documented tools: `PushNotification` has a `status: "proactive"` field and `SendUserFile` delivers files. No public source says they descend from it.
8. **`Sleep`.** Snapshot feature gated by `PROACTIVE`/`KAIROS`: wait without holding a shell, interruptible by the user. Current docs do not list it. The nearest shipped mechanisms are `ScheduleWakeup` and `Monitor`, but no source connects them.
9. **`Config`.** Snapshot tool available only to internal builds, reading and writing a whitelist of settings. Current docs do not list it. The user-facing `/config` command is unrelated to this tool's availability.

## Configuration & interfaces

| Key | Status |
| :- | :- |
| `taskOutputMaxChars` | No effect since v2.1.277 |
| `TASK_MAX_OUTPUT_LENGTH` | No effect since v2.1.277 |
| `CLAUDE_CODE_REPL` | Accepted through v2.1.274 only |
| `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` | Still current; implicit team since 2.1.178 |
| Agent `team_name` | Accepted, ignored |

## Failure modes & edge cases

- Tooling that diffs by name will flag `Task` as removed. It is an alias.
- A deny rule on a removed name such as `TaskOutput` is harmless and silent, so stale policy gives no feedback.
- A `Bash` output path now reaches Claude through `Read`, so a session with `Read` denied loses the replacement route for background output. Docs do not address this case.

## Changes since the snapshot

- 2.1.178: `TeamCreate`, `TeamDelete` removed; implicit single team.
- 2.1.277: `TaskOutput` removed, with `taskOutputMaxChars` and `TASK_MAX_OUTPUT_LENGTH` inert.
- v2.1.275 (SDK docs, no changelog line): `REPL` removed.

## Open questions

- Whether `SendUserMessage`, `Brief`, `Sleep` and `Config` still exist behind internal gates. Public sources are silent, so absence from docs is the only evidence.
- Whether `SandboxNetworkAccess` remains the internal request name.
- Whether `ListPeersTool` (gated in the snapshot) became `ListAgents`.
- How a session denied `Read` retrieves background output after the `TaskOutput` removal.
