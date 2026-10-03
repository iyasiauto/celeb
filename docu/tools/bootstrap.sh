#!/usr/bin/env bash
# bootstrap.sh - set up a fresh machine / Claude Code session so every project in projects/ builds.
#
#   docu/tools/bootstrap.sh [deps] [kit] [noah] [hasidic]      (no arguments = all four)
#
#   deps     pip packages (docu/requirements.txt) and a Chromium check
#   kit      the asset kit from Drive  -> media/kit      (fonts, maps, cut-outs, music, textures ...)
#            + the drawn props (envelope, notice, receipt, Yiddish list) into media/kit/cutouts
#   noah     Noah's Ark footage        -> media/footage  (+ media/work/ind: the two viral posts' images)
#   hasidic  Hasidic "Data" folder     -> media/hasidic  (+ picks/ staged from image_picks.json,
#                                                         footage/source_video -> src/clips)
#
# media/ sits next to docu/ and projects/ and is git-ignored. Every project's build.py uses it by
# default, so after this `python projects/<video>/build.py plan` works with no environment variables.
# Override any folder with VIDEO_ROOT / VIDEO_KIT / VIDEO_FOOTAGE / VIDEO_WORK / VIDEO_OUT.
# Downloads resume: re-run the same command to fetch what failed.
set -euo pipefail
REPO="$(cd "$(dirname "$0")/../.." && pwd)"
T="$REPO/docu/tools"
M="${VIDEO_ROOT:-$REPO/media}"
KIT_DRIVE="${KIT_DRIVE:-1CYxavMgiqBwVtUwFMizA-Txnf4123yYq}"          # asset kit (music, fonts, maps, cut-outs ...)
NOAH_DRIVE="${NOAH_DRIVE:-1HstYp4jR91BpL8QzGuBKUdaRqNpBOEar}"        # Noah's Ark footage + images
HASIDIC_DRIVE="${HASIDIC_DRIVE:-1iubj0u5xQdc_wO-I986zobwx5eLnUasm}"  # Hasidic niche clips + images
STEPS=("$@"); [ ${#STEPS[@]} -eq 0 ] && STEPS=(deps kit noah hasidic)
mkdir -p "$M"

for s in "${STEPS[@]}"; do
  echo "== $s"
  case "$s" in
    deps)
      pip install -q -r "$REPO/docu/requirements.txt"
      command -v ffmpeg >/dev/null || { echo "FFmpeg (with libx264) is missing: install it (apt-get install ffmpeg)"; exit 1; }
      python -c "import sys; sys.path.insert(0, '$REPO/docu'); import render, os; print('chromium:', render.CHROME, 'OK' if os.path.exists(render.CHROME) else 'MISSING -> run: playwright install chromium')"
      ;;
    kit)
      python "$T/fetch_drive.py" "$KIT_DRIVE" "$M/kit" 12
      python "$T/props.py" "$M/kit/cutouts"
      ;;
    noah)
      python "$T/fetch_drive.py" "$NOAH_DRIVE" "$M/footage" 12
      mkdir -p "$M/work/ind"
      i=0
      for d in "$M/footage/Individual Images/Researchers"* "$M/footage/Individual Images/"*HOW*; do
        i=$((i + 1)); [ -d "$d" ] || continue
        for f in "$d"/0[1-5].jpg; do dst="$M/work/ind/ind${i}_$(basename "$f")"; [ -e "$dst" ] || cp "$f" "$dst"; done
      done
      ;;
    hasidic)
      python "$T/fetch_drive.py" "$HASIDIC_DRIVE" "$M/hasidic/src" 12
      mkdir -p "$M/hasidic/footage"
      ln -sfn "$M/hasidic/src/clips" "$M/hasidic/footage/source_video"
      python "$T/catalog_images.py" stage "$REPO/projects/hasidic_benefits_cut/data/image_picks.json" \
             "$M/hasidic/src/images" "$M/hasidic/picks"
      ;;
    *) echo "unknown step $s (deps kit noah hasidic)"; exit 1 ;;
  esac
done
echo "ready: media root $M"
