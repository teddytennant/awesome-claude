# /doctor and diagnostics

**Status:** shipped
**Provenance:** both (reshaped since v2.1.205, 2026-07-08)
**Sources:** docs `skills`, `troubleshooting`, `debug-your-config`, `commands`, `cli-reference`, `env-vars`, `memory`, `errors`; snapshot `screens/Doctor.tsx`, `utils/doctorDiagnostic.ts`, `utils/doctorContextWarnings.ts`; changelog 2.1.105 through 2.1.311

## Purpose

Help a user find out why something is wrong: installation health, settings that did not load, resource problems and runtime faults. It offers a read-only shell report, an interactive checkup that can fix things, and supporting inspection commands.

## Behaviour

### Three surfaces

| Surface | Nature |
|---|---|
| `claude doctor` | Read-only shell report; works when a session cannot start. Reads settings in the cwd without a trust prompt |
| `/doctor`, `/checkup` | Bundled skill. Claude reports and proposes; changes after confirmation |
| `/doctor prompt-audit [path]` | Audit of instruction files (2.1.283) |

### /doctor checkup

1. Findings MUST come first. Nothing changes without confirmation.
2. Coverage:
   - Installation: duplicates, leftovers, `PATH`, unparseable settings, newer versions on the channel.
   - Extensions: unused skills, MCP servers and plugins against context cost; slow hooks.
   - `CLAUDE.md`: local files duplicating checked-in ones, derivable checked-in content (2.1.206), always-loaded guidance size.
   - Permissions: offer auto mode as default; pre-approve frequently denied read-only commands.
   - Usage: on paid plans, `/usage` recommendations over the last 7 days.
3. `disableBundledSkills` does not hide it. `DISABLE_DOCTOR_COMMAND` or `skillOverrides` does. Overrides keyed on the `checkup` alias apply.
4. `prompt-audit` runs through `/claude-api` and is unavailable if that skill is off. It covers `CLAUDE.md`, `CLAUDE.local.md`, `AGENTS.md`, rules, skills, commands, subagents and output styles.

### claude doctor report

5. Includes install health, settings-file validation errors, Remote Control eligibility, last update attempt (2.1.153), the Search line (`OK (bundled)` or the system ripgrep path), organisation policy load state (2.1.261), telemetry variables ignored in project settings (2.1.282), sandbox warnings such as mask files (2.1.257 per docs).
6. Hooks defined with array matchers are listed as invalid.

### Inspection commands

| Command | Use |
|---|---|
| `/context [all]` | What fills the window, by category, with sources; includes bundled skills |
| `/status` | Version, account, connectivity, settings sources, `Session kind`, Self-exec, policy state |
| `/memory`, `/skills`, `/hooks`, `/mcp`, `/permissions` | Loaded state per surface |
| `/skill-doctor` | Per-skill cost and use |
| `/debug [description]` | Turn on logging now and ask Claude to diagnose |
| `/heapdump` | Heap snapshot and diagnostics JSON |
| `/usage` | One-line fixes; `f` applies (`settings:fixUsage`) |
| `/insights` | Report over recent sessions |

### Logging

7. `--debug[=filter]` or `DEBUG=1` writes to `~/.claude/debug/<session-id>.txt`. `/debug` starts mid-session.
8. `--debug-file` chooses the path. `CLAUDE_CODE_DEBUG_LOGS_DIR` is a file path despite the name, and needs debug on separately. `--debug-file` wins.
9. `CLAUDE_CODE_DEBUG_LOG_LEVEL`: `verbose`, `debug` (default), `info`, `warn`, `error`.
10. The log records hook matching, keybinding warnings, status line stderr, `[spellcheck]` lines, MCP stderr and unknown agent frontmatter fields (2.1.296).

### Clean-room testing

11. `--safe-mode` disables `CLAUDE.md`, skills, plugins, hooks, MCP servers, custom commands, agents, output styles, workflows, themes, keybindings, status line and file-suggestion commands, LSP servers and auto memory. Auth, model, built-in tools and permissions work.
12. Managed policy still applies, including policy hooks, status line and file-suggestion commands. Managed plugins, skills, `CLAUDE.md` and MCP servers do not load.
13. For deeper isolation: `CLAUDE_CONFIG_DIR=<new dir> claude --setting-sources user` in an empty directory. Managed settings still apply, and claude.ai connectors load on sign-in.

### Performance rules

14. A critical memory warning MUST show past 2.5 GB heap and clear below it. Outside fullscreen, `/compact` frees memory. Otherwise restart with `--continue`.
15. `/heapdump` writes `<session-id>.heapsnapshot` and `<session-id>-diagnostics.json` to `~/Desktop`, or home on Linux without one. The summary states whether memory is JS heap or native, and any leak indicators. The snapshot can hold credentials; only the JSON is safe to share.
16. Thrashing compaction stops with `Autocompact is thrashing: the context refilled to the limit...`.

### Footer errors

17. `Auto-update failed · Run claude doctor` points at install troubleshooting. A one-time notice appears when an npm global install cannot auto-update (2.1.153).

## Configuration & interfaces

| Key | Effect |
|---|---|
| `DISABLE_DOCTOR_COMMAND` | Hide `/doctor` and `/checkup` only; not `claude doctor` |
| `disableBundledSkills` | Does not hide `/doctor` |
| `DEBUG` | Enable debug |
| `CLAUDE_CODE_DEBUG_LOGS_DIR`, `CLAUDE_CODE_DEBUG_LOG_LEVEL` | Log file, level |
| `CLAUDE_CODE_SAFE_MODE` | Safe mode |
| `USE_BUILTIN_RIPGREP=0` | System ripgrep |
| `CLAUDE_CONFIG_DIR` | Config home |

## Failure modes & edge cases

- `/doctor` in a remote session must not show a contradictory "Not inside a remote session" failure.
- An empty `.mcp.json` MUST NOT be reported invalid.
- `claude update` and `claude doctor` must not hang when a shell-config path is a directory.
- WSL search can return fewer matches while the Search line reads OK.
- Stale `enabledPlugins` entries must not report false "not found" errors.

## Changes since the snapshot

- 2.1.105: status icons, `f` to fix. 2.1.116: opens mid-turn. 2.1.178: flat tree layout.
- 2.1.205: replaced by a Claude-driven checkup; `Doctor` keybinding context and `doctor:fix` removed; `/checkup` added.
- 2.1.283: `prompt-audit`. 2.1.296: frontmatter hints.
- Warnings moved in: 2.1.144, 2.1.183, 2.1.203.

## Open questions

- The exact sections and output format of `claude doctor` today.
- Whether an in-session non-skill diagnostics view survives.
- Whether snapshot `claude doctor` Ink screen is still its implementation.
