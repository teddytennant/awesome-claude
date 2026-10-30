# Channels

**Status:** preview (research preview)
**Provenance:** both (research preview since v2.1.80, before the snapshot; organization, relay and runtime rules changed after it)
**Sources:** docs `channels`, `channels-reference`, `mcp`, `plugins__manifest-reference`; snapshot `services/mcp/channelNotification.ts`, `channelPermissions.ts`, `channelAllowlist.ts`; changelog 2.1.80, 2.1.81, 2.1.128.

## Purpose

A channel is an MCP server that pushes events into a running session, so the model can react to chat messages, CI results or alerts while the user is away. Channels can be two-way, and can relay permission prompts. Events arrive only while the session is open.

## Behaviour

### Availability

1. Channels MUST require Anthropic authentication through claude.ai or a Console API key (Console since v2.1.128). They are not available on Bedrock, Agent Platform or Foundry.
2. No channel runs until opted in per session with `--channels`. Being in `.mcp.json` is not enough.
3. `--channels` and `--dangerously-load-development-channels` work but are hidden from `claude --help` during the preview.
4. Pro and Max without an organization skip organization checks.
5. `channelsEnabled` is the master switch: required on claude.ai Team and Enterprise, and on Console orgs deploying managed settings. When off, the server connects and its tools work, but messages do not arrive, with a startup warning.
6. `allowedChannelPlugins` replaces the Anthropic list and requires `channelsEnabled: true`. `[]` blocks the list, but the development flag can still bypass; to block everything, leave `channelsEnabled` unset. An unreadable managed value MUST admit nothing.
7. A non-allowlisted plugin MUST start normally without registering, with a startup notice.
8. On the v2 runtime, a server negotiating revision 2026-07-28 MUST NOT register as a channel, as that revision cannot carry channel messages. Stdio servers are asked for it by default; `MCP_PROTOCOL_NEGOTIATION=legacy` keeps them on the earlier handshake.

### Server contract

9. A channel server MUST declare `capabilities.experimental['claude/channel']: {}`, emit `notifications/claude/channel`, and connect over stdio.
10. `instructions` SHOULD be set, and is delivered to the model at connection, explaining events, attributes and replies.
11. Notification params: `content` (string body), `meta` (string map). `meta` keys MUST be identifiers; others are silently dropped. The model receives `<channel source="...">` with `meta` as attributes, where `source` uses the scoped server name, such as `plugin:fakechat:fakechat`.
12. Two-way channels declare `capabilities.tools: {}`, expose a reply tool, and instruct its use. The terminal shows the inbound line and tool confirmation, not the reply text.
13. Channel servers MUST gate inbound messages on sender identity, to prevent prompt injection. Official plugins keep a sender allowlist and silently drop others. Telegram and Discord pair with a code; iMessage admits self-texts and adds handles with `/imessage:access allow`.

### Permission relay

14. Declaring `capabilities.experimental['claude/channel/permission']: {}` opts in. `false` or omission opts out (`false` was treated as declared before v2.1.234).
15. Requests MUST go only to servers registered as channels for the session (v2.1.234).
16. Claude Code sends `notifications/claude/channel/permission_request` with `request_id` (five lowercase letters, excluding `l`), `tool_name`, `description` (a summary, or the constant `Run shell command`), and `input_preview`.
17. Text is sanitized: direction-override, invisible and lookalike characters neutralized; whitespace folded; values relayed whole to 3,500 code points, then start and end around an elision marker; recognizable secrets masked, including key names. Spans with shell, path or URL characters are never masked, so a mask cannot hide what is approved. Unprefixed or whitespace-spanning secrets are not masked.
18. Verdicts arrive as `notifications/claude/channel/permission`, with an ID matching an open request. Unknown IDs drop silently. If an ID repeats within a session, all channel verdicts carrying it are dropped.
19. Inbound text that does not match the verdict form falls through as a normal message.
20. Anyone who can reply through the channel can approve tool use, so servers MUST authenticate senders before declaring this.

### Non-interactive

21. In `-p`, tools needing terminal input are disabled, so the session cannot stall (interactive sessions keep plan-mode tools, restored in v2.1.126). An unattended prompt otherwise pauses the session until answered or relayed.

## Configuration & interfaces

| Item | Notes |
| :- | :- |
| `--channels plugin:<name>@<marketplace>` | Space-separated list |
| `--dangerously-load-development-channels plugin:...` or `server:<name>` | Bypasses the allowlist after a confirmation |
| `channelsEnabled`, `allowedChannelPlugins` | Managed; Organization settings UI needs Owner |
| Manifest `channels[]` | `server` (key in `mcpServers`), `displayName`, `userConfig`; strict objects |

Supported plugins: Telegram, Discord, iMessage, and the `fakechat` demo at `http://localhost:8787`. They require Bun. Tokens go to `~/.claude/channels/<name>/.env`, or `TELEGRAM_BOT_TOKEN`, `DISCORD_BOT_TOKEN`.

## Failure modes & edge cases

- `failed` in `/mcp` usually means a server import or dependency error; debug with `claude --debug`.
- A managed `allowedChannelPlugins` that cannot be read admits nothing (fixed behaviour; see changelog text).
- Claude Tag Slack "channels" are unrelated.

## Changes since the snapshot

- v2.1.126: plan-mode tools restored in interactive `--channels` sessions.
- v2.1.128: `--channels` works with Console API keys; `channelsEnabled` required for managed Console orgs.
- v2.1.234: relay limited to registered channels; `false` honoured (docs).

## Open questions

- Default allowlist contents beyond `claude-plugins-official` channel plugins.
- Protocol contract may change during preview.
