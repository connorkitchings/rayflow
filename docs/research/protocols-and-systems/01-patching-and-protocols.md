# System Architecture, Patching, and Digital Protocols

**Source:** `docs/research/manual_research2.txt`  
**Parsed:** 2026-05-25

## The System Patching Workflow and Fixture Alignment

Patching maps physical lighting fixtures to logical control channels on the console. A single physical DMX universe contains 512 individual control addresses, each transmitting an 8-bit value from 0 to 255. A simple conventional dimmer requires only 1 DMX channel for intensity; complex automated fixtures can require 30 to 90 DMX channels.

### Patching Sequence

1. **Fixture Inventory and Profile Selection:** Identify every fixture in the rig. Locate or build a matching "fixture profile" in the console that maps what each DMX channel controls.
2. **Address Assignment:** Assign each fixture a unique starting DMX address within a specific universe. Fixtures must not overlap (e.g., if Fixture 1 uses 34 channels starting at address 1, the next fixture must start at address 35 minimum).
3. **Logical Channel Numbering:** Decouple physical DMX addresses from console control channels for organization (e.g., spots = channels 101-157, washes = channels 201-262).
4. **Fixture Alignment Calibration:** After the rig is hung, check physical orientation. Invert or swap pan/tilt channels in the console patch so all fixtures react uniformly to encoder controls.

## Data Transport, Bandwidth, and Ethernet Protocols

| Protocol | Cabling | Max Universes | Transmission | Key Features |
|---|---|---|---|---|
| DMX512 | RS-485 Serial (5-pin XLR) | 1 (512 channels) | Daisy-Chain Serial | Direct, low-latency. Limited to single-universe runs. |
| RDM | RS-485 Serial | 1 | Half-Duplex Bi-directional | Fixtures send feedback to console. Remote address changes and status monitoring. |
| Art-Net | Ethernet (Cat5e/Cat6) | 32,768 | Unicast or Broadcast | DMX over IP. Widely used for pixel mapping and media servers. Requires careful network configuration. |
| sACN (E1.31) | Ethernet (Cat5e/Cat6) | 63,999 | Multicast (Primary) | ANSI standard for high-capacity systems. Multicast reduces network load. Built-in priority management and synchronization. |
| Wireless DMX | RF Transmitter/Receiver | 1 per link | RF Broadcast | Eliminates long cable runs. Ideal for temporary outdoor events. Subject to wireless interference. |

## DMX512 Bandwidth Calculation

DMX512 operates at a fixed baud rate of 250,000 bits/second. The time required to transmit a single frame containing N control channels:

- Break time: 88 μs
- Mark After Break: 8 μs
- Slot time: 44 μs (1 start bit + 8 data bits + 2 stop bits = 11 bits)

For a fully saturated universe of 512 channels:
- Frame time = 88 + 8 + (513 × 44) = 22,660 μs
- Maximum theoretical refresh rate = 1 / 22,660 μs ≈ 44.1 Hz

A 44 Hz refresh rate is standard for physical DMX. When video cameras capture high-density LED fixtures, this can cause visible banding and flicker. Resolved by using fixtures with high internal PWM frequencies and routing frame-synchronized sACN or Art-Net data to high-performance pixel decoders.
