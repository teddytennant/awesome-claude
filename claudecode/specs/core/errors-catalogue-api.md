# Errors catalogue: API, usage, auth, network, request

**Status:** shipped
**Provenance:** both
**Sources:** docs errors (retries, server, usage, auth, network, request); snapshot `services/api/errors.ts`, `errorUtils.ts`; changelog 2.1.101, 2.1.129, 2.1.234, 2.1.243, 2.1.273, 2.1.311

## Purpose

Maps each user-visible error to its condition and required recovery guidance. Message text is a behavioural contract, and scripts match it. Retry rules are in [api-client.md](api-client.md). Local errors are in [errors-catalogue-local.md](errors-catalogue-local.md). Docs carry roughly 290 entries; this groups them and gives the required behaviour for the ones that shape the product.

## Behaviour

### General rules

1. An error shown to a user MUST mean applicable retries have finished.
2. Errors from model calls appear as `API Error: …` text. In `-p`, text output prints them; JSON outputs carry them in `result`.
3. Recovery hints MUST vary by surface: interactive names `/model`, `-p` names `--model`, SDK omits the hint, Desktop uses its picker.
4. Hints naming a service MUST vary by provider: `status.claude.com`, the provider status page, or the gateway host.
5. A proxy's HTML page MUST be reduced to status and page title, or status and standard name (documented from v2.1.281). Raw markup is never printed.
6. Connection failures name the code and what to fix, such as `NODE_EXTRA_CA_CERTS` (2.1.273). `Connection dropped` says where to look first (2.1.311).
7. Your original message remains in the conversation after an error, so `try again` suffices.

### Server

| Message | Condition | Recovery |
| - | - | - |
| `API Error: 500 …` / any 5xx | Server failure; HTML pages show title | Status page; `/feedback`; on gateways test `ENABLE_TOOL_SEARCH=false` |
| `API Error: Repeated 529 Overloaded errors` | Capacity across users, not quota | Wait; `/model` to another model |
| `Opus is experiencing high load…` | One model under load | Switch model |
| `Request timed out` | `API_TIMEOUT_MS` reached | Raise it; retry |
| `API Error: No response from API (waited …)` | First-byte deadlines both passed | Raise `API_TIMEOUT_MS` or `CLAUDE_STREAM_FIRST_BYTE_TIMEOUT_MS` |
| `API Error: Stream idle timeout - no chunks received` | Watchdog | See network config |
| `API Error: <reason>. The response above may be incomplete.` | Mid-stream failure after completed content | Reply `continue` |

Incomplete-response variants: `Server error mid-response`, `Connection lost mid-response`, `Your computer went to sleep mid-response`, `The response stopped arriving`, `Part of the response never arrived`, `The response stream was malformed`. Other stream terminals: `Connection lost before a response was produced`, `Your computer went to sleep before a response was produced`, `The response stalled before a response was produced`, `Content block not found`, `Content block already closed`, `Stream event unreadable`, and `The model's tool call could not be parsed (retry also failed).`

Auto mode classifier results (`Auto mode cannot determine…`, `The server returned no safety verdict`, `Was not reviewed and did not run`) and `Agent terminated early due to an API error` are returned to the model or subagent parent rather than ending the session.

### Usage limits

| Message | Condition |
| - | - |
| `You've hit your session limit` / weekly / `Opus` / `Sonnet` limit | Seat windows. Model-family limits can be escaped with `/model` |
| `Usage credits required for 1M context` | 1M needs credits; restart after enabling |
| Fable consent unanswered | Turn ended without sending |
| `Server is temporarily limiting requests` | Short throttle |
| `Request rejected (429)` | Key or project rate limit |
| `You've hit your monthly spend limit` and variants | Usage-credit limit: individual, org or team |
| `Spend limit reached` | Claude apps gateway cap; names the cap, reset and operator message (2.1.225) |
| `Credit balance is too low` | Console prepaid credits, or a key shadowing a subscription |
| `Could not update your spend limit` | Server refused the prompt's change |

8. Sessions can wait for a limit reset and continue automatically (2.1.234), controlled by `/config` and `autoContinueAtUsageLimit`.
9. Rate-limit messages show which limit and when it resets (2.1.101).

### Authentication

| Group | Entries |
| - | - |
| No credential | `Not logged in`, `Could not resolve authentication method` |
| API key | `Invalid API key`, `Your apiKeyHelper script is failing`, `Invalid request header value`, `This organization has been disabled`, `Your organization has disabled API key authentication` |
| Subscription | `Your organization has disabled Claude subscription access`, `OAuth token revoked or expired`, `API Error: 401 Invalid authentication credentials`, `Login expired`, `Could not refresh your login because another Claude Code process is refreshing it`, `Couldn't save your login`, `Couldn't start the local listener…`, `Your account is on hold`, `Anthropic profile login expired`, `OAuth scope requirement` |
| Cloud | `Claude login not accepted`, `Administrator policy requires a Cloud gateway sign-in`, `Cloud gateway session expired`, `Sign-in timed out…`, `Gateway refused the request` |
| Providers | `AWS credentials expired or invalid`, `AWS authentication failed`, `Google Cloud credentials expired or invalid`, `Google Cloud authentication failed`, `Microsoft Foundry authentication failed`, `Could not load AWS or Google Cloud credentials`, `AWS default-chain credential resolve timed out` (60s), `Bedrock setup verification timed out` |
| Remote Control | Requires the Anthropic API; refresh, renew, account-change and host-signout messages |
| MCP auth | `MCP server needs you to sign in again`, credential store unreadable, bad URL, issuer mismatch, non-https token endpoint |
| Other | `Routines are disabled by your organization's policy`, `Artifacts need a claude.ai login`, `claude.ai rejected the session token` |

10. Provider errors MUST distinguish expiry from authorization: a 401 on Agent Platform means expired; a 403 means denied. On Claude Platform on AWS and Mantle a 401 reports an expired token, while Bedrock's 401 or 403 is authentication.
11. A rejected credential MUST NOT be replaced silently: `apiKeyHelper` is retried, otherwise the error stands.

### Network

`Unable to connect to API` (names code and kind), `Unable to connect to Anthropic services` (first run), `Socket is closed`, `API returned an empty or malformed response`, `Streaming response ended before any complete data was received`, `Bedrock streaming response has an unexpected content-type`, SSL certificate errors, `Host not allowed in a cloud session`, `The proxy refused the connection`, cloud environments and Sessions API failures, Remote Control reconnect failures, transcript-share and feedback delivery failures, and MCP timeouts during clock changes.

12. An SSL failure MUST be reported on the first attempt.
13. A cloud-session network block names the host and reason (2.1.251).

### Request

| Message | Condition | Recovery |
| - | - | - |
| `Prompt is too long` / interactive `Context limit reached · /compact or /clear to continue` | Over window | Compact; `Prompt is too long · automatic compaction failed: <error>` names the cause |
| `Context exceeds the token limit` | `/context` warning | |
| `Request too large` | Body over the API's 32MB | Trim |
| `Image was too large`, `Unable to resize image`, PDF errors | Media limits | Rewind or re-share |
| `Request rejected as unprocessable by the model` | API's own text | |
| `Extra inputs are not permitted` | Endpoint rejects a field | `CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS` |
| `Tool input schema is invalid` | Bad `input_schema`, names `tools.N` | Fix the MCP server |
| `MCP tool name over 128 characters`, `tool_use.name over 200 characters` | Name limits | |
| `There's an issue with the selected model (…)` | Unknown or no access | Alias; `/model` |
| `Model is not a recognized model id`, `Model not found`, `Couldn't confirm model with the API`, `API error when checking the picked model` | Switch-time validation | Pick another |
| `Claude Opus is not available with the Claude Pro plan` | Plan | |
| `Claude Code does not support this model` | Server per-model minimum version | `claude update` |
| `Model … is restricted by your organization's settings` | Restrictions | |
| `Can't switch to the default model` | Default blocked | |
| `Model switch was blocked by a PreModelSwitch hook` | Hook | |
| `Couldn't save it as your default` | Settings unwritable | |
| `Advisor is less capable…` | Ranking | |
| `thinking.type.enabled is not supported…` | Old client | Update |
| `Effort '<level>' isn't available with thinking turned off…` | Client wording | Lower effort |
| `max_tokens must be greater than thinking.budget_tokens` | Budget vs output | Raise max tokens |
| `Claude's response exceeded the … output token maximum` | Cut off; non-streaming form can't be raised | `continue` |
| `400 due to tool use concurrency issues`, orphaned, duplicate id, `thinking blocks … cannot be modified` | History mismatch | `/rewind` |
| `Invalid data in redacted_thinking block`, `Invalid encrypted_content in search_result block` | Undecryptable history | |
| `role 'system' must precede an 'assistant' message` | Position rejected | |
| `Unsupported tool content removed` | Loading a session; informational | |

### Refusals

14. Usage Policy refusal: `API Error: <model> can't help with this. Start a new session to continue.` plus feedback and policy link, with Request ID and Message ID. `Claude` is used when no model is recorded. The check covers the whole conversation, so resume re-triggers.
15. Cyber flag: `<model>'s safeguards flagged this message…`, with Cyber Verification Program link. Automatic-fallback models print a different message. Third-party providers show the Usage Policy form.
16. `Details: [reasoning_extraction]` marks requests to reproduce reasoning (2.1.234), and the remedy is removing such instructions.
17. `Output blocked by content filtering policy`: API text after one automatic re-send.
18. Refusal hints vary: `-p` suggests a new session or `--model` (2.1.172).

## Configuration & interfaces

Stderr diagnostic: `[claude-code:unrecognized_model] {"model":…,"query_source":…}`, once per string per process, in `-p` under every output format; elsewhere in the debug log. Consumers match the prefix and ignore unknown JSON fields (2.1.233). `CLAUDE_CODE_MAX_RETRIES` and related tuning are in [api-client.md](api-client.md).

## Failure modes & edge cases

- `Could not resolve authentication method` reaches background and cloud workers started with no credential.
- Bedrock's `Input is too long for requested model.` and the `capability_rejected: prompt_too_long` gateway token MUST be treated as prompt-too-long.
- A gateway rewriting the too-long error disables recovery.

## Changes since the snapshot

- 2.1.101: refusal explanations from the API; better rate-limit retry messages.
- 2.1.129: policy refusals include the API Request ID.
- 2.1.172: non-interactive refusal hint.
- 2.1.234: empty-response error details; `reasoning_extraction` details.
- 2.1.243: effort with thinking off message.
- 2.1.273: SSL and proxy error wording.
- 2.1.311: `Connection dropped` guidance.

## Open questions

- Message text is stable only as far as docs show; many have changed by version, and old wordings still appear in the docs' lookup table.
