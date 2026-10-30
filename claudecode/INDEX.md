# Spec index


## Core runtime

| Spec | Status | Provenance |
|---|---|---|
| [Advisor](specs/core/advisor.md) | preview (experimental) | both |
| [API client: streaming, retries and error classes](specs/core/api-client.md) | shipped | both |
| [Architecture overview](specs/core/architecture-overview.md) | shipped | both |
| [Boot modes](specs/core/boot-modes.md) | shipped | both |
| [Context window sizing and auto-compact window](specs/core/context-window-sizing.md) | shipped | both |
| [Effort and thinking controls](specs/core/effort-and-thinking.md) | shipped | both |
| [Errors catalogue: API, usage, auth, network, request](specs/core/errors-catalogue-api.md) | shipped | both |
| [Errors catalogue: local, tool, session and configuration](specs/core/errors-catalogue-local.md) | shipped | both |
| [Fast mode](specs/core/fast-mode.md) | shipped (Opus 5 | both |
| [Model fallback](specs/core/model-fallback.md) | shipped | both (single `--fallback-model` predates the leak; chains and content  |
| [Model restrictions and organization defaults](specs/core/model-restrictions.md) | shipped | both (`availableModels` predates the leak; all else post-leak) |
| [Model selection, aliases and picker](specs/core/model-selection.md) | shipped | both |
| [Prompt caching](specs/core/prompt-caching.md) | shipped | both |
| [Agentic query loop and turn lifecycle](specs/core/query-loop.md) | shipped | both |
| [Request shaping: thinking, effort, 1M context and betas](specs/core/request-shaping.md) | shipped | both |
| [System prompt and context assembly](specs/core/system-prompt-and-context.md) | shipped | both |
| [Token and cost tracking, /usage](specs/core/token-cost-usage.md) | shipped | both |
| [Tool system contract](specs/core/tool-system.md) | shipped | both |

## Built-in tools

| Spec | Status | Provenance |
|---|---|---|
| [Coordination Tools: ListAgents, SubagentHandback, WaitForMcpServers](specs/tools/agent-coordination-tools.md) | shipped | post-leak (ListAgents since v2 |
| [Built-in Tool Catalogue](specs/tools/catalogue.md) | shipped | both |
| [Delivery and Reporting Tools: PushNotification, SendUserFile, ShareOnboardingGuide, ReportFindings](specs/tools/delivery-and-reporting-tools.md) | shipped | post-leak (PushNotification since v2 |
| [EndConversation and SendFeedback](specs/tools/end-conversation-and-send-feedback.md) | shipped | post-leak (EndConversation since v2 |
| [File Tools: Read, Write, Edit, NotebookEdit](specs/tools/file-tools.md) | shipped | both |
| [Interaction and Planning Tools](specs/tools/interaction-and-planning.md) | shipped | both |
| [LSP Tool and Code Intelligence](specs/tools/lsp-code-intelligence.md) | shipped | both |
| [Artifact Tool](specs/tools/post-leak-artifact.md) | shipped | post-leak (introduced in the week of 2026-06-15, digest range v2 |
| [Scheduling Tools: Cron*, ScheduleWakeup, RemoteTrigger](specs/tools/scheduling-tools.md) | shipped | both (`ScheduleWakeup`: post-leak; docs give v2 |
| [Search Tools: Glob, Grep, ToolSearch](specs/tools/search-tools.md) | shipped | both |
| [Background Execution, Monitor and TaskStop](specs/tools/shell-background-and-monitor.md) | shipped | both (Monitor: post-leak since v2 |
| [Shell Tools: Bash and PowerShell](specs/tools/shell-bash-powershell.md) | shipped (PowerShell: preview) | both |
| [Fate of Snapshot Tools No Longer Documented](specs/tools/snapshot-tool-fates.md) | removed | snapshot |
| [Web Tools: WebFetch and WebSearch](specs/tools/web-tools.md) | shipped | both |
| [Worktree Tools and Isolation](specs/tools/worktree-tools.md) | shipped | both |

## Agents and orchestration

| Spec | Status | Provenance |
|---|---|---|
| [Agent Teams and Teammates](specs/agents/agent-teams.md) | preview (experimental, disabled by default) | both (snapshot swarm architecture; implicit team model post-leak, sinc |
| [Agent View](specs/agents/agent-view.md) | preview (research preview) | post-leak (since v2 |
| [Background Sessions and Supervisor](specs/agents/background-sessions.md) | preview (research preview) | post-leak (since v2 |
| [Coordinator Mode](specs/agents/coordinator-mode.md) | gated/unreleased | snapshot |
| [Cross-Session Messaging](specs/agents/cross-session-messaging.md) | shipped | post-leak (since v2 |
| [Dynamic Workflows](specs/agents/dynamic-workflows.md) | shipped | post-leak (since v2 |
| [Forked Subagents and Session Forks](specs/agents/forks.md) | shipped | both (fork subagent gated in snapshot; default-on and `/fork` session  |
| [/goal](specs/agents/goal.md) | shipped | post-leak (since v2 |
| [/loop, Self-Pacing and Session Cron](specs/agents/loop-and-scheduling.md) | shipped | both (fixed-interval `/loop` and cron tools in snapshot; self-pacing,  |
| [Memory Consolidation (autoDream)](specs/agents/memory-consolidation.md) | gated/unreleased | snapshot |
| [Subagent Definitions and Built-in Agents](specs/agents/subagent-definitions.md) | shipped | both (snapshot core; `omitClaudeMd`, `autoCompactWindow`, `experimenta |
| [Subagent Runtime: Agent Tool, Lifecycle and Handback](specs/agents/subagent-runtime.md) | shipped | both (Agent tool in snapshot; background-by-default, nesting, limits,  |
| [Worktrees and Isolation](specs/agents/worktrees.md) | shipped | both (`--worktree`, `EnterWorktree`, `ExitWorktree`, agent isolation i |

## Extensibility

| Spec | Status | Provenance |
|---|---|---|
| [Channels](specs/extensibility/channels.md) | preview (research preview) | both (research preview since v2 |
| [Custom Commands](specs/extensibility/custom-commands.md) | shipped (legacy form of skills) | both |
| [Hook Events Reference](specs/extensibility/hook-events.md) | shipped | both (27 events in snapshot; 6 post-leak: `PostToolBatch`, `UserPrompt |
| [Hooks System](specs/extensibility/hooks.md) | shipped | both (core in snapshot; `mcp_tool` handlers, exec form, `onFailure`, ` |
| [Managed MCP](specs/extensibility/managed-mcp.md) | shipped | both (`managed-mcp |
| [Plugin Marketplaces](specs/extensibility/marketplaces.md) | shipped | both (core in snapshot; `archive`, `command` sources, relevance, `head |
| [MCP Authentication and Connectors](specs/extensibility/mcp-auth.md) | shipped | both (OAuth, `headersHelper` and connectors in snapshot; CLI login, CI |
| [MCP Client](specs/extensibility/mcp-client.md) | shipped | both (core in snapshot; v2 runtime, protocol 2026-07-28, URL elicitati |
| [MCP Tasks](specs/extensibility/mcp-tasks.md) | preview (public beta in CLI) | post-leak (since v2 |
| [Claude Mods](specs/extensibility/mods.md) | shipped | post-leak (since v2 |
| [Output Styles](specs/extensibility/output-styles.md) | shipped | both (mechanism in snapshot; Proactive and Concise styles, mid-session |
| [Plugin Evals](specs/extensibility/plugin-evals.md) | shipped (early-access gating messages exist in docs) | post-leak (since v2 |
| [Plugins](specs/extensibility/plugins.md) | shipped | both (core in snapshot; dependencies, monitors, themes, workflows, ski |
| [Skills](specs/extensibility/skills.md) | shipped | both (core in snapshot; claude |

## Permissions and security

| Spec | Status | Provenance |
|---|---|---|
| [Authentication and Credentials](specs/security/authentication-credentials.md) | shipped | both (profiles, federation, keyless Console, gateway post-leak) |
| [Auto Mode](specs/security/auto-mode.md) | shipped | both (gated as `TRANSCRIPT_CLASSIFIER` in the snapshot; changelog entr |
| [Enterprise Deployment: Launcher, HIPAA, ZDR, Data Usage, Legal](specs/security/enterprise-deployment.md) | shipped | post-leak for launcher (since v2 |
| [Managed, Server-Managed and Remote Settings as Policy](specs/security/managed-settings.md) | shipped | both; source composition, helpers, fail-closed parsing post-leak |
| [OS Sandbox for Shell Commands](specs/security/os-sandbox.md) | shipped (`network | both; network, credentials and policy locks mostly post-leak |
| [Permission Modes](specs/security/permission-modes.md) | shipped | both (`default`, `acceptEdits`, `plan`, `dontAsk`, `bypassPermissions` |
| [Permission Rules: Syntax and Evaluation Order](specs/security/permission-rules.md) | shipped | both; heavily extended post-leak |
| [Security Guidance and Security Review](specs/security/security-review-tools.md) | shipped | both (`/security-review` in snapshot); plugins post-leak, versions not |
| [Shell Command Safety](specs/security/shell-command-safety.md) | shipped | both |
| [Trust Dialogs and Configuration Trust](specs/security/trust-dialogs.md) | shipped | both; repository-supplied configuration rules reshaped post-leak |

## Memory, context and settings

| Spec | Status | Provenance |
|---|---|---|
| [Auto memory and memdir](specs/memory-context/auto-memory.md) | shipped (background consolidation and session memory: gated/ | both |
| [Checkpoints and /rewind](specs/memory-context/checkpoints-rewind.md) | shipped | both |
| [The .claude directory layout](specs/memory-context/claude-directory.md) | shipped | both |
| [CLAUDE.md, AGENTS.md and rules discovery](specs/memory-context/claude-md-and-rules.md) | shipped | both (AGENTS |
| [Compaction](specs/memory-context/compaction.md) | shipped (microcompact variants and session-memory compaction | both (idle compaction, `/autocompact`, partial summarise post-leak) |
| [Context window accounting and /context](specs/memory-context/context-window-accounting.md) | shipped | both |
| [Environment variables reference](specs/memory-context/env-vars-reference.md) | shipped | both |
| [Prompt caching behaviour](specs/memory-context/prompt-caching.md) | shipped | both (TTL controls, cache statistics and most stability guarantees pos |
| [Sessions: transcripts, resume, continue, branch, fork, rename, recap](specs/memory-context/sessions.md) | shipped | both (running-session resume, `/fork` copy, recap post-leak) |
| [Settings keys reference](specs/memory-context/settings-keys-reference.md) | shipped | both |
| [Settings system](specs/memory-context/settings-system.md) | shipped | both |
| [Team memory sync](specs/memory-context/team-memory-sync.md) | gated/unreleased | snapshot |

## Terminal interface and CLI

| Spec | Status | Provenance |
|---|---|---|
| [Accessibility](specs/interface/accessibility.md) | shipped | post-leak (since v2 |
| [CLI flags](specs/interface/cli-flags.md) | shipped | both |
| [CLI subcommands](specs/interface/cli-subcommands.md) | shipped | both |
| [/doctor and diagnostics](specs/interface/doctor-and-diagnostics.md) | shipped | both (reshaped since v2 |
| [Fullscreen mode and /tui](specs/interface/fullscreen-mode-and-tui.md) | preview (research preview; default for many users) | both (internal in snapshot; public since v2 |
| [Gated UI features and easter eggs](specs/interface/gated-ui-features.md) | gated/unreleased (mixed; `/buddy` shipped once, see below) | snapshot, with post-leak notes |
| [Keybindings](specs/interface/keybindings.md) | shipped | both |
| [Notifications](specs/interface/notifications.md) | shipped | both |
| [Onboarding, tips and /powerup](specs/interface/onboarding-tips-and-powerup.md) | shipped | both |
| [Prompt input and editing](specs/interface/prompt-input-and-editing.md) | shipped | both |
| [Slash commands catalogue](specs/interface/slash-commands-catalogue.md) | shipped | both |
| [Slash commands: snapshot-only names and their fate](specs/interface/slash-commands-snapshot-only.md) | removed (mixed: many rows are live aliases or internal; see  | snapshot |
| [Slash command system](specs/interface/slash-commands-system.md) | shipped | both |
| [Status line](specs/interface/status-line.md) | shipped | both |
| [Terminal renderer and layout](specs/interface/terminal-renderer-and-layout.md) | shipped | both |
| [Themes and colour](specs/interface/themes-and-colour.md) | shipped | both (built-in presets in snapshot; auto and custom themes post-leak,  |
| [Vim mode](specs/interface/vim-mode.md) | shipped | both |
| [Voice dictation](specs/interface/voice-dictation.md) | shipped | both (feature-gated in snapshot; public) |

## Platforms and integrations

| Spec | Status | Provenance |
|---|---|---|
| [Claude Agent SDK Core](specs/platforms/agent-sdk-core.md) | shipped | both (`entrypoints/agentSdkTypes |
| [Artifacts](specs/platforms/artifacts.md) | shipped | post-leak (no snapshot code; docs cite behaviours from 2 |
| [Claude in Chrome Integration](specs/platforms/chrome-integration.md) | shipped (generally available since 2 | both |
| [GitHub Actions, GitLab CI/CD and GitHub Enterprise Server](specs/platforms/ci-github-gitlab-ghes.md) | shipped (GitHub Actions, GHES); preview (GitLab CI/CD, beta, | both (`/install-github-app` in snapshot; action v1, federation and GHE |
| [Claude Apps Gateway](specs/platforms/claude-apps-gateway.md) | shipped | post-leak (since v2 |
| [Claude Code on the Web and Cloud Environments](specs/platforms/cloud-sessions.md) | shipped | both (teleport and upstream proxy in snapshot; environment model and s |
| [Code Review Service and /code-review](specs/platforms/code-review.md) | shipped | both (`/review` in snapshot; managed service and `/code-review` post-l |
| [Computer Use](specs/platforms/computer-use.md) | preview (research preview in CLI on macOS; Desktop on macOS  | both (snapshot `utils/computerUse/`, gated; public since then) |
| [Claude Desktop: Code Tab](specs/platforms/desktop-app.md) | shipped (Linux build is beta) | both (`/desktop` handoff in snapshot; app itself is outside the CLI so |
| [Desktop iOS Simulator Pane](specs/platforms/desktop-ios-simulator.md) | preview (public beta, macOS) | post-leak (app feature; no CLI version in changelog, requires Claude D |
| [Desktop Local Scheduled Tasks](specs/platforms/desktop-scheduled-tasks.md) | shipped | post-leak (Claude Desktop 1 |
| [Direct Connect Server](specs/platforms/direct-connect-server.md) | gated/unreleased | snapshot |
| [Feature Availability by Plan and Platform](specs/platforms/feature-availability.md) | shipped | post-leak (documented matrix at 2 |
| [Headless Mode and Stream-JSON Protocol](specs/platforms/headless-stream-json.md) | shipped | both (`cli/`, `entrypoints/sdk/controlSchemas |
| [Installation, Update Channels and Release Mechanics](specs/platforms/installation-updates-release.md) | shipped | both (`utils/nativeInstaller/`, `utils/autoUpdater` in snapshot) |
| [JetBrains Plugin](specs/platforms/jetbrains-plugin.md) | shipped (plugin settings page labelled Beta) | both |
| [LLM Gateway Protocol](specs/platforms/llm-gateway-protocol.md) | shipped | both (base URL handling in snapshot; contract documented post-leak) |
| [Claude Code on Mobile](specs/platforms/mobile.md) | shipped | both (`/mobile` in snapshot; Code tab behaviours post-leak) |
| [Remote Control Bridge Internals](specs/platforms/remote-control-bridge.md) | shipped (mechanics from snapshot; current wire details unver | snapshot |
| [Remote Control](specs/platforms/remote-control.md) | shipped | both (bridge in snapshot, behind `BRIDGE_MODE`; heavily changed post-l |
| [Cloud Scheduled Tasks (Routines)](specs/platforms/routines.md) | preview (research preview) | both (`/schedule` skill and `RemoteTrigger` tool in snapshot, gated; p |
| [Self-Hosted Environments and Runners](specs/platforms/self-hosted-environments.md) | preview (public beta on Team and Enterprise, off by default) | post-leak (since v2 |
| [Slack: Claude Tag and Earlier Claude Code in Slack](specs/platforms/slack-and-claude-tag.md) | preview (Claude Tag, public beta); removed in connected work | post-leak (Claude Tag changelog entries from v2 |
| [Telemetry, Monitoring and Analytics](specs/platforms/telemetry-monitoring.md) | shipped (traces in beta) | both (`services/analytics/`, `utils/telemetry/` in snapshot; many even |
| [Third-Party Providers](specs/platforms/third-party-providers.md) | shipped | both (Bedrock, Vertex, Foundry in snapshot; Claude Platform on AWS, Ma |
| [Ultrareview](specs/platforms/ultrareview.md) | preview (research preview) | both (`commands/review/ultrareview*` in snapshot; shipped publicly sin |
| [VS Code Extension](specs/platforms/vs-code-extension.md) | shipped | both (IDE bridge in the snapshot; graphical panel feature set largely  |
