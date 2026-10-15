# Claude: read HANDOVER.md, then AGENTS.md

This folder is a video-making kit for **any niche** (v2). **HANDOVER.md** says what the channel has made, what each
template looks like, and the rules. Read it first, then **AGENTS.md** and follow it exactly when the user wants a
video ("video banao", "start", "make a video"): ask the questions in one message, run `registry.py show <template>`
and study the previews + one worked example, then be the editor (`--until shotlist`, write the shot list,
`--resume plan`). Three gates hold every video: QC (talking heads / influencers / logos / watermarks out),
the edit audit (render blocked until the template is used in full), final QC. Never bypass them.
More than one niche? Each lives in its own workspace (`python niche.py new ...`) - work inside it, never mix.
The skill `/make-video` does the same.
Never commit or print API keys (api_keys/keys.env is git-ignored).
