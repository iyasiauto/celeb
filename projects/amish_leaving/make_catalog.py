"""data/catalog_all.json from the clips in media/amish/src/clips (one shot per file), and data/sources.json
(every clip and photograph with its source page and licence) from the download lists."""
import json, os, subprocess, glob, sys
HERE = os.path.dirname(os.path.abspath(__file__))
SP = os.environ.get("VIDEO_ROOT", os.path.join(HERE, "..", "..", "media"))
clips = sorted(glob.glob(f"{SP}/amish/src/clips/*.mp4"))
cat = []
for f in clips:
    d = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f], capture_output=True, text=True).stdout.strip()
    if not d:
        continue                                   # still downloading
    cat.append(dict(i=len(cat), video=os.path.basename(f), s=0.0, e=round(float(d), 2), w=1920, h=1080, quality=4, flags=[], tags=[], desc=""))
json.dump(cat, open(f"{HERE}/data/catalog_all.json", "w"), indent=0)
print(len(cat), "clips")
if len(sys.argv) > 1:                              # the download lists (scratch) -> sources.json
    src = {}
    for p in sys.argv[1:]:
        for k, v in json.load(open(p)).items():
            src[k] = dict(source=v["src"], page=v.get("page"), licence="Pexels licence" if v["src"] == "pexels" else "Pixabay content licence")
    json.dump(src, open(f"{HERE}/data/sources.json", "w"), indent=1)
