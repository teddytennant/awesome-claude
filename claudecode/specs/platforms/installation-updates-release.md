# Installation, Update Channels and Release Mechanics
**Status:** shipped
**Provenance:** both (`utils/nativeInstaller/`, `utils/autoUpdater` in snapshot)
**Sources:** docs `setup.md`, `troubleshoot-install.md`, `settings-reference.md`, `env-vars.md`; snapshot `utils/nativeInstaller/`; changelog 2.1.92 to 2.1.309

## Purpose
Define how Claude Code reaches a machine, how it stays current, and how organisations constrain versions.

## Behaviour

### Requirements
1. Platforms: macOS 13.0+, Windows 10 1809+ or Server 2019+, Ubuntu 20.04+, Debian 10+, Alpine 3.19+. 4 GB+ RAM, x64 or ARM64. Bash, Zsh, PowerShell or CMD.
2. 32-bit Windows is unsupported. WSL 2 supports sandboxing; WSL 1 and native Windows don't.
3. Git for Windows is recommended on Windows. Without it, PowerShell acts as the shell tool.
4. Musl systems need `bash` and `curl` for install, and `libgcc`, `libstdc++` and `ripgrep` at runtime, with `USE_BUILTIN_RIPGREP=0`.

### Channels of distribution
| Method | Auto-update | Channel choice |
|---|---|---|
| Native installer (`install.sh`, PowerShell, CMD) | Yes | `autoUpdatesChannel` or install arg |
| Homebrew | Opt-in | `claude-code` stable, `claude-code@latest` latest |
| WinGet | Opt-in | |
| apt, dnf, apk | No | By repository |
| npm `@anthropic-ai/claude-code` | Yes, if writable | Setting |

5. Since 2.1.113 the CLI spawns a native binary via a per-platform optional dependency, rather than bundled JavaScript. The npm package needs Node 22+ only for install tooling; `claude` itself doesn't invoke Node.
6. npm platforms: `darwin-arm64`, `darwin-x64`, `linux-x64`, `linux-arm64`, `linux-x64-musl`, `linux-arm64-musl`, `win32-x64`, `win32-arm64`. Optional dependencies must be allowed. `sudo` installs break self-update.
7. The VS Code extension bundles a private copy; JetBrains needs the CLI installed.
8. The native installer accepts `latest`, `stable`, or an exact version, and the channel chosen becomes the default.
9. Linux repositories are signed with the Claude Code release key, each with `stable` and `latest`. Docs give a key fingerprint for manual verification.
10. Each release publishes a `manifest.json` with SHA256 checksums per platform binary. Release verification failures are a documented error.
11. Binary is zstd-compressed since 2.1.243, about 75 MB instead of 340 MB on Linux x64, and about 5 MB smaller in 2.1.251.

### Native layout
12. On macOS and Linux, the launcher `~/.local/bin/claude` MUST be a symlink into `~/.local/share/claude/versions/`. On Windows, `%USERPROFILE%\.local\bin\claude.exe`.
13. A custom launcher MUST be left alone. New versions still install, every version is kept, and `claude doctor` reports it. Removing it and running `claude update` restores management.
14. Cleanup keeps the launcher's version, versions in use on the machine, and the two newest, deleting others.
15. Snapshot: per-version locks are held for the process lifetime, PID-based with liveness checks, with an mtime fallback. Multi-process safety uses locks during install and symlink update.
16. `~/.claude/local/` is a legacy local npm install.
17. Network storage: a running session reads the binary continually, so truncation gives a `Bus error`. Install locally, keep each version in its own directory, delete only when no machine runs it, and set `DISABLE_UPDATES`.

### Updating
18. Update checks MUST run on startup and periodically, in the background, taking effect on next start. The startup check runs about 10 seconds after launch (2.1.238).
19. `claude update` announces the target before downloading (2.1.166), and reports `Successfully updated from <old> to version <new>`, or `Claude Code is up to date (<version>)`. Package-managed installs report `Claude is up to date!`, or update through the package manager.
20. The updater MUST retry transient network failures and report error categories and OS codes (2.1.147). Verification waits out endpoint-security scanning (2.1.162).
21. Downloads retry on connection loss or stall up to 3 attempts. A 10-minute total deadline fails with `Download timed out: exceeded the total deadline`, without retry.
22. `claude doctor` shows the last update attempt (2.1.153). A failure shows `Auto-update failed · Run claude doctor` in the footer.
23. Windows failed updates restore the original executable.
24. `CLAUDE_CODE_PACKAGE_MANAGER_AUTO_UPDATE=1` runs Homebrew or WinGet upgrades in the background, and prompts to restart (2.1.129). WinGet may fail while running because of file locks.
25. Notifications may precede package availability; retry later.
26. A near-miss subcommand such as `claude udpate` prints a suggestion and exits (2.1.111).

### Channels and pins
27. `autoUpdatesChannel`: `latest` (default) or `stable`, typically a week old, skipping major regressions. A new model may need `latest`.
28. `minimumVersion` is a floor for updates. Switching to `stable` in `/config` offers staying (sets the floor) or downgrading; switching back clears it.
29. `requiredMinimumVersion` and `requiredMaximumVersion` (managed, 2.1.163) refuse to start outside a range, directing to an approved version. Updates respect the ceiling.
30. Managed `autoUpdatesChannel` enforces a channel.

### Disabling
31. `DISABLE_AUTOUPDATER=1` stops background checks; `claude update` still works. `claude doctor` shows `disabled (set by env: DISABLE_AUTOUPDATER)`.
32. `DISABLE_UPDATES=1` blocks all paths, including `claude update` and `claude install` (2.1.118).
33. `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1` also disables auto-updates.
34. `FORCE_AUTOUPDATE_PLUGINS=1` keeps plugin updates when binary updates are off.

### Other commands
35. `claude doctor` prints read-only install and settings diagnostics without a session. `claude install [target]` installs the native build. `/release-notes` shows history.
36. Uninstall is per method; config lives in `~/.claude`, `~/.claude.json`, and project `.claude`.

## Configuration & interfaces
| Item | Purpose |
|---|---|
| `autoUpdatesChannel`, `minimumVersion` | Any settings file |
| `requiredMinimumVersion`, `requiredMaximumVersion` | Managed |
| `DISABLE_AUTOUPDATER`, `DISABLE_UPDATES`, `CLAUDE_CODE_PACKAGE_MANAGER_AUTO_UPDATE`, `USE_BUILTIN_RIPGREP` | Environment |

## Failure modes & edge cases
- HTML from the installer URL means a block or wrong endpoint; `syntax error near unexpected token '<'`.
- `command not found: claude` is usually `PATH`.
- `Illegal instruction`, `Exec format error` on WSL1, `dyld: cannot load`, musl or glibc mismatch.
- Native binary not found after npm install: optional dependencies skipped.
- Install killed on low-memory servers; in Docker, running the installer from `/` scans the whole filesystem, so set a `WORKDIR` first.
- `claude.exe` missing after a Windows update.
- Conflicting installations: keep one.
- `Raw mode is not supported` in non-TTY.

## Changes since the snapshot
- 2.1.113: native binary spawn. 2.1.118: `DISABLE_UPDATES`. 2.1.129: package manager auto update.
- 2.1.147, 2.1.153: updater reliability, doctor line. 2.1.162: scanner wait. 2.1.163: required versions.
- 2.1.166: target announced. 2.1.238: delayed check. 2.1.243, 2.1.251: size reductions.
- 2.1.265: no native image module extraction to temp. 2.1.277: package-managed lookup failures no longer say up to date.

## Open questions
- Exact criteria for promoting a release to `stable`.
- The periodic check interval.
- Mirrors for air-gapped use are not covered in these docs.
