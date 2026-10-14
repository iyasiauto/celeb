# 2D Stories — one decision, ten years

Second-person money stories told over years, drawn as flat 2D cartoons with one recurring main character, the same face and clothes in every frame. Replace the cast and the art direction with your own.

*Second-person money stories, told over the years.*

Imported from Frontier (`styles/stories.json`) by `docu/tools/frontier_import.py`: the graphics are Frontier's own
documentary graphics (docgfx) drawn by the Docu engine, so a video made here looks like the
Frontier channel - and goes through Docu's QC, edit audit and final QC like every other template.

Preview: `templates/stories-2d/previews/sheet.jpg` · sample: `styles/stories-2d/sample.mp4` · worked example: `templates/stories-2d/demo_build.py`

## Devices

| Device | Use |
|---|---|
| `mg_title` | a title card for the idea of the moment (title + subtitle) |
| `mg_stat` | one number that matters, big, with a line |
| `mg_bars` | 2-6 bars compared (items: label, value) |
| `mg_crowd` | a crowd of people filling in, some highlighted (count, highlight) |
| `mg_flow` | an idea moving through 2-4 steps with icons and arrows |
| `mg_cards` | 2-4 cards with an icon, a label and a line |
| `mg_checklist` | 2-5 items ticked one by one |
| `mg_compare` | two sides, before / after or this / that |
| `mg_steps` | 2-5 numbered steps |
| `mg_warning` | a warning sign with one line |
| `mg_reveal` | items revealed one after another |
| `mg_image` | a picture with a caption |
| `mg_typing` | a line typed out |
| `mg_collage` | paper stickers and cut-outs around a title |
| `mg_photonote` | a photo with a handwritten note |
| `mg_scatter` | cut-outs scattered around a word |
| `mg_pillars` | 2-4 pillars of an idea |
| `mg_opener` | the opening card of the video |
| `mg_strikelist` | a list where items are struck through |
| `mg_icongrid` | a grid of icons |
| `mg_quotemark` | a short quote in big quote marks |
| `mg_deckfan` | cards fanned out like a deck |
| `mg_timeline` | 3-5 dated steps |
| `mg_splitreveal` | a split screen revealing two sides |
| `map` | where it happens (the template's map colours) |
| `spotlight` | a real photo of a person named, in a pool of light |
| `depth` | a 2.5D push into a still |


## Writing a shot list

```python
import frontier
F = frontier.Template("stories-2d")
at(cue, F.g("title", **{"title": "The shadow you refuse to see", "subtitle": "and why it follows you"}))     # a graphic, its sounds included
at(cue, F.framed(clip(12)))                                     # footage in the plain frame
at(cue, clip(14, overlays=[F.over("title", at=0.4, ...)]))   # a graphic over footage
```

## How it is cut

- Every graphic shows a real fact the voice gives at that moment (a name, a date, a place, a figure, a quote) - times come from the word timing, never before the narrator says it.
- Footage: clips under 5 s, chained when a line is longer; no talking heads, influencers or logos (QC).
