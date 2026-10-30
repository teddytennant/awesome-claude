# Cloud Scheduled Tasks (Routines)
**Status:** preview (research preview)
**Provenance:** both (`/schedule` skill and `RemoteTrigger` tool in snapshot, gated; public launch reported in the 2026 week 16 digest; renamed "scheduled tasks")
**Sources:** docs `routines.md`, `scheduled-tasks.md`, `desktop-scheduled-tasks.md`; snapshot `skills/bundled/scheduleRemoteAgents.ts`, `tools/RemoteTriggerTool/`; changelog 2.1.139 to 2.1.314

## Purpose
A saved Claude Code configuration (prompt, repositories, connectors, environment, model, triggers) that runs as a cloud session without the user's machine. See [desktop-scheduled-tasks.md](desktop-scheduled-tasks.md) for local tasks.

## Behaviour

### Availability
1. Pro, Max, Team and Enterprise. Owners can turn it off with **Scheduled tasks (Was Routines)** at Organization settings, Capabilities, Remote sessions, which stops existing tasks. Custom roles need the scheduled tasks permission.
2. `/schedule` (alias `/routines`) MUST need a claude.ai subscription login, and MUST be unavailable with Console API keys, profiles, cloud providers, inside cloud sessions, or when cloud sessions are off. Also disabled when `ANTHROPIC_API_KEY`, `apiKeyHelper` or `ANTHROPIC_AUTH_TOKEN` is set (2.1.139).

### Definition
3. A task MUST have a name, prompt, and at least one trigger. It may have several, of mixed kinds.
4. A task without a schedule trigger has no next run time.
5. Repositories are cloned on each run from the default branch, unless the prompt says otherwise. For a PR event on the first repository, it starts at the PR head.
6. Claude pushes to `claude/`-prefixed branches by default. Branch protection is the control.
7. All connected connectors are included by default, and included ones can write. Local `claude mcp add` servers aren't connectors; a single-repo task may use a committed `.mcp.json`. `/schedule` explains this when none attach (2.1.251).
8. Model and effort are selected per task (2.1.312).
9. A dialog task without repository or event or API trigger is a claude.ai chat task, not a Claude Code one.
10. The saved prompt MUST be treated as the session's assignment, since it was stored in advance, but MUST NOT act as approval for prompts that need a live answer.

### Triggers
11. **Schedule:** the minimum interval is 1 hour, and more frequent cron is rejected. Presets take local time. Custom cron with five fields is UTC, unless a `CRON_TZ=` prefix is present. Runs on the exact hour may start minutes late, so new schedules default to a few minutes past (2.1.283).
12. **One-off:** a single timestamp; afterwards the task turns off and is marked Completed. It can be re-armed from the edit dialog.
13. **API:** a per-task Fire URL and bearer token, shown once, added only on the web. POST starts a session. Regenerate and Delete take effect immediately.
14. API `text` body MUST arrive wrapped in a `<routine-fire-payload>` block labelled untrusted, so the saved prompt must opt in to act on it.
15. Response: `type: routine_fire`, `claude_code_session_id`, `claude_code_session_url`. Beta header `experimental-cc-routine-2026-04-01`. The endpoint is for claude.ai users only.
16. **GitHub:** needs the Claude GitHub App (not just `/web-setup`). Events: pull request, release, issue, by category or action, such as `pull_request.opened`. CLI attach since 2.1.225.
17. Each event starts a new session; sessions are not reused.
18. PR filters on Author, Title, Body, Base branch, Head branch, Labels, Is draft, Is merged, with equals, contains, starts with, is one of, is not one of, matches regex. All must match. Regex tests the whole value.
19. Events above per-task and per-account hourly caps MUST be dropped.

### Runs
20. Each run is a full, new session, which users can open, continue, and archive.
21. History states: Failed (**Error**), Cancelled, Succeeded. These describe how the session ended, not task success. Archiving a succeeded run's session makes it Cancelled.
22. New sessions start in auto mode where available. Runs stop for ask rules, or repeated blocks, until answered. Unavailable auto mode keeps the launch mode.
23. A run in a project may continue a thread, keeping its mode.
24. Artifact rules: scheduled and Run now runs publish new private artifacts, and update or save to artifacts the user can edit, without asking (2.1.275, 2.1.292, 2.1.295). Public artifacts, requests for connectors, and deletes still ask.
25. `/recap` declines when relayed from a routine or webhook (2.1.284).
26. Runs that are late display "Due" with the scheduled time (2.1.286).

### Management
27. `/schedule list`, `update`, `run`; history questions read run logs.
28. The page has Yours and Templates tabs (2.1.271), an on/off switch, Run now, and run history beside settings (2.1.273). "Discard unsaved changes?" guards edits.
29. A banner says why the last run didn't start (2.1.302). "The last run" warnings cover org concurrency limit, missing environment, blocked access, temporary issues, missing repo or branch, rejected settings, usage limit, and failure.
30. Missing or expired GitHub connection MUST skip runs and retry up to 72 hours, then turn the task off (2.1.274).
31. Paused subscriptions hold tasks, and the user re-enables them (2.1.274).
32. Deleting a self-hosted environment turns its routines off at once with a reason (2.1.299).
33. An archived or unavailable environment shows **Unavailable environment** in Edit.

### Usage
34. Runs draw on subscription usage like interactive sessions, with usage credits as overflow where enabled.
35. Hourly product limits: 100 scheduled runs per account (waits); 30 per task across Run now, API, and re-arm; 100 per account each for Run now and API fires (fails). No overage on these.

## Configuration & interfaces
| Item | Value |
|---|---|
| Web | `claude.ai/code/routines` |
| CLI | `/schedule [text]`, `/routines` |
| Non-matching host | `403`, `x-deny-reason: host_not_allowed` |

Environment rules are as in [cloud-sessions.md](cloud-sessions.md). Claude Tag routines are in [slack-and-claude-tag.md](slack-and-claude-tag.md).

## Failure modes & edge cases
- `/schedule` hidden: `Unknown command` unless the cause has its own message (2.1.268).
- A run reported as "The last run failed" has no session to open.
- Asking Claude to change a routine it didn't create links to the routine's page (2.1.275).
- Self-hosted routed runs call the API from the org's network, unaffected by IP allowlist.

## Changes since the snapshot
- 2.1.139: disabled with API key style auth. 2.1.225: CLI GitHub triggers. 2.1.227: Owner toggle honoured in CLI.
- 2.1.251: MCP explanation. 2.1.268: better `/schedule` messages.
- 2.1.271, 2.1.273: page redesign. 2.1.274: 72-hour retry, pause notice. 2.1.275: startup notice removed; link for others' routines.
- 2.1.282: faster list. 2.1.283: default schedule offset. 2.1.286: "Due". 2.1.302: start failure banner.
- 2.1.312: effort. 2.1.314: Include completed button on the Scheduled tasks page.

## Open questions
- Exact GitHub event caps.
- Field limits and error set for `/fire`; external reference.
