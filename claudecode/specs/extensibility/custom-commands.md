# Custom Commands

**Status:** shipped (legacy form of skills)
**Provenance:** both
**Sources:** docs `skills`, `commands`; snapshot `commands.ts`, `skills/loadSkillsDir.ts`; changelog 2.1.91 to 2.1.299.

## Purpose

Custom commands are single Markdown files that create a slash command. They have merged into the skills system: `.claude/commands/deploy.md` and `.claude/skills/deploy/SKILL.md` both create `/deploy` and behave alike. The older form keeps working, and new work should prefer skills, which add supporting files. All rendering, invocation and permission rules are in [skills.md](skills.md); this spec records only the differences.

## Behaviour

1. A Markdown file under `.claude/commands/` (project, personal `~/.claude/commands/`, or an added directory) MUST create a command.
2. The name MUST be the file name without extension. Subdirectories MUST namespace with `:`, so `.claude/commands/frontend/component.md` is `/frontend:component`.
3. Command files MUST accept the same frontmatter as skills, except `name` and `paths`.
4. When a skill and a command file share a name, the skill MUST win.
5. A file or subfolder named `anthropic-skills`, or starting with `anthropic-skills:`, MUST NOT load, and a startup notice names it.
6. A name with refused characters (zero-width, control, direction-changing, non-plain blanks, `<`, `>`) MUST NOT load until renamed (v2.1.299).
7. `` !`cmd` `` and ` ```! ` injection, argument substitution, `disableSkillShellExecution` and `UserPromptExpansion` hooks MUST apply as for skills. A `UserPromptSubmit` hook runs before expansion, so a block stops embedded commands (v2.1.299).
8. Added-directory `.claude/commands/` is not watched, so changes need a restart. `.claude/skills/` in an `--add-dir` is watched.
9. A plugin's `commands/` directory is also supported; see [plugins.md](plugins.md). Commands count with skills in `claude plugin details`.
10. A command file named `verify` or `simplify` counts for the pre-commit instruction (v2.1.286).
11. Typed commands are recorded with `command_name` and `command_source` in telemetry; custom names are redacted unless `OTEL_LOG_TOOL_DETAILS=1` (v2.1.117).
12. Mid-prompt typed commands show in a list; unknown commands suggest the closest match (v2.1.108, v2.1.265).

## Configuration & interfaces

| Path | Command |
| :- | :- |
| `.claude/commands/x.md` | `/x` |
| `~/.claude/commands/x.md` | `/x` |
| `.claude/commands/a/b.md` | `/a:b` |

A `.claude/commands/` file under a personal `~/.claude/` that takes a synced skill's short name is named in the `/skills` note, with what to rename or delete.

## Failure modes & edge cases

- A clicked autocomplete row fills the prompt rather than running (v2.1.162).
- Slash commands other than `/stop` sent while a turn runs from `claude agents` run when the turn ends (v2.1.287).

## Changes since the snapshot

- v2.1.91: `disableSkillShellExecution` covers commands.
- v2.1.108: closest-match suggestions.
- v2.1.152: `disallowed-tools` applies to commands.
- v2.1.290: raw control characters refused in `!` commands.
- v2.1.299: name character rules; `UserPromptSubmit` runs before expansion.

## Open questions

- No removal date for the `.claude/commands/` format is documented.
- Whether command files honour every newer skill field (for example `background`) is implied by "same frontmatter" but not separately stated.
