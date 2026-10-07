"""
gallery.py - render a preview of every scene type, in every theme.

    python gallery.py --kit /path/to/kit --photo landscape.jpg --portrait person.jpg \
                      --scan radar.jpg --object object.png [--out previews] [--themes paper,forensic,expedition]

It prepares the four pictures (grades, blur / dim variants, a cut-out of the portrait),
renders one frame of each scene spec below and writes previews/<theme>/<type>.jpg plus a
contact sheet per theme. The specs double as copy-paste examples: every key used here is
a real option of that scene.

Also a smoke test: after changing the engine, run it and look at the sheets.
"""

import argparse
import copy
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DOCU = os.path.dirname(HERE)
sys.path.insert(0, DOCU)

import prep      # noqa: E402
import render    # noqa: E402

# ------------------------------------------------------------------ the specs
# Picture names refer to the prepared files: P = landscape, PORT = portrait, SCAN = scan.
P, PORT, SCAN, OBJ = "g_photo.jpg", "g_portrait.jpg", "g_scan.jpg", "g_object.png"


def specs():
    S = []

    def add(name, spec, dur=6.0, themes=None):
        spec = dict(spec)
        spec.update(id=name, duration=dur, t0=0.0)
        S.append((name, spec, themes))

    # ---- photographs
    add("photo", dict(type="photo", img=P, move="in", focus=[0.5, 0.5], zoom=1.15,
                      overlays=[dict(type="chip", text="A chip label", at=0.3),
                                dict(type="source", text="Source: archive", at=0.5)]))
    add("photo_contain", dict(type="photo", img=PORT, fit="contain", move="in", zoom=1.1))
    add("depth", dict(type="depth", img=PORT, subject=[0.5, 0.5], hit=0.8, move="in",
                      overlays=[dict(type="lower", name="Person Name", role="Who they are", at=1.2)]))
    add("spotlight", dict(type="spotlight", img=P, center=[0.5, 0.55], radius=[0.16, 0.2], label="Look here", hit=0.4,
                          side="right", zoom=1.18))
    add("tv", dict(type="tv", img=P, focus=[0.5, 0.5]))
    add("card", dict(type="card", img=SCAN, focus=[0.5, 0.5], zoom=1.2, height=860))
    add("split", dict(type="split", left=PORT, right=P, leftLabel="Before", rightLabel="After"))

    # ---- paper
    add("collage", dict(type="collage", bg="paper", items=[
        dict(k="photo", img=P, x=560, y=470, w=720, rot=-3, at=0.0, caption="A taped photo card"),
        dict(k="cut", img=OBJ, x=1480, y=620, h=460, at=0.3),
        dict(k="stamp", text="CLAIMED", x=1300, y=250, at=0.6, rot=-8, size=100),
        dict(k="strip", text="a typewriter strip", x=620, y=900, at=0.9, rot=-1, size=40),
        dict(k="note", text="a sticky note in handwriting", x=1560, y=870, at=1.2, rot=4, w=380),
        dict(k="circle", x=560, y=470, rx=200, ry=140, at=1.6),
        dict(k="arrow", **{"from": [1050, 900]}, to=[800, 620], at=1.9, bend=60)]))
    add("corkboard", dict(type="collage", bg="cork", items=[
        dict(k="photo", img=P, x=520, y=420, w=560, rot=-4, at=0.0),
        dict(k="photo", img=PORT, x=1420, y=460, w=380, rot=3, at=0.2),
        dict(k="pin", x=520, y=180, at=0.5), dict(k="pin", x=1420, y=150, at=0.6),
        dict(k="string", pts=[[520, 180], [960, 330], [1420, 150]], at=0.9),
        dict(k="stat", value="88", label="samples", x=960, y=820, at=1.2, rot=-2),
        dict(k="title", text="THE BOARD", x=960, y=90, at=0.1, size=90, underline=True, color="#F4EFE4",
             shadow="0 6px 24px rgba(0,0,0,.7)")]))
    add("newspaper", dict(type="newspaper", masthead="THE MORNING LEDGER", date="SEPTEMBER 23, 1960", edition="LATE EDITION",
                          price="10 CENTS", headline="A SHIP ON\nA MOUNTAIN?", deck="Aerial survey finds a boat-shaped mound",
                          body=["Lorem ipsum dolor sit amet, consectetur adipiscing elit. " * 40], img=P, caption="The formation from the air"),
        dur=5.0)
    add("headlines", dict(type="headlines", items=[
        dict(text="THE FIRST HEADLINE", x=820, y=300, rot=-3, at=0.1, size=90, style="white"),
        dict(text="A SECOND ONE, IN RED", x=1100, y=560, rot=2, at=0.6, size=76, style="red"),
        dict(text="AND A THIRD", x=840, y=810, rot=-1.5, at=1.1, size=84, style="tan", sub="with a sub line")]))
    add("baskets", dict(type="baskets", reveal=True, at=0.2, gap=0.5))
    add("chapter", dict(type="chapter", n="01", kicker="PART ONE", title="THE CHAPTER TITLE", img=P, move="in", zoom=1.12))

    # ---- type and numbers
    add("title", dict(type="title", img=P, kicker="AN INVESTIGATION", title="THE TITLE", subtitle="A subtitle line",
                      tagline="WHAT WE ACTUALLY KNOW"))
    add("stat", dict(type="stat", img=P, value="515 FT", kicker="END TO END", note="about 157 metres",
                     source="Source: survey 2019", countFor=1.2))
    add("quote", dict(type="quote", img=PORT, text="“A quote revealed word by word, with a marker on the key word.”",
                      who="Speaker — where it was said", highlight=["key"], size=80, rate=8))
    add("words", dict(type="words", img=P, items=[
        dict(text="KINETIC", y=320, at=0.0, size=150),
        dict(text="TYPE, STRUCK", y=520, at=0.5, size=150, strike=1.2),
        dict(text="ON CUE.", y=720, at=1.4, size=150, color="#D9A441")]))
    add("ledger", dict(type="ledger", lines=[
        dict(text="Creation of the world ........ 4004 BC", at=0.1, y=260),
        dict(text="To the Flood .................... 1,656 years", at=0.9, y=390),
        dict(text="The Flood .......................... 2348 BC", at=1.7, y=540, color="#8a1a10", size=72)],
        ruleY=495, ruleAt=1.5, ruleW=1200, circle=dict(x=1300, y=585, rx=240, ry=70, at=2.6)))
    add("timeline", dict(type="timeline", img=P, events=[
        dict(year="1959", label="First aerial photograph"), dict(year="1960", label="First expedition"),
        dict(year="2026", label="First drilling")], stops=[dict(i=0, at=0.0), dict(i=1, at=1.2), dict(i=2, at=2.6)]))
    add("measure", dict(type="measure", title="LENGTH COMPARED", pxPerFt=2.7, bars=[
        dict(label="ROYAL CUBIT", ft=515, value="≈515 FT", at=0.1),
        dict(label="COMMON CUBIT", ft=450, value="≈450 FT", at=0.6, color="#8C8C8C"),
        dict(label="THE FORMATION", ft=515, value="≈515 FT", at=1.1, color="#D62E1F")],
        stamp=dict(text="MATCH?", at=2.2, x=1300, y=840)))
    add("checklist", dict(type="checklist", kicker="WHAT WOULD CONFIRM IT", img=P, items=[
        dict(text="Microscopy", at=0.2, mark="yes"), dict(text="Radiocarbon dating", at=0.7, mark="maybe"),
        dict(text="Independent replication", at=1.2, mark="no"), dict(text="A plain bullet", at=1.7, mark="dot")],
        size=70, gap=140, y0=300))
    add("geo_syncline", dict(type="geo", variant="syncline", beats=dict(deposit=-2, fold=-1.5, plan=0.2, slide=1.0),
                             labels=[dict(text="A doubly plunging syncline", x=960, y=110, at=0.2, size=40)]))
    add("geo_slump", dict(type="geo", variant="slump", beats=dict(deposit=-1, fold=-3, cav=0.2),
                          labels=[dict(text="A slumped block, hollowed by dissolution", x=960, y=120, at=0.2, size=40)]))

    # ---- maps
    add("map_globe", dict(type="map", stops=[dict(at=0, lon=-40, lat=30, scale=430), dict(at=0.5, lon=20, lat=35, scale=460, d=2.5)],
                          pins=[dict(lon=-86.4, lat=35.9, label="Tennessee", sub="from here", at=0.2, side="left")],
                          routes=[dict(**{"from": [-86.4, 35.9]}, to=[44.23, 39.44], at=0.6, d=2.0, dash=True)],
                          dots=[dict(lon=44.23, lat=39.44, label="Durupınar", at=2.0)]))
    add("map_region", dict(type="map", detail="geo_hi.json",
                           stops=[dict(at=0, lon=36, lat=39.2, scale=2900), dict(at=0.3, lon=43.2, lat=39.5, scale=9000, d=2.5)],
                           highlight=[dict(id="TUR", at=0.1)], names=[dict(text="Iran", lon=45.6, lat=39.1, at=1.0, size=40)],
                           circles=[dict(lon=44.2983, lat=39.7019, km=29, at=2.0)],
                           pins=[dict(lon=44.2317, lat=39.4403, label="Durupınar", sub="the formation", at=1.5, side="left")]))

    # ---- forensic / lab
    add("filter", dict(type="filter", items=[
        dict(text="The formation exists", col=0, at=0.1), dict(text="Straight lines on radar", col=0, at=0.5),
        dict(text="Decks and chambers", col=1, at=0.9), dict(text="A petrified hull", col=1, at=1.3)],
        zeroAt=2.0, zeroText="nothing confirmed yet"), themes=["forensic"])
    add("gauge", dict(type="gauge", img=P, kicker="CERTAINTY", from_=0, to=100, at=0.1, d=1.0, label="claimed",
                      to2=0, at2=1.8, d2=1.0, label2="confirmed by a laboratory"), themes=["forensic"])
    add("network", dict(type="network", center="ONE SOURCE", nodes=[
        dict(label="Press release", at=0.2), dict(label="Interview", at=0.5), dict(label="Viral post", at=0.8),
        dict(label="Headline", at=1.1), dict(label="Independent lab?", at=1.4, dashed=True)],
        stamp=dict(text="ONE SOURCE", at=2.2)), themes=["forensic"])
    add("valley", dict(type="valley", beats=dict(draw=0.1, boat=0.8, measure=1.4, water=2.0),
                       labels=[dict(text="A 1,000 m deep valley", x=1480, y=700, at=1.4, size=38)]), themes=["forensic"])
    add("cells", dict(type="cells", beats=dict(show=0.1, replace=0.6, dur=2.0),
                      labels=[dict(text="Minerals replace the tissue, cell by cell", x=960, y=110, at=0.3, size=40)]),
        themes=["forensic"])
    add("scan_item", dict(type="collage", bg="cork", items=[
        dict(k="photo", img=SCAN, x=960, y=520, w=1100, rot=-1, at=0.0),
        dict(k="scan", x=410, y=210, w=1100, h=620, at=0.4, period=2.0)]), themes=["forensic"])

    # ---- expedition / courtroom
    add("scales", dict(type="scales", title="THE CASE, WEIGHED", left=dict(title="THE CLAIM"), right=dict(title="THE GEOLOGY"),
                       items=[dict(side=0, text="Radar: straight lines", at=0.2), dict(side=0, text="Soil: 3× organics", at=0.6),
                              dict(side=1, text="Right-angle joints are natural", at=1.0),
                              dict(side=1, text="Peer-reviewed geology", at=1.4, w=2)]), themes=["expedition"])
    add("scoreboard", dict(type="scoreboard", title="THE SCOREBOARD · YEAR 2000", rows=[
        dict(n="1", text="FAILED DIG", at=0.2, stamp=dict(text="1960", at=2.0, size=48)),
        dict(n="1", text="RECANTED MOVEMENT", at=0.8), dict(n="1", text="VERY STUBBORN SHAPE", at=1.4, color="#9E2B25")]),
        themes=["expedition"])
    add("verdict", dict(type="verdict", left=dict(title="REALITY", sub="what is real"), right=dict(title="MYTH", sub="at least so far"),
                        items=[dict(side=0, text="The shape", at=0.3), dict(side=0, text="The expedition", at=0.6),
                               dict(side=1, text="The decks", at=0.9), dict(side=1, text="“One hundred percent”", at=1.2)],
                        stamp=dict(text="NOT YET VERIFIED", at=2.0)), themes=["expedition"])
    add("tags", dict(type="collage", bg="cork", items=[
        dict(k="tag", text="EXHIBIT A", sub="The scans", x=560, y=380, at=0.1, rot=-4),
        dict(k="tag", text="EXHIBIT B", sub="The soil", x=1300, y=420, at=0.4, rot=5),
        dict(k="tag", text="EXHIBIT C", sub="The cores", x=620, y=760, at=0.7, rot=3),
        dict(k="tag", text="EXHIBIT D", sub="The drill bit", x=1340, y=780, at=1.0, rot=-3)]), themes=["expedition"])
    # ---- broadcast / news desk
    TK = dict(type="ticker", label="BREAKING", clock="SEPT 2026", items=["A ticker crawl that keeps moving across cuts",
                                                                          "Second item of the crawl", "Third item"])
    BG = dict(type="bug", place="A place · A country")
    add("breaking", dict(type="breaking", img=P, headline="THE HEADLINE OF THE STORY GOES ON THIS WHITE BAR",
                         sub="Where · when · the sub line", overlays=[TK, BG]), themes=["broadcast"])
    add("segment", dict(type="segment", n="01", kicker="PART 01", title="WHAT WE CAN VERIFY", sub="The segment's sub line", img=P),
        themes=["broadcast"])
    add("borehole", dict(type="borehole", title="FOUR TO FIVE METRES DOWN", kicker="A BOREHOLE", beats=dict(draw=0.1, drill=0.6, hit=3.2),
                         cavities=[dict(depth=3.3, x=1010, w=110, h=30, water=True, at=0.8, fill=1.0)],
                         labels=[dict(text="Soil & sediment", depth=1.2, at=0.8), dict(text="Organic-rich interval", depth=2.35, at=1.4),
                                 dict(text="A cavity filling with water", depth=3.3, at=2.0, dy=50),
                                 dict(text="A layer harder than limestone?", depth=5.0, at=3.4, bg="#E10600", color="#fff")],
                         stamp=dict(text="BIT SHATTERED", at=3.6, size=48, x=1585, y=780)), themes=["broadcast"])
    add("factcheck", dict(type="factcheck", claim="“A claim, quoted exactly as it was made.”", source="— who said it, where, when",
                          rating="UNVERIFIED", ratingAt=2.2, note="What we actually know about it."), themes=["broadcast"])
    add("echo", dict(type="echo", headlines=[dict(text=f"A headline repeating the claim, version {i + 1}") for i in range(8)],
                     sources=[dict(title="1 PRESS RELEASE", sub="who wrote it"), dict(title="1 INTERVIEW", sub="who gave it")],
                     collapseAt=2.4, gap=0.12), dur=6.0, themes=["broadcast"])
    add("columns", dict(type="columns", left=dict(title="OBSERVED", sub="instrument record"), right=dict(title="CLAIMED"),
                        items=[dict(side=0, text="What was measured", tag="by whom", at=0.2), dict(side=0, text="What was recorded", tag="by whom", at=0.4),
                               dict(side=1, text="What it is said to mean", at=0.6), dict(side=1, text="A bigger claim on top", at=0.8)],
                        gapAt=1.4, gapText="THE COLUMNS NEVER TOUCH"), themes=["broadcast"])
    add("videowall", dict(type="videowall", imgs=[P, SCAN, PORT], focus=4, pushAt=3.5), themes=["broadcast"])
    add("newslist", dict(type="newslist", title="A NUMBERED LIST", items=[
        dict(text="A row with a green status", at=0.2, status="CONFIRMED", statusColor="#18C07A"),
        dict(text="A row with a yellow status", at=0.5, status="PER THE TEAM", statusColor="#FFC21A"),
        dict(text="A row with a red status", at=0.8, status="NOT YET", statusColor="#E10600"),
        dict(text="A row with a plain status", at=1.1, status="UNANSWERED")], y0=280), themes=["broadcast"])
    add("newslower", dict(type="photo", img=P, move="in", overlays=[
        dict(type="newslower", kicker="ON THE GROUND", text="A BROADCAST LOWER THIRD", sub="the sub strip", at=0.3), TK, BG]),
        themes=["broadcast"])
    # ---- calm documentary
    add("doctitle", dict(type="doctitle", img=P, kicker="Chapter 1", title="The Numbers", sub="What makes people ask"),
        themes=["documentary"])
    add("textcard", dict(type="textcard", img=P, lines=[dict(text="A calm line of text", at=0.2),
                                                         dict(text="and its answer, in gold.", at=0.8, color="#D8B26E")]),
        themes=["documentary"])
    add("bars", dict(type="bars", img=P, title="A calm comparison", note="a note under the title",
                     bars=[dict(label="First", value=50, text="≈ $50,000", at=0.3), dict(label="Second", value=98, text="≈ $98,000", at=0.8)],
                     max=100, source="Source: where the numbers come from"), themes=["documentary"])
    add("ledgerlist", dict(type="ledgerlist", img=P, title="The household ledger", items=[
        dict(label="1  Earned income", value="modest", at=-3), dict(label="2  Benefits scaled to household size", value="per person", at=-3),
        dict(label="3  Schooling", value="a fraction of market cost", at=0.4, color="#D8B26E")],
        total=dict(label="A system that doesn't need a high income", value="", at=1.2)), themes=["documentary"])
    add("sizechart", dict(type="sizechart", img=SCAN, title="The same income, a bigger family",
                          note="eligibility limits rise with every person (illustrative)", income=3.3, incomeLabel="one fixed income",
                          at=0.2, per=0.15, incomeAt=1.9), themes=["documentary"])
    add("place", dict(type="photo", img=P, move="in", overlays=[dict(type="place", text="A place, A state", sub="a line about it", at=0.3)]),
        themes=["documentary"])
    add("doclower", dict(type="photo", img=PORT, move="in", overlays=[dict(type="doclower", name="A Name", role="who they are", at=0.3)]),
        themes=["documentary"])
    # ---- heritage gazetteer (the almanac's second edition)
    A2 = ["almanac2"]
    add("gzhead", dict(type="photo", img=P, move="in", zoom=1.08, overlays=[
        dict(type="gzhead", n=4, kicker="Chapter four", title="What a settlement is", plate="plate",
             sub="one or more church districts, geographically connected", at=0.3)]), 9.0, A2)
    add("gztag", dict(type="photo", img=P, move="left", overlays=[
        dict(type="gztag", text="Cashton, Wisconsin", sub="founded in the 1960s", at=0.3)]), 7.0, A2)
    add("gzcard", dict(type="gzcard", img=P, kicker="the building block", lines=[
        dict(text="Pennsylvania built giants.", at=0.4),
        dict(text="Wisconsin built dots.", at=1.6, color="#7A2F2A")]), 8.0, A2)
    add("gzstat", dict(type="gzstat", img=P, value="44,765", kicker="Lancaster County settlement · 2025",
                       unit="people", note="larger than the whole Amish population of Wisconsin",
                       source="Young Center for Anabaptist and Pietist Studies", at=0.4, countFor=1.6), 8.0, A2)
    add("gzversus", dict(type="gzversus", title="Two states, two shapes of growth", note="2025 estimates",
                         left=dict(name="Pennsylvania", sub="the heartland"), right=dict(name="Wisconsin", sub="the frontier"),
                         rows=[dict(label="Amish residents", left="95,410", right="27,535", at=1.2, win="l", mark="3× more"),
                               dict(label="Settlements", left=63, right=68, at=2.8, win="r", mark="five more"),
                               dict(label="Church districts", left=636, right=209, at=4.4, win="l")],
                         verdict="more people there, more communities here", verdictAt=6.0), 9.5, A2)
    add("gzgiants", dict(type="gzgiants", title="One dot is not one community",
                         giant=dict(value="44,765", label="Lancaster County", sub="one settlement, 267 districts", at=0.8),
                         field=dict(n=68, label="Wisconsin", sub="68 settlements, 27,535 people", at=2.6, fill=2.0)), 9.0, A2)
    add("gzdivide", dict(type="gzdivide", title="How a district divides", frameLabel="one settlement",
                         note="20 to 40 households each", steps=[
                             dict(n=1, label="One church district", at=0.9),
                             dict(n=2, label="One becomes two", at=2.3),
                             dict(n=3, label="Two become three", at=3.6),
                             dict(n=10, label="Three become ten - still one settlement", at=5.0)]), 9.0, A2)
    add("gzindex", dict(type="gzindex", title="Settlements by state, 2025", note="the frontier is wider than it looks",
                        rows=[dict(label="Ohio", value=74, at=0.8), dict(label="Wisconsin", value=68, at=1.7, hi=True),
                              dict(label="Missouri", value=64, at=2.6), dict(label="Pennsylvania", value=63, at=3.5),
                              dict(label="New York", value=60, at=4.4)],
                        foot="five states, five different maps", footAt=5.6), 9.0, A2)
    add("gzdelta", dict(type="gzdelta", title="A decade apart", frm="2015", to="2025", items=[
        dict(label="Pennsylvania", **{"from": 465, "to": 636}, delta="+171 districts", at=0.9, note="nine new settlements"),
        dict(label="Wisconsin", **{"from": 138, "to": 209}, delta="+71 districts", at=3.4, note="eighteen new settlements",
             color="#38655C")], foot="one grew inward, the other outward", footY=840, footAt=6.2), 9.5, A2)
    add("gzmap", dict(type="map", detail="geo_hi.json", adminCountries=["USA"], title="Plat of the Amish map",
                      stops=[dict(at=0, lon=-85.5, lat=42.0, scale=4200)],
                      highlight=[dict(id="USA-3560", at=0.4), dict(id="USA-3553", at=1.0)],
                      pins=[dict(lon=-76.3, lat=40.04, label="Lancaster Co.", sub="44,765 people", at=1.6, side="right"),
                            dict(lon=-90.78, lat=43.74, label="Cashton", sub="the state's largest", at=2.4, side="left")],
                      dots=[dict(lon=-90.0 + (i % 8) * 0.55, lat=43.0 + (i // 8) * 0.42, r=6, at=3.0 + i * 0.04) for i in range(24)]),
        8.0, A2)
    add("almbars", dict(type="almbars", title="People per settlement", note="statewide average, 2025",
                        bars=[dict(label="Pennsylvania", value=1514, text="1,514", at=0.6),
                              dict(label="Wisconsin", value=405, text="405", at=1.6, color="#38655C")]), 8.0, A2)
    add("almgrowth", dict(type="almgrowth", title="The Amish population of North America", note="estimates",
                          points=[dict(x=2000, y=177910, label="177,910", at=1.0),
                                  dict(x=2010, y=249500, label="249,500", at=2.2),
                                  dict(x=2025, y=410955, label="410,955", at=3.6)],
                          grid=[dict(y=200000, label="200,000"), dict(y=400000, label="400,000")]), 8.0, A2)
    return S


# ------------------------------------------------------------------ build

def prepare(args, assets):
    prep.make_surfaces(assets, args.kit)
    jobs = [(args.photo, "g_photo", False, ("blur", "dim")), (args.portrait, "g_portrait", True, ("blur", "dim", "soft")),
            (args.scan, "g_scan", False, ("blur",))]
    for src, key, cut, var in jobs:
        if not os.path.exists(os.path.join(assets, key + ".jpg")):
            prep.prepare_image(src, assets, key, "doc", None, cut, var)
    if not os.path.exists(os.path.join(assets, "g_object.png")):
        prep.prepare_cutout(args.object, assets, "g_object", halftone=False, height=900, keyline=6, red=False)


def sheet(paths, out, cols=4):
    from PIL import Image, ImageDraw, ImageFont
    W, H = 480, 270
    rows = (len(paths) + cols - 1) // cols
    im = Image.new("RGB", (cols * W, rows * (H + 24)), "#111")
    d = ImageDraw.Draw(im)
    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", 16)
    except OSError:
        font = ImageFont.load_default()
    for i, p in enumerate(paths):
        x, y = (i % cols) * W, (i // cols) * (H + 24)
        im.paste(Image.open(p).convert("RGB").resize((W, H)), (x, y))
        d.text((x + 6, y + H + 3), os.path.splitext(os.path.basename(p))[0], fill="#F2C14E", font=font)
    im.save(out, quality=85)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--kit", required=True)
    ap.add_argument("--photo", required=True, help="a landscape photograph")
    ap.add_argument("--portrait", required=True, help="a person (gets a depth-pop cut-out)")
    ap.add_argument("--scan", required=True, help="a scan / chart / document")
    ap.add_argument("--object", required=True, help="an object photo or PNG to cut out")
    ap.add_argument("--work", default=os.path.join(HERE, "_gallery_work"))
    ap.add_argument("--out", default=os.path.join(HERE, "previews"))
    ap.add_argument("--themes", default="paper,forensic,expedition,broadcast,documentary")
    ap.add_argument("--only", default="", help="comma-separated spec names")
    a = ap.parse_args()
    assets = os.path.join(a.work, "assets")
    prepare(a, assets)
    only = set(filter(None, a.only.split(",")))
    for theme in a.themes.split(","):
        cfg = {"kit": "file://" + os.path.abspath(a.kit), "assets": "file://" + os.path.abspath(assets), "theme": theme, "grain": 0}
        sel = []
        for name, spec, themes in specs():
            if (themes and theme not in themes) or (only and name not in only):
                continue
            s = copy.deepcopy(spec)
            if "from_" in s:
                s["from"] = s.pop("from_")
            sel.append(s)
        tmp = os.path.join(a.work, "stills_" + theme)
        paths = render.stills(sel, cfg, tmp)
        od = os.path.join(a.out, theme)
        os.makedirs(od, exist_ok=True)
        final = []
        from PIL import Image
        for p in paths:
            name = os.path.basename(p).rsplit("_", 1)[0]
            dst = os.path.join(od, name + ".jpg")
            Image.open(p).convert("RGB").resize((800, 450), Image.LANCZOS).save(dst, quality=80)
            final.append(dst)
        if final and not only:
            sheet(final, os.path.join(a.out, f"sheet_{theme}.jpg"))
        print(theme, len(final), "previews")


if __name__ == "__main__":
    main()
