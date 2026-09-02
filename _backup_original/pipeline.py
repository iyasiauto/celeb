"""
Master Orchestrator for 30+ Minute YouTube Documentary Automation.
Executes Voiceover Synthesis, Semantic Timeline Building, Pure GPU NVENC Rendering, and Metadata Generation.
"""

import os, sys, time, argparse
from voiceover_engine import VoiceoverEngine
from timeline_engine import TimelineEngine
from render_engine import RenderEngine
from metadata_engine import MetadataEngine

def main():
    parser = argparse.ArgumentParser(description="YouTube Long-Form Documentary Production Pipeline")
    parser.add_argument("--script", required=True, help="Path to full documentary script text file")
    parser.add_argument("--output-dir", required=True, help="Destination directory for final video")
    parser.add_argument("--title", required=True, help="Documentary Title")
    parser.add_argument("--opening-clip", default=None, help="Path to topic opening hook clip")
    parser.add_argument("--bgm", default=None, help="Path to background music mp3")
    parser.add_argument("--voice-id", default="gcdNeREzHPJpCf9wnB0l", help="TwoSpeaker Voice ID")
    parser.add_argument("--api-key", default="vk-30bcf8472580aa90e90c3a7fa9563b1bd269c868a206f1fa", help="TwoSpeaker API Key")
    parser.add_argument("--clips-dir", default=r"C:\Users\ninja\Downloads\Dolly Parton\clips", help="Directory containing clips")
    parser.add_argument("--images-dir", default=r"C:\Users\ninja\Downloads\Dolly Parton\Real images data", help="Directory containing high-res photos")
    parser.add_argument("--grid-dir", default=r"C:\Users\ninja\Downloads\Dolly Parton\gird-pattern-background-design", help="Directory containing grid backgrounds")
    args = parser.parse_args()

    work_dir = os.path.join(args.output_dir, "temp_render_workspace")
    os.makedirs(work_dir, exist_ok=True)

    print("============================================================")
    print(f"STARTING PRODUCTION PIPELINE FOR: {args.title}")
    print("============================================================")

    # 1. Voiceover
    with open(args.script, "r", encoding="utf-8") as f:
        script_text = f.read()

    vo_engine = VoiceoverEngine(api_key=args.api_key, voice_id=args.voice_id)
    master_mp3, vo_dur = vo_engine.synthesize(script_text, work_dir)
    print(f"Voiceover generated: {vo_dur:.1f}s ({vo_dur/60:.2f} mins)")

    # 2. Timeline
    tl_engine = TimelineEngine(clips_dir=args.clips_dir, images_dir=args.images_dir, grid_dir=args.grid_dir)
    timeline_json = os.path.join(work_dir, "timeline.json")
    tl_engine.build_timeline(vo_dur, args.opening_clip, timeline_json)
    print("Timeline synchronized.")

    # 3. Render Engine
    final_video_path = os.path.join(args.output_dir, f"{args.title}.mp4")
    r_engine = RenderEngine(work_dir=work_dir, bgm_path=args.bgm, workers=6)
    r_engine.render_and_mux(timeline_json, master_mp3, final_video_path)
    print(f"Video rendered successfully: {final_video_path}")

    # 4. Metadata
    meta_path = os.path.join(args.output_dir, f"YOUTUBE_METADATA_{args.title.replace(' ', '_').upper()}.txt")
    MetadataEngine.generate_metadata(
        title=args.title,
        alt_titles=[f"The Untold Story of {args.title}", f"Behind The Scenes: {args.title}"],
        description=f"Full 30-minute documentary exploring {args.title}.",
        chapters=["0:00 Introduction", "2:45 The Turning Point", "10:00 The Legacy"],
        tags=["Documentary", "Biography", "History"],
        hashtags=["#Documentary", "#Biography"],
        out_path=meta_path
    )
    print("Metadata generated.")

if __name__ == "__main__":
    main()
