# First DMX — Send Your First DMX Values

This tutorial walks through sending DMX values from RayFlow to an Art-Net
receiver. That receiver can be grandMA3 onPC, QLC+, a visualizer, or hardware
on a private lighting network.

## Prerequisites

- RayFlow installed with lighting extras: `uv sync --extra lighting`
- An Art-Net receiver or controller configured on the target universe
- A patched fixture, visualizer channel, or receiver monitor to verify output

## Step 1: Verify A Receiver Is Running

1. Open your Art-Net receiver, controller, or visualizer.
2. Confirm it is listening on the target network interface.
3. Confirm a fixture, channel monitor, or visualizer object is patched.

## Step 2: Check Network Connection

Art-Net uses UDP port 6454. For local development, start with `127.0.0.1` when
your receiver supports loopback.

If using grandMA3 onPC, enable an Art-Net input row for the target local
universe. RayFlow's current MA3 compatibility baseline is grandMA3 onPC
2.3.2.0, where Art-Net input should be explicitly verified per show.

```bash
# Confirm something is listening for Art-Net after input is enabled
lsof -iUDP:6454
```

## Step 3: Send a DMX Value

```bash
# Send full intensity to channel 1 of universe 0
uv run rayflow bridge send --universe 0 --channel 1 --value 255
```

You should see the receiver, fixture, or visualizer respond.

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
- The receiver/controller may not be running
- If using grandMA3, check that Art-Net input is enabled in the show
- Verify firewall isn't blocking port 6454

### Wrong fixture responds
- Check the DMX address mapping
- Multiple fixtures may share the same universe — verify addresses don't overlap

## Next Steps

- **[Building a Rig](./building-a-rig.md)** — Create a full virtual stage with multiple fixtures
- **[Recording a Show](./recording-a-show.md)** — Program cues for a song and export video
