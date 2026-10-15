"""
Word timestamps for the voiceover (faster-whisper, CPU is fine: ~2 min for 14 min of speech).

    python transcribe.py path/to/vo.mp3 data/words.json [model]

model: small.en (default, good), medium.en (slower, slightly better on names).
The script text itself is aligned to these words by docu/timing.py, so transcription
mistakes in names do not matter - cues are matched on the surrounding words.
"""
import json
import sys
import time

from faster_whisper import WhisperModel

src, out = sys.argv[1], sys.argv[2]
model = sys.argv[3] if len(sys.argv) > 3 else "small.en"
t = time.time()
m = WhisperModel(model, device="cpu", compute_type="int8", cpu_threads=4)
segs, info = m.transcribe(src, word_timestamps=True, beam_size=1, vad_filter=False)
words = []
for s in segs:
    for w in s.words:
        words.append({"w": w.word.strip(), "s": round(w.start, 3), "e": round(w.end, 3)})
    print(f"{s.end:.1f}s", flush=True)
json.dump(words, open(out, "w"))
print("done:", len(words), "words in", round(time.time() - t), "s")
