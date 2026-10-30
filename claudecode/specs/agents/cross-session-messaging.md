# Cross-Session Messaging

**Status:** shipped
**Provenance:** post-leak (since v2.1.224, 2026-08-07); a gated `UDS_INBOX` peer mechanism with `ListPeers` and `uds:`/`bridge:` addresses existed in the snapshot
**Sources:** docs `cross-session-messaging`, `tools-reference`, `settings-reference`, `sub-agents`, `errors`; snapshot `tools/SendMessageTool`, `tools.ts`; changelog 2.1.224 to 2.1.309

## Purpose

Sessions belonging to one user can pass text to each other, on this machine, on other machines, or in the cloud. The sender discovers targets with `ListAgents` and sends with `SendMessage`, the same tool that addresses subagents and teammates. A message is text only, never history or files, and carries no user authority.

## Behaviour

### Availability

1. Messaging MUST be on with nothing to enable on 2.1.224 or later on macOS, Linux and WSL 2, and 2.1.234 on native Windows.
2. Same-machine messaging works on every provider and with flag fetching off (2.1.248 for those cases), and never touches Anthropic servers.
3. Beyond this machine, discovery requires this session connected to Remote Control with a claude.ai sign-in as active authentication. API keys and third-party providers MUST NOT find those sessions.
4. `/list-agents` (alias `/peers`) is the check. If unrecognised, the session lacks the feature.

### Discovery

5. `ListAgents` and `/list-agents` list: subagents; own teammates (2.1.239); other local sessions that bound an inbox; cloud sessions and Remote Control sessions on other machines while connected. Remote Control rows are labelled, cloud rows labelled `cloud`, and dropped connections `offline`.
6. The first line MAY show this session's own name.
7. Local rows show working directories to tell same-named sessions apart.
8. While connected to Remote Control, `/list-agents` output MUST withhold local working directories, names that cannot be attributed to a person (shown as `(unnamed session)`), and the first line unless the name was typed at this terminal. It ends with a note. What the model sees MUST NOT change.
9. A session answers to `/rename` or `--name`, else a generated name.
10. A name matching exactly one live session MUST be deliverable alone. With duplicates, or when not every location could be checked, rows gain a short identifier used in the address.
11. Session lists are read newest first up to a bounded page count. Tools MUST say when the list was too long to check fully (2.1.234).
12. `@` mentions pick sessions from a typeahead (2.1.232). Names with other characters are quoted, `@"release notes"`. The model is told which session the mention names. Beyond-machine sessions appear only after the model has listed or messaged them. A name that several live sessions answer to MUST make the model ask which.

### Transport

| Target | Route |
| --- | --- |
| Same machine | Per-session Unix socket; named pipe on native Windows |
| Other machine | Anthropic servers, then its Remote Control connection |
| Cloud | Anthropic servers |

13. Containers and hosts cannot reach each other. Two sessions in one container can. WSL 2 and native Windows cannot.
14. `SendMessage` to an `offline` session succeeds and arrives after reconnect.
15. A row with `can't receive cross-session messages (off in that session)` MUST refuse before leaving this machine, with a result beginning `Not sent`.
16. Sending to a session beyond this machine with this session not connected MUST go through without a reply address.
17. Cloud sessions, including self-hosted runners, MUST NOT be able to answer a message from another machine with `SendMessage`.

### Delivery

18. During an active turn the receiver reads messages between tool calls, never interrupting a running tool. An idle receiver starts a new turn.
19. Content is plain text. `@` mentions in it MUST NOT attach anything. Commands such as `/compact` MUST NOT execute.
20. The sender-side refusals: over size (about a million serialized characters, with exact sizes reported); a rapid burst past what the inbox accepts; a target listed as unable to receive; a reply target failing a safety check such as a symlink.
21. A send to a local session that refuses MUST report `refused`, not silent success (2.1.238). A session whose inbox drops for rate or queue reasons MUST tell the sender.
22. Display: a dim one-line preview, `› Message from @api-worker: ...`, cut with `…`, staying in the conversation. `Ctrl+O` shows full text, and a message not yet received is listed under `Waiting to be delivered` (2.1.309). Fullscreen click expands. `--verbose` shows full text. The model always reads the whole message.
23. Receiving counts as usage, like a typed prompt.
24. Throttling on the receiver: per-sender rate limit, identical repeats dropped in a short window, at most 50 queued. A loop between two sessions thus stops on its own.
25. A subagent's send to another session MUST note in its result that any reply goes to the parent session (2.1.248). Messages from a session's own subagents are framed as from a worker in this session (2.1.251).

### Authority

26. The receiver MUST be told the message came from another session. It MUST NOT count as consent, answer a permission prompt, or justify changing permissions, CLAUDE.md or configuration.
27. Permission prompts fire normally on the receiving side.
28. The sender is instructed never to ask another session to do what was denied in its own, routing that back to the user.
29. In auto mode, messages are classified before dispatch (2.1.222), and relayed permission requests are refused (2.1.166).

### Inbound control

30. `crossSessionInbound`: `accept` delivers; `hold` shows a notice and does not deliver, releasing when `accept` later applies; `refuse` drops.
31. Precedence: managed, then `--settings`, then user; first value wins. A project or local value applies only when stricter. With no trusted value, a project or local `hold` or `refuse` still applies.
32. An unrecognised value outside managed settings MUST warn and hold, unless a `refuse` applies. In managed settings it MUST act as `refuse`.
33. With no value, the default is per message by class. Bypass class: `bypassPermissions`, and plan mode in interactive terminal sessions with bypass available. All others, including auto, `acceptEdits` and `dontAsk`, are the prompting class.
    - Receiver prompts: deliver, holding only if the sender identifies as bypassing.
    - Receiver bypasses: hold, delivering only if the sender identifies as bypassing.
34. A default hold in an interactive terminal opens an approval dialog with sender and preview. Approve delivers; Deny or dismiss drops; unanswered past `dialogExpiry` (five minutes) drops.
35. While no terminal is attached to a background session, the dialog MUST stay open past the deadline. After attach, a full deadline period applies. The row shows `approve message from` under `Needs input`.
36. Where a dialog cannot show (`-p`, VS Code, Desktop), held messages wait until the deadline, then drop, reported as expired to a reachable sender. `dialogExpiry: "never"` keeps them until session end. An explicit `hold` does not expire.
37. A class change while messages are held MUST re-apply the rules and deliver what is now accepted, with a notice.
38. At most 100 held messages; past that, oldest dropped.
39. `-p` workers bind an inbox; `--bare` sessions MUST NOT and do not appear. For unattended intake, set `crossSessionInbound: accept` in `--settings`.

### Idle notices

40. `SendMessage` with `notify_when_idle` subscribes to one notice when a local session next goes idle (a turn finished with nothing queued) or exits (2.1.236, both sessions).
41. Alone, it MUST start no turn and spend no tokens in the watched session, and notify at once if already idle. With a message, the message arrives first.
42. The watched session shows a line. The notice names the session, and may give the turn end time and a one-line status. An idle asker starts a new turn.
43. A subscription expires at 12 hours and the model is told.
44. `refuse` on either side: nothing arrives. `hold` on either side: the notice omits the status, and the asker shows it in the transcript without delivery to the model.
45. Only the main conversation may subscribe, and only to local sessions. Any other target MUST refuse the whole call, attached message included.

### Socket

46. Each messaging session binds an inbox socket. `/status` shows `Peer address` (`uds:` path), or `unavailable` and a reason.
47. `CLAUDE_CODE_MESSAGING_SOCKET` and `CLAUDE_CODE_MESSAGING_TOKEN` MUST be exported to hooks and Bash, before any hook when messaging is on at start.
48. On macOS and Linux the socket is restricted to the OS user. On native Windows connections authenticate with a key only that user can read.
49. Unacceptable directories are refused, falling back to `/tmp/cc-socks-<uid>`. If none is acceptable, the session runs without an inbox and shows a notice. A planted symlink or another user's directory MUST be refused (2.1.232).
50. A connection may open with `{"type":"auth","token":"<token>"}`. It is optional on macOS, Linux and WSL 2, required on native Windows. Connections sending no complete line within 30 seconds close (2.1.243).
51. Own-child messages: with no inbound value set, a verified message from the session's own child processes MUST be delivered. Verification is by process evidence, or by the token where that evidence is missing (macOS after exit, PID 1 containers, native Windows). Unverifiable messages are treated as asserting no class.
52. Sandboxed commands reach the socket per `sandbox.network.allowAllUnixSockets` and `allowUnixSockets`.

### Restriction

53. `isolatePeerMachines: true` from any scope MUST require approval before a message leaves this machine, even in `bypassPermissions`.
54. Stop sending and listing with deny rules naming `SendMessage` and `ListAgents`, bare with no specifier. Denying `SendMessage` also removes subagent and teammate messaging.
55. `refuse` still binds the socket, and nothing in `/status` or other sessions' listings reveals it, for same-machine peers.

## Configuration & interfaces

| Item | Detail |
| --- | --- |
| `SendMessage` | `to`, `message`, optional `summary`, `notify_when_idle` |
| `summary` | 5-10 words typical. If omitted on plain text, the first line. Truncated past 200 characters |
| `crossSessionInbound` | `accept`, `hold`, `refuse`; `/config` row **Messages from your other sessions**, hidden when managed or `--settings` sets it. `/config crossSessionInbound=...` rejected |
| `dialogExpiry` | Duration or `never`; `/config` row **Dialog expiry** |
| `isolatePeerMachines` | Boolean |

## Failure modes & edge cases

- A send to the session's own name says so rather than `no agent named` (2.1.239).
- A confirmed Remote Control recipient MUST NOT be swapped for a same-named local session when its list could not be checked (2.1.225).
- A backgrounded session lists once, as its background session, and messages no longer reach the terminal it left (2.1.260).

## Changes since the snapshot

- 2.1.166: relayed messages lose user authority.
- 2.1.224: public launch with `ListAgents`, `crossSessionInbound`, `dialogExpiry`.
- 2.1.225: start conversations with Remote Control sessions by name.
- 2.1.232: `@` mentions; bare-name delivery; `/config` rows.
- 2.1.235, 2.1.236, 2.1.238: up-front size, burst and refused reporting; `notify_when_idle`.
- 2.1.239: Windows; teammates listed. 2.1.247: one-line preview.
- 2.1.248: third-party providers; private fallback directory.
- 2.1.309: `Waiting to be delivered`.
- Tool renamed from snapshot `ListPeers` to `ListAgents`; `/peers` remains as an alias.

## Open questions

- Full `ListAgents` output schema and reference identifier format.
- `dialogExpiry` accepted value syntax.
- Whether the snapshot's `uds:` and `bridge:` address forms are still model-visible.
- The sender self-identification mechanism for the permission class.
