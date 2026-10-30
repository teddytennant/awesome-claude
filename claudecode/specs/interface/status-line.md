# Status line

**Status:** shipped
**Provenance:** both
**Sources:** docs `statusline`, `settings-reference`, `hooks`; snapshot `components/StatusLine.tsx`, `commands/statusline.tsx`, `utils/hooks.ts`; changelog 2.1.97 through 2.1.293

## Purpose

Run a user command that receives session data as JSON and prints a persistent row or rows under the prompt. No tokens are consumed. A sibling command, `subagentStatusLine`, rewrites rows in the agent panel.

## Behaviour

### Setup

1. Configured with `statusLine` in settings: `type: "command"` and a `command` run in a shell.
2. `/statusline <description>` asks Claude to generate a script under `~/.claude/` and update settings. With no argument it derives one from the shell prompt. It can also remove the setting. File edits still go through permission prompts.
3. `padding` adds extra horizontal characters on top of built-in spacing. `refreshInterval` (seconds, minimum 1) re-runs the command on a timer as well as on events. `hideVimModeIndicator` hides the built-in mode text.

### Placement

4. Renders in its own row above footer badges and does not replace them.
5. With a custom status line, most footer hints MUST hide: `esc to interrupt`, `? for shortcuts`, `hold space to speak`.
6. It hides during some interactions, including the help menu and permission prompts.
7. A workspace must be trusted for it to run (snapshot `checkHasTrustDialogAccepted`; docs section `Workspace trust required`).

### When it runs

8. On session start and resume; on each new assistant message; when `/compact` finishes; on permission mode change; on vim mode toggle; on a change to the `command`; on the `refreshInterval` timer; when a rate-limit window in the last payload reaches `resets_at`; when a warm cache reaches `expires_at`.
9. Updates debounce at 300 ms. A `command` change skips debounce.
10. A new trigger cancels an in-flight run.
11. Edits to the script take effect at the next trigger.

### Output

12. Each stdout line is one row. ANSI colours and OSC 8 links are honoured.
13. Output is captured, so width detection inside the script fails. `COLUMNS` and `LINES` MUST be set in the environment (2.1.153).
14. stderr appears in `--debug` on every run, and the exit code on the first run. `CLAUDE_CODE_DEBUG_LOG_LEVEL=verbose` logs full command output.
15. `CLAUDE_CODE_CHILD_SESSION=1` is set in the child.

### Windows

16. Runs through Git Bash when installed, otherwise PowerShell. Paths need forward slashes under Git Bash; `~` expands to home.

### Gates

17. With `allowManagedHooksOnly`, or `disableAllHooks` outside managed settings, only a `statusLine` from managed settings runs. Otherwise it disappears silently.
18. `--safe-mode` skips non-policy status lines.

## Configuration & interfaces

### Input fields

| Field | Notes |
|---|---|
| `session_id`, `session_name`, `prompt_id`, `transcript_path`, `version` | `session_name` is custom or AI title only; `prompt_id` matches OTel `prompt.id` |
| `model.id`, `model.display_name` | |
| `cwd`, `workspace.current_dir`, `workspace.project_dir`, `workspace.added_dirs` | |
| `workspace.git_worktree` | Linked worktree name |
| `workspace.repo.host/owner/name` | From `origin`; `owner` holds GitLab namespaces (2.1.260) |
| `cost.total_cost_usd` | Client-side estimate; `modelPricing` applies; 0 after `/clear` |
| `cost.total_duration_ms`, `total_api_duration_ms`, `total_lines_added`, `total_lines_removed` | Duration accumulates across resumes |
| `context_window.total_input_tokens`, `total_output_tokens`, `context_window_size` | |
| `context_window.used_percentage`, `remaining_percentage` | Input tokens only; may be null early |
| `context_window.current_usage` | `input_tokens`, `output_tokens`, cache fields; null before first call and after `/compact` |
| `exceeds_200k_tokens` | Fixed threshold |
| `fast_mode`, `thinking.enabled`, `effort.level` | `effort` absent if unsupported; shows the session level, not skill or subagent |
| `rate_limits.five_hour`, `.seven_day` | `used_percentage`, `resets_at`; Pro and Max; dropped once reset |
| `rate_limits.spend_limit` | Gateway only (2.1.251): `used_percentage`, `resets_at`; and `used_usd`, `limit_usd`, `period` (`daily`, `weekly`, `monthly`, 2.1.284), about 5 minutes staler |
| `prompt_cache` | Absent until first response; see below |
| `output_style.name`, `vim.mode`, `agent.name` | |
| `pr.number`, `pr.url`, `pr.review_state`, `pr.kind` | GitHub, or GitLab MR with `kind: "mr"` |
| `worktree.name/path/branch/original_cwd/original_branch` | Worktree sessions only |

`prompt_cache` (2.1.251), main conversation only: `warm`, `caching_observed`, `ttl` (`5m` or `1h`), `expires_at`, `requests`, `misses`, `expected_rebuilds`, `hit_ratio`, `cache_write_tokens`, `miss_recache_tokens`, `last_miss_at`, `last_miss_cause` (with `causes`, plus `tools_added`, `tools_removed`, `system_char_delta`; 2.1.260), `miss_causes`, `recache_tokens_if_cold`.

A miss is a request re-processing over 5% and at least 2,000 tokens of cacheable content with no compaction or clearing to explain it.

### subagentStatusLine

- Receives base hook fields, `columns`, and `tasks[]`: `id`, `name`, `type` (`local_agent`), `agentType` (2.1.293), `status`, `description`, `label`, `startTime`, `model`, `effort`, `contextWindowSize`, `tokenCount`, `tokenSamples` (last 16), `cwd`.
- Writes one JSON line per overridden row: `{"id", "content"}`. Omit to keep default; empty content hides.
- Same trust and managed gates, though plugin defaults do not run under `allowManagedHooksOnly`, even when force-enabled.

## Failure modes & edge cases

- `/context` can read higher than `used_percentage`, because it estimates messages since the last response.
- Slow scripts lag; cache `git status`.
- Scripts must treat many fields as absent or null.
- Terminal.app has no OSC 8. SSH or tmux may strip it. `FORCE_HYPERLINK` overrides detection.
- Multi-line output has limited width and may truncate or wrap.

## Changes since the snapshot

- 2.1.97: `refreshInterval`.
- 2.1.145: repo and PR data.
- 2.1.153: `COLUMNS`, `LINES`.
- 2.1.234: GitLab MR data.
- 2.1.251: `prompt_cache`, `spend_limit`. 2.1.260: miss causes. 2.1.284: spend dollar fields.
- `subagentStatusLine` gained `effort` and `agentType` (2.1.293).
- Cost figures gained the data-residency premium (2.1.239).

## Open questions

- Timeout on a hung script.
- Whether `hideVimModeIndicator` and `padding` were in the snapshot-era schema.
- Exact interactions that hide the row, beyond the two named.
- 2.1.169 fixed footer hints such as `esc to interrupt` not showing with a custom status line, yet current docs say those hints stop. The doc is followed here; the conflict is unresolved.
