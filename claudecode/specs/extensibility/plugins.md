# Plugins

**Status:** shipped
**Provenance:** both (core in snapshot; dependencies, monitors, themes, workflows, skills-directory plugins, `archive`/`command` sources, claude.ai sync and many CLI verbs post-leak, since v2.1.90, 2026-04-01)
**Sources:** docs `plugins__overview`, `plugins__components`, `plugins__manifest-reference`, `plugins__loading`, `plugins__dependencies`, `plugins__install`, `plugins__security`, `plugins__org`, `plugins__cli-reference`, `plugins__measure`; snapshot `utils/plugins/`, `services/plugins/`, `plugins/`; changelog 2.1.90 to 2.1.314.

## Purpose

A plugin packages skills, commands, agents, hooks, MCP and LSP servers, output styles, themes, workflows, monitors, executables, channels and settings defaults into one installable unit. A plugin with a hooks module is a mod ([mods.md](mods.md)). Distribution is covered in [marketplaces.md](marketplaces.md).

## Behaviour

### Identity

1. A plugin id MUST have the form `<name>@<origin>`, where origin is a marketplace name or a reserved origin: `inline` (`--plugin-dir`, `--plugin-url`, `CLAUDE_CODE_PLUGIN_DIRS`, SDK `plugins`), `skills-dir`, `synced`, `builtin`.
2. A marketplace plugin has two names. The entry name is the install and `enabledPlugins` key and the cache directory name. The manifest name namespaces components and is what name conflicts compare.
3. The manifest MUST be optional. Without one, the name comes from the marketplace entry or directory name.

### Components

4. Default locations and manifest key behaviour:

| Component | Default | Manifest key | Key effect |
| :- | :- | :- | :- |
| Skills | `skills/`, or a root `SKILL.md` | `skills` | Adds |
| Commands | `commands/` | `commands` | Replaces |
| Agents | `agents/` (recursive) | `agents` | Replaces; `.md` files only |
| Hooks | `hooks/hooks.json` | `hooks` | Merges |
| MCP | `.mcp.json` | `mcpServers` | Merges; later name replaces |
| LSP | `.lsp.json` | `lspServers` | Merges; later name replaces |
| Output styles | `output-styles/` | `outputStyles` | Replaces |
| Workflows | `workflows/` | `workflows` | Replaces |
| Themes | `themes/` | `experimental.themes` | Replaces |
| Monitors | `monitors/monitors.json` | `experimental.monitors` | Replaces |
| Executables | `bin/` | none | |
| Settings | `settings.json` | `settings` | File wins if it sets a supported key |
| Evals | `evals/` | `experimental.evals` | See [plugin-evals.md](plugin-evals.md) |

5. When a replacing key is set and the default folder exists, a warning `Default <folder>/ folder is ignored because the manifest sets "<key>"` MUST appear in `claude plugin list` and `/plugin` (v2.1.140).
6. Skills are named `/<plugin>:<dir>`; `name` replaces the last segment. A root `SKILL.md` loads as a single skill when no `skills/` or key exists (v2.1.142). `"."` is accepted as a path (v2.1.221). Plugin skills declared via `skills: ["./"]` use frontmatter `name` (v2.1.94).
7. Agents are named `<plugin>:<subdirs>:<name>`. A file listed in the manifest loses subfolder names. Plugin agents MUST ignore `permissionMode`, `hooks`, `mcpServers`, `initialPrompt`; supported fields are `name`, `description`, `model`, `effort`, `maxTurns`, `autoCompactWindow`, `tools`, `disallowedTools`, `skills`, `memory`, `background`, `omitClaudeMd`, `isolation` (`worktree` only), `color`, and `experimental.cacheTtl`. Agent names over 256 characters are ignored, and agent names cannot contain `:` in their own frontmatter (v2.1.218).
8. Hooks register at plugin load, not at first skill use. One plugin per manifest name registers `hooks/hooks.json` hooks and one loads a hooks module; the managed-enabled copy holds the name. A note begins `Its hooks.json hooks do not run` (v2.1.296).
9. MCP servers appear as `plugin:<plugin>:<server>`, with tools `mcp__plugin_<plugin>_<server>__<tool>`. MCPB bundles (`.mcpb`, `.dxt`, path or `https://`) extract into `.mcpb-cache/` under the plugin root, and take their name from the bundle manifest. A required bundle setting with no value stops the server, with an Errors-tab message. On reload, unchanged servers keep their connection.
10. LSP: `.lsp.json` maps names to config with no wrapper. Any invalid entry skips the whole file. The binary is not installed by the plugin. Each extension gets one server, first registered wins, with a warning. Headers over 64 KiB, bodies over 32 MiB, or non-protocol stdout disconnect the server, counted as a crash. `requestTimeout` defaults to 60 s (v2.1.288). `socket` transport is accepted but stdio is used.
11. `bin/` MUST be on the Bash tool's `PATH` after the user's own entries, so it cannot shadow system commands. PowerShell gets it only outside the sandbox. claude.ai and Cowork refuse plugins with a top-level `bin/`.
12. `settings.json` honours only `agent` and `subagentStatusLine`; others drop. Plugin defaults are the lowest settings layer. Between plugins, the last loaded wins, logging `overrides setting`.
13. Monitors are persistent background shell commands, outside the sandbox, whose output reaches the model as notifications. `when` is `always` (session start and reload) or `on-skill-invoke:<skill>`. They MUST NOT start under `-p`. They need no feature flags from v2.1.310. A plugin disabled mid-session leaves monitors running. Copied-plugin updates need a restart for monitors.
14. `CLAUDE.md` at the plugin root MUST NOT load, and validate warns.
15. Plugin themes are read-only; edits are saved as a user copy. Output styles appear as `<plugin>:<name>`.
16. `channels` entries bind to a server key in `mcpServers`; see [channels.md](channels.md).

### User configuration

17. `userConfig` options are strict objects: `type` (`string`, `number`, `boolean`, `directory`, `file`), `title`, `description`, optional `required`, `default`, `options` (v2.1.271), `multiple`, `sensitive`, `min`, `max`. Keys are identifiers.
18. The dialog MUST appear in `/plugin` flows for unset options. `claude plugin install` MUST never prompt; it takes `--config KEY=VALUE`, and `claude plugin configure --values-stdin` sets values later (v2.1.285). Non-sensitive options also appear in `/config` (v2.1.269), except `multiple` lists.
19. Non-sensitive values go to `pluginConfigs`; sensitive ones go to the secure credential store. `pluginConfigs` is not read from project settings (v2.1.207).
20. `${user_config.KEY}` substitutes in MCP and LSP config, exec-form hook args, and skill and agent content, where sensitive values become placeholders. Shell-form hooks, monitors and MCP `headersHelper` MUST reject it. `CLAUDE_PLUGIN_OPTION_<KEY>` is exported to hooks only.

### Loading stages

21. Three stages MUST be distinguished: declared (`enabledPlugins`, `extraKnownMarketplaces`), fetched (`installed_plugins.json`, `known_marketplaces.json`, `cache/`), loaded (the running session's set).
22. Startup MUST load from records and cache without network. Background reconciliation then clones declared marketplaces missing from disk, re-fetches on source change, and downloads uncached enabled plugins.
23. `enabledPlugins` sources, low to high: `--add-dir` (true only), user, project, local, flag, managed. Merge is per key. Managed `true` force-enables and `false` blocks.
24. A plugin `true` only in project settings MUST NOT be fetched, unless it is relative-path or seeded; it shows an error. Fetching needs a `true` from user, untracked local, `--settings` or managed.
25. Project-scope plugins MUST pass the workspace trust check for that folder; parent trust and `-p` do not count. Their MCP servers use per-server approval, bundled or out-of-tree MCP servers are skipped, and monitors do not load. Personal `~/.claude/skills/` plugins are exempt.
26. Skills-directory plugins (v2.1.157) load from the primary working directory's `.claude/skills/`, not parents. They are silently skipped if any `strictPluginOnlyCustomization` kind is locked, or `strictKnownMarketplaces` lacks `{"source":"skills-dir"}`, or `blockedMarketplaces` has it. A root `SKILL.md` may still load as a plain skill.
27. In-place loads: `--plugin-dir`, skills-directory, relative-path entries in local marketplaces, and link-mode `command` sources. Zips and `--plugin-url` extract to a session temp directory. Others copy to `cache/<marketplace>/<plugin>/<version>/`.
28. A component path resolving outside the root, a symlink leading outside (except between plugins in one marketplace), or a backslash path on macOS and Linux MUST be rejected with `path escapes plugin directory`; the plugin loads without that component.
29. All component paths must start with `./` and exist. Exceptions: `skills` accepts `"."`, `mcpServers` accepts `https://` bundles.
30. Version directories replaced by update or uninstall get `.orphaned_at` and are removed 14 days later. The sweep runs only while an install record exists.

### Conflicts

31. Precedence for same manifest name: managed `enabledPlugins` id; session-only; installed marketplace; skills-directory (personal over project); synced. A session plugin replacing an installed one does so silently except in `--debug`.
32. Setting `<name>@inline` to `false` stops shadowing.

### Node dependencies

33. On cache creation, if the root has `package.json` and a supported lockfile, Claude Code MUST install with the lockfile's manager: `bun.lock`, then `npm-shrinkwrap.json`, then `package-lock.json`. `bun.lockb`, yarn and pnpm are skipped. npm lockfile version 2 or 3; bun no higher than 2.
34. The install MUST run no plugin code: registry packages pinned to exact versions, `https` links, a separate folder without the plugin's `.npmrc`, `.env` or `bunfig.toml`, frozen resolution, `--ignore-scripts`, no `overrides` or `patchedDependencies`, 60-second timeout. It cannot be disabled. On failure the plugin still loads, with a note.

### Versions and updates

35. Version resolution: manifest `version`, then entry `version`, then source-derived (`github`, `url`, `git-subdir`: 12-character SHA, plus subdir hash; `archive`: 12-character SHA-256; relative in git marketplace: directory commit; local non-git and `npm`: `unknown`). `command` always uses a hash, optionally `<manifest>-<hash>`. Enclosing repositories are not used.
36. A plugin in a local-path marketplace always loads current source. A claude.ai-hosted marketplace's recorded version overrides the manifest.
37. Auto-update runs in interactive sessions at a random delay of up to ten minutes after the first message. Updated plugins take effect on `/reload-plugins` or next launch. `autoUpdate` resolution: `extraKnownMarketplaces` entry, then `known_marketplaces.json`, then default (on for official names except `knowledge-work-plugins` and `first-party-plugins`, and claude.ai marketplaces). `DISABLE_UPDATES`, `DISABLE_AUTOUPDATER` and `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` disable it unless `FORCE_AUTOUPDATE_PLUGINS=1`. Entries with `headersHelper` are skipped.
38. Install activation: `/plugin` applies changes when the menu closes (v2.1.268) or activates immediately when safe (v2.1.221). A reload that would invalidate the prompt cache warns and needs `/reload-plugins --force`.

### Plugin dependencies

39. `dependencies` entries are `"name"`, `"name@marketplace"`, or `{name, version, marketplace}`. Bare names resolve in the declaring plugin's marketplace.
40. Version ranges resolve against git tags `<plugin-name>--v<version>` on the repository hosting the plugin (the marketplace repo for relative paths), choosing the highest match. Pre-releases need a suffix such as `^2.0.0-0`. Tag versions are used for checks, not `plugin.json`.
41. No satisfying tag: own-repo plugins fail with `has no git tag satisfying`; relative-path plugins use the current copy and check at load, leaving the dependent disabled if out of range.
42. Non-git sources (`npm`, `archive`, `command`): the constraint does not pick the version, and a `plugin.json` without a version satisfies nothing. `command` sources and `headersHelper` entries MUST never be auto-installed as dependencies.
43. Cross-marketplace dependencies MUST need the target listed in the root marketplace's `allowCrossMarketplaceDependenciesOn`, unless already enabled at the same scope.
44. Multiple constraints resolve to the highest common version. Non-overlapping constraints fail install, or leave the dependency in place during auto-update with an Errors entry. Auto-update of pinned plugins picks the highest satisfying tag (v2.1.119).
45. `install` installs and enables dependencies at the same scope. `enable` force-enables transitive dependencies. `disable` refuses if a dependent is enabled, printing a chain (v2.1.143). `uninstall` keeps auto-installed dependencies until `prune` (v2.1.121).
46. `/reload-plugins`, auto-update, re-install and `marketplace add` install missing dependencies from known marketplaces (v2.1.116, v2.1.117).
47. For `@synced` plugins, a marketplace-qualified dependency is met by the marketplace install or a same-named claude.ai plugin.

### claude.ai sync

48. Signed-in terminal sessions sync account plugins in the background at start, once per launch (v2.1.273 per docs; opt-out `syncClaudeAiPlugins`, v2.1.275). Same exclusions as skills sync. Changes show `Plugins changed. Run /reload-plugins to activate.`
49. Org-required plugins load regardless, and `claude plugin disable` refuses them. Synced plugins never override a same-named installed plugin (v2.1.239).

## Configuration & interfaces

### CLI verbs

| Command | Purpose |
| :- | :- |
| `claude plugin init <name>` | Scaffold (v2.1.157); `--with` adds components |
| `install`, `uninstall`, `enable`, `disable`, `update` | Lifecycle; `--scope`, `--json` (v2.1.268); install adds `--config`, `--marketplace`, `-y`, `--accept-command`; uninstall adds `--keep-data`, `--prune` |
| `list` | `--json`, `--available`, `--data-size` |
| `details <name>` | Inventory and token cost (v2.1.139) |
| `configure <plugin>` | Show or set options (v2.1.285) |
| `prune` | Remove orphaned dependencies (v2.1.121) |
| `tag` | Create `<name>--v<version>` after validation (v2.1.118) |
| `validate` | `--strict`, `--json`; exit 0, 1, 2 |
| `eval`, `test` | [plugin-evals.md](plugin-evals.md), [mods.md](mods.md) |
| `/plugin` | Discover, Installed, Marketplaces, Errors, Stats tabs |
| `/reload-plugins` | Apply changes; available headless (v2.1.260) |

`--plugin-dir` accepts directories, `.zip` files (v2.1.128) and folders of plugins (v2.1.265). `--plugin-url` fetches a zip (v2.1.129). `claude -p` refuses `/plugin`.

### Name rules

`name`: non-empty, no spaces, `@`, `:`, path separators, control or bidi characters. Validate errors for names starting `claude-`, `anthropic-`, `anthropics-`, `cc-plugin-`; for `claude`, `anthropic`, `anthropics`, `claude-code`, `claude-mods`; for `official` beside `claude` or `anthropic`. It warns on those words elsewhere. Loading still works for refused names.

### Unknown keys

Top-level unknown keys are stripped with a validate warning. Unknown keys in `userConfig` options, `channels`, `lspServers` and `monitors` entries are errors and block loading.

### Environment

| Variable | Notes |
| :- | :- |
| `${CLAUDE_PLUGIN_ROOT}` | Version path, changes on update |
| `${CLAUDE_PLUGIN_DATA}` | `~/.claude/plugins/data/<id>/`, survives updates; removed at last-scope uninstall unless `--keep-data` |
| `${CLAUDE_PROJECT_DIR}` | Project root |
| `CLAUDE_CODE_PLUGIN_CACHE_DIR` | Moves the plugins root |
| `CLAUDE_CODE_PLUGIN_DIRS` | Session plugin directories |
| `CLAUDE_CODE_PLUGIN_PREFER_HTTPS` | Clone over HTTPS (v2.1.141) |
| `CLAUDE_CODE_PLUGIN_KEEP_MARKETPLACE_ON_FAILURE` | Keep cache on failed pull (v2.1.90) |

The variables are not in the Bash tool's environment.

### On-disk files

`installed_plugins.json`, `known_marketplaces.json`, `known_marketplaces_claudeai.json`, `flagged-plugins.json`, `cache/`, `data/`, `marketplaces/`, `synced/`, `.trash/`, and `installed_plugins.set-aside.*` and `*.unreadable.*.kept` recovery copies (v2.1.283).

## Failure modes & edge cases

- `Plugin "<name>" not cached at <path>`, `is enabled in project settings but isn't installed here`, `has conflicting manifests`, `path not found`.
- A malformed agent file loads with all fields ignored, with description `Agent from <plugin> plugin`.
- Unused detection: a plugin moves under **Not used recently** after 14 days and 10 sessions, except session-only, managed, seed-mounted, or theme, style, monitor or workflow plugins, and when `strictKnownMarketplaces` is set.
- Telemetry names non-official plugins as `third-party` unless `OTEL_LOG_TOOL_DETAILS=1`.
- Sessions under `--safe-mode` disable plugins (v2.1.169).

## Changes since the snapshot

- v2.1.105: monitors.
- v2.1.118: themes; `claude plugin tag`.
- v2.1.121: `prune`.
- v2.1.128, v2.1.129: zip and `--plugin-url`.
- v2.1.129: `experimental` container.
- v2.1.139: `details`.
- v2.1.143: dependency enforcement.
- v2.1.154: `defaultEnabled`.
- v2.1.157: skills-directory plugins, `init`.
- v2.1.207: `${user_config.*}` hardening.
- v2.1.221: immediate activation.
- v2.1.224, v2.1.229: `archive`, `command` sources.
- v2.1.259: `validate --json`.
- v2.1.268: `--json` verbs.
- v2.1.269: `eval`.
- v2.1.275: npm sources use `--ignore-scripts`; terminal sync.
- v2.1.281: validate checks MCP.
- v2.1.285: `configure`.
- v2.1.287: Claude Mods.
- v2.1.292: `--marketplace`.
- v2.1.302: faster loading with many plugins.

## Open questions

- Terminal plugin sync: docs cite v2.1.273; changelog entry is v2.1.275.
- `plugin details` cost-model inputs beyond names and descriptions are not specified.
- `workflows` component version is not in the changelog entries reviewed.
