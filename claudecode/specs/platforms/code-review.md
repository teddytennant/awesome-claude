# Code Review Service and /code-review
**Status:** shipped
**Provenance:** both (`/review` in snapshot; managed service and `/code-review` post-leak)
**Sources:** docs `code-review*.md`, `ultrareview.md`; snapshot `commands/review.ts`; changelog 2.1.223 to 2.1.311

## Purpose
Two separate products. The managed **Code Review** service reviews GitHub pull requests on Anthropic infrastructure for Team and Enterprise. The local **`/code-review`** skill reviews changes inside a user's session on any plan. [ultrareview.md](ultrareview.md) covers the cloud variant.

## Behaviour

### Service availability
1. MUST need Team or Enterprise, and an Owner enabling it. Hosts: GitHub, GitHub Enterprise Server, GitHub Enterprise Cloud with data residency.
2. MUST NOT be available with ZDR, the HIPAA configuration, or CMEK. It is outside the BAA.
3. Orgs using third-party providers still need a Claude org on those plans. It does not route to self-hosted environments.
4. Runs when `disableWorkflows` is on, unless the reviewing machine has it by its own admin (2.1.285).

### Review pipeline
5. Stages MUST be Find (parallel agents on diff and surrounding code), Verify (filter false positives), Rank (dedupe and sort by severity), Post.
6. Default focus is correctness, not style or missing tests.
7. Repo access MUST be read-only. A review posts comments and a check run, resolves its own threads, and may react with 👀. It does not build or run code, push commits, approve, or block.
8. Service selects models, with no model choice. Levels: Quick, Standard (default), Deep, set per org with per-repo overrides (2.1.304).
9. Posted findings use short plain sentences naming who is affected, where it goes wrong, and the fix first (2.1.274).
10. A session start failure from a transient fault is retried once, and the check run says so (2.1.311).

### Findings
11. Severities: 🔴 Important, 🟡 Nit, 🟣 Pre-existing. A collapsed **Why this was flagged** section may appear.
12. A check run named **Claude Code Review** MUST list all findings in a table, including ones GitHub refused as inline. Findings with a line but no comment become annotations.
13. The check run concludes neutral, or skipped after some no-change pushes. It MUST NOT conclude as failure.
14. A finding clears by resolving its thread or pushing a fix. Replying alone does not dismiss, and a reply doesn't start a review; the next review reads replies and may resolve or reply once.
15. Follow-up reviews note that resolving, not just replying, stops a finding counting as open (2.1.268). Re-reviews do not open with LGTM while blocking findings are open (2.1.305).
16. Later automatic reviews focus on changes since the last, with fewer nits, and say how many were left out. `@claude review` covers the whole PR again.

### When reviews run
17. Per-repo modes: **Once after PR creation**, **After every push** (initial default), **Manual**. Any writer can comment to start one.
18. Automatic reviews skip drafts and forks. Pushes to a draft don't start reviews even when subscribed.
19. A push keeps the earlier result when the PR adds and removes the same lines and no Important thread has been resolved since. Titles: **Code review skipped — no new changes**, **Code review not repeated — earlier findings still open**.

### Comment commands
| Command | Effect |
|---|---|
| `@claude review`, `@claude review once` | One review, no subscription (since July 2026) |
| `@claude review always` | Review and subscribe to pushes |
| `@claude review stop`, `off`, `pause` | End subscription, no review (2.1.307) |

20. Commands MUST be a new top-level PR comment, on one line at the start. Capitalisation is ignored. The author needs write, maintain or admin. Bots don't count. The PR must be open.
21. A misspelled `always` or `stop` falls back to plain `@claude review`.
22. In **After every push**, stop is ineffective; converting to a draft stops reviews.
23. A second request while reviewing the same commit doesn't start another.
24. On forks, `always` doesn't subscribe and Re-run doesn't work.
25. The GitHub Action in interactive mode also fires on `@claude review` unless its `trigger_phrase` differs.

### Customisation
26. The service reads `CLAUDE.md` and `REVIEW.md`. `REVIEW.md` is at the repo root, with optional subdirectory additions, and is read from the base or default branch, never from PR changes.
27. On a protected default branch the root file MAY lower severity, exclude paths or issue classes, and cap nits.
28. A line with only `@file` includes that file in place. Skills can be included, but exclusions and caps should not sit in a skill.
29. The check run MUST say when `REVIEW.md` was cut, not applied or left out, including oversized and symlink cases (2.1.280, 2.1.285).

### Billing
30. Billed on tokens through usage credits to the org, separately from plan usage.
31. Reviews MUST be skipped when the Code Review spend limit, org spend limit or credit balance can't cover the expected cost. A comment beginning "⚠️ Code review skipped" names the cause and links the admin page (2.1.274).
32. A locked conversation yields a failure card saying nothing was posted or charged (2.1.287).
33. Analytics shows PRs reviewed, with period totals and by repository (2.1.292).

### Admin
34. Setup: **Allow code review** in Admin settings, Claude Code, connect GitHub, install the App, choose repositories, Finish. Adding a repo needs write access from the connected account; failures list per repo reasons (2.1.293).
35. An option MUST cover a whole GitHub organization, including future repos (2.1.304).
36. Tip comments can be toggled. Save errors state the cause (2.1.296).

### Local /code-review
37. `/review` is an alias since 2.1.223; earlier it was a single-pass PR review.
38. Runs as a background subagent by default and reports in the conversation. Foreground in `-p`, with `CLAUDE_CODE_DISABLE_BACKGROUND_TASKS=1`, or on a re-run while one is in progress.
39. Target: PR number, branch, path, or revision range. With none, the branch's commits ahead of upstream plus uncommitted changes, otherwise against `main` or the previous commit.
40. Effort: `low` to `max`, with `ultra` launching cloud review. A typed level is remembered, except in `-p` and `ultra`. `low` gives fewest, surest findings. No typed level uses session effort.
41. `--fix` applies findings through the permission mode. Background edits fall outside session checkpoints, so `/rewind` can't undo them fully.
42. `--comment` posts inline on GitHub, or a single note on GitLab via `glab` (2.1.257), printing locally if `glab` is absent. Self-managed GitLab needs a URL or `!123`.
43. `--max-findings <n>|all|default` overrides the limit (32 with the findings tool). The choice is reused until reset.
44. Hosts that request a findings list get a `ReportFindings` tool result, with each entry's location, summary and category. Later fixes mark entries fixed, skipped or no change needed.
45. The review follows `CLAUDE.md`, and doesn't read `REVIEW.md`.
46. Claude may start it itself, including on third-party providers, and scheduled tasks can run it.

## Configuration & interfaces
Script gating reads the last line of check run `output.text`, an HTML comment `<!-- bughunter-severity: {"nit":N,"normal":N,"pre_existing":N} -->`, where `normal` counts Important findings. A missing line means no verdict. Titles starting `Code review not repeated` have no line.

Check run titles: `Code review queued...`, `in progress...`, `found no issues`, `failed`, `timed out`, `declined`.

## Failure modes & edge cases
- Comment command ignored: inline comment, later line, edited comment, or no write access. 👀 alone doesn't prove a review started.
- Findings missing inline: see Details table or annotations.
- Model still can't analyze a change on automatic retry: the check run says no further automatic review starts (2.1.311).
- Org IP allowlisting fails hosted reviews unless exempted.

## Changes since the snapshot
- 2.1.223: `/review` aliased; effort reuse. 2.1.257: GitLab posting. 2.1.268, 2.1.273, 2.1.274: wording.
- 2.1.280, 2.1.285: REVIEW.md status. 2.1.285: `disableWorkflows` exception. 2.1.287: locked PR card.
- 2.1.292, 2.1.293: analytics, per-repo add errors. 2.1.304: levels, whole-org coverage.
- 2.1.305: no LGTM with open findings. 2.1.307: stop command. 2.1.311: transient retry.

## Open questions
- Size limits on `REVIEW.md`.
- Default `/code-review` finding limit in terminal mode.
