# Search Tools: Glob, Grep, ToolSearch

**Status:** shipped
**Provenance:** both
**Sources:** docs `tools-reference` (Glob, Grep), `mcp` (tool search), `agent-sdk/tool-search`, `agent-sdk/typescript`, `env-vars`, `sub-agents`; snapshot `tools/GlobTool`, `tools/GrepTool`, `tools/ToolSearchTool`; changelog 2.1.117, 2.1.162, 2.1.221, 2.1.287, 2.1.295, 2.1.304

## Purpose

`Glob` and `Grep` find files by name and content. On most platforms they are no longer in the default tool set, replaced by embedded search commands in Bash. `ToolSearch` is a different kind of search: it discovers deferred tool definitions and loads them on demand.

## Behaviour

### Default availability of Glob and Grep

1. On Windows, Glob and Grep MUST be in the default tool set.
2. On macOS, Linux and WSL they MUST be left out by default (native builds since 2.1.117). Claude searches with `find` and `grep` in Bash, which in Claude's shell run embedded `bfs` and `ugrep`. Those searches reach hooks and permission rules as `Bash` calls.
3. On macOS, Linux and WSL the tools MUST return when any of these holds:
   - `--tools` or `--allowedTools` names them at session start, or the SDK equivalents. `--tools` gives only those listed; naming either in `--allowedTools` restores both. An allow rule in a settings file does not have this effect.
   - A deny rule, `--disallowedTools` or `--restricted` removes `Bash`.
   - A subagent lists `Glob` or `Grep` in `tools` and omits `Bash`. They return for that subagent only, or for the whole session when it is the main-session agent through `--agent` or the `agent` setting.
4. `Read(...)` rules apply to Grep and Glob as path rules.

### Glob

5. Input is `pattern` and optional `path`. Standard glob syntax, including `**`.
6. Results MUST be sorted by modification time and capped at 100 files, with a truncation flag so Claude can narrow.
7. `totalMatches` (v2.1.191+) reports the pre-truncation count. When `countIsComplete` is false it is a lower bound.
8. Glob MUST ignore `.gitignore` by default, and includes dotfiles by default.
9. Permission MUST be decided before checking whether the directory exists, so a prompt for a path does not imply the path exists. The read-permission check still runs for a missing `path` outside the working directories.
10. A `pattern` or `path` containing a null byte MUST return an error.

### Grep

11. Built on ripgrep regex syntax, not POSIX grep.
12. A pattern, glob or type that ripgrep rejects MUST return an error with ripgrep's diagnostic (v2.1.208+). Earlier versions reported `No files found`.
13. `output_mode` is one of:
    - `files_with_matches` (default): paths only.
    - `content`: matching lines with file and line number. An `offset` past the last match of a matching pattern returns `No entries at this offset`, so Claude does not conclude there are no matches.
    - `count`: per-file counts then a total. The total covers all matches even when `head_limit`/`offset` trim the list.
14. Scoping is by `glob` or `type`. Matching is per line unless `multiline: true`.
15. Grep MUST respect `.gitignore`. To search an ignored file, Claude passes its path directly.
16. Permission ordering matches Glob (requirement 9).
17. Input tolerance: `file_path` is accepted for `path` (2.1.292), and a search sent with grep's `-l`, `-c` or `-r` flag runs rather than failing (2.1.295).

### ToolSearch

18. When tool search is active, tool definitions MUST be withheld from the context. Only names and server instructions load at session start, and the model searches when it needs a capability.
19. Up to five relevant tools load by default. They stay available for subsequent turns until compaction removes the messages that discovered them, after which the model searches again.
20. The wait for an MCP server still connecting happens inside the `ToolSearch` call when tool search is on. Otherwise `WaitForMcpServers` does it.
21. Core built-ins such as Bash, Read and Edit MUST load upfront and not count toward the `auto` threshold. Built-ins that load on demand, and MCP tools not marked `alwaysLoad`, are deferrable.
22. When a server finishes connecting mid-turn, its tool names MUST be listed to the model on the next request in that turn.
23. Mid-session MCP and plugin tools on supported models arrive as deferred definitions (2.1.267), to preserve prompt-cache reuse.

Snapshot behaviour, not confirmed in public docs: input is `query` plus `max_results` (default 5). `select:<name>` selects directly and `+term` marks a required term; other terms score on tool-name parts and hints. The result carries matched names, the query, the total deferred count and any pending MCP servers.

### When tool search is on

24. Default: on, deferring all MCP tools.
25. Forced upfront loading, not overridable by `ENABLE_TOOL_SEARCH=true`:
    - Models earlier than Opus 4, Sonnet 4, Haiku 4.5.
    - On Google Cloud's Agent Platform, models earlier than Opus 4.5, Sonnet 4.5, Haiku 4.5 (their serving stack rejects the required beta header).
    - Microsoft Foundry deployments hosted on Azure, detected from the server-side rejection.
26. `CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS` keeps it off and cannot be overridden by `ENABLE_TOOL_SEARCH`. Managed settings can keep it on under that variable (v2.1.227+).
27. HIPAA-configured sessions: off, not overridable.
28. Behind `ANTHROPIC_BASE_URL`: on by default (2.1.304). After a `400` or `422` of unrecognised cause, Claude Code MAY retry without it (v2.1.305+), load tools upfront, and try again later.
29. Denying `ToolSearch`, or omitting it from `--tools`, loads MCP tools upfront, though a request can still carry a placeholder `defer_loading` entry.

## Configuration & interfaces

| `ENABLE_TOOL_SEARCH` | Behaviour |
| :- | :- |
| unset or `true` | MCP tools deferred, with the fallbacks above |
| `auto` | Upfront while definitions total under 10% of context; deferred at or over that, and can stay deferred if the total later falls |
| `auto:N` | Same with threshold N (0 to 100) |
| `false` | All upfront |

| Key | Effect |
| :- | :- |
| `alwaysLoad` (server config) | `true` exempts a server and makes startup wait, capped at the 5-second connect timeout; `false` defers all its tools (v2.1.287+) |
| `_meta["anthropic/alwaysLoad"]` | Per-tool upfront or deferred preference (`false` needs v2.1.285+) |
| `isDeferred` on mod `$.tool.register` | `false` lists the schema from the start (2.1.293) |
| `CLAUDE_CODE_MAX_MCP_DESCRIPTION_LENGTH` | Replaces both description limits (v2.1.280+) |
| `CLAUDE_CODE_GLOB_NO_IGNORE` | `false` makes Glob respect `.gitignore` |
| `CLAUDE_CODE_GLOB_HIDDEN` | `false` excludes dotfiles |
| `CLAUDE_CODE_GLOB_TIMEOUT_SECONDS` | Discovery timeout; default 20, 60 on WSL |
| `USE_BUILTIN_RIPGREP` | `0` uses system `rg` |

Description limits: 4,096 characters for server instructions and upfront tools; 16,384 for tools loaded through tool search. Matching reads only the shorter limit, so searchable words belong near the start.

## Failure modes & edge cases

- Gateways that reject `defer_loading` or `tool_reference` produce "Extra inputs are not permitted"-class errors; the retry path covers unrecognised causes.
- `/context` may show `(deferred)` under the `auto` threshold because tool search stayed on once active.
- A 2.1.304 regression failed every request when an endpoint rejected tool search; fixed in 2.1.305.
- `--tools` naming Grep or Glob on embedded-search builds was silently ignored before 2.1.162.
- Embedded `grep`: pathological patterns fail fast (2.1.235).

## Changes since the snapshot

- 2.1.117: Glob and Grep replaced by embedded `bfs`/`ugrep` on native macOS and Linux builds.
- 2.1.122, 2.1.126: ToolSearch finds late-connecting MCP tools; deferred tools available to forked skills on their first turn.
- 2.1.162: `--tools` restores Grep and Glob.
- v2.1.191, v2.1.208, v2.1.210: `totalMatches`, `totalFiles`, `totalLines`, ripgrep diagnostics, count totals over the full set.
- 2.1.221: tool search re-enabled on Agent Platform for 4.5-generation and newer.
- 2.1.274: stream-json first turn no longer waits for deferred MCP servers.
- 2.1.287: `alwaysLoad: false` defers a whole server.
- 2.1.292, 2.1.295: Grep input tolerance; deferred description limit raised to 16,384.
- 2.1.304: on by default behind a gateway.

## Open questions

- Whether `select:` and `+term` query syntax and the snapshot's scoring are still current.
- The exact set of built-ins deferred today.
- The refresh rate and any cap on re-trying tool search behind a gateway.
- Whether `totalFiles`/`totalLines` behave the same under embedded search.
