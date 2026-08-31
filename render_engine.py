import os, sys, time, json, subprocess, glob
from concurrent.futures import ThreadPoolExecutor, as_completed

WORK_DIR = r"C:\Users\ninja\Downloads\Dolly Parton\video21_dolly_final_letter_children"
TIMELINE_FILE = os.path.join(WORK_DIR, "timeline.json")
SEGS_DIR = os.path.join(WORK_DIR, "segments")
WEBP_CACHE = os.path.join(WORK_DIR, "webp_cache")
MASTER_VOICE_MP3 = os.path.join(WORK_DIR, "voiceover.mp3")
OUTPUT_DIR = r"C:\Users\ninja\Downloads\Dolly Parton"
FINAL_VIDEO_PATH = os.path.join(OUTPUT_DIR, "Dolly Parton’s touching final message to children is going viral following her death at 80.mp4")

W, H = 1920, 1080
FPS = 30
ZOOM_PER_SEC = 0.015
FADE_S = 0.25
FILM_VISIBLE = "noise=alls=20:allf=t+u,vignette=PI/4,eq=gamma=0.96:gamma_r=1.08:gamma_b=0.92:saturation=0.88:contrast=1.08"
POSTCARD_EQ = "eq=gamma_r=1.12:gamma_b=0.88:saturation=0.82:contrast=1.10"

os.makedirs(SEGS_DIR, exist_ok=True)
os.makedirs(WEBP_CACHE, exist_ok=True)

def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)

def to_png(img_path):
    if not img_path or not os.path.exists(img_path): return img_path
    if not img_path.lower().endswith(".webp"): return img_path
    bname = os.path.splitext(os.path.basename(img_path))[0]
    out_png = os.path.join(WEBP_CACHE, bname + ".png")
    if not os.path.exists(out_png) or os.path.getsize(out_png) == 0:
        subprocess.run(["ffmpeg", "-y", "-i", img_path, out_png], capture_output=True)
    return out_png

def fades_str(dur):
    fo = max(0.0, dur - FADE_S)
    return f"fade=t=in:st=0:d={FADE_S},fade=t=out:st={fo:.4f}:d={FADE_S}"

def kb_filter(mode, dur, is_custom_graphic=False, postcard=False):
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
    
    if is_custom_graphic:
        chain.append("noise=alls=10:allf=t+u")
    else:
        if postcard: chain.append(POSTCARD_EQ)
        chain.append(FILM_VISIBLE)
        
    chain.append(fades_str(dur))
    return ",".join(chain)

def render_single_segment(seg):
    idx = seg["index"]
    out_file = os.path.join(SEGS_DIR, f"seg_{idx:04d}.mp4")
    dur = seg["duration"]
    st_t = time.time()
    
    gpu_enc = [
        "-c:v", "h264_nvenc", "-preset", "p1", "-rc", "vbr",
        "-b:v", "2500k", "-maxrate", "3500k", "-bufsize", "5000k",
        "-pix_fmt", "yuv420p", "-r", str(FPS), "-an"
    ]
    
    if seg["type"] == "headline":
        src = seg["file"]
        vf_head = f"scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:black,drawbox=x=0:y=0:w=iw:h=ih:color=0xdc2626@0.95:t=4,setsar=1,{FILM_VISIBLE},{fades_str(dur)}"
        cmd = ["ffmpeg", "-y", "-ss", "0", "-t", str(dur), "-i", src, "-vf", vf_head] + gpu_enc + [out_file]
    elif seg["type"] == "image":
        src = to_png(seg["file"])
        is_cg = (seg.get("section") == "custom_graphic")
        vf_img = kb_filter(seg["motion"], dur, is_custom_graphic=is_cg, postcard=seg.get("postcard", False))
        cmd = ["ffmpeg", "-y", "-loop", "1", "-framerate", str(FPS), "-i", src, "-vf", vf_img, "-t", str(dur)] + gpu_enc + [out_file]
    elif seg["type"] == "clip":
        src = seg["file"]
        vf_clip = f"scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:black,setsar=1,{FILM_VISIBLE},{fades_str(dur)}"
        cmd = ["ffmpeg", "-y", "-hwaccel", "cuda", "-ss", "0", "-t", str(dur), "-i", src, "-vf", vf_clip] + gpu_enc + [out_file]

    subprocess.run(cmd, capture_output=True)
    return idx, out_file, time.time() - st_t

def render_pipeline():
    with open(TIMELINE_FILE, "r", encoding="utf-8") as f:
        t_data = json.load(f)
    segments = t_data["segments"]

    log(f"============================================================")
    log(f"STARTING GPU NVENC RENDERING FOR VIDEO 21 ({len(segments)} segments)...")
    log(f"Topic: Dolly Parton’s touching final message to children is going viral following her death at 80")
    log(f"Voice ID: JBFqnCBsd6RMkjVDRZzb | Opening Hook: LIVE BREAKING DEATH NEWS SOUNDBITE")
    log(f"100% Curated Viral Letter & Dolly Imagery | 90+ Custom Graphics Embedded")
    log(f"High-Density Video Clips (Every 2-3 Segments) + Cancer & Death News Clips")
    log(f"Prominent Film Grain & Vignette | SUPER LOUD VO (2.5x) | NO BGM")
    log(f"============================================================")
    
    t_start = time.time()
    rendered_count = 0
    durations = []
    
    with ThreadPoolExecutor(max_workers=6) as executor:
        futures = {executor.submit(render_single_segment, s): s for s in segments}
        for future in as_completed(futures):
            idx, out_f, cost_t = future.result()
            rendered_count += 1
            durations.append(cost_t)
            if rendered_count % 50 == 0 or rendered_count == len(segments):
                avg_t = sum(durations) / max(1, len(durations))
                log(f"GPU Render: {rendered_count}/{len(segments)} segments completed (Avg {avg_t:.3f}s/seg).")

    total_render_t = time.time() - t_start
    log(f"All {rendered_count} segments rendered on GPU in {total_render_t:.2f}s! ({total_render_t/60:.2f} minutes).")

    log("Concatenating all segments into video_silent.mp4...")
    concat_txt = os.path.join(WORK_DIR, "segments_concat.txt")
    silent_mp4 = os.path.join(WORK_DIR, "video_silent.mp4")
    
    with open(concat_txt, "w", encoding="utf-8") as f:
        for seg in segments:
            idx = seg["index"]
            seg_p = os.path.join(SEGS_DIR, f"seg_{idx:04d}.mp4").replace("\\", "/")
            f.write(f"file '{seg_p}'\n")
            
    t_concat_start = time.time()
    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", concat_txt, "-c", "copy", silent_mp4
    ], capture_output=True, check=True)
    concat_t = time.time() - t_concat_start

    probe = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration,size", "-of", "json", silent_mp4], capture_output=True, text=True)
    try: total_vid_dur = float(json.loads(probe.stdout)["format"]["duration"])
    except: total_vid_dur = 2000.0

    log("Building Multi-Track Audio Matrix (Opening Soundbite + SUPER LOUD VO 2.5x + NO BGM)...")
    t_mux_start = time.time()
    
    opening_clip = segments[0]["file"] if segments else None
    audio_inputs = ["-i", silent_mp4]
    filter_parts = []
    mix_sources = []
    
    if opening_clip and os.path.exists(opening_clip) and segments[0].get("has_audio"):
        audio_inputs.extend(["-ss", "0", "-t", "4.5", "-i", opening_clip])
        filter_parts.append(f"[1:a]volume=1.8,apad=whole_dur={int(total_vid_dur)}[head_a]")
        mix_sources.append("[head_a]")
        vo_idx = 2
    else:
        vo_idx = 1
        
    audio_inputs.extend(["-i", MASTER_VOICE_MP3])
    filter_parts.append(f"[{vo_idx}:a]adelay=4500|4500,volume=2.5[vo]")
    mix_sources.append("[vo]")
    
    if len(mix_sources) > 1:
        filter_parts.append(f"{''.join(mix_sources)}amix=inputs={len(mix_sources)}:duration=first:dropout_transition=3[aout]")
        filter_complex = ";".join(filter_parts)
        final_cmd = ["ffmpeg", "-y"] + audio_inputs + [
            "-filter_complex", filter_complex,
            "-map", "0:v", "-map", "[aout]",
            "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
            FINAL_VIDEO_PATH
        ]
    else:
        filter_complex = ";".join(filter_parts)
        final_cmd = ["ffmpeg", "-y"] + audio_inputs + [
            "-filter_complex", filter_complex,
            "-map", "0:v", "-map", "[vo]",
            "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
            FINAL_VIDEO_PATH
        ]
    
    log(f"Muxing final production video to {FINAL_VIDEO_PATH}...")
    subprocess.run(final_cmd, capture_output=True, check=True)
    mux_t = time.time() - t_mux_start
    
    final_sz_mb = os.path.getsize(FINAL_VIDEO_PATH) / (1024 * 1024)
    log(f"============================================================")
    log(f"VIDEO 21 EXPORTED SUCCESSFULLY ON GPU!")
    log(f"Path: {FINAL_VIDEO_PATH}")
    log(f"Size: {final_sz_mb:.2f} MB")
    log(f"Mux Time: {mux_t:.2f}s | Total Render Time: {total_render_t + concat_t + mux_t:.2f}s")
    log(f"============================================================")

    with open(os.path.join(WORK_DIR, "render_benchmarks.json"), "w", encoding="utf-8") as f:
        json.dump({
            "total_segments": len(segments),
            "encoder": "h264_nvenc (NVIDIA GPU)",
            "bitrate": "VBR 2500k",
            "voice_volume_boost": "2.5x (Super Loud)",
            "background_music": "None (Vocals Only)",
            "total_render_time_sec": total_render_t,
            "concat_time_sec": concat_t,
            "mux_time_sec": mux_t,
            "final_video_mb": final_sz_mb,
            "final_video_path": FINAL_VIDEO_PATH
        }, f, indent=2)

if __name__ == "__main__":
    render_pipeline()
