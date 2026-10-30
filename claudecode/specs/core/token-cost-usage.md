# Token and cost tracking, /usage

**Status:** shipped
**Provenance:** both
**Sources:** docs costs, agent-sdk/cost-tracking, statusline, settings-reference (`modelPricing`), fast-mode; snapshot `cost-tracker.ts`, `utils/modelCost.ts`, `bootstrap/state.ts`, `commands/cost`, `commands/usage`, `commands/stats`; changelog 2.1.92, 2.1.118, 2.1.149, 2.1.208, 2.1.221, 2.1.236, 2.1.239, 2.1.243, 2.1.251, 2.1.271, 2.1.296, 2.1.299, 2.1.304

## Purpose

Keep a running estimate of tokens and dollars per session and per model, show it, enforce client-side budgets, and show plan usage for subscribers. All dollar figures are client estimates, never billing data.

## Behaviour

### Accounting

1. After each API response the client MUST add usage to per-model session totals: input, output, cache read and cache write tokens, plus web search requests and computed cost.
2. Cost is computed locally from a built-in price table keyed by canonical model. Data-residency responses at 1.1× are multiplied (2.1.239). The price table is updated in releases, such as Sonnet 5.5 cache reads at $0.10 per million (2.1.296).
3. Haiku 5.5 charges a higher rate on prompts over 100K tokens.
4. Advisor tokens count toward session totals. See [advisor.md](advisor.md).
5. Subagent usage MUST add to the totals. In the SDK result, `usage` covers only the main loop, while `total_cost_usd` and `modelUsage` cover the whole tree, including spend restored on resume.
6. Unknown models use a default tier in the snapshot.
7. Totals MUST be saved for the session and restored on resume.
8. `/clear` starts a new session, and totals reset (documented from v2.1.211).
9. API and wall durations and lines changed are tracked with cost.

### Contracted rates

10. Managed `modelPricing` substitutes reported rates: `multiplier` (below 1 for discount, up to 10 for markup since 2.1.271) and per-model `overrides` with `input`, `output`, `cacheRead`, `cacheWrite`. Overrides apply first, then the multiplier also reduces them.
11. It affects `/usage`, the status line, SDK `total_cost_usd`, `--max-budget-usd` and OpenTelemetry cost figures, not billing and not `/model` picker prices.
12. Only managed sources count. Key ignored in user, project and local settings, in `--settings`, and in the Windows HKCU registry. A host application may supply a table.
13. While a table applies, `Total cost` carries the note `at your organization's configured rates`.
14. A Claude apps gateway's `pricing:` reaches signed-in clients through managed settings (2.1.268).

### Budget

15. `--max-budget-usd` (print mode) checks the estimate between messages and ends with `error_max_budget_usd`. It can overshoot, so leave headroom. Multiplied and contracted rates count.

### /usage

16. `/usage` is the single screen; `/cost` and `/stats` are aliases, with `/stats` opening the Stats tab (2.1.118). Tabs include session, plan and stats views.
17. **Session block**: `Total cost`, `Total duration (API)`, `Total duration (wall)`, `Total code changes`, `Usage by model` with per-model tokens and cost. It is intended for API users. Subscribers also see plan bars and activity stats.
18. **Prompt cache line**: see [prompt-caching.md](prompt-caching.md).
19. **Plan bars**: session and weekly windows, with model-specific bars where relevant. The Sonnet-only bar hides for Pro and Enterprise (2.1.89).
20. **Plan breakdown** (Pro, Max, Team, Enterprise; `d`/`w` toggles 24 hours or 7 days): attribution to skills, subagents, plugins and MCP servers as percentages; recommendations of at least 10% share; Loops rows for the heaviest scheduled tasks. Figures are local and approximate, from session history on this machine.
21. An MCP server's share MUST count only requests that consumed one of its tool results (documented from v2.1.222).
22. Recommendation rows report what share of usage they apply to, not savings, and can exceed 100% in sum.
23. **Fix shortcut** (`f`, documented from v2.1.305): after any running turn ends, run each `/effort` row not marked `run`, then send one prompt with steps for the other actionable rows, asking Claude to show each change first. Rows ending in `run <cmd>` are left to the user. Footer: `f to fix 2 of 3`. The hint is hidden while Remote Control is connected, and pressing `f` in that race closes with `Nothing was sent. Turn off Remote Control to use fixes.`
24. Warnings cover max effort, workflows, always-on context and large tool results (2.1.299).
25. **Usage credits row**: Pro and Max show monthly spend against any limit, or `Unlimited`. Team and Enterprise show own spend against a personal limit. A row with a limit shows from 0% (2.1.236).
26. **Spend limit bar** behind a Claude apps gateway (2.1.251), with dollar amounts (2.1.284).
27. **Rate-limited usage endpoint**: show last-known bars from the past 60 minutes with a `Showing last-known usage` note and `r` to retry (2.1.208). Otherwise report the limit and when it ends (2.1.304). A message such as `rate limited until 3:14am` refers to fetching, not to the user's work.

### Spinner count

28. The spinner's `↓ N tokens` is a live approximate count of the current turn's output, including thinking and foreground subagents. It excludes everything sent to the model. It resets at each turn start and on compaction. It is hidden until output arrives, in narrow rows and in screen reader mode.

### /context and context size

29. `/context` shows a live category breakdown with suggestions. When the token-counting API is unavailable it uses a local estimate instead of small-model requests (2.1.261).
30. In the snapshot, token counts between responses come from the last reported usage plus an estimate of newer messages. The status line reports `context_window` fields from the most recent response.

### Status line and telemetry

31. Status line JSON exposes `cost.total_cost_usd`, `total_duration_ms`, `total_api_duration_ms`, lines changed, `context_window.*`, `rate_limits.five_hour`, `seven_day`, `spend_limit` and `prompt_cache`.
32. OpenTelemetry exports per-user token and cost metrics on every setup. `effort` appears on `llm_request` spans (2.1.274).

### Other surfaces

33. `/insights` writes an HTML report under `~/.claude/usage-data/`, covering up to 200 unseen sessions per run.
34. `/usage-credits` opens billing settings or, for members without billing access, confirms and sends a request to admins. It is not available with API-key auth, and duplicate requests are suppressed.
35. Pro users see a hint when returning after the cache expired, showing roughly how many tokens go uncached next turn (2.1.92).

## Configuration & interfaces

| Item | Effect |
| - | - |
| `--max-budget-usd` | Print-mode cap |
| `modelPricing` | Managed contracted rates |
| `result.total_cost_usd`, `modelUsage`, `usage` | SDK output |
| `/usage` keys | `d`, `w`, `r`, `f` |

## Failure modes & edge cases

- After a crash the final SDK result can have zero cost fields; totals can be recovered from the transcript as the cost-tracking doc describes.
- Python SDK fields are optional, so check for `None`.
- Spinner tokens won't match `/usage` output tokens, because they measure different things.
- Figures exclude other devices and claude.ai.

## Changes since the snapshot

- 2.1.92: per-model and cache-hit breakdown for subscribers.
- 2.1.118: `/cost` and `/stats` merged into `/usage`.
- 2.1.149: limits breakdown.
- 2.1.221: Stats counts cache tokens.
- 2.1.239: 1.1× data-residency premium.
- 2.1.243: `modelPricing`; Loops breakdown.
- 2.1.251: cache line; spend limit bar.
- 2.1.271: markup multipliers.
- 2.1.299: extra warnings.

## Open questions

- Exact tab names in `/usage`.
- How totals behave across a `/clear` in the SDK.
- Whether the unknown-model default tier in the snapshot is current.
