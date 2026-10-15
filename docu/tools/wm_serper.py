"""Wikimedia Commons photos found through Serper (commons.wikimedia.org is unreachable here; the en.wikipedia API
serves the same Commons file info, and upload.wikimedia.org serves the files). Free licences only.
usage: python wm_serper.py <out_dir> <per_query> "q1, q2, ..."
"""
import json, os, re, sys, time, urllib.parse, urllib.request

KIT = r"C:\Users\ninja\Downloads\X Colab Automation\DocuTemplates_Kit_v2\DocuTemplates_Kit"
sys.path.insert(0, os.path.join(KIT, "docu", "tools"))
from keys import get as key  # noqa: E402

UA = {"User-Agent": "DocuTemplates/1.0 (documentary research tool)"}
OUT, N, QUERIES = sys.argv[1], int(sys.argv[2]), [q.strip() for q in sys.argv[3].split(",") if q.strip()]
os.makedirs(OUT, exist_ok=True)
srcf = os.path.join(OUT, "sources.json")
sources = json.load(open(srcf, encoding="utf-8")) if os.path.exists(srcf) else {}
seen_titles = {v.get("title") for v in sources.values()}


def get(url, data=None, headers=None, raw=False):
    for i in range(3):
        try:
            req = urllib.request.Request(url, data=data, headers=dict(UA, **(headers or {})))
            with urllib.request.urlopen(req, timeout=60) as r:
                b = r.read()
                return b if raw else json.loads(b)
        except Exception as e:  # noqa: BLE001
            err = e
            time.sleep(2 * (i + 1))
    print("   fail", url[:90], err)
    return None


def serper(q):
    k = key("SERPER_API_KEY")
    titles = []
    for ep in ("images", "search"):
        d = get(f"https://google.serper.dev/{ep}", data=json.dumps(dict(q=q + " site:commons.wikimedia.org")).encode(),
                headers={"X-API-KEY": k, "Content-Type": "application/json"}) or {}
        for r in d.get("images", []) + d.get("organic", []):
            for u in (r.get("link", ""), r.get("imageUrl", "")):
                m = re.search(r"commons\.wikimedia\.org/wiki/(File:[^?#]+)", u)
                if m:
                    titles.append(urllib.parse.unquote(m.group(1)).replace("_", " "))
                m = re.search(r"upload\.wikimedia\.org/wikipedia/commons/(?:thumb/)?[0-9a-f]/[0-9a-f]{2}/([^/?#]+)", u)
                if m:
                    titles.append("File:" + urllib.parse.unquote(m.group(1)).replace("_", " "))
    out = []
    for t in titles:
        if t not in out and re.search(r"\.(jpe?g|png|tiff?|webp)$", t, re.I):
            out.append(t)
    return out


def info(titles):
    api = "https://en.wikipedia.org/w/api.php?"
    d = get(api + urllib.parse.urlencode(dict(action="query", titles="|".join(titles[:40]), prop="imageinfo",
                                              iiprop="url|size|extmetadata", iiurlwidth=1920, format="json"))) or {}
    res = []
    for p in (d.get("query") or {}).get("pages", {}).values():
        ii = (p.get("imageinfo") or [{}])[0]
        em = ii.get("extmetadata", {})
        lic = (em.get("LicenseShortName") or {}).get("value", "")
        if not re.search(r"public domain|pd|cc0|cc by", lic, re.I) or (ii.get("width") or 0) < 1200:
            continue
        artist = re.sub(r"<[^>]+>", "", (em.get("Artist") or {}).get("value", ""))[:80]
        res.append(dict(title=p["title"], url=ii.get("thumburl") or ii.get("url"), page=ii.get("descriptionurl"),
                        author=artist, licence=lic))
    return res


for q in QUERIES:
    slug = re.sub(r"[^a-z0-9]+", "_", q.lower()).strip("_")[:40]
    got = 0
    titles = [t for t in serper(q) if t not in seen_titles]
    for it in info(titles):
        if got >= N:
            break
        fid = abs(hash(it["title"])) % 10 ** 9
        name = f"{slug}__wm{fid}.jpg"
        time.sleep(2.5)
        b = get(it["url"], raw=True)
        if not b or len(b) < 30000:
            continue
        open(os.path.join(OUT, name), "wb").write(b)
        sources[name] = dict(kind="photo", src="wikimedia", query=q, **it)
        seen_titles.add(it["title"])
        got += 1
    print(f"{q}: {got} photos", flush=True)
    json.dump(sources, open(srcf, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print(f"{len(sources)} photos in {OUT}")
