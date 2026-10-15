"""
famespeak.py - voice-overs from FameSpeak (ElevenLabs library voices) with SRT subtitles.

API (https://famespeak.online/api/openapi.json), Bearer auth with a FameSpeak API key:
    GET  /api/v1/eleven-labs/voices?voiceId=...|search=...     look up / browse ElevenLabs voices
    POST /api/v1/eleven-labs/generations {voiceId, text, language?}  -> 202 {id, statusUrl}
    GET  <statusUrl>  (/api/v1/voice-clone/generations/{id})   poll until the run completes
    GET  /api/v1/voice-clone/generations/{id}/audio             the MP3
    GET  /api/v1/voice-clone/generations/{id}/subtitles         the SRT
    GET  /api/v1/account/usage                                  credits

Long scripts are sent in parts cut at paragraph / sentence ends (max_chars each). The parts' MP3s
are joined with FFmpeg and their SRTs merged with the right time offsets, so the result is one
voiceover.mp3 + one voiceover.srt, exactly like a single generation.

    python famespeak.py voice <voiceId>
    python famespeak.py make script.txt <voiceId> out_dir [--max-chars 4500] [--language en]
"""

import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

BASE = os.environ.get("FAMESPEAK_BASE", "https://famespeak.online")
DONE = {"completed", "complete", "succeeded", "success", "done", "ready", "finished"}
FAILED = {"failed", "error", "errored", "cancelled", "canceled", "expired"}


class FameSpeakError(RuntimeError):
    pass


class Client:
    def __init__(self, key, base=BASE, log=print):
        if not key:
            raise FameSpeakError("No FameSpeak API key: add it in Settings (or FAMESPEAK_API_KEY).")
        self.key, self.base, self.log = key, base.rstrip("/"), log

    # ------------------------------------------------------------------ http
    def _req(self, method, path, body=None, raw=False, ok=(200, 201, 202)):
        url = path if path.startswith("http") else self.base + (path if path.startswith("/api/") else "/api/v1" + path)
        data = json.dumps(body).encode() if body is not None else None
        req = urllib.request.Request(url, data=data, method=method, headers={
            "Authorization": f"Bearer {self.key}", "Accept": "*/*",
            **({"Content-Type": "application/json"} if data else {})})
        for attempt in range(4):
            try:
                with urllib.request.urlopen(req, timeout=120) as r:
                    payload = r.read()
                    if raw:
                        return r.status, payload, r.headers
                    return r.status, (json.loads(payload) if payload else {})
            except urllib.error.HTTPError as e:
                text = e.read().decode("utf-8", "ignore")
                if e.code in (409,) and raw:
                    return e.code, b"", e.headers            # not ready yet
                if e.code in (429, 500, 502, 503, 504) and attempt < 3:
                    time.sleep(3 * (attempt + 1))
                    continue
                msg = {401: "the API key is missing or invalid", 402: "not enough credits",
                       403: "this key/account has no ElevenLabs access", 404: "not found",
                       410: "the file has expired"}.get(e.code, "")
                raise FameSpeakError(f"FameSpeak {method} {path}: HTTP {e.code} {msg} {text[:300]}".strip())
            except urllib.error.URLError as e:
                if attempt < 3:
                    time.sleep(3 * (attempt + 1))
                    continue
                raise FameSpeakError(f"FameSpeak unreachable: {e}")

    # ------------------------------------------------------------------ calls
    def usage(self):
        return self._req("GET", "/account/usage")[1]

    def voice(self, voice_id):
        """The voice with this exact ElevenLabs ID, or None."""
        _, d = self._req("GET", "/eleven-labs/voices?" + urllib.parse.urlencode({"voiceId": voice_id}))
        voices = d.get("voices") if isinstance(d, dict) else d
        return (voices or [None])[0]

    def search(self, query="", page=1, language=None):
        q = {"search": query, "page": page}
        if language:
            q["language"] = language
        return self._req("GET", "/eleven-labs/voices?" + urllib.parse.urlencode(q))[1]

    def start(self, voice_id, text, language=None):
        body = {"voiceId": voice_id, "text": text}
        if language:
            body["language"] = language
        _, d = self._req("POST", "/eleven-labs/generations", body)
        d = d.get("generation", d) if isinstance(d, dict) else {}
        gid = d.get("id") or d.get("generationId")
        if not gid:
            raise FameSpeakError(f"FameSpeak did not return a generation id: {str(d)[:300]}")
        return gid, d.get("statusUrl") or f"/voice-clone/generations/{gid}"

    def wait(self, gid, status_url, on_tick=None, timeout=3600):
        t0 = time.time()
        while time.time() - t0 < timeout:
            _, d = self._req("GET", status_url)
            g = d.get("generation", d) if isinstance(d, dict) else {}
            st = str(g.get("status") or g.get("state") or "").lower()
            if on_tick:
                on_tick(st, g)
            if st in DONE or g.get("audioUrl") or g.get("completedAt"):
                return g
            if st in FAILED:
                raise FameSpeakError(f"FameSpeak generation {gid} {st}: {g.get('error') or g.get('message') or ''}")
            time.sleep(4)
        raise FameSpeakError(f"FameSpeak generation {gid} timed out")

    def download_audio(self, gid, path):
        for _ in range(30):
            code, data, _ = self._req("GET", f"/voice-clone/generations/{gid}/audio", raw=True)
            if code == 200 and data:
                open(path, "wb").write(data)
                return path
            time.sleep(4)
        raise FameSpeakError("audio not ready")

    def download_srt(self, gid, path):
        for _ in range(15):
            try:
                code, data, _ = self._req("GET", f"/voice-clone/generations/{gid}/subtitles?format=srt", raw=True)
            except FameSpeakError as e:
                if "404" in str(e):
                    return None                   # this generation has no subtitles
                raise
            if code == 200 and data:
                text = data.decode("utf-8-sig", "ignore")
                if text.lstrip().startswith('"'):    # a JSON string, just in case
                    text = json.loads(text)
                open(path, "w", encoding="utf-8").write(text)
                return path
            time.sleep(4)
        return None


# ---------------------------------------------------------------------- script parts
def split_script(text, max_chars=4500):
    """Parts of at most max_chars, cut at paragraph ends, else at sentence ends."""
    paras = [p.strip() for p in re.split(r"\n+", text) if p.strip()]
    parts, cur = [], ""
    for p in paras:
        units = [p] if len(p) <= max_chars else re.split(r"(?<=[.!?])\s+", p)
        for j, u in enumerate(units):
            sep = "\n\n" if j == 0 else " "
            if cur and len(cur) + len(sep) + len(u) > max_chars:
                parts.append(cur)
                cur = u
            else:
                cur = cur + sep + u if cur else u
    if cur:
        parts.append(cur)
    return parts


def _dur(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                       capture_output=True, text=True)
    return float(r.stdout.strip() or 0)


def _srt_shift(srt_text, offset, start_index):
    def ts(s):
        h, m, rest = s.replace(",", ".").split(":")
        return int(h) * 3600 + int(m) * 60 + float(rest)

    def fmt(t):
        ms = int(round(t * 1000))
        return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"
    out, n = [], start_index
    for block in re.split(r"\n\s*\n", srt_text.strip().replace("\r", "")):
        lines = [l for l in block.split("\n") if l.strip()]
        k = next((i for i, l in enumerate(lines) if "-->" in l), None)
        if k is None:
            continue
        a, b = [x.strip().split()[0] for x in lines[k].split("-->")]
        out.append(f"{n}\n{fmt(ts(a) + offset)} --> {fmt(ts(b) + offset)}\n" + "\n".join(lines[k + 1:]))
        n += 1
    return "\n\n".join(out), n


def make_voiceover(key, script_text, voice_id, out_dir, max_chars=4500, language=None, log=print, progress=None):
    """-> (mp3 path, srt path or None). Writes out_dir/voiceover.mp3 and out_dir/voiceover.srt."""
    os.makedirs(out_dir, exist_ok=True)
    c = Client(key, log=log)
    v = c.voice(voice_id)
    if v is None:
        raise FameSpeakError(f"No ElevenLabs voice with ID {voice_id} on FameSpeak")
    log(f"voice: {v.get('name') or v.get('voice_name') or voice_id}")
    parts = split_script(script_text, max_chars)
    log(f"{len(script_text)} characters in {len(parts)} part(s)")
    mp3s, srts = [], []
    for i, part in enumerate(parts):
        gid, status_url = c.start(voice_id, part, language)
        log(f"part {i + 1}/{len(parts)}: generation {gid}")
        c.wait(gid, status_url, on_tick=lambda st, g: progress and progress((i + 0.5) / len(parts), f"part {i + 1}: {st}"))
        mp3s.append(c.download_audio(gid, os.path.join(out_dir, f"_part{i:02d}.mp3")))
        srts.append(c.download_srt(gid, os.path.join(out_dir, f"_part{i:02d}.srt")))
        if progress:
            progress((i + 1) / len(parts), f"part {i + 1}/{len(parts)} done")
    mp3 = os.path.join(out_dir, "voiceover.mp3")
    if len(mp3s) == 1:
        os.replace(mp3s[0], mp3)
    else:
        lst = os.path.join(out_dir, "_parts.txt")
        open(lst, "w").write("".join(f"file '{os.path.abspath(p).replace(os.sep, '/')}'\n" for p in mp3s))
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c:a", "libmp3lame",
                        "-b:a", "192k", mp3], check=True)
    srt = None
    if all(srts):
        srt = os.path.join(out_dir, "voiceover.srt")
        if len(srts) == 1:
            os.replace(srts[0], srt)
        else:
            chunks, offset, n = [], 0.0, 1
            for p_mp3, p_srt in zip(mp3s, srts):
                txt, n = _srt_shift(open(p_srt, encoding="utf-8").read(), offset, n)
                chunks.append(txt)
                offset += _dur(p_mp3)
            open(srt, "w", encoding="utf-8").write("\n\n".join(chunks) + "\n")
    for f in os.listdir(out_dir):
        if f.startswith("_part"):
            os.remove(os.path.join(out_dir, f))
    return mp3, srt


if __name__ == "__main__":
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
    from keys import get
    k = get("FAMESPEAK_API_KEY")
    if sys.argv[1] == "voice":
        print(json.dumps(Client(k).voice(sys.argv[2]), indent=1))
    elif sys.argv[1] == "make":
        import argparse
        ap = argparse.ArgumentParser()
        ap.add_argument("cmd"); ap.add_argument("script"); ap.add_argument("voice"); ap.add_argument("out")
        ap.add_argument("--max-chars", type=int, default=4500); ap.add_argument("--language")
        a = ap.parse_args()
        print(make_voiceover(k, open(a.script, encoding="utf-8").read(), a.voice, a.out, a.max_chars, a.language))
