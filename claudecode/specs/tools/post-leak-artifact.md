# Artifact Tool

**Status:** shipped
**Provenance:** post-leak (introduced in the week of 2026-06-15, digest range v2.1.178 to v2.1.183)
**Sources:** docs `artifacts`, `tools-reference`, `agent-sdk/typescript`, `routines`, `env-vars`, `permissions`, `whats-new/2026-w25`; changelog 2.1.257 to 2.1.311

## Purpose

Publish a local HTML or Markdown file as a private, interactive page on claude.ai, for output that is better viewed than read in a terminal. A page updates in place, keeps versions, can be shared, can call MCP connectors for its viewers, and can receive comments that reach the session.

## Behaviour

### Availability

1. Publishing MUST require all of:
   - **Plan:** Pro, Max, Team or Enterprise. Team and Enterprise are on by default, and an Owner can turn them off.
   - **Authentication:** a claude.ai-backed session. API key, gateway token or cloud-provider credentials cannot publish. Claude Tag sessions need no sign-in step.
   - **Provider:** Anthropic API; not Bedrock, Agent Platform or Foundry.
   - **Organization:** no CMEK, HIPAA or Zero Data Retention.
   - **Surface:** CLI or desktop app 1.13576.0+. `claude remote-control`-served sessions can publish when the user started them (v2.1.281+).
2. It MUST be off by default in the Agent SDK, the GitHub Action, MCP-server contexts, `-p` from the user's own scripts, and under `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC`.
3. Permission depends on the org policy from `api.anthropic.com`. If it cannot load, artifacts are unavailable and Claude says why; loading is retried in the background.
4. When unavailable, Claude writes a local file or says it cannot publish.

### Publishing

5. Input per the SDK type: `action` (`publish` or `list`), `file_path`, `icon`, `favicon` (deprecated), `limit`, `scope`, `title`, `description`, `label`, `url`, `force`, `capabilities`, `contract`.
6. Claude writes the page to a file, in a temporary directory outside the project by default, then publishes it. A publish with no file MUST say to write one first (2.1.271).
7. A new artifact is private. The URL prints and the browser opens, unless `CLAUDE_CODE_ARTIFACT_AUTO_OPEN=0` or the prompt came through Remote Control.
8. `icon` is one short generic word on first publish, omitted on update so the stored icon stays (2.1.275).
9. `url` updates an existing artifact. Without a URL or attachment from `/artifacts`, a new session creates a new artifact.
10. Claude MAY apply a small change and publish in one call (2.1.300), reported in prompts as `Also makes 1 edit to that file on disk.` The page publishes first, then the edit is written. `CLAUDE_CODE_ARTIFACT_PUBLISH_EDITS=0` separates the steps. Where a PreToolUse hook covers Edit or Write, Claude edits first then republishes (2.1.301).
11. Each publish is a version. Viewers with the page open update in place.
12. Output is `url`, `path`, optional `title`, `version`, `capabilities`, `stored`, `warnings`, `contract`, `updated`, `liveSubscription`. It states who can open the page.

### Conflict handling

13. A publish built on an older version MUST be stopped before sending, with the newer page returned so Claude merges and republishes (2.1.274).
14. `force` is a last-resort overwrite, used only when the user explicitly asks to discard that version.
15. A publish whose connection drops after reaching claude.ai MUST be re-sent safely, without a duplicate version (2.1.273).

### Prompts

16. A new artifact published from a typed prompt needs no prompt or classifier review. Claude Code asks first, or the classifier reviews in auto mode, when:

| Case | Asks |
| :- | :- |
| Plan mode | Before first publish of each artifact |
| Publish declares runtime capabilities | Before that publish |
| Artifact is public | Once per conversation before changing it |
| Turn started by a session-scoped scheduled task | Before first publish of each artifact |
| File unreadable without approval | Before publishing; an `Artifact` allow rule does not skip it |
| Manual or `acceptEdits`, small edit to a protected file | Before publishing the change |

17. Scheduled runs: in auto mode, a publish goes through once the classifier allows it, unless an ask rule matches. In Accept edits mode, a schedule or **Run now** run MAY publish a new private artifact without asking. It MAY republish only when all hold: user can edit it and it is in their org; user owns it if the publish carries more than the page; it is not public; shared viewers do not auto-see new versions; no `force`; no runtime capabilities; no grant beyond the page. API and GitHub trigger runs ask.

### Reading

18. Claude reads links with this tool rather than WebFetch when available (2.1.277). Someone else's page returns a summary treated as untrusted, flagging embedded instructions rather than relaying them (2.1.265), and the full source is saved locally for editors.
19. Extra approval applies for: cloud sessions with no network; another org's public artifact (asks even in auto mode, and impossible in `bypassPermissions`); unconfirmed owner or network setting; someone else's artifact in plan mode.
20. If Claude cannot read a link, it MUST tell the user before continuing (2.1.280). A chat link, project link or bare ID gets a request for the right link (2.1.284).

### Listing

21. `list` accepts only `limit` and `scope`. `limit` is 1 to 200, default 25. `scope` is `mine`, `shared` or `all`. Rows have `title`, `url`, optional `updatedAt`, `rel`. Results carry `truncated`, `total`, `total_at_least`.
22. `/artifacts` lists owned and shared artifacts, this session's first. Keys: Enter, `o` open, `c` copy, `d` delete with confirmation (not in cloud sessions). `Ctrl+]` reopens the latest; a `⧉` pill shows session artifacts.

### Comments

23. Requires v2.1.221+ and feature-flag fetching. Claude can reply to or resolve only threads activated by an editor (**Send to Claude** or `@claude`).
24. After publishing, the session watches for sent comments (v2.1.228+). Modes decide: auto-reply when no approval is needed; `Comments are waiting on Artifact: <name>` when approval is needed or in plan mode.
25. Auto-replies MUST stop after 60 sent comments or activations on one artifact within an hour, and resume as they age out.
26. Stop controls: `Ctrl+C` once at idle pauses until the next message; stopping the task in `/tasks` sticks across republishing and resume; `Ctrl+X Ctrl+K` twice within 3 seconds stops for the session.
27. Local sessions watch up to 25 artifacts (2.1.299). Automatically armed watches end after 3.5 hours idle (2.1.283). A new version published elsewhere does not start a local turn (2.1.274).

### Page runtime

28. Pages are single, self-contained, static and under a strict CSP:
    - Scripts from cdnjs, unpkg, Tailwind and jQuery CDNs, and selected jsDelivr paths. Typefaces from Google Fonts. All else is inlined or embedded as data URIs.
    - `fetch`, XHR and WebSocket reach only the page's origin and Google Fonts hosts.
    - No relative links; no backend.
    - Claude pins libraries to exact versions at least two weeks old (2.1.293).
29. Source must be `.html`, `.htm` or `.md`, decoding as UTF-8 or LE UTF-16 by BOM, with no `U+FFFD`. Markdown renders as a styled document. Rendered size is at most 16 MiB. Network-share paths are refused without reading (2.1.284).
30. **Capabilities** declare runtime access, validated by the service. `{}` clears, omitted keeps. **`contract`** selects the runtime version: omit to keep, `latest` to upgrade, or pin a version.
31. **Connectors** (v2.1.209+): calls run through each viewer's own account, after that viewer approves. Only claude.ai connectors qualify, not local servers. Side-effecting controls act as the viewer. Unknown declared tool names warn, and the publish is refused when none match (2.1.265). Anonymous or external viewers see no live sections.
32. **Downloads** need the downloads capability; page-initiated downloads are blocked.
33. A database capability exists. Changelog entries cover per-field removal (2.1.273), ordered-query paging (2.1.283), size-limit errors (2.1.288) and a permission card (2.1.268).

## Configuration & interfaces

| Key | Effect |
| :- | :- |
| `enableArtifact` / `/config` **Artifacts** | `false` turns off; `true` in project files does not re-enable |
| `disableArtifact` | Deprecated off switch |
| `CLAUDE_CODE_DISABLE_ARTIFACT=1` | Off; no settings file re-enables |
| `CLAUDE_CODE_ARTIFACT_COMMENTS` | `0` stops comment reads and replies |
| `CLAUDE_CODE_ARTIFACT_COMMENTS_AUTOREACT` | `0` stops auto-replies |
| `Artifact` deny rule | Off |
| `WebFetch(domain:claude.ai)` deny or ask | Applies to artifact reads |

Admin: org toggles for artifacts, connectors and external sharing; retention; `claude_artifact_*` audit events; Compliance API. Viewer origin is `*.claudeusercontent.com`.

## Failure modes & edge cases

- `Artifacts need a claude.ai login`.
- Refused files report the line and column to fix.
- `Not published: Claude sent the same content again after a newer version of the artifact turned it away`.
- A declared capability the contract lacks produces an error listing supported ones (2.1.271).
- HTTP 403 on a capability publish says what to tell the user, not to retry (2.1.299).

## Changes since the snapshot

- Entirely new. Absent from the snapshot.
- 2.1.257: Cowork and cloud reads of others' artifacts always ask.
- 2.1.265: untrusted summaries; connector name validation.
- 2.1.268: icons; WebFetch rule separation; Cowork local-file refusal.
- 2.1.271: watch limit 10; Markdown styling.
- 2.1.273, 2.1.274: safe re-send, stale-publish stop.
- 2.1.275, 2.1.292, 2.1.295: scheduled-run publishing rules.
- 2.1.281: unpkg allowed; compressed uploads.
- 2.1.283: 3.5-hour auto-watch expiry.
- 2.1.292: listing up to 200.
- 2.1.300: one-call edit and publish.
- 2.1.299: watch limit 25.
- 2.1.311: page or document choice; `#name` view routing.

## Open questions

- The SDK `ArtifactInput` documents only `publish` and `list`, yet the changelog describes reads, updates, comments and data operations. The full action surface and any companion tools are not publicly specified.
- The exact introducing version; the changelog has no "Added" line.
- Database capability limits.
- The list of runtime capabilities beyond connectors, downloads and the database.
