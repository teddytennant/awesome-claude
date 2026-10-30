# Output Styles

**Status:** shipped
**Provenance:** both (mechanism in snapshot; Proactive and Concise styles, mid-session switching, SDK and Remote Control selection post-leak)
**Sources:** docs `output-styles`, `errors`; snapshot `outputStyles/loadOutputStylesDir.ts`; changelog 2.1.94; versions from docs.

## Purpose

An output style sets the model's role, tone and format for a whole session by changing the system prompt. It is an instruction, not an enforcement mechanism.

## Behaviour

1. The active style's instructions MUST be sent with every request.
2. `default` means no style. It MUST appear in the `/output-style` list.
3. Built-in styles (`Proactive`, `Concise`, `Explanatory`, `Learning`) MUST keep the standard instructions and add their own.
   - **Proactive**: start work immediately, assume on routine decisions, avoid plan mode unless asked, and check in the conversation before destructive or shared-system actions. It MUST NOT change the permission mode.
   - **Concise** (v2.1.237): lead with the result; no lead-in, narration or recap. Full length still applies to requested detail and to anything needed to act safely.
   - **Explanatory**: adds conversational `Insight` blocks, never file comments.
   - **Learning**: adds `Insight` blocks, leaves `TODO(human)` spots at real design decisions, and waits for the user.
4. `/output-style <style>` is case-insensitive. With no argument it lists styles and marks the current one. It works in `-p`, SDK and Remote Control sessions (v2.1.269); over Remote Control only built-in styles can be selected or listed.
5. The command, `/config` menu and VS Code menu (v2.1.257) MUST save to `.claude/settings.local.json`.
6. The `outputStyle` setting is case-sensitive, and a non-match gives Default. Project settings override user settings.
7. A switch applies from the next message (v2.1.251); earlier it took `/clear` or a new session.
8. Custom styles MUST load from `~/.claude/output-styles`, `.claude/output-styles` in each directory from cwd to the repo root (closest wins on a name clash), the managed directory, and plugin `output-styles/`.
9. The file name is the style name unless `name` is set. The terminal reads style files at startup, so edits need a restart. VS Code can create files (v2.1.261).
10. Custom styles MUST omit the built-in software engineering section of the full system prompt unless `keep-coding-instructions: true`. The shorter system prompt has no such section, so the field does nothing there. `CLAUDE_CODE_SIMPLE_SYSTEM_PROMPT=0` selects the full prompt on any model.
11. `force-for-plugin: true` (plugin styles only) MUST apply the style while the plugin is enabled, overriding `outputStyle`. The first loaded wins if several set it.
12. Styles MUST apply to the main conversation and forks. Other subagents keep their own system prompts.
13. Unknown frontmatter is ignored. Unparseable YAML loads the style under its file name with no fields.

## Configuration & interfaces

| Field | Default | Meaning |
| :- | :- | :- |
| `name` | file name | Picker name |
| `description` | none | Picker text |
| `keep-coding-instructions` | `false` | Keep the engineering section; also honoured for plugin styles (v2.1.94) |
| `force-for-plugin` | `false` | Plugin styles only |

| Interface | Notes |
| :- | :- |
| `outputStyle` setting | Value is the exact style name |
| `/output-style`, `/config` | Selection |
| Desktop app | Uses the settings file; `/config` opens app settings |

## Failure modes & edge cases

- `explanatory` in settings silently gives Default.
- A custom style selected over Remote Control is refused; `errors` describes this, covering also commands relayed into the session.
- Changing style mid-session changes the system prompt, affecting prompt caching on the next request.

## Changes since the snapshot

- v2.1.94: `keep-coding-instructions` for plugin styles.
- Per docs: Concise (v2.1.237), mid-session effect (v2.1.251), VS Code menu (v2.1.257), VS Code creation (v2.1.261), `/output-style` in non-interactive and Remote Control sessions (v2.1.269).
- Proactive added after the snapshot; version not stated.

## Open questions

- Which version introduced Proactive.
