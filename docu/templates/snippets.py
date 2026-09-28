"""
snippets.py - ready-made shot builders for the three house styles.

Import it after `edl` in any project's build.py:

    import edl
    from edl import *
    from snippets import *          # (docu/templates is put on sys.path by the starter)

Every function returns a plain dict (a scene spec, or an item for a collage), so you can
still add or override any key: `verdict([...], stamp=dict(text="OPEN", at=3))`.
Times are seconds from the start of the scene, or "@phrase" to land on a word.
Colours default to the palette of the active theme when left out.
"""

from edl import img, collage, pc, strip, stamp, title_   # noqa: F401  (re-exported for convenience)

# ---------------------------------------------------------------- shared items

def note(text, x, y, at, rot=0.0, w=420, **kw):
    """A yellow sticky note in handwriting (drops in)."""
    return dict(k="note", text=text, x=x, y=y, at=at, rot=rot, w=w, **kw)


def hand(text, x, y, at, size=54, w=900, **kw):
    """Handwriting straight on the page. Use "\\n" for line breaks."""
    return dict(k="text", text=text, x=x, y=y, at=at, size=size, w=w, font="Caveat", color="#2A1E12", **kw)


def cut(image_file, x, y, h, at=0.0, **kw):
    """A cut-out object (PNG with a baked white keyline). `image_file` comes from edl.cutout()."""
    return dict(k="cut", img=image_file, x=x, y=y, h=h, at=at, **kw)


def pin(x, y, at, **kw):
    return dict(k="pin", x=x, y=y, at=at, **kw)


def red_string(points, at, d=0.9, **kw):
    """Red string between pins: points = [[x, y], [x, y], ...]."""
    return dict(k="string", pts=points, at=at, d=d, **kw)


def ring(x, y, rx, ry, at, **kw):
    """A hand-drawn circle around something."""
    return dict(k="circle", x=x, y=y, rx=rx, ry=ry, at=at, **kw)


def arrow(p0, p1, at, bend=60, **kw):
    return dict(k="arrow", **{"from": list(p0)}, to=list(p1), at=at, bend=bend, **kw)


def stat_card(value, label, x, y, at, **kw):
    """A torn stat card that counts up (collage item)."""
    return dict(k="stat", value=value, label=label, x=x, y=y, at=at, **kw)


def tag(text, sub, x, y, at, rot=0.0, **kw):
    """A manila evidence tag on a string (needs scenes_court.js)."""
    return dict(k="tag", text=text, sub=sub, x=x, y=y, at=at, rot=rot, **kw)


def W_(text, y=540, at=0.1, size=150, **kw):
    """One line of kinetic type for words(). Extra keys: x, color, font, from, strike, out, dimAt."""
    return dict(text=text, y=y, at=at, size=size, **kw)


# ---------------------------------------------------------------- style 1: paper / Vox

def board(items, **kw):
    """Paper tabletop (theme 'paper': tan paper; 'expedition': ruled journal page)."""
    return collage(items, bg="paper", **kw)


def corkboard(items, **kw):
    """Cork board (forensic: light box, expedition: leather desk)."""
    return collage(items, bg="cork", **kw)


def evidence_board(photos, links, **kw):
    """Detective board: photos = [(name, x, y, w, rot, at)], links = [((x, y), (x, y), at)]."""
    items = [pc(n, x, y, w, rot=r, at=a) for n, x, y, w, r, a in photos]
    for (p0, p1, a) in links:
        items += [pin(p0[0], p0[1] - 40, a), pin(p1[0], p1[1] - 40, a), red_string([list(p0), list(p1)], a + 0.3)]
    return collage(items, bg="cork", **kw)


def baskets(reveal=True, active=-1, labels=None, stamps=None, **kw):
    """Three case folders: known / claimed / unknown. active=0..2 pulls one forward."""
    s = dict(type="baskets", reveal=reveal, active=active, **kw)
    if labels: s["labels"] = labels
    if stamps: s["stamps"] = stamps
    return s


def newspaper(masthead, headline, deck="", body=(), image=None, **kw):
    """A broadsheet page; the headline is highlighted line by line. headline may contain \\n."""
    s = dict(type="newspaper", masthead=masthead, headline=headline, deck=deck, body=list(body), **kw)
    if image: s["img"] = img(image, "bw")
    return s


def headlines(items, **kw):
    """Torn headline strips: items = [(text, x, y, rot, at, style)] style: white/red/black/tan."""
    return dict(type="headlines", items=[dict(text=t, x=x, y=y, rot=r, at=a, style=st) for t, x, y, r, a, st in items], **kw)


# ---------------------------------------------------------------- style 2: forensic / lab report

OBS, CLA, CON = 0, 1, 2          # filter columns: observed / claimed / confirmed


def fcard(text, col, at, size=None):
    d = dict(text=text, col=col, at=at)
    if size: d["size"] = size
    return d


def evidence_filter(items, heads=None, zero=None, zero_text=None, **kw):
    """Sort evidence cards into columns (default OBSERVED / CLAIMED / CONFIRMED).
    zero=time shows a big "0 - nothing confirmed yet" in the last column."""
    s = dict(type="filter", items=items)
    if heads: s["heads"] = heads
    if zero is not None:
        s["zeroAt"] = zero
        if zero_text: s["zeroText"] = zero_text
    s.update(kw)
    return s


def gauge(kicker, to, label="", bg=None, **kw):
    """Ring gauge that fills to `to` percent; to2/at2/label2 drain it to a second value."""
    s = dict(type="gauge", kicker=kicker, to=to, label=label)
    if bg: s["img"] = img(bg)
    s.update(kw)
    return s


def network(center, nodes, **kw):
    """One source, many echoes: nodes = [(label, at)] or dicts with r / dashed."""
    return dict(type="network", center=center,
                nodes=[n if isinstance(n, dict) else dict(label=n[0], at=n[1]) for n in nodes], **kw)


def xray(name, crop=None):
    """A picture graded as an x-ray (for scans, radar images)."""
    return img(name, "xray", crop)


# ---------------------------------------------------------------- style 3: expedition / courtroom

def journal(items, **kw):
    return collage(items, bg="paper", **kw)


def desk(items, **kw):
    return collage(items, bg="cork", **kw)


def exhibit(letter, what, photo_name, at_tag=0.1, crop=None, grade=None, w=860):
    """Opening card for one exhibit: the photo on the desk, then its tag."""
    return desk([pc(photo_name, 1180, 540, w, rot=2, at=0.0, crop=crop, grade=grade),
                 tag(f"EXHIBIT {letter}", what, 470, 520, at_tag, rot=-5, w=520, size=74, subSize=34)], z1=1.04)


def reclass(claim, finding, photo_name, at_find, crop=None, color="#5E8A3E"):
    """A claimed exhibit re-labelled by the lab: photo, the claim's tag, then the finding's tag."""
    return journal([pc(photo_name, 600, 520, 780, rot=-2, at=0.0, crop=crop),
                    tag(claim, "the claim", 1400, 360, 0.3, rot=4, w=560, size=52),
                    tag("FINDING", finding, 1400, 680, at_find, rot=-3, w=560, size=52, color=color)])


def pan(side, text, at, w=1, **kw):
    """An item for scales(): side 0 = left pan, 1 = right pan, w = weight."""
    return dict(side=side, text=text, at=at, w=w, **kw)


def scales(title, items, left="THE CASE FOR", right="THE CASE AGAINST", norm=3, **kw):
    """Scales of justice. The beam tips by (right weight - left weight) / norm.
    tilts=[dict(at=..., v=-1..1)] drives the beam by hand instead."""
    return dict(type="scales", title=title, left=dict(title=left), right=dict(title=right),
                items=items, norm=norm, **kw)


def scoreboard(title, rows, **kw):
    """Split-flap board: rows = [dict(n="1", text="FAILED DIG", at=..., stamp=dict(text=..., at=...))]."""
    return dict(type="scoreboard", title=title, rows=rows, **kw)


def vi(side, text, at, **kw):
    """An item for verdict(): side 0 = left column, 1 = right. mark: yes / no / dash."""
    return dict(side=side, text=text, at=at, **kw)


def verdict(items, left="REALITY", right="MYTH", left_sub="", right_sub="", **kw):
    """Two-column verdict sheet. focus=0/1 + focusAt dims the other column.
    Give items a negative `at` to have them already there (for a follow-up scene)."""
    s = dict(type="verdict", left=dict(title=left, sub=left_sub), right=dict(title=right, sub=right_sub), items=items)
    s.update(kw)
    return s


def ledger(lines, circle=None, **kw):
    """Handwriting on old paper, line by line: lines = [(text, at, y)] or dicts (size, color, x)."""
    s = dict(type="ledger", lines=[ln if isinstance(ln, dict) else dict(text=ln[0], at=ln[1], y=ln[2]) for ln in lines])
    if circle: s["circle"] = circle
    s.update(kw)
    return s


# ---------------------------------------------------------------- maps

def map_scene(stops, **kw):
    """stops = [dict(at, lon, lat, scale, d)] - scale ~450 whole globe, ~3000 a country,
    ~40000 a valley. Other keys: highlight, pins, dots, names, routes, circles, detail."""
    return dict(type="map", stops=stops, **kw)


def map_pin(lonlat, label, at, sub=None, side="right", **kw):
    d = dict(lon=lonlat[0], lat=lonlat[1], label=label, at=at, side=side, **kw)
    if sub: d["sub"] = sub
    return d


def map_route(a, b, at, d=1.6, dash=False, label=None, **kw):
    r = dict(**{"from": list(a)}, to=list(b), at=at, d=d, dash=dash, **kw)
    if label: r["label"] = label
    return r
