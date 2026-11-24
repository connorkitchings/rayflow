# RayFlow stage interchange

[RayFlow_Stage.mvr](RayFlow_Stage.mvr) packages the stage scenery, twelve lighting fixtures, their positions and their DMX addresses. Use this file to transfer the rig between design applications. Cues, lit looks, and audience cameras belong to the application that opens the rig.

## Patch

A fixture ID selects a light. Its DMX address identifies the first channel it uses. All twelve fixtures use universe 1. The MAC Ultra Performance uses Basic mode with 48 channels. The MAC Aura XB uses Standard mode with 14 channels. These are the profiles embedded in this file. The fixture IDs and hang positions follow the [RayFlow starter rig](../../docs/learn/starter-rig.md).

| ID | Model | Start address | X (m) | Y (m) | Z (m) |
|---:|---|---:|---:|---:|---:|
| 1 | Ultra Performance | 1.001 | −3 | 6 | 7 |
| 2 | Ultra Performance | 1.049 | −1 | 6 | 7 |
| 3 | Ultra Performance | 1.097 | 1 | 6 | 7 |
| 4 | Ultra Performance | 1.145 | 3 | 6 | 7 |
| 101 | Aura XB | 1.193 | −4.5 | −2 | 6 |
| 102 | Aura XB | 1.207 | −1.5 | −2 | 6 |
| 103 | Aura XB | 1.221 | 1.5 | −2 | 6 |
| 104 | Aura XB | 1.235 | 4.5 | −2 | 6 |
| 105 | Aura XB | 1.249 | −4 | 6 | 7 |
| 106 | Aura XB | 1.263 | −2 | 6 | 7 |
| 107 | Aura XB | 1.277 | 2 | 6 | 7 |
| 108 | Aura XB | 1.291 | 4 | 6 | 7 |

## Stage geometry

Positive X runs toward audience right, positive Y goes upstage, and positive Z goes up. The 12 × 10 m deck is centered at Y = 2 m with its top at Z = 0. The 3 × 2 m drum riser is centered at Y = 5 m, with its top 0.45 m above the deck. Both trusses span 11 m. The downstage truss sits above Y = −2 m with its underside at Z = 6 m. The upstage truss sits above Y = 6 m with its underside at Z = 7 m.

MVR object translations use millimetres. The embedded GLB meshes use metres and local Y-up coordinates. Each GDTF fixture profile contains its model and DMX channel definitions.

## Sources and checks

The reference input is **Demostage_MVR.mvr**, shipped with grandMA3 onPC 2.5.1.1. The two complete Martin GDTF profiles come from that archive. Each truss uses four 2.75 m bays derived from its Symbol 5 truss mesh. The deck and riser are original box meshes.

PyMVR 1.0.7 independently reopened the stage and resolved all twelve fixtures and four scenery objects. The offline check confirmed fixture IDs, hang coordinates, profile modes, and non-overlapping DMX addresses through 1.304. Mesh bounds confirmed the deck, riser and truss dimensions. The live grandMA3 import and rendered appearance require separate checks.

## Rebuild a copy

From this directory, run the one-off build with the demo installed on your Mac. Supply a fresh output filename. On another machine, substitute the local path to the same MA demo.

```sh
uv run --script build_stage.py \
  "$HOME/MALightingTechnology/gma3_2.5.1/shared/resource/lib_mvr/Demostage_MVR.mvr" \
  RayFlow_Stage_rebuilt.mvr
```

The reference demo used here has SHA-256 `5b2c456dc42d5d780ed6644aae005585e153710057671175a6e677caf7bc29ed`. A clean rebuild reproduced all six archive members byte for byte. ZIP timestamps can vary between runs.
