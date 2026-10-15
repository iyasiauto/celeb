"""
Narration timing: find when a phrase of the script is spoken.

Word timestamps come from a speech-to-text pass over the finished voiceover
(faster-whisper, word_timestamps=True). The script is aligned to them word by word,
so a cue can be written as the words themselves - `T.at("Irish archbishop")` -
instead of as a number that breaks whenever the voiceover is re-recorded.
"""

import re
import json
import difflib


def _norm(w):
    return re.sub(r"[^a-z0-9]", "", w.lower().replace("ı", "i").replace("ğ", "g").replace("ü", "u")
                  .replace("ş", "s").replace("ö", "o").replace("ç", "c").replace("İ".lower(), "i"))


class Timing:
    def __init__(self, script_text, words):
        self.tokens = [t for t in (_norm(w) for w in script_text.split()) if t]
        heard = [_norm(w["w"]) for w in words]
        sm = difflib.SequenceMatcher(None, self.tokens, heard, autojunk=False)
        start = [None] * len(self.tokens)
        end = [None] * len(self.tokens)
        for a, b, n in sm.get_matching_blocks():
            for k in range(n):
                start[a + k] = words[b + k]["s"]
                end[a + k] = words[b + k]["e"]
        # unmatched words take a share of the gap between their matched neighbours
        known = [i for i, s in enumerate(start) if s is not None]
        for i in range(len(start)):
            if start[i] is None:
                lo = max([k for k in known if k < i], default=None)
                hi = min([k for k in known if k > i], default=None)
                if lo is None:
                    start[i] = end[i] = 0.0
                elif hi is None:
                    start[i] = end[i] = end[lo]
                else:
                    f = (i - lo) / (hi - lo)
                    start[i] = end[lo] + (start[hi] - end[lo]) * f
                    end[i] = start[i]
        self.start, self.end = start, end
        self.cursor = 0
        self.matched = len(known) / max(1, len(self.tokens))

    @classmethod
    def load(cls, script_path, words_path):
        with open(script_path, encoding="utf-8-sig") as f:
            text = f.read()
        with open(words_path) as f:
            words = json.load(f)
        return cls(text, words)

    def find(self, phrase, after=None):
        """Index of the first token of `phrase` at or after the cursor."""
        want = [t for t in (_norm(w) for w in phrase.split()) if t]
        i0 = self.cursor if after is None else after
        for i in range(i0, len(self.tokens) - len(want) + 1):
            if self.tokens[i:i + len(want)] == want:
                return i
        raise KeyError(f"phrase not found after token {i0}: {phrase!r}")

    def at(self, phrase, offset=0.0, advance=True):
        """Start time (s) of `phrase`, searching forward from the last cue."""
        i = self.find(phrase)
        if advance:
            self.cursor = i
        return round(self.start[i] + offset, 3)

    def end_of(self, phrase):
        i = self.find(phrase)
        n = len([t for t in (_norm(w) for w in phrase.split()) if t])
        return round(self.end[i + n - 1], 3)
