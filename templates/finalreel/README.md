# Final Reel — childhood nostalgia · familiar faces · tragic endings

A film-archive memorial for list videos about child stars, celebrities and "gone too soon" stories.
Charcoal and ivory, a muted gold for what they were known for, one crimson for the ending. Names in Playfair,
labels in condensed caps, dates on a typewriter. Portraits sit in ivory film frames with sprocket holes over the same
picture blurred and dark; borrowed show / film clips play **inside** the film frame, never full screen.

Preview: `templates/finalreel/previews/sheet.jpg` · worked example: `projects/child_stars_died_too_soon/build.py`
(35 people, 14:13 — the shot list is generated from a table of people + the voice's own subtitles).

## Devices (scenes_finalreel.js)

| Device | What it is | Fields |
|---|---|---|
| `castcard` | who this is: framed portrait, rank, name wiping in, role, years, crimson age chip | `img, name, role, years, age, n, frameLabel, at, roleAt, yearsAt, ageAt, size, lines, tilt, zoom, fx, fy` |
| `ageclock` | the age they died at, counting up, with a date and one line | `img (blurred ground), kicker, value, unit, note, date, countFor, at, noteAt, size` |
| `memoriam` | closing card: B&W portrait in an arch, name, years, one line, candle flicker | `img, name, years, line, lineAt, fadeout, aw, ah` |
| `rollcall` | a wall of faces filling in, then a title | `imgs[], names[], cols, fillFor, title, sub, titleAt, color[] (tiles that turn to colour), colorAt, seed` |
| `lifeline` | a life on one line: born → roles → the end, markers on their words | `img, name, born, died, events[{year, label, age, at}], endAt, kicker` |
| overlay `reelframe` | the film frame around a clip rendered with `inset=[x,y,w,h]` | `box, caption, right, name, role` |
| overlay `nameplate` | name + role, lower left | `name, role, at, size` |

Also used from the engine: `map` (dark map palette), `quote`, `depth`, `photo`, the vintage TV gate (`archive=True`).

## Clips inside the frame (render.py)

A clip scene with `inset=[x, y, w, h]` is scaled into that window of the 1920×1080 picture; give it a `reelframe`
overlay with the same `box` (and `at: 0`). `flip=True` mirrors a shot. Short borrowed clips chain with `then=(...)`
(edl.clip) so one shot can carry several 2–4 s cuts of the same person.

## Pacing (the playbook, `template.json`)

- Cold open 45–60 s: one shot per subtitle line (1.5–2 s), framed clips + photos, a `rollcall` on the count.
- Body slow: castcard on the name → their roles (framed clips, photos with slow pushes) → the turn (photos, B-roll)
  → `ageclock` on the age → `memoriam` for the endings that land hardest; a `map` where the place matters.
- ~25–40 % moving footage (framed borrowed clips + nostalgic B-roll: VHS, CRT TVs, projectors, Hollywood).
- Grade `reel` (faded archive print), film-grain texture, light leak on every castcard, calm sound (paper, pop on
  the age chip, a counter roll on the ageclock).

## Footage for this niche

- Pictures of named people: `python docu/tools/fetch_people.py --out <pool>/images --people people.json --per 9`
  (files are named `<person_slug>__g<hash>.jpg`).
- QC in **people mode**: `python docu/tools/qc_pool.py <pool> --mode people --topic "..."` with a `people.json` in the
  pool — the person's own portraits are allowed; thumbnails / memes, somebody else, interviews to camera, logos,
  chyrons and watermarks are rejected.
- Competitor clips: cut from inside their frame, silent, 2–4 s, named `<person_slug>__cmp_NNN.mp4`; never full screen.
