# Slash command system

**Status:** shipped
**Provenance:** both
**Sources:** docs `commands`, `interactive-mode`, `skills`, `errors`, `keybindings`; snapshot `commands.ts`, `types/command.ts`, `commands/`, `hooks/useTypeahead.tsx`, `components/PromptInput/PromptInputFooterSuggestions.tsx`; changelog 2.1.84 through 2.1.284

## Purpose

Define how `/` commands are registered, filtered, dispatched and queued. The command list itself is in [slash-commands-catalogue.md](slash-commands-catalogue.md). Snapshot-only names are in [slash-commands-snapshot-only.md](slash-commands-snapshot-only.md).

## Behaviour

### Sources

1. The `/` menu merges built-in commands, bundled skills, bundled workflows, user and project skills, `.claude/commands/` files, plugin commands and skills, and MCP prompts.
2. Three public kinds appear in docs: built-in (coded into the CLI), **Skill** (a prompt handed to Claude) and **Workflow** (a bundled dynamic workflow fanning out subagents).
3. Snapshot built-ins have one of three types: `local` (returns text), `local-jsx` (renders a dialog), `prompt` (expands into model input). Fields include `name`, `aliases`, `description`, `argumentHint`, `isEnabled`, `isHidden`, `immediate`, `availability`, `supportsNonInteractive`.
4. A skill can shadow a command name. Bundled skill aliases such as `/checkup` and `/review` MUST still resolve when a user skill shadows the name, including in `-p` (2.1.233).
5. `disableBundledSkills` turns off bundled skills. `/doctor` stays typable; `DISABLE_DOCTOR_COMMAND` or a `skillOverrides` entry hides it.
6. `--disable-slash-commands` disables all skills and commands.
7. `skillOverrides` set under an alias apply to the underlying skill.

### Parsing

8. A command is recognised only at the start of the message. Following text is its arguments.
9. Several skills may start one message, up to six: `/skill-a /skill-b do XYZ` loads both and passes the trailing text to each. Terminal prompt only.
10. `command:<name>` in keybindings runs a command from a key.

### Menu filtering

11. Typing after `/` filters the menu.
12. The top suggestion is highlighted only when the letters match a name or alias from the start of the name or of a word in it, ignoring `:`, `_` and `-`. `/adddir` highlights `/add-dir`; `/new` highlights `/clear` through its alias. `Enter` runs the highlighted row (2.1.236 rules).
13. After a typo, nothing is highlighted. Close matches stay listed for `Tab` or arrows, but `Enter` submits as typed and reports `Unknown command`, with or without a `Did you mean` suggestion.
14. Unavailable commands are left out. With nothing matching, the menu shows `No commands match "/name"` (2.1.116).
15. Most unavailable commands return `Unknown command`. Some answer with their own availability message or a policy message, such as `/schedule` on a Console key, cloud commands disabled by policy, and `/feedback` disabled.
16. Hidden commands such as `/heapdump` never surface on partial names. They appear only once the full name is typed, and run on submit.
17. Matched characters are bolded, blue marks only the selected row, and the selected row starts with `❯` (2.1.119, 2.1.227, 2.1.290). Long descriptions wrap to a second line (2.1.119).
18. Fullscreen: hover highlights and click accepts (2.1.145).
19. `claude agents` dispatch input matches substrings (2.1.157).

### Availability

20. Commands may depend on platform, plan, provider, auth or environment. `/desktop` needs macOS or x64 Windows and a subscription; `/upgrade` does not show on Enterprise.
21. Snapshot `availability` values: `claude-ai`, `console`. Unavailable commands were hidden from 2.1.84.
22. `/feedback` explains why it is unavailable rather than disappearing (2.1.91).
23. `/rate-limit-options` moved into `/help` and the menu for subscribers (2.1.284).

### Timing during a turn

24. By default a command sent during a turn queues and runs after the turn, in order.
25. Some run at once without interrupting: `/status`, `/tasks`, `/usage`, `/model`, `/effort`, `/fast`, `/btw`.
26. In fullscreen, dialog commands such as `/theme`, `/help`, `/config`, `/autocompact`, `/advisor` open immediately (2.1.234).
27. `/add-dir` asks at once, and the next tool call in the same turn can use the directory (2.1.234). `/permissions` opens at once and applies from the next tool call (2.1.234). `/feedback` and `/bug` open at once (2.1.232). `/doctor`'s view could open mid-turn from 2.1.116.
28. New-setting semantics:
    - `/model`: applies from the next request in the turn, after any cache warning.
    - `/effort`: applies to the next message, or mid-turn if a message is queued during tool calls.
    - `/fast`: the running turn keeps its speed. Turning it on with an unsupported model also switches the model from the next request.

### Non-interactive use

29. Commands marked for `-p` work there: `/config key=value`, `/color`, `/rename`, `/effort` (2.1.205), `/model <arg>` (2.1.205, not saved), `/mcp` (text summary), `/reload-plugins` (2.1.260), `/advisor <arg>`, `/import` (lists and gives a confirm command).
30. Interactive-only commands report accordingly.
31. `/recap` runs only when the user asks. If relayed from Slack, Teams, a project thread or a scheduled task prompt, a notice replaces it.

### Output placement

32. `/release-notes` writes to the transcript without entering Claude's context.
33. Dialogs follow shared frames, hints and list rows (2.1.283, 2.1.286).

## Configuration & interfaces

| Item | Meaning |
|---|---|
| `disableBundledSkills` | Disable bundled skills |
| `--disable-slash-commands` | Disable all commands and skills |
| `command:<name>` | Keybinding action |
| `DISABLE_DOCTOR_COMMAND`, `DISABLE_FEEDBACK_COMMAND`, `DISABLE_INSTALL_GITHUB_APP_COMMAND`, `DISABLE_LOGIN_COMMAND`, `DISABLE_LOGOUT_COMMAND`, `DISABLE_UPGRADE_COMMAND` | Hide or disable the named command |
| `CLAUDE_CODE_NEW_INIT` | Interactive `/init` flow |

## Failure modes & edge cases

- `/foo` mid-sentence is plain text, though completion may offer it.
- A path such as `/tmp/x` at the start of a message is treated as a command attempt, and can report `Unknown command`.
- `!` and `/` commands with an unavailable paste placeholder cancel submission.

## Changes since the snapshot

- 2.1.91: `/feedback` explains unavailability.
- 2.1.116: `No commands match`.
- 2.1.119: match highlight, wrapped descriptions.
- 2.1.145: mouse.
- 2.1.227, 2.1.236, 2.1.290: highlighting rules and pointer.
- 2.1.234: immediate dialogs in fullscreen.

## Open questions

- Full list of commands that run immediately.
- Whether snapshot command fields remain.
- Whether chaining six skills also works from Remote Control or SDK input.
