# Claude in Chrome Integration
**Status:** shipped (generally available since 2.1.198)
**Provenance:** both
**Sources:** docs `chrome.md`, `vs-code.md`, `env-vars.md`, `settings-reference.md`; snapshot `utils/claudeInChrome/`; changelog 2.1.154 to 2.1.314

## Purpose
Connect Claude Code to the Claude in Chrome extension, so Claude can open tabs, read pages and console output, click, type, upload files and record GIFs in the user's real browser with their logged-in state.

## Behaviour

### Availability
1. MUST work with Chrome and Edge, and detect the extension in other Chromium browsers (Brave, Arc, Vivaldi, Opera). MUST NOT be supported in WSL.
2. MUST need extension 1.0.36+, a direct Anthropic plan, and a `/login` sign-in. API keys and `claude setup-token` tokens keep the integration off even with `--chrome`.
3. MUST be unavailable through third-party providers.
4. MUST follow the org's Claude in Chrome admin setting; when off, `--chrome`, `/chrome` and browser tools are unavailable (2.1.260). In HIPAA Enterprise orgs it is off by default and an Owner can enable it. The BAA does not cover data sent to third-party sites this way.
5. Extension and Claude Code MUST be signed in to the same account and organization.

### Enabling
6. `claude --chrome` turns it on. `--no-chrome` turns it off.
7. `/chrome` shows status, permissions, reconnect and browser selection. It works when the panel shows `Status: Enabled` and `Extension: Installed`.
8. **Enabled by default** is a single setting shared by CLI and VS Code (`claudeInChromeDefaultEnabled`). It increases context use as tools and instructions load each session.
9. With it on, VS Code sessions connect at start (2.1.287); otherwise on `@browser`.
10. The "Claude in Chrome extension detected" dialog changes that setting: yes turns it on and connects; no or Esc turns it off and stops offers.
11. Project and local settings MUST NOT turn Chrome on: `CLAUDE_CODE_ENABLE_CFC=1` there is ignored with a warning. A repository must not connect Claude to the browser.
12. `claude` MUST start normally when Chrome isn't running.
13. When the extension is undetected in an interactive session, a "Claude wants to use your browser" prompt MUST appear at most once per session, with Install extension (guided, same-session), Not now, and Don't ask again.
14. Blocking `claude-in-chrome` in `deniedMcpServers`, or deploying `managed-mcp.json` without allowance, turns that prompt off. `allowClaudeInChromeWithManagedMcp` allows it with exclusive managed MCP (2.1.282).

### Multiple browsers
15. With several connected browsers, the user MUST choose (2.1.154). The choice persists when others connect. Browsers are labelled by computer name (2.1.285).

### Tabs
16. Claude opens new tabs, grouped into a Chrome tab group tied to the session.
17. `/clear` closes the group including open pages, unless work surviving the clear still runs (2.1.239). `/resume`, exit, or such a clear closes only a group of empty new tabs.
18. Claude closes tabs it no longer needs (2.1.221).
19. On a login page or CAPTCHA, Claude MUST pause and ask the user.

### Permissions
20. Browser actions MUST go through Claude Code's permission checks, including when telemetry is off (2.1.251). The dialog starts `Claude in Chrome wants to` with an option to allow the site for the session.
21. Site-level permissions are inherited from the extension's settings.
22. In auto mode, a classifier-approved call skips the extension's per-site check, unless permission rules deny a site (2.1.275).
23. In VS Code, prompts appear as cards in chat. All sessions ask before actions on unapproved sites (2.1.296).
24. In plan mode a prompt MUST appear before recording a GIF, opening a tab, or running a shortcut, and for `tabs_context_mcp` with `createIfEmpty` and `browser_batch` with those actions.
25. In Cowork cloud sessions outside auto mode, an approved-site action flagged by the classifier asks instead of refusing, unless managed settings apply (2.1.299).

### Tool behaviour
26. Tools load in one batch (2.1.172) as MCP server `claude-in-chrome`. Calling a tool without the prefix gives an error naming the right one (2.1.284).
27. `browser_batch` times out at 90 seconds (2.1.290).
28. File upload reads the file and sends contents, so it works in remote sessions. Limits: `Read` permission required, 10 MB total per upload, no hard-linked files, and no credential-named paths such as `.env`, `.pem`, `.key`, `.ssh` (2.1.293).
29. Screenshots may be saved to disk with the path reported (`save_to_disk`, 2.1.211).
30. Long page reads stay inline (2.1.268).
31. GIF recordings capture all visible content, including account details.
32. In cloud sessions, when the browser can't be reached, the message MUST say the computer may be asleep, and mention org mismatch (2.1.271, 2.1.293). Claude may continue with alternatives (2.1.292).
33. Sessions created by a Remote Control server default to Chrome off without `--chrome`, per [remote-control.md](remote-control.md).

### Connection
34. Native host and a bridge connection at `bridge.claudeusercontent.com` link the CLI and extension. Network and IP allowlists must allow it.
35. "Reconnect extension" restarts a failed connection (2.1.290). Service workers can idle during long sessions.

## Configuration & interfaces
| Item | Purpose |
|---|---|
| `--chrome`, `--no-chrome` | Per session |
| `/chrome`, `@browser` | CLI and VS Code entry points |
| `claudeInChromeDefaultEnabled` | Default on |
| `CLAUDE_CODE_ENABLE_CFC` | `1` or `0` at start; not from project settings |
| `CLAUDE_CODE_DISABLE_CFC_PROMPT` | Keep tools, drop instructions |
| `allowClaudeInChromeWithManagedMcp` | Managed allowance |

## Failure modes & edge cases
| Error | Meaning |
|---|---|
| "Browser extension is not connected" | Not installed, wrong org, or IP allowlist blocks the bridge |
| "Not detected" | Disabled or absent |
| "No tab available" | Acted before tab ready |
| "Receiving end does not exist" | Idle service worker |
| "No browsers are connected" | Chrome closed, wrong account, or network |

Logging out of the extension to change organization loses its shortcuts and scheduled tasks.

## Changes since the snapshot
- 2.1.154: browser selection. 2.1.169: flag kept across background wake. 2.1.172: batched load. 2.1.198: GA.
- 2.1.211: upload path hardening, `save_to_disk`. 2.1.221: closes tabs. 2.1.239: tab groups on `/clear`.
- 2.1.251: permission checks unified. 2.1.260: admin setting. 2.1.275: auto-mode behaviour.
- 2.1.282: managed MCP allowance. 2.1.285: machine names. 2.1.287, 2.1.296: VS Code behaviour.
- 2.1.290: reconnect restart, 90-second batch. 2.1.293: credential file refusal. 2.1.314: instruction opt-out in VS Code.

## Open questions
- Whole tool list at 2.1.314; docs name only some, such as `tabs_context_mcp` and `browser_batch`.
