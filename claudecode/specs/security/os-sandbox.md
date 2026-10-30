# OS Sandbox for Shell Commands

**Status:** shipped (`network.tlsTerminate` experimental; sandbox runtime beta research preview)
**Provenance:** both; network, credentials and policy locks mostly post-leak
**Sources:** docs `sandboxing`, `sandbox-environments`, `settings-reference`, `managed-settings`, `permission-modes`; snapshot `utils/sandbox/sandbox-adapter.ts`, `tools/BashTool/shouldUseSandbox.ts`; changelog 2.1.92–2.1.314

## Purpose

An operating-system boundary around the shell commands Claude runs, so filesystem and network limits hold regardless of what the model chose to run. It reduces prompts and limits blast radius. It is not a complete isolation boundary.

## Behaviour

### Scope and platforms

1. The sandbox MUST wrap Bash, PowerShell and Monitor commands and their children. It is off by default.
2. macOS MUST use Seatbelt. Linux and WSL2 MUST use bubblewrap plus socat. Native Windows MUST run unsandboxed; WSL1 is unsupported. Implementation is the open source `@anthropic-ai/sandbox-runtime`.
3. These MUST be treated as outside the sandbox: Read, Edit, Write, WebFetch, WebSearch (governed by permission rules); hooks, local MCP servers, plugin monitors, LSP servers, status line and helper commands, and mod processes. Subagents share the parent's configuration. Background sessions follow their own settings.
4. Computer use runs on the real desktop, gated per app, not in this sandbox.
5. Commands typed at `!` run unsandboxed like the user's own terminal, except in background sessions under strict mode and Linux sessions with `CLAUDE_CODE_SUBPROCESS_ENV_SCRUB` set.

### Defaults

6. Defaults:

| Access | Default |
|---|---|
| Writes | Working directory, per-user temp directory, added directories, minus protected paths |
| Reads | Most of the machine, including credential files |
| Network | No direct route; a local proxy checks hostnames; allowed domains start empty |
| Environment | Inherited from Claude Code, including secrets |

7. Claude Code MUST set `$TMPDIR` to the per-user temp directory for sandboxed commands unless filesystem isolation is off.
8. No credential deny list is built in; only listed entries are protected.

### Modes

9. Auto-allow (`autoAllowBashIfSandboxed`, default `true`): a command that runs sandboxed MUST be approved without prompt. Excluded commands and unsandboxed retries MUST go through the regular flow.
10. Even under auto-allow: deny rules block; critical-path removals use the regular flow; content-scoped ask rules prompt; a bare `Bash` ask is skipped for sandboxed commands but not in plan mode; Monitor commands are not auto-approved. Commands where a leading assignment can change which program runs, and similar forms, go through the regular flow while staying sandboxed.
11. Regular permissions mode MUST send every command through the regular flow even when sandboxed.
12. Auto-allow is independent of permission mode except: plan mode, auto-mode commands carrying per-command domains, and server-side classifier review.

### Unsandboxed retry

13. A failed command MAY be retried with the `dangerouslyDisableSandbox` parameter. Approval: bypass runs without prompt; Manual and `acceptEdits` show a "Bash command (unsandboxed)" prompt; auto routes to the classifier; `dontAsk` denies.
14. A matching allow rule also approves the retry. `Bash(dangerouslyDisableSandbox:true)` as an ask rule forces a prompt in auto and bypass. `blockReadsOutsideWorkingDirectories` can also force one.
15. Strict sandbox mode (`allowUnsandboxedCommands: false`) MUST ignore the parameter. A `false` in user, `--settings` or managed settings MUST hold even if a project sets `true`. Shown as Strict sandbox mode on the `/sandbox` Overrides tab.

### Filesystem

16. `allowWrite`, `denyWrite`, `denyRead`, `allowRead` arrays MUST merge across scopes, minus entries a lock covers. Edits apply to the next sandboxed command. Excluded `--setting-sources` sources contribute no entries.
17. Paths use `/absolute` and `~/` conventions, unlike permission rules' `//`. Overlapping read rules: the narrower path wins, and a deny holds inside a wider allow, including wildcard denies.
18. Linked worktrees MUST allow writes to the shared `.git` except `hooks/` and `config`.
19. With `blockReadsOutsideWorkingDirectories`, sandboxed commands lose read access to home and user-file roots, with working directories, session worktrees, temp and needed `~/.claude` parts reopened. Global git config files are reopened, judged per file, and refused if a sandboxed command could write them. Credential stores stay blocked. Repo `allowRead` and `allowWrite` do not count. The block does not reach sandboxed commands when filesystem isolation is off, `allowManagedReadPathsOnly` is set, or the start path contains a glob character; file tools still enforce it.
20. Protected paths MUST stay write-denied inside writable directories, and `allowWrite` or `Edit` allow MUST NOT override them: `.claude` settings, skills, agents, commands, hooks, `.mcp.json`, workflows, scheduled tasks (working directory and ancestors); shell startup files, `.gitconfig`, `.vscode`, `.idea`, `.git/hooks`, `.git/config` (working directory); files that would make the working directory a bare repository; most of `~/.claude` (or `CLAUDE_CONFIG_DIR`), `~/.claude.json`, `.credentials.json`.
21. A symlink appearing at a protected settings path MUST extend denial to its target from the next command. On macOS, denied paths through symlinks also deny the real location.
22. After a command, a newer top-level `HEAD`, `objects` or `refs` MUST be deleted unless it is a non-empty folder; non-empty `objects` and `refs` are also removed if a `HEAD` was present when the config was built.
23. Bash output files MUST be created and read so a sandboxed command cannot redirect or replace them.
24. `filesystem.disabled: true` turns off filesystem isolation while keeping network isolation. It MUST be honoured only from user, managed and `--settings`; only from managed when managed configures `sandbox.filesystem` or a `credentials.files` `deny` entry; and from no source under `CLAUDE_CODE_SUBPROCESS_ENV_SCRUB`. With it off, `denyRead` and file `deny` entries are not enforced; env entries and masks are.

### Network

25. Linux and WSL2 MUST use a separate network namespace; macOS Seatbelt MUST block all but the proxy connection. Non-TCP traffic cannot leave. Tools ignoring proxy variables cannot connect. HTTP/SOCKS proxy variables direct commands to the local proxy.
26. The proxy MUST check each hostname against allow and deny lists. `deniedDomains` wins everywhere. An entry with no port allows all ports.
27. Allowlist inputs: `allowedDomains` plus `WebFetch(domain:...)` allow rules, honouring only leading `*.` and bare `*`.
28. Non-allowed host outcomes:

| Mode | Outcome |
|---|---|
| Bypass, plan with bypass available | Allowed |
| Manual, `acceptEdits`, plan otherwise | Prompt |
| Auto | Refused unless listed and classifier-approved |
| `dontAsk` | Refused |

29. `strictAllowlist` or `allowManagedDomainsOnly` MUST refuse non-allowlisted hosts in every mode. `strictAllowlist` set in repo files has no effect.
30. "Yes" allows the host for the session; "don't ask again" saves a `WebFetch(domain:...)` rule to local settings, or to user settings under an admin-required sandbox.
31. After a hostname passes, the proxy MUST resolve it and refuse if it resolves only to local addresses (loopback, link-local including the metadata endpoint, own-machine addresses), except `localhost` and `*.localhost`. Private ranges connect. IP entries are decided by lists and mode. Connections through an upstream corporate proxy skip this check.
32. Per-command allowed domains (auto mode with sandbox): a command MAY carry hosts, reviewed with the command. An approved list opens them for that command only. Such commands go to the classifier, not rules or auto-allow. Deny lists still block. Locked allowlists MUST refuse per-command lists. Unlisted hosts MUST be refused without a prompt, naming the host in the result.
33. IPv6 entries MUST be bracketed. Ambiguous entries MUST fail closed: deny lists deny every parse; allow lists never widen. `claude doctor` flags them.
34. Corporate proxy: allowlist first, then tunnel via `HTTPS_PROXY`. `httpProxyPort` and `socksProxyPort` replace the built-in proxy with a user-run proxy, which then owns all filtering.
35. `excludedCommands` matches each whole call with `Bash(...)` syntax and every subcommand must match. Redirects, `cd`, substitutions and others keep a call sandboxed; commands beginning with `unshare` stay sandboxed. Excluded commands run with full access and use the regular flow. Where the sandbox is enabled but cannot run, excluded commands ask before writing to write-list paths.

### Credentials

36. `sandbox.credentials.files` and `.envVars` entries take `deny` or `mask`. `deny` merges from every scope and cannot be removed. It blocks file reads (filesystem layer) and unsets variables.
37. `mask` shows a per-session sentinel and the proxy substitutes the real value on egress to `injectHosts`, or to all allowed domains if none are listed. `deny` wins over `mask`.
38. Masking requires `network.tlsTerminate` and a trusted scope. `mask`, `tlsTerminate`, `allowPlaintextInject`, `awsPairs`, `sigv4` MUST be honoured only from user, managed and `--settings`. Without TLS termination the sentinel reaches the server and auth fails, exposing nothing.
39. File masking works on Linux and WSL2. On macOS it falls back to `deny`. Non-maskable entries (directories, globs, files over 8 MiB, non-UTF-8) fall back to `deny`.
40. Fields: `extract`, `decode: "jwt"`, `maskClaims`, `onExtractNoMatch` (`warn`, `deny`, `error`), `maskDuplicates`. Default `warn` leaves the file readable if nothing matches.
41. AWS: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_SESSION_TOKEN` link automatically; `awsPairs` groups custom names; the proxy re-signs SigV4. Unrecomputable forms fail unless `sigv4` forwards them.

### Policy

42. Managed Booleans override local values. Keys that weaken the sandbox (`enableWeakerNestedSandbox`, `enableWeakerNetworkIsolation`, `allowAllUnixSockets`, `allowLocalBinding`, `allowAppleEvents`, `allowNestedUserNamespaces`) SHOULD be set `false` in managed settings if unwanted; the last two are not settable by a repository.
43. Admin-required sandbox: `allowUnsandboxedCommands: false` from managed or `--settings`, or managed `allowManagedDomainsOnly: true`. Then repository files MUST NOT widen it: excluded commands, ignore-violations, domain lists, unix sockets, mach lookup and proxy ports are ignored; write-widening entries lose their sandbox effect; weakening Booleans' `true` is ignored; `enabled` and `failIfUnavailable` `false` are ignored when user settings say `true`; `allowRead` under denied paths is ignored.
44. Without admin-required, narrower locks apply (2.1.285): managed or `--settings` `deniedDomains` or WebFetch deny blocks repo proxy ports; `strictAllowlist` blocks repo proxy ports, domains and WebFetch allows; managed or `--settings` read denies block repo widening under those paths.
45. `allowManagedReadPathsOnly` and `allowManagedDomainsOnly` are managed-only, read from every admin source. Proxy ports: managed only under `allowManagedDomainsOnly`; managed, `--settings` and user under admin-required or narrower locks.
46. Server-managed sandbox binary, network, isolation and non-deny credential settings require approval ([managed-settings.md](managed-settings.md)).
47. `sandbox.ripgrep` is honoured only from user, managed and `--settings`.
48. `failIfUnavailable: true` MUST make startup exit when the sandbox cannot start. By default the client runs commands unsandboxed. If it fails after startup, each sandboxed command MUST be refused with `Sandbox is required...`; retries are refused and the session continues.

### Whole-process isolation

49. `srt claude` wraps the whole process. Config in `~/.srt-settings.json` or `--settings`. Invalid or missing `--settings` files MUST refuse to start; a missing default file MUST start with network blocked and writes confined. On Linux, its deny list is built once at launch and does not cover later-created nested repositories.
50. Organization enforcement exists only for the built-in sandbox; dev containers and VMs are conventions unless device management enforces them. Isolation does not change what is sent to the model.

## Configuration & interfaces

| Key | Notes |
|---|---|
| `sandbox.enabled`, `failIfUnavailable`, `autoAllowBashIfSandboxed`, `allowUnsandboxedCommands`, `excludedCommands` | Core |
| `sandbox.ignoreViolations` | Maps command substrings to violation substrings; suppresses the report only, and the access stays blocked |
| `sandbox.filesystem.*` | `allowWrite`, `denyWrite`, `denyRead`, `allowRead`, `allowManagedReadPathsOnly`, `disabled` |
| `sandbox.network.*` | `allowedDomains`, `deniedDomains`, `strictAllowlist`, `allowManagedDomainsOnly`, `allowUnixSockets` (macOS only; ignored on Linux and WSL2), `allowAllUnixSockets`, `allowLocalBinding`, `allowMachLookup`, `httpProxyPort`, `socksProxyPort`, `tlsTerminate` |
| `sandbox.credentials.*` | `files`, `envVars`, `allowPlaintextInject`, `awsPairs`, `sigv4` |
| `sandbox.bwrapPath`, `socatPath`, `ripgrep` | Binary overrides |
| `enableWeakerNestedSandbox`, `enableWeakerNetworkIsolation`, `allowAppleEvents`, `allowNestedUserNamespaces` | Weakening options |
| `CLAUDE_CODE_SUBPROCESS_ENV_SCRUB`, `CLAUDE_CODE_SCRIPT_CAPS` | Credential scrub for subprocesses; per-session script limits |
| `/sandbox` | Tabs Mode, Overrides, Config, Dependencies (Linux); writes to local settings; refuses when a higher level sets core keys |
| `claude doctor` warnings | Stale mask files, unreliable domain spellings, unmatchable `injectHosts`, `TLS termination is unavailable` |

## Failure modes & edge cases

- Effective sandboxing needs both layers: an `allowWrite`, broad domain or `excludedCommands` entry can undo the other side.
- Hostname allow decisions use the client-supplied name and do not inspect TLS by default, so broad domains carry exfiltration risk. Custom inspecting proxies are the documented stronger control.
- Unix-socket allowances, weak `$PATH` write grants and weakening options are documented privilege risks. `allowNestedUserNamespaces` removes the boundary, and restrictions cannot be relied on with it.
- Linux creates 0-byte read-only placeholders for write denials on missing files; a killed session leaves them, blocking settings saves until removed.
- Under a required-sandbox failure, excluded commands continue outside the sandbox unless the env-scrub session applies.
- macOS SSH git cannot authenticate through the tunnel; Linux can with an allowed host.

## Changes since the snapshot

- 2.1.92: `apply-seccomp` shipped. 2.1.97: `allowMachLookup` effective on macOS. 2.1.98: PID namespace sandboxing with env scrub; `CLAUDE_CODE_SCRIPT_CAPS`.
- 2.1.113: `deniedDomains`. 2.1.116: auto-allow no longer skips dangerous-path `rm` check. 2.1.126: managed locks ignored-source fix. 2.1.133: `bwrapPath`, `socatPath`.
- 2.1.157: startup banner removed. 2.1.181: `allowAppleEvents`. 2.1.187: `sandbox.credentials`. 2.1.191: session-remembered hosts.
- 2.1.216: `filesystem.disabled`. 2.1.219: `strictAllowlist`. 2.1.221: file mask. 2.1.224: `extract`, `decode`, `awsPairs`, `sigv4`. 2.1.229: bracketed IPv6.
- 2.1.232: `ripgrep` scope, approval for binary overrides, Linux protected-path hardening. 2.1.236: macOS wildcard read denies. 2.1.243: bash prompt stops listing hosts.
- 2.1.251: approval for TLS, proxy, credential and weakening settings; hardened output files. 2.1.257: stale mask warning, `awsPairs`/`ripgrep` whole-value merge. 2.1.260: `!` runs unsandboxed under strict mode.
- 2.1.271: per-command domains. 2.1.282, 2.1.285: repository lock rules. 2.1.284: local-address refusal per docs. 2.1.290: warning when managed settings ignore user entries. 2.1.292: strict mode allows env-prefixed interpreters to auto-run.
- 2.1.300: `claude remote-control --sandbox` removed. 2.1.305: `allowNestedUserNamespaces`. 2.1.309: excluded-command writes ask when sandbox cannot run. 2.1.310: AppArmor guidance.

## Open questions

- Whether the seccomp filter contributes any guarantee beyond Unix-socket blocking; docs name only that.
- Whether `allowLocalBinding` has any planned Linux equivalent.
