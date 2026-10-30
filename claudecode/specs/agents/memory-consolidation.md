# Memory Consolidation (autoDream)

**Status:** gated/unreleased
**Provenance:** snapshot
**Sources:** snapshot `services/autoDream/*`, `tasks/DreamTask/DreamTask.ts`, `query/stopHooks.ts`, `utils/settings/types.ts`, `skills/bundled/index.ts`; no public doc or changelog entry mentions it

## Purpose

In the snapshot, autoDream was a background agent that periodically reviewed recent session transcripts and reorganised the auto memory directory. It ran with no user action once its gates opened. It is covered at feature level because nothing public describes it. The adjacent per-turn memory extraction and auto memory belong to the memory area.

## Behaviour

All rules below are snapshot evidence and MUST NOT be read as current behaviour.

### Triggering

1. It was invoked from the stop-hook stage after a turn, alongside memory extraction, and did nothing until initialised at startup.
2. Master gate: closed in assistant (KAIROS) mode, which used a separate disk-skill dream; closed in remote mode; closed if auto memory was off; otherwise open per the enabled setting.
3. Enablement: an explicit `autoDreamEnabled` user setting won, else a remote feature flag. Default off without the flag.
4. Gates ran cheapest first: time, then scan throttle, then session count, then lock.
5. Time gate: hours since the last consolidation at least `minHours` (default 24).
6. Scan throttle: at most one session scan per 10 minutes, since a passing time gate alone does not advance state.
7. Session gate: at least `minSessions` (default 5) transcripts touched since the last consolidation, excluding the current session. It counted per-working-directory transcripts by modification time. Undercounting worktree sessions was accepted, since this is only a skip gate.
8. Thresholds came from remote configuration with per-field validation: finite and positive, else default.

### Lock

9. `.consolidate-lock` in the memory directory doubled as state: its modification time was the last consolidation time, and its body the holder's PID. Absence meant time zero.
10. Acquisition failed if the lock was younger than one hour and held by a live PID. Older locks were stale even with a live PID, guarding against PID reuse. Dead or unparseable holders were reclaimed.
11. After writing its PID, the process re-read the file and backed off if another writer had won.
12. On agent failure or user kill, the modification time rolled back to its prior value and the PID cleared, so the time gate would pass again, with the scan throttle acting as backoff. With no prior file, the lock was deleted.
13. A crash left the time advanced with a dead PID, delaying the next run until `minHours`.
14. A manual `/dream` stamped the lock optimistically when building its prompt.

### Execution

15. The agent ran as a forked agent sharing cache-safe parameters with the parent, with no main-transcript recording.
16. Tool permissions reused the memory-extraction policy scoped to the memory directory. Bash was limited to read-only commands, and the agent was told so in advance.
17. The prompt gave the memory directory, transcript directory and session list. In substance it had four stages: orient on existing memory, gather recent signal with narrow transcript searches, merge into durable topic files, and prune and reindex the entrypoint.

### Surfacing

18. A `dream` background task showed in the footer pill and tasks dialog, labelled dreaming, with phase `starting` until the first Edit or Write, then `updating`.
19. It kept the 30 most recent turns as text plus a tool count, and the paths of Edit and Write calls. That list was explicitly incomplete, missing shell-mediated writes.
20. On completion with touched files, an inline message used the memory-saved format with the verb `Improved`.
21. Killing the task aborted the agent and rolled back the lock. The failure path avoided a double rollback.

## Configuration & interfaces

| Item | Detail |
| --- | --- |
| `autoDreamEnabled` | Boolean setting in the snapshot schema |
| `minHours`, `minSessions` | Remote defaults 24 and 5 |
| `<memdir>/.consolidate-lock` | State and lock |
| `/dream` | Gated manual skill; its module is behind a build flag and absent from public commands |

## Failure modes & edge cases

- An unreadable lock or session list skipped the run for that turn.
- Rollback failure delayed the next run to `minHours`.
- The session gate undercounted worktree sessions by design.

## Changes since the snapshot

None found. `autoDreamEnabled` and `/dream` are absent from the current settings reference, commands reference, memory docs and changelog. Related public changes: 2.1.285 stopped Auto-memory being turned on from a background session.

## Open questions

- Whether autoDream ships, is flag-limited, or was removed in 2.1.314. The allowed sources cannot show this.
- Whether a similar pass exists under another name. No public text describes one.
- Whether the `Improved` memory message still occurs.
