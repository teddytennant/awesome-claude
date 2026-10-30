# Authentication and Credentials

**Status:** shipped
**Provenance:** both (profiles, federation, keyless Console, gateway post-leak)
**Sources:** docs `authentication`, `settings-reference`, `legal-and-compliance`, `env-vars`, `errors`, `claude-apps-gateway` (referenced); snapshot `services/oauth/`, `utils/auth.ts`, `constants/oauth.ts`; changelog 2.1.92–2.1.300

Excluded: non-public endpoints, client identifiers, tokens, client attestation and rate-limit enforcement. Provider-specific setup belongs to the provider specs.

## Purpose

Decide which credential a session uses, obtain and store it safely, keep it fresh, and let organizations constrain sign-in.

## Behaviour

### Sign-in

1. First launch MUST open a browser login, unless an approved `ANTHROPIC_API_KEY` or an earlier sign-in applies. The OAuth flow MUST use authorization code with PKCE.
2. Two code paths MUST work: automatic redirect to a local listener, and pasting a code when the browser cannot reach localhost (WSL2, SSH, containers). `c` copies the URL and reports how.
3. Account types: Claude Pro, Max, Team, Enterprise via claude.ai; Claude Console; cloud providers via environment or setup wizard (**3rd-party platform** for Bedrock and Agent Platform); Claude apps gateway via corporate SSO.
4. `/logout` MUST sign out and reset first-launch state. `/login` MUST switch credentials for the session.
5. `claude auth login` and `claude auth logout` provide shell equivalents and MUST be exempt from fail-closed policy startup checks, so users can re-authenticate.
6. Console sign-in offers two routes (2.1.243): keyless, storing an OAuth login as an Anthropic profile, and creating an API key (legacy). Keyless sign-in writes the profile named by `ANTHROPIC_PROFILE`, else active, else `default`. It MUST refuse to overwrite a federation profile and MUST sign out any stored claude.ai login. `/logout` removes and revokes it.
7. The keyless choice MUST NOT be offered when: on a cloud provider; any settings file sets `forceLoginOrgUUID` or `forceLoginMethod: "claudeai"`; `forceLoginMethod: "console"` alone until a retry after failure; or a managed source exists but cannot be read and no other supplies policy.
8. `CLAUDE_CONFIG_DIR` gives each account its own settings, history and login. It does not separate keyless Console sign-ins.

### Precedence

9. When several credentials exist the client MUST choose in this order:
   1. Cloud provider, when `CLAUDE_CODE_USE_BEDROCK`, `_VERTEX` or `_FOUNDRY` is set
   2. `ANTHROPIC_AUTH_TOKEN` (Bearer)
   3. `ANTHROPIC_API_KEY` (`X-Api-Key`); interactive sessions prompt once to approve, and `/config` changes the answer; `-p` always uses it
   4. `apiKeyHelper` output
   5. `CLAUDE_CODE_OAUTH_TOKEN`
   6. Anthropic profile and federation credentials
   7. `/login` subscription OAuth
10. A signed-in Claude apps gateway session sits outside the list and outranks everything including provider variables.
11. When managed settings set `forceLoginMethod: "gateway"` or `forceLoginGatewayUrl` and no provider is selected, only the gateway sign-in MUST be used; leftover credentials are skipped and the user is sent to `/login`.
12. Profile sources, first set wins: `ANTHROPIC_PROFILE` (above `/login`); `ANTHROPIC_FEDERATION_RULE_ID` plus `ANTHROPIC_ORGANIZATION_ID` (above); active profile from `active_config` or `default` (above when `oidc_federation`; below a working `/login` when `user_oauth`).
13. Bare mode, Desktop and cloud sessions MUST NOT read profiles or federation variables. Bare mode does not read `CLAUDE_CODE_OAUTH_TOKEN`.
14. Cloud sessions MUST use subscription credentials; environment overrides do not apply.
15. Claude.ai-only features (connectors, `/schedule`, Remote Control, notification preferences) are unavailable when a profile or `ANTHROPIC_API_KEY`, `apiKeyHelper` or `ANTHROPIC_AUTH_TOKEN` is the selected credential.
16. `/status` MUST show the active method, `Profile` row where applicable, and mark an unused credential.

### Storage

17. macOS MUST use the encrypted Keychain, falling back to `~/.claude/.credentials.json` (mode `0600`) when a write is rejected. A Console login that creates a key MUST fail until the Keychain is writable.
18. Linux MUST use `~/.claude/.credentials.json` with mode `0600`. Windows uses `%USERPROFILE%\.claude\.credentials.json`, inheriting user-profile ACLs.
19. With `CLAUDE_CONFIG_DIR`, the file moves under it and the Keychain entry is keyed to it.
20. Credential stores MUST be write-protected from sandboxed commands, and shell writes to them MUST prompt even under a whole-tool `Bash` allow.
21. Secrets in telemetry, logs and uploads MUST be redacted where the pattern is known, including GitLab token families (2.1.232). Known patterns in MCP logs are redacted (2.1.257).

### Refresh and expiry

22. OAuth tokens MUST refresh automatically. Concurrent processes MUST coordinate refresh; the loser reports a specific error.
23. Within three days of expiry, a `/login`-created login MUST warn at startup without blocking. After expiry each request fails with `Login expired · Please run /login`.
24. `/status` MUST show `Login` as `Expired — log in again` plus saved org and email when the claude.ai login is active (2.1.210).
25. Expired `user_oauth` profiles MUST fail with a dedicated error, pointing to `/login` where a claude.ai login would take precedence (2.1.234).

### Helpers

26. `apiKeyHelper` runs a script returning a key. If it takes over 10 seconds, a notice shows elapsed time. Errors, timeouts or empty output MUST fail requests within three attempts.
27. Repository-supplied helpers are trust-sensitive: the snapshot defers them until trust in interactive sessions, while current docs list them as used with only a parent trusted and in `-p` ([trust-dialogs.md](trust-dialogs.md)). Bare mode reads `apiKeyHelper` only from `--settings`.
28. `apiKeyHelper` and the two environment keys apply to the CLI and its wrappers (VS Code, SDK, GitHub Actions), not Desktop or cloud sessions.
29. Bedrock and Vertex helpers (`awsAuthRefresh`, `awsCredentialExport`, `gcpAuthRefresh`) run as configured; `awsCredentialExport` output is cached until its `Expiration` (2.1.176).

### Long-lived tokens

30. `claude setup-token` MUST run the browser flow and print a one-year OAuth token without saving it. It requires Pro, Max, Team or Enterprise.
31. Such tokens can only make model requests, so they MUST NOT establish Remote Control or fetch connectors.
32. `CLAUDE_CODE_OAUTH_REFRESH_TOKEN` with `CLAUDE_CODE_OAUTH_SCOPES` lets `claude auth login` provision without a browser.
33. A `/login` while `CLAUDE_CODE_OAUTH_TOKEN` is set switches the session but the variable applies again next session; the warning is repeated after login (2.1.229).

### Organization restrictions

34. `forceLoginMethod` (`claudeai`, `console`, `gateway`) applies on every listed login path since 2.1.212. On the terminal's interactive screen it pre-selects without enforcing.
35. `forceLoginOrgUUID` (single UUID or array): only a managed source enforces it. For claude.ai, any other org MUST error at login and exit at startup if the credential in use is outside the list. A single UUID in any file pre-selects.
36. Enforcement coverage: terminal, VS Code and SDK claude.ai logins are verified. `setup-token` and `/install-github-app` enforce method only. Console logins are pre-selected, not verified. Gateway sign-in is governed by the identity provider.
37. With either key set, sessions using `ANTHROPIC_API_KEY`, `ANTHROPIC_AUTH_TOKEN` or `apiKeyHelper` MUST be blocked at startup, even when managed settings supply them, and the refusal MUST name the credential, its source and how to remove it. Under a gateway requirement, a saved Console key is blocked too.
38. Cloud provider and profile sessions are blocked only while one of those credentials is also present. The keys do not check a profile's organization.
39. `allowedProviders` (2.1.285) lists `anthropic`, `bedrock`, `vertex`, `foundry`, `anthropicAws`, and values including `customEndpoint`. An unlisted provider MUST be refused at startup, login and next API contact. A machine-source list and a server-managed list intersect; server-managed can narrow but not widen. Invalid value means empty allowlist, refusing every provider.
40. Login keys MUST come from the MDM policy or file ahead of remote settings ([managed-settings.md](managed-settings.md)). They cannot redirect a first login via server-managed delivery.
41. Organization sign-in enforcement MUST exit at start when administrator settings cannot be read, even if host-supplied or per-user sources exist.

### Acceptable use

42. OAuth is for subscribers and native applications. Third-party developers MUST NOT offer claude.ai login or route requests through consumer plan credentials on behalf of users, or collect or intermediate session tokens. See [enterprise-deployment.md](enterprise-deployment.md). Enforcement mechanics are excluded.

## Configuration & interfaces

| Interface | Purpose |
|---|---|
| `/login`, `/logout`, `claude auth login`, `claude auth logout`, `claude setup-token` | Sign-in management |
| `ANTHROPIC_API_KEY`, `ANTHROPIC_AUTH_TOKEN`, `CLAUDE_CODE_OAUTH_TOKEN` | Environment credentials |
| `ANTHROPIC_PROFILE`, `ANTHROPIC_FEDERATION_RULE_ID`, `ANTHROPIC_ORGANIZATION_ID`, `ANTHROPIC_WORKSPACE_ID`, `ANTHROPIC_IDENTITY_TOKEN_FILE` | Profiles and federation |
| `CLAUDE_CODE_OAUTH_REFRESH_TOKEN`, `CLAUDE_CODE_OAUTH_SCOPES` | Provisioning |
| `CLAUDE_CONFIG_DIR` | Configuration root |
| `apiKeyHelper`, `awsAuthRefresh`, `awsCredentialExport`, `gcpAuthRefresh`, `otelHeadersHelper` | Helpers |
| `forceLoginMethod`, `forceLoginOrgUUID`, `forceLoginGatewayUrl`, `gatewayInternalNetworks`, `allowedProviders` | Policy |
| `ANTHROPIC_BASE_URL` | Custom endpoint |
| `/status` rows | `Login method`, `Login`, `Profile`, `Organization`, `Email`, `Allowed providers` |
| Scopes (public) | `user:profile`, `user:inference`, `user:sessions:claude_code` (env-vars doc) |

## Failure modes & edge cases

- A disabled or expired org's `ANTHROPIC_API_KEY`, once approved, causes failures despite a valid subscription. `/status` shows which is active.
- A profile and an API key on one machine under `forceLoginOrgUUID`: session refused until logout.
- `forceLoginOrgUUID` invalid: no organization may log in until fixed.
- Keychain unavailable over SSH: file fallback; recovery steps move the login back.
- Login prompt after earlier sign-in: expired token, org restriction, or method mismatch.
- `gatewayInternalNetworks` invalid at the highest managed source: new gateway sign-ins refused.

## Changes since the snapshot

- 2.1.92, 2.1.98: Bedrock and Vertex setup wizards. 2.1.126: pasted OAuth code for `claude auth login`. 2.1.139: claude.ai features off with env credentials.
- 2.1.141: `ANTHROPIC_WORKSPACE_ID`. 2.1.186: Claude Platform on AWS refresh option. 2.1.210: `Login` expired row. 2.1.212: `forceLoginMethod` on all paths.
- 2.1.229: override warning. 2.1.232: GitLab redaction. 2.1.234: profile expiry. 2.1.243: keyless Console. 2.1.247: exit on unreadable admin policy.
- 2.1.261, 2.1.265: gateway-only machines ignore leftovers. 2.1.268: `gatewayInternalNetworks`. 2.1.275: confirm account on gateway sign-in. 2.1.284: refusal names the credential.
- 2.1.285: `allowedProviders`. 2.1.290: login prompt skipped when signed in. 2.1.295: gateway login keys in user settings on unmanaged machines. 2.1.299: login-key source ordering (per docs). 2.1.300: Desktop gateway managed settings.

## Open questions

- Current OAuth scope list beyond those the public env-var doc shows; the snapshot had more, not verified as current.
- Token lifetimes other than the one-year `setup-token`.
- Refresh coordination mechanism between processes is unspecified.
