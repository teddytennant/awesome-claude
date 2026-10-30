# Claude Mods

**Status:** shipped
**Provenance:** post-leak (since v2.1.287, 2026-10-01; Desktop v2.1.286)
**Sources:** docs `plugins__mods__overview`, `__reference`, `__events`, `__api`, `__interface`, `__create`, `__gallery`, `__test`, `__troubleshoot`, `__admin`; changelog 2.1.287 to 2.1.309. No snapshot counterpart.

## Purpose

A mod is a plugin containing JavaScript or TypeScript event handlers ("hooks") that run in Claude Code's own process, as middleware on engine events. Mods can draw interfaces, redraw built-in surfaces, step into tool calls and requests, add commands and tools, and call models. They are not sandboxed. On these pages "hook" means a mod handler; a configured shell, HTTP or prompt hook is a "settings hook" ([hooks.md](hooks.md)).

## Behaviour

### Packaging

1. A mod MUST be a plugin with `.claude-plugin/plugin.json`, and `hooks/hooks.json` whose `modules` holds one path to a hooks module. The same file can also hold settings hooks under `hooks`.
2. The module MUST be an ES module (`.js`, `.mjs`, `.cjs`, `.jsx`, `.ts`, `.mts`, `.cts`, `.tsx`) exporting `register(on, options)`, where `options` holds `userConfig` values with defaults.
3. `types/index.d.ts`, or the manifest's `types` path, declares `PluginState` and added namespaces, and is required when using `$.state` or adding a namespace.
4. One plugin per manifest name loads a hooks module.
5. Mods install as ordinary plugins. `--plugin-dir` loads for one session and reloads on save; `/reload-plugins` reloads explicitly. `CLAUDE_CODE_PLUGIN_DIR_WATCH=1` reloads in long-running non-interactive sessions.

### Handler contract

6. `on(event, [matcher], hook)` registers a handler and returns a registration with `.catch(handler)`.
7. Hooks receive `$` (the API), `e` (deeply frozen plain data), and `next`. Passing a copy to `next` rewrites the event. Returning an object without calling `next` answers it. `turn.step` and `process.spawn` hooks are async generators.
8. `next` exposes `signal`, `origin` (`{plugin, tier}`, with the engine as `{plugin:'engine', tier:'core'}`), `budget` (`ms`, `remainingMs`), and `to(e, tier)`, which only `prependPlugins` and `appendPlugins` mods may call. In `.catch`, `next.error` (`kind` of `throw`, `timeout` or `re-entry`; `cause` of `rewritten` or `lent`) and `next.called` are set.
9. Everything outside the mod's own code MUST go through `$`, so that static analysis can list what a mod does.

### Ordering

10. Hooks on one event form a chain, first outermost. A later mod cannot stop an earlier one seeing an event.
11. Order: `sec-default@builtin` (where loaded), `prependPlugins`, other organization mods; user-installed mods; `appendPlugins`; other built-in mods. Among installed mods, a mod runs before those in its `dependencies`. Within a module, `on` call order.
12. Managed `PreToolUse` settings hooks MUST run before the first `tool.call` hook; a block stops all `tool.call` hooks, and if a mod rewrites the call they run again on the rewrite. Other `PreToolUse` hooks run after the last mod calls `next`, so a mod answering `tool.call` prevents them. `tool.check` fires after `PreToolUse`.

### Failure

13. A failed hook (throw, timeout, wrong shape) without `.catch` MUST be skipped if it had not called `next`, with the next handler running in its place; if `next` had resolved, that result stands. A line names mod, event and reason.
14. `.catch` runs only for throw or timeout; events raised under the hook's own calls skip that hook without asking `.catch` (v2.1.301). If `.catch` fails, the hook is skipped as though it had none.
15. Fail-closed guards MUST use `.catch`. At `tool.check` and `plugin.register`, a refusal after `next` holds. At `tool.call`, a deny after `next` withholds the result, and the model and user are told the tool ran (v2.1.295).
16. A plugin-blockable action MUST be refused if the hook cannot be handed it or cannot answer (v2.1.299).
17. Long text is clipped and logged rather than refused (v2.1.290).

### Trust and permissions

18. In an untrusted interactive directory, no mod loads until the trust prompt is answered.
19. Without managed settings or Team/Enterprise `/login`, a mod approval can pass `ask` rules and a blocking `PreToolUse`. A mod can never change what a permission prompt shows.
20. Where `sec-default@builtin` loads (machine has managed settings, or Team/Enterprise `/login`; long-lived `CLAUDE_CODE_OAUTH_TOKEN` does not count), a user's mod MUST NOT approve past `deny` rules, `ask` rules, or a blocking `PreToolUse`, nor change managed hook inputs or decisions, the system prompt, managed instructions, settings reads, or managed MCP tools and descriptions. `allowModsToOverrideDenyRules` relaxes the deny case.
21. Under the guard, user-mod hooks never run on `classic.*`, `prompt.compose`, `prompt.section`, `prompt.context`, `prompt.attachment`, `skill.prompt`, `attribution.text`, `session.compact`, `settings.read`, and `session.append` doors `attachment`, `hook-context`, `compaction`. `/plugin` and validate note this (v2.1.299).
22. In auto mode, a mod-approved call skips the classifier, unless the guard is loaded and the session uses `--permission-prompt-tool` or `canUseTool`.
23. Permission rules govern Claude's tool calls only, not `$.fs` or `$.process`.
24. Network: an organization WebFetch disallow also refuses `$.http.fetch`. `CLAUDE_CODE_DISABLE_WEB_FETCH` or a `WebFetch` deny does not. `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` stops only built-in mods and requests carrying Anthropic credentials (v2.1.288).
25. If `prependPlugins` is set, the guard loads only when listed there.

### Controls

| Control | Effect |
| :- | :- |
| `pluginConfigs["cc-plugin-sec-default@builtin"].allowManagedModsOnly` | Managed only; only organization and built-in mods run hooks |
| `allowManagedHooksOnly` | Blocks hooks and mods that are not the organization's |
| `disableAllHooks` | In managed settings no installed plugin mod or hook runs; elsewhere, managed ones continue |
| `disableSideloadFlags` | Rejects `--plugin-dir`, `--plugin-url` |
| `--safe-mode`, `--bare` | Stop installed mods; built-in mods continue |

`disableAllHooks` and `allowManagedModsOnly` leave the plugin's other components loaded. `CLAUDE_CODE_ENABLE_FUNCTION_HOOKS` is ignored from v2.1.287. A remote rollout switch can turn installed mods off; mechanics are out of scope.

### Surfaces

| Where | Hooks run | Drawing |
| :- | :- | :- |
| Terminal, including JetBrains | Yes | Yes |
| Desktop Code tab | Yes | Except terminal-only elements |
| Desktop WSL session | No | No |
| VS Code panel | Yes | Extension 2.1.299; 2.1.304 without flags |
| `claude -p`, SDK | Yes | No |
| Remote Control | Yes, on the host | On the host terminal |
| Cloud | Yes, if the plugin reaches it | No |

## Configuration & interfaces

### Events

| Group | Events |
| :- | :- |
| Tools | `tool.call` (`{deny}`, `{result}`), `tool.check` (`{decision, reason}`; `e.agentId`, `e.ceiling` v2.1.290, `e.isReadOnly` v2.1.304), `tool.describe` (`{description, isDeferred}`) |
| Prompts | `prompt.submit` (`text`, `context`, `{drop}`; `$.prompt.media` for managed mods v2.1.299), `prompt.fill`, `prompt.suggest`, `prompt.edit`, `prompt.change` (v2.1.300), `prompt.autocomplete` (v2.1.292), `prompt.compose`, `prompt.section`, `prompt.context`, `prompt.attachment`, `prompt.mention` (v2.1.290), `skill.prompt` (source fields v2.1.299), `attribution.text` |
| Commands, config | `command.run`, `command.describe`, `config.set`, `config.describe`, `settings.read` (engine reads and `e.layers` v2.1.304) |
| Turns | `turn.start`, `turn.step` (`serverToolUses` v2.1.290), `turn.complete` |
| Session | `session.start`, `session.end`, `session.compact`, `session.receive`, `session.send`, `session.append` (`queue` door v2.1.299), `session.attach`, `session.detach`, `session.measure` |
| Agents | `agent.offer`, `agent.spawn` |
| Interface | `ui.render`, `ui.resolve`, `ui.press`, `ui.input`, `ui.select`, `ui.focus`, `ui.scroll`, `ui.close`, `ui.message`, `ui.fault` |
| Other mods | `plugin.register` (`{refuse}`; `e.uses`), `engine.create` |
| Telemetry | `telemetry.log`, `telemetry.mark`; installed mods MUST filter `{to:'collector'}`, or validate fails |
| Settings hooks | `classic.<Event>`, `e` being the stdin JSON |
| API calls | Each method is an event, such as `fs.read`; `next(e)`, `{deny}`, `{value}` |

`session.start` runs once per loaded mod and again after reload, not after `/clear`, `/resume` or `/branch`. `session.end` runs for those too.

### API namespaces

`$.plugin`, `$.ui`, `$.command`, `$.tool`, `$.agent`, `$.model` (`complete`, `fork`, `classify`), `$.prompt` (`submit` labels text with the mod unless `asUser: true`), `$.turn`, `$.session`, `$.config`, `$.settings`, `$.env`, `$.fs`, `$.store` (machine-wide JSON store, swept after `cleanupPeriodDays` unused), `$.state` (reactive; ends with the session or `/clear`, `/resume`, `/branch`), `$.clock`, `$.http`, `$.process`, `$.mcp`, `$.audio`, `$.telemetry`.

After a user interrupt, `$.prompt.submit`, `$.command.run`, `$.agent.spawn`, `$.session.send`, and background `$.tool.call` are refused, each in a defined shape. Some calls are also refused in `-p` and SDK sessions.

### Drawing

Sites: `Pane`, `AbovePrompt`, `UserMessage`, `AssistantMessage`, `ToolUse`, `ToolResult`, `ToolGroup`, `CommandOutput`, `AskUserQuestion`, `ToolProgress`, `Spinner`, `TurnDuration`, `InfoNotice`, `SessionMode`, `PromptHint`. Elements from `$.ui.resolve(e)`: `Box`, `Text`, `Button`, `Link`, `Code`, `Markdown`, `Input`, `Select` (all surfaces); `Svg` (Desktop, VS Code); `Client` (terminal, Desktop); `Raster`, `Image` (terminal). Mods cannot redraw the permission prompt. Each mod's Box or Text root carries `part: {plugin}` in test trees (v2.1.299). `$.ui.notify` reports refusal reasons `disabled`, `no-channel`, `no-surface`, `refused`.

### Limits

| Limit | Value |
| :- | :- |
| Hook execution | 10 s; 50 ms on `prompt.edit` |
| `.catch` | 1 s |
| `session.end` hooks together | SessionEnd budget |
| `$.process.run` | 30 s default, 10 min max; 4 MiB per stream |
| `$.fs` read and write | 4 MiB |
| `$.http.fetch` | 4 MiB each way; 30 s; 5 redirects |
| `$.model.complete` `maxTokens` | 1024 default; up to 64,000 or model limit |
| `$.store` | 4 MiB |
| `$.session.messages()` | Newest 4,096 |
| Tree | 32 levels, 20,000 elements, 100,000 chars drawn |
| `Raster`, `Image` | 262,144 cells; 2 MiB |
| Argument and result nesting | 28,000 levels (v2.1.299) |
| Module scopes | 2,000 nested |
| Names | Letters, digits, `_`, `-`; 64 chars |
| Redraws | 10 per second; 30 in terminal for key regions |
| Drop or deny reason | 4,096 chars, cut not failed (v2.1.292) |

### Commands

| Command | Behaviour |
| :- | :- |
| `claude plugin validate <dir>` | Reports errors, `hooks:` and `calls:` lines; `gatingHooks` under `--json` with `.catch` status (v2.1.290); names skipped hooks (v2.1.299) |
| `claude plugin test [dir]` | Runs `*.test.ts`, `*.test.tsx` with stubs and a fake clock; 5 s per test; failed `expect` in a hook or refused stub fails (v2.1.292); unanswered served `$` methods fail after 10 s (v2.1.299) |
| `/plugin` | Shows `N mod active · name`, excluding built-ins |

### Built-in mods

`cc-plugin-agents-md`, `cc-plugin-diff`, `cc-plugin-plugin-authoring` (skill only), `cc-plugin-sec-default`, `cc-plugin-telemetry`, `cc-plugin-you-should-know` (off by default; first-party with telemetry on). They cannot be updated or uninstalled, and are not stopped by `disableAllHooks`, `--bare` or `--safe-mode`. Source for several is public.

## Failure modes & edge cases

- `hooks module not loaded`, `another plugin of that name loads first`, `only managed plugins and built-in plugins run`.
- A rebound top-level `var` refuses the module, with the line named (v2.1.295). Too-deep nesting names the file (v2.1.309).
- `$.fs.write` is not atomic.
- A `-p` run can stay open if a mod keeps background work alive.
- `settings.read` errors include `the merge never settles for <key>` and `refused to the engine`.
- `Stopped: type a message to continue; a mod cannot resume work after Stop`.
- `SendMessage` resumes do not refire `agent.spawn`.
- A plugin running first that skips your hook is reported in the transcript (v2.1.304).

## Changes since the snapshot

- v2.1.287: Claude Mods; You should know.
- v2.1.289: `ui.fault`.
- v2.1.290: `prompt.mention`, `serverToolUses`, `ceiling`, `gatingHooks`; long text clipped.
- v2.1.292: `prompt.autocomplete`; test strictness.
- v2.1.295: post-run deny wording; `var` diagnostics.
- v2.1.299: `$.prompt.media`, `skill.prompt` fields, `queue` door, managed enforcement improved, `.catch` skip notes.
- v2.1.300: `prompt.change`.
- v2.1.301: `.catch` narrowed.
- v2.1.304: `settings.read` layers; validate no longer predicts where hooks run.

## Open questions

- What counts as "your organization's" mod is defined in the admin doc's later sections, not fully reviewed here.
- Docs state the reference covers CLI to v2.1.290; later event additions are from the changelog.
- `prompt.change` is in the changelog but not in the reference's event table reviewed.
- Hot-reload consent details ("stops asking to enable hot reloading") are not specified here.
