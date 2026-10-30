# Computer Use
**Status:** preview (research preview in CLI on macOS; Desktop on macOS and Windows)
**Provenance:** both (snapshot `utils/computerUse/`, gated; public since then)
**Sources:** docs `computer-use.md`, `desktop.md`; snapshot `utils/computerUse/`; changelog 2.1.243, 2.1.307

## Purpose
Let Claude see the screen and operate native apps, simulators and GUI-only tools, through a built-in MCP server on the user's real desktop. It is the slowest and broadest option, reserved for things nothing else can reach.

## Behaviour

### Availability
1. CLI MUST be macOS only, on Pro or Max, not Team or Enterprise, and interactive only (not `-p`).
2. Desktop MUST work on macOS and Windows, Pro or Max. It is not in the Linux app.
3. Tool order: connector or MCP server, then Bash, then Claude in Chrome, then (Desktop) iOS Simulator pane, then computer use.

### Enabling
4. CLI: `computer-use` is a built-in MCP server, off by default, enabled per project in `/mcp`.
5. Desktop: **Enable computer use** under Settings, in This computer > System or Capabilities. Windows takes effect immediately.
6. macOS MUST need Accessibility and Screen Recording. Prompts link to System Settings; a restart may be needed after Screen Recording.

### App access
7. Enabling MUST NOT grant any app. First use of each app in a session prompts with apps requested, extra permissions (such as clipboard), and how many apps will be hidden. Choices: **Allow for this session** or **Deny**.
8. Approvals last the session, or 30 minutes in Dispatch-spawned sessions.
9. Fixed tiers:

| Tier | Abilities | Apps |
|---|---|---|
| View only | Screenshots | Browsers, trading platforms |
| Click only | Click, scroll | Terminals, IDEs |
| Full | Click, type, drag, shortcuts | Others |

10. Warnings MUST appear for terminals and IDEs (shell access), Finder (any file), and System Settings. These apps aren't blocked.
11. Clicking the desktop, Dock or a Finder window MUST require granting Finder (2.1.243).

### Screen handling
12. Only one session at a time MUST use the computer. A lock is taken at first action, held until session exit, and a second session errors naming the holder.
13. Other apps MUST be hidden during control and restored at turn end. The terminal stays visible and is excluded from screenshots.
14. Screenshots MUST be downscaled automatically, preserving aspect ratio, with no setting. Example: 3456×2234 to roughly 1372×887.
15. A notification MUST appear on first use each turn, and another on finish. `Esc` anywhere or `Ctrl+C` in the terminal MUST abort immediately, stop Claude, and unhide apps. The lock stays held.
16. Claude checks actions and flags potential prompt injection from on-screen content.
17. A spent WebSearch budget notice also tells Claude not to query search engines via computer use (2.1.307).

### Desktop differences
18. Desktop has a Denied apps list and an **Unhide apps when Claude finishes** toggle, and Dispatch sessions can use it. CLI has neither option, and always unhides.
19. Denied apps can't be used directly but may be affected indirectly.

## Configuration & interfaces
Enable path as above. Snapshot sub-features (pixel validation, multi-line paste, mouse animation, hide before action, auto target display, clipboard guard) were remotely configured defaults; current state is unknown. No user settings for screenshot size.

## Failure modes & edge cases
- "Computer use is in use by another Claude session": exit that session.
- Repeated macOS permission prompts.
- `computer-use` absent from `/mcp`: platform, plan, or interactive requirements unmet.
- Sandboxing does not apply; the trust boundary differs from the Bash tool.

## Changes since the snapshot
- 2.1.243: Finder must be granted for desktop and Dock clicks.
- 2.1.307: WebSearch budget notice.
- Public availability is post-snapshot. Exact version not identified in the changelog topics.

## Open questions
- Which apps fall into each tier beyond categories.
- Whether Team and Enterprise access is planned.
