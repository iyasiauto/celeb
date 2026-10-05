# AGENTS.md: how an AI agent makes a video with this kit (v2)

You are an AI coding agent (Claude Code, Antigravity, Codex, Cursor, …) opened in this kit or in one of its niche
workspaces. Read **kit_docs/HANDOVER.md** first (what the channel has made, what each template looks like). Talk to the user
in the language they write in (often Roman Urdu / English). Keep messages short.

The kit does not trust any agent to "remember" the house style: three gates hold every video to it.

| Gate | What it stops | Where |
|---|---|---|
| **QC** (vision, Gemini 2.5 Flash Lite via OpenLux) | talking heads, influencers / face-cams, posed faces, stock watermarks, centre logos, someone else's captions, irrelevant footage. Corner logos are cropped away and the shot is re-styled | `docu/tools/qc_pool.py` → `qc.json`; `docu/qc_guard.py` refuses unchecked or rejected clips **and pictures** |
| **Edit audit** | a "slideshow" edit: missing template devices, too few graphics, long stretches of plain footage, places not mapped, numbers not shown, repeats, no chapters | `docu/tools/edit_audit.py`, runs at `plan`; **render is blocked** until every FAIL is fixed |
| **Final QC** | anything that slipped through, judged against the sentence spoken over it | `docu/tools/final_qc.py`, runs after `final` |

Never bypass them (`DOCU_SKIP_QC=1`, `DOCU_AUDIT=warn`) unless the user explicitly asks for that one video.

## 0. Where am I?

- **In a niche workspace** (the folder has `niche.json`): the niche, its default template / style, topic and footage
  pool are fixed there. Use `make.bat` / `./make.sh` (or `python <kit>/make_video.py --workspace .`). Never touch
  another workspace's footage or projects.
- **In the kit root**: if the user works on more than one niche, create a workspace per niche first:
  `python niche.py new <name> --template <id> --pool "<folder>" --topic "<what it is about>"` - then work inside it.
- Check the machine once: `python -c "import numpy, PIL, playwright" && echo ok` (else `setup.bat` / `./setup.sh`).
- QC needs `OPENLUX_API_KEY` in `api_keys/keys.env` (or FRONTIER_DIR set to the Frontier folder with its `.env`).

## 1. Ask the user everything in ONE message

1. **Title** of the video.
2. **Script** (`.txt`, or pasted → save to `inputs/<slug>/script.txt`).
3. **Voiceover**: MP3 (+ SRT if they have it), or a FameSpeak voice ID.
4. **Template / style** - only if the workspace has none, or the user wants a different one for this video.
   `python docu/registry.py list` shows them (templates/ and styles/ folders - new folders appear automatically).
5. **Footage**: the workspace pool (default), a folder, a Drive link, or online - and whether to top up online.

**Keys** go ONLY into `api_keys/keys.env` (git-ignored). Never echo, commit or copy them anywhere else.

## 2. Study the template - before writing a single line

```bash
python docu/registry.py show <template-or-style> --minutes <video length>
```

It prints the playbook: every device of the template, **how many this video needs at least**, what each is for,
its **preview image** and a **working example**. Then:

1. Open the preview sheet and the preview of every device you plan to use (you can look at images).
2. Read one worked example project **in full** (`projects/<example>/build.py`) - pacing, cues, device variety.
3. Read `docu/VISUAL_SYNC_GUIDE.md` (every sentence gets the picture that shows what it says, on its words).

Every engine device works in every template (quote, timeline, measure, checklist, headlines, baskets, chapter,
tv, spotlight, depth, card, split, collage, map, geo, stat, words …): the playbook is the minimum, not the limit.

## 3. Run the pipeline up to the shot list

```bash
python make_video.py --yes --title "<title>" --script <script.txt> --audio <vo.mp3> --srt <vo.srt> --until shotlist
   [--template <id> | --style <id>]   [--folder <path> | --drive <link> | --online "q, q"]   [--topic "<topic>"]
```

This links the footage, **runs QC** (only new files are checked), catalogs it, times the voice and writes a draft
`projects/<slug>/build.py`. Look at `media/<slug>/src/_qc/qc_report.md` and `_qc/qc_rejected.jpg`: those files are gone
from this video.

## 4. Write the shot list - you are the editor

Rewrite the shot-list part of `projects/<slug>/build.py` (keep its header with paths and `edl.setup`):

- `at("first words of the sentence", scene)`; `"@words"` inside a scene for timing on a word.
- Use the template's devices at least as often as the playbook says - collages with cut-out props and stamps
  (paper), versus/giants/delta (almanac), filter/network/gauge (forensic), scales/verdict (expedition),
  breaking/ticker/newslower (broadcast), doctitle/textcard/place (documentary) …
- Every place named → a map (coordinates: `python docu/tools/places.py find "<place>"`); every stressed number →
  a number device; every quotation → `quote`; dated passages → `timeline`; named people/objects → `depth`/`spotlight`.
- Archive / "back then" shots: `archive=True` adds the vintage TV-gate overlay.
- No clip or picture twice. Openings start on moving footage (calm templates).

## 5. Plan → audit → stills

```bash
python make_video.py --title "<title>" --yes --resume plan --until stills
```

The plan prints the **EDIT AUDIT**. Fix every `FAIL` and every `WARN` you can, run `plan` again until it passes.
Then look at the stills sheets (`media/work/<slug>/qa/` or the project's work folder): wrong pictures, cut-off text,
overlaps → fix → stills again.

## 6. Render → final QC → deliver

```bash
python make_video.py --title "<title>" --yes --resume render --upload
```

Textures, dust / light-leak / VHS overlays and the TV gate are applied automatically (per template, docu/asset_mix.py).
Final QC checks every shot against its sentence: replace flagged shots and re-render just those
(`python build.py render s012 s047` in the project folder, then `python build.py final`).

## 7. Report back

- `media/out/<Title>.mp4` (+ `_small.mp4` if it was over the limit), the gofile link + md5 if uploaded.
- The audit score and the final QC result (clean / flagged shots and what you did).
- `projects/<slug>/youtube_metadata.txt` (titles, description, chapters, tags).

## Adding templates and styles

- New template: `python docu/registry.py new-template <id> --from <template>` (or copy `templates/_example`);
  it can bring its own theme (`theme_def`) and scene code (`scene_files`) - no engine edits.
- New style: `python docu/registry.py new-style <id> --template <template>`; palette / fonts / pacing / device
  minimums / rules. Each video pins one style in `projects/<slug>/project.json`, so styles never mix.
- `python docu/registry.py check` validates everything.

## Rules

- Only the user's footage and free libraries (Pexels, Pixabay, Wikimedia). No AI-generated pictures. No talking
  heads, influencers, watermarks or logos - QC enforces it; never work around QC.
- One video = one project folder = one template (+ style) = one niche. Never reuse another project's catalog.
- If a step fails, read the log, fix it, continue with `--resume <stage>`. Don't start over.
  Stages: `footage catalog voice timing shotlist plan prep stills render mix final deliver metadata`.
- Never commit or print API keys.
