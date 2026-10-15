"""
places.py - coordinates and map ids for the places a script names, from the kit's own gazetteer
(Natural Earth: 258 countries, 4,596 states / provinces, 7,342 cities, rivers, regions) - no guessing on maps.

    python docu/tools/places.py find "Lancaster"            every match: kind, country, lon/lat, highlight id
    python docu/tools/places.py script data/script.txt      every place the script names, in order, ready for map()

A map scene uses: stops (lon, lat, scale), pins (label, lon, lat), highlight (id = the "id" printed here,
e.g. "USA-3560" for Pennsylvania, "PAK" for Pakistan), names, routes, dots.
Small towns and villages are not in the gazetteer (Natural Earth keeps larger places): look their coordinates
up and type them in. Scale guide: 400 the whole globe · 1,200 a continent · 3,500 a few states · 9,000 one state · 20,000 a county.
"""

import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
KIT = os.environ.get("VIDEO_KIT") or os.path.join(os.path.dirname(os.path.dirname(HERE)), "media", "kit")


def gaz():
    return json.load(open(os.path.join(KIT, "maps", "gazetteer.json"), encoding="utf-8"))


def _scale(bbox):
    if not bbox:
        return 9000
    span = max(bbox[2] - bbox[0], (bbox[3] - bbox[1]) * 1.6, 0.05)
    return int(max(380, min(60000, 9000 * 6.0 / span)))


def find(q, g=None, limit=12):
    g = g or gaz()
    ql = q.lower().strip()
    out = []
    for c in g["countries"]:
        if c.get("name") and (c["name"].lower() == ql or ql in [n.lower() for n in c.get("names", [])] or c.get("a3", "").lower() == ql):
            lon, lat = c.get("label") or [0, 0]
            out.append(dict(kind="country", name=c["name"], id=c["id"], lon=lon, lat=lat, scale=_scale(c.get("bbox")), rank=0))
    for a in g["admin1"]:
        names = [a.get("name") or "", a.get("alt") or "", a.get("gns") or ""]
        if any(n and n.lower() == ql for n in names):
            lon, lat = a.get("label") or [0, 0]
            out.append(dict(kind=a.get("type") or "admin1", name=a["name"], country=a.get("country"), id=a["id"],
                            lon=lon, lat=lat, scale=_scale(a.get("bbox")), rank=1))
    for c in g["cities"]:
        if c.get("name") and (c["name"].lower() == ql or ql in [n.lower() for n in c.get("names", [])]):
            out.append(dict(kind="city", name=c["name"], country=c.get("country"), adm1=c.get("adm1"), lon=c["lon"], lat=c["lat"],
                            pop=c.get("pop"), scale=20000, rank=2 + (c.get("rank") or 10) / 100))
    for r in g.get("regions", []) + g.get("water", []):
        if r.get("name") and r["name"].lower() == ql:
            lon, lat = r.get("label") or [0, 0]
            out.append(dict(kind=r.get("cls", "region"), name=r["name"], id=r.get("id"), lon=lon, lat=lat, scale=_scale(r.get("bbox")), rank=3))
    return sorted(out, key=lambda x: (x["rank"], -(x.get("pop") or 0)))[:limit]


def in_script(text, g=None):
    """every gazetteer name the script mentions, first mention first"""
    g = g or gaz()
    names = {}
    for c in g["countries"]:
        if c.get("name"):
            names[c["name"]] = 0
    for a in g["admin1"]:
        if a.get("name") and len(a["name"]) > 3:
            names.setdefault(a["name"], 1)
    for c in g["cities"]:
        if c.get("name") and len(c["name"]) > 3 and (c.get("rank") or 99) <= 8:
            names.setdefault(c["name"], 2)
    hits = []
    for n in names:
        m = re.search(r"(?<![A-Za-z])" + re.escape(n) + r"(?![A-Za-z])", text)
        if m:
            hits.append((m.start(), n))
    hits.sort()
    # context: the states / countries the script names decide which "Lancaster" or "Athens" is meant
    states = {n for _, n in hits if any(a.get("name") == n for a in g["admin1"] if a.get("a3") in ("USA", "CAN", "AUS", "GBR"))}
    countries = {n for _, n in hits if any(c.get("name") == n for c in g["countries"])}
    seen, out = set(), []
    for pos, n in hits:
        if any(n != o and n in o for _, o in hits):        # "York" inside "New York"
            continue
        if n in seen:
            continue
        seen.add(n)
        cands = find(n, g, limit=12)
        if not cands:
            continue
        pick = cands[0]
        if pick["kind"] not in ("country",) and (states or countries):
            local = [c for c in cands if c.get("adm1") in states or (c.get("kind") != "city" and c.get("country") in countries)
                     or (c.get("kind") != "city" and c.get("country") == "United States of America" and states)]
            local = local or [c for c in cands if c.get("country") in countries or
                              (states and c.get("country") == "United States of America")]
            if not local:
                continue                                  # a namesake elsewhere ("Young", "Kingston, Jamaica"): not this script's place
            pick = local[0]
        out.append(dict(pick, at_char=pos))
    return out


def main():
    if len(sys.argv) < 3 or sys.argv[1] not in ("find", "script"):
        print(__doc__)
        sys.exit(1)
    g = gaz()
    if sys.argv[1] == "find":
        for r in find(" ".join(sys.argv[2:]), g):
            extra = f"  {r.get('country', '')}{(' / ' + r['adm1']) if r.get('adm1') else ''}".rstrip()
            print(f"{r['kind']:12s} {r['name']:28s} lon {r['lon']:9.3f}  lat {r['lat']:8.3f}  scale ~{r['scale']:<6d}"
                  f"{'  id ' + r['id'] if r.get('id') else ''}{extra}")
    else:
        text = open(sys.argv[2], encoding="utf-8-sig").read()
        for r in in_script(text, g):
            print(f"{r['name']:28s} {r['kind']:10s} lon {r['lon']:9.3f}  lat {r['lat']:8.3f}  scale ~{r['scale']:<6d}"
                  f"{'  id ' + r['id'] if r.get('id') else ''}")


if __name__ == "__main__":
    main()
