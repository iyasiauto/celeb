"""
shots.py - the shot helpers a studio-generated build.py uses (`from shots import *`).

They are the helpers of the hand-made videos (projects/hasidic_benefits_cut/build.py), made
theme-aware so the same shot list works in every style:

    ph(key, move=None)              photograph with a slow move (the video's move cycle if move is None)
    cl(i, then=(), skip=0)          footage clip i of the catalog (then= joins more shots)
    place(scene, text, sub)         location caption overlay
    who(scene, name, role)          name / role lower third
    heading(n, title, bg, sub)      chapter heading (doctitle in "documentary", chapter card elsewhere)
    card(*lines, bg)                one to three lines over a darkened photo; line = text or (text, at, color, size)
    big(value, kicker, note, bg)    one big number
    bars(title, rows, bg, note)     calm bar chart; row = (label, value, text, at[, {color}])
    ledger(title, rows, bg, total)  list that writes in; row = (label, value, at[, color])
    board(items, bg="paper")        paper tabletop: pc(), strip(), title_(), prop()
    prop(name, x, y, h, at, rot)    drawn object / kit cut-out on a board (prop_envelope.png, vintage_open_book.png ...)
    mapscene(...)                   map with pins / highlights / routes (see docu/templates/README.md, Maps)
    spotlight(key, center, radius, label)
    title_card(kicker, title, bg)   the video's title card
    music_for(acts)                 one calm bed per act in this video's shuffled order

Colours: ACC (this video's accent), RUST, SAGE.
"""

import edl
from edl import clip, collage, cutout, depth, img, pc, photo, spot, stat, strip, title_   # noqa: F401

RUST, SAGE = "#B5523B", "#8DAA7B"
ACC = "#D8B26E"
THEME = "documentary"
CALM = ["02_Leaving_Home_Somber_Long_Bed.mp3", "03_Sovereign_Dark_Piano_Bed.mp3", "04_Sad_Trio_Somber_Piano_Cello.mp3",
        "11_Unanswered_Questions_Mystery.mp3", "12_Magic_Forest_Dark_Cello.mp3", "Mark Jubel - Efteraar.mp3",
        "Silent Tension Piano.mp3", "Slow Dramatic Ascent.mp3", "06_SCP-x6x_Hopes_Mysterious.mp3",
        "01_Metaphysik_Dramatic_Strings_Bed.mp3"]


def init():
    """call once after edl.setup()"""
    global ACC, THEME
    THEME = edl.P.get("theme", "documentary")
    if edl.V is not None:
        ACC = edl.V.accent


def _V():
    return edl.V


def ph(name, move=None, zoom=1.08, focus=None, **kw):
    V = _V()
    return photo(name, move=move or (V.move() if V else "in"), zoom=zoom, focus=focus, **kw)


def cl(i, **kw):
    kw.setdefault("zoom", 1.03)
    return clip(i, **kw)


def _overlay(scene, o):
    scene = dict(scene)
    scene["overlays"] = list(scene.get("overlays", [])) + [o]
    return scene


def place(scene, text, sub=None, at=0.6):
    o = dict(type="place", text=text, at=at)
    if sub:
        o["sub"] = sub
    return _overlay(scene, o)


def who(scene, name, role, at=0.6):
    return _overlay(scene, dict(type="doclower", name=name, role=role, at=at))


def fadein(scene, d=1.2):
    return _overlay(scene, dict(type="fadein", d=d))


def fadeout(scene, d=2.2):
    return _overlay(scene, dict(type="fadeout", d=d))


def heading(n, title, bg, sub=None, **kw):
    V = _V()
    kicker = V.kicker(n) if V else f"Chapter {n}"
    if THEME == "documentary":
        s = dict(type="doctitle", kicker=kicker, title=title, img=img(bg), move="in", zoom=1.08)
        if sub:
            s["sub"] = sub
    else:
        s = dict(type="chapter", n=n, kicker=kicker.upper(), title=title.upper(), img=img(bg), move="in", zoom=1.12)
    s.update(kw)
    return s


def title_card(kicker, title, bg, **kw):
    s = dict(type="doctitle", kicker=kicker, title=title, img=img(bg), move="in", zoom=1.08)
    s.update(kw)
    return s


def card(*lines, bg=None, dim=None, **kw):
    ls = []
    for ln in lines:
        if isinstance(ln, str):
            ls.append(dict(text=ln))
        else:
            d = dict(text=ln[0])
            if len(ln) > 1 and ln[1] is not None:
                d["at"] = ln[1]
            if len(ln) > 2 and ln[2]:
                d["color"] = ln[2]
            if len(ln) > 3 and ln[3]:
                d["size"] = ln[3]
            ls.append(d)
    V = _V()
    s = dict(type="textcard", lines=ls, dim=dim if dim is not None else (V["dim"] if V else 0.62))
    if bg:
        s["img"] = img(bg)
    s.update(kw)
    return s


def big(value, kicker, note="", bg=None, source=None, **kw):
    return stat(value, kicker, note, bg=bg, source=source, **kw)


def bars(title, rows, bg=None, note=None, source=None, **kw):
    s = dict(type="bars", title=title,
             bars=[dict(label=r[0], value=r[1], text=r[2], at=r[3], **(r[4] if len(r) > 4 else {})) for r in rows])
    if bg:
        s["img"] = img(bg)
    if note:
        s["note"] = note
    if source:
        s["source"] = source
    s.update(kw)
    return s


def ledger(title, rows, bg=None, total=None, **kw):
    items = []
    for r in rows:
        it = dict(label=r[0], value=r[1], at=r[2])
        if len(r) > 3 and r[3]:
            it["color"] = r[3]
        items.append(it)
    s = dict(type="ledgerlist", title=title, items=items, dim=0.84, gap=84, y0=260)
    if bg:
        s["img"] = img(bg)
    if total:
        s["total"] = total
    s.update(kw)
    return s


def board(items, bg="paper", **kw):
    for it in items:
        it.setdefault("from", "fade")
    return collage(items, bg=bg, z1=1.03, vignette=0.35, **kw)


def prop(name, x, y, h, at=0.1, rot=0.0, **kw):
    return dict(k="cut", img=cutout(name, red=False, keyline=0), x=x, y=y, h=h, at=at, rot=rot, **kw)


def mapscene(stops, pins=(), highlight=(), names=(), routes=(), dots=(), caption=None, caption_at=1.0, usa=True, **kw):
    """stops=[dict(at=0, lon, lat, scale), dict(at=.., lon, lat, scale, d=secs)]; pins=[dict(lon, lat, label, sub, at, side)]"""
    s = dict(type="map", stops=list(stops))
    if usa:
        s.update(detail="geo_hi.json", adminCountries=["USA"])
    for k, v in (("pins", pins), ("highlight", highlight), ("names", names), ("routes", routes), ("dots", dots)):
        if v:
            s[k] = list(v)
    if caption:
        s["overlays"] = [dict(type="caption", text=caption, at=caption_at)]
    s.update(kw)
    return s


def spotlight(name, center, radius, label=None, hit=0.8, **kw):
    kw.setdefault("side", "left")
    return spot(name, center=center, radius=radius, label=label, hit=hit, zoom=kw.pop("zoom", 1.08), **kw)


def music_for(acts, calm=None):
    """acts = [None, "cue of act 2", ...] -> music list for edl.main()"""
    V = _V()
    order = list(V["music"]) if V else list(CALM)
    if calm is None:
        calm = THEME == "documentary"
    beds = [t for t in order if t in CALM] if calm else order
    beds = beds or order or CALM
    return [dict(at=a, track=beds[i % len(beds)], db=0 if i else -1, lead=-1.0 if i else 0) for i, a in enumerate(acts)]


__all__ = ["ACC", "RUST", "SAGE", "init", "ph", "cl", "place", "who", "fadein", "fadeout", "heading", "title_card", "card",
           "big", "bars", "ledger", "board", "prop", "mapscene", "spotlight", "music_for", "pc", "strip", "title_", "depth",
           "img", "photo", "clip", "stat", "collage", "cutout", "spot"]
