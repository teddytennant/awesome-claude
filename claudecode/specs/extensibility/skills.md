# Skills

**Status:** shipped
**Provenance:** both (core in snapshot; claude.ai sync, nested loading, `disallowed-tools`, `/skill-doctor` and much of the name model post-leak, since v2.1.91, 2026-04-02)
**Sources:** docs `skills`, `commands`, `plugins__measure`, `settings-reference`, `errors`, `env-vars`; snapshot `skills/loadSkillsDir.ts`, `skills/bundled/`, `skills/bundledSkills.ts`; changelog 2.1.91 to 2.1.314.

## Purpose

A skill is a prompt package: a `SKILL.md` with YAML frontmatter and a Markdown body, plus optional supporting files. Its name and description sit in the model's context; the body loads only on invocation. Either the user (`/name`) or the model (Skill tool) can invoke it. Skills follow the Agent Skills open standard, with Claude Code extensions. Custom commands are the older single-file form of the same thing (see [custom-commands.md](custom-commands.md)).

## Behaviour

### Discovery

1. Skills MUST load from these locations.

| Location | Path | Reach |
| :- | :- | :- |
| Enterprise | `.claude/skills/<name>/SKILL.md` in the managed directory | Machines where deployed |
| Personal | `~/.claude/skills/<name>/SKILL.md` | All local projects; not Cowork or cloud |
| Project | `.claude/skills/<name>/SKILL.md` | The repository; not cloud project threads |
| Nested | `<subdir>/.claude/skills/...` | Sessions in or below `<subdir>`, else on first file work there |
| Additional dir | `.claude/skills/` under an `--add-dir` | That session |
| Plugin | `<plugin>/skills/<name>/SKILL.md` | Where the plugin is enabled |
| claude.ai account | Synced into `~/.claude/skills/synced/` | Cowork, cloud, and signed-in terminal sessions |

2. Project skills MUST load from the start directory and every parent up to the repo root. Linked worktrees stop at the worktree root, and if it has no `.claude/skills`, the main checkout's skills load (v2.1.277). `/cd` adds the new directory's skills (v2.1.246).
3. Skills below the start directory MUST load lazily, on the first read or edit of a file there, and persist for the session (v2.1.178). `/add-dir` on the subdirectory loads them sooner.
4. `permissions.additionalDirectories` MUST NOT load skills. Skills from added directories depend on the `project` setting source and are restricted by `strictPluginOnlyCustomization`, bare mode and `--safe-mode`.
5. Symlinked skill folders MUST load from the target, once per target, in enterprise, personal and project locations.
6. `synced` (any case) is reserved as a folder name. `anthropic-skills` and `anthropic-skills:*` are reserved for folders, frontmatter names, command files and saved workflows in every session; such items do not load and a startup notice names the first offender. A plugin named `anthropic-skills` loads, but `/anthropic-skills:<name>` runs the synced skill. An MCP server under that name, or `claude-ai`, lists no prompts or skills (v2.1.282).
7. A skill folder with `.claude-plugin/plugin.json` MAY load as plugin `<name>@skills-dir`, requiring trust in project locations and an administrator not having blocked it (v2.1.157). See [plugins.md](plugins.md).
8. The watcher MUST pick up `SKILL.md` changes in personal, project and `--add-dir` skills without restart, except in bare mode. A top-level skills directory created mid-session needs `/reload-skills`, on every change. Components of a skill-folder plugin need `/reload-plugins`.

### Naming

9. Personal and project skills take the frontmatter `name` if free, and the directory name also invokes them.
10. Clash resolution:

| Clash | Result |
| :- | :- |
| Enterprise, personal, project | Enterprise over personal over project |
| Those and a bundled skill or built-in | The skill replaces the command but not its aliases; the built-in case applies to local terminal sessions |
| Skill and `.claude/commands/` file | Skill |
| Root and nested | Both load: nested is `/<rel/dir>:<name>`, and the model is told to pick by file location |
| Added dir and any other | The other wins; added skill takes prefix `/<dirname>:<name>`; if two added dirs share a folder name, the prefix starts with the parent's name (v2.1.309) |
| Plugin and any other | Both load; plugin is `/<plugin>:<name>`, and the bare name works when free (v2.1.265) |
| Synced short name and anything | The other wins; synced runs only as `/anthropic-skills:<name>` |

11. A `name` already bearing the plugin prefix MUST NOT be doubled (fixed in v2.1.246).
12. Names with zero-width, control, private-use or unassigned characters, direction-changing characters, non-plain blanks, or `<`/`>` MUST be refused (v2.1.299). A refused file or directory name stops the skill loading, except for plugin folders, where the characters become hyphens. A refused frontmatter `name` is ignored. Debug tag: `[names]`. A `name` over 256 characters is ignored (v2.1.292).
13. Synced-name comparison MUST ignore case, spacing, invisible characters and compatibility forms. Cross-alphabet look-alikes count as distinct, and the `claude.ai sync` label distinguishes them (v2.1.228).

### Frontmatter

14. Frontmatter MUST be read only when `---` is the first line. Malformed YAML MUST load the body with empty metadata (v2.1.186). Unknown fields MUST be silently ignored. Booleans accept `yes`, `no`, `on`, `off`, `1`, `0` in any case (v2.1.218).

| Field | Effect |
| :- | :- |
| `name`, `description`, `when_to_use` | Identity and listing text; description falls back to the first non-empty body line; `<`, `>` are escaped |
| `argument-hint`, `arguments` | Autocomplete hint; named positional args (string or list) |
| `disable-model-invocation` | Model cannot auto-invoke; description leaves context; also blocks subagent preloading and scheduled-task firing |
| `user-invocable` | `false` hides from `/` and refuses typed `/name`; the model can still invoke |
| `allowed-tools` | Pre-approves tools for the invoking turn only; cleared on next message; does not restrict |
| `disallowed-tools` | Removes tools while active, cleared on next message; cannot remove `EndConversation` while other tools remain (v2.1.152) |
| `model`, `effort` | Rest of current turn; with `context: fork`, apply to the subagent. `CLAUDE_CODE_EFFORT_LEVEL` beats `effort`. A model excluded by `availableModels` or unsupported in auto mode is not used |
| `context`, `agent`, `background` | `fork` runs in a subagent; `agent` defaults to `general-purpose`; `background` defaults to true |
| `hooks` | See [hooks.md](hooks.md) |
| `paths` | Globs relative to cwd limiting auto-activation; files outside cwd never match |
| `shell` | `bash` or `powershell` |
| `metadata`, `license`, `compatibility` | Stored, not acted on; `compatibility` up to 500 characters; a non-map `metadata` is dropped |

15. `display-name`, `default-enabled`, `fallback` and `metadata.*` keys accept kebab, snake and camel case (v2.1.186).
16. claude.ai uploads, the Skills API and `package_skill.py` accept only `name`, `description`, `license`, `compatibility`, `metadata`, `allowed-tools`, and fail hard on others.

### Body rendering

17. Substitutions: `$ARGUMENTS`, `$ARGUMENTS[N]`, `$N`, `$name`, `${CLAUDE_SESSION_ID}`, `${CLAUDE_EFFORT}`, `${CLAUDE_SKILL_DIR}`, `${CLAUDE_PROJECT_DIR}`, and in plugin skills `${CLAUDE_PLUGIN_ROOT}`, `${CLAUDE_PLUGIN_DATA}`. The directory variables also substitute in `allowed-tools` Bash rules.
18. Indexed args use shell-style quoting. A missing indexed placeholder stays literal; a missing named placeholder is empty. Argument values are inserted literally, not re-expanded. `\$` escapes before a digit, `ARGUMENTS` or a declared name; `\\$1` still expands; `${CLAUDE_*}` cannot be escaped.
19. If arguments are given and no placeholder receives one, `ARGUMENTS: <value>` MUST be appended.
20. `` !`cmd` `` (at line start or after whitespace) and ` ```! ` blocks MUST run before the model sees the body, with output inserted as plain text and never re-scanned. Raw control characters other than tab and newline are refused (v2.1.290).
21. Injected commands run through the Bash or PowerShell tool, inheriting the session's cwd, 2-minute default timeout and output ceiling. `shell: bash` without bash fails the invocation. stderr merges into stdout on bash.
22. A failed command MUST abort the whole invocation; the model sees nothing. Exit 1 from search and comparison commands is a normal result. A command backgrounded on timeout still renders; one that cannot background is killed and aborts.
23. Injected commands MUST never prompt. Deny rules abort. Outside auto mode, any non-allow result aborts, so `allowed-tools` is how to pre-approve. In auto mode a command needing approval loads the skill with an instruction to run it as a reviewed call (v2.1.271), but still aborts in forked skills that set `agent` and in sessions lacking the shell tool.
24. `disableSkillShellExecution` replaces commands from user, project, plugin and additional-directory sources with a fixed placeholder. Bundled and managed skills are unaffected. A managed `true` cannot be overridden.
25. Synced skills: frontmatter applies, display text is sanitized, and `allowManagedPermissionRulesOnly` voids `allowed-tools`. Body: cloud keeps local behaviour; Cowork replaces `!` commands with the placeholder; other local sessions leave `!`, `@` and the two placeholders literal (v2.1.228).

### Invocation and lifecycle

26. A name at message start runs the skill. Mid-message, the name is permission only, and the model judges; such names are flagged to the model, including `disable-model-invocation` ones (v2.1.287).
27. At the terminal prompt, up to six leading skills stack (first plus five more; v2.1.199) with trailing text as `$ARGUMENTS` for each. Expansion stops at a non-inline skill, such as a fork or `/loop`. `-p` and the SDK load only the first.
28. Rendered content MUST enter the conversation once and persist; the file is not re-read. Re-invocation with identical output adds a short note; differing output appends in full.
29. After compaction, the latest invocation of each skill MUST be reattached: first 5,000 tokens each, 25,000 combined, newest first. The skill list is re-sent after compaction, and `/reload-skills` sends only new or changed skills (v2.1.304).
30. `context: fork` starts a fresh subagent without conversation history. It runs in the background by default, but waits in `-p`/SDK, with `CLAUDE_CODE_DISABLE_BACKGROUND_TASKS=1`, for overlapping invocations of the same skill, on scheduled-task firing, and for workflow agents (v2.1.295). Background forks use the narrower background tool set and edit outside checkpoints.
31. The model may invoke some built-ins via the Skill tool (`/init`, `/security-review`; v2.1.108), not others such as `/compact`. `/verify` and `/code-review` are never auto-run (v2.1.215).
32. A verify or simplify skill from enterprise, personal, project, additional-dir or command-file sources MUST trigger pre-commit instructions, unless model invocation is off or `includeGitInstructions` is disabled (v2.1.286). Bundled, plugin and synced ones do not count.

### Listing and relevance

33. The listing MUST contain every skill name. Descriptions are capped per entry at 1,536 characters (`skillListingMaxDescChars`), and the whole listing at 1% of the context window (`skillListingBudgetFraction`, or `SLASH_COMMAND_TOOL_CHAR_BUDGET` as a fixed count). On overflow, descriptions drop from least-invoked first, with a debug warning.
34. `paths` gates automatic activation. `/claude-api` activates on `anthropic` or `@anthropic-ai/sdk` imports. Plugin marketplace relevance is separate: see [marketplaces.md](marketplaces.md).

### Controls

35. `skillOverrides` values: `on`; `name-only`; `user-invocable-only` (labelled `user-only`); `off`. `off` also hides the skill from Remote Control and SDK command lists, and full-name invocation errors. Plugin skills are unaffected. In managed or `--settings` sources, aliases apply and can only restrict; elsewhere entries match skill names only. `/skills` writes to `.claude/settings.local.json`.
36. Permission rules: `Skill(name)`, `Skill(name *)`. Deny also blocks aliases, nested variants, Desktop plugin delivery of a synced skill, and `Skill(skill:<name>)` matches any of its names (v2.1.283). Allow matches only the skill's own name and the invoked name. `Skill(anthropic-skills:*)` covers only synced skills (v2.1.282).
37. Workspace trust does not gate `allowed-tools`. `allowManagedPermissionRulesOnly` voids it for project and personal skills (v2.1.282), and `/status` lists affected skills.

### claude.ai sync

38. Signed-in terminal sessions MUST download account skills in the background without delaying startup (v2.1.273 per docs; opt-out in v2.1.275), checking about every 10 minutes when active and 40 when idle (v2.1.293). The model waits only when invoking one. `CLAUDE_CODE_SYNC_SKILLS=1` makes `-p` wait for the list.
39. Sync MUST NOT run with non-`/login` credentials, without feature-flag fetching, in bare or safe mode, when managed settings lock skills to plugins, or with `--setting-sources` lacking `user`.
40. Sync is one-way; local edits are not saved and may be overwritten. Stale copies keep loading offline for the same account. `syncClaudeAiSkills: false` moves synced skills to `~/.claude/skills/.trash/` at next start.

### `/skill-doctor`

41. MUST report context cost and usage for session skills other than bundled and enterprise ones, flag listed-but-never-invoked skills, say where to turn each off, and list unused plugins. Interactive: opens the `/plugin` **Stats** tab. `-p`: prints text. Over Remote Control it replies that reports are unavailable. Unavailable without feature-flag fetching.

## Configuration & interfaces

### Bundled skills at v2.1.314

`/artifact-capabilities`, `/artifact-diagramming`, `/batch`, `/claude-api`, `/claude-in-chrome`, `/code-review`, `/dataviz`, `/debug`, `/design`, `/design-sync`, `/doctor` (alias `checkup`), `/fewer-permission-prompts`, `/loop`, `/run`, `/run-skill-generator`, `/simplify`, `/slides`, `/update-config`, `/verify`, `/workflow-authoring` (dynamic workflows only). `plugin-authoring` also exists as a built-in skill. `disableBundledSkills` turns them off; `/doctor` stays typable unless `DISABLE_DOCTOR_COMMAND` or a `skillOverrides` `off` entry applies. Snapshot-only bundled names (`keybindings`, `loremIpsum`, `remember`, `scheduleRemoteAgents`, `skillify`, `stuck`) are not confirmed current.

### `/claude-api` subcommands

`migrate`, `upgrade` (v2.1.236), `api-version` (v2.1.307), `managed-agents-onboard` (with URL or template, v2.1.290), `managed-agents-secure` (v2.1.304), `prompt-audit` (v2.1.221), `cost-optimize` (v2.1.247), `build-eval`, `hillclimb` (v2.1.259), `preserved-thinking-migration` (v2.1.282). On-demand reference loading reduced its cost from over 200k tokens to about 25k (v2.1.234).

### `/doctor`

Checkup covering installation, extensions, `CLAUDE.md` files, permissions and usage (v2.1.305); proposes before changing. `/doctor prompt-audit` audits instructions (v2.1.283). `claude doctor` is a separate read-only shell diagnostic.

### `/run`, `/verify`, `/run-skill-generator`

`/run-skill-generator` records a launch recipe as `.claude/skills/run-<name>/`. `/verify` records its own at `.claude/skills/verify/SKILL.md`; at the root this replaces the bundled skill.

## Failure modes & edge cases

- `Shell command failed for pattern "..."`, `Shell command permission check failed for pattern "..."`, and `No shell command in <name> was run` report render failures.
- A cloud scheduled task invoking a local-only skill reports it not found.
- `paths` does not match files in a sibling worktree even if added with `/add-dir`.
- Skill tool "Unknown skill" errors suggest the full plugin name (v2.1.269) or the listed name (v2.1.299), and report failed plugin loads (v2.1.283).
- Before v2.1.280, a `manifest.json` in `~/.claude/skills/` moved listed folders to `.trash`.
- Under a `strictPluginOnlyCustomization` hooks lock, a personal or project skill declaring `hooks` loses `allowed-tools`.

## Changes since the snapshot

- v2.1.91: `disableSkillShellExecution`.
- v2.1.105: listing cap 250 to 1,536.
- v2.1.108: built-ins via Skill tool.
- v2.1.152: `disallowed-tools`, `/reload-skills`.
- v2.1.157: skill-folder plugins.
- v2.1.178: nested skills.
- v2.1.186: malformed YAML tolerance.
- v2.1.198: `/dataviz`.
- v2.1.199: skill stacking.
- v2.1.228: synced skill hardening.
- v2.1.261: `/skill-doctor` (changelog).
- v2.1.269: `anthropic-skills:` naming.
- v2.1.275: terminal sync.
- v2.1.283: `/doctor prompt-audit`.
- v2.1.299: name character rules.
- v2.1.304: list re-sent after compaction.

## Open questions

- `/skill-doctor`: docs say v2.1.252; the changelog first lists it at v2.1.261.
- Terminal sync: docs say v2.1.273; the changelog entry is v2.1.275.
- The doc's "turned-off Skills" recovery path and retention are defined only by the general sweep.
- Exact `/skill-doctor` metrics are not specified.
- Skill description ranking or selection inside the model is model-side and not specified.
