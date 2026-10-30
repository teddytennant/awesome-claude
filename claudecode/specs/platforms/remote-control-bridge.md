# Remote Control Bridge Internals
**Status:** shipped (mechanics from snapshot; current wire details unverified)
**Provenance:** snapshot
**Sources:** snapshot `bridge/`, `remote/`; docs `remote-control.md`; changelog entries in [remote-control.md](remote-control.md)

## Purpose
Describe the client-side architecture behind Remote Control and remote session viewing. All statements describe the snapshot unless noted. Endpoints and credentials are omitted.

## Behaviour

### Topology
1. The bridge MUST run in two shapes: a standalone server loop (`bridgeMain`) that spawns child sessions, and an in-process REPL bridge (`replBridge`, set up by `initReplBridge`).
2. A newer env-less path (`remoteBridgeCore`) skips the environment and work-poll layer and connects a session directly. It has separate retry, heartbeat and token refresh config (`envLessBridgeConfig`) and its own minimum version.
3. Registration MUST create an environment describing machine name, directory, branch, git URL, max sessions, spawn mode and worker type (`claude_code`, `claude_code_assistant`).

### Work loop
4. The server loop polls for work. A response carries type `session` or `healthcheck`, and an encoded work secret with a session ingress token, API base URL, sources, and auth entries.
5. Poll intervals differ when at or below capacity and are remotely tunable. Defaults at capacity are long (10 minutes) since polling is a liveness signal and transport reconnects handle transient loss.
6. Backoff MUST separate connection and general errors, and SHOULD detect system sleep by a gap exceeding twice the backoff cap, resetting the budget.
7. `capacityWake` wakes the at-capacity sleep early when a slot frees.
8. Sessions have a default 24-hour timeout, and end with `completed`, `failed` or `interrupted`.
9. Children are spawned with an SDK URL and access token, and stdout is parsed for activities, held in a ring of about 10, for the status display.
10. In `worktree` mode the spawn mode is captured before async worktree creation, because `w` can mutate it mid-await.

### Transport
11. `ReplBridgeTransport` abstracts two generations: v1 (WebSocket read, HTTP POST write to session ingress) and v2 (SSE read, batched worker-event writes).
12. On connection, history MUST be flushed in one POST. `FlushGate` queues live messages until flush ends, so they do not interleave. The gate supports end (drain), drop (permanent close), and deactivate (transport swap).
13. Deduplication uses bounded UUID sets for echoes and re-delivery.
14. Worker heartbeat in the env-less path is about 20 seconds against a 60-second server TTL.
15. JWT expiry is parsed client-side to schedule refresh before `expires_in`.
16. Session IDs are translated between `session_` and `cse_` forms by `sessionIdCompat`.

### Messaging
17. Only eligible messages cross the bridge: user, assistant and selected system or local-command messages.
18. Inbound control requests (`initialize`, `set_model`, `can_use_tool`, `interrupt`, and others) MUST be answered. Unknown subtypes MUST yield an error so the server doesn't hang.
19. An outbound-only bridge MUST reject everything except `initialize`.
20. Permission decisions route through `bridgePermissionCallbacks`.
21. Inbound attachments are referenced by file UUID. They were written under `~/.claude/uploads/{sessionId}/` and prefixed as `@path`, best-effort with a 30-second timeout. Later versions pass photos directly (2.1.225).

### Crash recovery
22. A per-directory pointer file MUST be written after session creation, refreshed periodically, and cleared on clean shutdown. Staleness uses mtime, with a 4-hour TTL, which matches the documented "about four hours".
23. `--continue` searches git worktrees, capped at 50.

### Remote viewing
24. `RemoteSessionManager` and `SessionsWebSocket` let a CLI view a remote session with reconnect logic. `sdkMessageAdapter` converts SDK messages to REPL form.
25. `remotePermissionBridge` synthesises assistant messages and tool stubs so remote permission requests render in the local UI.

### Entitlement
26. Entitlement combined a build feature flag, a claude.ai subscriber check and a server gate. A blocking check refreshes a stale `false`. `getBridgeDisabledReason` gives diagnostics, and version floors exist.
27. Trusted device tokens are sent as a header when enabled. Attestation details are excluded from this spec.

## Configuration & interfaces
Types: `SpawnMode` (`single-session`, `worktree`, `same-dir`), `BridgeConfig`, `WorkResponse`, `SessionHandle`, `BridgeApiClient`. Flags: `--spawn`, `--capacity`. Snapshot debug helpers in `bridgeDebug` are internal.

## Failure modes & edge cases
- A 2-second shutdown budget forces a short archive timeout on teardown.
- Permanent close drops queued messages; transport replacement retains them.
- A silent session after `started` is detected by a connect timeout in the env-less path.

## Changes since the snapshot
- 2.1.224: compaction boundary and clear sync, stale archive. 2.1.225: direct photos.
- 2.1.232: about 30 minutes of reconnect. 2.1.236: quick offline marking.
- 2.1.281: attachment downloads reuse connections, skip duplicates.
- 2.1.288: credential renewal recovery.

## Open questions
- Whether v1 transport or the environment path remain in 2.1.314.
- Whether the remote-viewing CLI (`--remote` attach) persists, given `--cloud <id>` attach is refused.
