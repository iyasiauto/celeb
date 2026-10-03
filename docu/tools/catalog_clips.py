"""
catalog_clips.py - turn a folder of footage into the clip catalog that build.py's clip(i) uses.

Step 1  scan: probe every file, grab 3 frames per shot, and draw numbered contact sheets.

    python catalog_clips.py scan <footage>/source_video <cat_dir> [--split]

    --split   long files (> 20 s) are cut into shots with FFmpeg scene detection; without it every
              file is one shot (right for Drive folders of short, pre-cut clips).
    writes    <cat_dir>/shots.json          [{"i", "video", "s", "e", "w", "h"}]
              <cat_dir>/sheets_clips/*.jpg  6 shots per row x 3 frames, labelled with the index i

Step 2  look at the sheets and write <cat_dir>/notes_clips.txt, one line per shot you might use:

    # idx|quality 1-5|flags|tags|description
    24|4||wedding|Hasidic wedding: bride, women dancing, crowd of men
    28|2|i|book|reading a booklet, woman interview

    flags (comma separated): p presenter/vlogger · s burnt-in subtitles · t text/caption ·
                             g graphic · i interview. Shots with flags are avoided by the picker.

Step 3  build: merge shots + notes into data/catalog_all.json for the project.

    python catalog_clips.py build <cat_dir> <project>/data/catalog_all.json

List the clean shots by tag (what you choose from while writing the EDL):

    python catalog_clips.py list <project>/data/catalog_all.json [--min 3] [--unused <projects_root>]
"""

import argparse
import glob
import json
import os
import re
import subprocess
from concurrent.futures import ThreadPoolExecutor

from PIL import Image, ImageDraw, ImageFont

VIDEO_EXT = (".mp4", ".mov", ".mkv", ".webm", ".m4v", ".avi")


def _font(size):
    for p in ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"):
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def probe(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height:format=duration",
                        "-of", "json", path], capture_output=True, text=True)
    j = json.loads(r.stdout or "{}")
    st = (j.get("streams") or [{}])[0]
    return float(j.get("format", {}).get("duration", 0) or 0), st.get("width"), st.get("height")


def cuts(path, thresh=0.35):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", path, "-vf", f"select='gt(scene,{thresh})',showinfo", "-f", "null", "-"],
                       capture_output=True, text=True)
    return [float(m) for m in re.findall(r"pts_time:([0-9.]+)", r.stderr)]


def shots_of(path, split):
    dur, w, h = probe(path)
    name = os.path.basename(path)
    if not split or dur <= 20:
        return [dict(video=name, s=0.0, e=round(dur, 2), w=w, h=h)]
    marks = [0.0] + [c for c in cuts(path) if 0.5 < c < dur - 0.5] + [dur]
    out = []
    for a, b in zip(marks, marks[1:]):
        if b - a >= 2.0:                               # shorter than 2 s is rarely usable
            out.append(dict(video=name, s=round(a, 2), e=round(b, 2), w=w, h=h))
    return out


def frame(src, t, dst):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.2f}", "-i", src, "-frames:v", "1", "-vf", "scale=320:-2", dst])


def scan(src_dir, cat, split=False, workers=8):
    files = sorted(f for f in os.listdir(src_dir) if f.lower().endswith(VIDEO_EXT))
    with ThreadPoolExecutor(workers) as ex:
        lists = list(ex.map(lambda f: shots_of(os.path.join(src_dir, f), split), files))
    shots = [s for l in lists for s in l]
    for i, s in enumerate(shots):
        s["i"] = i
    os.makedirs(f"{cat}/frames", exist_ok=True)

    def grab(s):
        for k, frac in enumerate((0.2, 0.5, 0.8)):
            frame(os.path.join(src_dir, s["video"]), s["s"] + (s["e"] - s["s"]) * frac, f"{cat}/frames/{s['i']:05d}_{k}.jpg")
    with ThreadPoolExecutor(workers) as ex:
        list(ex.map(grab, shots))
    json.dump(shots, open(f"{cat}/shots.json", "w"), indent=0)
    sheets(shots, cat)
    print(len(shots), "shots from", len(files), "files; total", round(sum(s["e"] - s["s"] for s in shots) / 60, 1), "min")


def sheets(shots, cat, per=24):
    """contact sheets: each row = one shot's three frames, two shots per row, labelled i / duration"""
    out = f"{cat}/sheets_clips"
    os.makedirs(out, exist_ok=True)
    TW, TH, font = 213, 120, _font(15)
    for p in range(0, len(shots), per):
        chunk = shots[p:p + per]
        rows = (len(chunk) + 1) // 2
        sh = Image.new("RGB", (TW * 6 + 20, rows * (TH + 20)), "black")
        d = ImageDraw.Draw(sh)
        for j, s in enumerate(chunk):
            x0, y0 = (j % 2) * (TW * 3 + 20), (j // 2) * (TH + 20)
            for k in range(3):
                f = f"{cat}/frames/{s['i']:05d}_{k}.jpg"
                if os.path.exists(f):
                    im = Image.open(f).convert("RGB")
                    im.thumbnail((TW - 2, TH - 2))
                    sh.paste(im, (x0 + k * TW, y0))
            d.text((x0 + 2, y0 + TH + 1), f"{s['i']}  {s['e'] - s['s']:.1f}s  {s['video'][:26]}", fill="yellow", font=font)
        sh.save(f"{out}/clips_{p // per:03d}.jpg", quality=78)


def build(cat, dst):
    shots = json.load(open(f"{cat}/shots.json"))
    notes = {}
    for line in open(f"{cat}/notes_clips.txt", encoding="utf-8"):
        if not line.strip() or line.startswith("#"):
            continue
        p = line.rstrip("\n").split("|", 4)
        notes[int(p[0])] = p
    out = []
    for s in shots:
        n = notes.get(s["i"])
        e = dict(s)
        if n:
            e.update(quality=int(n[1] or 0), flags=[f for f in n[2].split(",") if f], tags=[t for t in n[3].split(",") if t], desc=n[4])
        else:
            e.update(quality=0, flags=["unreviewed"], tags=[], desc="")
        out.append(e)
    os.makedirs(os.path.dirname(os.path.abspath(dst)), exist_ok=True)
    json.dump(out, open(dst, "w"), indent=0)
    print(len(out), "shots,", len(notes), "reviewed ->", dst)


def used_elsewhere(projects_root):
    used = set()
    for p in glob.glob(os.path.join(projects_root, "*", "data", "assets_used.json")):
        used |= set(json.load(open(p)).get("clips", []))
    return used


def list_clean(catalog, min_q=3, unused_root=None):
    cat = json.load(open(catalog))
    used = used_elsewhere(unused_root) if unused_root else set()
    by = {}
    for c in cat:
        if c.get("flags") or c.get("quality", 0) < min_q or c["video"] in used:
            continue
        by.setdefault((c.get("tags") or ["untagged"])[0], []).append(c)
    for t, l in sorted(by.items(), key=lambda x: -len(x[1])):
        print(f"== {t} ({len(l)})")
        for c in l:
            print(f"  {c['i']:4d}  {c['e'] - c['s']:5.1f}s  q{c['quality']}  {c['desc']}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("scan"); a.add_argument("src"); a.add_argument("cat"); a.add_argument("--split", action="store_true")
    b = sub.add_parser("build"); b.add_argument("cat"); b.add_argument("dst")
    c = sub.add_parser("list"); c.add_argument("catalog"); c.add_argument("--min", type=int, default=3); c.add_argument("--unused")
    x = ap.parse_args()
    if x.cmd == "scan":
        scan(x.src, x.cat, x.split)
    elif x.cmd == "build":
        build(x.cat, x.dst)
    else:
        list_clean(x.catalog, x.min, x.unused)
