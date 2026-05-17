---
name: art-net-bridge
description: "Send and receive DMX via Art-Net protocol"
metadata:
  trigger-keywords: "art-net, send dmx, receive dmx, artdmx, udp lighting"
  trigger-patterns: "^art-net, ^send dmx, ^receive dmx, ^artdmx"
---

# Art-Net Bridge Skill

## When to Use

- Sending DMX values from Python to a visualizer or grandMA3 onPC
- Receiving DMX output from grandMA3 onPC
- Testing Art-Net communication
- Building a DMX bridge between protocols

## Inputs

- Universe number (0-15 for Art-Net 4)
- DMX channel values (0-255, up to 512 channels per universe)
- Target IP address (for sending)
- Optional: Broadcast address for discovery

## Steps

1. **Configure Art-Net connection**
   - Set target IP address
   - Set universe number
   - Configure port (default: 6454)
   - Choose broadcast or unicast mode

2. **Build ArtDMX packet**
   - Art-Net header: "Art-Net" + 0x00 + opcode 0x5000
   - Protocol version (14)
   - Sequence number (incrementing, prevents duplicates)
   - Physical port (0)
   - Universe (low byte + high byte)
   - Length (high byte + low byte)
   - DMX data (512 bytes)

3. **Send packet**
   - Open UDP socket
   - Send packet to target IP:6454
   - Increment sequence number
   - Handle errors (network unreachable, port in use)

4. **Receive packets (optional)**
   - Bind UDP socket to port 6454
   - Listen for ArtDMX packets
   - Parse header and extract DMX data
   - Map to universe and channels

5. **Verify communication**
   - Use Wireshark or similar to verify packets
   - Check that visualizer/console receives correct values
   - Verify sequence numbers are incrementing

## Validation

- ArtDMX packets are correctly formatted
- DMX values arrive at target unchanged
- Sequence numbers increment properly
- Multiple universes work independently

## Common Mistakes

- Not incrementing sequence number (receivers may drop duplicates)
- Wrong byte order for universe or length fields
- Broadcasting when unicast is needed (or vice versa)
- Not handling universe 0 vs universe 1 confusion (Art-Net uses 0-based)
- Sending packets too fast (Art-Net has no rate limiting, but receivers may drop)

## Links

- Art-Net Specification: https://art-net.org.uk/
- python-osc library: https://pypi.org/project/python-osc/
- sacn library: https://pypi.org/project/sacn/
- Project Charter: `docs/project_charter.md`
