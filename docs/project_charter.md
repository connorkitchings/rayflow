# Project Charter

## Goal
A beginner takes a song, builds a stage, and produces a lit version of the song in grandMA3 onPC, with AI doing the heavy programming and explaining each piece, so the user learns the console while getting a result.

## Decisions
- **Stack:** grandMA3 onPC (Mac) with its built-in 3D viewer. Capture deferred until a viz-key is purchased; onPC does not output to Capture without MA hardware.
- **AI role:** hybrid. AI generates the patch, groups, presets, cues and song timecode as MA3 Lua plugins and import files. The user loads them, watches in 3D, tweaks by hand, and AI explains.
- **Scope discipline:** every capability is proven by hand in MA3 (a spike) before any generator is written for it.
- **No custom AI framework or MCP server in v1.** Claude reads the research docs plus the song and design files and writes `design.yaml`.

## Pilot
Climb to Safety (Widespread Panic), end to end.

## Success
Generated plugin and timecode XML, run in a fresh show: the song plays, cues fire, and the 3D viewer shows the intended look.

## Non-goals (v1)
DMX/Art-Net/sACN output, QLC+, Capture, hardware consoles, a custom UI.

## History
v1 (YAML show models, DMX renderer, exporters) is archived at tag `archive/rayflow-v1`.
