# Control Backend Direction

**Status:** Current architecture direction as of 2026-05-23.

## Decision

RayFlow's core execution path should be backend-neutral. The show, rig,
fixture, cue, and vibe data in RayFlow are the source of truth. Backends are
adapters that translate that source of truth into concrete output:

- direct Art-Net or sACN DMX frames;
- QLC+ WebSocket commands and queries;
- grandMA3 export artifacts such as MVR, command lists, and Timecode XML;
- gated grandMA3 OSC commands for operations that have evidence.

grandMA3 remains an important professional compatibility target, but it is no
longer the blocker for the next RayFlow milestone.

## Why This Changed

The MA3 control probes proved useful facts, but also exposed structural
friction:

- OSC command receive is show-local and row-specific.
- UDP listener detection does not prove command acceptance.
- `/cmd` commands inherit MA3's current command-line destination.
- Fixture import and patching through MVR/command-line paths were not
  repeatably proven.
- Readback is indirect and often requires exports, UI observation, or Lua
  probes.

The manual research in
`docs/research/agentic_show_control_architectures/` reaches the same
conclusion: terminal agents work best against deterministic, structured,
queryable interfaces.

## Target Shape

```text
RayFlow show/rig/cue data
        |
        v
Fixture capability resolver
        |
        v
Fixture-aware DMX renderer
        |
        +--> Art-Net output
        +--> sACN output
        +--> QLC+ WebSocket adapter
        +--> MA3 export adapter
        +--> gated MA3 OSC adapter
```

## Adapter Contract

Every backend should eventually expose the same concepts:

- **dry run:** produce the commands, frames, or files without mutating external
  state;
- **apply:** perform the output operation only when explicitly requested;
- **evidence:** return structured proof such as command responses, query
  results, captured DMX frames, exported files, or recorded manual
  confirmations;
- **capabilities:** declare supported fixture attributes and unsupported
  operations.

The implementation-level contract is maintained in
[Backend Adapter Contract](./backend-adapter-contract.md). Use that document
for the Phase 8 interface shape, renderer inputs and outputs, evidence packet
fields, and backend-specific v1 behavior.

## Near-Term Priorities

1. Define the backend adapter boundary.
2. Render simple dimmer and RGB/RGBW cue intent to DMX universe frames.
3. Verify Art-Net/sACN output by captured packets or receiver state.
4. Add a QLC+ WebSocket research spike with command/query evidence.
5. Keep MA3 export and OSC probes as a compatibility track.

## Non-Goals

- Do not build MCP tools around unverified MA3 mutation.
- Do not make MVR import into MA3 the critical path for the next milestone.
- Do not claim backend support unless an evidence packet proves state changed.
