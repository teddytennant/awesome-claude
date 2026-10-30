# Prompt caching

**Status:** shipped
**Provenance:** both
**Sources:** docs prompt-caching, model-config, costs; snapshot `services/api/claude.ts`, `services/api/promptCacheBreakDetection.ts`; changelog 2.1.108, 2.1.212, 2.1.251, 2.1.260, 2.1.268, 2.1.299, 2.1.314

## Purpose

Caching is what makes re-sending whole conversations affordable. The client's job is to keep the request prefix byte-stable, choose a TTL, and explain misses.

## Behaviour

### Prefix discipline

1. The API matches an exact prefix. The client MUST order requests by change frequency (see [system-prompt-and-context.md](system-prompt-and-context.md)) and MUST NOT modify earlier content without reason.
2. Model and speed are part of the cache identity. Effort is too on most models.
3. Tool definitions sit in the system layer. Exceptions: the advisor definition sits after the breakpoint, and deferred loading keeps the list from the first request for the whole conversation.

### Invalidating actions

| Action | Effect | Mitigation or rule |
| - | - | - |
| Model switch | Full miss | `/model` at the terminal asks to confirm only while the cache is warm and the new model didn't produce the last response |
| Effort change | Full miss on most models, with confirmation while warm | Kept on Opus 5.5, Sonnet 5.5, Haiku 5.5 and Fable 5.1 with API key or subscription; not on Bedrock, Agent Platform, Claude apps gateway, `CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS` or HIPAA |
| Fast mode toggle | Other speed's cache unusable | Automatic speed changes count |
| MCP change | Depends on deferral | Table below |
| Plugin enable or disable | Skills, commands, agents, hooks, monitors and themes append only; MCP plugins follow MCP rules | `/reload-plugins` warns and holds a full re-read; `--force` applies |
| Bare tool deny rule | Full miss only without tool search | Scoped rules never affect it |
| Compaction | Conversation layer rebuilt | System prompt and project context can stay cached |
| Image or PDF limit reached | Reprocess from the earliest removed media | Batches of oldest removed |
| Upgrade | Fresh prefix for new conversations | Updates apply on next launch only |

Without tool search:

| Mid-session change | Cache | Definitions |
| - | - | - |
| Server connects or adds tools | Invalidated | Added |
| Server drops by itself | Kept | Unchanged; calls error unless restarted |
| Remote server auto-reconnects | Kept, unless `WaitForMcpServers` gets added once | Unchanged |
| Deliberate removal | Invalidated | Removed |

4. A resumed conversation's first request includes recorded definitions for still-connecting servers.
5. A plugin enabled then disabled in one session restores the previous request shape, so the older cache entry can hit.

### Actions that keep the cache

6. Repository edits, CLAUDE.md edits, permission mode changes (except `opusplan` plan toggles), output-style changes, skill and command invocation, `/recap`, `/rewind`, spawning subagents. A skill or command naming another `model` is a model switch for that turn.

### Cache lifetime

7. TTL is decided per request and falls into two buckets: main conversation, and everything else (subagents, workflows, in-process teammates, forks, compaction, titles).

| Bucket | Subscription within plan usage | Usage credits, API key, cloud |
| - | - | - |
| Main | 1 hour | 5 minutes |
| Everything else | 5 minutes, except server-controlled helpers at 1 hour | 5 minutes |

8. Moving onto usage credits MUST drop main to five minutes unless the user chose a TTL.
9. Resolution order, first match wins: `FORCE_PROMPT_CACHING_5M=1`; bucket env var; bucket setting; subagent `experimental.cacheTtl` (a `1h` is ignored on usage credits); `ENABLE_PROMPT_CACHING_1H=1`; bucket default. Values other than `5m` or `1h` are ignored.
10. Provider notes: one hour through an LLM gateway needs the `anthropic-beta` header forwarded; Claude apps gateway uses a policy; Bedrock varies by model.

### Marker placement and gateways

11. The mid-conversation system block is cached on every provider unless experimental betas are off.
12. A gateway that forwards markers behaves like the provider. A gateway that rejects with a 400 naming `cache_control` gets the marker moved to the last conversation message until exit. A gateway that strips markers bills everything uncached.

### Scope

13. Effective scope is one machine and directory, since the prompt embeds memory paths and the conversation opens with cwd and platform. Parallel sessions in one directory can share. Sequential ones share only when the git snapshot matches.
14. A fork inherits the parent's prefix exactly, so it reads the parent's cache. A subagent has its own prefix. Workflow fan-outs hold followers up to 5 seconds so they can read the first agent's prefix.

### Observability

15. Statistics come from `cache_creation_input_tokens` and `cache_read_input_tokens`, so they work on every provider.
16. `/usage` shows a `Prompt cache (main)` line after the first response (2.1.251): requests, percent of input from cache, misses, re-cached tokens, expected rebuilds, warm or cold with TTL. It names a likely cause when known (2.1.260), including thinking mode and display changes (2.1.280). It reports `no prompt caching reported by the API` when applicable. Subagents are excluded and `/clear` resets it.
17. Compaction and tool-result clearing count as expected rebuilds, not misses.
18. Status line scripts read the `prompt_cache` object.
19. `claude -p … --output-format json` reports writes under `usage.cache_creation.ephemeral_1h_input_tokens` and `ephemeral_5m_input_tokens`.
20. A startup warning appears when caching is disabled by variable (2.1.108).

### Idle compaction

21. A conversation of 200K tokens or more left idle about 54 minutes on the one-hour TTL is compacted before expiry (2.1.299). `CLAUDE_CODE_IDLE_COMPACT_MIN_TOKENS` changes the minimum, `idleCompaction: false` disables. From 2.1.314 it also runs for subscribers with telemetry off and on third-party providers and gateways once the one-hour cache is on.

## Configuration & interfaces

| Item | Effect |
| - | - |
| `DISABLE_PROMPT_CACHING` | All models |
| `DISABLE_PROMPT_CACHING_{HAIKU,SONNET,OPUS,FABLE}` | The model that alias resolves to, wherever it runs; Fable covers Fable only |
| `promptCacheTtl`, `CLAUDE_CODE_PROMPT_CACHE_TTL` | Main bucket |
| `subagentPromptCacheTtl`, `CLAUDE_CODE_SUBAGENT_PROMPT_CACHE_TTL` | Other bucket |
| `ENABLE_PROMPT_CACHING_1H`, `FORCE_PROMPT_CACHING_5M` | Global controls |

`ENABLE_PROMPT_CACHING_1H_BEDROCK` is deprecated but honoured.

## Failure modes & edge cases

- A different Sonnet or Opus version pinned as the main model keeps caching under the family variables, so use `DISABLE_PROMPT_CACHING` for it.
- A stripping gateway fails silently. The symptom is creation tokens high on every turn or `no prompt caching reported by the API`.
- `/compact` after a break longer than the TTL is the most expensive case.

## Changes since the snapshot

- 2.1.108: 1-hour opt-in, 5-minute override, `/model` warning, startup warning.
- 2.1.212: mid-conversation block behind gateways.
- 2.1.251: `Prompt cache (main)`.
- 2.1.260: likely-cause text; Fable 5.1 effort changes keep the cache.
- 2.1.268: stable tool list on third-party providers.
- 2.1.299: idle compaction.
- 2.1.314: idle compaction widened.

## Open questions

- Whether the snapshot's client-side cache-break detection is the implementation of likely-cause reporting.
- Which helper requests the server gives a one-hour TTL.
