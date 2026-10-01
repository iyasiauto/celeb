# Docu Studio: the desktop app

A premium desktop tool around this repo's documentary pipeline. You pick a **niche pipeline**, a **template style**
and a **voice**, press **Start production**, and the studio makes the video the same way the channel's videos were
made by hand in this project: word-exact timing, catalogued footage, a shot list written to the
[visual sync method](../docu/VISUAL_SYNC_GUIDE.md), stills QA, render, quiet mix, under-1-GB delivery, YouTube metadata.

```
Create video ─▶ Productions (live) ─▶ Library
   niche · style · script · voice · clip share · AI editor · AI QA · upload
```

## What it does, stage by stage

| Stage | What happens | Needs |
|---|---|---|
| Voiceover | **FameSpeak**: your script read by the ElevenLabs voice ID you give; long scripts go in parts and are joined; the **MP3 and the SRT** are downloaded and saved next to the video. Or bring your own recording (+ SRT) | FameSpeak API key (Settings) |
| Word timing | SRT → word times (instant), or Whisper on the recording | – |
| Shot list | **Claude AI editor**: reads the method, the style's rules and a finished example, the script with paragraph times, every clip and picture description (unused first), and writes the shot list. The plan check sends problems back until it's clean. **Offline rules** if there is no key | Claude API key (Settings) |
| Plan check | every cue found, clip share on target, no short clips, no repeats from earlier videos | – |
| Assets + stills | pictures graded, cut-outs, one QA frame per scene, contact sheets in the app | – |
| Visual QA | (optional) Claude looks at the contact sheets and fixes the shot list before rendering | Claude key |
| Render, mix, final | headless Chromium + FFmpeg, quiet ducked music, −14 LUFS | – |
| Deliver | size check, re-encode only if over the limit, gofile link with md5 check | optional gofile token |
| YouTube metadata | title, A/B titles, description, chapters, tags | Claude key (or a simple version) |

Every stage is resumable: **Resume from …** on a stopped production.

## Template styles (auto-discovered)

The style picker is rebuilt from disk every time you open or refresh it:

1. **Docu Studio templates**: Calm documentary, Paper / Vox, Forensic lab, Expedition & courtroom, Breaking news. Each card plays a sample (the channel's finished videos).
2. **Your templates**: every folder in `styles/` with a `style.json` (see [styles/README.md](../styles/README.md); copy `styles/_example`).
3. **Frontier styles**: every `styles/*.json` in your Frontier folder, with its sample video (DOSSIER, KINETIC, ATLAS, DEEP, NEWS, LEGEND, HUSTLE, Documentary, Courtside, Jung, 2D Stories, AI Presenter, Modern Homes, …). A Frontier style is made by **Frontier's own engine** (its pictures, footage and keys from its `.env`), driven through Frontier's local API, with your script and your FameSpeak voice as its audio. Settings → Frontier also opens Frontier's own app and previews its look kits.

## Niches

Niches & assets lists each footage pipeline (Hasidic, Noah's Ark, …): download it once per computer, or **add a niche**
from a Google Drive link and **Catalog with AI** (Claude describes every clip and picture from contact sheets, the step
that makes picture choice accurate). The asset kit (music, fonts, maps, cut-outs, drawn props) downloads from here too.

## Keys

Settings → API keys: **FameSpeak** (famespeak.online/api-keys), **Claude** (console.anthropic.com), **gofile** (optional).
They are encrypted with the system keychain (Electron safeStorage) in the app's user-data folder, never in the
workspace or git, and passed to the engine as environment variables only while it runs.

## Run it

Requirements on the computer: **Python 3.10+** (python.org; tick "Add to PATH" on Windows) and **Node 18+** to run from
source. FFmpeg and Chromium are installed by the app (Settings → Install / repair engine).

```bash
cd studio
npm install
npm start                      # the app, using this repo as its workspace
```

First run: Settings → **Install / repair engine** → Niches & assets → **Download kit** and **Download footage** →
Create video.

## Build an installer

```bash
npm run dist:win               # Windows: NSIS installer + portable .exe in studio/dist/
npm run dist:mac               # macOS .dmg (on a Mac)
npm run dist:linux             # Linux AppImage
```

The installed app carries the engine, templates and example projects; on first start it copies them to
`Documents/DocuStudio` (the workspace, changeable in Settings), where projects, media and outputs live.

## Files

| File | |
|---|---|
| `main.js` | window, settings, encrypted keys, runs the Python backend and streams its events |
| `preload.js` | the small API the window may use |
| `src/index.html`, `src/styles.css`, `src/app.js` | the interface |
| `../docu/studio/studio.py` | the backend: `info`, `doctor`, `setup`, `kit`, `niche-*`, `voice`, `make`, `frontier-*` |
| `../docu/studio/famespeak.py` | FameSpeak / ElevenLabs voice-overs + SRT |
| `../docu/studio/claude_shotlist.py` | the Claude shot list, plan-fix loop, visual QA |
| `../docu/studio/auto_shotlist.py` | the offline shot list |
| `../docu/studio/describe.py` | AI cataloging of a new niche |
| `../docu/studio/frontier.py` | Frontier styles and engine |
| `../docu/studio/niches/*.json` | the niche registry |
