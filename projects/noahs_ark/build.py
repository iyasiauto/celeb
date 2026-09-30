"""
Noah's Ark Confirmed After 4,300 Years? What We Actually Know
Faceless investigative documentary - edit decision list and build.

Every shot is cued by the words it lands on (`"Irish archbishop"`), resolved against
word timestamps of the finished voiceover, so the cut follows the narration exactly.
Inside a shot, "@<phrase>" times an element (a stamp, a pin, a strip) to its word.

    python build.py prep       prepare every picture, cutout and surface
    python build.py stills     one QA frame per scene -> stills/ + contact sheets
    python build.py render     render all scenes (resumable)
    python build.py mix        sound design + music + voiceover
    python build.py final      concat + mux -> final MP4
    python build.py all

Paths default to the working layout of this production; override with env vars.
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "docu"))

import edl                       # noqa: E402
from edl import *                # noqa: E402,F401,F403  (the shot helpers)

SP = os.environ.get("VIDEO_ROOT", os.environ.get("NOAH_ROOT", os.path.join(HERE, "..", "..", "media")))
edl.setup(
    name="Noahs_Ark_Confirmed_After_4300_Years",
    kit=os.environ.get("NOAH_KIT", f"{SP}/kit"),
    footage=os.environ.get("NOAH_FOOTAGE", f"{SP}/footage"),
    work=os.environ.get("NOAH_WORK", f"{SP}/work"),
    data=os.path.join(HERE, "data"),
    out=os.environ.get("NOAH_OUT", f"{SP}/out"),
    theme="paper", grade="doc", grain=5,
)

# Places (lon, lat)
DURUPINAR = (44.2317, 39.4403)
ARARAT = (44.2983, 39.7019)
DOGUBAYAZIT = (44.083, 39.547)
TENDUREK = (43.87, 39.37)
SIVAS = (37.035, 39.745)
ARMAGH = (-6.654, 54.350)
SYDNEY = (151.18, -33.87)
PETERSBURG_KY = (-84.60, 38.62)       # Ark Encounter is at Williamstown; the region reads the same

# --------------------------------------------------------------------- EDL
# (cue, scene): cue is a phrase of the script (the cut lands on its first word),
# a float (absolute seconds) or None (continue: split the previous span evenly).

A089 = "cand_089"

# ---------------------------------------------------------------- cold open
at(0.0, stat("4,300", "YEARS", "", bg=A089, size=300, align="center", y=300, count=True, countFor=1.8, dim=0.55,
             overlays=[dict(type="fadein", d=0.8)]))
at("That's the number in the title", card("ind1_01", focus=(0.5, 0.86), zoom=1.55, height=980))
at("before we go anywhere near the mountain", clip(425, zoom=1.04, then=(557, 11)))
at("Because it doesn't come from Turkey", words([
    W_("NOT FROM TURKEY.", y=330, at=0.05),
    W_("NOT FROM A LAB.", y=540, at="@It doesn't come from a laboratory"),
    W_("NOT FROM THE GROUND.", y=750, at="@anything pulled out of the ground", color="#D9A441")], bg="cand_13"))
at("It comes from arithmetic", clip(435, zoom=1.05))
at("Irish archbishop", dict(type="map", stops=[
        dict(at=0, lon=15, lat=40, scale=900), dict(at=2.2, lon=-6.5, lat=54.2, scale=5200, d=2.2)],
    highlight=[dict(id="IRL", at=0.4), dict(id="GBR", at=0.4, fill="rgba(47,150,168,.35)")],
    pins=[dict(lon=ARMAGH[0], lat=ARMAGH[1], label="Armagh", sub="Seat of Archbishop James Ussher", at=1.9, side="right")]))
at("In the 1650s, James Ussher", collage([
    pc("cand_464", 560, 520, 640, rot=-4, at=0.05, grade="sepia"),
    dict(k="cut", img=cutout("vintage_hand writing.png", keyline=6, red=False, height=700), x=1400, y=640, h=620, at=0.5, from_="up"),
    title_("JAMES USSHER", 1330, 190, at=0.2, size=120, underline=True),
    strip("Archbishop of Armagh", 1330, 300, at=0.8, rot=-1.5),
    stamp("1650s", 470, 900, at="@sat down", rot=-7)], bg="map"))
at("sat down with the genealogies", clip(465, zoom=1.04))
at("His conclusion", dict(type="ledger", lines=[
        dict(text="Creation of the world .............. 4004 BC", at=0.2, y=230),
        dict(text="Creation to the Flood .............. 1,656 years", at=1.2, y=350),
        dict(text="The Great Flood of Noah .......... 2348 BC", at="@in the year 2348", y=500, color="#8a1a10", size=72)],
    ruleY=455, ruleAt=2.0, ruleW=1200, circle=dict(x=1350, y=545, rx=220, ry=70, at="@before Christ")))
at("Do the math from today", stat("4,373", "FROM 2348 BC TO 2026", "years ago — “4,300” in round numbers", bg="cand_325",
                                  countFor=2.2, noteAt=5.0, source="Ussher, Annales Veteris Testamenti (1650)"))
at("That calculation became enormously influential", clip(62, zoom=1.04))
at("printed in the margins of Bibles", clip(148, zoom=1.06, then=(252,)))
at("it's still the date many believers", clip(441, skip=3.0, grade="none", zoom=1.03))
at("Now — here's why I'm telling you this", photo("cand_074", move="in", focus=[0.5, 0.62], zoom=1.18))
at("In September 2026, a research team", photo("cand_305", move="in", focus=[0.45, 0.5],
                                               chip="September 2026 · Ağrı Province, Turkey"))
at("into a boat-shaped formation", photo("cand_31", move="left", zoom=1.12))
at("and headlines around the world", dict(type="headlines", items=[
    dict(text="NOAH'S ARK CONFIRMED?", x=820, y=290, rot=-3, at=0.1, size=96),
    dict(text="DRILLING BEGINS AT BOAT-SHAPED 'ARK' SITE", x=1090, y=560, rot=2, at="@asking whether", size=62, style="red"),
    dict(text="...AFTER 4,300 YEARS?", x=780, y=820, rot=-1.5, at="@after four thousand", size=84, style="tan")]))
at("But no laboratory has dated", clip(396, zoom=1.05, chip="Laboratory dates so far: none", chip_at=1.2))
at("Not one sample", collage([
    pc("cand_144", 960, 500, 900, rot=-2, at=0.0, grade="doc"),
    stamp("NOT DATED", 1080, 780, at="@Not one splinter", rot=-9, size=120)], bg="dark"))
at("The number in those headlines isn't a measurement", words([
    W_("A MEASUREMENT", y=420, at=0.1, strike="@it's a tradition", size=140),
    W_("A TRADITION.", y=660, at="@it's a tradition", color="#D9A441", size=170)], bg="cand_381", dim=0.78))
at("A venerable, meaningful tradition", clip(486, grade="none", zoom=1.03))
at("but a tradition, not a test result", clip(467, grade="none", zoom=1.03))
at("And that distinction", dict(type="split", left=img("cand_500", "none"), right=img("cand_252", "doc"),
                                 leftLabel="What we inherit", rightLabel="What we measure", rightFocus=[0.55, 0.5]))
at("is the entire story of the Durupınar formation", clip(38, zoom=1.03, chip="The Durupınar formation", chip_at=0.6))
at("Because the honest question", dict(type="title", img=img(A089), kicker="AN INVESTIGATION", title="NOAH'S ARK",
                                       subtitle="Confirmed after 4,300 years?", tagline="WHAT WE ACTUALLY KNOW"))
at("So here's what we're going to do", dict(type="baskets", reveal=True, at=0.3, gap=0.7))
at("What we know — facts verified", dict(type="baskets", active=0, focusAt=0.1, stampAt=1.4))
at("What is claimed — real observations", dict(type="baskets", active=1, focusAt=0.1, stampAt=1.4))
at("And what remains unknown", dict(type="baskets", active=2, focusAt=0.1, stampAt=1.4))
at("If you value investigations", clip(381, zoom=1.05))
at("refuse to blur the line", photo("cand_308", move="in", zoom=1.12))

# -------------------------------------------------------- basket one: known
at("Basket one", chapter("01", "BASKET ONE", "WHAT WE ACTUALLY KNOW", "cand_20"))
at("Start with the object itself", clip(504, zoom=1.03))
at("On the slopes of Mount Tendürek", dict(type="map", stops=[
        dict(at=0, lon=28, lat=38, scale=950),
        dict(at=3.0, lon=36, lat=39.2, scale=2900, d=3.0),
        dict(at="@near the town of", lon=44.05, lat=39.55, scale=36000, d=3.4)], detail="geo_hi.json",
    highlight=[dict(id="TUR", at=0.6), dict(id="TUR-2307", at="@Ağrı Province", fill="rgba(217,164,65,.45)")],
    names=[dict(text="Turkey", lon=34.5, lat=39.2, at=1.2, out="@near the town of"),
           dict(text="Iran", lon=44.62, lat=39.40, at="@close to the Iranian border", size=40),
           dict(text="Armenia", lon=44.55, lat=39.93, at="@Greater Mount Ararat", size=30)],
    dots=[dict(lon=DOGUBAYAZIT[0], lat=DOGUBAYAZIT[1], label="Doğubayazıt", at="@near the town of", out="@there is a long"),
          dict(lon=ARARAT[0], lat=ARARAT[1], label="Mount Ararat · 5,137 m", at="@Greater Mount Ararat"),
          dict(lon=TENDUREK[0], lat=TENDUREK[1], label="Mt. Tendürek", at="@On the slopes")],
    routes=[dict(**{"from": list(DURUPINAR)}, to=list(ARARAT), at="@twenty-nine kilometers", d=1.0, label="29 km", lx=90, ly=10)],
    pins=[dict(lon=DURUPINAR[0], lat=DURUPINAR[1], label="Durupınar", sub="the boat-shaped formation",
               at="@there is a long", side="left")]))
at("Roughly 157 meters", stat("157 m", "LENGTH OF THE FORMATION", "about 515 feet — its most-cited measurement", bg="cand_06", countFor=1.4))
at("From the air, it looks uncannily", collage([
    pc("ind2_01", 960, 540, 1560, rot=0, at=0.0, pad=0, tape=False),
    dict(k="arrow", **{"from": [300, 180]}, to=[800, 250], at="@pointed at one end", bend=40),
    strip("POINTED END", 330, 150, at="@pointed at one end", rot=-2),
    dict(k="arrow", **{"from": [1620, 900]}, to=[1120, 860], at="@rounded at the other", bend=-40),
    strip("ROUNDED END", 1600, 960, at="@rounded at the other", rot=2),
    strip("RAISED EDGES, FULL LENGTH", 1300, 160, at="@with raised edges", rot=1.5)], bg="dark", z1=1.03))
at("That's not a claim", clip(16, zoom=1.03))
at("The shape is the one thing", collage([
    pc("cand_069", 900, 500, 1100, rot=-2.5, at=0.0),
    stamp("UNDISPUTED", 1180, 860, at="@nobody on any side disputes", rot=-7, color="#1A1A1A", size=110)]))
at("We also know how the modern story began", photo("cand_199", grade="doc", move="in", zoom=1.08))
at("In 1959, a Turkish army cartographer", collage([
    pc("cand_05", 600, 540, 700, rot=-3, at=0.0, grade="bw", crop=(0.18, 0.1, 1.0, 1.0)),
    title_("1959", 1350, 250, at=0.3, size=180),
    strip("Capt. İlhan Durupınar — Turkish Army cartographer", 1330, 450, at="@named Captain", rot=-1),
    strip("NATO aerial mapping mission", 1330, 560, at="@NATO mapping mission", rot=1),
    dict(k="cut", img=cutout("vintage_magnifying_glass_hand.png", red=False), x=1400, y=820, h=420, at="@when he noticed", **{"from": "right"})],
    bg="paper"))
at("Photographs of the site reached a wide audience", clip(316, grade="none", zoom=1.03,
                                                            chip="LIFE magazine · September 5, 1960", chip_at=0.6))
at("Life magazine published images", clip(162, grade="none", zoom=1.05))
at("and suddenly a remote hillside", photo("cand_45", grade="doc", crop=(0.0, 0.0, 1.0, 0.86), move="in", zoom=1.14))
at("was being discussed around the world", dict(type="map", stops=[
        dict(at=0, lon=35, lat=30, scale=430), dict(at=6, lon=10, lat=35, scale=420, d=6)],
    highlight=[dict(id="TUR", at=0.2)],
    routes=[dict(**{"from": list(DURUPINAR)}, to=[-73.98, 40.75], at=0.8, d=1.8),
            dict(**{"from": list(DURUPINAR)}, to=[-0.12, 51.50], at=1.3, d=1.2),
            dict(**{"from": list(DURUPINAR)}, to=[2.35, 48.85], at=1.6, d=1.2),
            dict(**{"from": list(DURUPINAR)}, to=[151.2, -33.9], at=1.9, d=1.8),
            dict(**{"from": list(DURUPINAR)}, to=[-43.2, -22.9], at=2.3, d=1.8)],
    pins=[dict(lon=DURUPINAR[0], lat=DURUPINAR[1], label="Durupınar", sub="1960", at=0.1, side="right", gap=120, size=40)]))
at("We know what happened next", collage([
    pc("cand_46", 820, 520, 1000, rot=-2, at=0.0, crop=(0.12, 0.0, 0.86, 1.0)),
    stamp("DOCUMENTED", 1250, 850, at="@because it was documented", rot=-6, color="#1A1A1A")]))
at("In 1960, an American-led expedition", dict(type="timeline", img=img("cand_46", "doc", (0.12, 0.0, 0.86, 1.0)),
    events=[dict(year="1959", label="Aerial photo reveals the shape"),
            dict(year="1960", label="An American-led expedition tests it")],
    stops=[dict(i=0, at=0.0), dict(i=1, at=1.6)]))
at("The team included surveyor Arthur Brandenberger", collage([
    title_("ARTHUR BRANDENBERGER", 960, 200, at=0.1, size=110, underline=True),
    strip("Surveyor · 1960 expedition", 960, 320, at=0.6),
    dict(k="note", text="personally believed the ark might be found", x=620, y=640, w=460, rot=-4, at="@personally believed"),
    stamp("NOT A HOSTILE INVESTIGATION", 1250, 860, at="@no hostile investigation", rot=-6, size=72)], bg="paper"))
at("They dug into the formation", clip(9, zoom=1.04))
at("They used dynamite", words([W_("DYNAMITE.", y=540, at=0.05, size=230, color="#D62E1F")], bg="cand_46", crop=(0.12, 0.0, 0.86, 1.0),
                               overlays=[dict(type="flash", at=0.05)]))
at("And their official conclusion", collage([
    title_("EXPEDITION FINDINGS · 1960", 960, 170, at=0.05, size=86),
    strip("No visible archaeological remains.", 960, 380, at="@no visible archaeological remains", size=44),
    strip("A natural formation.", 960, 510, at="@a natural formation", size=44),
    strip("“A freak of nature.”", 960, 640, at="@a freak of nature", size=44),
    stamp("NATURAL FORMATION", 960, 860, at="@a freak of nature", rot=-5, size=100)], bg="map"))
at("That was the first time the site was physically tested", collage([
    pc("cand_46", 960, 520, 1200, rot=1.5, at=0.0, crop=(0.12, 0.0, 0.86, 1.0)),
    stamp("TEST 1: FAILED", 960, 820, at="@failed the test", rot=-6, size=120)], bg="dark"))
at("It would not be the last", clip(66, zoom=1.03))
at("in 1987, the Turkish government", stat("1987", "TURKISH GOVERNMENT DESIGNATION", "a Noah's Ark national heritage site",
                                          bg="cand_20", count=False, noteAt="@national heritage site"))
at("complete with visitor infrastructure", clip(403, zoom=1.03, chip="Noah's Ark Visitor Center", chip_at=0.5))
at("You can visit it today", clip(22, zoom=1.04))
at("Now — hold that fact carefully", words([
    W_("“OFFICIAL”", y=470, at=0.1, size=240, color="#D9A441"),
    W_("a case study in how a word misleads", y=690, at="@a perfect case study", size=64, font="GaramondI")], bg="cand_082"))
at("A government can declare a site a national park", collage([
    pc("cand_082", 820, 500, 1050, rot=-2, at=0.0),
    stamp("NATIONAL PARK", 1250, 850, at=0.9, rot=-7, color="#2F6B3A")]))
at("Governments do that for cultural", checklist("WHY GOVERNMENTS DESIGNATE SITES", [
    dict(text="Cultural", at=0.2, mark="dot"), dict(text="Historical", at="@historical", mark="dot"),
    dict(text="Religious", at="@religious", mark="dot"), dict(text="Tourism", at="@and tourism reasons", mark="dot")],
    bg="cand_104", size=76, gap=150, y0=260))
at("and for a region eager", clip(577, zoom=1.04, chip="Doğubayazıt, Ağrı Province"))
at("What a government cannot do", words([W_("YOU CAN'T DECLARE", y=430, at=0.1, size=110),
                                         W_("GEOLOGY.", y=610, at="@declare geology", size=220, color="#D9A441")], bg="cand_267"))
at("Turkey's designation tells us", clip(120, zoom=1.03))
at("It tells us nothing", photo("cand_13", move="in", focus=[0.5, 0.45], zoom=1.2, chip="What's underneath?", chip_at=1.2))
at("Official recognition is not scientific confirmation", collage([
    title_("RECOGNITION", 960, 330, at=0.05, size=150),
    title_("IS NOT", 960, 500, at="@is not scientific", size=110, color="#D62E1F"),
    title_("CONFIRMATION", 960, 670, at="@scientific confirmation", size=150),
    stamp("CATEGORY ERROR", 1300, 900, at="@category error", rot=-6, size=90)], bg="paper"))
at("And we know the story of the man", depth("cand_299", subject=[0.5, 0.45], crop=(0.0, 0.0, 0.5, 0.78), grade="bw",
                                            hit=1.2, keys=[[0.5, 0.3, 1.0], [0.5, 0.33, 1.05]]))
at("Ron Wyatt was a nurse anesthetist", depth("cand_299", subject=[0.5, 0.55], crop=(0.0, 0.0, 0.5, 0.78), grade="bw",
                                             hit=0.0, keys=[[0.5, 0.33, 1.05], [0.5, 0.36, 1.1]], lower=("Ron Wyatt", "Nurse anesthetist · Tennessee", 0.4)))
at("not an archaeologist", words([
    W_("NOT AN ARCHAEOLOGIST.", y=380, at=0.05, size=120),
    W_("NOT A GEOLOGIST.", y=560, at="@not a geologist", size=120),
    W_("BIBLICAL ARCHAEOLOGY", y=760, at="@to biblical archaeology", size=100, color="#D9A441")], bg="cand_299", grade="bw", crop=(0.0, 0.0, 1.0, 0.78)))
at("Starting in 1977", photo("cand_300", crop=(0.44, 0.0, 1.0, 1.0), move="in", chip="1977 · Wyatt's surveys begin", chip_at=0.4))
at("the raised edges were hull timbers", collage([
    pc("cand_125", 880, 520, 1120, rot=-2, at=0.0),
    strip("“HULL TIMBERS” — Wyatt", 1350, 880, at=0.5, rot=2, size=40)], bg="dark"))
at("his metal detectors had found iron fittings", photo("cand_29", move="in", focus=[0.5, 0.42], zoom=1.2,
                                                         chip="Wyatt's “iron fitting” readings", chip_at=0.4))
at("and massive carved stones", clip(96, zoom=1.04))
at("were the ark's anchor stones", depth("cand_310", subject=[0.7, 0.6], hit=0.4, chip="“Anchor stone”"))
at("Over his career, Wyatt also claimed", collage([
    pc("cand_299", 420, 520, 520, rot=-3, at=0.0, grade="bw", crop=(0.0, 0.0, 0.5, 0.78)),
    dict(k="pin", x=420, y=250, at=0.3),
    strip("THE ARK OF THE COVENANT", 1320, 260, at="@the Ark of the Covenant", rot=-2, size=44),
    dict(k="pin", x=1320, y=225, at="@the Ark of the Covenant"),
    strip("THE “TRUE” MOUNT SINAI", 1380, 540, at="@the true Mount Sinai", rot=1.5, size=44),
    dict(k="pin", x=1380, y=505, at="@the true Mount Sinai"),
    strip("CHARIOT WHEELS, RED SEA FLOOR", 1300, 820, at="@chariot wheels", rot=-1, size=44),
    dict(k="pin", x=1300, y=785, at="@chariot wheels"),
    dict(k="string", pts=[[420, 250], [1320, 225]], at="@the Ark of the Covenant", d=0.6),
    dict(k="string", pts=[[420, 250], [1380, 505]], at="@the true Mount Sinai", d=0.6),
    dict(k="string", pts=[[420, 250], [1300, 785]], at="@chariot wheels", d=0.6)], bg="cork"))
at("And we know how his own inner circle broke", photo("cand_299", grade="bw", crop=(0.0, 0.0, 1.0, 0.78), move="in", zoom=1.1))
at("David Fasold, a marine salvage expert", depth("cand_298", subject=[0.62, 0.45], hit=0.5, keys=[[0.55, 0.28, 1.0], [0.58, 0.31, 1.06]],
                                                 lower=("David Fasold", "Marine salvage expert · Wyatt's partner in the 1980s")))
at("eventually concluded the site was natural", collage([
    pc("cand_298", 600, 540, 560, rot=-3, at=0.0),
    stamp("NATURAL", 1300, 520, at="@was natural", rot=-8, size=150)], bg="paper"))
at("In 1996 he co-authored", collage([
    title_("1996", 700, 300, at=0.05, size=220),
    strip("A co-authored geology paper:", 1250, 520, at=0.5, size=42),
    strip("the site is natural", 1250, 630, at="@saying so", size=42),
    dict(k="cut", img=cutout("vintage_stack_of_books.png", red=False), x=560, y=780, h=380, at=0.3),
    stamp("PUBLISHED", 1300, 870, at="@saying so", rot=-6, color="#1A1A1A")], bg="paper"))
at("In 1997, under oath", dict(type="map", stops=[
        dict(at=0, lon=60, lat=15, scale=520), dict(at=3.5, lon=110, lat=-10, scale=560, d=3.5)],
    routes=[dict(**{"from": list(DURUPINAR)}, to=list(SYDNEY), at=0.6, d=2.2, dash=True)],
    pins=[dict(lon=SYDNEY[0], lat=SYDNEY[1], label="Australia, 1997", sub="Fasold testifies under oath", at=2.4, side="left", size=46)]))
at("he called the claim that Noah's Ark", quote("“Absolute BS.”", who="David Fasold, under oath, 1997", bg="cand_298",
                                                 size=150, highlight=["absolute"], rate=2.2))
at("That's documented history", clip(41, zoom=1.03))
at("That's the end of basket one", checklist("BASKET ONE · WHAT WE KNOW", [
    dict(text="A real shape", at="@A real shape"),
    dict(text="A documented discovery, 1959", at="@A documented discovery"),
    dict(text="A failed physical test, 1960", at="@A failed physical test", mark="no"),
    dict(text="A designation that means culture, not science", at="@A government heritage", mark="dot"),
    dict(text="A co-founder who walked away", at="@And a believer-driven", mark="no")], bg="cand_074"))
at("Everything else in this story", dict(type="baskets", active=-1, stampAt=0.6))

# -------------------------------------------------------- basket two: claimed
at("Basket two", chapter("02", "BASKET TWO", "WHAT IS CLAIMED", "cand_12"))
at("The claims come from a research organization", dict(type="tv", img=img("cand_256", "none", (0.0, 0.0, 1.0, 0.8)), focus=[0.22, 0.5],
    overlays=[dict(type="lower", name="Andrew Jones", role="Noah's Ark Scans", at="@led by Andrew Jones", x=110, y=860)]))
at("an American who has been visiting", clip(387, zoom=1.04, chip="Noah's Ark Scans · in the field", chip_at=0.8, then=(395,)))
at("His conviction is not hidden", clip(571, zoom=1.04))
at("I believe this is Noah's Ark", quote("“I believe this is Noah's Ark.”", who="Andrew Jones, Noah's Ark Scans",
                                        bg="cand_122", highlight=["believe"], size=96, rate=4.5))
at("In September 2026, his team began", photo("cand_169", move="in", focus=[0.4, 0.55], chip="September 2026 · First deep core drilling"))
at("working under Turkish government authorization", photo("cand_11", move="in", focus=[0.7, 0.5], fit="contain"))
at("with archaeologists from Sivas Cumhuriyet University", dict(type="map", stops=[
        dict(at=0, lon=39.8, lat=39.3, scale=4300), dict(at=4, lon=40.4, lat=39.4, scale=4500, d=4)],
    highlight=[dict(id="TUR", at=0.1)],
    routes=[dict(**{"from": list(SIVAS)}, to=list(DURUPINAR), at=1.0, d=1.8, dash=True)],
    pins=[dict(lon=SIVAS[0], lat=SIVAS[1], label="Sivas Cumhuriyet University", sub="led by Prof. Cenker Atila", at=0.2, side="left", size=34, gap=90),
          dict(lon=DURUPINAR[0], lat=DURUPINAR[1], label="Durupınar", at=2.4, side="right", size=40, gap=120)]))
at("The expedition is real", words([W_("THE EXPEDITION IS REAL.", y=440, at=0.05, size=120),
                                    W_("THE PERMITS ARE REAL.", y=640, at="@The permits are real", size=120, color="#D9A441")], bg="cand_12"))
at("What follows is what the team says", collage([
    strip("NOAH'S ARK SCANS", 960, 540, at=0.1, size=56, bg="#1A1A1A", color="#F3EEE2"),
    dict(k="pin", x=960, y=500, at=0.2),
    pc("cand_06", 360, 250, 380, rot=-4, at=0.5, caption="1 · Dimensions"),
    pc("cand_15", 1560, 250, 420, rot=3, at=0.9, caption="2 · Scans"),
    pc("cand_157", 380, 820, 250, rot=3, at=1.3, caption="3 · Soil"),
    pc("cand_60", 1560, 820, 380, rot=-3, at=1.7, caption="4 · Drilling"),
    dict(k="string", pts=[[960, 520], [360, 240]], at="@every claim traces back", d=0.5),
    dict(k="string", pts=[[960, 520], [1560, 240]], at="@every claim traces back", d=0.6),
    dict(k="string", pts=[[960, 520], [380, 760]], at="@every claim traces back", d=0.7),
    dict(k="string", pts=[[960, 520], [1560, 780]], at="@every claim traces back", d=0.8),
    stamp("ONE SOURCE", 960, 700, at="@this one source", rot=-5, size=90)], bg="cork"))
at("Claim number one", words([W_("CLAIM 01", y=400, at=0.05, size=60, color="#D9A441", font="BarlowB"),
                              W_("THE DIMENSIONS", y=540, at=0.3, size=170)], bg="cand_122"))
at("Three hundred cubits", clip(441, skip=8.0, grade="none", zoom=1.04, chip="Genesis 6:15 · 300 cubits long", chip_at=0.8))
at("converts to roughly 515 feet", dict(type="measure", title="LENGTH: 300 CUBITS", pxPerFt=2.7, bars=[
    dict(label="ROYAL CUBIT (≈20.6 IN)", ft=515, value="≈515 FT", at=0.1),
    dict(label="THE DURUPINAR FORMATION", ft=515, value="≈515 FT", at="@The formation's length", color="#D62E1F")],
    stamp=dict(text="A MATCH?", at="@cornerstone of its case", x=1250, y=820)))
at("But a cubit was never a fixed unit", dict(type="measure", title="LENGTH: 300 CUBITS", pxPerFt=2.7, bars=[
    dict(label="ROYAL CUBIT (≈20.6 IN)", ft=515, value="≈515 FT", at=0.0, grow=0.01),
    dict(label="COMMON CUBIT (≈18 IN)", ft=450, value="≈450 FT", at="@use the shorter common cubit", color="#8C8C8C"),
    dict(label="THE DURUPINAR FORMATION", ft=515, value="≈515 FT", at=0.0, grow=0.01, color="#D62E1F")],
    stamp=dict(text="DEPENDS ON THE RULER", at="@shrinks to around", x=1000, y=870)))
at("And the width doesn't cooperate", dict(type="measure", title="WIDTH: 50 CUBITS", pxPerFt=9.0, bars=[
    dict(label="50 ROYAL CUBITS", ft=86, value="≈86 FT", at="@fifty royal cubits"),
    dict(label="THE FORMATION AT ITS MIDDLE", ft=138, value="≈138 FT", at="@while the formation spans", color="#D62E1F")],
    stamp=dict(text="NO MATCH", at="@at its middle", x=1300, y=820)))
at("Supporters say a collapsing hull", clip(597, zoom=1.03, skip=2.0))
at("Maybe", words([W_("MAYBE.", y=540, at=0.0, size=200)], bg="cand_125"))
at("But a theory that counts matches", collage([
    title_("MATCH", 520, 300, at=0.1, size=110, color="#2F6B3A"),
    strip("counted as evidence", 520, 430, at="@counts matches as evidence", size=40),
    title_("MISMATCH", 1400, 300, at="@explains away mismatches", size=110, color="#D62E1F"),
    strip("explained away", 1400, 430, at="@explains away mismatches", size=40),
    stamp("UNTESTABLE", 960, 760, at="@impossible to test", rot=-6, size=140),
    strip("…and so impossible to confirm", 960, 950, at="@impossible, therefore", size=40)], bg="paper"))
at("Claim number two", words([W_("CLAIM 02", y=400, at=0.05, size=60, color="#D9A441", font="BarlowB"),
                              W_("THE SCANS", y=540, at=0.3, size=170)], bg="cand_252", crop=(0.0, 0.12, 1.0, 1.0)))
at("The team has run ground-penetrating radar", clip(388, zoom=1.04, chip="Ground-penetrating radar", chip_at=0.4))
at("electrical resistivity tomography", clip(414, zoom=1.04, chip="Electrical resistivity tomography", chip_at=0.3))
at("LiDAR, thermal imaging", clip(415, zoom=1.06, chip="LiDAR · thermal · audio-magnetotelluric", chip_at=0.3, then=(391, 306)))
at("mapping, it says, as deep as", stat("300 m", "CLAIMED SURVEY DEPTH", "“mapping, it says, as deep as three hundred meters”", bg="cand_241", countFor=1.2))
at("It reports long straight lines", photo("ind2_04", move="in", fit="contain", grade="none", zoom=1.1))
at("interpreted as decks", collage([
    pc("cand_208", 760, 480, 1100, rot=-2, at=0.0, grade="none"),
    strip("“DECKS”", 1500, 300, at="@interpreted as decks", rot=-3, size=48),
    strip("“CORRIDORS”", 1560, 520, at="@corridors", rot=2, size=48),
    strip("“CHAMBERS”", 1480, 740, at="@and chambers", rot=-1.5, size=48)], bg="dark"))
at("Those radar images are the viral heart", card("ind1_03", focus=(0.5, 0.82), zoom=1.45, height=980))
at("Now, ground-penetrating radar genuinely detects", clip(243, zoom=1.05, then=(14, 253)))
at("places where material changes", clip(55, zoom=1.04))
at("But straight lines and right angles", words([
    W_("STRAIGHT LINES", y=320, at=0.05, size=120), W_("RIGHT ANGLES", y=490, at="@and right angles", size=120),
    W_("ARE NOT A HUMAN SIGNATURE", y=700, at="@a human signature", size=100, color="#D9A441")], bg="cand_252", crop=(0.0, 0.12, 1.0, 1.0)))
at("Limestone fractures along clean", clip(329, zoom=1.06, chip="Limestone joints", chip_at=0.5))
at("often perpendicular joints", clip(454, zoom=1.04))
at("geologists see right angles", photo("cand_076", move="in", zoom=1.15, chip="Natural right angles", chip_at=0.8))
at("Radar can show you a boundary", spot("cand_252", center=[0.52, 0.52], radius=[0.09, 0.11], label="A boundary", hit=0.3, zoom=1.25))
at("And the raw scan data has never been released", collage([
    dict(k="note", text="RAW SCAN DATA", x=720, y=500, w=600, rot=-3, at=0.0, bg="#D8BC80", size=80),
    stamp("NOT RELEASED", 1150, 700, at="@has never been released", rot=-8, size=120)], bg="paper"))
at("every rendered image of", collage([
    pc("cand_208", 520, 420, 640, rot=-5, at=0.0, grade="none"),
    pc("ind2_05", 1380, 380, 700, rot=4, at=0.3, grade="none"),
    pc("cand_170", 980, 700, 420, rot=-1, at=0.6, grade="none"),
    strip("Rendered by: the same team that believes", 960, 960, at="@produced by the same team", size=42)], bg="dark"))
at("Real surveys, real anomalies", words([
    W_("REAL SURVEYS.", y=260, at=0.0, size=110), W_("REAL ANOMALIES.", y=410, at="@real anomalies", size=110),
    W_("REAL CLAIMS.", y=560, at="@real claims", size=110),
    W_("NOT CONFIRMATIONS.", y=760, at="@not confirmations", size=130, color="#D62E1F")], bg="cand_252", crop=(0.0, 0.12, 1.0, 1.0)))
at("Claim number three", words([W_("CLAIM 03", y=400, at=0.05, size=60, color="#D9A441", font="BarlowB"),
                                W_("THE SOIL", y=540, at=0.3, size=170)], bg="cand_142"))
at("In 2024, the project collected", clip(24, zoom=1.04, chip="2024 · Soil sampling", chip_at=0.4))
at("88 soil samples", stat("88", "SOIL SAMPLES, 2024", "from inside and outside the outline", bg="cand_157", countFor=1.2))
at("and reports that interior soil", collage([
    pc("cand_142", 480, 540, 560, rot=-3, at=0.0),
    dict(k="stat", value="3×", label="organic matter", x=1150, y=380, at="@three times more organic", rot=-3),
    dict(k="stat", value="+38%", label="potassium", x=1500, y=720, at="@38 percent more potassium", rot=3, bg="#D9A441"),
    strip("Interior vs. exterior soil — as reported", 1300, 970, at=0.6, size=36)], bg="paper"))
at("presented as the chemical ghost", clip(398, zoom=1.06, chip="“The chemical ghost of a wooden vessel”?", chip_at=0.3, then=(397,)))
at("Vegetation above the formation", clip(21, zoom=1.03, then=(8, 42)))
at("visible from the air", spot("cand_074", center=[0.5, 0.62], radius=[0.12, 0.2], label="Greener growth", hit=0.2, zoom=1.15))
at("But the lab work has never been published", collage([
    pc("cand_182", 760, 520, 720, rot=-3, at=0.0, grade="none"),
    stamp("UNPUBLISHED", 1250, 820, at="@never been published", rot=-7, size=110),
    strip("No methods. No data. No outside review.", 1250, 250, at="@for outside review", size=38)], bg="paper"))
at("And the shape itself offers a rival explanation", photo("cand_125", move="in", zoom=1.12))
at("an elongated oval with raised edges is a bowl", collage([
    pc("cand_089", 960, 520, 1500, rot=0, at=0.0, pad=0, tape=False),
    dict(k="arrow", **{"from": [760, 110]}, to=[900, 420], at="@and bowls collect rainwater", bend=30, color="#4FA3D9"),
    dict(k="arrow", **{"from": [1180, 110]}, to=[1060, 420], at="@and bowls collect rainwater", bend=-30, color="#4FA3D9"),
    strip("A BOWL", 960, 900, at="@is a bowl", size=56, rot=-2)], bg="dark"))
at("Geologist Andrew Snelling", collage([
    title_("ANDREW SNELLING", 960, 190, at=0.05, size=120, underline=True),
    strip("Geologist", 960, 310, at=0.4, size=40),
    dict(k="note", text="young-earth creationist — believes the Flood literally happened", x=1300, y=620, w=520, rot=3, at="@young-earth creationist", size=42),
    dict(k="cut", img=cutout("vintage_holy_bible.png", red=False), x=560, y=680, h=520, at="@believes the flood")], bg="paper"))
at("points out that a wet depression", clip(70, zoom=1.03))
at("naturally grows richer vegetation", photo("cand_172", move="in", zoom=1.14, chip="Wet ground → richer growth", chip_at=0.6))
at("No ship required", words([W_("NO SHIP REQUIRED.", y=540, at=0.0, size=170)], bg="cand_172"))
at("His organization, Answers in Genesis", clip(520, zoom=1.03, chip="Ark Encounter · Kentucky", chip_at=0.4, then=(519,)))
at("has examined the Durupınar claims", collage([
    pc("cand_069", 820, 520, 1000, rot=-2, at=0.0),
    stamp("REJECTED", 1250, 820, at="@and rejected them", rot=-7, size=140),
    strip("— by creationist geologists", 1250, 960, at="@and rejected them", size=38)], bg="dark"))
at("Claim number four", words([W_("CLAIM 04", y=400, at=0.05, size=60, color="#D9A441", font="BarlowB"),
                               W_("THE DRILLING", y=540, at=0.3, size=170)], bg="cand_305",
                              overlays=[dict(type="flash", at="@the drilling")]))
at("According to the project's press release", card("ind1_04", focus=(0.5, 0.82), zoom=1.45, height=980))
at("cores pulled from as deep as", stat("18 m", "DEEPEST CORE", "about sixty feet", bg="cand_14", countFor=1.0))
at("contained layered sediments", photo("cand_60", move="in", focus=[0.7, 0.5], fit="contain",
                                         chip="Layered sediments · organic-rich intervals", chip_at=0.4))
at("and multiple cavities", clip(49, zoom=1.04, chip="Cavities", chip_at=0.5))
at("one of which kept filling with water", clip(50, zoom=1.06, chip="The “room”", chip_at="@dubbed a", then=(114, 74)))
at("And in one borehole inside the outline", photo("cand_161", move="up", fit="contain", zoom=1.1,
                                                    chip="4–5 m down: a layer too hard to drill", chip_at="@four to five meters"))
at("hard enough to shatter the bit", words([W_("THE BIT SHATTERED.", y=540, at="@shatter the bit", size=150, color="#D62E1F")],
                                           bg="cand_60", overlays=[dict(type="flash", at="@shatter the bit")]))
at("Jones's words", quote("“Harder than limestone.”", who="Andrew Jones", bg="cand_14", size=110, highlight=["harder"], rate=3.0))
at("with \"petrified or highly mineralized wood\"", collage([
    dict(k="cut", img=cutout("cand_312", red=True, height=700), x=720, y=560, h=380, at=0.0),
    strip("“petrified or highly mineralized wood”", 1150, 250, at=0.3, size=44),
    stamp("FOR LAB TESTING", 1300, 840, at="@third-party lab testing", rot=-6, size=100)], bg="paper"))
at("A day before drilling began", card("ind2_02", focus=(0.5, 0.25), zoom=1.3, height=1000))
at("one hundred percent", stat("100%", "CERTAINTY — BEFORE THE FIRST CORE", "that the formation is man-made", bg="cand_31", countFor=1.0))
at("So that's basket two", checklist("BASKET TWO · WHAT IS CLAIMED", [
    dict(text="Dimensions that match — under one ruler", at="@dimensions that match", mark="maybe"),
    dict(text="Scans showing boundaries", at="@scans showing boundaries", mark="maybe"),
    dict(text="Soil with elevated organics", at="@soil with elevated organics", mark="maybe"),
    dict(text="Cores with organic layers and cavities", at="@cores with organic layers", mark="maybe"),
    dict(text="One broken drill bit", at="@and one broken drill bit", mark="maybe")], bg="cand_31"))
at("every item observed or reported", collage([
    stamp("ONE TEAM", 560, 330, at=0.1, rot=-6, size=110, color="#1A1A1A"),
    stamp("NOT INDEPENDENTLY VERIFIED", 1180, 560, at="@none of it independently verified", rot=4, size=90),
    stamp("NOT PEER-REVIEWED", 900, 820, at="@published through peer review", rot=-5, size=110)], bg="paper"))

# -------------------------------------------------------- basket three: unknown
at("Which brings us to basket three", chapter("03", "BASKET THREE", "WHAT REMAINS UNKNOWN", "cand_308"))
at("And this is where our title's number", stat("4,300", "THE NUMBER IN THE TITLE", "…and the biggest unknown of all: time",
                                                bg="cand_336", count=False, noteAt="@is time itself"))
at("Nothing at Durupınar has ever been scientifically dated", collage([
    pc("cand_069", 900, 500, 1100, rot=-2, at=0.0),
    stamp("NEVER DATED", 1200, 860, at="@scientifically dated", rot=-7, size=130)], bg="dark"))
at("No radiocarbon analysis", checklist("SCIENTIFIC DATING AT DURUPINAR", [
    dict(text="Radiocarbon analysis", at=0.1, mark="no"),
    dict(text="Luminescence dating", at="@No luminescence", mark="no"),
    dict(text="Any laboratory date at all", at="@Nothing", mark="no")], bg="cand_267", size=76, gap=150, y0=300))
at("The four-thousand-three-hundred-year figure exists only", dict(type="ledger", lines=[
        dict(text="Creation of the world .............. 4004 BC", at=0.1, y=230, d=0.6),
        dict(text="Creation to the Flood .............. 1,656 years", at=0.8, y=350, d=0.6),
        dict(text="The Great Flood of Noah .......... 2348 BC", at=1.5, y=500, color="#8a1a10", size=72, d=0.6),
        dict(text="— arithmetic from genealogies, 1650s", at="@added up genealogies", y=700, size=54, font="Garamond")],
    ruleY=455, ruleAt=1.3, ruleW=1200, circle=dict(x=1350, y=545, rx=220, ry=70, at=2.4)))
at("And here's what makes that genuinely important", clip(400, zoom=1.05, then=(250,)))
at("for the first time in the site's history", clip(396, skip=1.0, zoom=1.08, chip="The unknowns are answerable", chip_at="@actually answerable"))
at("The cores now in cold storage", clip(404, zoom=1.05))
at("Petrified wood, if that's what", collage([
    dict(k="cut", img=cutout("cand_179", red=False, height=700), x=760, y=540, h=560, at=0.0),
    strip("growth rings", 1420, 380, at="@growth rings", rot=-2, size=44),
    strip("vessel structures", 1460, 560, at="@vessel structures", rot=2, size=44),
    dict(k="arrow", **{"from": [1300, 400]}, to=[960, 470], at="@growth rings", bend=30),
    dict(k="arrow", **{"from": [1320, 580]}, to=[1000, 600], at="@vessel structures", bend=-30)], bg="paper"))
at("visible under a microscope", photo("cand_188", move="in", zoom=1.2, chip="Under the microscope", chip_at=0.3, grade="none"))
at("That's a yes-or-no test", words([W_("YES", x=620, y=540, at=0.0, size=260, color="#6FBF73"),
                                     W_("or", x=960, y=560, at=0.25, size=90, font="GaramondI"),
                                     W_("NO", x=1300, y=540, at=0.45, size=260, color="#D62E1F")], bg="cand_189"))
at("The organic-rich layers can be radiocarbon dated", dict(type="timeline", img=img("cand_400" if False else "cand_24", "doc"),
    events=[dict(year="Today", label="Radiocarbon clock starts"),
            dict(year="4,300", label="years · the traditional flood era"),
            dict(year="50,000", label="years · practical limit of radiocarbon")],
    stops=[dict(i=0, at=0.0), dict(i=1, at="@a four-to-five-thousand-year-old"), dict(i=2, at="@within its range")]))
at("If the carbon comes back a few centuries old", collage([
    title_("IF IT COMES BACK…", 960, 120, at=0.0, size=70),
    strip("a few centuries old — or matching the sediments", 500, 330, at=0.3, size=36),
    stamp("ARK INTERPRETATION FINISHED", 500, 560, at="@the ark interpretation is finished", rot=-5, size=58),
    strip("near the traditional flood era", 1420, 330, at="@If it came back near", size=36),
    stamp("GEOLOGY IN CRISIS", 1420, 560, at="@would face a genuine crisis", rot=4, size=72, color="#1A1A1A")], bg="paper"))
at("The team says compositional, organic", dict(type="timeline", img=img("cand_12", "doc"),
    events=[dict(year="Sept 2026", label="Cores drilled"), dict(year="Winter", label="Compositional · organic · stratigraphic tests"),
            dict(year="2027", label="Radiocarbon dating · public statement")],
    stops=[dict(i=0, at=0.0), dict(i=1, at="@is scheduled through the winter"), dict(i=2, at="@with radiocarbon dating planned")]))
at("And there's a second route into the unknown", clip(50, skip=0.4, zoom=1.08))
at("The team has built a custom camera drone", clip(127, zoom=1.04, chip="GOPHER · camera drone", chip_at="@named GOPHER"))
at("designed to enter the radar-mapped voids", collage([
    title_("G.O.P.H.E.R.", 960, 260, at=0.0, size=150),
    strip("“Make thee an ark of gopher wood” — Genesis 6:14", 960, 400, at=0.4, size=40),
    pc("cand_14", 960, 790, 260, rot=-2, at=0.8)], bg="paper"))
at("As of today, it has not been deployed", collage([
    pc("cand_14", 820, 540, 420, rot=-3, at=0.0),
    stamp("NOT YET DEPLOYED", 1200, 620, at=0.5, rot=-7, size=100)], bg="dark"))
at("If it ever returns footage of worked timber", clip(519, skip=2.5, zoom=1.03, chip="Illustration: worked timber", chip_at=0.6))
at("the story of the century begins", words([W_("THE STORY OF THE CENTURY.", y=540, at=0.0, size=120)], bg="cand_308"))
at("If it returns dissolved limestone passages", dict(type="geo", variant="slump", beats=dict(deposit=-1, fold=-4, cav=0.2),
    labels=[dict(text="Dissolved limestone passages", x=960, y=120, at=0.2, size=42),
            dict(text="→ the published geology stands", x=960, y=200, at="@the published geology stands", size=42)]))
at("Now, before the payoff", chapter("", "BEFORE THE PAYOFF", "THE COUNTER-ARGUMENT", "cand_267"))
at("because it's not fringe", clip(385, zoom=1.04))
at("Geologist Lorence Collins", collage([
    title_("LORENCE COLLINS", 960, 180, at=0.05, size=120, underline=True),
    strip("Geologist · examined samples under a microscope", 960, 300, at=0.5, size=38),
    pc("cand_182", 700, 660, 560, rot=-3, at="@under a microscope", grade="none"),
    stamp("PUBLISHED", 1320, 760, at="@published his conclusions", rot=-7, color="#1A1A1A")], bg="paper"))
at("the structure is volcanic-origin sediment", dict(type="geo", variant="syncline",
    beats=dict(deposit=0.1, fold="@and folded by tectonic", plan="@a trough-shaped fold", slide="@by a clay-rich landslide"),
    labels=[dict(text="Volcanic-origin sediment · an ancient basin", x=960, y=110, at=0.3, size=40, out="@and folded by tectonic"),
            dict(text="Folded by tectonic forces", x=960, y=110, at="@and folded by tectonic", size=40, out="@a trough-shaped fold"),
            dict(text="A doubly plunging syncline — tilted at both ends", x=960, y=110, at="@a trough-shaped fold", size=40),
            dict(text="…scoured by a clay-rich landslide", x=1320, y=980, at="@by a clay-rich landslide", size=38)]))
at("Wyatt's \"iron fittings,\" Collins found", collage([
    pc("cand_29", 560, 480, 820, rot=-2, at=0.0, grade="doc"),
    strip("“IRON FITTINGS”", 560, 870, at=0.4, size=46),
    dict(k="arrow", **{"from": [1000, 600]}, to=[1230, 600], at="@natural concretions", bend=40),
    strip("LIMONITE + MAGNETITE", 1480, 520, at="@of limonite and magnetite", size=46),
    stamp("NATURAL", 1480, 760, at="@no smelting required", rot=-6, size=130)], bg="paper"))
at("The \"petrified gopher wood\"", collage([
    dict(k="cut", img=cutout("cand_144", red=True, height=700), x=640, y=560, h=420, at=0.0),
    strip("“PETRIFIED GOPHER WOOD”", 640, 230, at=0.2, size=44),
    dict(k="arrow", **{"from": [1000, 560]}, to=[1230, 560], at="@crinkled metamorphosed", bend=40),
    strip("METAMORPHOSED PERIDOTITE", 1480, 480, at="@crinkled metamorphosed peridotite", size=42),
    stamp("ROCK", 1480, 720, at="@common in this volcanic region", rot=-6, size=150)], bg="paper"))
at("The anchor stones were local andesite", depth("cand_310", subject=[0.7, 0.6], hit=0.3,
                                                  lower=("Anchor stones", "local andesite — the same stone as the mountains", 0.8)))
at("And fossil-bearing limestone", clip(459, zoom=1.04, chip="Fossil-bearing limestone", chip_at=0.4))
at("in ways that place its layers far older", clip(329, skip=0.2, zoom=1.1, then=(262,)))
at("A second peer-reviewed study", collage([
    title_("MURAT AVCI · 2007", 960, 190, at=0.05, size=120, underline=True),
    strip("Turkish geologist · peer-reviewed study", 960, 310, at=0.5, size=40),
    pc("cand_267", 760, 690, 700, rot=-3, at=0.6),
    stamp("PEER-REVIEWED", 1350, 760, at=1.4, rot=-7, color="#1A1A1A", size=90)], bg="paper"))
at("concluded the ship shape is a large block", dict(type="geo", variant="slump",
    beats=dict(deposit=0.1, fold="@that slumped downslope", cav="@and dissolution"),
    labels=[dict(text="A block of Miocene limestone", x=620, y=140, at=0.4, size=40),
            dict(text="…slumped downslope on weaker clays", x=1250, y=240, at="@that slumped downslope", size=40),
            dict(text="Earthflow · ice melt · dissolution", x=1250, y=340, at="@refined by earthflow", size=40),
            dict(text="KARST: dissolution hollows the rock", x=960, y=1000, at="@the same dissolution", size=44, bg="#1A1A1A", color="#F3EEE2")]))
at("Under that model, cavities and tunnels", words([
    W_("CAVITIES AREN'T ROOMS.", y=450, at=0.1, size=130),
    W_("THEY'RE EXPECTED.", y=650, at="@They're the expectation", size=140, color="#D9A441")], bg="cand_14"))
at("To be fair", clip(420, zoom=1.04, chip="The team's reply", chip_at=0.8))
at("the formation's symmetry is unusually clean", spot("ind2_01", center=[0.5, 0.5], radius=[0.2, 0.36], label="Unusually symmetrical", hit=0.3, zoom=1.12))
at("the pointed end, they note, faces uphill", collage([
    pc("ind2_01", 960, 540, 1500, rot=0, at=0.0, pad=0, tape=False),
    dict(k="arrow", **{"from": [1320, 900]}, to=[1320, 260], at="@faces uphill", bend=0, color="#D9A441"),
    strip("UPHILL", 1500, 220, at="@faces uphill", size=48),
    strip("“Sits awkwardly with mudflow dynamics” — the team", 900, 980, at="@sits awkwardly", size=36)], bg="dark"))
at("and their drilling, they say", photo("cand_31", move="right", zoom=1.12, chip="“No continuous bedrock inside the outline”", chip_at=0.8))
at("None of those are kill shots", words([W_("NOT KILL SHOTS.", y=540, at=0.0, size=170)], bg="cand_31"))
at("folded strata produce lens shapes", photo("cand_06", move="in", zoom=1.15, chip="Folded strata → lens shapes", chip_at=0.4))
at("and a slumped block riding on clay", clip(385, zoom=1.08, then=(65,)))
at("but they're real questions", clip(283, zoom=1.04))
at("with real cores", photo("cand_32", move="up", fit="contain", zoom=1.08))
at("That's what makes this a live controversy", collage([
    title_("SETTLED HOAX", 960, 360, at=0.0, size=130, color="#8C8C8C"),
    stamp("LIVE CONTROVERSY", 960, 640, at="@a live controversy", rot=-5, size=130)], bg="paper"))

# -------------------------------------------------------------- the answer
at("So.", dict(type="title", img=img("cand_308"), kicker="", title="CONFIRMED?", subtitle="Noah's Ark, after 4,300 years", tagline=""))
at("Here is the most honest answer", clip(76, zoom=1.03))
at("The four thousand three hundred years was never measured", words([
    W_("NEVER MEASURED.", y=430, at=0.05, size=150),
    W_("INHERITED.", y=640, at="@it was inherited", size=170, color="#D9A441")], bg="cand_464", grade="sepia"))
at("calculated by an archbishop from scripture", clip(465, skip=2.0, zoom=1.06))
at("And the confirmation has never happened", checklist("CONFIRMED BY…", [
    dict(text="A laboratory", at="@not by a laboratory", mark="no"),
    dict(text="Independent scientists", at="@not by independent scientists", mark="no"),
    dict(text="Any published paper", at="@not by any published paper", mark="no")], bg="cand_069", size=80, gap=160, y0=300))
at("What has happened is real", clip(504, skip=18.0, zoom=1.03))
at("is, for the first time, being physically sampled", photo("cand_305", move="in", zoom=1.12,
                                                             chip="Official permits · university supervision", chip_at="@under official permits"))
at("Cores from nearly sixty feet down", photo("cand_60", move="in", fit="contain", chip="≈60 ft · in cold storage", chip_at=0.4))
at("Organic layers await radiocarbon dating", clip(400, zoom=1.08))
at("An unidentified hard layer awaits microscopy", photo("cand_189", move="in", zoom=1.15, grade="none"))
at("And a research team that believes", clip(387, skip=0.5, zoom=1.06))
at("has finally handed its own claim over", words([
    W_("THE ONLY REFEREES THAT MATTER:", y=440, at=0.1, size=70, font="BarlowB", color="#E9E2D2"),
    W_("LABORATORIES.", y=600, at="@laboratories", size=190, color="#D9A441")], bg="cand_60"))
at("The ark has not been confirmed", collage([
    pc("cand_089", 960, 500, 1300, rot=-1.5, at=0.0),
    stamp("NOT CONFIRMED", 960, 820, at=0.3, rot=-5, size=140)], bg="dark"))
at("But the question has never been more testable", words([W_("NEVER MORE TESTABLE.", y=540, at=0.1, size=150)], bg="cand_13"))
at("And one final thought", clip(381, skip=0.2, zoom=1.08))
at("For Muslims, Christians, and Jews", photo("cand_500", grade="none", move="in", fit="contain", zoom=1.12))
at("a story of warning", clip(480, grade="none", zoom=1.03))
at("of obedience, of mercy", clip(485, grade="none", zoom=1.04))
at("It never needed a drill bit", quote("It never needed a drill bit to be true to the people who hold it.", bg="cand_381", size=78, rate=3.6))
at("And the mountain deserves", clip(425, zoom=1.06))
at("to be judged by evidence", photo("cand_340", move="in", zoom=1.12))
at("If the laboratories return ancient worked timber", photo("cand_312", move="in", fit="contain", grade="doc", zoom=1.1))
at("If they return Miocene limestone", clip(38, skip=0.0, zoom=1.06))
at("a spectacular shape", clip(504, skip=2.0, zoom=1.03))
at("Four thousand three hundred years is the legend", words([
    W_("4,300 YEARS", y=420, at=0.0, size=170), W_("IS THE LEGEND.", y=600, at="@is the legend", size=110, color="#D9A441")], bg="cand_089"))
at("The cores are the question", words([
    W_("THE CORES", y=420, at=0.0, size=170), W_("ARE THE QUESTION.", y=600, at="@are the question", size=110, color="#D9A441")], bg="cand_60"))
at("And this winter, for the first time", clip(397, zoom=1.05))
at("stops being a matter of who you believe", words([
    W_("WHO YOU BELIEVE", y=420, at=0.0, size=130, strike="@and becomes a matter"),
    W_("WHAT THE LABORATORY SAYS", y=640, at="@what the laboratory says", size=120, color="#D9A441")], bg="cand_189"))
at("When those results land", collage([
    strip("RESULTS: PENDING", 960, 420, at=0.1, size=64),
    strip("we'll go through them here — line by line", 960, 560, at="@we'll go through them", size=44),
    stamp("WINTER 2026–27", 960, 780, at=0.8, rot=-5, size=100, color="#1A1A1A")], bg="paper"))
at("Because the most interesting version", dict(type="headlines", items=[
    dict(text="NOAH'S ARK CONFIRMED?", x=820, y=330, rot=-3, at=0.0, size=96),
    dict(text="...AFTER 4,300 YEARS?", x=1080, y=620, rot=2, at=0.4, size=84, style="red")],
    overlays=[dict(type="fadeout", d=0.5)]))
at("It's the truth", words([W_("IT'S THE TRUTH.", y=500, at=0.1, size=150)], ground="dark",
                          overlays=[dict(type="fadeout", d=1.6)]))



# ------------------------------------------------------------------- music
# One bed per act, crossfaded; `at` is the cue whose scene the new bed starts under.
MUSIC = [
    dict(at=None, track="11_Unanswered_Questions_Mystery.mp3", db=0),
    dict(at="Basket one", track="10_Industrial_Cinematic_Investigation.mp3", db=-1, lead=-1.2),
    dict(at="And we know the story of the man", track="07_Wounded_Dark_Strings.mp3", db=0),
    dict(at="Basket two", track="08_Man_Down_Tension_Strings.mp3", db=-1, lead=-1.2),
    dict(at="Vegetation above the formation", track="Cinematic Tension Build.mp3", db=-2),
    dict(at="Which brings us to basket three", track="09_Thunder_Dreams_Dark_Drone.mp3", db=0, lead=-1.2),
    dict(at="Now, before the payoff", track="Silent Tension Piano.mp3", db=0, lead=-0.8),
    dict(at="So.", track="Slow Dramatic Ascent.mp3", db=0, lead=-0.8),
]


if __name__ == "__main__":
    edl.main(MUSIC)
