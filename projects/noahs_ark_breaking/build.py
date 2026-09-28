"""
BREAKING: They Drilled Into Noah's Ark - Then the Drill Bit Shattered
Faceless investigative documentary - edit decision list and build.

Look: "broadcast" theme - a breaking-news desk. The cold open runs as a live bulletin
(LIVE bug, a crawling ticker that keeps moving across cuts, news lower thirds, a red
BREAKING NEWS slab). The investigation is cut into eight numbered segments with bumpers,
and uses the news-desk graphics: the borehole cross-section where the bit shatters,
fact-check meters, a headline wall that collapses into its one source, the OBSERVED /
CLAIMED board whose columns never touch, video walls and numbered status rows.
The ending returns to the live bulletin as a developing story.
Music sits far under the narrator (see edl.setup below).

    python build.py plan | prep | stills [ids] | render [ids] | mix | final | all
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "docu"))

import edl                       # noqa: E402
from edl import *                # noqa: E402,F401,F403  (the shot helpers)

SP = os.environ.get("NOAH_ROOT", "/tmp/claude-0/-home-user-celeb/945fe076-994f-5d04-8c9c-fa77e8ef4232/scratchpad")
edl.setup(
    name="Noahs_Ark_Breaking_Drill_Bit_Shattered",
    kit=os.environ.get("NOAH_KIT", f"{SP}/kit"),
    footage=os.environ.get("NOAH_FOOTAGE", f"{SP}/footage"),
    work=os.environ.get("NOAH_WORK", f"{SP}/work4"),
    data=os.path.join(HERE, "data"),
    out=os.environ.get("NOAH_OUT", f"{SP}/out"),
    image_dirs=[f"{SP}/footage/images/approved", f"{SP}/work/ind", f"{SP}/footage/images/candidates"],
    theme="broadcast", grade="broadcast", grain=1.5,
    # the bed sits ~21 dB under the voice in the gaps and ~31 dB under it while he speaks
    music_floor_db=-21.0, music_duck_db=-10.0, sfx_gain=0.55,
)

DURUPINAR = (44.2317, 39.4403)
ARARAT = (44.2983, 39.7019)
TENDUREK = (43.87, 39.37)
UZENGILI = (44.205, 39.455)
DOGUBAYAZIT = (44.083, 39.547)
SIVAS = (37.035, 39.745)
TENNESSEE = (-86.4, 35.9)
SYDNEY = (151.18, -33.87)
CUDI = (42.45, 37.38)

RED, YEL, CYAN, GREEN, NAVY = "#E10600", "#FFC21A", "#1EA7FF", "#18C07A", "#0B1220"
GPR = "cand_252"
GPR_CROP = (0.0, 0.17, 1.0, 1.0)
WYATT = dict(grade="bw", crop=(0.0, 0.0, 0.5, 0.78))
C46 = (0.16, 0.01, 0.84, 0.99)

# ---------------------------------------------------------------- the live bulletin chrome
TICK_OPEN = dict(type="ticker", label="BREAKING", clock="SEPT 2026", items=[
    "Drill bit shatters inside boat-shaped Durupınar formation, eastern Turkey",
    "Research team: layer at 4–5 metres 'harder than limestone'",
    "'Petrified wood' suggested — no laboratory has identified the layer",
    "Cores to undergo third-party testing this winter"])
TICK_END = dict(type="ticker", label="DEVELOPING", clock="WINTER 2026–27", items=[
    "Durupınar cores in cold storage, headed for laboratory testing",
    "Hard layer at 4–5 metres not yet identified",
    "Independent review and peer review still to come",
    "Results expected through the winter of 2026 into 2027"])
BUG = dict(type="bug", place="Durupınar · Turkey")


def live(scene, ticker=TICK_OPEN, bug=True, intro=None):
    """Put the LIVE bug and the ticker on a scene (clips get them as a moving alpha layer)."""
    ov = list(scene.get("overlays", []))
    t = dict(ticker)
    b = dict(BUG)
    if intro is not None:
        t["intro"], b["intro"] = intro + 0.4, intro
    ov.append(t)
    if bug:
        ov.append(b)
    scene = dict(scene)
    scene["overlays"] = ov
    return scene


def lower(scene, kicker, text, sub=None, at=0.4, color=None, size=None):
    """A broadcast lower third on any scene."""
    o = dict(type="newslower", kicker=kicker, text=text, at=at)
    if sub: o["sub"] = sub
    if color: o["color"] = color
    if size: o["size"] = size
    scene = dict(scene)
    scene["overlays"] = list(scene.get("overlays", [])) + [o]
    return scene


def segment(n, title, sub=None, bg=None, **kw):
    s = dict(type="segment", n=n, kicker=f"PART {n}", title=title, **kw)
    if sub: s["sub"] = sub
    if bg: s["img"] = img(bg)
    return s


def bore(**kw):
    return dict(type="borehole", **kw)


def fact(claim, source, rating, at, note=None, **kw):
    s = dict(type="factcheck", claim=claim, source=source, rating=rating, ratingAt=at, **kw)
    if note: s["note"] = note
    return s


def nlist(title, items, **kw):
    return dict(type="newslist", title=title, items=items, **kw)


def row(text, at, status=None, color=None, **kw):
    d = dict(text=text, at=at, **kw)
    if status: d["status"] = status
    if color: d["statusColor"] = color
    return d


def cols(items, **kw):
    s = dict(type="columns", left=dict(title="OBSERVED", sub="what the instruments recorded"), right=dict(title="CLAIMED"), items=items)
    s.update(kw)
    return s


def wall(names, focus=4, push=1.2, grade=None, **kw):
    return dict(type="videowall", imgs=[img(n, grade) for n in names], focus=focus, pushAt=push, **kw)


def W2(a, b, bg, at_b, color=YEL, **kw):
    return words([W_(a, y=440, at=0.0, size=110), W_(b, y=620, at=at_b, size=120, color=color)], bg=bg, **kw)


LAYERS_4 = [dict(**{"from": 0}, to=0.6, kind="soil"), dict(**{"from": 0.6}, to=2.0, kind="sediment"),
            dict(**{"from": 2.0}, to=2.7, kind="organic"), dict(**{"from": 2.7}, to=4.4, kind="sediment"),
            dict(**{"from": 4.4}, to=6, kind="hard")]

# =================================================================== cold open: the bulletin
at(0.0, live(clip(371, zoom=1.04, overlays=[dict(type="fadein", d=0.8)]), intro=0.6))
at("a drilling crew lowered a percussion bit", live(photo("cand_159", move="in", focus=[0.35, 0.6], zoom=1.14)))
at("the kind of equipment designed", live(clip(329, zoom=1.05, then=(454,))))
at("Four to five meters down", live(bore(title="FOUR TO FIVE METRES DOWN", kicker="INSIDE THE BOAT-SHAPED OUTLINE", bot=940,
    layers=LAYERS_4, beats=dict(draw=0.1, drill=0.7, hit="@the drill hit something"),
    labels=[dict(text="the outline of a boat-shaped formation", depth=0.4, at="@the outline of a boat-shaped", line=False, x=1270)])))
at("And the bit shattered", live(dict(type="breaking", img=img("cand_089"), at=0.05,
    headline="THEY DRILLED INTO 'NOAH'S ARK' — THEN THE DRILL BIT SHATTERED",
    sub="Durupınar formation · Ağrı Province, eastern Turkey · September 2026")))
at("whatever lies at that depth is harder than limestone", live(W2("WHATEVER LIES DOWN THERE IS", "HARDER THAN LIMESTONE", "cand_11",
                                                                   "@harder than limestone")))
at("hard enough to destroy a tool", live(photo("cand_60", move="in", focus=[0.25, 0.5], zoom=1.18)))
at("And their suggestion for what it might be", live(wall(["ind1_01", "ind1_02", "ind1_03", "cand_256", "ind1_04", "cand_51",
                                                          "ind2_02", "cand_17", "ind2_05"], focus=4, push="@exploded across the internet",
                                                         grade="none")))
at("they believe it could be a layer of petrified wood", live(collage([
    dict(k="cut", img=cutout("cand_312"), x=960, y=560, h=420, at=0.0),
    title_("PETRIFIED WOOD?", 960, 200, at=0.2, size=120, color="#F4F6FA", shadow="0 8px 30px rgba(0,0,0,.6)")], bg="cork")))
at("Petrified wood. Inside", live(words([W_("PETRIFIED WOOD.", y=540, at=0.0, size=170, color=YEL)], bg="cand_179", grade="none")))
at("Inside a formation shaped like a ship", live(clip(598, grade="doc", zoom=1.03)))
at("Twenty-nine kilometers from the summit", live(lower(photo("cand_074", move="in", focus=[0.5, 0.55], zoom=1.12),
                                                       "LOCATION", "29 KM FROM MOUNT ARARAT", at=0.3)))

# ---- the turn: analysis mode (no ticker)
at("But here's what most of the headlines didn't tell you", words([
    W_("WHAT THE HEADLINES", y=440, at=0.0, size=120), W_("DIDN'T TELL YOU", y=610, at="@didn't tell you", size=130, color=RED)],
    ground="dark"))
at("That claim — like almost everything else", W2("ONE SOURCE:", "THE RESEARCH TEAM ITSELF", "cand_12", "@the research team itself"))
at("No laboratory has identified that layer", nlist("SO FAR", [
    row("A laboratory has identified the layer", 0.1, "NOT YET", RED),
    row("An independent scientist has examined it", "@No independent scientist", "NOT YET", RED)], y0=320))
at("And geologists who studied this exact site", dict(type="split", left=img("cand_089"), right=img("cand_182", "none"),
    leftLabel="The claim: a buried ship", rightLabel="The geology: rock", rightFocus=[0.5, 0.5]))
at("So what actually happened", nlist("THREE QUESTIONS", [
    row("What actually happened when they drilled?", 0.2),
    row("What did the drill really hit?", "@What did the drill"),
    row("What would it take to know the truth?", "@what would it take")], y0=300))
at("That's what we're going to untangle", clip(421, zoom=1.03, chip="Carefully · honestly · without the hype", chip_at="@carefully"))
at("If you enjoy investigations", clip(56, zoom=1.04))
at("consider subscribing", clip(147, zoom=1.04))

# =================================================================== 01 what we can verify
at("Let's start with what we can verify", segment("01", "WHAT WE CAN VERIFY", "The expedition, the permits, the press release", bg="cand_12"))
at("On September 23rd, 2026, a press release", collage([
    pc("ind1_04", 520, 540, 520, rot=-2, at=0.0, grade="none", crop=(0.0, 0.5, 1.0, 1.0)),
    title_("PRESS RELEASE", 1330, 260, at=0.2, size=110, underline=True),
    strip("September 23, 2026", 1330, 430, at="@September 23rd", size=40),
    strip("via a paid distribution service", 1330, 560, at="@a paid distribution service", size=40),
    strip("from: Noah's Ark Scans", 1330, 690, at="@from an organization called", size=40)]))
at("It announced that core drilling had officially begun", lower(photo("cand_169", move="in", focus=[0.4, 0.55], zoom=1.12),
                                                                 "SEPT 23, 2026", "CORE DRILLING OFFICIALLY BEGINS", at=0.3))
at("near the town of Doğubayazıt", dict(type="map", detail="geo_hi.json", stops=[
        dict(at=0, lon=38.5, lat=39.3, scale=3200), dict(at=0.4, lon=44.0, lat=39.5, scale=22000, d=2.6)],
    highlight=[dict(id="TUR", at=0.1), dict(id="TUR-2307", at="@Ağrı Province")],
    names=[dict(text="Iran", lon=44.62, lat=39.40, at="@close to the Iranian border", size=40)],
    dots=[dict(lon=DOGUBAYAZIT[0], lat=DOGUBAYAZIT[1], label="Doğubayazıt", at="@the town of")],
    pins=[dict(lon=DURUPINAR[0], lat=DURUPINAR[1], label="Durupınar", sub="the formation", at=1.6, side="left")]))
at("And this part is genuinely significant", words([W_("GENUINELY SIGNIFICANT.", y=540, at=0.0, size=140, color=YEL)], bg="cand_12"))
at("This is the largest officially permitted", lower(photo("cand_12", move="in", focus=[0.5, 0.55], zoom=1.12), "A FIRST",
                                                     "LARGEST PERMITTED EXPEDITION IN THE SITE'S HISTORY", at=0.3, size=40))
at("It's being directed in Turkey by Professor Cenker Atila", dict(type="map", stops=[
        dict(at=0, lon=39.8, lat=39.3, scale=4300), dict(at=4, lon=40.4, lat=39.4, scale=4500, d=4)],
    highlight=[dict(id="TUR", at=0.1)],
    routes=[dict(**{"from": list(SIVAS)}, to=list(DURUPINAR), at=1.4, d=1.8, dash=True)],
    pins=[dict(lon=SIVAS[0], lat=SIVAS[1], label="Sivas Cumhuriyet University", sub="Prof. Cenker Atila · archaeologist", at="@Professor Cenker",
               side="left", size=34, gap=90),
          dict(lon=DURUPINAR[0], lat=DURUPINAR[1], label="Durupınar", at=2.8, side="right", size=40, gap=120)]))
at("with university oversight", nlist("THE PAPERWORK", [
    row("University oversight", 0.1, "CONFIRMED", GREEN), row("Authorization from Turkish government agencies", "@authorization", "CONFIRMED", GREEN)],
    y0=340))
at("The American side is led by Andrew Jones", dict(type="tv", img=img("cand_256", "none", (0.0, 0.0, 1.0, 0.8)), focus=[0.22, 0.5],
    overlays=[dict(type="newslower", kicker="THE AMERICAN SIDE", text="ANDREW JONES", sub="Founder, Noah's Ark Scans", at="@Andrew Jones", x=110, y=820)]))
at("a man who has been visiting this site since 1997", dict(type="timeline", img=img("cand_301"), events=[
        dict(year="1997", label="First visit to the site"), dict(year="Today", label="Lives in Turkey year-round to study it")],
    stops=[dict(i=0, at=0.0), dict(i=1, at="@now lives in Turkey")]))
at("That matters, because for more than sixty years", wall(["cand_307", "cand_05", "cand_45", "cand_15", "cand_199", "cand_241",
                                                           "cand_46", "ind2_05", "cand_074"], focus=0, push="@photography", grade="none"))
at("There was one drilling attempt back in 1988", stat("1988", "ONE EARLIER DRILLING ATTEMPT", "cores taken with water-cooled drilling",
                                                      bg="cand_14", count=False))
at("those cores were contaminated", clip(114, zoom=1.05, then=(50,), chip="Contaminated by cooling water — per the current team", chip_at=0.3))
at("The 2026 expedition uses a dry percussion system", lower(photo("cand_305", move="in", focus=[0.4, 0.55], zoom=1.12),
                                                             "2026", "DRY PERCUSSION DRILLING", "no drilling fluids", at=0.3))
at("designed to bring up clean, intact cores", bore(title="UP TO 18 METRES", kicker="CLEAN, INTACT CORES", maxDepth=18, shatter=False,
    toDepth=18, statusText="CORING", layers=[dict(**{"from": 0}, to=1.5, kind="soil"), dict(**{"from": 1.5}, to=7, kind="sediment"),
    dict(**{"from": 7}, to=9, kind="organic"), dict(**{"from": 9}, to=18, kind="clay")], beats=dict(draw=0.1, drill=0.6, hit=5.0),
    labels=[dict(text="nearly sixty feet", depth=17, at="@Nearly sixty feet", bg=YEL)]))
at("And the press release describes what those first holes found", photo("cand_60", move="in", focus=[0.3, 0.5], zoom=1.15))
at("Layers of soil and sediment", bore(title="WHAT THE FIRST HOLES FOUND", kicker="PER THE PRESS RELEASE", shatter=False, toDepth=4.2,
    layers=LAYERS_4, beats=dict(draw=0.1, drill=0.4, hit=6.0),
    cavities=[dict(depth=3.3, x=1010, w=110, h=30, water=True, at="@Multiple cavities", fill="@kept filling with water")],
    labels=[dict(text="Soil & sediment", depth=1.2, at=0.3), dict(text="“Organic-rich” intervals", depth=2.35, at="@organic-rich material"),
            dict(text="A cavity filling with water", depth=3.3, at="@kept filling with water", dy=50)]))
at("which the team began referring to internally", words([W_("A “ROOM.”", y=540, at=0.2, size=220, color=YEL)], bg="cand_14",
                                                        crop=(0.0, 0.2, 1.0, 0.8)))
at("And then, in one borehole drilled inside", bore(title="THE DRILL STOPPED", kicker="ONE BOREHOLE · INSIDE THE OUTLINE", layers=LAYERS_4,
    beats=dict(draw=0.1, drill=0.5, hit="@the drill stopped"),
    labels=[dict(text="4–5 m", depth=4.5, at="@four to five meters", bg=YEL)],
    stamp=dict(text="HARD ENOUGH TO BREAK THE BIT", at="@break the bit", size=44, x=1585, y=780)))
at("Andrew Jones's quote", quote("“Whatever the core drill struck was harder than limestone — hard enough to break the bit.”",
                                 who="Andrew Jones — project statement", bg="cand_11", highlight=["harder", "limestone"], size=76, rate=5.5))
at("He added that", fact("“Petrified or highly mineralized wood are both a possibility we want to investigate.”",
                         "— Andrew Jones, project statement, Sept. 2026", "UNVERIFIED", "@third party lab testing",
                         note="Lab testing to come — not yet done.", size=50))
at("Read that sentence again", words([W_("“A POSSIBILITY", y=420, at=0.3, size=120), W_("WE WANT TO INVESTIGATE.”", y=580, at="@want to investigate", size=110, color=YEL)],
                                     ground="dark"))
at("Even the team itself has not identified the layer", W2("EVEN THE TEAM", "HAS NOT IDENTIFIED THE LAYER", "cand_60", "@has not identified", color=RED))
at("That identification — if it ever comes", clip(396, zoom=1.04, chip="A laboratory · months from now", chip_at="@months from now"))
at("But \"drill bit shatters", dict(type="headlines", items=[
    dict(text="DRILL BIT SHATTERS AT 'NOAH'S ARK' SITE", x=860, y=300, rot=-2, at=0.1, size=80, style="white"),
    dict(text="'PETRIFIED WOOD' FOUND?", x=1080, y=560, rot=2, at="@the kind of sentence", size=84, style="red"),
    dict(text="ARK MYSTERY DEEPENS", x=820, y=810, rot=-1.5, at="@built for", size=80, style="black")]))
at("and within days the story was everywhere", wall(["ind1_02", "cand_51", "ind1_01", "ind2_02", "ind1_03", "cand_256", "cand_17", "ind1_04",
                                                    "cand_242"], focus=4, push=0.6, grade="none"))
at("A day earlier, on September 22nd", dict(type="timeline", img=img("cand_305"), events=[
        dict(year="Sept 22", label="“100 percent” — to the Daily Mail"), dict(year="Sept 23", label="Drilling begins")],
    stops=[dict(i=1, at=0.0), dict(i=0, at="@on September 22nd")]))
at("One hundred percent. Before", words([W_("100%", y=420, at=0.0, size=240, color=RED),
                                          W_("BEFORE A SINGLE CORE WAS LAB-TESTED", y=640, at="@Before a single core", size=80)], ground="dark"))
at("Keep that number in your pocket", lower(clip(64, zoom=1.04), "REMEMBER", "100%", at=0.4, size=60))

# =================================================================== 02 the formation
at("So what is the Durupınar formation, stripped", segment("02", "THE FORMATION", "Stripped of the mythology", bg="cand_069"))
at("Geographically, it's a long, symmetrical", dict(type="map", detail="geo_hi.json", stops=[
        dict(at=0, lon=43.8, lat=39.5, scale=16000), dict(at=0.5, lon=44.12, lat=39.5, scale=42000, d=3.0)],
    highlight=[dict(id="TUR-2307", at=0.1)],
    dots=[dict(lon=TENDUREK[0], lat=TENDUREK[1], label="Mount Tendürek", at="@the slopes of Mount"),
          dict(lon=UZENGILI[0], lat=UZENGILI[1], label="Üzengili", at="@near the village")],
    pins=[dict(lon=DURUPINAR[0], lat=DURUPINAR[1], label="Durupınar", sub="the boat-shaped outline", at=0.6, side="right")]))
at("Depending on how you measure it", nlist("BY THE NUMBERS", [
    row("Length: roughly 157–164 metres", 0.2, "515–538 FT", YEL),
    row("Elevation: around 2,000 metres", "@sitting at an elevation", "6,500 FT", YEL)], y0=340))
at("about twenty-nine kilometers south of the summit", clip(412, zoom=1.04, then=(11,), chip="29 km to the summit of Greater Ararat", chip_at=0.3))
at("The shape is real", words([W_("THE SHAPE IS REAL.", y=420, at=0.0, size=140), W_("NOBODY DISPUTES IT.", y=600, at="@Nobody disputes", size=120, color=YEL)],
                             bg="cand_089"))
at("From the air, it genuinely looks", clip(602, grade="doc", zoom=1.02))
at("a pointed end, a rounded end, raised edges", collage([
    pc("ind2_01", 960, 540, 1560, rot=0, at=0.0, pad=0, tape=False, grade="doc"),
    dict(k="arrow", **{"from": [330, 230]}, to=[640, 330], at="@a pointed end", bend=40, color=RED),
    strip("POINTED END", 330, 190, at="@a pointed end", size=40),
    dict(k="arrow", **{"from": [1620, 900]}, to=[1300, 800], at="@a rounded end", bend=-40, color=RED),
    strip("ROUNDED END", 1600, 960, at="@a rounded end", size=40),
    strip("RAISED EDGES", 960, 150, at="@raised edges", size=40)], bg="cork", z1=1.03))
at("That shape is the entire reason", clip(410, zoom=1.03))
at("The formation was first noticed in 1959", lower(photo("cand_307", grade="bw", move="in", zoom=1.08), "1959",
                                                    "CAPT. İLHAN DURUPINAR", "Turkish army cartographer", at="@Captain"))
at("spotted it in aerial photographs taken during", clip(172, grade="none", zoom=1.04, chip="A NATO mapping mission", chip_at=0.4))
at("The site was eventually named after him", words([W_("DURUPINAR", y=540, at=0.1, size=220, color=YEL)], bg="cand_13", grade="none"))
at("A year later, in 1960", lower(photo("cand_46", crop=C46, move="in", zoom=1.1), "1960", "AN AMERICAN-LED EXPEDITION",
                                  "incl. surveyor Arthur Brandenberger", at="@which included"))
at("went to the site, dug into it", clip(133, zoom=1.04, overlays=[dict(type="flash", at="@even used dynamite")]))
at("Their official conclusion", nlist("1960 · OFFICIAL CONCLUSION", [
    row("No visible archaeological remains", "@no visible", "NATURAL", GREEN),
    row("A freak of nature", "@A freak of nature", "NATURAL", GREEN),
    row("Case closed", "@Case closed", "CLOSED", YEL)], y0=320))
at("Or so it seemed, until 1977", depth("cand_299", subject=[0.5, 0.45], hit=0.9, keys=[[0.5, 0.3, 1.0], [0.5, 0.34, 1.06]],
                                        overlays=[dict(type="newslower", kicker="1977", text="RON WYATT", sub="rediscovered and promoted the site",
                                                       at="@a man named Ron Wyatt")], **WYATT))
at("Wyatt was not an archaeologist or a geologist", words([W_("NOT AN ARCHAEOLOGIST.", y=440, at=0.0, size=120),
                                                            W_("NOT A GEOLOGIST.", y=620, at="@or a geologist", size=120, color=YEL)],
                                                           bg="cand_299", crop=WYATT["crop"], grade="bw"))
at("He was a nurse anesthetist from Tennessee", dict(type="map", stops=[
        dict(at=0, lon=-70, lat=36, scale=520), dict(at="@who devoted his life", lon=10, lat=38, scale=440, d=3.0)],
    pins=[dict(lon=TENNESSEE[0], lat=TENNESSEE[1], label="Tennessee", sub="nurse anesthetist", at="@from Tennessee", side="left", size=38)],
    routes=[dict(**{"from": list(TENNESSEE)}, to=list(DURUPINAR), at="@who devoted his life", d=2.6, dash=True)]))
at("and who claimed, over the years", nlist("WYATT ALSO CLAIMED TO HAVE FOUND", [
    row("Noah's Ark", "@not just Noah's Ark", "UNVERIFIED", YEL), row("The Ark of the Covenant", "@the Ark of the Covenant", "UNVERIFIED", YEL),
    row("The true site of Mount Sinai", "@the true site", "UNVERIFIED", YEL),
    row("Chariot wheels on the Red Sea floor", "@chariot wheels", "UNVERIFIED", YEL)], y0=250, gap=145))
at("At Durupınar, he claimed the raised edges", spot("cand_125", center=[0.5, 0.74], radius=[0.34, 0.1], label="“Petrified hull timbers”",
                                                     hit="@petrified hull timbers", side="left", zoom=1.12))
at("that he'd detected iron fittings", lower(photo("cand_300", move="in", focus=[0.75, 0.5], zoom=1.12), "WYATT'S CLAIM", "“IRON FITTINGS”",
                                             "metal-detector readings", at=0.4))
at("and that large carved stones", depth("cand_310", subject=[0.7, 0.6], hit=0.4, chip="“Anchor stones”"))
at("To his supporters, Wyatt was a pioneer", dict(type="split", left=img("cand_299", **WYATT), right=img("cand_29"),
    leftLabel="To supporters: a pioneer", rightLabel="To science: a sincere amateur", leftFocus=[0.5, 0.35]))
at("And here's a detail most retellings leave out", clip(16, zoom=1.04, then=(22,)))
at("David Fasold, a marine salvage expert", depth("cand_298", subject=[0.62, 0.45], hit=0.6, keys=[[0.55, 0.28, 1.0], [0.58, 0.31, 1.06]],
                                                  overlays=[dict(type="newslower", kicker="WYATT'S PARTNER", text="DAVID FASOLD",
                                                                 sub="marine salvage expert · 1980s", at="@David Fasold")]))
at("In 1996 he co-authored a geology paper", stat("1996", "A CO-AUTHORED GEOLOGY PAPER", "conclusion: natural", bg="cand_182", count=False))
at("And in 1997, under oath", dict(type="map", stops=[dict(at=0, lon=120, lat=-15, scale=520), dict(at=0.3, lon=140, lat=-28, scale=900, d=2.2)],
    pins=[dict(lon=SYDNEY[0], lat=SYDNEY[1], label="Australia · 1997", sub="a courtroom, under oath", at=1.0, side="left", size=40)]))
at("Fasold described the claim", quote("“Absolute BS.”", who="David Fasold — under oath, 1997, on the claim that the ark had been found",
                                       bg="cand_298", highlight=["BS"], size=150, rate=6.0))
at("The man who helped launch the modern", W2("HE HELPED LAUNCH IT —", "THEN TESTIFIED AGAINST IT", "cand_298", "@ended up testifying"))
at("That's the ground the 2026 drilling team", lower(photo("cand_31", move="in", focus=[0.55, 0.55], zoom=1.12), "2026", "NOT A BLANK SLATE",
                                                    at="@Not a blank slate"))
at("A site with sixty-six years of contested history", nlist("66 YEARS · THE SAME CYCLE", [
    row("An anomaly", "@an anomaly"), row("A headline", "@a headline"),
    row("A geological explanation", "@and a geological explanation")], y0=320))

# =================================================================== 03 why this hillside
at("Now — why this hillside", segment("03", "WHY THIS HILLSIDE?", "A story, a number, a location", bg="cand_308"))
at("The obvious answer is the story itself", clip(480, grade="none", zoom=1.03))
at("The flood of Noah — Prophet Nuh", clip(486, grade="none", zoom=1.03, then=(485,)))
at("In Genesis, God instructs Noah", nlist("GENESIS 6 · THE SPECIFICATION", [
    row("An ark of gopher wood", "@an ark of gopher wood"), row("300 cubits long", "@three hundred cubits long"),
    row("50 cubits wide", "@fifty cubits wide"), row("30 cubits high", "@thirty cubits high"),
    row("Rooms inside, sealed with pitch", "@with rooms inside")], y0=230, gap=150, rowH=120, size=40))
at("In the Qur'an, Prophet Nuh is commanded", lower(photo("cand_24", move="in", zoom=1.1), "THE QUR'AN", "PROPHET NUH BUILDS THE VESSEL",
                                                    "under divine guidance", at=0.4))
at("the Qur'an describes the ark coming to rest", dict(type="map", stops=[
        dict(at=0, lon=40, lat=38.5, scale=3000), dict(at=0.5, lon=43.3, lat=38.5, scale=7000, d=2.8)],
    highlight=[dict(id="TUR", at=0.1)],
    pins=[dict(lon=CUDI[0], lat=CUDI[1], label="Mount Cudi (Judi)", sub="one proposed “Al-Judi”", at="@Al-Judi", side="left", size=36),
          dict(lon=ARARAT[0], lat=ARARAT[1], label="Mount Ararat", sub="another tradition", at="@with various mountains proposed", side="right", size=36)]))
at("Neither text, it's worth stating plainly", words([
    W_("NEITHER TEXT NAMES DURUPINAR.", y=440, at=0.1, size=110),
    W_("THE LINK IS MODERN — NOT SCRIPTURE.", y=620, at="@made by modern researchers", size=90, color=YEL)], bg="cand_089"))
at("And the connection rests heavily on one number", words([W_("ONE NUMBER.", y=540, at=0.0, size=200, color=YEL)], ground="dark"))
at("The ark's length: three hundred cubits", clip(441, grade="none", zoom=1.03))
at("If you use the Egyptian royal cubit", dict(type="measure", title="300 CUBITS × THE ROYAL CUBIT", pxPerFt=2.7, bars=[
    dict(label="ROYAL CUBIT (≈20.6 IN)", ft=515, value="≈515 FT", at="@comes out to roughly"),
    dict(label="THE FORMATION'S MOST-CITED LENGTH", ft=515, value="≈515 FT", at="@most-cited measurement", color=RED)],
    stamp=dict(text="MATCH", at="@about 515 feet", x=1300, y=820)))
at("Supporters call that match extraordinary", words([W_("“EXTRAORDINARY.”", y=540, at=0.0, size=160, color=YEL)], bg="cand_06"))
at("Skeptics point out two problems", dict(type="measure", title="PROBLEM 1 · WHICH CUBIT?", pxPerFt=2.7, bars=[
    dict(label="ROYAL CUBIT (≈20.6 IN)", ft=515, value="≈515 FT", at=0.0, grow=0.01),
    dict(label="COMMON CUBIT (≈18 IN)", ft=450, value="≈450 FT", at="@a shorter common cubit", color="#8C8C8C"),
    dict(label="THE FORMATION", ft=515, value="≈515 FT", at=0.0, grow=0.01, color=RED)]))
at("Second, the formation is much wider", dict(type="measure", title="PROBLEM 2 · THE WIDTH", pxPerFt=9.0, bars=[
    dict(label="THE FORMATION", ft=138, value="≈138 FT", at="@about 138 feet", color=RED),
    dict(label="50 ROYAL CUBITS", ft=86, value="≈86 FT", at="@the roughly 86 feet")],
    stamp=dict(text="NO MATCH", at="@would give you", x=1300, y=820)))
at("Supporters answer that a decaying", clip(597, grade="doc", zoom=1.03, chip="“The hull splayed outward” — supporters", chip_at=0.5))
at("Which may be true", cols([
    dict(side=0, text="Length ≈515 ft (royal cubit)", tag="counted as evidence", at="@every measurement that matches"),
    dict(side=1, text="Width 138 ft, not 86 ft", tag="explained away", at="@every measurement that doesn't"),
    dict(side=1, text="Common cubit: 450 ft", tag="explained away", at="@explained away")],
    left=dict(title="MATCHES", sub="evidence"), right=dict(title="DOESN'T MATCH", sub="explained away"),
    gapAt="@a pattern worth watching", gapText="A PATTERN WORTH WATCHING"))
at("Then there's the location", dict(type="map", stops=[
        dict(at=0, lon=42.5, lat=39.5, scale=5000), dict(at=0.4, lon=44.0, lat=39.6, scale=9000, d=3.0)],
    highlight=[dict(id="TUR", at=0.1), dict(id="ARM", at="@a region, not a single peak")],
    circles=[dict(lon=ARARAT[0], lat=ARARAT[1], km=90, at="@a region, not a single peak")],
    dots=[dict(lon=ARARAT[0], lat=ARARAT[1], label="Greater Ararat", at="@the mountains of Ararat")],
    pins=[dict(lon=DURUPINAR[0], lat=DURUPINAR[1], label="Durupınar", sub="inside the broader region", at=3.0, side="left")]))
at("Durupınar sits in that broader region", clip(425, zoom=1.04, then=(557,), chip="Durupınar: inside the broader region", chip_at=0.3))
at("Critics counter with a specific problem", dict(type="valley",
    beats=dict(draw=0.1, boat="@the formation lies inside", measure="@a thousand meters deep", water=99),
    labels=[dict(text="≈1,000 m deep valley", x=1480, y=700, at="@a thousand meters", size=38),
            dict(text="volcanic terrain", x=960, y=90, at="@shaped by volcanism", size=38)]))
at("and Greater Ararat itself last erupted in 1840", stat("1840", "GREATER ARARAT'S LAST ERUPTION", "volcanic terrain all around",
                                                         bg="cand_322", count=False))
at("In Genesis, the ark lands while", dict(type="valley", beats=dict(draw=-2, boat=-1, measure=-1, water="@still submerged"),
    labels=[dict(text="Genesis: the peaks stay under water for months", x=960, y=90, at="@still submerged", size=38),
            dict(text="A vessel low in a deep valley?", x=960, y=980, at="@A vessel resting low", size=38)]))
at("and hard to square with the Qur'anic", dict(type="map", stops=[
        dict(at=0, lon=43.3, lat=38.5, scale=7000), dict(at=0.5, lon=43.0, lat=38.2, scale=8000, d=2.0)],
    highlight=[dict(id="TUR", at=0.0)],
    pins=[dict(lon=CUDI[0], lat=CUDI[1], label="Al-Judi?", sub="located elsewhere by many classical scholars", at="@located elsewhere",
               side="left", size=36),
          dict(lon=DURUPINAR[0], lat=DURUPINAR[1], label="Durupınar", at=0.2, side="right", size=36)]))
at("So before any radar was ever switched on", words([
    W_("INTERPRETATION", y=330, at=0.2, size=120),
    W_("LAYERED ON", y=530, at=0.9, size=90, color=YEL),
    W_("INTERPRETATION", y=720, at=1.5, size=120)], ground="dark"))

# =================================================================== 04 the instruments
at("Now we arrive at what the current team says is different", segment("04", "THE INSTRUMENTS", "Not arguments. Instruments.", bg="cand_241"))
at("The Noah's Ark Scans project has run a battery", clip(388, zoom=1.03, chip="Ground-penetrating radar", chip_at="@ground-penetrating radar"))
at("electrical resistivity tomography", clip(414, zoom=1.04, then=(415,)))
at("LiDAR, thermal imaging", clip(220, zoom=1.03))
at("and audio-magnetotelluric surveys", wall(["cand_15", "cand_216", "cand_227", "cand_63", "ind2_05", "cand_34", "cand_241", "cand_208", "cand_35"],
                                             focus=4, push="@three hundred meters", grade="none"))
at("The team says its scans reveal", nlist("WHAT THE SCANS SHOW — PER THE TEAM", [
    row("Long, straight lines", "@long, straight lines", "→ DECKS?", YEL),
    row("Right-angle intersections", "@right-angle intersections", "→ CORRIDORS?", YEL),
    row("Layered tiers", "@layered tiers", "→ DECKS?", YEL),
    row("Elongated voids", "@elongated voids", "→ CHAMBERS?", YEL)], y0=250, gap=150))
at("Then, soil", clip(24, zoom=1.04, then=(530, 18), chip="2024 · 88 soil samples", chip_at="@88 soil samples"))
at("According to the team, soil inside the formation", collage([
    dict(k="stat", value="3×", label="organic matter — inside the outline", x=560, y=500, at="@three times more", rot=-3, bg=RED),
    dict(k="stat", value="+38%", label="potassium — inside the outline", x=1360, y=500, at="@38 percent", rot=3, bg=YEL),
    strip("as reported by the team", 960, 880, at="@38 percent", size=40)]))
at("which they argue is consistent", clip(398, zoom=1.05, then=(397,), chip="“A decayed wooden structure” — the team", chip_at=0.4))
at("Vegetation above the formation", spot("cand_074", center=[0.5, 0.62], radius=[0.12, 0.2], label="Greener, denser", hit=0.4, grade="doc", zoom=1.15))
at("And in September 2026 came the drilling itself", clip(400, zoom=1.05, then=(250,)))
at("cores up to eighteen meters deep", nlist("THE DRILLING · SEPT 2026", [
    row("Cores up to 18 metres deep", 0.1, "REPORTED", CYAN), row("Organic-rich layers", "@organic-rich layers", "REPORTED", CYAN),
    row("Water-filled cavities", "@water-filled cavities", "REPORTED", CYAN)], y0=320))
at("the moment that made the title of this video", dict(type="breaking", img=img("cand_11"), at=0.05, kicker="THE MOMENT",
    headline="A DRILL BIT DESTROYED AT 4–5 METRES", sub="on a layer the team hopes is petrified or mineralized wood",
    subAt="@on a layer the team hopes"))
at("Let me explain why", lower(photo("cand_179", grade="none", move="in", zoom=1.1), "EXPLAINER", "WHY PETRIFIED WOOD MATTERS", at=0.4))
at("When wood petrifies", dict(type="cells", beats=dict(show=0.1, replace="@minerals slowly replace", dur=3.5),
    labels=[dict(text="Minerals replace the tissue, cell by cell", x=960, y=110, at="@minerals slowly replace", size=40),
            dict(text="…the structure survives in stone", x=960, y=980, at="@while preserving", size=40)]))
at("That's how a wooden hull could", photo("cand_312", grade="none", move="in", zoom=1.12, fit="contain"))
at("And petrified wood is genuinely hard", W2("PETRIFIED WOOD IS HARD —", "OFTEN HARDER THAN LIMESTONE", "cand_179", "@often harder", grade="none"))
at("So if a lab confirmed petrified wood", nlist("THREE IFS", [
    row("IF a lab confirms petrified wood", "@if a lab confirmed", "UNANSWERED", None, statusAt="@Every one of them"),
    row("IF the cellular structure is preserved", "@with preserved cellular", "UNANSWERED", None, statusAt="@Every one of them"),
    row("IF radiocarbon places it in the right era", "@if radiocarbon dating", "UNANSWERED", None, statusAt="@Every one of them")], y0=300))
at("Because here's the discipline", words([W_("THE DISCIPLINE", y=540, at=0.0, size=180, color=YEL)], ground="dark"))
at("A drill bit breaking tells you one thing only", cols([
    dict(side=0, text="A hard layer at 4–5 m", tag="a genuine observation", at="@there is a hard layer"),
    dict(side=1, text="Wood", at="@wood, deck"), dict(side=1, text="Deck", at="@deck, hull"),
    dict(side=1, text="Hull", at="@hull, ark"), dict(side=1, text="Ark", at="@ark — is interpretation")],
    left=dict(title="OBSERVATION"), right=dict(title="INTERPRETATION"), gap=100,
    gapAt="@is interpretation waiting", gapText="INTERPRETATION WAITING FOR EVIDENCE"))
at("Radar can tell you that underground material changes", clip(55, zoom=1.04, chip="Radar: boundaries", chip_at=0.4))
at("It cannot read the word", W2("RADAR CANNOT READ", "“SHIP” OFF A WAVEFORM", GPR, "@off a waveform", crop=GPR_CROP, grade="xray"))
at("Soil chemistry can tell you", lower(photo("cand_157", move="in", zoom=1.12), "SOIL CHEMISTRY", "ORGANICS: ELEVATED",
                                        "not proof the organic matter was a boat", at="@It cannot tell you"))
at("And all of these results, so far, come from one team", W2("ALL OF IT:", "ONE TEAM", "cand_12", "@come from one team"))
at("led by a man who has publicly stated", quote("“I believe this is Noah's Ark. That's why I'm putting the Durupınar site through the most rigorous testing possible.”",
                                                  who="Andrew Jones — project website", bg="cand_122", highlight=["believe"], size=64, rate=6.0))
at("That conviction is sincere", lower(photo("cand_259", grade="none", move="in", zoom=1.08, fit="contain"), "SINCERE", "IT MAY EVEN BE RIGHT", at="@It may even be right"))
at("But in science, the person who already knows", W2("THE ONE WHO ALREADY KNOWS", "NEEDS INDEPENDENT CHECKING MOST", "cand_182",
                                                      "@most need independent checking", grade="none"))
at("To the team's credit", nlist("THE PROCESS", [
    row("Third-party laboratory testing", "@third-party laboratory testing", "PROMISED", YEL),
    row("Peer review", "@and peer review", "PROMISED", YEL),
    row("Completed", "@It's just not the process", "NOT YET", RED)], y0=320))

# =================================================================== 05 the geology
at("So what do geologists", segment("05", "THE GEOLOGY", "What the published science says", bg="cand_076"))
at("This is the part the viral clips skip", clip(329, zoom=1.05, then=(454,)))
at("The most detailed explanation comes from geologist Lorence Collins", lower(photo("cand_182", grade="none", move="in", zoom=1.18),
                                                                           "PEER-REVIEWED", "LORENCE COLLINS", "geologist · rock samples from the site",
                                                                           at="@Lorence Collins"))
at("In his analysis, the formation is not timber", words([W_("NOT TIMBER.", y=430, at=0.1, size=160), W_("ROCK.", y=630, at="@It's rock", size=200, color=YEL)],
                                                          bg="cand_076"))
at("volcanic-origin sediments deposited", dict(type="geo", variant="syncline",
    beats=dict(deposit=0.1, fold="@folded by tectonic forces", plan="@imagine a trough-shaped", slide=99),
    labels=[dict(text="Volcanic-origin sediments in an ancient basin", x=960, y=110, at=0.3, size=40, out="@folded by tectonic"),
            dict(text="Folded: a doubly plunging syncline", x=960, y=110, at="@folded by tectonic", size=40),
            dict(text="…tilted at both ends", x=1200, y=990, at="@tilted at both ends", size=36)]))
at("Later, erosion, uplift", clip(65, zoom=1.04, chip="Erosion · uplift · a clay-rich landslide", chip_at=0.3))
at("scouring it into the boat-like profile", clip(38, zoom=1.03))
at("The famous \"iron brackets\"", fact("“Iron brackets from the ark.”", "— Ron Wyatt, metal-detector readings", "NATURAL", "@limonite and magnetite",
                                         note="Collins: natural limonite and magnetite concretions. No smelting required.",
                                         scale=["MAN-MADE", "UNCLEAR", "NATURAL"], colors=[RED, YEL, GREEN], meterTitle="COLLINS'S FINDING"))
at("The supposed petrified gopher wood", fact("“Petrified gopher wood.”", "— Ron Wyatt", "NATURAL", "@metamorphosed peridotite",
                                              note="Collins: crinkled, metamorphosed peridotite, a common rock in the region.",
                                              scale=["MAN-MADE", "UNCLEAR", "NATURAL"], colors=[RED, YEL, GREEN], meterTitle="COLLINS'S FINDING"))
at("The anchor stones? Local andesite", fact("“The ark's anchor stones.”", "— Ron Wyatt", "NATURAL", "@Local andesite",
                                             note="Collins: local andesite, the same stone as the surrounding mountains.",
                                             scale=["MAN-MADE", "UNCLEAR", "NATURAL"], colors=[RED, YEL, GREEN], meterTitle="COLLINS'S FINDING"))
at("And critically, fossil-bearing limestone", clip(459, grade="none", zoom=1.04, chip="Fossil-bearing limestone: far older than any human-era flood",
                                                   chip_at="@far older"))
at("A second peer-reviewed study", lower(clip(385, zoom=1.04, then=(34,)), "STUDY 2 · 2007", "MURAT AVCI", "Turkish geologist", at=0.4))
at("the ship shape is a large block of Miocene limestone", dict(type="geo", variant="slump",
    beats=dict(deposit=0.1, fold="@slumped downslope", cav="@the natural dissolution"),
    labels=[dict(text="A block of Miocene limestone", x=660, y=140, at=0.3, size=40),
            dict(text="…slumped on weaker clays · earthflow · ice melt · dissolution", x=1100, y=990, at="@slumped downslope", size=34)]))
at("which, by the way, also produces cavities", dict(type="geo", variant="slump", beats=dict(deposit=-1, fold=-4, cav=0.2),
    labels=[dict(text="Dissolution → cavities, tunnels, voids", x=960, y=120, at=0.3, size=40),
            dict(text="…how caves form", x=960, y=990, at="@how caves form", size=40)]))
at("Void spaces are not a signature of rooms", words([W_("NOT ROOMS.", y=440, at=0.0, size=150, color=RED),
                                                       W_("KARST.", y=640, at="@signature of karst", size=200, color=YEL)], ground="dark"))
at("And here's the detail that should give any viewer pause", W2("NOT SECULAR", "SKEPTICISM ALONE", "cand_267", "@skepticism alone"))
at("Answers in Genesis", lower(clip(520, zoom=1.04, then=(519,)), "YOUNG-EARTH CREATIONISTS", "ANSWERS IN GENESIS",
                               "built a full-size ark attraction in Kentucky", at=0.3))
at("has examined the Durupınar claims and rejected them", fact("“The Durupınar formation is Noah's Ark.”", "— the claim, as examined by Answers in Genesis",
                                                               "REJECTED", "@and rejected them", scale=["ACCEPTED", "UNDECIDED", "REJECTED"],
                                                               colors=[GREEN, YEL, RED], meterTitle="CREATIONIST VERDICT"))
at("Their geologist, Andrew Snelling", spot("cand_089", center=[0.5, 0.5], radius=[0.36, 0.2], label="An elongated bowl", hit="@an elongated bowl",
                                            zoom=1.1))
at("It collects rainwater", nlist("SNELLING: A MUNDANE EXPLANATION", [
    row("A bowl collects rainwater", 0.0), row("Different rock weathers into richer soil", "@Different underlying rock"),
    row("More moisture and nutrients", "@Better moisture"), row("Greener grass, more organic content", "@greener grass")], y0=250, gap=150))
at("No buried vessel required", words([W_("NO BURIED VESSEL REQUIRED.", y=540, at=0.0, size=120, color=YEL)], bg="cand_172", grade="doc"))
at("Their verdict, in essence", W2("NOTHING NEW SINCE", "THE 1980s", "cand_267", "@in the 1980s"))
at("When both secular geologists", dict(type="split", left=img("cand_182", "none"), right=img("cand_069"),
    leftLabel="Secular geologists: rock", rightLabel="Creationist geologists: rock"))
at("that is the mountain the 2026 expedition has to climb", clip(418, zoom=1.03))

# =================================================================== 06 side by side
at("So let's lay the pieces side by side", segment("06", "SIDE BY SIDE", "Observed vs. claimed"))
OBS = [("A boat-shaped outline", "undisputed", "@a boat-shaped outline"),
       ("Geophysical anomalies", "the project's instruments", "@Geophysical anomalies"),
       ("More organic content inside", "measured by the project", "@Soil inside the outline"),
       ("Organic-rich layers, cavities in cores", "recovered by the project", "@Core samples containing"),
       ("A hard layer that broke a bit", "reported by the project", "@A hard layer at four"),
       ("No continuous bedrock so far", "reported by the project", "@And no continuous bedrock")]
CLA = [("“100 percent” man-made", "@that the formation is"), ("Layers are decks, voids corridors", "@That the layers are decks"),
       ("A water-filled cavity is a “room”", "@is a \"room.\""), ("Organic soil is decayed hull timber", "@That organic soil"),
       ("The hard layer may be petrified wood", "@And that the hard layer")]
at("What has actually been observed", cols([dict(side=0, text=a, tag=b, at=c, size=30) for a, b, c in OBS[:3]], gap=100))
at("Core samples containing organic-rich layers", clip(404, zoom=1.06, then=(400,), chip="Recovered by the project", chip_at=0.4))
at("A hard layer at four to five meters that broke", cols([dict(side=0, text=a, tag=b, at=(-3 if k < 3 else (0.1 if k == 3 else c)), size=30)
                                                          for k, (a, b, c) in enumerate(OBS)], gap=100))
at("Now, what has been claimed", cols([dict(side=0, text=a, tag=b, at=-3, size=30) for a, b, c in OBS] +
                                      [dict(side=1, text=a, at=c, size=30) for a, c in CLA], gap=100))
at("Notice the two columns never touch", cols([dict(side=0, text=a, tag=b, at=-3, size=30) for a, b, c in OBS] +
                                              [dict(side=1, text=a, at=-3, size=30) for a, c in CLA], gap=100,
                                              gapAt=0.3, gapText="THE COLUMNS NEVER TOUCH"))
at("Right angles appear in fractured limestone", spot("cand_076", center=[0.45, 0.45], radius=[0.2, 0.2], label="Natural right angles", hit=0.3, zoom=1.15))
at("Organic matter accumulates in wet depressions", clip(446, zoom=1.03))
at("Cavities form when limestone dissolves", dict(type="geo", variant="slump", beats=dict(deposit=-1, fold=-4, cav=0.1),
    labels=[dict(text="Cavities: limestone dissolving", x=960, y=120, at=0.2, size=40)]))
at("Drill bits break on basalt", lower(photo("cand_327", grade="none", move="in", zoom=1.12), "VOLCANIC COUNTRY", "BASALT · SILICIFIED ROCK · DENSE LAYERS",
                                       at="@on basalt", size=40))
at("Collins's analysis found the area rich", depth("cand_386", subject=[0.72, 0.55], hit=0.4, chip="Basalts and andesites"))
at("A shattered bit in volcanic country", bore(title="SURPRISING ONLY IF…", kicker="A HARD LAYER IN VOLCANIC TERRAIN", layers=LAYERS_4,
    beats=dict(draw=0.1, drill=0.3, hit=1.6), labels=[dict(text="basalt? silicified rock? a dense natural layer?", depth=5.2, at=2.0, bg=YEL)]))
at("And the \"no bedrock\" point", fact("“No bedrock refutes the natural-formation theory.”", "— the project team", "DISPUTED", "@cuts both ways",
                                        note="Until the cores are published, it cuts both ways."))
at("A slumped limestone block riding on clay", dict(type="geo", variant="slump", beats=dict(deposit=0.1, fold="@riding on clay", cav=99),
    labels=[dict(text="A slumped block on clay isn't in-situ bedrock either", x=960, y=120, at="@wouldn't present", size=38)]))
at("The observation is real. What it means is contested", W2("THE OBSERVATION IS REAL.", "WHAT IT MEANS IS CONTESTED.", "cand_31", "@What it means"))
at("There's one more source-quality issue", dict(type="echo", headlines=[
    dict(text="Drill bit shatters at 'Noah's Ark' site"), dict(text="'Harder than limestone' layer found"),
    dict(text="Scientists drill into Noah's Ark"), dict(text="'100 percent' certain it's man-made"),
    dict(text="Petrified wood beneath the ark?"), dict(text="Mystery layer stops the drill"),
    dict(text="Noah's Ark: the drilling begins"), dict(text="A 'room' filling with water"),
    dict(text="Ark hunters hit something hard"), dict(text="Is this Noah's Ark? Drill breaks")],
    sources=[dict(title="1 PRESS RELEASE", sub="written by Noah's Ark Scans itself"), dict(title="1 INTERVIEW", sub="given to the Daily Mail")],
    collapseAt="@traces back to a single", gap=0.35))
at("Ten headlines do not equal ten confirmations", W2("TEN HEADLINES.", "ONE SOURCE, ECHOED.", "cand_256", "@one source, echoed", grade="none", crop=(0.0, 0.0, 1.0, 0.8)))

# =================================================================== 07 what would settle it
at("Here's the good news, and it's real", segment("07", "WHAT WOULD SETTLE IT", "For the first time: testable", bg="cand_60"))
at("Not by radar interpretation", clip(404, zoom=1.06, then=(396,), chip="Physical samples → laboratories", chip_at="@By physical samples"))
at("What would actually move the needle", words([W_("WHAT WOULD", y=440, at=0.0, size=130), W_("MOVE THE NEEDLE?", y=610, at=0.4, size=140, color=YEL)], ground="dark"))
at("First, microscopy and mineralogy", lower(photo("cand_188", grade="none", move="in", zoom=1.15), "TEST 1", "MICROSCOPY & MINERALOGY",
                                             "the hard layer · the organic-rich cores", at=0.3))
at("Petrified wood keeps its cellular architecture", photo("cand_189", grade="none", move="in", zoom=1.12, chip="Growth rings · vessel structures",
                                                           chip_at="@growth rings"))
at("That's a yes-or-no test", words([W_("YES", x=620, y=540, at=0.0, size=260, color=GREEN), W_("or", x=960, y=560, at=0.25, size=90, font="GaramondI"),
                                     W_("NO", x=1300, y=540, at=0.45, size=260, color=RED)], bg="cand_189", grade="none"))
at("Second, radiocarbon dating", lower(clip(400, zoom=1.06, then=(250,)), "TEST 2", "RADIOCARBON DATING", "of the organic material", at=0.3))
at("If the carbon is a few centuries old", nlist("RADIOCARBON · TWO OUTCOMES", [
    row("A few centuries old, or same as the sediment", 0.1, "ARK READING ENDS", RED),
    row("Around 4,000–5,000 years old", "@If it returned a date", "HARD TO EXPLAIN", YEL, sub="…though still not proof of a ship")],
    y0=320, gap=170, rowH=140))
at("Third, independent replication", lower(clip(420, zoom=1.03), "TEST 3", "INDEPENDENT REPLICATION", "outside geologists · the raw data · the cores", at=0.3))
at("And fourth, publication", collage([
    dict(k="cut", img=cutout("vintage_stack_of_books.png", red=False), x=620, y=580, h=460, at=0.0),
    title_("TEST 4", 1330, 280, at=0.1, size=110, underline=True),
    strip("publication in peer-reviewed journals", 1330, 470, at=0.4, size=40),
    stamp("PEER REVIEW", 1330, 700, at="@can be attacked", rot=-6, size=100)]))
at("The team says all of this is planned", dict(type="timeline", img=img("cand_24"), events=[
        dict(year="Winter 2026", label="Compositional, organic, stratigraphic testing"), dict(year="2027", label="A public scientific statement"),
        dict(year="Later", label="Further seasons planned")],
    stops=[dict(i=0, at=0.0), dict(i=1, at="@into 2027"), dict(i=2, at="@further seasons")]))
at("They also plan to send a custom-built camera drone", lower(clip(127, zoom=1.04, then=(49,)), "PLANNED", "GOPHER",
                                                               "a camera drone for the radar-mapped voids", at="@named it GOPHER"))
at("If that drone ever returns footage of worked timber", clip(519, grade="none", zoom=1.03, chip="Joinery · beams → the story of the century",
                                                             chip_at="@the story of the century"))
at("If it returns footage of dissolved limestone", dict(type="geo", variant="slump", beats=dict(deposit=-1, fold=-4, cav=0.2),
    labels=[dict(text="Dissolved limestone passages → the geology stands", x=960, y=120, at=0.2, size=40)]))
at("Either outcome is possible", W2("EITHER OUTCOME IS POSSIBLE.", "ONLY ONE HAS 60 YEARS OF EVIDENCE.", "cand_089", "@Only one of them"))

# =================================================================== 08 the answer (live again)
at("So — did they drill into Noah's Ark", segment("08", "THE ANSWER", "Did they drill into Noah's Ark?", bg="cand_089"))
at("Here is the most honest answer available today", live(lower(clip(504, grade="doc", zoom=1.02), "THE HONEST ANSWER", "WHAT HAPPENED", at=0.4),
                                                         ticker=TICK_END, intro=0.3))
at("In September 2026, a permitted", live(nlist("WHAT HAPPENED", [
    row("A permitted, university-supervised expedition", 0.2, "CONFIRMED", GREEN),
    row("The first deep coring in the site's history", "@the first deep coring", "CONFIRMED", GREEN)], y0=300), ticker=TICK_END))
at("In one borehole, at four to five meters down", live(clip(371, zoom=1.05, then=(74, 224), chip="4–5 m · a layer hard enough to break the bit",
                                                         chip_at=0.4), ticker=TICK_END))
at("That part happened, according to the team itself", live(nlist("WHAT HAPPENED", [
    row("A permitted, university-supervised expedition", -3, "CONFIRMED", GREEN),
    row("The first deep coring in the site's history", -3, "CONFIRMED", GREEN),
    row("A layer hard enough to break the bit", 0.1, "PER THE TEAM", YEL)], y0=300), ticker=TICK_END))
at("Everything beyond that is unfinished", live(words([W_("EVERYTHING BEYOND THAT", y=440, at=0.0, size=120),
                                                       W_("IS UNFINISHED.", y=620, at="@is unfinished", size=150, color=YEL)], ground="dark"), ticker=TICK_END))
at("The layer has not been identified", live(fact("“Petrified wood.”", "— the hope stated in the press release", "UNVERIFIED", "@not a laboratory result",
                                                  note="The layer has not been identified."), ticker=TICK_END))
at("The scans, the soil chemistry", live(nlist("ONE TEAM'S INTERPRETATIONS", [
    row("The scans", "@The scans", "NOT REVIEWED", RED), row("The soil chemistry", "@the soil chemistry", "NOT REVIEWED", RED),
    row("The organic cores", "@the organic cores", "NOT REVIEWED", RED), row("The “rooms”", "@the \"rooms\"", "NOT REVIEWED", RED)],
    y0=250, gap=150), ticker=TICK_END))
at("Against those claims stands decades", live(wall(["cand_182", "cand_298", "cand_076", "cand_13", "cand_386", "cand_144", "cand_267", "cand_069", "cand_172"],
                                                    focus=2, push="@including analyses", grade="none"), ticker=TICK_END))
at("describing a folded, slumped block", live(clip(600, zoom=1.03), ticker=TICK_END))
at("And yet, something real did change this year", clip(410, zoom=1.03))
at("For sixty-six years, this argument ran", dict(type="split", left=img("cand_307", "bw"), right=img("cand_60"),
    leftLabel="66 years: photographs", rightLabel="Now: cores in cold storage", rightFocus=[0.3, 0.5]))
at("For the first time, the claim has walked itself into a laboratory", clip(396, zoom=1.04, then=(397,)))
at("That is how truth is supposed to work", W2("EVIDENCE —", "OR QUIETLY EVAPORATE.", "cand_60", "@whichever way"))
at("One last thought, for viewers of every background", clip(486, grade="none", zoom=1.04))
at("For Muslims and Christians and Jews", clip(485, grade="none", zoom=1.04, then=(465,)))
at("was never really about timber", photo("cand_308", move="in", zoom=1.1))
at("It's about faith, warning, and mercy", words([W_("FAITH.", y=340, at="@faith", size=130), W_("WARNING.", y=540, at="@warning", size=130, color=YEL),
                                                  W_("MERCY.", y=740, at="@and mercy", size=130)], bg="cand_500", grade="none"))
at("and it has survived for millennia", clip(381, grade="none", zoom=1.05))
at("And for the scientists in the audience", photo("cand_327", grade="none", move="in", zoom=1.1, chip="If the labs return plain volcanic rock…",
                                                    chip_at="@plain volcanic rock"))
at("It becomes a spectacular lesson", clip(602, grade="doc", zoom=1.02))
at("The drill bit broke", live(bore(title="WHAT DID IT BREAK ON?", kicker="4–5 METRES · INSIDE THE OUTLINE", layers=LAYERS_4, bot=940,
    beats=dict(draw=0.1, drill=0.2, hit=1.2), labels=[dict(text="nobody on Earth can yet honestly tell you", depth=5.2, at="@nobody on Earth", bg=YEL)]),
    ticker=TICK_END))
at("The cores are being tested this winter", live(dict(type="breaking", img=img("cand_60"), at=0.1, kicker="DEVELOPING STORY",
    headline="CORES IN THE LAB THIS WINTER — RESULTS TO FOLLOW", sub="We'll walk through them, line by line", subAt="@we'll be here"), ticker=TICK_END))
at("Because the most interesting version", words([W_("THE MOST INTERESTING VERSION", y=440, at=0.0, size=100),
                                                  W_("WAS NEVER THE HEADLINE.", y=600, at="@never the headline", size=110, color=YEL)], ground="dark"))
at("It's the truth", words([W_("IT'S THE TRUTH.", y=540, at=0.1, size=170, color="#F4F6FA")], ground="dark",
                          overlays=[dict(type="fadeout", d=1.6)]))

edl.main(music=[
    dict(at=None, track="Cinematic Tension Build.mp3", db=-1),
    dict(at="Let's start with what we can verify", track="10_Industrial_Cinematic_Investigation.mp3", db=-1, lead=-1.0),
    dict(at="So what is the Durupınar formation, stripped", track="06_SCP-x6x_Hopes_Mysterious.mp3", db=0, lead=-1.0),
    dict(at="Now — why this hillside", track="12_Magic_Forest_Dark_Cello.mp3", db=0, lead=-1.0),
    dict(at="Now we arrive at what the current team says is different", track="Dramatic Piano Pulse.mp3", db=-1, lead=-1.0),
    dict(at="So what do geologists", track="08_Man_Down_Tension_Strings.mp3", db=-1, lead=-1.0),
    dict(at="So let's lay the pieces side by side", track="Silent Tension Piano.mp3", db=0, lead=-0.8),
    dict(at="Here's the good news, and it's real", track="11_Unanswered_Questions_Mystery.mp3", db=0, lead=-0.8),
    dict(at="So — did they drill into Noah's Ark", track="09_Thunder_Dreams_Dark_Drone.mp3", db=0, lead=-0.8),
    dict(at="One last thought, for viewers of every background", track="Mark Jubel - Efteraar.mp3", db=0, lead=-0.8),
])
