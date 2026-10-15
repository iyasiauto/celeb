"""gemini_images.py - Docu's bridge to Frontier's Gemini browser tool (gemini_image/), so templates that are drawn
pictures (2D Stories, Carl Jung) get them the way Frontier does. Copied from Frontier's gemini_browser.py; only where
the tool lives changed - Docu looks, in order, at $GEMINI_IMAGE_DIR, <kit>/gemini_image and <Frontier folder>/gemini_image
(Docu Studio's Frontier folder: $FRONTIER_DIR, media/frontier, or a Frontier folder next to the kit).

Frontier's original note: bridge from Frontier's image-gen API to the Gemini browser tool copied under
`gemini_image/`. The tool runs Chromium against gemini.google.com with 4
pre-logged-in Google profiles, so images are drawn through the web app instead
of a paid API.

Batch is the intended shape — the Node runner opens ONE Chromium session, pastes
every prompt into Gemini, waits for the whole set, then downloads them together.
It also auto-switches profiles when one hits its daily limit.

    from gemini_browser import batch_image_gen
    batch_image_gen(prompts, dests, slug=job.name)

The single-image `image_gen()` still works (for one-off calls / thumbnails) but is
slow — every call spins up its own browser.

Output naming from the Node tool: `<outDir>/ai_<slug>_S<N>_v1.<ext>`, where N is
1-based scene id (`S1`, `S2`, …). This module maps N → dests[N-1].

Requires: Node.js on PATH, `npm install` already run in `gemini_image/` (the
copy from `D:/New Hasidic/gemini_image/` already ships with `node_modules/`).
"""

import os
import re
import shutil
import subprocess
import threading
import time
from pathlib import Path
from typing import Iterable

def _find_root() -> Path:
    here = Path(__file__).resolve().parent
    cands = [os.environ.get("GEMINI_IMAGE_DIR", ""), str(here.parent / "gemini_image")]
    fr = os.environ.get("FRONTIER_DIR", "")
    try:                                                   # the Frontier folder Docu Studio finds (Settings, media/frontier ...)
        import sys as _sys
        _sys.path.insert(0, str(here / "studio"))
        import frontier as _fr
        fr = fr or _fr.find_dir(str(here.parent)) or ""
    except Exception:                                      # noqa: BLE001
        pass
    if fr:
        cands.append(str(Path(fr) / "gemini_image"))
    for c in cands:
        if c and (Path(c) / "run_gemini_images.js").exists():
            return Path(c)
    return Path(cands[0] or cands[1])


ROOT = _find_root()
RUNNER = ROOT / "run_gemini_images.js"

# One Chromium/profile session at a time — parallel launches fight over the same
# Google profiles and lock files. Callers (vox, thumbnails) may run in threads.
_SESSION_LOCK = threading.Lock()


class GeminiBrowserError(RuntimeError):
    pass


def _node_exe() -> str:
    exe = shutil.which("node")
    if not exe:
        raise GeminiBrowserError(
            "node.js not found on PATH — install from nodejs.org, then reopen the terminal.")
    return exe


def _check_setup() -> None:
    if not ROOT.exists():
        raise GeminiBrowserError(f"gemini_image/ folder not found at {ROOT} - copy Frontier's gemini_image folder into the "
                                 f"kit root, or set GEMINI_IMAGE_DIR / Docu Studio Settings -> Frontier folder")
    if not RUNNER.exists():
        raise GeminiBrowserError(f"missing runner: {RUNNER}")
    if not (ROOT / "node_modules").exists():
        raise GeminiBrowserError(
            f"gemini_image/node_modules missing — cd into {ROOT} and run `npm install` once.")


def _clean_prompt(text: str) -> str:
    """One image = one line, so newlines have to go."""
    return " ".join((text or "").split())


def _safe_slug(s: str) -> str:
    s = re.sub(r"\s+", "", s or "batch")
    return re.sub(r"[^\w.-]", "_", s) or "batch"


def _run(slug: str, input_file: Path, out_dir: Path, timeout_s: int, log=None) -> None:
    """Invoke the Node runner. Slug is the video/session tag Frontier passes in."""
    _check_setup()
    cmd = [_node_exe(), str(RUNNER), str(input_file), str(out_dir), "--slug", slug]
    if log:
        log(f"  gemini browser: {len(open(input_file, encoding='utf-8').readlines())} "
            f"prompt(s) -> {out_dir}")
    # Serialize: only one browser session at a time (parallel callers would clash on profiles).
    with _SESSION_LOCK:
        try:
            r = subprocess.run(cmd, capture_output=True, text=True,
                               timeout=timeout_s, cwd=str(ROOT),
                               encoding="utf-8", errors="replace")
        except subprocess.TimeoutExpired:
            raise GeminiBrowserError(f"gemini browser timed out after {timeout_s}s")
    tail_out = (r.stdout or "")[-800:]
    if log and tail_out.strip():
        for line in tail_out.strip().splitlines()[-6:]:
            log(f"    {line}")
    if r.returncode != 0:
        tail = (r.stderr or r.stdout or "")[-800:]
        raise GeminiBrowserError(f"gemini browser exited {r.returncode}: {tail}")


def _pickup(out_dir: Path, slug: str) -> dict:
    """Return {scene_number: source_file_path} for every `ai_<slug>_S<N>_v1.*` in out_dir."""
    if not out_dir.exists():
        return {}
    pat = re.compile(rf"^ai_{re.escape(slug)}_S(\d+)_v\d+\.(?:png|jpe?g|webp)$", re.IGNORECASE)
    out = {}
    for f in out_dir.iterdir():
        if not f.is_file():
            continue
        m = pat.match(f.name)
        if not m:
            continue
        n = int(m.group(1))
        # Keep the newer file if two versions match (v1 vs v2 etc.)
        if n not in out or f.stat().st_mtime > out[n].stat().st_mtime:
            out[n] = f
    return out


def batch_image_gen(prompts: Iterable[str], dests: Iterable[Path],
                    slug: str = "batch", timeout_s: int = 3600, log=None) -> list:
    """Draw many prompts in ONE browser session. `prompts` and `dests` line up 1:1.

    Returns the list of dests that actually received a file (missing ones are
    skipped — Frontier upstream handles a partial pool). If ANY image lands,
    the call is considered a success; profile switching happens inside the tool."""
    prompts = list(prompts)
    dests = [Path(d) for d in dests]
    if len(prompts) != len(dests):
        raise ValueError("prompts and dests must be the same length")
    if not prompts:
        return []
    for d in dests:
        d.parent.mkdir(parents=True, exist_ok=True)

    _check_setup()                       # a clear message before anything is written into the tool's folder
    slug = _safe_slug(slug)
    prompts_root = ROOT
    input_file = prompts_root / f"_frontier_{slug}.txt"
    # Write as CSV (the runner then honours scene_id order). The .tsv path is easier
    # because there is no need to escape commas inside a prompt.
    input_file = input_file.with_suffix(".tsv")
    lines = ["scene_id\tprompt"]
    for i, p in enumerate(prompts, 1):
        lines.append(f"S{i}\t{_clean_prompt(p)}")
    input_file.write_text("\n".join(lines) + "\n", encoding="utf-8")

    # The tool copies its produced files to <out_dir>/ai_<slug>_S<N>_v1.<ext>.
    # Use a scratch dir under the first destination's parent so cleanup is local.
    out_dir = dests[0].parent / f"_gemini_{slug}"
    out_dir.mkdir(parents=True, exist_ok=True)

    if log:
        log(f"gemini browser: batch of {len(prompts)} image(s) — one session, profile-rotation on failure")
    try:
        _run(slug, input_file, out_dir, timeout_s, log=log)
    finally:
        try:
            input_file.unlink()
        except OSError:
            pass

    picked = _pickup(out_dir, slug)
    landed = []
    for i, dst in enumerate(dests, 1):
        src = picked.get(i)
        if not src:
            if log:
                log(f"  ⚠ gemini: no image for scene S{i}")
            continue
        try:
            if dst.exists():
                dst.unlink()
            shutil.move(str(src), str(dst))
            landed.append(dst)
        except OSError as e:
            if log:
                log(f"  ⚠ gemini: could not save scene S{i}: {e}")

    # tidy scratch dir when everything has moved out
    try:
        for leftover in list(out_dir.iterdir()):
            leftover.unlink(missing_ok=True)
        out_dir.rmdir()
    except OSError:
        pass

    if not landed:
        raise GeminiBrowserError(
            f"gemini browser: none of {len(dests)} images were produced (check the log above)")
    return landed


def image_gen(prompt: str, dest: Path, label: str = "image", timeout_s: int = 600) -> None:
    """One-off convenience wrapper — batches a single prompt. Slow (browser boot per call);
    prefer `batch_image_gen` when you can group calls."""
    dest = Path(dest)
    slug = _safe_slug(dest.stem or f"img_{int(time.time())}")
    batch_image_gen([prompt], [dest], slug=slug, timeout_s=timeout_s)
