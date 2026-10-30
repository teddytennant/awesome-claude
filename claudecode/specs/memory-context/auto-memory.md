# Auto memory and memdir

**Status:** shipped (background consolidation and session memory: gated/unreleased, see below)
**Provenance:** both
**Sources:** docs `memory`, `claude-directory`, `settings-reference`, `sub-agents`, `errors`; snapshot `memdir/`, `services/extractMemories/`, `services/SessionMemory/`, `services/autoDream/`; changelog versions cited below

## Purpose

Let Claude accumulate durable, plain-Markdown notes across sessions without the user writing anything. Notes are per repository, machine-local, and separate from user-authored CLAUDE.md.

## Behaviour

### Enablement

1. Auto memory MUST be on by default in local sessions. Sessions in self-hosted environments, other than Claude Tag sessions, MUST default to off.
2. Resolution order: `CLAUDE_CODE_DISABLE_AUTO_MEMORY` in either direction (`1` off, `0` forces on even under `--bare` or `autoMemoryEnabled: false`), then session modes that turn it off (`--bare`, safe mode), then `autoMemoryEnabled`, then the default.
3. When off, Claude MUST neither read from nor write to the memory directory.
4. The `/memory` toggle MUST write `autoMemoryEnabled` to user settings.
5. In a background session, or a session started by another Claude Code session, the toggle MUST allow off but MUST refuse on, showing a reason that points to a directly started session.

### Storage

6. The default directory is `~/.claude/projects/<project>/memory/`. `<project>` MUST derive from the git repository, so all worktrees and subdirectories share one directory; outside git, from the project root.
7. With `CLAUDE_CODE_PROJECT_DIR_NAME` and `CLAUDE_CONFIG_DIR` both set, `<project>` MUST be the given name.
8. `autoMemoryDirectory` overrides the location. It MUST be absolute or start with `~/`. It is read from any settings scope; from project or local files it is honoured only under the workspace-trust rule that governs hooks.
9. While `permissions.blockReadsOutsideWorkingDirectories` is on, a directory chosen by a repository-supplied settings file MUST NOT be loaded, recalled, indexed, written to, or used for extraction.
10. Memory is machine-local, with no sharing across machines or cloud environments.
11. The retention sweep MUST NOT delete memory files. The directory itself is removed only if empty for the whole retention period.

### Layout and file format

12. The directory contains a `MEMORY.md` index, one line per memory, and one topic file per memory.
13. Each memory carries a `type` frontmatter field: `user`, `feedback`, `project` or `reference`.
14. Claude MUST skip anything derivable from the codebase or git history, and anything CLAUDE.md already states. It need not save something every session.
15. When Claude writes a memory file that begins with YAML frontmatter, the client MUST record the write time in a `modified` field as ISO 8601.
16. Explicit "remember" requests go to auto memory. CLAUDE.md is updated only on explicit request.

### Loading

17. The first 200 lines or first 25 KB of `MEMORY.md`, whichever comes first, MUST load at the start of every conversation. Topic files MUST NOT load at startup; Claude reads them on demand with standard file tools.
18. Limits are measured over loaded content, excluding frontmatter and HTML comments.
19. Invisible characters and tags that imitate Claude Code's own markup MUST be neutralised in `MEMORY.md` and recalled notes before they reach Claude.
20. The main conversation's memory MUST NOT load into ordinary subagents. A fork inherits it through the parent context. A subagent's `memory` field gives it a separate directory (`agent-memory/<name>/`).
21. Auto memory re-injects from disk after compaction.
22. The interface reports activity with messages like `Saved 2 memories` and `Recalled 2 memories`.

### Index maintenance

23. After a write to `MEMORY.md`, the client MUST measure it against both limits. Near a limit it MUST remind Claude to shorten it: one line per entry, detail moved to topic files, stale entries merged or dropped.
24. Over a limit, the write MUST still succeed, and the client MUST return an error telling Claude to rewrite the index, because the excess is dropped at the next load.
25. A truncation warning MUST state how many lines were cut and where the cut starts.

### Automatic recall and extraction

26. Recall surfaces relevant topic notes for a query. The snapshot scans frontmatter of up to 200 files (first 30 lines each), asks a small-model side request to choose up to five, excludes `MEMORY.md`, excludes already-surfaced files, and attaches each note with a freshness note derived from age. Post-leak changelog entries confirm that recall, age notes and structured-output use persist; the selection parameters are snapshot evidence only.
27. Extraction runs after a completed query loop, as a forked agent that shares the parent's prompt cache, and skips ranges where the main agent already wrote memory. The snapshot gates this behind a build flag and remote flags. v2.1.273 confirms that memory extraction exists; its current default is not documented.

### Gated features, snapshot only

28. **Session memory** (`services/SessionMemory/`): a per-session running notes file maintained by a background agent after thresholds (10,000 tokens to start, 5,000 tokens between updates, 3 tool calls), which can also serve as the source for compaction. Gated. No public documentation.
29. **Consolidation** (`services/autoDream/`): a background pass that merges memory across sessions after time and session-count gates (24 hours minimum in snapshot defaults), under a lock. Gated. It has no documented command, setting or changelog entry.

## Configuration & interfaces

| Interface | Effect |
|---|---|
| `autoMemoryEnabled` | On/off; any file; default `true` |
| `autoMemoryDirectory` | Location; any file, trust-gated from repository files |
| `CLAUDE_CODE_DISABLE_AUTO_MEMORY` | `1` off, `0` force on |
| `CLAUDE_CODE_DISABLE_CLAUDE_MDS` | Also prevents auto memory loading |
| `CLAUDE_CODE_PROJECT_DIR_NAME` | Names the project directory, launch environment only, needs `CLAUDE_CONFIG_DIR` |
| `CLAUDE_CODE_DISABLE_STRUCTURED_OUTPUTS` | Turns off structured outputs; recall requests are affected |
| `/memory` | Browse, edit, toggle, open folder |
| `claude purge` | Deletes project transcripts and auto memory |
| agent frontmatter `memory` | Enables per-subagent memory |

## Failure modes & edge cases

- An over-limit index is an error to Claude, not a failed write. See the `Memory index is over its read limit` entry in the errors reference.
- A memory file written with a value containing an inline `#` MUST keep the whole value (fixed v2.1.214).
- Age notes MUST stay stable between requests, or they cause prompt cache misses (fixed v2.1.275).
- Claude's edits to its own notes MUST NOT be blocked as sensitive-file writes when started in a repository subdirectory (fixed v2.1.283).
- In Cowork, a write conflict MUST show the full memory file rather than only its start and end (fixed v2.1.280).
- Before v2.1.228 the sweep could delete files in folders inside the memory directory.

## Changes since the snapshot

- v2.1.186: reminder when `MEMORY.md` nears its limit.
- v2.1.210: explicit error for writes leaving the index over limit, replacing silent truncation.
- v2.1.211: limit measures only loaded content.
- v2.1.214: `modified` frontmatter timestamp; inline `#` fix.
- v2.1.228: sweep no longer treats memory subfolders as session data.
- v2.1.234: `CLAUDE_CODE_PROJECT_DIR_NAME`.
- v2.1.268: truncation warning states lines cut. [Claude Tag] per-channel notes.
- v2.1.273: `blockReadsOutsideWorkingDirectories` hardening.
- v2.1.284: markup neutralisation.
- v2.1.285: `/memory` cannot turn memory on from background or Claude-started sessions.
- v2.1.287: arrow keys flip `/memory` toggles.
- v2.1.288: `CLAUDE_CODE_DISABLE_STRUCTURED_OUTPUTS` added after recall failures behind gateways.
- `autoMemoryDirectory` broadened: the snapshot ignored project settings outright for safety, while current docs honour project and local files under the trust rule.

## Open questions

- Whether extraction is on by default, and in which session types.
- The current recall model, limits and trigger.
- Whether snapshot-only path overrides (`CLAUDE_CODE_REMOTE_MEMORY_DIR`, `CLAUDE_COWORK_MEMORY_PATH_OVERRIDE`) persist; neither is documented.
- Whether session memory or consolidation ever shipped under another name.
