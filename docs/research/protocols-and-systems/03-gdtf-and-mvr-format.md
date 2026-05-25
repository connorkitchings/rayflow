# GDTF and MVR Format Reference

**Source:** `docs/research/ma3-probes/ma3_disposable_show_and_fixture_probe_2_3_2.md`, `docs/research/ma3-probes/ma3_fixture_import_probe_result.json`  
**Parsed:** 2026-05-25

## MVR (My Virtual Rig)

### Structure

An `.mvr` file is a ZIP archive containing:

```
rayflow_control_probe.mvr/
├── GeneralSceneDescription.xml    (required — MA3 expects this exact filename)
├── BlenderDMX@LED PAR 64 RGBW.gdtf
└── Robe Lighting@Robin MMX Blade.gdtf
```

### GeneralSceneDescription.xml Requirements

MA3 expects specific child elements within fixture definitions. RayFlow's first MVR export failed because it used simplified attributes instead of the expected GDTF child elements.

**Required elements per fixture:**

| Element | Purpose |
|---|---|
| `GDTFSpec` | References the embedded GDTF file name (e.g., `BlenderDMX@LED PAR 64 RGBW.gdtf`) |
| `GDTFMode` | Specifies the fixture mode/profile within the GDTF |
| `Addresses/Address` | DMX universe and starting address (e.g., universe 1, address 1) |
| `FixtureID` | Unique identifier for the fixture instance within the show |

### MA3 MVR Import Behavior

- **UI-assisted import:** Works via Patch menu → Import MVR. The user selects the `.mvr` file from the MA3 library folder (`~/MALightingTechnology/gma3_library/mvr/`).
- **Command-line import:** Unproven. MA3's command-line syntax for MVR import is context-sensitive and may require the World Server or UI interaction.
- **Merge behavior:** When importing into an existing show, MA3 presents a merge screen showing universes and fixture counts. RayFlow's second MVR attempt showed only a single `Univ` row with no fixture detail, indicating the XML structure was still not fully compatible.

### Known Issues

1. First MVR generation used simplified XML attributes instead of MA3/GDTF child elements → no fixtures visible in Patch.
2. Second generation fixed the XML shape but still showed only a `Univ` row in the merge screen → possible namespace or schema version mismatch.
3. Manual patching of a Generic/Dimmer fixture worked as a fallback proof path.

## GDTF (General Device Type Format)

### Purpose

GDTF is an XML-based fixture profile format that defines:

- **Physical properties:** Dimensions, weight, mounting points
- **DMX channel mapping:** Which channel controls which parameter
- **Wheel slots:** Color wheel colors, gobo patterns, prism types
- **Pan/tilt ranges:** Physical movement limits in degrees
- **Mode variations:** Different channel configurations for the same fixture (e.g., 8-bit vs 16-bit pan/tilt)

### Structure

```
FixtureName.gdtf (ZIP archive)
├── GDTF.xml                    (main fixture definition)
├── icon.svg                    (fixture icon for console display)
├── images/                     (photographs, beam renders)
└── wheels/                     (gobo images, color swatches)
```

### GDTF.xml Key Sections

| Section | Content |
|---|---|
| `DMXMode` | Channel list with names, default values, and resolution (8/16-bit) |
| `DMXChannel` | Per-channel definition with physical attribute mapping |
| `WheelSlot` | Color, gobo, or prism definitions for wheel-based fixtures |
| `PanTilt` | Physical rotation ranges for moving heads |
| `Geometry` | 3D model reference, beam angle, field angle |

### GDTF Naming Convention

GDTF files follow a naming convention: `Manufacturer@Fixture Name.gdtf` (e.g., `BlenderDMX@LED PAR 64 RGBW.gdtf`, `Robe Lighting@Robin MMX Blade.gdtf`). The `@` separator is significant for MA3's fixture type resolution.

## Implications for RayFlow

1. **MVR generation must produce MA3-compatible `GeneralSceneDescription.xml`** with proper `GDTFSpec`, `GDTFMode`, `Addresses/Address`, and `FixtureID` child elements.
2. **GDTF parsing** is required to extract channel mappings, feature families, and wheel data for fixture-aware programming.
3. **MVR import remains a manual/UI step** until a reliable command-line path is proven or MA3 provides an API.
4. **Fallback path:** Command-line fixture patching (`Fixture <n> "<type>" At Address <addr>`) works for simple fixtures but requires the fixture type to already exist in MA3's library.
