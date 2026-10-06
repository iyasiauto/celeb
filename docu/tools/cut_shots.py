"""
cut_shots.py - cut short, silent shots (2.2-4 s) out of a trailer / promo / episode, on its own scene cuts.

    python docu/tools/cut_shots.py <video or folder> <pool/clips> [--per 8] [--min 2.2] [--max 4.0]

Each source file must be named `<person_slug>__<anything>.mp4`; shots come out as
`<person_slug>__cmp_<tag>NNN_<T>s.mp4` (the same naming comp_clips.py uses, so a build's clips_of() finds them).
The first and last few seconds (studio logos, rating cards, end titles) are skipped. QC (`niche.py qc`) then
throws out what is not usable (interviews, logos, captions, somebody else).
"""

import argparse
import os
import re
import subprocess
import sys


def scene_cuts(path, thr=0.3):
    out = subprocess.run(["ffmpeg", "-hide_banner", "-i", path, "-vf", f"select='gt(scene,{thr})',showinfo", "-an", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    return [float(m) for m in re.findall(r"pts_time:([0-9.]+)", out)]


def duration(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                       capture_output=True, text=True).stdout.strip()
    return float(r or 0)


def shots(path, per, lo, hi, edge):
    D = duration(path)
    cuts = [0.0] + scene_cuts(path) + [D]
    segs = []
    for a, b in zip(cuts, cuts[1:]):
        a, b = a + 0.12, b - 0.12                      # off the cut itself (no flash frames)
        if b - a >= lo and a >= edge and b <= D - edge:
            mid = (a + b) / 2
            L = min(hi, b - a)
            segs.append((mid - L / 2, L))
    if len(segs) > per:                                # spread over the whole source
        segs = [segs[round(k * (len(segs) - 1) / (per - 1))] for k in range(per)] if per > 1 else segs[:1]
    return segs


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("src")
    ap.add_argument("out")
    ap.add_argument("--per", type=int, default=8, help="at most N shots per source file")
    ap.add_argument("--min", type=float, default=2.2)
    ap.add_argument("--max", type=float, default=4.0)
    ap.add_argument("--edge", type=float, default=4.0, help="skip this many seconds at both ends")
    a = ap.parse_args()
    files = [os.path.join(a.src, f) for f in sorted(os.listdir(a.src))] if os.path.isdir(a.src) else [a.src]
    files = [f for f in files if f.lower().endswith((".mp4", ".m4v", ".mkv", ".mov", ".webm")) and "__" in os.path.basename(f)]
    os.makedirs(a.out, exist_ok=True)
    n = 0
    for f in files:
        person = os.path.basename(f).split("__")[0]
        tag = re.sub(r"[^a-z0-9]", "", os.path.basename(f).split("__")[1].lower())[:6]
        edge = a.edge if duration(f) > 20 else 0.6
        for k, (s, L) in enumerate(shots(f, a.per, a.min, a.max, edge)):
            dst = os.path.join(a.out, f"{person}__cmp_{tag}{k:02d}_{int(s)}s.mp4")
            if os.path.exists(dst):
                continue
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{s:.2f}", "-i", f, "-t", f"{L:.2f}", "-an",
                            "-vf", "scale=-2:720:flags=lanczos,setsar=1,fps=30", "-c:v", "libx264", "-preset", "medium",
                            "-crf", "18", "-pix_fmt", "yuv420p", dst], check=False)
            n += os.path.exists(dst)
        print(f"  {os.path.basename(f)}: done", flush=True)
    print(f"{n} shots -> {a.out}")


if __name__ == "__main__":
    sys.exit(main())
