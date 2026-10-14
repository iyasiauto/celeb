# Documentary — Real stories, told like a streaming documentary.

Real stories told like a streaming documentary: real YouTube footage of the actual events, map animations, real newspaper headlines, real photos and objects, Vox-style collage scenes and quiet, premium graphics. No stock footage, no AI pictures.

*Real stories, told like a streaming documentary.*

Imported from Frontier (`styles/documentary.json`) by `docu/tools/frontier_import.py`: the graphics are Frontier's own
documentary graphics (docgfx) drawn by the Docu engine, so a video made here looks like the
Frontier channel - and goes through Docu's QC, edit audit and final QC like every other template.

Preview: `templates/frontier-documentary/previews/sheet.jpg` · sample: `styles/frontier-documentary/sample.mp4` · worked example: `templates/frontier-documentary/demo_build.py`

## Devices

| Device | Use |
|---|---|
| `doc_dateline` | a new place or time begins: PLACE, a gold rule, the date (over the blurred real picture) |
| `doc_number` | one figure that matters, counting up, its unit, what it means and its source |
| `doc_chart` | a comparison with real numbers: 2-6 bars on warm paper, the one that matters highlighted, source under |
| `doc_timeline` | 3-5 dated events on a line the camera travels along |
| `doc_quote` | a documented quote, word by word, with who said it and when |
| `doc_pivot` | one short serif line where the story turns |
| `doc_question` | the question the next part answers |
| `doc_card` | a short card of key lines, the words that matter highlighted |
| `doc_step` | one numbered step of a process |
| `doc_social` | a follow / unfollow between two public accounts |
| `doc_chapter` | the chapter card: number, kicker, title |
| `doc_place` | a place name card (city, region) |
| `doc_pull` | a real sentence from a real article with outlet, byline and date |
| `doc_table` | a small table of real figures with its source |
| `map` | where it happens (the template's map colours) |
| `spotlight` | a real photo of a person named, in a pool of light |
| `depth` | a 2.5D push into a still |


## Writing a shot list

```python
import frontier
F = frontier.Template("frontier-documentary")
at(cue, F.g("dateline", **{"place": "SARAJEVO, BOSNIA", "date": "June 28, 1914", "note": "Archduke Franz Ferdinand arrives", "duration": 5.0}))     # a graphic, its sounds included
at(cue, F.framed(clip(12)))                                     # footage in the plain frame
at(cue, clip(14, overlays=[F.over("dateline", at=0.4, ...)]))   # a graphic over footage
```

## How it is cut

- Every graphic shows a real fact the voice gives at that moment (a name, a date, a place, a figure, a quote) - times come from the word timing, never before the narrator says it.
- Footage: clips under 5 s, chained when a line is longer; no talking heads, influencers or logos (QC).
- Documentary videos are built from real things: YouTube footage first, then maps, headlines, real photos, real objects, Vox collage scenes and premium graphics. Stock footage and AI pictures are off — tick them if you want them as a fallback.
