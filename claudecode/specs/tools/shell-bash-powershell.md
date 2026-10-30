# Shell Tools: Bash and PowerShell

**Status:** shipped (PowerShell: preview)
**Provenance:** both
**Sources:** docs `tools-reference` (Bash, PowerShell), `agent-sdk/typescript`, `hooks`, `permissions`, `sandboxing`, `env-vars`, `settings-reference`; snapshot `tools/BashTool`, `tools/PowerShellTool`; changelog 2.1.89 to 2.1.314

## Purpose

Run shell commands in the user's environment. Each command runs in its own process, under a timeout, with output captured to a file and returned under size rules. Backgrounding and `Monitor` are in [shell-background-and-monitor](shell-background-and-monitor.md).

## Behaviour

### Input

1. Bash input is `command`, optional `timeout` (ms), `description`, `run_in_background`, `dangerouslyDisableSandbox`. PowerShell passes the command as `tool_input.command` with the same fields as Bash.
2. Claude writes `description` in plain words saying what the command does, not echoing it (2.1.267).
3. In auto mode with sandboxing, a command MAY carry per-command `allowed_domains`: hosts reviewed with the command and opened for it alone, for Bash, PowerShell and Monitor (2.1.271). Other hosts MUST be refused, with the refusal naming the host.

### Persistence

4. Main-session `cd` MUST carry to later commands, including later turns, while it stays inside the project or an additional working directory. If it leaves them, the cwd resets to the project and the result gains `Shell cwd was reset to <dir>`. Subagent sessions never carry directory changes.
5. Environment variables MUST NOT persist between commands.
6. At session start Claude Code MUST source `~/.zshrc`, `~/.bashrc` or `~/.profile` by shell, capture aliases, functions and options, and apply them to every Bash command. Since 2.1.314 the shell clears any inherited `which` alias or function and does not pass exported `which`/`unsetenv` functions to commands.
7. `CLAUDE_ENV_FILE` names a script run before each Bash command in the same shell process. A SessionStart hook can populate it.

### Timeout

8. Each command runs under a timeout. Claude passes `timeout` when it wants longer than the default.
9. Foreground default is 2 minutes (`BASH_DEFAULT_TIMEOUT_MS`). The ceiling is the larger of `BASH_MAX_TIMEOUT_MS` (default 10 minutes) and that default; larger requests are clamped, not rejected (enforced since 2.1.110).
10. In a session with a background time limit, `timeout` on a command started in the background sets that limit instead.
11. PowerShell follows the same rules and variables.
12. At timeout a foreground command moves to the background unless it starts with `sleep` or backgrounding is off, in which case it stops. The result shows output so far and says it is still running (2.1.311).

### Output

13. Output MUST stream to a working file as the command runs. A command whose output passes 5 GB is killed.
14. What reaches Claude depends on whether the result counts as a failure:

| Result | Inline | Past that |
| :- | :- | :- |
| Valid | About 30,000 characters | File path in the session directory, truncated past 64 MiB, plus a preview of up to 2,000 characters |
| Failure | About 10,000 characters | Head-and-tail excerpt of that size from the read-back window, no file path |

15. `BASH_MAX_OUTPUT_LENGTH` sets the read-back window (default 30,000; hard ceiling 150,000) and does not raise inline ceilings.
16. `bashOutputMaxChars` (up to 128,000; v2.1.261+) sizes the inline ceiling and read-back window together and makes `BASH_MAX_OUTPUT_LENGTH` ignored.

### Exit-code semantics

17. Exit 1 MUST count as valid only for `grep`, `rg`, `egrep`, `fgrep`, `find`, `diff`, `test`, `[`, `git diff`, `git grep`. Every other exit 1 is a failure, including `pgrep`, `jq -e`, `cmp`.
18. PowerShell can treat exit 1 as normal for `grep`, `rg`, `egrep`, `fgrep`, `findstr`, `git grep`, `git diff`. When such a search is part of a longer command, `Error: Exit code 1` can still appear. `where.exe`, `fc.exe`, `diff.exe` and `robocopy` (1 through 7) can show an error though the command succeeded.

### Result fields

19. `BashOutput.stdout` holds merged stdout and stderr; `stderr` holds notices the tool adds, not the command's stderr.
20. Other notable fields: `interrupted`, `backgroundTaskId`, `timedOutAfterMs`, `backgroundCwdHint`, `backgroundEndsWithFinalResponse`, `returnCodeInterpretation`, `persistedOutputPath`, `persistedOutputSize`, `staleReadFileStateHint`, `ghRateLimitHint`, and `gitOperation` recording commits, pushes, branch merges and rebases, and PR actions.
21. `staleReadFileStateHint` warns when a formatter or linter changed files Claude had read (2.1.89). `ghRateLimitHint` surfaces GitHub API limits (2.1.116).
22. A failed Bash call MUST NOT cancel other calls in the same batch (2.1.161).
23. A command cut off by a full disk MUST say so and name the folder to free (2.1.309).

### Changed-file diffs

24. When enabled, Claude Code records changes under the repository while a command ran and gives them to PostToolUse hooks as `tool_response.bashEditDiff` (v2.1.269+). It records in every mode with `bashEditDiffEnabled`, and otherwise only in auto and `bypassPermissions` modes when Claude is directed to edit through Bash. `CLAUDE_CODE_BASH_EDIT_DIFF` overrides.
25. The record is best-effort public beta, not an enforcement signal. Fields: `changedFiles` (up to 200), `files` (up to 5 diffs), `moreFiles`, `unavailable`, `skipped`, `shared`. Git-ignored and submodule files are excluded. Chained `git merge`, `pull` or `checkout` list files without full diffs (2.1.290).

### Permissions

26. Bash is permission-required, except that a built-in read-only set runs without a prompt in every mode, subject to `permissions.blockReadsOutsideWorkingDirectories`. `pyright` and more forms of `ps` left the set in 2.1.290.
27. Deny rules MUST match through exec wrappers such as `env`, `sudo`, `watch`, `ionice`, `setsid` (2.1.113). `Bash(find:*)` allows MUST NOT auto-approve `find -exec`/`-delete`.
28. A startup warning flags allow rules with a wildcard before the subcommand (2.1.246). `Bash(ls) x`-style rules are invalid settings (2.1.260).
29. `autoMode.classifyAllShell` routes all shell commands through the classifier (2.1.193).
30. The command-safety analyser, path validation and sandbox decision logic in the snapshot's `bashPermissions`, `bashSecurity`, `pathValidation`, `readOnlyValidation` and PowerShell counterparts exist; their rules are out of scope here. Rule matching is in `permissions`.

### Memory cap (Linux, WSL)

31. `CLAUDE_CODE_TOOL_MEMORY_LIMIT` (v2.1.233+) caps all of a session's Bash, PowerShell and Monitor commands as one pool through a memory cgroup. Sizes are bytes or `K`/`M`/`G`/`T`; `0`, `off`, `false`, `no`, `none` disable; unreadable values such as `4e9` are ignored.
32. If the cgroup cannot be set up, commands run uncapped and `--debug` says why. The first process's result holds until relaunch. The kernel kills an over-limit command, and nothing in the result names the cap.
33. `CLAUDE_CODE_TOOL_MEMORY_CGROUP_EXCLUDE` (v2.1.246+) lists kinds exempt from the cap: `mcp`, `lsp`, `hooks`, `plugin`, `helper`, `agent`; `none` caps all, `all-new` caps only the shell tools. Unset takes a server-delivered set. Permission-gating hooks, and MCP servers they call, stay excluded so a kill cannot allow what the hook was blocking.

### PowerShell availability

34. Windows without Git Bash: on automatically (2.1.120). Windows with Git Bash: on by default for claude.ai and Console accounts; `CLAUDE_CODE_USE_POWERSHELL_TOOL=1` enables it on Bedrock, Agent Platform and Foundry, `0` turns it off. Linux, macOS, WSL: opt-in, requires `pwsh` 7+ on PATH.
35. On Windows, `pwsh.exe` is detected with fallback to `powershell.exe` 5.1. When enabled, PowerShell is the primary shell (2.1.126); Bash stays for POSIX scripts when Git Bash exists.
36. PowerShell spawns with process-scope `-ExecutionPolicy Bypass` (2.1.143). Group Policy still applies. `CLAUDE_CODE_POWERSHELL_RESPECT_EXECUTION_POLICY=1` opts out.
37. On Windows with Git Bash, a Bash deny, scoped or bare, from settings or `--disallowedTools`, also turns PowerShell off for the session, because a `Bash` rule does not restrict PowerShell. An explicit enable value or a scoped `PowerShell` rule keeps it on. Removing all of Bash then leaves no shell tool; a startup warning covers this (2.1.287). A scoped deny disables PowerShell silently.
38. PowerShell shares cwd handling and `CLAUDE_BASH_MAINTAIN_PROJECT_WORKING_DIR`, and receives `CLAUDE_ENV_FILE` variables under the hooks-doc conditions (v2.1.296+).
39. Encoding: `>`/`>>` write UTF-8 on 5.1, piped stdin to native commands is UTF-8, captured error output has no ANSI codes, and a child waiting on stdin gets EOF.
40. Preview limits: profiles are not loaded; sandboxing is not supported on Windows.

### Windows Bash

41. Git Bash is located automatically or through `CLAUDE_CODE_GIT_BASH_PATH`. An invalid path falls back to detection with a `--debug` warning (not a startup exit since v2.1.219).

## Configuration & interfaces

| Key | Purpose |
| :- | :- |
| `BASH_DEFAULT_TIMEOUT_MS`, `BASH_MAX_TIMEOUT_MS` | Timeouts |
| `BASH_MAX_OUTPUT_LENGTH`, `bashOutputMaxChars` | Output sizing |
| `CLAUDE_BASH_MAINTAIN_PROJECT_WORKING_DIR` | Disable `cd` carry-over |
| `CLAUDE_CODE_SHELL` | Shell binary; `bash` or `zsh` only, otherwise auto-detect |
| `CLAUDE_CODE_SHELL_PREFIX` | Prefix wrapping spawned shell commands |
| `CLAUDE_ENV_FILE` | Per-command environment script |
| `CLAUDE_CODE_USE_POWERSHELL_TOOL` | PowerShell switch |
| `defaultShell`: `"powershell"` | Routes interactive `!` commands; needs the tool on |
| `shell: powershell` (skill frontmatter) | Inline shell blocks; needs the tool on |
| `"shell": "powershell"` (command hook) | Works whatever the tool's state |

Match `Bash|PowerShell` in hooks that inspect shell commands. `/env` applies to both (2.1.89). Plugin `bin/` executables are bare commands in Bash (2.1.91). Subprocesses inherit W3C `TRACEPARENT` when tracing is on (2.1.98).

## Failure modes & edge cases

- Virtualenv activation must precede launch or use `CLAUDE_ENV_FILE`.
- A failure's excerpt comes from the read-back window, so raising `BASH_MAX_OUTPUT_LENGTH` helps failures but not valid-result inlining.
- Sandboxed commands do not inherit WebFetch's preapproved domains.
- In cloud sessions, a proxy-dropped connection names the host and reason (2.1.251).
- `sed -i` runs as ordinary Bash and is not restored by `/rewind` (2.1.309).

## Changes since the snapshot

- 2.1.89: PowerShell argument hardening; `/env` coverage; stale-read warning.
- 2.1.110: enforced maximum timeout.
- 2.1.111: PowerShell progressive Windows rollout.
- 2.1.113: deny rules see through exec wrappers; removal-target and `find` hardening.
- 2.1.120, 2.1.126: Git Bash optional; PowerShell primary when on.
- 2.1.143: `-ExecutionPolicy Bypass`.
- 2.1.161: failed Bash no longer cancels siblings.
- 2.1.193: `autoMode.classifyAllShell`.
- 2.1.233, 2.1.246: tool memory cap and exclusions.
- 2.1.246: faster bash snapshot replay.
- 2.1.269, 2.1.290, 2.1.293: changed-file diffs.
- 2.1.271: per-command `allowed_domains`.
- 2.1.287: Windows warning when Bash deny removes PowerShell.
- 2.1.309, 2.1.311, 2.1.314: disk-full reporting; timeout result text; `which` cleanup.

## Open questions

- Whether `allowed_domains` is a formal input field; it is not in the published `BashInput`.
- The full read-only command set and how it differs between Bash and PowerShell.
- Current thresholds for blocking long foreground `sleep`; the snapshot detected leading sleeps of 2 seconds or more, and 2.1.310 says long foreground sleeps are blocked.
