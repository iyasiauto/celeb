# Test report — Style 1, Documentary

**Topic:** The Hindenburg disaster, Lakehurst, New Jersey, 6 May 1937.
**Video:** `reference-video.mp4` (31.8 s, 1920×1080, 30 fps) · contact sheet `reference-frames.jpg`.

## Script (62 words, voice 25.3 s + pauses + sound-up)
> At twenty-five past seven, a flame appears near the tail. Half a minute later, the largest aircraft ever flown is
> gone. Lakehurst, New Jersey. May sixth, nineteen thirty-seven. The Hindenburg had crossed the Atlantic with
> ninety-seven aboard. On the field, reporter Herbert Morrison kept talking. *[sound-up: "Oh, the humanity…"]*
> Thirty-six people died. By morning, it was front-page news. The age of the giant airship was over.

Voice: Jon (warm, grounded storyteller). The edit lengthened two pauses (1.8 s after "is gone.",
0.35 s after "died.") and put the 2.5 s sound-up in a 2.85 s gap after "kept talking."

## Sources
- YouTube `nJ4XsHRZmpw` (newsreel paired with Morrison's recording): 10.6–16 s (the hull bursting), 55–61 s (skeleton and
  black smoke), 36.5–42.5 s with its sound (sound-up 1.85–4.35 s: "…oh, the humanity…").
- YouTube `OetzoO3Csj4` (home movie, reverse angle): 25.3–29.5 s (fire at the tail).
- YouTube `2h4jDWEet9s` (Paramount newsreel): 44–55 s (airship at the Lakehurst water tower), 219–229 s (over Manhattan),
  193–203 s (the wreck at night).
- Google Images: Morrison portrait (thecaucusblog.com), Hindenburg photos (abcnews.com, worldhistory.org,
  antiquesboutique.com, Wikimedia Commons), Daily News and San Francisco Chronicle front pages of 7 May 1937
  (alexautographs.com, sfchronicle.com), burning-airship photo (si.edu). Full list: `public/jobs/01/sources.json` in the lab.

## EDL (13 slots, all hard cuts)
| # | Time | Type | Content | In | Text / SFX |
|---|---|---|---|---|---|
| 1 | 0.00–2.02 | V | hull bursting (newsreel) | cut | stamp top-left "7:25 P.M. / U.S. Naval Air Station"; deep hit |
| 2 | 2.02–4.95 | V | home movie, fire at the tail (crop 1.5× to lose sprockets) | cut | — |
| 3 | 4.95–7.75 | G number | "FEET, NOSE TO TAIL" · 804 counting · "three and a half jumbo jets" · source line, on blurred own footage | cut + whoosh | hit on the count, whoosh out |
| 4 | 7.75–9.00 | V | burnt skeleton, black smoke (held in the breath) | cut | — |
| 5 | 9.00–12.70 | M pin | midnight map, NJ teal, pin + rings on Lakehurst, date typed as the subtitle | cut + whoosh | hit on the pin, whoosh out |
| 6 | 12.70–13.85 | V | airship at the Lakehurst water tower | cut | — |
| 7 | 13.85–15.75 | X match cut | 4 real photos, airship locked to one spot, white flash per cut | cut | shutter ×4, riser into the last |
| 8 | 15.75–18.00 | V | airship over Manhattan | cut | figure label "97 / 36 passengers · 61 crew" |
| 9 | 18.00–20.42 | P spotlight | Morrison portrait, ground dims/blurs, camera pushes 9 % | cut + whoosh | name label "HERBERT MORRISON / Reporter, WLS Radio, Chicago" |
| 10 | 20.42–23.52 | S sound-up | the burning frame at dusk, Morrison's own voice | cut + whoosh | italic caption "Oh, the humanity …"; hit out |
| 11 | 23.52–25.75 | C collage 1 | halftone torn photo, red "36 DEAD" card thumps, typed strip "13 PASSENGERS · 22 CREW · 1 LINEMAN", stamp | cut | paper, thump, typing, stamp |
| 12 | 25.75–27.95 | C collage 2 | two real front pages torn, pins + red string, "MAY 7, 1937" stamp, red underline on "front-page" | cut | paper, stamp, tap, whoosh out |
| 13 | 27.95–31.80 | V | the wreck at night, held to the end | cut | bed fades, no hit |

Captions: still, Roboto Condensed 46 px, one line ≤48 chars, 96 px from the bottom, hidden under graphic, map and
collage, on over spotlight and match cut.

## Overlay effects (added after review)
- Film-dirt bed (dark specks, multiply, 0.35) on every footage stretch free of scenes and labels: 7.75–9.00, 20.44–23.20,
  28.27–31.78.
- Code-drawn fire-orange leak (screen 0.6, 0.5 s in / 0.7 s out) over the sound-up 20.74–23.20 — the red-orange leak clip
  was tried first and read as black in its opening seconds, so it was replaced.
- Warm leak (screen 0.55, 0.6 s in / 1.4 s out) over the closing shot 28.27–31.78, with a soft whoosh out (−20 dB) peaking
  on the cut into it.
- Placement check: 4 effects, 0 on graphics or text.

## Mix report
voice speech RMS −16.9 dBFS · music under voice **−11.6 dB** · music in pauses −9.4 dB · 34 SFX · final **−14.08 LUFS**,
true peak **−1.95 dBTP** · pass: true. (Bed "doc underscore" from 12 s, bed −6 dB vs voice, duck −6 dB, EQ carve −4 dB,
SFX base −14 dB with per-type offsets — now written into the sound sections.)

## Checklist confirmed
- First frame is real footage of the event with a deep hit; no intro card.
- Map, match cut, spotlight, collage, graphic, sound-up and 3 labels all inside the first 30 s.
- Every shot matches its sentence; no shot looped or repeated; no event shown early (the crossing photos come after the fire,
  as the narration flashes back).
- Sprockets, pillar bars and film frames cropped away; no watermarks or burned-in text left (the newsreel title cards
  were skipped).
- Grade contrast +4 %, saturation −6 % on all footage; no dust, vignette or leaks on footage; graphics carry grain + vignette.
- Fonts: EB Garamond / Roboto Condensed / Inter exactly as the typography table; gold #E3B25B, cream #F3EEE4.
- −14 LUFS, peaks under −1.5 dBTP.
- Overlay effects only on footage (dust bed, two warm leaks), none on scenes or under labels.

## What still differs, and why
- **Length vs the hook plan:** a 32 s video cannot hold the full 60 s hook. The real headline page (browser window +
  marker sweep) was dropped; the "front-page news" line is told with the two real front pages inside the collage instead.
  Only 3 labels (the spec's ≥5 applies to a full minute). Scenes follow each other with 1–2 s of footage between them
  (the hook asks for 2 s).
- **Scene lengths scaled down:** number 2.8 s (spec 6 s), map 3.7 s (7 s, camera flies in 0.74 s instead of 1.6 s),
  spotlight 2.4 s (5 s), collage 4.4 s in two shots (7–11 s), match cut 4 photos (6–10).
- **Spotlight cut-out:** there is no background remover in this lab; the subject is isolated with a feathered ellipse
  mask on the photo while the ground layer dims, desaturates and blurs — it reads as the spotlight but the edge is soft,
  not a true cut-out.
- **Map geography** is hand-traced (New Jersey, neighbours, Long Island) — correct in shape but simplified.
- The newsreel footage is 1937 archive: soft and grainy by nature (the home-movie angle needed a 1.5× crop).
