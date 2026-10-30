# Third-Party Providers
**Status:** shipped
**Provenance:** both (Bedrock, Vertex, Foundry in snapshot; Claude Platform on AWS, Mantle and wizards post-leak)
**Sources:** docs `amazon-bedrock.md`, `google-vertex-ai.md`, `microsoft-foundry.md`, `claude-platform-on-aws.md`, `model-config.md`, `env-vars.md`; snapshot `utils/model/`, `services/api/`; changelog 2.1.169 to 2.1.312

## Purpose
Run Claude Code against a provider other than the Anthropic API: Amazon Bedrock (Invoke API and Mantle), Google Cloud's Agent Platform (formerly Vertex AI; variable names keep `VERTEX`), Microsoft Foundry, or Claude Platform on AWS.

## Behaviour

### Selection and setup
1. A provider MUST be selected by `CLAUDE_CODE_USE_BEDROCK`, `CLAUDE_CODE_USE_VERTEX`, `CLAUDE_CODE_USE_FOUNDRY`, `CLAUDE_CODE_USE_MANTLE`, or `CLAUDE_CODE_USE_ANTHROPIC_AWS`.
2. The login prompt **3rd-party platform** MUST start a wizard for Bedrock and Vertex. `/setup-bedrock` and `/setup-vertex` reopen it to change credentials, region or project, and pins, writing to user settings. `/setup-bedrock` is hidden until the provider is set.
3. `allowedProviders` (managed) MAY limit providers a machine can use (2.1.285).
4. In these modes, claude.ai features are off: Remote Control, cloud sessions, artifacts, Chrome, `/schedule`. See [feature-availability.md](feature-availability.md).
5. Auto mode needs no opt-in on Bedrock, Vertex and Foundry since 2.1.207; disable by `disableAutoMode`.
6. Spend is billed by the provider. `/logout` is not offered for Foundry; `/login` and `/logout` don't apply to Claude Platform on AWS subscriptions.

### Models
7. Without pins, aliases resolve to Claude Code's built-in defaults for the provider, which can lag. Docs say to pin for multi-user deployments with `ANTHROPIC_DEFAULT_OPUS_MODEL`, `ANTHROPIC_DEFAULT_SONNET_MODEL`, `ANTHROPIC_DEFAULT_HAIKU_MODEL`.
8. Bedrock defaults: primary Opus 5.5 (since 2.1.280), small/fast Sonnet 4.5. Foundry's `opus` alias defaults to Opus 4.6.
9. Background tasks on Bedrock use the default Sonnet because Haiku may be unavailable, or the selected primary model. On Foundry they use the primary model.
10. Startup checks MUST verify access. For a pin older than the default where the newer is invokable, prompt to update; accepting writes user settings and restarts.
11. Unpinned and unavailable defaults MUST fall back for the session with a notice, to earlier versions, then to the default Sonnet when no Opus exists.
12. A session's specific `--model`, `ANTHROPIC_MODEL` or `model` acts as a pin. Aliases and unrecognised IDs do not.
13. Refusals are remembered on the machine for up to a day.
14. `enforceAvailableModels` with `availableModels` limits these checks (Bedrock Invoke, 2.1.287), comparing full inference profile IDs.
15. If access is lost mid-session, an unpinned tier MUST switch with a `Switched to <fallback> because <model>…` notice. A configured fallback chain replaces this. `CLAUDE_CODE_DISABLE_MODEL_ACCESS_FALLBACK=1` makes requests fail.
16. `/model` shows names rather than raw IDs when recognised (2.1.261). `modelPicker` curates entries (2.1.243). `maxEffortLevel` caps effort on all providers (2.1.267).
17. Fable, Sonnet 5+, and Opus 4.7+ MUST run at 1M context by default on Bedrock (Invoke and Mantle) and Agent Platform (since 2.1.287 for the latter). Opus 4.6 and Sonnet 4.6 use the `[1m]` suffix. `CLAUDE_CODE_DISABLE_1M_CONTEXT=1` keeps 200K.
18. Environment, model and settings details are delivered as attachments (2.1.268). Unrecognised model names get the shorter system prompt (2.1.312).

### Bedrock Invoke
19. Credentials: AWS profiles, API key (`AWS_BEARER_TOKEN_BEDROCK`), access keys, environment. Region comes from `AWS_REGION`, else `~/.aws` config (2.1.172); `/status` shows the source.
20. Cross-region prefixes by region: `us-gov.`, `us.`, `eu.`, `apac.`, otherwise `global.`. `ANTHROPIC_BEDROCK_REGION_PREFIX` (2.1.224) prefers another prefix (`us`, `eu`, `apac`, `jp`, `au`, `global`, and others) for built-in defaults, without pinning.
21. IAM: `bedrock:InvokeModel`, `InvokeModelWithResponseStream`, `ListInferenceProfiles`, `GetInferenceProfile`, plus Marketplace subscribe actions. Without `GetInferenceProfile`, ARN shape resolution retries once per model.
22. `ANTHROPIC_BEDROCK_SERVICE_TIER` sends `X-Amzn-Bedrock-Service-Tier`: `default`, `flex`, `priority`.
23. Guardrails MAY be set via `ANTHROPIC_CUSTOM_HEADERS`. A mid-response block keeps streamed text and ends with the configured message.
24. `awsAuthRefresh` re-runs login on expiry; `awsCredentialExport` output is cached until `Expiration` (2.1.176).
25. `ENABLE_PROMPT_CACHING_1H=1` requests 1-hour TTL; `DISABLE_PROMPT_CACHING=1` disables.

### Mantle
26. Mantle serves Claude in the native Anthropic API shape, with the same credentials. IAM uses `bedrock-mantle:CreateInference`, `bedrock-mantle:CountTokens`.
27. IDs are `anthropic.` prefixed without a version suffix, such as `anthropic.claude-sonnet-5`.
28. Setting both Bedrock and Mantle uses both, routing by ID format. `availableModels` surfaces Mantle IDs but restricts the picker.
29. `/status` shows `Amazon Bedrock (Mantle)` or `Amazon Bedrock + Amazon Bedrock (Mantle)`.

### Agent Platform
30. `CLOUD_ML_REGION` accepts `global`, multi-regions, or regions. Per-model overrides exist for global. Project from `ANTHROPIC_VERTEX_PROJECT_ID`.
31. Auth is ADC, a service account key, or environment. `roles/aiplatform.user` suffices; `aiplatform.endpoints.predict` is the needed permission.
32. Expired Google credentials MUST fail within seconds (2.1.228).
33. Idle timeout defaults to 5 minutes for Vertex and Foundry streams; `API_FORCE_IDLE_TIMEOUT=0` opts out (2.1.169).
34. Tool search is enabled for 4.5-generation and newer (2.1.221). Web search is offered for unrecognised models (2.1.282).

### Foundry
35. Auth: `ANTHROPIC_FOUNDRY_API_KEY`, Entra ID via default credential chain, or `ANTHROPIC_FOUNDRY_AUTH_TOKEN`.
36. Resource from `ANTHROPIC_FOUNDRY_RESOURCE` or `ANTHROPIC_FOUNDRY_BASE_URL`. Model values match deployment names, so pinning is mandatory in practice.
37. Roles `Azure AI User` or `Cognitive Services User` suffice.

### Claude Platform on AWS
38. It is the Anthropic-operated API with AWS auth and Marketplace billing. Subscribing provisions a separate Anthropic organization.
39. MUST require `ANTHROPIC_AWS_WORKSPACE_ID`, sent as `anthropic-workspace-id`.
40. Auth: SigV4 via the AWS chain, or `ANTHROPIC_AWS_API_KEY` as `x-api-key`, which takes precedence.
41. Base URL is computed from the region, overridable by `ANTHROPIC_AWS_BASE_URL`.
42. Features enabled by Anthropic's feature-flag service are off by default, and the advisor tool isn't available.
43. `/login` offers **Claude Platform on AWS · refresh credentials** with `awsAuthRefresh` (2.1.186).

## Configuration & interfaces
| Variable | Purpose |
|---|---|
| `ANTHROPIC_BEDROCK_BASE_URL`, `ANTHROPIC_VERTEX_BASE_URL`, `ANTHROPIC_FOUNDRY_BASE_URL`, `ANTHROPIC_BEDROCK_MANTLE_BASE_URL`, `ANTHROPIC_AWS_BASE_URL` | Endpoints or gateways |
| `CLAUDE_CODE_SKIP_BEDROCK_AUTH`, `_VERTEX_`, `_FOUNDRY_`, `_MANTLE_`, `_ANTHROPIC_AWS_` | Skip client auth, for gateways that sign |
| `ANTHROPIC_SMALL_FAST_MODEL_AWS_REGION` | Region for Haiku-class model |
| `CLAUDE_CODE_PROVIDER_MANAGED_BY_HOST` | Host manages routing, as with Desktop |

## Failure modes & edge cases
- Bedrock auth loops with SSO behind corporate proxies; TLS inspection needs CA trust.
- `Bedrock streaming response has content-type`: a gateway rewrote the event stream.
- Zero counts in `/context` when token counting is unavailable.
- Claude Platform on AWS: `403` or `AccessDenied`, missing workspace, or traffic still reaching `api.anthropic.com` when the env isn't set.
- A stale `CLAUDE_CODE_USE_VERTEX` exported by a shell can't be removed from a settings file.
- Application inference profile ARNs aren't pins and need `modelOverrides` for capabilities.

## Changes since the snapshot
- 2.1.169, 2.1.172, 2.1.176: timeouts, region lookup, credential cache. 2.1.186: Platform on AWS refresh.
- 2.1.207: auto mode on by default. 2.1.221: Vertex tool search. 2.1.224: region prefix.
- 2.1.228: quick credential failure. 2.1.234: Mantle probe skipped when a model is picked.
- 2.1.243, 2.1.261, 2.1.267: `modelPicker`, names, `maxEffortLevel`. 2.1.268: attachments.
- 2.1.280: Bedrock primary Opus 5.5. 2.1.285: `allowedProviders`. 2.1.287: `enforceAvailableModels`, Vertex 1M.
- 2.1.312: shorter prompt for unknown names.

## Open questions
- Full mapping of unpinned aliases for each provider over time.
- Mantle's first release in the changelog.
