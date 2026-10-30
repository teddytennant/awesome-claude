# Model selection, aliases and picker

**Status:** shipped
**Provenance:** both
**Sources:** docs model-config, errors, settings-reference (`modelPicker`, `modelOverrides`), commands, third-party-integrations; snapshot `utils/model/`, `commands/model`; changelog 2.1.117, 2.1.144, 2.1.196, 2.1.197, 2.1.219, 2.1.236, 2.1.243, 2.1.257, 2.1.268, 2.1.280, 2.1.284, 2.1.293, 2.1.301, 2.1.311

## Purpose

Decides which model a session uses, how names resolve per provider, and what `/model` shows. Allowlists are in [model-restrictions.md](model-restrictions.md).

## Behaviour

### Aliases

| Alias | Resolves to |
| - | - |
| `default` | Clears overrides; runtime default. Not itself an alias |
| `best` | `fable` target where available, else `opus` |
| `fable` | Fable 5.1, or Fable 5 in Claude apps gateway sessions |
| `opus`, `sonnet`, `haiku` | Newest for the provider |
| `opus[1m]`, `sonnet[1m]` | With 1M window; no effect on native-1M targets |
| `opusplan` | Opus in plan mode, Sonnet in execution |

| Provider | `opus` | `sonnet` | `haiku` |
| - | - | - | - |
| Anthropic API | Opus 5.5 | Sonnet 5.5 | Haiku 5.5 |
| Claude Platform on AWS | Opus 5.5 | Sonnet 4.6 | Haiku 4.5 |
| Bedrock, Agent Platform | Opus 5.5 | Sonnet 4.5 | Haiku 4.5 |
| Foundry | Opus 4.6 | Sonnet 4.5 | Haiku 4.5 |

1. Alias targets update with releases. Full model IDs pin. Minimum versions: Opus 5.5 at 2.1.280, Sonnet 5.5 at 2.1.284, Haiku 5.5 at 2.1.293, Fable 5.1 at 2.1.257.
2. `ANTHROPIC_DEFAULT_{OPUS,SONNET,HAIKU,FABLE}_MODEL` redirect aliases and the account default's version. `ANTHROPIC_SMALL_FAST_MODEL` is deprecated.
3. `CLAUDE_CODE_SUBAGENT_MODEL` sets the default for subagents, teammates and workflow agents. `CLAUDE_CODE_SUBAGENT_MODEL_FORCE` lets it override per-invocation and definition models.

### Precedence

4. First match wins: `/model` in session; `--model`; `ANTHROPIC_MODEL`; `model` setting; `ANTHROPIC_DEFAULT_MODEL`.
5. `ANTHROPIC_DEFAULT_MODEL` (2.1.236) applies only when no flag, variable, settings `model` or organization default selects a model. It is ignored when set to `default`, `inherit`, `opusplan` or `haiku`, under `enforceAvailableModels`, when restrictions exclude it, or when the account lacks it. When a new session would start on it, resume does too, without restoring the transcript's model.
6. **Default option** resolves in this order: organization default; `ANTHROPIC_DEFAULT_MODEL`; a model recorded on the Enterprise account; account-type default. Enforcement steps apply afterwards.
7. Account-type default: Opus 5.5 on Pro, Max, Team, Enterprise, Anthropic API, Claude Platform on AWS, Bedrock and Agent Platform; Sonnet 4.5 on Foundry. Fable is never the account default.

### Persistence

8. `/model` and picker `Enter` switch and write `model` to user settings. `s` in the picker switches for this session only (`modelPicker:thisSessionOnly`). Typing `/model <name>` behaves like `Enter`.
9. On Enterprise with a claude.ai login, a saved default is also recorded on the account (2.1.280). Default and `opusplan` don't change that record.
10. `--model` and `ANTHROPIC_MODEL` apply to that launch only.
11. `/model` in `-p` is session-only and unsaved.
12. A write failure to `~/.claude/settings.json` leaves the choice session-only and reports `Couldn't save it as your default`.
13. When the active model comes from project or managed settings, the startup header names the file. A user's `/model` choice persists but is outranked.
14. On a direct Anthropic API connection, a `claude-fable-5` or `claude-fable-5[1m]` value in user settings MUST migrate to the `fable` or `fable[1m]` alias the first time 2.1.257 or later runs, shown once as `(auto-updated)`. Values in project, local or managed settings stay.

### Resume

15. A resumed session keeps its transcript's model. It falls through to normal precedence if the model is retired or disallowed, or on providers with deployment-specific IDs (Bedrock, Agent Platform, Foundry).
16. `--model`, `ANTHROPIC_MODEL` and, as of the docs' v2.1.195, an `ANTHROPIC_DEFAULT_*_MODEL` family variable beat the restored model.
17. With `model: haiku`, a session saved on an older Haiku resumes on the current target.

### Switching

18. Before a switch applies, `PreModelSwitch` hooks run and may block or ask (2.1.251). If managed plugins that might carry such hooks can't be determined, the switch is refused and rechecked on each new attempt.
19. A switch at the terminal asks to confirm while the cache is warm (see [prompt-caching.md](prompt-caching.md)).
20. Switching to a smaller context window: a conversation too long for the new model is first summarized by the previous model (2.1.301).
21. Subagents that inherit resolve from the session's current model when started, so a `/model` switch reaches them.
22. Validation at the switch: Agent SDK `setModel()` and app switches confirm the ID with the provider once per session, unless accepted locally (documented from v2.1.268). Remote Control checks locally without a request. `--model`, `ANTHROPIC_MODEL` and `model` are not checked up front, so a typo fails on the first request.
23. Deprecation or remap warnings name the requested model: startup notice interactively, stderr in plain-text `-p` (2.1.183), covering subagent frontmatter; suppressed for JSON outputs, where `modelUsage` tells the truth.

### Picker

24. Rows show alias-based entries, a Default row and optional custom rows. Left and right arrows adjust the effort slider. Only the newest model's name is highlighted (2.1.219, 2.1.236).
25. The Default row shows labels: the organization default's name with `Org default`, or `Set by ANTHROPIC_DEFAULT_MODEL`.
26. A separate row for the usual account family stays when an org default differs (documented from v2.1.199).
27. Prices appear only for the Anthropic API or gateways proxying it, and describe the row's model. Third-party providers and the Claude apps gateway show none.
28. A pinned `ANTHROPIC_DEFAULT_*_MODEL` shows one row in place of the family's. `_NAME`, `_DESCRIPTION` and `_SUPPORTED_CAPABILITIES` companions customize it on third-party providers; the first two also work behind a gateway.
29. `ANTHROPIC_CUSTOM_MODEL_OPTION` adds one row after built-ins, unvalidated, with `_NAME` and `_DESCRIPTION`. It must be in `availableModels` if that is set.
30. `modelPicker` (2.1.243) adds or replaces rows: `options[]` with `model`, `label`, `description`, and `behavesAs`, plus `replaceBuiltInOptions`. It is read from managed settings, `--settings` and user settings, never project or local; the highest wins whole.
31. `CLAUDE_CODE_ENABLE_GATEWAY_MODEL_DISCOVERY=1` populates from the gateway's `/v1/models` (opt-in since 2.1.129, timeout variable 2.1.269, `description` field 2.1.257, runs under nonessential-traffic off since 2.1.257).
32. Fable appears on the Anthropic API unless excluded. When the organization can't use it, the row stays grayed out with a note (2.1.277). It may show `Requires usage credits`.

### Fable usage-credits consent

33. Where Fable bills to usage credits, an interactive consent prompt appears (not for Enterprise with organization billing). Declining at `/model` keeps the current model; mid-session it continues on the default model.
34. Unattended contexts (Remote Control connected, background session, teammate): hold until the `dialogExpiry` deadline, default five minutes, then end the turn without sending the request, add a transcript notice, and ask again next message. Any key at the terminal cancels the deadline for Remote Control and teammates.
35. `-p` and SDK hosts that don't show it bill without asking.

### Overrides and third-party IDs

36. `modelOverrides` maps Anthropic model IDs to provider strings. Keys must be Anthropic IDs. Unknown keys are ignored.
37. It applies to picker rows, `--model`, `ANTHROPIC_MODEL` and `ANTHROPIC_DEFAULT_*_MODEL`. On Bedrock it beats discovered inference profiles.
38. On Bedrock, Agent Platform and Mantle, an Anthropic ID with no override resolves to the same provider ID as the picker. Mantle supports a subset; others pass raw.
39. Bedrock and Agent Platform run startup model checks. If the default isn't enabled, they fall back to an earlier version, or to Sonnet if no Opus exists, with a notice. Results are remembered for up to a day (2.1.285). Explicit Sonnet or Opus choices skip the replaced default (documented from v2.1.211). Foundry has no such check.
40. Since 2.1.311, Bedrock, Mantle, Vertex and Foundry load model settings from a signed file; `CLAUDE_CODE_MODEL_CATALOG=off` disables.

## Configuration & interfaces

| Key | Effect |
| - | - |
| `model`, `ANTHROPIC_MODEL`, `--model` | Selection |
| `ANTHROPIC_DEFAULT_MODEL` | New-session default |
| `modelOverrides`, `modelPicker` | Mapping and lineup |
| `/model [name]` | Switch |
| `dialogExpiry` | Unattended prompt deadline |

## Failure modes & edge cases

See [errors-catalogue-api.md](errors-catalogue-api.md) for model errors. A gateway not configured for `claude-fable-5-1` rejects it, and `/model claude-fable-5-1` selects it explicitly where it is served.

## Changes since the snapshot

- 2.1.117: `/model` choices persist despite project pins.
- 2.1.144 to 2.1.152: `/model` was session-only for a period, with `d` to save; documented as reverted.
- 2.1.196: organization default models.
- 2.1.219, 2.1.280, 2.1.284, 2.1.293: alias targets.
- 2.1.236: `ANTHROPIC_DEFAULT_MODEL`.
- 2.1.243: `modelPicker`.
- 2.1.251: `PreModelSwitch`.
- 2.1.301: summarize before switching to a smaller window.
- 2.1.311: signed model catalog.

## Open questions

- Selection order between account-recorded model and `ANTHROPIC_DEFAULT_MODEL` is inferred from "unless an organization default model applies" and may differ.
- The changelog says 2.1.196 labels include "Role default", while docs say the label reads Org default for both.
