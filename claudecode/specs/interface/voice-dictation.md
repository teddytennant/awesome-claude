# Voice dictation

**Status:** shipped
**Provenance:** both (feature-gated in snapshot; public)
**Sources:** docs `voice-dictation`, `keybindings`, `settings-reference`, `interactive-mode`; snapshot `voice/voiceModeEnabled.ts`, `hooks/useVoice.ts`, `hooks/useVoiceIntegration.tsx`, `services/voice.ts`, `services/voiceStreamSTT.ts`, `services/voiceKeyterms.ts`, `commands/voice/`; changelog 2.1.122 through 2.1.280

## Purpose

Speak prompts into the terminal input. Audio is streamed to Anthropic for live transcription. Text appears in the prompt and mixes freely with typing.

## Behaviour

### Availability

1. Needs a claude.ai account as the active sign-in. API keys, `ANTHROPIC_AUTH_TOKEN`, `apiKeyHelper` and third-party providers take precedence over a sign-in, so `/voice` is then unavailable (`Unknown command: /voice`).
2. Needs a local microphone, so it does not work in cloud or SSH sessions. WSL needs WSLg.
3. An organisation policy can disable it.
4. Transcription MUST NOT consume messages or tokens, or count toward `/usage` limits.
5. Audio is captured by a built-in native module. Linux falls back to `arecord` or `rec`. If neither exists, `/voice` prints an install command.

### Enable

6. `/voice` toggles and keeps the mode; `/voice hold`, `/voice tap`, `/voice off` set it. Persisted in `voice` settings.
7. Enabling MUST run a microphone check, which triggers the macOS permission prompt if needed, and confirm mode, key and language.
8. For the first three sessions with voice on, a `hold space to speak` hint shows on an empty prompt, using the current binding. It does not show with a custom status line.

### Hold mode (default)

9. Holding the bound key records; release stops.
10. A bare key is detected by key-repeat. During warmup the footer says `keep holding…`, then `listening…`. The first repeat characters enter the input and MUST be removed on activation. One tap still types a space.
11. Snapshot constants: 120 ms rapid-key gap, 5 presses to activate, 2 warmup characters, 200 ms release timeout. May have changed.
12. A modifier combination such as `meta+k` starts on the first press with no warmup, and works outside places that would type, such as transcript view or vim NORMAL.
13. `Space` starts dictation only where it would otherwise type.
14. Text appears dimmed until finalised. It inserts at the cursor, which stays at the end of the insert. Repeat holds append.
15. With `voice.autoSubmit`, release sends when the transcript has at least three words.
16. While recording, the cursor becomes a level bar, unless `prefersReducedMotion`.
17. Hold mode also works in the agent view dispatch input and peek replies.

### Tap mode

18. On an empty prompt, tap starts recording; footer shows `● REC · tap to send`. Tap again stops.
19. The transcript inserts and submits if at least three words, otherwise inserts only.
20. Word counting MUST work for unspaced languages (Japanese, Chinese, Thai).
21. The second tap stops regardless of input content. Recording ends automatically after 15 seconds of silence or 2 minutes total.

### Cancel

22. `Esc` or `Ctrl+C` stops the microphone, discards the transcript and restores the prompt. Both also cancel during post-recording processing, and an edit or submit made in that window stands.
23. That press MUST do nothing else: no interrupting Claude, no clearing the prompt, no counting toward exit.

### Transcription

24. Tuned for coding vocabulary. The project name and git branch are sent as recognition hints.
25. Snapshot transport: a WebSocket to a claude.ai voice stream authenticated with the OAuth token, with keep-alive and close-stream control messages. Details are not public.

### Language

26. Uses the `language` setting (code or name), default English. Supported: cs, da, nl, en, fr, de, el, hi, id, it, ja, ko, no, pl, pt, ru, es, sv, tr, uk.
27. An unsupported value warns on enable and falls back to English for dictation only.

## Configuration & interfaces

| Key | Notes |
|---|---|
| `voice.enabled` | Boolean |
| `voice.mode` | `hold` default, or `tap` |
| `voice.autoSubmit` | Hold mode only |
| `voiceEnabled` | Deprecated since 2.1.92; `voice.enabled` wins |
| `language` | Shared with response language |
| `voice:pushToTalk` | `Chat`; default Space; one key at a time, a custom key replaces Space |

Avoid a bare letter in hold mode, since it types during warmup. Caps Lock binding shows an error (2.1.122).

## Failure modes & edge cases

| Message | Cause |
|---|---|
| `Unknown command: /voice` | No claude.ai sign-in active |
| `Voice mode requires a Claude.ai account` | Usable sign-in missing |
| `Voice mode is disabled by your organization's policy` | Admin policy |
| `Microphone access is denied` | OS permission |
| `Voice mode requires SoX for audio recording` | Native module failed, no fallback |
| `Voice mode requires a microphone, but SoX could not open an audio capture device` | Headless host (2.1.195) |
| `Voice mode could not find a working audio recorder in WSL` | Need `libsox-fmt-pulse` |
| `Voice input is failing repeatedly and has been paused` | 3 failures within 10 s; pause until 10 s after the first |
| `No audio detected from microphone` | Silence captured |
| `Voice connection failed` | Network |
| `Voice stream error: WebSocket upgrade rejected with HTTP <status>` | Non-4xx retried once while recording; 4xx suggests stale sign-in or proxy |
| `No speech detected` | Audio with no words |

Key-repeat disabled at OS level breaks hold detection; use tap mode. On macOS, a terminal missing from Microphone settings needs a `tccutil` reset for its bundle ID, a full quit, and a new `/voice`.

## Changes since the snapshot

- 2.1.92 (per settings docs): `voice` object replaced `voiceEnabled`.
- 2.1.122: Caps Lock binding error.
- 2.1.141: custom bindings and `"space": null` honoured.
- 2.1.195: Linux distinguishes no microphone from no SoX.
- 2.1.200, 2.1.202: silent-mic reporting; pause on repeated failures.
- 2.1.280: Ctrl+C stops the microphone; Esc cancels during processing.
- Docs now cover voice in agent view and a VS Code extension counterpart.

## Open questions

- Whether snapshot thresholds and the kill-switch flag still apply.
- Whether tap mode works in agent view; docs say hold mode only.
- Retention of audio and transcripts is deferred to data-usage docs.
