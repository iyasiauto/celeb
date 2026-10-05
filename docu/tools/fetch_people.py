"""
fetch_people.py - pictures of named people (celebrity / nostalgia niches) from Google Images (serper.dev) and
Wikimedia Commons: no stock sites, no watermark hosts, at least 600 px, de-duplicated. Every file goes through
qc_pool.py afterwards (celebrity mode keeps the person's own photos, drops logos, chyrons, watermarks).

    python fetch_people.py --out <pool>/images --people people.json [--per 8]
    people.json: [{"name": "River Phoenix", "queries": ["River Phoenix", "River Phoenix Stand By Me 1986"]}, ...]

Files: <out>/<person_slug>__g<hash>.jpg, and <out>/../people_sources.json (page + host of every picture).
"""
import argparse, hashlib, io, json, os, re, sys, urllib.request
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from keys import get as key
from PIL import Image
BLOCK = ("shutterstock", "gettyimages", "istockphoto", "alamy", "dreamstime", "123rf", "depositphotos", "adobestock", "stock.adobe",
         "pinterest", "facebook", "instagram", "tiktok", "vecteezy", "freepik", "pond5", "wireimage", "zimbio", "bridgeman",
         "agefotostock", "mediastorehouse", "photopin", "featurepics", "superstock", "granger", "mirrorpix", "rexfeatures",
         "shutterstock", "imago-images", "dpa-picture", "picryl", "lookaside")
UA = {"User-Agent": "Mozilla/5.0 (documentary research tool)"}
def slug(s): return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")
def serper(q, n=40):
    req = urllib.request.Request("https://google.serper.dev/images", data=json.dumps(dict(q=q, num=n)).encode(),
                                 headers={"X-API-KEY": key("SERPER_API_KEY"), "Content-Type": "application/json"}, method="POST")
    try:
        return json.loads(urllib.request.urlopen(req, timeout=40).read()).get("images", [])
    except Exception as e:
        print("  serper:", e); return []
def commons(q, n=10):
    u = ("https://commons.wikimedia.org/w/api.php?action=query&format=json&generator=search&gsrnamespace=6&gsrlimit=%d"
         "&prop=imageinfo&iiprop=url|size&iiurlwidth=1600&gsrsearch=%s" % (n, urllib.parse.quote(q)))
    try:
        d = json.loads(urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=40).read())
    except Exception:
        return []
    out = []
    for p in (d.get("query", {}).get("pages", {}) or {}).values():
        ii = (p.get("imageinfo") or [{}])[0]
        if ii.get("thumburl") and re.search(r"\.(jpe?g|png)$", ii.get("url", ""), re.I):
            out.append(dict(imageUrl=ii["thumburl"], link=ii.get("descriptionurl"), source="wikimedia", imageWidth=ii.get("width"), imageHeight=ii.get("height")))
    return out
import urllib.parse
def get(item, dst):
    try:
        b = urllib.request.urlopen(urllib.request.Request(item["imageUrl"], headers=UA), timeout=30).read()
        im = Image.open(io.BytesIO(b)); im.load()
        if max(im.size) < 600 or min(im.size) < 380:
            return None
        im = im.convert("RGB")
        if max(im.size) > 2400:
            im.thumbnail((2400, 2400))
        im.save(dst, quality=92)
        return dict(file=os.path.basename(dst), page=item.get("link"), host=item.get("source"), w=im.width, h=im.height)
    except Exception:
        return None
def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--out", required=True); ap.add_argument("--people", required=True)
    ap.add_argument("--per", type=int, default=8); a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    people = json.load(open(a.people, encoding="utf-8"))
    src_p = os.path.join(os.path.dirname(os.path.abspath(a.out)), "people_sources.json")
    sources = json.load(open(src_p)) if os.path.exists(src_p) else []
    seen_url = {s.get("url") for s in sources}
    for person in people:
        ps = slug(person["name"])
        have = len([f for f in os.listdir(a.out) if f.startswith(ps + "__")])
        if have >= a.per:
            continue
        cands = commons(person["name"])
        for q in person.get("queries") or [person["name"]]:
            cands += serper(q)
        pick, hosts = [], {}
        for c in cands:
            u, link = c.get("imageUrl", ""), (c.get("link") or "")
            if not u or u in seen_url or any(b in (u + link).lower() for b in BLOCK):
                continue
            if (c.get("imageWidth") or 9999) < 600 and (c.get("imageHeight") or 9999) < 600:
                continue
            h = (c.get("source") or "").lower()
            if hosts.get(h, 0) >= 3:            # spread over sites: fewer copies of the same press photo
                continue
            hosts[h] = hosts.get(h, 0) + 1
            pick.append(c)
        jobs, dsts = [], set()
        for c in pick[: a.per * 2]:
            hid = hashlib.md5(c["imageUrl"].encode()).hexdigest()[:8]
            dst = os.path.join(a.out, f"{ps}__g{hid}.jpg")
            if dst not in dsts and not os.path.exists(dst):
                dsts.add(dst); jobs.append((c, dst))
        with ThreadPoolExecutor(8) as ex:
            res = list(ex.map(lambda j: get(*j), jobs))
        # drop near-duplicates (same picture, different size)
        kept, sigs = have, []
        for (c, dst), r in zip(jobs, res):
            if not r or not os.path.exists(dst):
                continue
            im = Image.open(dst).convert("L").resize((12, 12))
            px = list(im.tobytes()); m = sum(px) / len(px); sig = [p > m for p in px]
            if any(sum(x != y for x, y in zip(sig, s)) < 14 for s in sigs) or kept >= a.per:
                os.remove(dst); continue
            sigs.append(sig); kept += 1
            sources.append(dict(r, person=person["name"], url=c["imageUrl"]))
        print(f"{person['name']}: {kept} pictures")
        json.dump(sources, open(src_p, "w"), indent=0)
if __name__ == "__main__":
    main()
