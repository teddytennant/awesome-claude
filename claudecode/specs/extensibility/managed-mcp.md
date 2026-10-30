# Managed MCP

**Status:** shipped
**Provenance:** both (`managed-mcp.json` and allow and deny lists in snapshot; `managedMcpServers`, `allowAllClaudeAiMcps`, pinned expansion post-leak)
**Sources:** docs `managed-mcp`, `mcp`; snapshot `services/mcp/config.ts`; changelog 2.1.149, 2.1.219, 2.1.259, 2.1.273, 2.1.301.

## Purpose

Lets administrators fix, provide, allow, deny, or disable MCP servers.

## Behaviour

### Patterns

| Pattern | Mechanism |
| :- | :- |
| Disable MCP | `managed-mcp.json` with an empty map |
| Fixed deployment | `managed-mcp.json` |
| Provided servers | `managedMcpServers` |
| Approved catalog | `allowedMcpServers` + `allowManagedMcpServersOnly: true` |
| Plugin servers only | `strictPluginOnlyCustomization` including `mcp` |
| Soft allowlist | `allowedMcpServers` alone; users can broaden |
| Denylist | `deniedMcpServers` |

### `managed-mcp.json`

1. Paths: `/Library/Application Support/ClaudeCode/`, `/etc/claude-code/`, `C:\Program Files\ClaudeCode\`. Same format as `.mcp.json`. It cannot be delivered through server-managed settings.
2. Exclusive control: only its servers, `managedMcpServers`, host-registered in-process servers, and Claude in Chrome if allowed may load. Plugin servers, `--mcp-config` servers and fetched connectors MUST NOT load.
3. `--mcp-config` on a workstation MUST exit with `You cannot dynamically configure MCP servers when an enterprise MCP config is present`. In cloud sessions on such a host, managed servers load, and delivered ones are skipped with a stderr warning only.
4. `--strict-mcp-config` MUST exit at startup on both.
5. `allowAllClaudeAiMcps`, read only from admin-controlled tiers, loads fetched connectors alongside (v2.1.149). A host file in a cloud session suppresses connectors regardless.
6. `allowClaudeInChromeWithManagedMcp`, device-managed sources only, allows Claude in Chrome (v2.1.282). Otherwise `claude --chrome` exits with a named error.
7. `claude mcp add` fails with `enterprise MCP configuration is active and has exclusive control over MCP servers`.
8. Credentials MUST NOT be stored in the file's `env`, as any local user can read it. Use `${VAR}`, OAuth or `headersHelper`.

### `managedMcpServers` (v2.1.259)

9. An object keyed by server name, from any managed source, with the shape of an HTTP or SSE `.mcp.json` entry plus `headers` and `oauth`.
10. An entry MUST be dropped with a `/status` notice unless: `type` is `http`, `sse` or `streamable-http`; `url` is `https://`, never plain `http`, even for localhost; it has no `command`, `args`, `env`, `headersHelper`; no `${VAR}` (not expanded); and the name uses letters, digits, `-`, `_`, with no control or invisible characters anywhere. Other entries still load.
11. Claude Desktop's same-named array form MUST NOT be accepted.
12. Provided servers beat same-named local, project, user servers and same-URL plugin or connector servers. With `managed-mcp.json`, the file wins by name. They continue under `strictPluginOnlyCustomization` `mcp`. They need no allowlist entry; `deniedMcpServers` applies, including a user's own.
13. Without `managed-mcp.json`, `--mcp-config` under the same name replaces for that run, checked against the allowlist, and `--strict-mcp-config` omits provided servers.
14. Users MUST NOT edit or remove them; they can toggle off in `/mcp` under **Managed MCPs**. Display shows host only and header names only.
15. Read from the selected managed source, or all admin sources under `managedSourcesBehavior: "merge"`. Never from HKCU or similar. Not read in Desktop Code tab third-party deployments or Cowork; `/status` says so.
16. Via server-managed settings, cached values are withheld until confirmed, and a failed confirmation continues without them. First launch connects when settings arrive; a `-p` run may finish without them. Running interactive sessions add, reconnect and remove on change; `-p` keeps a removed one until it ends.

### Allow and deny evaluation

17. Before loading any server, and on reconnect or re-enable: merge lists; check the denylist; check the allowlist. `sdk` servers skip all three.
18. Lists merge from every scope. `allowManagedMcpServersOnly` keeps only the managed allowlist, from the highest-ranked admin source that sets one (v2.1.273). The denylist always merges, and nothing overrides a match.
19. Unset allowlist allows all. `[]` allows none, apart from skip groups. Empty denylist blocks nothing.
20. Remote servers need a `serverUrl` match; `serverName` counts only if no `serverUrl` entries exist. Stdio needs `serverCommand`; `serverName` counts only if no `serverCommand` entries exist.
21. Allowlist skip groups: `managedMcpServers`; `managed-mcp.json` entries with no `${VAR}` outside `env` (v2.1.305); built-ins (Chrome, `ide`, CLI-configured); a Claude Tag session's Slack tools.
22. `serverName` is exact and is not a security control. In denylists it accepts any non-empty trimmed string, allowing `claude.ai Slack`. In allowlists it is restricted to letters, digits, `-`, `_`.
23. `serverCommand` compares command and all arguments exactly, in order; `env` is not compared.
24. `serverUrl` supports `*`, including the scheme. Host matching is case-insensitive and ignores a trailing dot; paths are case-sensitive. No port: a written-out host means the default port only, a host with `*` means any port. A pattern with no path matches any path.
25. Expansion applies to `serverCommand` and `serverUrl`, on both sides. Configured values expand from the live environment; policy entries from a pinned environment (v2.1.219).

| List | Expands from | Expansion changing scheme, host or path scope |
| :- | :- | :- |
| `allowedMcpServers` | Startup environment plus managed `env` | Entry ignored |
| `deniedMcpServers` | Same, filling from user or managed settings when unset | Still matches |

26. The lists also filter `--mcp-config` servers; `--strict-mcp-config` does not bypass them.
27. Cloud sessions apply lists to delivered connectors, but rewritten URLs do not match `serverUrl` patterns for the original URL.
28. `allowManagedPermissionRulesOnly` does not enforce the MCP allowlist.
29. A managed allowlist restricting Slack-started self-hosted sessions was fixed so repositories can attach; use `deniedMcpServers` to keep those tools off (v2.1.301).

## Configuration & interfaces

| Surface | Where |
| :- | :- |
| `managed-mcp.json` | System path; MDM, GPO, fleet tools |
| `managedMcpServers`, `allowManagedMcpServersOnly`, `allowAllClaudeAiMcps` | Managed sources only |
| `allowClaudeInChromeWithManagedMcp` | Device-managed sources only |
| `allowedMcpServers`, `deniedMcpServers` | Any scope; enforce through managed |

| Situation | Message |
| :- | :- |
| Denied add | `server is explicitly blocked by enterprise policy` |
| Not allowed add | `not allowed by enterprise policy` |
| Plugin-only add | `your organization's managed settings allow only MCP servers that plugins provide` |
| Removing a provided server | `is provided by your organization (managed settings) and cannot be removed locally.` |
| Newly blocked | Disappears from `/mcp` and `claude mcp list` silently |
| Blocked on reconnect | `MCP server <name> is blocked by enterprise managed policy` |

## Failure modes & edge cases

- Upgrading past v2.1.305 can start `managed-mcp.json` servers that were held back only by an allowlist and used `${VAR}` in `env`. Use `deniedMcpServers`.
- A parse failure shows in `claude mcp list` under `MCP config diagnostics`.
- A user can block a managed server for themselves.
- `disableAllHooks` and MCP policy are unrelated.
- Telemetry: `OTEL_LOG_TOOL_DETAILS=1` includes names.

## Changes since the snapshot

- v2.1.149: `allowAllClaudeAiMcps`.
- v2.1.219: pinned expansion environment.
- v2.1.259: `managedMcpServers`; managed servers mostly skip the allowlist.
- v2.1.273: lock read across sources.
- v2.1.282: Chrome alongside managed set.
- v2.1.301: self-hosted Slack sessions fix.
- v2.1.305: `${VAR}` in `env` no longer triggers the allowlist check.

## Open questions

- Precise semantics of "Keys read from every admin source" are in `managed-settings`, outside this area.
