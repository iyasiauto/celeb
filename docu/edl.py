"""
Shared edit-decision-list toolkit for docu projects.

A project calls `setup(...)` with its paths and look, declares its shots with `at(cue, scene)`
using the helpers below, and hands control to `main(music)`:

    python build.py plan | prep | stills [ids] | render [ids] | mix | final | all

Helpers register every picture they touch as a prep job, so `prep` prepares exactly what
the edit uses. `grade=None` means the project's default grade.
"""

import os
import sys
import json
import glob
import hashlib

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)

import prep                      # noqa: E402
import variety                   # noqa: E402
from timing import Timing        # noqa: E402

JOBS = []                        # prep jobs collected while the EDL is declared
E = []                           # (cue, scene) in order
CAT = []                         # the footage catalog
P = {}                           # project settings
V = None                         # this video's variety picks (variety.Picks) when setup(vary=...)


def setup(*, name, kit, footage, work, data, out, vo=None, theme="paper", grade="doc", grain=5.0,
          tail=4.8, image_dirs=None, music_floor_db=-12.5, music_duck_db=-9.0, sfx_gain=0.7, xfade=0.0,
          sfx_style="full", vary=None, vary_look=None):
    """Paths and look for one project. Call before declaring any shot."""
    global KIT, FOOT, WORK, ASSETS, SEGS, VO, SCRIPT, WORDS, OUT, IMG_DIRS, CUTS, VOX_TAIL
    KIT, FOOT, WORK, OUT = kit, footage, work, out
    # fonts shipped with the templates (docu/fonts, all OFL) join the kit's fonts once
    fdir = os.path.join(_HERE, "fonts")
    if os.path.isdir(fdir) and os.path.isdir(os.path.join(kit, "fonts")):
        import shutil
        for f in os.listdir(fdir):
            if not os.path.exists(os.path.join(kit, "fonts", f)):
                shutil.copy(os.path.join(fdir, f), os.path.join(kit, "fonts", f))
    ASSETS, SEGS = f"{work}/assets", f"{work}/segments"
    VO = vo or f"{work}/vo.mp3"
    SCRIPT, WORDS = f"{data}/script.txt", f"{data}/words.json"
    IMG_DIRS = image_dirs or [f"{footage}/images/approved", f"{work}/ind", f"{footage}/images/candidates"]
    CUTS = f"{kit}/cutouts"
    VOX_TAIL = tail
    CAT[:] = json.load(open(f"{data}/catalog_all.json"))
    if theme in ("almanac", "almanac2") and grade == "doc":
        grade = theme                     # each almanac edition's own print grade
    P.update(name=name, theme=theme, grade=grade, grain=grain, music_floor_db=music_floor_db,
             music_duck_db=music_duck_db, sfx_gain=sfx_gain, xfade=xfade, sfx_style=sfx_style, data=data)
    if vary is not None:
        # shuffle the look per video; remember what earlier videos used (see variety.py)
        global V
        proj = os.path.dirname(os.path.abspath(data))
        hist = variety.history(os.path.dirname(proj), exclude=proj)
        tracks = sorted(os.path.basename(t) for t in glob.glob(os.path.join(kit, "music", "*.mp3")))
        seed = variety.seed_for(name) if vary == "auto" else int(vary)
        v = variety.pick(seed, hist, tracks)
        used = set()
        for h in hist:
            used |= set(h.get("images", [])) | set(h.get("clips", []))
        V = variety.Picks(v, used)
        # the look shuffle (accent, fonts, grade, dissolve) suits the calm documentary; other themes keep their
        # own designed look and only use the asset rotation, unless vary_look=True
        look = (theme == "documentary") if vary_look is None else vary_look
        P.update(vary=v, vary_look=look)
        if look:
            P.update(grade=v["grade"], grain=v["grain"], xfade=v["xfade"] if xfade or theme == "documentary" else 0.0)


def at(cue, scene):
    E.append((cue, scene))


def _g(grade):
    return P.get("grade", "doc") if grade is None else grade

# ---------------------------------------------------------------- assets

def _src(name):
    if os.path.isabs(name):
        return name
    for base in IMG_DIRS:
        for ext in (".jpg", ".png", ".jpeg", ""):
            p = os.path.join(base, name + ext)
            if os.path.isfile(p):
                return p
    raise FileNotFoundError(name)


def img(name, grade=None, crop=None, cut=False, v=("blur",)):
    """A prepared picture; returns the file name scenes refer to."""
    grade = _g(grade)
    src = _src(name)
    tag = hashlib.md5(f"{grade}{crop}".encode()).hexdigest()[:4]
    key = f"{os.path.splitext(os.path.basename(src))[0]}_{grade}_{tag}"
    variants = set(v)
    if cut:
        variants |= {"soft"}
    JOBS.append(("img", src, key, grade, crop, cut, tuple(sorted(variants))))
    return key + ".jpg"


def cutout(name, halftone=False, keyline=6, red=True, height=1000):
    src = name if os.path.isabs(name) else (os.path.join(CUTS, name) if os.path.exists(os.path.join(CUTS, name)) else _src(name))
    key = "cut_" + hashlib.md5(f"{src}{halftone}{keyline}{red}{height}".encode()).hexdigest()[:8]
    JOBS.append(("cut", src, key, halftone, keyline, red, height))
    return key + ".png"


# ---------------------------------------------------------------- scenes

def photo(name, move="in", focus=None, zoom=None, grade=None, crop=None, fit=None, chip=None, lower=None,
          chip_at=0.5, dim=None, **kw):
    s = dict(type="photo", img=img(name, grade, crop), move=move)
    if focus: s["focus"] = focus
    if zoom: s["zoom"] = zoom
    if fit: s["fit"] = fit
    if dim: s["dim"] = dim
    ov = []
    if chip: ov.append(dict(type="chip", text=chip, at=chip_at))
    if lower: ov.append(dict(type="lower", name=lower[0], role=lower[1], at=lower[2] if len(lower) > 2 else 0.6))
    if ov: s["overlays"] = ov
    s.update(kw)
    return s


def clip(i, zoom=None, chip=None, chip_at=0.4, grade=None, skip=0.0, crop=None, lower=None, then=(), **kw):
    """A catalog shot; `then` appends further catalog shots when one is too short for its words."""
    c = CAT[i]
    src = os.path.join(FOOT, "source_video", c["video"])
    s = dict(type="clip", src=src, start=c["s"] + 0.15 + skip, end=c["e"] - 0.1, grade=_g(grade), cat=i)
    if then:
        s["more"] = [dict(src=os.path.join(FOOT, "source_video", CAT[j]["video"]), start=CAT[j]["s"] + 0.15,
                          end=CAT[j]["e"] - 0.1) for j in then]
    if zoom: s["zoom"] = zoom
    if crop: s["crop"] = crop
    ov = []
    if chip: ov.append(dict(type="chip", text=chip, at=chip_at))
    if lower: ov.append(dict(type="lower", name=lower[0], role=lower[1], at=0.5))
    if ov: s["overlays"] = ov
    s.update(kw)
    return s


def depth(name, subject, crop=None, grade=None, hit=0.6, lower=None, chip=None, move="in", focus=None, **kw):
    s = dict(type="depth", img=img(name, grade, crop, cut=True), subject=subject, hit=hit, move=move)
    if focus: s["focus"] = focus
    ov = []
    if lower: ov.append(dict(type="lower", name=lower[0], role=lower[1], at=lower[2] if len(lower) > 2 else hit + 0.6))
    if chip: ov.append(dict(type="chip", text=chip, at=hit + 0.6))
    if ov: s["overlays"] = ov
    s.update(kw)
    return s


def spot(name, center, radius, label=None, hit=0.7, grade=None, crop=None, side="right", zoom=1.2, **kw):
    s = dict(type="spotlight", img=img(name, grade, crop, v=("blur", "dim")), center=center, radius=radius,
             hit=hit, side=side, zoom=zoom)
    if label: s["label"] = label
    s.update(kw)
    return s


def words(items, bg=None, grade=None, dim=0.72, crop=None, **kw):
    s = dict(type="words", items=items)
    if bg: s["img"] = img(bg, grade, crop); s["dim"] = dim
    s.update(kw)
    return s


def W_(text, y=540, at=0.1, size=150, **kw):
    return dict(text=text, y=y, at=at, size=size, **kw)


def collage(items, bg="paper", **kw):
    return dict(type="collage", items=items, bg=bg, **kw)


def card(name, focus=(0.5, 0.5), zoom=1.3, height=940, grade="none", **kw):
    return dict(type="card", img=img(name, grade, v=()), focus=list(focus), zoom=zoom, height=height, **kw)


def stat(value, kicker, note="", bg=None, source=None, grade=None, **kw):
    s = dict(type="stat", value=value, kicker=kicker, note=note)
    if bg: s["img"] = img(bg, grade)
    if source: s["source"] = source
    s.update(kw)
    return s


def quote(text, who=None, bg=None, highlight=(), grade=None, crop=None, **kw):
    s = dict(type="quote", text=text, highlight=list(highlight))
    if who: s["who"] = who
    if bg: s["img"] = img(bg, grade, crop)
    s.update(kw)
    return s


def chapter(n, kicker, title, bg):
    return dict(type="chapter", n=n, kicker=kicker, title=title, img=img(bg), move="in", zoom=1.12)


def checklist(kicker, items, bg=None, **kw):
    s = dict(type="checklist", kicker=kicker, items=items)
    if bg: s["img"] = img(bg)
    s.update(kw)
    return s


def pc(name, x, y, w, rot=0.0, at=0.0, grade=None, crop=None, **kw):
    """photo card item for collages"""
    return dict(k="photo", img=img(name, grade, crop), x=x, y=y, w=w, rot=rot, at=at, **kw)


def strip(text, x, y, at, rot=0.0, **kw):
    return dict(k="strip", text=text, x=x, y=y, at=at, rot=rot, **kw)


def stamp(text, x, y, at, rot=-8, **kw):
    return dict(k="stamp", text=text, x=x, y=y, at=at, rot=rot, **kw)


def title_(text, x, y, at=0.1, size=120, **kw):
    return dict(k="title", text=text, x=x, y=y, at=at, size=size, **kw)



def music_plan(scenes, music):
    plan = []
    for m in music:
        t = 0.0 if m["at"] is None else next(s["t0"] for s in scenes if s["cue"] == m["at"]) + m.get("lead", 0)
        plan.append({"from": max(0.0, t), "track": m["track"], "db": m.get("db", 0)})
    return plan


def resolve(T, vo_dur):
    """Turn the cue list into timed scenes with ids, durations and resolved @phrases."""
    starts, idxs = [], []
    for cue, _ in E:
        if isinstance(cue, (int, float)):
            starts.append(float(cue)); idxs.append(T.cursor)
        else:
            i = T.find(cue)
            T.cursor = i
            starts.append(max(0.0, T.start[i] - 0.12))
            idxs.append(i)
    end = vo_dur + VOX_TAIL
    scenes = []
    for k, ((cue, sc), st, ti) in enumerate(zip(E, starts, idxs)):
        en = starts[k + 1] if k + 1 < len(E) else end
        dur = round(en - st, 3)
        if dur <= 0.2:
            raise ValueError(f"scene {k} ({cue!r}) has duration {dur}")
        s = json.loads(json.dumps(sc))

        def fix(o):
            if isinstance(o, dict):
                for kk, vv in list(o.items()):
                    if kk == "from_":
                        o["from"] = o.pop("from_")
                        continue
                    o[kk] = fix(vv)
                return o
            if isinstance(o, list):
                return [fix(x) for x in o]
            if isinstance(o, str) and o.startswith("@"):
                j = T.find(o[1:], after=ti)
                return round(max(0.0, T.start[j] - st - 0.05), 3)
            return o
        s = fix(s)
        s["id"] = f"s{k:03d}"
        # dissolves: every scene but the last renders a little longer and overlaps the next one
        xf = s.pop("xfade", None)
        if k + 1 < len(E):
            xf = P.get("xfade", 0.0) if xf is None else xf
            if xf:
                s["pad"] = round(float(xf), 3)
        s["t0"] = round(st, 3)
        s["duration"] = dur
        s["cue"] = cue if isinstance(cue, str) else f"{cue}"
        scenes.append(s)
    return scenes


def do_prep():
    prep.make_surfaces(ASSETS, KIT)
    from concurrent.futures import ThreadPoolExecutor
    # one job per key: a picture asked for plainly and as a depth pop gets both
    merged = {}
    for j in JOBS:
        if j[0] == "img":
            _, src, key, grade, crop, cut, variants = j
            if key in merged:
                m = merged[key]
                merged[key] = (m[0], m[1], m[2], m[3], m[4], m[5] or cut, tuple(sorted(set(m[6]) | set(variants))))
            else:
                merged[key] = j
        else:
            merged.setdefault(j[2], j)

    def run(j):
        if j[0] == "img":
            _, src, key, grade, crop, cut, variants = j
            prep.prepare_image(src, ASSETS, key, grade, crop, cut, variants)
        else:
            _, src, key, halftone, keyline, red, height = j
            prep.prepare_cutout(src, ASSETS, key, halftone=halftone, height=height, keyline=keyline, red=red)
    jobs = list(merged.values())
    with ThreadPoolExecutor(4) as ex:
        list(ex.map(run, [j for j in jobs if j[0] == "img" and not j[5]]))
    for j in [j for j in jobs if j[0] == "cut" or j[5]]:      # rembg jobs one at a time
        run(j)
    print(f"prepared {len(jobs)} assets")


def main(music=()):
    """music: [dict(at=cue or None, track=..., db=0, lead=0)] - one bed per act."""
    import subprocess
    import multiprocessing
    if multiprocessing.parent_process() is not None:
        return                         # a render worker re-importing build.py (Windows / macOS spawn): do nothing
    cmd = sys.argv[1] if len(sys.argv) > 1 else "plan"
    if cmd == "path":                  # where `final` writes the video (for pipeline scripts)
        print(os.path.join(OUT, P["name"] + ".mp4"))
        return
    T = Timing.load(SCRIPT, WORDS)
    vo_dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", VO],
                                  capture_output=True, text=True).stdout)
    scenes = resolve(T, vo_dur)
    os.makedirs(OUT, exist_ok=True)
    json.dump(scenes, open(f"{WORK}/scenes.json", "w"), indent=1, ensure_ascii=False)
    import render as _r
    cfg = {"kit": _r.file_uri(KIT), "assets": _r.file_uri(ASSETS), "theme": P["theme"], "grain": P["grain"]}
    if P.get("vary") and P.get("vary_look", True):
        cfg["vary"] = variety.engine_overrides(P["vary"])
    clips = sum(s["duration"] for s in scenes if s["type"] == "clip")
    total = sum(s["duration"] for s in scenes)
    print(f"{len(scenes)} scenes, {total:.1f}s, clips {clips:.1f}s ({100 * clips / total:.0f}%), alignment {T.matched:.0%}")
    # remember what this video used, so the next ones can avoid it
    imgs = sorted({os.path.splitext(os.path.basename(j[1]))[0] for j in JOBS if j[0] == "img"})
    clips = sorted({s["src"].split("/")[-1] for s in scenes if s["type"] == "clip"} |
                   {m["src"].split("/")[-1] for s in scenes if s["type"] == "clip" for m in s.get("more", [])})
    if P.get("vary"):
        json.dump(dict(name=P["name"], vary={k: v for k, v in P["vary"].items()}, images=imgs, clips=clips),
                  open(os.path.join(P["data"], "assets_used.json"), "w"), indent=0)
    if cmd in ("plan",):
        from collections import Counter
        if V is not None:
            again = [a for a in imgs + clips if a in V.used_before]
            vv = P["vary"]
            print(f"variety: accent={vv['accent']} fonts={vv['fonts']} kicker={vv['kicker']} grade={vv['grade']} "
                  f"grain={vv['grain']} xfade={vv['xfade']} moves={vv['moves']} place={vv['place']}")
            print(f"  reused from earlier videos: {len(again)} of {len(imgs) + len(clips)}" + (f"  e.g. {again[:8]}" if again else ""))
        print(Counter(s["type"] for s in scenes))
        for s in scenes:
            if s["type"] == "clip":
                avail = s["end"] - s["start"] + sum(m["end"] - m["start"] for m in s.get("more", []))
                if avail < s["duration"] * 0.5:
                    print(f"  WARN {s['id']} clip needs {s['duration']:.1f}s, has {avail:.1f}s")
        return
    if cmd in ("prep", "all"):
        do_prep()
    import render
    if cmd == "stills":
        only = sys.argv[2:] or None
        sel = [s for s in scenes if not only or s["id"] in only]
        paths = render.stills(sel, cfg, f"{WORK}/stills")
        print(len(paths), "stills")
    if cmd in ("render", "all"):
        only = sys.argv[2:] or None
        sel = [s for s in scenes if not only or s["id"] in only]
        if only:
            for s in sel:
                s["force"] = True
        fails = render.render_all(sel, SEGS, cfg, workers=int(os.environ.get("WORKERS", 4)))
        print("failures:", fails)
    if cmd in ("mix", "all"):
        import mix
        mix.build_mix(scenes, VO, KIT, f"{WORK}/mix.wav", vo_dur + VOX_TAIL, plan=music_plan(scenes, music),
                      music_floor_db=P["music_floor_db"], music_duck_db=P["music_duck_db"], sfx_gain=P["sfx_gain"],
                      sfx_style=P.get("sfx_style", "full"))
    if cmd in ("final", "all"):
        import mix
        if P.get("xfade"):
            render.concat_xfade(scenes, SEGS, f"{WORK}/video.mp4")
        else:
            render.concat(scenes, SEGS, f"{WORK}/video.mp4")
        out = os.path.join(OUT, P["name"] + ".mp4")
        mix.mux(f"{WORK}/video.mp4", f"{WORK}/mix.wav", out)
        print("final:", out)


