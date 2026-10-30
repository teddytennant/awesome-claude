# Tool system contract

**Status:** shipped
**Provenance:** both
**Sources:** docs tools-reference, mcp (tool search), agent-sdk/tool-search, agent-sdk/agent-loop, prompt-caching, llm-gateway-protocol, errors; snapshot `Tool.ts`, `tools.ts`, `services/tools/`, `tools/ToolSearchTool/`, `utils/toolSearch.ts`, `utils/toolResultStorage.ts`, `constants/toolLimits.ts`; comparison tools.md; changelog 2.1.101, 2.1.119, 2.1.154, 2.1.161, 2.1.221, 2.1.233, 2.1.268, 2.1.293, 2.1.304

## Purpose

Defines what every tool must provide, how the tool pool is assembled, how calls run and how results reach the model. Individual tool behaviour is out of scope here.

## Behaviour

### Tool definition

1. A tool MUST declare: `name`, input schema, description and prompt text, `call`, permission check, result-to-API mapping, `maxResultSizeChars`, and display hooks. Renamed tools MAY keep `aliases`, which resolve in lookups.
2. Defaults MUST fail closed where it matters: not concurrency-safe, not read-only, not destructive, enabled, no tool-specific permission logic, and skipped by the auto-mode classifier unless overridden. Security-relevant tools MUST override the classifier default.
3. Optional attributes: `isConcurrencySafe(input)`, `isReadOnly(input)`, `isDestructive(input)`, `interruptBehavior()` (`cancel` or `block`, default `block`), `shouldDefer`, `alwaysLoad`, `searchHint`, `strict`, `backfillObservableInput`, `validateInput`, `getPath`, `preparePermissionMatcher`, `toAutoClassifierInput`, `inputsEquivalent`.
4. `backfillObservableInput` works on copies of the input before observers (SDK stream, transcript, permission callback, hooks) see it. The API-bound input MUST NOT change, to protect the prompt cache.
5. MCP tools carry `mcpInfo` and may supply a JSON Schema directly.
6. Skills are not tools. They run through the `Skill` tool. The advisor is a server tool with no name usable in permission rules or hook matchers.

### Pool assembly

7. Built-in tools MUST be filtered in this order: mode restrictions (bare, restricted), blanket deny rules, `isEnabled()`.
8. A deny rule removes a tool from the pool only when it matches in the tool-name position: a bare name, `Tool(*)`, or a tool-name glob. Scoped rules are checked at call time. MCP server-prefix rules strip that server's tools.
9. Built-in and MCP partitions MUST each be sorted by name and concatenated, built-ins first, then deduplicated with built-ins winning. A flat sort would let an MCP tool shift built-ins and break cache keys.
10. `--tools` restricts built-ins, with `""` for none and `default` for the default set. `--allowedTools` changes permissions, not availability. Naming a task-tracking tool in either flag opts the session into those tools.
11. Tool names offered to the API MUST be valid: an MCP tool whose full name exceeds 128 characters is left out.
12. In 2.1.314 docs: `Glob` and `Grep` are absent by default on macOS, Linux and WSL, where Claude searches with `find` and `grep` through Bash, backed by embedded `bfs` and `ugrep`, so those searches reach hooks and permission rules as `Bash`. `TaskOutput` was removed in 2.1.277. Task-tracking tools are offered by default only on Opus 4.7, Sonnet 4.6, Haiku 4.5 and earlier unless `CLAUDE_CODE_ENABLE_TODO_TOOLS=1` (2.1.268), and always in background and cloud sessions.

New since the snapshot by name: `Artifact`, `EndConversation`, `ListAgents`, `Monitor`, `PushNotification`, `ReportFindings`, `ScheduleWakeup`, `SendFeedback`, `SendUserFile`, `ShareOnboardingGuide`, `SubagentHandback`, `WaitForMcpServers`, `Workflow`.

### Call pipeline

13. For each `tool_use`, in order: look up by name or alias; parse input against the schema; run `validateInput`; run `PreToolUse` hooks; check permissions; execute; map the result; persist if oversized; run `PostToolUse` hooks (or `PostToolUseFailure`).
14. An unknown tool name MUST return an error result to the model, and the turn continues. If the tool exists but is unavailable in this context, the error explains why and how to proceed (2.1.101).
15. Schema failures MUST return an `InputValidationError` tool result rather than throw.
16. `validateInput` failures inform the model and show no permission UI.
17. A hook may modify input, block, defer, or stop execution with a reason. A hook's `updatedInput` owns its shape, so backfill is not reapplied.
18. Every failure path MUST yield a `tool_result` with `is_error: true`. Error results carry text only inside `tool_result`, with any images as sibling blocks.

### Concurrency

19. A tool's concurrency safety is input-dependent. If parsing or `isConcurrencySafe` throws, the call MUST be treated as unsafe.
20. Calls are partitioned in order into batches: consecutive safe calls form one concurrent batch, and each unsafe call forms a batch of one. Order between batches is preserved. Snapshot concurrency cap: 10, set by `CLAUDE_CODE_MAX_TOOL_USE_CONCURRENCY`, not publicly documented.
21. Context modifiers from a concurrent batch MUST be applied after the batch, in the original call order. Serial tools apply them immediately.
22. Streaming execution starts tools as their blocks complete, subject to the same safety rule, and yields results in call order.
23. Each result stands on its own: a failed Bash command no longer cancels other calls in the same batch (2.1.161). The snapshot's sibling-abort behaviour is superseded on this point.
24. On user interrupt, only tools whose `interruptBehavior` is `cancel` stop; `block` tools run on and the new message waits.
25. On streaming fallback, queued tools MUST NOT start and in-flight tools receive synthetic errors. See [query-loop.md](query-loop.md).
26. MCP tools and SDK custom tools run sequentially unless marked with `readOnlyHint`.

### Deferred loading (tool search)

27. When tool search is active, deferred tools are sent with `defer_loading: true` and only their names reach the model, through system reminders in the conversation. `ToolSearch` returns full schemas, as `tool_reference` content the API expands.
28. A tool is deferred when it is an MCP tool or declares `shouldDefer`, unless `alwaysLoad` is set. MCP servers set this with `_meta['anthropic/alwaysLoad']`. `ToolSearch` is never deferred.
29. Mods can set `isDeferred: false` on `$.tool.register` (2.1.293).
30. Query forms: `select:<names>` for exact fetch, keywords for ranked search, `+term` to require a name match.
31. Calling a deferred tool before fetching its schema fails.
32. The tool list MUST stay byte-stable for a conversation when deferral is active: a server connecting late contributes deferred definitions instead of rewriting the list (on third-party providers since 2.1.268). Deny rules don't change definitions while tool search is active.
33. In the snapshot, discovered tools are recovered from `tool_reference` blocks in history, so they stay loaded.

Availability:

34. `ENABLE_TOOL_SEARCH` unset or `true`: MCP tools deferred, with these exceptions that load upfront: models before Opus 4 and Sonnet 4, Agent Platform models before Opus 4.5, Sonnet 4.5 and Haiku 4.5, and Foundry deployments hosted on Azure (detected from the server rejection). `true` does not override those.
35. `auto` and `auto:N`: threshold mode. Tools load upfront under N% of the context window (default 10) and defer at or above it, and may stay deferred afterwards.
36. `false`: everything loads upfront.
37. `CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS` keeps tool search off and overrides the variable; organizations can keep it on through managed settings (the docs say since v2.1.227). HIPAA configurations have their own rule.
38. Behind a custom `ANTHROPIC_BASE_URL`, tool search is on by default since 2.1.304. A 400 or 422 from the gateway retries without it.

### Waiting for MCP servers

39. With tool search on, the wait for a still-connecting server happens inside `ToolSearch`. Otherwise `WaitForMcpServers` is available, and adding it mid-conversation invalidates the cache once.

### Result handling

40. Results larger than a tool's `maxResultSizeChars` MUST be written to a file, and the model receives a preview with the path. Tools that self-limit (such as Read) set this to infinity, because persisting would create a read loop.
41. Snapshot limits: 50,000 characters default per tool, 200,000 characters aggregate per message, enforced before microcompact. Replacements MUST be recorded so resume reproduces the same bytes.
42. Documented limits: Bash output 30,000 characters by default, 150,000 maximum (`BASH_MAX_OUTPUT_LENGTH`, or `bashOutputMaxChars`, which takes precedence); Read 25,000 tokens (`CLAUDE_CODE_FILE_READ_MAX_OUTPUT_TOKENS`), with a truncated first page and a partial-view notice since 2.1.145; `allow_large` can exceed that while context has room; MCP output 25,000 tokens (`MAX_MCP_OUTPUT_TOKENS`), warning above 10,000, and tools may declare `anthropic/maxResultSizeChars`.
43. Whole-file reads over the limit MUST return a partial view rather than a hard error.

## Configuration & interfaces

| Item | Effect |
| - | - |
| `--tools`, `--allowedTools`, `--disallowedTools` | Availability and permission rules |
| `ENABLE_TOOL_SEARCH` | `true`, `false`, `auto`, `auto:N` |
| `CLAUDE_CODE_ENABLE_TODO_TOOLS`, `CLAUDE_CODE_ENABLE_TASKS` | Task-tracking tools |
| `CLAUDE_CODE_DISABLE_WEB_FETCH` | Removes WebFetch |
| `CLAUDE_CODE_DISABLE_ATTACHMENTS` | No attachment processing; `@` mentions stay as text |

## Failure modes & edge cases

- A gateway rejecting tool-search fields can surface as a 500 or a selected-model error. Test with `ENABLE_TOOL_SEARCH=false`.
- `tool_use.name` over 200 characters in history is rejected by the API.
- An invalid MCP `input_schema` fails the whole request and names the tool's position.
- Duplicate or orphaned tool ids surface as history mismatch errors recoverable with `/rewind`.

## Changes since the snapshot

- 2.1.101: clearer tool-not-available errors.
- 2.1.119: tool search disabled on Vertex by default, then 2.1.221 re-enabled it for 4.5-generation and newer models.
- 2.1.145: Read returns partial views.
- 2.1.154: streaming tool execution always on.
- 2.1.161: failed Bash no longer cancels siblings.
- 2.1.233, 2.1.268: task tools limited to older models.
- 2.1.268: stable tool list on third-party providers.
- 2.1.277: `TaskOutput` removed.
- 2.1.293: `isDeferred` for mods.
- 2.1.304: tool search on by default behind gateways.

## Open questions

- Whether the 10-call concurrency cap and the snapshot's per-tool character limits still hold.
- Current deferral rule for built-in tools. The snapshot lists exceptions per tool; the docs only cover MCP.
- Exact current format of deferred-tool announcements beyond "system reminders".
