# Hustle — make-money & youth business

Side hustles, online business and money explainers with the energy of the best young creators: footage on a dark glossy stage with a glow and a drop shadow, big two-to-four-word captions popping in the middle with the key word in red, DIFFICULTY LEVEL bars filling segment by segment, glossy 3D icons with one word, money raining over the footage, corner titles with a glossy blob logo, counters rolling up to the figure, one option versus another on scored bars, checklists ticked one by one. Fast cuts, punchy grade.

*Glossy black, glow, difficulty bars, money rain, counters.*

Imported from Frontier (`styles/hustle.json`) by `docu/tools/frontier_import.py`: the graphics are Frontier's own
look kit `hustle` drawn by the Docu engine, so a video made here looks like the
Frontier channel - and goes through Docu's QC, edit audit and final QC like every other template.

Preview: `templates/hustle/previews/sheet.jpg` · sample: `styles/hustle/sample.mp4` · worked example: `templates/hustle/demo_build.py`

## Devices

| Device | Use |
|---|---|
| `hustle_bar` | a rating of something on a segmented bar (difficulty, risk, profit) with value out of max |
| `hustle_icon3d` | a glossy icon (search | dollar | rocket | bulb | chart | clock | fire | lock) with one word |
| `hustle_moneyrain` | money raining over the footage with a figure (can also sit on a clip: overlay frontier) |
| `hustle_corner` | the two-line title of a section in the corner (can also sit on a clip: overlay frontier) |
| `hustle_counter` | a figure counting up with a label |
| `hustle_versus` | two options compared on 2-4 stats scored 1-10 |
| `hustle_checklist` | 2-5 items ticked one by one. |
| `map` | where it happens (the template's map colours) |
| `spotlight` | a real photo of a person named, in a pool of light |
| `depth` | a 2.5D push into a still |
| frame `stage` | footage treatment: every 1-th shot (F.framed(scene)) |

## Writing a shot list

```python
import frontier
F = frontier.Template("hustle")
at(cue, F.g("bar", **{"label": "DIFFICULTY LEVEL:", "value": 11, "max": 14}))     # a graphic, its sounds included
at(cue, F.framed(clip(12)))                                     # footage in the stage frame
at(cue, clip(14, overlays=[F.over("moneyrain", at=0.4, ...)]))   # a graphic over footage
```

## How it is cut

- Every graphic shows a real fact the voice gives at that moment (a name, a date, a place, a figure, a quote) - times come from the word timing, never before the narrator says it.
- Footage: every 1-th shot sits in the stage frame (frame='stage'); clips under 5 s, chained when a line is longer; no talking heads, influencers or logos (QC).
- This is a make-money explainer told with one 2D character: the first minute opens on a moneyrain (the figure the title promises) or a counter on the first sum, a headline with the REAL page of the first platform named (its url — etsy.com, upwork.com, fiverr.com, printify.com — photographed as it is), a bar (difficulty, risk or profit) on the first option rated, an icon3d with the key word of the first idea, and text labels for every figure.
- After the hook: the 2D character's pictures carry it; a headline with the real page for every platform or tool named (give its url); a bar rating every option; a counter on every sum; a versus when two options are compared; a checklist for what is needed; an icon3d on the key word of each idea; a real object (a product, a device) only when one is named. Something new every 8 to 12 seconds.
- HUSTLE: footage on a glossy dark stage, big pop captions with the key word in red, difficulty bars, glossy icons, money rain, counters, versus bars, checklists. Stock footage is on by default for the lifestyle shots; YouTube footage for real products and creators.
