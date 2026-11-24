# Live demo control on grandMA3 onPC 2.5.1.1

On November 23, 2026, the operator loaded the separate `RayFlow_Demo_Control_A` show on macOS, imported `grandmcp.xml` at plugin 99 and ran `Plugin "grandmcp"`. The plugin answered locally at `127.0.0.1:9810`. The MCP status tool independently returned plugin 0.22.2, onPC 2.5.1.1 and `ShowLoaded`. The persistent Codex registration defaults to read-only.

The live patch listed fixture 1 as a MAC Encore Performance CLD in Basic mode at 1.001. The default user profile contained a saved 3D view in slot 5. The operator recalled it and set fixture 1 to full. The native Display 1 screenshot showed the Front camera, one selected fixture, a yellow selection highlight on the leftmost head, a 100 Open dimmer, and multiple white beams. The number of visible beams prevents attributing a change in brightness to fixture 1 alone.

Creating another 3D window on Display 2 returned `Cannot Create Object`. Recalling the existing layout on Display 1 succeeded. These observations describe the bundled demo. The [custom stage](../../../stage-comparison/README.md) has its own patch and lighting looks.

The bridge then moved fixture 1 by one metre in X and restored its position. The console reported −7.200 m before the move, −6.200 m afterward and −7.200 m after restoration. Its patch remained 1.001 throughout. See the [live fixture readback](../../../stage-comparison/ma/demo-readback.json).

The move was verified through live patch readback. The bridge captures were blank or cropped on this Mac, so the operator screenshot established beam rendering and the patch readback established the position change. The [upstream plugin source](https://github.com/HybridFox/grandmcp/tree/745f80454f461bc09342c1197ca391eca79cfddb/plugin) is pinned to the revision used.

At wrap-up the operator confirmed the Save As dialog. `RayFlow_Jam_Stage_01.show` exists on disk and the bridge reported `ShowLoaded` for that name. The bridge still tracked the rename as a pending save, so check the save result before changing the patch. The next operation is to import `RayFlow_Stage.mvr` from the MA user library into this working copy. Include scene objects in Partial Show Read for the deck, riser and trusses, then verify the patch and lit views. [MA 2.5 Partial Show Read](https://help.malighting.com/grandMA3/2.5/HTML/sc_psr.html)
