# Claude Apps Gateway
**Status:** shipped
**Provenance:** post-leak (since v2.1.195 per docs)
**Sources:** docs `claude-apps-gateway.md`, `-config.md`, `-deploy.md`, `-on-aws.md`, `-on-gcp.md`, `-spend-limits.md`, `gateways.md`; changelog 2.1.198 to 2.1.314

## Purpose
Anthropic's self-hosted gateway, built into the `claude` binary, sits between Claude Code or Claude Desktop and a model provider. Developers sign in by corporate SSO instead of holding keys. The gateway holds upstream credentials, enforces models and managed settings per IdP group, and relays telemetry to the customer's stack.

## Behaviour

### Server
1. `claude gateway --config gateway.yaml` MUST run the server, on the native Linux binary only (macOS for development, Windows unsupported). Server and clients need 2.1.195+.
2. Requires an OIDC IdP (SAML and LDAP unsupported), PostgreSQL 11+, an upstream, and HTTPS.
3. Unknown config keys MUST fail boot. Invalid `match.groups`, `admin_groups` or `email_domain` values fail boot (2.1.232).
4. The gateway MUST send nothing to Anthropic unless the Anthropic API is a configured upstream. It stores no prompt or completion content.
5. Replicas are stateless and self-migrate the schema at boot, serialised across replicas.
6. `/healthz` is liveness; `/readyz` checks the store. `/protocol` serves the endpoint reference, listing usage-limit headers since 2.1.227, and says not to reject unknown input (2.1.286).

### Sign-in
7. Developers connect through `/login` on the **Cloud gateway** screen, using a device flow, so remote boxes can approve in a laptop browser. A Deny button ends a pending sign-in (2.1.290).
8. `forceLoginMethod: gateway` plus `forceLoginGatewayUrl` in managed settings opens that screen. Alone, `forceLoginMethod` leaves an admin-contact message. In user settings it works without managed sources, since 2.1.295, and project files can't set it.
9. These keys belong in device-delivered files, not `managed.policies[].cli`. They must not be in the gateway's `managed` block, or sessions may exit.
10. Address check: the hostname MUST resolve only to private ranges (RFC 1918, link-local, CGNAT, ULA, loopback), unless a declared public block applies. Anthropic-operated public endpoints are accepted (2.1.206). A first-connect TLS fingerprint prompt appears.
11. Gateway sign-in replaces other credentials: the gateway token is the only one, and saved logins are ignored. A configured API key or token conflicts per docs.
12. The signed-in account is confirmed before saving, and `/status` shows it (2.1.275).
13. `/logout` deletes the local credential. A `revocation_endpoint` on the same origin is called best-effort; the built-in server advertises none.
14. No service-token flow exists, so CI should use providers directly. After sign-in, `-p` and SDK runs on that machine use the gateway session.

### Sessions
15. Tokens are HS256 JWTs, `session.ttl_hours` default 1, refreshed silently when the IdP provides refresh tokens. `jwt_secret` accepts an array for rotation.
16. A disabled user expires within `ttl_hours` on refresh failure.
17. Startup with the gateway unreachable MUST exit after about 10 seconds rather than start without settings.
18. A 403 on the managed settings load says Claude Code may not be enabled for the org (2.1.261).

### Upstreams
19. `upstreams` is ordered, and the first resolving the model takes a request.
20. MUST fail over on `5xx`, `429`, `401`, `403`, `404` (2.1.198) or timeout; other `4xx` don't.
21. Providers: Anthropic, Bedrock (`bedrock-runtime`), `mantle` (2.1.283), Claude Platform on AWS (`anthropicAws`, 2.1.198), Agent Platform, Foundry. Same-provider upstreams need distinct `name:`.
22. Beta values are forwarded to each upstream; Bedrock gets them as `anthropic_beta` in the body.
23. Models translate per upstream. `auto_include_builtin_models` and `models` control the catalog.
24. Bedrock: `assume_role` via STS (2.1.281), `guardrail_trace` logs the filter fired without matched text (2.1.314), and CountTokens for aborted requests (2.1.260).
25. `forward_user_identity: true` on Anthropic upstreams sends identity headers (2.1.233), and a `429` then doesn't fail over (2.1.267).
26. SSE keep-alive pings prevent idle disconnects (2.1.229). `timeouts.upstream_ttfb_ms` bounds first byte for cloud upstreams (2.1.295).
27. Errors from upstreams carry upstream messages (2.1.233). Bedrock model rejects name the model (2.1.287).
28. `CLAUDE_GATEWAY_PROXY_IS_EGRESS_BOUNDARY=1` hands all outbound requests to a forward proxy (2.1.277).

### Policy
29. `managed.policies[]` are evaluated in order, first match wins, then merge onto the `match: {}` catch-all. Matchers: `groups` (case-sensitive any), `email_domain`, both.
30. Merge: `availableModels` and `permissions.allow` replace; deny lists and hook arrays union; `env`, `modelOverrides`, `skillOverrides` shallow-merge.
31. A user with no match gets all models and no settings.
32. `availableModels` MUST be enforced server-side with `400`; empty denies all. Missing or non-string `model` is rejected (2.1.221, 2.1.228).
33. Policy keys: `cli`, `code` (same as `cli`, also applied in Desktop's Code tab), `desktop` (Desktop-only).
34. Clients apply policy at the managed tier, at startup and on an hourly poll. Some changes need next launch. Group changes apply at the next token refresh.
35. Gateway sessions don't fetch claude.ai server-managed settings.
36. `parentSettingsBehavior: "merge"` opens parent settings to any launching host, so `allowManaged*Only` locks matter. Parent `sandbox.credentials` entries are stripped to restrictive forms.

### Desktop
37. `bootstrapUrl` is `<public_url>/user/bootstrap`, and policies opt in with `desktop` (2.1.203+). Cowork and Code tabs show by default; `chatTabEnabled: true` adds Chat (2.1.227). Unknown Desktop keys warn and are served (2.1.281 for new keys), but keys Desktop can't use from a gateway stop start.

### Telemetry
38. Clients send OTLP/HTTP to the gateway, instead of a local `OTEL_EXPORTER_OTLP_ENDPOINT`, unless a policy names a collector.
39. The gateway relays verbatim to `forward_to` destinations. Unconfigured signals are discarded.
40. Exports carry `user.id`, `user.email`, `user.groups`. Desktop and Cowork add `enduser.id`, `enduser.sub` (2.1.265).
41. Analytics stays off from startup when managed settings force gateway login (2.1.247).

### Spend limits
42. An `admin:` block enables `/v1/organizations/spend_limits`. Scopes: `user`, `rbac_group`, `organization`. `amount` is USD cents as a string, `null` unlimited, `"0"` blocks. Periods: `daily`, `weekly`, `monthly`, independent.
43. Group and org caps are per-seat defaults, not pools. Effective cap: user override, then the most restrictive group, then org.
44. Over-cap requests get `429`, `error.type: billing_error`, `x-should-retry: false`, with the period, reset and `admin.blocked_message`. UTC boundaries. `count_tokens` is never blocked.
45. `pricing` meters at contracted rates, also delivered to clients (2.1.268), with `multiplier` up to 10 (2.1.271).
46. `/usage` and status line show the spend bar and dollars (2.1.251, 2.1.284).
47. `enforcement.fail_closed_on_error` defaults false: enforcement fails open on store outage.

### Outages
48. With Postgres down, existing sessions work, and new sign-ins fail. Readiness fails unless `store.readiness_grace_seconds` is set (2.1.282).
49. With the IdP down, existing sessions last to `ttl_hours`.
50. `SIGTERM` drains in-flight streams, per `CLAUDE_GATEWAY_DRAIN_TIMEOUT_MS`. Stop timeouts must be at least 5 seconds longer. Cloud Run allows 10 seconds, Fargate 120.

## Configuration & interfaces
| Section | Purpose |
|---|---|
| `listen` (required) | Bind, `public_url`, TLS |
| `oidc` (required) | `issuer`, `client_id`, `client_secret`, `allowed_email_domains`, `allowed_groups`, `groups_claim`, `google_groups`, `email_claim`, `scopes`, `scope_on_refresh` (2.1.260), `use_pkce`, `token_endpoint_auth_method`, `client_assertion` (2.1.284), `use_proxy` (2.1.227), `ca_cert_pem` |
| `session` (required) | `jwt_secret`, `ttl_hours` |
| `store` (required) | `postgres_url`, `username`, `password`, `max_connections`, `connect_timeout_seconds` (2.1.274), `readiness_grace_seconds` |
| `upstreams` (required) | Ordered providers |
| `admin`, `enforcement`, `pricing`, `models`, `managed`, `telemetry` | Optional |
| `access_control`, `limits`, `timeouts`, `rate_limits` | HTTP tuning |
| `load_test_mode` | Signed, unsent requests with canned replies (2.1.283) |

Secret expansion supports `${VAR}` (boot fails if undefined) and `${file:/path}` as a field's entire value. `CLAUDE_GATEWAY_LOG_LEVEL` sets operational verbosity; audit events always emit.

Client feature limits: cloud sessions, Remote Control and claude.ai-only features aren't available through a gateway. See [feature-availability.md](feature-availability.md).

## Failure modes & edge cases
- Request headers too large after sign-in: IdP group-heavy tokens.
- Long thinking hitting proxy timeouts: raise timeouts and keep `API_TIMEOUT_MS` above gateway TTFB.
- Org-wide sign-outs need `jwt_secret` rotation.
- Forced login with an API key configured gives a startup refusal naming the credential (2.1.284).

## Changes since the snapshot
- All post-snapshot. 2.1.198: Platform on AWS, `404` failover. 2.1.206: public endpoints. 2.1.225: spend warning. 2.1.229: pings. 2.1.232: boot validation. 2.1.233: identity forwarding.
- 2.1.251: spend bar. 2.1.260: `scope_on_refresh`. 2.1.268, 2.1.271: pricing. 2.1.277: egress boundary. 2.1.281: `assume_role`. 2.1.283: `mantle`, `load_test_mode`. 2.1.290: Deny. 2.1.295: TTFB, user-settings login. 2.1.314: `guardrail_trace`.

## Open questions
- Full `managed.policies[]` key allowlist per surface.
- Full config for AWS and GCP deployment recipes is left to the dedicated docs.
