# Desktop Local Scheduled Tasks
**Status:** shipped
**Provenance:** post-leak (Claude Desktop 1.1.5368+)
**Sources:** docs `desktop-scheduled-tasks.md`, `scheduled-tasks.md`, `routines.md`

## Purpose
Start fresh Code tab sessions on a schedule on the user's machine, with local files and tools. Cloud scheduled tasks are covered by [routines.md](routines.md).

## Behaviour

### Definition
1. A task MUST have a name (lowercased to kebab-case, unique, used as its folder), instructions, folder, schedule, permission mode and model.
2. Local tasks MUST NOT have repository or GitHub event or API triggers; those make a task cloud. **Only on this computer** picks local.
3. Definition lives at `~/.claude/scheduled-tasks/<task-name>/SKILL.md` (or under `CLAUDE_CONFIG_DIR`), frontmatter `name` and `description`, prompt as body. Edits apply on the next run. Schedule, folder, model and enabled state are not stored there.
4. Runs use the working directory as it stands, including uncommitted changes, unless **Worktree** is selected in Edit (git repos only).
5. Claude MUST be able to list, create, edit and pause tasks from any Desktop session, but deletion is by the Delete button only. A one-time task MUST disable itself after firing.
6. A running task MAY change its own schedule or prompt with the `update_scheduled_task` MCP tool.

### Schedules
7. Options: Hourly, Daily, Weekdays, Weekly, Manual, Custom. Custom is a cron expression in local time with numeric days and months, Sunday `0`.
8. Forms MUST reject cron more frequent than hourly. Claude-set schedules may go down to 1 minute, and may be a single future run.

### Execution
9. Desktop MUST check every minute while open and start a fresh session when due, with a deterministic per-task delay of a few minutes to stagger traffic.
10. Tasks fire only while the app is running and the computer is awake. Otherwise the run is skipped. **Keep computer awake** prevents idle sleep but not lid-close sleep.
11. On start or wake, Desktop MUST check the last seven days and start exactly one catch-up run for the most recent missed time, with a notification, discarding older ones.
12. Run skip reasons MUST be shown in History: asleep, previous run still in progress, or other tasks already running.

### Permissions
13. Each task has its own mode. Allow rules in `~/.claude/settings.json` apply.
14. In Manual, a tool without permission MUST stall the run until approved in the run's session.
15. "Always allow" from a run MUST persist per task, reviewable and revocable in the **Always allowed** panel.
16. MCP tools with `requiresUserInteraction` prompt on every call, with no always-allow.

### Management
17. A detail page MUST offer Run now, Active/Paused, Edit, History, Always allowed and Delete.
18. Delete MUST archive the sessions and leave the task folder on disk.
19. The sidebar MAY show a Scheduled group, one row per task.

## Configuration & interfaces
| Option | Cloud | Desktop | `/loop` |
|---|---|---|---|
| Machine must be on | No | Yes | Yes |
| Open session needed | No | No | Yes |
| Survives restarts | Yes | Yes | On `--resume`, with exceptions |
| Local files | No | Yes | Yes |
| Permission prompts | Auto default | Per task | Inherited |
| Minimum interval | 1 hour | 1 minute by Claude, 1 hour in forms | 1 minute |

## Failure modes & edge cases
- A daily 9am task can fire at 11pm after sleep; prompts should guard for time.
- Older app versions call this feature Routines, with differing forms.
- Create stays disabled until folder, and on some forms description, are given.

## Changes since the snapshot
- Feature did not exist in the snapshot. Not versioned in the CLI changelog.

## Open questions
- Task concurrency limit that produces the "other tasks already running" skip.
