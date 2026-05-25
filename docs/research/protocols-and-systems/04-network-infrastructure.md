# Network Infrastructure for Lighting Systems

**Source:** Web research, Art-Net/sACN specifications, network engineering for live events
**Parsed:** 2026-05-25

## Why Networking Matters

A lighting rig with more than one DMX universe requires Ethernet-based transport (Art-Net or sACN). The moment Ethernet enters the system, lighting becomes a networking problem. Poor network design causes flickering fixtures, dropped cues, and show-stopping failures. Good network design is invisible.

## The Lighting Network Stack

```
Layer 7: Art-Net / sACN / MA-Net3 (application protocols)
Layer 4: UDP (connectionless, low-latency)
Layer 3: IP (addressing, routing)
Layer 2: Ethernet (frames, MAC addresses, VLANs)
Layer 1: Cat5e/Cat6 copper, fiber optic
```

Lighting protocols run on UDP, not TCP. UDP has no retransmission, no connection handshake, and no congestion control. Packets arrive fast or not at all. This is correct for real-time DMX: a late packet is worse than a lost packet (which just holds the last value for one frame).

## Network Topologies

### Star Topology (Recommended)
```
        ┌─────────┐
        │  Switch  │  (core, managed)
        └────┬─────┘
     ┌───────┼───────┐
  ┌──┴──┐ ┌──┴──┐ ┌──┴──┐
  │Node │ │Node │ │Node │  (Art-Net/sACN nodes, consoles, pre-viz)
  └─────┘ └─────┘ └─────┘
```
- Every device connects directly to the core switch.
- A single device failure does not affect others.
- Requires more cable, but is robust and troubleshootable.

### Daisy-Chain (Avoid)
```
[Console] → [Node 1] → [Node 2] → [Node 3]
```
- A single cable or device failure takes down the entire chain downstream.
- Latency accumulates through the chain.
- Never daisy-chain Ethernet for lighting. Use dual-port nodes only as a convenience, not as the primary topology.

### Ring (Redundant)
```
        ┌────────┐
   ┌────┤ Switch  ├────┐
   │    └────────┘    │  (RSTP — Rapid Spanning Tree Protocol)
┌──┴──┐            ┌──┴──┐
│Node │            │Node │
└──┬──┘            └──┬──┘
   └──────────────────┘
```
- Managed switches with RSTP detect a break and reconfigure within 1–2 seconds.
- Provides physical redundancy at the cost of switch complexity.

## IP Addressing Convention

Standard lighting network addressing (using 10.x.x.x private range):

```
10.{venue}.{function}.{device}

  Venue: 1 = FOH, 2 = Stage, 3 = Dimmer Beach, 4 = Video
  Function: 1 = Consoles, 2 = Nodes/Processors, 3 = Fixtures (if IP-addressable), 4 = Pre-Viz/Engineering
  Device: 1–254

Example:
  10.1.2.10  = FOH, Node, unit 10
  10.2.1.1   = Stage, Console, unit 1
  10.2.2.20  = Stage, Node, unit 20
```

Subnet mask: 255.255.255.0 (/24) per venue area. This means each area gets its own /24 subnet (254 usable addresses). If venues share infrastructure, use VLANs to separate them (see below).

### Art-Net Default
Art-Net uses network 2.0.0.0/8 or 10.0.0.0/8 by default. Many legacy installations use this. Modern installs should use the 10.x.x.x scheme above and configure Art-Net to use the custom network.

### sACN Default
sACN uses multicast addresses 239.255.0.0/16. The console/node automatically joins the multicast group for each universe it subscribes to. No IP addressing of individual universes is needed beyond the unicast IP of each device.

## VLANs: Separating Lighting from Everything Else

Lighting traffic must be isolated from other network traffic:

```
VLAN 10: Lighting Control (Art-Net, sACN, MA-Net)
VLAN 20: Lighting Fixture Management (RDM over Art-Net, fixture firmware updates)
VLAN 30: Audio Control (Dante, AES67)
VLAN 40: Video (NDI, SDI-over-IP)
VLAN 50: Internet / Show Management (email, cloud backup, remote desktop)
```

### Why VLANs Matter
- **Bandwidth isolation:** sACN for 100 universes at full rate saturates a 100 Mbps link. Video-over-IP saturates gigabit. Keep them apart.
- **Broadcast containment:** Art-Net uses broadcast by default (255.255.255.255). Without VLANs, every device on the network processes every broadcast packet.
- **Security:** Separate guest WiFi and show-critical lighting networks.

### VLAN Configuration on Managed Switches
- Trunk ports carry multiple VLANs between switches (tagged).
- Access ports carry a single VLAN to end devices (untagged). Consoles and nodes connect to access ports.
- Lighting VLAN should be isolated from internet access. No default gateway on the lighting VLAN.

## IGMP Snooping for sACN Multicast

sACN uses IP multicast. Without IGMP snooping, multicast packets are flooded to every port on the switch — every device receives every universe's data, saturating links.

**IGMP snooping** enables the switch to learn which ports have subscribed to which multicast groups. The switch sends sACN data only to ports where a device has requested that universe. This reduces network load by 90%+ in large installations.

### Configuration
- Enable IGMP snooping on all managed switches carrying sACN traffic.
- Designate an IGMP querier (usually the core switch or the console).
- Verify with: show all multi-homed devices only receive their subscribed universes.

## Network Hardware Selection

| Component | Requirement | Notes |
|-----------|------------|-------|
| **Switches** | Managed, Gigabit, IGMP snooping, VLAN support | Netgear M4250, Luminex GigaCore, Cisco SG350. Unmanaged switches are show-stoppers. |
| **Cable** | Cat5e minimum, Cat6 preferred | Shielded (STP) for touring. EtherCON connectors at termination points. |
| **Fiber** | Single-mode (SMF) for runs >100m | LC connectors. Use media converters or switches with SFP slots if console lacks fiber port. |
| **Wireless** | Never for show-critical lighting | Only for RFR (remote focus remote), MA3 remote app, or engineering access. |

## Common Network Problems

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| Intermittent flicker on all fixtures | Network congestion or broadcast storm | Enable IGMP snooping, separate VLANs |
| One universe flickers, others fine | IP address conflict, duplicate universe | Check Art-Net universe assignments, verify no two devices output the same universe |
| All fixtures freeze for 1–5 seconds | Network loop (no RSTP) | Check for accidental loops. Enable RSTP on managed switches. |
| Console can't discover nodes | VLAN mismatch, subnet mismatch | Verify console and nodes on same VLAN, same subnet |
| Fixtures respond slowly to console | High network latency, daisy-chain topology | Reduce hop count, check cable quality, use star topology |

## Physical Infrastructure

- **FOH to Stage run:** A single fiber pair or 2× Cat6 cables in a ruggedized multicore. This is the most critical cable in the system.
- **EtherCON:** RJ45 in a ruggedized XLR-style shell. Standard on professional lighting equipment. Locking, dust-proof, road-worthy.
- **Cable management:** Label both ends of every cable. Use different colors for different VLANs/network functions. Coil over-under.

## Implications for RayFlow

1. **Network map in rig model:** The `Rig` model should capture universe-to-protocol-to-subnet mappings for export as a network configuration document.
2. **Universe count warnings:** When a show exceeds 5 universes, RayFlow should recommend sACN (multicast efficiency) over Art-Net (broadcast overhead) and note that managed switches with IGMP snooping are required.
3. **IP address tracking:** The bridge module should log the source/destination IP and universe of incoming Art-Net/sACN packets for debugging.
4. **VLAN recommendation in exports:** The show export bundle should include a recommended VLAN configuration based on the show's universe count and protocol mix.
5. **Health check command:** A `bridge network-check` command could verify that Art-Net/sACN is flowing on the expected IP/subnet and that no universe conflicts exist.
