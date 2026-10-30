# Onboarding, tips and /powerup

**Status:** shipped
**Provenance:** both
**Sources:** docs `quickstart`, `settings-reference`, `terminal-config`, `commands`, `common-workflows`, `whats-new__2026-w14`, `errors`, `debug-your-config`; snapshot `components/Onboarding.tsx`, `components/LogoV2/`, `components/TrustDialog/`, `projectOnboardingState.ts`, `services/tips/`; changelog 2.1.90 through 2.1.311

## Purpose

Get a new user signed in and safe on first run, then surface features gradually through project hints, startup notices, spinner tips and interactive lessons.

## Behaviour

### First run

1. Snapshot step order: preflight connectivity, theme, API key approval (if one is found) or OAuth, security notes, terminal setup (offered only where useful). Steps depend on auth mode.
2. Preflight checks reach `api.anthropic.com` and `platform.claude.com` before sign-in, and a failure reports what to do.
3. The theme step shares the picker and plugin `config.set` rules.
4. The terminal setup step runs `/terminal-setup` when accepted.
5. Server-managed settings: at sign-in during first run, the app waits up to five seconds for them.
6. A clean `CLAUDE_CONFIG_DIR` repeats first-run screens.
7. First-time Bedrock and Vertex users can reach their wizards from the login screen.
8. Fullscreen may be offered at startup; see [fullscreen-mode-and-tui.md](fullscreen-mode-and-tui.md).

### Trust

9. Interactive runs show a workspace trust dialog in an untrusted folder, naming the repository root the grant covers (2.1.218). Home-directory trust is never saved.
10. `claude agents`, `--bg`, `claude rc` and `ultrareview` also check trust (2.1.225, 2.1.284, 2.1.309). `-p` skips the dialog.

### Project hints

11. Snapshot model: a new project may show steps such as creating an app or running `/init`, up to four views, until complete.
12. `/init` writes `CLAUDE.md`. `CLAUDE_CODE_NEW_INIT=1` runs an interactive flow, and it offers `/import` when other agents are configured.

### Startup banner and notices

13. The logo shows version, model and cwd (`CLAUDE_CODE_HIDE_CWD=1` hides cwd), with the Clawd mascot.
14. Notices sit under the logo. Overflow reads `N more notices hidden` (2.1.277).
15. Noise has been moved out of startup: skill truncation (2.1.144), setup issues (2.1.183), command missing (2.1.203), `/ide` hint (2.1.157), sandbox banner (2.1.157), Chrome and marketplace messages (2.1.162). They are available through `/doctor` or `/status`.
16. `companyAnnouncements` shows organisation messages at startup.
17. Launch-prompt warnings for deep links stay pinned below the input until acted on (2.1.162).
18. Permission-rule warnings show once per user until the rule changes (2.1.311).

### Spinner tips

19. While Claude works, the spinner line rotates tips. `spinnerTipsEnabled: false` hides all, including custom ones.
20. Snapshot selection: from relevant tips, pick the one unseen for the most sessions, then record it. Tips have a `cooldownSessions`.
21. Tips are contextual. Post-snapshot additions include `claude agents` (2.1.169), `/web-setup` (2.1.243), `/focus` (2.1.269, reworded 2.1.292), desktop app for third-party users (2.1.271), Explanatory style (2.1.311).
22. A tip for custom subagents was removed in 2.1.232. A tip MUST be suppressed where its command is disabled, and repository-host-specific tips respect the remote (2.1.233).
23. The status page link replaces the tip when the API is overloaded (2.1.198).

`spinnerTipsOverride`:

| Field | Meaning |
|---|---|
| `tips` | Strings, or `{id, text, cooldownSessions, priority}` |
| `tipsFile` | Absolute or `~/` path, JSON array or `{tips}`, up to 256 KB, read once per process |
| `label` | Prefix |
| `excludeDefault` | Hide built-ins |

Rules: `id` up to 64 characters from letters, digits, `.`, `_`, `-`; first of duplicates wins; `text` one line up to 500 characters, sanitised; `cooldownSessions` 0 to 1000; `priority` -10 to 10, higher first among equally unseen tips; at most 200 tips; invalid entries are dropped with a debug warning. Project and local settings contribute plain strings only (2.1.247).

### Prompt-level nudges

24. Example prompts, prompt suggestions and recaps are in [prompt-input-and-editing.md](prompt-input-and-editing.md).
25. A Bash permission prompt can offer "Yes, and switch to auto mode" (2.1.247).
26. "You should know" notes are an off-by-default built-in mod (2.1.287).

### /powerup

27. `/powerup` opens interactive lessons with animated demos in the terminal, teaching one feature at a time (2.1.90).
28. Content changes with releases. A subagent nudge was removed from the tour in 2.1.232.

### Help surfaces

29. `/help` shows commands and tabs. `?` on an empty prompt toggles shortcuts. Claude can answer questions about itself from documentation.
30. Upsells such as `/passes`, the desktop app and the guest-pass notice appear only to eligible accounts.
31. A session quality survey appears with probability `feedbackSurveyRate` (0 to 1) when a session is eligible. `0` stops it.

## Configuration & interfaces

| Key | Effect |
|---|---|
| `spinnerTipsEnabled`, `spinnerTipsOverride` | Tips |
| `companyAnnouncements` | Startup text |
| `CLAUDE_CODE_HIDE_CWD` | Logo |
| `CLAUDE_CODE_NEW_INIT` | `/init` flow |
| `feedbackSurveyRate` | Survey rate |
| `CLAUDE_CONFIG_DIR` | Config home |

## Failure modes & edge cases

- Tips and `/help` MUST NOT suggest `/feedback` where policy disables it.
- Reminder tips about push notifications stay hidden if Remote Control or those toggles are unavailable.
- A trust failure in a headless terminal reports `Workspace not trusted` rather than prompting.

## Changes since the snapshot

- 2.1.90: `/powerup`.
- 2.1.121: release-notes splash lost Recent Activity.
- 2.1.247: organisation tips. 2.1.277: notice overflow wording.
- Many startup items moved to `/doctor` and `/status` (see item 15).

## Open questions

- Current first-run order.
- `/powerup` lesson list, progress storage, and whether it has arguments.
- Whether the project-hint model and four-view limit remain.
- Tip registry contents today; the snapshot had 48 entries.
