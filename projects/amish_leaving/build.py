"""
Why Thousands of Amish Are Leaving Their 300-Year Homeland — The Real Reason is SHOCKING!
(Lancaster County, Pennsylvania, and the migration to New York, Kentucky and the Midwest)

Look: the ALMANAC template (docu/scenes_almanac.js, theme "almanac") - a farmer's almanac / heritage field
guide. Different from every earlier video: slab-serif chapter headings that rise over moving footage with a
stitched badge, seed-packet place tags, quilt-frame key-point cards, charts drawn on cream paper (a growth
line, a field fenced into five strips, generations as dots, a split bar, price columns, a church district),
and a cream survey map with red target markers and inked routes. Barn red, field green, wheat, denim.

Slow, calm pacing: footage carries most of the video (it opens on moving footage, not a still); photographs
drift slowly; graphics only on the key points; soft dissolves; paper-and-pen sound only.

Footage: free stock clips and photographs (Pexels / Pixabay licence: free to use, no attribution needed,
no watermarks), no talking heads. data/sources.json lists every file and its page.

    python build.py plan | prep | stills [ids] | render [ids] | mix | final | all
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "docu"))

import edl                       # noqa: E402
from edl import *                # noqa: E402,F401,F403

SP = os.environ.get("VIDEO_ROOT", os.path.join(HERE, "..", "..", "media"))
AM = f"{SP}/amish"
edl.setup(
    name="Why_Thousands_of_Amish_Are_Leaving_Their_300_Year_Homeland",
    kit=os.environ.get("VIDEO_KIT", f"{SP}/kit"),
    footage=os.environ.get("VIDEO_FOOTAGE", f"{AM}/footage"),
    work=os.environ.get("VIDEO_WORK", f"{SP}/work7"),
    data=os.path.join(HERE, "data"),
    out=os.environ.get("VIDEO_OUT", f"{SP}/out"),
    image_dirs=[os.environ.get("VIDEO_IMAGES", f"{AM}/src/images")],
    theme="almanac", grade="almanac", grain=4.0, xfade=0.5,
    music_floor_db=-21.0, music_duck_db=-10.0, sfx_gain=0.55,
    sfx_style="calm", vary="auto",
)

BARN, FIELD, WHEAT, DENIM = "#9E3A2B", "#5E7A44", "#D4A85A", "#4E6E8A"
LANC = (-76.30, 40.04)
PA, NY, KY, OH, MD = "USA-3560", "USA-3559", "USA-3548", "USA-3550", "USA-3557"
WI, MO, IA, MN, TN, IN = "USA-3553", "USA-3531", "USA-3529", "USA-3514", "USA-3551", "USA-3547"

# ---------------------------------------------------------------- building blocks
MISSING = []
_IDX = {c["video"][:-4]: c["i"] for c in edl.CAT}
_MOVES = ["in", "left", "out", "right", "in", "up"]
_m = [0]


def C(name, then=(), **kw):
    """a footage clip by its file name (data/catalog_all.json is made from media/amish/src/clips)"""
    kw.setdefault("zoom", 1.03)
    if os.environ.get("LOOSE") and name not in _IDX:      # plan before every download has landed
        MISSING.append(name)
        name, then = next(iter(_IDX)), ()
    return clip(_IDX[name], then=tuple(_IDX[t] for t in then), **kw)


def P(name, move=None, zoom=1.08, focus=None, **kw):
    """a photograph with a slow drift"""
    if move is None:
        move = _MOVES[_m[0] % len(_MOVES)]
        _m[0] += 1
    return photo(name, move=move, zoom=zoom, focus=focus, **kw)


def _ov(scene, o):
    scene = dict(scene)
    scene["overlays"] = list(scene.get("overlays", [])) + [o]
    return scene


def head(scene, n, title, kicker=None, sub=None, at=0.5, **kw):
    """chapter heading laid over moving footage"""
    o = dict(type="almhead", n=n, title=title, kicker=kicker or f"Chapter {['', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten'][n]}", at=at, **kw)
    if sub: o["sub"] = sub
    return _ov(scene, o)


def tag(scene, text, sub=None, at=0.6, **kw):
    o = dict(type="almtag", text=text, at=at, **kw)
    if sub: o["sub"] = sub
    return _ov(scene, o)


def card(*lines, bg, kicker=None, dim=0.62, **kw):
    """a key point in a quilt frame; each line: text or (text, at, color, size, font)"""
    ls = []
    for ln in lines:
        if isinstance(ln, str):
            ln = (ln,)
        d = dict(text=ln[0])
        for k, v in zip(("at", "color", "size", "font"), ln[1:]):
            if v is not None: d[k] = v
        ls.append(d)
    s = dict(type="almcard", lines=ls, img=img(bg), dim=dim)
    if kicker: s["kicker"] = kicker
    s.update(kw)
    return s


def stat(value, kicker, note, bg, **kw):
    return dict(type="almstat", value=value, kicker=kicker, note=note, img=img(bg), **kw)


def fadein(scene, d=1.6):
    return _ov(scene, dict(type="fadein", d=d))


def fadeout(scene, d=2.5):
    return _ov(scene, dict(type="fadeout", d=d))


def pin(label, lon, lat, at, sub=None, side="right", **kw):
    p = dict(label=label, lon=lon, lat=lat, at=at, side=side, **kw)
    if sub: p["sub"] = sub
    return p


def amap(stops, title=None, **kw):
    s = dict(type="map", detail="geo_hi.json", adminCountries=["USA"], stops=stops, **kw)
    if title: s["title"] = title
    return s


# =================================================================== cold open (moving footage)
at(0.0, fadein(tag(C("px18333469"), "Intercourse, Pennsylvania", "Route 340", at="@Intercourse")))
at("surrounded by idling suburban SUVs", C("px18333494"))
at("Behind the buggy stands a three-story", P("pe9826958", move="up", zoom=1.1))
at("But the rolling pastures that once surrounded it", C("px34208179"))
at("are now bordered by a sprawling shopping outlet", C("px32835508"))
at("a suburban housing subdivision", C("px32179574"))
at("An auction sign stands planted", C("px37920031"))
at("advertising prime Lancaster County agricultural soil", stat("$25,000", "Lancaster County farmland · per acre",
                                                                "advertised on a farm auction sign — and more", "pe4613517",
                                                                at="@for more than twenty-five", countFor=1.6))
at("For nearly three centuries", tag(C("px4617441"), "Lancaster County, Pennsylvania", "the Old Order Amish heartland"))
at("Yet today, hundreds of families are quietly packing", head(C("px39669906"), None, "Leaving Lancaster",
                                                                 kicker="The Amish exodus", at=0.8, size=118))
at("Almost everyone who sees them leave", C("px31612691"))
at("and that assumption is completely wrong", P("pe38726328", move="in"))
at("They are not leaving because their culture is shrinking", card(
    ("They are not leaving because", 0.3), ("their culture is shrinking.", 0.9),
    ("Their numbers are exploding.", "@they are leaving because their numbers", WHEAT, 92), bg="pi7637951"))

# =================================================================== 1 · the numbers
at("The demographic reality of the Amish", head(C("px19655183"), 1, "A Population Explosion"))
at("A century ago, the total Amish population", dict(
    type="almgrowth", title="The Amish population of North America", note="doubling roughly every 22 years",
    source="Young Center for Anabaptist and Pietist Studies · Elizabethtown College",
    points=[dict(x=1920, y=5000, label="5,000", sub="a century ago", at=0.8, dx=-40),
            dict(x=2000, y=165000, label="165,000", sub="2000", at="@By the year 2000"),
            dict(x=2024, y=400000, label="400,000+", sub="today · 32 states", at="@has surpassed four hundred thousand", dx=-240, dy=-50)],
    ticks=[1920, 1940, 1960, 1980, 2000, 2024], xmax=2030,
    grid=[dict(y=100000, label="100,000"), dict(y=200000, label="200,000"), dict(y=300000, label="300,000"), dict(y=400000, label="400,000")],
    ymax=460000))
at("Their numbers double roughly every", C("px9309696"))
at("While birth rates across the Western world", C("px37165618"))
at("the Amish maintain an average family size", stat("7–9", "Children in the average Amish family",
                                                      "and more than 85% of young adults stay and are baptized", "pe2998987",
                                                      count=False, at=0.4))

# =================================================================== the ordinary move
at("Consider how an ordinary American family", C("px28191277"))
at("You pack your belongings because of a corporate", C("px9507657", then=("px37368522",)))
at("You move as an isolated nuclear unit", C("px30728494"))
at("buy a house in a planned suburban development", C("px34668476"))
at("and immediately integrate into the local utility grid", C("px26547060"))
at("Your relocation is an individual economic transaction", C("px2818521"))
at("Why would thousands of deeply traditional families", C("px37920028"))
at("soil their ancestors cleared by hand", P("pe16636334", move="left"))
at("What is actually driving this mass migration", P("pe32678634", move="in"))
at("and where is America's fastest-growing", C("px4617492"))

# =================================================================== 2 · backwards
at("The conventional assumption made by outside observers", head(C("px19667210"), 2, "Completely Backwards",
                                                                    sub="it is not persecution, poverty or the youth leaving"))
at("The Amish exodus is governed not by", card(
    ("Not secular assimilation.", 0.4, None, 52, "BaskI"),
    ("Explosive population growth", "@explosive demographic compounding", WHEAT, 76),
    ("colliding with", "@and the non-negotiable", None, 40, "BaskI"),
    ("a faith that must farm, apart.", "@spiritual requirement of agrarian", None, 76),
    bg="pe1671846", kicker="The real reason"))
at("Under the unwritten communal code known as the Ordnung", tag(P("pe1733192", move="right"), "The Ordnung",
                                                                   "the unwritten rules of Amish life", at="@known as the Ordnung"))
at("it is the protective spiritual vessel", C("px9467497"))
at("When soaring land prices and suburban sprawl", C("px12240430"))
at("the community cannot simply adapt by becoming", C("px37368522"))
at("To preserve the soul of their faith", C("px18333476"))

# =================================================================== 3 · the promised valley
at("To understand the magnitude of this departure", head(C("px4617021"), 3, "The Promised Valley"))
at("In the early eighteenth century, Swiss-German", amap(
    [dict(at=0, lon=8.0, lat=46.8, scale=2600),
     dict(at="@Invited by William Penn", lon=-34.0, lat=46.0, scale=780, d=4.0),
     dict(at="@southeastern Pennsylvania", lon=-76.3, lat=40.3, scale=7800, d=3.0)],
    title="The 1700s · the crossing",
    pins=[pin("Switzerland", 8.2, 46.8, 0.8, "Anabaptist refugees", side="right", out="@Invited by William Penn"),
          pin("Lancaster County", *LANC, "@southeastern Pennsylvania", "Pennsylvania", side="right")],
    routes=[dict(from_=[7.6, 47.0], to=list(LANC), at="@Invited by William Penn", d=5.0, arrow=True, width=4, dash=True)],
    highlight=[dict(id=PA, at="@southeastern Pennsylvania")],
    names=[dict(text="Atlantic Ocean", lon=-38, lat=40, at="@absolute religious freedom", font="BaskI", size=40,
                out="@southeastern Pennsylvania")]))
at("There, they found some of the most fertile", C("px12484254"))

at("For generations, Lancaster County served", C("px19898363"))
at("The Amish community built an entirely self-contained", P("pi3268061", move="right"))
at("draft horses, mutual aid", C("px35732661"))
at("They rejected grid electricity", P("pi4901852", move="in"))
at("believing that modern consumer technology", C("px9467499"))
at("In this fertile valley, a father could farm", P("pe8514564", move="left"))
at("and pass the land down to his sons", C("px37920031", skip=8))

# =================================================================== 4 · the trap
at("That system worked flawlessly", head(C("px19655182"), 4, "The Mathematical Trap"))
at("In a society where every family averages", dict(
    type="almdots", title="Eight children a family", note="one community, one generation later each time",
    rows=[dict(label="Today", value="10,000", n=10, at=0.6),
          dict(label="1 generation", value="20,000", n=20, at="@twenty thousand in a single"),
          dict(label="2 generations", value="40,000", n=40, at="@forty thousand in the next"),
          dict(label="3 generations", value="80,000", n=80, at="@and eighty thousand soon after", color=BARN)],
    fill=0.9))
at("When an Amish farmer with eighty acres", dict(
    type="almsplit", title="One farm, five sons", note="an 80-acre dairy farm", label="80 acres", n=5,
    each="16 acres", who="son {n}", splitAt="@has four or five sons", verdictAt="@You cannot divide",
    verdict="too small to keep a family on a horse-drawn farm"))
at("Compounding this internal population pressure", C("px2570204"))
at("Over the last four decades", amap(
    [dict(at=0, lon=-76.3, lat=40.0, scale=11500), dict(at=8.5, lon=-76.1, lat=39.95, scale=12500, d=8.0)],
    title="Commuter belts",
    pins=[pin("Lancaster", *LANC, 0.5, "the Amish heartland", side="right", color=FIELD),
          pin("Philadelphia", -75.16, 39.95, "@Philadelphia", side="right"),
          pin("Harrisburg", -76.88, 40.27, "@Harrisburg", side="left"),
          pin("Baltimore", -76.61, 39.29, "@and Baltimore", side="left")],
    circles=[dict(lon=-75.16, lat=39.95, km=45, at="@Philadelphia"), dict(lon=-76.88, lat=40.27, km=30, at="@Harrisburg"),
             dict(lon=-76.61, lat=39.29, km=40, at="@and Baltimore")],
    highlight=[dict(id=PA, at=0.2), dict(id=MD, at="@and Baltimore", fill="rgba(78,110,138,.18)")]))
at("Prime farmland was rapidly purchased", C("px11841268"))
at("commercial shopping centers", C("px32835503"))
at("Simultaneously, the county became a major global tourist", P("pe8514530", move="right"))
at("drawing millions of visitors eager", P("pi1728517", move="in"))

# =================================================================== 5 · the price of soil
at("The collision of suburban development and agricultural", head(C("px19667208"), 5, "The Price of Soil"))
at("Agricultural land that once sold", dict(
    type="almbars", title="Lancaster County farmland · price per acre", note="as developers and tourism moved in",
    bars=[dict(label="once", value=3000, text="$3,000", at=0.8),
          dict(label="then", value=15000, text="$15,000", at="@climbed to fifteen thousand"),
          dict(label="later", value=25000, text="$25,000", at="@twenty-five thousand, and"),
          dict(label="prime land", value=35000, text="$35,000+", at="@more than thirty-five thousand", color=BARN)]))
at("For a young twenty-one-year-old Amish man", P("pe9568816", move="in", focus=(0.45, 0.4)))
at("Purchasing land, constructing a traditional bank barn", C("px15148904"))
at("acquiring a herd of dairy cows", C("px3530245"))
at("routinely required two to three million", stat("$2–3 million", "In cash, to start one 80-acre dairy farm",
                                                   "land, a bank barn, a dairy herd, horse-drawn machinery", "pe34471682",
                                                   count=False, at=0.2))

# =================================================================== 6 · off the soil
at("Because few young couples possessed millions", head(C("px19898357"), 6, "Off the Soil"))
at("Unable to buy farms", P("pe17544219", move="up"))
at("They transitioned into non-farm entrepreneurship", P("pe7361221", move="in"))
at("They opened woodworking shops", C("px5972112", then=("px20663033",)))
at("worked in commercial roofing crews", C("px7314256"))
at("and operated retail quilt stands", P("pe33451390", move="left"))
at("Today, researchers at Elizabethtown College", dict(
    type="almshare", title="How adult Amish men in Lancaster County earn a living",
    source="Elizabethtown College", y=440,
    parts=[dict(frac=0.31, big="< 1/3", label="Farming", sub="their primary living", color=FIELD, at="@fewer than one-third"),
           dict(frac=0.69, big="> 2/3", label="Trades, construction, manufacturing", sub="sheds, roofing, furniture, quilts",
                color=DENIM, at="@More than two-thirds work")]))
at("While these small businesses generated", C("px20184480"))
at("they created profound anxiety among church elders", P("pe9459922", move="right"))
at("To the outside observer, an Amish carpenter", card(
    ("To the outside observer:", 0.3, None, 40, "BaskI"),
    ("a model of American success.", "@looks like a model", None, 70),
    ("To a conservative bishop:", "@To a conservative Amish bishop", None, 40, "BaskI"),
    ("a slow, spiritual catastrophe.", "@a slow, spiritual catastrophe", WHEAT, 80), bg="pi5070133"))
at("The reason was simple", C("px9468666"))
at("When an Amish man worked his own fields", C("px13456884"))
at("the family spent twelve hours a day together", P("pe27539572", move="in"))
at("But when an Amish man operates a commercial construction", C("px11841266"))
at("he must travel in motor vehicles", C("px2836001"))
at("interact daily with secular contractors", C("px34006623"))
at("and carry battery-operated cellular phones", C("px6186015"))
at("Inside commercial workshops", C("px20374770"))
at("To compete in modern markets", C("px5759818"))
at("diesel generators", C("px30456100"))
at("Young Amish workers were suddenly earning", C("px35323779"))
at("spending their days listening to secular radio", C("px31025083"))
at("Traditional church leaders recognized", P("pe14058112", move="in"))
at("the internal spiritual discipline of the Ordnung", P("pe17488867", move="up"))
at("For conservative bishops and concerned fathers", C("px25405403"))
at("You cannot maintain the soul of an Old Order", card(
    ("You cannot maintain the soul", 0.3, None, 64), ("of an Old Order church", 0.9, None, 64),
    ("without the soil.", "@without the soil", WHEAT, 96),
    ("So the community had to leave.", "@then the community had to leave", None, 46, "BaskI"), bg="pe12345626"))
at("The only way to save the culture", C("px29011159"))
at("in regions where farmland was still cheap", C("px18486127"))

# =================================================================== 7 · the exodus
at("The migration was not a chaotic", head(C("px28122441"), 7, "The Exodus", sub="planned like a harvest"))
at("Church districts formed scouting committees", P("pe19051851", move="right"))
at("These scouts hired non-Amish drivers", C("px15450883"))
at("fertile soil, reliable rainfall", card(
    ("Fertile soil", 0.0, None, 60), ("Reliable rainfall", "@reliable rainfall", None, 60),
    ("Low property taxes", "@low local property taxes", None, 60), ("Affordable land", "@affordable land prices", None, 60),
    ("Neighbours who would welcome them", "@and local rural populations", WHEAT, 60),
    bg="pe34471682", kicker="What the scouts looked for", dim=0.68))
at("One of the primary destinations chosen", amap(
    [dict(at=0, lon=-77.3, lat=41.3, scale=5600), dict(at="@Regions like the Conewango", lon=-76.6, lat=42.5, scale=5000, d=2.5)],
    title="North to New York",
    pins=[pin("Lancaster County", *LANC, 0.5, "Pennsylvania", side="right", color=FIELD),
          pin("Conewango Valley", -79.0, 42.2, "@Regions like the Conewango", "& Chautauqua County", side="right"),
          pin("St. Lawrence County", -75.1, 44.5, "@Lawrence County", side="right"),
          pin("Mohawk Valley", -74.7, 42.9, "@and the Mohawk Valley", side="right", gap=90)],
    routes=[dict(from_=list(LANC), to=[-79.0, 42.2], at="@Regions like the Conewango", d=1.6, arrow=True, width=4),
            dict(from_=list(LANC), to=[-75.1, 44.5], at="@Lawrence County", d=1.6, arrow=True, width=4),
            dict(from_=list(LANC), to=[-74.7, 42.9], at="@and the Mohawk Valley", d=1.4, arrow=True, width=4)],
    highlight=[dict(id=PA, at=0.2), dict(id=NY, at="@Upstate and Western New York", fill="rgba(94,122,68,.22)")]))
at("In these counties, where centuries of rural", C("px29011156"))
at("productive agricultural land could be purchased", dict(
    type="almbars", title="Farmland · price per acre", note="roughly one-tenth the cost", x0=520, ht=500,
    bars=[dict(label="Lancaster County", value=25000, text="$25,000", at=0.6, color=BARN),
          dict(label="Upstate New York", value=3000, text="$2–4,000", at="@for two thousand to four thousand", color=FIELD)]))
at("The scale of the migration into New York", C("px12172104"))
at("In the early 1970s, New York", P("pe446341", move="in"))
at("Today, New York hosts more than", stat("23,000", "Amish residents in New York today",
                                         "in more than 60 settlements — from a handful in the early 1970s", "pe35743350",
                                         countFor=1.8))
at("Entire agricultural valleys that had been abandoned", C("px37919911"))
at("were brought back to life by horse-drawn plows", P("pi2818758", move="left"))
at("Abandoned dairy barns were repaired", C("px5768181"))
at("and quiet country roads were repaved", C("px19667212"))
at("Simultaneously, a massive southern migration", amap(
    [dict(at=0, lon=-80.5, lat=39.3, scale=3300), dict(at="@Areas like Hart County", lon=-85.6, lat=37.4, scale=5400, d=2.6)],
    title="South to Kentucky",
    pins=[pin("Lancaster County", *LANC, 0.4, "Pennsylvania", side="right", color=FIELD, out="@Areas like Hart County"),
          pin("Hart County", -85.88, 37.30, "@Areas like Hart County", "Munfordville · Horse Cave", side="right"),
          pin("Christian County", -87.49, 36.89, "@alongside settlements in Christian", "& Todd County", side="left", gap=100)],
    routes=[dict(from_=list(LANC), to=[-85.88, 37.30], at="@pushed into Kentucky", d=2.4, arrow=True, width=4)],
    highlight=[dict(id=PA, at=0.2), dict(id=KY, at="@pushed into Kentucky", fill="rgba(94,122,68,.22)")]))
at("According to census data, Kentucky", stat("17,000", "Amish residents in Kentucky",
                                             "in nearly 60 church districts — now among the top states", "pe34662340",
                                             countFor=1.8))
at("Similar daughter settlements were established", amap(
    [dict(at=0, lon=-86.0, lat=40.5, scale=2500), dict(at=6.0, lon=-87.0, lat=40.5, scale=2350, d=6.0)],
    title="Daughter settlements",
    highlight=[dict(id=PA, at=0), dict(id=NY, at=0, fill="rgba(94,122,68,.22)"), dict(id=KY, at=0, fill="rgba(94,122,68,.22)"),
               dict(id=WI, at="@in Wisconsin", fill="rgba(94,122,68,.22)"), dict(id=MO, at="@Missouri", fill="rgba(94,122,68,.22)"),
               dict(id=IA, at="@Iowa", fill="rgba(94,122,68,.22)"), dict(id=MN, at="@Minnesota", fill="rgba(94,122,68,.22)"),
               dict(id=TN, at="@and Tennessee", fill="rgba(94,122,68,.22)")],
    names=[dict(text="Wisconsin", lon=-89.9, lat=44.6, at="@in Wisconsin", font="Slab", size=30, color="#23211C"),
           dict(text="Missouri", lon=-92.5, lat=38.4, at="@Missouri", font="Slab", size=30, color="#23211C"),
           dict(text="Iowa", lon=-93.5, lat=42.0, at="@Iowa", font="Slab", size=30, color="#23211C"),
           dict(text="Minnesota", lon=-94.3, lat=46.3, at="@Minnesota", font="Slab", size=30, color="#23211C"),
           dict(text="Tennessee", lon=-86.3, lat=35.8, at="@and Tennessee", font="Slab", size=30, color="#23211C"),
           dict(text="Kentucky", lon=-85.3, lat=37.5, at=0.3, font="Slab", size=30, color="#23211C"),
           dict(text="New York", lon=-75.5, lat=42.9, at=0.3, font="Slab", size=30, color="#23211C"),
           dict(text="Pennsylvania", lon=-77.6, lat=40.9, at=0.3, font="Slab", size=30, color="#23211C")]))
at("If you value this kind of measured", C("px10885104"))
at("It helps support independent research", P("pe2042161", move="in"))

# =================================================================== 8 · building from nothing
at("The physical process of relocation", head(C("px34066758"), 8, "Building From Nothing"))
at("The basic unit of Amish life is the church district", dict(
    type="almdistrict", title="One church district", note="the unit that moves together", houses=30,
    centre="Church district", centreSub="25–35 families", housesAt=0.9, step=0.05,
    roles=[dict(text="1 bishop", at="@under the spiritual care of a bishop"), dict(text="2 ministers", at="@two ministers"),
           dict(text="1 deacon", at="@and a deacon")]))
at("When a new settlement is founded", C("px8457857"))
at("They hire chartered commercial flatbed trucks", C("px15510261"))
at("wood-burning stoves, and handmade furniture", P("pe9890650", move="in"))
at("Upon arriving in a new rural county", C("px4617442"))
at("They pool labor to raise barns", P("pe12983687", move="out"))
at("and erect a one-room parochial schoolhouse", C("px27132782"))
at("The children leave the public educational system", P("pe9575016", move="in"))
at("attending community schools taught by young", P("pe39102545", move="up"))
at("and German hymns through the eighth grade", P("pe20875548", move="in"))
at("Within months of arrival", C("px9316131"))
at("holding worship services in members' homes", P("pi166057", move="left"))
at("For many depressed rural American towns", C("px4606787"))
at("In rural counties where schools were closing", C("px4606785"))
at("and local main streets were shuttering", C("px10148955"))
at("They purchased decaying farmsteads", P("pi9616520", move="right"))
at("and established bustling sawmills", C("px7165540"))
at("produce auctions, bulk food stores", C("px10039848"))
at("Non-Amish hardware stores, feed mills", C("px19675231"))
at("creating cooperative relationships between", C("px27902028"))
at("Yet this rapid migration has also generated", P("pe5275507", move="in"))
at("In rural New York and Kentucky, local town councils", C("px5542449"))
at("with the sudden appearance of slow-moving buggies", P("pe32678634", move="left", zoom=1.12))
at("leading to traffic accidents and debates", P("pi1728517", move="out", focus=(0.6, 0.6)))
at("In several jurisdictions, tensions erupted", P("pe18671193", move="in"))
at("and state mandates requiring indoor plumbing", P("pe14280799", move="right"))

# =================================================================== 9 · what they leave behind
at("The emotional toll of this migration", head(C("px4817975"), 9, "What They Leave Behind",
                                              sub="three centuries of family heritage"))
at("When a young family packs their belongings", P("pe23500594", move="left"))
at("they are leaving behind the cemetery plots", P("pe37165990", move="in"))
at("of their direct ancestors lie buried", C("px27670380"))
at("They are separating elderly grandparents", P("pe5561791", move="in"))
at("in a society where telephone calls are restricted", C("px26771970"))
at("The move often divides extended families", P("pe32503372", move="in", focus=(0.5, 0.4)))
at("More progressive Amish families who choose to remain", C("px11645112"))
at("operating successful multi-million-dollar", C("px6789582"))
at("Meanwhile, the conservative families who depart", C("px19898361"))
at("They deliberately trade modern business wealth", P("pi5143781", move="right"))
at("choosing poverty and physical isolation", C("px29461443"))

# =================================================================== 10 · too successful
at("Here lies the great irony", head(C("px19898360"), 10, "Too Successful"))
at("the plain denim clothes", P("pi287407", move="right"))
at("and assume they are looking at a dying", P("pe17502895", move="up"))
at("In reality, the exact opposite is taking place", card(
    ("In reality,", 0.2, None, 44, "BaskI"), ("the exact opposite is taking place.", 0.8, None, 70),
    ("A traditional community is outgrowing", "@is watching a traditional community", WHEAT, 70),
    ("its own homeland.", "@the physical boundaries", WHEAT, 70), bg="pe33777985"))
at("The Amish are leaving Lancaster County not because", C("px4617576"))
at("They proved that a community built on shared faith", C("px35960596"))
at("When forced to choose between the financial wealth", C("px10061598"))
at("thousands of families chose the soil", P("pe16636334", move="in", zoom=1.14))
at("If current demographic trajectories continue", stat("1,000,000", "The Amish population, projected",
                                                         "by the middle of the twenty-first century · Young Center", "pe1089097",
                                                         at="@will approach one million", countFor=2.2))
at("As older settlements in Pennsylvania and Ohio", amap(
    [dict(at=0, lon=-80.5, lat=40.3, scale=2700), dict(at="@the map of rural America", lon=-86.5, lat=40.2, scale=2150, d=5.0)],
    title="The map, redrawn",
    highlight=[dict(id=PA, at=0.4), dict(id=OH, at="@and Ohio"),
               dict(id=NY, at="@the hills of New York", fill="rgba(94,122,68,.25)"),
               dict(id=KY, at="@the valleys of Kentucky", fill="rgba(94,122,68,.25)"),
               dict(id=IN, at="@the plains of the Midwest", fill="rgba(94,122,68,.25)"),
               dict(id=IA, at="@the plains of the Midwest", fill="rgba(94,122,68,.25)"),
               dict(id=WI, at="@the plains of the Midwest", fill="rgba(94,122,68,.25)"),
               dict(id=MO, at="@the plains of the Midwest", fill="rgba(94,122,68,.25)"),
               dict(id=MN, at="@the plains of the Midwest", fill="rgba(94,122,68,.25)")],
    names=[dict(text="Pennsylvania", lon=-77.6, lat=40.9, at=0.6, font="Slab", size=30, color="#23211C"),
           dict(text="Ohio", lon=-82.8, lat=40.3, at="@and Ohio", font="Slab", size=30, color="#23211C"),
           dict(text="New York", lon=-75.5, lat=42.9, at="@the hills of New York", font="Slab", size=30, color="#23211C"),
           dict(text="Kentucky", lon=-85.3, lat=37.5, at="@the valleys of Kentucky", font="Slab", size=30, color="#23211C"),
           dict(text="the Midwest", lon=-92.5, lat=42.0, at="@the plains of the Midwest", font="BaskI", size=44, color="#9E3A2B")]))
at("When you look at your own life", C("px39083602"))
at("how many compromises have you made", C("px10527947"))
at("What would it take for you to walk away", C("px39669906", skip=4))
at("What is your perspective on the Amish migration", fadeout(card(
    ("Can traditional farming communities", "@Can traditional agrarian", None, 62),
    ("survive in modern America?", "@survive indefinitely", None, 62),
    ("Or will the secular world catch up?", "@or will the secular world", WHEAT, 62),
    ("Share your perspective in the comments.", "@Share your perspective", None, 36, "BaskI"),
    bg="pi9594035", kicker="Your turn"), d=3.0))


# ============================================================== music: one quiet bed per act
edl.main(music=[
    dict(at=None, track="02_Leaving_Home_Somber_Long_Bed.mp3"),
    dict(at="To understand the magnitude of this departure", track="Mark Jubel - Efteraar.mp3", lead=-1.0),
    dict(at="That system worked flawlessly", track="04_Sad_Trio_Somber_Piano_Cello.mp3", lead=-1.0),
    dict(at="The migration was not a chaotic", track="Slow Dramatic Ascent.mp3", lead=-1.0),
    dict(at="The physical process of relocation", track="12_Magic_Forest_Dark_Cello.mp3", lead=-1.0),
    dict(at="Here lies the great irony", track="02_Leaving_Home_Somber_Long_Bed.mp3", lead=-1.0),
])
