# Web Tools: WebFetch and WebSearch

**Status:** shipped
**Provenance:** both
**Sources:** docs `tools-reference` (WebFetch, WebSearch), `agent-sdk/typescript`, `data-usage`, `env-vars`, `artifacts`, `errors`; snapshot `tools/WebFetchTool`, `tools/WebSearchTool`; changelog 2.1.105, 2.1.212, 2.1.233, 2.1.268, 2.1.285, 2.1.290, 2.1.299, 2.1.307

## Purpose

Let Claude read a known URL and search the web. WebFetch is intentionally lossy: page content passes through a separate model call. WebSearch returns result links, not page bodies.

## Behaviour

### WebFetch: pipeline

1. Input is `url`, `prompt`, optional `offset`. Output is `bytes`, `code`, `codeText`, `result`, `durationMs`, `url`, optional `artifactRead`.
2. HTTP URLs MUST be upgraded to HTTPS.
3. `localhost` and any hostname without a dot MUST be refused before a request, with an error pointing to `curl` through Bash.
4. HTML responses are converted to Markdown; this is not configurable. `<style>` and `<script>` contents are stripped (2.1.105). The request MUST send a `User-Agent` beginning with `Claude-User` and an `Accept` that prefers Markdown.
5. For most fetches, the `prompt` runs over the content in a separate model call and Claude receives that output, not the raw page. A result saying a page does not mention something may only mean the prompt did not ask for it.
6. That read's effort follows the caller's level on the caller's own model, otherwise the level settings give the small model (2.1.299).
7. On an overloaded API the extraction step retries with backoff, then errors.

### WebFetch: limits

8. Up to 100,000 characters per call. On v2.1.290+ the result says how much went unread, and `offset` (characters to skip) continues reading.
9. Responses are cached 15 minutes by default (`CLAUDE_CODE_WEBFETCH_CACHE_TTL_MS`, v2.1.233+).
10. A page not downloaded within five minutes, including redirects, fails with a deadline error (`CLAUDE_CODE_WEBFETCH_DEADLINE_MS`, v2.1.268+; `0` removes it).
11. A redirect to a different host MUST NOT be followed. The tool returns text naming both URLs, and Claude makes a second call.

Snapshot-only limits, not confirmed as current: URL length 2,000, HTTP body 10 MB, 10 same-host redirects, cache 50 MB.

### WebFetch: permissions

12. In Manual and `acceptEdits` modes a fetch prompts, unless permission rules decide it or the domain is in the built-in preapproved documentation set.
13. The prompt offers: yes once; yes and do not ask again for the domain, saving `WebFetch(domain:...)` to `.claude/settings.local.json`; no with feedback. The middle option MUST be hidden under `allowManagedPermissionRulesOnly`.
14. `auto` and `bypassPermissions` skip the prompt except for a domain matched by an explicit `ask` rule.
15. Explicit `WebFetch(domain:...)` rules in `deny`, `ask` or `allow` take precedence over the preapproved set. `WebFetch(domain:*)` allows all.
16. A plain `WebFetch` deny or ask rule MUST NOT apply to Artifact tool reads and updates; use an `Artifact` rule or `WebFetch(domain:claude.ai)` (2.1.268).
17. Whatever the rules allow, a fetch MUST first pass the domain safety check, which sends only the hostname to Anthropic and runs on every provider. A passing hostname is cached five minutes. Rate-limit errors from the check tell Claude not to loop (2.1.286). Enforcement detail is out of scope.
18. The sandbox and WebFetch allowlists are one-directional. Sandboxed commands do not inherit the preapproved set; a `WebFetch(domain:...)` rule or `allowedDomains` entry is needed. WebFetch never reads the sandbox allowlist, so sandbox entries do not stop it prompting.

### WebFetch: artifacts

19. For a claude.ai artifact link, Claude Code MAY ask for approval to read it, using the same questions as the Artifact tool's read (2.1.286). When the Artifact tool is available, Claude reads such links with it instead (2.1.277). `artifactRead` records the read so a later publish builds on the right version.

### WebFetch: availability

20. `CLAUDE_CODE_DISABLE_WEB_FETCH=1` turns it off (v2.1.285+). `--restricted` removes it unless named in `--tools`.
21. For Team and Enterprise claude.ai accounts not using an LLM gateway, and sessions whose plan cannot be determined, the tool depends on organization policy loaded from `api.anthropic.com` at session start. If the policy did not load, the tool MUST be withheld until it confirms the org allows it (2.1.285). `/status` and `claude doctor` show an `Organization policy` line. Once a permitting policy loads, the tool returns without restart.

### WebSearch

22. Input is `query`, optional `allowed_domains` or `blocked_domains`; the two MUST NOT be combined in one call. Output is `query`, `results`, `durationSeconds`, optional `searchCount`.
23. Runs against Anthropic's server-side web search and returns titles and URLs. It does not fetch pages; Claude follows up with WebFetch.
24. One call MAY issue up to eight backend searches.
25. Permission rules take no specifier. The backend is not configurable; other providers come through MCP.
26. On an overloaded API it retries with backoff, then errors.
27. Availability: Claude API, Claude Platform on AWS, Foundry; Agent Platform with Opus 4, Sonnet 4, Haiku 4.5 and later. Bedrock has no server-side search.

### WebSearch: search budget

28. Interactive terminal sessions have a limit of 200 calls, shared by the main conversation and subagents (2.1.212). The limit refills at about 100 calls per hour (2.1.290).
29. At the limit, searches appear as calls that did nothing, and Claude gets a notice to continue with what it has, say so, and ask the user to raise the limit if needed. The notice also tells it not to query search engines through a browser or computer use (2.1.307).
30. `/clear` resets the count, unless work that can still spawn subagents survives, in which case the count carries over.
31. In `-p` and the Agent SDK the limit is per turn, resetting at the next message or new `claude -p` run, even with `--continue` or `--resume`. Default refill there is `0`.
32. The cap can be raised but not disabled.

## Configuration & interfaces

| Key | Effect |
| :- | :- |
| `CLAUDE_CODE_DISABLE_WEB_FETCH` | Remove WebFetch |
| `CLAUDE_CODE_WEBFETCH_CACHE_TTL_MS` | Cache TTL; plain digits; read once per launch |
| `CLAUDE_CODE_WEBFETCH_DEADLINE_MS` | Download deadline |
| `CLAUDE_CODE_MAX_WEB_SEARCHES_PER_SESSION` | Cap; positive whole number |
| `CLAUDE_CODE_WEB_SEARCH_REFILLS_PER_HOUR` | Refill rate; `0` is off |
| `sandbox.network.allowedDomains` | Sandbox only, not WebFetch |

`OTEL_LOG_TOOL_CONTENT=1` adds WebFetch and WebSearch outputs to the `tool.output` span event (2.1.283).

## Failure modes & edge cases

- A false "not mentioned" from a narrow extraction prompt is expected behaviour.
- A blocked `api.anthropic.com` makes WebFetch fail at the safety check.
- In cloud sessions, a host that does not resolve is explained as possibly outside allowed network domains (2.1.312). A page that failed moments ago is reported without refetching in Cowork cloud sessions (2.1.300). Stalled requests there fail after 300 seconds (fixed 2.1.311).
- WebSearch at effort `xhigh`/`max` with thinking off used to fail with 400 (fixed 2.1.221).

## Changes since the snapshot

- 2.1.105: script and style stripping.
- 2.1.212: session search limit.
- 2.1.233, 2.1.268: cache TTL and deadline variables.
- 2.1.268: plain `WebFetch` rules no longer touch Artifact.
- 2.1.277, 2.1.286: artifact link handling.
- 2.1.283: OpenTelemetry output.
- 2.1.285: `CLAUDE_CODE_DISABLE_WEB_FETCH`; org-policy withholding.
- 2.1.290: `offset` reads; search refill.
- 2.1.292: WebFetch ignores stray parameters.
- 2.1.299: extraction effort.
- 2.1.307: stronger budget notice.

## Open questions

- Which fetches skip the extraction call ("most fetches" is the documented scope); the snapshot's treatment of preapproved hosts is unconfirmed.
- The current preapproved domain list.
- Whether body, URL and same-host redirect limits still match the snapshot.
