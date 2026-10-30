# GitHub Actions, GitLab CI/CD and GitHub Enterprise Server
**Status:** shipped (GitHub Actions, GHES); preview (GitLab CI/CD, beta, maintained by GitLab)
**Provenance:** both (`/install-github-app` in snapshot; action v1, federation and GHES post-leak or external)
**Sources:** docs `github-actions.md`, `github-actions-cloud-providers.md`, `gitlab-ci-cd.md`, `github-enterprise-server.md`; snapshot `commands/install-github-app/`; changelog 2.1.212, 2.1.229, 2.1.259, 2.1.314

## Purpose
Run Claude Code from repository events in CI, and connect self-managed GitHub instances to Claude Code's cloud features.

## Behaviour

### GitHub Action: modes
1. `anthropics/claude-code-action@v1` MUST run in **interactive** mode with no `prompt` input: waits for the trigger phrase (`@claude`) in a comment, a review, or a new issue's title or body.
2. With `prompt`, it MUST run in **automation** mode with no mention required. Results go to the run log by default.
3. `prompt` MAY be a skill invocation: `/skill-name` (requires `actions/checkout` first) or `/plugin:skill` (with `plugin_marketplaces` and `plugins`).

### Trigger gating
4. Before Claude starts, the action MUST check write access on issue and PR events, and MUST reject bot actors, failing the run if either rejects.
5. `allowed_non_write_users` (with a user-supplied `github_token`) and `allowed_bots` relax these. Bot rejection also applies to scheduled runs.

### Quick setup
6. `/install-github-app` MUST work only for github.com remotes. On gitlab.com or bitbucket.org it prints a notice and exits (2.1.259). It needs `gh`, authenticated.
7. It MUST install the App, then set a repository secret: `ANTHROPIC_API_KEY`, or `CLAUDE_CODE_OAUTH_TOKEN` for a subscription token. An existing key is reused, and an existing secret may be kept.
8. It MUST push a branch with selected workflows and open GitHub with a PR ready to create.
9. Esc stops after the current step; a closing message lists what happened. **Skip for now** leaves only the App installed.
10. `forceLoginMethod` applies to `install-github-app` logins (2.1.212).
11. The generated review workflow posts inline comments per issue, or one summary comment, using `--comment` (2.1.229); earlier versions wrote only to the run log. An explicit `--allowedTools` naming `mcp__github_inline_comment__create_inline_comment` is needed, because the action starts that server only then.
12. The review plugin skips drafts, closed PRs, trivial or automated PRs, and PRs already commented on by Claude.

### Organization rollout
13. Install the App at org level, store the secret as an org secret, and add a workflow or a reusable one. An API key is preferred over a personal OAuth token for shared use.
14. Workload identity federation MUST exchange the workflow's OIDC token for API access via a Console service account, using `anthropic_federation_rule_id`, `anthropic_organization_id`, optional `anthropic_service_account_id` and `anthropic_workspace_id`, and `id-token: write`.

### Permissions
15. The Claude GitHub App is shared across the action, Code Review and auto-fix, and has one permission set: read and write on Actions, Checks, Contents, Discussions, Issues, Pull requests, Repository hooks, Workflows; read on Administration, Members, Merge queues, Metadata, Statuses.
16. A new permission request MUST wait for owner approval, and the install keeps old permissions until then.
17. A custom App with Contents, Issues and Pull requests alone suffices for the action.

### Cloud providers
18. `use_bedrock`, `use_vertex`, `use_foundry` route inference via OIDC trust in the workflow. Identity choices: official App, custom App, or `GITHUB_TOKEN`.
19. Commits made with the default `GITHUB_TOKEN` do not trigger CI.

### GitLab CI/CD
20. The integration MUST be a job in `.gitlab-ci.yml` that installs Claude Code and runs `claude -p` with `--permission-mode acceptEdits` and `--allowedTools`, with results flowing through MRs.
21. Mention-driven runs need a project webhook on notes, an event listener, and the pipeline trigger API, with `AI_FLOW_INPUT` and `AI_FLOW_CONTEXT`.
22. Providers: Claude API, Bedrock (OIDC), Agent Platform (Workload Identity Federation).
23. GitLab API credentials default to `CI_JOB_TOKEN`, or a PAT stored as `GITLAB_ACCESS_TOKEN`.
24. The `/code-review` skill can post to a GitLab MR; see [code-review.md](code-review.md).

### GitHub Enterprise Server
25. Team and Enterprise only. An Owner connects once at Organization settings, Git providers, via a guided App manifest or manual steps. Display name up to 20 characters. Private CA certificates are accepted.
26. Support matrix:

| Feature | GHES |
|---|---|
| Cloud sessions, teleport | Yes |
| Code Review | Yes |
| Claude Security | Yes, Enterprise public beta |
| Plugin marketplaces | Yes, credentials vary by surface |
| GitHub Actions | Yes, manual workflows only |
| Contribution metrics | No |
| GitHub MCP server | No |

27. The host MUST be auto-detected from the git remote and routed via the org's configured instance.
28. App manifest permissions: Contents, Pull requests, Issues, Checks, Repository hooks read-write; Actions, Commit statuses, Metadata, Organization members read. Events: `pull_request`, `issue_comment`, `pull_request_review_comment`, `pull_request_review`, `check_run`, `status`.
29. A manifest applies only on creation, so older apps must be updated by hand.
30. Anthropic-hosted sessions and hosted pre-session flows need the instance reachable from Anthropic infrastructure, so an allowlist of Anthropic IPs is needed behind firewalls. Test connection also tests the session path, warning on failure (2.1.314).
31. GHES marketplaces are configurable through managed settings (`extraKnownMarketplaces`, `strictKnownMarketplaces` families); see the plugins specs.
32. GitHub Enterprise Cloud with data residency uses the same admin setup with a `ghe.com` hostname.

## Configuration & interfaces
| Action input | Purpose |
|---|---|
| `prompt`, `trigger_phrase` | Mode and trigger |
| `claude_args` | CLI passthrough: `--max-turns`, `--model`, `--mcp-config`, `--allowedTools`, `--debug` |
| `anthropic_api_key`, `claude_code_oauth_token` | Auth |
| `github_token` | Otherwise authenticates as the App |
| `plugin_marketplaces`, `plugins` | Plugin install |
| `settings` | JSON string or path |
| `use_bedrock`, `use_vertex`, `use_foundry` | Provider |
| `allowed_bots`, `allowed_non_write_users` | Trigger relaxations |

Beta migration: `@beta` to `@v1`, drop `mode`, `direct_prompt` to `prompt`, CLI options into `claude_args`, `custom_instructions` to `--append-system-prompt`.

## Failure modes & edge cases
- No response to `@claude`: check App install, workflows enabled, stored secrets, commenter write access, and that the comment has `@claude` as a whole word, not `/claude` or `@claude-bot`.
- CI not running on Claude's commits: remove `GITHUB_TOKEN` input.
- Cross-region Bedrock profiles need access in each region of the group.
- Marketplace add policy error and `Unable to get organization UUID` are documented GHES failures.
- App costs include Actions minutes as well as tokens; OAuth runs use subscription limits.

## Changes since the snapshot
- 2.1.212: forced login in `install-github-app`.
- 2.1.229: review workflow posts on the PR.
- 2.1.259: GitHub-only explanation.
- 2.1.314: GHES Test connection second path.
- The action itself lives in another repository; its releases are not in this changelog.

## Open questions
- Full action input list (external config reference).
- Date GHES support reached GA.
