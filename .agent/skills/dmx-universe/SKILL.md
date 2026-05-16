---
name: dmx-universe
description: "Manage DMX universes, channel addressing, and patching"
metadata:
  trigger-keywords: "universe, dmx address, channel map, patch fixture"
  trigger-patterns: "^universe, ^dmx address, ^channel map, ^patch"
---

# DMX Universe Skill

## When to Use

- Managing DMX universe allocation (512 channels per universe)
- Patching fixtures to specific DMX addresses
- Building channel maps for shows
- Resolving address conflicts

## Inputs

- Universe number (0-based)
- Fixture channel count
- DMX start address
- Optional: Fixture list for multi-fixture patching

## Steps

1. **Initialize universe**
   - Create universe data structure (512 channels, default 0)
   - Track used address ranges
   - Validate universe number (0-15 for Art-Net 4)

2. **Patch fixture**
   - Verify start address + channel count ≤ 512
   - Check for address conflicts with existing patches
   - Reserve address range in universe
   - Map fixture channels to DMX addresses

3. **Build channel map**
   - Create mapping: DMX address → fixture channel
   - Include metadata: fixture name, channel type, resolution
   - Export as table or JSON for reference

4. **Validate patch**
   - No overlapping address ranges
   - All fixtures within universe bounds
   - Channel types are valid (dimmer, pan, tilt, etc.)
   - Total channel count ≤ 512

5. **Manage multi-universe rigs**
   - Track which fixtures are on which universe
   - Handle cross-universe addressing
   - Calculate total DMX footprint

## Validation

- No address conflicts in universe
- All fixtures have valid DMX addresses
- Channel count does not exceed 512
- Channel map is complete and accurate

## Common Mistakes

- 1-based vs 0-based addressing confusion (DMX addresses are 1-512, array indices are 0-511)
- Not accounting for fixture channel count when patching
- Overlapping patches when adding fixtures incrementally
- Forgetting that some fixtures use 16-bit channels (2 DMX addresses per parameter)

## Links

- DMX512 Specification: 512 channels per universe
- Art-Net Universe: 0-based (0-15)
- grandMA3 Patching: Check MA3 manual under "Patch"
- Project Charter: `docs/project_charter.md`
