# AI Presenter — A face people trust, then the pictures do the talking.

A real-looking person opens every video and talks straight to camera, then it cuts to pictures drawn for the exact words being spoken. Built to be cheap: no generated video clips, a fresh picture every ten seconds, and graphics doing the heavy lifting.

*A face people trust, then the pictures do the talking.*

Imported from Frontier (`styles/avatar.json`) by `docu/tools/frontier_import.py`: the graphics are Frontier's own
documentary graphics (docgfx) drawn by the Docu engine, so a video made here looks like the
Frontier channel - and goes through Docu's QC, edit audit and final QC like every other template.

Preview: `templates/ai-presenter/previews/sheet.jpg` · sample: `styles/ai-presenter/sample.mp4` · worked example: `templates/ai-presenter/demo_build.py`

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
F = frontier.Template("ai-presenter")
at(cue, F.g("dateline", **{"place": "SARAJEVO, BOSNIA", "date": "June 28, 1914", "note": "Archduke Franz Ferdinand arrives", "duration": 5.0}))     # a graphic, its sounds included
at(cue, F.framed(clip(12)))                                     # footage in the plain frame
at(cue, clip(14, overlays=[F.over("dateline", at=0.4, ...)]))   # a graphic over footage
```

## How it is cut

- Every graphic shows a real fact the voice gives at that moment (a name, a date, a place, a figure, a quote) - times come from the word timing, never before the narrator says it.
- Footage: clips under 5 s, chained when a line is longer; no talking heads, influencers or logos (QC).
- The presenter is the point of this channel, so it is ticked by default — pick the face and the length under Options. Generated video clips are left off: they are the dearest thing in a video and pictures plus graphics carry it for a fraction.

## Drawn pictures (Gemini)

This template's pictures are drawn for the words, the way Frontier draws them - with Frontier's Gemini browser tool
(`gemini_image/`, no paid API):

```
python docu/tools/ai_pictures.py --template ai-presenter --script projects/<slug>/data/script.txt --out media/<niche>/ai_images
```

The AI art director (Docu Studio's AI) cuts the script into one frame every ~7.0 s and writes each prompt with the
channel's look; Gemini draws them all in one session into `media/<niche>/ai_images/ai_001.png ...`.
Add that folder to the niche's pictures and use them like any picture. Own prompts: `--prompts my_prompts.json`.
The tool is found at `<kit>/gemini_image`, `$GEMINI_IMAGE_DIR` or `<Frontier folder>/gemini_image`.
