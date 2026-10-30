# API client: streaming, retries and error classes

**Status:** shipped
**Provenance:** both
**Sources:** docs errors (Automatic retries), network-config, env-vars, llm-gateway-protocol; snapshot `services/api/claude.ts`, `client.ts`, `withRetry.ts`, `errors.ts`; changelog 2.1.105, 2.1.144, 2.1.181, 2.1.185, 2.1.186, 2.1.196, 2.1.199, 2.1.239, 2.1.246, 2.1.261, 2.1.284, 2.1.285, 2.1.286, 2.1.292, 2.1.295, 2.1.296, 2.1.301, 2.1.305

## Purpose

Sends model requests, consumes streams, and decides for every failure whether to retry, change the request, fall back, or surface an error. Request shaping for thinking, effort and context is in [request-shaping.md](request-shaping.md). Client-side attestation and rate-limit enforcement are excluded from this spec.

## Behaviour

### Client construction

1. One client factory MUST produce the right SDK client for the session's provider, with consistent headers, custom headers (`ANTHROPIC_CUSTOM_HEADERS`) and proxy settings.
2. A fresh client MUST be built on the first attempt and after auth failures, so refreshed credentials apply.
3. On stale-connection errors (`ECONNRESET`, `EPIPE`), keep-alive pooling is turned off and the retry opens a fresh socket (2.1.214).
4. Large request bodies on direct connections are gzip-compressed, except through a proxy, with a client certificate, or with `NODE_EXTRA_CA_CERTS` (`CLAUDE_CODE_GZIP_REQUEST_BODIES=0` disables).
5. Header values MUST be validated. A line break, NUL or a character above U+00FF is reported as an invalid header value.

### Streaming

6. Requests stream by default. The stream assembles content blocks, usage and stop reason, yielding each completed block.
7. Four independent timers abort a quiet stream:

| Timer | Aborts when | Runs on | Default |
| - | - | - | - |
| First-byte deadline | No response headers | Direct Anthropic API and Claude Platform on AWS, not through a gateway base URL; opt-in for Claude apps gateway | Byte watchdog timeout, plus 1s per 32KB of body |
| Event-level watchdog | No events parse | Every provider | 300s |
| Byte-level watchdog | No bytes on the wire | Direct, Claude Platform on AWS, gateways; opt-in on Bedrock; not Agent Platform or Foundry | 180s direct |
| Body idle timeout | No bytes for 5 minutes, including header wait | Other providers, unless `API_FORCE_IDLE_TIMEOUT` changes it | 5 min |

8. Where byte-level monitoring runs, arriving bytes including keep-alive pings also reset the event-level watchdog for a limited time. Pings alone MUST NOT keep a stream open forever: about five minutes at 10-second pings, about 12.5 minutes total on a Claude apps gateway's 15-second pings.
9. A retry after a first-byte timeout waits one second less than `API_TIMEOUT_MS`, so it can outlast a proxy that buffers until completion. Bedrock reuses the first deadline. If that also expires, the turn ends with `No response from API`.
10. After 20 seconds without data the UI shows a `Waiting for API response · will retry in …` banner, 45 seconds on gateway connections (2.1.309). It is not an error.

### Retry classification by stream position

11. The decision MUST depend on what the stream has already delivered, so tool calls never run twice.

| Failure point | Behaviour |
| - | - |
| Before any response content | Retry with backoff; streaming stall retried once |
| After thinking, before any text or tool call | Server error or drop retried up to 2 times; stall retried once. Then `Connection lost before a response was produced` or `The response stalled before a response was produced` |
| After a completed text or tool block, or a block started after thinking | Do NOT re-send. Keep completed blocks, run finished tool calls, continue the turn, append `The response above may be incomplete` |
| After the response finished | Keep it and end normally |

12. Sleep is detected and reported as a distinct reason, handled as a dropped connection.
13. Dropped, duplicated or damaged stream events: if only thinking completed, re-issue; if nothing completed, use non-streaming. Terminal messages are `Part of the response never arrived…` and `The response stream was malformed…`.
14. If the output content filter stops a stream before text, a tool call or finished thinking, re-send once within budget.

### Non-streaming fallback

15. When a stream fails before usable data, or ends without any complete data, the client MAY re-send without streaming. A non-streaming request allows at most 64,000 output tokens, and `CLAUDE_CODE_MAX_OUTPUT_TOKENS` cannot raise that.
16. Each attempt times out at 300 seconds locally, or at a positive `API_TIMEOUT_MS`. `CLAUDE_CODE_NONSTREAMING_TIMEOUT_RETRIES` limits re-sends of timed-out attempts (2.1.285).
17. `CLAUDE_CODE_DISABLE_NONSTREAMING_FALLBACK=1` turns it off, for proxies where it duplicates tool execution.
18. A success status whose body is not a Claude message MUST NOT retry; it ends with `API returned an empty or malformed response`, naming content type, body kind, size, request id and the original failure.
19. With partial messages on, a `ping` stream event is emitted every 30 seconds during non-streaming requests on the Anthropic API, Claude Platform on AWS and gateways (2.1.285).

### Retry policy

20. Default is 10 retries with exponential backoff, capped at 15 by `CLAUDE_CODE_MAX_RETRIES`. One limit covers a whole model call, so with defaults a failing call sends at most 14 requests (2.1.286). Dropped-connection retries share that budget (2.1.284).
21. Snapshot backoff: 500ms base doubling to a 32s ceiling, 25% jitter, `retry-after` honoured when present. Docs confirm 500ms and 32,000ms defaults for 529s through the overload variables.
22. Retried: connection errors, 408, 409, 5xx, overloaded errors, 429 throttles. A subscription sign-in also retries 429s that lack plan quota headers (the docs date this to v2.1.199).
23. 401 clears cached helper keys and refreshes; a `401` or `403` under `apiKeyHelper` re-runs the script within budget. OAuth revocation refreshes the token.
24. Retried at most twice: expired or missing Google credentials, and AWS credentials failing to load. Cached credentials are dropped first (2.1.228).
25. `input + max_tokens` over the context limit: retry with reduced `max_tokens`. Stop and compact when no reduction fits or it cannot shrink further.
26. Background requests MUST NOT amplify overload: only foreground sources retry 529s, so a title or suggestion request fails at once. Snapshot foreground sources include the main thread, SDK, agents, compaction, hooks, side questions and auto mode.
27. Repeated 529s trigger model fallback or end with `Repeated 529 Overloaded errors`. Snapshot threshold: 3 consecutive; docs give "with an API key on an Opus model, it stops at the third 529".
28. Not retried: TLS certificate validation failures (reported on the first attempt, while transient TLS such as handshake timeouts still retry), Bedrock unexpected content-type (documented from v2.1.208), organization policy denials (no retry, no fallback), and a gateway spend-limit 429.
29. In the snapshot, an `x-should-retry: false` response header is honoured.

### Unattended retry

30. `CLAUDE_CODE_RETRY_WATCHDOG=1` retries 429 and 529 indefinitely, raises the default retry count for other transient errors to 300 and removes the cap of 15 (2.1.199). Keep-alive output during long waits stops hosts marking the session idle.
31. It MUST fail at once on a standard-speed 429 reporting a spend limit or exhausted credits (2.1.239).
32. `CLAUDE_CODE_RETRY_WATCHDOG_MAX_WAIT_MS` limits the wait per request (2.1.295). `CLAUDE_CODE_RETRY_WATCHDOG_MAX_USAGE_LIMIT_WAIT_MS` ends a request at a usage limit that resets too far away (2.1.301). `CLAUDE_CODE_RETRY_WATCHDOG_USAGE_LIMIT_RECHECK_MS` polls for an early lift, valid from 60000 to 10800000 (2.1.305).

### Capability self-healing

33. Rejections of optional request parts MUST trigger one retry with the part changed or removed, and the change is remembered. Recognition uses error wording, so gateways must forward bodies unmodified, or use `capability_rejected:` tokens.

| Rejected | Client response | Remembered for |
| - | - | - |
| `thinking.type` value | Try the other type | Model, until exit |
| `role: "system"` in messages | Carry text in user messages | Until `/clear` or compaction |
| `cache_control` on a mid-conversation system message | Move the marker to the last non-system entry | Until exit |
| Thinking signature, including `bound to a different conversation` | Remove earlier thinking blocks | All later requests |
| Advisor tool type | Drop the entry and beta; `/advisor` unavailable | Base URL, until exit |
| `output_config.effort` or its beta | Drop both | Model, until exit |
| `context_management` | Drop | Per-rejection |
| Tool search fields | Retry without them | See [tool-system.md](tool-system.md) |

### Retry display

34. The spinner shows `Retrying in Ns · attempt x/y`. Actionable reasons (network down, TLS handshake, rate limit) are named immediately. Others read `API error` until the third attempt (2.1.198). Spinner tips hide during retries, and a 529 names the status page or provider host.
35. In SDK mode each retry emits an `api_retry` system event.

### Error classes

36. API failures map to the SDK's `SDKAssistantMessageError` categories: `authentication_failed`, `oauth_org_not_allowed`, `account_on_hold`, `billing_error`, `rate_limit`, `overloaded`, `invalid_request`, `model_not_found`, `server_error`, `max_output_tokens`, `cloud_credential_error`, `unknown`. See [errors-catalogue-api.md](errors-catalogue-api.md).
37. Terminal errors are recorded as synthetic assistant messages prefixed `API Error`, so they appear in transcripts and can be excluded from the next request and from stop hooks.

## Configuration & interfaces

| Variable | Default | Effect |
| - | - | - |
| `CLAUDE_CODE_MAX_RETRIES` | 10 | Retry attempts, cap 15 unless watchdog |
| `API_TIMEOUT_MS` | 600000 | Wait for headers; `0` disables this timeout only |
| `CLAUDE_STREAM_FIRST_BYTE_TIMEOUT_MS` | unset | Clamped 10s to 30min; `≥1` enables on Claude apps gateway |
| `CLAUDE_STREAM_IDLE_TIMEOUT_MS` | | Both watchdogs; floor 5min, byte cap 30min |
| `CLAUDE_BYTE_STREAM_IDLE_TIMEOUT_MS` | | Byte watchdog only, 10s to 30min |
| `CLAUDE_ENABLE_STREAM_WATCHDOG`, `CLAUDE_ENABLE_BYTE_WATCHDOG` | on | `0` or `1`; byte `0` also disables first-byte deadline |
| `CLAUDE_ENABLE_BYTE_WATCHDOG_BEDROCK` | off | Replaces body idle timeout on Bedrock |
| `API_FORCE_IDLE_TIMEOUT` | | `0` off, `1` everywhere |
| `CLAUDE_CODE_OVERLOADED_RETRY_BASE_DELAY_MS` | 500 | Up to 32000; 529 backoff start |
| `CLAUDE_CODE_OVERLOADED_RETRY_MAX_DELAY_MS` | 32000 | Up to 64000; 529 backoff ceiling |

Integer variables accept forms like `1e6` and `64_000` (2.1.211). The overload variables don't apply with the retry watchdog or to fast-mode requests.

## Failure modes & edge cases

- `API_TIMEOUT_MS=0` leaves the first-byte deadline and body idle timeout running; a positive value under 11 seconds turns the first-byte deadline off.
- A non-streaming retry of a very slow generation times out on every attempt; lower the retry limit.
- The body idle timeout applies during header wait, so unanswered requests on those connections end after 5 to 6 minutes.

## Changes since the snapshot

- 2.1.105: stalled streams abort after 5 minutes.
- 2.1.144: pre-response stalls retry streaming once.
- 2.1.181: drops mid-thinking retry.
- 2.1.185: banner rewording, 20s trigger.
- 2.1.186: retry cap of 15.
- 2.1.196: idle watchdog on by default everywhere.
- 2.1.199: mid-stream server errors keep partial output; watchdog extended.
- 2.1.239: watchdog fails on spend limits.
- 2.1.261: longer first-byte retry wait.
- 2.1.284: mid-stream connection retries share the budget.
- 2.1.286: per-call retry limit of 14 requests.
- `CLAUDE_CODE_RETRY_WATCHDOG` replaces the snapshot's internal unattended retry.

## Open questions

- How "up to 10 retries" and "at most 14 requests" combine across streaming and non-streaming layers.
- Whether the snapshot's fast-mode short-retry threshold still applies (see [fast-mode.md](fast-mode.md)).
