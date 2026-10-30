# Team memory sync

**Status:** gated/unreleased
**Provenance:** snapshot
**Sources:** snapshot `services/teamMemorySync/`, `memdir/teamMemPaths.ts`, `memdir/teamMemPrompts.ts`, `utils/claudemd.ts`; changelog v2.1.172; docs `memory` (states auto memory is machine-local)

## Purpose

Share memory among authenticated organisation members working in the same repository. The snapshot implements this as a subdirectory of auto memory, synced with a server. No public documentation describes the feature, and the docs state that auto memory is not shared across machines.

This spec is feature-level. Server endpoints and transport details are non-public and excluded.

## Behaviour

All requirements describe the 2026-03-31 snapshot.

### Enablement

1. The feature MUST require the `TEAMMEM` build flag, a remote gate, and enabled auto memory. Disabling auto memory disables team memory everywhere: prompt injection, the watcher and file detection.
2. Sync requires first-party OAuth and a repository identity derived from the git remote. Without either, sync does nothing and local files stay as they are.

### Storage

3. Team memory lives at `<auto-memory-dir>/team/`, with its own `MEMORY.md` entrypoint, loaded as a separate memory type (`TeamMem`).
4. Path checks MUST defend against traversal and symlink escape before writing, since writes come from server content and from the model.
5. `claudeMdExcludes` MUST NOT exclude team memory.

### Sync semantics

6. Scope is per repository, shared across authenticated organisation members.
7. Pull overwrites local files with server content, so the server wins per key.
8. Push uploads only keys whose content hash differs from the server's checksums. Keys absent from an upload are preserved on the server (upsert).
9. Deletions MUST NOT propagate: deleting a local file leaves it on the server, and the next pull restores it.
10. Conflict handling uses ETag-style concurrency with bounded retries (2 conflict retries, 3 general retries).
11. Oversized entries (over 250,000 bytes) MUST be filtered client-side. Upload bodies are split into sequential batches of at most 200,000 bytes; upsert semantics make the split safe.
12. The entry-count cap is server-controlled. The client learns it from a structured error and truncates only after that.
13. Requests time out after 30 seconds.

### Watcher

14. At startup, the client MUST perform an initial pull, then begin watching the team directory, so first-time writes to a fresh repository are noticed.
15. Pushes MUST be debounced by 2 seconds after the last change.
16. The watcher MUST suppress repeat failures, so a permanently failing push does not retry on each change.

### Secret protection

17. Before upload, the client MUST scan content with a local secret scanner and skip any file containing a detected secret.
18. FileWrite and FileEdit validation MUST refuse writes of detected secrets into team memory paths, because the content reaches all collaborators.
19. The scanner's rules are not reproduced here.

### Prompting

20. When enabled, Claude receives combined guidance distinguishing private from team memory and steering what belongs in each. The text is not reproduced.

## Configuration & interfaces

| Interface | Effect |
|---|---|
| `TEAMMEM` build flag | Compiles the feature in |
| Remote gate | Runtime enablement, internal |
| `autoMemoryEnabled`, `CLAUDE_CODE_DISABLE_AUTO_MEMORY` | Turning auto memory off disables team memory |

No public setting, flag, environment variable or command exists.

## Failure modes & edge cases

- A 404 from the service means no team data exists yet, which is not an error.
- A locally deleted note reappears after the next pull (requirement 9).
- Local edits made while offline can be overwritten by a pull, since the server wins per key.
- A file with a detected secret stays local and is omitted from upload.

## Changes since the snapshot

- v2.1.172: a fix for memory recall not finding mounted team memory stores (`CLAUDE_MEMORY_STORES`) in remote sessions. This is the only post-leak public trace found. It shows a related mount-based concept in remote sessions, not that the file sync shipped.
- v2.1.268, v2.1.296: Claude Tag keeps workspace and per-channel memory, administered from an Activity page. This is a separate product surface; whether it shares this sync code is unknown.

## Open questions

- Whether file-based team sync shipped, was replaced by mounted memory stores, or remains internal.
- The meaning, format and enablement of `CLAUDE_MEMORY_STORES`, which is absent from the environment variable reference.
- Whether Claude Tag memory reuses this mechanism.
