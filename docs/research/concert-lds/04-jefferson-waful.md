# Jefferson Waful — Umphrey's McGee

**Era:** Early 2000s – 2023
**Role:** Lighting Director, Umphrey's McGee

## The Hybrid Architect

Jefferson Waful lit Umphrey's McGee for over two decades, developing a hybrid approach that bridges structured programming and improvisational busking. Umphrey's McGee's music is uniquely demanding: complex composed sections with precise transitions between songs, but also extended improvisational passages where anything can happen. Waful's system handles both.

## Programming Style

### Section-Based Hybrid
- **Composed sections:** Timecoded or GO-triggered cue sequences for the arranged parts of songs (verses, choruses, bridges, composed transitions). The band plays these consistently each night — the lighting can be precise.
- **Improvisational jams:** When the band enters an improvised section, Waful releases control to busking faders. Pre-built movement generators, color chases, and intensity effects are always ready.
- **Handoff points:** Specific moments in each song are designated as busking handoff points. When the band reaches that structural marker, Waful switches modes.

### Intricate Layering
Where Kuroda favors bold, high-contrast looks, Waful's style is more intricate:
- Complex, interwoven movement patterns across fixture groups
- Multi-layer color blends (three or four colors simultaneously across different fixture groups)
- Detailed beam textures with gobo + prism + focus interplay
- Pixel-mapped LED fixtures integrated with conventional lighting

### Pixel Mapping Pioneer
Waful was an early adopter of pixel-mapped LED fixtures in the jam band scene. He integrated video-driven content on LED panels and multi-cell washes, synchronized to the performance. His pixel mapping adds a visual layer that conventional fixtures alone can't produce.

## Rig Evolution

Waful's rig grew substantially over his tenure, from a club-scale rig to arena production. His philosophy: the rig must support both the precision of composed sections (exact looks at exact moments) and the flexibility of improvisation (any look available instantly).

## LD Commentary: Umphrey's McGee "Der Bluten Kat"

**Source:** https://www.youtube.com/watch?v=bPf1svox900 (~17 min)

### Design Techniques Observed

- **Muscle memory is everything:** "This is all muscle memory. You see I'm not even looking at the stage. The stage is like an afterthought because I'm concentrating on what I'm doing."
- **Know the music cold:** "You want to know the music so cold that it's like the last thing on your mind. It's just ingrained in the DNA. I can hear the little nuances of the way they improvise, I can tell when they're gonna come to the next big peak."
- **Counting complex time signatures out loud:** Umphrey's writes in odd time signatures that sound like 4/4. Waful counts "1-2-3-4, next time 2-3-1-2-3" — literally speaks the rhythm.
- **Flash buttons (right hand):** Hold = white override, release = return. 20-year-old muscle memory pattern from park cans.
- **"Save your tricks":** "All of us improv guys kind of deal with the same thing — you got to save your tricks." Reserve best looks for peak moments.
- **Show builds over the night:** Architectural intensity curve — first set = restrained, second set = escalation, reserved cues only appear later.
- **Multi-attribute tempo sync:** Towers ghosting white pulse matched to bass player, rest of rig matched to hi-hat — 3-4 different attributes matching different band members simultaneously.
- **Cone gobos for "pretty" sections:** Purple + cone gobo = go-to reset look between intense passages.
- **White reserved for peaks:** "I went to white by accident there, I'd rather go to white on the big hit right here."
- **Composed vs. improv delineation:** "Up until this point this has all still been composed, there hasn't been really a note of improv."

### Video Projection Integration (Cap Theater)

- Venue had wall projection designed by Mark Brickman (Pink Floyd LD)
- Relay system: Waful calls hue names → crew chief Louie relays via headset → projectionist backstage executes
- Chose **organic/nature content** (raindrops, ocean, water) over psychedelic: "Nature can be way more psychedelic than people trying to be psychedelic"
- **Flow state goal:** Quotes Santana and Trey Anastasio — "the goal is always to get to a point where you're not thinking"

## RayFlow Relevance

1. **Hybrid cue stack generation:** For songs with known structures, generate timecoded cues for composed sections and busking handoff points for jam sections. This is a first-class authoring pattern.
2. **Pixel mapping as a cue dimension:** The authoring system should support pixel-mapped content as a fixture family alongside conventional attributes.
3. **Multi-layer color blending:** Generates color schemes that distribute across fixture groups (spots = warm, washes = cool, beams = saturated) rather than applying one color uniformly.
4. **Transition precision:** Waful's attention to song-to-song transitions highlights the importance of transition cues — looks that bridge the end of one song into the start of the next.
5. **Show arc intensity modeling:** Generated cues should be tagged with intensity tiers (reserved for set 2, climax only, opener-level). The AI should respect the arc when auto-generating a full show.
6. **Time signature awareness:** Parse odd time signatures and adjust cue timing. The AI should count for the user.
7. **"Save your tricks" intelligence:** Maintain a budget of high-impact looks and deploy them strategically across a set, not front-loaded.
8. **Organic > artificial aesthetic:** Prioritize natural imagery (water, light rays) over synthetic patterns.
9. **Page-based cue organization:** Left = bright, right = moody — semantic spatial organization within cue pages.

## Sources

- LD Commentary: "Umphrey's McGee - Der Bluten Kat (feat. Jefferson Waful)" — https://www.youtube.com/watch?v=bPf1svox900
- Raw transcript: `docs/research/raw_sources/bPf1svox900.en.srt`
