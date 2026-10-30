# Worktree Tools and Isolation

**Status:** shipped
**Provenance:** both
**Sources:** docs `worktrees`, `tools-reference`, `agent-sdk/typescript`, `settings-reference`, `errors`, `agent-view`, `sub-agents`; snapshot `tools/EnterWorktreeTool`, `tools/ExitWorktreeTool`; changelog 2.1.105, 2.1.128, 2.1.133, 2.1.143, 2.1.157, 2.1.206, 2.1.212, 2.1.309

## Purpose

Isolate a session's file edits in a git worktree. `EnterWorktree` and `ExitWorktree` are the mid-session interface; `--worktree` and subagent `isolation: worktree` share the same machinery. The session is then held inside the worktree by enforcement checks.

## Behaviour

### EnterWorktree

1. Input: `name` or `path`, mutually exclusive, both optional. Output: `worktreePath`, optional `worktreeBranch`, `message`.
2. With no `path` it MUST create a worktree under `.claude/worktrees/<name>/` on branch `worktree-<name>`, generating a name such as `bright-running-fox` if none is given.
3. With `path` it switches into an existing worktree. On first entry the target must be a worktree of the current repository or, in a multi-repo workspace, of a nested repository (v2.1.203+).
4. From inside a worktree session, or from a subagent with a pinned working directory, only the `path` form is available and the target MUST be under `.claude/worktrees/` of the session's repository. The previous worktree stays on disk (2.1.157).
5. New-worktree creation and paths under `.claude/worktrees/` MUST NOT prompt. A path outside it MUST prompt, since it moves the working directory, write access and project configuration (v2.1.206). An `EnterWorktree` rule or "don't ask again" does not suppress this; only `bypassPermissions` skips it.
6. The tool table marks it permission-required, but that applies only to the outside-path case above.
7. After entry, `${CLAUDE_PROJECT_DIR}` in hooks stays at the original root, while hook input `cwd` follows Claude. A transcript follows a git worktree the way `/cd` does; a `WorktreeCreate`-hook worktree keeps its transcript at the launch directory.

### ExitWorktree

8. Input: `action` of `keep` or `remove`, optional `discard_changes`. Output: `action`, `originalCwd`, `worktreePath`, optional `worktreeBranch`, `tmuxSessionName`, `discardedFiles`, `discardedCommits`, `message`.
9. It returns the session to the original directory. `keep` leaves worktree and branch on disk. `remove` deletes both.
10. `remove` MUST refuse without `discard_changes: true` when the worktree has uncommitted files or unmerged commits. In the snapshot it also refused when state could not be verified.
11. Not available to subagents already in their own directory.
12. After a `--continue` or `--resume` in print or SDK mode the session is back in the worktree, so `ExitWorktree` works (v2.1.212+).

### Creation

13. New worktrees branch from the remote default branch by default (`worktree.baseRef: "fresh"`). `"head"` branches from the current local `HEAD`, or that worktree's `HEAD` when inside a linked worktree. A branch name is not accepted.
14. For `"fresh"`: if not fetched in 24 hours, fetch the default branch, capped at five seconds, never waiting for terminal input. On failure use the cached ref. With no remote or uncached `origin/HEAD`, fall back to local `HEAD`.
15. Gitignored files matching `.worktreeinclude` (gitignore syntax) MUST be copied into each git-created worktree. Tracked files are never duplicated.
16. Repository-defined git filter drivers MUST be skipped, so `git lfs install --local` repositories get pointer files; `git lfs pull` fixes that. Creation fails outright if drivers cannot be determined or a setting cannot be neutralised (v2.1.247+).
17. Replaced objects are ignored through `GIT_NO_REPLACE_OBJECTS=1`.
18. Symlinks at `.claude`, `.claude/worktrees` or the target MUST refuse creation (v2.1.212+).
19. Git no longer fetches objects on demand during creation or reuse (2.1.309). Partial clones fetch first and fail with `This repository is a partial clone` if they cannot.
20. Reusing a name opens the existing worktree. With `"fresh"`, it resets to the default branch only when it is clean, on its own branch, and has no commits of its own or its PR was merged and remote branch deleted. Otherwise it reopens at its old tip.
21. `--worktree` also accepts `#<n>`, GitHub PR URLs and GitLab MR URLs (v2.1.233+), creating `.claude/worktrees/pr-<number>`.

### Identity checks

22. Before adopting any directory as an isolated checkout, Claude Code MUST verify its git identity, and refuse with `Refusing to use <path> as an isolation worktree` if metadata resolves into the main checkout or cannot be read. The directory is left in place.
23. A directory with no git metadata passes only when no repository contains it. Network-spelled paths are never resumed into.

### Enforcement

24. While isolated, four checks apply equally to `--worktree`, `EnterWorktree`, resumed sessions and their subagents, in interactive and background runs:
    - **File edits:** Edit, Write, NotebookEdit targeting the main checkout are blocked.
    - **Working directory:** Bash, PowerShell or Monitor commands resolving to the main checkout, or unverifiable, are blocked.
    - **Git redirects:** Bash or Monitor commands pointing git at the main checkout through `git -C`, `--git-dir`, `GIT_DIR`, `GIT_WORK_TREE` or a prior `cd` are blocked.
    - **Command shape:** Bash or Monitor commands whose git usage cannot be verified from their text are blocked. This cannot be turned off.
25. These checks read paths, directories and command text only. A write that runs no git, such as `cp` or a redirect, is governed by permissions and the sandbox instead.
26. PowerShell gets only the working-directory check.
27. Each refusal reaches Claude as a tool error naming the worktree and how to proceed, beginning `is isolated in the worktree <path>, but this command`.

### Background sessions

28. `worktree.bgIsolation` (default `"worktree"`) blocks `Edit` and `Write` in the main checkout until the session calls `EnterWorktree`. `"none"` edits in place (2.1.143). Sessions moved to the background with `←` or `/background` edit in place regardless. Background sessions are told of the block up front (2.1.169).

### Cleanup and resume

29. Interactive exit: a clean worktree in an unnamed session is removed with its branch; a named session prompts. Work present, another branch with new commits, or unverifiable state prompts keep or remove.
30. `-p` runs do not clean up, and leave the creation lock until a later stale-lock sweep.
31. The periodic sweep removes Claude-created subagent and background worktrees older than `cleanupPeriodDays`, keeping any with work, uninspectable submodules, unmarked origin, or a live non-backgrounded `--worktree` session. A marker in git metadata identifies Claude-created worktrees. Locks held for running agents are released when the process exits; user-set locks never are.
32. Resume returns to the worktree after verifying it. Missing worktree: continue in the launch directory and clear the binding. In `-p` and SDK resumes, every refusal except a gone worktree stops with a stderr error rather than continuing unisolated.

## Configuration & interfaces

| Key | Effect |
| :- | :- |
| `worktree.baseRef` | `fresh` or `head` |
| `worktree.bgIsolation` | `worktree` or `none` |
| `worktree.symlinkDirectories` | Symlink listed directories in |
| `worktree.sparsePaths` | Sparse-checkout paths; include `.claude` |
| `worktree.location` | Desktop SSH sessions only |
| `WorktreeCreate`, `WorktreeRemove` hooks | Replace git logic; `.worktreeinclude` is then not processed |
| `.worktreeinclude` | Copy ignored files |

Shared with the main checkout: `.git`, project-scope plugins, saved permission approvals (to the main `.claude/settings.local.json`, 2.1.211), and untracked `.claude/skills`, `agents`, `commands` when absent in the worktree (skills v2.1.277+).

## Failure modes & edge cases

- `Can only use --worktree in a git repository` without a `WorktreeCreate` hook.
- `belongs to a different repository` or `is a leftover worktree` after a project move; use another name.
- Resume messages: `Your worktree <path> no longer exists`, `Could not verify your worktree`, `Did not re-enter your worktree`, `Could not re-enter your worktree`.
- `includeIf` in repository `.git/config` blocks creation.
- A `WorktreeCreate` hook that fails outside a repository releases the background-edit block.

## Changes since the snapshot

- 2.1.105: `path` parameter.
- 2.1.128 then 2.1.133: branch base changed to local `HEAD`, then `worktree.baseRef` with `fresh` default.
- 2.1.143: `worktree.bgIsolation`.
- 2.1.157: switching between managed worktrees mid-session (the snapshot refused with "Already in a worktree session").
- 2.1.169: background sessions warned early.
- v2.1.203: nested repositories accepted.
- 2.1.206: prompt outside `.claude/worktrees/`.
- 2.1.211: approvals save at the repository root.
- 2.1.212: `ExitWorktree` after print-mode resume.
- 2.1.233: GitLab MR support.
- v2.1.247: filter drivers skipped.
- 2.1.265: parallel checkout (git 2.32+).
- 2.1.309: no on-demand object fetch.

## Open questions

- Whether `ExitWorktree` acts on a `--worktree` session; the snapshot limited it to `EnterWorktree` sessions, while docs say only "a worktree session".
- Whether `tmuxSessionName` output still has a live path to set it.
- Current `name` slug rules; the snapshot allowed letters, digits, dots, underscores and dashes per `/`-separated segment.
