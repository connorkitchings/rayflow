# Building a Rig — Create a Virtual Stage

This guide walks through creating a virtual stage with GDTF fixtures that you can import into grandMA3 onPC.

## Prerequisites

- grandMA3 onPC installed and running
- RayFlow installed with lighting extras
- Basic understanding of DMX addressing (see [Glossary](../glossary.md))

## Rig-Build Musts

Every RayFlow rig build must produce enough visual context for review before cue
authoring starts:

- A named venue shape with dimensions in meters.
- Fixture roles by family: front/key wash, backlight/wash, texture/beam/effect,
  and any specials.
- A patch plan with universe and start address for every fixture.
- A top plot showing `x` versus `y` placement.
- A front plot showing `x` versus `z` trim/height placement.
- A fixture index tying plot numbers to labels, fixture types, roles, and patch.
- A short inspiration note that says whether the rig is based on a real LD/show,
  a genre reference, or a purely original concept.

For an existing rig, generate review artifacts with:

```bash
uv run rayflow rig plot "My Rig" --dir data/rigs --output-dir exports/plots/my_rig
```

## Step 1: Choose Your Fixtures

Browse [gdtf-share.com](https://www.gdtf-share.com/) for fixtures. Good starting fixtures:

- **LED PAR** — Simple, few channels, great for learning
- **Moving Head** — Pan/tilt, color, gobo — more complex but visually impressive
- **Hazer/Fog** — Atmospheric effect, adds depth to the visualizer
- **Blinder/Strobe** — High-impact effect for dynamic moments

Download the `.gdtf.zip` files and place them in `data/fixtures/`.

RayFlow also includes a small checked-in sample pack for development:

```bash
uv run rayflow fixture list --dir data/fixtures/samples
uv run rayflow fixture info "LED PAR" --dir data/fixtures/samples
```

## Step 2: Load Fixtures into RayFlow

```python
from rayflow.engine.fixtures.parser import GdtfParser

parser = GdtfParser("data/fixtures/chauvet_dj_slimpar_pro_h_usb.gdtf.zip")
fixture = parser.parse()

print(f"Fixture: {fixture.name}")
print(f"Manufacturer: {fixture.manufacturer}")
print(f"DMX Mode: {fixture.dmx_mode}")
print(f"Channels: {fixture.channel_count}")
```

## Step 3: Plan Your DMX Addresses

Each fixture needs a starting DMX address. Plan carefully to avoid overlaps:

| Fixture | Channels | Start Address | End Address |
|---------|----------|---------------|-------------|
| LED PAR 1 | 4 | 1 | 4 |
| LED PAR 2 | 4 | 5 | 8 |
| LED PAR 3 | 4 | 9 | 12 |
| LED PAR 4 | 4 | 13 | 16 |
| Moving Head 1 | 16 | 17 | 32 |
| Moving Head 2 | 16 | 33 | 48 |
| Hazer | 1 | 49 | 49 |

Total: 49 channels used in Universe 1.

## Step 4: Create the Rig

```python
from rayflow.engine.fixtures.library import FixtureLibrary
from rayflow.engine.fixtures.patch import DmxUniverse

library = FixtureLibrary("data/fixtures/samples")
library.load()

universe = DmxUniverse(universe_number=0)
universe.patch_fixture(library.get("LED PAR"), address=1)
universe.patch_fixture(library.get("LED PAR"), address=5)
universe.patch_fixture(library.get("LED PAR"), address=9)
universe.patch_fixture(library.get("LED PAR"), address=13)
universe.patch_fixture(library.get("Moving Head"), address=17)
universe.patch_fixture(library.get("Moving Head"), address=33)
universe.patch_fixture(library.get("Hazer"), address=49)

print(f"Universe 0: {universe.used_channels}/512 channels used")
```

## Step 5: Arrange Fixtures in 3D Space

Define positions for each fixture on your virtual stage:

```python
from rayflow.engine.fixtures.mvr_export import FixturePosition

positions = [
    FixturePosition("LED PAR 1", x=-3, y=3, z=0, pan=0, tilt=90),
    FixturePosition("LED PAR 2", x=-1, y=3, z=0, pan=0, tilt=90),
    FixturePosition("LED PAR 3", x=1, y=3, z=0, pan=0, tilt=90),
    FixturePosition("LED PAR 4", x=3, y=3, z=0, pan=0, tilt=90),
    FixturePosition("Moving Head 1", x=-2, y=0, z=2, pan=0, tilt=0),
    FixturePosition("Moving Head 2", x=2, y=0, z=2, pan=0, tilt=0),
    FixturePosition("Hazer", x=0, y=4, z=-2, pan=0, tilt=0),
]
```

Coordinates:
- **X:** Left (-) to right (+) in meters
- **Y:** Height from floor in meters
- **Z:** Front (+) to back (-) in meters
- **Pan/Tilt:** Default orientation in degrees

## Step 6: Export as MVR

```python
from rayflow.engine.fixtures.mvr_export import export_mvr

export_mvr(universe, positions, output_path="data/shows/my_first_rig.mvr")
```

## Step 7: Import to grandMA3 onPC

1. In grandMA3 onPC, go to **Import** → **MVR**
2. Select `data/shows/my_first_rig.mvr`
3. The fixtures will appear in the 3D visualizer at their positions
4. Verify all fixtures are patched correctly

## Step 8: Test the Rig

```bash
# Light all PARs to full
uv run rayflow bridge send --universe 0 --channel 1 --value 255
uv run rayflow bridge send --universe 0 --channel 5 --value 255
uv run rayflow bridge send --universe 0 --channel 9 --value 255
uv run rayflow bridge send --universe 0 --channel 13 --value 255

# Move the first moving head
uv run rayflow bridge send --universe 0 --channel 17 --value 128
uv run rayflow bridge send --universe 0 --channel 18 --value 64
```

## Tips for Building Rigs

- **Start simple:** 4 PARs and 1 moving head is enough to learn
- **Think about the song:** What kind of lighting does the music need?
- **Symmetry helps:** Evenly spaced fixtures are easier to program
- **Height matters:** Fixtures at different heights create depth
- **Save your work:** Keep rig configs in `data/shows/` for reuse

## Next Steps

- **[Recording a Show](./recording-a-show.md)** — Program cues for a song and export video
- **[grandMA3 Setup](./grandma3-setup.md)** — Learn more about the console
