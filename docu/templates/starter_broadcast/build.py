"""
<VIDEO TITLE> - breaking-news broadcast style.

The skeleton of the fourth house style (see docu/templates/README.md, "Style D"):

  cold open   a live bulletin - LIVE bug + crawling ticker on every scene, a BREAKING NEWS slab,
              the key moment as a news graphic (here: a borehole where the bit shatters)
  segments    numbered bumpers (01, 02, ...) - one per act, a new music bed under each
  analysis    fact-check meters, the OBSERVED | CLAIMED board, the headline wall that collapses
              into its one source, numbered status rows, broadcast lower thirds on footage
  ending      back to the bulletin as a "DEVELOPING" story, then a quiet last line

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
from snippets import *           # noqa: E402,F401,F403  (breaking, segment, live, ticker, bug, factcheck, ...)

ROOT = os.environ.get("VIDEO_ROOT", os.path.join(HERE, "media"))
edl.setup(
    name="My_Breaking_News_Video",
    kit=os.environ.get("VIDEO_KIT", f"{ROOT}/kit"),
    footage=os.environ.get("VIDEO_FOOTAGE", f"{ROOT}/footage"),
    work=os.environ.get("VIDEO_WORK", f"{ROOT}/work"),
    data=os.path.join(HERE, "data"),
    out=os.environ.get("VIDEO_OUT", f"{ROOT}/out"),
    image_dirs=[f"{ROOT}/footage/images/approved", f"{ROOT}/footage/images/candidates"],
    theme="broadcast", grade="broadcast", grain=1.5,
    music_floor_db=-21.0, music_duck_db=-10.0, sfx_gain=0.55,
)

RED, YEL, GREEN = "#E10600", "#FFC21A", "#18C07A"
PLACE = (44.23, 39.44)                       # (lon, lat) of the story

# the two tickers: the breaking bulletin, and the developing story at the end
TICK = ticker(["First line of the news crawl", "Second line", "Third line — what is not yet known"], label="BREAKING", clock="DATE")
TICK_END = ticker(["What happens next", "When results are expected", "What is still unverified"], label="DEVELOPING", clock="NEXT")
LIVE = bug(place="Place · Country")

# =================================================================== cold open: the bulletin
at(0.0, live(clip(0, zoom=1.04, overlays=[dict(type="fadein", d=0.8)]), TICK, LIVE, intro=0.6))
at("the moment it happened", live(borehole(title="WHERE IT HAPPENED", kicker="THE KEY MOMENT", bot=940,
                                           layers=[layer(0, 0.6, "soil"), layer(0.6, 2.0, "sediment"), layer(2.0, 2.7, "organic"),
                                                   layer(2.7, 4.4, "sediment"), layer(4.4, 6, "hard")],
                                           beats=dict(draw=0.1, drill=0.7, hit="@the word it hits on")), TICK, LIVE))
at("the headline sentence", live(breaking("THE HEADLINE OF THE STORY", "Where · when", bg="my_picture", at=0.05), TICK, LIVE))
at("what the headlines didn't tell you", words([W_("WHAT THE HEADLINES", y=440, at=0.0, size=120),
                                                W_("DIDN'T TELL YOU", y=610, at=0.6, size=130, color=RED)], ground="dark"))

# =================================================================== 01
at("let's start with what we can verify", segment("01", "WHAT WE CAN VERIFY", "The facts first", bg="my_picture"))
at("a phrase about a person", news_lower(photo("portrait_picture", move="in", zoom=1.1), "WHO", "PERSON NAME", "their role", at=0.4))
at("a phrase with a claim", factcheck("“The claim, quoted exactly.”", "— who said it, when", "UNVERIFIED", "@not verified"))
at("a list of facts", newslist("WHAT HAPPENED", [nrow("First fact", 0.2, "CONFIRMED", GREEN),
                                                 nrow("Second fact", "@second", "PER THE TEAM", YEL)], y0=300))

# =================================================================== 02
at("now the other side", segment("02", "THE OTHER SIDE", "What the published science says"))
at("side by side", news_board([dict(side=0, text="An observation", tag="measured by", at=0.2),
                               dict(side=1, text="The claim built on it", at="@the claim")], gap_at="@never touch"))
at("every article traces back", echo([f"A headline repeating it ({i})" for i in range(1, 9)],
                                     [dict(title="1 PRESS RELEASE", sub="who wrote it")], "@traces back"))

# =================================================================== ending: developing story
at("so what is the honest answer", live(newslist("THE HONEST ANSWER", [nrow("What happened", 0.2, "CONFIRMED", GREEN),
                                                                        nrow("What it means", "@means", "NOT YET", RED)], y0=320),
                                        TICK_END, LIVE, intro=0.3))
at("the last line", words([W_("IT'S THE TRUTH.", y=540, at=0.1, size=170)], ground="dark", overlays=[dict(type="fadeout", d=1.6)]))

MUSIC = [
    dict(at=None, track="01_your_tension_bed.mp3", db=-1),
    dict(at="let's start with what we can verify", track="02_your_investigation_bed.mp3", db=-1, lead=-1.0),
]

if __name__ == "__main__":
    edl.main(MUSIC)
