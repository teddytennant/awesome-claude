# CLI flags

**Status:** shipped
**Provenance:** both
**Sources:** docs `cli-reference`, `remote-control`, `ultrareview`, `plugins__cli-reference`, `agent-view`, `errors`, `env-vars`; `pub/help.txt`, `pub/subhelp.txt`; `comparison/cli-flags.md`; snapshot `main.tsx`, `cli/print.ts`, `utils/deepLink/`; changelog (versions inline)

## Purpose

Specify every top-level `claude` flag. Subcommand flags are in [cli-subcommands.md](cli-subcommands.md). The comparison counts 107 documented flag names across both levels, 33 of them new.

## Behaviour

1. `claude --help` does not list every flag. Absence from help MUST NOT imply a flag is unavailable.
2. A mistyped subcommand prints `Did you mean claude <x>?` and exits without starting.
3. `claude --dangerously-skip-permissions daemon <sub>` and the `--allow-` form route to `daemon` when leading, so aliases keep working. Any other leading flag does not route.
4. Flags marked print-only are ignored or rejected outside `-p`.

## Configuration & interfaces

**New** marks names not in the snapshot.

### Session and prompt

| Flag | Value | Notes | New |
|---|---|---|---|
| `[prompt]` | text | Starts interactive with this prompt. Invisible characters are removed before sending | |
| `-p`, `--print` | | Print and exit. Skips the trust dialog. Invalid settings files are skipped silently | |
| `-c`, `--continue` | | Most recent conversation here. Skips `-p`, SDK and `/loop` sessions unless `-p --continue`. Includes finished background sessions (2.1.257) | |
| `-r`, `--resume` | `[session]` | ID, name, `.jsonl` path, or picker. ID search spans all projects (2.1.223). Running background sessions open via attach (2.1.285) | |
| `--fork-session` | | New ID when resuming | |
| `--session-id` | uuid | Must be a valid UUID | |
| `-n`, `--name` | name | Display name | |
| `--from-pr` | `[value]` | PR number or URL, GitHub Enterprise, GitLab MR, Bitbucket | |
| `--no-session-persistence` | | Print only; not saved | |
| `--teleport` | `[session]` | Pull a cloud session | |
| `--cloud` | `[description\|id\|url]` | New cloud session; with `session_`/`cse_` ID or URL and `-p`, queues a message | New |
| `--remote` | | Deprecated alias of `--cloud` | |
| `--environment` | id | New cloud session on self-hosted `ccpool_...` (2.1.224) | New |
| `--ref` | branch | With `--environment`, base checkout | New |
| `--remote-control`, `--rc` | `[name]` | Interactive with Remote Control | |
| `--remote-control-session-name-prefix` | prefix | Default hostname; also env var | New |
| `--bg`, `--background` | | Background session; prints the ID. Not with `-p`. Trust checked first | New |
| `--exec` | command | With `--bg`, PTY shell job | New |
| `--desktop` | | Open Desktop and exit. Only `--continue`, `--resume <id>`, `--verbose`, debug flags (2.1.285) | New |
| `-w`, `--worktree` | `[name]` | `<repo>/.claude/worktrees/<name>`. `#N` or PR/MR URL branches from it | |
| `--tmux` | `[=classic]` | Needs `--worktree`; iTerm2 panes when available | |
| `--add-dir` | paths | Validated; most network paths refused (2.1.257); access only | |

### Model and behaviour

| Flag | Value | Notes | New |
|---|---|---|---|
| `--model` | alias or ID | Beats `model` and `ANTHROPIC_MODEL` | |
| `--fallback-model` | list | Comma chain; primary retried each user turn | |
| `--effort` | level | `low`..`max`, `ultracode` (2.1.203); not persisted. Env `CLAUDE_CODE_EFFORT_LEVEL` wins | |
| `--advisor` | model | Beats `advisorModel` | |
| `--agent`, `--agents` | | Agent for session; inline JSON, or with `-p` a file (2.1.281). Validated at startup | |
| `--teammate-mode` | mode | `in-process`, `auto`, `tmux`, `iterm2` | |
| `--betas` | list | API-key users | |
| `--autocompact` | `auto\|tokens` | 100k to 1M; session only (2.1.221) | New |
| `--prompt-suggestions` | `[value]` | With `-p`, stream-json and `--verbose` | New |
| `--brief` | | Enable SendUserMessage tool | |
| `--chrome`, `--no-chrome` | | Chrome integration | |
| `--ide` | | Auto-connect when one IDE | |

### System prompt

| Flag | Notes | New |
|---|---|---|
| `--system-prompt`, `--system-prompt-file` | Replace | |
| `--append-system-prompt`, `--append-system-prompt-file` | Append; both forms combine, file text first (2.1.283) | |
| `--system-prompt-snapshot <on\|off>` | Record once per conversation; `off` rebuilds per request. Off by default under `--bare` outside cloud and background | New |
| `--exclude-dynamic-system-prompt-sections` | Move per-machine context to first message | New |
| `--append-subagent-system-prompt`, `--append-subagent-system-prompt-file` | `-p`; exclusive; skip forked subagents (2.1.205, 2.1.261) | New |

A line holding only `__SYSTEM_PROMPT_DYNAMIC_BOUNDARY__` splits cached from dynamic text (2.1.275). Other changes take effect after compaction or in a new conversation.

### Permissions and tools

| Flag | Notes | New |
|---|---|---|
| `--permission-mode` | `default` (`manual`), `acceptEdits`, `plan`, `auto`, `dontAsk`, `bypassPermissions` | |
| `--dangerously-skip-permissions` | Same as bypass mode | |
| `--allow-dangerously-skip-permissions` | Adds bypass to the cycle | |
| `--allowedTools`, `--allowed-tools` | Auto-allow rules | |
| `--disallowedTools`, `--disallowed-tools` | Bare names remove tools; scoped rules deny matches | |
| `--tools` | Restrict built-ins; `""`, `"default"` or list | |
| `--permission-prompt-tool` | MCP tool to answer prompts; waits for its server | |
| `--permission-prompts` | `host` or `none`, print mode (2.1.259) | New |
| `--restricted` | Harness mode: no code tools or WebFetch unless named, no user or project settings, confined file tools, no bypass, no cloud sessions (2.1.248) | New |
| `--enable-auto-mode` | Removed in 2.1.111 | |

### Print-mode I/O

| Flag | Notes | New |
|---|---|---|
| `--output-format` | `text`, `json`, `stream-json` | |
| `--input-format` | `text`, `stream-json` | |
| `--json-schema` | Validated output | |
| `--include-partial-messages`, `--include-hook-events`, `--replay-user-messages` | Stream-json options | |
| `--forward-subagent-text` | Subagent text and thinking in stream (2.1.211) | New |
| `--max-budget-usd`, `--max-turns` | Limits | |
| `--init`, `--init-only`, `--maintenance` | Setup hooks | |
| `--file` | `file_id:path` downloads | |

### Configuration, MCP, plugins

| Flag | Notes | New |
|---|---|---|
| `--settings` | File (max 2 MiB) or JSON; overrides same keys | |
| `--setting-sources` | `user,project,local` | |
| `--mcp-config`, `--strict-mcp-config` | With `-p`, waits for servers up to `MCP_TIMEOUT` (2.1.221) | |
| `--plugin-dir` | Directory, `.zip` or folder of plugins (2.1.265) | |
| `--plugin-url` | `.zip` URL for the session (2.1.129) | New |
| `--channels`, `--dangerously-load-development-channels` | Research preview | |
| `--disable-slash-commands` | Disable all commands and skills | |
| `--bare` | Minimal; sets `CLAUDE_CODE_SIMPLE` | |
| `--safe-mode` | Disable customisations; sets `CLAUDE_CODE_SAFE_MODE` (2.1.169) | New |

### Display and diagnostics

| Flag | Notes | New |
|---|---|---|
| `--ax-screen-reader` | Flat text (docs: 2.1.181; announced 2.1.208) | New |
| `--verbose` | Beats `viewMode` | |
| `-d`, `--debug` | Filter binds only in `=` form: `--debug='mcp,startup'` or `'!mcp'` | |
| `--debug-file` | Implies debug; beats `CLAUDE_CODE_DEBUG_LOGS_DIR` | |
| `-v`, `--version`; `-h`, `--help` | | |

### Snapshot-only flag names

| Names | Fate |
|---|---|
| `--afk`, `--delegate-permissions`, `--dangerously-skip-permissions-with-classifiers`, `--agent-teams`, `--tasks`, `--hard-fail` | Internal-only; not public |
| `--agent-id`, `--agent-name`, `--agent-color`, `--agent-type`, `--team-name`, `--plan-mode-required`, `--parent-session-id` | Hidden teammate plumbing; undocumented |
| `--sdk-url` | Hidden; remote I/O plumbing, named in a 2.1.69 crash fix; undocumented |
| `--assistant`, `--proactive`, `--messaging-socket-path` | Gated; undocumented |
| `--thinking`, `--max-thinking-tokens`, `--task-budget`, `--workload`, `--enable-auth-status`, `--mcp-debug`, `--debug-to-stderr` | Hidden. `--thinking disabled` is named in a 2.1.166 note |
| `--resume-session-at`, `--rewind-files` | Hidden print-mode SDK flags; `--rewind-files` in a changelog fix |
| `--deep-link-origin`, `--deep-link-repo`, `--deep-link-last-fetch`, `--handle-uri`, `--prefill` | Internal deep-link plumbing |
| `--port`, `--host`, `--auth-token`, `--unix`, `--workspace`, `--idle-timeout`, `--max-sessions` | Gated `claude server`; undocumented |
| `--local` | Gated `claude ssh` test flag; undocumented |
| `--owner`, `--clear-owner`, `--subject`, `--description`, `--status`, `--list`, `--pending` | Internal `claude task` options. `--description` also exists on `plugin init` |
| `--debug-brk`, `--inspect`, `--use-system-ca`, `--use-openssl-ca` | Runtime options the code detects; not CLI options |
| `--output` | Internal completion and export use |
| `--cowork` | Hidden plugin path option; undocumented |
| `--available`, `--claudeai`, `--client-secret`, `--force`, `--keep-data`, `--scope`, `--sparse`, `--transport` | Still public, on subcommands |
| `--safe` | Substring of `--safe-mode`; false match |
| `--flag` | False match on comments and docs |

The comparison also lists `--allowed` and `--disallowed` as present in both. No such flags exist: they are truncated matches of `--allowedTools` and `--disallowedTools`.

## Failure modes & edge cases

- `--bg` with `-p` is rejected.
- `--bare` plus unset snapshot flag leaves prompt recording off.
- `--debug hooks` (space) enables debug without a filter.
- `--desktop --resume` takes only an ID.
- `--append-subagent-system-prompt` and its file form cannot combine.

## Changes since the snapshot

- 33 new names (see above and the subcommands spec).
- 2.1.111: `--enable-auto-mode` removed. 2.1.200 (per docs): `manual` alias. 2.1.285: `--desktop`, and attach on resume.

## Open questions

- Which hidden snapshot flags remain accepted.
- `--tmux` value handling beyond `classic`.
- `--ax-screen-reader` first-version discrepancy (docs 2.1.181, changelog 2.1.208).
