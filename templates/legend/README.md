# Legend — told in the athlete's own voice

"John Daly Reveals the 5 Most Special Golfers He Ever Saw" — told by John Daly. The film opens on a real clip of the athlete or star talking on camera, about twenty seconds; their voice is cloned from that very clip, and the story continues in the first person, in their voice, over real footage and real photos of every person named. They are never shown again. Warm memoir look: photos centred over a blurred copy with a cream keyline, a yellow-bordered close-up inset sliding in, numbered chapter cards for each person on the list, lower thirds, scorecards, the narrator's own line as a card, dated years. No captions.

*A real clip, then the story in the star's own cloned voice.*

Imported from Frontier (`styles/legend.json`) by `docu/tools/frontier_import.py`: the graphics are Frontier's own
look kit `legend` drawn by the Docu engine, so a video made here looks like the
Frontier channel - and goes through Docu's QC, edit audit and final QC like every other template.

Preview: `templates/legend/previews/sheet.jpg` · sample: `styles/legend/sample.mp4` · worked example: `templates/legend/demo_build.py`

## Devices

| Device | Use |
|---|---|
| `legend_chapter` | the numbered card for each person or item of the list, the first time they are named (n = their number, note = one real fact) |
| `legend_lower` | a name and a role over the footage the first time another real person appears (can also sit on a clip: overlay frontier) |
| `legend_scorecard` | 2-5 rows of real numbers (a round, a season, a record) |
| `legend_line` | one short sentence the narrator himself says in the script, as a card in his name |
| `legend_years` | 2-5 real dated moments of a career. |
| `map` | where it happens (the template's map colours) |
| `spotlight` | a real photo of a person named, in a pool of light |
| `depth` | a 2.5D push into a still |
| frame `blurfill` | footage treatment: every 1-th shot (F.framed(scene)) |

## Writing a shot list

```python
import frontier
F = frontier.Template("legend")
at(cue, F.g("chapter", **{"n": 1, "name": "Fuzzy Zoeller", "note": "Masters champion, 1979", "subject": "Fuzzy Zoeller", "query": "Fuzzy Zoeller golfer portrait"}))     # a graphic, its sounds included
at(cue, F.framed(clip(12)))                                     # footage in the blurfill frame
at(cue, clip(14, overlays=[F.over("lower", at=0.4, ...)]))   # a graphic over footage
```

## How it is cut

- Every graphic shows a real fact the voice gives at that moment (a name, a date, a place, a figure, a quote) - times come from the word timing, never before the narrator says it.
- Footage: every 1-th shot sits in the blurfill frame (frame='blurfill'); clips under 5 s, chained when a line is longer; no talking heads, influencers or logos (QC).
- This is a first-person memoir: the first minute (after the real clip) opens on the narrator's own footage, a line card on the first sentence worth framing, a chapter card with its number the first time a person on the list is named, a spotlight (a real photo) of every person named, a lower third on each new person who is not on the list, and a years card if a career is summed up.
- After the hook: real footage of the people named carries it, every shot centred over its blurred copy; a chapter card each time the next person or item of the list is named (numbered in order); a spotlight on every person named — real photos only, never the same photo twice; a scorecard when scores, records or numbers of a round, a season or a career are given; a line card for one sentence per chapter the narrator himself says; a lower third for every other real person; years for a career summed up. Never a graphic in the first 3 seconds after a chapter card.
- LEGEND: the video opens on a real interview clip of the person in the title, their voice is cloned from it (Algrow, one clone per person, remembered), and the story continues in their first person over real footage and a real photo of every person named. Titles like "X Reveals the 5 ..." or "X on the day ..." work best.
