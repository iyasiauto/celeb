"""
Point this at a folder of footage and it writes a ready-to-run topic config.

    python init_project.py --root "D:/Tupac Case" --title "Who Killed Tupac"

It inspects the directory tree, works out which folders are subject buckets,
which hold the generic photo and clip pools, and which hold grid backgrounds,
then writes configs/<slug>.json and prints the exact pipeline command to run.

Nothing is guessed silently: every decision is reported, and anything it is
unsure about is listed so you can correct the config before rendering.
"""

import os
import re
import sys
import json
import glob
import argparse
from collections import Counter

from semantic_matcher import IMAGE_EXTS, VIDEO_EXTS, folder_entity, tokenize

# Folders that never hold subject footage - working directories, caches and
# render output rather than source material.
IGNORE = {"__pycache__", "temp_render_workspace", "segments", "voice_chunks",
          "image_cache", "webp_cache", "generated_graphics", "node_modules",
          "configs", "index_audit", ".git", "test_segments", "extracted_frames",
          "frames_step", "output", "outputs", "renders", "build", "dist"}

# Names that read as benchmark or experiment output, not footage.
NOT_FOOTAGE_RE = re.compile(
    r"(^[a-z]\._)|(\bnvenc\b)|(\bworkers?\b)|(\bbenchmark)|(\bbaseline\b)"
    r"|(\bvbr\b)|(\btest_)|(_test\b)", re.I)

GRID_HINTS = ("grid", "background", "backdrop", "pattern", "texture")
MUSIC_HINTS = ("music", "bgm", "audio", "soundtrack", "score")
GENERIC_HINTS = ("all", "misc", "general", "real images", "raw", "pool",
                 "images data", "stock")

AUDIO_EXTS = (".mp3", ".wav", ".m4a", ".aac", ".flac", ".ogg")


def slugify(text):
    s = re.sub(r"[^a-z0-9]+", "_", str(text).lower()).strip("_")
    return s or "project"


def scan(root, exclude=()):
    """Return one record per directory that holds usable media."""
    exclude = [e.lower() for e in exclude]
    records = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames
                       if d not in IGNORE and not d.startswith(".")
                       and not any(e in d.lower() for e in exclude)]
        if any(e in dirpath.lower() for e in exclude):
            continue
        images = [f for f in filenames if f.lower().endswith(IMAGE_EXTS)]
        clips = [f for f in filenames if f.lower().endswith(VIDEO_EXTS)]
        audio = [f for f in filenames if f.lower().endswith(AUDIO_EXTS)]
        if not (images or clips or audio):
            continue
        records.append({
            "path": dirpath,
            "name": os.path.basename(dirpath) or dirpath,
            "depth": os.path.relpath(dirpath, root).count(os.sep),
            "images": images,
            "clips": clips,
            "audio": audio,
        })
    return records


def classify(records, root):
    """Sort media folders into grids, music, generic pools and subject buckets."""
    grids, music, generic, subjects, rejected = [], [], [], [], []
    for r in records:
        low = r["name"].lower()
        if r["audio"] and not r["images"] and not r["clips"]:
            music.append(r)
        elif NOT_FOOTAGE_RE.search(r["name"]):
            rejected.append(r)
        elif any(h in low for h in GRID_HINTS):
            grids.append(r)
        elif any(h in low for h in GENERIC_HINTS):
            generic.append(r)
        elif os.path.normcase(r["path"]) == os.path.normcase(root):
            generic.append(r)
        else:
            subjects.append(r)
    return grids, music, generic, subjects, rejected


def describable_fraction(records):
    """Share of files whose names carry words beyond the folder's own name."""
    total = useful = 0
    for r in records:
        folder_words = set(tokenize(r["name"]))
        for f in r["images"] + r["clips"]:
            total += 1
            stem = os.path.splitext(f)[0]
            if set(tokenize(stem)) - folder_words:
                useful += 1
    return useful, total


def main():
    p = argparse.ArgumentParser(
        description="Inspect a footage folder and write a runnable topic config")
    p.add_argument("--root", required=True, help="Folder containing the footage")
    p.add_argument("--title", required=True, help="Documentary title")
    p.add_argument("--script", default=None, help="Path to the script text file")
    p.add_argument("--out", default=None, help="Config path (default configs/<slug>.json)")
    p.add_argument("--default-entity", default=None,
                   help="Main subject, only if it has NO folder of its own")
    p.add_argument("--min-subject-files", type=int, default=3,
                   help="Folders with fewer files than this are treated as generic")
    p.add_argument("--exclude", action="append", default=[],
                   help="Skip any folder whose path contains this text (repeatable)")
    args = p.parse_args()

    root = os.path.abspath(args.root)
    if not os.path.isdir(root):
        sys.exit(f"ERROR: not a directory: {root}")

    records = scan(root, args.exclude)
    if not records:
        sys.exit(f"ERROR: no images, clips or audio found under {root}")

    grids, music, generic, subjects, rejected = classify(records, root)

    small = [r for r in subjects
             if len(r["images"]) + len(r["clips"]) < args.min_subject_files]
    subjects = [r for r in subjects if r not in small]
    generic.extend(small)

    entities = {}
    for r in subjects:
        ent = folder_entity(r["path"])
        if ent:
            entities.setdefault(ent, []).append(r)

    total_images = sum(len(r["images"]) for r in records)
    total_clips = sum(len(r["clips"]) for r in records)

    print("=" * 68)
    print(f"SCANNED: {root}")
    print("=" * 68)
    print(f"Media folders found : {len(records)}")
    print(f"Images              : {total_images}")
    print(f"Clips               : {total_clips}")
    print()
    print(f"Subject folders     : {len(subjects)}  -> become searchable entities")
    for r in sorted(subjects, key=lambda x: -(len(x['images']) + len(x['clips'])))[:12]:
        ent = folder_entity(r["path"])
        print(f"    {len(r['images']):4d} img {len(r['clips']):4d} clip  "
              f"{r['name'][:36]:36s} -> {ent!r}")
    if len(subjects) > 12:
        print(f"    ... and {len(subjects) - 12} more")

    print()
    print(f"Generic pools       : {len(generic)}")
    for r in generic:
        print(f"    {len(r['images']):4d} img {len(r['clips']):4d} clip  {r['name'][:44]}")
    print(f"Grid backgrounds    : {len(grids)}")
    print(f"Music folders       : {len(music)}")
    if rejected:
        print(f"Skipped as build output : {len(rejected)}")
        for r in rejected[:6]:
            print(f"    {r['name'][:52]}")
        if len(rejected) > 6:
            print(f"    ... and {len(rejected) - 6} more")
        print("    (use --exclude if any of these are actually footage)")

    useful, counted = describable_fraction(subjects + generic)
    if counted:
        print()
        print(f"Filenames adding detail beyond the folder name: "
              f"{useful}/{counted} ({100 * useful / counted:.0f}%)")
        if useful / counted < 0.25:
            print("  -> Filenames are mostly uninformative. Folder names will do")
            print("     the work; run make_asset_tags.py if you want finer control.")

    # ---------------------------------------------------------------- config
    image_dirs = [r["path"] for r in generic if r["images"]]
    clip_dirs = [r["path"] for r in generic if r["clips"]]
    if not image_dirs:
        image_dirs = [r["path"] for r in subjects if r["images"]]
    if not clip_dirs:
        clip_dirs = [r["path"] for r in subjects if r["clips"]]

    bgm = None
    for r in music:
        if r["audio"]:
            bgm = os.path.join(r["path"], sorted(r["audio"])[0])
            break

    cfg = {
        "_generated_by": "init_project.py",
        "_root": root,
        "images_dir": os.pathsep.join(dict.fromkeys(image_dirs)) or root,
        "clips_dir": os.pathsep.join(dict.fromkeys(clip_dirs)) or root,
        "grid_dir": os.pathsep.join(r["path"] for r in grids),
        "entity_root": root,
        "generic_dirs": [r["path"] for r in generic],
        "entity_root_skip": sorted({r["name"] for r in grids + music + rejected}
                                   | {r["name"] for r in generic
                                      if os.path.normcase(r["path"]) != os.path.normcase(root)}),
        "tags": [args.title],
        "hashtags": ["#Documentary"],
        "chapter_titles": ["Introduction", "Background", "The Turning Point",
                           "The Reckoning", "Aftermath", "Legacy"],
    }
    if args.default_entity:
        cfg["default_entity"] = args.default_entity.lower()
    if bgm:
        cfg["bgm"] = bgm

    out = args.out or os.path.join("configs", slugify(args.title) + ".json")
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)

    print()
    print("=" * 68)
    print(f"WROTE CONFIG: {out}")
    print("=" * 68)

    warnings = []
    if not grids:
        warnings.append("No grid-background folder found. Grid graphic cards "
                        "will be skipped (other card styles still work).")
    if not bgm:
        warnings.append("No music folder found. Pass --bgm explicitly, or the "
                        "render runs with narration only.")
    if not clip_dirs:
        warnings.append("No generic clip pool found. Every clip slot will be "
                        "filled from subject folders only.")
    if args.default_entity:
        de = set(tokenize(args.default_entity))
        for r in subjects:
            ent = folder_entity(r["path"])
            et = set(tokenize(ent))
            if not et:
                continue
            if et == de:
                warnings.append(
                    f"--default-entity {args.default_entity!r} also exists as its "
                    f"own folder ({r['name']!r}). Drop the flag so that folder can "
                    "be preferred when the subject is named.")
            elif et < de:
                warnings.append(
                    f"Folder {r['name']!r} resolves to {ent!r}, a partial form of "
                    f"--default-entity {args.default_entity!r}. Add an explicit "
                    f'"entity_dirs" mapping so they are not treated as two '
                    "different subjects.")
    if warnings:
        print("REVIEW BEFORE RENDERING:")
        for w in warnings:
            print(f"  - {w}")
        print()

    script = args.script or "path/to/script.txt"
    print("Next, run a fast timeline-only check:")
    print()
    print(f'  python pipeline.py --title "{args.title}" --script "{script}" \\')
    print(f'      --topic-config "{out}" --output-dir "output" --skip-render')
    print()
    print("Then render for real by dropping --skip-render.")


if __name__ == "__main__":
    main()
