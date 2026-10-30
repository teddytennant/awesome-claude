# MCP Authentication and Connectors

**Status:** shipped
**Provenance:** both (OAuth, `headersHelper` and connectors in snapshot; CLI login, CIMD, scope pinning, trust rules, gateway headers post-leak)
**Sources:** docs `mcp`, `env-vars`; snapshot `services/mcp/auth.ts`, `headersHelper.ts`, `claudeai.ts`, `xaa.ts`; changelog 2.1.121 to 2.1.299.

## Purpose

Defines how Claude Code authenticates to remote MCP servers, and how claude.ai connectors arrive and are governed.

## Behaviour

### Needs-auth detection

1. A remote server answering 401 or 403 MUST be flagged in `/mcp` when no credential was configured.
2. A `401` or `403` at connect with a configured `Authorization` (in `headers` or `headersHelper`) MUST report connection failure, with no OAuth fallback.
3. A connector 401 caused by claude.ai rejecting the session token MUST show `session token rejected`; the fix is `/login` then reconnect (v2.1.222).
4. Cloud-delivered connectors MUST NOT run a sign-in flow; the session proxy authenticates.
5. A stored OAuth token rejected with 401 MUST refresh, reconnect and retry once before flagging. A rejected refresh token shows a notice pointing to `/mcp`.
6. Startup notice names servers needing sign-in, once per server until reconnected and re-needed (v2.1.193, v2.1.268), excluding servers only fixable on claude.ai (v2.1.218).
7. `-p` and SDK cannot run OAuth; sign in from `/mcp` or `claude mcp login`.
8. An `insufficient_scope` 403 on a tool call fails with `needs additional permissions`, offers re-authentication (v2.1.288), and flags the server. With pinned scopes, Claude Code requests the pinned set, not the named scope.

### OAuth flow

9. Discovery MUST check RFC 9728 protected resource metadata, then RFC 8414 authorization server metadata, unless `oauth.authServerMetadataUrl` (`https://` only) overrides. `WWW-Authenticate` hints are honoured.
10. Client identity: Dynamic Client Registration, Client ID Metadata Document, or pre-configured `--client-id`. Registration MUST NOT occur until the user actually authenticates (v2.1.265).
11. Callback uses `http://localhost:PORT/callback`, random by default; `--callback-port`, `oauth.callbackPort` or `MCP_OAUTH_CALLBACK_PORT` fix it. v2.1.229 sent `127.0.0.1`; v2.1.231 restored `localhost`.
12. The client secret is set only at add time (`--client-secret`, or `MCP_CLIENT_SECRET`), and stored in the keychain or a credentials file. To change it, remove and re-add at the same scope.
13. `oauth.scopes` (space-separated) beats metadata and discovery. If unset, the full `scopes_supported` from automatic discovery MUST NOT be requested; a configured metadata URL's `scopes_supported` is. `offline_access` is appended when advertised.
14. On the v2 runtime, an unexpected issuer MUST fail sign-in, and credentials go only to token endpoints on HTTPS or loopback.
15. Discovery and token requests retry once on transient errors (v2.1.191). Headless environments skip the browser and use the paste prompt.
16. `claude mcp login <name>` runs the flow from the shell (v2.1.186); `--no-browser` forces the URL prompt, which needs an interactive terminal (`ssh -t`). `claude mcp logout` revokes where supported.
17. Configured non-`Authorization` headers MUST be sent on sign-in, refresh and revocation requests to the server's origin (v2.1.299). They are not sent to the browser page or other-origin authorization servers.
18. Some Anthropic-hosted hosts refuse local OAuth with `is Anthropic-hosted and doesn't support local OAuth`, directing to claude.ai.
19. Sensitive URL and header parts MUST be redacted from logs (v2.1.257).

### `headersHelper`

20. Output MUST be a JSON object of strings on stdout within 10 s. Helper headers override static ones.
21. It MUST run fresh on each connection, with no caching. On 401 or 403 during a tool call, it re-runs, reconnects and retries once (v2.1.193).
22. Env: `CLAUDE_CODE_MCP_SERVER_NAME`, `CLAUDE_CODE_MCP_SERVER_URL`, `CLAUDE_PLUGIN_ROOT` for plugin servers. `${user_config.*}` is rejected (v2.1.207).
23. Working directory:

| Configured in | Directory |
| :- | :- |
| Plugin | Plugin root |
| Project `.mcp.json`, local scope | Declaring project directory |
| Project agent file, SDK servers, `--mcp-config` | Primary working directory |
| User scope, managed, connector, external agent file | Config directory (v2.1.238) |

24. Credential-looking variables (names containing `TOKEN`, `SECRET`, `PASSWORD`, `KEY`, `AUTH`, plus a fixed list) MUST be removed for project `.mcp.json`, plugin, and project or `--add-dir` agent-file helpers, except Git's `GIT_CONFIG_KEY_<n>`. A `url` carrying such a value has it replaced by `REDACTED` in `CLAUDE_CODE_MCP_SERVER_URL`.
25. Project and local-scope helpers MUST run only after the trust dialog for the declaring directory. Parent trust and `-p` trust do not count (v2.1.238). Until then the server connects with static headers, and `-p` prints `headersHelper not run` to stderr. `hasTrustDialogAccepted` in `~/.claude.json` grants it. Agent-file inline servers do not load at all until trusted.

### claude.ai connectors

26. Fetched only under a claude.ai subscription login. Not with `ANTHROPIC_API_KEY`, `ANTHROPIC_AUTH_TOKEN`, `apiKeyHelper` (v2.1.139), third-party providers, `ANTHROPIC_PROFILE`, federation, or `claude setup-token` tokens.
27. The list fetch retries three times in the background.
28. Delivery:

| Session | Arrival | Governed by |
| :- | :- | :- |
| Terminal, VS Code, JetBrains, SDK | Fetched | Settings here and managed MCP |
| Cloud | Passed by host | Org settings, delivered lists, host `managed-mcp.json` |
| Desktop local, SSH | In-process `sdk` | `blocked` tool controls only |

29. `disableClaudeAiConnectors`, `ENABLE_CLAUDEAI_MCP_SERVERS` and `allowAllClaudeAiMcps` affect fetched connectors only. `disableClaudeAiConnectors` is any-source-true; `--mcp-config` servers are unaffected.
30. Org tool control `ask` MUST prompt on every call with `Your organization requires approval for this tool`, in all modes, with no remember option; allow rules do not skip; `dontAsk` denies. `blocked` filters the tool before the model; `/mcp` still shows it for fetched connectors.
31. A locally added server with the same URL hides the connector, and `/mcp` shows how to remove the duplicate (v2.1.122). Same-URL connectors dedupe (v2.1.121). Never-used connectors collapse behind `Show unused connectors` (v2.1.161). `managed` marks org-managed auth (v2.1.243).
32. Requests to the connector proxy and Anthropic-hosted servers MUST NOT follow redirects (v2.1.299).

## Configuration & interfaces

| Field or flag | Notes |
| :- | :- |
| `oauth.clientId`, `oauth.callbackPort`, `oauth.authServerMetadataUrl`, `oauth.scopes` | Per server; HTTP and SSE only |
| `--client-id`, `--client-secret`, `--callback-port` | `claude mcp add` |
| `headers`, `headersHelper` | Per server |
| `/mcp` | **Re-authenticate**, **Clear authentication**, **Reconnect**, **Disable** |

## Failure modes & edge cases

- `Incompatible auth server: does not support dynamic client registration`.
- `Refusing to send credentials to non-https token endpoint`.
- On macOS in `-p`, an unreadable stored token gives a stored-credentials error.
- `${ANTHROPIC_AUTH_TOKEN}` in a header yields `Bearer ` and a 401.
- A helper failure at connect is reported as failed; retries apply only where its `Authorization` is the sole source.

## Changes since the snapshot

- v2.1.121: `mcp_authenticate` supports `redirectUri` in the SDK.
- v2.1.186: `claude mcp login`, `logout`.
- v2.1.193: helper re-run on 401.
- v2.1.238: helper trust and environment rules.
- v2.1.265: deferred client registration.
- v2.1.288: re-auth on scope demand.
- v2.1.299: gateway headers on OAuth; no redirects via proxies.

## Open questions

- Snapshot `xaa.ts` (cross-app access) has no public doc entry reviewed; current status unknown.
- The fixed list of non-pattern credential variables is only partly named.
