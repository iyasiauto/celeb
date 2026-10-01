"""
deliver.py - check the final MP4, shrink it under a size limit if needed, and upload it to gofile.

    python deliver.py <final.mp4> [--limit-gb 1.0] [--no-upload]

1. Checks: duration, resolution, frame rate, audio loudness (integrated LUFS) and file size.
2. If the file is over the limit: re-encodes the picture with 2-pass x264 at the bitrate that lands
   at 96 % of the limit (audio copied), keeping 1080p30 - visually the same at documentary bitrates
   (~7-8 Mb/s for 16 minutes under 1 GB).
3. Uploads with curl to gofile (tries upload.gofile.io, then the listed store servers), checks the
   md5 gofile reports against the local file, and prints the download page.
   The link is also written next to the video as <name>.link.txt. With GOFILE_TOKEN set (api_keys/),
   uploads go into your gofile account instead of anonymous links.
"""

import argparse
import hashlib
import json
import os
import re
import subprocess

from keys import get as _key

TOKEN = _key("GOFILE_TOKEN")          # optional, see api_keys/README.md

STORES = ["https://upload.gofile.io/uploadfile", "https://store-eu-par-4.gofile.io/uploadFile",
          "https://store-eu-par-3.gofile.io/uploadFile", "https://store-na-phx-1.gofile.io/uploadFile",
          "https://store1.gofile.io/uploadFile"]


def probe(p):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration,size:stream=codec_type,width,height,r_frame_rate",
                        "-of", "json", p], capture_output=True, text=True)
    return json.loads(r.stdout)


def loudness(p):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", p, "-vn", "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True)
    m = re.findall(r"I:\s+(-?[0-9.]+) LUFS", r.stderr)
    return float(m[-1]) if m else None


def shrink(src, limit_bytes):
    j = probe(src)
    dur = float(j["format"]["duration"])
    abr = 192_000
    vbr = int((limit_bytes * 0.96 * 8) / dur - abr)
    out = src.replace(".mp4", "_small.mp4")
    base = ["ffmpeg", "-v", "error", "-y", "-i", src, "-c:v", "libx264", "-preset", "slow", "-b:v", str(vbr),
            "-maxrate", str(int(vbr * 1.6)), "-bufsize", str(int(vbr * 3)), "-pix_fmt", "yuv420p"]
    log = src + ".2pass"
    subprocess.run(base + ["-pass", "1", "-passlogfile", log, "-an", "-f", "mp4", os.devnull], check=True)
    subprocess.run(base + ["-pass", "2", "-passlogfile", log, "-c:a", "copy", "-movflags", "+faststart", out], check=True)
    for f in os.listdir(os.path.dirname(os.path.abspath(src))):
        if f.startswith(os.path.basename(log)):
            os.remove(os.path.join(os.path.dirname(os.path.abspath(src)), f))
    print(f"re-encoded at {vbr / 1e6:.2f} Mb/s -> {out} ({os.path.getsize(out) / 1e9:.2f} GB)")
    return out


def md5(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def upload(p):
    local = md5(p)
    for url in STORES:
        for _ in range(2):
            auth = ["-H", f"Authorization: Bearer {TOKEN}"] if TOKEN else []      # your gofile account, if set
            r = subprocess.run(["curl", "-sS", "--retry", "2", *auth, "-F", f"file=@{p}", url], capture_output=True, text=True)
            try:
                d = json.loads(r.stdout)["data"]
            except Exception:
                print("  upload failed on", url, (r.stderr or r.stdout)[:120])
                continue
            if d.get("md5") and d["md5"] != local:
                print("  md5 mismatch on", url, "- retrying")
                continue
            return d.get("downloadPage"), local
    raise SystemExit("upload failed on every server")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("--limit-gb", type=float, default=1.0)
    ap.add_argument("--no-upload", action="store_true")
    x = ap.parse_args()
    j = probe(x.video)
    v = next(s for s in j["streams"] if s["codec_type"] == "video")
    size = os.path.getsize(x.video)
    print(f"{float(j['format']['duration']) / 60:.2f} min · {v['width']}x{v['height']} @ {v['r_frame_rate']} · "
          f"{size / 1e9:.2f} GB · {loudness(x.video)} LUFS")
    path = x.video if size <= x.limit_gb * 1e9 else shrink(x.video, x.limit_gb * 1e9)
    if not x.no_upload:
        link, h = upload(path)
        open(os.path.splitext(path)[0] + ".link.txt", "w").write(f"{link}\nmd5 {h}\n")
        print("gofile:", link, "\nmd5 verified:", h)
