# Model fallback

**Status:** shipped
**Provenance:** both (single `--fallback-model` predates the leak; chains and content fallback are post-leak)
**Sources:** docs model-config, errors, settings-reference, prompt-caching; snapshot `query.ts`, `services/api/withRetry.ts`; changelog 2.1.152, 2.1.166, 2.1.219, 2.1.284, 2.1.285, 2.1.286, 2.1.287, 2.1.312, 2.1.314

## Purpose

Two independent mechanisms keep a session moving: availability fallback for overload and unavailable models, lasting a turn; and content fallback for requests a safety classifier flags, lasting the session.

## Behaviour

### Availability: fallback chains

1. Triggers: overloaded, unavailable or other non-retryable server errors. Also a Bedrock or Agent Platform refusal of a model the account can't invoke.
2. MUST NOT trigger on: auth, billing, rate-limit, request-size or transport errors, or an organization policy denial.
3. A configured chain is tried in order, with a notice on each switch. The switch lasts for the current turn; the next message tries the primary.
4. An entry that fails also fails over to the next, such as a retired pin.
5. Chains are capped at three after deduplication. Extras are ignored.
6. `"default"` expands to the default model. `--fallback-model` (comma-separated) beats the `fallbackModel` setting.
7. No startup confirmation; `/status` doesn't show it. The first switch notice is the first sign.
8. Entries outside the allowlist are dropped on read.
9. Compaction uses the chain but MUST NOT fall back to a smaller context window, which would truncate before summarizing. If every entry is smaller, compaction shows the original error.
10. Subagents use the chain (documented from v2.1.247), continuing on the accepting model. The session model doesn't change.
11. A notice says when a fallback dropped the window from 1M to 200K (2.1.286).
12. `/bg` and detach preserve the chain (2.1.143).
13. Mid-turn mechanics: thinking and other model-bound blocks are stripped from history so the next model accepts it, and any partial attempt is retracted. See [query-loop.md](query-loop.md).
14. Unexpected non-retryable errors retry the turn once on the fallback model (2.1.166).

Changelog 2.1.152 said a not-found primary switches for the rest of the session, while current docs say any chain switch lasts the turn. See Open questions.

### Availability on Bedrock and Agent Platform

15. When access to a model is removed mid-session, the session switches to an older available model of the same tier instead of failing (2.1.285). Titles and summaries follow.
16. `CLAUDE_CODE_DISABLE_MODEL_ACCESS_FALLBACK=1` makes the refused request fail at once. A configured chain still switches.
17. The switch skips excluded models.

### Automatic overload suggestion

18. A 529 storm on one model produces `Opus is experiencing high load, please use /model to switch to Sonnet` or the Fable variant. Desktop apps omit the command.

### Content: automatic model fallback

19. Sources: Fable 5.1, Fable 5, Opus 5.5, Sonnet 5.5, Opus 5.

| Refusing model | Biology flag | Cybersecurity flag |
| - | - | - |
| Fable 5.1, Fable 5, Opus 5.5 | Re-run on Opus 5 | Re-run on Opus 4.8 |
| Sonnet 5.5 | Refusal | Re-run on Sonnet 5 |
| Opus 5 | Refusal | Re-run on Opus 4.8 |

20. In the main conversation, the switch shows a transcript notice. The session stays on the fallback model until `/model`. That is a model switch for caching.
21. Effort: the flagged request's level carries over (2.1.287), until the user changes effort, picks a model or resumes. A one-turn level from `ultrathink` or a skill applies to that turn only, and later turns resolve for the new model.
22. Fallback can fire on the very first request, since it carries CLAUDE.md and git status. `--safe-mode` tests customizations.
23. From 2.1.284, sessions pinning an Opus on the Anthropic API get the API's per-flag model choice, not the pin.
24. `CLAUDE_CODE_DISABLE_REFUSAL_FALLBACK=1` disables switching. Since 2.1.312 switches also cover unrecognized names such as custom deployments.

### Consent

25. `switchModelsOnFlag: false` (or `/config` → **Switch models when a message is flagged** → **Ask each time**) pauses at a flagged request with switch, or edit and retry.
26. The first time, interactively, with the key unset, Claude Code may ask whether to switch automatically. It saves the answer in user settings: staying saves `false`, dismissing saves nothing.
27. In Ask mode: no fallback category means refusal with no prompt; both models flagging offers edit or new session; mobile cloud sessions can't edit and retry; non-interactive and SDK contexts that can't prompt end the turn with a refusal; subagents don't prompt and re-run; a blocked target ends with a refusal.

### Third-party providers

28. Fallback runs only when both models are identifiable. Source: ID contains `claude-fable-5`, matches `ANTHROPIC_DEFAULT_FABLE_MODEL`, or is mapped by `modelOverrides`. Opus 5.5, Sonnet 5.5 and Opus 5 are recognized by provider ID or mapping.
29. An Opus target must resolve in the deployment for every source, including Sonnet 5.5: `ANTHROPIC_DEFAULT_OPUS_MODEL`, or an Opus 4.8 entry in the provider's list.
30. With that pin, all categories with a fallback re-run on it. Without it, cyber uses the Opus 4.8 entry and biology from Fable or Opus 5.5 uses an Opus 5 entry. Sonnet 5.5 cyber uses `ANTHROPIC_DEFAULT_SONNET_MODEL` or a Sonnet 5 entry.
31. A pin outside the family, or naming the refusing model, leaves the refusal.
32. The fallback MUST have a context window at least as large as the session's, or there is no switch.

### Refusal without fallback

33. A refusal surfaces as `API Error: <model> can't help with this. …` with request and message IDs. Evaluating the whole conversation means new messages usually re-trigger it. See [errors-catalogue-api.md](errors-catalogue-api.md).

## Configuration & interfaces

| Key | Effect |
| - | - |
| `--fallback-model a,b` | Session chain |
| `fallbackModel` | Persistent array |
| `switchModelsOnFlag` | `false` asks each time |
| `CLAUDE_CODE_DISABLE_REFUSAL_FALLBACK` | Off |
| `CLAUDE_CODE_DISABLE_MODEL_ACCESS_FALLBACK` | Off for provider access loss |

## Failure modes & edge cases

- Persistent biology work on Fable moves to Opus 5 once, then refuses there, since Opus 5 has no biology fallback.
- A fallback that retracts completed structured output with no retry ends in `error_max_structured_output_retries`.

## Changes since the snapshot

- 2.1.152: `--fallback-model` used when the primary isn't found.
- 2.1.166: `fallbackModel`, chains, interactive use, one-turn retry on unexpected errors.
- 2.1.219: category-based fallback; Opus 5 as a source.
- 2.1.284: API picks targets for pinned Opus on the Anthropic API; Sonnet safeguards notice.
- 2.1.285: same-tier fallback on access loss.
- 2.1.286: notices name a window drop.
- 2.1.287: effort carried across switches.
- 2.1.312: unrecognized names covered.
- 2.1.314: flagged requests retry on another model when pins or lists leave only an older Opus or none, which relaxes earlier refusal rules.

## Open questions

- 2.1.152 says "for the rest of the session" for a not-found primary, while docs say a switch lasts the turn. Current behaviour for not-found primaries is unclear.
- Exactly how 2.1.314 relaxes the third-party target requirements, since docs still state refusals in those cases.
