# Color Theory and LED Transitions

**Source:** `docs/research/manual_research2.txt`  
**Parsed:** 2026-05-25

## Additive vs Subtractive Color

Lighting design operates in the **additive color** domain. Unlike paint or print (subtractive color mixing), adding more light sources increases brightness and shifts the resulting color toward white.

### Additive Primary Colors

- **Red + Green = Yellow**
- **Green + Blue = Cyan**
- **Blue + Red = Magenta**
- **Red + Green + Blue = White**

### Subtractive Color (CMY) in Moving Lights

Many automated fixtures use **CMY (Cyan, Magenta, Yellow)** dichroic filters to subtract wavelengths from a white light source. This is the inverse of additive RGB mixing:

- **Cyan filter** removes red, passes green + blue
- **Magenta filter** removes green, passes red + blue
- **Yellow filter** removes blue, passes red + green

Combining CMY filters allows precise color subtraction from the lamp source. Modern LED fixtures often support both RGB additive mixing and CMY subtractive mixing, requiring the programmer to understand which model the fixture uses.

## Human Visual Limits

The human eye perceives color through three cone types (S, M, L — short, medium, long wavelength). Lighting designers must account for:

- **Color rendering accuracy:** Not all light sources render colors equally. Tungsten sources have a continuous spectrum (CRI ~100), while early LED sources had spectral gaps that made certain costume or set colors appear wrong.
- **Metamerism:** Two light sources can appear identical to the eye but render object colors differently. This is critical when mixing fixture types in the same rig.
- **Adaptation:** The human visual system adapts to overall color temperature over time. A look that appears warm initially may feel neutral after several minutes.

## Tungsten-to-LED Transition Challenges

The industry-wide shift from tungsten/halogen fixtures to LED sources introduced several design and technical challenges:

### Color Temperature Matching

- Tungsten fixtures operate at approximately **3200K** (warm white).
- LED fixtures must emulate this color temperature to blend seamlessly in mixed rigs.
- Many LED fixtures default to a cooler white (~5600K+), creating visible mismatch when used alongside legacy tungsten instruments.

### Dimming Behavior

- Tungsten dimming is naturally smooth: as voltage decreases, the filament cools, shifting color warmer (orange/red) before fading to black.
- LED dimming is electronic and can exhibit stepping, flicker, or abrupt cutoff if not properly calibrated.
- Quadratic or cubic output correction curves are used to emulate the natural dimming response of tungsten sources.

### Spectral Quality

- Tungsten produces a continuous blackbody radiation spectrum.
- LED sources use discrete wavelength emitters, creating spectral gaps.
- This affects how fabrics, skin tones, and painted surfaces appear under LED vs tungsten light.

### Legacy Workflow Adaptation

- Designers trained on tungsten instruments must recalibrate their color intuition for LED sources.
- Gel color references (e.g., Rosco, Lee, GAM) that were calibrated for tungsten sources may render differently under LED.
- Modern fixture profiles must include both the physical DMX mapping and the color-rendering characteristics of the source.

## Implications for RayFlow

RayFlow's fixture-aware color mapping must account for:

1. **Fixture color model:** Whether a fixture uses RGB additive, CMY subtractive, or hybrid mixing.
2. **Color temperature output:** Matching LED white point to the design intent.
3. **Dimming curve correction:** Applying quadratic/cubic output curves for smooth intensity transitions.
4. **Color palette portability:** Ensuring color presets translate correctly across fixture types with different color engines.
