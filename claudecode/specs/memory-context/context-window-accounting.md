# Context window accounting and /context

**Status:** shipped
**Provenance:** both
**Sources:** docs `context-window`, `model-config`, `commands`, `statusline`, `costs`, `errors`; snapshot `utils/analyzeContext.ts`, `commands/context/`, `utils/context.ts`, `services/compact/autoCompact.ts`; changelog versions cited below

## Purpose

Show the user what occupies the context window, warn before it runs out, and supply the token counts that compaction decisions rely on.

## Behaviour

### What fills the window

1. Before the first prompt, context MUST hold: the system prompt, tool definitions or names, CLAUDE.md or AGENTS.md, auto memory, MCP tool names, and skill descriptions. An output style or `--append-system-prompt` text may add to this.
2. During work, context grows with file reads, path-scoped rules loaded with matching files, hook output and tool results.
3. A subagent MUST use its own window; only its summary and a small metadata trailer return to the parent.

### Window size

4. The window comes from the resolved model. Fable models, Sonnet 5 and later, Haiku 5.5, Opus 4.6 and later, and Sonnet 4.6 support 1M. `[1m]` selects 1M on models that need the suffix.
5. An unrecognised model ID MUST assume 200K and warn at startup with the assumption stated. Corrections are, in order of preference, updating, `modelOverrides` or a `modelPicker` `behavesAs` row, a `[1m]` suffix, or `CLAUDE_CODE_MAX_CONTEXT_TOKENS`.
6. `CLAUDE_CODE_MAX_CONTEXT_TOKENS` applies directly only to unresolvable provider or custom spellings without `[1m]`. For an ID that resolves to a known model, or a bare `claude-` name, it takes effect only with `DISABLE_COMPACT`.
7. `CLAUDE_CODE_DISABLE_1M_CONTEXT` removes `[1m]` variants and holds native-1M models to 200K.
8. Behind a custom `ANTHROPIC_BASE_URL`, models with a 1M window use it (since v2.1.285); `/autocompact 200k` corrects gateways that stop at 200K.
9. The first request in a fresh environment or after a model switch MAY wait up to 1.5 seconds for server-provided limits rather than use built-in values.

### Token counting

10. Accounting MUST use the API's reported usage from the latest response as its base, and add an estimate for messages added since.
11. Turns using the advisor tool MUST NOT double-count context (fixed v2.1.273).
12. `/context` MUST count messages added since the last response, so its total can read higher than the status line.
13. When the token-counting API is unavailable, `/context` MUST use a local estimate, not extra small-model requests.
14. Behind a Claude apps gateway on Bedrock, the gateway obtains counts from AWS's CountTokens API.

### `/context`

15. `/context [all]` MUST render a coloured grid of usage by category, plus optimisation suggestions for context-heavy tools, memory bloat and capacity.
16. Categories in the snapshot: System prompt, System tools, MCP tools, Custom agents, Memory files, Skills, Messages, Free space, Autocompact buffer. MCP server instructions are their own row since v2.1.283.
17. **Memory files** MUST list the CLAUDE.md, rules, AGENTS.md and auto memory files that loaded at launch, not on-demand files.
18. Skills from plugins MUST show the providing plugin, and per-skill estimates MUST account for the model's tokenizer.
19. In fullscreen mode the per-item breakdown collapses to keep the grid visible; `all` expands it.
20. When the conversation exceeds the window, the output MUST include a warning stating how far over it is and which command frees space.
21. The grid MUST NOT enter the conversation; local command output is display-only.
22. `/context` also works in non-interactive mode, returning a Markdown table in the snapshot, and from Remote Control clients. VS Code opens a native dialog.

### Warnings

23. A context-low warning MUST appear as a transient footer notification.
24. Snapshot thresholds: warning and error at 20,000 tokens below the auto-compact threshold; a blocking limit at the effective window minus 3,000 when auto-compact is off. Whether these constants persist is unknown.
25. With auto-compact off, a context-limit error MUST say so and point to `/config`.
26. The status line receives `used_percentage`, measured against the full window, so it does not predict compaction while a window override is set.

### Skill listing budget

27. The skill listing MUST be capped at a fraction of the window (`skillListingBudgetFraction`, default 0.01), with each description capped at `skillListingMaxDescChars` (default 1,536). Over budget, the least-used skills lose descriptions but keep names. `SLASH_COMMAND_TOOL_CHAR_BUDGET` overrides the budget, with a fallback of 8,000 characters. `/doctor` reports contributors.

### Per-tool limits that affect context

28. Bash output past `bashOutputMaxChars` (default 30,000, clamp 4,000–128,000) MUST spill to a file with a preview and path.
29. File reads default to a 25,000-token cap (`CLAUDE_CODE_FILE_READ_MAX_OUTPUT_TOKENS`); the Read tool's `allow_large` parameter can exceed it when the context has room.
30. MCP responses cap at 25,000 tokens by default (`MAX_MCP_OUTPUT_TOKENS`), warning at 10,000.

## Configuration & interfaces

| Interface | Effect |
|---|---|
| `/context [all]` | Live breakdown |
| `/usage` (aliases `/cost`, `/stats`) | Cost and cache statistics |
| Status line JSON | `context_window` fields including `used_percentage`, and `current_usage` |
| `CLAUDE_CODE_MAX_CONTEXT_TOKENS`, `CLAUDE_CODE_DISABLE_1M_CONTEXT`, `CLAUDE_CODE_DISABLE_UNKNOWN_MODEL_WINDOW_ENFORCEMENT` | Window assumptions |
| `skillListingBudgetFraction`, `skillListingMaxDescChars` | Skill listing size |
| `bashOutputMaxChars`, `BASH_MAX_OUTPUT_LENGTH` | Bash output inline limit; the setting wins |

## Failure modes & edge cases

- Tool groups showing 0 tokens on Bedrock, fixed v2.1.196.
- Stale pre-compact usage after compacting from the message picker, fixed v2.1.218.
- Inflated percentages on Opus 4.7 from assuming 200K, fixed v2.1.117.
- After `/compact` or `/clear`, remote clients MUST NOT show a stale usage figure (fixed v2.1.280).
- With thousands of MCP tools, `/context` MUST stay responsive (v2.1.314).

## Changes since the snapshot

- v2.1.97: context-low warning became transient.
- v2.1.216: explicit over-limit warning; failed `/compact` displays as an error.
- v2.1.223: `CLAUDE_CODE_DISABLE_1M_CONTEXT` holds all native-1M models to 200K.
- v2.1.261: local estimate fallback.
- v2.1.280: AGENTS.md shown in `/context`.
- v2.1.281: total includes messages since the last response.
- v2.1.283: MCP server instructions row.
- v2.1.285: custom base URLs use 1M windows.
- v2.1.288: wait for server-provided limits.
- v2.1.295: gateway token counts on Bedrock.
- v2.1.314: faster `/context` with very many MCP tools.

## Open questions

- Current category names beyond those in the snapshot plus the MCP instructions row.
- Whether `/context` non-interactive output keeps the snapshot's table form.
- The default values behind the 1.5-second limit wait.
