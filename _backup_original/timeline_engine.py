import os, sys, time, json, random, subprocess, glob
from PIL import Image
from concurrent.futures import ThreadPoolExecutor

WORK_DIR = r"C:\Users\ninja\Downloads\Dolly Parton\video21_dolly_final_letter_children"
TOPIC_ASSETS = os.path.join(WORK_DIR, "topic_assets")
MASTER_CLIPS_DIR = r"C:\Users\ninja\Downloads\Dolly Parton\dolly clips"
CLIPS_DIR = r"C:\Users\ninja\Downloads\Dolly Parton\clips"
IMAGES_DIR = r"C:\Users\ninja\Downloads\Dolly Parton\Real images data"
GRID_DIR = r"C:\Users\ninja\Downloads\Dolly Parton\gird-pattern-background-design"
MASTER_VOICE_MP3 = os.path.join(WORK_DIR, "voiceover.mp3")
TIMELINE_FILE = os.path.join(WORK_DIR, "timeline.json")
GRAPHICS_DIR = os.path.join(WORK_DIR, "generated_graphics")
os.makedirs(GRAPHICS_DIR, exist_ok=True)

sys.path.append(r"C:\Users\ninja\Downloads\MASTER_YOUTUBE_DOCUMENTARY_PIPELINE")
from graphic_compositor import GraphicCompositor

def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)

def quick_valid_photo(p):
    try:
        if os.path.getsize(p) < 18000: return None
        with Image.open(p) as im:
            w, h = im.size
            if w < 300 or h < 300: return None
            im.verify()
        with Image.open(p) as im:
            im.convert("RGB")
        return p
    except:
        return None

def quick_valid_grid(p):
    try:
        if os.path.getsize(p) < 4000: return None
        with Image.open(p) as im:
            im.verify()
        with Image.open(p) as im:
            im.convert("RGB")
        return p
    except:
        return None

def quick_valid_clip(p):
    try:
        sz = os.path.getsize(p)
        if sz < 200000: return None
        bn = os.path.basename(p).lower()
        if any(k in bn for k in ['watermark', 'getty', 'alamy', 'stock']): return None
        return {"path": p, "duration": 5.0, "has_audio": False, "source_id": os.path.basename(p).split("_")[0]}
    except:
        return None

def get_duration(media_file):
    res = subprocess.run([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", media_file
    ], capture_output=True, text=True)
    try: return float(res.stdout.strip())
    except: return 0.0

def main():
    total_vo_dur = get_duration(MASTER_VOICE_MP3)
    log(f"Building Fast 32+ Min Timeline for Dolly Viral Letter (Target: {total_vo_dur:.2f}s / {total_vo_dur/60:.2f} mins)...")
    
    topic_files = glob.glob(os.path.join(TOPIC_ASSETS, "*.*"))
    dolly_raw = glob.glob(os.path.join(IMAGES_DIR, "*.*"))
    grid_raw = glob.glob(os.path.join(GRID_DIR, "*.*"))
    
    with ThreadPoolExecutor(max_workers=32) as pool:
        dolly_images = [f for f in pool.map(quick_valid_photo, dolly_raw) if f]
        grids = [g for g in pool.map(quick_valid_grid, grid_raw) if g]
    
    random.seed(1515)
    random.shuffle(dolly_images)
    
    all_curated_images = topic_files * 8 + dolly_images[:350]
    random.seed(999)
    random.shuffle(all_curated_images)
    
    raw_clips = (
        glob.glob(os.path.join(MASTER_CLIPS_DIR, "*.mp4")) +
        glob.glob(os.path.join(CLIPS_DIR, "*.mp4"))
    )
    
    with ThreadPoolExecutor(max_workers=32) as pool:
        parsed_clips = [c for c in pool.map(quick_valid_clip, raw_clips) if c]
        
    topic_opening_clip = os.path.join(MASTER_CLIPS_DIR, "dolly_death_news.mp4")
    if not os.path.exists(topic_opening_clip):
        topic_opening_clip = os.path.join(MASTER_CLIPS_DIR, "8aHU5RSHW5Y_s012.mp4")
        
    clean_clips = []
    cancer_news_clips = []
    death_news_clips = []
    
    for c in parsed_clips:
        if c["path"] == topic_opening_clip: continue
        bn = os.path.basename(c["path"])
        if any(k in bn for k in ['cancer', 'CNN_dolly_cancer', 'Dolly_cancer']):
            cancer_news_clips.append(c)
        elif any(k in bn for k in ['death', '8aHU5RSHW5Y_s001', '8aHU5RSHW5Y_s002', '8aHU5RSHW5Y_s014']):
            death_news_clips.append(c)
        else:
            clean_clips.append(c)
            
    random.seed(1515)
    random.shuffle(clean_clips)
    random.seed(42)
    random.shuffle(cancer_news_clips)
    random.shuffle(death_news_clips)
    
    # Pre-generate 90+ custom graphic cards
    log("Pre-generating 90+ custom graphic cards specifically for Dolly's Final Letter & Literacy Mission...")
    custom_graphics = []
    
    split_cards = [
        ("Imagination Library", "300 Million Books Gifted Worldwide"),
        ("Dolly Parton", "The Queen of American Music"),
        ("Robert Lee Parton", "Honoring Her Fathers Silent Pain"),
        ("1995 Sevier County", "The Birth of a Literacy Revolution"),
        ("Dream Big Dreams", "Learn Everything You Can"),
        ("Colonel Tom Parker", "The 1974 Stand for Sovereignty"),
        ("The Graduation Note", "I Will Always Love You, Dolly"),
        ("Brentwood Farm", "Morning Prayers by Candlelight"),
        ("August 25 2026", "A Global Wave of Grief and Love"),
        ("Vanderbilt Vaccine", "One Million Dollars to Heal Humanity"),
        ("The Sacred Vault", "An Eternal Endowment for Children"),
        ("Coat of Many Colors", "Dignity for Every Humble Child"),
        ("The Little Engine", "I Think I Can, I Know I Can"),
        ("Two Sovereign Queens", "One Immortal Legacy"),
        ("A Crown of Dignity", "Unshakeable Creative Freedom")
    ]

    headlines = [
        "August 25, 2026: A Global Farewell",
        "1995: 1,760 Books in Sevierville",
        "300 Million Books Gifted Worldwide",
        "Honoring Robert Lee Parton",
        "Dream Big Dreams, Learn Everything",
        "The Little Engine That Could",
        "1974: The Stand Against Colonel Parker",
        "1 Million Dollar Vanderbilt Gift",
        "The Graduation Letter That Moved the World",
        "Waking at 3 AM to Write by Candlelight",
        "The Passing of Carl Dean in March 2025",
        "Rest in Peace, Queen of the Smoky Mountains"
    ]

    quotes = [
        "Dream big dreams; learn everything you can learn.",
        "Care for all those who care for you.",
        "You can be anyone you want to be.",
        "I Will Always Love You, Dolly.",
        "Dolly was the conscience of American music.",
        "She taught every child that their mind is a treasure.",
        "She proved that true greatness is measured by love.",
        "God didnt give me children so all children could be mine.",
        "I will always love you, Dolly.",
        "The books will never stop coming.",
        "Remember you belong only to God and your family.",
        "Dollys love will outlive the mountains."
    ]

    img_i = 0
    grid_i = 0

    # 1. Style 3: Split Typography Cards
    for title, subtitle in split_cards:
        safe_fn = f"split_{title.lower().replace(' ', '_').replace('&', 'and').replace('\'', '')}.jpg"
        out_p = os.path.join(GRAPHICS_DIR, safe_fn)
        GraphicCompositor.style3_split_typography_card(all_curated_images[img_i % len(all_curated_images)], grids[grid_i % len(grids)], title, subtitle, out_p)
        custom_graphics.append(out_p)
        img_i += 1
        grid_i += 1

    # 2. Style 4: Centered Headlines
    for h_text in headlines:
        safe_fn = f"headline_{h_text[:14].lower().replace(' ', '_').replace(':', '').replace(',', '').replace('\'', '')}.jpg"
        out_p = os.path.join(GRAPHICS_DIR, safe_fn)
        GraphicCompositor.style4_centered_headline(all_curated_images[img_i % len(all_curated_images)], h_text, out_p)
        custom_graphics.append(out_p)
        img_i += 1

    # 3. Style 5: Quote Captions
    for q_text in quotes:
        safe_fn = f"quote_{q_text[:14].lower().replace(' ', '_').replace(',', '').replace('\'', '')}.jpg"
        out_p = os.path.join(GRAPHICS_DIR, safe_fn)
        GraphicCompositor.style5_quote_caption(all_curated_images[img_i % len(all_curated_images)], q_text, out_p)
        custom_graphics.append(out_p)
        img_i += 1

    # 4. Style 2: Triptych Layouts (3 Dolly & Book photos side-by-side)
    for i in range(18):
        out_p = os.path.join(GRAPHICS_DIR, f"triptych_{i+1:02d}.jpg")
        bg_p = all_curated_images[img_i % len(all_curated_images)]
        three_p = [all_curated_images[(img_i + 1) % len(all_curated_images)], all_curated_images[(img_i + 2) % len(all_curated_images)], all_curated_images[(img_i + 3) % len(all_curated_images)]]
        GraphicCompositor.style2_triptych_overlay(bg_p, three_p, out_p)
        custom_graphics.append(out_p)
        img_i += 4

    # 5. Style 1: Rounded Grid Cards (Dolly over colorful grids)
    for i in range(30):
        out_p = os.path.join(GRAPHICS_DIR, f"grid_card_{i+1:02d}.jpg")
        GraphicCompositor.style1_rounded_card_on_grid(all_curated_images[img_i % len(all_curated_images)], grids[grid_i % len(grids)], out_p)
        custom_graphics.append(out_p)
        img_i += 1
        grid_i += 1

    log(f"Pre-generated {len(custom_graphics)} high-density graphic cards!")

    segments = []
    current_time = 0.0
    seg_idx = 0
    img_cursor = img_i
    cg_cursor = 0
    used_clip_sources = {}
    used_clip_paths = set()
    cancer_news_cursor = 0
    death_news_cursor = 0
    mot_modes = ["zoomin", "zoomout", "panright", "panleft"]

    # Segment 0: Opening Real Breaking News Video Clip with Anchor Soundbite (4.5s)
    segments.append({
        "index": 0, "start": 0.0, "end": 4.5, "duration": 4.5,
        "type": "headline", "file": topic_opening_clip,
        "grid_file": None, "motion": "none",
        "postcard": False, "has_audio": True, "section": "breaking_death_news_opening"
    })
    current_time = 4.5
    seg_idx = 1

    def pick_next_clip(current_seg):
        for c in clean_clips:
            if c["path"] in used_clip_paths: continue
            src_id = c["source_id"]
            if current_seg - used_clip_sources.get(src_id, -999) >= 10:
                used_clip_paths.add(c["path"])
                used_clip_sources[src_id] = current_seg
                return c
        for c in clean_clips:
            if c["path"] not in used_clip_paths:
                used_clip_paths.add(c["path"])
                used_clip_sources[c["source_id"]] = current_seg
                return c
        return None

    # Fast Hook (4.5s to 22.5s) -> 100% Curated Viral Letter & Dolly with Books Assets!
    letter_1 = os.path.join(TOPIC_ASSETS, "dolly_graduation_letter_01.jpg")
    holding_b = os.path.join(TOPIC_ASSETS, "dolly_holding_books.jpg")
    letter_2 = os.path.join(TOPIC_ASSETS, "dolly_graduation_letter_02.png")
    
    hook_assets = [
        letter_1 if os.path.exists(letter_1) else all_curated_images[0],
        os.path.join(GRAPHICS_DIR, "split_imagination_library.jpg") if os.path.exists(os.path.join(GRAPHICS_DIR, "split_imagination_library.jpg")) else custom_graphics[1],
        holding_b if os.path.exists(holding_b) else all_curated_images[1],
        os.path.join(GRAPHICS_DIR, "quote_dream_big_drea.jpg") if os.path.exists(os.path.join(GRAPHICS_DIR, "quote_dream_big_drea.jpg")) else custom_graphics[2],
        letter_2 if os.path.exists(letter_2) else all_curated_images[2],
        os.path.join(GRAPHICS_DIR, "triptych_01.jpg") if os.path.exists(os.path.join(GRAPHICS_DIR, "triptych_01.jpg")) else custom_graphics[3],
        os.path.join(GRAPHICS_DIR, "headline_300_million_bo.jpg") if os.path.exists(os.path.join(GRAPHICS_DIR, "headline_300_million_bo.jpg")) else custom_graphics[4]
    ]

    for h_img in hook_assets:
        dur = round((22.5 - current_time) / (len(hook_assets) - (seg_idx - 1)), 2)
        if dur < 2.0: dur = 2.5
        if current_time + dur > 22.5: dur = round(22.5 - current_time, 2)
        segments.append({
            "index": seg_idx, "start": current_time, "end": round(current_time + dur, 2), "duration": dur,
            "type": "image", "file": h_img, "motion": random.choice(mot_modes), "has_audio": False, "section": "fast_hook_viral_letter"
        })
        current_time = round(current_time + dur, 2)
        seg_idx += 1

    # Documentary Body (22.5s to total_vo_dur + 4.5s)
    # High-Density Video Clips (Every 2-3 segments!) + High-Density Graphic Cards
    target_total = total_vo_dur + 4.5
    while current_time < target_total:
        dur = round(random.uniform(4.5, 5.8), 2)
        if current_time + dur > target_total:
            dur = round(target_total - current_time, 2)
            if dur < 1.0:
                segments[-1]["duration"] = round(segments[-1]["duration"] + dur, 2)
                segments[-1]["end"] = target_total
                break

        # Cancer news clip moments (around 1350s to 1600s)
        is_cancer_news_moment = (1350.0 <= current_time <= 1600.0) and (cancer_news_cursor < len(cancer_news_clips)) and (seg_idx % 2 == 0)
        # Death news clip moments (around 1600s to 1850s)
        is_death_news_moment = (1600.0 <= current_time <= 1850.0) and (death_news_cursor < len(death_news_clips)) and (seg_idx % 2 == 0)

        # High clip density: every 2nd or 3rd segment is a video clip!
        is_clip = (seg_idx % 2 == 0)
        is_custom_graphic = (seg_idx % 3 == 0) and len(custom_graphics) > 0
        
        if is_cancer_news_moment:
            c_clip = cancer_news_clips[cancer_news_cursor % len(cancer_news_clips)]
            cancer_news_cursor += 1
            segments.append({
                "index": seg_idx, "start": current_time, "end": round(current_time + dur, 2), "duration": dur,
                "type": "clip", "file": c_clip["path"], "motion": "none", "postcard": False, "has_audio": False, "section": "cancer_news_broadcast_clip"
            })
        elif is_death_news_moment:
            d_clip = death_news_clips[death_news_cursor % len(death_news_clips)]
            death_news_cursor += 1
            segments.append({
                "index": seg_idx, "start": current_time, "end": round(current_time + dur, 2), "duration": dur,
                "type": "clip", "file": d_clip["path"], "motion": "none", "postcard": False, "has_audio": False, "section": "death_announcement_news_clip"
            })
        elif is_clip:
            c = pick_next_clip(seg_idx)
            if c:
                segments.append({
                    "index": seg_idx, "start": current_time, "end": round(current_time + dur, 2), "duration": dur,
                    "type": "clip", "file": c["path"], "motion": random.choice(mot_modes), "postcard": False, "has_audio": c["has_audio"], "section": "documentary_clip"
                })
            else:
                img = all_curated_images[img_cursor % len(all_curated_images)]
                img_cursor += 1
                segments.append({
                    "index": seg_idx, "start": current_time, "end": round(current_time + dur, 2), "duration": dur,
                    "type": "image", "file": img, "motion": random.choice(mot_modes), "postcard": (seg_idx % 5 == 0), "has_audio": False, "section": "dolly_body"
                })
        elif is_custom_graphic:
            cg_file = custom_graphics[cg_cursor % len(custom_graphics)]
            cg_cursor += 1
            segments.append({
                "index": seg_idx, "start": current_time, "end": round(current_time + dur, 2), "duration": dur,
                "type": "image", "file": cg_file, "motion": "zoomout", "postcard": False, "has_audio": False, "section": "custom_graphic"
            })
        else:
            img = all_curated_images[img_cursor % len(all_curated_images)]
            img_cursor += 1
            segments.append({
                "index": seg_idx, "start": current_time, "end": round(current_time + dur, 2), "duration": dur,
                "type": "image", "file": img, "motion": random.choice(mot_modes), "postcard": (seg_idx % 5 == 0), "has_audio": False, "section": "dolly_body"
            })
        current_time = round(current_time + dur, 2)
        seg_idx += 1

    log(f"Timeline Built! Total Segments: {len(segments)} ({current_time:.2f}s / {current_time/60:.2f} mins).")
    log(f"Custom Graphics Embedded: {cg_cursor + 4} CARDS (APPEARING FREQUENTLY THROUGHOUT VIDEO!)")
    log(f"Cancer & Death News Clips Embedded: {cancer_news_cursor + death_news_cursor} news clips in health and memorial chapters.")
    
    with open(TIMELINE_FILE, "w", encoding="utf-8") as f:
        json.dump({"total_duration": current_time, "custom_graphics_count": cg_cursor + 4, "segments": segments}, f, indent=2)
        
    log(f"Saved timeline to {TIMELINE_FILE}")

if __name__ == "__main__":
    main()
