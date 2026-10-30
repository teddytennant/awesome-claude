# Claude Code on the Web and Cloud Environments
**Status:** shipped
**Provenance:** both (teleport and upstream proxy in snapshot; environment model and surfaces reshaped post-leak)
**Sources:** docs `claude-code-on-the-web.md`, `cloud-environments.md`, `web-quickstart.md`, `env-vars.md`; snapshot `upstreamproxy/`, `remote/`, `utils/teleport*`; changelog 2.1.101 to 2.1.314

## Purpose
A cloud session is a Claude Code session on cloud infrastructure that keeps running after the user's machine sleeps, and can be steered from any signed-in surface. An environment defines the network policy, variables, secrets and setup script applied to its sessions.

## Behaviour

### Availability and surfaces
1. Cloud sessions MUST be available on Pro, Max and Team, and for Enterprise premium or Chat + Claude Code seats. Where custom roles apply, the user needs a role with the cloud sessions permission. Free-plan users on claude.ai/code see the plans page (2.1.269).
2. Sessions MUST be startable from claude.ai/code, the mobile Code tab, the desktop app, `claude --cloud`, cloud scheduled tasks, and Claude Tag.
3. Usage MUST count against plan limits, with no separate VM charge.
4. ZDR orgs, HIPAA-configured orgs and CMEK orgs MUST NOT be able to start cloud sessions or use `/web-setup`.
5. `--cloud` requires an Anthropic account and the org's `allow_remote_sessions` policy. It is unavailable on third-party providers. An LLM gateway set only by `ANTHROPIC_BASE_URL` does not count as third-party, but login is still needed.
6. Org IP allowlisting makes all Anthropic-hosted sessions fail with an authentication error, unless Anthropic-hosted services are exempted.

### GitHub connection
7. Two methods MUST be supported: the Claude GitHub App (public repos plus installed private repos), and `/web-setup`, which sends the local `gh` token to the account (any repo that token can reach).
8. Auto-fix and project threads MUST require the App on the repository.
9. In Anthropic-hosted environments GitHub credentials MUST stay outside the VM. Git and API operations go through the GitHub proxy.
10. GitHub proxy rules: scoped credential swapped server-side; branch deletions and non-branch pushes rejected; API requests only for attached repositories, otherwise a 403 beginning `GitHub access to`; GraphQL rejected with a 403 naming the REST fallback, so `gh pr` and `gh issue` fail in that path.
11. Non-GitHub repos MAY be sent as a local bundle with `CCR_FORCE_BUNDLE=1`, without push-back. GitHub Enterprise Server is supported on Team and Enterprise.

### Terminal movement
12. `claude --cloud "<task>"` MUST create a session cloning the current GitHub remote at the current branch, not the local checkout. `--remote` is a deprecated alias. It handles one repo at a time.
13. A live provisioning checklist MUST display, with typed messages queued until ready.
14. `claude -p "<msg>" --cloud <id>` (or stdin) MUST post one message and exit without waiting. `<id>` is `session_…`, `cse_…`, or a claude.ai/code URL. No local state is sent, so it works from any logged-in machine.
15. `--cloud <id>` without `-p` MUST error: attaching is not enabled.
16. `claude --teleport [id]`, `/teleport`, `/tp`, or `t` in `/tasks` MUST verify the repository, fetch and check out the branch, and load the conversation, offering to stash uncommitted changes. The mismatch error shows which repo the checkout points at (2.1.219).
17. A teleported copy MUST NOT sync back. A compacted session loads from its last compaction, with a warning (2.1.311).
18. `/teleport` inside a cloud session MUST reply with the exact local command (2.1.223).
19. `--resume` MUST NOT list cloud sessions.

### Session behaviour
20. Permission modes are selected from a dropdown, and preserved when an expired session is reopened. Bypass is unavailable.
21. Text-output commands work. Terminal-only commands such as `/plugin` and `/resume` do not. `/model`, `/effort`, `/color` and `/rename` take arguments. `/fast` toggles (2.1.271). `/config` in the browser opens settings.
22. Cloud sessions set `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE` themselves, overriding any environment value. `CLAUDE_CODE_AUTO_COMPACT_WINDOW` and `/autocompact` still work.
23. Diffs MUST use raw git blob content, ignoring drivers and `textconv` (2.1.222). The Changes pane says when it lists only pushed commits or only Claude's edits (2.1.309).
24. Sessions MAY be archived, or deleted permanently with confirmation.
25. Non-interactive sessions, including cloud ones, MUST auto-continue a response cut off by a server error or stall (2.1.246).
26. `attribution.sessionUrl` MAY omit the session link from commits and PRs (2.1.183). `CLAUDE_CODE_REMOTE_SESSION_ID` supports linking back.
27. Repositories can be added to a running session. A private repo readable but not pushable attaches read-only (2.1.283).

### Auto-fix
28. Claude MUST subscribe to PR activity and, per event, push clear fixes, ask on ambiguity, or note duplicates.
29. Enable from the Changes card, `/autofix-pr`, the mobile app, or a pasted PR URL.
30. Base-branch conflicts produce no event, so Claude cannot react to them.
31. Replies post under the user's GitHub account and are labelled as Claude Code. This can trigger `issue_comment` automation.

### Environments
32. Onboarding creates **Default**: Trusted network, no variables or script. Team and Enterprise see a form unless Quick setup is on.
33. Personal environments belong to one account. Owners create shared ones, shown under Organization and read-only in the selector, or share a personal one, keeping its ID. Admin role cannot open the Cloud environments page.
34. Environment choice: the selector and org default in apps; `/remote-env` (`remote.defaultEnvironmentId`), then Anthropic-hosted, then first non-bridge environment in the CLI; `--environment <ccpool_…>` for self-hosted.
35. `/remote-env` only sets the default. Auto-creation of a default environment happens since 2.1.101.
36. Archiving hides an environment and blocks new sessions on every surface; running sessions continue. Anthropic-hosted environments can only be archived. Owners may delete self-hosted ones.
37. Variables use `.env` format: `#` starts a comment in unquoted values. All users of an environment can read them. `OTEL_*` values are not passed to commands.
38. Variables are read on create and each time Claude starts in the VM. Edits reach a running session only after restore or rebuild.
39. Transport variables in a repo's `env`, such as `NODE_EXTRA_CA_CERTS`, MUST be ignored and logged.

### Network
40. Levels: None, Trusted (default allowlist), Full, Custom (own list, optionally with defaults). `*.` matches all subdomains.
41. GitHub, enabled MCP connectors, network secret hosts and the Anthropic API MUST remain reachable at any level, including None.
42. There is no org-level push to allowlists; a shared environment with Custom access is the mechanism.
43. A network secret MUST stay outside the VM and be attached by the agent proxy after a request leaves the VM, for listed hosts only. Self-hosted environments have no network secrets.
44. All outbound traffic from a hosted session passes a security proxy. Abuse handling within it is excluded here.
45. Upstream proxy (snapshot, feature level): a local CONNECT relay tunnels traffic to a server-side proxy, with session credentials kept in memory, and fails open to keep sessions working. Current mechanics are not documented.

### Runtime
46. Hosted sessions MUST get a fresh Ubuntu 24.04 x86_64 VM with about 4 vCPU, 16 GB RAM, 30 GB disk (approximate, may change).
47. Pre-installed: Python, Node 20/21/22 at `/opt/node*` with 22 on `PATH`, Ruby, PHP, Java, Go, Rust, C/C++, Docker, PostgreSQL 16, Redis 7.0, and utilities. `check-tools` reports most versions.
48. Idle sessions pause with files saved after a few minutes; a paused VM can be reclaimed.
49. Reopening a reclaimed session MUST restore history only. Running shells, subagents and session-scoped schedules do not carry over; Claude is told which stopped. Waiting on MCP approval counts as inactivity.

### Carry-over
| Item | In cloud |
|---|---|
| Repo `CLAUDE.md`, rules, skills, agents, commands | Yes |
| Repo settings hooks and permissions, `.mcp.json` | Yes for single-repo sessions |
| Plugins declared by repo | No |
| Server-managed settings | Yes, except Claude Tag |
| User `~/.claude/*`, user plugins, local-scope MCP | No |
| claude.ai-enabled skills | Yes |
| Interactive auth such as AWS SSO | No |

### Setup scripts
50. A setup script is a Bash script that MUST run before Claude Code launches, without the environment's variables set.
51. If it finishes within about 5 minutes, a filesystem snapshot MUST be taken and reused, skipping the script. Running processes are not preserved.
52. The cache rebuilds on script or allowed-hosts change, or after about seven days.
53. A restored VM does not re-run the script.
54. SessionStart hooks run after launch on every session, including resumed ones. Hosted sessions run hooks from server-managed settings and the repo.

## Configuration & interfaces
| Item | Purpose |
|---|---|
| `--cloud`, `--remote` | Create or message |
| `--teleport`, `/teleport`, `/tp` | Pull local |
| `--environment <id>` | Self-hosted target |
| `/web-setup`, `/remote-env`, `/autofix-pr` | Connection, default, auto-fix |
| `remote.defaultEnvironmentId` | Saved default; stricter source rule for `ccpool_` IDs |
| `CCR_FORCE_BUNDLE` | Bundle local repo |
| `CLAUDE_CODE_REMOTE`, `CLAUDE_CODE_REMOTE_SESSION_ID` | Set in sessions |
| `BASH_DEFAULT_TIMEOUT_MS`, `BASH_MAX_TIMEOUT_MS` | Command timeouts |
| `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` | Enable agent teams |

Timeouts: foreground commands default to 2 minutes, up to 10. A timed-out command moves to background, except `sleep`, for up to 30 more minutes. SessionStart `command` hooks are cancelled after 600 seconds by default.

## Failure modes & edge cases
- `Branch <name> is not on GitHub`: push first.
- `Cloud sessions aren't available with <provider>`, policy-disabled, policy-unverifiable, `Session not found`, and archived-session errors all come from `--cloud` paths and are prefixed `Error: `.
- `Couldn't verify your organization's policy` is fail-closed when policy has not loaded.
- A setup script at None network cannot install packages.
- Failed startup says "Connection lost" or "Server error" (2.1.302).

## Changes since the snapshot
- 2.1.101: auto-created default environment. 2.1.183: `attribution.sessionUrl`.
- 2.1.222: raw blob diffs; ultraplan removed. 2.1.223: teleport hint.
- 2.1.246: auto-continue on cut-off. 2.1.269: Free-plan path.
- 2.1.271: Custom network in admin settings. 2.1.274: "cloud session" wording.
- 2.1.282: GitHub App status in Connectors; non-GitHub repo links.
- 2.1.283: read-only repo attach. 2.1.295: fast catch-up after reconnect.
- 2.1.310, 2.1.312: environment dialog rows, Choose file, Bash editor.
- 2.1.311: compacted teleport warning. 2.1.314: setup script failure no longer stops start.

## Open questions
- `cloud-environments.md` still says a non-zero setup script fails the session, while 2.1.314 says sessions from web, desktop and mobile start anyway. The behaviour for `--cloud` and scheduled tasks is unstated.
- Exact idle and expiry durations.
- Current upstream proxy design.
