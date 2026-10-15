"""
new_project.py - start a new video from a template, with its data ready for `build.py plan`.

    python new_project.py <projects_root>/<slug> --title "What Happens If ..." \
        --script script.txt --vo voiceover.mp3 [--srt voiceover.srt] \
        [--template starter_documentary] [--catalog <project or cat dir to copy data from>] \
        [--work <work dir>]

What it does
  1. copies docu/templates/<template>/build.py into the project and fills in the title, the file
     name and vary="auto" (a fresh look per video - see docu/variety.py)
  2. data/script.txt   <- --script
  3. data/words.json   <- from --srt (tools/srt2words.py, instant) or else Whisper (tools/transcribe.py)
  4. <work>/vo.mp3     <- --vo (the voiceover the video is cut to)
  5. data/catalog_all.json, image_picks.json, notes_*.txt <- --catalog (same footage as an earlier video)
  6. prints a paragraph map (start time of each paragraph) to plan chapters from

Then write the scenes in build.py and run: python build.py plan | prep | stills | render | mix | final
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DOCU = os.path.dirname(HERE)
sys.path.insert(0, DOCU)


def slug_name(title):
    return re.sub(r"_+", "_", re.sub(r"[^A-Za-z0-9]+", "_", title)).strip("_")[:80]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("project")
    ap.add_argument("--title", required=True)
    ap.add_argument("--script", required=True)
    ap.add_argument("--vo", required=True)
    ap.add_argument("--srt")
    ap.add_argument("--template", default="starter_documentary")
    ap.add_argument("--catalog")
    ap.add_argument("--work")
    x = ap.parse_args()

    proj = os.path.abspath(x.project)
    data = os.path.join(proj, "data")
    os.makedirs(data, exist_ok=True)
    work = os.path.abspath(x.work or os.path.join(proj, "media", "work"))
    os.makedirs(work, exist_ok=True)

    # 1. build.py from the template
    src = os.path.join(DOCU, "templates", x.template, "build.py")
    dst = os.path.join(proj, "build.py")
    if os.path.exists(dst):
        print("build.py exists - left as it is")
    else:
        s = open(src, encoding="utf-8").read()
        s = s.replace("<VIDEO TITLE>", x.title)
        s = re.sub(r'name="[^"]*"', f'name="{slug_name(x.title)}"', s, count=1)
        if "vary=" not in s:
            s = s.replace('sfx_style="calm",', 'sfx_style="calm",\n    vary="auto",           # shuffled look per video (docu/variety.py)', 1)
        s = s.replace('f"{ROOT}/work"', f'"{work}"', 1) if x.work else s
        open(dst, "w", encoding="utf-8").write(s)

    # 2-4. script, words, voiceover
    shutil.copy(x.script, os.path.join(data, "script.txt"))
    shutil.copy(x.vo, os.path.join(work, "vo.mp3"))
    words = os.path.join(data, "words.json")
    if x.srt:
        shutil.copy(x.srt, os.path.join(data, "voiceover.srt"))
        subprocess.run([sys.executable, os.path.join(HERE, "srt2words.py"), x.srt, words], check=True)
    else:
        subprocess.run([sys.executable, os.path.join(HERE, "transcribe.py"), x.vo, words], check=True)

    # 5. catalog from an earlier project (same footage)
    if x.catalog:
        c = x.catalog if os.path.isfile(os.path.join(x.catalog, "catalog_all.json")) else os.path.join(x.catalog, "data")
        for f in ("catalog_all.json", "image_picks.json", "notes_clips.txt", "notes_img.txt"):
            if os.path.exists(os.path.join(c, f)):
                shutil.copy(os.path.join(c, f), os.path.join(data, f))
    if not os.path.exists(os.path.join(data, "catalog_all.json")):
        json.dump([], open(os.path.join(data, "catalog_all.json"), "w"))
        print("no clip catalog yet - see tools/catalog_clips.py (an empty one was written)")

    # 6. paragraph map
    from timing import Timing
    T = Timing.load(os.path.join(data, "script.txt"), words)
    print(f"alignment {T.matched:.0%}")
    paras = [p.strip() for p in open(os.path.join(data, "script.txt"), encoding="utf-8").read().split("\n") if p.strip()]
    for p in paras:
        first = " ".join(p.split()[:6])
        try:
            t = T.at(first)
            print(f"  {t:7.1f}s  {first} ...")
        except Exception:
            print(f"     ?     {first} ...")
    print("project ready:", proj)


if __name__ == "__main__":
    main()
