"""
Why 20,000 Hasidic Jews Were Told To Stay Silent About Crime?  (18:46)  -  template: The Record (templates/record)

An investigation built from the record: rulings and guidance as transcript pages, figures as ledger rows with their
source, the rule itself as a lexicon entry, the mechanism (family -> rabbi -> police, the delay) as a chain, the
posters as a night wall, the names the DA withheld as a redacted list, the ten files as dockets.

Footage: media/hasidic/pool - the Hasidic Drive library (Brooklyn / Crown Heights / Mea Shearim street and
community footage), Wikimedia Commons (places, texts, posters), Pexels / Pixabay B-roll on the exact subject
(courtroom, gavel, phones, police lights, documents, ballots). QC faceless mode: no talking heads, vloggers,
influencers or interviews. Every clip is shorter than 5 s (longer lines are chained); stock always plays inside the
evidence viewer (casebox) with an exhibit number and caption. No faces of the victim, no private names anywhere.

Facts: data/facts.txt (sourced). Nothing is written on screen before the narrator says it: every device is timed on
its words (word timing: data/words.json).

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
HS = f"{SP}/hasidic"
TOPIC = ("the Hasidic and Haredi Jewish community of Brooklyn: the rule of mesirah, silence about crime and child abuse, "
         "rabbinical courts, a Brooklyn sex-abuse trial, the District Attorney, community pressure and posters")
edl.setup(
    name="Why_20000_Hasidic_Jews_Were_Told_To_Stay_Silent_About_Crime",
    kit=os.environ.get("VIDEO_KIT", f"{SP}/kit"),
    footage=f"{HS}/footage",
    work=f"{SP}/work_hm",
    data=os.path.join(HERE, "data"),
    out=f"{SP}/out",
    image_dirs=[f"{HS}/pool/images"],
    template="record",
    topic=TOPIC,
    music_floor_db=-16.0, music_duck_db=-8.0, sfx_gain=0.6,
)

QC = json.load(open(f"{HS}/pool/qc.json", encoding="utf-8"))
USED = set()


def ok(f):
    return f in QC and not QC[f].get("reject")


IMGS = sorted(f for f in os.listdir(f"{HS}/pool/images") if ok(f))


def ph(*slugs, reuse=True):
    """the next unused photograph whose name starts with one of these topics (in that order)"""
    for sl in slugs:
        for f in IMGS:
            if f.startswith(sl + "__") and f not in USED:
                USED.add(f)
                return os.path.splitext(f)[0]
    if reuse:
        for sl in slugs:
            for f in IMGS:
                if f.startswith(sl + "__"):
                    return os.path.splitext(f)[0]
    return None


# ------------------------------------------------------------------ footage
_IDX = {c["video"]: k for k, c in enumerate(edl.CAT)}
DESC = {v: (QC.get(v, {}).get("desc", "") + " " + " ".join(QC.get(v, {}).get("tags", []))).lower() for v in _IDX}
COMM = [v for v in _IDX if not v.startswith("broll_") and ok(v)]
CATS = {
    "street": r"street|sidewalk|walk|crosswalk|pedestrian",
    "gather": r"gather|table|hall|sukkah|tent|crowd|wedding",
    "study": r"torah|book|read|study|shelves|scroll",
    "poster": r"poster",
    "school": r"school|classroom|desk|worksheet",
    "family": r"famil|child|toddler|stroller|girls|playground|kitchen|baby",
    "night": r"night",
    "jerusalem": r"jerusalem|stone wall|cobblestone",
}


USES = {}


def comm(*cats):
    """a community clip of one of these kinds - unused first, then the least used (its next 2.6 s are shown)"""
    for c in cats:
        for v in COMM:
            if v not in USED and re.search(CATS[c], DESC[v]) and not (c != "jerusalem" and "measheari" in v.lower() and "poster" not in c):
                USED.add(v)
                USES[v] = 1
                return v
    pool = [v for v in COMM if any(re.search(CATS[c], DESC[v]) for c in cats)] or COMM
    pool = [v for v in pool if (edl.CAT[_IDX[v]]["e"] - edl.CAT[_IDX[v]]["s"]) - 2.6 * USES.get(v, 0) > 2.4] or pool
    v = min(pool, key=lambda x: USES.get(x, 0))
    USES[v] = USES.get(v, 0) + 1
    USED.add(v)
    return v


def skip_of(v):
    n = USES.get(v, 1) - 1
    c = edl.CAT[_IDX[v]]
    return min(2.6 * n, max(0.0, (c["e"] - c["s"]) - 2.6))


BROLL = {}
for v in _IDX:
    if v.startswith("broll_") and ok(v):
        BROLL.setdefault(v.split("__")[0][6:], []).append(v)


def stock(*topics):
    for t in topics:
        for v in BROLL.get(t, []):
            if v not in USED:
                USED.add(v)
                return v
    return None


BOX = [250, 110, 1420, 799]
EXH = [0]
CAPTION = {"empty_courtroom": "A COURTROOM · RECONSTRUCTION", "judge_gavel": "THE COURT", "courthouse_steps": "THE COURTHOUSE",
           "smartphone_taking_photo": "A PHONE RAISED · RECONSTRUCTION", "hand_holding_phone_dialing": "THE CALL", "police_car_lights_night": "THE POLICE",
           "police_officers_line": "CLOSING RANKS", "old_documents_archive": "THE RECORDS", "newspaper_printing_press": "THE PRESS",
           "ballot_box_voting": "THE VOTE", "church_interior": "A CHURCH", "university_campus_night": "A UNIVERSITY",
           "closed_door_hallway": "BEHIND CLOSED DOORS", "candle_dark_room": "", "child_silhouette_window": "", "family_dinner_table": "A FAMILY",
           "williamsburg_bridge": "WILLIAMSBURG BRIDGE · BROOKLYN", "brooklyn_street": "BROOKLYN"}


def casebox(video, caption=None, source=None, then=()):
    """footage inside the evidence viewer - stock never plays plain"""
    EXH[0] += 1
    USED.add(video)
    s = clip(_IDX[video], grade="record", skip=skip_of(video) if video in USES else 0.0, then=tuple(_IDX[m] for m in then))
    s.update(inset=BOX, no_texture=True)
    topic = video.split("__")[0][6:] if video.startswith("broll_") else None
    cap = caption if caption is not None else (CAPTION.get(topic, "") if topic else "BROOKLYN · ARCHIVE FOOTAGE")
    s["overlays"] = [dict(type="casebox", box=BOX, exhibit=f"EXHIBIT {EXH[0]:02d}", caption=cap, source=source, tc0=37 * EXH[0], at=0)]
    return s


def full(video, place=None, sub=None, src=None):
    USED.add(video)
    s = clip(_IDX[video], grade="record", zoom=1.03, skip=skip_of(video) if video in USES else 0.0)
    ov = []
    if place:
        ov.append(dict(type="place", name=place, sub=sub, at=0.5))
    if src:
        ov.append(dict(type="source", text=src, at=0.4))
    if ov:
        s["overlays"] = ov
    return s


def P(stem, move="in", place=None, sub=None, src=None, place_at=0.5, **kw):
    s = photo(stem, move=move, zoom=kw.pop("zoom", 1.06), grade="record", **kw)
    ov = []
    if place:
        ov.append(dict(type="place", name=place, sub=sub, at=place_at))
    if src:
        ov.append(dict(type="source", text=src, at=0.4))
    if ov:
        s["overlays"] = ov
    return s


def S(*topics, cap=None, src=None, alt=None):
    """stock in the casebox, else a community clip"""
    v = stock(*topics)
    if v:
        return casebox(v, cap, src)
    return casebox(comm(*(alt or ("street",))), cap)


# ------------------------------------------------------------------ the voice: sentences and words
WORDS = json.load(open(os.path.join(HERE, "data", "words.json"), encoding="utf-8"))
NORM = lambda x: re.sub(r"[^a-z0-9]", "", x.lower())   # noqa: E731


def _sentences(max_len=7.0, split_comma_over=4.5):
    out, cur = [], []
    for w in WORDS:
        cur.append(w)
        t = w["w"].strip()
        d = cur[-1]["e"] - cur[0]["s"]
        if t.endswith((".", "?", "!")) or (t.endswith(",") and d > split_comma_over) or d > max_len:
            out.append((cur[0]["s"], cur[-1]["e"], " ".join(x["w"] for x in cur)))
            cur = []
    if cur:
        out.append((cur[0]["s"], cur[-1]["e"], " ".join(x["w"] for x in cur)))
    return out


SRT = _sentences()


def L(phrase, after=0.0):
    """start of the first sentence (at/after `after`) that contains `phrase`"""
    p = NORM(phrase)
    for a, b, t in SRT:
        if a >= after - 0.01 and p in NORM(t):
            return a
    raise KeyError(phrase)


def Wt(word, after=0.0, before=1e9):
    """when the narrator says this word (first time after `after`)"""
    k = NORM(word)
    for w in WORDS:
        if after - 0.01 <= w["s"] < before and NORM(w["w"]) == k:
            return w["s"]
    raise KeyError(word)


def rel(word, t0, after=None):
    return round(Wt(word, after if after is not None else t0) - t0, 2)


BUSY = []


def put(t, scene, hold):
    """a device at t that owns the picture for `hold` seconds"""
    at(t, scene)
    BUSY.append((t, t + hold))


def busy(t):
    return any(a - 0.05 <= t < b for a, b in BUSY)


FILES = ["THE COMMUNITY", "THE RULE", "THE HISTORY", "THE RULINGS", "THE MACHINE", "THE TRIAL", "THE PRICE", "THE CITY",
         "THE OTHER SIDE", "THE MIRROR"]


def docket(n, title, line, bg, hold=4.6, t=None, phrase=None, size=128):
    t = t if t is not None else L(phrase)
    put(t, dict(type="docket", n=n, of=len(FILES), kicker=FILES[n - 1], title=title, line=line, files=FILES,
                img=img(bg, "record") if bg else None, at=0.3, size=size), hold)


# ================================================================== the devices, on their words
# ---- cold open: the girl on the stand
put(0.0, S("empty_courtroom", cap="KINGS COUNTY SUPREME COURT · RECONSTRUCTION"), 3.8)
put(L("It is December 2012"), P(ph("kings_county_supreme_court"), move="in", place="Kings County Supreme Court", sub="BROOKLYN, N.Y. · DECEMBER 2012"), 4.0)
put(Wt("telling", 6), S("judge_gavel"), 3.8)
put(L("Behind her, in the public benches"), S("empty_courtroom", "courthouse_steps", cap="THE PUBLIC BENCHES · RECONSTRUCTION"), 2.6)
put(Wt("lift", 12), S("smartphone_taking_photo", cap="A PHONE RAISED · RECONSTRUCTION"), 4.2)
put(L("Not for the court"), S("hand_holding_phone_dialing", "smartphone_taking_photo"), 2.0)
put(Wt("so", 20.5), full(comm("street"), place="Williamsburg, Brooklyn", sub="40.71° N · 73.96° W"), 6.0)
put(L("Court officers catch them"), S("police_car_lights_night", cap="ARRESTED IN THE COURTROOM"), 4.0)
put(L("Sit with what that takes"), S("candle_dark_room", cap=""), 1.9)
put(L("In the middle of a trial about a child"), S("child_silhouette_window", cap=""), 6.0)
put(L("It is to make sure everyone back home"), full(comm("street", "night")), 4.5)

# ---- FILE 01  the community
docket(1, "A world of its own", "BROOKLYN, NEW YORK", ph("williamsburg_brooklyn_hasidic"), hold=6.2, phrase="The community she comes from")
t = L("Around a quarter of a million")
put(t, dict(type="counts", kicker="HAREDI JEWS IN NEW YORK CITY", items=[dict(value="250,000", label="PEOPLE", at=rel("quarter", t))], cw=1200, numSize=230), 3.4)
t = Wt("most", 55)
put(t, dict(type="map", detail="geo_hi.json", adminCountries=["USA"],
            stops=[dict(at=0, lon=-73.98, lat=40.70, scale=26000), dict(at=0.4, lon=-73.965, lat=40.672, scale=90000, d=2.2)],
            pins=[dict(label="Williamsburg", lon=-73.957, lat=40.708, at=rel("handful", t), side="right"),
                  dict(label="Crown Heights", lon=-73.944, lat=40.669, at=rel("handful", t) + 0.5, side="right"),
                  dict(label="Borough Park", lon=-73.991, lat=40.633, at=rel("handful", t) + 1.0, side="left")]), 4.4)
t = L("These are streets with their own ambulance")
put(t, P(ph("hatzolah"), move="right", place="Hatzolah", sub="THE COMMUNITY'S OWN AMBULANCE SERVICE"), Wt("volunteer", t) - t)
t2 = Wt("volunteer", t)
put(t2, P(ph("shomrim_brooklyn"), move="left", place="Shomrim", sub="VOLUNTEER PATROL"), Wt("courts", t2) - t2)
put(Wt("courts", t2), P(ph("talmud_page", "mishneh_torah_manuscript"), move="in"), 3.2)
put(L("and by most ordinary measures"), full(comm("street"), place="Borough Park, Brooklyn", sub="40.63° N · 73.99° W"), 4.6)
t = L("In 2009, the Brooklyn District Attorney")
put(t, P(ph("charles_j_hynes", "brooklyn_municipal_building"), move="in", place="Charles J. Hynes", sub="KINGS COUNTY DISTRICT ATTORNEY · 1990 – 2013",
          src="KOL TZEDEK PROGRAM · 2009", place_at=rel("Attorney", t)), 7.6)
t = L("and in time announced ninety-five")
put(t, dict(type="counts", kicker="KOL TZEDEK · THE DA'S SPECIAL UNIT", items=[dict(value=95, label="ARRESTS ANNOUNCED", at=rel("ninetyfive", t) if False else 0.9)],
            cw=900, numSize=250), 3.5)
t = L("Then The New York Times went through")
put(t, S("newspaper_printing_press", "old_documents_archive", cap="THE NEW YORK TIMES · 2012", src="THE NEW YORK TIMES · 2012"), 6.8)
put(L("Case after case had quietly collapsed"), P(ph("brooklyn_municipal_building", "kings_county_supreme_court"), move="left", src="THE NEW YORK TIMES · 2012"), 3.4)
put(L("And the reason was nearly always"), full(comm("family", "street")), 4.6)

# ---- the reflex
put(L("You carry a reflex"), S("hand_holding_phone_dialing", cap="THE CALL"), 3.6)
t = L("Something happens to your child")
put(t, dict(type="chain", kicker="THE REFLEX", title="What you would do",
            nodes=[dict(label="SOMETHING HAPPENS", sub="to your child", at=rel("happens", t)), dict(label="THE PHONE", sub="before the thought has finished", at=rel("phone", t)),
                   dict(label="THE POLICE", sub="no permission · no calculation", at=rel("permission", t))]), 11.0)
put(L("Now set that reflex against"), P(ph("williamsburg_brooklyn_hasidic", "lee_avenue_williamsburg"), move="in"), 5.0)
t = L("that making that call is itself a sin")
put(t, dict(type="transcript", header="AN IDEA PRESSED IN FROM BIRTH", source="what the reflex is set against",
            lines=["Making that call is itself a sin.", "The real danger is [[the phone in your hand]].", "Lifting it could cost your family everything."],
            lineAt=[rel("making", t), rel("danger", t), rel("lifting", t)], hiAt=rel("phone", t, Wt("danger", t)) + 0.2), 14.1)
put(L("So how does calling the police"), S("police_car_lights_night"), 2.9)
put(L("And who told a community of tens of thousands"), full(comm("gather")), 6.9)

# ---- FILE 02  the rule
docket(2, "A word for the informer", "THE RULE BEHIND THE SILENCE", ph("talmud_page", "mishneh_torah_manuscript"), hold=5.0, phrase="Reach for the obvious answer")
t = L("and it has a name")
put(t, dict(type="lexicon", word="mesirah", hebrew="מסירה", pron="/ me·si·RAH /", pos="NOUN · HEBREW",
            hebAt=rel("mesirah", t), at=rel("mesirah", t),
            defs=["to hand over", "the one who does it: a [[moser]], an informer"],
            defAt=[rel("hand", t), rel("moser", t)], hiAt=rel("moser", t) + 0.3), Wt("informer", t) + 1.2 - t)
put(L("For most of Jewish history, this rule"), P(ph("mishneh_torah_manuscript", "talmud_page"), move="left"), 4.4)
t = L("For centuries across Europe")
put(t, dict(type="map", detail="geo_hi.json", adminCountries=["ESP", "GBR", "RUS", "POL", "DEU", "FRA"],
            stops=[dict(at=0, lon=10, lat=50, scale=900), dict(at=0.4, lon=12, lat=50, scale=1100, d=2.5)],
            pins=[dict(label="Spain", lon=-3.7, lat=40.4, at=1.0, side="left"), dict(label="England", lon=-1.5, lat=52.5, at=1.4, side="left"),
                  dict(label="Russian Empire", lon=30.3, lat=55.0, at=1.8, side="right")]), 4.0)
put(L("A Jew handed to a hostile government"), P(ph("expulsion_of_the_jews", "persecution_of_jews_medieval", "shtetl", "old_documents_archive"), move="in"), 5.2)
put(Wt("or", 195.5), P(ph("persecution_of_jews_medieval", "expulsion_of_the_jews", "shtetl", "talmud_page"), move="out"), 3.8)
t = L("So the law set hard")
put(t, dict(type="transcript", header="THE OLD LAW · DIN MOSER", source="as summarised from the classical sources",
            lines=["You do not deliver", "a fellow Jew", "[[to the outside power]]."],
            lineAt=[rel("deliver", t), rel("fellow", t), rel("outside", t)], hiAt=rel("outside", t) + 0.4), 5.4)
put(L("In its oldest and harshest form"), P(ph("shulchan_aruch", "mishneh_torah_manuscript", "talmud_page"), move="in"), 6.4)
put(L("placed in theory beside a man"), S("closed_door_hallway", cap=""), 4.2)
t = L("That is the rule this entire story turns on")
put(t, P(ph("williamsburg_brooklyn_hasidic"), move="in"), 6.0)
t = L("The rule was built for a world")
put(t, dict(type="chain", kicker="THE COLLISION", title="Built for one world, used in another",
            nodes=[dict(label="THE STATE", sub="once the predator", at=rel("state", t)), dict(label="THE RULE", sub="do not hand over a Jew", gate=True, at=rel("rule", t)),
                   dict(label="THE ACCUSED", sub="once innocent", at=rel("innocent", t))]), 6.2)
t = L("It was never written for a case")
put(t, dict(type="chain", kicker="TODAY", title="The same rule, turned around",
            nodes=[dict(label="THE AUTHORITY", sub="protecting a child", at=rel("protect", t)), dict(label="THE RULE", sub="do not hand over a Jew", gate=True, at=rel("Jewish", t) + 0.4),
                   dict(label="THE ABUSER", sub="the one who hurt her", at=rel("hurt", t))], blockAt=rel("hurt", t) + 0.5), 8.3)

# ---- FILE 03  the history
docket(3, "Where the rule came from", "WHY THE FEAR WAS REAL", ph("shtetl", "expulsion_of_the_jews", "talmud_page"), hold=6.3, phrase="You cannot feel the grip")
t = L("For a thousand years, in country after country")
put(t, dict(type="docketline", kicker="A THOUSAND YEARS", title="The knock at the door", **{"from": 1000, "to": 1950}, ticks=[1000, 1200, 1400, 1600, 1800],
            events=[dict(year=1100, when="1000s", label="Communities under hostile rulers", at=rel("thousand", t) + 0.6),
                    dict(year=1290, label="England expels its Jews", at=rel("country", t) + 0.5),
                    dict(year=1492, label="Spain expels its Jews", at=rel("country", t, Wt("country", t) + 0.3) + 0.5, up=False),
                    dict(year=1881, label="Pogroms in the Russian Empire", at=rel("knock", t), hi=True)]), 8.2)
put(L("Informers from inside their own ranks"), P(ph("persecution_of_jews_medieval", "expulsion_of_the_jews", "old_documents_archive"), move="in"), 6.8)
put(L("Families were ruined"), S("old_documents_archive", cap=""), 4.0)
put(L("Out of centuries of that"), P(ph("shtetl", "talmud_page"), move="left"), 7.1)
put(L("walls, in its own rabbinical courts"), P(ph("beth_din", "talmud_page", "shulchan_aruch"), move="in"), 6.0)
put(L("For most of history, that instinct"), full(comm("study", "gather")), 5.9)
t = L("And understand how seriously")
put(t, P(ph("mishneh_torah_manuscript", "shulchan_aruch"), move="in"), 8.0)
t = L("In its classical form, a habitual moser")
put(t, dict(type="transcript", header="CLASSICAL LAW · THE INFORMER", source="din moser and din rodef",
            lines=["A habitual moser", "is placed in the same category", "as a [[rodef]], a pursuer,", "a man actively trying to kill you."],
            lineAt=[rel("habitual", t), rel("same", t), rel("rodeph", t), rel("man", t)], hiAt=rel("pursuer", t)), 9.3)
put(L("In theory, the texts allowed"), P(ph("shulchan_aruch", "talmud_page", "mishneh_torah_manuscript"), move="out"), 7.6)
put(L("Nobody is carrying out"), full(comm("street")), 3.2)
put(L("But a rule that once ranked"), S("candle_dark_room", cap=""), 6.6)
put(L("It travels down the generations"), full(comm("family", "gather")), 9.8)
put(L("The trouble begins"), full(comm("street", "night")), 9.5)

# ---- FILE 04  the rulings
docket(4, "What the rabbis ruled", "WHAT THE RELIGIOUS AUTHORITIES SAID", ph("770_eastern_parkway"), hold=10.0, phrase="And this is where the angry version")
t = L("In two thousand eleven, a rabbinical court")
put(t, P(ph("770_eastern_parkway", "crown_heights_brooklyn"), move="in", place="Crown Heights, Brooklyn", sub="770 EASTERN PARKWAY · CHABAD", src="JTA · JULY 2011"), 6.8)
t = L("Where there is evidence of abuse")
put(t, dict(type="transcript", header="RULING · BEIS DIN OF CROWN HEIGHTS", source="JULY 2011 · as reported by JTA",
            lines=["Where there is evidence of abuse,", "mesirah does not apply.", "[[One is forbidden to remain silent]]", "in such a situation."],
            lineAt=[0.2, rel("mesirah", t), rel("forbidden", t), rel("situation", t) - 0.4], hiAt=rel("silent", t)), 10.0)
t = L("The Rabbinical Council of America said")
put(t, dict(type="transcript", header="STATEMENT · RABBINICAL COUNCIL OF AMERICA", source="as reported by JTA, 2011",
            lines=["If one becomes aware of an instance of child abuse,", "one is obligated to refer the matter", "[[to the secular authorities immediately]],",
                   "as the prohibition of mesirah does not apply."],
            lineAt=[rel("learns", t), rel("obligated", t), rel("secular", t), rel("informing", t)], hiAt=rel("secular", t) + 0.3, size=36), 12.8)
put(L("On paper, in the text itself"), P(ph("talmud_page", "shulchan_aruch"), move="left"), 4.6)
put(L("Reporting an abuser is not betrayal"), S("hand_holding_phone_dialing", cap=""), 4.6)
t = L("Some authorities went further still")
put(t, P(ph("mishneh_torah_manuscript", "talmud_page"), move="in"), 5.4)
t = L("If an informer is condemned")
put(t, dict(type="chain", kicker="THE COMMUNITY'S OWN LOGIC", title="Who is the pursuer?",
            nodes=[dict(label="THE INFORMER", sub="condemned as a danger", at=rel("informer", t)), dict(label="THE ABUSER", sub="harms the next child", at=rel("abuser", t)),
                   dict(label="THE RODEF", sub="the one you must stop", gate=True, at=rel("rodeph", t))]), 14.8)
put(L("By the community's own ancient reasoning"), S("hand_holding_phone_dialing", "smartphone_taking_photo", cap="THE CALL"), 6.8)
put(L("It is the man he is calling about"), full(comm("street")), 2.0)
put(L("In strict legal terms"), P(ph("shulchan_aruch", "talmud_page", "mishneh_torah_manuscript"), move="out"), 5.5)

# ---- FILE 05  the machine
docket(5, "Why the silence held", "A RULE DOES NOT LIVE ONLY ON PAPER", ph("lee_avenue_williamsburg", "williamsburg_brooklyn_hasidic"), hold=6.6, phrase="So if the law had settled it")
put(L("It lives in what a community"), full(comm("gather")), 4.3)
put(L("And there the machinery"), full(comm("street", "night")), 2.9)
t = L("One of the largest Haredi organizations")
put(t, dict(type="transcript", header="GUIDANCE · AGUDATH ISRAEL OF AMERICA", source="2011 · as summarised by JTA / J. Weekly",
            lines=["An observant Jew should not take", "an abuse allegation to law enforcement", "[[without first consulting a rabbi]]",
                   "to weigh whether the suspicion is strong enough."],
            lineAt=[rel("observant", t), rel("allegation", t), rel("consulting", t), rel("weigh", t)], hiAt=rel("rabbi", t, Wt("consulting", t)), size=38), 16.7)
put(L("Whatever the intention behind it"), full(comm("study", "gather")), 7.4)
put(L("power to whichever rabbi"), P(ph("lee_avenue_williamsburg", "williamsburg_brooklyn_hasidic"), move="in"), 3.0)
t = L("And circling all of it")
put(t, dict(type="wall", count=7, at=0.2, every=0.32, word="מוסר", gloss="MOSER · INFORMER", bigAt=rel("moser", t) - 0.3, wordAt=rel("moser", t) + 0.2), 8.3)
put(L("A clean ruling in a law book"), P(ph("shulchan_aruch", "talmud_page"), move="left"), 2.8)
put(L("The fear of your children"), full(comm("family", "school")), 4.4)
put(Wt("your", 481.5), full(comm("street")), 5.2)
put(L("That fear does not sit down"), S("closed_door_hallway", cap=""), 4.2)
t = L("To see how that punishment travels")
put(t, casebox(comm("poster"), "MEA SHEARIM · POSTERS ON THE WALLS"), 4.7)
t = L("They are called Pashkevilin")
put(t, dict(type="lexicon", word="pashkevil", hebrew="פשקוויל", pron="/ pash·KEH·vil /  ·  plural pashkevilin", pos="NOUN · YIDDISH",
            hebAt=0.3, at=0.2, defs=["a broadsheet pasted on walls and shop fronts", "the community's own [[front page]]"],
            defAt=[rel("broadsheets", t), rel("front", t)], hiAt=rel("front", t) + 0.3), 10.3)
put(L("A name printed on one"), P(ph("pashkevil", "mea_shearim_posters"), move="in", place="Pashkevilin", sub="WALL POSTERS · MEA SHEARIM, JERUSALEM", src="JTA · 2020"), 5.6)
put(L("It moves through the schools"), full(comm("school", "study")), 5.1)
put(L("And in a world where marriages are arranged"), full(comm("gather", "family")), 6.9)
put(L("that one word can quietly close"), P(ph("pashkevil", "mea_shearim_posters"), move="out"), 4.2)
put(L("Nobody needs to issue a threat"), full(comm("night", "street")), 5.0)
t = L("Tell a family to consult a rabbi")
put(t, dict(type="chain", kicker="THE GATEKEEPER", title="Consult a rabbi first",
            nodes=[dict(label="A FAMILY", sub="a frightened parent", at=rel("family", t)), dict(label="A RABBI", sub="weighs the suspicion", gate=True, at=rel("rabbi", t)),
                   dict(label="THE POLICE", sub="if it ever gets there", at=rel("police", t))],
            delay=1, delayAt=rel("delay", t), delayLabel="DELAY", blockAt=rel("cold", t)), Wt("cold", t) + 1.5 - t + 0.0)
put(L("You do not have to forbid a report"), S("closed_door_hallway", "candle_dark_room", cap=""), 7.0)

# ---- FILE 06  the trial
docket(6, "The case in that courtroom", "KINGS COUNTY · BROOKLYN", ph("kings_county_supreme_court"), hold=5.6, phrase="Nothing shows the machine running")
t = L("The accused was Nechemia Weberman")
put(t, P(ph("lee_avenue_williamsburg", "williamsburg_brooklyn_hasidic"), move="in", place="Williamsburg, Brooklyn", sub="THE SATMAR COMMUNITY"), 6.5)
put(L("a man with real standing"), full(comm("street")), 5.0)
put(L("A girl who had been sent to him"), full(comm("school", "family")), 5.6)
put(L("across years of so-called"), S("closed_door_hallway", cap=""), 4.4)
put(L("And she did the thing"), S("courthouse_steps", cap="THE COURTHOUSE"), 3.7)
put(L("She went to the authorities"), S("empty_courtroom", "judge_gavel", cap="OPEN COURT · RECONSTRUCTION"), 5.0)
t = L("In December two thousand twelve, a jury")
put(t, dict(type="counts", kicker="PEOPLE v. WEBERMAN · DECEMBER 2012",
            items=[dict(value=59, label="COUNTS · GUILTY ON ALL", at=rel("fiftynine", t) if False else rel("all", t)),
                   dict(value=103, label="YEARS IN PRISON", at=rel("hundred", t), strikeAt=rel("cut", t))],
            after="later cut on appeal", afterAt=rel("cut", t) + 0.3), 10.9)
t = L("Look at what formed around the trial")
put(t, dict(type="docketline", kicker="AROUND THE TRIAL · 2012", title="What formed around it", **{"from": 0, "to": 4}, ticks=[],
            events=[dict(year=0.3, when="DINNER", label="A fundraiser for his defense", at=rel("fundraising", t)),
                    dict(year=1.4, when="BRIBE", label="A charge: trying to buy the family off", at=rel("buy", t), up=False),
                    dict(year=2.6, when="KOSHER", label="A certificate torn off a restaurant", at=rel("kosher", t)),
                    dict(year=3.7, when="PHOTOS", label="Men arrested for photographing her", at=rel("photographing", t), up=False, hi=True)]), 34.2)
put(L("She told the truth"), full(comm("street")), 4.9)
put(L("It was to protect the man"), S("closed_door_hallway", cap=""), 2.2)
put(L("For many who watched it unfold"), P(ph("kings_county_supreme_court"), move="in", src="BROOKLYN EAGLE · DNAINFO · 2012"), 7.8)
put(L("was dragged fully into daylight"), S("courthouse_steps", "judge_gavel", cap=""), 7.8)
put(L("If you want the kind of story"), S("old_documents_archive", cap="THE RECORD"), 7.6)
put(L("this channel is worth following"), full(comm("street", "night")), 4.0)

# ---- FILE 07  the price
docket(7, "The real punishment", "WHAT NO COURT CAN TOUCH", ph("borough_park_brooklyn", "williamsburg_brooklyn_hasidic"), hold=9.8, phrase="And that is the part no court")
put(L("In a world this sealed"), full(comm("street")), 4.2)
t = L("Your school, your job")
put(t, dict(type="ripple", center="A FAMILY",
            rings=[dict(label="SCHOOL", at=rel("school", t), cutAt=rel("loss", t) + 0.0),
                   dict(label="JOB", at=rel("job", t), cutAt=rel("loss", t) + 0.25),
                   dict(label="MARRIAGE", at=rel("marriage", t), cutAt=rel("loss", t) + 0.5),
                   dict(label="FRIENDS", at=rel("friends", t), cutAt=rel("loss", t) + 0.75),
                   dict(label="HOME", at=rel("roof", t), cutAt=rel("loss", t) + 1.0)],
            aloneAt=rel("loss", t) + 1.2), Wt("loss", t) + 2.2 - t)
put(L("Your other children may never be matched"), full(comm("family", "gather")), 2.4)
put(L("Your family may be pushed out"), full(comm("street", "night")), 4.0)
put(L("Weighed against that"), S("closed_door_hallway", "candle_dark_room", cap=""), 7.6)
put(L("This is why the district attorney's cases"), S("old_documents_archive", cap="CASE FILES"), 4.0)
put(L("Not because the crimes were invented"), P(ph("brooklyn_municipal_building", "kings_county_supreme_court"), move="in", src="THE NEW YORK TIMES · 2012"), 8.8)
t = L("You can watch it in the numbers")
put(t, dict(type="tally", kicker="KOL TZEDEK · THE CLOSED CASES", title="What the unit's numbers show", source="The New York Times, 2012",
            rows=[dict(label="Cases that had closed", value=53, text="~50", at=rel("closed", t)),
                  dict(label="Thrown out", value=13, text="~12", at=rel("dozen", t)),
                  dict(label="Quiet plea deals", value=35, text="most", at=rel("plea", t)),
                  dict(label="Reached a jury", value=5, text="5", at=rel("jury", t), hi=True),
                  dict(label="Probation, reduced or nothing", value=24, text="~24", at=rel("two", t, Wt("Nearly", t)), hi=True)]), 25.7)
t = L("The reporters could only match")
put(t, dict(type="tally", kicker="KOL TZEDEK · THE 95 ARRESTS", title="What could be checked", source="The New York Times, 2012",
            rows=[dict(label="Arrests announced", value=95, at=rel("95", t)), dict(label="Matched to public records", value=47, at=rel("47", t), hi=True)],
            stamp="LITTLE TO DO WITH THE UNIT", stampAt=rel("credit", t), stampX=960, stampY=760), 12.0)
put(L("And this is the trap outsiders"), full(comm("street")), 4.0)
put(L("When people picture refusing to cooperate"), full(comm("gather", "study")), 7.5)
t = L("They do not picture a person who speaks little English")
put(t, dict(type="transcript", header="WHAT LEAVING MEANS", source="for someone raised wholly inside",
            lines=["Little English.", "Almost no secular schooling.", "[[No outside network]] of any kind."],
            lineAt=[rel("little", t), rel("secular", t), rel("network", t)], hiAt=rel("network", t) + 0.3), 8.7)
put(L("They do not picture that person being cut loose"), S("closed_door_hallway", cap=""), 5.3)
put(L("For someone raised wholly inside"), S("williamsburg_bridge", cap="WILLIAMSBURG BRIDGE · THE WAY OUT"), 5.1)
put(L("It is emigrating to a country"), full(comm("night", "street")), 4.0)
put(L("Seen that way, the silence"), S("candle_dark_room", "child_silhouette_window", cap=""), 3.5)
put(L("It is the clear-eyed arithmetic"), full(comm("street")), 6.4)

# ---- FILE 08  the city
docket(8, "Met halfway", "THE OUTSIDE INSTITUTIONS", ph("brooklyn_municipal_building"), hold=6.7, phrase="And it was not only the community that bent")
put(L("The same district attorney who ran"), P(ph("charles_j_hynes", "brooklyn_municipal_building"), move="in", place="Charles J. Hynes", sub="KINGS COUNTY DISTRICT ATTORNEY · 1990 – 2013"), 5.0)
t = L("For defendants from this community")
put(t, dict(type="redacted", header="DEFENDANTS · KINGS COUNTY", source="ORTHODOX DEFENDANTS · NAMES NOT RELEASED", rows=7, labels=["DEFENDANT"],
            tails=["CONVICTED", "PLEA", "PROBATION", "CONVICTED", "PLEA"], at=rel("release", t) - 1.2, every=0.32, stamp="NAMES WITHHELD",
            stampAt=rel("courtesy", t)), 10.4)
put(L("The stated reason was"), P(ph("brooklyn_municipal_building", "kings_county_supreme_court"), move="left", src="THE FORWARD · JTA"), 5.3)
put(L("The effect, critics said"), S("courthouse_steps", "judge_gavel", cap=""), 8.4)
t = L("When a community can move tens of thousands")
put(t, dict(type="ballot", kicker="BLOC VOTING", title="Tens of thousands of votes, one bloc", blocAt=rel("single", t), note="even those who must hold it to account step carefully"), 9.3)
put(L("The silence, then"), full(comm("street")), 6.7)
put(L("These communities often vote"), S("ballot_box_voting", cap="THE VOTE"), 7.5)
t = L("A candidate who wins an endorsement")
put(t, dict(type="chain", kicker="THE BLOC", title="How a neighbourhood votes",
            nodes=[dict(label="AN ENDORSEMENT", sub="from the leading rabbis", at=rel("endorsement", t)),
                   dict(label="ONE BLOC", sub="a whole neighbourhood's ballots", at=rel("ballots", t), gate=True),
                   dict(label="THE OFFICIAL", sub="wins - or loses them as fast", at=rel("lose", t))]), 10.5)
put(L("That turns a religious minority"), P(ph("brooklyn_municipal_building", "williamsburg_brooklyn_hasidic"), move="in"), 8.4)
put(L("Whatever is happening behind those walls"), S("closed_door_hallway", cap="BEHIND THOSE WALLS"), 6.8)

# ---- FILE 09  the other side
docket(9, "Not one single mind", "THE OTHER SIDE", ph("borough_park_brooklyn", "crown_heights_brooklyn"), hold=7.0, phrase="It would be easy to stop there")
put(L("This community is not one single mind"), full(comm("street")), 5.0)
put(L("The very same years produced survivors"), full(comm("night")), 5.3)
put(L("Advocates and whole organizations"), full(comm("study", "gather")), 7.0)
put(L("Rabbis who said out loud"), P(ph("talmud_page", "mishneh_torah_manuscript"), move="in"), 8.8)
t = L("The clearest rulings")
put(t, dict(type="docketline", kicker="WHAT CHANGED", title="Pulled into the open", **{"from": 0, "to": 4}, ticks=[],
            events=[dict(year=0.3, when="RULINGS", label="Abuse must be reported - from religious authorities", at=rel("rulings", t)),
                    dict(year=1.4, when="REPORTS", label="More report than a decade ago", at=rel("report", t), up=False),
                    dict(year=2.6, when="SUPPORT", label="Help for those who leave", at=rel("Organizations", t)),
                    dict(year=3.7, when="NAMES", label="Survivors under their own names", at=rel("Survivors", t), up=False, hi=True)]), 34.3)
put(L("None of this was handed down"), full(comm("street")), 8.4)
put(L("And the fear sitting under all of it"), P(ph("persecution_of_jews_medieval", "shtetl", "expulsion_of_the_jews"), move="in"), 11.0)
put(L("None of that unmakes"), S("child_silhouette_window", "candle_dark_room", cap=""), 3.0)
put(L("All of it explains why"), full(comm("street", "night")), 7.9)

# ---- FILE 10  the mirror
docket(10, "Every closed institution", "THE SAME RULE · WITHOUT A NAME", None, hold=10.5, phrase="And if you are tempted to file")
put(L("A church that transfers"), S("church_interior", cap="A CHURCH"), 3.8)
put(L("A university that buries"), S("university_campus_night", cap="A UNIVERSITY"), 4.0)
put(L("A police department that closes"), S("police_officers_line", "police_car_lights_night", cap="A POLICE DEPARTMENT"), 3.7)
put(L("A family that tells a child"), S("family_dinner_table", "child_silhouette_window", cap="A FAMILY"), 5.2)
put(L("Every closed institution on Earth"), S("closed_door_hallway", cap=""), 5.2)
put(L("The unspoken understanding"), full(comm("night")), 6.2)
t = L("What this community holds")
put(t, dict(type="lexicon", word="mesirah", hebrew="מסירה", pron="/ me·si·RAH /", pos="A REFLEX WITH A NAME", hebAt=0.3, at=0.2,
            defs=["written down, [[fought over for centuries]]"], defAt=[rel("written", t)], hiAt=rel("fought", t) + 0.2), 10.1)
put(L("The rest of us are running"), S("police_officers_line", "courthouse_steps", cap=""), 5.7)
put(L("So before you pass sentence"), full(comm("family", "street")), 7.2)
put(L("was never truly about one community"), full(comm("night")), 3.3)
put(L("It is about what truth costs"), S("candle_dark_room", cap=""), 5.8)
t = L("If speaking meant losing all of it")
put(t, dict(type="ripple", center="YOU",
            rings=[dict(label="FAMILY", at=rel("family", t), cutAt=rel("certain", t) + 0.0), dict(label="FRIENDS", at=rel("friends", t), cutAt=rel("certain", t) + 0.3),
                   dict(label="WORK", at=rel("work", t), cutAt=rel("certain", t) + 0.6), dict(label="EVERY FACE", at=rel("face", t), cutAt=rel("certain", t) + 0.9)],
            aloneAt=rel("certain", t) + 1.2), Wt("certain", t) + 2.0 - t)
t = L("genuinely certain")
put(t, S("hand_holding_phone_dialing", "smartphone_taking_photo", cap="THE CALL"), 3.4)
put(L("Say it honestly"), full(comm("street")), 7.9)
put(L("And somewhere in your own life"), S("closed_door_hallway", "candle_dark_room", cap=""), 9.5)
t = L("You have simply never been forced")
put(t, dict(type="docket", n=10, of=10, kicker="THE RECORD", title="Say it out loud.", line="", files=FILES, at=rel("out", t), size=120), 6.0)

# ================================================================== the rest: every line not owned by a device
MOOD = [(r"court|jury|trial|testif|verdict|convicted|sentenced|judge", lambda: S("judge_gavel", "empty_courtroom", "courthouse_steps")),
        (r"phone|call|photograph", lambda: S("hand_holding_phone_dialing", "smartphone_taking_photo")),
        (r"police|arrest|officer|law enforcement|authorit", lambda: S("police_car_lights_night", "police_officers_line")),
        (r"record|document|report|times|cases", lambda: S("old_documents_archive", "newspaper_printing_press")),
        (r"vote|ballot|candidate|endorse", lambda: S("ballot_box_voting")),
        (r"rabbi|rabbinical|law|text|ruling|halakh|informer|moser|mesirah", lambda: P(ph("talmud_page", "shulchan_aruch", "mishneh_torah_manuscript"), move="in")),
        (r"child|famil|parent|daughter|son", lambda: full(comm("family"))),
        (r"school|english|educat", lambda: full(comm("school"))),
        (r"silen|quiet|secret|door|wall", lambda: S("closed_door_hallway", "candle_dark_room"))]


def filler(text, k):
    for rx, mk in MOOD:
        if re.search(rx, text.lower()):
            return mk()
    pstem = ph("williamsburg_brooklyn_hasidic", "lee_avenue_williamsburg", "borough_park_brooklyn", "crown_heights_brooklyn", "satmar",
               "770_eastern_parkway", "hatzolah", "shomrim_brooklyn", reuse=False)
    return P(pstem, move=["in", "left", "right", "out"][k % 4]) if (pstem and k % 2) else full(comm("street", "gather"))


for k, (a, b, text) in enumerate(SRT):
    if not busy(a):
        at(a, filler(text, k))

# every cue is a time in seconds: order them, one shot per moment (a later, hand-placed shot wins)
_seen = {}
for cue, sc in edl.E:
    _seen[round(float(cue), 2)] = (cue, sc)
edl.E[:] = [_seen[k] for k in sorted(_seen)]

# ================================================================== no clip runs 5 s: a longer hold is cut into short shots
END = WORDS[-1]["e"] + 4.0
for _ in range(6):
    add = []
    for i, (cue, sc) in enumerate(edl.E):
        nxt = float(edl.E[i + 1][0]) if i + 1 < len(edl.E) else END
        if sc.get("type") == "clip" and nxt - float(cue) > 4.8:
            boxed = "inset" in sc
            topic = None
            v0 = edl.CAT[sc["cat"]]["video"] if "cat" in sc else ""
            if v0.startswith("broll_"):
                topic = v0.split("__")[0][6:]
            nv = stock(topic) if topic else None
            if nv:
                nx = casebox(nv, sc["overlays"][0].get("caption") if boxed and sc.get("overlays") else None)
            else:
                pstem = ph("williamsburg_brooklyn_hasidic", "lee_avenue_williamsburg", "borough_park_brooklyn", "crown_heights_brooklyn",
                           "770_eastern_parkway", "satmar", "hatzolah", reuse=False)
                nx = P(pstem, move=["in", "left", "right", "out"][len(add) % 4]) if pstem else full(comm("street", "gather", "night"))
            add.append((round(float(cue) + 4.4, 2), nx))
    if not add:
        break
    edl.E.extend(add)
    _seen = {}
    for cue, sc in edl.E:
        _seen[round(float(cue), 2)] = (cue, sc)
    edl.E[:] = [_seen[k] for k in sorted(_seen)]

# ================================================================== editor's pass
# s021: the Commons search for the DA returned a census page - the court building instead, labelled on the word;
# s089: a Crown Heights crime-scene photo under the gatekeeper line - a Williamsburg street instead
FIX = {72.98: lambda: P("kings_county_supreme_court__wm67269858", move="in", place="Downtown Brooklyn",
                        sub="KINGS COUNTY DISTRICT ATTORNEY · 2009", src="KOL TZEDEK PROGRAM · 2009", place_at=1.4),
       460.12: lambda: P("williamsburg_brooklyn_hasidic__wm63991997", move="left"),
       # final QC: a seascape phone, POV walking shots read as vlogs, a Romanian Satmar town, a phone at a shelf
       15.56: lambda: P("empty_courtroom__pe14766052", move="in"),
       41.52: lambda: P("williamsburg_brooklyn_hasidic__wm63992098", move="left"),
       142.56: lambda: P("lee_avenue_williamsburg__wm85681661", move="in"),
       409.882: lambda: P("hand_holding_phone_dialing__pe7346611", move="in"),
       522.62: lambda: P("pashkevil__wm140614695", move="in"),
       587.98: lambda: P("lee_avenue_williamsburg__wm83630839", move="right"),
       789.841: lambda: P("mea_shearim_posters__wm159295706", move="in"),
       806.121: lambda: P("williamsburg_bridge__pe13653997", move="in"),
       828.62: lambda: P("brooklyn_courthouse__wm65602649", move="left"),
       891.78: lambda: P("kings_county_supreme_court__wm80250911", move="in"),
       913.862: lambda: P("brooklyn_courthouse__wm80250918", move="in"),
       1055.46: lambda: P("old_documents_archive__pe51191", move="in"),
       1071.8: lambda: P("judge_gavel__pe6077447", move="left")}
for k, (cue, sc_) in enumerate(edl.E):
    for ft, make in FIX.items():
        if abs(ft - float(cue)) < 0.03:
            edl.E[k] = (cue, make())

if os.environ.get("CUES"):
    for cue, sc in edl.E:
        print(f"  {float(cue):7.2f}  {sc.get('type'):10s} {sc.get('title') or sc.get('kicker') or ''}")

edl.main(music=[
    dict(at=None, track="07_Wounded_Dark_Strings.mp3"),
    dict(at=L("Reach for the obvious answer"), track="03_Sovereign_Dark_Piano_Bed.mp3", lead=-1.0),
    dict(at=L("And this is where the angry version"), track="02_Leaving_Home_Somber_Long_Bed.mp3", lead=-1.0),
    dict(at=L("Nothing shows the machine running"), track="07_Wounded_Dark_Strings.mp3", lead=-1.0),
    dict(at=L("And it was not only the community that bent"), track="03_Sovereign_Dark_Piano_Bed.mp3", lead=-1.0),
    dict(at=L("And if you are tempted to file"), track="05_Despair_and_Triumph_Dark_Piano.mp3", lead=-1.0),
])
