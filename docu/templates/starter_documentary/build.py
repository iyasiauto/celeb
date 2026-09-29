"""
<VIDEO TITLE> - calm documentary style.

The skeleton of the fifth house style (see docu/templates/README.md, "Style E"):

  pace        long shots (5-10 s), slow camera moves, soft dissolves between every shot
  headings    "Chapter n" serif title cards, one per act, a new quiet music bed under each
  captions    a location caption with a thin gold rule; calm name lower thirds
  graphics    text cards, gentle bar charts, a household ledger that grows one line per chapter,
              a household-size chart, simple maps, a few depth pops and spotlights
  sound       soft only (paper, pen, ticks) - no whooshes, stamps or impacts; music far under the voice

Copy this folder to projects/<your_video>/, fill data/ (see data/README.txt), and run:

    python build.py plan | prep | stills [ids] | render [ids] | mix | final | all
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def _find_docu():
    if os.environ.get("DOCU_DIR"):
        return os.environ["DOCU_DIR"]
    d = HERE
    for _ in range(6):
        for cand in (os.path.join(d, "docu"), d):
            if os.path.isfile(os.path.join(cand, "engine.js")):
                return cand
        d = os.path.dirname(d)
    raise SystemExit("docu/ engine not found - set DOCU_DIR=/path/to/docu")


DOCU = _find_docu()
sys.path[:0] = [DOCU, os.path.join(DOCU, "templates")]

import edl                       # noqa: E402
from edl import *                # noqa: E402,F401,F403
from snippets import *           # noqa: E402,F401,F403  (doctitle, textcard, doc_bars, ledger_list, place_cap, ...)

ROOT = os.environ.get("VIDEO_ROOT", os.path.join(HERE, "media"))
edl.setup(
    name="My_Documentary",
    kit=os.environ.get("VIDEO_KIT", f"{ROOT}/kit"),
    footage=os.environ.get("VIDEO_FOOTAGE", f"{ROOT}/footage"),
    work=os.environ.get("VIDEO_WORK", f"{ROOT}/work"),
    data=os.path.join(HERE, "data"),
    out=os.environ.get("VIDEO_OUT", f"{ROOT}/out"),
    image_dirs=[f"{ROOT}/footage/images/approved", f"{ROOT}/footage/images/candidates"],
    theme="documentary", grade="doc", grain=1.5,
    music_floor_db=-21.0, music_duck_db=-10.0, sfx_gain=0.55,
    xfade=0.6,              # soft dissolves between every shot
    sfx_style="calm",       # paper, pen and ticks only
)

GOLD = "#D8B26E"
TOWN = (-74.17, 41.34)      # (lon, lat)

# the recurring device: a ledger that grows one line per chapter
LINES = [("1  First layer", "value"), ("2  Second layer", "value"), ("3  Third layer", "value")]


def ledger(n, new_at=0.8):
    items = [dict(label=l, value=v, at=(-3 if i < n - 1 else new_at), **({"color": GOLD} if i == n - 1 else {}))
             for i, (l, v) in enumerate(LINES[:n])]
    return ledger_list("The ledger", items, bg="a_picture")


# =================================================================== cold open
at(0.0, place_cap(photo("aerial_picture", move="in", zoom=1.12, overlays=[dict(type="fadein", d=1.2)]),
                  "A place, A state", "one line about it", at=1.0))
at("a striking number", stat("15.7", "A KICKER", "what the number means", bg="a_picture"))
at("the question", textcard(("The question everybody asks —", 0.2), ("in gold.", 0.9, GOLD, 84), bg="a_picture"))
at("a phrase over footage", clip(0, zoom=1.03))

# =================================================================== chapter 1
at("chapter one begins", doctitle(1, "The Numbers", "a_picture", sub="a quiet sub line"))
at("a place on the map", dict(type="map", detail="geo_hi.json", adminCountries=["USA"],
    stops=[dict(at=0, lon=-75.5, lat=41.2, scale=5200), dict(at=0.4, lon=-74.1, lat=41.0, scale=17000, d=3.0)],
    pins=[dict(lon=TOWN[0], lat=TOWN[1], label="The town", sub="its county", at=1.4, side="left")]))
at("a comparison", doc_bars("A calm comparison", [("First", 50, "≈ $50,000", "@first"), ("Second", 98, "≈ $98,000", "@second")],
                            bg="a_picture", max=100, source="Source: name it"))
at("a person", doc_lower(photo("portrait", move="in"), "A Name", "who they are"))
at("the first layer", ledger(1))

# =================================================================== chapter 2
at("chapter two begins", doctitle(2, "The Mechanism", "a_picture"))
at("eligibility rises with size", sizechart("The same income, a bigger family", 3.3, bg="a_picture",
                                            note="illustrative", incomeLabel="one fixed income"))
at("the second layer", ledger(2))

# =================================================================== ending
at("the last line", textcard(("A last, quiet line.", 0.3), bg="a_picture", overlays=[dict(type="fadeout", d=2.0)]))

MUSIC = [dict(at=None, track="01_quiet_bed.mp3", db=-1),
         dict(at="chapter one begins", track="02_quiet_bed.mp3", db=0, lead=-1.0)]

if __name__ == "__main__":
    edl.main(MUSIC)
