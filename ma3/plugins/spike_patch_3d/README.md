# spike_patch_3d

One-shot grandMA3 2.5.1 Lua spike. It imports two library fixture types, patches one mover and one wash, sets 3D positions, and writes a readback of what MA3 actually stored. It has never been run; the Lua was written from the help pages and MA's sample plugins without access to MA3.

Run it only in a new scratch show. It stores fixtures into `Stages.1.Fixtures` and changes `FixtureTypes` source settings.

## Install and run

1. Start grandMA3 onPC 2.5.1.
2. Copy this whole folder to `~/MALightingTechnology/gma3_library/datapools/plugins/spike_patch_3d/`.
3. In onPC, create a new empty scratch show (do not use `rayflow_test.show` or any show you care about).
4. Open a Plugins pool window (Add Window, Plugins).
5. Edit an empty pool slot, then use the import option to import `spike_patch_3d.xml` from the library. If the plugin does not appear, type `ReloadAllPlugins` in the command line and retry.
6. Run the plugin by tapping its pool object (or `Plugin "Spike Patch 3D"` in the command line).
7. Watch the System Monitor: every command and import attempt is echoed. Wait for the line `spike_patch_3d done`.
8. Confirm these files exist in `~/MALightingTechnology/gma3_library/` (the path is echoed in the System Monitor too): `spike_patch_3d_log.txt`, `spike_patch_3d_readback.json`, `spike_patch_3d_readback_exportjson.json`.
9. Open the 3D window and the Fixture Sheet (or Patch) and note, for the mover at 1.1 and the wash at 1.101, which direction +X, +Y and +Z move them on screen.

## Send back

- `spike_patch_3d_log.txt`
- `spike_patch_3d_readback.json`
- `spike_patch_3d_readback_exportjson.json` (even if it looks malformed)
- A screenshot of the 3D window showing both fixtures
- Your note from step 9 on axis directions
- The System Monitor text if any file is missing
