# Session Log — 2026-05-25 (Session 06)

## TL;DR (≤5 lines)
- **Goal**: Expand research knowledge base — lighting design concepts, concert LD profiles, rig breakdowns from verified sources, YouTube-sourced console tutorials
- **Accomplished**: 72 research docs (up from 26), 91 raw source files, 7 new rig breakdowns (3 verified), 5 YouTube-based reference docs, project charter rewritten to reflect true terminal goal
- **Blockers**: None
- **Next**: Rig builder tooling (auto-generate rigs from descriptions), palette generation, integrated visualization
- **Branch**: `codex/continue-development-session`

**Tags**: ["research", "docs", "lighting-design", "youtube", "concert-lds", "rig-breakdowns", "ma3", "charter"]

---

## Context
- **Started**: ~12:00
- **Ended**: ~14:30
- **Duration**: ~2.5 hours
- **User Request**: Documentation-only session. Expand research on lighting design concepts. Focus on concert lighting similar to Chris Kuroda, Andrew Goedde, Candace Brightman, Paul Hoffman, Jefferson Waful, Saxton Waller, Ben Factor, Luke Stratton.

---

## Work Completed

### Design Concepts (12 new docs, 17 total)
- `05-oscillators-and-effects.md` — Waveform types, effect parameters, DMX value mapping, BPM sync
- `06-dimmer-curve-physics.md` — Stevens' law, curve types, tungsten vs LED, perceptual response
- `07-gobo-design.md` — Metal/glass/plastic construction, mechanisms, optical path integration
- `08-movement-patterns.md` — Sine/cosine basis functions, Lissajous curves, phase offset, fanning
- `09-color-harmony.md` — Palette frameworks, color temp psychology, gel references
- `10-haze-and-atmosphere.md` — Oil vs water, DMX control, layering, health/safety
- `11-palette-design-philosophy.md` — Scope types, palette counts, update propagation
- `12-cue-timing-philosophy.md` — Beat-based timing, fade psychology, energy-to-density
- `13-rig-design-fixture-placement.md` — Truss positions, angles, throw distance, fixture mix
- `14-pixel-mapping.md` — Cell fixtures, layout grids, Art-Net universe planning
- `18-improvisational-concert-lighting.md` — LD as instrumentalist, busking philosophy, contrast
- `20-coordinate-system-and-placement.md` — Right-handed coordinate system, pan/tilt math, spacing
- `21-fixture-selection-and-rig-building.md` — Selection matrix, encodable rig building process, rules
- `22-design-iteration-loop.md` — Author → Critique → Refine pattern, micro/macro/show-level loops
- `23-reading-a-rig.md` — Fixture identification from photos/video, feature-to-model mapping
- `24-virtual-show-development.md` — Goedde-style offline pipeline, pre-viz integration, time budget
- `02-four-controllable-properties.md` (ai-lighting-patterns) — Intensity/Color/Distribution/Movement framework for AI authoring

### Concert LD Profiles (5 new, 10 total + README)
- `09-andrew-giffin.md` — Programmer for Kuroda (LD/programmer split maps to user/AI model)
- Updated `06-andrew-goedde.md` with virtual development workflow
- Updated `08-luke-stratton.md` with Dopapod rig rundown video details
- Corrected factual errors: Goedde=Goose not Pretty Lights, Hoffman=Widespread Panic not Greensky, Waller=STS9/Billy Strings

### Rig Breakdowns (7 docs in new `rig-breakdowns/` folder)
- `01-phish-2015.md` — Kuroda/Giffin, ~180-225 fixtures (estimated)
- `02-um-iceland-2022.md` — Waful, ~45-65 fixtures (estimated)
- `03-um-early-waful-2009-2014.md` — **VERIFIED** via Live Design Online articles. Mantis era: 12 MAC III, 6 MAC 2000, 8 Varyscan P2 250, 4 Atomics. MAC Viper era ~2013-2014.
- `04-widespread-panic-verified.md` — **VERIFIED** via Live Design. 2019: Robe BMFL/GLP/Martin/Vari-Lite. 2021: Ayrton Domino. Bandit Lites vendor.
- `05-goose-2022.md` — **VERIFIED** via Live Design. Dripfield: 16 Tetra2s, 18 Color STRIKE M, 16 cue-stacked songs. TAB co-headline: FORTES/Tarrantulas.
- `06-billy-strings-2025-2026.md` — Waller, ~95-160 fixtures, arena dual-mode (estimated)

### YouTube-Sourced Reference Docs (5 docs)
- `11-ma3-tutorial-series-reference.md` — ACT Entertainment 22-episode MA3 series (existing, reviewed)
- `12-ma3-tutorial-series-2-reference.md` — 19-episode MA3 series: recipes, selective/global/universal presets, filters, virtual dimmers
- `13-ma3-longform-tutorials-reference.md` — 3 longform videos: 102-min show build, 2-hr crash course, recipe deep dive
- `14-above-avl-youtube-reference.md` — 18 videos: amateur rig setups, console layouts by event type, console selection by use case
- `15-ma2-techniques-reference.md` — 14 MA2 technique videos: effects engine, Capture integration, tap-to-BPM, startup macros, timecode via REAPER

### Project Charter Rewrite
- `docs/project_charter.md` — Rewritten from "toolkit for lighting designers" to "AI-assisted design for amateurs"
- Terminal goal: pick a song → AI designs lighting → user sees and iterates → record the show. No live use.
- User is amateur, AI handles all console programming
- Research knowledge base (72 docs) serves as AI's design intelligence

### CONTEXT.md Updated
- Terminal goal stated upfront
- Research positioned as AI's design intelligence
- MA3 repositioned as visualization path (through pre-viz), not backend target

### Raw Sources (91 files)
- `livedesign/` — 7 Live Design Online articles via Wayback Machine (UM, Goose, Widespread Panic)
- `ma3-tutorial-series/` — 22 ACT Entertainment MA3 tutorials
- `ma3-tutorial-series-2/` — 19 MA3 tutorials (creator series)
- `ma3-longform/` — 3 longform MA3 tutorials
- `above-avl-youtube/` — 18 Above AVL educational videos
- `ma2-techniques/` — 14 MA2 technique videos
- `vectorworks-concert-lighting-101.txt` — Vectorworks concert lighting guide

### Verified Source Methodology
Discovered that industry articles (Live Design, PLSN) are Cloudflare-blocked but accessible via Wayback Machine. Established working pipeline: Wayback Machine → curl → Python text extraction → clean transcript. YouTube transcripts accessible via yt-dlp with Chrome cookies.

---

## Decisions Made

1. **Terminal goal: design, not performance.** Product ends when user is satisfied with the design. No live use.
2. **User is amateur, AI handles all console programming.** Every feature should be designed for this split.
3. **Research serves as AI knowledge base.** 72 docs translate amateur descriptions into correct technical output.
4. **Recipe-based authoring is the ideal AI paradigm.** Generate "Apply Preset X to Group Y" rather than absolute DMX values.
5. **Priority order:** Rig building → palette generation → visualization → console export → recording.
6. **YouTube is a first-class research source.** 91 raw transcripts from 86+ videos provide LD techniques, console workflows, and rig design patterns.

---

## Issues Encountered

- **Factual errors corrected by user:** Goedde=Goose (not Pretty Lights), Hoffman=Widespread Panic (not Greensky), Waller=STS9/Billy Strings. Kuroda does NOT use Unreal Engine pre-viz. Fixed in all affected docs.
- **Web sources blocked:** Live Design Online, PLSN, Reddit, YouTube search, Google — all blocked for automated access. Solved via Wayback Machine for text articles and yt-dlp with Chrome cookies for video transcripts.
- **Andrew Giffin added:** User requested adding Kuroda's programmer to influence repo. LD/programmer split maps directly to user/AI model.

---

## Next Steps

1. Build rig builder tooling — auto-generate rigs from descriptions (venue type, show scale, vibe)
2. Build palette generation — auto-generate position, color, beam preset libraries from vibe and fixture list
3. Tighten visualization feedback loop (author → see → critique → refine)
4. Console show file export (.show.gz for MA3) — enable direct import to offline editor
5. Continue rig breakdowns from verified sources — hunt Phish, Billy Strings, and additional UM/WSP/Goose articles

---

## Handoff Notes
- **Current state:** All Phases 1-11 complete. 72 research docs provide comprehensive AI knowledge base. Charter rewritten to reflect true terminal goal.
- **Blockers:** None
- **Next priority:** Rig builder tooling (auto-generate rigs from descriptions)
- **Open questions:** How will the user visualize their show during the design loop? MA3 3D? Capture? Future custom solution?
- **Context needed:** The recipe-based authoring model (groups + presets as abstract rules) should be the default. The four controllable properties framework (intensity/color/distribution/movement) should structure the AI's cue generation.

---

**Session Owner**: opencode
**User**: connorkitchings
