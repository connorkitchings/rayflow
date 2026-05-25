# Reading a Rig: Identifying Fixtures from Photos and Video

**Purpose:** Given concert photos, live streams, or phone videos, identify the lighting rig — fixture types, truss positions, programming patterns — and translate that into a buildable virtual rig.

## How to Read Fixtures from Visuals

### Step 1: Identify Fixture Family

Look at the light source and what it produces:

| What You See | Likely Fixture Family |
|-------------|----------------------|
| Sharp, tight beam shaft through haze (pencil-thin) | Beam moving head (2°–5°) |
| Wider shaft with visible gobo pattern projected on surface | Spot/profile moving head |
| Soft, broad cone of colored light covering an area — no sharp edges | Wash moving head or LED PAR |
| Multi-point bar of colored dots moving in sequence | Pixel bar |
| Intense white flash, brief, aimed at audience | Blinder |
| Rapid flashing, stop-motion effect on performers | Strobe |
| Thin colored line tracing geometric shapes | Laser |

### Step 2: Identify Fixture Housing

Moving head fixtures have recognizable silhouettes. Look for:

| Visual Feature | Suggests |
|---------------|----------|
| Large head, prominent lens barrel, square/rectangular body | Spot/profile (Robe, Martin, Ayrton) |
| Compact head, small lens, often wedge-shaped body | Beam (Clay Paky Sharpy, Robe Pointe) |
| Round/flat face, no protruding lens barrel, often larger body | Wash (Martin MAC Aura, Chauvet Rogue Wash) |
| Twin-lens or quad-lens face, small body | Multi-cell wash / Bee Eye (Martin MAC Aura PXL) |
| Long narrow bar with multiple individual lenses | Pixel bar (GLP Impression X4 Bar) |
| Small rectangular box with single bright LED, often 2 or 4 per unit | Blinder (Martin Atomic, Chauvet STRIKE) |

### Step 3: Count and Map Truss Positions

Look at the overall structure:

| Visual Pattern | Truss Structure |
|---------------|----------------|
| Fixtures in a straight line across the front, above the stage | FOH truss |
| Fixtures in a straight line directly over the stage, parallel to front | Downstage (DS) truss |
| Second or third line of fixtures behind the first, over the stage | Mid truss, Upstage (US) truss |
| Fixtures in vertical columns at the sides of the stage | Booms (Stage Left / Stage Right) |
| Fixtures at stage level, often aimed up or at audience | Floor package |
| Fixtures over the audience, aimed at the crowd | Audience truss |

Count fixtures per position:
- Count the visible beams or light sources in a straight-on photo
- In aerial/high-angle photos, count the physical units on each truss
- In video, freeze-frame on wide shots during bright, all-fixtures-on moments

### Step 4: Identify Programming Patterns

Watch the show and note:

| What You See | Programming Technique |
|-------------|---------------------|
| All fixtures change simultaneously on a beat | Snap cue, no fade |
| Color changes sweep left-to-right across fixtures | Color chase with sequential phase |
| Fixtures all move together in circles | Circle movement effect, synchronized phase |
| Fixtures create a wave motion (one moves, then next, then next) | Movement effect with spread phase |
| Sudden blackout then explosion | Busking contrast pattern |
| Color gradually shifts over 30+ seconds | Slow color crossfade |
| Fixtures strobe on every 4th beat only | Strobe linked to BPM with divider |
| Single fixture follows the lead performer | Followspot or tracked moving head |

### Step 5: Match to Known Fixture Models

Once you know the family and approximate era, narrow down to specific models:

#### Common Spot Moving Heads
| Fixture | Visual Tell | Common On |
|---------|------------|-----------|
| Robe MMX Blade | Large angular head, prominent framing shutter housing | Mid-size to large tours |
| Robe MegaPointe | Compact but powerful, distinctive wedge shape | Large tours, festivals |
| Martin MAC Encore | Rounded body, smooth lines, Martin orange/gray color scheme | Theater, large tours |
| Ayrton Ghibli | Compact, square housing, often black, very bright for size | Mid-size tours |
| Chauvet Maverick MK3 | Angular, modern styling, Chauvet branding visible up close | Mid-size, club tours |
| Elation Fuze | Compact, rounded, often white housing | Theater, corporate, small tours |

#### Common Beam Moving Heads
| Fixture | Visual Tell | Common On |
|---------|------------|-----------|
| Clay Paky Sharpy | Very small, iconic trapezoid body, extremely bright narrow beam | Festivals, large tours |
| Robe Pointe | Similar to Sharpy but slightly larger, excellent prism effects | Mid-size to large tours |
| Martin MAC Viper | Distinctive rounded head, very bright, fast movement | Large tours, arenas |
| Chauvet Intimidator Beam | Compact, budget, often in clubs | Clubs, small venues |

#### Common Wash Moving Heads
| Fixture | Visual Tell | Common On |
|---------|------------|-----------|
| Martin MAC Aura | Distinctive round face, LED ring visible when on, iconic design | Everywhere — clubs to arenas |
| Robe Spiider | 18 LED cells in flower pattern, distinctive look | Mid-size to large tours |
| Chauvet Rogue R2/R3 Wash | Round face, compact, common on mid-size rigs | Mid-size, clubs |
| Ayrton Mistral | Compact, square, very bright | Mid-size tours |

### Step 6: Note Rig-Specific Details

- **Trim height:** Estimate from performer height (5–6 ft). If fixtures appear 3–4 performer-heights above the stage, trim is ~18–25 ft.
- **Truss length:** Count fixtures on a truss. Multiply by spacing (~3 ft) to estimate truss length.
- **Haze density:** Continuous haze = oil-based hazer (DF-50 style). Pulsed fog = water-based fogger.
- **Console:** If visible, grandMA consoles are recognizable by their distinctive angled screen layout and motorized faders.

## Practical Exercise: Reverse-Engineer a Goose Rig

### From Photos: What You'd See

```
Truss structure: 4 horizontal trusses (FOH, DS, Mid, US) + floor package
  FOH truss: ~12 spot moving heads, spaced evenly
  DS truss: ~8 wash moving heads + ~8 beam moving heads
  Mid truss: ~8 wash moving heads + ~4 beam moving heads + ~4 pixel bars
  US truss: ~8 wash moving heads (backlight)
  Floor: 4 blinders, 2 hazers, LED PAR uplights

Visual characteristics:
  - Beams are pencil-thin with prism effects → Beam MH (likely Sharpy or Pointe)
  - Stage wash is soft and even with rich color → Wash MH with CMY/RGB (likely Aura or Spiider)
  - Front light is precise with gobo texture visible → Spot MH (likely MegaPointe or Encore)
  - Haze is dense and continuous → Oil-based hazer (DF-50)
  - Console visible: grandMA3 full-size
```

### Translated to RayFlow

```yaml
rig:
  name: "Goose-Inspired Club Rig"
  venue:
    name: "Mid-Size Club"
    dimensions: [40, 30, 25]
  fixtures:
    - label: "Spot_FOH_1" thru "Spot_FOH_12"
      fixture_name: "Robe@MegaPointe"
      mode: "Mode 1 (34ch)"
      universe: 1
      start_address: 1, 35, 69, ...
      position:
        x: [-16.5, -13.5, -10.5, -7.5, -4.5, -1.5, 1.5, 4.5, 7.5, 10.5, 13.5, 16.5]
        y: -20
        z: 22
    # ... wash, beam, blinder, haze fixtures similarly
```

## Fixture Identification Resources

When you can't identify a fixture from visuals alone:

1. **The band's social media** — LDs often post rig photos with fixture tags
2. **Rental house listings** — Check what gear companies like Christie Lites, 4Wall, and PRG stock
3. **Manufacturer websites** — Robe, Martin, Clay Paky, Chauvet, Elation, Ayrton all have product galleries
4. **Lighting forums** — Reddit r/lightingdesign, MA Lighting Forum, ControlBooth
5. **GDTF Share** — If you find a fixture name, download its GDTF file for exact channel specs

## Implications for RayFlow

1. **Rig import from description:** A future CLI command like `rayflow rig describe "4 trusses, 12 spots FOH, 8 washes per truss, 4 blinders floor"` could auto-generate a rig YAML with reasonable fixture selections and positions.
2. **Fixture library with visual references:** The GDTF library should eventually include fixture photos or renders to help users visually match fixtures to their reference images.
3. **Rig template gallery:** A gallery of known rigs (Goose Fall 2024, Phish Summer 2023, etc.) that users can browse, select, and instantiate with their venue dimensions.
4. **Programming pattern recognition:** Analysis of concert video could identify programming patterns (chase speeds, effect types, color palettes) and suggest equivalent RayFlow cue generation parameters.
