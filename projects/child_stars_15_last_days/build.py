"""
15 MOST FAMOUS Child Stars Who Died in the Last Few Days  (13:15)  -  Final Reel, second video

Built like projects/child_stars_died_too_soon (read its header). Differences: shots cut on the voice's own
sentence starts (word timing, data/words.json), each castcard starts on "Number N" and its name wipes in on the
spoken name; calmer finish (no light leaks, faint grain, slow pushes). Pictures: the shared nostalgia pool.
(The rest of this docstring is the first video's:)

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
    name="15_Most_Famous_Child_Stars_Who_Died_in_the_Last_Few_Days",
    kit=os.environ.get("VIDEO_KIT", f"{SP}/kit"),
    footage=f"{NS}/footage",
    work=f"{SP}/work_cs2",
    data=os.path.join(HERE, "data"),
    out=f"{SP}/out",
    image_dirs=[f"{NS}/src/images"],
    template="finalreel",
    topic="child actors and child stars who died young: childhood nostalgia, classic TV shows and films, their lives and tragic endings",
    music_floor_db=-16.0, music_duck_db=-8.0, sfx_gain=0.5,
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


# the show / film a person is remembered for, when the clip itself is of the show (cast, title, scenes) - archive.org
CTX = {"Hayden Panettiere": ["film_remember_the_titans"], "Kevin Clark": ["film_school_of_rock"],
       "Melanie Watson": ["show_diffrent_strokes"], "Malcolm-Jamal Warner": ["show_cosby_show"],
       "Adam Rich": ["show_eight_is_enough"], "Michelle Trachtenberg": ["film_harriet_the_spy"]}
CAPS = [("remember_the_titans", "REMEMBER THE TITANS · 2000"), ("ice_princess", "ICE PRINCESS · 2005"),
        ("school_of_rock", "SCHOOL OF ROCK · 2003"), ("diffrent_strokes", "DIFF'RENT STROKES"),
        ("cosby", "THE COSBY SHOW · 1984"), ("eight_is_enough", "EIGHT IS ENOUGH · 1977"), ("_cmp_eie", "EIGHT IS ENOUGH · 1979"),
        ("_cmp_hayden", "NASHVILLE · \"TELESCOPE\""), ("harri", "HARRIET THE SPY · 1996"), ("_cmp_turner", "HARRIET THE SPY · 1996"),
        ("party", "AARON'S PARTY · 2000")]


def cap(v, fallback):
    for k, c in CAPS:
        if k in v:
            return c
    return fallback


def clips_of(person):
    """their own clips first, then clips of the show / film they are remembered for"""
    own = [c["video"] for c in edl.CAT if c["video"].startswith(slug(person) + "__cmp_") and ok(c["video"])]
    ctx = [c["video"] for p in CTX.get(person, []) for c in edl.CAT if c["video"].startswith(p + "__") and ok(c["video"])]
    out = []
    for a, b in zip(own + [None] * len(ctx), ctx + [None] * len(own)):     # alternate: them, the show, them ...
        out += [x for x in (a, b) if x and x not in out]
    return out


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


def fresh(person, *topics, role=None):
    """an unused picture of the person, else B-roll - the outro never repeats a shot (role: a nameplate on it)"""
    if any(f not in USED for f in pics(person)):
        return P(take(person), move="in", **({"name": person, "role": role} if role else {}))
    return B(*(topics or ("box_of_old_photographs", "polaroid_photos", "theater_curtain_stage")), person=person)


def B(*topics, person=None):
    """B-roll for one of these topics, else a photograph of `person`"""
    v = broll(*topics)
    return bclip(v) if v else P(take(person or "Judith Barsi"), move="in")
DEPTH = {"Hayden Panettiere", "Malcolm-Jamal Warner", "Liam Payne", "Kim Sae-ron", "Aaron Carter"}


def P(stem, move="in", name=None, role=None, **kw):
    """a photograph: portraits shown whole on their blurred twin, landscapes full frame"""
    if tall(stem):
        kw.setdefault("fit", "contain")
        kw.setdefault("margin", 0.86)
    else:
        kw.setdefault("focus", (0.5, 0.32))
    s = photo(stem, move=move, zoom=kw.pop("zoom", 1.05), grade="reel", **kw)
    if name:
        s["overlays"] = list(s.get("overlays", [])) + [dict(type="nameplate", name=name, role=role or "", at=0.5)]
    return s


def castcard(person, n, role, years, age, **kw):
    stem = take(person, wide=False)
    s = dict(type="castcard", img=img(stem, "reel"), name=person, role=role, years=years, age=age, n=n,
             frameLabel=f"KODAK 5247  ▸ {n:02d}A", at=0.25, lines=2 if len(person) > 18 else 1,
             size=104 if len(person) > 18 else 104)
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


ROLL = {"Malcolm-Jamal Warner": "malcolm_jamal_warner__g158d6792.jpg"}      # a portrait of him alone, not the cast photo


def rollcall(people, title, sub=None, **kw):
    stems = [ROLL.get(p) or pics(p)[0] for p in people if pics(p)]
    s = dict(type="rollcall", imgs=[img(os.path.splitext(f)[0], "reel") for f in stems], names=list(people), cols=7,
             fillFor=kw.pop("fillFor", 2.4), title=title, sub=sub)
    s.update(kw)
    return s


def amap(stops, pins, **kw):
    s = dict(type="map", detail="geo_hi.json", adminCountries=kw.pop("countries", ["USA"]), stops=stops, pins=pins)
    s.update(kw)
    return s


# ------------------------------------------------------------------ the voice's own sentences (word timing)
WORDS = json.load(open(os.path.join(HERE, "data", "words.json"), encoding="utf-8"))
NORM = lambda x: re.sub(r"[^a-z0-9]", "", x.lower())


def _sentences(max_len=7.0, split_comma_over=4.5):
    """(start, end, text) for every sentence the narrator speaks; long ones split at a comma"""
    out, cur = [], []
    for w in WORDS:
        cur.append(w)
        t = w["w"].strip()
        dur_ = cur[-1]["e"] - cur[0]["s"]
        if t.endswith((".", "?", "!")) or (t.endswith(",") and dur_ > split_comma_over) or dur_ > max_len:
            out.append((cur[0]["s"], cur[-1]["e"], " ".join(x["w"] for x in cur))); cur = []
    if cur:
        out.append((cur[0]["s"], cur[-1]["e"], " ".join(x["w"] for x in cur)))
    return out


SRT = _sentences()


def line_at(phrase, after=0.0):
    """start of the first sentence at/after `after` that contains `phrase` (case / punctuation free)"""
    p = NORM(phrase)
    for a, b, t in SRT:
        if a >= after - 0.01 and p in NORM(t):
            return a
    raise KeyError(phrase)


def lines_between(t0, t1):
    return [(a, b, t) for a, b, t in SRT if t0 <= a < t1 - 0.05]


def word_t(token, after=0.0, before=1e9):
    """when the narrator says this word (first time after `after`), else None"""
    k = NORM(token)
    for w in WORDS:
        if after - 0.01 <= w["s"] < before and NORM(w["w"]) == k:
            return w["s"]
    return None


NUMWORD = {11: "eleven", 16: "sixteen", 18: "eighteen", 24: "twentyfour", 28: "twentyeight", 31: "thirtyone", 32: "thirtytwo",
           33: "thirtythree", 34: "thirtyfour", 36: "thirtysix", 39: "thirtynine", 54: "fiftyfour", 57: "fiftyseven"}

# "Number N" in the voice: where each castcard starts, and when the name is spoken
NUMS = [i for i, w in enumerate(WORDS) if NORM(w["w"]) == "number" and WORDS[i]["s"] > 20]


# ------------------------------------------------------------------ the 15
# (name, role / known for, years, age at death, phrase in the sentence that holds the age, extras)
PEOPLE = [
    ("Hayden Panettiere", "Claire Bennet · Heroes", "1989 — 2026", 36, "died at only 36",
     dict(life=[(2000, "Remember the Titans", 11, None), (2005, "Ice Princess", 15, "Ice Princess")],
          map=("found in cardiac arrest", [dict(at=0, lon=-88.0, lat=36.0, scale=2600), dict(at=0.5, lon=-82.4, lat=34.85, scale=14000, d=2.0)],
               [dict(label="Greenville, S.C.", sub="August 16, 2026", lon=-82.4, lat=34.85, at=1.6, side="right")]),
          memo="A girl who could heal from anything.", memo_at="made the loss feel even crueler",
          quote=("Save the cheerleader, save the world.", "Heroes · NBC, 2006", "Heroes"))),
    ("Blake Garrett", "Plug · How to Eat Fried Worms", "DIED 2026", 33, "suddenly at only 33", dict()),
    ("Melanie Watson", "Kathy Gordon · Diff'rent Strokes", "1968 — 2025", 57, "She was 57",
     dict(map=("she died in Colorado Springs", [dict(at=0, lon=-98.0, lat=39.0, scale=2200), dict(at=0.5, lon=-104.82, lat=38.83, scale=12000, d=2.0)],
               [dict(label="Colorado Springs", sub="December 26, 2025", lon=-104.82, lat=38.83, at=1.6, side="right")]))),
    ("Malcolm-Jamal Warner", "Theo Huxtable · The Cosby Show", "1970 — 2025", 54, "He was 54",
     dict(life=[(1984, "The Cosby Show", 14, None), (1996, "Malcolm & Eddie", 26, "starring in Malcolm"),
                (2015, "a Grammy", 45, "winning a Grammy")],
          map=("family trip to Costa Rica", [dict(at=0, lon=-80.0, lat=20.0, scale=1500), dict(at=0.5, lon=-84.1, lat=9.9, scale=9000, d=2.0)],
               [dict(label="Costa Rica", sub="July 20, 2025", lon=-84.1, lat=9.9, at=1.6, side="right")], ["CRI"]),
          memo="He left behind a wife and an eight-year-old daughter.", memo_at="a little girl now almost")),
    ("Millena Brandão", "child actress · Brazil", "DIED 2025", 11, "only 11 years old",
     dict(map=("Brazilian child actress", [dict(at=0, lon=-55.0, lat=-12.0, scale=900), dict(at=0.5, lon=-51.0, lat=-14.0, scale=1400, d=2.0)],
               [dict(label="Brazil", sub="May 2, 2025", lon=-51.0, lat=-14.0, at=1.6, side="right")], ["BRA"]),
          memo="She should have been worrying about homework.", memo_at="She should have been worrying")),
    ("Michelle Trachtenberg", "Harriet the Spy · Buffy · Gossip Girl", "1985 — 2025", 39, "She was 39",
     dict(quote=("There are as many ways to live as there are people in the world.", "Harriet the Spy · 1996", "Spy"))),
    ("Sophie Nyweide", "Mammoth · Bella · Noah", "2000 — 2025", 24, "at only 24", dict()),
    ("Kim Sae-ron", "The Man from Nowhere", "2000 — 2025", 24, "She was 24",
     dict(map=("was found dead in her", [dict(at=0, lon=127.5, lat=36.5, scale=3200), dict(at=0.5, lon=126.98, lat=37.56, scale=16000, d=2.0)],
               [dict(label="Seoul", sub="February 16, 2025", lon=126.98, lat=37.56, at=1.6, side="right")], ["KOR"]),
          memo="Adored as a child. Grieved as an adult.", memo_at="A country that had adored her")),
    ("Hudson Meek", "young Baby · Baby Driver", "2008 — 2024", 16, "He was 16",
     dict(map=("hometown of Vestavia Hills", [dict(at=0, lon=-87.5, lat=33.2, scale=5000), dict(at=0.5, lon=-86.79, lat=33.45, scale=20000, d=2.0)],
               [dict(label="Vestavia Hills, Ala.", sub="December 21, 2024", lon=-86.79, lat=33.45, at=1.6, side="right")]),
          memo="Every performance he gave now exists in the past tense.", memo_at="Every performance he ever gave")),
    ("Liam Payne", "One Direction", "1993 — 2024", 31, "He was 31",
     dict(map=("third-floor hotel balcony", [dict(at=0, lon=-62.0, lat=-30.0, scale=1300), dict(at=0.5, lon=-58.38, lat=-34.6, scale=12000, d=2.0)],
               [dict(label="Buenos Aires", sub="October 16, 2024", lon=-58.38, lat=-34.6, at=1.6, side="right")], ["ARG"]))),
    ("Adam Rich", "Nicholas Bradford · Eight Is Enough", "1968 — 2023", 54, "home at 54", dict()),
    ("Jansen Panettiere", "The Perfect Game · Martha Speaks", "1994 — 2023", 28, "at 28", dict()),
    ("Aaron Carter", "Aaron's Party", "1987 — 2022", 34, "home at 34",
     dict(life=[(1997, "First album", 9, None), (2000, "Aaron's Party", 13, "By 13")],
          map=("bathtub of his Lancaster", [dict(at=0, lon=-119.0, lat=36.0, scale=3500), dict(at=0.5, lon=-118.14, lat=34.7, scale=16000, d=2.0)],
               [dict(label="Lancaster, Calif.", sub="November 5, 2022", lon=-118.14, lat=34.7, at=1.6, side="right")]),
          memo="Famous for a quarter of a century. An adult for sixteen years.", memo_at="He had been famous for a quarter")),
    ("Tyler Sanders", "Just Add Magic: Mystery City", "2004 — 2022", 18, "only 18", dict()),
    ("Kevin Clark", "Freddy Jones · School of Rock", "1988 — 2021", 32, "He was 32",
     dict(map=("riding his bicycle through Chicago", [dict(at=0, lon=-88.5, lat=41.5, scale=6000), dict(at=0.5, lon=-87.65, lat=41.9, scale=20000, d=2.0)],
               [dict(label="Chicago", sub="May 26, 2021", lon=-87.65, lat=41.9, at=1.6, side="right")]),
          memo="The future ended on an ordinary street.", memo_at="Eighteen years later")),
]
NAMES = [p[0] for p in PEOPLE]
assert len(NUMS) >= len(PEOPLE), f"found {len(NUMS)} 'Number' words for {len(PEOPLE)} people"
NUMS = NUMS[:len(PEOPLE)]

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


MOOD = [(r"ocean|water|drown|submersion", ("costa_rica_ocean_waves",)),
        (r"stadium|band|album|concert|boy band|x factor|music", ("concert_stadium_crowd_lights", "recording_studio_microphone")),
        (r"drum|school of rock", ("drum_kit_drummer",)),
        (r"hospital|doctor|cardiac|heart|surgery|transplant", ("hospital_corridor",)),
        (r"bicycle|car|vehicle|road", ("chicago_street_bicycle", "los_angeles_night_street")),
        (r"balcony|hotel", ("balcony_hotel_night", "buenos_aires_city_night")),
        (r"seoul|korea|cafe|café", ("seoul_city_night",)),
        (r"magazine|covers|headlines", ("magazine_covers_stack",)),
        (r"school|algebra|homework|church", ("empty_classroom",)),
        (r"television|sitcom|episodes|show|series|soap", ("tv_studio_cameras", "vintage_tv_living_room", "old_crt_television_static"))] + MOOD
GENERIC = GENERIC + ("tv_studio_cameras", "magazine_covers_stack", "recording_studio_microphone", "empty_classroom", "hudson_river_town",
                     "colorado_springs_mountains", "sao_paulo_city")

# ================================================================== cold open (fast: a shot per phrase)
T_ROLL = line_at("15 of the most famous")
T_SUB = line_at("If you believe their stories", T_ROLL)


def _chunks(t0, t1, lo=1.5, hi=2.3):
    """cut points every ~2 s on word boundaries (a pause or a comma ends a chunk early)"""
    out, a = [], t0
    for w in WORDS:
        if w["s"] < t0 or w["e"] > t1:
            continue
        d = w["e"] - a
        if d >= hi or (d >= lo and w["w"].rstrip()[-1:] in ",.?!"):
            out.append(a)
            a = w["e"] + 0.02
    if t1 - a > 1.0:
        out.append(a)
    return out


def _fr(person):
    c = [v for v in clips_of(person) if v not in USED]
    return framed(c[0], cap(c[0], person.upper()), "▸ 35mm") if c else P(take(person), move="in")


OPEN = [lambda: P(take("Aaron Carter"), move="in"), lambda: _fr("Malcolm-Jamal Warner"), lambda: P(take("Hayden Panettiere"), move="left"),
        lambda: _fr("Kevin Clark"), lambda: B("magazine_covers_stack", "vhs_tape"), lambda: P(take("Liam Payne"), move="out"),
        lambda: _fr("Adam Rich"), lambda: P(take("Kim Sae-ron"), move="in"), lambda: _fr("Aaron Carter"),
        lambda: P(take("Michelle Trachtenberg"), move="right"), lambda: B("magazine_covers_stack", "old_crt_television_static"),
        lambda: P(take("Hudson Meek"), move="in"), lambda: _fr("Hayden Panettiere"), lambda: P(take("Malcolm-Jamal Warner"), move="left")]
for k, a in enumerate(_chunks(0.0, T_ROLL - 0.05)):
    at(max(0.0, a), OPEN[k % len(OPEN)]())
at(T_ROLL, rollcall(NAMES, "Fifteen child stars", "gone far too soon", fillFor=1.4, cols=5,
                    titleAt=max(0.8, (word_t("15", T_ROLL) or T_ROLL + 1.0) - T_ROLL)))
at(T_SUB, B("film_projector", "film_reel_spinning", "vhs_tape"))

# ================================================================== the 15
OUTRO = line_at("These 15 stars came from") if any("These 15 stars" in t for _, _, t in SRT) else line_at("stars came from different")
starts = [WORDS[i]["s"] for i in NUMS]
for k, (name, role, years, age, age_cue, ex) in enumerate(PEOPLE):
    t0, t1 = starts[k], (starts[k + 1] if k + 1 < len(PEOPLE) else OUTRO)
    t_name = word_t(name.split()[0], t0, t0 + 4.0) or WORDS[min(NUMS[k] + 2, len(WORDS) - 1)]["s"]
    cl = [c for c in clips_of(name) if c not in USED]
    # the card starts on "Number N" (only the rank shows), the name wipes in as it is spoken, the rest after it
    a0 = max(0.3, t_name - t0 - 0.3)
    at(t0, castcard(name, k + 1, role, years, age, rankAt=0.15, at=a0, roleAt=a0 + 1.3, yearsAt=a0 + 1.9, ageAt=a0 + 2.4))
    busy = t_name + 4.4
    def _t(phrase):
        try:
            return line_at(phrase, t0)
        except KeyError:
            print(f"   [{name}] no sentence with {phrase!r} - skipped")
            return None
    t_age = _t(age_cue) if age_cue else None
    t_memo = _t(ex["memo_at"]) if ex.get("memo_at") else None
    t_map = _t(ex["map"][0]) if ex.get("map") else None
    t_quote = word_t(ex["quote"][2], t0, t1) if ex.get("quote") else None   # set after the loop, on the word
    life = ex.get("life")
    t_life = _t(life[1][3]) if life else None
    special = {t for t in (t_age, t_memo, t_map, t_life) if t and t < t1}
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
            # the number counts up to the age as it is said, never before
            tw = word_t(str(age), a, b + 0.5) or word_t(NUMWORD.get(age, "-"), a, b + 0.5) or a + 1.0
            s0 = max(a, tw - 1.4)
            if a == t_map:                     # the place and the age in one sentence: the map first, then the count
                m = ex["map"]
                at(a, amap(m[1], m[2], **({"countries": m[3]} if len(m) > 3 else {})))
                s0 = max(a + 2.6, tw - 1.4)
            at(s0, ageclock(name, age, note=ex.get("note"), date=ex.get("date") or years.replace(" — ", " – "),
                            at=max(0.25, tw - s0 - 0.9)))
            busy = s0 + 3.8
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
            at(a, tv(v) if ex.get("tv") else framed(v, cap(v, role.upper()), "▸ 35mm", more=more))
            last_kind = "framed"
            if have < need - 1.0 and a + have + 2.0 < t1:      # out of footage before the line ends: a photograph takes over
                at(a + have, P(take(name), move="in"))
                last_kind = "photo"
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
    if t_quote:
        q = ex["quote"]
        tq = t_quote + 0.4
        keep = {round(x, 2) for x in special}
        nxt_sp = min([x for x in special if x > tq] + [t1])
        hold = min(tq + 4.5, nxt_sp)
        edl.E[:] = [(c, sc) for c, sc in edl.E if not (tq - 1.2 < float(c) < hold and sc.get("type") not in
                                                        ("ageclock", "memoriam", "map", "lifeline", "castcard"))]
        at(tq, quote(q[0], who=q[1], bg=take(name), size=84))
        # the quote holds ~4.5 s, then the story goes on with a photograph (unless a device already starts there)
        nxt_ = [a for a, _, _ in SRT if tq + 3.0 <= a < t1]
        if nxt_ and not any(tq < float(c) <= nxt_[0] + 0.01 for c, _ in edl.E if float(c) != tq):
            at(nxt_[0], P(take(name), move="in"))

# Jansen's story: his sister, named where the voice says her name
_tj = starts[NAMES.index("Jansen Panettiere")]
at(line_at("Three years later, Hayden", _tj), P(take("Hayden Panettiere"), move="in", name="Hayden Panettiere", role="his sister · 1989 — 2026"))

# ================================================================== outro
ot = lines_between(OUTRO, 1e9)
OUT = {"These 15 stars": lambda: rollcall(NAMES, "Fifteen stars", "fifteen unfinished stories", fillFor=1.4, titleAt=1.0, cols=5),
       "One sold out stadiums": lambda: fresh("Aaron Carter", role="sold-out stadiums at 13"),
       "One carried": lambda: B("film_reel_spinning", "old_cinema_marquee", "film_projector"),
       "One was still a child": lambda: fresh("Millena Brandão", role="11 years old"),
       "Some were taken by illness": lambda: fresh("Jansen Panettiere", role="a hidden heart condition"),
       "accidents": lambda: B("costa_rica_ocean_waves", "chicago_street_bicycle", "rainy_street_lights_night"),
       "addiction": lambda: B("rain_on_window_night", "rainy_street_lights_night"),
       "But every one": lambda: B("memorial_candles", "autumn_leaves_cemetery", "cemetery_flowers"),
       # "watch them exactly as they were": the wall of faces again, in colour this time, held over "The screen kept its promise"
       "We can press play": lambda: rollcall(NAMES, "Exactly as they were.", None, fillFor=1.2, cols=5, seed=5,
                                             titleAt=max(1.0, (word_t("were", 780.0) or 783.0) - line_at("We can press play") - 0.2),
                                             color=list(range(15)), colorAt=2.0),
       "They gave us": lambda: memoriam("Hayden Panettiere", "1989 — 2026", "They gave us their childhoods.", fadeout=True)}
for a, b, text in ot:
    for key, make in OUT.items():
        if NORM(key) in NORM(text):
            at(a, make())
            break

# ================================================================== editor's pass after final QC
# s000: the first face is Aaron Carter as a boy (not the adult); s012: Hayden's music video under the Heroes line;
# s122: a bicycle B-roll that "career" pulled in by its letters - a photograph of Tyler instead
FIX = {0.0: lambda: _fr("Aaron Carter"),          # a boy on screen, from his own clips
       43.22: lambda: B("tv_studio_cameras", "vintage_tv_living_room", "old_crt_television_static"),
       696.2: lambda: P(take("Tyler Sanders"), move="left")}
QC_OK = [767.7]          # "accidents on water": the Costa Rica sea from Malcolm-Jamal Warner's story - it belongs here
for k, (cue, sc_) in enumerate(edl.E):
    for ft, make in FIX.items():
        if abs(ft - float(cue)) < 0.03:
            edl.E[k] = (cue, make())
    if any(abs(q - float(cue)) < 0.03 for q in QC_OK):
        edl.E[k][1]["qc_ok"] = True

# every cue here is a time in seconds: put them in order, one shot per moment (a later, hand-placed shot wins)
_seen = {}
for cue, sc in edl.E:
    _seen[round(float(cue), 2)] = (cue, sc)
edl.E[:] = [_seen[k] for k in sorted(_seen)]

if os.environ.get("CUES"):                       # CUES=1 python build.py plan : print the generated cue list
    for cue, sc in edl.E:
        print(f"  {float(cue):7.2f}  {sc.get('type'):9s} {sc.get('video') or sc.get('name') or sc.get('text') or ''}")

edl.main(music=[
    dict(at=None, track="04_Sad_Trio_Somber_Piano_Cello.mp3"),
    dict(at=starts[NAMES.index("Malcolm-Jamal Warner")], track="02_Leaving_Home_Somber_Long_Bed.mp3", lead=-1.0),
    dict(at=starts[NAMES.index("Kim Sae-ron")], track="Mark Jubel - Efteraar.mp3", lead=-1.0),
    dict(at=starts[NAMES.index("Adam Rich")], track="03_Sovereign_Dark_Piano_Bed.mp3", lead=-1.0),
    dict(at=OUTRO, track="05_Despair_and_Triumph_Dark_Piano.mp3", lead=-1.0),
])
