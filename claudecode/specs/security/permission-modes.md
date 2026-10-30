# Permission Modes

**Status:** shipped
**Provenance:** both (`default`, `acceptEdits`, `plan`, `dontAsk`, `bypassPermissions` in snapshot; `auto` feature-gated in snapshot; `manual` label post-leak since v2.1.200, 2026-07-03)
**Sources:** docs `permission-modes`, `permissions`, `settings-reference`, `cli-reference`, `headless`, `hipaa-setup`; snapshot `types/permissions.ts`, `utils/permissions/PermissionMode.ts`, `getNextPermissionMode.ts`, `permissions.ts`, `filesystem.ts`; changelog 2.1.89–2.1.314

## Purpose

A permission mode sets the session-wide baseline for which actions need a human decision. Modes sit between permission rules (which match specific calls, see [permission-rules.md](permission-rules.md)) and isolation (which limits what a running command can reach, see [os-sandbox.md](os-sandbox.md)).

## Behaviour

### Mode catalogue

1. The system MUST support these config values: `default`, `acceptEdits`, `plan`, `auto`, `dontAsk`, `bypassPermissions`. `manual` MUST be accepted as an alias for `default` wherever a value is typed or configured.
2. `default` MUST be labelled Manual in the CLI, `--help`, IDE extensions and desktop app. Hooks and SDK integrations see `default`.
3. Baseline outcomes:

| Mode | Runs without asking | Everything else |
|---|---|---|
| `default` | Reads in working directories; built-in read-only commands | Prompt |
| `acceptEdits` | The above, plus file edits and a fixed set of filesystem commands on in-scope paths | Prompt |
| `plan` | Reads and exploration; edits blocked until a plan is approved | Depends on session, see below |
| `auto` | Reads and working-directory edits; other actions after classifier review | Blocked or prompted per [auto-mode.md](auto-mode.md) |
| `dontAsk` | Reads in working directories, read-only commands, calls approved by allow rule or hook | Denied, never prompted |
| `bypassPermissions` | Everything except the fixed exception list | Prompt or denial |

4. Deny rules MUST block in every mode, including `bypassPermissions`. Allow rules have no effect in `bypassPermissions`.
5. Modes are enforced by the client, not the model. Instructions in a prompt or `CLAUDE.md` MUST NOT change what is permitted.

### Actions no mode auto-approves

6. In every mode, including `bypassPermissions`, each of these MUST produce a prompt or a denial:
   - calls matching an explicit ask rule;
   - connector tools an organization set to `ask`, where that setting reaches the session;
   - tools that require user interaction (`AskUserQuestion`, MCP tools marked `requiresUserInteraction`);
   - recognized critical-path removals and commands that cannot be ruled out as such ([shell-command-safety.md](shell-command-safety.md));
   - cross-session messaging safeguards (the `isolatePeerMachines` approval, and holding inbound messages when no `crossSessionInbound` value applies);
   - reads outside working directories by recognized file-reading commands, and unsandboxed retries needing approval, while `permissions.blockReadsOutsideWorkingDirectories` is on.
7. `dontAsk` MUST deny (not prompt) the calls in rule 6 that would otherwise prompt. `AskUserQuestion`, `requiresUserInteraction` MCP tools, network-path reads and org-`ask` connector tools MUST be denied even if allow rules match them.

### Starting mode

8. A new terminal session MUST take its mode from the first that applies: `--permission-mode` or `--dangerously-skip-permissions`; `permissions.defaultMode` by settings precedence; the built-in default.
9. `auto` and `bypassPermissions` MUST NOT take effect as `defaultMode` from `.claude/settings.json` or `.claude/settings.local.json`. A repo-supplied `auto` falls to the built-in default (not to a user-file value); a repo-supplied `bypassPermissions` starts in Manual. Other values apply from any file.
10. Built-in default, first match wins:

| Condition | Mode |
|---|---|
| Any settings file sets `disableAutoMode: "disable"` | `default` |
| `claude -p` or Agent SDK | `default` |
| HIPAA configuration applied and session eligible | `default`, auto still selectable |
| Interactive terminal or VS Code | `auto` |

11. If anything selects `auto` but auto mode is unavailable, the session MUST start in Manual.
12. The first time the built-in default starts a session in auto, a one-time notice MUST be shown (terminal: once at top; VS Code: dismissable card).
13. If user settings set a non-`auto` `defaultMode` and nothing else sets one, sessions keep it. On Pro, Max, Team and sessions that do not fetch feature flags, the client SHOULD ask once whether to change to auto.
14. VS Code starts each conversation from the first of: `claudeCode.initialPermissionMode` (does not accept `auto`); the last picker choice if Manual, Edit automatically or Auto; `permissions.defaultMode` from managed or user settings; the built-in default. It MUST NOT read project files for the starting mode. With `claudeCode.claudeProcessWrapper` set, the last two steps do not apply.
15. Desktop reads the same settings files; a picker choice is remembered per folder and outranks `defaultMode`, except Plan, which is session-only.
16. Cloud sessions honour only `acceptEdits`, `plan`, `default`, `auto` from settings; `bypassPermissions` and `dontAsk` MUST be ignored silently so a checked-in file cannot select them.

### Switching

17. `Shift+Tab` MUST cycle: from `auto` to `default`, then `acceptEdits`, then `plan`, then optional modes with `bypassPermissions` before `auto`. `auto` appears only when available and switching to it needs no confirmation. `dontAsk` is never in the cycle.
18. `bypassPermissions` MUST appear in the cycle only if the session started with it enabled. A session started without it MUST NOT be able to enter it.
19. The footer MUST always show the active mode: `⏸ manual mode on` (grey), `⏵⏵ accept edits on`, `⏸ plan mode on`, `⏵⏵ auto mode on`, `⏵⏵ don't ask on`, `⏵⏵ bypass permissions on`.
20. In Manual and `acceptEdits`, Bash prompts SHOULD offer "Yes, and switch to auto mode" when auto is available. It MUST NOT appear on PowerShell prompts or on prompts forced by an ask rule or hook, since auto would still show those.
21. Screen reader mode MUST announce mode changes, including on plan approval.
22. Web: cloud sessions offer Accept edits, Plan, Auto (Bypass unavailable; "Accept edits" maps to `default` because cloud pre-approves edits). Remote Control offers Manual, Accept edits, Plan, Auto; Bypass MUST NOT be selectable from the app, and the app dropdown MUST track the local mode.

### `acceptEdits`

23. MUST auto-approve file edits and `mkdir`, `touch`, `rm`, `rmdir`, `mv`, `cp`, `sed` for paths inside working directories or `additionalDirectories`. Except for `touch`, prefixes of safe environment variables or process wrappers are tolerated.
24. MUST still prompt for out-of-scope paths, protected-path writes, critical-path removals, `touch` with anything beyond plain paths, and other non-read-only commands. Each path goes through the symlink check, so a write resolving out of scope is not auto-approved.
25. With the PowerShell tool enabled, MUST also auto-approve `Set-Content`, `Add-Content`, `Clear-Content`, `Remove-Item` (and aliases) on in-scope paths under the same limits. Positional arguments that cannot be statically validated MUST prompt.

### `plan`

26. Claude researches and proposes without editing source. Edits MUST stay blocked until a plan is approved, except in the interactive-terminal-with-bypass case below.
27. Shell commands during planning, first match:
    - interactive terminal with bypass available: no classifier and no prompt;
    - auto available and `useAutoModeDuringPlan` on (default): the classifier reviews commands other than critical-path removals;
    - otherwise: commands outside the read-only set prompt, even with sandbox auto-allow.
28. Approval options MUST include: approve and use auto mode (falling back to "auto-accept edits" when auto is unavailable, or to a bypass option when the session started with bypass enabled); approve and manually review edits; keep planning. Approving exits plan mode and switches to the option's mode.
29. `Ctrl+G` MUST open the plan in the editor. `showClearContextOnPlanAccept` adds an option that also clears planning context. Accepting a plan titles an unnamed session.
30. A hook or mod "allow" MUST NOT approve an edit or non-read-only call in plan mode, except `ExitPlanMode`. Hooks' `updatedInput` still applies. Plan-mode blocks MUST hold wherever there is no interactive terminal, including `-p`, SDK and VS Code's chat panel.
31. A one-time note SHOULD appear when plan mode will not ask before most edits or commands because bypass is available.

### `dontAsk`

32. Anything that would prompt MUST auto-deny; the session never waits for input. A mod the user installed can still approve some calls ([permission-rules.md](permission-rules.md)).
33. Allow rules and PreToolUse hooks MUST NOT approve critical-path removals or network-path reads here.

### `bypassPermissions`

34. Skips prompts and safety checks, including protected-path writes, subject to rule 6. The docs direct its use to isolated environments only.
35. Disabled when `permissions.disableBypassPermissionsMode: "disable"` is set: the flag MUST be rejected and agent frontmatter `permissionMode: bypassPermissions` ignored (subagent runs in the parent's mode).
36. `--restricted` sessions MUST refuse this mode.
37. First interactive entry MUST show a warning dialog. Accepting records `skipDangerousModePermissionPrompt: true` in user settings; declining exits. That key is honoured from user, local or managed scope only, so a repository cannot skip the dialog.
38. Background sessions honour acceptance only from user or managed settings. With none recorded, `claude --bg --permission-mode bypassPermissions` MUST be refused. Acceptance found only in local settings starts the session with the request ignored and a notice.
39. On Linux and macOS the mode MUST refuse to start as root or under sudo, except inside a recognized sandbox.
40. Reading another organization's public artifact needs an approval this mode cannot give, so the read MUST fail. PowerShell `Remove-Item` denials still apply.
41. In a `-p` run the few calls that would still prompt are denied.

### Protected paths

42. Writes to protected paths MUST never be auto-approved except in `bypassPermissions` and in interactive plan mode with bypass available. Outcomes:

| Mode | Protected-path write |
|---|---|
| `default`, `acceptEdits` | Prompt |
| `plan` | Allowed with bypass available; else classifier if auto is available; else prompt |
| `auto` | Classifier (not approvable in `--restricted`) |
| `dontAsk` | Denied |
| `bypassPermissions` | Allowed |

43. Allow rules MUST NOT pre-approve protected-path writes; the check runs first. Prompting modes MAY offer a session-scoped option to edit the project's `.claude` folder or `~/.claude`.
44. The set covers: version-control and hook metadata (`.git`, `.config/git`, `.husky`, `.gitconfig`, `.gitmodules`, pre-commit and lefthook configs); editor and devcontainer folders; `.claude` (with carve-outs for Claude's worktrees, session plan files, background scratch dirs, and Markdown in memory directories, the last two unavailable under `--restricted`); shell startup files and `.envrc`; package-manager and build-tool config (`.npmrc`, `.yarnrc*`, `.pnp.*`, `.cargo`, `.mvn`, `.yarn`, bazel and wrapper properties, `bunfig.toml`); tool configs (`.ripgreprc`, `pyrightconfig.json`); `.mcp.json`, `.claude.json`; files passed via `--settings`, `--mcp-config`, `--agents`; `--plugin-dir` directories and `dev-mods/`; targets of symlinked settings files.
45. A write the symlink check resolves to a protected path the request did not name MUST prompt rather than go to the classifier. The local copy of server-managed settings MUST be protected as settings files are.

## Configuration & interfaces

| Interface | Purpose |
|---|---|
| `--permission-mode <mode>` | Start in a mode; overrides settings |
| `--dangerously-skip-permissions` | Same as `--permission-mode bypassPermissions` |
| `--allow-dangerously-skip-permissions` | Add bypass to the cycle without activating it |
| `--permission-prompt-tool <mcp tool>` | Delegate prompts in print mode |
| `--permission-prompts host\|none` | `none`: deny anything that would prompt, without consulting a host (2.1.259) |
| `--restricted`, `CLAUDE_CODE_RESTRICTED=1` | Remove command and code tools and WebFetch, confine file tools, load only managed and `--settings`, refuse bypass (2.1.248) |
| `permissions.defaultMode` | Starting mode |
| `permissions.disableBypassPermissionsMode`, `permissions.disableAutoMode` (or top-level `disableAutoMode`) | `"disable"` removes the mode; any scope |
| `skipDangerousModePermissionPrompt`, `skipAutoPermissionPrompt` | Notice state; user-or-higher scope |
| `useAutoModeDuringPlan`, `showClearContextOnPlanAccept` | Plan behaviour |
| `claudeCode.initialPermissionMode` | VS Code starting mode |
| Agent frontmatter `permissionMode` | Subagent mode (ignored under auto; see [auto-mode.md](auto-mode.md)) |

## Failure modes & edge cases

- `-p` and SDK with no mode: calls needing approval are denied unless an allow rule, hook, `canUseTool` or prompt tool approves. With `--permission-prompts none`, tools needing a person are removed and denials appear as `permission_denied` events and in `permission_denials`.
- `disableAutoMode` delivered to a running auto session from an admin source MUST leave auto mode and show `auto mode disabled by settings`.
- `defaultMode: "auto"` in a project file fails silently to Manual with no error.
- An invalid managed `permissions.defaultMode` reads as `default`; an invalid disable lock reads as its restrictive value.
- Bypass requested by a background session without recorded acceptance shows a specific ignored-at-launch notice.

## Changes since the snapshot

- 2.1.89: auto mode denials surfaced in `/permissions`. 2.1.111: `--enable-auto-mode` removed; auto joins the cycle.
- 2.1.119: `--agent` honours built-in agents' `permissionMode`. 2.1.141: `/bg` preserves the mode. 2.1.143: `--dangerously-skip-permissions` persists across retire and wake; background sessions honour `defaultMode`.
- 2.1.126: bypass now skips protected-path prompts that the snapshot treated as bypass-immune; catastrophic removals remain.
- 2.1.200, 2.1.203: Manual naming and footer badge. 2.1.210: spoken mode changes.
- 2.1.247: "Yes, and switch to auto mode". 2.1.248: `--restricted`. 2.1.257: repo `defaultMode: bypassPermissions` ignored. 2.1.259: `--permission-prompts none`.
- 2.1.283, 2.1.284, 2.1.285, 2.1.302: built-in default moved to auto for interactive sessions; `-p` and SDK returned to `default`.
- 2.1.299: one-time plan-with-bypass note. 2.1.314: file tools ask before editing the local server-managed settings copy.

## Open questions

- Docs give v2.1.283 for auto as the universal interactive default; the changelog scopes 2.1.283 to third-party or telemetry-off sessions and 2.1.284 to every plan. Which release completed it is unclear.
- `bubble` existed as an internal mode in the snapshot; whether it survives is not documented.
- How a "recognized sandbox" is determined for the root check is not specified here and is deliberately left out.
