# First DMX — Send Your First DMX Values

This tutorial walks through sending DMX values from RayFlow to grandMA3 onPC and seeing lights respond in the visualizer.

## Prerequisites

- grandMA3 onPC installed and running (see [Setup Guide](./grandma3-setup.md))
- RayFlow installed with lighting extras: `uv sync --extra lighting`
- A fixture patched in grandMA3 (a simple PAR or dimmer works)

## Step 1: Verify grandMA3 is Running

1. Open grandMA3 onPC
2. Open the 3D visualizer
3. Confirm a fixture is patched and visible

## Step 2: Check Network Connection

grandMA3 onPC and RayFlow communicate over your local network. For local development, start with `127.0.0.1`.

Before sending DMX, enable an Art-Net input row in grandMA3 for the target local universe. RayFlow's current baseline is grandMA3 onPC 2.3.2.0, where Art-Net input should be explicitly verified per show.

```bash
# Confirm grandMA3 is listening for Art-Net after input is enabled
lsof -iUDP:6454
```

## Step 3: Send a DMX Value

```bash
# Send full intensity to channel 1 of universe 0
uv run rayflow bridge send --universe 0 --channel 1 --value 255
```

You should see the fixture light up in the grandMA3 visualizer.

## Step 4: Try Different Values

```bash
# Dim to 50%
uv run rayflow bridge send --universe 0 --channel 1 --value 128

# Turn off
uv run rayflow bridge send --universe 0 --channel 1 --value 0
```

## Step 5: Send Multiple Channels

The current CLI sends one channel at a time. If your fixture has multiple channels, send one command per channel:

```bash
# Red full, green off, blue off
uv run rayflow bridge send --universe 0 --channel 1 --value 255
uv run rayflow bridge send --universe 0 --channel 2 --value 0
uv run rayflow bridge send --universe 0 --channel 3 --value 0
```

## Step 6: Verify with Python

You can also send DMX directly from Python:

```python
from rayflow.bridge.artnet import ArtNetSender

sender = ArtNetSender(target_ip="127.0.0.1")
sender.send_dmx(universe=0, channel=1, value=255)
```

## Troubleshooting

### Fixture doesn't respond
- Verify the fixture is patched to the correct universe and address
- Confirm grandMA3 onPC has an enabled Art-Net input row for the target local universe
- Try sending to universe 1 instead of 0 (MA3 may use 1-based universes)

### Connection refused
- grandMA3 onPC may not be running
- Check that Art-Net input is enabled in the show
- Verify firewall isn't blocking port 6454

### Wrong fixture responds
- Check the DMX address mapping
- Multiple fixtures may share the same universe — verify addresses don't overlap

## Next Steps

- **[Building a Rig](./building-a-rig.md)** — Create a full virtual stage with multiple fixtures
- **[Recording a Show](./recording-a-show.md)** — Program cues for a song and export video
