# GDTF Fixture Ecosystem

> **FOR AI AGENTS.** Everything about GDTF fixtures: what they are, where to find them, how to inspect them, how MA3 handles them, and how RayFlow integrates.

---

## What is GDTF?

**General Device Type Format (GDTF)** is an open standard (DIN SPEC 15800:2022) for describing lighting fixtures. A GDTF file is a `.zip` archive containing:

```
fixture.gdtf.zip
├── description.xml       # Main fixture definition (channels, modes, physical properties)
├── Icons/                # Thumbnail and icon images
├── Profiles/             # Photometric data (IES files)
├── Resources/            # Gobo images, additional assets
└── geometries/           # 3D geometry data
```

The `description.xml` defines:
- **Manufacturer** and **Fixture Name**
- **DMX Modes** (different channel configurations — 8-bit, 16-bit, etc.)
- **DMX Channels** within each mode (dimmer, pan, tilt, color, gobo, etc.)
- **Geometry** tree (physical dimensions, beam angles, sub-fixtures)
- **Wheels** (color wheels, gobo wheels with slot definitions)

## Where to Find Fixtures

| Source | URL | Notes |
|--------|-----|-------|
| **GDTF Share** | https://gdtf-share.com/ | Primary source. Free, open library. |
| **GDTF Builder** | https://fixturebuilder.gdtf-share.com/ | Build custom fixtures |
| **MA Lighting** | https://www.malighting.com/ | Official MA fixture library |
| **Manufacturer sites** | Chauvet, Martin, Robe, etc. | May provide `.gdtf` downloads |

### GDTF Share API
GDTF Share has a search API but requires a user session for download. For offline/automated use, download samples manually and store them in `data/fixtures/`.

### MA3 World Server (GDTF Share in MA3)
MA3 can directly access GDTF Share via World Server:
1. Ensure World Server connection (Menu → Network)
2. Open Fixture Types → Import
3. Enable **Share** toggle (![Share])
4. Browse by Manufacturer → Fixture → Mode
5. Tap **Import**

---

## Channel Families

GDTF classifies every DMX channel into a family. Understanding these helps with patching, effects, and color management.

| Family | Description | Examples |
|--------|-------------|----------|
| **Dimmer** | Intensity control | Dimmer, Shutter, Strobe |
| **Color** | Color mixing | Red, Green, Blue, Cyan, Magenta, Yellow, Color Wheel |
| **Position** | Movement | Pan, Tilt, Pan Fine, Tilt Fine |
| **Gobo** | Pattern projection | Gobo Wheel, Gobo Rotation, Gobo Index |
| **Beam** | Shape and focus | Focus, Zoom, Iris, Frost |
| **Effect** | Built-in effects | Prism, Effect Wheel, Macro |
| **Control** | Fixture control | Reset, Lamp Control, Dimmer Curve |
| **Custom** | Manufacturer-specific | Any unmapped channel |

### 8-Bit vs 16-Bit Channels

A 16-bit channel uses **two DMX addresses** for fine control:
- **Coarse (MSB)**: Primary value (0-255)
- **Fine (LSB)**: Sub-value (0-255)
- **Combined value** = (coarse × 256) + fine = 0-65535

**Common 16-bit channels:** Pan, Tilt, Zoom
**Rare 16-bit channels:** Dimmer, Color mixing

In MA3, 16-bit is handled automatically if GDTF defines the Fine channel. The combined range is 0-65535 displayed as 0-100% with decimals.

---

## Using RayFlow to Inspect Fixtures

### CLI Commands

```bash
# List all fixtures in data/fixtures/
uv run rayflow fixture list

# Inspect a specific fixture (partial name match)
uv run rayflow fixture info "LED PAR"

# Search fixtures
uv run rayflow fixture search "Chauvet"
```

### Python API

```python
from rayflow.engine.fixtures.parser import GdtfParser
from rayflow.engine.fixtures.library import FixtureLibrary

# Parse a single fixture
parser = GdtfParser("data/fixtures/chauvet_slimpar_pro_h.gdtf.zip")
fixture = parser.parse()
print(f"Name: {fixture.manufacturer} - {fixture.name}")
print(f"DMX Modes: {len(fixture.modes)}")
for mode in fixture.modes:
    print(f"  {mode.name}: {mode.channel_count} channels")

# Get channel definitions for a mode
channels = parser.get_channel_map(mode_name="Default", start_address=1)
for ch in channels:
    print(f"  Ch {ch['address']:3d}: {ch['attribute']:20s} [{ch['family']}]")

# Load entire library
library = FixtureLibrary()
library.load("data/fixtures/")
library.list_fixtures()  # Show all loaded fixtures
matching = library.search("moving")  # Search by query
fixture_entry = library.get("LED PAR")  # Get by name match

# DMX addressing
from rayflow.engine.fixtures.patch import DmxUniverse
universe = DmxUniverse(1)
universe.patch("LED PAR 1", start_address=1, channel_count=7)
universe.patch("LED PAR 2", start_address=8, channel_count=7)
print(f"Used channels: {universe.used_channels}")
print(f"First free address: {universe.next_free()}")
```

---

## Common Fixture Categories

### LED PAR / Wash
**Channels:** 4-10
**Typical layout:** Dimmer, Red, Green, Blue, (White/Amber/UV), Strobe, Color Macro
**Use:** General wash lighting, color washes, stage illumination
**Example GDTF:** Chauvet SlimPAR Pro H USB, Martin Rush PAR 2

### Moving Head (Spot)
**Channels:** 12-24
**Typical layout:** Pan, Pan Fine, Tilt, Tilt Fine, Dimmer, Shutter, Red, Green, Blue, White/Amber, Color Wheel, Gobo Wheel, Gobo Rotation, Prism, Focus, Zoom, Control, Reset
**Use:** Position effects, gobo projection, spotlighting
**Example GDTF:** MAC Aura XB, Robe LEDBeam 150

### Moving Head (Beam)
**Channels:** 10-20
**Typical layout:** Pan, Pan Fine, Tilt, Tilt Fine, Dimmer, Shutter, Color Wheel, Gobo Wheel, Prism, Focus, Control
**Use:** Narrow beams, aerial effects, high-speed movement
**Example GDTF:** Claypaky Sharpy, Martin MAC 250 Beam

### LED Bar / Striplight
**Channels:** 8-48 (depends on pixel count)
**Typical layout:** Multi-instance — each pixel has Dimmer, R, G, B (+ optional W/A/UV)
**Use:** Wall washing, eye candy, pixel mapping
**Example GDTF:** Chauvet COLORado Batten, Martin VDO Atomic

### Hazer / Fog / Effect
**Channels:** 1-4
**Typical layout:** Haze/Fog Output, Fan Speed, Control
**Use:** Atmospheric effects, beam visibility
**Example GDTF:** Generic Hazer (in MA3 Generic library)

### Strobe / Blinder
**Channels:** 2-6
**Typical layout:** Dimmer, Strobe Rate, Strobe Duration, Control
**Use:** High-impact momentary effects (crowd blinders, strobe)
**Example GDTF:** Martin Atomic 3000, Generic Strobe

---

## MA3 Fixture Type Management

### Fixture Type Sources in MA3

| Source | Description | Access |
|--------|-------------|--------|
| **MA Library** | Built-in grandMA3 + converted grandMA2 fixtures | Patch → Insert → Library → MA |
| **User Library** | Custom-imported fixtures | Patch → Insert → Library → User |
| **GDTF Share** | Online GDTF library (via World Server) | Patch → Import → Share toggle |
| **USB** | Local `.gdtf` files from USB drive | USB at `grandMA3/gma3_library/fixturetypes/` |

### Importing GDTF to MA3

**Method 1: Via World Server (GDTF Share)**
1. Open `Menu → Patch → Fixture Types`
2. Tap **Import**
3. Enable **Share** toggle
4. Browse Manufacturer → Fixture → Mode
5. Tap **Import**

**Method 2: Via USB**
1. Download `.gdtf` from gdtf-share.com
2. Place on USB: `grandMA3/gma3_library/fixturetypes/`
3. Connect USB → Fixture Types → Import → USB drive
4. Select `.gdtf` → Import

**Method 3: Via RayFlow (future Phase 4)**
Planned: Download from GDTF Share, pre-process, and provide import-ready files.

### Fixture Type Versioning
Imported fixture types have a **Version** column showing the minimum grandMA3 version required. Check compatibility when importing older fixtures.

---

## Multi-Mode Fixtures

Many fixtures have multiple DMX modes. For example, an LED PAR might have:

| Mode | Channels | Description |
|------|----------|-------------|
| Basic | 4 | Dimmer, R, G, B (8-bit per color) |
| Standard | 7 | Dimmer, R, G, B, A, Strobe, Macro |
| Extended | 10 | 16-bit dimmer + full color mixing + strobe + macro + control |

**Choosing a mode:** Fewer channels = simpler to program but less control. More channels = finer control but uses more DMX footprint.

In MA3 patch wizard, you select the mode when adding fixtures. To change mode later: Patch Menu → edit the **Mode** column cell.

---

## DMX Address Planning

### Address Calculation
```
Fixture 1: Start address 1, uses 7 channels → range 1-7
Fixture 2: Start address 8, uses 7 channels → range 8-14
Fixture 3: Next free = 15
```

**Rule:** `start_address + channel_count - 1 <= 512` per universe.

### Multi-Universe
If universe 1 fills up (address > 512):
- Next fixture starts at universe 2, address 1
- In MA3: Patch as `2.1` (universe 2, address 1)
- Each universe = 512 channels

### Using RayFlow for Address Math
```python
from rayflow.engine.fixtures.patch import DmxUniverse

u1 = DmxUniverse(1)
u1.patch("PAR 1", 1, 7)    # Addresses 1-7
u1.patch("PAR 2", 8, 7)    # Addresses 8-14
u1.patch("MH 1", 15, 19)   # Addresses 15-33

print(u1.used_channels)     # 33
print(u1.next_free())        # 34

# Conflict detection
try:
    u1.patch("PAR 3", 10, 7)  # Overlaps PAR 2 (8-14)
except ValueError as e:
    print(e)  # "Address overlap: ..."
```

---

## RayFlow Knowledge Base Entries

Reference these KB entries for GDTF details:

| KB Entry | Topic |
|----------|-------|
| `KB:GDTFStructure` | GDTF ZIP archive layout (`description.xml`, profiles, geometry) |
| `KB:GDTFChannelMap` | GDTF mode to DMX address mapping function |
| `KB:GDTFSampleManifest` | Offline fixture sample management with manifest.json |
| `KB:DMXAddressing` | DMX address calculation: start + count - 1 ≤ 512 |
| `KB:16BitChannels` | 16-bit resolution: (coarse × 256) + fine |
| `KB:MVRExport` | MVR file structure for visualizer import |

See `../knowledge_base.md` for full details.

---

## Quick GDTF Cheat Sheet

```bash
# Download and inspect a fixture
wget https://open-fixture-library.org/.../fixture.gdtf  # Or from gdtf-share.com
mv fixture.gdtf data/fixtures/
uv run rayflow fixture info "fixture name"

# List all loaded fixtures
uv run rayflow fixture list

# Check channel requirements
uv run rayflow fixture info "Moving Head" | grep "channels"

# Calculate DMX addresses
python -c "
from rayflow.engine.fixtures.patch import DmxUniverse
u = DmxUniverse(1)
u.patch('PAR 1', 1, 7)
u.patch('PAR 2', 8, 7)
u.patch('MH 1', 15, 19)
print(f'Used: {u.used_channels}/512, Next free: {u.next_free()}')
"
```
