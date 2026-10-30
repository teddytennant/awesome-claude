# LLM Gateway Protocol
**Status:** shipped
**Provenance:** both (base URL handling in snapshot; contract documented post-leak)
**Sources:** docs `llm-gateway-protocol.md`, `llm-gateway-connect.md`, `llm-gateway-rollout.md`, `llm-gateway.md`, `gateways.md`; changelog 2.1.181 to 2.1.312

## Purpose
Define what Claude Code sends to and expects from a third-party LLM gateway, so operators stay compatible across releases. The Claude apps gateway has its own contract: see [claude-apps-gateway.md](claude-apps-gateway.md).

## Behaviour

### Formats
| Format | Selected by | Endpoints | Forward unchanged |
|---|---|---|---|
| Anthropic Messages | `ANTHROPIC_BASE_URL` | `/v1/messages`, `/v1/messages/count_tokens` (optional) | `anthropic-beta`, `anthropic-version` headers |
| Bedrock InvokeModel | `ANTHROPIC_BEDROCK_BASE_URL` + `CLAUDE_CODE_USE_BEDROCK=1` | `/model/{model}/invoke`, `/invoke-with-response-stream`, `/count-tokens` (optional) | `anthropic_beta`, `anthropic_version` body fields |
| Agent Platform rawPredict | `ANTHROPIC_VERTEX_BASE_URL` + `CLAUDE_CODE_USE_VERTEX=1` | `:rawPredict`, `:streamRawPredict`, `count-tokens:rawPredict` (optional) | Beta and version headers, and `anthropic_version` body field |

1. A gateway MUST expose at least one format.
2. Foundry and Claude Platform on AWS use Anthropic Messages through their own variables. A gateway fronting the latter must forward `anthropic-workspace-id`.
3. Only token counting is optional, with a character-based fallback.
4. Inference posts to `/v1/messages?beta=true`, so match on path.
5. Best-effort startup traffic may be rejected, such as `HEAD /api/hello` (skipped with a proxy or client cert), and Bedrock's inference profile list.
6. Fast mode availability and WebFetch domain checks go directly to `api.anthropic.com`, not through the gateway.

### Streaming
7. Responses MUST be relayed event by event. Buffering stalls the client.
8. The full sequence through `message_delta` and `message_stop` is required. A body ending early counts as a dropped connection.
9. SSE `ping` MUST pass; removal can trip the idle timeout during thinking. Translating gateways should synthesise keep-alives.
10. Bedrock streams MUST stay binary `application/vnd.amazon.eventstream`.

### Client behaviour by connection
| Behaviour | Bedrock/Agent Platform format | Messages format | Apps gateway sign-in |
|---|---|---|---|
| Model IDs | Provider form | Anthropic IDs | Anthropic IDs |
| `anthropic-beta` | Subset both clouds accept | Full set | Subset |
| Unknown model ID fields | Fixed-budget thinking, no effort or context management | Everything current models accept | Treated conservatively |
| 1-hour cache | `ttl` only | `ttl` plus `extended-cache-ttl` beta | `ttl` only |
| Background model | Default Sonnet or main | Main, or Haiku with a Console key | Per docs table |

11. Unknown IDs assume 200K context, 1M with `[1m]`. `modelOverrides` and `ANTHROPIC_DEFAULT_*_MODEL_SUPPORTED_CAPABILITIES` declare capabilities.

### Request headers
| Header | Note |
|---|---|
| `Authorization`, `x-api-key` | From `ANTHROPIC_AUTH_TOKEN` (bearer), `ANTHROPIC_API_KEY` (key); `apiKeyHelper` sends both |
| `anthropic-version` | `2023-06-01` |
| `anthropic-beta` | Forward verbatim, never allowlist |
| `x-claude-code-session-id` | Per session |
| `x-claude-code-agent-id`, `x-claude-code-parent-agent-id` | Subagents only; identify agents, not people |

12. `ANTHROPIC_CUSTOM_HEADERS` values also appear.
13. Hint headers (2.1.273) are sent by default on direct connections, and otherwise only with `CLAUDE_CODE_GATEWAY_HINT_HEADERS=1`; `0` stops them everywhere. They hold fixed vocabularies, tool names, durations and a random ID, never prompt text.

| Hint | Meaning |
|---|---|
| `x-claude-code-request-class` | `main`, `subagent`, `workflow`, `compaction`, `auxiliary` |
| `x-claude-code-agent-type` | Built-in type, `custom`, `teammate`, `fork` |
| `x-claude-code-compaction` | `auto`, `manual`, `reactive` |
| `x-claude-code-context-compacted` | First request after compaction |
| `x-claude-code-prev-tool-durations` | `<name>=<ms>;…`, at most 32 entries and 4 KB, percent-encoded names |
| `x-claude-code-prompt-id` | UUID per prompt (2.1.283) |

14. Absence of durations does not mean no tools ran.
15. Headers and body fields MUST be treated as open lists for Anthropic-format upstreams. Bridging to non-Anthropic schemas is the gateway's job.

### Response headers
16. `content-type` as above. `retry-after` in integer seconds; a value over 60 stops retries, outside `CLAUDE_CODE_RETRY_WATCHDOG` sessions. `x-should-retry` passes through. `anthropic-ratelimit-unified-*` forward unchanged, for plan usage display and distinguishing limits on `429`.
17. Error bodies MUST be forwarded unmodified, since recovery matches wording. Wrappers need a stable marker.

### System prompt attribution block
18. Claude Code prepends a short attribution block with version and a conversation-derived fingerprint. `api.anthropic.com` strips it positionally, so `system` must stay unchanged and the block stay first in its own entry.
19. `CLAUDE_CODE_ATTRIBUTION_HEADER=0` omits it, for gateways that must reshape. It is not a privacy control. On direct connections it stays on classifier requests. Any attestation aspects are excluded from this spec.
20. Stable for a conversation through a custom base URL since 2.1.181.

### Pass-through
21. Betas and paired body fields travel together. Stripping one half causes `400`s; removing both turns the feature off quietly. Rewriting bodies breaks pairs.
22. Pairs include: adaptive `thinking` (no beta), `context_management`, extended context and interleaved thinking (beta only), tool fields `strict` and `defer_loading`, `output_config` for effort, formats and budget, and `role: "system"` mid-conversation messages (no beta).
23. Fine-grained tool streaming stays off for custom base URLs unless `CLAUDE_CODE_ENABLE_FINE_GRAINED_TOOL_STREAMING=1`.

### Automatic recovery
24. On a rejection Claude Code MUST retry once, then persist the change: switch `thinking.type`; move mid-conversation system text into user messages; move a `cache_control` marker; drop earlier thinking blocks on signature rejection (including `bound to a different conversation`, which rewriting gateways can cause); drop the advisor tool; drop effort (including the `Unexpected value(s)` form, 2.1.310); retry without `context_management` (2.1.304); retry without tool search.
25. Other tool field rejections reach the developer.
26. `CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS=1` stops pre-release capabilities: context management, tool fields, `output_config.format` (2.1.287), task budget, and MCP tool search unless kept by managed settings (2.1.227). It leaves extended context, interleaved thinking, effort, adaptive thinking, mid-conversation system messages, the OAuth beta, and user-added `ANTHROPIC_BETAS` or `CLAUDE_CODE_EXTRA_BODY`.

### Model discovery
27. With `CLAUDE_CODE_ENABLE_GATEWAY_MODEL_DISCOVERY=1`, startup queries `/v1/models` and adds results to `/model`. Off by default so shared keys don't expose all models.
28. Skipped when a `CLAUDE_CODE_USE_*` variable is set, or the base URL is unset or `api.anthropic.com`.

### Connection
29. Gateway credentials win over saved logins, and the login stays unused. `ANTHROPIC_BASE_URL` alone with a saved claude.ai login keeps subscription limits and billing.
30. `apiKeyHelper` output is cached 5 minutes (`CLAUDE_CODE_API_KEY_HELPER_TTL_MS`).
31. `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1` stops background traffic outside the gateway, including auto-updates and the fast mode check.
32. Slack and cloud sessions are not part of a gateway deployment; gateway variables in a cloud environment are not applied. Remote Control and dictation need claude.ai identity.
33. Gateway sessions aren't eligible for the HIPAA configuration.

## Configuration & interfaces
See tables. Also `CLAUDE_STREAM_IDLE_TIMEOUT_MS`, `API_TIMEOUT_MS`, `CLAUDE_CODE_RETRY_WATCHDOG`. Rollout: confirm routing, issue developer credentials, test, distribute through managed settings, verify, and test new Claude Code releases before fleet upgrades.

## Failure modes & edge cases
- `400 Extra inputs are not permitted`: body forwarded to a stricter upstream. Forward both halves or set the disable variable.
- Credential in the wrong variable reaches an unread header.
- A proxy injecting its own envelope defeats recovery.
- Gateway-side cache keyed on the body needs the stable attribution block.

## Changes since the snapshot
- 2.1.181: stable attribution. 2.1.212: mid-conversation system block behind gateways.
- 2.1.227: tool search override. 2.1.257: keep-alive liveness.
- 2.1.273, 2.1.283: hint headers, prompt ID. 2.1.287: format stripping.
- 2.1.304: context management retry. 2.1.310: effort rejection form.
- 2.1.311: "Connection dropped" error says where to look first.

## Open questions
- The current beta header strings; docs refer elsewhere and warn that they change.
