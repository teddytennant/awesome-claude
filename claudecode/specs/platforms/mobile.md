# Claude Code on Mobile
**Status:** shipped
**Provenance:** both (`/mobile` in snapshot; Code tab behaviours post-leak)
**Sources:** docs `mobile.md`, `remote-control.md`, `claude-code-on-the-web.md`; snapshot `commands/mobile`; changelog 2.1.110, 2.1.225

## Purpose
The Claude app for iOS, iPadOS and Android is a client for Claude Code sessions. No code runs on the phone, and there is no separate Claude Code app.

## Behaviour
1. The **Code** tab MUST reach cloud sessions, projects, and Remote Control sessions. Dispatch is a task messaged in the app, needing Pro or Max.
2. A claude.ai account is required; Console API keys and third-party providers cannot use these features.
3. `/mobile`, `/ios` and `/android` MUST show a QR for claude.ai/mobile, which opens the right store.
4. `claude.ai/code/new` opens a new Code session in the app.
5. Cloud sessions from the app MUST pick a repository and branch and continue after the phone sleeps. Claude MAY be told to watch a PR.
6. Remote Control MUST be reachable by QR or the session list.
7. Photos MUST reach Claude directly and also be saved under `~/.claude/uploads/`; other files download and arrive as `@` references.
8. Push notifications per [remote-control.md](remote-control.md). Dispatch sends its own notifications.
9. From mobile, `/config` takes `key=value` or lists keys, `/mcp` returns a text summary, and `/model` and `/effort` take arguments.
10. Mods can render trees with Markdown up to 48 rows above the question dialog in mobile apps (2.1.301).
11. Permission modes offered: cloud sessions have Accept edits, Plan and Auto; Remote Control has Manual, Accept edits, Plan and Auto. Bypass MUST NOT be selectable from the app.
12. Dispatch is unavailable on Team and Enterprise.
13. Artifact pages paint the band above a sticky header so scrolled text doesn't show there in mobile apps (2.1.301).

### Surface comparison

| Feature | Connects to | Use when |
|---|---|---|
| Cloud sessions | Cloud session | Repo on GitHub; work must outlive the phone |
| Projects | Coordinating conversation with threads | A stream of related work |
| Remote Control | Session on the user's machine | Needs local files, tools or MCP |
| Dispatch | Desktop app | Message a task and let Dispatch route it |

Remote Control and Dispatch need the machine on, with Claude Code or Desktop running. A task started on one device stays available on others. On iPad the same iOS app is used.

## Failure modes & edge cases
- Code tab missing: plan or org may not include it.
- `No mobile registered` in `/config`: open the app to refresh its push token.
- iOS Focus modes and Android battery optimization can delay pushes.
- Machine sleep pauses Remote Control until it wakes.

## Changes since the snapshot
- 2.1.110: push tool. 2.1.225: direct photos. 2.1.301: mod and artifact rendering.

## Open questions
- Platform-level differences between iOS and Android are unstated.
