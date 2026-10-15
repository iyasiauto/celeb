"""
template_reel.py - a preview sheet and a short sample video for a template, rendered by the Docu engine itself.

    python docu/tools/template_reel.py dossier                 one template
    python docu/tools/template_reel.py all                     every template that has demo content
    python docu/tools/template_reel.py dossier --sheet-only    just the stills

Writes
    templates/<id>/previews/<device>.jpg   one still per device (registry.py show lists them)
    templates/<id>/previews/sheet.jpg      the contact sheet
    styles/<id>/preview.jpg                the card picture in Docu Studio (= the sheet)
    styles/<id>/sample.mp4                 ~45-70 s: every graphic of the template once, footage in its frame between
                                           them, the template's sound marks over a quiet music bed

Demo content: a Frontier-imported template uses the example fields of each graphic (frontier.json); pictures and
clips come from the shared stock library (stock_library/) or, failing that, any pool in media/.
"""

import argparse
import glob
import json
import os
import random
import shutil
import subprocess
import sys

DOCU = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(DOCU)
sys.path.insert(0, DOCU)

import registry   # noqa: E402

KIT = os.path.join(ROOT, "media", "kit")
W, H = 1920, 1080


def _media():
    imgs = sorted(glob.glob(os.path.join(ROOT, "stock_library", "images", "*.jpg")))
    clips = sorted(glob.glob(os.path.join(ROOT, "stock_library", "clips", "*.mp4")))
    if len(imgs) < 6:
        imgs += sorted(glob.glob(os.path.join(ROOT, "media", "*", "pool", "images", "*.jpg")))[:200]
    if len(clips) < 4:
        clips += sorted(glob.glob(os.path.join(ROOT, "media", "*", "pool", "clips", "*.mp4")))[:200]
    return imgs, clips


def _dur(p):
    try:
        return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p],
                                    capture_output=True, text=True).stdout.strip())
    except ValueError:
        return 0.0


def _prepared(src, work, k):
    """a picture at 1920 wide (a 6000-px original would stall the page)"""
    out = os.path.join(work, f"img_{k:02d}.jpg")
    if not os.path.exists(out):
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-vf", "scale='min(1920,iw)':-2", "-q:v", "3", out],
                       capture_output=True)
    return out if os.path.exists(out) else src


def demo_scenes(tid, work, cap=4.6):
    """the reel's scene list for an imported template: each graphic once, footage between"""
    import frontier
    F = frontier.Template(tid)
    imgs, clips = _media()
    rnd = random.Random(tid)
    rnd.shuffle(imgs)
    rnd.shuffle(clips)
    pics = [_prepared(p, work, k) for k, p in enumerate(imgs[:16])]
    scenes, k, c = [], 0, 0

    def clip(over=None, framed=True):
        nonlocal c
        if not clips:
            return None
        for _ in range(len(clips)):
            src = clips[c % len(clips)]
            c += 1
            d = _dur(src)
            if d >= 2.0:                     # a broken or tiny download is skipped
                break
        else:
            return None
        s = dict(type="clip", src=src, start=min(1.0, max(0.0, d - 3.0)), end=max(1.5, min(d, 4.5)), duration=2.8,
                 grade=registry.resolve(tid).get("grade", "doc"))
        if over:
            s["overlays"] = [over]
            s["duration"] = 3.8
        if framed and F.frame:
            s = F.framed(s, text="This is the line the narrator says over the shot, typed under it.")
        return s

    first = True
    for ty, info in F.types.items():
        ex = F.example(ty)
        if not ex:
            continue                      # no worked example for this type (docgfx card / step): not shown in the demo
        dur = min(cap, F.seconds(ty))
        if info.get("over_footage") and not first:
            sc = clip(over=F.over(ty, at=0.25, **ex), framed=False)
            if sc:
                sc["duration"] = max(sc["duration"], dur)
                scenes.append(sc)
                continue
        sc = F.g(ty, **ex)
        sc["img"] = pics[k % len(pics)] if pics else None
        k += 1
        sc["duration"] = dur
        scenes.append(sc)
        first = False
        if len(scenes) % 3 == 2:
            s2 = clip()
            if s2:
                scenes.append(s2)
    # a template's own extra devices (template.json "demo"): "$img" = the next demo picture, {"clip": true} = footage
    tj = json.load(open(os.path.join(ROOT, "templates", tid, "template.json"), encoding="utf-8"))

    docs = [_prepared(p, work, 90 + i) for i, p in enumerate([p for p in imgs if any(w in os.path.basename(p).lower()
                                                                for w in ("document", "newspaper", "archive", "paper", "letter"))][:2])]

    def fill(v):
        nonlocal k
        if v == "$doc" and docs:
            return docs[0]
        if v == "$img" or v == "$doc":
            k += 1
            return pics[k % len(pics)] if pics else None
        if isinstance(v, list):
            return [fill(x) for x in v]
        if isinstance(v, dict):
            return {kk: fill(vv) for kk, vv in v.items()}
        return v
    for d in tj.get("demo", []):
        d = fill(dict(d))
        if d.pop("clip", False):
            sc = clip(framed=False)
            if not sc:
                continue
            sc.update({kk: vv for kk, vv in d.items() if kk != "duration"})
            sc["duration"] = float(d.get("duration", 3.8))
        else:
            sc = d
        scenes.insert(min(len(scenes), int(d.pop("pos", len(scenes))) if isinstance(d.get("pos"), int) else len(scenes)), sc)
    t = 0.0
    for i, s in enumerate(scenes):
        s["id"] = f"r{i:02d}_{s['type']}"
        s["t0"] = round(t, 3)
        t += s["duration"]
    return scenes


def demo_builtin(tid, work, cap=4.8):
    """a Docu template (no frontier.json): each of its devices once, from the gallery's working examples
    (docu/templates/gallery.py), on pictures from the stock library; footage between them"""
    import copy
    sys.path.insert(0, os.path.join(DOCU, "templates"))
    import gallery
    pb = registry.resolve(tid)
    imgs, clips = _media()
    rnd = random.Random(tid)
    assets = os.path.join(work, "assets")
    os.makedirs(assets, exist_ok=True)

    def pick(*words):
        for w in words:
            for p in imgs:
                if w in os.path.basename(p).lower():
                    return p
        return imgs[rnd.randrange(len(imgs))]

    class A:
        kit = KIT
        photo = pick("courthouse", "building", "street", "farm", "landscape")
        portrait = pick("statue", "hands", "gavel", "documents")
        scan = pick("document", "archive", "newspaper", "map", "paper")
        object = pick("gavel", "phone", "key", "lamp", "clock")
    gallery.prepare(A, assets)
    ex = {}
    for name, spec, themes in gallery.specs():
        if themes and pb["theme"] not in themes and tid not in themes:
            continue
        ex.setdefault(spec["type"], spec)
        for o in spec.get("overlays", []):
            ex.setdefault("ov:" + o["type"], spec)
    seen, scenes, c = set(), [], 0
    good = [p for p in clips if _dur(p) >= 2.0][:12]
    rnd.shuffle(good)
    for d in pb.get("devices", []):
        spec = ex.get(d["type"])
        if not spec or id(spec) in seen:
            continue
        seen.add(id(spec))
        s = copy.deepcopy(spec)
        if "from_" in s:
            s["from"] = s.pop("from_")
        s["duration"] = min(cap, float(s.get("duration", 5.0)))
        scenes.append(s)
        if len(scenes) % 3 == 2 and good:
            src = good[c % len(good)]
            c += 1
            dd = _dur(src)
            scenes.append(dict(type="clip", src=src, start=min(1.0, max(0.0, dd - 3.0)), end=max(1.5, min(dd, 4.5)),
                               duration=2.8, grade=pb.get("grade", "doc")))
        if len(scenes) >= 18:
            break
    t = 0.0
    for i, s in enumerate(scenes):
        s["id"] = f"r{i:02d}_{s['type']}"
        s["t0"] = round(t, 3)
        t += s["duration"]
    return scenes, assets


def write_example(tid, scenes):
    """templates/<id>/demo_build.py: every device of the template as a shot-list line, with the fields it takes"""
    def clean(v):
        if isinstance(v, str) and (v.startswith("/") or ":\\" in v):
            return "<" + ("clip" if v.endswith(".mp4") else "picture") + ">"
        if isinstance(v, list):
            return [clean(x) for x in v]
        if isinstance(v, dict):
            return {k: clean(x) for k, x in v.items() if k not in ("id", "t0", "sfx", "pos", "frame_n")}
        return v
    lines = [f'"""', f"demo_build.py - every device of the {tid!r} template once, as shot-list lines (generated by",
             "docu/tools/template_reel.py from the sample it renders). Copy a line into a project's build.py and put real",
             "pictures / clips and the words' timing in. <picture> = a key or path from the niche pool, <clip> = a catalog clip.",
             "", "    import frontier", f"    F = frontier.Template({tid!r})", '"""', "", "DEMO = ["]
    import frontier
    F = frontier.Template(tid)
    rev = {v["scene"]: k for k, v in F.types.items()}
    for s in scenes:
        c = clean(dict(s))
        ty = c.pop("type")
        dur = c.pop("duration", None)
        if ty in rev:
            for k in ("page",):
                c.pop(k, None)
            if F.kind == "motion":
                c = {k: v for k, v in c.items() if k in ("title", "subtitle", "value", "count", "highlight", "items", "image")}
            lines.append(f"    F.g({rev[ty]!r}, **{c!r}),      # ~{dur} s")
        elif ty == "clip":
            ov = c.get("overlays") or []
            if ov and ov[0].get("type") == "frontier":
                o = {k: v for k, v in ov[0].items() if k not in ("type", "page", "kind", "at", "sfx")}
                lines.append(f"    clip(<i>, overlays=[F.over({ov[0]['kind']!r}, at={ov[0].get('at', 0.3)}, "
                             f"**{o!r})]),")
            elif ov:
                lines.append(f"    clip(<i>, overlays={ov!r}),")
            elif c.get("footage_frame"):
                lines.append(f"    F.framed(clip(<i>)),      # footage in the {c['footage_frame']!r} frame")
        else:
            lines.append(f"    dict(type={ty!r}, **{c!r}),      # ~{dur} s")
    lines.append("]")
    open(os.path.join(ROOT, "templates", tid, "demo_build.py"), "w", encoding="utf-8").write(
        "\n".join(lines).replace("<i>", "12") + "\n")


def render(tid, scenes, work, workers, assets=None):
    import render as R
    pb = registry.resolve(tid)
    cfg = {"kit": R.file_uri(KIT), "assets": R.file_uri(assets or work), "theme": pb["theme"], "grain": pb.get("grain", 1.0)}
    cfg.update(registry.engine_cfg(pb))
    fails = R.render_all(scenes, work, cfg, workers=workers)
    if fails:
        bad = {sid for sid, _ in fails}
        print(f"  {len(fails)} demo scenes failed and are left out: {sorted(bad)}")
        keep = [s for s in scenes if s["id"] not in bad]
        scenes[:] = keep
        t = 0.0
        for s in scenes:
            s["t0"] = round(t, 3)
            t += s["duration"]
    return cfg


def stills(tid, scenes, work):
    pv = os.path.join(ROOT, "templates", tid, "previews")
    os.makedirs(pv, exist_ok=True)
    shots = []
    for s in scenes:
        mp4 = os.path.join(work, s["id"] + ".mp4")
        name = s["type"] if s["type"] != "clip" else ("frame_" + (s.get("footage_frame") or "clip") if not s.get("overlays")
                                                      else "over_" + s["overlays"][0].get("kind", "clip"))
        out = os.path.join(pv, name + ".jpg")
        at = s["duration"] * (0.62 if s["type"] != "clip" else 0.7)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{at:.2f}", "-i", mp4, "-frames:v", "1", "-q:v", "3", out],
                       capture_output=True)
        if os.path.exists(out) and out not in shots:
            shots.append(out)
    from PIL import Image, ImageDraw, ImageFont
    pick = shots[:12]
    cols = 4
    rows = (len(pick) + cols - 1) // cols
    tw, th = 480, 270
    sheet = Image.new("RGB", (cols * tw, rows * (th + 34)), (14, 14, 14))
    try:
        font = ImageFont.truetype(os.path.join(KIT, "fonts", "Roboto-Condensed.ttf"), 22)
    except OSError:
        font = ImageFont.load_default()
    d = ImageDraw.Draw(sheet)
    for i, p in enumerate(pick):
        im = Image.open(p).convert("RGB").resize((tw, th))
        x, y = (i % cols) * tw, (i // cols) * (th + 34)
        sheet.paste(im, (x, y))
        d.text((x + 10, y + th + 6), os.path.splitext(os.path.basename(p))[0], fill=(220, 214, 200), font=font)
    out = os.path.join(pv, "sheet.jpg")
    sheet.save(out, quality=86)
    sdir = os.path.join(ROOT, "styles", tid)
    if os.path.isdir(sdir):
        shutil.copy(out, os.path.join(sdir, "preview.jpg"))
    return out


def sample(tid, scenes, work):
    import render as R
    import mix
    silent = os.path.join(work, "silence.wav")
    total = sum(s["duration"] for s in scenes)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", f"anullsrc=r=48000:cl=stereo", "-t", f"{total + 1:.2f}",
                    silent], capture_output=True)
    video = os.path.join(work, "reel_video.mp4")
    R.concat(scenes, work, video)
    tracks = sorted(f for f in os.listdir(os.path.join(KIT, "music")) if f.lower().endswith((".mp3", ".wav", ".m4a", ".ogg")))
    track = tracks[sum(map(ord, tid)) % len(tracks)] if tracks else None
    wav = os.path.join(work, "reel.wav")
    pb = registry.resolve(tid)
    plan = [dict(**{"from": 0.0}, track=track, db=-6)] if track else []
    mix.build_mix(scenes, silent, KIT, wav, total, plan=plan, music_floor_db=-15.0, music_duck_db=-15.0,
                  sfx_style=pb.get("sfx_style", "full")) if "sfx_style" in mix.build_mix.__code__.co_varnames else \
        mix.build_mix(scenes, silent, KIT, wav, total, plan=plan)
    sdir = os.path.join(ROOT, "styles", tid)
    os.makedirs(sdir, exist_ok=True)
    out = os.path.join(sdir, "sample.mp4")
    tmp = os.path.join(work, "sample_mux.mp4")
    mix.mux(video, wav, tmp)
    # small enough to ship in the kit: 1280 wide, ~2.5 Mbps
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", tmp, "-vf", "scale=1280:-2", "-c:v", "libx264", "-preset", "medium",
                    "-b:v", "1700k", "-maxrate", "2400k", "-bufsize", "3400k", "-c:a", "aac", "-b:a", "128k",
                    "-movflags", "+faststart", out], capture_output=True)
    return out


def one(tid, workers=4, sheet_only=False, keep=False):
    work = os.path.join(ROOT, "media", "work", f"_reel_{tid}")
    if os.path.isdir(work) and not keep:
        shutil.rmtree(work)
    os.makedirs(work, exist_ok=True)
    assets = None
    if os.path.exists(os.path.join(ROOT, "templates", tid, "frontier.json")):
        scenes = demo_scenes(tid, work)
    else:
        scenes, assets = demo_builtin(tid, work)
    json.dump(scenes, open(os.path.join(work, "scenes.json"), "w"), indent=1)
    render(tid, scenes, work, workers, assets)
    if not assets:
        write_example(tid, scenes)
    sh = stills(tid, scenes, work)
    print(f"{tid}: sheet {os.path.relpath(sh, ROOT)}")
    if not sheet_only:
        smp = sample(tid, scenes, work)
        print(f"{tid}: sample {os.path.relpath(smp, ROOT)} ({os.path.getsize(smp) / 1e6:.1f} MB, "
              f"{sum(s['duration'] for s in scenes):.0f} s)")
        if not keep:
            shutil.rmtree(work, ignore_errors=True)        # the segments are not needed once the sample exists


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("template")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--sheet-only", action="store_true")
    ap.add_argument("--keep", action="store_true", help="reuse segments already rendered")
    ap.add_argument("--force", action="store_true", help="render even when a recent sample exists")
    a = ap.parse_args()
    ids = [x for x in a.template.split(",") if x] if a.template != "all" else \
        [t for t in registry.templates() if not t.startswith("_")]
    import time
    for tid in ids:
        smp = os.path.join(ROOT, "styles", tid, "sample.mp4")
        busy = os.path.join(ROOT, "media", "work", f"_reel_{tid}", "scenes.json")
        if not a.force and not a.sheet_only and os.path.exists(smp) and time.time() - os.path.getmtime(smp) < 3 * 3600:
            print(f"{tid}: sample made in the last 3 hours - skipped (--force to redo)")
            continue
        if not a.force and os.path.exists(busy) and time.time() - os.path.getmtime(busy) < 600:
            print(f"{tid}: another run is rendering it - skipped")
            continue
        one(tid, a.workers, a.sheet_only, a.keep)


if __name__ == "__main__":
    main()
