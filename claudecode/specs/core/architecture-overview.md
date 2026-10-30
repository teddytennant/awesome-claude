# Architecture overview

**Status:** shipped
**Provenance:** both
**Sources:** docs how-claude-code-works, cli-reference, headless, env-vars, third-party-integrations; snapshot `entrypoints/cli.tsx`, `entrypoints/init.ts`, `main.tsx`, `setup.ts`, `bootstrap/state.ts`, `query.ts`, `QueryEngine.ts`, `replLauncher.tsx`; changelog 2.1.243, 2.1.277, 2.1.281, 2.1.283, 2.1.290, 2.1.311

## Purpose

Claude Code is a local agent harness: one CLI process wraps a Claude model with tools, context management, permissions and persistence. The same agentic loop runs behind every surface (terminal, IDE extensions, desktop app, cloud sessions, Remote Control, Slack, CI, Agent SDK). This spec fixes the process model and startup order. Boot modes are in [boot-modes.md](boot-modes.md); the loop is in [query-loop.md](query-loop.md).

## Behaviour

### Layers

1. The product MUST be structured as these layers, from outside in: launcher (fast-path dispatch), CLI (flag parsing and session setup), surface (interactive TUI, or the headless printer), session engine (one conversation), agentic loop, API client, tools.
2. Interactive and headless surfaces MUST share the agentic loop. A surface may only differ in how it renders events and answers prompts.
3. Other surfaces that "wrap" Claude Code (desktop, VS Code, cloud sessions, Agent SDK) MUST talk to a `claude` process rather than reimplement the loop. Errors the wrapper itself prints are the only exception (see [errors-catalogue-local.md](errors-catalogue-local.md)).
4. Three execution environments exist: local (default), cloud (Anthropic-managed VM or a self-hosted environment), Remote Control (code runs locally, driven from a browser or phone). The loop and tools are the same in all three.

### Process model

5. A session is one OS process with a single main conversation. Parallelism inside it comes from concurrent tools, subagents (in-process, own context window), background tasks and, where enabled, teammates in separate processes.
6. Background sessions (`--bg`, `claude agents`) run under a background service, each with its own terminal host process. See the agents spec area.
7. Processes that spawn children MUST mark them so nested interactive sessions are detected (`CLAUDE_CODE_CHILD_SESSION`, which turns transcript saving off when inherited).
8. Multiple processes share `~/.claude` state, so login refresh and settings writes MUST tolerate concurrent processes. A process that loses the refresh race reports that another process is refreshing rather than treating the login as rejected.
9. `SIGTERM` in print or SDK mode MUST terminate running commands and exit with code 143, without recording an interrupted turn or synthetic tool denials (since 2.1.236).

### Entrypoint dispatch (launcher)

10. The launcher MUST inspect raw argv before loading the full CLI, so cheap paths stay cheap. All heavy modules load dynamically.
11. `--version`/`-v` as the only argument MUST print the version with no further module loading.
12. Before full CLI load the launcher dispatches to dedicated paths: browser-integration and computer-use MCP server helpers, background-session management, `remote-control`, runners for self-hosted environments, `--worktree --tmux` (which execs into tmux), and `--update`.
13. `--bare` MUST be detected at this stage and set `CLAUDE_CODE_SIMPLE=1`, so code that reads the variable at module load sees it.
14. Launches whose only arguments are options and their values SHOULD skip subcommand registration (2.1.243, 2.1.311).
15. `claude -p` and Claude Code Remote MUST NOT load the interactive UI (2.1.283).

Snapshot-only dispatch paths for daemon workers, templates and an internal prompt-dump flag existed behind build gates and are not publicly documented.

### Startup order (full CLI)

The order below comes from the snapshot, updated by later changelog entries where noted. The exact current order is an open question.

16. Mode detection: the session is non-interactive when `-p`/`--print` or `--init-only` is present, when an SDK URL is given, or when stdout is not a TTY. The mode MUST be decided before `init()` runs, because `init` and settings handling depend on it.
17. Early settings: `--settings` and `--setting-sources` MUST be applied before anything reads settings.
18. `init()` runs once, on a pre-action hook, only if a command actually executes (so `--help` stays cheap). It enables config, applies only the environment variables that are safe before trust, applies extra CA certificates, sets up graceful shutdown, starts telemetry plumbing, begins loading server-managed settings and policy limits with a timeout, configures mTLS and proxy, and creates the scratchpad and temp directories.
19. Migrations MUST run before the session reads migrated values, and remote settings loading continues in the background.
20. The main action resolves prompts, flags, tools, the working directory and `setup()` (worktree creation, tmux, message socket, background prefetches).
21. Interactive only: `showSetupScreens` runs onboarding, the workspace trust dialog and approvals. Settings and hook execution that need trust MUST wait until trust is established.
22. Headless skips the trust dialog. Documented consequence: without `--bare`, `-p` runs project hooks and connects `.mcp.json` servers even in an untrusted folder, so users must only run `-p` where they trust the content. Settings files that fail validation are silently ignored in this mode.
23. MCP servers connect. The headless first turn waits a bounded time for servers (`CLAUDE_CODE_MCP_STARTUP_WAIT_MS`). It still waits up to 2 seconds for servers named by `--allowedTools` or an `mcp_tool` hook, even when that variable is `0` (2.1.284).
24. `startDeferredPrefetches` starts background work once it cannot compete with first paint. It MUST be skipped entirely in bare mode.
25. The surface starts: `launchRepl` for interactive, `runHeadless` for print and SDK.

### Startup performance requirements

26. Sandbox and MCP bring-up MUST NOT block the first frame (2.1.243).
27. Git reads, startup telemetry and third-party model-upgrade checks MUST NOT run before the first frame (2.1.281).
28. In SDK and headless use, the first turn MUST NOT wait on the per-directory CLAUDE.md lookup (2.1.277).
29. Auto-mode classifier rules and the Artifact tool load on first use rather than at launch (2.1.283).
30. `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` also skips the startup connection warm-up (2.1.290).

### Providers

31. A session selects exactly one API provider: Anthropic API (subscription login, Console login or API key), Amazon Bedrock, Bedrock Mantle, Google Cloud's Agent Platform (formerly Vertex AI), Microsoft Foundry, Claude Platform on AWS, a custom `ANTHROPIC_BASE_URL` (LLM gateway) or a Claude apps gateway.
32. The managed `allowedProviders` list MUST refuse a disallowed provider at startup, at login, and on the next API contact.
33. Sessions on third-party providers and Claude apps gateway sessions do not fetch feature flags unless a host platform arranges it. Any feature that needs a fetched flag MUST degrade to its code default there.

### Persistence

34. Each message, tool use and result MUST be appended to a JSONL transcript under `~/.claude/projects/`, which backs rewind, resume and fork. File snapshots taken before edits back checkpoint restore.
35. Sessions are independent. A new session has a fresh context window, and only CLAUDE.md and auto memory carry across.
36. Since 2.1.300, transcripts also record each API request's system prompt, tools and parameters.

## Configuration & interfaces

| Item | Effect |
| - | - |
| `-p`, `--print` | Headless surface |
| `--bare`, `--restricted`, `--safe-mode` | Boot modes, see [boot-modes.md](boot-modes.md) |
| `--init`, `--init-only` | Run Setup hooks before the session, or run Setup and `SessionStart` hooks then exit |
| `--setting-sources`, `--settings` | Limit or add setting sources |
| `CLAUDE_CODE_USE_BEDROCK`, `_VERTEX`, `_FOUNDRY`, `_MANTLE`, `_ANTHROPIC_AWS` | Provider selection |
| `CLAUDE_CODE_PROVIDER_MANAGED_BY_HOST` | Host owns routing; provider and auth variables in settings files are ignored |
| `CLAUDE_CODE_MCP_STARTUP_WAIT_MS` | First-turn MCP wait in headless mode |

Subcommands in 2.1.314 help: `agents`, `attach`, `auth`, `auto-mode`, `doctor`, `gateway`, `import`, `install`, `logs`, `mcp`, `plugin`, `purge`, `respawn`, `rm`, `setup-token`, `stop`/`kill`, `ultrareview`, `update`/`upgrade`.

## Failure modes & edge cases

- Bare `claude` with stdout redirected needs input and fails with `Input must be provided when using --print`.
- `claude` without `-p` with a non-TTY stdin reports that it cannot read the keyboard.
- A deleted working directory, or an unusable private temp directory, stops startup with a specific error.
- A mistyped subcommand prints the nearest match and exits without starting a session.
- Unparseable or unreadable managed settings exit at startup with code 1.

## Changes since the snapshot

- 2.1.243: sandbox and MCP bring-up stop blocking the first frame; bare launches skip subcommand registration.
- 2.1.248: `--restricted` added.
- 2.1.277: headless first turn stops waiting on the per-directory CLAUDE.md lookup.
- 2.1.281: git reads, telemetry and third-party model checks move after the first frame.
- 2.1.283: `-p` and Remote stop loading the interactive UI.
- 2.1.285: `allowedProviders` added.
- 2.1.311: faster startup for option-only launches.
- Bedrock, Mantle, Vertex and Foundry load model settings from a signed downloaded catalog from 2.1.311 (`CLAUDE_CODE_MODEL_CATALOG=off` disables it).

## Open questions

- The current order of `init()` steps is known only from the snapshot plus the changelog entries above.
- Whether the launcher fast paths in the snapshot other than those in current help still exist.
