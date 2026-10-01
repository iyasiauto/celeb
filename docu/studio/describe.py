"""
describe.py - catalog a new niche's footage with Claude looking at the contact sheets.

This is the step that makes picture choice accurate (docu/VISUAL_SYNC_GUIDE.md §3 step 1): every clip and
picture gets a literal one-line description, tags, a quality score and reject flags.

    images: tools/catalog_images.py scan -> sheets_img/<topic>_<nn>.jpg -> Claude -> notes_img.txt -> pick
    clips:  tools/catalog_clips.py scan  -> sheets_clips/clips_<nnn>.jpg -> Claude -> notes_clips.txt -> build
"""

import json
import os
import re
import sys
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [HERE, os.path.join(os.path.dirname(HERE), "tools")]

import claude_shotlist as cs      # noqa: E402

IMG_PROMPT = """This is a contact sheet of pictures for a faceless documentary channel. Niche: {niche}.
Each thumbnail is labelled with its position number and pixel size (e.g. "12 1920x1080").
For every picture worth using in a documentary, write ONE line:
{sheet}:<position>|<tags>|<literal description>
- tags: 1-3 short lowercase topic words, comma separated (place, institution, activity, object), e.g. street,family
- description: what is visible - who, where, what they do, day/night, colour or B&W, any readable sign. Max 12 words.
Skip pictures that are tiny, blurry, mostly text or a logo, memes, watermarked, or show readable private data
(names or ID numbers on cards). Output only the lines, no other text."""

CLIP_PROMPT = """This is a contact sheet of video shots for a faceless documentary channel. Niche: {niche}.
Each row holds shots side by side: three frames per shot (start, middle, end), labelled "<index>  <length>s  <file>".
For EVERY shot write ONE line:
<index>|<quality 1-5>|<flags>|<tags>|<literal description>
- quality: 5 sharp, steady, well framed ... 1 unusable
- flags (comma separated, empty if none): p presenter/vlogger on camera, s burnt-in subtitles, t text or captions,
  g foreign graphics/logos, i interview/talking head
- tags: 1-3 short lowercase topic words; description: what is visible, max 12 words.
Output only the lines, no other text."""


def _ask_sheet(session_args, prompt, path):
    key, model = session_args
    client = cs._client(key)
    content = [{"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": cs.jpeg_b64(path, 1800)}},
               {"type": "text", "text": prompt}]
    for attempt in range(3):
        try:
            with client.beta.messages.stream(
                model=model, max_tokens=16000, messages=[{"role": "user", "content": content}],
                thinking={"type": "adaptive"}, output_config={"effort": "medium"},
                betas=["server-side-fallback-2026-07-01"], fallbacks="default",
            ) as stream:
                msg = stream.get_final_message()
            if msg.stop_reason == "refusal":
                return []
            text = "".join(b.text for b in msg.content if b.type == "text")
            return [l.strip() for l in text.split("\n") if "|" in l]
        except Exception as e:                       # noqa: BLE001 - retry any transient failure, then give up
            if attempt == 2:
                raise
            import time
            time.sleep(10 * (attempt + 1))


def describe_images(cat_dir, niche_name, key, model=cs.MODEL, log=print, progress=None, workers=4):
    sheets = sorted(f for f in os.listdir(os.path.join(cat_dir, "sheets_img")) if f.endswith(".jpg"))
    out, done = [], [0]

    def one(f):
        sheet = os.path.splitext(f)[0]
        lines = _ask_sheet((key, model), IMG_PROMPT.format(niche=niche_name, sheet=sheet), os.path.join(cat_dir, "sheets_img", f))
        good = [l for l in lines if re.match(rf"^{re.escape(sheet)}:\d+\|", l)]
        done[0] += 1
        if progress:
            progress(done[0] / len(sheets), f"pictures: sheet {done[0]}/{len(sheets)}")
        return good
    with ThreadPoolExecutor(workers) as ex:
        for lines in ex.map(one, sheets):
            out += lines
    open(os.path.join(cat_dir, "notes_img.txt"), "w", encoding="utf-8").write(
        "# sheet:pos|tags|description   (written by describe.py)\n" + "\n".join(out) + "\n")
    log(f"{len(out)} pictures described")
    return len(out)


def describe_clips(cat_dir, niche_name, key, model=cs.MODEL, log=print, progress=None, workers=4):
    sheets = sorted(f for f in os.listdir(os.path.join(cat_dir, "sheets_clips")) if f.endswith(".jpg"))
    out, done = [], [0]

    def one(f):
        lines = _ask_sheet((key, model), CLIP_PROMPT.format(niche=niche_name), os.path.join(cat_dir, "sheets_clips", f))
        good = [l for l in lines if re.match(r"^\d+\|\d\|", l)]
        done[0] += 1
        if progress:
            progress(done[0] / len(sheets), f"clips: sheet {done[0]}/{len(sheets)}")
        return good
    with ThreadPoolExecutor(workers) as ex:
        for lines in ex.map(one, sheets):
            out += lines
    out.sort(key=lambda l: int(l.split("|")[0]))
    open(os.path.join(cat_dir, "notes_clips.txt"), "w", encoding="utf-8").write(
        "# idx|quality 1-5|flags|tags|description   (written by describe.py)\n" + "\n".join(out) + "\n")
    log(f"{len(out)} clips described")
    return len(out)
