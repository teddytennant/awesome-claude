# Settings keys reference

**Status:** shipped
**Provenance:** both
**Sources:** docs `settings-reference`, `settings`; snapshot `utils/settings/types.ts`, `entrypoints/sandboxTypes.ts`, `utils/config.ts`; `comparison/settings.md`

## Purpose

Lookup table of all 247 documented keys at 2.1.314, grouped by the documentation's topics, marking which existed in the snapshot. This is a lookup table, so it exceeds the usual length range. Resolution rules are in [settings-system.md](settings-system.md).

## Configuration & interfaces

Legend.

**Snap** extends `comparison/settings.md`, which reports 77 in both and 170 new by exact name:

| Value | Meaning | Count |
|---|---|---|
| `yes` | Top-level key in the snapshot settings schema | 77 |
| `sub` | Dotted key whose parent is in the snapshot and whose leaf name appears in the schema source; verified by a name search for this spec | 38 |
| `cfg` | Absent from the settings schema, but the same name was a `~/.claude.json` global config field in the snapshot | 21 |
| `new` | No match | 111 |

**Scope**: `Any` all four files; `U` user; `L` local; `M` managed; `G` global config in `~/.claude.json`.

**Since**: minimum version where the key's own entry states one in its opening text.  Rows where the docs state a minimum version that has no changelog heading show `–`. **Default**: as documented; `unset` means the behaviour described in the docs' default clause, which is summarised here only when it matters.

Behaviour text is a one-line summary. Where a key is `Boolean`, the summary describes `true` unless it says otherwise.

### Model and responses (23)

| Key | Snap | Scope | Default | Since | Behaviour |
|---|---|---|---|---|---|
| `advisorModel` | yes | Any | unset | – | Model answering advisor tool calls: alias `fable`, `opus` or `sonnet`. |
| `alwaysThinkingEnabled` | yes | Any | unset | – | `false` turns extended thinking off for every session. |
| `availableModels` | yes | Any | unset | – | Allowlist of pickable model aliases or IDs. |
| `availableModelsMatch` | new | M | `"prefix"` | 2.1.283 | `prefix` or exact matching for `availableModels` ID entries. |
| `deniedModels` | new | M | unset | 2.1.283 | Block models even if `availableModels` permits them. |
| `effortLevel` | yes | Any | unset | – | Default effort for models with no saved level. |
| `enforceAvailableModels` | new | Any | `false` | 2.1.175 | Keep the `/model` Default choice inside `availableModels`. |
| `fallbackModel` | new | Any | unset | – | Ordered backup models on overload; taken whole, no merge. |
| `fastMode` | yes | Any | unset | – | Fast mode on where available. |
| `fastModePerSessionOptIn` | yes | Any | `false` | – | Require turning fast mode on each session. |
| `language` | yes | Any | unset | – | Response language; also session titles. |
| `maxEffortLevel` | new | Any | unset | 2.1.267 | Effort cap globally or per model; lower cap honoured from any scope. |
| `model` | yes | Any | unset | – | Starting model; a managed value is a default, not a lock. |
| `modelOverrides` | yes | Any | unset | – | Map Anthropic model IDs to provider IDs such as Bedrock ARNs. |
| `modelPicker` | new | U,M | unset | – | `/model` rows and order; taken whole; ignored in project and local. |
| `modelPricing` | new | M | unset | – | Report spend at contracted rates. |
| `modelSettings` | new | Any | unset | 2.1.251 | Per-model saved effort, auto-compact window or effort cap. |
| `outputStyle` | yes | Any | unset | – | Name of a built-in or custom output style. |
| `promptCacheTtl` | new | Any | unset | – | Main-conversation TTL: `5m` or `1h`. |
| `showThinkingSummaries` | yes | Any | `false` | – | Show thinking summaries, not a stub. |
| `subagentPromptCacheTtl` | new | Any | unset | – | TTL for requests outside the main conversation. |
| `switchModelsOnFlag` | new | Any | unset | – | Switch automatically or pause when a safety classifier flags a request. |
| `ultracode` | new | Any | unset | – | Claude plans a workflow for each substantive task. |

### Agents, sessions, and worktrees (12)

| Key | Snap | Scope | Default | Since | Behaviour |
|---|---|---|---|---|---|
| `agent` | yes | Any | unset | – | Run the main thread as this named agent, with its prompt, tools and model. |
| `crossSessionInbound` | new | Any | unset | 2.1.224 | Inbound session messages: `accept`, `hold`, `refuse`. |
| `disableAgentView` | new | Any | unset | – | Turn off background agents and agent view. |
| `isolatePeerMachines` | new | Any | unset | – | Ask before messaging your sessions on other machines; `true` honoured from any scope. |
| `processWrapper` | new | U,M | unset | 2.1.210 | Launcher prefix for background processes on macOS and Linux. |
| `teammateMode` | cfg | Any | `"in-process"` | – | Display mode for agent team teammates. |
| `worktree` | yes | Any | unset | – | Container for worktree configuration. |
| `worktree.baseRef` | new | Any | `"fresh"` | – | Branch new worktrees from remote default (`fresh`) or local HEAD. |
| `worktree.bgIsolation` | new | Any | `"worktree"` | – | Let background sessions edit without a worktree. |
| `worktree.location` | new | U | unset | – | Desktop SSH remote worktree location. |
| `worktree.sparsePaths` | sub | Any | unset | – | Sparse checkout directories. |
| `worktree.symlinkDirectories` | sub | Any | unset | – | Directories symlinked into each worktree. |

### Remote, desktop, and notifications (14)

| Key | Snap | Scope | Default | Since | Behaviour |
|---|---|---|---|---|---|
| `agentPushNotifEnabled` | cfg | Any | `false` | – | Allow Claude-initiated phone push notifications. |
| `awaySummaryEnabled` | new | Any | unset | – | `false` turns off the session recap on return. |
| `disableArtifact` | new | Any | unset | – | Deprecated; prefer `enableArtifact: false`. |
| `disableDeepLinkRegistration` | yes | Any | unset | – | `"disable"` skips registering `claude-cli://`. |
| `disableDesktopLocalSessions` | new | M | unset | – | `true` turns off on-device Desktop Code sessions. |
| `disableRemoteControl` | new | Any | `false` | – | Turn off Remote Control everywhere. |
| `enableArtifact` | new | Any | unset | – | `false` turns off the Artifact tool from any file; nothing turns it back on. |
| `inputNeededNotifEnabled` | cfg | Any | `false` | – | Push notification when Claude waits on you. |
| `preferredNotifChannel` | cfg | Any | `"auto"` | – | Task-completion notification channel. |
| `remote.defaultEnvironmentId` | sub | Any | unset | – | Default cloud environment for `claude --cloud`; `ccpool_` IDs read only from user, managed, `--settings`. |
| `remoteControlAtStartup` | cfg | Any | unset | – | Auto-connect Remote Control; project and local can only turn it off. |
| `sshConfigs` | yes | U,M | unset | – | SSH connections for the Desktop selector. |
| `sshHostAllowlist` | new | M | unset | – | Limit hosts for Desktop SSH sessions. |
| `sshHostCommands` | new | U,M | unset | – | Command-sourced SSH connections for Desktop. |

### MCP (10)

| Key | Snap | Scope | Default | Since | Behaviour |
|---|---|---|---|---|---|
| `allowAllClaudeAiMcps` | new | M | `false` | – | Keep self-fetched claude.ai connectors alongside a deployed `managed-mcp.json`. |
| `allowClaudeInChromeWithManagedMcp` | new | M | `false` | 2.1.282 | Keep the Chrome server running alongside a deployed `managed-mcp.json`. |
| `allowedMcpServers` | yes | Any | unset | – | Allowlist of MCP servers users may add; empty array blocks all. |
| `allowManagedMcpServersOnly` | yes | M | `false` | – | Only the managed MCP allowlist applies. |
| `deniedMcpServers` | yes | Any | unset | – | Block MCP servers by name, URL or command. |
| `disableClaudeAiConnectors` | new | Any | `false` | – | Do not fetch claude.ai connectors; `true` honoured from any scope. |
| `disabledMcpjsonServers` | yes | Any | unset | – | Reject named `.mcp.json` servers. |
| `enableAllProjectMcpServers` | yes | Any | unset | – | Approve all `.mcp.json` servers without prompting. |
| `enabledMcpjsonServers` | yes | Any | unset | – | Approve named `.mcp.json` servers. |
| `managedMcpServers` | new | M | unset | 2.1.259 | Remote MCP servers provided to every user. |

### Plugins and skills (22)

| Key | Snap | Scope | Default | Since | Behaviour |
|---|---|---|---|---|---|
| `allowedChannelPlugins` | yes | M | unset | – | Replace the default allowlist of channel plugins (`marketplace`, `plugin` objects). |
| `appendPlugins` | new | U,M | unset | – | Organisation mods run after every user mod. |
| `blockedMarketplaces` | yes | M | unset | – | Marketplace sources blocked for the organisation. |
| `channelsEnabled` | yes | M | unset | – | Allow channels for the organisation. |
| `disableBundledSkills` | new | Any | unset | – | Remove bundled skills and workflows. |
| `disableCommandPluginSources` | new | M | unset | 2.1.229 | Block plugins that install by running a marketplace-declared command. |
| `disableSkillShellExecution` | new | Any | unset | – | Stop inline shell in skills and custom commands. |
| `enabledPlugins` | yes | Any | unset | – | Map of `plugin@marketplace` to on or off. |
| `extraKnownMarketplaces` | yes | Any | unset | – | Register marketplaces for a repository or organisation. |
| `pluginConfigs` | yes | U,M | unset | – | Stored plugin option answers, including AGENTS.md `instructionFiles`. |
| `pluginSuggestionMarketplaces` | new | M | unset | – | Marketplaces allowed to surface install suggestions. |
| `pluginTrustMessage` | yes | M | unset | – | Text appended to the plugin trust warning. |
| `prependPlugins` | new | U,M | unset | – | Organisation mods run before every user mod. |
| `skillOverrides` | new | Any | unset | – | Hide or collapse skills without editing them. |
| `strictKnownMarketplaces` | yes | M | unset | – | Allowlist of marketplace sources; empty array is a full lockdown. |
| `strictPluginOnlyCustomization` | yes | M | unset | – | `true` or a list locking customisation to plugin and managed sources. |
| `strictPluginOnlyCustomization.agents` | sub | M | not locked | – | List value locking agents. |
| `strictPluginOnlyCustomization.hooks` | sub | M | not locked | – | List value locking hooks. |
| `strictPluginOnlyCustomization.mcp` | sub | M | not locked | – | List value locking MCP servers. |
| `strictPluginOnlyCustomization.skills` | sub | M | not locked | – | List value locking skills. |
| `syncClaudeAiPlugins` | new | U,L,M | unset | 2.1.273 | `false` stops loading and downloading account plugins. |
| `syncClaudeAiSkills` | new | U,L,M | unset | – | `false` stops loading and downloading account skills. |

### Hooks and automation (9)

| Key | Snap | Scope | Default | Since | Behaviour |
|---|---|---|---|---|---|
| `allowedHttpHookUrls` | yes | Any | unset | – | URL patterns, `*` wildcard, that HTTP hooks may target. |
| `allowManagedHooksOnly` | yes | M | unset | – | Run only hooks from the organisation. |
| `disableAllHooks` | yes | Any | unset | – | Turn off hooks, custom status line and custom `@` file suggestion together. |
| `disableWorkflows` | new | Any | `false` | – | Turn off dynamic workflows for everyone. |
| `enableWorkflows` | new | Any | unset | – | Personal workflows on or off, against the plan default. |
| `hooks` | yes | Any | unset | – | Hook commands keyed by lifecycle event. |
| `httpHookAllowedEnvVars` | yes | Any | unset | – | Variables HTTP hooks may put in headers. |
| `workflowKeywordTriggerEnabled` | new | Any | `true` | – | `false` stops `ultracode` in a prompt starting a workflow. |
| `workflowSizeGuideline` | new | Any | `"medium"` | – | Advisory agent-count target. |

### Authentication and providers (10)

| Key | Snap | Scope | Default | Since | Behaviour |
|---|---|---|---|---|---|
| `allowedProviders` | new | M | unset | 2.1.285 | Restrict API providers usable on the machine. |
| `apiKeyHelper` | yes | Any | unset | – | Shell command producing the API credential. |
| `awsAuthRefresh` | yes | Any | unset | – | Command that refreshes Bedrock credentials in `.aws`. |
| `awsCredentialExport` | yes | Any | unset | – | Command that outputs Bedrock credentials as JSON. |
| `forceLoginGatewayUrl` | new | U,M | unset | – | Gateway URL for the login screen. |
| `forceLoginMethod` | yes | Any | unset | – | Restrict login to claude.ai, Console or gateway. |
| `forceLoginOrgUUID` | yes | Any | unset | – | Pin claude.ai logins to one or more organisations; enforced only from managed. |
| `gatewayInternalNetworks` | new | M | unset | 2.1.268 | Up to four public IPv4 CIDR blocks `/login` may treat as internal. |
| `gcpAuthRefresh` | yes | Any | unset | – | Command that refreshes Google Cloud credentials. |
| `otelHeadersHelper` | yes | Any | unset | – | Command generating rotating OpenTelemetry headers. |

### Permission settings (15)

| Key | Snap | Scope | Default | Since | Behaviour |
|---|---|---|---|---|---|
| `allowManagedPermissionRulesOnly` | yes | M | unset | – | Only managed settings supply permission rules. |
| `autoMode` | yes | U,M | unset | – | User rules for the auto mode classifier: `environment`, `allow`, `soft_deny`, `hard_deny`. |
| `autoMode.classifyAllShell` | new | U,M | `false` | 2.1.193 | Send all shell commands through the classifier, even ones a narrow allow rule matches. |
| `disableAutoMode` | yes | Any | unset | – | `"disable"` removes auto mode from the cycle. |
| `permissions` | yes | Any | unset | – | Container for allow, ask, deny, directories and starting mode. |
| `permissions.additionalDirectories` | sub | Any | unset | – | Extra directories for file access; trust-gated from repository files. |
| `permissions.allow` | sub | Any | unset | – | Approve listed tool uses; trust-gated from repository files. |
| `permissions.ask` | sub | Any | unset | – | Always prompt for listed tool uses. |
| `permissions.blockReadsOutsideWorkingDirectories` | new | Any | unset | 2.1.257 | File tools refuse reads outside working directories in every mode; `true` honoured from any scope. |
| `permissions.defaultMode` | sub | Any | unset | – | Starting mode; `auto` and `bypassPermissions` ignored in project and local files. |
| `permissions.deny` | sub | Any | unset | – | Block listed tool uses. |
| `permissions.disableBypassPermissionsMode` | sub | Any | unset | – | `"disable"` prevents bypass mode. |
| `skipAutoPermissionPrompt` | yes | U,M | unset | – | Skip the one-time auto mode notice. |
| `skipDangerousModePermissionPrompt` | yes | U,L,M | unset | – | Skip the bypass mode confirmation. |
| `useAutoModeDuringPlan` | yes | U,L,M | `true` | – | Classifier reviews shell commands in plan mode. |

### Interface and terminal (39)

| Key | Snap | Scope | Default | Since | Behaviour |
|---|---|---|---|---|---|
| `askUserQuestionTimeout` | new | U,M | `"never"` | – | Idle time before an unanswered question auto-continues: `60s`, `5m`, `10m`, `never`. |
| `autoContinueAtUsageLimit` | new | U,M | `true` | 2.1.234 | Wait and continue automatically when a claude.ai usage limit resets. |
| `autoScrollEnabled` | new | Any | `true` | – | Follow new output in fullscreen rendering. |
| `axScreenReader` | new | U,M | unset | – | Screen-reader friendly rendering. |
| `bashEditDiffEnabled` | new | U,M | unset | 2.1.269 | Record files changed during a Bash command in every permission mode. |
| `companyAnnouncements` | yes | Any | unset | – | Messages shown at startup. |
| `defaultShell` | yes | Any | `"bash"` | – | Shell for `!` commands: `bash` or `powershell`. |
| `dialogExpiry` | new | U,M | `"5m"` | 2.1.224 | Wait before cancelling a dialog forwarded to Remote Control or an SDK host. |
| `editorMode` | cfg | Any | `"normal"` | – | `normal` or `vim` prompt editing. |
| `emojiCompletionEnabled` | new | Any | `true` | – | `false` disables `:shortcode:` suggestions. |
| `fileSuggestion` | yes | Any | unset | – | Command that supplies `@` file autocomplete. |
| `footerLinksRegexes` | new | U,M | unset | – | Regexes that turn IDs in output into footer links. |
| `keybindingFlavor` | new | Any | unset | – | Deprecated, no effect. |
| `maxProseWidth` | new | Any | unset | 2.1.282 | Column cap for response prose, minimum 40. |
| `prefersReducedMotion` | yes | Any | `false` | – | Reduce spinner, shimmer and flash animation. |
| `promptSuggestionEnabled` | yes | Any | `true` | – | `false` hides grey prompt suggestions. |
| `respectGitignore` | yes | Any | `true` | – | Keep gitignored files out of the `@` picker. |
| `respondToBashCommands` | new | Any | `true` | – | `false` stops Claude responding after `!` commands. |
| `showClearContextOnPlanAccept` | yes | Any | `false` | – | Show the clear-context option on plan accept. |
| `showTurnDuration` | cfg | Any | `true` | – | `false` hides the turn duration line. |
| `spellcheck` | new | U,M | unset | 2.1.235 | Prompt spell checking with an installed checker. |
| `spinnerTipsEnabled` | yes | Any | `true` | – | `false` hides spinner tips. |
| `spinnerTipsOverride` | yes | Any | unset | – | Add or replace tips. |
| `spinnerVerbs` | yes | Any | unset | – | Add or replace spinner verbs. |
| `statusLine` | yes | Any | unset | – | Command rendering a status line. |
| `subagentStatusLine` | new | Any | unset | – | Command rewriting subagent task rows. |
| `syntaxHighlightingDisabled` | yes | Any | `false` | – | Turn off syntax highlighting. |
| `terminalProgressBarEnabled` | cfg | Any | `true` | – | `false` hides the terminal progress bar. |
| `terminalTitleFromRename` | yes | Any | `true` | – | `false` stops `/rename` and `--name` changing the tab title. |
| `theme` | cfg | Any | `"dark"` | – | Interface theme, built-in or custom. |
| `timeFormat` | new | Any | `"auto"` | 2.1.257 | 12-hour, 24-hour, UTC or strftime times. |
| `timeZone` | new | Any | unset | 2.1.257 | IANA zone for displayed times. |
| `tui` | new | Any | unset | – | Fullscreen or classic renderer. |
| `verbose` | cfg | Any | `false` | – | Full tool output; `viewMode` wins. |
| `viewMode` | new | Any | unset | – | Starting view: default, verbose or focus. |
| `vimInsertModeRemaps` | new | U,M | unset | – | Two-key INSERT sequence mapped to Escape. |
| `voice` | new | Any | unset | – | Voice dictation with hold or tap mode. |
| `voiceEnabled` | yes | Any | unset | – | Older single-key dictation form. |
| `wheelScrollAccelerationEnabled` | new | Any | `true` | – | `false` disables wheel acceleration. |

### Git and attribution (7)

| Key | Snap | Scope | Default | Since | Behaviour |
|---|---|---|---|---|---|
| `attribution` | yes | Any | unset | – | Object controlling commit and PR attribution; `false` hides all (older clients skip a file with that form). |
| `attribution.commit` | sub | Any | unset | – | Commit trailer text; empty hides it. |
| `attribution.pr` | sub | Any | unset | – | PR description line; empty hides it. |
| `attribution.sessionUrl` | new | Any | `true` | – | `false` omits the claude.ai session link from cloud and Remote Control commits. |
| `includeCoAuthoredBy` | yes | Any | `true` | – | Deprecated; use `attribution`. |
| `includeGitInstructions` | yes | Any | `true` | – | `false` removes built-in commit and PR instructions and the git snapshot. |
| `prUrlTemplate` | new | Any | unset | – | URL template pointing PR links at an internal tool. |

### Memory and context (14)

| Key | Snap | Scope | Default | Since | Behaviour |
|---|---|---|---|---|---|
| `autoCompactEnabled` | cfg | Any | `true` | – | Automatic compaction on or off; also governs idle compaction. |
| `autoCompactWindow` | new | Any | unset | – | Token window (100000–1000000) before auto-compaction, capped at the model's window. |
| `autoMemoryDirectory` | yes | Any | unset | – | Absolute or `~/` path for auto memory; repository files honoured under the trust rule. |
| `autoMemoryEnabled` | yes | Any | `true` | – | Auto memory on or off. |
| `bashOutputMaxChars` | new | Any | unset | 2.1.261 | Inline output limit for successful shell commands, clamped 4000–128000; overrides `BASH_MAX_OUTPUT_LENGTH`. |
| `claudeMd` | new | M | unset | – | Inline managed CLAUDE.md text, loaded ahead of user and project files. |
| `claudeMdExcludes` | yes | Any | unset | – | Globs or absolute paths of CLAUDE.md and rules to skip; managed files cannot be excluded. |
| `env` | yes | Any | unset | – | Variables for the session and subprocesses; see [env-vars-reference.md](env-vars-reference.md). |
| `fileCheckpointingEnabled` | cfg | Any | `true` | – | File snapshots for `/rewind`; ignored in `-p` and SDK. |
| `idleCompaction` | new | Any | `true` | – | Compact idle conversations before the one-hour cache expires. |
| `plansDirectory` | yes | Any | unset | – | Project-relative plan path; outside the root falls back to `~/.claude/plans`. |
| `skillListingBudgetFraction` | new | Any | `0.01` | – | Share of the window for the skill listing, 0 to 1. |
| `skillListingMaxDescChars` | new | Any | `1536` | – | Per-skill description cap in the listing. |
| `taskOutputMaxChars` | new | Any | – | – | Removed in v2.1.277 with `TaskOutput`. |

### Global config settings (12)

| Key | Snap | Scope | Default | Since | Behaviour |
|---|---|---|---|---|---|
| `autoConnectIde` | cfg | G | `false` | – | Connect to a running IDE from an external terminal. |
| `autoInstallIdeExtension` | cfg | G | `true` | – | `false` stops automatic extension install from a VS Code terminal. |
| `claudeInChromeDefaultEnabled` | cfg | G | unset | – | Start sessions with Chrome integration on. |
| `copyFullResponse` | cfg | G | `false` | – | `/copy` copies the full response with no picker. |
| `copyOnSelect` | cfg | G | `true` | – | `false` stops auto-copy of mouse selection in fullscreen and agent view. |
| `defaultToAgentsView` | new | G | `false` | – | Bare `claude` opens agent view. |
| `diffTool` | cfg | G | `"auto"` | – | Where proposed changes open: `auto`, IDE viewer, or terminal. |
| `externalEditorContext` | new | G | `false` | – | Show Claude's last response as comments in Ctrl+G. |
| `leftArrowOpensAgents` | new | G | `true` | – | `false` disables `←` backgrounding into agent view. |
| `permissionExplainerEnabled` | cfg | G | `true` | – | Removed in v2.1.257 with the `Ctrl+E` explanation. |
| `prStatusFooterEnabled` | cfg | G | `true` | – | `false` removes the PR status badge and its check. |
| `teammateDefaultModel` | cfg | G | unset | – | Removed in v2.1.234. |

### Updates and versioning (4)

| Key | Snap | Scope | Default | Since | Behaviour |
|---|---|---|---|---|---|
| `autoUpdatesChannel` | yes | Any | unset | – | Release channel; unset follows `latest`. |
| `minimumVersion` | yes | Any | unset | – | Floor for auto-updates. |
| `requiredMaximumVersion` | new | M | unset | 2.1.163 | Refuse to start on a newer version. |
| `requiredMinimumVersion` | new | M | unset | 2.1.163 | Refuse to start on an older version. |

### Tools (3)

| Key | Snap | Scope | Default | Since | Behaviour |
|---|---|---|---|---|---|
| `browserExternalPageTools` | new | M | unset | – | `disabled` keeps Claude's tools off external pages in the desktop Browser pane. |
| `disableBrowserExternalNavigation` | new | M | unset | – | `true` limits the desktop Browser pane to localhost. |
| `disableMobileSimulatorTools` | new | M | unset | – | `true` blocks Claude's tools in the desktop iOS Simulator pane. |

### Privacy and telemetry (5)

| Key | Snap | Scope | Default | Since | Behaviour |
|---|---|---|---|---|---|
| `cleanupPeriodDays` | yes | Any | `30` | – | Days to keep transcripts and other swept data; `0` is a validation error. |
| `desktopSessionCleanupPeriodDays` | new | U,M | `0` | 2.1.248 | Age limit for Desktop and Cowork transcripts; `0` means none. |
| `feedbackDrafts` | new | U,M | `"notify"` | – | Claude-drafted feedback: `notify`, `quiet`, `off`. |
| `feedbackSurveyRate` | yes | Any | unset | – | Session survey probability, 0 to 1. |
| `skipWebFetchPreflight` | yes | Any | unset | – | Skip the WebFetch hostname check when Anthropic is unreachable. |

### Enterprise and managed settings (9)

| Key | Snap | Scope | Default | Since | Behaviour |
|---|---|---|---|---|---|
| `disableSideloadFlags` | new | M | `false` | 2.1.193 | Reject CLI flags that sideload plugins, subagents and MCP servers. |
| `forceRemoteSettingsRefresh` | new | M | `false` | – | Block startup until server-managed settings are freshly fetched. |
| `managedSourcesBehavior` | new | M | `"first-wins"` | – | `first-wins` or `merge` across managed sources. |
| `parentSettingsBehavior` | new | M | `"first-wins"` | – | Apply or drop restrictions from an SDK or IDE host. |
| `policyHelper` | new | M | unset | – | Executable computing managed settings at startup. |
| `policyHelper.path` | new | M | none | – | Absolute normalised helper path; required. |
| `policyHelper.refreshIntervalMs` | new | M | unset | – | Background re-run interval; `0` disables. |
| `policyHelper.timeoutMs` | new | M | `10000` | – | Helper wait, minimum 1000. |
| `wslInheritsWindowsSettings` | new | M | `false` | – | WSL reads the Windows policy chain. |

### Sandbox settings (39)

| Key | Snap | Scope | Default | Since | Behaviour |
|---|---|---|---|---|---|
| `sandbox` | yes | Any | unset | – | Container for Bash sandboxing configuration. |
| `sandbox.allowAppleEvents` | new | U,M | `false` | – | Let sandboxed commands send Apple Events. |
| `sandbox.allowNestedUserNamespaces` | new | U,M | `false` | 2.1.305 | Let sandboxed commands create user namespaces on Linux and WSL2. |
| `sandbox.allowUnsandboxedCommands` | sub | Any | `true` | – | Permit retrying blocked commands outside the sandbox. |
| `sandbox.autoAllowBashIfSandboxed` | sub | Any | `true` | – | Run sandboxed commands without prompting. |
| `sandbox.bwrapPath` | new | M | unset | – | Absolute bubblewrap path. |
| `sandbox.credentials` | new | Any | unset | – | Container for credential hiding and masking. |
| `sandbox.credentials.allowPlaintextInject` | new | U,M | `false` | – | Let masked credentials reach plain HTTP on trusted test networks. |
| `sandbox.credentials.awsPairs` | new | U,M | unset | 2.1.224 | Link custom AWS key variables for re-signing. |
| `sandbox.credentials.envVars` | new | Any | unset | – | Unset or mask variables (`name`, `mode`). |
| `sandbox.credentials.files` | new | Any | unset | 2.1.221 | Block or mask credential file reads (`path`, `mode`). |
| `sandbox.credentials.sigv4` | new | U,M | unset | 2.1.224 | Handling of streaming, presigned and SigV4A AWS requests. |
| `sandbox.enabled` | sub | Any | `false` | – | Turn on Bash sandboxing on macOS, Linux and WSL2. |
| `sandbox.enableWeakerNestedSandbox` | sub | Any | `false` | – | Run the Linux sandbox inside an unprivileged container. |
| `sandbox.enableWeakerNetworkIsolation` | sub | Any | `false` | – | Let Go-based CLIs verify TLS behind the proxy on macOS. |
| `sandbox.excludedCommands` | sub | Any | unset | – | Commands allowed outside the sandbox. |
| `sandbox.failIfUnavailable` | sub | Any | `false` | – | Refuse to start rather than run unsandboxed. |
| `sandbox.filesystem` | sub | Any | unset | – | Container for path rules. |
| `sandbox.filesystem.allowManagedReadPathsOnly` | sub | M | `false` | – | Stop developers re-opening managed read blocks. |
| `sandbox.filesystem.allowRead` | sub | Any | unset | – | Re-open reads inside a `denyRead` region. |
| `sandbox.filesystem.allowWrite` | sub | Any | unset | – | Additional writable paths. |
| `sandbox.filesystem.denyRead` | sub | Any | unset | – | Blocked read paths. |
| `sandbox.filesystem.denyWrite` | sub | Any | unset | – | Blocked write paths. |
| `sandbox.filesystem.disabled` | new | U,M | `false` | – | Turn off filesystem isolation, keeping network isolation. |
| `sandbox.ignoreViolations` | sub | Any | unset | – | Silence violation reports by command substring. |
| `sandbox.network` | sub | Any | unset | – | Container for network rules. |
| `sandbox.network.allowAllUnixSockets` | sub | Any | `false` | – | Allow every Unix socket. |
| `sandbox.network.allowedDomains` | sub | Any | unset | – | Pre-allowed domains. |
| `sandbox.network.allowLocalBinding` | sub | Any | `false` | – | Allow listening, and localhost on macOS. |
| `sandbox.network.allowMachLookup` | new | Any | unset | – | macOS XPC service names. |
| `sandbox.network.allowManagedDomainsOnly` | sub | M | `false` | – | Lock the allowlist to managed settings. |
| `sandbox.network.allowUnixSockets` | sub | Any | unset | – | Permitted socket paths on macOS. |
| `sandbox.network.deniedDomains` | new | Any | unset | – | Blocked domains, even inside an allowed wildcard. |
| `sandbox.network.httpProxyPort` | sub | Any | unset | – | Route HTTP through your own proxy. |
| `sandbox.network.socksProxyPort` | sub | Any | unset | – | Route SOCKS through your own proxy. |
| `sandbox.network.strictAllowlist` | new | U,M | `false` | 2.1.219 | Deny hosts outside the allowlist instead of prompting. |
| `sandbox.network.tlsTerminate` | new | U,M | unset | – | Proxy terminates TLS to inspect HTTPS. |
| `sandbox.ripgrep` | sub | U,M | unset | – | Custom ripgrep binary in the sandbox. |
| `sandbox.socatPath` | new | M | unset | – | Absolute `socat` path. |
## Failure modes & edge cases

- Keys marked Removed or Deprecated stay listed because the docs still list them. Setting a removed key has no effect.
- Keys scoped narrower than `Any` are ignored in other files, apart from a few off-switches. See [settings-system.md](settings-system.md).
- `cfg` keys moved or were mirrored into settings at v2.1.119, when `/config` began persisting to `settings.json`. Those still scoped `G` remain in `~/.claude.json`.
- A key with `Default` of `unset` can still behave conditionally. For example `enableWorkflows` defaults off on Pro.

## Changes since the snapshot

- 170 names appear as new by exact match. Of these, 38 are dotted children of snapshot keys and 21 existed as global config, leaving 111 with no snapshot match.
- 58 snapshot schema keys are not documented; they are listed by count only in `comparison/settings.md`.
- v2.1.119: `/config` options persist to `settings.json`.

## Open questions

- A `sub` mark rests on a leaf-name search, so a generic leaf could be a coincidental match.
- Whether the 58 undocumented snapshot keys are removed, internal or merely undocumented.
- `Since` is blank for most keys because the docs state no version in the entry's opening.
