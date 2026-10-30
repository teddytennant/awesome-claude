# Telemetry, Monitoring and Analytics
**Status:** shipped (traces in beta)
**Provenance:** both (`services/analytics/`, `utils/telemetry/` in snapshot; many event and attribute changes post-leak)
**Sources:** docs `monitoring-usage.md`, `analytics.md`, `data-usage.md`, `env-vars.md`; snapshot `services/analytics/`; changelog 2.1.98 to 2.1.312

## Purpose
Three separate data paths exist. **OpenTelemetry export** goes to the customer's collector and is opt-in. **Operational telemetry** (metrics, error reports) goes to Anthropic and its vendors. **Analytics dashboards** present aggregated usage on claude.ai and the Console.

## Behaviour

### OTel enablement
1. Export MUST require `CLAUDE_CODE_ENABLE_TELEMETRY=1`, plus exporters (`OTEL_METRICS_EXPORTER`, `OTEL_LOGS_EXPORTER`: `console`, `otlp`, `prometheus` for metrics, `none`). No default OTLP protocol exists.
2. Project and local settings MUST NOT turn on export, set its endpoint, or capture content (2.1.282). A startup notice, `/status` and `claude doctor` list ignored variables.
3. `OTEL_*` values MUST NOT pass to subprocesses (Bash, hooks, MCP, language servers).
4. Per-signal variables win over generic ones; per-signal headers merge with generic headers.
5. Default intervals: metrics 60 seconds, logs and traces 5 seconds. Temporality defaults to `delta`.
6. `OTEL_RESOURCE_ATTRIBUTES` values also label metric datapoints (2.1.161).

### Managed destination lock
7. A managed `OTEL_EXPORTER_OTLP_*` value MUST remove conflicting developer-set variables at startup, logging a debug warning (since 2.1.217): endpoint removes per-signal endpoints; protocol removes per-signal protocols; credentials remove developer credentials.
8. Exporter selectors keep normal precedence, so a developer can still disable a signal or use console.
9. Developer `BETA_TRACING_ENDPOINT` is removed when logs or traces are pinned (2.1.251).
10. Variables set in managed settings themselves stay, allowing per-signal routing.
11. A launcher naming an OTLP endpoint (Desktop, runner) pins the same way.

### Metrics
| Metric | Unit |
|---|---|
| `claude_code.session.count` | count |
| `claude_code.lines_of_code.count` | count |
| `claude_code.pull_request.count` | count |
| `claude_code.commit.count` | count |
| `claude_code.cost.usage` | USD |
| `claude_code.token.usage` | tokens |
| `claude_code.code_edit_tool.decision` | count |
| `claude_code.active_time.total` | seconds |

### Events
12. Events MUST be emitted as OTel logs with `event.name`, `event.timestamp`, `event.sequence`, and correlation attributes, including `prompt.id`, `message.uuid`, `client_request_id` and `tool_source` (2.1.214).
13. Event set: `user_prompt`, `assistant_response`, `tool_result`, `tool_decision`, `api_request`, `api_error`, `api_refusal`, `api_request_body`, `api_response_body`, `api_retries_exhausted`, `permission_mode_changed`, `auth`, `mcp_server_connection`, `internal_error`, `plugin_installed`, `plugin_loaded`, `skill_activated`, `at_mention`, `hook_registered`, `hook_execution_start`, `hook_execution_complete`, `hook_plugin_metrics`, `compaction`, `subagent_completed`, `feedback_survey`, `retention_sweep`, `managed_settings_resolved`, each under the `claude_code.` prefix.
14. `claude_code.safety_event` MUST NOT be sent since 2.1.312, though `monitoring-usage.md` still lists it.
15. `tool_decision` and `tool_result` carry `tool_use_id`, and `tool_result` carries `tool_input_size_bytes` (2.1.119). `tool_decision` carries `classifier_category` with `OTEL_LOG_TOOL_DETAILS=1` (2.1.301).
16. `api_request` has `cache_creation_5m_tokens`, `cache_creation_1h_tokens` (2.1.300). Numeric attributes on `api_request` and `api_error` are numbers (2.1.122).
17. `user_prompt` carries `prompt` and a copy `prompt_text` when enabled (2.1.287). Masks must name both.
18. `managed_settings_resolved` gives sources and helper state; `OTEL_LOG_MANAGED_SETTINGS=1` adds redacted settings and digests (2.1.274).

### Content gates
| Variable | Adds |
|---|---|
| `OTEL_LOG_USER_PROMPTS` | Prompt text (otherwise length only) |
| `OTEL_LOG_ASSISTANT_RESPONSES` | Response text; falls back to prompts gate |
| `OTEL_LOG_TOOL_DETAILS` | Commands, MCP and skill names, tool input, commit `vcs.ref.head.*` |
| `OTEL_LOG_TOOL_CONTENT` | Tool content in `tool.output` span event |
| `OTEL_LOG_RAW_API_BODIES` | Full bodies, implying the whole conversation (2.1.111) |
| `CLAUDE_CODE_OTEL_CONTENT_MAX_LENGTH` | Content limit, default 60 KB (2.1.214) |

19. Raw file contents MUST NOT appear in metrics or events. Trace spans are a separate path behind gates.
20. `user.email` is sent only to the configured collector, under OAuth.

### Attributes
21. Standard: `session.id`, `ccr.session.id`, `app.version`, `app.entrypoint`, `user.account_uuid`, `user.account_id`, `organization.id`, `user.email`, and others. Cardinality variables: `OTEL_METRICS_INCLUDE_SESSION_ID` (true), `_VERSION` (false), `_ACCOUNT_UUID` (true), `_ENTRYPOINT` (false), `_RESOURCE_ATTRIBUTES` (true), `_REPOSITORY` (false, 2.1.269).
22. Resource attributes: `service.name` (`claude-code`, or `claude-code-desktop` for Code tab), `service.version`, `os.type`, `os.version`, `host.arch`, `wsl.version`. Meter `com.anthropic.claude_code`.
23. `app.entrypoint` values include `cli`, `sdk-cli`, `sdk-ts`, `sdk-py`, `claude-vscode`, `claude-in-slack`.

### Traces
24. Tracing MUST need `CLAUDE_CODE_ENABLE_TELEMETRY=1`, `CLAUDE_CODE_ENHANCED_TELEMETRY_BETA=1` and `OTEL_TRACES_EXPORTER`.
25. Hierarchy: `claude_code.interaction` root; children `claude_code.llm_request`, `claude_code.hook` (detailed beta), `claude_code.tool` with `claude_code.tool.blocked_on_user` and `claude_code.tool.execution`. Subagent spans nest under the Agent tool.
26. Spans carry `gen_ai.*` conventions, such as `gen_ai.provider.name`, `gen_ai.conversation.id`, `gen_ai.tool.name`, `error.type`, plus `stop_reason`, `gen_ai.response.finish_reasons` (2.1.121, 2.1.300).
27. Bash and PowerShell subprocesses MUST inherit `TRACEPARENT`.
28. `traceparent` on model and HTTP MCP requests is sent only for direct Anthropic API connections by default.
29. SDK and `-p` sessions MUST read `TRACEPARENT` and `TRACESTATE` to parent interaction spans (2.1.110), and event records then carry `trace_id` and `span_id`.
30. A deferred `PreToolUse` saves trace context for resume.
31. Turn spans wrap correctly under concurrent SDK calls, and headless turns end spans per turn (2.1.98).

### Dynamic headers and mTLS
32. `otelHeadersHelper` runs a script for headers, on `http/*` protocols only; `grpc` does not use it. Refresh defaults to 29 minutes (`CLAUDE_CODE_OTEL_HEADERS_HELPER_DEBOUNCE_MS`).
33. mTLS variables follow network config.

### Cloud sessions
34. Device files don't configure hosted sessions. Use `env` in server-managed settings, or the environment's variables. The latter is the only route for Claude Tag.
35. Exports travel on the session's network, so collectors must be allowed. Environment variables are readable by all users, and network secrets don't apply to Claude Code's own telemetry.
36. Cowork doesn't receive server-managed settings; it has its own admin form.

### Audit
37. Docs map security questions to events, such as `tool_decision`, `permission_mode_changed`, `hook_execution_complete`, `mcp_server_connection`, and `retention_sweep`, including egress paths to managed controls.

### Operational telemetry
38. Metrics to Anthropic default on for Claude API, off for Bedrock, Vertex, Foundry and Claude Platform on AWS unless `CLAUDE_CODE_PROVIDER_MANAGED_BY_HOST` applies. `DISABLE_TELEMETRY` or `DO_NOT_TRACK` opts out.
39. Error reports are on only for Pro and Max sign-ins on 2.1.198+ connecting directly without ZDR or HIPAA. `DISABLE_ERROR_REPORTING=1` opts out.
40. Metrics exclude code, prompts and file paths. Error reports redact known patterns.
41. `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1` covers all non-essential traffic.
42. Surveys: `CLAUDE_CODE_DISABLE_FEEDBACK_SURVEY=1`; `CLAUDE_CODE_ENABLE_FEEDBACK_SURVEY_FOR_OTEL=1` routes ratings to the customer's collector.
43. `/feedback` sends conversation history on first-party, and saves locally otherwise.
44. Export failures log as `[Anthropic telemetry]` at debug level (2.1.248).
45. Analytics stays off from startup with forced gateway login or a custom OAuth deployment (2.1.247).
46. Large requests to `api.anthropic.com` use gzip regardless of telemetry; `CLAUDE_CODE_GZIP_REQUEST_BODIES=0` disables (2.1.300).
47. Snapshot architecture: a sink routes events to Datadog and a first-party logger, with sampling, kill switch, metadata sanitising (tool names, file extensions), and feature flag evaluation. Disabled in tests, on third-party providers, and at reduced privacy levels. Current state is not public.

### Dashboards
48. Team and Enterprise: `claude.ai/analytics/claude-code`. Usage metrics, contribution metrics (public beta, GitHub App plus GitHub analytics toggle, github.com only, not under ZDR), leaderboard, CSV export. Admins and Owners can view. Data appears in about 24 hours.
49. API customers: `platform.claude.com/claude-code`, with usage, spend, team insights.
50. Per-user token cost needs OTel or the spend report.
51. Code Review has its own dashboard.

## Configuration & interfaces
Variables as above. Also `OTEL_METRIC_EXPORT_INTERVAL`, `OTEL_LOGS_EXPORT_INTERVAL`, `OTEL_TRACES_EXPORT_INTERVAL`, `OTEL_EXPORTER_OTLP_METRICS_TEMPORALITY_PREFERENCE`.

## Failure modes & edge cases
- A signal can vanish if a developer sets its exporter to `none`, since selectors aren't locked.
- Claude Tag `user.*` attributes describe the shared identity, not the tagger.
- gRPC with dynamic headers won't use the helper.
- `OTEL_LOG_RAW_API_BODIES` carries whole conversations to collectors.

## Changes since the snapshot
- 2.1.98, 2.1.101, 2.1.110: tracing fixes, gates, `TRACEPARENT`. 2.1.111: raw bodies. 2.1.119, 2.1.121, 2.1.122: event fields, `at_mention`.
- 2.1.161: resource attributes on datapoints. 2.1.214: correlation, content limit. 2.1.217: destination lock.
- 2.1.248, 2.1.251: log label, beta endpoint removal. 2.1.269: repository attributes. 2.1.274: `managed_settings_resolved`.
- 2.1.282: project settings ignored. 2.1.287: `prompt_text`. 2.1.300: cache split, GenAI attributes. 2.1.301: `classifier_category`. 2.1.312: `safety_event` stopped.

## Open questions
- Whether `safety_event` docs will be retired; the page and changelog disagree.
- Current first-party event pipeline and vendors.
