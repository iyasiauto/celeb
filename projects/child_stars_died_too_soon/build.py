"""
35 Child Actors Who Died Too Soon — How Many Do You Remember?  (14:13)

Look: FINAL REEL (templates/finalreel) - a film-archive memorial. Charcoal and ivory, a muted gold for what they
were known for, one crimson for the ending. Fast cold open (1.5-2 s cuts, a wall of faces on the count), then a
slow documentary body. One person = castcard on their name -> their roles (borrowed show / film clips, 2-4 s,
silent, INSIDE the film frame; Our Gang shorts in the vintage TV) and photographs -> the turn -> ageclock on the
age -> memoriam for the endings that land hardest. A map where the place matters; quotes where words were said.

Footage: media/nostalgia/src - QC'd in people mode (qc.json): competitor clips cut from inside their frame
(cmp_*), pictures from Google / Wikimedia (no stock or watermark hosts), B-roll from Pexels / Pixabay.

The shot list is generated from the table PEOPLE below and the voice's own subtitles (data/voiceover.srt), so every
cut lands on a spoken line; hand-placed shots (cold open, maps, quotes, outro) are listed explicitly.

    python build.py plan | prep | stills [ids] | render [ids] | mix | final
"""

import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "docu"))

import edl                       # noqa: E402
from edl import *                # noqa: E402,F401,F403

SP = os.environ.get("VIDEO_ROOT", os.path.join(HERE, "..", "..", "media"))
NS = f"{SP}/nostalgia"
edl.setup(
    name="35_Child_Actors_Who_Died_Too_Soon",
    kit=os.environ.get("VIDEO_KIT", f"{SP}/kit"),
    footage=f"{NS}/footage",
    work=f"{SP}/work_cs",
    data=os.path.join(HERE, "data"),
    out=f"{SP}/out",
    image_dirs=[f"{NS}/src/images"],
    template="finalreel",
    topic="child actors and child stars who died young: childhood nostalgia, classic TV shows and films, their lives and tragic endings",
    music_floor_db=-21.0, music_duck_db=-10.0, sfx_gain=0.5,
)

GOLD, CRIMSON, IVORY = "#C9A45C", "#A3262A", "#EDE6D6"
QC = json.load(open(f"{NS}/src/qc.json", encoding="utf-8"))
USED = set()


def ok(f):
    return f in QC and not QC[f].get("reject")


def slug(s):
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")


IMGS = sorted(f for f in os.listdir(f"{NS}/src/images") if ok(f))
_W = {}


def size(f):
    if f not in _W:
        from PIL import Image
        _W[f] = Image.open(f"{NS}/src/images/{f}").size
    return _W[f]


def pics(person):
    """this person's pictures, best first (QC quality, then size)"""
    fs = [f for f in IMGS if f.startswith(slug(person) + "__")]
    return sorted(fs, key=lambda f: (-(QC[f].get("quality") or 0), -size(f)[0] * size(f)[1]))


def take(person, wide=None):
    """the next unused picture of a person (wide=True prefers landscape, False portrait)"""
    fs = [f for f in pics(person) if f not in USED]
    if not fs:
        fs = pics(person)           # out of pictures: reuse the best (the audit warns)
    if wide is not None:
        pref = [f for f in fs if (size(f)[0] >= size(f)[1]) == wide]
        fs = pref or fs
    f = fs[0]
    USED.add(f)
    return os.path.splitext(f)[0]


def tall(stem):
    f = stem + ".jpg"
    w, h = size(f)
    return h > w * 0.95


_IDX = {c["video"]: k for k, c in enumerate(edl.CAT)}


def clips_of(person):
    return [c["video"] for c in edl.CAT if c["video"].startswith(slug(person) + "__cmp_") and ok(c["video"])]


BROLL = {}
for c in edl.CAT:
    if c["video"].startswith("broll_") and ok(c["video"]):
        BROLL.setdefault(c["video"].split("__")[0][6:], []).append(c["video"])


def broll(*topics):
    for t in topics:
        for v in BROLL.get(t, []):
            if v not in USED:
                USED.add(v)
                return v
    return None


# ------------------------------------------------------------------ devices
BOX = [330, 104, 1260, 709]                     # the window of the film frame (x, y, w, h)


def framed(video, caption="", right="", name=None, role=None, flip=False, skip=0.0, more=()):
    """a borrowed clip inside the ivory film frame (never full screen); `more` = further clips cut on after it"""
    i = _IDX[video]
    USED.add(video)
    USED.update(more)
    s = clip(i, grade="reel", skip=skip, then=tuple(_IDX[m] for m in more))
    s.update(inset=BOX, flip=flip, no_texture=True)
    o = dict(type="reelframe", box=BOX, caption=caption, right=right, at=0.0)
    if name:
        o.update(name=name, role=role or "")
    s["overlays"] = [o]
    return s


def tv(video, skip=0.0):
    """an Our Gang / archive clip in the vintage TV gate"""
    USED.add(video)
    s = clip(_IDX[video], grade="reel", skip=skip, zoom=1.04)
    s["archive"] = True
    return s


def bclip(video, skip=0.0):
    USED.add(video)
    return clip(_IDX[video], grade="reel", zoom=1.03, skip=skip)


def dur(video):
    c = edl.CAT[_IDX[video]]
    return c["e"] - c["s"] - 0.25


GENERIC = ("film_reel_spinning", "film_projector", "vintage_tv_living_room", "child_watching_tv_retro", "old_cinema_marquee",
           "kids_riding_bikes_suburb", "suburban_house_sunset", "empty_playground_swing", "theater_curtain_stage",
           "film_clapperboard", "stage_spotlight", "box_of_old_photographs", "tv_antenna_rooftop", "vintage_camera_film",
           "old_crt_television_static", "hollywood_walk_of_fame", "los_angeles_night_street")
RESERVED = {"memorial_candles", "cemetery_flowers", "sunset_boulevard", "hollywood_sign", "movie_theater_empty_seats",
            "polaroid_photos", "old_family_home_video", "vhs_tape"}


def fresh(person, *topics):
    """an unused picture of the person, else B-roll - the outro never repeats a shot"""
    if any(f not in USED for f in pics(person)):
        return P(take(person), move="in")
    return B(*(topics or ("box_of_old_photographs", "polaroid_photos", "theater_curtain_stage")), person=person)


def B(*topics, person=None):
    """B-roll for one of these topics, else a photograph of `person`"""
    v = broll(*topics)
    return bclip(v) if v else P(take(person or "Judith Barsi"), move="in")
DEPTH = {"River Phoenix", "Cameron Boyce", "Michelle Trachtenberg", "Heather O'Rourke", "Corey Haim", "Lee Thompson Young", "Anissa Jones"}


def P(stem, move="in", name=None, role=None, **kw):
    """a photograph: portraits shown whole on their blurred twin, landscapes full frame"""
    if tall(stem):
        kw.setdefault("fit", "contain")
        kw.setdefault("margin", 0.86)
    else:
        kw.setdefault("focus", (0.5, 0.32))
    s = photo(stem, move=move, zoom=kw.pop("zoom", 1.08), grade="reel", **kw)
    if name:
        s["overlays"] = list(s.get("overlays", [])) + [dict(type="nameplate", name=name, role=role or "", at=0.5)]
    return s


def castcard(person, n, role, years, age, **kw):
    stem = take(person, wide=False)
    s = dict(type="castcard", img=img(stem, "reel"), name=person, role=role, years=years, age=age, n=n,
             frameLabel=f"KODAK 5247  ▸ {n:02d}A", at=0.25, lines=2 if len(person) > 17 else 1,
             size=96 if len(person) > 17 else 112)
    s.update(kw)
    return s


def ageclock(person, value, note=None, date=None, **kw):
    stem = take(person)
    s = dict(type="ageclock", img=img(stem, "reel"), kicker=person.upper(), value=value, note=note, date=date,
             countFor=1.3, at=0.25)
    s.update(kw)
    return s


def memoriam(person, years, line=None, **kw):
    stem = take(person)
    s = dict(type="memoriam", img=img(stem, "bw"), name=person, years=years, line=line, at=0.1)
    s.update(kw)
    return s


def rollcall(people, title, sub=None, **kw):
    stems = [pics(p)[0] for p in people if pics(p)]
    s = dict(type="rollcall", imgs=[img(os.path.splitext(f)[0], "reel") for f in stems], names=list(people), cols=7,
             fillFor=kw.pop("fillFor", 2.4), title=title, sub=sub)
    s.update(kw)
    return s


def amap(stops, pins, **kw):
    s = dict(type="map", detail="geo_hi.json", adminCountries=kw.pop("countries", ["USA"]), stops=stops, pins=pins)
    s.update(kw)
    return s


# ------------------------------------------------------------------ the voice's own lines
SRT = []
for blk in open(os.path.join(HERE, "data", "voiceover.srt"), encoding="utf-8-sig").read().strip().split("\n\n"):
    ls = blk.strip().split("\n")
    if len(ls) < 3:
        continue
    a, b = ls[1].split(" --> ")
    ts = lambda x: int(x[:2]) * 3600 + int(x[3:5]) * 60 + float(x[6:].replace(",", "."))
    SRT.append((ts(a), ts(b), " ".join(ls[2:])))


def line_at(prefix, after=0.0):
    """start time of the first subtitle line at/after `after` that starts with `prefix`"""
    p = prefix.lower()
    for a, b, t in SRT:
        if a >= after - 0.01 and t.lower().startswith(p):
            return a
    raise KeyError(prefix)


def lines_between(t0, t1):
    return [(a, b, t) for a, b, t in SRT if t0 <= a < t1 - 0.05]


# ------------------------------------------------------------------ the 35
# (name, first words of their entry, role / known for, years, age, line that holds the age, extras)
PEOPLE = [
    ("Judith Barsi", "Judith Barsi was only", "Ducky · The Land Before Time", "1978 — 1988", 10, None,
     dict(memo="She never saw how loved they became.", memo_at="She never saw how loved",
          life=[(1984, "first commercials", 6, "Judith Barsi was only"), (1987, "Jaws: The Revenge", 9, "She was the voice"),
                (1988, "Ducky · Anne-Marie", 10, "and Anne-Marie")])),
    ("River Phoenix", "River Phoenix was the face", "Stand by Me · My Own Private Idaho", "1970 — 1993", 23, "He was twenty-three",
     dict(date="OCTOBER 31, 1993 · LOS ANGELES", memo="Hollywood lost the actor many believed would define the next thirty years.",
          memo_at="Hollywood lost the actor",
          map=("he collapsed outside", [dict(at=0, lon=-98.0, lat=38.5, scale=1300), dict(at=0.6, lon=-118.385, lat=34.09, scale=26000, d=2.4)],
               [dict(label="The Viper Room", sub="Sunset Strip, Los Angeles", lon=-118.385, lat=34.09, at=2.2, side="right")]))),
    ("Anton Yelchin", "Anton Yelchin played", "Chekov · Star Trek", "1989 — 2016", 27, "He was twenty-seven",
     dict(note="The accident led to a recall of over a million vehicles.")),
    ("Cameron Boyce", "Cameron Boyce", "Luke · Jessie  ·  Carlos · Descendants", "1999 — 2019", 20, "He was twenty,",
     dict(memo="His family turned grief into a foundation in his name.", memo_at="and his family turned grief")),
    ("Billy Laughlin", "Remember Froggy", "Froggy · Our Gang", "1932 — 1948", 16, "at just sixteen", dict(tv=True)),
    ("Brad Renfro", "Brad Renfro was discovered", "Mark Sway · The Client", "1982 — 2008", 25, "He died of a heroin", dict()),
    ("Bobby Driscoll", "Bobby Driscoll was Disney", "Peter Pan · Treasure Island", "1937 — 1968", 31, "at thirty-one",
     dict(memo="Peter Pan was buried in an unmarked grave.", memo_at="Peter Pan was buried",
          life=[(1946, "Song of the South", 9, None), (1950, "Treasure Island", 13, "the voice and model"),
                (1953, "Peter Pan", 16, "the boy who never grows up")])),
    ("Dana Plato", "Dana Plato was Kimberly", "Kimberly · Diff'rent Strokes", "1964 — 1999", 34, "at thirty-four", dict()),
    ("Gary Coleman", "Gary Coleman,", "Arnold · Diff'rent Strokes", "1968 — 2010", 42, "he died at forty-two",
     dict(life=[(1978, "Diff'rent Strokes begins", 10, None), (1979, "“What you talkin' 'bout, Willis?”", 11, "turned"),
                (1986, "the series ends", 18, "into a permanent piece")])),
    ("Corey Haim", "Corey Haim was half", "The Lost Boys · Lucas", "1971 — 2010", 38, "He died in two thousand and ten", dict()),
    ("Heather O'Rourke", "Heather O'Rourke said", "Carol Anne · Poltergeist", "1975 — 1988", 12, "She was twelve",
     dict(quote=("They're here.", "The little girl from Poltergeist"))),
    ("Jonathan Brandis", "Jonathan Brandis was", "seaQuest DSV · Ladybugs", "1976 — 2003", 27, "at twenty-seven", dict()),
    ("Lee Thompson Young", "Lee Thompson Young was", "The Famous Jett Jackson", "1984 — 2013", 29, "In 2013, at twenty-nine", dict()),
    ("Sawyer Sweeten", "Sawyer Sweeten", "Geoffrey · Everybody Loves Raymond", "1995 — 2015", 19, "just weeks before",
     dict(note="Weeks before his twentieth birthday.")),
    ("Skye McCole Bartusiak", "Skye McCole Bartusiak", "Susan · The Patriot", "1992 — 2014", 21, "at twenty-one", dict()),
    ("Carl Switzer", "Carl Switzer,", "Alfalfa · Our Gang", "1927 — 1959", 31, "He was thirty-one", dict(tv=True)),
    ("Matthew Garber", "Matthew Garber was", "Michael Banks · Mary Poppins", "1956 — 1977", 21, "He was twenty-one",
     dict(map=("he contracted hepatitis", [dict(at=0, lon=40.0, lat=35.0, scale=900), dict(at=0.4, lon=78.9, lat=22.0, scale=1700, d=2.0)],
               [dict(label="India", sub="1977", lon=78.9, lat=22.0, at=1.6, side="right")], ["IND"]))),
    ("Rob Knox", "Rob Knox had just", "Marcus Belby · Harry Potter", "1989 — 2008", 18, "He was eighteen",
     dict(map=("outside a London bar", [dict(at=0, lon=-2.5, lat=53.5, scale=2600), dict(at=0.4, lon=-0.12, lat=51.47, scale=16000, d=2.0)],
               [dict(label="Sidcup, London", sub="May 2008", lon=0.10, lat=51.43, at=1.6, side="right")], ["GBR"]))),
    ("Dominique Dunne", "Dominique Dunne played", "Dana · Poltergeist", "1959 — 1982", 22, "She died days later", dict()),
    ("Rebecca Schaeffer", "Rebecca Schaeffer starred", "Patti · My Sister Sam", "1967 — 1989", 21, "She was twenty-one",
     dict(memo="Her death gave America its first anti-stalking law.", memo_at="Her death pushed California")),
    ("Jonshel Alexander", "Jonchelle Alexander was", "Beasts of the Southern Wild", "DIED 2022", 22, "at twenty-two",
     dict(map=("she was shot while", [dict(at=0, lon=-92.0, lat=31.0, scale=5200), dict(at=0.4, lon=-90.07, lat=29.95, scale=24000, d=1.8)],
               [dict(label="New Orleans", sub="2022", lon=-90.07, lat=29.95, at=1.4, side="right")]))),
    ("Michelle Trachtenberg", "Michelle Trachtenberg was", "Harriet the Spy · Buffy · Gossip Girl", "1985 — 2025", 39, "She was thirty-nine",
     dict(memo="Three eras of kids grew up with her.", memo_end=True)),
    ("Christopher Pettiet", "Christopher Pettiet rode", "The Young Riders", "1976 — 2000", 24, "at twenty-four", dict()),
    ("Josh Ryan Evans", "Josh Ryan Evans was", "Timmy · Passions", "1982 — 2002", 20, "at twenty",
     dict(memo="He died on the day his character's death aired.", memo_at="on the exact same day")),
    ("Sammi Kane Kraft", "Sammy Kane Kraft was", "Amanda · The Bad News Bears", "1992 — 2012", 20, "at twenty,", dict()),
    ("Ashleigh Aston Moore", "Ashley Aston Moore", "young Chrissy · Now and Then", "1981 — 2007", 26, "at 26", dict()),
    ("Justin Pierce", "Justin Pierce was discovered", "Casper · Kids", "1975 — 2000", 25, "at 25", dict()),
    ("Nikita Pearl Waligwa", "Nikita Pearl Waligwa", "Gloria · Queen of Katwe", "2005 — 2020", 15, "She was 15",
     dict(quote=("In chess, the small one can become the big one.", "telling her"))),
    ("Mya-Lecia Naylor", 653.95, "Millie Inbetween · Almost Never", "2002 — 2019", 16, "at 16", dict()),
    ("Michael Cuccione", "Michael Cuccione made", "QT · 2gether", "1985 — 2001", 16, "The disease's complications", dict()),
    ("Anissa Jones", "Anissa Jones was Buffy", "Buffy · Family Affair", "1958 — 1976", 18, "at 18", dict()),
    ("Bridgette Andersen", "Bridgette Anderson", "Savannah Smiles", "1975 — 1997", 21, "She died of an accidental", dict()),
    ("Rusty Hamer", "Rusty Hamer grew up", "Rusty · Make Room for Daddy", "1947 — 1990", 42, "at 42", dict()),
    ("Logan Williams", "Logan Williams played", "young Barry Allen · The Flash", "DIED 2020", 16, "at sixteen", dict()),
    ("Tyler Sanders", "Tyler Sanders starred", "Just Add Magic: Mystery City", "2004 — 2022", 18, "at eighteen", dict()),
]
NAMES = [p[0] for p in PEOPLE]

# B-roll by what a line is about (never the same clip twice)
MOOD = [(r"overdose|heroin|drug|pills|fentanyl|addiction|painkiller", ("rain_on_window_night", "rainy_street_lights_night")),
        (r"cancer|tumor|lymphoma|heart|kidney|liver|diabetes|hepatitis|illness|seizure|septic", ("empty_playground_swing", "autumn_leaves_cemetery")),
        (r"truck|scooter|jeep|car accident|freeway|passenger", ("los_angeles_night_street",)),
        (r"shot|killed|knife|attack|stalk", ("rain_on_window_night", "los_angeles_night_street")),
        (r"suicide|own life", ("rain_on_window_night", "rainy_street_lights_night", "autumn_leaves_cemetery")),
        (r"hollywood|industry|studio|fame|cameras", ("hollywood_sign", "hollywood_walk_of_fame", "film_projector")),
        (r"television|tv|show|seasons|living rooms|sitcom", ("vintage_tv_living_room", "old_crt_television_static", "child_watching_tv_retro")),
        (r"film|movie|role|cast", ("film_reel_spinning", "film_clapperboard", "old_cinema_marquee", "film_projector"))]


def mood(text):
    for rx, topics in MOOD:
        if re.search(rx, text.lower()):
            v = broll(*[t for t in topics if t not in RESERVED])
            if v:
                return v
    return None


# ================================================================== cold open (fast: one shot per line)
at(0.0, fadein_clip := bclip(broll("vhs_tape") or broll("old_crt_television_static")))
fadein_clip["fadein"] = 1.0
at(line_at("They were children"), P(take("Cameron Boyce", wide=True), move="left"))
at(line_at("on a Saturday morning"), bclip(broll("child_watching_tv_retro", "vintage_tv_living_room")))
at(line_at("in a movie we wore out"), framed(clips_of("Judith Barsi")[2], "THE LAND BEFORE TIME · 1988", "▸ 35mm"))
at(line_at("in a show the whole"), framed(clips_of("Gary Coleman")[2], "DIFF'RENT STROKES · NBC", "▸ 35mm"))
at(line_at("And because they were children"), P(take("Heather O'Rourke"), move="in"))
at(line_at("we assumed they had decades"), bclip(broll("film_reel_spinning", "film_projector")))
at(line_at("Thirty-five young performers"), rollcall(NAMES, "Thirty-five young performers", "never got those decades",
                                                     titleAt=1.6, fillFor=1.5))
at(line_at("One of them died on the very"), P(take("Josh Ryan Evans"), move="in"))
at(line_at("One of them was taken"), P(take("Judith Barsi"), move="out"))
at(line_at("One of them lent her voice"), framed(clips_of("Judith Barsi")[0], "THE LAND BEFORE TIME · 1988", "▸ 35mm"))
at(line_at("and most people never learned"), P(take("Judith Barsi"), move="left"))
at(line_at("And one death on a front"), P(take("Rebecca Schaeffer"), move="in"))
at(line_at("changed American law forever"), bclip(broll("los_angeles_night_street")))
at(line_at("Stay until the end"), bclip(broll("old_crt_television_static", "vhs_tape")))
at(line_at("and chances are"), bclip(broll("polaroid_photos", "old_family_home_video")))
at(line_at("Let's begin with a voice"), bclip(broll("vintage_tv_living_room", "child_watching_tv_retro")))

# ================================================================== the 35
starts = [(p[1] if isinstance(p[1], float) else line_at(p[1], 57.0)) for p in PEOPLE]
OUTRO = line_at("Thirty-five names")
for k, (name, cue, role, years, age, age_cue, ex) in enumerate(PEOPLE):
    t0, t1 = starts[k], (starts[k + 1] if k + 1 < len(PEOPLE) else OUTRO)
    cl = [c for c in clips_of(name) if c not in USED]
    # the card holds the first line(s): at least 4.5 s
    at(t0, castcard(name, k + 1, role, years, age))
    busy = t0 + 4.5
    t_age = line_at(age_cue, t0) if age_cue else None
    t_memo = line_at(ex["memo_at"], t0) if ex.get("memo_at") else None
    t_map = line_at(ex["map"][0], t0) if ex.get("map") else None
    t_quote = None
    if ex.get("quote"):
        t_quote = line_at(ex["quote"][1], t0) if ex["quote"][1] != "They're here" else None
    life = ex.get("life")
    t_life = line_at(life[1][3], t0) if life else None
    special = {t for t in (t_age, t_memo, t_map, t_quote, t_life) if t}
    first_photo = True
    seg_lines = lines_between(t0, t1)
    last_kind = None
    for li, (a, b, text) in enumerate(seg_lines):
        nxt = seg_lines[li + 1][0] if li + 1 < len(seg_lines) else t1
        if a < busy - 0.05 and a not in special:
            continue
        if a == t_life:
            at(a, dict(type="lifeline", img=img(take(name), "reel"), name=name, born=int(years[:4]), died=int(years[-4:]),
                       events=[dict(year=life[0][0], label=life[0][1], age=life[0][2], at=0.8)] +
                              [dict(year=y, label=l, age=ag, at=f"@{c}") for y, l, ag, c in life[1:]]))
            busy = a + 6.0
            continue
        if a == t_age:
            at(a, ageclock(name, age, note=ex.get("note"), date=ex.get("date") or years.replace(" — ", " – ")))
            busy = a + 3.8
            continue
        if a == t_memo:
            at(a, memoriam(name, years, ex.get("memo")))
            busy = a + 5.0
            continue
        if a == t_map:
            m = ex["map"]
            at(a, amap(m[1], m[2], **({"countries": m[3]} if len(m) > 3 else {})))
            busy = a + 4.5
            continue
        if a == t_quote:
            q = ex["quote"][0]
            at(a, quote(q, who=name, bg=take(name), size=84))
            busy = a + 4.0
            continue
        if a < busy - 0.05:
            continue
        if b - a < 1.9 and a + 1.9 < t1:          # too short for its own shot: the previous one holds
            continue
        need = min(nxt, t1) - a
        # footage first: their own role clips (framed / TV, chained when short), B-roll for the mood, else a photograph
        if cl and (last_kind != "framed" or len(cl) > 2):
            v = cl.pop(0)
            more, have = [], dur(v)
            while have < need * 0.9 and cl and len(more) < 2:
                more.append(cl.pop(0)); have += dur(more[-1])
            at(a, tv(v) if ex.get("tv") else framed(v, role.split("  ·  ")[0].upper(), "▸ 35mm", more=more))
            last_kind = "framed"
            continue
        if (last_kind == "photo" and (m := (mood(text) or broll(*GENERIC)))) or (last_kind == "framed" and (m := mood(text))):
            at(a, bclip(m))
            last_kind = "broll"
            continue
        stem = take(name)
        if name in DEPTH and first_photo:
            at(a, depth(stem, subject=(0.5, 0.42), grade="reel", move="in"))
        else:
            at(a, P(stem, move=["in", "left", "out", "right"][len(USED) % 4],
                    **({"name": name, "role": role} if first_photo and not clips_of(name) else {})))
        first_photo = False
        last_kind = "photo"
    if ex.get("memo_end"):
        pass

# Heather O'Rourke's line, set where she says it
at(line_at("Heather O'Rourke said") + 3.0, quote("They're here.", who="Heather O'Rourke · Poltergeist (1982)", bg=take("Heather O'Rourke"),
                                                size=130, highlight=["here"]))

# ================================================================== outro
at(OUTRO, rollcall(NAMES, "Thirty-five names", "thirty-five unfinished stories", fillFor=1.6, titleAt=1.0))
at(line_at("And here's what stays"), B("memorial_candles", "cemetery_flowers", "rain_on_window_night"))
at(line_at("Some were taken by illness"), fresh("Nikita Pearl Waligwa"))
at(line_at("some by violence"), fresh("Rebecca Schaeffer"))
at(line_at("some by accidents"), fresh("Anton Yelchin"))
at(line_at("and far too many"), B("hollywood_sign", "hollywood_walk_of_fame", "film_projector"))
at(line_at("and then forgets them"), B("movie_theater_empty_seats", "film_reel_spinning"))
at(line_at("Laws changed because", OUTRO), P(take("Rebecca Schaeffer"), move="in", name="Rebecca Schaeffer", role="America's first anti-stalking law"))
at(line_at("Foundations exist", OUTRO), P(take("Cameron Boyce"), move="in", name="Cameron Boyce", role="The Cameron Boyce Foundation"))
at(line_at("Lee Thompson Young", OUTRO), fresh("Lee Thompson Young"))
at(line_at("Rob Knox", OUTRO), fresh("Rob Knox"))
at(line_at("and Michael Cuccione", OUTRO), B("box_of_old_photographs", "polaroid_photos", person="Michael Cuccione"))
at(line_at("Their stories did not end"), B("memorial_candles", "cemetery_flowers", "sunset_boulevard", person="Cameron Boyce"))
at(line_at("So the real question"), rollcall(NAMES, "How many will you remember now?", None, fillFor=1.2, titleAt=1.2,
                                             color=list(range(0, 35, 3)), colorAt=2.6, seed=5))
at(line_at("If this video meant"), B("polaroid_photos", "old_family_home_video", "vhs_tape"))
at(line_at("because every one of these"), memoriam("Judith Barsi", "1978 — 1988", "They deserve to be remembered.", fadeout=True))

# ================================================================== editor's pass after final QC
# shots final QC flagged with reason (black frame, somebody else, an unrelated marquee, burnt-in captions) are
# replaced here by time; the rest of the list stays as generated. Mood B-roll and role stills it called "off-topic"
# but that belong to the story are marked qc_ok.
FIX = {
    43.06: lambda: bclip("broll_vhs_tape__pe10599677.mp4"),
    119.38: lambda: P("anton_yelchin__g78316817", move="in"),
    191.47: lambda: framed("brad_renfro__cmp_052_427s.mp4", "THE CURE · 1995", "▸ 35mm"),
    360.9: lambda: P("sawyer_sweeten__g0739ddf3", move="left"),
    446.55: lambda: bclip("broll_rainy_street_lights_night__pe3638386.mp4"),
    524.68: lambda: P("michelle_trachtenberg__g12d06adb", move="in"),
    647.55: lambda: bclip("broll_kids_riding_bikes_suburb__pe3683318.mp4"),
    670.47: lambda: bclip("broll_suburban_house_sunset__pe17972365.mp4"),
    286.09: lambda: P("corey_haim__g290551b1", move="in"),            # an event backdrop logo behind him
}
QC_OK = [9.5, 191.47, 670.47, 40.26, 342.79, 383.81, 406.69, 640.71, 682.71, 827.93]
for k, (cue, sc_) in enumerate(edl.E):
    t = round(float(cue), 2)
    for ft, make in FIX.items():
        if abs(ft - t) < 0.03:
            edl.E[k] = (cue, make())
    if any(abs(q - t) < 0.03 for q in QC_OK):
        edl.E[k][1]["qc_ok"] = True

# every cue here is a time in seconds: put them in order, one shot per moment (a later, hand-placed shot wins)
_seen = {}
for cue, sc in edl.E:
    _seen[round(float(cue), 2)] = (cue, sc)
edl.E[:] = [_seen[k] for k in sorted(_seen)]

edl.main(music=[
    dict(at=None, track="04_Sad_Trio_Somber_Piano_Cello.mp3"),
    dict(at=starts[NAMES.index("Bobby Driscoll")], track="02_Leaving_Home_Somber_Long_Bed.mp3", lead=-1.0),
    dict(at=starts[NAMES.index("Lee Thompson Young")], track="Mark Jubel - Efteraar.mp3", lead=-1.0),
    dict(at=starts[NAMES.index("Rebecca Schaeffer")], track="07_Wounded_Dark_Strings.mp3", lead=-1.0),
    dict(at=starts[NAMES.index("Sammi Kane Kraft")], track="03_Sovereign_Dark_Piano_Bed.mp3", lead=-1.0),
    dict(at=OUTRO, track="05_Despair_and_Triumph_Dark_Piano.mp3", lead=-1.0),
])
