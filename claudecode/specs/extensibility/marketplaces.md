# Plugin Marketplaces

**Status:** shipped
**Provenance:** both (core in snapshot; `archive`, `command` sources, relevance, `headersHelper`, GitLab, name hardening post-leak)
**Sources:** docs `plugins__marketplace-reference`, `plugins__host-marketplace`, `plugins__create-marketplace`, `plugins__anthropic-marketplaces`, `plugins__relevance`, `plugins__org`, `plugins__publish`, `plugins__cli-reference`; snapshot `utils/plugins/`; changelog 2.1.101 to 2.1.299.

## Purpose

A marketplace is a catalog (`.claude-plugin/marketplace.json`) listing plugins and where to fetch them. Users add marketplaces, then install from them. Administrators allow, block or pre-register them.

## Behaviour

### File format

1. Top-level: `name`, `owner` (`name` required), `plugins` required. Optional: `$schema`, `description`, `version`, `metadata.{description,version,pluginRoot}`, `forceRemoveDeletedPlugins`, `allowCrossMarketplaceDependenciesOn`, `renames`.
2. `name` MUST use letters, digits, `.`, `_`, `-`, start alphanumeric, and contain no `..`. Each plugin entry is validated separately, so one bad entry does not fail the catalog.
3. Entry fields: `name`, `source`, `description`, `version`, `category`, `tags`, `strict`, `relevance`, `dependencies`, `defaultEnabled`, `displayName`, `metadata`, `headers`, `headersHelper`, plus manifest fields. Directory listing fields are unknown in entries.
4. Without a `plugin.json`, the entry is the manifest; entry `hooks` load only as an inline object.
5. With `plugin.json`, `strict: true` (default) appends entry `commands`, `agents`, `skills`, `outputStyles`, `themes` and replaces `hooks` matchers per event. `strict: false` with any of those is a conflict that fails loading.
6. Precedence: entry wins for `defaultEnabled` and display fields; manifest wins for `version`. Display metadata prefers the entry (v2.1.265).
7. A marketplace-root entry listing specific `skills` loads only those.

### Reserved names

8. These MUST be refused or restricted: official names (for example `claude-plugins-official`, `anthropic-marketplace`, `agent-skills`, `claude-code-plugins`); community names (`claude-community`, `claude-plugins-community`, `healthcare`); directory names (`anthropic-plugin-directory`, `claude-plugin-directory`); impersonating names and any non-ASCII name; respellings of reserved names (v2.1.280); `inline`, `builtin`, `skills-dir`, `synced`, `claude-plugin-test`; `npm`, `pip`, `uv`, `cargo`, `github`, `gh` (v2.1.275); JavaScript object member names; `claudeai-*`; and a registered GitHub marketplace's `<owner>-<repo>` download folder.
9. An official or community name from a source outside `github.com/anthropics/` MUST stop the marketplace and its plugins loading. Control and invisible characters are rejected (v2.1.247). Marketplace text in output is escape-safe.

### Plugin sources

| Type | Fields | Notes |
| :- | :- | :- |
| Relative path | string | Starts `./`, or a bare name under `metadata.pluginRoot` (v2.1.239); `"."` is the root; unusable with `url` marketplaces; rejected for `settings` |
| `github` | `repo`, `ref`, `sha` | |
| `url` | `url`, `ref`, `sha` | Any git repo |
| `git-subdir` | `url`, `path`, `ref`, `sha` | Sparse checkout |
| `npm` | `package`, `version`, `registry` | Fetched with `npm pack --ignore-scripts`, integrity-verified (v2.1.275); git, folder and alias specs refused (v2.1.286) |
| `archive` | `url`, `sha256` | Zip over HTTPS (v2.1.224) |
| `command` | `command`, `timeout`, `mode` | v2.1.229 |

10. `sha` MUST be a full 40-character lowercase SHA and beats `ref`.
11. Relative paths in git marketplaces interact with submodules: a plugin inside a submodule, or a submodule inside a plugin, or links into one are handled specially, and several placements are refused; the doc lists the cases.
12. `command` source: runs through `sh` or `cmd.exe` from home, prints exactly one absolute path line, exits 0 within `timeout`. The directory must hold plugin content at its top level, MUST NOT be the session directory or a parent, nor a UNC path.
13. `copy` mode hashes copied files, capped at 256 MiB and 20,000 entries. `link` mode links top-level entries, skips hashing and limits, skips Node dependency installs, refuses top-level symlinks leading out, is refused on Windows, and does not load in sessions started inside the directory. Link-mode version derives from the real path and top-level entries.
14. Accepted `command` text is remembered. Installs and updates ask `Run this command now?`; `-y` or `--accept-command <sha256>` (v2.1.271) accept. `-y` is ignored inside a Claude Code session. Bulk installs, suggestions, dependencies and background updates refuse instead of asking, listing the plugin in Errors. A changed command stops background runs until accepted.
15. Command sources re-run at install and update, once per session in the background (independent of auto-update, skipped with `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC`), and when the cached version is missing. Changed output reloads in place unless that would invalidate the prompt cache.

### Marketplace sources

16. Source types: `url`, `github`, `git`, `file`, `directory`, `settings`. `npm` parses but fails to load. `hostPattern`, `pathPattern` and `skills-dir` are valid only in policy lists.
17. `marketplace add` accepts `owner/repo` with `#ref` or `@ref`, `user@host:path`, git URLs (`.git`, `/_git/`, github.com, gitlab.com including subgroups, v2.1.232), `https://` file URLs, and paths starting `./`, `../` or absolute.
18. `github` and `git` support `path` and `sparsePaths`. `skipLfs` is accepted with no effect: clones leave LFS as pointers (v2.1.274).
19. Adding writes to `extraKnownMarketplaces` as well as disk. `known_marketplaces.json` is per user, across projects. Re-adding under the same name from another source reports the replacement (v2.1.284).
20. Private access follows the user's git setup. `owner/repo` probes SSH then falls back to HTTPS. Git prompts and askpass programs are off, so a credential that needs a prompt fails. SSH hosts must be in `known_hosts`.
21. Background checks that find new commits, or fail, re-clone and swap; a failed clone keeps the checkout. `CLAUDE_CODE_PLUGIN_KEEP_MARKETPLACE_ON_FAILURE=1` keeps it without re-cloning.
22. `name@marketplace` installs MUST refresh that marketplace first, independent of auto-update (v2.1.232), except for local or `settings` sources, seed directories, a refresh within 30 s, `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC`, or blocked marketplaces. A failed refresh proceeds from cache and reports `marketplace not refreshed`. Bare `/plugin install` refreshes auto-update marketplaces only after a miss. Bare `claude plugin install` refreshes nothing.

### Limits

| File | Size | Response | Redirects |
| :- | :- | :- | :- |
| `marketplace.json` from `url` | 5 MiB | 10 s | Cross-origin must be `https` and not loopback, link-local or metadata hosts |
| `archive` zip | 256 MiB | 120 s | At most 5, same restrictions |

Archive contents: 100,000 entries, 512 MiB per file, 1 GiB total, 50:1 compression. A `sha256` mismatch refuses the install.

### `headersHelper`

23. Available on a `url` marketplace source or a plugin entry (v2.1.238). Entry use requires `"strict": false`; headers apply only to `archive`.
24. Command rules: at most 500 printable ASCII characters, no run of four spaces, prints one JSON object of string values, exits 0 within 10 s, runs from the config directory. Credential-looking variables are removed when set from a `marketplace.json` entry or project settings. Env: `CLAUDE_CODE_MARKETPLACE_URL`, `CLAUDE_CODE_MARKETPLACE_NAME` (unset on first fetch), `CLAUDE_CODE_PLUGIN_NAME`, `CLAUDE_CODE_PLUGIN_ARCHIVE_URL`.
25. A failed helper MUST cancel the fetch. A non-`https` marketplace URL skips the helper. Off-origin redirects carry no helper or `headers` values. Routing and identity names (`Host`, `Cookie`, `X-Forwarded-*`) are dropped from entries. `--add-dir` settings helpers are ignored.
26. Marketplace helpers run without asking from user, `--settings` and managed files; from project settings only after folder trust, not `-p`; from server-managed settings after the security approval. Output is reused up to 60 s. Entry helpers run only on a single-plugin install or update, after acceptance. `disableCommandPluginSources` and `allowManagedHooksOnly` block them, except for managed-declared marketplaces.

### Maintenance

27. `renames` maps old to new or `null`; chains are followed and settings keys rewritten in user, project and local scopes (v2.1.193). Managed settings cannot be rewritten, so the notice recurs.
28. `forceRemoveDeletedPlugins` uninstalls removed plugins. Delisted plugins appear in `flagged-plugins.json` and the **Flagged** section.
29. Symlinks: inside the plugin are preserved; within the marketplace are dereferenced; outside are skipped.
30. There is no deprecation state, audience field, install-without-consent field, or stored git credential.

### Relevance suggestions

31. An entry's `relevance` holds optional `topic` (64 characters) and `signals`: `cwd` (10 globs, 256 chars), `cli` (10, 64), `hosts` (20, 128), `filesRead` (10, 256), `manifestDeps` (10 `{file, pattern}` regexes, 256; manifests over 512 KB skipped).
32. Matching MUST be local with no network or reporting. `cwd` matches absolute and repo-relative paths, case-insensitively, and is the only signal available at start. `cli` records only the leading command of each shell call after env assignments and `sudo`. `hosts` needs bare lowercase hostnames. `filesRead` and `manifestDeps` also cover written files and auto-loaded `CLAUDE.md` files.
33. Suggestions surface as a spinner tip, a start notification (`cwd` only) and a Discover pin. Frequency: at most once per three sessions; the notification stops after two combined displays; nothing repeats once installed; the Discover pin shows once, recorded in `~/.claude.json`.
34. Terminal suggestions require the name in managed `pluginSuggestionMarketplaces` (v2.1.152), plus a declared source for non-official marketplaces. A mismatch shows nothing. `spinnerTipsEnabled: false` or `spinnerTipsOverride` with `excludeDefault` stops tip and notification, not the pin. Installs always need confirmation.
35. Unknown `relevance` keys are ignored; exceeded limits invalidate that entry.

### Policy

36. `strictKnownMarketplaces` allowlists and `blockedMarketplaces` blocks; both are enforced on install, update, refresh and auto-update (v2.1.117). `owner/*` matches all repos of a GitHub owner (v2.1.223). `blockedMarketplaces` on `github` also blocks equivalent `git` URLs.
37. A managed marketplace entry replaces a same-named lower entry without merging. Cloud sessions do not add repository `extraKnownMarketplaces`.
38. Project `extraKnownMarketplaces` register after trust acceptance; in `-p` only for already accepted folders.

### Anthropic marketplaces

39. `claude-plugins-official` (`anthropics/claude-plugins-official`) is added on first interactive terminal start unless policy or `CLAUDE_CODE_DISABLE_OFFICIAL_MARKETPLACE_AUTOINSTALL` blocks it. `claude-community` is added manually. `claude-code-plugins` is deprecated. Tiers are official, community and third-party.

## Configuration & interfaces

| Command | Notes |
| :- | :- |
| `claude plugin marketplace add` | `--scope`, `--sparse`, `--claudeai` (v2.1.273), `--json` (v2.1.287) |
| `... list`, `... update`, `... remove` | `remove` takes `--scope` (v2.1.152) and uninstalls its plugins |
| `claude plugin validate <path>` | Reports schema, reserved names, Desktop acceptance (v2.1.221) |
| `/plugin` Marketplaces tab | Add, remove (`d`), auto-update toggle |

| Setting | Scope |
| :- | :- |
| `extraKnownMarketplaces` | Any; `autoUpdate` per entry |
| `strictKnownMarketplaces`, `blockedMarketplaces`, `pluginSuggestionMarketplaces` | Managed |
| `disableCommandPluginSources` | See rule 26 |

## Failure modes & edge cases

- `Marketplace name impersonates an official Anthropic/Claude marketplace`; `Marketplace is registered from an untrusted source`; `Plugin archive integrity check failed`; `Plugin <name> has conflicting manifests`.
- Claude Desktop rejects some names that the CLI accepts; validate warns (128-character limit; `org`, `org-provisioned`, `unknown`).
- claude.ai org sync accepts only some source types, requires private or internal repos on github.com and gitlab.com, and rejects top-level `bin/`.
- A `settings` source's `name` must equal its `extraKnownMarketplaces` key.

## Changes since the snapshot

- v2.1.101: refresh failures warn.
- v2.1.117: policy enforced on all paths.
- v2.1.152: `pluginSuggestionMarketplaces`.
- v2.1.154: relevance pinning.
- v2.1.193: `renames` followed.
- v2.1.223: `owner/*`.
- v2.1.224: `archive`.
- v2.1.229: `command`.
- v2.1.232: GitLab, refresh before install.
- v2.1.238: `headersHelper`.
- v2.1.247: name hardening.
- v2.1.271: `--accept-command`.
- v2.1.274: LFS pointers.
- v2.1.275: npm safety.
- v2.1.280: reserved-name imitation refused.
- v2.1.286: npm git and folder specs refused.
- v2.1.292: `--marketplace` on install.

## Open questions

- The full official-names list is in the docs and may change.
- claude.ai organization sync's accepted source types are given only by reference.
- `sha256` omission with `archive`: version falls back to the download digest, but no warning applies without a `headersHelper`.
