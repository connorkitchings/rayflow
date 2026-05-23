# Comparative Synthesis

## Platform Comparison

| Platform | Best Use | Agent Fit | Main Strength | Main Risk |
| --- | --- | --- | --- | --- |
| grandMA3 onPC | Professional MA-compatible show delivery | Medium to low until readback is proven | Industry workflow, Timecode, show export/playback | Fragile OSC setup, command context, weak structured feedback |
| QLC+ | Structured cue-based automated shows | High | Plain WebSocket command surface with query paths | Less aligned with pro MA venue workflows |
| Python Art-Net/sACN | Generative realtime lighting and deterministic tests | High | Direct protocol control, inspectable frames, no console UI dependency | RayFlow must own fixture mapping, safety, and show semantics |
| Chataigne | Middleware for mixed protocols and MA deployments | Medium to high | Stable translation layer and routing | Adds another runtime to install and configure |
| Open Stage Control | Browser control surfaces and human override | Medium | UI plus OSC/WebSocket bridge | Not a lighting engine by itself |
| ONYX | ONYX-specific control workflows | Medium | OSC and Device Space concepts | Licensing and input/display caveats |
| MagicQ | ChamSys-specific workflows | Low to medium | CREP exists for remote control | Binary protocol and hardware unlock limits |

## Architecture Pattern

The strongest pattern across the research is adapter separation:

```text
AI / Human Direction
        |
        v
RayFlow show intent and fixture model
        |
        v
Deterministic renderer
        |
        +--> QLC+ WebSocket adapter
        +--> Art-Net adapter
        +--> sACN adapter
        +--> grandMA3 export / gated OSC adapter
        +--> Middleware adapter such as Chataigne
```

The renderer boundary is the key. It prevents MA3 command syntax, QLC+ widget IDs, or Art-Net packet details from leaking into the AI-facing show design layer.

## Recommended Backend Priority

1. **RayFlow internal cue and fixture model:** keep as source of truth.
2. **DMX renderer:** convert fixture-aware intent into universe/channel values.
3. **Art-Net and sACN execution:** provide deterministic output and protocol-level verification.
4. **QLC+ WebSocket adapter:** provide a higher-level open-source controller with queryable state.
5. **MA3 export and gated OSC:** preserve professional workflow compatibility, but only promote operations after evidence packets prove them.
6. **Chataigne bridge:** evaluate if MA3 hardware remains mandatory and raw OSC remains unstable.

## Evidence Standard

For every backend operation, require one of:

- a direct structured response;
- a queryable state change;
- a captured DMX frame;
- an exported artifact diff;
- a human-confirmed UI step recorded as explicit evidence.

This standard keeps RayFlow from claiming capabilities based on "a command was sent" rather than "the intended state changed."
