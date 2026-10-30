# Enterprise Deployment: Launcher, HIPAA, ZDR, Data Usage, Legal

**Status:** shipped
**Provenance:** post-leak for launcher (since v2.1.208, 2026-07-13) and HIPAA configuration (since v2.1.285, 2026-09-29); data handling both
**Sources:** docs `admin-setup`, `corporate-launcher`, `hipaa-setup`, `zero-data-retention`, `data-usage`, `legal-and-compliance`, `security`, `network-config`, `sandbox-environments`; changelog 2.1.101–2.1.314

## Purpose

Specify what an organization can rely on when deploying Claude Code: how processes start, which regulated configurations exist, what data leaves the machine, and what terms apply. Policy delivery itself is in [managed-settings.md](managed-settings.md).

## Behaviour

### Deployment decisions

1. Administrators choose a provider (Teams or Enterprise, Console, Bedrock, Agent Platform, Foundry), a delivery mechanism, controls, visibility and data handling. Cloud sessions, routines, Code Review, Remote Control and Chrome MUST require a claude.ai account and are unavailable through Console or cloud-provider credentials alone.
2. Control surface: permissions and lockdown, starting mode, sandbox, managed `CLAUDE.md` (guidance, not enforced), MCP, plugin marketplace, customization lockdown, claude.ai sync, hooks, login, providers, agent view, launcher, models, effort, version floor, required range, telemetry opt-out.
3. `minimumVersion` blocks auto-update below a floor. `requiredMinimumVersion` and `requiredMaximumVersion` refuse startup outside a range. `availableModels` with `enforceAvailableModels` and `deniedModels` constrain models.
4. Organization model and effort controls are server-side on Enterprise and MUST NOT reach third-party providers.
5. Desktop WSL sessions are off on organization-managed devices until enabled by an HKLM policy under the Claude Desktop key. WSL sessions resolve managed settings via the WSL path unless inherited. Processes in the WSL VM are invisible to Windows sensors, while OTel tool telemetry is identical.
6. Network: proxy and CA settings apply to every provider. The OS CA store is trusted by default (`CLAUDE_CODE_CERT_STORE`).

### Corporate launcher

7. `CLAUDE_CODE_PROCESS_WRAPPER` (2.1.208) and `processWrapper` (2.1.210) MUST route every process Claude Code starts from its own binary through the launcher: background service, agent-view hosts and sessions including warm standbys, respawns, update relaunches, Remote Control session processes, split-pane teammates.
8. The variable takes precedence over the setting. Set via `env` in settings so the detached service inherits it. Managed values override user and shell values. Project and local settings MUST NOT configure it (ignored, with a debug warning).
9. If the launcher cannot run, the process MUST NOT start. Windows ignores it, with a debug warning, because the contract needs `exec`.
10. Not covered: sessions a user starts directly; deep-link sessions; the `--worktree --tmux` relaunch; the Chrome native-messaging host.
11. Launcher contract: end with `exec "$@"`; keep Claude Code's arguments; pass all inherited environment; reach `exec` in about three seconds; tolerate nesting; print nothing before `exec`; do not depend on argument spelling; `exec` from the starting directory; do not read stdin; use absolute paths.
12. Value format: argument list, double-quoted tokens, or a JSON string array beginning `[`. No shell syntax; unquoted operators MUST be rejected as configuration errors.
13. A running service reads the value once. `claude daemon stop --any` or the next new session retires an unwrapped service. `/status` Self-exec and `claude daemon status` MUST show the resolved command and warn on mismatch.
14. A launcher that forks leaves orphans; agent view marks the session failed. Launcher wrapping removes display labels of helpers but not their identity.
15. `CLAUDE_CODE_SHELL_PREFIX` is distinct: it wraps shell commands, hooks and stdio MCP startup, receiving one quoted string.

### HIPAA configuration

16. An organization setting on Claude Enterprise for BAA customers, covering local mode: terminal and Desktop Code tab, plus Cowork local. IDE extensions keep working but the BAA does not cover them.
17. It MUST take effect only with a Claude Enterprise sign-in connecting directly to the Claude API. Bedrock, Agent Platform, Foundry, Claude Platform on AWS, gateways, custom base URLs, `ANTHROPIC_AUTH_TOKEN` or `apiKeyHelper` without Enterprise sign-in, Console keys and federation are ineligible.
18. Requires v2.1.285 and Desktop v2.19675.0. Servers MUST reject older versions, which fail each request with a minimum-version error.
19. The client learns status by fetching organization policy at start and about hourly. Status lasts until restart even after `/login` to another organization.
20. Effects: WebFetch off (web search stays); `--cloud`, `/teleport`, Remote Control refused; `/feedback`, `/bug` off; artifact publishing off; MCP tool search off and not re-enablable; built-in `auto` default off (session starts Manual with a notice in the terminal), auto and bypass stay selectable unless disabled; Anthropic credentials removed from subprocess, hook and MCP environments.
21. Cloud and GitHub credentials are not removed; data sent to those services is outside the BAA.
22. Visibility: startup notice, `HIPAA configured` footer tag (`HIPAA` before 2.1.286), `/status` `Organization configuration` line. The Code tab is off until an Owner re-enables it.
23. Sample managed settings: `forceLoginMethod: "claudeai"`, `forceLoginOrgUUID`, `allowedProviders: ["anthropic"]`, `cleanupPeriodDays`. A wrong `forceLoginOrgUUID` exits every claude.ai session. Versions predating these keys ignore them; `requiredMinimumVersion` narrows that gap. An MDM-delivered policy needs the same keys in server-managed settings when both are used.

### Local data

24. Local data is the organization's responsibility. Transcripts are plaintext under `~/.claude/projects/`, default 30 days via `cleanupPeriodDays`. Retention runs only when Claude Code starts. Sessions from Desktop or Cowork are exempt from the limit by default outside HIPAA; with HIPAA, Desktop deletes inactive Code tab sessions older than the limit while running, including starred, removing worktrees only when clean, unpinned and unused.
25. `claude purge --all --yes` (v2.1.288; `claude project purge` from v2.1.126) removes transcripts, auto memory, `tasks/`, `debug/`, `file-history/`, `history.jsonl` and project entries. Other paths remain; device wipe clears everything. Seat removal and `/logout` delete nothing.

### Zero data retention

26. ZDR is per-organization, enabled by Anthropic for qualified Claude for Enterprise accounts, on the direct platform only. New organizations MUST be enabled separately.
27. It covers inference requests that authenticate into a ZDR organization. Personal accounts and other organizations' keys are not covered; `forceLoginMethod` and `forceLoginOrgUUID` keep claude.ai logins in scope.
28. Not covered: claude.ai chat, Cowork, analytics metadata, seat data, third-party integrations.
29. Backend-disabled regardless of client display: cloud sessions, unified Chat and Cowork, Claude Tag, Artifacts, `/feedback`, `/bug`, `/share`, Remote Control. Attempted use returns a policy error. Future storage-dependent features may be disabled too.
30. Fable models are Covered Models requiring retention by default; a ZDR organization may not be able to use them, and they are absent or disabled while the server rejects them. `best` resolves to Opus there.
31. Data may be retained if required by law or policy violation, up to 2 years for flagged sessions.
32. Organizations without the HIPAA configuration need ZDR for BAA coverage of Claude Code.

### Data usage

33. Consumer plans: training on data only when the user's setting allows. Retention 5 years when allowed, 30 days otherwise.
34. Commercial terms: Anthropic does not train on code or prompts unless the customer opts in (Development Partner Program). Standard retention 30 days.
35. All prompts and outputs go over TLS 1.2+. Encryption at rest varies by provider. Isolation MUST NOT change what is sent.
36. Cloud sessions: repository cloned into isolated VMs, transcripts stored, GitHub credentials kept outside the VM behind a proxy, all outbound traffic through a proxy.
37. Remote Control follows local flow with the transcript stored while connected.
38. Telemetry: usage metrics (no code, prompts or file paths) and error reports (redacted; on only for Pro and Max, v2.1.198+, direct, no ZDR or HIPAA). Off by default on third-party providers except when `CLAUDE_CODE_PROVIDER_MANAGED_BY_HOST` turns metrics on. Gateway sessions disable them by credential.
39. Opt-outs: `DISABLE_TELEMETRY`, `DISABLE_ERROR_REPORTING`, `DISABLE_FEEDBACK_COMMAND`, `CLAUDE_CODE_DISABLE_FEEDBACK_SURVEY`, `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC`. The telemetry and traffic switches also disable feature-flag fetching, affecting Remote Control.
40. `/feedback`, `/bug`, `/share` send transcripts retained 5 years. On third-party providers they write `~/.claude/feedback-bundles/` instead. A draft Claude prepares MUST NOT send until the user chooses.
41. Session quality rating records only the rating. The optional transcript share uploads transcript and logs with known secrets redacted, retained up to 6 months, never used for training, and writes locally on third-party providers. Absent under ZDR or disabled feedback.
42. WebFetch sends only the hostname to Anthropic for a blocklist check, cached five minutes when passed, independent of provider and non-essential-traffic settings. If the network blocks the check, fetches fail until `api.anthropic.com` is allowed.

### Legal

43. Commercial Terms cover Team, Enterprise, API. Consumer Terms cover Free, Pro, Max. Existing agreements apply through third-party providers.
44. Products preinstalling or running Claude Code MUST use the unmodified binary, MUST NOT remove authentication methods, and MUST NOT pay for, resell or intermediate usage. Each end user authenticates themselves. Names and logos follow Trademark Guidelines.
45. BAA extends to Claude Code under either the HIPAA configuration or ZDR. Under HIPAA, cloud sessions, Remote Control, mobile and third-party or gateway routing are not covered.
46. Usage is subject to the Usage Policy. Advertised Pro and Max limits assume ordinary individual use. Vulnerabilities are reported through HackerOne.
47. Anti-abuse enforcement is out of scope for this spec.

## Configuration & interfaces

| Key or command | Purpose |
|---|---|
| `processWrapper`, `CLAUDE_CODE_PROCESS_WRAPPER`, `CLAUDE_CODE_SHELL_PREFIX` | Launchers |
| `cleanupPeriodDays`, `claude purge` | Retention |
| `DISABLE_*`, `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` | Data controls |
| `disableAgentView`, `disableDeepLinkRegistration` | Surface controls |
| `minimumVersion`, `requiredMinimumVersion`, `requiredMaximumVersion` | Versions |
| `availableModels`, `enforceAvailableModels`, `deniedModels`, `maxEffortLevel` | Models |
| OTel | `OTEL_LOG_*`, `OTEL_LOG_MANAGED_SETTINGS`, `OTEL_METRICS_INCLUDE_REPOSITORY` |

## Failure modes & edge cases

- A launcher that rebuilds its environment breaks sessions; `/status` reports a mismatch.
- A launcher replacing the install symlink double-wraps and disables auto-update.
- Project settings cannot set telemetry-enabling variables or `CLAUDE_CODE_DISABLE_ATTACHMENTS`; `claude doctor` lists ignored ones.
- A session on a gateway gets request-level audit but is ineligible for HIPAA.
- HIPAA restrictions in a session outlive `/login` to another organization.

## Changes since the snapshot

- 2.1.101: OS CA trust. 2.1.163: version range. 2.1.175: `enforceAvailableModels`. 2.1.208, 2.1.210: launcher and `processWrapper`.
- 2.1.232: `blockedMarketplaces` URL handling; gateway policy boot checks. 2.1.247: analytics off for gateway login. 2.1.251: project `env` cannot set `CLAUDE_CONFIG_DIR` or temp variables. 2.1.282: project telemetry variables ignored; `allowClaudeInChromeWithManagedMcp`. 2.1.283: `deniedModels`.
- 2.1.285: HIPAA configuration minimum. 2.1.286: `HIPAA configured` tag. 2.1.288: `claude purge`. 2.1.290: project `CLAUDE_CODE_DISABLE_ATTACHMENTS` ignored. 2.1.310: Enterprise custom roles.

## Open questions

- HIPAA feature availability table is hosted outside this doc set.
- Whether the launcher's three-second budget is enforced or advisory.
- Which version introduced `disableAgentView`.
