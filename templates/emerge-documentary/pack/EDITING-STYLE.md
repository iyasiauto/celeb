# Documentary — editing template

A premium streaming-documentary look: real archive footage of the actual events carries the picture, and quiet,
expensive-looking scenes land exactly on the words that call for them — an animated map when a place matters, the
real newspaper article with the line highlighted, a real photo of the named person with the camera pushing in, a real
object cut out and flying in, a short paper-collage moment, and calm serif graphics for dates, figures and quotes.
The picture is nearly clean (a faint film-dirt bed on archive footage, a warm leak only on one or two emotional moments, no vignette), the type is cream and gold, the captions sit still, and
the sound design is felt rather than heard. Suits true stories of every kind: history, business and brand stories,
crime and scandal, sport, science and space, biographies, "how X happened" explainers.

## At a glance
- Real footage first: archive and news footage of the actual events, cut sentence by sentence (a new shot about every 4 s).
- No stock footage and no AI pictures by default; everything on screen is real (real photos, real pages, real objects).
- Scenes on the words: maps, real headlines, photo spotlights, cut-out objects, paper collage, serif graphics, text labels.
- The first 60 s is the most edited stretch — something extra on screen on every sentence.
- One quiet graphic about every 45 s in the body; 3–5 text labels a minute on the footage.
- Near-clean picture: gentle grade (contrast +4 %, saturation −6 %), a faint dust bed on footage, 1–2 warm leaks per video on emotional shots only, no vignette, hard cuts (see Overlay effects).
- Captions: still (no karaoke), Roboto Condensed 46 px, bottom-centre, one line.
- Soundtrack mastered to −14 LUFS; a music bed 6 dB under the voice, ducked 6 dB more while he speaks; soft synthetic whooshes and hits on every scene.

## Frame & format
- 1920×1080, 16:9, 30 fps. Everything is designed at that size; pixel values below are at 1080p.
- Footage grade (every real clip): contrast ×1.04 (+4 %), saturation ×0.94 (−6 %), gamma 0.99 (a hair darker in
  the mids). Natural colour, slightly calmer and denser than the source. As an ffmpeg filter:
  `eq=contrast=1.04:saturation=0.94:gamma=0.99`.
- Film dust: a faint bed on footage only (see Overlay effects). Vignette: OFF on footage (graphics carry their own soft vignette). Light leaks: only on 1–2 emotional footage moments, never as a transition device.
- Every clip is scaled to fill the frame (cover-crop, no letterbox bars kept, black bars and burned-in channel logos
  cropped away; a clip whose logo can't be cropped gets a 1.24× push-in, 1.28× on a still shot).
- Final encode: x264 medium, tune film, CRF 19 — keep it high quality; archive footage already carries grain.

## Palette
| Role | Hex | Where it's used |
|---|---|---|
| Gold accent | #E3B25B | Graphic rules, units, quote marks, timeline dots, label rules, the phrase box, caption accent |
| Cream ink | #F3EEE4 | All graphic type on dark grounds |
| Soft ink | #F3EEE4 at 72 % | Context lines, notes, sources |
| Steel blue | #9DB1BA | Third accent (neutral data) |
| Warm red (warn) | #C4553F | Negative figures, warnings |
| Sage (good) | #7FA58F | Positive figures |
| Graphic ground (no picture) | #221E19 → #15130F → #0A0907 | Radial dark-brown ground behind graphics when no footage is under them |
| Chart paper | #F1EBDD → #E7DFCE → #D8CDB7 | Warm paper ground of bar charts |
| Chart ink | #231E19 | Chart titles and bar labels |
| Chart highlight | #B8472F | The bar that matters, chart title rule |
| Chart default bar | #8E857A | Every other bar |
| Chart muted text | #857B6F | Axis numbers, source line on paper |
| Caption / label white | #FFFFFF | Captions, name/place labels |
| Label sub-line | #F2EDE6 | Role or detail line under a label |
| Outline / shade | #121212 / #101010 | Caption outline, label shadow |
| Highlighter (headline pages) | #F2D027 at 86 % | The marker sweeping across the real headline |
| Map teal land | #0C7393 (light #1790B3, dark #075670) | Country on the map |
| Map place | #2F9A62 (light #46B97B) | The place that lifts out of the map |
| Map pin / route | #FF5A4E / #FFC94D | Pins, travelled routes |
| Collage palette | tan #C9BB9C, ink #1A1A1A, grey #8C8C8C, hot red #D62E1F, mustard #D9A441 | Paper-collage moments (plus one story accent colour) |

## Typography
| Role | Font family | Weight | Size px @1080p | Case | Tracking | Colour | Effects |
|---|---|---|---|---|---|---|---|
| Graphic headline figure (number) | EB Garamond | 460 | 250 | lining, tabular figures | −0.02em | #F3EEE4 | counts up |
| Number unit / kicker | Roboto Condensed | 600 | 40 | UPPER | 0.20em | #E3B25B | — |
| Context / subline | EB Garamond Italic | 400 | 52 | sentence | 0 | cream 72 % | — |
| Source line | Roboto Condensed | 400 | 23 | UPPER | 0.16em | cream 72 % | 46 px hairline before it |
| Pivot line | EB Garamond | 470 | 104 | sentence | −0.014em | #F3EEE4 | 3 px gold rule above |
| Question box | Roboto Condensed | 700 | 76 | sentence | −0.005em | #16120D on #E3B25B box | box padding 20/34 px |
| Dateline place | Roboto Condensed | 500 | 42 | UPPER | 0.24em | #F3EEE4 | typed on letter by letter |
| Dateline date | EB Garamond Italic | 420 | 72 | Title | 0 | #F3EEE4 | — |
| Quote | EB Garamond Italic | 440 | 128 (≤24 chars) / 92 (≤60) / 64 | sentence | 0 | #F3EEE4 | 300 px gold “ mark |
| Quote attribution | Roboto Condensed + EB Garamond Italic | 600 / 400 | 30 / 32 | UPPER / sentence | 0.18em / 0 | cream / soft | 64 px gold rule before |
| Timeline date / label | Roboto Condensed / EB Garamond | 600 / 400 | 50 / 42 | as written | 0.06em / 0 | cream / soft | 18 px gold dots |
| Chart title | Roboto Condensed Italic | 700 | 54 | UPPER | 0.03em | #231E19 | 2 px red rule under |
| Chart labels / values | EB Garamond / Roboto Condensed | 450 (600 highlight) / 700 | 50 / 50 (≤3 bars), 40 / 38 | as written | 0.04em | #231E19 / #3A332C, highlight #B8472F | — |
| Captions | Roboto Condensed | 400 | 46 | sentence case | 0 | #FFFFFF | 1.7 px #121212 outline, 1.2 px soft shadow |
| Label: name | Roboto Condensed | Bold | 62 | UPPER | 2 px | #FFFFFF | 1.8 px shadow, gold rule, blurred shade |
| Label: role / detail | EB Garamond Italic | 400 | 44 | sentence | 0 | #F2EDE6 | 1.5 px shadow |
| Label: place / date stamp | Roboto Condensed | Bold | 62 | UPPER | 5 px | #FFFFFF | 1.8 px shadow, short gold rule |
| Label: figure | Roboto Condensed | Bold | 132 | as written | 0 | #FFFFFF | 2.4 px shadow, counts up |
| Label: key phrase | Roboto Condensed | Bold | 66 | UPPER | 1 px | #121212 on #E3B25B box | box wipes open |
| Map title / subtitle | EB Garamond / Inter SemiBold | 500 / 600 | ~90 / ~40 | Title | 0 | #FFFFFF / 88 % white | soft drop shadow |
| Collage labels | typewriter face + condensed bold caps | — | — | UPPER | — | ink / red | paper strips |

All faces are free Google Fonts (EB Garamond, Roboto Condensed, Inter). No other families appear.

Font files: EB-Garamond.ttf, EB-Garamond-Italic.ttf, Roboto-Condensed.ttf, Roboto-Condensed-Italic.ttf, Inter-SemiBold.ttf, Inter-Bold.ttf

## Captions / subtitles
- Mode: plain still captions — every word the same white; no karaoke, no word pop.
- Roboto Condensed 46 px, white #FFFFFF, outline 1.7 px #121212, soft shadow ~1.2 px (black at ~60 %).
- One line only, at most 48 characters; a longer cue is split into consecutive lines, each timed to the words it
  holds (a line appears as its first word is spoken and leaves as the next line's first word begins).
- Bottom-centre, 96 px above the bottom edge, 80 px side margins. 170 ms fade in and out.
- Spelling follows the script, never the transcription (names spelled right).
- Hidden over every graphic, map, headline page and collage scene (a cue that only grazes a scene's first or last
  0.5 s is trimmed to the footage instead of dropped). They STAY ON over real photo spotlights and cut-out objects —
  those are pictures, not graphics.

## Text labels on screen
Labels are small typographic cards over the footage between scenes — names, places, dates, figures and (rarely) a
key term. 3–5 a minute in the body; at least 5 in the first minute when the narration names that many.
- Name (a person): bottom-left. Name in caps, Roboto Condensed Bold 62 px, baseline at x 120, y 832; slides in 24 px
  from the left over 0.42 s. A gold rule 128×5 px wipes open under it (x 120, y 846) in 0.42 s. The role in EB Garamond
  Italic 44 px at x 122, y 866. A soft, heavily blurred dark patch (about 1040×260 px, ~40 % black) sits under it for
  legibility — never a hard box.
- Place / date: top-left stamp. Caps, Roboto Condensed Bold 62 px, 5 px tracking, top at x 144→166, y 100 (slides
  22 px in 0.42 s). A short gold rule 30×5 px at x 120, y 138. Detail line below at y 176.
- Figure: bottom-left, Roboto Condensed Bold 132 px, counts up to its value in 9 eased steps over ~0.6 s (figures of
  10 or more); a 60×4 px gold rule under it; what it counts in 40 px caps under that.
- Key phrase (only a real proper term the viewer must remember — a rule, a case, a product, a diagnosis — one or
  two per video at most): dark caps on a gold box, 66 px, bottom-left at x 136, y 858, the box wiping open left→right
  in 0.38 s.
- Timing: each label starts 0.1 s before its words; fades in 260 ms, out 320 ms; stays 2.2–4.5 s (3.6 s typical). A
  label leaves 0.3 s after its sentence ends (a name 1.2 s after). At least 0.25 s between two labels.
- Never on top of a graphic, map, headline page or collage (0.3 s clearance). Labels may sit on photo spotlights and
  object scenes, but a name only on the photo of that person. A kept photo spotlight gets a name label unless one
  already names that person. A scene that did not fit becomes a label instead (its figure, date, name or place).
- A dateline on the same moment as a map becomes the map's subtitle, never a second card.

## Footage & visuals
Proportion: real footage carries the video — roughly 58 % of the hook and 60–65 % of the body; the rest is the scenes
below. No stock footage, no AI pictures (both can be switched in only as a fallback).
- Real archive / news / broadcast footage of the actual people, places and events, chosen per sentence: each shot
  plays while the sentence it shows is spoken. Real footage only — no presenters, interviews, talking heads, graphics
  or big on-screen text inside the clip; no stock-library previews with watermarks.
- Each shot keeps its longest clean stretch between its own cuts (at least 2.2 s). A shot plays for as long as it
  really lasts: a slot slightly longer than the shot slows it (at most to 74 % speed, i.e. ×1.35 stretch) and then
  holds the last frame. A real shot is NEVER looped.
- A shot shown a second time comes at least 30 s later, from later in the shot and reframed 1.25× on one side, so it
  reads as another angle. Never the shot of a sentence still to come (it would show a later event early). No two clips
  of the same photo at different zooms; no near-black clips.
- A sentence nothing was found for may take a plain shot of the main subject from the same period — never one tied
  to another dated event.
- Photos: real photographs only (a photo of a person is used only when its caption names them). Photo spotlight:
  the subject is cut out; the camera pushes in on it while everything else in the photo darkens, loses colour and
  blurs; the cut-out grows a little against the fading ground. 5 s, starts 0.9 s before the name.
- Real objects: a real thing (a product, a trophy, a document) cut out of its photo, flying in over a blurred ground in
  its own colours with a soft drop shadow — rising in turning, overshooting and settling. Layouts: solo (4.6 s), crown
  (a second object drops onto the first and wobbles, 5.6 s), pair compared from both sides (5.2 s), row of 3–4 popping
  in one by one (5.4 s). Lands 0.5 s before its name.
- Match cut (once per video, on the first time the main person is named): 6–10 real photos of them cut fast, the face
  landing on the same spot at the same size each time (a blurred, darkened copy of the photo fills the frame behind a
  tight portrait), a white flash (92 % → 0 in 0.13 s) and a camera shutter on every cut, each photo pushing in 4.5 %,
  the last held with a 7 % eased push and a 0.3 s fade. 4.6 s.
- Text match cut (once per video, where the facts pile up; never within 20 s of the match cut): 3–5 punches of 1–4
  words in caps (Inter Display Black 150 px, white), each on a hard cut to another real photo of the subject darkened
  to 62 %, the words locked on one spot at left (x 132), an accent rule above, a red/cyan chroma split snapping shut, a
  white flash and a hit on every cut, the last line held. 5 s.
- Sound-up (1 per video, in the hook): after a sentence, one real clip plays with its own sound (a roar, a buzzer, a
  crowd, a crash) while the narration pauses; cut at a sentence end, a whoosh in and a hit out.
- Paper collage (Vox-style) moments: 7–14 s told as hand-cut paper collage on one shared aged-map/newsprint stage —
  black-and-white halftone cutouts of the real people with their real faces (white keyline, offset red stroke), torn
  archival photos, typewriter label strips, rubber stamps, big red number cards, brass pins and red string. Shots of
  2–4 s (about 3.4 s), each with one visual idea; cutouts spring up with overshoot, labels type on, stamps thump
  down, numbers tick, string draws itself, the camera drifts ~2 % and never goes closer than 2× (1.6× over a photo).
  Hard cuts inside, occasionally a paper wipe or torn-edge reveal. One story accent colour per video.
- Real headline pages: the real article behind a claim (or the encyclopedia page), photographed as it is — cookie
  banners and ads hidden, never accepted. A tilted browser window with the real address rises in, the camera pushes
  in on the headline, a yellow marker (#F2D027, 86 %) sweeps across it line by line as the voice says it, the rest of
  the page sinks back out of focus, a red–cyan flicker as it lands, a sheen, grain and vignette; source credited. Three
  movements rotated per video: window, paper, scan. 6.5 s, starts 1.3 s before the words.

## Graphics & scene types
Every graphic shows a real fact the voice does not say (a date, a place, a figure and its source, a comparison, a
sequence, a documented quote) or one short line at a real turn. Never retyped narration, never stickers, icons or
clip-art. Ground: this video's own footage near that moment, cover-cropped, desaturated to 85 %, darkened and blurred,
pushing in slowly (1.0 → 1.055, ease in-out) under an 8 % film-grain layer that shifts at 15 fps and a soft radial
vignette to 42 % black; charts sit on warm paper instead (push 1.0 → 1.022). The words leave in the last 0.5 s with an
ease; the picture stays until the cut. Left margin for left-aligned layouts: 132 px.

| Type | When | Look & animation | Length |
|---|---|---|---|
| Dateline | A new place or time begins | Bottom-left (132 px from left, 168 px from bottom) over a bottom-up dark gradient: place in tracked caps typed on letter by letter (35 ms each from 0.25 s), a 2 px gold rule grows to 220–640 px (0.55–1.45 s), the date in large serif italic rises 16 px (0.95–1.85 s), a small note fades in by 2.3 s | 5.0 s |
| Number | One figure that matters | Left-aligned block vertically centred: gold unit kicker, the figure in 250 px serif counting up from 0 (0.35–2.2 s, ease-out), italic context line rises at 1.5–2.4 s, "SOURCE: …" at the bottom-left fades in by 2.9 s | 6.0 s |
| Chart | A comparison of 3+ real things | 2–6 horizontal bars on warm paper, labels right-aligned left of the bars, dashed grid, the highlighted bar in brick red, bars grow one after another (0.14 s stagger, 1.6 s each, ease-out) with their values riding the bar end; the highlighted value pulses 8 %; source bottom-left | 8.0 s |
| Timeline | 3–5 dated events in order | A thin line draws across; gold dots pop, dates rise, labels fade in, one after another; the camera travels sideways so the newest event stays in view; events leaving frame fade | 8.5 s |
| Quote | A documented quote, word for word | Giant gold “ top-left, the quote appears word by word (over 1.4–3.4 s), then a gold rule + NAME + italic role/year | 7.5 s |
| Pivot | The story turns (≤ 7 words) | A 96 px gold rule draws, the serif line rises out of a mask line by line (0.17 s stagger), over a left-to-right dark gradient | 4.6 s |
| Question | The question the next part answers (≤ 6 words) | Dark text on a gold box that wipes open left→right (0.2–0.85 s), left-aligned, vertically centred | 4.2 s |
| Social | Two people follow / unfollow each other | Two white profile cards (700×270 px, 34 px radius) with gradient-ringed avatars; a cursor clicks "Following" → "Follow" (grey #EFEFEF / blue #0095F6); a red heart between them splits apart (or joins) | 5.2 s |
| Step / Card | How-to stories only | Step: grey #5E6064 ground, "STEP 2" in gold, white title, a rounded photo. Card: white rounded card, the key phrases swept with a yellow #FFE14D highlighter one by one | 3.2 s / 5.6 s |

Rules: "pivot" and "question" together at most once in every four graphic slots; never the same type twice in a row;
a chart or number always names its real source; a part of a whole is a number, not a chart; a record is "at the time"
unless it still stands. Text limits: place 32 chars, labels 28, notes 60, titles 48, quotes 160. Brand colours only
for real brands, teams, parties, flags.

## Transitions
- Footage to footage: hard cut, always. No dissolves, no whips, no light leaks, no dips to white.
- Into any scene (graphic, map, photo, object): hard cut, with a whoosh peaking on the cut; a softer whoosh on the cut
  back out of graphics and maps.
- Graphics: the words leave in the last 0.5 s (ease in-out), the picture holds to the cut — never an empty frame. A
  graphic in a slot longer than itself holds before its words leave.
- Match cut / text match cut: white flash on each internal cut (0.13 s decay) + shutter / hit.
- Paper collage: hard cuts, occasionally a paper wipe or a torn-edge reveal.
- NEVER: star wipes, 3D transitions, lens flares, glitches, film burns, zoom transitions, crossfades between clips.

## Motion & camera
- Every real clip: a slow, smooth push of 3.5 % over its slot (linear, sub-pixel — never a stepping crop or a shaky
  zoom). Nothing else moves the camera on footage: no shake, no speed ramps.
- Graphic grounds: 1.0 → 1.055 eased in-out over the whole graphic (charts on paper 1.0 → 1.022; chart page
  itself 1.0 → 1.018).
- Type in graphics never moves once landed (pixel-locked); only rules, grounds and bars move.
- Photo spotlight: steady push on the cut-out subject while the ground darkens and blurs.
- Objects: damped springs — rise, overshoot, settle; drop shadow lifts and softens with height.
- Match cut: 4.5 % push per photo, 7 % eased push on the last.
- Collage: ~2 % drift, micro pushes, max 2× zoom (1.6× over a photograph). Never spinning, never shaky.
- Easing everywhere: ease-out quint/cubic for arrivals, ease in-out cubic for moves; nothing linear except the
  footage push.

## Overlay effects
Effects stay quiet — this is a premium documentary, not a trailer. They sit ONLY on real footage (and the sound-up clip),
above the grade and below every caption, label and scene; never on a graphic, map, headline page, collage, match cut or
spotlight, never while a label is on screen (0.3 s clearance either side), never on a talking face.
| Effect | Clip / build | Blend | Opacity | Length & fades | How often, where | SFX |
|---|---|---|---|---|---|---|
| Film-dirt bed | dark specks and hairs on a white ground (film dirt) | multiply | 0.35 (0.25 on modern HD footage) | every footage stretch between scenes, 0.3 s fade in/out at the stretch edges | all real footage; strongest feel on pre-1970 archive | none |
| Warm leak on an emotional shot | red-orange edge leak drifting across (clip) or two warm blobs drifting from one side (#ff9a3c / #ff5a36 / #ffd58a) | screen | 0.5–0.55 | 2.5–3.5 s, fade in 0.5–0.6 s, fade out 0.7–1.4 s | 1–2 per video: the sound-up (fire, crowd, roar) and the closing payoff shot; never on an ordinary cut | soft whoosh out (−20 dB vs voice) peaking on the cut into the leak; none under a sound-up |
Never: glitches, VHS, film burns, flares, bokeh, rain/snow/fog, flicker, scanlines; no leak used as a transition between
two ordinary clips; no effect on graphics, maps, pages, collage, match cut, spotlight or under any label/caption block.

## Maps
- Look ("midnight"): a teal country (#0C7393) floating on near-black (#040506 → #1A1E21), glowing cyan state and
  coast lines (#78E2FF, glow rgba(40,190,255,.55)), a faint grid, dimmed neighbours; the picked place in green
  (#2F9A62) lifts out and leaves a grey hole (#7B7F82); pins #FF5A4E with rippling white rings; routes #FFC94D with a
  ship/plane/army icon on the line; names on dark plates; title in EB Garamond, subtitle in Inter SemiBold; radial
  vignette to 62 % black.
- Kinds: region (lights up and lifts out), pin (drops, rings ripple, a leader line to its name), route (draws from place
  to place, arrives on the word naming the destination), several places (each lights as it is named), satellite dive
  onto one exact place (the Earth fills the frame, dive to real imagery, tilt into 3D, the outline draws itself, the rest
  darkens; accent #FFC400; 7.2 s, starts 3.1 s before its words; at most one per 150 s), plus range rings, then-and-now,
  night lights and a low flyover (each at most once per 120 s).
- Timing: 7 s (a journey up to 11 s); the camera flies in for 1.6 s and arrives on the word that names the place.
- Frequency: at most one map per 35 s on average, never two within 15 s. Always a map of the first real place in the
  hook; after that only when the story moves somewhere new that matters. A video under 90 s never opens on a map.
- A dateline at the same moment rides on the map as its subtitle.

## Pacing & rhythm
- Narration about 120 words per minute; the story opens cold, in the middle of the action (no intro, no title card).
- Footage: a new real shot about every 4 s (a slot never longer than ~7 s), on the sentence it shows.
- Hook = the first 60 s: scenes may cover up to 62 % of it, 2 s of footage between scenes is enough; something extra on
  screen for every sentence: a map of the first place, a dateline on the first date (or the map's subtitle), a spotlight
  on the first public figure, an object for the product at the centre, a paper-collage moment of 7–11 s inside the first
  30 s (a second before 1:00 in videos over 3 min), the real headline on the first reported fact, the match cut on the
  first naming of the main person, the sound-up, and at least 5 labels.
- Body (worked in ~2.5-minute stretches): scenes cover at most 42 %; at least 6 s of plain footage between scenes; per
  minute roughly one collage, 1–2 spotlights/objects, one graphic (one every ~45 s), 1–2 real headlines on reported
  facts, 3–5 labels; a map when a new place matters. Photo scenes no closer than 3 s, on average one per 25 s.
- Variety: never the same scene type twice in a row, the same thing never shown twice.

## Sound design
All levels are relative to the narration's speech loudness (RMS while he speaks) unless marked LUFS/dBTP. Proven on the
reference test (voice, bed, 34 effects, one sound-up).
- Voice: one steady narrator, the loudest thing throughout. Processing: 80 Hz high-pass, gentle compression (threshold
  −18 dB, ratio 2.5:1, attack 8 ms, release 120 ms, +2 dB make-up). Pauses are part of the edit: a 1.5–2 s breath after
  a blow ("…is gone."), 0.3–0.6 s before a new beat.
- Music bed: one documentary underscore (no drums up front, no vocals), started 10–30 s into the track to skip a slow
  intro. Levelled to −6 dB vs the voice in the pauses (measured −9 dB after ducking release), ducked a further −6 dB
  while he speaks (so −12 dB under speech; must measure ≤ −10 dB), attack 40 ms, release 350 ms. An EQ carve of −4 dB
  centred on 2.6 kHz (Q 0.9, covering ~1.5–4 kHz) keeps the bed out of the words. Fades in 0.8–2.5 s, out over the last
  1.5–4 s under the final line. No track repeats across consecutive videos.
- Sound-up (1 per video, in the hook): the real clip's own sound (a roar, a buzzer, a broadcast line) placed in a pause of
  the narration, levelled to −1.5 dB vs the voice, 60 ms fade in, 250 ms fade out; the bed ducks under it as under the
  voice; its words are captioned in italic quotes.
- Effects (synthesised, soft, felt rather than heard), level vs the voice:
  | Effect | Level | Exactly where |
  |---|---|---|
  | Deep hit (boom) | −15 dB | frame 1 of the cold open |
  | Whoosh in | −18 dB | peak (0.7 s into the file) ON the cut into every graphic, map, spotlight, object, sound-up (−20 dB) |
  | Whoosh out (softer) | −23.5 dB | peak on the cut back out of a graphic, map or collage |
  | Low warm hit | −21 dB | a figure finishing its count (number +1.8–2.2 s), a map pin landing (−22 dB), the end of a sound-up (−20 dB), a pivot line (+0.35 s), a date landing (+0.95 s) |
  | Riser | −22 dB | ending on the last photo of the match cut, or on a question graphic |
  | Shutter | −17 dB | every cut inside the match cut |
  | Paper | −17.5 dB | the cut into each collage shot and each headline page (+ a hit at 1.4 s on a page) |
  | Stamp thump | −22 dB | the frame a rubber stamp or number card lands |
  | Typewriter key | −24 dB | every ~3rd character of a typed strip or dateline (about 9 per second) |
  | Tap | −21 dB | timeline dots, table rows, a red underline or marker line starting |
  Never: an effect on a plain footage-to-footage cut, on captions or on a label fading in; nothing in the 2 s before a
  twist word except the bed; no hit at the very end (the bed resolves alone).
- Master: the whole soundtrack to −14 LUFS integrated (two-pass, linear), true peak ≤ −1.5 dBTP (a final true-peak
  limiter at −1.95 dBTP gives margin; the test measured −14.08 LUFS / −1.95 dBTP).

## Rules — always / never
- ALWAYS real: real footage, real photos, real pages, real objects. No AI pictures, no stock, unless explicitly asked.
- ALWAYS show what the words say at that moment; never a later event early.
- NEVER loop a real shot; a repeat is ≥30 s later, reframed 1.25× from later in the shot.
- NEVER private people (victims, relatives, ordinary employees, children) as photos — they get a name label instead.
  Every public person named in a relationship story gets a real photo on their name.
- NEVER a presenter, interview head, title graphic, watermark or big burned-in text as B-roll.
- Graphics add a fact; they never retype the narration. Real sources on every figure; quotes only if documented.
- One scene at a time: labels never over graphics/maps/pages/collage; captions never over graphics/maps/pages.
- A cookie banner on a real page is hidden or declined, never accepted.
- Keep the picture clean: only the overlay effects listed below (dust bed, 1–2 warm leaks), no vignette on footage, no glitches, no burns.
- Collage: real faces for real people, no eye bars; filler words never become a card; words above pictures.

## Checklist before export
- [ ] First frame is a real, strong picture; a deep hit under it; no intro card.
- [ ] Map of the first real place, the match cut on the main person, a collage moment, a headline and ≥5 labels in the first 60 s.
- [ ] Every shot matches its sentence; no shot plays before its event; no shot looped; repeats ≥30 s apart and reframed.
- [ ] No watermarks, presenters, burned-in text or black bars in the footage.
- [ ] Graphics: real source on every figure, no retyped narration, no same type twice in a row, ~one per 45 s.
- [ ] Captions still, one line ≤48 chars, 46 px, bottom-centre, hidden under graphics/maps/pages.
- [ ] Labels in their corners (names/figures bottom-left, places/dates top-left), 2.2–4.5 s, never over a scene.
- [ ] Grade applied (contrast +4 %, saturation −6 %); no vignette on footage.
- [ ] Overlay effects: dust bed on footage only, 1–2 warm leaks on emotional shots, none on graphics, maps, pages, collage or under any label.
- [ ] At least 6 s of plain footage between scenes after the hook.
- [ ] Music 6 dB under the voice, ducking audible but smooth; SFX felt, not heard.
- [ ] Loudness −14 LUFS, peaks under −1.5 dBTP; no frozen frames at the end.
