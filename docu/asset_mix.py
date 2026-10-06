"""Template-aware asset mixing for the DocuTemplates_Kit.

Documentary editing stays simple on purpose. Not every video uses every asset — we rotate
through what makes sense for the template and the chapter, and we keep the per-video choice
deterministic (same slug + same template + same assets folder = same mix).

Expose:
    mix_for(slug, theme, assets_dir) -> dict:
        {
          "texture_png":  path or None,        # subtle paper/VHS layer applied under clips
          "texture_opacity": float,
          "chapter_dust": path or None,        # dust/lightleak overlay used sparingly on chapter heads
          "card_bg": path or None,             # paper texture behind title/stat cards
          "cutouts_dir": path or None,         # stickers available for photo/doc scenes
          "photofx": bool,                     # apply photofx grade to photo scenes
          "cinema_frame": path or None,        # tv.jpg + box.json for archive wraps
          "music_beds_dir": path or None,      # longer music beds to pick from
          "map_lib": path or None,             # assets/maps/map.js replacement
        }
The caller then decides WHERE to use each feature; this module only decides WHETHER.
"""
import json
import os
import random
import re

# --- what each template is allowed to opt into (never forced). None = never for this template.
#
#   textures         NEUTRAL overlay textures (assets/textures/grain_*.png, scanlines.png), blended soft-light over
#                    footage and photographs - grain and paper fibre, never a picture
#   chapter_overlays moving overlays on black at the assets root (dust, light leak, VHS), screened over the chapter
#                    headings and the opening
#   grounds          what paper / collage / card scenes stand on (cork board, dark) - never over footage
#   props            pictures used as cut-out props in collages (the newspaper globe)
#   tv_gate          the vintage TV / film-gate frame (green screen keyed out) over archive shots
TEMPLATE_PALETTE = {
    "datadoc": dict(
        textures=["grain_film.png"], texture_opacity=(0.45, 0.6),
        chapter_overlays=["overlay_dust.mp4", "lightleak.mp4", "overlay_vhs.mp4"],
        card_bgs=["background dark.png"], props=["paper earth.jpg"],
        cutouts=True, photofx=True, cinema_frame=True, tv_gate=True, music_beds=True, map_lib=True,
    ),
    "documentary": dict(
        textures=["grain_film.png", "grain_paper.png"], texture_opacity=(0.45, 0.65),
        chapter_overlays=["overlay_dust.mp4", "lightleak.mp4"],
        card_bgs=["background dark.png"], props=["paper earth.jpg"],
        cutouts=True, photofx=True, cinema_frame=True, tv_gate=True, music_beds=True, map_lib=True,
    ),
    "finalreel": dict(
        textures=["grain_film.png"], texture_opacity=(0.4, 0.55),
        chapter_overlays=["lightleak.mp4", "overlay_dust.mp4"], chapter_opacity=0.35,
        card_bgs=None, props=None,
        cutouts=False, photofx=True, cinema_frame=False, tv_gate=True, music_beds=True, map_lib=True,
    ),
    "almanac": dict(
        textures=["grain_paper.png"], texture_opacity=(0.55, 0.75),
        chapter_overlays=["lightleak.mp4", "overlay_dust.mp4"],
        card_bgs=None, props=["paper earth.jpg"],
        cutouts=True, photofx=True, cinema_frame=False, tv_gate=False, music_beds=True, map_lib=True,
    ),
    "paper": dict(
        textures=["grain_paper.png"], texture_opacity=(0.6, 0.8),
        chapter_overlays=["overlay_dust.mp4", "overlay_vhs.mp4"],
        card_bgs=["background 2.jpg"], props=["paper earth.jpg"],
        cutouts=True, photofx=True, cinema_frame=True, tv_gate=True, music_beds=True, map_lib=True,
    ),
    "forensic": dict(
        textures=["scanlines.png", "grain_film.png"], texture_opacity=(0.45, 0.6),
        chapter_overlays=["overlay_vhs.mp4"],
        card_bgs=["background dark.png"], props=None,
        cutouts=False, photofx=True, cinema_frame=True, tv_gate=True, music_beds=True, map_lib=True,
    ),
    "broadcast": dict(
        textures=["scanlines.png"], texture_opacity=(0.35, 0.5),
        chapter_overlays=["overlay_vhs.mp4"],
        card_bgs=None, props=None,
        cutouts=False, photofx=False, cinema_frame=True, tv_gate=True, music_beds=True, map_lib=True,
    ),
    "expedition": dict(
        textures=["grain_paper.png"], texture_opacity=(0.55, 0.75),
        chapter_overlays=["lightleak.mp4", "overlay_dust.mp4"],
        card_bgs=["background 2.jpg"], props=["paper earth.jpg"],
        cutouts=True, photofx=True, cinema_frame=False, tv_gate=True, music_beds=True, map_lib=True,
    ),
}
TEMPLATE_PALETTE["almanac2"] = TEMPLATE_PALETTE["almanac"]
TEMPLATE_PALETTE["almanac_v1"] = TEMPLATE_PALETTE["almanac"]

# per-feature probability. The user asked for the template's finishing layers on EVERY video, so the ones a
# template allows are on; what varies from video to video is WHICH texture / overlay is picked.
PROB = dict(
    texture=1.0,
    chapter_overlay=1.0,
    card_bg=1.0,
    cutouts=1.0,
    photofx=1.0,
    cinema_frame=1.0,
    tv_gate=1.0,
    music_beds=1.0,
    map_lib=0.0,      # the engine draws its own maps
)


def _seed(slug, theme):
    s = re.sub(r"[^a-z0-9]", "", (slug + "/" + theme).lower())
    return int.from_bytes(s[:16].encode(), "big") or 1


def _pick(options, rng):
    if not options:
        return None
    return options[rng.randrange(len(options))]


def mix_for(slug, theme, assets_dir, overrides=None):
    """Return a per-video feature mix.
    - slug: project slug (same slug + theme + assets => same mix)
    - theme: template name (datadoc / documentary / almanac / paper / forensic / broadcast / expedition)
    - assets_dir: absolute path to DocuTemplates_Kit/assets/
    - overrides: dict to force specific features on/off, e.g. {"texture": False}
    """
    pal = TEMPLATE_PALETTE.get(theme, TEMPLATE_PALETTE.get("documentary"))
    overrides = overrides or {}
    rng = random.Random(_seed(slug, theme))

    def abs_(sub, name):
        return os.path.join(assets_dir, sub, name) if name else None

    def abs_root(name):
        return os.path.join(assets_dir, name) if name else None

    def active(key):
        if key in overrides:
            return bool(overrides[key])
        return rng.random() < PROB.get(key, 0.5)

    out = dict(texture_png=None, texture_opacity=0.0, chapter_dust=None, card_bg=None,
               cutouts_dir=None, photofx=False, cinema_frame=None, music_beds_dir=None, map_lib=None,
               tv_gate=None, props=[])

    if pal.get("textures") and active("texture"):
        pick = _pick(pal["textures"], rng)
        out["texture_png"] = abs_("textures", pick)
        # neutral textures are blended soft-light (render.apply_fx), so this is the grain's strength, not a wash
        lo, hi = pal.get("texture_opacity", (0.45, 0.65))
        out["texture_opacity"] = round(lo + rng.random() * (hi - lo), 2)

    if pal.get("chapter_overlays") and active("chapter_overlay"):
        pick = _pick(pal["chapter_overlays"], rng)
        # these live at assets/ root, not under a subfolder
        out["chapter_dust"] = abs_root(pick)
        out["chapter_opacity"] = float(pal.get("chapter_opacity", 0.7))

    if pal.get("card_bgs") and active("card_bg"):
        pick = _pick(pal["card_bgs"], rng)
        out["card_bg"] = abs_("textures", pick)

    if pal.get("cutouts") and active("cutouts"):
        d = os.path.join(assets_dir, "cutouts")
        if os.path.isdir(d):
            out["cutouts_dir"] = d

    if pal.get("photofx") and active("photofx"):
        if os.path.exists(os.path.join(assets_dir, "photofx", "page.js")):
            out["photofx"] = True

    if pal.get("cinema_frame") and active("cinema_frame"):
        tv = os.path.join(assets_dir, "cinema", "tv.jpg")
        if os.path.exists(tv):
            out["cinema_frame"] = tv

    g = os.path.join(assets_dir, "VINTAGE OVERLAY green screen.mp4")
    if os.path.exists(g):
        out["tv_gate_file"] = g              # an editor's explicit archive=True always gets the gate
        if pal.get("tv_gate") and active("tv_gate"):
            out["tv_gate"] = g

    if pal.get("props"):
        out["props"] = [p for p in (abs_("textures", x) for x in pal["props"]) if p and os.path.exists(p)]

    if pal.get("music_beds") and active("music_beds"):
        d = os.path.join(assets_dir, "music")
        if os.path.isdir(d):
            out["music_beds_dir"] = d

    if pal.get("map_lib") and active("map_lib"):
        ml = os.path.join(assets_dir, "maps", "map.js")
        if os.path.exists(ml):
            out["map_lib"] = ml

    return out


def summary(mix):
    bits = []
    if mix.get("texture_png"):
        bits.append(f"texture={os.path.basename(mix['texture_png'])}@{mix['texture_opacity']}")
    if mix.get("chapter_dust"):
        bits.append(f"chapter={os.path.basename(mix['chapter_dust'])}")
    if mix.get("card_bg"):
        bits.append(f"card_bg={os.path.basename(mix['card_bg'])}")
    if mix.get("cutouts_dir"):
        bits.append("cutouts")
    if mix.get("photofx"):
        bits.append("photofx")
    if mix.get("cinema_frame"):
        bits.append("tv-frame")
    if mix.get("music_beds_dir"):
        bits.append("beds")
    if mix.get("map_lib"):
        bits.append("map.js")
    if mix.get("tv_gate"):
        bits.append("tv-gate")
    return "assets: " + (", ".join(bits) if bits else "(none picked for this video)")


if __name__ == "__main__":
    import sys
    slug = sys.argv[1] if len(sys.argv) > 1 else "demo"
    theme = sys.argv[2] if len(sys.argv) > 2 else "documentary"
    assets_dir = sys.argv[3] if len(sys.argv) > 3 else os.path.join(os.path.dirname(__file__), "..", "assets")
    m = mix_for(slug, theme, os.path.abspath(assets_dir))
    print(json.dumps(m, indent=1, default=str))
    print(summary(m))
