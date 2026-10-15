"""
build_kit.py - pack everything needed to make videos with any of the templates into one zip.

    python docu/tools/build_kit.py <out_dir>          ->  <out_dir>/DocuTemplates_Kit.zip
    python docu/tools/build_kit.py <out_dir> --clean  ->  a kit for a new PC / another channel: no niches (no projects,
                                                         no niche registry, no niche guides), every template with its
                                                         preview and sample, the asset kit; workspaces start empty

Contents: make_video.py + niche.py + setup/run scripts + docs (kit_docs/), the engine (docu/), the template
registry (templates/ + styles/), the finished example projects (projects/*/build.py + data + metadata), the asset kit
(media/kit: fonts, maps, music, cut-outs, cinema, frames, textures) and api_keys/ (names only, never keys).
"""

import os
import re
import shutil
import sys
import zipfile

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
NAME = "DocuTemplates_Kit"
KIT_PARTS = ["fonts", "maps", "music", "cutouts", "cinema", "kits/frames", "textures", "photofx", "vox", "headlines",
             "frontier", "characters", "cardtext"]
# the moving overlays asset_mix screens over headings / the opening, and the green-screen TV gate for archive shots
KIT_FILES = ["README.txt", "lightleak.mp4", "overlay_dust.mp4", "overlay_vhs.mp4", "VINTAGE OVERLAY green screen.mp4",
             "vhs_lines.png", "icons_fa.json"]
SKIP_DIRS = {"__pycache__", "_gallery_work", "node_modules", "dist", ".git"}
SKIP_FILES = {"keys.env", ".env"}


def add_tree(z, src, arc, keep=lambda p: True):
    for d, dirs, files in os.walk(src):
        dirs[:] = sorted(x for x in dirs if x not in SKIP_DIRS)
        for f in sorted(files):
            p = os.path.join(d, f)
            if f in SKIP_FILES or f.endswith((".pyc", ".log")) or not keep(p):
                continue
            z.write(p, os.path.join(arc, os.path.relpath(p, src)))


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    clean = "--clean" in sys.argv
    name = NAME + ("_Clean" if clean else "")
    out = os.path.abspath(args[0] if args else ".")
    os.makedirs(out, exist_ok=True)
    zp = os.path.join(out, name + ".zip")
    media = os.environ.get("VIDEO_ROOT") or os.path.join(REPO, "media")
    with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        root = name
        z.write(os.path.join(REPO, "make_video.py"), f"{root}/make_video.py")
        z.write(os.path.join(REPO, "niche.py"), f"{root}/niche.py")
        z.writestr(f"{root}/workspaces/README.txt", "One folder per niche: python niche.py new <name> --template <id> --pool <folder> --topic <topic>\n")
        kd = os.path.join(REPO, "kit_docs")           # docs, agent files (AGENTS.md, CLAUDE.md, .claude/, .agent/), scripts
        for d, dirs, files in os.walk(kd):
            for f in sorted(files):
                if clean and f.startswith("NICHE_"):
                    continue                          # a niche guide belongs to that channel
                rel = os.path.relpath(os.path.join(d, f), kd).replace(os.sep, "/")
                info = zipfile.ZipInfo(f"{root}/{rel}")
                info.external_attr = (0o755 if f.endswith(".sh") else 0o644) << 16
                info.compress_type = zipfile.ZIP_DEFLATED
                z.writestr(info, open(os.path.join(d, f), "rb").read())
        # the engine; only the shared niches (not test ones)
        add_tree(z, os.path.join(REPO, "docu"), f"{root}/docu",
                 keep=lambda p: not (os.sep + "niches" + os.sep in p and (clean or os.path.basename(p) not in ("hasidic.json", "noah.json"))))
        if clean:
            z.writestr(f"{root}/docu/studio/niches/README.txt", "Your niches appear here when you add them (python niche.py new ... or Docu Studio).\n")
            z.writestr(f"{root}/projects/README.txt", "Each video gets a folder here (projects/<slug>/build.py + data/).\n")
        if os.path.exists(os.path.join(REPO, "TEMPLATES_GALLERY.html")):
            z.write(os.path.join(REPO, "TEMPLATES_GALLERY.html"), f"{root}/TEMPLATES_GALLERY.html")
        add_tree(z, os.path.join(REPO, "styles"), f"{root}/styles")
        add_tree(z, os.path.join(REPO, "templates"), f"{root}/templates")
        for f in ("README.md", "keys.example.env", ".gitignore"):
            p = os.path.join(REPO, "api_keys", f)
            if os.path.exists(p):
                z.write(p, f"{root}/api_keys/{f}")
        for proj in ([] if clean else sorted(os.listdir(os.path.join(REPO, "projects")))):
            pd = os.path.join(REPO, "projects", proj)
            if proj.startswith(("zz_", "kit_test")) or not os.path.exists(os.path.join(pd, "build.py")):
                continue
            for f in ("build.py", "make_catalog.py", "youtube_metadata.txt"):
                if os.path.exists(os.path.join(pd, f)):
                    z.write(os.path.join(pd, f), f"{root}/projects/{proj}/{f}")
            if os.path.isdir(os.path.join(pd, "data")):
                add_tree(z, os.path.join(pd, "data"), f"{root}/projects/{proj}/data")
        for part in KIT_PARTS:
            p = os.path.join(media, "kit", part)
            if os.path.isdir(p):
                add_tree(z, p, f"{root}/media/kit/{part}")
        for f in KIT_FILES:
            p = os.path.join(media, "kit", f)
            if os.path.exists(p):
                z.write(p, f"{root}/media/kit/{f}")
        z.writestr(f"{root}/media/out/README.txt", "Finished videos land here.\n")
    # never ship a key: refuse the zip if anything looks like one
    bad = []
    with zipfile.ZipFile(zp) as z:
        for n in z.namelist():
            if n.endswith(("keys.env", "/.env")):
                bad.append(n)
        pat = re.compile(rb"(sk-or-v1-[0-9a-f]{20,}|sk-ant-[A-Za-z0-9_-]{20,}|AIza[0-9A-Za-z_-]{30,}|"
                         rb"(?:API_KEY|_TOKEN|SECRET)\s*=\s*['\"]?[A-Za-z0-9_\-]{16,})")
        for n in z.namelist():
            if n.endswith((".py", ".js", ".json", ".md", ".txt", ".env", ".bat", ".sh", ".html")):
                if pat.search(z.read(n)) and not n.endswith("keys.example.env"):
                    bad.append(n + " (looks like a key)")
    if bad:
        os.remove(zp)
        raise SystemExit(f"refused: {bad}")
    print(zp, round(os.path.getsize(zp) / 1e6, 1), "MB")


if __name__ == "__main__":
    main()
