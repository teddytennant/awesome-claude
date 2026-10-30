# Slash commands: snapshot-only names and their fate

**Status:** removed (mixed: many rows are live aliases or internal; see table)
**Provenance:** snapshot
**Sources:** `comparison/commands.md`; snapshot `commands.ts`, `commands/`, `skills/bundled/`; docs `commands`, `plugins__cli-reference`, `skills`; changelog versions inline

## Purpose

Classify the 62 names that `comparison/commands.md` marks as present in the snapshot and absent from current docs. The comparison matched on names, so many are aliases, directory names or false positives rather than real losses.

## Behaviour

Outcome summary:

| Outcome | Count |
|---|---|
| Still live as a documented alias | 15 |
| Alias of an undocumented command | 1 |
| Renamed, or directory name of a live command | 6 |
| False positive (not a command) | 8 |
| Internal-only or stub in the snapshot, not public now | 22 |
| Removed publicly | 1 |
| Gated, no public trace | 3 |
| Undocumented, status uncertain | 6 |

A spec implementer needs only rows marked **alias** or **renamed** to be compatible. Internal rows are listed for completeness.

| Name | Snapshot role | Fate |
|---|---|---|
| `/allowed-tools` | Alias of `/permissions` | alias, documented |
| `/android` | Alias of `/mobile` | alias, documented |
| `/app` | Alias of `/desktop` | alias, documented |
| `/bashes` | Alias of `/tasks` | alias, documented |
| `/checkpoint` | Alias of `/rewind` | alias, documented |
| `/continue` | Alias of `/resume` | alias, documented |
| `/ios` | Alias of `/mobile` | alias, documented |
| `/marketplace` | Alias of `/plugin` | alias, documented in plugin reference |
| `/new` | Alias of `/clear` | alias, documented |
| `/plugins` | Alias of `/plugin` | alias, documented in plugin reference |
| `/quit` | Alias of `/exit` | alias, documented |
| `/rc` | Alias of `/remote-control` | alias, documented |
| `/reset` | Alias of `/clear` | alias, documented |
| `/settings` | Alias of `/config` | alias, documented |
| `/share` | Internal stub | alias of `/bug`, documented; `/bug` and `/share` separated from `/feedback` in 2.1.212 per docs |
| `/remote` | Alias of `/session` | alias of an undocumented command; see `/session` |
| `/bridge` | Directory of `/remote-control` | renamed (directory name) |
| `/pr_comments` | Directory of `/pr-comments` | renamed (directory name); command removed 2.1.91 |
| `/remote-setup` | Directory of `/web-setup` | renamed (directory name) |
| `/sandbox-toggle` | Directory of `/sandbox` | renamed (directory name) |
| `/terminalSetup` | Directory of `/terminal-setup` | renamed (directory name) |
| `/extra-usage` | Billing dialog | renamed to `/usage-credits` in 2.1.144; old name still works |
| `/checking` | Step name in `remote-setup` and `install` state | false positive |
| `/confirm` | Step name in `remote-setup` | false positive |
| `/uploading` | Step name in `remote-setup` | false positive |
| `/node` | Environment entry in `remote-setup/api.ts` | false positive |
| `/python` | Environment entry in `remote-setup/api.ts` | false positive |
| `/suggestions` | Section name in `insights.ts` | false positive |
| `/createMovedToPluginCommand` | Helper function file | false positive |
| `/install` | Ink view for the `claude install` subcommand, not registered as a slash command | false positive for slash use; see [cli-subcommands.md](cli-subcommands.md) |
| `/ant-trace` | Internal, stubbed | not public |
| `/backfill-sessions` | Internal, stubbed | not public |
| `/break-cache` | Internal, stubbed | not public |
| `/bridge-kick` | Internal test command | not public |
| `/bughunter` | Internal, stubbed | not public |
| `/commit` | Internal prompt | not in commands docs. Docs use `/commit` only as an example of a user or plugin skill |
| `/ctx_viz` | Internal, stubbed | not public |
| `/debug-tool-call` | Internal, stubbed | not public |
| `/good-claude` | Internal, stubbed | not public |
| `/init-verifiers` | Internal prompt | not public |
| `/issue` | Internal, stubbed | not public |
| `/lorem-ipsum` | Internal-only bundled skill | not public |
| `/mock-limits` | Internal, stubbed | not public |
| `/oauth-refresh` | Internal, stubbed | not public |
| `/onboarding` | Internal, stubbed | not public |
| `/perf-issue` | Internal, stubbed | not public |
| `/remember` | Internal-only bundled skill | not public |
| `/reset-limits` | Internal, stubbed | not public |
| `/skillify` | Internal-only bundled skill | not public |
| `/stuck` | Internal-only bundled skill | not public |
| `/summary` | Internal, stubbed | not public |
| `/version` | Internal | not public |
| `/tag` | Internal-gated session tag toggle | removed in 2.1.92 |
| `/think-back` | Year-in-review, behind a server gate | no public trace; see [gated-ui-features.md](gated-ui-features.md) |
| `/thinkback` | Directory of `/think-back` | same |
| `/thinkback-play` | Hidden playback command | same |
| `/brief` | Toggle brief-only mode, build and server gated | undocumented. `--brief` and the SendUserMessage tool are public |
| `/commit-push-pr` | Internal prompt | undocumented in commands, but changelog 2.1.206 and 2.1.229 change its behaviour. Treat as live for some users |
| `/env` | Internal, stubbed | undocumented. Changelog 2.1.89 refers to `/env` applying to PowerShell commands |
| `/files` | Enabled only for internal users | undocumented |
| `/keybindings-help` | Bundled skill not user-invocable | undocumented model-facing skill; a session skill list can show it. See below |
| `/session` | Shows remote session URL and QR in remote mode | undocumented; current status unknown |

Counts above cover the 62 names in the comparison.

### Behaviour worth keeping

1. Alias rows MUST resolve exactly as their target.
2. `/extra-usage` MUST keep working.
3. `keybindings-help`: a skill loaded by Claude when a user asks to change shortcuts. Not typed by users. It teaches the model the current chord timeout and modifier rules (a stale 1-second figure was fixed in 2.1.283).
4. Snapshot skills marked internal were guarded by a user-type check, so were not in external builds.
5. Stubbed directories contain only a disabled placeholder in the snapshot, so nothing about them can be specified from that source.

## Configuration & interfaces

None.

## Failure modes & edge cases

- Typing an internal name in a public build yields `Unknown command`.
- `/think-back` needs a server gate, and installs and plays a plugin skill.

## Changes since the snapshot

- 2.1.91: `/pr-comments` removed.
- 2.1.92: `/tag` and `/vim` removed.
- 2.1.144: `/extra-usage` renamed.
- 2.1.206, 2.1.229: `/commit-push-pr` changes.
- 2.1.212: `/bug` and `/share` split as aliases, per docs.

## Open questions

- Whether `/session` and `/remote` still exist in `--cloud` sessions.
- Whether `/brief`, `/files` or `/env` remain typable.
- Who can reach `/commit-push-pr`.
- Whether the thinkback gate has fired since the snapshot.
