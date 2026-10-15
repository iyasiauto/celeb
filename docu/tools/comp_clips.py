"""
comp_clips.py - short, silent clips from a reference / competitor video, cut from INSIDE its frame.

Gallery-style list videos play the real show / film clip in a box over their own graphics (a grid of tiles,
names, icons). This finds that box, cuts the shots inside it (and any clean full-frame shots), drops the audio,
and - with --names - asks the vision AI which person each shot is about, naming files <person_slug>__cmp_NNN.mp4
so the shot list and QC (people mode) know who they show. Use them 2-4 s, inside the template's frame, under
narration; never full screen.

    python docu/tools/comp_clips.py <video.mp4> <pool>/clips [--names people.json] [--full-until 31]

    --full-until S   full-frame shots before S seconds are kept too (a clean cold open), later ones are skipped
    --box x,y,w,h    force the inset box (1080p pixels) instead of finding it
Writes <out>/../_comp/<video>.json (every shot: source time, person, work, flags). QC the pool afterwards:
    python docu/tools/qc_pool.py <pool> --mode people --topic "..."
"""

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from collections import Counter
from concurrent.futures import ThreadPoolExecutor

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [os.path.join(os.path.dirname(HERE), "studio"), HERE]


def motion_boxes(src, W=480, H=270, FPS=4):
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-i", src, "-vf", f"fps={FPS},scale={W}:{H},format=gray", "-f", "rawvideo", "-"],
                         stdout=subprocess.PIPE)
    frames = []
    while True:
        b = p.stdout.read(W * H)
        if len(b) < W * H:
            break
        frames.append(np.frombuffer(b, np.uint8).astype(np.int16))
    F = np.stack(frames).reshape(-1, H, W)
    out = []
    for i in range(len(F)):
        d = np.abs(F[min(len(F) - 1, i + 2)] - F[i]) > 18
        if i >= 2:
            d |= np.abs(F[i] - F[i - 2]) > 18
        ys, xs = np.nonzero(d)
        if len(xs) < 400:
            out.append(None)
            continue
        x0, x1 = np.percentile(xs, [2, 98])
        y0, y1 = np.percentile(ys, [2, 98])
        k = 1920 / W
        if x1 - x0 > W * 0.85 and y1 - y0 > H * 0.85:
            out.append("full")
        elif x1 - x0 > 60 and y1 - y0 > 35:
            out.append((int(x0 * k), int(y0 * k), int(x1 * k), int(y1 * k)))
        else:
            out.append(None)
    return out, FPS


def the_box(boxes):
    """the inset box the video uses most (median of the large, roughly 16:9 boxes)"""
    big = [b for b in boxes if b not in (None, "full") and (b[2] - b[0]) > 700 and 1.4 < (b[2] - b[0]) / max(1, b[3] - b[1]) < 2.2]
    if not big:
        return None
    a = np.array(big)
    x0, y0, x1, y1 = [int(np.median(a[:, i])) for i in range(4)]
    m = 22                                   # stay inside its border (and its scan-line edge)
    return [x0 + m, y0 + m, x1 - x0 - 2 * m, y1 - y0 - 2 * m]


def segments(boxes, fps, box, full_until):
    """time ranges where the inset box (or a clean full frame early on) is playing"""
    segs, cur = [], None
    for i, b in enumerate(boxes):
        t = i / fps
        kind = None
        if b == "full" and t < full_until:
            kind = "full"
        elif b not in (None, "full") and box:
            ix = max(0, min(b[2], box[0] + box[2]) - max(b[0], box[0]))
            iy = max(0, min(b[3], box[1] + box[3]) - max(b[1], box[1]))
            if ix * iy > 0.55 * box[2] * box[3]:
                kind = "box"
        if kind and cur and cur["kind"] == kind and i - cur["i1"] <= 3:
            cur["i1"] = i
        else:
            if cur:
                segs.append(cur)
            cur = dict(kind=kind, i0=i, i1=i) if kind else None
    if cur:
        segs.append(cur)
    return [(s["i0"] / fps + 0.15, (s["i1"] + 1) / fps - 0.15, s["kind"]) for s in segs if (s["i1"] - s["i0"] + 1) / fps >= 1.5]


def cut(src, segs, box, out, prefix):
    shots = []
    for t0, t1, kind in segs:
        crop = None if kind == "full" else f"{box[2] // 2 * 2}:{box[3] // 2 * 2}:{box[0]}:{box[1]}"
        r = subprocess.run(["ffmpeg", "-v", "info", "-ss", f"{t0:.2f}", "-to", f"{t1:.2f}", "-i", src, "-vf",
                            (f"crop={crop}," if crop else "") + "select='gt(scene,0.32)',showinfo", "-f", "null", "-"],
                           capture_output=True, text=True)
        cuts = [t0 + float(x) for x in re.findall(r"pts_time:([0-9.]+)", r.stderr)]
        edges = [t0] + [c for c in cuts if c - t0 > 0.3 and t1 - c > 0.3] + [t1]
        for a, b in zip(edges, edges[1:]):
            a, b = a + 0.08, b - 0.08
            if b - a < 1.2:
                continue
            n = len(shots) + 1
            f = os.path.join(out, f"{prefix}{n:03d}_{int(a)}s.mp4")
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{a:.2f}", "-to", f"{b:.2f}", "-i", src, "-an"] +
                           (["-vf", f"crop={crop}"] if crop else []) +
                           ["-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", f], check=True)
            shots.append(dict(file=os.path.basename(f), src_t=round(a, 2), dur=round(b - a, 2), kind=kind))
    return shots


PROMPT = """Image 1 is a full frame of a list video (often a grid of named portrait tiles with a framed clip playing in it).
Image 2 is three frames of the clip itself. Reply with ONE JSON object only:
{{"person": "which person the clip is about - pick from the names visible in image 1 or from this list: {names}; '' if none",
 "work": "film or TV show if you recognise it, else ''",
 "shows": "what the clip shows, one sentence",
 "talking_head_interview": bool, "text_or_logo_in_clip": bool, "quality": int}}"""


def identify(src, shots, out, names):
    import ai
    from PIL import Image
    prov = ai.resolve("vision")
    if not prov:
        print("no vision AI (OPENLUX_API_KEY): shots keep their plain names")
        return
    model = ai.model_for("vision", prov)

    def one(s):
        with tempfile.TemporaryDirectory() as tmp:
            ims = []
            for k, f in enumerate((0.15, 0.5, 0.85)):
                p = f"{tmp}/{k}.jpg"
                subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{s['dur'] * f:.2f}", "-i", os.path.join(out, s["file"]),
                                "-frames:v", "1", "-vf", "scale=480:-2", p])
                if os.path.exists(p):
                    ims.append(Image.open(p).convert("RGB"))
            if not ims:
                return s
            st = Image.new("RGB", (sum(i.width for i in ims), max(i.height for i in ims)))
            x = 0
            for i in ims:
                st.paste(i, (x, 0)); x += i.width
            st.save(f"{tmp}/strip.jpg", quality=85)
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(s["src_t"] + min(1.0, s["dur"] / 2)), "-i", src, "-frames:v", "1",
                            "-vf", "scale=1280:-2", f"{tmp}/full.jpg"])
            for _ in range(3):
                try:
                    txt = ai.Chat("vision", provider=prov, model=model, log=lambda *x: None).send(
                        PROMPT.format(names=", ".join(names)), images=[f"{tmp}/full.jpg", f"{tmp}/strip.jpg"], max_tokens=500)
                    s.update(json.loads(re.sub(r"//[^\n]*", "", re.search(r"\{.*\}", txt, re.S).group(0))))
                    return s
                except Exception:          # noqa: BLE001
                    pass
        return s

    with ThreadPoolExecutor(8) as ex:
        list(ex.map(one, shots))
    slug = lambda x: re.sub(r"[^a-z0-9]+", "_", (x or "").lower()).strip("_")
    known = {slug(n) for n in names}
    for s in shots:
        ps = slug(s.get("person"))
        pre = ps if ps in known else "other"
        new = f"{pre}__{s['file']}"
        os.rename(os.path.join(out, s["file"]), os.path.join(out, new))
        s["file"] = new


def main():
    ap = argparse.ArgumentParser(description="silent clips cut from inside a reference video's frame")
    ap.add_argument("video"); ap.add_argument("out")
    ap.add_argument("--names", help="people.json (list of {name}) - name each shot after the person it shows")
    ap.add_argument("--full-until", type=float, default=30.0)
    ap.add_argument("--box", help="x,y,w,h of the inset in 1080p pixels (default: found automatically)")
    ap.add_argument("--prefix", default="cmp_")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    boxes, fps = motion_boxes(a.video)
    box = [int(v) for v in a.box.split(",")] if a.box else the_box(boxes)
    print("inset box:", box or "none (full-frame shots only)")
    segs = segments(boxes, fps, box, a.full_until)
    shots = cut(a.video, segs, box, a.out, a.prefix)
    print(len(shots), "shots,", round(sum(s["dur"] for s in shots), 1), "s")
    if a.names:
        names = [x["name"] if isinstance(x, dict) else str(x) for x in json.load(open(a.names, encoding="utf-8"))]
        identify(a.video, shots, a.out, names)
        print("people:", dict(Counter(s["file"].split("__")[0] for s in shots)))
    rep = os.path.join(os.path.dirname(os.path.abspath(a.out)), "_comp")
    os.makedirs(rep, exist_ok=True)
    json.dump(dict(video=a.video, box=box, shots=shots), open(os.path.join(rep, os.path.basename(a.video) + ".json"), "w"), indent=1)


if __name__ == "__main__":
    main()
