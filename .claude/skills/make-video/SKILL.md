---
name: make-video
description: Make a faceless documentary video with this kit's six templates. Use when the user asks to make or start a video, gives a script/voiceover, or picks a template (documentary, almanac, paper, forensic, expedition, broadcast).
---

Follow AGENTS.md in the kit root, in order:

1. Check Python and the packages (step 0). Run setup if needed.
2. Ask the user in ONE message for:
   - title
   - script
   - voiceover (MP3 + SRT, or a FameSpeak voice ID)
   - template 1–6
   - footage: PC folder, Drive link, existing niche, or online; and whether to also fetch online
   - optional: clip %, gofile upload, keys
3. Save the inputs to `inputs/<slug>/`. Keys go only into `api_keys/keys.env`.
4. Be the editor:
   - `python make_video.py --yes ... --until shotlist`
   - read the guide, the template starter, an example project and the catalog
   - write `projects/<slug>/build.py`
   - `--resume plan --until stills`, then check the contact sheets and fix problems
   - `--resume render [--upload]`
   Run long steps in the background and poll the log.
5. Report back: the video path, the SRT, the metadata file, the gofile link and md5, and the footage sources.
