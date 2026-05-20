# Show Builder Prompt Template

Use this template when working with an AI coding tool to build or modify a lighting show in RayFlow.

## How to Use

1. Run `rayflow show context <show_name> --json` to get the full context bundle
2. Paste the JSON output into the `## Context` section below
3. Fill in your direction in the `## What I Want` section
4. Submit to the AI coding tool (opencode, Claude Code, Codex, etc.)

---

## Prompt

I'm working on a lighting show in RayFlow. Here's the context:

## Context

```json
{{paste output of: rayflow show context <show_name> --json}}
```

## What I Want

{{describe what you want to change or create}}

Examples:
- "Add cues for the intro section using the warm_wash preset"
- "Make the chorus brighter — increase all dimmer values to Full"
- "Create a new preset called verse_glow with dimmer 60 and warm amber color"
- "Add a slow pan sweep to all moving head fixtures during verse 2"
- "Change the color palette to cool blues for the chorus"
- "Suggest a vibe for this show based on the song structure"

## Instructions

1. Read the context above carefully
2. Understand the rig (fixtures, positions, presets) and current show state
3. Determine what changes are needed to fulfill my request
4. Show me the proposed changes before applying them:
   - What YAML files will be modified
   - What the diff will look like
   - What OSC commands would be sent to MA3 (if pushing)
5. Wait for my confirmation
6. After confirmation:
   - Modify the show/rig YAML files
   - If I asked to push to MA3, use `rayflow show push-to-ma3 <show_name> --execute`
   - Confirm what was changed

## Safety Rules

- Never send commands to MA3 without explicit `--execute` confirmation
- Always show proposed changes before modifying files
- If a change could break the show, warn me first
- Preserve existing cues unless I explicitly ask to modify or delete them

---

## Vibe Generation Guide

When asked to suggest a vibe, use this framework:

### Step 1: Analyze Song Structure
Read the show's sections from the context bundle. Consider:
- Section count and arrangement (intro, verses, choruses, bridge, outro)
- Energy levels (0-1 per section) — where does the song peak?
- Section moods — what emotions are described?

### Step 2: Choose a Color Palette
Select 3-5 colors that fit the song's mood. Store as hex codes:

| Mood | Suggested Colors |
|------|-----------------|
| Warm / energetic | `#FF6600`, `#FF3366`, `#FFCC00`, `#FF9933` |
| Cool / reflective | `#3366FF`, `#00CCFF`, `#6633FF`, `#0099CC` |
| Dark / aggressive | `#FF0000`, `#6600CC`, `#FF0066`, `#CC0000` |
| Bright / uplifting | `#FFFFFF`, `#FFCC00`, `#00FF66`, `#00CCFF` |
| Moody / cinematic | `#9933FF`, `#FF3366`, `#0033CC`, `#9900CC` |
| Natural / earthy | `#FF9933`, `#99CC33`, `#FFCC66`, `#66CC99` |

Common intensity curves for different song shapes:
- **Building energy**: `low → medium → high → peak → release`
- **Peak-early**: `high → medium → medium-low → high → low`
- **Wave**: `low → medium-high → low → medium-high → low`
- **Sustained energy**: `medium → high → high → high → medium`
- **Gentle arc**: `low → low-medium → medium → medium-low → low`

### Step 3: Select Movement Style
Match the song's energy pattern and fixture capabilities:
- **Static**: No movement — tight focus, best for ballads/spoken sections
- **Slow sweep**: Wide gentle pans — verses, atmospheric sections, bridges
- **Dynamic pan/tilt**: Energetic movement — choruses, builds, climaxes
- **Strobe + freeze**: Abrupt staccato — high-energy hits, EDM drops
- **Position palette**: Specific fixed looks — key changes, mood shifts

### Step 4: Define Beam Style
Based on fixture capability (beam fixtures = narrow, wash fixtures = wide):
- **Tight beams**: Focused, aerial — spot fixtures, aerial effects
- **Wide wash**: Broad coverage — PARs, wash fixtures, background fill
- **Mixed**: Both tight and wide — complex rigs with multiple fixture types
- **Gobo projection**: Patterned — requires gobo-capable fixtures

### Step 5: Set the Vibe
Use this command to apply the vibe to the show:

```bash
rayflow show set-vibe <show_name> --vibe-json vibe.json
```

Or inline:
```bash
rayflow show set-vibe <show_name> \
  --palette-name "Warm to Cool" \
  --colors '["#FF6600","#FF3366","#3366FF","#00CCFF"]' \
  --intensity "low → medium → high → peak → release" \
  --movement "slow sweep in verses, dynamic in choruses" \
  --beam "mixed"
```

---

## Cue Generation Guide

When generating cues from a vibe and section structure:

### Strategy: Section-Preset Mapping

Map each section to a preset and spacing:

```
Intro (0-15s, energy=0.3, mood="ambient"):
  - 3 cues, spaced 5s apart
  - Use: warm_wash preset, dimmer=40-60

Verse 1 (15-45s, energy=0.5, mood="mellow"):
  - 4 cues, spaced 8s apart (or on beat boundaries)
  - Use: warm_wash preset, dimmer=60-70, slow pan

Chorus (45-75s, energy=0.9, mood="uplifting"):
  - 6 cues, spaced 5s apart
  - Use: cold_beam preset, dimmer=Full, dynamic movement
```

### Cue Patterns by Section Energy

| Energy | Cue Spacing | Dimmer Range | Movement | Color |
|--------|-----------|-------------|----------|-------|
| 0.0-0.3 | 4-8s | 20-50 | static | palette[0] |
| 0.3-0.6 | 3-6s | 50-80 | slow sweep | palette[1] |
| 0.6-0.9 | 2-4s | 70-Full | dynamic | palette[2] |
| 0.9-1.0 | 1-3s | Full | strobe/fast | palette[3] |

### Adding Generated Cues

Use the CLI command to add cues:
```bash
rayflow show add-cue <show_name> --number <N> --label <label> \
  --section <section> --timestamp <seconds> --preset <preset> --fade <seconds>
```

Use `rayflow show generate-cues` for batch generation:
```bash
rayflow show generate-cues <show_name> --section "Chorus" \
  --preset "cold_beam" --count 6 --spacing 5 --fade 0.5
```

---

## Interactive Direction Guide

Common interactive directions and how to execute them:

### "Make the chorus brighter"
```bash
rayflow show batch-update-cues <show_name> --section "Chorus" \
  --attributes '{"dimmer":"Full"}'
```

### "Change to cool colors for verse 2"
```bash
rayflow show batch-update-cues <show_name> --section "Verse 2" \
  --attributes '{"color":"Cool Blue"}'
```

### "Add movement to the bridge"
```bash
rayflow show batch-update-cues <show_name> --section "Bridge" \
  --attributes '{"position":"Pan 45 Tilt 30"}'
```

### "Slow down the fade on the last chorus"
```bash
rayflow show batch-update-cues <show_name> --section "Chorus 3" \
  --set-fade 5.0
```

### "Delete all cues in the intro and start over"
```bash
rayflow show batch-update-cues <show_name> --section "Intro" --delete
```

---

## Available CLI Commands Reference

### Show Management
- `rayflow show create <name> --rig <rig> --title <title> --artist <artist> --duration <s>`
- `rayflow show list`
- `rayflow show info <name> [--json]`
- `rayflow show context <name> --json`

### Section Management
- `rayflow show add-section <show> --name <name> --start <s> --end <s> [--energy 0-1] [--mood <text>]`
- `rayflow show import-sections <show> <json_file>`
- `rayflow show update-section <show> --name <name> [--start <s>] [--end <s>] [--energy 0-1] [--mood <text>]`
- `rayflow show delete-section <show> --name <name>`

### Cue Management
- `rayflow show add-cue <show> --number <N> --label <text> --section <name> --timestamp <s> [--preset <name>] [--attributes '{"dimmer":"80"}'] [--channels <spec>] [--fade <s>]`
- `rayflow show update-cue <show> --number <N> [--label <text>] [--timestamp <s>] [--preset <name>] [--attributes '{...}'] [--fade <s>]`
- `rayflow show delete-cue <show> --number <N>`
- `rayflow show renumber <show>`
- `rayflow show generate-cues <show> --section <name> --preset <name> --count <N> --spacing <s> [--fade <s>]`
- `rayflow show batch-update-cues <show> [--section <name>] [--attributes '{...}'] [--set-fade <s>] [--delete]`
- `rayflow show save <show> [--message <text>]`
- `rayflow show versions <show>`
- `rayflow show restore <show> --version <id> [--force]`
- `rayflow show diff <show> --version <id> [--other-version <id>]`

### Vibe Management
- `rayflow show set-vibe <show> [--vibe-json <file>] [--palette-name <name> --colors '[...]' --intensity <curve> --movement <style>]`

### MA3 Integration
- `rayflow show push-to-ma3 <show> [--execute]`
- `rayflow show push-section <show> --section <name> [--execute]`
- `rayflow show export <show> --output-dir <path> [--sequence <N>]`
- `rayflow show export-mvr <show> --output <path.mvr>`
- `rayflow console cmd <command> [--execute]`

### Song Metadata
- `rayflow show set-song-meta <show> [--title <text>] [--artist <text>] [--duration <s>] [--bpm <N>]`

### Rig Management
- `rayflow rig create <name> --venue <name> --dimensions W,D,H`
- `rayflow rig list`
- `rayflow rig info <name> [--json]`
- `rayflow rig copy <source> <dest>`
- `rayflow rig add-fixture <rig> --fixture <name> --mode <name> --address <N> --label <text>`
- `rayflow rig add-preset <rig> <name> --description <text> --attributes '{"dimmer":"80","color":"Warm"}'
- `rayflow rig export-mvr <rig> --output <path.mvr>`
