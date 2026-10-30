# Worktrees and Isolation

**Status:** shipped
**Provenance:** both (`--worktree`, `EnterWorktree`, `ExitWorktree`, agent isolation in snapshot; enforcement checks and hardening post-leak)
**Sources:** docs `worktrees`, `tools-reference`, `hooks`, `settings-reference`, `sub-agents`, `permissions`; snapshot `utils/worktree.ts`, `tools/EnterWorktreeTool`, `tools/ExitWorktreeTool`; changelog 2.1.105 to 2.1.309

## Purpose

Worktrees give a session or agent a separate checkout, so parallel edits do not collide. This spec defines creation, entry, cleanup, resume, enforcement and non-git replacement. Which sessions move automatically is in [background-sessions.md](background-sessions.md).

## Behaviour

### Creation

1. `--worktree [name]` / `-w` MUST create `.claude/worktrees/<name>/` at the repository root on branch `worktree-<name>`, generating a name if omitted.
2. Interactive use requires workspace trust. `-p` skips the check.
3. An existing name MUST reopen that worktree. With a `fresh` base, a reopened worktree resets to the default branch only if it is clean, still on its own branch, and has no own commits (or its PR was merged and the remote branch deleted, detected from git state alone). Otherwise it opens at its old tip. It also opens at the old tip if state cannot be verified, with `baseRef: "head"`, or for PR references.
4. `worktree.baseRef`:
   - `fresh` (default): branch from the remote default. If not fetched in 24 hours, fetch with a five-second cap, using the cached ref on failure. If no remote or `origin/HEAD` is unavailable, use local `HEAD`.
   - `head`: current local `HEAD`, which inside a worktree means that worktree's `HEAD`.
   Branch names are not accepted.
5. A fetch MUST never wait for terminal input. A password, passphrase or host-confirmation request counts as failure.
6. `--worktree "#N"`, a GitHub PR URL or a GitLab MR URL MUST fetch that change's head from `origin` into `.claude/worktrees/pr-<number>`. Only the number is read from a URL. Path by host: github.com `pull/<n>/head`; gitlab.com `merge-requests/<n>/head`; otherwise try both.
7. `.worktreeinclude` (gitignore syntax) MUST copy files that both match and are gitignored, for every git-created worktree. A `**/` pattern reaches files inside a wholly ignored directory only when the directory matches or the first name after `**/` is in the directory's path.
8. `worktree.symlinkDirectories` symlinks listed directories. `worktree.sparsePaths` uses sparse-checkout; include `.claude` to keep settings and rules.
9. Checkout runs in parallel on git 2.32 or later (2.1.265).
10. Replaced objects MUST be ignored during checkout (`GIT_NO_REPLACE_OBJECTS=1`).
11. The repository's own filter drivers MUST NOT run during creation (2.1.247), so `git lfs install --local` repositories get pointer files until `git lfs pull`.
12. Creation MUST fail in four cases: repository config unreadable; a filter driver name that cannot be neutralised; an `includeIf` in the repository's git config; a repository config key pointing LFS at a program.
13. Creation MUST refuse if `.claude`, `.claude/worktrees` or the worktree directory is a symlink (2.1.212).
14. Git MUST NOT fetch objects on demand during creation or reuse. A partial clone with a Bash sandbox fetches them first (2.1.309). If that fails, the error contains `This repository is a partial clone`.
15. Claude Code MUST write a marker into the git metadata of each worktree it creates.

### Entry and exit tools

16. `EnterWorktree` creates a worktree and switches in, or takes `path` for an existing one (2.1.105). New creation and paths under `.claude/worktrees/` do not prompt.
17. A path outside `.claude/worktrees/` MUST prompt, because the move takes the working directory, write access and project configuration. Permission rules and "don't ask again" MUST NOT suppress this. Only `bypassPermissions` skips it (2.1.206).
18. On first entry, the target may be a worktree of the current repository or of a nested repository in a multi-repo workspace (2.1.203).
19. From a worktree session, or from a subagent with a pinned working directory, only the `path` form works and the target must be under `.claude/worktrees/` of the session's repository. Switching leaves the previous worktree untouched (2.1.157).
20. `ExitWorktree` returns to the original directory. It is unavailable to subagents with their own pinned directory.
21. When entering or exiting a git-created worktree, the transcript MUST move to the new directory's project, as `/cd` does. A hook-created worktree keeps its transcript at the launch directory.
22. `${CLAUDE_PROJECT_DIR}` in hooks stays at the original root. The hook input `cwd` follows.

### Subagent isolation

23. `isolation: worktree` in frontmatter or on the call MUST give an agent a temporary worktree from the configured base.
24. A clean finish removes it. With changes it remains until the sweep can remove it safely.
25. A subagent in its own worktree takes its starting instruction files from the main conversation. In the default location it MUST NOT load the worktree root's `CLAUDE.md` or `.claude/rules/` while reading files there.
26. A git status snapshot MUST reflect the worktree.

### Enforcement

27. While a session is isolated, by whatever route, four checks MUST apply to it and to every subagent. Agents with their own worktree carry the same checks.
    - File edits: block `Edit`, `Write` and `NotebookEdit` targeting the main checkout.
    - Command working directory: block Bash, PowerShell or Monitor commands whose directory resolves to the main checkout or cannot be verified to stay outside it.
    - Git redirects: block Bash or Monitor commands that point git at the main checkout.
    - Command shape: block Bash or Monitor commands when the text cannot show that any git it runs stays in the worktree. This check cannot be turned off.
28. The checks cover the launch repository and the main checkout of a linked worktree. PowerShell gets only the working-directory check.
29. Refusals MUST be tool errors naming the worktree and how to proceed.
30. The checks are not a write sandbox. They read paths, directories and command text, and do not track what a command writes. Containment of shell writes belongs to permissions and sandboxing.

### Identity verification

31. Before adopting a directory as an isolated checkout, whether creating, entering or reusing, Claude Code MUST verify its git identity, and refuse with `Refusing to use <path> as an isolation worktree` if its metadata resolves into the main checkout, or if a `.git` entry is unreadable. Refused directories stay on disk.
32. A directory with no git metadata passes only when no repository contains it.
33. It MUST refuse a directory containing the protected checkout, and problems in the main checkout's own git metadata MUST be reported as such.

### Cleanup on exit

34. Interactive exit, for git-created worktrees:
    - Clean, unnamed session: remove worktree and branch automatically.
    - Clean, named session: prompt.
    - Work present (changes, untracked, submodule work, new commits): prompt keep or remove. Keep prints a `claude --worktree <name> --resume` command.
    - Another branch checked out with commits past the start: prompt; that branch is kept either way.
    - State unverifiable: prompt, naming what could not be checked.
35. Removal MUST NOT fall back to `rm -rf` when `git worktree remove` fails (2.1.143).
36. On Windows, removal MUST delete only links, not targets, for junctions and symlinks.
37. `/exit`'s Remove worktree MUST run after stopping servers and shells started there (2.1.286).
38. `-p` runs have no prompt and leave worktrees and their locks in place.

### Sweep and locks

39. A periodic sweep MUST remove Claude-created agent and background-session worktrees older than `cleanupPeriodDays`.
40. It MUST keep a worktree with changes, untracked files or unpushed commits; submodule changes or uninspectable submodules; filter-driver config cases; a non-backgrounded `--worktree` session's worktree; user-created ones; anything with no marker.
41. Squash-merged PR worktrees are removable (2.1.105).
42. While an agent or backgrounded session runs, Claude Code MUST hold `git worktree lock`, released at finish (2.1.248 for backgrounded sessions). The sweep releases locks of exited processes, never user locks.
43. Claude-managed worktrees are unlocked when agents finish (2.1.157).

### Resume

44. A resume MUST return to the session's worktree, including `-p` and SDK resumes (2.1.212), after re-verifying it.
45. `--resume` from the main checkout or elsewhere in the repository re-enters a git-created worktree under `.claude/worktrees/`. From inside other worktrees it re-enters only if vouchable.
46. `--fork-session` starts in the launch directory and leaves the worktree alone.
47. A deleted worktree resumes in the launch directory, clearing the binding, with a notice.
48. Interactive messages: `Your worktree <path> no longer exists`; `Could not verify your worktree <path> this time` (binding kept); `Did not re-enter your worktree <path>` (binding cleared); `Could not re-enter your worktree <path>` (binding kept).
49. `-p` and SDK resumes MUST stop with a stderr error for every refusal except a gone worktree. With stream-json the same text arrives as a `result` of subtype `error_during_execution`, and `startup_failure_reason` is `worktree_unverified` or `worktree_resume_refused`.
50. Worktrees at network paths MUST NOT be resumed into.

### Sharing

51. Shared with the main checkout: `.git` (the sandbox allows those writes), project-scope plugins, and "don't ask again" rules saved to the main checkout's `.claude/settings.local.json` (with exceptions such as Windows).
52. When the worktree has no `.claude/skills` at its root, the main checkout's project skills load; if it has one, only that copy. The same read-through covers `.claude/agents` and `.claude/commands`.
53. Desktop worktree sessions read project configuration from the main root; CLAUDE.md and rules load from the worktree.

### Non-git

54. A `WorktreeCreate` hook MUST replace git logic entirely and return the directory path. `.worktreeinclude` is not processed. `WorktreeRemove` handles cleanup.
55. Triggers: `--worktree`, `EnterWorktree`, agent isolation, workflow agents, background isolation, `claude remote-control` worktree mode. Not `git worktree add` through Bash, and a plugin's hook does not run with `--worktree --tmux`.
56. `/batch` runs outside git with such a hook (2.1.281).

## Configuration & interfaces

| Setting | Values |
| --- | --- |
| `worktree.baseRef` | `fresh`, `head` |
| `worktree.bgIsolation` | `none` |
| `worktree.symlinkDirectories` | list |
| `worktree.sparsePaths` | list |
| `worktree.location` | Desktop SSH only |

Flags: `-w`, `--worktree`, `--tmux[=classic]` (requires `--worktree`). Status line JSON: `workspace.git_worktree` (2.1.97).

## Failure modes & edge cases

- `Can only use --worktree in a git repository` with no hook.
- `belongs to a different repository` or `is a leftover worktree` after a copy or move: use a new name.
- Startup entry failure: path printed, exit code 1.
- A bare-repository root gives a layout explanation (2.1.299). An unresolved base gives a detailed error.
- Suppressed transcript writes: the binding cannot be cleared, and the message says so.

## Changes since the snapshot

- 2.1.105: `path` on `EnterWorktree`; squash-merged cleanup.
- 2.1.133: `worktree.baseRef`. 2.1.128 briefly moved `EnterWorktree` to local `HEAD`.
- 2.1.143: no `rm -rf` fallback.
- 2.1.157: switching between worktrees. 2.1.203: nested repositories. 2.1.206: approval for outside paths.
- 2.1.212: symlink refusal; non-interactive worktree resume.
- 2.1.233: GitLab MR URLs. 2.1.247: filter drivers skipped.
- 2.1.260, 2.1.274: resume error reporting. 2.1.274: submodule checks.
- 2.1.277: skills read-through. 2.1.302: stray `.git` file handling with git 2.56.
- 2.1.309: no on-demand fetch.

## Open questions

- The exact sweep cadence.
- Marker storage within git metadata.
- Whether the snapshot's ephemeral slug patterns (`agent-a<hex>`, `wf_...`, `bridge-...`, `job-...`) remain the naming scheme.
