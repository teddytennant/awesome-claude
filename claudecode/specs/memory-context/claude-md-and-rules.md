# CLAUDE.md, AGENTS.md and rules discovery

**Status:** shipped
**Provenance:** both (AGENTS.md support post-leak, since v2.1.277, 2026-09-18)
**Sources:** docs `memory`, `context-window`, `prompt-caching`, `settings-reference`, `hooks`, `large-codebases`; snapshot `utils/claudemd.ts`, `utils/memory/`; changelog versions cited below

## Purpose

Give every session persistent, user-authored instructions. Files are discovered from fixed locations, concatenated, and delivered as context. They shape behaviour but are not enforced; enforcement belongs to permissions, hooks and managed settings.

## Behaviour

### Sources and order

1. The loader MUST assemble instruction files in this order, broadest first, so more specific content appears later in context:
   1. Managed policy: the OS-specific file (`/Library/Application Support/ClaudeCode/CLAUDE.md`, `/etc/claude-code/CLAUDE.md`, `C:\Program Files\ClaudeCode\CLAUDE.md`), managed rules, and the `claudeMd` managed-settings key.
   2. User: `~/.claude/CLAUDE.md` and `~/.claude/rules/`.
   3. Project: `./CLAUDE.md` or `./.claude/CLAUDE.md`, plus unscoped `.claude/rules/**/*.md`, for each directory from the filesystem root down to the working directory.
   4. Local: `CLAUDE.local.md` in each of those directories, appended after that directory's `CLAUDE.md`.
2. Files MUST be concatenated, never treated as overriding one another. Conflicting instructions are resolved by the model, not the client.
3. Content MUST be delivered as a user-role message after the system prompt, not inside the system prompt. Frontmatter and block-level HTML comments MUST be stripped before injection; comments inside code blocks MUST be preserved, and the Read tool still shows raw comments.
4. Root-chain files MUST load at launch. `CLAUDE.md` and `CLAUDE.local.md` in subdirectories of the working directory MUST load on demand, once, when Claude reads, writes or edits a file in that subdirectory. A read includes a Bash command that counts as a single-file read (`cat`, `head`, `tail`, `sed -n`, `grep`).
5. Files from `--add-dir` directories MUST NOT load unless `CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD` is set. When set, `CLAUDE.md`, `.claude/CLAUDE.md`, `.claude/rules/*.md` and `CLAUDE.local.md` load; `CLAUDE.local.md` is skipped if `local` is excluded from `--setting-sources`.
6. Project rules MUST be skipped when `project` is excluded from `--setting-sources`, including on-demand path-scoped and nested rules.

### Imports

7. `@path` references MUST expand inline. Relative paths resolve against the containing file. Absolute and `~` paths are allowed. Recursion MUST stop at a maximum depth of four hops.
8. Spaces in a path MUST be backslash-escaped; an unescaped space ends the path, and a quoted path MUST NOT be imported.
9. Import parsing MUST skip Markdown code spans and fenced code blocks.
10. An import in a project-level file that resolves outside the working directory is external. The first encounter in an interactive session MUST show a once-per-project approval dialog listing the files. Declining MUST leave the imports disabled and suppress the dialog afterwards.
11. User-scope files are trusted and load imports without the dialog, except in Cowork sessions, where imports resolving outside the session working directory are skipped, and a symlinked or hard-linked `~/.claude/CLAUDE.md` or a symlinked rules path outside the working directory is also skipped.

### Rules

12. All `*.md` files under `.claude/rules/` MUST be discovered recursively. A rule without `paths` loads at launch with the priority of `.claude/CLAUDE.md`.
13. `paths` is the only frontmatter field read; other fields are ignored without error. It accepts a YAML list or a comma-separated string. Unparseable frontmatter MUST degrade to an unscoped rule, with the parse error in `--debug` output.
14. A path-scoped rule MUST load when Read, Write or Edit touches a matching file, or a Bash command counts as a read of one. Matching MUST also work through a symlinked path to the project.
15. Patterns are relative to the directory containing the rule's `.claude` folder for project rules, and to the session's primary working directory for user rules.
16. Brace expansion MUST be bounded: one `paths` list shares a budget of 1,000 expanded patterns and 4 MiB. A pattern exceeding the budget is used unexpanded, so its literal braces match nothing. A `[` that cannot open a bracket expression makes that pattern invalid without affecting others.
17. Symlinks in `.claude/rules/` are followed, and cycles are handled. A target outside the working directory counts as an external import. After approval, only targets without `paths` load.
18. Symlinks to network paths (UNC shares, `/net`, `/Network`) MUST NOT be followed, because lookup can contact the named host. `\\wsl$` paths are not network paths.

### AGENTS.md

19. AGENTS.md reading is implemented by the built-in plugin `cc-plugin-agents-md@builtin` (ID `agents-md@builtin` before v2.1.285, and both are read now).
20. The default mode is `claude-md-or-agents-md`. Claude reads `AGENTS.md` only when no `CLAUDE.md`, `.claude/CLAUDE.md` or `CLAUDE.local.md` exists in the working directory or above. `~/.claude/CLAUDE.md`, the managed file and `.claude/rules/` do not count, and they continue to load alongside.
21. When it applies, every `AGENTS.md` and `.claude/AGENTS.md` up the chain MUST load at start, and an interactive session MUST show a line naming what loaded. A subdirectory `AGENTS.md` loads when Claude opens a file there with Read and that directory has none of the three CLAUDE files.
22. `AGENTS.local.md`, `AGENTS.override.md` and `.agents/` MUST NOT be read.
23. Imports and `claudeMdExcludes` apply inside `AGENTS.md`. Unlike `CLAUDE.md`, directly read `AGENTS.md` MUST NOT fire `InstructionsLoaded`, MUST NOT load from `--add-dir` directories, and MUST load external imports only when already approved, without prompting.
24. A file MUST be read at most once, whether reached directly, by `@AGENTS.md` import, or through a symlink.
25. AGENTS.md support is unavailable before v2.1.277, when the plugin is disabled, and in some first sessions after upgrading from v2.1.276 or earlier. The **Project instructions** row is then hidden.

### Size handling

26. A launch-time file of 4 MiB or smaller MUST load in full; a larger one MUST be skipped entirely.
27. Files that load on demand MUST be truncated to a per-file limit, ending in a note telling Claude to read the rest: 40,000 characters on a 200K window; on a 1M window 200,000 on Opus 4.6 and Sonnet 4.6, and 150,000 on later models. This covers subdirectory `CLAUDE.md`/`CLAUDE.local.md`, their imports, subdirectory rules, and path-scoped rules.
28. The client SHOULD warn at startup and in `/status` when a file exceeds the recommended length, or when several files together pass a combined limit. Each CLAUDE.md, rules file and import counts separately. Recommended length is a guideline of about 200 lines and the warning threshold scales with the context window.

### Lifecycle

29. Root and user files MUST be read once at session start and held in memory. A mid-session edit neither applies nor invalidates the prompt cache until `/clear`, `/compact` or restart.
30. An on-demand file edited before it loads takes effect. After loading it is conversation history and is not updated retroactively.
31. Compaction re-injects project-root CLAUDE.md and unscoped rules from disk. Nested files and path-scoped rules are summarised away and reload on demand.

### Exclusions and suppression

32. `claudeMdExcludes` (globs against absolute paths; arrays merge across layers) MUST NOT be able to exclude managed files. For a symlinked rule, a pattern matching either the rules path or the target excludes it.
33. `CLAUDE_CODE_DISABLE_CLAUDE_MDS`, `--bare`/`CLAUDE_CODE_SIMPLE` and `--safe-mode` suppress loading. A session started with loading fully off also omits managed content.
34. Agents with `omitClaudeMd` run without user, project and local files; managed files still load.
35. **Project instructions** values are in the table below. `managed-only` keeps managed CLAUDE.md and auto memory at launch, and on-demand subdirectory and path-scoped files still load.

### Commands

36. `/memory` MUST list instruction locations across scopes, including entries for files that do not exist yet, and selecting one opens it in the editor, creating it if needed. It also holds the auto memory toggle and folder.
37. `/context` lists launch-loaded files under **Memory files**; on-demand files do not appear there and show a `Loaded` line when they load.
38. `/init` generates or improves a `CLAUDE.md`. It reads Cursor and Copilot rule files. With `CLAUDE_CODE_NEW_INIT=1` it runs an interactive multi-artifact flow and also reads `AGENTS.md`, Devin, Windsurf and Cline rules.
39. `/import` appends a one-time copy of another agent's instruction files and carries over other configuration.
40. `/doctor` proposes trims of checked-in CLAUDE.md files. `/doctor prompt-audit [path]` reports outdated or conflicting instructions without editing files, and depends on the bundled `/claude-api` skill.

## Configuration & interfaces

| Interface | Effect |
|---|---|
| `claudeMd` (managed only) | Inline managed instructions; server-managed delivery needs no security approval since v2.1.260 |
| `claudeMdExcludes` | Skip files by glob; any settings layer |
| `pluginConfigs["cc-plugin-agents-md@builtin"].options.instructionFiles` | User, `--settings` or managed only; ignored in project and local files |
| `CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD` | Load instructions from `--add-dir` directories |
| `CLAUDE_CODE_DISABLE_CLAUDE_MDS` | Suppress all instruction and memory files |
| `CLAUDE_CODE_NEW_INIT` | Interactive `/init` |
| `--setting-sources` | Excluding `project` or `local` removes those instruction files |
| `InstructionsLoaded` hook | `load_reason`: `session_start`, `nested_traversal`, `path_glob_match`, `include`, `compact` |

| `instructionFiles` value | Reads |
|---|---|
| `claude-md-or-agents-md` | Default, as requirement 20 |
| `claude-md-and-agents-md` | Both; each directory's CLAUDE files first |
| `claude-md` | CLAUDE files only |
| `managed-only` | Managed CLAUDE.md and auto memory at launch |

## Failure modes & edge cases

- An `Instruction file not loaded` notice reports a file that could not load.
- Adding `CLAUDE.local.md` to a project that relies on `AGENTS.md` silently stops `AGENTS.md` loading, unless the mode is `claude-md-and-agents-md`.
- A `CLAUDE.md` symlinked to `AGENTS.md` is readable, but Edit and Write refuse to write through the symlink and direct Claude to the target.
- `permissions.blockReadsOutsideWorkingDirectories` or a `Read` deny rule MUST block project files symlinked outside the working directories (fixed v2.1.290).
- Write MUST ask Claude to read a truncated on-demand file in full, or edit in place, rather than overwrite it after seeing only the start (fixed v2.1.312).

## Changes since the snapshot

- v2.1.169: CLAUDE.md length warning scales with the context window; `--safe-mode` added.
- v2.1.198: conditional rules match through symlinked paths.
- v2.1.206: `/doctor` proposes CLAUDE.md trims.
- v2.1.211: excluded project sources also exclude on-demand rules.
- v2.1.217: bounded brace expansion in `paths`.
- v2.1.232: Cowork stops inlining external imports from user-scope files.
- v2.1.239: `claudeMdExcludes` matches symlink paths as well as targets.
- v2.1.260: `claudeMd` no longer triggers the server-managed security dialog.
- v2.1.271: `omitClaudeMd` agent frontmatter.
- v2.1.277: AGENTS.md support; v2.1.280 listed in `/memory` and `/context`; v2.1.281 extended to third-party providers and telemetry-off sessions.
- v2.1.281: startup notice counts files together.
- v2.1.283: `/doctor prompt-audit`.
- v2.1.284: external-symlinked rules now reach the approval prompt.
- v2.1.285: built-in plugin renamed.
- v2.1.288: Write and Edit trigger path-scoped and nested loading, previously Read only.
- v2.1.293: single-file Bash reads trigger loading.
- v2.1.309: per-file limit applied to on-demand files, fixing repeated compaction.
- v2.1.311: fixed freezes on very long list items, and stale content after automatic compaction.

## Open questions

- The snapshot restricted imports to a list of text file extensions and sets a depth constant of 5; whether the extension filter survives is not documented.
- The combined size limit for the startup warning is not published.
- Whether the first-session AGENTS.md gap is flag-driven is implied, not stated.
