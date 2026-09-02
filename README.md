# Automated Long-Form (30+ Minute) Documentary Video Production Pipeline

A high-throughput, 100% GPU hardware-accelerated video production suite designed to automate the end-to-end creation of 30+ minute Full HD (1080p @ 30 FPS) biographical, historical, and investigative documentaries for YouTube.

---

## ⚡ Key Architecture & Features

1. **Async Burst TTS Synthesis (TwoSpeaker ElevenLabs API)**
   - High-throughput multi-threaded chunking (3,800+ word scripts across 12 parallel jobs).
   - Speed `0.95`, Voice ID `gcdNeREzHPJpCf9wnB0l` with automatic exponential-backoff retries.
   - Generates 30+ minutes of studio-grade master narration in under 90 seconds.

2. **Narration-Aware Semantic Matching**
   - Assets are chosen by *what the narration is saying at that second*, not dealt out in a shuffled round robin.
   - **Three label sources**, most reliable first: the folder name (`porter-wagoner/` identifies every file inside it, however uninformative the filename), the filename itself, and an optional tags JSON.
   - **IDF weighting** means terms appearing across most of a library score near zero automatically, so no per-topic tuning is needed.
   - **Named subjects win outright**: when the script names someone other than the documentary's own subject, their footage is used if any is available; keyword overlap cannot outvote it.
   - Falls back to the documentary's own subject rather than showing a different named person.

3. **Semantic Asset & Dynamic Timeline Engine**
   - **Hook Protocol Compliance**: Delivers core topic promise within the first 150 words.
   - **Topic Opening Soundbites**: Integrates topic-specific archival interview clips at $t=0$ to $4.5$s with golden border framing.
   - **Grid Pattern Overlays**: Renders 2–3% of total segments as $1650\times 928$ framed composites over dark curved grid patterns with visible margins.
   - **15-Segment Source Cooldown**: Guarantees zero repetition of camera angles or sub-clips within 15 segments.
   - **Quality Filtering**: Strict exclusion of watermarked, low-contrast, or non-HD assets.

4. **100% Pure GPU NVENC Video Rendering**
   - NVIDIA NVENC hardware acceleration (`h264_nvenc`, VBR 2500 kbps, 6 parallel workers on RTX 3070 Ti).
   - Zero-shake sub-pixel linear perspective Ken Burns motion on 100% of still images.
   - Temporal film grain (`noise=alls=10:allf=t+u`), atmospheric smog/haze softness (`gblur=sigma=1.2`), and vintage grading.
   - Renders 350+ segments for a 30-minute documentary in **under 5.5 minutes**.

5. **Multi-Track Loud Audio Matrix Muxing**
   - **Voiceover Volume Boost**: Master narration boosted to **+75% (`1.75x`)** for crystal-clear speech.
   - **Ambient BGM Ducking**: `Dreamland - Aakash Gandhi.mp3` mixed at `volume=0.08`.
   - Lossless audio concatenation and hardware muxing.

6. **YouTube Upload Metadata Generator**
   - Generates compliant, human-written upload metadata TXT files with character-counted alt titles, full 30+ min chapter timestamps, relevant tags, hashtags, and upload checklists.

---

## 📁 Repository Structure

```
youtube-longform-documentary-pipeline/
├── init_project.py             # Scan a footage folder -> ready-to-run config
├── pipeline.py                 # Master CLI orchestrator
├── voiceover_engine.py         # VoiceoverEngine - TTS + timing manifest
├── semantic_matcher.py         # AssetIndex / ScriptTimeline / SemanticMatcher
├── timeline_engine.py          # TimelineEngine - narration-aware timeline
├── render_engine.py            # RenderEngine - pure GPU NVENC rendering & mux
├── metadata_engine.py          # MetadataEngine - YouTube upload metadata
├── graphic_compositor.py       # GraphicCompositor - the five card styles
├── looks.py                    # Named visual grades and fill modes
├── make_asset_tags.py          # Starter tags JSON for hard-to-label assets
├── configs/                    # Per-topic JSON configs (captions, clip groups)
│   └── dolly_parton.json
├── requirements.txt            # Python dependencies
├── .gitignore                  # Media & cache exclusion
└── README.md                   # System documentation & usage guide
```

Nothing about a given subject lives in the code. Card captions, keyword-matched
clip groups, hook assets and upload metadata all come from the topic config, so
the same four engines drive any documentary.

---

## 🚀 Quickstart & Usage

### 1. Prerequisites
- Python 3.10+
- FFmpeg (configured with `h264_nvenc` and `cuda` support)
- NVIDIA GPU (RTX 3060 / 3070 Ti / 3080 / 4090 recommended)

### 2. Installation
```bash
pip install -r requirements.txt
```

### 3. Start a New Topic in One Command

Point the bootstrap at a folder of footage. It inspects the tree, works out
which folders are subjects, which are generic pools, grids and music, writes a
ready-to-run config, and prints the command to run next:

```bash
python init_project.py --root "D:/Tupac Case" --title "Who Killed Tupac" --script "script.txt"
```

It reports every decision and flags anything ambiguous (build-output folders,
missing grids or music, a subject folder that clashes with `default_entity`)
before you render. Add `--exclude <text>` to skip folders it wrongly picked up.

### 4. Run Pipeline via CLI

With a topic config (recommended - carries captions, clip groups and metadata):

```bash
python pipeline.py --title "Documentary Title" --script "script.txt" --topic-config "configs/dolly_parton.json" --opening-clip "clips/opening.mp4" --output-dir "output"
```

Or entirely from flags, with no config at all:

```bash
python pipeline.py --title "Documentary Title" --script "script.txt" --clips-dir "path/to/clips" --images-dir "path/to/photos" --grid-dir "path/to/grids" --bgm "path/to/bgm.mp3" --output-dir "output"
```

### 5. Useful Flags

| Flag | Purpose |
|---|---|
| `--topic-config` | JSON with card captions, clip groups, hook assets, metadata |
| `--voiceover` | Reuse an existing MP3 and skip TTS entirely |
| `--limit-seconds` | Cap timeline length for a fast smoke test |
| `--skip-render` | Build voiceover, timeline and metadata without rendering |
| `--vo-volume` / `--bgm-volume` | Audio matrix levels (default `1.75` / `0.08`) |
| `--limiter-ceiling` | Peak ceiling for the final mix (default `0.95`, `0` disables) |
| `--clip-cooldown` | Minimum segments between clips from one source (default `15`) |
| `--workers` | Parallel GPU render workers (default `6`) |
| `--frame` | Frame preset: `1080p`, `720p`, `1440p`, `4k`, `vertical`, `square` |
| `--width` / `--height` / `--fps` | Exact frame size and rate, overriding `--frame` |
| `--seg-min` / `--seg-max` | Body segment length range (default `4.5` / `5.8`) |
| `--hook-end` / `--opening-lead` | Hook length and opening soundbite length |
| `--look` | Named grade: `vintage`, `clean`, `warm`, `noir`, `none` |
| `--fill-mode` | How off-aspect sources fill the frame: `blur`, `black`, `crop` |
| `--grade` | Raw FFmpeg filter chain, replacing the look's grade |
| `--border-color` | Opening-clip border, e.g. `0xdc2626` |
| `--no-semantic` | Turn narration-aware matching off |
| `--no-resume` | Re-render segments that already exist |

Directories accept multiple paths joined by the OS path separator, so several
clip or photo folders can feed one render.

### 6. Topic Config Format

```json
{
  "clips_dir": "C:\\media\\clips",
  "images_dir": "C:\\media\\photos",
  "grid_dir": "C:\\media\\grids",
  "bgm": "C:\\media\\music\\bed.mp3",
  "split_cards": [["Main Title", "Supporting subtitle"]],
  "headlines": ["A centered archival headline"],
  "quotes": ["A pull quote from the subject."],
  "clip_groups": [
    {"name": "news_broadcast", "keywords": ["news"], "start": 1350, "end": 1600}
  ],
  "hook_assets": ["hero_image_01.jpg"],
  "alt_titles": ["Alternate title for A/B testing"],
  "tags": ["Documentary"],
  "hashtags": ["#Documentary"],
  "chapter_titles": ["Introduction", "The Turning Point", "Legacy"]
}
```

`clip_groups` route keyword-matched clips into fixed time windows (for example
news footage during a memorial chapter). `chapter_titles` produce evenly spaced
placeholder timestamps marked for review; supply an explicit `chapters` array to
override them with real ones.

### 7. Looks and Framing

The grade is not fixed. `--look` selects one of five bundles, or set `"look"` in
a topic config:

| Look | For |
|---|---|
| `vintage` | Archival biography and true crime - grain, vignette, desaturation (default) |
| `clean` | Nature, travel, food, science - faithful colour, no texture |
| `warm` | Lifestyle and profile pieces - gentle warmth, no texture |
| `noir` | Investigative and historical - high-contrast monochrome |
| `none` | The source exactly as shot |

Override individual parts alongside a look (`--fill-mode`, `--fill-blur`,
`--grade`, `--border-color`, `--fade`, `--zoom-per-sec`), or set the same keys
in the topic config.

**Off-aspect sources.** A portrait photograph in a landscape frame is filled by
default (`--fill-mode blur`) with a scaled-up, blurred, slightly darkened copy of
itself rather than solid black bars. The backdrop is blurred at 1/6 scale, which
is visually identical once blurred and far cheaper than blurring full frames.
`black` restores the old bars; `crop` fills the frame and loses the edges.

**Framing.** `--frame vertical` renders 1080x1920 for Shorts, `--frame square`
1080x1080. Graphic cards are laid out proportionally, so the split-typography
card stacks its photo above its text when the frame is narrower than 4:3.

**Pacing.** `--seg-min` / `--seg-max` set how long each body segment holds.
Shorter values cut faster, which suits vertical and social edits.

```bash
python pipeline.py --title "Trail Notes" --script "script.txt" --topic-config "configs/trail.json" --output-dir "output" --look clean --frame vertical --fps 24 --seg-min 2.5 --seg-max 3.5
```

### 8. Semantic Matching Setup

Organise assets so each folder holds one subject. The folder name becomes the
label; filenames inside it can be as meaningless as `img_0001.jpg`.

```
Media Root/
├── porter-wagoner/     -> entity "porter wagoner"
├── carl-dean/          -> entity "carl dean"
├── knife-skills/       -> entity "knife skills"
└── all-photos/         -> the generic pool
```

Point the config at that root:

```json
{
  "default_entity": "dolly parton",
  "entity_root": "C:\\Users\\me\\Media Root",
  "entity_root_skip": ["Bg music", "grids"]
}
```

`default_entity` is the documentary's own subject: always safe to show, never
penalised. Folders naming more than three people are treated as generic
compilations rather than as one person.

To find which assets still lack usable terms, generate a starter tags file:

```bash
python make_asset_tags.py --topic-config configs/dolly_parton.json --out configs/dolly_tags.json
```

It reports how many assets are already describable and writes a JSON skeleton
covering only the rest, pre-seeded with each file's folder entity. Add scene
keywords, then pass it back with `--asset-tags`.

Timing comes from `voice_manifest.json`, written next to the voiceover during
synthesis. When a manifest is present the script is aligned by exact per-chunk
duration; without one, an even words-per-second estimate is used instead.

Every run writes `timeline_matches.json` beside the timeline, recording what was
chosen for each slot and why, plus a coverage summary reporting how often the
right person appeared when their footage was available.

---

## 📊 Performance Benchmarks (RTX 3070 Ti)

| Stage | Duration | Speed / Efficiency |
|---|---|---|
| **Voiceover Synthesis (3,800 words)** | ~80 - 100 sec | ~20x faster than real-time |
| **Timeline Assembly (350+ Segments)** | ~70 - 80 sec | Automated asset scoring |
| **GPU Video Rendering (30+ Min 1080p)** | ~300 - 330 sec (5.2 min) | ~6x faster than real-time |
| **Lossless Muxing & Metadata** | ~30 - 45 sec | Instant hardware concat |
| **TOTAL PIPELINE EXECUTION** | **~8.5 to 10 Minutes** | **100% Automated** |
