# Themes and colour

**Status:** shipped
**Provenance:** both (built-in presets in snapshot; auto and custom themes post-leak, since v2.1.111, 2026-04-16)
**Sources:** docs `terminal-config`, `settings-reference`, `commands`, `accessibility`, `plugins__components`; snapshot `utils/theme.ts`, `components/ThemePicker.tsx`, `components/design-system/ThemeProvider.tsx`, `ink/colorize.ts`; changelog 2.1.111 through 2.1.287

## Purpose

Give the UI a named palette that suits the user's terminal and vision. Allow custom palettes and session-level accents.

## Behaviour

### Presets

1. Built-ins: `dark`, `light`, `dark-daltonized`, `light-daltonized`, `dark-ansi`, `light-ansi`. Default `dark`.
2. `auto` resolves to dark or light from the terminal background and follows appearance changes when the terminal does.
3. ANSI presets use the terminal's palette, and dim text MUST stay distinct under them and on 16-colour terminals.
4. The app never changes the terminal's own colours.

### Picker

5. `/theme` or the `/config` Theme row opens a picker with a live preview. It is a scrolling list that fits the terminal, and number keys do not pick (2.1.286).
6. `Ctrl+T` in the picker toggles syntax highlighting.
7. It lists presets, custom themes and plugin themes, ending with **New custom theme…**. `Ctrl+E` on a custom theme edits it.
8. A plugin's `config.set` hook MUST be consulted before saving a theme (2.1.292).

### Custom themes

9. A theme is `~/.claude/themes/<slug>.json`. Selecting one stores `custom:<slug>`; plugin themes store `custom:<plugin-name>:<slug>`.
10. Fields, all optional: `name` (defaults to slug), `base` (preset, default `dark`), `overrides` (token to colour).
11. Colours: `#rrggbb`, `#rgb`, `rgb(r,g,b)`, `ansi256(n)`, `ansi:<name>` with the 16 standard names.
12. Unknown tokens and invalid values MUST be ignored, so a typo cannot break rendering.
13. The directory is watched, so edits apply live. If it did not exist at startup, one restart is needed after creating it.
14. The editor offers a few extra single-purpose tokens not in the public reference.
15. `--safe-mode` disables custom themes.

### Tokens

| Group | Tokens |
|---|---|
| Text and accent | `claude`, `text`, `inverseText`, `inactive`, `subtle`, `suggestion`, `permission`, `remember` |
| Status | `success`, `error`, `warning`, `merged` |
| Input and modes | `promptBorder`, `planMode`, `autoAccept`, `bashBorder`, `ide`, `fastMode`, `effortUltra` |
| Diff | `diffAdded`, `diffRemoved`, `diffAddedDimmed`, `diffRemovedDimmed`, `diffAddedWord`, `diffRemovedWord` |
| Backgrounds | `userMessageBackground`, `userMessageBackgroundHover`, `bashMessageBackgroundColor`, `memoryBackgroundColor`, `selectionBg`, `composerSidebarBackground` |
| Usage and labels | `rate_limit_fill`, `rate_limit_empty`, `briefLabelYou`, `briefLabelClaude` |
| Shimmer pairs | `claudeShimmer`, `warningShimmer`, `permissionShimmer`, `promptBorderShimmer`, `inactiveShimmer`, `fastModeShimmer` |
| Subagent palette | `<color>_FOR_SUBAGENTS_ONLY` for red, blue, green, yellow, purple, orange, pink, cyan |
| Rainbow | `rainbow_<color>` and `rainbow_<color>_shimmer` for red, orange, yellow, green, blue, indigo, violet |

`userMessageBackgroundHover`, `selectionBg`, `composerSidebarBackground` apply in fullscreen only. The rainbow renders `ultrathink` in the prompt when it can raise effort.

### Session colour

16. `/color <name>` sets the prompt bar: red, blue, green, yellow, purple, orange, pink, cyan. `default` resets. No argument picks a random colour. It syncs to claude.ai/code over Remote Control and works in `-p`.
17. `/rename` MUST keep the theme's prompt border colour (2.1.246).

### Other colour paths

18. `spellcheck.color` accepts names and the value forms above, falling back to the theme's error colour.
19. Light themes have raised prompt-border contrast (2.1.287).
20. Inside tmux, colour is clamped to 256 unless `CLAUDE_CODE_TMUX_TRUECOLOR` is non-empty. Snapshot tip `colorterm-truecolor` suggests a truecolour hint exists.
21. `syntaxHighlightingDisabled` plainly renders code. `CLAUDE_CODE_SYNTAX_HIGHLIGHT=false` affects diffs only.

## Configuration & interfaces

| Key | Notes |
|---|---|
| `theme` | Any file; old `~/.claude.json` value is used if no settings file sets it; `/config` label **Theme** |
| `/config theme=<value>` | Direct set |
| Plugin themes | Contributed through plugin components |
| Mod typings | `ThemeKey` and `Color` types available to mods |

## Failure modes & edge cases

- A malformed `theme` in `~/.claude.json` MUST NOT crash launch (2.1.277).
- A missing custom theme file behaviour is not documented.
- Mismatched app and terminal backgrounds can produce unreadable rows; agent view rows were fixed for this.

## Changes since the snapshot

- 2.1.111: Auto theme generally available (`AUTO_THEME` gate in snapshot).
- Custom themes in `~/.claude/themes/` and plugin themes are post-leak; docs give no version.
- 2.1.239: `effortUltra` override honoured.
- 2.1.246: custom diff colours honoured.
- 2.1.286: scrolling picker.
- 2.1.287: light-theme contrast.

## Open questions

- Version that added custom themes.
- Fallback when `custom:<slug>` is missing.
- Full token list, including the unlisted onboarding accents.
- How `auto` detects the background (snapshot gate only).
