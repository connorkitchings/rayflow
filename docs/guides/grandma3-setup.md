# grandMA3 onPC Setup Guide

This guide walks through installing and configuring grandMA3 onPC on macOS for RayFlow development.

**Verified local version:** grandMA3 onPC 2.3.2.0 on macOS (`/Applications/grandMA3.app`).

RayFlow instructions should be treated as version-specific. Re-check the installed version before relying on UI paths or protocol menu behavior:

```bash
/usr/libexec/PlistBuddy -c 'Print :CFBundleVersion' /Applications/grandMA3.app/Contents/Info.plist
```

## Prerequisites

- macOS 10.15 or later
- Apple Silicon (M1/M2/M3) or Intel Mac
- At least 4 GB RAM (8 GB recommended)
- Internet connection for download and fixture library

## 1. Download grandMA3 onPC

1. Visit [MA Lighting Downloads](https://www.malighting.com/downloads/products/grandma3/)
2. Find "grandMA3 onPC Software for macOS"
3. Download the ZIP file (~630 MB)
4. Current RayFlow baseline: 2.3.2.0

## 2. Install

1. Unzip the downloaded file
2. Open the `.dmg` or installer package
3. Drag grandMA3 onPC to your Applications folder
4. Launch the application

**Note:** macOS may warn about an unidentified developer. Go to System Settings → Privacy & Security → Allow Anyway.

## 3. First Launch

1. Open grandMA3 onPC
2. Select "New Show" when prompted
3. Choose a show name (e.g., "RayFlow Practice")
4. The console will initialize with default settings

## 4. Configure Network Settings

grandMA3 onPC needs network access for Art-Net, sACN, and OSC:

1. Open the network / DMX protocol settings for the active show.
2. Ensure the loopback or active network interface is available.
3. Note your Mac's IP address if RayFlow is not using localhost.
4. Enable an Art-Net input row for the target local universe. In grandMA3 2.3.2.0, Art-Net input is not safe to assume enabled in a new show.
5. Verify MA3 is listening for Art-Net after enabling input:

```bash
lsof -iUDP:6454
```

Expected result: a grandMA3 process such as `app_gma3` is bound to UDP port 6454.

## 5. Enable OSC

For RayFlow to control the console via OSC:

1. Open the **In & Out / OSC** configuration.
2. Enable OSC input.
3. Confirm the Receive row is enabled and uses the expected protocol and port.
4. Use port 8000 unless the show file has been configured differently.
5. Set allowed IP addresses for local development, preferring `127.0.0.1` or your Mac's local address.

RayFlow uses `/cmd` with a string argument for command-line control. The MA 2.3 manual notes that the grandMA3 command line is available over OSC through the `/cmd` address with OSC string type `s`.

## 6. Verify the 3D Visualizer

1. Press the **3D** button on the console toolbar
2. The visualizer window should open with a default stage
3. If prompted, download the default fixture library

## 7. Load a GDTF Fixture

To test that fixtures work:

1. Go to **Setup** → **Fixture** → **Fixture Type**
2. Browse or search for a fixture
3. Select a simple fixture (e.g., a PAR or generic dimmer)
4. Patch it to an address (e.g., Universe 1, Address 1)

## 8. Test with a Simple Cue

1. Select the fixture in the programmer
2. Set intensity to 100% (press `At` `Full`)
3. Press `Store` → `Cue` `1` → `Please`
4. Press `Clear` to clear the programmer
5. Press `Go` to play the cue — the fixture should light up in the visualizer

## 9. Compare a RayFlow Fixture Patch with grandMA3

Use this checklist when validating RayFlow's GDTF parsing and patching against grandMA3 onPC 2.3.2.0:

1. Verify the installed version:

```bash
/usr/libexec/PlistBuddy -c 'Print :CFBundleVersion' /Applications/grandMA3.app/Contents/Info.plist
```

2. In grandMA3, load or import the same GDTF fixture file used by RayFlow.
3. Patch the same DMX mode, universe, and start address.
4. Record the MA3-observed footprint in this JSON shape:

```json
{
  "manufacturer": "RayFlow",
  "fixture": "Sample Dimmer",
  "mode": "Basic",
  "universe": 0,
  "start_address": 1,
  "end_address": 1,
  "channel_count": 1,
  "required_attributes": ["Dimmer"]
}
```

5. Compare the observation with RayFlow:

```bash
rayflow fixture compare-ma3 "Sample" --dir data/fixtures/samples --ma3-json ma3-observation.json
```

Without `--ma3-json`, the command prints RayFlow's expected patch report for manual checking.

## 10. Generate Cue Stack Commands from JSON

RayFlow can build repeatable grandMA3 command-line workflows from a lightweight cue stack JSON file:

```json
{
  "sequence": 1,
  "name": "Demo Stack",
  "cues": [
    {
      "cue": 1,
      "label": "Intro",
      "channels": "1 Thru 8",
      "at": "Full",
      "fade": 2.5,
      "clear_after": true
    }
  ]
}
```

Preview generated commands without touching the console:

```bash
rayflow console cue-stack run demo-stack.json
```

Send them to grandMA3 only after verifying the dry run:

```bash
rayflow console cue-stack run demo-stack.json --execute
```

The same dry-run safety applies to shortcut commands such as `rayflow console cue store 1`, `rayflow console sequence go 1`, `rayflow console channel at "1 Thru 8" Full`, and `rayflow console clear`.

## Troubleshooting

### grandMA3 onPC won't launch
- Check macOS version compatibility
- Try reinstalling from the latest download
- Check Console.app for crash logs

### 3D Visualizer is blank
- Ensure a fixture is patched
- Check that the fixture has 3D geometry (some generic fixtures don't)
- Try loading a different fixture from the library

### OSC connection fails
- Verify OSC is enabled in Network Setup
- Check the port number (default: 8000)
- Ensure firewall isn't blocking the connection
- Test with a real OSC client; plain `nc` does not create valid OSC packets.

### Art-Net not receiving
- Check Network Setup for the correct interface
- Confirm an Art-Net input row is enabled for the target local universe
- Verify the universe number matches what RayFlow sends
- Use Wireshark or tcpdump to confirm Art-Net packets are arriving

```bash
sudo tcpdump -i lo0 -c 5 port 6454
```

## Learning Resources

Use these sources when RayFlow work depends on grandMA3 behavior:

- [grandMA3 2.3 Online Manual](https://help.malighting.com/grandMA3/2.3/HTML/index.html) — primary source for version-specific UI and command behavior.
- [MA Lighting Video Tutorials](https://www.malighting.com/ma-university/video-tutorials/) — official MA video index with grandMA3 series links.
- [MA Lighting Downloads](https://www.malighting.com/downloads/products/grandma3/) — release notes and installer versions.
- [GDTF Share](https://gdtf-share.com/) — fixture files for RayFlow Phase 3 tests.

## Next Steps

- Read the [First DMX Guide](./first-dmx.md) to connect RayFlow
- Read the [Building a Rig Guide](./building-a-rig.md) to create a virtual stage
- Explore the grandMA3 [Online Manual](https://onlinehelp.malighting.com/)
- For AI agents operating MA3: see [AI MASTER CONTEXT](../ai/MASTER_CONTEXT.md)
