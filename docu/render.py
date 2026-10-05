"""
Scene renderer: an edit decision list in, one finished MP4 per scene out.

Browser scenes are drawn by headless Chromium through window.renderFrame(t); each
frame is captured as JPEG and piped straight into an x264 encoder, so nothing
touches the disk between the page and the segment. Clip scenes never enter the
browser: FFmpeg trims, conforms and grades them to the same codec parameters, so
every segment concatenates losslessly.

Workers each keep one browser open and render whole scenes, longest first.
"""

import os
import sys
import json
import time
import base64
import pathlib
import subprocess
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__))
def _find_chrome():
    """$DOCU_CHROME, else any Playwright headless shell / chromium on this machine."""
    if os.environ.get("DOCU_CHROME"):
        return os.environ["DOCU_CHROME"]
    import glob
    roots = (os.environ.get("PLAYWRIGHT_BROWSERS_PATH", ""), "/opt/pw-browsers", os.path.expanduser("~/.cache/ms-playwright"),
             os.path.join(os.environ.get("LOCALAPPDATA", ""), "ms-playwright"), os.path.expanduser("~/Library/Caches/ms-playwright"))
    pats = ("chromium_headless_shell-*/chrome-linux*/headless_shell", "chromium-*/chrome-linux*/chrome",
            "chromium_headless_shell-*/chrome-headless-shell-win64/chrome-headless-shell.exe", "chromium-*/chrome-win*/chrome.exe",
            "chromium_headless_shell-*/chrome-headless-shell-mac*/chrome-headless-shell")
    for root in roots:
        for pat in pats:
            hits = sorted(glob.glob(os.path.join(root, pat))) if root else []
            if hits:
                return hits[-1]
    return None                     # let Playwright use its own default browser


CHROME = _find_chrome()


def file_uri(path):
    """file:// URL that works on Windows (file:///C:/...) as well as Linux and macOS."""
    return pathlib.Path(os.path.abspath(path)).as_uri()
FPS = 30
W, H = 1920, 1080

def _nvenc_works():
    """NVENC when this machine can actually use it (an NVIDIA GPU + a driver FFmpeg sees); x264 otherwise.
    DOCU_NVENC=0 / 1 forces either. Probed once with a tiny encode, so a laptop without a GPU never fails."""
    v = os.environ.get("DOCU_NVENC", "auto").lower()
    if v in ("0", "no", "false"):
        return False
    if v in ("1", "yes", "true"):
        return True
    try:
        r = subprocess.run(["ffmpeg", "-v", "error", "-f", "lavfi", "-i", "color=c=black:s=256x144:d=0.1",
                            "-c:v", "h264_nvenc", "-f", "null", "-"], capture_output=True, timeout=30)
        return r.returncode == 0
    except Exception:
        return False


_USE_NVENC = _nvenc_works()
os.environ.setdefault("DOCU_NVENC", "1" if _USE_NVENC else "0")     # edl._fit_size reads the same switch
# Per-scene encoder: keep per-scene bitrate higher so dissolves don't degrade; the final
# concat_xfade is what sets the deliverable's bitrate (and therefore its size).
if _USE_NVENC:
    X264 = ["-c:v", "h264_nvenc", "-preset", "p5", "-tune", "hq", "-rc", "vbr",
            "-cq", "22", "-b:v", "8M", "-maxrate", "12M", "-bufsize", "16M",
            "-pix_fmt", "yuv420p", "-profile:v", "high", "-r", str(FPS),
            "-g", str(FPS * 2), "-bf", "2", "-video_track_timescale", "15360", "-an"]
else:
    X264 = ["-c:v", "libx264", "-preset", "veryfast", "-crf", "19", "-pix_fmt", "yuv420p",
            "-profile:v", "high", "-r", str(FPS), "-g", str(FPS * 2), "-bf", "2",
            "-video_track_timescale", "15360", "-an"]


def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


# ----------------------------------------------------------------- browser

_B = {}


def _browser(cfg):
    key = json.dumps(cfg, sort_keys=True)
    if "page" in _B:
        if _B["cfg"] == key:
            return _B["page"], _B["cdp"]
        _B["page"].close()          # a new theme / kit: the page reads CFG only when it loads
        b, pw = _B["browser"], _B["pw"]
    else:
        from playwright.sync_api import sync_playwright
        pw = sync_playwright().start()
        b = pw.chromium.launch(executable_path=CHROME if CHROME and os.path.exists(CHROME) else None, args=[
            "--allow-file-access-from-files", "--disable-web-security", "--force-device-scale-factor=1",
            "--disable-gpu", "--hide-scrollbars", "--font-render-hinting=none"])
    page = b.new_page(viewport={"width": W, "height": H})
    page.add_init_script(f"window.CFG = {json.dumps(cfg)};")
    page.on("console", lambda m: m.type in ("error", "warning") and print("  [page]", m.text, flush=True))
    page.goto(file_uri(os.path.join(HERE, "engine.html")))
    page.wait_for_function("window.FONTS_READY === true", timeout=60000)
    cdp = page.context.new_cdp_session(page)
    _B.update(pw=pw, browser=b, page=page, cdp=cdp, cfg=key)
    return page, cdp


def _grain(cfg):
    """Film grain per project: it reads as texture, but it is also most of the bitrate."""
    g = float(cfg.get("grain", 5))
    return f"noise=alls={g:g}:allf=t" if g > 0 else "null"


def _length(scene):
    """Rendered length: the scene's own time plus the overlap a dissolve into the next scene needs."""
    return scene["duration"] + float(scene.get("pad", 0.0))


def _frames(scene):
    return max(1, int(round(_length(scene) * FPS)))


def render_browser_scene(scene, out_path, cfg, quality=90, only_times=None, still_dir=None):
    page, cdp = _browser(cfg)
    page.evaluate("s => window.setupScene(s)", scene)
    if only_times is not None:
        paths = []
        for t in only_times:
            page.evaluate(f"window.renderFrame({t})")
            r = cdp.send("Page.captureScreenshot", {"format": "jpeg", "quality": 88})
            p = os.path.join(still_dir, f"{scene['id']}_{t:05.2f}.jpg")
            open(p, "wb").write(base64.b64decode(r["data"]))
            paths.append(p)
        return paths
    n = _frames(scene)
    tmp = out_path + ".part.mp4"
    ff = subprocess.Popen(
        ["ffmpeg", "-v", "error", "-y", "-f", "image2pipe", "-framerate", str(FPS), "-c:v", "mjpeg",
         "-i", "-", "-vf", scene.get("vf", _grain(cfg)), "-threads", "2"] + X264 + [tmp],
        stdin=subprocess.PIPE)
    for f in range(n):
        page.evaluate(f"window.renderFrame({f / FPS})")
        r = cdp.send("Page.captureScreenshot", {"format": "jpeg", "quality": quality,
                                                  "optimizeForSpeed": True})
        ff.stdin.write(base64.b64decode(r["data"]))
    ff.stdin.close()
    if ff.wait() != 0:
        raise RuntimeError(f"encode failed for {scene['id']}")
    for _try in range(8):
        try:
            os.replace(tmp, out_path)
            break
        except (PermissionError, OSError):
            time.sleep(0.25 * (2 ** _try))
    else:
        os.replace(tmp, out_path)


# -------------------------------------------------------------------- clips

GRADES = {
    "doc": "eq=saturation=0.84:contrast=1.05:gamma=0.98,colorbalance=rs=0.02:bs=-0.02:rh=0.03:bh=-0.03",
    "bw": "hue=s=0,eq=contrast=1.12",
    "warmsepia": "eq=saturation=0.74:contrast=1.02,colorbalance=rs=0.04:gs=0.01:bs=-0.06:rm=0.03:bm=-0.04",
    "cool": "eq=saturation=0.8:contrast=1.07:gamma=0.98,colorbalance=rs=-0.02:bs=0.03:rh=-0.01:bh=0.02",
    "warm": "eq=saturation=0.92:contrast=1.04,colorbalance=rh=0.05:bh=-0.05",
    "broadcast": "eq=saturation=0.94:contrast=1.1,colorbalance=rs=-0.03:bs=0.04:rh=0.01:bh=-0.01",
    "almanac": "eq=saturation=0.86:contrast=1.03,colorbalance=rs=0.03:gs=0.01:bs=-0.03:rh=0.03:bh=-0.04,curves=all='0/0.035 1/0.975'",
    "almanac2": "eq=saturation=0.82:contrast=1.05,colorbalance=rs=-0.02:gs=0.01:bs=0.03:rh=0.02:bh=-0.02,curves=all='0/0.03 1/0.97'",
    "datadoc": "eq=contrast=1.06:saturation=0.86:gamma=0.97,colorbalance=rs=0.03:bs=-0.03:rh=0.02:bh=-0.02",
    "none": "",
}


def render_clip_scene(scene, out_path, cfg):
    """Trim, conform and grade one clip - or several shots cut together - to an exact length."""
    dur = _length(scene)
    parts = [dict(src=scene["src"], start=float(scene.get("start", 0)), end=float(scene.get("end", 0)))]
    parts += scene.get("more", [])
    avail = sum(max(0.3, p["end"] - p["start"]) for p in parts)
    # hold the shots with a gentle slow-down rather than repeating them
    speed = min(1.0, max(0.5, avail / dur))
    crop = scene.get("crop")          # fractional (x0, y0, x1, y1) to cut away bugs/lower thirds
    inputs, chains = [], []
    for k, p in enumerate(parts):
        length = max(0.3, p["end"] - p["start"])
        inputs += ["-ss", f"{p['start']:.3f}", "-t", f"{length:.3f}", "-i", p["src"]]
        ch = [f"[{k}:v]trim=duration={length:.3f}", f"setpts={1 / speed:.5f}*(PTS-STARTPTS)", f"fps={FPS}"]
        if crop:
            x0, y0, x1, y1 = crop
            ch.append(f"crop=iw*{x1 - x0:.4f}:ih*{y1 - y0:.4f}:iw*{x0:.4f}:ih*{y0:.4f}")
        ch.append(f"scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos,crop={W}:{H},setsar=1,format=yuv420p")
        chains.append(",".join(ch) + f"[p{k}]")
    fc = ";".join(chains) + ";" + "".join(f"[p{k}]" for k in range(len(parts))) + \
        f"concat=n={len(parts)}:v=1:a=0[cat]"
    post = []
    if speed * avail / 1.0 < dur:
        # still short after the slow-down: hold the last frame
        post.append(f"tpad=stop_mode=clone:stop_duration={dur:.3f}")
    z = scene.get("zoom")
    if z:
        # a fixed crop-in: trims edge artefacts and source bugs; the footage carries its own motion
        post.append(f"scale={int(W * z) // 2 * 2}:{int(H * z) // 2 * 2}:flags=lanczos,crop={W}:{H}")
    pz = float(scene.get("push") or 0)
    if pz:
        # a slow linear push across the shot (Data Documentary: 100 -> 103.5 %), scaled per frame, centre crop
        post.append(f"scale=w='2*trunc({W}*(1+{pz}*t/{dur:.3f})/2)':h='2*trunc({H}*(1+{pz}*t/{dur:.3f})/2)':eval=frame:flags=bicubic,"
                    f"crop={W}:{H}:(iw-{W})/2:(ih-{H})/2")
    g = GRADES.get(scene.get("grade", "doc"), scene.get("grade", ""))
    if g:
        post.append(g)
    post += [scene.get("vignette") or "vignette=PI/5", _grain(cfg)]
    if scene.get("fadein"):
        post.append(f"fade=t=in:st=0:d={scene['fadein']}")
    if scene.get("fadeout"):
        post.append(f"fade=t=out:st={dur - scene['fadeout']:.3f}:d={scene['fadeout']}")
    post.append(f"trim=duration={dur:.3f}")
    fc += ";[cat]" + ",".join(post) + "[v]"
    ovl = scene.get("overlay_png")
    mov = scene.get("overlay_mov")
    if mov:
        n = len(parts)
        inputs += ["-i", mov]
        fc += f";[{n}:v]format=rgba[o];[v][o]overlay=0:0:format=auto:eof_action=repeat[v2]"
        vout = "[v2]"
    elif ovl:
        n = len(parts)
        inputs += ["-loop", "1", "-t", f"{dur:.3f}", "-i", ovl]
        at = float(scene.get("overlay_at", 0.0))
        fc += f";[{n}:v]format=rgba,fade=t=in:st={at}:d=0.35:alpha=1[o];[v][o]overlay=0:0:format=auto[v2]"
        vout = "[v2]"
    else:
        vout = "[v]"
    tex = scene.get("texture_png")
    if tex:
        # a static looping overlay (VHS lines, dust, paper grain) on top of everything else
        tex_opacity = float(scene.get("texture_opacity", 0.6))
        n2 = len(parts) + (1 if (mov or ovl) else 0)
        inputs += ["-loop", "1", "-t", f"{dur:.3f}", "-i", tex]
        fc += f";[{n2}:v]format=rgba,colorchannelmixer=aa={tex_opacity:.3f}[t];{vout}[t]overlay=0:0:format=auto[v3]"
        vout = "[v3]"
    cmd = ["ffmpeg", "-v", "error", "-y"] + inputs + ["-filter_complex", fc, "-map", vout,
                                                       "-frames:v", str(_frames(scene)), "-threads", "3"] + X264 + [out_path + ".part.mp4"]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"clip {scene['id']} failed: {r.stderr[-800:]}")
    for _try in range(8):
        try:
            os.replace(out_path + ".part.mp4", out_path)
            break
        except (PermissionError, OSError):
            time.sleep(0.25 * (2 ** _try))
    else:
        os.replace(out_path + ".part.mp4", out_path)


def apply_fx(path, scene):
    """Finishing layers on a rendered segment, in one extra pass (same codec settings, so concat stays lossless):

        texture_png + texture_opacity     a still paper / grain / VHS-lines texture over the picture
        fx = [{src, mode, opacity}]        moving overlays on black (dust, light leak, VHS noise) blended in
                                           with `screen` (default) - or {src, key: "green"} to key out the
                                           green of a vintage-TV / film-gate frame and lay it over the shot

    Clip scenes already burn their still texture in render_clip_scene; this adds it to browser scenes and the
    moving overlays to both."""
    fxs = list(scene.get("fx") or [])
    tex = scene.get("texture_png")
    if not fxs and not tex:
        return
    dur = _length(scene)
    inputs, fc, last = ["-i", path], [], "[0:v]"
    k = 1
    if tex and os.path.exists(tex):
        # neutral (mid-grey) textures blend with soft-light: grain and paper fibre, the colours stay the footage's
        op = float(scene.get("texture_opacity", 0.6))
        mode = scene.get("texture_mode", "softlight")
        inputs += ["-loop", "1", "-t", f"{dur:.3f}", "-i", tex]
        fc.append(f"{last}format=gbrp[a{k}];[{k}:v]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
                  f"fps={FPS},format=gbrp[t{k}];[a{k}][t{k}]blend=all_mode={mode}:all_opacity={op:.3f},format=yuv420p[v{k}]")
        last, k = f"[v{k}]", k + 1
    for f in fxs:
        src = f.get("src")
        if not src or not os.path.exists(src):
            continue
        inputs += ["-stream_loop", "-1", "-t", f"{dur:.3f}", "-i", src]
        start = float(f.get("at", 0.0))
        if f.get("key") == "green":
            fc.append(f"[{k}:v]scale={W}:{H},fps={FPS},chromakey=0x22FF22:0.30:0.10,format=rgba,"
                      f"setpts=PTS+{start:.3f}/TB[f{k}];{last}[f{k}]overlay=0:0:format=auto:eof_action=pass[v{k}]")
        else:
            op = float(f.get("opacity", 0.6))
            mode = f.get("mode", "screen")
            fc.append(f"{last}format=gbrp[a{k}];[{k}:v]scale={W}:{H},fps={FPS},format=gbrp,"
                      f"trim=duration={dur:.3f},setpts=PTS-STARTPTS[f{k}];"
                      f"[a{k}][f{k}]blend=all_mode={mode}:all_opacity={op:.3f}:enable='gte(t,{start:.3f})',format=yuv420p[v{k}]")
        last, k = f"[v{k}]", k + 1
    if not fc:
        return
    tmp = path + ".fx.mp4"
    cmd = ["ffmpeg", "-v", "error", "-y"] + inputs + ["-filter_complex", ";".join(fc), "-map", last,
                                                       "-frames:v", str(_frames(scene)), "-threads", "3"] + X264 + [tmp]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"fx pass failed for {scene.get('id')}: {r.stderr[-600:]}")
    os.replace(tmp, path)


ANIMATED_OVERLAYS = {"ticker", "bug", "newslower", "almhead", "gzhead", "ddlabel", "ddtab"}


def render_overlay_video(scene, out_mov, cfg):
    """Render a clip's overlays as a moving alpha layer (for crawls and bugs that must keep
    moving over footage). The overlay page sees the clip's own t0, so a ticker runs on
    continuously across cuts."""
    page, cdp = _browser(cfg)
    spec = {"type": "blank", "duration": _length(scene), "t0": scene.get("t0", 0), "bgcolor": "transparent",
            "overlays": scene["overlays"]}
    page.evaluate("s => window.setupScene(s)", spec)
    page.evaluate("document.documentElement.style.background='transparent';document.body.style.background='transparent';"
                  "document.getElementById('stage').style.background='transparent'")
    cdp.send("Emulation.setDefaultBackgroundColorOverride", {"color": {"r": 0, "g": 0, "b": 0, "a": 0}})
    ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "image2pipe", "-framerate", str(FPS), "-c:v", "png", "-i", "-",
                           "-c:v", "qtrle", "-pix_fmt", "argb", out_mov], stdin=subprocess.PIPE)
    for f in range(_frames(scene)):
        page.evaluate(f"window.renderFrame({f / FPS})")
        r = cdp.send("Page.captureScreenshot", {"format": "png", "optimizeForSpeed": True})
        ff.stdin.write(base64.b64decode(r["data"]))
    ff.stdin.close()
    cdp.send("Emulation.setDefaultBackgroundColorOverride", {})
    if ff.wait() != 0:
        raise RuntimeError(f"overlay encode failed for {scene['id']}")


def render_overlay_png(scene_overlays, out_png, cfg):
    """Render a transparent overlay (chips, lower thirds) for a clip at its final state."""
    page, cdp = _browser(cfg)
    spec = {"type": "blank", "duration": 10, "bgcolor": "transparent", "overlays": scene_overlays}
    page.evaluate("s => window.setupScene(s)", spec)
    page.evaluate("window.renderFrame(8)")
    page.evaluate("document.documentElement.style.background='transparent';document.body.style.background='transparent';"
                  "document.getElementById('stage').style.background='transparent'")
    cdp.send("Emulation.setDefaultBackgroundColorOverride", {"color": {"r": 0, "g": 0, "b": 0, "a": 0}})
    r = cdp.send("Page.captureScreenshot", {"format": "png"})
    open(out_png, "wb").write(base64.b64decode(r["data"]))
    cdp.send("Emulation.setDefaultBackgroundColorOverride", {})


# ------------------------------------------------------------------- driver

def _work(args):
    scene, out_dir, cfg = args
    out = os.path.join(out_dir, f"{scene['id']}.mp4")
    if os.path.exists(out) and os.path.getsize(out) > 0 and not scene.get("force"):
        return scene["id"], 0.0, None
    t0 = time.time()
    try:
        if scene["type"] == "clip":
            if any(o["type"] in ANIMATED_OVERLAYS for o in scene.get("overlays", [])):
                mov = os.path.join(out_dir, f"{scene['id']}_ovl.mov")
                render_overlay_video(scene, mov, cfg)
                scene = dict(scene, overlay_mov=mov)
            elif scene.get("overlays"):
                png = os.path.join(out_dir, f"{scene['id']}_ovl.png")
                render_overlay_png(scene["overlays"], png, cfg)
                first = min(float(o.get("at", 0.5)) for o in scene["overlays"])
                scene = dict(scene, overlay_png=png, overlay_at=first)
            render_clip_scene(dict(scene, texture_png=None), out, cfg)
        else:
            render_browser_scene(scene, out, cfg)
        apply_fx(out, scene)
        return scene["id"], time.time() - t0, None
    except Exception as e:
        return scene["id"], time.time() - t0, str(e)[-600:]


def render_all(scenes, out_dir, cfg, workers=4):
    os.makedirs(out_dir, exist_ok=True)
    jobs = sorted(scenes, key=lambda s: -s["duration"] if s["type"] != "clip" else 0)
    t0 = time.time()
    fails = []
    with Pool(workers) as pool:
        for i, (sid, dt, err) in enumerate(pool.imap_unordered(_work, [(s, out_dir, cfg) for s in jobs])):
            if err:
                fails.append((sid, err))
                log(f"  FAIL {sid}: {err}")
            if (i + 1) % 10 == 0 or i + 1 == len(jobs):
                log(f"  {i + 1}/{len(jobs)} scenes ({time.time() - t0:.0f}s elapsed)")
    return fails


def concat(scenes, out_dir, out_path):
    lst = os.path.join(out_dir, "concat.txt")
    with open(lst, "w") as f:
        for s in scenes:
            f.write(f"file '{os.path.join(out_dir, s['id'] + '.mp4').replace(os.sep, '/')}'\n")
    r = subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst,
                        "-c", "copy", out_path], capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(r.stderr[-1500:])


def concat_xfade(scenes, out_dir, out_path, batch=24):
    """Join scene segments with dissolves. Each segment was rendered `pad` seconds longer than
    its slot; the dissolve into the next scene happens over that overlap, so every cut still
    lands exactly on its word. A scene with xfade=0 (or no pad) cuts hard.
    Runs in batches (a few dozen decoders at a time), then joins the batches the same way."""
    def join(items, out, crf):
        # items: [(path, slot_seconds, pad_seconds)]
        inputs, fc, last, t = [], [], "[0:v]", 0.0
        for k, (p, slot, pad) in enumerate(items):
            inputs += ["-i", p]
        for k in range(1, len(items)):
            t += items[k - 1][1]
            pad = items[k - 1][2]
            d = max(1.0 / FPS, pad)
            lab = f"[x{k}]"
            if pad > 0.01:
                fc.append(f"{last}[{k}:v]xfade=transition=fade:duration={d:.3f}:offset={t:.3f}{lab}")
            else:
                fc.append(f"{last}[{k}:v]concat=n=2:v=1:a=0{lab}")
            last = lab
        total = sum(x[1] for x in items) + items[-1][2]
        cmd = ["ffmpeg", "-v", "error", "-y"] + inputs
        if fc:
            cmd += ["-filter_complex", ";".join(fc), "-map", last]
        # Final concat_xfade is the deliverable: target ~700 MB (override via DOCU_TARGET_MB).
        # For a typical 15-20 min 1080p30 doc, ~5 Mbps lands around 650-800 MB.
        _target_mb = int(os.environ.get("DOCU_TARGET_MB", "700"))
        _mins_est = max(1.0, total / 60.0)
        _bv_kbps = max(2500, int((_target_mb * 8192) / (_mins_est * 60)))
        _bv_kbps = min(_bv_kbps, int(os.environ.get("DOCU_MAX_KBPS", "12000")))   # a short video must not get 90 Mbps
        _bv = f"{_bv_kbps}k"
        _max = f"{int(_bv_kbps * 1.4)}k"
        _buf = f"{int(_bv_kbps * 2)}k"
        if _USE_NVENC:
            cmd += ["-t", f"{total:.3f}", "-c:v", "h264_nvenc", "-preset", "p5", "-tune", "hq",
                    "-rc", "vbr", "-cq", str(max(22, min(30, int(crf) + 4))),
                    "-b:v", _bv, "-maxrate", _max, "-bufsize", _buf,
                    "-pix_fmt", "yuv420p", "-r", str(FPS), out]
        else:
            cmd += ["-t", f"{total:.3f}", "-c:v", "libx264", "-preset", "veryfast",
                    "-b:v", _bv, "-maxrate", _max, "-bufsize", _buf, "-pix_fmt", "yuv420p",
                    "-r", str(FPS), "-threads", "4", out]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0:
            raise RuntimeError(r.stderr[-1500:])
        return total
    items = [(os.path.join(out_dir, s["id"] + ".mp4"), s["duration"], float(s.get("pad", 0.0))) for s in scenes]
    parts = []
    for b in range(0, len(items), batch):
        chunk = items[b:b + batch]
        out = os.path.join(out_dir, f"_xf_{b // batch:03d}.mp4")
        log(f"  dissolves: batch {b // batch + 1}/{(len(items) + batch - 1) // batch}")
        join(chunk, out, 14)
        parts.append((out, sum(x[1] for x in chunk), chunk[-1][2]))
    join(parts, out_path, 18)
    for p, _, _ in parts:
        os.remove(p)


def stills(scenes, cfg, still_dir, per_scene=1):
    """Render QA stills (no encoding) for browser scenes."""
    os.makedirs(still_dir, exist_ok=True)
    out = []
    for s in scenes:
        if s["type"] == "clip":
            continue
        ts = [s["duration"] * (k + 1) / (per_scene + 1) for k in range(per_scene)] if per_scene > 1 else [min(s["duration"] - 0.05, max(2.2, s["duration"] * 0.7))]
        out += render_browser_scene(s, None, cfg, only_times=ts, still_dir=still_dir)
    return out
