# The .claude directory layout

**Status:** shipped
**Provenance:** both
**Sources:** docs `claude-directory`, `sessions`, `settings`, `memory`, `checkpointing`; snapshot `utils/envUtils.ts`, `utils/cleanup.ts`, `utils/sessionStorage.ts`; changelog versions cited below

## Purpose

Define every path Claude Code reads or writes under a project's `.claude/`, `~/.claude/` and `~/.claude.json`, plus what expires, what persists and how users delete it.

## Behaviour

### Roots

1. `~/.claude` resolves to `%USERPROFILE%\.claude` on Windows. `CLAUDE_CONFIG_DIR` relocates every `~/.claude` path, and `.claude.json` with it.
2. `~/.claude.json` MUST be created at session start or by a subcommand such as `claude auth status`, not by `--version` or `--help`.

### Authored files

| Path | Scope | Committed | Role |
|---|---|---|---|
| `CLAUDE.md` | Project, global | Yes | Instructions |
| `rules/*.md` | Project, global | Yes | Optionally path-gated instructions |
| `settings.json` | Project, global | Yes | Settings |
| `settings.local.json` | Project | No | Personal overrides |
| `.mcp.json` | Project root | Yes | Team MCP servers |
| `.worktreeinclude` | Project root | Yes | Gitignored files copied into new worktrees |
| `skills/<name>/SKILL.md` | Project, global | Yes | `/name` or auto-invoked prompts |
| `commands/*.md` | Project, global | Yes | Single-file prompts, same mechanism as skills |
| `output-styles/*.md` | Project, global | Yes | Instruction sets |
| `agents/*.md` | Project, global | Yes | Subagent definitions |
| `workflows/*.js` | Project, global | Yes | Workflow scripts, each a `/<name>` command |
| `agent-memory/<name>/` | Project, global | Yes | Subagent persistent memory |
| `~/.claude.json` | Global | No | App state, account, personal MCP, global config |
| `projects/<project>/memory/` | Global | No | Auto memory |
| `keybindings.json` | Global | No | Shortcuts |
| `themes/*.json` | Global | No | Custom themes |

Outside the tree: `managed-settings.json` (system path), `CLAUDE.local.md` (project root), `AGENTS.md` (project root, `.claude/`, or any directory), installed plugins (`~/.claude/plugins`, with `synced/` for account-synced plugins).

### Frontmatter by file

| File | Fields |
|---|---|
| `SKILL.md` | `name`, `description`, `when_to_use`, `argument-hint`, `arguments`, `disable-model-invocation`, `user-invocable`, `allowed-tools`, `disallowed-tools`, `model`, `effort`, `context`, `agent`, `background`, `hooks`, `paths`, `shell`, `metadata`, `license`, `compatibility` |
| `commands/*.md` | Skill fields except `name` and `paths` |
| `agents/*.md` | `name`, `description`, `tools`, `disallowedTools`, `model`, `permissionMode`, `maxTurns`, `autoCompactWindow`, `skills`, `mcpServers`, `hooks`, `memory`, `background`, `effort`, `isolation`, `color`, `initialPrompt`, `omitClaudeMd`, `experimental` |
| `output-styles/*.md` | `name`, `description`, `keep-coding-instructions`, `force-for-plugin` |
| `rules/*.md` | `paths` |

### Swept paths

3. The sweep MUST delete these once older than `cleanupPeriodDays` (default 30, minimum 1, and `0` is a validation error). The same cutoff applies to orphaned worktrees.

| Under `~/.claude/` | Contents |
|---|---|
| `projects/<project>/<session>.jsonl` | Transcript, including request system prompt, tools and parameters |
| `…/<session>.orphaned-<ts>-<suffix>.jsonl`, `…/<session>.jsonl.superseded-<ts>` | Set-aside transcripts, hidden from the picker |
| `…/<session>/subagents/` | Subagent transcripts, removed with the parent |
| `…/<session>/tool-results/` | Spilled outputs and full-size MCP images |
| `…/<session>/mcp-tasks/` | Running MCP task state and unread results |
| `file-history/<session>/` | Checkpoint backups, 100 checkpoints, first snapshots kept |
| `plans/` | Plan files |
| `debug/` | Debug logs |
| `paste-cache/` | Large pastes |
| `image-cache/<session>/` | Images from v2.1.274 and earlier; others' leftovers removed at any age |
| `uploads/<session>/` | Remote Control attachments |
| `dev-mods/<session>/` | Mods written during a session |
| `session-env/` | Per-session environment metadata |
| `tasks/` | Task lists |
| `shell-snapshots/` | Shell state; removed on clean exit, sweep clears crash leftovers |
| `backups/` | `.claude.json` copies; five newest plus unparseable copies |
| `feedback-bundles/` | Redacted archives for third-party or uncredentialed `/feedback` |
| `feedback/drafts/` | Drafts; shorter of `cleanupPeriodDays` or 30 days, 10-draft limit, oldest evicted |
| `usage-data/` | `/insights` reports and analysis cache |
| `skills/.trash/`, `plugins/.trash/` | Sync-removed items, about 1024 entries each |
| `plugins/installed_plugins.set-aside.*`, `.unreadable.*.kept` | Copies from rewrites of the install record |
| `todos/`, `statsig/`, `logs/` | Legacy, removed then the empty directory too |

### Retention exceptions

4. `sessions/` holds one small file per running session, for concurrency and crash detection. It is outside the age sweep: removed on exit, crash leftovers cleared on next launch.
5. Memory files are excluded; a memory directory is removed only if empty for the whole period.
6. Claude Desktop and Cowork transcripts persist at any age unless `desktopSessionCleanupPeriodDays` is set. `cleanupPeriodDays` applies instead when managed settings set it or the HIPAA configuration applies.
7. The sweep MUST NOT run in `claude -p --bare`.
8. The sweep MUST pause when retention cannot be determined safely. A file that cannot be read or parsed, or settings errors with either period set explicitly, MUST show a `/status` warning. A managed `cleanupPeriodDays` keeps the sweep running. A `retention_sweep` telemetry event reports this.

### Scratchpad

9. A per-session temp directory is provided under Claude Code's temp root, not `~/.claude`: `/private/tmp/claude-<uid>/<project>/<session-id>/scratchpad/` on macOS, `/tmp/claude-<uid>/…` or `$TMPDIR` on Linux, `%TEMP%\claude\…` on Windows, or under `CLAUDE_CODE_TMPDIR`.
10. Claude can use it without permission prompts. Hooks receive it as `scratchpad_dir`.
11. It exists only with a claude.ai sign-in, on the Anthropic API, with `enableArtifact` not `false`.
12. It lasts as long as the transcript, though the OS can clear it earlier. `claude purge` does not touch it.
13. Images since v2.1.274 live in an `images/` directory per session under the same temp root.

### Persistent paths

| Path | Contents | Notes |
|---|---|---|
| `history.jsonl` | Prompts with timestamp and project | Up-arrow, `Ctrl+R`, `!` completion; swept only under HIPAA |
| `stats-cache.json` | `/usage` totals | |
| `remote-settings.json` | Server-managed cache, or `{}` | Refreshed at startup and hourly; deleted on logout |
| `cache/changelog.md` | `/release-notes` cache | |
| `policy-limits.json` + `.stamp.json` | Feature policy cache | Deleted on logout |
| `.credentials.json` | Credentials | Keep |
| `agent-memory/` | Subagent memory | Keep |
| `jobs/`, `daemon/` | Background session state | Keep |

### Plaintext

14. Transcripts and history are not encrypted at rest. Anything passing through a tool is written to disk, along with the system prompt, tool definitions, parameters, and instruction files.
15. Mitigations: lower `cleanupPeriodDays`, set `desktopSessionCleanupPeriodDays`, use `CLAUDE_CODE_SKIP_PROMPT_HISTORY` or `--no-session-persistence`, and deny credential reads.

### `claude purge`

16. `claude purge [path]` MUST delete one project's transcripts and auto memory, per-session `tasks/`, `debug/` and `file-history/`, matching `history.jsonl` lines, and the `~/.claude.json` project entry.
17. It MUST print the plan and confirm unless `--yes` is passed. `--dry-run` previews, `-i` steps through, `--all` covers every project and deletes `history.jsonl` outright, and no path opens a picker.
18. It MUST leave `shell-snapshots/`, `backups/` and temp directories alone, and warn about them.
19. No matching state exits 1 with an error. A deletion failure MUST continue, list what failed, and exit 1.
20. It affects local data only and says so.
21. `.heapsnapshot` files from `/heapdump` are not touched by the sweep or purge.

## Configuration & interfaces

| Interface | Effect |
|---|---|
| `CLAUDE_CONFIG_DIR`, `CLAUDE_CODE_TMPDIR` | Roots; neither settable from project or local `env` |
| `cleanupPeriodDays`, `desktopSessionCleanupPeriodDays` | Retention |
| `plansDirectory`, `autoMemoryDirectory` | Relocate plans and memory |
| `claude purge` | Project deletion; `claude project purge` still works with a notice |

## Failure modes & edge cases

- Deleting `~/.claude.json`, `settings.json` or `plugins/` loses account details, preferences or installed plugins.
- `--setting-sources` without `user` MUST NOT make cleanup ignore `cleanupPeriodDays`.
- A very large `cleanupPeriodDays` MUST NOT delete recent files.
- Git worktrees the user created MUST NOT be swept because of a stale background record.

## Changes since the snapshot

- v2.1.89: `cleanupPeriodDays: 0` rejected.
- v2.1.126: `claude project purge`; v2.1.288 renamed `claude purge`.
- v2.1.208: backups pruned.
- v2.1.228: memory subfolders protected.
- v2.1.248: `desktopSessionCleanupPeriodDays`, desktop retention.
- v2.1.257: daemon temp leftovers swept.
- v2.1.271: synced skills not refreshed within the period move to trash.
- v2.1.293: purge failure handling.
- v2.1.310: large period fix.
- v2.1.311: purge states it is local only.
- v2.1.314: `.trash` capped near 1024 entries.
- New paths with no snapshot counterpart verified by name: `dev-mods/`, `mcp-tasks/`, `feedback/drafts/`, `feedback-bundles/`, `jobs/`, `daemon/`, `workflows/`, `themes/`.

## Open questions

- The contents of `session-env/` and the full schema of `~/.claude.json`.
- Whether undocumented caches and lock files exist beyond those listed; docs say such files are safe to delete.
