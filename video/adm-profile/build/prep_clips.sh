#!/bin/sh
# v5: model clips -> per-frame JPEGs for the deterministic seek(t) render (src/ is gitignored; the clips stay there).
#   src/sonet_clip.mp4 (Kia Sonet, 2024) is cropped to its top-left 1120x630 so the "JN0942" watermark (x>=1040, y>=645)
#   is cut away, then scaled to 1920x1080; src/k3_clip.mp4 (Kia K3, 2026) is only scaled. Native 24 fps, 240 frames each.
set -e
cd "$(dirname "$0")/.."
mkdir -p src/footage/sonet src/footage/k3
ffmpeg -v error -y -i src/sonet_clip.mp4 -vf "crop=1120:630:80:0,scale=1920:1080:flags=lanczos,unsharp=5:5:0.4" -q:v 3 src/footage/sonet/f_%06d.jpg
ffmpeg -v error -y -i src/k3_clip.mp4 -vf "scale=1920:1080:flags=lanczos,unsharp=5:5:0.3" -q:v 3 src/footage/k3/f_%06d.jpg
echo "frames: $(ls src/footage/sonet | wc -l) sonet, $(ls src/footage/k3 | wc -l) k3"
