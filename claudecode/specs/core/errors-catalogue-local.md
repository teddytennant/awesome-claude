# Errors catalogue: local, tool, session and configuration

**Status:** shipped
**Provenance:** both
**Sources:** docs errors (command-line, plugin, tool, background, wrapper, rewind, session saving, configuration); changelog 2.1.101, 2.1.210, 2.1.246, 2.1.287

## Purpose

Catalogues failures that originate on the client rather than the model API, so an implementer knows which conditions need a dedicated message and whether each is fatal, a refusal or a warning. API-side errors are in [errors-catalogue-api.md](errors-catalogue-api.md).

## Behaviour

### General rules

1. CLI argument and startup failures MUST exit with code 1 before any model request.
2. Tool failures MUST be returned to the model as tool results. The turn continues. They are not user-facing errors unless shown in the transcript.
3. Warnings MUST state a concrete fix. Each warning is shown once where repetition would be noise (permission-rule warnings once per user until the rule changes, 2.1.311).
4. Where a warning goes depends on surface: plain-text `-p` uses stderr; interactive, background and JSON modes use the debug log or a notice. `--debug` writes `~/.claude/debug/<session-id>.txt`.
5. Refusals in a path-safety area MUST fail closed: an unverifiable path is not touched.

### Command-line (fatal unless stated)

| Area | Entries |
| - | - |
| Flag conflicts | `--bg` with `--print`; `--bg` ambiguous as flag or text; subagent system prompt with its file form |
| Invalid values | `--agents`; `--json-schema`; `--settings` over 2MiB; `--permission-prompt-tool` not found |
| Environment | Current directory gone; temp directory refused or uncreatable; `/add-dir` unresolvable |
| Input | `Input must be provided when using --print`; keyboard unreadable; whitespace-only input; stream-json over 268,435,456 characters without a newline |
| Trust | Workspace untrusted for Remote Control, `ultrareview` or background dispatch |
| Remote Control | Flags not carried to spawned sessions; `--sandbox` unsupported |
| Cloud | Refused from `--restricted`; `allow_remote_sessions` off; policy unverifiable; denial naming a credential; login form |
| Commands | `Unknown command`; `/security-review` needs `origin/HEAD`; dynamic context command refused; `/recap` must be user-initiated; custom output style refused over Remote Control |
| Code review | Diff too large; no merge-base; no branches; GitHub not connected or can't see the repo; organization policy; SSO needed |
| Resume | Failed to resume; no conversation for that ID; Windows EBADF |
| Restart | Cannot switch renderers; can't restart while work runs; couldn't restart |
| MCP config | Managed scope; plugin-only customization; `.mcp.json` unreadable; change unverified; hosted connector has no local OAuth; `headersHelper` rejected; elicitation capability rejected by old SDKs; OAuth port conflict |
| Import | Flow turned off; `~/.claude.json` unparsable |

### Plugins

Marketplace name and source checks (reserved names, untrusted source, spoofed spelling, duplicate source), archive integrity failure, shell use of `${user_config.KEY}`, paths escaping the plugin or marketplace, manifest not read, path check errors, unloadable marketplace registry, required plugin can't be disabled, uninstall stopped, `plugin eval` early access, and a cached MCP stdio failure with a 15-minute retry.

6. Component-level path failures MUST drop only that path; manifest failures drop the whole plugin.

### Tools (returned to the model)

| Tool area | Conditions |
| - | - |
| Lookup | `No such tool available`; explanation when known (2.1.101) |
| MCP | Connection closed before answer, so the outcome is unknown; server disabled; elicitation timed out |
| Agents | Zero usable tools; `subagent_type` required |
| Files | Read deny rule covers Edit or Write; null bytes in path; image over 128 MB; not valid UTF-8 (nothing written); memory index over 200 lines or 25KB (write succeeded) |
| Shell | PowerShell invisible characters; `pkill` pattern matching Claude Code; disk full or quota lines; Apple git stub |
| Teams and messaging | Inbox write failure; definition not restored; shutdown approval from a non-teammate; deny rule can't transfer; cross-session size, rate, drop and identity refusals |
| Safety | Refusing to read, write or search a path; task output swap refused; `WebFetch cannot fetch localhost`; domain safety check failed |
| Artifacts | Source not UTF-8; network share; repeated rejected publish; Cowork folder limit |

7. WebFetch MUST refuse hostnames without a dot. It MUST treat a failed domain safety check as a failure, unless configured otherwise, and tell the model not to retry in a loop (2.1.286).
8. An MCP call whose connection died MUST report the outcome as unknown rather than failed.

### Background sessions

Commands refused without a terminal; write or command blocked by worktree isolation (unresolvable path, network location, command checks); no saved transcript; running in another terminal; transcript deleted; worktree has unpushed commits (kept); terminal host died; not responding after about 10 seconds; stopped during respawn; agent no longer available; missed `/loop` wakeup; shell-only gateway variable not passed on; `CLAUDE_CODE_PROCESS_WRAPPER` errors; `EUNKNOWN`; `EACCES`; service exited; directory gone; untrusted workspace.

### Wrappers

Printed by the launcher, not Claude Code: `Claude Code process exited with code N` (real cause is in the process output), `Could not locate the Claude CLI on PATH`, missing bundled binary, and a connection ended before completion.

### Rewind and saving

Restore skipped files, no files restored, transcript writes failing (names the cause), and saving off through `CLAUDE_CODE_SKIP_PROMPT_HISTORY` or an inherited `CLAUDE_CODE_CHILD_SESSION`.

### Configuration warnings

| Group | Entries |
| - | - |
| Trust | `Workspace has not been trusted`; network working directory; `headersHelper not run` |
| Instructions | Agent descriptions over 15.0k tokens; instruction file not loaded; reserved skill or command names; hook needs quotes |
| Managed settings | Failed to load; not approved (exit); need approval; block the default model (exit); disallowed provider; MCP blocked; unparsable (exit 1); unreadable; invalid hook entries |
| Permissions | Malformed rule; matches no tool; not matched by file checks; wildcard before the subcommand (2.1.246); denying Bash disables PowerShell (2.1.287); `Write(path)`-style rules (2.1.210) |
| Other | `crossSessionInbound` value; Foundry resource name; `otelHeadersHelper`; 200K not enforced; unrecognized model; sandbox entries ignored under a managed lock; sandbox mask files; unrecoverable interface error |

9. Managed settings problems that could silently weaken policy MUST be fatal or visible, never ignored. In `-p`, invalid managed hooks print a stderr block naming hooks that are NOT loaded.

## Configuration & interfaces

`--debug [filter]`, `--debug-file`. `claude doctor` and `/doctor`, `/status` for diagnostics (2.1.248, 2.1.261). `/feedback` for reporting.

## Failure modes & edge cases

- Some wording varies by surface. A cloud variant is not implied by the local one.
- Docs list old wordings in the lookup table so old-version users can find them.

## Changes since the snapshot

- This catalogue is largely new in docs; individual entries cite their versions in sibling specs.
- 2.1.210, 2.1.246, 2.1.287: permission-rule warnings added.
- 2.1.311: permission-rule warnings shown once per user.

## Open questions

- Which of these conditions exist with the same wording in cloud and Desktop surfaces. Docs state errors apply across them, with exceptions.
- Exit codes other than 1 and 143 are not catalogued in the sources.
