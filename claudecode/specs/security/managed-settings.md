# Managed, Server-Managed and Remote Settings as Policy

**Status:** shipped
**Provenance:** both; source composition, helpers, fail-closed parsing post-leak
**Sources:** docs `managed-settings`, `server-managed-settings`, `settings`, `settings-reference`, `admin-setup`, `errors`, `claude-apps-gateway` (referenced); snapshot `services/remoteManagedSettings/`, `services/policyLimits/`; changelog 2.1.92–2.1.314

Excluded: non-public endpoints. Server-managed delivery is a client-side control; how it can be defeated is out of scope.

## Purpose

Let an organization deliver settings that outrank everything a developer or repository sets, from a central place, and make policy failures visible and safe.

## Behaviour

### Tier

1. Managed values MUST outrank user, project, local and `--settings`. Exceptions MUST honour a stricter lower-level value, for: `disableClaudeAiConnectors`, `enableArtifact`, `isolatePeerMachines`, `blockReadsOutsideWorkingDirectories`, `autoMode.classifyAllShell`, `remoteControlAtStartup`, `crossSessionInbound`, `useAutoModeDuringPlan`, `syncClaudeAiSkills`, `syncClaudeAiPlugins`, `maxEffortLevel`.
2. Array settings merge across tiers, so developers can extend but not remove; restriction allowlists such as `availableModels` replace.
3. A managed `model` or `autoCompactWindow` is a default; `availableModels` restricts choice.
4. `/config` settings participate in the same precedence (2.1.119).

### Sources and ranking

5. Sources, highest first:

| Rank | Source | Location | Refresh |
|---|---|---|---|
| 1 | Remote settings | claude.ai console or Claude apps gateway | Startup, hourly |
| 2 | MDM or OS policy | macOS `com.anthropic.claudecode`; `HKLM\SOFTWARE\Policies\ClaudeCode` value `Settings` | Startup, 30 minutes |
| 3 | File | `managed-settings.json` and `managed-settings.d/*.json` in `/Library/Application Support/ClaudeCode/`, `/etc/claude-code/`, `C:\Program Files\ClaudeCode\` | Startup, on change |
| 4 | HKCU | `HKCU\SOFTWARE\Policies\ClaudeCode` | Startup, 30 minutes |

6. Admin sources are ranks 1–3. HKCU is user-writable and MUST be used only with no admin document present and no restrictive parent settings. A document is present if it sets a non-null policy key or exists unreadably.
7. WSL reads `/etc/claude-code` only, unless `wslInheritsWindowsSettings` from HKLM or the Windows file turns on the Windows chain. Present but invalid Windows admin policy MUST keep user-writable sources from applying.
8. Drop-ins MUST merge after `managed-settings.json` in filename order, ignoring hidden and non-`.json` files. Scalars replace; lists union; blocks merge by key; `fallbackModel`, `modelPicker`, `extraKnownMarketplaces` and `managedMcpServers` entries replace whole.
9. A file deployed as a link is honoured; a link leaving the system directory MUST warn in `/status` and `claude doctor`.

### Composition

10. `managedSourcesBehavior`:
    - `"first-wins"` (default): use the highest source delivering at least one policy key; ignore others except cross-source keys.
    - `"merge"`: combine admin sources by kind of key.
11. Control keys (`wslInheritsWindowsSettings`, `managedSourcesBehavior`) do not count as policy keys.
12. Cross-source keys read from every admin source include: `allowManagedDomainsOnly`, `allowManagedReadPathsOnly`, `allowManagedMcpServersOnly`, `allowAllClaudeAiMcps`, `deniedMcpServers`, `disableClaudeAiConnectors`, `bwrapPath`, `socatPath`, `ripgrep`, `filesystem.disabled`, `strictAllowlist`, `useAutoModeDuringPlan`, `syncClaudeAiSkills`, `syncClaudeAiPlugins`, `enableArtifact`, `maxEffortLevel`, attribution opt-outs, `forceRemoteSettingsRefresh`, and `env` merged per variable.
13. Under a lock, the locked allowlist is unioned across admin sources for sandbox, or taken from the highest setter for MCP.
14. `env` exceptions: telemetry exporter variables travel as a unit from the highest source so an endpoint never pairs with another source's credentials; routing variables paired with a credential key contribute only when that source wins.
15. Under `"merge"`: lists union; locks take the strictest; restriction allowlists come whole from the highest setter; `awsPairs` and `ripgrep` are whole values; `permissions.defaultMode`, `modelPicker` and credential helpers come from the highest source only. Login keys come from the MDM or file source under either setting, and merge never includes HKCU.
16. Login keys: MDM or file values win over remote settings for `forceLoginOrgUUID` and `forceLoginMethod` `claudeai`/`console` (with remote filling omitted keys); gateway login keys never come from remote settings.

### Policy helper

17. `policyHelper` (`path`, `timeoutMs`, `refreshIntervalMs`) from the plist, HKLM or file runs an executable at startup. Its `managedSettings` MUST become the only managed settings for the session, apart from `forceRemoteSettingsRefresh`.
18. It MUST NOT run while server-managed settings deliver a policy key; if a later fetch reports them removed, it runs immediately and a failure ends the session.
19. Startup failure (bad path, no file, non-zero exit, timeout, over 1 MiB output, invalid or unrepairable JSON) MUST refuse to start across all session kinds. Refresh failure MUST keep the last good policy and show in `/status`.

### Embedding hosts

20. Hosts pass `managedSettings` via SDK as parent settings. These MUST be ignored when an admin source is present unless `parentSettingsBehavior: "merge"`. Merged values keep only restrictions, except permission allow rules and sandbox allowlists unless `allowManaged*Only` locks are set. Parent allow rules are dropped under `allowManagedPermissionRulesOnly`, and parent `!` carve-outs are dropped always. Parent `forceLoginOrgUUID`, `allowedMcpServers`, `availableModels`, `strictKnownMarketplaces`, `allowedProviders` yield to admin values; parent `blockedMarketplaces` add.

### Surfaces

21. Terminal, IDE, Desktop Code tab and SDK sessions read all sources, including SDK sessions excluding other settings. Anthropic-hosted cloud sessions read only server-managed. Self-hosted cloud sessions also read the runner image's file. Claude Tag does not receive server-managed settings. Cowork never fetches server-managed settings.
22. Most changes reach running sessions on the refresh schedule. `forceRemoteSettingsRefresh`, `requiredMinimumVersion` and some keys take effect at next start. `requiredMinimumVersion` does not end running sessions.

### Server-managed delivery

23. Requires Team or Enterprise and Owner or Primary Owner role. The editor validates against the published schema, warning without blocking.
24. Delivery requires a direct `api.anthropic.com` connection and a Team or Enterprise OAuth login, `CLAUDE_CODE_OAUTH_TOKEN`, direct API key, or `user_oauth` profile. `apiKeyHelper` keys and federation credentials MUST NOT trigger the fetch. Sessions on other providers or base URLs skip it; a gateway provides the equivalent.
25. A session receives its own credential's organization's settings; Console keys belong to a separate organization.
26. First launch: at sign-in, wait up to five seconds so policy applies from the first screen, ending the wait when approval is needed. Otherwise open while the fetch continues, warning if it fails.
27. Subsequent launches: cached settings apply immediately from `~/.claude/remote-settings.json`, except values withheld until the server confirms: `modelPricing`, `managedMcpServers` (waits up to 30 seconds), changes that remove or reposition the built-in guard, and `env` categories for proxy and TLS, routing and provider selection, credentials, `CLAUDE_CONFIG_DIR`, credential-source and OS directory selectors. Withholding stops a cached value from redirecting the confirming fetch itself.
28. Federation and profile selectors MUST NOT switch credentials after startup even when delivered.
29. Fetch failure with cache: continue, warn. Without cache: continue, warn, apply endpoint settings. Requests send `Cache-Control: no-cache`.
30. `forceRemoteSettingsRefresh: true` MUST block startup until a fresh fetch and exit on failure; it self-perpetuates through the cache and is honoured from any admin source. `claude auth` subcommands are exempt. Gateway clients always wait and exit on failure, except a `401` on an attended launch, which opens signed out of the gateway.

### Security approval

31. Interactive sessions MUST show a blocking dialog for: shell-command settings (`apiKeyHelper`, `statusLine`, `otelHeadersHelper`); sandbox binary settings; sandbox network and isolation settings (non-deny-only credentials, TLS termination, proxy ports, weakening options, unix sockets, mach lookup, filesystem disable); certain `env` variables; hooks. `processWrapper` is also listed.
32. Rejecting MUST exit, printing why. A declined dialog is not remembered.
33. Non-sensitive toggles MUST NOT prompt: feature and command toggles, model and behaviour settings, context settings, UI, numeric limits. Privacy toggles set truthy, `API_FORCE_IDLE_TIMEOUT` truthy, tracing falsy, and tag-only headers skip approval. Proxy or base-URL variables, `OTEL_EXPORTER_OTLP_ENDPOINT`, `CLAUDE_CODE_DISABLE_1M_CONTEXT` always need it. `ANTHROPIC_CUSTOM_HEADERS` lines naming credentials, tenants, routing or API behaviour need it.
34. `claudeMd` needs no approval (2.1.260).
35. The dialog lists only changes since last approval, shows endpoint URLs and clearer telemetry wording.
36. Approval memory: per organization for saved claude.ai logins and keyless Console, held by the latest approving account; per gateway for gateway sign-in (invalidated by changed settings, gateway or certificate); with the cached copy for other credentials. Approval of credentials or TLS covers `allowedDomains` in the same payload.
37. Cannot-show cases: an interactive session unable to show keeps last-approved; `claude install` or `update` run with last-approved unless startup waits; non-interactive runs apply for that run only, not cached or recorded.

### Validation

38. Managed values MUST be salvaged per entry with a warning. Interactive startup shows a dialog, `-p` prints to stderr, `claude doctor` lists each.
39. A managed file, drop-in, plist or HKLM value that exists but is not a JSON object MUST refuse to start, naming the source, even when another source is valid. HKCU never blocks launch.
40. Unreadable documents: OS-denied reads start without that source and record it; other failures exit with a message to contact an administrator.
41. Keys with one restrictive value MUST read as that value when invalid. Quoted Booleans read as Booleans with a notice. `null` removes a key. `disableAllHooks` is dropped.
42. Restriction lists fall back to empty (`allowedMcpServers`, `allowedProviders`, `allowedHttpHookUrls`, `httpHookAllowedEnvVars`, `allowedChannelPlugins`, `strictKnownMarketplaces`, `availableModels`). `crossSessionInbound` reads `refuse`. Deny lists wholly invalid are dropped with a warning since denying everything would block the unnamed.
43. When a `deny` or `ask` list is unreadable, `allow` and `additionalDirectories` MUST be withheld. An unreadable `soft_deny` or `hard_deny` withholds `allow` and `environment`. Unreadable `deniedDomains` withholds `allowedDomains`. Unreadable `denyRead` or `denyWrite` withholds `allowRead` and `allowWrite`.
44. In `sandbox`: invalid Booleans read strictest, except `failIfUnavailable`, which is dropped so policy typos cannot stop sessions across a fleet. Invalid `sandbox.credentials` entries degrade to `deny` where possible.
45. `requiredMinimumVersion` and `requiredMaximumVersion` fail open.
46. A payload where every setting fails and none falls back to stricter MUST apply nothing and leave the cache unchanged; fail-closed clients exit.

### Managed-only keys

47. Read only from managed sources: `allowAllClaudeAiMcps`, `allowedChannelPlugins`, `allowManagedHooksOnly`, `allowManagedMcpServersOnly`, `allowManagedPermissionRulesOnly`, `blockedMarketplaces`, `channelsEnabled`, `disableCommandPluginSources`, `disableSideloadFlags`, `forceRemoteSettingsRefresh`, `managedMcpServers`, `managedSourcesBehavior`, `parentSettingsBehavior`, `pluginSuggestionMarketplaces`, `pluginTrustMessage`, `policyHelper`, `allowManagedReadPathsOnly`, `allowManagedDomainsOnly`, `strictKnownMarketplaces`, `strictPluginOnlyCustomization`, `wslInheritsWindowsSettings`, plus others flagged in `settings-reference`.

### Organization policy limits

48. Separately from settings, the client MUST fetch an organization policy record (features allowed or restricted, HIPAA status) at startup and about hourly while in use. `claude doctor` and `/status` report it on an `Organization policy` line. The snapshot's service used ETag caching, background polling and failed open generally; current docs show cloud-session paths refusing when the policy cannot be verified.
49. Owners enable or disable Remote Control and cloud sessions org-wide. On Enterprise, custom roles control access to each (2.1.310). Turning Remote Control off disconnects sessions about hourly (from 2.1.286). `disableRemoteControl` disables per device.

## Configuration & interfaces

| Verification | Shows |
|---|---|
| `/status` `Setting sources` | `Enterprise managed settings` plus a source label: `remote`, `plist`, `HKLM`, `file`, `drop-ins`, `HKCU`, `parent process`, `helper`; lists ending `, merged` |
| `/status` `Skipped sources` | Present but unselected sources (2.1.243) |
| `claude doctor` `Managed settings (remote)` | Loaded, none, failed with cache state, skipped with reason (2.1.248) |
| `claude doctor` `Organization policy` | Source or failure (2.1.261) |
| OTel `claude_code.managed_settings_resolved` | Sources and helper state; redacted settings with `OTEL_LOG_MANAGED_SETTINGS=1` (2.1.274) |
| `ConfigChange` hook | Local file edits; not run for server or MDM changes; cannot block `policy_settings` |
| Audit | Compliance API or export: action, account, device, value references |

## Failure modes & edge cases

- Clearing server settings leaves cached values until the next fetch and next-launch keys until relaunch.
- Provider or base-URL exports skip the fetch; `/status` and `claude doctor` report it. Endpoint-managed delivery is the documented route where this matters.
- Server-managed settings apply uniformly; per-group policy needs separate files or a gateway. `managed-mcp.json` cannot be delivered this way.
- Server-managed settings are a client-side control. Endpoint delivery under MDM gives stronger guarantees.

## Changes since the snapshot

- 2.1.92: `forceRemoteSettingsRefresh`. 2.1.118: `wslInheritsWindowsSettings`. 2.1.163: required version range. 2.1.169: partial application of invalid payloads.
- 2.1.218: benign toggles skip approval. 2.1.232: dialog URLs and telemetry wording. 2.1.243: `Skipped sources`. 2.1.247: exit when required policy unreadable. 2.1.251: changed-only dialog.
- 2.1.257: helper diagnostics; helper runs when server settings vanish. 2.1.260: `claudeMd` no approval. 2.1.274: resolved event. 2.1.281: no retry of hopeless fetches.
- 2.1.282: present-invalid policy blocks HKCU; fail-closed key handling. 2.1.283: per-field sandbox handling. 2.1.290: link warning. 2.1.293: earlier fetch, 3-second stalled retry. 2.1.314: file tools ask before editing the local copy.

## Open questions

- Full `Organization policy` key list is unpublished; snapshot uses `allow_product_feedback`, `allow_remote_control`, `allow_remote_sessions`, which may be outdated.
- Docs give a minimum version for `managedSourcesBehavior` that has no matching changelog heading, so it is not cited here.
- `processWrapper` appears in the corporate launcher doc as dialog-listed but not in the server-managed dialog list.
