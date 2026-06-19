# Session Log — 2026-06-06 (Session 01)

## TL;DR

- **Goal**: Prove `exports/capture/climb-to-safety/rig.mvr` imports into Capture and that one RayFlow cue visibly changes Capture over DMX.
- **Result**: Partial proof only. RayFlow dry-run and Art-Net send worked; Capture import/visible stage proof is blocked by the installed Capture app wrapper.
- **Blocker**: `/Applications/Capture.app` is the iOS-on-Mac Capture wrapper (`se.capture.capturemobile`, version `2026.0.34`), not the desktop Capture workflow expected by the MVR import plan. It exposes `.c2p`/`.c2s` document types only, showed a blank scene window, and did not expose an accessible MVR import command.
- **Next**: Install/open the desktop Capture 2026 or Student Edition workflow that exposes File > Import Model > MVR, then repeat the import and DMX visual proof.
- **Branch**: `codex/climb-to-safety-product-loop`

## Commands And Evidence

### Capture App Inspection

Installed app found:

```bash
ls /Applications
```

Relevant result:

```text
Capture.app
```

The runnable app is wrapped:

```bash
find /Applications/Capture.app -maxdepth 3 -type f -name Info.plist -print
```

Relevant result:

```text
/Applications/Capture.app/Wrapper/Capture.app/Info.plist
```

Bundle inspection:

```bash
plutil -p /Applications/Capture.app/Wrapper/Capture.app/Info.plist
```

Relevant findings:

- `CFBundleIdentifier`: `se.capture.capturemobile`
- `CFBundleShortVersionString`: `2026.0.34`
- `CFBundleSupportedPlatforms`: `iPhoneOS`
- `LSRequiresIPhoneOS`: `true`
- Document types: Capture Project `.c2p` and Capture Student Project `.c2s`
- No MVR document type was registered.

Opening the generated MVR with Capture:

```bash
open -a /Applications/Capture.app /Users/connorkitchings/Desktop/Repositories/rayflow/exports/capture/climb-to-safety/rig.mvr
```

Observed result:

- Capture accepted the app handoff.
- The visible window title became `Capture`.
- The scene remained blank.
- The accessible File menu contained only disabled `Open...`, `Open Recent`, `Close`, and `Close All`.
- No fixture matching prompts appeared.
- No visible fixture/stage import was verifiable.

## RayFlow DMX Proof Attempts

### sACN Dry Run

```bash
uv run rayflow show output-cue 'Climb to Safety Studio' 1 \
  --dir data/shows \
  --rig-dir data/rigs \
  --fixture-dir data/fixtures/samples \
  --rig 'Rig 1' \
  --backend sacn \
  --json
```

Result:

- Passed.
- Rendered cue 1, `Intro Warm Front`.
- Mapped RayFlow universe `0` to E1.31/sACN universe `1`.
- Produced nonzero values on channels `1-30`.

### sACN Live Attempt

```bash
uv run rayflow show output-cue 'Climb to Safety Studio' 1 \
  --dir data/shows \
  --rig-dir data/rigs \
  --fixture-dir data/fixtures/samples \
  --rig 'Rig 1' \
  --backend sacn \
  --execute \
  --json
```

Result:

- Failed before sending.
- Error: `NetworkError: Cannot initialize sACN sender: [Errno 48] Address already in use`.
- `lsof` showed Capture already listening on UDP `*:5568`.
- Interpretation: Capture owns the sACN port. The current Python sACN sender also binds to `5568`, so local same-host sACN send and Capture receive conflict on macOS with this library/app combination.

### Art-Net Dry Run

```bash
uv run rayflow show output-cue 'Climb to Safety Studio' 1 \
  --dir data/shows \
  --rig-dir data/rigs \
  --fixture-dir data/fixtures/samples \
  --rig 'Rig 1' \
  --backend artnet \
  --target 127.0.0.1 \
  --json
```

Result:

- Passed.
- Target: `127.0.0.1:6454`.
- Rendered the same nonzero channel values for universe `0`.

### Art-Net Live Send

```bash
uv run rayflow show output-cue 'Climb to Safety Studio' 1 \
  --dir data/shows \
  --rig-dir data/rigs \
  --fixture-dir data/fixtures/samples \
  --rig 'Rig 1' \
  --backend artnet \
  --target 127.0.0.1 \
  --execute \
  --json
```

Result:

- Passed.
- RayFlow reported `status: sent`, universe `0`, evidence quality `send-call-only`.
- `lsof` showed Capture listening on UDP `*:6454`.
- Visual proof still failed because the Capture scene remained blank and MVR import was not verifiable.

## Fixture Import Status

No fixture matching prompts were observed. Fixture substitutions and universe assignments inside Capture could not be recorded because the MVR import did not visibly complete.

Expected RayFlow handoff metadata remains:

- Show: `Climb to Safety Studio`
- Rig: `Rig 1`
- Fixture count: `14`
- Cue count: `16`
- Preferred protocol: `sacn`
- Fallback protocol tested: `artnet`

## Decision

This is not a completed Capture proof. It proves:

- RayFlow can render the pilot cue.
- RayFlow can send Art-Net to a local Capture listener on UDP `6454`.
- The installed Capture wrapper listens on Art-Net and sACN ports.

It does not prove:

- MVR import into Capture.
- Fixture matching.
- Plausible stage positioning.
- Visible fixture response.

## Next Steps

1. Use the desktop Capture 2026 or Student Edition workflow that exposes MVR model import.
2. Import `exports/capture/climb-to-safety/rig.mvr` through Capture's MVR import path rather than opening the file as a project document.
3. Record every fixture matching prompt and substitution.
4. Retry Art-Net first on `127.0.0.1:6454`, since that send path worked locally.
5. Revisit sACN only after either using a separate network interface/host or changing RayFlow's sACN sender strategy so it does not conflict with Capture's bind on UDP `5568`.
