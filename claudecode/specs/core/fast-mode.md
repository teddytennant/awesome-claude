# Fast mode

**Status:** shipped (Opus 5.5); preview (Opus 5, Opus 4.8)
**Provenance:** both
**Sources:** docs fast-mode, prompt-caching, model-config; snapshot `utils/fastMode.ts`, `services/api/withRetry.ts`, `commands/fast`; changelog 2.1.142, 2.1.154, 2.1.219, 2.1.221, 2.1.271, 2.1.280, 2.1.281, 2.1.299, 2.1.304

## Purpose

A speed setting for Opus: same model and quality, up to 2.5 times faster, at a higher per-token price. It is a request configuration, not a separate model.

## Behaviour

### Eligibility

1. Fast mode MUST be limited to Opus 5.5, Opus 5 and Opus 4.8. Enabling it on another model switches the session to the default fast Opus (Opus 5.5 from 2.1.280). If an allowlist excludes that model but the session is on a supported Opus, it enables in place.
2. Providers: Anthropic Console API and subscriptions only. It MUST NOT be offered on Bedrock, Agent Platform, Foundry or Claude Platform on AWS.
3. Subscription use draws only from usage credits, even with plan usage remaining. Without credits, `/fast` reports `Fast mode requires usage credits`.
4. Team and Enterprise need Owner enablement. Console organizations need provisioned access for Opus 5 and 4.8. Without it, requests hit the fast limit and fall back.
5. A free Console Evaluation plan reports that credits must be purchased.

### Availability check

6. Before offering fast mode, the client checks organization availability directly against `api.anthropic.com`. The check ignores `ANTHROPIC_BASE_URL`, uses any configured HTTP proxy, and caches a success.
7. The check is skipped under `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC`, and when a gateway-issued key is not in Anthropic key format.
8. `ANTHROPIC_AUTH_TOKEN` alone, with no login, key or cached success, is treated as disabled by the organization without sending the check. A proxy answering the check with a 200 block page reads the same way.
9. `CLAUDE_CODE_SKIP_FAST_MODE_NETWORK_ERRORS=1` treats a failed check as available and honours a disabled response. `CLAUDE_CODE_SKIP_FAST_MODE_ORG_CHECK=1` skips it entirely.
10. Skipping changes only the client check. The API still rejects requests from a disabled organization, and the client then retries at standard speed and turns fast mode off.

### Toggle

11. `/fast` opens a dialog with Space to toggle and Enter to confirm; `/fast on|off` sets directly. Turning it on confirms with `Fast mode ON` and shows `↯` next to the prompt.
12. By default the choice persists through the `fastMode` user setting.
13. Per-session opt-in: `fastModePerSessionOptIn: true` starts each session with fast mode off and leaves the saved preference intact. When that key comes from managed settings, `/fast on` works only in an interactive terminal session and is refused elsewhere, with the organization-disabled message.
14. `-p`: `/fast` works only in a session launched with fast mode in `--settings`; the change lasts for that session.
15. Cloud sessions: `/fast on` applies to that session only, and the web composer has a switch (2.1.271, 2.1.281).
16. Agent view: `/fast` sets what new sessions start with (2.1.299).
17. Turning fast mode off leaves the session on Opus.
18. Mid-turn: the toggle applies at once, the running turn finishes at its original speed, and the change takes effect next turn. A model change implied by enabling applies from the next request in that turn.

### Model switches

19. Switching to an unsupported model MUST turn fast mode off, including Opus 4.7 (documented from v2.1.221).
20. Switching back to a supported Opus MUST turn it on again only when the saved preference is on and per-session opt-in is not configured.
21. Any such change MUST show the ON or OFF confirmation, whether the switch came from `/model`, `/config model=…` or Remote Control. Status is resent to Remote Control devices after a switch, reconnect or failed check.

### Client behaviour on rejection

22. Snapshot behaviour: on a 429 or 529 for a fast request, the client either waits and retries at fast speed for a short `retry-after`, preserving the cache, or enters cooldown at standard speed, with a minimum cooldown floor to prevent flip-flopping. Docs confirm the cooldown and automatic return.
23. During cooldown the icon turns gray, requests run at standard speed and price, and fast mode re-enables when cooldown ends. `/fast` can disable it during cooldown. Speed changes made automatically count as toggles for caching.
24. Out of usage credits, each rejected request retries at standard speed with no cooldown. Interactive: `Fast mode disabled · usage credits exhausted`, off for the session, and the saved preference unchanged. stream-json and SDK: the same text as a `system` message with subtype `notification`, once per turn, with fast mode staying on (2.1.221).
25. An organization-disabled rejection turns fast mode off and retries at standard speed.
26. The 529 backoff variables don't apply to fast-mode requests. The retry watchdog points to these rate-limit rules for fast requests.

### Pricing

| Model | Input per MTok | Output per MTok |
| - | - | - |
| Opus 5.5 | $8 | $40 |
| Opus 5 | $10 | $50 |
| Opus 4.8 | $10 | $50 |

27. Fast pricing is flat across the 1M window.
28. Fast and standard speed keep separate caches. The first enable in a conversation reads the whole context uncached at fast rates.

## Configuration & interfaces

| Key | Scope | Meaning |
| - | - | - |
| `fastMode` | User settings; `false` in managed blocks it | Saved preference |
| `fastModePerSessionOptIn` | Any settings file | Reset each session |
| `CLAUDE_CODE_DISABLE_FAST_MODE` | Env | Off entirely |
| `CLAUDE_CODE_SKIP_FAST_MODE_NETWORK_ERRORS`, `CLAUDE_CODE_SKIP_FAST_MODE_ORG_CHECK` | Env | Check handling |

Status line field: `fast_mode`.

## Failure modes & edge cases

Messages from `/fast`:

| Message | Cause |
| - | - |
| `Fast mode has been disabled by your organization.` | Org off, managed `fastMode: false`, managed per-session opt-in outside a terminal, or a misread check |
| `…is not in your organization's allowed models` | Allowlist excludes the implied Opus |
| `Fast mode requires usage credits` | Credits off |
| `Fast mode unavailable during evaluation…` | Console free plan |
| `Fast mode unavailable due to network connectivity issues` | Check failed |
| `Fast mode is currently unavailable` | Check not sent and nothing cached |

## Changes since the snapshot

- 2.1.142: default moved from Opus 4.6 to 4.7.
- 2.1.154: Opus 4.8 fast at twice the standard rate; `CLAUDE_CODE_OPUS_4_6_FAST_MODE_OVERRIDE` deprecated.
- 2.1.219: Opus 4.7 removed; Opus 5 at $10/$50.
- 2.1.221: exhausted credits reported on the stream.
- 2.1.243: `/fast` runs mid-turn on every provider.
- 2.1.271: cloud sessions.
- 2.1.280: Opus 5.5 default.
- 2.1.281: web composer switch.
- 2.1.290: Slack `!fast`.
- 2.1.304: "(research preview)" label removed on Opus 5.5.

## Open questions

- Interaction between `CLAUDE_CODE_RETRY_WATCHDOG` and fast mode beyond the note that the watchdog's immediate-failure rule covers standard-speed requests.
- Current values for the short-retry threshold and cooldown floor.
- Opus 5.5 access rules for Console organizations beyond "depends on usage tier".
