# Fixtures guide: what the lights are and what the pros hang

This guide explains the kinds of lighting fixtures, lists the fixtures that the six sourced lighting designers (LDs) actually used, and says which of them exist in the onPC 2.5 fixture library. It ends with the choice for the starter rig and the real fixtures to graduate to in Module 2.

The starter rig itself (4 moving heads and 8 LED washes, with patch addresses) lives in `docs/learn/starter-rig.md`. Terms such as "attribute" and "patch" are in `docs/learn/glossary.md`.

## 1. Fixture families in plain words

The depth lives in two research files. This section is the short version.
- `docs/research/design-concepts/21-fixture-selection-and-rig-building.md`: how designers choose fixtures and build a rig.
- `docs/research/protocols-and-systems/02-fixture-types-and-capabilities.md`: what each fixture type can do in DMX terms.

| Family | What the audience's eye sees | How it makes color | Key attributes | Typical hang positions |
|---|---|---|---|---|
| Spot / profile | A sharp-edged, bright pool or beam of light that can carry patterns and be shaped. The "texture" light. | CMY mixing (cyan, magenta, yellow flags) plus a color wheel, or an LED engine | Gobo wheels (patterns), zoom, iris, prism, framing shutters, focus | Front-of-house (FOH) truss and downstage truss for key light; upstage truss and floor for gobo texture on the back wall |
| Wash | A soft, wide, even field of color with a blurry edge. The "paint" light. | CMY mixing, or an RGBW LED engine (most modern washes) | Zoom, frost, sometimes pixel cells inside the lens | Downstage and mid truss for color on the band; upstage truss and booms for backlight and side light |
| Beam | A thin, hard, very bright shaft of light, best seen in haze. The "aerial effect" light. | Fixed color wheel (a handful of slots), no mixing | Prism, tight fixed beam, sometimes zoom; usually no shutters or gobo shaping | Mid and upstage truss, floor behind the band, pointing out over the audience |
| Hybrid | One fixture that behaves like a beam, a spot and sometimes a wash by switching modes. | Color wheel, CMY or LED, depending on the model | Gobos, prism, a narrow beam and a wider beam in one lens | Wherever a designer wants one fixture to do several jobs, often mid truss |
| LED bar / pixel | A line of color you can chase, wipe or split across its length, or a panel of pixels showing a pattern. | RGBW or RGB LED cells, each cell (pixel) controlled separately | Cell count, tilt (for moving batten types), zoom on some models | Floor in front of or behind the band, mid and upstage truss, booms |
| Strobe / blinder | A flash or a hard, warm or white blast aimed at the audience or the stage. | White or warm LED, sometimes RGB, sometimes pixel-mappable | Intensity, strobe rate, sometimes pixel cells | Floor facing the audience or band, front truss, or in rows on trusses |

Notes that apply across families:
- "Moving head" means the fixture pans and tilts (turns and nods) on a yoke. Spots, washes, beams and hybrids are usually moving heads. Bars and blinders are usually fixed, although some bars (the Robe Tetra2 for example) tilt.
- An LED fixture mixes color by turning red, green, blue and white emitters up and down. A lamp fixture (an arc lamp behind a CMY system or color wheel) mixes by sliding colored flags in front of white light.
- Hang position follows job: key light comes from the front, backlight from behind, texture lands on walls and scenery, and aerial beams fill the air.

## 2. LD fixture census

Every fixture below appears in a rig the profiled LDs used, taken from `docs/research/rig-breakdowns/` and the profiles in `docs/research/concert-lds/`. In the source column, `profile [n]` means the numbered LD profile file and a bracket such as `[3]` points to the source list inside that profile. A web-sourced row carries its URL. Rows marked "est." come from breakdown files that rate their own fixture identification as medium or low confidence; treat them as "likely".

Profile numbers: `01-candace-brightman.md` (Brightman), `02-chris-kuroda.md` (Kuroda), `03-paul-hoffman.md` (Hoffman), `04-jefferson-waful.md` (Waful), `05-saxton-waller.md` (Waller), `06-andrew-goedde.md` (Goedde).

Umphrey's McGee (UM) note: Jefferson Waful was UM's LD until August 2019, and Ben Factor is the LD after him (`docs/research/concert-lds/07-ben-factor.md`). The Iceland 2022 rig is therefore **Ben Factor era**, not a Waful rig, even though `docs/research/rig-breakdowns/02-um-iceland-2022.md` is written under Waful's name and rates its fixture list as low confidence. Its rows are marked "est." and labeled Ben Factor era here.

| Fixture model | Family | LD / tour | Year | Source | Library check |
|---|---|---|---|---|---|
| Panaspot | Spot (early moving light) | Brightman / Grateful Dead | 1980s, exact year not given | `profile [1]` (Relix [1]); web: https://relix.com/articles/detail/move-me-brightly-grateful-dead-lighting-director-candace-brightman/ | not found |
| Vari-Lite VL3000 Spot | Spot | Brightman / Fare Thee Well | 2015 | `profile [1]` (PLSN [3]) | `vari_lite@vl3000 spot.pxml` |
| Vari-Lite VL3500 Wash | Wash | Brightman / Fare Thee Well | 2015 | `profile [1]` (PLSN [3]) | `vari_lite@vl3500 wash.pxml` |
| Robe BMFL Spot | Spot | Brightman / Fare Thee Well; Hoffman / Widespread Panic Halloween | 2015; 2019 | `profile [1]`; `04-widespread-panic-verified.md` | `robe@robin bmfl spot.pxml` |
| Martin MAC Viper Profile | Spot | Brightman / Fare Thee Well; Kuroda / Phish; Waful / UM; Hoffman / Widespread Panic | 2015 (Fare Thee Well, Phish, Widespread Panic); 2013 to 2018 (UM) | `profile [1]`; `01-phish-2015.md` (est.); `03-um-early-waful-2009-2014.md` and `profile [4]`; `profile [3]` | `martin@mac viper profile.pxml` |
| Martin MAC III Profile | Spot | Waful / UM | 2009 to 2018 | `03-um-early-waful-2009-2014.md`; `profile [4]` | `martin@mac iii profile.pxml` |
| Martin MAC 2000 Profile | Spot | Waful / UM | 2009 to 2010 | `03-um-early-waful-2009-2014.md` | `martin@mac 2000 profile.pxml` |
| Varyscan P2 250 | Spot | Waful / UM Mantis tour | 2009 to 2010 | `03-um-early-waful-2009-2014.md` | not found |
| Vari-Lite VL3500 (spot or wash, model not named) | Spot / wash | Kuroda / Phish | 2015 | `01-phish-2015.md` (est.) | `vari_lite@vl3500 spot.pxml`, `vari_lite@vl3500 wash.pxml` |
| Vari-Lite VLM | Wash (1990s, still in use) | Hoffman / Widespread Panic | 2015 | `profile [3]` (PLSN [3], LSI [4]) | `vari_lite@vlm.pxml` |
| Vari-Lite VL500 | Wash | Hoffman / Widespread Panic Halloween | 2019 | `04-widespread-panic-verified.md` | `vari_lite@vl500.pxml` |
| Martin MAC Aura | Wash | Kuroda / Phish; Billy Strings (est.) | 2015; 2025 to 2026 | `01-phish-2015.md` (est.); `06-billy-strings-2025-2026.md` (est.) | `martin@mac aura.pxml` |
| Martin MAC Quantum Wash | Wash | Waful / UM | 2018 | `profile [4]` (PLSN [1]) | `martin@mac quantum wash.pxml` |
| GLP Impression X4 | Wash (pixel-mappable LED) | Kuroda / Phish (est.); Hoffman / Widespread Panic | 2015; 2016 | `01-phish-2015.md` (est.); `profile [3]` (LSI [5]) | `glp@impression x4.pxml` |
| GLP Impression X4S | Wash (compact LED) | Hoffman / Widespread Panic | 2015; 2019 | `profile [3]` (PLSN [3]); `04-widespread-panic-verified.md` | `glp@impression x4s.pxml` |
| Robe Spiider | Wash (LED) | Kuroda / Phish; Trey Anastasio Band (TAB) in the TAB-Goose tour | 2022 | `profile [2]` (LSI [4]); `05-goose-2022.md` | `robe@robin spiider.pxml` |
| Chauvet Rogue R2 Wash | Wash | Goedde / early Goose; Ben Factor era UM (est.) | about 2019; 2022 | `05-goose-2022.md`; `02-um-iceland-2022.md` (est.) | `chauvet@rogue r2 wash.pxml` |
| Chauvet Rogue R1 Spot | Spot | Goedde / early Goose | about 2019 | `05-goose-2022.md` | `chauvet@rogue r1 spot.pxml` |
| Chauvet Rogue R2 Spot | Spot | Ben Factor era UM, Iceland (est.) | 2022 | `02-um-iceland-2022.md` (est.) | `chauvet@rogue r2 spot.pxml` |
| Chauvet Rogue RH1 Hybrid | Hybrid | Goedde / early Goose | about 2019 | `05-goose-2022.md` | `chauvet@rogue rh1 hybrid.pxml` |
| Ayrton Domino | Spot / profile (LED) | Hoffman / Widespread Panic MEMPHO | 2021 | `profile [3]` (Ayrton [2]); `04-widespread-panic-verified.md` | `ayrton@domino lt.pxml`, `ayrton@domino s.pxml`, `ayrton@domino tc.pxml` (a plain "Domino" is not listed; these are variants) |
| Ayrton Mistral | Spot (LED) | Hoffman / Pulse Lighting owned stock | 2021 | `profile [3]` | `ayrton@mistral.pxml` |
| Ayrton Ghibli | Wash (LED) | Hoffman / Pulse Lighting owned stock | 2021 | `profile [3]` | `ayrton@ghibli.pxml` |
| Robe MegaPointe | Hybrid (beam, spot) | Waller / Billy Strings; Goedde / Goose Goosemas | 2025; 2023 | `profile [5]` (TPi [3]); web: https://robe.cz/news/all-you-need-for-goosemas-is-robe | `robe@robin mega_pointe.pxml` |
| Robe Pointe | Hybrid (beam, spot) | Hoffman / Widespread Panic | 2015 | `profile [3]` (PLSN [3]) | `robe@robin pointe.pxml` |
| Robe iFORTE | Spot (LED, long throw) | Waller / Billy Strings | 2025 | `profile [5]` (TPi [3]) | `robe@robin i_forte fs.pxml` (closest; exact iFORTE variant unverified) |
| Robe FORTE | Spot (LED, long throw) | Goedde / Goose; TAB-Goose tour | 2022; 2023 | `profile [6]` (PLSN [1]); `05-goose-2022.md` | not found (only `robe@robin forte hp.pxml` and Fresnel/PC variants) |
| Robe Tarrantula | Hybrid / effect | Goedde / Goose | 2022; 2023 | `05-goose-2022.md`; web: https://robe.cz/news/all-you-need-for-goosemas-is-robe | `robe@robin tarrantula.pxml` |
| Robe Spikie | Beam (LED) | TAB / TAB-Goose tour | 2022 | `05-goose-2022.md` | `robe@robin spikie.pxml` |
| Robe LEDBeam 350 | Wash / beam (small LED) | Goedde / Goose Goosemas | 2023 | web: https://robe.cz/news/all-you-need-for-goosemas-is-robe | `robe@robin ledbeam 350.pxml` |
| Clay Paky Sharpy | Beam | Kuroda / Phish (est.); Hoffman / Widespread Panic (replaced by Pointe) | 2015 | `01-phish-2015.md` (est.); `profile [3]` | `clay paky@sharpy.pxml` |
| Clay Paky B-Eye K20 | LED wash / effect | Waful / UM | 2018 | `profile [4]` (PLSN [1]) | `clay paky@a leda b-eye k20.pxml` |
| Elation Platinum Beam 5R | Beam | Ben Factor era UM, Iceland (est.) | 2022 | `02-um-iceland-2022.md` (est., "or similar") | `elation@platinum beam 5r.pxml` |
| GLP Impression X4 Bar 20 | LED bar / pixel | Kuroda / Phish (est.); Hoffman / Widespread Panic | 2015; 2019 | `01-phish-2015.md` (est.); `04-widespread-panic-verified.md` | `glp@impression x4 bar 20.pxml` |
| Robe Tetra2 | LED bar / pixel (tilting) | Kuroda / Phish; Goedde / Goose | 2022 | `profile [2]` (LSI [4]); `profile [6]` (TPi [2]) | not found |
| Martin VDO Sceptron | LED bar / pixel batten | Hoffman / Widespread Panic Halloween | 2019 | `04-widespread-panic-verified.md` | `martin@vdo sceptron 20 1000.pxml` (one of several lengths listed) |
| Elation SixBar | LED bar | Kuroda / Phish | 2015 | `01-phish-2015.md` (est., "or similar") | not found |
| Bandit 5x5 | LED panel / matrix | Hoffman / Widespread Panic | 2016 | `profile [3]` (LSI [5]) | `bandit lites@matrix 5x5.pxml` (likely the same product; unconfirmed) |
| Martin Atomic 3000 | Strobe | Kuroda / Phish (est.); Waful / UM | 2009 to 2015 | `01-phish-2015.md` (est.); `03-um-early-waful-2009-2014.md` | `martin@atomic 3000.pxml`, `martin@atomic 3000 led.pxml` |
| Chauvet Color STRIKE M | Strobe / blinder (pixel-mappable) | Goedde / Goose | 2022 | `profile [6]` (LSI [3]); `05-goose-2022.md` | `chauvet@color strike m.pxml` |
| Chauvet STRIKE 4 | Strobe / blinder | Goedde / early Goose | about 2019 | `05-goose-2022.md` | `chauvet@strike 4.pxml` |
| Molefay-style 4-lite blinder | Blinder | Kuroda / Phish | 2015 | `01-phish-2015.md` (est., "or similar") | not found |

### Census gaps

- **Brightman, Vari-Lite era (1980s to 1990s):** The only moving light named in the sources is the Panaspot, with no year. The web pass found no Dead tour fixture list for those years: the Relix article names only "Panaspots", and the Live Design gear-list page (https://www.livedesignonline.com/concerts/grateful-dead-lighting-plots-and-gear-list) returned HTTP 403, so it was not read. The first sourced Vari-Lite fixtures for Brightman are the 2015 Fare Thee Well VL3000 and VL3500.
- **Billy Strings 2025:** Covered by `profile [5]` (iFORTE and MegaPointe, sourced). The other fixtures in `docs/research/rig-breakdowns/06-billy-strings-2025-2026.md` (such as MAC Aura) are that file's own low-confidence guesses and are marked est.
- **Goose today:** The web pass found no published fixture list for 2025 beyond the 2022 and Goosemas 2023 rigs above. Treat the Goose rows as 2022 and 2023 facts, not a current rig.
- **UM Iceland 2022:** Fixtures are the breakdown file's low-confidence estimates, now labeled Ben Factor era.
- **Fixtures with no library match:** Panaspot, Varyscan P2 250, FORTE, Tetra2, SixBar, Molefay-style blinder.

## 3. Library check: commands and notes

The library root is `~/MALightingTechnology/gma3_2.5.1/shared/lib_fixture_types/` (onPC 2.5.1). File names are `manufacturer@model`. The file contents are encrypted, so this check proves only that a file with that name exists, not what channels or modes it has.

The library holds two kinds of files:
- `grandma3/` holds 172 files. Apart from `generic@moving_head.xml`, `generic@grouping.xml`, `ayrton@alienpix-rs.xml` and two `ma lighting@` helper types, they are set-piece objects (truss, platforms, letters). No real LD fixture lives here.
- `grandma2/` holds 11,536 `.pxml` files, including every real fixture in the census. In the table above, "library check" lists a `grandma2/` file name.

Commands (each prints the matching file names, which are the values in the census):

```
LIB=~/MALightingTechnology/gma3_2.5.1/shared/lib_fixture_types

# one query per manufacturer group, case-insensitive
ls $LIB/grandma2 | grep -i -E '^martin@mac (iii profile|2000 profile|viper profile|aura\.|quantum wash)'
ls $LIB/grandma2 | grep -i -E '^glp@impression x4( bar 20|s)?\.'
ls $LIB/grandma2 | grep -i -E '^robe@robin (bmfl spot|i_forte|forte|mega_pointe|pointe|tarrantula|spiider|spikie|ledbeam 350)'
ls $LIB/grandma2 | grep -i -E '^chauvet@(rogue r[12] (spot|wash)|rogue rh1|strike 4|color strike m)'
ls $LIB/grandma2 | grep -i -E '^ayrton@(domino|mistral|ghibli)'
ls $LIB/grandma2 | grep -i -E '^vari_lite@(vl3000 spot|vl3500 (spot|wash)\.|vl500\.|vlm)'
ls $LIB/grandma2 | grep -i -E '^(clay paky@(sharpy\.|a leda b-eye k20\.)|elation@platinum beam 5r\.|martin@(atomic 3000|vdo sceptron 20 1000)|bandit lites@matrix)'

# "not found" checks: none of these has a file for the named model
ls $LIB/grandma2 | grep -i -E 'varyscan p2|panaspot|sixbar|molefay|tetra2|tetrax|^robe@robin forte\.pxml'

# generic fixtures used by the starter rig
ls $LIB/grandma3 | grep -i 'moving_head'
ls $LIB/grandma2 | grep -i '^generic@led - irgbw'
```

Caveats:
- A name match is not an exact variant match. Models such as the Domino, iFORTE, FORTE and Sceptron ship in several variants, so the census lists the closest file name. Check the exact variant in the Patch window before relying on it.
- "not found" for the Robe Tetra2 is by file name. The library holds `venue lighting effects@tetra *` types, which are a different product.
- The library is the one shipped with onPC 2.5.1. A newer library may add fixtures.

## 4. Starter choice and where to graduate

**Starter rig: generic fixtures only.** The stage is 4 spots and 8 washes:
- The 4 spots use Generic `Moving Head` (`grandma3/generic@moving_head.xml`). It mixes color with RGB and has zoom, iris and a color wheel, so it behaves like a simple spot.
- The 8 washes use the Generic LED wash `LED - IRGBW` (`grandma2/generic@led - irgbw.pxml`). It is intensity plus red, green, blue and white, the same color method as most modern wash fixtures.

Why generic first: the starter rig teaches console skills (groups, presets, cues) with the fewest moving parts. Generic types have no gobos, prisms or special modes to learn. Details, modes and addresses are in `docs/learn/starter-rig.md`.

**Real fixtures come in Module 2.** Nothing in Module 1 uses the fixtures below. When Module 2 starts, repatch one role at a time to these, one change per step.

| Role | Graduate-to pick | Exact library file | Why |
|---|---|---|---|
| Spot (replaces the 4 generic moving heads) | Martin MAC Viper Profile | `martin@mac viper profile.pxml` | It appears in the most rigs in the census (Brightman, Kuroda, Waful and Hoffman), and it is a classic gobo-and-color profile |
| Wash (replaces the 8 generic LED washes) | GLP Impression X4 | `glp@impression x4.pxml` | It appears in the Phish and Widespread Panic rigs, and it is an RGBW LED wash like the generic one, so the move from generic is small |

Runner-up spot: `robe@robin bmfl spot.pxml` (Robe BMFL Spot) appears in two rigs (Fare Thee Well 2015 and Widespread Panic 2019). It is a good alternative if the MAC Viper mode names are confusing in the Patch window.
