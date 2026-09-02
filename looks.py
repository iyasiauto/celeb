"""
Named visual looks.

A documentary's grade should not be welded into the renderer: archival biography
wants grain and a vignette, a cooking or nature film wants neither. Each look is
a small bundle of FFmpeg filter fragments that the render engine splices in.

Pick one by name (`"look": "clean"` in a topic config, or --look clean), or
override individual fields alongside it.
"""

LOOKS = {
    # Grainy, vignetted, desaturated - archival biography and true crime.
    "vintage": {
        "grade": ("noise=alls=20:allf=t+u,vignette=PI/4,"
                  "eq=gamma=0.96:gamma_r=1.08:gamma_b=0.92:"
                  "saturation=0.88:contrast=1.08"),
        "postcard_eq": ("eq=gamma_r=1.12:gamma_b=0.88:"
                        "saturation=0.82:contrast=1.10"),
        "graphic_grade": "noise=alls=10:allf=t+u",
        "border_color": "0xdc2626",
        "fill_mode": "blur",
    },
    # No grain, no vignette, faithful colour - nature, travel, food, science.
    "clean": {
        "grade": "eq=saturation=1.04:contrast=1.02",
        "postcard_eq": "",
        "graphic_grade": "",
        "border_color": "0x1d4ed8",
        "fill_mode": "blur",
    },
    # Gentle warmth and lift, no texture - lifestyle and profile pieces.
    "warm": {
        "grade": ("eq=gamma=1.02:gamma_r=1.06:gamma_b=0.96:"
                  "saturation=1.06:contrast=1.03"),
        "postcard_eq": "",
        "graphic_grade": "",
        "border_color": "0xd97706",
        "fill_mode": "blur",
    },
    # High contrast monochrome - investigative and historical.
    "noir": {
        "grade": ("hue=s=0,noise=alls=14:allf=t+u,vignette=PI/3.5,"
                  "eq=gamma=0.94:contrast=1.22"),
        "postcard_eq": "eq=contrast=1.15",
        "graphic_grade": "hue=s=0",
        "border_color": "0xe5e5e5",
        "fill_mode": "blur",
    },
    # Nothing at all - deliver the source exactly as shot.
    "none": {
        "grade": "",
        "postcard_eq": "",
        "graphic_grade": "",
        "border_color": "0xdc2626",
        "fill_mode": "blur",
    },
}

DEFAULT_LOOK = "vintage"

# Every field a look may define, with the value used when it is absent.
FIELDS = {
    "grade": "",
    "postcard_eq": "",
    "graphic_grade": "",
    "border_color": "0xdc2626",
    "fill_mode": "blur",      # blur | black | crop
    "fill_blur": 22,          # gaussian sigma for the blurred backdrop
    "fill_dim": 0.12,         # how far the backdrop is darkened, 0-1
    "fill_downscale": 6,      # blur a 1/N thumbnail instead of the full frame
    "fade_s": 0.25,
    "zoom_per_sec": 0.015,
}


def resolve(look=None, overrides=None):
    """Merge a named look with any explicit overrides into a full spec."""
    spec = dict(FIELDS)

    if isinstance(look, dict):
        spec.update({k: v for k, v in look.items() if k in FIELDS})
    elif look:
        name = str(look).lower()
        if name not in LOOKS:
            raise ValueError(
                f"Unknown look {look!r}. Available: {', '.join(sorted(LOOKS))}")
        spec.update(LOOKS[name])
    else:
        spec.update(LOOKS[DEFAULT_LOOK])

    for k, v in (overrides or {}).items():
        if k in FIELDS and v is not None:
            spec[k] = v
    return spec


def names():
    return sorted(LOOKS)
