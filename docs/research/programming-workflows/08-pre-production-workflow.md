# Pre-Production Workflow: Concept to Curtain

**Source:** Web research, professional production workflows, touring practices
**Parsed:** 2026-05-25

## The Production Timeline

Lighting design is not a single act of creativity — it is a phased process spanning weeks to months. Each phase has distinct goals, artifacts, and stakeholders. Understanding the timeline reveals where AI-assisted design can inject value.

## Phase 1: Advance Work (Weeks Before)

**Goal:** Understand the show, the venue, and the constraints before any creative work begins.

### Activities
- Receive the tech rider, stage plot, and input list from the artist/tour.
- Review venue tech specs: stage dimensions, trim heights, power availability, house rig inventory.
- Confirm console and protocol compatibility with the house system.
- Identify gaps: does the house have enough fixtures, or is a rental package needed?

### Artifacts
- Venue tech spec summary
- Initial fixture inventory
- Power and network plan (rough)

### RayFlow Role
- Load venue dimensions and house patch into a `Venue` model.
- Validate that the planned rig fits within venue constraints (throw distances, power budget, universe capacity).
- Flag fixture/console incompatibilities before travel.

## Phase 2: Concept and Plot (1–4 Weeks Before)

**Goal:** Design the visual world of the show.

### Activities
- The LD develops a visual concept: color palette, mood references, key looks.
- Discuss with artist/creative director: what does the show feel like?
- Draft the light plot: fixture positions, types, counts, DMX addressing.
- Select fixtures: GDTF profiles checked, rental availability confirmed.
- Create palette/preset strategy for the show.

### Artifacts
- Light plot (Vectorworks, WYSIWYG, or hand draft)
- Instrument schedule (every fixture, its position, type, address, channel)
- Channel hookup (console channel → DMX address mapping)
- Color palette reference (gel colors or RGB values for each look)
- Magic sheet / layout design (operator interface)

### RayFlow Role
- Generate initial rig from a template matching the venue type and performance type.
- Auto-populate fixture positions based on zone coverage calculations.
- Suggest color palettes based on vibe/mood keywords.
- Generate initial preset library (position, color, beam, gobo).
- Export the rig as MVR for pre-viz import.

## Phase 3: Pre-Programming / Pre-Viz (1–2 Weeks Before)

**Goal:** Program the show offline before any fixture is hung.

### Activities
- Build the show file: patch fixtures, create groups, build presets/palettes, program cue lists.
- Connect to pre-viz software (Capture, Vision, Depence²).
- Run through the entire show in pre-viz. The LD and programmer iterate on looks with zero labor cost.
- Timecode programming: if the show runs to timecode, this is when cues get sync'd frame-accurately.
- Generate paperwork: cue sheets, patch sheets, network diagrams.

### Artifacts
- Complete show file on console or console offline editor
- Pre-viz session file
- Cue sheets with timecode triggers
- Network configuration document

### RayFlow Role
- Generate initial cue list from song sections, vibe, and performance type.
- Author dimmer, color, and position cues per section.
- Render cues to DMX frames for verification.
- Export cue sheets (CSV), MVR (for pre-viz), and Timecode XML.
- The show file at this point is >80% complete before anyone steps into the venue.

## Phase 4: Load-In and Focus (Day 0–1)

**Goal:** Hang, cable, patch, and focus the physical rig.

### Activities
- Crew hangs fixtures at plotted positions.
- Electricians run power and data cables.
- Fixtures are patched to the console.
- Programmer loads the pre-programmed show file.
- Focus session: the LD calls focus notes while fixtures are pointed and sharpened. This is where the pre-viz fades away and the real look appears.

### Artifacts
- Hung and patched rig
- Updated patch sheet (as-built vs. as-designed)
- Focused fixtures

### RayFlow Role
- Generate focus sheets: which fixture, which preset, where it points, focus notes.
- Re-render cues against the as-built patch if addresses changed during load-in.
- Compare as-built universe layout against as-designed and flag address conflicts.

## Phase 5: Tech Rehearsal (Day 1–3)

**Goal:** Integrate lighting with all other production elements.

### Activities
- Cue-to-cue: run every cue in sequence, stop at each, refine timing and look.
- Integrate with audio, video, automation, and performers.
- The LD and programmer make hundreds of micro-adjustments: dimmer is 5% too hot, gobo is 2° out of focus, the blue wash needs 10% more saturation.
- Dry tech (no performers) → Full tech (with performers, stop-and-go) → Dress rehearsal (full run, no stops).

### Artifacts
- Polished show file with refined cues
- Updated cue sheets
- Operator notes (manual triggers, special sequences, emergency procedures)

### RayFlow Role
- Before tech: generate a change log comparing the pre-programmed show file to what was loaded into the venue console.
- During tech: not a real-time role. RayFlow is a pre-production tool, not an on-site console replacement.
- After tech: import the refined show file back into RayFlow's library, diff against the pre-production version, and capture the changes as lessons for future shows.

## Phase 6: Show and Strike

**Goal:** Execute the show and capture lessons.

### Activities
- Perform the show. The operator executes cues and handles any live adjustments.
- Strike: de-rig, pack, and load out. Typically faster than load-in since no focus is required.

### Artifacts
- Final show file (post-show, with any live adjustments baked in)
- Show report (issues, notes for next performance or next tour leg)

### RayFlow Role
- Archive the final show file in the library.
- Diff against the pre-production version and pre-vis version.
- Capture metadata: what changed, why, and what can be learned for future AI authoring.

## Where AI Fits in the Timeline

| Phase | AI Value | Current RayFlow Capability |
|-------|---------|---------------------------|
| Advance | Venue constraint validation | `Venue` model with dimensions |
| Concept & Plot | Rig generation, palette suggestion | Rig templates, presets |
| Pre-Programming | Cue generation, render verification | `plan-cues`, `render-cue`, `workflow-report` |
| Load-In & Focus | Focus sheets, address conflict detection | MVR export, patch export |
| Tech | Change tracking, version comparison | `show diff` |
| Show & Strike | Show archiving, lesson capture | `show save/versions` |

## Implications for RayFlow

1. **Phase-aware commands:** CLI commands could be organized by production phase: `rayflow advance check`, `rayflow design generate-rig`, `rayflow program generate-cues`, `rayflow tech diff-show`.
2. **Template progression:** Each phase produces templates that feed the next. Advance prep produces a venue model → design produces a rig → programming produces cues → tech refines everything.
3. **Change capture:** The `show diff` command should be enhanced to produce human-readable change summaries ("Cue 12 dimmer changed from 80% to 75%") suitable for the LD's notes.
4. **Offline-first design:** RayFlow's value is highest in Phases 2–3 when there's no physical venue access. The goal should be: arrive at load-in with a show that's 80% programmed.
