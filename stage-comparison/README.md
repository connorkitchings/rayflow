# Jam-band stage comparison

Open [Stage.blend](blender/Stage.blend) in Blender. Frame **1** recalls the warm wash. Frame **2** recalls the crossing blue beams over the drum riser. The two frames are independent still looks. On this Mac, Blender 4.5.16 LTS is installed in the user Applications folder and BlenderDMX 2.3.2 is enabled.

| View | What to inspect |
|---|---|
| [Amber audience view](blender/amber.png) | Front light, rear wash and the visibility of the band positions |
| [Crossed-blue audience view](blender/crossed-blue.png) | Height and width of the beam crossing relative to the drums |
| [Overhead rig view](blender/overhead.png) | The fixture IDs, two truss lines and drum riser |

## Shared stage

The rig uses four Martin MAC Ultra Performance movers and eight MAC Aura XB washes. Their profiles come from the MA demo supplied with onPC 2.5.1.1. The [stage interchange file](interchange/RayFlow_Stage.mvr) contains the profiles, patch, deck, riser and trusses. The Blender file also includes concert dressing, cameras, haze and the two looks.

Blender reopened the saved show with all twelve fixtures. An independent comparison of the reopened Blender scene against the MVR matched every fixture ID, mode, DMX start address and XYZ hang position. The [fixture table and rebuild notes](interchange/README.md) give the dimensions and addresses. “Climb to Safety” is the selected song. The recording and timing are still open.
