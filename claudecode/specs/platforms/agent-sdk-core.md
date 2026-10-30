# Claude Agent SDK Core
**Status:** shipped
**Provenance:** both (`entrypoints/agentSdkTypes.ts`, `entrypoints/sdk/` in snapshot; much API surface post-leak)
**Sources:** docs `agent-sdk__*.md`, especially `overview`, `typescript`, `python`, `sessions`, `session-storage`, `streaming-output`, `permissions`, `hosting`, `migration-guide`, `typescript-v2-preview`; snapshot `entrypoints/`; changelog 2.1.90 to 2.1.314

## Purpose
A Python and TypeScript library that embeds Claude Code's agent loop, tools, permissions, sessions and hooks in a host process by driving the Claude Code binary as a subprocess. Distinct from the Client SDK (raw API) and Managed Agents (hosted harness). See [headless-stream-json.md](headless-stream-json.md) for the wire protocol.

## Behaviour

### Packaging
1. Packages are `@anthropic-ai/claude-agent-sdk` and `claude-agent-sdk`, renamed from `@anthropic-ai/claude-code` and `claude-code-sdk`.
2. The TS package MUST bundle a native binary as a per-platform optional dependency. The SDK version tracks the bundled Claude Code version.
3. `pathToClaudeCodeExecutable` overrides it. A `/core` entry supports bundlers, and a compile-to-executable path is documented.
4. Languages other than Python and TS use `claude -p` directly.
5. The V2 session API (`unstable_v2_*`) is removed at TS SDK 0.3.142; the version jumped from 0.2.x to 0.3.142.

### Entry points (TypeScript)
6. `query({prompt, options})` MUST return a `Query`, an async generator of `SDKMessage`. `prompt` may be a string or an `AsyncIterable<SDKUserMessage>` for streaming input.
7. `startup()` MUST spawn and complete the initialize handshake ahead of a prompt, returning `WarmQuery`.
8. `prewarm()` (alpha, TS SDK 0.3.282+) MUST start a spare process in a private temp dir or `options.cwd`, to be bound later with `claim()`.
9. `tool()` and `createSdkMcpServer()` define in-process MCP tools.
10. Session helpers MUST include `listSessions`, `getSessionMessages`, `getSessionInfo`, `renameSession`, `tagSession`, `forkSession`. `resolveSettings` reports effective settings.
11. Python mirrors these, plus `ClaudeSDKClient` for multi-turn sessions, and a `Transport` abstraction.
12. `break` from `for await`, or `await using`, MUST clean up subprocess and temp files (2.1.101).

### Query control
13. `Query` methods MUST include: `interrupt`, `rewindFiles`, `setPermissionMode`, `setModel`, `setMaxThinkingTokens`, `applyFlagSettings`, `updateSettings`, `initializationResult`, `reinitialize`, `supportedCommands`, `supportedModels`, `supportedAgents`, `mcpServerStatus`, `getContextUsage`, `readFile`, `reloadPlugins`, `reloadSkills`, `reloadOutputStyles`, `seedReadState`, `accountInfo`, `reconnectMcpServer`, `toggleMcpServer`, `setMcpServers`, `setMcpPermissionModeOverride`, `readMcpResource`, `stopTask`, `backgroundTasks`, `close`.
14. `setModel` mid-turn MUST apply at the next model round trip (2.1.212).

### Options
15. Core: `cwd`, `model`, `fallbackModel` (comma-separated chain), `effort`, `thinking`, `maxTurns`, `maxBudgetUsd`, `taskBudget` (alpha), `env` (replaces, not merges), `abortController`, `additionalDirectories`.
16. Tools and agents: `tools` (list or `claude_code` preset), `allowedTools`, `disallowedTools`, `toolConfig`, `toolAliases`, `agent`, `agents`, `skills`, `plugins`, `mcpServers`, `strictMcpConfig`.
17. Permissions: `permissionMode`, `allowDangerouslySkipPermissions`, `canUseTool`, `permissionPromptToolName`, `permissionPrompts` (`host` or `none`), `planModeInstructions`, `onElicitation`.
18. Prompt: `systemPrompt` (string, array, `custom`, or `claude_code` preset with `append`, `excludeDynamicSections`). An array form caches above the dynamic boundary. A `__SYSTEM_PROMPT_DYNAMIC_BOUNDARY__` line in `--system-prompt` has the same effect (2.1.275).
19. Settings: `settings`, `settingSources` (default all, `[]` disables user, project, local), `managedSettings`, `projectConfigRoot`.
20. Sessions: `continue`, `resume`, `forkSession`, `resumeSessionAt`, `resumeDropsTurn`, `sessionId`, `persistSession`, `title`, `sessionStore`, `sessionStoreFlush`, `loadTimeoutMs`.
21. Streaming: `includePartialMessages`, `includeHookEvents`, `forwardSubagentText`, `agentProgressSummaries`, `promptSuggestions`, `verbatimPrompts`, `outputFormat`.
22. Host integration: `spawnClaudeCodeProcess`, `executable`, `executableArgs`, `extraArgs`, `stderr`, `debug`, `debugFile`, `enableFileCheckpointing`, `sandbox`, `hooks`, `betas`.
23. `outputStyle` is not an `Options` field; use `settings`.
24. `maxThinkingTokens` is deprecated.

### Managed settings from a host
25. `managedSettings` is a policy-tier layer from the host. On machines with admin-deployed managed settings, it is ignored unless admins set `parentSettingsBehavior: "merge"` (default `first-wins`; 2.1.133).
26. `forceLoginMethod` is enforced for SDK logins (2.1.212).

### Messages
27. `SDKMessage` union covers assistant, user, replay, result, system, partial stream events, compact boundary, status, local command output, hook lifecycle, plugin install, tool progress, auth status, task notification, started, progress and updated, background tasks changed, thinking tokens, session state changed, worker shutting down, commands changed, notifications, files persisted, tool use summary, memory recall, rate limit, elicitation complete, permission denied, prompt suggestion, API retry, control request progress, model refusal fallback or no fallback, mirror error, informational, and conversation reset.
28. Streams that are cut off MUST still deliver `message_stop` since 2.1.290 (TS SDK 0.3.290). `message_delta` can be missing, and a tool block open at `message_stop` has incomplete input.
29. With partial messages, a `ping` stream event is sent every 30 seconds during non-streaming fallback (2.1.285). Gateway keep-alive liveness is reported (2.1.257).
30. Structured output streams as unvalidated `input_json_delta`; only the final result's `structured_output` is validated.

### Sessions
31. Sessions persist to local disk unless `persistSession` is false. Fork creates a new ID.
32. `--resume` picker hides SDK and `-p` sessions (2.1.90).
33. Priority "now" messages MUST NOT cancel a running web fetch or search (2.1.287).
34. Long compacted resumes are fast (2.1.281, 2.1.304).
35. Fork subagents are on by default in SDK sessions (2.1.302).
36. `SessionStore` MUST provide `append` and `load`, and may provide `listSessions`, `listSessionSummaries`, `delete`, `listSubkeys`. Keys are `projectKey`, `sessionId`, `subpath`.
37. Local disk stays primary: mirror writes are best-effort and report `SDKMirrorErrorMessage`. Resume materialises from the store. `getSessionMessages` returns the post-compaction chain. `forkSession` isn't a byte copy.

### Hosting
38. Each query uses a subprocess with state on local disk. Patterns: ephemeral, long-running, hybrid, multi-agent container.
39. The host should sandbox by container, and bring its own auth, persistence and observability. Shared multi-tenant containers should pass `settingSources: []`, set `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1` (auto memory ignores `settingSources`), and give each tenant its own `CLAUDE_CONFIG_DIR`.
40. Third-party developers can't offer claude.ai login through their products without approval, per terms; use API keys or provider credentials.

## Configuration & interfaces
| Variable | Purpose |
|---|---|
| `API_TIMEOUT_MS` | Header wait per attempt, default 600000 |
| `CLAUDE_CODE_MAX_RETRIES` | Default 10, cap 15 |
| `CLAUDE_STREAM_IDLE_TIMEOUT_MS`, `CLAUDE_ENABLE_STREAM_WATCHDOG` | Stall detection |
| `CLAUDE_ASYNC_AGENT_STALL_TIMEOUT_MS` | Subagent watchdog |
| `CLAUDE_CODE_ACCOUNT_UUID`, `CLAUDE_CODE_USER_EMAIL`, `CLAUDE_CODE_ORGANIZATION_UUID` | Host-supplied account info |
| `CLAUDE_CODE_FORWARD_SUBAGENT_TEXT` | As option |

## Failure modes & edge cases
- `env` replacing the environment can drop `PATH` unless the host spreads `process.env`.
- `allowedTools` is not an allowlist of available tools; use `tools` or `disallowedTools`.
- `canUseTool` fires only if permission flow falls to a prompt.
- A truncating resume is refused if `resumeDropsTurn` doesn't match what is discarded.
- `maxBudgetUsd` is client-side and can be exceeded.
- Non-streaming fallback uses a different failure path; see `agent-sdk__troubleshooting.md`.

## Changes since the snapshot
- 2.1.90: transcript writes no longer quadratic. 2.1.98, 2.1.110: tracing, `TRACEPARENT`.
- 2.1.101: cleanup on break. 2.1.133: `parentSettingsBehavior`.
- 2.1.212: `set_model` mid-turn. 2.1.246: auto-continue on cut-off.
- 2.1.260: lower idle CPU. 2.1.277: first turn doesn't wait on directory CLAUDE.md lookup.
- 2.1.280: effort holds dropped. 2.1.296: Sonnet 5.5 cache read price. 2.1.310: compaction memory.
- SDK surface additions: `startup`, `prewarm`, `SessionStore`, `resolveSettings`, `toolAliases`, `permissionPrompts`, and new message types.

## Open questions
- Python parity for `startup`, `prewarm`, and alpha options; not verified line by line.
- Exact mapping of SDK versions to CLI versions before 0.3.142.
