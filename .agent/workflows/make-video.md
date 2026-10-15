---
description: Make a faceless documentary video with the kit (ask for script, voice, template, footage; then build it)
---

1. Read AGENTS.md in the workspace root and follow it.
2. Check Python and the packages. If they are missing, run setup.bat (Windows) or ./setup.sh.
3. Ask the user in one message for:
   - title
   - script file
   - voiceover MP3 (+ SRT), or a FameSpeak voice ID
   - template 1–6
   - footage: a folder on this PC, a Google Drive link, an existing niche, or online (Pexels / Pixabay /
     Wikimedia / Google); and whether to also fetch online
   - optional: clip %, gofile upload
4. Run `python make_video.py --yes ... --until shotlist` in the background.
5. As the editor, rewrite `projects/<slug>/build.py`. Follow docu/VISUAL_SYNC_GUIDE.md and the template's
   starter in docu/templates/.
6. Run `python make_video.py --title "<title>" --yes --resume plan --until stills`. Look at the stills in
   media/work/<slug>/qa/ and fix problems.
7. Run `python make_video.py --title "<title>" --yes --resume render --upload`.
8. Report back: the video path, the gofile link and md5, the metadata file, and the footage sources.
