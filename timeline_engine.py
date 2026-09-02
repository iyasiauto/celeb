"""
Semantic Asset & Dynamic Timeline Engine.

Builds a segment timeline (JSON) that fills the master voiceover duration with a
mix of video clips, curated photographs and generated graphic cards.

All topic-specific content (card captions, keyword-matched clip groups, hook
assets) comes from a topic config dict, so the same engine drives any subject.
"""

import os
import json
import glob
import time
import random
import subprocess
from collections import Counter
from concurrent.futures import ThreadPoolExecutor

from PIL import Image

from graphic_compositor import GraphicCompositor
from semantic_matcher import (AssetIndex, ScriptTimeline, SemanticMatcher,
                              folder_entity, load_tags)

VIDEO_EXTS = (".mp4", ".mov", ".mkv", ".webm", ".m4v")
IMAGE_EXTS = (".jpg", ".jpeg", ".png", ".webp", ".bmp")
DEFAULT_EXCLUDE = ("watermark", "getty", "alamy", "stock")


def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def get_duration(media_file):
    """Return media duration in seconds, or 0.0 if it cannot be probed."""
    res = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", media_file],
        capture_output=True, text=True)
    try:
        return float(res.stdout.strip())
    except ValueError:
        return 0.0


def _as_dir_list(value):
    """Accept a single path, a list of paths, or an os.pathsep-joined string."""
    if not value:
        return []
    if isinstance(value, (list, tuple)):
        dirs = list(value)
    else:
        dirs = value.split(os.pathsep) if os.pathsep in value else [value]
    return [d for d in (p.strip() for p in dirs) if d and os.path.isdir(d)]


class TimelineEngine:
    """Builds a documentary timeline from a pool of clips, photos and grids."""

    def __init__(self, clips_dir, images_dir, grid_dir,
                 topic_assets_dir=None, graphics_dir=None, topic_config=None,
                 opening_lead_s=4.5, hook_end_s=22.5,
                 seg_min_s=4.5, seg_max_s=5.8,
                 clip_cooldown=15, max_images=350, hook_count=7,
                 asset_seed=1515, curate_seed=999, scan_workers=32,
                 semantic=True, script_text=None, voice_manifest=None,
                 asset_tags=None, entity_boost=6.0,
                 width=1920, height=1080):
        self.clips_dirs = _as_dir_list(clips_dir)
        self.images_dirs = _as_dir_list(images_dir)
        self.grid_dirs = _as_dir_list(grid_dir)
        self.topic_assets_dir = (topic_assets_dir
                                 if topic_assets_dir and os.path.isdir(topic_assets_dir)
                                 else None)
        self.graphics_dir = graphics_dir
        self.cfg = dict(topic_config or {})

        self.opening_lead_s = float(opening_lead_s)
        self.hook_end_s = float(hook_end_s)
        self.seg_min_s = float(seg_min_s)
        self.seg_max_s = float(seg_max_s)
        self.clip_cooldown = int(clip_cooldown)
        self.max_images = int(max_images)
        self.hook_count = int(hook_count)
        self.asset_seed = asset_seed
        self.curate_seed = curate_seed
        self.scan_workers = int(scan_workers)

        self.exclude_keywords = tuple(
            k.lower() for k in self.cfg.get("exclude_keywords", DEFAULT_EXCLUDE))

        # Quality floors. They keep thumbnails and broken downloads out of a
        # documentary, but a legitimately small library must be able to lower
        # them rather than be told nothing was found.
        self.min_image_bytes = int(self.cfg.get("min_image_bytes", 18000))
        self.min_image_px = int(self.cfg.get("min_image_px", 300))
        self.min_clip_bytes = int(self.cfg.get("min_clip_bytes", 200000))

        self.width = int(width)
        self.height = int(height)
        self.semantic = bool(semantic)
        self.script_text = script_text
        self.voice_manifest = voice_manifest
        self.asset_tags = asset_tags or {}
        self.entity_boost = float(entity_boost)
        self.matcher = None

    # ------------------------------------------------------------- semantics

    def _entity_dirs(self):
        """Directories whose folder name identifies who or what is depicted."""
        pairs = []
        for entity, path in (self.cfg.get("entity_dirs") or {}).items():
            if os.path.isdir(path):
                pairs.append((entity.lower(), path))

        root = self.cfg.get("entity_root")
        if root and os.path.isdir(root):
            skip = {s.lower() for s in self.cfg.get("entity_root_skip", [])}
            owned = {os.path.normcase(os.path.abspath(d))
                     for d in self.clips_dirs + self.images_dirs + self.grid_dirs}
            for name in sorted(os.listdir(root)):
                path = os.path.join(root, name)
                if not os.path.isdir(path) or name.lower() in skip:
                    continue
                if os.path.normcase(os.path.abspath(path)) in owned:
                    continue
                entity = folder_entity(path)
                if entity:
                    pairs.append((entity, path))
        return pairs

    def build_matcher(self, vo_duration, lead):
        """Index every labelled asset and align the script to wall-clock time."""
        index = AssetIndex()
        default_entity = (self.cfg.get("default_entity") or "").lower() or None

        # An asset directory is either a generic pool (label everything with the
        # documentary's own subject) or a subject folder (label by folder name).
        # Getting this wrong collapses every folder into one entity and silently
        # disables folder-based matching, so it is stated explicitly in config.
        declared = self.cfg.get("generic_dirs")
        if declared is None:
            generic = None          # legacy: treat every asset dir as generic
        else:
            generic = {os.path.normcase(os.path.abspath(d))
                       for d in _as_dir_list(declared)}

        def label_for(d):
            if generic is None or os.path.normcase(os.path.abspath(d)) in generic:
                return default_entity
            return folder_entity(d) or default_entity

        for d in self.images_dirs:
            index.add_dir(d, "image", entity=label_for(d))
        for d in self.clips_dirs:
            index.add_dir(d, "clip", entity=label_for(d))

        entity_pairs = self._entity_dirs()
        for entity, path in entity_pairs:
            index.add_dir(path, "image", entity=entity)
            index.add_dir(path, "clip", entity=entity)

        applied = index.apply_tags(self.asset_tags)
        index.build_idf()

        if self.voice_manifest:
            script = ScriptTimeline.from_manifest(self.voice_manifest, lead=lead)
            source = "voiceover manifest (exact chunk timing)"
        elif self.script_text:
            script = ScriptTimeline.from_text(self.script_text, vo_duration, lead=lead)
            source = "proportional estimate from script"
        else:
            log("Semantic matching disabled: no script text or voice manifest.")
            return None

        stats = index.stats()
        log(f"Semantic index: {stats['total']} assets "
            f"({stats['images']} images, {stats['clips']} clips), "
            f"{stats['entities']} entities, {stats['describable']} with usable terms.")
        if applied:
            log(f"Applied {applied} tag entries from the asset tags file.")
        log(f"Script alignment: {len(script.spans)} spans from {source}.")

        return SemanticMatcher(index, script, entity_boost=self.entity_boost,
                               cooldown=self.clip_cooldown,
                               default_entity=default_entity)

    # ---------------------------------------------------------------- assets

    def _validate_photo(self, path):
        """Return the path, or a short reason the photo was rejected."""
        try:
            if os.path.getsize(path) < self.min_image_bytes:
                return "too small on disk (<%d bytes)" % self.min_image_bytes
            with Image.open(path) as im:
                w, h = im.size
                if w < self.min_image_px or h < self.min_image_px:
                    return "below %dpx" % self.min_image_px
                im.verify()
            with Image.open(path) as im:
                im.convert("RGB")
            return path
        except Exception as e:
            return "unreadable (%s)" % type(e).__name__

    def _validate_grid(self, path):
        try:
            if os.path.getsize(path) < 4000:
                return None
            with Image.open(path) as im:
                im.verify()
            with Image.open(path) as im:
                im.convert("RGB")
            return path
        except Exception:
            return None

    def _validate_clip(self, path):
        """Return a clip record, or a short reason it was rejected."""
        try:
            if os.path.getsize(path) < self.min_clip_bytes:
                return "too small on disk (<%d bytes)" % self.min_clip_bytes
            name = os.path.basename(path).lower()
            hit = next((k for k in self.exclude_keywords if k in name), None)
            if hit:
                return "excluded by keyword %r" % hit
            return {"path": path,
                    "has_audio": False,
                    "source_id": os.path.basename(path).split("_")[0]}
        except OSError as e:
            return "unreadable (%s)" % type(e).__name__

    def _scan(self, dirs, exts):
        found = []
        for d in dirs:
            for entry in glob.glob(os.path.join(d, "*.*")):
                if entry.lower().endswith(exts):
                    found.append(entry)
        return found

    def collect_assets(self):
        """Scan and validate every asset pool. Returns (images, grids, clips)."""
        raw_images = self._scan(self.images_dirs, IMAGE_EXTS)
        raw_grids = self._scan(self.grid_dirs, IMAGE_EXTS)
        raw_clips = self._scan(self.clips_dirs, VIDEO_EXTS)

        with ThreadPoolExecutor(max_workers=self.scan_workers) as pool:
            img_results = list(pool.map(self._validate_photo, raw_images))
            grids = [g for g in pool.map(self._validate_grid, raw_grids) if g]
            clip_results = list(pool.map(self._validate_clip, raw_clips))

        raw_image_set = set(raw_images)
        images = [r for r in img_results if r in raw_image_set]
        clips = [r for r in clip_results if isinstance(r, dict)]

        rejects = Counter(r for r in img_results if r not in raw_image_set)
        rejects.update(r for r in clip_results if isinstance(r, str))

        log(f"Assets validated: {len(images)} photos, {len(grids)} grids, {len(clips)} clips.")
        if rejects:
            summary = ", ".join(f"{n} {why}" for why, n in rejects.most_common(4))
            log(f"Rejected {sum(rejects.values())} files: {summary}")

        if not images and not clips:
            found = len(raw_images) + len(raw_clips)
            if found:
                # Reporting "nothing found" when the filters threw everything
                # away sends you looking in entirely the wrong place.
                detail = "; ".join(f"{n} {why}" for why, n in rejects.most_common())
                raise RuntimeError(
                    f"Found {found} media files but none passed validation: {detail}. "
                    f"Lower min_image_bytes / min_image_px / min_clip_bytes in the "
                    f"topic config if these files are genuinely usable.")
            raise RuntimeError(
                f"No media files found at all. Scanned {len(self.images_dirs)} image "
                f"and {len(self.clips_dirs)} clip directories - check --images-dir "
                f"and --clips-dir.")
        return images, grids, clips

    def curate_images(self, images):
        """Shuffle deterministically and weight topic assets more heavily."""
        topic_files = []
        if self.topic_assets_dir:
            topic_files = self._scan([self.topic_assets_dir], IMAGE_EXTS)

        random.seed(self.asset_seed)
        pool = list(images)
        random.shuffle(pool)

        weight = int(self.cfg.get("topic_asset_weight", 8))
        curated = topic_files * weight + pool[:self.max_images]
        if not curated:
            raise RuntimeError("No usable photographs after validation.")

        random.seed(self.curate_seed)
        random.shuffle(curated)
        return curated, topic_files

    def group_clips(self, clips, opening_clip):
        """Split clips into the generic pool plus keyword-matched groups."""
        groups = {g["name"]: [] for g in self.cfg.get("clip_groups", [])}
        generic = []

        for c in clips:
            if opening_clip and os.path.abspath(c["path"]) == os.path.abspath(opening_clip):
                continue
            name = os.path.basename(c["path"]).lower()
            for g in self.cfg.get("clip_groups", []):
                if any(k.lower() in name for k in g.get("keywords", [])):
                    groups[g["name"]].append(c)
                    break
            else:
                generic.append(c)

        random.seed(self.asset_seed)
        random.shuffle(generic)
        for name in groups:
            random.shuffle(groups[name])
        return generic, groups

    # -------------------------------------------------------------- graphics

    def generate_graphics(self, curated, grids):
        """Pre-render the graphic cards described by the topic config."""
        if not self.graphics_dir:
            return []
        os.makedirs(self.graphics_dir, exist_ok=True)

        made = []
        img_i = 0
        grid_i = 0

        def next_img():
            nonlocal img_i
            p = curated[img_i % len(curated)]
            img_i += 1
            return p

        def next_grid():
            nonlocal grid_i
            if not grids:
                return None
            g = grids[grid_i % len(grids)]
            grid_i += 1
            return g

        def safe(prefix, text, i):
            slug = "".join(ch if ch.isalnum() else "_" for ch in text.lower())[:28].strip("_")
            return os.path.join(self.graphics_dir, f"{prefix}_{i:02d}_{slug or 'card'}.jpg")

        for i, item in enumerate(self.cfg.get("split_cards", [])):
            grid = next_grid()
            if not grid:
                break
            if isinstance(item, (list, tuple)):
                title = item[0] if len(item) > 0 else ""
                subtitle = item[1] if len(item) > 1 else ""
            else:
                title, subtitle = str(item), ""
            out = safe("split", title, i)
            try:
                GraphicCompositor.style3_split_typography_card(
                    next_img(), grid, title, subtitle, out,
                    width=self.width, height=self.height)
                made.append(out)
            except Exception as e:
                log(f"  split card '{title}' failed: {e}")

        for i, text in enumerate(self.cfg.get("headlines", [])):
            out = safe("headline", text, i)
            try:
                GraphicCompositor.style4_centered_headline(
                    next_img(), text, out, width=self.width, height=self.height)
                made.append(out)
            except Exception as e:
                log(f"  headline '{text[:24]}' failed: {e}")

        for i, text in enumerate(self.cfg.get("quotes", [])):
            out = safe("quote", text, i)
            try:
                GraphicCompositor.style5_quote_caption(
                    next_img(), text, out, width=self.width, height=self.height)
                made.append(out)
            except Exception as e:
                log(f"  quote '{text[:24]}' failed: {e}")

        for i in range(int(self.cfg.get("triptych_count", 18))):
            out = os.path.join(self.graphics_dir, f"triptych_{i + 1:02d}.jpg")
            bg = curated[img_i % len(curated)]
            three = [curated[(img_i + k) % len(curated)] for k in (1, 2, 3)]
            try:
                GraphicCompositor.style2_triptych_overlay(
                    bg, three, out, width=self.width, height=self.height)
                made.append(out)
            except Exception as e:
                log(f"  triptych {i + 1} failed: {e}")
            img_i += 4

        if grids:
            for i in range(int(self.cfg.get("grid_card_count", 30))):
                out = os.path.join(self.graphics_dir, f"grid_card_{i + 1:02d}.jpg")
                try:
                    GraphicCompositor.style1_rounded_card_on_grid(
                        next_img(), next_grid(), out,
                        width=self.width, height=self.height)
                    made.append(out)
                except Exception as e:
                    log(f"  grid card {i + 1} failed: {e}")

        log(f"Generated {len(made)} graphic cards into {self.graphics_dir}")
        return made

    # -------------------------------------------------------------- timeline

    def _resolve_hook_assets(self, curated, graphics, topic_files):
        """Config-named hook assets first, then topic photos, graphics, curated."""
        resolved = []
        for entry in self.cfg.get("hook_assets", []):
            cand = entry
            if not os.path.isabs(cand) and self.topic_assets_dir:
                cand = os.path.join(self.topic_assets_dir, entry)
            if os.path.exists(cand):
                resolved.append(cand)

        fillers = list(topic_files) + list(graphics) + list(curated)
        fi = 0
        while len(resolved) < self.hook_count and fi < len(fillers):
            if fillers[fi] not in resolved:
                resolved.append(fillers[fi])
            fi += 1
        return resolved[:self.hook_count]

    def build_timeline(self, vo_duration, opening_clip, out_path):
        """Build the full segment list and write it to out_path as JSON."""
        vo_duration = float(vo_duration)
        images, grids, clips = self.collect_assets()
        curated, topic_files = self.curate_images(images)

        has_opening = bool(opening_clip and os.path.exists(opening_clip))
        if opening_clip and not has_opening:
            log(f"WARNING: opening clip not found, skipping: {opening_clip}")
        lead = self.opening_lead_s if has_opening else 0.0

        generic_clips, clip_groups = self.group_clips(
            clips, opening_clip if has_opening else None)
        graphics = self.generate_graphics(curated, grids)

        self.matcher = self.build_matcher(vo_duration, lead) if self.semantic else None
        if self.matcher and has_opening:
            self.matcher.used_paths.add(opening_clip)

        segments = []
        seg_idx = 0
        current = 0.0
        used_paths = set()
        used_sources = {}
        group_cursors = {name: 0 for name in clip_groups}
        img_cursor = 0
        cg_cursor = 0
        motions = ["zoomin", "zoomout", "panright", "panleft"]

        random.seed(self.asset_seed)

        # Segment 0 - opening soundbite, keeps its native audio.
        if has_opening:
            segments.append({
                "index": 0, "start": 0.0, "end": lead, "duration": lead,
                "type": "headline", "file": opening_clip, "motion": "none",
                "postcard": False, "has_audio": True, "section": "opening_soundbite",
            })
            current = lead
            seg_idx = 1

        # Fast hook - front-loaded curated assets up to hook_end_s.
        hook_assets = self._resolve_hook_assets(curated, graphics, topic_files)
        if hook_assets and self.hook_end_s > current:
            remaining = len(hook_assets)
            for asset in hook_assets:
                if current >= self.hook_end_s:
                    break
                dur = round((self.hook_end_s - current) / max(1, remaining), 2)
                dur = max(dur, 2.0)
                if current + dur > self.hook_end_s:
                    dur = round(self.hook_end_s - current, 2)
                if dur < 1.0:
                    break
                segments.append({
                    "index": seg_idx, "start": round(current, 2),
                    "end": round(current + dur, 2), "duration": dur,
                    "type": "image", "file": asset, "motion": random.choice(motions),
                    "postcard": False, "has_audio": False, "section": "fast_hook",
                })
                current = round(current + dur, 2)
                seg_idx += 1
                remaining -= 1

        def pick_clip(at_index, start, end):
            """Semantic pick when available, else cooldown-ordered round robin."""
            if self.matcher:
                asset, _score, _ents = self.matcher.pick(start, end, "clip", at_index)
                if asset:
                    return {"path": asset.path, "has_audio": False,
                            "source_id": asset.source_id}
            for c in generic_clips:
                if c["path"] in used_paths:
                    continue
                last = used_sources.get(c["source_id"], -10 ** 9)
                if at_index - last >= self.clip_cooldown:
                    used_paths.add(c["path"])
                    used_sources[c["source_id"]] = at_index
                    return c
            for c in generic_clips:
                if c["path"] not in used_paths:
                    used_paths.add(c["path"])
                    used_sources[c["source_id"]] = at_index
                    return c
            return None

        def group_for(t, index):
            """Return the keyword clip group whose time window covers t."""
            if index % 2 != 0:
                return None
            for g in self.cfg.get("clip_groups", []):
                name = g["name"]
                pool = clip_groups.get(name) or []
                if not pool or group_cursors[name] >= len(pool):
                    continue
                if float(g.get("start", 0)) <= t <= float(g.get("end", 0)):
                    return g
            return None

        target = vo_duration + lead

        while current < target:
            dur = round(random.uniform(self.seg_min_s, self.seg_max_s), 2)
            if current + dur > target:
                dur = round(target - current, 2)
                if dur < 1.0 and segments:
                    segments[-1]["duration"] = round(segments[-1]["duration"] + dur, 2)
                    segments[-1]["end"] = round(target, 2)
                    break

            def add_image(section, postcard):
                nonlocal img_cursor
                img = None
                if self.matcher:
                    asset, _score, _ents = self.matcher.pick(
                        current, current + dur, "image", seg_idx)
                    if asset:
                        img = asset.path
                if img is None:
                    img = curated[img_cursor % len(curated)]
                    img_cursor += 1
                segments.append({
                    "index": seg_idx, "start": round(current, 2),
                    "end": round(current + dur, 2), "duration": dur,
                    "type": "image", "file": img, "motion": random.choice(motions),
                    "postcard": postcard, "has_audio": False, "section": section,
                })

            group = group_for(current, seg_idx)
            if group:
                name = group["name"]
                c = clip_groups[name][group_cursors[name]]
                group_cursors[name] += 1
                segments.append({
                    "index": seg_idx, "start": round(current, 2),
                    "end": round(current + dur, 2), "duration": dur,
                    "type": "clip", "file": c["path"], "motion": "none",
                    "postcard": False, "has_audio": False, "section": name,
                })
            elif seg_idx % 2 == 0:
                c = pick_clip(seg_idx, current, current + dur)
                if c:
                    segments.append({
                        "index": seg_idx, "start": round(current, 2),
                        "end": round(current + dur, 2), "duration": dur,
                        "type": "clip", "file": c["path"], "motion": "none",
                        "postcard": False, "has_audio": False,
                        "section": "documentary_clip",
                    })
                else:
                    add_image("body", seg_idx % 5 == 0)
            elif seg_idx % 3 == 0 and graphics:
                segments.append({
                    "index": seg_idx, "start": round(current, 2),
                    "end": round(current + dur, 2), "duration": dur,
                    "type": "image", "file": graphics[cg_cursor % len(graphics)],
                    "motion": "zoomout", "postcard": False, "has_audio": False,
                    "section": "custom_graphic",
                })
                cg_cursor += 1
            else:
                add_image("body", seg_idx % 5 == 0)

            current = round(current + dur, 2)
            seg_idx += 1

        counts = {}
        for s in segments:
            counts[s["type"]] = counts.get(s["type"], 0) + 1

        data = {
            "total_duration": round(current, 2),
            "voiceover_duration": vo_duration,
            "opening_lead_s": lead,
            "segment_count": len(segments),
            "type_counts": counts,
            "custom_graphics_used": cg_cursor,
            "graphics_available": len(graphics),
            "semantic": bool(self.matcher),
            "segments": segments,
        }

        if self.matcher:
            cov = self.matcher.coverage()
            data["semantic_coverage"] = cov
            slots = cov["named_subject_slots"]
            log(f"Semantic picks: {cov['picks']} ({cov['scored']} scored on real terms)")
            if slots:
                reachable = cov["named_correct"] + cov["named_missed_despite_available"]
                pct = 100 * cov["named_correct"] / max(1, reachable)
                log(f"Named-subject slots: {slots} | right person shown "
                    f"{cov['named_correct']}/{reachable} ({pct:.0f}% of slots where "
                    f"they were available) | {cov['named_none_left_to_show']} had "
                    f"none left in the library")
                log(f"Wrong person shown: {cov['wrong_person_shown']} "
                    f"({100 * cov['wrong_person_shown'] / max(1, slots):.1f}% of "
                    f"named-subject slots)")
            with open(os.path.splitext(out_path)[0] + "_matches.json", "w",
                      encoding="utf-8") as f:
                json.dump(self.matcher.match_log, f, indent=2)

        os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        log(f"Timeline: {len(segments)} segments, {current / 60:.2f} min, types={counts}")
        log(f"Saved timeline to {out_path}")
        return data
