"""
project.py - workspace layout, niches, styles, and turning a job into a project folder.

Workspace (the repo):  <W>/docu  <W>/projects/<slug>/  <W>/media/{kit, <niche folders>, work/<slug>, out}
A job (from the app) is a dict:
    title, niche, style, clip_share, script (path), voice {mode: famespeak|file, ...},
    shotlist (claude|auto), ai_qa, model, deliver {upload, limit_gb}, workers
"""

import glob
import json
import os
import re
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
DOCU = os.path.dirname(HERE)

STYLES = {
    "documentary": dict(name="Calm documentary", letter="E", example="projects/hasidic_benefits_cut",
                        blurb="Slow photographs, soft dissolves, serif chapter headings, place captions, gentle charts, one recurring device. Look shuffled per video.",
                        sfx="calm", xfade=0.6, preview="templates/previews/documentary/doctitle.jpg", sheet="templates/previews/sheet_documentary.jpg", readme="Style E"),
    "paper": dict(name="Paper / Vox explainer", letter="A", example="projects/noahs_ark",
                  blurb="Paper tabletop collages, cut-outs, typed strips, stamps, newspaper pages, ledger arithmetic.",
                  sfx="full", xfade=0.0, preview="templates/previews/paper/collage.jpg", sheet="templates/previews/sheet_paper.jpg", readme="Style A"),
    "forensic": dict(name="Forensic lab report", letter="B", example="projects/noahs_ark_100",
                     blurb="Observed / Claimed / Confirmed filter, certainty gauge, scans, one-source network.",
                     sfx="full", xfade=0.0, preview="templates/previews/forensic/filter.jpg", sheet="templates/previews/sheet_forensic.jpg", readme="Style B"),
    "expedition": dict(name="Expedition & courtroom", letter="C", example="projects/noahs_ark_myth",
                       blurb="Field journal, antique map routes, evidence tags, scales of justice, scoreboard, verdict.",
                       sfx="full", xfade=0.0, preview="templates/previews/expedition/scales.jpg", sheet="templates/previews/sheet_expedition.jpg", readme="Style C"),
    "broadcast": dict(name="Breaking-news broadcast", letter="D", example="projects/noahs_ark_breaking",
                      blurb="LIVE bug and ticker, BREAKING slab, fact-check meters, headline wall, segment bumpers.",
                      sfx="full", xfade=0.0, preview="templates/previews/broadcast/breaking.jpg", sheet="templates/previews/sheet_broadcast.jpg", readme="Style D"),
    "almanac": dict(name="Heritage almanac", letter="F", example="projects/amish_two_states",
                    blurb="Updated edition: engraved caps on a letterpress plate over moving footage, didone figures, "
                          "ledger-slip key points, a surveyor's pencil for the notes, state-against-state comparisons, "
                          "giants-against-dots, dividing districts, index pages, and a plat map with a township grid. "
                          "Slate ink on oatmeal paper. Slow and calm.",
                    sfx="calm", xfade=0.55, preview="templates/previews/almanac2/gzhead.jpg",
                    sheet="templates/previews/sheet_almanac2.jpg", readme="Style F"),
}


def custom_styles(w):
    """your own templates: <workspace>/styles/<name>/style.json (re-read every time, so new folders show up at once)

    style.json: {"name": "Cold Case Files", "theme": "forensic", "blurb": "...", "letter": "G",
                 "example": "build.py" (a finished shot list in this style, optional),
                 "rules": "rules.md" (how this style is edited, optional),
                 "preview": "preview.jpg", "sample": "sample.mp4", "sfx": "full|calm", "xfade": 0.0}
    """
    out = {}
    for p in sorted(glob.glob(os.path.join(w, "styles", "*", "style.json"))):
        d0 = os.path.dirname(p)
        if os.path.basename(d0).startswith("_"):
            continue                                   # _example and other parked templates
        try:
            d = json.load(open(p, encoding="utf-8"))
        except Exception:
            continue
        theme = d.get("theme", "documentary")
        if theme not in STYLES:
            theme = "documentary"
        base = STYLES[theme]
        f = lambda k: os.path.join(d0, d[k]) if d.get(k) and os.path.exists(os.path.join(d0, d[k])) else None
        out["custom:" + os.path.basename(d0)] = dict(
            name=d.get("name") or os.path.basename(d0), letter=d.get("letter", "★"), blurb=d.get("blurb", ""),
            theme=theme, sfx=d.get("sfx", base["sfx"]), xfade=float(d.get("xfade", base["xfade"])), readme=base["readme"],
            example_path=f("example") or os.path.join(os.path.dirname(DOCU), base["example"], "build.py"),
            rules_path=f("rules"), preview_path=f("preview") or os.path.join(DOCU, base["preview"]),
            sample_path=f("sample"), engine="docu", folder=d0)
    return out


def all_styles(w):
    """every style the app can offer: built-in templates, your template folders, Frontier's channel styles"""
    out = {}
    samples = dict(documentary="What_Happens_If_the_Government_Cuts_Hasidic_Benefits.mp4",
                   paper="Noahs_Ark_Confirmed_After_4300_Years_1080p.mp4", forensic="Noahs_Ark_100_Percent_Confirmed.mp4",
                   expedition="Noahs_Ark_Myth_or_Reality.mp4", broadcast="Noahs_Ark_Breaking_Drill_Bit_Shattered.mp4",
                   almanac="Pennsylvania_Has_95000_Amish_So_Why_Does_Wisconsin_Have_MORE_Settlements.mp4")
    for k, v in STYLES.items():
        smp = os.path.join(media(w), "out", samples[k])
        out[k] = dict(v, theme=k, engine="docu", preview_path=os.path.join(DOCU, v["preview"]),
                      example_path=os.path.join(os.path.dirname(DOCU), v["example"], "build.py"),
                      sample_path=smp if os.path.exists(smp) else None)
    out.update(custom_styles(w))
    try:
        import frontier
        for st in frontier.styles(frontier.find_dir(w)):
            out[st["id"]] = st
    except Exception:
        pass
    return out


def style_info(sid, w):
    st = all_styles(w).get(sid)
    if not st:
        raise KeyError(f"unknown style {sid}")
    return st


def workspace(w=None):
    return os.path.abspath(w or os.environ.get("STUDIO_WORKSPACE") or os.path.dirname(DOCU))


def media(w):
    return os.path.abspath(os.environ.get("VIDEO_ROOT") or os.path.join(w, "media"))


def niches_dir():
    """the niche registry: a niche workspace keeps its own (STUDIO_NICHES), so niches never mix"""
    d = os.environ.get("STUDIO_NICHES") or os.path.join(HERE, "niches")
    os.makedirs(d, exist_ok=True)
    return d


def niches():
    out = []
    for p in sorted(glob.glob(os.path.join(niches_dir(), "*.json"))):
        try:
            out.append(json.load(open(p, encoding="utf-8")))
        except Exception:
            pass
    return out


def niche(nid):
    for n in niches():
        if n["id"] == nid:
            return n
    raise KeyError(f"unknown niche {nid}")


def save_niche(n):
    n["id"] = re.sub(r"[^a-z0-9_]+", "_", n["id"].lower()).strip("_")
    json.dump(n, open(os.path.join(niches_dir(), n["id"] + ".json"), "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    return n


def slugify(title):
    s = re.sub(r"[^a-z0-9]+", "_", title.lower()).strip("_")
    return s[:60] or "video"


def name_of(title):
    return re.sub(r"_+", "_", re.sub(r"[^A-Za-z0-9]+", "_", title)).strip("_")[:80] or "Video"


def niche_status(n, w):
    """what is on disk for this niche"""
    M = media(w)
    sv = os.path.join(M, n["source_video"])
    clips = len(os.listdir(sv)) if os.path.isdir(sv) else 0
    idir = os.path.join(M, n["images"]) if n.get("images") else None
    imgs = len(os.listdir(idir)) if idir and os.path.isdir(idir) else 0
    cat = os.path.join(w, n["catalog_from"]) if n.get("catalog_from") else None
    has_cat = bool(cat and os.path.exists(os.path.join(cat, "catalog_all.json")))
    has_img_cat = bool(cat and os.path.exists(os.path.join(cat, "image_picks.json")))
    return dict(clips_on_disk=clips, images_on_disk=imgs, clip_catalog=has_cat, image_catalog=has_img_cat,
                downloaded=clips > 0 or imgs > 0)


HEADER = '''"""
{title}
Generated by Docu Studio · style: {style_name} · niche: {niche_name} · shot list: {mode}

    python build.py plan | prep | stills [ids] | render [ids] | mix | final | path
Edit the shot list below like any hand-made build.py; data/studio_job.json holds the paths.
"""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
JOB = json.load(open(os.path.join(HERE, "data", "studio_job.json"), encoding="utf-8"))
DOCU = os.environ.get("DOCU_DIR") or os.path.join(HERE, "..", "..", "docu")
sys.path[:0] = [DOCU, os.path.join(DOCU, "studio")]

import edl                       # noqa: E402
from edl import *                # noqa: E402,F401,F403
from shots import *              # noqa: E402,F401,F403
import shots                     # noqa: E402

M = os.environ.get("VIDEO_ROOT") or os.path.join(HERE, "..", "..", "media")
P_ = JOB["paths"]
edl.setup(
    name=JOB["name"],
    kit=os.environ.get("VIDEO_KIT", os.path.join(M, "kit")),
    footage=os.path.join(M, P_["footage"]),
    work=os.path.join(M, "work", JOB["slug"]),
    data=os.path.join(HERE, "data"),
    out=os.path.join(M, "out"),
    image_dirs=[os.path.join(M, d) for d in P_["image_dirs"]],
    theme=JOB.get("theme") or JOB["style"],
    music_floor_db=-21.0, music_duck_db=-10.0, sfx_gain=0.55,
    sfx_style=JOB["sfx_style"], xfade=JOB["xfade"], vary="auto",
)
shots.init()
ACC = shots.ACC                  # this video's accent colour
V = edl.V

# ============================================================== shot list
'''

FOOTER = '''
# ============================================================== music: one bed per act
edl.main(music=music_for(ACTS))
'''


def create(job, w):
    """make projects/<slug>/ with data/ filled from the niche; returns (project_dir, work_dir, job)"""
    n = niche(job["niche"]) if job.get("niche") else None
    st = style_info(job["style"], w)
    slug = job.get("slug") or slugify(job["title"])
    proj = os.path.join(w, "projects", slug)
    data = os.path.join(proj, "data")
    os.makedirs(data, exist_ok=True)
    M = media(w)
    work = os.path.join(M, "work", slug)
    os.makedirs(work, exist_ok=True)
    os.makedirs(os.path.join(M, "out"), exist_ok=True)
    src = os.path.join(w, n["catalog_from"]) if n and n.get("catalog_from") else None
    for f in ("catalog_all.json", "image_picks.json", "notes_clips.txt", "notes_img.txt"):
        if src and os.path.exists(os.path.join(src, f)):
            shutil.copy(os.path.join(src, f), os.path.join(data, f))
    if not os.path.exists(os.path.join(data, "catalog_all.json")):
        json.dump([], open(os.path.join(data, "catalog_all.json"), "w"))
    job = dict(job, slug=slug, name=name_of(job["title"]), engine=st.get("engine", "docu"), theme=st.get("theme"),
               sfx_style=st.get("sfx", "full"), xfade=st.get("xfade", 0.0),
               paths=dict(footage=n["footage"], image_dirs=n["image_dirs"], picks=n.get("picks")) if n else {})
    json.dump(job, open(os.path.join(data, "studio_job.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    return proj, work, job


def write_build(proj, job, body, mode, w=None):
    n = niche(job["niche"])
    st = style_info(job["style"], workspace(w))
    head = HEADER.format(title=job["title"], style_name=st["name"], niche_name=n["name"], mode=mode)
    path = os.path.join(proj, "build.py")
    open(path, "w", encoding="utf-8").write(head + body.strip() + "\n" + FOOTER)
    return path


# ------------------------------------------------------------------ what the shot list can use
def used_before(w, exclude=None):
    used = set()
    for p in glob.glob(os.path.join(w, "projects", "*", "data", "assets_used.json")):
        if exclude and os.path.abspath(p).startswith(os.path.abspath(exclude) + os.sep):
            continue
        try:
            d = json.load(open(p))
            used |= set(d.get("images", [])) | set(d.get("clips", []))
        except Exception:
            pass
    return used


def assets(proj, w, job):
    """clips and pictures available to this video, unused ones first"""
    data = os.path.join(proj, "data")
    M = media(w)
    used = used_before(w, exclude=proj)
    cat = json.load(open(os.path.join(data, "catalog_all.json")))
    clips = []
    for c in cat:
        if c.get("flags") or c.get("quality", 0) < 3:
            continue
        clips.append(dict(i=c["i"], dur=round(c["e"] - c["s"], 1), q=c.get("quality", 3), tags=c.get("tags", []),
                          desc=c.get("desc", ""), used=c["video"] in used))
    images = []
    picks = os.path.join(data, "image_picks.json")
    if os.path.exists(picks):
        for r in json.load(open(picks)):
            images.append(dict(key=r["key"], tags=r.get("tags", []), desc=r.get("desc", ""), used=r["key"] in used,
                               wide=r.get("w", 1600) >= 1200))
    else:                                       # no picture catalog yet: file names only
        seen = set()
        for d in job["paths"]["image_dirs"]:
            for f in sorted(glob.glob(os.path.join(M, d, "*"))):
                k = os.path.splitext(os.path.basename(f))[0]
                if k not in seen and f.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
                    seen.add(k)
                    images.append(dict(key=k, tags=[], desc="(no description)", used=k in used, wide=True))
    clips.sort(key=lambda c: (c["used"], -c["q"]))
    images.sort(key=lambda r: r["used"])
    props = sorted(os.path.basename(p) for p in glob.glob(os.path.join(M, "kit", "cutouts", "*.png")))
    return clips, images, props
