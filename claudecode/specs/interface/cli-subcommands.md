# CLI subcommands

**Status:** shipped
**Provenance:** both
**Sources:** docs `cli-reference`, `plugins__cli-reference`, `mcp`, `remote-control`, `ultrareview`, `agent-view`, `self-hosted-environments-reference`, `claude-directory`, `auto-mode-config`, `claude-apps-gateway`; `pub/help.txt`, `pub/subhelp.txt`; `comparison/cli-flags.md`; snapshot `main.tsx`, `cli/handlers/`; changelog (versions inline)

## Purpose

Specify every `claude <subcommand>` and its flags. **New** means not in the snapshot.

## Behaviour

1. Subcommands run without an interactive session unless stated.
2. Global flags before a subcommand are not always honoured. `remote-control` drops those it cannot carry.

## Configuration & interfaces

### Sessions and background

| Command | Flags | Behaviour | New |
|---|---|---|---|
| `agents` | `--add-dir`, `--agent`, `--all`, `--allow-dangerously-skip-permissions`, `--cwd`, `--dangerously-skip-permissions`, `--effort`, `--json`, `--mcp-config`, `--model`, `--permission-mode`, `--plugin-dir`, `--settings` | Agent view. `--json` prints active sessions; `--json --all` adds completed. Needs a terminal to open. Snapshot `agents` only listed configured agents | reshaped |
| `attach <id\|name>` | | Open a background session here. Partial name (2.1.290) | New |
| `logs <id\|name>` | | Recent output | New |
| `stop\|kill <id>` | | Stop, keep conversation | New |
| `rm <id>` | `--discard-unpushed <commit>@<worktree-id>`, `--force-remove-worktree <worktree-id>` | Remove session; a refusal prints the exact flag (2.1.260, 2.1.268) | New |
| `respawn [id]` | `--all` | Restart with current version | New |
| `daemon status` | | State, version, socket dir, workers. Exit 1 if not running | New |
| `daemon logs` | | Follow `~/.claude/daemon.log` | New |
| `daemon run` | | Foreground supervisor | New |
| `daemon stop` | `--any`, `--keep-workers` | `--any` confirms on-demand supervisor | New |
| `remote-control`, `rc` | `--name`, `--remote-control-session-name-prefix`, `-c`/`--continue`, `--session-id`, `--spawn <same-dir\|worktree\|session>`, `--capacity <N>` (32), `--[no-]create-session-in-dir`, `--permission-mode`, `--chrome`/`--no-chrome`, `-d`/`--debug[=filter]`, `--debug-file`, `--verbose` | Server mode. `--sandbox` flags removed 2.1.300 and now error. Asks for trust (2.1.284). Resume works about four hours | reshaped |
| `ultrareview [target]` | `--json`, `--timeout <minutes>` (45), `--post`, `--no-post`, `--trust-workspace` | Cloud review, stdout findings; 0, 1, 130 exit codes. Requires trust (2.1.309) | New |
| `import [source]` | `--dry-run`, `--yes` | Interactive session running `/import` | New |
| `purge [path]` | `--dry-run`, `-y`/`--yes`, `-i`/`--interactive`, `--all` | Delete local project state; this computer only. `claude project purge` still works | New |

### Account and install

| Command | Flags | Behaviour | New |
|---|---|---|---|
| `auth login` | `--email`, `--sso`, `--console` | Sign in | |
| `auth logout` | | Sign out | |
| `auth status` | `--json` (default), `--text` | Exit 0 if signed in, 1 if not. JSON has `authMethod` (`none`, `claude.ai`, `oauth_token`, `api_key`, `api_key_helper`, `third_party`) and `configDirectory` (2.1.268) | |
| `setup-token` | | Long-lived token, printed not saved. Rejects extra args (2.1.234) | |
| `install [target]` | `--force` (snapshot) | Native binary: `stable`, `latest` or version | |
| `update`, `upgrade` | | Update, through the package manager where relevant | |
| `doctor` | | Read-only diagnostics; see [doctor-and-diagnostics.md](doctor-and-diagnostics.md) | |

### Auto mode

| Command | Flags | Behaviour | New |
|---|---|---|---|
| `auto-mode defaults` | `--label <prefix>` | Rules as JSON (2.1.208) | |
| `auto-mode config` | | Effective config | |
| `auto-mode critique` | `--model` | Review custom rules | |
| `auto-mode reset` | `-y`/`--yes` | Remove `autoMode` from user settings (2.1.212) | New |

### MCP

| Command | Flags | Behaviour |
|---|---|---|
| `mcp add <name> <commandOrUrl> [args...]` | `--transport`, `-s`/`--scope`, `-e`/`--env`, `--header`, `--client-id`, `--client-secret`, `--callback-port` | `--` separates server arguments |
| `mcp add-json <name> <json>` | `-s`, `--client-secret` | stdio, SSE, HTTP, WebSocket |
| `mcp add-from-claude-desktop` | `-s` | Mac and WSL |
| `mcp get <name>`, `mcp list` | | Pending `.mcp.json` servers are not connected (2.1.196); disabled show `⊘ Disabled` |
| `mcp remove <name>` | `-s` | Deletes stored OAuth tokens and client registration |
| `mcp login <name>` | `--no-browser` | OAuth without the panel (2.1.186, **New**) |
| `mcp logout <name>` | | Clear credentials (**New**) |
| `mcp serve` | `-d`, `--verbose` | Run as an MCP server |
| `mcp reset-project-choices` | | Reset `.mcp.json` approvals |

### Plugins

`claude plugin` and `claude plugins`. Exit 0 or 1 unless stated.

| Command | Aliases | Flags |
|---|---|---|
| `init <name>` | `new` | `--description`, `--author`, `--author-email`, `--with <components...>`, `-f`/`--force` |
| `install <plugin>` | `i` | `-s`, `--config <key=value>`, `-y`/`--yes`, `--accept-command <sha256>`, `--json`, `--marketplace <source>` |
| `uninstall <plugin>` | `remove`, `rm` | `-s`, `--keep-data`, `--prune`, `-y`, `--json` |
| `enable <plugin>` | | `-s`, `--json` |
| `disable [plugin]` | | `-a`/`--all`, `-s`, `--json` |
| `update <plugin>` | | `-s` (also `managed`), `-y`, `--accept-command`, `--json` |
| `list` | | `--json`, `--available`, `--data-size [plugin]` |
| `details <name>` | | Inventory and token cost |
| `configure <plugin>` | | `--values-stdin`, `--json`; qualified name only |
| `prune` | `autoremove` | `-s`, `--dry-run`, `-y` |
| `eval [target]` | | `--runs`, `-j`/`--concurrency`, `--model`, `--judge-model`, `--ablation`, `--threshold`, `--max-cost-usd`, `--allow-tools`, `--scaffold`, `--trust-plugin`, `--mocks`, `--eval-dir`, `--json [path]`, `--no-publish`. Exits 0, 1, 2, 130, 143 |
| `eval init` | | `--bare`, `-i`/`--interactive`, `--eval-dir` |
| `tag` | | `--push`, `--dry-run`, `-f`, `-m`, `--remote` |
| `test` | | Listed in docs |
| `validate <path>` | | `--strict`, `--json`. Exit 2 on unexpected error |
| `marketplace add <source>` | | `--scope`, `--sparse`, `--claudeai`, `--json` |
| `marketplace list` | | `--json` |
| `marketplace remove` | `rm` | `--scope`, `--json` |
| `marketplace update [name]` | | `--json`; refuses `--json` with no name |

`--json` on plugin commands prints one object on the last stdout line, with `command`, `outcome`, `message` and optional `failureCode`.

### Admin servers

| Command | Flags | Behaviour | New |
|---|---|---|---|
| `gateway` | `--config <file>` required | Claude apps gateway server (2.1.195 per docs) | New |
| `self-hosted-runner` | About 40 flags in the self-hosted reference, such as `--environment-secret-file`, `--base-dir`, `--capacity`, `--client-label`, `--configure-git`, `--exec-path`, `--health-port`, `--hooks-dir`, `--log-file`, `--log-level`, `--trust-workspace`, `--use-anthropic-git-proxy` | Register and host cloud sessions (2.1.224) | New |
| `self-hosted-runner setup`, `doctor`, `orchestrator` | Orchestrator: `--hook-concurrency`, `--hook-timeout`, `--expected-spawn-seconds`, `--min-idle`, `--shutdown-drain-sec`, `--debug-dir`, and `--scm-connector-*` | Walkthrough, diagnosis, on-demand runners | New |

### Snapshot-only subcommands

| Name | Gate | Fate |
|---|---|---|
| `server`, `open <cc-url>` | Build gate | Undocumented |
| `ssh <host> [dir]` | Build gate | Undocumented |
| `assistant [sessionId]` | Build gate | Undocumented |
| `completion <shell>` | Hidden | Undocumented |
| `up`, `rollback`, `log`, `error`, `export`, `task *` | Internal only | Not public |

## Failure modes & edge cases

- `plugin install` without a TTY and no `-y` or `--accept-command` refuses a marketplace-declared command. `-y` is ignored when Claude runs the command.
- `/plugin install <source>` differs from the shell form and reports marketplace not found.
- `--env` directly before the server name absorbs the name as a pair.
- `ultrareview` in CI needs `--trust-workspace`.

## Changes since the snapshot

- New groups: `attach`, `logs`, `stop`, `rm`, `respawn`, `daemon`, `gateway`, `self-hosted-runner`, `purge`, `import`, `ultrareview`.
- `agents` changed from a list to agent view.
- `project purge` renamed (2.1.288).
- `--sandbox` removed from `remote-control` (2.1.300).

## Open questions

- Full `self-hosted-runner` list is delegated to its reference page.
- Whether `install --force` is still accepted.
- `plugin test` flags.
- Flags of `claude gateway` beyond `--config`.
