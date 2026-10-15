"""
fetch_online.py - collect footage and pictures for a video from free online libraries (optional).

    python fetch_online.py --out <folder> --query "amish buggy, lancaster farm, horse plow"
    python fetch_online.py --out <folder> --script script.txt          # queries picked from the script
    options: --clips 6 --photos 8 (per query) --sources pexels,pixabay,wikimedia[,google] --max-seconds 20

Writes <folder>/clips/*.mp4 (1080p, 30 fps, no sound) and <folder>/images/*.jpg, named
"<query>__<source><id>" so the offline shot list can match them by name, and <folder>/sources.json
(every file with its page, author and licence - keep it for the video description).

Sources and keys (keys are read from the environment, api_keys/keys.env or your Frontier .env):
    pexels     PEXELS_API_KEY   videos + photos, Pexels licence (free, no attribution, no watermark)
    pixabay    PIXABAY_API_KEY  videos + photos, Pixabay content licence (free, no watermark)
    wikimedia  no key           photos under public-domain / CC licences (credit the author; CC BY-SA
                                means share-alike); slow (rate-limited), skipped politely when busy
    google     SERPER_API_KEY   Google Images through serper.dev - LICENCE UNKNOWN: off by default,
                                watermark/stock hosts are blocked, check every picture before publishing
Talking heads, logos and watermarks: the libraries above are stock/archival; still look at the contact
sheets (catalog step) and delete what you don't want.
"""

import argparse
import collections
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from keys import get as key      # noqa: E402

UA = {"User-Agent": "DocuTemplates/1.0 (documentary research tool)"}
BLOCK = ("shutterstock", "gettyimages", "istockphoto", "alamy", "dreamstime", "123rf", "depositphotos", "adobestock",
         "stock.adobe", "pinterest", "facebook", "instagram", "tiktok", "youtube", "vecteezy", "freepik", "pond5")
STOP = set("""a an the and or but of to in on at by for with from as is are was were be been being it its this that these those
they them their there here he she his her we our you your i me my not no so than then too very can could will would should
may might must do does did done have has had having into over under about after before between through during without
within more most less many much some any each every all both few other such only own same just also now when where why how
what which who whom whose while because if until again further once one two three four five six seven eight nine ten
hundred thousand million year years today ago yet still even like make made way people life world""".split())


def _get(url, headers=None, tries=4):
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=dict(UA, **(headers or {}))), timeout=60) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            if e.code == 429:
                time.sleep(15 * (i + 1))
                continue
            print(f"  ({urllib.parse.urlsplit(url).netloc}: HTTP {e.code}, skipped)", flush=True)
            return None
        except Exception:
            time.sleep(3)
    return None


def slug(s):
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")[:40] or "x"


# ------------------------------------------------------------------ sources
def pexels_videos(q, n):
    k = key("PEXELS_API_KEY")
    if not k:
        return []
    d = _get("https://api.pexels.com/videos/search?" + urllib.parse.urlencode(dict(query=q, per_page=max(n * 2, 10), orientation="landscape")),
             {"Authorization": k}) or {}
    out = []
    for v in d.get("videos", []):
        fs = sorted([f for f in v["video_files"] if (f.get("width") or 0) >= 1280 and f.get("file_type") == "video/mp4"],
                    key=lambda f: abs(f["width"] - 1920))
        if fs:
            out.append(dict(kind="clip", src="pexels", id=v["id"], url=fs[0]["link"], page=v["url"], dur=v["duration"],
                            author=(v.get("user") or {}).get("name", ""), licence="Pexels licence"))
    return out[:n]


def pixabay_videos(q, n):
    k = key("PIXABAY_API_KEY")
    if not k:
        return []
    d = _get("https://pixabay.com/api/videos/?" + urllib.parse.urlencode(dict(key=k, q=q, per_page=max(n * 2, 10)))) or {}
    out = []
    for v in d.get("hits", []):
        f = v["videos"].get("large") or v["videos"].get("medium")
        if f and f.get("url") and f.get("width", 0) >= 1280:
            out.append(dict(kind="clip", src="pixabay", id=v["id"], url=f["url"], page=v["pageURL"], dur=v["duration"],
                            author=v.get("user", ""), licence="Pixabay content licence"))
    return out[:n]


def pexels_photos(q, n):
    k = key("PEXELS_API_KEY")
    if not k:
        return []
    d = _get("https://api.pexels.com/v1/search?" + urllib.parse.urlencode(dict(query=q, per_page=max(n * 2, 10), orientation="landscape")),
             {"Authorization": k}) or {}
    return [dict(kind="photo", src="pexels", id=p["id"], url=p["src"]["original"], page=p["url"], author=p.get("photographer", ""),
                 licence="Pexels licence") for p in d.get("photos", [])][:n]


def pixabay_photos(q, n):
    k = key("PIXABAY_API_KEY")
    if not k:
        return []
    d = _get("https://pixabay.com/api/?" + urllib.parse.urlencode(dict(key=k, q=q, per_page=max(n * 2, 10), image_type="photo",
                                                                        orientation="horizontal"))) or {}
    return [dict(kind="photo", src="pixabay", id=p["id"], url=p["largeImageURL"], page=p["pageURL"], author=p.get("user", ""),
                 licence="Pixabay content licence") for p in d.get("hits", []) if p.get("imageWidth", 0) >= 1600][:n]


def wikimedia_photos(q, n):
    api = "https://commons.wikimedia.org/w/api.php?"
    s = _get(api + urllib.parse.urlencode(dict(action="query", list="search", srsearch=q + " filetype:bitmap", srnamespace=6,
                                               srlimit=max(n * 3, 15), format="json")), tries=2)
    titles = [r["title"] for r in ((s or {}).get("query") or {}).get("search", [])]
    if not titles:
        return []
    d = _get(api + urllib.parse.urlencode(dict(action="query", titles="|".join(titles[:40]), prop="imageinfo",
                                               iiprop="url|size|extmetadata", iiurlwidth=2400, format="json")), tries=2) or {}
    out = []
    for p in (d.get("query") or {}).get("pages", {}).values():
        ii = (p.get("imageinfo") or [{}])[0]
        em = ii.get("extmetadata", {})
        lic = (em.get("LicenseShortName") or {}).get("value", "")
        if not re.search(r"public domain|pd|cc0|cc by", lic, re.I) or (ii.get("width") or 0) < 1400:
            continue
        artist = re.sub(r"<[^>]+>", "", (em.get("Artist") or {}).get("value", ""))[:80]
        out.append(dict(kind="photo", src="wikimedia", id=abs(hash(p["title"])) % 10 ** 9, url=ii.get("thumburl") or ii.get("url"),
                        page=ii.get("descriptionurl"), author=artist, licence=lic))
    return out[:n]


def google_photos(q, n):
    k = key("SERPER_API_KEY")
    if not k:
        return []
    req = urllib.request.Request("https://google.serper.dev/images", data=json.dumps(dict(q=q, num=max(n * 3, 20))).encode(),
                                 headers={"X-API-KEY": k, "Content-Type": "application/json"}, method="POST")
    try:
        d = json.loads(urllib.request.urlopen(req, timeout=40).read())
    except Exception:
        return []
    out = []
    for i, r in enumerate(d.get("images", [])):
        u = r.get("imageUrl", "")
        if any(b in (u + r.get("link", "")).lower() for b in BLOCK) or (r.get("imageWidth") or 0) < 1400:
            continue
        out.append(dict(kind="photo", src="google", id=abs(hash(u)) % 10 ** 9, url=u, page=r.get("link"), author=r.get("source", ""),
                        licence="UNKNOWN - check before publishing"))
    return out[:n]


VIDEO = {"pexels": pexels_videos, "pixabay": pixabay_videos}
PHOTO = {"pexels": pexels_photos, "pixabay": pixabay_photos, "wikimedia": wikimedia_photos, "google": google_photos}


# ------------------------------------------------------------------ download
def fetch_clip(item, path, max_s):
    raw = path + ".part"
    try:
        req = urllib.request.Request(item["url"], headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=300) as r, open(raw, "wb") as f:
            while True:
                b = r.read(1 << 20)
                if not b:
                    break
                f.write(b)
        dur = float(item.get("dur") or 10)
        ss = 0.4 if dur > 6 else 0
        r = subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(ss), "-i", raw, "-t", f"{min(dur - ss - 0.2, max_s):.2f}", "-an",
                            "-vf", "scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,fps=30,format=yuv420p",
                            "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", path], capture_output=True, text=True)
        return r.returncode == 0
    except Exception:
        return False
    finally:
        if os.path.exists(raw):
            os.remove(raw)


def fetch_photo(item, path):
    try:
        import io
        from PIL import Image
        data = urllib.request.urlopen(urllib.request.Request(item["url"], headers={"User-Agent": "Mozilla/5.0"}), timeout=120).read()
        im = Image.open(io.BytesIO(data)).convert("RGB")
        if im.width < 1200:
            return False
        im.thumbnail((2560, 2560))
        im.save(path, quality=90)
        return True
    except Exception:
        return False


def queries_from_script(text, title="", n=12):
    """the script's most repeated content words and two-word phrases (proper names first)"""
    words = re.findall(r"[A-Za-z][A-Za-z'-]+", text)
    low = [w.lower() for w in words]
    names = collections.Counter(w for w in words if w[0].isupper() and w.lower() not in STOP and len(w) > 3)
    bi = collections.Counter(f"{a} {b}" for a, b in zip(low, low[1:]) if a not in STOP and b not in STOP and len(a) > 3 and len(b) > 3)
    uni = collections.Counter(w for w in low if w not in STOP and len(w) > 4)
    topic = " ".join(w for w in re.findall(r"[A-Za-z]+", title) if w.lower() not in STOP)[:40]
    qs = [topic] if topic else []
    qs += [p for p, c in bi.most_common(n) if c > 1]
    qs += [w for w, c in names.most_common(6)]
    qs += [w for w, c in uni.most_common(n)]
    out = []
    for q in qs:
        if q and q.lower() not in [o.lower() for o in out]:
            out.append(q)
    return out[:n]


def main():
    ap = argparse.ArgumentParser(description="collect free footage and pictures for a video")
    ap.add_argument("--out", required=True)
    ap.add_argument("--query", help="comma-separated searches")
    ap.add_argument("--script", help="pick searches from this script")
    ap.add_argument("--title", default="")
    ap.add_argument("--clips", type=int, default=6)
    ap.add_argument("--photos", type=int, default=8)
    ap.add_argument("--sources", default="pexels,pixabay,wikimedia")
    ap.add_argument("--max-seconds", type=float, default=20)
    a = ap.parse_args()
    qs = [q.strip() for q in (a.query or "").split(",") if q.strip()]
    if a.script:
        qs += queries_from_script(open(a.script, encoding="utf-8-sig").read(), a.title)
    if not qs:
        sys.exit("give --query or --script")
    srcs = [s.strip() for s in a.sources.split(",") if s.strip()]
    if not any(key(k) for k in ("PEXELS_API_KEY", "PIXABAY_API_KEY")):
        print("note: no PEXELS_API_KEY / PIXABAY_API_KEY - only Wikimedia photos (and no clips) will be fetched")
    cdir, idir = os.path.join(a.out, "clips"), os.path.join(a.out, "images")
    os.makedirs(cdir, exist_ok=True); os.makedirs(idir, exist_ok=True)
    srcf = os.path.join(a.out, "sources.json")
    sources = json.load(open(srcf)) if os.path.exists(srcf) else {}
    jobs, seen = [], set(sources)
    for q in qs:
        found = []
        for s in srcs:
            if s in VIDEO and a.clips:
                found += [x for x in VIDEO[s](q, a.clips)]
            if s in PHOTO and a.photos:
                found += [x for x in PHOTO[s](q, a.photos)]
        nc = np_ = 0
        for it in found:
            name = f"{slug(q)}__{it['src'][:2]}{it['id']}"
            if name in seen:
                continue
            if it["kind"] == "clip" and nc < a.clips:
                nc += 1
            elif it["kind"] == "photo" and np_ < a.photos:
                np_ += 1
            else:
                continue
            seen.add(name)
            jobs.append((name, q, it))
        print(f"{q}: {nc} clips, {np_} photos", flush=True)
    done = [0]

    def run(job):
        name, q, it = job
        if it["kind"] == "clip":
            ok = fetch_clip(it, os.path.join(cdir, name + ".mp4"), a.max_seconds)
        else:
            ok = fetch_photo(it, os.path.join(idir, name + ".jpg"))
        done[0] += 1
        print(f"{done[0]} / {len(jobs)} {name} {'ok' if ok else 'failed'}", flush=True)
        if ok:
            return name, dict(query=q, kind=it["kind"], source=it["src"], page=it.get("page"), author=it.get("author"),
                              licence=it.get("licence"))
        return None
    with ThreadPoolExecutor(4) as ex:
        for r in ex.map(run, jobs):
            if r:
                sources[r[0]] = r[1]
    json.dump(sources, open(srcf, "w"), indent=1, ensure_ascii=False)
    n_c = sum(1 for v in sources.values() if v["kind"] == "clip")
    print(f"{n_c} clips and {len(sources) - n_c} photos in {a.out} (sources.json lists every page and licence)")


if __name__ == "__main__":
    main()
