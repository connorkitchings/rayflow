# Palette and Preset Design Philosophy

**Source:** Web research, console manuals, professional programming guides
**Parsed:** 2026-05-25

## What Palettes Are (and Why They Matter for RayFlow)

Palettes (called Presets on grandMA3) are named references to fixture attribute values — positions, colors, gobos, beam settings — stored independently of cues. A cue records a *pointer* to a palette, not the raw DMX values. When the palette is updated, every cue referencing it updates automatically.

For RayFlow, palettes are the bridge between the AI's creative intent ("make it warm and moody") and concrete DMX output. The palette model determines how reusable, portable, and maintainable the AI's design decisions are.

## Palette Types by Scope

| Scope | Description | When to Use |
|-------|-------------|-------------|
| **Global** | Applies to all fixture types. A "Red" global palette stores per-fixture channel values that produce red on each type. | Color, dimmer — attributes where the intent is universal |
| **Universal** | Applies to fixtures of the same type family (all spots, all washes). Different families may have different palette data. | Position — a spot and a beam fixture point to different DMX positions for "Stage Right" |
| **Selective** | Applies to a specific group of fixtures, possibly of different types. | Special-purpose: "Band Key Light" position for the front truss fixtures |
| **All** | Applies to every fixture in the rig. | Full rig blackout, full rig white |

## How Many Palettes? Designing a Palette Library

### Color Palettes

| Minimum Set | Purpose |
|-------------|---------|
| 8–12 named colors | Red, Orange, Amber, Yellow, Green, Cyan, Blue, Lavender, Magenta, Pink, White, Warm White |
| 4–6 show-specific | Custom colors matching the show's vibe palette |
| 1–2 "Open" / "No Color" | Returns color mixing to open white |

### Position Palettes

| Minimum Set | Purpose |
|-------------|---------|
| 4–8 stage positions | DSL (Downstage Left), DSC, DSR, CSL, CS, CSR, USL, USC, USR |
| 2–4 band positions | "Lead Singer," "Guitar 1," "Drummer," "Keys" |
| 2 audience positions | "Audience Left," "Audience Right" |
| 1 "Home" | Fixture's neutral/zero position for safety |

### Beam Palettes

| Minimum Set | Purpose |
|-------------|---------|
| 2–3 gobo selections | "Breakup," "Open," "Logo" |
| 2–3 zoom levels | "Narrow," "Medium," "Wide" |
| 1–2 focus settings | "Sharp," "Soft" |
| 1 "Open" | No gobo, iris open, no frost |

### Typical Total Palette Count

A well-designed show file has 40–60 palettes across all attribute families. More than 80 becomes unwieldy. Fewer than 25 limits creative flexibility.

## Palette Update Propagation

When a palette is modified, the console recalculates every cue that references it. This is the fundamental power of palette-based programming, but it carries risks:

### Safe Updates
- Changing a color palette's per-fixture values. Every cue using that color smoothly transitions to the new mix.
- Updating a position palette after venue recalibration (different trim height).

### Risky Updates
- Changing a palette's scope (selective → global). May break cues that depended on the selective scope.
- Deleting a palette that is referenced by active cues. Creates "broken references" — some consoles fall back to absolute values, others go dark.

### Best Practice: Palette Versioning
- Before a major palette update, clone the palette as "Red v2" and selectively re-point cues. This preserves the old look as a fallback while testing the new one.

## Palette-Driven Programming vs. Absolute Programming

| Approach | Cue Content | Edit Impact | Tour Compatibility |
|----------|------------|-------------|-------------------|
| **Palette-Driven** | Palette references only | Update once, propagate everywhere | High — update position palette for new venue |
| **Absolute** | Raw DMX/channel values per cue | Manually edit every affected cue | Low — every cue needs per-venue editing |
| **Hybrid** | Palettes for position/color, absolute for specialty effects | Mixed impact | Moderate |

RayFlow should encourage palette-driven authoring. The AI should generate position, color, beam, and gobo presets, then record cues that reference them.

## RayFlow's Current Preset Model

The current `Preset` dataclass stores:
- `name`, `description`, `attributes` (keyed by family: dimmer, position, color, beam, focus, gobo)
- `channels` (specific fixture channel references)
- `tags` (for categorization)

Gaps versus professional palette design:

1. **Scope control:** No distinction between global, universal, selective, or all presets.
2. **Per-fixture values:** A preset stores one set of values, but professional palettes store per-fixture values (fixture A's "Red" may need different DMX values than fixture B's).
3. **Palette count guidance:** The authoring system doesn't suggest how many presets to create or what minimum set is needed.
4. **Update propagation:** The current model doesn't track which cues reference which presets, making it hard to warn about risky palette edits.

## Implications for RayFlow

1. **Scope field on Preset:** Add a `scope` attribute (global, universal, selective, all) to the `Preset` model.
2. **Per-fixture preset values:** Support per-fixture override maps within a preset (e.g., fixture "Spot 1" → DMX pan=128, fixture "Spot 2" → DMX pan=64 for the same "Stage Right" position preset).
3. **Minimum palette generation:** When creating a show on a new rig, the authoring system should auto-generate a minimum set of position, color, and beam palettes.
4. **Cue-to-preset reference tracking:** The `Cue` model's `preset` field should be enriched — a cue may reference multiple presets (one per attribute family), and the relationship should be tracked for update validation.
5. **Palette library as shared resource:** Like the fixture library, maintain a palette library with common templates (standard stage positions, common colors, standard gobo selections) that can be imported into any show.
