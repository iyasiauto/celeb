"""
<VIDEO TITLE>
Faceless investigative documentary - edit decision list and build.

Copy this folder to projects/<your_video>/, fill data/, then work top to bottom:

    python build.py plan        check every cue against the voiceover, clip-length warnings
    python build.py prep        grade pictures, cut out subjects, make paper surfaces
    python build.py stills      one QA frame per scene   -> <work>/stills/
    python build.py stills s012 s013                     (only some scenes)
    python build.py render      render every scene (resumable, 4 workers; WORKERS=6 to change)
    python build.py render s012 re-render one scene after a fix
    python build.py mix         sound design + music + voiceover -> <work>/mix.wav
    python build.py final       join scenes + mux audio -> <out>/<name>.mp4
    python build.py all         everything in one go

A cue is the exact phrase of the script the cut lands on. Inside a scene, "@phrase" times
an element to that word. See docu/templates/README.md for every scene type and option.
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def _find_docu():
    """docu/ is found from $DOCU_DIR, or by walking up from this folder."""
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
from edl import *                # noqa: E402,F401,F403  (photo, clip, depth, spot, words, collage, ...)
from snippets import *           # noqa: E402,F401,F403  (tag, verdict, scales, scoreboard, gauge, ...)

ROOT = os.environ.get("VIDEO_ROOT", os.path.join(HERE, "media"))     # kit/, footage/, work/, out/
edl.setup(
    name="My_Video_Title",                          # file name of the final MP4
    kit=os.environ.get("VIDEO_KIT", f"{ROOT}/kit"),               # fonts, music, maps, cutouts
    footage=os.environ.get("VIDEO_FOOTAGE", f"{ROOT}/footage"),   # source_video/ + images/
    work=os.environ.get("VIDEO_WORK", f"{ROOT}/work"),            # vo.mp3 goes here; renders go here
    data=os.path.join(HERE, "data"),               # script.txt, words.json, catalog_all.json
    out=os.environ.get("VIDEO_OUT", f"{ROOT}/out"),
    image_dirs=[f"{ROOT}/footage/images/approved", f"{ROOT}/footage/images/candidates"],
    # the look: pick a theme and a grade that suit the topic (see README "Choosing a style")
    theme="paper",            # paper | forensic | expedition | broadcast (see starter_broadcast/)
    grade="doc",              # doc | cool | warmsepia | broadcast | bw | sepia | none
    grain=3.0,                # film grain strength, 0 = off
    # quiet music: the bed sits ~21 dB under the voice in gaps and ~31 dB under it while speaking
    music_floor_db=-21.0, music_duck_db=-10.0, sfx_gain=0.55,
)

# places (lon, lat) for map scenes
HOME = (0.0, 51.5)

# =================================================================== cold open
at(0.0, clip(0, zoom=1.03, overlays=[dict(type="fadein", d=1.0)]))
at("the second phrase of your script", photo("my_picture", move="in", focus=[0.5, 0.45], zoom=1.15,
                                            chip="A chip label", chip_at="@a word"))
at("a third phrase", words([W_("BIG WORDS.", y=440, at=0.0, size=150),
                            W_("ON CUE.", y=620, at="@on cue", size=150, color="#D9A441")], bg="my_picture"))

# =================================================================== part one
at("Part one begins here", chapter("01", "PART ONE", "THE TITLE", "my_picture"))
at("a phrase about a place", map_scene(
    stops=[dict(at=0, lon=10, lat=40, scale=900), dict(at="@a place", lon=HOME[0], lat=HOME[1], scale=6000, d=2.5)],
    pins=[map_pin(HOME, "A place", "@a place", sub="what happened here")]))
at("a phrase about a person", depth("portrait_picture", subject=[0.5, 0.45], hit=0.6,
                                   lower=("Person Name", "Who they are", "@a person")))
at("a phrase with evidence", board([
    pc("my_picture", 600, 520, 760, rot=-3, at=0.0),
    stamp("CLAIMED", 1350, 420, at="@evidence", rot=-7, size=110),
    strip("what the evidence says", 1350, 620, at=0.8, size=40)]))

# =================================================================== ending
at("your final line", board([
    title_("THE QUESTION?", 960, 380, at=0.1, size=150, underline=True),
    hand("to be continued", 960, 620, 0.6, size=62, w=1200, align="center")],
    overlays=[dict(type="fadeout", d=1.6)]))

# one music bed per act, crossfaded; `at` = the cue whose scene the new bed starts under
MUSIC = [
    dict(at=None, track="01_your_opening_track.mp3", db=0),
    dict(at="Part one begins here", track="02_your_second_track.mp3", db=-1, lead=-1.0),
]

if __name__ == "__main__":
    edl.main(MUSIC)
