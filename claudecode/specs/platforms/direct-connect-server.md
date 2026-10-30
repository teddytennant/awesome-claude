# Direct Connect Server
**Status:** gated/unreleased
**Provenance:** snapshot
**Sources:** snapshot `server/`, `main.tsx` (`DIRECT_CONNECT` feature)

## Purpose
A snapshot-only feature: a local Claude Code session server, with a thin CLI client that connects to it. Public docs and `--help` for 2.1.314 do not list it.

## Behaviour
1. `claude server` MUST start a session server, with `--port` (0), `--host` (`0.0.0.0`), `--auth-token`, `--unix`, `--workspace`, `--idle-timeout` (600000 ms; 0 never), `--max-sessions` (32; 0 unlimited).
2. Clients MUST create a session by HTTP and receive `session_id`, `ws_url` and optional `work_dir`.
3. `claude connect <url>` and `cc://` or `cc+unix://` URLs MUST open the full TUI against a remote server. With `-p`, a `cc://` URL is rewritten to an internal `open` subcommand that runs headless instead.
4. Session states are `starting`, `running`, `detached`, `stopping`, `stopped`.
5. A session index in `~/.claude/server-sessions.json` MUST map stable keys to session IDs, transcript IDs, working directory, permission mode and timestamps, so sessions resume across restarts.
6. `DirectConnectManager` exchanges SDK messages and permission requests over WebSocket, and users answer permission prompts locally.

7. The server MUST hold sessions as subprocesses and detach them when a client disconnects. Detached sessions expire by `--idle-timeout`.
8. A client session is created by POST with a working directory, falling back to the server's `--workspace` default, and resumes by stable key through the index.
9. Permission requests from a remote session MUST be forwarded to the connected client rather than answered on the server, and the client returns an allow or deny response.
10. Inbound interrupts and user messages MUST use the same SDK message forms as stream-json, so the client reuses the normal TUI over a remote transport.
11. The feature is compiled out of external builds unless the `DIRECT_CONNECT` build flag is on.

## Configuration & interfaces
Flags listed in item 1. Types: `ServerConfig`, `SessionInfo`, `SessionIndexEntry`.

## Failure modes & edge cases
- Binding `0.0.0.0` with no token exposes the server to the network, and a generated token is the mitigation in the snapshot's startup path.
- Connection failures during session creation surface as `DirectConnectError`, with the CLI exiting rather than starting a local session.
- A session index survives restarts, but a subprocess does not, so resumption relies on the transcript ID and `--resume`.
- Sessions at `--max-sessions` cannot be created until one ends; `0` removes the cap.

## Changes since the snapshot
- None found.

## Open questions
- Whether this shipped under another name, or was dropped.
