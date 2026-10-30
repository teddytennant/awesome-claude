# Compaction

**Status:** shipped (microcompact variants and session-memory compaction: undocumented, see below)
**Provenance:** both (idle compaction, `/autocompact`, partial summarise post-leak)
**Sources:** docs `context-window`, `model-config`, `prompt-caching`, `settings-reference`, `hooks`, `checkpointing`, `commands`, `errors`; snapshot `services/compact/`, `commands/compact/`; changelog versions cited below

## Purpose

Keep a long conversation inside the model's context window by replacing older history with a summary, then restoring the context Claude needs to continue. A full window MUST NOT end a session.

## Behaviour

### Core flow

1. Compaction MUST send a separate summarisation request repeating the conversation's system prompt, tools and the history being summarised, ending with a summarisation instruction, so a warm prompt cache is reused.
2. That request MUST run under the conversation's own system prompt, including `--agent` sessions, and inherit the session's extended-thinking configuration. Thinking affects only how the summary is produced.
3. The summary is structured to preserve the user's requests, work state and next step. The prompt text is not reproduced. Text containing `$` sequences MUST NOT be mangled.
4. On success, the history MUST be replaced with a boundary marker, the summary, retained messages if any, and restored context. The original messages stay in the transcript file.
5. If the reply contains no summary, the client SHOULD ask again once before replacing the conversation.
6. If the summarisation request is refused, the client MUST retry on a fallback model. `--fallback-model` MUST apply to compaction.
7. The spinner MUST start its timer when compaction begins and count summary tokens as they stream, with retry countdown and stall hints.

### What survives

8. Post-compaction state MUST be as follows:

| Mechanism | After compaction |
|---|---|
| System prompt, output style | Still apply |
| Project-root CLAUDE.md, unscoped rules | Re-injected from disk |
| Auto memory | Re-injected from disk |
| Skill descriptions | Rebuilt from current skills and re-sent |
| Git status snapshot | Re-read fresh, if the session had one |
| Plan-mode plan | Re-injected from disk |
| Path-scoped rules, nested CLAUDE.md | Reload on demand |
| Files read or edited | Up to five re-read, most recently modified first; a file over 5,000 tokens returns as a path reference shown as `Referenced file` |
| Invoked skill bodies | Re-injected, 5,000 tokens per skill, 25,000 total, oldest dropped first, truncation keeps the start |
| Background commands and subagents | Keep running; Claude is reminded which are running so it does not start duplicates |
| Hook-added context | Summarised with the rest |
| SessionStart hooks matching `compact` | Run, output added |

9. A mid-turn compaction MUST NOT lose fork-session lineage, active goals, scheduled tasks or unread subagent reports.

### Automatic compaction

10. Auto-compact MUST run when context reaches the threshold, unless disabled.
11. The window's source order is: `CLAUDE_CODE_AUTO_COMPACT_WINDOW` (unless ignored as invalid), then `--autocompact`, then a per-model `modelSettings` entry, then `autoCompactWindow`, then the tuned default. Every result is capped at the model's context window. Unlike `/autocompact`, the flag is not preempted by a higher settings scope.
12. Default thresholds: at the model's limit generally; approaching the limit in cloud sessions; at the 200K boundary for Sonnet 4.6 and Opus 4.6 without extended context, and for native-1M models under `CLAUDE_CODE_DISABLE_1M_CONTEXT=1`; at about 967K for models running a native 1M window.
13. Snapshot formula, consistent with 967K: effective window is the context window minus the smaller of max output and 20,000; threshold is that minus 13,000. `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE` can lower the trigger but never raise it.
14. An unrecognised model ID compacts at the assumed window (200K by default). `CLAUDE_CODE_MAX_CONTEXT_TOKENS` and `CLAUDE_CODE_DISABLE_UNKNOWN_MODEL_WINDOW_ENFORCEMENT` adjust this.
15. Repeated compaction that frees too little MUST stop with an "Autocompact is thrashing" error, not loop. The snapshot's circuit breaker stops after 3 consecutive failures.

### `/autocompact` and window values

16. `/autocompact <value>` MUST save to user settings under the current model in `modelSettings` and apply to the session. `/autocompact auto` returns to the tuned window. With no argument it opens a dialog showing the current window.
17. Command and flag accept 100K to 1M as a plain count, a `k`/`M` suffix, or a bare 100–1000 meaning thousands.
18. For `CLAUDE_CODE_AUTO_COMPACT_WINDOW`, a bare number means tokens, so `200` means 200 tokens. Below 100,000 it is treated as the 100K minimum with a warning; above 1M, as the 1M maximum with a warning; a non-size is ignored with a warning. While set, `/autocompact` reports the override and does not save.
19. A subagent's `autoCompactWindow` can lower the applicable window but never raise it.

### Manual compaction

20. `/compact [instructions]` MUST summarise the conversation, optionally focused by the instructions. It keeps working while auto-compact is off.
21. If typed while viewing a background agent's or teammate's transcript, a dialog MUST name the target and ask first.

### Partial compaction

22. The rewind menu offers **Summarize from here** and **Summarize up to here**, with optional guidance text (see [checkpoints-rewind.md](checkpoints-rewind.md)). Neither changes files. Both show a **Summarized conversation** marker. These options MUST be hidden when `DISABLE_COMPACT` is set.

### Reactive recovery

23. When the API rejects a request as too long, the client MUST compact and retry.
24. The first attempt SHOULD seed from the overflow size in the original rejection, avoiding a near-full retry.
25. If the compacted request is still too long, the client MUST compact again, keeping less recent conversation.
26. The summarisation request itself may overflow. The snapshot truncates the oldest history and retries up to 3 times; dense text such as base64 MUST be measured correctly so the retry helps.
27. A session dominated by one very large first prompt MUST summarise that prompt on its own, not leave it out.
28. If compaction had to leave the oldest messages out of its summary, Claude MUST be told.
29. Failure messages MUST explain why recovery failed, and say when auto-compact is off. Conversations over the API's 32 MB request limit with nothing strippable MUST fail once, clearly.
30. A blocking `PreCompact` hook on a reactive pass means the error stands; a proactive pass is skipped and the conversation continues.

### Idle compaction

31. Idle compaction is on by default when all hold: interactive terminal, VS Code chat panel, or desktop Code tab running locally or over SSH; `autoCompactEnabled` on; one-hour TTL in use; feature flags fetchable; context at least `CLAUDE_CODE_IDLE_COMPACT_MIN_TOKENS` (default 200,000, minimum 100,000); about an hour since the last request, with the machine awake.
32. Its purpose is to summarise shortly before the one-hour cache expires, so the next message does not reprocess everything. In the terminal it runs at about 54 minutes of idle time.
33. The conversation MUST show a notice: in the terminal a line beginning `Compacted while idle, before the prompt cache expired`; in VS Code and desktop, a notice including `a summary written while you were away`, with how to turn it off.
34. In VS Code and desktop, the summary is used on the next message only if the cache has expired.
35. `idleCompaction: false`, the `/config` **Idle compaction** row, or turning auto-compact off disables it. The row is hidden where another source sets the key or flags are unavailable.

### Disabling

36. `autoCompactEnabled: false` or `DISABLE_AUTO_COMPACT` stops automatic and idle compaction; whichever disables it, the other cannot re-enable it.
37. `DISABLE_COMPACT` removes all compaction, including `/compact`, and hides its hints. From settings files and mods it can only turn compaction off.

### Microcompact (snapshot, undocumented)

38. The snapshot clears old tool results without summarising, using three paths: a cached variant restricted to internal builds; a time-based variant, default off, that clears results when the gap since the last assistant message exceeds 60 minutes, keeping the 5 most recent; and an API-side context-management variant. Targets are read, shell, search, web and edit tool results.
39. Public docs and changelog contain no mention of microcompact. Status at 2.1.314 is unknown.

### Session-memory compaction (snapshot, gated)

40. A variant substitutes the session-memory file for a generated summary and keeps recent messages (10,000 to 40,000 tokens, at least 5 text messages). It is gated and undocumented. Context collapse (`CONTEXT_COLLAPSE`) is another gated, unreleased mechanism.

### Hooks

41. `PreCompact` and `PostCompact` fire with matcher `manual` or `auto`; idle compaction is `auto`. `PreCompact` can block by exit 2 or `decision: "block"`, and each hook's output is cut at 10,000 characters. `systemMessage` and `continue` from `PreCompact` are discarded. `PostCompact` has no decision control.

## Configuration & interfaces

| Interface | Effect |
|---|---|
| `/compact [instructions]`, `/autocompact [auto\|<tokens>]` | Manual compaction; window |
| `--autocompact <auto\|tokens>` | Window for one launch |
| `autoCompactEnabled`, `autoCompactWindow`, `idleCompaction`, `modelSettings` | Settings |
| agent frontmatter `autoCompactWindow` | Per-subagent window |
| `DISABLE_AUTO_COMPACT`, `DISABLE_COMPACT` | Disable automatic, or all |
| `CLAUDE_CODE_AUTO_COMPACT_WINDOW`, `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE`, `CLAUDE_CODE_IDLE_COMPACT_MIN_TOKENS` | Tuning |
| `CLAUDE_CODE_MAX_CONTEXT_TOKENS`, `CLAUDE_CODE_DISABLE_UNKNOWN_MODEL_WINDOW_ENFORCEMENT`, `CLAUDE_CODE_DISABLE_1M_CONTEXT` | Window assumptions |
| `CLAUDE_CODE_TRANSCRIPT_LOCAL_GC` | Trim `-p`/SDK transcripts after compaction |
| `x-claude-code-compaction`, `x-claude-code-context-compacted` | Gateway hint headers, opt-in |

## Failure modes & edge cases

- Stopping a turn during compaction MUST NOT leave a "Prompt is too long" state.
- A Mac sleeping during compaction MUST NOT cause it to give up.
- A last reply reporting zero token usage MUST NOT defeat auto-compact.
- Gateways naming a different model than requested MUST NOT cause repeated compaction.
- Resume after compaction MUST keep the summary, kept messages and restored context, and a compaction row in a resumed session says where earlier messages are saved.
- A malformed compaction marker in a transcript MUST NOT crash compaction or resume.
- `CLAUDE_CODE_AUTO_COMPACT_WINDOW` while set makes the status line's `used_percentage` a poor indicator of when compaction runs, as that field measures the full window.

## Changes since the snapshot

- v2.1.105: PreCompact can block.
- v2.1.142: reactive compaction seeds from overflow size.
- v2.1.141: "Summarize up to here".
- v2.1.178: `--fallback-model` honoured.
- v2.1.198: inherits thinking configuration.
- v2.1.221: `/autocompact` and `--autocompact` (per docs).
- v2.1.223: auto-compact keeps unrecognised IDs within the assumed window.
- v2.1.229, v2.1.235: clearer overflow errors.
- v2.1.247: Sonnet 5 1M window compacts near 967K; `--agent` system prompt respected.
- v2.1.260: 1M auto-compact timing and recovery improved.
- v2.1.281: oversized first prompt summarised alone.
- v2.1.282: fallback on refused summary.
- v2.1.283: spinner counts tokens.
- v2.1.284: second compaction when still too long.
- v2.1.288: `/autocompact` per model.
- v2.1.296: subagent `autoCompactWindow`.
- v2.1.299: idle compaction in terminal, with `CLAUDE_CODE_IDLE_COMPACT_MIN_TOKENS`.
- v2.1.302: `/config` row.
- v2.1.304: skill list re-sent; tool names in Ctrl+O summary; `k`/`M` suffixes for the variable.
- v2.1.311: retry on missing summary; `DISABLE_COMPACT` cannot be re-enabled from settings.
- v2.1.312: subagent window can lower the variable's value.
- v2.1.314: idle compaction in VS Code and desktop, and with telemetry off, on third-party providers and gateways once the one-hour cache is on; `PreCompact` output cap.

## Open questions

- Whether the post-compaction file budget (50,000 tokens in the snapshot) still applies alongside the documented five-file rule.
- Whether microcompact, session-memory compaction or context collapse are live.
- The current numeric thresholds for the thrashing error and overflow retries.
- The exact order between `--autocompact`, `modelSettings` and scoped settings when a managed scope sets a window: docs say the flag is not preempted, and the command saves but does not take effect.
