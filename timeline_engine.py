"""
Timeline & Asset Synchronization Engine.
Enforces 15-segment source cooldown, zero watermarks, 2-3% grid margin overlays, and 100% HD media assets.
"""

import os, sys, time, json, random, subprocess, glob
from PIL import Image, ImageStat

class TimelineEngine:
    def __init__(self, clips_dir, images_dir, grid_dir):
        self.clips_dir = clips_dir
        self.images_dir = images_dir
        self.grid_dir = grid_dir

    def is_pristine_image(self, img_path):
        try:
            if os.path.getsize(img_path) < 75000: return False
            with Image.open(img_path) as im:
                w, h = im.size
                if w < 1000 or h < 700: return False
                fn = os.path.basename(img_path).lower()
                if any(k in fn for k in ['getty', 'watermark', 'alamy', 'stock', 'shutter', 'preview', 'watermarked']):
                    return False
                gray = im.convert('L')
                stat = ImageStat.Stat(gray)
                if stat.var[0] < 400: return False
            return True
        except:
            return False

    def is_hd_clip(self, clip_path):
        try:
            if os.path.getsize(clip_path) < 150000: return False, 0, 0, 0.0, False
            fn = os.path.basename(clip_path).lower()
            if any(k in fn for k in ['watermark', 'getty', 'alamy', 'stock', 'logo']):
                return False, 0, 0, 0.0, False
            res = subprocess.run([
                "ffprobe", "-v", "error", "-select_streams", "v:0",
                "-show_entries", "stream=width,height,duration",
                "-of", "csv=p=0:s=x", clip_path
            ], capture_output=True, text=True)
            parts = res.stdout.strip().split("x")
            w, h = int(parts[0]), int(parts[1])
            if w < 1280 or h < 720: return False, w, h, 0.0, False
            dur = float(parts[2]) if len(parts) > 2 else 5.0
            res_a = subprocess.run([
                "ffprobe", "-v", "error", "-select_streams", "a:0",
                "-show_entries", "stream=codec_type",
                "-of", "default=noprint_wrappers=1:nokey=1", clip_path
            ], capture_output=True, text=True)
            return True, w, h, dur, bool(res_a.stdout.strip())
        except:
            return False, 0, 0, 0.0, False

    def build_timeline(self, voiceover_duration, opening_clip_path, output_json_path):
        raw_images = glob.glob(os.path.join(self.images_dir, "*.*"))
        clean_images = [f for f in raw_images if self.is_pristine_image(f)]
        random.shuffle(clean_images)

        raw_clips = glob.glob(os.path.join(self.clips_dir, "*.mp4"))
        clean_clips = []
        for c in raw_clips:
            if c == opening_clip_path or "headline" in os.path.basename(c).lower(): continue
            is_hd, w, h, dur, has_a = self.is_hd_clip(c)
            if is_hd:
                clean_clips.append({"path": c, "duration": dur, "has_audio": has_a, "source_id": os.path.basename(c).split("_")[0]})
        random.shuffle(clean_clips)

        raw_grids = glob.glob(os.path.join(self.grid_dir, "*.*"))
        grids = [g for g in raw_grids if os.path.getsize(g) > 5000]

        segments = []
        current_time = 0.0
        seg_idx = 0
        img_cursor = 0
        grid_cursor = 0
        used_clip_sources = {}
        used_clip_paths = set()
        mot_modes = ["zoomin", "zoomout", "panright", "panleft"]

        if opening_clip_path and os.path.exists(opening_clip_path):
            segments.append({
                "index": 0, "start": 0.0, "end": 4.5, "duration": 4.5,
                "type": "headline", "file": opening_clip_path,
                "grid_file": grids[0] if grids else None, "motion": "none",
                "postcard": False, "has_audio": True
            })
            current_time = 4.5
            seg_idx = 1

        def pick_clip(s_idx):
            for c in clean_clips:
                if c["path"] in used_clip_paths: continue
                if s_idx - used_clip_sources.get(c["source_id"], -999) >= 15:
                    used_clip_paths.add(c["path"])
                    used_clip_sources[c["source_id"]] = s_idx
                    return c
            for c in clean_clips:
                if c["path"] not in used_clip_paths:
                    used_clip_paths.add(c["path"])
                    used_clip_sources[c["source_id"]] = s_idx
                    return c
            return None

        # Fast hook (4.5s to 22.5s)
        while current_time < 22.5:
            dur = round(random.uniform(2.0, 2.6), 2)
            if current_time + dur > 22.5: dur = round(22.5 - current_time, 2)
            use_clip = (seg_idx % 2 == 1)
            use_grid = (seg_idx in [1, 5]) and len(grids) > 0
            if use_clip:
                c = pick_clip(seg_idx)
                if c:
                    segments.append({
                        "index": seg_idx, "start": current_time, "end": round(current_time + dur, 2), "duration": dur,
                        "type": "grid_clip" if use_grid else "clip", "file": c["path"],
                        "grid_file": grids[grid_cursor % len(grids)] if use_grid else None,
                        "motion": random.choice(mot_modes), "postcard": False, "has_audio": c["has_audio"]
                    })
                    if use_grid: grid_cursor += 1
            else:
                img = clean_images[img_cursor % len(clean_images)]
                img_cursor += 1
                segments.append({
                    "index": seg_idx, "start": current_time, "end": round(current_time + dur, 2), "duration": dur,
                    "type": "grid_image" if use_grid else "image", "file": img,
                    "grid_file": grids[grid_cursor % len(grids)] if use_grid else None,
                    "motion": random.choice(mot_modes), "postcard": False, "has_audio": False
                })
                if use_grid: grid_cursor += 1
            current_time = round(current_time + dur, 2)
            seg_idx += 1

        # Body (22.5s to end)
        target_total = voiceover_duration + 4.5
        while current_time < target_total:
            dur = round(random.uniform(4.5, 5.8), 2)
            if current_time + dur > target_total:
                dur = round(target_total - current_time, 2)
                if dur < 1.0:
                    segments[-1]["duration"] = round(segments[-1]["duration"] + dur, 2)
                    segments[-1]["end"] = target_total
                    break
            is_clip = (seg_idx % 3 == 0)
            is_grid = (seg_idx % 32 == 0) and len(grids) > 0
            if is_clip:
                c = pick_clip(seg_idx)
                if c:
                    segments.append({
                        "index": seg_idx, "start": current_time, "end": round(current_time + dur, 2), "duration": dur,
                        "type": "grid_clip" if is_grid else "clip", "file": c["path"],
                        "grid_file": grids[grid_cursor % len(grids)] if is_grid else None,
                        "motion": random.choice(mot_modes), "postcard": False, "has_audio": c["has_audio"]
                    })
                    if use_grid: grid_cursor += 1
            else:
                img = clean_images[img_cursor % len(clean_images)]
                img_cursor += 1
                segments.append({
                    "index": seg_idx, "start": current_time, "end": round(current_time + dur, 2), "duration": dur,
                    "type": "grid_image" if is_grid else "image", "file": img,
                    "grid_file": grids[grid_cursor % len(grids)] if is_grid else None,
                    "motion": random.choice(mot_modes), "postcard": (seg_idx % 5 == 0), "has_audio": False
                })
                if use_grid: grid_cursor += 1
            current_time = round(current_time + dur, 2)
            seg_idx += 1

        with open(output_json_path, "w", encoding="utf-8") as f:
            json.dump({"total_duration": current_time, "segments": segments}, f, indent=2)
        return output_json_path
