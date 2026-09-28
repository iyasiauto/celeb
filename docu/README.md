# docu: motion-graphics documentary engine

A second renderer beside the Ken Burns pipeline, for faceless investigative documentaries that need
designed scenes: Vox-style paper collages, depth pop, photo spotlights, map animations, newspapers,
stat counters, and sound design timed to the picture.

The engine turns an edit decision list (EDL) into a finished MP4:

| Step | Module | Output |
|---|---|---|
| Timing | `timing.py` | Script phrases mapped to word timestamps of the voiceover |
| Assets | `prep.py` | Graded pictures, blur/dim variants, rembg cutouts with baked keylines, paper textures |
| Picture | `engine.html` + `scenes_*.js`, driven by `render.py` | One H.264 segment per scene, from headless Chromium or FFmpeg (clips) |
| Sound | `mix.py` | Synthesised SFX spotted from the scenes, music beds per act, ducking, loudness at -14 LUFS |

## Scenes

Every scene is a pure function of time: `setupScene(spec)` builds it, `renderFrame(t)` draws frame `t`.
Workers can render any frame in any order, and a scene can be re-rendered alone.

| Type | What it draws |
|---|---|
| `photo` | Ken Burns over a still (cover, or contain over a blurred copy) |
| `depth` | Depth pop: the cut-out subject lifts off a blurred, dimmed ground |
| `spotlight` | The frame dims except one region; a red ring and a label land on it |
| `collage` | Paper tabletop: photo cards, halftone cutouts, stamps, typewriter strips, pins, red string, arrows, stat cards, notes |
| `newspaper` / `headlines` / `card` / `tv` | Newsprint page with a marker sweep, torn headline strips, a found post, a picture on a TV set |
| `map` | Orthographic globe to province (Natural Earth): highlights, pins, routes, distance circles |
| `stat` / `quote` / `words` / `ledger` / `checklist` / `timeline` / `measure` | Counters, quotes revealed word by word, kinetic type, handwritten arithmetic, ticked lists, dated rails, bar comparisons |
| `chapter` / `title` / `baskets` / `split` | Chapter cards, the title, three case folders, before/after split |
| `geo` | Animated geology cross-sections (syncline fold, slumped block with karst) |
| `clip` | A catalog shot, or several joined together, trimmed and graded by FFmpeg |

## Writing an EDL

See `projects/noahs_ark/build.py`. A cue is the phrase of the script that the cut lands on. Inside a
scene, `"@phrase"` times an element to its word:

```python
at("In 1959, a Turkish army cartographer", collage([
    pc("cand_05", 600, 540, 700, rot=-3, at=0.0, grade="bw"),
    strip("NATO aerial mapping mission", 1330, 560, at="@NATO mapping mission"),
    stamp("1959", 1350, 250, at="@In 1959")]))
```

`python build.py plan` checks every cue against the voiceover. `stills` renders one QA frame per
scene. `render`, `mix` and `final` build the video. Renders resume, and `render s042 s043` redoes
only those scenes.

## Requirements

Python 3.10+, FFmpeg (libx264), Playwright with Chromium, Pillow, NumPy, SciPy, rembg, and
faster-whisper for word timestamps. An NVIDIA GPU is not needed.
