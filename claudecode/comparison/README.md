# Snapshot vs. current release

Name-level inventory of the 2026-03-31 snapshot against the public docs for 2.1.314.

| Surface | Documented now | Snapshot | Both | New | Snapshot only |
|---|---|---|---|---|---|
| [Tools](tools.md) | 46 | 43 | 33 | 13 | 10 |
| [Slash commands](commands.md) | 120 | 143 | 81 | 39 | 62 |
| [Hook events](hook-events.md) | 33 | 27 | 27 | 6 | 0 |
| [CLI flags](cli-flags.md) | 107 | 136 | 74 | 33 | 62 |
| [Settings keys](settings.md) | 247 | 135 | 77 | 170 | 58 |
| [Environment variables](env-vars.md) | 424 | 697 | 213 | 211 | 484 |

Counts are raw name matches. The tool counts have known errors, listed in [tools.md](tools.md). Reviewed status for each item is in the catalogues under [specs/](../specs/). Bundled skills are counted as slash commands because the docs list them together.
