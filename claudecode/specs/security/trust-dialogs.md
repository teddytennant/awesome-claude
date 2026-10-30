# Trust Dialogs and Configuration Trust

**Status:** shipped
**Provenance:** both; repository-supplied configuration rules reshaped post-leak
**Sources:** docs `permissions`, `security`, `settings-reference`, `errors`, `mcp` (referenced); snapshot `components/TrustDialog/`, `interactiveHelpers.tsx`, `utils/config.ts`, `utils/auth.ts`, `services/mcp/headersHelper.ts`; changelog 2.1.196–2.1.314

## Purpose

A cloned repository is untrusted input that can carry settings, hooks, MCP servers and helper commands. Trust dialogs make the user decide before a repository's capability-granting configuration takes effect, and scope rules keep repository files from loosening protections.

## Behaviour

### When the dialog appears

1. Interactive sessions MUST show the workspace trust dialog at start in a folder not yet trusted. In the snapshot, declining exits the process.
2. `-p` and SDK sessions MUST NOT show it.
3. `claude --bg` and `claude agents` MUST check trust first: on a terminal, ask; where no dialog can appear, exit with `Workspace not trusted`. `claude remote-control` asks on the terminal in untrusted folders. `claude ultrareview` and `/ultrareview` require trust before running git, with `--trust-workspace` for scripts.
4. `/cd` to an untrusted directory MUST prompt listing the allow rules, directories, hooks and helpers that would activate. Declining stays put. After a move, the directory's project configuration applies as at startup, including `.mcp.json` approval.

### What the dialog shows

5. The dialog MUST list what the folder would grant: allow rules, additional directories, hooks, helper commands (`apiKeyHelper`, `otelHeadersHelper`, cloud auth), dangerous environment settings, MCP servers.
6. It MUST name the repository root the grant covers (2.1.218).

### Keying and persistence

7. In a repository, trust is keyed on the git root, in a worktree on the main checkout's root, and covers everything except nested git repositories.
8. Outside a repository, trust is keyed on the start directory and covers subdirectories, except nested repositories.
9. Starting directly in the home directory MUST hold trust for the session only, never written to disk. There is no setting to persist it.
10. Trust is stored as a per-project `hasTrustDialogAccepted` flag in the user's global config. Once true it does not revert in a session, and acceptance is picked up mid-session.
11. Nested repositories MUST show their own dialog; parent trust does not extend to them.

### What needs trust

12. Project `permissions.allow` and `additionalDirectories` MUST apply only after acceptance for that folder. `deny` and `ask` always apply.
13. `.claude/settings.local.json` is normally the user's own and applies without trust. When tracked in git, or when `.claude` is a symlink, it MUST be treated as repository-supplied. Git MUST run only once the folder is trusted, or in `-p` and SDK. Until then, rules are applied directly in the configuration home and held elsewhere. After the check, untracked files or those outside any repository apply.
14. Situations for an untrusted exact folder:

| Repository content | Only a parent trusted | `-p` or SDK, never trusted |
|---|---|---|
| Settings hooks, `env`, helpers; project skill hooks and `allowed-tools` | Used | Used |
| `permissions.allow`, `additionalDirectories` | Held; dialog reappears | Held; stderr warning |
| Project subagent frontmatter hooks; `@skills-dir` plugins; repo `extraKnownMarketplaces` | Not used, no dialog | Not used |
| Inline `mcpServers` in subagent frontmatter | Not used, no dialog | Not used |
| `.mcp.json` servers | Ask; repo self-approvals do not count | Connected; SDK needs project settings source |
| `headersHelper` in `.mcp.json` | Not run; connect with static headers | Not run; stderr line |

15. Workspace trust never gates a skill's `allowed-tools` in any session.
16. Trusting a parent MUST NOT count for rows needing the exact folder.
17. `claude mcp list` and `get` MUST NOT spawn repo-self-approved `.mcp.json` servers; untrusted workspaces show pending (2.1.196).
18. Project `headersHelper` runs without inherited credential variables (2.1.238).

### Repository scope limits

19. Regardless of trust, project and local settings MUST NOT:
    - set `autoMode`, or `defaultMode` to `auto` or `bypassPermissions`;
    - set `CLAUDE_CONFIG_DIR`, `CLAUDE_CODE_TMPDIR`, directory variables, Windows program and configuration variables, content-exporting variables or telemetry-enabling variables through `env`;
    - set `CLAUDE_CODE_DISABLE_ATTACHMENTS`, `axScreenReader`;
    - configure `processWrapper` or `CLAUDE_CODE_PROCESS_WRAPPER`;
    - set `sandbox.filesystem.disabled`, `strictAllowlist`, `mask` credentials, `tlsTerminate`, `allowPlaintextInject`, `awsPairs`, `sigv4`, `ripgrep`, `allowAppleEvents`, `allowNestedUserNamespaces`;
    - skip the bypass warning.
20. Repository `useAutoModeDuringPlan`, `syncClaudeAiSkills`, `syncClaudeAiPlugins` set `false` in `.claude/settings.json` are ignored.
21. A startup notice, `/status` and `claude doctor` MUST list telemetry variables ignored from project files.
22. Under admin-required sandbox and related locks, repository widening is ignored ([os-sandbox.md](os-sandbox.md)).
23. Writes to configuration MUST be protected: `.claude`, `.mcp.json`, settings files and hooks directories are protected paths for tools and the sandbox.

### Other trust prompts

24. API key approval: an `ANTHROPIC_API_KEY` is approved once interactively.
25. `bypassPermissions` warning ([permission-modes.md](permission-modes.md)).
26. Plugin trust warning before install, with managed `pluginTrustMessage`; marketplaces from untrusted sources error.
27. Server-managed approval ([managed-settings.md](managed-settings.md)).
28. Auto-mode opt-in notice and first-read prompt ([auto-mode.md](auto-mode.md)).
29. `.mcp.json` server approval is separate from workspace trust; repo-side approvals do not count without trust.
30. Cross-session messages MUST carry no user authority: receivers refuse relayed permission requests, and inbound messages to a bypassed session are held.
31. In the snapshot, every hook checks workspace trust before running in interactive sessions.

### Guidance for unknown repositories

32. Documented safer options for `-p` in unknown repositories: restrict setting sources, start bare, or turn off hooks via `--settings`; reject servers by name. Bare mode still applies project `env` and helpers.

## Configuration & interfaces

| Interface | Notes |
|---|---|
| `hasTrustDialogAccepted` | Per-project state in `~/.claude.json` |
| `--setting-sources`, SDK `settingSources` | Exclude sources |
| `--bare`, `--safe-mode`, `--restricted` | Reduced configuration modes |
| `disabledMcpjsonServers` | Reject `.mcp.json` servers by name |
| `--trust-workspace` | `claude ultrareview` scripting |
| Errors | `Workspace not trusted`, `this workspace has not been trusted`, `headersHelper not run` |

## Failure modes & edge cases

- `settings.local.json` in the home directory applies only in sessions started there; it is not global.
- `CLAUDE_CONFIG_DIR` inside a repository whose local settings live at the root holds rules as usual.
- Home-directory `claude rc` errors explain that trust is never saved there.
- Versions 2.1.196–2.1.199 treated users' local settings as repository-supplied in some workspaces.

## Changes since the snapshot

- 2.1.196: repo-approved `.mcp.json` no longer spawned by `claude mcp list`. 2.1.207: `autoMode` local ignored. 2.1.214: `claude rc` home error. 2.1.218: dialogs name the root. 2.1.225: `claude agents` prompt.
- 2.1.238: `headersHelper` and inline MCP trust. 2.1.246: `/cd` applies configuration and lists grants (per docs). 2.1.251, 2.1.285, 2.1.290, 2.1.307: project `env` narrowing. 2.1.257: `defaultMode: bypassPermissions` ignored.
- 2.1.282: project OTel variables ignored with notice. 2.1.284: `remote-control` asks. 2.1.309, 2.1.314: `ultrareview` trust.
- 2.1.166, 2.1.224: cross-session authority and holds.

## Open questions

- Docs describe settings hooks as "used" with only a parent trusted, and in `-p`. The behaviour with no trust at all in an interactive session is confirmed only by the snapshot.
- Exact current dialog contents: the snapshot list may have grown.
- The trust key's normalization rules on Windows are not stated.
