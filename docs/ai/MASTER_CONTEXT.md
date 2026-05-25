# AI Master Context — grandMA3 Compatibility Track

> **FOR AI AGENTS.** This document is the entry point for sessions involving
> grandMA3 onPC compatibility work. For backend-neutral RayFlow direction, read
> `docs/architecture/control-backend-direction.md` first.

---

## Project Goal

**Build lighting shows for recorded songs.** RayFlow owns the show and rig
intent. grandMA3 onPC 2.3.2.0 is a professional compatibility target for MVR,
Timecode XML, review bundles, and gated OSC operations. The human user is not
expected to learn MA3 separately, but agents must not treat MA3 mutation as the
mainline execution path unless the operation has evidence.

## Version Baseline

**grandMA3 onPC 2.3.2.0** on macOS (`/Applications/grandMA3.app`).

To verify the installed version, see the canonical command in
[grandMA3 Setup Guide](../guides/grandma3-setup.md).

All GUI paths, CLI syntax, and protocol behavior in these docs should be sourced
from the **grandMA3 2.3 online manual** and verified against 2.3.2.0 before
being used for live mutation.

## Document Map

| Document | Purpose | When to Read |
|----------|---------|--------------|
| **MASTER_CONTEXT.md** (this file) | Entry point, conventions, quick map | Start of every session |
| [MA3_OPERATIONS.md](./MA3_OPERATIONS.md) | Every MA3 operation: GUI path + CLI + OSC/RayFlow | When you need to DO something in MA3 |
| [MA3_COMMAND_REFERENCE.md](./MA3_COMMAND_REFERENCE.md) | Complete CLI syntax reference | When you need exact command syntax |
| [SHOW_BUILDING_WORKFLOW.md](./SHOW_BUILDING_WORKFLOW.md) | End-to-end process: song → finished show | When starting a new show build |
| [FIXTURE_ECOSYSTEM.md](./FIXTURE_ECOSYSTEM.md) | GDTF fixtures, sources, channel families | When working with fixtures |
| **Knowledge Base** | [`../knowledge_base.md`](../knowledge_base.md) | Protocol details, discovered patterns |
| **MA3 Setup Guide** | [`../guides/grandma3-setup.md`](../guides/grandma3-setup.md) | First-time setup, network config |
| **MA3 Learning Resources** | [`../guides/grandma3-learning-resources.md`](../guides/grandma3-learning-resources.md) | External references, YouTube tutorials |

## How to Read These Docs

### GUI Paths
Format: `Menu → Submenu → Item → [Specific Button/Field]`
- `→` means "navigate to"
- `[Tap]` means tap/press the named button
- `[Select]` means select/tap the named item
- All paths verified against MA3 2.3.2.0

### CLI Commands
Format: `Keyword Argument1 Thru Argument2 At Value`
- Commands are typed into the MA3 command line (press `.` to open)
- `Please` executes the command (may be shown explicitly or implied)
- Case-insensitive, but we capitalize keywords for readability
- Shortcuts exist (e.g., `S` for Store, `C` for Cue, `Seq` for Sequence)
- Text with spaces/names must be quoted: `Store Cue "My Look"`

### OSC/RayFlow
Format: `client.send("Command String")` or `rayflow bridge send ...`
- Python code paths or CLI commands for RayFlow integration
- OSC commands go to MA3 port 8000 via `/cmd` endpoint
- Art-Net DMX goes to MA3 port 6454

### Verification
Every operation includes verification: how to confirm it worked.
- Look for `Verify:` or `Expected result:`
- When possible, verify with both GUI (visualizer) and network tools (tcpdump)

## Quick Reference Map

| I need to... | Read... | Key command/tool |
|-------------|---------|-----------------|
| Start a new show | MA3_OPERATIONS § Show Management | `Menu → New Show` |
| Patch fixtures | MA3_OPERATIONS § Patching, FIXTURE_ECOSYSTEM | `Fixture 4 "LED PAR" At Address 1` |
| Create groups | MA3_OPERATIONS § Groups & Presets | `Group 1` then `Store Group 1` |
| Set fixture values | MA3_OPERATIONS § Programming | `Fixture 1 At 50`, `Full`, `Zero` |
| Store a cue | MA3_OPERATIONS § Programming | `Store Cue 1` or `Store` + executor key |
| Set fade times | MA3_OPERATIONS § Timing | `Cue 1 Time 3 Please` |
| Create a chase | MA3_OPERATIONS § Effects Engine | `MA + Next`, set values, `Store` |
| Play back show | MA3_OPERATIONS § Playback | `Go+`, `Pause`, `Goto Cue 5` |
| Record to video | MA3_OPERATIONS § Recording & Export | `Menu → Recording → Screen Capture` |
| Send DMX from Python | Knowledge Base § ArtNetPacket | `rayflow bridge send -c 1 -v 255` |
| Configure Art-Net | MA3_OPERATIONS § Network Protocols | `Menu → DMX Protocols → Art-Net` |
| Enable OSC | MA3_OPERATIONS § Network Protocols | `Menu → In & Out → OSC` |

## Conventions

### Fixture Selection
- `Fixture 1 Thru 5` — select fixtures 1 through 5
- `Fixture 1 Thru 10 - 6 Thru 8` — select 1-5 + 9-10 (exclude 6-8)
- `Fixture 1 + 5 + 9` — add specific fixtures
- `Fixture Thru` — select all fixtures

### Value Entry
- `At 50` — set intensity to 50% (preset type defaults to Dimmer)
- `Full` — 100%
- `Zero` — 0%
- `At 3 0` — set value to 30 (two digits for 30)

### The Programmer (Critical Concept)
The programmer is MA3's **temporary working buffer**. Values go here first, then you store them:
1. Select fixtures → values appear in programmer (temporary)
2. `Store Cue 1` → values are committed to cue 1
3. `Clear` → programmer is cleared (cue remains)

**Clear levels:**
- 1st press: Deselect fixtures (values STILL active — can still store)
- 2nd press: Deactivate values (storing produces empty cue)
- 3rd press: Full clear
- Hold Clear (≥1 sec): Full clear immediately

## Integration: RayFlow ↔ MA3

| Operation | Use RayFlow When | Use MA3 Directly When |
|-----------|-----------------|----------------------|
| Patch fixtures | Testing address math, exports, compatibility probes | Interactive GUI setup |
| Send DMX values | Scripts, renderer tests, direct Art-Net/sACN output | Real-time manual operation |
| Inspect fixtures | `rayflow fixture list/info` from CLI | Need to see 3D model |
| Store cues | Gated OSC for verified dimmer/sequence paths | Live manual programming |
| Playback | OSC `go_sequence()` | Physical control or live operation |
| 3D visualization | Backend-dependent; future visualizer possible | MA3 built-in visualizer for compatibility review |

## Known Limitations & Rules

1. **`.show` files are binary** — Do NOT propose generating `.show` files. They cannot be created outside MA3.
2. **Evidence-first** — Prefer RayFlow CLI, exported artifacts, packet capture, queryable state, or recorded manual confirmation over assuming MA3 accepted a command.
3. **Verify version first** — Before giving MA3 UI instructions, confirm the installed version is 2.3.2.0.
4. **Art-Net input not default** — Must be manually enabled per show (one-time).
5. **OSC bundles not supported** — Only individual OSC messages. No batch sending.
6. **sACN multicast input limited to 20 universes**.
7. **Combined Art-Net + sACN input limited to 128 universes**.
8. **MA3 is a compatibility adapter** — Do not block backend-neutral renderer work on MA3 fixture import or readback.

## Session Startup Checklist (for AI Agents)

Before any MA3 compatibility session:
- [ ] Read this MASTER_CONTEXT.md
- [ ] Verify MA3 2.3.2.0 is installed: `PlistBuddy -c 'Print :CFBundleVersion' /Applications/grandMA3.app/Contents/Info.plist`
- [ ] Check if MA3 onPC is running (and which show is loaded)
- [ ] Verify network setup (Art-Net/OSC enabled for the current show)
- [ ] Confirm the target operation is part of the MA3 compatibility track, not the backend-neutral renderer milestone
- [ ] Read [MA3_OPERATIONS.md](./MA3_OPERATIONS.md) section for your first task
- [ ] Read [SHOW_BUILDING_WORKFLOW.md](./SHOW_BUILDING_WORKFLOW.md) if building a complete show

## Links

- **MA3 2.3 Online Manual**: https://help.malighting.com/grandMA3/2.3/HTML/index.html
- **MA Lighting Downloads**: https://www.malighting.com/downloads/products/grandma3/
- **MA Lighting Video Tutorials**: https://www.malighting.com/ma-university/video-tutorials/
- **GDTF Share**: https://gdtf-share.com/
- **YouTube**: https://www.youtube.com/results?search_query=grandma+onpc+tutorial
- **YouTube Playlist**: https://www.youtube.com/watch?v=TRYe5c2KVAw&list=PLBtvj74f8NI_aIpHpAf7QWbFbV0zeeu7a
