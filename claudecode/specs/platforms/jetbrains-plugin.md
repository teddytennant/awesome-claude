# JetBrains Plugin
**Status:** shipped (plugin settings page labelled Beta)
**Provenance:** both
**Sources:** docs `jetbrains.md`, `settings-reference.md`, `env-vars.md`; snapshot `utils/ide.ts`, `utils/idePathConversion.ts`; changelog entries mentioning JetBrains

## Purpose
Connect a terminal `claude` to a JetBrains IDE so diffs open in the IDE, the selection is shared, and IDE inspections are readable by Claude. Unlike VS Code, the plugin has a thin terminal-based model: it does not bundle the CLI.

## Behaviour

### Installation and launch
1. The plugin MUST NOT bundle the CLI. It runs the `claude` command in the IDE's integrated terminal.
2. When `claude` cannot be found, the plugin MUST show a "Cannot launch Claude Code" notification unless suppressed.
3. A custom command MUST be settable, for example an absolute path, `npx @anthropic-ai/claude-code`, or `wsl -d <distro> -- bash -lic "claude"`.
4. Remote Development MUST use the plugin installed on the remote host (Settings, Plugin (Host)), not on the client.
5. The plugin SHOULD work with IntelliJ IDEA, PyCharm, Android Studio, WebStorm, PhpStorm and GoLand among others. The snapshot's IDE list also has RubyMine, CLion, Rider, DataGrip, AppCode, DataSpell, Aqua, Gateway and Fleet.

### Features
6. `Cmd+Esc` / `Ctrl+Esc` or a UI button MUST open Claude Code.
7. Diffs MUST open in the IDE viewer unless `diffTool` is `terminal`. The **Diff tool** row MUST appear in `/config` only while connected to an IDE.
8. The current selection or tab MUST be shared automatically, except for files matching `Read` deny rules.
9. `Cmd+Option+K` / `Alt+Ctrl+K` MUST insert a reference such as `@src/auth.ts#L1-99`.
10. Claude reads inspections by calling `getDiagnostics`. The CLI MUST NOT pull diagnostics from the plugin on its own after edits.
11. Running `claude` in the integrated terminal MUST auto-connect. From an external terminal, `/ide` MUST connect and confirm, for example `Connected to IntelliJ IDEA.`
12. The same lockfile mechanism as VS Code is used on the CLI side in the snapshot. `/ide` lists running IDEs by reading lockfiles and validating workspace folders against the current directory.
13. Starting Claude from the project root SHOULD be used for file parity with the IDE.
14. Claude Code MUST NOT suggest installing the plugin on startup; that suggestion has been removed.

### Panel
15. Changelog entries refer to a "VS Code and JetBrains panels" surface (usage-limit "Get more usage" link in 2.1.301; auto-mode billed-classifier Continue/Stop prompt in 2.1.281). Docs for JetBrains describe only terminal use, so the panel's scope is unresolved. See Open questions.

### WSL
16. On WSL2, connecting to an IDE on the Windows host can fail with "No available IDEs detected" because of NAT or Windows Firewall. Supported fixes are a firewall rule for the WSL subnet, or `networkingMode=mirrored` in `.wslconfig` (Windows 11 22H2+). WSL1 is unaffected.
17. CLI-side snapshot behaviour: reads Windows-side lockfiles via `/mnt/c`, converts paths, checks the distro match, and picks the Windows host address unless `CLAUDE_CODE_IDE_HOST_OVERRIDE` is set.

## Configuration & interfaces

### Plugin settings (Settings, Tools, Claude Code [Beta])
| Setting | Effect |
|---|---|
| Claude command | Custom launch command |
| Suppress notification for when Claude Command is not found | Silences item 2 |
| Enable using Option+Enter for multi-line prompts | macOS only; needs terminal restart |
| Enable automatic updates | Plugin updates applied on restart |

### CLI side
`diffTool`, `autoConnectIde`, `CLAUDE_CODE_AUTO_CONNECT_IDE`, `CLAUDE_CODE_IDE_HOST_OVERRIDE`, `CLAUDE_CODE_IDE_SKIP_VALID_CHECK`, `/ide`, `/config`. `autoInstallIdeExtension` is documented as applying to a VS Code terminal only.

## Failure modes & edge cases
- ESC may not interrupt because JetBrains moves focus to the editor. Fix: uncheck "Move focus to the editor with Escape", or delete the "Switch focus to Editor" terminal keybinding.
- Plugin features missing: run from project root, check the plugin is enabled, and fully restart the IDE, possibly more than once.
- Edit and Write once paused about 5 seconds in JetBrains terminals with the plugin connected; fixed.
- Flicker in 2026.1+ terminals was fixed by enabling synchronized output; 2025.2 scroll-wheel events are normalised.

## Changes since the snapshot
- 2.1.301: "Get more usage" link in JetBrains panels.
- 2.1.160: plugin install suggestion removed from startup. 2.1.311: `/ide` no longer claims to have installed the plugin when it did not.
- 2.1.200: "default" permission mode shown as "Manual" in JetBrains too.
- 2.1.281: Continue/Stop prompt in VS Code and JetBrains panels when auto mode falls back to billed classifier requests.
- Fixes: 2.1.132 scroll events; 2.1.136 MCP servers vanishing after `/clear`; 2.1.166 flicker; 2.1.239 Edit and Write pauses; 2.1.311 custom skills missing editor context in the panel.

## Open questions
- Whether a graphical JetBrains panel exists, and in which builds. Changelog names it; `jetbrains.md` does not describe it.
- Whether the plugin still uses the same `~/.claude/ide/*.lock` format at 2.1.314.
- Full supported-IDE list at 2.1.314; docs say "most".
