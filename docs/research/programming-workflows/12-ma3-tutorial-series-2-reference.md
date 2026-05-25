# GrandMA3 Tutorial Series 2 — Reference Index

**Source:** YouTube playlist — https://www.youtube.com/playlist?list=PL_CGrOZmBj_DiqpjYDRltnnR8pSRRocv3
**Episodes:** 19
**Total duration:** ~1h 38m
**Raw transcripts:** `docs/research/raw_sources/ma3-tutorial-series-2/`
**Parsed:** 2026-05-26

---

## Episode Index

| # | Title | Duration | Video ID |
|---|-------|----------|----------|
| E01 | Patching Fixtures in GrandMA3 | 3:00 | o5hYaurUw0Y |
| E02 | Positioning Fixtures in 3D - GrandMA3 | 4:50 | Wwz0wpYi110 |
| E03 | Creating Fixture Groups in GrandMA3 | 3:02 | ViC1mFf1Lro |
| E04 | Multi-Instance Fixtures - GrandMA3 | 3:01 | 0JuAuXX4F5o |
| E05 | Selection Grid in GrandMA3 | 4:36 | UacbVfDNRbg |
| E06 | Creating Presets in GrandMA3 | 6:11 | yqiYjbZek1k |
| E07 | Selective, Global & Universal Presets in GrandMA3 | 4:18 | nQ20BX1kPYE |
| E08 | Creating & Using Filters in GrandMA3 | 5:37 | 95jn4aVWMb0 |
| E09 | Magic Presets - GrandMA3 | 3:26 | jqdqK1iXUZk |
| E10 | Phasers in GrandMA3 - Chase Effects | 5:25 | 296WRfavW80 |
| E11 | Phasers in GrandMA3 - Movement Effects | 4:24 | s1weufDsI3E |
| E12 | Sequences in GrandMA3 | 4:24 | EQre3DhVqPM |
| E13 | Cue Recipes in GrandMA3 | 5:19 | 7FXzgPIFSMI |
| E14 | Updating Groups Used In Recipes - GrandMA3 | 12:06 | Ie4iFke2cwY |
| E15 | Universal MAgic Presets? - GrandMA3 | 12:08 | q8pE4ry0D5s |
| E16 | Universal MAgic Presets? Method 2 - GrandMA3 | 6:02 | F6sxrG-vfTA |
| E17 | Understanding Preset Modes - GrandMA3 | 8:31 | DQSlCpskSFM |
| E18 | How I Set Up My Multi-Instance Fixtures | 10:53 | B7HJxNwFGpY |
| E19 | Creating Virtual Dimmers in GrandMA3 | 12:51 | sBTS7iiVsBQ |

---

## Series Structure

This series builds a complete MA3 show from scratch, progressing through:
1. **Foundation (E01–E05):** Patching → 3D positioning → Groups → Multi-instance → Selection Grid
2. **Presets (E06–E09):** Creating → Selective/Global/Universal → Filters → Magic Presets
3. **Effects (E10–E11):** Phaser chase effects → Phaser movement effects
4. **Sequencing (E12–E16):** Sequences → Cue Recipes → Updating recipe groups → Universal Magic Presets (two methods)
5. **Advanced (E17–E19):** Preset modes → Multi-instance setup → Virtual Dimmers

---

## Key Differences from Series 1 (ACT Entertainment)

| Aspect | Series 1 (ACT) | Series 2 (This) |
|--------|---------------|-----------------|
| Focus | MA3 fundamentals, screen-by-screen | Building a practical show file |
| Preset approach | Basic swipey/pool workflow | Deep dive into Selective/Global/Universal/Magic presets |
| Filter system | Not covered | Dedicated episode on creating and using filters |
| Recipes | Not covered | Two-episode deep dive on Cue Recipes |
| Multi-instance | Not covered | Three episodes on multi-instance setups |
| Virtual Dimmers | Not covered | Dedicated episode — advanced workflow |
| Style | Official MA3 tutorial voice | Practical, working-LD perspective |

---

## Unique Concepts Not Covered Elsewhere in Our Research

### 1. Cue Recipes (E13)
Instead of hard-coding fixture values into cues, recipes use abstract rules: apply Preset X to Group Y. When you update the preset or group, all recipe cues update automatically. This is the MA3 equivalent of palette-based programming but taken further — the recipe defines which fixtures to apply which preset to, rather than storing per-fixture values.

### 2. Selective vs. Global vs. Universal Presets (E07)
- **Selective:** Preset values stored per specific fixture. Fixture 1's "Red" can differ from Fixture 2's "Red."
- **Global:** A single value applied to all fixture types that share the attribute. Changing it changes it for everything.
- **Universal:** Fixture-type-aware. A "Red" universal preset stores different DMX values for spots vs. washes but presents as one preset to the user.

### 3. Filters (E08)
MA3 filters determine which attributes get stored when you record a cue. You can create a "Color Only" filter that only records color values, or a "Position Only" filter, etc. This enables partial cue recording — updating only color while keeping everything else tracked.

### 4. Magic Presets (E09)
A "Magic Preset" stores values across all preset types simultaneously — position + color + gobo + beam in one preset. Applying it sets everything at once. This is the MA3 version of a "look" or "snapshot."

### 5. Virtual Dimmers (E19)
For multi-instance fixtures where the real dimmer affects all instances, you create a virtual dimmer — a DMX channel not in the GDTF profile that the console treats as a dimmer for intensity control without affecting the actual fixture's master dimmer.

---

## Usefulness for RayFlow

### For the AI Authoring System

1. **Recipe-based authoring is the ideal abstraction.** Instead of "Cue 5 sets fixture 701 to value 187," the AI should think in recipes: "Cue 5 applies Color Preset 'Deep Blue' to Group 'Backlight'." This is more portable, more maintainable, and closer to how LDs actually program.

2. **Filter system maps to the four controllable properties.** The "Color Only" filter = only modifying the Color property. "Position Only" = only modifying Distribution. The AI's per-property critique becomes a filter application.

3. **Magic Presets are the user's "look" concept.** When the user says "I want the chorus to look like this," they're describing a Magic Preset. The AI should generate Magic Presets as composite looks, not separate position/color/gobo/dimmer presets.

4. **Virtual Dimmers solve a real authoring problem.** When cueing multi-cell fixtures (washes, pixel bars), the AI needs to control per-cell intensity without killing the fixture's master dimmer. Virtual dimmers enable this.

### For Console Integration

5. **Recipes are export-friendly.** A recipe ("Apply Preset X to Group Y") is a single MA3 command. Exporting recipes is simpler than exporting per-fixture per-cue DMX values.

6. **Filters prevent tracking contamination during authoring.** When the AI generates a cue that only changes color (and leaves position tracked), it should apply a "Color Only" filter to the Store command.

---

## Comparison to Our Existing MA3 Knowledge

| Concept | Series 1 (ACT) coverage | Series 2 (this) coverage | New for RayFlow? |
|---------|------------------------|------------------------|-----------------|
| Patching | E02 | E01 | Covered |
| 3D positioning | E04 | E02 | Covered |
| Groups | E03 | E03 | Covered |
| Selection Grid / MAtricks | E14 (MAtricks) | E05 | Partially covered |
| Preset creation | E05 (swipeys) | E06 | Covered |
| Selective/Global/Universal | Not covered | E07 | **NEW** |
| Filters | Not covered | E08 | **NEW** |
| Magic Presets | E07 (Recast) | E09 | **NEW — different concept** |
| Phaser chase effects | E10 (beginners) | E10 | Deeper coverage |
| Phaser movement effects | E11 (flyout) | E11 | Deeper coverage |
| Sequences | E08 | E12 | Covered |
| Cue Recipes | Not covered | E13 | **NEW — high value** |
| Recipe group updates | Not covered | E14 | **NEW** |
| Universal Magic Presets | Not covered | E15–E16 | **NEW** |
| Preset modes | Not covered | E17 | **NEW** |
| Multi-instance setup | Not covered | E18 | **NEW** |
| Virtual Dimmers | Not covered | E19 | **NEW** |

---

## Implications for RayFlow

1. **Recipe-based cue generation should be the primary authoring model.** Recipes are cleaner, more portable, and more console-exportable than absolute DMX values. Prioritize recipe generation over per-fixture value generation.

2. **Selective → Global → Universal → Magic is a preset scope hierarchy.** The AI should generate presets at the right scope level for each use case. Color presets should be global. Position presets should be selective (per fixture). Composite looks should be Magic Presets.

3. **Filters enable safe partial cue updates.** When the user says "just change the color of cue 12," the AI should apply a Color Only filter — not regenerate the entire cue risking position/dimmer loss.

4. **Virtual dimmers unlock multi-cell fixture authoring.** Pixel-mapped fixtures need per-cell intensity control. Virtual dimmers are the MA3 mechanism for this. The AI should know when to create them.

5. **The two series together provide complete MA3 command coverage for automated show building.** Series 1 covers fundamentals; Series 2 covers advanced presets, recipes, and fixture configuration. Together they span everything the AI needs to generate a valid MA3 show file.
