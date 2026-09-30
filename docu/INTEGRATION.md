# Integration guide: the calm documentary pipeline

This kit turns **a script, a voiceover and a folder of real footage and pictures** into a finished,
faceless documentary: 1080p30 MP4, a quiet music bed, soft sound design, under 1 GB. It is the
pipeline behind:

| Video | Length | Look (picked by `variety.py`) |
|---|---|---|
| *How Do Hasidic Jews Afford 10 Kids Without Jobs* | 17:24 | gold accent · Playfair + Inter · "Chapter 3" · grade doc |
| *What Happens If the Government Cuts Hasidic Jews Community Benefits?* | 16:41 | teal accent · DM Serif + Barlow · "Part Three" · grade doc · 0.62 s dissolves |

Both use the same template, the **calm documentary** (§5). Each video still looks different, because
a per-video seed shuffles the look and the asset rotation keeps the pictures fresh (§7).

No AI images, no stock footage. Every picture and clip comes from your own folders, and the graphics
(maps, charts, text cards, drawn props) are drawn by the engine.

---

## 1. What is in the zip

```
docu/                         the engine: copy this folder into your pipeline as it is
├── INTEGRATION.md            this guide
├── README.md                 engine overview
├── requirements.txt          Python packages
├── edl.py                    shot helpers (photo, clip, depth, spot, collage, …) + build commands
├── variety.py                per-video look shuffle + asset rotation              (§7)
├── timing.py                 script phrases → voiceover word times
├── prep.py                   picture grading, blur/dim variants, cut-outs, paper surfaces
├── render.py                 headless Chromium / FFmpeg → one MP4 per scene, dissolves, concat
├── mix.py                    synthesised SFX, music beds, ducking, −14 LUFS
├── engine.html, engine.js    the page, themes, fonts, overlays
├── scenes_*.js               scene types (photo, paper, data, map, doc, news, lab, court)
├── tools/                    pipeline tools                                        (§3)
│   ├── fetch_drive.py        parallel download of a shared Drive folder
│   ├── catalog_clips.py      footage → numbered contact sheets → catalog_all.json
│   ├── catalog_images.py     pictures → topic sheets → staged picks + image_picks.json
│   ├── srt2words.py          SRT → word timestamps (instant)
│   ├── transcribe.py         voiceover → word timestamps with Whisper (when there is no SRT)
│   ├── props.py              drawn "real object" props: envelope, notice, receipt, shopping list
│   ├── new_project.py        scaffold a new video from the template
│   ├── deliver.py            checks, shrink under 1 GB, gofile upload with md5 check
│   └── run_video.sh          all stages in one command
└── templates/
    ├── README.md             every style, scene, option, SFX and delivery rule, with previews
    ├── snippets.py           ready-made builders (doctitle, textcard, doc_bars, ledger_list, ph, prop, …)
    ├── starter_documentary/  the template to copy for a new video in this style
    └── previews/             preview images of every scene
projects/
├── hasidic_10_kids/          worked example 1 (build.py = the full shot list)
└── hasidic_benefits_cut/     worked example 2 (build.py = the full shot list)
kit/                          fonts, maps, cut-outs + props, music, textures used by the engine
```

---

## 2. Requirements and settings

| Need | Version / note |
|---|---|
| Python | 3.10+ |
| Python packages | `pip install -r docu/requirements.txt` (numpy, scipy, Pillow, playwright, rembg, onnxruntime, faster-whisper) and `pip install gdown` for Drive downloads |
| FFmpeg | with libx264, on `PATH` |
| Chromium | `playwright install chromium`, then `export DOCU_CHROME=<path to chrome or headless_shell>` |
| CPU / RAM | 8 cores and 16 GB recommended. No GPU needed |
| Disk | about 6 GB per 16-minute video while it renders (segments + assets); the final file is under 1 GB |

**Environment variables** (all optional; each project's `build.py` falls back to its own `media/` folder):

| Variable | Meaning |
|---|---|
| `DOCU_DIR` | where `docu/` is, if the project is not inside the same tree |
| `DOCU_CHROME` | Chromium binary for rendering |
| `VIDEO_ROOT` | one folder holding `kit/`, `footage/`, `work/`, `out/` |
| `VIDEO_KIT` / `VIDEO_FOOTAGE` / `VIDEO_WORK` / `VIDEO_OUT` | override any one of them |
| `WORKERS` | scenes rendered in parallel (default 4; 6 on 8 cores) |

**Running the two example projects** (their defaults point at this production's folders):

```bash
export VIDEO_KIT=$PWD/kit                                  # the kit/ from this zip
export VIDEO_FOOTAGE=/data/hasidic/footage                 # contains source_video/ (the Drive clips)
export VIDEO_IMAGES=/data/hasidic/src/images               # the Drive pictures
export VIDEO_PICKS=/data/hasidic/picks                     # staged by catalog_images.py pick
export VIDEO_WORK=/data/work/benefits  VIDEO_OUT=/data/out
python projects/hasidic_benefits_cut/build.py plan
```

---

## 3. The pipeline, stage by stage

```
 Drive folder ──fetch_drive──▶ footage/source_video/*.mp4 + images/*.jpg
                                   │
          catalog_clips scan ◀─────┤────▶ catalog_images scan        (contact sheets)
          notes_clips.txt  (you)   │      notes_img.txt  (you)      (what is in each shot/picture)
          catalog_clips build      │      catalog_images pick        (catalog_all.json, image_picks.json, picks/)
                                   ▼
 script.txt + vo.mp3 (+ .srt) ──new_project──▶ projects/<video>/build.py + data/
                                   │
                    you write the shot list in build.py   (§5, §6)
                                   │
      plan ─▶ prep ─▶ stills (QA) ─▶ render ─▶ mix ─▶ final ─▶ deliver
```

### Inputs (per video)

| File | Where | Format |
|---|---|---|
| Title | `new_project.py --title` | becomes the MP4 file name |
| Script | `data/script.txt` | the narration **exactly as recorded**, one paragraph per line |
| Voiceover | `<work>/vo.mp3` | the recorded narration (any length) |
| Subtitles (optional) | `data/voiceover.srt` | if present, word times come from it instantly (`srt2words.py`); otherwise Whisper (`transcribe.py`, about 2 min per 15 min of speech on CPU) |
| Word times | `data/words.json` | `[{"w": "Eleven", "s": 17.52, "e": 17.9}, …]` |
| Clip catalog | `data/catalog_all.json` | `[{"i": 24, "video": "abc.mp4", "s": 0, "e": 8.0, "quality": 4, "flags": [], "tags": ["wedding"], "desc": "…"}]`; `clip(24)` uses entry 24 |
| Picture picks | `data/image_picks.json` + `picks/<key>.jpg` | `ph("money_00_4")` finds `picks/money_00_4.jpg` |

**Footage layout** (`VIDEO_FOOTAGE`): `source_video/` holds every clip file named in the catalog.
Pictures can live anywhere; list their folders in `image_dirs=[picks_dir, originals_dir]`.

### Outputs

| File | What |
|---|---|
| `<out>/<Name>.mp4` | H.264 1080p30 (CRF 18), AAC 256 kb/s, −14 LUFS, true peak −1.2 dB |
| `<out>/<Name>.link.txt` | gofile page and md5 (after `deliver`) |
| `data/assets_used.json` | this video's look + every picture and clip it used (read by the next video) |
| `<work>/scenes.json` | the resolved timeline (scene, start, duration, spec) |
| `<work>/stills/*.jpg` | one QA frame per designed scene |
| `youtube_metadata.txt` | title, A/B titles, description, chapters, tags (write per video; see the example projects) |

### Commands

```bash
# 0. once per footage folder
python docu/tools/fetch_drive.py "<drive folder url>" media/footage_raw 12
python docu/tools/catalog_clips.py scan  media/footage/source_video media/cat          # then write media/cat/notes_clips.txt
python docu/tools/catalog_clips.py build media/cat projects/my_video/data/catalog_all.json
python docu/tools/catalog_images.py scan media/footage/images media/cat               # then write media/cat/notes_img.txt
python docu/tools/catalog_images.py pick media/cat media/footage/images media/footage/picks projects/my_video/data/image_picks.json
python docu/tools/props.py media/kit/cutouts                                          # the drawn props

# 1. a new video
python docu/tools/new_project.py projects/my_video --title "My Title" \
       --script script.txt --vo voiceover.mp3 --srt voiceover.srt --catalog projects/previous_video
#    prints the start time of every paragraph: plan the chapters from it

# 2. choose visuals nobody has seen yet
python docu/tools/catalog_clips.py  list projects/my_video/data/catalog_all.json --unused projects
python docu/tools/catalog_images.py list projects/my_video/data/image_picks.json --unused projects

# 3. write the shot list in projects/my_video/build.py, then:
docu/tools/run_video.sh projects/my_video plan          # cues, clip share, reuse count, variety picks
docu/tools/run_video.sh projects/my_video prep stills   # read every still (QA checklist §9)
WORKERS=6 docu/tools/run_video.sh projects/my_video render mix final deliver
```

Every stage is **resumable**. `python build.py render s042 s043` re-renders two scenes after a fix;
`python build.py stills s042` redraws one QA frame.

### Calling it from Python (instead of the CLI)

A `build.py` is plain Python, so another pipeline can generate it or drive it:

```python
import sys; sys.path.insert(0, "docu"); sys.path.insert(0, "docu/templates")
import edl
from edl import *
from snippets import *
edl.setup(name="My_Title", kit=KIT, footage=FOOT, work=WORK, data="projects/x/data", out=OUT,
          image_dirs=[PICKS, IMAGES], theme="documentary",
          music_floor_db=-21.0, music_duck_db=-10.0, sfx_gain=0.55, sfx_style="calm", vary="auto")
at(0.0, place_cap(ph("maps_00_40"), "Kiryas Joel, New York"))
at("Eleven people live in this house", stat("11", "PEOPLE IN THIS HOUSE", bg="women_00_20"))
...
sys.argv = ["build.py", "plan"]; edl.main(music=[...])      # then "prep", "render", "mix", "final"
```

### Timings (8 vCPU, `WORKERS=6`, 16:41 video, 166 scenes)

| Stage | Time |
|---|---|
| srt2words / plan | seconds |
| prep (105 pictures + cut-outs) | ~2 min |
| stills (112 frames) | ~40 s |
| render (166 scenes) | ~25 min |
| mix | ~1 min |
| final (dissolves + mux) | FINAL_TIME |
| deliver (upload) | 1–3 min |

---

## 4. Writing the shot list

A cue is **the exact phrase of the script that the cut lands on**. Inside a scene, `"@phrase"` times
an element to that word, and a number times it in seconds from the scene start.

```python
at("Eleven people live in this house", big("11", "PEOPLE IN THIS HOUSE", "one household, one envelope", bg="women_00_20"))
at("Lower a threshold", ledger("What a real cut looks like", [
        ("Lower a threshold", "", 0.1),
        ("Tighten a test", "", "@Tighten a test"),
        ("Cap a credit", "", "@Cap a credit")]))
```

`plan` resolves every cue against the voiceover and prints the clip share, the variety picks, how
many assets repeat from earlier videos, and warnings for clips too short for their words. A cue it
can't find is reported by name: pick a longer or more unusual phrase.

**Rule of thumb for 16 minutes:** about 160 scenes, 5–8 s each, one scene per sentence or two.

---

## 5. The template: calm documentary

The brief this template answers: *"documentary style, not fast-paced, not complicated, the audience
must not get confused; 30 % clips and 70 % pictures."*

| Rule | Setting / how |
|---|---|
| Footage share **about 30 %**, pictures and calm graphics 70 % | `plan` prints the share: `clips 288.6s (29%)` |
| Long, quiet shots (5–10 s), slow camera moves | `ph(key)`: Ken Burns in/out/left/right/up, zoom 1.08 |
| **Soft dissolves** between every shot | `xfade` 0.45–0.8 s (picked per video); every cut still lands on its word |
| **Chapter heading** per act, and a new music bed under each | `heading(n, "Title", bg)` / snippets `doctitle(n, …)` |
| One idea per text card, one to three lines, the key words in the accent colour | `card(("line", at), ("key line", "@word", ACC))` |
| Location captions, name lower thirds | `place(scene, "Kiryas Joel, New York", "sub")`, `who(scene, "Hatzalah", "volunteer ambulance service")` |
| **One recurring device** the audience learns once | video 1: a household ledger that gains a layer per chapter · video 2: the brown envelope prop on a paper table + "what the street runs itself" list |
| Numbers shown gently | `big()` counter, `bars()` horizontal, `sizechart()`, `ledger()` lists; mark **illustrative** figures on screen |
| Maps for every place | `type="map"` with a highlight, pins, a route, or dots across the country |
| Claims labelled as claims | e.g. "The $100,000 figure is… asserted / not verified / not published by any agency" |
| Sound: soft only | `sfx_style="calm"`: paper, pen, soft ticks and pings. No whooshes, stamps or impacts |
| Music far under the voice | `music_floor_db=-21`, `music_duck_db=-10`, `sfx_gain=0.55`, calm beds only |

### Chapter plan used for video 2 (16:41)

| Time | Chapter | Recurring device |
|---|---|---|
| 0:00 | Cold open: the envelope on the kitchen table, the street, "the switch" | envelope + notice + shopping list props |
| 2:40 | Title: *What Happens If the Benefits Are Cut?* | |
| 2:51 | Part One: There Is No Switch | the four programmes on a paper board |
| 3:59 | Part Two: A Different Lever | envelope vs. ambulance + school bus |
| 4:54 | Part Three: How the Envelope Is Filled | "Inside the envelope" ledger |
| 8:02 | Part Four: Substantially Equivalent | NY State map, 7:30 am – 9:30 pm |
| 10:18 | Part Five: What the Street Runs Itself | the seven institutions list |
| 11:15 | Part Six: Who Absorbs a Cut | "Who absorbs a cut first?" ledger |
| 12:58 | Part Seven: The Case Against | |
| 15:37 | And yet: Your Envelope | the envelope again, then the viewer's |

---

## 6. Features and assets used (and which matter most)

### Scene types (★ = carries the style; use in every video)

| Feature | Helper | Used for |
|---|---|---|
| ★ Photograph with slow move | `ph(key)` / `photo()` | most of the 70 % |
| ★ Footage clip | `cl(i)` / `clip(i, then=(j,))` | the 30 %; `then=` joins shots when one is too short |
| ★ Chapter heading | `heading(n, title, bg, sub)` | one per act |
| ★ Text card | `card(*lines, bg)` | the lines the narrator stresses |
| ★ Location caption | `place(scene, text, sub)` | first time each place appears |
| ★ Recurring device | `ledger()` list, paper `board()` with `prop()` | the thread of the video |
| Name / role lower third | `who(scene, name, role)` | institutions, people, sources |
| Big number | `big(value, kicker, note, bg, source)` | one headline figure at a time |
| Bar chart | `bars(title, rows, …)` | two or three values compared |
| Household-size chart | `sizechart` | "same income, bigger family" |
| Ledger / list | `ledger(title, rows, total)` | lists that fill in on the words |
| Map | `dict(type="map", …)` | states, pins, routes, dots across the country |
| Paper board (Vox, calm) | `board([pc(), strip(), prop(), title_()])` | real objects and documents on a table; everything fades in |
| Photo spotlight | `spot(key, center, radius, label)` | "through a child's desk", "absorbed by a family" |
| Depth pop | `depth(key, subject)` | a person lifted off the background (use sparingly) |
| Fade in / fade out | `overlays=[dict(type="fadein", d=1.2)]` | first and last scene |

### Assets

| Asset | Where | Notes |
|---|---|---|
| Pictures | your Drive folder → `picks/<key>.jpg` | about 100 per 16-min video |
| Clips | your Drive folder → `footage/source_video/` | about 55–65 shots per 16-min video; avoid flagged shots (presenter, subtitles, logos, interviews) |
| Drawn props | `kit/cutouts/prop_*.png` from `tools/props.py` | envelope, school notice, till receipt, Yiddish shopping list; add your own functions for new topics |
| Vintage cut-outs | `kit/cutouts/*.png` | magnifying glass, open book, key, lock, question mark, … |
| Fonts | `kit/fonts/` | Playfair, DM Serif, EB Garamond, Lora, Inter, Barlow, Montserrat, Roboto Condensed, Poppins, Oswald |
| Maps | `kit/maps/` | world + `geo_hi.json` states/provinces (US ids: NY `USA-3559`, NJ `USA-3558`, PA `USA-3560`, CT `USA-3537`) |
| Music | `kit/music/` | calm beds: Leaving Home, Sovereign, Sad Trio, Unanswered Questions, Magic Forest, Efteraar, Silent Tension Piano, Slow Dramatic Ascent, Hopes Mysterious, Metaphysik |
| SFX | synthesised in `mix.py` | no files needed |

---

## 7. Variety: so videos never look template-generated

Two mechanisms, both automatic once `edl.setup(..., vary="auto")` is set.

### 7.1 The look is shuffled per video

A seed made from the video's name (`vary="auto"`, or `vary=1234` to pin one) picks:

| What | Options | Rule |
|---|---|---|
| Accent colour | gold, copper, teal, sage, rose, slate, amber, ivory | never the same as the previous video |
| Font pairing | 5 sets (heading serif + caption sans + italic) | never the same as the previous video |
| Chapter heading style | "Chapter 3" · "Part III" · "03" · "— 3 —" · "Part Three" | never the same as the previous video |
| Picture grade + grain | doc 1.0 / 1.5 / 2.0, cool 1.5 | |
| Dissolve length | 0.45–0.8 s | |
| Camera-move cycle | 4 different orders of in / out / left / right / up | `ph()` without `move=` takes the next one |
| Caption corner | bottom-left, top-left, bottom-right | |
| Text-card darkness | 0.55–0.68 | |
| Music order | all beds shuffled; a track that no earlier video opened with comes first | |

In `build.py`: `V = edl.V`, then `V.kicker(3)`, `V.move()`, `V.accent`, `V["music"]`, `V["dim"]`.
The snippets (`doctitle`, `textcard`, `ph`, `accent()`) already use them.
See the looks used so far and preview the next one:

```bash
python docu/variety.py projects "Next Video Title"
```

### 7.2 Assets rotate between videos

Each `plan` writes `data/assets_used.json` (the look and every picture and clip used). The next video
reads all of them:

- `plan` prints **`reused from earlier videos: N of M`**. Aim for 0; video 2 is at 0 of 167.
- `catalog_*.py list … --unused projects` lists only material no video has used yet.
- `V.fresh(candidates, n)` picks unused keys at random (seeded) when you want the engine to choose.

### 7.3 What you vary by hand (the engine can't)

| Vary per video | Video 1 | Video 2 |
|---|---|---|
| The recurring device | household ledger, one layer per chapter | brown envelope prop + "what the street runs itself" |
| Opening | aerial photo + a big number | paper table with props, then the street |
| Chart types | sizechart, bars, 7-layer ledger | ×1/×2/×4 bars, US dots map, "Inside the envelope" ledger |
| Map moves | NY → KJ route, Israel globe | NYC-area pins, US dots, two-household map, NY State |
| Ending | the village with fade-out | the viewer's envelope + aerial with fade-out |

Keep the **rules** of §5 fixed (that is the template) and change the **devices** (this table).

---

## 8. Integrating into an existing pipeline

- **Drop in:** copy `docu/` and `kit/` next to your projects. Each video is one folder with
  `build.py` + `data/`. Nothing is installed system-wide.
- **As a stage:** call `tools/run_video.sh <project> [stages]`. It exits non-zero on failure and
  every stage can be re-run. Read the final path with `python build.py path`.
- **Generated shot lists:** your pipeline can write `build.py` (or call `edl.at()` directly) from
  its own shot plan. Cues are plain script phrases, so any planner that outputs "phrase → scene"
  works. Run `plan` first; it lists every cue it can't place.
- **Parallel videos:** give each video its own `VIDEO_WORK`. Renders share nothing else.
- **Keep `projects/*/data/assets_used.json`** in your repo or storage. That is the memory the
  variety and asset rotation read.

---

## 9. QA checklist

- [ ] `plan`: all cues found (alignment ≥ 95 %), clips at 25–35 %, no clip warnings, reuse 0.
- [ ] `stills`: read every frame. Check that no text is cut off at the edges, labels don't overlap, and the picture matches the words (a photo of a court in another country must not be labelled as the local one).
- [ ] No private data visible (names on benefit cards, addresses, faces of children in close-up with names).
- [ ] Anything the script calls a claim is labelled as a claim on screen; invented example numbers say **illustrative**.
- [ ] No fake mastheads or logos of real publications. Props stay generic.
- [ ] After `final`: watch the opening, every chapter change and the ending; check the loudness (−14 LUFS) and the size (< 1 GB).

## 10. Troubleshooting

| Symptom | Fix |
|---|---|
| `cue not found` in plan | copy the phrase exactly from `script.txt`; pick a rarer phrase |
| Clip warning "needs 7 s, has 3 s" | `clip(i, then=(j, k))` joins more shots, or use a photo |
| Spotlight label outside the frame | fixed in the engine (labels are kept inside); use `side="left"` for subjects on the right |
| Map labels overlap | fewer pins, merge nearby ones ("Williamsburg · Borough Park"), or zoom in |
| Hebrew or Yiddish text reversed on a prop | Pillow needs libraqm; `props.py` falls back automatically |
| Video over 1 GB | `deliver.py` re-encodes at the right bitrate; or lower `grain` |
| gofile upload reset | `deliver.py` retries other servers and checks the md5 |
| Anything else | `templates/README.md` §12 |
