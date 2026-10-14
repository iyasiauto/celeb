"""stock_lib.py - a reusable stock B-roll library (Pexels / Pixabay), filled one topic at a time.

Instead of downloading a big list up front, ask for the topics a video needs. A topic already in the
library is reused (no download); only missing topics are fetched, QC'd (faceless) and kept for next time.

  python docu/tools/stock_lib.py get "empty courtroom, judge gavel" --clips 2 --photos 1 --to <project pool dir>
  python docu/tools/stock_lib.py list
  python docu/tools/stock_lib.py import <folder fetched by fetch_online.py>

Library (kit root, shared by every niche - stock is generic):
  stock_library/clips/broll_<topic>__pe123.mp4     moving B-roll (name as the Record example expects)
  stock_library/images/<topic>__pe456.jpg           photos
  stock_library/qc.json                             qc_pool.py verdicts (the gate)
  stock_library/sources.json                        page, author and licence of every file

--to <dir> hard-links the QC-kept files into <dir>/clips and <dir>/images (or <dir>/source_video if that
exists) so a project / pool can use them without copying. Keys come from api_keys/keys.env or
$FRONTIER_DIR/.env - they are never printed.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LIB = os.path.join(ROOT, "stock_library")
CLIPS, IMAGES = os.path.join(LIB, "clips"), os.path.join(LIB, "images")
TOOLS = os.path.dirname(os.path.abspath(__file__))
FRONTIER = r"C:\Users\ninja\Downloads\X Colab Automation\Frontier"


def slug(s):
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")[:40] or "x"


def load(p, default):
    try:
        return json.load(open(p, encoding="utf-8"))
    except (OSError, ValueError):
        return default


def topic_of(name):
    stem = os.path.splitext(name)[0]
    stem = stem[6:] if stem.startswith("broll_") else stem
    return stem.split("__")[0]


def kept(kind=None):
    """{topic: {"clips": [paths], "images": [paths]}} of files that passed QC"""
    qc = load(os.path.join(LIB, "qc.json"), {})
    out = {}
    for d, k in ((CLIPS, "clips"), (IMAGES, "images")):
        if not os.path.isdir(d):
            continue
        for f in sorted(os.listdir(d)):
            v = qc.get(f)
            if v is None or v.get("reject"):
                continue
            out.setdefault(topic_of(f), {"clips": [], "images": []})[k].append(os.path.join(d, f))
    return out


def pending():
    """files in the library that QC has not seen yet"""
    qc = load(os.path.join(LIB, "qc.json"), {})
    return [f for d in (CLIPS, IMAGES) if os.path.isdir(d) for f in os.listdir(d) if f not in qc]


def ingest(src):
    """move fetch_online.py output into the library (clips renamed broll_<topic>__...)"""
    os.makedirs(CLIPS, exist_ok=True)
    os.makedirs(IMAGES, exist_ok=True)
    sources = load(os.path.join(LIB, "sources.json"), {})
    sources.update(load(os.path.join(src, "sources.json"), {}))
    n = 0
    for dp, _, fs in os.walk(src):
        for f in fs:
            p = os.path.join(dp, f)
            ext = os.path.splitext(f)[1].lower()
            if ext in (".mp4", ".mov", ".webm", ".m4v"):
                dst = os.path.join(CLIPS, f if f.startswith("broll_") else "broll_" + f)
            elif ext in (".jpg", ".jpeg", ".png", ".webp"):
                dst = os.path.join(IMAGES, f)
            else:
                continue                                   # .part leftovers, sources.json
            if os.path.exists(dst):
                continue
            shutil.move(p, dst)
            n += 1
    json.dump(sources, open(os.path.join(LIB, "sources.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    return n


def qc(topic):
    if not pending():
        return
    subprocess.run([sys.executable, os.path.join(TOOLS, "qc_pool.py"), LIB, "--topic", topic,
                    "--mode", "faceless"], check=False)


def link_to(paths, to):
    vd = os.path.join(to, "source_video") if os.path.isdir(os.path.join(to, "source_video")) else os.path.join(to, "clips")
    idir = os.path.join(to, "images")
    out = []
    for p in paths:
        d = vd if p.startswith(CLIPS) else idir
        os.makedirs(d, exist_ok=True)
        dst = os.path.join(d, os.path.basename(p))
        if not os.path.exists(dst):
            try:
                os.link(p, dst)
            except OSError:
                shutil.copy2(p, dst)
        out.append(dst)
    return out


def cmd_get(a):
    topics = [t.strip() for t in a.topics.split(",") if t.strip()]
    have = kept()
    need = [t for t in topics
            if len(have.get(slug(t), {}).get("clips", [])) < a.clips
            or len(have.get(slug(t), {}).get("images", [])) < a.photos]
    for t in topics:
        h = have.get(slug(t), {"clips": [], "images": []})
        print(f"  {t:<34} in library: {len(h['clips'])} clips, {len(h['images'])} photos"
              + ("  -> fetching" if t in need else "  -> reuse"))
    if need:
        env = dict(os.environ)
        if not env.get("FRONTIER_DIR") and os.path.isdir(FRONTIER):
            env["FRONTIER_DIR"] = FRONTIER
        tmp = tempfile.mkdtemp(prefix="stock_")
        subprocess.run([sys.executable, os.path.join(TOOLS, "fetch_online.py"), "--out", tmp,
                        "--query", ", ".join(need), "--clips", str(a.clips), "--photos", str(a.photos),
                        "--sources", a.sources, "--max-seconds", str(a.max_seconds)], env=env, check=False)
        print(f"  added {ingest(tmp)} files to {LIB}")
        shutil.rmtree(tmp, ignore_errors=True)
    qc(a.qc_topic or ", ".join(topics))
    have = kept()
    paths = [p for t in topics for k in ("clips", "images") for p in have.get(slug(t), {}).get(k, [])]
    if a.to:
        paths = link_to(paths, a.to)
    print(f"{len(paths)} QC-kept files for {len(topics)} topics" + (f" linked into {a.to}" if a.to else ""))
    for p in paths:
        print("   ", p)


def cmd_list(a):
    have = kept()
    for t in sorted(have):
        print(f"  {t:<40} {len(have[t]['clips'])} clips  {len(have[t]['images'])} photos")
    p = pending()
    print(f"{len(have)} topics" + (f", {len(p)} files waiting for QC" if p else ""))


def cmd_import(a):
    print(f"  added {ingest(a.folder)} files to {LIB}")
    qc(a.qc_topic or "stock B-roll for investigative documentaries")
    cmd_list(a)


def main():
    ap = argparse.ArgumentParser(description="reusable stock B-roll library, filled topic by topic")
    sp = ap.add_subparsers(dest="cmd", required=True)
    g = sp.add_parser("get")
    g.add_argument("topics", help="comma-separated topics, e.g. 'empty courtroom, judge gavel'")
    g.add_argument("--clips", type=int, default=2)
    g.add_argument("--photos", type=int, default=1)
    g.add_argument("--to", default="", help="hard-link the kept files into this pool / project folder")
    g.add_argument("--sources", default="pexels,pixabay")
    g.add_argument("--max-seconds", type=int, default=30)
    g.add_argument("--qc-topic", default="", help="what the video is about (QC relevance)")
    g.set_defaults(fn=cmd_get)
    sp.add_parser("list").set_defaults(fn=cmd_list)
    i = sp.add_parser("import")
    i.add_argument("folder")
    i.add_argument("--qc-topic", default="")
    i.set_defaults(fn=cmd_import)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
