"""
Pure GPU NVENC Rendering Engine.

Renders every timeline segment in parallel with hardware encoding, concatenates
them losslessly, then muxes the multi-track audio matrix (opening soundbite +
boosted master voiceover + ducked background music).

Frame size, pacing and the visual grade are all supplied by the caller - see
looks.py for the named grades. Nothing about the subject of the documentary,
or about how it should look, is baked in here.
"""

import os
import json
import time
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed

import looks as looks_module


def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def probe_duration(path):
    """Return media duration in seconds, or 0.0 if it cannot be probed."""
    res = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", path],
        capture_output=True, text=True)
    try:
        return float(res.stdout.strip())
    except ValueError:
        return 0.0


def _join(*parts):
    """Comma-join filter fragments, dropping the empty ones."""
    return ",".join(p for p in parts if p)


class RenderEngine:
    """Renders a timeline JSON into a finished, muxed MP4."""

    def __init__(self, work_dir, bgm_path=None, workers=6,
                 width=1920, height=1080, fps=30,
                 encoder="h264_nvenc", preset="p1",
                 bitrate="2500k", maxrate="3500k", bufsize="5000k",
                 vo_volume=1.75, bgm_volume=0.08, opening_volume=1.5,
                 limiter_ceiling=0.95, hwaccel="cuda",
                 look=None, look_overrides=None):
        self.work_dir = work_dir
        self.bgm_path = bgm_path if bgm_path and os.path.exists(bgm_path) else None
        if bgm_path and not self.bgm_path:
            log(f"WARNING: BGM not found, continuing without it: {bgm_path}")
        self.workers = int(workers)

        self.W = int(width)
        self.H = int(height)
        self.fps = int(fps)
        self.encoder = encoder
        self.preset = preset
        self.bitrate = bitrate
        self.maxrate = maxrate
        self.bufsize = bufsize

        self.vo_volume = float(vo_volume)
        self.bgm_volume = float(bgm_volume)
        self.opening_volume = float(opening_volume)
        self.limiter_ceiling = float(limiter_ceiling) if limiter_ceiling else 0.0
        self.hwaccel = hwaccel

        self.look = looks_module.resolve(look, look_overrides)
        self.fade_s = float(self.look["fade_s"])
        self.zoom_per_sec = float(self.look["zoom_per_sec"])

        self.segments_dir = os.path.join(work_dir, "segments")
        self.cache_dir = os.path.join(work_dir, "image_cache")

    # ----------------------------------------------------------- filtergraph

    def _gpu_encode_args(self):
        return ["-c:v", self.encoder, "-preset", self.preset, "-rc", "vbr",
                "-b:v", self.bitrate, "-maxrate", self.maxrate,
                "-bufsize", self.bufsize, "-pix_fmt", "yuv420p",
                "-r", str(self.fps), "-an"]

    def _fades(self, dur):
        out_at = max(0.0, dur - self.fade_s)
        return f"fade=t=in:st=0:d={self.fade_s},fade=t=out:st={out_at:.4f}:d={self.fade_s}"

    def _to_png(self, img_path):
        """WebP sources are decoded once to PNG; other formats pass through."""
        if not img_path or not os.path.exists(img_path):
            return img_path
        if not img_path.lower().endswith(".webp"):
            return img_path
        os.makedirs(self.cache_dir, exist_ok=True)
        out_png = os.path.join(
            self.cache_dir, os.path.splitext(os.path.basename(img_path))[0] + ".png")
        if not os.path.exists(out_png) or os.path.getsize(out_png) == 0:
            subprocess.run(["ffmpeg", "-y", "-i", img_path, out_png], capture_output=True)
        return out_png

    def _fit(self, w, h, tag=""):
        """Fit any aspect ratio into w x h without leaving dead black bars.

        A portrait photograph in a landscape frame used to be padded with solid
        black down both sides, which is the single most obvious flaw in the
        finished video. "blur" instead fills the surround with a scaled-up,
        blurred, slightly darkened copy of the same frame.
        """
        mode = self.look["fill_mode"]
        fit = f"scale={w}:{h}:force_original_aspect_ratio=decrease"

        if mode == "crop":
            # Fill the frame completely, losing whatever falls outside it.
            return (f"scale={w}:{h}:force_original_aspect_ratio=increase,"
                    f"crop={w}:{h},setsar=1")

        if mode != "blur":
            return (f"{fit},pad={w}:{h}:trunc((ow-iw)/2):trunc((oh-ih)/2):black,"
                    f"setsar=1")

        sigma = float(self.look["fill_blur"])
        dim = float(self.look["fill_dim"])
        # Blurring at full resolution is the single most expensive filter in the
        # chain. Shrinking first, blurring the thumbnail, then scaling back up
        # is visually identical once blurred and roughly six times cheaper, so
        # sigma is divided by the same factor to keep the same apparent blur.
        shrink = max(1, int(self.look["fill_downscale"]))
        bw = max(16, (w // shrink) // 2 * 2)
        bh = max(16, (h // shrink) // 2 * 2)
        bg, fg, out = f"bg{tag}", f"fg{tag}", f"px{tag}"
        return (
            f"split[{bg}][{fg}];"
            f"[{bg}]scale={bw}:{bh}:force_original_aspect_ratio=increase,"
            f"crop={bw}:{bh},gblur=sigma={max(0.5, sigma / shrink):.3f},"
            f"scale={w}:{h}:flags=bilinear,eq=brightness=-{dim:.3f}[{out}];"
            f"[{fg}]{fit}[{fg}s];"
            f"[{out}][{fg}s]overlay=(W-w)/2:(H-h)/2,setsar=1"
        )

    def _ken_burns(self, mode, dur, is_graphic=False, postcard=False):
        """Zero-shake sub-pixel motion via the perspective filter."""
        frames = max(1, int(dur * self.fps) - 1)
        z = self.zoom_per_sec * dur
        CW = round(self.W * (1 + z) / 16) * 16
        CH = (round(CW * self.H / self.W) // 2) * 2

        if mode == "zoomin":
            p = (f"x0=0+{z}*{CW}/2*on/{frames}:y0=0+{z}*{CH}/2*on/{frames}:"
                 f"x1={CW}-{z}*{CW}/2*on/{frames}:y1=0+{z}*{CH}/2*on/{frames}:"
                 f"x2=0+{z}*{CW}/2*on/{frames}:y2={CH}-{z}*{CH}/2*on/{frames}:"
                 f"x3={CW}-{z}*{CW}/2*on/{frames}:y3={CH}-{z}*{CH}/2*on/{frames}")
        elif mode == "zoomout":
            p = (f"x0=0+{z}*{CW}/2*(1-on/{frames}):y0=0+{z}*{CH}/2*(1-on/{frames}):"
                 f"x1={CW}-{z}*{CW}/2*(1-on/{frames}):y1=0+{z}*{CH}/2*(1-on/{frames}):"
                 f"x2=0+{z}*{CW}/2*(1-on/{frames}):y2={CH}-{z}*{CH}/2*(1-on/{frames}):"
                 f"x3={CW}-{z}*{CW}/2*(1-on/{frames}):y3={CH}-{z}*{CH}/2*(1-on/{frames})")
        elif mode == "panright":
            p = (f"x0=0+{z}*{CW}*on/{frames}:y0=0:"
                 f"x1={CW}+{z}*{CW}*on/{frames}:y1=0:"
                 f"x2=0+{z}*{CW}*on/{frames}:y2={CH}:"
                 f"x3={CW}+{z}*{CW}*on/{frames}:y3={CH}")
        else:
            p = (f"x0={z}*{CW}*(1-on/{frames}):y0=0:"
                 f"x1={CW}+{z}*{CW}*(1-on/{frames}):y1=0:"
                 f"x2={z}*{CW}*(1-on/{frames}):y2={CH}:"
                 f"x3={CW}+{z}*{CW}*(1-on/{frames}):y3={CH}")

        grade = (self.look["graphic_grade"] if is_graphic
                 else _join(self.look["postcard_eq"] if postcard else "",
                            self.look["grade"]))

        return _join(
            self._fit(CW, CH),
            f"perspective=eval=frame:sense=source:interpolation=linear:{p}",
            f"scale={self.W}:{self.H}:flags=bicubic,setsar=1",
            grade,
            self._fades(dur),
        )

    # -------------------------------------------------------------- segments

    def _render_segment(self, seg):
        """Render one segment. Returns (index, path, ok, elapsed, error)."""
        idx = seg["index"]
        out_file = os.path.join(self.segments_dir, f"seg_{idx:04d}.mp4")
        dur = float(seg["duration"])
        src = seg.get("file")
        started = time.time()

        if not src or not os.path.exists(src):
            return idx, out_file, False, 0.0, f"source missing: {src}"

        gpu = self._gpu_encode_args()
        stype = seg.get("type")

        if stype == "headline":
            vf = _join(
                self._fit(self.W, self.H),
                f"drawbox=x=0:y=0:w=iw:h=ih:"
                f"color={self.look['border_color']}@0.95:t=4",
                self.look["grade"], self._fades(dur))
            cmd = ["ffmpeg", "-y", "-ss", "0", "-t", str(dur), "-i", src,
                   "-vf", vf] + gpu + [out_file]
        elif stype == "image":
            png = self._to_png(src)
            vf = self._ken_burns(seg.get("motion", "zoomin"), dur,
                                 is_graphic=(seg.get("section") == "custom_graphic"),
                                 postcard=bool(seg.get("postcard")))
            cmd = ["ffmpeg", "-y", "-loop", "1", "-framerate", str(self.fps),
                   "-i", png, "-vf", vf, "-t", str(dur)] + gpu + [out_file]
        elif stype == "clip":
            vf = _join(self._fit(self.W, self.H), self.look["grade"],
                       self._fades(dur))
            cmd = (["ffmpeg", "-y", "-hwaccel", self.hwaccel, "-ss", "0",
                    "-t", str(dur), "-i", src, "-vf", vf] + gpu + [out_file])
        else:
            return idx, out_file, False, 0.0, f"unknown segment type: {stype!r}"

        res = subprocess.run(cmd, capture_output=True, text=True, errors="replace")
        elapsed = time.time() - started

        if res.returncode != 0 or not os.path.exists(out_file) or os.path.getsize(out_file) == 0:
            tail = (res.stderr or "").strip().splitlines()[-3:]
            return idx, out_file, False, elapsed, " | ".join(tail) or "ffmpeg failed"
        return idx, out_file, True, elapsed, None

    def render_segments(self, segments, resume=True):
        """Render all segments in parallel. Returns (ok, failures, seconds)."""
        os.makedirs(self.segments_dir, exist_ok=True)

        ok, todo = {}, []
        for s in segments:
            path = os.path.join(self.segments_dir, f"seg_{s['index']:04d}.mp4")
            if resume and os.path.exists(path) and os.path.getsize(path) > 0:
                ok[s["index"]] = path
            else:
                todo.append(s)

        if ok:
            log(f"Reusing {len(ok)} segments already on disk.")
        log(f"Rendering {len(todo)} segments on {self.encoder} "
            f"at {self.W}x{self.H}@{self.fps} with {self.workers} workers...")

        failures, times = [], []
        started = time.time()

        if todo:
            with ThreadPoolExecutor(max_workers=self.workers) as pool:
                futures = {pool.submit(self._render_segment, s): s for s in todo}
                done = 0
                for fut in as_completed(futures):
                    idx, path, good, elapsed, err = fut.result()
                    done += 1
                    times.append(elapsed)
                    if good:
                        ok[idx] = path
                    else:
                        failures.append((idx, err))
                    if done % 50 == 0 or done == len(todo):
                        avg = sum(times) / max(1, len(times))
                        log(f"  {done}/{len(todo)} segments (avg {avg:.3f}s/seg, "
                            f"{len(failures)} failed).")

        total = time.time() - started
        log(f"Segment rendering finished in {total:.2f}s ({total / 60:.2f} min).")
        return ok, failures, total

    # ------------------------------------------------------------- assembly

    def concat_segments(self, segments, ok, silent_path):
        """Losslessly concatenate rendered segments in timeline order."""
        concat_txt = os.path.join(self.work_dir, "segments_concat.txt")
        written = 0
        with open(concat_txt, "w", encoding="utf-8") as f:
            for seg in segments:
                path = ok.get(seg["index"])
                if not path:
                    continue
                f.write("file '%s'\n" % path.replace("\\", "/").replace("'", "'\\''"))
                written += 1

        if written == 0:
            raise RuntimeError("No segments rendered successfully; nothing to concatenate.")

        log(f"Concatenating {written} segments into {os.path.basename(silent_path)}...")
        started = time.time()
        res = subprocess.run(
            ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_txt,
             "-c", "copy", silent_path],
            capture_output=True, text=True, errors="replace")
        if res.returncode != 0:
            raise RuntimeError(f"Concat failed:\n{res.stderr[-2000:]}")
        return time.time() - started

    def build_audio_matrix(self, silent_path, master_mp3, opening_clip,
                           lead_s, video_duration, final_path):
        """Mux opening soundbite + boosted voiceover + ducked BGM onto the video."""
        inputs = ["-i", silent_path]
        filters = []
        mix = []
        next_idx = 1

        if opening_clip and lead_s > 0 and os.path.exists(opening_clip):
            inputs += ["-ss", "0", "-t", str(lead_s), "-i", opening_clip]
            filters.append(
                f"[{next_idx}:a]volume={self.opening_volume},"
                f"apad=whole_dur={video_duration:.3f}[head_a]")
            mix.append("[head_a]")
            next_idx += 1

        inputs += ["-i", master_mp3]
        delay_ms = int(round(lead_s * 1000))
        vo_chain = f"[{next_idx}:a]"
        if delay_ms > 0:
            vo_chain += f"adelay={delay_ms}|{delay_ms},"
        vo_chain += f"volume={self.vo_volume}[vo]"
        filters.append(vo_chain)
        mix.append("[vo]")
        next_idx += 1

        if self.bgm_path:
            inputs += ["-stream_loop", "-1", "-i", self.bgm_path]
            filters.append(
                f"[{next_idx}:a]volume={self.bgm_volume},"
                f"atrim=0:{video_duration:.3f},asetpts=N/SR/TB[bgm]")
            mix.append("[bgm]")
            next_idx += 1

        if len(mix) > 1:
            # normalize=0 keeps the boosted voiceover at its intended level;
            # amix otherwise divides every input by the number of streams.
            filters.append(
                f"{''.join(mix)}amix=inputs={len(mix)}:duration=longest:"
                f"dropout_transition=0:normalize=0[mixed]")
            out_label = "[mixed]"
        else:
            out_label = mix[0]

        if self.limiter_ceiling > 0:
            # A boosted voiceover summed with BGM overshoots 0 dBFS and clips.
            # level=disabled stops the limiter making up gain afterwards.
            filters.append(
                f"{out_label}alimiter=limit={self.limiter_ceiling}:level=disabled[aout]")
            out_label = "[aout]"

        cmd = (["ffmpeg", "-y"] + inputs +
               ["-filter_complex", ";".join(filters),
                "-map", "0:v", "-map", out_label,
                "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                "-movflags", "+faststart", "-shortest", final_path])

        log(f"Muxing audio matrix -> {final_path}")
        started = time.time()
        res = subprocess.run(cmd, capture_output=True, text=True, errors="replace")
        if res.returncode != 0:
            raise RuntimeError(f"Audio mux failed:\n{res.stderr[-2000:]}")
        return time.time() - started

    # ------------------------------------------------------------ entrypoint

    def render_and_mux(self, timeline_json, master_mp3, final_video_path,
                       resume=True):
        """Full stage 3+4: render every segment, concatenate, mux audio."""
        with open(timeline_json, "r", encoding="utf-8") as f:
            data = json.load(f)
        segments = data["segments"]
        lead_s = float(data.get("opening_lead_s", 0.0))

        os.makedirs(os.path.dirname(os.path.abspath(final_video_path)), exist_ok=True)

        log("=" * 60)
        log(f"GPU RENDER: {len(segments)} segments -> {os.path.basename(final_video_path)}")
        log(f"{self.W}x{self.H}@{self.fps} | {self.encoder}/{self.preset} @ "
            f"{self.bitrate} | fill={self.look['fill_mode']}")
        log(f"VO x{self.vo_volume} | BGM "
            f"{'x%s' % self.bgm_volume if self.bgm_path else 'none'} | "
            f"limiter {self.limiter_ceiling or 'off'}")
        log("=" * 60)

        ok, failures, render_t = self.render_segments(segments, resume=resume)

        if failures:
            log(f"WARNING: {len(failures)} of {len(segments)} segments failed to render.")
            for idx, err in failures[:10]:
                log(f"  seg {idx:04d}: {err}")
            if len(ok) < len(segments) * 0.9:
                raise RuntimeError(
                    f"Too many segment failures ({len(failures)}/{len(segments)}); aborting.")

        silent_path = os.path.join(self.work_dir, "video_silent.mp4")
        concat_t = self.concat_segments(segments, ok, silent_path)

        video_duration = probe_duration(silent_path)
        if video_duration <= 0:
            raise RuntimeError(f"Could not probe duration of {silent_path}")

        opening_clip = segments[0]["file"] if segments and segments[0].get("has_audio") else None
        mux_t = self.build_audio_matrix(
            silent_path, master_mp3, opening_clip, lead_s, video_duration, final_video_path)

        size_mb = os.path.getsize(final_video_path) / (1024 * 1024)
        log("=" * 60)
        log(f"EXPORTED: {final_video_path}")
        log(f"Duration {video_duration / 60:.2f} min | Size {size_mb:.2f} MB")
        log(f"Render {render_t:.1f}s | Concat {concat_t:.1f}s | Mux {mux_t:.1f}s")
        log("=" * 60)

        benchmarks = {
            "total_segments": len(segments),
            "segments_rendered": len(ok),
            "segments_failed": len(failures),
            "resolution": f"{self.W}x{self.H}",
            "fps": self.fps,
            "encoder": self.encoder,
            "bitrate": self.bitrate,
            "fill_mode": self.look["fill_mode"],
            "voice_volume": self.vo_volume,
            "bgm": os.path.basename(self.bgm_path) if self.bgm_path else None,
            "bgm_volume": self.bgm_volume if self.bgm_path else None,
            "render_time_sec": round(render_t, 2),
            "concat_time_sec": round(concat_t, 2),
            "mux_time_sec": round(mux_t, 2),
            "final_duration_sec": round(video_duration, 2),
            "final_video_mb": round(size_mb, 2),
            "final_video_path": final_video_path,
        }
        with open(os.path.join(self.work_dir, "render_benchmarks.json"), "w",
                  encoding="utf-8") as f:
            json.dump(benchmarks, f, indent=2)
        return benchmarks
