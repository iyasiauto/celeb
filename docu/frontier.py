"""
frontier.py - write a shot list with a template imported from Frontier (docu/tools/frontier_import.py).

    import frontier
    F = frontier.Template("dossier")

    at(cue, F.g("alert", head="CODE RED", sub="U.S. EMBASSY", lines=["URGENT ALERT"], stamp="EVACUATE NOW", body="..."))
    at(cue, F.g("title_gold", name="MILES", sub="a 4chan user from Birmingham", img=photo_path))   # img = the ground
    at(cue, F.framed(clip(12)))                        # the footage in the template's frame (print, monitor, news ...)
    at(cue, clip(14, overlays=[F.over("stamp", at=0.4, text="2021", sub="Kabul")]))   # a graphic over footage

F.g() returns an ordinary Docu scene (type "<prefix>_<type>", e.g. "dossier_alert") with Frontier's own sound marks
under it (scene["sfx"], mixed by docu/mix.py), so a template's graphics sound the way they do in Frontier.
F.types lists what the template offers, F.example(type) the fields one graphic takes.
"""

import json
import os
import re

DOCU = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(DOCU)
TPL_DIR = os.environ.get("DOCU_TEMPLATES") or os.path.join(ROOT, "templates")


class Template:
    def __init__(self, tid):
        p = os.path.join(TPL_DIR, tid, "frontier.json")
        if not os.path.exists(p):
            raise SystemExit(f"{tid}: not a template imported from Frontier (no {p})")
        self.id = tid
        self.info = json.load(open(p, encoding="utf-8"))
        self.types = self.info["types"]
        self.kind = self.info["kind"]
        self.frame = self.info.get("frame")
        self.frame_every = int(self.info.get("frame_every") or 0)
        self._framed = 0

    def example(self, ty):
        return dict(self.types[ty]["example"])

    def seconds(self, ty):
        return float(self.types[ty]["seconds"])

    def marks(self, ty, sc):
        sc = dict(sc, type=ty)
        sc.setdefault("duration", self.seconds(ty))
        if self.kind == "kit":
            return [list(m) for m in kit_marks(self.info["kit"], sc)]
        if self.kind == "motion":
            n = len(sc.get("items") or [])
            return [[0.0, "whoosh", -6.0]] + [[round(0.8 + i * 0.45, 2), "pop", -10.0] for i in range(min(6, n))]
        return [list(m) for m in doc_marks(sc)]

    def g(self, ty, **fields):
        """a full-frame graphic of this template"""
        if ty not in self.types:
            raise KeyError(f"{self.id} has no graphic {ty!r} - it has: {', '.join(self.types)}")
        sc = dict(fields)
        if self.kind == "motion":
            sc = self._motion(ty, sc)
        sc["type"] = self.types[ty]["scene"]
        sc["sfx"] = self.marks(ty, fields)
        return sc

    # ------------------------------------------------------------ motion graphics (Frontier's original look)
    def _motion(self, ty, sc):
        """what Frontier's motion.py prepares in Python before its page draws: skin, variant, icons, ground"""
        i = getattr(self, "_mg", 0)
        self._mg = i + 1
        skins = self.info.get("skins") or ["paper"]
        prev = getattr(self, "_mg_prev", None)
        skin = sc.pop("skin", None) or skins[i % len(skins)]
        if prev == ty and len(skins) > 1:              # the same layout twice in a row: the other skin, another variant
            skin = skins[(i + 1) % len(skins)]
        self._mg_prev = ty
        items = [dict(it) for it in (sc.get("items") or []) if isinstance(it, dict)][:8]
        for it in items:
            it["label"] = str(it.get("label", ""))[:42]
            it["text"] = str(it.get("text", ""))[:90]
        out = dict(template=ty, skin=skin, title=str(sc.get("title", ""))[:110], subtitle=str(sc.get("subtitle", ""))[:130],
                   value=str(sc.get("value", ""))[:12], count=sc.get("count"), highlight=sc.get("highlight"), items=items,
                   image=sc.get("image") or sc.get("img") or "", groups=sc.get("groups") or [],
                   variant=(i + (1 if prev == ty else 0)) % 4, drift=(i % 5) * 1.1, seed=7 + i * 13, brand=self.info["style"],
                   intro=(i == 0))
        if self.info.get("ground"):
            out["ground"] = self.info["ground"]
        out["icons"] = self._icons(out)
        if sc.get("cutouts"):
            out["cutouts"], out["cut_ar"] = self._cutouts(sc["cutouts"])
        out["page"] = (self.info.get("pages") or {}).get(skin)
        for k, v in sc.items():
            if k not in out and k not in ("img", "cutouts"):
                out[k] = v
        return out

    def _icons(self, sc):
        icons = dict(self.info.get("icons") or {})
        want = {str(it["icon"]) for it in sc.get("items", []) if it.get("icon")}
        want |= {str(sc[k]) for k in ("icon", "center_icon") if sc.get(k)}
        fa = None
        for name in want - set(icons):
            if fa is None:
                p = os.path.join(ROOT, "media", "kit", "icons_fa.json")
                fa = json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {}
            q = re.sub(r"[^a-z0-9 ]+", " ", name.lower()).strip()
            al = (self.info.get("fa_aliases") or {})
            for cand in (q, q.replace(" ", "-"), al.get(q, ""), al.get(q.split()[-1] if q.split() else "", "")):
                if cand and cand in fa:
                    icons[name] = fa[cand]
                    break
            else:
                import difflib
                hit = difflib.get_close_matches(q.replace(" ", "-"), list(fa), n=1, cutoff=0.62)
                if hit:
                    icons[name] = fa[hit[0]]
        return icons

    def _cutouts(self, names):
        from PIL import Image
        d = os.path.join(ROOT, "media", "kit", "cutouts")
        paths, ars = [], []
        for n in names:
            p = n if os.path.isabs(str(n)) else os.path.join(d, str(n) if str(n).endswith(".png") else f"{n}.png")
            if os.path.exists(p):
                with Image.open(p) as im:
                    ars.append(im.width / max(1, im.height))
                paths.append(p)
        return paths, ars

    def over(self, ty, at=0.3, **fields):
        """the same graphic as an overlay on a clip or photo (transparent, no ground)"""
        o = dict(fields, type="frontier", page=self.types[ty]["page"], kind=ty, at=at)
        o["sfx"] = self.marks(ty, fields)
        return o

    def framed(self, scene, kind=None, text="", n=None):
        """footage in this template's frame (print, monitor, news, board, page, stage, paper, blurfill, crt, player);
        `text` is the line typed under a page / board / news frame (the words spoken over the shot)"""
        k = kind or self.frame
        if not k:
            return scene
        s = dict(scene, footage_frame=k, frame_n=self._framed if n is None else n)
        if text:
            s["frame_text"] = text
        self._framed += 1
        return s

    def every(self, scene, text=""):
        """frame every n-th footage shot, as the style does (frame_every in the template)"""
        self._count = getattr(self, "_count", 0) + 1
        if self.frame and self.frame_every and self._count % self.frame_every == 0:
            return self.framed(scene, text=text)
        return scene


# ---------------------------------------------------------------- Frontier's sound marks (kits.py / docgfx.py)
def kit_marks(kit: str, sc: dict) -> list:
    """[(second, sound, dB)] under this scene (sfx.py BANK names)."""
    t, d = sc.get("type"), float(sc.get("duration", 6.0))
    k = kit
    if k == "dossier":
        if t in ("alert", "dialogue", "stamp"):
            n = int(min(28, max(6, d * 5)))
            return [(0.0, "static", -14.0)] + [(0.25 + i * (min(3.2, d - 1.5) / n), "typekey", -13.0) for i in range(n)] + [(d - 0.6, "hit", -12.0)]
        if t == "crosshair":
            return [(0.0, "whoosh", -6.0), (1.1, "click", -6.0), (1.6, "ping", -12.0)]
        if t == "disclaimer":
            return [(0.0, "static", -9.0), (0.3, "hit", -8.0)]
        if t == "title_gold":
            return [(0.0, "riser", -8.0), (1.2, "hit", -3.0)]
        if t == "tracker":
            return [(0.0, "static", -12.0), (0.9, "click", -6.0), (1.8, "typekey", -12.0), (2.4, "click", -8.0)]
        if t == "stack":
            return [(0.0, "paper", -4.0), (1.3, "paper", -5.0), (2.6, "paper", -5.0), (3.4, "click", -9.0)]
    if k == "kinetic":
        if t == "bigword":
            return [(0.05, "hit", -5.0), (1.5, "hit", -6.0)]
        if t == "board":
            return [(0.0, "whoosh", -6.0), (0.4, "tap", -12.0)] + [(1.2 + i * 0.07, "typekey", -18.0) for i in range(18)]
        if t == "doodle":
            return [(0.1, "tap", -10.0), (0.5, "tap", -12.0), (0.9, "tap", -12.0), (1.3, "pop", -9.0)]
        if t == "phones":
            return [(0.2, "whoosh", -5.0), (1.2, "whoosh", -6.0), (2.2, "whoosh", -6.0), (3.4, "whoosh_out", -8.0)] + \
                   [(3.9 + i * 0.08, "typekey", -16.0) for i in range(16)]
        if t == "comment":
            return [(0.0, "whoosh", -7.0), (1.4, "click", -8.0), (2.4, "click", -8.0), (3.4, "click", -8.0)]
        if t == "scroll":
            return [(0.0, "whoosh", -6.0), (2.5, "whoosh", -9.0)]
        if t == "mosaic":
            return [(0.3, "pop", -6.0), (0.9, "pop", -6.0)]
        if t == "sources":
            return [(0.4 + i * 0.09, "typekey", -15.0) for i in range(24)]
    if k == "atlas":
        if t == "timemachine":
            return [(0.1, "pop", -13.0), (3.2, "boing", -16.0)]
        if t == "flipchart":
            n = max(1, len(sc.get("pages") or []) - 1)
            return [(0.9 + i * max(1.2, (d - 1.4) / n), "paper", -13.0) for i in range(n)]
        if t == "watch":
            return [(0.3, "click", -15.0), (1.4, "boing", -17.0)]
        if t == "stamp":
            return [(0.15 + i * 0.12, "pop", -10.0) for i in range(6)] + [(1.6, "boing", -10.0)]
        if t == "wave":
            return [(0.0, "whoosh", -7.0)]
        if t == "scoreboard":
            return [(0.2, "pop", -10.0), (0.5, "pop", -10.0), (1.0, "riser", -14.0), (3.0, "boing", -12.0)]
        if t == "signpost":
            return [(0.2, "boing", -10.0), (0.9, "pop", -11.0), (1.3, "pop", -11.0), (1.7, "pop", -11.0)]
    if k == "deep":
        if t == "stencil":
            return [(0.0, "ping", -8.0), (0.3, "hit", -9.0)]
        if t == "route":
            return [(0.0, "ping", -8.0), (1.2, "whoosh", -9.0), (3.5, "ping", -11.0)]
        if t == "cutaway":
            return [(0.0, "hum", -9.0), (1.4, "ping", -10.0), (2.8, "ping", -12.0)]
        if t == "sonar":
            return [(0.0, "ping", -6.0), (1.7, "ping", -6.0), (3.4, "ping", -6.0)]
        if t == "readout":
            return [(0.0, "static", -14.0)] + [(0.5 + i * 0.09, "typekey", -16.0) for i in range(22)]
        if t == "maproom":
            return [(0.0, "hum", -10.0), (2.2, "click", -9.0), (3.0, "whoosh", -9.0)]
    if k == "frontline":
        if t == "newsbar":
            return [(0.1, "whoosh", -12.0)]
        if t == "timeline":
            return [(0.6 + i * 0.5, "tap", -11.0) for i in range(min(5, len(sc.get("events") or [])))]
        if t == "label":
            return [(0.0, "click", -6.0), (0.2, "pop", -9.0)]
        if t == "arrows":
            return [(0.9, "whoosh", -11.0), (1.9, "whoosh", -12.0)]
        if t == "ticker":
            return [(0.0, "sting", -11.0)]
        if t == "count":
            return [(0.3, "riser", -13.0)]
    if k == "legend":
        if t == "chapter":
            return [(0.0, "whoosh", -6.0), (0.7, "hit", -9.0)]
        if t == "lower":
            return [(0.0, "whoosh", -9.0)]
        if t == "scorecard":
            return [(0.0, "paper", -5.0), (1.0, "tap", -8.0), (1.5, "tap", -8.0), (2.0, "tap", -8.0)]
        if t == "line":
            return [(0.0, "whoosh", -8.0)]
        if t == "years":
            return [(0.3 + i * 0.6, "tap", -8.0) for i in range(5)]
    if k == "hustle":
        if t == "bar":
            n = int(sc.get("value") or 6)
            return [(0.0, "whoosh", -6.0)] + [(0.9 + i * 0.12, "click", -9.0) for i in range(max(1, min(14, n)))]
        if t == "icon3d":
            return [(0.1, "whoosh", -5.0), (0.6, "pop", -5.0), (1.2, "pop", -7.0)]
        if t == "moneyrain":
            return [(0.0, "cash", -6.0), (1.2, "cash", -8.0)]
        if t == "corner":
            return [(0.1, "pop", -6.0), (0.5, "pop", -6.0)]
        if t == "counter":
            return [(0.2, "riser", -9.0), (2.2, "cash", -5.0)]
        if t == "versus":
            return [(0.2, "hit", -6.0), (1.0, "pop", -7.0), (1.4, "pop", -7.0), (1.8, "pop", -7.0)]
        if t == "checklist":
            return [(0.8 + i * 0.7, "pop", -6.0) for i in range(5)]
    if k == "tape":
        if t == "title":
            return [(0.3, "whoosh", -10.0), (1.2, "hit", -10.0)]
        if t == "player":
            return [(0.0, "whoosh", -8.0), (0.7, "click", -10.0)]
        if t == "subs":
            return [(0.2, "riser", -10.0), (2.5, "pop", -6.0)]
        if t == "post":
            return [(0.1, "pop", -6.0), (1.5, "click", -9.0), (2.6, "click", -9.0)]
        if t == "timeline":
            return [(0.2, "whoosh", -8.0)] + [(0.7 + i * 0.55, "tap", -7.0) for i in range(5)]
        if t == "quote":
            return [(0.0, "whoosh", -9.0), (0.4, "tap", -9.0)]
        if t == "versus":
            return [(0.1, "whoosh", -7.0), (0.3, "whoosh", -7.0), (0.9, "hit", -8.0)]
        if t == "chapter":
            return [(0.05, "hit", -7.0), (0.4, "whoosh", -9.0)]
    if k == "analog":
        if t == "machine":
            return [(0.05, "whoosh", -7.0), (0.35, "hit", -11.0)] + \
                   [(1.6 + i * 0.42, "typekey", -15.0) for i in range(min(5, len(sc.get("specs") or [])))]
        if t == "steps":
            return [(0.0, "whoosh", -11.0)] + _pattern_marks(sc)
        if t == "wave":
            lanes = (sc.get("lanes") or [{"sound": sc.get("sound") or "kick"}])[:2]
            return [(0.45 + j * 1.7, _DRUM.get(str(l.get("sound") or "kick").lower()[:4], ("bd808", 6.0))[0],
                     _DRUM.get(str(l.get("sound") or "kick").lower()[:4], ("bd808", 6.0))[1]) for j, l in enumerate(lanes)]
        if t == "record":
            return [(0.05, "whoosh", -8.0), (0.8, "whoosh", -13.0), (1.5, "crackle", -4.0)]
        if t == "price":
            n = len(sc.get("tags") or []) or 1
            gap = min(1.3, (d - 2.2) / max(1, n))
            out = [(0.2 + i * gap + 0.35, "paper", -6.0) for i in range(n)] + [(0.2 + i * gap + 0.95, "tap", -9.0) for i in range(n - 1)]
            if sc.get("stamp"):
                out.append((0.2 + (n - 1) * gap + 1.2, "hit", -6.0))
            return out
        if t == "units":
            a = min(d - 1.4, 3.6)
            return [(0.2, "riser", -12.0)] + [(0.5 + i * 0.22, "click", -14.0) for i in range(int((a - 0.6) / 0.22))] + \
                   ([(a + 0.05, "hit", -4.0)] if sc.get("stamp") else [])
        if t == "timeline":
            return [(0.1, "whoosh", -9.0)] + [(0.4 + i * 0.5, "paper", -9.0) for i in range(min(5, len(sc.get("events") or [])))]
        if t == "quote":
            return [(0.05, "whoosh", -9.0), (0.35, "paper", -6.0)]
        if t == "city":
            return [(0.0, "whoosh", -6.0), (0.35, "hit", -8.0)]
    return [(0.0, "whoosh", -6.0)]


# the ANALOG kit's drum voices: row name -> (sfx.BANK sound, dB relative to the channel's sfx level)
_DRUM = {"bd": ("bd808", 14.0), "kick": ("bd808", 14.0), "808": ("bd808", 14.0), "acou": ("kickac", 11.0),
         "sd": ("sd808", 10.0), "snar": ("sd808", 10.0), "cp": ("cp808", 9.0), "clap": ("cp808", 9.0),
         "ch": ("ch808", 6.0), "hat": ("ch808", 6.0), "oh": ("oh808", 6.0), "open": ("oh808", 6.0),
         "cb": ("cb808", 7.0), "cowb": ("cb808", 7.0), "rs": ("rs808", 6.0), "lt": ("tom808", 8.0), "mt": ("tom808", 8.0),
         "ht": ("tom808", 8.0), "cy": ("oh808", 5.0), "ma": ("rs808", 3.0), "cl": ("rs808", 5.0)}


def _pattern_marks(sc: dict) -> list:
    """The 16-step pattern the steps scene shows, as sounds on its playhead (the JS starts it at 1.0 s)."""
    rows = sc.get("rows") or {}
    if isinstance(rows, list):
        rows = {str(o.get("name") or o.get("k") or ""): str(o.get("steps") or o.get("v") or "") for o in rows if isinstance(o, dict)}
    try:
        bpm = max(60.0, min(180.0, float(sc.get("bpm") or 100)))
    except (TypeError, ValueError):
        bpm = 100.0
    step, t0, end = 60.0 / bpm / 4, 1.0, float(sc.get("duration", 7.0)) - 0.5
    pats = []
    for name, steps in list(rows.items())[:5]:
        hits = [c in "xX1*o" for c in re.sub(r"[\s|]", "", str(steps))][:32]
        voice = _DRUM.get(str(name).lower()[:2]) or _DRUM.get(str(name).lower()[:4])
        if hits and voice:
            pats.append((hits, voice))
    out, k = [], 0
    while t0 + k * step < end:
        for hits, (snd, gain) in pats:
            if hits[k % len(hits)]:
                out.append((round(t0 + k * step, 4), snd, gain))
        k += 1
    return out


def doc_marks(sc: dict) -> list:
    """[(second, sound, gain dB)] — where sfx.py puts its sounds under this graphic, from its own timing."""
    t, d = sc["type"], float(sc.get("duration", 6.0))
    if t == "number":
        return [(0.0, "whoosh", -3.0), (2.2, "hit", -5.0)]
    if t == "chart":
        return [(0.0, "whoosh", -3.0), (2.5, "hit", -9.0)]
    if t == "dateline":
        return [(0.0, "whoosh", -3.0), (0.95, "hit", -7.0)]
    if t == "question":
        return [(0.2, "riser", -6.0), (0.22, "hit", -4.0)]
    if t == "pivot":
        return [(0.0, "whoosh", -4.0), (0.35, "hit", -7.0)]
    if t == "card":
        return [(0.1, "whoosh", -5.0)] + [(round(0.95 + i * 0.45, 2), "tap", -8.0) for i in range(len(sc.get("highlight") or []))]
    if t == "step":
        return [(0.0, "whoosh", -4.0), (0.3, "hit", -8.0)]
    if t == "social":
        clicks = [1.05, 1.75] if sc.get("mutual") else [1.05]
        return [(0.05, "whoosh", -5.0)] + [(c, "tap", -5.0) for c in clicks] + [(clicks[-1] + 0.3, "hit", -9.0)]
    if t == "chapter":
        if sc.get("vhs"):
            return [(0.0, "tape", -7.0), (0.3 if not sc.get("episode") else 0.85, "hit", -3.0)]
        return [(0.0, "whoosh", -6.0), (0.25 if not sc.get("episode") else 0.8, "hit", -3.0)]
    if t == "place":
        return [(0.0, "whoosh", -4.0), (0.08, "hit", -6.0)]
    if t == "pull":
        return [(0.0, "paper", -6.0), (0.3, "hit", -10.0)]
    if t == "table":
        n = len(sc.get("rows") or [])
        return [(0.0, "whoosh", -4.0)] + [(round(0.5 + i * 0.22, 2), "tap", -8.0) for i in range(n)]
    if t == "timeline":
        n = len(sc.get("events") or [])
        step = (d - 2.6) / max(1, n - 1)
        return [(0.0, "whoosh", -3.0)] + [(round(0.45 + i * step, 2), "tap", -6.0) for i in range(n)]
    return [(0.0, "whoosh", -6.0)]
