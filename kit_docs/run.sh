#!/usr/bin/env bash
cd "$(dirname "$0")"
exec "${PYTHON:-python3}" make_video.py "$@"
