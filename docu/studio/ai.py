"""
ai.py - the studio's AI, from whichever provider you use. Claude is optional.

Two roles, each set in Settings (env STUDIO_EDITOR / STUDIO_VISION, models STUDIO_EDITOR_MODEL / STUDIO_VISION_MODEL):

    editor   writes the shot list, fixes it from the plan check, writes the YouTube metadata
    vision   looks at pictures: the stills QA and cataloging a new niche

Providers:

    auto          the first one that is set up, in the order below
    claude_code   the Claude Code CLI on this PC (`claude -p`), your own plan, no API key
    openrouter    OpenRouter (OPENROUTER_API_KEY; e.g. deepseek/deepseek-chat) - OpenAI-compatible
    openlux       OpenLux (OPENLUX_API_KEY; e.g. gemini-2.5-flash-lite, sees pictures) - OpenAI-compatible
    antigravity   your Antigravity / Gemini account through a local model router (cli-proxy-api), an
                  OpenAI-compatible endpoint on this PC (ANTIGRAVITY_BASE_URL, default http://127.0.0.1:8317/v1)
    custom        any OpenAI-compatible endpoint (CUSTOM_AI_BASE_URL, CUSTOM_AI_API_KEY)
    claude_api    the Anthropic API (ANTHROPIC_API_KEY)
    none          no AI: the offline shot list, no visual QA

Keys come from the app, api_keys/keys.env, or your Frontier .env (tools/keys.py).
"""

import base64
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "tools"))
from keys import get as key      # noqa: E402

ORDER_EDITOR = ["claude_code", "openrouter", "antigravity", "openlux", "custom", "claude_api"]
ORDER_VISION = ["openlux", "claude_code", "antigravity", "custom", "claude_api", "openrouter"]
DEFAULT_MODEL = {"claude_code": "sonnet", "openrouter": "deepseek/deepseek-chat", "openlux": "gemini-2.5-flash-lite",
                 "antigravity": "gemini-2.5-pro", "custom": "", "claude_api": "claude-opus-5-5"}
VISION_OK = {"claude_code", "openlux", "antigravity", "custom", "claude_api"}
LABEL = {"claude_code": "Claude Code (your plan)", "openrouter": "OpenRouter", "openlux": "OpenLux",
         "antigravity": "Antigravity (local router)", "custom": "Custom endpoint", "claude_api": "Claude API", "none": "off"}


class AIError(RuntimeError):
    pass


def _claude_exe():
    found = shutil.which("claude")
    if not found:
        for c in (os.path.expandvars(r"%USERPROFILE%\.local\bin\claude.exe"), os.path.expandvars(r"%APPDATA%\npm\claude.cmd"),
                  "/opt/homebrew/bin/claude", "/usr/local/bin/claude", os.path.expanduser("~/.local/bin/claude")):
            if os.path.exists(c):
                return c
    return found


def _endpoint(p):
    """(base_url, api_key) for an OpenAI-compatible provider, or None when it isn't set up"""
    if p == "openrouter":
        k = key("OPENROUTER_API_KEY")
        return ((key("OPENROUTER_BASE_URL") or "https://openrouter.ai/api/v1").rstrip("/"), k) if k else None
    if p == "openlux":
        k = key("OPENLUX_API_KEY")
        return ((key("OPENLUX_BASE_URL") or "https://api.openlux.ai/v1").rstrip("/"), k) if k else None
    if p == "antigravity":
        base = (key("ANTIGRAVITY_BASE_URL") or "http://127.0.0.1:8317/v1").rstrip("/")
        if key("ANTIGRAVITY_BASE_URL") or key("ANTIGRAVITY_API_KEY") or _alive(base):
            return base, key("ANTIGRAVITY_API_KEY") or "none"
        return None
    if p == "custom":
        base = key("CUSTOM_AI_BASE_URL")
        return (base.rstrip("/"), key("CUSTOM_AI_API_KEY") or "none") if base else None
    return None


def _alive(base):
    try:
        urllib.request.urlopen(base + "/models", timeout=2)
        return True
    except urllib.error.HTTPError:
        return True                      # it answered (401 etc.): something is listening
    except Exception:
        return False


def ready(p):
    if p == "claude_code":
        return bool(_claude_exe())
    if p == "claude_api":
        return bool(key("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN"))
    return _endpoint(p) is not None


def resolve(role):
    """the provider to use for a role, or None for 'no AI'"""
    want = (os.environ.get("STUDIO_" + role.upper()) or "auto").lower()
    if want == "none":
        return None
    if want != "auto":
        return want if ready(want) else None
    for p in (ORDER_VISION if role == "vision" else ORDER_EDITOR):
        if ready(p) and (role != "vision" or p in VISION_OK):
            return p
    return None


def model_for(role, p):
    return os.environ.get("STUDIO_" + role.upper() + "_MODEL") or \
        (key("OPENROUTER_MODEL") if p == "openrouter" else None) or \
        (key("OPENLUX_MODEL") if p == "openlux" else None) or \
        (key("ANTIGRAVITY_MODEL") if p == "antigravity" else None) or \
        (key("CUSTOM_AI_MODEL") if p == "custom" else None) or DEFAULT_MODEL.get(p, "")


def status():
    out = {}
    for p in ORDER_EDITOR:
        out[p] = ready(p)
    out["editor"] = resolve("editor")
    out["vision"] = resolve("vision")
    return out


def jpeg_b64(path, width=1600):
    from PIL import Image
    im = Image.open(path).convert("RGB")
    if im.width > width:
        im = im.resize((width, int(im.height * width / im.width)))
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=80)
    return base64.standard_b64encode(buf.getvalue()).decode()


class Chat:
    """one conversation with the role's provider; history is kept so fixes keep their context"""

    def __init__(self, role, system="", log=print, provider=None, model=None, effort="high"):
        self.p = provider or resolve(role)
        if not self.p:
            raise AIError(f"no AI provider is set up for the {role} (Settings → AI)")
        self.role, self.system, self.log, self.effort = role, system, log, effort
        self.model = model or model_for(role, self.p)
        self.history = []                 # [(role, text, [image paths])]
        self._claude_msgs = []

    @property
    def label(self):
        return f"{LABEL.get(self.p, self.p)} · {self.model}"

    def send(self, text, images=(), on_text=None, max_tokens=32000):
        images = list(images)
        if images and self.p not in VISION_OK:
            raise AIError(f"{LABEL[self.p]} cannot look at pictures; choose a vision provider")
        fn = {"claude_code": self._claude_code, "claude_api": self._claude_api}.get(self.p, self._openai)
        out = fn(text, images, on_text, max_tokens)
        self.history += [("user", text, images), ("assistant", out, [])]
        return out

    # ---------------------------------------------------------------- OpenAI-compatible
    def _openai(self, text, images, on_text, max_tokens):
        base, k = _endpoint(self.p)
        msgs = [{"role": "system", "content": self.system}] if self.system else []
        for r, t, ims in self.history:
            msgs.append({"role": r, "content": t if not ims else self._parts(t, ims)})
        msgs.append({"role": "user", "content": text if not images else self._parts(text, images)})
        out = ""
        for part in range(6):                     # continue when the model stops at its output limit
            d = self._post(base, k, {"model": self.model, "messages": msgs, "max_tokens": max_tokens, "temperature": 0.4})
            ch = (d.get("choices") or [{}])[0]
            piece = ((ch.get("message") or {}).get("content") or "")
            out += piece
            if on_text:
                on_text(len(out))
            if ch.get("finish_reason") != "length":
                break
            msgs += [{"role": "assistant", "content": piece},
                     {"role": "user", "content": "Continue exactly where you stopped, without repeating anything."}]
            self.log("(the answer hit the model's output limit: asking it to continue)")
        u = d.get("usage") or {}
        self.log(f"{self.label}: {u.get('prompt_tokens', '?')} in, {u.get('completion_tokens', '?')} out")
        if not out.strip():
            raise AIError(f"{self.label} returned an empty answer")
        return out

    @staticmethod
    def _parts(text, images):
        return [{"type": "text", "text": text}] + [
            {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64," + jpeg_b64(p)}} for p in images]

    def _post(self, base, k, body):
        req = urllib.request.Request(base + "/chat/completions", data=json.dumps(body).encode(), method="POST", headers={
            "Authorization": f"Bearer {k}", "Content-Type": "application/json",
            "HTTP-Referer": "https://docu.studio.local", "X-Title": "Docu Studio"})
        last = ""
        for attempt in range(6):
            try:
                with urllib.request.urlopen(req, timeout=900) as r:
                    return json.loads(r.read())
            except urllib.error.HTTPError as e:
                last = f"HTTP {e.code}: {e.read().decode('utf-8', 'ignore')[:300]}"
                if e.code < 500 and e.code != 429:
                    raise AIError(f"{self.label}: {last}")
            except Exception as e:                # noqa: BLE001 - network: retry
                last = str(e)
            wait = min(60, 8 * (attempt + 1))
            self.log(f"{self.label} error ({last[:80]}); retrying in {wait}s")
            time.sleep(wait)
        raise AIError(f"{self.label}: {last}")

    # ---------------------------------------------------------------- Claude Code CLI
    def _claude_code(self, text, images, on_text, max_tokens):
        exe = _claude_exe()
        convo = ""
        for r, t, _ in self.history:
            convo += f"\n\n<{r}>\n{t}\n</{r}>"
        prompt = (f"{convo}\n\n<user>\n{text}\n</user>\n\nReply to the last user message." if convo else text)
        if images:
            prompt = "First read these image files so you can see them:\n" + "\n".join(f"- {os.path.abspath(p)}" for p in images) + "\n\n" + prompt
        cwd = os.path.join(tempfile.gettempdir(), "docu-studio-claude")
        os.makedirs(cwd, exist_ok=True)
        cmd = [exe, "-p", "--model", self.model, "--output-format", "text", "--no-session-persistence",
               "--disable-slash-commands", "--strict-mcp-config", "--system-prompt", self.system or "Answer the user."]
        if images:
            cmd += ["--tools", "Read", "--allowedTools", "Read", "--permission-mode", "dontAsk"]
            for d in sorted({os.path.dirname(os.path.abspath(p)) for p in images}):
                cmd += ["--add-dir", d]
        else:
            cmd += ["--tools", ""]
        last = ""
        for attempt in range(3):
            r = subprocess.run(cmd, input=prompt, text=True, capture_output=True, timeout=1800, cwd=cwd,
                               encoding="utf-8", errors="replace")
            out = (r.stdout or "").strip()
            if r.returncode == 0 and out:
                self.log(f"{self.label}: {len(out)} characters")
                if on_text:
                    on_text(len(out))
                return out
            last = ((r.stderr or "").strip() or out)[:300] or f"exit {r.returncode}"
            if any(w in last.lower() for w in ("authentication", "oauth", "usage limit", "not logged")):
                break
            time.sleep(5 * (attempt + 1))
        raise AIError(f"Claude Code CLI: {last}")

    # ---------------------------------------------------------------- Anthropic API
    def _claude_api(self, text, images, on_text, max_tokens):
        import anthropic
        client = anthropic.Anthropic(api_key=key("ANTHROPIC_API_KEY")) if key("ANTHROPIC_API_KEY") else anthropic.Anthropic()
        content = [{"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": jpeg_b64(p)}}
                   for p in images] + [{"type": "text", "text": text}]
        self._claude_msgs.append({"role": "user", "content": content})
        system = [{"type": "text", "text": self.system, "cache_control": {"type": "ephemeral"}}] if self.system else []
        with client.beta.messages.stream(
            model=self.model, max_tokens=64000, system=system, messages=self._claude_msgs,
            thinking={"type": "adaptive"}, output_config={"effort": self.effort},
            betas=["server-side-fallback-2026-07-01"], fallbacks="default",
        ) as stream:
            n = 0
            for ev in stream:
                if ev.type == "content_block_delta" and getattr(ev.delta, "type", "") == "text_delta":
                    n += len(ev.delta.text)
                    if on_text:
                        on_text(n)
            msg = stream.get_final_message()
        if msg.stop_reason == "refusal":
            self._claude_msgs.pop()
            raise AIError("Claude declined this request (refusal)")
        self._claude_msgs.append({"role": "assistant", "content": msg.content})
        u = msg.usage
        self.log(f"{self.label}: {u.input_tokens} in (+{getattr(u, 'cache_read_input_tokens', 0) or 0} cached), {u.output_tokens} out")
        return "".join(b.text for b in msg.content if b.type == "text")


def extract_code(text):
    """the ```python block of an answer, cleaned of setup lines, compiled to check it"""
    m = re.findall(r"```(?:python|py)?\s*\n(.*?)```", text, re.S)
    code = max(m, key=len).strip() if m else text.strip()
    code = "\n".join(l for l in code.split("\n") if not re.match(r"\s*(import |from |edl\.setup|edl\.main|shots\.init)", l))
    if "ACTS" not in code:
        code += "\n\nACTS = [None]\n"
    compile(code, "shotlist", "exec")
    return code
