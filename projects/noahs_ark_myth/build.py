"""
Myth or Reality? Hunting for the REAL Noah's Ark | The Search for History's Greatest Mystery
Faceless investigative documentary - edit decision list and build.

Look: "expedition" theme - an explorer's field journal that turns into a courtroom.
Part one and two read like a hunt: an antique parchment map, ruled journal pages, the
hunters' case files. Parts three to five are a trial: numbered evidence tags (EXHIBIT A-D),
the scales of justice for the prosecution and the defence, a split-flap scoreboard, and a
two-column REALITY / MYTH verdict sheet. Warm sepia grade, brass and oxblood, light grain.
Music sits far under the narrator (see edl.setup below).

    python build.py plan | prep | stills [ids] | render [ids] | mix | final | all
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "docu"))

import edl                       # noqa: E402
from edl import *                # noqa: E402,F401,F403  (the shot helpers)

SP = os.environ.get("VIDEO_ROOT", os.environ.get("NOAH_ROOT", os.path.join(HERE, "..", "..", "media")))
edl.setup(
    name="Noahs_Ark_Myth_or_Reality",
    kit=os.environ.get("NOAH_KIT", f"{SP}/kit"),
    footage=os.environ.get("NOAH_FOOTAGE", f"{SP}/footage"),
    work=os.environ.get("NOAH_WORK", f"{SP}/work3"),
    data=os.path.join(HERE, "data"),
    out=os.environ.get("NOAH_OUT", f"{SP}/out"),
    image_dirs=[f"{SP}/footage/images/approved", f"{SP}/work/ind", f"{SP}/footage/images/candidates"],
    theme="expedition", grade="warmsepia", grain=2.0,
    # the bed sits ~21 dB under the voice in the gaps and ~31 dB under it while he speaks
    music_floor_db=-21.0, music_duck_db=-10.0, sfx_gain=0.55,
)

DURUPINAR = (44.2317, 39.4403)
ARARAT = (44.2983, 39.7019)
TENDUREK = (43.87, 39.37)
SIVAS = (37.035, 39.745)
TENNESSEE = (-86.4, 35.9)
SYDNEY = (151.18, -33.87)

GOLD, RED, CYAN, GREEN = "#C8963E", "#9E2B25", "#2F6F7E", "#5E8A3E"
GPR = "cand_252"
GPR_CROP = (0.0, 0.17, 1.0, 1.0)
WYATT = dict(grade="bw", crop=(0.0, 0.0, 0.5, 0.78))
C46 = (0.16, 0.01, 0.84, 0.99)          # the 1960 photo without its margin and label


def tag(text, sub, x, y, at, rot=0.0, **kw):
    """a manila evidence tag"""
    return dict(k="tag", text=text, sub=sub, x=x, y=y, at=at, rot=rot, **kw)


def note(text, x, y, at, rot=0.0, w=420, **kw):
    return dict(k="note", text=text, x=x, y=y, at=at, rot=rot, w=w, **kw)


def hand(text, x, y, at, size=54, w=900, **kw):
    """handwriting straight onto the journal page"""
    return dict(k="text", text=text, x=x, y=y, at=at, size=size, w=w, font="Caveat", color="#2A1E12", **kw)


def journal(items, **kw):
    return collage(items, bg="paper", **kw)


def desk(items, **kw):
    return collage(items, bg="cork", **kw)


def exhibit(letter, what, photo_name, at_tag=0.1, crop=None, grade=None, w=860):
    """opening card for one of the four exhibits: the photo, then its tag"""
    return desk([pc(photo_name, 1180, 540, w, rot=2, at=0.0, crop=crop, grade=grade),
                 tag(f"EXHIBIT {letter}", what, 470, 520, at_tag, rot=-5, w=520, size=74, subSize=34)], z1=1.04)


def reclass(claim, finding, photo_name, at_find, crop=None):
    """one of Wyatt's exhibits, re-labelled by the lab"""
    return journal([pc(photo_name, 600, 520, 780, rot=-2, at=0.0, crop=crop),
                    tag(claim, "Wyatt's exhibit", 1400, 360, 0.3, rot=4, w=560, size=52),
                    tag("FINDING", finding, 1400, 680, at_find, rot=-3, w=560, size=52, color=GREEN)])


def scales(title, items, left="THE CASE FOR", right="THE CASE AGAINST", **kw):
    return dict(type="scales", title=title, left=dict(title=left, color=GOLD), right=dict(title=right, color=CYAN),
                items=items, **kw)


def pan(side, text, at, w=1, **kw):
    return dict(side=side, text=text, at=at, w=w, **kw)


def verdict(items, **kw):
    s = dict(type="verdict", left=dict(title="REALITY", sub="what is real", color=GREEN),
             right=dict(title="MYTH", sub="at least so far", color=RED), items=items)
    s.update(kw)
    return s


def vi(side, text, at, **kw):
    return dict(side=side, text=text, at=at, **kw)


def board(title, rows, **kw):
    return dict(type="scoreboard", title=title, rows=rows, **kw)


def mapc(**kw):
    return dict(type="map", **kw)


# =================================================================== cold open
at(0.0, clip(598, grade="doc", zoom=1.03, overlays=[dict(type="fadein", d=1.2)]))
at("where the grass grows greener", spot("cand_01", center=[0.46, 0.47], radius=[0.12, 0.36], label="Greener than anywhere around it",
                                         hit=0.4, grade="doc", zoom=1.12))
at("From the ground, you'd walk right past it", clip(22, zoom=1.04))
at("But from the air", clip(504, grade="doc", zoom=1.02))
at("that has started arguments for sixty-six years", words([
    W_("66 YEARS", y=430, at="@sixty-six years", size=210, color=GOLD),
    W_("OF ARGUMENTS", y=640, at="@sixty-six years", size=110)], bg="cand_089"))
at("the outline of a ship", collage([
    pc("ind2_01", 960, 540, 1560, rot=0, at=0.0, pad=0, tape=False, grade="doc"),
    strip("A LONG HULL", 960, 150, at="@A long hull", rot=-1.5, size=40),
    dict(k="arrow", **{"from": [330, 230]}, to=[640, 330], at="@A pointed bow", bend=40, color=RED),
    strip("A POINTED BOW", 330, 190, at="@A pointed bow", rot=-2, size=40),
    dict(k="arrow", **{"from": [1620, 900]}, to=[1300, 800], at="@A rounded stern", bend=-40, color=RED),
    strip("A ROUNDED STERN", 1600, 960, at="@A rounded stern", rot=2, size=40)], bg="cork", z1=1.03))
at("Five hundred and fifteen feet from end to end", stat("515 FT", "END TO END", "about 157 metres", bg="cand_089", countFor=1.3))
at("the same length you get if you convert", clip(480, grade="none", zoom=1.03))
at("using one particular ancient ruler", journal([
    dict(k="cut", img=cutout("vintage_open_book.png", red=False), x=560, y=560, h=520, at=0.0),
    strip("Genesis 6:15 — 300 cubits long", 1270, 420, at=0.2, size=40, rot=-1),
    strip("× ONE particular cubit", 1270, 560, at="@one particular", size=40, rot=1),
    dict(k="circle", x=1320, y=560, rx=260, ry=60, at="@ancient ruler", color=RED)]))
at("And this September", clip(371, zoom=1.04, chip="September 2026", chip_at=0.3))
at("for the first time in history", words([
    W_("FOR THE FIRST TIME IN HISTORY", y=430, at=0.0, size=100),
    W_("SOMEONE DRILLED INTO IT.", y=610, at="@someone drilled into it", size=140, color=GOLD)], bg="cand_31",
    overlays=[dict(type="flash", at="@drilled into it")]))

at("So here are the three questions", dict(type="ledger", lines=[
    dict(text="Three questions —", at=0.2, y=170, size=58, color="#6b4a22"),
    dict(text="I.   A ship — or a coincidence of geology?", at="@Is that shape a ship", y=320, size=64),
    dict(text="II.  What lies underneath it?", at="@What did the drills", y=460, size=64)]))
at("What did the drills and scanners", clip(49, zoom=1.04, then=(127,)))
at("And if this isn't Noah's Ark", dict(type="ledger", lines=[
    dict(text="Three questions —", at=-2, y=170, size=58, color="#6b4a22"),
    dict(text="I.   A ship — or a coincidence of geology?", at=-2, y=320, size=64),
    dict(text="II.  What lies underneath it?", at=-2, y=460, size=64),
    dict(text="III. If not the ark — then what is it?", at=0.15, y=600, size=64, color="#8a1a10")],
    circle=dict(x=800, y=640, rx=480, ry=70, at="@why does it look like that")))
at("Stay until the end", clip(421, zoom=1.03, chip="The last answer is the most interesting one", chip_at="@the last answer"))
at("If you're new here", clip(56, zoom=1.04))
at("and we tell you what's proven", words([
    W_("PROVEN.", y=320, at="@what's proven", size=130, color=GREEN),
    W_("CLAIMED.", y=520, at="@what's claimed", size=130, color=GOLD),
    W_("STILL UNKNOWN.", y=720, at="@still unknown", size=130, color="#D9C9A8")], bg="cand_082"))
at("Subscribe if that's your kind of channel", clip(147, zoom=1.04))

# =================================================================== part one: the hunt
at("Let's begin with the hunt itself", dict(type="chapter", n="01", kicker="PART ONE", title="THE HUNT", img=img("cand_46", crop=C46), move="in", zoom=1.12))
at("The formation sits on the slopes", mapc(detail="geo_hi.json", stops=[
        dict(at=0, lon=36.5, lat=39.2, scale=2900),
        dict(at="@in Turkey's", lon=43.6, lat=39.5, scale=15000, d=2.6),
        dict(at="@twenty-nine kilometers", lon=44.12, lat=39.56, scale=38000, d=2.6)],
    highlight=[dict(id="TUR", at=0.3), dict(id="TUR-2307", at="@Province", fill="rgba(158,43,37,.35)")],
    names=[dict(text="Turkey", lon=34.5, lat=39.2, at=0.6, out="@Province"),
           dict(text="Ağrı Province", lon=43.2, lat=39.75, at="@Province", size=40, out="@twenty-nine kilometers"),
           dict(text="Iran", lon=44.62, lat=39.40, at="@close to the Iranian border", size=40)],
    dots=[dict(lon=TENDUREK[0], lat=TENDUREK[1], label="Mount Tendürek", at="@the slopes of Mount"),
          dict(lon=ARARAT[0], lat=ARARAT[1], label="Greater Mount Ararat", at="@Greater Mount Ararat")],
    routes=[dict(**{"from": list(DURUPINAR)}, to=list(ARARAT), at="@twenty-nine kilometers", d=1.0, label="29 km", lx=-90, ly=10)],
    pins=[dict(lon=DURUPINAR[0], lat=DURUPINAR[1], label="Durupınar", sub="the boat-shaped outline", at="@twenty-nine kilometers", side="right")]))
at("It first surfaced in 1959", photo("cand_307", grade="bw", move="in", zoom=1.08, chip="1959", chip_at=0.3))
at("a Turkish army cartographer", journal([
    pc("cand_05", 560, 540, 600, rot=-3, at=0.0, grade="bw"),
    tag("CAPT. İLHAN DURUPINAR", "Turkish army cartographer", 1330, 400, "@Captain", rot=4, w=640, size=46),
    hand("spotted it in aerial photographs\n— a NATO mapping mission", 1330, 700, "@spotted it", size=50, w=640)]))
at("The site still carries his name", words([W_("DURUPINAR", y=540, at=0.1, size=230, color=GOLD)], bg="cand_13", grade="none"))
at("Photographs reached Life magazine", clip(162, grade="none", zoom=1.05))
at("and a remote Anatolian hillside", dict(type="headlines", items=[
    dict(text="A SHIP ON A MOUNTAIN?", x=820, y=300, rot=-3, at=0.1, size=92, style="white"),
    dict(text="'ARK' SHAPE SEEN FROM THE AIR", x=1080, y=560, rot=2, at="@suddenly became", size=74, style="tan"),
    dict(text="THE WORLD WANTS TO KNOW", x=840, y=810, rot=-1.5, at="@a global conversation", size=80, style="red")]))

at("The very next year came the first physical test", photo("cand_46", crop=C46, move="in", zoom=1.1,
                                                          chip="1960 · the first physical test", chip_at=0.4))
at("An American-led expedition", clip(419, grade="none", zoom=1.03, then=(172,)))
at("a man who genuinely believed", journal([
    pc("cand_45", 580, 520, 700, rot=-2, at=0.0),
    tag("SURVEYOR", "Arthur Brandenberger", 1360, 380, 0.2, rot=4, w=560, size=56),
    note("He genuinely believed the ark might be found.", 1360, 700, 0.6, rot=-3, w=460)]))
at("dug into the formation and used dynamite", clip(133, zoom=1.04, overlays=[dict(type="flash", at="@used dynamite")]))
at("Their official conclusion", journal([
    pc("cand_46", 600, 520, 820, rot=-2, at=0.0, crop=C46),
    tag("EXPEDITION · 1960", "Official conclusion", 1380, 300, 0.2, rot=4, w=540, size=48),
    strip("No visible archaeological remains.", 1380, 520, at="@no visible archaeological", size=36),
    strip("A natural formation.", 1380, 620, at="@A natural formation", size=36),
    stamp("A FREAK OF NATURE", 1380, 800, at="@A freak of nature", rot=-7, size=74)]))
at("The hunt went quiet", photo("cand_529", move="out", zoom=1.12))
at("Then, in 1977, it found its most famous hunter", depth("cand_299", subject=[0.5, 0.45], hit=0.9,
                                                          keys=[[0.5, 0.3, 1.0], [0.5, 0.34, 1.06]],
                                                          lower=("Ron Wyatt", "The most famous hunter · from 1977", "@its most famous hunter"),
                                                          **WYATT))
at("Ron Wyatt was not an archaeologist", words([
    W_("NOT AN ARCHAEOLOGIST.", y=540, at=0.05, size=140)], bg="cand_299", crop=WYATT["crop"], grade="bw"))
at("He was a nurse anesthetist from Tennessee", mapc(stops=[
        dict(at=0, lon=-70, lat=36, scale=520),
        dict(at="@who poured his life", lon=10, lat=38, scale=440, d=3.0)],
    pins=[dict(lon=TENNESSEE[0], lat=TENNESSEE[1], label="Tennessee", sub="nurse anesthetist", at="@from Tennessee", side="left", size=38)],
    routes=[dict(**{"from": list(TENNESSEE)}, to=list(DURUPINAR), at="@who poured his life", d=2.6, dash=True)],
    dots=[dict(lon=DURUPINAR[0], lat=DURUPINAR[1], label="Durupınar", at="@biblical discovery")]))
at("At Durupınar, he claimed the raised edges", spot("cand_125", center=[0.5, 0.74], radius=[0.34, 0.1], label="“Petrified hull timbers”",
                                                     hit="@petrified hull timbers", side="left", zoom=1.12))
at("He said his metal detectors", desk([
    pc("cand_300", 700, 540, 960, rot=-2, at=0.0),
    tag("CLAIM", "“Iron fittings” — metal detector readings", 1480, 540, "@iron fittings", rot=4, w=520, size=60)]))
at("He pointed to massive carved stones", clip(96, zoom=1.04))
at("and called them the ark's anchor stones", depth("cand_310", subject=[0.7, 0.6], hit=0.4, chip="“Anchor stones”"))
at("Over his career, Wyatt also claimed", dict(type="ledger", lines=[
        dict(text="Ron Wyatt — also claimed to have found:", at=0.2, y=190, size=56, color="#6b4a22"),
        dict(text="The Ark of the Covenant", at="@the Ark of the Covenant", y=340),
        dict(text="Chariot wheels — floor of the Red Sea", at="@chariot wheels", y=470)],
    ruleY=580, ruleAt="@a résumé", ruleW=1150))
at("a résumé that made institutions deeply wary", journal([
    pc("cand_299", 640, 520, 560, rot=-3, at=0.0, **WYATT),
    stamp("HANDLE WITH CAUTION", 1330, 460, at="@deeply wary", rot=-8, size=76),
    hand("…everything he touched", 1330, 680, "@everything he touched", size=58, w=640)]))

at("And then came the twist", clip(410, zoom=1.03))
at("Wyatt's own expedition partner", depth("cand_298", subject=[0.62, 0.45], hit=0.6, keys=[[0.55, 0.28, 1.0], [0.58, 0.31, 1.06]],
                                       lower=("David Fasold", "Marine salvage expert · Wyatt's expedition partner", "@David Fasold")))
at("studied the site for years", words([W_("HE CHANGED HIS MIND.", y=540, at="@changed his mind", size=150, color=GOLD)],
                                       bg="cand_298", crop=(0.0, 0.0, 1.0, 0.7)))
at("In 1996, he co-authored a geology paper", journal([
    dict(k="cut", img=cutout("vintage_stack_of_books.png", red=False), x=620, y=580, h=480, at=0.0),
    title_("1996", 1330, 300, at=0.1, size=150, underline=True),
    strip("a co-authored geology paper", 1330, 520, at="@co-authored", size=40),
    stamp("NATURAL", 1330, 740, at="@was natural", rot=-7, size=110, color=GREEN)]))
at("In 1997, under oath", mapc(stops=[dict(at=0, lon=120, lat=-15, scale=520), dict(at=0.3, lon=140, lat=-28, scale=900, d=2.2)],
    pins=[dict(lon=SYDNEY[0], lat=SYDNEY[1], label="Australia · 1997", sub="a courtroom, under oath", at=1.0, side="left", size=40)]))
at("he described the claim", quote("“Absolute BS.”", who="David Fasold — under oath, 1997, on the claim that the ark had been found",
                                   bg="cand_298", highlight=["BS"], size=150, rate=6.0))
at("The hunter who helped launch the modern search", dict(type="split", left=img("cand_299", **WYATT), right=img("cand_298"),
    leftLabel="The discovery", rightLabel="The testimony against it", leftFocus=[0.5, 0.35], rightFocus=[0.6, 0.35]))
at("So by the year 2000", board("THE SCOREBOARD · YEAR 2000", [
    dict(n="1", text="FAILED DIG", at="@one failed dig", stamp=dict(text="1960", at="@one recanted", size=48)),
    dict(n="1", text="RECANTED MOVEMENT", at="@one recanted movement", stamp=dict(text="1997", at="@one very stubborn", size=48)),
    dict(n="1", text="VERY STUBBORN SHAPE", at="@one very stubborn shape", color=RED)]))
at("The hunt could have died there", clip(172, grade="none", zoom=1.04))
at("Instead, it changed weapons", words([W_("IT CHANGED WEAPONS.", y=540, at="@changed weapons", size=160, color=GOLD)],
                                       bg=GPR, crop=GPR_CROP, overlays=[dict(type="flash", at="@changed weapons")]))

# =================================================================== part two: the modern hunt
at("Enter the modern phase", chapter("02", "PART TWO", "THE MODERN HUNT", "cand_169"))
at("A research organization called Noah's Ark Scans", dict(type="tv", img=img("cand_256", "none", (0.0, 0.0, 1.0, 0.8)), focus=[0.22, 0.5],
    overlays=[dict(type="lower", name="Andrew Jones", role="Noah's Ark Scans", at="@led by an American", x=110, y=860)]))
at("has spent recent years running", clip(388, zoom=1.03))
at("Jones has visited the site since 1997", dict(type="timeline", img=img("cand_301"), events=[
        dict(year="1997", label="First visit to the site"), dict(year="Today", label="Lives in Turkey to be near it")],
    stops=[dict(i=0, at=0.0), dict(i=1, at="@now lives in Turkey")]))
at("and states his conclusion openly", quote("“I believe this is Noah's Ark.”", who="Andrew Jones — the project's website", bg="cand_122",
                                          highlight=["believe"], size=96, rate=5.0))
at("In September 2026, his team began", photo("cand_159", move="in", focus=[0.35, 0.6], zoom=1.12,
                                              chip="First deep core drilling ever permitted", chip_at="@deep core drilling"))
at("under official Turkish government authorization", journal([
    pc("cand_12", 640, 520, 860, rot=-2, at=0.0),
    tag("PERMIT", "Official Turkish government authorization", 1450, 500, 0.3, rot=4, w=520, size=64, color=GREEN)]))
at("working with archaeologists", mapc(stops=[
        dict(at=0, lon=39.8, lat=39.3, scale=4300), dict(at=4, lon=40.4, lat=39.4, scale=4500, d=4)],
    highlight=[dict(id="TUR", at=0.1)],
    routes=[dict(**{"from": list(SIVAS)}, to=list(DURUPINAR), at=1.0, d=1.8, dash=True)],
    pins=[dict(lon=SIVAS[0], lat=SIVAS[1], label="Sivas Cumhuriyet University", sub="led by Prof. Cenker Atila", at="@Sivas", side="left", size=34, gap=90),
          dict(lon=DURUPINAR[0], lat=DURUPINAR[1], label="Durupınar", at=2.4, side="right", size=40, gap=120)]))
at("That expedition is real", verdict([
    vi(0, "The expedition", 0.2), vi(0, "The permits", "@The permits are real"),
    vi(0, "The university supervision", "@The university supervision")], focus=0, focusAt=0.0, headAt=[0.05, 0.3]))
at("Now let's examine what they say", clip(404, zoom=1.05, then=(400,)))
at("everything you're about to hear comes from that one team", journal([
    title_("ONE RULE", 960, 200, at=0.05, size=120, underline=True),
    hand("Everything that follows comes from ONE team,\nthrough its own announcements.", 960, 470, 0.4, size=60, w=1300, align="center"),
    stamp("NOT INDEPENDENTLY VERIFIED", 960, 800, at="@No independent laboratory", rot=-4, size=80)]))
at("Their evidence comes in four forms", desk([
    tag("EXHIBIT A", "The scans", 520, 330, "@four forms", rot=-5, w=440, size=62),
    tag("EXHIBIT B", "The soil", 1380, 330, 0.9, rot=4, w=440, size=62),
    tag("EXHIBIT C", "The cores", 520, 760, 1.3, rot=3, w=440, size=62),
    tag("EXHIBIT D", "The drill bit", 1380, 760, 1.7, rot=-4, w=440, size=62)], z1=1.03))

# ---- exhibit A: the scans
at("First, the scans", exhibit("A", "The scans", "cand_15", at_tag=0.2))
at("Ground-penetrating radar", clip(395, zoom=1.03))
at("electrical resistivity tomography", clip(414, zoom=1.04, then=(415,)))
at("LiDAR, thermal imaging", clip(220, zoom=1.03))
at("and audio-magnetotelluric surveys", stat("300 m", "MAPPED DEPTH", "“down to three hundred meters” — per the team", bg="cand_241",
                                             countFor=1.4))
at("The reported results", desk([
    pc("ind2_04", 480, 540, 440, rot=-2, at=0.0, grade="none"),
    strip("long straight lines", 1250, 250, at="@long straight lines", size=40),
    strip("right-angle intersections", 1250, 380, at="@right-angle intersections", size=40),
    strip("layered tiers", 1250, 510, at="@layered tiers", size=40),
    strip("elongated voids", 1250, 640, at="@elongated voids", size=40),
    stamp("DECKS · CORRIDORS · CHAMBERS?", 1250, 850, at="@interpreted as decks", rot=-5, size=58, color=GOLD)]))
at("These are the images that go viral", photo("ind2_05", grade="none", move="in", zoom=1.1, fit="contain"))
at("they look like blueprints of a buried ship", photo("cand_17", grade="none", move="in", zoom=1.12, focus=[0.55, 0.5],
                                                     chip="“Blueprints of a buried ship”", chip_at=0.3))

# ---- exhibit B: the soil
at("Second, the soil", exhibit("B", "The soil", "cand_142", at_tag=0.2))
at("88 samples from inside", clip(24, zoom=1.04, chip="2024 · 88 soil samples", chip_at=0.3))
at("The team reports the interior soil", journal([
    dict(k="stat", value="3×", label="organic matter — inside the outline", x=560, y=500, at="@three times more", rot=-3, bg=RED),
    dict(k="stat", value="+38%", label="potassium — inside the outline", x=1360, y=500, at="@38 percent", rot=3, bg=GOLD),
    hand("…as reported by the team", 960, 900, "@38 percent", size=50, w=900, align="center")]))
at("presented as the chemical ghost", clip(398, zoom=1.05, then=(397,)))
at("And remember that greener grass", spot("cand_074", center=[0.5, 0.62], radius=[0.12, 0.2], label="The greener grass", hit=0.3,
                                           grade="doc", zoom=1.15))
at("The team presents it as the visible surface echo", photo("cand_092", grade="doc", move="in", zoom=1.14,
                                                           chip="“A surface echo” — per the team", chip_at=0.8))

# ---- exhibit C: the cores
at("Third, the cores", exhibit("C", "The cores", "cand_60", at_tag=0.2))
at("drilling to depths of eighteen meters", stat("18 m", "DRILLING DEPTH", "nearly sixty feet down", bg="cand_32", countFor=1.2))
at("pulled up layered sediments", clip(400, zoom=1.04, then=(250, 396), chip="Layered · organic-rich · cavities", chip_at="@multiple underground cavities"))
at("One cavity kept filling with water", clip(50, zoom=1.05, then=(114,)))
at("the team began informally calling it", words([W_("A “ROOM.”", y=540, at="@a room", size=220, color=GOLD)], bg="cand_14",
                                                  crop=(0.0, 0.2, 1.0, 0.8)))

# ---- exhibit D: the drill bit
at("And fourth", exhibit("D", "The drill bit", "cand_14", at_tag=0.1, crop=(0.0, 0.22, 1.0, 0.72), w=760))
at("In one borehole inside the boat-shaped outline", photo("cand_161", move="in", zoom=1.1, focus=[0.5, 0.45],
                                                           chip="4–5 m down", chip_at="@four to five meters"))
at("the drill struck a layer hard enough", words([W_("HARD ENOUGH", y=420, at=0.0, size=140),
                                                  W_("TO SHATTER THE BIT.", y=600, at="@shatter the bit", size=150, color=RED)],
                                                 bg="cand_305", overlays=[dict(type="flash", at="@shatter the bit")]))
at("Jones's quote", quote("“Harder than limestone.”", who="Andrew Jones", bg="cand_10", highlight=["limestone"], size=110, rate=5.5))
at("His suggested possibilities", journal([
    dict(k="cut", img=cutout("cand_312"), x=620, y=520, h=380, at=0.0),
    strip("“petrified or highly mineralized wood”", 1260, 360, at=0.3, size=38),
    tag("PENDING", "to be determined by third-party laboratory testing", 1300, 660, "@to be determined", rot=-3, w=600, size=60, color=GOLD)]))
at("One day before drilling began", desk([
    pc("ind1_01", 560, 540, 520, rot=-3, at=0.0, grade="none", crop=(0.0, 0.55, 1.0, 1.0)),
    stamp("“ONE HUNDRED PERCENT”", 1300, 420, at="@one hundred percent", rot=-6, size=72),
    note("…told to the press ONE DAY BEFORE the drilling began", 1300, 700, 0.5, rot=3, w=520)]))
at("So that's the case for the prosecution", scales("THE CASE FOR THE PROSECUTION", [
    pan(0, "Scans", "@Scans, soil"), pan(0, "Soil", "@soil, cores"), pan(0, "Cores", "@cores, a broken"),
    pan(0, "A broken drill bit", "@a broken drill bit"), pan(0, "Total confidence", "@and total confidence")],
    left="THE CASE FOR", right="THE CASE AGAINST", norm=5))

# =================================================================== part three: the defence
at("Now the case for the defense", chapter("03", "PART THREE", "THE DEFENSE", "cand_076"))
at("Start with the scans", clip(55, zoom=1.04, chip="Radar sees boundaries", chip_at="@detects boundaries"))
at("It cannot identify what the material is", words([
    W_("IT CANNOT IDENTIFY", y=440, at=0.0, size=130), W_("WHAT THE MATERIAL IS.", y=620, at=0.4, size=130, color=GOLD)],
    bg=GPR, crop=GPR_CROP, grade="xray"))
at("And here's the detail the thumbnails omit", desk([
    pc("ind1_03", 560, 540, 560, rot=-3, at=0.0, grade="none", crop=(0.0, 0.0, 1.0, 0.72)),
    strip("straight lines + right angles", 1320, 420, at="@straight lines and right angles", size=42),
    stamp("NOT A HUMAN SIGNATURE", 1320, 640, at="@are not a human signature", rot=-6, size=76)]))
at("Limestone fractures along clean", clip(329, zoom=1.05, then=(454,)))
at("Geologists see right angles", spot("cand_076", center=[0.45, 0.45], radius=[0.2, 0.2], label="Natural right angles", hit=0.3, zoom=1.15))
at("The raw scan data, by the way", journal([
    pc("cand_208", 620, 500, 820, rot=-2, at=0.0, grade="none"),
    stamp("RAW DATA NOT RELEASED", 1380, 380, at="@never been released", rot=-7, size=64),
    hand("every rendered “deck” comes from\nthe team that already believes", 1380, 700, "@every rendered image", size=50, w=680)]))

at("Then the soil", photo("cand_157", move="in", zoom=1.1, chip="Richer in organics — reported", chip_at="@richer in organics"))
at("But look at the shape again", spot("cand_089", center=[0.5, 0.5], radius=[0.36, 0.2], label="An elongated oval, raised edges", hit=0.3,
                                       zoom=1.1))
at("That's a bowl", words([W_("A BOWL.", y=540, at=0.0, size=260, color=GOLD)], bg="cand_089"))
at("Bowls collect rainwater", clip(446, zoom=1.03))
at("and geologist Andrew Snelling", journal([
    pc("cand_172", 560, 520, 700, rot=-3, at=0.0, grade="doc"),
    tag("GEOLOGIST", "Andrew Snelling", 1360, 300, 0.3, rot=4, w=520, size=56),
    hand("a wet depression over different rock\n→ richer vegetation\n→ more organic content", 1360, 600,
         "@a wet depression", size=48, w=700),
    stamp("NO SHIP REQUIRED", 1360, 880, at="@no ship required", rot=-6, size=70)]))
at("And here's what makes Snelling's objection", words([
    W_("NOT A SECULAR SKEPTIC.", y=540, at="@he isn't a secular skeptic", size=130, color=GOLD)], bg="cand_267"))
at("He's a young-earth creationist geologist", journal([
    tag("ANSWERS IN GENESIS", "young-earth creationist geologist", 640, 420, 0.2, rot=-4, w=640, size=54),
    dict(k="cut", img=cutout("vintage_holy_bible.png", red=False), x=1380, y=440, h=440, at=0.5),
    note("believes the flood literally happened", 760, 780, "@believes the flood", rot=3, w=520)]))
at("and built a full-size ark attraction", clip(520, zoom=1.04, chip="Full-size ark attraction · Kentucky", chip_at=0.3))
at("His group examined the Durupınar claims", journal([
    pc("cand_069", 640, 520, 860, rot=-2, at=0.0),
    stamp("REJECTED", 1420, 520, at="@and rejected them", rot=-8, size=120)]))
at("When the people most motivated to believe", clip(381, grade="none", zoom=1.03, then=(425,)))

at("And the geology underneath everything", journal([
    dict(k="cut", img=cutout("vintage_stack_of_books.png", red=False), x=560, y=600, h=460, at=0.0),
    stamp("PEER-REVIEWED", 1320, 330, at="@peer-reviewed", rot=-6, size=90, color=CYAN),
    strip("Study 1 — Lorence Collins", 1320, 560, at="@two forms", size=40),
    strip("Study 2 — Murat Avci, 2007", 1320, 680, at="@two forms", size=40)]))
at("Geologist Lorence Collins examined rock samples", photo("cand_182", grade="none", move="in", zoom=1.18,
                                                          lower=("Lorence Collins", "Geologist · thin sections under a microscope", 0.5)))
at("and described volcanic-origin sediments", dict(type="geo", variant="syncline",
    beats=dict(deposit=0.1, fold="@folded by tectonic forces", plan="@a doubly plunging", slide="@later scoured"),
    labels=[dict(text="Volcanic-origin sediments", x=960, y=110, at=0.3, size=40, out="@folded by tectonic"),
            dict(text="Folded into a trough — a doubly plunging syncline", x=960, y=110, at="@folded by tectonic", size=40),
            dict(text="…scoured into a boat profile by a clay-rich landslide", x=1200, y=990, at="@later scoured", size=36)]))
at("Wyatt's \"iron fittings,\" Collins found", reclass("“IRON FITTINGS”", "natural limonite & magnetite concretions", "cand_29",
                                                      "@were natural limonite"))
at("The \"petrified gopher wood\"", reclass("“GOPHER WOOD”", "metamorphosed peridotite — common in the region", "cand_144",
                                           "@was metamorphosed peridotite"))
at("The anchor stones were local andesite", reclass("“ANCHOR STONES”", "local andesite — the same stone as the mountains", "cand_386",
                                                   "@local andesite"))

at("A second study, by Turkish geologist Murat Avci", clip(385, zoom=1.04, chip="Study 2 · Murat Avci · 2007", chip_at=0.4))
at("concluded the shape is a block of Miocene limestone", dict(type="geo", variant="slump",
    beats=dict(deposit=0.1, fold="@slumped downslope", cav="@and dissolution"),
    labels=[dict(text="A block of Miocene limestone", x=660, y=140, at=0.3, size=40),
            dict(text="…slumped downslope on weaker clays", x=1250, y=990, at="@slumped downslope", size=38)]))
at("And dissolution matters here", dict(type="geo", variant="slump", beats=dict(deposit=-1, fold=-4, cav=0.3),
    labels=[dict(text="Dissolution hollows caves into limestone — worldwide", x=960, y=120, at=0.3, size=40)]))
at("Under that model", words([
    W_("CAVITIES. TUNNELS. WATER.", y=360, at="@underground cavities", size=100),
    W_("NOT “ROOMS.”", y=560, at="@aren't rooms", size=150, color=RED),
    W_("WHAT LIMESTONE DOES.", y=760, at="@what limestone does", size=120, color=GOLD)], bg="cand_14", crop=(0.0, 0.2, 1.0, 0.8)))

at("Even the famous dimensions", clip(480, grade="none", zoom=1.05))
at("The 515-foot match only works", dict(type="measure", title="LENGTH · 300 CUBITS", pxPerFt=2.7, bars=[
    dict(label="ROYAL CUBIT (≈20.6 IN)", ft=515, value="≈515 FT", at="@Egyptian royal cubit"),
    dict(label="COMMON CUBIT (≈18 IN)", ft=450, value="≈450 FT", at="@shorter common cubit", color="#8C8C8C"),
    dict(label="THE FORMATION", ft=515, value="≈515 FT", at=0.2, color=RED)]))
at("And the width doesn't match", dict(type="measure", title="WIDTH · 50 ROYAL CUBITS", pxPerFt=9.0, bars=[
    dict(label="50 ROYAL CUBITS", ft=86, value="≈86 FT", at="@about 86 feet"),
    dict(label="THE FORMATION", ft=138, value="≈138 FT", at="@roughly 138 feet", color=RED)],
    stamp=dict(text="NO MATCH", at="@across its middle", x=1300, y=820)))
at("So is it case closed", desk([
    title_("CASE CLOSED?", 960, 380, at=0.05, size=190, color="#F1E6CF", shadow="0 10px 40px rgba(0,0,0,.6)"),
    title_("MYTH DEBUNKED?", 960, 640, at="@Myth debunked", size=150, color=GOLD, shadow="0 10px 40px rgba(0,0,0,.6)")]))

at("Not quite", clip(420, zoom=1.03, chip="The team fires back", chip_at=0.5))
at("The formation's symmetry is unusually clean", spot("ind2_01", center=[0.5, 0.5], radius=[0.2, 0.36], label="Unusually clean symmetry",
                                                       hit=0.3, zoom=1.12, grade="doc"))
at("The pointed end, they note", collage([
    pc("ind2_01", 960, 540, 1500, rot=0, at=0.0, pad=0, tape=False, grade="doc"),
    dict(k="arrow", **{"from": [1320, 900]}, to=[1320, 260], at="@faces uphill", bend=0, color=GOLD),
    strip("POINTED END → FACES UPHILL", 1400, 200, at="@faces uphill", size=42),
    strip("awkward for a mudflow-around-a-boulder theory", 760, 960, at="@mudflow-around-a-boulder", size=36)], bg="cork"))
at("And their drilling, they say", photo("cand_31", move="in", zoom=1.12, focus=[0.55, 0.55],
                                        chip="No continuous bedrock inside the outline — per the team", chip_at="@no continuous bedrock"))
at("None of these are kill shots", scales("THE REBUTTAL, WEIGHED", [
    pan(1, "Right-angle joints", 0.1), pan(1, "A rain-fed bowl", 0.35), pan(1, "Peer-reviewed geology", 0.6, w=2),
    pan(0, "Clean symmetry", 1.0), pan(0, "Bow faces uphill", 1.3), pan(0, "No bedrock", 1.6)],
    left="THE TEAM'S POINTS", right="THE GEOLOGY", norm=3))
at("but they're real arguments", clip(404, zoom=1.06, then=(24,)))

# =================================================================== part four: the verdict
at("Which leaves us exactly here", dict(type="title", img=img("cand_089"), kicker="THE VERDICT", title="MYTH OR REALITY?",
                                        subtitle="", tagline=""))
at("Here's the honest answer", chapter("04", "PART FOUR", "NEITHER EASY ANSWER", "cand_308"))
at("Reality: the shape is real", verdict([
    vi(0, "The shape", "@the shape is real"), vi(0, "The September 2026 expedition", "@expedition is real"),
    vi(0, "The cores in cold storage", "@cold storage"), vi(0, "The broken drill bit (as reported)", "@really happened")],
    focus=0, focusAt=0.0, headAt=[0.05, 0.3]))
at("Myth — at least so far", verdict([
    vi(0, "The shape", -3), vi(0, "The September 2026 expedition", -3), vi(0, "The cores in cold storage", -3),
    vi(0, "The broken drill bit (as reported)", -3),
    vi(1, "The decks", "@The decks"), vi(1, "The rooms", "@the rooms"), vi(1, "The decayed hull", "@the decayed hull"),
    vi(1, "“One hundred percent”", "@the \"one hundred percent\"")],
    focus=1, focusAt=0.3, headAt=[-2, -2]))
at("all of it comes from one team", checklist("THE INTERPRETATIONS, SO FAR", [
    dict(text="From more than one team", at="@one team that already believes", mark="no"),
    dict(text="Independently verified", at="@independently verified", mark="no"),
    dict(text="Peer-reviewed", at="@none of it peer-reviewed", mark="no"),
    dict(text="Dated", at="@none of it dated", mark="no")], bg="cand_267", size=70, gap=140, y0=290))
at("And against it stands decades of published geology", dict(type="timeline", img=img("cand_46", crop=C46), events=[
        dict(year="1960", label="Brandenberger's dynamite — “natural”"),
        dict(year="1996", label="Fasold's geology paper — “natural”"),
        dict(year="1997", label="Fasold's courtroom oath")],
    stops=[dict(i=0, at="@from Brandenberger's"), dict(i=1, at="@to Fasold's"), dict(i=2, at="@courtroom oath")]))
at("kept arriving at the same word", words([W_("THE SAME WORD:", y=360, at=0.0, size=90),
                                           W_("NATURAL.", y=580, at="@natural", size=260, color=GREEN)], bg="cand_46", crop=C46))

# =================================================================== part five: what happens next
at("But here's why I told you to stay", chapter("05", "PART FIVE", "WHAT HAPPENS NEXT", "cand_189"))
at("Because for the first time in sixty-six years", dict(type="split", left=img("cand_307", "bw"), right=img("cand_188", "none"),
    leftLabel="66 years of photographs", rightLabel="Now: the laboratory", rightFocus=[0.5, 0.5]))
at("Petrified wood, if the hard layer", dict(type="cells", beats=dict(show=0.1, replace="@retains its cellular", dur=3.0),
    labels=[dict(text="Petrified wood keeps its cells", x=960, y=110, at="@retains its cellular", size=40),
            dict(text="growth rings · vessel anatomy · under a microscope", x=960, y=980, at="@growth rings", size=38)]))
at("That is a yes-or-no test", words([W_("YES", x=620, y=540, at=0.0, size=260, color=GREEN),
                                      W_("or", x=960, y=560, at=0.25, size=90, font="GaramondI"),
                                      W_("NO", x=1300, y=540, at=0.45, size=260, color=RED)], bg="cand_189", grade="none"))
at("The organic-rich core layers", clip(400, zoom=1.06, then=(250,), chip="Radiocarbon dating", chip_at="@radiocarbon dated"))
at("and radiocarbon handles", stat("5,000", "YEARS OLD", "well within radiocarbon's range", bg="cand_325", countFor=1.2))
at("the team says that testing is scheduled", dict(type="timeline", img=img("cand_24"), events=[
        dict(year="Winter 2026", label="Laboratory testing begins"), dict(year="2027", label="Results — per the team's schedule")],
    stops=[dict(i=0, at=0.0), dict(i=1, at="@into 2027")]))
at("And they've built a custom camera drone", clip(127, zoom=1.04, then=(49,), chip="GOPHER · a camera for the voids", chip_at="@named GOPHER"))
at("to fly into the radar-mapped voids", desk([
    pc("ind2_03", 700, 520, 1000, rot=-2, at=0.0, grade="none"),
    tag("GOPHER", "after the gopher wood of Genesis", 1500, 360, 0.2, rot=4, w=480, size=60),
    stamp("HASN'T FLOWN YET", 1480, 720, at="@It hasn't flown yet", rot=-7, size=64)]))
at("If it ever returns footage of beams and joinery", clip(519, grade="none", zoom=1.03,
                                                        chip="Beams and joinery → the story of the century", chip_at="@the story of the century"))
at("If it returns dissolved limestone passages", dict(type="geo", variant="slump", beats=dict(deposit=-1, fold=-4, cav=0.2),
    labels=[dict(text="Dissolved limestone passages → the geology stands", x=960, y=120, at=0.2, size=40)]))

at("Myth or reality? Today", clip(504, grade="doc", zoom=1.03, skip=18.0,
                                  chip="A spectacular natural formation", chip_at="@a spectacular natural"))
at("carrying a spectacular claim", words([W_("A SPECTACULAR CLAIM", y=440, at=0.0, size=120, color=GOLD),
                                          W_("NOT YET VERIFIED.", y=620, at="@has not yet survived", size=130)], bg="cand_089"))
at("But the claim is, at last, testable", board("THE QUEUE · WINTER 2026–27", [
    dict(n="1", text="MICROSCOPY", at="@testable", color=GOLD),
    dict(n="2", text="RADIOCARBON", at="@and the tests", color=GOLD),
    dict(n="3", text="GOPHER DRONE", at="@already in the queue", color=GOLD)], cols=12))

# =================================================================== ending
at("And maybe that's the right note to end on", clip(486, grade="none", zoom=1.03))
at("Muslims who revere Prophet Nuh", clip(485, grade="none", zoom=1.04, then=(465,)))
at("the ark was never really about timber", photo("cand_308", move="in", zoom=1.1))
at("It's a story of warning, faith, and mercy", words([
    W_("WARNING.", y=340, at="@warning", size=130), W_("FAITH.", y=540, at="@faith", size=130, color=GOLD),
    W_("MERCY.", y=740, at="@mercy", size=130)], bg="cand_500", grade="none"))
at("and it has never needed a drill bit", clip(381, grade="none", zoom=1.05))
at("The mountain, in return", photo("cand_340", move="in", zoom=1.1))
at("The grass is greener over that outline", spot("cand_074", center=[0.5, 0.62], radius=[0.12, 0.2], label="The greener grass", hit=0.4,
                                                  grade="doc", zoom=1.15))
at("What we don't know yet", clip(602, grade="doc", zoom=1.02))
at("is whether the reason is rain pooling", dict(type="split", left=img("cand_089", "doc"), right=img("cand_500", "none"),
    leftLabel="Rain in a natural bowl…", rightLabel="…or the most famous vessel ever built", leftFocus=[0.5, 0.5]))
at("The cores will answer", photo("cand_60", move="in", zoom=1.12, focus=[0.3, 0.5]))
at("And when they do", journal([
    title_("MYTH OR REALITY?", 960, 330, at=0.1, size=150, underline=True),
    hand("to be continued — when the cores report", 960, 560, 0.6, size=62, w=1200, align="center"),
    stamp("CASE OPEN", 960, 790, at="@line by line", rot=-5, size=110, color=RED)],
    overlays=[dict(type="fadeout", d=1.6)]))

edl.main(music=[
    dict(at=None, track="09_Thunder_Dreams_Dark_Drone.mp3", db=0),
    dict(at="Let's begin with the hunt itself", track="02_Leaving_Home_Somber_Long_Bed.mp3", db=0, lead=-1.0),
    dict(at="Then, in 1977, it found its most famous hunter", track="08_Man_Down_Tension_Strings.mp3", db=-1, lead=-0.8),
    dict(at="Enter the modern phase", track="10_Industrial_Cinematic_Investigation.mp3", db=-1, lead=-1.0),
    dict(at="First, the scans", track="Dramatic Piano Pulse.mp3", db=-1, lead=-0.8),
    dict(at="Now the case for the defense", track="01_Metaphysik_Dramatic_Strings_Bed.mp3", db=-1, lead=-1.0),
    dict(at="Not quite", track="Silent Tension Piano.mp3", db=0, lead=-0.6),
    dict(at="Here's the honest answer", track="03_Sovereign_Dark_Piano_Bed.mp3", db=0, lead=-0.8),
    dict(at="But here's why I told you to stay", track="11_Unanswered_Questions_Mystery.mp3", db=0, lead=-0.8),
    dict(at="And maybe that's the right note to end on", track="Slow Dramatic Ascent.mp3", db=0, lead=-0.8),
])
