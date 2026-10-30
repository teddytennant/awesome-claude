# Feature Availability by Plan and Platform
**Status:** shipped
**Provenance:** post-leak (documented matrix at 2.1.314)
**Sources:** docs `feature-availability.md`, `platforms.md`, plus each surface's page; changelog 2.1.139, 2.1.196, 2.1.285

## Purpose
State which features work for each authentication path, provider, plan and surface. This is a snapshot of the 2.1.314 public matrix.

## Behaviour

### Provider-agnostic
1. Available everywhere: CLI, Agent SDK, VS Code and JetBrains extensions, subagents, hooks, commands, skills, CLAUDE.md memory, plugins, MCP, checkpoints, sandboxing, workflows, OTel metrics, and the managed settings file.
2. Claude.ai connectors load only with an active claude.ai login.
3. Tool search isn't supported on Azure-hosted Foundry, or on Agent Platform models before 4.5-generation.
4. `/voice` needs claude.ai. `/design-sync` and `/import` (`claude import`) are unavailable on cloud providers and through the Claude apps gateway. `/list-agents` and `/peers` need cross-session messaging.
5. When the main conversation runs Fable, Explore runs on Opus for subscription, Console, and `ANTHROPIC_BASE_URL` gateways, and on Fable on other providers.

### Requires a claude.ai login
6. Cloud sessions and mobile; Slack (Pro and Max for the earlier app); Desktop (with the exception below); `/schedule`; ultrareview; Code Review (Team, Enterprise); Remote Control; Chrome; computer use (Pro, Max); artifacts; voice dictation.
7. Desktop exception: gateway routing, or Claude Desktop on 3P for the Code tab on Bedrock, Agent Platform, Foundry, a self-hosted gateway, or the Claude API with a Console key.
8. `ANTHROPIC_API_KEY`, `apiKeyHelper` or `ANTHROPIC_AUTH_TOKEN` disable Remote Control, `/schedule`, connectors and notification preferences (2.1.139).
9. When `ANTHROPIC_BASE_URL` points elsewhere than `api.anthropic.com`, Claude Code turns off Remote Control and server-managed settings, whatever the gateway does (2.1.196).

### By provider
| Feature | Subscription | Console | Bedrock | Platform on AWS | Agent Platform | Foundry |
|---|---|---|---|---|---|---|
| Web search | Yes | Yes | No | Yes | Opus 4, Sonnet 4, Haiku 4.5+ | Yes |
| Fast mode | Owner-enabled on Team, Enterprise | Opus 5 and 4.8 need provisioning | No | No | No | No |
| Auto mode | Yes | Yes | Limited models | Yes | Limited models | Limited models |
| Advisor | Yes | Yes | No | No | No | No |
| Cross-session messaging | Yes | Same machine | Same machine | Same machine | Same machine | Same machine |
| Channels | Yes | Yes | No | No | No | No |
| GitHub Actions | Yes | Yes | Yes | No | Yes | Yes |
| GitLab CI/CD | Yes | Yes | Yes | Yes | Yes | No |
| Analytics | Dashboard Team+, API Enterprise | Dashboard and API | No | No | No | No |
| Server-managed settings | Team, Enterprise | See platform notes | No | No | No | No |
| Zero Data Retention | Qualified Enterprise | Qualified | Per agreement | Qualified | Per agreement | Per agreement |

10. Limited auto mode models: Sonnet 5+, Opus 4.7+, Haiku 5.5, Fable.
11. Cross-session messaging needs 2.1.224 on macOS and Linux, 2.1.234 on native Windows.
12. Through an LLM gateway, availability matches the underlying provider, except features Claude Code disables itself.
13. `allowedProviders` restricts which providers a machine may use (2.1.285).

### By plan
| Feature | Pro | Max | Team | Enterprise |
|---|---|---|---|---|
| Cloud sessions | Yes | Yes | Yes | Premium or Chat + Claude Code seats |
| Cloud scheduled tasks | Yes | Yes | Yes | Yes |
| Remote Control | Yes | Yes | Admin-enabled | Admin-enabled |
| Channels | Yes | Yes | Admin-enabled | Admin-enabled |
| Computer use | Yes | Yes | No | No |
| Dispatch | Yes | Yes | No | No |
| Code Review | No | No | Yes | Yes |
| Artifacts | Yes | Yes | Yes | Yes |
| Analytics and contribution metrics | No | No | Yes | Yes |
| Enterprise Analytics API, SCIM, Compliance API | No | No | No | Yes |
| Server-managed settings, SSO | No | No | Yes | Yes |
| ZDR | No | No | No | Add-on |
| Claude Tag | No | No | Yes | Yes |
| Self-hosted environments (beta) | No | No | Yes | Yes |
| GitHub Enterprise Server | No | No | Yes | Yes |

14. HIPAA-configured Enterprise orgs lose some features, such as cloud sessions, Remote Control and iOS Simulator. Desktop and Chrome are Owner-enabled there.
15. ZDR, HIPAA and CMEK exclude cloud sessions, Remote Control, artifacts and Code Review as stated in those specs.

### Default operational traffic
16. On Bedrock, Agent Platform, Foundry and Claude Platform on AWS, error reporting, telemetry and bug reporting default off. Claude Platform on AWS also has feature-flag features off by default.

### Surfaces
17. Surfaces: CLI, Desktop, VS Code, JetBrains, web, mobile, Slack, CI, Chrome. See `platforms.md` for choosing among them. Computer use is unavailable in the Linux desktop app.

## Configuration & interfaces
Authentication selects the column. See [third-party-providers.md](third-party-providers.md), [claude-apps-gateway.md](claude-apps-gateway.md), [llm-gateway-protocol.md](llm-gateway-protocol.md).

Alternatives on cloud providers: `/loop` for `/schedule`, CI for cloud sessions, WebFetch with URLs for web lookups on Bedrock.

## Failure modes & edge cases
- Server-managed settings set in claude.ai don't reach sessions with a Console API key.
- A gateway sign-in replaces a Teams or Enterprise login.
- Claude Tag runs auto mode with no server-managed settings.

## Changes since the snapshot
- 2.1.139: API key style auth disables claude.ai features. 2.1.196: base URL check for Remote Control. 2.1.207: auto mode on cloud providers. 2.1.285: `allowedProviders`.
- Matrix columns for Claude Platform on AWS and Claude Tag rows are post-snapshot.

## Open questions
- "See Platform availability" for Console server-managed settings is resolved in `server-managed-settings.md`, not reviewed here.
- GitHub Actions on Claude Platform on AWS is marked unavailable, though no reason is given.
