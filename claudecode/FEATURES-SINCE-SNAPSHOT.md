# Features since the snapshot

The headline features of each week, taken from the public weekly digests. The digests stop at 2026 week 37, so the later months come from the changelog's "Added" entries. The complete record is in [releases/](releases/README.md).

## Week 37 (September 7–11, 2026)

**`claude plugin eval`**: run your plugin against a suite of test cases, score the results, and compare against a no-plugin baseline. `claude plugin eval init` drafts the cases and graders for you. Also this week: pop any **Claude Code Desktop pane** out into its own window and dock it back later; the **`maxEffortLevel`** setting caps the effort level on every provider; and a page that **WebFetch** hasn't finished downloading within five minutes fails instead of hanging.

## Week 36 (August 31 – September 4, 2026)

**Claude Fable 5.1**: available in Claude Code with a 1M-token context window. Also this week: on Pro and Max plans, **computer use in the Desktop app** works in the background on macOS while you keep working; in fullscreen rendering, **`/diff`** opens a live panel beside the conversation that refreshes as Claude edits; and **`/skill-doctor`** shows what each of your skills costs in context and how often it gets used.

## Week 35 (August 24–28, 2026)

**Resume terminal sessions in the Desktop app**: type `/resume` in the Claude Code Desktop prompt box to pick up any session you started from the CLI, with the full conversation and context intact. Also this week: **Claude-drafted feedback** has Claude write up a feedback report when something goes wrong in a session, which you review and send from `/feedback`; **`--restricted`** starts a session without the command-running tools or your user and project settings, for evaluation harnesses on shared machines; and the **`modelPicker`** setting controls which models the `/model` picker lists.

## Week 34 (August 17–21, 2026)

**`/design`**: a research preview that brings Claude Design's artboard workflow into the CLI and Claude Code Desktop, built on artifacts, so Claude drafts editable artboards for your UI and implements the one you pick. Also this week: the built-in **Concise output style** makes Claude lead with the result and skip preamble; any machine running `claude remote-control` shows up as a **device card** on your phone so you can start a session on it from the Code tab; and **`ANTHROPIC_DEFAULT_MODEL`** sets the model new sessions start on.

## Week 33 (August 10–14, 2026)

**Auto-continue after a usage limit on Desktop**: when you hit your session limit in Claude Code Desktop, check **Auto-continue when limits reset** on the limit card and the app retries the interrupted turn once the limit resets. Also this week: **fork mode** is on by default in interactive sessions, so Claude can delegate a side task to a subagent that inherits the full conversation; **GitLab** merge request URLs work with `--worktree` and the `claude agents` view, and marketplaces clone bare `gitlab.com` URLs; and typing **`@`** in the prompt mentions another Claude session by name.

## Week 32 (August 3–7, 2026)

**Cross-session messaging**: on macOS and Linux, your Claude Code sessions can now message each other, so Claude passes a finding or a decision from one session to another instead of you re-explaining it. Also this week: **self-hosted environments** run Claude Code cloud sessions on infrastructure your organization operates, in public beta on Team and Enterprise plans; **auto mode** becomes the default permission mode for new sessions on Pro, Max, and Team plans starting August 14; and the **VS Code extension** gets Focus view.

## Week 30 (July 20–24, 2026)

**Claude Opus 5**: the new default Opus model in Claude Code, with a 1M-token context window and fast mode at \$10/\$50 per MTok. Also this week: **Claude Code Desktop** opens an iOS Simulator pane in public beta so Claude can run your app and tap through it while you watch; the **Claude Security plugin** runs a multi-agent vulnerability scan of your codebase and turns the findings you pick into patches you apply yourself; and **`/code-review`** runs as a background subagent.

## Week 29 (July 13–17, 2026)

**Artifacts call your MCP connectors**: a published artifact can pull live data and take actions through each viewer's own MCP connectors when they open the page, and this week also adds public sharing links, editor roles on Team and Enterprise, and artifacts created from Claude Tag sessions. Also this week: **screen reader mode** replaces the visual terminal interface with plain, linear text for screen readers such as VoiceOver and NVDA; **`/fork`** copies your conversation into a new background session while you keep working; and **auto mode** no longer needs an opt-in variable on Amazon Bedrock, Google Cloud's Agent Platform, and Microsoft Foundry.

## Week 28 (July 6–10, 2026)

**In-app browser on Desktop**: Claude Code on desktop gets a built-in browser, so Claude can pull up docs, designs, or any other site and interact with pages the same way it does with your local dev server previews. Also this week: **`/doctor`** is a full setup checkup that diagnoses issues and can fix them, with `/checkup` as its alias; **auto mode** blocks transcript tampering and asks before `rm -rf` on unresolved variables; and **agent view rows** show a colored state word and a classifier-written headline.

## Week 27 (June 29 – July 3, 2026)

**Claude Sonnet 5**: the new default model for Pro, Team Standard, and Enterprise subscription seats, with top-tier coding and tool use at Sonnet pricing, a native 1M-token context window, and adaptive thinking on by default. Also this week: **Claude in Chrome** is generally available on all direct Anthropic plans; **subagents run in the background by default** so Claude keeps working while they run; **Claude Desktop on Linux** lands in beta on Ubuntu and Debian; and **`/radio`** tunes into Claude FM lo-fi radio.

## Week 26 (June 22–26, 2026)

**`claude mcp login`**: authenticate a configured MCP server from your shell instead of the interactive `/mcp` menu, and clear its stored credentials later with `claude mcp logout`. Also this week: **shell mode responds to command output** (`! npm test` gets an explanation without a second prompt); **`/rewind`** can resume a conversation from before `/clear` was run; and **background subagents** now surface permission prompts in the main session instead of auto-denying.

## Week 25 (June 15–19, 2026)

**Artifacts**: turn a session's output into a live, shareable page on claude.ai that updates in place as the session works, now in beta on Team and Enterprise plans. Also this week: **deny and ask rules match tool parameters** with `Tool(param:value)`, for example `Agent(model:opus)`; **`/config key=value`** sets any setting from the prompt, in `-p` mode, and from Remote Control; and **auto mode blocks destructive git commands** when you didn't ask to discard local work.

## Week 24 (June 8–12, 2026)

**`/cd`**: move the current session to a new working directory mid-conversation without rebuilding the prompt cache. Also this week: **sub-agents can spawn their own sub-agents** (background chains are capped at five levels deep); **`--safe-mode`** starts Claude Code with all customizations disabled for troubleshooting; and **`fallbackModel`** configures up to three fallback models tried in order.

## Week 23 (June 1–5, 2026)

**Auto mode on Amazon Bedrock, Google Cloud's Agent Platform, and Microsoft Foundry**: auto mode is now available on third-party providers for Opus 4.7 and Opus 4.8, replacing permission prompts with background safety checks. Also this week: **safer automatic edits** prompt before writing files that can run code in `acceptEdits` mode; **`/plugin list`** prints your installed plugins inline; and **version requirements** let managed deployments require an approved Claude Code version range.

## Week 22 (May 25–29, 2026)

**Claude Opus 4.8**: the new default model for Max, Team Premium, Enterprise pay-as-you-go, and Anthropic API accounts, with high effort by default and `/effort xhigh` for the hardest tasks. Also this week: **dynamic workflows** orchestrate dozens to hundreds of subagents from a script Claude writes; the **security-guidance plugin** reviews Claude's changes for vulnerabilities as it works; and **fast mode** runs on Opus 4.8 at \$10/\$50 per MTok.

## Week 21 (May 18–22, 2026)

**Auto mode on the Pro plan**: auto mode now runs on Pro accounts and supports Sonnet 4.6 alongside Opus, replacing permission prompts with background safety checks. Also this week: **`/usage`** breaks down what drives your plan limits by skill, subagent, plugin, and MCP server; the new **`/code-review`** command reports correctness bugs; and **background sessions** appear in `/resume` and stay alive when pinned.

## Week 20 (May 11–15, 2026)

**Agent view**: `claude agents` opens one screen for every Claude Code session, showing what's running, what's blocked on you, and what's done. Also this week: **`/goal`** keeps Claude working across turns until a completion condition holds; **fast mode** now runs on Opus 4.7 by default; and the **Rewind menu** can compress earlier context with "Summarize up to here".

## Week 19 (May 4–8, 2026)

**Plugins load from `.zip` archives and URLs**: `--plugin-dir` now accepts `.zip` files, and `--plugin-url` fetches a plugin archive for the current session. Also this week: **`worktree.baseRef`** chooses whether new worktrees branch from the remote default or local `HEAD`; **auto mode hard deny rules** block actions unconditionally regardless of allow exceptions; and **hooks see the active effort level** via `effort.level` and `$CLAUDE_EFFORT`.

## Week 18 (April 27 – May 1, 2026)

**Windows without Git Bash**: Git for Windows is no longer required, and Claude Code uses PowerShell as the shell tool when Bash is absent. Also this week: **`claude ultrareview`** brings cloud code review to CI and scripts; **`claude project purge`** cleans up local state for a project; and pasting a **PR URL into `/resume`** finds the session that created it.

## Week 17 (April 20–24, 2026)

**`/ultrareview`** opens as a public research preview: a fleet of bug-hunting agents runs in the cloud and findings land back in your CLI or Desktop automatically. Also this week: **session recap** shows you what happened while a terminal was unfocused; **custom themes** let you build and ship color palettes from `/theme` or a plugin; and **Claude Code on the web** gets a redesign with a new sessions sidebar and drag-and-drop layout.

## Week 16 (April 13–17, 2026)

**Claude Opus 4.7** lands as the new default on Max and Team Premium, with a new `xhigh` effort level that's the recommended setting for most coding work and an interactive `/effort` slider to dial it in. Also this week: **Routines** on Claude Code on the web fire templated cloud agents from a schedule, GitHub event, or API call; **mobile push notifications** ping your phone when a long task finishes or Claude needs you; `/usage` shows what's driving your limits; and the CLI moves to native binaries.

## Week 15 (April 6–10, 2026)

**Ultraplan** enters early preview: draft a plan in the cloud from your CLI, review and comment on it in a web editor, then run it remotely or pull it back local. The first run now auto-creates a cloud environment for you. Also this week: the **Monitor** tool streams background events into the conversation so Claude can tail logs and react live, `/loop` self-paces when you omit the interval, `/team-onboarding` packages your setup into a replayable guide, and `/autofix-pr` turns on PR auto-fix from your terminal.

## Week 14 (March 30 – April 3, 2026)

**Computer use** comes to the CLI in research preview: Claude can open native apps, click through UI, and verify changes from your terminal. Best for closing the loop on things only a GUI can verify. Also this week: `/powerup` interactive lessons, flicker-free alt-screen rendering, a per-tool MCP result-size override up to 500K, and plugin executables on the Bash tool's `PATH`.

## Week 13 (March 23–27, 2026)

**Auto mode** lands in research preview: a classifier handles your permission prompts so safe actions run without interruption and risky ones get blocked. The middle ground between approving everything and `--dangerously-skip-permissions`. Also this week: computer use in the Desktop app, PR auto-fix on Web, transcript search with `/`, a native PowerShell tool for Windows, and conditional `if` hooks.

## After the digests: Sep 12 to Oct 30

- 2.1.286: a count such as "2 of 5" to the permission prompt when several permission requests stack up
- 2.1.286: mouse support for the "N more" rows of lists in fullscreen mode: click one to jump to that end of the list, with hover and pressed states
- 2.1.285: `CLAUDE_CODE_DISABLE_WEB_FETCH` environment variable to turn off the WebFetch tool
- 2.1.285: `claude --desktop` to open the Claude desktop app on the current directory, or on a session with `--continue` / `--resume <id>`
- 2.1.285: `claude plugin configure <plugin>` to show a plugin's options and which are unset, or save new values read from stdin with `--values-stdin`
- 2.1.285: `<server>.<key>=<value>` to `claude plugin install --config`, so a bundled `.mcpb` MCP server's own settings can be set at install time and it starts without visiting `/plugin` → Configure
- 2.1.285: `allowedProviders` managed setting to limit which API providers a machine may use (Anthropic API, a custom endpoint, Bedrock, Mantle, Vertex AI, Foundry, Claude Platform on AWS, or a Cloud gateway)
- 2.1.285: `CLAUDE_CODE_NONSTREAMING_TIMEOUT_RETRIES` environment variable to cap re-sends of a non-streaming fallback request that timed out
- 2.1.284: Claude Sonnet 5.5 (`claude-sonnet-5-5`), now the default Sonnet model on the Anthropic API — 1M context, $2/$10 per Mtok with $0.20/Mtok cache reads
- 2.1.284: a "Yes, but ask again next time" answer to auto mode's prompt before a read outside the working directories, so you can allow that one read and still be asked about later ones
- 2.1.284: dollar amounts to the Claude apps gateway spend limit in `/usage` and the status line (for example "$271.40 / $500.00 spent this month") when the gateway runs this version or later; the status line's `rate_limits.spend_limit` also gains `used_usd`, `limit_usd` and `period`
- 2.1.284: `effortSlider:decreaseEffort`, `increaseEffort` and `toggleUltracode` keybinding actions, so the `/effort` slider's arrow and Tab keys can be rebound in `keybindings.json`
- 2.1.284: `/rate-limit-options` to `/help` and the command menu for claude.ai subscribers, so the usage-limit notices that mention it point to a command you can find
- 2.1.284: `/mcp reconnect all` in the interactive terminal to retry every MCP server that failed to connect or needs authentication at once
- 2.1.284: Claude apps gateway startup warnings when a managed policy's `availableModels` is empty, or leaves out the model Claude Code starts on without setting `model` or `enforceAvailableModels`
- 2.1.284: `auth: { google: {} }` for Claude apps gateway `telemetry.forward_to` destinations, so telemetry can be exported straight to Google Cloud's OTLP endpoint using the gateway's Google Cloud credentials
- 2.1.284: certificate client authentication (`private_key_jwt`) between the Claude apps gateway and its identity provider, for identity providers that issue certificate credentials instead of client secrets
- 2.1.283: `x-claude-code-prompt-id` to the gateway hint headers so LLM gateways can group the requests that serve one user prompt; opt in with `CLAUDE_CODE_GATEWAY_HINT_HEADERS=1`
- 2.1.283: `availableModelsMatch` managed setting: with `"exact"`, an `availableModels` entry allows only the model version it names, so new releases stay blocked until listed
- 2.1.283: `deniedModels` managed setting to block specific models, even when `availableModels` allows them
- 2.1.283: MCP tool, WebFetch and WebSearch outputs to the `tool.output` OpenTelemetry span event when `OTEL_LOG_TOOL_CONTENT=1`
- 2.1.283: `/doctor prompt-audit` (also `/checkup prompt-audit`) to audit your CLAUDE.md files, skills, agents and commands for prompting patterns written for older models
- 2.1.283: click-to-expand for truncated messages from your other sessions in fullscreen mode
- 2.1.283: `path` to `--plugin-dir` load-failure entries in the stream-json `system/init` `plugin_errors`, naming the directory that did not load
- 2.1.283: an opt-in `load_test_mode` block to the Claude apps gateway config: requests are built and signed but not sent upstream, and clients get a canned reply, so a deployment can be load tested
- 2.1.283: a `mantle` upstream provider to the Claude apps gateway for Amazon Bedrock's Mantle endpoint
- 2.1.282: a `maxProseWidth` setting that caps the width of Claude's prose in wide terminals while tables and code blocks keep the full width
- 2.1.282: a startup notice, and `/status` and `claude doctor` entries, listing telemetry variables in a project's settings files that were ignored or that turned telemetry off
- 2.1.282: the `allowClaudeInChromeWithManagedMcp` managed setting to let `claude --chrome` run alongside an exclusive `managed-mcp.json`; the error shown when Chrome is blocked now names it
- 2.1.282: `store.readiness_grace_seconds` to the Claude apps gateway so `/readyz` can stay ready through a short Postgres outage such as a database failover
- 2.1.282: a scrollbar to the `/feedback` drafts list in fullscreen mode; it appears while the mouse is over the list
- 2.1.281: Claude apps gateway support for newer Claude Desktop keys in `desktop` policy blocks, including `blockReadsOutsideWorkingDirectories` and `disableBypassPermissionsMode`
- 2.1.281: `assume_role` on Claude apps gateway Bedrock upstreams: the gateway calls Bedrock as an IAM role it assumes through STS, in another AWS account if needed, optionally one session per developer
- 2.1.281: `guardrail: {id, version}` on Claude apps gateway Bedrock upstreams to apply an Amazon Bedrock guardrail to every request sent through them (set it on all Bedrock upstreams or none)
- 2.1.281: `telemetry.resource_attributes` to the Claude apps gateway config, to put fixed labels on the telemetry of Claude Desktop and `/login` sessions
- 2.1.281: `"attribution": false` in `settings.json` to hide all commit and PR attribution; older CLI versions skip a settings file that holds it, so keep the object form in files shared across versions
- 2.1.281: MCP URL-mode elicitation on 2026-07-28 protocol connections, so servers can ask Claude Code to open a browser-based flow; no waiting dialog is left on screen when the server has no way to confirm completion
- 2.1.281: MCP server checks to `claude plugin validate`: it reports `.mcp.json` entries that would be silently dropped at load, undeclared `${user_config.*}` references, and insecure URLs
- 2.1.281: an auto mode recommendation to `/insights` that estimates how many permission prompts auto mode could have handled in your recent sessions
- 2.1.281: a scrollbar to the `/skills`, `/mcp` and `/plugin` Installed lists in fullscreen mode, like the one `/workflows` now has: it appears while the mouse is over the list and can be clicked or dragged
- 2.1.280: Claude Opus 5.5 (`claude-opus-5-5`), now the default Opus model — 1M context, $4/$20 per Mtok with $0.20/Mtok cache reads
- 2.1.280: mouse support to more lists in fullscreen mode: the wheel scrolls the `/skills` list, and a skill's state options in `/plugin` can be clicked
- 2.1.280: `CLAUDE_CODE_MAX_MCP_DESCRIPTION_LENGTH` to change the 2,048-character cap on MCP tool descriptions and server instructions for every MCP server in the session
- 2.1.280: hook output sizes and the number of oversized outputs saved to a file to the `hook_execution_complete` OpenTelemetry event
- 2.1.278: an `Auto mode server` row to `/status` showing whether this session's auto mode classifier runs on the server
- 2.1.277: AGENTS.md support: in a project with no CLAUDE.md, Claude Code reads AGENTS.md instead; change it under "Project instructions" in `/config`
- 2.1.277: `CLAUDE_GATEWAY_PROXY_IS_EGRESS_BOUNDARY=1` for Claude apps gateways whose only egress is a forward proxy: every outbound request hands the proxy the hostname instead of resolving it locally
- 2.1.277: an optional `headers:` map on Claude apps gateway upstreams, to send static headers to a proxy you run in front of a provider
- 2.1.277: a line saying a background task's update is waiting when it finishes while a panel such as `/tasks` is open
- 2.1.275: the signed-in account to Claude apps gateway sign-in: when the gateway names it, you confirm it before the credential is saved, and `/status` shows it
- 2.1.275: a send-now key (ctrl+enter, or ctrl+x ctrl+s) that interrupts the current turn and sends all queued messages at once; sent and queued messages show in gray until the model receives them
- 2.1.275: a startup warning when a configured `otelHeadersHelper` fails, so sessions that silently export no telemetry are noticed
- 2.1.275: syncing of the skills and plugins enabled on your claude.ai account to terminal sessions signed in with it; opt out with `syncClaudeAiSkills: false` or `syncClaudeAiPlugins: false`
- 2.1.275: `/plugin install <plugin> --marketplace <source>`, which offers to add the marketplace before installing the plugin
- 2.1.274: a visible warning when memory usage is critical, with steps to free memory or restart safely
- 2.1.274: `CLAUDE_CODE_MCP_STARTUP_WAIT_MS` to bound how long the first non-interactive turn waits for connecting MCP servers (`0` = don't wait)
- 2.1.274: `effort` attribute to the `claude_code.llm_request` OpenTelemetry trace span, matching the `api_request` event
- 2.1.274: `claude_code.managed_settings_resolved` OTel event: managed-settings sources and policy helper state; redacted settings and digests with `OTEL_LOG_MANAGED_SETTINGS=1`
- 2.1.274: `store.connect_timeout_seconds` to the Claude apps gateway config to lengthen the Postgres connect timeout (default 5 seconds), and improved the boot error when the database is unreachable to point to `store.postgres_url` and the configured timeout
- 2.1.274: `enduser.sub`, the IdP subject, to the telemetry Claude Desktop and Cowork send through a Claude apps gateway
- 2.1.274: a Claude apps gateway warning when a replica has more requests open than the 256 it sends upstream at once, and a startup log line showing that limit
- 2.1.274: click-to-expand for collapsed teammate and agent messages in fullscreen mode
- 2.1.273: `x-claude-code-request-class`, `x-claude-code-agent-type`, `x-claude-code-prev-tool-durations`, `x-claude-code-compaction` and `x-claude-code-context-compacted` request headers for LLM gateways; opt in with `CLAUDE_CODE_GATEWAY_HINT_HEADERS=1`
- 2.1.273: a notification when an MCP server disconnects mid-session and automatic reconnection gives up, pointing at `/mcp`
- 2.1.273: forking a session started with `claude --remote-control` or `/remote-control` from the Claude app; the fork runs as a background session on your computer
- 2.1.271: fast mode in Claude Code Remote sessions (cloud and self-hosted runners): the host's fast-mode setting or `/fast` typed in the session applies where your organization allows it
- 2.1.271: mouse support to the `/config` panel in fullscreen mode: the wheel scrolls the settings list, a click on a setting's value changes it, and the row under the pointer is highlighted
- 2.1.271: `claude self-hosted-runner --drain-marker-file <path>`: when that file exists at a SIGTERM drain, the runner reports its exit to the server as a host drain (telemetry only)
- 2.1.271: per-command `allowed_domains` to Bash, PowerShell and Monitor in auto mode with sandboxing: the hosts a command needs are reviewed with it and opened for it alone; other hosts are refused
- 2.1.271: `omitClaudeMd` to agent frontmatter and `--agents` JSON, letting custom and plugin subagents run without user, project and local CLAUDE.md files; managed policy files still load
- 2.1.271: `--accept-command <sha256>` to `claude plugin install` and `claude plugin update` to accept exactly the command a previous `--json` run displayed, instead of `-y`
- 2.1.271: support for a `multiplier` above 1, up to 10, in the `modelPricing` managed setting and the Claude apps gateway `pricing` block, for marked-up internal chargeback rates
- 2.1.271: a spinner tip pointing Bedrock, Vertex AI, Foundry and LLM gateway users to the Claude desktop app; the claude.ai desktop app tip now suggests `/desktop`, which offers to download the app
- 2.1.314: `permissions.blockWritesOutsideWorkingDirectories`: Write, Edit and NotebookEdit refuse paths outside the working directories in every permission mode
- 2.1.314: an optional `groups` list to Claude apps gateway upstreams: only developers in the listed IdP groups are sent to that upstream, on failover too
- 2.1.314: `guardrail_trace` to Claude apps gateway Bedrock upstreams, to log which Amazon Bedrock guardrail filter fired on a request, without the matched text
- 2.1.314: idle compaction to VS Code and Claude Desktop's Code tab: a 200K+ token conversation left idle is summarized, and the summary is used on your next message if the prompt cache has expired
- 2.1.312: `oidc.user_id_claim` to the Claude apps gateway, to identify people by an id_token claim other than `sub`, such as Microsoft Entra ID's `oid`
- 2.1.312: click to send: in fullscreen, clicking the "to send now" hint under a queued message sends it right away, as its key does
- 2.1.311: `--hold-idle-file` and `--max-hold-min` to `self-hosted-runner`, to keep an idle session while your host reports processes it left running
- 2.1.311: a tip for the Explanatory output style, shown when you ask Claude for explanations
- 2.1.310: the Monitor tool and plugin monitors on Bedrock, Vertex, and Foundry, and when telemetry or nonessential traffic is disabled; long foreground sleeps are now blocked there too
- 2.1.307: `/claude-api api-version` to move Claude API code to API version `2026-10-21`
- 2.1.307: the `claude_code.safety_event` OpenTelemetry event for each tool call a permission rule, auto mode, a safety check, a hook or the sandbox stopped, prompted or sent back
- 2.1.305: `sandbox.allowNestedUserNamespaces` so sandboxed commands on Linux can create user namespaces (Chromium, rootless podman); this lets them get around the sandbox's file protections
- 2.1.305: `CLAUDE_CODE_RETRY_WATCHDOG_USAGE_LIMIT_RECHECK_MS` so unattended retry mode (`CLAUDE_CODE_RETRY_WATCHDOG`) notices a usage limit that was lifted before its reset
- 2.1.304: a transcript line when a plugin that runs first skips one of your mod's hooks, naming the event and the plugin
- 2.1.304: `decider: "person"` to a mod's `tool.check` answer: only the permission dialog or a host's callback can approve the ask, and it is refused with the mod's reason where nobody can be asked
- 2.1.304: `e.isReadOnly` to a mod's `tool.check` event, set when the tool call is read-only
- 2.1.304: `/auto-mode-setup`: a guided setup that reads your project and recent sessions to teach auto mode about your environment, now also available on Bedrock, Vertex, Foundry, Claude apps gateway and telemetry-disabled sessions
- 2.1.304: `/claude-api managed-agents-secure`, which compares a Managed Agents agent's settings with Anthropic's published security guide, without changing anything
- 2.1.304: the names of the tools called earlier to the compaction summary in the transcript view (Ctrl+O)
- 2.1.304: a warning on Pro and Max plans when resuming an inactive conversation would use a noticeable share of your 5-hour usage limit: resume anyway, or start a new conversation and Claude can look up the previous one if you refer to it
- 2.1.302: `CLAUDE_CODE_AUTO_MODE_MODEL` to choose the model the client-side auto mode classifier uses; it does not change the model for server-side auto mode
- 2.1.302: an `Idle compaction` row to `/config` for turning idle compaction off or back on; the notices shown after an idle compaction now say how to turn it off
- 2.1.302: a notice to `/design-sync` and `/design-login` that standalone Claude Design (claude.ai/design) closes by December 14, 2026
- 2.1.301: `CLAUDE_CODE_RETRY_WATCHDOG_MAX_USAGE_LIMIT_WAIT_MS` so unattended retry mode (`CLAUDE_CODE_RETRY_WATCHDOG`) ends a request at a usage limit that resets too far away instead of waiting
- 2.1.301: OpenTelemetry tracing guidance to the `claude-api` skill, including setting up trace destinations with the `ant` CLI
- 2.1.301: the `%` motion to vim mode: jump to the matching bracket, alone or with d/c/y
- 2.1.301: `rows` to a mod's `Input`: a text field of several lines in the terminal, where Enter submits and Shift+Enter or a backslash before Enter starts a new line
- 2.1.301: `classifier_verdict` and `permission_mode` to OpenTelemetry `tool_decision` events, so auto mode classifier decisions can be told apart from permission rules
- 2.1.301: `classifier_category` to OpenTelemetry `tool_decision` events, naming the built-in rule a classifier block matched, when `OTEL_LOG_TOOL_DETAILS=1`
- 2.1.300: `virtualText` to a mod's prompt decorations: text drawn in the prompt box that never enters the draft or the submitted prompt
- 2.1.300: `cache_creation_5m_tokens` and `cache_creation_1h_tokens` to the OpenTelemetry `api_request` event, splitting cache writes by lifetime
- 2.1.300: `$.ui.view({ agentId })` for mods: shows an agent's transcript in the main view when you ask, and `$.ui.view({})` goes back
- 2.1.300: a `dir` prop on a mod's `Text` for right-to-left text: on Windows and in VS Code's terminal its rows read in that direction and sit flush right
- 2.1.300: `/advisor` on Claude Platform on AWS; no advisor runs until you pick one with `/advisor`, `advisorModel` or `--advisor`, and `CLAUDE_CODE_DISABLE_ADVISOR_TOOL=1` turns it off
- 2.1.300: OpenTelemetry GenAI semantic-convention attributes to trace spans, such as `gen_ai.provider.name`, `gen_ai.conversation.id`, `gen_ai.tool.name` and `error.type`
- 2.1.300: support for rewriting a workflow agent's `prompt` and `model` in the `agent.spawn` mod hook, which could only refuse workflow agents before
- 2.1.300: the `prompt.change` mod hook, raised when the prompt box's text changes without a typed edit: a recalled history entry, a clear, an undo, or a plugin's fill
- 2.1.299: `CLAUDE_CODE_DISABLE_FILE_MENTIONS` environment variable: Claude gets the paths of `@` file mentions to read with its file tools, not the files' contents
- 2.1.299: idle compaction in the terminal: a 200K+ token conversation left idle for about 54 minutes is compacted before its one-hour prompt cache expires, so your next message doesn't reprocess it all
- 2.1.299: `CLAUDE_CODE_IDLE_COMPACT_MIN_TOKENS` to change idle compaction's 200K-token minimum; `"idleCompaction": false` in settings.json turns it off. Both need v2.1.290 or later
- 2.1.299: `$.prompt.media` so a `prompt.submit` hook of a mod installed by managed settings can read the bytes of an image or document attached to the prompt
- 2.1.299: `$.session.identity()` for mods installed by managed settings: how the session is signed in, and its organization and email when managed `forceLoginOrgUUID` lists that organization
- 2.1.299: `size`, `weight`, `mono` and `tabular` to a mod's `Text` and named spacing steps (`xs` to `xl`) to its `Box`; `bold` is deprecated in favor of `weight`
- 2.1.299: `--shutdown-drain-sec` to `claude self-hosted-runner orchestrator`: on SIGTERM it stops polling and gives the poll in flight and running spawn hooks up to that many seconds to finish
- 2.1.299: the skill's frontmatter, source, plugin name and file path to what a mod's `skill.prompt` hook receives
- 2.1.299: `/effort` and `/fast` in agent view to set what new sessions start with; a bare `/model`, `/effort` or `/fast` there now opens a picker
- 2.1.299: a "safe mode" line to the agents view peek panel for background sessions started with `--safe-mode`
- 2.1.299: a one-time note when plan mode won't ask before most edits or commands because bypass permissions is available
- 2.1.299: `--disallow-tools` and a `disallowed_tools` case field to `claude plugin eval` to keep specific built-in tools, such as Agent, out of eval runs
- 2.1.299: support for turning off the attribution block in Claude Desktop's Code tab: set `CLAUDE_CODE_ATTRIBUTION_HEADER=0` in the `env` of a Claude apps gateway's `code` policy
- 2.1.299: a field to the attribution block in Claude Code sessions behind a Claude apps gateway; remove the block with `CLAUDE_CODE_ATTRIBUTION_HEADER=0`
- 2.1.299: a `queue` door to the `session.append` mod hook, so a mod can make the transcript's queue records differ from the prompt as sent
- 2.1.299: a note in `/plugin` and `claude plugin validate` naming a mod's hooks that are skipped where an organization manages Claude Code
- 2.1.299: `/usage` warnings for max effort, workflows, always-on context and large tool results
- 2.1.296: a `code` key to the Claude apps gateway's `managed.policies[]`: the same settings as `cli`, also applied in Claude Desktop's Code tab; beside `desktop`, it turns on Claude Desktop's gateway mode
- 2.1.296: `autoCompactWindow` to subagent frontmatter and `--agents` definitions, so a subagent can auto-compact earlier than the main conversation's window
- 2.1.296: `CLAUDE_CODE_WORKFLOW_SUBAGENT_MODEL` to run every workflow agent on one model while other subagents keep theirs
- 2.1.296: `CLAUDE_CODE_OVERLOADED_RETRY_MAX_DELAY_MS` environment variable to set a longer maximum delay for the backoff when retrying an overloaded (529) request
- 2.1.296: a note in `/plugin` on a plugin whose hooks are left out because another enabled plugin has the same name
- 2.1.296: an `allow_large` option to the Read tool so Claude can read a text file past the usual size limits in one call when it needs the whole file and the context has room
- 2.1.295: `onFailure: "block"` for command and HTTP hooks: a hook that can't start, times out, or exits with an unexpected code blocks the action instead of letting it through
- 2.1.295: Program Status Protocol (OSC 7501) support: terminals that implement it can show whether Claude Code is working, waiting on you, or done
- 2.1.295: quoted text to the `/copy` picker, so a drafted message copies without its `>` markers
- 2.1.295: a warning to `claude plugin install`, `enable`, `disable` and `marketplace add` when the settings file they write to does not load
- 2.1.295: a line on stderr, when it is a terminal, that says what a `claude -p` run is waiting for when it stays open after its last turn
- 2.1.295: support for `timeouts.upstream_ttfb_ms` on the Claude apps gateway's Bedrock, Vertex, Foundry and other cloud upstreams: a value you set now limits how long a stream may take to start there, after which it fails over or gets a 502
- 2.1.295: a "Backgrounding cancelled" message when you stop the turn while `←` is waiting for the current tool to finish
- 2.1.295: an optional `models` list to every Claude apps gateway upstream: only the listed models are sent there, on failover too, and one `*` in an entry is a wildcard
- 2.1.295: support for `forceLoginMethod: "gateway"` and `forceLoginGatewayUrl` in your own user settings on machines with no managed settings, so `/login` opens on that Claude apps gateway
- 2.1.295: advice to `claude plugin validate` when a plugin's README has no install line: it prints the line to paste and never changes the exit code, even with `--strict`
- 2.1.295: `upstream_request_id` to the Claude apps gateway's `inference` audit event: the request ID from Amazon Bedrock, the Anthropic API or another upstream, for support cases
- 2.1.295: `$.ui.notify` for mods: raises a native notification through your own notification setting and says which channel sent it
- 2.1.295: children to a mod's `Button`: strings and `Text`, so a row of a list is one pressable with a chip or a dim detail inside
- 2.1.295: `CLAUDE_CODE_RETRY_WATCHDOG_MAX_WAIT_MS` to limit how long unattended retry mode (`CLAUDE_CODE_RETRY_WATCHDOG`) waits out 429 and 529 errors
- 2.1.295: a `request-id` header to the Claude apps gateway's successful inference responses, so `request_id` in Claude Code telemetry matches the gateway's audit log
- 2.1.293: Claude Haiku 5.5 (`claude-haiku-5-5`), now the default Haiku model on the Anthropic API — 1M context, $0.10/$0.50 per Mtok ($0.50/$2.50 for prompts over 100K)
- 2.1.293: `agentType` to the `subagentStatusLine` payload, so scripts can tell custom subagent types apart
- 2.1.293: `isDeferred` to `$.tool.register` for mods: `false` lists the tool's schema in the prompt from the start instead of behind tool search
- 2.1.292: `--marketplace <source>` to `claude plugin install`: adds the marketplace if needed, under the same policy checks as `claude plugin marketplace add`, then installs the plugin from it
- 2.1.292: an `effort` parameter to the Agent tool, so Claude runs a sub-agent at the effort level you ask for
- 2.1.292: `CLAUDE_CODE_OVERLOADED_RETRY_BASE_DELAY_MS` environment variable to set a longer base delay for the backoff when retrying an overloaded (529) request
- 2.1.292: `prompt.autocomplete`, an event a mod hooks to add its own rows to the prompt box's autocomplete list
- 2.1.292: prompt caching to `$.model.complete` for mods: `prompt` and `system` take blocks of text, and `cache: true` on a block caches the request up to it
- 2.1.292: workflow agents to the `agent.spawn` mod hook, with their run and index, so a mod can refuse them
- 2.1.290: `serverToolUses` to the result of a mod's `turn.step` hook: the tool calls the API ran itself (the advisor), each with its id, name, input, start and end
- 2.1.290: `agentId` to the `tool.check` event of plugin hooks, so a hook can tell a subagent's permission check from the main session's
- 2.1.290: `ceiling` to the question and verdict a mod's `tool.check` hook reads, naming the approval an organization requires for a tool
- 2.1.290: `ThemeKey` and `Color` types to the plugin hooks typings, so an editor lists the theme colors a mod's drawing can name
- 2.1.290: to `claude plugin validate`: each hook a mod registers at a gating site is listed with whether it has a `.catch` (`gatingHooks` under `--json`)
- 2.1.290: a Deny button to the Claude apps gateway's sign-in approval page: it ends the pending sign-in, so the waiting terminal stops within seconds
- 2.1.290: `claude attach <name>` and `claude logs <name>`: part of a session name works in place of the id
- 2.1.290: `/claude-api managed-agents-onboard <url>` to set up the Managed Agents pattern a page describes as `ant apply` files
- 2.1.290: `/claude-api managed-agents-onboard <quickstart-name>` to build a Console quickstart template, such as `deep-researcher`, with the `ant` CLI
- 2.1.290: a warning when a managed settings file is a link to a file outside the managed settings folder
- 2.1.290: a /status and doctor warning when managed settings ignore user-configured sandbox allowRead paths or allowed domains
- 2.1.289: `agent.spawn` for teammates, one agent id across plugin hook events, and idle and waiting states in `$.agent.list()`
- 2.1.288: `$.ui.selection()` for mods: returns the text you last selected in fullscreen mode and, when the selection lies within one transcript row, that row
- 2.1.288: a built-in `gh api` to cloud sessions whose image has no GitHub CLI, and fixed the built-in sending control characters from file names, jq filters or GitHub errors to the terminal
- 2.1.288: recovery for a prompt cleared with Ctrl+C: pressing Up on the empty prompt brings the draft back, including pasted text and images
- 2.1.288: a re-authenticate prompt when an MCP server asks for more OAuth scope during a tool call
- 2.1.288: `--max-findings <n>|all` to /code-review to report more or fewer findings than the usual limit; the choice is reused until you pass `--max-findings default`
- 2.1.288: Ctrl+F to find a session by name and Alt+↑/↓ to jump between groups in the agents view; both, and rename, can be rebound in keybindings.json
- 2.1.288: a screen reader mode announcement of the new permission mode when you approve a plan, including with Shift+Tab
- 2.1.287: Claude Mods: plugins may now modify deeper behavior
- 2.1.287: You should know, a built-in mod where a side agent watches your back and flags things you or Claude might miss. Turn it on with `/plugin enable cc-plugin-you-should-know@builtin` (for first-party sessions with telemetry on)
- 2.1.287: an `n:<text>` filter to the agents view that matches session names and tasks; a filter now shows matches in collapsed sections and Enter opens the first match
- 2.1.287: `prompt_text` to the OpenTelemetry `user_prompt` event, a copy of `prompt` for backends that nest dotted keys; drop or mask it wherever you drop or mask `prompt` (anthropics/claude-code#70763)
- 2.1.287: URL prompts from MCP servers on the 2025-11-25 protocol, for example to sign in. If a server no longer connects after this update, add "bareElicitationCapability": true to its MCP config entry
