# Slash commands catalogue

**Status:** shipped
**Provenance:** both
**Sources:** docs `commands`, `skills`, `interactive-mode`, `plugins__cli-reference`; `comparison/commands.md`; snapshot `commands.ts`, `commands/`, `skills/bundled/`; changelog (versions inline)

## Purpose

List all 120 documented command names as of 2.1.314, with arguments, kind, aliases, snapshot presence and required behaviour.

## Behaviour

Legend. **Kind:** B built-in, S bundled skill, W bundled workflow, R removed (documented tombstone). **Snap:** `yes` public or ordinary in snapshot; `gated` named in snapshot but behind a build gate, internal list or stub; `no` absent by name. Comparison counts: 81 both, 39 new; `gated` is a subset of whichever side the comparison placed it.

| Command | Args | Kind | Aliases | Snap | Purpose and required behaviour |
|---|---|---|---|---|---|
| `/add-dir` | `<path>` | B | | yes | Add a working directory. Tab-completes. Refuses most network paths. Fires `DirectoryAdded`. Grants file access, not `.claude/` discovery. Mid-turn: confirm now, usable by next tool call |
| `/advisor` | `[model\|off]` | B | | yes | Enable or disable advisor. `fable`, `opus`, `sonnet` or ID. No arg opens picker; prints current when no terminal or over Remote Control |
| `/agents` | | B | | yes | Prints a reminder to ask Claude or edit `.claude/agents/`. Was a management UI through 2.1.197 |
| `/artifact-capabilities` | | S | | no | Reference for artifact runtime capabilities |
| `/artifact-diagramming` | | S | | no | Diagramming guidance for artifacts (2.1.221) |
| `/artifacts` | | B | | no | List own and shared artifacts; attach, open or copy link |
| `/auto-mode-setup` | | B | | no | Draft `autoMode.environment` from the project, review, save to user settings (2.1.228; Enterprise and Console 2.1.283) |
| `/autocompact` | `[auto\|<tokens>]` | B | | no | Set auto-compact window, saved to user settings. No arg opens dialog (2.1.221) |
| `/autofix-pr` | `[prompt]` | B | | gated | Cloud session watches the branch's PR and pushes fixes. Needs `gh` |
| `/background` | `[prompt]` | B | `/bg` | no | Detach session as a background agent. Optional last instruction |
| `/batch` | `<instruction>` | S | | yes | Decompose into 5 to 30 units and run a subagent per worktree after plan approval |
| `/branch` | `[name]` | B | | yes | Branch the conversation and switch into it; original is resumable |
| `/btw` | `[question]` | B | | yes | Side question, no tools, not in history. Overlay keys: Space, Enter, Esc dismiss; Up/Down scroll; Shift+arrows or `[` `]` history; `c` copy; `f` fork; `x` clear. Bare form reopens latest. Replays newest 20 exchanges |
| `/bug` | `[report]` | B | `/share` | yes | Report with consent screen. Anthropic first-party, else local archive under `~/.claude/feedback-bundles/` |
| `/cd` | `<path>` | B | | no | Move session to a new directory, keeping the conversation (2.1.169) |
| `/chrome` | | B | | yes | Claude in Chrome settings, including browser choice |
| `/claude-api` | `[migrate\|upgrade\|api-version\|managed-agents-onboard\|managed-agents-secure\|prompt-audit\|cost-optimize\|build-eval\|hillclimb\|preserved-thinking-migration]` | S | | gated | Claude API reference for the project's language; auto-activates on SDK imports |
| `/claude-in-chrome` | `[task]` | S | | gated | Carry out a browser task |
| `/clear` | `[name]` | B | `/reset`, `/new` | yes | New empty conversation; name labels the old one for `/resume`. Restorable from rewind in the same process |
| `/code-review` | `[low..max\|ultra] [--fix] [--comment] [--max-findings n\|all\|default] [pr#\|branch\|path]` | S | `/review` | no | Review for correctness bugs. `--comment` posts to GitHub or GitLab; `--post` with `ultra`. Last level is reused |
| `/color` | `[color\|default]` | B | | yes | Prompt bar colour; random if empty; syncs over Remote Control; works in `-p` |
| `/compact` | `[instructions]` | B | | yes | Summarise conversation |
| `/config` | `[key=value ...]` | B | `/settings` | yes | Settings panel, or set keys directly, also in `-p` and from mobile. Cannot turn on confirmation-required settings. `--help` lists keys. Esc saves |
| `/context` | `[all]` | B | | yes | Coloured grid of context use with suggestions. Fullscreen collapses the breakdown unless `all` |
| `/copy` | `[N]` | B | | yes | Copy Nth-latest response. Picker for code blocks and quotes; `w` writes to a file |
| `/cost` | | B | | yes | Alias behaviour for `/usage` |
| `/dataviz` | `[request]` | S | | no | Chart design guidance with palette validator (2.1.198) |
| `/debug` | `[description]` | S | | yes | Enable debug logging from this point and diagnose from the log |
| `/deep-research` | `<question>` | W | | no | Fan out searches, cross-check, write a cited report. Manual only (2.1.218) |
| `/design` | `[brief]` | S | | no | Draft mockups as a Claude Design artifact (2.1.265). `/design consent` and `/design revoke` manage access |
| `/design-login` | | B | | no | Authorise design-system access. Standalone site closes by 2026-12-14 |
| `/design-sync` | `[hint]` | S | | no | Convert and upload a React design system. Same closure |
| `/desktop` | | B | `/app` | yes | Continue in Desktop. macOS or x64 Windows, subscription |
| `/diff` | | B | | yes | Fullscreen: side panel. Classic: dialog. From `cc-plugin-diff`; older viewer if that mod is off. Panel needs git, 110+ columns, 2.1.287+ |
| `/doctor` | `[prompt-audit [path]]` | S | `/checkup` | yes | Setup checkup, fixes after confirmation (skill since 2.1.205). `prompt-audit` from 2.1.283 |
| `/effort` | `[level\|auto\|status\|ultracode [on\|off]]` | B | | yes | Set effort, or slider. `max` is session-only. Works in `-p` (2.1.205) |
| `/exit` | | B | `/quit` | yes | Exit; detaches in an attached background session |
| `/export` | `[filename]` | B | | yes | Plain-text export to file or clipboard |
| `/fast` | `[on\|off]` | B | | yes | Toggle fast mode, applied without waiting |
| `/feedback` | `[report]` | B | | yes | Same dialog as `/bug`; no arg may open Claude-drafted feedback queue |
| `/fewer-permission-prompts` | | S | | no | Scan transcripts and add a read-only allowlist to project settings |
| `/focus` | `[on\|off]` over Remote Control | B | | no | Toggle focus view, sticky. Fullscreen only (2.1.110). Remote form affects session only (2.1.281) |
| `/fork` | `[prompt]` | B | | gated | Copy conversation to a new background session (2.1.212). In snapshot, an alias of `/branch` or a gated command. Falls back to a forked subagent with agent view off |
| `/goal` | `[condition\|clear]` | B | | no | Keep working across turns until met (2.1.139). `clear`, `stop`, `off`, `reset`, `none`, `cancel` remove |
| `/heapdump` | | B | | yes | Hidden. Writes `.heapsnapshot` and `-diagnostics.json`; only the latter is safe to share |
| `/help` | | B | | yes | Help and commands |
| `/hooks` | | B | | yes | View hooks |
| `/ide` | | B | | yes | IDE integrations and status |
| `/import` | `[codex\|gemini\|cursor] [--dry-run] [--yes]` | B | | no | Import config from other agents. Not on third-party providers or without flag fetch (Cursor from 2.1.265) |
| `/init` | | B | | yes | Create `CLAUDE.md`; offers `/import` if other agents are found |
| `/insights` | | B | | yes | HTML report of recent sessions; not in cloud sessions |
| `/install-github-app` | | B | | yes | GitHub App and Actions setup. github.com only; prints a notice for gitlab.com and bitbucket.org |
| `/install-slack-app` | | B | | yes | OAuth in browser |
| `/keybindings` | | B | | yes | Open or create the file |
| `/list-agents` | | B | `/peers` | no | List messageable subagents, teammates, sessions (2.1.224; teammates 2.1.239). `/peers` was gated in snapshot |
| `/login` | | B | | yes | Sign in |
| `/logout` | | B | | yes | Sign out |
| `/loop` | `[interval] [prompt]` | S | `/proactive` | gated | Repeat a prompt; self-paced if no interval; default prompt or `loop.md` if none. Esc cancels wakeups |
| `/mcp` | `[reconnect (<server>\|all)\|enable\|disable [<server>\|all]]` | B | | yes | MCP list and OAuth; text summary in `-p` |
| `/memory` | | B | | yes | Edit `CLAUDE.md`, toggle and view auto memory |
| `/mobile` | | B | `/ios`, `/android` | yes | QR code (single, claude.ai/mobile, 2.1.271) |
| `/model` | `[model]` | B | | yes | Switch and save default. `s` for session only; arrows adjust effort. In `-p`, not saved |
| `/output-style` | `[style]` | B | | yes | List or switch styles (2.1.269). Hidden deprecated stub in snapshot |
| `/passes` | | B | | yes | Share a free week; eligible accounts only |
| `/permissions` | | B | `/allowed-tools` | yes | Rules by scope, working directories, denials, Auto mode tab |
| `/plan` | `[description]` | B | | yes | Enter plan mode, optionally start a task |
| `/plugin` | `[subcommand]` | B | `/plugins`, `/marketplace` | yes | Panel, or `list`, `install`, `enable`, `disable`, `uninstall`, `configure`, `validate`, `tag`, `manage`, `stats`, `marketplace ...`, `help` |
| `/plugin-authoring` | | S | | no | Mod-writing reference, from a built-in plugin (2.1.287) |
| `/powerup` | | B | | no | Interactive feature lessons (2.1.90) |
| `/pr-comments` | `[PR]` | R | | yes | Removed in 2.1.91 |
| `/privacy-settings` | | B | | yes | Pro and Max only |
| `/radio` | | B | | no | Open Claude FM in browser, or print URL |
| `/rate-limit-options` | | B | | yes | Options at a usage limit: wait, credits, upgrade. Opens itself once per reset window |
| `/recap` | | B | | no | One-line summary, capped at 400 characters (2.1.108) |
| `/release-notes` | | B | | yes | Version picker (2.1.92); output stays out of context |
| `/reload-plugins` | `[--force]` | B | | yes | Reload plugins; warns and skips if MCP tool changes would break cache, unless forced |
| `/reload-skills` | | B | | no | Re-scan skill directories (2.1.152) |
| `/remote-control` | | B | `/rc` | gated | Make the session available from claude.ai |
| `/remote-env` | | B | | yes | Default cloud environment |
| `/rename` | `[name]` | B | | yes | Rename, or auto-generate. Control characters become spaces; cap 200 (2.1.221). Works in `-p` |
| `/restart` | | B | `/update` | no | Restart and resume after an update. Pro or Max native on macOS or Linux, not WSL (2.1.288). Refuses during surviving work or Remote Control |
| `/resume` | `[session]` | B | `/continue` | yes | Picker or by ID or name. Attaches to a running background session (2.1.285) |
| `/review` | as `/code-review` | B | | yes | Alias of `/code-review` (2.1.223) |
| `/rewind` | | B | `/checkpoint`, `/undo` | yes | Rewind conversation or code, or summarise from a message |
| `/run` | | S | | no | Launch and drive the app |
| `/run-skill-generator` | | S | | no | Record a per-project launch recipe |
| `/sandbox` | | B | | yes | Toggle sandbox, where supported |
| `/schedule` | `[description]` | S | `/routines` | gated | Create or run cloud scheduled tasks |
| `/scroll-speed` | | B | | no | Interactive wheel speed. Fullscreen, not JetBrains (2.1.139) |
| `/security-review` | | B | | yes | Review branch diff against origin's default branch; needs `origin` |
| `/setup-bedrock` | | B | | no | Bedrock wizard. Hidden until `CLAUDE_CODE_USE_BEDROCK=1` |
| `/setup-vertex` | | B | | no | Vertex wizard. Hidden until `CLAUDE_CODE_USE_VERTEX=1` |
| `/simplify` | `[target]` | S | | yes | Four cleanup agents, then apply. No bug hunting (2.1.154) |
| `/skill-doctor` | | B | | no | Skill context cost and use (changelog 2.1.261; docs floor 2.1.252). Needs flag fetch |
| `/skills` | | B | | yes | Filter; `t` sort by tokens; Space or Enter cycle visibility; Esc save |
| `/slides` | `[brief]` | S | | no | Claude Slides artifact (2.1.265) |
| `/stats` | | B | | yes | Alias behaviour for `/usage`, opening Stats |
| `/status` | | B | | yes | Settings at Status tab; `Session kind` row (2.1.221); immediate |
| `/statusline` | `[description]` | S-like prompt | | yes | Configure status line |
| `/stickers` | | B | | yes | Order stickers |
| `/stop` | | B | | no | Stop the attached or peeked background session; transcript and worktree kept |
| `/subtask` | `<task>` | B | | no | Forked background subagent; result returns here. Unavailable with agent view off |
| `/tasks` | | B | `/bashes` | yes | Background work; system tasks fold under one row (2.1.285) |
| `/team-onboarding` | | B | | no | Guide from last 30 days of use (2.1.101); share link on Team and Enterprise |
| `/teleport` | | B | `/tp` | gated | Pull a cloud session here. Subscription |
| `/terminal-setup` | | B | | yes | Shift+Enter binding, or Apple Terminal and iTerm2 fixes |
| `/theme` | | B | | yes | Theme picker |
| `/tui` | `[default\|fullscreen]` | B | | no | Set renderer and relaunch (2.1.110) |
| `/ultraplan` | `<prompt>` | R | | gated | Removed 2.1.222 |
| `/ultrareview` | `[PR or branch]` | B | | gated | Alias path to `/code-review ultra`. 3 free runs on Pro and Max, then usage credits |
| `/update-config` | `[request]` | S | | yes | Edit `settings.json` by description |
| `/upgrade` | | B | | yes | Open upgrade page. Not on Enterprise |
| `/usage` | | B | | yes | Cost, limits, stats, plan breakdown; Loops (2.1.243). Merged `/cost` and `/stats` (2.1.118) |
| `/usage-credits` | | B | | no | Billing page, or admin request with confirmation. Renamed from `/extra-usage` (2.1.144), which still works |
| `/verify` | | S | | gated | Build, run and observe a change. Manual only (2.1.215 per docs) |
| `/vim` | | R | | yes | Removed 2.1.92; use `/config` |
| `/voice` | `[hold\|tap\|off]` | B | | gated | Toggle dictation. claude.ai account |
| `/web-setup` | | B | | gated | Connect GitHub for cloud sessions through `gh` credentials |
| `/workflow-authoring` | | S | | no | Workflow script reference (2.1.248) |
| `/workflows` | | B | | gated | Watch, pause, resume, save workflows. Gated with source absent in snapshot |

`/design consent` and `/design revoke` share the `/design` name in the count.

## Failure modes & edge cases

- `/fast`, `/model` and `/effort` differ in when they take effect. See [slash-commands-system.md](slash-commands-system.md).
- `/background` cannot run when queued items cannot move.
- `/design` and `/slides` are unavailable on third-party providers. `/design-sync` also fails through a Claude apps gateway.
- `/rename` rejects a name that is empty once invisible characters go, with `That name is empty once invisible characters are removed. Usage: /rename <name>`.

## Changes since the snapshot

- 39 new names, listed with `no` or `gated` above.
- Behaviour shifts: `/review` is now a code-review alias (2.1.223); `/agents` lost its UI (after 2.1.197); `/doctor` became a skill (2.1.205); `/output-style` returned (2.1.269); `/bug` split from `/feedback` as aliases (2.1.212, per docs); `/release-notes` picker (2.1.92).
- Removed: `/pr-comments` (2.1.91), `/vim` (2.1.92), `/ultraplan` (2.1.222).

## Open questions

- `/statusline` kind: the docs give no **Skill** marker, while the snapshot is a `prompt` command.
- Version that introduced `/background`, `/stop`, `/subtask`, `/run`, `/fewer-permission-prompts`.
- Whether `/insights` is a built-in or prompt in the current build. It was `prompt` in the snapshot.
