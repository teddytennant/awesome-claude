# Plugin Evals

**Status:** shipped (early-access gating messages exist in docs)
**Provenance:** post-leak (since v2.1.269, 2026-09-11)
**Sources:** docs `plugin-evals`, `plugins__cli-reference`, `plugins__measure`, `skills`; changelog 2.1.269, 2.1.283, 2.1.299.

## Purpose

`claude plugin eval` measures whether a plugin changes Claude's behaviour, by running each case in fresh isolated non-interactive sessions, scoring with graders, and comparing against a no-plugin baseline. It produces a reproducible JSON result and an HTML report, and exits non-zero under a threshold for CI use. It is separate from the `skill-creator` plugin's `evals/evals.json` format; the two are not interchangeable.

## Behaviour

### Requirements

1. MUST run on v2.1.269 or later. If git is installed, it MUST be 2.31 or later, or the command stops before any case (v2.1.283). No git is acceptable.
2. The target MUST have `plugin.json` or `.claude-plugin/plugin.json`, or be a skills-directory plugin.
3. Runs and judges use the caller's credentials and provider, and count against usage.

### Targets

| Target | Runs |
| :- | :- |
| Plugin root (`.`), or omitted | Every case in its eval directory |
| A `prompt.md` or `case.yaml` | That case, with its enclosing plugin |
| `name` or `name@marketplace` | Installed plugin's cases; results under `./evals/results/` |
| `name@skills-dir` | The same, for a skills-directory plugin |

4. A plugin from a local-path marketplace that no session could load is refused with `cannot be evaluated where sessions load it`.
5. The target MUST come before `--tag`, `--allow-tools` and `--json`, which would otherwise consume it.

### Execution

6. Each run MUST be a fresh non-interactive session with only the plugin loaded, ending at completion, turn cap or timeout.
7. MUST NOT load user settings, hooks, `CLAUDE.md`, personal MCP servers, other plugins, memory, or skills. Project `.claude/`, `CLAUDE.md` and `.mcp.json` MUST NOT load, including ones a scaffold writes.
8. Managed settings still apply. The Artifact tool MUST be off. The eval directory MUST be unreadable to the agent.
9. Runs MUST never prompt. Built-in tools needing an ungranted permission MUST be removed from the session. Listed `allowed_tools` from `Read`, `Glob`, `Grep`, `NotebookRead`, `Skill`, `AskUserQuestion`, `Agent`, `TodoWrite`, `TaskCreate`, `TaskGet`, `TaskList`, `TaskUpdate`, `TaskStop` are allowed; others need `--allow-tools`, which applies to all cases. `allowed_tools` and skill `allowed-tools` MUST NOT widen the grant.
10. `--disallow-tools` and case `disallowed_tools` keep tools such as `Agent` out (v2.1.299).
11. Any `Bash` grant MUST run under the OS sandbox: writes confined to the workspace, home and config unreadable, network limited to granted `WebFetch(domain:...)` domains. Bash or PowerShell grants without a sandbox backend MUST refuse each run. No network sandbox applies outside shell commands.
12. The child environment inherits only an allowlist (basics, proxy and certificate settings, provider selection and auth). Case `env` keys MUST match `EVAL_[A-Z0-9_]*`, else the run fails.

### Trust

13. The first run on a directory MUST ask `Trust this plugin directory?` unless already trusted. A yes inside a git repo trusts the repo, for interactive sessions too. Without a terminal, or under `--json`, the run is refused with exit 1 unless `--trust-plugin`.
14. `--scaffold`, `--allow-tools` and real-server flags gate code that would otherwise not run. Hook and real-server scores are advisory outside isolation, since they run unsandboxed and could alter files graders read.

### Scoring

15. A run's score MUST be the weighted fraction of graders passed. A case's score is the mean of with-arm runs. A case passes at or above `--threshold`.
16. Unless ablation is off, each case MUST also run with no plugin. `Δ` is with minus without.
17. One arm runs under `--ablation none`, for a path-target case with `context.history_file`, or when no plugin was located. The latter print `single-arm (no Δ)` notices.
18. In two-arm mode, graders that could never pass without the plugin are excluded from scores in both arms and reported with `scored: false`. If all would be excluded, all are scored. `arm: both` forces scoring; `arm: with-only` excludes. `--ablation none` excludes nothing.
19. `Δ` MUST NOT affect exit code. Baseline scores never decide a case, but a baseline API error can still fail the command.
20. A run ending on an API error scores 0 ungraded. A run aborted by a mock scores 0 with `aborted` set. Other errors may still be graded.
21. A run counts cases × runs × arms, plus three judge calls per `llm` or `baseline` grader per run.

### Mocks

22. Real plugin MCP servers MUST NOT start by default. Each is replaced by a substitute under its own name. Mocked tools answer from files and need no grant. Unmocked tools are unavailable.
23. `--allow-real-servers` starts real processes for servers with no mock. `--mocks off` ignores mocks and starts all. Real tools also need a grant.
24. `fixed` mocks return the body, with `{{input.<field>}}` and `{{file:fixtures/{input.<field>}.json}}` substitution. `error: true` returns a tool error.
25. `agent` mocks have the judge answer from the body as instructions. Calls share a budget of four times `max_turns` per run; exceeding it aborts with score 0. Answers can be saved and replayed with `--mocks record`.
26. `expect` validates input by dotted path against a type name, `/regex/`, literal or list; a violation aborts. `abort_when` lists agent-mock abort conditions.
27. `_server.md` is one agent mock for tools in `tools:`, with `<tool>.md` overriding. `_tools.json` is a saved `tools/list` for real schemas.

### Results

28. `aggregate-result.json` and `report.html` MUST go to `<eval dir>/results/<timestamp>/` unless `--output-dir`. `report.html` is self-contained with no external requests.
29. `--json [path]` silences progress; a path must end in `.json`. Report publishing can be disabled with `--no-publish`, and forced with `--publish-report`. Publishing failures MUST NOT alter the exit code.
30. `--max-cost-usd` is checked before each run against list-price estimates; started runs finish, so spend can pass it. If runs were left unstarted, exit 2.

## Configuration & interfaces

### Options

| Option | Default |
| :- | :- |
| `--runs <n>` | Case `runs`, else 3 |
| `-j, --concurrency` | 1 (1 to 8) |
| `--model` | Case `model`, `ANTHROPIC_MODEL`, default |
| `--judge-model` | Background model |
| `--ablation none\|with-without` | Per case |
| `--threshold <0..1>` | 1.0 |
| `--max-cost-usd` | None |
| `--allow-tools`, `--disallow-tools` | None |
| `--scaffold`, `--no-scaffold`, `--trust-plugin`, `--allow-real-servers`, `--keep-temp` | Off |
| `--mocks record\|off` | `record` |
| `--eval-dir` | `experimental.evals`, else `evals` |
| `--case <glob>`, `--tag <tag>` | Filters |
| `--json`, `--output-dir`, `--no-publish`, `--publish-report`, `--report`, `--verbose` | Output |

`claude plugin eval init` interviews and writes cases; `--bare <name>` writes a template; `-i` requires the interview. It needs a terminal, so CI uses `--bare`.

### Exit codes

| Code | Meaning |
| :- | :- |
| 0 | All cases at threshold, nothing else failed |
| 1 | Case below threshold, load error, no cases, start failure, API-error run, untrusted directory, invalid option, unwritable `--json` |
| 2 | Partial: cost ceiling or rejected credential; `partial: true` is written |
| 130, 143 | Interrupted, terminated; partial results on 130 |

### Case format

`evals/<case>/prompt.md` frontmatter: `schema_version` (`1.1`), `name`, `description`, `tags`, `plugins`, `runs` (1 to 50), `expected_outcome`, `model`, `max_turns` (default 10, max 200), `timeout_seconds` (default 300, max 3600), `allowed_tools`, `disallowed_tools`, `append_system_prompt`, `env`. `case.yaml` adds `context.scaffold_script` (120 s, `--scaffold` only, non-zero fails), `context.history_file`, `context.add_dirs`, `execution.prompt`, `graders`.

### Graders

| Type | Passes when |
| :- | :- |
| `regex` | `pattern` (JavaScript, `flags`) found; `match: not_contains`, `count:N` |
| `tool_used` | Matching call count between `min` (1) and `max`; both 0 asserts absence |
| `tool_order` | `before` precedes `after`; both called |
| `file_exists` | A created file matches `path`; `exists: false` inverts |
| `llm` | At least two of three judge votes pass `criteria`, optional `focus` |
| `baseline` | Judge finds the run at least as good as `baseline_file` |

Common keys: `type`, `weight` (1), `arm`. Targets: `last_message` (default), `trace` (JSON per line; `llm` sees first and last 12 messages), `files` (created paths only), `{source: file, path}`, `mock_calls`. An `llm` judge sees PNG, JPEG, GIF, WebP as images and refuses other binaries.

### JSON result

`partial`, `partialReason` (`cost_ceiling`, `interrupted`, `auth_failed`), `aggregates.{overallScore,casesPassed,casesTotal,meanDelta}`, `cases[].{name,aggregates.{score,delta},arms.{with,without}[].{error,aborted,skippedPaidGraders}}`, `costUsd`, `durationSeconds`, `claudeVersion`.

## Failure modes & edge cases

- Inline `(?i)` is unsupported; use `flags: i`.
- A `trace` regex sees JSON-escaped text.
- `file_exists` ignores scaffolded and merely modified files.
- `max_turns` exhaustion is a run error, usually lowering the score.
- `--json output path must end in .json`.
- Troubleshooting lists early-access and unavailable messages.

## Changes since the snapshot

- v2.1.269: `claude plugin eval` added.
- v2.1.283: git 2.31 minimum.
- v2.1.299: `--disallow-tools`, `disallowed_tools`.

## Open questions

- Conditions for the "early access" and "unavailable" states are not reviewed in full here.
- `--report` semantics are listed only in `--help`.
- Where published reports go is not specified in the sections reviewed.
