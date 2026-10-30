# Forked Subagents and Session Forks

**Status:** shipped
**Provenance:** both (fork subagent gated in snapshot; default-on and `/fork` session copy post-leak, since v2.1.212, 2026-07-16)
**Sources:** docs `sub-agents`, `agent-view`, `agents`, `commands`; snapshot `tools/AgentTool/forkSubagent.ts`, `commands.ts`; changelog 2.1.117, 2.1.121, 2.1.212, 2.1.216, 2.1.221, 2.1.232, 2.1.257, 2.1.273, 2.1.302, 2.1.307

## Purpose

Two features share the word "fork". A forked subagent is an in-session worker that inherits the whole conversation, so it needs no briefing and reuses the prompt cache. A session fork copies the conversation into a new, independent background session. This spec defines both and how the commands map to them.

## Behaviour

### Fork mode

1. Fork mode MUST be on by default in every interactive and non-interactive surface (terminal 2.1.232; `-p`, SDK, desktop, VS Code 2.1.302). `claude mcp serve` MUST never offer forks.
2. `CLAUDE_CODE_FORK_SUBAGENT=0` MUST turn fork mode off. `permissions.deny` with `Agent(fork)` stops forks only, leaving other fork-mode effects in place.
3. While fork mode is on, the model MUST NOT be able to wait for a subagent in interactive terminal, VS Code or desktop sessions on the local machine.

### Forked subagent semantics

4. A fork is requested with `subagent_type: "fork"` on the Agent tool or by the user with `/subtask <task>`.
5. A fork MUST inherit full message history, the rendered system prompt, the exact tool pool, and the model of the parent at spawn. It ignores background tool filters.
6. A fork's first request MUST reuse the parent's prompt cache, which requires an identical system prompt and tool definitions. In the snapshot design, sibling forks also shared a message prefix, differing only in the per-child directive.
7. The tool calls that a fork makes MUST stay out of the parent's transcript. Only its final result returns, as a message in the main conversation.
8. A fork MUST NOT spawn another fork. It keeps `Agent` listed so tool definitions stay identical, and the tool returns an error at call time. At the depth limit `Agent` likewise errors in a fork rather than being withheld.
9. `/subtask` MUST work whether or not fork mode is on and is named from the first words of the task. It takes a concurrency slot and MUST NOT be blocked by the concurrent subagent limit.
10. A fork MUST receive no `--append-subagent-system-prompt` text and retains the output style, because it reuses the conversation's prompt.
11. The per-invocation `effort` parameter applies only to non-fork subagents. A fork MUST stay on the main model under `CLAUDE_CODE_SUBAGENT_MODEL_FORCE`.
12. The Agent call may pass `isolation: "worktree"` for a fork, so that edits land in a separate worktree.
13. Forks launched together MUST each be told which launch is theirs, so they do not start each other's work (2.1.307).
14. `SubagentHandback` MUST NOT be provided to forks.

### Panel and steering

15. Running forks MUST appear in the panel below the prompt, with one row for main and one per fork. `↑`/`↓` move, `Enter` opens the transcript and allows follow-ups, `x` stops or dismisses, `Esc` returns focus.
16. On the main row, or on the row whose transcript is open, `x` MUST type into the prompt instead.
17. A successful fork's row is removed. A failed or stopped fork's row stays for 30 seconds.

### Session copy with `/fork`

18. With agent view available, `/fork [prompt]` MUST copy the conversation into a new background session while the original keeps running. With agent view turned off, `/fork` MUST start a forked subagent and `/subtask` MUST be unavailable.
19. The copy MUST carry the conversation so far, the model, permission mode, effort, added directories and "don't ask again" grants. It appears as its own row and starts with `SessionStart` source `fork` (2.1.214).
20. A prompt starts the copy working at once. Without one the copy waits, and its selected row shows `space to send it a prompt`.
21. The copy's name comes from the session name, or from the prompt when the session has no title (2.1.212).
22. The confirmation MUST be one line: state, row name, and session ID for `claude attach`. Clicking the name moves this session to the background and opens the copy. It ends with `runs in the origin tree` or `edits this checkout` only when applicable (2.1.216).
23. The two sessions MUST then be independent. Messaging between them requires cross-session messaging.
24. The copy's worktree briefing MUST arrive as a message, not a system-prompt change, keeping the original prompt cache (2.1.257).

### Where the copy runs

25. Unless it edits in place, the copy MUST be instructed to create its own worktree before code changes (2.1.221). Outside git, only a copy moved out of a hook-created worktree gets the instruction.
26. A copy moved out of the user's worktree MUST be told never to edit, run commands in, or enter that worktree, regardless of the isolation setting.
27. If the session moved into a linked worktree after starting, the copy MUST start where the session was before the move. When that worktree is on a branch, the instruction also tells a copy whose task builds on that work to base its branch on it.
28. If the session launched inside a linked worktree of a repository with a main working tree, the copy MUST start in the main working tree, with no branch instruction.
29. If the session launched inside a worktree of a bare-repository layout, the copy stays put and the confirmation ends `edits this checkout`. The same note applies when isolation is off outside a linked worktree.

### Refusals

30. Sessions launched with flags the copy would not inherit, such as a replaced system prompt or a `--tools` allowlist, MUST be refused with an explanation rather than partially copied.
31. A session dispatched from agent view MUST fork normally, keeping the same agent definition and appended instructions.
32. `/fork` of a session that itself began as a copy and has no new prompt MUST still copy the full conversation (fixed 2.1.246).

### Related

33. `/branch` branches the conversation and switches into the branch; it is a transcript operation, not a fork of execution.
34. A session started with `claude --remote-control` or `/remote-control` can be forked from the Claude app, running as a background session on the local machine (2.1.273).
35. `context: fork` skills run through subagent machinery but follow the skill rules; they run in the background by default, with `background: false` to opt out (2.1.218).

## Configuration & interfaces

| Surface | Meaning |
| --- | --- |
| `subagent_type: "fork"` | Model-initiated fork |
| `/subtask <task>` | User-initiated fork |
| `/fork [prompt]` | Session copy, or forked subagent when agent view is off |
| `CLAUDE_CODE_FORK_SUBAGENT` | `0` off; default on |
| `Agent(fork)` | Permission rule target |
| `--fork-session` | With `--resume`, new session ID (see [background-sessions.md](background-sessions.md)) |

## Failure modes & edge cases

- A fork's `isolation: "worktree"` does not change context inheritance; it starts from the parent's messages with different file state.
- `CLAUDE_CODE_DISABLE_BACKGROUND_TASKS=1` also stops background runs of forked skills.

## Changes since the snapshot

- 2.1.117: forks enabled on external builds with `CLAUDE_CODE_FORK_SUBAGENT=1`. 2.1.121: works in non-interactive sessions.
- 2.1.212: `/fork` became a session copy; subagent behaviour moved to `/subtask`.
- 2.1.214: `SessionStart` reports `fork`.
- 2.1.216: one-line confirmation. 2.1.221: copy gets its own worktree. 2.1.257: prompt cache preserved.
- 2.1.232: default on in the terminal, with `subagent_type: "fork"` explicit rather than implied by an omitted type as in the snapshot.
- 2.1.302: default on everywhere else.
- 2.1.307: sibling-awareness.

## Open questions

- Current fork `maxTurns`. The snapshot had 200; docs do not say.
- Snapshot fork mode was mutually exclusive with coordinator mode. Unknown now.
- How permission prompts surface for forks in 2.1.314. The snapshot bubbled them to the parent; docs imply the same as background agents.
