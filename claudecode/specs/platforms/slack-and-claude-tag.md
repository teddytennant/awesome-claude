# Slack: Claude Tag and Earlier Claude Code in Slack
**Status:** preview (Claude Tag, public beta); removed in connected workspaces (earlier app, retired for connected workspaces on 2026-10-05, retained for Pro and Max)
**Provenance:** post-leak (Claude Tag changelog entries from v2.1.267, 2026-09-09)
**Sources:** docs `slack.md`, `claude-tag.md` (landing page); `claude.com/docs/claude-tag/concepts/how-it-works.md`, `users/commands.md`, `concepts/for-claude-code-users.md` (fetched because the code docs page is only a landing page); `monitoring-usage.md`, `managed-settings.md`; changelog `[Claude Tag]` entries 2.1.267 to 2.1.314; snapshot `commands/install-slack-app`

## Purpose
Put Claude in Slack. **Claude Tag** runs `@Claude` as the organisation's shared identity with admin-configured per-channel access, on Team and Enterprise. **Claude Code in Slack** is the earlier per-user app, routing mentions to the user's own cloud sessions on Pro and Max.

## Behaviour

### Claude Tag availability
1. MUST be Team and Enterprise on first-party service only. Not on Free, Pro or Max, or third-party deployments. An org pairs its Slack workspace with its Claude org.
2. Slack users don't each need a seat for channels. By default anyone in the paired workspace can tag; an Owner can restrict to org members or, on Enterprise, specific roles.
3. Channel, thread and group DM work MUST bill by usage to the org balance, under a spend limit.
4. One-to-one DMs from a connected member MUST run on that account and seat. The seat must include Claude Code, or on Enterprise be Standard or Usage-Based Chat with Cowork (2.1.285). Unconnected members may bill to the org for a limited time. Owners may disable DMs.
5. ZDR note: retains channel memory and session transcripts.

### Session model
6. A top-level tag is picked up by the channel's own session. Work needing investigation gets a thread bound to its own session.
7. Each thread has a separate ephemeral sandbox, the same infrastructure as cloud sessions, created at start and discarded when idle. The transcript persists at Anthropic.
8. Lifecycle: start, sandbox builds, working loop, result in thread, quiet period. A reply rebuilds the sandbox.
9. A session starts with no repository. Naming a granted repository clones it, and then `CLAUDE.md`, `.claude/CLAUDE.md`, `.claude/rules/*.md` and `.claude/skills/` load. Repo hooks and `.mcp.json` do not.
10. Local `~/.claude`, personal settings, shell environment and local MCP never load. Server-managed settings are not delivered; a self-hosted environment still reads the runner image's managed file.
11. Sessions run in auto mode. Admins pre-approve via auto mode allow rules. Effort is not configurable; default model is per channel, switchable in a thread.
12. Baseline without connections: read thread and channel history including pins, search workspace content, and run code in the sandbox.
13. A channel session is replaced after about an hour without activity or on config change. Claude stops reading top-level messages after about 100 since it last posted, until mentioned. These are approximate defaults.

### Steering and progress
14. Anyone in the channel MUST be able to steer by replying in the thread, without re-mentioning.
15. A working indicator with **Stop** MUST show in channel threads, and a thread title is set (2.1.280). In DMs it reads "is thinking…". Stop keeps the session and posts who stopped it.
16. Longer tasks post a checklist edited in place: capped at 2,000 characters, reposted at most every 15 minutes in busy threads (2.1.274), and not reposted just because of background work (2.1.287).
17. Editing a message sends a note with old and new text. Deleting a reply sends nothing. Deleting the thread's first message closes and archives the session.
18. A mid-thread mention gets a window of the thread, with other bots filtered out.
19. Sandbox-only files don't survive idle.

### Access
20. Access is set by an Owner or Claude Tag admin at org, workspace or channel scope, directly or through bundles. Bundles MAY have attach conditions covering guest or Slack Connect channels (2.1.275).
21. Thread locks skills, plugins and custom instructions at start. Connectors and domain rules are enforced per request, so additions work in running threads.
22. Credentials are held outside the sandbox and added at the network layer.
23. Channels use agent service accounts. One-to-one DMs use the member's connectors and are attributed to them. Personal connectors can be used in a channel for the member's own tasks after allowing.
24. Connector actions needing approval show a private Allow once / Deny card; others see only that it's waiting (2.1.300).
25. "Channels Claude can search" MAY limit Slack search to public channels Claude is in (2.1.283). Search is unavailable in channels with guests.

### Other channels
26. Reading other public channels is allowed except from conversations with guests. Posting is allowed from public channels; from private channels or group DMs it is not; from a one-to-one DM only new top-level posts after **Approve and post**.
27. Posts carry an attribution line. Claude MUST NOT post into Slack Connect or cross-workspace channels. Posting needs membership, and channels with guests need Full access.
28. Claude MAY follow a channel or thread, acting in the asking conversation, including a thread it only read (2.1.288).

### Output and memory
29. Output forms: reply, file or chart, page kept current, hosted page (artifact, with channel-based access). Code work usually becomes a draft PR under the Claude GitHub App. Claude may delete a canvas it created (2.1.299).
30. Each channel has its own notes. Public channels may also save workspace notes, read everywhere. Private channels only add to their own. Public channels no longer recall other public channels' notes (2.1.268). Anyone in the channel can correct entries. Admins with the permission can edit memory files on the Activity page (2.1.296).

### Commands
| Command | Effect |
|---|---|
| `!help` | Lists commands; varies by workspace |
| `!configure` | Link to channel Configure page |
| `!restart` | Archives and starts fresh; thread or channel scope |
| `!status` | Whether Claude is working; muted state |
| `!mute`, `!unmute` | Per thread only; a mention unmutes |
| `!fast [on\|off]` | Fast mode, may switch to Opus; Owner must allow |
| `!fork` | Continues a thread; first message is a source card (2.1.292) |

31. Commands follow `@Claude` immediately. Standalone commands with extra words become ordinary prompts.
32. In Slack Connect only `!help`, `!mute`, `!unmute`, `!restart`, `!fast` work, and external users only `!help`.

### Routines
33. Tag routines run on a schedule, channel watch or repository event with the channel's connections. A run MAY reply in an existing thread (2.1.269), and MAY end with no post if nothing to report (2.1.311). Asking in a thread lists that thread's tasks by default (2.1.281).

### Earlier app
34. MUST need Pro or Max, a workspace not connected to Claude Tag, cloud sessions, connected GitHub, and account link in App Home. Channels only, no DMs.
35. Routing modes: **Code only**, **Code + Chat** with Retry as Code. Claude reads thread or recent channel context, picks a repository, and posts updates.
36. On finish it @mentions the user with **View Session** and **Create PR**. GitHub only; one PR per session.
37. In connected workspaces it replies with a retirement notice. Elsewhere, without Pro or Max, it replies `This workspace isn't set up for Claude Tag yet`, naming `@Claude connect`.

## Configuration & interfaces
`/install-slack-app` opens the OAuth flow. Environments for channels must be org-shared; a personal environment fails sessions. Telemetry reaches Tag sessions through the environment's variables; `app.entrypoint` is `claude-in-slack`, and `user.*` attributes don't identify the tagger. Admin Activity page lists scheduled work, memory files and network events. No admin page exposes individual messages.

## Failure modes & edge cases
- Claude cannot reach a service: ask what it can access; the channel lacks the grant.
- Out of credits: says so (2.1.267). Retry notice names model or rate limits (2.1.312).
- Confirmation cards stay open 30 minutes (2.1.295).
- Deleting messages in Slack doesn't remove them from the transcript.
- Running threads aren't told about config changes.

## Changes since the snapshot
- All of Claude Tag is post-snapshot. Key changes: 2.1.268 memory scoping; 2.1.274 checklist limits; 2.1.275 bundle conditions; 2.1.280 native indicator; 2.1.283 search limit; 2.1.285 DM seats; 2.1.292 `!fork` card; 2.1.296 memory editing; 2.1.300 approval cards; 2.1.302 repo search scale; 2.1.311, 2.1.312; 2.1.314 API docs link.

## Open questions
- Claude Tag API surface, connector catalog and federated access are in documentation outside this corpus and are not specified here.
- First release of Claude Tag; changelog tagging starts at 2.1.267 but the feature may predate it.
- `!feedback` exact form.
