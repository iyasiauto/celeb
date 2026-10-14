# Courtside — sports documentaries

Sports and NBA documentaries cut like a streaming film: real game footage, real photos of every player named (never AI), old newspapers animated on screen, Kodak contact strips, an old television for archive footage, cinematic black-and-white maps, article lines over darkened photos, stats tables, chapter cards, real interview clips with their own sound, and a VHS grade for the old stories — clean and modern for a young star like Lamine Yamal. The story comes first: cold open, rise, fall, what remains.

*Real photos, old newspapers, Kodak strips, VHS — the story first.*

Imported from Frontier (`styles/courtside.json`) by `docu/tools/frontier_import.py`: the graphics are Frontier's own
documentary graphics (docgfx) drawn by the Docu engine, so a video made here looks like the
Frontier channel - and goes through Docu's QC, edit audit and final QC like every other template.

Preview: `templates/courtside/previews/sheet.jpg` · sample: `styles/courtside/sample.mp4` · worked example: `templates/courtside/demo_build.py`

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
F = frontier.Template("courtside")
at(cue, F.g("dateline", **{"place": "SARAJEVO, BOSNIA", "date": "June 28, 1914", "note": "Archduke Franz Ferdinand arrives", "duration": 5.0}))     # a graphic, its sounds included
at(cue, F.framed(clip(12)))                                     # footage in the plain frame
at(cue, clip(14, overlays=[F.over("dateline", at=0.4, ...)]))   # a graphic over footage
```

## How it is cut

- Every graphic shows a real fact the voice gives at that moment (a name, a date, a place, a figure, a quote) - times come from the word timing, never before the narrator says it.
- Footage: clips under 5 s, chained when a line is longer; no talking heads, influencers or logos (QC).
- This is a sports documentary: the viewer decides in the first minute. Open on the strongest real picture — the footage of the moment, a Kodak strip of the player, or the old newspaper — and put a map of the FIRST place the cold open names (a city, a courthouse, an arena) inside the first 15 seconds: the map tells the viewer where we are. In the first minute use: a match cut (6-10 real photos of the main person, every face on one spot, a flash and a shutter per cut) on the FIRST time they are named, right after the opening montage; a Kodak strip (2 or 3 real photos) on the second public person who matters, or on the main person later in the hook; a place card on the first city; an old newspaper (press) on the first reported fact — a draft, a trade, a lawsuit, a record, a death; a map when the story moves to a new city or country; a stats table when numbers are compared; a pull line (a real sentence from a real article, with the outlet and date) on a claim the press made; a photo spotlight on every other person named; a number graphic on the figure that matters most; and text labels on the footage between the scenes for every name, year and figure.
- After the hook: real footage carries it; a Kodak strip or a spotlight every time a new person matters (real photos only, never twice the same person in the same tool); an old newspaper (press) on every reported fact of the era — a trade, a contract, a court decision, a record, a firing — and a headline (the modern web page) only for stories from the internet era; a map when the story moves city or country; a place card on a new city; a stats table for a comparison of numbers, a number graphic for one figure; a pull line for a documented sentence from an article; a quote graphic only for a documented quote; a pivot or question at a real turn; three to five text labels a minute. A story from before the 1990s has little footage: real photographs carry more of it — a strip, a spotlight or a pull line every 20 to 25 seconds, each of a DIFFERENT real photo — so no shot has to play twice.
- Sports documentaries: real game footage, real photos of every player named, old newspapers animated, Kodak strips, an old TV for archive shots, black-and-white film maps, interview clips with their own sound, and a VHS grade for the old stories. Paste YouTube links of source videos into Extra instructions to use them as research. The opening montage is real interviews only: people on camera saying the name.
