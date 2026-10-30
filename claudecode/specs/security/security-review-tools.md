# Security Guidance and Security Review

**Status:** shipped
**Provenance:** both (`/security-review` in snapshot); plugins post-leak, versions not stated in changelog
**Sources:** docs `security-guidance`, `claude-security`, `commands`, `errors`, `security`; snapshot `commands/security-review.ts`; changelog 2.1.108, 2.1.314

## Purpose

Three tools help find vulnerabilities in code at different points: an always-on plugin that reviews what Claude writes, an on-demand single pass on the branch, and a multi-agent scanner. None is a replacement for static analysis, dependency scanning or human review.

## Behaviour

### Layering

| Stage | Tool | Coverage |
|---|---|---|
| In session | `security-guidance` plugin | Common vulnerabilities in Claude's own changes |
| On demand, single pass | `/security-review` | Current branch diff |
| On demand, deep | `claude-security` plugin | Repository or diff, independently verified |
| On pull request | Code Review (Team, Enterprise) | Correctness and security review |
| Managed | Claude Security product (Enterprise) | Hosted monitoring |
| CI | User's scanners | Deterministic rules, supply chain |

### `/security-review`

1. MUST review the diff between the current branch and origin's default branch for risks such as injection, auth issues and data exposure. It needs an `origin` remote; lacking `origin/HEAD` fails with an `ambiguous argument` error covered in the error reference.
2. Runs as a prompt-based command. In the snapshot it has read-oriented tool allowances (git inspection, file reading and search) and gathers status, changed files, commits and diff before the model reviews.
3. Model-invocable via the Skill tool (2.1.108). Sessions starting with it get a title from it (2.1.314).

### `security-guidance` plugin

4. Installed from `security-guidance@claude-plugins-official`. Enabling via `.claude/settings.json` or managed `enabledPlugins`. Available on all plans. Cloud sessions load it only through organization distribution.
5. Requires Python 3.7+; agentic commit review, and all model-backed reviews on third-party providers, need 3.10+. First run creates a virtualenv under `~/.claude/security/` with the Agent SDK. On failure, first-party commit review falls back to a single-shot review, while third-party model reviews skip, with a one-time notice.
6. Built entirely on hooks:

| Event | Purpose |
|---|---|
| `SessionStart` | Bootstrap |
| `UserPromptSubmit` | Capture working-tree baseline |
| `PostToolUse` on `Edit`, `Write`, `NotebookEdit` | Pattern check |
| `Stop` | Background diff review |
| `PostToolUse` on `Bash`, filtered to `git commit`, `git push` | Background commit review |

7. Per-edit layer: deterministic string match, no model call, after the edit lands. Warnings MUST fire once per pattern per file per session.
8. End-of-turn layer: git diff of everything changed in the turn, including Bash and subagents, sent to a separate review. Up to 30 files per turn and at most three consecutive firings. Findings re-prompt Claude.
9. Commit layer: agentic review reading surrounding code on commits and pushes Claude makes through Bash only, capped at 20 per rolling hour. Duplicates of end-of-turn findings MUST NOT re-prompt.
10. Reviews MUST run with fresh context, separate from the writing Claude.
11. No layer blocks writes or commits; findings are instructions and can be missed.
12. Custom rules:
    - guidance: `claude-security-guidance.md` in `~/.claude/`, `.claude/`, or `.claude/claude-security-guidance.local.md`, concatenated with an 8 KB cap;
    - patterns: `security-patterns.yaml|yml|json` at the same locations, fields `rule_name`, `reminder` (1 KB), `regex` or `substrings`, `paths`, `exclude_paths`; up to 50 rules; backtracking-prone regexes skipped; YAML needs PyYAML.
13. Rules are additive and MUST NOT suppress built-in checks or findings.
14. End-of-turn and commit reviews default to an Opus model and spend usage. Per-edit costs nothing.

### `claude-security` plugin

15. Installed from `claude-security@claude-plugins-official`. Adds `/claude-security` with jobs: scan codebase, scan changes, suggest patches. Requires a paid plan, API access or third-party provider (for dynamic workflows), `python3` 3.9+, Git for change scans and patches.
16. Agents use the session model; supporting steps use the `sonnet` alias. No separate provider configuration.
17. Full scans map architecture, build a threat model, hunt, and independently verify. Scope options state file counts and relative cost. Nothing runs until confirmed. Claude Code must stay open.
18. Change scans cover a branch diff, an open pull request or a commit, committed changes only. Finding open PRs is the only network step and requires existing `gh` permission.
19. Scan effort: `low` skips the map and threat model; `medium` default; `high` adds hunting. Verification is the same at all levels. Results are nondeterministic.
20. Outputs in `CLAUDE-SECURITY-<timestamp>/`: `CLAUDE-SECURITY-RESULTS.md`, `.jsonl`, `.sarif` (SARIF 2.1.0 with CWE classes), and `CLAUDE-SECURITY-REVISION-<commit>.json` recording commit, effort, whether uncommitted changes were included and verification thoroughness (`UNVERSIONED` outside version control). The directory is the only change to the checkout and carries its own `.gitignore`.
21. Patches MUST be built against committed code in a scratch copy, skipping findings whose code changed. Each is reviewed by an independent agent running tests where they exist. A patch MUST be written only if that agent vouches it addresses the finding, adds no vulnerability and leaves behaviour otherwise unchanged; otherwise a note explains why.
22. Patches MUST NEVER be applied automatically. They go to `patches/F<n>.patch` with a note.
23. On Fable, safeguards may flag requests; automatic fallback re-runs on Opus, or a refusal may end the request on some cloud deployments.

## Configuration & interfaces

| Env var | Effect |
|---|---|
| `ENABLE_PATTERN_RULES=0` | Disable per-edit check |
| `ENABLE_STOP_REVIEW=0` | Disable end-of-turn review |
| `ENABLE_COMMIT_REVIEW=0` | Disable commit review |
| `ENABLE_CODE_SECURITY_REVIEW=0` | Disable model-backed reviews |
| `SECURITY_GUIDANCE_DISABLE=1` | Disable the plugin |
| `SECURITY_REVIEW_MODEL`, `SG_AGENTIC_MODEL` | Review models |

Diagnostics: `~/.claude/security/log.txt`. `/workflows` shows scan detail.

## Failure modes & edge cases

- Reviews skip silently outside a git repository, without authentication, or if a YAML file cannot be parsed.
- Project-enabled plugin uninstalled by a user writes an override to local settings, so teammates are unaffected. Managed enablement is admin-only.
- `/claude-security` warns when `python3` is missing or too old.

## Changes since the snapshot

- 2.1.108: `/security-review` discoverable through the Skill tool.
- 2.1.314: session titles derived from prompt-based commands such as `/security-review`.
- `security-guidance` and `claude-security` plugins documented; introduced after the snapshot with no specific changelog version found.

## Open questions

- Whether `/security-review`'s tool allowances match the snapshot's list in 2.1.314.
- Whether it remains a built-in or has moved toward a plugin: the snapshot used a moved-to-plugin wrapper, while docs list it in commands.
- First shipped versions of both plugins.
