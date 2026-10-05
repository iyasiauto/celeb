#!/usr/bin/env python3
"""
make_video.py - pick a template, point it at your footage, and the video gets made.

    python make_video.py                      # asks everything step by step
    python make_video.py --title "..." --script script.txt --audio vo.mp3 --srt vo.srt \
        --template almanac --folder "D:/My Footage" [--online "query, query"] [--upload]

Steps it runs for you (all logged; any step can be resumed with --resume <stage>):
    1 footage   your folder (linked, not copied) / a Google Drive folder link / an existing niche,
                optionally topped up from Pexels, Pixabay, Wikimedia (and Google, licence unknown)
    2 catalog   contact sheets of every clip and picture, described by your AI vision provider if one is
                set up (api_keys/keys.env), otherwise from file names and folder names
    3 make      voice / timing / shot list (AI editor or offline rules) / plan check / stills / render /
                mix / final / size check (+ gofile link) / YouTube metadata

Templates (see TEMPLATES.md): paper, forensic, expedition, broadcast, documentary, almanac
- plus any folder in styles/ with a style.json.
"""

import argparse
import glob
import json
import os
import re
import shutil
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.abspath(__file__))          # the kit: engine, templates, shared assets
WS = ROOT                                                  # where projects / media live: the kit, or a niche workspace
NICHE = {}                                                 # the workspace's niche.json (niche.py)
DOCU = os.path.join(ROOT, "docu")
STUDIO = os.path.join(DOCU, "studio", "studio.py")
TOOLS = os.path.join(DOCU, "tools")
sys.path[:0] = [os.path.join(DOCU, "studio"), DOCU, TOOLS]
PY = sys.executable
VIDEO_EXT = (".mp4", ".mov", ".mkv", ".webm", ".m4v", ".avi")
IMAGE_EXT = (".jpg", ".jpeg", ".png", ".webp")

TEMPLATES = [
    ("documentary", "Calm documentary", 30, "slow photographs, soft dissolves, serif chapter cards, place captions, gentle charts"),
    ("almanac", "Heritage almanac", 45, "opens on moving footage, slab headings over clips, quilt-frame cards, paper charts, cream survey map"),
    ("paper", "Paper / Vox explainer", 25, "paper tabletop collages, cut-outs, typed strips, stamps, newspaper pages, ledger maths"),
    ("forensic", "Forensic lab report", 25, "observed / claimed / confirmed filter, certainty gauge, x-ray scans, source network"),
    ("expedition", "Expedition & courtroom", 25, "field journal, antique map routes, evidence tags, scales of justice, verdict"),
    ("broadcast", "Breaking-news broadcast", 30, "LIVE bug and ticker, BREAKING slab, fact-check meters, headline wall, bumpers"),
]


# ------------------------------------------------------------------ small helpers
def ask(q, default=None, required=True):
    while True:
        a = input(f"{q}" + (f" [{default}]" if default not in (None, "") else "") + ": ").strip().strip('"').strip("'")
        if not a and default is not None:
            return default
        if a or not required:
            return a
        print("  (needed)")


def yes(q, default=False):
    a = input(f"{q} [{'Y/n' if default else 'y/N'}]: ").strip().lower()
    return default if not a else a.startswith("y")


def slugify(s):
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")[:50] or "video"


def env():
    e = dict(os.environ, PYTHONUNBUFFERED="1", PYTHONIOENCODING="utf-8")
    e["STUDIO_WORKSPACE"] = WS
    e["VIDEO_ROOT"] = os.path.join(WS, "media")
    e.setdefault("VIDEO_KIT", os.path.join(ROOT, "media", "kit"))
    e.setdefault("DOCU_ASSETS", os.path.join(ROOT, "media", "kit"))
    if NICHE:
        e["STUDIO_NICHES"] = os.path.join(WS, "niches")      # this niche's registry only - niches never mix
        e["DOCU_NICHE"] = NICHE["id"]
    return e


def find_workspace(arg):
    """--workspace, or a niche.json in the current folder or one above it"""
    for d in ([arg] if arg else [os.getcwd(), os.path.dirname(os.getcwd())]):
        if d and os.path.isfile(os.path.join(d, "niche.json")):
            return os.path.abspath(d)
    if arg:
        sys.exit(f"not a niche workspace (no niche.json): {arg}")
    return None


def studio(*args, quiet=False):
    """run one studio.py command, print its events as readable lines; returns the 'result' data or True"""
    p = subprocess.Popen([PY, STUDIO, "--workspace", WS, *args], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env(),
                         text=True, encoding="utf-8", errors="replace", bufsize=1)
    result, ok, last_p = None, None, 0
    for line in p.stdout:
        line = line.rstrip()
        try:
            ev = json.loads(line)
        except ValueError:
            if line and not quiet:
                print("   " + line[:200])
            continue
        t = ev.get("t")
        if t == "stage":
            mark = {"running": "▶", "done": "✓", "skipped": "·", "error": "✗"}.get(ev.get("status"), "•")
            print(f" {mark} {ev['stage']:<9} {ev.get('msg') or ''}", flush=True)
        elif t == "progress":
            if time.time() - last_p > 4:
                print(f"     {int(100 * ev.get('value', 0)):3d}%  {(ev.get('msg') or '')[:100]}", flush=True)
                last_p = time.time()
        elif t == "log" and not quiet:
            print("   " + str(ev.get("msg"))[:200])
        elif t == "artifact" and ev.get("kind") in ("video", "link", "metadata", "srt"):
            print(f"   → {ev.get('label')}: {ev.get('path')}")
        elif t == "result":
            result = ev.get("data")
        elif t == "error":
            print("   ERROR: " + str(ev.get("msg"))[-1500:])
        elif t == "done":
            ok = ev.get("ok")
    p.wait()
    if p.returncode != 0 or ok is False:
        raise SystemExit(f"\nstopped at: studio.py {' '.join(args[:2])}  (fix the error above, then run again with --resume)")
    return result if result is not None else True


LINKED = {}                       # linked name -> original path (to carry a pool's qc.json over)


def link_into(src_dir, clips_dir, images_dir):
    """every video and picture under src_dir linked (or copied) flat into clips_dir / images_dir"""
    n = 0
    for d, dirs, files in os.walk(src_dir):
        dirs[:] = [x for x in dirs if not x.startswith((".", "_"))]
        for f in files:
            if f.startswith(("qc_", ".", "_")):
                continue                     # the kit's own reports and sheets, never footage
            ext = os.path.splitext(f)[1].lower()
            dst_dir = clips_dir if ext in VIDEO_EXT else images_dir if ext in IMAGE_EXT else None
            if not dst_dir:
                continue
            rel = os.path.relpath(d, src_dir)
            pooled = rel.replace("\\", "/") in ("clips", "images", "source_video")    # a pool's own folders keep the names
            name = f if (rel == "." or pooled) else f"{slugify(rel)}__{f}"
            dst = os.path.join(dst_dir, name)
            LINKED[name] = os.path.join(d, f)
            if os.path.exists(dst):
                continue
            os.makedirs(dst_dir, exist_ok=True)
            for fn in (os.link, os.symlink):
                try:
                    fn(os.path.abspath(os.path.join(d, f)), dst)
                    break
                except OSError:
                    continue
            else:
                shutil.copy2(os.path.join(d, f), dst)
            n += 1
    return n


def drive_id(link):
    m = re.search(r"folders/([A-Za-z0-9_-]+)", link) or re.search(r"id=([A-Za-z0-9_-]+)", link)
    return m.group(1) if m else link.strip()


def check_engine():
    missing = []
    for mod in ("numpy", "PIL", "playwright"):
        try:
            __import__(mod)
        except ImportError:
            missing.append(mod)
    if not (shutil.which("ffmpeg") and shutil.which("ffprobe")):
        try:
            import static_ffmpeg
            static_ffmpeg.add_paths()            # puts ffmpeg on PATH for every step below
        except ImportError:
            missing.append("ffmpeg")
    if missing:
        print(f"Python packages missing ({', '.join(missing)}): run setup first (setup.bat on Windows, ./setup.sh on Mac/Linux).")
        sys.exit(1)
    if not os.path.isdir(os.path.join(ROOT, "media", "kit", "fonts")):
        print("The asset kit (media/kit) is missing - downloading it from the Drive once…")
        studio("kit")


def carry_qc(base):
    """the pools' qc.json entries, renamed for the linked files, into <base>/qc.json"""
    out_p = os.path.join(base, "qc.json")
    out = json.load(open(out_p, encoding="utf-8")) if os.path.exists(out_p) else {}
    cache = {}
    n = 0
    for name, src in LINKED.items():
        if name in out:
            continue
        d = os.path.dirname(src)
        for q in (os.path.join(d, "qc.json"), os.path.join(os.path.dirname(d), "qc.json")):
            if q not in cache:
                cache[q] = json.load(open(q, encoding="utf-8")) if os.path.exists(q) else {}
            r = cache[q].get(os.path.basename(src))
            if r:
                out[name] = r
                n += 1
                break
    if out:
        json.dump(out, open(out_p, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    return n


def run_qc(base, topic):
    """mandatory vision QC of everything this video may use; files QC'd before are not checked again"""
    import ai
    if not ai.resolve("vision"):
        if os.environ.get("DOCU_SKIP_QC") == "1":
            print("   QC skipped (DOCU_SKIP_QC=1) - talking heads and logos are NOT being checked")
            return
        sys.exit("No vision AI for QC. Put OPENLUX_API_KEY in api_keys/keys.env (Gemini 2.5 Flash Lite checks every clip for "
                 "talking heads, influencers, watermarks and logos). QC is mandatory.")
    subprocess.run([PY, os.path.join(TOOLS, "qc_pool.py"), base, "--topic", topic, "--workers", "8"], env=env(), check=True)


# ------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser(description="make a video from a template")
    ap.add_argument("--title"); ap.add_argument("--script"); ap.add_argument("--audio"); ap.add_argument("--srt")
    ap.add_argument("--famespeak-voice", help="make the voiceover with FameSpeak (FAMESPEAK_API_KEY) instead of --audio")
    ap.add_argument("--template", help="documentary | almanac | paper | forensic | expedition | broadcast | custom:<folder>")
    ap.add_argument("--folder", help="footage folder on this computer (videos + pictures, any sub-folders)")
    ap.add_argument("--drive", help="Google Drive folder link with the footage (shared: anyone with the link)")
    ap.add_argument("--niche", help="use an existing niche (docu/studio/niches/<id>.json)")
    ap.add_argument("--online", help="also fetch from free libraries: comma-separated searches, or 'auto' (from the script)")
    ap.add_argument("--sources", default="pexels,pixabay,wikimedia", help="online sources (add google for Google Images, licence unknown)")
    ap.add_argument("--clip-share", type=int)
    ap.add_argument("--ai", default="auto", choices=["auto", "none"], help="auto = AI editor if one is set up, else offline rules")
    ap.add_argument("--upload", action="store_true", help="upload the result to gofile (link + md5)")
    ap.add_argument("--limit-gb", type=float, default=1.0)
    ap.add_argument("--resume", choices=["footage", "catalog", "voice", "timing", "shotlist", "plan", "prep", "stills", "render",
                                         "mix", "final", "deliver", "metadata"])
    ap.add_argument("--until", choices=["catalog", "shotlist", "plan", "stills", "render", "final"],
                    help="stop after this stage (agents: --until shotlist, write projects/<title>/build.py, then --resume plan)")
    ap.add_argument("--yes", action="store_true", help="no questions (use the flags and defaults)")
    ap.add_argument("--workspace", help="a niche workspace (niche.py new ...); found automatically when you run from inside one")
    ap.add_argument("--style", help="a style from styles/ (python docu/registry.py list)")
    ap.add_argument("--topic", help="what the video is about - QC judges relevance against it")
    a = ap.parse_args()
    interactive = not a.yes
    global WS, NICHE
    w = find_workspace(a.workspace)
    if w:
        WS = w
        NICHE = json.load(open(os.path.join(w, "niche.json"), encoding="utf-8"))
        print(f"niche workspace: {NICHE['name']}  ({w})")
        os.environ.update(STUDIO_NICHES=os.path.join(w, "niches"), STUDIO_WORKSPACE=w, VIDEO_ROOT=os.path.join(w, "media"),
                          DOCU_NICHE=NICHE["id"])
        a.template = a.template or (None if a.style else NICHE.get("template"))
        a.style = a.style or (NICHE.get("style") if not a.template or a.template == NICHE.get("template") else None)
        a.topic = a.topic or NICHE.get("topic")
    if a.topic:
        os.environ["DOCU_TOPIC"] = a.topic          # QC and final QC judge relevance against the niche's topic
        if not (a.folder or a.drive or a.niche or a.online):
            a.folder = os.path.join(w, NICHE.get("pool", "pool"))
    if a.style:
        import registry
        pb = registry.resolve(a.style)
        a.template = a.template or pb["id"]
        os.environ["DOCU_STYLE"] = a.style

    print("\n=== Docu Templates · make a video ===\n")
    check_engine()
    title = a.title or ask("Video title")
    slug = slugify(title)
    state_f = os.path.join(WS, "media", "runs", slug + ".json")
    state = json.load(open(state_f)) if os.path.exists(state_f) else {}

    script = a.script or state.get("script") or ask("Script file (.txt)")
    if not os.path.isfile(script):
        sys.exit(f"script not found: {script}")
    if a.famespeak_voice:
        voice = dict(mode="famespeak", voice_id=a.famespeak_voice)
    elif a.audio or state.get("voice"):
        voice = state.get("voice") if not a.audio else dict(mode="file", mp3=os.path.abspath(a.audio),
                                                             srt=os.path.abspath(a.srt) if a.srt else None)
    elif interactive and yes("Make the voiceover with FameSpeak (needs FAMESPEAK_API_KEY)?", False):
        voice = dict(mode="famespeak", voice_id=ask("ElevenLabs voice ID"))
    else:
        mp3 = ask("Voiceover file (.mp3/.wav)")
        srt = ask("Subtitles .srt (optional, Enter to skip - Whisper will time the words)", "", required=False)
        voice = dict(mode="file", mp3=os.path.abspath(mp3), srt=os.path.abspath(srt) if srt else None)

    import project as P
    styles = P.all_styles(WS)
    import registry
    for tid in registry.templates():                       # templates dropped into templates/ are choosable too
        if tid not in styles and registry.templates()[tid]["installed"]:
            t = registry.templates()[tid]
            styles[tid] = dict(name=t["name"], blurb=t.get("look", ""), theme=t["theme"])
    template = a.template or state.get("template")
    if not template:
        print("\nTemplates:")
        opts = [t for t in TEMPLATES] + [(k, v["name"], 30, v.get("blurb", "")[:80]) for k, v in styles.items() if k.startswith("custom:")]
        for i, (k, name, cs, blurb) in enumerate(opts, 1):
            print(f"  {i}. {name:<26} {blurb}")
        c = ask("Choose a template (number)", "1")
        template = opts[int(c) - 1][0] if c.isdigit() and 0 < int(c) <= len(opts) else c
    if template not in styles:
        sys.exit(f"unknown template {template}; choose one of: {', '.join(k for k in styles if not k.startswith('frontier:'))}")
    clip_share = a.clip_share or state.get("clip_share") or next((t[2] for t in TEMPLATES if t[0] == template), 30)

    # ---------------------------------------------------------- 1 footage
    niche = a.niche or state.get("niche")
    folder, drive, online = a.folder, a.drive, a.online
    if not niche and not (folder or drive or online):
        print("\nWhere is the footage (clips and pictures) for this video?")
        print("  1. A folder on this computer")
        print("  2. A Google Drive folder link")
        print("  3. An existing niche: " + ", ".join(n["id"] for n in P.niches()))
        print("  4. Nothing yet - fetch it online (Pexels / Pixabay / Wikimedia)")
        c = ask("Choose", "1")
        if c == "1":
            folder = ask("Folder path")
        elif c == "2":
            drive = ask("Drive folder link")
        elif c == "3":
            niche = ask("Niche id")
        else:
            online = "auto"
        if c in ("1", "2") and yes("Also fetch extra footage online (Pexels / Pixabay / Wikimedia)?", False):
            online = ask("Searches, comma-separated (or 'auto' to pick them from the script)", "auto")
        if online and yes("Include Google Images too (licence unknown - check each picture)?", False):
            a.sources += ",google"

    if not niche:
        niche = slug
        base = os.path.join(WS, "media", niche, "src")
        clips, images = os.path.join(base, "clips"), os.path.join(base, "images")
        if a.resume in (None, "footage"):
            print("\n[1/3] Footage")
            os.makedirs(clips, exist_ok=True); os.makedirs(images, exist_ok=True)
            if folder:
                if not os.path.isdir(folder):
                    sys.exit(f"folder not found: {folder}")
                print(f"   {link_into(folder, clips, images)} files linked from {folder}")
            if drive:
                dl = os.path.join(WS, "media", niche, "drive")
                subprocess.run([PY, os.path.join(TOOLS, "fetch_drive.py"), drive_id(drive), dl, "12"], env=env(), check=True)
                print(f"   {link_into(dl, clips, images)} files from the Drive folder")
            if online:
                cmd = [PY, os.path.join(TOOLS, "fetch_online.py"), "--out", base, "--sources", a.sources]
                cmd += ["--script", script, "--title", title] if online.strip().lower() == "auto" else ["--query", online]
                subprocess.run(cmd, env=env(), check=True)
            nc, ni = len(os.listdir(clips)), len(os.listdir(images))
            print(f"   footage ready: {nc} clips, {ni} pictures")
            if nc + ni == 0:
                sys.exit("no footage: give a folder, a Drive link or --online searches")
            print("\n[QC] talking heads, influencers, watermarks, logos, relevance")
            print(f"   {carry_qc(base)} files already checked in their pool")
            run_qc(base, a.topic or title)
            studio("niche-add", "--name", title, "--id", niche, "--folder", base, "--clips", clips, "--images", images,
                   "--style", template, "--clip-share", str(clip_share), quiet=True)
        a.resume = None if a.resume == "footage" else a.resume
    else:
        n = P.niche(niche)
        if not P.niche_status(n, WS)["downloaded"] and a.resume in (None, "footage"):
            print("\n[1/3] Footage: downloading the niche from its Drive folder")
            studio("niche-fetch", "--niche", niche)

    # ---------------------------------------------------------- 2 catalog
    n = P.niche(niche)
    st = P.niche_status(n, WS)
    if a.resume in (None, "footage", "catalog") and (not st["clip_catalog"] or a.resume == "catalog" or not n.get("drive")):
        print("\n[2/3] Catalog (contact sheets + descriptions)")
        studio("niche-catalog", "--niche", niche)

    # ---------------------------------------------------------- 3 make
    state.update(title=title, script=os.path.abspath(script), voice=voice, template=template, niche=niche, clip_share=clip_share)
    os.makedirs(os.path.dirname(state_f), exist_ok=True)
    json.dump(state, open(state_f, "w"), indent=1)
    job = dict(title=title, niche=niche, style=template, clip_share=clip_share, script=os.path.abspath(script), voice=voice,
               shotlist="ai" if a.ai == "auto" else "auto", ai_qa=a.ai == "auto", effort="high",
               workers=max(2, min(8, (os.cpu_count() or 4) - 2)), deliver=dict(upload=bool(a.upload), limit_gb=a.limit_gb))
    jf = os.path.join(WS, "media", "runs", slug + ".job.json")
    json.dump(job, open(jf, "w"), indent=1)
    print(f"\n[3/3] Making the video · template {styles[template]['name']} · footage '{niche}' · {clip_share} % clips")
    args = ["make", "--job", jf]
    if a.resume and a.resume not in ("footage", "catalog"):
        args += ["--from", a.resume]
    if a.until == "catalog":
        print("\nStopped after the catalog (--until catalog).")
        return
    if a.until:
        args += ["--until", a.until]
    studio(*args)
    if a.until:
        print(f"\nStopped after '{a.until}'. Shot list: projects/{slug}/build.py · stills: media/work/{slug}/qa/ · "
              f"continue with: {'make.bat / ./make.sh' if WS != ROOT else 'python make_video.py'} --title \"{title}\" --yes --resume <next stage>")
        return
    print("\nDone. The video, subtitles and YouTube metadata are in media/out/ and projects/" + slug + "/")
    print("Edit projects/" + slug + "/build.py to change any shot, then: python make_video.py --title \"" + title +
          "\" --yes --resume shotlist   (or cd into the project and run python build.py stills / render / final)")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nstopped")
