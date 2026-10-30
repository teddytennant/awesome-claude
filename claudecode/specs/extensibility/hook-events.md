# Hook Events Reference

**Status:** shipped
**Provenance:** both (27 events in snapshot; 6 post-leak: `PostToolBatch`, `UserPromptExpansion`, `MessageDisplay`, `DirectoryAdded`, `PreModelSwitch`, `PostModelSwitch`)
**Sources:** docs `hooks`; snapshot `utils/hooks/`, `schemas/hooks.ts`; `comparison/hook-events.md`; changelog 2.1.89 to 2.1.314. Common mechanics are in [hooks.md](hooks.md).

## Purpose

Defines every hook event at v2.1.314: when it fires, what it matches on, payload fields, output it honours, and exit-2 effect.

## Behaviour

### Common payload

1. Every event MUST carry `session_id`, `transcript_path`, `cwd`, `hook_event_name`. `transcript_path` may lag the live conversation.
2. Conditional common fields: `prompt_id` (absent before first input); `scratchpad_dir` (v2.1.257); `permission_mode` (not on every event; never `"manual"`, which arrives as `"default"`); `effort.level` (events with tool-use context, on models with effort); `agent_id`, `agent_type`.
3. Only `SessionStart` can carry `model`. Model-switch events carry `from_model` and `to_model`.
4. Tool events on MCP tools MUST add `mcp_server: {name, source}`, on `PreToolUse`, `PermissionRequest`, `PostToolUse`, `PostToolUseFailure`, `PermissionDenied` (v2.1.274). Trust decisions SHOULD key on `source`.
5. `additionalContext` placement: conversation start (`SessionStart`, `SubagentStart`); alongside the prompt (`UserPromptSubmit`, `UserPromptExpansion`); next to the tool result (`PreToolUse`, `PostToolUse`, `PostToolUseFailure`, `PostToolBatch`); end of turn, continuing it (`Stop`, `SubagentStop`); next request (`PostModelSwitch`). Multiple hooks' values are all delivered.

### Handler-type support

| Types | Events |
| :- | :- |
| All five | `PermissionDenied`, `PostToolBatch`, `PostToolUse`, `PostToolUseFailure`, `PreToolUse`, `Stop`, `SubagentStop`, `TaskCompleted`, `TaskCreated`, `TeammateIdle`, `UserPromptExpansion`, `UserPromptSubmit` |
| All but `agent` | `PermissionRequest` |
| `command`, `http`, `mcp_tool` | `ConfigChange`, `CwdChanged`, `DirectoryAdded`, `Elicitation`, `ElicitationResult`, `FileChanged`, `InstructionsLoaded`, `MessageDisplay`, `Notification`, `PostCompact`, `PostModelSwitch`, `PreCompact`, `PreModelSwitch`, `SessionEnd`, `StopFailure`, `SubagentStart`, `WorktreeCreate`, `WorktreeRemove` |
| `command`, `mcp_tool` | `SessionStart`, `Setup` |

Per the docs, only `command` hooks run on `Setup`, as its `mcp_tool` hooks are always skipped.

### Prompt/agent `ok: false` handling

| Event | Effect |
| :- | :- |
| `Stop`, `SubagentStop` | Reason becomes the next instruction; `impossible: true` (prompt only) lets the stop proceed |
| `PreToolUse` | Denied; turn ends with a warning line by default; `continueOnBlock` returns it as a tool error |
| `PostToolUse` | Turn ends by default; `continueOnBlock` feeds it back |
| `PostToolBatch`, `UserPromptSubmit`, `UserPromptExpansion` | Turn ends with warning |
| `PostToolUseFailure`, `TaskCreated` | Tool error; turn continues |
| `TaskCompleted` | Tool error when marked during a turn; like `TeammateIdle` when a teammate stops |
| `TeammateIdle` | Teammate stops; `continueOnBlock` keeps it working |
| `PermissionRequest`, `PermissionDenied` | No effect |

## Configuration & interfaces

Column `2` means exit-2 effect. "Discards" means `systemMessage` and `continue` are ignored.

### Session

**`SessionStart`**: session begins or resumes. Matcher: `startup`, `resume`, `clear`, `compact`, `fork`. Payload: `source`; optional `model`, `agent_type`, `session_title`. On `resume` or `fork` with at least one prior response: `seconds_since_last_response`, `context_tokens`, `prompt_cache_likely_expired`, `estimated_cache_write_usd` (v2.1.251). Output: `additionalContext`, `initialUserMessage` (`-p` only; becomes the first turn), `sessionTitle` (startup, resume, fork), `watchPaths`, `reloadSkills` (v2.1.152). `2`: stderr shown to user as a notice. Runs in the background at launch and `/clear`: typing is possible, but the first response waits; `/resume` inside a session waits. `Esc` retrieves a waiting prompt (v2.1.271). After `/clear` or a switch, late output is dropped. A late-installing plugin's `initialUserMessage` and `sessionTitle` are ignored. Provides `CLAUDE_ENV_FILE`.

**`Setup`**: only `--init-only`, or `--init`/`--maintenance` with `-p`. Matcher and `trigger`: `init`, `maintenance`. Discards all JSON. `2`: ignored. `--init-only` also runs `SessionStart` with `startup`, then exits. Provides `CLAUDE_ENV_FILE`.

**`SessionEnd`**: session terminates. Matcher and `reason`: `clear`, `resume`, `logout`, `prompt_input_exit`, `other` (`bypass_permissions_disabled` removed in v2.1.234). Discards JSON. `2`: stderr to user. Budget 1.5 s total; per-hook `timeout` in settings raises it up to 60 s, but plugin timeouts do not. `CLAUDE_CODE_SESSIONEND_HOOKS_TIMEOUT_MS` overrides the budget and sets the default per hook (v2.1.268 for the latter).

**`InstructionsLoaded`**: a `CLAUDE.md` or `.claude/rules/*.md` loads, eagerly or lazily. Not fired for direct `AGENTS.md` reads; fired when imported (`include`) or symlinked. Matcher and `load_reason`: `session_start`, `nested_traversal`, `path_glob_match`, `include`, `compact`. Payload: `file_path`, `memory_type` (`User`, `Project`, `Local`, `Managed`), optional `globs`, `trigger_file_path`, `parent_file_path`. Async, no control, discards.

### Prompt

**`UserPromptSubmit`**: prompt submitted, and on self-started turns: session-scoped scheduled tasks, `/loop`, background subagent reports, cross-session messages. No matcher. Payload: `prompt` (literal command line, not expanded; pasted placeholders expanded and possibly wrapped in `<pasted_content>`), optional `session_title`. Output: `decision`, `reason` (user only, not context), `additionalContext`, `sessionTitle` (v2.1.94), `suppressOriginalPrompt`. `2`: blocks; stderr routes like `reason`. Runs before skill or command expansion, so a block also stops embedded `!` commands (v2.1.299). Block message includes `Original prompt:` unless suppressed; the text can still persist locally. `Esc` stops the check and returns typed text, unless a hook blocked at the same moment. Timeout discards output and the prompt proceeds, unless `onFailure: "block"`.

**`UserPromptExpansion`**: a user-typed command expands. Covers direct `/skill`, which bypasses `PreToolUse`. Matcher: `command_name`. Payload: `expansion_type` (`slash_command`, `mcp_prompt`), `command_name`, `command_args`, `command_source`, `prompt`. Output: `decision`, `reason`, `additionalContext`. `2`: blocks expansion.

**`MessageDisplay`** (v2.1.152): assistant text is displayed. No matcher; not fired for text-free messages. Payload: `turn_id`, `message_id` (not the API id), `index`, `final`, `delta`. Output: `displayContent` only; discards. Display-only: transcript, model and verbose view keep the original. Each batch is held until the hook returns; failure or timeout (default 10 s) shows the original. Interactive: once per batch of whole lines, final batch may be empty or mid-line. `-p`/SDK: one call with `index` 0, `final` true, full text. `2`: original shown.

### Tools

**`PreToolUse`**: tool parameters formed, before processing. Matcher: tool name; never `EndConversation`. Not fired for `@` file insertion (see `CLAUDE_CODE_DISABLE_FILE_MENTIONS`, v2.1.299). Payload: `tool_name`, `tool_input`, `tool_use_id`. File-tool paths are always absolute, native separators. `ExitPlanMode` input has `plan` and `planFilePath` injected; `allowedPrompts` is deprecated and ignored. `AskUserQuestion` accepts `answers` through `updatedInput`. Output under `hookSpecificOutput`: `permissionDecision` (`allow`, `deny`, `ask`, `defer`), `permissionDecisionReason`, `updatedInput` (whole-object replace; rules re-evaluated against it), `additionalContext`. Precedence `deny` > `defer` > `ask` > `allow`. Deprecated top-level `approve`/`block` map to `allow`/`deny`. `2`: blocks, stderr shown to model.

- `allow` skips prompts, but deny and ask rules still apply, as do actions no mode auto-approves, network-path reads, SDK `always_ask` tools, and MCP tools marked `_meta["anthropic/requiresUserInteraction"]`, which hooks cannot pre-approve.
- `AskUserQuestion` and `ExitPlanMode` need `allow` plus `updatedInput`.
- `ask` shows a source label: `[settings]`, `[plugin:<name>]`, `[skill]`. In auto mode it normally goes to the prompt; protected-path or sandbox-escape calls may be denied by the classifier first; `SubagentHandback` shows no prompt, and a `deny` tells the subagent to retry up to three times.
- `defer` works only in `-p`, on a single-tool turn. Otherwise it is ignored with a warning. Result: `stop_reason: "tool_deferred"` and `deferred_tool_use {id, name, input}`. Resuming refires the hook. A missing tool yields `tool_deferred_unavailable` with `is_error: true`. A prompt sent with or after a resume makes Claude Code answer without the result and drop the call. No timeout; retention is `cleanupPeriodDays`.

**`PermissionRequest`**: about to ask, or would auto-deny a call that cannot prompt. Not for sandbox network requests. Runs alongside `--permission-prompt-tool` and `canUseTool`; first to decide wins. Matcher: tool name. Payload: `tool_name`, `tool_input`, optional `mcp_server`, `permission_suggestions`; no `tool_use_id`. Output: `decision.behavior` (`allow`, `deny`), `updatedInput`, `updatedPermissions` (allow), `message`, `interrupt` (deny). `2`: not honoured, stderr discarded. In Cowork cloud sessions a `setMode` in an allow is ignored (v2.1.300).

Permission update entries: `addRules`, `replaceRules`, `removeRules` (`rules`, `behavior`, `destination`), `setMode` (`mode`, `destination`), `addDirectories`, `removeDirectories`. `destination`: `session`, `localSettings`, `projectSettings`, `userSettings`. `setMode` to `bypassPermissions` is a no-op unless bypass was available at launch, and is never persisted.

**`PostToolUse`**: tool succeeded. Matcher: tool name. Payload adds `tool_response` (structured tool output), `tool_use_id`, `duration_ms` (v2.1.119). Bash may carry `tool_response.bashEditDiff {changedFiles, files, moreFiles, unavailable, skipped, shared}` (v2.1.269, beta, best effort). Foreground `Agent` carries `status`, `agentId`, `content`, `resolvedModel`, `modelsUsed`, `totalTokens`, `totalDurationMs`, `totalToolUseCount`, `usage`; background carries `status: "async_launched"`, `agentId`, `description`, `prompt`, `outputFile`, `resolvedModel`. Output: `decision: "block"` plus `reason` (next to result, original stays), `additionalContext`, `updatedToolOutput` (v2.1.121; must match the tool's shape for built-ins, or is ignored; MCP unvalidated), `updatedMCPToolOutput` (legacy), `classifierContext` (v2.1.236). `2`: stderr to model.

`classifierContext` MUST be capped at 2,000 characters per call across hooks, ignored from async hooks, dropped on calls the classifier omits, and dropped if its paired rewrite fails. Treated as unverified, except for live in-process TypeScript SDK callbacks.

**`PostToolUseFailure`**: a started tool failed. Not for validation rejections or permission denials. Matcher: tool name. Payload: `tool_name`, `tool_input`, `tool_use_id`, `error`, optional `is_interrupt`, `duration_ms`. `error` is display text; key on `Exit code N`. User cancel does not fire. Output: `additionalContext`. `2`: stderr to model.

**`PostToolBatch`**: all calls in a batch resolved, before the next model call. No matcher. Payload: `tool_calls[]` of `{tool_name, tool_input, tool_use_id, tool_response}`, where `tool_response` is the serialized `tool_result` content, unlike `PostToolUse`. Output: `additionalContext`; `decision: "block"` or `continue: false` stops the loop. `2`: stops the loop, message visible as a warning and retained.

**`PermissionDenied`**: auto mode denies a call, including no-verdict denials. Not for manual denial, hook blocks, or deny rules. Matcher: tool name. Payload: `tool_name`, `tool_input`, `tool_use_id`, `reason`. Output: `hookSpecificOutput.retry: true` adds a may-retry note without reversing the denial; ignored for no-verdict denials. Prompt and agent hooks run here, but their output is discarded. `2`: ignored.

### Agents and tasks

**`SubagentStart`**: Agent tool spawn, subagent resume, and each new message to an in-process teammate. Matcher: agent type; plugin agents use `plugin:name`, so anchor with `^...$`. Payload: `agent_id`, `agent_type`. Output: `additionalContext` into the subagent; re-injected only if not already held. `2`: notice in the subagent's own transcript.

**`SubagentStop`**: subagent finished, including internal agents such as prompt suggestions and `/btw`, where `agent_type` is the session agent or empty. Payload: `stop_hook_active`, `agent_id`, `agent_type`, `agent_transcript_path`, `last_assistant_message` (not the handback report), `background_tasks`, `session_crons`. Output: as `Stop`; `reason` becomes the subagent's next instruction. Named matchers do not match an empty `agent_type`.

**`Stop`**: main agent finished. Not on user interrupt; API errors fire `StopFailure`. No matcher. Payload: `stop_hook_active`, `last_assistant_message`, `background_tasks[]` (`id`, `type`, `status`, `description`, optional `command`, `agent_type`, `server`, `tool`, `name`), `session_crons[]` (`id`, `schedule`, `recurring`, `prompt`) (v2.1.145). Output: `decision: "block"` with required `reason`; `additionalContext` continues as non-error feedback (v2.1.163). `2`: continues, stderr as explanation. Cap: 8 consecutive continuations, reset by a tool call; `CLAUDE_CODE_STOP_HOOK_BLOCK_CAP` overrides. `/goal` is a built-in session-scoped prompt Stop hook.

**`StopFailure`**: replaces `Stop` on an API-error end. Matcher and `error`: `rate_limit`, `overloaded`, `authentication_failed`, `oauth_org_not_allowed`, `account_on_hold`, `billing_error`, `invalid_request`, `model_not_found`, `server_error`, `max_output_tokens`, `cloud_credential_error` (v2.1.267), `unknown`. Payload adds `error_details`, `last_assistant_message` (the error string). Output ignored except `terminalSequence`.

**`TeammateIdle`**: teammate about to idle. No matcher. Payload: `teammate_name`, deprecated `team_name`, optional `agent_id` (v2.1.290). `2`: teammate continues with stderr feedback. `continue: false` stops it.

**`TaskCreated`**: `TaskCreate` running; not fired without Task tools. No matcher. Payload: `task_id`, `task_subject`, optional `task_description`, `teammate_name`, `team_name`, `agent_id`. `2` or `decision: "block"`: task deleted, message returned as tool error. `continue: false` ignored.

**`TaskCompleted`**: marked complete by `TaskUpdate`, or teammate finishes with in-progress tasks. No matcher. Same payload. `2`: stays open, stderr fed back. `continue: false` stops a finishing teammate; ignored when `TaskUpdate` triggered it.

### Environment

**`ConfigChange`**: settings, managed-file or skill file changes. Not fired for server-managed settings, macOS or Windows policy, or WSL-inherited policy polls. Matcher and `source`: `user_settings`, `project_settings`, `local_settings`, `policy_settings`, `skills`. Payload: optional `file_path`. `2` or `decision: "block"`: change not applied, except `policy_settings`. No message surfaces; only a debug line. Discards.

**`CwdChanged`**: a main-conversation shell command changes directory. No matcher. Payload: `old_cwd`, `new_cwd`. Output: `watchPaths` (replaces dynamic list; `[]` clears), `systemMessage` (terminal notification only). Provides `CLAUDE_ENV_FILE`, cleared at the next `CwdChanged`. `2`: stderr to user.

**`DirectoryAdded`** (v2.1.219): after `/add-dir` or SDK `register_repo_root`, once sandbox and permissions are refreshed. Not for `--add-dir`, the `/permissions` Workspace tab, or already covered paths. Matcher and `source`: `slash_command`, `register_repo_root`. Payload: `directory`. Background; hook commands run unsandboxed. `systemMessage` reaches the model next turn for `slash_command`, the debug log for `register_repo_root`. `2`: debug log.

**`FileChanged`**: watcher sees a change, whatever caused it. Matcher does double duty: split on `|` into literal filenames for the watch list, then filters on basename by standard rules. An omitted matcher matches all and adds no watches; `"*"` watches a file literally named `*`. Payload: `file_path`, `event` (`change`, `add`, `unlink`). Output: `watchPaths`, `systemMessage` as `CwdChanged`. The watcher starts only when something names a file. A hook rewriting its own file can loop. `2`: stderr to user.

**`WorktreeCreate`**: `--worktree`, `EnterWorktree`, `isolation: "worktree"`, workflow agents, background sessions, `claude remote-control` worktree mode. Not for Bash `git worktree add`, nor plugin hooks with `--worktree --tmux`. No matcher. Payload: `name`. Replaces git behaviour, so `.worktreeinclude` is unprocessed. Command hook prints the path as last non-empty stdout line, ANSI stripped; HTTP returns `hookSpecificOutput.worktreePath`. Any failure or missing path fails creation. Absolute paths with `.` or `..`, or symlinks below the repo root, are refused.

**`WorktreeRemove`**: cleanup of a hook-created worktree at interactive exit, unnamed clean session, background-session delete, `ExitWorktree`, or `remote-control` cleanup. Not after subagent or workflow agents. No matcher. Payload: `worktree_path`. Non-zero with the directory still present fails removal with no git fallback. No hook: git fallback for exit and `ExitWorktree`; `remote-control` keeps it. Branches are never deleted. JSON discarded. Change detection uses git, so non-git work looks clean.

**`Notification`**: matcher and `notification_type`: `permission_prompt`, `idle_prompt`, `auth_success`, `elicitation_dialog`, `elicitation_url_dialog`, `elicitation_complete`, `elicitation_response`, `agent_needs_input`, `agent_completed`, `quota_auto_resume_fired`, `quota_auto_resume_stale`, `quota_auto_resume_disabled` (v2.1.234), `plugin_notification`. Payload: `message`, optional `title`. Discards, but `terminalSequence` works. Fires regardless of `preferredNotifChannel`. Timing gates: about 6 s for prompts and elicitation dialogs, deferred by keystrokes; about 60 s for idle. `canUseTool` hosts time `permission_prompt` at 6 s without deferral (`CLAUDE_CODE_DISABLE_PERMISSION_PROMPT_NOTIFY_HOOKS` disables; fires since v2.1.233).

### Compaction and model

**`PreCompact`**: matcher and `trigger`: `manual`, `auto` (includes idle compaction). Payload: `custom_instructions`. `2` or `decision: "block"` blocks (v2.1.105). Proactive auto compaction is skipped; recovery compaction surfaces the context error. Discards.

**`PostCompact`**: matcher as above. Payload: `trigger`, `compact_summary`. No control; discards. `2`: stderr to user.

**`PreModelSwitch`** (v2.1.251): requested switches only (`/model`, pickers, `/config`, fast mode when it changes the model, SDK `set_model`, `apply_flag_settings`). Matcher: canonical name of the target, ignoring `[1m]`; unresolvable targets run every hook, so hooks SHOULD check `to_model`. Payload: `from_model`, `to_model`, `requested_model`, `source` (`command`, `picker`, `sdk`), `context_tokens`, `prompt_cache_warm`, `cache_ttl`, `estimated_cache_write_usd`, `pricing` (`configured`, `catalog`, `default`). Output: `permissionDecision` (`allow`, `deny`, `ask`), `permissionDecisionReason`, or `decision: "block"`; no `defer`, `updatedInput`, `additionalContext`. Precedence `deny` > `ask` > `allow`. `ask` works only for interactive `/model`; elsewhere it refuses. `allow` skips the warm-cache confirmation. `systemMessage` always shows. `2` and timeout block.

**`PostModelSwitch`** (v2.1.251): after any session model change, including fallback, `opusplan`, and restore on resume; not for one-turn fallback chains. Same payload and matcher; `source` adds `auto` and `resume`. Output: plain stdout or `additionalContext` on the next request. If unfinished 5 s after the next prompt, it goes on the following request. With several switches, only the last target's output is delivered. `2`: notice only.

### MCP elicitation

**`Elicitation`**: matcher: server name. Payload: `mcp_server_name`, `message`, optional `mode`, `url`, `elicitation_id`, `requested_schema`. Output on exit 0: `action` (`accept`, `decline`, `cancel`), `content`. No output leaves the dialog. `accept` on URL mode skips opening it. `2` or `decision: "block"` declines; block overrides `action`; a decline beats other hooks' answers. Reason never visible. Discards `reason`.

**`ElicitationResult`**: after a user responds, including decline or cancel. Not after a hook answered. Payload: `mcp_server_name`, `action`, optional `mode`, `elicitation_id`, `content`. Output: `action` plus `content` (replaces whole object); `action` is required or the output is ignored. `cancel` still sends submitted values; `decline` withholds them. Hooks can flip a decline to accept, so SHOULD check input `action`. `2` or `decision: "block"` blocks.

## Failure modes & edge cases

- `decision` from elicitation hooks was ignored from v2.1.105 until v2.1.284.
- `PostToolBatch.tool_response` and `PostToolUse.tool_response` differ in shape.
- `SubagentHandback` reports reach hooks through `tool_input.message`, not `last_assistant_message` (v2.1.271).

## Changes since the snapshot

- v2.1.89: `permissionDecision: "defer"`; `PermissionDenied` retry; `TaskCreated` documented.
- v2.1.94: `sessionTitle` on `UserPromptSubmit`.
- v2.1.105: `PreCompact` blocking.
- v2.1.119: `duration_ms`.
- v2.1.145: `background_tasks`, `session_crons`.
- v2.1.152: `MessageDisplay`; `reloadSkills`; `sessionTitle` on `SessionStart`.
- v2.1.163: `additionalContext` on `Stop`.
- v2.1.219: `DirectoryAdded`.
- v2.1.251: model-switch events; resume cost fields.
- v2.1.299: `UserPromptSubmit` ordering.

## Open questions

- Which events include `permission_mode` is only shown by per-event examples.
- `PostToolBatch` and `UserPromptExpansion` introduction versions are not in the changelog.
