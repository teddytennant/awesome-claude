# Request shaping: thinking, effort, 1M context and betas

**Status:** shipped
**Provenance:** both
**Sources:** docs model-config, env-vars, llm-gateway-protocol, errors; snapshot `services/api/claude.ts`, `utils/thinking.ts`, `utils/effort.ts`, `utils/betas.ts`, `constants/betas.ts`; changelog 2.1.111, 2.1.154, 2.1.166, 2.1.223, 2.1.251, 2.1.285, 2.1.287, 2.1.311

## Purpose

How session configuration turns into fields on an API request. User-facing effort resolution is in [effort-and-thinking.md](effort-and-thinking.md), window selection in [context-window-sizing.md](context-window-sizing.md).

## Behaviour

### Thinking parameter

1. Adaptive models (Fable, Sonnet 5 and later, Haiku 5.5, Opus 4.7 and later) MUST receive adaptive thinking with effort, not a fixed budget.
2. Opus 4.6 and Sonnet 4.6 use adaptive thinking unless `CLAUDE_CODE_DISABLE_ADAPTIVE_THINKING=1`, which falls back to a fixed budget from `MAX_THINKING_TOKENS`.
3. `MAX_THINKING_TOKENS` is capped to one below the request's max output tokens, and never below 1,024.
4. Thinking off on the Anthropic API sends an explicit disabled configuration (2.1.166). On third-party providers the parameter is omitted, and adaptive models may still think.
5. `CLAUDE_CODE_DISABLE_THINKING=1` omits the parameter everywhere, as a proxy compatibility measure.
6. Opus 5.5, Sonnet 5.5, Haiku 5.5 and Fable MUST ignore every thinking-off control. See [effort-and-thinking.md](effort-and-thinking.md).
7. Interactive sessions on the Anthropic API request redacted thinking by default; `showThinkingSummaries: true` requests summaries. Thinking tokens are billed either way.
8. Interleaved thinking uses a beta header, suppressed by `DISABLE_INTERLEAVED_THINKING`.
9. Subagents and compaction inherit the session's thinking configuration (2.1.198).

### Effort parameter

10. Effort goes in `output_config.effort` when the model supports it, with the appropriate beta header. Unsupported levels step down to the highest supported level at or below the request.
11. With thinking off on a model that rejects high effort without thinking, such as Opus 5, the client MUST send `high` instead (documented from v2.1.251).
12. `CLAUDE_CODE_EFFORT_LEVEL=auto|unset` omits the effort field so the API default applies, unless a `maxEffortLevel` below `max` is in force, in which case the client's own default lowered to the cap is sent.
13. Whether effort is part of the cache key depends on the model; see [prompt-caching.md](prompt-caching.md).

### Output tokens

14. `max_tokens` comes from the model's default, overridden by `CLAUDE_CODE_MAX_OUTPUT_TOKENS` and clamped to the model's cap. Unknown model IDs default to 32,000 with a 128,000 cap.
15. Non-streaming requests are limited to 64,000.
16. A context-overflow rejection retries with a reduced value (see [api-client.md](api-client.md)). The snapshot's floor is 3,000 tokens.

### 1M context on the wire

17. A `[1m]` suffix MUST be stripped before the model ID reaches the provider. It is a client-side marker.
18. Native-1M models need no suffix. Opus 4.6 and Sonnet 4.6 reach 1M only through `[1m]`, which requests the context-1m beta.
19. `CLAUDE_CODE_DISABLE_1M_CONTEXT=1` MUST stop requesting 1M and holds native-1M models to a 200K window through auto-compaction (2.1.223). A `context-1m` beta added through `ANTHROPIC_BETAS` or `--betas` still requests it, which triggers a warning.
20. Plan checks for `[1m]` run only on a direct Anthropic API connection.
21. Since 2.1.311, model names and IDs drop the `[1m]` suffix and label where it has no effect. The suffix remains accepted.

### Beta headers

22. The client MUST assemble `anthropic-beta` from model capability, provider, feature state and user additions. The snapshot latches some headers once sent, so a mid-session feature flip doesn't change the header and break the cache.
23. `--betas` is limited to API-key users. `ANTHROPIC_BETAS` adds values without that limit.
24. `CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS=1` strips pre-release beta headers, their paired body fields, and tool-schema fields such as `defer_loading` and `eager_input_streaming`. It also uncaches the mid-conversation system block.
25. `CLAUDE_CODE_DISABLE_STRUCTURED_OUTPUTS=1` removes only `output_config.format` and its beta.
26. Requests may carry server tools such as web search and the advisor. The advisor entry sits after the cache breakpoint (see [advisor.md](advisor.md)).

### Other body and header controls

27. `CLAUDE_CODE_EXTRA_BODY` merges JSON into the top level of every request. `/bug` and `/feedback` reports omit its fields (2.1.273).
28. The system prompt may begin with an attribution block carrying the client version and a prompt fingerprint. `CLAUDE_CODE_ATTRIBUTION_HEADER=0` omits it. In some direct-connection setups the block stays on auto mode classifier requests regardless.
29. `CLAUDE_CODE_GATEWAY_HINT_HEADERS=1` adds `x-claude-code-*` hint headers for gateways (2.1.273), including `x-claude-code-prompt-id` (2.1.283).
30. `ANTHROPIC_BEDROCK_SERVICE_TIER` sets a Bedrock service tier header (2.1.122).
31. `ANTHROPIC_WORKSPACE_ID` scopes workload-identity tokens (2.1.141).
32. Bedrock, Mantle and Claude Platform on AWS sign the port in the Host header on non-default ports (2.1.285).

## Configuration & interfaces

| Capability value | Enables |
| - | - |
| `effort` | Effort and `/effort` |
| `xhigh_effort`, `max_effort` | Those levels |
| `thinking`, `adaptive_thinking`, `interleaved_thinking` | Thinking variants |

Pinned third-party models declare capabilities with `ANTHROPIC_DEFAULT_{OPUS,SONNET,HAIKU,FABLE}_MODEL_SUPPORTED_CAPABILITIES` or `ANTHROPIC_CUSTOM_MODEL_OPTION_SUPPORTED_CAPABILITIES`. When set, unlisted capabilities are disabled. When unset, detection is by model ID.

## Failure modes & edge cases

- `thinking.type.enabled is not supported`: client older than the model's minimum.
- `max_tokens must be greater than thinking.budget_tokens`: raise `CLAUDE_CODE_MAX_OUTPUT_TOKENS`.
- `Effort 'xhigh' isn't available with thinking turned off`: the client's own wording, varying by surface.
- Provider IDs that match no pattern silently lose effort and thinking until capabilities are declared.

## Changes since the snapshot

- 2.1.111: `xhigh`.
- 2.1.154: lean system prompt default for newer models.
- 2.1.166: thinking-off controls send a real disable on the Claude API.
- 2.1.223: `CLAUDE_CODE_DISABLE_1M_CONTEXT` covers every native-1M model.
- 2.1.285: gateways get native 1M windows.
- 2.1.287: Opus 4.7+ and Fable default to 1M on Bedrock, Vertex, Foundry and the apps gateway.
- 2.1.311: `[1m]` dropped from names where it has no effect.

## Open questions

- Whether the 3,000-token floor is current. The docs only say retries stop when `max_tokens` can't shrink further.
- Full current beta list. Docs intentionally describe a subset.
