# Advisor

**Status:** preview (experimental)
**Provenance:** both
**Sources:** docs advisor, settings-reference (`advisorModel`), env-vars, llm-gateway-protocol, errors, prompt-caching; snapshot `utils/advisor.ts`, `commands/advisor.ts`, `services/api/claude.ts`; changelog 2.1.117, 2.1.210, 2.1.232, 2.1.260, 2.1.287, 2.1.290, 2.1.293, 2.1.300

## Purpose

Lets the model consult a second, usually stronger, model at decision points. It runs server-side as an API server tool. The client only attaches it, validates pairings and renders results.

## Behaviour

### Enablement

1. Sources: `/advisor`, `advisorModel`, `--advisor`. `--advisor` beats the setting for that session and is hidden from help. Default is off.
2. Requires: Anthropic API (see Open questions for Claude Platform on AWS), a supported main model (Fable, Opus 4.6+, Sonnet 4.6+, Haiku 4.5, Haiku 5.5), and fetched feature flags. Variables that turn fetching off (for example `DISABLE_TELEMETRY`) keep it off.
3. After start, a notification reads `Advisor Tool (experimental) is on and may use more tokens · /advisor`.
4. `CLAUDE_CODE_DISABLE_ADVISOR_TOOL=1` removes `/advisor`, ignores `advisorModel` and accepts but ignores `--advisor`.
5. Through a gateway, availability depends on forwarding. A rejected tool type causes one retry without the entry and beta, and `/advisor` becomes unavailable for that base URL until exit.

### Choosing

6. `/advisor` opens a picker with models and **No advisor**. `/advisor <model>` confirms `Advisor set to …` and saves to user settings, unless picked from Remote Control or a remote-attached session, which is session-only. `/advisor off` turns it off.
7. Without a terminal (`-p`, SDK, desktop, Remote Control, 2.1.260): no argument prints current model and accepted aliases.
8. Accepted names: `fable`, `opus`, `sonnet`, or a full ID such as `claude-haiku-5-5`.

### Pairing

9. Models are ranked for this role, and an advisor MUST rank at or above the main model.

| Main | Accepted advisors |
| - | - |
| Haiku 4.5, Sonnet 4.6 | Fable, Opus, Sonnet, Haiku 5.5 |
| Opus 4.6 | Fable, Opus, Sonnet 5+, Haiku 5.5 |
| Sonnet 5, Haiku 5.5 | Fable, Opus 4.7+, Sonnet 5+, Haiku 5.5 |
| Opus 4.7, Opus 4.8 | Fable, Opus 4.7+, Sonnet 5.5 |
| Sonnet 5.5 | Fable, Opus 5+, Sonnet 5.5 |
| Opus 5, Opus 5.5 | Fable, Opus 5+ |
| Fable 5 | Fable 5.1, Fable 5 |
| Fable 5.1 | Fable 5.1 |

10. Haiku 4.5 can call the advisor but can't be one. Unknown main or advisor models aren't attached.
11. Validation is done twice. Client: below-rank advisors aren't attached to main requests, and `/advisor` output plus a notification say so. API: on refusal of an attached pairing, the client resends without it, silently, and it stays off until `/clear` or `/compact`, even after a model switch. A different pick then takes effect after `/clear` or `/compact` and in new sessions.
12. Advisors unsupported by the current main model are still saved, and activate after a compatible switch.
13. Subagents inherit the advisor and apply the same check against their own model.

### `--advisor` failures

14. At launch, exit with an error when the main model doesn't support the advisor, the model can't advise, the allowlist excludes it, or Fable needs consent. A background session starts without it instead.
15. A valid advisor ranked below the main model starts the session regardless; the main model runs without it. Non-interactive runs warn on stderr.

### Allowlist

16. A saved advisor excluded by `availableModels` MUST NOT be invoked, which disables the advisor for that session. `--advisor` with an excluded model exits at launch.

### Fable consent

17. Fable as advisor needs the one-time usage-credits consent where required. Before consent: `/advisor fable` or picking it saves nothing and points to `/model fable`; `--advisor fable` exits, or starts without in the background; a saved value sends requests without it, with an interactive notification. Accepting is done through `/model fable`, which also saves Fable as the selected model.

### Runtime

18. The model decides when to consult. No setting caps or forces calls. Users can ask in prompts or in instructions.
19. The advisor receives the full conversation including every tool call and result.
20. Advisor tool instructions are delivered to the main model. The prompt text is out of scope here.
21. The advisor entry goes after the cache breakpoint, so toggling keeps the main prefix cached. Returned guidance is cached with the transcript. The advisor's own read is never cached.
22. It has no name for permission rules or hook matchers. Mods' `turn.step` results list these calls as `serverToolUses` (2.1.290).

### Display

23. While running: `Advising` line with model name. On return: reviewed (`Ctrl+O` reads guidance when readable), `Advisor declined to advise on this request`, or `Advisor unavailable (<error_code>)`.
24. The model generally follows guidance but surfaces a conflict when evidence contradicts it.

### Cost

25. Advisor tokens bill at the advisor's rates on API plans, and count toward plan limits on subscriptions, except Fable advisors billed to usage credits. They appear in session totals and in `/usage`.

## Configuration & interfaces

| Key | Notes |
| - | - |
| `advisorModel` | Any settings file; string alias or ID |
| `--advisor <model>` | Session override |
| `/advisor [model\|off]` | Command |
| `CLAUDE_CODE_DISABLE_ADVISOR_TOOL` | Disable |

## Failure modes & edge cases

- `Advisor is less capable than the current main model`: keep it for subagents, or change either model. Notification: `Advisor will not activate on the main model…`.
- Pairing rules changed at 2.1.287: Sonnet 5.5 became accepted for Opus 4.7 and 4.8, and an Opus 4.8 advisor for a Sonnet 5.5 main is now refused.
- Stuck "tool result content could not be processed" errors were fixed in 2.1.117.

## Changes since the snapshot

- 2.1.117: experimental label, startup notification.
- 2.1.210: Fable temporarily unavailable in the picker.
- 2.1.232: Fable returns, gated on consent.
- 2.1.260: `/advisor` works without a terminal.
- 2.1.287: pairing ranks changed.
- 2.1.290: `serverToolUses` for mods.
- 2.1.293: Haiku 5.5 as main or advisor.
- 2.1.300: `/advisor` on Claude Platform on AWS.

## Open questions

- Docs state the advisor isn't available on Claude Platform on AWS, while changelog 2.1.300 adds `/advisor` there with no default advisor. The docs may lag.
- Whether the snapshot's experiment-configured advisor pairing is still used.
