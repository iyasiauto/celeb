"""
template_catalog.py - one page to choose a template from: every template's preview picture and sample video side by side.

    python docu/tools/template_catalog.py          writes TEMPLATES_GALLERY.html (kit root, open it in a browser)
                                                   and kit_docs/TEMPLATE_CATALOG.md (the same as a table)

Run it again after adding a template or a style folder (the page links the files where they are, nothing is copied).
"""

import html
import json
import os
import sys

DOCU = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(DOCU)
sys.path.insert(0, DOCU)

import registry   # noqa: E402

GROUPS = [
    ("Docu templates (made for this channel)", ["documentary", "almanac", "paper", "forensic", "expedition", "broadcast",
                                                "datadoc", "finalreel", "record"]),
    ("Frontier's channel looks (imported)", ["dossier", "kinetic", "atlas", "deep", "news-frontline", "legend", "hustle",
                                             "frontier-documentary", "courtside", "ai-presenter", "hasidic-frontier",
                                             "modern-homes", "dark-psychology", "stories-2d"]),
    ("New Style 3", ["emerge-documentary"]),
]


def cards():
    T, S = registry.templates(), registry.styles()
    by_t = {}
    for sid, s in S.items():
        by_t.setdefault(s.get("template") or s.get("theme"), []).append(s)
    out = []
    seen = set()
    order = [t for _, ts in GROUPS for t in ts] + sorted(t for t in T if t not in {x for _, ts in GROUPS for x in ts})
    for tid in order:
        t = T.get(tid)
        if not t or tid in seen:
            continue
        seen.add(tid)
        sts = by_t.get(tid, [])
        main = next((s for s in sts if s["id"] == tid), sts[0] if sts else None)

        def f(k, base):
            if main and main.get(k) and os.path.exists(os.path.join(main["dir"], main[k])):
                return os.path.relpath(os.path.join(main["dir"], main[k]), ROOT)
            return base
        prev = f("preview", t.get("preview_sheet") if t.get("preview_sheet") and os.path.exists(os.path.join(ROOT, t["preview_sheet"])) else None)
        smp = f("sample", None)
        ref = f("reference", None)
        out.append(dict(id=tid, name=(main or {}).get("name") or t.get("name", tid), letter=(main or {}).get("letter", ""),
                        best=t.get("best_for", ""), tag=(main or {}).get("tagline") or t.get("tagline", ""),
                        points=(main or {}).get("points") or [], preview=prev, sample=smp, reference=ref,
                        style=(main or {}).get("id"), variants=[s["id"] for s in sts if s is not main],
                        source=t.get("source", "Docu"), devices=len(t.get("devices", [])),
                        group=next((g for g, ts in GROUPS if tid in ts), "Other")))
    return out


def page(cs):
    def card(c):
        media = (f'<video controls preload="none" poster="{html.escape(c["preview"] or "")}" src="{html.escape(c["sample"])}"></video>'
                 if c["sample"] else (f'<img src="{html.escape(c["preview"])}" alt="">' if c["preview"] else '<div class="none">no preview yet</div>'))
        pts = "".join(f"<li>{html.escape(p)}</li>" for p in c["points"][:5])
        var = (f'<p class="var">Variations: {", ".join(html.escape(v) for v in c["variants"])}</p>' if c["variants"] else "")
        ref = f' · <a href="{html.escape(c["reference"])}">reference video</a>' if c["reference"] else ""
        prev = f'<a href="{html.escape(c["preview"])}">preview sheet</a>' if c["preview"] else ""
        return f"""<article>
  {media}
  <div class="body">
    <h3>{html.escape(c['name'])} <code>{html.escape(c['id'])}</code></h3>
    <p class="tag">{html.escape(c['tag'])}</p>
    <p class="best"><b>Best for:</b> {html.escape(c['best'])}</p>
    <ul>{pts}</ul>
    {var}
    <p class="use">Use it: Docu Studio card <b>{html.escape(c['name'])}</b> · <code>python niche.py new &lt;niche&gt; --style {html.escape(c['style'] or c['id'])}</code> ·
    <code>python docu/registry.py show {html.escape(c['id'])}</code></p>
    <p class="links">{prev}{ref} · {c['devices']} devices</p>
  </div>
</article>"""
    body = []
    for g, _ in GROUPS + [("Other", [])]:
        sel = [c for c in cs if c["group"] == g]
        if sel:
            body.append(f"<h2>{html.escape(g)}</h2><div class='grid'>" + "".join(card(c) for c in sel) + "</div>")
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Template Gallery</title><style>
:root{{--bg:#111214;--card:#1B1D21;--ink:#ECE8E1;--soft:#A7A39B;--acc:#E3B25B}}
body{{margin:0;background:var(--bg);color:var(--ink);font:15px/1.5 system-ui,Segoe UI,Arial,sans-serif}}
header{{padding:28px 32px 8px}} h1{{margin:0 0 4px;font-size:28px}} header p{{color:var(--soft);margin:0}}
h2{{margin:28px 32px 12px;font-size:19px;color:var(--acc)}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(420px,1fr));gap:18px;padding:0 32px}}
article{{background:var(--card);border-radius:10px;overflow:hidden;display:flex;flex-direction:column}}
article video,article img{{width:100%;aspect-ratio:16/9;object-fit:cover;background:#000;display:block}}
.none{{aspect-ratio:16/9;display:grid;place-items:center;color:var(--soft);background:#000}}
.body{{padding:14px 16px 16px}} h3{{margin:0 0 4px;font-size:18px}} code{{font-size:12px;color:var(--acc);background:#0004;padding:1px 5px;border-radius:4px}}
.tag{{margin:0 0 6px;color:var(--ink)}} .best,.use,.links,.var{{margin:6px 0;color:var(--soft);font-size:13.5px}}
ul{{margin:6px 0 6px 18px;padding:0;color:var(--soft);font-size:13.5px}} a{{color:var(--acc)}}
@media (max-width:520px){{.grid{{grid-template-columns:1fr;padding:0 16px}} h2{{margin:24px 16px 10px}} header{{padding:20px 16px 4px}}}}
</style></head><body><header><h1>Template Gallery</h1>
<p>{len(cs)} templates. Play a sample, open the preview sheet, then pick the card in Docu Studio (or the style id on the command line).</p></header>
{''.join(body)}<p style="height:40px"></p></body></html>"""


def table(cs):
    rows = ["| # | Template (`id`) | Kahan se | Best for | Preview | Sample |", "|---|---|---|---|---|---|"]
    for i, c in enumerate(cs, 1):
        rows.append(f"| {i} | **{c['name']}** (`{c['id']}`) | {c['group'].split(' (')[0]} | {c['best']} | "
                    f"{('`' + c['preview'] + '`') if c['preview'] else '-'} | {('`' + c['sample'] + '`') if c['sample'] else '-'} |")
    return ("# Template catalog\n\nHar template ka apna folder hai: `templates/<id>/` (engine ka hissa: template.json, scenes, previews) aur "
            "`styles/<id>/` (chunne ka card: style.json, rules.md, **preview.jpg**, **sample.mp4**). Sab ek page par dekhne ke liye "
            "kit root mein **TEMPLATES_GALLERY.html** browser mein kholein.\n\n" + "\n".join(rows) + "\n")


def main():
    cs = cards()
    open(os.path.join(ROOT, "TEMPLATES_GALLERY.html"), "w", encoding="utf-8").write(page(cs))
    os.makedirs(os.path.join(ROOT, "kit_docs"), exist_ok=True)
    open(os.path.join(ROOT, "kit_docs", "TEMPLATE_CATALOG.md"), "w", encoding="utf-8").write(table(cs))
    print(f"{len(cs)} templates -> TEMPLATES_GALLERY.html, kit_docs/TEMPLATE_CATALOG.md")
    for c in cs:
        print(f"  {c['id']:22s} preview={'Y' if c['preview'] else '-'} sample={'Y' if c['sample'] else '-'}")


if __name__ == "__main__":
    main()
