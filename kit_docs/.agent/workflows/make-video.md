---
description: Make a faceless documentary video for any niche with this kit (v2)
---

Follow AGENTS.md (kit_docs/AGENTS.md in the repo) in order:

1. Where am I? In a niche workspace (`niche.json`) use its template, topic and pool via `make.bat` / `./make.sh`.
   In the kit root with several niches: `python niche.py new <name> --template <id> --pool <folder> --topic <topic>`
   first, then work inside that workspace. Never mix niches or templates in one project.
2. Ask the user in ONE message: title, script, voiceover (MP3 + SRT, or a FameSpeak voice ID), template/style
   (`python docu/registry.py list`) only if the workspace has none, footage (pool / folder / Drive / online).
   Keys go only into `api_keys/keys.env` - never print them. QC needs OPENLUX_API_KEY.
3. `python docu/registry.py show <template-or-style> --minutes <length>`: look at the preview sheet and the
   preview of every device you will use, read one worked example build.py IN FULL, read docu/VISUAL_SYNC_GUIDE.md.
4. Be the editor:
   - `--until shotlist` (links footage, runs QC, catalogs, times the voice)
   - write `projects/<slug>/build.py`: the template's devices at least as often as the playbook says, a map for
     every place (`docu/tools/places.py find`), a number device for every stressed number, `quote` for quotes,
     `archive=True` for archive shots, no repeats
   - `--resume plan --until stills`: fix every EDIT AUDIT FAIL (render is blocked until they are gone), check stills
   - `--resume render [--upload]`, then read final_qc.md and replace flagged shots
   Run long steps in the background and poll the log.
5. Report back: video path, audit score, final QC result, metadata file, gofile link + md5.
