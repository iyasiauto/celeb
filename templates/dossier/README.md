# Dossier — true crime & internet mysteries

True crime and internet mysteries told as a case file on a black table: real footage lying on an aviation chart under a spotlight, real posts and documents as cards, notices and messages typed out like a teletype, a red crosshair on what was found, the main person's name in gold serif, a tracking box on the suspect, two-colour dialogue between police and suspect, and a typewriter caption in the corner. Web pages, real photos, maps in a chart skin.

*A case file on a black table: typed alerts, red crosshairs, real documents.*

Imported from Frontier (`styles/dossier.json`) by `docu/tools/frontier_import.py`: the graphics are Frontier's own
look kit `dossier` drawn by the Docu engine, so a video made here looks like the
Frontier channel - and goes through Docu's QC, edit audit and final QC like every other template.

Preview: `templates/dossier/previews/sheet.jpg` · sample: `styles/dossier/sample.mp4` · worked example: `templates/dossier/demo_build.py`

## Devices

| Device | Use |
|---|---|
| `dossier_alert` | a real notice, warning, court order, message or post typed out like a teletype (only real text or a faithful summary marked as such) |
| `dossier_crosshair` | a thing found or targeted (icon folder | photo | pin | phone) |
| `dossier_disclaimer` | only at the very start of a story with violence or crime |
| `dossier_title_gold` | the main person's name the first time it matters |
| `dossier_tracker` | a real photo of a public person with a red tracking box, their name and a tag (SUSPECT, WITNESS, VICTIM only for public figures; private people get no photo) |
| `dossier_dialogue` | 2-4 real exchanged lines between two people (police and suspect, two users, a call) typed in two colours |
| `dossier_stack` | 2-3 real documents, posts or messages as cards on the table, the key line marked yellow (mark = index of the line, -1 none) |
| `dossier_stamp` | a year or a place typed big over the footage. |
| `map` | where it happens (the template's map colours) |
| `spotlight` | a real photo of a person named, in a pool of light |
| `depth` | a 2.5D push into a still |
| frame `print` | footage treatment: every 2-th shot (F.framed(scene)) |

## Writing a shot list

```python
import frontier
F = frontier.Template("dossier")
at(cue, F.g("alert", **{"head": "CODE RED", "sub": "U.S. EMBASSY", "lines": ["URGENT ALERT", "ALL CITIZENS IN AFGHANISTAN"], "stamp": "EVACUATE NOW", "body": "one or two sentences of the real notice, warning or message, typed out"}))     # a graphic, its sounds included
at(cue, F.framed(clip(12)))                                     # footage in the print frame
at(cue, clip(14, overlays=[F.over("alert", at=0.4, ...)]))   # a graphic over footage
```

## How it is cut

- Every graphic shows a real fact the voice gives at that moment (a name, a date, a place, a figure, a quote) - times come from the word timing, never before the narrator says it.
- Footage: every 2-th shot sits in the print frame (frame='print'); clips under 5 s, chained when a line is longer; no talking heads, influencers or logos (QC).
- This is a case file. The first minute opens on a stamp (the year or the place typed big over the footage) on the first date or place, a disclaimer only if the story holds violence or a crime against a person, then title_gold on the first time the main person is named, a headline (the real post, page or message) on the first thing that was written online, an alert for the first notice, warning, message or court order the story quotes, a crosshair on the first thing found or targeted, a map (the chart) on the first place that matters, a spotlight on every other public person named, and text labels on the footage for names, dates and figures.
- After the hook: the real footage carries it, treated as prints on the chart. A stack (the real documents, posts or messages as cards) whenever the story quotes something written; a dialogue when two people exchanged real words (police and suspect, two users, a call); a tracker on a public person the story follows; a crosshair on each new piece of evidence; an alert for any notice or warning; a headline for every real page named; a map when the story moves; a spotlight on each new public person; a stamp on each new year. Never twice the same tool in a row.
- DOSSIER: real footage lying on a chart, real posts and documents as cards, typed notices, a red crosshair on the evidence, the name in gold, a tracking box on the suspect, typewriter captions. Paste links to the real posts, articles or videos into Extra instructions and they are used as research.
