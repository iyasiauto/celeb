# Kinetic — essays where the words are the picture

Essays where the words are the picture: one huge word on a turn, the clip pinned to a chalkboard with the line written under it in chalk, chalk line drawings that draw themselves (a lightbulb, a brain, an arrow, a clock, a target), white line-drawn stills that sketch themselves on, phone cards stacking then scattering round a serif title, a real comment with its phrases highlighted, headlines scrolling by, sources typed with a cursor. Lowercase techno-mono captions at the bottom, the key word yellow.

*The words are the picture: clusters, white pages, phone cards, comments.*

Imported from Frontier (`styles/kinetic.json`) by `docu/tools/frontier_import.py`: the graphics are Frontier's own
look kit `kinetic` drawn by the Docu engine, so a video made here looks like the
Frontier channel - and goes through Docu's QC, edit audit and final QC like every other template.

Preview: `templates/kinetic/previews/sheet.jpg` · sample: `styles/kinetic/sample.mp4` · worked example: `templates/kinetic/demo_build.py`

## Devices

| Device | Use |
|---|---|
| `kinetic_bigword` | one or two words of the sentence, huge and centred, one after another (a question, a turn) |
| `kinetic_board` | a clip or a quote pinned on the chalkboard with the line written under it in chalk (inner = the words as the source itself captioned them, source = who said it) |
| `kinetic_doodle` | a chalk icon drawn on the board for the idea of the moment (icon: lightbulb | brain | arrow | question | clock | dollar | heart | eye | gear | target | chart | person | fire | star | check | cross | book | phone | key | cloud) with 1-3 words beside it |
| `kinetic_phones` | 1-3 short posts/videos as phone cards stacking up, then the episode's serif title typed |
| `kinetic_comment` | one real comment or post, the key phrases highlighted one after another (marks = 1-3 exact phrases from text) |
| `kinetic_scroll` | 2-4 real headlines scrolling by (bold = words to bold) |
| `kinetic_mosaic` | two pixelated pictures popping in with a caption, for a joke about what cannot be shown (can also sit on a clip: overlay frontier) |
| `kinetic_sources` | 2-4 real sources or figures listed with a typing cursor. |
| `map` | where it happens (the template's map colours) |
| `spotlight` | a real photo of a person named, in a pool of light |
| `depth` | a 2.5D push into a still |
| frame `board` | footage treatment: every 3-th shot (F.framed(scene)) |

## Writing a shot list

```python
import frontier
F = frontier.Template("kinetic")
at(cue, F.g("bigword", **{"words_big": ["where", "at?"]}))     # a graphic, its sounds included
at(cue, F.framed(clip(12)))                                     # footage in the board frame
at(cue, clip(14, overlays=[F.over("mosaic", at=0.4, ...)]))   # a graphic over footage
```

## How it is cut

- Every graphic shows a real fact the voice gives at that moment (a name, a date, a place, a figure, a quote) - times come from the word timing, never before the narrator says it.
- Footage: every 3-th shot sits in the board frame (frame='board'); clips under 5 s, chained when a line is longer; no talking heads, influencers or logos (QC).
- This is an essay: the first minute opens on a bigword (one or two words of the opening question), a doodle (a chalk icon drawn for the idea: a lightbulb for an idea, a brain for thinking, a clock for time, a target for a goal, with 1-3 words beside it), then a board (the clip or the quote that set the question off, with the line written under it), a comment for the first real post quoted, and text labels for names and figures, and a spotlight (the real photo) on EVERY person named — an author, a scientist, an investor — the moment their name is said.
- After the hook: footage carries it, every third shot pinned to the chalkboard; a doodle every 30-40 seconds on the idea of the moment (icons: lightbulb, brain, arrow, question, clock, dollar, heart, eye, gear, target, chart, person, fire, star, check, cross, book, phone, key, cloud); a board for a quote or a clip; a comment for every real post quoted; a sources card when studies or figures are listed; a scroll when several headlines are named; a bigword on every turn of the argument; a mosaic for a joke about what cannot be shown. Something new every 8 to 12 seconds. A spotlight with the real photo on every person named, every time a new name comes up; real footage of the thing named is always welcome between the drawings.
- KINETIC: the caption gathers word by word left and right of the frame; big single words, white pages with typed lines, phone cards, real comments and headlines. Paste links to the studies, articles or videos you quote into Extra instructions.
