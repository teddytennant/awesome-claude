# Remote Control
**Status:** shipped
**Provenance:** both (bridge in snapshot, behind `BRIDGE_MODE`; heavily changed post-leak)
**Sources:** docs `remote-control.md`, `mobile.md`, `desktop.md`, `vs-code.md`; snapshot `bridge/`, `commands/bridge`; changelog 2.1.92 to 2.1.314

## Purpose
Attach claude.ai/code or the Claude app to a Claude Code session running on the user's machine, so a user can steer it from any device while execution, filesystem access and MCP servers stay local. See [remote-control-bridge.md](remote-control-bridge.md) for transport internals.

## Behaviour

### Eligibility
1. MUST need a claude.ai login on Pro, Max, Team or Enterprise. API keys are unsupported. On Team and Enterprise an Owner must enable the toggle. Custom roles need both the cloud sessions and **Claude Code remote control** permissions.
2. MUST NOT work with Bedrock, Agent Platform, Foundry, `ANTHROPIC_BASE_URL` on another host (2.1.196), or an enterprise Claude apps gateway (2.1.235 for `claude rc`).
3. MUST NOT work with ZDR or HIPAA-configured orgs.
4. `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` or `DISABLE_GROWTHBOOK` make it unavailable, since feature flags cannot be read. `DISABLE_TELEMETRY` or `DO_NOT_TRACK` alone leave it available unless Trusted Devices is required (2.1.283; 2.1.304 in Desktop).
5. Without an eligible login, `claude remote-control` MUST exit with an error, while `claude --remote-control` starts interactively and notifies of failure.
6. In an untrusted directory, `claude remote-control` MUST ask `Trust <directory>? [y/N]`. Home directory trust is never saved. Non-TTY exits with `Workspace not trusted`.
7. A one-time confirmation MUST be accepted before first start, in both server and `/remote-control` forms. Its options are briefly inactive after window refocus (2.1.281).

### Invocation
8. **Server mode:** `claude remote-control` (`claude rc`) MUST wait for connections, show a URL, a QR on spacebar, connection status and tool activity.
9. **Interactive:** `claude --remote-control [name]` or `--rc` MUST run a normal session also available remotely.
10. **Existing session:** `/remote-control [name]` or `/rc` MUST carry over history. VS Code takes no name and shows no QR.
11. Default names use the hostname prefix, such as `myhost-graceful-unicorn` (2.1.92).
12. Global flags before `remote-control` MUST NOT be carried silently. Harmless ones pass; others such as `--settings` refuse start and name the flag.
13. Each non-server process has at most one remote session. Server mode handles many.

### Spawn modes and server sessions
14. `--spawn same-dir|worktree|session`. `worktree` needs git or a `WorktreeCreate` hook. `session` rejects further connections.
15. `--capacity` defaults to 32 and is incompatible with `--spawn=session`.
16. `--create-session-in-dir` (default on) pre-creates a session. With `--no-create-session-in-dir` sessions are archived on stop.
17. `w` MUST toggle same-dir and worktree, saved per folder, with the source announced at the next start (2.1.305).
18. Server sessions begin with Chrome off unless `--chrome` is given.
19. A crashed server session MUST be re-served on the next message (2.1.238).
20. `--sandbox` and `--no-sandbox` are removed; passing them exits with an error (2.1.300). Sandbox comes from settings.

### Auto-connect
21. `remoteControlAtStartup` or `/config` **Enable Remote Control for all sessions**: `true`, `false`, `default`.
22. Repo-local settings MUST NOT turn it on, but can turn it off, even over a managed `true` (2.1.222).
23. `disableRemoteControl: true` MUST stop sessions connecting. A session already connected when the file is saved stays connected until turned off.

### Sync
24. Conversations and subagent or workflow progress MUST stay in sync. Terminal, browser and phone can send interchangeably.
25. Compaction progress and boundary, and `/clear`, MUST propagate (2.1.224).
26. `/resume` and `/teleport` MUST NOT send earlier history of the switched-to conversation, but new messages flow.
27. The diff pane MUST show changes since the merge base on ahead branches, otherwise uncommitted changes. It uses raw blobs.
28. Model picks from devices apply to the session; `/model <name>` also sets the default (2.1.238). Effort picks apply (2.1.234), except when `CLAUDE_CODE_EFFORT_LEVEL` pins a level.
29. `@`-file autocomplete works remotely (2.1.113). `/color` syncs (2.1.118).
30. Photos MUST reach Claude directly and be saved under `~/.claude/uploads/` with the path told to Claude (2.1.225). Other files download and become `@` references. Failed downloads add a note such as `[1 of 3 attachments did not arrive]`.
31. `SendUserFile` delivery retries once on timeout, network error or 502-504 (2.1.287).
32. `/btw` in app-hosted sessions sees the turn in progress (2.1.285).
33. Cross-session messaging uses the same connection, and `ListAgents` shows remote sessions as `name [ref]`, marks `offline` and `cloud` (2.1.225, 2.1.229).

### Commands from devices
34. Terminal-only commands do not work. Text commands work, value commands take arguments, and `/config` takes `key=value` on mobile but opens Settings on web. `/claude-api` is blocked from remote clients (2.1.285). `/usage-credits` prints a URL.
35. Supported with arguments or text forms: `/compact`, `/clear`, `/context`, `/usage`, `/exit`, `/recap`, `/reload-plugins`, `/model`, `/effort`, `/fast`, `/color`, `/rename`, `/mcp`, `/autocompact` (2.1.221), `/advisor` (2.1.260), `/output-style` (2.1.269, built-in only remotely), `/focus` (2.1.281).

### Status and failures
36. `/rc active` footer pill links to the session (2.1.162, 2.1.172), hidden when narrow. Fullscreen uses the header (2.1.268). Failures show a persistent `/rc failed` (2.1.178, 2.1.224).
37. `/remote-control` while connected MUST open a status panel with URL, QR and disconnect. In an auto-connected session it says it is already on.
38. Failure messages MUST distinguish takeover, end or archive elsewhere, and deletion, and MUST NOT suggest reconnects that undo those (2.1.232).
39. A session goes offline within seconds of exit (2.1.236).
40. Reconnecting continues about 30 minutes after a network blip (2.1.232). HTTP 403 from an edge is tolerated up to 3 minutes, with the refusing party named (2.1.238). In an outage, server mode exits after about 10 minutes, and interactive retries indefinitely.
41. Signing into a different account stops the session within seconds (2.1.234).
42. Credential expiry recovery keeps sessions connected during renewal (2.1.288).

### Resume
43. After stopping, `claude remote-control` brings back all sessions for about four hours. `--continue` brings back the first; `--session-id` one. Both exit when that session ends, and both unarchive since 2.1.228.
44. `--resume` in a second terminal MUST NOT steal Remote Control; it prints `Remote Control not started here`. `/remote-control` there moves it (2.1.232).
45. Deleted sessions on resume MUST start a replacement (2.1.232). A fresh session after compaction archives the stale one (2.1.224).

### Security
46. The local session makes outbound HTTPS only, and opens no inbound ports.
47. Transcripts MUST be stored on Anthropic servers while connected.
48. Multiple short-lived, purpose-scoped credentials are used.

### Trusted Devices
49. Off by default, in beta. Owners enable it org-wide at Organization settings, Capabilities, Remote sessions; Pro and Max users enable it for themselves.
50. When on, viewing or steering needs an enrolled device and a sign-in under 18 hours old, refreshed by biometric or passkey step-up.
51. Applies to sessions started after enabling. It also covers Cowork Computer access. Terminal, chat and API usage are unaffected.
52. Enrollment is offered only shortly after a full sign-in. The terminal receives its credential at CLI sign-in. Removing a device revokes immediately.

### Push
53. `/config` toggles **Push when Claude decides** and **Push when actions required**. Claude MAY send a push through a notification tool (2.1.110).
54. Pushes are skipped while the user is typing or focused in the terminal. `CLAUDE_CLIENT_PRESENCE_FILE` extends this to the file's existence.

## Configuration & interfaces
| Item | Purpose |
|---|---|
| `--name`, `--remote-control-session-name-prefix`, `CLAUDE_REMOTE_CONTROL_SESSION_NAME_PREFIX` | Names |
| `-c`, `--session-id` (2.1.200) | Resume; exclusive with `--spawn`, `--capacity`, `--create-session-in-dir` |
| `--permission-mode` | Server start mode; bad value stops startup |
| `--chrome`, `--no-chrome` | Chrome in spawned sessions |
| `-d`, `--debug[=filter]` (2.1.282), `--debug-file`, `--verbose` | Diagnostics |
| `remoteControlAtStartup`, `disableRemoteControl` | Settings |
| `attribution.sessionUrl` | Omit session URL (2.1.183) |
| `CLAUDE_CODE_BRIDGE_SESSION_ID` | Set in child processes while connected |

## Failure modes & edge cases
| Message | Cause |
|---|---|
| "requires a claude.ai subscription", "full-scope login token" | Wrong login type |
| "isn't enabled for this account" | Gate, check failure, stale entitlement or org (2.1.178) |
| "requires feature-flag evaluation" | Flags disabled |
| "only available when using Claude via api.anthropic.com" | Names the setting (2.1.219) |
| "disabled by your organization's policy", "turned off by" | Policy or roles |
| "Couldn't verify your organization's policy" | Policy unavailable |
| "Previous session is unavailable" | Session gone |
| Trusted Devices errors | Org requires it; expired check |

Forwarded dialogs other than permissions and questions expire after five minutes by default. The Fable usage-credits consent prompt is not forwarded.

Connector re-authorization from a device uses `claude mcp login "claude.ai <Name>" --no-browser` on the host.

## Changes since the snapshot
- 2.1.92: hostname names. 2.1.110: push. 2.1.113: `@` completion, `/extra-usage`.
- 2.1.162 to 2.1.178: footer pill and failure states. 2.1.196: non-Anthropic base URL disabled.
- 2.1.222: repo settings can't enable. 2.1.224: compaction visibility, persistent failures, stale archive.
- 2.1.225: photos, `SendMessage` by name. 2.1.232: reliability set. 2.1.234: account change stop, effort.
- 2.1.236, 2.1.238: offline marking, 403 tolerance, crash re-serve.
- 2.1.251: VS Code pill. 2.1.271: fewer empty sessions. 2.1.281: confirmation guard.
- 2.1.285: `/claude-api` blocked. 2.1.288: credential recovery. 2.1.300: sandbox flags removed.
- 2.1.305: spawn mode messages. 2.1.307: faster connect with large images.

## Open questions
- Exact credential lifetimes and which are in use.
- Whether a default for `remoteControlAtStartup` varies by plan.
