#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
PY=${PYTHON:-python3}
echo "Installing Docu Templates (Python packages, Chromium, FFmpeg)..."
$PY -m pip install --upgrade pip
$PY -m pip install -r docu/requirements.txt static-ffmpeg anthropic
$PY -m playwright install chromium
command -v ffmpeg >/dev/null || $PY -c "import static_ffmpeg; static_ffmpeg.add_paths(); import shutil; print('ffmpeg:', shutil.which('ffmpeg'))"
[ -f api_keys/keys.env ] || cp api_keys/keys.example.env api_keys/keys.env
echo "Done. Put your keys (optional) in api_keys/keys.env, then run ./run.sh"
