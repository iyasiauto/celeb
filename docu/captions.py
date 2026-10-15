#!/usr/bin/env python3
"""captions.py — Frontier's burned-in captions in the Docu kit.

Ported from Frontier's make_video.py (_build_burn_ass, _build_burn_ass_kit and their helpers) so a template imported
from Frontier keeps its caption look. Every mode draws exactly as it did there:

    (no mode)  the plain caption: ONE line per cue, a soft fade, bottom centre (or mid-frame with "center"); options
               font, size, upper, outline, shadow, box (a filled band), outline_colour, line_chars, margin_v, and
               karaoke (the word being said sweeps to the accent colour; on unless "karaoke": false)
    cluster    the words of a phrase gather one by one in a block on the LEFT, the next phrase on the RIGHT
    typewriter a black bar top-left appears at its full width, then the line types into it
    shout      two or three words at a time, caps, a heavy face with a red stroke, at the bottom, popping in
    pop        a few words centred with a soft glow, the key word in the accent colour
    comic      one bold outlined line at the bottom that pops in
    pill       4-6 words in a dark rounded pill at the bottom; said words white, the word being said in the accent
    stack      kinetic typography: 3-6 words build word by word beside the picture (left, then right)

What differs from Frontier is only the input side. Frontier read an SRT and a whisper word clock from the job folder;
Docu has the voice's words already timed (data/words.json: [{"w", "s", "e"}]), so the cues are built here from the
words (one-line cues, broken at sentence ends and pauses) and every cue carries its own word clock. Captions are
muted while a full-frame graphic scene is on screen (any scene type outside FOOTAGE_TYPES). Frontier's kinetic intro
(KIN_UNTIL, off by default there too) and its overlay text labels have no Docu equivalent and are left out.

Fonts come from media/kit/fonts. A caption's font name is resolved against the names inside those files (family,
full name, PostScript name, file name), so "Poppins ExtraBold" or "KodeMono" reach the face libass will match.

    from docu import captions
    ass = captions.build_ass(words, scenes, cap, "out.ass", accent=None)
    captions.burn("in.mp4", ass, "out.mp4", fonts_dir)

    python docu/captions.py <words.json> <scenes.json> <style.json|template.json> <video_in> <video_out>
"""

import json
import math
import re
import struct
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
FONTS = HERE.parent / "media" / "kit" / "fonts"


def configure(kit_dir) -> None:
    """point the module at a kit folder (media/kit of the workspace being rendered)"""
    global FONTS
    FONTS = Path(kit_dir) / "fonts"
    _FONT_INDEX.clear()


# ── Frontier's caption constants (its defaults, without the environment overrides) ─────────────────────────────────
SUB_FONT = "Inter ExtraBold"
SUB_FONT_SERIF = "Inter ExtraBold"
CAPTION_ACCENT = "&H3CB9F5&"         # ASS BGR: a warm gold — the word being spoken in a karaoke caption
SUB_SIZE_PX = 73                     # real pixels at 1080p
SUB_SIZE_CENTER_PX = 68
SUB_LINE_CHARS = 44                  # one line, max this many chars
SUB_FADE_MS = 170                    # soft appear/disappear
SUB_SHADOW = 3.4

# scene types that show footage or a photo: captions draw over them; every other type is a full-frame graphic
FOOTAGE_TYPES = {"clip", "photo", "depth", "spotlight", "tv", "card", "ddphoto", "ddspot"}
KIT_MODES = ("cluster", "typewriter", "shout", "pop", "comic", "pill", "stack")
# cues for the modes that cut a cue into word groups (stack, pop, shout, pill, cluster): a cue is a spoken phrase,
# as long as a subtitle cue was in Frontier, not one rendered line — those modes lay their own lines out
WORD_MODE_CUE_CHARS = 60
CUE_GAP_S = 1.0                      # a pause this long between two words always starts a new cue
CUE_MAX_S = 6.0                      # and no cue runs longer than this


# ── fonts ────────────────────────────────────────────────────────────────────────────────────────────────────────────
_FONT_INDEX: dict = {}
_WEIGHTS = {"thin", "extralight", "light", "regular", "medium", "semibold", "bold", "extrabold", "black"}


def _norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", str(s).lower())


def _sfnt_names(path: Path) -> dict:
    """{name id: [strings]} from a TrueType/OpenType file's name table (ids 1, 2, 4, 6, 16, 17). Pure Python."""
    out: dict = {}
    try:
        data = path.read_bytes()
        if data[:4] == b"ttcf":
            data_off = struct.unpack(">I", data[12:16])[0]
        else:
            data_off = 0
        num = struct.unpack(">H", data[data_off + 4:data_off + 6])[0]
        name_off = None
        for i in range(num):
            rec = data_off + 12 + i * 16
            if data[rec:rec + 4] == b"name":
                name_off = struct.unpack(">I", data[rec + 8:rec + 12])[0]
                break
        if name_off is None:
            return out
        _fmt, count, str_off = struct.unpack(">HHH", data[name_off:name_off + 6])
        for i in range(count):
            r = name_off + 6 + i * 12
            pid, eid, lid, nid, ln, off = struct.unpack(">HHHHHH", data[r:r + 12])
            if nid not in (1, 2, 4, 6, 16, 17):
                continue
            raw = data[name_off + str_off + off:name_off + str_off + off + ln]
            if pid in (0, 3):
                s = raw.decode("utf-16-be", "ignore")
            elif pid == 1 and eid == 0:
                s = raw.decode("latin-1", "ignore")
            else:
                continue
            s = s.strip()
            if s and s not in out.setdefault(nid, []):
                out[nid].append(s)
    except (OSError, struct.error, IndexError):
        pass
    return out


def _font_index() -> list:
    """[(path, names)] for every font file in the kit's fonts folder (cached)."""
    key = str(FONTS)
    if key not in _FONT_INDEX:
        rows = []
        for f in sorted(list(FONTS.glob("*.ttf")) + list(FONTS.glob("*.otf"))):
            rows.append((f, _sfnt_names(f)))
        _FONT_INDEX[key] = rows
    return _FONT_INDEX[key]


def resolve_font(name: str) -> tuple:
    """(the name to write in the ASS, the font file or None) for a caption's font name.

    libass matches a family name (name id 1), a full name (id 4) or a PostScript name (id 6). A name that is already
    one of a kit file's family names is kept as written; one that only matches a full name, a PostScript name, a
    typographic family + style ("Poppins" + "ExtraBold") or a file name ("KodeMono") becomes that face's full name.
    An upright face is preferred over an italic one. A name the kit does not have is kept (a system font)."""
    want = _norm(name)
    if not want:
        return name, None
    best = None
    for f, nm in _font_index():
        italic = any("italic" in s.lower() for s in nm.get(2, []) + nm.get(17, []))
        fams = nm.get(1, [])
        full = (nm.get(4) or [None])[0]
        cands = []
        for fam in fams:
            if want == _norm(fam):
                cands.append((0, fam))                    # a family name, spelled the way the file spells it
        if want in {_norm(s) for s in nm.get(4, []) + nm.get(6, [])}:
            cands.append((1, full or name))
        for fam in nm.get(16, []) + fams:
            for sty in nm.get(17, []) + nm.get(2, []):
                if want == _norm(fam + sty):
                    cands.append((2, full or name))
        if want == _norm(f.stem) or want == _norm(f.stem.replace("-Regular", "")):
            cands.append((3, full or name))
        # a weight the kit has only as a variable font's instance ("Roboto Condensed Bold"): its family, so the
        # caption keeps the right face rather than falling back to a system font
        for fam in fams:
            nf = _norm(fam)
            if want.startswith(nf) and want[len(nf):] in _WEIGHTS:
                cands.append((4, fam))
        for rank, out in cands:
            score = (rank, 1 if italic else 0)
            if best is None or score < best[0]:
                best = (score, out, f)
    if best is None:
        return name, None
    return best[1], best[2]


def _font_measure(font_name: str, size: int):
    """A function giving the pixel width of a string in one of the kit's fonts (resolved like the captions' own font
    name), or a fair guess when the font is not there."""
    _n, path = resolve_font(font_name)
    if path is not None:
        try:
            from PIL import ImageFont
            ft = ImageFont.truetype(str(path), size)
            return lambda text: ft.getlength(text)
        except Exception:                                   # noqa: BLE001 - the guess below
            pass
    return lambda text: len(text) * size * 0.58


# ── small helpers (as in Frontier) ──────────────────────────────────────────────────────────────────────────────────
def _ass_time(t: float) -> str:
    t = max(0.0, t)
    h = int(t // 3600); m = int((t % 3600) // 60); sec = t % 60
    return f"{h}:{m:02d}:{sec:05.2f}"


def _split_one_line(text: str, limit: int) -> list:
    """Break a cue into chunks that each fit on ONE line."""
    words, lines, cur = text.split(), [], ""
    for w in words:
        cand = f"{cur} {w}".strip()
        if len(cand) <= limit or not cur:
            cur = cand
        else:
            lines.append(cur); cur = w
    if cur:
        lines.append(cur)
    return lines or [text]


def _ass_hex(hex_: str, alpha: str = "00") -> str:
    """"#RRGGBB" -> "&HAABBGGRR" (ASS colour order). An ASS colour ("&HBBGGRR&", "&HAABBGGRR") is accepted as is."""
    s = str(hex_ or "#FFFFFF").strip()
    if s.upper().startswith("&H"):
        h = s[2:].rstrip("&")
        if len(h) == 8:
            return f"&H{h.upper()}"
        if len(h) == 6:
            return f"&H{alpha}{h.upper()}"
    h = s.lstrip("#")
    if len(h) != 6:
        h = "FFFFFF"
    return f"&H{alpha}{h[4:6]}{h[2:4]}{h[0:2]}"


def _tag_colour(c) -> str:
    """Any colour ("#RRGGBB", "&HBBGGRR&", "&HAABBGGRR") as an ASS override colour "&HBBGGRR&"."""
    return f"&H{_ass_hex(c)[-6:]}&"


def _style_colour(c, default: str) -> str:
    """A style-line colour: an ASS colour is kept as written (Frontier wrote outline_colour raw), "#hex" converted."""
    if not c:
        return default
    s = str(c).strip()
    return s if s.upper().startswith("&H") else _ass_hex(s)


_NEG_WORDS = {"not", "never", "no", "cant", "dont", "wont", "hard", "harder", "hardest", "difficult", "wrong", "fail",
              "failed", "failure", "lose", "lost", "worst", "stop", "stopped", "impossible", "dangerous", "danger", "dead",
              "death", "killed", "broke", "broken", "expensive", "against", "without", "risk", "risky", "mistake", "lie",
              "lied", "nobody", "nothing", "problem", "trap", "scam", "banned", "illegal"}


def _kit_keyword(words: list) -> int:
    """The word a cluster or a pop lights up: the longest word of six letters or more (the last when tied), else -1."""
    best, k = -1, 0
    for i, w in enumerate(words):
        n = len(re.sub(r"[^\w]", "", w))
        if n >= 6 and n >= k:
            best, k = i, n
    return best


def _head(width: int, height: int, styles: list) -> str:
    return ("[Script Info]\nScriptType: v4.00+\n"
            f"PlayResX: {width}\nPlayResY: {height}\n"
            "WrapStyle: 2\nScaledBorderAndShadow: yes\n\n"
            "[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, "
            "OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, "
            "Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, "
            "MarginV, Encoding\n" + "".join(s + "\n" for s in styles)
            + "\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n")


# ── Docu adapter: cues + word clock from words.json, mute ranges from the scene list ────────────────────────────────
_SENT_END = re.compile(r"[.!?…][\"'”’)\]]*$")


def _tokens(words: list) -> list:
    """[(word, start, end)] — one token per space-free word, in time order; a "w" holding a space is shared out."""
    out = []
    for d in words or []:
        try:
            txt, s, e = str(d.get("w") or "").strip(), float(d.get("s")), float(d.get("e"))
        except (TypeError, ValueError, AttributeError):
            continue
        parts = txt.split()
        if not parts:
            continue
        e = max(e, s + 0.02)
        tot = float(sum(len(p) for p in parts)) or 1.0
        acc = 0.0
        for p in parts:
            a = s + (e - s) * acc / tot
            acc += len(p)
            out.append((p, a, s + (e - s) * acc / tot))
    out.sort(key=lambda x: x[1])
    return out


def cues_from_words(words: list, limit: int) -> tuple:
    """([(start, end, text)], {cue index: [(start, end) per word]}) — the SRT cues and word clock Frontier read from
    its job folder. A cue is one line of at most `limit` characters; it ends at a sentence end (.!?), before a pause
    of CUE_GAP_S, or at CUE_MAX_S. It runs from its first word's start to its last word's end, held to the next cue
    when the gap is under 0.25 s (as Frontier's subtitle writer did), so lines do not blink between words."""
    toks = _tokens(words)
    groups, cur = [], []
    for t in toks:
        if cur:
            too_long = len(" ".join(x[0] for x in cur + [t])) > limit
            pause = t[1] - cur[-1][2] >= CUE_GAP_S
            if too_long or pause or t[2] - cur[0][1] > CUE_MAX_S:
                groups.append(cur)
                cur = []
        cur.append(t)
        if _SENT_END.search(t[0]):
            groups.append(cur)
            cur = []
    if cur:
        groups.append(cur)
    cues, clock = [], {}
    for k, g in enumerate(groups):
        a, b = g[0][1], max(g[-1][2], g[0][1] + 0.3)
        if k + 1 < len(groups) and groups[k + 1][0][1] - b < 0.25:
            b = max(a + 0.05, groups[k + 1][0][1])
        cues.append((a, b, " ".join(x[0] for x in g)))
        clock[k] = [(round(x[1], 3), round(x[2], 3)) for x in g]
    return cues, clock


def mute_ranges(scenes: list) -> list:
    """[(t0, t1)] of every full-frame graphic scene (a type outside FOOTAGE_TYPES): no caption is drawn there."""
    out = []
    for s in scenes or []:
        if str(s.get("type") or "") in FOOTAGE_TYPES:
            continue
        try:
            t0, d = float(s.get("t0") or 0.0), float(s.get("duration") or 0.0)
        except (TypeError, ValueError):
            continue
        if d > 0:
            out.append((t0, t0 + d))
    return out


# ── the kit modes (Frontier's _build_burn_ass_kit) ──────────────────────────────────────────────────────────────────
def _build_kit(cues: list, clock: dict, mute: list, cap: dict, mode: str, width: int, height: int) -> tuple:
    font = resolve_font(str(cap.get("font") or SUB_FONT))[0]
    size = int(cap.get("size") or 56)
    accent = _ass_hex(str(cap.get("accent") or "#F2C230"))
    box = _ass_hex(str(cap.get("box_colour") or "#E5322D"))
    ink = _ass_hex(str(cap.get("colour") or "#FFFFFF"))
    stroke = _ass_hex(str(cap.get("outline_colour") or "#121212"))
    limit = int(cap.get("line_chars") or 26)
    marginv = int(cap.get("margin_v") or 120)
    lower, upper = bool(cap.get("lower")), bool(cap.get("upper"))
    hold = float(cap.get("hold") or 0.15)
    cx = width // 2

    def muted(a: float, b: float) -> bool:
        return any(a < e and b > s for s, e in mute)

    def tail(ci: int, en: float) -> float:
        # Frontier held a line `hold` past its cue; here the hold stops where the next cue starts, so two lines in
        # the same place never sit on top of each other (Frontier's SRT cues ran back to back, so it never had to)
        nxt = cues[ci + 1][0] if ci + 1 < len(cues) else math.inf
        return max(en, min(en + hold, nxt))

    def timed(ci: int, st: float, en: float, txt: str) -> list:
        ws = txt.split()
        wt = clock.get(ci) if clock.get(ci) and len(clock[ci]) == len(ws) else None
        if wt:
            return [(w, max(st, float(x[0]) - 0.04), max(st + 0.05, float(x[1]))) for w, x in zip(ws, wt)]
        n = max(1, len(ws))
        span = (en - st) / n
        return [(w, st + i * span, st + (i + 1) * span) for i, w in enumerate(ws)]

    def clean(w: str) -> str:
        w = w.replace("\\", "").replace("{", "(").replace("}", ")")
        return w.lower() if lower else (w.upper() if upper else w)

    def chunks(words: list, n_max: int, end: float) -> list:
        """[(text words, start, end)] — groups of up to n_max words, each shown until the next group starts.
        A group never runs past a sentence end, and a lone leftover word joins the group before it."""
        groups, cur = [], []
        for w in words:
            cur.append(w)
            if len(cur) >= n_max or re.search(r"[.!?…]$", w[0]):
                groups.append(cur)
                cur = []
        if cur:
            if groups and len(cur) == 1 and len(groups[-1]) < n_max + 1:
                groups[-1] = groups[-1] + cur
            else:
                groups.append(cur)
        out = []
        for gi, g in enumerate(groups):
            a = g[0][1]
            b = groups[gi + 1][0][1] if gi + 1 < len(groups) else end
            out.append(([clean(w) for w, _, _ in g], a, max(a + 0.25, b)))
        return out

    events, styles, kept = [], [], 0
    fmt_style = ("Style: {name},{font},{size},{ink},{sec},{outl},{back},{bold},0,0,0,100,100,{sp},0,{bs},{ol},{sh},{al},{ml},{mr},{mv},1")
    if mode == "cluster":
        styles += [fmt_style.format(name="KitL", font=font, size=size, ink=ink, sec="&H000000FF", outl=stroke, back="&H00000000",
                                    bold=0, sp=2, bs=1, ol=round(size / 22, 1), sh=round(size / 16, 1), al=7, ml=0, mr=0, mv=0),
                   fmt_style.format(name="KitR", font=font, size=size, ink=ink, sec="&H000000FF", outl=stroke, back="&H00000000",
                                    bold=0, sp=2, bs=1, ol=round(size / 22, 1), sh=round(size / 16, 1), al=9, ml=0, mr=0, mv=0),
                   fmt_style.format(name="KitLB", font=font, size=size, ink=ink, sec="&H000000FF", outl=box, back=box,
                                    bold=0, sp=2, bs=3, ol=round(size / 9, 1), sh=0, al=7, ml=0, mr=0, mv=0),
                   fmt_style.format(name="KitRB", font=font, size=size, ink=ink, sec="&H000000FF", outl=box, back=box,
                                    bold=0, sp=2, bs=3, ol=round(size / 9, 1), sh=0, al=9, ml=0, mr=0, mv=0)]
        top = int(cap.get("top") or 300)
        per = max(2, int(cap.get("words") or 6))          # a cluster holds a phrase, not a whole sentence
        side = 0
        groups = []
        for ci, (st, en, txt) in enumerate(cues):
            words = timed(ci, st, en, txt)
            if not words or muted(st, en + hold):
                continue
            for gi in range(0, len(words), per):
                g = words[gi:gi + per]
                g_end = words[gi + per][1] if gi + per < len(words) else tail(ci, en)
                groups.append((g, g_end))
        for g, g_end in groups:
            words = g
            right = side % 2 == 1
            side += 1
            pos = f"\\pos({int(cap.get('right_x') or 1660) if right else int(cap.get('left_x') or 260)},{top})"
            ws = [clean(w) for w, _, _ in words]
            key = _kit_keyword(ws)
            neg = next((i for i, w in enumerate(ws) if re.sub(r"[^\w]", "", w.lower()) in _NEG_WORDS), -1)
            rows, row = [], []
            for w in ws:
                if row and len(" ".join(row)) + 1 + len(w) > limit:
                    rows.append(row)
                    row = [w]
                else:
                    row.append(w)
            if row:
                rows.append(row)
            starts = [a for _, a, _ in words] + [g_end]
            for wi in range(len(ws)):
                a, b = starts[wi], starts[wi + 1]
                if b - a < 0.02:
                    continue
                shown, idx, plain, boxed = wi + 1, 0, [], []
                for r in rows:
                    pr, br = [], []
                    for w in r:
                        if idx < shown:
                            if idx == key and idx != neg:
                                pr.append(f"{{\\1c{accent}}}{w}{{\\1c{ink}}}")
                            else:
                                pr.append(w)
                            br.append(("{\\alpha&H00&}" if idx == neg else "{\\alpha&HFF&}") + w)
                        idx += 1
                    if pr:
                        plain.append(" ".join(pr))
                        boxed.append(" ".join(br))
                base = "KitR" if right else "KitL"
                events.append(f"Dialogue: 1,{_ass_time(a)},{_ass_time(b)},{base},,0,0,0,,{{{pos}}}" + "\\N".join(plain))
                if 0 <= neg <= wi:
                    events.append(f"Dialogue: 0,{_ass_time(a)},{_ass_time(b)},{base}B,,0,0,0,,{{{pos}}}" + "\\N".join(boxed))
            kept += 1
    elif mode == "typewriter":
        # SecondaryColour fully transparent + a \k per character: each letter appears as its time comes; the opaque
        # box (BorderStyle 3) is drawn for the whole line from the start — the black bar, then the typing
        styles.append(fmt_style.format(name="KitT", font=font, size=size, ink=ink, sec="&HFF000000", outl="&H00000000",
                                       back="&H00000000", bold=0, sp=0, bs=3, ol=round(size / 4.5, 1), sh=0, al=7, ml=0, mr=0, mv=0))
        x, y = int(cap.get("left_x") or 120), int(cap.get("top") or 96)
        for ci, (st, en, txt) in enumerate(cues):
            if not txt.strip() or muted(st, en + hold):
                continue
            parts = _split_one_line(clean(txt), limit)
            nchars = sum(len(p) for p in parts)
            per = max(0.012, min(0.055, (en - st) * 0.72 / max(1, nchars)))
            cs = max(1, int(round(per * 100)))
            body = "\\N".join("".join(f"{{\\k{cs}}}{c}" for c in p) for p in parts)
            events.append(f"Dialogue: 1,{_ass_time(st)},{_ass_time(tail(ci, en))},KitT,,0,0,0,,{{\\pos({x},{y})}}{body}")
            kept += 1
    elif mode == "shout":
        styles.append(fmt_style.format(name="KitS", font=font, size=size, ink=ink, sec="&H000000FF", outl=box, back="&H00000000",
                                       bold=-1, sp=0, bs=1, ol=round(size / 11, 1), sh=0, al=2, ml=60, mr=60, mv=marginv))
        for ci, (st, en, txt) in enumerate(cues):
            for ws, a, b in chunks(timed(ci, st, en, txt), int(cap.get("words") or 3), tail(ci, en)):
                if muted(a, b):
                    continue
                events.append(f"Dialogue: 1,{_ass_time(a)},{_ass_time(b)},KitS,,0,0,0,,"
                              f"{{\\fscx86\\fscy86\\t(0,80,\\fscx100\\fscy100)}}{' '.join(w.upper() for w in ws)}")
                kept += 1
    elif mode == "pop":
        styles.append(fmt_style.format(name="KitP", font=font, size=size, ink=ink, sec="&H000000FF", outl=stroke, back="&H00000000",
                                       bold=-1, sp=0, bs=1, ol=round(size / 30, 1), sh=round(size / 14, 1), al=5, ml=0, mr=0, mv=0))
        y = int(cap.get("y") or 720)
        for ci, (st, en, txt) in enumerate(cues):
            for ws, a, b in chunks(timed(ci, st, en, txt), int(cap.get("words") or 4), tail(ci, en)):
                if muted(a, b):
                    continue
                key = _kit_keyword(ws)
                text = " ".join(f"{{\\1c{accent}}}{w}{{\\1c{ink}}}" if i == key else w for i, w in enumerate(ws))
                plain = " ".join(ws)
                pop_in = "\\fscx84\\fscy84\\t(0,90,\\fscx100\\fscy100)"
                events.append(f"Dialogue: 0,{_ass_time(a)},{_ass_time(b)},KitP,,0,0,0,,"
                              f"{{\\pos({cx},{y}){pop_in}\\bord16\\blur18\\1a&HFF&\\3a&H70&\\3c&HFFFFFF&\\shad0}}{plain}")
                events.append(f"Dialogue: 1,{_ass_time(a)},{_ass_time(b)},KitP,,0,0,0,,{{\\pos({cx},{y}){pop_in}}}{text}")
                kept += 1
    elif mode == "pill":
        # a dark rounded pill drawn as an ASS shape under 4-6 words (one shape per group, measured with the real font,
        # so the per-word colour runs never split it); one text event per spoken word: the words already said are
        # white, the word being said takes the accent colour, the words to come are dim — nothing jumps
        pill_col = _ass_hex(str(cap.get("pill_colour") or "#000000"))[4:]
        pill_a = str(cap.get("pill_alpha") or "58")
        dim = _ass_hex(str(cap.get("dim") or "#9A9A9A"))[4:]
        acc, ink6 = accent[4:], ink[4:]
        styles.append(fmt_style.format(name="KitI", font=font, size=size, ink=ink, sec="&H000000FF", outl="&H00000000", back="&H00000000",
                                       bold=-1, sp=0, bs=1, ol=0, sh=0, al=5, ml=0, mr=0, mv=0))
        styles.append(fmt_style.format(name="KitIBox", font=font, size=size, ink=f"&H{pill_a}{pill_col}", sec="&H000000FF", outl="&H00000000",
                                       back="&H00000000", bold=0, sp=0, bs=1, ol=0, sh=0, al=5, ml=0, mr=0, mv=0))
        measure = _font_measure(font, size)
        pad_x, pad_y = int(size * 0.55), int(size * 0.26)
        box_h = int(size * 1.28) + 2 * pad_y
        y = height - marginv - box_h // 2
        r = min(18, box_h // 3)

        def pill_shape(w: int, h: int) -> str:
            x0, y0, x1, y1 = 0, 0, w, h
            return (f"m {x0 + r} {y0} l {x1 - r} {y0} b {x1} {y0} {x1} {y0} {x1} {y0 + r} l {x1} {y1 - r} b {x1} {y1} {x1} {y1} {x1 - r} {y1} "
                    f"l {x0 + r} {y1} b {x0} {y1} {x0} {y1} {x0} {y1 - r} l {x0} {y0 + r} b {x0} {y0} {x0} {y0} {x0 + r} {y0}")

        for ci, (st, en, txt) in enumerate(cues):
            allw = timed(ci, st, en, txt)
            for ws, a, b in chunks(allw, int(cap.get("words") or 5), tail(ci, en)):
                if muted(a, b):
                    continue
                starts, k0 = [], 0
                for w in ws:
                    for j in range(k0, len(allw)):
                        if clean(allw[j][0]) == w:
                            starts.append(max(a, allw[j][1]))
                            k0 = j + 1
                            break
                    else:
                        starts.append(a + (b - a) * len(starts) / max(1, len(ws)))
                starts[0] = a
                plain = " ".join(ws)
                w_px = int(measure(plain)) + 2 * pad_x
                pop = "\\fscx92\\fscy92\\t(0,70,\\fscx100\\fscy100)"
                events.append(f"Dialogue: 0,{_ass_time(a)},{_ass_time(b)},KitIBox,,0,0,0,,{{\\an5\\pos({cx},{y}){pop}\\p1}}{pill_shape(w_px, box_h)}{{\\p0}}")
                for i, w in enumerate(ws):
                    t0_ = starts[i]
                    t1_ = starts[i + 1] if i + 1 < len(ws) else b
                    if t1_ - t0_ < 0.03:
                        continue
                    text = " ".join((f"{{\\1c&H{acc}&}}{x}{{\\1c&H{ink6}&}}" if j == i else (x if j < i else f"{{\\1c&H{dim}&}}{x}{{\\1c&H{ink6}&}}"))
                                    for j, x in enumerate(ws))
                    fx = pop if i == 0 else ""
                    events.append(f"Dialogue: 1,{_ass_time(t0_)},{_ass_time(t1_)},KitI,,0,0,0,,{{\\an5\\pos({cx},{y}){fx}}}{text}")
                kept += 1
    elif mode == "stack":
        # kinetic typography: a block of 3-6 words builds word by word as they are spoken, beside the picture (left,
        # then right), 1-3 ragged lines; the key word bigger in the accent colour, a negative word red, the last word
        # of a sentence in the serif italic. One event per spoken word holding the WHOLE block, the words still to
        # come transparent — libass lays the lines out itself, so nothing is measured and nothing jumps.
        big_font = resolve_font(str(cap.get("big_font") or cap.get("font") or SUB_FONT))[0]
        serif = resolve_font(str(cap.get("serif_font") or "Playfair Display"))[0]
        red = _ass_hex(str(cap.get("box_colour") or "#E5322D"))
        s_main, s_big, s_serif = size, int(size * 1.4), int(size * 1.18)
        styles.append(fmt_style.format(name="KitK", font=font, size=s_main, ink=ink, sec="&H000000FF", outl=stroke, back="&H00000000",
                                       bold=0, sp=1, bs=1, ol=round(s_main / 24, 1), sh=round(s_main / 10, 1), al=4, ml=0, mr=0, mv=0))
        x_left, x_right = int(cap.get("left_x") or 150), int(cap.get("right_x") or 1770)
        y_mid = int(cap.get("y") or 540)
        per_line = int(cap.get("line_chars") or 16)
        side = 0
        for ci, (st, en, txt) in enumerate(cues):
            allw = timed(ci, st, en, txt)
            ends_sentence = txt.strip()[-1:] in ".?!"
            for ws, a, b in chunks(allw, int(cap.get("words") or 5), tail(ci, en)):
                if muted(a, b):
                    continue
                key = _kit_keyword(ws)
                starts, k0 = [], 0
                for w in ws:
                    for j in range(k0, len(allw)):
                        if clean(allw[j][0]) == w:
                            starts.append(max(a, allw[j][1]))
                            k0 = j + 1
                            break
                    else:
                        starts.append(a + (b - a) * len(starts) / max(1, len(ws)))
                starts[0] = a
                last_of_sentence = ends_sentence and ws[-1] == clean(allw[-1][0])
                # each word's look, and its weight in characters for the ragged wrap
                looks, weights = [], []
                for i, w in enumerate(ws):
                    if i == key:
                        looks.append(f"{{\\fn{big_font}\\fs{s_big}\\b1\\1c{accent}}}"); weights.append(len(w) * 1.4)
                    elif re.sub(r"[^a-z']", "", w.lower()) in _NEG_WORDS:
                        looks.append(f"{{\\1c{red}}}"); weights.append(len(w))
                    elif last_of_sentence and i == len(ws) - 1 and len(ws) > 2:
                        looks.append(f"{{\\fn{serif}\\fs{s_serif}\\i1}}"); weights.append(len(w) * 1.05)
                    else:
                        looks.append(""); weights.append(len(w))
                lines_, cur, cur_w = [], [], 0.0
                for i in range(len(ws)):
                    ww = weights[i] + (1 if cur else 0)
                    if cur and cur_w + ww > per_line:
                        lines_.append(cur); cur, cur_w = [i], weights[i]
                    else:
                        cur.append(i); cur_w += ww
                if cur:
                    lines_.append(cur)
                reset = f"{{\\fn{font}\\fs{s_main}\\b0\\i0\\1c{ink}}}"
                hold_to = b + hold
                al = 4 if side == 0 else 6
                x = x_left if side == 0 else x_right
                for i in range(len(ws)):
                    t0_ = starts[i]
                    t1_ = starts[i + 1] if i + 1 < len(ws) else hold_to
                    if t1_ - t0_ < 0.04:
                        continue
                    rows = []
                    for idxs in lines_:
                        parts_ = []
                        for j in idxs:
                            hidden = "{\\alpha&HFF&}" if j > i else "{\\alpha&H00&}"
                            parts_.append(f"{looks[j]}{hidden}{clean(ws[j])}{reset}")
                        rows.append(" ".join(parts_))
                    pop = "\\fscx90\\fscy90\\t(0,120,\\fscx100\\fscy100)" if i == 0 else ""
                    events.append(f"Dialogue: 1,{_ass_time(t0_)},{_ass_time(t1_)},KitK,,0,0,0,,"
                                  f"{{\\an{al}\\pos({x},{y_mid}){pop}}}" + "\\N".join(rows))
                side = 1 - side
                kept += 1
    else:   # comic
        styles.append(fmt_style.format(name="KitC", font=font, size=size, ink=ink, sec="&H000000FF", outl=stroke, back="&H00000000",
                                       bold=0, sp=0, bs=1, ol=round(size / 12, 1), sh=0, al=2, ml=60, mr=60, mv=marginv))
        for ci, (st, en, txt) in enumerate(cues):
            words = timed(ci, st, en, txt)
            parts = _split_one_line(clean(txt), limit)
            n = 0
            for pi, part in enumerate(parts):
                k = len(part.split())
                a = words[n][1] if n < len(words) else st
                b = (words[n + k][1] if n + k < len(words) else tail(ci, en))
                n += k
                if muted(a, b):
                    continue
                events.append(f"Dialogue: 1,{_ass_time(a)},{_ass_time(max(a + 0.25, b))},KitC,,0,0,0,,"
                              f"{{\\fscx80\\fscy80\\t(0,90,\\fscx100\\fscy100)}}{part}")
                kept += 1
    return styles, events, kept, f"{mode}, {font} {size}px"


# ── the plain caption (Frontier's _build_burn_ass) ──────────────────────────────────────────────────────────────────
def _build_plain(cues: list, clock: dict, mute: list, cap: dict, accent: str, center: bool,
                 width: int, height: int) -> tuple:
    size = int(cap.get("size") or (SUB_SIZE_CENTER_PX if center else SUB_SIZE_PX))
    font = resolve_font(str(cap.get("font") or (SUB_FONT_SERIF if center else SUB_FONT)))[0]
    limit = int(cap.get("line_chars") or SUB_LINE_CHARS)
    upper = bool(cap.get("upper"))
    thick = float(cap.get("outline") or 1.0)
    # "karaoke": false keeps every word the same colour — a documentary caption sits still
    karaoke = cap.get("karaoke") is not False
    soft = float(cap.get("shadow") or 1.0)

    def muted(a: float, b: float) -> bool:
        # drop a cue that overlaps a scene window at all — a half-shown line blinking on at the cut looks worse
        return any(a < e and b > s for s, e in mute)

    def trimmed(a: float, b: float):
        # a cue that only grazes a scene window — its last or first few tenths of a second — keeps the part
        # on the footage; a real overlap is dropped
        for s, e in mute:
            if a < e and b > s:
                if b - s <= 0.5 and s - a >= 0.8:
                    b = s
                elif e - a <= 0.5 and b - e >= 0.8:
                    a = e
                else:
                    return None
        return a, b

    events, kept, dropped = [], 0, 0
    for ci, (st, en, txt) in enumerate(cues):
        ab = trimmed(st, en)
        if ab is None:
            dropped += 1
            continue
        st, en = ab
        parts = _split_one_line(txt.upper() if upper else txt, limit)
        span = (en - st) / len(parts)
        wt = clock.get(ci) if clock.get(ci) and len(clock[ci]) == len(txt.split()) else None
        firsts = []
        for part in parts:
            firsts.append(sum(len(x.split()) for x in parts[:len(firsts)]))
        for i, line in enumerate(parts):
            a = st + i * span
            b = a + span
            if wt:
                # a line comes up as its first word is said and goes as the next line's first word begins
                a = st if i == 0 else max(st, wt[firsts[i]][0] - 0.06)
                b = en if i == len(parts) - 1 else min(en, max(a + 0.3, wt[firsts[i + 1]][0] - 0.06))
            if muted(a, b):
                dropped += 1
                continue
            line = line.replace("\\", "").replace("{", "(").replace("}", ")")
            if not karaoke:
                events.append(f"Dialogue: 0,{_ass_time(a)},{_ass_time(b)},Def,,0,0,0,,"
                              f"{{\\fad({SUB_FADE_MS},{SUB_FADE_MS})}}{line}")
                kept += 1
                continue
            # the word being spoken sweeps to the accent colour and back — the highlight travels with the voice
            words = line.split()
            if wt:
                # each word lights as the voice says it (a hair early, so the eye is there when the ear is)
                own = wt[firsts[i]:firsts[i] + len(words)]
                marks = [max(0.0, x[0] - a - 0.04) for x in own] + [max(0.0, min(b - a, own[-1][1] - a))]
            else:
                weights = [max(2, len(w)) for w in words]
                tot = float(sum(weights)) or 1.0
                marks, acc = [], 0.0
                for wgt in weights:
                    marks.append((b - a) * 0.92 * (acc / tot))
                    acc += wgt
                marks.append((b - a) * 0.92)
            chunks = []
            for wi, w in enumerate(words):
                on = int(marks[wi] * 1000)
                off = int(marks[wi + 1] * 1000)
                chunks.append(
                    f"{{\\1c&HFFFFFF&"
                    f"\\t({on},{min(off, on + 90)},\\1c{accent})"
                    f"\\t({off},{off + 90},\\1c&HFFFFFF&)}}{w}")
            events.append(f"Dialogue: 0,{_ass_time(a)},{_ass_time(b)},Def,,0,0,0,,"
                          f"{{\\fad({SUB_FADE_MS},{SUB_FADE_MS})}}{' '.join(chunks)}")
            kept += 1

    align = 5 if center else 2          # 5 = middle-centre, 2 = bottom-centre
    # distance from the bottom edge for a bottom-anchored caption (smaller sits lower); captions.margin_v overrides
    marginv = 0 if center else int(cap.get("margin_v") or 96)
    primary = "&H00FFFFFF"
    bold = 0                            # the ExtraBold cut carries the weight itself
    # 1 = a stroke around each letter, 3 = a filled band behind the line (captions.box)
    border_style = 3 if cap.get("box") else 1
    k = size / 56.0
    outline = round(4.2 * k * thick, 2)
    outline_colour = _style_colour(cap.get("outline_colour"), "&H00121212")
    shadow = round(3.2 * k * (1.0 + (thick - 1.0) * 0.5) * soft, 2)
    style = (f"Style: Def,{font},{size},{primary},&H000000FF,{outline_colour},&H64000000,{bold},0,0,0,"
             f"100,100,0,0,{border_style},{outline},{shadow},{align},80,80,{marginv},1")
    note = f"plain{' karaoke' if karaoke else ''}, {font} {size}px" + (f", {dropped} muted" if dropped else "")
    return [style], events, kept, note


# ── public API ──────────────────────────────────────────────────────────────────────────────────────────────────────
def build_ass(words, scenes, cap, out_ass, accent=None, width=1920, height=1080, center=None) -> str:
    """Write the burn-in .ass for a video and return its path.

    words   [{"w", "s", "e"}] — the voice's words (data/words.json)
    scenes  the rendered scene list ({"type", "t0", "duration"}); full-frame graphics mute the captions
    cap     a style's captions dict (look.captions); "mode" picks a kit mode, none = the plain caption; "off" = none
    accent  the karaoke colour of the plain caption ("#RRGGBB" or an ASS "&HBBGGRR&", e.g. look.caption_accent);
            falls back to cap["accent"], then Frontier's gold. The kit modes take theirs from cap["accent"].
    center  the plain caption mid-frame (Frontier's look.center_subtitles); default cap.get("center")"""
    cap = dict(cap or {})
    out_ass = Path(out_ass)
    out_ass.parent.mkdir(parents=True, exist_ok=True)
    width, height = int(width), int(height)
    center = bool(cap.get("center")) if center is None else bool(center)
    mute = mute_ranges(scenes)
    mode = str(cap.get("mode") or "").lower()
    if cap.get("off"):
        styles, events, note = [], [], "off"
    elif mode in KIT_MODES:
        limit = int(cap.get("line_chars") or 26)
        cue_chars = int(cap.get("cue_chars") or (limit if mode in ("typewriter", "comic") else max(limit, WORD_MODE_CUE_CHARS)))
        cues, clock = cues_from_words(words, cue_chars)
        styles, events, kept, note = _build_kit(cues, clock, mute, cap, mode, width, height)
        note += f": {kept} lines"
    else:
        cues, clock = cues_from_words(words, int(cap.get("cue_chars") or cap.get("line_chars") or SUB_LINE_CHARS))
        acc = _tag_colour(accent or cap.get("accent") or CAPTION_ACCENT)
        styles, events, kept, note = _build_plain(cues, clock, mute, cap, acc, center, width, height)
        note += f": {kept} lines"
    out_ass.write_text(_head(width, height, styles) + "\n".join(events) + "\n", encoding="utf-8")
    print(f"captions ({note}) -> {out_ass}")
    return str(out_ass)


def _ff(path) -> str:
    """A path the way ffmpeg's filter parser wants it (Windows backslashes and drive colons escaped)."""
    return str(path).replace("\\", "/").replace(":", r"\:")


def burn(video_in, ass_path, video_out, fonts_dir, nvenc=False) -> None:
    """Burn the .ass into the video (re-encode; the audio, when there is any, is copied)."""
    vf = f"ass='{_ff(ass_path)}':fontsdir='{_ff(fonts_dir)}'"
    enc = (["-c:v", "h264_nvenc", "-preset", "p5", "-cq", "19"] if nvenc
           else ["-c:v", "libx264", "-preset", "veryfast", "-crf", "18"])
    Path(video_out).parent.mkdir(parents=True, exist_ok=True)
    cmd = (["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(video_in), "-vf", vf,
            "-map", "0:v:0", "-map", "0:a?"] + enc + ["-pix_fmt", "yuv420p", "-c:a", "copy",
                                                      "-movflags", "+faststart", str(video_out)])
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"caption burn failed: {r.stderr.strip()[-800:]}")


def caption_settings(doc: dict) -> tuple:
    """(cap, accent, center) from a style or template json: look.captions, captions or frontier.look.captions."""
    for look in (doc.get("look"), doc, (doc.get("frontier") or {}).get("look")):
        if isinstance(look, dict) and isinstance(look.get("captions"), dict):
            return dict(look["captions"]), look.get("caption_accent"), bool(look.get("center_subtitles"))
    return {}, None, False


def _probe_size(video: str) -> tuple:
    try:
        r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height",
                            "-of", "csv=p=0:s=x", str(video)], capture_output=True, text=True, check=True)
        w, h = r.stdout.strip().split("x")[:2]
        return int(w), int(h)
    except (subprocess.CalledProcessError, ValueError, OSError):
        return 1920, 1080


def main(argv: list) -> int:
    if len(argv) != 5:
        print(__doc__.strip().splitlines()[-1].strip())
        return 2
    words_f, scenes_f, style_f, vin, vout = argv
    words = json.loads(Path(words_f).read_text(encoding="utf-8"))
    scenes = json.loads(Path(scenes_f).read_text(encoding="utf-8"))
    if isinstance(scenes, dict):
        scenes = scenes.get("scenes") or []
    cap, accent, center = caption_settings(json.loads(Path(style_f).read_text(encoding="utf-8")))
    w, h = _probe_size(vin)
    ass = build_ass(words, scenes, cap, Path(vout).with_suffix(".ass"), accent=accent, width=w, height=h, center=center)
    burn(vin, ass, vout, FONTS)
    print(f"burned -> {vout}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
