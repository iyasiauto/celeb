"""
frontier_import.py - bring Frontier's channel styles into the Docu kit as real Docu templates.

Frontier (the other studio) ships its channel styles as styles/<name>.json plus the code that draws them: the look
kits (assets/kits/<kit>.js, kits.py), the documentary graphics (docgfx.py), the motion graphics (motion.py) and the
footage frames (frames.py). This tool reads a Frontier folder and writes, for every style:

    templates/<id>/template.json      the Docu playbook: theme (fonts, palette, map), grade, devices with how often each
                                      is needed, audit limits, rules - so registry.py / the edit audit / Docu Studio
                                      treat it like any other template
    templates/<id>/scenes_<id>.js     Frontier's own page for this look, registered with docu/scenes_frontier.js, and
                                      one SCENES.<prefix>_<type> per graphic - the Docu engine draws Frontier's page
                                      frame by frame (nothing is re-written, so the look is Frontier's exactly)
    templates/<id>/frontier.json      what docu/frontier.py needs to write a shot list: scene types and lengths, the
                                      footage frame, sound marks, example fields per type
    templates/<id>/README.md          the devices, how the style is cut, where its footage comes from
    styles/<id>/style.json            the detailed style (Frontier's full style file kept under "frontier") + rules.md
    media/kit/frontier/...            the kit props and the frame grounds (hustle icons, chalkboard, chart, monitor ...)

    python docu/tools/frontier_import.py --frontier <Frontier folder>            every style
    python docu/tools/frontier_import.py --frontier <folder> --only dossier,news
    python docu/tools/frontier_import.py --frontier <folder> --list              what would be imported

Re-run it when Frontier changes; rules.md and README.md you edited are kept unless --force.
Previews and sample videos: python docu/tools/template_reel.py <id>.
"""

import argparse
import glob
import importlib
import json
import os
import re
import shutil
import sys

DOCU = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(DOCU)

# Frontier style -> Docu template id, a letter for the card, the scene-name prefix
IDS = {
    "dossier": ("dossier", "K"), "kinetic": ("kinetic", "L"), "atlas": ("atlas", "M"), "deep": ("deep", "N"),
    "news": ("news-frontline", "O"), "legend": ("legend", "P"), "hustle": ("hustle", "Q"),
    "documentary": ("frontier-documentary", "S"), "courtside": ("courtside", "T"), "avatar": ("ai-presenter", "U"),
    "hasidic": ("hasidic-frontier", "V"), "modern-homes": ("modern-homes", "W"), "jung": ("dark-psychology", "X"),
    "stories": ("stories-2d", "Y"),
}
KIT_PREFIX = {"frontline": "news"}          # kit name -> scene prefix (SCENES.news_newsbar)

# Docu's own scenes (photo captions, maps, lower thirds) speak in these font aliases: point them at the kit's faces
ALIAS_ROLES = {
    "serif": ["DMSerif", "Garamond", "Engr", "Rec"], "serif_i": ["GaramondI", "RecI", "Caveat"],
    "cond": ["Barlow", "Oswald", "Label"], "cond_b": ["BarlowB", "OswaldB", "LabelB"],
    "mono": ["Elite", "Mono", "Code"], "display": ["Anton", "Num"],
}


def _load_frontier(fdir):
    sys.path.insert(0, fdir)
    mods = {}
    for m in ("kits", "docgfx", "motion"):
        try:
            mods[m] = importlib.import_module(m)
        except Exception as e:            # noqa: BLE001
            print(f"  (frontier {m}.py not loaded: {type(e).__name__}: {str(e)[:120]})")
    return mods


def _font_roles(fonts):
    """the kit's faces sorted into roles, for the engine aliases"""
    roles = {}
    for fam, file, wt, st in fonts:
        f = file.lower()
        role = ("mono" if any(k in f for k in ("mono", "courier", "elite", "sharetech", "vt323")) else
                "serif_i" if ("italic" in f and any(k in f for k in ("garamond", "lora", "playfair", "crimson", "baskerville"))) else
                "serif" if any(k in f for k in ("garamond", "lora", "playfair", "dmserif", "cinzel", "crimson", "baskerville", "zilla")) else
                "cond_b" if any(k in f for k in ("condensed-bold", "barlowcondensed-bold", "oswald", "bebas")) else
                "cond" if any(k in f for k in ("condensed", "barlow")) else
                "display" if any(k in f for k in ("black", "archivo", "anton", "bangers", "lilita", "extrabold", "stencil")) else
                "body")
        roles.setdefault(role, file)
    roles.setdefault("serif", roles.get("display") or "EB-Garamond.ttf")
    roles.setdefault("serif_i", roles.get("serif"))
    roles.setdefault("cond", roles.get("cond_b") or "Roboto-Condensed.ttf")
    roles.setdefault("cond_b", roles.get("cond") or "BarlowCondensed-Bold.ttf")
    roles.setdefault("mono", "KodeMono.ttf")
    roles.setdefault("display", roles.get("cond_b"))
    return roles


def _theme_def(fonts, pal, accent, dark=True):
    roles = _font_roles(fonts)
    fmap = {}
    for role, names in ALIAS_ROLES.items():
        for n in names:
            fmap[n] = roles[role]
    a = (accent or ["#E3B25B"])
    gold = a[0]
    red = pal.get("red") or (a[3] if len(a) > 3 else "#C4553F")
    ink = "#0D0C0A" if dark else "#F3EEE4"
    cream = pal.get("paper") or pal.get("cream") or pal.get("ink") or "#F3EEE4"
    if not cream.startswith("#") or cream.upper() in ("#FFFFFF",):
        cream = "#F3EEE4"
    rgb = lambda h: ",".join(str(int(h.lstrip("#")[i:i + 2], 16)) for i in (0, 2, 4))
    return {
        "fonts": fmap,
        "pal": {"ink": ink, "cream": cream, "gold": gold, "mustard": gold, "red": red,
                "cyan": pal.get("cyan") or pal.get("blue") or "#8FB3D9", "green": pal.get("green") or "#6E9B7B",
                "paperWash": "13,12,10", "paperEdge": "rgba(0,0,0,.6)"},
        "grounds": {"paper": "paper_tan.jpg", "map": "paper_map.jpg", "cork": "studio_dark.jpg", "parchment": "parchment.jpg"},
        "map": {"bg0": "#16140F", "bg1": "#0B0A08", "sea": "#0F0E0B", "rim": "rgba(243,238,228,.22)",
                "grat": "rgba(243,238,228,.04)", "land": "#24211B", "border": "rgba(243,238,228,.32)", "admin": "243,238,228",
                "hi": rgb(gold), "hiA": 0.3, "text": "#F3EEE4", "sub": "#A39C8E", "dot": gold, "dotText": "#F3EEE4",
                "name": "rgba(243,238,228,.6)", "shadow": "rgba(8,7,6,.95)", "pin": "dot", "route": gold,
                "hiLine": f"rgba({rgb(gold)},A)"},
    }


def _js_string(s):
    return json.dumps(s, ensure_ascii=False).replace("</", "<\\/")


def _descriptions(prompt):
    """{type: one-line use} from a kit's prompt text ("alert = a real notice ..." clauses)"""
    text = " ".join(l.strip() for l in prompt.splitlines() if not l.strip().startswith("{") and not l.strip().startswith("- graphic"))
    out = {}
    for m in re.finditer(r"(?:^|;\s*|\.\s+)([a-z0-9_]+)\s*=\s*(.+?)(?=;\s*[a-z0-9_]+\s*=|$)", text):
        out[m.group(1)] = m.group(2).strip().rstrip(";").strip()
    return out


def _examples(prompt):
    out = {}
    for line in prompt.splitlines():
        line = line.strip()
        if line.startswith("{"):
            try:
                raw = json.loads(line)
            except ValueError:
                continue
            t = raw.get("type")
            if t:
                out[t] = {k: v for k, v in raw.items() if k not in ("tool", "cue", "words", "type")}
    return out


DOC_USES = {
    "dateline": "a new place or time begins: PLACE, a gold rule, the date (over the blurred real picture)",
    "number": "one figure that matters, counting up, its unit, what it means and its source",
    "chart": "a comparison with real numbers: 2-6 bars on warm paper, the one that matters highlighted, source under",
    "timeline": "3-5 dated events on a line the camera travels along",
    "quote": "a documented quote, word by word, with who said it and when",
    "pivot": "one short serif line where the story turns",
    "question": "the question the next part answers",
    "card": "a short card of key lines, the words that matter highlighted",
    "step": "one numbered step of a process",
    "social": "a follow / unfollow between two public accounts",
    "chapter": "the chapter card: number, kicker, title",
    "place": "a place name card (city, region)",
    "pull": "a real sentence from a real article with outlet, byline and date",
    "table": "a small table of real figures with its source",
}
DOC_MIN = {"dateline": 1.5, "number": 1.2, "chart": 0.6, "timeline": 0.6, "quote": 0.5, "pivot": 0.8, "question": 0.5,
           "card": 0.3, "step": 0, "social": 0, "chapter": 3, "place": 1, "pull": 0.6, "table": 0.4}


def _kit_page(kits, kit):
    js = open(os.path.join(os.path.dirname(kits.__file__), "assets", "kits", f"{kit}.js"), encoding="utf-8").read()
    return kits.PAGE.replace("__KITJS__", js)


def _doc_page(docgfx, look):
    serif = str(look.get("title_font") or "")
    serif_css = (f"{serif},'Doc Serif',Georgia,serif" if serif and "garamond" not in serif.lower()
                 and "newsreader" not in serif.lower() else "'Doc Serif','EB Garamond',Georgia,serif")
    doc = look.get("docgfx") if isinstance(look.get("docgfx"), dict) else {}
    if doc.get("serif"):
        serif_css = f"{doc['serif']},'Doc Serif',Georgia,serif"
    display_css = (f"{serif},'Doc Display','Inter Display Black',sans-serif" if serif else "'Doc Display','Inter Display Black',sans-serif")
    return docgfx.PAGE.replace("__SERIF__", serif_css).replace("__DISPLAY__", display_css)


DOC_FONTS = [["Doc Serif", "EB-Garamond.ttf", "400 800", "normal"], ["Doc Serif", "EB-Garamond-Italic.ttf", "400 800", "italic"],
             ["Doc Sans", "Roboto-Condensed.ttf", "100 900", "normal"], ["Doc Sans", "Roboto-Condensed-Italic.ttf", "100 900", "italic"],
             ["Doc Display", "InterDisplay-Black.ttf", "100 900", "normal"], ["Doc Body", "Inter-Bold.ttf", "700", "normal"],
             ["Doc Body", "Inter-SemiBold.ttf", "600", "normal"]]


def _title_fonts(look):
    """the style's own title face (look.title_font) as @font-face entries, when the kit folder has it"""
    out = []
    fdir = os.path.join(ROOT, "media", "kit", "fonts")
    for fam in re.findall(r"'([^']+)'", str(look.get("title_font") or "")):
        cand = fam.replace(" ", "")
        for f in (f"{cand}.ttf", fam.replace(" ", "-") + ".ttf", re.sub(r"(Black|Bold|ExtraBold|SemiBold)$", r"-\1", cand) + ".ttf"):
            if os.path.exists(os.path.join(fdir, f)):
                out.append([fam, f, "100 1000", "normal"])
                break
    return out


def _copy_assets(fdir, kit_dir):
    src = os.path.join(fdir, "assets", "kits")
    dst = os.path.join(kit_dir, "frontier")
    n = 0
    for p in glob.glob(os.path.join(src, "**", "*"), recursive=True):
        if os.path.isdir(p) or not re.search(r"\.(png|jpe?g|json)$", p, re.I) or "_raw." in p:
            continue
        rel = os.path.relpath(p, src)
        q = os.path.join(dst, rel)
        if os.path.exists(q) and os.path.getsize(q) == os.path.getsize(p):
            continue
        os.makedirs(os.path.dirname(q), exist_ok=True)
        shutil.copy2(p, q)
        n += 1
    return n


MG_USES = {
    "title": "a title card for the idea of the moment (title + subtitle)", "stat": "one number that matters, big, with a line",
    "bars": "2-6 bars compared (items: label, value)", "crowd": "a crowd of people filling in, some highlighted (count, highlight)",
    "flow": "an idea moving through 2-4 steps with icons and arrows", "cards": "2-4 cards with an icon, a label and a line",
    "checklist": "2-5 items ticked one by one", "compare": "two sides, before / after or this / that",
    "steps": "2-5 numbered steps", "warning": "a warning sign with one line", "reveal": "items revealed one after another",
    "image": "a picture with a caption", "typing": "a line typed out", "collage": "paper stickers and cut-outs around a title",
    "photonote": "a photo with a handwritten note", "scatter": "cut-outs scattered around a word", "pillars": "2-4 pillars of an idea",
    "opener": "the opening card of the video", "strikelist": "a list where items are struck through", "icongrid": "a grid of icons",
    "quotemark": "a short quote in big quote marks", "deckfan": "cards fanned out like a deck", "timeline": "3-5 dated steps",
    "splitreveal": "a split screen revealing two sides",
}
MG_MIN = {"title": 2, "opener": 0.3, "stat": 1, "bars": 0.6, "flow": 0.6, "cards": 0.6, "checklist": 0.5, "compare": 0.5,
          "quotemark": 0.5, "timeline": 0.4, "steps": 0.4}
MG_EX = {
    "title": {"title": "The shadow you refuse to see", "subtitle": "and why it follows you"},
    "stat": {"title": "Most people never notice", "value": "7", "subtitle": "out of ten repeat the same pattern"},
    "bars": {"title": "Where the pressure lands", "items": [{"label": "Work", "value": 5}, {"label": "Love", "value": 3},
                                                          {"label": "Money", "value": 4}]},
    "crowd": {"title": "Most people feel it", "count": 60, "highlight": 22, "subtitle": "but only a few know why"},
    "flow": {"title": "How it moves", "items": [{"label": "Trigger", "icon": "bolt"}, {"label": "You", "icon": "person"},
                                                 {"label": "Reaction", "icon": "fire"}]},
    "cards": {"title": "Three signs", "items": [{"label": "Projection", "text": "You see it in others", "icon": "eye"},
                                                  {"label": "Denial", "text": "You call it their fault", "icon": "shield"},
                                                  {"label": "Return", "text": "It comes back stronger", "icon": "clock"}]},
    "checklist": {"title": "Before you react", "items": [{"label": "Name the feeling"}, {"label": "Ask where it started"},
                                                          {"label": "Wait one day"}]},
    "compare": {"title": "Persona and shadow", "items": [{"label": "Persona", "text": "The face you show"},
                                                          {"label": "Shadow", "text": "The part you hide"}]},
    "quotemark": {"title": "What you resist persists.", "subtitle": "Carl Jung"},
    "timeline": {"title": "How it builds", "items": [{"label": "Childhood", "text": "a rule is learned"},
                                                      {"label": "Youth", "text": "it is hidden"}, {"label": "Adult", "text": "it returns"}]},
    "warning": {"title": "Do not ignore it", "subtitle": "it grows in the dark"},
    "steps": {"title": "Three steps", "items": [{"label": "Notice", "text": "what repeats"}, {"label": "Own", "text": "your part"},
                                                 {"label": "Change", "text": "one habit"}]},
}


def _motion_pages(motion, sname, look):
    """Frontier's motion-graphics page, one per skin of the style, with the scene and the fonts left as placeholders"""
    if look.get("title_font"):
        motion.BRAND[sname] = {"title_font": look["title_font"], "title_weight": str(look.get("title_weight", "900")),
                               "accent": look.get("accent") or ["#E8A33D"], "warn": look.get("warn", "#C4553F"),
                               "good": look.get("good", "#2F8F83")}
    skins = [k for k in (look.get("skins") or ["paper", "clean"]) if k in motion.SKINS] or ["paper"]
    pages = {}
    real_dumps, real_fonts = motion.json.dumps, motion._bundled_font_css
    try:
        motion._bundled_font_css = lambda: "__FONTS__"
        motion.json.dumps = lambda o, *a, **k: ("__SCENE__" if isinstance(o, dict) and o.get("__sentinel__")
                                                 else real_dumps(o, *a, **k))
        for sk in dict.fromkeys(skins):
            html = motion.build_html({"template": "title", "skin": sk, "brand": sname, "__sentinel__": 1, "items": []})
            fams = set(re.findall(r"'([A-Z][A-Za-z ]+)'", html))
            fonts = []
            for f in sorted(glob.glob(os.path.join(ROOT, "media", "kit", "fonts", "*.ttf"))):
                fam = re.sub(r"(?<=[a-z])(?=[A-Z])", " ", os.path.basename(f)[:-4]).replace("-", " ")
                if fam in fams:
                    fonts.append([fam, os.path.basename(f), "1 1000", "normal"])
            pages[sk] = (html, fonts)
    finally:
        motion.json.dumps, motion._bundled_font_css = real_dumps, real_fonts
    return skins, pages


def _motion_ground(look):
    g = (look.get("ground") or "").strip()
    if not g:
        return ""
    if os.path.exists(os.path.join(ROOT, "media", "kit", g)):       # Frontier's assets/textures/... = the kit's textures/...
        return "kit:" + g
    return f"kit:frontier/grounds/{os.path.basename(g)}"


def _motion_assets(fdir, kit_dir, look):
    dst = os.path.join(kit_dir, "frontier")
    os.makedirs(os.path.join(dst, "grounds"), exist_ok=True)
    for src, q in [(os.path.join(fdir, "assets", "vintage_old_paper_background.jpg"), os.path.join(dst, "vintage_old_paper_background.jpg")),
                   (os.path.join(fdir, "assets", (look.get("ground") or "").strip()), os.path.join(dst, "grounds", os.path.basename((look.get("ground") or "").strip())))]:
        if os.path.isfile(src) and not os.path.exists(q):
            shutil.copy2(src, q)
    alt = os.path.join(kit_dir, "vintage_old_paper_background.jpg")
    if not os.path.exists(os.path.join(dst, "vintage_old_paper_background.jpg")) and os.path.exists(alt):
        shutil.copy2(alt, os.path.join(dst, "vintage_old_paper_background.jpg"))


def _audit(pacing, kind):
    every = float(pacing.get("graphic_every_min") or 0.7)
    gpm = round(min(2.4, max(0.5, 0.85 / max(0.25, every))), 1)
    return {"clip_share": [0.2, 0.75], "graphics_per_min": gpm, "max_gap_s": int(min(75, max(30, every * 60 * 1.6))),
            "max_plain_run": 8, "chapter_every_s": 210, "min_distinct_devices": 5 if kind != "motion" else 4,
            "sfx_per_min": 1.0}


def _sanitise(sty):
    """a style file as it may travel with the kit: no account-bound ids (a cloned voice, a private asset library)"""
    sty = json.loads(json.dumps(sty))
    v = sty.get("voice")
    if isinstance(v, dict):
        for k in ("voice_id", "voice_name", "wavespeed_voice"):
            if k in v:
                v[k] = ""
        v["note"] = "Pick the narrator in Docu Studio (FameSpeak) or put your own voice id here."
    al = sty.get("asset_library")
    if isinstance(al, dict):
        sty["asset_library"] = {k: v for k, v in al.items() if k not in ("topic", "folder", "drive", "id", "path")}
    return sty


def build(fdir, mods, sname, sty, force=False, kit_dir=None):
    sty = _sanitise(sty)
    tid, letter = IDS.get(sname, (sname, "Z"))
    look = sty.get("look") or {}
    pacing = sty.get("pacing") or {}
    kits, docgfx = mods.get("kits"), mods.get("docgfx")
    kit = kits.kit_of(look) if kits else ""
    graphics = str(look.get("graphics") or "").lower()
    kind = "kit" if kit else ("docgfx" if graphics == "documentary" or docgfx and graphics != "" else "motion")
    if graphics in ("", "none") and not kit:
        kind = "motion"
    tdir = os.path.join(ROOT, "templates", tid)
    sdir = os.path.join(ROOT, "styles", tid)
    os.makedirs(tdir, exist_ok=True)
    os.makedirs(sdir, exist_ok=True)
    cinema = look.get("cinema") or {}
    frame = cinema.get("frame") if cinema.get("frame") in ("blurfill", "print", "page", "stage", "crt", "monitor", "news",
                                                            "paper", "player", "board") else None
    accent = look.get("accent") or ["#E3B25B"]
    pages, scenes, devices, fj_types = [], [], [], {}

    if kind == "kit":
        K = kits.KITS[kit]
        prefix = KIT_PREFIX.get(kit, kit)
        pal = dict(K["palette"])
        if accent:
            pal.setdefault("accent", accent[0])
        fonts = [list(f) for f in K["fonts"]]
        defaults = {}
        if kit == "kinetic":
            defaults = {"board": {"board": "kit:frontier/frames/gen_sketchboard.jpg"}, "doodle": {"board": "kit:frontier/frames/gen_sketchboard.jpg"}}
        if kit == "atlas":
            defaults = {"stamp": {"wall": "kit:frontier/frames/gen_titlewall.jpg"}}
        if kit == "hustle":
            defaults = {"icon3d": {"prop": "kit:frontier/hustle/{icon}.png"}, "moneyrain": {"bill": "kit:frontier/hustle/bill.png"},
                        "counter": {"stack": "kit:frontier/hustle/stack.png"}}
        pages.append((kit, _kit_page(kits, kit), fonts, pal, defaults, ""))
        uses, ex = _descriptions(K["prompt"]), _examples(K["prompt"])
        over = set(getattr(kits, "CAPTIONED", ()))
        heading = {"dossier": "title_gold", "kinetic": "bigword", "atlas": "stamp", "deep": "stencil", "frontline": "ticker",
                   "legend": "chapter", "hustle": "corner"}.get(kit)
        for ty, dur in K["types"].items():
            scenes.append((f"{prefix}_{ty}", kit, ty))
            fam = "heading" if ty == heading else ("over-footage" if ty in over else "graphic")
            devices.append({"type": f"{prefix}_{ty}", "family": fam,
                            "min_per_10min": 3 if ty == heading else (1.0 if ty not in over else 1.5),
                            "use": (uses.get(ty) or ty) + (" (can also sit on a clip: overlay frontier)" if ty in over else "")})
            fj_types[ty] = {"scene": f"{prefix}_{ty}", "page": kit, "seconds": dur, "example": ex.get(ty, {}), "over_footage": ty in over}
        dark = True
    elif kind == "motion" and mods.get("motion"):
        # motion graphics (the original Frontier look): one page per skin the style rotates through
        motion = mods["motion"]
        prefix = "mg"
        skins, mpages = _motion_pages(motion, sname, look)
        for sk, (html, fonts) in mpages.items():
            pages.append((f"mg_{tid.replace('-', '_')}_{sk}", html, fonts, None, {}, ""))
        uses = MG_USES
        for ty in motion.TEMPLATES:
            if ty in ("subscribe", "introcap", "comment"):
                continue
            scenes.append((f"{prefix}_{ty}", pages[0][0], ty))
            devices.append({"type": f"{prefix}_{ty}", "family": "heading" if ty in ("opener", "title") else "graphic",
                            "min_per_10min": MG_MIN.get(ty, 0.3), "use": uses.get(ty, ty)})
            fj_types[ty] = {"scene": f"{prefix}_{ty}", "page": pages[0][0], "seconds": 6.0, "example": MG_EX.get(ty, {}),
                            "over_footage": False}
        pal = {"ink": "#F4EDDF"}
        dark = True
        _motion_assets(fdir, kit_dir, look)
    else:
        # documentary graphics: Frontier's docgfx page in this style's serif / display face and accent
        prefix = "doc"
        page_id = f"doc_{tid.replace('-', '_')}"
        fonts = DOC_FONTS + _title_fonts(look)
        vhs = str(((look.get("docgfx") or {}) if isinstance(look.get("docgfx"), dict) else {}).get("skin") or "").lower() == "vhs"
        defaults = {"*": {"ink": "#F3EEE4", "soft": "rgba(243,238,228,.72)", "accent": accent[0], "vhs": vhs},
                    "chart": {"paper": True}}
        css = "#ground{filter:blur(16px) brightness(.5) saturate(.85)}"
        pages.append((page_id, _doc_page(docgfx, look), fonts, None, defaults, css))
        for ty in docgfx.TYPES:
            scenes.append((f"{prefix}_{ty}", page_id, ty))
            devices.append({"type": f"{prefix}_{ty}", "family": "heading" if ty == "chapter" else "graphic",
                            "min_per_10min": DOC_MIN.get(ty, 0.3), "use": DOC_USES.get(ty, ty)})
            ex = next((dict(s) for s in docgfx.SAMPLES if s.get("type") == ty), {})
            ex.pop("type", None)
            fj_types[ty] = {"scene": f"{prefix}_{ty}", "page": page_id, "seconds": docgfx.LENGTH.get(ty, 6.0), "example": ex,
                            "over_footage": ty in ("dateline", "place", "pivot", "question")}
        pal = {"ink": "#F3EEE4"}
        dark = True
        kind = "docgfx"

    # Docu's own scenes the style also uses (in its palette and fonts)
    feats = set((sty.get("features") or {}).get("on") or [])
    extra = [("map", "map", 0.6 if "maps" in feats else 0.2, "where it happens (the template's map colours)"),
             ("spotlight", "photo", 0.8 if "spotlight" in feats else 0.2, "a real photo of a person named, in a pool of light"),
             ("depth", "photo", 0.4 if "depth" in feats else 0, "a 2.5D push into a still")]
    for t, fam, mn, use in extra:
        devices.append({"type": t, "family": fam, "min_per_10min": mn, "use": use})

    # scenes file
    lines = [f"/* scenes_{tid}.js - {sty.get('label') or sty.get('name')}: Frontier's own graphics, drawn by the Docu engine",
             f"   (docu/scenes_frontier.js). Generated by docu/tools/frontier_import.py from Frontier's styles/{sname}.json -",
             "   edit the Frontier source and re-import rather than this file. */", '"use strict";']
    for pid, html, fonts, pal_, defaults, css in pages:
        d = {"fonts": fonts, "palette": pal_, "defaults": defaults, "css": css}
        lines.append(f"FRONTIER.page({json.dumps(pid)}, Object.assign({json.dumps(d, ensure_ascii=False)}, {{html: {_js_string(html)}}}));")
    for name, pid, ty in scenes:
        lines.append(f"SCENES.{name} = FRONTIER.scene({json.dumps(pid)}, {json.dumps(ty)});")
    open(os.path.join(tdir, f"scenes_{tid}.js"), "w", encoding="utf-8").write("\n".join(lines) + "\n")

    label = sty.get("label") or sty.get("name") or tid
    name = re.split(r"\s+[—-]\s+", label)[0].strip()
    name = name.title() if name.isupper() else name
    best = re.split(r"\s+[—-]\s+", label, maxsplit=1)[1] if re.search(r"\s+[—-]\s+", label) else (sty.get("tagline") or "")
    grade = look.get("footage_grade") or "eq=saturation=0.9:contrast=1.04"
    tj = {
        "id": tid, "name": name, "version": 1, "source": f"Frontier styles/{sname}.json",
        "theme": tid, "grade": grade, "grain": 1.2 if kind == "kit" else 1.0,
        "xfade": 0.0 if kind == "kit" and kit in ("kinetic", "hustle", "atlas") else 0.45,
        "sfx_style": "full",
        "best_for": best, "look": sty.get("description", ""),
        "tagline": sty.get("tagline", ""),
        "examples": [f"templates/{tid}/demo_build.py"],
        "starter": f"templates/{tid}/README.md",
        "preview_dir": f"templates/{tid}/previews", "preview_sheet": f"templates/{tid}/previews/sheet.jpg",
        "scene_files": [f"scenes_{tid}.js"],
        "requires": ["docu/scenes_frontier.js"],
        "theme_def": _theme_def(pages[0][2] if kind == "kit" else DOC_FONTS, pal, accent, dark),
        "audit": _audit(pacing, kind),
        "devices": devices,
        "also_available": ["photo", "clip", "map", "depth", "spotlight"],
        "frontier": {"style": sname, "kind": kind, "kit": kit, "frame": frame,
                     "frame_every": int(cinema.get("frame_every") or (1 if cinema.get("frame_all") else 2)) if frame else 0},
        "rules": [r for r in [
            "Every graphic shows a real fact the voice gives at that moment (a name, a date, a place, a figure, a quote) - "
            "times come from the word timing, never before the narrator says it.",
            f"Footage: {'every ' + str(int(cinema.get('frame_every') or 2)) + '-th shot sits in the ' + frame + ' frame (frame=' + repr(frame) + '); ' if frame else ''}"
            "clips under 5 s, chained when a line is longer; no talking heads, influencers or logos (QC).",
            (pacing.get("hook_notes") or "").strip(),
            (pacing.get("body_notes") or "").strip(),
            (look.get("options_note") or "").strip(),
        ] if r],
        "qc_mode": "faceless",
        "guide": f"templates/{tid}/README.md",
    }
    if look.get("captions"):
        # the channel's burned-in captions (docu/captions.py at `final`; DOCU_CAPTIONS=0 turns them off)
        tj["captions"] = dict(look["captions"])
        if look.get("caption_accent"):
            tj["caption_accent"] = look["caption_accent"]
    json.dump(tj, open(os.path.join(tdir, "template.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)

    # what docu/frontier.py needs
    fj = {"template": tid, "style": sname, "kind": kind, "kit": kit, "prefix": prefix, "frame": frame,
          "frame_every": tj["frontier"]["frame_every"], "types": fj_types}
    if kind == "motion":
        motion = mods["motion"]
        fj.update(skins=skins, pages={sk: f"mg_{tid.replace('-', '_')}_{sk}" for sk in mpages}, icons=motion.ICONS,
                  icon_rotation=motion.ICON_ROTATION, fa_aliases=getattr(motion, "_FA_ALIASES", {}),
                  ground=_motion_ground(look), paper_bg="kit:frontier/vintage_old_paper_background.jpg",
                  dark=bool(look.get("dark") or any(k in str(skins) for k in ("dark", "noir", "glass", "astro"))))
    json.dump(fj, open(os.path.join(tdir, "frontier.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)

    # README
    rp = os.path.join(tdir, "README.md")
    if force or not os.path.exists(rp):
        rows = "\n".join(f"| `{d['type']}` | {d['use']} |" for d in devices)
        ex_t, ex_f = next(iter(fj_types.items()))
        open(rp, "w", encoding="utf-8").write(f"""# {name} — {best}

{sty.get('description', '')}

*{sty.get('tagline', '')}*

Imported from Frontier (`styles/{sname}.json`) by `docu/tools/frontier_import.py`: the graphics are Frontier's own
{'look kit `' + kit + '`' if kind == 'kit' else 'documentary graphics (docgfx)'} drawn by the Docu engine, so a video made here looks like the
Frontier channel - and goes through Docu's QC, edit audit and final QC like every other template.

Preview: `templates/{tid}/previews/sheet.jpg` · sample: `styles/{tid}/sample.mp4` · worked example: `templates/{tid}/demo_build.py`

## Devices

| Device | Use |
|---|---|
{rows}
{'| frame `' + frame + '` | footage treatment: every ' + str(tj['frontier']['frame_every']) + '-th shot (F.framed(scene)) |' if frame else ''}

## Writing a shot list

```python
import frontier
F = frontier.Template("{tid}")
at(cue, F.g("{ex_t}", **{json.dumps(ex_f['example'], ensure_ascii=False)[:300]}))     # a graphic, its sounds included
at(cue, F.framed(clip(12)))                                     # footage in the {frame or 'plain'} frame
at(cue, clip(14, overlays=[F.over("{next((t for t, v in fj_types.items() if v['over_footage']), ex_t)}", at=0.4, ...)]))   # a graphic over footage
```

## How it is cut

""" + "\n".join(f"- {r}" for r in tj["rules"]) + "\n")

    # the style folder: everything Frontier knows about the channel + the Docu fields
    st = {
        "name": name, "label": label, "letter": letter, "template": tid, "theme": tid,
        "blurb": sty.get("description", ""), "tagline": sty.get("tagline", ""), "points": sty.get("points", []),
        "best_for": best, "example": None, "rules": "rules.md", "preview": "preview.jpg", "sample": "sample.mp4",
        "sfx": tj["sfx_style"], "xfade": tj["xfade"],
        "look": {"accent": accent, "title_font": look.get("title_font"), "grade": grade,
                 "captions": look.get("captions"), "labels": look.get("labels"), "footage_frame": frame,
                 "frame_every": tj["frontier"]["frame_every"], "fonts": pages[0][2], "palette": pal},
        "voice": sty.get("voice"), "pacing": pacing, "features": sty.get("features"),
        "overrides": {}, "devices": {}, "audit": {},
        "frontier": sty,
    }
    json.dump(st, open(os.path.join(sdir, "style.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    rp = os.path.join(sdir, "rules.md")
    if force or not os.path.exists(rp):
        open(rp, "w", encoding="utf-8").write(f"# {name} — how it is edited\n\n" + "\n".join(f"- {r}" for r in tj["rules"]) + "\n")
    return tid, kind, len(scenes)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--frontier", required=True, help="the Frontier folder (with styles/ and assets/kits/)")
    ap.add_argument("--only", default="", help="comma list of Frontier style names")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--force", action="store_true", help="rewrite README.md / rules.md too")
    ap.add_argument("--kit", default=os.path.join(ROOT, "media", "kit"), help="the kit folder for props and grounds")
    a = ap.parse_args()
    fdir = os.path.abspath(a.frontier)
    files = sorted(glob.glob(os.path.join(fdir, "styles", "*.json")))
    files = [f for f in files if not os.path.basename(f).startswith("_")]
    only = {x.strip() for x in a.only.split(",") if x.strip()}
    if only:
        files = [f for f in files if os.path.basename(f)[:-5] in only]
    if a.list:
        for f in files:
            n = os.path.basename(f)[:-5]
            print(f"{n:14s} -> templates/{IDS.get(n, (n,))[0]}")
        return
    mods = _load_frontier(fdir)
    print(f"props / grounds copied: {_copy_assets(fdir, a.kit)}")
    for f in files:
        n = os.path.basename(f)[:-5]
        sty = json.load(open(f, encoding="utf-8"))
        tid, kind, k = build(fdir, mods, n, sty, a.force, a.kit)
        print(f"{n:14s} -> templates/{tid:22s} {kind:7s} {k} scene types")


if __name__ == "__main__":
    main()
