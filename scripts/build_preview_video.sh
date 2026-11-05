#!/usr/bin/env bash
# Builds the homepage hero video (assets/steadiday-preview-886x1920.mp4)
# from the screenshot PNGs in assets/: each slide holds for 3.5 s and
# cross-fades into the next over 0.5 s, 25 s in all, 886x1920 at 30 fps.
#
# The screenshots themselves are rendered from HTML in the app repo:
# steadiday-app/marketing/app-store-screenshots (see its README). Copy the
# new renders into assets/ first, then run this from the repo root:
#
#   scripts/build_preview_video.sh
set -euo pipefail

cd "$(dirname "$0")/.."

SLIDES=(
  assets/screenshot-01-simple-home.png
  assets/screenshot-02-medicines.png
  assets/screenshot-07-fall-detection.png
  assets/screenshot-03-share-activity.png
  assets/screenshot-04-steady-moves.png
  assets/screenshot-05-sos.png
  assets/screenshot-06-premium.png
)
HOLD=4.0   # seconds each slide is on screen, fade included
FADE=0.5
OUT=assets/steadiday-preview-886x1920.mp4

inputs=()
for s in "${SLIDES[@]}"; do
  [[ -f "$s" ]] || { echo "missing $s" >&2; exit 1; }
  inputs+=(-loop 1 -t "$HOLD" -framerate 30 -i "$s")
done

filter=""
for i in "${!SLIDES[@]}"; do
  filter+="[$i:v]scale=886:1920:flags=lanczos,setsar=1,format=yuv420p[s$i];"
done
prev="s0"
for ((i = 1; i < ${#SLIDES[@]}; i++)); do
  offset=$(awk -v i="$i" -v h="$HOLD" -v f="$FADE" 'BEGIN { printf "%.2f", i * (h - f) }')
  out="x$i"
  filter+="[$prev][s$i]xfade=transition=fade:duration=$FADE:offset=$offset[$out];"
  prev="$out"
done
filter="${filter%;}"

ffmpeg -v error -y "${inputs[@]}" -filter_complex "$filter" -map "[$prev]" \
  -r 30 -c:v libx264 -profile:v high -pix_fmt yuv420p -crf 23 -preset slow \
  -movflags +faststart -an "$OUT"

ffprobe -v error -show_entries format=duration:stream=width,height,r_frame_rate \
  -of compact "$OUT"
ls -l "$OUT"
