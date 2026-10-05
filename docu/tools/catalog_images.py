"""
catalog_images.py - sort a folder of pictures into topic contact sheets, then stage the ones you pick
under short keys (money_00_4, street_01_12 ...) that build.py refers to.

Step 1  scan: size, near-duplicate hash and flatness of every picture; contact sheets per topic.

    python catalog_images.py scan <images_dir> <cat_dir> [--topic-regex '^([a-z_]+?)_[0-9a-f]{16}\\.']

    topic     taken from the file name with --topic-regex (group 1); files that don't match go to
              "named". Drive folders exported per topic (money_*.jpg, street_*.jpg) sort themselves.
    drops     near-duplicates (same average hash), pictures under 500 px wide, flat/blank ones.
    writes    <cat_dir>/images_clean.json   [{"file", "topic", "sheet", "pos", "w", "h"}]
              <cat_dir>/sheets_img/<topic>_<nn>.jpg   8 x 7 thumbnails, each labelled "pos WxH"

Step 2  look at the sheets and write <cat_dir>/notes_img.txt, one line per picture you might use:

    # sheet:pos|tags|description
    money_00:4|ebt,snap|hand holding a Minnesota EBT card
    institutions_00:9|hatzalah|Hatzalah ambulance on a street

Step 3  pick: stage the chosen pictures as <picks_dir>/<sheet>_<pos>.jpg (symlinks) and write
        data/image_picks.json. In build.py, ph("money_00_4") then finds the picture by that key.

    python catalog_images.py pick <cat_dir> <images_dir> <picks_dir> <project>/data/image_picks.json

On a fresh machine with the same footage, re-create picks/ straight from a project's image_picks.json:

    python catalog_images.py stage <project>/data/image_picks.json <images_dir> <picks_dir>

List picks by tag, marking the ones earlier videos already used:

    python catalog_images.py list <project>/data/image_picks.json [--unused <projects_root>]
"""

import argparse
import glob
import json
import os
import re
from concurrent.futures import ThreadPoolExecutor

from PIL import Image, ImageDraw, ImageFont

IMG_EXT = (".jpg", ".jpeg", ".png", ".webp")
COLS, ROWS, TW, TH = 8, 7, 240, 150


def _link(src, dst):
    """symlink, else hard link, else copy (Windows without developer mode can't symlink)"""
    src = os.path.abspath(src)
    for f in (os.symlink, os.link):
        try:
            return f(src, dst)
        except OSError:
            pass
    import shutil
    shutil.copy2(src, dst)


def _font(size):
    for p in ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"):
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def info(path, topic_re):
    f = os.path.basename(path)
    m = re.match(topic_re, f)
    topic = m.group(1) if m else "named"
    try:
        im = Image.open(path)
        w, h = im.size
        px = list(im.convert("L").resize((16, 16)).tobytes())
        avg = sum(px) / 256
        return dict(file=f, topic=topic, w=w, h=h, hash="".join("1" if v > avg else "0" for v in px),
                    std=round((sum((v - avg) ** 2 for v in px) / 256) ** 0.5, 1))
    except Exception as e:
        return dict(file=f, topic=topic, w=0, h=0, hash="", std=0, err=str(e)[:80])


def _qc_rejected(src):
    """pictures the vision QC rejected never reach a contact sheet (talking heads, influencers, logos...)"""
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    try:
        import qc_guard
    except Exception:
        return set()
    qc = qc_guard._load(qc_guard.find_qc(os.path.abspath(src)))
    return {os.path.basename(k) for k, v in qc.items() if v.get("reject")}


def _origin(picks, key_file, orig_file):
    """picks/_origin.json: staged name -> the original file, so the QC gate can trace a copied pick back to it"""
    p = os.path.join(picks, "_origin.json")
    try:
        m = json.load(open(p, encoding="utf-8"))
    except Exception:
        m = {}
    m[key_file] = orig_file
    json.dump(m, open(p, "w", encoding="utf-8"), indent=0)


def scan(src, cat, topic_re):
    bad = _qc_rejected(src)
    files = sorted(f for f in os.listdir(src) if f.lower().endswith(IMG_EXT) and f not in bad)
    if bad:
        print(len(bad), "pictures left out (rejected by QC)")
    with ThreadPoolExecutor(8) as ex:
        rows = list(ex.map(lambda f: info(os.path.join(src, f), topic_re), files))
    seen, clean = set(), []
    for r in rows:
        if r.get("err") or r["w"] < 500 or r["std"] < 12 or r["hash"] in seen:
            continue
        seen.add(r["hash"])
        clean.append(r)
    out = f"{cat}/sheets_img"
    os.makedirs(out, exist_ok=True)
    for f in glob.glob(f"{out}/*.jpg"):
        os.remove(f)
    font = _font(13)
    by = {}
    for r in clean:
        by.setdefault(r["topic"], []).append(r)
    n = 0
    for topic in sorted(by):
        lst = by[topic]
        for p in range(0, len(lst), COLS * ROWS):
            sheet = f"{topic}_{p // (COLS * ROWS):02d}"
            sh = Image.new("RGB", (COLS * TW, ROWS * (TH + 18)), "black")
            d = ImageDraw.Draw(sh)
            for i, r in enumerate(lst[p:p + COLS * ROWS]):
                x, y = (i % COLS) * TW, (i // COLS) * (TH + 18)
                try:
                    im = Image.open(os.path.join(src, r["file"])).convert("RGB")
                    im.thumbnail((TW - 4, TH - 4))
                    sh.paste(im, (x + 2, y + 2))
                except Exception:
                    pass
                r["sheet"], r["pos"] = sheet, i
                d.text((x + 2, y + TH + 1), f"{i} {r['w']}x{r['h']}", fill="yellow", font=font)
            sh.save(f"{out}/{sheet}.jpg", quality=78)
            n += 1
    json.dump(clean, open(f"{cat}/images_clean.json", "w"), indent=0)
    print(len(rows), "pictures;", len(clean), "kept on", n, "sheets;", sorted(by))


def pick(cat, src, picks, dst):
    clean = {(r["sheet"], r["pos"]): r for r in json.load(open(f"{cat}/images_clean.json"))}
    os.makedirs(picks, exist_ok=True)
    out = []
    for line in open(f"{cat}/notes_img.txt", encoding="utf-8"):
        if not line.strip() or line.startswith("#"):
            continue
        ref, tags, desc = line.rstrip("\n").split("|", 2)
        sheet, pos = ref.split(":")
        r = clean.get((sheet, int(pos)))
        if not r:
            print("  not on a sheet:", ref)
            continue
        key = f"{sheet}_{pos}"
        ext = os.path.splitext(r["file"])[1].lower()
        link = os.path.join(picks, key + (ext if ext in (".jpg", ".png", ".jpeg") else ".jpg"))
        if not os.path.exists(link):
            _link(os.path.join(src, r["file"]), link)
        _origin(picks, os.path.basename(link), r["file"])
        out.append(dict(key=key, file=r["file"], w=r["w"], h=r["h"], tags=[t for t in tags.split(",") if t], desc=desc))
    os.makedirs(os.path.dirname(os.path.abspath(dst)), exist_ok=True)
    json.dump(out, open(dst, "w"), indent=0)
    print(len(out), "pictures staged in", picks, "->", dst)


def stage(picks_json, src, picks):
    """Re-create picks/<key>.jpg links from an existing image_picks.json (a fresh machine, same footage)."""
    os.makedirs(picks, exist_ok=True)
    n = miss = 0
    for r in json.load(open(picks_json)):
        p = os.path.join(src, r["file"])
        if not os.path.exists(p):
            miss += 1
            continue
        ext = os.path.splitext(r["file"])[1].lower()
        link = os.path.join(picks, r["key"] + (ext if ext in (".jpg", ".png", ".jpeg") else ".jpg"))
        if not os.path.lexists(link):
            _link(p, link)
        _origin(picks, os.path.basename(link), r["file"])
        n += 1
    print(n, "picks staged in", picks, f"({miss} missing from {src})" if miss else "")


def list_picks(picks_json, unused_root=None):
    used = set()
    if unused_root:
        for p in glob.glob(os.path.join(unused_root, "*", "data", "assets_used.json")):
            used |= set(json.load(open(p)).get("images", []))
    by = {}
    for r in json.load(open(picks_json)):
        by.setdefault((r["tags"] or ["untagged"])[0], []).append(r)
    for t, l in sorted(by.items(), key=lambda x: -len(x[1])):
        print(f"== {t} ({len(l)})")
        for r in l:
            print(f"  {r['key']:24s} {'(used) ' if r['key'] in used else ''}{r['desc']}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("scan"); a.add_argument("src"); a.add_argument("cat")
    a.add_argument("--topic-regex", default=r"^([a-z_]+?)_[0-9a-f]{16}\.")
    b = sub.add_parser("pick"); b.add_argument("cat"); b.add_argument("src"); b.add_argument("picks"); b.add_argument("dst")
    c = sub.add_parser("list"); c.add_argument("picks_json"); c.add_argument("--unused")
    d = sub.add_parser("stage"); d.add_argument("picks_json"); d.add_argument("src"); d.add_argument("picks")
    x = ap.parse_args()
    if x.cmd == "scan":
        scan(x.src, x.cat, x.topic_regex)
    elif x.cmd == "stage":
        stage(x.picks_json, x.src, x.picks)
    elif x.cmd == "pick":
        pick(x.cat, x.src, x.picks, x.dst)
    else:
        list_picks(x.picks_json, x.unused)
