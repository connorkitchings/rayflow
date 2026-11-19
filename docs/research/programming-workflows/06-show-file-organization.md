# Show File Organization and Version Control

**Source:** Web research, professional touring workflows, console best practices
**Parsed:** 2026-05-25

## The Show File as a Living Document

A show file is not static — it evolves through pre-production, rehearsals, venue calibration, and multiple performances. Poor organization makes evolution painful. Good organization makes the show file resilient to change, understandable by other programmers, and recoverable from failure.

## Naming Conventions

### Cue Naming

A consistent cue naming convention makes hundreds of cues navigable:

```
Format: {SequenceNumber}_{Section}_{Purpose}
Examples:
  01_Intro_Wash
  03_Verse1_Backlight
  07_Chorus1_Ballyhoo
  12_Bridge_DeepBlue
  15_Outro_FadeOut
```

Alternative for timecode shows:
```
Format: {Timecode}_{Section}_{Look}
Examples:
  00:00:30_Intro_DimUp
  00:01:02_Verse1_Front
  00:01:47_Chorus_HighEnergy
```

### Sequence Naming
```
Format: {ShowArea}_{FixtureGroup}_{Purpose}
Examples:
  Show_Spots_Base
  Show_Washes_Color
  Show_Beams_Aerial
  Busk_Strobes
  Key_Speaker_Front
```

### Palette Naming
```
Format: {Attribute}_{Name}_{Variant or Index}
Examples:
  Color_Red
  Color_DeepBlue
  Position_LeadSinger
  Position_AudienceLeft
  Beam_Gobo_Breakup
  Beam_Zoom_Narrow
```

### Fixture Labeling
```
Format: {Type}_{Location}_{Number}
Examples:
  Spot_FOH_1, Spot_FOH_2
  Wash_MidTruss_1, Wash_MidTruss_2
  Beam_USTruss_1 (Upstage Truss)
  Blinder_Floor_1
  PAR_BoomSL_1 (Stage Left Boom)
```

## File Hierarchy for Touring Shows

```
MyShow/
├── MyShow_v3.2_MAIN.show.gz           (current production file)
├── Archive/
│   ├── MyShow_v3.1.show.gz
│   ├── MyShow_v3.0_Rehearsal.show.gz
│   ├── MyShow_v2.5_PreTour.show.gz
│   └── MyShow_v1.0_Bare.show.gz
├── HouseFiles/
│   ├── VenueA_HousePatch.xml
│   ├── VenueB_HousePatch.xml
│   └── VenueC_HousePatch.xml
├── Exports/
│   ├── MyShow_2026-05-25_MVR.zip
│   ├── MyShow_2026-05-25_Timecode.xml
│   └── MyShow_2026-05-25_CueSheet.pdf
├── Fixtures/
│   └── Custom_FixtureProfiles/
│       └── MyCompany@MyCustomFixture.gdtf
└── README.txt
```

## Version Control Strategy

### Incremental Saves
- Save a new version after every significant programming session.
- Use semantic-ish versioning: `ShowName_v{major}.{minor}_{Purpose}`
  - Major: show-stopping changes (new act, fixture swap, complete re-patch)
  - Minor: cue additions/edits, palette updates, timing adjustments
  - Purpose: `_Rehearsal`, `_ShowReady`, `_Backup`

### Rollback Policy
- Keep the last 3 production versions immediately accessible.
- Never delete the "bare" file — the baseline show with only the patch and basic palettes, no cues. This is the emergency rebuild point.
- Before any destructive edit (re-patch, delete large cue ranges), save a version with `_PRE_{change}` suffix.

### Merge and Import Workflows

**Tour arrival at new venue:**
1. Load the house patch file (venue's DMX addressing and fixture inventory).
2. Import the tour show file.
3. Merge: house patch + tour cues. Cues reference palettes; palettes reference fixture types; the console resolves per-fixture DMX values from the merged patch.
4. Run a full cue list offline to verify all fixtures respond.
5. Save as `ShowName_v{major}.{minor}_{VenueName}.show.gz`.

## Cue Sheet Documentation

A printed/digital cue sheet is essential for operator handoff:

| Cue | Timecode | Section | Description | Fade | Follow | Notes |
|-----|----------|---------|-------------|------|--------|-------|
| 1 | 00:00:00.00 | Intro | Full blackout | 0s | Manual | Wait for house lights down |
| 2 | 00:00:05.00 | Intro | Dim wash up, warm | 3s | 4s | Soft intro bloom |
| 3 | 00:00:09.00 | Intro | Add backlight, cool | 2s | Manual | Hold for first verse |
| 4 | Verse 1 | Warm front, back off | 1s | Manual | GO on vocal start |

## Network and Universe Documentation

Every touring file should include a network map:

| Universe | Protocol | IP Range / Subnet | Fixture Types | Address Range |
|----------|----------|-------------------|---------------|---------------|
| 1 | Art-Net (0) | 10.0.1.0/24 | Dimmers, House Lights | 1–200 |
| 2 | Art-Net (1) | 10.0.1.0/24 | Front Spots (×8) | 1–192 |
| 3 | Art-Net (2) | 10.0.1.0/24 | Mid Truss Washes (×12) | 1–240 |
| 4 | sACN (3) | 10.0.2.0/24 | LED Pixel Bars (×4) | 1–320 |

## Backup and Redundancy

### The 3-2-1 Rule
- **3 copies** of the show file
- **2 different media** (console SSD + USB stick)
- **1 off-site copy** (cloud storage, tour manager's laptop)

### Pre-Show Checklist
- [ ] Current show file loaded on primary AND backup console
- [ ] USB stick with show file taped inside the console road case
- [ ] Cloud copy uploaded within last 24 hours
- [ ] Printed cue sheet at operator position
- [ ] Network diagram at FOH position for house tech reference

### Emergency Recovery
- If the primary console fails mid-show, the backup console takes over on the same network.
- The backup should be pre-loaded with the same show file and receive the same Art-Net/sACN feed.
- A basic "emergency look" (wash at 30%, front at 50%) should be stored on a physical fader as a failsafe.

## RayFlow Show Library vs. Console Show Files

RayFlow's show library (`show save/versions/restore/diff`) provides console-independent versioning:

| RayFlow Feature | Console Equivalent |
|----------------|-------------------|
| `show save` | Save As |
| `show versions` | Load Show (browse versions) |
| `show restore` | Load and overwrite current |
| `show diff` | No direct equivalent — powerful advantage |
| `show export` | Export MVR + CSV + Timecode XML as a bundle |

RayFlow's YAML-based show storage is human-readable and version-controllable in git, unlike binary console show files. A `show diff` between versions reveals exactly which cue values changed.

## Implications for RayFlow

1. **Naming convention enforcement:** The CLI and authoring system should validate cue, preset, and fixture labels against a configurable naming convention pattern.
2. **Auto-generated cue sheets:** The `show export` command should generate a human-readable cue sheet (CSV or PDF) alongside MVR and Timecode XML exports.
3. **Pre-push backup:** Before `show push-to-ma3`, RayFlow should auto-save the current show version to the library as a rollback point.
4. **Network map in rig model:** The `Rig` model should include a `network_map` field documenting universe-to-protocol-to-subnet mappings for export and documentation.
5. **Version diffing:** The existing `show diff` command is a foundation. Enhance it with palette reference diffing (which palettes changed between versions) and fixture coverage diffing.
