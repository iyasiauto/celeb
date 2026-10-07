"""
pool.py - keep one reusable footage pool per subject ("the data library") instead of collecting the
same clips again for every video.

A pool is a plain folder:

    <pool>/clips/*.mp4 *.mov        the footage
    <pool>/images/*.jpg *.png       the pictures
    <pool>/library.json             one record per file: source, page, author, licence, query, tags
    <pool>/tags.json                {file: [tags]} - what `niche-add --tags` and the offline
                                    shot list match the words of a sentence against
    <pool>/CREDITS.md               every file with its page and licence (for the description)
    <pool>/README.md                what is in here and how to use it

    python pool.py merge <pool> <new_dir>...     move newly fetched clips/images into the pool
    python pool.py build <pool> [--meta f.json]  (re)write library.json, tags.json, CREDITS.md, README.md
    python pool.py sheets <pool> <out_dir>       contact sheets of everything, labelled with the names
    python pool.py catalog <pool> <out.json>     the clip catalog a project's build.py uses

`--meta` takes the download lists of earlier videos ({key: {src, id, page, q, by, ...}} or
fetch_online.py's sources.json) so files collected before the pool existed keep their credit.
Nothing is deleted and nothing is re-downloaded: merge only moves files in, build only re-reads them.
"""

import argparse
import glob
import json
import os
import re
import shutil
import subprocess
from concurrent.futures import ThreadPoolExecutor

VIDEO_EXT = (".mp4", ".mov", ".m4v", ".webm", ".mkv")
IMAGE_EXT = (".jpg", ".jpeg", ".png", ".webp")
LICENCE = {"pexels": "Pexels licence", "pixabay": "Pixabay content licence", "wikimedia": "see the file page",
           "google": "UNKNOWN - check before publishing"}
_STOP = set("the and from with for left right img dsc vid clip mov jpg jpeg png mp4 copy final edit version photo "
            "image picture video stock footage hd free download file wikimedia commons flickr jpeg".split())


def words(s, n=8):
    out = [t for t in re.split(r"[^a-z]+", s.lower()) if len(t) > 2 and re.search(r"[aeiouy]", t)
           and t not in _STOP and not re.fullmatch(r"[a-f0-9]{5,}", t)]
    return list(dict.fromkeys(out))[:n]


def stem(p):
    return os.path.splitext(os.path.basename(p))[0]


def files(pool):
    cl = sorted(p for p in glob.glob(os.path.join(pool, "clips", "*")) if p.lower().endswith(VIDEO_EXT))
    im = sorted(p for p in glob.glob(os.path.join(pool, "images", "*")) if p.lower().endswith(IMAGE_EXT))
    return cl, im


# ------------------------------------------------------------------ merge
def cmd_merge(a):
    cd, idir = os.path.join(a.pool, "clips"), os.path.join(a.pool, "images")
    os.makedirs(cd, exist_ok=True); os.makedirs(idir, exist_ok=True)
    moved, skipped, meta = 0, 0, {}
    for src in a.new_dirs:
        sj = os.path.join(src, "sources.json")
        if os.path.exists(sj):
            meta.update(json.load(open(sj)))
        for sub, dst, ext in (("clips", cd, VIDEO_EXT), ("images", idir, IMAGE_EXT)):
            for p in sorted(glob.glob(os.path.join(src, sub, "*"))):
                if not p.lower().endswith(ext):
                    continue
                q = os.path.join(dst, os.path.basename(p))
                if os.path.exists(q):
                    skipped += 1
                    continue
                shutil.move(p, q)
                moved += 1
    if meta:
        mf = os.path.join(a.pool, "sources_in.json")
        old = json.load(open(mf)) if os.path.exists(mf) else {}
        old.update(meta)
        json.dump(old, open(mf, "w"), indent=1, ensure_ascii=False)
    print(f"{moved} files moved into {a.pool} ({skipped} already there)")


# ------------------------------------------------------------------ build
def load_meta(pool, extra):
    """every piece of metadata we can find, keyed by file stem and by bare id"""
    out = {}

    def put(key, rec):
        if key and key not in out:
            out[key] = rec

    paths = [os.path.join(pool, "sources_in.json")] + list(extra or [])
    for p in paths:
        if not os.path.exists(p):
            continue
        for k, v in json.load(open(p)).items():
            src = v.get("source") or v.get("src") or ""
            rec = dict(source=src, page=v.get("page"), author=v.get("author") or v.get("by") or "",
                       licence=v.get("licence") or LICENCE.get(src, ""), query=v.get("query") or v.get("q") or "",
                       alt=v.get("alt") or "")
            put(k, rec)
            if v.get("id") and src:                        # pexels_18333494 / px18333494 / pe18333494
                short = {"pexels": "p", "pixabay": "px"}.get(src, src[:2])
                put(f"{src}_{v['id']}", rec)
                put(f"px{v['id']}", rec); put(f"pe{v['id']}", rec); put(f"{short}{v['id']}", rec)
    return out


def record(path, kind, meta):
    st = stem(path)
    m = meta.get(st)
    if not m:
        # "wisconsin_dairy_farm__px12345" or a bare "px12345" / "pe12345"
        base = st.split("__")[-1]
        m = meta.get(base) or {}
    src = m.get("source") or ("pexels" if st.startswith(("px", "pe")) else "")
    q = m.get("query") or (st.split("__")[0].replace("_", " ") if "__" in st else "")
    slug = re.sub(r"[-_/]+", " ", (m.get("page") or "").rstrip("/").rsplit("/", 1)[-1])
    tags = words(" ".join([q, m.get("alt", ""), slug]))
    r = dict(file=os.path.basename(path), kind=kind, source=src, page=m.get("page"), author=m.get("author", ""),
             licence=m.get("licence") or LICENCE.get(src, ""), query=q, tags=tags)
    if m.get("alt"):
        r["desc"] = m["alt"]
    return r


def probe(path):
    try:
        o = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                            "stream=width,height:format=duration", "-of", "json", path],
                           capture_output=True, text=True, timeout=60).stdout
        d = json.loads(o)
        s = (d.get("streams") or [{}])[0]
        return int(s.get("width") or 0), int(s.get("height") or 0), round(float(d.get("format", {}).get("duration") or 0), 2)
    except Exception:
        return 0, 0, 0.0


def cmd_build(a):
    cl, im = files(a.pool)
    meta = load_meta(a.pool, a.meta)
    lib = []
    with ThreadPoolExecutor(8) as ex:
        dims = list(ex.map(probe, cl + im))
    for p, (w, h, d) in zip(cl + im, dims):
        kind = "clip" if p in cl else "photo"
        r = record(p, kind, meta)
        r.update(w=w, h=h)
        if kind == "clip":
            r["dur"] = d
        lib.append(r)
    json.dump(lib, open(os.path.join(a.pool, "library.json"), "w"), indent=1, ensure_ascii=False)
    json.dump({r["file"]: r["tags"] for r in lib if r["tags"]}, open(os.path.join(a.pool, "tags.json"), "w"),
              indent=1, ensure_ascii=False)
    # credits, grouped by licence
    by = {}
    for r in lib:
        by.setdefault(r["licence"] or "unknown", []).append(r)
    with open(os.path.join(a.pool, "CREDITS.md"), "w") as f:
        f.write(f"# Credits - {os.path.basename(os.path.abspath(a.pool))}\n\n"
                "Every clip and picture in this pool, with the page it came from. Free-stock licences (Pexels,\n"
                "Pixabay) ask for no credit; anything else does - copy those lines into the video description.\n")
        for lic in sorted(by):
            f.write(f"\n## {lic} ({len(by[lic])} files)\n\n")
            for r in sorted(by[lic], key=lambda x: x["file"]):
                who = f" - {r['author']}" if r.get("author") else ""
                f.write(f"- `{r['file']}`{who} - {r['page'] or 'no page recorded'}\n")
    n_c = sum(1 for r in lib if r["kind"] == "clip")
    q = {}
    for r in lib:
        if r["query"]:
            q[r["query"]] = q.get(r["query"], 0) + 1
    with open(os.path.join(a.pool, "README.md"), "w") as f:
        f.write(f"""# {a.name or os.path.basename(os.path.abspath(a.pool))} - footage pool

{n_c} clips and {len(lib) - n_c} pictures, collected for earlier videos and kept for the next ones.
Everything here is free stock (Pexels / Pixabay) or freely licensed (Wikimedia); `CREDITS.md` lists
every file with its page and licence.

    clips/        the footage
    images/       the pictures
    library.json  one record per file: source, page, author, licence, the search it came from, tags
    tags.json     {{file: [tags]}} - give this to the kit so it can match pictures to sentences
    CREDITS.md    credits per licence
    sources_in.json  the raw download lists, kept so nothing loses its page

## Use it in the kit

    python make_video.py --title "..." --script script.txt --audio vo.mp3 --srt vo.srt \\
      --template almanac2 --folder "<this folder>"

or register it once as a niche and then just name it:

    python docu/studio/studio.py niche-add --name "{a.name or 'Pool'}" --folder "<this folder>" \\
      --clips clips --images images --tags "<this folder>/tags.json"
    python make_video.py ... --niche {re.sub(r'[^a-z0-9]+', '-', (a.name or 'pool').lower()).strip('-')}

## Add more to it

    python docu/tools/fetch_online.py --out /tmp/new --query "wisconsin dairy farm, ..." --clips 3 --photos 4
    python docu/tools/pool.py merge "<this folder>" /tmp/new
    python docu/tools/pool.py build "<this folder>"

## What the searches were

""")
        for k in sorted(q, key=lambda x: -q[x]):
            f.write(f"- {k} ({q[k]})\n")
    print(f"{len(lib)} files ({n_c} clips, {len(lib) - n_c} pictures) in {a.pool}")
    print(f"wrote library.json, tags.json, CREDITS.md, README.md")


# ------------------------------------------------------------------ sheets
def cmd_sheets(a):
    from PIL import Image, ImageDraw, ImageFont
    cl, im = files(a.pool)
    os.makedirs(a.out, exist_ok=True)
    font = None
    for p in ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf"):
        if os.path.exists(p):
            font = ImageFont.truetype(p, 15)
    tmp = os.path.join(a.out, "_th")
    os.makedirs(tmp, exist_ok=True)

    def thumb(p):
        q = os.path.join(tmp, stem(p) + ".jpg")
        if os.path.exists(q):
            return q
        if p.lower().endswith(VIDEO_EXT):
            subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", "1", "-i", p, "-vframes", "1",
                            "-vf", "scale=300:-2", q], capture_output=True)
        else:
            try:
                img = Image.open(p).convert("RGB"); img.thumbnail((300, 240)); img.save(q, quality=82)
            except Exception:
                return None
        return q if os.path.exists(q) else None

    for kind, lst in (("clips", cl), ("images", im)):
        if not lst:
            continue
        with ThreadPoolExecutor(8) as ex:
            ths = list(ex.map(thumb, lst))
        W, H, C, per = 300, 200, 7, 42
        for n in range(0, len(lst), per):
            part = list(zip(lst[n:n + per], ths[n:n + per]))
            rows = (len(part) + C - 1) // C
            sh = Image.new("RGB", (W * C, rows * (H + 24)), (14, 14, 16))
            d = ImageDraw.Draw(sh)
            for j, (p, th) in enumerate(part):
                x, y = (j % C) * W, (j // C) * (H + 24)
                if th:
                    try:
                        img = Image.open(th).convert("RGB"); img.thumbnail((W - 4, H - 4))
                        sh.paste(img, (x + 2 + (W - 4 - img.width) // 2, y + 2))
                    except Exception:
                        pass
                d.text((x + 4, y + H + 3), stem(p)[:46], fill=(235, 235, 225), font=font)
            out = os.path.join(a.out, f"{kind}_{n // per:02d}.jpg")
            sh.save(out, quality=80)
            print(out, len(part))


# ------------------------------------------------------------------ catalog
def cmd_catalog(a):
    cl, _ = files(a.pool)
    lib = {}
    p = os.path.join(a.pool, "library.json")
    if os.path.exists(p):
        lib = {r["file"]: r for r in json.load(open(p))}
    cat = []
    with ThreadPoolExecutor(8) as ex:
        dims = list(ex.map(probe, cl))
    for f, (w, h, d) in zip(cl, dims):
        if not d:
            continue
        r = lib.get(os.path.basename(f), {})
        cat.append(dict(i=len(cat), video=os.path.basename(f), s=0.0, e=d, w=w or 1920, h=h or 1080,
                        quality=4, flags=[], tags=r.get("tags", []), desc=r.get("desc", "")))
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    json.dump(cat, open(a.out, "w"), indent=0)
    print(len(cat), "clips ->", a.out)


def main():
    ap = argparse.ArgumentParser(description="keep one reusable footage pool per subject")
    sub = ap.add_subparsers(dest="cmd", required=True)
    m = sub.add_parser("merge"); m.add_argument("pool"); m.add_argument("new_dirs", nargs="+"); m.set_defaults(fn=cmd_merge)
    b = sub.add_parser("build"); b.add_argument("pool"); b.add_argument("--meta", nargs="*"); b.add_argument("--name")
    b.set_defaults(fn=cmd_build)
    s = sub.add_parser("sheets"); s.add_argument("pool"); s.add_argument("out"); s.set_defaults(fn=cmd_sheets)
    c = sub.add_parser("catalog"); c.add_argument("pool"); c.add_argument("out"); c.set_defaults(fn=cmd_catalog)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
