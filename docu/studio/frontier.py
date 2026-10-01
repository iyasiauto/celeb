"""
frontier.py - use the Frontier app's channel styles from Docu Studio.

Frontier (a separate faceless-video studio, folder "Frontier" in the Drive) has its own engine, its own
channel styles (styles/*.json, one sample video each in samples/) and its own API keys (.env: Algrow,
Gemini, WaveSpeed, ...). Docu Studio does not copy that engine. It:

  * lists Frontier's styles (re-read from disk every time, so a style file you add appears at once),
    with each style's preview picture and sample video;
  * runs a video in a Frontier style through Frontier's own local API (python app.py):
        POST /api/run {title, style, script, byo_audio, steps}  ->  GET /api/status/<slug>  ->  /f/video/<slug>
    with your script and, if you made one, your FameSpeak voiceover as Frontier's "bring your own audio";
  * then delivers the result like any other video (size check, gofile, metadata).

The Frontier folder: Settings -> Frontier folder, or `studio.py frontier-fetch` downloads the parts needed
(code, styles, samples, kits) from the Drive - never its .env, which holds the keys of whoever made it.
"""

import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request

DRIVE = "1wC9Vu4B7GeR_hE6SA78sNXE5o5A5zmde"
PORT = int(os.environ.get("FRONTIER_PORT") or 7871)


def find_dir(w):
    """the Frontier folder: $FRONTIER_DIR, media/frontier, or a 'Frontier' folder next to the workspace"""
    cands = [os.environ.get("FRONTIER_DIR"), os.path.join(w, "media", "frontier"), os.path.join(w, "Frontier"),
             os.path.join(os.path.dirname(w), "Frontier")]
    for c in cands:
        if c and os.path.isfile(os.path.join(c, "make_video.py")) and os.path.isdir(os.path.join(c, "styles")):
            return os.path.abspath(c)
    for c in cands:                       # styles-only download (no engine yet) still shows the catalogue
        if c and os.path.isdir(os.path.join(c, "styles")):
            return os.path.abspath(c)
    return None


def styles(fdir):
    """Frontier channel styles as Docu Studio style cards"""
    out = []
    if not fdir:
        return out
    sd = os.path.join(fdir, "styles")
    files = sorted(f for f in os.listdir(sd) if f.endswith(".json") and not f.startswith("_"))
    for f in files:
        try:
            d = json.load(open(os.path.join(sd, f), encoding="utf-8"))
        except Exception:
            continue
        name = d.get("name") or f[:-5]
        prev = None
        for p in (os.path.join(fdir, "assets", "styles", name + ".jpg"), os.path.join(fdir, "assets", "styles", name + ".png")):
            if os.path.exists(p):
                prev = p
        sample = os.path.join(fdir, "samples", name + ".mp4")
        if not prev and os.path.exists(sample):
            prev = _thumb(sample, os.path.join(fdir, "assets", "styles", "_thumbs", name + ".jpg"))
        points = d.get("points") or []
        out.append(dict(id="frontier:" + name, engine="frontier", name=d.get("label") or name.title(),
                        letter="F", blurb=d.get("tagline") or d.get("description") or "", points=points,
                        description=d.get("description", ""), preview_path=prev,
                        sample_path=sample if os.path.exists(sample) else None,
                        runnable=os.path.isfile(os.path.join(fdir, "make_video.py"))))
    return out


def _thumb(video, out, at=6.0):
    """a preview picture from a sample video (made once)"""
    if not os.path.exists(out):
        os.makedirs(os.path.dirname(out), exist_ok=True)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(at), "-i", video, "-frames:v", "1", "-vf", "scale=640:-2", out])
    return out if os.path.exists(out) else None


# ------------------------------------------------------------------ fetch from Drive
def fetch(dest, log=print, progress=None):
    """download Frontier's code, styles, samples and kits (not .env, footage, browser bundles)"""
    import gdown
    from concurrent.futures import ThreadPoolExecutor
    items = gdown.download_folder(id=DRIVE, output=os.path.join(dest, "_list") + "/", skip_download=True, quiet=True)
    root = os.path.join(dest, "_list")

    def rel(it):
        r = os.path.relpath(it.local_path, root).replace(os.sep, "/")
        return r[len("Frontier/"):] if r.startswith("Frontier/") else r

    def want(q):
        if q in (".env", ".DS_Store") or q.startswith((".env", "__pycache__", "gemini_image/", "Pipiline", "scratch",
                                                       "asset_cache", "farm/__pycache__", "assets/memes", "assets/brand/")):
            return False
        if "/" not in q:
            return q.endswith((".py", ".md", ".html", ".txt", ".json", ".example")) and not q.startswith(".env")
        return q.startswith(("styles/", "samples/", "assets/", "farm/"))
    sel = [(it.id, rel(it)) for it in items if want(rel(it))]
    log(f"Frontier: {len(sel)} files to fetch")
    done = [0]

    def get(r):
        fid, q = r
        out = os.path.join(dest, q)
        os.makedirs(os.path.dirname(out), exist_ok=True)
        if not (os.path.exists(out) and os.path.getsize(out) > 0):
            for _ in range(3):
                try:
                    gdown.download(id=fid, output=out, quiet=True)
                    if os.path.exists(out):
                        break
                except Exception:
                    time.sleep(2)
        done[0] += 1
        if progress and done[0] % 10 == 0:
            progress(done[0] / len(sel), f"{done[0]}/{len(sel)} files")
    with ThreadPoolExecutor(10) as ex:
        list(ex.map(get, sel))
    try:
        import shutil
        shutil.rmtree(root)
    except OSError:
        pass
    return dest


# ------------------------------------------------------------------ the local Frontier server
def _get(url, timeout=10):
    with urllib.request.urlopen(url, timeout=timeout) as r:
        return json.loads(r.read() or b"{}")


def _post(url, body, timeout=30):
    req = urllib.request.Request(url, data=json.dumps(body).encode(), method="POST", headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read() or b"{}")
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"Frontier refused the job: {e.read().decode('utf-8', 'ignore')[:400]}")


def server(fdir, python=None, log=print):
    """start Frontier's app.py on PORT unless it is already running -> (base_url, process or None)"""
    base = f"http://127.0.0.1:{PORT}"
    try:
        _get(base + "/api/channels", timeout=4)
        return base, None
    except Exception:
        pass
    env = dict(os.environ, FRONTIER_PORT=str(PORT), PYTHONUNBUFFERED="1")
    p = subprocess.Popen([python or sys.executable, "app.py"], cwd=fdir, env=env, stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace")
    t0 = time.time()
    while time.time() - t0 < 120:
        if p.poll() is not None:
            raise RuntimeError("Frontier's app.py stopped while starting:\n" + (p.stdout.read() or "")[-1500:])
        try:
            _get(base + "/api/channels", timeout=4)
            log(f"Frontier engine running on {base}")
            return base, p
        except Exception:
            time.sleep(2)
    p.kill()
    raise RuntimeError("Frontier's app.py did not start within 2 minutes (check its requirements and .env)")


def run(fdir, style, title, script_text, out_dir, name, audio=None, minutes=10, python=None, log=print, progress=None, extra=""):
    """make one video in a Frontier style and copy its files to out_dir -> {video, srt, desc, script}"""
    base, proc = server(fdir, python, log)
    try:
        steps = ["script", "voiceover", "pexels", "images", "video", "thumbnail"]
        body = dict(title=title, style=style, steps=steps, script=script_text, minutes=max(1, int(round(minutes))),
                    byo_audio=audio or "", burn_subs=True, desc=True, chapters=8, sources=4, extra=extra)
        r = _post(base + "/api/run", body)
        slug = (r.get("queued") or [{}])[0].get("slug")
        if not slug:
            raise RuntimeError(f"Frontier did not queue the job: {r}")
        log(f"Frontier job {slug} queued (style {style})")
        seen = 0
        while True:
            time.sleep(3)
            try:
                st = _get(f"{base}/api/status/{slug}")
            except Exception as e:                       # noqa: BLE001
                log(f"(waiting for Frontier: {e})")
                continue
            lines = st.get("lines") or []
            new = lines[seen:] if len(lines) >= seen else lines[-20:]
            for l in new:
                log("[frontier] " + str(l))
            seen = len(lines)
            if progress:
                progress(float(st.get("progress") or 0), (lines[-1] if lines else "")[:120])
            if st.get("done"):
                if st.get("state") == "error":
                    raise RuntimeError("Frontier: " + str(st.get("error")))
                break
        res = _get(f"{base}/api/result/{slug}")
        files = {}
        for kind, flag, ext in (("video", "video", ".mp4"), ("srt", "srt", ".srt"), ("desc", "desc", ".youtube.txt"),
                                ("script", "script", ".script.txt")):
            if res.get(flag):
                files[kind] = download(base, slug, kind, os.path.join(out_dir, name + ext))
        if "video" not in files:
            raise RuntimeError(f"Frontier finished without a video: {res}")
        return files
    finally:
        if proc is not None:
            proc.terminate()


def download(base, slug, kind, dest):
    """/f/video|srt|desc|script/<slug> -> dest"""
    with urllib.request.urlopen(f"{base}/f/{kind}/{slug}", timeout=600) as r, open(dest, "wb") as f:
        while True:
            b = r.read(1 << 20)
            if not b:
                break
            f.write(b)
    return dest
