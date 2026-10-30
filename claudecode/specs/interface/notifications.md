# Notifications

**Status:** shipped
**Provenance:** both
**Sources:** docs `terminal-config`, `hooks`, `accessibility`, `remote-control`, `settings-reference`, `interactive-mode`; snapshot `services/notifier.ts`, `ink/useTerminalNotification.ts`, `context/notifications.tsx`, `components/PromptInput/Notifications.tsx`; changelog 2.1.181 through 2.1.295

## Purpose

Tell the user when Claude needs them or has finished, through OS or terminal alerts, hooks, phone pushes and in-app toasts.

## Behaviour

### Desktop and terminal channel

1. When Claude finishes or waits on a prompt, and the user appears away, a notification event fires.
2. `preferredNotifChannel` selects delivery:

| Value | Delivery |
|---|---|
| `auto` (default) | iTerm2, Ghostty, Kitty: desktop notification. Terminal.app: bell only when audible bell is off in the front window's profile. Others: nothing |
| `terminal_bell` | BEL anywhere |
| `iterm2` | iTerm2 notification |
| `iterm2_with_bell` | iTerm2 notification and BEL |
| `kitty` | Kitty notification |
| `ghostty` | Ghostty notification |
| `notifications_disabled` | No alert |

3. Escape sequences pass through multiplexers. Inside tmux this needs `allow-passthrough`.
4. Desktop notifications reach the local machine over SSH, for terminals that forward them. iTerm2 needs Notification Center Alerts and escape-sequence alerts turned on.
5. Terminal.app bell state is read from the current profile (snapshot uses `osascript` and `defaults`).
6. `/terminal-setup` in Terminal.app turns off audible bell, except in screen reader mode.

### Hook event

7. `Notification` hooks MUST run whatever the channel, including `notifications_disabled`, and alongside it.
8. Matchers:

| Matcher | Fires when |
|---|---|
| `permission_prompt` | A prompt, or sandbox network request, has waited about 6 s |
| `idle_prompt` | Claude finished about 60 s ago and nothing typed |
| `auth_success` | Authentication completes |
| `elicitation_dialog` | MCP form idle about 6 s |
| `elicitation_url_dialog` | MCP URL ask idle about 6 s |
| `elicitation_complete` | URL elicitation done |
| `elicitation_response` | Elicitation response sent |
| `agent_needs_input` | A background session waits, with agent view open; also teammate setup and classifier-charge notices |
| `agent_completed` | A background session ends, with agent view open |
| `quota_auto_resume_fired` | Task continued after a usage limit |
| `quota_auto_resume_stale` | Limit reset during long sleep; waits for Enter |
| `quota_auto_resume_disabled` | Automatic continue ended |

`idle_prompt` MUST NOT fire while background agents run (2.1.288). A queued MCP or permission ask under another dialog gets the same delay as a visible one (2.1.257).

### Phone push

9. While Remote Control is connected: `agentPushNotifEnabled` (**Push when Claude decides**, default false) and `inputNeededNotifEnabled` (**Push when actions required**, default false).
10. Pushes are skipped while typing in or focused on the connected terminal. `CLAUDE_CLIENT_PRESENCE_FILE` extends that to any time a marker file exists (2.1.181).
11. `/config` warns **No mobile registered** when no device is registered.
12. Sessions under `claude remote-control` follow the account-saved value.

### In-app toasts

13. Snapshot model: a queue with priority `low`, `medium`, `high`, `immediate`; default timeout 8 seconds; `invalidates` keys; `fold` merges same-key items.
14. Toasts MUST appear in the status area, not above the prompt, for items such as the Feature of the Week claim (2.1.157).
15. Toasts MUST NOT wait unseen behind the `/diff` panel or dialog (2.1.296).
16. An organisation's mod toasts show ahead of other mods' (2.1.295).
17. `$.ui.notify` lets a mod raise a native notification through this channel and reports which channel sent it (2.1.295).

### Other attention signals

18. Tab status: see OSC 7501 and progress in [terminal-renderer-and-layout.md](terminal-renderer-and-layout.md).
19. `claude agents` tab title shows the awaiting-input count (2.1.145).
20. Screen reader mode rings BEL at reply end, when a dialog needs an answer, and when a tool over 5 seconds finishes.
21. Skipped pushes, recap on return, and usage-limit lines are covered in their own topics.

## Configuration & interfaces

| Key | Scope |
|---|---|
| `preferredNotifChannel` | Any file; old `~/.claude.json` value honoured; `/config` **Local notifications** |
| `agentPushNotifEnabled` | Any file; saved to account from `/config` |
| `inputNeededNotifEnabled` | Any file |
| `CLAUDE_CLIENT_PRESENCE_FILE` | Env |
| `hooks.Notification` | Settings |

## Failure modes & edge cases

- Warp and the VS Code terminal receive no desktop notification under `auto`; use a hook or `terminal_bell`.
- Apple Terminal needs Audible bell on to hear `terminal_bell`.
- The OS must allow the terminal to notify.
- `Notification` hooks fire for permission prompts under Claude Desktop and VS Code hosts (2.1.233).

## Changes since the snapshot

- 2.1.157: Feature of the Week claim moved to a notification.
- 2.1.181: presence file.
- 2.1.295: OSC 7501; organisation toast priority.
- New `Notification` matchers for agents and quota auto-resume; docs give no single version.
- Snapshot config label for this row already depended on a push gate; docs now show public push settings.

## Open questions

- How "appears away" is computed, beyond the listed delays.
- Whether the toast queue model remains.
- Whether `iterm2_with_bell` is shown in `/config`.
