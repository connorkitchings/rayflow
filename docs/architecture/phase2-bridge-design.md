# Phase 2 Bridge Design

> **Status:** Draft · **Phase:** 2 — Art-Net / sACN Bridge · **Date:** 2026-05-15

## Purpose

Design the bridge layer that allows RayFlow to send and receive DMX values over Art-Net and sACN protocols. This document defines the architecture, API contracts, CLI surface, error model, and integration points before implementation begins.

---

## 1. Current State

Phase 1 produced wrapper classes around the `stupidArtnet` and `sacn` libraries:

| File | Classes | Coverage | Status |
|------|---------|----------|--------|
| `bridge/artnet.py` | `ArtNetSender`, `ArtNetReceiver` | 44% | Wrappers exist, untested, unused by CLI |
| `bridge/sacn_bridge.py` | `SacnSender`, `SacnReceiver` | 31% | Wrappers exist, untested, unused by CLI |
| `cli.py` | `bridge send` command | 0% | Stub: prints placeholder text |
| `fixtures/patch.py` | `DmxUniverse`, `FixturePatch` | 27% | Data model exists, untested, unused |
| `config.py` | `Settings`, `ArtnetConfig`, `SacnConfig` | 96% | Loads from env vars |

**Critical gaps:**
- CLI commands are stubs — `rayflow bridge send` does nothing
- No functional tests for any bridge class
- No error handling for network failures, invalid channels, or universe overflow
- `DmxUniverse` model is isolated — not connected to the bridge layer
- `tests/conftest.py` contains template debris (`import vibe_coding.config`)

---

## 2. Design Decisions

### 2.1 Keep wrappers, do not build a unified abstraction yet

The `ArtNetSender`/`SacnSender` classes remain separate. They wrap fundamentally different libraries with different lifecycle models — Art-Net uses a threaded sender, sACN uses a fire-and-forget model. A shared interface would abstract away meaningful protocol differences that users need to reason about.

**Decision:** Keep current class structure. Add a thin CLI dispatch layer that selects the appropriate sender based on `--protocol`.

### 2.2 Wire CLI directly to wrapper classes

The CLI is the entry point for Phase 2. The `bridge send` command instantiates the correct sender, calls the appropriate setter, and prints confirmation. No intermediate service layer is needed at this stage.

**Decision:** CLI commands instantiate senders directly, not via a factory or DI container.

### 2.3 sACN commands default to unicast in development

sACN typically uses multicast, but during development on a single machine, unicast to `127.0.0.1` is simpler and avoids network configuration issues. Multicast remains available via a `--multicast` flag.

**Decision:** Default to unicast for all bridge commands targeting `127.0.0.1`.

### 2.4 DMX value persistence is deferred to Phase 3+

Phase 2 sends DMX on demand (one-shot). A full universe with persistent 30Hz streaming is a Phase 3/4 concern — it needs the GDTF fixture layer and a reason to stream (MA3 connection or visualizer). The `start_thread()`/`stop_thread()` methods on `ArtNetSender` already exist for this.

**Decision:** Phase 2 implements one-shot send only. Persistent streaming is Phase 4+.

### 2.5 DmxUniverse model stays in fixtures/ for now

The `DmxUniverse` model logically belongs with the bridge, but the patching system ties it to fixtures. Moving it would break the GDTF patching workflow in Phase 3. Keep it where it is; the bridge reads from it without owning it.

**Decision:** `DmxUniverse` stays in `fixtures/patch.py`. Bridge classes accept raw channel/value pairs; universe-level operations reference `DmxUniverse` as input.

---

## 3. CLI Contract

### 3.1 `bridge send` — Send a single DMX channel value

```
rayflow bridge send [OPTIONS]

Options:
  -u, --universe INTEGER    DMX universe (0-15 for Art-Net, 1-63999 for sACN) [default: 0]
  -c, --channel INTEGER     DMX channel (1-512) [default: 1]
  -v, --value INTEGER       DMX value (0-255) [default: 0]
  -p, --protocol TEXT       Protocol: artnet or sacn [default: artnet]
  -t, --target TEXT         Target IP address [default: from ARTNET_TARGET env, else 127.0.0.1]
  --multicast / --no-multicast  Use multicast (sACN only) [default: no-multicast]
```

**Success output:**
```
Sending channel 1 = 255 on universe 0 via artnet
Target: 127.0.0.1:6454
Packet 1 sent — verify with Wireshark or console visualizer
```

**Error output (target unreachable):**
```
Error: Cannot reach 192.168.1.100:6454 — network unreachable
```

### 3.2 `bridge recv` — Listen for incoming DMX

```
rayflow bridge recv [OPTIONS]

Options:
  -u, --universe INTEGER    DMX universe to listen on [default: 0]
  -p, --protocol TEXT       Protocol: artnet or sacn [default: artnet]
  --duration INTEGER        Seconds to listen [default: 10]
  -c, --channel INTEGER     Filter to single channel (1-512)
```

**Output (all channels, non-zero values):**
```
Listening on universe 0 via artnet (port 6454) for 10 seconds...

Channel   Value
--------  -----
1         255
3         128
10        64
```

### 3.3 `bridge status` — Show configured bridge settings

```
rayflow bridge status

Options:
  (none — reads from environment / config)
```

**Output:**
```
RayFlow Bridge Status
─────────────────────

Art-Net
  Target:    127.0.0.1
  Port:      6454
  Universe:  0
  Status:    Ready

sACN
  Universe:  1
  Multicast: off
  Source:    RayFlow
  Status:    Ready
```

---

## 4. Error Model

All errors surface through Typer's exception handling with user-friendly messages. No stack traces in normal operation.

| Error | Trigger | CLI Behavior |
|-------|---------|--------------|
| Invalid channel | channel < 1 or channel > 512 | Exit code 2, message: "Channel must be 1-512" |
| Invalid value | value < 0 or value > 255 | Exit code 2, message: "Value must be 0-255" |
| Invalid universe | universe out of protocol range | Exit code 2, message: "Universe must be 0-15 (Art-Net) or 1-63999 (sACN)" |
| Network unreachable | DNS failure, no route to host | Exit code 1, message: "Cannot reach {ip}:{port}" |
| Port in use | Address already bound | Exit code 1, message: "Port {port} in use — stop other Art-Net/sACN tools" |
| Protocol unknown | not "artnet" or "sacn" | Exit code 2, message: "Unknown protocol: {name}. Use artnet or sacn" |

---

## 5. Integration Points

```
┌──────────────┐      ┌──────────────────┐      ┌──────────────────┐
│   CLI (Typer)│─────►│  Bridge Layer     │─────►│  Network (UDP)   │
│   cli.py     │      │  artnet.py        │      │  Port 6454       │
│              │      │  sacn_bridge.py   │      │  grandMA3 onPC   │
│              │─────►│  config.py        │      │  Web Visualizer  │
│              │      │  (env vars)       │      │  Wireshark       │
└──────────────┘      └──────────────────┘      └──────────────────┘
         │
         │ (Phase 3+)
         ▼
  ┌──────────────┐
  │  DmxUniverse │
  │  (patch.py)  │
  └──────────────┘
```

- **CLI → Bridge**: Direct instantiation. `send_dmx()` creates `ArtNetSender` or `SacnSender`.
- **Bridge → Network**: Wrapped library handles UDP socket creation and packet formatting.
- **Config → Bridge**: `Settings.from_env()` reads `ARTNET_TARGET`, `ARTNET_PORT`, `ARTNET_UNIVERSE`, `SACN_UNIVERSE`, `SACN_MULTICAST` from environment.
- **DmxUniverse → Bridge** (Phase 3+): When sending full universe data, a `DmxUniverse` instance provides the channel map.

---

## 6. Updated System Diagram (Phase 2)

```mermaid
graph TD
    CLI[RayFlow CLI]

    subgraph "Bridge Layer (Phase 2)"
        AN[Art-Net Sender/Receiver]
        SN[sACN Sender/Receiver]
        DMX[DmxUniverse Model]
    end

    subgraph "External"
        MA3[grandMA3 onPC]
        VIZ[Web Visualizer (Phase 5)]
        WIRE[Wireshark Verification]
    end

    CLI -->|send| AN
    CLI -->|send| SN
    CLI -->|recv| AN
    CLI -->|recv| SN

    AN -->|ArtDMX UDP 6454| MA3
    AN -->|ArtDMX UDP 6454| VIZ
    SN -->|sACN E1.31| MA3
    SN -->|sACN E1.31| VIZ

    DMX -->|channel map| CLI
    DMX -->|patch data| AN
    DMX -->|patch data| SN

    MA3 -->|receives DMX| MA3_V[MA3 3D Visualizer]
```

---

## 7. Testing Strategy

### 7.1 Unit Tests (mocked network)

- `test_artnet_send_single_channel`: Verify `set_channel()` call reaches `stupidArtnet.set_single_value()`
- `test_artnet_set_channels`: Verify dict dispatch
- `test_sacn_set_channels`: Verify `sacn` library DMX data update
- `test_sacn_multicast_mode`: Verify multicast flag is set on output
- `test_artnet_receiver_buffer`: Verify buffer retrieval from mock server

### 7.2 Input Validation Tests

- `test_send_channel_zero_raises`: Channel 0 is invalid
- `test_send_channel_513_raises`: Channel > 512 is invalid
- `test_send_value_256_raises`: Value > 255 is invalid
- `test_send_value_negative_raises`: Negative values invalid
- `test_send_invalid_protocol`: Unknown protocol name

### 7.3 Integration Tests

- `test_cli_creates_artnet_sender`: Verify the CLI correctly instantiates ArtNetSender
- `test_cli_creates_sacn_sender`: Verify the CLI correctly instantiates SacnSender
- `test_cli_fails_on_bad_protocol`: Verify graceful error for bad protocol flag

### 7.4 Manual Verification (requires grandMA3 onPC)

- Send a DMX value and observe fixture movement in MA3 3D visualizer
- Capture ArtDMX packet with Wireshark, decode header and payload
- Verify sequence number increments across multiple sends

---

## 8. Files To Modify

| File | Change |
|------|--------|
| `src/rayflow/cli.py` | Rewrite `send_dmx()` to use real bridge classes; add `recv`, `status` commands; add input validation |
| `src/rayflow/bridge/artnet.py` | Add input validation to `set_channel()` (channel 1-512, value 0-255) |
| `src/rayflow/bridge/sacn_bridge.py` | Add input validation to `set_channels()` |
| `src/rayflow/bridge/__init__.py` | Export sender/receiver classes |
| `tests/conftest.py` | Remove `vibe_coding` reference; add bridge-specific fixtures |
| `tests/test_bridge.py` | New file: functional bridge tests |
| `tests/test_cli.py` | New file: CLI integration tests |
| `tests/fixtures/` | Remove template fixtures (`sample_*`) |
| `CHANGELOG.md` | Replace template changelog with RayFlow history |

---

## 9. Files NOT To Modify (Phase 2)

- `fixtures/patch.py` — DmxUniverse model stays as-is; used in Phase 3
- `fixtures/library.py` — no bridge dependency
- `console/osc.py` — Phase 4 concern
- `visualizer/__init__.py` — Phase 5 concern
- `config.py` — already loads env vars correctly; only used as-is by CLI

---

## 10. Risks

| Risk | Probability | Mitigation |
|------|-------------|------------|
| `stupidArtnet` library is unmaintained | Medium | Wrappers make it easy to replace with raw socket implementation if needed |
| `sacn` library API changes | Low | Pinned version in pyproject.toml |
| sACN multicast blocked on local network | Low | Default to unicast; multicast is opt-in |
| Art-Net universe numbering confusion (0-based vs 1-based) | Medium | Document in CLI help text; accept both and warn |
