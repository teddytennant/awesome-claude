# Context window sizing and auto-compact window

**Status:** shipped
**Provenance:** both
**Sources:** docs model-config, env-vars, settings-reference, errors; snapshot `services/compact/autoCompact.ts`, `utils/context.ts`; changelog 2.1.223, 2.1.247, 2.1.260, 2.1.285, 2.1.287, 2.1.288, 2.1.299

## Purpose

Determines the window size Claude Code assumes for a model and how full it may get before compaction. How compaction works is covered by the memory-context spec area.

## Behaviour

### Window per model

1. Native 1M with no suffix: Fable 5.1, Fable 5, Sonnet 5 and later, Haiku 5.5, Opus 4.7 and later, on every provider and through the Claude apps gateway (2.1.287).
2. Opus 4.6 and Sonnet 4.6 reach 1M only through `[1m]`. Plan rules: Opus 4.6 1M is included on Max, Team and Enterprise and needs usage credits on Pro. Sonnet 4.6 1M needs usage credits on every subscription. API and pay-as-you-go have full access.
3. Plan checks run only on direct Anthropic API connections. Behind a gateway the `[1m]` options stay available and the gateway decides.
4. Behind `ANTHROPIC_BASE_URL`, recognized models get the same window as on the Anthropic API (2.1.285). The client cannot detect a lower gateway limit.
5. A pinned ID matches a known model when it contains the Anthropic ID or is mapped by `modelOverrides`. Otherwise it is 200K unless it carries `[1m]`. The suffix is read per variable.
6. Pricing: 1M uses standard pricing except Haiku 5.5, which costs more on prompts over 100K tokens.

### Unknown IDs

7. An unrecognized ID assumes 200K, with a startup warning. Fixes: `claude update`; `modelOverrides` entry; `modelPicker` row with `behavesAs`; `[1m]` suffix; `CLAUDE_CODE_MAX_CONTEXT_TOKENS`.
8. `CLAUDE_CODE_MAX_CONTEXT_TOKENS` rules: an unrecognized non-`claude-` spelling without `[1m]`: applies directly. With `[1m]`: 1M is assumed and the variable needs `CLAUDE_CODE_DISABLE_1M_CONTEXT=1` as well. A recognized ID or bare `claude-` name: applies only with `DISABLE_COMPACT`. Stripped suffixes such as `@YYYYMMDD` count as provider spelling.
9. Sessions on unknown IDs compact within the assumed window (2.1.223). `CLAUDE_CODE_DISABLE_UNKNOWN_MODEL_WINDOW_ENFORCEMENT=1` compacts only after a recognized too-long rejection.

### Disable 1M

10. `CLAUDE_CODE_DISABLE_1M_CONTEXT=1` removes `[1m]` rows and treats native-1M models as 200K. Auto-compaction holds at 200K. With auto-compaction off, sessions stop with the context-limit error. A window above 200K doesn't lift the hold.
11. A warning appears when other configuration defeats that limit. See `The 200K limit isn't enforced`.

### Auto-compact window

12. Sources, highest first: `CLAUDE_CODE_AUTO_COMPACT_WINDOW`; `--autocompact`; `modelSettings.<model>.autoCompactWindow` (saved by `/autocompact`); top-level `autoCompactWindow`. All are capped at the model's window.
13. `/autocompact 500k` saves per model (2.1.288) and applies now. `/autocompact auto` returns to the tuned window. If a higher settings scope sets a window, the command saves but the session keeps that scope's value, and says so.
14. `--autocompact` isn't preempted by managed settings, and `--autocompact auto` ignores saved values.
15. Accepted forms for command and flag: 100K to 1M as a count, `k` or `M` suffix, or a bare 100 to 1000 meaning thousands.
16. The variable differs: `200` means 200 tokens. It accepts `k` and `M` from the docs' v2.1.304. Warnings: `reads as <N> tokens…` (treated as 100k minimum), `is too large…` (1M maximum), `isn't a usable size…` (ignored).
17. `/autocompact` reports the override when the variable is set. Status line `used_percentage` measures the full window, so doesn't show when compaction will run.
18. Subagents can set their own window.

### Default thresholds

19. No window set: compact at the model's context limit, except: cloud sessions compact as they approach it; Sonnet 4.6 and Opus 4.6 without 1M at 200K; `CLAUDE_CODE_DISABLE_1M_CONTEXT` at 200K; native 1M at about 967K (2.1.247, 2.1.260); unknown IDs at the assumed window.
20. Snapshot reserved buffers: 13,000 below the effective window for auto-compact, 20,000 for warning and error thresholds, 3,000 for manual compact. Current numbers aren't documented.

### Idle compaction

21. See [prompt-caching.md](prompt-caching.md).

## Configuration & interfaces

| Item | Notes |
| - | - |
| `autoCompactEnabled` | User toggle in `/config` |
| `DISABLE_AUTO_COMPACT`, `DISABLE_COMPACT` | Off; settings or mod `$.env.set` can only turn compaction off (2.1.311) |
| `CLAUDE_CODE_AUTO_COMPACT_WINDOW` | Variable |
| `autoCompactWindow`, `modelSettings` | Settings |
| `--autocompact` | Flag |

## Failure modes & edge cases

- `Usage credits required for 1M context`: credits needed; turning them on mid-session takes effect after restart (2.1.268).
- A window drop on fallback shows in the fallback notice (2.1.286).
- Compaction can't fall back to a smaller window. See [model-fallback.md](model-fallback.md).
- Recovery compaction on very large contexts no longer times out at 10 minutes (2.1.260).
- `Prompt is too long` when auto-compact is off carries hints about `/config`, unless a higher scope or `DISABLE_*` decided it.

## Changes since the snapshot

- 2.1.223: unknown-ID enforcement; 1M disable broadened.
- 2.1.247: Sonnet 5 compacts at about 967K.
- 2.1.260: Opus and Fable compact shortly before 1M.
- 2.1.285: gateways get 1M.
- 2.1.287: 1M default on third-party providers.
- 2.1.288: per-model window.
- 2.1.299: one-line unknown-model warning.

## Open questions

- Whether "compact at about 967K" derives from the snapshot buffers or a separate tuned number.
