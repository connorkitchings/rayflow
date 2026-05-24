# Backend Adapter Contract

**Status:** Phase 8 implementation contract.

**Phase 8 MVP status:** Implemented for fixture-aware dimmer/RGB/RGBW rendering,
Art-Net/sACN dry-run and gated apply evidence, and an experimental QLC+
WebSocket spike. QLC+ remains experimental until verified against a live local
QLC+ instance. MA3 remains export/playback and gated OSC compatibility.

This document defines the first backend-neutral execution surface for RayFlow.
It is the implementation companion to
[Control Backend Direction](./control-backend-direction.md).

## Goal

RayFlow show, rig, cue, preset, and fixture data remain the source of truth.
Backends are adapters that translate rendered intent into an external system.
The same cue should be inspectable as a dry-run artifact before it is sent over
Art-Net, sACN, QLC+, grandMA3 export files, or gated grandMA3 OSC.

The first implementation slice is intentionally narrow:

- render dimmer and RGB/RGBW cue intent to DMX universe frames;
- report unsupported attributes without corrupting supported output;
- send rendered frames through Art-Net or sACN only behind an explicit execute
  gate;
- capture structured evidence for every claimed backend result;
- keep QLC+ and MA3 behavior evidence-gated until local proof exists.

## Contract Concepts

### ControlBackend

A backend adapter should expose these concepts, regardless of concrete Python
names chosen during implementation:

| Concept | Meaning |
|---------|---------|
| `capabilities` | Static or queried declaration of supported attributes, operations, evidence types, and live-output requirements. |
| `dry_run` | Produce frames, commands, files, or plans without mutating an external target. This is the default mode. |
| `apply` | Perform the operation against the selected backend. This must require an explicit execute flag from the CLI or calling workflow. |
| `evidence` | Return structured proof of what RayFlow produced and what the backend observed or accepted. |

Backends must not require show or cue models to store backend-specific command
syntax. Backend IDs, network targets, controller object IDs, and transport
settings belong in adapter configuration or CLI options.

### Renderer Input

The fixture-aware DMX renderer consumes RayFlow source-of-truth objects:

- `Show`: selected cue, selected section, or whole-show cue list;
- `Rig`: fixture slots, DMX universes, start addresses, positions, and rig
  presets;
- resolved presets from `resolve_presets(rig, show)`;
- fixture capabilities and channel maps from the GDTF fixture library;
- `Cue` intent, including `preset`, `attributes`, `channels`, `fade_time`, and
  timestamp metadata.

The renderer should not know whether the final target is Art-Net, sACN, QLC+,
or MA3. Its output is an intermediate artifact that adapters consume.

### Renderer Output

Renderer output is a deterministic DMX frame plan:

- universe number;
- channel values in the DMX range `0..255`;
- source cue metadata;
- fixture labels and channel map references when available;
- warnings for unsupported, ambiguous, or ignored attributes.

The initial frame plan may be represented as sparse channel values per universe
for dry-run readability. Art-Net and sACN adapters can expand sparse values to
512-channel buffers before sending.

Unsupported attributes must be warnings, not silent drops. A cue with supported
dimmer output and unsupported gobo output should still render the dimmer values
and return a warning for the gobo intent.

### Evidence Packet

Every backend operation returns evidence with the same minimum shape:

| Field | Meaning |
|-------|---------|
| `backend` | Backend name such as `artnet`, `sacn`, `qlcplus`, `ma3-export`, or `ma3-osc`. |
| `operation` | Operation name such as `render-cue`, `send-frame`, `export-bundle`, or `query-state`. |
| `mode` | `dry-run` or `apply`. |
| `target` | Network target, file path, controller endpoint, or other destination summary. |
| `frames` | Rendered universe/channel values when DMX frames are involved. |
| `commands` | Backend commands or generated files when the backend is command/file based. |
| `observed` | Receiver state, query result, exported file proof, packet capture summary, or manual confirmation. |
| `warnings` | Unsupported attributes, skipped fixtures, missing capabilities, or degraded proof. |
| `timestamp` | Operation timestamp in an ISO-like format. |

Sending a command is not evidence by itself. Evidence must prove either the
rendered artifact exists, the receiver observed the frame, the controller query
returned matching state, or a compatibility export was produced.

## Backend V1 Behavior

### Art-Net

Art-Net consumes rendered DMX frames. Dry-run returns the frame plan and target
universe mapping. Apply sends 512-channel universe buffers through the existing
Art-Net bridge and must capture one of:

- Art-Net receiver buffer state;
- packet capture summary;
- explicit test harness observation.

RayFlow uses the existing Art-Net universe convention from
`rayflow.bridge.artnet`, where current validation accepts universes `0..15`.
Any future expansion must update this contract and tests together.

### sACN

sACN consumes the same rendered DMX frames as Art-Net, but with E1.31 universe
numbering. The current bridge defaults to universe `1`, while RayFlow rig data
allows universe values starting at `0`. The first sACN implementation must make
the mapping explicit in adapter configuration and evidence, for example by
recording both `rayflow_universe` and `sacn_universe`.

Apply sends 512-channel universe buffers and must capture receiver state,
packet capture evidence, or test harness observation.

### QLC+

QLC+ is a research adapter until local WebSocket command/query behavior is
proven. The spike should launch or connect to QLC+ with its web interface
enabled and test plain-text WebSocket commands such as:

- list functions;
- set a function status;
- query a function, widget, or channel value.

Until query evidence exists, QLC+ support must be documented as experimental and
must not shape show/cue models around QLC+ function IDs or widget IDs.

### grandMA3

grandMA3 remains a compatibility track:

- MA3 export adapter: MVR, OSC command lists, Timecode XML, README files, and
  handoff bundles.
- Gated MA3 OSC adapter: only operations with command acceptance, disposable
  show protection, and export/readback or UI evidence.

MA3 fixture import, patch mutation, and runtime readback are not mainline Phase
8 dependencies. Do not build MCP tools around MA3 mutation until the underlying
operation has repeatable evidence.

## Example Scenarios

### Render One Dimmer Cue

Given a cue with `attributes: {"dimmer": "50%"}` and a fixture slot whose GDTF
channel map includes a dimmer channel, the renderer produces the corresponding
DMX value, for example channel 1 -> 128. Dry-run evidence includes the rendered
frame and no external output.

### Render One RGB/RGBW Cue

Given a cue with a color attribute resolved from a preset or vibe palette, and a
fixture with RGB or RGBW color channels, the renderer maps red, green, blue, and
optional white values to fixture channels. If a fixture only supports a color
wheel, the renderer reports an unsupported-color warning for v1.

### Report Unsupported Attributes

Given a cue with dimmer and gobo attributes where the fixture supports dimmer
but has no gobo channel, the renderer emits the dimmer channel value and records
a warning for the gobo attribute. The warning should name the cue, fixture, and
unsupported family.

### Capture Art-Net Or sACN Evidence

Given a rendered frame and `--execute`, the selected backend sends the frame and
returns evidence showing the frame plan plus the receiver observation or packet
capture summary. A successful send without receiver/capture proof is degraded
evidence and must be marked as such.

### Treat QLC+ As Research

Given a request to use QLC+, the next implementation should run a WebSocket
command/query spike and record the exact request, response, endpoint, and QLC+
version. It should not promote QLC+ to a supported backend until query evidence
proves state can be read back.

## Acceptance Checklist

- Backend-specific command syntax does not leak into `Show`, `Rig`, `Cue`, or
  `Preset` models.
- Dry-run is the default for every backend.
- Apply requires an explicit execute flag.
- Evidence is returned for every backend operation RayFlow claims as supported.
- Unsupported attributes are reported as warnings with enough context to fix the
  cue, fixture, or adapter.
- The first renderer slice is limited to dimmer and RGB/RGBW fixtures.
- QLC+ remains a research adapter until local WebSocket query evidence exists.
- MA3 remains export/gated OSC compatibility and does not block fixture-aware
  DMX rendering.
