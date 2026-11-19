# Starter rig: fixture types, modes and addresses

This file is the single source for the starter rig (4 moving heads and 8 LED washes). The first-hour guide and any later patch plugin should take fixture names, modes, FIDs and addresses from here.

## How these names were found

Library root for onPC 2.5.1.1 on this Mac: `~/MALightingTechnology/gma3_2.5.1/shared/lib_fixture_types/`. The user library `~/MALightingTechnology/gma3_library/fixturetypes/` holds only `fixture_cache.dat` (nothing user-added).

Commands used:

```
ls ~/MALightingTechnology/gma3_2.5.1/shared/lib_fixture_types/grandma3 | grep -i '^generic'
ls ~/MALightingTechnology/gma3_2.5.1/shared/lib_fixture_types/grandma2 | grep -i '^generic@'
grep -o '<DMXMode [^>]*>' ~/MALightingTechnology/gma3_2.5.1/shared/lib_fixture_types/grandma3/generic@moving_head.xml
```

Two formats exist:
- `grandma3/` holds readable XML fixture types. Only two are Generic: `generic@moving_head.xml` and `generic@grouping.xml`.
- `grandma2/` holds 134 `generic@*.pxml` files (MA2-style types shown in the MA3 library). These files are encrypted/compressed and could not be read, so their modes and channel counts are not confirmed.

## Table

| Role | Fixture type name (as the library lists it) | Mode | Channels | Count | FIDs | DMX addresses | Status |
|---|---|---|---|---|---|---|---|
| Mover (spot/profile) | Manufacturer `Generic`, fixture `Moving Head` | `Default` (the only mode) | 18 | 4 | 1 to 4 | 1.001, 1.019, 1.037, 1.055 (uses 1.001 to 1.072) | Verified from `generic@moving_head.xml` |
| LED wash | Manufacturer `Generic`, fixture `LED - IRGBW` (file `generic@led - irgbw.pxml`) | unverified | unverified; the name suggests 5 (intensity, red, green, blue, white) | 8 | 101 to 108 | if 5 channels: 1.101, 1.106, ... 1.136 (uses 1.101 to 1.140) | File exists; mode, channels and display name unverified |

The `Moving Head` type has 9 attributes, each 16-bit (coarse and fine DMX channel): `Dimmer` (1-2), `Pan` (3-4), `Tilt` (5-6), `ColorRGB_R` (7-8), `ColorRGB_G` (9-10), `ColorRGB_B` (11-12), `Zoom` (13-14), `Iris` (15-16), `Color1` color wheel (17-18). It is an RGB-mixing head with zoom and iris. It has no gobo wheel or prism.

Spacing the washes at 101 keeps them clear of the movers' address range even if the wash turns out to need more channels (the gap is 1.073 to 1.100).

## Finding each one in Insert New Fixtures

1. Open `Menu 'Patch'.'Edit'` to get the Insert New Fixtures dialog.
2. Open the Library tab and choose the MA source.
3. For the mover, type `moving head` in the search box and pick Manufacturer `Generic`, fixture `Moving Head`, mode `Default`.
4. For the wash, type `led - irgbw` in the search box and pick the entry under Manufacturer `Generic`. Write down the mode and channel count the dialog shows, then fill in the Unverified section below.

## Unverified

- The wash row: the fixture's display name, its mode names and its channel count. `grandma2/generic@led - irgbw.pxml` could not be read. Other candidate names with the same role include `LED - RGBW` and `LED - RGB`. Confirm in the dialog and update the table.
- `generic@wash.pxml`, `generic@profile.pxml` and `generic@follow spot.pxml` exist in `grandma2/`. They are probably simple types without per-color control, but this was not confirmed. They are not recommended for this rig.
- Whether the MA3 dialog displays the `grandma2/` types under the same names as their file names (capitalization, spacing).
- Whether the 3D viewer shows the generic types with a usable model. Check in the first-hour guide, section 2.
