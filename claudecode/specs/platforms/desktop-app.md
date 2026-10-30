# Claude Desktop: Code Tab
**Status:** shipped (Linux build is beta)
**Provenance:** both (`/desktop` handoff in snapshot; app itself is outside the CLI source)
**Sources:** docs `desktop.md`, `desktop-quickstart.md`, `desktop-wsl.md`, `desktop-linux.md`, `platforms.md`; snapshot `commands/desktop`, `utils/desktopDeepLink.ts`; changelog entries naming Claude Desktop

## Purpose
The Code tab of the Claude desktop app is a graphical host for Claude Code sessions, beside Chat and Cowork. It runs sessions locally, in WSL, over SSH, or in the cloud, and adds pane layouts, diff review, a browser pane, PR monitoring and session orchestration. The app source is not in the snapshot.

## Behaviour

### Platforms
1. The app MUST ship for macOS (universal), Windows x64 and ARM64, and Linux (beta, Ubuntu 22.04+ or Debian 12+, x86_64 or arm64).
2. Linux MUST be delivered through Anthropic's apt repository, or a `.deb` from its pool. The `.deb` carries the signing key and registers the repository unless `/etc/default/claude-desktop` sets `CLAUDE_DESKTOP_ADD_REPO="false"`.
3. The Linux app MUST NOT update itself; updates arrive through system packages. Other distros use the CLI instead.
4. Linux Cowork runs tasks in a QEMU/KVM VM and needs hardware virtualization, QEMU with UEFI firmware plus `virtiofsd`, and `kvm` group membership (for `/dev/vhost-vsock`). Requirements are checked once at launch.
5. Computer use MUST NOT be offered on Linux at this time.

### Sessions and layout
6. Each session has its own history and project folder. The sidebar lists sessions and runs several in parallel, each optionally in a worktree.
7. Panes (chat, diff, browser, terminal, file, plan, tasks, subagent, and iOS Simulator on macOS) MUST be draggable, resizable, and able to pop out into their own windows. This needs Desktop v1.2581.0+.
8. The current layout (Desktop v2.37337.0+, or v3.1623.0+ / v4.29.0+ for third-party local / organization-hosted setups) places the environment selector under the prompt box. The earlier layout lacks the session details panel and saved environments.
9. `claude --desktop` MUST open the app on the current directory, or on a session with `--continue` or `--resume <id>`, without starting a terminal session. `/desktop` hands off an existing session.

### Permission modes
10. Modes: Manual (`default`), Accept edits, Plan, Auto, Bypass permissions. `dontAsk` is CLI-only.
11. A mode picked in the selector MUST be remembered per folder and beat `permissions.defaultMode`, except Plan, which is session-only.
12. Bypass permissions needs a Settings toggle on Pro and Max, and organization policy on Team and Enterprise.
13. Cloud sessions MUST offer only Accept edits, Plan and Auto. Bypass is unavailable there, including self-hosted environments.
14. In bypass mode the dangerous `rm`/`rmdir` prompt denies at once with a rewrite hint, so unattended sessions keep going.

### Browser pane
15. Claude MUST be able to start a dev server, open it in the pane, and verify changes by screenshots, DOM inspection and interaction. Auto-verify runs after edits by default. Configuration lives in `.claude/launch.json`.
16. The pane MUST be a tabbed browser supporting sign-in, including popup OAuth, with **Keep cookies** and **Clear browsing data** controls.
17. On external pages, safety classifiers MUST review write actions in every permission mode; a flag yields a permission prompt regardless of mode.
18. Outside Auto and Bypass, a domain allowlist check MUST run before Claude navigates to a new site.
19. In SSH sessions Claude has no pane tools; users forward ports themselves.
20. First external link click asks where links open. Cmd/Ctrl-click always uses the default browser.

### Pull requests
21. An open PR MUST show CI status in the Changes card. PR monitoring needs `gh` installed and authenticated; Desktop prompts to install except over SSH.
22. **Auto-fix** addresses failing checks. Locally it also addresses review comments from others, when the author is the owner, an org member, a collaborator or a GitHub App.
23. **Merge when ready** enables GitHub auto-merge, requesting squash locally unless the base uses a merge queue. It is disabled over SSH and WSL.
24. Sessions MAY auto-archive on merge or close.

### Cross-session work
25. Claude MUST be able to list, read, message, rename and archive Code tab sessions the app itself runs (local, SSH, WSL). It sees neither cloud nor CLI or extension sessions, never lists the asking session, defaults to the 20 most recently active, and skips archived unless asked.
26. Messages arrive as cards labelled with the sender and a link back, are held until current work ends, and cannot be delivered to archived sessions.
27. Archiving needs an approval card, except in Auto and Bypass.
28. Each message MUST be checked against the receiver's inbound controls. `crossSessionInbound: refuse` drops it and the refusal is reported to the app.
29. Claude's suggested tasks MUST render as cards with Start, Do it here, Options and Start all, or a Suggested task card in cloud sessions and the earlier layout.

### Environments
30. Saved environments pair a target with a folder. Variables for local sessions live in a saved local environment. `PATH` on Windows comes from system variables, since PowerShell profiles are not read.
31. SSH MUST support Linux, macOS and Windows remotes. Desktop installs a helper and Claude Code under `~/.claude/remote/` on first connect, uploading the binary if the remote can't download it.
32. SSH remote needs: x86_64 or arm64, glibc 2.17+ or musl, an SFTP subsystem, a non-`noexec` home, about 1 GB of disk per user, and a shell that runs commands sent over SSH.
33. Proxy and CA variables for Linux remotes MUST go in `env` of the remote `~/.claude/settings.json`, because login profile files do not reach SSH sessions. `SSL_CERT_FILE` there is not trusted; use `NODE_EXTRA_CA_CERTS`.
34. With `MaxSessions 1`, use Desktop v3.1623.0+ on macOS or Linux, or the OpenSSH client on Windows. Desktop logs in at least twice per connect.
35. Cloud sessions continue after the app closes, and support multiple repositories.
36. **Open in** MUST move a session to Cloud with the conversation as a summary, or open the folder in an editor. SSH and WSL sessions cannot move this way.

### WSL
37. On Windows, the Code tab MUST run sessions inside a WSL 2 distribution with Claude, tools and git executing there on Linux paths. WSL 1 is unsupported and `git` must exist in the distro.
38. Workspace trust MUST be per distribution and folder.
39. Picking a `\\wsl.localhost\...` folder MUST reopen inside that distribution.
40. Plugins are unavailable, the file pane is view-only, and attachments may be images only. Terminal and connectors roll out separately on Claude accounts and are absent on third-party providers.
41. "Open in editor" opens VS Code through Remote - WSL. WSL may be blocked on managed devices.

### Other integrations
42. Dispatch (in Cowork) MAY route development tasks to Code sessions, which appear in the sidebar.
43. `/config` opens Settings. Commands with no argument form reply `isn't available in this environment`. Agent teams are unavailable; dynamic workflows run instead.
44. A local session appears on other devices once Remote Control connects it. The setting **Connect new sessions to Remote Control**, once saved, overrides `remoteControlAtStartup`. `disableRemoteControl: true` stops all local connections. Archiving in Desktop also archives the Remote Control copy.
45. Idle compaction summarises a 200K+ token idle conversation (2.1.314).
46. `/advisor` has a text form in Desktop (2.1.260).

## Configuration & interfaces

### Managed settings
| Key | Effect | Source |
|---|---|---|
| `permissions.disableBypassPermissionsMode` | `"disable"` | any; managed prevents override |
| `disableAutoMode` | `"disable"`; also under `permissions` | any |
| `autoMode` | Classifier trust and block customisation | |
| `browserExternalPageTools` | `"disabled"` blocks Claude's tools on external pages | |
| `disableBrowserExternalNavigation` | `true` blocks external navigation for all | |
| `disableMobileSimulatorTools` | `true` removes Claude's simulator tools | |
| `sshConfigs` | Preconfigured SSH connections | |
| `sshHostCommands` | Host from a command; Desktop v3.6556.0+ | file or MDM only |
| `sshHostAllowlist` | Hostname patterns | managed only |
| `disableDesktopLocalSessions` | `true` turns off on-device sessions | managed only |
| `disableSshSavedPasswords` | Stops saved password use; does not delete | managed only |
| `managedMcpServers` | MCP push | 3P deployments only |

### Where settings apply
| Session | Source of managed settings |
|---|---|
| Local | Disk file; server-managed on eligible login |
| Cloud | Server-managed; self-hosted also reads file in runner image |
| SSH | Remote host file. Desktop reads `sshConfigs`, `sshHostAllowlist`, `disableSshSavedPasswords`, `disableDesktopLocalSessions` locally |
| Cowork | Never fetches admin console settings; reads machine policy |

Connectors are delivered directly by the app in local and SSH sessions, and neither MCP settings nor `managed-mcp.json` reach them.

### Device policy
macOS domain `com.anthropic.claudefordesktop`; Windows registry `SOFTWARE\Policies\Claude`; Linux `/etc/claude-desktop/managed-settings.json` (root-owned, refused if writable by others, separate from Claude Code's managed file).

Admin console toggles: Desktop, Cloud sessions, Remote Control. In HIPAA-enabled Enterprise orgs Desktop is off by default and can be turned on by an Owner, while Cloud sessions and Remote Control cannot.

Code tab telemetry needs `CLAUDE_CODE_ENABLE_TELEMETRY` and `OTEL_*` in managed `env`; the Cowork OTel form does not apply to it.

## Failure modes & edge cases
- `Error 403: Forbidden` in the Code tab: sign out and back in, verify a paid subscription, and fully quit the app if the CLI works.
- Local entry greyed out "Disabled by your organization"; saved local environments error on selection.
- SSH host key mismatch refuses the connection. On Windows without an OpenSSH client some keys are refused.
- A proxy variable set in `~/.zshenv` or `/etc/environment` on a remote beats the one in settings.
- SSH tasks can stop when the sign-in expires while Desktop is disconnected.
- Since 2.1.304 exported shell variables reach unsandboxed Bash commands on macOS and Linux.
- One-time code logins with `MaxSessions 1` break `!` commands.

## Changes since the snapshot
- 2.1.234: inbound checks for messages from the desktop surface.
- 2.1.260: text `/advisor`. 2.1.285: `claude --desktop`.
- 2.1.288: no background command limit in Desktop.
- 2.1.304: exported variables reach commands.
- 2.1.314: idle compaction.
- App-side, unversioned here: Linux beta, WSL sessions, panes, iOS Simulator, current layout, Dispatch.

## Open questions
- Which plans and rollout states gate WSL terminal and connectors.
- Exact Desktop version for WSL support.
- Whether Windows ARM64 has feature gaps.
