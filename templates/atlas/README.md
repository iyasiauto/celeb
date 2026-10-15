# Atlas — cartoon history explainers

History explained in a thick-outline cartoon world: every picture drawn flat with bold black outlines and a yellowed-paper palette, a TIME MACHINE bar at the bottom when the story jumps in time, a flipchart of eras and dynasties, a wristwatch showing the year, a bouncy title card, paint-wave wipes between chapters, scoreboards of armies and gold, a signpost of where the story could go, cartoon maps with thick outlines and handwritten names, and comic captions. Playful narration, real facts.

*History as a bold cartoon: the time machine, the flipchart, the paint wipe.*

Imported from Frontier (`styles/atlas.json`) by `docu/tools/frontier_import.py`: the graphics are Frontier's own
look kit `atlas` drawn by the Docu engine, so a video made here looks like the
Frontier channel - and goes through Docu's QC, edit audit and final QC like every other template.

Preview: `templates/atlas/previews/sheet.jpg` · sample: `styles/atlas/sample.mp4` · worked example: `templates/atlas/demo_build.py`

## Devices

| Device | Use |
|---|---|
| `atlas_timemachine` | the time-travel bar when the story jumps in time (years as numbers, BC negative) |
| `atlas_flipchart` | 2-4 eras, rulers, dynasties or stages as flipped pages, each with its year, its name and a colour (green|blue|red|yellow|purple| orange) |
| `atlas_watch` | a wristwatch showing the year the story lands in |
| `atlas_stamp` | the bouncy title card of an episode or a part |
| `atlas_wave` | a paint wipe between two eras or places (yellow|red|blue|green) |
| `atlas_scoreboard` | two sides compared with real numbers counting up |
| `atlas_signpost` | the places the story could go next or the roads out of a place. |
| `map` | where it happens (the template's map colours) |
| `spotlight` | a real photo of a person named, in a pool of light |
| `depth` | a 2.5D push into a still |
| frame `paper` | footage treatment: every 2-th shot (F.framed(scene)) |

## Writing a shot list

```python
import frontier
F = frontier.Template("atlas")
at(cue, F.g("timemachine", **{"from_year": 2026, "to_year": -753, "label": "Rome is founded"}))     # a graphic, its sounds included
at(cue, F.framed(clip(12)))                                     # footage in the paper frame
at(cue, clip(14, overlays=[F.over("timemachine", at=0.4, ...)]))   # a graphic over footage
```

## How it is cut

- Every graphic shows a real fact the voice gives at that moment (a name, a date, a place, a figure, a quote) - times come from the word timing, never before the narrator says it.
- Footage: every 2-th shot sits in the paper frame (frame='paper'); clips under 5 s, chained when a line is longer; no talking heads, influencers or logos (QC).
- This is a cartoon history explainer: the first minute opens on a stamp (the episode's title card), a timemachine on the first jump in time (from now to the year of the story), a watch on the year the story lands in, a map (cartoon) on the first place, a flipchart when eras, rulers or stages are listed, and text labels for names and years over the pictures.
- After the hook: the drawn pictures carry it; a timemachine on every jump of more than a century; a wave (paint wipe) between chapters; a scoreboard whenever two sides or two numbers are compared; a signpost when the story could go several ways or the roads out of a place are named; a flipchart for any list of eras, rulers, dynasties or stages; a map when the story moves; a watch on a new year that matters. Keep it moving: something new every 8 to 12 seconds.
- ATLAS: a cartoon world drawn for the exact words, with the TIME MACHINE bar, the flipchart, the wristwatch, paint wipes, scoreboards and cartoon maps. Real footage is off by default so the world stays drawn — tick YouTube footage to mix real shots in as paper prints. Every other drawn picture is set in motion by a cheap image-to-video model (look.animate).
