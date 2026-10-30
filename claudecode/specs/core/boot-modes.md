# Boot modes

**Status:** shipped
**Provenance:** both
**Sources:** docs cli-reference, headless, env-vars, errors, model-config; help.txt; snapshot `main.tsx`, `tools.ts`, `utils/envUtils.ts`; changelog 2.1.169, 2.1.248, 2.1.286, 2.1.299

## Purpose

Boot modes change what a session loads and what it may do, independent of the surface. Three exist beyond the default: bare (fast and hermetic for scripts), safe (troubleshooting), restricted (evaluation harnesses on shared machines). `-p` is a surface, not a boot mode, and combines with all three.

## Behaviour

### Comparison

| Aspect | Default | `--bare` | `--safe-mode` | `--restricted` |
| - | - | - | - | - |
| Purpose | Normal use | Reproducible scripted runs | Find a broken customization | Harness must not run commands or read local settings |
| CLAUDE.md, auto memory | Loaded | Not discovered | Not loaded | Not stated |
| User, project, local settings | Loaded | Not stated; `--settings` honoured | Customizations in them don't load | Ignored |
| Managed settings | Applied | Not stated | Applied, with exceptions below | Applied |
| Hooks | Loaded | Skipped | Skipped except policy-configured ones | Settings hooks only from managed settings or `--settings` |
| MCP servers | Loaded | Only those named on the command line | None, including policy-configured | Loaded unless `--strict-mcp-config` |
| Tools | Full set | Bash, file read, file edit, plus MCP from `--mcp-config` | Built-ins as normal | Removes command-running tools and WebFetch |
| Auth | All methods | API key or `apiKeyHelper` in `--settings`; third-party credentials | Normal | Normal |

### Bare mode

1. `--bare` or `CLAUDE_CODE_SIMPLE=1` MUST start in minimal mode. The flag sets the variable early, before module load (see [architecture-overview.md](architecture-overview.md)).
2. Bare mode MUST skip auto-discovery of hooks, skills, custom commands, subagents, installed plugins, MCP servers, auto memory and CLAUDE.md. It also skips LSP, plugin sync, attribution, background prefetches and keychain reads. Hooks built into Claude Code are unaffected.
3. Context MUST be supplied explicitly through `--system-prompt[-file]`, `--append-system-prompt[-file]`, `--add-dir`, `--mcp-config`, `--settings`, `--agents` and `--plugin-dir`.
4. A directory named by `--add-dir` is a partial exception: skills in its `.claude/skills/` load, while its `.claude/commands/` and `.claude/agents/` do not. Help text states skills still resolve through `/skill-name`.
5. OAuth tokens and keychain credentials MUST NOT be read. The Anthropic API credential must come from `ANTHROPIC_API_KEY` or an `apiKeyHelper` given through `--settings`. Bedrock, Agent Platform and Foundry use their own credentials as usual.
6. The tool set is Bash, file read and file edit, plus MCP tools from `--mcp-config`. Deny rules still filter it.
7. Since 2.1.286, bare mode MUST connect only the MCP servers named on the command line, send the model no system reminders, and start no background tasks. A shell command reaching its timeout stops instead of moving to the background.
8. System-prompt recording is off in bare mode outside cloud and background sessions unless `--system-prompt-snapshot on` is passed.
9. Background sessions preserve `--bare` across retire and wake (2.1.169).

### Safe mode

10. `--safe-mode` or `CLAUDE_CODE_SAFE_MODE=1` MUST disable CLAUDE.md, skills, plugins, hooks, MCP servers, custom commands and agents, output styles, workflows, custom themes, custom keybindings, status line and file-suggestion commands, LSP servers and auto memory.
11. Authentication, model selection, built-in tools, built-in plugins and permissions MUST work normally. This distinguishes it from bare mode.
12. Managed policy still applies, including policy-configured hooks, status line and file-suggestion commands. Managed plugins, managed skills, managed CLAUDE.md and policy-configured MCP servers do NOT load.
13. `--agents` is ignored under safe mode, so an invalid value cannot stop the launch.
14. The agents view shows a "safe mode" line for background sessions started this way (2.1.299).
15. Safe mode is the documented way to test whether a customization triggers a safety classifier (see [model-fallback.md](model-fallback.md)). Git status and directory names still reach the model.

### Restricted mode

16. `--restricted` or `CLAUDE_CODE_RESTRICTED=1` MUST start restricted. The variable is ignored in a settings file's `env` block.
17. Built-in tools that run commands or code (Bash, PowerShell and the other code-running tools) and WebFetch MUST be removed, unless named individually in `--tools`. Naming them through the `default` preset does not count.
18. User, project and local settings files MUST be ignored. Managed settings and `--settings` still apply.
19. MCP servers are unaffected unless `--strict-mcp-config` is added.
20. Built-in file tools MUST be confined to the working directories, including `--add-dir` entries.
21. `bypassPermissions` MUST be refused.
22. Writes to settings, git and tool-configuration files MUST be approvable only by a person or the configured permission handler.
23. Creating a cloud session from a restricted session MUST be refused, because the new session would run outside the restricted process.

### Non-interactive sessions

24. `-p` skips the workspace trust dialog and all prompts that need a terminal. What cannot be asked is decided by the permission mode and `--permission-prompts` (`host` or `none`). Details belong to the permissions and SDK spec areas.

## Configuration & interfaces

| Flag | Variable | Notes |
| - | - | - |
| `--bare` | `CLAUDE_CODE_SIMPLE` | Equivalent |
| `--safe-mode` | `CLAUDE_CODE_SAFE_MODE` | Equivalent |
| `--restricted` | `CLAUDE_CODE_RESTRICTED` | Since 2.1.248; not honoured from settings `env` |
| `--system-prompt-snapshot on\|off` | | Default depends on mode |
| `--strict-mcp-config` | | Only `--mcp-config` servers |
| `--tools` | | Exact list, `default` or `""` |

## Failure modes & edge cases

- `--bare` without `ANTHROPIC_API_KEY` or a helper on the Anthropic API fails as not logged in, even with a valid subscription login.
- A cloud-session attempt from `--restricted` fails with a dedicated refusal message.
- `--restricted --tools default` still lacks Bash and WebFetch.
- `CLAUDE_CODE_RESTRICTED=1` in settings has no effect, so a project cannot silently opt in or out.

## Changes since the snapshot

- 2.1.169: `--safe-mode` added.
- 2.1.169: background sessions preserve `--bare` and other flags across retire and wake.
- 2.1.248: `--restricted` added.
- 2.1.286: bare mode reduced further (command-line MCP only, no reminders, no background tasks, timed-out shell commands stop).
- 2.1.299: safe-mode line in the agents view.
- `--bare` itself predates the snapshot.

## Open questions

- Whether bare mode applies managed settings. Sources describe what it skips but do not state this.
- Help says bare mode skips hooks "defined in settings and by installed plugins", while docs say all hook discovery. Whether `--settings` hooks run in bare mode is unstated.
- Whether safe mode reads non-customization keys such as `model` from user settings. The docs say model selection works normally but do not give a key-by-key list.
- Exact list of "other code-running tools" removed by `--restricted`.
