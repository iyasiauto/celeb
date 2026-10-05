"""qc_guard.py — mandatory QC gate for the DocuTemplates render pipeline.

Policy (every template, every video, no exceptions):
  * A clip in a project's catalog can only reach `scenes.json` if it passed the vision QC
    pass (`docu/tools/qc_pool.py`, strict prompt). Rejected clips never render.
  * A pool used by a project MUST have `qc.json` covering every file in
    `footage/source_video/`. Otherwise the plan step aborts with a clear "run qc_pool.py"
    message. No video ships without QC.
  * Clips flagged with a logo in a specific CORNER by QC can still be used — the render
    auto-crops that corner (handled in `render.render_clip_scene` via the `crop` field).
    Clips flagged with a CENTER talking head are hard-rejected and are not usable at all.

Public API (used by `edl.main` and project shotlists):

    enforce(pool_dir, catalog_path)
        Called from edl.setup. Raises SystemExit if the pool has unQC'd files.

    is_usable(video_name, qc)
        Returns True if the clip passed QC (used by V() in shotlists). Rejected = False.

    recommended_crop(video_name, qc)
        Returns a (x0, y0, x1, y1) tuple if the QC flagged a corner logo for this clip,
        else None. Render applies this automatically.
"""
import json
import os
import sys

CORNER_CROP = {
    # aspect-keeping crops: the corner (or edge) with the logo falls outside the frame, 16:9 is kept
    "top-left":     (0.14, 0.14, 1.00, 1.00),
    "top-right":    (0.00, 0.14, 0.86, 1.00),
    "bottom-left":  (0.14, 0.00, 1.00, 0.86),
    "bottom-right": (0.00, 0.00, 0.86, 0.86),
    "top":          (0.07, 0.14, 0.93, 1.00),
    "bottom":       (0.07, 0.00, 0.93, 0.86),
    "left":         (0.14, 0.07, 1.00, 0.93),
    "right":        (0.00, 0.07, 0.86, 0.93),
    "any":          (0.07, 0.07, 0.93, 0.93),   # general all-around safe crop
}


def find_qc(*dirs):
    """qc.json for a folder of media: in it, next to it, or next to the folder it links to"""
    for d in dirs:
        if not d:
            continue
        for base in (d, os.path.dirname(d), os.path.realpath(d), os.path.dirname(os.path.realpath(d))):
            p = os.path.join(base, "qc.json")
            if os.path.exists(p):
                return p
    return os.path.join(dirs[0], "qc.json")


def _load(path):
    if not os.path.exists(path):
        return {}
    try:
        return json.load(open(path, encoding="utf-8"))
    except Exception:
        return {}


def _qc_lookup(video_name, qc):
    """Look up a clip by basename, regardless of whether qc.json keys include a subdir prefix."""
    bn = os.path.basename(video_name)
    if bn in qc:
        return qc[bn]
    # qc_pool.py keys files relative to the pool, e.g. "source_video/clips__xxx.mp4"
    for k, v in qc.items():
        if os.path.basename(k) == bn:
            return v
    return None


def is_usable(video_name, qc):
    """True iff this clip has a QC entry that is not a hard reject.
    A clip with no QC entry is NOT usable — the plan should have failed first."""
    r = _qc_lookup(video_name, qc)
    if r is None:
        return False
    if r.get("reject"):
        return False
    return True


def recommended_crop(video_name, qc):
    """If QC flagged a corner logo for this clip, return a crop tuple to hide it."""
    r = _qc_lookup(video_name, qc) or {}
    if isinstance(r.get("crop"), list) and len(r["crop"]) == 4:
        return list(r["crop"])            # qc_pool.py measured the logo: crop exactly past it
    corner = (r.get("logo_corner") or r.get("corner") or "").lower().strip()
    if corner in CORNER_CROP:
        return list(CORNER_CROP[corner])
    return None


def enforce(pool_dir, catalog_path=None, project_name=None):
    """Mandatory gate called from edl.setup. Aborts the pipeline if QC is missing or stale.

    pool_dir: the clip pool (e.g. media/<slug>/footage).
    catalog_path: the project's catalog_all.json (optional, used to narrow the check).
    project_name: shown in the error message.
    """
    bypass = os.environ.get("DOCU_SKIP_QC", "").lower() in ("1", "true", "yes")
    source_dir = os.path.join(pool_dir, "source_video")
    qc_path = find_qc(pool_dir, source_dir)
    qc = _load(qc_path)
    if not os.path.isdir(source_dir):
        return qc

    pool_files = {f for f in os.listdir(source_dir)
                  if f.lower().endswith((".mp4", ".mov", ".mkv", ".webm"))}

    # If a catalog is passed, we only need QC for clips actually referenced there.
    if catalog_path and os.path.exists(catalog_path):
        try:
            cat = json.load(open(catalog_path, encoding="utf-8"))
            needed = {e["video"] for e in cat if isinstance(e, dict) and e.get("video")}
            pool_files = pool_files & needed
        except Exception:
            pass

    # qc.json may key files relative to the pool (e.g. "source_video/x.mp4"); fold to basenames.
    qc_bn = {os.path.basename(k): v for k, v in qc.items()}
    missing = sorted(pool_files - set(qc_bn.keys()))
    rejects = sorted(f for f in pool_files if (qc_bn.get(f) or {}).get("reject"))

    print(f"[qc_guard] pool={os.path.basename(pool_dir)}  files={len(pool_files)}  "
          f"QC'd={len(pool_files) - len(missing)}  rejected={len(rejects)}  missing={len(missing)}")

    if missing and not bypass:
        topic = project_name or os.path.basename(pool_dir)
        sys.stderr.write(
            "\n*** QC GATE: this pool has clips that were never checked by Gemini. ***\n"
            f"    pool:    {pool_dir}\n"
            f"    missing: {len(missing)} clips (e.g. {missing[:3]})\n\n"
            "Run strict vision QC before rendering (reject talking heads, logos, chyrons):\n"
            f'  python docu/tools/qc_pool.py "{pool_dir}" '
            f'--topic "{topic}" --only clips --workers 10\n\n'
            "To bypass this gate (NOT recommended, user has forbidden it), set DOCU_SKIP_QC=1.\n\n"
        )
        raise SystemExit(2)

    if bypass and missing:
        print(f"[qc_guard] WARNING: bypassed with DOCU_SKIP_QC=1 — {len(missing)} clips unchecked")

    return qc


def filter_catalog(catalog, qc):
    """Drop rejected entries from an edl catalog list in place; mark corner-crops on survivors.

    Returns (kept, removed) counts.
    """
    kept, removed = 0, 0
    for e in catalog[:]:
        name = e.get("video")
        if not name:
            continue
        if not is_usable(name, qc):
            catalog.remove(e)
            removed += 1
            continue
        crop = recommended_crop(name, qc)
        if crop:
            e["_crop"] = crop   # consumed by edl.cl() when building a clip scene
        kept += 1
    return kept, removed


_IMG_QC = {}


def _origin_of(path):
    """a staged pick (picks/named_00_3.jpg) is a symlink, hard link or copy of a pool picture: QC knows the original"""
    if os.path.islink(path):
        return os.path.realpath(path)
    d = os.path.dirname(os.path.abspath(path))
    try:
        orig = json.load(open(os.path.join(d, "_origin.json"), encoding="utf-8")).get(os.path.basename(path))
    except Exception:
        orig = None
    if orig:
        for base in (os.path.join(os.path.dirname(d), "src", "images"), os.path.join(os.path.dirname(d), "images"), d):
            if os.path.exists(os.path.join(base, orig)):
                return os.path.join(base, orig)
        return os.path.join(d, orig)          # the QC lookup is by name; the name is what matters
    return path


def check_image(path):
    """Pictures pass the same gate as clips. Returns None when usable; raises SystemExit with the reason when
    QC rejected the picture or never saw it (DOCU_SKIP_QC=1 bypasses, which the user has forbidden)."""
    if os.environ.get("DOCU_SKIP_QC", "").lower() in ("1", "true", "yes"):
        return None
    path = _origin_of(path)
    d = os.path.dirname(os.path.abspath(path))
    if d not in _IMG_QC:
        _IMG_QC[d] = _load(find_qc(d))
    qc = _IMG_QC[d]
    r = _qc_lookup(path, qc)
    name = os.path.basename(path)
    if r is None:
        if not qc:
            sys.stderr.write(
                f"\n*** QC GATE: the pictures in {d} were never checked. ***\n"
                f'  python docu/tools/qc_pool.py "{os.path.dirname(d)}" --topic "<topic>" --only images\n\n')
        else:
            sys.stderr.write(f"\n*** QC GATE: {name} is not in qc.json (added after the last QC run).\n"
                             f'  python docu/tools/qc_pool.py "{os.path.dirname(d)}" --topic "<topic>" --only images\n\n')
        raise SystemExit(2)
    if r.get("reject"):
        sys.stderr.write(f"\n*** QC GATE: {name} was rejected by QC ({r.get('reason')}). Pick another picture.\n\n")
        raise SystemExit(2)
    return None
