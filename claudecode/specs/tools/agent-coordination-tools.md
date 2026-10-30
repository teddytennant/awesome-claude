# Coordination Tools: ListAgents, SubagentHandback, WaitForMcpServers

**Status:** shipped
**Provenance:** post-leak (ListAgents since v2.1.224, 2026-08-07; SubagentHandback requires v2.1.271; WaitForMcpServers: no dated introduction found)
**Sources:** docs `tools-reference`, `cross-session-messaging`, `sub-agents`, `hooks`, `mcp`, `prompt-caching`, `agent-sdk/typescript`; changelog 2.1.224, 2.1.229, 2.1.234, 2.1.239, 2.1.248, 2.1.285

## Purpose

Small tools that help work move between agents: find who can be messaged, hand a report back reliably, and wait for an MCP server that is still connecting. `SendMessage` itself and the messaging protocol belong to the agents area.

## Behaviour

### ListAgents

1. Lists the agents Claude can message with `SendMessage`, and backs `/list-agents`, also available as `/peers`.
2. The first line, when present, is this session's own name, the one peers use to reach it (v2.1.239+).
3. Rows:

| Kind | Shown when |
| :- | :- |
| Subagents | Running in this session |
| Teammates | This session's team (v2.1.239+) |
| Other local sessions | Same machine, including background; only those binding an inbox socket |
| Cloud sessions | This session is connected to Remote Control; labelled `cloud` |
| Remote Control sessions on other machines | Same; labelled `Remote Control`, shown `name [ref]`, status `offline` when disconnected |

4. It MUST appear only where cross-session messaging is enabled: v2.1.224+ on macOS, Linux and WSL 2; v2.1.234+ on native Windows; v2.1.248+ for same-machine messaging on third-party providers or with flag fetching off.
5. Reaching sessions beyond this machine needs a claude.ai sign-in as the active authentication and Remote Control. API keys and third-party providers cannot.
6. It MUST state when the account's session list was too long to check fully, rather than treating unseen sessions as absent (2.1.234). Lists are read newest first over a bounded number of pages.
7. Remote Control connected: the `/list-agents` output withholds some details of local sessions, while what Claude sees is unchanged.
8. Internal idle pre-warmed workers MUST NOT be listed until a task claims them (fixed 2.1.238), and a backgrounded session MUST NOT appear twice (fixed 2.1.260).
9. A foreground subagent inherits the tool where messaging is enabled. A background subagent does not keep it.
10. Deny rules take the bare tool name. A deny on `SendMessage` and `ListAgents` stops sending and listing; `crossSessionInbound: refuse` stops receiving.
11. `/status` shows a `Peer address` row with the inbox address, or `unavailable` with the reason.

### SubagentHandback

12. Delivers a subagent's final report to whichever conversation receives its result.
13. Provided only in auto mode, to subagents the Agent tool runs locally, excluding forks, in the terminal CLI, IDE extensions, cloud sessions and the Agent SDK. Requires v2.1.271+.
14. Where the conditions hold, the subagent MUST get the tool, even if it is omitted from `tools` or listed in `disallowedTools`. Background subagents keep it.
15. The classifier reviews the report before delivery. No prompt appears, and the call runs even if the classifier objects.
16. A PreToolUse hook can stop a call by returning `"deny"`. The subagent is told up to three times that the report was not delivered and to call again. If denial continues, the subagent ends without delivering through this tool, and the waiting conversation gets a note.
17. A subagent's run MUST end as soon as it hands back, without further turns (2.1.285).
18. The Agent tool's `completed` result, and the hook `content` field, carry a short note about the hand-back in place of the report.

### WaitForMcpServers

19. Waits for one or more MCP servers still connecting in the background, so a request can use their tools without restarting.
20. Claude calls it when a needed server is not connected.
21. It MUST appear only when tool search is disabled, since `ToolSearch` does the wait when enabled. Such configurations include `ENABLE_TOOL_SEARCH=false`, and models earlier than Opus 4.5, Sonnet 4.5, Haiku 4.5 on Agent Platform.
22. A Foundry deployment hosted on Azure starts on the tool-search path, as the rejection is only discovered from the API. After the switch to upfront loading, tools arrive on Claude's next request.
23. Subagents never get it.
24. A request sent while a remote server reconnects can add this tool, invalidating the prompt cache once.

## Configuration & interfaces

| Key | Effect |
| :- | :- |
| `crossSessionInbound` | `accept`, `hold` or `refuse` for inbound messages; `/config` row **Messages from your other sessions** (v2.1.232+) |
| `ENABLE_TOOL_SEARCH` | `false` brings WaitForMcpServers in |
| `MCP_CONNECTION_NONBLOCKING` | `0` makes startup wait |

None of these three tools has a published SDK input type. `SubagentHandback` and `ListAgents` take bare names in rules.

## Failure modes & edge cases

- A session can be addressed through an `@` mention without Claude listing sessions first.
- A message to an `offline` peer goes through but arrives after reconnection.
- Older cloud or other-machine sessions that fell past the bounded pages cannot be messaged by name.
- Background subagents in auto mode used to send reports twice (fixed 2.1.299).
- A session's own name, messaged directly, says so rather than "no agent named" (2.1.239).

## Changes since the snapshot

- 2.1.224: `ListAgents`, with cross-session `SendMessage`.
- 2.1.225: Remote Control peers by name.
- 2.1.229: `offline` and `cloud` labels.
- 2.1.234: incomplete-list notice.
- 2.1.239: teammates listed, own name shown, Windows availability.
- 2.1.248: same-machine messaging on third-party providers and with telemetry off.
- 2.1.285: subagent runs end at hand-back; redundant reply prompt removed.
- v2.1.271 (docs): `SubagentHandback`.

## Open questions

- First native Windows version: docs say v2.1.234; the changelog announces it at 2.1.239.
- Whether `ListAgents` output has a stable structured form.
- Input of `WaitForMcpServers` (server names or all) and its timeout.
- What the classifier's review of a hand-back can change, given the call runs even on objection.
- Whether the snapshot's gated `ListPeersTool` is the origin of `ListAgents`.
