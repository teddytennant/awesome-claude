# File Tools: Read, Write, Edit, NotebookEdit

**Status:** shipped
**Provenance:** both
**Sources:** docs `tools-reference` (Read, Write, Edit, NotebookEdit, Large files, Non-UTF-8 files), `agent-sdk/typescript`, `permissions`, `errors`, `env-vars`; snapshot `tools/FileReadTool`, `FileWriteTool`, `FileEditTool`, `NotebookEditTool`; changelog 2.1.89 to 2.1.314

## Purpose

The four tools through which Claude reads and changes local files. They share path permissions, a read-before-write guard, encoding rules and worktree isolation.

## Behaviour

### Common

1. Permission for reads MUST be matched against `Read(path)` rules and for changes against `Edit(path)` rules. `Write(path)`, `NotebookEdit(path)` and `Glob(path)` path rules MUST be accepted but never match; a startup warning names them (2.1.210). Whole-tool bare names still work.
2. `Edit(...)` allow rules MUST also grant read on that path.
3. A `Read(...)` deny MUST also refuse Edit and Write on that path, including creating a new file (Write since v2.1.228). NotebookEdit is not covered by this, so a path no tool may change needs an `Edit` deny.
4. When `permissions.blockWritesOutsideWorkingDirectories` is on, Write, Edit and NotebookEdit MUST refuse paths outside the working directories in every permission mode (2.1.314).
5. In a session isolated in a worktree, Edit, Write and NotebookEdit MUST be blocked on main-checkout paths.
6. With `CLAUDE_CODE_PERFORCE_MODE=1`, Edit, Write and NotebookEdit MUST fail with a `p4 edit <file>` hint when the target lacks the owner-write bit.
7. A path containing a null byte MUST fail that one tool call with a clear error rather than ending the turn (2.1.281).
8. Read, Write and WebFetch SHOULD ignore a few stray input parameters rather than failing the call (2.1.292).

### Read

9. Input is `file_path` plus optional `offset`, `limit`, `pages`, `allow_large`. Output is line-numbered text. Claude is instructed to pass absolute paths.
10. An empty file MUST return a notice that it exists but is empty. An `offset` past the last line MUST return a notice giving the line count.
11. Directories MUST be refused; Claude lists them with a shell command.
12. Files whose extension is treated as binary (for example `.xlsx`, `.parquet`, `.heic`, `.zip`, `.xlsm`, `.epub`) MUST be refused, with an error suggesting a matching skill or a shell command. An `@`-mention of such a file gives Claude the path but not the contents.
13. **Images** (PNG, JPEG, GIF, WebP) are returned as visual content, resized and recompressed to model limits. Sources over 128 MB MUST be refused with advice to make a smaller copy (2.1.302).
14. **PDFs:** short files are read whole. Over 10 pages, reads use `pages` such as `"1-5"`, at most 20 pages per call.
    - Page-range reads need `pdftoppm`; without it the read fails with `pdftoppm is not installed`.
    - A comma list such as `"6,9,15"` MUST error, telling Claude to read each range separately (2.1.292).
    - An empty `pages` value is treated as omitted (2.1.295).
    - Result content is either a summary `text` block plus a `document` block, or a summary plus one block per page (an `image`, or a `text` block naming a page that could not be rendered).
15. **Notebooks** return all cells with outputs. Cells totalling over 256 KB, or over the token limit, MUST error. Files over 100 MB MUST be refused, with guidance on reading a slice with a shell command.
16. **Large text.** Defaults: at most 25,000 tokens per call (`CLAUDE_CODE_FILE_READ_MAX_OUTPUT_TOKENS`), and a whole-file read refused over 256 KB.

| Read | Over limit | Result |
| :- | :- | :- |
| Whole file | Token limit | First page plus `PARTIAL view` notice with how to continue (since 2.1.145; `truncatedByTokenCap` in SDK output) |
| Whole file | 256 KB | Error directing to `offset`/`limit` or a search |
| `offset`/`limit` | Token limit | Error directing to a smaller portion or a search |

17. `allow_large: true` (v2.1.296+) lets one call return a whole text file or long range, sized against the room left in the context window instead of the defaults. Images, PDFs and notebooks keep their limits.
18. Output is a union discriminated on `type`: `text`, `image`, `notebook`, `pdf`, `parts`, `file_unchanged`. `file_unchanged` is a dedup result; its `source: "seeded"` marks a match against startup-seeded content such as CLAUDE.md.

### Edit

19. Input is `file_path`, `old_string`, `new_string`, optional `replace_all`. It is exact string replacement, with no regex or fuzzy matching.
20. Before any other check, a path under a `Read` deny MUST be refused.
21. The edit MUST satisfy:
    - **Read-before-edit:** the file was read in this conversation. A read cut short with `PARTIAL view` does not count. Opus 4.6, Haiku 4.5 and older always require it. Newer models MAY edit an unread file when reading it would not need a prompt and the Read tool is available.
    - **Match:** `old_string` appears exactly as written.
    - **Uniqueness:** exactly one occurrence, unless `replace_all: true`.
22. A file changed on disk since the last read MUST still be editable when `old_string` matches current content unambiguously and the file is readable without a prompt. The result notes the other changes so Claude re-reads before edits depending on context (2.1.208). This replaces the snapshot's flat "file unexpectedly modified" failure in that case. Otherwise Claude re-reads.
23. These single-file Bash views, with no pipes or redirects, satisfy the read check: `cat`, `nl`, `bat`, `batcat`, `head`, `tail`, `sed -n 'X,Yp'`, `grep`, `egrep`, `fgrep`, `rg`. If the command printed none of the file's text the check still applies. Such a view also loads applicable subdirectory CLAUDE.md files and path-scoped rules (2.1.293).
24. A non-match on large non-ASCII edits MUST report string-not-found rather than a regex-size error (2.1.277). An escaped backslash followed by `uXXXX` text MUST NOT be treated as a unicode escape (2.1.277).

### Non-UTF-8 files

25. Edit and NotebookEdit MUST refuse a file that is not valid UTF-8 and leave it untouched, since saving would replace undecodable bytes with `U+FFFD` (2.1.296). The exception: Edit accepts a file starting with a little-endian UTF-16 byte-order mark.
26. The error MUST tell Claude to use a shell command that keeps the encoding, or to ask about converting.
27. Write MAY still replace such a file, saved as UTF-8, unless the new content contains `U+FFFD`, which guards against writing back garbled text Read returned.

### Write

28. Input is `file_path`, `content`. It creates or fully overwrites; it does not append or merge. Claude uses Edit for partial changes.
29. Overwriting an existing file: Opus 4.6, Haiku 4.5 and older require a prior read and otherwise fail. Newer models MAY overwrite an unread file under the Edit conditions (v2.1.228+). Notebooks and files read only as `PARTIAL view` require the read on every model. New files need no read. Bash views count as for Edit.
30. A target that is an existing directory MUST report a clear error rather than ending the turn as a declined permission (2.1.277).
31. Output carries `type` (`create`/`update`), `structuredPatch`, `originalFile` and optional `gitDiff`. `originalFile` is null and the patch empty for a new file, or for previous content over about 10 MB. The patch is also empty when nothing changed or the diff timed out.

### NotebookEdit

32. Input is `notebook_path`, `new_source`, optional `cell_id`, `cell_type`, `edit_mode`. It works one cell at a time by `cell_id`.
33. Modes:
    - `replace` (default): overwrites the cell's source.
    - `insert`: adds after the target, or at the start with no `cell_id`; requires `cell_type` of `code` or `markdown`.
    - `delete`: removes the target.

### Security

The detailed path-safety validation in these tools is out of scope for this spec.

## Configuration & interfaces

| Key | Effect |
| :- | :- |
| `CLAUDE_CODE_FILE_READ_MAX_OUTPUT_TOKENS` | Read token limit |
| `CLAUDE_CODE_PERFORCE_MODE` | Read-only file guard |
| `permissions.blockWritesOutsideWorkingDirectories` | Hard write fence (2.1.314) |
| `permissions.blockReadsOutsideWorkingDirectories` | File tools refuse fenced paths in every mode |
| `fileCheckpointingEnabled` | File snapshots for `/rewind` |

Hook `tool_input` field names match the input schemas above; see `hooks` PreToolUse input.

## Failure modes & edge cases

- `@`-mentioning a refused file gives a path with no contents.
- `Read` on a Bash output path is the normal route for large or background output, so a denied path can hide it.
- Windows AppContainer or restricted-token sandboxes previously made every file refuse with a symlink error (fixed 2.1.265).
- In Cowork cloud sessions, a path on the user's computer previously reported false success (fixed 2.1.300).
- A partial read through `PARTIAL view` lets Claude see the file but does not unlock editing.

## Changes since the snapshot

- 2.1.89: Edit works after viewing a file with `sed -n` or `cat`.
- 2.1.91: Edit uses shorter `old_string` anchors.
- 2.1.92: faster Write diffs on large files.
- 2.1.98: `CLAUDE_CODE_PERFORCE_MODE`.
- 2.1.126: Read's per-file malware reminder removed.
- 2.1.145: Read returns a partial first page instead of a hard error.
- 2.1.160: single-file `grep`-family views satisfy the read check.
- 2.1.208: Edit tolerates unrelated on-disk changes.
- v2.1.228: model-dependent read requirement for Write; `Read` deny blocks Write.
- 2.1.281, 2.1.292, 2.1.295, 2.1.301, 2.1.302: input and format hardening noted above.
- 2.1.296: `allow_large`; non-UTF-8 refusal.
- 2.1.309: `sed -i` no longer gets a simulated file-edit preview; it takes the ordinary Bash prompt and is not restored by `/rewind`.
- 2.1.314: `permissions.blockWritesOutsideWorkingDirectories`.

## Open questions

- The list of "a few stray parameters" tolerated since 2.1.292.
- The complete binary extension list.
- The exact model boundary for "newer" beyond the named older models.
- Conditions that produce `file_unchanged` beyond dedup against earlier reads.
