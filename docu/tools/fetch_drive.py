"""
fetch_drive.py - download a shared Google Drive folder (images + clips) fast, in parallel.

    python fetch_drive.py <folder url or id> <dest dir> [threads=12]

gdown downloads a folder one file at a time, which takes hours for ~1,000 files. This lists the
folder first (gdown, no download), writes <dest>/manifest.json, then fetches the files with a
thread pool, retrying each up to 3 times. Re-running skips everything already on disk, and the
files that still failed are listed in <dest>/fails.json.

Files keep the Drive folder layout, e.g. <dest>/clips/..., <dest>/images/... Point the project's
`footage` / `image_dirs` at them (see INTEGRATION.md, "Footage layout").
"""

import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor

import gdown


def list_folder(url, dest):
    """[(file_id, relative_path)] for every file under the folder (recursively)."""
    kw = dict(url=url) if url.startswith("http") else dict(id=url)
    items = gdown.download_folder(output=dest.rstrip("/") + "/", skip_download=True, quiet=True, **kw)   # gdown >= 5
    out = []
    for it in items or []:
        rel = os.path.relpath(it.local_path, dest)
        out.append((it.id, rel))
    return out


def fetch(items, dest, threads=12):
    done, fails = [0], []

    def get(it):
        fid, rel = it
        path = os.path.join(dest, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        if os.path.exists(path) and os.path.getsize(path) > 0:
            done[0] += 1
            return
        for k in range(3):
            try:
                gdown.download(id=fid, output=path, quiet=True)
                if os.path.exists(path) and os.path.getsize(path) > 0:
                    break
            except Exception:
                time.sleep(2 + 3 * k)
        else:
            fails.append(it)
        done[0] += 1
        if done[0] % 100 == 0:
            print(time.strftime("%H:%M:%S"), done[0], "/", len(items), "fails", len(fails), flush=True)

    items = sorted(items, key=lambda x: "clip" not in x[1].lower())        # clips first: fewer, bigger
    with ThreadPoolExecutor(threads) as ex:
        list(ex.map(get, items))
    return fails


if __name__ == "__main__":
    url, dest = sys.argv[1], sys.argv[2]
    threads = int(sys.argv[3]) if len(sys.argv) > 3 else 12
    os.makedirs(dest, exist_ok=True)
    man = os.path.join(dest, "manifest.json")
    if os.path.exists(man):
        items = [tuple(x) for x in json.load(open(man))]
    else:
        items = list_folder(url, dest)
        json.dump(items, open(man, "w"), indent=0)
    print(len(items), "files listed")
    fails = fetch(items, dest, threads)
    json.dump(fails, open(os.path.join(dest, "fails.json"), "w"))
    print("done;", len(fails), "failed" + (" (run again to retry)" if fails else ""))
