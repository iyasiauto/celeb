"""
studio.py - the Docu Studio backend. The desktop app runs it; it also works on its own.

    python studio.py info                         workspace, styles, niches, projects, keys present
    python studio.py doctor                       what is installed / missing
    python studio.py setup                        install Python packages, Chromium, FFmpeg
    python studio.py kit [--folder <dir>]         the asset kit (music, fonts, maps, cut-outs) from the Drive or a folder
                                                  on this PC (e.g. your Frontier folder's assets) + props
    python studio.py niche-fetch --niche hasidic  download a niche's footage (or link its local folders) and stage pictures
    python studio.py niche-add --name "..." --folder <dir> [--tags tags.json]   a new niche from a folder on this PC
    python studio.py niche-add --name "..." --drive <folder link>               ... or from a Drive folder
    python studio.py niche-link --niche hasidic --folder <dir>   use footage already on this PC for a niche
    python studio.py niche-catalog --niche <id> [--tags tags.json]   contact sheets + AI descriptions -> catalog
    python studio.py voice --voice-id <id>        look up a FameSpeak / ElevenLabs voice
    python studio.py make --job job.json [--from render]            make a video end to end

Every line on stdout is a JSON event (events.py). Keys come from the environment (the app passes them),
api_keys/keys.env, or your Frontier folder's .env (tools/keys.py). The AI is whichever provider you set up
(ai.py: Claude Code CLI, OpenRouter, OpenLux, Antigravity, any OpenAI-compatible endpoint, Claude API) - or none.
"""

import argparse
import glob
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
DOCU = os.path.dirname(HERE)
sys.path[:0] = [HERE, DOCU, os.path.join(DOCU, "tools")]

import events as E                # noqa: E402
import project as P               # noqa: E402
from keys import get as key       # noqa: E402

PY = sys.executable
STAGES = ["project", "voice", "timing", "shotlist", "plan", "prep", "stills", "qa", "render", "mix", "final", "deliver", "metadata"]


def _ensure_ffmpeg():
    if shutil.which("ffmpeg") and shutil.which("ffprobe"):
        return True
    try:
        import static_ffmpeg
        static_ffmpeg.add_paths()
        return bool(shutil.which("ffmpeg"))
    except Exception:
        return False


def run(cmd, cwd=None, on_line=None, env=None):
    """run a child process, forward its output as log lines (or to on_line); raise on failure"""
    e = dict(os.environ, PYTHONUNBUFFERED="1", PYTHONIOENCODING="utf-8")
    e.update(env or {})
    p = subprocess.Popen(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=e, text=True,
                         encoding="utf-8", errors="replace", bufsize=1)
    tail = []
    for line in p.stdout:
        line = line.rstrip()
        if not line:
            continue
        tail = (tail + [line])[-60:]
        if on_line:
            on_line(line)
        else:
            E.log(line)
    p.wait()
    if p.returncode != 0:
        raise RuntimeError(f"{os.path.basename(cmd[1]) if len(cmd) > 1 else cmd[0]} failed:\n" + "\n".join(tail[-25:]))
    return tail


# ------------------------------------------------------------------ info / doctor / setup
def cmd_info(a):
    w = P.workspace(a.workspace)
    M = P.media(w)
    import frontier
    fdir = frontier.find_dir(w)
    styles = [dict(v, id=k) for k, v in P.all_styles(w).items()]
    niches = [dict(n, status=P.niche_status(n, w)) for n in P.niches()]
    projects = []
    for d in sorted(glob.glob(os.path.join(w, "projects", "*", "build.py")), key=os.path.getmtime, reverse=True):
        proj = os.path.dirname(d)
        slug = os.path.basename(proj)
        info = dict(slug=slug, path=proj, modified=os.path.getmtime(d))
        jf = os.path.join(proj, "data", "studio_job.json")
        if os.path.exists(jf):
            j = json.load(open(jf, encoding="utf-8"))
            info.update(title=j.get("title"), style=j.get("style"), niche=j.get("niche"), name=j.get("name"))
        au = os.path.join(proj, "data", "assets_used.json")
        if os.path.exists(au):
            v = json.load(open(au)).get("vary", {})
            info["look"] = {k: v.get(k) for k in ("accent", "kicker", "fonts")}
            info.setdefault("name", json.load(open(au)).get("name"))
        name = info.get("name")
        if name:
            mp4 = os.path.join(M, "out", name + ".mp4")
            if os.path.exists(mp4):
                info["video"] = mp4
                info["size"] = os.path.getsize(mp4)
            lk = os.path.join(M, "out", name + ".link.txt")
            if os.path.exists(lk):
                info["link"] = open(lk).read().split("\n")[0].strip()
        meta = os.path.join(proj, "youtube_metadata.txt")
        if os.path.exists(meta):
            info["metadata"] = meta
            m = re.search(r"^TITLE\s*\n(.+)$", open(meta, encoding="utf-8", errors="ignore").read(), re.M)
            if m and not info.get("title"):
                info["title"] = m.group(1).strip()
        info.setdefault("title", slug.replace("_", " ").title())
        projects.append(info)
    import ai
    import keys as K
    E.result(dict(workspace=w, media=M, styles=styles, niches=niches, projects=projects,
                  frontier=dict(dir=fdir, engine=bool(fdir and os.path.exists(os.path.join(fdir, "make_video.py"))),
                                env=bool(fdir and os.path.exists(os.path.join(fdir, ".env"))),
                                assets=_frontier_assets(fdir)),
                  styles_folder=os.path.join(w, "styles"),
                  keys={k: bool(key(k)) for k in K.KNOWN},
                  key_source={k: K.source(k) for k in K.KNOWN},      # where each key was found - never its value
                  voice_id=key("FAMESPEAK_VOICE_ID") or "",
                  ai=dict(ai.status(), editor_label=ai.LABEL.get(ai.resolve("editor") or "none"),
                          vision_label=ai.LABEL.get(ai.resolve("vision") or "none"))))


def _frontier_assets(fdir):
    """Frontier's assets folder (fonts, music, maps, cut-outs ...) when it is on this PC"""
    d = os.path.join(fdir, "assets") if fdir else None
    return d if d and os.path.isdir(d) else None


def cmd_doctor(a):
    w = P.workspace(a.workspace)
    M = P.media(w)
    checks = []

    def add(name, ok, detail="", fix="", optional=False):
        checks.append(dict(name=name, ok=bool(ok), detail=detail, fix=fix, optional=optional))
    add("Python 3.10+", sys.version_info >= (3, 10), sys.version.split()[0], "install Python 3.10 or newer")
    for mod, pip in (("numpy", "numpy"), ("scipy", "scipy"), ("PIL", "Pillow"), ("playwright", "playwright"),
                     ("rembg", "rembg[cpu]"), ("faster_whisper", "faster-whisper"), ("gdown", "gdown")):
        add(f"Python package {pip}", importlib.util.find_spec(mod) is not None, "", "Settings → Install / repair")
    ff = _ensure_ffmpeg()
    add("FFmpeg + FFprobe", ff, shutil.which("ffmpeg") or "not found", "Settings → Install / repair")
    try:
        import render
        ch = render.CHROME
        ok = bool(ch and os.path.exists(ch))
        if not ok and importlib.util.find_spec("playwright"):
            ok, ch = True, "Playwright default Chromium"
    except Exception as e:                              # noqa: BLE001
        ok, ch = False, str(e)[:80]
    add("Chromium (renderer)", ok, ch or "", "Settings → Install / repair")
    for sub in ("fonts", "maps", "music", "cutouts"):
        d = os.path.join(M, "kit", sub)
        n = len(os.listdir(d)) if os.path.isdir(d) else 0
        add(f"Asset kit: {sub}", n > 0, f"{n} files", "Niches → Asset kit (from Frontier's assets or the Drive)")
    import ai
    import keys as K
    src = K.source("FAMESPEAK_API_KEY")
    add("FameSpeak API key", src, f"from {src}" if src else "", "Settings → API keys (only for generated voiceovers)", True)
    for role, what in (("editor", "AI editor (shot list, fixes, metadata)"), ("vision", "AI vision (visual QA, cataloging)")):
        p = ai.resolve(role)
        add(what, p, f"{ai.LABEL.get(p)} · {ai.model_for(role, p)}" if p else "off - the offline rules are used",
            "Settings → AI: Claude Code, OpenRouter, OpenLux, Antigravity or any OpenAI-compatible endpoint", True)
    fdir = __import__("frontier").find_dir(w)
    add("Frontier folder", fdir, fdir or "not set", "Settings → Frontier folder (Frontier's styles and assets)", True)
    E.result(dict(checks=checks, workspace=w, media=M))


def cmd_setup(a):
    E.stage("setup")
    req = os.path.join(DOCU, "requirements.txt")
    run([PY, "-m", "pip", "install", "--upgrade", "-r", req, "anthropic", "static-ffmpeg"])
    E.progress(0.6, "Python packages installed")
    run([PY, "-m", "playwright", "install", "chromium"])
    E.progress(0.85, "Chromium installed")
    if not (shutil.which("ffmpeg") and shutil.which("ffprobe")):
        run([PY, "-c", "import static_ffmpeg; static_ffmpeg.add_paths(); import shutil; print('ffmpeg:', shutil.which('ffmpeg'))"])
    E.stage("setup", "done")
    E.emit("done", ok=True)


def cmd_kit(a):
    w = P.workspace(a.workspace)
    M = P.media(w)
    E.stage("kit")
    kit = os.path.join(M, "kit")
    folder = a.folder
    if folder == "frontier":
        import frontier
        folder = _frontier_assets(frontier.find_dir(w))
        if not folder:
            raise RuntimeError("No Frontier assets folder: set Settings → Frontier folder first.")
    if folder:
        if not os.path.isdir(folder):
            raise RuntimeError(f"Not a folder: {folder}")
        n = _link_tree(folder, kit, progress=lambda v, m: E.progress(v, m, "kit"))
        E.log(f"{n} kit files taken from {folder} (linked where possible, so nothing is duplicated)")
    else:
        drive = a.drive or "1CYxavMgiqBwVtUwFMizA-Txnf4123yYq"
        run([PY, os.path.join(DOCU, "tools", "fetch_drive.py"), drive, kit, "12"], on_line=_fetch_progress)
    run([PY, os.path.join(DOCU, "tools", "props.py"), os.path.join(kit, "cutouts")])
    E.stage("kit", "done")
    E.emit("done", ok=True)


def _is_link(p):
    return os.path.islink(p) or getattr(os.path, "isjunction", lambda x: False)(p)


def _link_dir(src, dst):
    """dst -> src as a folder link: symlink, else a Windows junction (no admin needed), else a copy"""
    src = os.path.abspath(src)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    if _is_link(dst):
        try:
            os.unlink(dst)
        except OSError:
            os.rmdir(dst)                                # a junction is removed with rmdir (its target stays)
    elif os.path.isdir(dst) and not os.listdir(dst):
        os.rmdir(dst)
    if os.path.exists(dst):
        raise RuntimeError(f"{dst} already exists as a real folder; move it away to link {src} there")
    try:
        os.symlink(src, dst, target_is_directory=True)
        return "link"
    except OSError:
        pass
    if os.name == "nt":
        r = subprocess.run(["cmd", "/c", "mklink", "/J", dst, src], capture_output=True, text=True)
        if r.returncode == 0:
            return "junction"
    shutil.copytree(src, dst)
    return "copy"


def _link_file(src, dst):
    for f in (os.symlink, os.link):
        try:
            return f(os.path.abspath(src), dst)
        except OSError:
            pass
    shutil.copy2(src, dst)


def _link_tree(src, dst, progress=None):
    """every file under src that dst lacks, linked (or copied) into the same place under dst"""
    todo = []
    for d, dirs, files in os.walk(src):
        dirs[:] = [x for x in dirs if not x.startswith((".", "__pycache__", "_thumbs"))]
        for f in files:
            s = os.path.join(d, f)
            t = os.path.join(dst, os.path.relpath(s, src))
            if not os.path.exists(t) and not f.startswith("."):
                todo.append((s, t))
    for i, (s, t) in enumerate(todo, 1):
        os.makedirs(os.path.dirname(t), exist_ok=True)
        _link_file(s, t)
        if progress and (i % 25 == 0 or i == len(todo)):
            progress(i / len(todo), f"{i}/{len(todo)} files")
    return len(todo)


def _fetch_progress(line):
    m = re.search(r"(\d+) / (\d+)", line)
    if m:
        E.progress(int(m.group(1)) / max(1, int(m.group(2))), line)
    else:
        E.log(line)


# ------------------------------------------------------------------ niches
VIDEO_EXT = (".mp4", ".mov", ".mkv", ".webm", ".m4v", ".avi")
IMAGE_EXT = (".jpg", ".jpeg", ".png", ".webp")


def _stage_footage(n, M):
    """footage/source_video -> the niche's clips folder (the engine reads clips from there)"""
    src = os.path.join(M, n["source_video"])
    sv = os.path.join(M, n["footage"], "source_video")
    if not os.path.isdir(src) or os.path.normpath(sv) == os.path.normpath(src):
        return
    if os.path.exists(sv) and not _is_link(sv):
        return                                           # an earlier copy: leave it
    how = _link_dir(src, sv)
    E.log(f"clips: {sv} -> {src} ({how})")


def _stage_picks(n, w, M):
    picks_json = os.path.join(w, n.get("catalog_from") or "", "image_picks.json")
    if n.get("picks") and n.get("images") and os.path.exists(picks_json):
        run([PY, os.path.join(DOCU, "tools", "catalog_images.py"), "stage", picks_json, os.path.join(M, n["images"]),
             os.path.join(M, n["picks"])])


def cmd_niche_fetch(a):
    w = P.workspace(a.workspace)
    M = P.media(w)
    n = P.niche(a.niche)
    if n.get("drive") and not n.get("local"):
        E.stage("download")
        run([PY, os.path.join(DOCU, "tools", "fetch_drive.py"), n["drive"], os.path.join(M, n["download_to"]), "12"],
            on_line=_fetch_progress)
        E.stage("download", "done")
    else:
        E.stage("download", "skipped", "footage is in a folder on this PC")
    E.stage("stage")
    _stage_footage(n, M)
    if n["id"] == "noah":                               # the two viral posts' images, as the Noah projects expect
        dst = os.path.join(M, "work", "ind")
        os.makedirs(dst, exist_ok=True)
        dirs = sorted(glob.glob(os.path.join(M, "footage", "Individual Images", "Researchers*"))) + \
            sorted(glob.glob(os.path.join(M, "footage", "Individual Images", "*HOW*")))
        for i, d in enumerate(dirs[:2], 1):
            for f in sorted(glob.glob(os.path.join(d, "0[1-5].jpg"))):
                t = os.path.join(dst, f"ind{i}_{os.path.basename(f)}")
                if not os.path.exists(t):
                    shutil.copy(f, t)
    _stage_picks(n, w, M)
    E.stage("stage", "done")
    E.emit("done", ok=True)


def _count(d, ext):
    try:
        return sum(f.lower().endswith(ext) for f in os.listdir(d))
    except OSError:
        return 0


def _guess_dirs(root):
    """the folder with the most videos and the one with the most pictures (clips/ and images/ win when present)"""
    best_v, best_i = (0, ""), (0, "")
    for d, dirs, files in os.walk(root):
        dirs[:] = [x for x in dirs if not x.startswith((".", "_", "cat", "picks", "footage"))]
        v = sum(f.lower().endswith(VIDEO_EXT) for f in files)
        i = sum(f.lower().endswith(IMAGE_EXT) for f in files)
        best_v = max(best_v, (v, d))
        best_i = max(best_i, (i, d))
    return (best_v[1] if best_v[0] else None), (best_i[1] if best_i[0] else None)


def _local_dirs(folder, clips=None, images=None):
    folder = os.path.abspath(folder)
    if not os.path.isdir(folder):
        raise RuntimeError(f"Not a folder: {folder}")
    gv, gi = _guess_dirs(folder)
    vdir = os.path.abspath(clips) if clips else gv
    idir = os.path.abspath(images) if images else gi
    if not vdir and not idir:
        raise RuntimeError(f"No videos or pictures found in {folder}")
    return folder, vdir, idir


def cmd_niche_add(a):
    nid = P.slugify(a.id or a.name)
    w = P.workspace(a.workspace)
    M = P.media(w)
    n = dict(id=nid, name=a.name, description=a.description or "", footage=f"{nid}/footage", picks=f"{nid}/picks",
             catalog_from=f"catalogs/{nid}", clip_share=int(a.clip_share), default_style=a.style, map_hint=a.map_hint or "")
    if a.folder:
        folder, vdir, idir = _local_dirs(a.folder, a.clips, a.images)
        n.update(local=True, folder=folder, download_to=folder, source_video=vdir or f"{nid}/footage/source_video",
                 images=idir, image_dirs=[f"{nid}/picks"] + ([idir] if idir else []))
        if a.tags:
            n["tags_json"] = os.path.abspath(a.tags)
        n["description"] = n["description"] or f"{_count(vdir, VIDEO_EXT) if vdir else 0} clips, " \
                                               f"{_count(idir, IMAGE_EXT) if idir else 0} pictures in {folder}"
        _stage_footage(n, M)
    elif a.drive:
        n.update(drive=a.drive, download_to=f"{nid}/src", source_video=f"{nid}/src/clips", images=f"{nid}/src/images",
                 image_dirs=[f"{nid}/picks", f"{nid}/src/images"])
    else:
        raise RuntimeError("Give the niche a folder on this PC (--folder) or a Drive link (--drive)")
    E.result(P.save_niche(n))


def cmd_niche_link(a):
    """point an existing niche at footage already on this PC (no download), then stage its picture picks"""
    w = P.workspace(a.workspace)
    M = P.media(w)
    n = P.niche(a.niche)
    folder, vdir, idir = _local_dirs(a.folder, a.clips, a.images)
    E.stage("stage")
    n.update(local=True, folder=folder)
    if vdir:
        n["source_video"] = vdir
        sv = os.path.join(M, n["footage"], "source_video")
        if os.path.exists(sv) and not _is_link(sv):        # a downloaded copy lives there: use a fresh footage folder
            n["footage"] = n["id"] + "/footage_local"
        _stage_footage(n, M)
    if idir:
        n["images"] = idir
        n["image_dirs"] = [n.get("picks") or n["id"] + "/picks", idir]
    if a.tags:
        n["tags_json"] = os.path.abspath(a.tags)
    P.save_niche(n)
    _stage_picks(n, w, M)
    E.log(f"{n['name']}: clips {vdir or '-'} · pictures {idir or '-'}")
    E.stage("stage", "done")
    E.result(n)


def _words(name):
    """tags from a file name: 'kiryas_joel_street-03.mp4' -> ['kiryas', 'joel', 'street']"""
    stem = os.path.splitext(os.path.basename(name))[0].lower()
    out = [t for t in re.split(r"[^a-z]+", stem) if len(t) > 2 and re.search(r"[aeiouy]", t)
           and t not in _STOP and not re.fullmatch(r"[a-f]{6,}", t)]
    return list(dict.fromkeys(out))[:6]


_STOP = set("the and from with for left right img dsc vid clip mov jpg jpeg png mp4 copy final edit version photo image "
            "picture video stock footage".split())


def _tags_map(path):
    """your own tags file -> {file stem: (tags, description)}

    Accepts {"file.jpg": ["tag", ...]}, {"file.jpg": "description"}, {"file.jpg": {"tags": [...], "desc": "..."}}
    or a list of {"file"|"path"|"name": ..., "tags": [...], "desc"|"description"|"caption": ...}."""
    if not path or not os.path.exists(path):
        return {}
    d = json.load(open(path, encoding="utf-8-sig"))
    items = d.items() if isinstance(d, dict) else [((r.get("file") or r.get("path") or r.get("name") or ""), r)
                                                   for r in d if isinstance(r, dict)]
    out = {}
    for f, v in items:
        if isinstance(v, list):
            tags, desc = [str(t) for t in v], ""
        elif isinstance(v, str):
            tags, desc = [], v
        elif isinstance(v, dict):
            tags = v.get("tags") or v.get("keywords") or []
            tags = [t.strip() for t in tags.split(",")] if isinstance(tags, str) else [str(t) for t in tags]
            desc = v.get("desc") or v.get("description") or v.get("caption") or ""
        else:
            continue
        stem = os.path.splitext(os.path.basename(str(f).replace("\\", "/")))[0].lower()
        if stem:
            out[stem] = ([re.sub(r"[|,\n]", " ", t).strip().lower() for t in tags if t.strip()][:4],
                         re.sub(r"[|\n]", " ", desc).strip()[:120])
    return out


def _merge_tags(line, idx_tags, idx_desc, extra):
    """add your own tags/description to an AI catalog line"""
    if not extra:
        return line
    p = line.split("|")
    tags, desc = extra
    p[idx_tags] = ",".join(dict.fromkeys([t for t in p[idx_tags].split(",") if t] + tags))[:80]
    if desc and len(p) > idx_desc and len(p[idx_desc]) < 8:
        p[idx_desc] = desc
    return "|".join(p)


def cmd_niche_catalog(a):
    w = P.workspace(a.workspace)
    M = P.media(w)
    n = P.niche(a.niche)
    import ai
    vision = ai.resolve("vision")
    if n.get("local"):
        vdir = os.path.join(M, n["source_video"]) if os.path.isdir(os.path.join(M, n.get("source_video", ""))) else None
        idir = os.path.join(M, n["images"]) if n.get("images") and os.path.isdir(os.path.join(M, n["images"])) else None
    else:
        vdir, idir = _guess_dirs(os.path.join(M, n["download_to"]))
        if vdir:
            n["source_video"] = os.path.relpath(vdir, M).replace(os.sep, "/")
        if idir:
            n["images"] = os.path.relpath(idir, M).replace(os.sep, "/")
            n["image_dirs"] = [n["picks"], n["images"]]
    if a.tags:
        n["tags_json"] = os.path.abspath(a.tags)
    P.save_niche(n)
    tags = _tags_map(n.get("tags_json"))
    if tags:
        E.log(f"your tags file: {len(tags)} files described")
    E.log(f"AI vision: {ai.LABEL[vision]} · {ai.model_for('vision', vision)}" if vision else
          "no AI vision provider: clips and pictures are described from your tags file and their file names")
    cat = os.path.join(M, n["id"], "cat")
    out = os.path.join(w, n["catalog_from"])
    os.makedirs(out, exist_ok=True)
    import describe
    tools = os.path.join(DOCU, "tools")
    if vdir:
        E.stage("clips")
        run([PY, os.path.join(tools, "catalog_clips.py"), "scan", vdir, cat] + (["--split"] if a.split else []))
        shots = json.load(open(os.path.join(cat, "shots.json")))
        notes = os.path.join(cat, "notes_clips.txt")
        if vision:
            describe.describe_clips(cat, n["name"], provider=vision, log=E.log, progress=lambda v, m: E.progress(v, m, "clips"))
            vid = {s["i"]: os.path.splitext(s["video"])[0].lower() for s in shots}
            lines = [l.rstrip("\n") for l in open(notes, encoding="utf-8") if l.strip() and not l.startswith("#")]
            lines = [_merge_tags(l, 3, 4, tags.get(vid.get(int(l.split("|")[0])))) for l in lines]
            seen = {int(l.split("|")[0]) for l in lines}
            if not lines:
                E.log("the AI described no clips: falling back to your tags file and the file names")
            for s in shots:                                  # tagged by you but not described: keep them
                key_ = os.path.splitext(s["video"])[0].lower()
                if s["i"] not in seen and (key_ in tags or not lines):
                    t, d = tags.get(key_, ([], ""))
                    t = t or _words(s["video"])
                    lines.append(f"{s['i']}|3||{','.join(t)}|{d or ' '.join(t) or s['video']}")
            lines.sort(key=lambda l: int(l.split("|")[0]))
        else:
            lines = []
            for s in shots:
                t, d = tags.get(os.path.splitext(s["video"])[0].lower(), ([], ""))
                t = t or _words(s["video"])
                lines.append(f"{s['i']}|3||{','.join(t)}|{d or ' '.join(t) or s['video']}")
        open(notes, "w", encoding="utf-8").write("# idx|quality 1-5|flags|tags|description\n" + "\n".join(lines) + "\n")
        run([PY, os.path.join(tools, "catalog_clips.py"), "build", cat, os.path.join(out, "catalog_all.json")])
        shutil.copy(notes, os.path.join(out, "notes_clips.txt"))
        E.stage("clips", "done", f"{len(lines)} shots")
        _stage_footage(dict(n, source_video=os.path.relpath(vdir, M) if not n.get("local") else n["source_video"]), M)
    if idir:
        E.stage("pictures")
        run([PY, os.path.join(tools, "catalog_images.py"), "scan", idir, cat, "--topic-regex", a.topic_regex])
        notes = os.path.join(cat, "notes_img.txt")
        clean = json.load(open(os.path.join(cat, "images_clean.json")))
        if vision:
            describe.describe_images(cat, n["name"], provider=vision, log=E.log, progress=lambda v, m: E.progress(v, m, "pictures"))
            ref = {f"{r['sheet']}:{r['pos']}": os.path.splitext(r["file"])[0].lower() for r in clean}
            lines = [l.rstrip("\n") for l in open(notes, encoding="utf-8") if l.strip() and not l.startswith("#")]
            lines = [_merge_tags(l, 1, 2, tags.get(ref.get(l.split("|")[0]))) for l in lines]
            seen = {l.split("|")[0] for l in lines}
            if not lines:
                E.log("the AI described no pictures: falling back to your tags file and the file names")
            for r in clean:
                k_ = f"{r['sheet']}:{r['pos']}"
                if k_ not in seen and (ref[k_] in tags or not lines):
                    t, d = tags.get(ref[k_], ([], ""))
                    t = t or _words(r["file"]) or [r["topic"]]
                    lines.append(f"{k_}|{','.join(t)}|{d or ' '.join(t)}")
        else:
            lines = []
            for r in clean:
                t, d = tags.get(os.path.splitext(r["file"])[0].lower(), ([], ""))
                t = t or _words(r["file"]) or [r["topic"]]
                lines.append(f"{r['sheet']}:{r['pos']}|{','.join(t)}|{d or ' '.join(t)}")
        open(notes, "w", encoding="utf-8").write("# sheet:pos|tags|description\n" + "\n".join(lines) + "\n")
        run([PY, os.path.join(tools, "catalog_images.py"), "pick", cat, idir, os.path.join(M, n["picks"]),
             os.path.join(out, "image_picks.json")])
        shutil.copy(notes, os.path.join(out, "notes_img.txt"))
        E.stage("pictures", "done", f"{len(lines)} pictures")
    E.emit("done", ok=True)


# ------------------------------------------------------------------ voice
def cmd_voice(a):
    import famespeak
    c = famespeak.Client(key("FAMESPEAK_API_KEY"))
    v = c.voice(a.voice_id) if a.voice_id else None
    out = dict(voice=v)
    try:
        out["usage"] = c.usage()
    except Exception as e:                              # noqa: BLE001
        out["usage_error"] = str(e)
    E.result(out)


# ------------------------------------------------------------------ make
def _para_times(script_path, words_path):
    from timing import Timing
    T = Timing.load(script_path, words_path)
    times = []
    for p in [p for p in open(script_path, encoding="utf-8-sig").read().split("\n") if p.strip()]:
        try:
            times.append(T.at(" ".join(p.split()[:6])))
        except KeyError:
            times.append(times[-1] if times else 0.0)
    return T, times


def _plan(proj, env):
    lines = []
    try:
        run([PY, "build.py", "plan"], cwd=proj, on_line=lambda l: (lines.append(l), E.log(l)), env=env)
        ok, err = True, ""
    except RuntimeError as e:
        ok, err = False, str(e)
    info = dict(ok=ok, error=err, warns=[l.strip() for l in lines if "WARN" in l])
    for l in lines:
        m = re.search(r"(\d+) scenes, ([\d.]+)s, clips ([\d.]+)s \((\d+)%\), alignment (\d+)%", l)
        if m:
            info.update(scenes=int(m.group(1)), total=float(m.group(2)), clip_pct=int(m.group(4)), align=int(m.group(5)))
        m = re.search(r"reused from earlier videos: (\d+) of (\d+)", l)
        if m:
            info.update(reused=int(m.group(1)), assets=int(m.group(2)))
    return info


def _problems(info, target):
    out = []
    if not info["ok"]:
        out.append("The plan failed:\n" + info["error"][-2500:])
        return out
    if abs(info.get("clip_pct", target) - target) > 6:
        out.append(f"Clip share is {info.get('clip_pct')} %, the target is {target} %. Move clips to or from beats to get within 4 points.")
    if info["warns"]:
        out.append("Clips too short for their words (join more shots with then=(...) or use a photo):\n" + "\n".join(info["warns"][:30]))
    if info.get("reused", 0) > 3:
        out.append(f"{info['reused']} assets were already used by earlier videos; replace them with unused ones.")
    return out


def _render_progress(line):
    m = re.search(r"(\d+)/(\d+) scenes", line)
    if m:
        E.progress(int(m.group(1)) / max(1, int(m.group(2))), f"{m.group(1)}/{m.group(2)} scenes", "render")
    elif "dissolves: batch" in line:
        m = re.search(r"batch (\d+)/(\d+)", line)
        if m:
            E.progress(int(m.group(1)) / max(1, int(m.group(2))), line.strip(), "final")
    E.log(line)


def _sheets(stills_dir, scenes, out_dir):
    """contact sheets of the stills, labelled with scene id and cue (for the app and for AI QA)"""
    from PIL import Image, ImageDraw, ImageFont
    os.makedirs(out_dir, exist_ok=True)
    for f in glob.glob(os.path.join(out_dir, "qa_*.jpg")):
        os.remove(f)
    cue = {s["id"]: s.get("cue", "") for s in scenes}
    fs = sorted(glob.glob(os.path.join(stills_dir, "*.jpg")))
    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", 15)
    except OSError:
        font = ImageFont.load_default()
    W, H, out = 560, 315, []
    for k in range(0, len(fs), 12):
        sh = Image.new("RGB", (W * 3, (H + 24) * 4), (12, 12, 14))
        d = ImageDraw.Draw(sh)
        for j, f in enumerate(fs[k:k + 12]):
            sid = os.path.basename(f)[:4]
            x, y = (j % 3) * W, (j // 3) * (H + 24)
            sh.paste(Image.open(f).convert("RGB").resize((W, H)), (x, y))
            d.text((x + 6, y + H + 3), f"{sid}  {cue.get(sid, '')[:58]}", fill=(255, 220, 90), font=font)
        p = os.path.join(out_dir, f"qa_{k // 12:02d}.jpg")
        sh.save(p, quality=82)
        out.append(p)
    return out


def _metadata(proj, job, scenes, editor):
    heads = [s for s in scenes if s["type"] in ("doctitle", "chapter")]
    chapters = ["0:00 " + (job["title"][:60])]
    for s in heads:
        t = int(s["t0"])
        if t > 0:
            chapters.append(f"{t // 60}:{t % 60:02d} " + (s.get("kicker", "") + ": " if s.get("kicker") and s["type"] == "doctitle" and s.get("kicker") != "A documentary" else "") + s.get("title", "").title())
    text = None
    if editor:
        try:
            import ai
            script = open(os.path.join(proj, "data", "script.txt"), encoding="utf-8").read()
            chat = ai.Chat("editor", provider=editor, log=E.log, effort="medium")
            text = chat.send(
                "Write YouTube upload metadata for this faceless documentary as plain text with these sections in this order: "
                "TITLE, ALTERNATIVE TITLES (A/B) (4 lines), DESCRIPTION (2 short paragraphs, factual, no hype, no emojis), "
                "CHAPTERS (use exactly these lines), TAGS (comma separated, under 450 characters), HASHTAGS (3), "
                "UPLOAD CHECKLIST (category, thumbnail, chapters, music licences, sources). No markdown.\n\n"
                f"Title: {job['title']}\n\nChapters:\n" + "\n".join(chapters) + "\n\nScript:\n" + script, max_tokens=4000).strip()
        except Exception as e:                          # noqa: BLE001
            E.log(f"metadata via the AI failed ({e}); writing the simple version")
    if not text:
        text = (f"TITLE\n{job['title']}\n\nDESCRIPTION\n(write two short paragraphs)\n\nCHAPTERS\n" + "\n".join(chapters) +
                "\n\nTAGS\n\nHASHTAGS\n\nUPLOAD CHECKLIST\n- Category: Education\n- Set the thumbnail\n"
                "- Chapters above in the description (0:00 first)\n- Check the music licences\n")
    p = os.path.join(proj, "youtube_metadata.txt")
    open(p, "w", encoding="utf-8").write(text + "\n")
    return p


def cmd_make(a):
    w = P.workspace(a.workspace)
    M = P.media(w)
    job = json.load(open(a.job, encoding="utf-8"))
    start = STAGES.index(a.start) if a.start else 0
    import ai
    want_ai = job.get("shotlist", "ai") in ("ai", "claude")
    editor = ai.resolve("editor") if want_ai else None
    env = {"VIDEO_ROOT": M, "DOCU_DIR": DOCU, "WORKERS": str(job.get("workers", 4))}
    _ensure_ffmpeg()

    def want(s):
        return STAGES.index(s) >= start

    # project
    E.stage("project")
    proj, work, job = P.create(job, w)
    data = os.path.join(proj, "data")
    E.artifact("project", proj, job["title"])
    E.stage("project", "done", proj)

    # voice
    if want("voice"):
        E.stage("voice")
        shutil.copy(job["script"], os.path.join(data, "script.txt"))
        v = job.get("voice", {})
        if v.get("mode") == "frontier":
            if job.get("engine") != "frontier":
                raise RuntimeError("'Frontier's own voice' only works with a Frontier style; choose FameSpeak or a file.")
            E.log("the voiceover is made by Frontier with the voice in its .env")
        elif v.get("mode") == "famespeak":
            import famespeak
            text = open(os.path.join(data, "script.txt"), encoding="utf-8-sig").read()
            if not key("FAMESPEAK_API_KEY"):
                raise RuntimeError("No FameSpeak key: Settings → API keys, or your Frontier folder's .env")
            mp3, srt = famespeak.make_voiceover(key("FAMESPEAK_API_KEY"), text, v.get("voice_id") or key("FAMESPEAK_VOICE_ID"), work,
                                                max_chars=int(v.get("max_chars", 4500)), language=v.get("language") or None,
                                                log=E.log, progress=lambda x, m: E.progress(x, m, "voice"))
            os.replace(mp3, os.path.join(work, "vo.mp3"))
            if srt:
                shutil.copy(srt, os.path.join(data, "voiceover.srt"))
                out_dir = os.path.join(M, "out")
                shutil.copy(srt, os.path.join(out_dir, job["name"] + ".srt"))
                E.artifact("srt", os.path.join(out_dir, job["name"] + ".srt"), "Subtitles (SRT)")
            shutil.copy(os.path.join(work, "vo.mp3"), os.path.join(M, "out", job["name"] + "_voiceover.mp3"))
            E.artifact("audio", os.path.join(M, "out", job["name"] + "_voiceover.mp3"), "Voiceover")
        else:
            shutil.copy(v["mp3"], os.path.join(work, "vo.mp3"))
            if v.get("srt"):
                shutil.copy(v["srt"], os.path.join(data, "voiceover.srt"))
        E.stage("voice", "done")

    if job.get("engine") == "frontier":
        return _make_frontier(job, w, M, proj, work, data)

    # timing
    if want("timing"):
        E.stage("timing")
        srt = os.path.join(data, "voiceover.srt")
        if os.path.exists(srt):
            run([PY, os.path.join(DOCU, "tools", "srt2words.py"), srt, os.path.join(data, "words.json")])
        else:
            E.log("no SRT: transcribing the voiceover with Whisper (a few minutes)")
            run([PY, os.path.join(DOCU, "tools", "transcribe.py"), os.path.join(work, "vo.mp3"), os.path.join(data, "words.json")])
        T, ptimes = _para_times(os.path.join(data, "script.txt"), os.path.join(data, "words.json"))
        E.log(f"alignment {T.matched:.0%}")
        if T.matched < 0.9:
            E.log("warning: the script and the voiceover differ in places - cues there may land late")
        E.stage("timing", "done", f"alignment {T.matched:.0%}")
    else:
        T, ptimes = _para_times(os.path.join(data, "script.txt"), os.path.join(data, "words.json"))

    target = int(job.get("clip_share", 30))
    n = P.niche(job["niche"])
    session = None

    # shot list + plan loop
    if want("shotlist"):
        E.stage("shotlist")
        clips, images, props = P.assets(proj, w, job)
        dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                    os.path.join(work, "vo.mp3")], capture_output=True, text=True).stdout or 0)
        if editor:
            import claude_shotlist as cs
            import variety
            hist = variety.history(os.path.join(w, "projects"), exclude=proj)
            v = variety.pick(variety.seed_for(job["name"]), hist, [])
            v = {kk: v[kk] for kk in ("accent", "kicker", "moves", "place")}
            v["heading_example"] = variety.KICKERS[v["kicker"]](3)
            session = cs.Session(P.style_info(job["style"], w), log=E.log, provider=editor,
                                 model=job.get("editor_model") or None, effort=job.get("effort", "high"))
            E.log(f"{session.label} is writing the shot list...")
            msg = cs.job_message(job, n, open(os.path.join(data, "script.txt"), encoding="utf-8").read(), ptimes, dur,
                                 clips, images, props, v)
            body = session.first(msg, on_text=lambda c: E.progress(min(0.95, c / 45000), f"{c // 1000}k characters written"))
            mode = session.label
        else:
            if want_ai:
                E.log("no AI editor set up (Settings → AI): using the offline shot list")
            import auto_shotlist
            body = auto_shotlist.build(os.path.join(data, "script.txt"), os.path.join(data, "words.json"), clips, images,
                                       job["title"], target, job["style"])
            mode = "offline rules"
        P.write_build(proj, job, body, mode, w)
        E.stage("shotlist", "done", mode)

    if want("plan"):
        E.stage("plan")
        for rnd in range(4):
            info = _plan(proj, env)
            probs = _problems(info, target)
            E.log(f"plan: {info.get('scenes', '?')} scenes, clips {info.get('clip_pct', '?')} %, reused {info.get('reused', '?')}, "
                  f"{len(info['warns'])} warnings" if info["ok"] else "plan failed")
            if not probs:
                break
            if session is None or rnd == 3:
                if not info["ok"]:
                    raise RuntimeError(info["error"])
                break
            E.log(f"sending the plan's problems back to {session.label}: " + "; ".join(p.split("\n")[0] for p in probs))
            body = session.fix("The engine's plan found these problems. Reply with the full corrected shot list.\n\n" + "\n\n".join(probs))
            P.write_build(proj, job, body, session.label, w)
        E.stage("plan", "done", f"{info.get('scenes', '?')} scenes · {info.get('clip_pct', '?')} % clips")

    if want("prep"):
        E.stage("prep")
        run([PY, "build.py", "prep"], cwd=proj, env=env)
        E.stage("prep", "done")

    def stills():
        st_dir = os.path.join(work, "stills")
        if os.path.isdir(st_dir):
            shutil.rmtree(st_dir)
        run([PY, "build.py", "stills"], cwd=proj, env=env)
        scenes = json.load(open(os.path.join(work, "scenes.json"), encoding="utf-8"))
        sheets = _sheets(st_dir, scenes, os.path.join(work, "qa"))
        for s in sheets:
            E.artifact("sheet", s, os.path.basename(s))
        return sheets, scenes

    if want("stills"):
        E.stage("stills")
        sheets, scenes = stills()
        E.stage("stills", "done", f"{len(sheets)} contact sheets")

    if want("qa"):
        vision = ai.resolve("vision") if job.get("ai_qa") else None
        if vision:
            E.stage("qa")
            sheets = sorted(glob.glob(os.path.join(work, "qa", "qa_*.jpg")))
            notes = _visual_qa(sheets, job, vision)
            open(os.path.join(work, "qa", "qa_notes.txt"), "w", encoding="utf-8").write("\n".join(notes) + "\n")
            E.artifact("qa", os.path.join(work, "qa", "qa_notes.txt"), "Visual QA notes")
            if not notes:
                E.stage("qa", "done", "no problems seen")
            elif session is None:
                E.stage("qa", "done", f"{len(notes)} notes (no AI editor to apply them; see the QA notes)")
            else:
                E.log(f"{session.label} is fixing {len(notes)} QA notes")
                body = session.fix("A visual check of the rendered stills (one frame per designed scene) found these problems. "
                                   "Fix each one in the shot list - another picture, a shorter label, a different device - and "
                                   "reply with the full corrected shot list.\n\n" + "\n".join(notes))
                P.write_build(proj, job, body, session.label + " + visual QA", w)
                info = _plan(proj, env)
                if not info["ok"]:
                    raise RuntimeError(info["error"])
                run([PY, "build.py", "prep"], cwd=proj, env=env)
                stills()
                E.stage("qa", "done", f"{len(notes)} notes fixed")
        else:
            E.stage("qa", "skipped", "visual QA off" if not job.get("ai_qa") else "no AI vision provider (Settings → AI)")

    if want("render"):
        E.stage("render")
        run([PY, "build.py", "render"], cwd=proj, on_line=_render_progress, env=env)
        E.stage("render", "done")
    if want("mix"):
        E.stage("mix")
        run([PY, "build.py", "mix"], cwd=proj, env=env)
        E.stage("mix", "done")
    out_mp4 = os.path.join(M, "out", job["name"] + ".mp4")
    if want("final"):
        E.stage("final")
        run([PY, "build.py", "final"], cwd=proj, on_line=_render_progress, env=env)
        E.artifact("video", out_mp4, "Final video")
        E.stage("final", "done")
    link = None
    if want("deliver"):
        E.stage("deliver")
        d = job.get("deliver", {})
        cmd = [PY, os.path.join(DOCU, "tools", "deliver.py"), out_mp4, "--limit-gb", str(d.get("limit_gb", 1.0))]
        if not d.get("upload"):
            cmd.append("--no-upload")
        tail = run(cmd)
        for l in tail:
            if l.startswith("gofile:"):
                link = l.split("gofile:", 1)[1].strip()
                E.artifact("link", link, "gofile link")
        small = out_mp4.replace(".mp4", "_small.mp4")
        if os.path.exists(small):
            out_mp4 = small
            E.artifact("video", small, "Final video (under the size limit)")
        E.stage("deliver", "done", link or "checked")
    if want("metadata"):
        E.stage("metadata")
        scenes = json.load(open(os.path.join(work, "scenes.json"), encoding="utf-8"))
        meta = _metadata(proj, job, scenes, editor)
        E.artifact("metadata", meta, "YouTube metadata")
        E.stage("metadata", "done")
    E.emit("done", ok=True, output=out_mp4, link=link, project=proj)


def _visual_qa(sheets, job, vision):
    """the vision provider looks at the stills contact sheets -> a list of problems ("0012: ...") or []"""
    import ai
    out = []
    prompt = ("These are contact sheets of a faceless documentary's stills, titled \"{title}\": one frame per designed scene, "
              "each labelled under it with the scene id and the words spoken there (clips are not shown). Check every frame: "
              "the picture fits its words and place, no text cut off at the frame edges, no overlapping labels, no black "
              "borders or letterboxing, no readable private data (names or ID numbers), no watermark, the same picture not "
              "repeated in neighbouring scenes. For each frame with a problem write ONE line: <scene id, e.g. s012>: <the problem> -> "
              "<a fix>. If nothing is wrong on these sheets, reply only OK.")
    for k in range(0, len(sheets), 4):
        part = sheets[k:k + 4]
        E.progress(k / max(1, len(sheets)), f"visual QA: sheets {k + 1}-{k + len(part)} of {len(sheets)}", "qa")
        try:
            chat = ai.Chat("vision", provider=vision, log=E.log)
            ans = chat.send(prompt.format(title=job["title"]), images=part, max_tokens=3000)
        except Exception as e:                           # noqa: BLE001 - QA is a bonus; never fail the video on it
            E.log(f"visual QA failed on sheets {k + 1}-{k + len(part)}: {e}")
            continue
        for l in ans.split("\n"):
            l = l.strip().lstrip("-*• ").strip()
            l = re.sub(r"^\**(?:scene\s*)?(s\d{3})\**", r"\1", l, flags=re.I)
            if re.match(r"^s\d{3}\s*[:\-]", l) and len(l) > 8:
                out.append(l)
    E.log(f"visual QA ({ai.LABEL[vision]}): {len(out)} problems" + ("" if not out else ": " + "; ".join(out[:5])))
    return out


def _make_frontier(job, w, M, proj, work, data):
    """a Frontier style: Frontier's engine makes the video from the script (+ our voiceover), we deliver it"""
    import frontier
    fdir = frontier.find_dir(w)
    if not fdir or not os.path.exists(os.path.join(fdir, "make_video.py")):
        raise RuntimeError("Frontier's engine is not on this computer: Settings → Frontier folder (or Download Frontier).")
    audio = os.path.join(work, "vo.mp3")
    audio = audio if os.path.exists(audio) and job.get("voice", {}).get("mode") != "frontier" else None
    script = open(os.path.join(data, "script.txt"), encoding="utf-8-sig").read() if os.path.exists(os.path.join(data, "script.txt")) \
        else open(job["script"], encoding="utf-8-sig").read()
    minutes = len(script.split()) / 150.0
    if audio:
        minutes = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", audio],
                                       capture_output=True, text=True).stdout or 600) / 60
    style = job["style"].split(":", 1)[1]
    E.stage("render", "running", f"Frontier · {style}")
    out_dir = os.path.join(M, "out")
    files = frontier.run(fdir, style, job["title"], script, out_dir, job["name"], audio=audio, minutes=minutes,
                         python=os.environ.get("FRONTIER_PYTHON") or PY, log=E.log,
                         progress=lambda v, m: E.progress(v, m, "render"))
    for st in ("timing", "shotlist", "plan", "prep", "stills", "qa"):
        E.stage(st, "skipped", "done by Frontier")
    E.stage("render", "done", "Frontier")
    E.stage("mix", "skipped", "done by Frontier")
    out_mp4 = files["video"]
    E.artifact("video", out_mp4, "Final video")
    if files.get("srt"):
        E.artifact("srt", files["srt"], "Subtitles (SRT)")
    E.stage("final", "done")
    link = None
    d = job.get("deliver", {})
    E.stage("deliver")
    cmd = [PY, os.path.join(DOCU, "tools", "deliver.py"), out_mp4, "--limit-gb", str(d.get("limit_gb", 1.0))]
    if not d.get("upload"):
        cmd.append("--no-upload")
    for l in run(cmd):
        if l.startswith("gofile:"):
            link = l.split("gofile:", 1)[1].strip()
            E.artifact("link", link, "gofile link")
    E.stage("deliver", "done", link or "checked")
    E.stage("metadata")
    if files.get("desc"):
        shutil.copy(files["desc"], os.path.join(proj, "youtube_metadata.txt"))
        E.artifact("metadata", os.path.join(proj, "youtube_metadata.txt"), "YouTube metadata")
    E.stage("metadata", "done")
    E.emit("done", ok=True, output=out_mp4, link=link, project=proj)


def cmd_frontier_fetch(a):
    import frontier
    w = P.workspace(a.workspace)
    dest = os.environ.get("FRONTIER_DIR") or os.path.join(P.media(w), "frontier")
    E.stage("frontier")
    frontier.fetch(dest, log=E.log, progress=lambda v, m: E.progress(v, m, "frontier"))
    req = os.path.join(dest, "requirements.txt")
    if os.path.exists(req):
        E.log("installing Frontier's Python requirements")
        run([os.environ.get("FRONTIER_PYTHON") or PY, "-m", "pip", "install", "-r", req])
    E.stage("frontier", "done", dest)
    E.emit("done", ok=True, output=dest)


def cmd_frontier_open(a):
    """start Frontier's own app (its full UI and tools) and keep it running until stopped"""
    import frontier
    w = P.workspace(a.workspace)
    fdir = frontier.find_dir(w)
    if not fdir:
        raise RuntimeError("No Frontier folder: Settings → Frontier folder, or Download Frontier.")
    base, proc = frontier.server(fdir, os.environ.get("FRONTIER_PYTHON") or PY, log=E.log)
    E.emit("result", data=dict(url=base))
    E.artifact("link", base, "Frontier app")
    if proc:
        for line in proc.stdout:
            E.log(line.rstrip())
    E.emit("done", ok=True)


def cmd_frontier_kit(a):
    """Frontier's kit preview: every scene of one look kit as a short clip"""
    import frontier
    w = P.workspace(a.workspace)
    fdir = frontier.find_dir(w)
    if not fdir:
        raise RuntimeError("No Frontier folder.")
    E.stage("preview")
    run([os.environ.get("FRONTIER_PYTHON") or PY, "kits.py", "preview", a.kit], cwd=fdir)
    E.stage("preview", "done")
    E.emit("done", ok=True, output=os.path.join(fdir, "preview", "kits"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workspace")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("info"); sub.add_parser("doctor"); sub.add_parser("setup")
    k = sub.add_parser("kit"); k.add_argument("--drive"); k.add_argument("--folder", help="a folder on this PC, or 'frontier'")
    f = sub.add_parser("niche-fetch"); f.add_argument("--niche", required=True)
    n = sub.add_parser("niche-add")
    n.add_argument("--name", required=True); n.add_argument("--drive"); n.add_argument("--folder")
    n.add_argument("--clips"); n.add_argument("--images"); n.add_argument("--tags")
    n.add_argument("--id"); n.add_argument("--description"); n.add_argument("--clip-share", default=30)
    n.add_argument("--style", default="documentary"); n.add_argument("--map-hint")
    nl = sub.add_parser("niche-link"); nl.add_argument("--niche", required=True); nl.add_argument("--folder", required=True)
    nl.add_argument("--clips"); nl.add_argument("--images"); nl.add_argument("--tags")
    c = sub.add_parser("niche-catalog"); c.add_argument("--niche", required=True); c.add_argument("--split", action="store_true")
    c.add_argument("--tags")
    c.add_argument("--topic-regex", default=r"^([a-z_]+?)_[0-9a-f]{16}\.")
    v = sub.add_parser("voice"); v.add_argument("--voice-id")
    m = sub.add_parser("make"); m.add_argument("--job", required=True); m.add_argument("--from", dest="start", choices=STAGES)
    sub.add_parser("frontier-fetch"); sub.add_parser("frontier-open")
    fk = sub.add_parser("frontier-kit"); fk.add_argument("--kit", default="all")
    a = ap.parse_args()
    try:
        {"info": cmd_info, "doctor": cmd_doctor, "setup": cmd_setup, "kit": cmd_kit, "niche-fetch": cmd_niche_fetch,
         "niche-add": cmd_niche_add, "niche-link": cmd_niche_link, "niche-catalog": cmd_niche_catalog, "voice": cmd_voice, "make": cmd_make,
         "frontier-fetch": cmd_frontier_fetch, "frontier-open": cmd_frontier_open, "frontier-kit": cmd_frontier_kit}[a.cmd](a)
    except Exception as e:                              # noqa: BLE001 - every failure reaches the app as an event
        E.error(str(e))
        E.emit("done", ok=False, error=str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
