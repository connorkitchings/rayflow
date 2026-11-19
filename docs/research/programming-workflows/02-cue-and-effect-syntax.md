# Cue and Effect Syntax

**Source:** `docs/research/manual_research2.txt`  
**Parsed:** 2026-05-25

## ETC Eos Effect Construction

| Target Effect | Key Sequence Summary | Result |
|---|---|---|
| Simple Intensity Chase | Double tap [Effect] → select {Step Based} → map steps to channels → [Enter] | Sequential step-by-step intensity chase across fixtures |
| Chase with a Build | Select {Attributes} → select {Build} softkey | Previously triggered channels remain on as chase progresses |
| Chase with a Bounce | Select {Attributes} → select {Bounce} softkey | Sequence runs forward then backward, repeating continuously |
| Fluid Linear Chase | Select {Linear} → {Parameters} → {Intensity} → {Size} | Smooth, wave-like intensity transition based on sine wave |
| Fluid Chase (Center Out) | {Offset} {Mirror Out} on active linear effect | Intensity wave starts at center and flows outward |
| Color Wipe (Left to Right) | Map steps, set {On State} and {Off State} color palettes, {Build}, {Stop and Hold} | Single color transition left to right; freezes at end |
| Absolute Rainbow Chase | Create 7 Color Palettes → {Absolute} → {Action} [@][Color Palette] | Smooth chase through rainbow colors, looping continuously |

## Moving Light Wipes and Sequence Execution

### Mechanical Wipes

A moving light projects only while panning in one direction, then fades out to return home silently. Requires synchronizing fixture physical position with its dimmer. On grandMA: apply PWM effect to dimmer channel and synchronized tilt-ramp waveform to movement channel. On Avolites: use Key Frame Shapes (Key Frame 1 = start position, dimmer at zero; Key Frame 2 = end position, dimmer at full).

### Pixel-Based Wipes

For multi-cell fixtures (e.g., GLP Impression X4 Bar), run lights in high-resolution single-pixel modes. Place cells in layout view to establish physical order, record a two-cue color sequence, and apply sequential delay (e.g., Delay 0 Thru 5 Seconds) to the color channel for a smooth sweep across all cells.
