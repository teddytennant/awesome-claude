# Environment variables reference

**Status:** shipped
**Provenance:** both
**Sources:** docs `env-vars`, `settings-reference`, `settings`; `comparison/env-vars.md`; changelog versions cited below

## Purpose

Inventory of all 424 variable names in the public documentation at 2.1.314, grouped by topic. This is a lookup table, so it exceeds the usual length range. Behaviour of each feature is specified in its own spec.

Safety-check rows are inventory only and give no usage guidance. The snapshot also read 484 further names, most of them internal; those are not listed, per the name-level comparison.

## Behaviour

### Value parsing

1. On/off variables MUST accept `1`, `true`, `yes`, `on` and `0`, `false`, `no`, `off`, in any casing.
2. `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC`, `DISABLE_TELEMETRY`, `DISABLE_ERROR_REPORTING`, `CLAUDE_CODE_TMUX_TRUECOLOR` and `IS_DEMO` read presence only: any non-empty value, including `0`, turns them on.
3. `FORCE_HYPERLINK` is numeric: only `0` turns it off, and `false` turns it on.
4. Numeric variables MUST accept scientific notation and digit separators (`2e3`, `64_000`), unless the variable says plain digits only.

### Setting and precedence

5. Shell values are read at startup. Settings `env` values reapply to a running session on save, except for features reading variables once at startup. Removing one does not unset it until the next launch.
6. A settings `env` entry overwrites the inherited shell value in most sessions. When Claude Desktop or a self-hosted runner built the launch environment, that environment wins, and the debug log names ignored variables.
7. Between files, `env` follows settings precedence. An empty string cancels a shell export for provider selection, and subprocesses inherit the empty value.
8. Variable versus flag or setting precedence is per variable. `ANTHROPIC_MODEL` is overridden by `--model` and `/model`; `CLAUDE_CODE_EFFORT_LEVEL` overrides `--effort` and `/effort`.
9. `NO_COLOR` and `FORCE_COLOR` in `env` reach subprocesses only.

### Restrictions on `env` blocks

10. Project and local settings MUST NOT set: path-choosing variables (`CLAUDE_CONFIG_DIR`, `CLAUDE_CODE_TMPDIR`, `HOME`, `TMPDIR`, `TMP`, `TEMP`, `XDG_*`); Windows program and configuration variables (`SystemRoot`, `ComSpec`, `ProgramData`, `LOCALAPPDATA`, `PATHEXT`, `PSModulePath`, `ProgramFiles*`); session-content exporters (`OTEL_LOG_RAW_API_BODIES`, the beta tracing pair); telemetry enablers and destinations, including the enhanced-telemetry pair and per-signal OTLP forms; `CLAUDE_CODE_PROCESS_WRAPPER`, `CLAUDE_CODE_SYNC_SKILLS`, `CLAUDE_CODE_SYNC_PLUGINS`, `CLAUDE_CODE_PLUGIN_CACHE_DIR`, `CLAUDE_CODE_PLUGIN_SEED_DIR`; `CLAUDE_AX_*`; `CLAUDE_CODE_USER_DIALOG_TIMEOUT_MS`; `CLAUDE_CODE_DISABLE_ATTACHMENTS`; `CLAUDE_CODE_DISABLE_FILE_MENTIONS`.
11. Off values still apply from those files: `none` for the three exporter selectors, and an off value for the three content variables. Ignored telemetry variables are reported at interactive startup, in `/status` and in `claude doctor`, by name only.
12. Ignored from every file: identity variables such as `CLAUDE_CODE_REMOTE` and `CLAUDE_CODE_ACCOUNT_UUID`; `CLAUDE_CODE_MESSAGING_SOCKET`, `CLAUDE_CODE_MESSAGING_TOKEN`.
13. Launch environment only: `CLAUDE_CODE_PROJECT_DIR_NAME`, `CLAUDE_CODE_RESTRICTED`, the `rm` and PowerShell check variables, `CLAUDE_CODE_EVEN_MORE_DANGEROUSLY_SKIP_PERMISSIONS`, `CLAUDE_CODE_WARN_DISK_FREE_GIB`, `CLAUDE_CODE_WARN_MEMORY_FREE_GIB`.
14. `CLAUDE_CODE_PROVIDER_MANAGED_BY_HOST` makes provider, endpoint and auth variables in settings files ignored.

### Subprocess scrub

15. With `CLAUDE_CODE_SUBPROCESS_ENV_SCRUB=1`, credentials MUST be removed from Bash, hook and stdio MCP environments, identified by name or value shape. The Claude Code process keeps its own.

| Example | Result |
|---|---|
| `ANTHROPIC_API_KEY`, `AWS_SECRET_ACCESS_KEY`, `CLAUDE_CONFIG_DIR` | Removed |
| `NPM_TOKEN`, `DB_PASSWORD` | Removed, by name |
| `DATABASE_URL` with a password | Removed, by value |
| `PIP_INDEX_URL`, `NPM_CONFIG_REGISTRY` with a password | Kept, credentials cut from the URL |
| `GITHUB_TOKEN`, `GH_TOKEN`, `GH_ENTERPRISE_TOKEN`, `GITHUB_ENTERPRISE_TOKEN` | Left in place |
| `HTTP_PROXY`, `HTTPS_PROXY`, `GIT_CONFIG_*` | Left in place |

16. On Linux the scrub also runs Bash in an isolated PID namespace.

### Feature-flag fetching

17. Fetching is skipped under `DISABLE_GROWTHBOOK`, `DISABLE_TELEMETRY`, `DO_NOT_TRACK`, `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC`, on third-party providers unless a host sets `CLAUDE_CODE_PROVIDER_MANAGED_BY_HOST`, and on a Claude apps gateway.
18. Without it, features that need flags are unavailable, including Remote Control under two of those variables, `/import`, `/skill-doctor`, skill and plugin sync, the advisor, MCP tasks, artifact comments, and idle compaction. A flag-gated feature can also be missing in the first session after install or upgrade.

## Configuration & interfaces

Legend. **Snap**: `yes` name found in the 2026-03-31 snapshot; `new` not found. This is a name match, and it says nothing about behaviour being unchanged. **Since**: documented minimum version, where the row states one for the variable as a whole. Rows where the docs state a minimum version that has no changelog heading show `–`.

### Authentication and credentials (23)

| Variable | Snap | Since | Behaviour |
|---|---|---|---|
| `ANTHROPIC_API_KEY` | yes | – | API key sent as `X-Api-Key`; overrides a subscription, always in `-p`, after one approval interactively. |
| `ANTHROPIC_AUTH_TOKEN` | yes | – | Value for `Authorization`, prefixed `Bearer `. |
| `ANTHROPIC_AWS_API_KEY` | new | – | Claude Platform on AWS workspace key; beats SigV4. |
| `ANTHROPIC_FEDERATION_RULE_ID` | new | – | Workload Identity Federation rule; with the organisation ID, outranks `/login`. |
| `ANTHROPIC_FOUNDRY_API_KEY` | yes | – | Foundry API key. |
| `ANTHROPIC_FOUNDRY_AUTH_TOKEN` | new | 2.1.203 | Foundry bearer token; beats the API key and Azure chain. |
| `ANTHROPIC_ORGANIZATION_ID` | new | – | Federation organisation ID. |
| `ANTHROPIC_PROFILE` | new | – | Named Anthropic profile to authenticate with. |
| `ANTHROPIC_WORKSPACE_ID` | new | – | Target workspace for a federation rule scoped to several. |
| `AWS_BEARER_TOKEN_BEDROCK` | yes | – | Bedrock API key. |
| `AWS_SECRET_ACCESS_KEY` | yes | – | Standard AWS credential; named by the subprocess scrub, which removes it. |
| `CLAUDE_CODE_API_KEY_HELPER_TTL_MS` | yes | – | Refresh interval for `apiKeyHelper` credentials. |
| `CLAUDE_CODE_AWS_CHAIN_RESOLVE_TIMEOUT_MS` | new | 2.1.207 | Wait for the AWS default chain, default 60000. |
| `CLAUDE_CODE_DISABLE_AUTH_REFRESH_LOCK` | new | 2.1.286 | Run `gcpAuthRefresh`/`awsAuthRefresh` in this process, not waiting on another. |
| `CLAUDE_CODE_OAUTH_REFRESH_TOKEN` | yes | – | Refresh token exchanged by `claude auth login`; needs scopes. |
| `CLAUDE_CODE_OAUTH_SCOPES` | yes | – | Space-separated scopes for the refresh token. |
| `CLAUDE_CODE_OAUTH_TOKEN` | yes | – | OAuth access token for automation; beats keychain credentials. |
| `CLAUDE_CODE_SKIP_ANTHROPIC_AWS_AUTH` | new | – | Skip client auth for Claude Platform on AWS, for signing gateways. |
| `CLAUDE_CODE_SKIP_AWS_CRED_CACHE` | new | 2.1.207 | Resolve the AWS chain on every request. |
| `CLAUDE_CODE_SKIP_BEDROCK_AUTH` | yes | – | Skip AWS auth for Bedrock. |
| `CLAUDE_CODE_SKIP_FOUNDRY_AUTH` | yes | – | Skip Azure auth; ignored when a Foundry key or token is set. |
| `CLAUDE_CODE_SKIP_MANTLE_AUTH` | new | – | Skip AWS auth for Mantle. |
| `CLAUDE_CODE_SKIP_VERTEX_AUTH` | yes | – | Skip Google auth for Agent Platform. |

### Providers and endpoints (24)

| Variable | Snap | Since | Behaviour |
|---|---|---|---|
| `ANTHROPIC_AWS_BASE_URL` | new | – | Claude Platform on AWS endpoint; defaults to a regional host. |
| `ANTHROPIC_AWS_WORKSPACE_ID` | new | – | Required workspace header for Claude Platform on AWS. |
| `ANTHROPIC_BASE_URL` | yes | – | API endpoint override; disables Remote Control on non-Anthropic hosts since v2.1.196. |
| `ANTHROPIC_BEDROCK_BASE_URL` | yes | – | Bedrock endpoint override. |
| `ANTHROPIC_BEDROCK_MANTLE_BASE_URL` | new | – | Mantle endpoint override. |
| `ANTHROPIC_BEDROCK_REGION_PREFIX` | new | – | Preferred cross-region inference prefix; ignored in GovCloud. |
| `ANTHROPIC_BEDROCK_SERVICE_TIER` | new | – | `default`, `flex` or `priority`, sent as a header. |
| `ANTHROPIC_FOUNDRY_BASE_URL` | yes | – | Full Foundry base URL. |
| `ANTHROPIC_FOUNDRY_RESOURCE` | yes | – | Foundry resource name; URLs refused. |
| `ANTHROPIC_VERTEX_BASE_URL` | yes | – | Agent Platform endpoint override. |
| `ANTHROPIC_VERTEX_PROJECT_ID` | yes | – | GCP project for Agent Platform. |
| `CLAUDE_CODE_DISABLE_BEDROCK_CONTENT_TYPE_DEFAULT` | new | 2.1.239 | Do not treat a missing Bedrock streaming content type as the binary event stream. |
| `CLAUDE_CODE_DISABLE_BEDROCK_CONTENT_TYPE_GUARD` | new | 2.1.208 | Skip the Bedrock streaming content-type check. |
| `CLAUDE_CODE_DISABLE_MODEL_ACCESS_FALLBACK` | new | 2.1.285 | Do not switch to an older model when Bedrock or Agent Platform access is lost. |
| `CLAUDE_CODE_ENABLE_GATEWAY_MODEL_DISCOVERY` | new | – | Fill `/model` from a gateway's `/v1/models`. |
| `CLAUDE_CODE_GATEWAY_HINT_HEADERS` | new | 2.1.273 | `1` sends gateway hint headers on proxies and third-party providers; `0` stops them everywhere. |
| `CLAUDE_CODE_GATEWAY_MODEL_DISCOVERY_TIMEOUT_MS` | new | 2.1.269 | Discovery timeout, default 3000, plain digits. |
| `CLAUDE_CODE_PROVIDER_MANAGED_BY_HOST` | yes | – | Set by embedding hosts; ignores provider, endpoint and auth variables in settings files, and takes host model configuration. |
| `CLAUDE_CODE_SKIP_MODEL_ACCESS_MEMORY` | new | 2.1.285 | Do not remember models found uninvokable for up to a day. |
| `CLAUDE_CODE_USE_ANTHROPIC_AWS` | new | – | Use Claude Platform on AWS. |
| `CLAUDE_CODE_USE_BEDROCK` | yes | – | Use Amazon Bedrock. |
| `CLAUDE_CODE_USE_FOUNDRY` | yes | – | Use Microsoft Foundry. |
| `CLAUDE_CODE_USE_MANTLE` | new | – | Use the Bedrock Mantle endpoint. |
| `CLAUDE_CODE_USE_VERTEX` | yes | – | Use Google Cloud's Agent Platform. |

### Model selection (35)

| Variable | Snap | Since | Behaviour |
|---|---|---|---|
| `ANTHROPIC_CUSTOM_MODEL_OPTION` | yes | – | Extra `/model` picker entry. |
| `ANTHROPIC_CUSTOM_MODEL_OPTION_DESCRIPTION` | yes | – | Description for the custom entry. |
| `ANTHROPIC_CUSTOM_MODEL_OPTION_NAME` | yes | – | Display name for the custom entry. |
| `ANTHROPIC_CUSTOM_MODEL_OPTION_SUPPORTED_CAPABILITIES` | new | – | Capabilities of the custom entry. |
| `ANTHROPIC_DEFAULT_FABLE_MODEL` | new | – | Target of `fable`; also recognised as Fable for automatic fallback on third-party providers. |
| `ANTHROPIC_DEFAULT_FABLE_MODEL_DESCRIPTION` | new | – | `/model` picker description for the pinned model of that family. |
| `ANTHROPIC_DEFAULT_FABLE_MODEL_NAME` | new | – | `/model` picker display name for the pinned model of that family. |
| `ANTHROPIC_DEFAULT_FABLE_MODEL_SUPPORTED_CAPABILITIES` | new | – | Comma-separated capabilities of the pinned model. |
| `ANTHROPIC_DEFAULT_HAIKU_MODEL` | yes | – | Target of `haiku`; used for background work. |
| `ANTHROPIC_DEFAULT_HAIKU_MODEL_DESCRIPTION` | yes | – | `/model` picker description for the pinned model of that family. |
| `ANTHROPIC_DEFAULT_HAIKU_MODEL_NAME` | yes | – | `/model` picker display name for the pinned model of that family. |
| `ANTHROPIC_DEFAULT_HAIKU_MODEL_SUPPORTED_CAPABILITIES` | yes | – | Comma-separated capabilities of the pinned model. |
| `ANTHROPIC_DEFAULT_MODEL` | new | – | Default for new sessions; applies only when no file sets `model`. |
| `ANTHROPIC_DEFAULT_OPUS_MODEL` | yes | – | Target of `opus`, and `opusplan` in plan mode. |
| `ANTHROPIC_DEFAULT_OPUS_MODEL_DESCRIPTION` | yes | – | `/model` picker description for the pinned model of that family. |
| `ANTHROPIC_DEFAULT_OPUS_MODEL_NAME` | yes | – | `/model` picker display name for the pinned model of that family. |
| `ANTHROPIC_DEFAULT_OPUS_MODEL_SUPPORTED_CAPABILITIES` | yes | – | Comma-separated capabilities of the pinned model. |
| `ANTHROPIC_DEFAULT_SONNET_MODEL` | yes | – | Target of `sonnet`, and `opusplan` outside plan mode. |
| `ANTHROPIC_DEFAULT_SONNET_MODEL_DESCRIPTION` | yes | – | `/model` picker description for the pinned model of that family. |
| `ANTHROPIC_DEFAULT_SONNET_MODEL_NAME` | yes | – | `/model` picker display name for the pinned model of that family. |
| `ANTHROPIC_DEFAULT_SONNET_MODEL_SUPPORTED_CAPABILITIES` | yes | – | Comma-separated capabilities of the pinned model. |
| `ANTHROPIC_MODEL` | yes | – | Model setting name; `--model` and `/model` override it. |
| `ANTHROPIC_SMALL_FAST_MODEL` | yes | – | Deprecated Haiku-class background model. |
| `ANTHROPIC_SMALL_FAST_MODEL_AWS_REGION` | yes | – | Region for the Haiku-class model on Bedrock or Mantle. |
| `CLAUDE_CODE_AUTO_MODE_MODEL` | yes | 2.1.302 | Model for auto mode classifier requests. |
| `CLAUDE_CODE_DISABLE_ADVISOR_TOOL` | yes | – | Disable the advisor tool; `--advisor` is accepted and ignored. |
| `CLAUDE_CODE_DISABLE_FAST_MODE` | yes | – | Disable fast mode. |
| `CLAUDE_CODE_DISABLE_LEGACY_MODEL_REMAP` | yes | – | Keep Opus 4 and 4.1 from remapping on the Anthropic API. |
| `CLAUDE_CODE_DISABLE_REFUSAL_FALLBACK` | new | – | Turn off automatic model switch on a safety flag. |
| `CLAUDE_CODE_ENABLE_OPUS_4_7_FAST_MODE` | new | – | Removed in v2.1.142. |
| `CLAUDE_CODE_OPUS_4_6_FAST_MODE_OVERRIDE` | new | – | Removed in v2.1.160, no-op. |
| `CLAUDE_CODE_SKIP_FAST_MODE_NETWORK_ERRORS` | yes | – | Treat a failed availability check as available. |
| `CLAUDE_CODE_SKIP_FAST_MODE_ORG_CHECK` | new | – | Skip the client availability check; the API still enforces. |
| `CLAUDE_CODE_SUBAGENT_MODEL` | yes | – | Default model for subagents, teammates and workflow agents. |
| `CLAUDE_CODE_SUBAGENT_MODEL_FORCE` | new | 2.1.257 | Force one model onto those agents. |

### Agent Platform regions (20)

| Variable | Snap | Since | Behaviour |
|---|---|---|---|
| `VERTEX_REGION_CLAUDE_3_5_HAIKU` | yes | – | Agent Platform region override for that model. |
| `VERTEX_REGION_CLAUDE_3_5_SONNET` | yes | – | Agent Platform region override for that model. |
| `VERTEX_REGION_CLAUDE_3_7_SONNET` | yes | – | Agent Platform region override for that model. |
| `VERTEX_REGION_CLAUDE_4_0_OPUS` | yes | – | Agent Platform region override for that model. |
| `VERTEX_REGION_CLAUDE_4_0_SONNET` | yes | – | Agent Platform region override for that model. |
| `VERTEX_REGION_CLAUDE_4_1_OPUS` | yes | – | Agent Platform region override for that model. |
| `VERTEX_REGION_CLAUDE_4_5_OPUS` | new | – | Agent Platform region override for that model. |
| `VERTEX_REGION_CLAUDE_4_5_SONNET` | yes | – | Agent Platform region override for that model. |
| `VERTEX_REGION_CLAUDE_4_6_OPUS` | new | – | Agent Platform region override for that model. |
| `VERTEX_REGION_CLAUDE_4_6_SONNET` | yes | – | Agent Platform region override for that model. |
| `VERTEX_REGION_CLAUDE_4_7_OPUS` | new | – | Agent Platform region override for that model. |
| `VERTEX_REGION_CLAUDE_4_8_OPUS` | new | – | Agent Platform region override for that model. |
| `VERTEX_REGION_CLAUDE_5_5_OPUS` | new | 2.1.280 | Agent Platform region override for that model. |
| `VERTEX_REGION_CLAUDE_5_5_SONNET` | new | 2.1.284 | Agent Platform region override for that model. |
| `VERTEX_REGION_CLAUDE_5_OPUS` | new | 2.1.219 | Agent Platform region override for that model. |
| `VERTEX_REGION_CLAUDE_5_SONNET` | new | 2.1.197 | Agent Platform region override for that model. |
| `VERTEX_REGION_CLAUDE_FABLE_5` | new | 2.1.170 | Agent Platform region override for that model. |
| `VERTEX_REGION_CLAUDE_FABLE_5_1` | new | 2.1.257 | Agent Platform region override for that model. |
| `VERTEX_REGION_CLAUDE_HAIKU_4_5` | yes | – | Agent Platform region override for that model. |
| `VERTEX_REGION_CLAUDE_HAIKU_5_5` | new | 2.1.293 | Agent Platform region override for that model. |

### Effort, thinking and output (7)

| Variable | Snap | Since | Behaviour |
|---|---|---|---|
| `CLAUDE_CODE_ALWAYS_ENABLE_EFFORT` | yes | – | Send effort even for unrecognised model IDs. |
| `CLAUDE_CODE_DISABLE_ADAPTIVE_THINKING` | yes | – | Fixed thinking budget on Opus 4.6 and Sonnet 4.6. |
| `CLAUDE_CODE_DISABLE_THINKING` | yes | – | Omit the `thinking` parameter, for proxies. |
| `CLAUDE_CODE_EFFORT_LEVEL` | yes | – | Effort level; beats `--effort`, `/effort` and settings; `maxEffortLevel` still caps; `auto`/`unset` sends none. |
| `CLAUDE_CODE_MAX_OUTPUT_TOKENS` | yes | – | Max output for most requests, lowered to the model's cap. |
| `DISABLE_INTERLEAVED_THINKING` | yes | – | Drop the interleaved-thinking beta header. |
| `MAX_THINKING_TOKENS` | yes | – | Fixed thinking budget, capped below max output, floor 1024. |

### API requests, retries and streaming (26)

| Variable | Snap | Since | Behaviour |
|---|---|---|---|
| `ANTHROPIC_BETAS` | yes | – | Extra `anthropic-beta` values. |
| `ANTHROPIC_CUSTOM_HEADERS` | yes | – | Newline-separated `Name: Value` request headers. |
| `API_FORCE_IDLE_TIMEOUT` | new | – | Override the 5-minute stream idle timeout: `0` off, `1` on everywhere. |
| `API_TIMEOUT_MS` | yes | – | Per-attempt time to response headers, default 600000. |
| `CLAUDE_BYTE_STREAM_IDLE_TIMEOUT_MS` | new | 2.1.210 | Byte-level watchdog timeout, clamped 10 s to 30 min. |
| `CLAUDE_CODE_ATTRIBUTION_HEADER` | yes | – | `0` omits the attribution block from the system prompt. |
| `CLAUDE_CODE_CONNECT_TIMEOUT_MS` | new | – | Removed in v2.1.186, no-op. |
| `CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS` | yes | – | Strip pre-release beta headers and paired fields. |
| `CLAUDE_CODE_DISABLE_NONSTREAMING_FALLBACK` | yes | – | No non-streaming fallback after a stream failure. |
| `CLAUDE_CODE_DISABLE_STRUCTURED_OUTPUTS` | new | 2.1.288 | Stop sending structured-output fields. |
| `CLAUDE_CODE_ENABLE_FINE_GRAINED_TOOL_STREAMING` | yes | – | Control streaming of tool inputs. |
| `CLAUDE_CODE_EXTRA_BODY` | yes | – | JSON merged into every request body. |
| `CLAUDE_CODE_GZIP_REQUEST_BODIES` | new | – | `0` turns off gzip of large request bodies. |
| `CLAUDE_CODE_MAX_RETRIES` | yes | – | Retry count, default 10, capped at 15. |
| `CLAUDE_CODE_NONSTREAMING_TIMEOUT_RETRIES` | new | 2.1.285 | Retries of a timed-out non-streaming request. |
| `CLAUDE_CODE_OVERLOADED_RETRY_BASE_DELAY_MS` | new | 2.1.292 | 529 backoff start, 500–32000. |
| `CLAUDE_CODE_OVERLOADED_RETRY_MAX_DELAY_MS` | new | 2.1.296 | 529 backoff ceiling, 32000–64000. |
| `CLAUDE_CODE_RETRY_WATCHDOG` | new | 2.1.186 | Retry 429 and 529 indefinitely for unattended runs. |
| `CLAUDE_CODE_RETRY_WATCHDOG_MAX_WAIT_MS` | new | 2.1.295 | Per-request wait cap for the watchdog. |
| `CLAUDE_CODE_RETRY_WATCHDOG_USAGE_LIMIT_RECHECK_MS` | new | 2.1.305 | Minimum interval between usage-limit rechecks. |
| `CLAUDE_ENABLE_BYTE_WATCHDOG` | new | – | Force the byte-level watchdog on or off; `0` also drops the first-byte deadline. |
| `CLAUDE_ENABLE_BYTE_WATCHDOG_BEDROCK` | new | – | Enable the byte watchdog on Bedrock. |
| `CLAUDE_ENABLE_STREAM_WATCHDOG` | yes | – | Force the event-level watchdog on or off. |
| `CLAUDE_STREAM_FIRST_BYTE_TIMEOUT_MS` | new | – | First-byte deadline for streaming. |
| `CLAUDE_STREAM_IDLE_TIMEOUT_MS` | yes | – | Stream watchdog timeout; minimum 300000 when set. |
| `MAX_STRUCTURED_OUTPUT_RETRIES` | yes | – | Attempts for `--json-schema` and workflow structured output. |

### Prompt caching (10)

| Variable | Snap | Since | Behaviour |
|---|---|---|---|
| `CLAUDE_CODE_PROMPT_CACHE_TTL` | new | – | Main-conversation TTL, `5m` or `1h`. |
| `CLAUDE_CODE_SUBAGENT_PROMPT_CACHE_TTL` | new | – | TTL outside the main conversation. |
| `DISABLE_PROMPT_CACHING` | yes | – | Disable caching for all models. |
| `DISABLE_PROMPT_CACHING_FABLE` | new | – | Disable for Fable models. |
| `DISABLE_PROMPT_CACHING_HAIKU` | yes | – | Disable for the default Haiku model, wherever it runs. |
| `DISABLE_PROMPT_CACHING_OPUS` | yes | – | Disable for the default Opus model. |
| `DISABLE_PROMPT_CACHING_SONNET` | yes | – | Disable for the default Sonnet model. |
| `ENABLE_PROMPT_CACHING_1H` | new | – | Request 1-hour TTL. |
| `ENABLE_PROMPT_CACHING_1H_BEDROCK` | yes | – | Deprecated form of the above. |
| `FORCE_PROMPT_CACHING_5M` | new | – | Force 5-minute TTL; beats all TTL controls. |

### Context and compaction (10)

| Variable | Snap | Since | Behaviour |
|---|---|---|---|
| `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE` | yes | – | Trigger percentage, 1–100; can only lower. |
| `CLAUDE_CODE_AUTO_COMPACT_WINDOW` | yes | – | Auto-compact window, 100000–1000000; `k`/`M` suffix since v2.1.304. |
| `CLAUDE_CODE_DISABLE_1M_CONTEXT` | yes | – | Remove `[1m]` variants and hold models to 200K. |
| `CLAUDE_CODE_DISABLE_UNKNOWN_MODEL_WINDOW_ENFORCEMENT` | new | 2.1.223 | Unrecognised IDs compact only after an API rejection. |
| `CLAUDE_CODE_FILE_READ_MAX_OUTPUT_TOKENS` | yes | – | File read token limit, default 25000. |
| `CLAUDE_CODE_IDLE_COMPACT_MIN_TOKENS` | new | 2.1.290 | Idle compaction threshold, default 200000, minimum 100000. |
| `CLAUDE_CODE_MAX_CONTEXT_TOKENS` | yes | – | Context window assumed for the model; applicability depends on the ID. |
| `DISABLE_AUTO_COMPACT` | yes | – | Turn off automatic and idle compaction. |
| `DISABLE_COMPACT` | yes | – | Turn off all compaction; from settings it can only turn off. |
| `SLASH_COMMAND_TOOL_CHAR_BUDGET` | yes | – | Character budget for skill metadata, default 1% of window. |

### Memory and instructions (4)

| Variable | Snap | Since | Behaviour |
|---|---|---|---|
| `CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD` | yes | – | Load instruction files from `--add-dir` directories. |
| `CLAUDE_CODE_DISABLE_AUTO_MEMORY` | yes | – | `1` off; `0` forces on, even under `--bare`. |
| `CLAUDE_CODE_DISABLE_CLAUDE_MDS` | yes | – | Load no memory files, including auto memory. |
| `CLAUDE_CODE_NEW_INIT` | yes | – | Interactive `/init` flow. |

### Sessions, modes and storage (18)

| Variable | Snap | Since | Behaviour |
|---|---|---|---|
| `CLAUDE_CODE_DISABLE_FILE_CHECKPOINTING` | yes | – | Disable checkpoints; beats the setting. |
| `CLAUDE_CODE_ENABLE_AWAY_SUMMARY` | new | – | Force recaps on or off; beats setting and `/config`. |
| `CLAUDE_CODE_EXIT_AFTER_STOP_DELAY` | yes | – | Exit after idle for this many ms, for automation. |
| `CLAUDE_CODE_FORCE_SESSION_PERSISTENCE` | new | – | Persist even when launched inside another session. |
| `CLAUDE_CODE_PROJECT_DIR_NAME` | new | 2.1.234 | Name of the `projects/` directory; launch environment only; needs `CLAUDE_CONFIG_DIR`. |
| `CLAUDE_CODE_RESTRICTED` | new | 2.1.248 | Restricted mode; launch environment only. |
| `CLAUDE_CODE_RESUME_INTERRUPTED_TURN` | yes | – | Continue a mid-turn session automatically. |
| `CLAUDE_CODE_RESUME_INTERRUPTED_TURN_MAX_AGE_MS` | new | 2.1.211 | Maximum last-message age for that continuation. |
| `CLAUDE_CODE_RESUME_PROMPT` | new | – | Continuation message text. |
| `CLAUDE_CODE_RESUME_SHOWS_CUT_OFF_CALLS` | new | 2.1.309 | Keep interrupted calls, marked cut off. |
| `CLAUDE_CODE_SAFE_MODE` | new | – | Start with customisations disabled; managed policy still applies. |
| `CLAUDE_CODE_SIMPLE` | yes | – | Bare mode: minimal prompt and tools, no discovery. |
| `CLAUDE_CODE_SIMPLE_SYSTEM_PROMPT` | new | – | Choose full or shorter system prompt. |
| `CLAUDE_CODE_SKIP_PROMPT_HISTORY` | yes | – | Do not write history or transcripts. |
| `CLAUDE_CODE_STARTUP_FAILURE_RESULTS` | new | 2.1.274 | Write a stream-json result naming a startup refusal. |
| `CLAUDE_CODE_TASK_LIST_ID` | yes | – | Shared task list across sessions. |
| `CLAUDE_CODE_TRANSCRIPT_LOCAL_GC` | new | 2.1.287 | Trim `-p`/SDK transcripts after compaction. |
| `CLAUDE_CONFIG_DIR` | yes | – | Configuration root; not settable from project or local `env`. |

### Agents, background work and workflows (33)

| Variable | Snap | Since | Behaviour |
|---|---|---|---|
| `CLAUDE_AGENT_SDK_DISABLE_BUILTIN_AGENTS` | yes | – | Remove built-in subagents in `-p`. |
| `CLAUDE_AGENT_SDK_MCP_NO_PREFIX` | yes | – | Skip the `mcp__` prefix on SDK server tools. |
| `CLAUDE_ASYNC_AGENT_STALL_TIMEOUT_MS` | new | – | Subagent stall timeout, default 600000. |
| `CLAUDE_AUTO_BACKGROUND_TASKS` | yes | – | Force automatic backgrounding of long agent tasks. |
| `CLAUDE_CODE_AUTO_BACKGROUND_WORKER_CHECKIN_SECONDS` | new | – | Removed in v2.1.283. |
| `CLAUDE_CODE_BG_TASKS_REPORT_RUNNING` | new | – | `0` reports idle at turn end despite background work. |
| `CLAUDE_CODE_DISABLE_AGENT_VIEW` | new | – | Turn off background agents and agent view. |
| `CLAUDE_CODE_DISABLE_BACKGROUND_TASKS` | yes | – | Remove `run_in_background` and automatic backgrounding. |
| `CLAUDE_CODE_DISABLE_BG_EXIT_HANDOFF` | new | 2.1.196 | Stop in-flight work rather than hand it to the next process. |
| `CLAUDE_CODE_DISABLE_BG_SHELL_PRESSURE_REAP` | new | 2.1.193 | Do not reap background shells under memory pressure. |
| `CLAUDE_CODE_DISABLE_CRON` | yes | – | Disable session-scoped scheduled tasks and `/loop`. |
| `CLAUDE_CODE_DISABLE_EXPLORE_PLAN_AGENTS` | new | 2.1.198 | Remove the Explore and Plan subagents. |
| `CLAUDE_CODE_DISABLE_WORKFLOWS` | new | – | Disable workflows. |
| `CLAUDE_CODE_EMIT_SESSION_STATE_EVENTS` | yes | – | Add `session_state_changed` messages to the stream. |
| `CLAUDE_CODE_ENABLE_TASKS` | yes | – | `0` selects legacy `TodoWrite`. |
| `CLAUDE_CODE_ENABLE_TODO_TOOLS` | new | 2.1.233 | Provide task tools on every model. |
| `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` | yes | – | Enable agent teams. |
| `CLAUDE_CODE_FORK_SUBAGENT` | new | – | Controls fork mode, on by default. |
| `CLAUDE_CODE_FORWARD_SUBAGENT_TEXT` | new | 2.1.211 | Emit subagent text in stream-json. |
| `CLAUDE_CODE_GOAL_CHECKIN_MINUTES` | new | 2.1.234 | Goal check-in delay, default 30, `0` off. |
| `CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS` | new | 2.1.217 | Concurrent subagent cap, default 20. |
| `CLAUDE_CODE_MAX_SUBAGENTS_PER_SESSION` | new | – | Removed in v2.1.224, no-op. |
| `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH` | new | 2.1.217 | Nesting depth, default 3. |
| `CLAUDE_CODE_MAX_TURNS` | new | – | Default turn cap; `--max-turns` wins. |
| `CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS` | new | – | Idle wait for background work after a `-p` run, default 600000. |
| `CLAUDE_CODE_PROCESS_WRAPPER` | new | 2.1.208 | Launcher argv prefix for processes from Claude's binary. |
| `CLAUDE_CODE_SESSIONEND_HOOKS_TIMEOUT_MS` | yes | – | SessionEnd hook budget, default 1.5 s, raised to the highest per-hook timeout. |
| `CLAUDE_CODE_STOP_HOOK_BLOCK_CAP` | new | – | Consecutive Stop or SubagentStop blocks before the turn ends anyway, default 8, `0` off. |
| `CLAUDE_CODE_WORKER_CHECKIN_SCHEDULE` | new | 2.1.283 | Comma-separated second waits for background subagent reminders. |
| `CLAUDE_CODE_WORKFLOW_MAX_CONCURRENT_AGENTS` | new | 2.1.269 | Agents per workflow run, 1–256. |
| `CLAUDE_CODE_WORKFLOW_PREFIX_STAGGER_MS` | new | 2.1.229 | Maximum same-prefix hold in a fan-out. |
| `CLAUDE_SUBAGENT_BG_SHELL_MAX_MS` | new | – | Removed in v2.1.260, no-op. |
| `TASK_MAX_OUTPUT_LENGTH` | yes | – | Removed in v2.1.277, no-op. |

### Tools and shell (31)

| Variable | Snap | Since | Behaviour |
|---|---|---|---|
| `BASH_DEFAULT_TIMEOUT_MS` | yes | – | Default foreground shell timeout, 120000. |
| `BASH_MAX_OUTPUT_LENGTH` | yes | – | Shell output characters, default 30000, maximum 150000; ignored if `bashOutputMaxChars` is set. |
| `BASH_MAX_TIMEOUT_MS` | yes | – | Maximum foreground timeout the model may set, default 600000. |
| `CLAUDE_BASH_MAINTAIN_PROJECT_WORKING_DIR` | yes | – | Return to the original directory after each command. |
| `CLAUDE_CODE_BASH_EDIT_DIFF` | new | 2.1.269 | `0` off, `1` every mode; beats `bashEditDiffEnabled`. |
| `CLAUDE_CODE_DISABLE_ATTACHMENTS` | yes | – | Disable attachment processing; repository-denied. |
| `CLAUDE_CODE_DISABLE_FILE_MENTIONS` | new | 2.1.299 | Do not expand `@` mentions; repository-denied. |
| `CLAUDE_CODE_DISABLE_GIT_INSTRUCTIONS` | yes | – | Remove git instructions and the status snapshot; beats the setting. |
| `CLAUDE_CODE_DISABLE_WEB_FETCH` | new | 2.1.285 | Turn off WebFetch. |
| `CLAUDE_CODE_DISABLE_WINDOWS_SHELL_LAUNCHER` | new | 2.1.269 | Start PowerShell directly, not through `cmd.exe`. |
| `CLAUDE_CODE_GIT_BASH_PATH` | yes | – | Windows path to Git Bash. |
| `CLAUDE_CODE_GLOB_HIDDEN` | yes | – | `false` excludes dotfiles from Glob. |
| `CLAUDE_CODE_GLOB_NO_IGNORE` | yes | – | `false` makes Glob respect `.gitignore`. |
| `CLAUDE_CODE_GLOB_TIMEOUT_SECONDS` | yes | – | Glob timeout, 20 s, or 60 s on WSL. |
| `CLAUDE_CODE_MAX_WEB_SEARCHES_PER_SESSION` | new | 2.1.212 | WebSearch cap, default 200. |
| `CLAUDE_CODE_PERFORCE_MODE` | new | – | Fail writes to read-only files with a `p4 edit` hint. |
| `CLAUDE_CODE_POWERSHELL_RESPECT_EXECUTION_POLICY` | new | – | Do not pass `-ExecutionPolicy Bypass`. |
| `CLAUDE_CODE_SCRIPT_CAPS` | new | – | JSON per-script call limits under the scrub. |
| `CLAUDE_CODE_SHELL` | yes | – | `bash` or `zsh` binary for the Bash tool. |
| `CLAUDE_CODE_SHELL_PREFIX` | yes | – | Prefix wrapping spawned shell commands. |
| `CLAUDE_CODE_TMPDIR` | yes | – | Temp root; repository-denied. |
| `CLAUDE_CODE_TOOL_MEMORY_CGROUP_EXCLUDE` | new | 2.1.246 | Process kinds excluded from the memory cap. |
| `CLAUDE_CODE_TOOL_MEMORY_LIMIT` | new | 2.1.233 | Linux and WSL memory cap for tool commands. |
| `CLAUDE_CODE_USE_POWERSHELL_TOOL` | yes | – | Enable or disable the PowerShell tool by platform. |
| `CLAUDE_CODE_WARN_DISK_FREE_GIB` | new | 2.1.304 | Remind Claude when disk is below this; launch only. |
| `CLAUDE_CODE_WARN_MEMORY_FREE_GIB` | new | 2.1.304 | Remind Claude when memory is below this; launch only. |
| `CLAUDE_CODE_WEBFETCH_CACHE_TTL_MS` | new | 2.1.233 | WebFetch cache lifetime, default 900000. |
| `CLAUDE_CODE_WEBFETCH_DEADLINE_MS` | new | 2.1.268 | WebFetch download deadline, default 300000, `0` none. |
| `CLAUDE_CODE_WEB_SEARCH_REFILLS_PER_HOUR` | new | 2.1.290 | WebSearch refill rate; 100 interactive, 0 non-interactive. |
| `CLAUDE_ENV_FILE` | yes | – | Script run before each Bash command in the same shell. |
| `USE_BUILTIN_RIPGREP` | yes | – | `0` uses the system `rg`. |

### Safety and permission checks (10)

| Variable | Snap | Since | Behaviour |
|---|---|---|---|
| `CLAUDE_CODE_AUTO_MODE_SERVER` | new | 2.1.271 | `0` uses client classifier requests. |
| `CLAUDE_CODE_DISABLE_DANGEROUS_RM_TIMEOUT` | new | 2.1.281 | Turn off the critical-path removal time limit; launch only. |
| `CLAUDE_CODE_DISABLE_INLINE_SHELL_RM_PROMPT` | new | 2.1.288 | Do not inspect `-c` scripts for critical-path removals; launch only. |
| `CLAUDE_CODE_DISABLE_MOUNTED_DRIVE_RM_PROMPT` | new | 2.1.304 | Turn off the mounted drive prompt; launch only. |
| `CLAUDE_CODE_DISABLE_POWERSHELL_CMD_RM_DENY` | new | 2.1.283 | Turn off the PowerShell `cmd` built-in check; launch only. |
| `CLAUDE_CODE_DISABLE_SUBSTITUTION_RM_PROMPT` | new | 2.1.281 | Turn off the substitution target check; launch only. |
| `CLAUDE_CODE_DISABLE_ULTRAREVIEW_TRUST_CHECK` | new | 2.1.309 | `claude ultrareview` does not exit in an untrusted folder; launch only. |
| `CLAUDE_CODE_ENABLE_AUTO_MODE` | new | – | Accepted, no effect; auto mode is available everywhere. |
| `CLAUDE_CODE_EVEN_MORE_DANGEROUSLY_SKIP_PERMISSIONS` | new | 2.1.311 | Removes a destructive-delete prompt in bypass mode; launch only. Limits are in the permission docs. |
| `CLAUDE_CODE_SUBPROCESS_ENV_SCRUB` | yes | – | Remove credentials from subprocess environments; see scrub table below. |

### MCP (23)

| Variable | Snap | Since | Behaviour |
|---|---|---|---|
| `CLAUDE_CODE_DISABLE_MCP_TASK_BACKGROUND` | new | 2.1.304 | Wait for MCP task results interactively. |
| `CLAUDE_CODE_MAX_MCP_DESCRIPTION_LENGTH` | new | 2.1.280 | Limit for tool descriptions and server instructions. |
| `CLAUDE_CODE_MCP_ALLOWLIST_ENV` | new | – | Spawn stdio servers with a safe baseline environment. |
| `CLAUDE_CODE_MCP_AUTO_BACKGROUND_MS` | new | 2.1.212 | Time before an MCP call backgrounds, default 120000, `0` off. |
| `CLAUDE_CODE_MCP_STARTUP_WAIT_MS` | new | 2.1.274 | First-turn wait for connecting servers in non-interactive sessions. |
| `CLAUDE_CODE_MCP_TOOL_IDLE_TIMEOUT` | new | – | Idle timeout for MCP tool calls. |
| `ENABLE_CLAUDEAI_MCP_SERVERS` | yes | – | `false` stops fetching claude.ai servers. |
| `ENABLE_TOOL_SEARCH` | yes | – | Tool search control: unset/`true`, `auto`, `auto:N`, `false`. |
| `MAX_MCP_OUTPUT_TOKENS` | yes | – | MCP response cap, default 25000. |
| `MCP_CLIENT_SECRET` | yes | – | OAuth client secret for pre-configured servers. |
| `MCP_CONNECTION_NONBLOCKING` | new | – | `0` waits for servers before the first query. |
| `MCP_CONNECT_TIMEOUT_MS` | new | – | Blocking startup batch wait, default 5000. |
| `MCP_DISCOVERY_CACHE` | new | – | Discovery cache on or off. |
| `MCP_DISCOVERY_CACHE_MAX_STALE_S` | new | – | Maximum entry age, default 14400. |
| `MCP_DISCOVERY_CACHE_STRIKES` | new | 2.1.238 | Failed refreshes before discarding, default 1. |
| `MCP_DISCOVERY_CACHE_TTL_S` | new | – | Fresh period, default 900. |
| `MCP_OAUTH_CALLBACK_PORT` | yes | – | Fixed OAuth redirect port. |
| `MCP_PROTOCOL_NEGOTIATION` | new | 2.1.221 | `legacy` or `auto` probing on the v2 runtime. |
| `MCP_REMOTE_SERVER_CONNECTION_BATCH_SIZE` | yes | – | Remote servers connected in parallel, default 20. |
| `MCP_SDK_GENERATION` | new | 2.1.218 | Pin client runtime: `v1` or `v2`. |
| `MCP_SERVER_CONNECTION_BATCH_SIZE` | yes | – | Local servers connected in parallel, default 3. |
| `MCP_TIMEOUT` | yes | – | Server startup timeout, default 30000. |
| `MCP_TOOL_TIMEOUT` | yes | – | Tool execution timeout, default 100000000. |

### Plugins and skills (17)

| Variable | Snap | Since | Behaviour |
|---|---|---|---|
| `CLAUDE_CODE_DISABLE_BUNDLED_SKILLS` | new | – | Remove bundled skills and workflows. |
| `CLAUDE_CODE_DISABLE_OFFICIAL_MARKETPLACE_AUTOINSTALL` | yes | – | Skip marketplace registration, permanently once skipped. |
| `CLAUDE_CODE_DISABLE_POLICY_SKILLS` | yes | – | Skip the system managed skills directory. |
| `CLAUDE_CODE_ENABLE_BACKGROUND_PLUGIN_REFRESH` | new | – | Refresh plugins at turn ends in `-p`; invalidates cache. |
| `CLAUDE_CODE_PLUGIN_CACHE_DIR` | yes | – | Plugins root, despite the name. |
| `CLAUDE_CODE_PLUGIN_DIRS` | new | – | Plugin directories for the session; absolute or `~`. |
| `CLAUDE_CODE_PLUGIN_DIR_WATCH` | new | – | Reload mods loaded with `--plugin-dir` on change. |
| `CLAUDE_CODE_PLUGIN_GIT_TIMEOUT_MS` | yes | – | Marketplace clone timeout, default 120000. |
| `CLAUDE_CODE_PLUGIN_KEEP_MARKETPLACE_ON_FAILURE` | new | – | Keep the existing checkout if refresh fails. |
| `CLAUDE_CODE_PLUGIN_PREFER_HTTPS` | new | – | Clone GitHub shorthand over HTTPS. |
| `CLAUDE_CODE_PLUGIN_SEED_DIR` | yes | – | Read-only pre-populated plugin directories. |
| `CLAUDE_CODE_SYNC_PLUGIN_INSTALL` | yes | – | Wait for plugin install before the first `-p` query. |
| `CLAUDE_CODE_SYNC_PLUGIN_INSTALL_TIMEOUT_MS` | yes | – | Bound on that wait. |
| `CLAUDE_CODE_SYNC_SKILLS` | new | – | Download account skills in `-p` and wait for the list. |
| `CLAUDE_CODE_SYNC_SKILLS_INSTALL_TIMEOUT_MS` | new | – | Mid-session resync timeout, default 30000. |
| `CLAUDE_CODE_SYNC_SKILLS_WAIT_TIMEOUT_MS` | new | – | First-query wait, default 5000. |
| `FORCE_AUTOUPDATE_PLUGINS` | yes | – | Plugin auto-updates despite `DISABLE_AUTOUPDATER`. |

### Interface, IDE and artifacts (43)

| Variable | Snap | Since | Behaviour |
|---|---|---|---|
| `CCR_FORCE_BUNDLE` | yes | – | Force `claude --cloud` to bundle and upload. |
| `CLAUDE_AX_PREPARK_MS` | new | 2.1.233 | Screen reader write delay, default 0, cap 5000. |
| `CLAUDE_AX_SCREEN_READER` | new | 2.1.181 | `1` on, `0` force off; flag wins; repository-denied. |
| `CLAUDE_AX_STARTUP_QUIET_MS` | new | 2.1.217 | Screen reader startup hold, default 3000. |
| `CLAUDE_CLIENT_PRESENCE_FILE` | new | 2.1.181 | While present, skip Remote Control pushes. |
| `CLAUDE_CODE_ACCESSIBILITY` | yes | – | Keep the native cursor visible for magnifiers. |
| `CLAUDE_CODE_ALT_SCREEN_FULL_REPAINT` | new | – | Full repaint per frame in fullscreen. |
| `CLAUDE_CODE_ARTIFACT_AUTO_OPEN` | new | – | `0` stops browser open on publish. |
| `CLAUDE_CODE_ARTIFACT_COMMENTS` | new | 2.1.221 | `0` stops reading and replying to comments. |
| `CLAUDE_CODE_ARTIFACT_COMMENTS_AUTOREACT` | new | 2.1.228 | `0` stops automatic comment replies. |
| `CLAUDE_CODE_ARTIFACT_PUBLISH_EDITS` | new | 2.1.300 | `0` stops edits applied as part of publishing. |
| `CLAUDE_CODE_AUTO_CONNECT_IDE` | yes | – | Override IDE auto-connection; beats `autoConnectIde`. |
| `CLAUDE_CODE_BS_AS_CTRL_BACKSPACE` | new | – | Read `0x08` as Backspace or Ctrl+Backspace. |
| `CLAUDE_CODE_DISABLE_ALTERNATE_SCREEN` | new | – | Classic renderer; beats `tui`. |
| `CLAUDE_CODE_DISABLE_ARTIFACT` | new | – | Turn off the Artifact tool; no settings file can turn it back on. |
| `CLAUDE_CODE_DISABLE_CFC_PROMPT` | new | 2.1.257 | Keep Chrome tools, drop their prompt section and skill. |
| `CLAUDE_CODE_DISABLE_MOUSE` | yes | – | Disable mouse tracking in fullscreen. |
| `CLAUDE_CODE_DISABLE_MOUSE_CLICKS` | yes | 2.1.195 | Disable clicks, keep wheel. |
| `CLAUDE_CODE_DISABLE_NOTIFICATION_PRESENCE_CHECK` | new | 2.1.193 | Send the desktop notification even when active. |
| `CLAUDE_CODE_DISABLE_PERMISSION_PROMPT_NOTIFY_HOOKS` | new | 2.1.233 | Skip `Notification` hooks in SDK-hosted sessions. |
| `CLAUDE_CODE_DISABLE_TERMINAL_TITLE` | yes | – | No title updates or title generation. |
| `CLAUDE_CODE_DISABLE_VIRTUAL_SCROLL` | yes | – | Render every message in fullscreen. |
| `CLAUDE_CODE_ENABLE_CFC` | yes | – | Start with Chrome on or off; flags win. |
| `CLAUDE_CODE_ENABLE_PROMPT_SUGGESTION` | yes | – | `false` turns off suggestions. |
| `CLAUDE_CODE_ENABLE_SHARE_BUNDLE` | new | 2.1.299 | `/share` saves a local archive. |
| `CLAUDE_CODE_FORCE_STRIKETHROUGH` | new | 2.1.186 | Force strikethrough rendering. |
| `CLAUDE_CODE_FORCE_SYNC_OUTPUT` | new | – | Force synchronized output. |
| `CLAUDE_CODE_FORCE_TERMINAL_IMAGES` | new | – | Draw mod images as pictures. |
| `CLAUDE_CODE_HIDE_CWD` | new | – | Hide the working directory in the logo. |
| `CLAUDE_CODE_IDE_HOST_OVERRIDE` | yes | – | IDE host address. |
| `CLAUDE_CODE_IDE_SKIP_AUTO_INSTALL` | yes | – | Skip extension auto-install. |
| `CLAUDE_CODE_IDE_SKIP_VALID_CHECK` | yes | – | Skip lockfile validation. |
| `CLAUDE_CODE_NATIVE_CURSOR` | new | – | Show the terminal's cursor at the caret. |
| `CLAUDE_CODE_NONBLOCKING_STDOUT` | new | 2.1.261 | Write output through a non-blocking descriptor. |
| `CLAUDE_CODE_NO_FLICKER` | yes | – | Enable fullscreen rendering; beats `tui`. |
| `CLAUDE_CODE_SCROLL_SPEED` | yes | – | Wheel multiplier, up to 20. |
| `CLAUDE_CODE_SYNTAX_HIGHLIGHT` | yes | – | `false` disables diff highlighting. |
| `CLAUDE_CODE_TMUX_TRUECOLOR` | yes | – | Allow truecolor in tmux; any non-empty value. |
| `CLAUDE_CODE_USER_DIALOG_TIMEOUT_MS` | new | – | Deadline for forwarded dialogs; repository-denied. |
| `CLAUDE_CODE_YOU_SHOULD_KNOW_DEBUG` | new | 2.1.287 | Show the last three mod checks. |
| `CLAUDE_REMOTE_CONTROL_SESSION_NAME_PREFIX` | new | – | Prefix for generated Remote Control names. |
| `FORCE_HYPERLINK` | new | – | Numeric; `0` off, anything else on. |
| `IS_DEMO` | yes | – | Hide identity and skip onboarding; any non-empty value. |

### Telemetry (32)

| Variable | Snap | Since | Behaviour |
|---|---|---|---|
| `BETA_TRACING_ENDPOINT` | yes | – | OTLP/HTTP endpoint for detailed beta tracing; repository-denied. |
| `CLAUDE_CODE_ENABLE_FEEDBACK_SURVEY_FOR_OTEL` | new | – | Route surveys to your collector when Anthropic traffic is blocked. |
| `CLAUDE_CODE_ENABLE_TELEMETRY` | yes | – | Enable OpenTelemetry; repository-denied. |
| `CLAUDE_CODE_OTEL_CONTENT_MAX_LENGTH` | new | – | Content attribute limit, default 61440. |
| `CLAUDE_CODE_OTEL_DIAG_STDERR` | new | – | Write exporter errors to stderr. |
| `CLAUDE_CODE_OTEL_FLUSH_TIMEOUT_MS` | yes | – | Span flush timeout, default 5000. |
| `CLAUDE_CODE_OTEL_HEADERS_HELPER_DEBOUNCE_MS` | yes | – | Dynamic header refresh, default 1740000. |
| `CLAUDE_CODE_OTEL_SHUTDOWN_TIMEOUT_MS` | yes | – | Exporter shutdown timeout, default 2000. |
| `CLAUDE_CODE_PROPAGATE_TRACEPARENT` | new | 2.1.152 | Propagate W3C trace context through a custom proxy. |
| `ENABLE_BETA_TRACING_DETAILED` | yes | – | Detailed beta tracing; repository-denied. |
| `OTEL_ATTRIBUTE_VALUE_LENGTH_LIMIT` | new | – | SDK attribute limit; the smaller with the content limit applies. |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | yes | – | Standard OTLP endpoint; repository-denied. |
| `OTEL_EXPORTER_OTLP_HEADERS` | yes | – | Standard OTLP headers; repository-denied. |
| `OTEL_EXPORTER_OTLP_PROTOCOL` | yes | – | Standard OTLP protocol; repository-denied. |
| `OTEL_LOGRECORD_ATTRIBUTE_VALUE_LENGTH_LIMIT` | new | – | Variants of the above. |
| `OTEL_LOGS_EXPORTER` | yes | – | Log exporter; only `none` applies from repository files. |
| `OTEL_LOG_ASSISTANT_RESPONSES` | new | – | Include response text; defaults to the user-prompt value. |
| `OTEL_LOG_MANAGED_SETTINGS` | new | – | Add redacted managed settings to events. |
| `OTEL_LOG_RAW_API_BODIES` | new | – | Emit request and response JSON; `1` inline, `file:<dir>` on disk; repository-denied. |
| `OTEL_LOG_TOOL_CONTENT` | yes | – | Tool content in `tool.output` span event. |
| `OTEL_LOG_TOOL_DETAILS` | yes | – | Tool inputs, names and raw errors. |
| `OTEL_LOG_USER_PROMPTS` | yes | – | Include prompt text. |
| `OTEL_METRICS_EXPORTER` | yes | – | Metrics exporter; only `none` applies from repository files. |
| `OTEL_METRICS_INCLUDE_ACCOUNT_UUID` | yes | – | `false` excludes account UUID. |
| `OTEL_METRICS_INCLUDE_ENTRYPOINT` | new | 2.1.152 | `true` includes entrypoint. |
| `OTEL_METRICS_INCLUDE_REPOSITORY` | new | – | `true` adds `vcs.*` attributes. |
| `OTEL_METRICS_INCLUDE_RESOURCE_ATTRIBUTES` | new | – | `false` excludes resource attributes from labels. |
| `OTEL_METRICS_INCLUDE_SESSION_ID` | yes | – | `false` excludes session ID. |
| `OTEL_METRICS_INCLUDE_VERSION` | yes | – | `true` includes version. |
| `OTEL_METRIC_EXPORT_INTERVAL` | yes | – | Standard metric export interval. |
| `OTEL_RESOURCE_ATTRIBUTES` | yes | – | Resource attributes; attached to metric labels. |
| `OTEL_SPAN_ATTRIBUTE_VALUE_LENGTH_LIMIT` | new | – | Variants of the above. |

### Updates, commands and diagnostics (23)

| Variable | Snap | Since | Behaviour |
|---|---|---|---|
| `CLAUDE_CODE_DEBUG_LOGS_DIR` | yes | – | Debug log file path, despite the name; needs debug mode. |
| `CLAUDE_CODE_DEBUG_LOG_LEVEL` | yes | – | Minimum debug level, default `debug`. |
| `CLAUDE_CODE_DISABLE_FEEDBACK_SURVEY` | yes | – | Disable session surveys. |
| `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` | yes | – | Disable updates, telemetry, error reporting and related traffic; any non-empty value. |
| `CLAUDE_CODE_PACKAGE_MANAGER_AUTO_UPDATE` | new | – | Let Homebrew or WinGet upgrade in the background. |
| `CLAUDE_CODE_SEND_FEEDBACK` | new | – | `0` off, `1` on where the account has access. |
| `DEBUG` | yes | – | Truthy enables debug mode; namespace patterns do not. |
| `DISABLE_AUTOUPDATER` | yes | – | No background updates; manual update still works. |
| `DISABLE_BUG_COMMAND` | yes | – | Older name for `DISABLE_FEEDBACK_COMMAND`. |
| `DISABLE_COST_WARNINGS` | yes | – | No cost warnings. |
| `DISABLE_DOCTOR_COMMAND` | yes | – | Hide the `/doctor` skill. |
| `DISABLE_ERROR_REPORTING` | yes | – | Opt out; any non-empty value, including `0`. |
| `DISABLE_EXTRA_USAGE_COMMAND` | yes | – | Hide `/usage-credits`. |
| `DISABLE_FEEDBACK_COMMAND` | yes | – | Disable `/feedback`, `/bug`, `/share` and drafts. |
| `DISABLE_GROWTHBOOK` | new | – | Disable feature-flag fetching. |
| `DISABLE_INSTALLATION_CHECKS` | yes | – | No installation warnings. |
| `DISABLE_INSTALL_GITHUB_APP_COMMAND` | yes | – | Hide `/install-github-app`. |
| `DISABLE_LOGIN_COMMAND` | yes | – | Hide `/login`. |
| `DISABLE_LOGOUT_COMMAND` | yes | – | Hide `/logout`. |
| `DISABLE_TELEMETRY` | yes | – | Opt out and stop flag fetching; any non-empty value. |
| `DISABLE_UPDATES` | new | – | Block all updates including manual. |
| `DISABLE_UPGRADE_COMMAND` | yes | – | Hide `/upgrade`. |
| `DO_NOT_TRACK` | new | – | Same as `DISABLE_TELEMETRY`, read as a boolean. |

### Network and TLS (10)

| Variable | Snap | Since | Behaviour |
|---|---|---|---|
| `CLAUDE_CODE_CERT_STORE` | new | – | CA sources: `bundled`, `system`. |
| `CLAUDE_CODE_CLIENT_CERT` | yes | – | mTLS certificate path. |
| `CLAUDE_CODE_CLIENT_KEY` | yes | – | mTLS key path. |
| `CLAUDE_CODE_CLIENT_KEY_PASSPHRASE` | yes | – | Passphrase for that key. |
| `CLAUDE_CODE_DISABLE_MTLS_RELOAD_ON_STALE_CONNECTION` | new | 2.1.232 | Do not re-read mTLS files on connection errors. |
| `CLAUDE_CODE_PROXY_RESOLVES_HOSTS` | yes | – | Let the proxy resolve DNS. |
| `HTTPS_PROXY` | yes | – | HTTPS proxy. |
| `HTTP_PROXY` | yes | – | HTTP proxy. |
| `NODE_EXTRA_CA_CERTS` | yes | – | Extra CA bundle; also disables gzip of bodies. |
| `NO_PROXY` | yes | – | Proxy bypass list. |

### Set by Claude Code (12)

| Variable | Snap | Since | Behaviour |
|---|---|---|---|
| `CLAUDECODE` | new | – | `1` in spawned subprocesses and IDE terminals. |
| `CLAUDE_CODE_BRIDGE_SESSION_ID` | new | – | `session_` ID while Remote Control is active. |
| `CLAUDE_CODE_CHILD_SESSION` | new | 2.1.172 | `1` in Bash, PowerShell, Monitor, hook and status line subprocesses. |
| `CLAUDE_CODE_MESSAGING_SOCKET` | yes | 2.1.224 | Inbox socket path; ignored from every file. |
| `CLAUDE_CODE_MESSAGING_TOKEN` | new | 2.1.228 | Per-session inbox token; ignored from every file. |
| `CLAUDE_CODE_REMOTE` | yes | – | `true` in cloud sessions; ignored from every file. |
| `CLAUDE_CODE_REMOTE_SESSION_ID` | yes | – | Cloud session ID. |
| `CLAUDE_CODE_SESSION_ID` | yes | – | Current session ID, updated on `/clear`. |
| `CLAUDE_EFFORT` | new | – | Effort level in Bash and hooks, when supported. |
| `CLAUDE_JOB_DIR` | yes | – | Background session's `~/.claude/jobs/<id>`. |
| `CLAUDE_PID` | new | 2.1.214 | Claude Code's process ID. |
| `TRACEPARENT` | new | – | W3C trace context for subprocesses, when propagation is on. |

### Referenced, not configuration (13)

| Variable | Snap | Since | Behaviour |
|---|---|---|---|
| `DATABASE_URL` | new | – | Example names in the scrub table; not read as configuration. |
| `DB_PASSWORD` | new | – | Example names in the scrub table; not read as configuration. |
| `GH_ENTERPRISE_TOKEN` | new | – | GitHub tokens the scrub leaves in place. |
| `GH_TOKEN` | yes | – | GitHub tokens the scrub leaves in place. |
| `GITHUB_ENTERPRISE_TOKEN` | new | – | GitHub tokens the scrub leaves in place. |
| `GITHUB_TOKEN` | new | – | GitHub token the scrub leaves in place. |
| `GIT_CONFIG_COUNT` | new | – | Left in place by the scrub, with `GIT_CONFIG_KEY_<n>` and `GIT_CONFIG_VALUE_<n>`. |
| `NPM_CONFIG_REGISTRY` | new | – | Example names in the scrub table; not read as configuration. |
| `NPM_TOKEN` | new | – | Example names in the scrub table; not read as configuration. |
| `PATH` | yes | – | Standard variables consulted, for example `TERM_PROGRAM` and `TERM` in Backspace handling. |
| `PIP_INDEX_URL` | new | – | Example names in the scrub table; not read as configuration. |
| `TERM` | yes | – | Standard variables consulted, for example `TERM_PROGRAM` and `TERM` in Backspace handling. |
| `TERM_PROGRAM` | yes | – | Standard variables consulted, for example `TERM_PROGRAM` and `TERM` in Backspace handling. |
## Failure modes & edge cases

- `CLAUDE_CODE_AUTO_COMPACT_WINDOW=200` means 200 tokens, handled with a warning as the 100K minimum.
- `CLAUDE_CODE_DEBUG_LOGS_DIR` is a file path, despite the name, and `CLAUDE_CODE_PLUGIN_CACHE_DIR` is the plugins root.
- `DEBUG=express:*` does not enable debug mode.
- Before v2.1.211, spellings like `1e6` could silently set a much smaller value.
- `SLASH_COMMAND_TOOL_CHAR_BUDGET` keeps a legacy name.

## Changes since the snapshot

- 211 of the 424 names are new since the snapshot, as marked above.
- v2.1.186: `CLAUDE_CODE_MAX_RETRIES` capped at 15; `CLAUDE_CODE_CONNECT_TIMEOUT_MS` removed.
- v2.1.211: numeric spellings parsed properly.
- v2.1.251: project and local `env` lose path-choosing and content-export variables.
- v2.1.282: project and local `env` lose telemetry variables.
- v2.1.290: `CLAUDE_CODE_DISABLE_ATTACHMENTS` and dialog timers repository-denied.
- Removed or no-op: see rows beginning "Removed".

## Open questions

- Several names in the 424 are examples or standard variables rather than configuration; they are grouped under "Referenced, not configuration".
- `Since` is blank for most rows because the docs give no version; for new names, the first version is unknown without per-release diffing.
- `CLAUDE_CODE_SYNC_PLUGINS` and `CLAUDE_CODE_ACCOUNT_UUID` appear in the `env` restriction text but have no row of their own, so they are outside the 424.
