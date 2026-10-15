"""
auto_shotlist.py - an offline shot list (no AI key needed), built by rules:

  * timing    every sentence's start is found in the voiceover (same alignment as hand-made videos);
              short sentences merge into the previous beat
  * structure cold open, a title card, then chapter headings at paragraph starts every ~1.5-3 min
  * choice    each beat's words are matched against the catalog descriptions and tags (IDF-weighted);
              clips go to the best-matching beats until the clip share is reached; numbers become a big
              counter, short emphatic lines and questions become text cards; nothing repeats
  * pacing    long beats are split across two visuals

It is a quick draft. The Claude shot list (claude_shotlist.py) follows docu/VISUAL_SYNC_GUIDE.md
properly: maps, lists, boards, recurring devices, the right picture for each claim.
"""

import json
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from timing import Timing, _norm          # noqa: E402

STOP = set("""a an the and or but if then than that this these those there their they them it its is are was were be been being
to of in on at by for with from as into onto about over under after before between through during without within
he she his her we our you your i me my mine not no nor so such very can could would should will shall may might must
do does did done have has had having just also only even still yet more most much many any some each every other
what which who whom whose when where why how all both few one two three four five six seven eight nine ten
here now out up down off again further once same own too s t don isn aren wasn weren doesn didn hasn haven""".split())
NUM = re.compile(r"(\$?\d[\d,\.]*\s?(?:%|percent|million|billion|thousand)?)", re.I)


def _words(text):
    return [w for w in (re.sub(r"[^a-z0-9]", "", x.lower()) for x in text.split()) if len(w) > 2 and w not in STOP]


def _stem(w):
    for suf in ("ings", "ing", "ies", "es", "s", "ed"):
        if w.endswith(suf) and len(w) - len(suf) >= 4:
            return w[: -len(suf)]
    return w


def _sentences(par):
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+(?=[\"“‘'A-Z0-9])", par) if s.strip()]


def _cue(sentence, n=7):
    ws = sentence.split()
    return " ".join(ws[:n]).rstrip(",;:—-")


def _title(sentence, n=6):
    ws = [w.strip(",.;:!?\"“”'") for w in sentence.split()[:n]]
    while ws and ws[-1].lower() in STOP:
        ws.pop()
    return " ".join(w[:1].upper() + w[1:] for w in ws) or "Next"


def _wrap(line, fn):
    """at(<json cue>, EXPR) -> at(<json cue>, fn(EXPR))"""
    m = re.match(r'^at\(("(?:[^"\\]|\\.)*"), (.*)\)$', line)
    return f"at({m.group(1)}, {fn}({m.group(2)}))" if m else line


class Index:
    def __init__(self, items, text_of):
        self.items = items
        self.toks = [set(_stem(w) for w in _words(text_of(it))) for it in items]
        df = {}
        for t in self.toks:
            for w in t:
                df[w] = df.get(w, 0) + 1
        n = max(1, len(items))
        self.idf = {w: math.log(1 + n / c) for w, c in df.items()}

    def rank(self, words, exclude=()):
        ws = set(_stem(w) for w in words)
        scored = []
        for k, (it, t) in enumerate(zip(self.items, self.toks)):
            if k in exclude:
                continue
            s = sum(self.idf.get(w, 0) for w in ws & t)
            if it.get("used"):
                s -= 100.0                   # material earlier videos used goes last
            scored.append((s, k))
        scored.sort(key=lambda x: -x[0])
        return scored


def build(script_path, words_path, clips, images, title, clip_share=30, style="documentary"):
    """-> body text for build.py (at(...) lines + ACTS)"""
    T = Timing.load(script_path, words_path)
    text = open(script_path, encoding="utf-8-sig").read()
    paras = [p.strip() for p in text.split("\n") if p.strip()]
    beats, cursor = [], 0
    for pi, par in enumerate(paras):
        for si, s in enumerate(_sentences(par)):
            cue = _cue(s)
            try:
                T.cursor = cursor
                i = T.find(cue)
            except KeyError:
                continue
            cursor = i
            beats.append(dict(text=s, cue=cue, t=T.start[i], par=pi, first=(si == 0)))
    if not beats:
        raise RuntimeError("no sentence of the script was found in the voiceover")
    end = T.end[-1] + 1.0
    for k, b in enumerate(beats):
        b["dur"] = (beats[k + 1]["t"] if k + 1 < len(beats) else end) - b["t"]
    merged = []
    for b in beats:                          # short sentences ride along with the previous beat
        if merged and merged[-1]["dur"] < 3.2 and not b["first"]:
            merged[-1]["dur"] += b["dur"]
            merged[-1]["text"] += " " + b["text"]
        else:
            merged.append(dict(b))
    beats = merged
    total = end

    # chapters at paragraph starts
    chap_len = min(180.0, max(90.0, total / 8))
    title_at, chapters, last = None, [], 0.0
    for k, b in enumerate(beats):
        if not b["first"] or k == 0:
            continue
        if title_at is None:
            if b["t"] >= min(45.0, total * 0.1):
                title_at, last = k, b["t"]
            continue
        if b["t"] - last >= chap_len and total - b["t"] > 60:
            chapters.append(k)
            last = b["t"]

    ci = Index(clips, lambda c: c["desc"] + " " + " ".join(c["tags"]))
    ii = Index(images, lambda r: r["desc"] + " " + " ".join(r["tags"]))
    used_c, used_i, recent = set(), set(), []
    clip_secs, lines, acts = 0.0, [], [None]
    target = clip_share / 100.0

    def pick_image(words):
        for s, k in ii.rank(words, exclude=used_i):
            if images[k]["key"] not in recent:
                used_i.add(k)
                recent.append(images[k]["key"])
                del recent[:-12]
                return images[k]["key"]
        used_i.clear()                         # ran out: allow repeats again (oldest first)
        k = ii.rank(words)[0][1]
        return images[k]["key"]

    def pick_clips(words, need):
        ranked = [(s, k) for s, k in ci.rank(words, exclude=used_c)]
        if not ranked:
            return None, 0
        s0, k0 = ranked[0]
        got, chosen = clips[k0]["dur"], [k0]
        tags0 = set(clips[k0]["tags"][:1])
        for s, k in ranked[1:]:
            if got >= need * 0.9 or len(chosen) >= 4:
                break
            if not tags0 or tags0 & set(clips[k]["tags"]):
                chosen.append(k)
                got += clips[k]["dur"]
        for k in chosen:
            used_c.add(k)
        return chosen, s0

    q = json.dumps
    n_chap = 0
    for k, b in enumerate(beats):
        words = _words(b["text"])
        cue = q(b["cue"])
        elapsed = b["t"] + b["dur"]
        if k == title_at:
            lines.append(f'at({cue}, title_card("A documentary", {q(title)}, {q(pick_image(words))}))')
            continue
        if k in chapters:
            n_chap += 1
            acts.append(b["cue"])
            lines.append(f'at({cue}, heading({n_chap}, {q(_title(b["text"]))}, {q(pick_image(words))}))')
            continue
        nums = [m for m in NUM.finditer(b["text"]) if re.search(r"\d", m.group(1))]
        nums.sort(key=lambda m: not re.search(r"%|percent|\$|million|billion|thousand", m.group(1), re.I))
        num = nums[0] if nums else None
        short = len(b["text"].split()) <= 9
        want_clip = clips and (clip_secs / max(1.0, elapsed) < target) and not num
        strong = num and re.search(r"%|percent|\$|million|billion", num.group(1), re.I)
        if num and (strong or k % 2 == 0):
            val = re.sub(r"\s*percent", " %", num.group(1).strip(), flags=re.I).replace("%", " %").replace("  ", " ")
            kick = " ".join(w.upper() for w in words if not re.search(r"\d|percent", w))[:40].strip() or "THE NUMBER"
            lines.append(f'at({cue}, big({q(val)}, {q(kick)}, "", bg={q(pick_image(words))}, count=False))')
        elif (b["text"].endswith("?") or (short and k % 3 == 0)) and not want_clip:
            ln = b["text"].strip()
            lines.append(f'at({cue}, card(({q(ln)}, 0.2, ACC, 72), bg={q(pick_image(words))}))')
        elif want_clip:
            chosen, score = pick_clips(words, b["dur"])
            if chosen:
                clip_secs += b["dur"]
                more = f", then={tuple(clips[c]['i'] for c in chosen[1:])}" if len(chosen) > 1 else ""
                lines.append(f'at({cue}, cl({clips[chosen[0]]["i"]}{more}))')
            else:
                lines.append(f'at({cue}, ph({q(pick_image(words))}))')
        else:
            lines.append(f'at({cue}, ph({q(pick_image(words))}))')
        if b["dur"] > 11 and not lines[-1].startswith(f"at({cue}, heading"):
            # a long beat gets a second visual half way, on a word in the middle of the sentence
            ws = b["text"].split()
            mid = " ".join(ws[len(ws) // 2: len(ws) // 2 + 5]).rstrip(",;:—-")
            if len(mid.split()) >= 4:
                lines.append(f'at({q(mid)}, ph({q(pick_image(_words(mid) + words))}))')
    # soft start and end
    if lines:
        lines[0] = _wrap(lines[0], "fadein")
        lines[-1] = _wrap(lines[-1], "fadeout")
    body = ["# written by auto_shotlist.py (offline rules) - edit freely", ""]
    body += lines
    body.append("")
    body.append(f"ACTS = {json.dumps(acts)}".replace("null", "None"))
    return "\n".join(body) + "\n"
