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
| Voiceover | **FameSpeak**: your script read by the ElevenLabs voice ID you give (pre-filled from `FAMESPEAK_VOICE_ID` in your Frontier `.env`); long scripts go in parts and are joined; the **MP3 and the SRT** are downloaded and saved next to the video. Or bring your own recording (+ SRT), or, for a Frontier style, let **Frontier make the voice** with its own `.env` | FameSpeak key (Settings, or your Frontier `.env`) |
| Word timing | SRT → word times (instant), or Whisper on the recording | – |
| Shot list | **AI editor**: reads the method, the style's rules and a finished example, the script with paragraph times, every clip and picture description (unused first), and writes the shot list. The plan check sends problems back until it's clean. **Offline rules** if no AI is set up | any AI editor (Settings → AI), optional |
| Plan check | every cue found, clip share on target, no short clips, no repeats from earlier videos | – |
| Assets + stills | pictures graded, cut-outs, one QA frame per scene, contact sheets in the app | – |
| Visual QA | (optional) the **AI vision** provider (e.g. OpenLux · gemini-2.5-flash-lite) looks at the contact sheets and lists problems per scene; the AI editor fixes them before rendering | an AI vision provider |
| Render, mix, final | headless Chromium + FFmpeg, quiet ducked music, −14 LUFS | – |
| Deliver | size check, re-encode only if over the limit, gofile link with md5 check | optional gofile token |
| YouTube metadata | title, A/B titles, description, chapters, tags | the AI editor (or a simple version) |

Every stage is resumable: **Resume from …** on a stopped production.

## AI (optional; Claude is not required)

Settings → **AI** picks who does the editing and who looks at pictures. Each can be **Auto** (the first one set up),
a provider, or **Off**:

| Provider | What it is | Set up with |
|---|---|---|
| Claude Code CLI | `claude -p` on this PC, on your own plan | Claude Code installed and logged in; no key |
| OpenRouter | e.g. `deepseek/deepseek-chat` (what Frontier uses for scripts) | `OPENROUTER_API_KEY` (or `OPENROUTER_KEY`) |
| OpenLux | e.g. `gemini-2.5-flash-lite`; sees pictures, so a good **vision** choice | `OPENLUX_API_KEY` (+ `OPENLUX_BASE_URL`, `OPENLUX_MODEL`) |
| Antigravity | your Antigravity / Gemini Pro account through your local model router (cli-proxy-api), an OpenAI-compatible URL on this PC | Settings → Antigravity router URL (default `http://127.0.0.1:8317/v1`), key only if the router asks |
| Custom endpoint | any OpenAI-compatible server (LM Studio, Ollama, a proxy) | Settings → Custom URL (+ key) |
| Claude API | Anthropic API | `ANTHROPIC_API_KEY` |

Model fields are optional (each provider has a default, or the `*_MODEL` from your Frontier `.env`).

## Template styles (auto-discovered)

The style picker is rebuilt from disk every time you open or refresh it:

1. **Docu Studio templates**: Calm documentary, Paper / Vox, Forensic lab, Expedition & courtroom, Breaking news. Each card plays a sample (the channel's finished videos).
2. **Your templates**: every folder in `styles/` with a `style.json` (see [styles/README.md](../styles/README.md); copy `styles/_example`).
3. **Frontier styles**: every `styles/*.json` in **your own Frontier folder on this PC** (Settings → Frontier folder), with its sample video (DOSSIER, KINETIC, ATLAS, DEEP, NEWS, LEGEND, HUSTLE, Documentary, Courtside, Jung, 2D Stories, AI Presenter, Modern Homes, …), including any style you add there later. A Frontier style is made by **Frontier's own engine** with your setup exactly as it is (its `.env`: FameSpeak, OpenRouter, OpenLux, stock cascade, rembg, agy …), driven through Frontier's local API, with your script and your voice (FameSpeak, a recording, or Frontier's own). Settings → Frontier also opens Frontier's own app and previews its look kits.

## Niches

Niches & assets lists each footage pipeline (Hasidic, Noah's Ark, …).

* **Add a niche from a folder on this PC**: choose the folder (videos and pictures; sub-folders such as `clips/` and
  `images/` are found) and, optionally, your own **tags file** (e.g. the `ASSET_TAGS_JSON` Frontier uses:
  `{"file.jpg": ["tag", …]}`, `{"file.jpg": "description"}`, `{"file.jpg": {"tags": […], "desc": "…"}}` or a list of
  `{"file", "tags", "desc"}`). Nothing is copied: the clips folder is linked (symlink, or a Windows junction).
* **Use a folder on this PC** on an existing niche: point Hasidic at e.g. `D:\New Hasidic\assets` instead of
  downloading it again; the catalogued picture picks are re-linked from there.
* A Drive link still works (Download footage).
* **Catalog**: contact sheets of every clip and picture, described by your AI vision provider (the step that makes
  picture choice accurate), merged with your tags file. Without AI, your tags file and the file names are used.
* **Asset kit** (music, fonts, maps, cut-outs, textures, drawn props): **Use Frontier's assets** (your Frontier
  folder's `assets/`, linked, not copied), **Choose kit folder…**, or download.

## Keys

A key is looked up in this order: Settings → API keys (encrypted with the system keychain through Electron
safeStorage, in the app's user-data folder) → `api_keys/keys.env` → **your Frontier folder's `.env`**. So the keys
Frontier already uses on this PC work here without being typed again; Settings shows "found in your Frontier .env"
for them (never the value). Keys are never written into the workspace or git; the engine reads them only while it
runs. Keys: FameSpeak, OpenRouter, OpenLux, Antigravity router (if it asks), custom endpoint, Claude API (optional),
gofile (optional).

## Run it

Requirements on the computer: **Python 3.10+** (python.org; tick "Add to PATH" on Windows) and **Node 18+** to run from
source. FFmpeg and Chromium are installed by the app (Settings → Install / repair engine).

```bash
cd studio
npm install
npm start                      # the app, using this repo as its workspace
```

First run: Settings → **Install / repair engine** → Settings → **Frontier folder** (your own) and **AI** → Niches &
assets → **Use Frontier's assets** for the kit and **Use a folder on this PC** for each niche → Create video.

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
| `../docu/studio/ai.py` | the AI providers (Claude Code, OpenRouter, OpenLux, Antigravity, custom, Claude API) |
| `../docu/studio/claude_shotlist.py` | the AI shot list prompt and the plan-fix conversation |
| `../docu/studio/auto_shotlist.py` | the offline shot list |
| `../docu/studio/describe.py` | AI cataloging of a new niche |
| `../docu/studio/frontier.py` | Frontier styles and engine |
| `../docu/tools/keys.py` | key lookup: app → `api_keys/keys.env` → Frontier `.env` |
| `../docu/studio/niches/*.json` | the niche registry |
