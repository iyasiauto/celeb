# Faceless Documentary Channel: session README

Everything this chat built, what it was built from, and how to pick it up in **any new Claude Code
session** without redoing the setup.

> **Short version (Roman Urdu):** Nayi session mein repo `iyasiauto/celeb` kholo, branch
> `claude/relaxed-goldberg-8akz98` lo, neeche §1 wala prompt paste karo, aur script + voiceover (+ SRT)
> + title attach karo. Claude `docu/tools/bootstrap.sh` chala ke kit aur footage khud download kar lega
> aur video bana dega.

---

## 0. The desktop app: Docu Studio

Everything below is also available as an app: [`studio/`](studio/README.md). Pick a niche, a template style
(built-in, your own folders in `styles/`, or any Frontier style with its sample), give it a script and a voice
(FameSpeak voice ID → MP3 + SRT, or your recording), press **Start production**. The Claude AI editor writes the shot
list by the [visual sync method](docu/VISUAL_SYNC_GUIDE.md), checks the stills, renders, delivers under 1 GB and
writes the YouTube metadata. Windows: unzip `DocuStudio-Windows-x64.zip` and run `Docu Studio.exe`.
From source: `cd studio && npm install && npm start`.

## 1. Launch in a new session (copy-paste)

1. Open a Claude Code session on the GitHub repo **`iyasiauto/celeb`**, branch
   **`claude/relaxed-goldberg-8akz98`** (or `main` once the PR is merged).
2. Paste this prompt and attach the files:

```text
Read DOCUMENTARY_CHANNEL_README.md and docu/VISUAL_SYNC_GUIDE.md first and follow them.
Run docu/tools/bootstrap.sh (deps kit + the footage set I name below), then make the next video.

Title: <title>
Niche / footage: <hasidic | noah | new Drive link: https://drive.google.com/drive/folders/...>
Style: <same template as last video (calm documentary, shuffled look) | new style for this topic>
Clips vs images: <30% clips / 70% images>
Attached: script.txt, voiceover.mp3, voiceover.srt (optional)

Rules: only my footage and images, no AI or stock media; quiet ducked music; final MP4 under 1 GB
without quality loss; gofile link with md5 check; youtube_metadata.txt; commit and push.
```

3. What Claude will run (you don't have to):

```bash
docu/tools/bootstrap.sh deps kit hasidic        # ~10-15 min: packages, asset kit, footage, staged picks
python docu/tools/new_project.py projects/<slug> --title "<title>" \
       --script script.txt --vo voiceover.mp3 --srt voiceover.srt --catalog projects/hasidic_benefits_cut
# write projects/<slug>/build.py (the shot list), then:
docu/tools/run_video.sh projects/<slug> plan prep stills     # check cues + read every still
WORKERS=6 docu/tools/run_video.sh projects/<slug> render mix final deliver
```

A new session is a fresh machine: nothing from this session's disk survives. Everything needed is
either **in the repo** (engine, tools, shot lists, catalogs, word timings) or **re-downloaded from
your Drive** by `bootstrap.sh`.

---

## 2. Your resources used (everything besides script, voiceover and title)

| # | Resource you gave | Link / ID | What was in it | Used for | What exactly was used |
|---|---|---|---|---|---|
| 1 | **GitHub repo** `iyasiauto/celeb` | github.com/iyasiauto/celeb | Your original GPU pipeline (`pipeline.py`, `render_engine.py`, `semantic_matcher.py`, ElevenLabs/Edge TTS voice engine, NVENC renderer) | All videos: the repo is where the new engine `docu/`, the tools and every shot list live (draft PR iyasiauto/celeb#1) | Your original pipeline code was **read, not run**: this cloud machine has no NVIDIA GPU, so a CPU engine (`docu/`) was built beside it. Nothing of yours was deleted or changed |
| 2 | **Asset kit** ("Yahan tumhen sb mil jayga music, sound…") | Drive `1CYxavMgiqBwVtUwFMizA-Txnf4123yYq` | Frontier-style kit: music, fonts, maps, cut-outs, cinema, kits, textures, avatars, brand, memes, vox, styles, headlines, photofx, overlays | **All 6 videos** | **music/**: all background beds (18 tracks, e.g. *Leaving Home*, *Sovereign Dark Piano*, *Unanswered Questions*, *Efteraar*, *Silent Tension Piano*) · **fonts/**: Playfair, DM Serif, EB Garamond, Lora, Inter, Barlow, Oswald, Montserrat, Poppins, Roboto Condensed, Anton, Courier Prime… · **maps/**: world + state/province geodata (`geo_hi.json`, `geo_lo.json`, relief) for every map animation · **cutouts/**: vintage objects (open book, stack of books, magnifying glass, writing hand, Bible) · **cinema/**: TV set for the "picture on a TV" scene · **kits/frames**: cork board texture. **Not used:** avatars, brand, characters, memes, vox previews, styles previews, headlines, photofx, VHS/dust/light-leak overlays. Sound effects were **synthesised in code**, not taken from the kit |
| 3 | **Noah's Ark project folder** | Drive `16RNSweyA9msU88S1aAOrah5CtLNvBop6` | Script (and later the video 2 script/voiceover) | Videos 1–2 | Script text only (no footage in this folder) |
| 4 | **Noah's Ark footage** | Drive `1HstYp4jR91BpL8QzGuBKUdaRqNpBOEar` | `clips/approved`, `clips/candidates`, `images/approved`, `images/candidates`, `source_video/` (10 long source videos), `Individual Images/` (2 viral posts × 5 images), `Individual Videos/` | **Videos 1–4** (Noah's Ark) | Clips cut from the source videos (~20 % of each video), approved + candidate images, the two viral posts' images (as `work/ind/ind1_*`, `ind2_*`) for the "viral claim" scenes |
| 5 | **Hasidic "Data and Pipeline" folder** | Drive `1iubj0u5xQdc_wO-I986zobwx5eLnUasm` | `clips/` (525 short clips, ~58 min) and `images/` (2,845 pictures, by topic: money, children, street, institutions, study, Shabbat, food, maps, historical…) | **Videos 5–6** (Hasidic niche) | 351 clean clips catalogued, 587 pictures picked. Video 5 used 72 pictures + 55 clips; video 6 used 101 **different** pictures + 66 **different** clips |
| 6 | **Your uploads per video** | chat attachments | script `.txt`, voiceover `.mp3` (voices "Jeremy – Warm, Trustworthy", "Peter – Engaging and Informative", and others), and for video 6 an `.srt` | the video each came with | the SRT for video 6 gave instant, exact word timings |
| 7 | **Your editing brief** | chat messages | the rules collected in §4 | all videos | |

**Not used, on purpose:** no AI-generated images or video, no stock sites, no Wikimedia or web
downloads, no TTS (your voiceovers only). The only things the engine *draws* itself are graphics:
maps from the kit's geodata, charts, text cards, paper boards and the simple props from
`docu/tools/props.py` (envelope, notice, receipt, Yiddish shopping list).

---

## 3. Tools and software used (mine, not provided by you)

| Tool | Why |
|---|---|
| **`docu/` engine** (written in this chat) | Scenes as HTML/JS drawn frame by frame in headless Chromium; shot list = Python (`build.py`) |
| Python 3, NumPy, SciPy, Pillow | engine, picture grading, sound synthesis and mixing |
| **FFmpeg / libx264** | clip trimming and grading, dissolves, encoding (CRF 18), muxing, loudness |
| **Playwright + Chromium (headless)** | renders every designed scene at 1920×1080, 30 fps |
| **rembg** | cuts people or objects out of photos for depth-pop scenes |
| **faster-whisper** | word timestamps when there is no SRT |
| **gdown** | downloads your Drive folders (`fetch_drive.py`, 12 files in parallel) |
| **gofile.io** (via `curl`) | temporary download links for finished videos and zips, md5 verified |
| GitHub (MCP tools) | commits, pushes, the draft PR |

---

## 4. The standing brief (your rules, collected)

| Rule | Where it came from | How it's applied |
|---|---|---|
| Faceless documentary / investigative commentary, high quality | video 1 | 1080p30, −14 LUFS, every cut on the spoken word |
| **Only your footage and images: no AI, no stock** | video 1 | assets only from Drive folders #4 and #5 |
| Scenes wanted: depth pop, motion graphics, Vox-style paper scenes, map animations, photo spotlight, real objects, newspaper animations, sound design | video 1 | all exist as scene types (`docu/templates/README.md`) |
| **Background music quiet, ducked** ("bilkul lite") | after video 1 | `music_floor_db=-21`, `music_duck_db=-10`, `sfx_gain=0.55` |
| **Change the editing style per topic** | video 2 onwards | 5 styles so far (§5); a new topic gets a new style unless you ask for the same one |
| Templates + detailed README after each new style | videos 3–6 | `docu/templates/` (+ zips) |
| **Under 1 GB without visible quality loss** | video 2 | grain ≤ 2, CRF 18; `deliver.py` re-encodes only if needed |
| Delivery via **gofile link**, md5 checked | video 1 | `deliver.py` |
| Noah's Ark niche: ~20 % clips / 80 % images | video 1 | `plan` prints the share |
| Documentary niche: **30 % clips / 70 % images, not fast-paced, not complicated, no heavy editing, audience must not get confused, no forensic/case-file look** | videos 5–6 | the calm documentary template |
| **Same template, but shuffled per video so it never looks template-generated** | video 6 | `vary="auto"` + asset rotation (`docu/variety.py`) |
| Pipeline integration zip with tools, features and assets listed | video 6 | `docu/INTEGRATION.md` + the kit zip |

---

## 5. What was produced

| # | Title | Style | Length · size | Clips | Download |
|---|---|---|---|---|---|
| 1 | Noah's Ark Confirmed After 4,300 Years? What We Actually Know | A · Paper / Vox explainer | 19:24 · 1.35 GB | ~23 % | gofile.io/d/RsdLaJWd |
| 2 | Noah's Ark "100% Confirmed"? Here's What Researchers Actually Found | B · Forensic lab report | 26:26 · 899 MB | ~19 % | gofile.io/d/2q6EfLuM |
| 3 | Myth or Reality? Hunting for the REAL Noah's Ark | C · Expedition & courtroom | 13:47 · 497 MB | 21 % | gofile.io/d/KG3bq2ip |
| 4 | BREAKING: They Drilled Into Noah's Ark — Then the Drill Bit Shattered | D · Breaking-news broadcast | 22:36 · 740 MB | 19 % | gofile.io/d/nvRT5qos |
| 5 | How Do Hasidic Jews Afford 10 Kids Without Jobs | E · Calm documentary (gold) | 17:24 · 652 MB | 30 % | gofile.io/d/DmmRYiEV |
| 6 | What Happens If the Government Cuts Hasidic Jews Community Benefits? | E · Calm documentary, shuffled (teal) | 16:41 · 647 MB | 29 % | gofile.io/d/8NIRzf0R |

Template / kit zips: styles A–C gofile.io/d/t5QDjqF0 · style D gofile.io/d/NwcIDgKi ·
style E gofile.io/d/QDjrkt9y · **full pipeline kit** gofile.io/d/kRaYhoTJ.
Free gofile links expire after some days without downloads: keep your own copies in Drive.
Every video can be rebuilt from the repo: `python projects/<video>/build.py all`.

---

## 6. Where everything is

```
DOCUMENTARY_CHANNEL_README.md   this file
docu/
  INTEGRATION.md                pipeline integration: inputs, outputs, stages, features, variety
  VISUAL_SYNC_GUIDE.md          how the right clip/picture lands on the right word (any niche)
  templates/README.md           every style A-E, every scene type and option, with previews
  templates/starter_documentary the project to copy for a new calm documentary
  tools/bootstrap.sh            fresh machine -> ready (deps, kit, footage, picks)
  tools/                        fetch_drive, catalog_clips, catalog_images, srt2words, transcribe,
                                props, new_project, deliver, run_video.sh
  edl.py timing.py prep.py render.py mix.py variety.py engine.* scenes_*.js   the engine
projects/<video>/
  build.py                      the shot list (every scene, cued on script phrases)
  data/                         script.txt, words.json, catalog_all.json, image_picks.json,
                                notes_*.txt, assets_used.json (look + assets used)
  youtube_metadata.txt          title, A/B titles, description, chapters, tags
media/                          (git-ignored, made by bootstrap.sh) kit/, footage/, hasidic/, work*/, out/
```

---

## 7. Making the next video (the workflow)

1. **Setup:** `docu/tools/bootstrap.sh deps kit <footage set>`. For a new niche, add its Drive link:
   `python docu/tools/fetch_drive.py <link> media/<niche>/src`, then catalog it (step 3).
2. **Project:** `new_project.py` copies the template, sets `vary="auto"`, makes `words.json` from the
   SRT (or Whisper) and prints the start time of every paragraph. Plan the chapters from that.
3. **Visuals (new footage only):** `catalog_clips.py scan` / `catalog_images.py scan`. Read every
   contact sheet, write `notes_clips.txt` / `notes_img.txt`, then run `build` / `pick`. Same niche as
   before: skip this, since the catalog is copied with `--catalog`.
4. **Shot list:** write `build.py` following `docu/VISUAL_SYNC_GUIDE.md`. List unused material with
   `catalog_*.py list … --unused projects`.
5. **Check:** `plan` (all cues found, clip share, 0 reused, no clip warnings) → `prep` → `stills`,
   and read every still.
6. **Build:** `render` (~25 min per 16 min of video on 8 cores) → `mix` → `final` → `deliver`
   (size, loudness, gofile, md5).
7. **Hand over:** gofile link, `youtube_metadata.txt`, commit and push.

Style choice: same niche and you liked the look → same template with `vary="auto"`. New topic →
pick or build a new style (`docu/templates/README.md` §3 lists which style suits which topic).

---

## 8. Known limits

| Limit | What to do |
|---|---|
| Claude can't write to your Google Drive (share links are view-only) | delivery is by gofile link; download and move the file to Drive yourself |
| File attachments in chat are limited to ~30 MB | videos always go through gofile |
| Each session is a new machine | `bootstrap.sh` re-downloads kit + footage (~10–15 min) |
| Rendering is CPU-only here | ~25 min for a 16-min video with `WORKERS=6`; your GPU pipeline could be used locally instead |
| gofile uploads need permission for `curl` to gofile | allow it once in Claude Code settings if asked |
| Music licences | the tracks come from your kit; confirm their licences before publishing |
| Drive folders must be shared "Anyone with the link" | otherwise `fetch_drive.py` can't list them |
| Frontier styles | rendered by Frontier's own engine with its `.env` keys (Algrow, Gemini, …); the app only drives it |
| API keys | names and setup in `api_keys/README.md`; values go in the cloud environment's variables (or a git-ignored `api_keys/keys.env`), never in chat or git |
