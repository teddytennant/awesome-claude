# MCP Tasks

**Status:** preview (public beta in CLI)
**Provenance:** post-leak (since v2.1.304 per docs, 2026-10-19)
**Sources:** docs `mcp`, `env-vars`, `hooks`. No dedicated changelog entry found in the topic files.

## Purpose

An MCP task is a long job a server runs itself under the MCP tasks extension. The tool call returns on acceptance, Claude keeps working, and the result arrives when the job ends. This is distinct from automatic backgrounding of a plain call, which does not survive exit ([mcp-client.md](mcp-client.md)).

## Behaviour

### Eligibility

1. A call MUST become a task only when all hold: the server supports tasks; it is an HTTP, stdio or connector server on revision 2026-07-28; the session fetches feature flags; tasks are on for the session kind (terminal CLI, SDK, GitHub Actions at v2.1.304, not VS Code or Desktop); the call is from the main conversation; and the session is interactive, or an SDK or stream-json run with `CLAUDE_AUTO_BACKGROUND_TASKS=1`, `CLAUDE_CODE_DISABLE_MCP_TASK_BACKGROUND` not `1`, and `CLAUDE_CODE_MCP_AUTO_BACKGROUND_MS` not `0`.
2. `MCP_SDK_GENERATION=v1` or `MCP_PROTOCOL_NEGOTIATION=legacy` rules tasks out.
3. One-shot `claude -p "<prompt>"` does not get tasks. SDK and stream-json runs MUST keep input open, as the run does not wait after it closes.

### Client behaviour

4. The footer shows a count such as `1 MCP task`. Tasks appear in `/tasks`, and `x` stops one. `Esc` does not. Stopping requests cancellation; the server may still finish.
5. Result goes to the model, not the transcript. If idle, the model starts on it unprompted.
6. Tasks may open elicitation dialogs, hidden while `/tasks` is open. Decline and `Esc` are answers. Non-interactive sessions MUST ask the server to cancel a task needing input, without running `Elicitation` hooks or `onElicitation`.
7. No Claude Code time limit applies in the background. Call limits apply until the task answer, or for the whole task if waiting. Answered status checks count as activity for idle timeout.
8. Waiting: `CLAUDE_CODE_MCP_AUTO_BACKGROUND_MS=0` waits for every call. `CLAUDE_CODE_DISABLE_MCP_TASK_BACKGROUND=1` waits for tasks, with the usual two-minute move as a plain background call. While waiting, `Esc` or a limit ends the call and asks cancellation.
9. `CLAUDE_CODE_DISABLE_BACKGROUND_TASKS=1` and bare mode alone do not make Claude wait.

### Across sessions

| Situation | Result |
| :- | :- |
| `/clear`, `/branch`, `/resume` elsewhere | Result arrives in the current conversation while open |
| Exit | Remote tasks continue; no exit option cancels; stdio process stops |
| Interactive resume of that session | Followed again once the server connects |
| `--resume` in one-shot `-p` | Not followed |
| New session, `--fork-session` | Not followed |

### Server contract

10. On revision 2026-07-28 each request carries capabilities at `params._meta["io.modelcontextprotocol/clientCapabilities"]`. Servers MUST answer with a task only when `"io.modelcontextprotocol/tasks": {}` is under `extensions`.
11. Task object as `tools/call` `result`: `resultType: "task"`, `taskId` (at most 128 printable ASCII, no spaces), `status` (`working`, `input_required`, `completed`, `failed`, `cancelled`), `createdAt`, `lastUpdatedAt`, `ttlMs` (nullable), optional `pollIntervalMs` (non-null, clamped 250 to 30000, default 2000), optional `statusMessage`.
12. Missing fields or a bad status give `Unsupported result type 'task' for tools/call`. A malformed ID gives `returned a malformed task handle`. `ttlMs` expiry does not drop a task.
13. Polling: `tasks/get` right after acceptance, then per interval. Responses carry `resultType: "complete"` plus the same fields. HTTP and connector task answers MUST start within the per-request timer.

| Status or method | Handling |
| :- | :- |
| `working` | Keep polling |
| `completed` | Top-level `result` as `tools/call`; `isError` is failure |
| `failed` | Top-level `error.message`, else `statusMessage`, else `Task failed` |
| `cancelled` | `statusMessage`, else `Task was cancelled by the server` |
| `input_required` | `inputRequests` map answered once each via `tasks/update` with `inputResponses`; over 16 keys ignored |
| Other status | Cancel and report failed |
| JSON-RPC `-32602` | Unknown ID; keep asking up to five minutes, then unknown |
| `tasks/cancel` | Sent on stop while connected; not on exit |
| `tasks/result`, `tasks/list`, `notifications/tasks` | Not used |

14. `elicitation/create` in `inputRequests` is served only in interactive terminal sessions; `roots/list` everywhere. Otherwise the client asks cancellation.

## Configuration & interfaces

| Variable | Effect |
| :- | :- |
| `CLAUDE_CODE_MCP_AUTO_BACKGROUND_MS` | `0` waits for all calls |
| `CLAUDE_CODE_DISABLE_MCP_TASK_BACKGROUND` | `1` waits for tasks |
| `CLAUDE_AUTO_BACKGROUND_TASKS` | `1` for SDK and stream-json |

## Failure modes & edge cases

Status messages: `reconnecting…`, `needs a sign-in to <server>`, `status requests come back with errors; retrying…`, and 300-second forms for no reconnect, no accepted sign-in, and errors. `is not configured in this session`, `was reconfigured to a different transport since this task was created`, `the server rejected this task's id; asking again…`, and `outcome unknown.`, after which a repeat call may duplicate work.

Stopping a task on a disconnected server sends no cancel and forgets the task. Server name and connection settings MUST stay unchanged to follow a task across resume.

## Changes since the snapshot

- v2.1.304: MCP tasks public beta (docs).

## Open questions

- The changelog topic files have no entry naming MCP tasks; the version comes from the docs alone.
- Stop hook `background_tasks` reports these as `MCP task`, but behaviour across `/goal` and similar loops is unspecified.
