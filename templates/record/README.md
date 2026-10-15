# The Record — investigative documentary

For investigations into closed communities and institutions: cover-ups, silence and pressure, court cases, rulings,
how a system protects itself. The case is assembled from the record itself — every claim appears as part of it.

Blue-black ink ground with a faint ledger grid, bone-white paper pages, steel-grey labels and **one** signal colour
(sodium amber) for the thing that matters — a marked line, the number that gives it away. A muted red is kept for
stamps and verdicts only. Statements in Crimson Pro, labels in condensed caps, anything from a file or a court in
Kode Mono, Hebrew / Yiddish in Frank Ruhl Libre (`media/kit/fonts/FrankRuhlLibre-*.ttf`). Grade `record`: drained
colour, cool shadows, true blacks. Sound: a riser and a low hit on each file, typewriter ticks for typed lines,
paper, a stamp for verdicts, soft whooshes into graphics — all under the voice (`sfx_style: full`, gain 0.6).

Preview: `templates/record/previews/sheet.jpg` · worked example: `projects/hasidic_mesirah/build.py`
(*Why 20,000 Hasidic Jews Were Told To Stay Silent About Crime?*, 18:46).

## Devices (scenes_record.js)

| Device | What it is | Fields |
|---|---|---|
| `docket` | chapter heading: FILE 03 / 10, kicker, title, a typed docket line, the index of files with this one lit | `n, of, kicker, title, line, files[], img, at, size` |
| `transcript` | a ruling / statement / guidance as a line-numbered page; lines arrive as spoken, `[[words]]` get the amber marker | `header, source, lines[], lineAt[], hiAt, size, every, tilt, img` |
| `lexicon` | a term the story turns on: Hebrew word, transliteration, pronunciation, numbered meanings | `word, hebrew, pron, pos, defs[], defAt[], hebAt, hiAt, at` |
| `tally` | a ledger of numbers as bars counting up row by row; a row can be struck; a stamp on the verdict | `kicker, title, rows[{label, value, text, at, hi, strikeAt}], stamp, stampAt, source` |
| `counts` | a sentence board: big counts and what happened after | `kicker, items[{value, label, at, hi, strikeAt}], after, afterAt, stamp, stampAt, cw, numSize` |
| `chain` | a mechanism: nodes joined by arrows lighting on their words; a gate node, a delay clock, a block (×) | `kicker, title, nodes[{label, sub, at, gate}], delay (index), delayAt, delayLabel, blockAt` |
| `redacted` | a list whose names are blacked out one by one, then a stamp — never a real private name | `header, source, rows, labels[], tails[], at, every, stamp, stampAt` |
| `wall` | posters pasted on a night wall; the last carries one word, stamped | `count, at, every, heads[], bigHead, bigAt, word, wordAt, gloss` |
| `docketline` | a time axis (centuries, years or just steps): a marker travels, events land on their words | `from, to, ticks[], events[{year, when, label, at, hi, up}], kicker, title` |
| `ripple` | a person at the centre with the rings of a life; rings appear on their words and are cut away | `center, rings[{label, at, cutAt}], aloneAt` |
| `ballot` | a field of votes turning as one bloc | `kicker, title, blocAt, bloc, note, cols, rows` |
| overlay `casebox` | footage inside the evidence viewer: frame, corner brackets, EXHIBIT number, running timecode, caption, source | `box, exhibit, caption, source, tc0` (render the clip with `inset=box`) |
| overlay `source` | a citation tag, top right: SOURCE — publication, year (typed) | `text, at` |
| overlay `place` | where we are: place name + a typed coordinates / date line, lower left | `name, sub, at` |

Also used from the engine: `photo`, `clip`, `map` (dark map, amber pins), `depth`.

## How it is cut

- **Nothing is written before it is said.** Every device's times come from word timing (`data/words.json`):
  `lineAt`, `hiAt`, `defAt`, `at` on the word (`rel("word", t)` in the example build). Chapter headings say what the
  file is about, never a name or number the narrator has not reached yet.
- **Stock is never plain.** Every stock clip plays in the `casebox` viewer (exhibit number, timecode, caption);
  community footage plays full frame with a `place` line, or in the viewer. **Every clip is under 5 s** — a longer
  line is cut into short shots (the build's last pass), alternating footage and photographs.
- About 30–38 % moving footage, the rest photographs and graphics; a graphic at least every 40 s; one docket per act.
- No faces of victims or private people, no influencers / vloggers / talking heads (QC faceless mode).
- Figures carry their source (`tally.source`, overlay `source`); rulings are transcripts with their source line.

## Footage for this kind of video

1. The niche's own library (Drive): `python niche.py add <niche> <folder>`.
2. Subject stock — **specific, not general** (courtroom, gavel, phone dialing, police lights, case files, ballot box…):
   `python docu/tools/fetch_online.py --out tmp --query "empty courtroom, judge gavel, ..." --clips 3 --photos 2 --sources pexels,pixabay`
   then name the clips `broll_<topic>__...` in `pool/clips/`.
3. Places, texts and posters from Wikimedia Commons (`pool/images/<topic>__wm<id>.jpg`).
4. QC: `python niche.py qc <niche>` (faceless mode).
