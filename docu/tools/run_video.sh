#!/usr/bin/env bash
# run_video.sh - one video, end to end, as a single pipeline stage.
#
#   tools/run_video.sh <project dir> [stage ...]
#
# stages (default: all, in this order): plan prep stills render mix final deliver
# Stops at the first failing stage. Every stage is resumable: re-running `render` only renders
# scenes whose segment is missing. WORKERS (default 4) = scenes rendered in parallel;
# LIMIT_GB (default 1.0) = size limit for delivery; NO_UPLOAD=1 skips the gofile upload.
#
#   tools/run_video.sh projects/hasidic_benefits_cut                 # everything
#   tools/run_video.sh projects/hasidic_benefits_cut plan stills     # check cues + QA frames only
set -euo pipefail
PROJ="$(cd "$1" && pwd)"; shift
TOOLS="$(cd "$(dirname "$0")" && pwd)"
STAGES=("$@"); [ ${#STAGES[@]} -eq 0 ] && STAGES=(plan prep stills render mix final deliver)
cd "$PROJ"
for st in "${STAGES[@]}"; do
  echo "== $st  ($(date +%H:%M:%S))"
  if [ "$st" = deliver ]; then
    MP4="$(python build.py path)"
    python "$TOOLS/deliver.py" "$MP4" --limit-gb "${LIMIT_GB:-1.0}" ${NO_UPLOAD:+--no-upload}
  else
    python build.py "$st"
  fi
done
