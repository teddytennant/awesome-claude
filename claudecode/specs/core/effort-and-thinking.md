# Effort and thinking controls

**Status:** shipped
**Provenance:** both
**Sources:** docs model-config, settings-reference, env-vars, commands; snapshot `utils/effort.ts`, `utils/thinking.ts`, `commands/effort`; changelog 2.1.89, 2.1.94, 2.1.111, 2.1.117, 2.1.166, 2.1.251, 2.1.257, 2.1.260, 2.1.267, 2.1.280, 2.1.287, 2.1.311, 2.1.312

## Purpose

User-facing rules for how much the model reasons. Wire format is in [request-shaping.md](request-shaping.md).

## Behaviour

### Levels

| Model | Levels | Default |
| - | - | - |
| Fable 5.1, Fable 5 | low, medium, high, xhigh, max | high |
| Opus 5.5, Sonnet 5.5, Haiku 5.5 | same | medium |
| Opus 5, Sonnet 5, Opus 4.8 | same | high |
| Opus 4.7 | same | xhigh |
| Opus 4.6, Sonnet 4.6 | low, medium, high, max | high |

1. Unsupported levels MUST step down to the highest supported at or below the setting. Models not listed have no effort.
2. Scales are per model, so the same name doesn't mean the same value across models.

### Resolution

3. First match: `CLAUDE_CODE_EFFORT_LEVEL`; a level chosen in session (`/effort`, picker, `applyFlagSettings()`); `--effort`; settings (`modelSettings` per model, or `effortLevel`); the model default, or an organization default model's configured level.
4. `maxEffortLevel` and organization caps limit every source. See [model-restrictions.md](model-restrictions.md).
5. Top-level `effortLevel` in user settings doesn't apply to Opus 5.5 and later models (2.1.280). In project, local, managed or `--settings` sources it applies to every model. Within one file, a model's entry beats the top-level key. Across files, each model resolves from the highest-precedence file that sets something applying to it.
6. Skill `effort` lasts until the end of its turn, or the forked run with `context: fork`. Subagent `effort` lasts while it runs unless the invocation overrides. Both yield to the environment variable and caps.
7. After automatic fallback, see [model-fallback.md](model-fallback.md).

### Persistence

8. `Enter` in the slider or picker, or a level typed after `/effort`, saves per model under `modelSettings` in user settings (2.1.251). `s` is session-only (2.1.257). `-p` and Remote Control are session-only.
9. `max` is session-only unless set by `CLAUDE_CODE_EFFORT_LEVEL`. `max` is not accepted in `effortLevel` or `modelSettings`.
10. `/effort auto` clears the saved level for the active model. `/effort status` prints the level: `Effort level: auto` means none sent; `auto (currently <level>)` means a level is sent because of a cap.

### Timing

11. A new level applies to the next message. Queueing a message while Claude works delivers it when tools finish and the new level applies from then on. `/model`'s level takes effect by the next message at the latest. The prompt indicator notes when a mid-task change may wait (2.1.312).
12. Header and footer display the set level, even while the old level finishes.

### Ultracode

13. Ultracode is a Claude Code setting, not an API level: it directs Claude to orchestrate dynamic workflows. On/off doesn't change effort (2.1.284). `--effort ultracode` and SDK `effortLevel: "ultracode"` turn it on and set `xhigh`.
14. Settings: `ultracode` key, `/effort ultracode [on|off]`, or Tab in the slider. `effortLevel` and `CLAUDE_CODE_EFFORT_LEVEL` reject it.
15. Unavailable if workflows are off or the model lacks `xhigh`. Then `--effort ultracode` starts with it off at the highest allowed level up to `xhigh`.

### ultrathink

16. `ultrathink` anywhere in a prompt adds an in-context instruction for that turn. No other phrases are keywords, including "think", "think hard" and "think more".
17. Typed in the interactive terminal on Opus 5.5, Sonnet 5.5, Haiku 5.5 or Fable 5.1 through Anthropic's API, it also raises the turn to `xhigh`; typed while Claude works, it raises the rest of that turn (2.1.311).
18. The rainbow highlight appears only where the word can raise effort. It's absent in quotes, brackets, paths, commands, prompts starting with `/`, or when the environment variable or a cap holds effort below `xhigh`.

### Thinking toggle

19. Controls: `Option+T`/`Alt+T` for the session; `/config` writes `alwaysThinkingEnabled`; `MAX_THINKING_TOKENS=0`.
20. Opus 5.5, Sonnet 5.5, Haiku 5.5 and Fable can't turn thinking off. The toggle and `/config` row read `Thinking can't be turned off`, and saved values have no effect until the model changes.
21. Fixed budgets are only for Opus 4.6 and Sonnet 4.6 through `CLAUDE_CODE_DISABLE_ADAPTIVE_THINKING=1`.
22. Thinking displays collapsed; `Ctrl+O` shows it. Summaries are off by default interactively (2.1.89); `showThinkingSummaries: true` restores them.
23. Spinner progress wording changes during long thinking; amber after 10 seconds (2.1.141) and `deep in thought` after 45 seconds (2.1.271).

### Environment exposure

24. Hooks get `effort.level` and `$CLAUDE_EFFORT`, Bash commands can read `$CLAUDE_EFFORT` (2.1.133), skills can use `${CLAUDE_EFFORT}` (2.1.120), status line gets `effort.level` and `thinking.enabled` (2.1.119). The transcript records effort per assistant message (2.1.212).

## Configuration & interfaces

| Item | Values |
| - | - |
| `/effort` | level, `auto`, `status`, `ultracode [on\|off]`; no argument opens slider |
| `--effort` | low to max, or `ultracode` |
| `CLAUDE_CODE_EFFORT_LEVEL` | Levels, `auto`, `unset` |
| `effortLevel` | low, medium, high, xhigh |
| `modelSettings.<model>` | `effortLevel`, `maxEffortLevel`, `autoCompactWindow` |
| Keybindings | `effortSlider:decreaseEffort`, `increaseEffort`, `toggleUltracode` |

## Failure modes & edge cases

- `/effort` confirmation states whether a level persists (2.1.162).
- `--effort ultracode` on old clients printed an unknown-value message; docs date acceptance to v2.1.203.
- In screen reader mode the selector is a numbered list (2.1.233).

## Changes since the snapshot

- 2.1.94: default high for API-key, third-party, Team and Enterprise.
- 2.1.111: `xhigh`; `/effort` slider.
- 2.1.117: Pro and Max default high on 4.6.
- 2.1.166: thinking-off controls honoured on models that think by default.
- 2.1.251: per-model saved effort.
- 2.1.257: `s` for session-only.
- 2.1.267: `maxEffortLevel`.
- 2.1.280: Opus 5.5 default medium; old saved level no longer applies to new models.
- 2.1.284: ultracode independent of effort.
- 2.1.311: `ultrathink` raises effort.

## Open questions

- Does the numeric effort value in the snapshot (`EffortValue` numbers) remain supported?
- Whether Sonnet 5.5's "default medium" applies equally on all providers.
