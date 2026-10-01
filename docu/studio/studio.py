"""
studio.py - the Docu Studio backend. The desktop app runs it; it also works on its own.

    python studio.py info                         workspace, styles, niches, projects, keys present
    python studio.py doctor                       what is installed / missing
    python studio.py setup                        install Python packages, Chromium, FFmpeg
    python studio.py kit                          download the asset kit (music, fonts, maps, cut-outs) + props
    python studio.py niche-fetch --niche hasidic  download a niche's footage and stage its pictures
    python studio.py niche-add --name "..." --drive <folder link>   register a new niche
    python studio.py niche-catalog --niche <id>   contact sheets + Claude descriptions -> catalog
    python studio.py voice --voice-id <id>        look up a FameSpeak / ElevenLabs voice
    python studio.py make --job job.json [--from render]            make a video end to end

Every line on stdout is a JSON event (events.py). Keys come from the environment (the app passes them),
or api_keys/keys.env: FAMESPEAK_API_KEY, ANTHROPIC_API_KEY, GOFILE_TOKEN.
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
    E.result(dict(workspace=w, media=M, styles=styles, niches=niches, projects=projects,
                  frontier=dict(dir=fdir, engine=bool(fdir and os.path.exists(os.path.join(fdir, "make_video.py"))),
                                env=bool(fdir and os.path.exists(os.path.join(fdir, ".env")))),
                  styles_folder=os.path.join(w, "styles"),
                  keys={k: bool(key(k)) for k in ("FAMESPEAK_API_KEY", "ANTHROPIC_API_KEY", "GOFILE_TOKEN")}))


def cmd_doctor(a):
    w = P.workspace(a.workspace)
    M = P.media(w)
    checks = []

    def add(name, ok, detail="", fix=""):
        checks.append(dict(name=name, ok=bool(ok), detail=detail, fix=fix))
    add("Python 3.10+", sys.version_info >= (3, 10), sys.version.split()[0], "install Python 3.10 or newer")
    for mod, pip in (("numpy", "numpy"), ("scipy", "scipy"), ("PIL", "Pillow"), ("playwright", "playwright"),
                     ("rembg", "rembg[cpu]"), ("faster_whisper", "faster-whisper"), ("anthropic", "anthropic"), ("gdown", "gdown")):
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
        add(f"Asset kit: {sub}", n > 0, f"{n} files", "Niches → Download asset kit")
    add("FameSpeak API key", key("FAMESPEAK_API_KEY"), "", "Settings → API keys (only for generated voiceovers)")
    add("Claude API key", key("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN"), "",
        "Settings → API keys (AI shot list, AI QA and AI cataloging)")
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
    drive = a.drive or "1CYxavMgiqBwVtUwFMizA-Txnf4123yYq"
    run([PY, os.path.join(DOCU, "tools", "fetch_drive.py"), drive, os.path.join(M, "kit"), "12"], on_line=_fetch_progress)
    run([PY, os.path.join(DOCU, "tools", "props.py"), os.path.join(M, "kit", "cutouts")])
    E.stage("kit", "done")
    E.emit("done", ok=True)


def _fetch_progress(line):
    m = re.search(r"(\d+) / (\d+)", line)
    if m:
        E.progress(int(m.group(1)) / max(1, int(m.group(2))), line)
    else:
        E.log(line)


# ------------------------------------------------------------------ niches
def cmd_niche_fetch(a):
    w = P.workspace(a.workspace)
    M = P.media(w)
    n = P.niche(a.niche)
    E.stage("download")
    run([PY, os.path.join(DOCU, "tools", "fetch_drive.py"), n["drive"], os.path.join(M, n["download_to"]), "12"],
        on_line=_fetch_progress)
    E.stage("download", "done")
    E.stage("stage")
    sv = os.path.join(M, n["footage"], "source_video")
    if os.path.normpath(sv) != os.path.normpath(os.path.join(M, n["source_video"])) and not os.path.exists(sv):
        os.makedirs(os.path.dirname(sv), exist_ok=True)
        try:
            os.symlink(os.path.join(M, n["source_video"]), sv, target_is_directory=True)
        except OSError:
            shutil.copytree(os.path.join(M, n["source_video"]), sv)
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
    picks_json = os.path.join(w, n.get("catalog_from") or "", "image_picks.json")
    if n.get("picks") and os.path.exists(picks_json):
        run([PY, os.path.join(DOCU, "tools", "catalog_images.py"), "stage", picks_json, os.path.join(M, n["images"]),
             os.path.join(M, n["picks"])])
    E.stage("stage", "done")
    E.emit("done", ok=True)


def cmd_niche_add(a):
    nid = P.slugify(a.id or a.name)
    n = dict(id=nid, name=a.name, description=a.description or "", drive=a.drive, download_to=f"{nid}/src",
             footage=f"{nid}/footage", source_video=f"{nid}/src/clips", images=f"{nid}/src/images",
             picks=f"{nid}/picks", image_dirs=[f"{nid}/picks", f"{nid}/src/images"], catalog_from=f"catalogs/{nid}",
             clip_share=int(a.clip_share), default_style=a.style, map_hint=a.map_hint or "")
    E.result(P.save_niche(n))


def _guess_dirs(root):
    """after a download: the folder with the most videos and the one with the most pictures"""
    best_v, best_i = (0, None), (0, None)
    for d, _, files in os.walk(root):
        v = sum(f.lower().endswith((".mp4", ".mov", ".mkv", ".webm", ".m4v")) for f in files)
        i = sum(f.lower().endswith((".jpg", ".jpeg", ".png", ".webp")) for f in files)
        best_v = max(best_v, (v, d))
        best_i = max(best_i, (i, d))
    return best_v[1], best_i[1]


def cmd_niche_catalog(a):
    w = P.workspace(a.workspace)
    M = P.media(w)
    n = P.niche(a.niche)
    k = key("ANTHROPIC_API_KEY")
    vdir, idir = _guess_dirs(os.path.join(M, n["download_to"]))
    if vdir:
        n["source_video"] = os.path.relpath(vdir, M).replace(os.sep, "/")
    if idir:
        n["images"] = os.path.relpath(idir, M).replace(os.sep, "/")
        n["image_dirs"] = [n["picks"], n["images"]]
    P.save_niche(n)
    cat = os.path.join(M, n["id"], "cat")
    out = os.path.join(w, n["catalog_from"])
    os.makedirs(out, exist_ok=True)
    import describe
    tools = os.path.join(DOCU, "tools")
    if vdir:
        E.stage("clips")
        run([PY, os.path.join(tools, "catalog_clips.py"), "scan", vdir, cat] + (["--split"] if a.split else []))
        if k:
            describe.describe_clips(cat, n["name"], k, log=E.log, progress=lambda v, m: E.progress(v, m, "clips"))
        else:
            open(os.path.join(cat, "notes_clips.txt"), "w").write("")
            E.log("no Claude key: clips catalogued without descriptions (the offline shot list will match on file names only)")
        run([PY, os.path.join(tools, "catalog_clips.py"), "build", cat, os.path.join(out, "catalog_all.json")])
        if os.path.exists(os.path.join(cat, "notes_clips.txt")):
            shutil.copy(os.path.join(cat, "notes_clips.txt"), os.path.join(out, "notes_clips.txt"))
        E.stage("clips", "done")
        sv = os.path.join(M, n["footage"], "source_video")
        if not os.path.exists(sv):
            os.makedirs(os.path.dirname(sv), exist_ok=True)
            try:
                os.symlink(vdir, sv, target_is_directory=True)
            except OSError:
                shutil.copytree(vdir, sv)
    if idir:
        E.stage("pictures")
        run([PY, os.path.join(tools, "catalog_images.py"), "scan", idir, cat, "--topic-regex", a.topic_regex])
        if k:
            describe.describe_images(cat, n["name"], k, log=E.log, progress=lambda v, m: E.progress(v, m, "pictures"))
            run([PY, os.path.join(tools, "catalog_images.py"), "pick", cat, idir, os.path.join(M, n["picks"]),
                 os.path.join(out, "image_picks.json")])
            shutil.copy(os.path.join(cat, "notes_img.txt"), os.path.join(out, "notes_img.txt"))
        else:
            E.log("no Claude key: pictures will be used by file name only")
        E.stage("pictures", "done")
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


def _metadata(proj, job, scenes, k, model):
    heads = [s for s in scenes if s["type"] in ("doctitle", "chapter")]
    chapters = ["0:00 " + (job["title"][:60])]
    for s in heads:
        t = int(s["t0"])
        if t > 0:
            chapters.append(f"{t // 60}:{t % 60:02d} " + (s.get("kicker", "") + ": " if s.get("kicker") and s["type"] == "doctitle" and s.get("kicker") != "A documentary" else "") + s.get("title", "").title())
    text = None
    if k:
        try:
            import claude_shotlist as cs
            script = open(os.path.join(proj, "data", "script.txt"), encoding="utf-8").read()
            client = cs._client(k)
            with client.beta.messages.stream(
                model=model, max_tokens=8000, thinking={"type": "adaptive"}, output_config={"effort": "medium"},
                betas=["server-side-fallback-2026-07-01"], fallbacks="default",
                messages=[{"role": "user", "content":
                           "Write YouTube upload metadata for this faceless documentary as plain text with these sections in this order: "
                           "TITLE, ALTERNATIVE TITLES (A/B) (4 lines), DESCRIPTION (2 short paragraphs, factual, no hype, no emojis), "
                           "CHAPTERS (use exactly these lines), TAGS (comma separated, under 450 characters), HASHTAGS (3), "
                           "UPLOAD CHECKLIST (category, thumbnail, chapters, music licences, sources).\n\n"
                           f"Title: {job['title']}\n\nChapters:\n" + "\n".join(chapters) + "\n\nScript:\n" + script}],
            ) as st:
                msg = st.get_final_message()
            if msg.stop_reason != "refusal":
                text = "".join(b.text for b in msg.content if b.type == "text").strip()
        except Exception as e:                          # noqa: BLE001
            E.log(f"metadata via Claude failed ({e}); writing the simple version")
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
    model = job.get("model") or "claude-opus-5-5"
    k_claude = key("ANTHROPIC_API_KEY")
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
        if v.get("mode") == "famespeak":
            import famespeak
            text = open(os.path.join(data, "script.txt"), encoding="utf-8-sig").read()
            mp3, srt = famespeak.make_voiceover(key("FAMESPEAK_API_KEY"), text, v["voice_id"], work,
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
        return _make_frontier(job, w, M, proj, work, data, model, k_claude)

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
    use_claude = job.get("shotlist", "claude") == "claude" and bool(k_claude)

    # shot list + plan loop
    if want("shotlist"):
        E.stage("shotlist")
        clips, images, props = P.assets(proj, w, job)
        dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                    os.path.join(work, "vo.mp3")], capture_output=True, text=True).stdout or 0)
        if use_claude:
            import claude_shotlist as cs
            import variety
            hist = variety.history(os.path.join(w, "projects"), exclude=proj)
            v = variety.pick(variety.seed_for(job["name"]), hist, [])
            v = {kk: v[kk] for kk in ("accent", "kicker", "moves", "place")}
            v["heading_example"] = variety.KICKERS[v["kicker"]](3)
            E.log(f"Claude ({model}) is writing the shot list...")
            session = cs.Session(k_claude, P.style_info(job["style"], w), model=model, effort=job.get("effort", "high"), log=E.log)
            msg = cs.job_message(job, n, open(os.path.join(data, "script.txt"), encoding="utf-8").read(), ptimes, dur,
                                 clips, images, props, v)
            body = session.first(msg, on_text=lambda c: E.progress(min(0.95, c / 45000), f"{c // 1000}k characters written"))
            mode = f"Claude ({model})"
        else:
            if job.get("shotlist", "claude") == "claude":
                E.log("no Claude API key: using the offline shot list")
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
            E.log("sending the plan's problems back to Claude: " + "; ".join(p.split("\n")[0] for p in probs))
            body = session.fix("The engine's plan found these problems. Reply with the full corrected shot list.\n\n" + "\n\n".join(probs))
            P.write_build(proj, job, body, f"Claude ({model})", w)
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
        if job.get("ai_qa") and session is not None:
            E.stage("qa")
            import claude_shotlist as cs
            sheets = sorted(glob.glob(os.path.join(work, "qa", "qa_*.jpg")))
            body = session.fix(
                "Here are the stills contact sheets (one frame per designed scene, labelled with scene id and cue; clips are "
                "not shown). Check every frame against its words and the rules: right picture for the words, right place, "
                "no text cut off at the edges, no overlapping labels, no black borders, no private data, no picture repeated "
                "in consecutive scenes, the device and the pacing. Reply with the full corrected shot list (or the same one "
                "if nothing needs to change).", images=[cs.jpeg_b64(s) for s in sheets[:20]])
            P.write_build(proj, job, body, f"Claude ({model}) + visual QA", w)
            info = _plan(proj, env)
            if not info["ok"]:
                raise RuntimeError(info["error"])
            run([PY, "build.py", "prep"], cwd=proj, env=env)
            stills()
            E.stage("qa", "done")
        else:
            E.stage("qa", "skipped", "AI QA off" if not job.get("ai_qa") else "needs the Claude shot list")

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
        meta = _metadata(proj, job, scenes, k_claude if use_claude else None, model)
        E.artifact("metadata", meta, "YouTube metadata")
        E.stage("metadata", "done")
    E.emit("done", ok=True, output=out_mp4, link=link, project=proj)


def _make_frontier(job, w, M, proj, work, data, model, k_claude):
    """a Frontier style: Frontier's engine makes the video from the script (+ our voiceover), we deliver it"""
    import frontier
    fdir = frontier.find_dir(w)
    if not fdir or not os.path.exists(os.path.join(fdir, "make_video.py")):
        raise RuntimeError("Frontier's engine is not on this computer: Settings → Frontier folder (or Download Frontier).")
    audio = os.path.join(work, "vo.mp3")
    audio = audio if os.path.exists(audio) else None
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
    k = sub.add_parser("kit"); k.add_argument("--drive")
    f = sub.add_parser("niche-fetch"); f.add_argument("--niche", required=True)
    n = sub.add_parser("niche-add")
    for x in ("--name", "--drive"):
        n.add_argument(x, required=True)
    n.add_argument("--id"); n.add_argument("--description"); n.add_argument("--clip-share", default=30)
    n.add_argument("--style", default="documentary"); n.add_argument("--map-hint")
    c = sub.add_parser("niche-catalog"); c.add_argument("--niche", required=True); c.add_argument("--split", action="store_true")
    c.add_argument("--topic-regex", default=r"^([a-z_]+?)_[0-9a-f]{16}\.")
    v = sub.add_parser("voice"); v.add_argument("--voice-id")
    m = sub.add_parser("make"); m.add_argument("--job", required=True); m.add_argument("--from", dest="start", choices=STAGES)
    sub.add_parser("frontier-fetch"); sub.add_parser("frontier-open")
    fk = sub.add_parser("frontier-kit"); fk.add_argument("--kit", default="all")
    a = ap.parse_args()
    try:
        {"info": cmd_info, "doctor": cmd_doctor, "setup": cmd_setup, "kit": cmd_kit, "niche-fetch": cmd_niche_fetch,
         "niche-add": cmd_niche_add, "niche-catalog": cmd_niche_catalog, "voice": cmd_voice, "make": cmd_make,
         "frontier-fetch": cmd_frontier_fetch, "frontier-open": cmd_frontier_open, "frontier-kit": cmd_frontier_kit}[a.cmd](a)
    except Exception as e:                              # noqa: BLE001 - every failure reaches the app as an event
        E.error(str(e))
        E.emit("done", ok=False, error=str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
