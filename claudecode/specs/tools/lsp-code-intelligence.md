# LSP Tool and Code Intelligence

**Status:** shipped
**Provenance:** both
**Sources:** docs `tools-reference` (LSP), `plugins/code-intelligence`, `plugins/components`, `plugins/manifest-reference`, `sub-agents`; snapshot `tools/LSPTool`, `tools.ts`; changelog 2.1.89, 2.1.98, 2.1.162, 2.1.208, 2.1.280, 2.1.288

## Purpose

Give Claude editor-grade diagnostics and symbol navigation by connecting to a language server. The model gets both automatic diagnostics after edits and an explicit navigation tool.

## Behaviour

### Activation

1. The tool MUST stay inactive until a code intelligence plugin for the language is installed. The snapshot required `ENABLE_LSP_TOOL`; the current gate is the plugin.
2. Plugin language servers MUST NOT start in cloud sessions, so the tool stays inactive there.
3. Plugins supply configuration only. The server binary is a separate install, started by name from the user's `PATH`.
4. A server starts the first time Claude edits a file with a matching extension.
5. Safe mode (`CLAUDE_CODE_SAFE_MODE=1`) MUST NOT load LSP servers.

### Automatic diagnostics

6. After each file edit, type errors and warnings MUST be reported to Claude so it can fix them without a build step.
7. The transcript shows `Found N new diagnostic issues in M files (ctrl+o to expand)`. Summaries expand on click or `ctrl+o` (2.1.121).
8. Diagnostics from before an edit MUST NOT appear after it (fixed 2.1.111).

### Navigation operations

9. Operations:

| Operation | Purpose |
| :- | :- |
| `goToDefinition` | Symbol's definition |
| `findReferences` | All references |
| `hover` | Docs and type at a position |
| `documentSymbol` | Symbols in a file |
| `workspaceSymbol` | Search across the workspace, with `query` (2.1.162) |
| `goToImplementation` | Implementations of an interface or abstract method |
| `prepareCallHierarchy` | Call hierarchy item at a position |
| `incomingCalls` | Callers |
| `outgoingCalls` | Callees |

10. Each call takes `operation`, `filePath`, `line`, `character`, the last two 1-based as in editors (snapshot schema). The SDK reference publishes no `LSP` input type.
11. Claude Code MUST return an error result for each call on a file whose server cannot start.
12. Requests MUST time out, 60 seconds by default, per-server `requestTimeout` (2.1.288), so a server using dynamic registration or stopping responding cannot hang the call.
13. Snapshot details not confirmed as current: results filtered of gitignored locations; files over 10 MB skipped; result size cap 100,000 characters.

### Server lifecycle

14. Claude Code identifies itself through `clientInfo` in `initialize` (2.1.98).
15. A crashed server restarts on the next request (2.1.89), subject to `restartOnCrash` (default `true`) and `maxRestarts`.
16. Open documents are held in an LRU with a 50-document cap (2.1.208).
17. At session end, `exit` MUST be sent even if `shutdown` fails (2.1.269). `shutdownTimeout` bounds graceful shutdown.
18. A server that fails to initialize MUST NOT stop another plugin's valid server handling the same extension (2.1.205).
19. A server's stdout is protocol only, with headers up to 64 KiB and bodies up to 32 MiB. Exceeding either, or writing non-protocol output, disconnects the server and counts as a crash.
20. `/reload-plugins` drops the tool when the last LSP plugin is disabled, and warns before an LSP plugin change that would re-read the conversation (2.1.243).

### Permissions and subagents

21. The tool is not permission-gated in Manual mode. `Read(...)` path rules cover it.
22. Background subagents have `LSP` (v2.1.280+).

### Recommendation dialog

23. A dialog titled **LSP plugin recommendation** MAY appear after Claude edits a file, when a marketplace lists a plugin for that extension and the binary is installed.
24. The official marketplace's plugin is preferred, the dialog appears at most once per session, and never when attached to a cloud session.
25. The offer waits until the user has sent or cleared what they are typing (2.1.251).

## Configuration & interfaces

`.lsp.json` at the plugin root, or the `lspServers` manifest key (path, inline object, or array). A manifest server with the same name replaces the `.lsp.json` entry.

| Field | Required | Meaning |
| :- | :- | :- |
| `command` | Yes | Binary name |
| `args` | No | Arguments |
| `extensionToLanguage` | Yes | At least one `.ext` to language mapping |
| `transport` | No | Transport |
| `initializationOptions` | No | Sent in `initialize`; `${user_config.*}` and `${CLAUDE_PLUGIN_ROOT}` are substituted (2.1.288) |
| `startupTimeout` | No | Milliseconds |
| `shutdownTimeout` | No | Milliseconds |
| `requestTimeout` | No | Milliseconds; default 60000 (v2.1.288+) |
| `restartOnCrash` | No | Default `true` |
| `maxRestarts` | No | Restart attempts |

Official plugins exist for C/C++, C#, Go, Java, Kotlin, Lua, PHP, Python, Ruby, Rust, Swift and TypeScript/JavaScript; `liquid-lsp` is listed and maintained by Shopify. The binary-to-plugin mapping is in `plugins/code-intelligence`.

`lsp` is a kind name for `CLAUDE_CODE_TOOL_MEMORY_CGROUP_EXCLUDE`.

## Failure modes & edge cases

- Invalid entries skip the whole `.lsp.json`, reported as `Invalid LSP server config for ".lsp.json"` in the `/plugin` **Errors** tab. `claude plugin validate` does not read that file. Unknown keys in `lspServers` are errors, and the plugin does not load.
- A missing binary logs `LSP server <name> failed to start` and shows `Executable not found in $PATH: "<binary>"`. Claude Code retries on the next matching edit.
- Two servers on one extension: the first registered wins, with `LSP server "<name>" is not used for <ext> files`.
- A server exiting or closing stdin used to end `--bg` sessions (fixed 2.1.277).
- Binary detection's POSIX `which` fallback had a command injection flaw (fixed 2.1.101).

## Changes since the snapshot

- 2.1.89: crash recovery.
- 2.1.98: `clientInfo`.
- 2.1.111: stale diagnostic ordering fixed.
- 2.1.121: expandable diagnostics summaries.
- 2.1.162: `workspaceSymbol` takes `query`.
- 2.1.208: 50-document LRU.
- 2.1.243: `/reload-plugins` handling.
- 2.1.269: `exit` always sent.
- 2.1.280: background subagent access.
- 2.1.288: 60-second request timeout; config placeholder substitution.

## Open questions

- Whether `filePath`, `line` and `character` remain required for `workspaceSymbol` now that it takes `query`; the snapshot required all three.
- Whether the snapshot's gitignore filtering and 10 MB limit remain.
- Supported `transport` values.
- Whether `ENABLE_LSP_TOOL` still has any effect; it is not in current `env-vars`.
