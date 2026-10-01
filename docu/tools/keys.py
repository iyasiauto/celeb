"""
keys.py - read API keys by name: environment variable first, then api_keys/keys.env (git-ignored).

    from keys import get
    get("GOFILE_TOKEN")        # -> str or None

    python keys.py             # lists which known keys are set (never prints values)
"""

import os

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
FILE = os.environ.get("API_KEYS_FILE", os.path.join(REPO, "api_keys", "keys.env"))
KNOWN = ["TWOSPEAKER_API_KEY", "GOFILE_TOKEN"]


def _file_values():
    out = {}
    if os.path.exists(FILE):
        for line in open(FILE, encoding="utf-8"):
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                v = v.strip().strip('"').strip("'")
                if v:
                    out[k.strip()] = v
    return out


def get(name, default=None):
    return os.environ.get(name) or _file_values().get(name) or default


if __name__ == "__main__":
    for k in KNOWN:
        src = "environment" if os.environ.get(k) else ("api_keys/keys.env" if _file_values().get(k) else None)
        print(f"{k:22s} {'set (' + src + ')' if src else 'not set'}")
