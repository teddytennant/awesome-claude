# Headless Mode and Stream-JSON Protocol
**Status:** shipped
**Provenance:** both (`cli/`, `entrypoints/sdk/controlSchemas.ts`, `coreSchemas.ts` in snapshot)
**Sources:** docs `headless.md`, `cli-reference.md`, `agent-sdk__streaming-output.md`, `agent-sdk__streaming-vs-single-mode.md`, `agent-sdk__typescript.md`; snapshot `entrypoints/sdk/`; changelog 2.1.81 to 2.1.311

## Purpose
`claude -p` runs Claude Code non-interactively for scripts and CI, and `stream-json` over stdio is the wire protocol the Agent SDK and IDE hosts use. Public docs specify flags and messages. The control protocol is mostly evidenced by the snapshot and the SDK reference.

## Behaviour

### Basic run
1. `-p` / `--print` MUST run non-interactively and exit 0 on success, non-zero on failure. Invalid flags error on stderr before the run. Run failures print as the result.
2. `--bg` MUST be rejected with `-p`, and `--cloud` with a description too. `--cloud <id> -p` queues a message and exits.
3. Piped stdin is capped at 10 MB, with an error over the cap.
4. `-p` shows no workspace trust dialog or per-server approval. It runs project hooks and connects `.mcp.json` servers even in untrusted folders.
5. `--mcp-config` with `-p` waits for pending servers before running.
6. Since 2.1.302, runs start in Manual when nothing sets a mode, and calls needing approval are denied unless a hook or `--permission-prompt-tool` approves.
7. `--permission-prompts none` (2.1.259) MUST not consult a host, MUST deny anything that would prompt unless a `PermissionRequest` hook allows, MUST tell Claude not to retry, removes `AskUserQuestion`-type tools, and cancels unhandled elicitations.
8. Denials appear as `permission_denied` system messages and in the result's `permission_denials`.
9. `dontAsk` denies what would prompt. Allowed entries and read-only actions run.
10. Background command limits apply only to unattended sessions (2.1.288).
11. Background Haiku auto-title is not sent from `claude -p` runs launched outside an SDK or IDE (2.1.277).
12. Skipped MCP entries are in `mcp_server_errors` on init (2.1.219).

### Bare mode
13. `--bare` (2.1.81) MUST skip discovery of hooks, skills, commands, subagents, installed plugins, MCP, auto memory and CLAUDE.md.
14. It MUST NOT read OAuth or the keychain. It needs `ANTHROPIC_API_KEY`, an `apiKeyHelper` in `--settings`, or provider credentials.
15. Tools are Bash, file read, and file edit. Context comes through flags: `--append-system-prompt[-file]`, `--settings`, `--mcp-config`, `--agents`, `--plugin-dir`, `--plugin-url`.
16. Since 2.1.286: only CLI-supplied MCP connects, no IDE auto-connect unless `--ide`, no system reminders, no background tasks, and timed-out commands stop.
17. `--add-dir` skills load, partially.
18. Docs state `--bare` will become the `-p` default in a future release.

### Exit and background work
19. After a turn with stdin closed, the run MUST wait for background work: commands from the main conversation until exit or limit, then one more turn; subagents and workflows until done; Monitor until timeout (5 minutes by default) or the cap; pending `/loop` wakeups for prompt-as-text runs.
20. Idle wait cap is 10 minutes, set by `CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS` (0 for none), dropping partial results at the cap.
21. A stderr line beginning `Waiting for background work to finish` appears after 5 seconds if stderr is a terminal. In JSON modes it prints only when stdout isn't a terminal.
22. `--max-budget-usd` reached stops background work.
23. Each turn's result prints in `text` mode (2.1.295); `json` prints the last.
24. Slow stream consumers get a drain wait, capped at 30 seconds.
25. SIGTERM MUST exit 143, kill running Bash trees, run `SessionEnd`, and not record an interrupted turn or synthetic denials (2.1.236). `CLAUDE_CODE_RESUME_INTERRUPTED_TURN=1` continues on resume. SIGINT or `interrupt()` ends the turn.
26. A deleted working directory leaves the session running, with a warning at turn start and shell failures.
27. Responses cut off by server error, connection loss or stall MUST auto-continue (2.1.246).

### Output formats
28. `text`, `json` (`result`, `session_id`, metadata), `stream-json` (NDJSON).
29. `--json-schema` MUST validate, and exits with `Error: --json-schema is not a valid JSON Schema` on bad input. `format` is an annotation only. Absent `structured_output` means no valid output.
30. `stream-json` needs `--verbose` for full output, and `--include-partial-messages` for deltas (`type: stream_event`).
31. JSON output MUST write DEL, C1 and Unicode format characters as `\uXXXX` escapes; parsed values are unchanged (2.1.311).

### Messages
32. `system/init` MUST carry `session_id`, `uuid`, `claude_code_version`, `cwd`, `tools`, `mcp_servers` (`name`, `status`, `source`), `model`, `slash_commands`, `terminal_slash_commands`, `output_style`, `skills`, `plugins`, and optional `agents`, `betas`, `mcp_server_errors`, `plugin_errors`.
33. `result` subtypes: `success`, `error_during_execution`, `error_max_turns`, `error_max_budget_usd`, `error_max_structured_output_retries`.
34. `result` fields: `duration_ms`, `duration_api_ms`, `is_error`, `api_error_status`, `num_turns`, `result`, `stop_reason`, `total_cost_usd`, `usage`, `permission_denials`, `structured_output`, `deferred_tool_use`, `terminal_reason`, `result_index`, `queued_turn_count`, `user_message_uuids`, `ttft_ms` and timing fields.
35. `rate_limit_event` warnings say whether extra usage is on (2.1.295).
36. Hook events: `SessionStart` and `Setup` are always included; others with `--include-hook-events`.
37. Subagent text and thinking with `--forward-subagent-text`, keyed by `parent_tool_use_id`, including nested depth (2.1.219 and earlier).

### Input and control protocol
38. `--input-format stream-json` takes NDJSON user messages on stdin. `--replay-user-messages` re-emits them for acknowledgment.
39. Snapshot control envelope: `control_request` with `request_id` and `request`; `control_response` with `response.subtype` of `success` or `error`, and `request_id`; `control_cancel_request`.
40. Snapshot request subtypes: `initialize`, `interrupt`, `can_use_tool`, `set_permission_mode`, `set_model`, `set_max_thinking_tokens`, `mcp_status`, `get_context_usage`, `rewind_files`, `cancel_async_message`, `seed_read_state`, `hook_callback`, `mcp_message`, `mcp_set_servers`, `reload_plugins`, `mcp_reconnect`, `mcp_toggle`, `stop_task`, `apply_flag_settings`, `get_settings`, `elicitation`.
41. Current docs add `register_repo_root` (`DirectoryAdded` hook) and reference surfaces for reads and reloads through `Query` methods.
42. `initialize` carries hooks, `sdkMcpServers`, `jsonSchema`, `systemPrompt`, `appendSystemPrompt`, `agents`, `promptSuggestions`, `agentProgressSummaries`. Its response carries commands, agents, output style, models, account, pid and fast mode state.
43. `set_model` applies mid-turn (2.1.212).
44. Model switches, messages and interrupts MUST NOT wait behind a context usage check.
45. A message with `priority` "now" interleaves without cancelling running web tools (2.1.287).
46. A message using `client_composed: true` is delivered verbatim, skipping prompt processing that `verbatimPrompts` describes.
47. A `PreToolUse` `defer` decision pauses at a tool call; `-p --resume` re-evaluates. `deferred_tool_use` reports it.
48. With stream-json input, `--max-turns` semantics apply per message per the CLI reference.

## Configuration & interfaces
| Flag | Purpose |
|---|---|
| `-p`, `--print` | Non-interactive |
| `--output-format`, `--input-format` | Formats |
| `--include-partial-messages`, `--include-hook-events`, `--forward-subagent-text`, `--replay-user-messages` | Stream contents |
| `--json-schema` | Structured output |
| `--max-turns`, `--max-budget-usd` | Print-only limits |
| `--no-session-persistence`, `--session-id`, `--fork-session` | Sessions |
| `--permission-mode`, `--permission-prompts`, `--permission-prompt-tool`, `--allowedTools`, `--tools` | Permissions |
| `--system-prompt[-file]`, `--append-system-prompt[-file]`, `--exclude-dynamic-system-prompt-sections`, `--system-prompt-snapshot` | Prompt |
| `--setting-sources`, `--settings`, `--strict-mcp-config`, `--mcp-config` | Config |

Commands available in headless: `/config key=value`, `/goal`, `/output-style`, `/advisor`, `/reload-plugins`, among others. `/code-review` runs foreground.

## Failure modes & edge cases
- A `-p` run with no host denies approvals, so use `--allowedTools` or a mode.
- A bare `Bash` in `--allowedTools` is dropped in auto mode.
- Cost figures come from a client-side estimate.
- Partial results are lost at the wait cap.
- `CLAUDE_CODE_EXIT_AFTER_STOP_DELAY` exits idle SDK mode.

## Changes since the snapshot
- 2.1.90: picker hides `-p` sessions. 2.1.121: `CLAUDE_CODE_FORK_SUBAGENT=1`; on by default since 2.1.302.
- 2.1.212: mid-turn model. 2.1.219: `mcp_server_errors`, nested forwarding. 2.1.236: SIGTERM rework.
- 2.1.246: auto-continue. 2.1.259: `--permission-prompts`. 2.1.277: no auto-title, faster first turn.
- 2.1.286: stricter bare. 2.1.288: limits unattended only. 2.1.295: per-turn text results, `rate_limit_event` wording.
- 2.1.302: Manual default. 2.1.311: escaped output.

## Open questions
- Authoritative list of control subtypes at 2.1.314; the wire protocol isn't publicly specified.
- Whether the snapshot's `--sdk-url` remote transport (which required stream-json in both directions, used by bridge sessions) remains at 2.1.314; it isn't in public help.
