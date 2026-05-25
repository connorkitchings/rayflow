# Coordinate System and Fixture Placement

**Purpose:** Define the spatial model for RayFlow's rig builder. Every fixture position, every venue dimension, every truss structure uses this coordinate system.

## The Coordinate System

RayFlow uses a right-handed coordinate system oriented from the audience perspective:

```
                    +Y (upstage / away from audience)
                    │
                    │   Stage Area
                    │
                    │
     ───────────────┼─────────────── +X (stage right)
                    │
                    │
                    │
                    │
                    ▼ -Y (downstage / toward audience)
                   AUDIENCE
```

| Axis | Direction | Zero Point | Range |
|------|-----------|-----------|-------|
| **X** | Stage Left ↔ Stage Right | Center line | Negative = Stage Left, Positive = Stage Right |
| **Y** | Downstage ↔ Upstage | Downstage edge (front of stage) | Negative = in the audience, Positive = upstage |
| **Z** | Floor ↔ Ceiling | Stage floor (deck) | 0 = floor, Positive = upward |

### Units
All values in **feet** (US touring standard). Venues and fixtures are dimensioned in feet. Throw distances, trim heights, and beam diameters are calculated in feet. Conversion to meters: `1 ft = 0.3048 m`.

## Fixture Position (Position3D)

```python
Position3D(
    x=0.0,      # Stage center (0 = center line)
    y=10.0,     # 10 ft upstage from downstage edge
    z=20.0,     # 20 ft above deck (trim height)
    pan=0.0,    # Pan orientation: 0° = straight downstage
    tilt=90.0,  # Tilt orientation: 90° = horizontal, 0° = straight down
)
```

### Pan Convention (Fixture Orientation in the X-Y Plane)
- **0°** — Fixture points straight downstage (toward audience)
- **+90°** — Fixture points Stage Right
- **+180° / -180°** — Fixture points straight upstage (away from audience)
- **-90°** — Fixture points Stage Left

### Tilt Convention (Vertical Angle from Nadir)
- **0°** — Fixture points straight down (nadir)
- **90°** — Fixture points horizontal (level with the deck)
- **180°** — Fixture points straight up (zenith, rarely used)

### The Pan/Tilt for a Typical Front Light
A fixture on the FOH truss pointing at a performer at center stage:
```
Position3D(
    x=-15.0,     # 15 ft Stage Left of center
    y=-20.0,     # 20 ft downstage (over audience)
    z=25.0,      # 25 ft trim height
    pan=approx_45,   # Angled toward center from Stage Left position
    tilt=approx_55,  # Angled down at 35° from horizontal toward performer
)
```

## Placement Reference Points

### Stage Reference Point (0, 0, 0)
The origin is **center line, downstage edge, at deck height**. All fixture positions are relative to this point. A performer standing at center stage, 10 ft from the downstage edge, is at position (0, 10, 5.5) — 5.5 ft being approximate face height.

### Truss Position Reference Points

| Truss | Typical (X, Y) Range | Typical Z |
|-------|---------------------|-----------|
| **FOH Truss** | X: depends on width, Y: -20 to -60 | 20–35 ft |
| **Downstage Truss** | X: spans stage width, Y: 0 to 5 | 18–25 ft |
| **Mid Truss** | X: spans stage width, Y: 10 to 20 | 15–25 ft |
| **Upstage Truss** | X: spans stage width, Y: 20 to 35 | 15–25 ft |
| **Stage Left Booms** | X: -stage_width/2 - 5, Y: 5 to 25 | 0–10 ft |
| **Stage Right Booms** | X: +stage_width/2 + 5, Y: 5 to 25 | 0–10 ft |
| **Floor (deck)** | X: various, Y: 2 to 25 | 0–3 ft |

### Fixture Spacing on Truss
Fixtures hang from truss at regular intervals. The spacing depends on fixture size and truss length:

```
fixture_spacing = max(fixture_width + 0.5, 3.0)  # feet, minimum 3 ft apart

For a 40 ft truss with 2 ft wide fixtures:
  fixture_spacing = max(2.5, 3.0) = 3.0 ft
  max_fixtures = floor(40 / 3.0) = 13 fixtures

  Positions (X):  -18, -15, -12, -9, -6, -3, 0, 3, 6, 9, 12, 15, 18
```

## Zone Coverage Calculation

### How Many Fixtures to Cover a Zone

Given a zone of width W and depth D at distance T (throw), and a fixture with beam angle θ:

```
beam_diameter = 2 * T * tan(θ / 2)

fixtures_per_row = ceil(W / beam_diameter)
fixtures_per_column = ceil(D / beam_diameter)
total_fixtures = fixtures_per_row * fixtures_per_column
```

### Example: Covering a 30 ft × 20 ft Stage with Front Wash

```
Fixture: LED PAR with 36° beam angle
Throw: 25 ft (FOH truss to center stage)

beam_diameter = 2 * 25 * tan(36°/2) = 2 * 25 * tan(18°) = 2 * 25 * 0.325 = 16.25 ft

fixtures_per_row = ceil(30 / 16.25) = 2 fixtures across
fixtures_per_column = ceil(20 / 16.25) = 2 fixtures deep
total = 4 fixtures

Note: Beam overlap of 30% is standard for even coverage. Adjust:
fixtures_per_row = ceil(W / (beam_diameter * 0.7))
```

## Pan/Tilt Calculation for Targeting

Given fixture position (fx, fy, fz) and target position (tx, ty, tz):

```python
import math

dx = tx - fx
dy = ty - fy
dz = tz - fz

# Horizontal distance in X-Y plane
horizontal_distance = math.sqrt(dx**2 + dy**2)

# Pan: angle in X-Y plane
pan = math.degrees(math.atan2(dx, dy))  # atan2(x, y) = atan2(delta_x, delta_y)

# Tilt: angle from straight down
tilt = math.degrees(math.atan2(horizontal_distance, dz))
# tilt = 90° when horizontal_distance ≫ dz (far horizontal throw)
# tilt = 0°  when horizontal_distance = 0 (straight down)
# tilt = 45° when horizontal_distance = dz (classic 45° angle)
```

### Example
```
Fixture at FOH: x=-15, y=-20, z=25
Target (performer face at center): x=0, y=10, z=5.5

dx = 0 - (-15) = 15
dy = 10 - (-20) = 30
horizontal_distance = sqrt(15² + 30²) = sqrt(1125) = 33.5 ft

pan = atan2(15, 30) = 26.6° (points right of center, toward target)
tilt = atan2(33.5, 25 - 5.5) = atan2(33.5, 19.5) = 59.8°
```

## Node Types for Fixture Placement

Each fixture slot should declare its mounting node type:

| Node Type | Description | Z Origin | Pan Default |
|-----------|-------------|----------|-------------|
| `foh_truss` | Front-of-house truss, over audience | Z = trim height | 0° (downstage) |
| `ds_truss` | Downstage truss, just upstage of proscenium | Z = trim height | 0° |
| `mid_truss` | Mid-stage truss | Z = trim height | 0° or 180° |
| `us_truss` | Upstage truss | Z = trim height | 180° (downstage) |
| `boom_sl` | Stage Left vertical boom | Z varies by instrument | 90° (cross-stage) |
| `boom_sr` | Stage Right vertical boom | Z varies by instrument | -90° (cross-stage) |
| `floor` | Stage deck | Z = 0–3 ft | Varies |
| `audience` | Audience area | Z = trim height | 0° |

## Implications for RayFlow

1. Add a `node` field to `Position3D` or `FixtureSlot` — `node: str = "ds_truss"`. This enables zone-based programming ("all mid_truss fixtures go red").
2. Implement `auto_pan_tilt(fixture_pos, target_pos)` — calculate pan/tilt from positions. Used when the user places a fixture and specifies "point at DSC" (Downstage Center).
3. Implement `calculate_coverage(venue, fixture_type, beam_angle, throw_distance)` — return how many fixtures are needed and where they should go.
4. Implement `auto_space_fixtures(truss_start_x, truss_end_x, fixture_count, z)` — return a list of Position3D values evenly spaced along a truss.
5. The rig builder CLI should accept high-level instructions ("add 8 spots on FOH truss, spaced evenly") and auto-calculate positions and pan/tilt.
