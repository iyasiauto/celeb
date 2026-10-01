"""
claude_shotlist.py - Claude writes the shot list the way the hand-made videos were edited.

Claude gets: the editing method (docu/VISUAL_SYNC_GUIDE.md), the style's rules and a finished example
shot list in that style, the scene reference (docu/templates/README.md), the helper API (shots.py),
then the job: script with paragraph times, every usable clip and picture with its description
(unused ones first), the drawn props, map coordinates for the niche, and this video's variety picks.

It answers with the body of build.py (at(...) calls + ACTS). The studio then runs `plan` and sends
any problems back (missing cue, short clip, clip share off, repeats) until the plan is clean.
With ai_qa on, the stills contact sheets go back to Claude for a visual check, like the manual QA.

The model and effort are settings; the default is Claude Opus 5.5 at high effort.
Server-side fallback ("default") is on, so a rare classifier refusal is retried on another model.
"""

import base64
import io
import json
import os
import re

import anthropic

HERE = os.path.dirname(os.path.abspath(__file__))
DOCU = os.path.dirname(HERE)
MODEL = "claude-opus-5-5"

RULES = """You are the editor of a faceless documentary / investigative YouTube channel. You write the shot list for one
video: a Python file body that the channel's engine renders. The narration is already recorded; every cut must
land on the spoken word and every picture must show what the narrator is talking about at that moment.

How you work (this is the channel's method - follow it exactly):
1. Split the script into beats: one sentence or clause = one visual idea. Typical scene length 5-8 s in the calm
   documentary style, 3-6 s in the other styles. About one scene per sentence; a long sentence may take two.
2. For each beat ask "what is the narrator pointing at right now?" and pick the visual type:
   place -> map move/pin or an establishing photo with place(...) caption; named institution/person -> photo or clip
   with who(...) lower third; everyday action -> footage clip; one number -> big(...); comparison -> bars(...);
   a list -> ledger(...) that writes in on each word; documents/sources -> board([...]) with pc()/strip();
   the key line of a section -> card(...) with the stressed words in ACC; an abstract idea -> the video's recurring
   device; chapter start -> heading(n, title, bg); emotional beat -> people/families from behind or at a distance.
3. Pick the file: literal first (an ambulance when the narrator says ambulance), specific beats generic, right place
   and era (never label a picture from another country as the local place), nothing that contradicts the words
   (no visible captions/logos), privacy (no readable names or ID numbers; for accusations show documents or
   buildings, not identifiable faces), clip length must cover the beat (cl(i, then=(j, k)) joins more shots of the
   same subject), no picture twice in a row and at most twice per video, prefer material marked as unused.
4. Claims look like claims: "reported", "claimed", "asserted" in the script are labelled so on screen; any number you
   make up for an example is labelled "illustrative".
5. Give the video ONE recurring device the audience learns once (a ledger that grows, an object on a paper table,
   a map route, an evidence board) that returns at the opening, in the middle and at the end. Vary the device,
   the opening and the chart types from video to video.
6. Structure: a cold open (no heading), then title_card(...) with the video's title, then one heading per act
   (every 1.5-3 minutes, 5-9 headings for a 15-20 minute video), and an ending that returns to the device.
   The first scene gets fadein(...), the last fadeout(...).
7. Use "@phrase" inside a scene to make an element appear exactly on its word (list rows, numbers, pins, strips,
   the key line of a card). A number is seconds from the scene start.

Hard rules for the code:
- Cues: the first argument of at() is a phrase copied EXACTLY from the script (4-8 words, same spelling and
  punctuation inside the words), in script order. It must not occur again between the previous cue and itself.
  "@phrase" values must occur in the script after their scene's cue.
- Only use clip indices i and picture keys from the lists you are given; prop names from the props list.
- Only use the helpers listed below. No imports, no edl.setup, no edl.main, no other code than at(...) calls,
  small local helper functions/constants if you need them, and finally ACTS.
- End with ACTS = [None, "<cue of the first heading>", "<cue of the second heading>", ...] - the cues where a new
  music bed starts (None = the start of the video).
- Reply with exactly one ```python fenced block and nothing else.
"""

HELPERS = """Helpers available in the shot list (already imported):
  at(cue, scene)                     place a scene on the cue phrase
  ph(key, move=None, zoom=1.08, focus=[x, y])          photo with a slow move ("in","out","left","right","up")
  cl(i, then=(j, k), skip=0.0, zoom=1.03)              catalog clip i (plus more shots to cover a long beat)
  place(scene, "Kiryas Joel, New York", "sub", at=0.6) location caption overlay
  who(scene, "Hatzalah", "volunteer ambulance service", at=0.5)   lower third
  fadein(scene, d=1.2) / fadeout(scene, d=2.2)
  heading(n, "Title", bg_key, sub=None)               chapter heading (kicker style comes from this video's variety picks)
  title_card("A documentary", "The Title", bg_key)
  card(("line", at, color, size), ("key line", "@word", ACC, 84), bg=key)   1-3 lines over a darkened photo
  big("91.5 %", "SPOKE YIDDISH AT HOME", "note", bg=key, source="Source: ...", count=False, countFor=1.4, size=170)
  bars("Title", [("Label", value, "text", at_or_@phrase, dict(color=ACC))], bg=key, max=100, note="...", source="...")
  ledger("Title", [("Label", "value", at_or_@phrase, color_or_None)], bg=key, total=dict(label=..., value=..., at=...))
  board([pc(key, x, y, w, rot=-2, at=0.1, grade="none"), strip("typed label", x, y, at, size=36, type=False),
         title_("Big title", x, y, at=0.3, size=60), prop("prop_envelope.png", x, y, h, at=0.1, rot=-3)])   1920x1080 canvas
  mapscene(stops=[dict(at=0, lon=, lat=, scale=5200), dict(at=0.4, lon=, lat=, scale=17000, d=3.0)],
           pins=[dict(lon=, lat=, label="", sub="", at=1.2, side="left"|"right", size=30)],
           highlight=[dict(id="USA-3559", at=0.3)], names=[dict(text=, lon=, lat=, at=, size=)],
           routes=[dict(**{"from": [lon, lat]}, to=[lon, lat], at=0.6, d=2.0, dash=True, label="")],
           dots=[dict(lon=, lat=, at=, label="")], caption="text", usa=True)    scale ~1150 = USA, 5200 = a state, 17000 = a metro area
  spotlight(key, center=[0.5, 0.55], radius=[0.3, 0.34], label="through a child's desk")
  depth(key, subject=[x, y], hit=0.6)                person lifted off the background (use rarely)
  stat(...), words([...]), quote(...), collage(...), and every scene type in the scene reference (as dict(type=...))
Colours: ACC (this video's accent), RUST (warnings, "no"), SAGE (positive).
"""


def _read(p, limit=None):
    try:
        t = open(p, encoding="utf-8").read()
        return t[:limit] if limit else t
    except OSError:
        return ""


def system_blocks(st):
    """st: the style's info (project.style_info)"""
    example = _read(st.get("example_path") or "")
    rules = _read(st["rules_path"]) if st.get("rules_path") else ""
    guide = _read(os.path.join(DOCU, "VISUAL_SYNC_GUIDE.md"))
    scenes = _read(os.path.join(DOCU, "templates", "README.md"))
    static = (RULES + "\n" + HELPERS +
              f"\n\n=== STYLE: {st['name']} (engine theme \"{st['theme']}\") ===\n{st.get('blurb', '')}\n"
              "The theme's full rules are in the scene reference below under \"" + st.get("readme", "") + "\".\n" +
              (f"\n=== THIS TEMPLATE'S OWN RULES ===\n{rules}\n" if rules else "") +
              "\n=== THE CHANNEL'S METHOD (VISUAL_SYNC_GUIDE.md) ===\n" + guide +
              "\n\n=== SCENE REFERENCE (docu/templates/README.md) ===\n" + scenes +
              "\n\n=== A FINISHED SHOT LIST IN THIS STYLE ===\n"
              "It defines its own small helpers at the top; yours (listed above) do the same jobs. Study its pacing, "
              "variety of scene types, device and how cues and @phrases are chosen.\n\n" + example)
    return [{"type": "text", "text": static, "cache_control": {"type": "ephemeral"}}]


def job_message(job, niche, script, para_times, duration, clips, images, props, variety):
    def fmt_clip(c):
        return f"{c['i']}\t{c['dur']}s\tq{c['q']}\t{','.join(c['tags'])}\t{c['desc']}" + ("\t(used before)" if c["used"] else "")

    def fmt_img(r):
        return f"{r['key']}\t{','.join(r['tags'])}\t{r['desc']}" + ("" if r.get("wide", True) else "\t(small)") + \
               ("\t(used before)" if r["used"] else "")
    lines = [
        f"Title: {job['title']}",
        f"Style: {job['style']}   Niche: {niche['name']}",
        f"Voiceover length: {duration:.1f} s ({duration / 60:.1f} min)",
        f"Clip share target: about {job.get('clip_share', 30)} % of the running time in footage clips, the rest photos and graphics.",
        f"This video's variety picks: {json.dumps(variety)} (headings, accent and moves are applied automatically).",
        f"Map help for this niche: {niche.get('map_hint', '')}",
        "", "=== SCRIPT (each paragraph with the second it starts in the voiceover) ===",
    ]
    for t, p in zip(para_times, [p for p in script.split("\n") if p.strip()]):
        lines.append(f"[{t:7.1f}s] {p.strip()}")
    lines += ["", f"=== CLIPS ({len(clips)}; index, length, quality, tags, description) ==="] + [fmt_clip(c) for c in clips]
    lines += ["", f"=== PICTURES ({len(images)}; key, tags, description) ==="] + [fmt_img(r) for r in images]
    lines += ["", "=== PROPS / CUT-OUTS for boards ===", ", ".join(props),
              "", "Write the complete shot list now."]
    return "\n".join(lines)


def _client(key):
    return anthropic.Anthropic(api_key=key) if key else anthropic.Anthropic()


def ask(client, system, messages, model=MODEL, effort="high", on_text=None):
    with client.beta.messages.stream(
        model=model, max_tokens=64000, system=system, messages=messages,
        thinking={"type": "adaptive"}, output_config={"effort": effort},
        betas=["server-side-fallback-2026-07-01"], fallbacks="default",
    ) as stream:
        n = 0
        for ev in stream:
            if ev.type == "content_block_delta" and getattr(ev.delta, "type", "") == "text_delta":
                n += len(ev.delta.text)
                if on_text:
                    on_text(n)
        msg = stream.get_final_message()
    if msg.stop_reason == "refusal":
        raise RuntimeError("Claude declined this request (refusal). Try again or use the offline shot list.")
    text = "".join(b.text for b in msg.content if b.type == "text")
    if msg.stop_reason == "max_tokens":
        raise RuntimeError("the shot list was cut off (max_tokens)")
    return msg, text


def extract_code(text):
    m = re.findall(r"```(?:python)?\s*\n(.*?)```", text, re.S)
    if not m:
        raise RuntimeError("Claude's answer had no ```python block")
    code = max(m, key=len).strip()
    code = "\n".join(l for l in code.split("\n")
                     if not re.match(r"\s*(import |from |edl\.setup|edl\.main|shots\.init)", l))
    if "ACTS" not in code:
        code += "\n\nACTS = [None]\n"
    compile(code, "shotlist", "exec")
    return code


class Session:
    """one shot-list conversation (append-only, so fixes keep the context and the cache)"""

    def __init__(self, key, style_info, model=MODEL, effort="high", log=print):
        self.client = _client(key)
        self.system = system_blocks(style_info)
        self.model, self.effort, self.log = model, effort, log
        self.messages = []

    def first(self, user_text, on_text=None):
        self.messages.append({"role": "user", "content": user_text})
        return self._turn(on_text)

    def fix(self, problems, on_text=None, images=None):
        content = []
        for b64 in images or []:
            content.append({"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": b64}})
        content.append({"type": "text", "text": problems})
        self.messages.append({"role": "user", "content": content})
        return self._turn(on_text)

    def _turn(self, on_text):
        for attempt in range(2):
            try:
                msg, text = ask(self.client, self.system, self.messages, self.model, self.effort, on_text)
                self.messages.append({"role": "assistant", "content": msg.content})
                u = msg.usage
                self.log(f"Claude: {u.input_tokens} in (+{getattr(u, 'cache_read_input_tokens', 0) or 0} cached), "
                         f"{u.output_tokens} out")
                return extract_code(text)
            except SyntaxError as e:
                self.messages.append({"role": "assistant", "content": msg.content})
                self.messages.append({"role": "user", "content": f"That code does not compile: {e}. Reply with the full corrected shot list."})
            except anthropic.RateLimitError:
                import time
                time.sleep(30)
        raise RuntimeError("Claude could not produce a valid shot list")


def jpeg_b64(path, width=1600):
    from PIL import Image
    im = Image.open(path).convert("RGB")
    if im.width > width:
        im = im.resize((width, int(im.height * width / im.width)))
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=80)
    return base64.standard_b64encode(buf.getvalue()).decode()
