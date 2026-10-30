# Settings system

**Status:** shipped
**Provenance:** both
**Sources:** docs `settings`, `settings-reference`, `managed-settings`, `server-managed-settings`, `env-vars`, `debug-your-config`; snapshot `utils/settings/`, `migrations/`, `main.tsx`, `utils/config.ts`; changelog versions cited below

## Purpose

Resolve configuration from layered JSON sources into one effective view, apply changes live where safe, and let organisations enforce policy. For every key see [settings-keys-reference.md](settings-keys-reference.md).

## Behaviour

### Sources

1. Files: user `~/.claude/settings.json`; shared project `.claude/settings.json`; project local `.claude/settings.local.json`. Plus the `--settings <file-or-json>` layer and managed sources. Terminal, VS Code, JetBrains and desktop read the same files.
2. No file is created at install. The user file is created on the first `/config` change stored there; the local file on the first standing permission approval. A few `/config` options, such as **Show tips**, save locally.
3. `~/.claude.json` is a separate, app-written file: account, MCP servers, per-project state, and the **Global config** keys.
4. `--setting-sources` limits loaded sources to any of `user`, `project`, `local`, and spawned sessions inherit the list. An excluded file MUST supply nothing, including auto mode rules and saved consents.

### Local file placement

5. In a git repository, the local file lives at the repository root, or the main checkout's root in a worktree, and approvals apply repo-wide.
6. It stays beside `.claude/settings.json` outside git, when the root is the home directory, on Windows, or when the root, `.git` or `.claude` is not owned by the user.
7. An older local file left in a starting directory is still read: on conflict the root's value applies, and permission rules from both apply.
8. On first write in an unignored repository, the client MUST add `**/.claude/settings.local.json` to the global git excludes file.
9. The shared project file is read from the session's primary working directory. After `/cd`, both project files are read from the new directory.

### Precedence and merge

10. Highest first: managed, command line (`--settings`), local, shared project, user. A key at a higher level overrides lower ones.
11. Environment variables are not a level. Each pair is decided individually. `env` blocks are ordinary keys that follow the levels.
12. Lists MUST concatenate and deduplicate across layers. Objects merge deeply. Snapshot implementation: `mergeWith` with an array customiser.
13. Exceptions: `fallbackModel` is taken whole; `modelPicker` is taken whole from the highest of managed, `--settings` and user, and ignored in project and local; `availableModels` from managed is applied as-is unless a host supplies its own; `modelSettings` resolves per model together with `effortLevel`.

### Managed tier

14. Sources rank: remote (server-managed from claude.ai or a Claude apps gateway); MDM (macOS plist, HKLM); files (`managed-settings.d/*.json` over `managed-settings.json`, drop-ins sorted and merged); HKCU, used only when no admin document is present.
15. `managedSourcesBehavior: "first-wins"` (default) uses the highest source carrying a policy key. `"merge"` combines all admin sources by kind: lists union, locks take the strictest, allowlists and some values come whole from the highest source. `env` merges per variable either way.
16. `policyHelper` computes managed settings from an executable; when it emits `managedSettings`, that is the only managed policy for the session.
17. Embedding hosts add restrictive policy through the SDK `managedSettings` option, governed by `parentSettingsBehavior`.
18. Delivery timing: remote at startup and hourly; MDM at startup and every 30 minutes; files on change.
19. Server-managed changes that need approval, such as hooks or `env`, wait for a dialog in interactive sessions. `forceRemoteSettingsRefresh` blocks startup until a fresh fetch.
20. Managed settings reach cloud sessions only through server-managed delivery. Cowork does not fetch them; it reads device policy unless a full-VM sandbox is required.

### Restrictive-value exceptions

21. The following values MUST be honoured from a scope that otherwise cannot override managed: `disableClaudeAiConnectors: true`, `enableArtifact: false`, `disableArtifact: true`, `isolatePeerMachines: true`, and `permissions.blockReadsOutsideWorkingDirectories: true` from any scope; `autoMode.classifyAllShell: true` from user or `--settings`; `remoteControlAtStartup: false` and a stricter `crossSessionInbound` from project or local; `useAutoModeDuringPlan`, `syncClaudeAiSkills`, `syncClaudeAiPlugins` `false` from any managed source, `--settings`, user or local (not shared project); a lower `maxEffortLevel` from any scope.
22. `CLAUDE_CODE_PROVIDER_MANAGED_BY_HOST` lets a host's model configuration override `model`, `fallbackModel`, `modelPicker`, `modelOverrides` and managed model variables.

### Repository trust

23. `permissions.allow`, `permissions.additionalDirectories`, `extraKnownMarketplaces` and most `env` values from a repository file MUST wait for workspace trust; `deny` and `ask` apply at once.
24. An untracked local file's allow rules do not wait for trust; a tracked one's do.
25. Keys scoped `User`, `User or managed`, `User, local, or managed`, `Managed` or `Global config` MUST be ignored in a shared project file, apart from specific off-switches.
26. `permissions.defaultMode` values `auto` and `bypassPermissions` MUST NOT take effect from project or local files.

### `env` application

27. A settings `env` value overwrites a shell export, except when the desktop app or a self-hosted runner built the launch environment, whose values win.
28. User, `--settings` and managed values apply at startup and on change; project and local values after trust (at startup in `-p`). Variables classified safe apply at startup from every file, apart from those denied. After `/cd`, new project values layer on.
29. Values are copied literally, with no `~` or `$HOME` expansion. Removing a variable does not unset it in a running session. An empty string cancels a shell export for provider selection.
30. Variables denied in project and local files, identity variables ignored everywhere, and launch-only variables are listed in [env-vars-reference.md](env-vars-reference.md).

### Editing and live reload

31. Settings files are strict JSON. The `$schema` line points to the public schema, which can lag releases.
32. `/config` opens the dialog on **Config**; `/status` on **Status**. `/config key=value` sets options, in interactive mode, `-p` and Remote Control, and `/config --help` lists shorthand keys. It cannot enable options requiring panel confirmation. Writes go to user settings mostly, some to local, and global options to `~/.claude.json`.
33. In the browser at claude.ai/code, `/config` opens the account settings page.
34. The client MUST watch settings files and apply edits to the running session, including new files where the folder existed, or the project `.claude/` created mid-session.
35. Snapshot: a chokidar-based detector with MDM polling; internal writes are suppressed to avoid self-triggering. `ConfigChange` hooks fire for each detected file change, not for MDM or remote delivery.
36. `model`, `effortLevel` and `modelSettings` are read at session start; use `/model` or `/effort`.
37. In-app writes MUST refresh the in-memory snapshot.

### Validation

38. Invalid JSON or a schema-rejected value in a user, project or local file is a **Settings Error**: an interactive dialog offers fix with Claude's help, exit, or continue without. An individually bad entry is a **Settings Warning**: skip that value, keep the rest.
39. `-p` shows no dialog, skips the broken part, and lists it on stderr in text output.
40. Managed settings keep enforcing valid content; some keys fail closed. A mistyped boolean lock value MUST apply the lock. An unparseable managed document has separate handling.
41. A corrupted `~/.claude.json` MUST be copied to `~/.claude/backups/.claude.json.corrupted.<timestamp>`, with an exit-or-reset prompt; `-p` errors out. Five timestamped backups are kept.
42. `--settings` files MUST be regular files of at most 2 MiB.
43. Schema building is lazy, covering only the parts in use. The snapshot retains unknown keys through passthrough.
44. `claude doctor` lists rejected entries. `/status` shows `Setting sources` and `Skipped sources`.

### Migrations

45. At startup the snapshot runs versioned, one-shot migrations gated by `migrationVersion` (current value 11): moving legacy global-config values into settings (`autoUpdates`, bypass-permission acceptance, project MCP approval, `replBridgeEnabled` to `remoteControlAtStartup`), remapping model strings (Sonnet 1M, Sonnet 4.5 to 4.6, legacy Opus, Opus to Opus 1M, an internal codename), and resetting opt-ins and defaults. Asynchronous migrations run after, such as moving the changelog cache.
46. Migrations MUST be idempotent and write only where the user had an affected value.

## Configuration & interfaces

| Interface | Effect |
|---|---|
| `--settings`, `--setting-sources` | Session layer; source filter |
| `/config`, `/status`, `claude doctor` | Edit; inspect |
| `ConfigChange` hook | Observes file changes, can block |
| `managedSourcesBehavior`, `policyHelper`, `parentSettingsBehavior`, `forceRemoteSettingsRefresh`, `wslInheritsWindowsSettings` | Managed tier control |
| `CLAUDE_CONFIG_DIR` | Moves user-level files |

## Failure modes & edge cases

- A read-only or generated user file means saved choices apply only to the current session.
- A symlinked settings file MUST hot-reload and write correctly.
- Numeric `env` values MUST NOT crash startup. Prototype-named permission rules MUST NOT invalidate a file. Legacy enum values MUST NOT invalidate a whole file.
- A managed-settings file that is a link outside the managed folder produces a warning. OS-denied reads warn and continue.
- A tampered cache of server-managed settings MUST NOT disable built-in policy.
- Cloud sessions read shared project settings only with one repository and outside project threads. Several repositories read only `enabledPlugins` and `extraKnownMarketplaces`.
- Claude's file tools MUST ask before editing settings files, including the server-managed cache.

## Changes since the snapshot

- v2.1.119: `/config` settings persist to `settings.json` and join precedence.
- v2.1.181: `/config key=value`. v2.1.183: `--help`, Esc saves.
- v2.1.207: `autoMode` no longer read from local settings.
- v2.1.211 (per docs): local file moves to repository root.
- v2.1.214: 2 MiB `--settings` cap.
- v2.1.223: admin `env` merges per key.
- v2.1.257: `managedSourcesBehavior: "merge"` takes `sandbox.credentials.awsPairs` and `sandbox.ripgrep` whole; the key itself has no changelog entry.
- v2.1.243: `Skipped sources` in `/status`.
- v2.1.246: `/cd` applies new project settings at once.
- v2.1.251: project `env` loses path-choosing variables.
- v2.1.257: `bypassPermissions` no longer from any file.
- v2.1.260: `claudeMd` skips the approval dialog.
- v2.1.281: `"attribution": false`; `--setting-sources` forwarded to spawned sessions.
- v2.1.282: telemetry variables ignored in project and local files, with notice; mistyped lock values apply the lock.
- v2.1.284: lazy schema.
- v2.1.290: `CLAUDE_CODE_DISABLE_ATTACHMENTS` and dialog timers repository-denied; Chrome cannot be enabled by project files.
- v2.1.304: mods' `settings.read` hooks see each layer.
- v2.1.314: excluded sources supply nothing; file tools ask before editing the remote cache.

## Open questions

- The current migration list and version.
- Whether unknown keys remain preserved under the lazily built schema.
- How the mods' `settings.read` layer interacts with managed precedence, beyond making a value a ceiling.
