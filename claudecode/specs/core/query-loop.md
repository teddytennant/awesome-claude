# Agentic query loop and turn lifecycle

**Status:** shipped
**Provenance:** both
**Sources:** docs how-claude-code-works, agent-sdk/agent-loop, agent-sdk/typescript, interactive-mode, errors, context-window; snapshot `query.ts`, `query/`, `QueryEngine.ts`, `services/tools/`, `services/compact/`; changelog 2.1.154, 2.1.163, 2.1.236, 2.1.246, 2.1.251, 2.1.275, 2.1.307

## Purpose

The loop turns one user prompt into a sequence of model calls and tool executions until the model stops asking for tools or a limit ends it. It owns recovery paths, compaction triggers, queued input, stop hooks and terminal states.

## Terminology

- **User turn**: one submitted prompt through to the end of the loop.
- **Loop iteration** (an "agentic turn" in `--max-turns` terms): one model call and its tool batch.
- **Request**: one HTTP attempt. One iteration can include several through retries and fallbacks.

## Behaviour

### Iteration structure

1. Each iteration MUST perform, in order: compute the message view after the last compact boundary, apply context reductions, run auto-compact if needed, check the blocking limit, call the model with streaming, execute tools, gather attachments, then decide to continue or end.
2. Context reductions that the snapshot runs before auto-compact, in order: per-message aggregate tool-result budget, then microcompact. Further gated reductions are listed under Gated.
3. Immutable inputs (system prompt, user context, system context, permission callback, query source, max turns) MUST stay fixed for the call. Mutable state (messages, tool context, recovery counters, turn count) MUST be replaced as a whole at each continue site, with a recorded transition reason.
4. Environment and flag state MUST be snapshotted once at entry so a mid-turn change does not produce a mixed iteration.
5. The system prompt MUST be sent with system context appended, and user context prepended as a leading user message (see [system-prompt-and-context.md](system-prompt-and-context.md)).
6. The effective model is recomputed per iteration from the session model, the permission mode and message size, which is how `opusplan` works.
7. Whether to continue MUST be driven by whether `tool_use` blocks arrived during streaming, not by `stop_reason`, which is not reliable for this purpose.

### Interrupts and queued input

8. `Esc` MUST stop the turn. The running tool is cancelled and any queued messages are sent next.
9. Every `tool_use` emitted MUST get a matching `tool_result`. On abort or a failed stream, the loop MUST synthesize error results for any unanswered calls so history stays valid.
10. A message submitted during tool execution stays queued and MUST be delivered as soon as those tool calls finish, within the same turn. Messages still queued at turn end go out automatically in order.
11. Queued slash commands and `!` shell commands are held until the turn ends, then run one at a time in order.
12. The send-now key (`chat:sendNow`, `Ctrl+Enter` or `Ctrl+X Ctrl+S`, since 2.1.275) delivers queued messages at once. Work that can move to the background does so and the turn continues; otherwise the turn is interrupted. A queued `!` command ahead of the messages always interrupts.
13. `/model`, `/fast` and `/effort` run mid-turn without queueing on all providers (2.1.243).

### Model streaming and recoverable outcomes

14. Partial assistant blocks MUST be yielded as they complete, so tools can start during streaming (see [tool-system.md](tool-system.md)). Streaming tool execution is always on since 2.1.154.
15. Some errors MUST be withheld from the stream until recovery has been tried: prompt-too-long, oversized media and max-output-tokens. If recovery succeeds the user never sees them.
16. **Prompt too long**: try reactive compaction once per loop, then continue. If that fails, surface the error, run `StopFailure` hooks, skip `Stop` hooks and end.
17. **Max output tokens**: first escalate the output cap for one clean retry (snapshot: to 64k), then inject a continuation nudge. The snapshot limits nudges to 3 per turn, after which the error surfaces.
18. **Streaming fallback**: when the client abandons a stream for a non-streaming request, assistant messages already yielded for that attempt MUST be retracted with tombstones and pending tool results discarded, because their thinking signatures and tool ids are now orphaned.
19. **Model fallback mid-turn**: on a fallback signal, switch the model for the turn and retry the iteration, stripping any model-bound thinking signatures so the new model accepts the history. A warning-level system message names the switch. See [model-fallback.md](model-fallback.md).
20. **Cut-off responses in non-interactive sessions**: if a main-conversation response with text and no tool calls is cut off mid-stream, the loop MUST prompt the model to continue, up to three times in a row, before surfacing the notice (2.1.246). Subagents do the same whether or not the session is interactive (2.1.257).
21. **Tool-call parse failure**: when a response claims a tool call but contains none, retry up to two times asking for the call (2.1.307), dropping the broken output from the retry context (2.1.251). Then end with `The model's tool call could not be parsed (retry also failed).`

### Stop hooks and completion

22. When no tools were requested, the loop MUST run `Stop` hooks, unless the last message is an API error. API errors run `StopFailure` hooks instead, which prevents an error, hook block, retry spiral.
23. A blocking stop hook MUST continue the loop with its feedback. `additionalContext` from `Stop` or `SubagentStop` keeps the turn going without being labelled a hook error (2.1.163).
24. Stop-hook input includes `background_tasks` and `session_crons` (2.1.145).
25. `/goal` clears itself when a turn dies on an unrecoverable error (2.1.234).

### Between iterations

26. After tools, the loop MUST gather attachments (file-change notes, background notifications, queued input, memory and skill prefetch results, deferred tool announcements), check `maxTurns`, and continue.
27. Background task notifications between turns arrive inside system reminders (2.1.234).
28. Tool-use summaries are generated in the background and yielded on the next iteration.

### Limits

29. `--max-turns` / `maxTurns` limits iterations. Exceeding it ends the run with an error. In SDK terms: `error_max_turns`, with no final response. Count each tool-using turn plus one for the final text. With stream-json input, a message still queued when the limit ends a turn starts a new turn with its own limit.
30. `--max-budget-usd` / `maxBudgetUsd` ends the run with `error_max_budget_usd` once estimated cost reaches the cap, checked between messages. Spend can pass the cap. Subagent spend counts.
31. A subagent stopping at its `maxTurns` returns its output marked partial with a hint to continue it (2.1.246).
32. Snapshot behaviour: the blocking-limit check returns a too-long error before calling the API when automatic recovery can't handle it, for example with auto-compact off. It MUST NOT run on compaction requests themselves, which would deadlock. `blocking_limit` remains a documented terminal reason.

### Session engine

33. `QueryEngine` (SDK and headless) owns one conversation across `submitMessage` calls: messages, file-state cache, usage, permission denials. It translates loop events into SDK messages, emits `system`/`init`, `compact_boundary`, `api_retry` events, and ends with one `result` message. The interactive surface drives the same `query()` generator directly.
34. Every result subtype MUST carry `total_cost_usd`, `usage`, `num_turns` and `session_id`. Trailing system events such as `prompt_suggestion` can follow the result, so consumers must drain the stream.

### Compaction triggers

35. Auto-compact fires when the token count reaches the threshold for the session's auto-compact window (see [context-window-sizing.md](context-window-sizing.md)). The result yields a compact boundary and post-compact messages, and the iteration proceeds with those.
36. Repeated failure trips a circuit breaker (snapshot: 3 consecutive failures). Compaction that cannot make progress stops with a thrashing error rather than looping.
37. Summarization requests inherit the session's thinking configuration (2.1.198). If a reply contains no summary, the client usually asks once more before replacing the conversation (2.1.311).
38. Idle compaction can compact a conversation outside any user turn (2.1.299). Compaction mechanics belong to the memory-context spec area.

## Configuration & interfaces

| Result subtype | Meaning |
| - | - |
| `success` | Normal end; `result` text present |
| `error_max_turns` | `maxTurns` reached |
| `error_max_budget_usd` | Budget reached |
| `error_during_execution` | Error interrupted the loop; after a crash, cost fields may be zero and `stop_reason` null |
| `error_max_structured_output_retries` | No valid structured output within the retry limit, or a fallback retracted completed output |

SDK `terminal_reason` values: `completed`, `max_turns`, `tool_deferred`, `aborted_streaming`, `aborted_tools`, `hook_stopped`, `stop_hook_prevented`, `background_requested`, `blocking_limit`, `rapid_refill_breaker`, `prompt_too_long`, `image_error`, `model_error`, `api_error`, `malformed_tool_use_exhausted`, `budget_exhausted`, `structured_output_retry_exhausted`, `tool_deferred_unavailable`, `turn_setup_failed`. Meanings the docs don't state are open questions.

A `PreToolUse` hook returning `permissionDecision: "defer"` ends the run with `stop_reason: "tool_deferred"` and a `deferred_tool_use` record.

Snapshot loop transitions: `next_turn`, `reactive_compact_retry`, `max_output_tokens_escalate`, `max_output_tokens_recovery`, `stop_hook_blocking`, `collapse_drain_retry`, `token_budget_continuation`.

## Failure modes & edge cases

- Stop hooks that keep blocking on prompt-too-long would burn requests, which is why hooks are skipped there.
- A resumed session keeps usage from the transcript, so per-block entries must carry final token usage rather than streaming placeholders (2.1.97).
- `SIGTERM` headless behaviour: see [architecture-overview.md](architecture-overview.md).
- Long headless turns with many subagents must not retain each subagent's tool results until turn end (2.1.314).

## Gated

Behind build or runtime gates in the snapshot, with no public documentation: history snip, context collapse (with its own overflow drain), a `+500k`-style token budget auto-continue. API `task_budget` is now a documented SDK option (`taskBudget`), distinct from these.

## Changes since the snapshot

- 2.1.154: streaming tool execution always on.
- 2.1.163: `additionalContext` from stop hooks.
- 2.1.236: SIGTERM no longer records an interrupted turn.
- 2.1.243: `/model`, `/fast`, `/effort` apply mid-turn on every provider.
- 2.1.246: automatic continuation of cut-off responses in non-interactive sessions.
- 2.1.251, 2.1.307: malformed tool-call recovery improved, then two retries.
- 2.1.275: send-now key.
- 2.1.311: extra request when compaction returns no summary.

## Open questions

- Current max-output-tokens recovery numbers. The snapshot's escalate-to-64k and three nudges are unconfirmed for 2.1.314.
- Whether the capped default output tokens in the snapshot remain.
- Current state of snapshot-gated reductions (snip, collapse).
- Exact trigger for `rapid_refill_breaker`, `background_requested`, `tool_deferred_unavailable` and `turn_setup_failed`.
