"""
srt2words.py - word timestamps from an SRT subtitle file (no transcription needed).

    python srt2words.py voiceover.srt data/words.json

Each subtitle cue's time span is shared out across its words in proportion to their length
(with a little weight per word for the gap between words). Cues from a TTS / editor export are
short (1-5 s), so every word lands within a few hundredths of a second - plenty for cutting on
words. docu/timing.py then aligns the script to these words, exactly as with transcribe.py.
"""
import json
import re
import sys


def parse_srt(text):
    blocks = re.split(r"\n\s*\n", text.strip().replace("\r", ""))
    cues = []
    for b in blocks:
        lines = [l for l in b.split("\n") if l.strip()]
        tl = next((i for i, l in enumerate(lines) if "-->" in l), None)
        if tl is None:
            continue
        a, b2 = [x.strip() for x in lines[tl].split("-->")]
        cues.append((ts(a), ts(b2.split()[0]), " ".join(lines[tl + 1:])))
    return cues


def ts(s):
    h, m, rest = s.replace(",", ".").split(":")
    return int(h) * 3600 + int(m) * 60 + float(rest)


def words_from_cues(cues):
    out = []
    for s, e, text in cues:
        ws = text.split()
        if not ws:
            continue
        weights = [len(w) + 2 for w in ws]
        tot = sum(weights)
        t = s
        for w, k in zip(ws, weights):
            d = (e - s) * k / tot
            out.append({"w": w, "s": round(t, 3), "e": round(t + d * 0.92, 3)})
            t += d
    return out


if __name__ == "__main__":
    src, dst = sys.argv[1], sys.argv[2]
    words = words_from_cues(parse_srt(open(src, encoding="utf-8-sig").read()))
    json.dump(words, open(dst, "w"))
    print(len(words), "words ->", dst)
