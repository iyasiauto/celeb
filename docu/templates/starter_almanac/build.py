"""
<VIDEO TITLE> - heritage almanac style.

The skeleton of the sixth house style (see docu/templates/README.md, "Style F"), updated edition.
Full worked example: projects/amish_two_states/build.py ("Pennsylvania Has 95,000 Amish - So Why Does
Wisconsin Have MORE Settlements?"). The first edition (slab serif, barn red, quilt frames) is still there:
set theme="almanac_v1" and use the alm* scenes instead of the gz* ones.

  pace        slow: footage carries about half the video, photographs drift, soft 0.5 s dissolves;
              the video OPENS ON MOVING FOOTAGE (never a still), the title rises over a clip
  headings    gzhead - a notched "PLATE IV" stamp, a kicker, and an engraved-caps title whose
              letter-spacing closes in over the moving clip; hairlines open out; one per act
  captions    gztag - the place engraved on a slate cartouche with a pencil note slipped under it
  key points  gzcard (ledger slip: punched holes, double keyline, ochre band), gzstat (one stamped figure)
  figures     only for the numbers that carry the argument: gzversus (two things compared row by row),
              gzgiants (one circle sized by its value beside a field of dots), gzdivide (one cell
              dividing into many), gzindex (index rows with dotted leaders), gzdelta (2015 -> 2025 with
              the difference stamped), plus the almanac's paper charts in the same palette: almgrowth,
              almsplit, almdots, almshare, almbars, almdistrict
  maps        the plat map: township grid, square section markers, slate cartouche labels, inked routes
              with arrowheads, and dots that carry a size (one dot = 40 people, another = 44,765)
  palette     slate ink #1E2832, ochre #BE8A2C, oxblood #7A2F2A, verdigris #38655C, oatmeal paper #E8E2D0
  type        Cinzel (engraved headings), Playfair (didone figures), EB Garamond (body),
              Patrick Hand (the surveyor's pencil), Oswald (labels) - all OFL, shipped in the kit
  grade       "almanac2" - muted, cool ink, lifted blacks like a lithographic plate print (set for you)
  sound       soft only (paper, pen, a count roll) - no whooshes; music far under the voice

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

SP = os.environ.get("VIDEO_ROOT", os.path.join(HERE, "..", "..", "media"))
edl.setup(
    name="My_Video",
    kit=os.environ.get("VIDEO_KIT", f"{SP}/kit"),
    footage=os.environ.get("VIDEO_FOOTAGE", f"{SP}/my_niche/footage"),      # footage/source_video/<clips>
    work=os.environ.get("VIDEO_WORK", f"{SP}/work_my_video"),
    data=os.path.join(HERE, "data"),
    out=os.environ.get("VIDEO_OUT", f"{SP}/out"),
    image_dirs=[os.environ.get("VIDEO_IMAGES", f"{SP}/my_niche/images")],
    theme="almanac", grain=3.5, xfade=0.55,          # theme="almanac_v1" for the first edition
    music_floor_db=-21.0, music_duck_db=-10.0, sfx_gain=0.55, sfx_style="calm", vary="auto",
)

OCHRE, OXBLOOD, VERD, SLATE = "#BE8A2C", "#7A2F2A", "#38655C", "#2C4760"
BARN, FIELD, WHEAT, DENIM = OXBLOOD, VERD, OCHRE, SLATE      # the first edition's names still work

# ---------------------------------------------------------------- building blocks (copy freely)
_IDX = {c["video"].rsplit(".", 1)[0]: c["i"] for c in edl.CAT}
_MOVES = ["in", "left", "out", "right", "in", "up"]
_m = [0]


def C(name, then=(), **kw):
    """a footage clip by file name (or catalog index)"""
    kw.setdefault("zoom", 1.03)
    i = name if isinstance(name, int) else _IDX[name]
    return clip(i, then=tuple(t if isinstance(t, int) else _IDX[t] for t in then), **kw)


def P(name, move=None, zoom=1.08, focus=None, **kw):
    """a photograph with a slow drift (the move cycles unless named)"""
    if move is None:
        move = _MOVES[_m[0] % len(_MOVES)]
        _m[0] += 1
    return photo(name, move=move, zoom=zoom, focus=focus, **kw)


def _ov(scene, o):
    scene = dict(scene)
    scene["overlays"] = list(scene.get("overlays", [])) + [o]
    return scene


def head(scene, n, title, kicker=None, sub=None, at=0.5, **kw):
    """chapter heading over moving footage; n=None hides the badge (use for the title)"""
    o = dict(type="gzhead", n=n, title=title, kicker=kicker or f"Chapter {n}", at=at, **kw)
    if sub: o["sub"] = sub
    return _ov(scene, o)


def tag(scene, text, sub=None, at=0.6):
    o = dict(type="gztag", text=text, at=at)
    if sub: o["sub"] = sub
    return _ov(scene, o)


def card(*lines, bg, kicker=None, dim=0.62, **kw):
    """key point on a ledger slip; each line: text or (text, at, color, size, font)"""
    ls = []
    for ln in lines:
        ln = (ln,) if isinstance(ln, str) else ln
        d = dict(text=ln[0])
        for k, v in zip(("at", "color", "size", "font"), ln[1:]):
            if v is not None: d[k] = v
        ls.append(d)
    s = dict(type="gzcard", lines=ls, img=img(bg), dim=dim)
    if kicker: s["kicker"] = kicker
    s.update(kw)
    return s


def stat(value, kicker, note, bg, **kw):
    """one big number counting up (count=False for text like '7-9')"""
    return dict(type="gzstat", value=value, kicker=kicker, note=note, img=img(bg), **kw)


def pin(label, lon, lat, at, sub=None, side="right", **kw):
    p = dict(label=label, lon=lon, lat=lat, at=at, side=side, **kw)
    if sub: p["sub"] = sub
    return p


def amap(stops, title=None, **kw):
    s = dict(type="map", detail="geo_hi.json", adminCountries=["USA"], stops=stops, **kw)
    if title: s["title"] = title
    return s


# =================================================================== the edit
# Cues are the first words of the narration where the shot starts; "@words" inside a scene times an
# element to the moment those words are spoken.

at(0.0, _ov(tag(C("opening_clip"), "A place, a state", "a road · a year", at="@place name"), dict(type="fadein", d=1.6)))
at("The sentence where the title should rise", head(C("a_moving_shot"), None, "The Title", kicker="A documentary", size=118))
at("First words of chapter one", head(C("an_aerial_clip"), 1, "Chapter Title", sub="a quiet subtitle"))
at("A sentence with one key number", stat("$25,000", "What the number measures", "one line of context", "a_photo",
                                          at="@the number itself"))
at("A sentence that is the turn of the story", card(("First half of the point", 0.3), ("the payoff line.", "@payoff words", WHEAT, 90),
                                                    bg="a_photo", kicker="The real reason"))
at("Two things that need comparing", dict(
    type="gzversus", title="A against B", note="what the figures are",
    left=dict(name="The first", sub="what it is", color=OXBLOOD), right=dict(name="The second", sub="what it is", color=VERD),
    rows=[dict(label="People", left="95,410", right="27,535", at="@the first pair of numbers", win="l", mark="three times as many"),
          dict(label="Places", left=63, right=68, at="@the second pair", win="r", mark="five more")],
    verdict="what the table proves", verdictAt="@the sentence that sums it up"))
at("One giant beside many small ones", dict(
    type="gzgiants", title="One is not like the others",
    giant=dict(value="44,765", label="The giant", sub="a single one", unit="people", at=0.6, r=206),
    field=dict(n=68, label="All the rest", sub="68 of them", at="@the moment the many appear", fill=2.4)))
at("Something that keeps dividing", dict(
    type="gzdivide", title="How one becomes ten", frameLabel="one settlement", note="what each cell is",
    steps=[dict(n=1, label="One", at=0.9), dict(n=2, label="One becomes two", at="@two"),
           dict(n=3, label="Two become three", at="@three"), dict(n=10, label="Three become ten", at="@ten")]))
at("A list with figures", dict(
    type="gzindex", title="The list", note="what it ranks",
    rows=[dict(label="First", value=74, at=0.8, hi=True), dict(label="Second", value=68, at="@the second name"),
          dict(label="Third", value=64, at="@the third name", sub="a note under the name")],
    foot="the line that lands the point", footAt="@the closing words"))
at("What a decade did", dict(
    type="gzdelta", title="2015 to 2025", **{"from": "2015", "to": "2025"},
    items=[dict(label="Settlements", **{"from": 54, "to": 63}, delta="+9", at=0.9, note="a net gain of nine", color=OXBLOOD),
           dict(label="Districts", **{"from": 465, "to": 636}, delta="+171", at="@the second measure", note="much bigger inside", color=VERD)],
    foot="what the two columns mean together", footAt="@the conclusion"))
at("Numbers that grow over time", dict(
    type="almgrowth", title="What grew", note="how fast", source="Source",
    points=[dict(x=1920, y=5000, label="5,000", sub="then", at=0.8),
            dict(x=2000, y=165000, label="165,000", sub="2000", at="@words for 2000"),
            dict(x=2024, y=400000, label="400,000", sub="today", at="@words for today", dx=-240, dy=-50)],
    ticks=[1920, 1960, 2000, 2024], xmax=2030, ymax=460000,
    grid=[dict(y=200000, label="200,000"), dict(y=400000, label="400,000")]))
at("A whole divided into equal parts", dict(
    type="almsplit", title="One farm, five sons", note="an 80-acre farm", label="80 acres", n=5, each="16 acres",
    who="son {n}", splitAt="@words for the split", verdict="the conclusion", verdictAt="@words for the conclusion"))
at("Doubling generations", dict(
    type="almdots", title="Doubling", rows=[dict(label="Today", value="10,000", n=10, at=0.6),
                                            dict(label="Next", value="20,000", n=20, at="@twenty thousand")]))
at("A share of a whole", dict(
    type="almshare", title="How they earn a living", parts=[
        dict(frac=0.31, big="< 1/3", label="Farming", color=FIELD, at="@one-third"),
        dict(frac=0.69, big="> 2/3", label="Trades", color=DENIM, at="@two-thirds")]))
at("Prices that climbed", dict(
    type="almbars", title="Price per acre", bars=[dict(label="once", value=3000, text="$3,000", at=0.8),
                                                  dict(label="now", value=25000, text="$25,000", at="@twenty-five", color=BARN)]))
at("A group and its leaders", dict(
    type="almdistrict", title="One church district", houses=30, centre="Church district", centreSub="25-35 families",
    roles=[dict(text="1 bishop", at="@bishop"), dict(text="2 ministers", at="@ministers"), dict(text="1 deacon", at="@deacon")]))
at("A move across the map", amap(
    [dict(at=0, lon=-77.3, lat=41.3, scale=5600), dict(at="@the destination", lon=-76.6, lat=42.5, scale=5000, d=2.5)],
    title="North to New York",
    pins=[pin("From here", -76.30, 40.04, 0.5, "the origin", color=FIELD), pin("To here", -75.1, 44.5, "@the destination")],
    routes=[dict(from_=[-76.30, 40.04], to=[-75.1, 44.5], at="@the destination", d=1.6, arrow=True, width=4)],
    highlight=[dict(id="USA-3559", at="@the destination", fill="rgba(94,122,68,.22)")]))
at("The closing question", _ov(card(("The question?", "@the question", None, 62), ("Tell us in the comments.", "@comments", None, 36, "BaskI"),
                                    bg="a_photo", kicker="Your turn"), dict(type="fadeout", d=3.0)))

edl.main(music=[dict(at=None, track="02_Leaving_Home_Somber_Long_Bed.mp3"),
                dict(at="First words of chapter one", track="Mark Jubel - Efteraar.mp3", lead=-1.0)])
