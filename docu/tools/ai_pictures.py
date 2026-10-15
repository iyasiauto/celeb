"""
ai_pictures.py - pictures drawn for the words, for the templates built on them (2D Stories, Carl Jung, and any
template whose template.json has an "ai_images" block), made with Frontier's Gemini browser tool (docu/gemini_images.py).

    # 1. let the AI art director cut the script into frames and write a prompt for each (Frontier's own scene prompt,
    #    the channel's cast and look), then draw them all in one Gemini session:
    python docu/tools/ai_pictures.py --template stories-2d --script projects/<slug>/data/script.txt --out media/<niche>/ai_images

    # 2. or draw prompts you (or Claude) wrote yourself - a JSON list [{"key": "kitchen_0615", "prompt": "..."}]:
    python docu/tools/ai_pictures.py --template dark-psychology --prompts prompts.json --out media/<niche>/ai_images

    --dry-run       write the prompts (ai_prompts.json next to the pictures) without opening Gemini
    --count N       number of frames (default: script length / the template's every_s)

Every prompt gets the template's look suffix (still_suffix) and, for a story channel, the cast description word for
word, so the same person comes back in every picture. The pictures land as <out>/<key>.png; add <out> to the niche's
image folders (niche.py) and use them in the shot list like any picture: photo("ai_003"), F.g("image", image=...).

Needs: Node.js and Frontier's gemini_image/ folder (npm install done, Google profiles logged in) - see
docu/gemini_images.py for where it is looked for. The art director uses Docu Studio's AI (docu/studio/ai.py,
Settings -> AI); without one, write the prompts yourself and use --prompts.
"""

import argparse
import json
import os
import re
import sys

DOCU = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(DOCU)
sys.path[:0] = [DOCU, os.path.join(DOCU, "studio")]


def settings(tid):
    p = os.path.join(ROOT, "templates", tid, "template.json")
    t = json.load(open(p, encoding="utf-8"))
    a = t.get("ai_images")
    if not a:
        raise SystemExit(f"{tid}: this template has no ai_images block (drawn pictures are not part of its look)")
    return t, a


def art_director(a, script, count, log=print):
    """Frontier's scene prompt, filled: [{text, prompt}] x count, from Docu Studio's AI"""
    import ai
    scene = (a.get("scene_prompt") or "").replace("[INSERT CHANNEL HERE]", a.get("channel", "")) \
        .replace("[INSERT COUNT HERE]", str(count)).replace("[INSERT SCRIPT HERE]", script)
    cast = (a.get("character") or "").strip()
    if cast:
        scene += ("\n\nTHE CAST — these people recur through the whole video:\n" + cast +
                  "\n\nWhenever one of them is in frame, copy their description into the prompt WORD FOR WORD, every time." +
                  (" The main character is in EVERY frame — in a close-up, at least their hand, sleeve or shoulder in the"
                   " foreground." if a.get("placement") == "story" else
                   " Scenes with no people (an object, a room, a street) are welcome and should be about a third of the set."))
    chat = ai.Chat("editor", system="You are an art director. Answer with the JSON array only.", log=log)
    raw = chat.send(scene)
    m = re.search(r"\[.*\]", raw, re.S)
    if not m:
        raise SystemExit("the art director did not answer with a JSON array")
    rows = json.loads(m.group(0))
    return [r for r in rows if isinstance(r, dict) and r.get("prompt")]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--template", required=True)
    ap.add_argument("--out", required=True, help="folder the pictures go to (a niche image folder)")
    ap.add_argument("--script", help="the narration (plain text) - the art director writes the prompts")
    ap.add_argument("--prompts", help="a JSON list of {key, prompt} you wrote")
    ap.add_argument("--count", type=int, default=0)
    ap.add_argument("--wpm", type=float, default=140.0, help="narration speed, to turn the script into seconds")
    ap.add_argument("--slug", default="")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    t, cfg = settings(a.template)
    os.makedirs(a.out, exist_ok=True)
    if a.prompts:
        rows = json.load(open(a.prompts, encoding="utf-8"))
    elif a.script:
        script = open(a.script, encoding="utf-8").read().strip()
        secs = len(script.split()) / a.wpm * 60.0
        count = a.count or max(4, int(round(secs / float(cfg.get("every_s") or 6.0))))
        print(f"{a.template}: {count} frames for ~{secs / 60:.1f} min of narration")
        rows = art_director(cfg, script, count)
    else:
        raise SystemExit("give --script (the AI writes the prompts) or --prompts (your own)")
    suffix = (cfg.get("still_suffix") or "").strip()
    jobs = []
    for i, r in enumerate(rows, 1):
        key = re.sub(r"[^a-z0-9_]+", "_", str(r.get("key") or f"ai_{i:03d}").lower()).strip("_")
        jobs.append(dict(key=key, text=r.get("text", ""), prompt=" ".join(f"{r['prompt']} {suffix}".split())))
    json.dump(jobs, open(os.path.join(a.out, "ai_prompts.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print(f"{len(jobs)} prompts -> {os.path.join(a.out, 'ai_prompts.json')}")
    if a.dry_run:
        return
    todo = [j for j in jobs if not os.path.exists(os.path.join(a.out, j["key"] + ".png"))]
    if not todo:
        print("every picture is already there")
        return
    import gemini_images
    from pathlib import Path
    got = gemini_images.batch_image_gen([j["prompt"] for j in todo], [Path(a.out) / (j["key"] + ".png") for j in todo],
                                        slug=a.slug or a.template, log=print)
    print(f"{len(got)} / {len(todo)} pictures drawn into {a.out}")


if __name__ == "__main__":
    main()
