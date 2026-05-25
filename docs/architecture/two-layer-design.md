# Layered Design

> **Merged:** The content of this document has been consolidated into
> [system_overview.md](./system_overview.md). This file is retained for
> historical reference only.

## Layer 1: Show Intent

The source of truth is RayFlow project data:

- rig YAML;
- show YAML;
- GDTF fixture definitions;
- presets, vibes, sections, cues, and timestamps.

This layer is intentionally AI-readable. A coding agent can inspect it, propose
diffs, run validation, and preserve history without needing to mutate a running
lighting console.

## Layer 2: Fixture Resolution And Rendering

This layer translates abstract intent into concrete fixture behavior:

- fixture selection;
- channel addressing;
- attribute family support;
- dimmer and color values;
- future pan/tilt, beam, focus, gobo, and effect handling.

The renderer should be deterministic and testable. Given the same show, rig,
and fixture library, it should produce the same universe/channel output.

## Layer 3: Output Adapters

Adapters are replaceable. They should not define the core show model.

| Adapter | Role | Status |
| --- | --- | --- |
| Art-Net | Direct DMX output | Bridge exists; fixture-aware renderer is next |
| sACN | Direct DMX output | Bridge exists; fixture-aware renderer is next |
| QLC+ WebSocket | Structured cue/controller execution | Research spike planned |
| grandMA3 export | MVR, commands, Timecode XML, handoff bundle | Partially implemented |
| grandMA3 OSC | Gated direct console mutation | Implemented for verified/dry-run-safe paths only |
| Middleware | Chataigne/Open Stage Control style routing | Future evaluation |

## Communication Shape

```text
Show/Rig YAML
    |
    v
Fixture capability resolution
    |
    v
DMX frame or controller command plan
    |
    +--> dry-run artifact
    +--> apply through selected adapter
    +--> evidence packet
```

## Where RayFlow Adds Value

RayFlow is not trying to replace a professional console. It adds value by
making the creative and technical show plan explicit, reviewable, and
portable:

1. **AI-directed design:** natural-language iteration over structured show
   data.
2. **Fixture-aware rendering:** translating design intent to valid output.
3. **Backend choice:** direct DMX for deterministic tests, QLC+ for structured
   open-source control, MA3 for professional compatibility.
4. **Evidence-based automation:** every backend capability must prove state
   changed through queries, captured packets, exports, or recorded manual
   confirmation.

## Why Not Keep MA3 As The Core Layer?

grandMA3 is powerful, but the live probes showed that it is not an ideal
terminal-agent API:

- setup is show-local;
- command acceptance is not equivalent to UDP listener presence;
- command-line destination changes command meaning;
- fixture import and patching are still not repeatable through CLI alone;
- readback is indirect.

Those traits make MA3 a compatibility adapter, not the safest core execution
loop.

## Future Visualization

A custom visualizer is still optional. RayFlow can use MA3, QLC+, a future web
visualizer, or captured DMX frames for verification depending on the backend.
The renderer and adapter contract should not depend on a single visualizer.
