# Recording a Show — Program Cues and Export Video

This guide walks through the complete workflow: load a song, program lighting cues, and export a video of your virtual show.

## Prerequisites

- RayFlow installed
- A song you want to light
- A generated RayFlow show and rig
- For the current visual-review path: Capture 2026 or Capture 2026 Student Edition
- Optional compatibility path: grandMA3 onPC with a rig loaded

## Step 1: Listen and Analyze the Song

Before programming, listen to the song and note its structure:

| Section | Time | Mood | Lighting Idea |
|---------|------|------|---------------|
| Intro | 0:00-0:30 | Ambient | Slow fade, cool colors |
| Verse 1 | 0:30-1:00 | Intimate | Warm wash, low intensity |
| Chorus 1 | 1:00-1:30 | Energy | Full stage, bright colors |
| Verse 2 | 1:30-2:00 | Building | Add movement, increase intensity |
| Chorus 2 | 2:00-2:30 | Peak | Full energy, strobes, effects |
| Bridge | 2:30-3:00 | Atmospheric | Hazer, slow color transitions |
| Chorus 3 | 3:00-3:30 | Climax | Everything at full |
| Outro | 3:30-4:00 | Fade out | Slow dim, single color |

## Step 2: Set Up the Audio

grandMA3 onPC can play audio synced to cues:

1. Go to **Setup** → **Audio** → **Import Audio**
2. Select your song file
3. Set the audio to play from the beginning
4. Adjust volume for monitoring

## Step 3: Program the Intro

Start simple — set the mood:

1. **Clear** the programmer
2. Select all PAR fixtures
3. Set to a cool blue at 30% intensity
4. Set the hazer to 50%
5. **Store** → **Cue 1** → **Please**
6. Set fade time: **Time 1** → **5** → **Please** (5 second fade)

## Step 4: Program the Verse

1. **Clear** the programmer
2. Set PARs to warm amber at 50%
3. Position moving heads to center stage
4. **Store** → **Cue 2** → **Please**
5. Set fade time: **Time 2** → **3** → **Please**

## Step 5: Program the Chorus

1. **Clear** the programmer
2. Set all PARs to full intensity, mixed colors
3. Set moving heads to wide positions
4. Add a strobe effect to the moving heads
5. **Store** → **Cue 3** → **Please**
6. Set fade time: **Time 3** → **0.5** → **Please** (quick hit)

## Step 6: Continue Through the Song

Repeat the pattern for each section. Tips:

- **Use cues to mark transitions:** Each song section = at least one cue
- **Vary intensity:** Not everything needs to be full — dynamics matter
- **Use color strategically:** Warm for intimate, cool for atmospheric, mixed for energy
- **Add movement in choruses:** Moving heads add visual energy
- **Don't over-program:** Sometimes less is more

## Step 7: Use AI to Generate Starting Cues

RayFlow can propose starting cues for your show using the authoring planner:

```bash
# Propose cues for a section (dry-run by default)
uv run rayflow show plan-cues --show my_show --rig my_rig --section "Verse 1" --style warm

# Apply the proposed cues after review
uv run rayflow show plan-cues --show my_show --rig my_rig --section "Verse 1" --style warm --apply
```

Use `--style vibe-palette` to draw colors from the show's vibe instead of specifying a style. The command is proposal-only by default and requires `--apply` to write changes.

For more detail, see the [AI Interaction Contract](../ai_interaction_contract.md).

## Step 8: Export The Capture Handoff

Export the generated show into a Capture-ready handoff bundle:

```bash
uv run rayflow show export-capture my_show \
  --dir data/shows \
  --rig-dir data/rigs \
  --fixture-dir data/fixtures/samples \
  --output-dir exports/capture/my_show \
  --dmx-protocol sacn
```

The bundle contains:

- `rig.mvr` for Capture import
- `cue_sheet.md` for human review
- `metadata.json` linking the show, rig, fixture count, cue count, and DMX protocol
- `README.md` with the exact Capture import and review steps

## Step 9: Rehearse the Show

1. Open Capture and import `exports/capture/my_show/rig.mvr`.
2. If Capture asks for fixture matching, map imported fixture types to the nearest available Capture library fixtures.
3. Enable the selected DMX input protocol, starting with sACN unless your local setup requires Art-Net.
4. Play the song and trigger the RayFlow cues in song time.
5. Note timing, color, movement, and intensity issues by timestamp.

## Step 10: Record Capture

Use Capture as the review surface and record that window with QuickTime, OBS, or another screen recorder:

1. Start your screen/audio recorder (e.g. OBS, QuickTime).
2. Set it to capture the Capture visualizer window and the song audio.
3. Start RayFlow DMX output for the show through the selected protocol.
4. Stop the screen recording once the song completes.
5. Save the video beside the Capture handoff bundle and link it in the pilot report.

## Step 11: Recording Report

The generated recording report links the show design, rig, and output artifacts:

```json
{
  "show": "my_show",
  "rig": "my_rig",
  "mode": "live",
  "timing": {
    "kind": "observed",
    "summary": "Live mode records measured trigger offsets from the WebSocket playout loop."
  },
  "video_path": "exports/recordings/my_show.mp4",
  "audio_path": "data/audio/my_song.mp3",
  "visualizer": "Capture",
  "handoff_bundle": "exports/capture/my_show",
  "playout_log": [
    {
      "cue_number": 1,
      "cue_label": "Intro",
      "scheduled_time": 0.0,
      "actual_trigger_time": 0.002,
      "trigger_time_kind": "observed",
      "status": "success",
      "error": null
    }
  ],
  "timestamp": "2026-05-28T12:00:00Z",
  "status": "completed"
}
```

## Tips for Better Shows

- **Less is more:** Don't light every beat — let the music breathe
- **Build energy:** Start small, grow to a climax, then resolve
- **Use silence:** Dark moments make bright moments more impactful
- **Color tells a story:** Warm = intimate, cool = distant, red = intense, blue = calm
- **Movement adds life:** Even subtle pan/tilt changes make a scene feel alive
- **Record everything:** You'll learn more from watching your work than from programming it

## Exporting for Sharing

Once you're happy with the recording:

1. The video file is saved to your chosen output location.
2. You can add the original audio track in a video editor if needed.
3. Export as MP4 for sharing on social media or portfolio.
