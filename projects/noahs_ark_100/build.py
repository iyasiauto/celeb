"""
Noah's Ark "100% Confirmed"? Here's What Researchers Actually Found
Faceless investigative documentary - edit decision list and build.

Look: "forensic" theme - a lab report and case file. Graph paper, stencil stamps,
cyan / amber / green for observed / claimed / confirmed, x-ray treatments of the radar
images, and the recurring confirmation filter that sorts every piece of evidence.
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
    name="Noahs_Ark_100_Percent_Confirmed",
    kit=os.environ.get("NOAH_KIT", f"{SP}/kit"),
    footage=os.environ.get("NOAH_FOOTAGE", f"{SP}/footage"),
    work=os.environ.get("NOAH_WORK", f"{SP}/work2"),
    data=os.path.join(HERE, "data"),
    out=os.environ.get("NOAH_OUT", f"{SP}/out"),
    image_dirs=[f"{SP}/footage/images/approved", f"{SP}/work/ind", f"{SP}/footage/images/candidates"],
    theme="forensic", grade="cool", grain=2.0,
    # the bed sits ~21 dB under the voice in the gaps and ~31 dB under it while he speaks
    music_floor_db=-21.0, music_duck_db=-10.0, sfx_gain=0.55,
)

DURUPINAR = (44.2317, 39.4403)
ARARAT = (44.2983, 39.7019)
DOGUBAYAZIT = (44.083, 39.547)
TENDUREK = (43.87, 39.37)
SIVAS = (37.035, 39.745)
SYDNEY = (151.18, -33.87)
CUDI = (42.45, 37.38)            # Mount Cudi (Judi), one proposed site of Al-Judi

OBS, CLA, CON = 0, 1, 2


def fcard(text, col, at, size=None):
    d = dict(text=text, col=col, at=at)
    if size: d["size"] = size
    return d


def filt(items, zero=None, zero_text=None, **kw):
    s = dict(type="filter", items=items)
    if zero is not None:
        s["zeroAt"] = zero
        if zero_text: s["zeroText"] = zero_text
    s.update(kw)
    return s


def gauge(kicker, to, label="", bg=None, **kw):
    s = dict(type="gauge", kicker=kicker, to=to, label=label)
    if bg: s["img"] = img(bg)
    s.update(kw)
    return s


def xray(name, crop=None):
    return img(name, "xray", crop)


GPR = "cand_252"
GPR_CROP = (0.0, 0.17, 1.0, 1.0)

# =================================================================== intro
at(0.0, gauge("SEPTEMBER 22, 2026", 100, "“one hundred percent” — to a British newspaper", bg="cand_089",
              at=0.15, d=1.1, dim=0.78))
at("standing in front of a boat-shaped", clip(6, zoom=1.03))
at("His team, he said", card("ind2_02", focus=(0.5, 0.2), zoom=1.25, height=1000))
at("that this formation", photo("cand_074", move="in", focus=[0.5, 0.62], zoom=1.16, chip="Durupınar site · near Mount Ararat"))
at("is man-made", words([W_("MAN-MADE.", y=540, at=0.0, size=210, color="#F2B134")], bg="cand_125"))
at("Not probably", words([W_("NOT PROBABLY.", y=330, at=0.0, size=130),
                          W_("NOT LIKELY.", y=520, at="@Not likely", size=130),
                          W_("100%.", y=760, at="@One hundred percent", size=220, color="#F2B134")], bg="cand_13"))
at("Within hours", card("ind1_01", focus=(0.5, 0.86), zoom=1.5, height=980))
at("Headlines appeared asking", dict(type="headlines", items=[
    dict(text="NOAH'S ARK FINALLY CONFIRMED?", x=860, y=300, rot=-3, at=0.1, size=86),
    dict(text="'100%' — RESEARCHERS", x=1100, y=560, rot=2, at=1.0, size=72, style="red"),
    dict(text="SCIENTISTS 'PROVE' THE ARK?", x=800, y=820, rot=-1.5, at="@Videos racked up", size=80, style="tan")]))
at("Videos racked up millions", card("ind1_02", focus=(0.5, 0.82), zoom=1.45, height=980))
at("Comment sections filled", words([W_("CELEBRATION.", y=330, at="@with celebration", size=120),
                                     W_("MOCKERY.", y=510, at="@with mockery", size=120, color="#E5484D"),
                                     W_("ARGUMENTS.", y=690, at="@and with arguments", size=120, color="#F2B134")], bg="cand_381"))
at("about faith and science", clip(472, grade="none", zoom=1.04))
at("But here's the thing about the number", stat("100%", "THE NUMBER", "…and the thing about it", bg="cand_13", count=False,
                                                 align="center", y=330, size=260))
at("Science doesn't actually work in percentages", words([W_("SCIENCE DOESN'T WORK", y=440, at=0.0, size=110),
                                                          W_("IN PERCENTAGES LIKE THAT.", y=600, at=0.6, size=110, color="#3FC7D6")], bg="cand_182", grade="none"))
at("No laboratory certifies", collage([
    pc("cand_182", 540, 520, 620, rot=-3, at=0.0, grade="none"),
    stamp("100% CONFIRMED", 1330, 360, at="@one hundred percent confirmed", rot=-6, size=90),
    strip("— no laboratory issues this", 1330, 520, at="@one hundred percent confirmed", size=38),
    strip("— no journal stamps certainty onto a claim", 1330, 640, at="@No peer-reviewed journal", size=38)]))
at("Real confirmation is a process", checklist("REAL CONFIRMATION IS A PROCESS", [
    dict(text="Evidence", at="@evidence", mark="dot"),
    dict(text="Replication", at="@replication", mark="dot"),
    dict(text="Independent verification", at="@independent verification", mark="dot"),
    dict(text="Years. Sometimes decades.", at="@and it takes years", mark="dot")], bg="cand_267", size=76, gap=150, y0=280))
at("So when a lead researcher declares", dict(type="timeline", img=img("cand_305"),
    events=[dict(year="Sept 22", label="“One hundred percent” certain"), dict(year="Sept 23", label="Drilling program begins")],
    stops=[dict(i=0, at=0.0), dict(i=1, at="@one day before his team's")]))
at("a responsible investigator has to ask", clip(227, zoom=1.04))
at("Not \"is the ark confirmed?\"", words([
    W_("IS THE ARK CONFIRMED?", y=380, at=0.0, size=120, strike="@But this"),
    W_("WHAT HAS BEEN FOUND?", y=600, at="@what has actually been found", size=130, color="#3FC7D6")], bg="cand_089"))
at("What has genuinely been confirmed", words([W_("WHAT IS CONFIRMED?", y=540, at=0.0, size=150, color="#3DBE7A")], bg="cand_089"))
at("And what is still a claim wearing", collage([
    stamp("CLAIM", 700, 480, at=0.1, rot=-6, size=150, color="#F2B134"),
    strip("…wearing the costume of a conclusion", 1180, 700, at="@the costume of a conclusion", size=44)]))
at("That's what this video is going to do", clip(38, zoom=1.03))
at("Not mock the claim", words([W_("NOT MOCK IT.", y=430, at=0.0, size=150),
                                W_("NOT SELL IT.", y=640, at="@Not sell it either", size=150, color="#F2B134")], bg="cand_069"))
at("We're going to walk through every pillar", collage([
    title_("FIVE PILLARS OF EVIDENCE", 960, 150, at=0.1, size=96, underline=True),
    pc("cand_06", 260, 520, 280, rot=-3, at="@the dimensions", caption="Dimensions"),
    pc("cand_45", 610, 560, 300, rot=2, at="@the history", caption="History", crop=(0.0, 0.0, 1.0, 0.86)),
    pc(GPR, 960, 520, 320, rot=-2, at="@the scans", caption="Scans", crop=GPR_CROP),
    pc("cand_142", 1310, 560, 240, rot=3, at="@the soil", caption="Soil"),
    pc("cand_305", 1660, 520, 300, rot=-2, at="@brand-new drilling", caption="Drilling")]))
at("and for each one", filt([], headAt=["@what was observed", "@what was claimed", "@has actually been confirmed"]))
at("If you're the kind of viewer", clip(412, zoom=1.04, then=(323,)))
at("consider subscribing", clip(103, zoom=1.03))
at("Let's start with the word", words([W_("“CONFIRMED”", y=540, at="@confirmed", size=230, color="#3DBE7A")], bg="cand_182", grade="none"))
at("When you hear that something", clip(397, zoom=1.05, then=(398, 250)))
at("Researchers make a claim", checklist("WHAT “CONFIRMED” MEANS", [
    dict(text="Researchers make a claim", at=0.1, mark="dot"),
    dict(text="Outside experts test it", at="@Outside experts", mark="dot"),
    dict(text="Laboratories analyse the physical evidence", at="@Laboratories analyze", mark="dot"),
    dict(text="Published, attacked, defended, replicated", at="@Results get published", mark="dot"),
    dict(text="Independent agreement → confirmed", at="@And only then", mark="yes")], bg="cand_182", size=66, gap=130))
at("None of that has happened", checklist("AT DURUPINAR, AS OF SEPTEMBER 2026", [
    dict(text="Outside experts have tested it", at=0.2, mark="no"),
    dict(text="A laboratory has analysed it", at=0.6, mark="no"),
    dict(text="Results have been published", at=1.0, mark="no"),
    dict(text="Anyone has replicated it", at=1.4, mark="no")], bg="cand_089", size=70, gap=140, y0=290))
at("What has happened is this", clip(534, zoom=1.04))
at("A research organization called Noah's Ark Scans", dict(type="tv", img=img("cand_256", "none", (0.0, 0.0, 1.0, 0.8)), focus=[0.22, 0.5],
    overlays=[dict(type="lower", name="Andrew Jones", role="Noah's Ark Scans", at="@led by an American", x=110, y=860)]))
at("has spent years scanning", clip(294, zoom=1.04, then=(253,), chip="Scanning · sampling · drilling", chip_at="@sampling"))
at("In his own words", card("cand_259", focus=(0.5, 0.4), zoom=1.2, height=720, grade="cool"))
at("I believe this is Noah's Ark", quote("“I believe this is Noah's Ark.”", who="Andrew Jones — project website", bg="cand_122",
                                        highlight=["believe"], size=96, rate=5.0))
at("And this September, the team began", photo("cand_169", move="in", focus=[0.4, 0.55], chip="September 2026 · first deep core drilling"))
at("working with Turkish archaeologists", dict(type="map", stops=[
        dict(at=0, lon=39.8, lat=39.3, scale=4300), dict(at=4, lon=40.4, lat=39.4, scale=4500, d=4)],
    highlight=[dict(id="TUR", at=0.1)],
    routes=[dict(**{"from": list(SIVAS)}, to=list(DURUPINAR), at=1.0, d=1.8, dash=True)],
    pins=[dict(lon=SIVAS[0], lat=SIVAS[1], label="Sivas Cumhuriyet University", sub="led by Prof. Cenker Atila", at=0.2, side="left", size=34, gap=90),
          dict(lon=DURUPINAR[0], lat=DURUPINAR[1], label="Durupınar", at=2.4, side="right", size=40, gap=120)]))
at("under official authorization", collage([
    pc("cand_12", 700, 520, 820, rot=-2, at=0.0),
    stamp("AUTHORIZED", 1380, 470, at=0.4, rot=-7, size=110, color="#3DBE7A"),
    strip("Turkish government agencies", 1380, 640, at=0.7, size=40)]))
at("That expedition is real", filt([
    fcard("The expedition", OBS, 0.1), fcard("The permits", OBS, "@The permits are real"),
    fcard("The university partnership", OBS, "@The university partnership"),
    fcard("Core samples in cold storage", OBS, "@The core samples")]))
at("And every single headline", dict(type="network", center="NOAH'S ARK SCANS", nodes=[
    dict(label="“100%” quote", at="@the one hundred percent quote"), dict(label="The drilling", at="@the drilling"),
    dict(label="The shattered drill bit", at="@the shattered drill bit"),
    dict(label="“Petrified wood”", at="@the whispers of petrified wood"),
    dict(label="Press releases", at="@through its own press releases"), dict(label="Interviews", at="@and interviews")]))
at("There is, at this moment, no second source", words([
    W_("NO SECOND SOURCE.", y=330, at=0.0, size=120), W_("NO INDEPENDENT LAB.", y=520, at="@No independent laboratory", size=120),
    W_("NO OUTSIDE CONFIRMATION.", y=720, at="@No outside confirmation", size=120, color="#E5484D")], bg="cand_12"))
at("Keep that architecture in mind", clip(3, zoom=1.03, then=(110, 122)))
at("And some of it is genuinely intriguing", clip(79, zoom=1.03))

# =================================================================== pillar one
at("Pillar one", chapter("01", "PILLAR ONE", "THE SHAPE AND THE SIZE", "cand_069"))
at("The Durupınar formation is a long", dict(type="map", detail="geo_hi.json", stops=[
        dict(at=0, lon=36, lat=39.2, scale=2900),
        dict(at="@about twenty-nine kilometers", lon=44.05, lat=39.55, scale=36000, d=3.2)],
    highlight=[dict(id="TUR", at=0.3), dict(id="TUR-2307", at=1.2, fill="rgba(242,177,52,.45)")],
    names=[dict(text="Turkey", lon=34.5, lat=39.2, at=0.6, out="@about twenty-nine kilometers"),
           dict(text="Iran", lon=44.62, lat=39.40, at="@near Turkey's border with Iran", size=40),
           dict(text="Armenia", lon=44.55, lat=39.93, at="@Greater Mount Ararat", size=30)],
    dots=[dict(lon=ARARAT[0], lat=ARARAT[1], label="Mount Ararat · 5,137 m", at="@Greater Mount Ararat"),
          ],
    routes=[dict(**{"from": list(DURUPINAR)}, to=list(ARARAT), at="@twenty-nine kilometers", d=1.0, label="29 km", lx=90, ly=10)],
    pins=[dict(lon=DURUPINAR[0], lat=DURUPINAR[1], label="Durupınar", sub="the boat-shaped outline", at="@the slopes of", side="left")]))
at("From the air, it looks astonishingly", collage([
    pc("ind2_01", 960, 540, 1560, rot=0, at=0.0, pad=0, tape=False),
    dict(k="arrow", **{"from": [300, 180]}, to=[800, 250], at="@a pointed end", bend=40),
    strip("POINTED END", 330, 150, at="@a pointed end", rot=-2),
    dict(k="arrow", **{"from": [1620, 900]}, to=[1120, 860], at="@a rounded end", bend=-40),
    strip("ROUNDED END", 1600, 960, at="@a rounded end", rot=2),
    strip("RAISED EDGES", 1300, 160, at="@raised edges", rot=1.5)], bg="cork", z1=1.03))
at("Turkish army cartographer", photo("cand_307", grade="bw", move="in", zoom=1.1))
at("in aerial photographs in 1959", photo("cand_199", move="in", zoom=1.08, chip="1959 · NATO mapping mission", chip_at="@during a NATO"))
at("Its most-cited length", stat("157 m", "MOST-CITED LENGTH", "about 515 feet", bg="cand_06", countFor=1.3))
at("And here is the fact that has powered", clip(17, zoom=1.04))
at("in the Book of Genesis", clip(480, grade="none", zoom=1.03, chip="Genesis 6:15 · 300 cubits", chip_at=0.6))
at("If you convert that using the Egyptian", dict(type="measure", title="300 CUBITS × ROYAL CUBIT", pxPerFt=2.7, bars=[
    dict(label="ROYAL CUBIT (≈20.6 IN)", ft=515, value="≈515 FT", at="@three hundred cubits comes out"),
    dict(label="THE DURUPINAR FORMATION", ft=515, value="≈515 FT", at="@almost exactly 515 feet", color="#E5484D")],
    stamp=dict(text="MATCH", at="@almost exactly 515 feet", x=1300, y=820)))
at("The match is real", filt([fcard("Length ≈ 515 ft — under the royal cubit", OBS, 0.1)]))
at("And supporters of the site treat this", clip(56, zoom=1.04))
at("But let's do what", words([W_("STRESS TEST.", y=540, at="@stress-test it", size=200, color="#F2B134")], bg=GPR, crop=GPR_CROP,
                              overlays=[dict(type="flash", at="@stress-test it")]))
at("First problem", dict(type="measure", title="PROBLEM 1: WHICH CUBIT?", pxPerFt=2.7, bars=[
    dict(label="ROYAL CUBIT (≈20.6 IN)", ft=515, value="≈515 FT", at=0.0, grow=0.01),
    dict(label="COMMON CUBIT (≈18 IN)", ft=450, value="≈450 FT", at="@Use a shorter common cubit", color="#8C8C8C"),
    dict(label="THE DURUPINAR FORMATION", ft=515, value="≈515 FT", at=0.0, grow=0.01, color="#E5484D")],
    stamp=dict(text="A MUCH WORSE MATCH", at="@a much worse match", x=1000, y=870)))
at("So the famous 515-foot correspondence", words([W_("IT DEPENDS", y=440, at=0.1, size=150),
                                                   W_("ON THE RULER.", y=640, at="@which ancient ruler", size=150, color="#F2B134")], bg="cand_06"))
at("Second problem", dict(type="measure", title="PROBLEM 2: WIDTH", pxPerFt=9.0, bars=[
    dict(label="50 ROYAL CUBITS", ft=86, value="≈86 FT", at="@Fifty royal cubits"),
    dict(label="THE FORMATION AT ITS MIDDLE", ft=138, value="≈138 FT", at="@The formation measures", color="#E5484D")],
    stamp=dict(text="OFF BY MORE THAN HALF", at="@off by more than half", x=1100, y=820)))
at("Supporters answer that a wooden hull", clip(597, zoom=1.03, skip=8.0))
at("But notice the logic", collage([
    title_("MATCH", 520, 300, at=0.1, size=110, color="#3DBE7A"),
    strip("= evidence", 520, 430, at="@it's evidence", size=40),
    title_("MISMATCH", 1400, 300, at="@When it doesn't", size=110, color="#E5484D"),
    strip("= explained away", 1400, 430, at="@there's an explanation", size=40),
    stamp("UNTESTABLE", 960, 740, at="@can never actually be tested", rot=-6, size=140),
    strip("…and so it can never be confirmed", 960, 930, at="@can never be confirmed", size=40)]))
at("That's not cynicism", words([W_("NOT CYNICISM —", y=430, at=0.0, size=120),
                                 W_("HOW CONFIRMATION WORKS.", y=620, at="@that's just how", size=120, color="#3DBE7A")], bg="cand_182", grade="none"))
at("There's also the location itself", dict(type="map", detail="geo_hi.json", stops=[
        dict(at=0, lon=43.3, lat=39.3, scale=9000), dict(at=6, lon=43.8, lat=39.4, scale=12000, d=6)],
    highlight=[dict(id="TUR", at=0.2), dict(id="ARM", at="@a region, not a single peak", fill="rgba(242,177,52,.35)"),
               dict(id="IRN", at="@a region, not a single peak", fill="rgba(242,177,52,.25)")],
    names=[dict(text="“Mountains of Ararat” · a region", lon=43.6, lat=40.35, at="@on the mountains of Ararat", size=34, color="#F2B134")],
    dots=[dict(lon=ARARAT[0], lat=ARARAT[1], label="Mount Ararat", at=0.4)],
    routes=[dict(**{"from": list(DURUPINAR)}, to=list(ARARAT), at="@twenty-nine kilometers", d=0.8, label="29 km", lx=70, ly=10)],
    pins=[dict(lon=DURUPINAR[0], lat=DURUPINAR[1], label="Durupınar", at=0.8, side="left", size=40)]))
at("But critics raise a specific difficulty", dict(type="valley",
    beats=dict(draw=0.1, boat="@the formation lies low", measure="@a valley roughly a thousand", water="@the surrounding mountaintops"),
    labels=[dict(text="≈1,000 m deep valley", x=1480, y=700, at="@a thousand meters", size=38),
            dict(text="Genesis: the peaks stay under water for months", x=960, y=90, at="@remain submerged", size=38),
            dict(text="A vessel at the bottom of a deep valley?", x=960, y=980, at="@A vessel settling", size=38)]))
at("So pillar one gives us this verdict", filt([
    fcard("A striking shape", OBS, "@a genuinely striking shape"),
    fcard("Length matches — under one cubit standard", OBS, "@a length that matches"),
    fcard("Width: explained by a collapsed hull", CLA, "@a width that doesn't"),
    fcard("Location fits “mountains of Ararat”", CLA, "@and a location both sides")],
    zero="@Confirmed as a ship", zero_text="confirmed as a ship: no"))
at("And before we go further", clip(104, zoom=1.04))
at("In the Islamic tradition", clip(446, grade="none", zoom=1.03))
at("The Qur'an describes him building", dict(type="map", stops=[
        dict(at=0, lon=43.2, lat=38.6, scale=5200), dict(at=7, lon=43.3, lat=38.5, scale=5600, d=7)],
    highlight=[dict(id="TUR", at=0.2)],
    names=[dict(text="Iraq", lon=43.0, lat=36.4, at=0.6, size=30), dict(text="Iran", lon=45.6, lat=38.2, at=0.6, size=30),
           dict(text="Syria", lon=40.5, lat=36.3, at=0.6, size=30)],
    pins=[dict(lon=CUDI[0], lat=CUDI[1], label="Mount Cudi", sub="one proposed site of Al-Judi", at="@Al-Judi", side="left", size=40, gap=130),
          dict(lon=ARARAT[0], lat=ARARAT[1], label="Mount Ararat", sub="the “mountains of Ararat” region", at="@with various mountains", side="right", size=40, gap=130)]))
at("In the Biblical tradition", clip(486, grade="none", zoom=1.04, skip=1.5))
at("These are two great textual traditions", words([W_("TWO GREAT TRADITIONS.", y=500, at=0.1, size=140),
                                                   W_("their own details, vocabularies and scholarship", y=680, at="@their own vocabularies", size=56, font="GaramondI")], bg="cand_381"))
at("And here is what neither of them contains", collage([
    strip("QUR'AN — Al-Judi", 560, 330, at=0.1, size=48),
    strip("GENESIS — the mountains of Ararat", 1320, 330, at=0.4, size=48),
    stamp("NO MENTION OF DURUPINAR", 960, 650, at="@any mention of the", rot=-5, size=100)]))
at("The connection between this specific hillside", clip(112, zoom=1.03, chip="A modern connection", chip_at=1.0))
at("It was made by modern researchers", clip(295, zoom=1.04))
at("That's not an insult to the connection", clip(425, zoom=1.04, then=(557, 11)))

# =================================================================== history
at("Which brings us to the history", dict(type="timeline", img=img("cand_46", "cool", (0.12, 0.0, 0.86, 1.0)),
    events=[dict(year="1959", label="The aerial photo"), dict(year="1960", label="First expedition"),
            dict(year="1977", label="Ron Wyatt"), dict(year="1996", label="Fasold's geology paper"),
            dict(year="1997", label="Testimony under oath"), dict(year="2026", label="Deep core drilling")],
    stops=[dict(i=0, at=0.0), dict(i=5, at=3.6)], gap=460))
at("The first serious expedition came in 1960", photo("cand_45", crop=(0.0, 0.0, 1.0, 0.86), move="in", zoom=1.12, chip="1960 · first expedition"))
at("An American-led team", collage([
    title_("ARTHUR BRANDENBERGER", 960, 200, at=0.1, size=110, underline=True),
    strip("Surveyor · 1960 expedition", 960, 320, at="@included surveyor", size=40),
    dict(k="note", text="personally believed the ark could be found", x=700, y=640, w=460, rot=-4, at="@personally believed")]))
at("traveled to the site, dug into it", clip(277, zoom=1.04))
at("and even used dynamite", words([W_("DYNAMITE.", y=540, at=0.05, size=230, color="#E5484D")], bg="cand_46", crop=(0.12, 0.0, 0.86, 1.0),
                                   overlays=[dict(type="flash", at=0.05)]))
at("Their official conclusion", collage([
    stamp("NO VISIBLE REMAINS", 700, 380, at="@no visible archaeological remains", rot=-5, size=100),
    strip("“A freak of nature.”", 1300, 620, at="@A freak of nature", size=48),
    stamp("CASE CLOSED", 960, 830, at="@Case closed", rot=4, size=120, color="#15191C")]))
at("For a while, it was", photo("cand_46", grade="bw", crop=(0.12, 0.0, 0.86, 1.0), move="in", zoom=1.08))
at("Then, in 1977, the site was rediscovered", depth("cand_299", subject=[0.5, 0.45], crop=(0.0, 0.0, 0.5, 0.78), grade="bw",
                                                     hit=0.8, keys=[[0.5, 0.3, 1.0], [0.5, 0.34, 1.06]],
                                                     lower=("Ron Wyatt", "From 1977", "@a man named Ron Wyatt")))
at("Wyatt was not an archaeologist", words([
    W_("NOT AN ARCHAEOLOGIST.", y=330, at=0.0, size=110), W_("NOT A GEOLOGIST.", y=500, at="@or a geologist", size=110),
    W_("NURSE ANESTHETIST · TENNESSEE", y=720, at="@he was a nurse anesthetist", size=90, color="#F2B134")],
    bg="cand_299", grade="bw", crop=(0.0, 0.0, 1.0, 0.78)))
at("Over the years he claimed to have found", collage([
    pc("cand_299", 420, 520, 520, rot=-3, at=0.0, grade="bw", crop=(0.0, 0.0, 0.5, 0.78)),
    dict(k="pin", x=420, y=250, at=0.3),
    strip("NOAH'S ARK", 1300, 200, at="@not only Noah's Ark", rot=-2, size=42),
    dict(k="pin", x=1300, y=165, at="@not only Noah's Ark"),
    strip("THE ARK OF THE COVENANT", 1380, 420, at="@the Ark of the Covenant", rot=1.5, size=42),
    dict(k="pin", x=1380, y=385, at="@the Ark of the Covenant"),
    strip("THE “TRUE” MOUNT SINAI", 1300, 640, at="@the true site of Mount Sinai", rot=-1, size=42),
    dict(k="pin", x=1300, y=605, at="@the true site of Mount Sinai"),
    strip("CHARIOT WHEELS, RED SEA", 1380, 860, at="@chariot wheels", rot=2, size=42),
    dict(k="pin", x=1380, y=825, at="@chariot wheels"),
    dict(k="string", pts=[[420, 250], [1300, 165]], at="@not only Noah's Ark", d=0.5),
    dict(k="string", pts=[[420, 250], [1380, 385]], at="@the Ark of the Covenant", d=0.5),
    dict(k="string", pts=[[420, 250], [1300, 605]], at="@the true site of Mount Sinai", d=0.5),
    dict(k="string", pts=[[420, 250], [1380, 825]], at="@chariot wheels", d=0.5)], bg="cork"))
at("At Durupınar, he claimed the raised edges", photo("cand_300", crop=(0.44, 0.0, 1.0, 1.0), move="in",
                                                        chip="“Petrified hull timbers”", chip_at="@petrified hull timbers"))
at("that his metal detectors", photo("cand_29", move="in", focus=[0.5, 0.42], zoom=1.2, chip="“Iron fittings”", chip_at=0.4))
at("and that massive carved stones", depth("cand_310", subject=[0.7, 0.6], hit=0.5, chip="“Anchor stones”"))
at("To his supporters", dict(type="split", left=img("cand_299", "bw", (0.0, 0.0, 0.5, 0.78)), right=img("cand_29"),
                             leftLabel="To supporters: a pioneer", rightLabel="To science: a sincere amateur", leftFocus=[0.5, 0.35]))
at("And here's the detail most retellings", photo("cand_299", grade="bw", crop=(0.0, 0.0, 1.0, 0.78), move="in", zoom=1.08))
at("Wyatt's own expedition partner", depth("cand_298", subject=[0.62, 0.45], hit=0.6, keys=[[0.55, 0.28, 1.0], [0.58, 0.31, 1.06]],
                                           lower=("David Fasold", "Marine salvage expert · Wyatt's partner in the 1980s", "@David Fasold")))
at("concluded the site was a natural formation", collage([
    pc("cand_298", 600, 540, 560, rot=-3, at=0.0),
    stamp("NATURAL FORMATION", 1300, 520, at=0.4, rot=-8, size=100)]))
at("In 1996, he co-authored", collage([
    title_("1996", 700, 300, at=0.05, size=220),
    strip("A co-authored geology paper", 1250, 520, at=0.4, size=42),
    dict(k="cut", img=cutout("vintage_stack_of_books.png", red=False), x=560, y=780, h=380, at=0.3),
    stamp("PUBLISHED", 1300, 760, at="@arguing exactly that", rot=-6, color="#15191C")]))
at("And in 1997, under oath", dict(type="map", stops=[
        dict(at=0, lon=60, lat=15, scale=520), dict(at=3.5, lon=110, lat=-10, scale=560, d=3.5)],
    routes=[dict(**{"from": list(DURUPINAR)}, to=list(SYDNEY), at=0.6, d=2.2, dash=True)],
    pins=[dict(lon=SYDNEY[0], lat=SYDNEY[1], label="Australia, 1997", sub="Fasold testifies under oath", at=2.4, side="left", size=46)]))
at("had been found as", quote("“Absolute BS.”", who="David Fasold, under oath, 1997", bg="cand_298", size=150, highlight=["absolute"], rate=2.2))
at("The man who helped launch", photo("cand_298", move="in", focus=[0.6, 0.35], zoom=1.1, chip="He testified against it", chip_at=1.2))
at("That's the ground the 2026 expedition", photo("cand_31", move="right", zoom=1.12))
at("A site with sixty-six years", dict(type="network", center="SINCE 1959", rot=0.5, nodes=[
    dict(label="An anomaly", at="@an anomaly", r=520), dict(label="A headline", at="@a headline", r=520),
    dict(label="A geological explanation", at="@and a geological explanation", r=520)],
    stamp=dict(text="THE SAME CYCLE", at="@and a geological explanation")))
at("The current team knows this history", clip(534, skip=1.2, zoom=1.08))
at("Their entire strategy", checklist("THE 2026 STRATEGY", [
    dict(text="Better technology", at="@better technology"), dict(text="Official permits", at="@official permits"),
    dict(text="Actual cores", at="@actual cores")], bg="cand_169", size=80, gap=160, y0=320))
at("So let's look at what that technology found", clip(375, zoom=1.04))

# =================================================================== pillar two
at("Pillar two", chapter("02", "PILLAR TWO", "THE SCANS", "cand_241"))
at("Over recent years", clip(295, skip=0.6, zoom=1.06))
at("Ground-penetrating radar, which sends", clip(388, zoom=1.04, chip="Ground-penetrating radar", chip_at=0.4))
at("Electrical resistivity tomography", clip(414, zoom=1.04, chip="Electrical resistivity tomography", chip_at=0.3))
at("LiDAR surface mapping", photo("cand_63", move="in", zoom=1.12, chip="LiDAR · thermal imaging", chip_at=0.2))
at("Audio-magnetotelluric surveys", stat("300 m", "CLAIMED SURVEY DEPTH", "audio-magnetotelluric surveys", bg="cand_241", countFor=1.2))
at("And the team reports remarkable results", photo("ind2_04", move="in", fit="contain", grade="none", zoom=1.1))
at("right-angle intersections", clip(571, zoom=1.04))
at("features they interpret as decks", collage([
    pc("cand_208", 760, 500, 1100, rot=-2, at=0.0, grade="xray"),
    dict(k="scan", x=210, y=190, w=1100, h=620, at=0.2),
    strip("“DECKS”", 1520, 300, at="@as decks", rot=-3, size=48),
    strip("“CORRIDORS”", 1560, 520, at="@corridors", rot=2, size=48),
    strip("“CHAMBERS”", 1500, 740, at="@and chambers", rot=-1.5, size=48)], bg="cork"))
at("In interviews, team members", quote("“Like a structure, not like rock.”", who="Noah's Ark Scans team, in interviews",
                                        bg=GPR, crop=GPR_CROP, size=96, rate=3.6, highlight=["structure"]))
at("This is the pillar that produces the viral", card("ind1_03", focus=(0.5, 0.82), zoom=1.45, height=980))
at("Now here's what ground-penetrating radar actually does", clip(243, zoom=1.05, then=(14,)))
at("It detects boundaries", collage([
    title_("WHAT RADAR SEES: BOUNDARIES", 960, 150, at=0.0, size=90, underline=True),
    pc("cand_62", 500, 580, 380, rot=-2, at=0.2, grade="none"),
    strip("soil → stone", 1250, 420, at="@soil to stone", size=48),
    strip("solid → void", 1250, 580, at="@solid to void", size=48),
    strip("dry → wet", 1250, 740, at="@dry to wet", size=48)]))
at("It can absolutely reveal straight lines", spot(GPR, center=[0.52, 0.52], radius=[0.12, 0.12], label="Straight lines", hit=0.3,
                                                     zoom=1.2, crop=None))
at("But here's the part that never makes", words([
    W_("STRAIGHT LINES + RIGHT ANGLES", y=420, at=0.1, size=100),
    W_("ARE NOT A HUMAN SIGNATURE.", y=620, at="@are not a human signature", size=110, color="#F2B134")], bg=GPR, crop=GPR_CROP))
at("Limestone fractures along planar joints", clip(329, zoom=1.06, then=(454,), chip="Limestone joints", chip_at=0.5))
at("Geologists encounter right angles", photo("cand_076", move="in", zoom=1.15, chip="Natural right angles", chip_at=0.6))
at("A radar return can tell you", filt([fcard("A boundary exists", OBS, 0.2),
                                       fcard("Someone built it", CLA, "@who built the boundary")]))
at("Think of it like an X-ray", collage([
    pc(GPR, 760, 520, 1180, rot=0, at=0.0, pad=0, tape=False, grade="xray"),
    dict(k="scan", x=170, y=190, w=1180, h=660, at=0.3),
    strip("THE X-RAY: A SHAPE INSIDE", 1500, 900, at="@can show you a shape", size=44)], bg="cork"))
at("It takes a trained radiologist", collage([
    pc("cand_60", 760, 520, 900, rot=-2, at=0.0),
    strip("THE BIOPSY: WHAT IT ACTUALLY IS", 1420, 900, at="@and often a biopsy", size=44)], bg="cork"))
at("The scans at Durupınar are the X-ray", dict(type="split", left=xray(GPR, GPR_CROP), right=img("cand_60"),
                                                leftLabel="The X-ray = the scans", rightLabel="The biopsy = the cores",
                                                leftFocus=[0.5, 0.5], rightFocus=[0.7, 0.5]))
at("And the biopsy results aren't back yet", collage([
    pc("cand_60", 820, 520, 900, rot=-2, at=0.0),
    stamp("RESULTS PENDING", 1250, 800, at=0.3, rot=-7, size=110, color="#F2B134")], bg="cork"))
at("There's also a second limitation", words([W_("THE MOST IMPORTANT", y=440, at=0.1, size=120),
                                              W_("LIMITATION.", y=620, at=0.6, size=160, color="#E5484D")], bg=GPR, crop=GPR_CROP))
at("Those radar images you see online", collage([
    pc("ind2_05", 760, 520, 1100, rot=-2, at=0.0, grade="none"),
    strip("An interpretation — not the raw data", 1250, 920, at="@interpretations of raw data", size=42)], bg="cork"))
at("The raw data has never been released", collage([
    dict(k="note", text="RAW SCAN DATA", x=720, y=500, w=600, rot=-3, at=0.0, bg="#D8BC80", size=80),
    stamp("NOT RELEASED", 1150, 700, at="@never been released", rot=-8, size=120)]))
at("Every rendered image", collage([
    pc("cand_208", 520, 420, 640, rot=-5, at=0.0, grade="none"),
    pc("ind2_05", 1380, 380, 700, rot=4, at=0.3, grade="none"),
    pc("cand_170", 980, 700, 420, rot=-1, at=0.6, grade="none"),
    strip("Rendered by: the same team that believes", 960, 960, at="@produced by the same team", size=42)], bg="cork"))
at("That doesn't make the scans fake", filt([fcard("Scans: decks, corridors, chambers", CLA, 0.1),
                                             fcard("Not fake — unverified", CLA, "@It makes them unverified")],
                                            zero="@the opposite of confirmed", zero_text="unverified ≠ confirmed"))

# =================================================================== pillar three
at("Pillar three", chapter("03", "PILLAR THREE", "THE SOIL", "cand_142"))
at("In 2024, the project collected", clip(530, zoom=1.04, chip="2024 · soil sampling", chip_at=0.4))
at("some from inside the boat-shaped", stat("88", "SOIL SAMPLES, 2024", "inside vs. outside the outline", bg="cand_157", countFor=1.0))
at("According to the team, the interior soil", collage([
    pc("cand_142", 480, 540, 560, rot=-3, at=0.0),
    dict(k="stat", value="3×", label="organic matter", x=1150, y=380, at="@three times more organic", rot=-3),
    dict(k="stat", value="+38%", label="potassium", x=1500, y=720, at="@38 percent more potassium", rot=3, bg="#F2B134"),
    strip("Interior vs. exterior — as reported by the team", 1300, 970, at=0.6, size=34)]))
at("Their interpretation", photo("cand_17", move="in", zoom=1.1, chip="“The chemical ghost of a wooden ship”?", chip_at=1.0))
at("They also point out that grass", clip(40, zoom=1.03, then=(58,)))
at("visible from the air", spot("cand_074", center=[0.5, 0.62], radius=[0.12, 0.2], label="Greener growth", hit=0.2, zoom=1.15))
at("Of all the project's claims", checklist("THE SHAPE OF TESTABLE SCIENCE", [
    dict(text="Samples", at="@samples"), dict(text="Numbers", at="@numbers"),
    dict(text="A comparison group", at="@a comparison group")], bg="cand_142", size=80, gap=160, y0=320))
at("But then you have to ask", checklist("THE CONFIRMATION QUESTION", [
    dict(text="Examined outside the project?", at="@has anyone outside", mark="no"),
    dict(text="Published with methods and raw data?", at="@Has the lab work been published", mark="no"),
    dict(text="As of today: no", at="@As of today", mark="no")], bg="cand_142", size=70, gap=150, y0=320))
at("The figures come from the team's own", dict(type="network", center="TEAM ANNOUNCEMENTS", nodes=[
    dict(label="Tabloid interviews", at="@repeated by friendly media"), dict(label="Faith news sites", at=1.2),
    dict(label="Viral videos", at=1.6), dict(label="Social posts", at=2.0), dict(label="Headlines", at=2.4),
    dict(label="Independent lab?", at=2.8, dashed=True)],
    stamp=dict(text="ONE SOURCE, MANY ECHOES", at="@One source, many echoes")))
at("And there's a competing explanation", clip(39, zoom=1.03))
at("Look at the shape again", collage([
    pc("cand_089", 960, 520, 1500, rot=0, at=0.0, pad=0, tape=False),
    dict(k="arrow", **{"from": [760, 110]}, to=[900, 420], at="@Bowls collect rainwater", bend=30, color="#3FC7D6"),
    dict(k="arrow", **{"from": [1180, 110]}, to=[1060, 420], at="@Bowls collect rainwater", bend=-30, color="#3FC7D6"),
    strip("A BOWL", 960, 900, at="@That's a bowl", size=56, rot=-2)], bg="cork"))
at("And here's the geological detail", clip(262, zoom=1.04, chip="Different rock → different soil", chip_at="@different rock weathers"))
at("Geologist Andrew Snelling", collage([
    title_("ANDREW SNELLING", 960, 190, at=0.05, size=120, underline=True),
    strip("Geologist — examined this exact claim", 960, 310, at="@who examined this exact claim", size=40)]))
at("points out that a depression", clip(177, zoom=1.04, then=(70, 106)))
at("In other words: greener grass", filt([fcard("Greener grass, organic-rich soil", OBS, "@greener grass"),
                                         fcard("A rotted ship underneath", CLA, "@whether there's a ship")]))
at("Now — here's a detail about Snelling", words([W_("ABOUT ANDREW SNELLING…", y=540, at=0.1, size=130)], bg="cand_267"))
at("Andrew Snelling is not a secular debunker", words([W_("NOT A SECULAR DEBUNKER.", y=540, at=0.0, size=130, color="#F2B134")], bg="cand_267"))
at("He is a young-earth creationist geologist", collage([
    dict(k="note", text="young-earth creationist geologist", x=1250, y=520, w=520, rot=3, at=0.0, size=48),
    dict(k="cut", img=cutout("vintage_holy_bible.png", red=False), x=620, y=560, h=560, at=0.1)]))
at("He works for Answers in Genesis", clip(520, zoom=1.03, then=(519,), chip="Answers in Genesis · Ark Encounter, Kentucky", chip_at=0.4))
at("This is a man whose worldview", photo("cand_500", grade="none", move="in", fit="contain", zoom=1.12))
at("And he rejects the Durupınar site", collage([
    pc("cand_069", 820, 520, 1000, rot=-2, at=0.0),
    stamp("REJECTED", 1250, 820, at=0.3, rot=-7, size=140)], bg="cork"))
at("His organization has publicly concluded", words([
    W_("NOTHING NEW.", y=430, at=0.1, size=150),
    W_("CLAIMS MADE — AND REFUTED — DECADES AGO", y=630, at="@and refuted", size=70, color="#F2B134")], bg="cand_069"))
at("When the people most motivated", filt([fcard("The evidence, examined by believers", OBS, 0.2),
                                          fcard("They walk away", OBS, "@walk away")],
                                         zero="@is not the word", zero_text="“confirmed” is not the word"))

# =================================================================== pillar four
at("Pillar four", chapter("04", "PILLAR FOUR", "THE DRILLING", "cand_305"))
at("This is the newest evidence", dict(type="headlines", items=[
    dict(text="DRILLING BEGINS AT 'NOAH'S ARK' SITE", x=900, y=330, rot=-2, at=0.1, size=80),
    dict(text="SEPTEMBER 2026", x=1180, y=620, rot=2, at="@exploded in September 2026", size=90, style="red")]))
at("For sixty years, nobody had properly drilled", clip(105, zoom=1.04))
at("A 1988 attempt produced cores", collage([
    title_("1988", 560, 330, at=0.05, size=220),
    strip("cores cooled with drilling water", 1250, 460, at="@by the water used to cool", size=42),
    stamp("CONTAMINATED", 1250, 680, at="@were contaminated", rot=-6, size=110)]))
at("Surface observation and scanning", clip(220, zoom=1.04))
at("Then, on September 23rd, 2026", dict(type="timeline", img=img("cand_305"),
    events=[dict(year="Sept 22", label="“One hundred percent”"), dict(year="Sept 23", label="Deep coring begins")],
    stops=[dict(i=0, at=0.0), dict(i=1, at="@the team announced that deep coring")]))
at("a dry percussion system", photo("cand_10", move="up", fit="contain", zoom=1.08, chip="Dry percussion · no drilling fluids", chip_at=0.3))
at("pulling intact cores from as deep as", stat("18 m", "DEEPEST CORE", "nearly sixty feet down", bg="cand_14", countFor=1.0))
at("And according to the project's own press release", card("ind1_04", focus=(0.5, 0.82), zoom=1.45, height=980))
at("layered sediments, organic-rich", photo("cand_60", move="in", focus=[0.7, 0.5], fit="contain",
                                          chip="Layered sediments · organic-rich intervals", chip_at=0.3))
at("multiple underground cavities", clip(49, zoom=1.04, chip="Cavities", chip_at=0.4))
at("one of which kept filling with water", clip(50, zoom=1.06, then=(114, 74), chip="The “room”", chip_at="@a room"))
at("And in one borehole", photo("cand_161", move="up", fit="contain", zoom=1.1, chip="4–5 m down: a layer too hard to drill",
                                 chip_at="@four to five meters"))
at("the drill hit a layer so hard", words([W_("THE BIT SHATTERED.", y=540, at="@it shattered the bit", size=150, color="#E5484D")],
                                          bg="cand_60", overlays=[dict(type="flash", at="@it shattered the bit")]))
at("Jones's quote", quote("“Harder than limestone.”", who="Andrew Jones", bg="cand_14", size=110, highlight=["harder"], rate=3.0))
at("His suggested possibilities", collage([
    dict(k="cut", img=cutout("cand_312", red=True, height=700), x=720, y=560, h=380, at=0.0),
    strip("“petrified or highly mineralized wood”", 1150, 250, at="@petrified or highly", size=44),
    stamp("THIRD-PARTY TESTING", 1300, 840, at="@third-party laboratory testing", rot=-6, size=90)]))
at("If you watched this story on social media", dict(type="headlines", items=[
    dict(text="DRILL BREAKS ON PETRIFIED WOOD INSIDE NOAH'S ARK", x=960, y=480, rot=-2, at="@Drill breaks on petrified", size=74)]))
at("But walk it back through the confirmation filter", filt([
    fcard("A hard layer at 4–5 m — reported by the project", OBS, "@A hard layer at four"),
    fcard("Possibly petrified wood — a hope, not a result", CLA, "@Possibly petrified wood")],
    zero="@Nothing", zero_text="no laboratory has touched it"))
at("And this is volcanic terrain", clip(418, zoom=1.04, chip="Volcanic terrain · basalt · andesite", chip_at=0.6))
at("Drill bits break on natural volcanic rock", photo("cand_11", move="in", focus=[0.7, 0.5], fit="contain"))
at("A shattered bit is a genuine event", words([W_("A GENUINE EVENT.", y=430, at=0.0, size=140),
                                                W_("NOT A SPECIES ID.", y=630, at="@It is not a species", size=140, color="#F2B134")], bg="cand_11"))
at("Same discipline for the", clip(224, zoom=1.05, then=(127,), chip="Observed: a water-filled cavity", chip_at="@A water-filled cavity"))
at("But limestone dissolves in groundwater", dict(type="geo", variant="slump", beats=dict(deposit=-1, fold=-4, cav=0.3),
    labels=[dict(text="Limestone dissolves in groundwater", x=960, y=120, at=0.2, size=42),
            dict(text="→ caves, all over the world", x=960, y=200, at="@it's how caves form", size=42)]))
at("And geologist Murat Avci's", collage([
    title_("MURAT AVCI · 2007", 960, 190, at=0.05, size=120, underline=True),
    strip("Peer-reviewed study of this very site", 960, 310, at="@peer-reviewed 2007 study", size=40),
    pc("cand_267", 760, 690, 700, rot=-3, at=0.6),
    stamp("PEER-REVIEWED", 1350, 760, at=1.4, rot=-7, color="#15191C", size=90)]))
at("describes the formation as a slumped block", dict(type="geo", variant="slump",
    beats=dict(deposit=0.1, fold="@as a slumped block", cav="@through exactly that dissolution"),
    labels=[dict(text="A slumped block of Miocene limestone", x=660, y=140, at=0.3, size=40),
            dict(text="KARST: voids and tunnels by dissolution", x=960, y=1000, at="@what geologists call karst", size=44, bg="#15191C", color="#EEF1F0")]))
at("Cavities in limestone are the expectation", words([W_("CAVITIES ARE EXPECTED.", y=440, at=0.0, size=130),
                                                       W_("NOT AN ANOMALY.", y=630, at="@not the anomaly", size=130, color="#F2B134")], bg="cand_14"))
at("Calling one a", filt([fcard("A water-filled cavity", OBS, 0.1),
                          fcard("A “room”", CLA, "@is an interpretation layered")]))

# =================================================================== the tally
at("So run the tally", filt([
    fcard("Shape & length", OBS, "@Observations", size=28), fcard("Scan boundaries", OBS, "@genuinely intriguing", size=28),
    fcard("Elevated organics", OBS, "@genuinely intriguing", size=28), fcard("Cores, cavities, a hard layer", OBS, "@Claims", size=28),
    fcard("A ship", CLA, "@Claims", size=28), fcard("Decks and chambers", CLA, "@sometimes extraordinary", size=28),
    fcard("A rotted wooden hull", CLA, "@sometimes extraordinary", size=28), fcard("Petrified wood, a “room”", CLA, "@Confirmations", size=28)],
    zero="@Confirmations: zero", zero_text="the process hasn't happened yet"))
at("Which raises an uncomfortable question", gauge("IF NOTHING IS CONFIRMED…", 100, "where did “one hundred percent” come from?",
                                                   bg="cand_089", from_=100, at=0.1, d=0.1))
at("It came from conviction", words([W_("CONVICTION.", y=540, at=0.0, size=220, color="#F2B134")], bg="cand_122"))
at("Jones has been visiting", checklist("ANDREW JONES", [
    dict(text="Visiting the site since 1997", at=0.2, mark="dot"),
    dict(text="Moved to Turkey to be near it", at="@He moved to Turkey", mark="dot"),
    dict(text="His organization fundraises around it", at="@His organization fundraises", mark="dot"),
    dict(text="Sincere — by every account", at="@by every account", mark="yes")], bg="cand_122", size=66, gap=140, y0=300))
at("But sincerity and certainty", words([W_("SINCERITY", y=430, at=0.0, size=160),
                                         W_("IS NOT CERTAINTY.", y=630, at="@are not the same thing", size=140, color="#E5484D")], bg="cand_122"))
at("And here's the asymmetry", dict(type="timeline", img=img("cand_305"),
    events=[dict(year="Sept 22", label="“One hundred percent” declared"), dict(year="Sept 23", label="The first physical test begins")],
    stops=[dict(i=0, at=0.0), dict(i=1, at="@The drilling — the first physical")]))
at("Certainty arrived one day before", words([W_("CERTAINTY ARRIVED", y=430, at=0.0, size=130),
                                              W_("ONE DAY BEFORE THE EVIDENCE.", y=620, at="@one day before", size=110, color="#F2B134")], bg="cand_305"))
at("That's not how confirmation works", words([W_("NOT HOW CONFIRMATION WORKS.", y=430, at=0.0, size=110),
                                               W_("HOW BELIEF WORKS.", y=620, at="@That's how belief works", size=140, color="#F2B134")], bg="cand_381"))
at("And belief, it's worth saying clearly", quote("Belief doesn't need a rock formation to be valid. A rock formation needs more than belief to be confirmed.",
                                                  bg="cand_381", size=70, rate=3.4, highlight=["confirmed"]))

# =================================================================== the other side
at("Now, in the spirit of honesty", chapter("", "IN FAIRNESS", "THE OTHER SIDE", "cand_267"))
at("because the skeptical case is not invincible", clip(385, zoom=1.04, then=(65,)))
at("The mainstream geological explanation", collage([
    title_("TWO PUBLISHED EXPLANATIONS", 960, 200, at=0.05, size=96, underline=True),
    strip("1 · LORENCE COLLINS — petrology", 960, 460, at=0.5, size=48),
    strip("2 · MURAT AVCI, 2007 — slumped limestone", 960, 620, at=1.0, size=48)]))
at("Geologist Lorence Collins", collage([
    title_("LORENCE COLLINS", 960, 180, at=0.05, size=120, underline=True),
    strip("Examined rock samples under a microscope", 960, 300, at="@under a microscope", size=38),
    pc("cand_182", 960, 660, 620, rot=-3, at="@under a microscope", grade="none")]))
at("describes folded, volcanic-origin sediments", dict(type="geo", variant="syncline",
    beats=dict(deposit=0.1, fold="@a structure called a doubly", plan="@essentially a trough-shaped", slide="@later scoured"),
    labels=[dict(text="Folded, volcanic-origin sediments", x=960, y=110, at=0.3, size=40, out="@a structure called a doubly"),
            dict(text="A doubly plunging syncline — tilted at both ends", x=960, y=110, at="@a structure called a doubly", size=40),
            dict(text="…scoured by a clay-rich landslide", x=1320, y=980, at="@later scoured", size=38)]))
at("He identified Wyatt's famous", collage([
    pc("cand_29", 560, 480, 820, rot=-2, at=0.0),
    strip("“IRON FITTINGS”", 560, 870, at=0.4, size=46),
    dict(k="arrow", **{"from": [1000, 600]}, to=[1230, 600], at="@natural concretions", bend=40),
    strip("LIMONITE + MAGNETITE", 1480, 520, at="@of limonite and magnetite", size=46),
    stamp("NATURAL", 1480, 760, at="@with no human involvement", rot=-6, size=130)]))
at("The supposed petrified wood", collage([
    dict(k="cut", img=cutout("cand_144", red=True, height=700), x=640, y=560, h=420, at=0.0),
    strip("“PETRIFIED WOOD”", 640, 230, at=0.2, size=44),
    dict(k="arrow", **{"from": [1000, 560]}, to=[1230, 560], at="@was crinkled metamorphosed", bend=40),
    strip("METAMORPHOSED PERIDOTITE", 1480, 480, at="@crinkled metamorphosed peridotite", size=42),
    stamp("ROCK", 1480, 720, at="@a common rock", rot=-6, size=150)]))
at("And the anchor stones were carved", clip(608, skip=1.5, zoom=1.03, chip="Anchor stones: local andesite", chip_at="@from local andesite"))
at("Avci's 2007 study, as we heard", dict(type="geo", variant="slump", beats=dict(deposit=0.1, fold=0.6, cav="@and dissolution"),
    labels=[dict(text="Slumped limestone block · earthflow · ice melt · dissolution", x=960, y=120, at=0.3, size=38)]))
at("That's the published, peer-reviewed position", collage([
    dict(k="cut", img=cutout("vintage_stack_of_books.png", red=False), x=760, y=560, h=460, at=0.0),
    stamp("PEER-REVIEWED", 1250, 560, at=0.3, rot=-7, color="#15191C", size=110)]))
at("But the current team raises points", clip(420, zoom=1.04))
at("The formation's symmetry is striking", spot("ind2_01", center=[0.5, 0.5], radius=[0.2, 0.36], label="Striking symmetry", hit=0.3, zoom=1.12))
at("The mudflow-around-a-boulder theory", collage([
    pc("ind2_01", 960, 540, 1500, rot=0, at=0.0, pad=0, tape=False),
    dict(k="arrow", **{"from": [1320, 900]}, to=[1320, 260], at="@faces uphill", bend=0, color="#F2B134"),
    strip("POINTED END → UPHILL", 1450, 220, at="@faces uphill", size=44),
    strip("“A fluid-dynamics problem” — the team's defenders", 900, 980, at="@has a fluid-dynamics problem", size=34)], bg="cork"))
at("And the team's drilling, they say", photo("cand_31", move="right", zoom=1.12, chip="“No continuous bedrock inside”", chip_at=0.8))
at("which they present as contradicting", clip(41, zoom=1.04))
at("Are those kill shots", words([W_("KILL SHOTS?", y=430, at=0.0, size=160), W_("NO.", y=640, at="@No", size=200, color="#E5484D")], bg="cand_31"))
at("Symmetry can emerge from folded strata", dict(type="geo", variant="syncline", beats=dict(deposit=-3, fold=-2.5, plan=0.3, slide=99),
    labels=[dict(text="Folded strata → a lens shape", x=960, y=110, at=0.3, size=42)]))
at("The \"no bedrock\" point cuts both ways", dict(type="geo", variant="slump", beats=dict(deposit=0.1, fold="@a slumped block riding", cav=99),
    labels=[dict(text="“No bedrock” cuts both ways", x=960, y=120, at=0.2, size=42),
            dict(text="A block riding on clay isn't in-situ bedrock either", x=960, y=1000, at="@wouldn't read as in-situ", size=38)]))
at("But these are real arguments", clip(206, zoom=1.04, then=(120, 82)))
at("That's what makes this a genuine controversy", collage([
    title_("SIMPLE HOAX", 960, 330, at=0.0, size=130, color="#8C8C8C"),
    stamp("GENUINE CONTROVERSY", 960, 600, at="@a genuine controversy", rot=-5, size=120),
    strip("the dispute: how to interpret real observations", 960, 860, at="@the dispute is over", size=40)]))

# =================================================================== the roadmap
at("So what would actually confirm this", words([
    W_("NOT A QUOTE.", y=330, at="@Not a quote", size=120), W_("NOT A RADAR IMAGE.", y=500, at="@Not a radar image", size=120),
    W_("WHAT WOULD IT TAKE?", y=720, at="@What would it take", size=130, color="#3DBE7A")], bg="cand_182", grade="none"))
at("The roadmap is refreshingly concrete", checklist("THE ROADMAP TO “CONFIRMED”", [
    dict(text="1 · Microscopy on the cores", at=0.4, mark="dot"), dict(text="2 · Radiocarbon dating", at=1.0, mark="dot"),
    dict(text="3 · Independent replication", at=1.6, mark="dot"), dict(text="4 · Peer-reviewed publication", at=2.2, mark="dot")],
    bg="cand_182", size=76, gap=150, y0=300))
at("First: microscopy on the cores", photo("cand_188", move="in", zoom=1.2, grade="none", chip="Step 1 · microscopy", chip_at=0.2))
at("If petrified wood exists", collage([
    dict(k="cut", img=cutout("cand_179", red=False, height=700), x=760, y=540, h=560, at=0.0),
    strip("growth rings", 1420, 380, at="@growth rings", rot=-2, size=44),
    strip("vessel structures", 1460, 560, at="@vessel structures", rot=2, size=44),
    dict(k="arrow", **{"from": [1300, 400]}, to=[960, 470], at="@growth rings", bend=30),
    dict(k="arrow", **{"from": [1320, 580]}, to=[1000, 600], at="@vessel structures", bend=-30)]))
at("When wood petrifies", dict(type="cells", beats=dict(show=0.1, replace="@minerals replace the organic", dur=3.0),
    labels=[dict(text="Minerals replace the tissue, cell by cell", x=960, y=110, at="@minerals replace", size=40),
            dict(text="…the anatomy survives in stone", x=960, y=980, at="@preserving its anatomy", size=40)]))
at("That is a yes-or-no answer", words([W_("YES", x=620, y=540, at=0.0, size=260, color="#3DBE7A"),
                                        W_("or", x=960, y=560, at=0.25, size=90, font="GaramondI"),
                                        W_("NO", x=1300, y=540, at=0.45, size=260, color="#E5484D")], bg="cand_189", grade="none"))
at("Second: radiocarbon dating", clip(404, zoom=1.06, chip="Step 2 · radiocarbon dating", chip_at=0.2))
at("If the carbon dates to a few centuries", collage([
    title_("IF THE CARBON COMES BACK…", 960, 120, at=0.0, size=70),
    strip("a few centuries — or matching the sediments", 520, 330, at=0.3, size=32),
    stamp("ARK INTERPRETATION FINISHED", 500, 540, at="@the ark interpretation is finished", rot=-5, size=40),
    strip("four to five thousand years old", 1420, 330, at="@If it came back around", size=32),
    stamp("A HARD PROBLEM FOR SKEPTICS", 1430, 620, at="@skeptics would face", rot=4, size=42, color="#15191C"),
    strip("…but ancient carbon is not automatically a ship", 960, 850, at="@though even then", size=38)]))
at("Third: independent replication", clip(283, zoom=1.05, chip="Step 3 · independent replication", chip_at=0.2))
at("Outside geologists and geophysicists", dict(type="network", center="RAW DATA + CORES", nodes=[
    dict(label="Outside geologists", at=0.3), dict(label="Geophysicists", at="@and geophysicists"),
    dict(label="No stake in the outcome", at="@with no stake"), dict(label="Competing hypotheses", at="@competing hypotheses")]))
at("And fourth: peer-reviewed publication", collage([
    title_("STEP 4 · PEER REVIEW", 960, 170, at=0.0, size=100, underline=True),
    strip("Methods: open", 960, 400, at="@methods open", size=48),
    strip("Data: open", 960, 540, at="@data open", size=48),
    strip("Conclusions: exposed to attack", 960, 680, at="@conclusions exposed", size=48)]))
at("The team says all of this is planned", dict(type="timeline", img=img("cand_12"),
    events=[dict(year="Sept 2026", label="Cores drilled"), dict(year="Winter", label="Compositional · organic · stratigraphic tests"),
            dict(year="2027", label="A public scientific statement")],
    stops=[dict(i=0, at=0.0), dict(i=1, at="@testing through the winter"), dict(i=2, at="@with a public scientific")]))
at("They also intend to send", collage([
    title_("G.O.P.H.E.R.", 960, 260, at=0.0, size=150),
    strip("named for the gopher wood of Genesis", 960, 400, at="@after the gopher wood", size=40),
    pc("cand_14", 960, 790, 260, rot=-2, at="@into the radar-mapped voids")]))
at("If that drone ever returns images", photo("cand_498", move="in", zoom=1.1, chip="Illustration: timber construction", chip_at=0.5))
at("If it returns dissolved limestone passages", dict(type="geo", variant="slump", beats=dict(deposit=-1, fold=-4, cav=0.2),
    labels=[dict(text="Dissolved limestone passages → the geology stands", x=960, y=120, at=0.2, size=40)]))
at("Either outcome is possible", words([W_("EITHER OUTCOME IS POSSIBLE.", y=540, at=0.0, size=120)], bg="cand_089"))
at("But as of today, the drone has not flown", checklist("AS OF TODAY", [
    dict(text="The drone has flown", at=0.2, mark="no"), dict(text="The labs have reported", at="@The labs have not", mark="no"),
    dict(text="The journals have published", at="@The journals have not", mark="no")], bg="cand_089", size=80, gap=160, y0=320))

# =================================================================== the answer
at("Which brings us back to the title", clip(504, skip=5.0, zoom=1.03))
at("Noah's Ark — one hundred percent confirmed?", dict(type="title", img=img("cand_089"), kicker="",
                                                       title="100% CONFIRMED?", subtitle="Noah's Ark", tagline=""))
at("No. Not by the standard", gauge("CONFIRMED?", 100, "“one hundred percent” certainty", bg="cand_089", from_=100, at=0.05, d=0.05,
                                    to2=0, at2=0.2, d2=1.4, label2="confirmed by no laboratory, scientist or paper"))
at("The \"one hundred percent\" is one sincere man's", quote("“One hundred percent” is one sincere man's statement of belief.",
                                                             bg="cand_308", size=80, rate=3.6, highlight=["belief"]))
at("Strip away the headline", photo("cand_305", move="in", zoom=1.12, chip="Permitted · university-supervised · first of its kind",
                                    chip_at="@a genuinely permitted"))
at("the first of its kind", clip(504, skip=20.0, zoom=1.03))
at("Real cores from nearly sixty feet down", photo("cand_60", move="in", fit="contain", chip="≈60 ft · in cold storage", chip_at=0.3))
at("Organic-rich layers, now awaiting testing", clip(400, zoom=1.08))
at("Underground cavities consistent", clip(224, skip=0.5, zoom=1.08, then=(74,)))
at("A hard layer at four to five meters that broke", photo("cand_161", move="up", fit="contain", zoom=1.08))
at("Scans showing boundaries", photo("cand_241", move="in", zoom=1.1))
at("Soil with elevated organics", clip(40, skip=0.4, zoom=1.06, then=(58,)))
at("And a sixty-six-year-old controversy", clip(397, skip=0.2, zoom=1.08, then=(396,)))
at("That's the honest state of play", words([W_("LESS THAN “CONFIRMED.”", y=430, at="@It's less than", size=130),
                                             W_("MORE THAN “NOTHING.”", y=630, at="@And it's more than", size=130, color="#F2B134")], bg="cand_089"))
at("And maybe that's the real story here", photo("cand_307", grade="bw", move="in", zoom=1.1))
at("Ron Wyatt claimed petrified timbers", photo("cand_299", grade="bw", crop=(0.0, 0.0, 1.0, 0.78), move="in", zoom=1.08))
at("Geologists published", words([W_("GEOLOGISTS PUBLISHED.", y=320, at=0.0, size=110),
                                  W_("BELIEVERS BELIEVED.", y=490, at="@believers believed", size=110),
                                  W_("NOTHING MOVED.", y=700, at="@nothing moved", size=140, color="#F2B134")], bg="cand_46", crop=(0.12, 0.0, 0.86, 1.0)))
at("Now, finally, there are physical samples", photo("cand_11", move="in", focus=[0.7, 0.5], fit="contain"))
at("Whatever you hope is down there", words([W_("FROM ASSERTION", y=430, at="@from assertion", size=140),
                                             W_("TO EVIDENCE.", y=630, at="@to evidence", size=160, color="#3DBE7A")], bg="cand_308"))
at("Even the researchers' fiercest critics", clip(54, zoom=1.03))
at("Even their most devoted supporters", clip(64, zoom=1.04))
at("Because the story of Noah", clip(381, zoom=1.05, then=(412,)))
at("It asks for belief", clip(446, skip=3.0, grade="none", zoom=1.04))
at("And the rock formation on that Turkish", clip(37, zoom=1.03))
at("to be judged by evidence", clip(16, zoom=1.03, then=(124, 135)))
at("So is the ark one hundred percent confirmed", words([
    W_("100% CONFIRMED?", y=420, at=0.0, size=150, strike="@No — and anyone"),
    W_("NO.", y=640, at="@No — and anyone", size=200, color="#E5484D")], bg="cand_089"))
at("Is the investigation more real", checklist("THE INVESTIGATION IS…", [
    dict(text="More real", at="@more real"), dict(text="More serious", at="@more serious"),
    dict(text="More testable than ever before", at="@and more testable")], bg="cand_305", size=84, gap=160, y0=320))
at("The cores are in the lab queue", clip(404, skip=0.3, zoom=1.06, chip="In the lab queue · winter 2026–27", chip_at=0.4))
at("When those results land", collage([
    strip("RESULTS: PENDING", 960, 380, at=0.1, size=64),
    strip("confirmation · refutation · something stranger", 960, 520, at="@confirmation, refutation", size=44),
    strip("we'll go through them here — line by line", 960, 660, at="@we'll go through them", size=44),
    stamp("WINTER 2026–27", 960, 860, at=1.2, rot=-5, size=100, color="#15191C")]))
at("Observed, claimed, confirmed", filt([], headAt=["@Observed", "@claimed", "@confirmed"], focus=CON,
                                        focusAt="@And only one of them counts", overlays=[dict(type="fadeout", d=1.8)]))


# ------------------------------------------------------------------- music
# One quiet bed per act; the levels are set in edl.setup above.
MUSIC = [
    dict(at=None, track="06_SCP-x6x_Hopes_Mysterious.mp3", db=0),
    dict(at="Pillar one", track="12_Magic_Forest_Dark_Cello.mp3", db=0, lead=-1.0),
    dict(at="Which brings us to the history", track="04_Sad_Trio_Somber_Piano_Cello.mp3", db=0, lead=-0.8),
    dict(at="Pillar two", track="Dramatic Piano Pulse.mp3", db=-1, lead=-1.0),
    dict(at="Pillar three", track="02_Leaving_Home_Somber_Long_Bed.mp3", db=0, lead=-1.0),
    dict(at="Pillar four", track="01_Metaphysik_Dramatic_Strings_Bed.mp3", db=-1, lead=-1.0),
    dict(at="Now, in the spirit of honesty", track="03_Sovereign_Dark_Piano_Bed.mp3", db=0, lead=-0.8),
    dict(at="So what would actually confirm this", track="Mark Jubel - Efteraar.mp3", db=0, lead=-0.8),
    dict(at="Which brings us back to the title", track="05_Despair_and_Triumph_Dark_Piano.mp3", db=0, lead=-0.8),
]


if __name__ == "__main__":
    edl.main(MUSIC)
