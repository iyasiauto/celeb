"""
Asset preparation for the scene renderer.

Every picture a scene uses is prepared once, here, so the browser never runs a
full-frame CSS filter per frame:

    <key>.jpg        the picture, resized (long side <= 2600) and graded
    <key>_blur.jpg   small, heavily blurred and darkened - fill behind contain-fit shots
    <key>_soft.jpg   full size, blurred, dimmed, desaturated - the ground of a depth pop
    <key>_dim.jpg    full size, dimmed, blurred and desaturated - spotlight surround
    <key>_cut.png    the subject cut out (rembg), same size as <key>.jpg

plus the procedural surfaces the paper scenes stand on (tan paper, parchment,
newsprint, a grunge mask for stamps) and a television set with its screen cut out.
"""

import os
import hashlib

import numpy as np
from PIL import Image, ImageFilter, ImageEnhance, ImageOps

MAX_SIDE = 2600
_REMBG = None


def _session():
    global _REMBG
    if _REMBG is None:
        from rembg import new_session
        _REMBG = new_session("isnet-general-use")
    return _REMBG


def grade(im, kind):
    """Named grades applied once at prep time."""
    if kind in (None, "", "none"):
        return im
    if kind == "bw":
        g = ImageOps.grayscale(im)
        g = ImageEnhance.Contrast(g).enhance(1.12)
        return Image.merge("RGB", (g, g, g))
    if kind == "sepia":
        g = ImageEnhance.Contrast(ImageOps.grayscale(im)).enhance(1.08)
        a = np.asarray(g, dtype=np.float32) / 255.0
        rgb = np.stack([a * 1.06 + 0.02, a * 0.96 + 0.01, a * 0.80], -1)
        return Image.fromarray(np.clip(rgb * 255, 0, 255).astype(np.uint8))
    if kind == "xray":
        # radiograph look: inverted luminance, cyan tint, lifted contrast
        g = ImageOps.invert(ImageEnhance.Contrast(ImageOps.grayscale(im)).enhance(1.35))
        a = np.asarray(g, dtype=np.float32) / 255.0
        rgb = np.stack([a * 0.62, a * 0.93, a * 1.0], -1) ** 1.1
        return Image.fromarray(np.clip(rgb * 255, 0, 255).astype(np.uint8))
    if kind == "cool":
        # the forensic grade: cooler, cleaner, a little more contrast
        im = ImageEnhance.Color(im).enhance(0.78)
        im = ImageEnhance.Contrast(im).enhance(1.08)
        a = np.asarray(im, dtype=np.float32) / 255.0
        a = a * np.array([0.96, 1.0, 1.04], np.float32)
        return Image.fromarray(np.clip(a * 255, 0, 255).astype(np.uint8))
    if kind == "warmsepia":
        # the expedition grade: warm, slightly faded, like a print in a field journal
        im = ImageEnhance.Color(im).enhance(0.72)
        a = np.asarray(im, dtype=np.float32) / 255.0
        a = a * np.array([1.06, 1.0, 0.86], np.float32) + np.array([0.02, 0.01, 0.0], np.float32)
        a = 0.06 + 0.9 * a
        return Image.fromarray(np.clip(a * 255, 0, 255).astype(np.uint8))
    if kind == "doc":
        # the documentary grade: slightly muted, warm highlights, cool shadows
        im = ImageEnhance.Color(im).enhance(0.82)
        im = ImageEnhance.Contrast(im).enhance(1.06)
        a = np.asarray(im, dtype=np.float32) / 255.0
        lum = a.mean(-1, keepdims=True)
        warm = np.array([1.03, 1.0, 0.94], dtype=np.float32)
        cool = np.array([0.96, 1.0, 1.04], dtype=np.float32)
        a = a * (lum * warm + (1 - lum) * cool)
        return Image.fromarray(np.clip(a * 255, 0, 255).astype(np.uint8))
    raise ValueError(f"unknown grade {kind!r}")


def _crop(im, box):
    """Crop by fractional box (x0, y0, x1, y1)."""
    if not box:
        return im
    w, h = im.size
    x0, y0, x1, y1 = box
    return im.crop((int(x0 * w), int(y0 * h), int(x1 * w), int(y1 * h)))


def prepare_image(src, out_dir, key, grade_kind="doc", crop=None, cut=False,
                  variants=("blur",), upscale_to=1920):
    """Prepare one picture and the variants a scene asks for. Returns the key."""
    os.makedirs(out_dir, exist_ok=True)
    main = os.path.join(out_dir, key + ".jpg")
    stamp = os.path.join(out_dir, key + ".src")
    sig = f"{src}|{grade_kind}|{crop}|{cut}|{sorted(variants)}|v3"
    if os.path.exists(main) and os.path.exists(stamp) and open(stamp).read() == sig:
        return key

    im = Image.open(src).convert("RGB")
    im = _crop(im, crop)
    w, h = im.size
    k = min(1.0, MAX_SIDE / max(w, h))
    # small sources are upscaled so a cover fit is not soft; Lanczos then a light sharpen
    if max(w, h) * k < upscale_to:
        k = upscale_to / max(w, h)
    if abs(k - 1) > 1e-3:
        im = im.resize((max(1, int(w * k)), max(1, int(h * k))), Image.LANCZOS)
        if k > 1:
            im = im.filter(ImageFilter.UnsharpMask(radius=1.6, percent=60, threshold=2))
    im = grade(im, grade_kind)
    im.save(main, quality=93)

    if "blur" in variants:
        sm = im.copy()
        sm.thumbnail((480, 480))
        sm = sm.filter(ImageFilter.GaussianBlur(14))
        sm = ImageEnhance.Brightness(sm).enhance(0.55)
        sm.save(os.path.join(out_dir, key + "_blur.jpg"), quality=88)
    if "soft" in variants or "dim" in variants or cut:
        sm = im.resize((im.width // 3, im.height // 3), Image.BILINEAR).filter(ImageFilter.GaussianBlur(7))
        sm = sm.resize(im.size, Image.BILINEAR)
        soft = ImageEnhance.Brightness(ImageEnhance.Color(sm).enhance(0.55)).enhance(0.62)
        soft.save(os.path.join(out_dir, key + "_soft.jpg"), quality=90)
        dim = ImageEnhance.Brightness(ImageEnhance.Color(sm).enhance(0.3)).enhance(0.55)
        dim.save(os.path.join(out_dir, key + "_dim.jpg"), quality=90)
    if cut:
        from rembg import remove
        out = remove(im, session=_session(), post_process_mask=True)
        out.save(os.path.join(out_dir, key + "_cut.png"))
        # the depth-pop subject with its keyline and shadow baked in, same frame as the photo
        bake_keyline(out, keyline=max(4, im.width // 480), red=False, pad=0).save(
            os.path.join(out_dir, key + "_cutk.png"))
    open(stamp, "w").write(sig)
    return key


def bake_keyline(im, keyline=6, red=True, pad=60, red_off=(16, 12), shadow=(0, 26, 22, 0.45)):
    """White keyline, offset red stroke and a soft drop shadow, baked into the PNG.

    CSS drop-shadow filters on a moving layer are recomputed every frame; baking them
    here is what keeps collage and depth-pop scenes fast.
    """
    im = im.convert("RGBA")
    if pad:
        big = Image.new("RGBA", (im.width + 2 * pad, im.height + 2 * pad), (0, 0, 0, 0))
        big.paste(im, (pad, pad))
        im = big
    a = im.getchannel("A")
    hard = a.point(lambda v: 255 if v > 110 else 0)
    ring = hard.filter(ImageFilter.MaxFilter(2 * keyline + 1)) if keyline else hard
    layers = Image.new("RGBA", im.size, (0, 0, 0, 0))
    dx, dy, blur, alpha = shadow
    sh = ring.filter(ImageFilter.GaussianBlur(blur)).point(lambda v: int(v * alpha))
    shadow_img = Image.new("RGBA", im.size, (0, 0, 0, 255)); shadow_img.putalpha(sh)
    layers.alpha_composite(shadow_img, (dx, dy))
    if red:
        red_img = Image.new("RGBA", im.size, (214, 46, 31, 255)); red_img.putalpha(ring)
        layers.alpha_composite(red_img, red_off)
    if keyline:
        white = Image.new("RGBA", im.size, (250, 248, 242, 255)); white.putalpha(ring)
        layers.alpha_composite(white)
    layers.alpha_composite(im)
    return layers


def prepare_cutout(src, out_dir, key, halftone=False, height=1100, keyline=6, red=True):
    """A transparent PNG object (kit cutouts, or a rembg cut of a photo)."""
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, key + ".png")
    if os.path.exists(out):
        return key
    im = Image.open(src)
    if im.mode != "RGBA":
        from rembg import remove
        im = remove(im.convert("RGB"), session=_session(), post_process_mask=True)
    bb = im.getbbox()
    if bb:
        im = im.crop(bb)
    k = height / im.height
    if k < 1:
        im = im.resize((int(im.width * k), int(im.height * k)), Image.LANCZOS)
    if halftone:
        im = _halftone(im)
    if keyline or red:
        im = bake_keyline(im, keyline=keyline, red=red)
    im.save(out)
    return key


def _halftone(im, cell=5):
    """Black-and-white halftone look for collage cutouts, alpha preserved."""
    a = im.getchannel("A")
    g = np.asarray(ImageEnhance.Contrast(ImageOps.grayscale(im.convert("RGB"))).enhance(1.25), dtype=np.float32) / 255
    h, w = g.shape
    yy, xx = np.mgrid[0:h, 0:w]
    # rotated dot screen
    u = (xx * 0.7071 + yy * 0.7071) / cell
    v = (-xx * 0.7071 + yy * 0.7071) / cell
    d = np.hypot(u - np.round(u), v - np.round(v)) / 0.7071
    dots = (d > np.sqrt(np.clip(1 - g, 0, 1)) * 0.95).astype(np.float32)
    mix = np.clip(0.55 * g + 0.45 * dots, 0, 1)
    mix = 0.1 + 0.86 * mix
    out = Image.fromarray((mix * 255).astype(np.uint8)).convert("RGB")
    out.putalpha(a)
    return out


# ------------------------------------------------------------------ surfaces

def _noise(h, w, scale, seed):
    rs = np.random.RandomState(seed)
    small = rs.rand(max(2, h // scale), max(2, w // scale)).astype(np.float32)
    return np.asarray(Image.fromarray((small * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC), dtype=np.float32) / 255


def make_surfaces(out_dir, kit_dir):
    os.makedirs(out_dir, exist_ok=True)
    W, H = 1920, 1080

    def paper(name, base, stains, seed, fibers=True):
        p = os.path.join(out_dir, name)
        if os.path.exists(p):
            return
        n = (0.5 * _noise(H, W, 180, seed) + 0.3 * _noise(H, W, 40, seed + 1) + 0.2 * _noise(H, W, 6, seed + 2))
        img = np.ones((H, W, 3), np.float32) * np.array(base, np.float32) / 255
        img *= (0.9 + 0.16 * n)[..., None]
        st = _noise(H, W, 260, seed + 3)
        img *= (1 - stains * np.clip((st - 0.62) * 3, 0, 1))[..., None] * np.array([1, 0.97, 0.9])
        if fibers:
            rs = np.random.RandomState(seed + 4)
            fib = rs.rand(H, W) > 0.9985
            img[fib] *= 0.8
        yy, xx = np.mgrid[0:H, 0:W]
        vig = 1 - 0.28 * (((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
        img *= vig[..., None]
        Image.fromarray(np.clip(img * 255, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.6)).save(p, quality=92)

    paper("paper_tan.jpg", (214, 202, 174), 0.10, 11)
    paper("parchment.jpg", (226, 208, 168), 0.22, 23)
    paper("newsprint.jpg", (236, 229, 211), 0.05, 37, fibers=False)

    lab = os.path.join(out_dir, "paper_lab.jpg")
    if not os.path.exists(lab):
        # engineering graph paper: cool off-white, fine and bold grid, faint fold
        n = 0.6 * _noise(H, W, 120, 51) + 0.4 * _noise(H, W, 8, 52)
        img = np.ones((H, W, 3), np.float32) * np.array([232, 236, 234], np.float32) / 255
        img *= (0.94 + 0.08 * n)[..., None]
        yy, xx = np.mgrid[0:H, 0:W]
        fine = ((xx % 24) == 0) | ((yy % 24) == 0)
        bold = ((xx % 120) == 0) | ((yy % 120) == 0)
        img[fine] *= np.array([0.93, 0.96, 0.98])
        img[bold] *= np.array([0.84, 0.91, 0.95])
        vig = 1 - 0.22 * (((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
        img *= vig[..., None]
        Image.fromarray(np.clip(img * 255, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.4)).save(lab, quality=92)
    jn = os.path.join(out_dir, "paper_journal.jpg")
    if not os.path.exists(jn):
        # an explorer's field journal: warm cream, faint blue rules, a red margin, worn edges
        n = 0.55 * _noise(H, W, 150, 71) + 0.3 * _noise(H, W, 30, 72) + 0.15 * _noise(H, W, 5, 73)
        img = np.ones((H, W, 3), np.float32) * np.array([238, 226, 198], np.float32) / 255
        img *= (0.9 + 0.14 * n)[..., None]
        yy, xx = np.mgrid[0:H, 0:W]
        rules = ((yy - 150) % 54 == 0) & (yy > 120)
        img[rules] = img[rules] * 0.55 + np.array([0.55, 0.66, 0.78]) * 0.45
        margin = (np.abs(xx - 210) <= 1)
        img[margin] = img[margin] * 0.4 + np.array([0.75, 0.3, 0.28]) * 0.6
        st = _noise(H, W, 240, 74)
        img *= (1 - 0.14 * np.clip((st - 0.6) * 3, 0, 1))[..., None] * np.array([1, 0.97, 0.9])
        vig = 1 - 0.34 * (((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2) ** 1.4
        img *= vig[..., None]
        Image.fromarray(np.clip(img * 255, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.5)).save(jn, quality=92)
    lt = os.path.join(out_dir, "leather.jpg")
    if not os.path.exists(lt):
        # a dark leather desk: warm brown grain with a pool of lamplight
        n = 0.45 * _noise(H, W, 3, 81) + 0.35 * _noise(H, W, 14, 82) + 0.2 * _noise(H, W, 90, 83)
        yy, xx = np.mgrid[0:H, 0:W]
        r = np.sqrt(((xx - W * 0.5) / (W * 0.62)) ** 2 + ((yy - H * 0.42) / (H * 0.7)) ** 2)
        lamp = np.clip(1 - r, 0, 1) ** 1.3
        base = np.array([46, 28, 17], np.float32) / 255
        img = base * (0.75 + 0.45 * n)[..., None] + lamp[..., None] * np.array([0.16, 0.10, 0.05], np.float32)
        Image.fromarray(np.clip(img * 255, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.6)).save(lt, quality=92)
    lb = os.path.join(out_dir, "lightbox.jpg")
    if not os.path.exists(lb):
        # a dark lightbox / evidence table: graphite with a cool glow in the middle
        n = 0.7 * _noise(H, W, 160, 61) + 0.3 * _noise(H, W, 5, 62)
        yy, xx = np.mgrid[0:H, 0:W]
        r = np.sqrt(((xx - W / 2) / (W * 0.6)) ** 2 + ((yy - H / 2) / (H * 0.6)) ** 2)
        glow = np.clip(1 - r, 0, 1) ** 1.6
        base = np.array([16, 22, 26], np.float32) / 255
        img = base * (0.85 + 0.25 * n)[..., None] + glow[..., None] * np.array([0.05, 0.11, 0.13], np.float32)
        grid = ((xx % 80) == 0) | ((yy % 80) == 0)
        img[grid] += np.array([0.02, 0.05, 0.06])
        Image.fromarray(np.clip(img * 255, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.5)).save(lb, quality=92)

    pm = os.path.join(out_dir, "paper_map.jpg")
    if not os.path.exists(pm):
        _paper_map(pm, os.path.join(out_dir, "parchment.jpg"), os.path.join(kit_dir, "maps", "geo_lo.json"))

    g = os.path.join(out_dir, "grunge.png")
    if not os.path.exists(g):
        n = 0.6 * _noise(300, 600, 3, 5) + 0.4 * _noise(300, 600, 25, 6)
        a = np.clip((n - 0.12) * 4.0, 0, 1)
        m = Image.fromarray((a * 255).astype(np.uint8))
        rgba = Image.new("RGBA", m.size, (0, 0, 0, 255))
        rgba.putalpha(m)
        rgba.save(g)

    tv = os.path.join(out_dir, "kit_tv_cut.png")
    if not os.path.exists(tv):
        room = Image.open(os.path.join(kit_dir, "cinema", "tv.jpg")).convert("RGBA")
        mask = Image.open(os.path.join(kit_dir, "cinema", "tv_mask.png")).convert("L")
        # white in the mask is the screen: make it transparent
        alpha = ImageOps.invert(mask).filter(ImageFilter.GaussianBlur(1.2))
        room.putalpha(alpha)
        room.save(tv)


def _topo_lines(path):
    """Decode a quantized TopoJSON file into lon/lat polylines (its arcs)."""
    import json
    t = json.load(open(path))
    sx, sy = t["transform"]["scale"]
    tx, ty = t["transform"]["translate"]
    out = []
    for arc in t["arcs"]:
        x = y = 0
        pts = []
        for dx, dy in arc:
            x += dx; y += dy
            pts.append((x * sx + tx, y * sy + ty))
        out.append(pts)
    return out


def _paper_map(out, base_path, topo_path):
    """An old-atlas surface: parchment with faint coastlines, borders and graticule."""
    from PIL import ImageDraw
    base = Image.open(base_path).convert("RGB")
    W, H = base.size
    ink = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(ink)
    # a regional window centred on the Near East, like a page torn from an atlas
    lon0, lat0, k = 38.0, 38.0, 26.0
    proj = lambda lo, la: ((lo - lon0) * k * 0.8 + W / 2, (lat0 - la) * k + H / 2)
    for lo in range(-40, 120, 10):
        d.line([proj(lo, -60), proj(lo, 80)], fill=40, width=1)
    for la in range(-60, 90, 10):
        d.line([proj(-40, la), proj(120, la)], fill=40, width=1)
    for arc in _topo_lines(topo_path):
        pts = [proj(lo, la) for lo, la in arc]
        if len(pts) > 1:
            d.line(pts, fill=150, width=2)
    ink = ink.filter(ImageFilter.GaussianBlur(0.8))
    a = np.asarray(base, np.float32)
    m = np.asarray(ink, np.float32)[..., None] / 255.0
    tint = np.array([92, 70, 44], np.float32)
    a = a * (1 - 0.55 * m) + tint * 0.55 * m
    Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).save(out, quality=92)


def file_key(path, extra=""):
    base = os.path.splitext(os.path.basename(path))[0]
    h = hashlib.md5((path + extra).encode()).hexdigest()[:6]
    safe = "".join(ch if ch.isalnum() else "_" for ch in base)[:40]
    return f"{safe}_{h}"
