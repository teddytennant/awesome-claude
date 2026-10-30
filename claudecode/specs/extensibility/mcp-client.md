# MCP Client

**Status:** shipped
**Provenance:** both (core in snapshot; v2 runtime, protocol 2026-07-28, URL elicitation, auto-backgrounding, `alwaysLoad`, discovery cache post-leak)
**Sources:** docs `mcp`, `mcp-quickstart`, `tools-reference`, `env-vars`, `prompt-caching`; snapshot `services/mcp/`; changelog 2.1.89 to 2.1.314. Authentication is in [mcp-auth.md](mcp-auth.md), server-side tasks in [mcp-tasks.md](mcp-tasks.md), policy in [managed-mcp.md](managed-mcp.md).

## Purpose

Claude Code is an MCP client. It connects to configured servers, exposes their tools, resources and prompts, and manages lifecycle, limits and context cost. It can also act as a server through `claude mcp serve`.

## Behaviour

### Transports

1. `http` (recommended; `streamable-http` is an alias), `sse` (deprecated), `stdio`, `ws`. `sdk` is registrable only by an SDK host; such an entry in config, plugins or agent files MUST be skipped with a warning (v2.1.274).
2. An entry with `url` and no `type` MUST be skipped with the `has a "url" but no "type"` error (v2.1.202), since no `type` means stdio.
3. `claude mcp add --transport http` MUST try HTTP then fall back to SSE (v2.1.265). `--transport` does not accept `ws`. `ws` is header-only auth and has no OAuth.
4. Stdio servers MUST receive `CLAUDE_PROJECT_DIR` (v2.1.139), `CLAUDE_CODE_SESSION_ID` and `CLAUDECODE=1` (v2.1.154). `CLAUDE_CODE_MCP_ALLOWLIST_ENV=1` gives a safe baseline environment plus `env`. `OTEL_*` variables are not inherited (v2.1.128).
5. `roots/list` MUST return the launch directory and all additional working directories, and `notifications/roots/list_changed` is sent on change (v2.1.203).
6. Stdio shutdown on macOS and Linux: `SIGINT`, `SIGTERM` after 100 ms, `SIGKILL` after 400 ms more. Windows closes stdin, then ends the tree after 300 ms (v2.1.296).
7. `claude mcp serve` exposes Claude Code's tools over stdio; the client owns confirmation. `backgroundOutputPath` appears in Bash and PowerShell results for backgrounded commands (v2.1.295).

### Runtimes and protocol

8. Two runtimes exist: v1 (SDK 1.x) and v2 (SDK 2.0, adding revision 2026-07-28). The choice is fixed per process. v2 is used where flags are fetched (from v2.1.232) and by default without flags (v2.1.274), unless a host platform sets `CLAUDE_CODE_PROVIDER_MANAGED_BY_HOST`.
9. On v2, HTTP, stdio and claude.ai connector servers are probed for 2026-07-28 and use it if supported (stdio by default on all installs v2.1.292; connectors v2.1.295; cloud and Remote Control connectors v2.1.299). Stdio servers ignoring the probe are remembered for 7 days (v2.1.292). `MCP_SDK_GENERATION` and `MCP_PROTOCOL_NEGOTIATION` override.
10. On the newer revision, `list_changed` arrives over a held stream. A close within 10 s reopens up to three times. Longer-lived closes get five reopens an hour, then wait about six hours.

### Scopes and precedence

| Scope | Stored in | Reach |
| :- | :- | :- |
| Local (default) | `~/.claude.json` under the project | You, this project |
| Project | `.mcp.json` | Team, via VCS |
| User | `~/.claude.json` | You, all projects |

11. Precedence: `managedMcpServers`, then local, project, user, plugin, claude.ai connector. Whole entries win; no field merging.
12. Scopes dedupe by name. Plugins and connectors dedupe by endpoint, ignoring URL case of scheme and host, default port, and trailing slash.
13. Interactive sessions MUST prompt for approval of `.mcp.json` servers. `-p`, SDK and most cloud sessions load them without asking. `disabledMcpjsonServers`, `--setting-sources` and `--strict-mcp-config` keep them out.
14. A cloned repo MUST NOT self-approve: `enableAllProjectMcpServers` and `enabledMcpjsonServers` in committed settings are ignored in untrusted folders. User, managed and `--settings` approvals apply. Untracked local settings apply only after trust.
15. `/cd` applies the new directory's `.mcp.json`, behind approval (v2.1.246).

### Expansion

16. `${VAR}` and `${VAR:-default}` expand in `command`, `args`, `env`, `url`, `headers`. Unset without default loads unexpanded with a warning. An empty value counts as set.
17. Credential variables (`ANTHROPIC_API_KEY`, `ANTHROPIC_AUTH_TOKEN`, `AWS_BEARER_TOKEN_BEDROCK`, `HTTPS_PROXY`, `NPM_TOKEN` and others) MUST read as empty in a remote server's `url` and `headers`, ignoring defaults. A debug line says `never expanded toward a remote server`. Base URLs like `ANTHROPIC_BASE_URL` still expand unless they embed a credential.
18. `/mcp` and CLI output show references, not values (v2.1.268).

### Startup and availability

19. Servers MUST connect in the background by default (v2.1.117 for concurrency). `MCP_SERVER_CONNECTION_BATCH_SIZE` (3), `MCP_REMOTE_SERVER_CONNECTION_BATCH_SIZE` (20), `MCP_TIMEOUT` (30 s), `MCP_CONNECT_TIMEOUT_MS` (5 s).
20. `alwaysLoad: true` makes startup wait, capped at 5 s, unless a valid `cached` entry supplies the tools. `MCP_CONNECTION_NONBLOCKING=0` waits for all.
21. The first non-interactive turn waits up to about 2 s for connecting servers (`CLAUDE_CODE_MCP_STARTUP_WAIT_MS`, v2.1.274). It still waits up to 2 s for servers named by `--allowedTools` or an `mcp_tool` hook even at `0` (v2.1.284). HTTP and SSE `resources/list` is not awaited (v2.1.292).
22. `resources/templates/list` is deferred to first `@` (v2.1.116).
23. With tool search, a wait for a connecting server happens inside `ToolSearch`. Without it, the model uses `WaitForMcpServers`, which appears only when tool search is disabled. A Foundry deployment on Azure starts on the tool-search path. A request adding `WaitForMcpServers` during a reconnect invalidates the prompt cache once.
24. With tool search, servers finishing mid-turn have tool names listed on the next request in that turn. On resume, a call to a still-connecting tool MUST be held up to 10 s on the first attempt; else `No such tool available`.
25. With tool search, the model is told of failed servers and their errors. Bedrock, Vertex, Foundry and telemetry-off sessions were improved at v2.1.247. Without tool search, it is not told.
26. A `-p` or SDK run with an unauthenticated server tells the model those tools are unavailable, when tool search is on.

### Discovery cache

27. A remote server used before may show `cached`, with tools from the cache and connection on first call. `MCP_DISCOVERY_CACHE` toggles it; default off unless rollout-enabled (before v2.1.238, on). Tuning: `MCP_DISCOVERY_CACHE_TTL_S` (900), `_MAX_STALE_S` (14400), `_STRIKES`. Disable and Clear authentication discard the entry. In cloud, an environment-variable setting reuses connector lists after restart (v2.1.285).

### Reconnection

28. Remote mid-session drops: five attempts with exponential backoff from 1 s. Interactive then marks failed with a notification (v2.1.273). `-p` and SDK continue without tools; on transient errors HTTP and SSE keep retrying for about half an hour; auth failures stop.
29. HTTP and SSE first connect: three retries on transient errors (v2.1.121), not stdio, `ws`, auth or not-found, nor a proxy 403 (v2.1.290). A `headersHelper`-only `Authorization` still retries.
30. Discovery requests retry three times on transient errors (v2.1.191), not auth, 4xx or timeouts.
31. Stdio: interactive marks failed, needing **Reconnect**. `-p` and SDK restart it on the next tool call after a mid-session exit. Failed plugin servers are skipped for 15 minutes.
32. `/mcp reconnect all` retries failed and unauthenticated servers (v2.1.284).
33. `list_changed` refreshes the tool, prompt and resource lists interactively; only tools in `-p` and SDK. A failed refresh keeps prior lists.

### Limits and tool handling

34. Tool timeout: per-server `timeout` (ms, at least 1000), else `MCP_TOOL_TIMEOUT` (about 28 hours). HTTP, SSE and connector requests also have a per-request timer to first byte (60 s default). Progress does not extend the wall-clock limit.
35. Idle timeout: 5 minutes remote, 30 minutes stdio, excluding IDE and SDK servers; `CLAUDE_CODE_MCP_TOOL_IDLE_TIMEOUT`, `0` disables. Per-server `timeout` is a floor.
36. Main-conversation calls over 2 minutes MUST move to a background task (v2.1.212; `CLAUDE_CODE_MCP_AUTO_BACKGROUND_MS`, `0` disables). Not for subagents, IDE servers, or non-interactive runs unless `CLAUDE_AUTO_BACKGROUND_TASKS=1`, and deferred during an open elicitation. Stopping cancels the call, without guaranteeing server-side stop.
37. Output: warn at 10,000 tokens; `MAX_MCP_OUTPUT_TOKENS` (25,000). Successful results over the limit, or text over 50,000 characters, are saved to `tool-results` and replaced by a path. `_meta["anthropic/maxResultSizeChars"]` raises the threshold up to 500,000 (v2.1.91). Error text over about 11,000 keeps first and last 5,000. HTTP, SSE and `ws` responses over 16 MiB fail (v2.1.295 for `ws`).
38. Images display inline and are also saved to a file (v2.1.283).
39. Root `anyOf`, `oneOf`, `allOf` schemas are flattened with an explanatory description. Tools with invalid property names or schemas are excluded when flags are available. An API-refused schema is resent parameterless (v2.1.300). Tools with full names over 128 characters are omitted.
40. `_meta["anthropic/requiresUserInteraction"]: true` forces a prompt on every call, in all modes; `dontAsk` denies; hooks cannot allow; `--permission-prompt-tool` allow converts to deny.
41. `idempotentHint` or `readOnlyHint` lets a call pending at connection close repeat once on HTTP or connectors. `readOnlyHint` runs in parallel with other read-only calls.
42. Allow rules reach only the named server: `mcp__a` does not allow `a__b` or `a_` (v2.1.299).

### Tool search

43. Default on: MCP tools defer, with names and server instructions loaded up front. No per-server cap.
44. Models: Opus 4, Sonnet 4, Haiku 4.5 and later; on Agent Platform, 4.5 generation and later. Earlier models load upfront regardless. Foundry on Azure rejects it server-side and falls back. `CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS` and HIPAA configurations keep it off.
45. Behind `ANTHROPIC_BASE_URL` gateways it is on by default (v2.1.304), with a retry without tool search after an unrecognized 400 or 422 (v2.1.305).
46. Limits: 4,096 characters for instructions and upfront descriptions (v2.1.296), 16,384 for searched descriptions (v2.1.295); search matches only within the shorter limit. `CLAUDE_CODE_MAX_MCP_DESCRIPTION_LENGTH` replaces both (v2.1.280). Some `api.anthropic.com` servers are exempt (v2.1.299).
47. Server `alwaysLoad: true` exempts it. `false` defers everything including author-marked tools (v2.1.287). Tool `_meta["anthropic/alwaysLoad"]`: `true` loads upfront; `false` stays deferred under a config `alwaysLoad: true` for `--mcp-config`, SDK or plugin servers (v2.1.285).

### Resources

48. `@server:protocol://path` attaches resources; `@` autocomplete lists them fuzzily. List and read tools are provided when supported. `ui://` or `text/html;profile=mcp-app` entries are hidden, though readable by URI (v2.1.281).

### Prompts

49. Prompts appear as `/server:prompt (MCP)`; `/mcp__server__prompt` also runs. Arguments split on whitespace. They fire `UserPromptExpansion` with `mcp_prompt`.
50. Servers named `anthropic-skills` or `claude-ai` list no prompts or skills.

### Elicitation

51. Form mode shows a dialog. URL mode asks to open a link, passing it to the system URL handler, with a cap of about 8,000 characters counting each escaped character four times; over the cap, the user can only decline.
52. Capabilities: `{form:{}, url:{}}` on 2026-07-28 connections (v2.1.281), and earlier-revision connections to configured servers (v2.1.287). Otherwise bare `{}`. `bareElicitationCapability: true` is the per-server opt-out.
53. A server unable to report completion leaves the call waiting on "I'm done, continue" (v2.1.288).
54. Hooks: see `Elicitation`, `ElicitationResult` in [hook-events.md](hook-events.md). A timed-out call with an unanswered elicitation tells the model no answer came (v2.1.310).

## Configuration & interfaces

| Command | Purpose |
| :- | :- |
| `claude mcp add`, `add-json`, `add-from-claude-desktop`, `list`, `get`, `remove`, `reset-project-choices`, `serve`, `login`, `logout` | Management |
| `/mcp` | Status, auth, tools, toggle, reconnect |

`claude mcp list` statuses include `✔ Connected`, `! Needs authentication`, `✘ Failed to connect`, `⏸ Pending approval`, `✘ Rejected`, `⊘ Disabled for this project`, `✘ Blocked by enterprise managed policy`. An empty `url` shows `not configured` (v2.1.208). Plugin stdio and `ws` values are redacted by `claude mcp get` (v2.1.285).

| Key | Meaning |
| :- | :- |
| `disabledMcpServers` | Per-project opt-out, in `~/.claude.json` |
| `enabledMcpServers` | Opt-in for default-off built-ins such as `computer-use` |
| `enabledMcpjsonServers`, `disabledMcpjsonServers`, `enableAllProjectMcpServers` | `.mcp.json` approval |
| `disableClaudeAiConnectors`, `ENABLE_CLAUDEAI_MCP_SERVERS` | Fetched connectors |

Reserved names: `workspace`, `claude-in-chrome`, `computer-use`, `Claude Preview`, `Claude Browser`, and `widgets` in cloud and runner sessions (v2.1.285). Names from `claude mcp` use letters, digits, `-`, `_`.

## Failure modes & edge cases

- `/doctor` and `/mcp` warn on hidden whitespace (v2.1.219), same name with different endpoints, and missing variables.
- `MCP server "all" not found` before v2.1.284.
- `connection closed before the tool call was answered`.
- Removing a remote server deletes local tokens but does not revoke; `claude mcp logout` first.

## Changes since the snapshot

- v2.1.91: `maxResultSizeChars`.
- v2.1.118: `mcp_tool` hooks.
- v2.1.121: `alwaysLoad`, retries, connector dedupe.
- v2.1.128: `workspace` reserved.
- v2.1.203: `roots/list` extension.
- v2.1.212: auto-backgrounding.
- v2.1.232: v2 runtime.
- v2.1.259: `managedMcpServers`.
- v2.1.274: `sdk` entries skipped; startup wait variable.
- v2.1.281: URL elicitation.
- v2.1.287: earlier-revision URL prompts; `alwaysLoad: false`.
- v2.1.292: stdio negotiation default.
- v2.1.295, v2.1.296: description limits.
- v2.1.299: allow rules scoped, redirects not followed through session proxies.
- v2.1.304: tool search default behind gateways.

## Open questions

- Exact per-request timer formula is truncated in the sections reviewed.
- Full reserved-name list beyond those named.
- Rollout criteria for the discovery cache are not public.
