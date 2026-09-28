"""
Sound design and the final mix.

Sound effects are synthesised here (no sample library needed) and placed from the
scenes themselves: a stamp scene already knows when its stamp lands, a map when
its pin drops, a strip when its typewriter runs - so every hit is frame-accurate
with the picture without a separate spotting pass.

Music beds are laid per act with crossfades and ducked under the narrator by an
envelope follower on the voiceover; the result is loudness-normalised for YouTube.
"""

import os
import json
import subprocess

import numpy as np
from scipy import signal

SR = 48000


# ------------------------------------------------------------------ audio io

def load(path, sr=SR, ch=2):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-f", "f32le", "-ac", str(ch), "-ar", str(sr), "-"],
                         capture_output=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, ch).copy()


def save_wav(path, x, sr=SR):
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ac", str(x.shape[1]), "-ar", str(sr),
                          "-i", "-", "-c:a", "pcm_s24le", path], stdin=subprocess.PIPE)
    p.stdin.write(x.astype(np.float32).tobytes())
    p.stdin.close()
    p.wait()


# ------------------------------------------------------------------ synthesis

_rs = np.random.RandomState(1234)


def _t(d):
    return np.arange(int(d * SR)) / SR


def _bp(x, lo, hi, order=2):
    sos = signal.butter(order, [lo, hi], btype="band", fs=SR, output="sos")
    return signal.sosfilt(sos, x)


def _lp(x, f, order=2):
    return signal.sosfilt(signal.butter(order, f, btype="low", fs=SR, output="sos"), x)


def _hp(x, f, order=2):
    return signal.sosfilt(signal.butter(order, f, btype="high", fs=SR, output="sos"), x)


def _norm(x, peak=0.9):
    m = np.max(np.abs(x)) or 1.0
    return x / m * peak


def _reverb(x, secs=1.2, mix=0.25):
    n = int(secs * SR)
    ir = _rs.randn(n) * np.exp(-np.linspace(0, 7, n))
    ir = _lp(ir, 6000)
    conv = signal.fftconvolve(x, ir)
    wet = np.zeros(len(x) + n)
    wet[:min(len(wet), len(conv))] = conv[:len(wet)]
    dry = np.concatenate([x, np.zeros(n)])
    return dry * (1 - mix) + _norm(wet, np.max(np.abs(x))) * mix


def whoosh(d=0.7, lo=300, hi=5000, rev=True):
    t = _t(d)
    n = _rs.randn(len(t))
    # sweep a band-pass up then down across the body of the whoosh
    out = np.zeros_like(n)
    steps = 24
    for k in range(steps):
        a, b = int(len(t) * k / steps), int(len(t) * (k + 1) / steps)
        p = k / (steps - 1)
        f = lo + (hi - lo) * np.sin(np.pi * p) ** 1.5
        out[a:b] = _bp(n, max(60, f * 0.55), min(SR / 2 - 100, f * 1.6))[a:b]
    env = np.sin(np.pi * np.clip(t / d, 0, 1)) ** 2.2
    x = out * env
    return _norm(_reverb(x, 0.6, 0.18) if rev else x, 0.8)


def impact(d=1.6, f0=58):
    t = _t(d)
    body = np.sin(2 * np.pi * (f0 * t - 18 * t ** 2)) * np.exp(-t * 3.2)
    thump = np.sin(2 * np.pi * 110 * t) * np.exp(-t * 18)
    crack = _hp(_rs.randn(len(t)), 1800) * np.exp(-t * 40) * 0.35
    x = body * 0.9 + thump * 0.6 + crack
    return _norm(_reverb(_lp(x, 9000), 1.4, 0.3), 0.95)


def riser(d=1.8):
    t = _t(d)
    n = _rs.randn(len(t))
    x = np.zeros_like(n)
    steps = 30
    for k in range(steps):
        a, b = int(len(t) * k / steps), int(len(t) * (k + 1) / steps)
        f = 400 + 5000 * (k / steps) ** 2
        x[a:b] = _bp(n, f * 0.6, min(SR / 2 - 200, f * 1.5))[a:b]
    tone = np.sin(2 * np.pi * (110 * t + 90 * t ** 2 / d)) * 0.25
    env = (t / d) ** 2.6
    return _norm((x + tone) * env, 0.7)


def stamp_hit():
    t = _t(0.45)
    thud = np.sin(2 * np.pi * 85 * t) * np.exp(-t * 26)
    slap = _bp(_rs.randn(len(t)), 700, 4000) * np.exp(-t * 55)
    return _norm(_reverb(thud * 1.0 + slap * 0.7, 0.35, 0.12), 0.9)


def paper(d=0.35):
    t = _t(d)
    n = _bp(_rs.randn(len(t)), 1500, 9000)
    crackle = (_rs.rand(len(t)) > 0.985) * _rs.randn(len(t)) * 3
    env = np.sin(np.pi * np.clip(t / d, 0, 1)) ** 1.2
    return _norm((n + _hp(crackle, 2000)) * env, 0.5)


def type_click():
    t = _t(0.05)
    x = _bp(_rs.randn(len(t)), 1800, 7000) * np.exp(-t * 160) + np.sin(2 * np.pi * 180 * t) * np.exp(-t * 90) * 0.4
    return _norm(x, 0.6)


def typewriter(d, cps=30):
    out = np.zeros(int(d * SR) + SR // 10)
    k = type_click()
    n = int(d * cps)
    for i in range(n):
        at = int((i / cps + _rs.uniform(-0.006, 0.006)) * SR)
        at = max(0, at)
        out[at:at + len(k)] += k[:len(out) - at] * _rs.uniform(0.6, 1.0)
    return out


def pop():
    t = _t(0.18)
    f = 900 * np.exp(-t * 10) + 350
    return _norm(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 22), 0.6)


def ping():
    t = _t(1.4)
    x = (np.sin(2 * np.pi * 1320 * t) + 0.4 * np.sin(2 * np.pi * 2640 * t)) * np.exp(-t * 4.5)
    return _norm(_reverb(x, 1.0, 0.35), 0.45)


def zip_(d=0.6):
    t = _t(d)
    x = _bp(_rs.randn(len(t)), 2500, 8000) * np.sin(np.pi * np.clip(t / d, 0, 1))
    return _norm(x, 0.35)


def tick():
    t = _t(0.03)
    return _norm(_hp(_rs.randn(len(t)), 3000) * np.exp(-t * 200), 0.4)


def counter_roll(d):
    out = np.zeros(int(d * SR) + 2000)
    k = tick()
    n = int(d * 22)
    for i in range(n):
        p = i / max(1, n)
        at = int(d * (1 - (1 - p) ** 2) * SR)
        out[at:at + len(k)] += k[:len(out) - at] * 0.6
    return out


def pen(d=0.9):
    t = _t(d)
    x = _bp(_rs.randn(len(t)), 2500, 7000) * (0.5 + 0.5 * np.abs(np.sin(2 * np.pi * 7 * t)))
    return _norm(x * np.sin(np.pi * np.clip(t / d, 0, 1)) ** 0.5, 0.3)


def tv_on():
    t = _t(0.6)
    static = _bp(_rs.randn(len(t)), 800, 9000) * np.exp(-t * 4)
    hum = np.sin(2 * np.pi * 60 * t) * 0.3 * np.exp(-t * 2)
    return _norm(static + hum, 0.5)


def clank():
    """a brass pan settling: a few inharmonic partials with a quick decay"""
    t = _t(1.2)
    x = sum(a * np.sin(2 * np.pi * f * t) * np.exp(-t * d) for f, a, d in
            ((523, 1.0, 5.0), (1187, 0.6, 7.0), (1893, 0.35, 9.0), (2771, 0.2, 12.0)))
    x += _hp(_rs.randn(len(t)), 2000) * np.exp(-t * 60) * 0.5
    return _norm(x, 0.5)


def flaps(d):
    """split-flap clatter: dense ticks thinning out as the letters settle"""
    out = np.zeros(int(d * SR) + 2000)
    k = tick()
    n = int(d * 60)
    for i in range(n):
        p = i / max(1, n)
        at = int(d * p * SR) + int(_rs.rand() * 400)
        if _rs.rand() < 1 - 0.7 * p and at + len(k) < len(out):
            out[at:at + len(k)] += k * (0.5 + 0.5 * _rs.rand())
    return _norm(out, 0.45)


def sting():
    """a news sting: a bright stacked stab over a short rising swoosh"""
    t = _t(1.8)
    stab = sum(np.sin(2 * np.pi * f * t) * a for f, a in ((392, 1.0), (523.3, 0.8), (659.3, 0.7), (784, 0.5), (1046.5, 0.35)))
    env = np.clip(t / 0.01, 0, 1) * np.exp(-t * 2.6)
    sw = _bp(_rs.randn(len(t)), 800, 6000) * np.clip(1 - t / 0.3, 0, 1) ** 2 * 0.6
    return _norm(_reverb(stab * env + sw, 1.4, 0.3), 0.7)


def glitch():
    """digital glitch: chopped square bursts and crushed noise"""
    t = _t(0.4)
    sq = np.sign(np.sin(2 * np.pi * (180 + 900 * (t * 7 % 1)) * t))
    gate = (np.floor(t * 38) % 3 != 0).astype(np.float32)
    x = (0.5 * sq + 0.5 * np.round(_rs.randn(len(t)) * 3) / 3) * gate * np.exp(-t * 4)
    return _norm(_hp(x, 300), 0.35)


def drill(d):
    """percussion drilling: a low motor rumble and rapid hammer hits"""
    t = _t(d)
    rum = np.sin(2 * np.pi * 52 * t) * 0.5 + _lp(_rs.randn(len(t)), 180) * 1.2
    hits = np.zeros(len(t))
    k = _bp(_rs.randn(int(0.03 * SR)), 900, 4000) * np.exp(-np.arange(int(0.03 * SR)) / SR * 120)
    for i in range(int(d * 11)):
        a = int(i / 11 * SR)
        hits[a:a + len(k)] += k[:len(hits) - a]
    env = np.clip(t / 0.4, 0, 1) * np.clip((d - t) / 0.2, 0, 1)
    return _norm((rum * 0.6 + hits * 0.5) * env, 0.5)


def shatter():
    """the bit breaking: a hard crack, ringing steel, falling fragments, a low thump"""
    t = _t(1.6)
    crack = _hp(_rs.randn(len(t)), 1800) * np.exp(-t * 40)
    ring = sum(a * np.sin(2 * np.pi * f * t) * np.exp(-t * dd) for f, a, dd in ((2210, 0.5, 6), (3470, 0.35, 8), (5130, 0.25, 11), (1380, 0.3, 5)))
    thump = np.sin(2 * np.pi * (70 * t - 18 * t * t)) * np.exp(-t * 7)
    bits = np.zeros(len(t))
    for i in range(14):
        a = int((0.08 + _rs.rand() * 0.9) * SR)
        n = int(0.02 * SR)
        bits[a:a + n] += _hp(_rs.randn(n), 3000)[:len(bits) - a] * np.exp(-np.arange(n) / SR * 200) * (0.2 + 0.3 * _rs.rand())
    return _norm(crack * 0.9 + ring * 0.5 + thump * 0.8 + bits * 0.5, 0.9)


def boom_soft():
    t = _t(2.2)
    x = np.sin(2 * np.pi * (46 * t - 5 * t ** 2)) * np.exp(-t * 1.8)
    return _norm(_lp(x, 400), 0.8)


BANK = {}


def bank():
    if not BANK:
        BANK.update(whoosh=whoosh(0.7), whoosh_s=whoosh(0.45, 600, 7000), whoosh_l=whoosh(1.4, 200, 3500),
                    impact=impact(), riser=riser(), stamp=stamp_hit(), paper=paper(), pop=pop(),
                    ping=ping(), zip=zip_(), pen=pen(), tv=tv_on(), boom=boom_soft(), clank=clank(), sting=sting(), glitch=glitch(), shatter=shatter())
    return BANK


# ------------------------------------------------------------------ spotting

CALM_KEEP = {"paper", "pen", "type", "ping", "roll", "pop", "clank"}


def spot(scenes, style="full"):
    """(time, name, gain_db, extra) for every sound the picture calls for.
    style="calm" (documentary): no whooshes on cuts, no stamps or impacts - only soft,
    physical sounds (paper, pen, typing, a ping on a map pin), a few dB lower."""
    if style == "calm":
        ev = spot(scenes, "full")
        return [(t, n, db - 4, kw) for t, n, db, kw in ev if n in CALM_KEEP]
    ev = []

    def add(t, name, db=0.0, **kw):
        # a cue before its own scene starts (items shown as already there) makes no sound
        if cur and t < cur[0] - 0.3 and name not in ("riser", "whoosh", "whoosh_s", "whoosh_l"):
            return
        ev.append((max(0.0, t), name, db, kw))

    cur = []

    prev = None
    for s in scenes:
        t0, ty = s["t0"], s["type"]
        cur[:] = [t0]
        graphic = ty not in ("clip", "photo")
        # cuts into graphic scenes carry a whoosh; clip-to-clip and photo cuts stay clean
        if graphic and ty not in ("chapter", "title", "segment") and prev is not None:
            add(t0 - 0.28, "whoosh_s" if ty in ("words", "stat", "quote") else "whoosh", -9)
        if ty == "chapter":
            add(t0 - 1.75, "riser", -13)
            add(t0, "impact", -7)
            add(t0 + 0.85, "whoosh", -12)
        if ty == "title":
            add(t0 + 0.45, "impact", -9)
            add(t0 + 0.4, "whoosh_l", -14)
        if ty == "words":
            for it in s.get("items", []):
                add(t0 + float(it.get("at", 0)), "stamp" if it.get("size", 150) >= 120 else "pop", -10)
                if it.get("strike"):
                    add(t0 + float(it["strike"]), "zip", -8)
        if ty == "stat":
            add(t0 + 0.35, "whoosh_s", -14)
            if s.get("count", True) is not False:
                add(t0 + 0.35, "roll", -12, d=float(s.get("countFor", 1.6)))
        if ty in ("collage", "headlines"):
            for it in s.get("items", []):
                at = t0 + float(it.get("at", 0))
                k = it.get("k", "headline")
                if k in ("photo", "cut", "note"):
                    add(at, "paper", -9)
                elif k == "stamp" or ty == "headlines":
                    add(at, "stamp", -5)
                elif k == "strip":
                    add(at + 0.25, "type", -15, d=len(it.get("text", "")) / 30.0)
                elif k == "pin":
                    add(at + 0.35, "pop", -12)
                elif k in ("string", "arrow", "circle"):
                    add(at, "zip", -12)
                elif k == "stat":
                    add(at, "stamp", -8)
                    add(at + 0.1, "roll", -13, d=1.2)
                elif k == "title":
                    add(at, "whoosh_s", -15)
                elif k == "tag":
                    add(at + 0.3, "paper", -8)
        if ty == "baskets":
            if s.get("reveal"):
                for i in range(3):
                    add(t0 + float(s.get("at", 0.3)) + i * float(s.get("gap", 0.9)), "paper", -8)
                    add(t0 + float(s.get("at", 0.3)) + i * float(s.get("gap", 0.9)) + 0.45, "stamp", -8)
            elif s.get("active", -1) >= 0:
                add(t0 + float(s.get("focusAt", 0.4)), "paper", -9)
                add(t0 + float(s.get("stampAt", 1.0)), "stamp", -5)
            else:
                add(t0 + float(s.get("stampAt", 0.6)), "stamp", -9)
        if ty == "checklist":
            for it in s.get("items", []):
                add(t0 + float(it["at"]) + 0.3, "stamp" if it.get("mark") == "no" else "pop", -11)
        if ty == "measure":
            for b in s.get("bars", []):
                add(t0 + float(b.get("at", 0)) + 0.2, "whoosh_s", -16)
            if s.get("stamp"):
                add(t0 + float(s["stamp"]["at"]), "stamp", -5)
        if ty == "map":
            add(t0, "whoosh_l", -14)
            for p in s.get("pins", []):
                add(t0 + float(p.get("at", 0)) + 0.4, "ping", -10)
            for r in s.get("routes", []):
                add(t0 + float(r.get("at", 0)), "zip", -14)
        if ty == "ledger":
            for ln in s.get("lines", []):
                add(t0 + float(ln.get("at", 0)), "pen", -10)
            if s.get("circle"):
                add(t0 + float(s["circle"]["at"]), "pen", -8)
        if ty == "timeline":
            for st in s.get("stops", [])[1:]:
                add(t0 + float(st["at"]) - 0.3, "whoosh_s", -14)
        if ty == "spotlight":
            add(t0 + float(s.get("hit", 0.7)), "boom", -10)
            add(t0 + float(s.get("hit", 0.7)) + 1.2, "paper", -14)
        if ty == "depth":
            add(t0 + float(s.get("hit", 0.6)), "whoosh_s", -11)
        if ty in ("card", "newspaper"):
            add(t0, "paper", -8)
            add(t0, "whoosh", -13)
        if ty == "tv":
            add(t0 + 0.05, "tv", -12)
        if ty == "split":
            add(t0, "whoosh", -12)
        if ty == "geo":
            add(t0, "paper", -12)
        if ty == "filter":
            for it in s.get("items", []):
                add(t0 + float(it.get("at", 0)) + 0.3, "paper", -11)
        if ty == "network":
            for nd in s.get("nodes", []):
                add(t0 + float(nd.get("at", 0)) + 0.4, "pop", -13)
        if ty == "scales":
            for it in s.get("items", []):
                add(t0 + float(it.get("at", 0)) + 0.35, "paper", -10)
                add(t0 + float(it.get("at", 0)) + 0.45, "clank", -17)
            for k in s.get("tilts", []):
                add(t0 + float(k["at"]), "clank", -15)
        if ty == "scoreboard":
            for r in s.get("rows", []):
                add(t0 + float(r.get("at", 0)), "flaps", -13, d=0.9)
                if r.get("stamp"):
                    add(t0 + float(r["stamp"]["at"]), "stamp", -7)
        if ty == "verdict":
            for i, a in enumerate(s.get("headAt", [0.1, 0.45])):
                add(t0 + float(a), "stamp", -7)
            for it in s.get("items", []):
                add(t0 + float(it.get("at", 0)) + 0.25, "pen", -12)
            if s.get("stamp"):
                add(t0 + float(s["stamp"]["at"]), "stamp", -5)
        if ty == "ledgerlist":
            for i, it in enumerate(s.get("items", [])):
                add(t0 + float(it.get("at", 0.8 + i * 0.5)), "pen", -12)
        if ty == "bars":
            for i, b in enumerate(s.get("bars", [])):
                add(t0 + float(b.get("at", 0.8 + i * 0.6)) + 0.2, "roll", -18, d=1.2)
        if ty == "segment":
            add(t0 - 0.2, "whoosh", -11)
            add(t0 + 0.55, "sting", -12)
        if ty == "breaking":
            a0 = float(s.get("at", 0.25))
            add(t0 + a0 - 0.05, "glitch", -12)
            add(t0 + a0, "sting", -9)
            add(t0 + float(s.get("headAt", a0 + 0.5)), "whoosh_s", -15)
        if ty == "borehole":
            B = dict(draw=0.1, drill=1.0, hit=4.0); B.update(s.get("beats", {}))
            if s.get("shatter", True) is not False:
                add(t0 + float(B["drill"]), "drill", -15, d=max(0.3, float(B["hit"]) - float(B["drill"])))
                add(t0 + float(B["hit"]), "shatter", -7)
            else:
                add(t0 + float(B["drill"]), "drill", -17, d=max(0.5, float(s["duration"]) - float(B["drill"]) - 0.5))
            for lb in s.get("labels", []):
                add(t0 + float(lb.get("at", 0)), "pop", -16)
            if s.get("stamp"):
                add(t0 + float(s["stamp"]["at"]), "stamp", -8)
        if ty == "factcheck":
            ra = float(s.get("ratingAt", 1.6))
            add(t0 + 0.8, "roll", -16, d=max(0.3, ra - 0.8))
            add(t0 + ra, "stamp", -7)
        if ty == "echo":
            hs = s.get("headlines", [])
            for i, h in enumerate(hs):
                at = h.get("at") if isinstance(h, dict) and h.get("at") is not None else 0.2 + i * float(s.get("gap", 0.18))
                add(t0 + float(at), "pop", -17)
            c = float(s.get("collapseAt", 3.0))
            add(t0 + c, "whoosh_l", -12)
            add(t0 + c + 0.6, "impact", -10)
        if ty == "columns":
            for it in s.get("items", []):
                add(t0 + float(it.get("at", 0)), "whoosh_s", -18)
            if s.get("gapAt") is not None:
                add(t0 + float(s["gapAt"]), "zip", -12)
        if ty == "videowall":
            add(t0 + 0.05, "tv", -15)
            add(t0 + float(s.get("pushAt", 1.2)), "whoosh_l", -13)
        if ty == "newslist":
            for it in s.get("items", []):
                add(t0 + float(it.get("at", 0)), "whoosh_s", -17)
                if it.get("status"):
                    add(t0 + float(it.get("statusAt", float(it.get("at", 0)) + 0.5)), "stamp", -12)
        for o in s.get("overlays", []):
            if o["type"] == "newslower":
                add(t0 + float(o.get("at", 0.4)), "whoosh_s", -16)
            if o["type"] == "flash":
                add(t0 + float(o.get("at", 0)), "impact", -6)
            if o["type"] in ("chip", "lower"):
                add(t0 + float(o.get("at", 0.5)), "whoosh_s", -20)
        prev = s
    return ev


# ------------------------------------------------------------------ music

def music_bed(plan, kit_dir, total):
    out = np.zeros((int(total * SR) + SR, 2), np.float32)
    xf = 2.5
    for i, m in enumerate(plan):
        a, b = m["from"], (plan[i + 1]["from"] if i + 1 < len(plan) else total)
        x = load(os.path.join(kit_dir, "music", m["track"]))
        x = x[int(m.get("skip", 0) * SR):]
        need = int((b - a + xf) * SR)
        while len(x) < need:
            x = np.concatenate([x, x])
        x = x[:need] * (10 ** (m.get("db", 0) / 20))
        n = len(x)
        env = np.ones(n, np.float32)
        fi = int((xf if i else 1.5) * SR)
        env[:fi] = np.linspace(0, 1, fi) ** 1.5
        fo = int(xf * SR) if i + 1 < len(plan) else int(4.0 * SR)
        env[-fo:] *= np.linspace(1, 0, fo) ** 1.5
        s0 = int(a * SR)
        end = min(len(out), s0 + n)
        out[s0:end] += (x * env[:, None])[:end - s0]
    return out


def duck_curve(vo, depth_db=-9.0, floor_db=-12.5):
    """Music gain over time: floor_db in the gaps, floor+depth under the voice."""
    from scipy.ndimage import uniform_filter1d, maximum_filter1d
    mono = np.abs(vo).mean(1)
    rms = np.sqrt(np.maximum(0.0, uniform_filter1d(mono ** 2, int(0.05 * SR))))
    active = (rms > 0.02).astype(np.float32)
    # hold through short gaps between words, then smooth attack/release
    active = maximum_filter1d(active, int(0.35 * SR)) > 0
    g_db = np.where(active, floor_db + depth_db, floor_db).astype(np.float32)
    a = np.exp(-1 / (0.12 * SR))
    sm = signal.lfilter([1 - a], [1, -a], g_db)
    return (10 ** (sm / 20)).astype(np.float32)


# ------------------------------------------------------------------ build

def build_mix(scenes, vo_path, kit_dir, out_wav, total, plan=None, music_floor_db=-12.5, music_duck_db=-9.0,
              sfx_gain=0.7, sfx_style="full"):
    """music_floor_db: the bed's level in the gaps; music_duck_db: how much further it
    dips under the narrator; sfx_gain: overall level of the sound design."""
    total = float(total)
    n = int(total * SR) + SR
    vo = load(vo_path)
    vo = vo / (np.max(np.abs(vo)) or 1) * 0.89
    voice = np.zeros((n, 2), np.float32)
    voice[:len(vo)] = vo[:n]

    music = music_bed(plan or [], kit_dir, total)[:n]
    g = duck_curve(voice, depth_db=music_duck_db, floor_db=music_floor_db)
    music *= g[:len(music), None]

    sfx = np.zeros((n, 2), np.float32)
    B = bank()
    for t, name, db, kw in spot(scenes, sfx_style):
        if name == "type":
            x = typewriter(kw.get("d", 0.8))
        elif name == "roll":
            x = counter_roll(kw.get("d", 1.2))
        elif name == "flaps":
            x = flaps(kw.get("d", 0.9))
        elif name == "drill":
            x = drill(kw.get("d", 2.0))
        else:
            x = B[name]
        x = x * (10 ** (db / 20))
        a = int(t * SR)
        if a >= n:
            continue
        e = min(n, a + len(x))
        pan = 0.5 + 0.15 * np.sin(t * 1.7)
        sfx[a:e, 0] += x[:e - a] * (1 - pan) * 1.4
        sfx[a:e, 1] += x[:e - a] * pan * 1.4
    # keep sound design under the narrator too, but less than the music
    sfx *= (0.55 + 0.45 * (g / g.max()))[:n, None]

    mix = voice + music + sfx * sfx_gain
    tmp = out_wav + ".raw.wav"
    save_wav(tmp, mix)
    # loudness to YouTube's reference with a true-peak ceiling
    r = subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", tmp, "-af",
                        "loudnorm=I=-14:TP=-1.2:LRA=11", "-ar", str(SR), "-c:a", "pcm_s24le", out_wav],
                       capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(r.stderr[-800:])
    os.remove(tmp)
    return out_wav


def mux(video, wav, out):
    r = subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", video, "-i", wav, "-map", "0:v", "-map", "1:a",
                        "-c:v", "copy", "-c:a", "aac", "-b:a", "256k", "-ar", "48000", "-movflags", "+faststart",
                        "-shortest", out], capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(r.stderr[-800:])
    return out
