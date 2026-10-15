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
    "record": dict(name="The Record", letter="R", example="projects/hasidic_mesirah",
                   blurb="Investigative documentary: dockets, transcript pages with marked lines, lexicon, tally, chain, "
                         "redacted lists, stock inside an evidence viewer. Blue-black ink, bone paper, one amber signal.",
                   sfx="full", xfade=0.4, preview="../templates/record/previews/sheet.jpg",
                   sheet="../templates/record/previews/sheet.jpg", readme="The Record"),
    "datadoc": dict(name="Data Documentary", letter="G", example="docu/templates/starter_documentary",
                    blurb="Data-led documentary: big quiet numbers on near-black navy (ddroll, ddbars, dddots, ddstrike, "
                          "ddread), stats, checklists, splits, the midnight map, chapter tabs on full-frame footage.",
                    sfx="calm", xfade=0.5, preview="../templates/record/previews/sheet.jpg",
                    sheet="../templates/record/previews/sheet.jpg", readme="Data Documentary"),
}


def custom_styles(w):
    """your own templates: <workspace>/styles/<name>/style.json (re-read every time, so new folders show up at once)

    style.json: {"name": "Cold Case Files", "template": "forensic" (or the older "theme"), "blurb": "...", "letter": "G",
                 "example": "build.py" (a finished shot list in this style, optional),
                 "rules": "rules.md" (how this style is edited, optional),
                 "preview": "preview.jpg", "sample": "sample.mp4", "sfx": "full|calm", "xfade": 0.0}
    A style names its template; the template's own look (templates/<id>/) is what renders - never a fallback.
    """
    out = {}
    try:
        import sys as _s
        _s.path.insert(0, DOCU)
        import registry
        T = registry.templates()
    except Exception:                                  # noqa: BLE001
        registry, T = None, {}
    roots = [os.path.join(w, "styles")]
    kit_styles = os.path.join(os.path.dirname(DOCU), "styles")
    if os.path.abspath(kit_styles) != os.path.abspath(roots[0]):
        roots.append(kit_styles)                       # a niche workspace also sees the kit's styles
    for root in roots:
        for p in sorted(glob.glob(os.path.join(root, "*", "style.json"))):
            d0 = os.path.dirname(p)
            sid = os.path.basename(d0)
            if sid.startswith("_") or ("custom:" + sid) in out:
                continue                               # _example and other parked templates
            try:
                d = json.load(open(p, encoding="utf-8"))
            except Exception:
                continue
            tid = d.get("template") or d.get("theme") or "documentary"
            t = T.get(tid) or {}
            base = STYLES.get(tid) or STYLES.get(t.get("theme", ""), STYLES["documentary"])
            f = lambda k: os.path.join(d0, d[k]) if d.get(k) and os.path.exists(os.path.join(d0, d[k])) else None
            sheet = os.path.join(os.path.dirname(DOCU), t["preview_sheet"]) if t.get("preview_sheet") else None
            ex = f("example")
            if not ex and t.get("examples"):
                ex = os.path.join(os.path.dirname(DOCU), t["examples"][0])
            out["custom:" + sid] = dict(
                id="custom:" + sid, style_id=sid, template=tid,
                name=d.get("name") or sid, letter=d.get("letter", "★"), blurb=d.get("blurb", ""),
                tagline=d.get("tagline", ""), points=d.get("points", []), best_for=d.get("best_for") or t.get("best_for", ""),
                theme=t.get("theme") or tid, sfx=d.get("sfx", t.get("sfx_style", base["sfx"])),
                xfade=float(d.get("xfade", t.get("xfade", base["xfade"]))), readme=d.get("name") or base["readme"],
                example_path=ex if ex and os.path.exists(ex) else os.path.join(os.path.dirname(DOCU), base["example"], "build.py"),
                rules_path=f("rules"),
                preview_path=f("preview") or (sheet if sheet and os.path.exists(sheet) else os.path.join(DOCU, base["preview"])),
                sample_path=f("sample"), engine="docu", folder=d0, installed=bool(t.get("installed", True)))
    return out


def all_styles(w):
    """every look the app can offer, one card each: the style folders (styles/<id>/ - each with its template, preview
    picture and sample video), then the built-in templates that have no folder of their own, then Frontier's channel
    styles that were not imported into the kit yet (those still run through Frontier's own app)"""
    out = {}
    custom = custom_styles(w)
    have = {v["template"] for v in custom.values()}
    samples = dict(documentary="What_Happens_If_the_Government_Cuts_Hasidic_Benefits.mp4",
                   paper="Noahs_Ark_Confirmed_After_4300_Years_1080p.mp4", forensic="Noahs_Ark_100_Percent_Confirmed.mp4",
                   expedition="Noahs_Ark_Myth_or_Reality.mp4", broadcast="Noahs_Ark_Breaking_Drill_Bit_Shattered.mp4",
                   almanac="Pennsylvania_Has_95000_Amish_So_Why_Does_Wisconsin_Have_MORE_Settlements.mp4")
    out.update(custom)
    for k, v in STYLES.items():
        if k in have:
            continue                                   # its style folder already shows it, with preview and sample
        smp = os.path.join(media(w), "out", samples.get(k, "-"))
        out[k] = dict(v, theme=k, engine="docu", preview_path=os.path.join(DOCU, v["preview"]),
                      example_path=os.path.join(os.path.dirname(DOCU), v["example"], "build.py"),
                      sample_path=smp if os.path.exists(smp) else None)
    try:
        import frontier
        imported = set()
        for v in custom.values():
            if v.get("template"):
                try:
                    fj = json.load(open(os.path.join(os.path.dirname(DOCU), "templates", v["template"], "frontier.json"),
                                        encoding="utf-8"))
                    imported.add(fj.get("style"))
                except Exception:                      # noqa: BLE001
                    pass
        for st in frontier.styles(frontier.find_dir(w)):
            if st["id"].split(":", 1)[-1] not in imported:
                out[st["id"]] = st
    except Exception:
        pass
    return out


def style_info(sid, w):
    every = all_styles(w)
    st = every.get(sid) or every.get("custom:" + str(sid))      # an older job may name a built-in that has a folder now
    if not st and sid in STYLES:
        v = STYLES[sid]
        st = dict(v, theme=sid, engine="docu", preview_path=os.path.join(DOCU, v["preview"]),
                  example_path=os.path.join(os.path.dirname(DOCU), v["example"], "build.py"), sample_path=None)
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
DOCU = os.environ.get("DOCU_DIR") or next((d for d in (os.path.join(HERE, "..", "..", "docu"), JOB.get("docu", ""))
                                           if d and os.path.isfile(os.path.join(d, "edl.py"))), "docu")
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
    style=JOB.get("style_id"), template=JOB.get("template_id"),
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
               style_id=st.get("style_id"), template_id=st.get("template"),
               sfx_style=st.get("sfx", "full"), xfade=st.get("xfade", 0.0),
               paths=dict(footage=n["footage"], image_dirs=n["image_dirs"], picks=n.get("picks")) if n else {},
               docu=os.path.dirname(os.path.dirname(os.path.abspath(__file__))))      # the kit's engine, for workspaces
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
