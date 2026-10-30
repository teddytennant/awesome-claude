# Checkpoints and /rewind

**Status:** shipped
**Provenance:** both
**Sources:** docs `checkpointing`, `claude-directory`, `errors`, `settings-reference`, `tools-reference`; snapshot `utils/fileHistory.ts`, `commands/rewind/`, `components/MessageSelector.tsx`; changelog versions cited below

## Purpose

Let the user undo Claude's file edits and conversation turns within a session, or compress part of the conversation, without using version control.

## Behaviour

### Capture

1. Every prompt that starts a turn MUST create a checkpoint recording tracked file state before the turn.
2. A file becomes tracked when Claude first edits it with its file-editing tools. Backups MUST be taken before the edit.
3. Backups live in `~/.claude/file-history/<session>/`; a `file-history-snapshot` transcript entry links them to a message, so rewind works after resume.
4. The client MUST keep snapshots for the 100 most recent checkpoints. Evicting a checkpoint MUST delete backups no remaining checkpoint references, except each file's first snapshot, which VS Code uses as its diff baseline.
5. Backups are removed by the retention sweep about 30 days after the session last saved one, governed by `cleanupPeriodDays`.
6. Once a file is tracked, later changes to it from any source, including Bash, are captured and counted. A file that only Bash changed is not tracked.
7. `sed -i` is an ordinary Bash edit and is not restored (since v2.1.309).
8. Subagent edits are generally not captured. A foreground forked skill (`context: fork`, `background: false`) edits within the user's turn, so its edits are restored. Other subagents, including background forks and background `/code-review --fix`, leave edits to untracked files in place.
9. External and concurrent-session edits are not captured unless they touch a tracked file.
10. A message typed during a turn has no checkpoint and MUST be marked **No code restore**.

### Menu

11. `/rewind` (aliases `/checkpoint`, `/undo`), or `Esc` twice on an empty prompt, MUST open the menu listing prompts sent in the session, including prompts sent while Claude was working. With text in the input, double `Esc` clears it and saves it to history.
12. After selecting a prompt, the actions are: **Restore code and conversation**, **Restore conversation**, **Restore code**, **Summarize from here**, **Summarize up to here**, **Never mind**.
13. Code options MUST appear only when the checkpoint has tracked changes to revert. Each prompt lists change counts for tracked files, whatever made the change.
14. Summarize options MUST be hidden when `DISABLE_COMPACT` is set.
15. Typed from a background agent or teammate transcript view, a dialog MUST name the target first.

### Restore

16. Restoring code MUST return tracked files to the checkpoint, deleting those created after it.
17. It MUST NOT restore or delete through a symlink or hard link at a tracked path. Skipped paths keep current content, and a `Restored the code, but skipped N files` warning MUST appear. `/debug` logging names each.
18. It MUST NOT report success when backups are missing and nothing was restored; the error is `No files were restored`.
19. Backups MUST NOT be restored partially filled, including in forked sessions.
20. Restoring conversation MUST truncate to that point, clear read tracking from rewound turns, keep the skill listing, and restore the selected prompt into the input for re-send or editing.
21. Truncation returns to a cached prefix. Restoring files has no cache effect.

### Rewound messages returning

22. Rewound messages can return if the user exits before sending another prompt, since the rewound state is saved with that next prompt. Repeating the restore and sending a prompt persists it. Restored files stay restored. The prompt sent after a rewind MUST NOT be lost, even if the session is backgrounded or killed.

### Summarize

23. **Summarize from here** compresses from the selected message forward and restores its prompt to the input. **Summarize up to here** compresses earlier messages, keeps later ones, and leaves the input empty at the end of the conversation.
24. Guidance: highlighting an option and typing into **add context (optional)**, then `Enter`. A number key summarises immediately. Both keep the same session, change no files, keep originals in the transcript, and show a **Summarized conversation** marker.

### Past `/clear`

25. After `/clear` in the same process, the menu MUST show a top entry `/resume <session-id> (previous session)` until exit or another resume.

## Configuration & interfaces

| Interface | Effect |
|---|---|
| `fileCheckpointingEnabled` | Default `true`; `/config` **Rewind code (checkpoints)**; ignored in `-p`/SDK |
| `CLAUDE_CODE_DISABLE_FILE_CHECKPOINTING` | Off; neither it nor the setting can re-enable the other |
| `CLAUDE_CODE_ENABLE_SDK_FILE_CHECKPOINTING=true` | Enables in bare `-p`; SDK uses `enableFileCheckpointing` |
| `claude -p --resume <id> --rewind-files <checkpoint-uuid>` | Non-interactive restore; accepted but absent from `--help`; needs checkpointing enabled |
| `cleanupPeriodDays` | Backup retention |
| `select:*` keybindings | List movement; `messageSelector:*` still works |

## Failure modes & edge cases

- Files hard-linked by pnpm, or symlinked by dotfile managers, are never restored.
- After retention expires, rewind fails with `No files were restored`.
- Resuming preserves checkpoints, but scheduled tasks stopped before a rewind MUST NOT return.
- Checkpoints are not version control.

## Changes since the snapshot

- v2.1.108: `/undo` alias.
- v2.1.141: **Summarize up to here**.
- v2.1.191: rewind past `/clear`.
- v2.1.208: superseded backups pruned, transcripts smaller.
- v2.1.216: symlinks and hard links skipped with a warning.
- v2.1.260: missing backups reported; read tracking cleared.
- v2.1.275: forked-session restore corruption fixed.
- v2.1.283: list keybindings unified.
- v2.1.290: prompts sent mid-turn listed.
- v2.1.295: post-rewind prompt preserved across kill.
- v2.1.301: skill listing kept after rewind.
- v2.1.309: change counts reflect subagent, `--fix` and shell changes; `sed -i` no longer restored.
- v2.1.311: copy fixes; summarise options hidden under `DISABLE_COMPACT`.

## Open questions

- Whether a hash or a copy deduplicates backups in the current implementation.
