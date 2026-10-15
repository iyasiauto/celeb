"""
props.py - simple flat "real object" props drawn in code (no stock, no AI), saved as transparent PNGs
into the kit's cutouts/ folder so collage boards can use them like any other cut-out:

    dict(k="cut", img=cutout("prop_envelope.png", red=False), x=960, y=560, h=520, at=0.3)

    python props.py <kit>/cutouts          # writes every prop below

Props: prop_envelope (brown government envelope, window + "OFFICIAL BUSINESS"),
       prop_notice (a folded paper notice with lines of text), prop_receipt (a till receipt), prop_list (a shopping list in Yiddish).
"""

import os
import random
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont, features

FONT_DIRS = ["/usr/share/fonts/truetype/dejavu", "/usr/share/fonts/truetype/liberation"]


def _font(size, bold=True):
    names = ["DejaVuSans-Bold.ttf", "LiberationSans-Bold.ttf"] if bold else ["DejaVuSans.ttf", "LiberationSans-Regular.ttf"]
    for d in FONT_DIRS:
        for n in names:
            p = os.path.join(d, n)
            if os.path.exists(p):
                return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def _paper(w, h, base, speck=0.018, seed=1):
    """flat colour with fine fibres and speckle so it reads as paper, not a vector box"""
    r = random.Random(seed)
    im = Image.new("RGBA", (w, h), base + (255,))
    d = ImageDraw.Draw(im)
    for _ in range(int(w * h * speck / 40)):
        x, y = r.randrange(w), r.randrange(h)
        k = r.randint(-18, 14)
        c = tuple(max(0, min(255, v + k)) for v in base) + (255,)
        if r.random() < 0.7:
            d.point((x, y), fill=c)
        else:
            d.line((x, y, x + r.randint(-9, 9), y + r.randint(-3, 3)), fill=c, width=1)
    return im


def _shadowed(im, blur=18, off=(10, 14), alpha=110):
    w, h = im.size
    pad = blur * 3
    out = Image.new("RGBA", (w + pad * 2, h + pad * 2), (0, 0, 0, 0))
    sh = Image.new("RGBA", out.size, (0, 0, 0, 0))
    mask = im.split()[3].point(lambda a: alpha if a > 0 else 0)
    sh.paste((0, 0, 0, 255), (pad + off[0], pad + off[1]), mask)
    sh = sh.filter(ImageFilter.GaussianBlur(blur))
    out.alpha_composite(sh)
    out.alpha_composite(im, (pad, pad))
    return out


def envelope(w=1500, h=860):
    kraft = (178, 132, 84)
    im = _paper(w, h, kraft, seed=3)
    d = ImageDraw.Draw(im)
    dark = (140, 100, 60, 255)
    # back flap seams (seen through from the front as faint folds)
    d.line((0, 0, w * 0.5, h * 0.52), fill=(160, 117, 72, 255), width=3)
    d.line((w, 0, w * 0.5, h * 0.52), fill=(160, 117, 72, 255), width=3)
    # address window
    wx, wy, ww, wh = int(w * 0.36), int(h * 0.50), int(w * 0.44), int(h * 0.26)
    d.rounded_rectangle((wx, wy, wx + ww, wy + wh), radius=10, fill=(214, 206, 188, 255), outline=dark, width=2)
    f = _font(30, bold=False)
    for i, ln in enumerate(["HOUSEHOLD OF 11", "KIRYAS JOEL NY 10950"]):
        d.text((wx + 30, wy + 34 + i * 48), ln, fill=(70, 62, 52, 255), font=f)
    # sender block and franking
    d.text((60, 56), "DEPARTMENT OF SOCIAL SERVICES", fill=(88, 58, 30, 255), font=_font(32))
    d.text((60, 100), "OFFICIAL BUSINESS", fill=(88, 58, 30, 255), font=_font(26, bold=False))
    d.text((60, 136), "PENALTY FOR PRIVATE USE $300", fill=(88, 58, 30, 255), font=_font(20, bold=False))
    fx, fy = w - 300, 50
    d.rectangle((fx, fy, fx + 230, fy + 150), outline=(88, 58, 30, 255), width=4)
    d.text((fx + 30, fy + 28), "POSTAGE &", fill=(88, 58, 30, 255), font=_font(24))
    d.text((fx + 30, fy + 62), "FEES PAID", fill=(88, 58, 30, 255), font=_font(24))
    d.text((fx + 30, fy + 100), "PERMIT G-10", fill=(88, 58, 30, 255), font=_font(20, bold=False))
    # edge wear
    d.rectangle((0, 0, w - 1, h - 1), outline=dark, width=3)
    return _shadowed(im.rotate(0, expand=True))


def notice(w=900, h=1180):
    im = _paper(w, h, (238, 233, 220), seed=5)
    d = ImageDraw.Draw(im)
    d.text((70, 70), "NOTICE", fill=(40, 40, 40, 255), font=_font(64))
    r = random.Random(9)
    y = 190
    while y < h - 120:
        L = r.randint(int(w * 0.45), int(w * 0.82))
        d.rounded_rectangle((70, y, 70 + L, y + 16), radius=8, fill=(150, 146, 138, 255))
        y += r.choice([42, 42, 42, 80])
    d.line((0, h * 0.34, w, h * 0.34), fill=(214, 208, 194, 255), width=3)     # fold
    d.line((0, h * 0.67, w, h * 0.67), fill=(214, 208, 194, 255), width=3)
    return _shadowed(im)


def receipt(w=560, h=1300):
    im = _paper(w, h, (246, 244, 238), seed=7)
    d = ImageDraw.Draw(im)
    f = _font(30, bold=False)
    rows = ["CHALLAH  x3", "MILK  x6", "EGGS  x4 DZ", "APPLES  5 LB", "RICE  10 LB", "CHICKEN  x3", "DIAPERS  x2",
            "POTATOES  10 LB", "BREAD  x4", "JUICE  x6"]
    d.text((60, 60), "GROCERY", fill=(40, 40, 40, 255), font=_font(44))
    for i, rw in enumerate(rows):
        d.text((60, 160 + i * 80), rw, fill=(60, 60, 60, 255), font=f)
    d.line((60, 160 + len(rows) * 80 + 10, w - 60, 160 + len(rows) * 80 + 10), fill=(90, 90, 90, 255), width=3)
    d.text((60, 190 + len(rows) * 80), "TOTAL", fill=(40, 40, 40, 255), font=_font(40))
    return _shadowed(im)


def shopping_list(w=640, h=900):
    """a lined notepad page with a short list in Yiddish (Hebrew script, drawn right to left)"""
    im = _paper(w, h, (244, 238, 214), seed=11)
    d = ImageDraw.Draw(im)
    for y in range(150, h - 40, 84):
        d.line((30, y, w - 30, y), fill=(170, 190, 210, 255), width=2)
    d.line((w - 90, 0, w - 90, h), fill=(210, 140, 140, 255), width=2)
    items = ["חלה", "מילך", "אייער", "עפל", "ברויט", "קארטאפל", "הינער"]      # challah, milk, eggs, apples, bread, potatoes, chicken
    f = _font(52, bold=False)
    for i, it in enumerate(items):
        t = it if features.check("raqm") else it[::-1]    # without libraqm PIL can't lay out right-to-left
        tw = d.textlength(t, font=f)
        d.text((w - 120 - tw, 150 + i * 84 - 62), t, fill=(40, 50, 110, 255), font=f)
    return _shadowed(im)


PROPS = dict(prop_envelope=envelope, prop_notice=notice, prop_receipt=receipt, prop_list=shopping_list)


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "."
    os.makedirs(out, exist_ok=True)
    for name, fn in PROPS.items():
        p = os.path.join(out, name + ".png")
        fn().save(p)
        print(p)
