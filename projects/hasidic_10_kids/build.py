"""
How Do Hasidic Jews Afford 10 Kids Without Jobs
Faceless documentary - edit decision list and build.

Look: "documentary" theme - calm, classic long-form documentary. Slow camera moves over
real photographs, soft dissolves between every shot, serif chapter headings, a location
caption with a thin gold rule, gentle charts. No stamps, slams or whooshes; the sound design
is only paper, pen and soft ticks, and the music sits far under the narrator.

The recurring device is THE LEDGER: a household ledger that gains one layer per chapter -
earned income, benefits scaled to household size, low-cost schooling, interest-free credit,
charity, dense housing - until the last line, which is not money at all.

About 30 % footage clips, 70 % photographs and calm graphics.

    python build.py plan | prep | stills [ids] | render [ids] | mix | final | all
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "docu"))

import edl                       # noqa: E402
from edl import *                # noqa: E402,F401,F403  (the shot helpers)

SP = os.environ.get("NOAH_ROOT", "/tmp/claude-0/-home-user-celeb/945fe076-994f-5d04-8c9c-fa77e8ef4232/scratchpad")
H5 = f"{SP}/hasidic"
edl.setup(
    name="How_Do_Hasidic_Jews_Afford_10_Kids",
    kit=os.environ.get("NOAH_KIT", f"{SP}/kit"),
    footage=os.environ.get("HASIDIC_FOOTAGE", f"{H5}/footage"),
    work=os.environ.get("NOAH_WORK", f"{SP}/work5"),
    data=os.path.join(HERE, "data"),
    out=os.environ.get("NOAH_OUT", f"{SP}/out"),
    image_dirs=[f"{H5}/picks", f"{H5}/src/images"],
    theme="documentary", grade="doc", grain=1.5,
    music_floor_db=-21.0, music_duck_db=-10.0, sfx_gain=0.55,
    xfade=0.6, sfx_style="calm",
)

GOLD, RUST, SAGE, CREAM = "#D8B26E", "#B5523B", "#8DAA7B", "#F3EEE4"
NYC = (-74.006, 40.713)
KJ = (-74.168, 41.340)
NEW_SQUARE = (-74.029, 41.139)
WILLIAMSBURG = (-73.957, 40.708)
LAKEWOOD = (-74.217, 40.096)
ISRAEL = (34.9, 31.6)
NY_STATE, NJ_STATE = "USA-3559", "USA-3558"


# ---------------------------------------------------------------- calm building blocks

def ph(name, move="in", zoom=1.08, focus=None, **kw):
    """a photograph with a slow move (the documentary default)"""
    return photo(name, move=move, zoom=zoom, focus=focus, **kw)


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
    s = dict(type="doctitle", kicker=f"Chapter {n}", title=title, img=img(bg), move="in", zoom=1.08)
    if sub: s["sub"] = sub
    s.update(kw)
    return s


def card(*lines, bg=None, dim=0.62, **kw):
    """one to three lines of text over a darkened photo; each line: text or (text, at, color, size)"""
    ls = []
    for i, ln in enumerate(lines):
        if isinstance(ln, str):
            ls.append(dict(text=ln))
        else:
            d = dict(text=ln[0])
            if len(ln) > 1 and ln[1] is not None: d["at"] = ln[1]
            if len(ln) > 2 and ln[2]: d["color"] = ln[2]
            if len(ln) > 3 and ln[3]: d["size"] = ln[3]
            ls.append(d)
    s = dict(type="textcard", lines=ls, dim=dim)
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


# the recurring ledger: seven layers, filled one chapter at a time
LAYERS = [
    ("1  Earned income", "modest"),
    ("2  Benefits scaled to household size", "per person"),
    ("3  Yeshiva schooling", "a fraction of market cost"),
    ("4  Gemach: interest-free credit", "0 % interest"),
    ("5  Tzedakah: community charity", "built in"),
    ("6  Dense, shared housing", "cost per person, down"),
    ("7  Children as the purpose", "not an expense"),
]


def ledger(n_shown, new_at=0.9, title="The household ledger", total=None, **kw):
    """the ledger with the first n_shown layers; the newest one writes itself in at new_at"""
    items = []
    for i, (lab, val) in enumerate(LAYERS[:n_shown]):
        it = dict(label=lab, value=val, at=(-3 if i < n_shown - 1 else new_at))
        if i == n_shown - 1:
            it["color"] = GOLD
        items.append(it)
    s = dict(type="ledgerlist", title=title, items=items, img=img("shabbat_02_30"), dim=0.84, gap=80, y0=250)
    if total:
        s["total"] = total
    s.update(kw)
    return s


def board(items, bg="paper", **kw):
    """a calm paper tabletop (Vox style, but everything fades or slides in gently)"""
    for it in items:
        it.setdefault("from", "fade")
    return collage(items, bg=bg, z1=1.03, vignette=0.35, **kw)


# =================================================================== cold open
at(0.0, place(ph("maps_00_9", move="in", zoom=1.12, focus=[0.5, 0.55], overlays=[dict(type="fadein", d=1.2)]),
              "Orange County, New York", "about an hour north of New York City", at=1.2))
at("the median age is 15.7 years", big("15.7", "MEDIAN AGE", "in one village north of New York City", bg="children_00_45",
                                       countFor=1.8))
at("Not 35. Not 40.", card(("Not 35.", 0.1), ("Not 40.", "@Not 40"), ("Fifteen point seven.", "@Fifteen point seven", GOLD, 84),
                           bg="children_02_49"))
at("According to World Population Review", clip(38, zoom=1.03))
at("the village of Kiryas Joel", place(clip(29, zoom=1.03), "Kiryas Joel, New York", "Satmar Hasidic village", at=0.4))
at("which means half the people living there are children", clip(225, zoom=1.03, then=(150,)))
at("Now add the other numbers", ledger(0, title="Kiryas Joel, by the numbers", items=[
        dict(label="Median household income", value="≈ $50,000", at="@Median household income"),
        dict(label="Per capita income", value="$14,440", at="@Per capita income"),
        dict(label="Poverty rate", value="≈ 38 %", at="@Poverty rate", color=RUST)],
    source=None))
at("And these aren't households of two people", clip(485, grade="none", zoom=1.03))
at("families of eight, nine, ten children are completely normal", spot("children_02_18", center=[0.5, 0.55], radius=[0.36, 0.34],
                                                                       label="Eight, nine, ten children", hit=0.8, zoom=1.08))
at("So the question writes itself", clip(26, zoom=1.03))
at("how do Hasidic families afford ten kids", card(("How do they afford ten kids —", 0.2),
                                                   ("without jobs?", "@without jobs", GOLD, 84), bg="street_01_54"))
at("But here's what you'll learn", clip(199, zoom=1.03))
at("that question is half wrong", card(("That question is", 0.1), ("half wrong.", "@half wrong", GOLD, 96), bg="children_02_40"))
at("Because when you actually pull the data", board([
    pc("doc_00_19", 520, 520, 620, rot=-2, at=0.1, grade="none"),
    pc("money_00_12", 1100, 440, 520, rot=2.5, at="@university studies", grade="none"),
    pc("institutions_00_44", 1520, 640, 460, rot=-1.5, at="@federal court filings", grade="none"),
    strip("census records", 520, 900, at="@census records", size=36, type=False),
    strip("university studies", 1100, 800, at="@university studies", size=36, type=False),
    strip("federal court filings", 1520, 950, at="@federal court filings", size=36, type=False)]))
at("Not a community surviving without work", clip(205, zoom=1.03))
at("A system with its own rules", card(("Its own rules.", "@its own rules"), ("Its own banking.", "@its own banking"),
                                       ("Its own math.", "@its own math", GOLD), bg="street_01_3"))
at("And once you see how it works", clip(42, zoom=1.03))
at("Let's go inside the numbers", dict(type="title", img=img("street_00_2"), kicker="A DOCUMENTARY",
                                       title="TEN KIDS", subtitle="How Hasidic families make the math work", tagline=""))

# =================================================================== chapter 1: the numbers
at("Start with the facts", heading(1, "The Numbers", "exterior_building_00_53", sub="What makes people ask"))
at("Kiryas Joel — a village in Orange County", dict(type="map", detail="geo_hi.json", adminCountries=["USA"], stops=[
        dict(at=0, lon=-75.5, lat=41.2, scale=5200),
        dict(at="@a village in Orange County", lon=-74.1, lat=41.0, scale=17000, d=3.0)],
    highlight=[dict(id=NY_STATE, at=0.3), dict(id=NJ_STATE, at=0.6, fill="rgba(243,238,228,.08)")],
    names=[dict(text="New York", lon=-75.2, lat=42.2, at=0.6, size=40), dict(text="New Jersey", lon=-74.75, lat=40.3, at=0.9, size=34)],
    dots=[dict(lon=NYC[0], lat=NYC[1], label="New York City", at=1.2)],
    routes=[dict(**{"from": list(NYC)}, to=list(KJ), at="@home to the Satmar", d=1.8, dash=True, label="≈ 1 hour", lx=70, ly=0)],
    pins=[dict(lon=KJ[0], lat=KJ[1], label="Kiryas Joel", sub="Orange County", at="@a village in Orange County", side="left")]))
at("had about 33,000 residents at the 2020 census", big("33,000", "RESIDENTS · 2020 CENSUS", "and it has kept growing since",
                                                        bg="maps_01_1", countFor=1.6))
at("Census Reporter data shows", bars("Median household income", [
        ("Kiryas Joel", 50, "≈ $50,000", "@its median household income", dict(color=RUST)),
        ("Its metropolitan area", 98, "≈ $98,000", "@which sits near")],
    bg="maps_00_20", note="roughly half", source="Source: Census Reporter / U.S. Census Bureau", max=100))
at("Per capita income is about", big("$12,000–14,000", "PER CAPITA INCOME", "depending on the year measured", bg="street_00_29",
                                     count=False, size=170))
at("Then there's New Square", dict(type="map", detail="geo_hi.json", adminCountries=["USA"], stops=[
        dict(at=0, lon=-74.1, lat=41.0, scale=17000), dict(at=0.4, lon=-74.05, lat=41.15, scale=30000, d=2.4)],
    highlight=[dict(id=NY_STATE, at=0.0)],
    pins=[dict(lon=KJ[0], lat=KJ[1], label="Kiryas Joel", at=0.0, side="left", size=34),
          dict(lon=NEW_SQUARE[0], lat=NEW_SQUARE[1], label="New Square", sub="Rockland County", at="@another Hasidic village", side="right")]))
at("It is, by multiple measures", bars("New Square: poverty rate", [
        ("Wikipedia's census summary", 64.4, "64.4 %", "@puts its poverty rate", dict(color=RUST)),
        ("Study reported by The Center Square", 63.3, "63.3 %", "@found a poverty rate", dict(color=RUST))],
    bg="street_02_26", note="median household income: $23,578 (same study)", max=100,
    source="Sources: U.S. Census data via Wikipedia; The Center Square"))
at("In Williamsburg, Brooklyn", place(clip(201, zoom=1.03), "Williamsburg, Brooklyn", "one of the largest Hasidic communities in the world"))
at("WNYC reporting found", big("55 %", "HASIDIC HOUSEHOLDS BELOW THE POVERTY LINE", "nearly triple the rate of New York City as a whole",
                               bg="street_00_46", source="Source: WNYC reporting", countFor=1.4))
at("And a 2023 UJA-Federation study", big("1 in 3", "JEWISH HOUSEHOLDS IN THE REGION RECEIVE SOME ASSISTANCE",
                                          "subsidized health insurance is the most common", bg="money_01_30", count=False,
                                          source="Source: UJA-Federation of New York, 2023"))
at("And in Lakewood, New Jersey", dict(type="map", detail="geo_hi.json", adminCountries=["USA"], stops=[
        dict(at=0, lon=-74.05, lat=41.15, scale=30000), dict(at=0.3, lon=-74.2, lat=40.4, scale=16000, d=2.2)],
    highlight=[dict(id=NJ_STATE, at=0.2)],
    pins=[dict(lon=LAKEWOOD[0], lat=LAKEWOOD[1], label="Lakewood", sub="New Jersey", at=1.0, side="right")]))
at("65,000 people", big("65,000", "PEOPLE IN LAKEWOOD ON MEDICAID", "more than half the township · 2017", bg="money_02_43",
                        source="Source: Los Angeles Times, 2017", countFor=1.5))
at("So yes. The poverty numbers are real", card(("The poverty numbers are real.", 0.2), ("The benefits usage is real.", "@The benefits usage"),
                                                bg="money_00_39"))
at("Now here's the part almost nobody checks", ledger(0, title="The other half of the ledger", items=[
        dict(label="Money going out", value="?", at="@the other half")]))

# =================================================================== chapter 2: who works?
at("Ask yourself this", heading(2, "Who Brings Home the Money?", "p_01_53"))
at("The stereotype says the men don't work", clip(428, zoom=1.03))
at("And full-time Torah study is genuinely central", ph("men_study_00_47", move="in", zoom=1.1))
at("in Israel, a 2021 report", dict(type="map", stops=[
        dict(at=0, lon=-40, lat=38, scale=420), dict(at=0.2, lon=30, lat=33, scale=1400, d=2.6)],
    pins=[dict(lon=ISRAEL[0], lat=ISRAEL[1], label="Israel", sub="Israel Democracy Institute, 2021", at=2.2, side="right")]))
at("only 51 percent of ultra-Orthodox men", bars("Israel: ultra-Orthodox workforce participation", [
        ("Men", 51, "51 %", "@51 percent"),
        ("Women", 78, "≈ 78 %", "@roughly 78 percent", dict(color=SAGE))],
    bg="p_02_7", note="women's rate exceeds the national female average", max=100,
    source="Source: Israel Democracy Institute, 2021"))
at("But that's Israel. What about the United States", clip(203, zoom=1.03))
at("Here's where it gets interesting", board([
    pc("doc_00_2", 620, 520, 700, rot=-2, at=0.1, grade="none"),
    title_("2025 analysis", 1330, 340, at=0.4, size=78),
    strip("American Community Survey data", 1330, 480, at="@American Community Survey", size=34, type=False),
    strip("published by YAFFED", 1330, 580, at="@YAFFED", size=34, type=False),
    strip("Hasidic men: as likely, or slightly more likely, to work", 1100, 900, at="@marginally more likely", size=34, type=False)]))
at("Let that sink in", card(("In America, Hasidic men work —", 0.3), ("at rates comparable to similar men.", "@at rates comparable", GOLD),
                            bg="street_03_3"))
at("The difference isn't whether they work", card(("Not whether they work.", 0.2), ("What they earn.", "@It's what they earn", GOLD, 90),
                                                   bg="food_kosher_00_51"))
at("They run small businesses", clip(142, zoom=1.03, then=(501,)))
at("contracting crews, jewelry stores", clip(436, zoom=1.03, then=(438,)))
at("They work long hours for modest incomes", clip(499, zoom=1.03))
at("Many combine that with part-time study", clip(206, zoom=1.03))
at("The image of the man who never earns a dollar", depth("street_00_43", subject=[0.5, 0.5], hit=0.6, move="in"))
at("So if the men usually work", clip(432, zoom=1.03))
at("Two reasons", ledger(1, new_at="@One: large single-income", title="The household ledger"))
at("the system is designed so that it doesn't need much money", clip(228, zoom=1.03))
at("And that design starts with a form", board([
    pc("money_00_55", 700, 540, 800, rot=-1.5, at=0.2, grade="none"),
    dict(k="cut", img=cutout("vintage_hand writing.png", red=False), x=1400, y=620, h=520, at=0.8),
    strip("at the kitchen table", 1350, 250, at="@kitchen table", size=40, type=False)]))

# =================================================================== chapter 3: the form
at("Here is the single most misunderstood mechanic", heading(3, "A Form at the Kitchen Table", "money_01_13",
                                                             sub="the most misunderstood mechanic"))
at("Government benefit programs don't ask", card(("Not: what is your family worth?", 0.4),
                                                 ("But: income relative to household size.", "@They look at your household income", GOLD),
                                                 bg="money_00_17"))
at("And in America, the eligibility line moves", dict(type="sizechart", title="The same income, a bigger family",
    note="eligibility limits rise with every person in the household (illustrative)", income=4.1, incomeLabel="one fixed income",
    barLabel="eligibility limit, by household size", at=0.6, per=0.3, incomeAt="@with every child you add", img=img("money_02_13"),
    source="Illustrative: limits for programs like Medicaid and SNAP are set per household size"))
at("That means a family of twelve", dict(type="sizechart", title="A family of twelve vs. a family of three",
    note="same income, around $70,000 (illustrative)", income=4.1, incomeLabel="≈ $70,000", barLabel="eligibility limit",
    sizes=[3, 12], at=-5, per=0.0, incomeAt=0.5, img=img("money_02_13"),
    source="Illustrative comparison from the script's example"))
at("As one analysis of New Jersey's Orthodox communities", clip(62, zoom=1.03))
at("because eligibility for programs like Medicaid and SNAP", board([
    pc("money_01_30", 620, 480, 620, rot=-2, at=0.1, grade="none"),
    pc("money_00_18", 1300, 560, 620, rot=2, at="@and SNAP", grade="none"),
    strip("income-tested per household", 960, 930, at="@income-tested per household", size=40, type=False)]))
at("Now, notice what that means economically", clip(475, grade="none", zoom=1.03))
at("For a ten-child family, public programs aren't a lifestyle", card(
    ("Not a lifestyle.", 0.2), ("The health insurance. The food cushion. The housing support.", "@they're the health insurance", GOLD, 52),
    bg="children_02_54"))
at("The community isn't gaming this", card(("It's arithmetic.", "@It's arithmetic", GOLD, 96), bg="money_01_42"))
at("Add a child", clip(378, zoom=1.03))
at("And that leads to the second half of the equation", ledger(2, new_at=0.8))
at("It's about costs going out", clip(233, zoom=1.03))

# =================================================================== chapter 4: the cost side
at("Ask any middle-class American parent", heading(4, "The Cost Side", "children_00_7", sub="childcare and education"))
at("Here, that entire category is structurally different", clip(185, zoom=1.03, then=(186,)))
at("Hasidic children attend yeshivas", place(clip(258, zoom=1.03), "A yeshiva classroom", "private religious schools run by the community"))
at("And those schools price nothing like", clip(44, zoom=1.03))
at("Surveys on Jewish education forums", big("≈ $4,000", "TYPICAL HASIDIC YESHIVA TUITION", "per child, per year — often less",
                                             bg="children_01_26", count=False, source="Source: surveys on Jewish education forums"))
at("How is that possible", card(("How is that possible?", 0.2), bg="children_00_39"))
at("Because teachers are community members", clip(266, zoom=1.03, then=(262,)))
at("and the system's goal isn't profit", card(("The goal isn't profit.", 0.2), ("It's continuity.", "@it's continuity", GOLD, 90),
                                              bg="children_02_15"))
at("Tuition breaks are standard for large families", clip(38, zoom=1.03))
at("Then add the food economy", clip(142, zoom=1.03, skip=2.0))
at("Families buy in bulk", ph("food_kosher_01_5", move="in", zoom=1.1))
at("because a household of twelve consumes like a small restaurant", clip(485, grade="none", zoom=1.05, skip=1.5))
at("Shared institutions negotiate group rates", ph("food_kosher_00_37", move="left", zoom=1.08))
at("Every dollar here works harder", card(("Every dollar works harder here.", 0.2, GOLD), bg="money_00_21"))
at("But even that isn't the deepest layer", ledger(3, new_at=0.8))

# =================================================================== chapter 5: the gemach
at("In nearly every Hasidic neighborhood", heading(5, "The Gemach", "p_00_10", sub="a bank that charges nothing"))
at("it refers to a free-loan society", board([
    title_("gemach", 960, 250, at=0.1, size=130),
    strip("from the Hebrew for “acts of kindness”", 960, 400, at=0.4, size=38, type=False),
    pc("p_00_18", 520, 700, 460, rot=-2, at="@borrow money", grade="none"),
    pc("children_00_3", 960, 720, 420, rot=1.5, at="@baby cribs", grade="none"),
    pc("p_00_29", 1400, 700, 460, rot=-1, at="@wedding dresses", grade="none")]))
at("at zero interest", big("0 %", "INTEREST", "", bg="p_00_4", count=False, size=300))
at("This isn't informal", clip(248, zoom=1.03))
at("gemach networks are a vast, organized financial layer", ph("p_00_12", move="in", zoom=1.1))
at("lending to someone in need is a commandment", card(("Lending to someone in need: a commandment.", 0.3),
                                                      ("Charging interest: forbidden.", "@charging interest is forbidden", GOLD),
                                                      bg="men_study_00_13"))
at("The economic effect is hard to overstate", bars("Who pays more for credit?", [
        ("Outside: payday loans, card interest", 90, "the poor pay more", "@Payday loans", dict(color=RUST)),
        ("Inside: the gemach", 6, "the poor pay less", "@the poor pay less", dict(color=SAGE))],
    bg="money_02_6", note="illustrative", max=100))
at("A bride's family needs $8,000", clip(24, zoom=1.03))
at("A father loses his job", ph("p_02_6", move="in", zoom=1.08))
at("Layer on top: tzedakah", clip(226, zoom=1.03))
at("from wealthier community members", ph("men_study_01_1", move="in", zoom=1.08))
at("Plus organizations like the Hebrew Free Loan Society", ph("arch_00_6", move="in", zoom=1.08, grade="none"))
at("So the ledger now reads", ledger(5, new_at="@plus internal charity", title="The household ledger · five layers"))
at("But there are two more", clip(371, zoom=1.03))

# =================================================================== chapter 6: housing
at("Poverty statistics measure income per household", heading(6, "The Housing", "exterior_building_00_44",
                                                                sub="nobody sleeps in a statistic"))
at("They sleep in an apartment", ph("exterior_building_01_12", move="up", zoom=1.08))
at("it lowers the cost per person", card(("Lower the cost per person —", 0.3), ("by raising the number of people per room.", "@by raising", GOLD),
                                         bg="exterior_building_00_2"))
at("In Williamsburg, Hasidic families routinely house", clip(211, zoom=1.03))
at("In Kiryas Joel, urban planners have documented", spot("maps_00_9", center=[0.55, 0.55], radius=[0.2, 0.18],
                                                          label="High-density multifamily housing", hit=0.8, zoom=1.12))
at("the community builds upward and close", clip(152, zoom=1.03))
at("The 2018 comprehensive plan", board([
    pc("maps_00_2", 640, 520, 820, rot=-1.5, at=0.1, grade="none"),
    title_("2018 comprehensive plan", 1360, 330, at=0.5, size=60),
    strip("“the Satmar community needs", 1360, 480, at="@the Satmar community needs", size=36, type=False),
    strip("high-density multifamily housing”", 1360, 570, at="@high-density", size=36, type=False)]))
at("families moved out of crowded Williamsburg", dict(type="map", detail="geo_hi.json", adminCountries=["USA"], stops=[
        dict(at=0, lon=-74.1, lat=41.0, scale=17000), dict(at=2, lon=-74.1, lat=41.05, scale=18000, d=3)],
    highlight=[dict(id=NY_STATE, at=0.0)],
    routes=[dict(**{"from": list(WILLIAMSBURG)}, to=list(KJ), at=0.6, d=2.2, dash=True)],
    pins=[dict(lon=WILLIAMSBURG[0], lat=WILLIAMSBURG[1], label="Williamsburg", sub="crowded", at=0.2, side="right"),
          dict(lon=KJ[0], lat=KJ[1], label="Kiryas Joel", sub="cheaper suburban land", at=2.0, side="left")]))
at("single-family homes that quickly filled with wings", ph("maps_00_20", move="right", zoom=1.08))
at("Is this comfortable by suburban American standards", card(("Comfortable by suburban standards?", 0.2), ("Often no.", "@Often no", GOLD, 90),
                                                              bg="street_03_6"))
at("Federal data has repeatedly flagged overcrowding", clip(215, zoom=1.03))
at("But it collapses the most expensive line item", bars("A home for a big family, per month", [
        ("Five-bedroom house elsewhere", 4000, "≈ $4,000", "@a five-bedroom house"),
        ("Shared, dense housing", 1900, "under half", "@might pay under half", dict(color=SAGE))],
    bg="exterior_building_00_4", note="illustrative, from the script's example", max=4200))
at("shared across a household structure with multiple earners", ledger(6, new_at=0.6))

# =================================================================== chapter 7: the ugly part
at("Now — we have to talk about the part", heading(7, "The Part That's Ugly", "institutions_00_44",
                                                     sub="not everything is charity and math"))
at("In 2019, in federal court in Brooklyn", board([
    pc("institutions_00_44", 620, 520, 760, rot=-1.5, at=0.1, grade="none"),
    title_("2019 · federal court, Brooklyn", 1340, 300, at=0.5, size=56),
    strip("Central United Talmudical Academy", 1340, 450, at="@the Central United", size=34, type=False),
    strip("admitted a benefit fraud conspiracy", 1340, 550, at="@admitted", size=34, type=False)]))
at("Its administrators had underreported income", ph("money_00_43", move="in", zoom=1.1, grade="none"))
at("The school agreed to pay $8 million", big("$8 million", "SETTLEMENT", "its director was sentenced to two years in prison",
                                              bg="money_02_2", count=False, source="Source: U.S. Attorney's Office, 2019"))
at("In Lakewood, New Jersey, in 2017", big("14", "DEFENDANTS · LAKEWOOD, 2017", "seven couples charged in a welfare fraud sting",
                                           bg="money_02_46", countFor=1.0))
at("And in New York, prosecutors have brought cases", big("$20 million", "IN MORTGAGE LOANS", "13 people accused, alongside welfare fraud",
                                                          bg="money_00_40", count=False))
at("Here's what matters about these cases", card(("Real. Documented.", 0.3), ("Pretending otherwise would be dishonest.", "@would be dishonest", GOLD),
                                                 bg="institutions_00_44"))
at("They fed a political backlash", ph("street_01_19", move="in", zoom=1.08))
at("But zoom out, and the honest picture is this", card(("Specific people. Specific institutions.", "@these are prosecutions of specific"),
                                                        ("A minority of benefit recipients.", "@a minority", GOLD), bg="street_00_51"))
at("Statistically, benefit fraud is not unique", ph("money_01_42", move="in", zoom=1.08, grade="none"))
at("The Hasidic cases got headlines", clip(62, zoom=1.03, skip=2.0))
at("They do not explain how a system", clip(55, zoom=1.03))
at("The system functions because of the layers", ledger(6, new_at=-3, title="The household ledger · one layer remains"))

# =================================================================== chapter 8: the definition of wealth
at("Here is the deepest difference", heading(8, "A Different Definition of Wealth", "shabbat_01_39"))
at("In the surrounding culture, a child is a cost", big("$200,000+", "TO RAISE ONE CHILD IN AMERICA", "estimates run past this",
                                                        bg="children_00_32", count=False))
at("In Hasidic theology, a child is the opposite", clip(508, grade="none", zoom=1.03))
at("The commandment to be fruitful", ph("named_02_37", move="in", zoom=1.1, grade="none",
                                        overlays=[dict(type="caption", text="“Be fruitful and multiply” — Genesis 1:28", at=0.8)]))
at("And the data reflects it", who(ph("men_study_00_15", move="in", zoom=1.08), "Lydia Stone",
                                   "demographer · Demographic Research, 2023", at="@Lydia Stone"))
at("driven by near-universal marriage", clip(24, zoom=1.03, skip=3.0))
at("One widely cited analysis found", bars("Expected children per woman", [
        ("Yiddish-speaking women in the U.S.", 6.6, "6.6", "@6.6 children", dict(color=GOLD)),
        ("The United States overall", 1.6, "1.6", "@compared to 1.6")],
    bg="children_02_18", max=7, note="one widely cited analysis"))
at("So when you ask \"how do they afford ten kids", clip(378, zoom=1.03, skip=0.5))
at("that question assumes kids are something you afford", card(("Children are the return —", 0.3),
                                                                ("not the expense.", "@not the expense", GOLD, 96), bg="p_02_27"))
at("And once you see that", ledger(7, new_at=0.5))

# =================================================================== the answer
at("So — how do Hasidic Jews afford ten kids", dict(type="doctitle", kicker="The answer", title="How Do They Afford Ten Kids?",
                                                    img=img("street_00_3"), move="in", zoom=1.08))
at("They don't", card(("They don't — not “without jobs.”", 0.2),
                      ("Most men work: small businesses, modest wages.", "@The men do some work", GOLD, 52), bg="street_01_52"))
at("What they don't have is high income", clip(205, zoom=1.03, skip=1.0))
at("Layer by layer", ledger(7, new_at=-3, title="Layer by layer",
                            total=dict(label="A system that doesn't need a high income", value="", at="@a system that doesn't")))
at("Benefits scaled to household size", clip(185, zoom=1.03))
at("Yeshiva education at a fraction", clip(258, zoom=1.03, skip=1.0))
at("Interest-free credit through thousands of gemachs", ph("p_00_18", move="in", zoom=1.08))
at("Dense, cheap, shared housing", ph("exterior_building_00_43", move="in", zoom=1.08))
at("And underneath all of it", clip(474, grade="none", zoom=1.03))
at("Is the model perfect", card(("Is the model perfect?", 0.2), ("No.", "@No.", GOLD, 110), bg="street_00_46"))
at("Poverty rates near 40, 50, even 60 percent are real", bars("Poverty rates, from this video", [
        ("Kiryas Joel", 38, "≈ 38 %", 0.4, dict(color=RUST)), ("Williamsburg Hasidic households", 55, "55 %", 0.8, dict(color=RUST)),
        ("New Square", 64.4, "64.4 %", 1.2, dict(color=RUST))],
    bg="street_02_26", max=100, note="the price of the design"))
at("And where individuals abused the system", ph("institutions_00_44", move="in", zoom=1.08, grade="none"))
at("But here's the final implication", clip(25, zoom=1.03))
at("It proved that family size isn't determined by income", card(("Family size isn't set by income.", 0.3),
                                                                 ("It's set by cost structure and values.", "@it's determined by cost structure", GOLD),
                                                                 bg="children_01_42"))
at("Somewhere between the poverty map and the playgrounds", clip(150, zoom=1.03))
at("If your economy makes children the most expensive", card(("If your economy makes children", 0.4),
                                                             ("the most expensive thing you'll ever do —", 1.4),
                                                             ("is the economy the sensible part?", "@is the economy the sensible part", GOLD, 70),
                                                             bg="children_02_38"))
at("Because that village where the median age is fifteen", place(ph("maps_00_9", move="out", zoom=1.12,
                                                                    overlays=[dict(type="fadeout", d=2.2)]),
                                                                 "Kiryas Joel, New York", "median age: 15.7", at=0.8))

edl.main(music=[
    dict(at=None, track="11_Unanswered_Questions_Mystery.mp3", db=-1),
    dict(at="Start with the facts", track="04_Sad_Trio_Somber_Piano_Cello.mp3", db=0, lead=-1.0),
    dict(at="Ask yourself this", track="Mark Jubel - Efteraar.mp3", db=0, lead=-1.0),
    dict(at="Here is the single most misunderstood mechanic", track="02_Leaving_Home_Somber_Long_Bed.mp3", db=0, lead=-1.0),
    dict(at="In nearly every Hasidic neighborhood", track="12_Magic_Forest_Dark_Cello.mp3", db=0, lead=-1.0),
    dict(at="Now — we have to talk about the part", track="03_Sovereign_Dark_Piano_Bed.mp3", db=-1, lead=-1.0),
    dict(at="Here is the deepest difference", track="Silent Tension Piano.mp3", db=0, lead=-1.0),
    dict(at="So — how do Hasidic Jews afford ten kids", track="Slow Dramatic Ascent.mp3", db=0, lead=-1.0),
])
