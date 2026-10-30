# System prompt and context assembly

**Status:** shipped
**Provenance:** both
**Sources:** docs cli-reference (system prompt flags), agent-sdk/modifying-system-prompts, how-claude-code-works, prompt-caching, context-window, env-vars; snapshot `constants/prompts.ts`, `constants/systemPromptSections.ts`, `utils/systemPrompt.ts`, `context.ts`; changelog 2.1.98, 2.1.154, 2.1.201, 2.1.212, 2.1.257, 2.1.265, 2.1.267, 2.1.268, 2.1.275, 2.1.283, 2.1.302, 2.1.312

## Purpose

Defines what the model receives apart from the conversation and in what order. This is a functional description; the prompt text itself is out of scope.

## Behaviour

### Layers

1. Each request is ordered so rarely changing content comes first: system prompt with tool definitions, then project context, then conversation. See [prompt-caching.md](prompt-caching.md).
2. The default system prompt covers identity, operating rules, task and tool guidance, tone, environment facts, memory location and session-specific guidance. It is assembled from named sections, each computed once and cached, with explicit opt-outs for sections that must recompute.
3. A static/dynamic boundary marker (`__SYSTEM_PROMPT_DYNAMIC_BOUNDARY__`) separates content cacheable across users from per-session content.
4. Git status, memory location, working directory and environment details are per-session. Since 2.1.268 third-party providers also deliver environment, model and settings details as attachments, matching first-party sessions.
5. Two prompt variants exist: full and shorter ("lean", with abbreviated tool descriptions). Lean became the default for all but Haiku, Sonnet, and Opus 4.7 and earlier in 2.1.154. As of the env-var reference: when unset, Haiku 4.5, Sonnet 5, Opus 4.7 and earlier in those families use full, and newer models use lean. Unrecognized model names on third-party providers use lean (2.1.312). `CLAUDE_CODE_SIMPLE_SYSTEM_PROMPT=1` forces lean, `0`/`false`/`no`/`off` forces full. Both keep the full tool set, hooks, MCP and CLAUDE.md.
6. Bare mode uses a minimal prompt.

### Precedence

7. Effective prompt selection, highest first: an override (loop-style callers, replaces everything); coordinator prompt if active; main-thread agent prompt; `--system-prompt[-file]`; default.
8. An agent prompt replaces the default, except in gated proactive modes where it appends.
9. Append text is added at the end in every case except the override.
10. Text and file forms can be combined since 2.1.283. The file's text comes first, then a blank line, then the flag text, whatever the argument order.
11. Replacement removes all default guidance. The commit and PR instructions live in the Bash tool description, so they survive a custom prompt unless `includeGitInstructions` is false.

### Prompt recording

12. By default the prompt is built once, on the conversation's first request, including flag text, and recorded in the session. Every later request and resume uses the record until compaction. Different flag text on a resume takes effect after compaction or in a new conversation.
13. `--system-prompt-snapshot off` rebuilds per request. Default is `on` except in bare mode outside cloud and background sessions.
14. Compaction of a resumed conversation switches to the current prompt, costing one layer rebuild.
15. The Agent SDK can update instructions mid-session with an in-place mechanism; see the SDK spec area.

### Project context

16. CLAUDE.md files (or AGENTS.md in place of one), unscoped rules and auto memory load at session start and are prepended as a user-context message, along with the current date in the snapshot. See the memory-context spec area for discovery.
17. Project-root and user CLAUDE.md are read once and held. Edits apply on `/clear`, `/compact` or restart. Nested CLAUDE.md and path-scoped rules load on demand into message history.
18. The first 200 lines or 25KB of `MEMORY.md`, whichever comes first, load at start.
19. A git status snapshot (branch, recent commits, status) is taken at startup, once. Snapshot limit: 2,000 characters.
20. Skills appear as descriptions, with bodies loaded on use. MCP tool names and server instructions appear; definitions may be deferred.

### Reminders

21. The harness adds context as system reminders alongside messages: file-changed notes, CLAUDE.md, output style instructions, attribution lines, background notifications, deferred tool names, task nudges.
22. Plan mode, skills and output-style changes are delivered as messages so the prefix stays intact. An output-style change applies from the next message (documented from v2.1.251).
23. Reminders can use a mid-conversation system role. That block is marked for caching on every provider (2.1.212). Sonnet 5 does not use the role (2.1.201). Rejecting upstreams get the fallback in [api-client.md](api-client.md).
24. `--bare` sends no reminders (2.1.286).

### Per-machine sections

25. `--exclude-dynamic-system-prompt-sections` moves cwd, environment, memory paths and git status into the first user message, for cross-user cache reuse. It applies only to the default prompt.
26. For a custom prompt, a line holding only `__SYSTEM_PROMPT_DYNAMIC_BOUNDARY__` splits it at the first occurrence and is removed; the part above stays cached (2.1.275).

### Compaction interaction

27. After compaction the system prompt and output style still apply; CLAUDE.md, unscoped rules and auto memory re-inject from disk; skill descriptions rebuild (documented from v2.1.304); a fresh git snapshot is read if the session had one; plans re-inject; up to five recent files are re-read; invoked skill bodies return capped at 5,000 tokens each and 25,000 in total.

### Turning context off

| Context | Control |
| - | - |
| Commit and PR instructions, git snapshot | `includeGitInstructions: false`, `CLAUDE_CODE_DISABLE_GIT_INSTRUCTIONS=1` |
| Co-Authored-By trailer, PR footer | `attribution.commit`, `attribution.pr` |
| All CLAUDE.md, including auto memory | `CLAUDE_CODE_DISABLE_CLAUDE_MDS=1` |
| Task nudges, file-changed notes, skill list, `@` expansion | `CLAUDE_CODE_DISABLE_ATTACHMENTS=1` |
| `@` expansion only | `CLAUDE_CODE_DISABLE_FILE_MENTIONS=1` |
| Attribution block | `CLAUDE_CODE_ATTRIBUTION_HEADER=0` |

## Configuration & interfaces

| Flag | Effect |
| - | - |
| `--system-prompt`, `--system-prompt-file` | Replace |
| `--append-system-prompt`, `--append-system-prompt-file` | Append |
| `--append-subagent-system-prompt[-file]` | Subagent append (file form 2.1.261); combining both forms exits 1 |
| `--system-prompt-snapshot on\|off` | Recording (2.1.267) |
| `--exclude-dynamic-system-prompt-sections` | Cross-user caching (2.1.98) |

## Failure modes & edge cases

- A prompt or customization asking the model to write out reasoning verbatim can trigger a `reasoning_extraction` refusal.
- Large system prompts from self-hosted runners pass as private files, not command-line text (2.1.281).
- Local transcripts record each request's system prompt, tools and parameters (2.1.300). Feedback surveys can upload them with consent (2.1.224).

## Changes since the snapshot

- 2.1.98: `--exclude-dynamic-system-prompt-sections`.
- 2.1.154: lean prompt default on newer models.
- 2.1.212: mid-conversation system block works behind gateways.
- 2.1.267: `--system-prompt-snapshot`; subagents and flagged sessions record prompt and tools.
- 2.1.268: third-party sessions deliver details as attachments.
- 2.1.275: boundary marker honoured in `--system-prompt`.
- 2.1.283: text and file forms combine.
- 2.1.302: Chrome instructions moved for shared caching.
- 2.1.312: lean prompt for unrecognized third-party names.

## Open questions

- Current section list and order. Snapshot section names are not assumed current.
- Whether the date still lives in user context.
- Exact trigger set for the mid-conversation system role on non-Sonnet-5 models.
