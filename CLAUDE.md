# Claude: read HANDOVER.md, then AGENTS.md

This folder is a video-making kit. **kit_docs/HANDOVER.md** is the handover note: what the channel has
already made, what each template looks like now, and the rules. Read it first, then AGENTS.md. When the user wants a video (or says "video banao", "start", "make a video"),
follow **AGENTS.md** exactly: ask the 5 questions in one message, then run `make_video.py`, preferably as the
editor yourself (`--until shotlist`, write the shot list, `--resume plan`). The skill `/make-video` does the same.
Docs: kit_docs/HANDOVER.md (handover), kit_docs/START_HERE.md (user guide), kit_docs/TEMPLATES.md, kit_docs/DATA_SOURCES.md, docu/VISUAL_SYNC_GUIDE.md.
Never commit or print API keys (api_keys/keys.env is git-ignored).
