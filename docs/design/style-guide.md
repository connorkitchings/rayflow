# Personal Style Guide: 4 Moving Heads + 8 LED Washes

A beginner's rule set for a small rig. A moving head is a fixture that can pan, tilt and project a beam, gobo (a pattern stencil) or color. An LED wash is a fixture that floods an area with soft colored light. A "look" is one saved arrangement of what every fixture is doing at a moment. A "cue" is one stored step that recalls a look.

Citations read `(LD surname, profile file, [n])`: open that file in `docs/research/concert-lds/` and find source [n] in its Sources list. Rules marked `[house rule]` are design decisions for this project, not facts about any designer.

## 1. Palette families

1. Pick one base color per song and build from it; keep that color as the starting wash. (Goedde, `06-andrew-goedde.md`, [1])
2. Pair colors that complement each other (sit opposite on the color wheel, such as blue and amber), rather than using one color everywhere. (Kuroda, `02-chris-kuroda.md`, [8])
3. Put opposite colors on opposite sides: for example UV or deep blue on one side and pink on the other, instead of the stock red/blue/amber/green wash. (Brightman, `01-candace-brightman.md`, [1])
4. Use two-tone looks: split the washes so half show one color and half another. (Waful, `04-jefferson-waful.md`, [1])
5. Allow "dirty" colors (slightly muddy or layered, not pure primaries) to widen the palette. (Kuroda, `02-chris-kuroda.md`, [2])
6. For Widespread Panic material, the default is a warm base (amber, gold, warm white) against lavender and blue. This is the owner's stated preference, not a sourced fact: Hoffman's profile explicitly found no source for a warm palette (`03-paul-hoffman.md`, Unverified or removed). `[stated preference]`
7. Limit a look to one or two colors, and save a third for a peak. `[house rule]`

## 2. Contrast and dynamics

1. Plan dark, mysterious moments against full-rig moments; the contrast is the drama. (Waller, `05-saxton-waller.md`, [3])
2. Build across the night instead of starting big: Brightman had the crowd fully in about two-thirds of the way through. (Brightman, `01-candace-brightman.md`, [1])
3. A hard color swing on a slow song can land well, for example deep red to icy cool. (Brightman, `01-candace-brightman.md`, [1])
4. Light the band from behind for silhouettes and color washes. (Hoffman, `03-paul-hoffman.md`, [2])
5. Use stationary lights for texture while others move. (Kuroda, `02-chris-kuroda.md`, [1])
6. Skip blinders (bright lights aimed at the audience). (Kuroda, `02-chris-kuroda.md`, [1])
7. Avoid "busy" or "flashy" looks; the audience should feel the music more than notice the rig. (Waful, `04-jefferson-waful.md`, [2])
8. Keep two anchor looks: a "mystery" look (one or two heads, low intensity) and a "full" look (everything on). `[house rule]`

## 3. Movement restraint

1. Leave heads lit while they move to a new position, so the audience sees the light travel instead of snapping. (Brightman, `01-candace-brightman.md`, [2])
2. Make sweeps slow and deliberate, including slow sweeps over the audience. (Brightman, `01-candace-brightman.md`, [2])
3. Treat slow movement during a big moment like slow motion in video. (Waful, `04-jefferson-waful.md`, [1])
4. Save the large audience sweeps for choruses. (Kuroda, `02-chris-kuroda.md`, [8])
5. Keep fixtures mirrored left and right so looks read as balanced. (Waful, `04-jefferson-waful.md`, [1]; Kuroda, `02-chris-kuroda.md`, [1]) Brightman did the opposite with asymmetrical rigs (`01-candace-brightman.md`, [1]), so symmetry is a choice, not a law.
6. Move one or two heads at a time and leave the others still. `[house rule]`

## 4. Section-to-look mapping

The sections are the ones Goedde cues in his show file: verse, chorus, bridge and solos. (Goedde, `06-andrew-goedde.md`, [3]) The look choices in the table are built from the rules above; the last column says what is sourced and what is a `[house rule]`.

| Section | Look | Basis |
|---|---|---|
| Intro | Song's base color, low intensity, heads still | Base color per song (Goedde, `06-andrew-goedde.md`, [1]); build across the night (Brightman, `01-candace-brightman.md`, [1]). The low-intensity choice is a `[house rule]`. |
| Verse | Base color on washes, one or two heads in a slow, quiet position | Restraint (Waful, `04-jefferson-waful.md`, [2]); slow movement (Brightman, `01-candace-brightman.md`, [2]) |
| Chorus | Add the complementary color; two heads sweep slowly over the audience | (Kuroda, `02-chris-kuroda.md`, [8]) |
| Bridge | Change the color relationship (for example a color swing) and keep heads mostly still | Color swing (Brightman, `01-candace-brightman.md`, [1]); stillness as texture (Kuroda, `02-chris-kuroda.md`, [1]). Using them on bridges is a `[house rule]`. |
| Peak or solo | Full look, all fixtures on, the most contrast of the night | Contrast and full-rig energy (Waller, `05-saxton-waller.md`, [3]); placing the full look on solos is a `[house rule]`. |
| Outro | Return to the base color and fade the heads down slowly | `[house rule]` |

## 5. How an AI designer should use this

1. Treat sections 1 to 3 as defaults; prefer a cited rule over a house rule when they conflict.
2. When explaining a choice to the user, name the designer and file from the citation; never credit a designer for a `[house rule]` or `[stated preference]`.
3. Ask which band or song the user is lighting before choosing a palette; apply the warm-base preference only to Widespread Panic material.
4. Keep suggestions within 4 heads and 8 washes, and do not state how any particular console or software behaves; check the project's MA3 docs for that.
5. If a rule here conflicts with what the user hears in the music, the music wins: "Learn the music" is Waful's first principle (`04-jefferson-waful.md`, [2]).
