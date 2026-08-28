"""
Pure GPU NVENC Hardware Accelerated Rendering Engine.
Renders zero-shake Ken Burns perspective motion, smog/film grain/vintage grading, and loud audio matrix ducking.
"""

import os, sys, time, json, subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed

W, H = 1920, 1080
FPS = 30
ZOOM_PER_SEC = 0.006
FADE_S = 0.25
FILM = "noise=alls=10:allf=t+u,gblur=sigma=1.2,eq=gamma=0.97:gamma_r=1.05:gamma_b=0.93:saturation=0.78:contrast=1.03"
POSTCARD_EQ = "eq=gamma_r=1.10:gamma_b=0.90:saturation=0.85:contrast=1.03"

class RenderEngine:
    def __init__(self, work_dir, bgm_path=None, workers=6):
        self.work_dir = work_dir
        self.bgm_path = bgm_path
        self.workers = workers
        self.segs_dir = os.path.join(work_dir, "segments")
        self.webp_cache = os.path.join(work_dir, "webp_cache")
        os.makedirs(self.segs_dir, exist_ok=True)
        os.makedirs(self.webp_cache, exist_ok=True)

    def to_png(self, img_path):
        if not img_path or not os.path.exists(img_path): return img_path
        if not img_path.lower().endswith(".webp"): return img_path
        bname = os.path.splitext(os.path.basename(img_path))[0]
        out_png = os.path.join(self.webp_cache, bname + ".png")
        if not os.path.exists(out_png) or os.path.getsize(out_png) == 0:
            subprocess.run(["ffmpeg", "-y", "-i", img_path, out_png], capture_output=True)
        return out_png

    def fades_str(self, dur):
        fo = max(0.0, dur - FADE_S)
        return f"fade=t=in:st=0:d={FADE_S},fade=t=out:st={fo:.4f}:d={FADE_S}"

    def kb_filter(self, mode, dur, postcard=False):
        n = int(dur * FPS)
        N1 = max(1, n - 1)
        z = ZOOM_PER_SEC * dur
        CW = round(W * (1 + z) / 16) * 16
        CH = (round(CW * H / W) // 2) * 2

        if mode == "zoomin":
            p = f"x0=0:y0=0:x1={CW}:y1=0:x2=0:y2={CH}:x3={CW}:y3={CH}:" \
                f"x0=0+{z}*{CW}/2*on/{N1}:y0=0+{z}*{CH}/2*on/{N1}:" \
                f"x1={CW}-{z}*{CW}/2*on/{N1}:y1=0+{z}*{CH}/2*on/{N1}:" \
                f"x2=0+{z}*{CW}/2*on/{N1}:y2={CH}-{z}*{CH}/2*on/{N1}:" \
                f"x3={CW}-{z}*{CW}/2*on/{N1}:y3={CH}-{z}*{CH}/2*on/{N1}"
        elif mode == "zoomout":
            p = f"x0=0+{z}*{CW}/2*(1-on/{N1}):y0=0+{z}*{CH}/2*(1-on/{N1}):" \
                f"x1={CW}-{z}*{CW}/2*(1-on/{N1}):y1=0+{z}*{CH}/2*(1-on/{N1}):" \
                f"x2=0+{z}*{CW}/2*(1-on/{N1}):y2={CH}-{z}*{CH}/2*(1-on/{N1}):" \
                f"x3={CW}-{z}*{CW}/2*(1-on/{N1}):y3={CH}-{z}*{CH}/2*(1-on/{N1})"
        elif mode == "panright":
            p = f"x0=0+{z}*{CW}*on/{N1}:y0=0:x1={CW}+{z}*{CW}*on/{N1}:y1=0:" \
                f"x2=0+{z}*{CW}*on/{N1}:y2={CH}:x3={CW}+{z}*{CW}*on/{N1}:y3={CH}"
        else:
            p = f"x0={z}*{CW}*(1-on/{N1}):y0=0:x1={CW}+{z}*{CW}*(1-on/{N1}):y1=0:" \
                f"x2={z}*{CW}*(1-on/{N1}):y2={CH}:x3={CW}+{z}*{CW}*(1-on/{N1}):y3={CH}"

        persp = f"perspective=eval=frame:sense=source:interpolation=linear:{p}"
        scale_in = f"scale={CW}:{CH}:force_original_aspect_ratio=decrease,pad={CW}:{CH}:trunc((ow-iw)/2):trunc((oh-ih)/2):black,setsar=1"
        scale_out = f"scale={W}:{H}:flags=bicubic,setsar=1"
        chain = [scale_in, persp, scale_out]
        if postcard: chain.append(POSTCARD_EQ)
        chain.append(FILM)
        chain.append(self.fades_str(dur))
        return ",".join(chain)

    def render_segment(self, seg):
        idx = seg["index"]
        out_file = os.path.join(self.segs_dir, f"seg_{idx:04d}.mp4")
        dur = seg["duration"]
        gpu_enc = ["-c:v", "h264_nvenc", "-preset", "p1", "-rc", "vbr", "-b:v", "2500k", "-maxrate", "3500k", "-bufsize", "5000k", "-pix_fmt", "yuv420p", "-r", str(FPS), "-an"]

        if seg["type"] in ["grid_image", "grid_clip", "headline"]:
            grid_src = self.to_png(seg.get("grid_file"))
            main_src = self.to_png(seg["file"]) if seg["type"] in ["image", "grid_image"] else seg["file"]
            if grid_src and os.path.exists(grid_src):
                fc = f"[0:v]scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080[bg]; " \
                     f"[1:v]scale=1650:928:force_original_aspect_ratio=decrease,pad=1650:928:(ow-iw)/2:(oh-ih)/2:black,drawbox=x=0:y=0:w=iw:h=ih:color=0xf5b300@0.95:t=4[fg]; " \
                     f"[bg][fg]overlay=135:76,{FILM},{self.fades_str(dur)}[outv]"
                if seg["type"] in ["grid_image", "image"]:
                    cmd = ["ffmpeg", "-y", "-loop", "1", "-framerate", str(FPS), "-t", str(dur), "-i", grid_src,
                           "-loop", "1", "-framerate", str(FPS), "-t", str(dur), "-i", main_src,
                           "-filter_complex", fc, "-map", "[outv]"] + gpu_enc + [out_file]
                else:
                    cmd = ["ffmpeg", "-y", "-loop", "1", "-framerate", str(FPS), "-t", str(dur), "-i", grid_src,
                           "-hwaccel", "cuda", "-ss", "0", "-t", str(dur), "-i", main_src,
                           "-filter_complex", fc, "-map", "[outv]"] + gpu_enc + [out_file]
            else:
                src = self.to_png(seg["file"])
                vf = self.kb_filter(seg.get("motion", "zoomin"), dur)
                cmd = ["ffmpeg", "-y", "-loop", "1", "-framerate", str(FPS), "-i", src, "-vf", vf, "-t", str(dur)] + gpu_enc + [out_file]
        elif seg["type"] == "image":
            src = self.to_png(seg["file"])
            vf = self.kb_filter(seg["motion"], dur, postcard=seg.get("postcard", False))
            cmd = ["ffmpeg", "-y", "-loop", "1", "-framerate", str(FPS), "-i", src, "-vf", vf, "-t", str(dur)] + gpu_enc + [out_file]
        elif seg["type"] == "clip":
            src = seg["file"]
            vf = f"scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:black,setsar=1,{FILM},{self.fades_str(dur)}"
            cmd = ["ffmpeg", "-y", "-hwaccel", "cuda", "-ss", "0", "-t", str(dur), "-i", src, "-vf", vf] + gpu_enc + [out_file]

        subprocess.run(cmd, capture_output=True)
        return idx, out_file

    def render_and_mux(self, timeline_json, master_voice_mp3, final_output_path):
        with open(timeline_json, "r", encoding="utf-8") as f:
            t_data = json.load(f)
        segments = t_data["segments"]

        with ThreadPoolExecutor(max_workers=self.workers) as executor:
            futures = {executor.submit(self.render_segment, s): s for s in segments}
            for _ in as_completed(futures): pass

        concat_txt = os.path.join(self.work_dir, "segments_concat.txt")
        silent_mp4 = os.path.join(self.work_dir, "video_silent.mp4")
        with open(concat_txt, "w", encoding="utf-8") as f:
            for s in segments:
                f.write(f"file '{os.path.join(self.segs_dir, f'seg_{s[\"index\"]:04d}.mp4').replace('\\', '/')}'\n")

        subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_txt, "-c", "copy", silent_mp4], capture_output=True, check=True)

        audio_inputs = ["-i", silent_mp4]
        filter_parts = []
        mix_sources = []
        opening_clip = segments[0]["file"] if segments else None
        if opening_clip and os.path.exists(opening_clip) and segments[0].get("has_audio"):
            audio_inputs.extend(["-ss", "0", "-t", "4.5", "-i", opening_clip])
            filter_parts.append(f"[1:a]volume=1.5,apad=whole_dur={int(t_data.get('total_duration', 1800))}[head_a]")
            mix_sources.append("[head_a]")
            vo_idx = 2
        else:
            vo_idx = 1

        audio_inputs.extend(["-i", master_voice_mp3])
        filter_parts.append(f"[{vo_idx}:a]adelay=4500|4500,volume=1.75[vo]")
        mix_sources.append("[vo]")
        bg_idx = vo_idx + 1

        if self.bgm_path and os.path.exists(self.bgm_path):
            audio_inputs.extend(["-stream_loop", "-1", "-i", self.bgm_path])
            filter_parts.append(f"[{bg_idx}:a]volume=0.08[bgm]")
            mix_sources.append("[bgm]")

        filter_parts.append(f"{''.join(mix_sources)}amix=inputs={len(mix_sources)}:duration=first:dropout_transition=3[aout]")
        final_cmd = ["ffmpeg", "-y"] + audio_inputs + [
            "-filter_complex", ";".join(filter_parts),
            "-map", "0:v", "-map", "[aout]",
            "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
            final_output_path
        ]
        subprocess.run(final_cmd, capture_output=True, check=True)
        return final_output_path
