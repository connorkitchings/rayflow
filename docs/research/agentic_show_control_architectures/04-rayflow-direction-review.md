# RayFlow Direction Review

## Current Direction

RayFlow has been moving toward a grandMA3-centered workflow:

- build rig and show data in RayFlow;
- generate cue intent;
- export MVR, command lists, and Timecode XML;
- push or import artifacts into grandMA3 onPC;
- eventually expose MA3 operations through MCP.

That direction is still useful for MA-compatible deliverables, but the manual research suggests it is the wrong center of gravity for an agent-first control system.

## What The Research Changes

The recent MA3 probes were not just incidental setup pain. They exposed structural mismatch:

- RayFlow needs deterministic machine feedback.
- MA3 mainly gives command-line mutation plus indirect evidence.
- RayFlow needs repeatable fixture import and patching.
- MA3 fixture workflows still appear UI-heavy or syntax-sensitive.
- RayFlow needs agents to compose safe operations.
- MA3 raw command generation depends on destination context, exact syntax, show-local OSC settings, and version-specific behavior.

The research therefore supports a pivot: continue MA3 compatibility, but build the primary agent loop on APIs and protocols that are easier to test.

## Recommended Adjustment

RayFlow should become a backend-neutral show-intent and DMX-rendering system.

Near-term architecture:

1. Preserve RayFlow YAML show and rig files as the canonical source of truth.
2. Add a fixture-aware renderer that can resolve cue intent into DMX universe values.
3. Treat Art-Net and sACN as first-class live output targets.
4. Add QLC+ WebSocket support as the first structured controller adapter.
5. Keep grandMA3 as an export/playback adapter with gated OSC probes.
6. Defer mutating MA3 MCP tools until MA3 operations have repeatable evidence.

This does not abandon MA3. It makes MA3 one backend rather than the backend.

## Do Next

- Define a `ControlBackend` or equivalent adapter boundary with dry-run, apply, and readback/evidence methods.
- Implement a minimal DMX renderer for dimmer and RGB/RGBW fixtures using existing GDTF parsing.
- Add an Art-Net or sACN proof that renders a RayFlow cue to a captured universe frame.
- Add a QLC+ research spike for WebSocket command/query behavior.
- Update the implementation schedule so MA3 fixture import is no longer blocking the agent-first MVP.

## Stop Doing For Now

- Stop treating MVR import into MA3 as the critical path for RayFlow's next milestone.
- Stop expanding MA3 mutation commands until readback is improved.
- Stop planning MCP around desired MA3 operations that are not verified.

## Decision

The current MA3 research remains valuable, but it should move from "mainline implementation path" to "professional-console compatibility track." The mainline should focus on deterministic, inspectable control through RayFlow data, direct DMX output, and API-first controller adapters.
