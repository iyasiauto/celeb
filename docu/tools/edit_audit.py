"""
edit_audit.py - is this shot list a real edit in its template, or a slideshow of clips?

Checks the timed plan (scenes.json) against the template's playbook (templates/<id>/template.json, through
docu/registry.py) and the script itself:

    devices      every device of the template appears at least as often as the playbook asks (per 10 minutes)
    variety      enough different devices
    density      template graphics per minute; the longest stretch with none; runs of plain clips / photos
    chapters     a heading every ~N seconds (chapter, doctitle, segment, breaking, gzhead / almhead overlays)
    places       places the narration names (kit gazetteer) are shown on maps
    numbers      sentences with figures are matched by number devices (stat, versus, bars, ledger, timeline...)
    quotes       quotations in the script are set as quote scenes
    repeats      no clip or picture twice
    finish       texture on footage, overlays on headings (docu/asset_mix.py), sound effects per minute

edl.py runs it at `plan` (report) and before `render` (gate: any FAIL stops the render; DOCU_AUDIT=warn turns the
gate into a warning for a deliberate exception). Standalone:

    python docu/tools/edit_audit.py <work_dir>/scenes.json --template paper --script data/script.txt
"""

import json
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DOCU = os.path.dirname(HERE)
sys.path.insert(0, DOCU)

FOOTAGE = {"clip", "photo"}
RICH_OVERLAYS = {"gzhead", "almhead", "gztag", "almtag", "place", "doclower", "lower", "newslower", "chip", "ddlabel", "ddtab"}
HEADING_TYPES = {"chapter", "doctitle", "segment", "breaking", "title"}
HEADING_OVERLAYS = {"gzhead", "almhead", "ddlabel"}
PASSIVE_OVERLAYS = {"fadein", "fadeout", "flash", "caption", "source", "ticker", "bug"}
NUMBER_DEVICES = {"stat", "gzstat", "gzversus", "gzindex", "gzdelta", "gzgiants", "gzdivide", "bars", "almbars", "almgrowth",
                  "almshare", "almdots", "almsplit", "almstat", "ledger", "ledgerlist", "measure", "sizechart", "cells",
                  "gauge", "columns", "scoreboard", "timeline", "almdistrict"}
MAP_DEVICES = {"map", "geo"}
NUM_WORDS = r"(hundred|thousand|million|billion|trillion|percent|per cent|dozen|half|twice|double|triple)"


def _overlays(s):
    return [o.get("type") for o in s.get("overlays", []) if o.get("type")]


def device_counts(scenes):
    c = {}
    for s in scenes:
        c[s["type"]] = c.get(s["type"], 0) + 1
        for o in set(_overlays(s)):
            c["ov:" + o] = c.get("ov:" + o, 0) + 1
        for it in s.get("items", []) if s["type"] == "collage" else []:
            if it.get("k") == "cut":
                c["cutout"] = c.get("cutout", 0) + 1
    return c


def is_graphic(s):
    if s["type"] not in FOOTAGE:
        return True
    return bool(set(_overlays(s)) & RICH_OVERLAYS)


def sentences(text):
    return [x.strip() for x in re.split(r"(?<=[.!?])\s+|\n+", text) if x.strip()]


def places_in(text, max_city_rank=6):
    """place names from the kit gazetteer that the script mentions (countries, states/provinces, larger cities)"""
    try:
        g = json.load(open(os.path.join(os.environ.get("DOCU_KIT") or os.path.join(os.path.dirname(DOCU), "media", "kit"),
                                        "maps", "gazetteer.json"), encoding="utf-8"))
    except Exception:          # noqa: BLE001 - no kit maps: skip the place check
        return []
    names = set()
    for c in g.get("countries", []):
        if c.get("name"):
            names.add(c["name"])
    for a in g.get("admin1", []):
        if a.get("a3") in ("USA", "CAN", "GBR", "AUS", "IND", "PAK", "DEU", "FRA", "ITA", "ESP", "MEX", "BRA", "CHN", "JPN", "RUS",
                           "TUR", "IRN", "IRQ", "ISR", "EGY", "NGA", "ZAF"):
            if a.get("name"):
                names.add(a["name"])
    for c in g.get("cities", []):
        if c.get("name") and (c.get("rank") or 99) <= max_city_rank and len(c["name"]) > 3:
            names.add(c["name"])
    found = []
    for n in sorted(names, key=len, reverse=True):
        if re.search(r"(?<![A-Za-z])" + re.escape(n) + r"(?![A-Za-z])", text):
            if not any(n in f for f in found):
                found.append(n)
    return found


def map_text(scenes):
    t = []
    for s in scenes:
        if s["type"] in MAP_DEVICES:
            for k in ("pins", "names", "dots", "labels"):
                for p in s.get(k, []) or []:
                    t += [str(p.get("label", "")), str(p.get("text", "")), str(p.get("sub", ""))]
            t.append(str(s.get("title", "")))
            for h in s.get("highlight", []) or []:
                t.append(str(h.get("id", "")))
    return " ".join(t)


def run(scenes, pb, script_text="", sfx_events=None, finish_summary=None):
    a = dict(pb.get("audit") or {})
    total = sum(s["duration"] for s in scenes) or 1.0
    minutes = total / 60.0
    counts = device_counts(scenes)
    fails, warns, oks = [], [], []

    # 1) the template's devices, scaled to the length of the video
    for d in pb.get("devices", []):
        x = float(d.get("min_per_10min", 0)) * minutes / 10.0
        need = math.ceil(x - 1e-9) if minutes >= 5 else int(x + 0.5)      # a short teaser is not held to a full video's quota
        have = counts.get(d["type"], 0)
        if need <= 0:
            continue
        if have < need:
            fails.append(f"{d['type']}: {have} of {need} - {d.get('use', '')}")
        else:
            oks.append(f"{d['type']} {have}/{need}")

    # 2) variety
    used = {k for k, v in counts.items() if v and k not in FOOTAGE and k not in ("ov:" + p for p in PASSIVE_OVERLAYS)
            and k != "cutout" and k != "blank"}
    md = int(a.get("min_distinct_devices") or 0)
    if md and minutes < 5:
        md = min(md, max(3, round(md * minutes / 5)))
    if md and len(used) < md:
        fails.append(f"variety: {len(used)} different devices, the template needs {md}+ ({', '.join(sorted(used)) or 'none'})")

    # 3) density
    graphics = sum(1 for s in scenes if is_graphic(s))
    gpm = graphics / minutes
    if a.get("graphics_per_min") and gpm < float(a["graphics_per_min"]):
        fails.append(f"density: {gpm:.2f} template graphics a minute, needs {a['graphics_per_min']} "
                     f"({graphics} in {minutes:.1f} min - add about {math.ceil(float(a['graphics_per_min']) * minutes) - graphics})")
    gaps, t_last, run_n, runs = [], 0.0, 0, []
    for s in scenes:
        if is_graphic(s):
            if s["t0"] - t_last > float(a.get("max_gap_s") or 1e9):
                gaps.append((t_last, s["t0"]))
            t_last = s["t0"] + s["duration"]
            if run_n > int(a.get("max_plain_run") or 1e9):
                runs.append((run_n, s["id"]))
            run_n = 0
        elif s["duration"] >= 2.5:
            run_n += 1                    # montage cuts under 2.5 s (a fast cold open) are not a slideshow
    if total - t_last > float(a.get("max_gap_s") or 1e9):
        gaps.append((t_last, total))
    if gaps:
        fmt = lambda x: f"{int(x) // 60}:{int(x) % 60:02d}"                 # noqa: E731
        fails.append(f"gaps: {len(gaps)} stretches over {a.get('max_gap_s')} s with no template graphic - "
                     + ", ".join(f"{fmt(x)}-{fmt(y)}" for x, y in gaps[:8]) + (" ..." if len(gaps) > 8 else ""))
    if runs:
        worst = max(r[0] for r in runs)
        msg = f"plain runs: {len(runs)} runs of more than {a.get('max_plain_run')} plain clips/photos in a row (longest {worst}, before {runs[0][1]})"
        (fails if worst > 2 * int(a.get("max_plain_run") or 1) else warns).append(msg)

    # 4) clip share
    clips = sum(s["duration"] for s in scenes if s["type"] == "clip") / total
    lo, hi = (a.get("clip_share") or [0, 1])
    if clips < lo or clips > hi:
        msg = f"clip share {clips:.0%}, the template wants {lo:.0%}-{hi:.0%}"
        (fails if clips < lo * 0.5 else warns).append(msg)

    # 5) chapters
    # a template's own heading devices count too (family "heading" in its playbook, e.g. finalreel's castcard)
    own = {d["type"] for d in pb.get("devices", []) if d.get("family") == "heading"}
    own_t = {t for t in own if not t.startswith("ov:")}
    own_o = {t[3:] for t in own if t.startswith("ov:")}
    heads = sum(1 for s in scenes if s["type"] in HEADING_TYPES | own_t or set(_overlays(s)) & (HEADING_OVERLAYS | own_o))
    ce = float(a.get("chapter_every_s") or 0)
    if ce:
        need = max(1, int(total // ce))
        if heads < need:
            fails.append(f"chapters: {heads} headings for {minutes:.0f} min, needs {need} (one every ~{ce:.0f} s)")

    # 6) places -> maps
    if script_text:
        pl = places_in(script_text)
        maps = sum(counts.get(k, 0) for k in MAP_DEVICES)
        if len(pl) >= 2:
            need = max(1, math.ceil(len(pl) / 4))
            if maps < need:
                fails.append(f"maps: the script names {len(pl)} places ({', '.join(pl[:10])}{'...' if len(pl) > 10 else ''}) "
                             f"but the edit has {maps} map scenes - needs {need}")
            mt = map_text(scenes).lower()
            missing = [p for p in pl if p.lower() not in mt]
            if missing and maps:
                warns.append(f"places named but not labelled on any map: {', '.join(missing[:10])}")

    # 7) numbers -> number devices
    if script_text:
        num = [x for x in sentences(script_text) if re.search(r"\d", x) or re.search(NUM_WORDS, x, re.I)]
        own_num = {d["type"] for d in pb.get("devices", []) if d.get("family") in ("number", "timeline")}
        have = sum(counts.get(k, 0) for k in set(NUMBER_DEVICES) | own_num) + sum(
            1 for s in scenes for o in s.get("overlays", []) if o.get("type") == "chip" and re.search(r"\d", str(o.get("text", ""))))
        need = math.ceil(len(num) / 6)
        if need and have < need:
            fails.append(f"numbers: {len(num)} sentences carry figures but only {have} number graphics - needs {need} "
                         f"(stat / versus / bars / ledger / timeline / measure ... in this template)")

    # 8) quotes
    if script_text:
        q = [m for m in re.findall(r"[\"“]([^\"”]{25,300})[\"”]", script_text) if len(m.split()) >= 6]
        if q and counts.get("quote", 0) < math.ceil(len(q) / 2):
            warns.append(f"quotes: the script quotes {len(q)} times, the edit has {counts.get('quote', 0)} quote scenes")

    # 9) repeats - the same footage twice is a FAIL; a photo reused only as the dimmed ground of a graphic is a warn
    shown = {"clip", "photo", "depth", "spotlight", "tv", "split", "card"}
    seen, rep, soft = {}, [], []
    for s in scenes:
        key = None
        if s["type"] == "clip":
            key = (os.path.basename(s.get("src", "")), round(float(s.get("start", 0)) / 3))
        elif s.get("img"):
            key = (re.sub(r"_[A-Za-z0-9]+_[0-9a-f]{4}\.(jpg|png)$", "", s["img"]),)     # the picture, not its grade
        if not key or s.get("repeat_ok"):
            continue
        if key in seen:
            first = seen[key]
            if s["type"] in shown or first[1] in shown:
                rep.append(f"{s['id']}={first[0]}")
            else:
                soft.append(f"{s['id']}={first[0]}")
        else:
            seen[key] = (s["id"], s["type"])
    if rep:
        fails.append(f"repeats: the same shot twice - {', '.join(rep[:10])}{' ...' if len(rep) > 10 else ''}")
    if soft:
        warns.append(f"backgrounds reused under graphics: {', '.join(soft[:8])}")

    # 10) finishing layers and sound
    tex = sum(1 for s in scenes if s.get("texture_png"))
    fx = sum(1 for s in scenes if s.get("fx"))
    if finish_summary is not None and tex == 0 and fx == 0:
        warns.append("finish: no texture and no overlays applied (assets folder missing? see docu/asset_mix.py)")
    if sfx_events is not None and a.get("sfx_per_min"):
        spm = sfx_events / minutes
        if spm < float(a["sfx_per_min"]) * 0.6:
            warns.append(f"sound: {spm:.1f} effects a minute, the template's sound design expects ~{a['sfx_per_min']}")

    score = max(0, 100 - 10 * len(fails) - 3 * len(warns))
    return dict(template=pb.get("id"), style=pb.get("style"), minutes=round(minutes, 1), score=score,
                fails=fails, warns=warns, ok=oks, graphics_per_min=round(gpm, 2), clip_share=round(clips, 3),
                distinct_devices=sorted(used), headings=heads)


def report(r, log=print):
    log(f"EDIT AUDIT  {r['template']}{' / ' + r['style'] if r.get('style') else ''}  ·  {r['minutes']} min  ·  score {r['score']}/100  ·  "
        f"{r['graphics_per_min']} graphics/min · clips {r['clip_share']:.0%} · {len(r['distinct_devices'])} devices · {r['headings']} headings")
    for f in r["fails"]:
        log(f"  FAIL  {f}")
    for w in r["warns"]:
        log(f"  warn  {w}")
    if not r["fails"]:
        log("  pass  the edit uses its template in full")


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("scenes")
    ap.add_argument("--template", required=True, help="template or style id")
    ap.add_argument("--script")
    a = ap.parse_args()
    import registry
    pb = registry.resolve(a.template)
    sc = json.load(open(a.scenes, encoding="utf-8"))
    txt = open(a.script, encoding="utf-8-sig").read() if a.script else ""
    r = run(sc, pb, txt)
    report(r)
    sys.exit(1 if r["fails"] else 0)


if __name__ == "__main__":
    main()
