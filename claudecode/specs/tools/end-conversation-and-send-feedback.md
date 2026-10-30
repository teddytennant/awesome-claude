# EndConversation and SendFeedback

**Status:** shipped
**Provenance:** post-leak (EndConversation since v2.1.214, 2026-07-18; SendFeedback since v2.1.247, 2026-08-26, docs say v2.1.238)
**Sources:** docs `tools-reference` (EndConversation, SendFeedback), `sub-agents`, `settings-reference`, `env-vars`; changelog 2.1.214, 2.1.247

## Purpose

Two session-boundary tools. `EndConversation` lets Claude end a session as a last resort. `SendFeedback` lets Claude draft a report about Claude Code that stays local until the user sends it.

## Behaviour

### EndConversation: use

1. Claude uses the tool only:
   - as a last resort against sustained abusive input, after attempts to redirect and a clear earlier warning; or
   - when the user explicitly asks to see it demonstrated and confirms ending the session.
2. General frustration, profanity, a failing task, and requests for harmful content MUST NOT qualify. Harmful requests are declined instead.

### EndConversation: effect

3. An ended interactive session MUST lock. New prompts and most commands return `Claude ended this conversation. Start a new session (or /clear) to continue.`
4. Only `/clear`, `/resume`, `/help`, `/exit` and `/feedback` still run.
5. The end MUST be recorded in the transcript. Resuming restores the lock; history is not deleted.
6. Resuming an ended session with `-p` MUST error and exit with code 1, so scripts do not read it as success.

### EndConversation: controls

7. It never prompts, and PreToolUse hooks do not run for it.
8. While any other tool remains, it cannot be blocked: deny and ask rules naming it have no effect, and neither `--disallowedTools` nor a `--tools` list removes it. Docs justify this by noting the tool only ends the conversation, and a safeguard of this kind holds only if the affected session cannot switch it off.
9. Exception: when deny rules remove every other tool and also match it (such as `"*"`), it MUST be removed too, rather than left as the only tool, unless an allow rule names it explicitly. A deny list that removes all others without matching it leaves it in place.
10. Subagents never get it. Background tasks sharing the main tool list see it, but calling it there ends nothing.

### EndConversation: availability

11. The tool appears only when all hold:
    - **Model:** Opus 4.8, Sonnet 5, Fable 5, or later in those families.
    - **Surface:** interactive terminal, including an IDE integrated terminal. Excluded: `-p`, Agent SDK packages, the VS Code panel, GitHub Actions, cloud sessions.
    - **Startup:** not `--bare`.
    - **Provider:** not Bedrock, Claude Platform on AWS, Agent Platform, Foundry, or cloud-gateway sign-in.

### SendFeedback: drafting

12. Claude drafts a report when a tool or command keeps failing, it cannot do what was asked, a mistake is pointed out or noticed, or the user asks.
13. Drafts MUST be saved under `~/.claude/feedback/drafts/`, and nothing reaches Anthropic until the user sends.
14. The working directory is kept in the local draft to find the transcript, and is not sent.

### SendFeedback: review

15. A card above the prompt shows the title. `1` reviews, `2` twice sends as written, `0` dismisses. A dismissed draft stays queued.
16. After a dismissal, Claude Code asks whether to turn the feature off, and stops asking after two declines.
17. At most three cards per session by default, server-adjustable. After that, or with `feedbackDrafts: quiet`, only a footer count shows.
18. `/feedback` with no argument opens the queue across all sessions. A draft can have its title, area and details edited, and **Send transcript** set. It starts at `yes` when the transcript is still available. Pressing `w` opens the standard dialog. `/feedback <text>` and `/bug` open it directly.

### SendFeedback: sending

19. Sending works like a `/feedback` report, with the same retention, and deletes the local draft. The card shows `✓ Sent`; the queue closes with a receipt ID.
20. The report carries title, area, details, environment info (version, OS, model), recent API request IDs, and the transcript only if **Send transcript** is `yes`. Sending from the card MUST NOT include the transcript.

### SendFeedback: retention

21. Discard deletes the draft. A kept draft expires after 30 days, or `cleanupPeriodDays` if shorter.
22. The queue holds 10 drafts across sessions; an eleventh deletes the oldest.
23. `/exit` with drafts from the session asks to review or discard them.

### SendFeedback: availability

24. Included only in interactive terminal sessions on the user's machine using the Claude API.
25. Excluded: `-p` and SDK sessions; cloud sessions; Bedrock, Claude Platform on AWS, Agent Platform, Foundry; `CLAUDE_CODE_SEND_FEEDBACK=0`; `DISABLE_FEEDBACK_COMMAND=1`; `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC`; feature-flag fetching off; organizations with product feedback off, Zero Data Retention or the HIPAA configuration.
26. If a ZDR session still offers it, drafts stay local and sending fails with `Feedback collection is not available for organizations with custom data retention policies.`

## Configuration & interfaces

| Key | Effect |
| :- | :- |
| `feedbackDrafts` | `off`, `quiet`, or default; user or managed; managed wins |
| `/config` **Claude-drafted feedback** | Writes `feedbackDrafts` |
| `CLAUDE_CODE_SEND_FEEDBACK` | `0` off for a session; `1` on only where already allowed |
| `DISABLE_FEEDBACK_COMMAND` | Disables `/feedback`, drafting, `/bug`, `/share` |
| `cleanupPeriodDays` | Can shorten draft expiry |

Neither tool has a published SDK input type.

## Failure modes & edge cases

- `--tools` lists do not remove `EndConversation`, so a caller's tool allowlist is not exhaustive in interactive terminal sessions on qualifying models.
- `/feedback` still runs in a locked session.
- A draft's transcript option depends on the transcript still existing.

## Changes since the snapshot

- 2.1.214: EndConversation added. The changelog wording mentions abusive users and jailbreak attempts, while current docs exclude requests for harmful content.
- 2.1.247: SendFeedback added, with `feedbackDrafts`.
- Both tools are absent from the snapshot.

## Open questions

- Discrepancy on SendFeedback's first version: docs v2.1.238, changelog 2.1.247.
- Whether "jailbreak attempts" remains a trigger; docs do not list it.
- Input schemas for both tools.
- `feedbackDrafts` default value name.
