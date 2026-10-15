"""
What Happens If the Government Cuts Hasidic Jews Community Benefits?
Faceless documentary - edit decision list and build.

Look: the calm "documentary" template from video 5 (slow moves over real photographs, soft dissolves,
serif chapter headings, place captions, gentle charts, paper-and-pen sound only), but shuffled by
variety.py: this video gets its own accent colour, font pairing, chapter-number style, grade, grain,
dissolve length, camera-move cycle, caption corner and music order, and prefers pictures and clips
that video 5 never used.

The recurring device is THE ENVELOPE: a brown government envelope on a kitchen table (a prop drawn in
code, docu/tools/props.py). It opens the video, comes back whenever the script asks what the money
actually holds up, and closes the video on the viewer's own envelope. Its counterpart is the list of
WHAT THE STREET RUNS ITSELF (Hatzalah, Shomrim, Chaveirim, Beth Din, free loans, schools).

About 30 % footage clips, 70 % photographs and calm graphics.

    python build.py plan | prep | stills [ids] | render [ids] | mix | final | all
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "docu"))

import edl                       # noqa: E402
from edl import *                # noqa: E402,F401,F403  (the shot helpers)

SP = os.environ.get("VIDEO_ROOT", os.path.join(HERE, "..", "..", "media"))
H5 = f"{SP}/hasidic"
edl.setup(
    name="What_Happens_If_the_Government_Cuts_Hasidic_Benefits",
    kit=os.environ.get("VIDEO_KIT", f"{SP}/kit"),
    footage=os.environ.get("VIDEO_FOOTAGE", f"{H5}/footage"),
    work=os.environ.get("VIDEO_WORK", f"{SP}/work6"),
    data=os.path.join(HERE, "data"),
    out=os.environ.get("VIDEO_OUT", f"{SP}/out"),
    image_dirs=[os.environ.get("VIDEO_PICKS", f"{H5}/picks"), os.environ.get("VIDEO_IMAGES", f"{H5}/src/images")],
    theme="documentary",
    music_floor_db=-21.0, music_duck_db=-10.0, sfx_gain=0.55,
    sfx_style="calm", vary="auto",           # grade, grain and xfade come from the variety picks
)
V = edl.V

ACC = V.accent                         # this video's accent colour (was gold in video 5)
RUST, SAGE = "#B5523B", "#8DAA7B"
NYC = (-74.006, 40.713)
KJ = (-74.168, 41.340)
WILLIAMSBURG = (-73.957, 40.708)
BOROUGH_PARK = (-73.990, 40.634)
NEW_SQUARE = (-74.029, 41.139)
MONSEY = (-74.068, 41.111)
NY_STATE, NJ_STATE, PA_STATE, CT_STATE = "USA-3559", "USA-3558", "USA-3560", "USA-3537"


# ---------------------------------------------------------------- calm building blocks

def ph(name, move=None, zoom=1.08, focus=None, **kw):
    """a photograph with a slow move; the move comes from this video's move cycle unless named"""
    return photo(name, move=move or V.move(), zoom=zoom, focus=focus, **kw)


def cl(i, **kw):
    kw.setdefault("zoom", 1.03)
    return clip(i, **kw)


def place(scene, text, sub=None, at=0.6):
    o = dict(type="place", text=text, at=at)
    if sub: o["sub"] = sub
    scene = dict(scene)
    scene["overlays"] = list(scene.get("overlays", [])) + [o]
    return scene


def who(scene, name, role, at=0.6):
    scene = dict(scene)
    scene["overlays"] = list(scene.get("overlays", [])) + [dict(type="doclower", name=name, role=role, at=at)]
    return scene


def heading(n, title, bg, sub=None, **kw):
    s = dict(type="doctitle", kicker=V.kicker(n), title=title, img=img(bg), move="in", zoom=1.08)
    if sub: s["sub"] = sub
    s.update(kw)
    return s


def card(*lines, bg=None, dim=None, **kw):
    """one to three lines of text over a darkened photo; each line: text or (text, at, color, size)"""
    ls = []
    for ln in lines:
        if isinstance(ln, str):
            ls.append(dict(text=ln))
        else:
            d = dict(text=ln[0])
            if len(ln) > 1 and ln[1] is not None: d["at"] = ln[1]
            if len(ln) > 2 and ln[2]: d["color"] = ln[2]
            if len(ln) > 3 and ln[3]: d["size"] = ln[3]
            ls.append(d)
    s = dict(type="textcard", lines=ls, dim=dim if dim is not None else V["dim"])
    if bg: s["img"] = img(bg)
    s.update(kw)
    return s


def bars(title, rows, bg=None, note=None, source=None, **kw):
    s = dict(type="bars", title=title, bars=[dict(label=r[0], value=r[1], text=r[2], at=r[3], **(r[4] if len(r) > 4 else {}))
                                             for r in rows])
    if bg: s["img"] = img(bg)
    if note: s["note"] = note
    if source: s["source"] = source
    s.update(kw)
    return s


def big(value, kicker, note="", bg=None, source=None, **kw):
    return stat(value, kicker, note, bg=bg, source=source, **kw)


def ledger(title, rows, bg="shabbat_02_7", total=None, **kw):
    """a calm list: rows of (label, value, at[, color])"""
    items = []
    for r in rows:
        it = dict(label=r[0], value=r[1], at=r[2])
        if len(r) > 3 and r[3]: it["color"] = r[3]
        items.append(it)
    s = dict(type="ledgerlist", title=title, items=items, img=img(bg), dim=0.84, gap=84, y0=260)
    if total: s["total"] = total
    s.update(kw)
    return s


def board(items, bg="paper", **kw):
    """a calm paper tabletop - everything fades or slides in gently"""
    for it in items:
        it.setdefault("from", "fade")
    return collage(items, bg=bg, z1=1.03, vignette=0.35, **kw)


def prop(name, x, y, h, at=0.1, rot=0.0, **kw):
    return dict(k="cut", img=cutout(name, red=False, keyline=0), x=x, y=y, h=h, at=at, rot=rot, **kw)


ENV = "prop_envelope.png"

# the street's own institutions - the recurring counterpart to the envelope
STREET = [
    ("Hatzalah", "volunteer ambulances"),
    ("Shomrim · Shmira", "neighbourhood patrols"),
    ("Chaveirim", "roadside help"),
    ("Beth Din", "a religious court"),
    ("Hebrew Free Loan Society", "loans at 0 % interest"),
    ("Bonei Olam", "fertility treatment fund"),
    ("Yeshivas", "its own schools"),
]


def street_list(n, new_at=0.6, step=0.0, title="What the street runs itself", **kw):
    rows = []
    for i, (a, b) in enumerate(STREET[:n]):
        at_ = new_at + i * step if step else (-3 if i < n - 1 else new_at)
        rows.append((a, b, at_, ACC if i == n - 1 and not step else None))
    return ledger(title, rows, bg="institutions_00_21", **kw)


# =================================================================== cold open: the envelope
at(0.0, board([
    prop(ENV, 940, 540, 470, at=0.3, rot=-3),
    prop("prop_list.png", 1650, 480, 500, at="@a shopping list written in Yiddish", rot=4),
    prop("prop_notice.png", 260, 500, 540, at="@a stack of school notices", rot=-6),
    strip("Kiryas Joel, New York", 900, 930, at="@Kiryas Joel", size=38, type=False)],
    overlays=[dict(type="fadein", d=1.2)]))
at("Eleven people live in this house", big("11", "PEOPLE IN THIS HOUSE", "one household, one envelope", bg="women_00_20",
                                           countFor=1.2))
at("That envelope decides whether the grocery money", ph("money_00_51", move="in", zoom=1.1))
at("Now step outside onto the same street", place(cl(155), "Kiryas Joel, New York", "the same street", at=0.5))
at("A volunteer ambulance is parked at the corner", cl(509))
at("An office that lends money at no interest", ph("named_00_2", move="left"))
at("A private school system runs to its own timetable", ph("children_00_52", move="in"))
at("Almost everyone who hears the question", cl(221))
at("A switch in an office somewhere", card(("A switch in an office somewhere.", 0.1), ("Someone flips it.", "@Someone flips it"),
                                           ("The money stops.", "@The money for this community stops", ACC, 84),
                                           bg="money_01_43"))
at("And everything you just saw on that street", cl(245))

at("The number attached to this argument", big("$100,000", "A YEAR — THE CLAIM", "combined benefits and tax credits, per large family",
                                                 bg="p_00_1", countFor=1.6))
at("The claim, repeated in the biggest documentaries", cl(465, then=(466,)))
at("Say that with the attribution it actually deserves", ledger("The $100,000 figure is…", [
        ("Asserted in source reporting", "yes", "@It is a figure asserted"),
        ("Repeated in documentary commentary", "yes", "@in documentary commentary"),
        ("A verified official payment to any household", "no", "@It is not a verified", RUST),
        ("Published by any agency", "no", "@no agency has published", RUST)], bg="money_00_8"))
at("Now the reversal", cl(56))
at("You would expect a community argued about", cl(148, then=(210,)))
at("It is not shrinking", card(("It is not shrinking.", 0.2, ACC, 96), bg="named_03_5"))
at("There are roughly a hundred thousand or more", dict(type="map", detail="geo_hi.json", adminCountries=["USA"], stops=[
        dict(at=0, lon=-74.4, lat=41.0, scale=11000), dict(at=1.0, lon=-74.1, lat=40.95, scale=15000, d=3.0)],
    highlight=[dict(id=NY_STATE, at=0.3), dict(id=NJ_STATE, at=0.6, fill="rgba(243,238,228,.08)")],
    pins=[dict(lon=WILLIAMSBURG[0], lat=WILLIAMSBURG[1], label="Williamsburg · Borough Park", at=0.8, side="right", size=30),
          dict(lon=MONSEY[0], lat=MONSEY[1], label="Monsey · New Square", at=1.6, side="right", size=30),
          dict(lon=KJ[0], lat=KJ[1], label="Kiryas Joel", at=2.0, side="left", size=30)],
    overlays=[dict(type="caption", text="≈ 100,000+ Hasidic Jews in the greater New York area", at=2.6)]))
at("and the population nearly doubles about every twenty years", bars("A population that doubles about every 20 years", [
        ("Today", 1, "×1", 0.3),
        ("+20 years", 2, "×2", 0.9),
        ("+40 years", 4, "×4", 1.5, dict(color=ACC))],
    bg="street_01_33", max=4.2, note="illustrative: what “nearly doubles every twenty years” compounds to"))
at("Kiryas Joel is the youngest municipality", place(ph("maps_00_40", move="in", zoom=1.1), "Kiryas Joel, New York",
                                                     "youngest municipality in the U.S. by median age", at=0.5))
at("In the 2010 census, 91.5 percent", big("91.5 %", "SPOKE YIDDISH AT HOME", "Kiryas Joel · 2010 census", bg="signage_00_52",
                                            source="Source: U.S. Census, 2010", countFor=1.6))

at("Now think about the last time you took public money", cl(213))
at("Not a handout. A tax credit", card(("Not a handout.", 0.1), ("A tax credit.", "@A tax credit", ACC, 90),
                                       bg="money_01_48"))
at("If you have ever claimed a federal tax credit", board([
    pc("money_01_43", 560, 520, 700, rot=-2, at=0.1, grade="none"),
    prop(ENV, 1360, 560, 470, at="@sitting inside that brown envelope", rot=3),
    strip("a federal tax credit", 560, 930, at="@a federal tax credit", size=36, type=False),
    strip("the same machinery", 1360, 930, at="@the same machinery", size=36, type=False)]))
at("You did not think of yourself as a recipient", card(("Not a recipient.", 0.1),
                                                        ("A taxpayer getting something back.", "@You thought of yourself as a taxpayer", ACC),
                                                        bg="money_00_13"))
at("The difference between you and the household", cl(157))
at("The difference is how many people", card(("How many people it is applied to —", 0.2),
                                             ("and whether anyone wrote an article about it.", "@and whether anybody thought", ACC, 52),
                                             bg="street_02_43"))

at("So here is the question this video answers", dict(type="doctitle", kicker="A documentary",
                                                     title="What Happens If the Benefits Are Cut?", img=img("maps_00_41"),
                                                     move="in", zoom=1.08))
at("And who, exactly, would be doing the cutting", card(("And who, exactly,", 0.1),
                                                        ("would be doing the cutting?", "@would be doing the cutting", ACC, 84),
                                                        bg="street_01_26"))

# =================================================================== 1: there is no switch
at("Now, here is where it gets genuinely interesting", heading(1, "There Is No Switch", "money_01_7"))
at("You are almost certainly wrong about the answer", cl(367))
at("There is no switch", card(("There is no switch.", 0.1, ACC, 100), bg="street_03_14"))
at("Means tested public benefits in the United States", card(("Not granted to communities.", 0.4),
                                                             ("Granted to households — one at a time.", "@They are granted to households", ACC),
                                                             bg="exterior_building_01_21"))
at("under programme rules set by statute", ph("street_03_21"))
at("Food assistance. Medicaid", board([
    pc("money_00_4", 330, 470, 460, rot=-3, at=0.0, grade="none"),
    pc("money_01_36", 790, 520, 460, rot=2, at="@Medicaid", grade="none"),
    pc("money_02_38", 1250, 470, 460, rot=-1.5, at="@Housing vouchers", grade="none"),
    pc("money_01_48", 1650, 540, 420, rot=2.5, at="@Federal tax credits", grade="none"),
    strip("food assistance", 330, 830, at=0.2, size=32, type=False),
    strip("Medicaid", 790, 860, at="@Medicaid", size=32, type=False),
    strip("housing vouchers", 1250, 830, at="@Housing vouchers", size=32, type=False),
    strip("federal tax credits", 1650, 860, at="@Federal tax credits", size=32, type=False)]))
at("Read those rules and you will not find", ledger("What the rules ask a household", [
        ("Income", "asked", 0.4),
        ("Household size", "asked", 0.9),
        ("Religion", "never asked", "@according to a household's religion", RUST),
        ("Which community you belong to", "never asked", "@which community you belong to", RUST)], bg="money_01_20"))
at("And a government in the United States cannot lawfully", ph("street_00_47", move="in"))
at("So the question as it is usually asked", cl(227))
at("Not a difficult mechanism", card(("Not a difficult mechanism.", 0.1), ("No mechanism at all.", "@No mechanism at all", ACC, 90),
                                     bg="street_01_17"))

# =================================================================== 2: a different lever
at("What does exist is a different lever", heading(2, "A Different Lever", "children_00_23", sub="not the grocery money"))
at("It is the money attached to the schools", cl(444))
at("That lever is real", card(("That lever is real.", 0.1), ("It has already been pulled.", "@It has already been pulled", ACC),
                              bg="children_01_11"))
at("And it explains why the answer this community has given", cl(146))
at("Build the institution yourself", card(("Build the institution yourself —", 0.1),
                                          ("so the state has nothing to switch off.", "@so the state has nothing", ACC),
                                          bg="institutions_00_41"))
at("Hold on to that", cl(137))
at("Once you see that the load bearing structure", board([
    prop(ENV, 470, 600, 330, at=0.1, rot=-4),
    strip("not the envelope", 470, 860, at="@is not the envelope", size=34, type=False),
    pc("institutions_01_30", 1080, 470, 480, rot=2, at="@the load bearing structure", grade="none"),
    pc("children_00_10", 1560, 560, 460, rot=-2, at="@on that street", grade="none"),
    strip("the load-bearing structure", 1320, 900, at="@the load bearing structure", size=36, type=False)]))
at("It stops being what happens if the money stops", card(("Not: what happens if the money stops?", 0.1),
                                                          ("But: what was the money ever holding up?", "@It becomes what the money", ACC),
                                                          bg="street_02_52"))
at("If you’re enjoying this investigation", cl(57, then=(238,)))

# =================================================================== 3: how the envelope is filled
at("Start with how the envelope is actually filled", heading(3, "How the Envelope Is Filled", "money_01_28"))
at("An eligibility worker does not assess a community", cl(517))
at("and they assess it against two figures", ledger("Two figures", [
        ("What comes in", "income", "@what comes in"),
        ("How many people it has to cover", "household size", "@how many people it has to cover", ACC)],
    bg="exterior_building_00_29"))
at("That second figure is the part the argument almost always skips", cl(140))
at("A house of eleven and a house of three", dict(type="sizechart", title="Same income: a house of three, a house of eleven",
    note="the same income, measured against household size (illustrative)", income=3.3, incomeLabel="the same income",
    barLabel="what the formula allows, by household size", sizes=[3, 11], at=0.4, per=0.8, incomeAt=0.2,
    img=img("money_00_8"), source="Illustrative: eligibility and amounts are set per household size"))
at("because household size is written into the formula", card(("Household size", 0.1),
                                                              ("is written into the formula.", "@is written into the formula", ACC, 80),
                                                              bg="money_00_31"))
at("So when a very large family appears in a news story", ph("women_00_16", move="in"))
at("you are looking at arithmetic", cl(374))
at("The same formula applied to the same statute", dict(type="map", detail="geo_hi.json", adminCountries=["USA"], stops=[
        dict(at=0, lon=-96, lat=38.5, scale=1150), dict(at=0.2, lon=-96, lat=38.5, scale=1450, d=3.0)],
    dots=[dict(lon=-122.3, lat=47.6, at="@for any household that size", label=""),
          dict(lon=-104.9, lat=39.7, at="@at that income", label=""),
          dict(lon=-97.3, lat=37.7, at="@anywhere in the country", label=""),
          dict(lon=-90.2, lat=38.6, at="@anywhere in the country", label=""),
          dict(lon=-84.4, lat=33.7, at="@of any religion", label=""),
          dict(lon=-87.6, lat=41.9, at="@of any religion", label=""),
          dict(lon=-111.9, lat=33.4, at="@or none", label=""),
          dict(lon=KJ[0], lat=KJ[1], at=0.4, label="Kiryas Joel")],
    overlays=[dict(type="caption", text="same household size + same income = the same result", at="@anywhere in the country")]))

at("Which means a real cut has to take a different form", cl(231))
at("It has to be a change to a programme rule", card(("A real cut is", 0.1), ("a change to a programme rule.", "@a change to a programme rule", ACC, 80),
                                                     bg="money_01_33"))
at("Lower a threshold", ledger("What a real cut looks like", [
        ("Lower a threshold", "", 0.1),
        ("Tighten a test", "", "@Tighten a test"),
        ("Cap a credit", "", "@Cap a credit"),
        ("Change how household size is counted", "", "@Change how household size", ACC)], bg="money_01_43"))
at("Do any of that and it applies to every household", ph("exterior_building_00_43", move="in"))
at("A household of two in a town you have never visited", dict(type="map", detail="geo_hi.json", adminCountries=["USA"], stops=[
        dict(at=0, lon=-88, lat=40, scale=1700), dict(at="@A household of eleven", lon=-80, lat=41, scale=2600, d=2.2)],
    pins=[dict(lon=-93.1, lat=41.6, label="a household of two", sub="a town you've never visited", at=0.8, side="left", size=30),
          dict(lon=KJ[0], lat=KJ[1], label="a household of eleven", sub="Kiryas Joel", at="@A household of eleven", side="right", size=30)]))
at("The rule reaches both or it reaches neither", card(("The rule reaches both —", 0.1), ("or it reaches neither.", "@or it reaches neither", ACC, 84),
                                                       bg="street_00_24"))
at("So there is no policy that cuts this community", cl(369))
at("There is only policy that cuts everybody", bars("One rule change, two households (illustrative)", [
        ("A household of two", 2, "smaller cut", 0.4),
        ("A household of eleven", 11, "larger cut", "@happens to reach these houses harder", dict(color=ACC))],
    bg="exterior_building_01_12", max=12, note="household size sits inside the formula"))
at("because families of ten or more children are common here", cl(472))

at("Which brings us back to the hundred thousand dollars", big("$100,000", "BACK TO THE CLAIM", "what kind of figure is it?",
                                                               bg="money_02_21", count=False))
at("Reporting on this community's economics has drawn on", board([
    pc("men_study_01_40", 420, 480, 560, rot=-2, at=0.1, grade="none"),
    pc("money_01_36", 960, 540, 560, rot=1.5, at="@United States Census figures", grade="none"),
    pc("signage_00_11", 1500, 480, 560, rot=-1, at="@The New York Times", grade="none"),
    strip("the YAFFED report, 2018–2022", 420, 860, at="@the YAFFED report", size=32, type=False),
    strip("U.S. Census figures", 960, 900, at="@United States Census figures", size=32, type=False),
    strip("The New York Times", 1500, 860, at="@The New York Times", size=32, type=False)]))
at("That is where the figure lives", ph("men_study_00_41", move="in"))
at("It is a combined total, assembled across several programmes", ledger("Inside the envelope", [
        ("Food assistance", "+", 0.3), ("Medicaid", "+", 0.6), ("Housing support", "+", 0.9), ("Tax credits", "+", 1.2)],
    total=dict(label="What a large household could receive", value="≈ $100,000", at="@describing what a large household"),
    bg="money_02_34"))
at("How that total is put together is a whole subject", ph("money_01_25", move="in"))
at("What matters right here is only this", card(("Every part of it: a household-level determination.", "@Every component of it", None, 52),
                                                ("Not one addressed to a community.", "@not one of them is addressed", ACC, 60),
                                                bg="exterior_building_01_24"))

at("And the household is not sitting still", cl(188))
at("Women are the community's primary paid workforce", cl(386))
at("That single sentence overturns most", card(("Women are the community's", 0.1),
                                               ("primary paid workforce.", 0.4, ACC, 84), bg="street_02_7"))
at("The wages arriving in these houses", cl(60))
at("and family businesses carry much of the rest", cl(500))
at("So a home on that street usually has income", ledger("The household, counted properly", [
        ("Mothers' wages", "rarely counted", "@has income the argument rarely counts", ACC),
        ("Family businesses", "rarely counted", "@rarely counts"),
        ("Public support", "often counted twice", "@count twice", RUST)], bg="women_00_32"))
at("If the envelope stopped coming tomorrow", board([
    prop(ENV, 960, 520, 560, at=0.1, rot=2),
    strip("not into a vacuum", 960, 900, at="@it would not be stopping into a vacuum", size=40, type=False)]))
at("It would be stopping into a house that already has earners", cl(372))
at("on a street that already runs services", cl(138))

# =================================================================== 4: substantially equivalent
at("Now, here is the part that actually decides this question", heading(4, "Substantially Equivalent", "children_00_9",
                                                                        sub="the part that decides it"))
at("New York State law requires that non public schools", dict(type="map", detail="geo_hi.json", adminCountries=["USA"], stops=[
        dict(at=0, lon=-75.8, lat=42.7, scale=4200)],
    highlight=[dict(id=NY_STATE, at=0.3)],
    names=[dict(text="New York State", lon=-75.6, lat=42.9, at=0.6, size=46)],
    overlays=[dict(type="caption", text="non-public schools must give instruction “substantially equivalent” to local public schools",
                   at="@substantially equivalent")]))
at("That is the standard", card(("“Substantially equivalent.”", 0.1, ACC, 90), ("That is the standard.", 0.9), bg="children_00_6"))
at("It is not a funding rule dressed up", card(("Not a funding rule.", 0.1),
                                               ("An education rule — with funding attached.", "@It is an education rule with funding", ACC),
                                               bg="children_02_0"))
at("and attached is the word that matters", cl(306, then=(426,)))
at("State and city reviews of Hasidic yeshivas", board([
    pc("named_01_23", 560, 500, 700, rot=-2, at=0.1, grade="none"),
    title_("State and city reviews", 1360, 330, at=0.4, size=62),
    strip("some Hasidic yeshivas", 1360, 480, at="@found that some of them", size=36, type=False),
    strip("did not meet the standard", 1360, 580, at="@did not meet", size=36, type=False)]))
at("Boys in strict Hasidic yeshivas typically study", big("7:30 am – 9:30 pm", "A TYPICAL DAY · STRICT HASIDIC YESHIVAS",
                                                          "ten or more hours a day · little secular education",
                                                          bg="children_01_22", count=False, size=150))
at("ten or more hours a day", cl(310))
at("Those two sentences are the entire dispute", ph("men_study_01_29", move="in"))

at("And notice where that lever actually touches", cl(392))
at("It does not touch the grocery money", card(("Not the grocery money.", 0.1), ("The classroom.", "@It touches the classroom", ACC, 96),
                                               bg="children_00_25"))
at("Funding attached to a school is withheld", spot("p_01_41", center=[0.5, 0.55], radius=[0.32, 0.34],
                                                    label="through a child's desk", hit=0.9, zoom=1.08, side="left"))
at("That is the whole reason this is the live fight", cl(312))
at("One of them has a mechanism written into law", ledger("Two arguments", [
        ("Schools: a named standard", "✓", "@with a named standard"),
        ("Schools: a review process", "✓", "@a review process"),
        ("Schools: a remedy at the end", "✓", "@a remedy at the end"),
        ("Benefits: a number in a newspaper", "nothing behind it", "@The other has a number", RUST)], bg="men_study_00_37"))

at("So what happened when the lever was pulled", cl(111, then=(89,)))
at("The reviews were carried out", board([
    pc("children_00_35", 620, 520, 740, rot=-1.5, at=0.1, grade="none"),
    strip("the reviews were carried out", 1340, 420, at=0.2, size=36, type=False),
    strip("the findings landed", 1340, 540, at="@The findings landed", size=36, type=False)]))
at("The argument went into years of hearings", card(("Hearings. Objections.", 0.2), ("Revisions. Litigation.", "@revisions and litigation"),
                                                    ("Not settled.", "@it is not settled now", ACC, 84), bg="institutions_01_1"))
at("Nobody has finally ruled", cl(408))
at("What the community did instead was organise", cl(388))
at("It argued the case in public", cl(412))
at("And it kept the school day exactly as it was", cl(457))
at("That response tells you something the figures never will", ph("men_study_00_50", move="in"))
at("Pressure applied to the money produced a defence", card(("Pressure on the money", 0.1), ("produced a defence of the institution —", 0.8),
                                                            ("not a modification of it.", "@not a modification of it", ACC),
                                                            bg="men_study_00_49"))

# =================================================================== 5: what the street runs itself
at("Look again at that street", heading(5, "What the Street Runs Itself", "institutions_00_13"))
at("The community runs Hatzalah", who(cl(139), "Hatzalah", "volunteer ambulance service", at=0.4))
at("It runs Shomrim and Shmira patrols", who(cl(324), "Shomrim · Shmira", "neighbourhood patrols", at=0.3))
at("It runs Chaveirim for roadside help", who(cl(107), "Chaveirim", "volunteer roadside help", at=0.3))
at("It runs a Beth Din, a religious court", who(ph("institutions_01_7", move="in"), "Beth Din", "a religious court", at=0.3))
at("Not one of those is a state service", card(("Not one of those", 0.1), ("is a state service.", 0.5, ACC, 84), bg="institutions_01_14"))
at("The Hebrew Free Loan Society lends money", board([
    pc("money_02_11", 600, 540, 700, rot=-2, at=0.1, grade="none"),
    title_("Hebrew Free Loan Society", 1330, 380, at=0.3, size=56),
    strip("loans at no interest", 1330, 530, at="@lends money at no interest", size=38, type=False)]))
at("Charity funds cover specific needs", who(cl(382), "Bonei Olam", "charity fund for fertility treatment",
                                             at="@among them Bonei Olam"))
at("This community operates its own schools", street_list(7, new_at=0.2, step=0.45))
at("Add that up", cl(136, then=(442,)))
at("Ambulances. Courts. Loans. Schools", board([
    pc("institutions_00_9", 330, 500, 460, rot=-2, at=0.0, grade="none"),
    pc("institutions_01_15", 790, 540, 460, rot=1.5, at="@Courts", grade="none"),
    pc("money_02_47", 1250, 500, 460, rot=-1.5, at="@Loans", grade="none"),
    pc("children_00_1", 1650, 550, 420, rot=2, at="@Schools", grade="none"),
    strip("ambulances", 330, 850, at=0.2, size=34, type=False),
    strip("courts", 790, 880, at="@Courts", size=34, type=False),
    strip("loans", 1250, 850, at="@Loans", size=34, type=False),
    strip("schools", 1650, 880, at="@Schools", size=34, type=False)]))
at("The things most exposed to a funding decision", card(("Most exposed to a funding decision —", 0.1),
                                                         ("here, furthest from one.", "@the things furthest from one", ACC, 80),
                                                         bg="institutions_00_22"))

# =================================================================== 6: who absorbs a cut
at("Which gives us the honest answer", heading(6, "Who Absorbs a Cut", "women_00_14", sub="the honest answer"))
at("If public support to these households were reduced", ledger("Who absorbs a cut first?", [
        ("Hatzalah", "not first", "@would not be Hatzalah"),
        ("The Beth Din", "not first", "@It would not be the Beth Din"),
        ("The school day", "not first", "@It would not be the school day")], bg="institutions_00_21"))
at("Those get defended first", ph("historical_00_42", move="in"))
at("The absorption would happen inside the houses", ledger("Who absorbs a cut first?", [
        ("Hatzalah", "not first", -3), ("The Beth Din", "not first", -3), ("The school day", "not first", -3),
        ("The households", "first", 0.4, ACC)], bg="institutions_00_21"))
at("It would land on the mothers already carrying", cl(59))
at("It would land on the children in a home of eleven", cl(480))
at("where a reduction per person looks small", bars("A small cut, per person (illustrative)", [
        ("One person", 20, "− $20 a month", 0.3),
        ("A home of eleven", 220, "− $220 a month", "@looks very different on a table", dict(color=ACC))],
    bg="shabbat_00_23", max=240, note="illustrative figures: small per person, large per table"))
at("That is the part both sides of this argument walk past", cl(481))
at("The institutions are the strong points", card(("The institutions are the strong points.", 0.1),
                                                  ("The people are the soft ones.", "@The people are the soft ones", ACC),
                                                  bg="children_02_34"))
at("A cut aimed at a system is absorbed by a family", spot("women_00_16", center=[0.5, 0.55], radius=[0.34, 0.4],
                                                           label="absorbed by a family", hit=0.8, zoom=1.08, side="left"))

at("And that order of priority is the real finding here", cl(200))
at("Decades of pressure, and the pattern never varies", ph("historical_01_9", move="in"))
at("Income is negotiable", card(("Income is negotiable.", 0.1), ("Institutions are not.", "@Institutions are not", ACC, 96),
                                bg="named_02_3"))
at("A community that will accept being poorer", ph("children_02_31", move="in"))
at("Whether you find that admirable or indefensible", card(("Admirable, or indefensible?", 0.1),
                                                           ("It depends on what you believe a childhood is for.", "@what you believe a childhood is for", ACC, 52),
                                                           bg="children_01_49"))
at("But it is not a mystery", cl(223, then=(21, 391)))
at("The reason a cut does not produce the collapse", board([
    prop(ENV, 900, 520, 520, at=0.1, rot=-2),
    strip("never carrying the weight", 900, 890, at="@was never carrying the weight", size=40, type=False)]))

# =================================================================== 7: the case against
at("Now the steel man", heading(7, "The Case Against", "children_02_0", sub="put properly"))
at("Critics, including taxpayers and public officials", ph("exterior_building_00_12", move="in"))
at("argue that public money should not support", card(("“Public money should not support a system", 0.1),
                                                      ("that leaves children without a secular education.”", 0.7, ACC, 54),
                                                      bg="children_02_6"))
at("That is not a bigoted position", card(("Not a bigoted position.", 0.1),
                                          ("A claim about children — not a complaint about adults.", "@It rests on a claim about children", ACC, 52),
                                          bg="children_01_43"))
at("The argument runs like this", cl(30))
at("A benefit paid to a household is paid because", ph("children_00_53", move="in"))
at("If that same society also requires", ledger("Two obligations", [
        ("Children should not go without", "funded", 0.3, SAGE),
        ("Children taught to read and reason in the country's language", "unmet", "@then funding one obligation", RUST)],
    bg="children_01_13"))
at("It is the abandonment of a child", card(("The abandonment of a child", 0.1), ("in the name of respect.", "@in the name of respect", ACC, 84),
                                            bg="children_01_38"))
at("The people making that case say the education standard", ph("children_02_25", move="in"))
at("and on the plain text of the standard", card(("On the plain text of the standard,", 0.1), ("they are right.", "@they are right", ACC, 90),
                                                 bg="children_00_40"))
at("That is the strongest version of the case", cl(31, then=(27,)))

at("Then there is a second group", ph("street_01_1", move="in"))
at("Critics who grew up inside these communities and left", ph("named_00_54", move="in"))
at("Not impossible. Harder", card(("Not impossible.", 0.1), ("Harder.", "@Harder", ACC, 110), bg="street_00_27"))
at("Yiddish is the daily language of these communities", board([
    pc("signage_00_9", 560, 500, 640, rot=-2, at=0.1, grade="none"),
    pc("children_01_13", 1320, 540, 600, rot=2, at="@and English is for many boys", grade="none"),
    strip("Yiddish: the daily language", 560, 880, at=0.3, size=34, type=False),
    strip("English: a second language, learned late", 1320, 900, at="@a second language", size=34, type=False)]))
at("They describe losing not only a religion", card(("Not only a religion —", 0.1), ("a language, a neighbourhood,", "@but a language"),
                                                    ("a whole set of shared references.", "@an entire set of shared references", ACC),
                                                    bg="street_02_5"))
at("When they say the schooling was the wall", cl(336, then=(235,)))
at("And notice what that does to the argument", cl(239, then=(241,)))
at("It becomes a question about whether the way out", card(("A door —", 0.1),
                                                           ("or a wall with a handle painted on it?", "@or a wall with a handle", ACC, 70),
                                                           bg="women_00_0"))

at("So concede what is true", cl(14))
at("The standard is lawful", ledger("Concede what is true", [
        ("The standard", "lawful", 0.1),
        ("The findings", "real", "@The findings were real"),
        ("The concern for the children", "the serious version", "@The concern about the children", ACC),
        ("Answered by pointing at ambulances?", "no", "@it has not been answered", RUST)], bg="children_02_53"))
at("What the community's own conduct has established", cl(33))
at("It has established that money is not the pressure point", card(("Money is not the pressure point.", 0.1, ACC),
                                                                   ("That is all it has established.", "@That is all it has established"),
                                                                   bg="money_02_34"))
at("It has not made the education question go away", ph("children_01_33", move="in"))

# =================================================================== the viewer's own envelope
at("And yet. Turn the question around", dict(type="doctitle", kicker="And yet", title="Your Envelope",
                                             img=img("exterior_building_00_55"), move="in", zoom=1.08))
at("Public money runs through your life too", board([
    prop(ENV, 700, 540, 500, at=0.1, rot=-3),
    strip("your tax credit", 700, 880, at="@inside the tax credit you claimed", size=38, type=False),
    prop("vintage_open_book.png", 1430, 540, 440, at="@It paid for the classroom"),
    strip("your classroom", 1430, 880, at="@It paid for the classroom", size=38, type=False)]))
at("where somebody taught you to read", ph("historical_00_52", move="in"))
at("So imagine a proposal to reduce it", cl(358, then=(368,)))
at("What would you give up first", card(("What would you give up first?", 0.1, ACC, 84), bg="shabbat_00_29"))
at("Most people answer that question exactly the way", cl(460))
at("You would take the smaller cheque", card(("You would take the smaller cheque.", 0.1),
                                             ("You would not take the different childhood.", "@You would not take the different childhood", ACC, 60),
                                             bg="shabbat_01_37"))
at("The brown envelope on that kitchen table", board([
    prop(ENV, 940, 540, 470, at=0.1, rot=-3),
    prop("prop_list.png", 1650, 480, 500, at=0.4, rot=4),
    prop("prop_notice.png", 260, 500, 540, at=0.4, rot=-6),
    strip("not what holds that street together", 900, 930, at="@is not what holds that street together", size=38, type=False)]))
at("It would only confirm what the people living there", place(ph("maps_00_35", move="in"), "Kiryas Joel, New York", at=0.6))
at("The more useful question is what a similar envelope", card(("What would a similar envelope —", 0.1),
                                                               ("and a similar threat —", "@and a similar threat"),
                                                               ("reveal about yours?", "@would reveal about yours", ACC, 84),
                                                               bg="street_01_17", overlays=[dict(type="fadeout", d=2.4)]))

# music: calm beds only, in this video's shuffled order (a fresh opener first)
CALM = ["02_Leaving_Home_Somber_Long_Bed.mp3", "03_Sovereign_Dark_Piano_Bed.mp3", "04_Sad_Trio_Somber_Piano_Cello.mp3",
        "11_Unanswered_Questions_Mystery.mp3", "12_Magic_Forest_Dark_Cello.mp3", "Mark Jubel - Efteraar.mp3",
        "Silent Tension Piano.mp3", "Slow Dramatic Ascent.mp3", "06_SCP-x6x_Hopes_Mysterious.mp3", "01_Metaphysik_Dramatic_Strings_Bed.mp3"]
BEDS = [t for t in V["music"] if t in CALM]
ACTS = [None, "Now, here is where it gets genuinely interesting", "Start with how the envelope is actually filled",
        "Now, here is the part that actually decides this question", "Look again at that street",
        "Which gives us the honest answer", "Now the steel man", "And yet. Turn the question around"]
edl.main(music=[dict(at=a, track=BEDS[i % len(BEDS)], db=0 if i else -1, lead=-1.0 if i else 0) for i, a in enumerate(ACTS)])
