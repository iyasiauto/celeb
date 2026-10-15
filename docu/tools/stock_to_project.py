"""link stock_library clips into a project's footage (src/clips + src/qc.json + data/catalog_all.json)
usage: python add_stock.py <media slug> <project dir> <topic> [<topic> ...]"""
import json, os, shutil, subprocess, sys

KIT = r"C:\Users\ninja\Downloads\X Colab Automation\DocuTemplates_Kit_v2\DocuTemplates_Kit"
STOCK = os.path.join(KIT, "stock_library")
slug, proj, topics = sys.argv[1], sys.argv[2], sys.argv[3:]
src = os.path.join(KIT, "workspaces", "hasidic", "media", slug, "src")
clips = os.path.join(src, "clips")
sq = json.load(open(os.path.join(STOCK, "qc.json"), encoding="utf-8"))
qp = os.path.join(src, "qc.json")
q = json.load(open(qp, encoding="utf-8"))
cp = os.path.join(proj, "data", "catalog_all.json")
cat = json.load(open(cp, encoding="utf-8"))
have = {c["video"] for c in cat}
nxt = max(c.get("i", -1) for c in cat) + 1
for f in sorted(os.listdir(os.path.join(STOCK, "clips"))):
    t = f[6:].split("__")[0]
    if t not in topics or sq.get(f, {}).get("reject", True):
        continue
    p = os.path.join(STOCK, "clips", f)
    d = os.path.join(clips, f)
    if not os.path.exists(d):
        try:
            os.link(p, d)
        except OSError:
            shutil.copy2(p, d)
    q[f] = sq[f]
    if f in have:
        continue
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                        "stream=width,height:format=duration", "-of", "json", p], capture_output=True, text=True)
    j = json.loads(r.stdout or "{}")
    st = (j.get("streams") or [{}])[0]
    dur = float((j.get("format") or {}).get("duration") or 0)
    v = sq[f]
    cat.append(dict(video=f, s=0.0, e=round(min(dur, 20.0), 2), w=st.get("width", 1920), h=st.get("height", 1080),
                    i=nxt, quality=v.get("quality", 3), flags=[], tags=v.get("tags", []), desc=v.get("desc", "")))
    print(f"  {nxt}: {f}  {dur:.1f}s")
    nxt += 1
json.dump(q, open(qp, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
json.dump(cat, open(cp, "w", encoding="utf-8"), indent=0, ensure_ascii=False)
