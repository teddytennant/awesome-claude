# Claude Code specification

A behavioural spec of Claude Code as of **2.1.314** (2026-10-30), built on the 2026-03-31 source snapshot of 2.1.88 and everything released since.

| Start here | What it holds |
|---|---|
| [INDEX.md](INDEX.md) | Every spec, with status and provenance |
| [FEATURES-SINCE-SNAPSHOT.md](FEATURES-SINCE-SNAPSHOT.md) | Headline features since the snapshot |
| [releases/](releases/README.md) | Every non-fix changelog entry for 183 versions |
| [comparison/](comparison/README.md) | Snapshot vs. current, by name |
| [LEAK-TIMELINE.md](LEAK-TIMELINE.md) | How the snapshot date and version were established |
| [KNOWN-CONFLICTS.md](KNOWN-CONFLICTS.md) | Where public sources disagree |
| [OPEN-QUESTIONS.md](OPEN-QUESTIONS.md) | What could not be established |

## Coverage

| Area | Specs |
|---|---|
| [core](specs/core) | 18 |
| [tools](specs/tools) | 15 |
| [agents](specs/agents) | 13 |
| [extensibility](specs/extensibility) | 14 |
| [security](specs/security) | 10 |
| [memory-context](specs/memory-context) | 12 |
| [interface](specs/interface) | 18 |
| [platforms](specs/platforms) | 27 |

## How to read a spec

Each spec opens with its status and provenance:

- **Status:** `shipped`, `preview`, `gated/unreleased` or `removed`.
- **Provenance:** `snapshot`, `post-leak` with its first version, or `both`.

Requirements are numbered and use MUST and SHOULD. Features unchanged since the snapshot are kept short, and the detail goes to what changed after it.

## Sources and how far to trust them

1. **Public docs for 2.1.314** are the main authority for current behaviour.
2. **The public changelog** covers what changed and when.
3. **The snapshot** covers internals, but it only shows how 2.1.88 worked. Internal details with no public confirmation are marked as snapshot evidence and may no longer be true.

The current release was compared using public material only. The installed binary was not decompiled, so internals added after the snapshot are unknown. A feature's public docs define its behaviour here, not its implementation.

## What is deliberately left out

- Source code and model-facing prompt text. A check for 14-word runs shared with the snapshot found none.
- Anti-abuse, client attestation, anti-distillation and rate-limit enforcement mechanics.
- Ways around permissions, sandboxes or safety checks.
- Non-public endpoints, keys and tokens.

## Known limits

- The topic tags in the release log come from keyword rules, so individual tags can be wrong.
- The comparison is a name match and has [known errors](comparison/tools.md).
- Two reference files and a few others run past the 2,500-word target, because they are lookup tables.
- Some long doc pages were read in part: `plugins__org`, `plugins__install`, `plugins__troubleshooting`, `hooks-guide` and parts of the mods docs.
- Of the Claude Tag docs, only three pages were read.

## Regenerating

`tools/` holds the scripts behind the generated files. Each takes paths to a local working directory of public sources and, for the comparison and verification, a local copy of the snapshot. No source is stored in this repo.
