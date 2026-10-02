"""
build_kit.py - pack everything needed to make videos with any of the templates into one zip.

    python docu/tools/build_kit.py <out_dir>          ->  <out_dir>/DocuTemplates_Kit.zip

Contents: make_video.py + setup/run scripts + docs (kit_docs/), the engine (docu/), the template folder
(styles/), the finished example projects (projects/*/build.py + data + metadata), the asset kit
(media/kit: fonts, maps, music, cut-outs, cinema, frames, textures) and api_keys/ (names only, never keys).
"""

import os
import shutil
import sys
import zipfile

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
NAME = "DocuTemplates_Kit"
KIT_PARTS = ["fonts", "maps", "music", "cutouts", "cinema", "kits/frames", "textures"]
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
    out = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else ".")
    os.makedirs(out, exist_ok=True)
    zp = os.path.join(out, NAME + ".zip")
    media = os.environ.get("VIDEO_ROOT") or os.path.join(REPO, "media")
    with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        root = NAME
        z.write(os.path.join(REPO, "make_video.py"), f"{root}/make_video.py")
        for f in sorted(os.listdir(os.path.join(REPO, "kit_docs"))):
            info = zipfile.ZipInfo(f"{root}/{f}")
            info.external_attr = (0o755 if f.endswith(".sh") else 0o644) << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, open(os.path.join(REPO, "kit_docs", f), "rb").read())
        # the engine; only the shared niches (not test ones)
        add_tree(z, os.path.join(REPO, "docu"), f"{root}/docu",
                 keep=lambda p: not (os.sep + "niches" + os.sep in p and os.path.basename(p) not in ("hasidic.json", "noah.json")))
        add_tree(z, os.path.join(REPO, "styles"), f"{root}/styles")
        for f in ("README.md", "keys.example.env", ".gitignore"):
            p = os.path.join(REPO, "api_keys", f)
            if os.path.exists(p):
                z.write(p, f"{root}/api_keys/{f}")
        for proj in sorted(os.listdir(os.path.join(REPO, "projects"))):
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
        for f in ("README.txt",):
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
    if bad:
        os.remove(zp)
        raise SystemExit(f"refused: {bad}")
    print(zp, round(os.path.getsize(zp) / 1e6, 1), "MB")


if __name__ == "__main__":
    main()
