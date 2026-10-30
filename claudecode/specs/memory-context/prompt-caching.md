# Prompt caching behaviour

**Status:** shipped
**Provenance:** both (TTL controls, cache statistics and most stability guarantees post-leak)
**Sources:** docs `prompt-caching`, `settings-reference`, `model-config`, `hooks`, `costs`, `statusline`; snapshot `services/api/claude.ts`, `services/compact/`; changelog versions cited below

## Purpose

Keep each request's prefix byte-stable, so the API reuses prior processing. The client manages this automatically. The specification below is what a client must keep stable, and what it must do when it cannot.

## Behaviour

### Prefix structure

1. Each request MUST re-send full context, ordered from least to most volatile: system prompt with tool definitions; project context (CLAUDE.md, auto memory, unscoped rules); conversation.
2. Matching is by exact prefix. A change anywhere recomputes everything after it, with no per-file caching.
3. Plan mode, skill loading and output-style switches MUST arrive as conversation messages, so they do not disturb the prefix. Since v2.1.257, `/fork` briefings do the same.
4. System context appended mid-conversation, such as file-change notices, MUST be marked for caching on every provider, unless `CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS` is set.
5. The advisor tool's definition sits after the cache breakpoint, so toggling `/advisor` keeps the prefix.

### Gateways

6. If a gateway rejects the marked block with a 400 naming `cache_control`, the client MUST re-send with the marker moved to the last conversation message, and keep that until exit. A gateway silently stripping markers leaves everything uncached.
7. One-hour TTL through a gateway needs the `anthropic-beta` header forwarded.

### Actions that invalidate

8. **Model switch**: each model has its own cache. `/model` MUST confirm only while the cache is warm and the new model differs from the one that produced the last response; a `PreModelSwitch` hook can require or skip this. `opusplan` toggles, automatic fallback, and a skill's `model` frontmatter are all model switches.
9. **Effort change**: invalidates on most models, confirmed while warm. On Opus 5.5, Sonnet 5.5, Haiku 5.5 and Fable 5.1 with an API key or subscription, the cache is kept, except on Bedrock, Agent Platform, a Claude apps gateway, under `CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS`, or under HIPAA.
10. **Fast mode**: fast and standard speed keep separate caches; each toggle, including automatic ones, reads uncached whatever the other lacks.
11. **MCP**: with tool search deferring tools, the tool list from the first request MUST stay fixed for the conversation, and later servers MUST arrive as deferred definitions. Without it, see the table below.
12. **Plugins**: skills, commands, agents, hooks, monitors and themes append and never invalidate. MCP-providing plugins follow requirement 11. `/reload-plugins` MUST warn and not apply a reload that would cause a full re-read, unless `--force` is passed. Disabling a plugin enabled earlier in the session MUST restore the previous request shape.
13. **Whole-tool deny**: a bare name, `Bash(*)` or a tool-name glob removes the tool when tool search is off. With tool search active, definitions stay and the prefix survives. Scoped rules never change the tool list.
14. **Compaction** invalidates the conversation layer. System and project layers can stay cached if files are unchanged. A resumed conversation with an outdated system prompt switches to the current one on first compaction, rebuilding that layer once.
15. **Images**: past the API's per-request limits or the client's total size cap, the client MUST remove a batch of the oldest images and PDFs, so misses occur per batch rather than per screenshot.
16. **Upgrade**: a new version typically changes the prefix. Updates MUST NOT apply mid-session.

| Change without tool search | Cache | Next request |
|---|---|---|
| Server connects, dynamic tool add | Invalidated | Definitions added |
| Server drops by itself | Kept | Definitions unchanged; calls error unless restarted |
| Remote server auto-reconnects | Kept, except adding `WaitForMcpServers` once | Definitions unchanged |
| Tool removed on purpose | Invalidated | Definition removed |

### Actions that keep the cache

17. Repository edits (a reminder is appended), CLAUDE.md edits (not applied until reload), permission mode changes except with `opusplan`, output style changes, skills and commands, `/recap`, `/rewind`, and spawning a subagent.
18. `/rewind` MUST truncate to a prefix already cached, kept warm by every later turn reading through it. Restoring files has no separate cache effect.

### Lifetime

19. Each request classifies into a bucket, **main conversation** or **everything else** (subagents, workflows, teammates, forks, compaction, session titles).

| Bucket | Subscription within plan | Usage credits, API key, cloud provider |
|---|---|---|
| Main conversation | 1 hour | 5 minutes |
| Everything else | 5 minutes, except server-controlled helpers at 1 hour | 5 minutes |

20. A subscription drawing on usage credits MUST drop the main conversation to 5 minutes, unless the user chose a TTL.
21. TTL precedence, first match wins: `FORCE_PROMPT_CACHING_5M=1`; the bucket's environment variable; the bucket's setting; a subagent's `experimental.cacheTtl` (a `1h` is ignored on usage credits); `ENABLE_PROMPT_CACHING_1H=1`; the bucket default.
22. TTL controls accept only `5m` and `1h`; anything else MUST be ignored.

### Resume

23. Resume MUST send the conversation with the system prompt recorded on its first request, so its history stays behind the same prefix. Different prompt flags take effect on compaction or in a new conversation. `--system-prompt-snapshot off` rebuilds on each request; bare mode leaves recording off unless `--system-prompt-snapshot on`.
24. If a transcript recorded a still-connecting MCP server's tools, the first resumed request MUST include them as recorded.
25. Resume MUST NOT change the re-rendered form of earlier messages or attachments.

### Scope

26. The cache is effectively per machine and directory: the system prompt embeds memory paths, and the conversation opens with environment details. Parallel sessions in one directory can share; sequential ones share only when the startup git snapshot matches.
27. A subagent starts its own cache. A fork inherits the parent's exact prefix and reads its cache. Compaction, resumed subagents and workflow fan-outs also reuse prefixes; a fan-out holds all but the first agent for up to 5 seconds by default.

### Statistics

28. `/usage` MUST add a `Prompt cache (main)` line after the first main response: hit ratio, misses, warm or cold, and likely cause of the last miss when identifiable. The same data is in the status line's `prompt_cache` object.
29. `-p --output-format json` reports `usage.cache_creation` with `ephemeral_1h_input_tokens` and `ephemeral_5m_input_tokens`.
30. `SessionStart` input includes `prompt_cache_likely_expired`.

### Disabling

31. `DISABLE_PROMPT_CACHING` disables all models. Per-family variables apply only to the model the alias resolves to, wherever it runs; a differently pinned version keeps caching. A startup warning MUST appear when caching is disabled.

## Configuration & interfaces

| Interface | Effect |
|---|---|
| `promptCacheTtl`, `CLAUDE_CODE_PROMPT_CACHE_TTL` | Main-bucket TTL |
| `subagentPromptCacheTtl`, `CLAUDE_CODE_SUBAGENT_PROMPT_CACHE_TTL` | Other-bucket TTL |
| `ENABLE_PROMPT_CACHING_1H`, `FORCE_PROMPT_CACHING_5M` | Global TTL opt-in and force |
| `DISABLE_PROMPT_CACHING`, `_HAIKU`, `_SONNET`, `_OPUS`, `_FABLE` | Disable |
| `--system-prompt-snapshot`, `--exclude-dynamic-system-prompt-sections` | Prefix stability controls |
| `CLAUDE_CODE_WORKFLOW_PREFIX_STAGGER_MS` | Fan-out hold |
| `prompt_cache` (status line), `Prompt cache (main)` (`/usage`) | Statistics |

## Failure modes & edge cases

- Tool definitions MUST NOT change on OAuth refresh, LSP disconnect, Remote Control connect or `/model`.
- `MEMORY.md` age notes MUST stay stable across resume.
- An interrupted thought or pending permission prompt at restart MUST NOT change re-sent history.
- A gateway per-request token that changes each turn defeats caching.
- A 1-hour TTL MUST NOT be silently downgraded.
- Bedrock support, minimum length and 1-hour availability vary by model; zero cache counts usually mean an unsupported model or region.

## Changes since the snapshot

- v2.1.92: Pro footer hint about uncached next turn.
- v2.1.108: `ENABLE_PROMPT_CACHING_1H`; startup warning when disabled.
- v2.1.212: mid-conversation block works behind gateways.
- v2.1.238: `/model` confirms only while warm.
- v2.1.243: TTL settings and variables.
- v2.1.248: `experimental.cacheTtl`.
- v2.1.251: `Prompt cache (main)` and `prompt_cache`; mid-session output style applies.
- v2.1.257: `/fork` keeps cache.
- v2.1.260: likely-cause text; effort keeps cache on Fable 5.1.
- v2.1.265, v2.1.267: subagent and system prompt recording; `--system-prompt-snapshot` defaults reworked.
- v2.1.267: `/model` no longer re-sends tool definitions.
- v2.1.281: MCP disconnects and connecting-at-resume keep cache without tool search.
- v2.1.283: `DISABLE_PROMPT_CACHING_HAIKU` covers the main model.
- v2.1.299: idle compaction before one-hour expiry.

## Open questions

- Which helper requests the server grants one hour.
- Whether the snapshot's cache-break detection (`PROMPT_CACHE_BREAK_DETECTION`) is what produces the likely-cause text.
