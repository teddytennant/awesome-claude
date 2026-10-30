# Subagent Definitions and Built-in Agents

**Status:** shipped
**Provenance:** both (snapshot core; `omitClaudeMd`, `autoCompactWindow`, `experimental.cacheTtl`, `claude` agent post-leak)
**Sources:** docs `sub-agents`, `agents`, `tools-reference`, `agent-sdk/typescript`; snapshot `tools/AgentTool/loadAgentsDir.ts`, `builtInAgents.ts`, `built-in/*`, `agentMemory.ts`, `agentMemorySnapshot.ts`; changelog 2.1.198, 2.1.248, 2.1.271, 2.1.281, 2.1.295, 2.1.296, 2.1.312

## Purpose

A subagent definition is a named, reusable configuration: a system prompt plus limits on tools, model, permissions, MCP servers, hooks, memory and isolation. The model delegates to one by name, the user can force one, or a whole session can run as one. This spec covers how definitions are found, validated and resolved, and which agents ship in the box. Runtime behaviour is in [subagent-runtime.md](subagent-runtime.md).

## Behaviour

### Discovery and precedence

1. Definitions MUST load from these scopes, highest priority first: managed settings (`.claude/agents/` inside the managed settings directory), `--agents` CLI JSON, project `.claude/agents/`, user `~/.claude/agents/`, plugin `agents/`.
2. When two scopes define the same name, the higher-priority definition MUST win.
3. Project discovery MUST walk from the working directory up to the repository root, scanning every `.claude/agents/`. On a name collision the definition closest to the working directory MUST win (since 2.1.178).
4. `--add-dir` and `/add-dir` directories MUST also contribute their `.claude/agents/`.
5. Project and user directories MUST be scanned recursively. Subfolders MUST NOT affect identity, which comes only from `name`.
6. Two files with the same name in one directory tree load only one, in filesystem read order. `/doctor` MUST report such duplicates and propose a rename or removal.
7. Plugin `agents/` directories are scanned recursively, but subfolders MUST become part of the scoped identifier: `agents/review/security.md` in `my-plugin` is `my-plugin:review:security`.
8. A file watcher MUST pick up additions and edits in `~/.claude/agents/` and `.claude/agents/` within seconds, applying them to the next delegation. Exceptions needing a restart: a directory that did not exist at session start, `--add-dir` directories, and sessions started with `--disable-slash-commands`.
9. When the combined descriptions of non-built-in agents exceed 15,000 tokens, startup MUST warn with the total and still load every agent.

### File format and validation

10. A definition is Markdown with YAML frontmatter. The body is the system prompt. Only `name` and `description` are required.
11. Field names are camelCase and exact. Unknown fields MUST be ignored without a session-visible error. Since 2.1.296 the debug log MUST name up to five unknown top-level fields, with a suggested correction when one is close.
12. In project, user, managed and `--add-dir` directories the loader MUST skip a file, without any in-session report, if it has no `name`, has `---` not on line 1, has a name that starts with `-`, contains `:` or exceeds 256 characters, has a name but no `description`, or has unparseable YAML. The latter three kinds of error MUST be written to the debug log. A file with no `name` is treated as documentation.
13. A plugin agent with no `name` or unparseable frontmatter MUST still load, under its filename.
14. `claude plugin validate <dir>` MUST check a named `agents` directory for frontmatter that does not parse. It does not flag parseable frontmatter with no `name`.

### Frontmatter semantics

15. `tools` is an allowlist and `disallowedTools` a denylist. `disallowedTools` applies first, then `tools` resolves against what remains, so a tool in both is removed.
16. A `disallowedTools` entry with a specifier such as `Bash(git push *)` MUST remove the whole tool. Command-level blocks belong in `permissions.deny`.
17. Both fields accept whole-server entries: `mcp__server__*` in `tools`; `mcp__server`, `mcp__server__*` or `mcp__*` in `disallowedTools`. A server name containing `__` needs the trailing `__*` in `tools`. In `disallowedTools`, `mcp__reports` also withholds a server named `reports__v2`, because matching is by prefix.
18. Plugin agents MUST ignore `hooks`, `mcpServers` and `permissionMode`.
19. `Agent(type, ...)` inside `tools` is an allowlist only for an agent running as the main thread. In a subagent definition the parenthesised list MUST be ignored. `Task(...)` remains an alias of `Agent(...)`.
20. `skills` MUST preload full skill content, up to the first 32 distinct names (2.1.295). It MUST NOT limit which skills the agent can invoke. A skill with `disable-model-invocation: true` cannot be preloaded. A missing or disabled skill is skipped with a debug warning.
21. `memory` gives the agent a persistent directory. It MUST inject instructions plus the first 200 lines or 25 KB of that directory's `MEMORY.md`, whichever comes first, and MUST auto-enable Read, Write and Edit. If auto memory is off, the field MUST have no effect.
22. `omitClaudeMd: true` MUST exclude user, project and local CLAUDE.md from initial context while keeping managed policy files, except for a managed definition, which loads none. A subdirectory's CLAUDE.md and path-scoped rules still load when the agent touches files there. The field is ignored when the agent runs as the main session.
23. `autoCompactWindow` only lowers the window, never raises it. It accepts plain integers from 100000 to 1000000. `200k` is read as 200, is out of range, and is logged as `invalid autoCompactWindow`. It has no effect when the agent is the main session.
24. `initialPrompt` MUST auto-submit as the first user turn only when the agent is the main session. Commands and skills in it are processed, it is prepended to any user prompt, and plugin agents ignore it.
25. `experimental.cacheTtl` accepts `5m` or `1h`, is read only from subagent files, and is ignored for other values or for `1h` while a subscription uses usage credits.

### MCP servers and trust

26. `mcpServers` entries are either a name that reuses the parent's connection or an inline server config (stdio, http, sse, ws). Inline servers MUST connect at agent start and disconnect at its finish.
27. As a main session agent, inline servers connect at startup alongside other MCP configuration.
28. Inline servers from a project or `--add-dir` agent file MUST load only after the exact folder holding that file is trusted (2.1.238). Parent-folder trust and the implicit trust of `-p` or SDK sessions MUST NOT count. Untrusted files skip the servers and log the `hasTrustDialogAccepted` key needed.
29. Named references and inline servers from user, `--agents`, SDK or managed definitions MUST NOT need that trust check.
30. Managed MCP policy, `--strict-mcp-config` and `--bare` apply to frontmatter servers with a visible warning naming blocked servers. `--strict-mcp-config` MUST NOT filter inline servers passed through `--agents` or the SDK `agents` option (2.1.153).
31. Frontmatter hooks of a project agent MUST run only after the exact containing folder is trusted. The agent still runs without them, with a debug log error.

### Session-wide agents

32. `--agent <name>` or the `agent` setting runs the main thread as that agent. The flag beats the setting.
33. Unless the prompt is empty, the agent's prompt MUST replace the default system prompt. CLAUDE.md and project memory still load. With `-p` and a custom agent that has its own prompt, the git status snapshot is omitted.
34. An agent with an empty `prompt` and no `memory` selected this way MUST leave the session's system prompt unchanged (2.1.281).
35. Resume MUST restore the agent's tool limits and model. If the agent no longer exists the session continues with default tools and a warning naming it.
36. The startup header MUST show `@<name>`.
37. For a plugin agent the bare name MUST resolve; the scoped name disambiguates.

### Built-in agents

38. The following built-ins MUST be registered in interactive sessions. Each inherits the parent's permission rules.

| Agent | Model | Tools | Notes |
| --- | --- | --- | --- |
| `Explore` | Main model; see rule 39 | Read-only, Write/Edit denied | No CLAUDE.md or git status. Caller states thoroughness: quick, medium, very thorough. One-shot |
| `Plan` | Inherit | Read-only | Used in plan mode. No CLAUDE.md or git status. One-shot |
| `general-purpose` | `CLAUDE_CODE_SUBAGENT_MODEL` if nothing else assigns one, else main | All subagent tools | Fallback when `subagent_type` is omitted |
| `claude` | None of its own; subagent model order | All subagent tools | Catch-all; default for dispatched background sessions |
| `statusline-setup` | Sonnet | Not stated | `/statusline` |
| `claude-code-guide` | Haiku | Not stated | Questions about Claude Code |

39. When the main conversation runs Fable, Explore MUST run on the `opus` alias model for subscription, Console and `ANTHROPIC_BASE_URL` gateway connections, and stay on the main model for Bedrock, Google Cloud's Agent Platform, Foundry, Claude Platform on AWS and Claude apps gateways.
40. A user or project agent named `Explore` MUST override the built-in and keep its own `model`.
41. An Agent call that omits `subagent_type` MUST fail with `subagent_type is required` when no `general-purpose` agent exists.
42. Built-ins MUST be removable: `permissions.deny` with `Agent(<name>)` per type, deny `Agent` for all delegation, `CLAUDE_CODE_DISABLE_EXPLORE_PLAN_AGENTS=1` for Explore and Plan, and `CLAUDE_AGENT_SDK_DISABLE_BUILTIN_AGENTS=1` for all, in non-interactive mode only.

### Invocation

43. Delegation is driven by `description` matching. `@"name (agent)"` or `@agent-<name>` MUST guarantee that the named agent is invoked. The user's whole message still goes to the model, which writes the task prompt.
44. `subagent_type` matching MUST accept case- and separator-insensitive values, so `Code Reviewer` resolves to `code-reviewer` (2.1.140).
45. `/agents` MUST print a notice with the file locations. The interactive wizard was removed in 2.1.198.

## Configuration & interfaces

### Frontmatter

| Field | Values | Since / notes |
| --- | --- | --- |
| `name` | up to 256 chars, no `:`, no leading `-` | required; hooks see it as `agent_type` |
| `description` | text | required |
| `tools`, `disallowedTools` | comma string or YAML list | |
| `model` | `sonnet`, `opus`, `haiku`, `fable`, full ID, `inherit` | |
| `permissionMode` | `default`, `manual` (alias), `acceptEdits`, `auto`, `dontAsk`, `bypassPermissions`, `plan` | subject to parent mode |
| `maxTurns` | integer | partial marking 2.1.246 |
| `autoCompactWindow` | 100000 to 1000000 | 2.1.296 |
| `skills` | list | cap 32 |
| `mcpServers` | list | |
| `hooks` | hook config | `Stop` converts to `SubagentStop` |
| `memory` | `user`, `project`, `local` | `~/.claude/agent-memory/<n>/`, `.claude/agent-memory/<n>/`, `.claude/agent-memory-local/<n>/` |
| `background` | boolean | |
| `omitClaudeMd` | boolean | 2.1.271 |
| `effort` | `low`, `medium`, `high`, `xhigh`, `max` | |
| `isolation` | `worktree` | |
| `color` | `red`, `blue`, `green`, `yellow`, `purple`, `orange`, `pink`, `cyan` | |
| `initialPrompt` | text | main session only |
| `experimental` | map; `cacheTtl` | 2.1.248 |

### `--agents` JSON

An object keyed by agent name. Each value takes `prompt` plus the frontmatter fields except `color` and `experimental`, which are ignored rather than rejected. In `-p` mode the value may be a path to a JSON file; interactive mode MUST refuse a path (2.1.281). A name may not start with `-`.

### SDK

`AgentDefinition` mirrors these fields and adds `criticalSystemReminder_EXPERIMENTAL`. `effort` also accepts an integer there.

## Failure modes & edge cases

- Every `tools` entry unresolved: the Agent tool usually refuses to launch, naming the entries.
- `autoCompactWindow` above the inherited window or invalid: silently no effect apart from the debug log entry.
- First agent file in a brand-new directory: not seen until restart.
- Definition removed while a resumed session references it: warning and default tools.
- Task tools are absent from subagents in sessions without them, even if the subagent's model would otherwise qualify.

## Changes since the snapshot

- 2.1.140: case- and separator-insensitive `subagent_type`.
- 2.1.153: strict MCP no longer strips explicitly passed inline servers; blocked servers warn.
- 2.1.178: closest nested `.claude/` wins name collisions.
- 2.1.198: `/agents` wizard removed. Explore moved from Haiku to the main model, capped at Opus.
- 2.1.238: folder trust required for inline MCP servers from project agent files.
- 2.1.248: `experimental.cacheTtl`.
- 2.1.271: `omitClaudeMd`.
- 2.1.281: empty `prompt`; `--agents` file path in `-p`.
- 2.1.295: 32-skill preload cap.
- 2.1.296: `autoCompactWindow`, unknown-field debug logging.
- 2.1.312: `autoCompactWindow` lowers a window set by `CLAUDE_CODE_AUTO_COMPACT_WINDOW`.

## Open questions

- Docs still state that `CLAUDE_CODE_AUTO_COMPACT_WINDOW` overrides the field, while the 2.1.312 changelog says the field lowers it. The changelog is newer; confirm.
- Snapshot-only: a gated `verification` built-in (read-only, background, inherit model). Not documented now; current status unknown. A bundled `/verify` skill exists separately.
- Snapshot-only: agent memory snapshots under `.claude/agent-memory-snapshots/<agent>/`, gated. Not documented now.
- Exact tool lists for `statusline-setup` and `claude-code-guide` in 2.1.314.
