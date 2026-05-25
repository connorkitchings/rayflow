# Fixture-Aware DMX Renderer

The renderer translates RayFlow cue intent into concrete DMX universe/channel
frames, using GDTF channel maps to resolve abstract attributes to fixture-specific
addresses.

## Location

`src/rayflow/rendering/dmx.py`

## Data Structures

| Structure | Purpose |
|-----------|---------|
| `DmxFrame` | Sparse DMX channel values for one universe (`{channel: value}`) |
| `DmxRenderWarning` | Non-fatal warning when a fixture lacks a requested attribute |
| `RenderedCue` | Dry-run render result: cue metadata + frames + warnings |
| `RenderedCueGroup` | Ordered render results for a section or complete show |

## Supported Attribute Families

| Family | Attributes | Rendering |
|--------|-----------|-----------|
| Dimmer | `dimmer` | Percentage to 0-255 (or 16-bit pair) |
| Color | `color` (RGB/RGBW/named) | Named color lookup or direct RGB/RGBW to fixture channels |
| Position | `pan`, `tilt`, `position.pan`, `position.tilt` | Percentage to channel range; 16-bit fine channels when available |
| Beam | `zoom`, `focus` | Percentage to 0-255 |
| Effects | `shutter`, `gobo` | Percentage to 0-255 |

When a fixture mode lacks a requested channel, the renderer emits a
`DmxRenderWarning` and skips that attribute for that fixture.

## Rendering Functions

| Function | Scope | CLI Command |
|----------|-------|-------------|
| `render_cue_to_dmx()` | Single cue | `rayflow show render-cue` |
| `render_section_to_dmx()` | All cues in a section | (used internally) |
| `render_show_to_dmx()` | All cues in a show | (used internally) |

## Output Flow

```text
Show + Rig + Cue
    |
    v
resolve_presets() → expand fixture-level overrides
    |
    v
For each FixtureSlot:
    load GDTF channel map → match attribute families → compute DMX values
    |
    v
DmxFrame per universe (sparse: only channels with values)
    |
    v
RenderedCue (frames + warnings + metadata)
```

## Backend Output

Rendered frames are passed to a backend adapter for dry-run or live output:

- `show output-cue` — render + send through selected backend
- `show output-section` — render + send all cues in a section

Dry-run is the default. Use `--execute` to apply through the backend.

## Testing

Tests use real checked-in GDTF samples from `data/fixtures/samples/` to validate
channel map resolution, 16-bit channel handling, named color lookups, and warning
generation for missing attributes.

## See Also

- [Backend Adapter Contract](./backend-adapter-contract.md) — interface for output backends
- [System Overview](./system_overview.md) — where the renderer fits in the architecture
- [AI Interaction Contract](../ai_interaction_contract.md) — renderer-supported attribute families
