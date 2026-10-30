# Interaction and Planning Tools

**Status:** shipped
**Provenance:** both
**Sources:** docs `tools-reference` (AskUserQuestion, Task tool availability), `permission-modes`, `hooks`, `settings-reference`, `interactive-mode`, `sub-agents`, `agent-sdk/typescript`; snapshot `tools/AskUserQuestionTool`, `EnterPlanModeTool`, `ExitPlanModeTool`, `TodoWriteTool`, `TaskCreateTool`, `TaskGetTool`, `TaskListTool`, `TaskUpdateTool`; changelog 2.1.200, 2.1.205, 2.1.218, 2.1.233, 2.1.268

## Purpose

Tools for pausing to ask the user, for separating planning from editing, and for tracking multi-step work. The task-tracking tools have moved from always-on to a default-off feature on newer models.

## Behaviour

### AskUserQuestion

1. Input: `questions` (one to four), each with `question`, `header`, `options` and `multiSelect`. Each option has `label`, `description`, optional `preview`. Also `answers`, `annotations`, `metadata`.
2. Option count is two to four, and question text and option labels are unique, per the snapshot schema. Confirm against current behaviour.
3. Answers are chosen by option, by typed text through the `Other` row, or in the notes field.
4. A typed answer MUST be relayed in neutral wording so Claude follows it, including a request to wait or explain first (2.1.216).
5. `answers` is not set by Claude. A hook or SDK caller supplies it through `updatedInput` to answer programmatically. Multi-select answers join labels with commas.
6. Dialogs MUST stay open until answered by default (2.1.200). `askUserQuestionTimeout` of `60s`, `5m` or `10m` opts into an idle timeout, in user settings or `/config`.
7. On timeout the dialog submits any selected options and tells Claude the user may be away, so it proceeds on judgment and can re-ask later. A countdown shows for the last 20 seconds, any key restarts the timer, and the timer does not count while the terminal reports its window focused.
8. The timer MUST NOT start in a background session, in screen reader mode, or while connected to Remote Control. Permission prompts, including plan approval, never auto-resolve.
9. Subagents never get this tool. In auto mode, answers count as intent signal for the classifier (2.1.147).

### Plan mode

10. Plan mode makes Claude research and propose without editing source. Edits stay blocked until approval, except in interactive terminal sessions with bypass permissions available, where the blocks are not enforced but Claude is still told to plan. A one-time note says so (2.1.299). Non-interactive surfaces keep the blocks.
11. Shell commands during planning follow the first matching case:
    - Interactive terminal with bypass available: neither classifier nor prompt.
    - Auto mode available and `useAutoModeDuringPlan` on (default): classifier reviews commands other than critical-path removals (2.1.218).
    - Otherwise: commands outside the read-only set prompt, even with sandbox auto-allow.
12. Entry: `Shift+Tab`, `/plan [description]`, `--permission-mode plan`, `defaultMode: "plan"`, or `EnterPlanMode`. VS Code conversations use `claudeCode.initialPermissionMode`.
13. `Shift+Tab` leaves plan mode without approving.

### EnterPlanMode

14. Input is empty. Output is a confirmation `message`.
15. It MUST NOT run in subagents. The tool table marks it as not requiring permission.

### ExitPlanMode

16. Claude writes the plan to a file first, so the model's `tool_input` is typically empty. Claude Code injects `plan` and `planFilePath` before hooks run. In PostToolUse, `tool_response` has `plan` and `filePath`.
17. `allowedPrompts` is deprecated and ignored, and accepted for validation only (before v2.1.205 it requested prompt-based Bash permissions).
18. It presents the plan for approval:
    - **Yes, and use auto mode.** Reads **Yes, auto-accept edits** when auto is unavailable, or the bypass wording when started with bypass enabled.
    - **Yes, manually approve edits.**
    - **No, keep planning.**
    - With `showClearContextOnPlanAccept`, a first option also clears planning context.
19. Approval exits plan mode and switches to the mode that option describes. `Ctrl+G` opens the plan for editing first, reported as `planWasEdited`. Accepting also titles an unnamed session from the plan.
20. Plan files default to `~/.claude/plans`, or `plansDirectory` relative to the project root. They are writable during planning.
21. A subagent gets the tool only when its `permissionMode` is `plan`.
22. Snapshot, and consistent with output fields `awaitingLeaderApproval` and `requestId`: a teammate required to plan sends the plan to the team lead for approval and needs the plan file present. Other teammates exit locally. A call outside plan mode is rejected before the dialog.

### Task tracking availability

23. Provided by default only on Opus 4.7, Sonnet 4.6, Haiku 4.5 and earlier (v2.1.268+). Every other model, including unrecognised IDs such as gateway model names, MUST NOT get them unless opted in. On those models Claude adds nothing to the task list.
24. Opt-ins: `CLAUDE_CODE_ENABLE_TODO_TOOLS=1` exported before start, on every model and provider; naming a tool in `--allowedTools`; listing tools in `--tools`; the matching SDK options.
25. Background sessions and cloud sessions provide the tools on every model.
26. Wherever available, the session gets the four Task tools, or `TodoWrite` instead with `CLAUDE_CODE_ENABLE_TASKS=0`.
27. Subagents have them only when the session does, whatever model they run. In-process teammates follow the session. A split-pane teammate inherits `--tools` and deny rules but not `--allowedTools` or an exported variable, so `--settings '{"env":...}'` is needed to pass the switch.
28. Without them, agents coordinate through messages rather than the shared task list.

### TaskCreate, TaskGet, TaskList, TaskUpdate

29. `TaskCreate`: `subject`, `description`, optional `activeForm`, `metadata`. Returns `task: {id, subject}`. Malformed input is repaired where possible (2.1.169).
30. `TaskUpdate`: `taskId` plus optional `status` (`pending`, `in_progress`, `completed`, `deleted`), `subject`, `description`, `activeForm`, `addBlocks`, `addBlockedBy`, `owner`, `metadata`. `deleted` removes the task. Returns `success`, `taskId`, `updatedFields`, optional `error`, `statusChange`.
31. `TaskGet`: `taskId`; returns the record with `blocks` and `blockedBy`, or `null`.
32. `TaskList`: empty input; returns `id`, `subject`, `status`, optional `owner`, `blockedBy`, sorted by ID (2.1.119).
33. `TaskCreated` and `TaskCompleted` hooks fire around these operations and can block (see `hooks`).
34. Snapshot detail: a teammate marking a task in progress with no owner becomes owner. Not separately documented today.
35. Storage is under `~/.claude/tasks/`. `CLAUDE_CODE_TASK_LIST_ID` names a shared directory, so several instances coordinate on one list.
36. Tasks persist across compaction. `Ctrl+T` toggles the view, showing up to five; an expanded view is restored on resume when tasks remain.

### TodoWrite

37. Input `todos`, each with `content`, `status`, `activeForm`. Returns `oldTodos`, `newTodos`. The legacy single-list form of task tracking, off by default.
38. Snapshot detail: a call completing every item clears the stored list, and closing three or more items with no verification item adds a reminder. Unconfirmed as current.

## Configuration & interfaces

| Key | Effect |
| :- | :- |
| `askUserQuestionTimeout` | Idle auto-continue; user or managed |
| `useAutoModeDuringPlan` | Classifier during planning; default on |
| `plansDirectory` | Plan file location |
| `showClearContextOnPlanAccept` | Clear-context approval option |
| `CLAUDE_CODE_ENABLE_TODO_TOOLS` | Opt in on all models (v2.1.233+) |
| `CLAUDE_CODE_ENABLE_TASKS` | `0` selects `TodoWrite` |
| `CLAUDE_CODE_TASK_LIST_ID` | Shared list |
| `CLAUDE_CODE_DISABLE_EXPLORE_PLAN_AGENTS` | Plan mode reads files directly |

Hooks see `AskUserQuestion` and `ExitPlanMode` fields through `tool_input` (`hooks` reference). Artifact publishing and some artifact reads ask in plan mode; see [post-leak-artifact](post-leak-artifact.md).

## Failure modes & edge cases

- The task list stays empty on newer models, and `Ctrl+T` then has no visible effect.
- An unrecognised custom model ID behaves as "newer", so gateway users lose the tools silently.
- `BUILTIN_TOOL_NAMES` lists `TodoWrite` regardless of availability.
- Hooks previously saw a stale plan when it was written in the same response as `ExitPlanMode` (fixed 2.1.285).
- `--permission-mode` was ignored resuming a plan session with `-p` (fixed 2.1.132).

## Changes since the snapshot

- 2.1.101: Ultraplan refine option hidden when unreachable.
- 2.1.147: AskUserQuestion answers inform the classifier.
- 2.1.169: TaskCreate input repair.
- 2.1.200: no auto-continue by default.
- v2.1.205: `allowedPrompts` ignored.
- 2.1.216: neutral wording for typed answers.
- 2.1.218: plan mode with auto uses the classifier.
- 2.1.233: task tools withdrawn from Opus 4.8, Sonnet 5, Fable 5, Mythos 5 and newer; `CLAUDE_CODE_ENABLE_TODO_TOOLS`.
- 2.1.268: narrowed to Claude 3.x, Opus 4.0 to 4.7, Sonnet 4.0 to 4.6, Haiku 4.5.
- 2.1.286: foreground subagents no longer miss task tools.
- 2.1.299: note when plan mode is not enforced.

## Open questions

- Whether the snapshot's `--channels` gate disabling plan tools and AskUserQuestion remains.
- The current validation limits on options and uniqueness.
- Whether `metadata` on AskUserQuestion has any user-visible effect.
- Whether the `TodoWrite` clearing and verification-reminder logic survives.
