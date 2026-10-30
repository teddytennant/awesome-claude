# Coordinator Mode

**Status:** gated/unreleased
**Provenance:** snapshot
**Sources:** snapshot `coordinator/coordinatorMode.ts`, `constants/tools.ts`, `tools.ts`, `tools/AgentTool/builtInAgents.ts`, `tools/AgentTool/forkSubagent.ts`; absent from public docs and changelog as a Claude Code mode

## Purpose

In the snapshot, coordinator mode turned the main session into an orchestrator with almost no direct tools. It delegated all work to workers and synthesised their results for the user. It is covered here at feature level because no public documentation describes it.

Do not confuse it with unrelated uses of the word: the Agent SDK message origin `{ kind: "coordinator" }` (documented as a team coordinator in an agent team), the project conversation "coordinator" in Projects, or the `coordinator` setting of Managed Agents in the `claude-api` skill (2.1.309).

## Behaviour

Everything below is snapshot evidence only and MUST NOT be read as current behaviour.

### Activation

1. The mode required a build-time flag and a truthy `CLAUDE_CODE_COORDINATOR_MODE` environment variable. External builds had the flag compiled off.
2. The check read the variable live, with no caching.
3. Sessions recorded their mode as `coordinator` or `normal`. On resume, a mismatch flipped the variable to match and surfaced a notice that the session had entered or exited the mode. Sessions with no stored mode were left alone.

### Tool surface

4. The coordinator's own tools were limited to `Agent`, `TaskStop`, `SendMessage` and the structured-output tool.
5. In simple mode (`CLAUDE_CODE_SIMPLE`), Agent, TaskStop and SendMessage were added to the Bash, Read and Edit set, so that the coordinator got the former and workers the latter.
6. Workers received the async-agent allowed tools, minus team management, `SendMessage` and structured output, plus MCP tools from connected servers.
7. Coordinator mode replaced the built-in agent list with a separate worker agent set from `coordinator/workerAgent.js`. That module is missing from the snapshot.
8. Fork subagents were disabled while coordinator mode was on, because the coordinator already owned orchestration.

### Prompting

9. A dedicated system prompt replaced the default, casting the model as an orchestrator whose user-facing output is a synthesis of worker results.
10. It set out a phased workflow of research, synthesis, implementation and verification, with concurrency guidance, failure handling, and instructions on writing self-contained worker prompts.
11. User context listed the tools available to workers, the MCP servers, and an optional scratchpad directory that workers could use without prompts for durable cross-worker knowledge. The scratchpad had a separate gate.

### Interaction

12. Agents ran asynchronously, reporting through task notifications.
13. Continuing a worker by message was preferred when context overlapped, and spawning fresh otherwise. Stopped workers could be continued.

## Configuration & interfaces

| Item | Detail |
| --- | --- |
| `CLAUDE_CODE_COORDINATOR_MODE` | Activation variable, undocumented |
| `CLAUDE_CODE_SIMPLE` | Reduces worker tools |
| Session mode | `coordinator` or `normal` in session metadata |

## Failure modes & edge cases

- Mode mismatch on resume changed the mode rather than refusing.
- Scratchpad text appeared only when both a path and its gate were present.

## Changes since the snapshot

None found. No changelog entry or doc mentions this mode. Features with overlapping aims have shipped publicly: background-by-default subagents with completion notifications (2.1.198, 2.1.232), resume through `SendMessage`, [dynamic workflows](dynamic-workflows.md) (2.1.154), and [agent teams](agent-teams.md). The `/claude-api` change in 2.1.309 concerns Managed Agents.

## Open questions

- Whether the code path, variable or build flag still exists in 2.1.314. This cannot be determined from allowed sources.
- Whether Projects' cloud "coordinator" conversation reuses it.
- Worker agent definitions, since the module is missing from the snapshot.
- Interaction with teams and `SubagentHandback`, which postdate the snapshot.
