# Hooks System

**Status:** shipped
**Provenance:** both (core in snapshot; `mcp_tool` handlers, exec form, `onFailure`, `defer` and others post-leak, since v2.1.89, 2026-03-31)
**Sources:** docs `hooks`, `hooks-guide`; snapshot `utils/hooks/`, `schemas/hooks.ts`; changelog 2.1.89 to 2.1.314. Per-event detail lives in [hook-events.md](hook-events.md).

## Purpose

Hooks let users, projects, organizations, plugins, skills and agents attach handlers to lifecycle events. A handler can observe an event, add context for the model, rewrite tool input or output, or block the action. Hooks are enforced by the harness rather than by model cooperation. JavaScript function hooks registered by mods are a separate mechanism (see [mods.md](mods.md)) and coexist with these.

## Behaviour

### Configuration model

1. Configuration MUST have three levels: event name, matcher group (`matcher`, `hooks`), and handler.
2. Hooks MUST load from: user, project and local settings files, managed policy, plugin `hooks/hooks.json` (with optional top-level `description`), skill frontmatter, and agent frontmatter.
3. Entries from settings levels MUST merge, not replace. Lower levels add hooks and cannot remove managed ones.
4. A handler defined identically in several settings files MUST run once. A plugin's or skill's identical copy stays separate.
5. An unrecognized event name MUST NOT invalidate the settings file (v2.1.101).
6. Settings-file hooks, managed hooks and plugin hooks MUST also fire inside subagents, with `agent_id` and `agent_type` in the input.
7. Cloud sessions do not read the local user settings. Self-hosted runner sessions also run operator-seeded hooks from the runner's `~/.claude/` and may run the runner image's managed settings, subject to managed-source precedence.

### Frontmatter hooks

8. Agent frontmatter hooks MUST be active only while that agent runs, and a `Stop` hook there MUST convert to `SubagentStop`. They also fire for a main-thread `--agent` session (v2.1.116).
9. Skill frontmatter hooks MUST register on invocation and stay registered for the rest of the session, across later turns. `once: true` removes a hook after its first successful run; a failure, exit 2 or timeout leaves it in place. `once` is honoured only in skill frontmatter.
10. A skill's front-matter `UserPromptSubmit` hook MUST first run on the prompt after the one that invoked the skill (v2.1.299).
11. Each skill source (project, personal folder, each plugin) MUST be limited per session to 1,024 hooks and 16,384 total matcher characters, where a matcher counts once per hook under it. A skill that crosses the limit registers none of its hooks and logs `registers none of its hooks` (v2.1.304).
12. Under `strictPluginOnlyCustomization` locking hooks, only plugin, bundled and managed-directory skills keep frontmatter hooks. A skill whose hooks are kept out also loses `allowed-tools` when used in the main conversation (v2.1.304).

### Matching

13. A matcher of `"*"`, `""` or omitted MUST match everything.
14. A matcher using only letters, digits, `_`, `-`, spaces, `,` and `|` MUST be an exact string or list of exact strings, split on `|` or `,` with surrounding whitespace trimmed.
15. Any other matcher MUST be an unanchored JavaScript regular expression.
16. `FileChanged` and `StopFailure` MUST use a narrower exact set (letters, digits, `_`, `|`); a hyphen, space or comma keeps them on the regex path, and only `|` separates alternatives.
17. A bare `mcp__server` contains only exact-match characters, so it matches no tool. `mcp__server__.*` is required. Plugin MCP tools use the segment `plugin_<plugin>_<server>`, and bare server keys never match them.
18. A `matcher` on an event without matcher support MUST be silently ignored.
19. The optional per-handler `if` holds exactly one permission rule, evaluated only on `PreToolUse`, `PostToolUse`, `PostToolUseFailure`, `PermissionRequest` and `PermissionDenied`. A handler with `if` on any other event MUST never run.
20. For Bash, `if` MUST strip leading `VAR=value` assignments and check each subcommand, including those inside `$()` and backticks. If the commands cannot be determined, or a pattern more specific than a command name meets `$()`, backticks or `$VAR`, the hook MUST run anyway. `if` is best-effort and is not an enforcement boundary.
21. A single-segment directory pattern on a file tool (`Edit(src/**)`) matches only `<cwd>/src` and below; `**/src/**` matches any depth (v2.1.214). `Monitor(...)` matches the Monitor tool's shell commands as `Bash(...)` matches Bash's (v2.1.314).

### Execution

22. Matching handlers for one event MUST run in parallel. At most 12 prompt or agent hooks of one event run at once; the rest wait, and a waiter's timeout starts when it starts (v2.1.302).
23. Handlers run in the current directory. If that directory no longer exists, command hooks MUST fall back to the first existing of: session start directory, project root, home, system temp, and log a warning.
24. On macOS and Linux, command hooks MUST run in their own session with no controlling terminal.
25. The hook environment MUST inherit the parent's minus `OTEL_*` exporter variables (v2.1.128), minus scrubbed variables when `CLAUDE_CODE_SUBPROCESS_ENV_SCRUB=1`, and minus Anthropic credentials in HIPAA-configured sessions.
26. Output strings (`additionalContext`, `systemMessage`, `initialUserMessage`, plain stdout) MUST be measured individually and, above 10,000 characters, saved to a file in the session directory and replaced by the path plus a preview of up to 2,000 characters (v2.1.89). There is no override.
27. `<system-reminder>` and its closing tag in `additionalContext` MUST have the `<` escaped to `&lt;` before reaching the model (v2.1.292).
28. Injected text is saved in the transcript and replayed on resume, not regenerated. `SessionStart` runs again on resume.

### Outcome rules

The table MUST be applied for sync command hooks on ordinary events.

| Stdout | Exit 0 | Exit 2 | Other exit |
| :- | :- | :- | :- |
| Valid, schema-passing JSON object | Fields apply | Blocks; fields read but cannot override the block | Fields alone decide (unless failure-blocking applies, then it is a failure) |
| Unparseable or schema-failing JSON | Non-blocking error | Blocks; stderr is the reason | Non-blocking error |
| Plain text or empty | Success | Blocks; stderr is the reason | Non-blocking error carrying first stderr line |

29. Stdout counts as JSON only when it is a single object with only whitespace around it. Output not starting with `{`, or not ending with `}`, is plain text. Multi-line output where each line parses as JSON is plain text unless a line is a field-setting object, in which case it is a parse failure.
30. Plain stdout MUST be added to model context only on `UserPromptSubmit`, `UserPromptExpansion`, `SessionStart` and `PostModelSwitch`. Elsewhere it goes to the debug log.
31. stderr from a hook exiting 0 MUST NOT reach the model.
32. Event exceptions: any non-zero exit fails `WorktreeCreate`; any non-zero exit fails `WorktreeRemove` if the directory still exists; on `Stop`, `SubagentStop`, `TaskCompleted` and a plugin's `UserPromptSubmit`, an exit 2 with empty stdout and a "file missing" stderr is a non-blocking error; `Elicitation` and `ElicitationResult` apply `hookSpecificOutput` only on exit 0; events that discard output ignore JSON except side-effect fields such as `terminalSequence`.
33. Timed-out `command`, `http` and `mcp_tool` hooks MUST be cancelled and their output discarded. On most events that renders no decision, so a stalled hook is not a gate. `PreModelSwitch` is the exception: timeout blocks the switch.
34. Agent SDK callback hooks that time out on `PreToolUse` or `UserPromptSubmit` MUST block.
35. If a sync hook prints an allow, then leaves a background process holding its stdout or stderr, the harness MUST block with an error containing `refusing to honor the suspect capture`. A decision printed after reading stops is ignored.

### Failure-blocking (`onFailure`, v2.1.295)

36. `onFailure: "block"` on `command` and `http` hooks MUST turn a failure into what exit 2 does on that event, except that on `PermissionRequest` it denies. Failures are: cannot start; exit code other than 0 or 2 (even with allowing JSON); HTTP connection failure or non-2xx; timeout; invalid output, including a 2xx HTTP body that is neither empty nor a JSON object. Plain-text command stdout is not a failure.
37. `onFailure` MUST have no effect on `Stop`, `SubagentStop`, `TaskCompleted`, `TeammateIdle`, or background hooks.
38. On Windows without Git Bash, a shell-form `PreToolUse` or `PermissionRequest` command hook with `onFailure` unset that fails or times out MUST block the call, since only exit 0 or 2 counts as its verdict. `onFailure: "continue"` opts out.
39. A plugin hook that cannot be handed an action, or cannot hand back an answer, MUST refuse the action; a tool that already ran has its result withheld (v2.1.299).

### Handler-type behaviour

40. **Exec form**: when `args` is present, `command` MUST be resolved as an executable and spawned without a shell, with placeholders substituted as plain strings (v2.1.139). A bare `command` containing whitespace alongside `args` logs a warning. `.cmd` and `.bat` shims on Windows cannot be spawned this way.
41. **Shell form**: `sh -c` on macOS and Linux, Git Bash on Windows, else PowerShell; `shell` overrides. In PowerShell shell form, `${CLAUDE_PROJECT_DIR}`, `${CLAUDE_PLUGIN_ROOT}` and `${CLAUDE_PLUGIN_DATA}` MUST be rewritten to `${env:NAME}`; bare `$CLAUDE_PROJECT_DIR` is not rewritten and logs a warning.
42. **`${user_config.*}`** MUST substitute in exec-form plugin hooks only. In shell form the hook MUST fail (v2.1.207); `$CLAUDE_PLUGIN_OPTION_<KEY>` is the alternative.
43. **HTTP** hooks POST the input as JSON. Header `$VAR` interpolation resolves only names in `allowedEnvVars`, also intersected with `httpHookAllowedEnvVars`; unlisted names become empty. `allowedHttpHookUrls`, when defined at any level, gates all sources. Snapshot code also has an SSRF guard (`utils/hooks/ssrfGuard.ts`); current state is not stated in the docs. Response mapping: 2xx empty is success; 2xx JSON object is parsed; any other 2xx body, non-2xx and connection failure are non-blocking errors.
44. **`mcp_tool`** calls a tool on a configured server (v2.1.118). String values in `input` support `${path}` substitution from the hook input. Text output is treated as stdout; `isError: true` is a non-blocking error. On blocking events the hook MUST wait for a connecting server, up to `MCP_TIMEOUT` and within its own timeout; on observational events it does not wait. A `cached` server connects at call time. It MUST never start OAuth. `SessionStart` at launch and all `Setup` events MUST skip `mcp_tool` hooks with a debug line.
45. **`prompt`** sends the input and prompt to the background model and expects `{ok, reason, impossible}`. If `$ARGUMENTS` is absent, the input is appended. `\$` escapes literals.
46. **`agent`** (experimental) spawns a subagent with tool access, up to 50 turns, returning `{ok, reason}`. It behaves like a prompt hook with `continueOnBlock: true`, and has no `continueOnBlock` or `impossible`.
47. `ok: false` handling is per event; see [hook-events.md](hook-events.md).
48. **Async**: `async: true` (command hooks only) runs without blocking and ignores decision fields. `timeout` is not enforced once running. `additionalContext` and `systemMessage` are delivered to the model on the next turn, and are not shown to the user. `asyncRewake` runs in the background, keeps `timeout`, and on exit 2 wakes the model even when idle, passing stderr (or stdout) as a system reminder. In `-p`, remaining async hooks are killed at teardown as `cancelled`. Invalid-typed fields are dropped, not rejected. An async `SessionStart` skips output identical to what the model last got from it.

### Trust, disabling, debugging

49. Interactive sessions MUST hold back all settings-file hooks, including the user's own, until the workspace trust dialog is accepted. `-p` and SDK sessions treat the folder as trusted.
50. Project skill frontmatter hooks follow the settings-file rule. Project subagent frontmatter hooks require trust acceptance, which `-p` does not supply.
51. `disableAllHooks` resolves through settings precedence, and non-managed levels MUST NOT disable managed hooks. `--settings '{"disableAllHooks": true}'` is the one-run override. No per-hook disable exists. `--safe-mode` disables hooks entirely (v2.1.169).
52. `allowManagedHooksOnly` MUST block user, project, local and plugin hooks, exempting plugins force-enabled in managed `enabledPlugins`. It also narrows `statusLine`, `fileSuggestion` and `subagentStatusLine`, and disables `command`-source plugins and marketplace `headersHelper` commands unless `disableCommandPluginSources` is explicitly `false`.
53. `/hooks` is a read-only browser opening on configured hooks grouped by event, with source labels, full text, and an `All events` entry (v2.1.286). The VS Code Hooks dialog can edit user, project and local hooks (v2.1.269). Direct file edits are picked up by the watcher.
54. Debug logs SHOULD record `Hooks:` completion lines with event, command, plugin, outcome and duration (v2.1.296).

## Configuration & interfaces

### Handler fields

| Field | Types | Notes |
| :- | :- | :- |
| `type` | all | `command`, `http`, `mcp_tool`, `prompt`, `agent` |
| `if` | all | One permission rule; tool events only |
| `timeout` | all | Seconds. Default 600 (`command`, `http`, `mcp_tool`), 30 (`prompt`), 60 (`agent`). 30 on `UserPromptSubmit`, `PreModelSwitch`, `PostModelSwitch`; 10 on `MessageDisplay`; `SessionEnd` shares a budget |
| `statusMessage` | all | Spinner text |
| `once` | all | Skill frontmatter only |
| `command`, `args`, `async`, `asyncRewake`, `shell`, `onFailure` | command | See above |
| `url`, `headers`, `allowedEnvVars`, `onFailure` | http | |
| `server`, `tool`, `input` | mcp_tool | Plugin servers use `plugin:<plugin>:<server>` |
| `prompt`, `model` | prompt, agent | |
| `continueOnBlock` | prompt | v2.1.139; default false |

### Universal output fields

| Field | Effect |
| :- | :- |
| `continue` | `false` halts processing; beats event decisions |
| `stopReason` | Shown to the user; stays in the conversation |
| `suppressOutput` | Accepted, no effect |
| `systemMessage` | User warning; some events discard or reroute it |
| `terminalSequence` | Emitted by the harness; allowlist is OSC 0, 1, 2, 9, 99, 777 and BEL. Any other content voids the field. Interactive and on-screen only (v2.1.141) |
| `decision`, `reason` | Top-level; only value is `"block"` |
| `hookSpecificOutput` | Requires `hookEventName` |

### Placeholders and environment

| Name | Meaning |
| :- | :- |
| `CLAUDE_PROJECT_DIR` | Project root at session start; does not follow worktrees. Input `cwd` does |
| `CLAUDE_PLUGIN_ROOT`, `CLAUDE_PLUGIN_DATA` | Plugin install and persistent data directories |
| `CLAUDE_ENV_FILE` | Available on `SessionStart`, `Setup`, `CwdChanged`, `FileChanged`; not in PowerShell hooks |
| `CLAUDE_CODE_REMOTE`, `CLAUDE_CODE_BRIDGE_SESSION_ID` | Remote context (the latter since v2.1.199) |
| `CLAUDE_EFFORT` | Same as input `effort.level` |
| `CLAUDE_CODE_SESSIONEND_HOOKS_TIMEOUT_MS`, `CLAUDE_CODE_STOP_HOOK_BLOCK_CAP`, `CLAUDE_CODE_DEBUG_LOG_LEVEL` | Tuning |

There is no `$CLAUDE_MODEL`. `ANTHROPIC_MODEL` does not track `/model`.

## Failure modes & edge cases

- Exit 1 without valid JSON is non-blocking. Policy hooks MUST use exit 2 or `onFailure: "block"`.
- A mistyped path in shell form exits 127 and surfaces as a non-blocking `No such file or directory` notice.
- In PowerShell, a `command` that is only quoted strings prints instead of running; the error says `PowerShell started no program`.
- `updatedInput` from `PreToolUse` and `PermissionRequest` is validated like model input: unknown keys dropped, and rejected input denies the call (v2.1.300).
- A hook configured with an unsupported type is skipped or errors, e.g. prompt or agent on `SessionStart`, `Setup`, `SubagentStart` (v2.1.142), agent on `PermissionRequest` (v2.1.280).
- `updatedToolOutput` changes only what the model sees. Telemetry records the original output.

## Changes since the snapshot

- v2.1.89: `defer`; `PermissionDenied`; 10,000-character output handling.
- v2.1.101: unknown event names tolerated.
- v2.1.105: `PreCompact` can block.
- v2.1.118: `mcp_tool` handlers.
- v2.1.121: `updatedToolOutput` for all tools.
- v2.1.139: exec-form `args`; `continueOnBlock`.
- v2.1.141: `terminalSequence`.
- v2.1.207: shell-form `${user_config.*}` rejected.
- v2.1.214: `if` directory semantics changed.
- v2.1.219, v2.1.251, v2.1.152: `DirectoryAdded`, model-switch events, `MessageDisplay`.
- v2.1.281: `claude plugin validate` warns on unquoted `${CLAUDE_PLUGIN_ROOT}`.
- v2.1.292: `<system-reminder>` escaping.
- v2.1.295: `onFailure`.
- v2.1.296: debug `Hooks:` lines.
- v2.1.299: `UserPromptSubmit` runs before skill expansion; plugin hooks refuse when they cannot answer.
- v2.1.300: `updatedInput` validated.
- v2.1.302: 12-hook concurrency limit.
- v2.1.304: skill hook limits.
- v2.1.314: auto mode in Cowork cloud sessions treats a hook's allow of an MCP tool as no answer.

## Open questions

- First versions of `PostToolBatch`, `UserPromptExpansion` and `asyncRewake` are not stated in the changelog.
- Whether the snapshot's HTTP SSRF guard still applies unchanged is not documented.
- Full ordering semantics when `continue: false` and event-specific decisions come from different parallel hooks are not specified beyond "`continue` takes precedence".
