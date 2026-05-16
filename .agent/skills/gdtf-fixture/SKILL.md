---
name: gdtf-fixture
description: "Load, parse, and manage GDTF fixture profiles"
metadata:
  trigger-keywords: "gdtf, fixture, load profile, channel definition, parse gdtf"
  trigger-patterns: "^gdtf, ^fixture, ^load fixture, ^parse gdtf"
---

# GDTF Fixture Skill

## When to Use

- Loading GDTF fixture files (.gdtf.zip) from gdtf-share.com
- Parsing fixture channel definitions (dimmer, pan, tilt, color, gobo)
- Building a fixture library for a show
- Mapping DMX addresses to fixture channels

## Inputs

- Path to GDTF file (.gdtf.zip)
- Optional: DMX start address, universe number
- Optional: Fixture count for multi-fixture rigs

## Steps

1. **Locate GDTF file**
   - Check `data/fixtures/` for existing files
   - If not found, download from gdtf-share.com
   - Verify file is a valid .gdtf.zip archive

2. **Parse GDTF structure**
   - Extract Device.xml from the zip
   - Parse XML for:
     - Fixture name and manufacturer
     - DMX mode(s) and channel count
     - Channel definitions (type, resolution, default value)
     - Physical properties (beam angle, weight, dimensions)
     - Wheel definitions (color, gobo, prism)

3. **Build fixture model**
   - Create fixture object with all parsed data
   - Map channels to DMX addresses
   - Store in fixture library

4. **Validate fixture**
   - Verify channel count matches DMX mode
   - Check that all required channels are present
   - Validate physical properties are reasonable

5. **Add to library**
   - Save parsed fixture to `data/fixtures/` cache
   - Register in fixture catalog
   - Log successful load

## Validation

- GDTF file parses without errors
- Channel count matches expected DMX mode
- Fixture appears in library catalog
- DMX addressing is correct (no overlaps)

## Common Mistakes

- Not handling multiple DMX modes (some fixtures have 8-bit and 16-bit modes)
- Ignoring channel resolution (8-bit vs 16-bit vs 32-bit)
- Not validating DMX address ranges (max 512 channels per universe)
- Forgetting to handle wheel types (color, gobo, effect, prism)

## Links

- GDTF Specification: https://www.gdtf-share.com/
- GDTF Forum: https://gdtf-share.com/forum/
- grandMA3 GDTF Support: https://www.malighting.com/grandma3/
- Project Charter: `docs/project_charter.md`
