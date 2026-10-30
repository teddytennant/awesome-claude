# Artifacts
**Status:** shipped
**Provenance:** post-leak (no snapshot code; docs cite behaviours from 2.1.209 onward)
**Sources:** docs `artifacts.md`, `routines.md`, `env-vars.md`, `settings-reference.md`; changelog 2.1.265 to 2.1.311

## Purpose
Publish session output as a private, live web page on claude.ai, which can be updated in place, shared, commented on, and connected to live data.

## Behaviour

### Availability
1. MUST need every one of: Pro, Max, Team or Enterprise; a claude.ai-backed session; Anthropic API (not Bedrock, Agent Platform, Foundry); no CMEK, HIPAA or ZDR; CLI or Desktop 1.13576.0+, Claude Tag sessions, or user-started `claude remote-control` sessions.
2. API keys, gateway tokens and cloud credentials MUST NOT publish.
3. Org policy loads from `api.anthropic.com`. If unavailable, artifacts are unavailable, with retry in the background.
4. Otherwise Claude writes a local HTML file or says it can't publish.

### Publishing
5. Claude MAY publish unprompted when output suits a page. Pages are written to a temp directory by default, then published privately, and the browser opens.
6. `CLAUDE_CODE_ARTIFACT_AUTO_OPEN=0` prevents opening. No tab opens for prompts through Remote Control.
7. `Ctrl+]` reopens the latest artifact. A `⧉ name` or `⧉ N` pill opens `/artifacts` (2.1.281).
8. Claude picks a title and tab icon (2.1.268) and uses a name the user gave as title (2.1.284). Publish results name the icon, and warn on NUL bytes (2.1.275).
9. Files MUST be `.html`, `.htm` or `.md`, UTF-8 or BOM-marked UTF-16LE. `U+FFFD` or undecodable input is refused with line and column.
10. Rendered size MUST be at most 16 MiB. Markdown renders as styled documents (2.1.271).
11. Network-host paths MUST be refused without being read, except mapped drives added with `--add-dir` (2.1.284).
12. Disallowed file types give a plain error stating what is served (2.1.273).
13. Large uploads are compressed (2.1.281). A dropped publish is retried safely without duplicates (2.1.273).

### Permission
14. A publish from a typed prompt MUST pass without a prompt or classifier, except:

| Case | Behaviour |
|---|---|
| Plan mode | Asks before first publish of each artifact |
| Declares runtime capabilities | Asks |
| Publicly shared | Asks once per conversation before changing |
| Session-scoped schedule turn | Asks before first publish |
| File unreadable without approval | Asks; `Artifact` allow rule doesn't skip |
| File edit needing approval in Manual or `acceptEdits` | Asks |

15. In auto mode the classifier reviews those cases. Routine behaviour is in [routines.md](routines.md).
16. Plain `WebFetch` rules don't apply to artifact reads; use `Artifact` rules or `WebFetch(domain:claude.ai)` (2.1.268).

### Updating
17. A publish MUST create a version at the same URL; open pages update live. The Share control picks which version viewers see.
18. A small change can apply in the same publish call, and is written to disk after approval (2.1.300). The prompt then notes the edit.
19. Other sessions need the URL or `/artifacts` attach. Otherwise a new artifact is created.
20. A publish built on an older version MUST be stopped, and Claude merges onto the newer page (2.1.274).
21. Claude updates shared artifacts in place when the user has edit access (2.1.275).

### Finding
22. `/artifacts` lists owned and shared, with This session first. Keys: `Enter` open or attach, `o` open, `c` copy, `d` delete with numbered confirm (1 or Enter keep, 2 delete, Esc cancel; 2.1.305). Delete isn't available in a cloud session.
23. Opening in a browser closes the list (2.1.290).
24. Listing supports up to 200 at once (2.1.292).

### Sharing
25. New artifacts are private. Team and Enterprise can share with people or the org. Public links need no sign-in, and on Team and Enterprise need an Owner to enable **External sharing**. Turning it off blocks existing links.
26. Viewers vs editors: editors (Team and Enterprise) republish through Claude.
27. Views link by `#name` anchors (2.1.311).
28. Org viewers see the publisher's name; outsiders see a generic label.

### Reading others' artifacts
29. Claude MUST read others' pages as a summary answering what it asked, reporting embedded instructions rather than relaying them (2.1.265). Full source is saved locally.
30. Extra approval applies: cloud sessions with no network; another org's public artifact (even in auto mode, and impossible where it can't ask); unconfirmed owner or network state; plan mode.
31. claude.ai artifact links MUST use the Artifact tool over WebFetch when available (2.1.277). If unreadable, Claude tells the user (2.1.280). Chat or project links prompt for the right link (2.1.284).

### Comments
32. Claude can read threads (2.1.221) on org-shared artifacts, and reply to or resolve activated ones, via **Send to Claude** or `@claude` from an editor.
33. After publishing, the session MUST watch for sent comments (2.1.228). Replies are automatic if the mode allows, otherwise `Comments are waiting on Artifact: <name>`. Plan mode pauses.
34. Auto replying stops after 60 sent comments or activations in an hour.
35. Stops: Ctrl+C at idle pauses until next message; stopping the task in `/tasks` stops that artifact persistently; `Ctrl+X Ctrl+K` twice in 3 seconds stops for the session.
36. Local sessions can watch up to 25 artifacts (2.1.299). A new version elsewhere doesn't start a turn (2.1.274). Auto-armed watches end after 3.5 idle hours (2.1.283).

### Runtime capabilities
37. Declared at publish: connector calls and file downloads, among others set per account.
38. Connector calls (2.1.209) MUST run through the viewer's connections after their consent. Calls never expose credentials. Side-effect actions use the clicking viewer's account. Unsigned or external viewers see no live sections.
39. Responses are browser-cached. Pages may refresh on an interval.
40. A page cannot start downloads itself, including `data:` and `blob:` links. The downloads capability provides controls.
41. An artifact database exists. Updates can remove a single field (2.1.273), ordered queries state when a result is one page (2.1.283), and size-limit refusals state the limit and what frees space (2.1.288). Reads saved to the scratchpad skip working-folder approval (2.1.269).

### Page limits
42. Pages are single, self-contained, wrapped in a shell, under strict CSP. External: Google Fonts; scripts from cdnjs, unpkg (2.1.281), Tailwind CDN, jQuery CDN, and jsDelivr paths. All other external loads are blocked, including images.
43. No backend or viewer auth. Relative links don't resolve.
44. Claude pins libraries at exact versions two weeks old or more (2.1.293), avoids blocked Print and dialog features, and supports dark mode (2.1.280).

### Templates
45. Slides, Design and Docs templates (beta) open in claude.ai editors. On by default on Pro, Max and Team; Enterprise Owners enable each. `/slides` and `/design` depend on them.
46. Claude chooses a page for visual or interactive work, and a document for writing people keep editing (2.1.311).

## Configuration & interfaces
| Control | Effect |
|---|---|
| `enableArtifact: false` (`/config` Artifacts row) | Off for user; project scope honoured in recent versions; `true` there doesn't re-enable |
| `disableArtifact: true` | Deprecated |
| `CLAUDE_CODE_DISABLE_ARTIFACT=1` | Off; not reversible by settings files |
| `permissions.deny: ["Artifact"]` | Off |
| Admin **Enable artifact connectors** | Connector calls |
| Retention | Separate private and shared periods |
| Audit | `claude_artifact_*` events |
| Compliance API | `/v1/compliance/apps/code/artifacts` list, version content, delete |

Network: `*.claudeusercontent.com` with `claude.ai`; optionally font and script CDNs. `*.frame.claudeusercontent.com` is needed for local CLI, self-hosted runners, and reading other orgs' public artifacts in cloud sessions.

## Failure modes & edge cases
- `Artifacts need a claude.ai login`.
- Page without live data: viewer lacks connection or consent.
- First session after installing or upgrading past 2.1.221 may not read comments.
- Comments need feature-flag fetching.
- Public-link-only viewers don't see comments.

## Changes since the snapshot
- Feature is post-snapshot. Dated in changelog from 2.1.265 on; see inline versions.
- 2.1.268: icons. 2.1.271: Markdown documents. 2.1.274, 2.1.275: stale publish protection and routines. 2.1.292: unprompted private publishes in routines. 2.1.299: 25 watches. 2.1.300: one-call edits. 2.1.311: `#name` routing, page vs document.

## Open questions
- First release of the Artifact tool (earliest doc-cited version is 2.1.209).
- Limits on the artifact database; the docs page doesn't specify it, and details above come from changelog entries.
