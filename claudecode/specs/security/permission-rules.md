# Permission Rules: Syntax and Evaluation Order

**Status:** shipped
**Provenance:** both; heavily extended post-leak
**Sources:** docs `permissions`, `settings-reference`, `settings`, `agent-sdk/permissions`, `errors`, `hooks`; snapshot `utils/permissions/permissions.ts`, `permissionRuleParser.ts`, `permissionsLoader.ts`, `shadowedRuleDetection.ts`, `shellRuleMatching.ts`, `pathValidation.ts`, `filesystem.ts`; changelog 2.1.111–2.1.314

## Purpose

Permission rules let users, projects and organizations declare which tool calls run, prompt or are refused. The client, not the model, enforces them.

## Behaviour

### Evaluation order

1. Rule outcomes MUST be evaluated deny, then ask, then allow. The first match decides and specificity MUST NOT change that order. An allow rule cannot carve an exception from a deny or ask rule.
2. The full call pipeline MUST be:
   1. PreToolUse hooks run first. A blocking hook stops the call. A hook `allow` MUST NOT skip step 2 or 3.
   2. Whole-tool deny, then whole-tool ask (a sandbox auto-allow can stand in for a whole-tool ask; see [os-sandbox.md](os-sandbox.md)).
   3. The tool's own check: content-scoped deny, content-scoped ask, safety checks, path validation.
   4. Interaction-required tools prompt regardless of mode.
   5. Mode evaluation (`bypassPermissions`, plan constraints).
   6. Allow rules.
   7. Anything unresolved becomes an ask, then the mode transforms it: `dontAsk` denies; `auto` routes to the classifier; otherwise a mod's `tool.check`, the `canUseTool` callback, `--permission-prompt-tool`, or the dialog answers.
3. The ask-to-deny transformation for `dontAsk` MUST happen last, so no earlier return can skip it.
4. Allow rules MUST NOT approve: protected-path writes, critical-path removals, network-path reads, requires-interaction MCP tools, org-`ask` connector tools.
5. PreToolUse `allow` likewise MUST NOT approve critical-path removals, network-path reads, requires-interaction MCP tools or org-`ask` connector tools.

### Hooks and mods

6. A mod's `tool.check` answers after PreToolUse hooks. With managed settings on the machine, or a Team or Enterprise `/login` as the session's credential, a mod approval MUST NOT by default override: a deny (the organization can change this), an ask, a hook or `blockReadsOutsideWorkingDirectories` prompt, a hook block, or a configured prompt tool or `canUseTool` callback. Otherwise a mod the user installed may approve those calls.
7. Regardless of setup: in auto, a mod approval skips the classifier except where it cannot pass a prompt tool or callback; in plan, a mod cannot approve non-read-only calls; in `dontAsk`, a mod can approve calls that only the mode would deny; a mod approval MUST NOT skip the prompt for `AskUserQuestion` and other interaction-required tools.
8. A mod's `decider: "person"` answer means only the dialog or a host callback can approve; where nobody can be asked it MUST be refused with the mod's reason.

### Scopes and merging

9. Rule arrays MUST merge across scopes rather than override. Deny at any level beats allow at any other. `--allowedTools` adds allow rules, `--disallowedTools` adds deny rules. Managed deny MUST NOT be overridable by any flag.
10. `allowManagedPermissionRulesOnly` makes managed settings the only settings source of rules: user, project, local and `--settings` rules and `--allowedTools` are ignored, always-allow choices are hidden and no rules are saved. `--disallowedTools` and session deny and ask rules still apply, surviving settings reloads. From 2.1.282 it also ignores `allowed-tools` frontmatter from repo, user, `--add-dir` and repo-shared plugin sources.
11. Project `permissions.allow` and `additionalDirectories` MUST apply only after workspace trust ([trust-dialogs.md](trust-dialogs.md)). Deny and ask are unaffected.

### Rule grammar

12. A rule is `Tool` or `Tool(specifier)`. Parentheses inside a specifier are literal and need no escape. Text after the closing parenthesis MUST be reported as invalid.
13. `Tool` and `Tool(*)` are equivalent. As a deny, a bare name removes the tool from Claude's context; a scoped rule leaves it and blocks matching calls. Mid-session additions apply from the next tool call.
14. `EndConversation` MUST NOT be removed or prompted by deny or ask while any other tool remains.
15. Rules match canonical tool names, not display labels. A deny or ask naming no known tool MUST warn at startup, except names containing `_` or `*` and names of removed tools.
16. `Tool(param:value)` works for deny and ask on built-in tools only:
    - one top-level scalar parameter per rule; nested fields are not matchable;
    - `*` is a wildcard; an omitted parameter never matches; comparison uses the literal input before normalization;
    - primary content fields (`command`, `file_path`, `path`, `notebook_path`, `url`) MUST be rejected with a startup warning;
    - `Skill(skill:<name>)` deny matches the skill under any name;
    - settings-file `mcp__` rules with parentheses are skipped and reported; MCP parameter deny rules go through `--disallowedTools`.
17. Tool-name globs: deny and ask accept full-name globs (`*`, `mcp__*`); a bare-name glob deny removes matched tools. Allow accepts globs only after a literal `mcp__<server>__` prefix; unanchored allow globs MUST be skipped.

### Bash and PowerShell rules

18. Bash rules match command text. `*` matches any text including spaces and may appear anywhere; no `*` means exact match. A trailing ` *` as the only wildcard also matches the bare command, and the space is significant. `:*` is an equivalent trailing form, recognized only at the end.
19. Compound commands split on `&&`, `||`, `;`, `|`, `|&`, `&` and newlines. Every subcommand must be allowed. Deny and ask rules apply if any subcommand matches, including inside subshells, substitutions and control-flow bodies, and including in auto mode.
20. A dangling `&&` or `||` makes the command unparseable for allow matching.
21. Before matching, a fixed non-configurable set of process wrappers and known-safe leading environment assignments is stripped. Deny and ask rules match past any leading assignment, and exec-wrapper forms; allow rules do not match past unknown assignments.
22. Prefix rules MUST NOT auto-approve exec wrappers or `find` with actions that run, delete or write. Those prompt unless an exact-match rule with no `*` names the full command.
23. Rules naming an environment runner match whatever follows it, so the docs direct one rule per inner command.
24. Bash rules are command-text matches, not a boundary around a program. Enforcement that must not depend on spelling belongs in the sandbox or a PreToolUse hook. This spec does not catalogue non-matching forms.
25. Allow rules with a wildcard before the subcommand MUST warn at startup.
26. PowerShell rules share the shape, are case-insensitive, canonicalize common aliases, and split via the PowerShell AST (including `&&` and `||` on 7+).
27. `Monitor` commands share Bash rule semantics.
28. Approving a compound command with "don't ask again" MUST save a separate rule per subcommand needing approval, at most 5.

### Read and Edit rules

29. `Edit` rules apply to all built-in editors. `Read` rules apply best-effort to built-in readers, `@file`, pasted image paths, directory listings, IDE context and changed-file re-reads.
30. `Read` deny also blocks Edit and Write on the path, including creation. NotebookEdit is not covered; use an `Edit` deny.
31. Read and Edit denies reach built-in tools, recognized file commands in Bash and redirect targets, but not arbitrary subprocesses. OS-level enforcement requires the sandbox.
32. `Write(path)`, `NotebookEdit(path)`, `Glob(path)` and `MultiEdit(path)` path rules never match and MUST warn at startup. Bare names still work.
33. `.claudeignore` has no effect.
34. Path patterns use gitignore syntax:

| Pattern | Anchor |
|---|---|
| `//path` | Filesystem root |
| `~/path` | Home |
| `/path` | Settings source: primary working directory for project, local, CLI and session rules; `~/.claude` for user; file's directory for `--settings` |
| `path`, `./path` | Current directory |

35. Bare filenames match at any depth under the anchor. A single-directory relative pattern (`src/**`) MUST match only `<cwd>/src` as an allow, but at any depth as a deny or ask, so that restrictions cover nested copies. Other shapes behave identically in all rule types.
36. Windows paths normalize to POSIX form; drive-letter paths are root-anchored and case-insensitive on the drive letter.
37. Paths approved through a prompt MUST be escaped so the rule matches only the literal path. Hand-written rules are not escaped.
38. A deny or ask pattern unusable as gitignore still guards that exact path; an unusable allow pattern approves nothing.
39. `!` deny or ask patterns carve from earlier `path` or `./path` rules in the same source only. They MUST NOT cancel rules from another source, reach `/`, `~/` or `//` anchored rules, or reopen a file inside a directory blocked as a whole.

### Symlinks and paths that change

40. Allow rules MUST require both the requested and resolved paths to match. Deny rules MUST apply if either matches. Deny and ask rules written through a symlinked directory also apply at its real location on macOS and Linux.
41. `Edit` and `Write` on a path that is itself a symlink MUST refuse and direct Claude to the target.
42. Writes passing through a symlinked directory, or by shell commands, that resolve outside working directories MUST NOT be auto-approved in `acceptEdits`, and MUST prompt in auto mode (naming the resolved path) unless an allow rule approves them.
43. Unresolvable paths MUST be refused. On open, tools MUST confirm the path still resolves to the location the check approved.
44. `@`-mentions that cannot be examined MUST render as a "not read" placeholder.

### Network paths

45. Reads via UNC or `/net` paths MUST get their own check: allow rules, hook `allow` and the classifier MUST NOT pre-approve them. `dontAsk` denies. `bypassPermissions`, and interactive plan with bypass available, skip the prompt.
46. Network paths MUST NOT be added as working directories, without being looked up. A mapped drive passed at launch is the documented alternative.

### WebFetch, MCP, Agent, Cd

47. `WebFetch(domain:...)` is case-insensitive on hostname, ignoring a trailing dot. `*.example.com` matches subdomains at any depth, not the apex. Elsewhere `*` matches within one dot-delimited label. `domain:*` covers all hosts.
48. Bare `WebFetch` and `WebFetch(domain:*)` differ: only the `domain:` form feeds the sandbox domain lists; as a deny the bare form removes the tool while the `domain:` form refuses each fetch. Artifact reads are governed by `domain:` rules covering their hosts and `Artifact` rules, not by bare `WebFetch`.
49. `mcp__<server>__*` and `mcp__<server>` match a server's tools; `mcp__<server>__<tool>` matches one. Names are normalized. Allow rules MUST reach only the named server. Deny and ask rules for a shorter prefix also cover longer `__` names.
50. Org-`ask` connector tools: allow rules do not take effect; every call prompts, and `dontAsk` denies.
51. In Cowork, whole-tool `Bash` or `WebFetch` deny rules MUST also apply to Cowork's workspace tools. Allow rules MUST NOT carry over.
52. `Agent(Name)` matches a subagent type.
53. `Cd` rules govern only the user's `/cd`. Bare `Cd` deny disables it; deny checks every spelling including symlink hops; any `Cd` allow switches to allowlist mode. `*` is one segment, `**` crosses segments, and matching is against the whole directory path.

### Working directories

54. Readable-without-prompt scope is the start directory plus `--add-dir`, `/add-dir`, `permissions.additionalDirectories`.
55. `additionalDirectories` from settings grant file access only. `--add-dir` directories also load skills, commands, agents, `enabledPlugins` and `extraKnownMarketplaces`, and `CLAUDE.md` only with `CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1`.
56. `permissions.blockReadsOutsideWorkingDirectories`: `Read`, `Grep`, `Glob`, `LSP` MUST refuse outside paths in every mode, with Claude's own config kept readable. `true` in any file applies; a repository can turn it on but not lift yours. Repo-only `additionalDirectories` do not count. Recognized shell reads prompt, or the sandbox enforces.
57. `permissions.blockWritesOutsideWorkingDirectories`: Write, Edit, NotebookEdit MUST refuse outside paths in every mode (2.1.314).

### Interaction surfaces

58. Prompts show what will run, then options. "Don't ask again" saves to `.claude/settings.local.json` at the repository root, resolved through worktrees, so it applies across subdirectories and worktrees. File-modification approvals last until session end.
59. "Don't ask again" and session-allow options MUST be offered only when the prompt can show everything they would cover. Otherwise only one-time approval appears.
60. `Tab` on Yes or No attaches a comment on most prompts. On Yes it is delivered after the result; on No it is the denial reason and Claude continues. No without comment on a main-conversation prompt stops the turn.
61. `/permissions` lists rules by source, adds and removes rules, manages directories and shows auto mode tabs. It MUST open during a turn and changes apply from the next tool call. Delete confirmations default to No. Calls that cannot be read in full MUST NOT be approvable from its review tab.
62. Prompts SHOULD count stacked requests and show oldest first, except countdown prompts.
63. Startup warnings about rules show once per user until the rule changes.

## Configuration & interfaces

| Key or flag | Notes |
|---|---|
| `permissions.allow`, `.ask`, `.deny` | Rule arrays |
| `permissions.additionalDirectories`, `--add-dir`, `/add-dir` | Working directories |
| `permissions.blockReadsOutsideWorkingDirectories`, `.blockWritesOutsideWorkingDirectories` | Fences |
| `allowManagedPermissionRulesOnly` | Managed-only |
| `--allowedTools`, `--disallowedTools`, `--tools` | Per-session lists; `--tools` restricts availability |
| Events | `PreToolUse`, `PermissionRequest`, `PermissionDenied` ([../extensibility/hooks.md](../extensibility/hooks.md)); mod `tool.check` |
| OTel | `tool_decision` carries `permission_mode`, `classifier_verdict`, `classifier_category` |

## Failure modes & edge cases

- Invalid entries in user, project or local files are skipped with a warning; a file failing JSON or shape validation is rejected whole. VS Code shows a banner when settings fail to parse.
- If a managed `deny` or `ask` list cannot be read, managed `allow` and `additionalDirectories` MUST be withheld.
- Extending `Read` denies to arbitrary Bash arguments was tried twice and reverted, because it refused unrelated commands. Rule 31 reflects the current state.

## Changes since the snapshot

- 2.1.111: read-only globs and `cd <project> &&` stop prompting; Windows drive-letter anchoring. 2.1.113: deny rules match through exec wrappers; `find` actions need approval.
- 2.1.166: tool-name globs. 2.1.178: `Tool(param:value)`. 2.1.210: never-matching path rule warnings. 2.1.211: rules saved at repository root.
- 2.1.232 then 2.1.233: input-redirect checking added then reverted; docs state it returned by 2.1.257.
- 2.1.234: `/permissions` during a turn. 2.1.235: grant-accurate options. 2.1.246: wildcard-before-subcommand warning.
- 2.1.257: `blockReadsOutsideWorkingDirectories`. 2.1.260: revert of 2.1.259's Read deny on Bash arguments; invalid text after `)`. 2.1.268 then 2.1.273: similar revert.
- 2.1.268: symlinked-directory deny and ask. 2.1.269: `tee` target checks. 2.1.280, 2.1.281, 2.1.286, 2.1.287: `/permissions` and prompt ergonomics.
- 2.1.287: whole-tool `Bash` allow and allowing hooks prompt for shell writes to credential files that file tools refuse. 2.1.292: network-path read check. 2.1.299: MCP allow reaches only the named server. 2.1.304: `decider: "person"`. 2.1.311: warnings once per user.
- 2.1.314: `blockWritesOutsideWorkingDirectories`; `/permissions` Recently blocked refuses unreadable calls.

## Open questions

- `blockWritesOutsideWorkingDirectories` appears only in the changelog; scope and merge semantics are unconfirmed, though "every permission mode" is stated.
- Docs call the tab "Recently denied"; the 2.1.314 changelog calls it "Recently blocked".
- Exact position of mod `tool.check` relative to the `dontAsk` transform is inferred from docs, not stated.
