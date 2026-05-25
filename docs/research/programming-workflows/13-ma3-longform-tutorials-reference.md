# MA3 Longform Tutorial References

**Source:** YouTube, three instructional videos
**Raw transcripts:** `docs/research/raw_sources/ma3-longform/`
**Parsed:** 2026-05-26

---

## Video 1: Learn GrandMA3 Programming — Full Show In 102 Minutes

**URL:** https://www.youtube.com/watch?v=Gwpt_ZyyNKU
**Duration:** ~102 minutes
**Transcript:** 2,271 lines

### Summary
A complete show-building walkthrough from blank show file to finished programming. Covers the entire MA3 workflow in linear sequence: interface tour → patching → 3D positioning → groups → presets → effects → sequences → executors → recording cues. Targeted at users who know MA2 and are transitioning to MA3.

### Key Topics
- Interface overview (command section, master controls, speed masters, screen layout)
- Patching fixtures from GDTF and MA3 library
- 3D fixture positioning (X/Y/Z in meters)
- Creating groups by fixture type and position
- Building position, color, gobo, beam, and dimmer presets
- Phaser effects (chase and movement)
- Sequence creation and cue recording
- Executor assignment to faders and buttons
- Speed master setup for tempo control
- Store modes (Merge, Overwrite, Remove)

### Unique Value
- Complete end-to-end workflow in one session — mirror of what RayFlow needs to automate
- Practical "real LD" perspective rather than feature-by-feature documentation
- MA2-to-MA3 transition context (notes what's different)

---

## Video 2: GrandMA3 Beginner / 2 Hour Crash Course

**URL:** https://www.youtube.com/watch?v=HVd27azY0vc
**Duration:** ~2 hours
**Transcript:** 2,623 lines

### Summary
A comprehensive beginner introduction to MA3. Starts from absolute zero — what is DMX, what is a fixture, what does a console do — and builds through the complete MA3 workflow. More foundational than the "Full Show in 102 Minutes" video, with deeper explanations of WHY things work the way they do.

### Key Topics
- DMX basics (what it is, how addressing works, universe structure)
- Console layout and navigation
- Patch fundamentals (fixture types, modes, addressing)
- 3D visualizer for seeing your programming
- Groups and worlds (filtering fixture views)
- Presets (position, color, gobo, beam, dimmer)
- Effects/phasers
- Sequences and cues
- Executor pages and faders
- Show file management

### Unique Value
- Deep DMX fundamentals — useful for the AI's knowledge base when explaining concepts to amateur users
- Step-by-step, no-assumptions approach
- Covers worlds (a concept not in our other MA3 references) — filtered views of the rig that don't affect programming

---

## Video 3: The EXTREME POWER Of GrandMA3 Recipes For Your Tour

**URL:** https://www.youtube.com/watch?v=jtf__V9jYkg
**Duration:** ~8 minutes
**Transcript:** 233 lines

### Summary
A focused tutorial on MA3 cue recipes — how to use abstract "apply Preset to Group" rules instead of storing absolute fixture values in cues. Demonstrates the tour-ready power of recipes: swap fixture types, add or remove fixtures from groups, and all recipe-based cues update automatically without reprogramming.

### Key Technical Details (Extracted from Transcript)

**Enabling Recipes View:**
Press MA button → Settings → Mask → enable "Show Recipes"

**Recipe Structure:**
A cue contains recipes, not values. Each recipe line has:
- **Selection:** which group of fixtures to apply to
- **Value:** which preset/pool entry to apply (dimmer, position, color, gobo, etc.)

**Building a Recipe Cue:**
1. Right-click in the recipe section of a cue
2. Set the selection (group) → e.g., "Astra 600"
3. Set the value (preset) → e.g., Dimmer Preset 1
4. Add more recipe lines for additional attributes

**Tour-Ready Power:**
- **Fixture swap:** Change a group's fixture type in the patch → all recipe cues update because they reference the group, not specific fixture IDs
- **Fixture count change:** Add or remove fixtures from a group → recipes scale automatically
- **Preset update:** Change a preset's values → all recipe cues using that preset update
- **Venue adaptation:** Arrive at a venue with different fixtures → swap the fixture type in the patch → show adapts

**Recipe vs. Absolute Cues:**
- Absolute cues store fixture ID + DMX value. Venue change = reprogram everything.
- Recipe cues store group + preset reference. Venue change = update the patch or preset once, cascade everywhere.

### Unique Value for RayFlow
- **Recipes are the ideal RayFlow authoring abstraction.** The AI generates "Apply Color Preset 'Deep Blue' to Group 'Backlight'" — portable, maintainable, and venue-adaptable — rather than "Fixture 701 channel 5 = 187."
- **Recipe-based show files survive fixture changes.** This is exactly what amateur users need: build a show once, adapt it to different virtual rigs without reprogramming.
- **The "tour-ready" concept maps to RayFlow's "rig-portable" concept.** A show generated for one rig should work on a different rig if the group and preset structure is maintained.

---

## Cross-Video Patterns

| Concept | Video 1 (102m) | Video 2 (2h crash) | Video 3 (recipes) |
|---------|---------------|-------------------|-------------------|
| Skill level | MA2→MA3 transition | Absolute beginner | Intermediate |
| Focus | Practical show building | Fundamentals + workflow | Single advanced feature |
| Patching | ✅ | ✅ (with DMX theory) | — |
| 3D positioning | ✅ | ✅ | — |
| Groups | ✅ | ✅ | ✅ (recipe selection) |
| Presets | ✅ | ✅ | ✅ (recipe values) |
| Effects | ✅ | ✅ | — |
| Sequences | ✅ | ✅ | ✅ (recipe-based) |
| Recipes | — | — | ✅ (deep dive) |
| Worlds | — | ✅ | — |
| MA2 comparison | ✅ | — | — |
| Tour adaptability | — | — | ✅ |

---

## Implications for RayFlow

1. **Recipe-based authoring is confirmed as the ideal AI paradigm.** All three videos converge on groups + presets as the foundational building blocks. Video 3 explicitly shows why: portability.

2. **The complete MA3 workflow is now documented across 5 sources:** ACT Entertainment series (22 episodes), this creator's series (19 episodes), plus these 3 longform videos. The AI has comprehensive command coverage for automated show building.

3. **"Worlds" are a new concept for our knowledge base.** They're filtered views of the rig that segment fixtures for programming convenience without affecting output. Useful for the AI to organize complex rigs into manageable sections.

4. **The "beginner" video provides the DMX fundamentals explanation** that the AI can use when explaining concepts to amateur users who have never touched a lighting console.

5. **The recipe video confirms that recipe-based cues are the future-proof export format.** If RayFlow generates recipe-based cues, the user can swap their virtual rig from "Small Club" to "Mid-Size Venue" and the show adapts automatically.
