# Desktop iOS Simulator Pane
**Status:** preview (public beta, macOS)
**Provenance:** post-leak (app feature; no CLI version in changelog, requires Claude Desktop v1.24012.0)
**Sources:** docs `desktop-ios-simulator.md`, `desktop.md`

## Purpose
Show and drive Apple's iOS Simulator inside the Code tab next to the conversation, so Claude can build, install, launch and verify an app, and the user can tap through it. It drives the simulator directly, so it needs no computer use and never takes over the screen. The CLI reaches the simulator via computer use instead.

## Behaviour

### Availability
1. MUST be available on Pro, Max, Team and Enterprise, excluding Enterprise orgs with a HIPAA configuration.
2. MUST require a Mac, Desktop v1.24012.0+ and Xcode with the iOS platform. Xcode 26.x or 27 is recommended.
3. MUST use the install selected by `xcode-select`; changing it requires reopening Desktop.
4. MUST be available in local sessions only.

### Opening and attaching
5. The pane MUST open automatically when Claude launches an app in a simulator. No command or setting is needed.
6. A request about seeing the app SHOULD make Claude start a simulator before beginning the work.
7. An **iOS Simulator** title-bar button MUST appear once a simulator is attached or iOS work is detected. **Attach simulator** or a device pick attaches; picking a shut-down device boots it.
8. If Xcode or simulators are missing, the pane MUST show setup steps.
9. The pane shows whichever device the app launched in. Naming a device targets it.

### Interaction
10. Users MUST be able to tap and swipe, use Simulator shortcuts (Cmd+Shift+H, Cmd+L, Cmd+Up/Down), rotate (Cmd+Right), switch devices, save a screenshot (Cmd+S) or recording (Cmd+R) to the Desktop folder, and detach.
11. A **Display** menu MAY tune frame rate and resolution without changing app behaviour.
12. User and Claude share a device. A **Claude is using this device** badge MUST show while Claude drives.

### Device lifecycle
13. A device MUST belong to the session that launched it; parallel sessions do not share devices. Switching session switches the view.
14. Each session MAY have up to 4 device panes.
15. Desktop MUST shut down simulators it booted when the app quits, the session archives, or 10 minutes after detach. Devices booted elsewhere MUST NOT be auto-shut.

### Consent
16. Claude MUST get consent before controlling a device. Building or opening a URL follows the session permission mode.

## Configuration & interfaces
| Control | Effect |
|---|---|
| App setting | User turns off Claude's simulator access |
| `disableMobileSimulatorTools: true` (managed) | Removes Claude's tools; pane remains for user taps; not overridable |
| `requireCoworkFullVmSandbox` (policy) | Disables pane and tools entirely |

## Failure modes & edge cases
- No simulators found: install an iOS platform in Xcode.
- Cloud and SSH sessions cannot reach simulators on the Mac.
- User taps during a Claude action alter results.

## Changes since the snapshot
- None found in the CLI changelog; the feature is entirely post-snapshot and versioned by Desktop release.

## Open questions
- Names of Claude's simulator tools.
- Whether physical devices will be supported.
