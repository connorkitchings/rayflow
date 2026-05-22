# MA3 Basic Looks Control Probe

**Date:** 2026-05-22  
**grandMA3 onPC version:** 2.3.2.0  
**Target show intended:** `RayFlow Control Probe`  
**Actual loaded show affected:** `rayflow_test.show`  
**OSC target:** `127.0.0.1:8000`

## Result

This probe proved that RayFlow can send command batches over OSC and cause MA3
to create/export group, preset, and sequence pool objects. It did **not** prove
fixture-aware basic-look programming yet.

Important safety finding: the command-line show setup path is not verified.
`SaveShow As "RayFlow Control Probe"` did not create a new show file under
`~/MALightingTechnology/gma3_2.3.2/shared/shows`; the only recently modified show
file was `rayflow_test.show`. Further live probes must first verify a
disposable-show creation/load path, or use explicit manual confirmation that the
loaded show is disposable.

Follow-up note: MA's documented command-line syntax is `SaveShow "Show_Name"`,
not `SaveShow As "Show_Name"`. Using `As` can be parsed as the Assign keyword
shortcut and create `As.show`.

## Environment Evidence

Installed MA3 version:

```text
2.3.2.0
```

OSC listener:

```text
app_gma3 ... UDP *:8000
```

Computer Use attached only to the small `grandMA3 Terminal` window, not the full
MA3 programming UI. Visual verification was therefore unavailable in this run.

## Commands Sent

The following command batch was sent through RayFlow's OSC client with 0.25 s
delays between commands:

```text
SaveShow
NewShow
SaveShow As "RayFlow Control Probe"
ClearAll
Delete Sequence 1 /NoConfirmation
Delete Group 1 /NoConfirmation
Delete Preset 1.1 /NoConfirmation
Delete Preset 2.1 /NoConfirmation
Delete Preset 4.1 /NoConfirmation
Fixture 1 "LED PAR 64 RGBW" At Address 1
Fixture 2 "Robin MMX Blade" At Address 20
Channel 1 At Full
Store Group 1 /Overwrite /NoConfirmation
Label Group 1 "Probe Fixtures"
Store Preset 1.1 /Overwrite /NoConfirmation
Label Preset 1.1 "Probe Dimmer Full"
Store Preset 4.1 /Overwrite /NoConfirmation
Label Preset 4.1 "Probe Color Candidate"
Store Preset 2.1 /Overwrite /NoConfirmation
Label Preset 2.1 "Probe Position Candidate"
Store Sequence 1 /Overwrite /NoConfirmation
Label Sequence 1 "RayFlow Control Probe"
Store Sequence 1 Cue 1 /Overwrite /NoConfirmation
Label Sequence 1 Cue 1 "Dimmer Proof"
Set Sequence 1 Cue 1 CueFade "1"
Clear
Go Sequence 1
Assign Sequence 1 At Executor 201
Export Sequence 1 "rayflow_control_probe_sequence"
Export Group 1 "rayflow_control_probe_group"
Export Preset 1.1 "rayflow_control_probe_preset_dimmer"
Export Preset 2.1 "rayflow_control_probe_preset_position"
Export Preset 4.1 "rayflow_control_probe_preset_color"
```

## Export Evidence

MA3 wrote these exported pool objects:

```text
~/MALightingTechnology/gma3_library/datapools/groups/rayflow_control_probe_group.xml
~/MALightingTechnology/gma3_library/datapools/sequences/rayflow_control_probe_sequence.xml
~/MALightingTechnology/gma3_library/datapools/presets/rayflow_control_probe_preset_dimmer.xml
~/MALightingTechnology/gma3_library/datapools/presets/rayflow_control_probe_preset_position.xml
~/MALightingTechnology/gma3_library/datapools/presets/rayflow_control_probe_preset_color.xml
```

Sequence export excerpt:

```xml
<Sequence Name="RayFlow Control Probe" ...>
    <Cue Name="OffCue" Release="Yes" .../>
    <Cue Name="CueZero" No="  0">...</Cue>
    <Cue Name="Dimmer Proof" No="  1" AllowDuplicates="">
        <Part Name="Dimmer Proof" ... CueInFade="1.000"/>
    </Cue>
</Sequence>
```

Group export excerpt:

```xml
<Group Name="Probe Fixtures" ...>
    <SelectionData Size="1">
        <Item IDType="0" ID="1" X="0" Y="0" Z="0"/>
    </SelectionData>
</Group>
```

Preset exports were named correctly but contained no fixture/attribute data:

```xml
<Preset Name="Probe Dimmer Full" ... PresetModeInternal="Universal" .../>
<Preset Name="Probe Color Candidate" ... PresetModeInternal="Global" .../>
<Preset Name="Probe Position Candidate" .../>
```

No fixture or patch export was produced during this run.

## Capability Outcomes

| Capability | Outcome | Evidence | Notes |
| --- | --- | --- | --- |
| OSC command send | Pass | Command batch completed; MA3 wrote exports | UDP send is proven; command success still needs object/export evidence. |
| Disposable show creation | Fail / unsafe | Only `rayflow_test.show` was recently modified | Do not rely on `SaveShow As "RayFlow Control Probe"` until syntax/UI path is verified. |
| Sequence/cue creation | Pass for structure | `rayflow_control_probe_sequence.xml` contains Sequence name and Cue 1 | Cue contains timing but no stored fixture values. |
| Group creation | Partial pass | `rayflow_control_probe_group.xml` contains Group 1 and SelectionData ID 1 | Proves selected object was captured; does not prove fixture type/patch correctness. |
| Preset creation | Partial pass | Preset XML files exist and are labeled | Presets are empty shells; no dimmer/color/position values were captured. |
| Fixture patching | Not proven | No patch/fixture export and no UI observation | The commands may have selected/created channel IDs without proving sample fixture import. |
| Dimmer programming | Not proven for fixture output | Sequence part has no attribute data | `Channel 1 At Full` did not produce export-visible cue content. |
| Color programming | Fail for this pass | Color preset export is empty | Direct RayFlow color programming remains unverified. |
| Position programming | Fail for this pass | Position preset export is empty | Moving-head pan/tilt control remains unverified. |
| Executor assignment/playback | Not proven | No executor/current-cue readback | `Assign` and `Go` were sent but not independently verified. |
| Current-cue/readback | Not proven | No usable feedback/UI/export delta | This remains a blocker for MCP state resources. |

## Next Required Probe

Do not continue deeper programming probes until show isolation is solved.

Recommended next probe:

1. Manually or visually confirm MA3 is in a disposable show before mutation.
2. Verify a command-line show path with a no-space name, for example
   `SaveShow "rayflow_control_probe"`, and confirm the new `.show` file is
   created before any patch/programming commands.
3. Import the sample MVR through the MA3 UI or find a verified MVR import
   command. Command-line fixture patching is not enough unless fixture type
   existence can be exported/read back.
4. After fixtures are visibly/importably present, rerun the smaller proof:
   selection -> dimmer -> store preset -> export preset -> store cue -> export
   sequence.
5. Only then update RayFlow push code to handle fixture-aware color or position.

## Implementation Implications

- Add a RayFlow safety helper before more live probes: a command runner that
  logs every MA3 command, enforces a target show name, waits between commands,
  and verifies expected export files.
- Keep MCP deferred. The probe strengthened the original conclusion: we need a
  verified MA3 control/readback layer before exposing tools to AI clients.
