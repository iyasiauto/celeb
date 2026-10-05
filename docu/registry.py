"""
registry.py - every template and style of the kit, found by folder, so a new one is a folder you drop in.

    templates/<id>/template.json   a TEMPLATE: the engine look (theme), its settings, its devices with how often
                                   each must appear, its rules, previews and worked examples. A brand-new look can
                                   bring its own theme (theme_def) and scene code (scene_files) - no engine edits.
    styles/<id>/style.json         a STYLE (like Frontier's): one template plus overrides - palette, fonts, grade,
                                   pacing, sound, extra rules and device minimums. Many styles can share one template
                                   without mixing: each video pins exactly one (projects/<slug>/project.json).

    python docu/registry.py list                       every template and style, and whether it is installed
    python docu/registry.py show <template|style>      the playbook: what to use, how often, previews, example code
    python docu/registry.py check                      validate every folder against the engine
    python docu/registry.py new-template <id> --from <template>
    python docu/registry.py new-style <id> --template <template>

Agents: run `show` for the video's template BEFORE writing a shot list, open its preview images, and read one of
its example projects in full. The edit audit (docu/tools/edit_audit.py) holds the shot list to these minimums.
"""

import argparse
import glob
import json
import math
import os
import re
import shutil
import sys

DOCU = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(DOCU)
TPL_DIR = os.environ.get("DOCU_TEMPLATES") or os.path.join(ROOT, "templates")
STY_DIR = os.environ.get("DOCU_STYLES") or os.path.join(ROOT, "styles")
ALIASES = {"almanac2": "almanac", "gazetteer": "almanac", "vox": "paper", "news": "broadcast", "lab": "forensic",
           "court": "expedition", "doc": "documentary"}


def _load(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def templates():
    out = {}
    for p in sorted(glob.glob(os.path.join(TPL_DIR, "*", "template.json"))):
        d = os.path.dirname(p)
        if os.path.basename(d).startswith("_"):
            continue
        t = _load(p)
        t.setdefault("id", os.path.basename(d))
        t["dir"] = d
        need = [os.path.join(d, f) if not os.path.isabs(f) else f for f in t.get("scene_files", [])]
        need += [os.path.join(ROOT, f) for f in t.get("requires", [])]
        missing = [os.path.relpath(f, ROOT) for f in need if not os.path.exists(f)]
        t["installed"] = not missing
        t["missing"] = missing
        out[t["id"]] = t
    return out


def styles():
    out = {}
    for p in sorted(glob.glob(os.path.join(STY_DIR, "*", "style.json"))):
        d = os.path.dirname(p)
        if os.path.basename(d).startswith("_"):
            continue
        s = _load(p)
        s.setdefault("id", os.path.basename(d))
        s["dir"] = d
        s.setdefault("template", s.get("theme"))
        out[s["id"]] = s
    return out


def resolve(name):
    """a template id, a style id or an engine theme name -> the merged playbook"""
    T, S = templates(), styles()
    name = (name or "").strip()
    sty = None
    if name in S:
        sty = S[name]
        name = sty.get("template") or sty.get("theme")
    tid = ALIASES.get(name, name)
    if tid not in T:
        # an engine theme with no template folder (e.g. almanac_v1): a bare playbook, audit uses defaults
        base = T.get(ALIASES.get(tid, ""), None)
        pb = dict(id=tid, name=tid, theme=tid, devices=[], audit={}, rules=[], installed=True, missing=[])
        if base:
            pb.update({k: v for k, v in base.items() if k not in ("id", "name", "theme")})
        pb["theme"] = tid
    else:
        pb = json.loads(json.dumps(T[tid]))
    if not pb.get("installed", True):
        raise SystemExit(f"template {pb['id']!r} is not installed - missing: {', '.join(pb['missing'])}")
    if sty:
        pb["style"] = sty["id"]
        pb["name"] = f"{sty.get('name', sty['id'])} ({pb['name']})"
        ov = sty.get("overrides", {})
        for k in ("grade", "grain", "xfade", "sfx_style"):
            if k in ov:
                pb[k] = ov[k]
        for k in ("sfx", "xfade"):                      # the older Docu Studio style.json keys
            if k in sty and k == "sfx":
                pb["sfx_style"] = sty[k]
            elif k in sty:
                pb[k] = sty[k]
        pb["vary"] = {k: ov[k] for k in ("pal", "fonts", "map") if k in ov}
        mins = sty.get("devices", {})
        for dv in pb.get("devices", []):
            if dv["type"] in mins:
                dv["min_per_10min"] = mins[dv["type"]]
        known = {d["type"] for d in pb.get("devices", [])}
        for k, v in mins.items():
            if k not in known:
                pb.setdefault("devices", []).append(dict(type=k, family="style", min_per_10min=v, use="required by the style"))
        pb["audit"] = dict(pb.get("audit", {}), **sty.get("audit", {}))
        rules = sty.get("rules")
        if isinstance(rules, str) and os.path.exists(os.path.join(sty["dir"], rules)):
            pb["rules_md"] = open(os.path.join(sty["dir"], rules), encoding="utf-8").read()
        elif isinstance(rules, list):
            pb["rules"] = pb.get("rules", []) + rules
        if sty.get("example"):
            ex = os.path.join(sty["dir"], sty["example"])
            if os.path.exists(ex):
                pb["examples"] = [os.path.relpath(ex, ROOT)] + pb.get("examples", [])
    return pb


def _static_scene_files():
    html = open(os.path.join(DOCU, "engine.html"), encoding="utf-8").read()
    return set(re.findall(r'src="(scenes_[^"]+\.js)"', html))


def engine_cfg(pb):
    """what render.py hands the page for this playbook: its own theme, its own scene code, style overrides"""
    import pathlib
    cfg = {}
    if pb.get("theme_def"):
        cfg["themeDef"] = pb["theme_def"]
    files = []
    static = _static_scene_files()
    for p in sorted(glob.glob(os.path.join(DOCU, "scenes_*.js"))):    # a scenes file dropped into docu/ loads too
        if os.path.basename(p) not in static:
            files.append(p)
    for f in pb.get("scene_files", []):
        p = f if os.path.isabs(f) else os.path.join(pb.get("dir", ROOT), f)
        if os.path.exists(p) and p not in files:
            files.append(p)
    if files:
        cfg["scenes"] = [pathlib.Path(p).as_uri() for p in files]
    if pb.get("vary"):
        cfg["vary_style"] = pb["vary"]
    return cfg


def engine_devices():
    """every scene and overlay type the engine (and any dropped-in scene file) defines"""
    found = set()
    files = glob.glob(os.path.join(DOCU, "*.js")) + glob.glob(os.path.join(TPL_DIR, "*", "*.js"))
    for p in files:
        src = open(p, encoding="utf-8").read()
        found |= set(re.findall(r"^SCENES\.([A-Za-z0-9_]+)\s*=", src, re.M))
        found |= {"ov:" + x for x in re.findall(r"^OVERLAYS\.([A-Za-z0-9_]+)\s*=", src, re.M)}
        m = re.search(r"const OVERLAYS = \{(.*?)\n\};", src, re.S)
        if m:
            found |= {"ov:" + x for x in re.findall(r"^\s{2}([a-z]+): \(o", m.group(1), re.M)}
    return found


# ------------------------------------------------------------------ the gallery: one working example per device
def gallery_examples():
    try:
        sys.path.insert(0, os.path.join(DOCU, "templates"))
        import gallery
        out = {}
        for name, spec, themes in gallery.specs():
            t = spec.get("type")
            keys = [t] + ["ov:" + o["type"] for o in spec.get("overlays", [])]
            for k in keys:
                out.setdefault(k, (name, spec, themes))
        return out
    except Exception:          # noqa: BLE001
        return {}


def _preview(pb, dev):
    t = dev[3:] if dev.startswith("ov:") else dev
    cands = [os.path.join(ROOT, pb.get("preview_dir", ""), t + ".jpg")]
    cands += sorted(glob.glob(os.path.join(ROOT, pb.get("preview_dir", "") or "-", t + "_*.jpg")))
    cands += glob.glob(os.path.join(DOCU, "templates", "previews", "*", t + ".jpg"))
    cands += sorted(glob.glob(os.path.join(DOCU, "templates", "previews", "*", t + "_*.jpg")))
    for c in cands:
        if os.path.exists(c):
            return os.path.relpath(c, ROOT)
    return None


def need_for(min_per_10min, minutes):
    """how many of a device a video of this length needs (the edit audit uses the same rule)"""
    x = float(min_per_10min or 0) * minutes / 10.0
    return math.ceil(x - 1e-9) if minutes >= 5 else int(x + 0.5)      # a short teaser is not held to a full video's quota


def distinct_for(md, minutes):
    md = int(md or 0)
    return min(md, max(3, round(md * minutes / 5))) if md and minutes < 5 else md


def show(name, minutes=15.0):
    pb = resolve(name)
    ex = gallery_examples()
    a = pb.get("audit", {})
    print(f"# {pb['name']}   (template: {pb['id']}, engine theme: {pb['theme']})\n")
    if pb.get("best_for"):
        print(f"Best for: {pb['best_for']}")
    if pb.get("look"):
        print(f"Look: {pb['look']}")
    print(f"\nSettings for edl.setup(): theme={pb['theme']!r}, grade={pb.get('grade')!r}, grain={pb.get('grain')}, "
          f"xfade={pb.get('xfade')}, sfx_style={pb.get('sfx_style')!r}" + (f", style={pb['style']!r}" if pb.get("style") else ""))
    if pb.get("preview_sheet"):
        print(f"Preview sheet (LOOK AT IT): {pb['preview_sheet']}")
    if pb.get("examples"):
        print("Worked examples (READ ONE IN FULL before writing): " + ", ".join(pb["examples"]))
    if pb.get("starter"):
        print(f"Starter skeleton: {pb['starter']}")
    if a:
        print(f"\nThe edit audit holds a {minutes:.0f}-minute video to: clips {int(a.get('clip_share', [0, 1])[0] * 100)}-"
              f"{int(a.get('clip_share', [0, 1])[1] * 100)} % of the time, at least {a.get('graphics_per_min')} template graphics a minute, "
              f"no stretch over {a.get('max_gap_s')} s without one, at most {a.get('max_plain_run')} plain shots in a row, "
              f"a chapter heading every ~{a.get('chapter_every_s')} s, {distinct_for(a.get('min_distinct_devices'), minutes)}+ different devices, "
              f"~{a.get('sfx_per_min')} sound effects a minute; every place named on a map, every stressed number shown.")
    print(f"\n## Devices - and how many a {minutes:.0f}-minute video needs at least\n")
    for d in pb.get("devices", []):
        need = need_for(d["min_per_10min"], minutes)
        prev = _preview(pb, d["type"])
        print(f"- {d['type']:14s} >= {need:<3d} {d['use']}")
        if prev:
            print(f"  {'':14s}      preview: {prev}")
        e = ex.get(d["type"])
        if e:
            spec = {k: v for k, v in e[1].items() if k not in ("id", "duration", "t0")}
            js = json.dumps(spec, ensure_ascii=False)
            print(f"  {'':14s}      example: {js[:400]}{' ...' if len(js) > 400 else ''}")
    if pb.get("also_available"):
        print(f"\n({pb['also_available']})")
    print("\n## Rules\n")
    for r in pb.get("rules", []):
        print(f"- {r}")
    if pb.get("rules_md"):
        print("\n" + pb["rules_md"])
    return pb


def check():
    dev = engine_devices()
    ok = True
    for tid, t in templates().items():
        bad = [d["type"] for d in t.get("devices", []) if d["type"] not in dev and d["type"] not in ("cutout",)]
        state = "installed" if t["installed"] else f"NOT installed (missing {', '.join(t['missing'])})"
        print(f"template {tid:12s} {state}" + (f"   unknown devices: {bad}" if bad else ""))
        ok &= not bad
    for sid, s in styles().items():
        base = ALIASES.get(s.get("template") or "", s.get("template"))
        good = base in templates() or base in ("almanac_v1",)
        print(f"style    {sid:20s} -> {s.get('template')}" + ("" if good else "   UNKNOWN TEMPLATE"))
        ok &= good
    return ok


def new_template(tid, base):
    T = templates()
    if base not in T:
        raise SystemExit(f"no template {base!r}")
    dst = os.path.join(TPL_DIR, tid)
    if os.path.exists(dst):
        raise SystemExit(f"{dst} already exists")
    shutil.copytree(T[base]["dir"], dst)
    t = _load(os.path.join(dst, "template.json"))
    t.update(id=tid, name=f"{t['name']} (copy)", examples=t.get("examples", []))
    # a new template brings its own look: the base theme copied as a theme_def you can edit freely
    t.setdefault("theme_def", None)
    json.dump(t, open(os.path.join(dst, "template.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    with open(os.path.join(dst, "README.md"), "w", encoding="utf-8") as f:
        f.write(f"""# {tid}

Made from `{base}`. Edit `template.json`:

- `theme`: the engine look it renders with. For a look of its own, set `"theme": "{tid}"` and fill `theme_def`
  with fonts / pal / grounds / map (copy one from docu/engine.js THEMES as a start).
- `scene_files`: your own scene code (e.g. `["scenes_{tid}.js"]` in this folder) - it is loaded automatically.
- `devices`: what this template uses and how often (min_per_10min); the edit audit enforces it.
- `audit`: pacing limits; `rules`: how it is edited; `examples`: finished shot lists to copy the style from.

Then `python docu/registry.py check` and `python docu/registry.py show {tid}`.
""")
    print(f"created {dst}")


def new_style(sid, tid):
    if ALIASES.get(tid, tid) not in templates():
        raise SystemExit(f"no template {tid!r}")
    dst = os.path.join(STY_DIR, sid)
    if os.path.exists(dst):
        raise SystemExit(f"{dst} already exists")
    os.makedirs(dst)
    json.dump(dict(name=sid.replace("-", " ").title(), template=tid,
                   blurb="what this style is for",
                   overrides=dict(grade=None, grain=None, xfade=None, sfx_style=None, pal={}, fonts={}),
                   devices={}, audit={}, rules="rules.md"),
              open(os.path.join(dst, "style.json"), "w", encoding="utf-8"), indent=1)
    open(os.path.join(dst, "rules.md"), "w", encoding="utf-8").write(
        f"# {sid}\n\nHow this style is edited (opening, recurring devices, pacing, what gets stamped). "
        "The agent reads this together with the template's playbook.\n")
    print(f"created {dst} - edit style.json (remove the null overrides you do not need) and rules.md")


def main():
    ap = argparse.ArgumentParser(description="templates and styles of the kit")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list")
    s = sub.add_parser("show"); s.add_argument("name"); s.add_argument("--minutes", type=float, default=15.0)
    sub.add_parser("check")
    n = sub.add_parser("new-template"); n.add_argument("id"); n.add_argument("--from", dest="base", required=True)
    n2 = sub.add_parser("new-style"); n2.add_argument("id"); n2.add_argument("--template", required=True)
    a = ap.parse_args()
    if a.cmd == "list":
        print("TEMPLATES")
        for tid, t in templates().items():
            print(f"  {tid:12s} {t['name']:28s} {'' if t['installed'] else '(not installed: ' + ', '.join(t['missing']) + ')'}")
        print("STYLES")
        for sid, st in styles().items():
            print(f"  {sid:20s} -> {st.get('template')}   {st.get('blurb', '')[:70]}")
    elif a.cmd == "show":
        show(a.name, a.minutes)
    elif a.cmd == "check":
        sys.exit(0 if check() else 1)
    elif a.cmd == "new-template":
        new_template(a.id, a.base)
    elif a.cmd == "new-style":
        new_style(a.id, a.template)


if __name__ == "__main__":
    main()
