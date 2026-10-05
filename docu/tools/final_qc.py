"""
final_qc.py - the last check before a video ships: every piece of footage, against the words it sits under.

For each clip and photograph scene of the finished edit, the frame the viewer sees (the footage after the
QC crop - our own graphics left out, they are ours) is shown to the vision model together with the
sentence spoken over it. It is flagged when:

    - a person talks to the camera, poses for it, looks into the lens, or a face is the subject
    - an influencer / vlog / face-cam shot slipped through
    - any channel logo, @handle, TV bug or stock watermark is still visible (the crop missed it)
    - captions or chyrons that are not ours are burnt in
    - the picture is off-topic for the video (topic_fit 0-1 of 5); a loose literal match is only reported

    python docu/tools/final_qc.py <work_dir> --words <project>/data/words.json --topic "<topic>" [--workers 8]

edl.py runs it after `final` when a vision AI is set up. It writes final_qc.json, final_qc.md and
final_qc_flags.jpg (every flagged frame with its scene id and reason) into the work folder and exits 1
when anything was flagged: replace those shots in build.py and re-render just them
(`python build.py render s012 s047`, then `final`).
"""

import argparse
import concurrent.futures as cf
import json
import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "studio"))

PROMPT = """Final check of a faceless documentary before it is published. Topic of the whole video: "{topic}".
Look at the picture and report literally, one JSON object and nothing else.

First judge the picture ON ITS OWN, as B-roll for a documentary about that topic (ignore the narration here):
"topic_fit" 0-5. Documentary B-roll sets place and mood: anything from the topic's own world - its places,
landscapes, buildings, people at work, objects, animals, vehicles, archive material - fits (4-5) even when it does
not show one exact sentence. Score 0-1 ONLY when the picture plainly belongs to a different subject altogether
(something no viewer of this topic would expect to see).

Then read what the narrator says over it: "{line}"
"match" 0-5: how literally the picture shows those words (B-roll is often 1-2, and that is fine).

{{"topic_fit": int, "match": int,
  "speaking_to_camera": bool, "posed_portrait": bool, "influencer_or_vlog": bool, "eye_contact": bool,
  "largest_face_pct": number,          // biggest visible face as % of the frame, 0 if none
  "logo_or_handle": bool,              // a channel logo, TV bug, @handle, URL or stock watermark DRAWN ON TOP of the footage
                                       // (NOT shop signs, building lettering, labels or print that physically exist in the scene)
  "logo_where": "none|top-left|top-right|bottom-left|bottom-right|top|bottom|center",
  "burnt_in_text": bool,               // subtitles, captions, chyrons or titles added in someone else's edit (not signs in the scene)
  "desc": "what the picture shows, one sentence"}}"""


def spoken(words, t0, t1):
    w = [x["w"] for x in words if x["e"] > t0 and x["s"] < t1]
    return " ".join(w)[:400] or "(music only)"


def frame_of(scene, assets_dir, tmp):
    """the footage the viewer sees in this scene, without our overlays"""
    out = os.path.join(tmp, scene["id"] + ".jpg")
    if scene["type"] == "clip":
        t = float(scene.get("start", 0)) + min(2.0, max(0.2, (float(scene.get("end", 0)) - float(scene.get("start", 0))) * 0.4))
        vf = []
        if scene.get("crop"):
            x0, y0, x1, y1 = scene["crop"]
            vf.append(f"crop=iw*{x1 - x0:.4f}:ih*{y1 - y0:.4f}:iw*{x0:.4f}:ih*{y0:.4f}")
        vf.append("scale=960:-2")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.2f}", "-i", scene["src"], "-vframes", "1", "-vf", ",".join(vf), out],
                       capture_output=True)
    else:
        src = os.path.join(assets_dir, scene["img"])
        if not os.path.exists(src):
            return None
        from PIL import Image
        im = Image.open(src).convert("RGB")
        im.thumbnail((960, 960))
        im.save(out, quality=82)
    return out if os.path.exists(out) else None


def judge(r, scene=None):
    why = []
    face = float(r.get("largest_face_pct") or 0)
    if r.get("speaking_to_camera"):
        why.append("talking head")
    if r.get("influencer_or_vlog"):
        why.append("influencer / vlog")
    if r.get("posed_portrait"):
        why.append("posed portrait")
    if r.get("eye_contact") and face >= 1:
        why.append("looks into the camera")
    elif face >= 25:
        why.append(f"a face is the subject ({face:.0f}%)")
    if r.get("logo_or_handle"):
        why.append(f"logo / handle / watermark still visible ({r.get('logo_where', '?')})")
    if r.get("burnt_in_text"):
        why.append("someone else's captions burnt in")
    fit = r.get("topic_fit")
    fit = int(fit) if isinstance(fit, (int, float)) else 3
    if fit <= 1 and not (scene or {}).get("qc_ok"):
        why.append("off-topic for this video")        # an editor who chose a loose shot on purpose marks it qc_ok=True
    return why


def run(scenes, words, topic, assets_dir, out_dir, workers=8, provider=None, model=None, log=print):
    import ai
    prov = provider or ai.resolve("vision")
    if not prov:
        log("final QC skipped: no vision AI set up (OPENLUX_API_KEY)")
        return None
    model = model or ai.model_for("vision", prov)
    todo = [s for s in scenes if s["type"] in ("clip", "photo", "depth", "spotlight")]
    log(f"final QC: {len(todo)} footage scenes · {ai.LABEL.get(prov, prov)} · {model}")
    res = {}

    def one(s):
        with tempfile.TemporaryDirectory() as tmp:
            pic = frame_of(s, assets_dir, tmp)
            if not pic:
                return s["id"], dict(flags=["frame could not be read"], line="")
            line = spoken(words, s["t0"], s["t0"] + s["duration"])
            for _ in range(3):
                try:
                    txt = ai.Chat("vision", provider=prov, model=model, log=lambda *x: None).send(
                        PROMPT.format(topic=topic, line=line), images=[pic], max_tokens=500)
                    m = re.search(r"\{.*\}", txt, re.S)
                    r = json.loads(re.sub(r"//[^\n]*", "", m.group(0)))
                    keep = os.path.join(out_dir, "final_qc_frames")
                    os.makedirs(keep, exist_ok=True)
                    dst = os.path.join(keep, s["id"] + ".jpg")
                    os.replace(pic, dst)
                    weak = int(r.get("match") if r.get("match") is not None else 3) <= 1 or int(r.get("topic_fit") or 3) == 2
                    return s["id"], dict(flags=judge(r, s), weak=weak, line=line, match=r.get("match"), desc=r.get("desc", ""), frame=dst)
                except Exception as e:          # noqa: BLE001
                    err = str(e)
            return s["id"], dict(flags=[f"QC call failed: {err[:80]}"], line=line)

    with cf.ThreadPoolExecutor(max(1, workers)) as ex:
        for sid, r in ex.map(one, todo):
            res[sid] = r
    bad = {k: v for k, v in res.items() if v["flags"]}
    json.dump(res, open(os.path.join(out_dir, "final_qc.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    with open(os.path.join(out_dir, "final_qc.md"), "w", encoding="utf-8") as f:
        weak = {k: v for k, v in res.items() if v.get("weak") and not v["flags"]}
        f.write(f"# Final QC\n\n{len(res)} footage scenes checked, {len(bad)} flagged (must be replaced), "
                f"{len(weak)} only loosely fit their words (worth a second look).\n\n## Flagged\n\n")
        for k in sorted(bad):
            v = bad[k]
            f.write(f"- **{k}** - {', '.join(v['flags'])}\n  - narration: \"{v['line'][:160]}\"\n"
                    + (f"  - picture: {v.get('desc', '')}\n" if v.get("desc") else ""))
        f.write("\n## Loose fit (not blocking)\n\n")
        for k in sorted(weak):
            f.write(f"- {k} - \"{weak[k]['line'][:100]}\" / {weak[k].get('desc', '')}\n")
    if bad:
        try:
            from PIL import Image, ImageDraw
            items = sorted(bad)[:40]
            Wd, Hd, C = 400, 225, 4
            sh = Image.new("RGB", (Wd * C, ((len(items) + C - 1) // C) * (Hd + 40)), (14, 14, 16))
            d = ImageDraw.Draw(sh)
            for j, k in enumerate(items):
                x, y = (j % C) * Wd, (j // C) * (Hd + 40)
                fr = bad[k].get("frame")
                if fr and os.path.exists(fr):
                    im = Image.open(fr).convert("RGB")
                    im.thumbnail((Wd - 4, Hd - 4))
                    sh.paste(im, (x + 2, y + 2))
                d.text((x + 4, y + Hd + 2), k, fill=(250, 220, 120))
                d.text((x + 4, y + Hd + 18), ", ".join(bad[k]["flags"])[:56], fill=(240, 120, 110))
            sh.save(os.path.join(out_dir, "final_qc_flags.jpg"), quality=82)
        except Exception as e:     # noqa: BLE001
            log(f"(no flag sheet: {e})")
    log(f"final QC: {len(res) - len(bad)} clean, {len(bad)} flagged" +
        (f" -> {', '.join(sorted(bad)[:12])}{' ...' if len(bad) > 12 else ''}  (see final_qc.md)" if bad else ""))
    return bad


def main():
    ap = argparse.ArgumentParser(description="final footage QC of a finished edit")
    ap.add_argument("work", help="the project's work folder (has scenes.json and assets/)")
    ap.add_argument("--words", required=True)
    ap.add_argument("--topic", default="")
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--provider")
    ap.add_argument("--model")
    a = ap.parse_args()
    scenes = json.load(open(os.path.join(a.work, "scenes.json"), encoding="utf-8"))
    words = json.load(open(a.words, encoding="utf-8"))
    bad = run(scenes, words, a.topic, os.path.join(a.work, "assets"), a.work, a.workers, a.provider, a.model)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
