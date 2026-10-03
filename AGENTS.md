# AGENTS.md: how an AI agent makes a video with this kit

You are an AI coding agent (Claude Code, Antigravity, Codex, Cursor, …) opened in this folder.
Read **kit_docs/HANDOVER.md** first - it says what this channel has already made, what each template looks
like now, and where the finished shot lists are to copy the house style from. The user wants a
faceless documentary video made with one of the six templates. Follow this file step by step. Talk to the user
in the language they write in (often Roman Urdu / English). Keep messages short.

## 0. Check the machine (once per session)

```bash
python --version            # 3.10+ ; on Mac/Linux it may be python3
python -c "import numpy, PIL, playwright" && echo ok
```

If the check fails, run `kit_docs/setup.bat` (Windows) or `kit_docs/setup.sh` (Mac/Linux). In a sandbox without a GUI, run
`python -m pip install -r docu/requirements.txt static-ffmpeg gdown` and then
`python -m playwright install chromium`. If `media/kit/fonts` is missing, the asset kit downloads by itself on
the first run (from Google Drive).

## 1. Ask the user everything in ONE message

Ask these together, with a short example for each. Don't ask them one by one.

1. **Title** of the video.
2. **Script**: attach the `.txt`, or paste the text. If they paste it, save it to `inputs/<slug>/script.txt`.
3. **Voiceover**: attach the MP3, plus the SRT if they have one (more exact, and faster). The other option is
   a **FameSpeak voice ID**, which needs `FAMESPEAK_API_KEY`.
4. **Template**, 1–6:
   1. Calm documentary
   2. Heritage almanac (engraved caps, didone figures, ledger slips, plat map)
   3. Paper / Vox explainer
   4. Forensic lab report
   5. Expedition & courtroom
   6. Breaking-news broadcast

   One line on each is in `kit_docs/TEMPLATES.md`. If they don't care, suggest one that suits the topic.
5. **Footage**:
   - (1) a folder on this computer: only if you run on the user's PC, as Antigravity or local Claude Code do
   - (2) a Google Drive folder link, shared as "anyone with the link"
   - (3) an existing niche: `hasidic` or `noah`
   - (4) nothing yet, fetch it online

   For (1)–(3), also ask: **also fetch extra footage online?** That uses Pexels and Pixabay (keys needed),
   Wikimedia (free), and optionally Google Images (licence unknown).
6. *(Optional)* clip share %, upload to gofile (yes/no), and any API keys they want to use.

Where uploaded files land depends on the agent. Find them, for example with `find / -name "*.mp3" -mmin -60`
in a cloud sandbox. Then copy them into `inputs/<slug>/`.

**Keys:** if the user gives keys, write them ONLY to `api_keys/keys.env` (it is git-ignored). Never echo them,
never commit them, never put them in any other file. The names are in `api_keys/keys.example.env`.

## 2. Map the answers to one command

```bash
python make_video.py --yes --title "<title>" --script inputs/<slug>/script.txt \
  --audio inputs/<slug>/vo.mp3 [--srt inputs/<slug>/vo.srt]  |  --famespeak-voice <id>
  --template documentary|almanac|paper|forensic|expedition|broadcast
  --folder "<path>"  |  --drive "<link>"  |  --niche hasidic   [--online "query, query" | --online auto]
  [--sources pexels,pixabay,wikimedia[,google]] [--clip-share 40] [--upload]
```

Template numbers map to ids: 1 `documentary`, 2 `almanac`, 3 `paper`, 4 `forensic`, 5 `expedition`,
6 `broadcast`. Use `--online auto` to pick the searches from the script. Better: write 8–15 searches yourself
from the script, naming concrete visible things (`"amish buggy", "lancaster farmland aerial", "barn raising"`).

A full video takes 30–90 minutes to render. Run it in the background, write to a log, and poll the log.
Don't block on it.

```bash
python make_video.py ... > media/run.log 2>&1 &      # then: tail -n 30 media/run.log
```

## 3. Choose the editor: quick or best

**Quick** (good enough when an AI key is set): if `api_keys/keys.env` has an AI provider (OpenRouter, OpenLux,
Claude API, a custom endpoint) or the Claude Code CLI is installed, `make_video.py` writes the shot list with
it. Without any of them, it uses offline rules, which match words to file and folder names. Just run step 2.

**Best: you are the editor.** This is the way the channel's videos were made. You write the shot list yourself:

1. Run step 2 with **`--until shotlist`**. It gathers the footage, catalogs it, times the voiceover, and writes a
   draft `projects/<slug>/build.py`.
2. Read:
   - `docu/VISUAL_SYNC_GUIDE.md`: the method. Every sentence gets the picture that shows what is said, when
     it is said.
   - The template's section in `kit_docs/TEMPLATES.md`, its starter `docu/templates/starter_<template>/build.py`
     (`starter/` for paper, forensic and expedition), and a finished example in `projects/` that uses the same
     template.
   - The material in `projects/<slug>/data/`:
     - `script.txt`
     - `words.json` (word times)
     - `catalog_all.json` (clips: index, file, tags, description)
     - `image_picks.json` / `notes_img.txt` (pictures with descriptions)
     - the contact sheets in `media/<slug>/cat/`. Look at them; you can see images.
3. Rewrite the shot-list part of `projects/<slug>/build.py`. Keep its header, which holds the paths and
   `edl.setup`. Use `at("first words of the sentence", scene)`, the template's own scenes (chapter headings,
   cards, big numbers, maps), `"@words"` for timing inside a scene, and no clip or picture twice in a row.
   Openings start on moving footage.
4. `python make_video.py --title "<title>" --yes --resume plan --until stills`. This checks the plan (fix every
   `WARN`) and renders one still per scene. Look at the contact sheets in `media/work/<slug>/qa/` and fix wrong
   pictures, cut-off text and overlaps.
5. `python make_video.py --title "<title>" --yes --resume render` (add `--upload` for a gofile link).

## 3b. Keep the footage for next time

One subject, one pool: `python docu/tools/pool.py merge <pool> <new_dir>` moves freshly fetched files in,
`build <pool> --name "<Name>"` (re)writes library.json / tags.json / CREDITS.md, `sheets` draws contact
sheets and `catalog` writes a project's clip catalog. Register it once with `studio.py niche-add` and
later videos only need `--niche <id>`. See kit_docs/HANDOVER.md §6.

## 4. Report back

- The final file: `media/out/<Title>.mp4`. If it was over 1 GB, there is also an `_small.mp4`.
- The SRT, `projects/<slug>/youtube_metadata.txt` (title options, description, chapters, tags), and the gofile
  link with its md5, if uploaded.
- One line on what footage was used: own, Drive, or online with its sources. For online footage, the licences
  are in `media/<slug>/src/sources.json`.

## Rules

- Use only the user's footage plus the free libraries above. No AI-generated pictures. No talking heads,
  watermarks or logos: delete such files from `media/<slug>/src/` and run `--resume catalog`.
- Keep the music quiet under the voice; the defaults already do this.
- If a step fails, read the error in the log, fix it, and continue with `--resume <stage>`. Don't start over.
  The stages are `footage catalog voice timing shotlist plan prep stills render mix final deliver metadata`.
- Never commit or print API keys. Never upload the user's private files anywhere except gofile when they asked
  for `--upload`.
