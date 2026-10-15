Put three files here:

script.txt         The narration exactly as recorded, one paragraph per line (blank lines are fine).
                   Cues in build.py are phrases copied from this file.

words.json         Word timestamps of the voiceover:  python ../transcribe.py <work>/vo.mp3 words.json
                   Format: [{"w": "There's", "s": 0.12, "e": 0.40}, ...]

catalog_all.json   Your clip catalog - one entry per usable shot in footage/source_video/:
                   [{"i": 0, "video": "abc.mp4", "s": 17.5, "e": 20.2,
                     "desc": "Team hiking along the ridge", "tags": ["ground"], "flags": [], "quality": 4}, ...]
                   clip(i) in build.py refers to entry i. "s"/"e" are seconds inside the video.
                   flags: "text" / "logo" / "graphic" / "presenter" mark shots to avoid.
                   An empty list [] is fine for a video made only of pictures.
