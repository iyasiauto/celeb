"""
Pennsylvania Has 95,000 Amish — So Why Does Wisconsin Have MORE Amish Settlements?
(settlements against church districts: Lancaster's giants and Wisconsin's dots)

Look: the HERITAGE ALMANAC, updated edition (docu/scenes_almanac2.js, theme "almanac") - a county
atlas and land-survey gazetteer. Engraved caps on a letterpress plate laid over moving footage,
didone figures, ledger-slip key points, a surveyor's pencil for the notes, and a plat map with a
township grid and square section markers. Slate ink on oatmeal paper: ochre, oxblood, verdigris.
Its own scenes carry the argument: a state-against-state table (gzversus), one giant circle beside a
field of dots (gzgiants), a district dividing into ten (gzdivide), index pages (gzindex) and a decade
of change (gzdelta), with the almanac's paper charts (growth line, split field, share bar, columns,
church district) in the new palette.

Slow and calm: footage carries the video, photographs drift, graphics only on the numbers that
matter, soft dissolves, paper-and-pencil sound only.

Footage: the Amish pool (media/amish/src - free stock from Pexels and Pixabay, no watermarks, no
talking heads). data/sources.json lists every file with its page and licence.

    python build.py plan | prep | stills [ids] | render [ids] | mix | final | all
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "docu"))

import edl                       # noqa: E402
from edl import *                # noqa: E402,F401,F403

SP = os.environ.get("VIDEO_ROOT", os.path.join(HERE, "..", "..", "media"))
AM = f"{SP}/amish"
edl.setup(
    name="Pennsylvania_Has_95000_Amish_So_Why_Does_Wisconsin_Have_MORE_Settlements",
    kit=os.environ.get("VIDEO_KIT", f"{SP}/kit"),
    footage=os.environ.get("VIDEO_FOOTAGE", f"{AM}/footage"),
    work=os.environ.get("VIDEO_WORK", f"{SP}/work8"),
    data=os.path.join(HERE, "data"),
    out=os.environ.get("VIDEO_OUT", f"{SP}/out"),
    image_dirs=[os.environ.get("VIDEO_IMAGES", f"{AM}/src/images")],
    theme="almanac", grain=3.5, xfade=0.55,
    music_floor_db=-21.0, music_duck_db=-10.0, sfx_gain=0.55,
    sfx_style="calm", vary="auto",
)

OCHRE, OXBLOOD, VERD, SLATE, INK = "#BE8A2C", "#7A2F2A", "#38655C", "#2C4760", "#1E2832"
PA, WI, OH, NY, KY, MO, IN, IA, MN = ("USA-3560", "USA-3553", "USA-3550", "USA-3559", "USA-3548",
                                      "USA-3531", "USA-3547", "USA-3529", "USA-3514")
LANC, YORK, SPRINGRUN = (-76.30, 40.04), (-76.73, 39.96), (-77.76, 40.17)
MIFFLIN, INDIANA_CO = (-77.62, 40.61), (-79.09, 40.65)
CASHTON, KINGSTON, AUGUSTA = (-90.78, 43.74), (-89.12, 43.66), (-91.12, 44.68)
HILLSBORO, WILTON, ATHENS = (-90.34, 43.65), (-90.52, 43.81), (-90.08, 44.98)
ADAMS, CAMPDOUGLAS, WARRENS = (-89.77, 43.95), (-90.27, 43.92), (-90.50, 44.13)

# ---------------------------------------------------------------- building blocks
MISSING = []
_IDX = {c["video"].rsplit(".", 1)[0]: c["i"] for c in edl.CAT}
_MOVES = ["in", "left", "out", "right", "in", "up"]
_m = [0]


def C(name, then=(), **kw):
    """a footage clip by its file name (data/catalog_all.json is made from media/amish/src/clips)"""
    kw.setdefault("zoom", 1.03)
    if os.environ.get("LOOSE") and name not in _IDX:
        MISSING.append(name)
        name, then = next(iter(_IDX)), ()
    return clip(_IDX[name], then=tuple(_IDX[t] for t in then), **kw)


def P(name, move=None, zoom=1.08, focus=None, **kw):
    """a photograph with a slow drift"""
    if move is None:
        move = _MOVES[_m[0] % len(_MOVES)]
        _m[0] += 1
    return photo(name, move=move, zoom=zoom, focus=focus, **kw)


def _ov(scene, o):
    scene = dict(scene)
    scene["overlays"] = list(scene.get("overlays", [])) + [o]
    return scene


def head(scene, n, title, kicker=None, sub=None, at=0.5, **kw):
    """chapter heading stamped over moving footage"""
    o = dict(type="gzhead", n=n, title=title, at=at,
             kicker=kicker or f"Chapter {['', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten', 'eleven'][n]}", **kw)
    if sub:
        o["sub"] = sub
    return _ov(scene, o)


def tag(scene, text, sub=None, at=0.6, **kw):
    o = dict(type="gztag", text=text, at=at, **kw)
    if sub:
        o["sub"] = sub
    return _ov(scene, o)


def card(*lines, bg, kicker=None, dim=0.6, **kw):
    """a key point on a ledger slip; each line: text or (text, at, color, size, font)"""
    ls = []
    for ln in lines:
        if isinstance(ln, str):
            ln = (ln,)
        d = dict(text=ln[0])
        for k, v in zip(("at", "color", "size", "font"), ln[1:]):
            if v is not None:
                d[k] = v
        ls.append(d)
    s = dict(type="gzcard", lines=ls, img=img(bg), dim=dim)
    if kicker:
        s["kicker"] = kicker
    s.update(kw)
    return s


def stat(value, kicker, note, bg, unit=None, **kw):
    s = dict(type="gzstat", value=value, kicker=kicker, note=note, img=img(bg), **kw)
    if unit:
        s["unit"] = unit
    return s


def vs(title, left, right, rows, **kw):
    """left/right = (name, sub[, colour]); row = (label, left, right, at[, "l"|"r"][, mark])"""
    def side(x):
        d = dict(name=x[0])
        if len(x) > 1 and x[1]:
            d["sub"] = x[1]
        d["color"] = x[2] if len(x) > 2 and x[2] else None
        return {k: v for k, v in d.items() if v is not None}
    rs = []
    for r in rows:
        d = dict(label=r[0], left=r[1], right=r[2], at=r[3])
        if len(r) > 4 and r[4]:
            d["win"] = r[4]
        if len(r) > 5 and r[5]:
            d["mark"] = r[5]
        rs.append(d)
    return dict(type="gzversus", title=title, left=side(left), right=side(right), rows=rs, **kw)


def giants(title, giant, field, **kw):
    return dict(type="gzgiants", title=title, giant=giant, field=field, **kw)


def divide(title, steps, **kw):
    return dict(type="gzdivide", title=title, steps=[dict(n=s[0], label=s[1], at=s[2]) for s in steps], **kw)


def indexp(title, rows, **kw):
    """row = (label, value, at[, sub][, hi][, count])"""
    rs = []
    for r in rows:
        d = dict(label=r[0], value=r[1], at=r[2])
        if len(r) > 3 and r[3]:
            d["sub"] = r[3]
        if len(r) > 4 and r[4]:
            d["hi"] = True
        if len(r) > 5 and r[5] is False:
            d["count"] = False
        rs.append(d)
    return dict(type="gzindex", title=title, rows=rs, **kw)


def delta(title, items, **kw):
    return dict(type="gzdelta", title=title, items=items, **kw)


def fadein(scene, d=1.6):
    return _ov(scene, dict(type="fadein", d=d))


def fadeout(scene, d=2.5):
    return _ov(scene, dict(type="fadeout", d=d))


def pin(label, lonlat, at, sub=None, side="right", **kw):
    p = dict(label=label, lon=lonlat[0], lat=lonlat[1], at=at, side=side, **kw)
    if sub:
        p["sub"] = sub
    return p


def dot(lonlat, at, r=7, color=None, label=None, **kw):
    d = dict(lon=lonlat[0], lat=lonlat[1], at=at, r=r, **kw)
    if color:
        d["color"] = color
    if label:
        d["label"] = label
    return d


def amap(stops, title=None, **kw):
    s = dict(type="map", detail="geo_hi.json", adminCountries=["USA"], stops=stops, **kw)
    if title:
        s["title"] = title
    return s


def scatter(centre, n, at, spread=1.1, r=6, color=VERD, step=0.05, seed=3):
    """a field of settlement dots around a point, appearing one after another off one cue"""
    out, s = [], seed
    for i in range(n):
        s = (s * 1103515245 + 12345) % 2147483648
        dx = (s / 2147483648 - 0.5) * 2 * spread * 1.45
        s = (s * 1103515245 + 12345) % 2147483648
        dy = (s / 2147483648 - 0.5) * 2 * spread
        out.append(dot((centre[0] + dx, centre[1] + dy), at, r=r, color=color, wait=round(i * step, 2)))
    return out


# =================================================================== cold open
at(0.0, fadein(tag(C("px29461443"), "Lancaster County, Pennsylvania", "the oldest Amish settlement in America",
                   at="@center of Amish life")))
at("And the numbers seem to prove them right", C("px34208179"))
at("Pennsylvania had an estimated", stat("95,410", "Pennsylvania · Amish residents, 2025", "the state everyone pictures first",
                                         "pe29051618", unit="people", at="@an estimated", countFor=1.8, color=OXBLOOD))
at("Wisconsin had only", stat("27,535", "Wisconsin · Amish residents, 2025", "barely more than a quarter as many",
                              "wisconsin_farmland__pe33851721", unit="people", at="@Wisconsin had only", countFor=1.6, color=VERD))
at("So Pennsylvania has well over", C("px4617441"))
at("But now look at the map in a different way", amap(
    [dict(at=0, lon=-83.0, lat=41.6, scale=3600), dict(at=2.2, lon=-83.6, lat=41.8, scale=4300, d=2.0)],
    highlight=[dict(id=PA, at="@Pennsylvania has 63"), dict(id=WI, at="@Wisconsin has 68", fill="rgba(56,101,92,.28)")],
    names=[dict(text="Pennsylvania", lon=-77.6, lat=40.9, at="@Pennsylvania has 63", font="Engr", size=32, color=INK),
           dict(text="Wisconsin", lon=-89.9, lat=44.4, at="@Wisconsin has 68", font="Engr", size=32, color=INK)]))
at("Wisconsin actually has more separate", vs(
    "Settlements, not people", ("Pennsylvania", "95,410 Amish", OXBLOOD), ("Wisconsin", "27,535 Amish", VERD),
    [("Amish settlements", 63, 68, "@Wisconsin actually has", "r", "five more")],
    note="2025 estimates", verdict="fewer people, more communities", verdictAt="@in the American imagination"))
at("And that is not even the strangest part", C("px12484254"))
at("One Amish settlement around Lancaster County", stat(
    "44,765", "the Lancaster County settlement", "one geographic community", "pe34471682",
    unit="people", at="@contains roughly", countFor=2.0, color=OXBLOOD))
at("That single settlement is larger than", giants(
    "One settlement against a whole state",
    dict(value="44,765", label="Lancaster County, Pennsylvania", sub="a single settlement", at=0.4, r=206),
    dict(n=68, label="All of Wisconsin", sub="68 settlements · 27,535 people", at="@Yet Wisconsin still has", fill=2.4),
    source="Young Center for Anabaptist and Pietist Studies"))
at("So what exactly are we counting", C("px19675231"))
at("spread themselves across", P("pe12001572", move="right"))
at("The answer is not that Wisconsin somehow", C("px37919911"))
at("It is that these two states represent", P("pe29137946", move="in"))
at("Pennsylvania built giants", card(
    ("Pennsylvania built giants.", "@Pennsylvania built giants", OXBLOOD),
    ("Wisconsin built dots.", "@Wisconsin built dots", VERD),
    bg="pe32320447", kicker="two ways to grow", dim=0.66))
at("And once you understand why", C("px2570204"))

# =================================================================== I · what a settlement is
at("The first thing to understand", head(C("px4617021"), 1, "What a settlement is",
                                         sub="not a town, not a boundary — a geographic community", at=0.6))
at("It does not necessarily have a mayor", P("pe9552899", move="up"))
at("It may not have a sign", P("pe23339815", move="in"))
at("It may cross county lines", C("px34066758"))
at("And sometimes an English-speaking neighbor", C("px18333476"))
at("might not even realize that researchers", P("pe446341", move="left", zoom=1.1))
at("Researchers at the Young Center", card(
    ("A settlement is a geographic", "@define a settlement", None, 54),
    ("Amish community containing", "@as a geographic", None, 54),
    ("one or more church districts.", "@containing one or more", OXBLOOD, 54),
    bg="pe34391784", kicker="the definition", dim=0.68))
at("And the church district is the more important", C("px19655182"))
at("An Amish church district generally contains", stat(
    "20 to 40", "one church district", "no building — worship moves from home to home", "pi287407",
    unit="households", count=False, at="@generally contains around", color=OCHRE))
at("There is normally no giant church building", P("church_pews_empty__pe10373537", move="out", zoom=1.12))
at("Worship usually takes place in homes", P("pe20875548", move="in"))
at("barns, or other local spaces", P("pe21482854", move="right"))
at("That limits how large a congregation", C("px9309696"))
at("So when enough families accumulate", divide(
    "How one district becomes ten",
    [(1, "One church district", "@the church district divides"),
     (2, "One becomes two", "@One becomes two"),
     (3, "Two become three", "@two become three"),
     (10, "Three become ten — still one settlement", "@three become ten")],
    frame_label="one settlement", note="20 to 40 households each; worship in homes"))
at("That distinction explains almost everything", C("px4617492"))
at("How many geographically separate", P("pe34471682", move="in", zoom=1.12))
at("How large those communities have become", P("pe33777989", move="left"))
at("And suddenly Pennsylvania and Wisconsin stop", vs(
    "The same map, two different questions", ("Pennsylvania", "the heartland", OXBLOOD), ("Wisconsin", "the frontier", VERD),
    [("Settlements", 63, 68, "@Pennsylvania has 636", "r", "more dots"),
     ("Church districts", 636, 209, "@Wisconsin has only 209", "l", "three times as many")],
    note="2025 estimates", verdict="one counts dots, the other counts congregations",
    verdictAt="@is packed inside those dots"))

# =================================================================== II · Lancaster
at("The best example is Lancaster", head(C("px35323779"), 2, "The giant",
                                         sub="Lancaster County, Pennsylvania", at=0.5))
at("is one of the oldest continuously existing", P("pi166057", move="in"))
at("In 2025, researchers estimated it at roughly", P("pe4613517", move="right", zoom=1.1))
at("And 267 church districts", vs(
    "Lancaster against a whole state", ("Lancaster Co.", "one settlement", OXBLOOD), ("Wisconsin", "sixty-eight settlements", VERD),
    [("People", "44,765", "27,535", "@Pause on that second", "l"),
     ("Church districts", 267, 209, "@The entire state of Wisconsin", "l", "more congregations")],
    note="2025 estimates", verdict="one dot holds more congregations than sixty-eight dots",
    verdictAt="@One Pennsylvania dot", source="Young Center for Anabaptist and Pietist Studies"))
at("And Lancaster is not Pennsylvania's only large community", C("px27132782"))
at("would you want to see more videos like this", P("pe29675750", move="in"))
at("If yes, subscribe", C("px37920031"))
at("The Mifflin County area has around", dict(
    type="almbars", title="Church districts in three Pennsylvania settlements", note="2025 estimates",
    bars=[dict(label="Lancaster Co.", value=267, text="267", at="@The Mifflin County area"),
          dict(label="Mifflin Co.", value=36, text="36", at="@has around 36", color=OCHRE),
          dict(label="Indiana Co.", value=25, text="25", at="@The Indiana County area", color=SLATE)],
    source="Young Center for Anabaptist and Pietist Studies"))
at("Pennsylvania has several old communities", C("px4617442"))
at("has accumulated in roughly the same", P("pe33777985", move="left"))
at("This is what a mature Amish settlement", P("pe14833989", move="in", zoom=1.12))
at("It does not necessarily create a new settlement", C("px19655183"))
at("Often, it simply keeps dividing internally", C("px34006623"))
at("The map still shows one settlement", P("pe34599831", move="right"))
at("But underneath that single dot", P("pe248837", move="in"))
at("This is why simply counting settlements", C("px12172104"))
at("A brand-new Amish community with fifteen people", P("pe11898750", move="out"))
at("On a map, both receive a dot", C("px35960596"))
at("In reality, they are completely different", P("pe2889384", move="in"))

# =================================================================== III · the archipelago
at("Wisconsin has some substantial Amish communities", head(
    C("wisconsin_farmland__pe29951077"), 3, "The archipelago", sub="Wisconsin, one dot at a time", at=0.5))
at("Cashton has grown into the state's largest", amap(
    [dict(at=0, lon=-90.2, lat=44.3, scale=9000)], title="Wisconsin",
    highlight=[dict(id=WI, at=0.2, fill="rgba(56,101,92,.20)")],
    pins=[pin("Cashton", CASHTON, "@Cashton has grown", sub="the state's largest", side="left"),
          pin("Kingston", KINGSTON, "@Kingston is another", sub="another major center", side="right"),
          pin("Augusta", AUGUSTA, "@Augusta, Hillsboro", sub="decades old", side="left")],
    dots=[dot(HILLSBORO, "@Hillsboro", r=8), dot(WILTON, "@Wilton-Tomah", r=8), dot(ATHENS, "@and several others", r=8)]
         + scatter((-90.1, 44.3), 40, "@have existed for decades", spread=1.6, r=6, step=0.06)))
at("But most of Wisconsin's map is not one enormous", C("wisconsin_farmland__pe7225075"))
at("It is a network of smaller ones", P("wisconsin_farmland__pe33864432", move="in"))
at("were spread across 68 settlements", vs(
    "The average dot", ("Pennsylvania", "63 settlements", OXBLOOD), ("Wisconsin", "68 settlements", VERD),
    [("People per settlement", "1,514", "405", "@That works out to roughly", "l", "nearly four times"),
     ("Districts per settlement", 10, 3, "@Pennsylvania averages roughly", "l")],
    note="statewide averages, 2025", verdict="a dot in Pennsylvania is not a dot in Wisconsin",
    verdictAt="@and many Wisconsin communities"))
at("In Adams County, a settlement established", indexp(
    "The smallest dots on the Wisconsin map",
    [("Adams County", "40 people", "@In Adams County", "established 2023"),
     ("Camp Douglas", "15 people", "@Camp Douglas", "founded 2024", True),
     ("Warrens", "20 people", "@Warrens, established", "established 2023")],
    note="each one counts as a settlement", foot="others are one district and a few dozen families",
    footAt="@Other settlements consist"))
at("At the same time, older Wisconsin communities", C("wisconsin_dairy_farm__pe27444497"))
at("So Wisconsin is not one unified Amish belt", C("px2836001"))
at("It is more like an archipelago", card(
    ("Large communities.", "@Large communities", VERD),
    ("Medium communities.", "@medium communities", None),
    ("Tiny communities.", "@tiny communities", OCHRE),
    bg="pe29461446", kicker="an archipelago", dim=0.66))
at("Some are only a few years old", C("px29011156"))
at("All separated enough geographically", P("pe7054539", move="left"))

# =================================================================== IV · built in waves
at("Why did Wisconsin develop this way", head(C("px29461443", skip=3), 4, "Built in waves",
                                              sub="different families, different decades, different counties", at=0.4))
at("Wisconsin's Amish map was built in waves", C("gravel_road_farms__pe36766648"))
at("Some early settlements appeared more than a century", P("pe17488867", move="in"))
at("but several failed", P("pe9575016", move="out"))
at("Families moved away", C("px9507657"))
at("Ministers left", P("pe37165990", move="in"))
at("Communities disappeared", P("pi5070133", move="right"))
at("Then new groups arrived later", C("px30728494"))
at("The modern Wisconsin Amish landscape", C("wisconsin_farmland__pe5775086"))
at("Cashton dates to the", indexp(
    "When the Wisconsin communities began",
    [("Cashton", "1960s", "@Cashton dates to", None, False, False),
     ("Wilton–Tomah", "1960s", "@Wilton-Tomah also emerged", None, False, False),
     ("Kingston", "1970s", "@Kingston took shape", None, False, False),
     ("Augusta", "1970s", "@Augusta followed", None, False, False),
     ("and on through", "2020s", "@Then came communities", "1980s · 1990s · 2000s · 2010s", True, False)],
    note="sixty-eight settlements, laid down a few at a time"))
at("In other words, Wisconsin did not receive one giant", C("px39669906"))
at("Different Amish groups arrived at different times", P("pi287407", move="in", zoom=1.1))
at("That matters because the Amish are", card(
    ("There is no national", "@There is no national", None, 56),
    ("Amish headquarters deciding", "@Amish headquarters", None, 56),
    ("“this county gets 500 families.”", "@This county gets", OXBLOOD, 50, "Garamond"),
    bg="pe12983687", kicker="no head office", dim=0.68))
at("Individual church communities differ in how they regulate", C("px20184480"))
at("farming practices, and other details", C("px9467497"))
at("Families often prefer to settle near other Amish", P("pe9459922", move="in"))
at("So when Amish migration enters a state", C("px25405403"))
at("Sometimes the better fit is somewhere else", P("gravel_road_farms__pe35117861", move="left"))
at("a different cluster", P("pe32320447", move="right"))
at("and Wisconsin has become a place where many", C("wisconsin_farmland__pe29951077", skip=4))
at("There is a revealing example from", amap(
    [dict(at=0, lon=-83.6, lat=41.6, scale=4200), dict(at="@They liked the area", lon=-85.0, lat=42.4, scale=5200, d=3.0)],
    title="1990 · Spring Run to Athens",
    highlight=[dict(id=PA, at=0.3), dict(id=WI, at="@traveled west to inspect", fill="rgba(56,101,92,.24)")],
    pins=[pin("Spring Run, Pa.", SPRINGRUN, "@A group of Amish men", sub="the old settlement", side="right"),
          pin("Athens, Wis.", ATHENS, "@They liked the area", sub="a new settlement followed", side="left")],
    routes=[dict(**{"from": SPRINGRUN, "to": ATHENS}, at="@traveled west to inspect", d=2.6, arrow=True,
                 color=OXBLOOD, width=5)]))
at("they were looking for two very practical things", C("wisconsin_dairy_farm__pe10041433"))
at("less expensive farms", tag(C("milk_tanker_truck__pe35355552"), "a workable milk market",
                               "cheap farms and somewhere to sell the milk", at="@and a workable milk market"))
at("A new settlement followed", C("cheese_factory_creamery__pe854838"))
at("That story is small", P("pe14021175", move="in"))
at("but the mechanism is enormous", C("px34208179", skip=4))

# =================================================================== V · the land
at("For a young Amish family trying to establish", head(
    C("px9316131"), 5, "The arithmetic of land", sub="more sons than acres", at=0.5))
at("It can determine whether the lifestyle", P("pe8514564", move="in"))
at("When an old settlement grows for generations", dict(
    type="almsplit", title="One farm, five sons", note="land does not multiply with the population",
    n=5, label="one farm", each="1/5", who="son {n}",
    at="@farmland gets divided", splitAt="@More sons and daughters",
    verdict="the amount of land does not multiply with the population", verdictAt="@but the amount of land"))
at("Eventually, some families look outward", C("px4617576"))
at("not because the old community is dying", P("pe2042161", move="right"))
at("It has produced more families than the local", C("px11841268"))
at("And Wisconsin has repeatedly offered", C("wisconsin_farmland__pe7225075", skip=5))
at("rural agricultural areas where a new group", P("wisconsin_farmland__pe34014614", move="in"))
at("But cheap land is only one part", C("px37920028"))
at("The Young Center lists several reasons", card(
    ("Affordable farmland.", "@Affordable farmland", OCHRE, 44),
    ("Suitable work off the farm.", "@access to suitable", None, 44),
    ("Rural isolation.", "@rural isolation", None, 44),
    ("An environment that fits the way they live.", "@a local social", None, 44),
    ("Relatives and compatible church groups.", "@proximity to relatives", None, 44),
    ("And sometimes a disagreement to resolve.", "@and sometimes the need", OXBLOOD, 44),
    bg="pe29051618", kicker="why a new settlement starts", dim=0.72, w=1320))
at("That means two families can leave the same", C("px26771970"))
at("and two groups arriving in Wisconsin may", P("pe33786718", move="left"))
at("More migration does not always make one dot bigger", P("pe12345626", move="in"))

# =================================================================== VI · still happening
at("The movement is still happening", head(C("px12484254", skip=3), 6, "Still happening",
                                           sub="where a family lands, and why", at=0.4))
at("found that newcomers were not simply shifting", dict(
    type="almshare", title="Who moves into a Wisconsin settlement", note="households that reported a prior location, 2025 study",
    parts=[dict(frac=0.58, big="most", label="from another state", color=OXBLOOD, at="@a majority of those moving"),
           dict(frac=0.42, big="many", label="from another Wisconsin settlement", color=VERD, at="@A large share also moved")],
    source="2025 study of relocations into Wisconsin Amish settlements"))
at("and the patterns were not random", C("px18486127"))
at("Religious affiliation appeared to be an important", P("pe5561791", move="in"))
at("Imagine Wisconsin not as one destination", C("px2570204", skip=4))
at("but as dozens of potential destinations", P("pe34471682", move="right", zoom=1.1))
at("They may ask", card(
    ("Which community has people we know?", "@Which community has", None, 46),
    ("Which church practices match ours?", "@Which church practices", None, 46),
    ("Where is land available?", "@Where is land available", OCHRE, 46),
    ("Where can I make a living?", "@Where can I make", None, 46),
    ("Where can my children find spouses?", "@Where can my children", OXBLOOD, 46),
    bg="pe26830925", kicker="a family's questions", dim=0.72, w=1320))
at("Those decisions create a decentralized", C("px28122441"))
at("One family goes first", dict(
    type="almdistrict", title="How a dot appears", note="one household at a time",
    centre="A new settlement", centreSub="one district", houses=24, step=0.12,
    housesAt="@Relatives visit", count="enough families to support regular worship",
    countAt="@Eventually, there are enough",
    roles=[dict(text="a school", at="@A school may appear"), dict(text="businesses", at="@Businesses follow")]))
at("A tiny cluster becomes a functioning settlement", C("rural_crossroads_village__pe27132781"))
at("If you're enjoying stories about how communities", P("pe29137946", move="left"))
at("this pattern goes much further", C("px4606785"))

# =================================================================== VII · a decade apart
at("Now compare what happened from", head(C("px34668476"), 7, "A decade apart",
                                          sub="2015 against 2025", at=0.4))
at("Pennsylvania went from 54", delta(
    "Pennsylvania, 2015 → 2025",
    [dict(label="Settlements", **{"from": 54, "to": 63}, delta="+9", at="@Pennsylvania went from 54",
          note="a net gain of nine", color=OXBLOOD),
     dict(label="Church districts", **{"from": 465, "to": 636}, delta="+171 districts",
          at="@But its church districts exploded", note="the same communities, much bigger", color=OXBLOOD)],
    frm="2015", to="2025", foot="classic internal growth", footAt="@An increase of 171", footY=820))
at("Existing communities are getting much bigger", P("pe33777986", move="in"))
at("Wisconsin followed a different path", delta(
    "Wisconsin, 2015 → 2025",
    [dict(label="Settlements", **{"from": 50, "to": 68}, delta="+18", at="@It went from 50",
          note="twice Pennsylvania's gain", color=VERD),
     dict(label="Church districts", **{"from": 138, "to": 209}, delta="+71 districts",
          at="@Its church districts also", note="new ground, not deeper ground", color=VERD)],
    frm="2015", to="2025", foot="the geographic spread is the striking part",
    footAt="@the geographic spread is the striking", footY=820))
at("Wisconsin kept adding separate communities", C("px2818521"))
at("over that decade, Pennsylvania", vs(
    "One new settlement for every…", ("Pennsylvania", "grew inward", OXBLOOD), ("Wisconsin", "grew outward", VERD),
    [("Additional church districts", 19, 4, "@added roughly one new settlement", "r", "a new dot far sooner")],
    note="per new settlement, 2015 → 2025", verdict="not a rule — the shape of growth",
    verdictAt="@but the contrast reveals"))
at("Pennsylvania's growth is heavily concentrated", P("pe4613517", move="in", zoom=1.12))
at("Wisconsin is much more geographically distributed", C("midwest_farmland_aerial__pe9708017"))
at("and Wisconsin is not even the only state", indexp(
    "Amish settlements by state, 2025",
    [("Missouri", 64, "@Missouri had 64"),
     ("New York", 60, "@New York had 60"),
     ("Kentucky", 55, "@Kentucky had 55"),
     ("Michigan", 53, "@Michigan had 53"),
     ("Ohio", 74, "@Ohio led them all", "more than any other state", True)],
    note="the settlement frontier, not the population", y0=268, rowH=86,
    foot="the old picture — Pennsylvania, Ohio, Indiana — is getting less useful",
    footAt="@The old mental picture", source="Young Center for Anabaptist and Pietist Studies"))
at("Those states still contain most of the people", C("px12240430"))
at("but the settlement frontier is much wider", P("pe207058", move="right"))

# =================================================================== VIII · a research category
at("There is one important caution here", head(C("old_atlas_map__pe13661114"), 8, "A research category",
                                               sub="where one settlement ends and another begins", at=0.5))
at("It is not a permanent legal boundary", P("old_atlas_map__pe13630461", move="in", zoom=1.12))
at("Researchers sometimes reconsider where", C("old_atlas_map__pe13661113"))
at("That happened recently around Lancaster", amap(
    [dict(at=0, lon=-76.5, lat=40.0, scale=14000), dict(at="@researchers began listing", lon=-76.5, lat=40.0, scale=16000, d=3.0)],
    title="Lancaster and York",
    pins=[pin("Lancaster Co.", LANC, "@For years, church districts", sub="44,765 people", side="right"),
          pin("York Co.", YORK, "@As the York County community", sub="listed separately", side="left")],
    dots=scatter(LANC, 26, "@For years, church districts", spread=0.34, r=8, color=OXBLOOD, step=0.04)
         + scatter(YORK, 10, "@researchers began listing", spread=0.22, r=8, color=SLATE, step=0.06)))
at("Nothing dramatic happened overnight", P("pe29024187", move="in"))
at("The classification changed because the community", C("px11645112"))
at("The exact difference between", card(
    ("Five is not a magical number.", "@Five is not a magical", OXBLOOD),
    ("Next year's totals may change.", "@Next year's totals", None),
    bg="pe39334207", kicker="a caution", dim=0.66))
at("Communities can begin", C("px31025083"))
at("They can divide", P("pe5367172", move="left"))
at("Researchers can refine boundaries", P("old_atlas_map__pe159757", move="in"))
at("The meaningful fact is the structure", C("px12484254", skip=6))
at("One state contains many more people concentrated", P("pe34258436", move="right"))
at("The other spreads a much smaller population", C("wisconsin_farmland__pe29951077", skip=8))

# =================================================================== IX · a population that doubles
at("The Amish population of North America is not stable", head(
    C("px9467499"), 9, "A population that doubles", sub="every twenty years", at=0.4))
at("It is growing rapidly", dict(
    type="almgrowth", title="The Amish population of North America", note="estimates, 2000 to 2025",
    points=[dict(x=2000, y=177910, label="177,910", sub="2000", at="@In 2000", dy=-110),
            dict(x=2012, y=273700, label="273,700", sub="2012", at=5.0, dy=-106),
            dict(x=2025, y=410955, label="410,955", sub="2025", at="@the estimate had reached", color=OXBLOOD, dy=-112)],
    grid=[dict(y=200000, label="200,000"), dict(y=400000, label="400,000")],
    ticks=[2000, 2005, 2010, 2015, 2020, 2025], ymax=460000,
    source="Young Center for Anabaptist and Pietist Studies"))
at("an increase of about", stat("131%", "growth since 2000", "the population roughly doubles every twenty years",
                                "pi5143781", unit="in 25 years", at="@an increase of about", countFor=1.6, color=OXBLOOD))
at("The main reasons are unusually large families", C("px9467497", skip=4))
at("That creates a simple geographic problem", P("pe11111325", move="in"))
at("Every generation needs more households", C("px31025083", skip=4))
at("Some communities absorb those households", P("pe33777985", move="left"))
at("More homes", C("px20663033"))
at("more church districts", P("pe2708223", move="in"))
at("Existing settlement gets denser and larger", C("px19675231", skip=4))
at("But there is a limit to how much expansion", C("px32179574"))
at("Land becomes difficult to obtain", P("farm_for_sale_sign__pe8470803", move="in", zoom=1.12))
at("Development closes in", C("px26547060"))
at("Then the pressure escapes outward", C("px39669906", skip=4))
at("and if enough compatible families follow", P("pe5541665", move="right"))
at("It reproduces somewhere else", C("px37920031", skip=3))
at("That is why the Amish map expands differently", C("px34066758", skip=4))
at("Growth does not have to produce a giant city", P("pe12345627", move="in"))
at("In 2025 alone", stat(
    "9", "newly established settlements, 2025", "and not one existing settlement dissolved that year",
    "pe2042161", unit="new dots on the map", at="@researchers recorded nine", countFor=1.2, color=VERD))
at("And more than half of all Amish settlements", dict(
    type="almshare", title="How big is a typical settlement?", note="all Amish settlements in North America, 2025",
    parts=[dict(frac=0.52, big="more than half", label="one church district", color=VERD,
                at="@contain only a single"),
           dict(frac=0.48, big="the rest", label="two districts or more", color=OCHRE, at="@That means most dots")],
    source="Young Center for Anabaptist and Pietist Studies"))
at("They are small", P("pe11898750", move="out", zoom=1.1))
at("Some may not survive", C("px35960596", skip=3))
at("but a few of them could eventually become", P("pe12001572", move="in"))

# =================================================================== X · back to the numbers
at("Now go back to the original numbers", head(C("px34208179", skip=8), 10, "Back to the numbers",
                                               sub="what they actually describe", at=0.4))
at("about 95,410 Amish people", vs(
    "Pennsylvania and Wisconsin, 2025", ("Pennsylvania", "older, deeper roots", OXBLOOD), ("Wisconsin", "more separate shoots", VERD),
    [("Amish residents", "95,410", "27,535", "@about 95,410", "l", "three times as many"),
     ("Settlements", 63, 68, "@63 settlements", "r", "five more"),
     ("Church districts", 636, 209, "@636 church districts", "l", "almost three times")],
    note="Young Center estimates", verdict="the numbers no longer contradict each other",
    verdictAt=12.5, rowH=126))
at("Pennsylvania has more than three times", C("px4617441", skip=4))
at("They describe two different stages", P("pe29051618", move="out"))
at("Pennsylvania is filled with older", P("pe1089097", move="in"))
at("Wisconsin contains more separate shoots", C("wisconsin_farmland__pe5775086", skip=3))
at("Pennsylvania's typical map dot", P("pe4613517", move="left", zoom=1.12))
at("Wisconsin needs many more dots", C("midwest_farmland_aerial__pe18749793"))
at("and that is why the map feels wrong at first", P("pe29675750", move="in"))
at("We unconsciously assume one settlement means", card(
    ("A settlement can mean fifteen people", "@A settlement can mean", None, 52),
    ("in a new rural cluster —", "@in a new rural", None, 52),
    ("or forty-five thousand around Lancaster.", "@or nearly forty-five", OXBLOOD, 52),
    ("Both are counted once.", "@Both are counted once", OCHRE, 56),
    bg="pe34471682", kicker="one dot, two worlds", dim=0.7, w=1280))

# =================================================================== XI · the smallest dots
at("So why does Wisconsin have more Amish settlements", head(
    C("px29011159"), 11, "Deep, and wide", sub="the real answer", at=0.4))
at("Not because Pennsylvania is losing its importance", C("px27902028"))
at("And not because Amish families are abandoning", P("pe38726328", move="in"))
at("Pennsylvania shows what happens when Amish communities", card(
    ("Pennsylvania shows what happens", "@Pennsylvania shows what", None, 54),
    ("when communities grow deep.", "@when Amish communities grow", OXBLOOD, 54),
    ("Wisconsin shows what happens", "@Wisconsin shows what happens", None, 54),
    ("when they grow wide.", "@when they grow wide", VERD, 54),
    bg="sunrise_barn_mist__pe28887344", kicker="deep and wide", dim=0.7, w=1300))
at("In Pennsylvania, generations have piled into", P("pe34391784", move="right"))
at("One geographic community can contain hundreds", C("px19655182", skip=4))
at("In Wisconsin, different waves of families", C("wisconsin_farmland__pe7225075", skip=8))
at("formed separate communities", P("pe32320447", move="left"))
at("Pennsylvania built giants", amap(
    [dict(at=0, lon=-83.0, lat=41.6, scale=3800), dict(at="@And the smallest dots", lon=-84.6, lat=42.0, scale=4400, d=3.0)],
    title="Giants and dots",
    highlight=[dict(id=PA, at="@Pennsylvania built giants"), dict(id=WI, at="@Wisconsin built dots", fill="rgba(56,101,92,.26)")],
    dots=[dot(LANC, "@Pennsylvania built giants", r=34, color=OXBLOOD),
          dot(MIFFLIN, "@Pennsylvania built giants", r=15, color=OXBLOOD),
          dot(INDIANA_CO, "@Pennsylvania built giants", r=13, color=OXBLOOD)]
         + scatter((-90.1, 44.2), 46, "@Wisconsin built dots", spread=1.7, r=7, step=0.045)))
at("because Lancaster was once a small settlement too", C("px29461443", skip=6))
at("Cashton was once a handful of families", P("pe11929455", move="in"))
at("Every giant Amish community began with someone", P("pe14058112", move="right", zoom=1.1))
at("There is not enough room for our future here", C("px5542449"))
at("A farm is purchased", P("real_estate_auction_sign__pe8482511", move="in"))
at("Another family follows", P("pe14280799", move="in"))
at("A congregation forms", P("pe12983687", move="left"))
at("Children are born", P("pe8603672", move="in"))
at("The district divides", C("px19655183", skip=5))
at("And if enough people remain long enough", C("sunrise_barn_mist__pe29065906"))
at("That is the real meaning behind Wisconsin's", stat(
    "68", "Wisconsin · settlements", "the Amish map is not only growing — it is spreading into more versions of itself",
    "sunrise_barn_mist__pe28887344", unit="separate communities", at="@That is the real meaning", countFor=1.4, color=VERD))
at("And that leaves an even more interesting question", C("px29011156", skip=4))
at("If a handful of Amish families find cheap land", fadeout(card(
    ("What has to happen", "@what exactly has to happen", None, 58),
    ("before a handful of families", "@before they can call", None, 58),
    ("can call it a real settlement?", "@a real Amish settlement", OXBLOOD, 58),
    ("Because buying the farms is only the beginning.", "@Because buying the farms", None, 38, "Garamond"),
    bg="sunrise_barn_mist__pe34387507", kicker="the next question", dim=0.72, w=1320), d=3.2))


# ============================================================== music: one quiet bed per act
edl.main(music=[
    dict(at=None, track="02_Leaving_Home_Somber_Long_Bed.mp3"),
    dict(at="The first thing to understand", track="Mark Jubel - Efteraar.mp3", lead=-1.0),
    dict(at="Wisconsin has some substantial Amish communities", track="04_Sad_Trio_Somber_Piano_Cello.mp3", lead=-1.0),
    dict(at="For a young Amish family trying to establish", track="11_Unanswered_Questions_Mystery.mp3", lead=-1.0),
    dict(at="Now compare what happened from", track="Slow Dramatic Ascent.mp3", lead=-1.0),
    dict(at="The Amish population of North America is not stable", track="12_Magic_Forest_Dark_Cello.mp3", lead=-1.0),
    dict(at="So why does Wisconsin have more Amish settlements", track="02_Leaving_Home_Somber_Long_Bed.mp3", lead=-1.0),
])
