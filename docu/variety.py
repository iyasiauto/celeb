"""
variety.py - so that no two videos look template-generated.

One seed per video (default: derived from the project name) picks a combination of:

  accent     the accent colour family (gold, copper, teal, sage, rose, slate, amber, ivory)
  fonts      heading / body / caption font pairing
  kicker     how chapter headings are numbered ("Chapter 3", "Part III", "03", "— 3 —", "Three")
  grade      picture grade (doc / cool / warm-doc) and grain amount
  xfade      dissolve length (0.45 - 0.8 s)
  moves      the Ken Burns move cycle used by ph() when a shot doesn't name its own move
  place      which corner the location caption sits in
  dim        how dark text cards darken their photo
  music      the order of music beds, never repeating the previous videos' openers

and it remembers which pictures and clips earlier videos used (assets_used.json per project), so
`fresh()` can hand out pictures nobody has seen yet and `plan` can warn about repeats.

Usage in a project's build.py:

    edl.setup(..., theme="documentary", vary="auto")      # or vary=1234 to pin a seed
    V = edl.V                                             # the picks, e.g. V["kicker"](3) -> "Part III"
"""

import glob
import hashlib
import json
import os
import random

ACCENTS = {
    "gold":   dict(gold="#D8B26E", mustard="#D8B26E", red="#B5523B", green="#8DAA7B", cyan="#7FA7B5"),
    "copper": dict(gold="#C98B5B", mustard="#C98B5B", red="#A9473A", green="#8FA886", cyan="#7C9DAE"),
    "teal":   dict(gold="#79B4B0", mustard="#79B4B0", red="#C0664F", green="#9CB77E", cyan="#79B4B0"),
    "sage":   dict(gold="#A7BE8C", mustard="#A7BE8C", red="#B8573F", green="#A7BE8C", cyan="#86A9B6"),
    "rose":   dict(gold="#D49A8C", mustard="#D49A8C", red="#B24A45", green="#93AD8A", cyan="#8AA5B8"),
    "slate":  dict(gold="#9DB3CF", mustard="#9DB3CF", red="#C06A55", green="#98B08A", cyan="#9DB3CF"),
    "amber":  dict(gold="#E0A64B", mustard="#E0A64B", red="#B8503A", green="#8FAE7D", cyan="#7FA3B3"),
    "ivory":  dict(gold="#E4D6B8", mustard="#E4D6B8", red="#B5523B", green="#9DB38C", cyan="#A2B6C0"),
}
# (heading serif, lower-third sans, caption italic) - all in the kit's fonts/
FONTSETS = [
    dict(DMSerif="PlayfairDisplay.ttf", Anton="PlayfairDisplay.ttf", Barlow="Inter-SemiBold.ttf", GaramondI="Lora-Italic.ttf", Elite="Lora.ttf"),
    dict(DMSerif="DMSerifDisplay.ttf", Anton="DMSerifDisplay.ttf", Barlow="BarlowCondensed-SemiBold.ttf", GaramondI="EB-Garamond-Italic.ttf", Elite="EB-Garamond.ttf"),
    dict(DMSerif="EB-Garamond.ttf", Anton="EB-Garamond.ttf", Barlow="Montserrat-ExtraBold.ttf", GaramondI="EB-Garamond-Italic.ttf", Elite="Lora.ttf"),
    dict(DMSerif="Lora.ttf", Anton="Lora.ttf", Barlow="Roboto-Condensed.ttf", GaramondI="Lora-Italic.ttf", Elite="Lora.ttf"),
    dict(DMSerif="PlayfairDisplay.ttf", Anton="PlayfairDisplay.ttf", Barlow="Poppins-SemiBold.ttf", GaramondI="EB-Garamond-Italic.ttf", Elite="EB-Garamond.ttf"),
]
ROMAN = ["", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII"]
WORDS = ["", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten", "Eleven", "Twelve"]
KICKERS = {
    "chapter": lambda n: f"Chapter {n}",
    "part_roman": lambda n: f"Part {ROMAN[n]}",
    "number": lambda n: f"{n:02d}",
    "dash": lambda n: f"— {n} —",
    "word": lambda n: f"Part {WORDS[n]}",
}
MOVES = [["in", "right", "in", "left", "up", "out"], ["in", "left", "out", "right", "in", "down"],
         ["right", "in", "left", "in", "push", "out"], ["in", "up", "in", "right", "out", "left"]]
GRADES = [("doc", 1.5), ("doc", 2.0), ("cool", 1.5), ("doc", 1.0)]
PLACES = [dict(x=96, y=930), dict(x=96, y=90), dict(x=1180, y=930)]


def seed_for(name):
    return int(hashlib.md5(name.encode()).hexdigest()[:8], 16)


def history(projects_root, exclude=None):
    """Every earlier project's picks and assets (from their assets_used.json)."""
    out = []
    for p in sorted(glob.glob(os.path.join(projects_root, "*", "data", "assets_used.json")), key=os.path.getmtime):  # oldest first
        if exclude and os.path.abspath(os.path.dirname(os.path.dirname(p))) == os.path.abspath(exclude):
            continue
        try:
            out.append(json.load(open(p)))
        except Exception:
            pass
    return out


def pick(seed, hist=(), tracks=()):
    """Choose this video's look. Avoids repeating the last video's accent, fonts and kicker."""
    r = random.Random(seed)
    last = hist[-1]["vary"] if hist and "vary" in hist[-1] else {}
    def choose(options, avoid):
        opts = [o for o in options if o != avoid] or list(options)
        return r.choice(opts)
    accent = choose(list(ACCENTS), last.get("accent"))
    fonts = choose(range(len(FONTSETS)), last.get("fonts"))
    kicker = choose(list(KICKERS), last.get("kicker"))
    grade, grain = r.choice(GRADES)
    used_openers = {h.get("vary", {}).get("music", [None])[0] for h in hist}
    music = list(tracks)
    r.shuffle(music)
    music.sort(key=lambda t: t in used_openers)          # a fresh opener first
    return dict(seed=seed, accent=accent, fonts=fonts, kicker=kicker, grade=grade, grain=grain,
                xfade=round(r.uniform(0.45, 0.8), 2), moves=r.choice(range(len(MOVES))),
                place=r.choice(range(len(PLACES))), dim=round(r.uniform(0.55, 0.68), 2), music=music)


def engine_overrides(v):
    """What the browser engine applies on top of the theme (CFG.vary)."""
    g = ACCENTS[v["accent"]]["gold"].lstrip("#")
    rgb = ",".join(str(int(g[i:i + 2], 16)) for i in (0, 2, 4))
    return dict(pal=ACCENTS[v["accent"]], fonts=FONTSETS[v["fonts"]], place=PLACES[v["place"]],
                map=dict(hi=rgb, rim=f"rgba({rgb},.25)"))


class Picks:
    """Convenient access in build.py: V.kicker(3), V.move(), V.accent, V['xfade'] ..."""
    def __init__(self, v, used_before):
        self.v = v
        self.used_before = used_before
        self._m = 0

    def __getitem__(self, k):
        return self.v[k]

    def kicker(self, n):
        return KICKERS[self.v["kicker"]](n)

    def move(self):
        seq = MOVES[self.v["moves"]]
        m = seq[self._m % len(seq)]
        self._m += 1
        return m

    @property
    def accent(self):
        return ACCENTS[self.v["accent"]]["gold"]

    def fresh(self, candidates, n=1, rng_seed=0):
        """Pick n of `candidates` (image keys or clip ids) that no earlier video used."""
        r = random.Random(self.v["seed"] + rng_seed)
        pool = [c for c in candidates if c not in self.used_before] or list(candidates)
        r.shuffle(pool)
        return pool[:n] if n > 1 else pool[0]


if __name__ == "__main__":
    # python variety.py <projects_root> ["Next_Video_Name"]  - the looks used so far, and the next one
    import sys
    root = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "projects")
    hist = history(root)
    for h in hist:
        v = h.get("vary", {})
        print(f"{h.get('name', '?')[:48]:48s} accent={v.get('accent')} fonts={v.get('fonts')} kicker={v.get('kicker')} "
              f"grade={v.get('grade')} xfade={v.get('xfade')}  images={len(h.get('images', []))} clips={len(h.get('clips', []))}")
    if len(sys.argv) > 2:
        v = pick(seed_for(sys.argv[2]), hist, ())
        print("next:", {k: v[k] for k in ("accent", "fonts", "kicker", "grade", "grain", "xfade", "moves", "place", "dim")},
              "| heading example:", KICKERS[v["kicker"]](3))
