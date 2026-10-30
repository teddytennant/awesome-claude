# Model restrictions and organization defaults

**Status:** shipped
**Provenance:** both (`availableModels` predates the leak; all else post-leak)
**Sources:** docs model-config, settings-reference, errors, managed-settings; snapshot `utils/model/modelAllowlist.ts`; changelog 2.1.187, 2.1.196, 2.1.267, 2.1.283, 2.1.285, 2.1.314

## Purpose

Lets administrators limit which models and effort levels a session can use, and set defaults. Precedence for choosing a model is in [model-selection.md](model-selection.md).

## Behaviour

### `availableModels`

1. Entries match a family (`sonnet`), a version prefix (`claude-sonnet-4-5`) or a full ID. A version prefix also matches later IDs extending it with another segment, so `claude-fable-5` permits Fable 5 and 5.1.
2. An entry naming a specific model in a family disables that family's wildcard. Mantle IDs and custom IDs embedding a family name count as specific.
3. `availableModels: []` blocks named selections.
4. Merge: a managed list applies alone (unless a host supplies its own) and is never merged across managed sources. Otherwise user, project and local lists concatenate and deduplicate.
5. The allowlist MUST apply to: `/model`, `--model`, `ANTHROPIC_MODEL`, `model`, `ANTHROPIC_DEFAULT_MODEL`, resume, alias redirection, `/fast` implied switches, subagent and teammate models, `CLAUDE_CODE_SUBAGENT_MODEL`, skill and command models, advisor, and dispatch picker models.
6. It is evaluated against the Anthropic ID, not an override value. `[1m]` is stripped from both sides. Provider prefixes such as `us.anthropic.` are not, so list the full provider ID or map through `modelOverrides`. On Agent Platform, an `@` date must be included.

### Alias substitution

7. On the Anthropic API and Claude Platform on AWS, a family alias resolves to its usual model if allowed, otherwise to the newest permitted version of the family, with a notice naming both (documented from v2.1.205). If no version is permitted, it is treated as blocked.

### Blocked selections

| Source | Behaviour |
| - | - |
| `/model` | Rejected with an error |
| `--model`, `ANTHROPIC_MODEL`, `model` | Replaced at startup with a warning; default model used |
| `ANTHROPIC_DEFAULT_MODEL` | Ignored |
| Subagent or teammate | Runs on a fallback model; interactive warning for subagents only |
| Skill or command | Override ignored; runs on session model, or subagent rule if forked |
| `advisorModel` | Advisor off for the session |
| `--advisor` | Exit at launch; background sessions start without it |
| `CLAUDE_CODE_AUTO_MODE_MODEL` | Ignored |
| Hook or background request naming a `deniedModels` model | Runs on the session model |

### Automatic model changes

8. Fallback chain entries outside the list MUST be dropped when the chain is read.
9. Plan-mode upgrades use the newest permitted version on the Anthropic API and Claude Platform on AWS. Elsewhere, or with none permitted, planning stays on the session model.
10. A content fallback to a blocked target doesn't run; the refusal stands.
11. Fast mode refuses if the resulting model is excluded.
12. Bedrock and Agent Platform availability fallback skips excluded models. Startup checks skip them only with `enforceAvailableModels`.
13. Auto mode classifier uses the session model, or an Opus in Fable sessions, when its default is excluded.

### Picker

14. Excluded models are hidden. On the Anthropic API, Claude Platform on AWS, the Claude apps gateway or an `ANTHROPIC_BASE_URL` gateway, a listed Anthropic ID with no built-in row gets its own labelled row, unless `replaceBuiltInOptions` is set. On Bedrock, Agent Platform and Foundry, only `anthropic.`-prefixed IDs get rows.

### Enforcement of Default

15. Without further keys, `availableModels` does not affect the Default option. `enforceAvailableModels: true` with a non-empty list extends it: a Default outside the list resolves to the first entry naming an allowed, available model, at startup, in `/model`, in chains' `"default"` keyword and in the drop fallback.
16. If no entry resolves, enforcement is skipped with a `--debug`-only warning.
17. Deploy both keys in the highest-ranked managed source. By default only that source is read.

### Denials

18. `deniedModels` blocks listed models even when permitted, and works with no allowlist (2.1.283). `availableModelsMatch: "exact"` makes each ID entry permit only that version. Both are managed-only, and elsewhere they are ignored with a warning.
19. A blocked Default steps down: newest permitted version of the same family; newest permitted of each lower-cost family (Sonnet, then Haiku); first permitted `availableModels` entry. If none, a session on Default refuses to start, naming the key.
20. With `enforceAvailableModels` and a non-empty list, a blocked default counts as outside the list instead.
21. Earlier versions ignore both keys, so pair them with `requiredMinimumVersion`.

### Organization restrictions

22. Enterprise admins disable models org-wide or per custom role in the admin console (2.1.187). Delivered with entitlements on authentication and enforced again by the server. Applies to members signing in or using their own API key, not to organization-scoped credentials.
23. A member with several roles gets the union. Haiku can't be disabled. Changes reach requests in about a minute and the picker next session.
24. Applies with `availableModels`: a model must pass both. Reaches Anthropic API and LLM gateway sessions only.
25. Messages: startup `Model "<name>" is restricted by your organization's settings. Using <model> instead.`; `/model` rejection `…Run /model to choose a different model.` Aliases substitute the newest allowed family version; `/model <alias>` is rejected only when all versions are restricted.

### Organization default model

26. Admins set a default for the organization or a role (2.1.196). Role beats org. With several role defaults, the most capable wins. Read once at startup.
27. Precedence: below `--model`, `ANTHROPIC_MODEL`, managed `model`, `--settings` and user, project or local `model`. With override on, it beats user, project and local settings, and `/model` lasts the session with the note `Your organization's default (<model>) applies on restart`.
28. Without override, the first interactive launch after an admin change clears the `model` key from user settings once.
29. Checks: `availableModels` alone doesn't apply; with enforcement, it is remapped. Org-restricted defaults become the newest allowed in family, or a lower-cost family. Unavailable defaults are skipped.
30. Anthropic API only. Gateways use managed `model`.

### Effort caps

31. `maxEffortLevel` caps effort on every provider (2.1.267), top-level or per model in `modelSettings`. Enterprise roles can cap per model (documented from v2.1.195). The lower cap wins between the two, and the least restrictive when several roles grant a model.
32. Levels above the cap aren't offered, and higher requests run at the cap. Plain-text `--print` warns on stderr; other surfaces log to debug.

### Provider allowlist

33. `allowedProviders` (2.1.285, managed): values include `anthropic`, `bedrock`, `vertex`, `foundry`, `anthropicAws`. Machine sources keep applying when server-managed settings also set one; a session uses only providers on both, so server lists can narrow but not widen.

### Surfaces

34. Server-managed settings reach CLI, IDE, desktop, cloud and SDK sessions, not third-party providers or API-key fleets, and Claude Tag and Cowork are special cases. MDM and file settings reach local surfaces and self-hosted runners. Pickers on claude.ai hide excluded models as a convenience. Enforcement is by server or client.
35. Hosts with `CLAUDE_CODE_PROVIDER_MANAGED_BY_HOST` override managed model keys, but a managed allowlist stays in force unless the host supplies its own.

## Configuration & interfaces

| Key | Scope |
| - | - |
| `availableModels` | Any, managed wins |
| `enforceAvailableModels`, `deniedModels`, `availableModelsMatch`, `allowedProviders` | Managed |
| `maxEffortLevel` | Settings, top-level or per model |
| `requiredMinimumVersion` | Managed |

## Failure modes & edge cases

- A `modelOverrides` map from a lower-ranked source is ignored under the opt-in merge. With a managed allowlist, only managed overrides apply to directly passed IDs, and an excluded ID is never resolved through any override.
- `Can't switch to the default model`: picking Default when blocked.
- `Managed settings block the default model`: startup exit.

## Changes since the snapshot

- 2.1.187: organization restrictions.
- 2.1.196: organization default.
- 2.1.267: `maxEffortLevel`.
- 2.1.283: `availableModelsMatch`.
- 2.1.285: `allowedProviders`.
- 2.1.314: flagged requests retry on another model when pins or lists leave only an older Opus or none.

## Open questions

- Exact wording of the "most capable" ordering for role defaults.
- How 2.1.314's change interacts with the rule that a blocked fallback target ends in a refusal, stated in 2.1.314's docs without this nuance.
