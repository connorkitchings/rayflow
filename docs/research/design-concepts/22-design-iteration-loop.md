# The Design Iteration Loop: Author → Critique → Refine

**Source:** Industry knowledge, LD workflows, design process theory
**Parsed:** 2026-05-26

## The Loop

The lighting designer's fundamental workflow is not linear. It is a tight loop repeated hundreds of times per show:

```
        ┌──────────────────────────┐
        │      AUTHOR (build)       │
        │  Create/change a look     │
        └─────────────┬────────────┘
                      │
                      ▼
        ┌──────────────────────────┐
        │     VISUALIZE (see)       │
        │  See the result in        │
        │  pre-viz, console, or DMX │
        └─────────────┬────────────┘
                      │
                      ▼
        ┌──────────────────────────┐
        │     CRITIQUE (judge)      │
        │  Does this work?          │
        │  What's wrong?            │
        │  What would make it       │
        │  better?                  │
        └─────────────┬────────────┘
                      │
          ┌───────────┴───────────┐
          │                       │
          ▼                       ▼
    ┌──────────┐          ┌──────────────┐
    │  COMMIT  │          │    REFINE     │
    │  Done.   │          │  Iterate on   │
    │  Move on.│          │  the change.  │
    └──────────┘          └──────┬───────┘
                                 │
                                 └──→ back to AUTHOR
```

## The Loop in Practice

### Author (Build)
The LD does something: records a cue, adjusts a palette, builds an effect, changes a color. The action is small — one cue, one parameter change, one look. LDs don't design an entire show at once; they build it one moment at a time.

### Visualize (See)
The LD sees the result. This happens in pre-viz software during pre-production, on the console output window during programming, or on the actual stage during tech rehearsal. The visualization doesn't need to be perfect — it needs to be *fast*. The key metric is latency between authoring and seeing: sub-second is ideal; 15+ seconds breaks the flow.

### Critique (Judge)
The LD evaluates against multiple criteria simultaneously:

| Criteria | Question | Concert Example | Theater Example |
|----------|----------|----------------|----------------|
| **Visibility** | Can I see what I'm supposed to see? | Is the lead singer's face lit? | Can the audience read the actor's expression? |
| **Energy** | Does it match the musical moment? | Does the snap land on the kick drum? | Does the fade feel like sunset or like an error? |
| **Focus** | Where is the audience looking? | Is the beam pulling eyes to the guitarist during the solo? | Is the brightest thing on stage the thing the audience should watch? |
| **Contrast** | Is there enough difference from the previous moment? | Is this chorus visually bigger than the verse? | Does this scene feel different from the last? |
| **Taste** | Does it feel right artistically? | Would Kuroda/Waful make this choice? | Does this serve the story? |
| **Technical** | Does it work mechanically? | Did the color wheel settle before the dimmer opened? | Is the gobo sharp at this throw distance? |

### Commit or Refine
- **Commit:** The look works. It passes all criteria. Move to the next moment.
- **Refine:** Something is wrong. The LD identifies the specific problem and fixes it: "dimmer is 10% too hot," "blue is too saturated," "movement is too fast for this section," "the fixture group is wrong — this should be washes, not spots."

The LD loops through Author → See → Critique → Refine → See → Critique... until the look passes. Then commits and moves on.

## How Fast Is the Loop?

| Phase | Author → See Latency | Loops Per Look | Total Time Per Look |
|-------|---------------------|----------------|---------------------|
| Pre-production (pre-viz) | 1–3 seconds | 2–5 | 10–60 seconds |
| Console programming (output window) | Sub-second | 1–3 | 5–30 seconds |
| Tech rehearsal (real rig) | Real-time | 1–2 | 5–30 seconds |
| Showtime (busking) | Real-time | 0 (no loops — commit or fail) | Instant (one shot) |

## The Inner Monologue

An experienced LD's inner monologue during the loop:

```
BUILD:    "I need a warm front wash for the verse."
SEE:      "Okay, that's up."
JUDGE:    "Amber is reading too yellow on these LEDs. The dimmer is fine.
           But it's flat — no backlight. The singer is blending into the
           backdrop. And the intensity is 5% too hot for a verse."
REFINE:   "Add cool backlight at 60%. Pull spots dimmer to 75%.
           Shift amber to a warmer straw tone."
SEE:      "Better. Singer has rim separation now. But the backlight
           feels too cool against the warm front. Too much contrast for
           a verse — this is a pre-chorus level of drama."
REFINE:   "Shift backlight from deep blue to lavender. Pull backlight
           dimmer to 40%."
SEE:      "Good. The singer is visible, the front is warm but not hot,
           the backlight gives depth without aggression."
JUDGE:    "This works for the verse. Commit. What's next?"
```

## The Micro-Loop vs. the Macro-Loop

### Micro-Loop (Per Look)
The Author → See → Critique → Refine cycle for a single cue or look. Runs in seconds to minutes. The LD polishes individual moments.

### Macro-Loop (Per Song / Per Section)
The LD steps back and evaluates the larger arc:

```
"Does the energy curve of this song work?"
  → Map intensity across sections: Intro (30%) → Verse (50%) → Chorus (80%) → Bridge (40%) → Chorus (90%) → Outro (20%)

"Are the color transitions working?"
  → Warm verse → Cool pre-chorus → Full-spectrum chorus → Monochrome bridge → Explosion final chorus

"Is the contrast arc right?"
  → Sparse intro → Building verse → Dense chorus → Sparse bridge → Maximum climax → Decay outro

"Am I signaling the song structure?"
  → Verse 2 should look different from Verse 1 (same palette, different intensity or position)
  → Each chorus should be progressively bigger (Chorus 3 > Chorus 2 > Chorus 1)
```

### Show-Level Loop
The LD evaluates the entire show's pacing:

```
"Does the show have a journey?"
  → Song 1: Welcoming, warm, moderate energy
  → Song 2-3: Building energy
  → Song 4: First peak
  → Song 5-6: Mid-set contrast (slower, intimate)
  → Song 7-9: Building to set closer
  → Encore: Celebration, full rig, maximum impact

"Are there enough quiet moments?"
  → Every 3-4 songs, the LD should pull back. Constant high energy is monotonous.

"Does the show feel like one cohesive work or a series of disconnected songs?"
  → Color palette consistency, rig identity, recurring visual themes.
```

## The Critique Vocabulary

Critiquing a look requires specific language. Vague feedback ("it doesn't feel right") is useless for iteration. Good critique is specific and actionable:

| Vague Critique | Specific, Actionable Critique |
|---------------|------------------------------|
| "It's too bright" | "Spots dimmer is 10% too hot. Pull to 70%." |
| "The color is wrong" | "The amber is reading yellow on these LEDs. Try Rosco 02 instead of R17." |
| "It's boring" | "No movement. Add a slow sine chase on the backlight at 20% size." |
| "It doesn't pop" | "No contrast with the previous look. Change backlight from blue to a complementary color." |
| "The timing is off" | "Fade is too slow for this BPM. Change from 4s to 1 bar (1.5s at 160 BPM)." |

## The Critique Hierarchy

When multiple things are wrong, fix in this order:

1. **Visibility** — Can the audience see what they need to see? If not, nothing else matters.
2. **Timing** — Does the change land on the right beat? If not, the perfect look at the wrong time is a mistake.
3. **Position** — Are fixtures pointing where they should? Wrong position undermines everything else.
4. **Intensity** — Is the brightness right? Too bright is as bad as too dim.
5. **Color** — Is the palette working? Color is the last thing to tweak because it's the most subjective.

## Implications for RayFlow

1. **The loop is the product.** RayFlow's value is accelerating the Author → See → Critique → Refine loop. Every feature should be measured against this: does it make the loop faster, easier, or more informative?

2. **Fast visualization is critical.** The Author → See step must be fast. Sub-5-second latency from cue authoring to DMX evidence or pre-viz output. If the loop is too slow, the LD will stop iterating and settle for "good enough."

3. **Critique assistance.** RayFlow's AI should provide specific, actionable critique:
   - "Cue 12 is 20% dimmer than Cue 8 in the same section — this may feel like an unintended drop."
   - "The color palette for the bridge section is the same as the chorus. Consider adding contrast."
   - "No fixture in this rig supports gobo. Cue 14 requests a gobo preset that cannot render."

4. **Micro → Macro → Show-level views.** The UI/CLI should support all three critique levels:
   - Micro: per-cue rendering and DMX evidence
   - Macro: per-section energy arc, color arc, contrast arc
   - Show: full-set pacing, consistency, journey

5. **Iteration history.** Track the Author → Refine chain. The `show diff` command should show the evolution of a cue through its refinement history, not just the before/after. This captures design intent for future AI learning.

6. **The first render is never right.** The authoring system should assume the first version of any cue will be iterated. Don't optimize for perfect first-pass generation — optimize for fast iteration. Generate "good enough to critique" cues, then support rapid refinement.
