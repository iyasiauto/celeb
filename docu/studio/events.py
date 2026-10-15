"""
events.py - the studio backend talks to the desktop app with one JSON object per stdout line.

    {"t": "stage",    "stage": "render", "status": "running"|"done"|"error"|"skipped", "msg": "..."}
    {"t": "progress", "stage": "render", "value": 0.42, "msg": "70/166 scenes"}
    {"t": "log",      "msg": "..."}
    {"t": "artifact", "kind": "still"|"sheet"|"video"|"audio"|"srt"|"link"|"project", "path": "...", "label": "..."}
    {"t": "result",   "data": {...}}                     (answer of a query command)
    {"t": "done",     "ok": true, "output": "...", "link": "..."}
    {"t": "error",    "msg": "..."}

Anything a child process prints that isn't JSON is forwarded as a log line.
"""

import json
import sys
import time

_stage = [None]


def emit(t, **kw):
    kw["t"] = t
    kw.setdefault("ts", round(time.time(), 3))
    sys.stdout.write(json.dumps(kw, ensure_ascii=False) + "\n")
    sys.stdout.flush()


def log(msg):
    emit("log", msg=str(msg))


def stage(name, status="running", msg=""):
    _stage[0] = name
    emit("stage", stage=name, status=status, msg=msg)


def progress(value, msg="", name=None):
    emit("progress", stage=name or _stage[0], value=round(max(0.0, min(1.0, value)), 4), msg=msg)


def artifact(kind, path, label=""):
    emit("artifact", kind=kind, path=path, label=label)


def result(data):
    emit("result", data=data)


def error(msg):
    emit("error", msg=str(msg))
