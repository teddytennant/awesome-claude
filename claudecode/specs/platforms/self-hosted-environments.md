# Self-Hosted Environments and Runners
**Status:** preview (public beta on Team and Enterprise, off by default)
**Provenance:** post-leak (since v2.1.224, 2026-08-07)
**Sources:** docs `self-hosted-environments*.md`; changelog 2.1.224 to 2.1.314

## Purpose
Execute cloud sessions on infrastructure an organisation operates, while Anthropic keeps the control plane, queueing, and claude.ai interface. Developers pick an environment as usual. Repository checkouts and build artifacts stay in the customer network, while the conversation (prompts, responses, tool results) still goes to `api.anthropic.com`.

## Behaviour

### Model
1. Three entities MUST exist: **environment** (named runner group, API name `pool`, ID `ccpool_…`), **runner** (long-lived process, ID `ccrunner_…`), **session** (one child Claude Code process).
2. Sessions MUST be routed to an environment, never to a runner.
3. Environments are created on the Cloud environments admin page by an Owner, after **Allow self-hosted environments** is on, which requires cloud sessions enabled.
4. The environment secret ("environment key") is shown once and authenticates runner registration.
5. Unavailable for ZDR and HIPAA-configured orgs.
6. Dispatch has no per-environment access control: any org member can dispatch to any environment.

### Surfaces
7. claude.ai/code, mobile, desktop, cloud scheduled tasks, `claude --cloud`, `--environment` dispatch, and Claude Tag MUST be able to route to self-hosted environments.
8. Access bundles are unavailable in Claude Tag sessions there. Claude Security and Code Review do not route there yet.
9. Bypass permissions is unavailable. Network secrets do not exist here.
10. `--environment` dispatch MAY use non-GitHub git hosts; other surfaces use GitHub or GitHub Enterprise Server.

### Session lifecycle
11. The control plane MUST queue the session. A runner with capacity claims it under a lease, clones the repository, and spawns a child.
12. The child streams events over HTTPS. Each poll refreshes the lease and acts as heartbeat.
13. A lapsed lease (about 60 seconds) MUST allow requeue, which may take minutes.
14. Poll requests have a 10-second budget. On timeout, loss or unparseable response, the runner MUST keep live sessions and retry after a second or two, doubling up to 20 seconds.
15. No inbound connectivity is required.
16. Sessions moving to a new runner MUST see the interrupted tool call marked outcome unknown (2.1.309).
17. A session released while idle MUST resume on the next message, on any runner, in its earlier permission mode. Unpushed work may be lost; see Failure modes.

### Owner locking
18. A runner MUST lock to the owner of its first session and serve only that owner, up to `--capacity`. Owner is the user, or for Claude Tag channel sessions the Tag agent.
19. Minimum fleet size equals the number of concurrently active owners.
20. With `--drain-grace-sec 0` the runner MUST exit when its sessions finish, so a supervisor restarts it fresh. A positive value keeps polling that owner's queue.
21. `--lock-to-account` pre-locks. A pre-locked runner never takes Claude Tag channel sessions.

### Shutdown
22. `SIGTERM` MUST drain per `--drain-wait-sec`, or defer per `--defer-shutdown-max-min`. At startup the runner MUST log how long it can need, for example `This runner needs up to 80s`. Stop timeouts must be sized to that.
23. `--retire-at` MUST stop new work and release each session (mid-turn after it ends; background tasks waited up to 60 seconds), then exit 0.
24. A signal-less kill is recorded as a lost worker and the session requeues.
25. `--drain-marker-file` reports the exit as a host drain, for telemetry only (2.1.271).
26. `--hold-idle-file` plus `--max-hold-min` keep an idle session while host processes run (2.1.311).

### Git
27. Options: runner-configured git (`--configure-git`), git config shipped in the image, or Anthropic-managed git (`--use-anthropic-git-proxy`).
28. `--configure-git` MUST write a global identity, enable Anthropic commit signing, turn on push negotiation (2.1.257), and install a `Co-authored-by:` trailer hook.
29. Anthropic-managed git is github.com only, requires `--capacity 1` and git 2.32+, covers only the session's repositories, allows branch pushes only, requires each user to connect GitHub, and is decided per session.
30. It MUST delete and replace the runner user's global git config at startup and before each session, without backup.
31. The runner's own git MUST verify Anthropic's git route regardless of `GIT_SSL_CAINFO` or `GIT_SSL_NO_VERIFY` (2.1.283). Its certificate file filters trust like the CLI (2.1.307).
32. On macOS and Linux with managed git and no `gh`, a built-in REST-only `gh api` MUST be provided (2.1.287), which supports `--paginate` and suggests equivalents for refused commands (2.1.288).
33. `--git-host-rewrite` and `--git-ssh-rewrite` MUST rewrite source URLs; `CLAUDE_RUNNER_FETCH_DEPTH` defaults to 50.
34. A pre-warmed clone MAY be supplied at the runner's canonical clone path, to skip cold clones. At `--capacity 1` the runner fetches the ref, detaches `HEAD` and resets hard.

### Customisation
35. `--exec-path` MUST spawn a wrapper instead of the binary. A wrapper ends by exec-ing `CLAUDE_RUNNER_CLAUDE_BIN` with its arguments, and keeps stdin (control channel, including token rotation) and file descriptor 3 (activity signals) attached, or the session fails when its initial token expires in about 30 minutes. System prompt flags must pass through.
36. Lifecycle hooks in `--hooks-dir`: `checkout` (per repo, replaces clone), `post-session` (per session end with a child), `command`, and `spawn-runner` (orchestrator).
37. `post-session` MUST NOT affect outcome. `CLAUDE_RUNNER_EXIT_REASON` is `completed`, `failed`, `interrupted`, or reserved `abandoned`. It cannot fire on abrupt termination.
38. Each session MUST receive a seed of the host's config (`SELF_HOSTED_RUNNER_HOST_CONFIG_DIR`, default `~/.claude`), taken at startup per `--host-config-snapshot`.
39. `--trust-workspace` (default on) seeds trust so repo `permissions.allow` apply. `--confine-repo-settings` (`warn` default, `enforce`, `off`) flags repo settings reaching outside the workspace, non-empty `env`, or posture overrides such as `sandbox.enabled: false`. It does not cover hooks, `.mcp.json` or Bash rules.
40. `--server-auto-mode-lists` (`all`, `no-allow` default, `none`) limits which control-plane classifier lists reach a session. `CCR_AUTO_MODE_*` are no longer passed to children (2.1.295).
41. `CLAUDE_CODE_DISABLE_ARTIFACT=1` disables the Artifact tool and its egress need.

### On-demand runners
42. `claude self-hosted-runner orchestrator` MUST poll spawn requests and run a `spawn-runner` hook, passing a single-use work-order JWT, so the environment secret stays off session hosts.
43. `--min-idle` MAY pre-warm slots. `--hook-timeout` + 5s kill grace MUST stay below `--expected-spawn-seconds` (server range 10-3600).
44. SCM connector flags exist but the connector is documented as not available; leave them unset.

### Model providers
45. A runner MAY send inference to Bedrock or Google Agent Platform. Content still flows to Anthropic in the event stream, and server-managed settings and claude.ai org policies do not reach those sessions.
46. Configure every runner in an environment the same way.
47. `forceRemoteSettingsRefresh: true` in the runner image's `managed-settings.json` stops a session starting when its settings fetch fails. Leave it out on runners serving Claude Tag channels, whose fetches are refused, so they would fail to start.

### Session identity
48. Sessions receive `CLAUDE_CODE_SESSION_ACCESS_TOKEN`: prefix `sk-ant-cc-` plus an ES256 JWT, 4-hour default, 8-hour maximum life. Refreshes arrive on the child's stdin, so a wrapper sees only the first value.
49. Verifiers MUST strip the prefix, check against the JWKS by `kid`, reject other prefixes, and verify `aud` contains the `ccpool_…` ID, not `anthropic-api`.
50. Token proves issuer, session, environment and creator type, but not which process presents it; any session code can read it. Derived credentials must be scoped to a session.
51. Identity should key on `act.sub` or `ccr:account_id`; flat claims are back-compat. `ccr:session_id` uses `cse_…`, and hooks see the same ID as `session_…`.

## Configuration & interfaces

### Subcommands
`claude self-hosted-runner`, with `setup`, `doctor`, `orchestrator`. Windows requires explicit `--base-dir` (2.1.229). `--log-file` is required for `doctor` to tail logs.

### Selected runner flags
| Flag | Default | Purpose |
|---|---|---|
| `--environment-secret-file` | required | Secret path; or `SELF_HOSTED_RUNNER_ENVIRONMENT_SECRET` |
| `--base-dir` | `/workspace` | Checkouts and session dirs |
| `--capacity` | 1 | Concurrent sessions |
| `--client-label` | hostname | 2.1.248 |
| `--drain-grace-sec`, `--drain-wait-sec` | 0 | Exit and drain timing |
| `--defer-shutdown-max-min` | 0 | Keep serving after first signal |
| `--exit-if-unused-min` | 0 | Autoscaler scale-down |
| `--health-port` | 8080 | `/healthz`, `/metrics`; 0 disables |
| `--kill-session-after-min` | 0 | Lifetime limit; since 2.1.260 releases rather than kills |
| `--release-idle-session-min` | 0 | Idle slot release |
| `--startup-timeout-min` | 15 | Child init timeout |
| `--session-stop-grace-sec` | 5 | Clean exit wait |
| `--post-session-hook-timeout-sec` | 60 | Hook budget |
| `--push-outcome-on-release` | off | Best-effort push before deletion |
| `--remove-session-state` | off | Delete `_sessions` dirs |
| `--proxy-authorization-command`, `--proxy-authorization-file` | unset | `Proxy-Authorization` per connection |

Flags win over variables. Duration variables use `_MS`. Flag values above the cap (7 days for `--*-min`) fail at startup; variables are clamped.

### Orchestrator
`--hook-concurrency` 4, `--hook-timeout` 60, `--expected-spawn-seconds` 120, `--min-idle` 0, `--shutdown-drain-sec` 0, `--debug-dir`.

### Variables to wrappers and hooks
`CCR_SESSION_ACCOUNT_EMAIL` (unverified, for labels only), `CLAUDE_RUNNER_CLIENT_PLATFORM` (`web_claude_ai`, `desktop_app`, `ios`, `claude_code_cli`, `scheduled_trigger`), `CLAUDE_RUNNER_REPO_URL`, `CLAUDE_RUNNER_REPO_REF`, `CLAUDE_RUNNER_CHECKOUT_PATH`, `CLAUDE_RUNNER_SESSION_ID`, `CLAUDE_RUNNER_SESSION_UUID`, `CLAUDE_RUNNER_WORKSPACE_PATHS`, `CLAUDE_RUNNER_DEBUG_LOG_PATH`, `CLAUDE_RUNNER_API_BASE_URL`, `GIT_CONFIG_*` (2.1.280).

### Observability
`GET /healthz` is 200 whenever the process lives, with `status`, `runner_id`, `active_sessions`, `last_poll_at`, `last_poll_age_ms`, so probes detect dead processes only. `GET /metrics` serves `claude_code_self_hosted_runner_*` (info, capacity, active_sessions, locked_account, last_poll_age_seconds, poll_errors_total, sessions_started/completed/failed/interrupted_total by `client_platform`, init metrics, session_idle_seconds) and `claude_code_self_hosted_orchestrator_*`.

### Hardening expectations
Ephemeral per-session containers, no broad credentials in images, default-deny egress, blocked cloud metadata endpoint, read-only hooks and wrapper, and on-demand runners to isolate the environment secret.

## Failure modes & edge cases
- First message never answered: a proxy may be buffering SSE.
- Provider egress blocked: Claude Code may retry for hours before showing an error.
- Git host "not found" names the repo and whom to ask (2.1.304). A never-pushed branch gets a specific fix (2.1.314).
- HTTP 429 or wrapper exit 75 on an added read-only repo: session starts without it (2.1.311).
- `--retire-at` values before 2001 or too far ahead are rejected.
- Some sessions don't count as idle, so pair idle release with `--kill-session-after-min`.
- Connector traffic leaves the customer network.
- A crafted long error line no longer freezes the runner (2.1.290).
- reftable checkouts reuse fixed (2.1.302).

## Changes since the snapshot
- 2.1.224: feature added. 2.1.229: explicit Windows `--base-dir`. 2.1.248: `--client-label`. 2.1.257: push negotiation. 2.1.260: lifetime release.
- 2.1.267: git proxy reported at registration, warnings for legacy path.
- 2.1.271: `--drain-marker-file`. 2.1.280: `--retire-at` settle. 2.1.283: TLS handling.
- 2.1.287, 2.1.288: built-in `gh api`. 2.1.290: `--environment` uses current Sessions API.
- 2.1.295: fetch progress cap, `CCR_AUTO_MODE_*` removed.
- 2.1.296, 2.1.299, 2.1.305: admin status filters, deletion turns routines off, delete dialog explains blockers.
- 2.1.309: outcome-unknown tool calls. 2.1.311: hold-idle. 2.1.314: idle pause no longer migrates on lost connection.

## Open questions
- When the SCM connector will ship.
- Whether Foundry will be supported for runners.
