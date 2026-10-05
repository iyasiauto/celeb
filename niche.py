#!/usr/bin/env python3
"""
niche.py - one kit, many niches, no mixing.

Every niche gets its own workspace folder. The engine, templates and assets stay in the kit (shared, read-only);
everything that belongs to a niche - its footage pool, its QC, its projects, its renders, its settings - lives
in the workspace and nowhere else. Open a workspace folder in Claude / Antigravity and the agent sees one niche,
one default template, one pool.

    python niche.py new true-crime --template forensic --pool "D:\\Footage\\Crime" --topic "unsolved crimes in the US"
    python niche.py new space --template documentary --drive "https://drive.google.com/drive/folders/..." --topic "space missions"
    python niche.py new history --style paper-vox --topic "ancient empires"        (empty pool: fill it later)
    python niche.py list
    python niche.py qc space                     # vision QC of the whole pool (talking heads, logos, watermarks...)
    python niche.py add space <folder>           # merge more footage into the pool (then qc again)
    python niche.py add space "<old kit>\\media" --only moon,apollo   # pull an old kit's footage, only those videos

Any subject works: the niche's --topic is what QC judges relevance against; the template decides the look.

    workspaces/<niche>/
        niche.json      name, template, style, topic, pool - the defaults every video of this niche uses
        pool/           the footage (clips/ + images/) - or a link to your own folder; qc.json lives here
        projects/       one folder per video: build.py, data/, project.json (pins template + niche)
        media/          renders, work folders, out/   (media/kit links to the kit's shared assets)
        inputs/         scripts and voiceovers you hand in
        make.bat / make.sh   python <kit>/make_video.py --workspace <this folder> ...
        CLAUDE.md, AGENTS.md, GEMINI.md   the agent's instructions, scoped to this niche
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time

KIT = os.path.dirname(os.path.abspath(__file__))
WS_ROOT = os.environ.get("DOCU_WORKSPACES") or os.path.join(KIT, "workspaces")
PY = sys.executable
sys.path[:0] = [os.path.join(KIT, "docu")]


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-") or "niche"


def link_dir(src, dst):
    """symlink, else a Windows junction, else nothing (the caller copies)"""
    if os.path.lexists(dst):
        return True
    try:
        os.symlink(src, dst, target_is_directory=True)
        return True
    except (OSError, NotImplementedError):
        pass
    if os.name == "nt":
        r = subprocess.run(["cmd", "/c", "mklink", "/J", dst, src], capture_output=True)
        return r.returncode == 0
    return False


def ws_dir(name):
    d = os.path.join(WS_ROOT, slug(name))
    if not os.path.isfile(os.path.join(d, "niche.json")):
        raise SystemExit(f"no niche workspace {name!r} (python niche.py list)")
    return d


AGENT_MD = """# Niche workspace: {name}

This folder is ONE niche of the video kit. Everything you do here belongs to **{name}** and nothing else.

| | |
|---|---|
| default template | **{template}**{style_line} |
| topic | {topic} |
| footage pool | `pool/` ({pool_note}) - QC'd: `pool/qc.json` |
| projects | `projects/<video>/` - one folder per video, pinned to its template in `project.json` |
| the kit (engine, templates, docs) | `{kit}` - shared, do not edit it from here |

## Rules for this workspace

1. Read the kit's handover first: `{kit}/kit_docs/HANDOVER.md`, then `{kit}/kit_docs/AGENTS.md`.
2. Before writing any shot list run `python "{kit}/docu/registry.py" show {template_or_style}` and follow it:
   look at the preview sheet, read one worked example in full, use the devices it lists as often as it says.
3. Footage comes ONLY from `pool/` (or online fetches merged into it). Never use another workspace's footage.
4. Every video uses this niche's template unless the user names another one for that video - then pass
   `--template` explicitly; the project pins it and never switches.
5. QC is mandatory: `python "{kit}/niche.py" qc {id}` after new footage. No talking heads, influencers,
   watermarks or logos; corner logos are cropped away by the pipeline.
6. Make a video: `make.bat` / `./make.sh` with the usual make_video.py flags (title, script, audio, srt).
   The edit audit must pass before render; final QC runs after the render.
"""


def cmd_new(a):
    name = a.name
    nid = slug(name)
    d = os.path.join(WS_ROOT, nid)
    if os.path.exists(os.path.join(d, "niche.json")):
        raise SystemExit(f"{d} already exists")
    import registry
    tpl = registry.resolve(a.style or a.template or "documentary")      # validates the template / style now
    for sub in ("projects", "media", "inputs", "niches"):
        os.makedirs(os.path.join(d, sub), exist_ok=True)
    # the shared asset kit, linked so every workspace renders with the same fonts, maps, music and overlays
    kit_media = os.path.join(KIT, "media", "kit")
    if os.path.isdir(kit_media) and not link_dir(kit_media, os.path.join(d, "media", "kit")):
        print("  (could not link media/kit - set VIDEO_KIT to the kit's media/kit)")
    pool = os.path.join(d, "pool")
    pool_note = "empty: add footage with `niche.py add`"
    if a.pool:
        src = os.path.abspath(a.pool)
        if not os.path.isdir(src):
            raise SystemExit(f"not a folder: {src}")
        if link_dir(src, pool):
            pool_note = f"linked to {src}"
        else:
            shutil.copytree(src, pool)
            pool_note = f"copied from {src}"
    else:
        os.makedirs(os.path.join(pool, "clips"), exist_ok=True)
        os.makedirs(os.path.join(pool, "images"), exist_ok=True)
    if a.drive:
        print("downloading the Drive folder into the pool (once)...")
        dl = os.path.join(pool, "_drive")
        subprocess.run([PY, os.path.join(KIT, "docu", "tools", "fetch_drive.py"), _drive_id(a.drive), dl, "12"], check=True)
        n = _flatten(dl, pool)
        pool_note = f"{n} files from Drive"
    cfg = dict(id=nid, name=name, template=tpl["id"], style=tpl.get("style"), topic=a.topic or name,
               pool="pool", drive=a.drive, clip_share=a.clip_share, created=time.strftime("%Y-%m-%d"))
    json.dump(cfg, open(os.path.join(d, "niche.json"), "w", encoding="utf-8"), indent=1)
    md = AGENT_MD.format(name=name, id=nid, template=tpl["id"], style_line=f" (style **{tpl['style']}**)" if tpl.get("style") else "",
                         topic=cfg["topic"], pool_note=pool_note, kit=KIT, template_or_style=tpl.get("style") or tpl["id"])
    for f in ("CLAUDE.md", "AGENTS.md", "GEMINI.md"):
        open(os.path.join(d, f), "w", encoding="utf-8").write(md)
    mk = f'"{PY}" "{os.path.join(KIT, "make_video.py")}" --workspace "{d}"'
    open(os.path.join(d, "make.bat"), "w").write(f"@echo off\r\n{mk} %*\r\n")
    with open(os.path.join(d, "make.sh"), "w") as f:
        f.write(f"#!/bin/sh\nexec {mk} \"$@\"\n")
    os.chmod(os.path.join(d, "make.sh"), 0o755)
    print(f"niche workspace ready: {d}\n  template {tpl['id']}" + (f" / style {tpl['style']}" if tpl.get("style") else "") +
          f" · pool: {pool_note}\n  next: python niche.py qc {nid}   then open the folder in Claude and ask for a video")


def _drive_id(link):
    m = re.search(r"folders/([A-Za-z0-9_-]+)", link) or re.search(r"id=([A-Za-z0-9_-]+)", link)
    return m.group(1) if m else link.strip()


VIDEO_EXT = (".mp4", ".mov", ".mkv", ".webm", ".m4v", ".avi")
IMAGE_EXT = (".jpg", ".jpeg", ".png", ".webp")


def _flatten(src, pool):
    n = 0
    for dd, dirs, files in os.walk(src):
        for f in files:
            ext = os.path.splitext(f)[1].lower()
            sub = "clips" if ext in VIDEO_EXT else "images" if ext in IMAGE_EXT else None
            if not sub:
                continue
            rel = os.path.relpath(dd, src)
            name = f if rel == "." else re.sub(r"[^a-z0-9]+", "_", rel.lower()).strip("_") + "__" + f
            dst = os.path.join(pool, sub, name)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            if not os.path.exists(dst):
                shutil.move(os.path.join(dd, f), dst)
                n += 1
    return n


# folders an old kit's media/ holds that are not footage: contact-sheet frames, staged copies, renders, the asset kit
SKIP_DIRS = {"cat", "picks", "frames", "stills", "segments", "seg", "work", "out", "kit", "qa", "assets", "_qc",
             "final_qc_frames", "runs", "frontier", "sheets_clips", "sheets_img"}


def cmd_add(a):
    """copy every video and picture under a folder (even a whole old media/ folder) into the pool, once each"""
    d = ws_dir(a.name)
    pool = os.path.join(d, "pool")
    seen = set()
    for sub in ("clips", "images"):
        sd = os.path.join(pool, sub)
        os.makedirs(sd, exist_ok=True)
        for f in os.listdir(sd):
            try:
                seen.add((f.lower(), os.path.getsize(os.path.join(sd, f))))
                seen.add(("size", sub, os.path.getsize(os.path.join(sd, f))))
            except OSError:
                pass
    only = [x.lower() for x in (a.only or "").split(",") if x.strip()]
    n = dup = 0
    root = os.path.abspath(a.folder)
    visited = set()
    # follow linked folders too: an old kit linked a video's footage to the pool it came from
    for dd, dirs, files in os.walk(root, followlinks=True):
        real = os.path.realpath(dd)
        if real in visited:
            dirs[:] = []
            continue
        visited.add(real)
        dirs[:] = [x for x in dirs if x.lower() not in SKIP_DIRS and not x.startswith(".")]
        rel = os.path.relpath(dd, root).lower()
        if only and rel != "." and not any(o.strip() in rel for o in only):
            continue
        for f in files:
            ext = os.path.splitext(f)[1].lower()
            sub = "clips" if ext in VIDEO_EXT else "images" if ext in IMAGE_EXT else None
            if not sub or f.startswith(("qc_", "_", ".")):
                continue
            src = os.path.join(dd, f)
            try:
                size = os.path.getsize(src)
            except OSError:
                continue
            if ("size", sub, size) in seen:             # the same file under another name (footage/ and src/ copies)
                dup += 1
                continue
            dst = os.path.join(pool, sub, f)
            if os.path.exists(dst):
                dst = os.path.join(pool, sub, f"{os.path.splitext(f)[0]}_{size % 100000}{ext}")
            shutil.copy2(src, dst)
            seen.add(("size", sub, size))
            n += 1
            if n % 50 == 0:
                print(f"  {n} files...")
    if n == 0 and dup == 0:
        print(f"no videos or pictures found under {root}" + (f" in folders matching {a.only!r}" if only else "") +
              " - check the path, and the --only words against the folder names")
    print(f"{n} files added to {pool} ({dup} duplicates skipped) - now run: python niche.py qc {slug(a.name)}")


def cmd_qc(a):
    d = ws_dir(a.name)
    cfg = json.load(open(os.path.join(d, "niche.json"), encoding="utf-8"))
    cmd = [PY, os.path.join(KIT, "docu", "tools", "qc_pool.py"), os.path.join(d, "pool"), "--topic", cfg.get("topic") or cfg["name"],
           "--workers", str(a.workers)] + (["--strict"] if a.strict else [])
    raise SystemExit(subprocess.call(cmd))


def cmd_list(a):
    if not os.path.isdir(WS_ROOT):
        print("no niche workspaces yet:  python niche.py new <name> --template <id> --pool <folder>")
        return
    for nid in sorted(os.listdir(WS_ROOT)):
        p = os.path.join(WS_ROOT, nid, "niche.json")
        if not os.path.isfile(p):
            continue
        c = json.load(open(p, encoding="utf-8"))
        pool = os.path.join(WS_ROOT, nid, "pool")
        nclip = len(os.listdir(os.path.join(pool, "clips"))) if os.path.isdir(os.path.join(pool, "clips")) else 0
        nimg = len(os.listdir(os.path.join(pool, "images"))) if os.path.isdir(os.path.join(pool, "images")) else 0
        qc = os.path.exists(os.path.join(pool, "qc.json"))
        nproj = len([x for x in os.listdir(os.path.join(WS_ROOT, nid, "projects"))]) if os.path.isdir(os.path.join(WS_ROOT, nid, "projects")) else 0
        print(f"{nid:16s} template {c.get('style') or c['template']:22s} pool {nclip} clips / {nimg} pictures "
              f"{'QC ok' if qc else 'NOT QC-ed'} · {nproj} videos")


def main():
    ap = argparse.ArgumentParser(description="niche workspaces: one kit, many niches, no mixing")
    sub = ap.add_subparsers(dest="cmd", required=True)
    n = sub.add_parser("new"); n.add_argument("name")
    n.add_argument("--template"); n.add_argument("--style"); n.add_argument("--pool", help="your footage folder (clips/ + images/, or any)")
    n.add_argument("--drive", help="a Google Drive folder link, downloaded once into the pool")
    n.add_argument("--topic", help="what the niche is about (QC judges relevance against it)")
    n.add_argument("--clip-share", type=int, default=None)
    sub.add_parser("list")
    q = sub.add_parser("qc"); q.add_argument("name"); q.add_argument("--workers", type=int, default=8); q.add_argument("--strict", action="store_true")
    ad = sub.add_parser("add"); ad.add_argument("name"); ad.add_argument("folder", help="a footage folder, or a whole old media/ folder")
    ad.add_argument("--only", help="comma list: only video folders whose name contains one of these (e.g. hasidic,permission)")
    a = ap.parse_args()
    {"new": cmd_new, "list": cmd_list, "qc": cmd_qc, "add": cmd_add}[a.cmd](a)


if __name__ == "__main__":
    main()
