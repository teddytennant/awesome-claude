# Known conflicts between sources

Places where the public docs and changelog for 2.1.314 disagree, or where the changelog is ahead of the docs. The specs record these rather than resolve them.

| Topic | One source says | The other says | Spec |
|---|---|---|---|
| Auto mode default | Docs: universal interactive default since v2.1.283 | Changelog: 2.1.283 covers third-party or telemetry-off sessions, 2.1.284 covers every plan | [auto-mode](specs/security/auto-mode.md) |
| `/permissions` tab | Docs: Recently denied | 2.1.314 changelog: Recently blocked | [permission-rules](specs/security/permission-rules.md) |
| `/advisor` on Claude Platform on AWS | 2.1.300 changelog: added | Docs: not available | [advisor](specs/core/advisor.md) |
| Primary model not found | 2.1.152 changelog: fallback lasts the session | Docs: fallback lasts one turn | [model-fallback](specs/core/model-fallback.md) |
| Refusal fallback rules | 2.1.314 changelog: relaxed | Docs: older refusals | [model-fallback](specs/core/model-fallback.md) |
| Org default label | 2.1.196 changelog: mentions "Role default" | Docs: always Org default | [model-restrictions](specs/core/model-restrictions.md) |
| `/skill-doctor` first version | Docs: v2.1.252 | Changelog: 2.1.261 | [skills](specs/extensibility/skills.md) |
| Terminal skill and plugin sync | Docs: v2.1.273 | Changelog: 2.1.275 | [skills](specs/extensibility/skills.md) |
| Skill stacking limit | Docs: first plus five (six) | Changelog: up to 5 | [skills](specs/extensibility/skills.md) |
| `prompt.change` mod event | Changelog: present | Mods reference: absent | [mods](specs/extensibility/mods.md) |
| `SendFeedback` first version | Docs: v2.1.238 | Changelog: 2.1.247 | [end-conversation-and-send-feedback](specs/tools/end-conversation-and-send-feedback.md) |
| Native Windows cross-session messaging | Docs: v2.1.234 | Changelog: 2.1.239 | [cross-session-messaging](specs/agents/cross-session-messaging.md) |
| `--ax-screen-reader` first version | Docs: 2.1.181 | Changelog: 2.1.208 | [accessibility](specs/interface/accessibility.md) |
| `Ctrl+U` | 2.1.111 changelog | Current docs differ; the spec follows the docs | [prompt-input-and-editing](specs/interface/prompt-input-and-editing.md) |
| Status line hints | 2.1.169 changelog fix | Current docs differ; the spec follows the docs | [status-line](specs/interface/status-line.md) |
| Cloud setup script failure | Docs: stops the session | 2.1.314 changelog: session starts anyway | [cloud-sessions](specs/platforms/cloud-sessions.md) |
| `safety_event` telemetry | Docs: listed | 2.1.312 changelog: no longer sent | [telemetry-monitoring](specs/platforms/telemetry-monitoring.md) |
| Subagent `autoCompactWindow` | Docs: `CLAUDE_CODE_AUTO_COMPACT_WINDOW` overrides it | 2.1.312 changelog: the field lowers it | [subagent-runtime](specs/agents/subagent-runtime.md) |
| `CLAUDE_CODE_WORKFLOW_SUBAGENT_MODEL` | 2.1.296 changelog: present | Env var reference: absent | [dynamic-workflows](specs/agents/dynamic-workflows.md) |

Docs also cite v2.1.182, v2.1.213 and v2.1.242, which have no changelog heading. Specs use a nearby version or leave the number out.
