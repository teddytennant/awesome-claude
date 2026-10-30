# Gated UI features and easter eggs

**Status:** gated/unreleased (mixed; `/buddy` shipped once, see below)
**Provenance:** snapshot, with post-leak notes
**Sources:** snapshot `buddy/`, `commands/thinkback/`, `commands/thinkback-play/`, `commands/stickers/`, `commands/passes/`, `utils/terminalPanel.ts`, `components/GlobalSearchDialog.tsx`, `components/QuickOpenDialog.tsx`, `components/messageActions.tsx`, `components/DevBar.tsx`, `moreright/`, `keybindings/defaultBindings.ts`, `skills/bundled/loremIpsum.ts`; docs `commands`, `settings-reference`, `whats-new__2026-w14`, `whats-new__2026-w27`; changelog 2.1.89, 2.1.251

## Purpose

Record playful and gated interface features at feature level, so the spec is complete without implying they are all current.

## Behaviour

### /buddy companion

Public record: 2.1.89 says `/buddy` arrived for April 1st, hatching a small creature that watches you code. It appears in no current doc or command table, and no removal line exists.

Snapshot feature (build gate `BUDDY`):

1. A teaser window of April 1 to 7, 2026 local time shows a rainbow `/buddy` notification for 15 seconds when no companion exists. The command stays live afterwards. `/buddy` in the prompt is rainbow-highlighted.
2. A companion has deterministic "bones" and a model-generated "soul".
3. Bones derive from a seeded hash of the account ID: rarity (common 60, uncommon 25, rare 10, epic 4, legendary 1, with star ratings and theme colours), one of 18 species, eye glyph, hat (none for common), a 1% shiny chance, and five stats (DEBUGGING, PATIENCE, CHAOS, WISDOM, SNARK) with one peak, one dump and a rarity floor.
4. Bones are never stored and are recomputed on read, so editing config cannot change rarity.
5. The soul (name, personality) and hatch time persist in global config as `companion`. `companionMuted` silences it.
6. A small ASCII sprite sits beside the prompt, with a 500 ms idle animation. Below 100 columns it collapses to a one-liner.
7. After a turn an observer may give a speech-bubble reaction, shown about 10 seconds and fading for the last 3. In fullscreen the bubble floats, and scrolling dismisses it.
8. `/buddy pet` floats hearts for 2.5 seconds.
9. It is a footer item, and the model is told about it through a short intro.
10. The `commands/buddy/` source is absent from the snapshot. Subcommands beyond `pet` cannot be specified.

### Thinkback (year in review)

11. `/think-back`: a "2025 Year in Review", behind a server gate. It installs a plugin from a marketplace and runs its skill. `/thinkback-play` is the hidden animation runner, launching a player through `node`.
12. No public changelog or doc mention exists.

### Other easter eggs and small delights

13. `/stickers`: documented; orders stickers.
14. `/radio`: documented; opens Claude FM lo-fi stream, or prints the URL. Available on third-party providers and without telemetry since 2.1.251.
15. `/passes`: documented; guest passes for eligible accounts.
16. Spinner verbs: whimsical rotating verbs, customisable with `spinnerVerbs`. Past-tense versions appear in the turn line, such as `Sautéed`.
17. `ultrathink` renders with a rainbow gradient in the prompt when it can raise effort.
18. Clawd mascot in the banner, with animated variants in the snapshot. Its feet were adjusted in 2.1.282.
19. `lorem-ipsum` skill: internal only.
20. `good-claude`: internal stub.

### Snapshot gated UI

| Feature | Gate | What it does | Public now |
|---|---|---|---|
| Terminal panel | `TERMINAL_PANEL` | `Meta+J` toggles a tmux-backed per-instance shell, suspending the UI | Not documented |
| Global search | `QUICK_SEARCH` | `app:globalSearch` dialog | Not documented |
| Quick open | `QUICK_SEARCH` | `app:quickOpen` file opener | Not documented |
| History picker | `HISTORY_PICKER` | Dialog form of history search | Fullscreen `Ctrl+R` dialog is documented |
| Message actions | `MESSAGE_ACTIONS` | `chat:messageActions` on transcript messages | Not documented |
| Brief mode | `KAIROS`, `KAIROS_BRIEF` | `/brief`, `app:toggleBrief`, `You`/`Claude` labels | `--brief` and label tokens documented; command not |
| Auto theme | `AUTO_THEME` | Follow terminal | Shipped 2.1.111 |
| Away summary | `AWAY_SUMMARY` | Recap | Shipped (`/recap`, 2.1.108) |
| Fullscreen | runtime | Internal default | Public 2.1.89 |
| Teammate preview | none | `app:toggleTeammatePreview` on `Ctrl+Shift+O` | Not documented |
| Token budget triggers | `TOKEN_BUDGET` | Spinner and prompt highlights | Not documented |
| Shot stats | `SHOT_STATS` | Distribution in `Stats` | Not documented |
| Dev bar | build | Developer status row | Internal |
| `moreright` | stub | External stub of an internal hook | Internal |
| Torch | `TORCH` | Source absent | Unknown |
| Grove | none seen | `components/grove/` dialog | Unknown |

## Configuration & interfaces

| Key | Notes |
|---|---|
| `companion`, `companionMuted` | Snapshot global config |
| `spinnerVerbs` | Public |

## Failure modes & edge cases

- Hidden features keyed to internal users do nothing in public builds.
- Any feature absent from public docs SHOULD be treated as unsupported.

## Changes since the snapshot

- 2.1.89: `/buddy` release note.
- 2.1.108: recap public. 2.1.111: auto theme public.
- 2.1.251: `/radio` wider availability; its first release is covered in the w27 digest.
- 2.1.282: Clawd's feet.

## Open questions

- Whether `/buddy` still exists, was limited to a window, or was removed. The changelog is silent after 2.1.89.
- Whether any gate above has opened without a release note.
- Grove's purpose.
- `/radio` first version. The digest places it in week 27.
