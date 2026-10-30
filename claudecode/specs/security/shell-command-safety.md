# Shell Command Safety

**Status:** shipped
**Provenance:** both
**Sources:** docs `permissions` (Bash, PowerShell, redirections), `permission-modes` (critical paths), `security`; snapshot `tools/BashTool/` (feature-level only), `utils/permissions/dangerousPatterns.ts`, `shellRuleMatching.ts`; changelog 2.1.90–2.1.314

Scope: conceptual. This spec states which protections exist and how outcomes vary. It deliberately omits parser heuristics, specific detection cases and anything that describes how a check could be avoided. Documented opt-outs for individual checks are out of scope.

## Purpose

Shell commands are the widest capability Claude has. Before running one, the client must decide whether the text can be understood well enough to trust a rule or a read-only judgment, and must treat anything it cannot understand as needing a human or a stronger boundary.

## Behaviour

### Principles

1. Analysis MUST be fail-closed: a command that cannot be fully analysed MUST NOT be treated as read-only or as matching an allow rule. In Manual mode it asks.
2. Static analysis MUST be understood as a decision aid. Where a guarantee is needed, OS enforcement ([os-sandbox.md](os-sandbox.md)) or a user hook is the mechanism.
3. A partial allow rule MUST NOT skip the prompt for a command that could not be analysed. Sandboxed commands can run without it because the boundary contains them.
4. Very long commands (over 10,000 characters) MUST always prompt.
5. Prompts MUST show the command in full between dashed lines and SHOULD give a short reason when part of it cannot be checked. Options that would grant more than can be displayed MUST be withheld.
6. Prompts SHOULD render unusual Unicode legibly (2.1.282).

### Read-only classification

7. A built-in, non-configurable set of commands MUST run without prompting in every mode, covering listing, viewing, searching, comparing and read-only `git` forms, subject to `blockReadsOutsideWorkingDirectories`. To require a prompt, users add an ask or deny rule. In auto mode these may wait for server review.
8. Read-only status MUST be judged per invocation, not per program name. The classification MUST lose read-only status when flags or context change a command's effect, including: flags that can write, execute, open extra files or expose environment; globs that could expand into such flags; selection of a different container daemon; arguments reaching network paths on Windows; changes to shell variables that control lookup or word splitting.
9. `cd` into a working directory is read-only. Compound commands of read-only parts run unprompted, except a directory change combined with `git` (since repository hooks could run) or with a redirect whose base cannot be determined.

### Compound and nested commands

10. Commands MUST be split into subcommands, and each MUST be approved. Deny and ask rules apply to subcommands wherever nested.
11. Redirects and `tee` destinations MUST be checked as file operations, against Edit rules, protected paths and working directories for output, and Read rules and working directories for input. Allow rules approve the command, not its targets. Targets with no backing file are not checked.
12. Recognized file commands such as `cat`, `sed` and `tee` MUST be subject to Read and Edit deny rules for the paths they name.
13. Writes that file tools refuse outright (credential stores) MUST prompt even with a whole-tool `Bash` allow or an allowing hook.
14. Daemon-redirect options for container tooling MUST require permission.

### Critical-path removals

15. Critical paths are the filesystem root, its direct children, the home directory, drive roots and their top-level directories, the working directory and its parents, and, for globs only, additional working directories and their parents. Spellings that resolve to these on Windows count, as do macOS `/private` system paths.
16. The check MUST also treat as critical: targets that could become a critical path when an expansion is empty; targets that cannot be determined before running; and paths whose reach cannot be bounded before running.
17. The check MUST look inside nested command forms and inline shell scripts.
18. When the shell might read a command differently from how it was parsed, the client MUST report that a dangerous removal cannot be ruled out and treat it as critical.
19. Mounted drive paths under `/Volumes`, `/System/Volumes`, `/media`, `/run/media`, `/mnt` MUST get the same handling for recursive removal.
20. No allow rule, PreToolUse `allow`, or auto-allow MUST approve a recognized removal.
21. Outcomes:

| Mode | Outcome |
|---|---|
| `default`, `acceptEdits` | Prompt |
| `plan` | Prompt; as `auto` when the classifier reviews commands and bypass is unavailable |
| `auto` | Terminal prompt with time limit; elsewhere deny |
| `dontAsk` | Deny |
| `bypassPermissions` | Terminal prompt with time limit; elsewhere per host |

22. Explicit ask rules MUST prompt, untimed, even in auto. `PermissionRequest` hooks can answer in modes that ask.
23. The time-limited prompt MUST count down two minutes, stop on any keypress, then deny and tell Claude what to do instead. After three unanswered prompts in a session, further removals MUST be denied immediately until a new user message.
24. VS Code chat panel and Desktop MUST deny in auto. In bypass they deny unless a `PermissionRequest` hook allows. `-p` and SDK in bypass use the prompt tool or callback, else deny unless a hook allows.
25. Prompts name the flagged command and offer a rewrite hint so unattended runs can recover.
26. The check is best-effort: a miss gets no special handling and other commands can delete too. Deny rules, the sandbox and strict sandbox mode apply independently, and the docs direct relying on those for a guarantee.
27. Any documented opt-out from these prompts MUST be read only from the launch environment, MUST be ignored in settings `env` blocks, and MUST NOT take effect while something else handles prompts, deny or ask rules cover relevant tools, managed settings are unreadable, or the session was started by Claude Code itself. Startup MUST report its state.

### PowerShell

28. `Remove-Item` and `cmd` `rd`, `rmdir`, `del`, `erase` MUST have their own checks. System paths MUST be denied in every mode, without asking. `Remove-Item` wildcard targets MUST be denied before the classifier. Recursive removal of the working directory or parents needs normal approval.
29. Parsing MUST use the PowerShell AST. Failure to parse MUST NOT degrade deny rules.
30. Commands with UNC arguments MUST prompt.

### Subprocess environment

31. Only known-safe leading variable assignments MUST be stripped for allow matching, and assignments that can change which program runs MUST NOT be auto-allowed by the sandbox.
32. Project settings MUST NOT set variables that choose where files are stored, which binaries Windows runs, or what telemetry exports ([trust-dialogs.md](trust-dialogs.md)).
33. `CLAUDE_CODE_SUBPROCESS_ENV_SCRUB=1` MUST strip credentials from subprocess environments while the client keeps them for API calls, leaving GitHub tokens and proxy settings. On Linux every command then runs sandboxed. `CLAUDE_CODE_SCRIPT_CAPS` caps per-session script invocations as a defence-in-depth measure and does not detect runtime fan-out.
34. Clipboard writes on Windows MUST NOT expose content in process arguments.

## Configuration & interfaces

| Interface | Purpose |
|---|---|
| `permissions.ask`, `.deny` | Force or block |
| `CLAUDE_CODE_SUBPROCESS_ENV_SCRUB`, `CLAUDE_CODE_SCRIPT_CAPS` | Subprocess hardening |
| `PreToolUse` | Own inspection of full command text |
| `PermissionRequest` | Answers critical-path prompts in modes that ask |

## Failure modes & edge cases

- Analysis time spent on wildcard rule expansion MUST stay interruptible (Linux, 2.1.299).
- Classifier and read-only judgments in auto can be overridden by server review, which also covers sandboxed commands.
- `-p` runs with a denied removal continue working.

## Changes since the snapshot

- 2.1.90: PowerShell hardening. 2.1.111: read-only globs. 2.1.113: macOS `/private` targets, `find` actions, exec-wrapper deny matching. 2.1.116: sandbox auto-allow keeps the check.
- 2.1.119: PowerShell auto-approval. 2.1.126: Windows clipboard arguments. 2.1.208: nested-form catastrophic removals prompt in bypass and auto. 2.1.214: daemon-redirect and `file` flag checks.
- 2.1.218: dangerous-`rm`, background `&` and Windows path checks adjudicated by the classifier in auto. 2.1.238: zsh conditional syntax. 2.1.257: Ctrl+E explanation removed.
- 2.1.269: `tee` target checks. 2.1.277: named-command prompt and rewrite hint. 2.1.281: two-minute prompt. 2.1.283: `cmd` removal checks. 2.1.287: credential-file shell writes prompt. 2.1.288: shorter reasons. 2.1.290: `pyright` and `ps` forms need approval. 2.1.292: Windows volume and short-name spellings. 2.1.309: immediate denial in Desktop and VS Code bypass.

## Open questions

- Whether `auto` still routes some checks to the classifier in terminal sessions when time limits are off is not reviewed; opt-outs are out of scope.
- The exact current read-only set is not published in full; `permissions` gives examples only.
