"""
qc_pool.py - strict vision QC for a footage pool, before any of it can reach a video.

Every clip (three frames: start, middle, end) and every picture is shown to a vision model
(OpenLux / Gemini 2.5 Flash Lite by default - any provider docu/studio/ai.py knows works) with one
question: is this usable B-roll for a faceless documentary about <topic>? The model reports what it
sees; the *rules* below decide, so the decision never depends on how a model phrases a yes:

    REJECT (never used, in any template)
      talking head        someone speaking to the camera, an interview, a presenter, a podcast, a news anchor
      influencer / vlog   a face-cam, selfie video, creator talking, reaction video, any face that is the subject
      face close-up       one identifiable face filling much of the frame
      watermark           a stock watermark across the picture (Shutterstock, Getty, Alamy, iStock, Dreamstime...)
      centre logo / text  a logo, handle, @name or a subtitle/chyron in the middle of the frame
      screen recording    phone or desktop UI, a social-media post, a YouTube page
      irrelevant          relevance 0-1 out of 5 for the topic
    KEEP, CROPPED (the corner goes, the clip becomes ours)
      a channel logo / bug / handle in one corner or along one edge: qc.json gets `logo_corner` and an
      aspect-keeping `crop`; edl.clip() applies it, and the template's grade, grain, push-in and texture
      do the rest, so the shot no longer looks like somebody else's.

    python docu/tools/qc_pool.py <pool> --topic "<what the niche is about>" [--only clips|images]
                                 [--workers 8] [--strict] [--redo] [--provider openlux] [--model ...]

<pool> may be a niche pool (clips/ + images/), a footage folder (source_video/), or a project's media
folder (src/clips + src/images). Writes <pool>/qc.json (the gate edl.py enforces), qc_report.md and a
contact sheet of everything rejected (qc_rejected.jpg), so you can see what was thrown out and why.
Results are cached per file (size + mtime): re-running only checks new files.
"""

import argparse
import concurrent.futures as cf
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import threading

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "studio"))
sys.path.insert(0, os.path.dirname(HERE))

VIDEO_EXT = (".mp4", ".mov", ".m4v", ".webm", ".mkv")
IMAGE_EXT = (".jpg", ".jpeg", ".png", ".webp")

PROMPT = """You are the footage checker for a faceless documentary YouTube channel. Topic of the video: "{topic}".
You see {what}. Report ONLY what is visibly there - be literal, do not guess. Answer with one JSON object, nothing else:

{{"people": int,                 // people visible (0 if none)
  "largest_face_pct": number,    // the biggest visible human face as % of the frame area (0 if no face is visible)
  "face_toward_camera": bool,    // a clearly visible face turned toward the camera (frontal or three-quarter; NOT profile, NOT from behind)
  "eye_contact": bool,           // someone looks straight into the lens
  "speaking_to_camera": bool,    // someone talks to the camera or to an interviewer: presenter, anchor, interview, podcast, lecture
  "posed_portrait": bool,        // a person is the posed subject of a portrait / model shoot / selfie
  "influencer_or_vlog": bool,    // vlog, face-cam, selfie video, reaction, creator or social-media content
  "watermark": bool,             // a stock watermark across the picture (shutterstock, getty, alamy, istock, dreamstime, adobe stock...)
  "logo": bool,                  // a channel logo, TV bug, brand mark, @handle or URL drawn ON TOP of the footage
  "logo_corner": "none|top-left|top-right|bottom-left|bottom-right|top|bottom|left|right|center",
  "logo_box": [x0, y0, x1, y1] or null,   // where that logo/handle is, 0..1 of width/height
  "edited_text": bool,           // text ADDED in editing: subtitles, captions, chyrons, lower thirds, titles. NOT signs, labels or print that physically exist in the scene
  "edited_text_position": "none|top|bottom|center|corner",
  "screen_recording": bool,      // phone/desktop UI, a web page, a social-media post, a video player
  "relevance": int,              // 0-5: how well this works as B-roll for the topic (5 = exactly it, 1 = loosely, 0 = unrelated)
  "quality": int,                // 1-5: sharp, well exposed, steady, usable at 1080p
  "desc": "one plain sentence: what the shot shows",
  "tags": ["3-8 short tags of visible things"]}}"""

LOCK = threading.Lock()

# aspect-keeping crops that drop one corner or edge (x0, y0, x1, y1 as fractions of the frame)
CORNER_CROP = {
    "top-left": (0.14, 0.14, 1.00, 1.00), "top-right": (0.00, 0.14, 0.86, 1.00),
    "bottom-left": (0.14, 0.00, 1.00, 0.86), "bottom-right": (0.00, 0.00, 0.86, 0.86),
    "top": (0.07, 0.14, 0.93, 1.00), "bottom": (0.07, 0.00, 0.93, 0.86),
    "left": (0.14, 0.07, 1.00, 0.93), "right": (0.00, 0.07, 0.86, 0.93),
}


def find_dirs(pool):
    cands_v = [os.path.join(pool, d) for d in ("source_video", "clips", "src/clips", "footage/source_video")]
    cands_i = [os.path.join(pool, d) for d in ("images", "src/images", "images/approved")]
    vdir = next((d for d in cands_v if os.path.isdir(d)), None)
    idir = next((d for d in cands_i if os.path.isdir(d)), None)
    return vdir, idir


def sig(p):
    st = os.stat(p)
    return f"{st.st_size}:{int(st.st_mtime)}"


def duration(p):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p],
                       capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except ValueError:
        return 0.0


def strip(p, tmpdir):
    """three frames of a clip side by side (start, middle, end) - one picture, one model call"""
    from PIL import Image
    d = duration(p)
    if d <= 0:
        return None
    frames = []
    for k, f in enumerate((0.12, 0.5, 0.88)):
        out = os.path.join(tmpdir, f"f{k}.jpg")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{d * f:.2f}", "-i", p, "-vframes", "1",
                        "-vf", "scale=640:-2", out], capture_output=True)
        if os.path.exists(out):
            frames.append(Image.open(out).convert("RGB"))
    if not frames:
        return None
    h = max(f.height for f in frames)
    sheet = Image.new("RGB", (sum(f.width for f in frames) + 8 * (len(frames) - 1), h), (0, 0, 0))
    x = 0
    for f in frames:
        sheet.paste(f, (x, 0))
        x += f.width + 8
    out = os.path.join(tmpdir, "strip.jpg")
    sheet.save(out, quality=82)
    return out


def ask(chat_factory, topic, kind, picture):
    what = ("three frames from one video clip (start, middle, end), side by side" if kind == "clip"
            else "one photograph")
    for attempt in range(3):
        chat = chat_factory()
        txt = chat.send(PROMPT.format(topic=topic, what=what), images=[picture], max_tokens=700)
        m = re.search(r"\{.*\}", txt, re.S)
        if m:
            try:
                return json.loads(re.sub(r"//[^\n]*", "", m.group(0)))
            except json.JSONDecodeError:
                pass
    raise RuntimeError("the model did not return JSON")


def crop_for(r):
    """an aspect-keeping crop that removes the logo box, else the corner table"""
    box = r.get("logo_box")
    if isinstance(box, list) and len(box) == 4:
        try:
            x0, y0, x1, y1 = [min(1.0, max(0.0, float(v))) for v in box]
            cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
            # keep the side away from the logo; cut just past it on both axes so 16:9 is kept
            if cy < 0.5 and cx < 0.5:
                c = max(x1, y1) + 0.02
                cand = (c, c, 1.0, 1.0)
            elif cy < 0.5:
                c = max(1 - x0, y1) + 0.02
                cand = (0.0, c, 1 - c, 1.0)
            elif cx < 0.5:
                c = max(x1, 1 - y0) + 0.02
                cand = (c, 0.0, 1.0, 1 - c)
            else:
                c = max(1 - x0, 1 - y0) + 0.02
                cand = (0.0, 0.0, 1 - c, 1 - c)
            if c <= 0.25:                 # small enough to crop away and still look full-frame
                return [round(v, 3) for v in cand]
        except (TypeError, ValueError):
            pass
    corner = (r.get("logo_corner") or "").lower()
    return list(CORNER_CROP[corner]) if corner in CORNER_CROP else None


def decide(r, strict):
    """the rules, applied to what the model saw (strict lowers the face thresholds)"""
    why = []
    face = float(r.get("largest_face_pct") or 0)
    if r.get("speaking_to_camera"):
        why.append("talking head")
    if r.get("influencer_or_vlog"):
        why.append("influencer / vlog")
    if r.get("posed_portrait"):
        why.append("posed portrait")
    # the model's face SIZE estimates run high, its semantic answers (posed, eye contact, speaking) are reliable:
    # size alone rejects only a real close-up; --strict brings back the tighter face rules
    if r.get("eye_contact") and face >= (0.5 if strict else 1.0):
        why.append("looks into the camera")
    elif strict and r.get("face_toward_camera") and face >= 4.0:
        why.append(f"face toward camera ({face:.0f}% of frame)")
    elif face >= (12.0 if strict else 25.0):
        why.append(f"a face is the subject ({face:.0f}% of frame)")
    if r.get("watermark"):
        why.append("stock watermark")
    if r.get("screen_recording"):
        why.append("screen recording / UI")
    corner = (r.get("logo_corner") or "none").lower()
    if r.get("logo") and corner == "center":
        why.append("logo in the middle")
    tpos = (r.get("edited_text_position") or "none").lower()
    if r.get("edited_text") and tpos == "center":
        why.append("captions / text in the middle")
    rel = int(r.get("relevance") if r.get("relevance") is not None else 3)
    if rel <= 0:
        why.append("unrelated to the topic")
    if int(r.get("quality") if r.get("quality") is not None else 3) <= 1:
        why.append("unusable quality")
    out = dict(reject=bool(why), reason=", ".join(why))
    if rel == 1 and not why:
        out["weak"] = True                # usable, but only loosely about the topic: the editor should prefer others
    if not why and (r.get("logo") or (r.get("edited_text") and tpos in ("top", "bottom", "corner"))):
        if r.get("logo"):
            c = crop_for(r) or list(CORNER_CROP.get(corner, CORNER_CROP["bottom-right"]))
            where = corner
        else:
            c = list(CORNER_CROP["bottom"] if tpos != "top" else CORNER_CROP["top"])
            where = tpos if tpos != "corner" else "bottom"
        out.update(crop=c, logo_corner=where, note="logo / added text cropped away")
    return out


def main():
    ap = argparse.ArgumentParser(description="strict vision QC for a footage pool")
    ap.add_argument("pool")
    ap.add_argument("--topic", default="", help="what the videos are about (relevance is judged against it)")
    ap.add_argument("--only", choices=["clips", "images", "all"], default="all")
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--strict", action="store_true", help="reject every face close-up, even in a group")
    ap.add_argument("--redo", action="store_true", help="check every file again, ignoring the cache")
    ap.add_argument("--provider", default=None, help="ai.py provider (default: the vision provider, OpenLux first)")
    ap.add_argument("--model", default=None)
    ap.add_argument("--limit", type=int, default=0, help="check at most N new files (a quick test)")
    ap.add_argument("--retopic", action="store_true", help="check files again when the topic changed (relevance)")
    ap.add_argument("--redecide", action="store_true", help="re-apply the rules to what the model already reported (no AI calls)")
    a = ap.parse_args()
    if a.redecide:
        pool = os.path.abspath(a.pool)
        qc_path = os.path.join(pool, "qc.json")
        qc = json.load(open(qc_path, encoding="utf-8"))
        n = 0
        for k, v in qc.items():
            if not v.get("seen"):
                continue
            r = dict(v["seen"], relevance=v.get("relevance"), quality=v.get("quality"))
            d = decide(r, a.strict)
            for key in ("reject", "reason", "crop", "logo_corner", "note", "weak"):
                v.pop(key, None)
            v.update(d)
            n += 1
        json.dump(qc, open(qc_path, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
        print(f"re-decided {n} files with the current rules")
        report(pool, qc, *find_dirs(pool))
        return

    import ai
    prov = a.provider or ai.resolve("vision")
    if not prov:
        sys.exit("No vision AI is set up. Put OPENLUX_API_KEY in api_keys/keys.env (or set FRONTIER_DIR).")
    model = a.model or ai.model_for("vision", prov)

    def factory():
        return ai.Chat("vision", provider=prov, model=model, log=lambda *x: None)

    pool = os.path.abspath(a.pool)
    vdir, idir = find_dirs(pool)
    topic = a.topic or os.path.basename(pool.rstrip("/\\")).replace("_", " ")
    qc_path = os.path.join(pool, "qc.json")
    qc = json.load(open(qc_path, encoding="utf-8")) if os.path.exists(qc_path) else {}
    todo = []
    for kind, d, ext in (("clip", vdir, VIDEO_EXT), ("image", idir, IMAGE_EXT)):
        if not d or (a.only == "clips" and kind == "image") or (a.only == "images" and kind == "clip"):
            continue
        for f in sorted(os.listdir(d)):
            if not f.lower().endswith(ext) or f.startswith(("qc_", "_", ".")):
                continue
            p = os.path.join(d, f)
            old = qc.get(f)
            if old and not a.redo and old.get("sig") == sig(p) and (old.get("topic") == topic or not a.retopic):
                continue                  # unchanged file: faces / logos / watermarks don't depend on the topic's wording
            todo.append((kind, p))
    if a.limit:
        todo = todo[:a.limit]
    print(f"QC  {pool}\n    topic: {topic}\n    model: {ai.LABEL.get(prov, prov)} · {model}\n"
          f"    {len(todo)} files to check ({len(qc)} already in qc.json)", flush=True)

    done = [0]

    def run(job):
        kind, p = job
        name = os.path.basename(p)
        with tempfile.TemporaryDirectory() as tmp:
            pic = strip(p, tmp) if kind == "clip" else p
            if not pic:
                rec = dict(kind=kind, reject=True, reason="unreadable file")
            else:
                try:
                    r = ask(factory, topic, kind, pic)
                    rec = dict(kind=kind, **decide(r, a.strict), relevance=r.get("relevance"), quality=r.get("quality"),
                               desc=r.get("desc", ""), tags=r.get("tags", []), seen={k: r.get(k) for k in (
                                   "people", "largest_face_pct", "face_toward_camera", "eye_contact", "speaking_to_camera",
                                   "posed_portrait", "influencer_or_vlog", "watermark", "logo", "logo_corner", "logo_box",
                                   "edited_text", "edited_text_position", "screen_recording")})
                except Exception as e:         # noqa: BLE001 - one bad file must not stop the pool
                    rec = dict(kind=kind, reject=True, reason=f"QC failed: {str(e)[:120]}", error=True)
        rec.update(sig=sig(p), topic=topic, model=model)
        with LOCK:
            qc[name] = rec
            done[0] += 1
            if done[0] % 10 == 0 or done[0] == len(todo):
                json.dump(qc, open(qc_path, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
            flag = "REJECT " + rec["reason"] if rec.get("reject") else ("crop " + rec.get("logo_corner", "") if rec.get("crop") else "ok")
            print(f"  [{done[0]}/{len(todo)}] {name[:60]:60s} {flag}", flush=True)
        return name

    with cf.ThreadPoolExecutor(max(1, a.workers)) as ex:
        list(ex.map(run, todo))
    json.dump(qc, open(qc_path, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    report(pool, qc, vdir, idir)


def report(pool, qc, vdir, idir):
    rej = {k: v for k, v in qc.items() if v.get("reject")}
    crop = {k: v for k, v in qc.items() if not v.get("reject") and v.get("crop")}
    errs = {k: v for k, v in qc.items() if v.get("error")}
    n_c = sum(1 for v in qc.values() if v.get("kind") == "clip")
    rep_dir = os.path.join(pool, "_qc")
    os.makedirs(rep_dir, exist_ok=True)
    with open(os.path.join(rep_dir, "qc_report.md"), "w", encoding="utf-8") as f:
        f.write(f"# QC report\n\n{len(qc)} files checked ({n_c} clips, {len(qc) - n_c} pictures): "
                f"{len(qc) - len(rej)} usable, {len(crop)} of them cropped, {len(rej)} rejected"
                f"{f', {len(errs)} could not be checked (rejected until re-run)' if errs else ''}.\n\n## Rejected\n\n")
        for k, v in sorted(rej.items()):
            f.write(f"- `{k}` - {v['reason']}" + (f" - {v.get('desc')}" if v.get("desc") else "") + "\n")
        f.write("\n## Kept with a corner cropped away\n\n")
        for k, v in sorted(crop.items()):
            f.write(f"- `{k}` - {v.get('logo_corner')} - crop {v['crop']}\n")
    # a contact sheet of the rejects, so a person can check the checker
    try:
        from PIL import Image, ImageDraw
        items = sorted(rej)[:63]
        if items:
            W, H, C = 320, 180, 7
            rows = (len(items) + C - 1) // C
            sh = Image.new("RGB", (W * C, rows * (H + 34)), (14, 14, 16))
            d = ImageDraw.Draw(sh)
            for j, k in enumerate(items):
                x, y = (j % C) * W, (j // C) * (H + 34)
                src = None
                for base in (vdir, idir):
                    if base and os.path.exists(os.path.join(base, k)):
                        src = os.path.join(base, k)
                if not src:
                    continue
                if src.lower().endswith(VIDEO_EXT):
                    tmp = os.path.join(tempfile.gettempdir(), "qc_" + hashlib.md5(k.encode()).hexdigest() + ".jpg")
                    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", "1", "-i", src, "-vframes", "1", "-vf", "scale=320:-2", tmp],
                                   capture_output=True)
                    src = tmp
                try:
                    im = Image.open(src).convert("RGB")
                    im.thumbnail((W - 4, H - 4))
                    sh.paste(im, (x + 2, y + 2))
                except Exception:      # noqa: BLE001
                    pass
                d.text((x + 4, y + H + 2), k[:44], fill=(235, 230, 220))
                d.text((x + 4, y + H + 16), rej[k]["reason"][:48], fill=(240, 120, 110))
            sh.save(os.path.join(rep_dir, "qc_rejected.jpg"), quality=80)
    except Exception as e:             # noqa: BLE001
        print("  (no reject sheet:", e, ")")
    print(f"\n{len(qc) - len(rej)} usable ({len(crop)} cropped), {len(rej)} rejected"
          f"{f', {len(errs)} errors' if errs else ''}  ->  {os.path.join(pool, 'qc.json')}")
    print(f"see {os.path.join(pool, '_qc', 'qc_report.md')}" + ("  and _qc/qc_rejected.jpg" if rej else ""))


if __name__ == "__main__":
    main()
