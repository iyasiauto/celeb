"""
keys.py - read API keys and provider settings by name, from (first match wins):

    1. the environment (the desktop app passes its encrypted keys this way)
    2. api_keys/keys.env in this repo (git-ignored)
    3. your Frontier folder's .env ($FRONTIER_DIR/.env) - so a key Frontier already uses on this PC
       (FameSpeak, OpenRouter, OpenLux, Pexels ...) works here too without being entered twice

Values are only read on this computer; nothing here copies them anywhere.

    from keys import get, source
    get("OPENLUX_API_KEY")        # -> str or None
    source("OPENLUX_API_KEY")     # -> "environment" | "api_keys/keys.env" | "Frontier .env" | None

    python keys.py                # which known keys are set and where from (never prints values)
"""

import os

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
FILE = os.environ.get("API_KEYS_FILE", os.path.join(REPO, "api_keys", "keys.env"))
KNOWN = ["FAMESPEAK_API_KEY", "FAMESPEAK_VOICE_ID", "OPENROUTER_API_KEY", "OPENLUX_API_KEY", "ANTIGRAVITY_API_KEY",
         "CUSTOM_AI_API_KEY", "ANTHROPIC_API_KEY", "GOFILE_TOKEN", "TWOSPEAKER_API_KEY"]
ALIASES = {"OPENROUTER_API_KEY": ["OPENROUTER_KEY"]}


def _parse(path):
    out = {}
    try:
        with open(path, encoding="utf-8-sig") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    v = v.split(" #")[0].strip().strip('"').strip("'")
                    if v:
                        out[k.strip()] = v
    except OSError:
        pass
    return out


def _frontier_env():
    d = os.environ.get("FRONTIER_DIR")
    return _parse(os.path.join(d, ".env")) if d else {}


def _lookup(name):
    for n in [name] + ALIASES.get(name, []):
        if os.environ.get(n):
            return os.environ[n], "environment"
        v = _parse(FILE).get(n)
        if v:
            return v, "api_keys/keys.env"
        v = _frontier_env().get(n)
        if v:
            return v, "Frontier .env"
    return None, None


def get(name, default=None):
    return _lookup(name)[0] or default


def source(name):
    return _lookup(name)[1]


if __name__ == "__main__":
    for k in KNOWN:
        src = source(k)
        print(f"{k:22s} {'set (' + src + ')' if src else 'not set'}")
