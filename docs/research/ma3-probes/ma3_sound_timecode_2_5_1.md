# MA3 Sound and Timecode Playback (2.5.1)

**Target:** grandMA3 onPC 2.5.1 on macOS
**Status:** UNVERIFIED on onPC for macOS. Everything below comes from the MA help pages. Nothing here has been run.
**Sources:** `~/MALightingTechnology/gma3_2.5.1/shared/language/HTML/`
- `sound_pool.html`, "Sounds Pool" (help version 2.4)
- `sound.html`, "Sound" (help version 2.4)
- `timecode_tracks.html`, "Tracks" (help version 2.5)

## What the help pages say

- **Folder.** `sound_pool.html`: "The folder is /gma3_library/media/sounds." On this Mac that is `~/MALightingTechnology/gma3_library/media/sounds/`.
- **Import.** Sound files are imported into the Sounds Pool. `sound_pool.html` gives two routes: the Show Creator import function, or the Sounds pool itself ("Tap Import.").
- **Size limit.** `sound_pool.html`: "The Sounds Pool has a limit of 100 MB for all objects." It also says "The total size of all media pools is limited to 300 MB."
- **Timecode track.** `sound_pool.html`: "Sound pool objects can be played back in the pool or added as a track in a timecode object." `timecode_tracks.html`: "Sound pool objects can be assigned to tracks and will display the waveform in the timecode show."
- **Playback.** `timecode_tracks.html`: "The sound assigned to a track is played back when the timecode show is played." `sound_pool.html`: "Running the timecode show plays the sound from the timecode object."
- **Audio output.** `sound_pool.html`: "The master needs a physical audio output connected. Learn how in the Connect Sound Out topic." and "The Sound Out master fader must be turned up." The Connect Sound Out topic was not read for this note.
- **Track limits.** `timecode_tracks.html`: "Events cannot be added to the soundtrack." A warning icon shows if the sound file is corrupted.
- **Level.** `sound_pool.html`: the dB setting ranges from -6 db to +6 db.

## Discrepancy with the brief

The brief said "Running the timecode show plays the sound." The page's exact sentence is "Running the timecode show plays the sound from the timecode object." The meaning is the same, but quote the page, not the brief.

## Size check

A 281 s, 16-bit stereo WAV is about 50 MB at 44.1 kHz (281 × 44,100 × 2 channels × 2 bytes ≈ 49.7 MB). At 48 kHz it is about 54 MB. Both fit under the 100 MB Sounds Pool limit. This is arithmetic, not a test: the pool's counting method for imported files is not stated in the help pages.

## Consequence for RayFlow (our inference, unverified)

If the file plays from a timecode show inside onPC on macOS, the chain is: sound file in the pool, Sound track on a timecode show, run the timecode show. That would not need a DAW, an IAC driver, or an MTC script.

The help pages do not say that any of those are unnecessary, and they do not describe macOS audio. This note does not cover syncing to an external clock; `timecode_external_connections.html` was not read.

## Open questions (spike)

1. Does a sound pool object play on onPC 2.5.1 on macOS when `Go+` is run on it?
2. Which audio output device does onPC use on this Mac, and does the Sound Out master fader need to be raised for output?
3. Does a Sound track play when the timecode show runs?
4. How far does the sound drift from the 3D playback (latency or sync), measured by eye and ear?

## Spike checklist

1. Copy the song WAV (16-bit stereo) into `~/MALightingTechnology/gma3_library/media/sounds/`.
2. Create a new scratch show in onPC (not a show you care about).
3. Open a Sounds Pool window, edit an empty slot, and tap Import. Select the file and import it. Note the file size and the Duration shown in the Edit Sound pop-up.
4. Run `Go+` on the sound pool object. Note whether sound is audible.
5. Connect the physical audio output as described in the Connect Sound Out topic (read it first). Raise the Sound Out master fader. Run step 4 again.
6. Create a timecode show, add a track group and a track, and set the track target to the sound object (the editor steps are in `timecode_tracks.html`). Run the timecode show and note whether sound plays.
7. Once the patch and 3D spike has run, play the 3D show and the timecode show together. Note any offset.
8. Record the onPC build, the audio output device, and the results in this file. The menu labels and button names above are from the help text only; check them on screen and note any differences.
