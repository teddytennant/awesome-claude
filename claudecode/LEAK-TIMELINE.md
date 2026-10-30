# Snapshot date and version

The baseline for these specs is **version 2.1.88**, published to npm on **2026-03-30 at 22:36 UTC** and publicly disclosed on **2026-03-31**.

## Timeline

| When (UTC) | Event | Evidence |
|---|---|---|
| 2026-03-29 01:40 | 2.1.87 published | npm registry |
| 2026-03-30 22:36 | 2.1.88 published with a source map of about 59.8 MB | npm registry; press coverage |
| 2026-03-31 | Exposure disclosed publicly by Chaofan Shou | Press coverage |
| 2026-03-31 23:32 | 2.1.89 published, about 25 hours after 2.1.88 | npm registry |
| After disclosure | 2.1.88 removed from npm | Registry keeps the timestamp but no version record |
| 2026-10-30 00:12 | 2.1.314 published, the newest release covered here | npm registry |

Anthropic described the event as a release packaging issue caused by human error, and said no customer data or credentials were exposed.

## Why the snapshot is taken to be 2.1.88

- The public changelog has no 2.1.88 section, and 2.1.87 has one entry. The 2.1.89 section therefore describes the work done across both releases.
- The snapshot already contains `PermissionDenied` and `CLAUDE_CODE_NO_FLICKER`, both announced in 2.1.89.
- The snapshot does not contain `MCP_CONNECTION_NONBLOCKING`, also announced in 2.1.89.

Together these place the snapshot after 2.1.87 and before the final 2.1.89 build, which matches 2.1.88. It is an inference: the snapshot's version is injected at build time, so the source does not state it.

Because of this overlap, the release log starts at 2.1.89 and some of its 2.1.89 entries were already in the snapshot.

## What was not verified

- The exact time of the npm removal is not recorded; the registry's `unpublished` field is empty.
- Press reports disagree on how many earlier source map exposures there were, so none is claimed here.

## Sources

- [SiliconANGLE, 2026-03-31](https://siliconangle.com/?p=736948)
- [InfoQ](https://infoq.com/news/2026/04/claude-code-source-leak)
- [Daring Fireball, 2026-04-06](https://daringfireball.net/linked/2026/04/06/anthropic-claude-code-leak)
- [AI Magazine](https://aimagazine.com/news/anthropic-claude-code-leak)
- [npm registry record](https://registry.npmjs.org/@anthropic-ai/claude-code)
- [Public changelog](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md)
