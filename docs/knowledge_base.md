# Knowledge Base

This document is a curated collection of reusable patterns, protocol specifications, and insights discovered during RayFlow development.

Use the format `[KB:PatternName]` to reference entries from other documents.

---

## `[KB:ArtNetPacket]` — Art-Net ArtDMX Packet Structure

- **Context:** Building Art-Net packets to send DMX values over UDP.
- **Pattern:**
  ```
  Header: "Art-Net" (8 bytes) + 0x00 (1 byte)
  Opcode: 0x5000 (ArtDMX, little-endian: 0x00, 0x50)
  Protocol Version: 14 (2 bytes, big-endian)
  Sequence: Incrementing counter (1 byte, prevents duplicate processing)
  Physical: Port number (1 byte, usually 0)
  Universe: Low byte + High byte (2 bytes)
  Length: High byte + Low byte (2 bytes, typically 0x02, 0x00 for 512)
  Data: 512 bytes of DMX values
  ```
- **Usage:** Construct byte array, send via UDP to port 6454.
- **Note:** Art-Net uses little-endian for opcode, big-endian for protocol version.

## `[KB:sACNMulticast]` — sACN Multicast Addressing

- **Context:** sACN uses multicast for efficient multi-receiver distribution.
- **Pattern:** Multicast address = `239.255.<universe_high>.<universe_low>`
  - Universe 1 → `239.255.0.1`
  - Universe 512 → `239.255.2.0`
- **Usage:** Join multicast group, send/receive on that address.
- **Note:** sACN also supports unicast for point-to-point communication.

## `[KB:GDTFStructure]` — GDTF File Format

- **Context:** Parsing GDTF fixture files (.gdtf.zip archives).
- **Pattern:** A .gdtf.zip contains:
  - `description.xml` — Main fixture definition (channels, modes, wheels, physical)
  - `Icons/` — Thumbnail and icon images
  - `Profiles/` — Photometric data (IES files)
  - `Resources/` — Additional assets
- **Usage:** Validate the ZIP archive, then parse `description.xml`.
- **Note:** GDTF supports multiple DMX modes per fixture (8-bit, 16-bit, etc.).

## `[KB:GDTFSampleManifest]` — Checked-In Fixture Sample Baseline

- **Context:** Phase 3 channel mapping needs real fixture files, but GDTF Share API downloads require an authenticated user session.
- **Pattern:** Keep a small offline sample pack in `data/fixtures/samples/` with `manifest.json` entries for source URL, SHA-256, expected modes, minimum channel counts, and expected attributes.
- **Usage:** Tests load every manifest entry through `GdtfParser`, `FixtureLibrary`, and fixture CLI commands. Add future samples by copying the `.gdtf` file and extending the manifest.
- **Note:** GDTF Share remains the preferred production source. Public open-source samples are used here for reproducible tests without credentials.

## `[KB:GDTFChannelMap]` — GDTF Mode to DMX Address Mapping

- **Context:** Turning a parsed GDTF DMX mode into concrete fixture channel addresses for future patching.
- **Pattern:** Use `GdtfParser.get_channel_map(mode_name=..., start_address=..., universe=...)` to produce ordered entries with fixture name, mode name, universe, 1-based DMX address, relative channel, original attribute, normalized attribute, family, geometry, break, default, highlight, and resolution.
- **Usage:** Validate `start_address` is `1..512` and `start_address + channel_count - 1 <= 512` before patching.
- **Note:** Fine channels preserve the original leading `+` attribute, but family classification strips it so `Pan` and `+Pan` both classify as `position`.

## `[KB:OSCCommand]` — grandMA3 OSC Command Format

- **Context:** Sending commands to grandMA3 onPC via OSC.
- **Pattern:**
  - Endpoint: `/cmd`
  - Argument: String containing MA3 command
  - Example: OSC message to `/cmd` with argument `"Store Cue 1"`
- **Common Commands:**
  - `Store Cue <n>` — Store programmer state as cue
  - `Go Sequence <n>` — Execute sequence
  - `At <value>` — Set intensity
  - `Channel <n> Thru <m> At Full` — Set channels
  - `About` — Get console info (good for connection test)
- **Note:** Default OSC port is 8000. For grandMA3 2.3, the receive row must allow command-line control through `/cmd` with OSC string type `s`. MA3 OSC is now treated as a compatibility adapter, not RayFlow's core execution loop.

## `[KB:BackendNeutralControl]` — RayFlow Source Of Truth And Adapter Boundary

- **Context:** MA3 live probes showed that raw console mutation is too fragile to be the main agent loop.
- **Pattern:** Keep show/rig/cue data as RayFlow's source of truth. Resolve fixture capabilities and render intent into deterministic output artifacts. Backends then translate those artifacts to Art-Net, sACN, QLC+ WebSockets, MA3 export files, or gated MA3 OSC.
- **Usage:** New output features should define dry-run, apply, evidence, and capability reporting. Do not claim a backend operation works until it returns structured evidence, captured DMX frames, exported artifacts, or recorded manual confirmation.
- **Note:** See `docs/architecture/control-backend-direction.md` and `docs/research/agentic_show_control_architectures/`.

## `[KB:DMXAddressing]` — DMX Address Calculation

- **Context:** Calculating DMX addresses when patching fixtures.
- **Pattern:**
  - Fixture start address + channel count = next available address
  - Address 1 + 16 channels = next fixture starts at address 17
  - Max address per universe = 512
  - If start + channels > 512, fixture spans to next universe
- **Usage:** Always validate: `start_address + channel_count - 1 <= 512`
- **Note:** DMX addresses are 1-based (1-512), array indices are 0-based (0-511).

## `[KB:16BitChannels]` — 16-Bit Channel Resolution

- **Context:** Some fixtures use 16-bit resolution for fine control (pan, tilt).
- **Pattern:** 16-bit channel uses 2 DMX addresses:
  - Coarse (MSB): Primary value (0-255)
  - Fine (LSB): Fine adjustment (0-255)
  - Combined value = (coarse * 256) + fine (0-65535)
- **Usage:** When patching, allocate 2 addresses per 16-bit channel.
- **Note:** grandMA3 handles 16-bit automatically if GDTF defines it.

## `[KB:MVRExport]` — MVR File Generation

- **Context:** Creating MVR files for import to grandMA3 visualizer.
- **Pattern:** MVR is a ZIP containing:
  - `myvirtualrig.xml` — Stage geometry, fixture positions, truss data
  - GDTF references — Links to fixture definitions
- **Usage:** Generate XML from fixture patch data, package as .mvr.zip.
- **Note:** MVR is based on GDTF and supported by most modern visualizers.

---

*Add new entries as patterns are discovered during development.*

## `[KB:stupidArtnetShow]` — stupidArtnet Requires Explicit show() Call

- **Context:** The `stupidArtnet` library buffers DMX values but does not send them until `show()` is called.
- **Pattern:** Every setter (`set_single_value`, `set_rgb`, etc.) only writes to an internal buffer. `show()` constructs the ArtDMX packet and sends it via UDP. Without `show()`, no packets leave the machine.
- **Usage:** Always call `self._client.show()` after any buffer modification in a one-shot send.
- **Note:** `start()` calls `show()` once then recurses in a thread for persistent streaming.

## `[KB:stupidArtnetServerAPI]` — StupidArtnetServer Uses Register Pattern

- **Context:** The `StupidArtnetServer` constructor only takes a port number. Universe filtering uses `register_listener()`.
- **Pattern:**
  ```python
  server = StupidArtnetServer()  # binds to port 6454
  listener_id = server.register_listener(universe=0, callback_function=cb)
  buffer = server.get_buffer(listener_id)
  ```
- **Usage:** Do NOT pass universe or callback to the constructor. Use `register_listener()` with `universe`, `sub`, `net`, `is_simplified`, and `callback_function`.
- **Note:** The `get_buffer()` method requires a listener ID, not a universe number.

## `[KB:ArtNetUniverseMapping]` — Art-Net Universe Mapping in grandMA3

- **Context:** grandMA3 onPC displays universes as 1-based but Art-Net uses 0-based universe addressing.
- **Pattern:** In MA3's Art-Net settings, "Local Universe 1" may map to Art-Net universe 0 or 1 depending on configuration. Test both if packets don't arrive.
- **Usage:** Brute-force test: send to Art-Net universes 0-15, watch for fixture response.
- **Note:** MA3 uses "net:subnet:universe" addressing. With default simplified mode, Art-Net universe 0 = net 0, subnet 0, universe 0. MA3 may display this as "1.0" or "1:1" depending on version.

## `[KB:MA3ArtNetEnable]` — Enabling Art-Net Input in grandMA3 onPC

- **Context:** Art-Net input is NOT safe to assume enabled by default in grandMA3 onPC 2.3.2.0.
- **Pattern:** In the Art-Net menu, create or enable an input row for the target local universe. Verify with `lsof -iUDP:6454` that MA3 is listening.
- **Usage:** One-time configuration per show file. Saved with the show.
- **Note:** The process name is `app_gma3`. After enabling, `lsof -iUDP:6454` should show it listening on `*:6454`.

## `[KB:MA3VersionBaseline]` — grandMA3 Version-Specific Guidance

- **Context:** grandMA3 UI paths and network behavior can shift between releases, and stale instructions caused bad session guidance.
- **Pattern:** Verify the installed app before giving UI instructions:
  ```bash
  /usr/libexec/PlistBuddy -c 'Print :CFBundleVersion' /Applications/grandMA3.app/Contents/Info.plist
  ```
- **Usage:** Current RayFlow baseline is grandMA3 onPC 2.3.2.0. Use MA's 2.3 manual pages for OSC, Art-Net, fixture import/export, and GDTF workflows.
- **Note:** Use video tutorials for conceptual learning, then verify exact menu paths against the matching manual or installed app.
