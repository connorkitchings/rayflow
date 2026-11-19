---
name: ld-designer
description: "Write a song's design.yaml with per-section reasoning that names the lighting-design technique used and cites the style guide or LD profile"
---

# LD Designer

## Inputs
- `docs/design/style-guide.md`
- Profiles `docs/research/concert-lds/01..06-*.md`
- `songs/<song>/song.yaml` (sections, energy, mood) and the rig in `docs/learn/starter-rig.md`

## Steps
1. Read the style guide, then the profiles, then `song.yaml`. Note each section's energy and mood.
2. For each section, pick a look using only what the rig can do (4 movers, 8 washes).
3. Write `songs/<song>/design.yaml`. Each section has: look, color, movement, timing, and `reasoning`.
4. In `reasoning`, name the technique (for example the profile's signature look) and cite its source: `style-guide.md#<heading>` or `<profile file> [n]`.
5. Explain the result to the user in plain English, section by section.

## Rules
- No technique without a citation. If nothing sourced fits, say so and mark the choice **unverified**.
- Do not use effects the style guide forbids or the rig cannot render.
- design.yaml describes intent; it does not claim MA behavior. Any MA claim cites a probe or the manual.
