# Auto Mode

**Status:** shipped
**Provenance:** both (gated as `TRANSCRIPT_CLASSIFIER` in the snapshot; changelog entries from 2.1.77; default start mode since 2.1.283/2.1.284)
**Sources:** docs `permission-modes`, `auto-mode-config`, `auto-mode-classifier-billing`, `settings-reference`, `errors`, `env-vars`; snapshot `utils/permissions/autoModeState.ts`, `denialTracking.ts`, `classifierDecision.ts`, `yoloClassifier.ts` (feature-level only); changelog 2.1.77–2.1.314

Scope: user-visible behaviour, configuration and billing. Classifier internals, prompts and rule wording are excluded. The server-side prompt-injection probe and separate safety checks are noted only where they change what a user sees.

## Purpose

Auto mode replaces routine prompts with a second model that reviews actions, so long tasks run hands-off while risky or out-of-scope actions are stopped. It reduces prompts and does not guarantee safety.

## Behaviour

### Availability

1. Auto mode MUST be available on all plans and providers subject to:
   - Model: on the Anthropic API and Claude Platform on AWS, Opus 4.6+, Sonnet 4.6+, Haiku 5.5, Fable. On Bedrock, Agent Platform, Foundry and signed-in Claude apps gateway, Sonnet 5+, Opus 4.7+, Haiku 5.5, Fable. Older models unsupported anywhere.
   - No settings file setting `disableAutoMode: "disable"`.
   - Not turned off server-side and not rejected for the account. Either answer keeps auto off for the rest of the session.
2. If unavailable, a session that requested auto MUST start in Manual. The auto tab, cycle entry and offers MUST be absent.

### Decision order

3. Each action MUST follow this order, first match wins:
   1. Allow, ask and deny rules resolve at once, with exceptions: protected-path writes go to the classifier even with an allow rule; critical-path removals are not approvable by allow rules; requires-interaction MCP tools, org-`ask` connector tools, symlink-to-protected writes and network-path reads prompt; content-scoped ask rules prompt; shell commands carrying per-command domains go to the classifier.
   2. Read-only actions and working-directory edits auto-approve, except protected paths and the first out-of-directory read. Under server-side review, read-only and sandboxed shell commands wait for review and are blocked if flagged. Writes the symlink check resolves outside prompt.
   3. Everything else goes to the classifier, except critical-path removals under default handling and the direct-prompt tools.
   4. On a block, Claude receives the reason, normally the matched rule name such as `[Data Exfiltration]`.
4. Entering auto mode MUST suspend allow rules that grant arbitrary execution (blanket shell, wildcarded interpreters, package-manager run commands, `Agent` and `Monitor` rules) and MUST restore them on exit. Narrow rules stay.
5. `autoMode.classifyAllShell: true` MUST suspend every Bash and PowerShell allow rule while auto is active, so every shell command is reviewed except critical-path removals.
6. Before commands that would discard uncommitted work, the client MUST inspect git status itself and give the classifier the result, including untracked files regardless of repository config.
7. Client-sent classifier requests see user messages, tool calls other than read-only lookups, and `CLAUDE.md` content. Tool results MUST be stripped so hostile content cannot address the classifier. A PostToolUse hook's `classifierContext` adds application context (2.1.236).

### What is reviewed

8. The classifier MUST review each `SendMessage` before delivery, in auto and in plan under classifier review (2.1.222).
9. Subagents MUST be reviewed three times: the task at spawn; each action under the same order, ignoring frontmatter `permissionMode`; the work and report at finish. A flagged result is still delivered with a security warning; if the classifier is unavailable, the report arrives with a note to verify.
10. Classifier-approved Chrome calls skip the extension's per-site check, as bypass does.

### Default policy

11. By default only the working directory and the remotes configured at session start are trusted. Remotes added or repointed mid-session are not.
12. Default blocks cover these families:
    - code download and execution; data exfiltration; credential exposure; printing live secrets; reading host-owned credentials and metadata credentials;
    - production deploys, migrations, shared-infrastructure and IaC destroy or protected-scope applies; DNS, TLS, secret-manager, feature-flag and IAM changes; cluster-wide writes;
    - force push, history rewriting, discarding uncommitted work, amending commits not made this session;
    - merging unreviewed pull requests, self-approval, disabling CI, tests guarding security behaviour, automation-trigger comments;
    - pushes or PRs to external repositories, repointing remotes or endpoints, sensitive content in public or outbound places;
    - irreversible deletion of pre-existing data, including on shared scratch directories by wildcard and via unresolved variables;
    - tunnels and reverse shells, cross-tenant reach, route-around egress (Containment Escape, 2.1.257);
    - flags that disarm safety guards, launching unattended agent loops without isolation;
    - actions by Claude on its own oversight, such as driving its own terminal pane or writing session transcripts.
13. `claude auto-mode defaults` is the authoritative list. This spec MUST NOT be treated as the rule text.
14. Allowed by default: local working-directory operations; declared dependency installs; reading `.env` and sending credentials to their matching API; read-only HTTP; pushing to the working repository's non-deploy branches; deleting jobs Claude created this session; security-related code work; messages within a multi-agent session; data flow to listed trusted destinations; Chrome navigation to trusted or named URLs.

### User statements

15. Boundaries stated in conversation MUST act as block signals until lifted by a later user message. Claude's own judgment MUST NOT lift them. They are re-read per check and can be lost to compaction, so they are not a guarantee.
16. Approvals in conversation clear a block only if they name the action and its dangerous specifics, and cover one action unless granted as standing. `hard_deny` rules are unaffected.
17. Auto mode also nudges Claude to continue without clarifying questions unless a prompt or skill relies on them.

### First read outside working directories

18. While `blockReadsOutsideWorkingDirectories` is off, the first Read, Grep or Glob outside working directories in an interactive session MUST prompt: allow and keep allowing (recorded); block from now on (sets the key `true` in user settings, refuses the read); refuse once; allow once. `-p` and background sessions do not prompt. The prompt says when blocking makes shell commands ask.

### Fallbacks

19. On a block, show a notification and record it under `/permissions`; `r` marks it for retry and exiting sends a retry message.
20. After 3 consecutive or 20 total blocks, auto MUST pause and prompts resume; approving resumes auto. Thresholds are not configurable. The total persists for the session and resets only when it trips. Denials from a separate safety check do not count. `-p` without a prompt tool keeps running and the action is skipped.
21. No verdict from the classifier (a separate safety check refused its request, or unparseable response): deny without notification or record, shown as a dim `Not run` row.
22. No server verdict: deny rather than run unreviewed; stop the turn after ten consecutive responses without a verdict.
23. A mode switch during a pending check MUST discard a verdict the new mode would not have requested, then prompt, or deny in `dontAsk`.
24. A stalled check MUST turn the spinner red.
25. Conversations too long for review MUST be compacted rather than failing every call (client 2.1.288, server 2.1.302).
26. Denial messages SHOULD name the command and rule, say Claude may retry and auto mode checks again, and point to `/permissions`.

### Server-side review and classifier model

27. Sessions SHOULD ask the server to review actions within their model requests when on a direct API connection, a cloud provider, an LLM gateway, a signed-in Claude apps gateway, or an Anthropic-hosted cloud session, subject to rollout. Server verdicts then decide.
28. If the server does not review a session, the client MUST fall back to its own classifier requests. `/status` row `Auto mode server` reads `Enabled` or `Disabled`.
29. Client classifier model defaults to Sonnet 5, validated on first request and pinned for the session. Overrides: an Anthropic-configured model; Sonnet 4.6 for sessions on it; `ANTHROPIC_DEFAULT_SONNET_MODEL` (Sonnet 5.5 and Opus 5.5 values are replaced by Sonnet 5); else a fallback to the session model, or Opus in a Fable session.
30. `CLAUDE_CODE_AUTO_MODE_MODEL` sets the client classifier model; it is ignored for Opus 5, Sonnet 5.5, Opus 5.5 or policy-excluded models, and does not affect server review. An unservable model makes checks fail, denying each checked action.

### Billing

31. Server-side checks MUST NOT be charged. Client classifier requests count as token usage on Enterprise, API, Claude Platform on AWS, Bedrock, Agent Platform and Foundry; Pro, Max and Team plans never see the billing notice.
32. When fallback holds on a billed account, the client MUST show a notice, naming the gateway if identifiable, and hold the first checked action until answered. Enter continues with billed requests for the session; a named-gateway acknowledgment suppresses the notice on that machine for 24 hours. Esc or Ctrl+C cancels the action and stops the turn, still in auto, remembering nothing.
33. Where the notice cannot wait, it goes to stderr in `-p` and a `system` warning in `stream-json`. VS Code and JetBrains show a Continue/Stop prompt.
34. Reads and working-directory edits skip the classifier. Sandboxed network access adds no per-connection classifier call: hosts are judged with the command.

### Configuration

35. `autoMode` MUST be read only from user settings, managed settings, and `--settings` or SDK inline settings. It MUST NOT be read from project or local files. Entries combine; a developer can extend but not remove managed entries. Because `allow` is an exception to `soft_deny`, a developer `allow` can override an organization `soft_deny`, so hard policy belongs in managed `permissions.deny`.
36. `environment`, `allow`, `soft_deny`, `hard_deny` are arrays of prose. `"$defaults"` splices built-ins at its position; omitting it replaces that section only.
37. Precedence inside the classifier: `hard_deny` blocks unconditionally; `soft_deny` blocks next; `allow` overrides matching `soft_deny`; explicit user intent that specifically describes the action overrides remaining soft blocks.
38. Environment entries come in three kinds: context slots (organization, use, clouds, visibility, snippet hosting, CLIs, secrets, CI/CD, network posture, host containment, protected namespaces, retention); trust slots (trusted repo, source control, domains, buckets, services, internal registry); sensitivity slots (sensitive data and audiences, sensitive remote targets, protected IaC scopes), which default to broad heuristics until named.
39. Invalid managed `soft_deny` or `hard_deny` MUST withhold managed `allow` and `environment`.

### `/auto-mode-setup`

40. Drafts environment entries, sometimes rule entries, and on acceptance writes to user settings. It asks how the project is used and offers two optional scans (first word of shell history; remote hosts of repos under home). It always reads project docs and remotes, `autoMode` and `permissions.allow`, and hosts, buckets and command names from recent sessions, never messages.
41. The draft is accepted or discarded whole. After saving it offers to remove `permissions.allow` rules auto mode ignores or that approve destructive commands. Offered by a dialog after repeated blocks with no environment entries. `skillOverrides: {"auto-mode-setup": "off"}` removes it. Not available in cloud sessions.

## Configuration & interfaces

| Interface | Purpose |
|---|---|
| `autoMode.environment`, `.allow`, `.soft_deny`, `.hard_deny`, `.classifyAllShell` | Classifier config |
| `permissions.disableAutoMode`, `disableAutoMode` | Remove auto |
| `useAutoModeDuringPlan` | Classifier during plan |
| `skipAutoPermissionPrompt` | Skip opt-in notice |
| `claude auto-mode defaults [--label]`, `config`, `critique`, `reset [--yes]` | Inspect, review, reset user config |
| `/permissions` Auto mode tab | View and edit; managed and `--settings` entries read-only; saves to user settings (2.1.246) |
| `CLAUDE_CODE_AUTO_MODE_SERVER` | `0` opts out of server review, `1` opts in on direct connections; temporary |
| `CLAUDE_CODE_AUTO_MODE_MODEL` | Client classifier model |
| `CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS` | Also stops server review when the above is unset |
| `PermissionDenied` hook | Receives denied `tool_input`; can request retry |
| `--debug-file` | Log lines such as `classifier_request_started` |
| OTel `tool_decision` | `classifier_verdict`, `permission_mode` (2.1.301), `classifier_category` (2.1.301) |

## Failure modes & edge cases

- Rejections are sticky: a session told auto is off or rejected stays off until it ends.
- A gateway that strips fields causes billed fallback; one that truncates or rewrites results causes no-verdict denials.
- A resumed session can reuse the classifier prompt cache (2.1.281).
- Cowork cloud: a hook's allow of an MCP call counts as no answer (2.1.314); `PermissionRequest` hooks cannot approve shell commands or subagents (2.1.299).
- Reading an artifact that isn't yours always asks, even in auto (2.1.257).
- `autoMode` in local settings stopped being read at 2.1.207.

## Changes since the snapshot

- 2.1.89: denial notifications and `/permissions` retry; `PermissionDenied` hook. 2.1.111: `--enable-auto-mode` removed.
- 2.1.118: "Don't ask again" on opt-in. 2.1.136: `hard_deny`. 2.1.141: dialog explains `ask` rule cause. 2.1.143: Shift+Tab in attached agent sessions.
- 2.1.166: relayed messages carry no user authority. 2.1.183: destructive git and IaC defaults. 2.1.193: denial reasons, `classifyAllShell`.
- 2.1.205: transcript tamper rule; variable `rm -rf` handling. 2.1.207: local `autoMode` ignored. 2.1.210: Sonnet 5 default.
- 2.1.218: dangerous-`rm` and other checks adjudicated by classifier, not dialogs. 2.1.221, 2.1.281, 2.1.304: cost and session-size work.
- 2.1.236: `Monitor` allow rules suspended; `classifierContext`. 2.1.246: Auto mode tab. 2.1.247: prompt switch option.
- 2.1.257: Containment Escape; first out-of-directory read prompt. 2.1.261: URL-embedded content counts as upload. 2.1.268: denials name rules.
- 2.1.271: per-command `allowed_domains`. 2.1.273 then 2.1.278: third-party classifier default flips, ending at server default with no classifier charge. 2.1.281: server review also waits on read-only and sandboxed shell. 2.1.282: telemetry-off default to server.
- 2.1.281 then 2.1.293: outcome-scoped denial wording added then reverted.
- 2.1.302: `CLAUDE_CODE_AUTO_MODE_MODEL`. 2.1.304: `/auto-mode-setup` on third-party providers. 2.1.312: `claude_code.safety_event` no longer sent. 2.1.314: blocked-call messaging.

## Open questions

- The doc's 2.1.257 rule family "Containment Escape" and the blanket classifier block list change frequently; only `claude auto-mode defaults` is current for a given build.
- Whether `/permissions` retains "Recently denied" naming or "Recently blocked" (changelog 2.1.314).
- Server-side rollout coverage per region and credential is not published.
- `CLAUDE_CODE_AUTO_MODE_SERVER` is described as temporary with no removal plan.
