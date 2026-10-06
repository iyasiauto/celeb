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


PB = {}                          # the template / style playbook (docu/registry.py)


def _pin(proj_dir, pb, niche, footage):
    """one video = one template (+ style) + one niche, written once, checked on every run"""
    p = os.path.join(proj_dir, "project.json")
    want = dict(template=pb.get("id"), style=pb.get("style"), niche=niche or os.environ.get("DOCU_NICHE"))
    if os.environ.get("DOCU_TOPIC"):
        want["topic"] = os.environ["DOCU_TOPIC"]
    if os.path.exists(p):
        have = json.load(open(p, encoding="utf-8"))
        clash = [k for k in ("template", "style", "niche") if have.get(k) and want.get(k) and have[k] != want[k]]
        if clash and os.environ.get("DOCU_REPIN") != "1":
            raise SystemExit(f"\n*** {os.path.basename(proj_dir)} is pinned to " +
                             ", ".join(f"{k}={have[k]!r}" for k in clash) + " but this run asks for " +
                             ", ".join(f"{k}={want[k]!r}" for k in clash) +
                             f".\n    One video keeps one template and one niche. Start a new project for a different one, or\n"
                             f"    edit {p} on purpose (DOCU_REPIN=1 rewrites it).\n")
        if not clash:
            return
    import time
    want.update(footage=os.path.abspath(footage), pinned=time.strftime("%Y-%m-%d %H:%M"))
    os.makedirs(proj_dir, exist_ok=True)
    json.dump(want, open(p, "w", encoding="utf-8"), indent=1)


def _niche_topic(proj_dir, pinned):
    """what the niche is about (QC judges relevance against it): DOCU_TOPIC, the pinned project, or the
    workspace's niche.json found above the project - never just the video's title"""
    t = os.environ.get("DOCU_TOPIC") or pinned.get("topic")
    d = proj_dir
    for _ in range(4):
        if t:
            break
        d = os.path.dirname(d)
        nj = os.path.join(d, "niche.json")
        if os.path.isfile(nj):
            try:
                t = json.load(open(nj, encoding="utf-8")).get("topic")
            except Exception:
                pass
    return t or ""


def _topic(topic, name, proj_dir, pinned):
    title = name.replace("_", " ")
    t = topic or _niche_topic(proj_dir, pinned)
    return f"{t} (this video: {title})" if t and title.lower() not in t.lower() else (t or title)


def setup(*, name, kit, footage, work, data, out, vo=None, theme=None, grade=None, grain=None,
          tail=4.8, image_dirs=None, music_floor_db=-12.5, music_duck_db=-9.0, sfx_gain=0.7, xfade=None,
          sfx_style=None, vary=None, vary_look=None, topic=None, assets=None, finish=True, template=None, style=None,
          niche=None):
    """Paths and look for one project. Call before declaring any shot.

    The look comes from the registry: style= (styles/<id>) or template= (templates/<id>) or, as before, theme=.
    grade / grain / xfade / sfx_style default to the template's own; pass them only to override.
    The first plan pins template, style and niche in projects/<slug>/project.json; a later run that asks for a
    different one stops - one video, one template, no mixing."""
    global KIT, FOOT, WORK, ASSETS, SEGS, VO, SCRIPT, WORDS, OUT, IMG_DIRS, CUTS, VOX_TAIL, PB
    import registry
    # a project that was pinned keeps its style / template, even when build.py only names the theme
    pin_p = os.path.join(os.path.dirname(os.path.abspath(data)), "project.json")
    pinned = json.load(open(pin_p, encoding="utf-8")) if os.path.exists(pin_p) else {}
    style = style or os.environ.get("DOCU_STYLE") or pinned.get("style")
    template = template or os.environ.get("DOCU_TEMPLATE") or (pinned.get("template") if not theme else None)
    PB = registry.resolve(style or template or theme or "paper")
    theme = PB["theme"] if (style or template or not theme) else theme
    grade = grade if grade is not None else PB.get("grade") or "doc"
    grain = grain if grain is not None else (PB.get("grain") if PB.get("grain") is not None else 5.0)
    xfade = xfade if xfade is not None else (PB.get("xfade") or 0.0)
    sfx_style = sfx_style or PB.get("sfx_style") or "full"
    _pin(os.path.dirname(os.path.abspath(data)), PB, niche, footage)
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
    # mandatory vision-QC gate: every clip in the pool must have passed qc_pool.py
    # (talking heads / channel bugs / chyrons / center-frame interviews are rejected).
    # Set DOCU_SKIP_QC=1 only in an emergency; the user has explicitly forbidden it.
    try:
        import qc_guard
        qc = qc_guard.enforce(footage, catalog_path=f"{data}/catalog_all.json", project_name=name)
        if qc:
            kept, removed = qc_guard.filter_catalog(CAT, qc)
            if removed:
                print(f"[qc_guard] filtered catalog: kept {kept}, dropped {removed} QC-rejected clips")
    except ImportError:
        pass
    if theme in ("almanac", "almanac2") and grade == "doc":
        grade = "almanac2"                # the updated almanac's cooler print grade
    if theme == "datadoc" and grade == "doc":
        grade = "datadoc"                 # Data Documentary: muted, faintly warm, deep blacks
    if theme == "almanac_v1" and grade == "doc":
        grade = "almanac"                 # the first edition's warm print grade
    P.update(name=name, theme=theme, grade=grade, grain=grain, music_floor_db=music_floor_db,
             music_duck_db=music_duck_db, sfx_gain=sfx_gain, xfade=xfade, sfx_style=sfx_style, data=data,
             topic=_topic(topic, name, os.path.dirname(os.path.abspath(data)), pinned), finish=finish,
             assets=assets or os.environ.get("DOCU_ASSETS") or kit)
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
    """A prepared picture; returns the file name scenes refer to. Pictures pass the same QC gate as clips
    (no talking heads, posed faces, influencers, watermarks or centre logos - see docu/tools/qc_pool.py)."""
    grade = _g(grade)
    src = _src(name)
    if not src.startswith(os.path.abspath(KIT)):
        try:
            import qc_guard
            qc_guard.check_image(src)
        except ImportError:
            pass
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
    if crop:
        s["crop"] = crop
    elif c.get("_crop"):
        # QC flagged a corner logo for this clip: crop it away, and make the shot ours - a slow push-in on top of
        # the template's grade, grain and texture, so it no longer reads as somebody else's footage
        s["crop"] = c["_crop"]
        s.setdefault("push", 0.035)
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
        if m["at"] is None:
            t = 0.0
        elif isinstance(m["at"], (int, float)):
            t = float(m["at"]) + m.get("lead", 0)          # a time in seconds
        else:
            t = next(s["t0"] for s in scenes if s["cue"] == m["at"]) + m.get("lead", 0)
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
                # cap xfade pad to the scene's own duration; a pad >= duration collapses the xfade filter graph
                capped = min(float(xf), max(0.0, dur - 0.1))
                s["pad"] = round(capped, 3) if capped >= 0.05 else 0.0
        s["t0"] = round(st, 3)
        s["duration"] = dur
        s["cue"] = cue if isinstance(cue, str) else f"{cue}"
        scenes.append(s)
    return scenes


# ---------------------------------------------------------------- finishing layers (docu/asset_mix.py)
FOOTAGE_TYPES = {"clip", "photo", "depth", "spotlight", "tv", "split", "card"}
HEADING_OVERLAYS = {"almhead", "gzhead", "ddlabel"}
HEADING_TYPES = {"chapter", "doctitle", "title", "segment", "breaking"}


NEEDS = {"spotlight": ("dim",), "depth": ("soft",)}


def _variants_for(scenes):
    """a scene written as a raw dict (copied from a playbook example) still gets the picture variants its device
    needs: spotlight -> the dimmed copy, depth -> the cut-out subject"""
    want = {}
    for s in scenes:
        for v in NEEDS.get(s.get("type"), ()):
            if s.get("img"):
                want.setdefault(s["img"], set()).add(v)
    if not want:
        return
    for k, j in enumerate(JOBS):
        if j[0] == "img" and j[2] + ".jpg" in want:
            add = want[j[2] + ".jpg"]
            cut = j[5] or "soft" in add
            JOBS[k] = j[:5] + (cut, tuple(sorted(set(j[6]) | add)))


def finish(scenes):
    """The template's own textures and overlays on every video (asset_mix decides which, per template):
    a soft-light grain / paper / scan-line texture on all footage and photographs, a dust / light-leak / VHS
    overlay screened over the opening and every chapter heading, and the vintage-TV gate over shots marked
    archive=True. A scene opts out with no_texture=True or no_fx=True."""
    _variants_for(scenes)
    if not P.get("finish", True):
        return scenes
    try:
        import asset_mix
    except ImportError:
        return scenes
    mix = asset_mix.mix_for(P["name"], P["theme"], P["assets"])
    n_tex = n_fx = n_gate = 0
    for k, s in enumerate(scenes):
        if s["type"] in FOOTAGE_TYPES and mix.get("texture_png") and not s.get("no_texture"):
            s.setdefault("texture_png", mix["texture_png"])
            s.setdefault("texture_opacity", mix["texture_opacity"])
            n_tex += 1
        own = {d["type"] for d in (PB or {}).get("devices", []) if d.get("family") == "heading"}
        heading = s["type"] in HEADING_TYPES | own or any(o.get("type") in HEADING_OVERLAYS or "ov:" + str(o.get("type")) in own
                                                          for o in s.get("overlays", []))
        if (heading or k == 0) and mix.get("chapter_dust") and not s.get("no_fx"):
            s.setdefault("fx", []).append(dict(src=mix["chapter_dust"], mode="screen", opacity=0.7))
            n_fx += 1
        gate = mix.get("tv_gate") or mix.get("tv_gate_file")
        if (s.get("archive") or s.get("gate")) and gate and not s.get("no_fx"):
            s.setdefault("fx", []).append(dict(src=gate, key="green"))
            n_gate += 1
    P["mix"] = asset_mix.summary(mix)
    print(f"{P['mix']}  ->  texture on {n_tex} scenes, overlay on {n_fx} headings, TV gate on {n_gate} archive shots")
    return scenes


def _audit(scenes):
    """the edit audit (docu/tools/edit_audit.py) against this video's playbook; report + audit.json"""
    try:
        sys.path.insert(0, os.path.join(_HERE, "tools"))
        import edit_audit
        import mix as _mix
        ev = _mix.spot(scenes, P.get("sfx_style", "full"))
        txt = open(SCRIPT, encoding="utf-8-sig").read() if os.path.exists(SCRIPT) else ""
        r = edit_audit.run(scenes, PB, txt, sfx_events=len(ev), finish_summary=P.get("mix"))
        edit_audit.report(r)
        json.dump(r, open(f"{WORK}/audit.json", "w", encoding="utf-8"), indent=1)
        return r
    except Exception as e:         # noqa: BLE001 - the audit must never break a plan
        print("edit audit could not run:", e)
        return None


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
    scenes = finish(resolve(T, vo_dur))
    os.makedirs(OUT, exist_ok=True)
    json.dump(scenes, open(f"{WORK}/scenes.json", "w"), indent=1, ensure_ascii=False)
    import render as _r
    cfg = {"kit": _r.file_uri(KIT), "assets": _r.file_uri(ASSETS), "theme": P["theme"], "grain": P["grain"]}
    import registry
    cfg.update(registry.engine_cfg(PB))            # a template's own theme / scene code, a style's palette and fonts
    if P.get("vary") and P.get("vary_look", True):
        cfg["vary"] = variety.engine_overrides(P["vary"])
    clips = sum(s["duration"] for s in scenes if s["type"] == "clip")
    total = sum(s["duration"] for s in scenes)
    print(f"{len(scenes)} scenes, {total:.1f}s, clips {clips:.1f}s ({100 * clips / total:.0f}%), alignment {T.matched:.0%}")
    audit = _audit(scenes)
    if cmd in ("render", "all") and audit and audit["fails"] and os.environ.get("DOCU_AUDIT", "").lower() != "warn" \
            and not sys.argv[2:]:
        raise SystemExit(f"\n*** The edit does not use its template in full ({len(audit['fails'])} FAIL above). Fix the shot list "
                         f"and run `plan` again.\n    For a deliberate exception: DOCU_AUDIT=warn python build.py render\n")
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
        _fit_size(out)
        print("final:", out)
        # the last gate: every shot against the words it sits under (talking heads, logos, irrelevance)
        try:
            sys.path.insert(0, os.path.join(_HERE, "tools"))
            sys.path.insert(0, os.path.join(_HERE, "studio"))
            import final_qc
            words = json.load(open(WORDS, encoding="utf-8"))
            bad = final_qc.run(scenes, words, P.get("topic", ""), ASSETS, WORK)
            if bad:
                print(f"*** final QC flagged {len(bad)} shots - see {WORK}/final_qc.md and final_qc_flags.jpg; "
                      f"replace them in build.py, then: python build.py render {' '.join(sorted(bad)[:8])} && python build.py final")
        except Exception as e:          # noqa: BLE001 - QC must never lose a finished render
            print("final QC could not run:", e)


def _fit_size(path):
    """Hard-cut joins are stream copies, so the size follows the per-scene bitrate; re-encode once on the
    GPU (NVENC, multipass) to land on DOCU_TARGET_MB when the file is larger."""
    import subprocess
    target = int(os.environ.get("DOCU_TARGET_MB", "700"))
    if os.path.getsize(path) <= target * 1.08 * 1024 * 1024:
        return
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of",
                                "default=nk=1:nw=1", path], capture_output=True, text=True).stdout)
    vb = max(2500, int(target * 8192 / dur - 192))
    tmp = path[:-4] + ".fit.mp4"
    enc = ["-c:v", "h264_nvenc", "-preset", "p6", "-tune", "hq", "-multipass", "fullres", "-rc", "vbr"] \
        if os.environ.get("DOCU_NVENC", "1") != "0" else ["-c:v", "libx264", "-preset", "medium"]
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", path] + enc +
                   ["-b:v", f"{vb}k", "-maxrate", f"{vb * 3 // 2}k", "-bufsize", f"{vb * 2}k", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", tmp], check=True)
    os.replace(tmp, path)
    print(f"   fitted to {os.path.getsize(path) / 1048576:.0f} MB")


