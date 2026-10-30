# Delivery and Reporting Tools: PushNotification, SendUserFile, ShareOnboardingGuide, ReportFindings

**Status:** shipped
**Provenance:** post-leak (PushNotification since v2.1.110, 2026-04-15; ReportFindings since v2.1.196 per SDK docs; ShareOnboardingGuide with `/team-onboarding`, v2.1.101, 2026-04-10 or later); PushNotification and SendUserFile also have gated references in the snapshot
**Sources:** docs `tools-reference`, `agent-sdk/typescript`, `remote-control`, `commands`, `env-vars`; snapshot `tools.ts`, `tools/ToolSearchTool/prompt.ts`, `tools/ConfigTool/supportedSettings.ts`; changelog 2.1.101, 2.1.110, 2.1.181, 2.1.293, 2.1.295, 2.1.299

## Purpose

Tools that get output to the user by something other than the terminal transcript: a phone or desktop notification, a delivered file, a shareable onboarding guide, or a structured review list.

## Behaviour

### PushNotification

1. Input: `message`, `status` (literal `"proactive"`). `message` SHOULD stay under 200 characters, since mobile systems truncate longer text.
2. Output: `message`, optional `pushSent`, `localSent`, `disabledReason` (`config_off`, `user_present`, `no_transport`), `sentAt`.
3. It sends a desktop notification, plus a phone push when Remote Control is connected. Long-running tasks and scheduled tasks use it to reach an absent user.
4. Claude decides when to push, typically when a long task finishes or a decision is needed. A user can also ask, for example "notify me when the tests finish". Beyond the toggles there is no per-event configuration.
5. Mobile push needs **Push when Claude decides** enabled in `/config`. **Push when actions required** is a separate toggle covering permission prompts and questions.
6. By default the tool MUST skip both desktop notification and mobile push on recent keyboard activity or terminal focus. `CLAUDE_CODE_DISABLE_NOTIFICATION_PRESENCE_CHECK=1` disables only that local check, so the server can still suppress the mobile push. `CLAUDE_CLIENT_PRESENCE_FILE` extends suppression of mobile push to whenever the marker file exists.
7. Not accessible on Bedrock, Claude Platform on AWS, Agent Platform or Foundry, because delivery runs through Anthropic-hosted infrastructure.
8. Remote Control, `/schedule` and notification preferences are disabled when an API key or auth token is set, even with a claude.ai login (2.1.139).

### SendUserFile

9. Sends session files to the user, with an optional caption, so a report, diagram, screenshot or build output reaches their device rather than only being named in the transcript.
10. `display` controls presentation: `render` opens inline, `attach` shows a download card, and unset leaves it to the client by file type.
11. Available only with a Remote Control client connected, or in a cloud session.
12. Not available on Bedrock, Agent Platform or Foundry. Docs for this tool omit Claude Platform on AWS from that list, unlike `PushNotification`.
13. In the snapshot, delivery tools were kept out of deferral so they were immediately callable with an active bridge. Whether that holds is unknown.

### ShareOnboardingGuide

14. Called from `/team-onboarding` after `ONBOARDING.md` is written. It uploads the guide and returns a share link teammates open in Claude Code.
15. It requires permission and accepts only the bare tool name in rules.
16. Available to claude.ai subscribers on Team and Enterprise plans. Others get the local Markdown guide from the command, which draws on 30 days of sessions, commands and MCP usage.

### ReportFindings

17. Reports code-review findings as a structured list so Claude Code renders them rather than printing text. Claude calls it when active code-review instructions say to.
18. Input: optional `level` (`low` to `max`), and `findings`, each with:

| Field | Required | Meaning |
| :- | :- | :- |
| `file` | Yes | Repo-relative path |
| `line` | No | 1-indexed anchor |
| `summary` | Yes | One sentence on the defect |
| `failure_scenario` | Yes | Concrete inputs and state causing the failure |
| `short_summary` | No | Up to 60 characters; v2.1.212+ |
| `category` | No | Kebab-case slug, shown beside the location; v2.1.199+ |
| `verdict` | No | `CONFIRMED` or `PLAUSIBLE`; set when a verify pass ran |
| `outcome` | No | `fixed`, `skipped`, `no_change_needed`; set only when re-reporting after fixes |

19. Findings are ordered most-severe first, at most 32 per call, and empty when none survived.
20. `level` is what Claude reports, and is not compared with the level the review ran at.
21. Output: `count`, `level`, and the findings echoed.

## Configuration & interfaces

| Key | Effect |
| :- | :- |
| `/config` **Push when Claude decides** | Proactive pushes |
| `/config` **Push when actions required** | Prompt and question pushes |
| `CLAUDE_CLIENT_PRESENCE_FILE` | Marker file suppresses mobile push (2.1.181) |
| `CLAUDE_CODE_DISABLE_NOTIFICATION_PRESENCE_CHECK` | Desktop notification despite terminal activity |

Snapshot config keys, unconfirmed as current names: `agentPushNotifEnabled`, `inputNeededNotifEnabled`, `taskCompleteNotifEnabled`.

## Failure modes & edge cases

- `/config` shows **No mobile registered** until the phone app refreshes its token.
- iOS Focus modes can delay or suppress pushes.
- PushNotification used to report Remote Control inactive in SDK-hosted and `claude remote-control` sessions (fixed 2.1.152, 2.1.293, 2.1.295).
- `/config` toggles used to send the previous value (fixed 2.1.299).

## Changes since the snapshot

- 2.1.101: `/team-onboarding`.
- 2.1.110: push notification tool.
- 2.1.181: `CLAUDE_CLIENT_PRESENCE_FILE`.
- v2.1.196, v2.1.199, v2.1.212: `ReportFindings` and its optional fields (SDK docs).
- 2.1.214: Remote Control "session ready" push limited to sessions with Remote Control explicitly enabled.
- 2.1.293, 2.1.295, 2.1.299: PushNotification reporting fixes.

## Open questions

- Full `SendUserFile` input schema and size limits; it has no published SDK type.
- First public version of `SendUserFile`; there is no changelog line.
- Whether `ShareOnboardingGuide` link storage has an expiry.
- Whether Claude Platform on AWS supports `SendUserFile`.
